import argparse
import json
import os
import random
import re
from pathlib import Path
from typing import Any, Dict, Optional

import openai


class ReasoningEngine:
    """
    GEM-LLM Reasoning Engine: Phase 2 of the framework.
    Synthesizes global semantic invariants using CoT and few-shot prompting.
    """

    def __init__(
        self,
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.2,
        top_p: float = 0.95,
        max_tokens: int = 1024,
        seed: int = 42,
    ) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.seed = seed
        self.is_local = model_name.startswith("local-")
        self.template_path = os.path.join(os.path.dirname(__file__), "prompts", "cot_template.json")

        random.seed(self.seed)

        if self.is_local:
            self._init_local_model(model_name.replace("local-", ""))
        else:
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key is required for non-local models. "
                    "Set OPENAI_API_KEY or provide it via --api-key."
                )
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)

    def _init_local_model(self, local_model: str) -> None:
        """Load local Hugging Face model lazily so OpenAI-only setups work."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, set_seed
        except ImportError as exc:
            raise ImportError(
                "Local model support requires `transformers` (and a compatible backend such as torch)."
            ) from exc

        set_seed(self.seed)
        self.tokenizer = AutoTokenizer.from_pretrained(local_model)
        self.model = AutoModelForCausalLM.from_pretrained(local_model)
        self.generator = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

    def _load_template(self) -> Dict[str, Any]:
        with open(self.template_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_final_prompt(self, context_ir: Dict[str, Any]) -> str:
        template = self._load_template()
        prompt = "### Few-Shot Examples for Invariant Inference:\n"
        for i, example in enumerate(template["few_shot_examples"], 1):
            prompt += f"Example {i}:\nContext: {json.dumps(example['context'])}\n"
            prompt += f"Reasoning: {example['reasoning']}\n"
            prompt += f"Output: {example['output']}\n\n"

        prompt += "### Current Task:\n"
        prompt += f"Context (JSON-IR): {json.dumps(context_ir)}\n"
        prompt += f"Task: {template['task_description']}\n\n"

        prompt += "### Reasoning Steps:\n"
        for step in template["cot_steps"]:
            prompt += f"- {step}\n"

        prompt += "\nConstraints: " + ", ".join(template["constraints"])
        return prompt

    @staticmethod
    def _extract_balanced_from(text: str, start: int) -> Optional[str]:
        depth = 0
        for idx in range(start, len(text)):
            char = text[idx]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    return text[start : idx + 1]
        return None

    @classmethod
    def extract_assertion(cls, raw_response: str) -> str:
        """
        Normalize the LLM output to a single SMT-LIB assertion.
        Accepts either a plain logical term or a full `(assert ...)` form.
        """
        if not raw_response or not raw_response.strip():
            raise ValueError("LLM returned an empty response.")

        text = raw_response.strip()

        match = re.search(r"\(assert\b", text)
        if match:
            assertion = cls._extract_balanced_from(text, match.start())
            if assertion:
                return assertion

        first_paren = text.find("(")
        if first_paren >= 0:
            expr = cls._extract_balanced_from(text, first_paren)
            if expr:
                return f"(assert {expr})"

        raise ValueError(f"Could not extract an SMT-LIB assertion from response: {text[:200]}")

    def _generate_remote(self, template: Dict[str, Any], final_prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": template["system_role"]},
                {"role": "user", "content": final_prompt},
            ],
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            seed=self.seed,
        )
        return (completion.choices[0].message.content or "").strip()

    def _generate_local(self, final_prompt: str) -> str:
        outputs = self.generator(
            final_prompt,
            max_new_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            do_sample=True,
            return_full_text=False,
        )
        return outputs[0]["generated_text"].strip()

    def generate_invariant(self, slice_data: Dict[str, Any]) -> str:
        template = self._load_template()
        final_prompt = self._build_final_prompt(slice_data)
        try:
            raw_response = self._generate_local(final_prompt) if self.is_local else self._generate_remote(template, final_prompt)
            return self.extract_assertion(raw_response)
        except Exception as exc:
            raise RuntimeError(f"Error during invariant generation: {exc}") from exc


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def infer_slice_path(project: Optional[str], version: Optional[str]) -> Optional[Path]:
    if not project:
        return None

    stem = f"{project}_{version}" if version else project
    candidates = [
        Path("data") / "outputs" / f"{stem}_slice.json",
        Path("data") / "outputs" / stem / "slice.json",
        Path("data") / "subjects" / stem / "slice.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a contextual invariant from a JSON slice.")
    parser.add_argument("--slice-file", help="Path to the JSON slice emitted by the slicer.")
    parser.add_argument("--project", help="Project name (used to resolve the default slice path).")
    parser.add_argument("--version", help="Project version, e.g. 1b.")
    parser.add_argument("--model", default="gpt-4o", help="Model name. Prefix with local- for local HF models.")
    parser.add_argument("--api-key", help="OpenAI API key. Defaults to OPENAI_API_KEY.")
    parser.add_argument("--base-url", help="Optional OpenAI-compatible base URL.")
    parser.add_argument("--output", help="Optional file to save the invariant assertion.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    slice_path = Path(args.slice_file) if args.slice_file else infer_slice_path(args.project, args.version)
    if slice_path is None or not slice_path.exists():
        raise FileNotFoundError(
            "No slice JSON was found. Provide --slice-file or place a slicer output in one of: "
            "data/outputs/<project>_<version>_slice.json, data/outputs/<project>_<version>/slice.json, "
            "or data/subjects/<project>_<version>/slice.json."
        )

    slice_data = load_json(str(slice_path))
    engine = ReasoningEngine(model_name=args.model, api_key=args.api_key, base_url=args.base_url)
    invariant = engine.generate_invariant(slice_data)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(invariant + "\n", encoding="utf-8")
    print(invariant)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

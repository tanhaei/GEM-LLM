import openai
import json
import os
from typing import Dict, Any, Optional

class ReasoningEngine:
    """
    GEM-LLM Reasoning Engine: Phase 2 of the framework.
    Synthesizes global semantic invariants using CoT and Few-Shot prompting.
    """
    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initializes the engine with specific hyperparameters to ensure reproducibility.
        """
        self.model_name = model_name
        # Fixed parameters as per Section 4.6 of the paper
        self.temperature = 0.2  # Minimizes hallucinations [cite: 285, 405]
        self.top_p = 0.95       # Balances creativity and logic [cite: 133, 285]
        self.max_tokens = 1024  # Sufficient for SMT-LIB assertions [cite: 133]
        self.seed = 42          # Ensures deterministic results [cite: 286]
        
        # Support for both OpenAI API and local inference servers (e.g., vLLM)
        self.client = openai.OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY", "EMPTY"),
            base_url=base_url  # Used for local Llama-3/Gemma deployment [cite: 438]
        )
        
        self.template_path = os.path.join(os.path.dirname(__file__), "prompts", "cot_template.json")

    def _load_template(self) -> Dict[str, Any]:
        """Loads the prompting strategy from the template file."""
        with open(self.template_path, "r") as f:
            return json.load(f)

    def _build_final_prompt(self, context_ir: Dict[str, Any]) -> str:
        """
        Constructs a structured prompt using Chain-of-Thought (CoT) 
        and Few-Shot examples[cite: 111, 144].
        """
        template = self._load_template()
        
        # Start with few-shot examples for guidance [cite: 143, 146]
        prompt = "### Few-Shot Examples for Invariant Inference:\n"
        for i, example in enumerate(template["few_shot_examples"], 1):
            prompt += f"Example {i}:\nContext: {json.dumps(example['context'])}\n"
            prompt += f"Reasoning: {example['reasoning']}\n"
            prompt += f"Output: {example['output']}\n\n"
        
        # Add the current target context from Soat slicer [cite: 105, 116]
        prompt += "### Current Task:\n"
        prompt += f"Context (JSON-IR): {json.dumps(context_ir)}\n"
        prompt += f"Task: {template['task_description']}\n\n"
        
        # Enforce CoT reasoning steps [cite: 112-114, 127-130]
        prompt += "### Reasoning Steps:\n"
        for step in template["cot_steps"]:
            prompt += f"- {step}\n"
            
        prompt += "\nConstraints: " + ", ".join(template["constraints"])
        return prompt

    def generate_invariant(self, slice_data: Dict[str, Any]) -> str:
        """
        Invokes the LLM to generate a global invariant IG[cite: 79, 108].
        """
        template = self._load_template()
        final_prompt = self._build_final_prompt(slice_data)
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": template["system_role"]},
                {"role": "user", "content": final_prompt}
            ],
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            seed=self.seed
        )
        
        # Return the raw SMT-LIB assertion for Phase 3 
        return response.choices[0].message.content.strip()

# Technical validation section for the Banking scenario
if __name__ == "__main__":
    # Example logic from Listing 1 of the paper [cite: 85-101]
    engine = ReasoningEngine(api_key="sk-your-key-here")
    
    context_data = {
        "mutated_method": "process",
        "callers": ["executeTransfer"],
        "guards": "amount > 100 && amount <= 5000",
        "data_flow": "value -> amount"
    }
    
    print(">>> Generating Invariant for Banking Service...")
    # invariant = engine.generate_invariant(context_data)
    # print(f"Identified Invariant: {invariant}")
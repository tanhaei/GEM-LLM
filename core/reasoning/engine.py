import openai
import json
import os
from typing import Dict, Any, Optional

# Add Hugging Face Transformers for local model support
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

class ReasoningEngine:
    """
    GEM-LLM Reasoning Engine: Phase 2 of the framework.
    Synthesizes global semantic invariants using CoT and Few-Shot prompting.
    """
    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initializes the engine with specific hyperparameters to ensure reproducibility.
        Supports both OpenAI API and local models (e.g., 'local-gemma-27b') for privacy.
        """
        self.model_name = model_name
        # Fixed parameters as per Section 4.6 of the paper
        self.temperature = 0.2  # Minimizes hallucinations [cite: 285, 405]
        self.top_p = 0.95       # Balances creativity and logic [cite: 133, 285]
        self.max_tokens = 1024  # Sufficient for SMT-LIB assertions [cite: 133]
        self.seed = 42          # Ensures deterministic results [cite: 286]
        
        self.is_local = model_name.startswith("local-")
        
        if self.is_local:
            # Local model setup (e.g., Gemma or Llama via Hugging Face)
            local_model = model_name.replace("local-", "")
            self.tokenizer = AutoTokenizer.from_pretrained(local_model)
            self.model = AutoModelForCausalLM.from_pretrained(local_model)
            self.generator = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
        else:
            # OpenAI API setup
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("API key is required for non-local models. Set OPENAI_API_KEY or provide via constructor.")
            self.client = openai.OpenAI(
                api_key=api_key,
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
        
        # Add the current target context from Soot slicer [cite: 105, 116]
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
        Handles both remote API and local inference.
        """
        template = self._load_template()
        final_prompt = self._build_final_prompt(slice_data)
        
        try:
            if self.is_local:
                # Local generation
                inputs = self.tokenizer(final_prompt, return_tensors="pt")
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    do_sample=True  # Seed not directly supported; use for determinism approximation
                )
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            else:
                # OpenAI API generation
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
                ).choices[0].message.content.strip()
            
            # Return the raw SMT-LIB assertion for Phase 3 
            return response
            
        except Exception as e:
            raise RuntimeError(f"Error during invariant generation: {str(e)}")

# Technical validation section for the Banking scenario
if __name__ == "__main__":
    # Example: Remote OpenAI
    engine = ReasoningEngine(api_key="sk-your-key-here")
    
    # Example: Local model (uncomment and adjust as needed)
    # engine = ReasoningEngine(model_name="local-gemma-2b")  # Assuming model is downloaded
    
    context_data = {
        "mutated_method": "process",
        "callers": ["executeTransfer"],
        "guards": "amount > 100 && amount <= 5000",
        "data_flow": "value -> amount"
    }
    
    print(">>> Generating Invariant for Banking Service...")
    invariant = engine.generate_invariant(context_data)
    print(f"Identified Invariant: {invariant}")
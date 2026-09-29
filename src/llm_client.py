"""Local Hugging Face causal language-model client."""

from __future__ import annotations

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class HuggingFaceLLM:
    """Generate text using a Hugging Face causal language model."""

    def __init__(
        self,
        model_name: str = "EleutherAI/gpt-neo-125M",
        device: str | None = None,
    ) -> None:
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 180,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response from a prompt."""
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048,
        )

        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=temperature > 0,
                temperature=temperature if temperature > 0 else None,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        generated_tokens = output[0][inputs["input_ids"].shape[1] :]
        return self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True,
        ).strip()

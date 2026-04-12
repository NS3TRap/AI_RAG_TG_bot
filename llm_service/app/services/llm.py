import os
import torch
import logging
from typing import List
from transformers import AutoTokenizer, AutoModelForCausalLM

from llm_service.app.config import LLMConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        config = LLMConfig.from_env()
        self.model_name = config.model_name
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            token = config.huggingface_token
        )
        logger.info("Tokenizer loaded.")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto",
            token = config.huggingface_token,
            trust_remote_code=True
        )
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info(f"Model loaded on {self.device}")

    def build_prompt(self, query: str, context: List[str]) -> str:
        context_text = "\n".join(context) if context else "Контекст отсутствует"
        logger.debug(f"Building prompt with context: {context_text} and query: {query}")
        return [
            {
                "role": "system",
                "content": context_text
            },
            {
                "role": "user",
                "content": query
            }
               ]

    def generate(self, query: str, context: List[str]) -> str:
        prompt = self.build_prompt(query, context)

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

        result = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        answer = result.replace(prompt, "").strip()
        logger.debug(f"Generated answer: {answer}")
        return answer
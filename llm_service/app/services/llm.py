import torch
import logging
from typing import List
from transformers import AutoTokenizer, AutoModelForCausalLM

from llm_service.app.config import LLMConfig


logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        config = LLMConfig.from_env()

        self.model_name = config.model_name

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            token=config.huggingface_token
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto",
            trust_remote_code=True,
            token=config.huggingface_token
        )

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info(f"Model loaded on {self.device}")

    def generate(self, query: str, context: list[str]) -> str:
        context_text = "\n".join(context) if context else "Контекст отсутствует"

        messages = [
            {
                "role": "system",
                "content": f"Ты полезный ассистент. Отвечай кратко и по делу.\nКонтекст:\n{context_text}"
            },
            {
                "role": "user",
                "content": query
            }
        ]

        input_text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(
            input_text,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=800,
                temperature=0.2,        
                top_p=0.85,
                repetition_penalty=1.2,
                do_sample=True,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id
            )

        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        answer = decoded.split("assistant")[-1].strip()
        answer = answer.replace(":", "").strip()

        return answer
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass

@dataclass
class LLMConfig():
    host: str = "127.0.0.1"
    port: int = 8000
    model_name: str = "stub"
    huggingface_token: str = ""

    @classmethod
    def from_env(cls):
        load_dotenv(Path(__file__).resolve().parents[2] / ".env")
        logging.info("PATH Path(__file__).resolve().parents[2]")
        host = os.getenv("LLM_SERVER_HOST") or "127.0.0.1"
        port = int(os.getenv("LLM_SERVER_PORT")) if os.getenv("LLM_SERVER_PORT") else 8000
        model_name = os.getenv("LLM_MODEL_NAME") or "stub"
        huggingface_token = os.getenv("HUGGINGFACE_TOKEN") or ""
        return cls(
            host=host.strip(),
            port=port,
            model_name=model_name.strip(),
            huggingface_token=huggingface_token.strip()
        )




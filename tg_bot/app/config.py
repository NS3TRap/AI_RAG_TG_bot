import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

@dataclass
class BotConfig:
    token: str
    webhook_url: str
    host: str = "0.0.0.0"
    port: int = 8000
    path: str = "/webhook"

    @classmethod
    def from_env(cls):
        load_dotenv(Path(__file__).resolve().parents[2] / ".env")

        token = os.getenv("TG_BOT_TOKEN") or os.getenv("TOKEN")
        webhook_url = os.getenv("WEBHOOK_URL") or os.getenv("BASE_WEBHOOK_URL")
        if not token or not webhook_url:
            raise RuntimeError("Set TG_BOT_TOKEN (or TOKEN) and WEBHOOK_URL (or BASE_WEBHOOK_URL) environment variables")

        host = os.getenv("WEBAPP_HOST") or os.getenv("WEB_SERVER_HOST") or "0.0.0.0"
        port = os.getenv("WEBAPP_PORT") or os.getenv("WEB_SERVER_PORT") or "8000"

        return cls(
            token=token.strip(),
            webhook_url=webhook_url.strip(),
            host=host.strip(),
            port=int(port),
            path=os.getenv("WEBHOOK_PATH", "/webhook").strip(),
        )

    @property
    def webhook_path(self) -> str:
        return self.path if self.path.startswith("/") else f"/{self.path}"

    @property
    def webhook_full_url(self) -> str:
        return f"{self.webhook_url.rstrip('/')}" + self.webhook_path

bot_config = BotConfig.from_env()
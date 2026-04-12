import os
import aiohttp
import logging

class LLMClient:
    def __init__(self):
        self.url = "http://" + os.getenv("LLM_SERVER_HOST") + ":" + os.getenv("LLM_SERVER_PORT") + "/generate"

    async def generate(self, query: str, context: list[str] | None = None) -> str:
        payload = {
            "query": query,
            "context": context or []
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=payload) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logging.error(f"LLM error: {text}")
                        return "Ошибка при обращении к LLM"

                    data = await resp.json()
                    return data.get("answer", "Пустой ответ от LLM")

        except Exception as e:
            logging.exception("LLM request failed")
            return "Не удалось подключиться к LLM"


llm_client = LLMClient()
import asyncio
import logging
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMQueue:
    def __init__(self, llm_service):
        self.queue = asyncio.Queue()
        self.llm_service = llm_service
        self.worker_task = None

    async def start(self):
        self.worker_task = asyncio.create_task(self.worker())
        logger.info("LLM Queue worker started")

    async def worker(self):
        while True:
            task = await self.queue.get()

            try:
                result = self.llm_service.generate(
                    task["query"],
                    task["context"]
                )
                task["future"].set_result(result)

            except Exception as e:
                task["future"].set_exception(e)

            finally:
                self.queue.task_done()

    async def add_task(self, query: str, context: list[str]):
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        await self.queue.put({
            "query": query,
            "context": context,
            "future": future
        })
        logger.info(f"Task added to queue: {query}")
        return await future
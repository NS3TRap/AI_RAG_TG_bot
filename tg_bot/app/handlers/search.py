from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging

from tg_bot.app.services.chroma_service import ChromaService
from tg_bot.app.handlers.states import UserStates

router = Router()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.message(Command("search"))
async def cmd_search(message: types.Message, state: FSMContext) -> None:
    await state.set_state(UserStates.search)
    await message.answer(
        "Напишите текст, который вы хотите найти в базе данных."
    )
    logger.info("Пользователь %s начал поиск текста", message.from_user.id)

@router.message(UserStates.search)
async def process_search(message: types.Message, state: FSMContext) -> None:
    query = message.text
    chroma_service = ChromaService()
    results = chroma_service.search_query(
        query,
        metadata={"user_id": message.from_user.id}
    )
    await state.clear()

    if results:
        response = "Найдены следующие результаты:\n\n"
        for idx, result in enumerate(results, start=1):
            response += f"{idx}. {result['text']}\n"
    else:
        response = "К сожалению, ничего не найдено по вашему запросу."

    await message.answer(response)
    logger.info("Пользователь %s завершил поиск текста: %s", message.from_user.id, query)
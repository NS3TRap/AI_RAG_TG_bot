from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging

from tg_bot.app.services.chroma_service import ChromaService
from tg_bot.app.handlers.states import UserStates

router = Router()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.message(Command("add"))
async def cmd_add(message: types.Message, state: FSMContext) -> None:
    await state.set_state(UserStates.add)
    await message.answer(
        "Напишите текст, который вы хотите добавить в базу данных."
    )
    logger.info("Пользователь %s начал добавление текста", message.from_user.id)

@router.message(UserStates.add)
async def process_add(message: types.Message, state: FSMContext) -> None:
    text_to_add = message.text
    chroma_service = ChromaService()
    chroma_service.insert_query(
        text_to_add,
        metadata={"user_id": message.from_user.id}
    )
    await state.clear()
    await message.answer("Текст успешно добавлен в базу данных!")
    logger.info("Пользователь %s добавил текст: %s", message.from_user.id, text_to_add)
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging

from tg_bot.app.services.chroma_service import ChromaService
from tg_bot.app.handlers.states import UserStates
router = Router()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)    

@router.message(Command("delete"))
async def cmd_delete(message: types.Message, state: FSMContext) -> None:
    chroma_service = ChromaService()
    data = chroma_service.list_query()

    if not data:
        await message.answer("База данных пуста, удалять нечего.")
        return

    await state.update_data(items=data)
    await state.set_state(UserStates.delete)

    text = "Выбери номер записи для удаления:\n\n"
    for i, item in enumerate(data, start=1):
        text += f"{i}. {item[1]}\n"

    await message.answer(text)

@router.message(UserStates.delete)
async def process_delete(message: types.Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    items = user_data.get("items", [])

    try:
        index = int(message.text) - 1
        if index < 0 or index >= len(items):
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введи корректный номер.")
        return

    doc_id, doc_text = items[index]

    chroma_service = ChromaService()
    chroma_service.delete_query(doc_id)

    await state.clear()
    await message.answer(f"Удалено:\n{doc_text}")
    
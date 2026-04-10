from aiogram import Router, types
from aiogram.filters import Command

from tg_bot.app.services.chroma_service import ChromaService

router = Router()


@router.message(Command("list"))
async def cmd_list(message: types.Message) -> None:
    chroma_service = ChromaService()
    data = chroma_service.list_query()

    if not data:
        await message.answer("База данных пуста.")
        return

    text = "Текущие записи в базе данных:\n\n"
    for i, item in enumerate(data, start=1):
        text += f"{i}. {item[1]}\n"

    await message.answer(text)
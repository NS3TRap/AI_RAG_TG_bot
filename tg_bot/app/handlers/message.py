from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    await message.answer(
        "Привет! Я простой Telegram бот на aiogram через webhook.\n"
        "Отправь любой текст, и я отвечу тем же."
    )

@router.message()
async def echo(message: types.Message) -> None:
    if message.text:
        await message.answer(f"Ты написал: {message.text}")

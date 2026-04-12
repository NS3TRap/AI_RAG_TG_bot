from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging

from tg_bot.app.services.chroma_service import ChromaService
from tg_bot.app.services.llm_client import llm_client
from tg_bot.app.handlers.states import UserStates

router = Router()
chroma = ChromaService()

@router.message(Command("userag"))
async def cmd_use_rag(message: types.Message, state: FSMContext) -> None:
    await state.set_state(UserStates.useRag)
    await message.answer("Теперь я буду использовать RAG для ответов. Отправь текст.")

@router.message(Command("norag"))
async def cmd_no_rag(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("RAG отключён. Теперь обычный режим.")

@router.message(UserStates.useRag)
async def handle_rag_message(message: types.Message, state: FSMContext) -> None:
    query = message.text

    try:
        context = chroma.select_query(query)
        if not context:
            await message.answer("Контекст не найден")
            return

        answer = await llm_client.generate(query, context)
        await message.answer(answer, parse_mode=None)
    
    except Exception as e:
        logging.exception("RAG error")
        await message.answer("Ошибка при обработке RAG")

@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    await message.answer(
        "Привет! Я простой Telegram бот на aiogram через webhook.\n"
        "Отправь любой текст, и я отвечу тем же."
    )

@router.message()
async def echo(message: types.Message) -> None:
    if not message.text:
        return

    try:
        answer = await llm_client.generate(message.text)
        await message.answer(answer, parse_mode=None)

    except Exception as e:
        logging.exception("LLM error")
        await message.answer("Ошибка при обращении к LLM")

# AI RAG Telegram Bot

## О проекте

Этот проект представляет собой Telegram-бота с поддержкой **RAG (Retrieval-Augmented Generation)** — подхода, при котором ответы формируются на основе заранее сохранённых данных.

Бот позволяет:

* сохранять текстовые данные в векторное хранилище
* находить релевантные документы по запросу пользователя
* использовать их для формирования ответа

Кроме того, реализовано управление режимом RAG прямо через команды Telegram.

**Основные возможности:**

* Добавление данных в векторную базу (команда /add);
* Поиск похожих записей (команда /search);
* Просмотр данных в векторной базе (команда /list);
* Удаление записей (команда /delete);
* Переключение режимов работы
  * с RAG (команда /userag);
  * без RAG (команда /norag);

### Команды бота


| Команда | Описание                                             |
| -------------- | ------------------------------------------------------------ |
| `/start`       | Запустить бота                                  |
| `/help`        | Показать справку                              |
| `/add`         | Добавить данные в векторную базу |
| `/delete`      | Удалить запись из базы                    |
| `/list`        | Показать все сохранённые данные  |
| `/search`      | Найти похожие записи                       |
| `/userag`      | Включить использование RAG              |
| `/norag`       | Отключить использование RAG            |

## Архитектура проекта

Проект состоит из двух независимых сервисов:

1. Telegram Bot Service

Отвечает за:

* обработку сообщений пользователей
* управление состоянием (RAG включён / выключен)
* работу с векторной базой данных (ChromaDB)

Используемая модель эмбеддингов:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

Работает в режиме WebHook, используя ngrok для получения домена и сертификата.

2. LLM Service

Отвечает за:

* приём запросов от Telegram-сервиса
* постановку задач в очередь
* взаимодействие с LLM
* возврат результата

Особенности:

* асинхронная обработка через очередь
* изолированная работа с моделью
* масштабируемость (можно вынести на отдельный сервер)

## Как это работает

1. Пользователь отправляет сообщение боту
2. Бот:
   * проверяет, включён ли режим RAG
   * при необходимости ищет релевантные данные в ChromaDB
3. Формируется запрос к LLM (с контекстом или без)
4. Запрос отправляется в LLM Service
5. LLM обрабатывает запрос
6. Ответ возвращается в Telegram Bot
7. Бот отправляет результат пользователю

### Примеры кода

Листин 1. Генерация ответа

```python
from fastapi import APIRouter
from llm_service.app.models.schemas import GenerateRequest, GenerateResponse
from llm_service.app.services.queue import llm_queue

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    answer = await llm_queue.add_task(
        query=request.query,
        context=request.context
    )

    return GenerateResponse(answer=answer)
```

Листинг 2. Управление состояними.

```python
@router.message(Command("userag"))
async def cmd_use_rag(message: types.Message, state: FSMContext) -> None:
    await state.set_state(UserStates.useRag)
    await message.answer("Теперь я буду использовать RAG для ответов. Отправь текст.")

@router.message(Command("norag"))
async def cmd_no_rag(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("RAG отключён. Теперь обычный режим.")
```

Листинг 3. Обработка запросов с телеграмма.

```python
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging

from tg_bot.app.services.chroma_service import ChromaService
from tg_bot.app.services.llm_client import llm_client
from tg_bot.app.handlers.states import UserStates

router = Router()
chroma = ChromaService()

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

```

## Запуск проекта

1. Клонирование репозитория

```bash
git clone repo_url
cd project_folder
```

2. Создание виртуального окружения

```bash
python **-m** venv venv
source venv/bin/activate  **# Linux / Mac**
venv\\Scripts\\activate     **# Windows**
```

3. Установка зависимостей

```Bash
pip install **-r** requirements.txt
```

4. Настройка окружения

Укажите необходимые параметры в `.env`

5. Запуск сервисов

Запуск Telegram-бота

```
python -m tg_bot.app.main
```

Запуск LLM-сервиса

```
python -m llm_service.app.main
```

## Публичный доступ через ngrok (опционально)

Если LLM-сервис или Telegram-бот должны быть доступны извне (например, при работе через webhook или при разнесённых сервисах), можно использовать **ngrok**.

1. Установите ngrok (см. официальный сайт: [https://ngrok.com](https://ngrok.com))
2. Запустите туннель:

```
ngrok http 8000
```

(где `8000` — порт вашего LLM-сервиса или Telegram-бота)

3. Получите публичный URL, например:

```
https://abcd-1234.ngrok-free.app
```

4. Используйте этот URL:

* в `.env` (например, `WEBHOOK_URL`)
* или при настройке webhook в LLM

## Тестирование ответов модели с RAG / без RAG

Для тестирования качества генерации использовалась модель:<br>
LiquidAI/LFM2.5-1.2B-Instruct<br>

* Кол-во параметров: 1.17B;
* Кол-во слоёв: 16;
* Длина контекста: 32,768 токенов;
* Размер словаря: 65,536;
* Языки: английский, арабский, китайский, французский, немецкий, японский, корейский, испанский;
* Параметры генерации:
  * temperature: 0.2;
  * top_p: 0.85;
  * top_k: 50 (default);
  * repetition_penalty: 1.2.

Сравнивались ответы модели:

* без использования RAG
* с использованием RAG (с контекстом из базы данных)

### Данные в базе

В векторной базе данных (ChromaDB) хранятся следующие примеры:

> * Погода, состояние атмосферы в рассматриваемом месте в определённый момент или за ограниченный промежуток времени (сутки, месяц, год).
> * Металлоло́м — общее, собирательное название различного металлического мусора, утилизируемого или не утилизируемого во вторичном металлургическом цикле. Чаще всего к металлолому относят специально концентрируемый в отведенных местах металлический мусор для последующей переработки или утилизации.
> * STM32F103C8T6 — это популярный 32-битный микроконтроллер от STMicroelectronics на базе ядра ARM Cortex-M3 (72 МГц), известный как «сердце» отладочной платы Blue Pill. Он часто используется в электронике благодаря высокой производительности, наличию USB, 64 КБ Flash-памяти и низкой цене.

### Сравнение ответов

<table><tr><td>Запрос пользователя</td><td>Ответ без RAG</td><td>Ответ с RAG</td></tr>
<tr><td>Расскажи про металлолом</td><td>Металло — это общее название для групп аlynn-ме탈,включая</br> знанные элементы неродон (Zn), медаль (Ag), циркديوم (Cu) и т.д.</br> Основные особенности</br>**Использование** Используется в промышленности,</br> электроника, транспорте и других областях.</br>**Признаки** Можно найти его на рынках, в производстве</br> устройств и машинах.</br>**Сообщения** Возможны проблемы с поведением при</br> высоких температурах или из-за загрязнения.</br>
Если хотите, могу подробнее рассказать о какой-то</br> конкретном металле!</td>
<td>Металлоло́м — это совокупность разных материалов из</br>промышленности, которые после использования становятся</br> мусором. Это включает металлические детали, старые машины,</br> конструкции и другие предметы, которые нуждаются в</br> переработке или утилизации.</td></tr>
<tr><td>STM32F103C8T6</td><td>STM32F103C8T6 — это микроконтроллер ARM Cortex-M3, 16 MHz, 4KB RAM,<br> 2MB Flash.</td>
<td>STM32F103C8T6 — это 32-битный mikrocontroller с ARM Cortex-M3,<br> 72 MHz, 64 KB Flash, ideal для разнообразных приложений.</td></tr></table>

### Вывод

* Без RAG модель даёт **общие и менее точные ответы**
* С RAG ответы становятся:
  * более точными
  * контекстно обоснованными
  * ближе к данным, хранящимся в базе

Кроме того, использование RAG позволяет **контролировать знания модели**, опираясь на собственную базу данных, а не только на предобученные параметры модели.

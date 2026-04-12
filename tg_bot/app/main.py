import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

from .config import bot_config, BotConfig
from .handlers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def on_startup(app: web.Application) -> None:
    config: BotConfig = app["config"]
    bot: Bot = app["bot"]

    logger.info("Запускаю webhook: %s", config.webhook_full_url)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(config.webhook_full_url)
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
    ])


async def on_shutdown(app: web.Application) -> None:
    bot: Bot = app["bot"]
    logger.info("Останавливаю бота и удаляю webhook")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()


async def health(request: web.Request) -> web.Response:
    return web.Response(text="ok")


def create_app(config: BotConfig) -> web.Application:
    bot = Bot(token=config.token, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)

    app = web.Application()
    app["config"] = config
    app["bot"] = bot
    app["dispatcher"] = dp

    app.router.add_post(config.webhook_path, SimpleRequestHandler(dispatcher=dp, bot=bot).handle)
    app.router.add_get("/health", health)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    return app


def main() -> None:
    config = BotConfig.from_env()
    app = create_app(config)
    web.run_app(app, host=config.host, port=config.port)


if __name__ == "__main__":
    main()

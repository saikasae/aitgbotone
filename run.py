import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from app.admin import admin
from app.database.models import async_main
from app.user import user
from app.utils.description import set_default_description


async def main():
    load_dotenv()
    bot = Bot(
        token=os.getenv("TOKEN"),
        default=DefaultBotProperties(parse_mode="Markdown"),
    )
    dp = Dispatcher()
    dp.include_routers(user, admin)
    dp.startup.register(on_startup)
    await set_default_description(bot)
    await dp.start_polling(bot)


async def on_startup():
    await async_main()


if __name__ == __name__:
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")

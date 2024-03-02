import os
import asyncio
import logging
import sys
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker
from crypto_track.database.run import init_db
from crypto_track.database.manager import AsyncDatabaseManager
from crypto_track.api.manager import AsyncAPIManager
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from crypto_track.signup import signup_router
from crypto_track.profile import profile_router
from crypto_track.crypto_price import crypto_price_router
from crypto_track.update_price import update_all_cryptos


dp = Dispatcher()
# Load .env variables
load_dotenv()
# Aiogram logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


async def main():
    DATABASE_URL = os.getenv('DATABASE_URL')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    API_KEY = os.getenv('API_KEY')

    DB_ENGINE = await init_db(database_url=DATABASE_URL)
    async_session = async_sessionmaker(DB_ENGINE, expire_on_commit=False)
    database_manager_instance = AsyncDatabaseManager(async_session=async_session)
    api_manager_instance = AsyncAPIManager(api_key=API_KEY)

    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp.include_router(signup_router)
    dp.include_router(profile_router)
    dp.include_router(crypto_price_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 

import os
import asyncio
import logging
import sys
import threading
import time
import asyncio
import schedule
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
from crypto_track.update_price import update_prices_manager


dp = Dispatcher()
# Load .env variables
load_dotenv()
# Aiogram logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def run_continuously(interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def run_prices_updater():
    asyncio.run(update_prices_manager())

async def main():
    DATABASE_URL = os.getenv('DATABASE_URL')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    API_KEY = os.getenv('API_KEY')

    DB_ENGINE = await init_db(database_url=DATABASE_URL)
    async_session = async_sessionmaker(DB_ENGINE, expire_on_commit=False)
    database_manager_instance = AsyncDatabaseManager(async_session=async_session)
    api_manager_instance = AsyncAPIManager(api_key=API_KEY)

    schedule.every(5).minutes.do(run_prices_updater)
    stop_run_continuously = run_continuously()

    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp.include_router(signup_router)
    dp.include_router(profile_router)
    dp.include_router(crypto_price_router)
    await dp.start_polling(bot)
    stop_run_continuously.set()

if __name__ == "__main__":
    asyncio.run(main()) 

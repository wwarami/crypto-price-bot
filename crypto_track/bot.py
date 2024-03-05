import os
from aiogram import Bot
from aiogram.enums import ParseMode
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)

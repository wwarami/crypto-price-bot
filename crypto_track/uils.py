from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup)

def generate_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='پروفایل 🧒')],
            [KeyboardButton(text='دریافت قیمت لحظه ای 📈')]
        ],
        resize_keyboard=True
    )

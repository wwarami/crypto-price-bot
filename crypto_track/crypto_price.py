from aiogram import Router, F
from aiogram.types import (Message, ReplyKeyboardRemove)
from crypto_track.database.manager import AsyncDatabaseManager


def load_crypto_price_messages():
    with open('messages/crypto_price/account_not_exists.txt', 'r', encoding='utf-8') as file:
        account_not_exists_text = file.read()
    with open('messages/crypto_price/price_list.txt', 'r', encoding='utf-8') as file:
        price_list_text = file.read()

    return account_not_exists_text, price_list_text
account_not_exists_text, price_list_text = load_crypto_price_messages()

crypto_price_router = Router()


@crypto_price_router.message(F.text == 'دریافت قیمت لحظه ای 📈')
async def get_user_crypto_prices(message: Message):
    user = await AsyncDatabaseManager().get_user_with_cryptos(user_id=message.from_user.id)
    print(user)
    if not user:
        await message.reply(account_not_exists_text, reply_markup=ReplyKeyboardRemove())
        return
    crypto_ids = [str(crypto.id) for crypto in user.tracking_cryptos]
    cryptos_prices = await AsyncDatabaseManager().get_multiple_cryptos_current_price(crypto_ids=crypto_ids)

    prices_formated = [f"🔹{crypto_price.crypto.name}: <code>{crypto_price.price}</code>💲" for crypto_price in cryptos_prices]
    
    await message.answer(price_list_text.format(cryptos_prices='\n'.join(prices_formated)))

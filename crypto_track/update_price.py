from crypto_track.database.manager import AsyncDatabaseManager
from crypto_track.api.manager import AsyncAPIManager
from crypto_track.bot import bot
from datetime import datetime
from crypto_track.database.models import Crypto


with open('messages/crypto_price/price_list.txt', 'r', encoding='utf-8') as file:
        price_list_text = file.read()


async def update_prices_manager():
    cryptos = await update_all_cryptos()
    users = await AsyncDatabaseManager().get_multiple_users_with_cryptos()
    cryptos_id_price_dict = generate_id_price_cryptos_dict(cryptos)

    for user in users:
        now = datetime.now(user.last_update.tzinfo)
        minutes_ago = round(((now - user.last_update).total_seconds() / 60))

        if minutes_ago >= int(user.how_often.value):
            await send_update_to_user(user, cryptos_id_price_dict)
            await AsyncDatabaseManager().update_user(user_id=user.id, new_last_update=now)
            

def generate_id_price_cryptos_dict(cryptos):
    return {crypto.id: crypto.current_price.price for crypto in cryptos}

async def send_update_to_user(user, cryptos_id_price):
    new_update = {}
    for crypto in user.tracking_cryptos:
        new_update[crypto] = cryptos_id_price.get(crypto.id)

    prices_formated = [f"🔹{crypto.name}: <code>{price}</code>💲" for crypto, price in new_update.items()]
    
    await bot.send_message(chat_id=user.id ,text=price_list_text.format(cryptos_prices='\n'.join(prices_formated)))


async def update_all_cryptos() -> list[Crypto]:
    available_cryptos = await AsyncDatabaseManager().get_all_cryptos()
    cryptos_symbols_list = [crypto.symbol for crypto in available_cryptos]
    try:
        update_raw_data = await AsyncAPIManager().get_crpyto_prices(cryptos_symbols_list)
        update_data = {key: value['USD'] for key, value in update_raw_data.items()}
        
        updated_cryptos = await AsyncDatabaseManager().update_cryptos_prices_by_symbol(data=update_data)

        return updated_cryptos
    except ConnectionError:
        print('\u001b[31mConnection error happend while trying to update Crypto List.\u001b[37m')
    except Exception as ex:
        print(f'\u001b[31mException happend while trying to update Crypto List.\nDetail:{ex}\u001b[37m')

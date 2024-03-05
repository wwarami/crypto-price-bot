from crypto_track.database.manager import AsyncDatabaseManager
from crypto_track.api.manager import AsyncAPIManager
from crypto_track.bot import bot
from datetime import datetime


from crypto_track.database.models import Crypto

async def update_prices_manager():
    cryptos = await update_all_cryptos()
    users = await AsyncDatabaseManager().get_multiple_users_with_cryptos()
    need_update = []

    for user in users:
        now = datetime.now(user.last_update.tzinfo)
        minutes_ago = round(((now - user.last_update).total_seconds() / 60))

        if minutes_ago >= int(user.how_often.value):
            need_update.append(user)
            ...


async def update_all_cryptos() -> list[Crypto]:
    available_cryptos = await AsyncDatabaseManager().get_all_cryptos()
    cryptos_symbols_list = [crypto.symbol for crypto in available_cryptos]
    try:
        update_raw_data = await AsyncAPIManager().get_crpyto_prices(cryptos_symbols_list)
        update_data = {key: value['USD'] for key, value in update_raw_data.items()}
        
        await AsyncDatabaseManager().update_cryptos_prices_by_symbol(data=update_data)

        return available_cryptos
    except ConnectionError:
        print('\u001b[31mConnection error happend while trying to update Crypto List.\u001b[37m')
    except Exception as ex:
        print(f'\u001b[31mException happend while trying to update Crypto List.\nDetail:{ex}\u001b[37m')

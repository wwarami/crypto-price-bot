# Crypto Price Telegram Bot
Track any crypto price using this bot!

# How to start?
1. **Create a ```.env``` file and put the required data in it**
```python
DATABASE_URL = "sqlite+aiosqlite:///cryptotrack.db"
BOT_TOKEN = ""
API_KEY = ""
```
* BOT_TOKEN: The api token for your bot, get it from [Botfather](https://telegram.me/BotFather).
* API_KEY: The api key for fetching cryptos prices. Get it from [CryptoCompare](https://min-api.cryptocompare.com/).

2. **Install the requirements**
```commandline
pip install -r requirements.txt
```
3. **Start the bot**
```commandline
python main.py bot
```
4. **Use the CLI for managing the bot**
```commandline
python main.py cli
```
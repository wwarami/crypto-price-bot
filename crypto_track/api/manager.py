import aiohttp
import json

class AsyncAPIManager:
    _instance = None
    _is_initialized = False

    def __new__(cls, api_key=None):
        if cls._instance is None:
            cls._instance = super(AsyncAPIManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, api_key: str=None):
        if not self._is_initialized:
            if not api_key:
                raise ValueError('AsyncAPIManager should be initialized with an api key first.')
            self.api_key = api_key
            self._is_initialized = True

    async def get_crpyto_prices(self, ctyptos_symbols: list) -> dict:
        url = f'https://min-api.cryptocompare.com/data/pricemulti?fsyms={",".join(ctyptos_symbols)}&tsyms=USD&api_key={self.api_key}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise ConnectionError('A problem happend while fetching the api.')
                response = await resp.text()
                return json.loads(response)


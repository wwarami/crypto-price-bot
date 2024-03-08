import sys
import os
from rich.console import Console
from crypto_track.database.manager import AsyncDatabaseManager
from cli.utils import validate_price
from crypto_track.update_price import update_all_cryptos

class CLIManager:
    ri = Console()

    BANNER = """
 ██████╗██████╗ ██╗   ██╗██████╗ ████████╗ ██████╗     ██████╗ ██████╗ ██╗ ██████╗███████╗    ████████╗██████╗  █████╗  ██████╗██╗  ██╗
██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗    ██╔══██╗██╔══██╗██║██╔════╝██╔════╝    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝
██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║   ██║    ██████╔╝██████╔╝██║██║     █████╗         ██║   ██████╔╝███████║██║     █████╔╝ 
██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║   ██║    ██╔═══╝ ██╔══██╗██║██║     ██╔══╝         ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ 
╚██████╗██║  ██║   ██║   ██║        ██║   ╚██████╔╝    ██║     ██║  ██║██║╚██████╗███████╗       ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗
 ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝     ╚═╝     ╚═╝  ╚═╝╚═╝ ╚═════╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
A telegram bot for tracking any crypto you want!
Developer: wwwaramii
        ---------------------------------------------------------        """
    COMMANDS = """Select what you want to do:
1- Add new crypto
2- Delete a crypto
3- Get all cryptos
4- Get all users
5- Delete a user
6- Delete all prices of a crypto
7- Update all cryptos
8- Quit"""

    async def start(self):
        # Start the program
        os.system('clear')
        self.ri.print(self.BANNER, style='blue')
        while True:
            command = self.get_command()
            try:
                await self.parse_command(command)
            except KeyboardInterrupt:
                self.ri.print('\nCommand cancelled.', style='green bold')
                continue
            except Exception as ex:
                self.ri.print(f'Something went wrong while parsing your command. Detail: {ex}', style='red')
                break

    def get_command(self):
        self.ri.print(self.COMMANDS, style='white')
        self.ri.print('Select what you want to do: ', style='blue bold', end='')
        return input()

    async def parse_command(self, command: str):
        match command.strip():
            case '1':
                await self.add_new_crypto()
            case '2':
                await self.delete_crypto()
            case '3':
                await self.get_all_cryptos()
            case '4':
                await self.get_all_users()
            case '5':
                await self.delete_user()
            case '6':
                await self.delete_prices_of_crypto()
            case '7':
                await self.update_cryptos()
            case '8':
                sys.exit()
            case _:
                self.ri.print('Not a valid command! Enter the command number please.', style='green bold')
    
    async def add_new_crypto(self):
        self.ri.print('*Creating a new Crypto(Use "ctrl + c" to cancel.): ', style='bold')
        
        # Get crypto name
        while True:
            self.ri.print('Enter the crypto name: ', end='', style='bold')
            name = input()
            if name == '':
                self.ri.print('Please enter a valid name.', style='red')
            else:
                break
        # Get crypto symbol
        while True:
            self.ri.print('Enter the crypto symbol: ', end='', style='bold')
            symbol = input().upper()
            if symbol == '':
                self.ri.print('Please enter a valid symbol.', style='red')
            else:
                break       
        # Get crypto current price
        while True:
            self.ri.print('Enter the crypto current price: ', end='', style='bold')
            price = input()
            if price == '':
                self.ri.print('Please enter a valid symbol.', style='red')
            elif not validate_price(price):
                self.ri.print('Please enter a valid symbol.', style='red')
            else:
                price = float(price)
                break
        
        try:
            crypto = await AsyncDatabaseManager().create_new_crypto(crypto_name=name.strip(),
                                                           symbol=symbol.strip(),
                                                           current_price=price)
            self.ri.print(f'New crypto created: {crypto}.')
        except Exception as ex:
            self.ri.print(f'Something went wrong while trying to create the crypto! Detail: {ex}', style='red bold')

    async def delete_crypto(self):
        while True:
            self.ri.print('*Delete a Crypto(Use "ctrl + c" to cancel.): ', style='bold')

            self.ri.print('Enter the crypto id to delete: ', end='', style='bold')
            crypto_id = input()
            result = await AsyncDatabaseManager().delete_crypto(crypto_id=crypto_id)
            if result:
                self.ri.print(f'Crypto with (id={crypto_id}), deleted.', style='green bold')
            else:
                self.ri.print(f'Could not delete Crypto with (id={crypto_id})!.', style='red bold')

    async def get_all_cryptos(self):
        self.ri.print('*List of all cryptos:(Use "ctrl + c" to cancel). ', style='bold')
        self.ri.print('Press Enter: ', style='bold blue', end='')
        input()
        cryptos_prices = await AsyncDatabaseManager().get_multiple_cryptos_current_price()
        for index, price in enumerate(cryptos_prices):
            self.ri.print(f'{index+1}- {price.crypto}, Price: {price.price}$')

        self.ri.print('Press Enter to continue: ', end='')
        input()
    
    async def get_all_users(self):
        self.ri.print('*List of all users:(Use "ctrl + c" to cancel). ', style='bold')
        self.ri.print('Press Enter: ', style='bold blue', end='')
        input()
        users = await AsyncDatabaseManager().get_multiple_users_with_cryptos()
        for index, user in enumerate(users):
            self.ri.print(f'{index+1}- {user}, Cryptos: {user.tracking_cryptos}\n')

        self.ri.print('Press Enter to continue: ', end='')
        input()

    async def delete_user(self):
        while True:
            self.ri.print('*Delete a User(Use "ctrl + c" to cancel.): ', style='bold')

            self.ri.print('Enter the user id to delete: ', end='', style='bold')
            user_id = input()
            result = await AsyncDatabaseManager().delete_user(user_id=user_id)
            if result:
                self.ri.print(f'User with (id={user_id}), deleted.', style='green bold')
            else:
                self.ri.print(f'Could not delete User with (id={user_id})!.', style='red bold')

    async def update_cryptos(self):
        self.ri.print('*Update all cryptos(Use "ctrl + c" to cancel.): ', style='bold')
        self.ri.print('Press Enter: ', style='bold blue', end='')
        input()
        res = await update_all_cryptos()
        if res:
            self.ri.print('All cryptos updated.', style='green bold')
        else:
            self.ri.print('Could not update cryptos. Check the logs.', style='red bold')

    async def delete_prices_of_crypto(self):
        while True:
            self.ri.print('*Delete a Cryptos all prices (Use "ctrl + c" to cancel.): ', style='bold')

            self.ri.print('Enter the crypto id: ', end='', style='bold')
            crypto_id = input()
            
            result = await AsyncDatabaseManager().delete_all_prices_of_crypto(crypto_id=crypto_id)
            if result:
                self.ri.print(f'All prices of crypto with (id={crypto_id}), deleted.', style='green bold')
            else:
                self.ri.print(f'Could not delete all prices of crypto (id={crypto_id}).', style='red bold')

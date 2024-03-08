from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from crypto_track.database.models import User, Crypto, Price
from sqlalchemy.future import select
from crypto_track.enums import TimeOptions
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy import select, func

class AsyncDatabaseManager:
    _instance = None
    _is_initialized = False

    def __new__(cls, async_session=None):
        if cls._instance is None:
            cls._instance = super(AsyncDatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, async_session: AsyncSession=None):
        if not self._is_initialized:
            if not async_session:
                raise ValueError('AsyncDatabaseManager should be initialized with an async session first.')
            self.async_session = async_session
            self._is_initialized = True
    
    async def create_new_user(self, 
                          user_id: str, 
                          user_name: str, 
                          how_often: TimeOptions) -> User:
        async with self.async_session() as session:
            new_user = User(id=user_id, name=user_name, how_often=how_often)
            session.add(new_user)
            await session.commit()

            return new_user

    async def create_new_user_and_add_cryptos(self, 
                                            user_id: str, 
                                            user_name: str, 
                                            how_often: TimeOptions, 
                                            cryptos_to_add_ids: List[str]) -> User:
        async with self.async_session() as session:
            new_user = User(id=user_id, name=user_name, how_often=how_often)
            
            cryptos = await session.execute(select(Crypto).filter(Crypto.id.in_(cryptos_to_add_ids)))
            cryptos_list = cryptos.scalars().all()

            if not cryptos_list and cryptos_to_add_ids:
                raise ValueError("No cryptos found with provided IDs.")
            
            new_user.tracking_cryptos.extend(cryptos_list)
            
            session.add(new_user)
            await session.commit()

            return new_user
    
    async def update_user(self, 
                          user_id: str,
                          new_user_name: str = None,
                          new_how_often: TimeOptions = None,
                          new_last_update: datetime =None) -> User:
        async with self.async_session() as session:
            query = select(User).filter(User.id == user_id)
            result = await session.execute(query)
            user = result.scalars().first()
            if new_user_name:
                user.name = new_user_name
            if new_how_often:
                user.how_often = new_how_often

            if new_last_update:
                user.last_update = new_last_update

            await session.commit()
            return user

    async def check_user_exists(self, 
                                user_id: str) -> User | None:
        async with self.async_session() as session:
            query = select(User).filter(User.id == user_id)
            result = await session.execute(query)
            user = result.scalars().first()

            return user if user else None
    
    async def add_cryptos_to_user_tracked(self,
                                      user_id: str,
                                      cryptos_to_add_ids: List[str]) -> User:
        # Gets a user id and list of crypto ids for the user to track.
        async with self.async_session() as session:
            result = await session.execute(
                select(User).options(selectinload(User.tracking_cryptos)).filter_by(id=user_id)
            )
            user = result.scalars().first()

            if not user:
                raise ValueError("User not found.")

            cryptos = await session.execute(select(Crypto).filter(Crypto.id.in_(cryptos_to_add_ids)))
            cryptos_list = cryptos.scalars().all()

            if not cryptos_list:
                raise ValueError("No cryptos found with provided IDs.")

            user.tracking_cryptos = cryptos_list
            await session.commit()

            return user
    
    async def get_user_cryptos(self, 
                           user_id: str) -> List[Crypto]:
        async with self.async_session() as session:
            query = select(User).options(selectinload(User.tracking_cryptos)).filter(User.id == user_id)
            result = await session.execute(query)
            user = result.scalars().first()

            if user:
                return user.tracking_cryptos
            else:
                return None
    
    async def get_user_with_cryptos(self, user_id: str) -> User | None:
        async with self.async_session() as session:
            # Perform a query to fetch the user and eagerly load the tracking_cryptos relationship
            result = await session.execute(
                select(User).options(selectinload(User.tracking_cryptos)).filter_by(id=user_id)
            )
            user = result.scalars().first()

            return user
    
    async def delete_user(self, user_id: str) -> bool:
        async with self.async_session() as session:
            query = select(User).filter_by(id=user_id)
            result = await session.execute(query)
            user = result.scalars().first()
            
            if user:
                await session.delete(user)
                await session.commit()
                return True
            
            return False

    async def delete_crypto(self, crypto_id: str) -> bool:
        async with self.async_session() as session:
            query = select(Crypto).filter_by(id=crypto_id)
            result = await session.execute(query)
            crypto = result.scalars().first()
            
            if crypto:
                await session.delete(crypto)
                await session.commit()
                return True
            return False

    async def get_multiple_users_with_cryptos(self, user_ids: Optional[List[str]] = None) -> List[User]:
        async with self.async_session() as session:
            # Start constructing the query
            query = select(User).options(selectinload(User.tracking_cryptos))
            
            # If user_ids is provided and not empty, filter by the given IDs
            if user_ids:
                query = query.filter(User.id.in_(user_ids))
            
            result = await session.execute(query)
            users = result.scalars().all()
            
            return users
        
    async def create_new_crypto(self,
                            crypto_name: str, 
                            symbol: str,
                            current_price: float) -> Crypto:
        async with self.async_session() as session:
            new_crypto = Crypto(name=crypto_name,
                                symbol=symbol)
        
            session.add(new_crypto)
            await session.flush()

            new_price = Price(crypto_id=new_crypto.id, price=current_price)
            session.add(new_price)

            await session.commit()

            return new_crypto
    
    async def get_all_cryptos(self) -> List[Crypto]:
        async with self.async_session() as session:
            query = select(Crypto)
            result = await session.execute(query)
            cryptos = result.scalars().all()
            
            return cryptos
    
    async def get_crypto_all_prices(self,
                            crypto_id: str) -> List[Price]:
        async with self.async_session() as session:
            query = select(Price).filter(Price.crypto_id == crypto_id)
            result = await session.execute(query)
            prices = result.scalars().all()
            return prices
        
    async def delete_all_prices_of_crypto(self, crypto_id=str) -> bool:
        async with self.async_session() as session:
            query = select(Price).filter(Price.crypto_id == crypto_id)
            result = await session.execute(query)
            prices = result.scalars().all()

            if not prices:
                return False
            
            for price in prices:
                await session.delete(price)
            
            await session.commit()
            return True

    async def get_crypto_current_price(self,
                                   crypto_id: str) -> Price:
        async with self.async_session() as session:
            query = select(Price).filter(Price.crypto_id == crypto_id). \
                                                order_by(Price.date.desc()).limit(1)
            result = await session.execute(query)
            current_price = result.scalars().first()

            return current_price
    
    async def get_multiple_cryptos_current_price(self, crypto_ids: List[str] = None):
        async with self.async_session() as session:
            # Subquery to find the latest price date for each of the specified crypto_ids  
            if crypto_ids:
                latest_price_subquery = select(
                    Price.crypto_id,
                    func.max(Price.date).label('max_date')
                ).where(Price.crypto_id.in_(crypto_ids)).group_by(Price.crypto_id).subquery('latest_price')
            else:
                latest_price_subquery = select(
                        Price.crypto_id,
                        func.max(Price.date).label('max_date')
                    ).group_by(Price.crypto_id).subquery('latest_price')

            # Aliasing the Price table to join with the subquery
            latest_price = aliased(Price)

            # Query to select the prices that match the latest date found for each specified crypto
            query = (
                select(Price)
                .join(
                    latest_price_subquery,
                    (Price.crypto_id == latest_price_subquery.c.crypto_id) &
                    (Price.date == latest_price_subquery.c.max_date)
                ).options(selectinload(Price.crypto))
            )

            result = await session.execute(query)
            current_prices = result.scalars().all()

            return current_prices
    
    async def add_new_price(self, 
                        crypto_id: str,
                        new_price: float) -> Price:

        async with self.async_session() as session:
            new_price = Price(crypto_id=crypto_id, price=new_price)
            session.add(new_price)
            await session.commit()
            return new_price

    async def update_cryptos_prices_by_symbol(self,
                                           data: dict[str, float]) -> list[Crypto]:
        async with self.async_session() as session:
            query = select(Crypto)
            result = await session.execute(query)
            cryptos = result.scalars().all()

            for crypto in cryptos:
                new_price = data.get(crypto.symbol)
                if not new_price:
                    continue
                new_price = Price(crypto_id=crypto.id, price=new_price)
                crypto.current_price = new_price
                session.add(new_price)
            
            await session.commit()
            return cryptos
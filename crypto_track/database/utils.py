"""
This functions are used to interact with the database.
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from crypto_track.database.models import User, Crypto, Price
from sqlalchemy.future import select
from crypto_track.enums import TimeOptions
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy import select, func


async def check_user_exists(async_session: AsyncSession, user_id: str) -> User | None:
    async with async_session() as session:
        query = select(User).filter(User.id == user_id)
        result = await session.execute(query)
        user = result.scalars().first()

        return user if user else None

async def create_new_user(async_session: AsyncSession, 
                          user_id: str, 
                          user_name: str, 
                          how_often: TimeOptions) -> User:
    async with async_session() as session:
        new_user = User(id=user_id, name=user_name, how_often=how_often)
        session.add(new_user)
        await session.commit()

        return new_user


async def add_cryptos_to_user_tracked(async_session: AsyncSession,
                                      user_id: str,
                                      cryptos_to_add_ids: List[str]) -> User:
    # Gets a user id and list of crypto ids for the user to track.
    async with async_session() as session:
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

        for crypto in cryptos_list:
            if crypto not in user.tracking_cryptos:
                user.tracking_cryptos.append(crypto)

        await session.commit()

        return user


async def get_user_cryptos(async_session: AsyncSession, 
                           user_id: int) -> List[Crypto]:
    async with async_session() as session:
        query = select(User).options(selectinload(User.tracking_cryptos)).filter(User.id == user_id)
        result = await session.execute(query)
        user = result.scalars().first()

        if user:
            return user.tracking_cryptos
        else:
            return None


async def create_new_crypto(async_session: AsyncSession,
                            crypto_name: str, 
                            symbol: str,
                            current_price: float) -> Crypto:
    async with async_session() as session:
        new_crypto = Crypto(name=crypto_name,
                            symbol=symbol)
    
        session.add(new_crypto)
        await session.flush()

        new_price = Price(crypto_id=new_crypto.id, price=current_price)
        session.add(new_price)

        await session.commit()

        return new_crypto
    

async def get_all_cryptos(async_session: AsyncSession) -> List[Crypto]:
    async with async_session() as session:
        query = select(Crypto)
        result = await session.execute(query)
        cryptos = result.scalars().all()
        
        return cryptos
    

async def get_crypto_all_prices(async_session: AsyncSession,
                            crypto_id: str) -> List[Price]:
    async with async_session() as session:
        query = select(Price).filter(Price.crypto_id == crypto_id)
        result = await session.execute(query)
        prices = result.scalars().all()
        return prices


async def get_crypto_current_price(async_session: AsyncSession,
                                   crypto_id: str) -> Price:
    async with async_session() as session:
        query = select(Price).filter(Price.crypto_id == crypto_id). \
                                            order_by(Price.date.desc()).limit(1)
        result = await session.execute(query)
        current_price = result.scalars().first()

        return current_price


async def get_multiple_cryptos_current_price(async_session: AsyncSession, crypto_ids: List[str]):
    async with async_session() as session:
        # Subquery to find the latest price date for each of the specified crypto_ids
        latest_price_subquery = (
            select(
                Price.crypto_id,
                func.max(Price.date).label('max_date')
            )
            .where(Price.crypto_id.in_(crypto_ids))
            .group_by(Price.crypto_id)
            .subquery('latest_price')
        )

        # Aliasing the Price table to join with the subquery
        latest_price = aliased(Price)

        # Query to select the prices that match the latest date found for each specified crypto
        query = (
            select(Price)
            .join(
                latest_price_subquery,
                (Price.crypto_id == latest_price_subquery.c.crypto_id) &
                (Price.date == latest_price_subquery.c.max_date)
            )
        )

        result = await session.execute(query)
        current_prices = result.scalars().all()

        return current_prices


async def add_new_price(async_session: AsyncSession, 
                        crypto_id: str,
                        new_price: float) -> Price:

    async with async_session() as session:
        new_price = Price(crypto_id=crypto_id, price=new_price)
        session.add(new_price)
        await session.commit()
        return new_price

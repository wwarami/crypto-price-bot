import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker
from crypto_track.database.run import init_db

async def main():
    global async_session
    db_engine = await init_db()
    async_session = async_sessionmaker(db_engine, expire_on_commit=False)


if __name__ == "__main__":
    asyncio.run(main()) 
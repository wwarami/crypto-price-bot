import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker
from crypto_track.database.run import init_db

# Load .env variables
load_dotenv()


async def main():
    DATABASE_URL = os.getenv('DATABASE_URL')
    DB_ENGINE = await init_db(database_url=DATABASE_URL)
    async_session = async_sessionmaker(DB_ENGINE, expire_on_commit=False)


if __name__ == "__main__":
    asyncio.run(main()) 

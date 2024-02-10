from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from crypto_track.database.models import Base

DB_URL = 'sqlite+aiosqlite:///sqlalchemy_example.db'

async def init_db() -> AsyncEngine:
    engine = create_async_engine(
        DB_URL,
        echo=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return engine
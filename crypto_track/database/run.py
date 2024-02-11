from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from crypto_track.database.models import Base

async def init_db(database_url: str) -> AsyncEngine:
    engine = create_async_engine(
        database_url,
        echo=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return engine
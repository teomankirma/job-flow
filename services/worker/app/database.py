import os

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_db() -> None:
    global engine, async_session_factory
    url = os.environ["DATABASE_URL"]
    engine = create_async_engine(url, echo=False)
    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


async def close_db() -> None:
    global engine
    if engine:
        await engine.dispose()
        engine = None

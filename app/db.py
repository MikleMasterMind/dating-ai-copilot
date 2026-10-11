from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings
from app.models import Base

engine: AsyncEngine = create_async_engine(get_settings().database_url)
session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    """Create all tables defined by the ORM models."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

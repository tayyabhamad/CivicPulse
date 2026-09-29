from collections.abc import AsyncIterator
from functools import lru_cache
from typing import cast

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    return create_async_engine(get_settings().database_url, pool_pre_ping=True)


@lru_cache
def create_session_factory() -> async_sessionmaker[AsyncSession]:
    engine = get_engine()
    return async_sessionmaker(engine, expire_on_commit=False)


@lru_cache
def get_redis() -> Redis:
    return cast(
        Redis,
        Redis.from_url(get_settings().redis_url, encoding="utf-8", decode_responses=True),
    )


async def get_session() -> AsyncIterator[AsyncSession]:
    session_factory = create_session_factory()
    async with session_factory() as session:
        yield session


async def close_connections() -> None:
    """Dispose resources at application shutdown (also useful in tests)."""
    if get_redis.cache_info().currsize:
        await get_redis().aclose()
        get_redis.cache_clear()
    if get_engine.cache_info().currsize:
        await get_engine().dispose()
        get_engine.cache_clear()
        create_session_factory.cache_clear()


async def dependencies_are_ready() -> bool:
    """Check infrastructure dependencies without coupling HTTP routes to drivers."""
    try:
        async with get_engine().connect() as connection:
            await connection.execute(text("SELECT 1"))
        await get_redis().ping()
    except Exception:  # noqa: BLE001
        return False
    return True

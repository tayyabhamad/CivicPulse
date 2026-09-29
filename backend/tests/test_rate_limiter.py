"""
Tests for the Redis-backed rate limiter.
Uses eval-based Lua script via redis mock.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.services.rate_limit import RateLimiter


def make_redis(count: int) -> MagicMock:
    redis = MagicMock()
    redis.eval = AsyncMock(return_value=count)
    return redis


def make_request(host: str = "127.0.0.1") -> MagicMock:
    req = MagicMock()
    req.client.host = host
    return req


@pytest.mark.asyncio
async def test_request_within_limit_passes():
    """A count below the limit must not raise."""
    limiter = RateLimiter(redis=make_redis(5), limit=10)
    await limiter.enforce(make_request())  # should not raise


@pytest.mark.asyncio
async def test_request_at_limit_passes():
    """A count exactly at the limit must not raise."""
    limiter = RateLimiter(redis=make_redis(10), limit=10)
    await limiter.enforce(make_request())  # should not raise


@pytest.mark.asyncio
async def test_request_over_limit_raises_429():
    """A count exceeding the limit must raise HTTP 429."""
    limiter = RateLimiter(redis=make_redis(11), limit=10)
    with pytest.raises(HTTPException) as exc_info:
        await limiter.enforce(make_request())
    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_redis_error_fails_open():
    """If Redis raises, the limiter must fail open (not block the request)."""
    redis = MagicMock()
    redis.eval = AsyncMock(side_effect=ConnectionError("redis down"))
    limiter = RateLimiter(redis=redis, limit=10)
    await limiter.enforce(make_request())  # must NOT raise

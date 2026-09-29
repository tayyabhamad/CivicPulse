"""Tests for the Redis-backed fixed-window rate limiter."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.services.rate_limit import RateLimiter


def _redis(count: int = 1) -> MagicMock:
    r = MagicMock()
    r.eval = AsyncMock(return_value=count)
    return r


def _request(host: str = "127.0.0.1") -> MagicMock:
    req = MagicMock()
    req.client.host = host
    return req


@pytest.mark.asyncio
async def test_within_limit_passes() -> None:
    """Requests below the limit must not raise."""
    await RateLimiter(redis=_redis(5), limit=10).enforce(_request())


@pytest.mark.asyncio
async def test_at_limit_passes() -> None:
    """A count exactly at the limit is still allowed."""
    await RateLimiter(redis=_redis(10), limit=10).enforce(_request())


@pytest.mark.asyncio
async def test_over_limit_raises_429() -> None:
    """A count above the limit must raise HTTP 429."""
    with pytest.raises(HTTPException) as exc:
        await RateLimiter(redis=_redis(11), limit=10).enforce(_request())
    assert exc.value.status_code == 429


@pytest.mark.asyncio
async def test_redis_failure_fails_open() -> None:
    """Redis errors must not block the citizen — limiter fails open."""
    r = MagicMock()
    r.eval = AsyncMock(side_effect=ConnectionError("redis down"))
    await RateLimiter(redis=r, limit=10).enforce(_request())

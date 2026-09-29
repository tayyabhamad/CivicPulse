import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.rate_limit import RateLimiter

@pytest.fixture
def mock_redis():
    redis = MagicMock()
    redis.incr = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=True)
    return redis

@pytest.mark.asyncio
async def test_first_request_is_allowed(mock_redis):
    limiter = RateLimiter(redis=mock_redis, limit=10, window_seconds=60)
    assert await limiter.is_allowed("client-1") is True

@pytest.mark.asyncio
async def test_request_over_limit_is_rejected(mock_redis):
    mock_redis.incr = AsyncMock(return_value=11)
    limiter = RateLimiter(redis=mock_redis, limit=10, window_seconds=60)
    assert await limiter.is_allowed("client-1") is False

@pytest.mark.asyncio
async def test_expire_called_on_first_request(mock_redis):
    limiter = RateLimiter(redis=mock_redis, limit=10, window_seconds=60)
    await limiter.is_allowed("new-client")
    mock_redis.expire.assert_called_once()

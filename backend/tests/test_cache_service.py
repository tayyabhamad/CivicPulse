import pytest, json
from unittest.mock import AsyncMock, MagicMock
from app.services.cache import TriageCache

@pytest.fixture
def mock_redis():
    redis = MagicMock()
    redis.get = AsyncMock(return_value=None)
    redis.setex = AsyncMock(return_value=True)
    return redis

@pytest.mark.asyncio
async def test_cache_miss_returns_none(mock_redis):
    cache = TriageCache(redis=mock_redis, ttl=300)
    assert await cache.get("burst water main") is None

@pytest.mark.asyncio
async def test_cache_hit_returns_value(mock_redis):
    data = {"category": "water", "priority": "critical", "summary": "Burst main"}
    mock_redis.get = AsyncMock(return_value=json.dumps(data).encode())
    cache = TriageCache(redis=mock_redis, ttl=300)
    assert await cache.get("burst water main") == data

@pytest.mark.asyncio
async def test_set_uses_configured_ttl(mock_redis):
    cache = TriageCache(redis=mock_redis, ttl=300)
    await cache.set("text", {"category": "road", "priority": "low", "summary": "Pothole"})
    assert mock_redis.setex.call_args[0][1] == 300

@pytest.mark.asyncio
async def test_different_texts_have_different_keys(mock_redis):
    cache = TriageCache(redis=mock_redis, ttl=300)
    assert cache._make_key("water burst") != cache._make_key("broken light")

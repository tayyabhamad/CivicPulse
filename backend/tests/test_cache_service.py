"""Tests for the TriageCache service."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.cache import TriageCache


def make_redis(value=None):
    redis = MagicMock()
    redis.get = AsyncMock(return_value=value)
    redis.set = AsyncMock(return_value=True)
    return redis


@pytest.mark.asyncio
async def test_cache_miss_returns_none():
    cache = TriageCache(redis=make_redis(None), ttl_seconds=300)
    result = await cache.get("burst water main", "Street 12", "rules:v1")
    assert result is None


@pytest.mark.asyncio
async def test_different_texts_produce_different_keys():
    key1 = TriageCache.key_for("burst water pipe", "Street 1", "rules:v1")
    key2 = TriageCache.key_for("broken street light", "Street 2", "rules:v1")
    assert key1 != key2


@pytest.mark.asyncio
async def test_same_text_produces_same_key():
    key1 = TriageCache.key_for("burst water pipe", "Street 1", "rules:v1")
    key2 = TriageCache.key_for("burst water pipe", "Street 1", "rules:v1")
    assert key1 == key2


@pytest.mark.asyncio
async def test_key_is_case_insensitive():
    key1 = TriageCache.key_for("Burst Water Pipe", "Street 1", "rules:v1")
    key2 = TriageCache.key_for("burst water pipe", "street 1", "rules:v1")
    assert key1 == key2

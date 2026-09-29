import pytest
from fastapi import HTTPException

from app.routes.operations import readiness
from app.services.cache import STATS_CACHE_KEY, CachedTriageResult, StatsCache, TriageCache
from app.services.rate_limit import RateLimiter


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    async def get(self, key: str) -> object | None:
        return self.values.get(key)

    async def set(self, key: str, value: object, ex: int) -> None:
        self.values[key] = value

    async def delete(self, key: str) -> None:
        self.values.pop(key, None)

    async def incr(self, key: str) -> int:
        value = int(self.values.get(key, 0)) + 1
        self.values[key] = value
        return value

    async def expire(self, key: str, seconds: int) -> None:
        return None

    async def eval(self, script: str, numkeys: int, key: str, seconds: str) -> int:
        assert numkeys == 1
        assert seconds == "60"
        return await self.incr(key)


class FakeClient:
    host = "127.0.0.1"


class FakeRequest:
    client = FakeClient()


@pytest.mark.asyncio
async def test_stats_cache_round_trip_and_invalidation() -> None:
    redis = FakeRedis()
    cache = StatsCache(redis, ttl_seconds=30)  # type: ignore[arg-type]
    assert await cache.get() is None
    await cache.set({"total": 3, "by_status": {}, "by_category": {}})
    assert await cache.get() == {"total": 3, "by_status": {}, "by_category": {}}
    await cache.invalidate()
    assert STATS_CACHE_KEY not in redis.values


@pytest.mark.asyncio
async def test_rate_limiter_returns_retry_after_on_limit() -> None:
    limiter = RateLimiter(FakeRedis(), limit=1)  # type: ignore[arg-type]
    request = FakeRequest()
    await limiter.enforce(request)  # type: ignore[arg-type]
    with pytest.raises(HTTPException) as error:
        await limiter.enforce(request)  # type: ignore[arg-type]
    assert error.value.status_code == 429
    assert error.value.headers and "Retry-After" in error.value.headers


@pytest.mark.asyncio
async def test_triage_cache_normalizes_key_validates_value_and_sets_day_ttl() -> None:
    redis = FakeRedis()
    cache = TriageCache(redis)  # type: ignore[arg-type]
    entry = CachedTriageResult.model_validate(
        {
            "result": {
                "category": "water",
                "priority": "high",
                "summary": "Burst pipe flooding street",
                "confidence": 0.9,
            },
            "triaged_by": "simulated",
        }
    )

    await cache.set("  Burst PIPE  ", " Main Street ", "simulated:v1", entry)
    assert await cache.get("burst pipe", "main street", "simulated:v1") == entry
    assert len(redis.values) == 1

    key = cache.key_for("burst pipe", "main street", "simulated:v1")
    redis.values[key] = "{not-json"
    with pytest.raises(ValueError):
        await cache.get("burst pipe", "main street", "simulated:v1")


def test_triage_cache_key_uses_separate_fields_and_provider_namespace() -> None:
    cache = TriageCache(FakeRedis())  # type: ignore[arg-type]

    assert cache.key_for("a b", "c", "simulated:v1") != cache.key_for("a", "b c", "simulated:v1")
    assert cache.key_for("Burst pipe", "Main Street", "simulated:v1") != cache.key_for(
        "Burst pipe", "Main Street", "openrouter:google/gemini-2.0-flash-001"
    )
    assert cache.key_for(
        "Burst pipe", "Main Street", "openrouter:google/gemini-2.0-flash-001"
    ) != cache.key_for("Burst pipe", "Main Street", "openrouter:google/gemini-2.5-flash")


@pytest.mark.asyncio
async def test_readiness_uses_infrastructure_check(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.routes import operations

    async def ready() -> bool:
        return True

    monkeypatch.setattr(operations, "dependencies_are_ready", ready)
    assert await readiness() == {"status": "ready"}

    async def unavailable() -> bool:
        return False

    monkeypatch.setattr(operations, "dependencies_are_ready", unavailable)
    with pytest.raises(HTTPException) as error:
        await readiness()
    assert error.value.status_code == 503

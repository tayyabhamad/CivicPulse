import json
from hashlib import sha256
from typing import Any

from pydantic import BaseModel
from redis.asyncio import Redis

from app.schemas import TriageResult

STATS_CACHE_KEY = "civicpulse:stats:v1"
TRIAGE_CACHE_PREFIX = "civicpulse:triage:v2:"


class StatsCache:
    def __init__(self, redis: Redis, ttl_seconds: int) -> None:
        self._redis = redis
        self._ttl_seconds = ttl_seconds

    async def get(self) -> dict[str, object] | None:
        value = await self._redis.get(STATS_CACHE_KEY)
        return json.loads(value) if value else None

    async def set(self, value: dict[str, object]) -> None:
        await self._redis.set(STATS_CACHE_KEY, json.dumps(value), ex=self._ttl_seconds)

    async def invalidate(self) -> None:
        await self._redis.delete(STATS_CACHE_KEY)


class CachedTriageResult(BaseModel):
    result: TriageResult
    triaged_by: str


class TriageCache:
    """Caches validated AI/rules output for equivalent normalized reports."""

    def __init__(self, redis: Redis, ttl_seconds: int = 86400) -> None:
        self._redis = redis
        self._ttl_seconds = ttl_seconds

    @staticmethod
    def key_for(text: str, location: str, provider_identity: str) -> str:
        """Return a collision-resistant key for a provider's normalized report.

        Each input is normalized separately, then serialized as canonical JSON.
        This prevents ambiguous joins such as ``("a b", "c")`` and
        ``("a", "b c")`` sharing a cache entry.  The provider/model identity
        ensures a changed configuration does not reuse another model's output.
        """
        canonical = json.dumps(
            {
                "location": " ".join(location.casefold().split()),
                "provider": provider_identity,
                "text": " ".join(text.casefold().split()),
            },
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        digest = sha256(canonical.encode("utf-8")).hexdigest()
        return f"{TRIAGE_CACHE_PREFIX}{digest}"

    async def get(
        self, text: str, location: str, provider_identity: str
    ) -> CachedTriageResult | None:
        value = await self._redis.get(self.key_for(text, location, provider_identity))
        if not value:
            return None
        return CachedTriageResult.model_validate_json(value)

    async def set(
        self,
        text: str,
        location: str,
        provider_identity: str,
        value: CachedTriageResult,
    ) -> None:
        await self._redis.set(
            self.key_for(text, location, provider_identity),
            value.model_dump_json(),
            ex=self._ttl_seconds,
        )


def serializable_stats(value: dict[str, object]) -> dict[str, Any]:
    """Narrow helper retained to make the cache boundary JSON-only."""
    return value

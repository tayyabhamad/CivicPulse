import time
from collections.abc import Awaitable
from typing import cast

from fastapi import HTTPException, Request, status
from redis.asyncio import Redis

_INCREMENT_WITH_EXPIRY = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
"""


class RateLimiter:
    """Redis fixed-window limiter for write endpoints.

    The limiter fails open when Redis is unavailable so a cache outage does not
    prevent residents reporting a potentially urgent safety issue.
    """

    def __init__(self, redis: Redis, limit: int) -> None:
        self._redis = redis
        self._limit = limit

    async def enforce(self, request: Request) -> None:
        client = request.client.host if request.client else "unknown"
        window = int(time.time() // 60)
        key = f"civicpulse:rate:{client}:{window}"
        try:
            raw_count = await cast(
                Awaitable[str], self._redis.eval(_INCREMENT_WITH_EXPIRY, 1, key, "60")
            )
            count = int(raw_count)
            if count > self._limit:
                remaining = max(1, 60 - int(time.time() % 60))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many complaint submissions. Please try again shortly.",
                    headers={"Retry-After": str(remaining)},
                )
        except HTTPException:
            raise
        except Exception:  # noqa: BLE001
            return

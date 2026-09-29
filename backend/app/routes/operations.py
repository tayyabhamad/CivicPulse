import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import close_connections, dependencies_are_ready, get_redis, get_session
from app.providers.triage.factory import make_triage_provider
from app.repositories.complaints import ComplaintRepository
from app.schemas import ComplaintStatsRead
from app.services.cache import StatsCache

router = APIRouter(tags=["operations"])


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await close_connections()


@router.get("/ready")
async def readiness() -> dict[str, str]:
    if not await dependencies_are_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Dependency unavailable"
        )
    return {"status": "ready"}


@router.get("/metrics")
async def metrics(session: AsyncSession = Depends(get_session)) -> Response:
    stats = await ComplaintRepository(session).statistics()
    by_status = cast(dict[str, int], stats["by_status"])
    body = "\n".join(
        [
            "# HELP civicpulse_complaints_total Number of submitted complaints",
            "# TYPE civicpulse_complaints_total gauge",
            f"civicpulse_complaints_total {stats['total']}",
        ]
        + [
            f'civicpulse_complaints_by_status{{status="{key}"}} {value}'
            for key, value in by_status.items()
        ]
    )
    return Response(content=f"{body}\n", media_type="text/plain; version=0.0.4")


@router.get("/api/stats", response_model=ComplaintStatsRead)
async def statistics(
    response: Response, session: AsyncSession = Depends(get_session)
) -> ComplaintStatsRead:
    cache = StatsCache(get_redis(), get_settings().stats_cache_ttl_seconds)
    try:
        cached = await cache.get()
    except Exception:  # noqa: BLE001
        cached = None
    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        return ComplaintStatsRead.model_validate(cached)
    value = await ComplaintRepository(session).statistics()
    result = ComplaintStatsRead.model_validate(value)
    response.headers["X-Cache"] = "MISS"
    try:
        await cache.set(result.model_dump(mode="json"))
    except Exception:  # noqa: BLE001, S110
        pass
    return result


@router.get("/api/meta/providers")
async def provider_metadata() -> dict[str, Any]:
    settings = get_settings()
    configured = settings.triage_provider
    available = ["simulated", "rules", "openrouter"]
    try:
        make_triage_provider(configured, settings.openrouter_api_key, settings.openrouter_model)
        outcome = "configured"
    except ValueError:
        outcome = "misconfigured"
    return {
        "configured_provider": configured,
        "configured_outcome": outcome,
        "fallback_provider": "rules",
        "available_providers": available,
        "timestamp_unix": int(time.time()),
    }

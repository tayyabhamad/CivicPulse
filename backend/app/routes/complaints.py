from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_redis, get_session
from app.domain import Category, ComplaintStatus, Priority
from app.providers.triage.factory import make_triage_provider
from app.providers.triage.rules import RuleBasedTriage
from app.repositories.complaints import ComplaintRepository
from app.schemas import ComplaintCreate, ComplaintListRead, ComplaintRead, ComplaintStatusUpdate
from app.services.cache import StatsCache, TriageCache
from app.services.complaints import ComplaintNotFoundError, ComplaintService
from app.services.rate_limit import RateLimiter
from app.services.status import InvalidStatusTransition
from app.services.triage import TriageService

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


def get_service(session: AsyncSession = Depends(get_session)) -> ComplaintService:
    settings = get_settings()
    try:
        provider = make_triage_provider(
            settings.triage_provider, settings.openrouter_api_key, settings.openrouter_model
        )
    except ValueError:
        provider = RuleBasedTriage()
    triage_cache = TriageCache(get_redis(), settings.triage_cache_ttl_seconds)
    return ComplaintService(
        ComplaintRepository(session), TriageService(provider, cache=triage_cache)
    )


def get_rate_limiter() -> RateLimiter:
    return RateLimiter(get_redis(), get_settings().rate_limit_per_minute)


def get_stats_cache() -> StatsCache:
    return StatsCache(get_redis(), get_settings().stats_cache_ttl_seconds)


@router.post("", response_model=ComplaintRead, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    payload: ComplaintCreate,
    request: Request,
    service: ComplaintService = Depends(get_service),
    limiter: RateLimiter = Depends(get_rate_limiter),
    cache: StatsCache = Depends(get_stats_cache),
) -> ComplaintRead:
    await limiter.enforce(request)
    complaint = await service.create(payload)
    try:
        await cache.invalidate()
    except Exception:  # noqa: BLE001, S110
        pass
    return ComplaintRead.model_validate(complaint)


@router.get("/{complaint_id}", response_model=ComplaintRead)
async def get_complaint(
    complaint_id: UUID, service: ComplaintService = Depends(get_service)
) -> ComplaintRead:
    try:
        return ComplaintRead.model_validate(await service.get(complaint_id))
    except ComplaintNotFoundError as error:
        raise HTTPException(status_code=404, detail="Complaint not found") from error


@router.get("", response_model=ComplaintListRead)
async def list_complaints(
    category: Category | None = None,
    priority: Priority | None = None,
    complaint_status: ComplaintStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: ComplaintService = Depends(get_service),
) -> ComplaintListRead:
    items, total = await service.list(category, priority, complaint_status, page, page_size)
    return ComplaintListRead(
        items=[ComplaintRead.model_validate(item) for item in items],
        total=total,
    )


@router.patch("/{complaint_id}/status", response_model=ComplaintRead)
async def update_complaint_status(
    complaint_id: UUID,
    payload: ComplaintStatusUpdate,
    service: ComplaintService = Depends(get_service),
    cache: StatsCache = Depends(get_stats_cache),
) -> ComplaintRead:
    try:
        complaint = await service.update_status(complaint_id, payload.status)
        try:
            await cache.invalidate()
        except Exception:  # noqa: BLE001, S110
            pass
        return ComplaintRead.model_validate(complaint)
    except ComplaintNotFoundError as error:
        raise HTTPException(status_code=404, detail="Complaint not found") from error
    except InvalidStatusTransition as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain import Category, ComplaintStatus, Priority


class ComplaintCreate(BaseModel):
    text: str = Field(min_length=10, max_length=2000)
    location: str = Field(min_length=3, max_length=200)
    reporter_contact: str | None = Field(default=None, max_length=200)


class TriageResult(BaseModel):
    category: Category
    priority: Priority
    summary: str = Field(max_length=140)
    confidence: float = Field(ge=0.0, le=1.0)


class ComplaintStatusUpdate(BaseModel):
    status: ComplaintStatus


class ComplaintRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    location: str
    reporter_contact: str | None
    category: Category
    priority: Priority
    status: ComplaintStatus
    ai_summary: str | None
    triaged_by: str
    triage_latency_ms: int


class ComplaintListRead(BaseModel):
    """The paginated complaint collection returned by ``GET /api/complaints``."""

    items: list[ComplaintRead]
    total: int = Field(ge=0)


class ComplaintStatsRead(BaseModel):
    """Aggregate counts used by the operations dashboard."""

    total: int = Field(ge=0)
    by_status: dict[ComplaintStatus, int]
    by_category: dict[Category, int]


class ProviderOutcome(BaseModel):
    provider: str
    latency_ms: int
    fallback: bool

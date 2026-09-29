from uuid import UUID

from app.domain import Category, ComplaintStatus, Priority
from app.models import Complaint
from app.repositories.complaints import ComplaintRepository
from app.schemas import ComplaintCreate
from app.services.status import InvalidStatusTransition, require_valid_transition
from app.services.triage import TriageService


class ComplaintNotFoundError(LookupError):
    pass


class ConcurrentStatusTransitionError(InvalidStatusTransition):
    """Raised when another request changed a complaint after it was read."""


class ComplaintService:
    def __init__(self, repository: ComplaintRepository, triage: TriageService) -> None:
        self._repository = repository
        self._triage = triage

    async def create(self, payload: ComplaintCreate) -> Complaint:
        execution = await self._triage.triage(payload.text, payload.location)
        return await self._repository.create(
            Complaint(
                text=payload.text,
                location=payload.location,
                reporter_contact=payload.reporter_contact,
                category=execution.result.category,
                priority=execution.result.priority,
                status=ComplaintStatus.OPEN,
                ai_summary=execution.result.summary,
                triaged_by=execution.triaged_by,
                triage_latency_ms=execution.latency_ms,
            )
        )

    async def get(self, complaint_id: UUID) -> Complaint:
        complaint = await self._repository.get(complaint_id)
        if complaint is None:
            raise ComplaintNotFoundError(str(complaint_id))
        return complaint

    async def list(
        self,
        category: Category | None,
        priority: Priority | None,
        status: ComplaintStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Complaint], int]:
        return await self._repository.list(
            category=category, priority=priority, status=status, page=page, page_size=page_size
        )

    async def update_status(self, complaint_id: UUID, status: ComplaintStatus) -> Complaint:
        complaint = await self.get(complaint_id)
        require_valid_transition(complaint.status, status)
        updated = await self._repository.transition_status(
            complaint_id, current=complaint.status, target=status
        )
        if updated is None:
            raise ConcurrentStatusTransitionError(
                "Complaint status changed concurrently; refresh and try again"
            )
        return updated

    async def statistics(self) -> dict[str, object]:
        return await self._repository.statistics()

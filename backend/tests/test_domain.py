import pytest

from app.domain import Category, ComplaintStatus, Priority, can_transition
from app.models import Complaint
from app.services.complaints import ComplaintService, ConcurrentStatusTransitionError
from app.services.status import InvalidStatusTransition, require_valid_transition


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (ComplaintStatus.OPEN, ComplaintStatus.IN_PROGRESS),
        (ComplaintStatus.OPEN, ComplaintStatus.REJECTED),
        (ComplaintStatus.IN_PROGRESS, ComplaintStatus.RESOLVED),
        (ComplaintStatus.IN_PROGRESS, ComplaintStatus.REJECTED),
    ],
)
def test_transition_table_allows_defined_transitions(
    current: ComplaintStatus, target: ComplaintStatus
) -> None:
    assert can_transition(current, target)


def test_transition_table_rejects_terminal_transition() -> None:
    with pytest.raises(InvalidStatusTransition, match="resolved to open"):
        require_valid_transition(ComplaintStatus.RESOLVED, ComplaintStatus.OPEN)


class ConcurrentRepository:
    def __init__(self, complaint: Complaint) -> None:
        self.complaint = complaint
        self.observed: tuple[ComplaintStatus, ComplaintStatus] | None = None

    async def get(self, complaint_id: object) -> Complaint:
        return self.complaint

    async def transition_status(
        self,
        complaint_id: object,
        *,
        current: ComplaintStatus,
        target: ComplaintStatus,
    ) -> None:
        self.observed = (current, target)
        # This emulates another request committing its change between read and update.


@pytest.mark.asyncio
async def test_status_update_rejects_a_stale_conditional_write() -> None:
    repository = ConcurrentRepository(
        Complaint(
            text="A burst pipe is flooding homes",
            location="Street 12",
            category=Category.WATER,
            priority=Priority.HIGH,
            status=ComplaintStatus.OPEN,
            triaged_by="rules",
            triage_latency_ms=0,
        )
    )
    service = ComplaintService(repository, object())  # type: ignore[arg-type]

    with pytest.raises(ConcurrentStatusTransitionError, match="changed concurrently"):
        await service.update_status(repository.complaint.id, ComplaintStatus.IN_PROGRESS)

    assert repository.observed == (ComplaintStatus.OPEN, ComplaintStatus.IN_PROGRESS)

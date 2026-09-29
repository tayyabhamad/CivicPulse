from enum import StrEnum


class Category(StrEnum):
    WATER = "water"
    ELECTRICITY = "electricity"
    SANITATION = "sanitation"
    ROADS = "roads"
    STREETLIGHTS = "streetlights"
    OTHER = "other"


class Priority(StrEnum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class ComplaintStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


ALLOWED_STATUS_TRANSITIONS: dict[ComplaintStatus, frozenset[ComplaintStatus]] = {
    ComplaintStatus.OPEN: frozenset({ComplaintStatus.IN_PROGRESS, ComplaintStatus.REJECTED}),
    ComplaintStatus.IN_PROGRESS: frozenset({ComplaintStatus.RESOLVED, ComplaintStatus.REJECTED}),
    ComplaintStatus.RESOLVED: frozenset(),
    ComplaintStatus.REJECTED: frozenset(),
}


def can_transition(current: ComplaintStatus, target: ComplaintStatus) -> bool:
    """Return whether the explicit domain transition table permits this move."""
    return target in ALLOWED_STATUS_TRANSITIONS[current]

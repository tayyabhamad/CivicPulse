from app.domain import ComplaintStatus, can_transition


class InvalidStatusTransition(ValueError):
    """Raised when an operator asks for a transition not in the domain table."""


def require_valid_transition(current: ComplaintStatus, target: ComplaintStatus) -> None:
    if not can_transition(current, target):
        raise InvalidStatusTransition(f"Cannot transition complaint from {current} to {target}")

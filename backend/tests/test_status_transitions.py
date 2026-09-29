"""Tests for complaint status transition validation."""

from __future__ import annotations

import pytest

from app.domain import ComplaintStatus, can_transition
from app.services.status import InvalidStatusTransition, require_valid_transition


def test_open_to_in_progress_allowed() -> None:
    assert can_transition(ComplaintStatus.OPEN, ComplaintStatus.IN_PROGRESS) is True


def test_open_to_rejected_allowed() -> None:
    assert can_transition(ComplaintStatus.OPEN, ComplaintStatus.REJECTED) is True


def test_open_to_resolved_not_allowed() -> None:
    assert can_transition(ComplaintStatus.OPEN, ComplaintStatus.RESOLVED) is False


def test_in_progress_to_resolved_allowed() -> None:
    assert can_transition(ComplaintStatus.IN_PROGRESS, ComplaintStatus.RESOLVED) is True


def test_in_progress_to_rejected_allowed() -> None:
    assert can_transition(ComplaintStatus.IN_PROGRESS, ComplaintStatus.REJECTED) is True


def test_resolved_is_terminal() -> None:
    assert can_transition(ComplaintStatus.RESOLVED, ComplaintStatus.OPEN) is False
    assert can_transition(ComplaintStatus.RESOLVED, ComplaintStatus.IN_PROGRESS) is False


def test_require_valid_transition_does_not_raise() -> None:
    require_valid_transition(ComplaintStatus.OPEN, ComplaintStatus.IN_PROGRESS)


def test_require_invalid_transition_raises() -> None:
    with pytest.raises(InvalidStatusTransition):
        require_valid_transition(ComplaintStatus.OPEN, ComplaintStatus.RESOLVED)

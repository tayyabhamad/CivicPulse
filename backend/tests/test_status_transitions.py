"""Tests for complaint status transition validation."""
import pytest
from app.domain import ComplaintStatus, can_transition
from app.services.status import require_valid_transition, InvalidStatusTransition


def test_open_to_in_progress_is_valid():
    assert can_transition(ComplaintStatus.OPEN, ComplaintStatus.IN_PROGRESS) is True


def test_open_to_resolved_is_invalid():
    assert can_transition(ComplaintStatus.OPEN, ComplaintStatus.RESOLVED) is False


def test_in_progress_to_resolved_is_valid():
    assert can_transition(ComplaintStatus.IN_PROGRESS, ComplaintStatus.RESOLVED) is True


def test_resolved_to_closed_is_valid():
    assert can_transition(ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED) is True


def test_invalid_transition_raises():
    with pytest.raises(InvalidStatusTransition):
        require_valid_transition(ComplaintStatus.OPEN, ComplaintStatus.CLOSED)


def test_valid_transition_does_not_raise():
    require_valid_transition(ComplaintStatus.OPEN, ComplaintStatus.IN_PROGRESS)

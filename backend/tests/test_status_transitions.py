import pytest
from app.services.status import is_valid_transition

def test_open_to_in_progress_is_valid():
    assert is_valid_transition("open", "in_progress") is True

def test_open_to_resolved_is_invalid():
    assert is_valid_transition("open", "resolved") is False

def test_in_progress_to_resolved_is_valid():
    assert is_valid_transition("in_progress", "resolved") is True

def test_resolved_to_closed_is_valid():
    assert is_valid_transition("resolved", "closed") is True

def test_closed_has_no_valid_transitions():
    assert is_valid_transition("closed", "open") is False
    assert is_valid_transition("closed", "in_progress") is False

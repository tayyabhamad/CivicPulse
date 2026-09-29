"""Tests for the rules-based and simulated triage providers."""

from __future__ import annotations

import pytest

from app.domain import Category
from app.providers.triage.rules import RuleBasedTriage
from app.providers.triage.simulated import SimulatedTriage


@pytest.mark.asyncio
async def test_rules_detects_water_keyword() -> None:
    result = await RuleBasedTriage().triage("burst water pipe flooding street", "Street 12")
    assert result.category == Category.WATER


@pytest.mark.asyncio
async def test_rules_result_has_required_fields() -> None:
    result = await RuleBasedTriage().triage("broken street light near park", "Main Road")
    assert result.category is not None
    assert result.priority is not None
    assert result.summary != ""


@pytest.mark.asyncio
async def test_rules_unknown_text_returns_other() -> None:
    result = await RuleBasedTriage().triage("xyzzyx unknown abcdef", "Somewhere")
    assert result.category == Category.OTHER


@pytest.mark.asyncio
async def test_simulated_is_deterministic() -> None:
    provider = SimulatedTriage()
    r1 = await provider.triage("test complaint", "Street 1")
    r2 = await provider.triage("test complaint", "Street 1")
    assert r1.category == r2.category
    assert r1.priority == r2.priority


@pytest.mark.asyncio
async def test_simulated_fail_mode_raises() -> None:
    with pytest.raises(RuntimeError, match="simulated triage failure"):
        await SimulatedTriage(should_fail=True).triage("test", "loc")

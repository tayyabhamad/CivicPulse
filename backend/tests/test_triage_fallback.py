"""Tests for triage provider fallback behaviour."""
import pytest
from app.providers.triage.rules import RuleBasedTriage
from app.providers.triage.simulated import SimulatedTriage
from app.domain import Category


@pytest.mark.asyncio
async def test_rules_detects_water_keyword():
    provider = RuleBasedTriage()
    result = await provider.triage("burst water pipe flooding street", "Street 12")
    assert result.category == Category.WATER


@pytest.mark.asyncio
async def test_rules_returns_required_fields():
    provider = RuleBasedTriage()
    result = await provider.triage("broken street light near park", "Main Road")
    assert result.category is not None
    assert result.priority is not None
    assert result.summary != ""


@pytest.mark.asyncio
async def test_simulated_is_deterministic():
    provider = SimulatedTriage()
    r1 = await provider.triage("test complaint", "Street 1")
    r2 = await provider.triage("test complaint", "Street 1")
    assert r1.category == r2.category
    assert r1.priority == r2.priority


@pytest.mark.asyncio
async def test_simulated_fail_mode_raises():
    provider = SimulatedTriage(should_fail=True)
    with pytest.raises(RuntimeError, match="simulated triage failure"):
        await provider.triage("test complaint", "Street 1")


@pytest.mark.asyncio
async def test_rules_unknown_text_returns_other():
    provider = RuleBasedTriage()
    result = await provider.triage("xyzzyx unknown abcdef", "Somewhere")
    assert result.category == Category.OTHER

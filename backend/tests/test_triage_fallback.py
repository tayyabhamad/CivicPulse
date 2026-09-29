import pytest
from app.providers.triage.rules import RulesTriageProvider
from app.providers.triage.simulated import SimulatedTriageProvider

@pytest.mark.asyncio
async def test_rules_detects_water_keyword():
    provider = RulesTriageProvider()
    result = await provider.triage("burst water pipe flooding street")
    assert result["category"] == "water"

@pytest.mark.asyncio
async def test_rules_returns_required_fields():
    provider = RulesTriageProvider()
    result = await provider.triage("broken street light near park")
    assert all(k in result for k in ("category", "priority", "summary"))

@pytest.mark.asyncio
async def test_simulated_is_deterministic():
    provider = SimulatedTriageProvider()
    r1 = await provider.triage("test complaint")
    r2 = await provider.triage("test complaint")
    assert r1["category"] == r2["category"]

@pytest.mark.asyncio
async def test_rules_handles_unknown_text():
    provider = RulesTriageProvider()
    result = await provider.triage("xyzzyx unknown abcdef")
    assert result["category"] is not None

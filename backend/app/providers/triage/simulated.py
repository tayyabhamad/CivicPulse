import hashlib

from app.domain import Category, Priority
from app.schemas import TriageResult


class SimulatedTriage:
    """Seeded network-free provider: the only provider permitted in CI."""

    name = "simulated"
    cache_identity = "simulated:v1"

    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    async def triage(self, text: str, location: str) -> TriageResult:
        if self.should_fail:
            raise RuntimeError("simulated triage failure")
        digest = hashlib.sha256(f"{text}|{location}".encode()).digest()
        categories = list(Category)
        priorities = list(Priority)
        return TriageResult(
            category=categories[digest[0] % len(categories)],
            priority=priorities[digest[1] % len(priorities)],
            summary=" ".join(text.strip().split())[:140],
            confidence=round(0.5 + (digest[2] / 510), 2),
        )

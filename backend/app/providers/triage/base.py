from typing import Protocol

from app.schemas import TriageResult


class TriageProvider(Protocol):
    """The only interface the application needs from a triage implementation."""

    name: str

    async def triage(self, text: str, location: str) -> TriageResult:
        """Classify one complaint or raise a provider-specific error."""

from app.domain import Category, Priority
from app.schemas import TriageResult


class RuleBasedTriage:
    """Deterministic, dependency-free provider used as the safety net."""

    name = "rules"
    cache_identity = "rules:v1"
    _keywords: tuple[tuple[Category, tuple[str, ...]], ...] = (
        (Category.WATER, ("water", "pipe", "leak", "burst", "sewer", "naali")),
        (Category.ELECTRICITY, ("electricity", "transformer", "wire", "bijli", "shock")),
        (Category.SANITATION, ("garbage", "trash", "waste", "kooda", "smell")),
        (Category.ROADS, ("road", "pothole", "footpath", "gutter", "street")),
        (Category.STREETLIGHTS, ("streetlight", "street light", "lamp", "light pole")),
    )
    _high_words = ("flood", "fire", "shock", "danger", "urgent", "burst", "injury")
    _low_words = ("suggestion", "whenever", "minor", "cosmetic")

    async def triage(self, text: str, location: str) -> TriageResult:
        normalized = text.lower()
        category = next(
            (
                candidate
                for candidate, words in self._keywords
                if any(word in normalized for word in words)
            ),
            Category.OTHER,
        )
        priority = (
            Priority.HIGH
            if any(word in normalized for word in self._high_words)
            else Priority.LOW
            if any(word in normalized for word in self._low_words)
            else Priority.NORMAL
        )
        summary = " ".join(text.strip().split())[:140]
        return TriageResult(
            category=category,
            priority=priority,
            summary=summary,
            confidence=0.65 if category is not Category.OTHER else 0.35,
        )

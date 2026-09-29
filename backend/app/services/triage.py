import time
from dataclasses import dataclass

from app.providers.triage.base import TriageProvider
from app.providers.triage.rules import RuleBasedTriage
from app.schemas import TriageResult
from app.services.cache import CachedTriageResult, TriageCache


@dataclass(frozen=True)
class TriageExecution:
    result: TriageResult
    triaged_by: str
    latency_ms: int
    used_fallback: bool


class TriageService:
    """Safely invokes a selected provider and guarantees an available fallback."""

    def __init__(
        self,
        provider: TriageProvider,
        fallback: TriageProvider | None = None,
        cache: TriageCache | None = None,
    ) -> None:
        self._provider = provider
        self._fallback = fallback or RuleBasedTriage()
        self._cache = cache

    @property
    def _cache_identity(self) -> str:
        """Expose a stable namespace without requiring provider SDK internals."""
        return str(getattr(self._provider, "cache_identity", self._provider.name))

    async def triage(self, text: str, location: str) -> TriageExecution:
        started = time.perf_counter()
        if self._cache is not None:
            try:
                cached = await self._cache.get(text, location, self._cache_identity)
                if cached is not None:
                    return TriageExecution(
                        result=cached.result,
                        triaged_by=f"cache:{cached.triaged_by}",
                        latency_ms=int((time.perf_counter() - started) * 1000),
                        used_fallback=cached.triaged_by == "rules:fallback",
                    )
            except Exception:  # noqa: BLE001, S110
                # Redis is an optimization: a corrupt entry or outage must not reject a report.
                pass
        try:
            result = await self._provider.triage(text, location)
            execution = TriageExecution(
                result=result,
                triaged_by=self._provider.name,
                latency_ms=int((time.perf_counter() - started) * 1000),
                used_fallback=False,
            )
        # This is the provider boundary: malformed model output and unexpected SDK errors
        # must fail closed into the deterministic fallback, never escape as a 500 response.
        except Exception:  # noqa: BLE001
            result = await self._fallback.triage(text, location)
            execution = TriageExecution(
                result=result,
                triaged_by="rules:fallback",
                latency_ms=int((time.perf_counter() - started) * 1000),
                used_fallback=True,
            )
        if self._cache is not None:
            try:
                await self._cache.set(
                    text,
                    location,
                    self._cache_identity,
                    CachedTriageResult(result=execution.result, triaged_by=execution.triaged_by),
                )
            except Exception:  # noqa: BLE001, S110
                pass
        return execution

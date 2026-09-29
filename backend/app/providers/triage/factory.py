from app.providers.triage.base import TriageProvider
from app.providers.triage.openrouter import OpenRouterTriage
from app.providers.triage.rules import RuleBasedTriage
from app.providers.triage.simulated import SimulatedTriage


def make_triage_provider(provider_name: str, api_key: str = "", model: str = "") -> TriageProvider:
    """Create a provider from explicit configuration, never from frontend input."""
    match provider_name:
        case "simulated":
            return SimulatedTriage()
        case "rules":
            return RuleBasedTriage()
        case "openrouter":
            return OpenRouterTriage(api_key, model)
        case _:
            raise ValueError(f"Unsupported TRIAGE_PROVIDER: {provider_name}")

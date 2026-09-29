# ADR 001: Triage provider boundary

Use a `TriageProvider` interface with simulated, rule-based, and OpenRouter implementations. Provider output is Pydantic-validated; retryable failures fall back to deterministic rules. This makes CI reliable and protects citizens from upstream outages.

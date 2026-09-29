# CivicPulse — Project Charter

## Problem

Municipal complaints arrive as unstructured text, so urgent incidents can be delayed behind routine reports. CivicPulse classifies, prioritises, stores, and exposes these reports through an operations dashboard.

## Product promise

- Citizens submit text, location, and optional contact information.
- Operators see an AI-derived category, priority, concise summary, provider, status, and aggregate statistics.
- Triage technology is replaceable and failure of a hosted provider never becomes a user-facing server error.
- The same source runs locally with Docker Compose and in Kubernetes.

## Architectural boundaries

```text
Browser → nginx/frontend → FastAPI backend → PostgreSQL
                               └──────────→ Redis
                               └──────────→ OpenRouter hosted LLM (when configured)
```

The frontend contains presentation logic only. Business rules belong in services; SQL belongs exclusively in repositories; external integrations sit behind provider interfaces.

## Success measures

- Valid complaint submission returns HTTP 201 with a validated triage result.
- Invalid status transitions return HTTP 409 with the attempted transition explained.
- `/health` never accesses dependencies; `/ready` fails if PostgreSQL or Redis is unavailable.
- Duplicate content reuses cached triage for 24 hours; stats cache reports `X-Cache: MISS` then `HIT` with 30-second TTL and invalidation on writes.
- Provider error, malformed data, timeout, retryable upstream error, or rate limit results in safe rule-based fallback.
- CI remains deterministic because it uses simulated triage only.

## Governance rules

- No API key, `.env`, token, or password enters Git history.
- No `latest` deployment tag, unpinned base image, service-to-service `localhost`, or public database/cache port.
- GitHub history must be genuine: issues, feature branches, PRs, reviews, and merge conflict evidence reflect actual team work.
- AI assistance is disclosed precisely in `docs/AI-USAGE.md`; students must be able to explain every submitted line.

## Project constraints

- Team size: two.
- Target execution plan: three focused days.
- Assignment specifies 150 marks and an individual viva multiplier.
- Hosted LLM choice is OpenRouter with a low-budget Gemini Flash-class model, but exact availability/model ID must be confirmed in the account before it is enabled.

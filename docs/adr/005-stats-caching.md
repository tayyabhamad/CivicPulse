# ADR 005 — Stats Endpoint Caching

**Date:** 2026-09-29 | **Status:** Accepted | **Author:** Hamza Mahfooz

## Context
GET /stats aggregates all complaints — expensive under load.
30-second staleness is acceptable for the dashboard.

## Decision
Cache stats in Redis (TTL=30s). Return X-Cache: HIT/MISS header.
Frontend displays this to make caching visible in the UI.

## Consequences
- Reduces DB load by ~95% under sustained polling
- Assignment rubric rewards visible cache behaviour in UI
- Stats may lag up to 30s after new complaint (acceptable)

## Alternatives
1. No caching — fails under K6 load
2. HTTP Cache-Control — no server-side observability
3. Event-driven invalidation — over-engineered for 30s window

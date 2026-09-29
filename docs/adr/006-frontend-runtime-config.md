# ADR 006 — Frontend Runtime Configuration

**Date:** 2026-09-29 | **Status:** Accepted | **Author:** Hamza Mahfooz

## Context
Vite bakes import.meta.env values into JS at build time.
If the API URL is baked in, the image is environment-specific,
destroying build-once-deploy-many.

## Decision
Use nginx as a reverse proxy: all /api/ requests are proxied to
http://backend:8000/ at runtime via DNS resolution.
The frontend never contains an absolute backend URL.

## Consequences
- One image works in dev, staging, and production
- Backend URL resolved at runtime via Docker/Kubernetes DNS
- No /config.js endpoint needed (simpler)

## Evidence
frontend/nginx/default.conf.template line 8:
  proxy_pass http://backend:8000/;

# CivicPulse Runbook

## Local launch

1. Install and start a Docker-compatible engine (Docker Desktop or native WSL Docker Engine).
2. Copy `.env.example` to `.env`; add an OpenRouter key only if using `TRIAGE_PROVIDER=openrouter`.
3. Run `docker compose up --build` and open `http://localhost:8080`.
4. Stop with `docker compose down`; data persists in named volumes. Use `down -v` only when intentionally resetting data.

## Triage incident

Set `TRIAGE_PROVIDER=rules` for immediate deterministic operation. The application already falls back to rules when OpenRouter times out, rate-limits, returns malformed output, or is misconfigured. Inspect JSON stdout logs by request ID and `/api/meta/providers`.

## Kubernetes

Install metrics-server and an ingress controller, then apply `kubectl apply -k k8s/overlays/local`. Check `kubectl get pods,hpa -n civicpulse`. Roll back an unsafe release with `kubectl rollout undo deployment/backend -n civicpulse`; use the previous SHA overlay for the auditable declarative rollback.

The local kind verification used native WSL Docker Engine and a Metrics Server
configured for kind. The migration Job waits for PostgreSQL, applies Alembic
migrations, and then seeds 32 fixtures before the dashboard is used.

## Evidence still required

Capture real screenshots/output for branch protection, failed/green merge,
network isolation, HPA scaling, load chart, and rollback. Do not fabricate
evidence. See [EVIDENCE.md](EVIDENCE.md) for the current verified baseline and
the remaining evidence checklist.

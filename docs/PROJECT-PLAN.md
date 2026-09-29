# CivicPulse — 3-Day Delivery Plan

**Course:** CS4032 — Software Construction and Design, Assignment 1
**Team:** Two members
**Delivery mode:** Three focused build days plus genuine GitHub and demo evidence
**Project manager / technical owner:** Codex (planning, implementation sequencing, quality gates, and documentation); students retain control of credentials, GitHub access, demonstrations, attribution, and submission.

## 1. Outcome

Deliver CivicPulse: a municipal complaint intake and operations dashboard. A citizen submits a complaint; the backend validates it, asks a replaceable triage provider for category/priority/summary, safely falls back to rules when that provider fails, persists the result, and exposes it to an operator dashboard.

The submission must run locally from a clean clone with Docker Compose, test deterministically in CI, and have a Kubernetes deployment path with verifiable operational evidence.

## 2. Scope and priority

### Non-negotiable core

1. FastAPI four-layer backend: routes → services → repositories → providers.
2. PostgreSQL migrations, indexes, and an idempotent seed of at least 30 complaints.
3. Redis statistics cache and distributed submission rate limit.
4. Provider interface with simulated, rule-based, and hosted-LLM implementations.
5. Hosted provider safety: validated structured output, 10-second timeout, one retry only for retryable failures, content-hash cache, and rule fallback.
6. React dashboard and submit form, backed by the OpenAPI contract.
7. Multi-stage, non-root images; network-segmented Compose stack; persistent volumes.
8. Deterministic backend/frontend tests and CI.
9. Kubernetes manifests, probes, resources, HPA, VPA recommender configuration, and load-test evidence.
10. README, ADRs, runbook, engineering notes, AI-use disclosure, and submission evidence.

### Out of scope until the core is green

- Visual polish beyond a clear, usable interface.
- Bonus work (GitOps, Cosign, Grafana, OpenTelemetry) unless all mandatory checks and evidence are complete.
- A live hosted-model call in CI. CI always uses `SimulatedTriage`.

## 3. Technology decisions

| Concern | Decision | Reason |
| --- | --- | --- |
| Backend | FastAPI + Pydantic v2 + SQLAlchemy + Alembic | Typed OpenAPI, shared validation model, clean testability. |
| Frontend | React 18 + Vite + TypeScript | Required by the assignment. |
| Database/cache | PostgreSQL 16 + Redis 7 | Required by the assignment. |
| Hosted AI | OpenRouter, configured by environment variable | Uses the existing key; never committed or exposed to the browser. |
| Low-budget model | A Gemini Flash-class model available in the team’s OpenRouter account, selected through `OPENROUTER_MODEL` | Cheap/fast path, while retaining provider interchangeability. Confirm the exact model identifier against the OpenRouter account before enabling it. |
| Local/offline AI | RuleBasedTriage (required) and optional Ollama | Keeps demos and development functional if the hosted provider is unavailable. |
| CI provider | SimulatedTriage | No network dependency or flaky model behavior. |
| Frontend API path | nginx proxy for `/api` | No baked-in backend URL; one frontend image can run in every environment. |
| Kubernetes | kind or k3d + Kustomize | Free local cluster and assignment-aligned manifests. |

## 4. Roles and ownership

| Workstream | Codex | Student A | Student B |
| --- | --- | --- | --- |
| Architecture and backlog | Owns design, sequencing, acceptance checks | Reviews and understands | Reviews and understands |
| Backend/data/AI | Can implement and test | Owns a feature branch/PR and explains it | Reviews PR; understands implementation |
| Frontend | Can implement and test | Reviews and tests UI | Owns a feature branch/PR and explains it |
| Docker/Kubernetes/CI | Can implement and troubleshoot | Runs local commands and records evidence | Reviews and records evidence |
| GitHub configuration | Provides instructions | Enables protection/settings and opens PRs | Reviews/approves PRs |
| Credentials | Never receives secrets | Creates/adds OpenRouter/GitHub secrets | Verifies they are absent from Git history |
| Video/viva/submission | Prepares script and checklist | Speaks, demonstrates, submits | Speaks, demonstrates, submits |

Both students must read and be able to modify every major area. The individual viva multiplies the team mark.

## 5. GitHub workflow

### Before Day 1 (student-operated)

1. Create the GitHub repository and invite the teammate and instructors as required.
2. Create `main` and `dev` branches.
3. Protect `main`: PR required, CI required, one approval required, direct pushes disabled.
4. Capture the branch-protection screenshot in `docs/evidence/`.
5. Create Issues before corresponding PRs and link each PR to its Issue.
6. Add `OPENROUTER_API_KEY` only as a GitHub Secret if a hosted deployment genuinely needs it. Keep local keys only in untracked `.env`.

### Required PR plan

| PR | Branch | Issue | Main content | Reviewer |
| --- | --- | --- | --- | --- |
| 1 | `feature/backend-foundation` | Backend contract/data | FastAPI skeleton, migrations, seed, health endpoints | Other student |
| 2 | `feature/triage-and-cache` | AI resilience | Providers, fallback, Redis cache/rate limit, tests | Other student |
| 3 | `feature/frontend-dashboard` | Operator UI | Submission, dashboard, stats, component tests | Other student |
| 4 | `feature/compose-and-ci` | Reproducible delivery | Images, Compose, CI, smoke test | Other student |
| 5 | `feature/kubernetes-and-docs` | Operations/evidence | Kustomize, HPA/VPA, docs and scripts | Other student |

Each review must contain one substantive comment. Use conventional commits. Aim for 35+ meaningful commits total and keep each student at or above 35% contribution by `git shortlog -sn`.

## 6. Three-day schedule

### Day 1 — Working vertical slice and resilient backend

**Goal:** one complaint can travel from HTTP request to PostgreSQL and return a triage result even when the hosted provider fails.

| Block | Work | Exit criterion |
| --- | --- | --- |
| 1 | Initialise repository, branches, issue board, `.gitignore`, `.env.example`, Python/Node tooling, folder layout | Clean local setup; no secrets tracked. |
| 2 | Implement domain types, Pydantic schemas, Alembic migration, repository layer, indexes, and idempotent 30-record seed | Migration and seed rerun safely. |
| 3 | Implement complaint create/read/list/status routes, explicit transition table, `/health`, `/ready`, request ID logging | Correct validation, 409 transitions, and dependency-aware readiness. |
| 4 | Implement `TriageProvider`, simulated and rules providers, OpenRouter provider configuration, structured-output validation, timeout/retry/fallback | A failing provider still produces HTTP 201 with `rules:fallback`. |
| 5 | Add Redis triage hash cache, `/api/stats` cache/invalidation, Redis rate limiter, backend tests | At least 14 deterministic tests; core flows pass. |

**Day-1 proof:** `POST /api/complaints` works; provider failure test passes; data survives restart; API docs are usable.

### Day 2 — User interface, containers, and CI

**Goal:** a clean clone launches the full system via Compose and CI validates it.

| Block | Work | Exit criterion |
| --- | --- | --- |
| 1 | Build React submit view with client validation, loading state, result/provider rendering, and error boundary | Complaint submission is demonstrable. |
| 2 | Build dashboard with filters, pagination, status changes, server 409 rendering, and stats/cache state | Operator workflow is demonstrable. |
| 3 | Create typed API client checked against OpenAPI and at least five component tests | UI contract and tests are green. |
| 4 | Create multi-stage Dockerfiles, nginx `/api` proxy, Compose networks/volumes/health checks | `docker compose up --build` works; frontend cannot reach database. |
| 5 | Add CI: lint/type checks, deterministic test jobs, image builds, Trivy, kubeconform, Compose smoke test | CI runs on `dev` and pull requests. |

**Day-2 proof:** clean Compose run; seeded dashboard; X-Cache transitions from MISS to HIT; network-isolation command fails as expected; CI is green.

### Day 3 — Kubernetes, evidence, documentation, and rehearsal

**Goal:** deploy the same application locally to Kubernetes, collect real evidence, and make the handover/submission defensible.

| Block | Work | Exit criterion |
| --- | --- | --- |
| 1 | Add Kustomize base/overlays, namespace, Deployments, Postgres StatefulSet/PVC, Redis PVC, Services, Ingress, ConfigMap/placeholder Secret | `kubectl apply -k` produces healthy resources. |
| 2 | Add probes, resources, PDB, HPA behavior, VPA Off/recommender config and load script | HPA can read CPU metrics and VPA offers recommendations. |
| 3 | Configure CD workflow to test → push SHA-tagged images → ephemeral-cluster deploy/smoke test | Jobs use `needs:` gates and deploy immutable SHA tags. |
| 4 | Capture protection/PR/conflict/CI/HPA/rollback evidence and scaling chart; write docs | Every rubric claim has evidence or an honest recorded limitation. |
| 5 | Run `scripts/check_submission.py`, perform a clean-clone test, rehearse demo and viva questions | Submit only after final checklist is complete. |

**Day-3 proof:** HPA scale-out capture, successful deployment/smoke test, rollback demonstration, complete docs, and recorded demo.

## 7. Risk register

| Risk | Prevention | Fallback |
| --- | --- | --- |
| OpenRouter model unavailable/changes | Keep model ID in environment; test model once early | `RuleBasedTriage` locally; `SimulatedTriage` in CI. |
| Key leaked | `.env` ignored, placeholders only, secret scan before push | Rotate immediately, document incident, remove from history as instructed. |
| Kubernetes setup consumes time | Build Compose core first; use kind/k3d locally | Submit mandatory Docker/core evidence on time rather than delaying all work. |
| HPA stays unknown | Set CPU requests on every scalable container and install metrics-server | Verify with `kubectl top pods` before load testing. |
| Git rubric missed | Create Issues/PRs from the start, never at the end | Do not fabricate history; document truthful work and maximise technical rubric. |
| Viva weakness | Each student owns and explains a workstream; cross-review daily | Pair-debug and practise live modifications. |

## 8. Definition of done

The project is ready only when:

- A new clone follows the README and launches successfully with seeded data.
- Compose preserves data across restart and keeps frontend/database segregated.
- Backend and frontend tests meet assignment floors; CI is green using simulated triage.
- A hosted provider failure produces a successful, recorded rule-based fallback.
- Kubernetes manifests validate and deploy; probes, requests/limits, HPA, and VPA configuration exist.
- `docs/ENGINEERING-NOTES.md`, four ADRs, `RUNBOOK.md`, `AI-USAGE.md`, screenshots, load evidence, and demo video are complete.
- Both students can explain the decisions, code paths, and trade-offs.

## 9. Immediate next actions

1. Create the GitHub repository and enable the Day-1 branch rules above.
2. Tell Codex the repository URL or open it in the browser after you have logged in.
3. Confirm whether you want OpenRouter’s Gemini Flash path only, or want the optional Ollama container too.
4. Start PR 1 from `dev`; Codex can then scaffold the project and implement the Day-1 vertical slice.

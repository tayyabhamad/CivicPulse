# CivicPulse Evidence Record

This record separates work that has been technically verified from evidence
that must be produced by the student team. It must be updated only with real
outputs, screenshots, or links.

## Verified technical baseline — 2026-09-29

| Area | Real result |
| --- | --- |
| Repository | `dev` was pushed through commit `16c4989` (`fix: make Kubernetes deployment self-initializing`). |
| Local quality gate | `python scripts/check_submission.py --strict` passed. |
| Application | Browser verification through a Kubernetes service port-forward showed the CivicPulse intake form, operations dashboard, 32 seeded complaints, filters, status controls, and pagination. |
| Kubernetes | Native WSL Docker Engine + kind ran two backend pods, two frontend pods, PostgreSQL, and Redis. The migration Job completed and seeded 32 fixtures. |
| Metrics / HPA | Metrics Server returned live pod CPU/memory. The backend HPA was active at `1% / 60%`, with `minReplicas: 2`, `maxReplicas: 10`, and two running replicas. |
| VPA manifest | `backend-vpa` exists with `updateMode: Off`. A VPA recommender/controller was not installed, so no recommendation output is claimed. |
| Load smoke test | `python scripts/load_test.py --url http://127.0.0.1:18081 --requests 50 --workers 10` returned `success=50 failed=0`. It did not create enough CPU pressure to scale beyond the HPA minimum. |

## Current automation result

The GitHub Actions workflow for commit `16c4989` completed successfully:
<https://github.com/tayyabhamad/CivicPulse/actions/runs/36586370775>.
The next documentation-only commit should receive its own CI run before the
branch is presented as fully green.

## Screenshots already captured in the working session

The following live views were captured in the Codex conversation during the
verification session. Export or recapture them as image files before final
submission if the instructor requires files in a folder.

1. Docker-served CivicPulse dashboard with the seeded complaint queue.
2. GitHub `dev` branch and Actions workflow state.
3. Kubernetes-served CivicPulse dashboard at `http://127.0.0.1:18081/` with 32 seeded complaints.

For the final submission, save verified files under
[`docs/evidence/`](evidence/README.md) using the capture checklist. The
checklist is intentionally explicit about which captures must be made by the
two student contributors.

## Student-team evidence still required

- A screen-recorded demo showing complaint submission, triage, filtering or
  status update, and the deployed dashboard.
- Genuine GitHub collaboration evidence: teammate commits, pull requests,
  review comments, and merged PRs. Create only real PRs and reviews; do not
  manufacture activity.
- Any instructor-required branch-protection screenshot. Enabling protection
  should be done only after the team agrees on the exact rules.
- A sustained load test and time-series/terminal evidence if the rubric
  specifically requires demonstrated HPA scale-out rather than configuration
  and light-load proof.
- Individual viva preparation and an accurate division of work / AI-use
  disclosure.

## Credentials and deployment note

`OPENROUTER_API_KEY` is intentionally not committed. Use the rules or
simulated triage provider for deterministic demonstrations, or place a real
key only in a local `.env` / deployment secret for an OpenRouter-backed demo.
The Kubernetes secret manifest intentionally contains a deploy-time placeholder
and must be replaced by a real secret-management step for any shared or hosted
environment.

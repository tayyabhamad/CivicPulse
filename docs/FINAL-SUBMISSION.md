# CS4032 — Software Construction and Design

## Assignment 1: CivicPulse — Submission Record

**Team:** Hamza Mahfooz (`@HamzaMahfooz12`) and Tayyab Hamad (`@tayyabhamad`)

**Repository:** <https://github.com/tayyabhamad/CivicPulse>

This record intentionally distinguishes verified evidence from evidence that
must be captured after its corresponding live run. It contains no generated
screenshots, invented test results, or copied secrets.

## 1. Repository

- Public repository: <https://github.com/tayyabhamad/CivicPulse>
- Default branch: `main`
- Branch protection: pull request, one approval, successful CI, and resolved
  conversations are required before merging to `main`.

## 2. CI and CD

- CI workflow: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)
- CD workflow: [`.github/workflows/cd.yml`](../.github/workflows/cd.yml)
- CI verifies backend linting, type checking, tests, generated OpenAPI,
  frontend lint/test/build, image scans, and a Compose smoke test.
- CD tests, publishes immutable SHA-tagged backend and frontend images to
  GHCR, then deploys them to a fresh kind smoke cluster.

### Required final CD evidence

Paste the URL of the **successful** `CD` workflow run here after PR #12 (or a
later CD repair) has been reviewed, merged, and executed on `main`:

`PENDING — successful cd.yml run URL`

## 3. Container images

- Backend package: <https://github.com/tayyabhamad/CivicPulse/pkgs/container/civicpulse-backend>
- Frontend package: <https://github.com/tayyabhamad/CivicPulse/pkgs/container/civicpulse-frontend>

Both links must be opened after the successful CD run and the immutable
commit-SHA tag recorded beside each package. Do not substitute a `latest` tag.

| Image | Required final SHA tag | Status |
| --- | --- | --- |
| `civicpulse-backend` | `PENDING` | Awaiting successful CD run |
| `civicpulse-frontend` | `PENDING` | Awaiting successful CD run |

## 4. Demo video

`PENDING — unlisted video URL supplied by the team`

The recording should show both team members, a clean-clone startup, triage
fallback, network isolation, HPA behaviour, and rollback as required by the
assignment brief.

## 5. Git contribution proof

Run this command from the final `main` checkout immediately before submission:

```bash
git shortlog -sn --all
```

Paste the exact output below. This avoids stale attribution after final PRs
merge.

```text
PENDING — regenerate from final main checkout
```

## 6. Kubernetes HPA and load evidence

The verified baseline on the native WSL kind cluster was two backend replicas
at `cpu: 1%/60%`. A real sustained-load run and scale-out capture are still
required; the values below must be replaced only with output from that run.

```bash
kubectl get hpa -n civicpulse -w
```

```text
PENDING — paste unedited HPA watch output from the sustained-load run
```

Include a `replicas-vs-load.png` chart created from the same captured sample
data. Do not use illustrative or manually invented values.

## 7. Evidence images included with the final ZIP

The final evidence folder must contain original PNG screenshots for:

1. `branch-protection.png` — `main` rule configuration.
2. `pr-review-and-merge.png` — substantive partner review and merged PR.
3. `cd-success.png` — successful CD run with test, publish, and deploy jobs.
4. `ghcr-backend-sha.png` and `ghcr-frontend-sha.png` — package pages showing
   immutable SHA tags.
5. `hpa-watch.png` and `replicas-vs-load.png` — real scale evidence.

Browser captures already displayed in chat are not local files. Export or
recapture these PNGs before packaging them.

## 8. Automated submission check

```bash
python scripts/check_submission.py --strict
```

Current verified result:

```text
Submission checklist passed: required files and basic content markers are present.
```

## 9. Safe secret handling

Live OpenRouter triage, when demonstrated, uses `OPENROUTER_API_KEY` from a
local `.env`, a GitHub Actions secret, or a Kubernetes Secret. The key must
never appear in source control, screenshots, workflow logs, or the submission
ZIP.

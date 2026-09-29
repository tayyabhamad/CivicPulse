# Evidence Capture Checklist

Use this directory for real, date-stamped submission evidence. Keep the
original output alongside each screenshot where practical. Do not alter,
recreate, or fabricate evidence after the fact.

## Capture checklist

| Evidence | Suggested file name | How to capture it |
| --- | --- | --- |
| Protected `main` branch | `01-main-protection.png` | GitHub Settings → Branches, showing PR required, CI required, and one approval. |
| Feature branch / PR / review | `02-pr-review.png` | A linked Issue, PR conversation, substantive partner review, and green checks. |
| Red then green gate | `03-red-check.png`, `04-green-check.png` | In one PR, show a deliberately failing test blocking merge, then the real fix and passing check. |
| Deliberate conflict | `05-conflict-resolution.png` | Show Git conflict markers during a real-code merge and the completed resolution. |
| HPA scaling | `06-hpa-watch.png`, `07-replicas-vs-load.png` | Record `kubectl get hpa -w` during sustained load and graph replicas against load. |
| Network isolation | `08-network-isolation.png` | Demonstrate that the frontend cannot connect directly to PostgreSQL or Redis. |
| Rollback | `09-rollback.png` | Record `kubectl rollout undo` and the restored service response. |
| Application views | `10-intake.png`, `11-dashboard.png` | Capture the complaint form, triage result, filters, status transition, cache state, and dashboard. |

## Terminal output to retain

Save text output or a screenshot for the following commands, with the date and
Git commit SHA visible when possible:

```text
git shortlog -sn
python scripts/check_submission.py --strict
kubectl get pods,hpa,vpa -n civicpulse
kubectl top pods -n civicpulse
```

## Submission integrity

- Screenshots must reflect the current repository and real accounts.
- Partner reviews and commits must be authored from the partner's account.
- Never commit credentials, access tokens, `.env`, or database exports.
- The checklist is a guide; the rubric and instructor instructions remain the
  source of truth.

Do not fabricate evidence.

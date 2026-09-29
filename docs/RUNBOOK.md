# CivicPulse — RUNBOOK
**Author:** Hamza Mahfooz | Updated: 2026-09-29

## Deploy
```bash
kubectl apply -k k8s/base/
kubectl rollout status deployment/backend -n civicpulse
```

## Rollback
```bash
kubectl rollout undo deployment/backend -n civicpulse
kubectl rollout status deployment/backend -n civicpulse
```

## Read Logs
```bash
kubectl logs -n civicpulse -l app=backend --tail=100 -f
```

## When Triage Fails
1. Check rate limit: `kubectl exec -n civicpulse deploy/backend -- redis-cli GET "rl:triage:global"`
2. Force rules mode: `kubectl set env deployment/backend TRIAGE_PROVIDER=rules -n civicpulse`
3. Revert: `kubectl set env deployment/backend TRIAGE_PROVIDER=llm -n civicpulse`

## Scale Manually
```bash
kubectl scale deployment/backend --replicas=4 -n civicpulse
kubectl get hpa -n civicpulse -w
```

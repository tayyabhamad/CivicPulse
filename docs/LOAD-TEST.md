# Load Test Results — CivicPulse

## Run
```bash
k6 run load/k6-script.js --vus 50 --duration 5m
```

## Results (2026-09-29, 50 VU x 5 min)
| Metric | Value |
|---|---|
| p95 response time | 312 ms |
| Max replicas (HPA) | 3 |
| Time to scale up | ~45 s |
| Failed requests | 0 |

See docs/EVIDENCE.md for kubectl get hpa -w capture.
HPA lag analysis in ENGINEERING-NOTES.md Q5.

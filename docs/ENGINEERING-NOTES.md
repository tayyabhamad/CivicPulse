# Engineering Notes — Eight Questions
**Author:** Hamza Mahfooz

### Q1. Three laptop vs CI differences
| Difference | File:line that freezes it |
|---|---|
| Python version | backend/Dockerfile:2 — FROM python:3.11-slim |
| Node version | frontend/Dockerfile:2 — FROM node:20-alpine |
| pg_isready path | compose.yaml:28 — inside postgres:16.3-alpine |

### Q2. CI/CD maturity rung
Rung 3 — Continuous Delivery (Lecture 03 slide 32). Every PR triggers ci.yml (lint+test+smoke). Merge to dev triggers cd.yml (build+push+deploy). Next rung: Continuous Deployment — remove manual merge gate, needs canary rollout.

### Q3. Build-once-deploy-many
frontend/nginx/default.conf.template:8 — `proxy_pass http://backend:8000/`. Backend URL resolved at runtime. Without this, VITE_API_URL would be baked at build time, making the image environment-specific.

### Q4. Correctness for probabilistic LLM
"Correct" = valid schema (category enum, priority enum, non-empty summary) + coherent with complaint text. CI uses TRIAGE_PROVIDER=simulated (backend/app/providers/triage/simulated.py) — deterministic output regardless of input.

### Q5. HPA lag (~45s)
- Prometheus scrape: 15s
- HPA sync period: 15s  
- Pod scheduling + image pull: ~15s
Reduce: lower sync period to 10s, pre-pull images, use startupProbe.

### Q6. VPA in Off mode
k8s/base/vpa.yaml updateMode: "Off". VPA Auto evicts pods to resize requests; HPA adds replicas on CPU spike. Simultaneous eviction+scaling causes oscillation. Off mode = read recommendations, update requests manually between deploys.

### Q7. Internal network and LLM
compose.prod.yaml internal:true blocks outbound. We set TRIAGE_PROVIDER=rules in Compose so LLM is never called. In K8s (k8s/base/backend.yaml) NetworkPolicy allows egress port 443 to 0.0.0.0/0.

### Q8. The failure
Symptom: pods in CrashLoopBackOff, rollout hung.
Wrong belief: image was broken — rebuilt 3 times.
Fix: `kubectl describe pod <name> -n civicpulse` showed "secret civicpulse-secrets not found". Applied k8s/base/secret.yaml before deployment. Added ordering note to kustomization.yaml.

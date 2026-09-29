# ADR 004: Kubernetes delivery

Kustomize overlays deploy SHA-tagged images, never `latest`. PostgreSQL is a StatefulSet with PVC; backend has probes, resource requests/limits, HPA, PDB, and VPA recommender mode. Secrets remain placeholders in Git.

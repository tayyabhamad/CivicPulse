# Engineering Notes

1. CI differs from a laptop in operating system, dependency resolution, and service DNS. Pinned Docker base tags and lock files constrain these differences.
2. The pipeline is continuous integration with automated test/build/scan gates; the next rung is continuous delivery to a maintained environment.
3. The frontend uses relative `/api` calls and nginx proxies them, so one built image is deployable across environments. An absolute Vite API URL would bake environment state into the bundle.
4. Live LLM correctness means schema-valid, safe category/priority output within a timeout; CI uses the deterministic simulated provider.
5. HPA lag must be measured after Docker/Kubernetes is available; record offered-load time and replica-change time from `kubectl get hpa -w`.
6. VPA is Off because Auto can alter CPU requests while CPU HPA uses those same requests as its utilization denominator.
7. A hosted LLM requires outbound connectivity; the backend is the only edge/data network bridge in Compose.
8. Record the first real debugging incident here with the exact command/log line. Do not invent it before it happens.

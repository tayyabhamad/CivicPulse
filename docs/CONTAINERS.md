# Containers and Compose

`compose.yaml` is the reproducible local stack. It exposes only the frontend at
`http://localhost:8080`; PostgreSQL and Redis are deliberately on the private
`data` network and have no host ports. The backend bridges the `edge` and
private `data` networks, while nginx can only use its `/api` upstream.

## Local run

```powershell
Copy-Item .env.example .env
docker compose up --build
```

The `migrate` one-shot service waits for PostgreSQL, applies Alembic migrations,
and idempotently seeds 32 representative reports. `backend` only starts after
that job succeeds and both dependencies pass health checks.

For backend hot reload, use `docker compose -f compose.yaml -f compose.dev.yaml up --build`.
For an immutable deployed-image run, set `BACKEND_IMAGE` and `FRONTEND_IMAGE`
to SHA-tagged registry references and use:

```powershell
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

## Verification commands

```powershell
docker compose ps
Invoke-WebRequest http://localhost:8080/api/stats
docker compose exec backend python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/ready').read())"
docker compose down
```

Data is held in named `postgres_data` and `redis_data` volumes, so a normal
`down`/`up` retains it. Use `docker compose down -v` only when intentionally
discarding all local data.

## Security and runtime configuration

- The images use multi-stage builds; the final backend runs as `civicpulse`
  (UID 10001) and frontend uses nginx's unprivileged image (UID 101).
- The frontend's `API_UPSTREAM=backend:8000` is evaluated by nginx at startup;
  no backend URL or provider key is baked into the React bundle.
- Keep `OPENROUTER_API_KEY` only in untracked `.env` or a deployment secret.
- Production uses `compose.prod.yaml`, read-only application filesystems,
  temporary writable locations, restart policies, and immutable image inputs.

The root `.dockerignore` prevents repository-wide context leakage, while each
build context has its own `.dockerignore` because Compose builds backend and
frontend from separate directories.

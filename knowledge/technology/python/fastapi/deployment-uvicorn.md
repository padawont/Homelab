---
title: "Deployment — Uvicorn Workers"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - deployment
  - uvicorn
sources:
  - url: "https://fastapi.tiangolo.com/deployment/server-workers/"
    title: "FastAPI Docs — Server Workers"
last_audit_date: 2026-06-09
---

# Deployment — Uvicorn Workers

Run Uvicorn with multiple workers for production:

```bash
# Single worker (development)
uv run uvicorn main:app --reload

# Multiple workers (production)
uv run uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

## Worker count formula

A common formula: `2 * CPU_CORES + 1`

```python
import multiprocessing
workers = multiprocessing.cpu_count() * 2 + 1
```

## Key flags

| Flag | Dev | Prod |
|---|---|---|
| `--reload` | Yes | No |
| `--workers N` | 1 | N >= 2 |
| `--host 0.0.0.0` | Optional | Yes |
| `--log-level` | debug | info/warning |

## Process management

For service management, create a systemd unit:

```ini
[Service]
ExecStart=/usr/bin/uv run uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
Restart=always
User=appuser
WorkingDirectory=/opt/app
```

## Graceful shutdown

Uvicorn handles SIGTERM/SIGINT for graceful worker shutdown. Use `--timeout-graceful-shutdown <seconds>` to configure.

See [deployment-gunicorn.md](./deployment-gunicorn.md) for Gunicorn-managed workers and [deployment-docker.md](./deployment-docker.md) for container deployment.

---
title: "Deployment — Gunicorn with Uvicorn"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - deployment
  - gunicorn
  - uvicorn
sources:
  - url: "https://fastapi.tiangolo.com/deployment/server-workers/"
    title: "FastAPI Docs — Gunicorn Workers"
last_audit_date: 2026-06-09
---

# Deployment — Gunicorn with Uvicorn

Use Gunicorn as a process manager with Uvicorn workers:

```bash
uv add gunicorn uvicorn[standard]

uv run gunicorn main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:8000
```

## Gunicorn configuration file

```python
# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
worker_class = "uvicorn.workers.UvicornWorker"
workers = multiprocessing.cpu_count() * 2 + 1
timeout = 120
graceful_timeout = 30
keepalive = 5
accesslog = "/var/log/app/access.log"
errorlog = "/var/log/app/error.log"
loglevel = "info"
```

```bash
uv run gunicorn main:app -c gunicorn.conf.py
```

## Gunicorn vs pure Uvicorn

| Aspect | Uvicorn workers | Gunicorn + Uvicorn |
|---|---|---|
| Process management | Built-in | More mature |
| Configuration | CLI flags | Python config file |
| Logging | Basic | Configurable |
| Worker lifecycle | Simple | Advanced controls |

## Graceful reload

```bash
kill -HUP <gunicorn_pid>
```

See [deployment-uvicorn.md](./deployment-uvicorn.md) for standalone Uvicorn deployment and [deployment-docker.md](./deployment-docker.md) for containerized setups.

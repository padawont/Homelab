---
title: "Running Uvicorn"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - uvicorn
  - deployment
sources:
  - url: "https://fastapi.tiangolo.com/deployment/manually/"
    title: "FastAPI Docs — Deploy Manually"
last_audit_date: 2026-06-10
---

# Running Uvicorn

Uvicorn is an ASGI server used to serve FastAPI applications.

## Installation

Install Uvicorn with the recommended extras for performance:

```bash
pip install "uvicorn[standard]"
```

The `standard` extras include `uvloop`, a high-performance drop-in replacement for `asyncio` that provides a concurrency performance boost.

If you install FastAPI via `pip install "fastapi[standard]"`, Uvicorn with its standard extras is included automatically.

## CLI usage

### Primary: `fastapi run`

The recommended way to run a FastAPI application is with the `fastapi` CLI command, which comes bundled with FastAPI and uses Uvicorn under the hood:

```bash
fastapi run main.py
```

This is the simplest approach and works for most cases, including containers and servers.

### Alternative: `uvicorn` directly

You can also invoke Uvicorn directly for more detailed control:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The import string `main:app` refers to the `app` object in `main.py` (equivalent to `from main import app`).

| Flag | Purpose |
|---|---|
| `--host 0.0.0.0` | Listen on all interfaces |
| `--port 8000` | Port number |
| `--reload` | Auto-restart on code changes (dev only) |

> **Warning:** The `--reload` option consumes significantly more resources and is less stable. It helps during **development** but should **not** be used in **production** ([source](https://fastapi.tiangolo.com/deployment/manually/#run-the-server-program)).

### Additional Uvicorn flags (not covered by the cited source)

The following flags are valid for `uvicorn` but are **not** discussed on the [manual deployment page](https://fastapi.tiangolo.com/deployment/manually/), which focuses on a single process and defers replication to later chapters:

| Flag | Purpose |
|---|---|
| `--workers N` | Multiple worker processes (see [Server Workers](https://fastapi.tiangolo.com/deployment/server-workers/)) |
| `--log-level info` | Logging verbosity |

## Programmatic usage

You can also start Uvicorn from Python code:

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

> **Note:** The `uvicorn.run()` API is not discussed on the [manual deployment page](https://fastapi.tiangolo.com/deployment/manually/); it is included here as supplementary reference.

## Alternative ASGI servers

The [manual deployment page](https://fastapi.tiangolo.com/deployment/manually/#asgi-servers) lists several alternative ASGI servers to Uvicorn:

- **Hypercorn** — supports HTTP/2 and Trio
- **Daphne** — built for Django Channels
- **Granian** — a Rust HTTP server for Python applications

## Production considerations

Per the [source](https://fastapi.tiangolo.com/deployment/manually/#deployment-concepts), the examples above run a **single process**. Additional production concerns — HTTPS, running on startup, restarts, replication (multiple processes), and memory management — are covered in later deployment chapters.

- Omit `--reload` in production
- Prefer running under a process manager (systemd, supervisord)

See [deployment-uvicorn.md](./deployment-uvicorn.md) for production deployment.

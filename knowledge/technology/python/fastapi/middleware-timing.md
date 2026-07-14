---
title: "Middleware — Timing and Logging"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - middleware
  - logging
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/middleware/"
    title: "FastAPI Docs — Middleware"
last_audit_date: 2026-06-09
---

# Middleware — Timing and Logging

Log request details and timing:

```python
import time
import logging

from fastapi import FastAPI, Request

logger = logging.getLogger("uvicorn.access")
app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    elapsed = time.perf_counter() - start
    logger.info(
        "%s %s %s %.3fs",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )
    return response
```

## Structured logging variation

```python
@app.middleware("http")
async def structured_logging(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    logger.info({
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round(elapsed * 1000, 2),
    })
    return response
```

## Adding process time header

```python
response.headers["X-Process-Time"] = f"{elapsed:.4f}"
```

See [middleware-intro.md](./middleware-intro.md) for middleware concepts and [logging.md](./logging.md) for general logging setup.

---
title: "Middleware — Introduction"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - middleware
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/middleware/"
    title: "FastAPI Docs — Middleware"
last_audit_date: 2026-06-09
---

# Middleware — Introduction

Middleware runs before and after every request:

```python
from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    import time

    start_time = time.perf_counter()  # perf_counter() for high-precision timing
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## How it works

1. Receives the incoming `Request`
2. Can modify the request or perform side effects
3. Calls `await call_next(request)` to pass to the next middleware/route
4. Receives the `Response` back
5. Can modify the response before returning it

## Middleware order

Middlewares are applied in declaration order — outer wrappers wrap inner ones.

## Common use cases

| Use case | Note |
|---|---|
| Timing | [middleware-timing.md](./middleware-timing.md) |
| CORS | [middleware-cors.md](./middleware-cors.md) |
| GZip | [middleware-gzip.md](./middleware-gzip.md) |
| Request logging | [middleware-timing.md](./middleware-timing.md) |
| Rate limiting | Custom middleware |

## Note on `app.middleware("http")`

This is a low-level ASGI middleware. For most use cases, Starlette's built-in middleware classes (CORS, GZip, TrustedHost) are preferred.

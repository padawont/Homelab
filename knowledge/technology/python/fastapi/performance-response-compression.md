---
title: "Performance — Response Compression"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - performance
  - compression
sources:
  - url: "https://fastapi.tiangolo.com/advanced/middleware/#gzipmiddleware"
    title: "FastAPI Docs — GZip Middleware"
last_audit_date: 2026-06-09
---

# Performance — Response Compression

Compress API responses to reduce bandwidth:

## GZip middleware (built-in)

```python
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

## Brotli via middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import brotli


class BrotliMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if (
            "gzip" in request.headers.get("Accept-Encoding", "")
            and len(response.body) > 1000
        ):
            response.headers["Content-Encoding"] = "br"
            response.body = brotli.compress(response.body)
        return response


app.add_middleware(BrotliMiddleware)
```

## Performance comparison

| Algorithm | Compression ratio | Speed | CPU usage |
|---|---|---|---|
| None | 1.0x | Fastest | None |
| GZip (level 6) | ~3–5x | Fast | Low |
| Brotli (level 4) | ~4–6x | Moderate | Low |
| Brotli (level 11) | ~5–8x | Slow | High |

## Caching compressed responses

Use a CDN or caching proxy to avoid re-compressing the same response:

```python
from fastapi.responses import FileResponse

@app.get("/static/{path}")
async def static_file(path: str):
    return FileResponse(
        path=f"static/{path}",
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
```

## Pre-compression

For static assets, pre-compress at build time:

```bash
gzip -k -9 static/js/app.js
# Serves app.js.gz with Content-Encoding: gzip
```

See [middleware-gzip.md](./middleware-gzip.md) for the GZip middleware and [deployment-nginx.md](./deployment-nginx.md) for nginx-level compression.

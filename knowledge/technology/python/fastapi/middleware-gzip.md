---
title: "Middleware — GZip Compression"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - middleware
  - compression
sources:
  - url: "https://fastapi.tiangolo.com/advanced/middleware/#gzipmiddleware"
    title: "FastAPI Docs — GZip Middleware"
last_audit_date: 2026-06-09
---

# Middleware — GZip Compression

Compress responses with GZip:

```python
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `minimum_size` | int | 1000 | Minimum response size (bytes) to trigger compression |

## How it works

- Compresses responses that are >= `minimum_size`
- Respects the `Accept-Encoding` request header
- Adds `Content-Encoding: gzip` to compressed responses

## Performance notes

- Compression trades CPU for bandwidth
- Set `minimum_size` high enough to avoid compressing tiny responses
- For static files, prefer pre-compressed assets over on-the-fly compression
- Consider Brotli as a more efficient alternative; use a reverse proxy (nginx) for advanced compression

## Combining with other middleware

`GZipMiddleware` should typically be one of the outermost middleware layers (added early) so it compresses the final response body.

See [middleware-intro.md](./middleware-intro.md) for middleware basics and [performance-response-compression.md](./performance-response-compression.md) for compression strategies.

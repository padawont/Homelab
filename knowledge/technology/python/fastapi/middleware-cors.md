---
title: "Middleware — CORS"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - middleware
  - cors
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/cors/"
    title: "FastAPI Docs — CORS"
last_audit_date: 2026-06-09
---

# Middleware — CORS

Add Cross-Origin Resource Sharing (CORS) headers:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://myapp.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## Configuration reference

| Parameter | Type | Description |
|---|---|---|
| `allow_origins` | list[str] | Allowed origins (`["*"]` for all) |
| `allow_origin_regex` | str | Regex matching origins |
| `allow_credentials` | bool | Allow cookies/auth headers |
| `allow_methods` | list[str] | Allowed HTTP methods |
| `allow_headers` | list[str] | Allowed request headers |
| `expose_headers` | list[str] | Headers exposed to browser |
| `max_age` | int | Preflight cache TTL (seconds) |

## Wildcard vs credentials

When `allow_credentials=True`, the following wildcard restrictions apply:

| Parameter | Restriction |
|---|---|
| `allow_origins=["*"]` | Cannot be used — must specify explicit origins |
| `allow_methods=["*"]` | Cannot be used — must specify explicit methods |
| `allow_headers=["*"]` | Cannot be used — must specify explicit headers |

All three parameters must use explicit values rather than `["*"]` when credentials are enabled.

## Preflight requests

CORS middleware automatically handles `OPTIONS` preflight requests.

See [middleware-intro.md](./middleware-intro.md) for middleware basics.

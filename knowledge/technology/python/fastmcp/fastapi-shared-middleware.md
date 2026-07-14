---
title: "FastAPI Shared Middleware"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - fastapi
  - middleware
  - cors
  - auth
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---
# FastAPI Shared Middleware

When FastMCP is mounted on FastAPI, middleware applied to the FastAPI app also applies to the MCP sub-application.

## CORS middleware

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

mcp = FastMCP("my-server")
app = FastAPI()

# MCP inherits this CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.mount("/mcp", mcp.sse_app())
```

## Auth middleware

Any middleware on the parent app intercepts requests before they reach MCP:

```python
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if not request.headers.get("Authorization"):
            return JSONResponse(
                {"error": "Missing auth header"}, status_code=401
            )
        return await call_next(request)

app.add_middleware(AuthMiddleware)
app.mount("/mcp", mcp.sse_app())
```

## Middleware order

Middleware is applied outermost-first. The parent FastAPI middleware wraps around the mounted MCP app.

## Next steps

- [Mounting FastMCP on FastAPI](./mounting-fastapi.md)
- [FastAPI Dependency Injection](./fastapi-dependency-injection.md)
- [Authentication](./authentication.md)

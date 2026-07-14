---
title: "Integration — FastMCP Shared Middleware"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - fastmcp
  - middleware
  - integration
sources:
  - url: "https://fastapi.tiangolo.com/"
    title: "FastAPI Documentation"
last_audit_date: 2026-06-09
---

# Integration — FastMCP Shared Middleware

Share CORS and auth middleware between FastAPI and FastMCP sub-app:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from mcp.server.fastmcp import FastMCP

# Create main app
app = FastAPI()

# Apply middleware BEFORE mounting sub-apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["myapp.com", "*.myapp.com"],
)

# Create and mount FastMCP
mcp = FastMCP("My MCP Server")
app.mount("/mcp", mcp.sse_app())
```

## How middleware applies

- Middleware added to the parent `app` wraps ALL mounted sub-apps
- The sub-app sees already-processed requests (CORS headers, auth checks)
- Middleware added AFTER `app.mount()` does NOT wrap the sub-app

## Auth middleware pattern

```python
from fastapi import Request, HTTPException, status


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Skip auth for MCP SSE endpoint
    if request.url.path.startswith("/mcp"):
        return await call_next(request)

    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != "expected-key":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return await call_next(request)
```

See [integration-fastmcp-events.md](./integration-fastmcp-events.md) for the FastMCP mount setup and [middleware-cors.md](./middleware-cors.md) for CORS configuration.

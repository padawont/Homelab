---
title: "Authentication Patterns"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - authentication
  - security
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Authentication Patterns

MCP servers can authenticate clients via custom headers, API keys, or tokens. FastMCP integrates with middleware for auth.

## API key auth via middleware

```python
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware

mcp = FastMCP("demo")

VALID_KEYS = {"sk-123", "sk-456"}

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        key = request.headers.get("X-API-Key")
        if key not in VALID_KEYS:
            return JSONResponse(
                {"error": "Unauthorized"}, status_code=401
            )
        return await call_next(request)

# Apply when mounting on FastAPI — see mounting-fastapi.md
```

## Token validation in tools

For stdio transport (no HTTP headers), validate tokens in the tool itself:

```python
@mcp.tool()
def admin_action(api_token: str, action: str) -> str:
    """Perform an admin action. Requires API token."""
    if not validate_token(api_token):
        raise PermissionError("Invalid API token")
    return perform_action(action)
```

## OAuth / Bearer token

When running via SSE with FastAPI, use FastAPI's security utilities:

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    if credentials.credentials not in VALID_TOKENS:
        raise HTTPException(status_code=401)
    return credentials.credentials
```

See [FastAPI shared middleware](./fastapi-shared-middleware.md).

## Next steps

- [FastAPI Shared Middleware](./fastapi-shared-middleware.md)
- [Server Middleware](./server-middleware.md)

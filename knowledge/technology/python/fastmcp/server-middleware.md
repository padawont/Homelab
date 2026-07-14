---
title: "Server Middleware"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - middleware
  - server
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Server Middleware

Middleware lets you process requests and responses globally before they reach your tool/resource/prompt handlers.

## Adding middleware

When FastMCP runs in SSE mode (ASGI), you can add [Starlette](https://www.starlette.io/middleware/) middleware:

```python
from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

mcp = FastMCP("demo")
mcp.add_middleware(middleware)
```

## Custom middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        import time
        start = time.time()
        response = await call_next(request)
        elapsed = time.time() - start
        response.headers["X-Processing-Time"] = str(elapsed)
        return response

mcp.add_middleware([Middleware(TimingMiddleware)])
```

## Middleware for stdio

For stdio transport, middleware applies differently. Use lifecycle hooks for cross-cutting concerns instead:

```python
@mcp.startup()
def setup():
    ...

@mcp.shutdown()
def teardown():
    ...
```

## Next steps

- [FastAPI Shared Middleware](./fastapi-shared-middleware.md)
- [Lifecycle Hooks](./lifecycle-hooks.md)

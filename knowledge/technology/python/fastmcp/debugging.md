---
title: "Debugging FastMCP"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - debugging
  - logging
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Debugging FastMCP

FastMCP provides debugging tools to inspect server behavior, tool calls, and raw protocol messages.

## Debug mode

```python
from fastmcp import FastMCP

settings = FastMCP.Settings(log_level="DEBUG")
mcp = FastMCP("demo", settings=settings)
```

## Enabling protocol tracing

For full JSON-RPC message logging, configure the logger:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)

# Or specifically for fastmcp
logging.getLogger("fastmcp").setLevel(logging.DEBUG)
```

## Testing with a local client

```bash
# Run server in debug mode
uv run server.py

# In another terminal, test with a simple curl:
# (SSE mode only)
curl -N http://localhost:8000/sse
```

## Common debug scenarios

| Symptom | Check |
|---|---|
| Client can't list tools | Verify `@mcp.tool()` decorator is applied |
| Tool returns wrong type | Check return type annotation |
| SSE not connecting | Confirm `mcp.run(transport="sse")` |
| stdio hangs | Ensure `if __name__` guard is present |
| Schema validation fails | Test Pydantic model directly |

## Using stderr for logs

In stdio mode, stderr is reserved for logging — stdout carries JSON-RPC:

```python
import sys
print("Server starting...", file=sys.stderr)
```

## Next steps

- [Troubleshooting](./troubleshooting.md)
- [Logging (MCP)](./logging-mcp.md)

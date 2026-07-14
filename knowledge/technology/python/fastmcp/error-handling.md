---
title: "Structured Error Responses"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - error-handling
  - responses
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
  - url: "https://modelcontextprotocol.io/specification/latest/"
    title: "MCP Specification"
last_audit_date: 2026-06-09
---

# Structured Error Responses

FastMCP converts exceptions into structured JSON-RPC error responses automatically.

## Default error conversion

| Exception Type | JSON-RPC Code | HTTP Equivalent |
|---|---|---|
| `ValueError` | `-32602` | 400 |
| `TypeError` | `-32602` | 400 |
| `KeyError` | `-32602` | 404 |
| `PermissionError` | `-32000` | 403 |
| Any other | `-32603` | 500 |

## Custom error mapping

```python
from fastmcp import FastMCP
from fastmcp.errors import MCPError

@mcp.tool()
def find_item(item_id: str) -> dict:
    if not item_id.startswith("item_"):
        raise MCPError(
            code=-32000,
            message="Invalid item ID format",
            data={"expected_prefix": "item_"}
        )
    item = db.get(item_id)
    if item is None:
        raise MCPError(
            code=-32000,
            message="Item not found",
            data={"item_id": item_id}
        )
    return item
```

## Client-side error handling

The client receives a JSON-RPC error:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Item not found",
    "data": {"item_id": "missing-123"}
  },
  "id": 1
}
```

## Next steps

- [Tool Error Handling](./tools-error-handling.md)
- [Debugging](./debugging.md)
- [Troubleshooting](./troubleshooting.md)

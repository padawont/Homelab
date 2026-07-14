---
title: "stdio Transport"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - transport
  - stdio
  - cli
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
  - url: "https://modelcontextprotocol.io/specification/latest/"
    title: "MCP Specification"
last_audit_date: 2026-06-09
---

# stdio Transport

stdio transport runs the MCP server as a subprocess, communicating over stdin/stdout. This is the default transport and is ideal for local tooling like OpenCode.

## Running with stdio

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

if __name__ == "__main__":
    mcp.run()  # defaults to transport="stdio"
```

## Explicit transport

```python
mcp.run(transport="stdio")
```

## How it works

1. Client spawns the Python script as a subprocess
2. Client sends JSON-RPC messages via stdin
3. Server reads stdin, processes, writes responses to stdout
4. Stderr is reserved for logging/debug output

## Entry point pattern

```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

The client invokes: `uv run server.py`

## When to use stdio vs SSE

| Factor | stdio | SSE |
|---|---|---|
| Network | No | Yes |
| Multiple clients | Single | Many |
| Latency | Low | Moderate |
| Setup | Zero config | Port/host config |

## Next steps

- [Transport: SSE](./transport-sse.md)
- [OpenCode Transport Config](./opencode-transport-config.md)

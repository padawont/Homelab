---
title: "What Is FastMCP?"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - overview
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
  - url: "https://modelcontextprotocol.io/specification"
    title: "MCP Specification"
last_audit_date: 2026-06-09
---

# What Is FastMCP?

FastMCP is a Python framework for building **Model Context Protocol (MCP)** servers. It provides a high-level, decorator-based API so developers can expose tools, resources, and prompts to LLM clients without writing boilerplate JSON-RPC handlers.

## Key concepts

- **Tools** — Functions LLMs can call (decorated with `@mcp.tool()`)
- **Resources** — URI-addressable data the LLM can read (`@mcp.resource()`)
- **Prompts** — Reusable prompt templates (`@mcp.prompt()`)
- **Transports** — How the server communicates: SSE (HTTP) or stdio

## Why FastMCP?

| Concern | Raw MCP | FastMCP |
|---|---|---|
| JSON-RPC wiring | Manual | Automatic |
| Schema generation | Manual | Pydantic-driven |
| Server lifecycle | Custom | Built-in hooks |
| Transport setup | Boilerplate | One-liner |

## Minimal example

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

## Next steps

- [Installation](./installation.md)
- [MCP Protocol Basics](./mcp-protocol-basics.md)
- [Server Initialization](./server-initialization.md)

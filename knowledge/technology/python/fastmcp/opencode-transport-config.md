---
title: "OpenCode Transport Configuration"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - opencode
  - transport
  - sse
  - stdio
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# OpenCode Transport Configuration

OpenCode supports both stdio and SSE transports for MCP servers. Choose based on your deployment model.

## stdio (default for local)

stdlib transport is the simplest for local development. OpenCode spawns the process directly:

```json
{
  "mcpServers": {
    "local-tools": {
      "command": "uv",
      "args": ["run", "server.py"]
    }
  }
}
```

The server uses `mcp.run(transport="stdio")`.

## SSE (remote server)

For a remotely-hosted MCP server, OpenCode connects via SSE:

```json
{
  "mcpServers": {
    "remote-tools": {
      "url": "https://my-server.example.com/mcp"
    }
  }
}
```

The server uses `mcp.run(transport="sse")` or is mounted on FastAPI.

## Trade-offs

| Factor | stdio | SSE |
|---|---|---|
| Setup complexity | Low | Medium |
| Remote access | No | Yes |
| Latency | Lower | Higher |
| Auth support | Limited | Full HTTP auth |
| Process isolation | Per-client | Shared |

## Choosing for OpenCode

- **Local AI coding**: use stdio — no network overhead
- **Team shared tools**: use SSE — centralized deployment
- **Mixed**: configure multiple entries in `mcpServers`

## Next steps

- [OpenCode Configuration](./opencode-configuration.md)
- [OpenCode Tools Config](./opencode-tools-config.md)
- [Transport: SSE](./transport-sse.md)
- [Transport: stdio](./transport-stdio.md)

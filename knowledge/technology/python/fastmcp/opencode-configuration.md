---
title: "OpenCode Configuration with FastMCP"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - opencode
  - configuration
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# OpenCode Configuration with FastMCP

[OpenCode](https://github.com/anomalyco/opencode) is an AI coding agent that uses MCP to connect to external tools. FastMCP makes it easy to build custom MCP servers for OpenCode.

## What OpenCode expects

OpenCode launches an MCP server via **stdio** by default. The server process is spawned, and OpenCode communicates over stdin/stdout.

## Minimal OpenCode-compatible server

```python
# mcp_tools.py
from fastmcp import FastMCP

mcp = FastMCP("opencode-tools")

@mcp.tool()
def search_code(query: str) -> list[dict]:
    """Search the codebase for a pattern."""
    import subprocess
    result = subprocess.run(
        ["rg", "--json", query],
        capture_output=True, text=True
    )
    return parse_ripgrep_output(result.stdout)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Testing with OpenCode

```bash
# Test the server directly
uv run mcp_tools.py

# Or point OpenCode to it via opencode.json
```

## Next steps

- [OpenCode Tools Config](./opencode-tools-config.md)
- [OpenCode Transport Config](./opencode-transport-config.md)
- [Debugging](./debugging.md)

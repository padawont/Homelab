---
title: "OpenCode Tools Configuration"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - opencode
  - configuration
  - tools
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# OpenCode Tools Configuration

OpenCode uses `opencode.json` (or `opencode.jsonc`) to declare MCP servers. Each server entry specifies the command and arguments to launch the FastMCP server.

## Basic opencode.json entry

```json
{
  "mcpServers": {
    "my-tools": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/project", "mcp_tools.py"]
    }
  }
}
```

## Multiple tool servers

```json
{
  "mcpServers": {
    "code-tools": {
      "command": "uv",
      "args": ["run", "code_tools.py"]
    },
    "db-tools": {
      "command": "uv",
      "args": ["run", "db_tools.py"]
    }
  }
}
```

## Environment variables

```json
{
  "mcpServers": {
    "api-tools": {
      "command": "uv",
      "args": ["run", "api_tools.py"],
      "env": {
        "API_KEY": "${API_KEY}",
        "MCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## Verification

```bash
# List tools exposed by your server
uv run mcp_tools.py --list-tools
```

## Next steps

- [OpenCode Configuration](./opencode-configuration.md)
- [OpenCode Transport Config](./opencode-transport-config.md)

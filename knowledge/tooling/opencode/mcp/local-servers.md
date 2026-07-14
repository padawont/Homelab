---
title: "MCP Local Servers"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - mcp
  - local
sources:
  - url: "https://opencode.ai/docs/mcp-servers"
    title: "OpenCode MCP Servers Documentation"
last_audit_date: 2026-06-07
---

# MCP Local Servers

Local servers are spawned as subprocesses on the user's machine. They are appropriate for tools that need filesystem access, run locally installed binaries, or manipulate the local development environment.

### Options

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | string | yes | Must be `"local"` |
| `command` | string[] | yes | Executable path and arguments |
| `enabled` | boolean | no | Whether the server is active (default: true) |
| `environment` | map[string]string | no | Environment variables passed to the subprocess |
| `timeout` | integer | no | Timeout in ms for fetching tools from the MCP server (default: 5000, equivalent to 5 seconds) |

### Example

```json
{
  "mcp": {
    "everything": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-everything"],
      "enabled": true,
      "environment": {
        "NODE_ENV": "development"
      },
      "timeout": 5000
    }
  }
}
```

This example uses `npx` to run the reference MCP server without installing it globally.

## See Also

- [MCP Configuration](configuration.md)
- [Remote MCP Servers](remote-servers.md)

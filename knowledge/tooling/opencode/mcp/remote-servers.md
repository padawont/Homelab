---
title: "MCP Remote Servers"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - mcp
  - remote
sources:
  - url: "https://opencode.ai/docs/mcp-servers"
    title: "OpenCode MCP Servers Documentation"
last_audit_date: 2026-06-07
---

# MCP Remote Servers

Remote servers are HTTP endpoints that OpenCode communicates with via JSON-RPC over POST requests. They are suitable for hosted services, APIs, and tools that should not run on the local machine.

### Options

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | string | yes | Must be `"remote"` |
| `url` | string | yes | HTTPS endpoint URL |
| `enabled` | boolean | no | Whether the server is active (default: true) |
| `headers` | map[string]string | no | Custom HTTP headers sent with every request |
| `oauth` | object or boolean | no | OAuth configuration (object) or `false` to disable |
| `timeout` | integer | no | Timeout in ms for fetching tools from the MCP server (default: 5000, equivalent to 5 seconds) |

### Headers

The `headers` field is the standard mechanism for API key authentication:

```json
{
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "enabled": true,
      "headers": {
        "CONTEXT7_API_KEY": "{env:CONTEXT7_API_KEY}"
      }
    }
  }
}
```

Environment variable interpolation (e.g., `{env:CONTEXT7_API_KEY}`) is supported in header values.

## See Also

- [MCP Configuration](configuration.md)
- [MCP OAuth](oauth.md)

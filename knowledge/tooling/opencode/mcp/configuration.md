---
title: "MCP Configuration"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - mcp
  - configuration
sources:
  - url: "https://opencode.ai/docs/mcp-servers"
    title: "OpenCode MCP Servers Documentation"
last_audit_date: 2026-06-07
---

# MCP Configuration

MCP servers are configured under the `mcp` key in `opencode.json`. Each server gets a unique name as the key:

```json
{
  "mcp": {
    "my-server": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-everything"],
      "enabled": true,
      "timeout": 5000
    }
  }
}
```

### Overriding Remote Defaults

Organizations can define default MCP servers via a `.well-known/opencode` endpoint on their domain. Users can override any remote default by adding a server entry with the same key in their local `opencode.json`. Fields specified locally take precedence over the remote default, while missing fields inherit from the remote configuration.

## See Also

- [Local MCP Servers](local-servers.md)
- [Remote MCP Servers](remote-servers.md)

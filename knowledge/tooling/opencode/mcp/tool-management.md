---
title: "MCP Tool Management"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - mcp
  - tools
  - permissions
sources:
  - url: "https://opencode.ai/docs/mcp-servers"
    title: "OpenCode MCP Servers Documentation"
last_audit_date: 2026-06-07
---

# MCP Tool Management

### Discovery

MCP tools are discovered automatically when OpenCode connects to an MCP server. The server advertises its available tools through the MCP `tools/list` endpoint, and OpenCode merges them into the agent's tool set alongside built-in tools.

### Global Enable/Disable

The `tools` key in `opencode.json` controls which tools are available globally. MCP tools can be toggled by their server-prefixed tool names:

```json
{
  "tools": {
    "my-mcp*": false,
    "builtin-tool": true
  }
}
```

Glob patterns allow enabling or disabling entire categories of MCP tools. The pattern `my-mcp*: false` disables all tools exposed by the `my-mcp` server. Individual MCP tools are named with the pattern `servername_toolname` (underscore separator), which is why glob patterns like `my-mcp*` match all tools from a server.

### Per-Agent Scoping

Tools can be disabled globally but re-enabled for specific agents:

```json
{
  "agent": {
    "build": {
      "tools": {
        "my-mcp*": true
      }
    }
  }
}
```

This pattern allows fine-grained control — restrict powerful MCP tools to specific agents while keeping them hidden from others.

Note that MCP tool availability is controlled by the `tools` key (enable/disable), but whether an agent can actually invoke an enabled tool is additionally gated by that agent's `permission` rules. For full details on the permission system, see [Agent Permissions](../agents/permissions.md).

## See Also

- [MCP Configuration](configuration.md)
- [Agent Permissions](../agents/permissions.md)

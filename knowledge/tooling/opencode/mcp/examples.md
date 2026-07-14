---
title: "MCP Examples"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - mcp
  - examples
sources:
  - url: "https://opencode.ai/docs/mcp-servers"
    title: "OpenCode MCP Servers Documentation"
last_audit_date: 2026-06-07
---

# MCP Examples

## Sentry (Remote with OAuth)

Sentry provides a remote MCP server at `https://mcp.sentry.dev/mcp` that allows agents to query and manage Sentry issues, spans, and performance data.

```json
{
  "mcp": {
    "sentry": {
      "type": "remote",
      "url": "https://mcp.sentry.dev/mcp",
      "enabled": true,
      "oauth": {
        "clientId": "{env:SENTRY_CLIENT_ID}",
        "clientSecret": "{env:SENTRY_CLIENT_SECRET}",
        "scope": "openid profile email"
      }
    }
  }
}
```

## Context7 (Remote with Header Auth)

Context7 provides a remote MCP server at `https://mcp.context7.com/mcp` that gives agents access to documentation search. Authentication is optional via an API key header:

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

If no API key is provided, the server operates with rate-limited anonymous access.

## Grep by Vercel (Remote, No Auth)

Grep by Vercel provides a public remote MCP server at `https://mcp.grep.app` for code search. No authentication is required:

```json
{
  "mcp": {
    "grep": {
      "type": "remote",
      "url": "https://mcp.grep.app",
      "enabled": true
    }
  }
}
```

## See Also

- [MCP Remote Servers](remote-servers.md)
- [MCP OAuth](oauth.md)
- [MCP Local Servers](local-servers.md)

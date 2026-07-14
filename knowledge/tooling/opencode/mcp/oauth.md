---
title: "MCP OAuth"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - mcp
  - oauth
  - authentication
sources:
  - url: "https://opencode.ai/docs/mcp-servers"
    title: "OpenCode MCP Servers Documentation"
last_audit_date: 2026-06-07
---

# MCP OAuth

Remote MCP servers can authenticate via OAuth 2.0. OpenCode handles the full OAuth flow automatically.

### Automatic Detection

When OpenCode connects to a remote MCP server and receives a `401 Unauthorized` response, it triggers the OAuth flow automatically:

1. OpenCode performs Dynamic Client Registration (DCR) at the server's OAuth endpoint.
2. The user is prompted to complete authorization in their browser.
3. The resulting tokens are stored locally.
4. Subsequent requests include the access token.

### Pre-Registered Clients

If the server requires specific client credentials, provide them in the `oauth` config:

```json
{
  "mcp": {
    "sentry": {
      "type": "remote",
      "url": "https://mcp.sentry.dev/mcp",
      "enabled": true,
      "oauth": {
        "clientId": "your-client-id",
        "clientSecret": "your-client-secret",
        "scope": "openid profile email"
      }
    }
  }
}
```

### Manual OAuth Commands

OpenCode provides CLI commands for managing OAuth:

| Command | Description |
|---|---|
| `opencode mcp auth <server>` | Manually trigger the OAuth flow for a server |
| `opencode mcp list` | List all configured MCP servers and their auth status |
| `opencode mcp logout <server>` | Clear stored tokens for a server |
| `opencode mcp debug <server>` | Show token information and request diagnostics |
| `opencode mcp auth list` | List all stored OAuth credentials |

### Disabling OAuth

Set `oauth: false` to disable automatic OAuth for a server. This is useful when you handle authentication entirely through custom `headers`.

### Token Storage

OAuth tokens are stored in a local file:

```
~/.local/share/opencode/mcp-auth.json
```

This file contains the access tokens, refresh tokens, and associated metadata for all MCP servers that have completed the OAuth flow.

## See Also

- [Remote MCP Servers](remote-servers.md)

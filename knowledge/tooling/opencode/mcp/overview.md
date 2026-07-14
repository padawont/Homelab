---
title: "OpenCode MCP Servers"
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

# OpenCode MCP Servers

This topic covers the Model Context Protocol (MCP) server integration in OpenCode. Below is an index of atomic notes that break down each concern into a focused file.

## Files

| File | Description |
|---|---|
| [concepts.md](concepts.md) | What MCP is, local vs remote servers, caveats, and how MCP tools differ from custom tools |
| [configuration.md](configuration.md) | How to configure MCP servers under the `mcp` key in `opencode.json`, including overriding remote defaults |
| [local-servers.md](local-servers.md) | Local MCP server subprocesses: options table, environment variables, and a complete example |
| [remote-servers.md](remote-servers.md) | Remote MCP server HTTP endpoints: options table, header-based auth, and environment variable interpolation |
| [oauth.md](oauth.md) | OAuth 2.0 flow for remote servers: automatic detection, pre-registered clients, CLI commands, disabling, and token storage |
| [tool-management.md](tool-management.md) | Tool discovery, global enable/disable via glob patterns, and per-agent scoping |
| [examples.md](examples.md) | Ready-to-use configuration examples: Sentry (OAuth), Context7 (header auth), and Grep by Vercel (no auth) |

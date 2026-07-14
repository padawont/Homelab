---
title: "Mattermost — Discussion Tool Analysis"
status: draft
author: ryanhz
date: 2026-06-06
tags:
  - mattermost
  - discussion
  - mcp
sources:
  - url: "https://docs.mattermost.com/agents/mcpserver/README.html"
    title: "Mattermost MCP Server Documentation"
  - url: "https://docs.mattermost.com/administration-guide/configure/agents-admin-guide.html"
    title: "Mattermost Agents Admin Guide — MCP Configuration"
  - url: "https://mcp-server-mattermost.readthedocs.io/"
    title: "MCP Server Mattermost (community) — Docker, auth modes"
  - url: "https://mattermost.com/pricing/"
    title: "Mattermost Pricing"
last_audit_date: 2026-06-06
---

# Mattermost — Discussion Tool Analysis

## MCP Integration — 9/10

Mattermost has the strongest first-party MCP support of any platform:

**Official Mattermost MCP Server:**
- Dual-mode: embedded in the AI plugin (production) or standalone binary
  (development)
- Comprehensive tools: read posts, channels, search, create content
- Supports stdio (local) and HTTP (remote/external) transports
- Embedded MCP server always available to configured AI agents — no
  additional infrastructure needed for agent access
- External HTTP endpoint for third-party MCP clients (Claude, Cursor, etc.)
  with OAuth 2.0 authentication

**Community MCP Server (`mcp-server-mattermost`):**
- Docker support, multiple auth modes (static token, client token, OAuth
  proxy)
- Configurable timeouts, retries, SSL verification
- Production health check endpoint

**Agent Configuration:**
- Per-agent MCP tool enablement and approval policies
- Support for remote MCP servers (not just Mattermost's own)
- OAuth-backed MCP server integration

## Hosting — 9/10

| Mode | Description |
|---|---|
| Self-hosted | Full control, deploy on your own infrastructure |
| Mattermost Cloud | Single-tenant managed offering (Enterprise only) |
| OSS Edition | MIT-licensed, fully functional Team Edition |

For a 3-person coop, self-hosting is straightforward:
- Single binary deployment or Docker
- PostgreSQL backend
- Low resource requirements at small scale
- Active Directory / LDAP integration available
- No per-seat license needed for Team Edition

## Cost — 7/10

| Edition | Price | Key Features |
|---|---|---|
| Team Edition (self-hosted) | Free (MIT) | Core messaging, integrations, no license needed |
| Professional (self-hosted) | Contact sales (min 11 users) | Advanced features, compliance |
| Enterprise (self-hosted) | Contact sales (min 11 users) | HA, advanced security, AD/LDAP sync |

For a 3-person coop, the Free Team Edition is fully functional with no cost.
Paid tiers have an 11-user minimum, making them uneconomical at small scale.
The free tier lacks some enterprise features but covers all basic team
messaging needs.

## Features — 7/10

- **Messaging** — channels, threads, search, file sharing
- **Voice/Video** — no native support (requires plugin or third-party
  integration like Jitsi)
- **Playbooks** — incident response, checklists, workflows
- **Boards** — Kanban-style project management (Focalboard integration)
- **Plugins** — extensive plugin ecosystem, custom plugin development
- **Channels** — public, private, direct messages
- **Search** — full-text with filters, file content search

Missing native voice/video is a notable gap. For a remote coop, this means
separating real-time calls to another tool.

## Agent-Friendliness — 9/10

- **REST API** — comprehensive, well-documented, versioned
- **Webhooks** — incoming and outgoing webhooks
- **Slash commands** — custom slash command integration
- **Bot accounts** — first-class bot API with granular permissions
- **MCP** — official embedded and external MCP server
- **Plugins** — Go/JavaScript plugin system for deep integration
- **Open source** — full codebase available for customisation

Mattermost is arguably the most agent-friendly platform evaluated. The
combination of open source, comprehensive API, and official MCP support
makes it ideal for AI-driven workflows.

## Privacy — 9/10

- **Self-hosting** — full data ownership on your infrastructure
- **Encryption** — TLS in transit, E2EE available via plugin
- **Data control** — export tools, data retention policies, compliance
  exports
- **Audit logging** — comprehensive audit trails
- **Open source** — verifiable security, no closed-source components
- **GDPR** — full compliance feasible with self-hosting
- **Federation** — limited (not a core focus like Matrix)

For a small coop with privacy requirements, Mattermost is excellent — you
own the server, the data, and the keys.

## References

- [Mattermost MCP Server Docs](https://docs.mattermost.com/agents/mcpserver/README.html)
- [Mattermost Agents Admin Guide](https://docs.mattermost.com/administration-guide/configure/agents-admin-guide.html)
- [MCP Server Mattermost (community)](https://mcp-server-mattermost.readthedocs.io/)
- [Mattermost Pricing](https://mattermost.com/pricing/)

---
title: "Slack — Discussion Tool Analysis"
status: draft
author: ryanhz
date: 2026-06-06
tags:
  - slack
  - discussion
  - mcp
sources:
  - url: "https://docs.slack.dev/ai/slack-mcp-server"
    title: "Slack MCP Server — Official Developer Docs"
  - url: "https://slack.com/help/articles/48855576908307-Guide-to-the-Slack-MCP-server"
    title: "Slack MCP Server User Guide"
  - url: "https://github.com/slackapi/slack-mcp-plugin"
    title: "Slack MCP Plugin (GitHub)"
  - url: "https://slack.com/pricing"
    title: "Slack Pricing Plans"
last_audit_date: 2026-06-06
---

# Slack — Discussion Tool Analysis

## MCP Integration — 9/10

Slack has the strongest first-party MCP server of the SaaS platforms:

**Official Slack MCP Server (General Availability since Feb 2026):**
- Hosted at `https://mcp.slack.com/mcp`
- Streamable HTTP transport (JSON-RPC 2.0)
- OAuth 2.0 authentication (confidential clients)
- Tools: search messages/files/members/channels, read and send messages,
  manage canvases, access member profiles
- Available in partner clients: Claude.ai, Claude Code, Perplexity, Cursor
- Admin-approval workflow for workspace management
- Well-documented developer API with OAuth metadata endpoints

**Limitations:**
- Requires directory-published or internal Slack apps
- No Dynamic Client Registration (DCR)
- Admin approval required per workspace
- Currently no SSE support
- No self-hosted option — fully managed by Slack

## Hosting — 2/10

Slack is SaaS-only with no self-hosting option whatsoever.

- **No self-hosting** — entirely proprietary, cloud-only
- **Vendor lock-in** — migration tools exist but are limited
- **Uptime SLA** — available on Business+ and above
- **Data residency** — configurable region on Enterprise plans

For a 3-person team, the simplicity is appealing but the lack of control is
a significant risk for long-term operations.

## Cost — 5/10

| Plan | Price | Key Limits |
|---|---|---|
| Free | $0 | 90-day history, 10 integrations, 1:1 huddles only |
| Pro | $8.75/user/mo ($7.25 annual) | Unlimited history, full features |
| Business+ | $18/user/mo ($15 annual) | SAML, 24/7 support, compliance exports |
| Enterprise+ | Custom | HIPAA, EKM, advanced compliance |

For 3 users: Pro = $26.25/mo, Business+ = $54/mo. Expensive compared to
Discord (free) or self-hosted Mattermost (free). The Free plan's severe
limitations (90-day history, 10 integrations) make it impractical for a
coop with long-running projects.

## Features — 8/10

- **Threads** — mature threading, but less structured than Zulip
- **Search** — excellent full-text search with filters
- **File sharing** — unlimited file uploads on paid plans
- **Voice/Video** — Slack Huddles (group on paid, 1:1 on free), screen
  sharing, video clips
- **Canvases** — collaborative documents for project planning
- **Lists** — lightweight project tracking
- **Workflow Builder** — no-code automation, conditional branching (B+)
- **Integrations** — largest app directory of any platform
- **AI features** — conversation summaries, recaps, Slackbot agent

## Agent-Friendliness — 8/10

- **Slack API** — well-documented, mature, extensive SDKs
- **Webhooks** — inbound/outbound webhooks with simple setup
- **Bolt SDK** — modern framework for building Slack apps
- **Slackbot** — built-in AI agent with MCP access
- **MCP** — official server with OAuth, partner integrations
- **Rate limits** — reasonable but can be restrictive for heavy automation
- **Limitations** — MCP requires admin approval; some API features are
  Enterprise-only

## Privacy — 4/10

- **Data ownership** — data on Slack's infrastructure
- **Encryption** — TLS in transit and at rest
- **E2EE** — not available
- **Enterprise Key Management** — add-on (Enterprise only)
- **Data residency** — Enterprise only
- **Compliance** — HIPAA on Enterprise+
- **Third-party access** — privacy policy permits data use for platform
  operations

## References

- [Slack MCP Server Docs](https://docs.slack.dev/ai/slack-mcp-server)
- [Slack MCP Server Guide](https://slack.com/help/articles/48855576908307-Guide-to-the-Slack-MCP-server)
- [Slack MCP Plugin](https://github.com/slackapi/slack-mcp-plugin)
- [Slack Pricing](https://slack.com/pricing)

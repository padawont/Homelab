---
title: "Discord — Discussion Tool Analysis"
status: draft
author: ryanhz
date: 2026-06-06
tags:
  - discord
  - discussion
  - mcp
sources:
  - url: "https://github.com/goul4rt/mcp-discord"
    title: "@goul4rt/mcp-discord — 80+ tools, production-proven"
  - url: "https://github.com/jhm1909/discord-mcp"
    title: "cappylab/discord-mcp — 192 tools, OTel-instrumented"
  - url: "https://github.com/rayenking/discord-mcp"
    title: "@rayenking/discord-mcp — 94 tools"
  - url: "https://github.com/sushi-dev55/discord-mcp"
    title: "sushi-dev55/discord-mcp — Vencord plugin bridge, 26 tools"
  - url: "https://github.com/TaeRaeKim/discord-mcp"
    title: "@taeraekim/discord-mcp — 37 tools, discord.js v14"
  - url: "https://discord.com/nitro"
    title: "Discord Nitro Pricing"
  - url: "https://discord.com/blog/introducing-discord-nitro-basic"
    title: "Discord Nitro Basic Announcement"
last_audit_date: 2026-06-06
---

# Discord — Discussion Tool Analysis

## MCP Integration — 8/10

Discord has the most vibrant MCP server ecosystem of any platform evaluated.
Multiple mature, production-grade community servers exist:

| Server | Tools | Distinguishing Features |
|---|---|---|
| `@goul4rt/mcp-discord` | 80+ | Dual-mode (standalone or plugin), REST + Gateway, HTTP transport |
| `cappylab/discord-mcp` | 192 | OTel instrumentation, audit logging, migration adapters, v0.12.0 |
| `@rayenking/discord-mcp` | 94 | Full message data (attachments, embeds, stickers), no runtime setup |
| `@taeraekim/discord-mcp` | 37 | Docker support, discord.js v14 |
| `sushi-dev55/discord-mcp` | 26 | Vencord plugin bridge (user account, not bot) |

Strengths: Wide tool coverage (messages, moderation, channels, roles, voice
in some servers), multiple transport options (stdio, HTTP), active
maintenance. Weakness: No official Discord MCP server — all community
maintained. Some servers depend on desktop client plugins (Vencord) rather
than a standard bot API.

## Hosting — 3/10

Discord is SaaS-only with no meaningful self-hosting option. The entire
infrastructure is owned and operated by Discord Inc.

- **SaaS only** — no server software to deploy
- **Limited self-hosting** — only the client desktop/mobile apps
- **Vendor lock-in** — cannot migrate servers or data to another provider
- **Uptime** — depends entirely on Discord's infrastructure

For a 3-person team, this is simple (no ops burden) but provides zero
control over the platform's availability, roadmap, or policies.

## Cost — 9/10

| Tier | Price | Key Limits |
|---|---|---|
| Free | $0 | Full messaging, 25MB uploads, 2FA |
| Nitro Basic | $2.99/mo | Custom emoji anywhere, bigger uploads |
| Nitro | $9.99/mo ($99.99/yr) | HD video, 500MB uploads, more features |

For a 3-person coop, Discord Free is completely viable. Nitro is optional
and purely cosmetic/quality-of-life. No per-seat pricing — an exceptional
value at small scale.

## Features — 9/10

- **Voice/Video** — best-in-class, low latency, screen sharing, Go Live
- **Threads** — built-in threading for focused discussions
- **Search** — full-text search across messages and files
- **File sharing** — drag-and-drop, 25MB free / 500MB Nitro
- **Channels** — text, voice, stage, forum, announcements
- **Integrations** — wide webhook/bot ecosystem, many pre-built

No significant feature gaps for a small team. The main limitation is the
absence of native project management or wiki features.

## Agent-Friendliness — 7/10

- **Bot API** — well-documented, discord.js is mature
- **Webhooks** — simple inbound/outbound webhooks
- **Rate limits** — generous but can be restrictive
- **Gateway API** — real-time events via WebSocket
- **MCP** — no official server but rich community alternatives
- **Limitations** — bot accounts cannot join voice channels natively (no
  audio MCP tools); some operations need a user account (Vencord plugin
  approach)

## Privacy — 4/10

- **Data ownership** — Discord owns the platform; data lives on Discord's
  servers
- **Encryption** — TLS in transit; no E2EE
- **Data access** — Discord's privacy policy permits data usage for
  platform improvement
- **GDPR** — compliant but data resides on US servers (EU data centres also
  available)
- **Self-hosting** — impossible
- **Audit logging** — limited compared to enterprise platforms

Suitable for casual/community communication but not for sensitive internal
discussions requiring full data sovereignty.

## References

- [@goul4rt/mcp-discord](https://github.com/goul4rt/mcp-discord)
- [cappylab/discord-mcp](https://github.com/jhm1909/discord-mcp)
- [@rayenking/discord-mcp](https://github.com/rayenking/discord-mcp)
- [Discord Nitro](https://discord.com/nitro)

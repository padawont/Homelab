---
title: "Zulip — Discussion Tool Analysis"
status: draft
author: ryanhz
date: 2026-06-06
tags:
  - zulip
  - discussion
  - mcp
sources:
  - url: "https://github.com/prixite/zulip-mcp"
    title: "prixite/zulip-mcp — Stream/DM management, search"
  - url: "https://github.com/VanBarbascu/zulip-mcp"
    title: "VanBarbascu/zulip-mcp — SSE transport, notifications"
  - url: "https://github.com/lwsinclair/zulipchat-mcp"
    title: "lwsinclair/zulipchat-mcp — Docker, FastMCP, 8+ tools"
  - url: "https://github.com/windborne/zulipmcp"
    title: "windborne/zulipmcp — XML formatting, long-poll listener"
  - url: "https://pypi.org/project/zulipchat-mcp/0.7.1/"
    title: "zulipchat-mcp v0.7.1 — 20 core / 56 extended tools"
  - url: "https://zulip.com/plans/"
    title: "Zulip Plans and Pricing"
last_audit_date: 2026-06-06
---

# Zulip — Discussion Tool Analysis

## MCP Integration — 6/10

Zulip has a growing ecosystem of community-built MCP servers, but no
official server from the Zulip project itself:

| Server | Tools | Features |
|---|---|---|
| `prixite/zulip-mcp` | 15+ | Stream/DM messaging, search, reactions, resources |
| `zulipchat-mcp` (PyPI) | 20 core / 56 extended | Dual identity, search, approval workflows |
| `VanBarbascu/zulip-mcp` | 9 | SSE transport, notification bot |
| `windborne/zulipmcp` | 8+ | XML formatting for LLMs, real-time listener |
| `lwsinclair/zulipchat-mcp` | 8+ | Docker, FastMCP, daily summaries |

Strengths: Multiple server options covering messaging, search, reactions,
stream management, and extended features like dual-identity and approval
workflows. Some servers (zulipchat-mcp) are actively maintained with large
tool surfaces.

Weakness: No official Zulip MCP server. Community servers may have varying
maintenance quality. Documentation quality varies between projects.

## Hosting — 8/10

| Mode | Description |
|---|---|
| Zulip Cloud (Free) | Hosted by Zulip, 10K message history, 5GB storage |
| Zulip Cloud (Standard) | Hosted, $8/user/mo, unlimited history, 5GB/user storage |
| Self-hosted (Free) | Full open source, all features, 10-user push notification limit |
| Self-hosted (Basic) | $3.50/user/mo, unlimited push notifications |
| Self-hosted (Business) | $8/user/mo, commercial support, 25-user minimum |

Self-hosting is straightforward with Docker. Requires a Linux server with
PostgreSQL and RabbitMQ. Well-documented installation process.

## Cost — 9/10

| Plan | Price (3 users) | Notes |
|---|---|---|
| Cloud Free | $0 | 10K message search history limit |
| Cloud Standard | $24/mo | Unlimited everything |
| Self-hosted Free | $0 | All features, push for up to 10 users |
| Self-hosted Basic | $10.50/mo | Push notifications unlimited |

For a 3-person coop, self-hosted Free is excellent — you get the full
feature set with no cost. Cloud Free is also viable if the 10K message
search limit is acceptable. Discounted/non-profit pricing available.

## Features — 8/10

- **Threading** — best-in-class topic-based threading model (unique
  differentiator)
- **Search** — powerful full-text search with filters
- **File sharing** — 5GB total (cloud free) or 5GB/user (cloud paid)
- **Voice/Video** — no native support (third-party integration needed)
- **Integrations** — hundreds of pre-built integrations (webhooks, bots)
- **Streams** — public/private channels with fine-grained permissions
- **Topics** — every message belongs to a topic, enabling structured
  asynchronous conversations
- **Mobile** — excellent mobile apps with push notifications

Topic-based threading is Zulip's killer feature for async work. It makes
long-running project discussions far more navigable than linear chat.

## Agent-Friendliness — 8/10

- **REST API** — well-documented, consistent, versioned
- **Webhooks** — incoming webhooks for integrations
- **Bots** — bot API with fine-grained permissions
- **Real-time API** — long-polling event system
- **MCP** — multiple community servers with broad tool coverage
- **Open source** — full Python codebase, customisable
- **API bindings** — official Python library, community bindings for other
  languages

## Privacy — 8/10

- **Self-hosting** — full data ownership on your infrastructure
- **Encryption** — TLS in transit, no E2EE
- **Data exports** — high-quality export/import tools (full fidelity)
- **Open source** — 100% open source, verifiable (Apache 2.0)
- **GDPR** — full compliance feasible with self-hosting
- **Authentication** — SAML, LDAP, Google OAuth, GitHub OAuth

## References

- [prixite/zulip-mcp](https://github.com/prixite/zulip-mcp)
- [zulipchat-mcp (PyPI)](https://pypi.org/project/zulipchat-mcp/0.7.1/)
- [Zulip Pricing](https://zulip.com/plans/)
- [Zulip Self-hosting Guide](https://zulip.com/help/self-hosted-billing)

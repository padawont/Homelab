# ADR-0004: Discussion Tools

## README.md

# ADR 0004: Discussion Tools

Selects Discord (Free plan) as the primary team discussion platform for RunicEngines, a 3-person cooperative, based on a structured evaluation of five platforms across six weighted criteria.

See [overview.md](./overview.md) for the full decision record.

## overview.md

---
adr: 0004
title: "Select Discord as Team Discussion Platform"
author: padawont
status: final
topic: collaboration
date: 2026-06-14
date-proposed: 2026-06-14
history: "https://github.com/RunicEngines/knowledge-base/pull/76"
context: >
  RunicEngines, a 3-person cooperative, requires a real-time discussion
  platform with MCP integration for AI agent workflows, threaded chat,
  file sharing, and minimal hosting overhead. Five platforms were
  researched and scored across six criteria: MCP integration, hosting
  model, cost, features, agent-friendliness, and privacy.
decision: >
  Adopt Discord (Free plan) as the primary team discussion platform for
  RunicEngines. Discord provides the best overall value — free for a
  3-person team with no feature restrictions, a mature community MCP
  ecosystem (192 tools via cappylab/discord-mcp), best-in-class
  voice/video and file sharing, and zero operational overhead as a
  SaaS-only platform.
consequences: >
  Positive: free for indefinite use at current team size; zero ops
  burden; best all-in-one communication features (chat, threads,
  voice/video, screen sharing, file sharing); mature MCP ecosystem
  sufficient for agent workflows; scales without effort. Negative: no
  self-hosting or data sovereignty; privacy depends on Discord's
  policies; MCP servers are community-maintained (no official Discord
  MCP server).
sources:
  - "../knowledge/technology/discussion-tools/discord/overview.md"
  - "../knowledge/technology/discussion-tools/mattermost/overview.md"
  - "../knowledge/technology/discussion-tools/slack/overview.md"
  - "../knowledge/technology/discussion-tools/zulip/overview.md"
  - "../knowledge/technology/discussion-tools/matrix-element/overview.md"
  - "../knowledge/technology/discussion-tools/overview.md"
  - "../research/discussion-tools-mcp/overview.md"
references:
  - "https://github.com/goul4rt/mcp-discord"
  - "https://github.com/jhm1909/discord-mcp"
  - "https://github.com/rayenking/discord-mcp"
  - "https://docs.mattermost.com/agents/mcpserver/README.html"
  - "https://docs.slack.dev/ai/slack-mcp-server"
  - "https://github.com/prixite/zulip-mcp"
  - "https://github.com/rosquillas/element-mcp-server"
---

# ADR 0004: Select Discord as Team Discussion Platform

## Status

Final (2026-06-14)

## Context and Problem Statement

RunicEngines is a distributed 3-person cooperative that needs a
real-time team discussion platform. The platform must support:

- **MCP integration** — AI agents need to interact with the discussion
  platform for automated workflows (message sending, channel monitoring,
  role management).
- **Text communication** — threaded chat with search and file sharing.
- **Voice/video communication** (nice-to-have) — synchronous
  collaboration for a distributed team.
- **Low cost** — the team is small with minimal budget.
- **Minimal operational overhead** — no dedicated infrastructure team.

Five platforms were evaluated in a structured research pipeline (Idea
#46 — `ideas/organisation/tools/discussion-tools-mcp-comparison/`,
Knowledge #43 — `knowledge/technology/discussion-tools/`, Research #44
— `research/discussion-tools-mcp/`) across six weighted criteria: MCP
integration, hosting flexibility, cost, features (chat, threads,
voice/video, file sharing), agent-friendliness (API surface, webhooks,
bots), and privacy/sovereignty.

## Decision

RunicEngines **will adopt Discord (Free plan)** as the primary team
discussion platform.

This decision is informed by the research analysis in
`research/discussion-tools-mcp/overview.md`, which synthesises detailed
knowledge notes for each platform.

### Why Discord

| Factor | Detail |
|---|---|
| **Cost** | Free for unlimited users with all core features. No paid tier needed at current or foreseeable team size. |
| **Features** | Best-in-class chat, threads, voice/video, screen sharing, and drag-and-drop file sharing in a single product. |
| **MCP Integration** | Multiple production-grade community MCP servers: cappylab/discord-mcp (192 tools, OTel-instrumented), @goul4rt/mcp-discord (80+ tools), and others. Sufficient for all agent workflow needs. |
| **Operations** | SaaS-only — zero infrastructure to manage, no server updates, no monitoring. |
| **Scalability** | The free plan accommodates growth without additional cost or configuration. |

## Consequences

### Positive

- **$0 cost** — Free plan with no feature restrictions at the current
  team size.
- **Zero operational burden** — No server provisioning, maintenance, or
  monitoring.
- **Best communication experience** — Voice/video, screen sharing, file
  sharing, and threaded chat in a single, polished interface.
- **Mature MCP ecosystem** — 192+ tools available through
  community-maintained MCP servers, covering the full Discord API.
- **Scales naturally** — Adding team members costs nothing on the Free
  plan.

### Negative

- **No self-hosting** — All data resides on Discord's infrastructure
  with no on-premises option.
- **Privacy constraints** — Data sovereignty depends entirely on
  Discord's privacy policy and terms of service.
- **Community MCP** — Unlike Mattermost and Slack, Discord has no
  official MCP server. Reliance on third-party community projects
  introduces a maintenance and trust risk.
- **SaaS dependency** — Service availability, feature changes, and
  pricing terms are controlled by Discord.

### Accepted Trade-offs

- **Data sovereignty** is acceptable for a 3-person cooperative that
  does not handle sensitive data or operate under compliance
  requirements.
- **Community MCP servers** are production-proven (cappylab has OTel
  instrumentation, 192 tools, and migration adapters for other major
  Discord MCP servers) and have a lower bus-factor risk than commercial
  alternatives.

## Considered Options

### Discord (chosen)

- **MCP**: 8/10 — 5+ community servers, 192 tools (cappylab), production-proven
- **Hosting**: 3/10 — SaaS only
- **Cost**: 9/10 — Free for unlimited users
- **Features**: 9/10 — Best-in-class voice/video, threads, file sharing
- **Agent-Friendly**: 7/10 — Mature bot API, discord.js, webhooks
- **Privacy**: 4/10 — No self-hosting, data on Discord infra
- **Verdict**: Best overall value for a small team; the feature and
  cost advantages outweigh the privacy trade-off.

### Mattermost

- **MCP**: 9/10 — Strongest first-party support (official server, embedded,
  external HTTP, OAuth)
- **Hosting**: 9/10 — Full self-hosting, MIT-licensed
- **Cost**: 7/10 — Free Team Edition, but 11-user minimum on paid tiers
- **Features**: 7/10 — No native voice/video
- **Agent-Friendly**: 9/10 — Excellent API, webhooks, bot framework
- **Privacy**: 9/10 — Full data control
- **Verdict**: Rejected due to missing native voice/video and
  uneconomical paid tier pricing for a 3-person team. Best alternative
  if self-hosting becomes a requirement in the future.

### Slack

- **MCP**: 9/10 — Official GA server since February 2026
- **Hosting**: 2/10 — SaaS only
- **Cost**: 5/10 — $8.75/user/month Pro ($26.25/mo for 3 users); 90-day
  history limit on Free plan
- **Features**: 8/10 — Strong chat, threads, search, file sharing; no
  native voice/video in free tier
- **Agent-Friendly**: 8/10 — Official API, SDKs, extensive
  documentation
- **Privacy**: 4/10 — SaaS only, data on Slack infra
- **Verdict**: Rejected — expensive for a small team, 90-day message
  history limit on Free makes it unusable long-term, and voice/video
  requires paid tier or third-party integration.

### Zulip

- **MCP**: 6/10 — Community servers only, no official support
- **Hosting**: 8/10 — Self-hosted or cloud
- **Cost**: 9/10 — Free self-hosted
- **Features**: 8/10 — Best threading model (topic-based); no native
  voice/video
- **Agent-Friendly**: 8/10 — Well-documented API, webhooks, bots
- **Privacy**: 8/10 — Self-hosting option, data control
- **Verdict**: Rejected — no official MCP server, no native
  voice/video, and the absence of an official MCP server adds
  uncertainty for agent-driven workflows.

### Matrix/Element

- **MCP**: 5/10 — Immature ecosystem, small community servers
- **Hosting**: 10/10 — Most flexible (Synapse, Dendrite, Conduit)
- **Cost**: 8/10 — Free self-hosted
- **Features**: 7/10 — E2EE, federation, bridges; voice/video via
  Element Call
- **Agent-Friendly**: 6/10 — Complex API, fewer client libraries
- **Privacy**: 10/10 — E2EE, federation, air-gap capable
- **Verdict**: Rejected — immature MCP ecosystem and highest
  operational complexity make it unsuitable for a small team without
  infrastructure experience.

## Compliance

No compliance enforcement mechanism is required at this time. This ADR
is informational — team members are encouraged to use Discord for
team communication. If a platform change becomes necessary in the
future (e.g., due to privacy requirements or team growth), a new ADR
should be proposed.
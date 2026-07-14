---
title: "Discussion Tools with MCP Integration — Research Analysis"
status: draft
author: ryanhz
date: 2026-06-06
tags:
  - discussion
  - mcp
  - research
  - discord
sources:
  - knowledge: "knowledge/technology/discussion-tools/discord/overview"
  - knowledge: "knowledge/technology/discussion-tools/mattermost/overview"
  - knowledge: "knowledge/technology/discussion-tools/slack/overview"
  - knowledge: "knowledge/technology/discussion-tools/zulip/overview"
  - knowledge: "knowledge/technology/discussion-tools/matrix-element/overview"
  - knowledge: "knowledge/technology/discussion-tools/overview"
references:
  - url: "https://github.com/goul4rt/mcp-discord"
    title: "@goul4rt/mcp-discord — 80+ tools, production-proven"
  - url: "https://github.com/jhm1909/discord-mcp"
    title: "cappylab/discord-mcp — 192 tools, OTel-instrumented"
  - url: "https://github.com/rayenking/discord-mcp"
    title: "@rayenking/discord-mcp — 94 tools"
  - url: "https://docs.mattermost.com/agents/mcpserver/README.html"
    title: "Mattermost MCP Server Documentation"
  - url: "https://docs.slack.dev/ai/slack-mcp-server"
    title: "Slack MCP Server Documentation"
  - url: "https://github.com/prixite/zulip-mcp"
    title: "prixite/zulip-mcp — Zulip MCP Server"
  - url: "https://github.com/rosquillas/element-mcp-server"
    title: "Element MCP Server"
last_audit_date: 2026-06-06
---

# Discussion Tools with MCP Integration — Research Analysis

## Context

RunicEngines is a 3-person cooperative evaluating a team discussion
platform. The primary driver is MCP (Model Context Protocol) integration
for AI agent workflows. Secondary needs include threaded conversations,
chat, file sharing, low cost, and minimal operational overhead. Voice/video
is not required and there are no near-term growth concerns.

This research synthesises the knowledge notes produced in stage 2 to
produce a recommendation for ADR 0004: Discussion Tools.

**Pipeline:**
- Idea: `ideas/organisation/tools/discussion-tools-mcp-comparison/` (#46)
- Knowledge: `knowledge/technology/discussion-tools/` (#43)

## Findings

### Score Comparison

| Criteria | Discord | Mattermost | Slack | Zulip | Matrix/Element |
|---|---|---|---|---|---|
| MCP Integration | 8 | 9 | 9 | 6 | 5 |
| Hosting | 3 | 9 | 2 | 8 | 10 |
| Cost | 9 | 7 | 5 | 9 | 8 |
| Features | 9 | 7 | 8 | 8 | 7 |
| Agent-Friendliness | 7 | 9 | 8 | 8 | 6 |
| Privacy | 4 | 9 | 4 | 8 | 10 |

### Platform Summaries

**Discord** — Best feature set (chat, threads, voice/video, file sharing).
Free for small teams. 5+ production-grade community MCP servers: cappylab
(192 tools), @goul4rt (80+ tools), @rayenking (94 tools), and others.
SaaS-only with zero operational overhead.

**Mattermost** — Strongest first-party MCP support (official server,
embedded in platform, external HTTP endpoint, OAuth). Full self-hosting,
MIT-licensed. No native voice/video. 11-user minimum for paid tiers makes
it uneconomical for a 3-person team.

**Slack** — Official MCP server (GA since February 2026), well-documented,
OAuth-based. Expensive at scale ($8.75/user/month Pro). SaaS-only.
90-day history limit on free tier makes it impractical.

**Zulip** — Best threading model (topic-based). Solid self-hosting and
pricing (free self-hosted). Only community MCP servers — no official
support. No native voice/video.

**Matrix/Element** — Best privacy/sovereignty (E2EE, federation,
self-hosting, air-gap capable). Immature MCP ecosystem with small,
community servers. Highest operational complexity.

## Analysis

### Decision Factors

**1. MCP Integration**
Discord scores 8/10. While Mattermost (9) and Slack (9) have official
MCP servers, Discord's community ecosystem is mature with multiple
production-proven alternatives. `cappylab/discord-mcp` (192 tools) and
`@goul4rt/mcp-discord` (80+ tools) cover the full Discord API surface
including messages, channels, moderation, roles, and monitoring. This
is sufficient for RunicEngines' agent workflows.

**2. Features**
Discord leads on all communication features: threads, channels,
full-text search, drag-and-drop file sharing, voice/video, and screen
sharing. Best all-in-one communication experience.

**3. Cost**
Discord Free is $0 with no practical limits for a 3-person team. No
other platform offers this combination of features at no cost.

**4. Hosting**
SaaS-only means zero operational burden. For a small coop with no
dedicated infrastructure team, this is a significant advantage.

**5. Agent-Friendliness**
Discord's bot API is mature and well-documented (discord.js). MCP
servers bridge directly to Discord's full API. Webhooks are
straightforward.

**6. Privacy**
Discord's weakest category. Data stays on Discord's infrastructure with
no self-hosting option. For a small coop without sensitive compliance
requirements, this trade-off is acceptable.

### Trade-off Summary

| For Discord | Against Discord |
|---|---|
| Best features, free cost, zero ops | No self-hosting or data sovereignty |
| Mature MCP ecosystem (192 tools) | Community-maintained (not official) |
| Scales without cost or effort | Privacy depends on Discord's policies |

## Recommendations

**Adopt Discord as the primary team discussion platform for RunicEngines.**

Rationale:
- Best all-in-one communication (chat, threads, voice/video, file sharing)
- Free for a 3-person team with no feature limitations
- Production-grade MCP ecosystem sufficient for agent workflows
- Zero operational overhead
- Scales without additional cost or effort

Trade-off accepted: data sovereignty. For a 3-person cooperative without
sensitive data or compliance requirements, Discord's SaaS model is
acceptable.

This recommendation feeds directly into ADR 0004: Discussion Tools.

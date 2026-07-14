---
title: "Ecosystem Plugins"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - ecosystem
  - plugins
sources:
  - url: "https://opencode.ai/docs/ecosystem"
    title: "OpenCode Ecosystem Documentation"
  - url: "https://github.com/topics/opencode-plugin"
    title: "OpenCode Plugin Topic on GitHub"
  - url: "https://opencode.cafe"
    title: "opencode.cafe Community"
  - url: "https://github.com/awesome-opencode/awesome-opencode"
    title: "Awesome OpenCode"
last_audit_date: 2026-06-07
---

# Ecosystem Plugins

Plugins hook into the OpenCode lifecycle — tool execution, model interaction, session management, and file operations. They are installed via the `opencode plugin` CLI and configured in `opencode.json`.

### Auth & API Billing

| Name | Description | Repository |
|---|---|---|
| opencode-openai-codex-auth | Use ChatGPT Plus/Pro subscription instead of API credits | `opencode-openai-codex-auth` |
| opencode-gemini-auth | Use existing Gemini plan instead of API billing | `opencode-gemini-auth` |
| opencode-antigravity-auth | Use Antigravity's free models instead of API billing | `opencode-antigravity-auth` |
| opencode-google-antigravity-auth | Google Antigravity OAuth Plugin | `opencode-google-antigravity-auth` |

### Sandbox & Environment

| Name | Description | Repository |
|---|---|---|
| opencode-daytona | Auto-run OpenCode sessions in isolated Daytona sandboxes with git sync and live previews | `opencode-daytona` |
| opencode-devcontainers | Multi-branch devcontainer isolation | `opencode-devcontainers` |

### Code Editing & Injection

| Name | Description | Repository |
|---|---|---|
| opencode-type-inject | Auto-inject TypeScript/Svelte types into file reads | `opencode-type-inject` |
| opencode-morph-fast-apply | 10x faster code editing with Morph Fast Apply API | `opencode-morph-fast-apply` |
| opencode-morph-plugin | Fast Apply editing, WarpGrep, context compaction via Morph | `opencode-morph-plugin` |

### Context & Memory

| Name | Description | Repository |
|---|---|---|
| opencode-dynamic-context-pruning | Optimize token usage by pruning obsolete tool outputs | `opencode-dynamic-context-pruning` |
| opencode-supermemory | Persistent memory across sessions | `opencode-supermemory` |
| opencode-skillful | Lazy load prompts with skill discovery and injection | `opencode-skillful` |

### Security & Privacy

| Name | Description | Repository |
|---|---|---|
| opencode-vibeguard | Redact secrets/PII into placeholders before LLM calls | `opencode-vibeguard` |

### Shell & Terminal

| Name | Description | Repository |
|---|---|---|
| opencode-pty | Run background processes in PTY, send interactive input | `opencode-pty` |
| opencode-shell-strategy | Instructions for non-interactive shell commands | `opencode-shell-strategy` |
| opencode-zellij-namer | AI-powered Zellij session naming | `opencode-zellij-namer` |

### Web & Search

| Name | Description | Repository |
|---|---|---|
| opencode-websearch-cited | Native websearch support | `opencode-websearch-cited` |
| opencode-firecrawl | Web scraping, crawling, and search via Firecrawl CLI | `opencode-firecrawl` |

### Notifications

| Name | Description | Repository |
|---|---|---|
| opencode-notificator | Desktop notifications and sound alerts | `opencode-notificator` |
| opencode-notifier | Desktop notifications for permission, completion, error events | `opencode-notifier` |
| opencode-notify | Native OS notifications | `opencode-notify` |

### Workflow & Orchestration

| Name | Description | Repository |
|---|---|---|
| @plannotator/opencode | Interactive plan review with visual annotation | `@plannotator/opencode` |
| @openspoon/subtask2 | Extend /commands into orchestration system | `@openspoon/subtask2` |
| opencode-scheduler | Schedule recurring jobs via launchd/systemd | `opencode-scheduler` |
| opencode-conductor | Protocol-Driven Workflow (Context -> Spec -> Plan -> Implement) | `opencode-conductor` |
| micode | Structured Brainstorm -> Plan -> Implement workflow | `micode` |
| octto | Interactive browser UI for AI brainstorming | `octto` |
| opencode-background-agents | Background agents with async delegation | `opencode-background-agents` |
| opencode-workspace | Bundled multi-agent orchestration (16 components) | `opencode-workspace` |
| opencode-worktree | Zero-friction git worktrees | `opencode-worktree` |
| opencode-goal-plugin | Session-scoped /goal workflow | `opencode-goal-plugin` |

### Monitoring & Tracking

| Name | Description | Repository |
|---|---|---|
| opencode-helicone-session | Auto-inject Helicone session headers for request grouping | `opencode-helicone-session` |
| opencode-wakatime | Track OpenCode usage with Wakatime | `opencode-wakatime` |
| opencode-sentry-monitor | Trace/debug AI agents with Sentry AI Monitoring | `opencode-sentry-monitor` |

### Formatting & Utilities

| Name | Description | Repository |
|---|---|---|
| opencode-md-table-formatter | Clean up markdown tables from LLMs | `opencode-md-table-formatter` |

### Bundled Plugin Suites

| Name | Description | Repository |
|---|---|---|
| oh-my-opencode | Background agents, pre-built LSP/AST/MCP tools, curated agents | `oh-my-opencode` |

### Integrations

| Name | Description | Repository |
|---|---|---|
| opencode-jfrog-plugin | JFrog integration | `opencode-jfrog-plugin` |

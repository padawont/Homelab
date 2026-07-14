---
title: "OpenCode Plugins"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - architecture
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# OpenCode Plugins

OpenCode's plugin system allows extending functionality through JavaScript/TypeScript modules and npm packages. This directory contains atomic reference notes covering architecture, creation, distribution, events, and bundling patterns.

## Architecture & Creation

- [Architecture](architecture.md) — Local vs npm plugins, installation mechanics, publishing overview
- [Loading](loading.md) — Load order (global → project → local) and deduplication rules
- [Creation](creation.md) — Basic plugin structure, TypeScript support, dependencies, configuration patterns
- [Examples](examples.md) — Complete code examples: notifications, .env protection, environment injection, custom tools, logging, compaction hooks

## Distribution

- [npm Packaging](npm-packaging.md) — Package naming, `@opencode-ai/plugin` dependency, package.json conventions, Bun auto-install, caching
- [Private Distribution](private-distribution.md) — GitHub npm registry, .npmrc, authentication tokens, consumer configuration
- [Versioning](versioning.md) — SemVer strategy, changelog conventions, breaking change migration
- [Publishing Workflow](publishing-workflow.md) — Manual publishing, version bumps, CI/CD via GitHub Actions, GitHub Release integration

## Bundle Components

- [Bundling Components](bundling-components.md) — Bundling agents, skills, and custom tools in a single npm plugin; directory layout; auto-discovery boundary; registration mechanisms; RunicEngines use case

## Event Reference

- [Command Events](event-command.md) — `command.execute.before`
- [Chat Events](event-chat.md) — `chat.message`, `chat.params`, `chat.headers`
- [Permission Events](event-permission.md) — `permission.ask`
- [Shell Events](event-shell.md) — `shell.env`
- [Tool Events](event-tool.md) — `tool.execute.before`, `tool.execute.after`, `tool.definition`
- [Session Events](event-session.md) — All 8 session SSE events
- [File Events](event-file.md) — `file.edited`, `file.watcher.updated`
- [System Events](event-system.md) — Installation, LSP, Message, Server, Todo SSE events
- [TUI Events](event-tui.md) — `tui.prompt.append`, `tui.command.execute`, `tui.toast.show`
- [Compaction Hooks](event-compaction.md) — All 6 experimental hooks
- [Handler Patterns](event-patterns.md) — Named handlers vs wildcard event handler

## See Also

- [Custom Tools](../custom-tools/) — Plugins can define custom tools via the `tool()` helper
- [SDK](../sdk/) — The OpenCode SDK client available to plugins
- [Ecosystem](../ecosystem/) — Community-contributed plugins catalogue
- [MCP Servers](../mcp/) — Model Context Protocol extensibility (adjacent to plugins)
- [Agents](../agents/) — Plugins can define and load agents
- [Skills](../skills/) — Agent skill loading and discovery

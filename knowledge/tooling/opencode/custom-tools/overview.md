---
title: "OpenCode Custom Tools"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - tools
  - configuration
sources:
  - url: "https://opencode.ai/docs/custom-tools"
    title: "OpenCode Custom Tools Documentation"
  - url: "https://opencode.ai/docs/mcp-servers"
    title: "OpenCode MCP Servers Documentation"
last_audit_date: 2026-06-07
---

# OpenCode Custom Tools

Custom tools extend the LLM's built-in capabilities with user-defined TypeScript/JavaScript functions. They are auto-discovered from `.opencode/tools/` (project) and `~/.config/opencode/tools/` (global), and defined using the `tool()` helper from `@opencode-ai/plugin`.

## Atomic Notes

- **[definition.md](definition.md)** — What custom tools are, where they live, and how to define them with the `tool()` helper, including the `description`, `args`, and `execute` fields.
- **[arguments.md](arguments.md)** — Zod argument schemas: supported types (string, number, boolean, enum, array, object), modifiers (`.optional()`, `.default()`, `.describe()`), and examples.
- **[execution-context.md](execution-context.md)** — The `context` object passed to `execute`: agent, sessionID, messageID, directory, and worktree properties.
- **[advanced.md](advanced.md)** — Multiple tools per file via named exports, name collision precedence (custom over built-in), and cross-language execution via `Bun.$`.
- **[permissions.md](permissions.md)** — Glob-based permission rules, exact/prefix/suffix matching, and comparison between MCP tool permissions and custom tool permissions.

## Related Topics

- **[Plugins](../plugins/)** — Plugins can also register custom tools via the same `tool()` helper. Use plugin-level tools for tools bundled with installable plugins; use standalone custom tools for project-local or global per-user tools.
- **[MCP Servers](../mcp/)** — MCP servers provide external tools from subprocesses or remote HTTP endpoints. Custom tools run locally as TypeScript/JavaScript.
- **[Agents](../agents/)** — Agents are the runtime entities that invoke tools. Custom tools are available to all agents unless restricted via permissions.
- **[Skills](../skills/)** — Skills can instruct agents to use custom tools, extending skill capabilities beyond built-in tooling.
- **[SDK](../sdk/)** — The SDK provides programmatic access to OpenCode sessions and configuration, complementary to custom tool development.

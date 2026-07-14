---
title: "Agent Discovery"
status: draft
author: "Khalid"
date: 2026-05-31
tags:
  - opencode
  - agents
  - discovery
sources:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/config"
    title: "OpenCode Config Documentation"
last_audit_date: 2026-05-31
---

## Agent Definition Locations

| Location | Scope | Mechanism |
|---|---|---|
| `.opencode/agents/<name>.md` | Project-local | Auto-discovered (file scan) |
| `~/.config/opencode/agents/<name>.md` | Global/user | Auto-discovered (file scan) |
| `opencode.json` `"agent"` key | Any | Explicit registration |
| `OPENCODE_CONFIG_DIR` custom path | Runtime | Scanned like `.opencode/` |

Backward compatibility: `agent/` (singular) is also supported alongside `agents/` (plural).

## Auto-Discovery Mechanism

OpenCode scans `.opencode/agents/` and `~/.config/opencode/agents/` for `.md` files. Each `.md` file directly in the `agents/` directory becomes an agent — the file name (without `.md`) is the agent name. Only `.md` files are recognized.

Project-level discovery walks up from the current working directory (CWD) to the nearest Git worktree root. Global agents under `~/.config/opencode/agents/` are always available.

## Explicit Registration

Agents can be defined in `opencode.json` under the `"agent"` key:
```json
{
  "agent": {
    "agent-name": {
      "description": "...",
      "mode": "subagent"
    }
  }
}
```

## Coexistence & Precedence

Config sources are merged across tiers (remote → global → OPENCODE_CONFIG (custom config file) → project → .opencode dirs → OPENCODE_CONFIG_DIR (custom directory) → inline → managed → macOS managed). Later tiers override earlier ones for conflicting keys; non-conflicting keys from all tiers are preserved.

> **Note:** `OPENCODE_CONFIG_DIR`'s position after `.opencode dirs` is documented — the docs state it "is loaded after the global config and `.opencode` directories". Its tier position relative to `inline` is not explicitly stated and is inferred from that ordering.

If the same agent name appears in both `opencode.json` and a `.md` file, the `.md` file (loaded from `.opencode/ dirs`) wins for project and lower tiers. Higher tiers (inline, managed, macOS managed) can override both. Avoid name collisions across definition formats.

## Naming Convention

File name (without `.md`) becomes the agent name. The convention follows lowercase alphanumeric characters separated by single hyphens — matching built-in names: `build`, `plan`, `general`, `explore`, `scout`, `compaction`, `title`, `summary`. Spaces or uppercase in filenames are atypical.

## See Also

- [configuration](configuration.md)
- [context-loading](context-loading.md)



---
title: "Context Loading"
status: draft
author: "Khalid"
date: 2026-05-31
tags:
  - opencode
  - agents
  - context
  - configuration
sources:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/config"
    title: "OpenCode Config Documentation"
  - url: "https://opencode.ai/docs/rules"
    title: "OpenCode Rules Documentation"
last_audit_date: 2026-05-31
---

## Overview

How AGENTS.md files and instruction files are consumed by OpenCode agents. Two main mechanisms: the global `instructions` field and per-agent `prompt` overrides.

## The `instructions` Field

Configured in `opencode.json` as an array of paths, globs, or URLs:

```json
{
  "instructions": ["AGENTS.md", ".opencode/rules/*.md"]
}
```

- Paths are relative to the config file directory
- Supports glob patterns (e.g. `".opencode/rules/*.md"`)
- Remote URLs supported (5s timeout)
- All resolved files merge into every agent's context
- Supplements, does not replace, auto-discovered AGENTS.md files

## Per-Agent `prompt` Field

Agent-specific system prompt override:

```json
{
  "agent": {
    "build": {
      "prompt": "{file:./prompts/build.txt}"
    }
  }
}
```

- Can be inline string or `{file:./path}` reference
- Path relative to config file directory
- **Difference from `instructions`**: `instructions` is global for all agents; `prompt` is per-agent and replaces the agent's default system prompt

## Auto-Discovery & Merging

OpenCode automatically finds AGENTS.md files by traversing up from CWD. Also loads `~/.config/opencode/AGENTS.md` globally. Falls back to `CLAUDE.md` if no AGENTS.md found. All sources merge together — no override.

## Variable Substitution

- `{env:VAR_NAME}` — substitutes environment variable value (empty string if unset)
- `{file:path}` — substitutes file contents. Path relative to config file, or absolute (`/`), or home-relative (`~`)
- Works in config values: prompts, API keys, model names, etc.

## The `{file:path}` Pattern

Used for:
- Agent prompts: `"prompt": "{file:./prompts/build.txt}"`
- API keys: `"apiKey": "{file:~/.secrets/openai-key}"`
- Generic config values

Path resolution is always relative to the config file containing the reference, unless absolute or home-relative.

## Lazy Loading Pattern (This Repo)

The repo's `opencode.json`:

```json
{
  "instructions": ["AGENTS.md"]
}
```

Root `AGENTS.md` is deliberately minimal — directory structure, naming, content pipeline, statuses, cross-linking. It instructs agents to load section-specific AGENTS.md files on demand via the Read tool:

- `@templates/AGENTS.md`
- `@ideas/AGENTS.md`
- `@knowledge/AGENTS.md`
- etc.

Critical directive: **"Do NOT preemptively load all references — load them on a need-to-know basis."** This avoids context bloat.

## Best Practices

- Keep root AGENTS.md concise
- Use glob patterns for monorepo instruction files
- Teach agents to load section-specific rules on demand
- Prefer lazy loading over bundling all instructions upfront

## See Also

- [configuration](configuration.md)
- [discovery](discovery.md)

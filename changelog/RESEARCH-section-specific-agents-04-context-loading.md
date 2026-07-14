---
title: "Context Loading: How Agents Consume AGENTS.md"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - agents
  - context
  - configuration
sources:
  - knowledge: "knowledge/tooling/opencode/agents/context-loading"
  - knowledge: "knowledge/tooling/opencode/agents/agent-configuration"
references:
  - url: "https://opencode.ai/docs/config"
    title: "OpenCode Config Documentation"
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/rules"
    title: "OpenCode Rules Documentation"
last_audit_date: 2026-05-31
---

# Context Loading: How Agents Consume AGENTS.md

## 1. How `instructions` Works

- Global array in `opencode.json`: `"instructions": ["AGENTS.md"]`
- Paths/globs are relative to the config file directory
- Merges into ALL agents' contexts — both primary agents and subagents
- Supplements auto-discovered AGENTS.md files (does not replace them)

## 2. How `prompt` Works

- Per-agent override defined in agent frontmatter or `opencode.json`
- Supports inline text or `{file:./path}` syntax for loading from an external file
- Key difference from `instructions`: `instructions` is global and additive; `prompt` replaces the agent's system prompt entirely

## 3. Current Repo Setup

- `opencode.json`: `"instructions": ["AGENTS.md"]` only
- Root AGENTS.md is always in context for ALL agents
- Section AGENTS.md files are NOT listed in `instructions` — they are lazy-loaded

## 4. The Lazy Loading Pattern

- Root AGENTS.md lists section files as `@path` references
- Directs agents: "Do NOT preemptively load all references — load them on a need-to-know basis when relevant to the current task."
- This is the foundation that section-specific agents build on

## 5. Three-Layer Loading Architecture

```
Session Start
    │
    ▼
┌───────────────────────────────────────┐
│ Layer 1: Root AGENTS.md               │ ← injected via instructions
│   - Repo structure, pipeline, statuses │
│   - Lazy loading directive             │
└───────────────────────────────────────┘
    │
    ▼ (agent encounters section task)
    │
┌───────────────────────────────────────┐
│ Layer 2: Section AGENTS.md            │ ← Read tool at invocation
│   - Section-specific rules            │
│   - Categorization, frontmatter       │
└───────────────────────────────────────┘
    │
    ▼ (agent needs specialized logic)
    │
┌───────────────────────────────────────┐
│ Layer 3: Skills / Knowledge Notes     │ ← skill() or Read on demand
│   - Reusable skill modules            │
│   - External references               │
└───────────────────────────────────────┘
```

## 6. How Subagents Inherit Context

- Subagents get Layer 1 (root AGENTS.md via `instructions`) automatically — no manual injection needed
- Their own prompt body is the agent definition body written in the `.md` file
- They can Read Layer 2 (section AGENTS.md) at invocation time via the Read tool
- They can call `skill()` for Layer 3 on demand when reusable utilities are needed

## 7. Interaction with Section-Specific Agents

- Each section agent reads its section's AGENTS.md at invocation time via the Read tool
- This is consistent with the root AGENTS.md's lazy loading directive — nothing is preloaded
- The root AGENTS.md provides global context (structure, pipeline, statuses); the section AGENTS.md provides specific rules (frontmatter requirements, categorization)
- Layer 3 skills provide reusable utility instructions that any agent can invoke via `skill()`

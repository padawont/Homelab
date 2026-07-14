---
title: "Approach Comparison: Subagents vs Skills vs Hybrid for Section-Specific Agents"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - agents
  - skills
  - architecture
sources:
  - knowledge: "knowledge/tooling/opencode/agents/overview"
  - knowledge: "knowledge/tooling/opencode/agents/agent-configuration"
  - knowledge: "knowledge/tooling/opencode/agents/agent-discovery"
  - knowledge: "knowledge/tooling/opencode/agents/agent-permissions"
  - knowledge: "knowledge/tooling/opencode/agents/context-loading"
  - knowledge: "knowledge/tooling/opencode/skills/overview"
  - knowledge: "knowledge/tooling/opencode/skills/skill-configuration"
  - knowledge: "knowledge/tooling/opencode/skills/gh-skill-case-study"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
last_audit_date: 2026-05-31
---

# Approach Comparison: Subagents vs Skills vs Hybrid for Section-Specific Agents

## Context

The RunicEngines knowledge base contains five content sections — ideas, knowledge, research, proposals, and ADRs — each with distinct conventions encoded in their respective `AGENTS.md` files. Currently, no automation enforces the content pipeline (Idea → Knowledge → Research → Proposal → ADR), leaving contributors to manually follow conventions. Three possible approaches exist to implement section-specific agents using OpenCode's subagent and skill primitives: subagents-only, skills-only, and a hybrid combining both.

## The Three-Layer Architecture

[GitHub issue #11](https://github.com/RunicEngines/knowledge-base/issues/11) introduced a three-layer architecture that serves as the lens for comparing approaches. Each layer has a distinct responsibility, owner, and mechanism:

| Layer | Mechanism | Ownership | Role |
|---|---|---|---|
| **Rules** | Section `AGENTS.md` | Human-maintained | Declarative — defines what must happen |
| **Orchestrators** | `.opencode/agents/*.md` | Agent-defined | Procedural — automates applying the rules |
| **Utilities** | `.opencode/skills/*/SKILL.md` | Agent-defined | Reusable — loads on-demand instructions |

```
┌─────────────────────────────┐
│     Rules (AGENTS.md)       │  Declarative, human-owned
│  "Section must have X, Y"   │
└─────────────┬───────────────┘
              │ read at runtime
              ▼
┌─────────────────────────────┐
│  Orchestrators (agents/*)   │  Procedural, agent-owned
│  "Read AGENTS.md, apply X"  │
└─────────────┬───────────────┘
              │ call on-demand
              ▼
┌─────────────────────────────┐
│   Utilities (skills/*)      │  Reusable, agent-owned
│  "How to scaffold template" │
└─────────────────────────────┘
```

## Approach Comparison

The following table evaluates three approaches across seven criteria relevant to the knowledge-base use case:

| Criterion | Subagents-only | Skills-only | Subagents + Shared Skills |
|---|---|---|---|
| **Permission isolation** | Per-agent permissions (full granularity) | None — inherits caller's permissions | Per-agent + skill access controlled via `permission.skill` |
| **Model pinning** | Per-agent model override | None — runs under caller's model | Per-agent model override |
| **DRY shared logic** | Duplicated across agents | Natural sharing (skills designed for reuse) | Extracted to skills; agent prompt stays focused |
| **Context loading** | Agent prompt + Read AGENTS.md at runtime | Inline SKILL.md instructions + agent decides to Read AGENTS.md | Agent prompt + Read AGENTS.md + skill() on demand |
| **Complexity** | Moderate — standalone .md files, no dependencies | High — skills can't be automation units; needs orchestrator agent | Moderate-high initially, lower long-term via shared utilities |
| **Discoverability** | High — @mention + task tool + auto-discovered | Medium — only via skill tool `<available_skills>` | High for agents (@mention), medium for skills (skill tool) |
| **AGENTS.md awareness** | Direct — agent prompt says "Read section AGENTS.md" | Indirect — skill can suggest it, agent must decide | Agent-driven + skill-enabled |

## Detailed Analysis

### Permission Isolation

Subagents support full YAML frontmatter permissions — each agent can define granular `allow`/`ask`/`deny` rules per tool, including bash command patterns for `bash` tool restrictions. This is essential for section-specific agents that need different capabilities (e.g., a proposal agent may run Quarto, while an idea agent only edits markdown). Skills have no permission model; they inherit whatever permissions the calling agent holds. In the hybrid model, the `permission.skill` field at the agent level controls which skills an agent may invoke, preserving isolation while enabling shared utilities.

### Model Pinning

Subagents can pin a specific model via `model: provider/model-id` in frontmatter. Without this field, a subagent inherits the invoker's model. Skills have no model field — they always run under the calling agent's model. For section-specific agents that may benefit from different model capabilities (e.g., a cheaper/faster model for simple filing tasks vs. a stronger model for complex research analysis), subagent model pinning is a critical feature that skills cannot provide.

### DRY Shared Logic

Subagents-only forces duplication of any shared instruction patterns across all five agent files — frontmatter validation, template scaffolding, cross-linking conventions. Skills naturally support reuse: a single `SKILL.md` defines the pattern, and any agent that calls `skill({ name: "..." })` gets the instructions injected. The hybrid approach extracts common patterns into skills while keeping section-specific logic in the agent prompt, achieving the best of both worlds.

### Context Loading

A subagent loads its context from its prompt (defined in the `.md` file) plus the root `AGENTS.md` (injected automatically). It then reads the section `AGENTS.md` at runtime via the Read tool — this is the lazy pattern that prevents duplication and drift. A skill can describe _how_ to read `AGENTS.md` in its instructions, but the agent must independently decide to follow those instructions. In hybrid mode, the agent prompt controls the _timing_ of reads while skills control the _method_ of common operations.

### Complexity

Subagents-only requires five standalone `.md` files with no cross-agent dependencies — moderate complexity. Skills-only requires an orchestrator agent with complex routing logic to decide which skill to invoke for which section, and skills themselves cannot act as automation units (they're instruction-only). Hybrid has higher initial complexity (agent files + skill files) but the separation of concerns — rules in `AGENTS.md`, automation in agents, utilities in skills — reduces long-term maintenance burden.

### Discoverability

Subagents are auto-discovered from `.opencode/agents/` and appear in `@mention` lists, the task tool, and the agent switcher. Skills are listed inside `<available_skills>` XML in agent tool descriptions and require a `skill()` call to load — an extra step that the agent must initiate. Hybrid maximizes discoverability for agents while keeping skills accessible on demand.

### AGENTS.md Awareness

A subagent's prompt can directly instruct: "Read the `ideas/AGENTS.md` file to understand the conventions for this section." This creates a deterministic link between the orchestrator and the rules it enforces. A skill can only _suggest_ reading `AGENTS.md` — the calling agent retains full discretion. In hybrid mode, the agent controls when to read (`Read AGENTS.md` at startup) and skills provide the detailed how-to for specific sub-tasks.

## Conclusion

Subagents-only is a viable starting point — five standalone agents, each with full permission isolation, model pinning, and direct `AGENTS.md` awareness — but it misses the benefits of shared logic, leading to prompt duplication and drift over time. Skills-only is unsuitable as the primary automation mechanism: skills lack permission models, cannot pin models, have indirect `AGENTS.md` awareness, and require a separate orchestrator to route work. **Subagents + Shared Skills (the hybrid approach) is the recommended architecture.** It combines the permission isolation and model pinning of subagents with the reusable, DRY instruction patterns of skills, aligned with the three-layer architecture of Rules → Orchestrators → Utilities.

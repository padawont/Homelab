# ADR-0005: Knowledge Base Agents and Skills

## README.md

# ADR 0005: Knowledge Base Agents and Skills Architecture

Architecture decision record covering the hybrid subagent + shared skills approach for automating this Knowledge Base's content sections and pipeline.

[overview.md](./overview.md) contains the full decision record in MADR format.

## overview.md

---
adr: 0005
title: "Knowledge Base Agents and Skills Architecture"
author: "refactorartist (Khalid Zubair)"
status: final
date: 2026-06-05
topic: "agents-and-skills"
date-proposed: 2026-05-31
history: "https://github.com/RunicEngines/knowledge-base/pull/30"
context: >
  This repository's five content sections each have distinct AGENTS.md
  conventions and a content pipeline (Idea → Knowledge → Research →
  Proposal → ADR), but no automation enforces them. OpenCode offers
  subagent and skill primitives; this ADR decides which combination best
  serves this Knowledge Base's specific needs.
decision: >
  Adopt a hybrid subagents + shared skills architecture scoped to this
  repo: five section agents (ideas-agent, knowledge-agent, research-agent,
  proposals-agent, adr-agent), three role agents (kb-architect, kb-tech-lead,
  kb-editor), and four shared skills (kb-scaffold-topic, kb-frontmatter-validate,
  kb-cross-link-check, kb-status-transition) under .opencode/, with
  zero-registration auto-discovery and fail-and-explain validation.
consequences: >
  Permission isolation, model pinning, and DRY shared logic across all
  Knowledge Base agents. Trade-offs: higher initial complexity, kb- prefix
  needed for namespace isolation within this repo's skill set, shared
  skills create cross-agent regression risk, no central agent registry.
sources:
  - "../research/section-specific-agents/01-approach-comparison"
  - "../research/section-specific-agents/02-directory-layout"
  - "../research/section-specific-agents/03-registration-discovery"
  - "../research/section-specific-agents/04-context-loading"
  - "../research/section-specific-agents/05-shared-skills"
  - "../research/section-specific-agents/06-scaffolding-validation"
  - "../research/section-specific-agents/07-permissions"
  - "../research/section-specific-agents/10-governance"
  - "../research/section-specific-agents/12-kb-architect"
  - "../research/section-specific-agents/13-kb-tech-lead"
  - "../research/section-specific-agents/14-kb-editor"
  - "../knowledge/tooling/opencode/agents/overview"
  - "../knowledge/tooling/opencode/agents/configuration"
  - "../knowledge/tooling/opencode/agents/discovery"
  - "../knowledge/tooling/opencode/agents/permissions"
  - "../knowledge/tooling/opencode/agents/context-loading"
  - "../knowledge/tooling/opencode/skills/overview"
  - "../knowledge/tooling/opencode/skills/configuration"
  - "../knowledge/tooling/opencode/skills/gh-case-study"
references:
  - "https://github.com/RunicEngines/knowledge-base/issues/11"
  - "https://github.com/RunicEngines/knowledge-base/issues/15"
  - "https://opencode.ai/docs/agents"
  - "https://opencode.ai/docs/skills"
  - "https://opencode.ai/docs/permissions"
---

# ADR 0005: Knowledge Base Agents and Skills Architecture

## Status

Final (2026-06-05)

## Context and Problem Statement

The RunicEngines Knowledge Base contains five content sections — ideas, knowledge, research, proposals, and ADRs — each with distinct conventions encoded in their respective AGENTS.md files: unique frontmatter schemas, status lifecycles, folder structures, and cross-linking requirements. A content pipeline flows through these sections (Idea → Knowledge → Research → Proposal → ADR), but currently no automation enforces section-specific conventions or pipeline progression. Contributors must manually follow the rules encoded in each section's AGENTS.md — a process that is error-prone, inconsistent, and limited to those who have read the documentation.

OpenCode provides two primitives for automating workflows: subagents (self-contained automation units with permission isolation and model pinning) and skills (reusable instruction modules loaded on demand). Together with the existing AGENTS.md files (which serve as declarative rules), these form a three-layer architecture of Rules → Orchestrators → Utilities.

The Knowledge Base needs to decide which combination of these primitives — subagents-only, skills-only, or subagents + shared skills (hybrid) — best automates its section-specific workflows and content pipeline, before implementation begins.

## Decision

### Architecture: Subagents + Shared Skills (Hybrid)

Adopt the hybrid approach combining subagents (for permission isolation, model pinning, and direct AGENTS.md awareness) with shared skills (for DRY, reusable utility instructions). The three-layer architecture maps cleanly to:

| Layer | Mechanism | Ownership | Role |
|---|---|---|---|
| Rules | Section AGENTS.md | Human-maintained | Declarative — defines what must happen |
| Orchestrators | .opencode/agents/*.md | Agent-defined | Procedural — automates applying the rules |
| Utilities | .opencode/skills/*/SKILL.md | Agent-defined | Reusable — loads on-demand instructions |

### Agent Roster: 5 Section Agents + 3 Role Agents

**Section agents** — one per content section, each enforcing its AGENTS.md:

| Agent | Section | Purpose |
|---|---|---|
| ideas-agent | ideas/ | Draft and evolve ideas with changelog tracking |
| knowledge-agent | knowledge/ | Create and maintain knowledge notes with sources |
| research-agent | research/ | Synthesize ideas + knowledge into analysis |
| proposals-agent | proposals/ | Manage versioned implementation plans |
| adr-agent | adr/ | Write architecture decision records in MADR format |

**Role agents** — cross-sectional, not tied to a single section:

| Agent | Scope | Purpose |
|---|---|---|
| kb-architect | ADRs + Proposals | Heavy architectural drafting; delegates scaffolding to adr-agent and proposals-agent via task tool |
| kb-tech-lead | Knowledge + Research | External accuracy validation via websearch and webfetch; read-only |
| kb-editor | All sections | Cross-cutting proofreading using shared skills; no bash or webfetch |

### Skill Roster: 4 Shared Skills

Four utility directories under .opencode/skills/:

| Skill | Purpose | Used by |
|---|---|---|
| kb-scaffold-topic | Create topic folder from template, populate frontmatter | All agents |
| kb-frontmatter-validate | Check required fields, types, valid values | All agents |
| kb-cross-link-check | Verify referenced paths exist on disk | All agents |
| kb-status-transition | Validate status lifecycle transitions | All agents |

### Directory Layout

All agent and skill files live under .opencode/ at the repository root:

```
.opencode/
├── agents/
│   ├── ideas-agent.md
│   ├── knowledge-agent.md
│   ├── research-agent.md
│   ├── proposals-agent.md
│   ├── adr-agent.md
│   ├── kb-architect.md
│   ├── kb-tech-lead.md
│   └── kb-editor.md
└── skills/
    ├── kb-scaffold-topic/
    │   └── SKILL.md
    ├── kb-frontmatter-validate/
    │   └── SKILL.md
    ├── kb-cross-link-check/
    │   └── SKILL.md
    └── kb-status-transition/
        └── SKILL.md
```

Both agents and skills are auto-discovered — agents from .opencode/agents/*.md (flat, no subdirectories), skills from .opencode/skills/\<name\>/SKILL.md (one level, exactly SKILL.md per directory).

### Naming Conventions

| Entity | Pattern | Examples | Rationale |
|---|---|---|---|
| Section agents | \<section\>-agent | ideas-agent, adr-agent | Explicit purpose, avoids confusion with section directory names |
| Role agents | kb-\<role\> | kb-architect, kb-tech-lead | kb- prefix scopes to this repo (role names are generic enough to collide across projects) |
| Skills | kb-\<verb\>-\<noun\> | kb-scaffold-topic | kb- prefix prevents collisions in OpenCode's globally flat skill namespace |

### Model Pinning

Each agent pins a model appropriate to its task complexity:

| Agent | Model | Rationale |
|---|---|---|
| ideas-agent | opencode-go/deepseek-v4-flash | Simple scaffolding and frontmatter filling |
| knowledge-agent | opencode-go/deepseek-v4-pro | Factual accuracy benefits from stronger reasoning |
| research-agent | opencode-go/deepseek-v4-pro | Synthesis of ideas + knowledge requires complex reasoning |
| proposals-agent | opencode-go/deepseek-v4-pro | Implementation planning benefits from deeper context |
| adr-agent | opencode-go/deepseek-v4-pro | Trade-off analysis and consequence reasoning |
| kb-architect | opencode-go/deepseek-v4-pro | Heavy architectural document drafting |
| kb-tech-lead | opencode-go/deepseek-v4-pro | External accuracy validation |
| kb-editor | opencode-go/deepseek-v4-flash | Proofreading is lightweight; flash is sufficient |

If omitted, an agent inherits the calling agent's model.

### Permissions

All agents start with full-access permissions as explicit documentation of intent:

```yaml
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  bash: allow
  list: allow
  task: allow
  skill: allow
```

These match OpenCode's defaults — no opencode.json changes are required. Restrictions can be added per-agent as a one-line YAML change if concerns arise later (e.g., limiting bash command patterns or skill access).

### Registration: Zero-Config Auto-Discovery

No changes to opencode.json are required. Both agents and skills are auto-discovered by walking from the CWD to the git worktree root:

- **Agents**: .opencode/agents/*.md — the filename (minus .md extension) becomes the agent name for @mention and task tool invocation.
- **Skills**: .opencode/skills/\<name\>/SKILL.md — the directory name becomes the skill identifier for `skill({ name: "..." })` calls.

Adding a new agent or skill is purely additive: place the file in the correct directory and it becomes available immediately. No registry, no manifest, no config key.

### Context Loading: Three-Layer Lazy Pattern

Context is loaded in three layers, consistent with the root AGENTS.md lazy-loading directive:

| Layer | Source | Loaded | Content |
|---|---|---|---|
| Layer 1 | Root AGENTS.md | Always (via opencode.json instructions) | Repo structure, pipeline, statuses, lazy-load directive |
| Layer 2 | Section AGENTS.md | At invocation via Read tool | Section-specific rules (frontmatter, categorization) |
| Layer 3 | Skills | On demand via skill() | Reusable utility instructions |

Subagents inherit Layer 1 automatically. They read Layer 2 at startup via the Read tool. They call skill() for Layer 3 when a utility is needed. Nothing is preloaded — every section's AGENTS.md is loaded on a need-to-know basis.

### Error Handling: Fail-and-Explain (JSON)

All validation returns structured JSON for deterministic agent consumption:

```json
{"valid": false, "errors": [
  {"field": "sources", "type": "missing", "detail": "Required field `sources` not found in frontmatter"},
  {"field": "status", "type": "invalid_transition", "detail": "draft → final is invalid for research"}
]}
```

Agents receive JSON and report to the user in natural language. This ensures consistent parsing across all four skills and eliminates silent quality drift.

### Governance: Three-Layer Boundary

The three-layer architecture (Rules → Orchestrators → Utilities) defines when to create or extend each component:

| Action | When |
|---|---|
| New section agent | New content section with its own AGENTS.md and unique conventions |
| New role agent | Cross-cutting workflow that spans multiple sections |
| Extend existing agent | New task in same section with same model/permission profile |
| New shared skill | Same instruction pattern used by 2+ agents |
| Inline in agent prompt | Section-specific logic used by only one agent |

Anti-patterns to avoid: duplicating logic across agents (extract to skill instead), embedding rules in agent prompts (read AGENTS.md at runtime instead), creating skills used by only one agent, using skills as automation units (they are instruction-only).

### ADR Numbering

The adr-agent determines the next sequential ADR number by loading the gh skill via `skill({ name: "gh" })` to scan the repository's GitHub issues for ADR-labeled issues, identifying the highest existing ADR number from issue titles, incrementing by 1, and zero-padding to 4 digits. No counter file is maintained — GitHub issues are the source of truth.

### Agent Mode

All eight agents use `mode: subagent` — they are specialized helpers invoked via @mention or the task tool, not primary agents. This keeps them discoverable in autocomplete while ensuring they are only invoked when explicitly requested.

## Consequences

### Positive

- **Permission isolation**: Each section agent can define tool-level restrictions independently, preventing scope creep across sections.
- **Model pinning**: Agents match model capability to task complexity — flash for lightweight scaffolding, pro for deep reasoning.
- **DRY shared logic**: Common patterns (scaffolding, validation, cross-link checking, status transitions) live in skills rather than being duplicated across eight agent prompts.
- **Zero-config registration**: Adding new agents or skills requires no opencode.json changes — auto-discovery handles everything.
- **Lazy context loading**: Section AGENTS.md is only read when needed, avoiding context bloat across all agents.
- **Fail-and-explain validation**: Structured JSON errors catch quality issues early and prevent silent drift.
- **Clear governance**: The three-layer boundary provides explicit rules for when to create agents, skills, or inline logic.

### Negative

- **Higher initial complexity**: The hybrid approach requires creating and maintaining both agent files and skill files, compared to a subagents-only approach that needs only agent files.
- **kb- prefix burden**: All skill and role-agent names must carry the kb- prefix to avoid namespace collisions in OpenCode's flat skill registry.
- **Cross-agent regression risk**: A change to a shared skill affects all agents that call it, requiring broader testing than a change to an isolated agent prompt.
- **No central registry**: Auto-discovery means there is no single manifest of all agents and skills — auditing what exists requires scanning the filesystem.
- **Agent-skill coupling**: Agents must know which skills to call and when, creating a dependency between an agent's procedural flow and the skills it invokes.

## Considered Options

Three approaches were evaluated across seven criteria:

| Criterion | Subagents-only | Skills-only | Hybrid (chosen) |
|---|---|---|---|
| **Permission isolation** | Per-agent permissions (full granularity) | None — inherits caller's permissions | Per-agent + skill access controlled via permission.skill |
| **Model pinning** | Per-agent model override | None — runs under caller's model | Per-agent model override |
| **DRY shared logic** | Duplicated across agents | Natural sharing (skills designed for reuse) | Extracted to skills; agent prompt stays focused |
| **Context loading** | Agent prompt + Read AGENTS.md | Skill suggests reading; agent decides | Agent prompt + Read AGENTS.md + skill() on demand |
| **Complexity** | Moderate — standalone .md files | High — skills can't be automation units | Moderate-high initially, lower long-term |
| **Discoverability** | High — @mention + task + auto-discovered | Medium — only via skill() call | High for agents, medium for skills |
| **AGENTS.md awareness** | Direct — prompt says "Read section AGENTS.md" | Indirect — skill can suggest it | Agent-driven + skill-enabled |

### Subagents-Only

Five standalone agent files with full permission isolation and model pinning. Simple initial setup but forces duplication of shared patterns (frontmatter validation, template scaffolding) across all agents, leading to prompt drift over time.

### Skills-Only

Reusable instruction modules with no permission isolation or model pinning. Unsuitable as the primary automation mechanism — skills lack permission models, cannot pin models, have indirect AGENTS.md awareness, and require a separate orchestrator to route work.

### Subagents + Shared Skills (Hybrid — Chosen)

Combines the permission isolation and model pinning of subagents with the DRY instruction patterns of skills. Aligns with the three-layer architecture of Rules → Orchestrators → Utilities. Higher initial complexity but lower long-term maintenance burden.

## Compliance

Compliance with this ADR is enforced through:

1. **Governance rules**: The three-layer boundary defined in this decision must be followed for all future agent and skill additions. Any new agent or skill must be justified against the governance criteria before creation.

2. **Manual smoke tests**: After implementation, each agent and skill must pass the verification checklist — scaffold creation, frontmatter validation, cross-link checking, status transitions, ADR numbering, and @mention invocability.

3. **Code review**: All additions or modifications to agents and skills under .opencode/ must be reviewed against this ADR's architecture and naming conventions as part of the PR process.

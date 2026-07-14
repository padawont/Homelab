---
title: "Governance: When to Add Agents, Skills, or Inline Logic"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - agents
  - skills
  - governance
sources:
  - knowledge: "knowledge/tooling/opencode/agents/overview"
  - knowledge: "knowledge/tooling/opencode/skills/overview"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-05-31
---

# Governance: When to Add Agents, Skills, or Inline Logic

## 1. The Three-Layer Boundary

Quick reference table:

| Layer | What | File | Owner | Loaded |
|---|---|---|---|---|
| Rules | Declarative conventions (what) | `section/AGENTS.md` | Human editors | Read tool at invocation |
| Orchestrator | Procedural workflow (how) | `.opencode/agents/<name>.md` | Agent developer | Auto-discovered |
| Utilities | Reusable instructions (how-to) | `.opencode/skills/kb-<name>/SKILL.md` | Agent developer | `skill()` on demand |

## 2. When to Add a New Agent

Create a new agent when:
- A new content section is added to the pipeline with its own `AGENTS.md`
- The section has a distinct workflow not shared by existing agents
- The section requires a different model (flash vs pro) or different permission profile
- The section's `AGENTS.md` has unique conventions to enforce
- A **cross-cutting role** emerges that supports multiple sections (e.g., architect for ADR/proposal coordination, tech-lead for external validation, editor for proofreading) — these are role-based agents that coordinate with or validate the work of section agents

Do NOT create a new agent for:
- Index-only sections with no content pipeline (projects, tasks)
- Minor workflow variations within an existing section (extend the existing agent)

## 3. When to Extend an Existing Agent

Add steps to an existing agent when:
- The new task belongs to the same content section
- The task follows the same scaffold → validate → cross-link → transition pattern
- The task is governed by the same section's `AGENTS.md`
- The same model/permission profile suffices

## 4. When to Add a New Skill

Create a skill when:
- The same instruction pattern is used by 2+ agents (the defining criterion)
- The logic is a self-contained, teachable unit
- It solves a "duplicated across agents" problem
- It operates on a single concern (single responsibility)

Use the `kb-` prefix for all Knowledge Base skills.

## 5. When to Inline in Agent Prompt

Keep logic in the agent prompt when:
- It is section-specific and meaningful to only one section
- It is called only once or rarely
- It is tightly coupled to the agent's procedural flow (e.g., "Read section AGENTS.md")
- It requires agent-specific context (permissions, model, state)

## 6. Anti-Patterns

- **Duplicating the same logic across agents** → extract into a skill
- **Embedding rules in agent prompt instead of reading AGENTS.md** → always read at runtime
- **Creating a skill used by only one agent** → inline in agent prompt unless projected for reuse
- **Creating a new agent when an existing one covers the same section** → extend
- **Pre-loading all AGENTS.md at startup** → lazy-load per the root directive
- **Deep nesting in directories** → agents flat, skills one level only
- **Using skills as automation units** → skills are instruction-only, not orchestrators
- **Skill name collisions** → always use `kb-` prefix
- **Bundling unrelated concerns into one skill** → single responsibility per skill

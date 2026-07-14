---
title: "Section-Specific OpenCode Agents — Implementation Approaches"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - agents
  - skills
  - knowledge-base
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
  - url: "https://opencode.ai/docs/config"
    title: "OpenCode Config Documentation"
  - url: "https://github.com/RunicEngines/knowledge-base/blob/main/.opencode/skills/gh/SKILL.md"
    title: "gh Skill Reference Implementation"
last_audit_date: 2026-05-31
---

# Section-Specific OpenCode Agents — Implementation Approaches

## Context

The RunicEngines Knowledge Base has five content sections — ideas, knowledge, research, proposals, and adr — each with its own `AGENTS.md` defining distinct conventions for frontmatter, status lifecycles, folder structures, and cross-linking. The root `AGENTS.md` is injected into all agents via `opencode.json`'s `instructions` key, providing global structure and the lazy-loading directive. Section `AGENTS.md` files are loaded on demand via the Read tool at agent invocation time, never preloaded.

No automation currently enforces section-specific conventions or the content pipeline (Idea → Knowledge → Research → Proposal → Project/Task, with ADR as a branch). Contributors must manually follow the rules encoded in each section's `AGENTS.md`. [GitHub issue #11](https://github.com/RunicEngines/knowledge-base/issues/11) proposed creating section-specific OpenCode agents to automate convention enforcement, template scaffolding, and content pipeline progression. This research evaluates the implementation approaches, directory layout, context-loading architecture, shared utilities, permissions, and verification strategy for these agents.

## Findings

- **01-approach-comparison.md** — Three approaches were evaluated: subagents-only, skills-only, and subagents + shared skills (hybrid). The hybrid approach was recommended because subagents provide permission isolation and model pinning while skills provide DRY shared logic. Skills-only lacks permission models and cannot pin models; subagents-only duplicates logic across agents.

- **02-directory-layout.md** — Five agent files under `.opencode/agents/` (`ideas-agent.md`, `knowledge-agent.md`, `research-agent.md`, `proposals-agent.md`, `adr-agent.md`) and four skill directories under `.opencode/skills/` with the `kb-` prefix (`kb-scaffold-topic`, `kb-frontmatter-validate`, `kb-cross-link-check`, `kb-status-transition`). Agents use `mode: subagent`; skills follow the flat `<name>/SKILL.md` structure.

- **03-registration-discovery.md** — Zero `opencode.json` changes needed. Both agents and skills are auto-discovered by walking from the CWD to the git worktree root. No explicit registration or config key is required. Adding an agent is a simple matter of placing a `.md` file in the correct directory.

- **04-context-loading.md** — Three-layer context loading: Layer 1 (root `AGENTS.md`) is always injected via `instructions`; Layer 2 (section `AGENTS.md`) is loaded lazily via the Read tool at invocation time; Layer 3 (skills) is loaded on demand via `skill()`. Subagents inherit Layer 1 automatically and read Layer 2 themselves.

- **05-shared-skills.md** — Four skills handle the common operations across all agents: `kb-scaffold-topic` (template-based folder creation), `kb-frontmatter-validate` (field presence, types, statuses, dates, kebab-case tags), `kb-cross-link-check` (path existence verification), `kb-status-transition` (lifecycle validation). Skills follow the `gh` skill design patterns: directive tone, gotcha-first, LLM-scannable.

- **06-scaffolding-validation.md** — Template scaffolding follows a six-step workflow (copy template to section folder, create kebab-case folder, copy template files into folder, populate frontmatter, remove comments, write content). Validation uses a fail-and-explain pattern that reports specific violations and halts rather than silently continuing or auto-correcting. Each section has unique scaffolding requirements including distinct folder patterns and mandatory files.

- **07-permissions.md** — All agents start with full-access permissions (`allow` on read, edit, glob, grep, bash, list, task, skill), matching OpenCode's defaults. This is explicit documentation of intent rather than a functional requirement. A restriction can be added per-agent as a one-line YAML change if concerns arise later.

- **08-open-questions-resolved.md** — All 10 open questions from the idea were resolved: ADR numbering via directory scan + increment, agent visibility via `@mention`, filenames using the `ideas-agent` pattern, model pinning (flash for ideas, pro for the rest), fail-and-explain error handling, zero `opencode.json` changes, `kb-` prefix for skill namespacing, and `mode: subagent` for all agents.

- **09-verification.md** — Manual smoke test checklist covering scaffold creation, frontmatter validation, cross-link checking, status transitions, ADR numbering, and `@mention` invocability for all five section agents.

- **10-governance.md** — Decision rules for when to create a new agent, extend an existing one, create a shared skill, or keep logic in an agent prompt. Defines the three-layer boundary (Rules → Orchestrator → Utilities) and lists anti-patterns.

- **11-change-management.md** — How changes to research notes, agent definitions, and skills are tracked. Proposes research changelog.md following the ideas changelog pattern. Agent and skill changes are tracked via git history.

- **12-kb-architect.md** — Cross-sectional role agent that handles heavy architectural document writing (ADRs, proposals). Uses deepseek-v4-pro for strong reasoning. Delegates scaffolding to adr-agent and proposals-agent via task.

- **13-kb-tech-lead.md** — Validation agent that checks knowledge and research notes against external authoritative sources using websearch and webfetch. Uses deepseek-v4-pro. Read-only — does not create or edit content.

- **14-kb-editor.md** — Proofreading agent that reuses kb-frontmatter-validate, kb-cross-link-check, and kb-status-transition across all sections. Uses deepseek-v4-flash. No bash, no webfetch — works entirely with repo-internal content.

## Analysis

The hybrid architecture (subagents + shared skills) was chosen over the alternatives because it cleanly maps to the three-layer model of Rules → Orchestrator → Utilities. Subagents provide permission isolation and model pinning — critical for section-specific agents that may benefit from different model capabilities (flash for simple idea scaffolding, pro for complex ADR analysis) and may need different tool access levels. Skills provide DRY shared logic, eliminating the prompt duplication and drift that would occur with a subagents-only approach. The `kb-` prefix for skills prevents namespace collisions in OpenCode's flat skill namespace, which is shared across all projects on the same machine; agents do not need a prefix since they are scoped per-project.

No `opencode.json` changes are required because OpenCode auto-discovers agents from `.opencode/agents/` and skills from `.opencode/skills/`. This means adding agents and skills is purely additive — create files in the correct directories, and they become available immediately. The fail-and-explain pattern for validation ensures errors are caught early and reported clearly, preventing silent drift in content quality. The lazy-loading architecture (root `AGENTS.md` always in context, section `AGENTS.md` read at invocation time) is consistent with the existing root directive and avoids bloating every agent's context with irrelevant rules.

## Recommendations

1. **Adopt the hybrid subagents + shared skills architecture** — five agent `.md` files under `.opencode/agents/` and four skill directories under `.opencode/skills/`.

2. **Create five section agent files**: `ideas-agent.md`, `knowledge-agent.md`, `research-agent.md`, `proposals-agent.md`, `adr-agent.md` — each with `mode: subagent`, full-access permissions, and a pinned model (flash for ideas, pro for the rest).

3. **Create three role-based agent files**: `kb-architect.md` (cross-sectional ADR and proposal drafting, deepseek-v4-pro), `kb-tech-lead.md` (external accuracy validation via websearch/webfetch, deepseek-v4-pro), `kb-editor.md` (cross-cutting proofreading using shared skills, deepseek-v4-flash).

4. **Create four skill directories**: `kb-scaffold-topic/`, `kb-frontmatter-validate/`, `kb-cross-link-check/`, `kb-status-transition/` — each containing a single `SKILL.md` following the `gh` skill design patterns.

5. **Do not modify `opencode.json`** — auto-discovery handles all registration. The existing `instructions: ["AGENTS.md"]` config remains sufficient.

6. **Verify via the manual smoke test checklist** — scaffold a topic in each section, validate frontmatter, check cross-links, test status transitions, confirm ADR numbering, and verify `@mention` invocation for all five section agents.

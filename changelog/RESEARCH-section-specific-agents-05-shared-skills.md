---
title: "Shared Skills: Common Utility Modules for All Agents"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - skills
  - utilities
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview"
  - knowledge: "knowledge/tooling/opencode/skills/skill-configuration"
  - knowledge: "knowledge/tooling/opencode/skills/gh-skill-case-study"
  - knowledge: "knowledge/tooling/opencode/agents/agent-permissions"
references:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
last_audit_date: 2026-05-31
---

# Shared Skills: Common Utility Modules for All Agents

## 1. Why Shared Skills?

Without skills, each agent duplicates scaffolding, validation, cross-link checking, and status transition logic in its prompt. With skills, agents call `skill({ name: "kb-..." })` instead of duplicating instructions. This addresses Open Question #2 from the idea: "should shared workflow logic be extracted into a shared skill or kept duplicated per agent?"

## 2. Skill Format and Naming

Quick recap: `.opencode/skills/<name>/SKILL.md`, required `name` + `description` frontmatter, `kb-` prefix for Knowledge Base namespace.

## 3. The `kb-` Prefix

Skill names live in a globally flat namespace. The `kb-` prefix scopes skills to this repo, preventing collision with other projects. The prefix applies only to skills (agents are project-scoped and do not need it).

## 4. Proposed Skills

**`kb-scaffold-topic`** — Create topic folder from section template, populate frontmatter.
- Determine target section from context.
- Create kebab-case topic folder.
- Copy templates from the matching template directory (note: template dirs use singular names — `templates/idea/` for section `ideas/`, `templates/proposal/` for section `proposals/`).
- Fill required frontmatter fields.
- Used by: all 5 agents.

**`kb-frontmatter-validate`** — Check required fields, types, valid values.
- Read YAML frontmatter of a given file.
- Validate against section's rules.
- Check field types, valid status, kebab-case tags, ISO dates.
- Used by: all 5 agents.

**`kb-cross-link-check`** — Verify referenced paths exist on disk.
- Parse cross-link fields: `sources`, `related_ideas`, `related_research`, `related_adrs`, `replaces`, `replaced-by`.
- Check that each referenced path exists relative to file location.
- Report broken links.
- Used by: 4 of 5 agents (optional for ideas).

**`kb-status-transition`** — Validate status lifecycle transitions per section rules.
- Accept current status + proposed new status + section.
- Look up section's valid lifecycle.
- Report valid/invalid transitions.
- Used by: all 5 agents (each section has its own lifecycle).

## 5. Agent-to-Skill Mapping

| Agent | kb-scaffold-topic | kb-frontmatter-validate | kb-cross-link-check | kb-status-transition |
|---|---|---|---|---|
| ideas-agent | Yes | Yes | Maybe | Yes |
| knowledge-agent | Yes | Yes | Yes | Yes |
| research-agent | Yes | Yes | Yes | Yes |
| proposals-agent | Yes | Yes | Yes | Yes |
| adr-agent | Yes | Yes | Yes | Yes |

## 6. Reference: The `gh` Skill Design Patterns

The existing `gh` skill (`.opencode/skills/gh/SKILL.md`) establishes several patterns that the proposed skills should follow:

- **Directive tone** — says what the agent should do, not what it could do.
- **Gotcha-first** — common mistakes called out before the rule.
- **LLM-scannable** — short sections with clear headings.
- **No redundant docs** — only what agents get wrong; no platform documentation.

## 7. How Agents Use Skills in Workflow

1. Agent loads section `AGENTS.md` for rules.
2. Agent calls `kb-scaffold-topic` to create new content.
3. Agent calls `kb-frontmatter-validate` to check the result.
4. Agent calls `kb-cross-link-check` to verify cross-references.
5. Agent calls `kb-status-transition` for lifecycle moves.

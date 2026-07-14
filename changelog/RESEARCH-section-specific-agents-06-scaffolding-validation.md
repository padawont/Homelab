---
title: "Scaffolding and Validation: How Agents Create and Verify Content"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - agents
  - skills
  - validation
  - scaffolding
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview"
  - knowledge: "knowledge/tooling/opencode/skills/skill-configuration"
references:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-05-31
---

# Scaffolding and Validation: How Agents Create and Verify Content

## 1. The Scaffolding Workflow

Creating a new topic folder follows a six-step process defined in `templates/AGENTS.md`:

1. Copy the relevant template from `templates/` into the target section folder.
2. Create a new kebab-case folder for the topic.
3. Copy the template files into that folder.
4. Fill in the YAML frontmatter — all fields are required unless marked optional.
5. Remove any template comments (`<!-- ... -->`).
6. Write the content following the section's conventions.

The `kb-scaffold-topic` skill automates this entirely. The agent determines the target section from context, calls `kb-scaffold-topic`, and the skill handles folder creation, file copying, frontmatter population, and template comment removal in a single invocation.

## 2. Section-Specific Scaffolding Details

Each section has unique scaffolding requirements. The skill must account for all of them.

| Aspect | ideas | knowledge | research | proposals | adr |
|--------|-------|-----------|----------|-----------|-----|
| Template dir | `templates/idea/` | `templates/knowledge/` | `templates/research/` | `templates/proposal/` | `templates/adr/` |
| Required files | README, overview, changelog | README, overview | README, overview | README, overview, index.qmd | README, overview |
| Folder pattern | `<cat>/<subcat>/<topic>/` | `<cat>/<subcat>/<topic>/` | `<topic>/` (flat) | `<topic>/` (flat) | `<NNNN>-<topic>/` |
| Extra steps | Changelog init | Sources + audit date | Sources + references | Version init, quarto | NNNN numbering, MADR |

Template directories use singular names (`templates/idea/`, `templates/proposal/`) while section directories use plural (`ideas/`, `proposals/`). The skill must map between the two.

## 3. Frontmatter Validation

The `kb-frontmatter-validate` skill checks a file's YAML frontmatter against the section's rules:

- **Required fields present** — each section has a mandatory set (e.g., `sources` and `last_audit_date` for knowledge; `sources`, `references`, and `last_audit_date` for research).
- **Field types correct** — `title` must be a string, `tags` an array, `version` an integer, `date` a date string.
- **Status values valid** — the value must be one of the section's lifecycle statuses (e.g., `final` is valid for ADR but not for ideas).
- **Tags in kebab-case** — each tag must be lowercase with hyphens.
- **Dates in YYYY-MM-DD format** — `date`, `last_audit_date`, `date-proposed` must match this format.
- **Template comments removed** — no `<!-- ... -->` blocks may remain in the file.

## 4. Cross-Link Validation

The `kb-cross-link-check` skill verifies that every cross-reference points to an existing path on disk:

| Field | Sections | Check |
|-------|----------|-------|
| `related_ideas` | ideas | Paths exist relative to repository root |
| `sources` (knowledge: path) | research | Knowledge paths exist on disk |
| `sources` (url: URL) | knowledge | URLs are well-formed |
| `references` | research | URLs are well-formed (no path existence check) |
| `related_research` | proposals | Paths exist relative to repository root |
| `related_adrs` | proposals | Paths exist relative to repository root |
| `replaces` | adr | Path exists relative to ADR folder |
| `replaced-by` | adr | Path exists relative to ADR folder |

All checks are strict: a missing path or malformed URL causes a validation failure.

## 5. Status Transition Validation

The `kb-status-transition` skill validates lifecycle moves per section's rules. It accepts the current status, the proposed new status, and the section, then checks against the section's valid lifecycle.

| Section | Valid Lifecycle |
|---------|----------------|
| ideas | `draft` → `exploring` → `proposed` → `accepted` → `completed` / `superseded` |
| knowledge | `draft` → `exploring` → `accepted` → `completed` / `superseded` |
| research | `draft` → `exploring` → `proposed` → `accepted` → `completed` / `superseded` |
| proposals | `draft` → `proposed` → `accepted` → `completed` / `superseded` |
| adr | `draft` → `final` or `cancelled` or `superseded` |

Transitions must follow the directional arrows. Skipping a state (e.g., `draft` → `accepted` in research) is invalid. Terminal states (`completed`, `superseded`, `cancelled`, `final` for ADR) may not transition to any other status.

## 6. Error Handling

All validation skills follow a **fail-and-explain** pattern: they report specific violations and halt, rather than silently continuing or auto-correcting.

Examples of error messages:

- "Missing required field `sources` in frontmatter"
- "Cross-link `knowledge/foo/` does not exist"
- "Status transition `draft → final` is invalid for research (valid: draft → exploring → proposed → accepted → completed / superseded)"
- "Template comments remain in `overview.md`"
- "Tag `MyTag` is not kebab-case (expected `my-tag`)"
- "Date `2026-31-05` is not a valid calendar date (expected YYYY-MM-DD)"

This strict approach ensures agents produce correct content on the first attempt and eliminates silent drift.

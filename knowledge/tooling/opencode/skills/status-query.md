---
title: "Status-Aware Query Discovery Skill"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - discovery
  - status
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Status-Aware Query Discovery Skill

## Purpose

Query the knowledge base with status filters: find all `draft` ideas, recently accepted proposals, superseded ADRs, or any other status-based subset.

## SKILL.md Frontmatter

```yaml
---
name: kb-status-query
description: Query KB content by status field. Supports filtering by status value, section, and date range. Useful for review workflows and audits.
---
```

## When to Invoke

- A user asks "Find all draft ideas" or "What proposals were recently accepted?"
- Before a review session to collect items needing attention.
- Auditing the health of the knowledge base (e.g., too many draft items).
- Checking for superseded documents that may need cleanup.

## Required Tools / Permissions

| Tool | Purpose |
|------|---------|
| `grep` | Extract `status:` lines from frontmatter |
| `glob` | Find all overview.md files by section |
| `read` | Load frontmatter to extract dates, author, and title |
| `skill` (`kb-frontmatter-validate`) | Validate status values against section lifecycle rules |

The SKILL.md should instruct the agent to:

1. Accept a target section (or `*` for all) and one or more status values.
2. Use `grep -r "^status: "` on overview.md files in the target section.
3. For each match, read the file to extract `title`, `author`, and `date` frontmatter fields.
4. Sort results by date descending.
5. Validate all returned status values against the section's allowed lifecycle.

## Example Use Case

A user asks: "Show me all draft knowledge notes that need work."

The agent loads the `kb-status-query` skill and runs:

```
rg "^status: draft" knowledge/ --include "overview.md" -l
```

It reads each matching file's frontmatter and returns a table:

| Title | Author | Date | Path |
|-------|--------|------|------|
| Discovery Skill Patterns | Khalid | 2026-06-06 | `knowledge/tooling/opencode/skills/discovery-patterns.md` |
| Plugin Architecture | Khalid | 2026-05-28 | `knowledge/tooling/opencode/plugins/overview.md` |

The user now has a clear list of items to review.

## See Also

- [Recent Content](recent-content.md) — Find recently created or updated content
- [Pipeline Trace](pipeline-trace.md) — Trace topic lifecycle through the pipeline
- [Discovery Patterns](discovery-patterns.md) — Cross-pattern usage and composition

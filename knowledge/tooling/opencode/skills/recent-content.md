---
title: "Recent Content Query Discovery Skill"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - discovery
  - recent
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Recent Content Query Discovery Skill

## Purpose

Find recently created or updated content across sections. Useful for staying current with team activity and discovering what has changed since the last review.

## SKILL.md Frontmatter

```yaml
---
name: kb-recent
description: Find recently created or modified KB content. Filters by date range, section, and author. Uses git log and frontmatter date fields.
---
```

## When to Invoke

- The user asks "What's new?" or "What changed this week?"
- Onboarding to catch up on recent team activity.
- Before a sync meeting to prepare a summary of recent additions.

## Required Tools / Permissions

| Tool | Purpose |
|------|---------|
| `bash` (git) | `git log --diff-filter=AM --name-only --since=` for recently changed files |
| `grep` | Extract frontmatter `date` fields |
| `glob` | Discover files by section |
| `read` | Load content of recent files |

The SKILL.md should instruct the agent to:

1. Use `git log` with `--diff-filter=AM` (added or modified) and `--since` to find recently changed markdown files.
2. For each file, read its frontmatter `date` field for the authoritative creation date.
3. Group results by section and sort by date descending.
4. Exclude template files and AGENTS.md / README.md index files.
5. Return a summary with file path, title, date, and author.

### Alternative (No Git)

If git history is unavailable or unreliable, fall back to scanning frontmatter `date` fields across all overview.md files, sorted by date descending.

## Example Use Case

A user asks: "What has been added to the knowledge base this week?"

The agent loads the `kb-recent` skill and runs:

```bash
git log --diff-filter=AM --since="7 days ago" --name-only --format="" -- "*.md" \
  | grep -v "AGENTS.md\|README.md\|templates/"
```

It reads each result's title and date from frontmatter, and returns:

| File | Title | Date | Author |
|------|-------|------|--------|
| `knowledge/tooling/opencode/skills/discovery-patterns.md` | Discovery Skill Patterns | 2026-06-06 | Khalid |
| `research/skill-discovery-analysis/overview.md` | Analysis of Discovery Methods | 2026-06-04 | Khalid |

The user has a clear picture of the week's additions.

## See Also

- [Status Query](status-query.md) — Filter content by status
- [Full-Text Search](full-text-search.md) — Search by keyword
- [Discovery Patterns](discovery-patterns.md) — Cross-pattern usage and composition

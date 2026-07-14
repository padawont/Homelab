---
title: "Full-Text Search Discovery Skill"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - discovery
  - search
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Full-Text Search Discovery Skill

## Purpose

Search across all knowledge base content for a given term or phrase, with section-level filtering and result ranking.

## SKILL.md Frontmatter

```yaml
---
name: kb-search
description: Search across all KB markdown files by term, filter by section, return ranked results. Uses grep and glob for content discovery.
---
```

## When to Invoke

- The agent needs to find all occurrences of a concept, API name, or pattern across sections.
- The user asks a question like "What does this codebase say about X?"
- The agent needs to verify whether a topic already exists before creating new content.

## Required Tools / Permissions

| Tool | Purpose |
|------|---------|
| `grep` / `rg` | Pattern search across file contents |
| `glob` | File discovery by name pattern |
| `read` | Load matched files for context |

No special permissions beyond the default tool set. The SKILL.md should instruct the agent to:

1. Use `grep` with the search term across `**/*.md` files.
2. If the result set is large, filter by section path prefix (e.g., `knowledge/`, `ideas/`, `research/`).
3. For ranking, prioritize exact title matches in frontmatter, then heading matches, then body matches.
4. Return results grouped by section with file paths and match counts.

## Example Use Case

A user asks: "What do we know about plugin architecture in OpenCode?"

The agent loads the `kb-search` skill and runs:

```
rg -l "plugin" knowledge/ ideas/ research/
```

Results show matches in `knowledge/tooling/opencode/plugins/`, `ideas/plugin-system/`, and `research/plugin-ecosystem/`. The agent reads the overview files and summarizes current knowledge.

## See Also

- [Cross-Reference](cross-reference.md) — Follow frontmatter cross-links between sections
- [Pipeline Trace](pipeline-trace.md) — Trace a topic through the content pipeline
- [Discovery Patterns](discovery-patterns.md) — Cross-pattern usage and composition

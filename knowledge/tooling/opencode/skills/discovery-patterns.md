---
title: "Discovery Skill Patterns"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - discovery
  - patterns
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Discovery Skill Patterns

## Overview

Discovery skills are a class of OpenCode agent skills designed for searching, tracing, and querying content across a knowledge base. In a repository like the RunicEngines knowledge-base, where content is organized into interconnected sections (ideas, knowledge, research, proposals, ADRs), discovery skills give agents the ability to find relevant information, follow cross-references, and understand how topics flow through the content pipeline.

## Cross-Pattern Usage Notes

### Combining Patterns

The five patterns are designed to compose. Common combinations:

| Combination | Use Case |
|-------------|----------|
| Full-Text Search + Cross-Reference | Find a concept, then map all its relationships |
| Pipeline Trace + Status Query | Trace a topic through the pipeline, filtering to accepted or completed items |
| Recent Content + Status Query | Find recently created drafts that need review |
| Cross-Reference + Pipeline Trace | Build the full dependency graph for a topic including status metadata |

Discovery skills and workflow skills are complementary and can be composed — for example, a pipeline trace discovery followed by an issue-to-plan workflow. See [`workflow-patterns.md`](./workflow-patterns.md) for the companion workflow pattern catalogue.

### Shared Tool Dependencies

All five patterns depend on a common set of tools. A discovery skill suite should verify these are available:

- `grep` / `rg` — content and frontmatter search
- `glob` — file discovery
- `read` — frontmatter and content extraction
- `bash` — git operations (for `kb-recent`)

### Existing Skill Implementations

Several knowledge-base-specific skills already exist in the repository under `.opencode/skills/`, including `kb-frontmatter-validate`, `kb-cross-link-check`, and `kb-scaffold-topic`. Note the distinction between `kb-cross-link-check` (validates that cross-link paths resolve to existing files or URLs) and the `kb-cross-ref` pattern described above (builds a content relationship graph by following cross-links between topics). The former is a pass/fail validation; the latter is a graph construction and discovery operation.

### Permission Requirements

None of the discovery patterns require special permissions in `opencode.json`. They operate entirely through the agent's existing tool set. If the agent has file read access to the repository, all five patterns are usable.

### Skill File Placement

Following OpenCode discovery rules, discovery skills should be placed at:

```
.opencode/skills/kb-search/SKILL.md
.opencode/skills/kb-cross-ref/SKILL.md
.opencode/skills/kb-pipeline-trace/SKILL.md
.opencode/skills/kb-status-query/SKILL.md
.opencode/skills/kb-recent/SKILL.md
```

Each skill name must match the directory name and follow the `^[a-z0-9]+(-[a-z0-9]+)*$` naming convention.

## See Also

- [Full-Text Search](full-text-search.md) — Search across all KB content
- [Cross-Reference](cross-reference.md) — Follow frontmatter cross-links
- [Pipeline Trace](pipeline-trace.md) — Trace topic through content pipeline
- [Status Query](status-query.md) — Query by status field
- [Recent Content](recent-content.md) — Find recently created or modified content
- [Workflow Patterns](workflow-patterns.md) — Companion workflow skill catalogue
- [Tool Mechanism](tool-mechanism.md) — How skills are discovered and loaded

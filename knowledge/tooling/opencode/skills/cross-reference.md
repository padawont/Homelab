---
title: "Cross-Reference Lookup Discovery Skill"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - discovery
  - cross-reference
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Cross-Reference Lookup Discovery Skill

## Purpose

Given a topic, find all related content across sections by following frontmatter cross-link fields.

## SKILL.md Frontmatter

```yaml
---
name: kb-cross-ref
description: Follow frontmatter cross-links (sources, related_ideas, related_research, related_adrs) to build a graph of related content across KB sections.
---
```

## When to Invoke

- The agent needs to understand the full context around a topic.
- A user asks "What is this related to?" or "What depends on this?"
- Before modifying or superseding content, to identify all dependents.

## Required Tools / Permissions

| Tool | Purpose |
|------|---------|
| `grep` | Search frontmatter blocks for cross-link field names |
| `glob` | Discover markdown files by section |
| `read` | Load frontmatter of candidate files |
| `skill` (`kb-cross-link-check`) | Validate that cross-link paths resolve |

The SKILL.md should instruct the agent to:

1. Start from a target file or topic folder.
2. Read its frontmatter to collect `sources`, `related_ideas`, `related_research`, `related_adrs`, and `replaces`/`replaced-by` fields.
3. For each relative path, resolve it against the repo root and load the target's frontmatter.
4. Build a directed graph: topic --> related topics.
5. Optionally invert: search the whole KB for files whose frontmatter references the starting topic.

## Example Use Case

A user asks: "What research and proposals are related to the OpenCode skills knowledge note?"

The agent loads the `kb-cross-ref` skill, starts from `knowledge/tooling/opencode/skills/overview.md`, and reads its frontmatter. It finds no `related_research` or `related_ideas` fields directly. It then inverts the search, running:

```
rg "tooling/opencode/skills" proposals/ research/ ideas/
```

This reveals references in `proposals/skill-system/overview.md` and `research/skill-discovery/overview.md`, providing the user with the full relationship map.

## See Also

- [Full-Text Search](full-text-search.md) — Find content by keyword
- [Pipeline Trace](pipeline-trace.md) — Trace through Idea -> Knowledge -> Research -> Proposal -> ADR
- [Discovery Patterns](discovery-patterns.md) — Cross-pattern usage and composition

---
title: "Pipeline Tracing Discovery Skill"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - discovery
  - pipeline
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Pipeline Tracing Discovery Skill

## Purpose

Trace a topic through the content pipeline: Idea -> Knowledge -> Research -> Proposal -> ADR. Follow cross-links to build a dependency graph showing how a concept evolves.

## SKILL.md Frontmatter

```yaml
---
name: kb-pipeline-trace
description: Trace a topic through the Idea -> Knowledge -> Research -> Proposal -> ADR pipeline by following frontmatter cross-links and section conventions.
---
```

## When to Invoke

- The user wants to see the full lifecycle of a concept.
- The agent needs to understand what decisions have been made and what research supports them.
- Auditing or reviewing a topic's completeness (e.g., does every proposal have supporting research?).

## Required Tools / Permissions

| Tool | Purpose |
|------|---------|
| `grep` | Search for topic mentions across sections |
| `glob` | Discover topic folders |
| `read` | Load frontmatter and content |
| `skill` (`kb-cross-link-check`) | Validate cross-link resolution |

The SKILL.md should instruct the agent to:

1. Identify the starting topic and determine which section it belongs to (ideas, knowledge, research, proposal, adr).
2. Based on the section, know which forward links to expect:

   | Section | Forward Links To |
   |---------|-----------------|
   | Idea | No mandated forward links; may become knowledge or research |
   | Knowledge | `sources` in research notes reference knowledge paths |
   | Research | `related_research` in proposals; `sources` in research link to knowledge |
   | Proposal | `related_research`, `related_adrs` |
   | ADR | `replaces`, `replaced-by` (other ADRs) |

3. Follow each link recursively, recording the path.
4. Return the chain as a linear or branching diagram.

## Example Use Case

A user asks: "Trace the topic 'skill system permissions' through the pipeline."

The agent loads the `kb-pipeline-trace` skill and discovers:

- **Idea**: `ideas/skill-permissions/` (first proposal of the concept)
- **Knowledge**: `knowledge/tooling/opencode/skills/configuration.md` (documents the permission model)
- **Research**: `research/skill-permissions-analysis/` (evaluates permission design options, `sources` references the knowledge note)
- **Proposal**: `proposals/permission-model-v2/` (proposes changes, `related_research` points to the research note)
- **ADR**: `adr/0005-permission-model.md` (records the final decision, `replaces` references the old ADR)

This gives the user a complete picture of how the permissions concept evolved.

## See Also

- [Cross-Reference](cross-reference.md) — Build relationship graphs for a topic
- [Status Query](status-query.md) — Filter pipeline items by status
- [Discovery Patterns](discovery-patterns.md) — Cross-pattern usage and composition

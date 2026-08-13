# AGENTS.md — 01_Ideas

Raw, unstructured concept capture. Low friction — just enough context to remember.

## Why have ideas?

To capture every thought about the homelab before it's lost. Ideas are the seed of the pipeline — no idea is too small or too vague.

## When to create

Any thought about new tech, homelab changes, or wishlist items.

## Status Lifecycle

```
draft → accepted
  L__> archived → (move to 06_Archive/ideas/)
```

- **draft**: Just captured
- **accepted**: Worth pursuing
- **archived**: Discarded or superseded

## File system layout

```
01_Ideas/{topic}/
├── idea-{name}.md     # one per specific idea
├── idea-notes.md      # scratchpad, raw thoughts, links
└── overview.md        # high-level summary of the topic area
```

All names in kebab-case. Multiple files per topic allowed. Use the atomic rule (150 lines) to decide when to split.

## Frontmatter (required)

```yaml
---
title: ""
status: draft        # draft | accepted | archived
author: ""
date: YYYY-MM-DD
tags: []
technologies: []
related_ideas: []
---
```

Example:

```yaml
---
title: "Move databases to separate node"
status: draft
author: "padawont"
date: 2026-08-13
tags: [databases, performance, architecture]
technologies: [postgresql, mysql, mariadb]
related_ideas: []
---
```

See `./Templates/ideas/idea.md` for a copyable template.

## Structure

No strict structure — freeform markdown. The template provides a starting point.

## Conventions

- No formal review needed for `draft → accepted`
- No stale timeout — ideas live indefinitely
- When `accepted`, the idea is ready — optionally create a Knowledge note
- Use `idea-notes.md` for loose thoughts that don't warrant their own file

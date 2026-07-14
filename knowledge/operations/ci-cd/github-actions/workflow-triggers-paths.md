---
title: "Workflow Path Triggers"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - triggers
  - paths
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#onpushpull_requestpull_request_targetpathspaths-ignore"
    title: "GitHub Actions: Filter by paths"
last_audit_date: 2026-06-09
---

# Workflow Path Triggers

Use `paths` and `paths-ignore` to run workflows only when specific files change.

## Syntax

```yaml
on:
  push:
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
      - "uv.lock"
  pull_request:
    paths-ignore:
      - "docs/**"
      - "*.md"
      - ".gitignore"
```

## Rules

- `paths` — workflow runs only if at least one path matches
- `paths-ignore` — workflow runs unless all changes match ignored paths
- Patterns use [glob syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#filter-pattern-cheat-sheet)
- `!` prefix negates a pattern

## Example: Python CI Only

```yaml
on:
  push:
    paths:
      - "**.py"
      - "pyproject.toml"
      - "uv.lock"
      - ".github/workflows/ci.yml"
```

## Limitations

- Path filters do NOT affect what is checked out — use `actions/checkout` with `fetch-depth: 0` if you need the full history
- A workflow is skipped entirely if no paths match (job won't show as failed)

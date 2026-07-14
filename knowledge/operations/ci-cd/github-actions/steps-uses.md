---
title: "Steps: uses (Actions Reference)"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - steps
  - actions
  - checkout
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsuses"
    title: "GitHub Actions: steps.uses"
last_audit_date: 2026-06-09
---

# Steps: uses (Actions Reference)

The `uses` keyword references an action to run as a step.

## Common Actions

```yaml
steps:
  # Checkout repository
  - uses: actions/checkout@v6
    with:
      fetch-depth: 0

  # Setup Python via uv
  - uses: astral-sh/setup-uv@v8.2.0

  # Setup Node.js
  - uses: actions/setup-node@v6
    with:
      node-version: 22

  # Cache dependencies
  - uses: actions/cache@v5
    with:
      path: ~/.cache/uv
      key: uv-${{ hashFiles('uv.lock') }}
```

## Action Source Types

| Format | Example | Description |
|---|---|---|
| `{owner}/{repo}@{ref}` | `actions/checkout@v6` | Public GitHub repository |
| `{owner}/{repo}/{path}@{ref}` | `org/actions/.github/actions/my-action@v1` | Action in subdir |
| `./path/to/action` | `./.github/actions/local-action` | Local action |
| `docker://{image}:{tag}` | `docker://alpine:latest` | Docker Hub |

## Pinning Versions

- Pin to a release tag (`@v6`) for stability
- Pin to a full SHA (`@abc123def456`) for maximum security
- Avoid `@main` or `@master` in production workflows

## See Also

- [steps-run.md](./steps-run.md) — Run shell commands in steps
- [actions-marketplace.md](./actions-marketplace.md) — Finding actions

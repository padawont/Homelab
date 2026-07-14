---
title: "Custom GITHUB_TOKEN Permissions"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - token
  - permissions
sources:
  - url: "https://docs.github.com/en/actions/tutorials/authenticate-with-github_token"
    title: "GitHub Actions: Authenticate with GITHUB_TOKEN"
last_audit_date: 2026-06-09
---

# Custom GITHUB_TOKEN Permissions

Use the `permissions` block to restrict what the `GITHUB_TOKEN` can do.

## Workflow-Level Permissions

```yaml
name: CI
on: push

permissions:
  contents: read
  pull-requests: write
  issues: none

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
```

## Job-Level Permissions

Override workflow-level permissions for specific jobs:

```yaml
jobs:
  lint:
    permissions:
      contents: read
    runs-on: ubuntu-latest
    steps:
      - run: uv run ruff check

  release:
    permissions:
      contents: write    # Needed to create release
      packages: write    # Needed to push Docker image
    runs-on: ubuntu-latest
    steps:
      - run: uv run release
```

## Permission Values

| Value | Meaning |
|---|---|
| `none` | No access |
| `read` | Read-only access |
| `write` | Read and write access |

## Using a Personal Access Token (PAT)

When `GITHUB_TOKEN` doesn't have enough scope (e.g., cross-repo access):

```yaml
steps:
  - env:
      GH_TOKEN: ${{ secrets.MY_PAT }}
    run: gh pr create
```

## Best Practice

Always set `permissions: read-all` at the workflow level, then grant `write` only to jobs that need it (principle of least privilege).

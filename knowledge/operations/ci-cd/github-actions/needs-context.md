---
title: "needs Context"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - context
  - needs
  - dependencies
sources:
  - url: "https://docs.github.com/en/actions/learn-github-actions/contexts#needs-context"
    title: "GitHub Actions: needs Context"
last_audit_date: 2026-06-09
---

# needs Context

The `needs` context provides access to outputs and results of dependency jobs.

## Basic Usage

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - id: version
        run: echo "version=1.2.3" >> "$GITHUB_OUTPUT"

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying ${{ needs.build.outputs.version }}"
```

## Accessing Job Results

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
  test:
    needs: lint
    runs-on: ubuntu-latest
  notify:
    if: always()
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "lint result: ${{ needs.lint.result }}"
          echo "test result: ${{ needs.test.result }}"
```

## Key Fields

| Expression | Type | Description |
|---|---|---|
| `needs.<job>.outputs.<name>` | string | Job output value |
| `needs.<job>.result` | string | `success`, `failure`, `cancelled`, or `skipped` |

## Rules

- The current job must list the dependency in `needs:`
- Outputs are strings only (max 1 MB per job)
- Use `needs.<job>.result` to implement custom orchestration

## See Also

- [jobs-outputs.md](./jobs-outputs.md) — Defining job outputs
- [jobs-needs.md](./jobs-needs.md) — Job dependencies

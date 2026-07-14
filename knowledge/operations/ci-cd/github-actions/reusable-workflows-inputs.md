---
title: "Reusable Workflow Inputs"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - reusable-workflows
  - inputs
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/reusing-workflows#using-inputs-and-outputs-in-a-reusable-workflow"
    title: "GitHub Actions: Reusable Workflow Inputs"
last_audit_date: 2026-06-09
---

# Reusable Workflow Inputs

Pass data to reusable workflows using `inputs`.

## Defining Inputs

```yaml
# .github/workflows/ci.yml
name: CI Pipeline
on:
  workflow_call:
    inputs:
      python-version:
        description: "Python version to use"
        required: false
        default: "3.13"
        type: string
      run-lint:
        description: "Run linting step"
        required: false
        default: true
        type: boolean
      timeout:
        required: false
        default: 15
        type: number
```

## Using Inputs in the Called Workflow

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: astral-sh/setup-uv@v8.2.0
        with:
          python-version: ${{ inputs.python-version }}
      - if: inputs.run-lint
        run: uv run ruff check
```

## Calling with Inputs

```yaml
jobs:
  ci:
    uses: ./.github/workflows/ci.yml
    with:
      python-version: "3.12"
      run-lint: false
```

## Input Types

| Type | YAML Example | Notes |
|---|---|---|
| `string` | `"hello"` | Default type |
| `boolean` | `true` / `false` | Conditional logic |
| `number` | `42` | Integer or float |
| `choice` | N/A | Not supported directly |

## See Also

- [reusable-workflows-intro.md](./reusable-workflows-intro.md) — Overview
- [reusable-workflows-secrets.md](./reusable-workflows-secrets.md) — Passing secrets

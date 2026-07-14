---
title: "Matrix with Reusable Workflows"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - reusable-workflows
  - matrix
  - strategy
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/reusing-workflows#using-a-matrix-strategy-with-a-reusable-workflow"
    title: "GitHub Actions: Matrix with Reusable Workflows"
last_audit_date: 2026-06-10
---

# Matrix with Reusable Workflows

Call a reusable workflow with a matrix strategy.

## Calling Workflow

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python: ["3.12", "3.13"]
    uses: ./.github/workflows/test-job.yml
    with:
      os: ${{ matrix.os }}
      python-version: ${{ matrix.python }}
```

## Reusable Workflow

```yaml
# .github/workflows/test-job.yml
name: Test Job
on:
  workflow_call:
    inputs:
      os:
        required: true
        type: string
      python-version:
        required: true
        type: string

jobs:
  run:
    runs-on: ${{ inputs.os }}
    steps:
      - uses: astral-sh/setup-uv@v8.2.0
        with:
          python-version: ${{ inputs.python-version }}
      - run: uv run pytest
```

## Limitations

- The `runs-on` value MUST be a string (cannot use the matrix directly in `runs-on` for the calling job — use `with:`)
- Each matrix combination creates a separate call
- Naming convention: `jobs.<job_id>.name` helps identify variants

```yaml
jobs:
  test:
    name: "${{ matrix.os }} / Python ${{ matrix.python }}"
    strategy:
      matrix:
        os: [ubuntu-latest]
        python: ["3.12", "3.13"]
    uses: ./.github/workflows/test-job.yml
    with:
      os: ${{ matrix.os }}
      python-version: ${{ matrix.python }}
```

## See Also

- [jobs-strategy-matrix.md](./jobs-strategy-matrix.md) — Matrix strategy
- [reusable-workflows-intro.md](./reusable-workflows-intro.md) — Reusable workflows overview

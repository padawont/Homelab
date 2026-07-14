---
title: "Step Working Directory"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - steps
  - working-directory
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsworking-directory"
    title: "GitHub Actions: steps.working-directory"
last_audit_date: 2026-06-10
---

# Step Working Directory

Use `working-directory` to specify which directory a step runs in.

## Basic Usage

```yaml
steps:
  - uses: actions/checkout@v6

  - name: Install frontend
    working-directory: frontend
    run: npm ci

  - name: Run backend tests
    working-directory: backend
    run: uv run pytest
```

## With Defaults

Set a default for all steps in a job:

```yaml
jobs:
  test:
    defaults:
      run:
        working-directory: ./backend
    steps:
      - uses: actions/checkout@v6
      - run: uv sync          # Runs in ./backend
      - run: uv run pytest    # Runs in ./backend
```

## Override on Specific Steps

```yaml
defaults:
  run:
    working-directory: ./backend
steps:
  - run: uv run pytest   # Backend tests
  - name: Install infra
    working-directory: ./infra
    run: terraform plan   # Runs in ./infra
```

## Key Points

- Path is relative to `$GITHUB_WORKSPACE` (the repo root)
- Directory must exist before the step runs
- Works only with `run:` steps, not `uses:`

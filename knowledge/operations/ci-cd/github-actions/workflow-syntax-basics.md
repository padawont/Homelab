---
title: "Workflow Syntax Basics"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - workflow-syntax
  - yaml
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions"
    title: "GitHub Actions: Workflow Syntax"
last_audit_date: 2026-06-09
---

# Workflow Syntax Basics

A workflow is a YAML file in `.github/workflows/` that defines automated processes.

## Minimal Structure

```yaml
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: echo "Hello, world!"
```

## Top-Level Keys

| Key | Required | Description |
|---|---|---|
| `name` | No | Display name in the Actions tab |
| `on` | Yes | Event(s) that trigger the workflow |
| `jobs` | Yes | Map of job definitions |
| `env` | No | Default environment variables for all jobs |
| `defaults` | No | Default settings for all jobs |
| `concurrency` | No | Concurrency control across runs |
| `run-name` | No | Display name for workflow runs from the Actions tab |
| `permissions` | No | Default permissions for the `GITHUB_TOKEN` |

## Naming Convention

Use `kebab-case` for workflow filenames. Each workflow file should have a single responsibility.

## See Also

- [workflow-triggers.md](./workflow-triggers.md) — Trigger events
- [jobs-runners.md](./jobs-runners.md) — Runner configuration
- [steps-run.md](./steps-run.md) — Shell command steps

---
title: "Job Concurrency"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - concurrency
  - jobs
sources:
  - url: "https://docs.github.com/en/actions/using-jobs/using-concurrency"
    title: "GitHub Actions: Concurrency"
last_audit_date: 2026-06-09
---

# Job Concurrency

Use `concurrency` to limit concurrent runs and cancel redundant work.

## Basic Usage

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

This ensures only one run per branch. A new push cancels the in-progress run.

## Environment Deployments

```yaml
concurrency:
  group: deploy-${{ github.ref_name }}
  cancel-in-progress: false
```

Prevents simultaneous deploys to the same environment without cancelling.

## Workflow-Level vs Job-Level

Use `concurrency` at the workflow level (top of file) to cancel redundant CI:

```yaml
# .github/workflows/ci.yml
name: CI
on: push
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Per-job concurrency is useful for deployment steps where you want serial execution.

## Key Points

- `cancel-in-progress: true` cancels any running job in the same group
- If not cancelled, the queued run waits for the running run to finish
- Concurrency groups are scoped to the repository

---
title: "github Context"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - context
  - github
sources:
  - url: "https://docs.github.com/en/actions/learn-github-actions/contexts#github-context"
    title: "GitHub Actions: github Context"
last_audit_date: 2026-06-09
---

# github Context

The `github` context contains metadata about the workflow run and the event that triggered it.

## Common Fields

```yaml
jobs:
  example:
    steps:
      - run: |
          echo "Repository: ${{ github.repository }}"
          echo "Branch: ${{ github.ref_name }}"
          echo "SHA: ${{ github.sha }}"
          echo "Actor: ${{ github.actor }}"
          echo "Workflow: ${{ github.workflow }}"
          echo "Run ID: ${{ github.run_id }}"
          echo "Run Number: ${{ github.run_number }}"
```

## Field Reference

| Field | Type | Description |
|---|---|---|
| `github.repository` | string | `owner/repo` |
| `github.repository_owner` | string | Repository owner |
| `github.ref` | string | Full ref (e.g., `refs/heads/main`) |
| `github.ref_name` | string | Short ref name (e.g., `main`) |
| `github.ref_type` | string | `branch` or `tag` |
| `github.sha` | string | Commit SHA |
| `github.actor` | string | User who triggered run |
| `github.event_name` | string | Event type (e.g., `push`) |
| `github.workflow` | string | Workflow name |
| `github.run_id` | string | Unique run ID |
| `github.run_number` | string | Run number (increments per workflow) |
| `github.token` | string | `GITHUB_TOKEN` value |
| `github.job` | string | The `job_id` of the current job |

## Accessing Event Payload

```yaml
steps:
  - run: |
      echo "PR title: ${{ github.event.pull_request.title }}"
      echo "PR number: ${{ github.event.number }}"
```

## See Also

- [env-context.md](./env-context.md) — env context
- [needs-context.md](./needs-context.md) — needs context
- [vars-context.md](./vars-context.md) — vars context

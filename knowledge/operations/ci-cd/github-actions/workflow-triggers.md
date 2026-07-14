---
title: "Workflow Triggers"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - triggers
  - events
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows"
    title: "GitHub Actions: Events That Trigger Workflows"
last_audit_date: 2026-06-09
---

# Workflow Triggers

The `on` key defines which events start the workflow.

## Common Triggers

```yaml
# Branch push
on: push

# Pull request events
on: pull_request

# Multiple triggers
on: [push, pull_request]

# Schedule (cron)
on:
  schedule:
    - cron: "0 6 * * 1"   # Every Monday at 06:00 UTC

# Manual trigger with inputs
on:
  workflow_dispatch:
    inputs:
      environment:
        description: "Target environment"
        required: true
        default: staging
```

## Activity Types

Many events support `types:` to filter on activity subtypes (see [workflow-triggers-types.md](./workflow-triggers-types.md)).

## Path Filtering

Add `paths:` or `paths-ignore:` to limit triggers to specific files (see [workflow-triggers-paths.md](./workflow-triggers-paths.md)).

## Best Practices

- Use `workflow_dispatch` for manual deployments
- Use `schedule` for periodic maintenance (dependency bumps, cache refresh)
- Combine `push` and `pull_request` for CI
- Only trigger on branches that need it

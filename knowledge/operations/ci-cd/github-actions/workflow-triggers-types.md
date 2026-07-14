---
title: "Workflow Trigger Activity Types"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - triggers
  - events
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request"
    title: "GitHub Actions: pull_request activity types"
last_audit_date: 2026-06-09
---

# Workflow Trigger Activity Types

Many events support activity `types:` to filter on specific actions.

## pull_request Types

```yaml
on:
  pull_request:
    types: [opened, synchronize, labeled, unlabeled, closed]
```

| Type | When it Fires |
|---|---|
| `opened` | A new PR is created |
| `synchronize` | Commits are pushed to the PR branch |
| `labeled` / `unlabeled` | A label is added or removed |
| `ready_for_review` | Draft PR is marked ready |
| `review_requested` | A reviewer is requested |
| `closed` | PR is closed (merged or not) |

## issue_comment Types

```yaml
on:
  issue_comment:
    types: [created, edited, deleted]
```

Useful for running agents on issue comments (see [opencode-agent-issue-comment.md](./opencode-agent-issue-comment.md)).

## workflow_dispatch

No `types:` — use `inputs:` instead for parameterisation.

## Best Practice

Always specify `types:` when using `pull_request` to avoid duplicate runs. Opening a PR fires `opened`, pushing commits fires `synchronize`.

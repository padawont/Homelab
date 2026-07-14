---
title: "Job Timeout"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - jobs
  - timeout
sources:
  - url: "https://docs.github.com/en/actions/using-jobs/using-jobs-in-a-workflow#timeout-minutes"
    title: "GitHub Actions: timeout-minutes"
last_audit_date: 2026-06-09
---

# Job Timeout

Use `timeout-minutes` to prevent jobs from running indefinitely.

## Default Timeouts

- **GitHub-hosted runners**: 360 minutes (6 hours) per job
- **Self-hosted runners**: 360 minutes (same default, configurable per job)
  > Note: There is also a hard **execution limit** of 7200 minutes (5 days) for self-hosted runners and 360 minutes (6 hours) for GitHub-hosted runners — this is separate from the `timeout-minutes` default.

## Setting Timeout

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: astral-sh/setup-uv@v8.2.0
      - run: uv run pytest

  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - run: echo "Deploying..."
```

## Best Practices

- Set reasonable timeouts to save runner minutes
- Use 10–15 minutes for standard CI jobs
- Use 30–60 minutes for long-running integration tests
- Always set a timeout for jobs that call external APIs
- Timeouts apply per job or per step — set `timeout-minutes` at the step level for granular control

## Cancellation Behavior

When a job times out, all running steps are cancelled and the job is marked as cancelled (not failed). Dependent jobs that check for `failure()` will **not** trigger — a cancelled job does not count as a failure. Use `cancelled()` or `always()` instead to handle cancelled jobs.

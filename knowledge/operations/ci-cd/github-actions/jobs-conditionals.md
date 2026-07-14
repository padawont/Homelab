---
title: "Job Conditionals (if:)"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - jobs
  - conditionals
  - expressions
sources:
  - url: "https://docs.github.com/en/actions/using-jobs/using-conditions-to-control-job-execution"
    title: "GitHub Actions: Conditional Job Execution"
last_audit_date: 2026-06-10
---

# Job Conditionals (if:)

Use `if:` to conditionally run a job based on an expression.

## Basic Conditionals

```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to production"

  notify:
    if: failure()
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deployment failed"
```

## Status Check Functions

A default status check of `success()` is automatically applied to any `if:` condition that does not explicitly include a status check function. To override this default, include one of the functions below in your expression.

| Expression | Description |
|---|---|
| `success()` | At the job level: returns `true` when all jobs listed in `needs` have succeeded (checks dependencies, not "previous steps"). At the step level: returns `true` when all prior steps in the same job have succeeded. This is the **default** status check — if no status function is used, `success()` is implied. |
| `failure()` | At the step level: returns `true` when any previous step in the same job has failed. At the job level in a chain of dependent jobs (`needs`): returns `true` if **any ancestor job** (transitive dependency) has failed. |
| `always()` | Always runs, returning `true` even when the workflow is cancelled. Use sparingly — see warning below. |
| `cancelled()` | Returns `true` if the workflow was cancelled. |

> **WARNING**: Avoid using `always()` for tasks that could suffer from a critical failure (e.g., checking out sources), or the workflow may hang until timeout. If your intent is to "run regardless of success or failure" but **not** when cancelled, use `if: ${{ !cancelled() }}` instead. This is the recommended alternative per the official GitHub documentation.

## Common Patterns

```yaml
# Run only on main branch
if: github.ref_name == 'main'

# Run on tag push
if: startsWith(github.ref, 'refs/tags/v')

# Skip for bot commits
if: github.actor != 'dependabot[bot]'

# Run for specific PR labels
if: contains(github.event.pull_request.labels.*.name, 'deploy')
```

## See Also

- [github-context.md](./github-context.md) — github.* field reference
- [steps-if-conditionals.md](./steps-if-conditionals.md) — Step-level conditionals

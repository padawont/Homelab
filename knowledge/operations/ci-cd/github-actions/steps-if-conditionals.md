---
title: "Step Conditionals (if: on Steps)"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - steps
  - conditionals
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsif"
    title: "GitHub Actions: steps.if"
last_audit_date: 2026-06-09
---

# Step Conditionals (if: on Steps)

Use `if:` on individual steps for fine-grained control.

## Common Patterns

```yaml
steps:
  - run: uv run pytest

  - if: failure()
    run: echo "Tests failed"

  - if: success()
    run: echo "Tests passed"

  - if: always()
    run: echo "This always runs (even on cancellation)"
```

## Step-Specific Conditions

```yaml
steps:
  - name: Lint
    run: uv run ruff check

  - name: Deploy to staging
    if: github.ref_name == 'main'
    run: echo "Deploying staging..."

  - name: Deploy to production
    if: startsWith(github.ref, 'refs/tags/v')
    run: echo "Deploying production..."
```

## Referencing Step Outcomes

```yaml
steps:
  - id: build
    continue-on-error: true
    run: uv build

  - if: steps.build.outcome == 'success'
    run: echo "Build succeeded"

  - if: steps.build.outcome == 'failure'
    run: echo "Build failed"
```

## Differences from Job Conditionals

Step conditionals evaluate within the job context. They can reference:
- `steps.<id>.outcome` and `steps.<id>.conclusion`
- `env.*` variables
- `github.*` context

See [jobs-conditionals.md](./jobs-conditionals.md) for job-level equivalents.

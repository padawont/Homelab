---
title: "Reusable Workflows (workflow_call)"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - reusable-workflows
  - workflow-call
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/reusing-workflows"
    title: "GitHub Actions: Reusing Workflows"
last_audit_date: 2026-06-09
---

# Reusable Workflows (workflow_call)

Reusable workflows are called by other workflows using the `uses` keyword at the job level.

## Defining a Reusable Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to ${{ inputs.environment }}"
```

## Calling a Reusable Workflow

```yaml
# .github/workflows/ci.yml
jobs:
  deploy-staging:
    uses: ./.github/workflows/deploy.yml
    with:
      environment: staging

  deploy-production:
    uses: ./.github/workflows/deploy.yml
    with:
      environment: production
```

## Location Rules

- Same repository: `uses: ./.github/workflows/deploy.yml`
- Other repository: `uses: myorg/shared-workflows/.github/workflows/deploy.yml@v1`
- Cross-repo references supported for both public and private repositories (with proper configuration)

## Constraints

- Reusable workflows can call other reusable workflows (nesting supported, max 10 total levels (1 caller + 9 nested))
- The caller's env context values are not propagated to the called workflow (env starts empty in the called workflow)
- The `github` context and `GITHUB_TOKEN` are inherited from the caller workflow

## See Also

- [reusable-workflows-inputs.md](./reusable-workflows-inputs.md) — Inputs
- [reusable-workflows-secrets.md](./reusable-workflows-secrets.md) — Secrets
- [reusable-workflows-strategy.md](./reusable-workflows-strategy.md) — Matrix strategy

---
title: "GHA Environments for Approvals"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - deployment
  - environments
  - approvals
  - gha
sources:
  - url: "https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment"
    title: "GitHub Actions: Using Environments for Deployment"
last_audit_date: 2026-06-09
---

# GHA Environments for Approvals

GitHub Environments provide protected deployment targets with approval gates.

## Environment Setup

Create environments in repo Settings → Environments:

- `staging` — optional review, auto-deploy from main
- `production` — required reviewers, protected branch

## Workflow with Environment

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    environment:
      name: staging
      url: https://staging.app.example.com
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to staging..."

  deploy-production:
    needs: deploy-staging
    environment:
      name: production
      url: https://app.example.com
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to production..."
```

## Protection Rules

| Rule | Description |
|---|---|
| **Required reviewers** | Specific users/teams must approve |
| **Wait timer** | Delay before deployment starts (1-43200 min) |
| **Deployment branches** | Only allow deploys from specific branches |

## Environment Secrets

Each environment has its own secrets:

```yaml
steps:
  - env:
      DB_URL: ${{ secrets.DB_URL }}       # Environment-specific
      API_KEY: ${{ secrets.API_KEY }} # Overrides repo-level secret of same name
    run: uv run deploy
```

## See Also

- [secrets-environment.md](./secrets-environment.md) — Environment secrets
- [deployment-continuous.md](./deployment-continuous.md) — CD patterns

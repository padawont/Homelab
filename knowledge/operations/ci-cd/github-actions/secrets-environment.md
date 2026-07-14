---
title: "Environment-Level Secrets"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - secrets
  - environments
sources:
  - url: "https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment"
    title: "GitHub Actions: Environments"
last_audit_date: 2026-06-09
---

# Environment-Level Secrets

Secrets can be scoped to a deployment environment.

## Setup

Create an environment in GitHub repo Settings → Environments. Then add secrets to that environment.

## Usage in Workflow

```yaml
jobs:
  deploy:
    environment: production
    runs-on: ubuntu-latest
    steps:
      - env:
          DEPLOY_URL: ${{ secrets.DEPLOY_URL }}
          API_KEY: ${{ secrets.API_KEY }}
        run: uv run deploy
```

## Environment Protection Rules

Environments can require:

- **Required reviewers** — approval before deployment
- **Wait timer** — delay before deployment starts
- **Deployment branches and tags** — restrict which branches and tags can deploy (e.g., "No restriction", "Protected branches only", or "Selected branches and tags")

Example with protection:

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://app.example.com
    runs-on: ubuntu-latest
    steps:
      - run: uv run deploy
```

## Best Practices

- Use separate environments for `staging` and `production`
- Environment secrets override repo and org secrets of the same name
- Use [deployment-environments.md](./deployment-environments.md) for deployment patterns

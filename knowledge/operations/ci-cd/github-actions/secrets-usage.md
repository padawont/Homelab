---
title: "Using Secrets in Workflows"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - secrets
  - usage
sources:
  - url: "https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#using-secrets-in-a-workflow"
    title: "GitHub Actions: Accessing Secrets"
last_audit_date: 2026-06-09
---

# Using Secrets in Workflows

Access secrets via the `${{ secrets }}` context.

## Basic Syntax

```yaml
steps:
  - name: Deploy
    env:
      DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
      API_TOKEN: ${{ secrets.API_TOKEN }}
    run: |
      echo "$DEPLOY_KEY" > deploy_key.pem
      uv run deploy --token "$API_TOKEN"
```

## Passing to Actions

```yaml
steps:
  - name: Docker login
    uses: docker/login-action@v4
    with:
      username: ${{ secrets.DOCKER_USER }}
      password: ${{ secrets.DOCKER_TOKEN }}
```

## Passing to Reusable Workflows

```yaml
jobs:
  deploy:
    uses: ./.github/workflows/deploy.yml
    secrets:
      deploy_key: ${{ secrets.DEPLOY_KEY }}
```

See [reusable-workflows-secrets.md](./reusable-workflows-secrets.md).

## Important Rules

- Secrets are automatically masked in log output
- Avoid passing secrets via `run:` inline. If necessary, use proper shell quoting to prevent exposure. — prefer `env:` or action `with:`
- Secrets (except GITHUB_TOKEN) are NOT passed to the runner when a workflow is triggered from a forked repository.
- Max secret size: 48 KB
- Names are case-insensitive and must not start with `GITHUB_`

---
title: "Reusable Workflow Secrets"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - reusable-workflows
  - secrets
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/reusing-workflows#using-secrets-in-a-reusable-workflow"
    title: "GitHub Actions: Secrets in Reusable Workflows"
last_audit_date: 2026-06-09
---

# Reusable Workflow Secrets

Pass secrets to reusable workflows using the `secrets` keyword.

## Defining Expected Secrets

```yaml
# .github/workflows/deploy.yml
on:
  workflow_call:
    secrets:
      cloud-api-key:
        description: "Cloud provider API key"
        required: true
      docker-token:
        description: "Docker registry token"
        required: false
```

## Using Secrets Inside

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - env:
          API_KEY: ${{ secrets.cloud-api-key }}
        run: uv run deploy --api-key "$API_KEY"
```

## Passing Secrets from Caller

```yaml
jobs:
  deploy:
    uses: ./.github/workflows/deploy.yml
    secrets:
      cloud-api-key: ${{ secrets.PROD_API_KEY }}
      docker-token: ${{ secrets.DOCKER_TOKEN }}
```

## Passing All Secrets

```yaml
jobs:
  deploy:
    uses: ./.github/workflows/deploy.yml
    secrets: inherit
```

## Important Notes

- Secrets must be explicitly listed in `workflow_call.secrets` (except when using `secrets: inherit`, which passes all inherited secrets automatically)
- Use `secrets: inherit` to pass all caller secrets (use sparingly)
- Each secret is limited to 48 KB ([source](https://docs.github.com/en/actions/reference/secrets-reference#limits-for-secrets))
- Secrets are masked in logs even when passed through reusable workflows

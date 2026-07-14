---
title: "Organization vs Repository Secrets"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - secrets
  - organization
  - repository
sources:
  - url: "https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository"
    title: "GitHub Actions: Creating Secrets"
  - url: "https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-an-organization"
    title: "GitHub Actions: Organization Secrets"
last_audit_date: 2026-06-10
---

# Organization vs Repository Secrets

Secrets can be defined at the repository or organization level.

## Repository Secrets

```bash
# Create via GitHub CLI
gh secret set DEPLOY_KEY --repo myorg/myapp --body "$(cat deploy_key.pem)"
```

- Scoped to a single repository
- Managed in repo Settings → Secrets and variables → Actions
- Each repo has its own set

## Organization Secrets

```bash
# Create org-level secret
gh secret set ORG_DOCKER_TOKEN --org myorg --body "$DOCKER_TOKEN"
```

- Available to all (or selected) repositories in the organization
- Managed in org Settings → Secrets and variables → Actions
- Can limit access to specific repos

## Resolution Order

1. Environment secrets (highest priority)
2. Repository secrets
3. Organization secrets (lowest priority)

If the same secret name exists at multiple levels, the more specific one wins.

## Best Practices

- Put shared tokens (npm token, Docker Hub) at org level
- Put repo-specific secrets (deploy keys, service accounts) at repo level
- Use [secrets-environment.md](./secrets-environment.md) for environment-specific secrets

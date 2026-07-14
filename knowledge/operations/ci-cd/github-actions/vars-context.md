---
title: "vars Context (Organization Variables)"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - context
  - vars
  - variables
sources:
  - url: "https://docs.github.com/en/actions/learn-github-actions/contexts#vars-context"
    title: "GitHub Actions: vars Context"
last_audit_date: 2026-06-09
---

# vars Context (Organization Variables)

The `vars` context provides access to configuration variables set at the organization, repository, or environment level.

## Setting Variables

Variables are managed in the GitHub UI or CLI:

```bash
# Repository variable
gh variable set DOCKER_REGISTRY --repo myorg/myapp --body "ghcr.io"

# Organization variable
gh variable set ORG_DEFAULT_REGION --org myorg --body "us-east1"
```

## Usage in Workflows

```yaml
steps:
  - run: |
      echo "Registry: ${{ vars.DOCKER_REGISTRY }}"
      echo "Region: ${{ vars.REGION }}"
```

## vars vs secrets vs env

| Context | Masked | Best For |
|---|---|---|
| `secrets` | Yes | Sensitive values |
| `vars` | No | Non-sensitive config |
| `env` | No | Per-run overrides |

## Scope Priority

Environment variables > Repository variables > Organization variables

```yaml
# Reusable across multiple repos without duplication
steps:
  - run: |
      docker build -t ${{ vars.DOCKER_REGISTRY }}/myapp:${{ github.sha }} .
      docker push ${{ vars.DOCKER_REGISTRY }}/myapp:${{ github.sha }}
```

## See Also

- [env-context.md](./env-context.md) — env context
- [env-vs-secrets.md](./env-vs-secrets.md) — env vs secrets comparison

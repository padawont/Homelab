---
title: "env vs secrets"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - env
  - secrets
  - variables
sources:
  - url: "https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions"
    title: "GitHub Actions: Using Secrets"
last_audit_date: 2026-06-09
---

# env vs secrets

Understand when to use environment variables vs secrets.

## Comparison

| Aspect | `env` | `secrets` |
|---|---|---|
| Visibility | Visible in logs | Masked in logs |
| Storage | Workflow file, vars, or env context | Encrypted in GitHub UI |
| Scope | Workflow, job, or step | Repository, org, or environment |
| Use For | Config, paths, feature flags | API keys, tokens, passwords |

## When to Use Each

**Use `env` for:**
- Non-sensitive configuration (`PYTHONPATH`, `DJANGO_SETTINGS_MODULE`)
- Feature flags and toggles
- Build parameters (version numbers, paths)

**Use `secrets` for:**
- API tokens and keys
- Database connection strings
- Cloud provider credentials
- Any value that should not appear in logs

> **Warning:** Never store secrets in workflow files or commit them to the repository. Use GitHub Secrets in the UI or CLI.

## Example

```yaml
steps:
  - env:
      LOG_LEVEL: debug     # Non-sensitive config
      API_KEY: ${{ secrets.API_KEY }}  # Masked in logs
    run: uv run deploy
```

## See Also

- [secrets-usage.md](./secrets-usage.md) — Using secrets in workflows
- [vars-context.md](./vars-context.md) — Org-level variables

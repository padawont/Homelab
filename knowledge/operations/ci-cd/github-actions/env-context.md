---
title: "env Context"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - context
  - env
sources:
  - url: "https://docs.github.com/en/actions/learn-github-actions/contexts#env-context"
    title: "GitHub Actions: env Context"
last_audit_date: 2026-06-09
---

# env Context

The `env` context contains environment variables set at the workflow, job, or step level.

## Usage

```yaml
env:
  APP_ENV: production
  LOG_LEVEL: info

jobs:
  test:
    env:
      DATABASE_URL: postgres://localhost/test
    steps:
      - run: echo "App env: ${{ env.APP_ENV }}"
      - run: echo "DB URL: ${{ env.DATABASE_URL }}"
      - run: echo "Log level: ${{ env.LOG_LEVEL }}"
```

## Important Notes

- The `env` context only contains variables set via `env:` in the workflow YAML
- It does NOT include variables set via `$GITHUB_ENV` during steps
- Variables set via `$GITHUB_ENV` must be accessed as regular shell variables (`$VAR_NAME`)
- The `env` context is evaluated at runtime, not at workflow parse time

## Example: Runtime Dynamic Values

```yaml
steps:
  - run: echo "BUILD_ID=$(date +%s)" >> "$GITHUB_ENV"
  - run: echo "Build ID is $BUILD_ID"   # Shell variable, not env context
```

## See Also

- [steps-env.md](./steps-env.md) — Step-level env
- [vars-context.md](./vars-context.md) — vars for org-level variables
- [env-vs-secrets.md](./env-vs-secrets.md) — env vs secrets

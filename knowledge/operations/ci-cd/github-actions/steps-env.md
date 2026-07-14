---
title: "Step Environment Variables"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - steps
  - environment
  - env
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsenv"
    title: "GitHub Actions: steps.env"
last_audit_date: 2026-06-09
---

# Step Environment Variables

Set environment variables at the step level using `env`.

## Step-Level env

```yaml
steps:
  - name: Run tests
    env:
      DJANGO_SETTINGS_MODULE: config.settings.test
      DATABASE_URL: postgres://localhost:5432/test
      PYTHONPATH: src
    run: uv run pytest
```

## Scoping Priority

Environment variables cascade by scope. Inner scopes override outer:

```yaml
env:
  GLOBAL_VAR: global   # workflow-level

jobs:
  test:
    env:
      JOB_VAR: job      # job-level
    steps:
      - env:
          STEP_VAR: step # step-level
        run: echo "$GLOBAL_VAR $JOB_VAR $STEP_VAR"
```

## Setting Variables During a Step

```yaml
steps:
  - run: echo "MY_VAR=hello" >> "$GITHUB_ENV"
  - run: echo "$MY_VAR"   # Outputs: hello
```

Use `$GITHUB_ENV` to set variables that persist for subsequent steps.

## See Also

- [env-vs-secrets.md](./env-vs-secrets.md) — env vs secrets comparison
- [steps-id.md](./steps-id.md) — Accessing step outputs

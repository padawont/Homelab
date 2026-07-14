---
title: "Devbox CI/CD — Running Commands"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "ci-cd", "commands", "scripts"]
sources:
  - "https://www.jetify.com/docs/devbox/cli-reference/devbox-run/"
last_audit_date: 2026-05-24
---

# Running Commands and Scripts

After the install step, use `devbox run` to execute commands inside the Devbox environment:

```yaml
- name: Run arbitrary command
  run: devbox run echo "Hello from devbox"

- name: Run defined script
  run: devbox run test

- name: Run one-off with flags
  run: devbox run -q lsof -i :80
```

## Environment Variables

```yaml
- name: Run with env vars
  run: devbox run --env CI=true --env-file .env.ci test
```

Without `--env` / `--env-file`, `devbox run` inherits the CI runner's existing environment variables.

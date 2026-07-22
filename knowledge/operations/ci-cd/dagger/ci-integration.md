---
title: "Dagger — CI Integration with Forgejo Actions"
status: draft
author: "padawont"
date: 2026-07-22
tags: ["dagger", "forgejo", "ci-cd", "actions"]
sources:
  - url: "https://docs.dagger.io/getting-started/ci-integrations/github-actions"
    title: "Dagger GitHub Actions Integration"
  - url: "https://forgejo.org/docs/latest/user/actions/"
    title: "Forgejo Actions Documentation"
last_audit_date: 2026-07-22
related_configs:
  - configs-and-adr/node-main/kubernetes/forgejo.yaml
  - .forgejo/workflows/ci.yml
---

# Dagger CI Integration with Forgejo Actions

Dagger is not a CI provider — it is a CI engine. You still need a CI trigger to call `dagger call`. In this homelab, the trigger is **Forgejo Actions**.

Forgejo Actions uses GitHub-compatible workflow YAML syntax. Workflows live in `.forgejo/workflows/` or `.github/workflows/`.

## Sample Workflow

```yaml
# .forgejo/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  dagger:
    runs-on: docker
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install Dagger
        run: |
          curl -fsSL https://dl.dagger.io/dagger/install.sh | BIN_DIR=/usr/local/bin sh

      - name: Run Dagger pipeline
        run: |
          dagger call test --source=.
```

## Passing Secrets

Secrets are passed to Dagger via environment variables using the `env://` provider:

```yaml
- name: Run with secrets
  run: |
    dagger call deploy \
      --source=. \
      --registry-token=env://REGISTRY_TOKEN
  env:
    REGISTRY_TOKEN: ${{ secrets.REGISTRY_TOKEN }}
```

In the Dagger module:

```python
@function
async def deploy(self, src: dagger.Directory, registry_token: dagger.Secret) -> str:
    return await (
        dag.container()
        .with_secret_variable("REGISTRY_TOKEN", registry_token)
        .with_exec(["deploy", "script"])
        .stdout()
    )
```

## Caching Across CI Runs

- Dagger's engine cache is ephemeral by default in CI
- For self-hosted Forgejo runners, cache volumes persist if the runner host persists
- Use explicit cache volume namespaces per project
- Dagger Cloud (paid) provides persistent cross-run caching

## Runner Requirements

- Forgejo Actions runner must have Docker access (for Dagger Engine auto-provisioning)
- Docker-in-Docker (DinD) configuration is recommended for runner isolation

## Architecture

```
Push to Forgejo
    │
    ▼
Forgejo Actions (trigger)
    │
    ▼
dagger call test --source=.
    │
    ▼
Dagger Engine (auto-provisioned in Docker)
    │
    ▼
BuildKit containers (build, test, lint)
```

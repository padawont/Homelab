---
title: "Dagger + DevSpace Integration"
status: draft
author: "padawont"
date: 2026-07-22
tags: ["dagger", "devspace", "kubernetes", "k3d", "deployment"]
sources:
  - url: "https://www.devspace.sh/docs/configuration/pipelines/"
    title: "DevSpace Pipelines Documentation"
  - url: "https://www.devspace.sh"
    title: "DevSpace Documentation"
last_audit_date: 2026-07-22
related_configs:
  - deployment/procedures/setup-dagger.md
---

# Dagger + DevSpace Integration

In the homelab's testing phase (Issue #7), Dagger and DevSpace form a complementary stack:

| Layer | Tool | Role |
|---|---|---|
| Pipeline orchestration | **Dagger** | Build, test, lint, scan — defined in Python |
| K8s deployment | **DevSpace** | Deploy to k3d, validate K8s manifests |
| Local env | **DevBox** | Reproducible tooling (Dagger CLI, Python, etc.) |

## Integration Pattern

The tools operate sequentially in a workflow — they do **not** call each other natively:

```bash
#!/bin/bash
# Step 1: Dagger builds and tests
dagger call test --source=.
dagger call build --source=. --output=./dist

# Step 2: DevSpace deploys to k3d
devspace deploy --profile=k3d
```

## Calling DevSpace from Dagger (Optional)

For a fully orchestrated pipeline, DevSpace can be run inside a Dagger container:

```python
@function
async def deploy(self, kubeconfig: dagger.Secret) -> str:
    return await (
        dag.container()
        .from_("alpine:latest")
        .with_exec(["apk", "add", "curl", "bash"])
        .with_exec(["sh", "-c", "curl -fsSL https://get.devspace.sh | bash"])
        .with_secret_variable("KUBECONFIG", kubeconfig)
        .with_exec(["devspace", "deploy", "--profile=k3d"])
        .stdout()
    )
```

## DevSpace Pipeline with Dagger Call

Alternatively, DevSpace can invoke Dagger from its own pipeline definition (`devspace.yaml`):

```yaml
version: v2beta1
pipelines:
  deploy:
    - run: |-
        dagger call build --source=. --output=./dist
        create_deployments --all
```

## Three-Layer Stack Summary

```
DevBox  ─►  Reproducible CLI tooling (dagger, python, devspace)
  │
  ▼
Dagger  ─►  Pipeline orchestration (build, test, lint, scan)
  │
  ▼
DevSpace ─►  K8s deployment (k3d cluster, manifest validation)
```

## Related Dagger Module

A community Dagger module exists at `github.com/MacroPower/x/toolchains/devbox` that can run `devbox` commands inside Dagger pipelines — useful for ensuring CI uses the same Nix-backed toolchain as local dev.

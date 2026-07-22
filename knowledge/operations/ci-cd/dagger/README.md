---
title: "Dagger — Index"
status: draft
author: "padawont"
date: 2026-07-22
tags: ["dagger", "ci-cd", "index"]
sources:
  - url: "https://docs.dagger.io"
    title: "Dagger Documentation"
  - url: "https://pypi.org/project/dagger-io/"
    title: "dagger-io on PyPI"
last_audit_date: 2026-07-22
---

# Dagger.io

Dagger is a programmable CI/CD engine that replaces YAML-based pipelines with portable code written in Python (and other languages). Pipelines run in containers via a BuildKit engine — the same code runs identically on a developer's laptop and in CI.

## Index

| File | Description |
|---|---|
| [AGENTS.md](./AGENTS.md) | Rules and conventions for Dagger docs in this repo |
| [overview.md](./overview.md) | What Dagger is, architecture, key concepts |
| [installation.md](./installation.md) | CLI installation via devbox, engine provisioning |
| [core-concepts.md](./core-concepts.md) | DAG execution, caching, modules, Daggerverse |
| [python-sdk.md](./python-sdk.md) | Python SDK — `dagger-io`, async API, decorators |
| [ci-integration.md](./ci-integration.md) | Forgejo Actions integration |
| [devspace-integration.md](./devspace-integration.md) | Dagger + DevSpace for K8s deployment |
| [comparison.md](./comparison.md) | Dagger vs GitHub Actions, GitLab CI, Jenkins, Tekton |

## Related Topics

- [Devbox CI/CD](../devbox-ci/) — devbox environment used alongside Dagger
- [GitHub Actions](../github-actions/) — current CI platform, replaced by Dagger + Forgejo
- [Python CI Caching](../python-ci-caching/) — caching patterns relevant to Dagger Python pipelines

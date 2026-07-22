---
title: "Forgejo Actions"
status: draft
tags:
  - git
  - forge
  - ci-cd
  - actions
  - runner
  - dagger
sources:
  - url: "https://forgejo.org/docs/latest/admin/actions/"
    title: "Forgejo Actions Administrator Guide"
  - url: "https://forgejo.org/docs/latest/user/actions/quick-start/"
    title: "Forgejo Actions Quick Start"
  - url: "https://forgejo.org/docs/latest/user/actions/github-actions/"
    title: "Forgejo Actions — GitHub Actions Compatibility"
  - url: "https://forgejo.org/docs/latest/user/actions/reference/"
    title: "Forgejo Actions Reference"
  - url: "https://forgejo.org/docs/latest/admin/actions/registration/"
    title: "Forgejo Runner Registration"
  - url: "https://forgejo.org/docs/latest/admin/actions/docker-access/"
    title: "Utilizing Docker within Actions"
  - url: "https://forgejo.org/docs/latest/admin/actions/security/"
    title: "Securing Forgejo Actions Deployments"
last_audit_date: 2026-07-22
related_configs:
  - "configs-and-adr/node-main/kubernetes/forgejo.yaml"
---

# Forgejo Actions

Forgejo Actions provides GitHub Actions-compatible CI/CD built directly into Forgejo. Workflow files are placed in `.forgejo/workflows/` (or `.github/workflows/` for compatibility).

## Architecture

Forgejo Actions has two components:

1. **Forgejo instance** — Parses workflow files, schedules jobs, stores logs and artifacts
2. **Forgejo Runner** — A separate program that executes workflow jobs on designated machines

The Forgejo Runner fetches jobs from the Forgejo instance, executes them locally (or via Docker), and reports results back.

## Workflow Syntax

Workflows are YAML files compatible with GitHub Actions syntax:

```yaml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Hello, Forgejo!"
```

Key differences from GitHub Actions:
- Workflow files in `.forgejo/workflows/` by default (`.github/workflows/` also works)
- `DEFAULT_ACTIONS_URL` configures where actions without absolute URLs are resolved from
- The recommended default is `https://data.forgejo.org`

## Available Actions

Forgejo maintains a curated set of actions at [data.forgejo.org](https://data.forgejo.org):
- `actions/checkout` — Clone repository
- `actions/setup-node` — Set up Node.js
- `actions/setup-python` — Set up Python
- `actions/cache` — Cache dependencies
- `docker/login`, `docker/build-push` — Docker operations

These actions are tested to work with Forgejo Actions and published under Free Software licenses.

## Runner Registration

1. Install the Forgejo Runner (binary, Docker, or package)
2. Register with the Forgejo instance:
   ```bash
   forgejo-runner register --instance https://git.homelab.internal \
     --token <registration-token> \
     --name runner-1 \
     --labels ubuntu-latest:docker://node:20-bullseye
   ```
3. The registration token is obtained from the Forgejo admin UI: Site Administration → Actions → Runners → Create Runner

## Runner Labels

Labels map `runs-on` values to container images:

```
ubuntu-latest:docker://node:20-bullseye
ubuntu-22.04:docker://node:20-bullseye
```

Multiple labels can be specified, comma-separated. The runner will only pick up jobs whose `runs-on` matches one of its labels.

## Docker-in-Docker

Actions that need to build container images require Docker-in-Docker. Configure the runner with:

```yaml
container:
  docker_host: unix:///var/run/docker.sock
  options: --privileged
```

Alternatively, use `dind` (Docker-in-Docker) sidecars. See the [Docker access guide](https://forgejo.org/docs/latest/admin/actions/docker-access/) for details.

## Caching

Caching is handled by the runner, not Forgejo. The cache is stored locally on the runner. Use `actions/cache` with the `~/.cache` path for language-specific caches.

## Secrets

Workflow secrets are configured in the Forgejo web UI at Settings → Actions → Secrets for each repository, organization, or user.

## GitHub Actions Compatibility

Forgejo Actions aims for broad compatibility with GitHub Actions workflows:
- Same YAML syntax (jobs, steps, `uses:`, `run:`, `with:`)
- Same expression syntax (`${{ }}`, `github.*`, `env.*` context)
- Workflow files in `.github/workflows/` work without changes
- `actions/*` actions resolve via `DEFAULT_ACTIONS_URL`

Known differences:
- No GitHub-specific contexts like `github.token` (use `gitea.token` or a custom PAT)
- Some GitHub Actions marketplace actions may not work if they depend on GitHub-specific APIs
- Matrix strategy syntax is fully supported

## Log and Artifact Retention

Configured in `app.ini`:

```ini
[actions]
LOG_RETENTION_DAYS = 365
ARTIFACT_RETENTION_DAYS = 90
```

## Homelab Role

Forgejo Actions will serve as the CI trigger platform for Dagger pipelines (see Issue #6). Workflow files in repositories will trigger Forgejo Actions jobs that invoke Dagger for build and deployment pipelines.

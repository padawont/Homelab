---
title: "Continuous Deployment Patterns"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - deployment
  - cd
  - patterns
  - gha
sources:
  - url: "https://docs.github.com/en/actions/deployment"
    title: "GitHub Actions: Deployment"
last_audit_date: 2026-06-09
---

# Continuous Deployment Patterns

Common CD patterns using GitHub Actions.

## Pattern 1: Branch-Based Deploy

```yaml
name: CD
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v6
      - run: echo "Deploying..."
```

## Pattern 2: Tag-Triggered Release

```yaml
on:
  push:
    tags: ["v*"]

jobs:
  release:
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v6
      - uses: docker/build-push-action@v7
      - uses: softprops/action-gh-release@v3
```

## Pattern 3: Manual Approval with Environments

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: "Target environment"
        required: true
        default: staging

jobs:
  deploy:
    environment: ${{ inputs.environment }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: uv run deploy -e ${{ inputs.environment }}
```

## Pattern 4: Promote Between Environments

```yaml
jobs:
  build:
    outputs:
      image: ${{ steps.build.outputs.image }}
    steps:
      - id: build
        run: echo "image=app:${{ github.sha }}" >> "$GITHUB_OUTPUT"

  deploy-staging:
    needs: build
    environment: staging
    steps:
      - run: echo "Deploy ${{ needs.build.outputs.image }}"

  deploy-production:
    needs: deploy-staging
    environment: production
    steps:
      - run: echo "Promote ${{ needs.build.outputs.image }}"
```

## See Also

- [deployment-environments.md](./deployment-environments.md) — Environment approvals
- [deployment-docker.md](./deployment-docker.md) — Docker builds

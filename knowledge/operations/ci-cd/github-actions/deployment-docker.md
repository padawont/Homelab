---
title: "Build and Push Docker Image"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - docker
  - deployment
  - container
  - gha
sources:
  - url: "https://docs.docker.com/build/ci/github-actions/"
    title: "Docker: CI with GitHub Actions"
last_audit_date: 2026-06-09
---

# Build and Push Docker Image

Build and push a Docker image to a container registry using GitHub Actions.

## Build and Push to GHCR

```yaml
name: Build Docker Image
on:
  push:
    branches: [main]
    tags: ["v*"]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v6

      - uses: docker/login-action@v4
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/metadata-action@v6
        id: meta
        with:
          images: ghcr.io/${{ github.repository }}

      - uses: docker/build-push-action@v7
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

## Docker Metadata Tags

The `metadata-action` generates tags like:

- `ghcr.io/myorg/myapp:main` — for branch pushes
- `ghcr.io/myorg/myapp:v1.2.3` — for version tags
- `ghcr.io/myorg/myapp:latest` — for latest release

## Cache Docker Layers

```yaml
- uses: docker/build-push-action@v7
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## See Also

- [deployment-fastapi.md](./deployment-fastapi.md) — Deploy FastAPI
- [github-token-custom.md](./github-token-custom.md) — Package write permissions

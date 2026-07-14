---
title: "Deploy FastAPI to Cloud Run"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - deployment
  - cloud-run
  - gcp
sources:
  - url: "https://github.com/google-github-actions/deploy-cloudrun"
    title: "google-github-actions/deploy-cloudrun"
last_audit_date: 2026-06-10
---

# Deploy FastAPI to Cloud Run

Deploy a FastAPI application to Google Cloud Run using GitHub Actions.

## Workflow

```yaml
name: Deploy FastAPI
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/setup-uv@v8
      - run: uv run pytest

      - id: auth
        uses: google-github-actions/auth@v3
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - uses: google-github-actions/setup-gcloud@v3

      - uses: google-github-actions/deploy-cloudrun@v3
        with:
          service: my-fastapi-app
          source: ./
          region: us-central1
```

## Dockerfile

```dockerfile
FROM python:3.13-slim
RUN pip install uv
COPY . .
RUN uv sync --no-dev
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Required Secrets

| Secret | Description |
|---|---|
| `GCP_SA_KEY` | Google Cloud service account key (JSON) |
| `GCP_PROJECT_ID` | GCP project ID (use vars if non-sensitive) |

## See Also

- [deployment-fastmcp.md](./deployment-fastmcp.md) — Deploy FastMCP
- [deployment-docker.md](./deployment-docker.md) — Docker build/push
- [secrets-environment.md](./secrets-environment.md) — Environment-level secrets

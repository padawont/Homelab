---
title: "Deploy FastMCP to Cloud Run"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - deployment
  - cloud-run
  - gcp
  - mcp
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP Documentation"
last_audit_date: 2026-06-09
---

# Deploy FastMCP to Cloud Run

Deploy a FastMCP MCP server to Google Cloud Run.

## Workflow

```yaml
name: Deploy FastMCP
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/setup-uv@v8.2.0
      - run: uv run pytest

      - id: auth
        uses: google-github-actions/auth@v3
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - uses: google-github-actions/deploy-cloudrun@v3
        with:
          service: my-mcp-server
          source: ./
          region: us-central1
```

## Dockerfile

```dockerfile
FROM python:3.13-slim
RUN pip install uv
COPY . .
RUN uv sync --no-dev
CMD ["uv", "run", "python", "-m", "src.mcp_server"]
```

## Configuration

FastMCP provides two standard environment variables for runtime configuration:

- `FASTMCP_PORT` — integer, HTTP port the server listens on (default: `8000`)
- `FASTMCP_LOG_LEVEL` — log verbosity, one of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (default: `INFO`)

The HTTP port can also be configured programmatically via `mcp.run()` or via a `fastmcp.json` deployment configuration file:

```python
# In your server entrypoint
if __name__ == "__main__":
    mcp.run(transport="http", port=8080)
```

Or via `fastmcp.json`:

```json
{
  "deployment": {
    "transport": "http",
    "port": 8080
  }
}
```

When deploying to Cloud Run, ensure `PORT` (Cloud Run's standard env var) maps to the same port your server listens on. Cloud Run always injects `PORT` — your FastMCP server should read it if you want to stay Cloud Run-idiomatic.

```yaml
with:
  service: my-mcp-server
  env_vars: |
    # Cloud Run injects PORT automatically; FastMCP reads it at runtime if configured
```

## See Also

- [deployment-fastapi.md](./deployment-fastapi.md) — Deploy FastAPI
- [deployment-docker.md](./deployment-docker.md) — Docker build/push
- [deployment-environments.md](./deployment-environments.md) — Deployment environments

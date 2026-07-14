---
title: "FastMCP Installation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - installation
  - uv
sources:
  - url: "https://github.com/PrefectHQ/fastmcp"
    title: "FastMCP on GitHub"
  - url: "https://gofastmcp.com/getting-started/installation"
    title: "Official FastMCP Installation Guide"
last_audit_date: 2026-06-09
---

# FastMCP Installation

## Prerequisites

- Python 3.10+
- `uv` installed ([docs](https://docs.astral.sh/uv/))

## Install as a project dependency

```bash
uv add fastmcp
```

## Install globally via uv tool

```bash
uv tool install fastmcp
```

## Verify installation

```bash
fastmcp version
```

This works after both `uv add fastmcp` (project install) and `uv tool install fastmcp` (global install).

## Dependencies

FastMCP core dependencies (`fastmcp-slim`):
- `pydantic` — schema validation for tool/resource/prompt parameters
- `pydantic-settings` — configuration management
- `rich` — CLI output formatting
- `python-dotenv` — environment variable loading
- `platformdirs` — platform-specific directory paths
- `typing-extensions` — backported type hints

When installed with the default extras (via `uv add fastmcp`), the `mcp` package (MCP Python SDK ≥1.24.0) is also included, which handles SSE transport and brings `httpx` and `starlette` transitively.

All dependencies are fetched automatically when you `uv add fastmcp`.

## Next steps

See [what-is-fastmcp.md](./what-is-fastmcp.md) for an overview of the framework.

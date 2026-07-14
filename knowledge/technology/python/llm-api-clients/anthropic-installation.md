---
title: "Anthropic Installation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - installation
  - uv
sources:
  - url: "https://docs.anthropic.com/en/docs/quickstart"
    title: "Get started with Claude"
last_audit_date: 2026-06-09
---

# Anthropic Installation

Install the Anthropic Python SDK using `uv`:

```bash
uv add anthropic
```

> **Note:** The official Anthropic quickstart uses `pip install anthropic`. This document uses `uv add anthropic`, a valid alternative that handles dependency management and environment syncing in one step.

## Verify Installation

```python
import anthropic
print(anthropic.__version__)
```

## Dependencies

The `anthropic` package requires **Python 3.9 or later**. It also depends on `httpx` for HTTP transport and bundles its own type definitions and response models.

## Virtual Environment

If working in a project, add the dependency with:

```bash
uv add anthropic
```

`uv add` updates `pyproject.toml` and syncs the environment in a single step — no separate `uv sync` needed.

## API Key

Set the `ANTHROPIC_API_KEY` environment variable:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

See [anthropic-client-init.md](./anthropic-client-init.md) for next steps on creating a client.

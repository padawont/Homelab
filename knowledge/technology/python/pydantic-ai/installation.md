---
title: "Installation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - installation
  - uv
sources:
  - url: "https://docs.pydantic.dev/latest/install/"
    title: "Pydantic Installation Guide"
  - url: "https://ai.pydantic.dev/install/"
    title: "Pydantic AI Installation Guide"
last_audit_date: 2026-06-09
---

# Installation

## Python Version Requirements

Pydantic v2 requires Python 3.9+. Pydantic AI requires Python 3.10+.

## Installing with uv

```bash
# Install pydantic (core validation library)
uv add pydantic

# Install pydantic with email validation support
uv add "pydantic[email]"

# Install pydantic-ai (structured LLM outputs)
uv add pydantic-ai
```

## Verifying Installation

```python
import pydantic
print(pydantic.__version__)  # e.g., 2.12.0
```

## Dependencies

Pydantic v2 bundles `pydantic-core` (Rust-based validation engine). The full `pydantic-ai` package bundles dependencies for all supported model providers (OpenAI, Anthropic, Google, Groq, Mistral, Cohere, etc.). For per-provider selection, use `pydantic-ai-slim` and add only the provider extras you need. `uv add` handles both the `pyproject.toml` update and the environment sync in a single step — no separate `uv sync` is needed.

See [defining models](./defining-models.md) to get started.

---
title: "OpenAI Installation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - installation
  - uv
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
last_audit_date: 2026-06-09
---

# OpenAI Installation

Install the OpenAI Python SDK using `uv`:

```bash
uv add openai
```

For a minimum version:

```bash
uv add "openai>=1.0.0"
```

## Verify Installation

```python
import openai
print(openai.__version__)
```

## Dependencies

The `openai` package requires `pydantic` for response models and `httpx` for HTTP transport. These are installed automatically.

See [openai-client-initialization.md](./openai-client-initialization.md) for next steps on creating a client.

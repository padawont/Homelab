---
title: "OpenAI Client Initialization"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - client
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
last_audit_date: 2026-06-09
---

# OpenAI Client Initialization

## API Key Setup

Set the `OPENAI_API_KEY` environment variable:

```bash
export OPENAI_API_KEY="sk-..."
```

Or pass it directly (less secure):

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")
```

## Synchronous Client

```python
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from env
```

## Async Client

```python
from openai import AsyncOpenAI

client = AsyncOpenAI()  # reads OPENAI_API_KEY from env
```

## Organization ID (optional)

```python
client = OpenAI(organization="org-...")
```

## Project ID (optional)

```python
client = OpenAI(project="proj_...")
```

See [openai-client-sync.md](./openai-client-sync.md) and [openai-client-async.md](./openai-client-async.md) for usage patterns.

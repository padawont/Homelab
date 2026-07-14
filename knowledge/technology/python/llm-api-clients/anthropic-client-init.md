---
title: "Anthropic Initial Setup Guide"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - anthropic
  - python
  - client
sources:
  - url: "https://docs.anthropic.com/en/docs/initial-setup"
    title: "Anthropic Initial Setup Guide"
last_audit_date: 2026-06-09
---

# Anthropic Initial Setup Guide

## API Key Setup

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Direct key (less secure):

```python
from anthropic import Anthropic

client = Anthropic(api_key="sk-ant-...")
```

## Synchronous Client

```python
from anthropic import Anthropic

client = Anthropic()  # reads ANTHROPIC_API_KEY from env
```

## Async Client

```python
from anthropic import AsyncAnthropic

client = AsyncAnthropic()
```

## Context Manager

Both clients support `with` / `async with`:

```python
with Anthropic() as client:
    ...

async with AsyncAnthropic() as client:
    ...
```

## Custom base_url

```python
client = Anthropic(base_url="https://my-proxy.example.com")
```

See [anthropic-messages-api.md](./anthropic-messages-api.md) for making API calls.

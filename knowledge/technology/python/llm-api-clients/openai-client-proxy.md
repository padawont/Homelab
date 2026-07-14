---
title: "OpenAI Proxy Configuration"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - proxy
  - configuration
sources:
  - url: "https://github.com/openai/openai-python#configuring-the-http-client"
    title: "OpenAI Python SDK — Configuring the HTTP client"
last_audit_date: 2026-06-09
---

# OpenAI Proxy Configuration

## Custom base_url

Use `base_url` to route through a proxy or self-hosted endpoint:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://my-proxy.example.com/v1",
)
```

## Azure Endpoint

```python
client = OpenAI(
    base_url="https://my-resource.openai.azure.com",
    api_key="my-azure-key",
    api_version="2024-10-21",
)
```

## HTTP/HTTPS Proxy via httpx

Pass an `http_client` with proxy settings:

```python
from openai import OpenAI
import httpx

proxy_client = OpenAI(
    http_client=httpx.Client(
        proxies="http://localhost:8080"
    ),
)
```

## Async with Proxy

```python
from openai import AsyncOpenAI
import httpx

proxy_client = AsyncOpenAI(
    http_client=httpx.AsyncClient(
        proxies="http://localhost:8080"
    ),
)
```

Some providers (e.g., Together AI, Groq) are OpenAI-compatible — point `base_url` at their endpoint and use their API key.

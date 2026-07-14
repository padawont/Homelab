---
title: "OpenAI Cost Tracking"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - python
  - costs
  - tokens
sources:
  - url: "https://platform.openai.com/docs/pricing"
    title: "OpenAI Pricing"
last_audit_date: 2026-06-10
---

# OpenAI Cost Tracking

## Access Token Usage

```python
response = client.chat.completions.create(
    model="gpt-5.4",
    messages=[{"role": "user", "content": "Hello"}],
)

usage = response.usage
print(f"Prompt tokens: {usage.prompt_tokens}")
print(f"Completion tokens: {usage.completion_tokens}")
print(f"Total tokens: {usage.total_tokens}")
```

## Cost Estimation Function

```python
MODEL_RATES = {
    "gpt-5.4": {"input": 2.50, "output": 15.00},      # per 1M tokens
    "gpt-5.4-mini": {"input": 0.75, "output": 4.50},
    "gpt-5.4-nano": {"input": 0.20, "output": 1.25},
}

def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    rates = MODEL_RATES.get(model)
    if not rates:
        return 0.0
    input_cost = (prompt_tokens / 1_000_000) * rates["input"]
    output_cost = (completion_tokens / 1_000_000) * rates["output"]
    return round(input_cost + output_cost, 6)
```

## Streaming Cost Tracking

For streaming, usage data is in the final chunk:

```python
last_chunk = None
for chunk in stream:
    last_chunk = chunk
    # process delta...

if last_chunk and last_chunk.usage:
    print(last_chunk.usage.total_tokens)
```

See [openai-rate-limits.md](./openai-rate-limits.md) for rate limit tracking and [openai-retry-strategy.md](./openai-retry-strategy.md) for retry patterns that avoid wasted tokens.

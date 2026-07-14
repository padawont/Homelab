---
title: "LLM API Clients — Troubleshooting"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - anthropic
  - python
  - troubleshooting
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
  - url: "https://docs.anthropic.com/en/docs"
    title: "Anthropic Python SDK"
last_audit_date: 2026-06-09
---

# Troubleshooting

## OpenAI Issues

### Authentication Error (401)

```
openai.AuthenticationError: Incorrect API key provided
```

**Fix:** Check `OPENAI_API_KEY` env variable is set correctly. Regenerate key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### Rate Limit (429)

```
openai.RateLimitError: Rate limit exceeded
```

**Fix:** See [openai-rate-limits.md](./openai-rate-limits.md) for backoff strategies and [openai-retry-strategy.md](./openai-retry-strategy.md) for tenacity patterns.

### Model Not Found (404)

```
openai.NotFoundError: Model 'gpt-4o' does not exist
```

**Fix:** Verify model name. Older models may be deprecated. Check access in your OpenAI account.

## Anthropic Issues

### Overloaded (529)

```
anthropic.OverloadedError: Overloaded
```

**Fix:** Implement retry with exponential backoff. See [anthropic-rate-limits.md](./anthropic-rate-limits.md).

### Invalid API Key

```
anthropic.AuthenticationError: Invalid API Key
```

**Fix:** Verify `ANTHROPIC_API_KEY` env variable. Generate key at [console.anthropic.com](https://console.anthropic.com).

### Max Tokens Exceeded

Error when `max_tokens` is too low for the response.

**Fix:** Increase `max_tokens`. For thinking mode, ensure `max_tokens >= budget_tokens + 1024`.

## VCR.py Issues

### Cassette Not Found

```
vcr.errors.CannotOverwriteExistingCassetteException
```

**Fix:** Set `record_mode="new_episodes"` or delete the cassette to re-record.

### API Key Leaked in Cassette

**Fix:** Use `filter_headers` — see [vcrpy-filtering-openai.md](./vcrpy-filtering-openai.md) and [vcrpy-filtering-anthropic.md](./vcrpy-filtering-anthropic.md).

## Pydantic Issues

### ValidationError on Response

**Fix:** Check the response shape matches your model. Use `extra="ignore"` in model config for flexible parsing. See [pydantic-validation-openai.md](./pydantic-validation-openai.md).

### Streaming ValidationError

**Fix:** Streaming chunks may have `None` fields — use optional fields. See [pydantic-streaming-validation.md](./pydantic-streaming-validation.md).

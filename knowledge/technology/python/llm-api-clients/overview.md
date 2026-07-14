---
title: "LLM API Clients"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - openai
  - anthropic
  - llm
  - api
  - python
sources:
  - url: "https://platform.openai.com/docs/libraries"
    title: "OpenAI Python SDK"
  - url: "https://docs.anthropic.com/en/docs"
    title: "Anthropic Python SDK"
last_audit_date: 2026-06-09
---

# LLM API Clients

This topic covers Python SDK usage for OpenAI and Anthropic LLM APIs, including installation, synchronous/async clients, streaming, structured outputs, tool calling, error handling, rate limits, and cost tracking. Also covers VCR.py recording/filtering patterns and Pydantic response validation.

## Atomic Notes

### OpenAI
- [OpenAI Installation](./openai-installation.md) — Adding `openai` with uv
- [Client Initialization](./openai-client-initialization.md) — `OpenAI()`, `AsyncOpenAI()`, API key setup
- [Sync Client](./openai-client-sync.md) — Synchronous request patterns
- [Async Client](./openai-client-async.md) — Async request patterns with `await`
- [Proxy Configuration](./openai-client-proxy.md) — Custom `base_url` and proxy
- [Chat Completions API](./openai-chat-completions.md) — `client.chat.completions.create`
- [Message Format](./openai-messages-format.md) — System, user, assistant, tool roles
- [Basic Streaming](./openai-streaming-basic.md) — `stream=True`, chunk iteration
- [Async Streaming](./openai-streaming-async.md) — `async for` with streaming
- [Structured Outputs](./openai-structured-outputs.md) — `response_format` parameter
- [JSON Schema Mode](./openai-structured-outputs-json-schema.md) — JSON Schema structured output
- [Pydantic Model Response](./openai-structured-outputs-basemodel.md) — Pydantic model structured output
- [Tool Calling](./openai-tool-calling.md) — `tools` parameter, `tool_choice`
- [Parallel Tool Calls](./openai-tool-calling-parallel.md) — Multiple tool calls in one response
- [Error Handling](./openai-error-handling.md) — `APIError`, `RateLimitError`, etc.
- [Retry Strategy](./openai-retry-strategy.md) — Tenacity/backoff patterns
- [Timeout Configuration](./openai-timeout-config.md) — `timeout` parameter
- [Rate Limits](./openai-rate-limits.md) — Rate limit handling
- [Cost Tracking](./openai-cost-tracking.md) — Token usage, cost estimation

### Anthropic
- [Anthropic Installation](./anthropic-installation.md) — Adding `anthropic` with uv
- [Client Init](./anthropic-client-init.md) — `Anthropic()`, `AsyncAnthropic()`
- [Messages API](./anthropic-messages-api.md) — `client.messages.create`
- [Message Format](./anthropic-messages-format.md) — `role`, content blocks
- [System Prompts](./anthropic-system-prompts.md) — `system` parameter
- [Streaming](./anthropic-streaming.md) — `stream=True` for Messages API
- [Tool Use](./anthropic-tool-use.md) — `tools`, `tool_choice`
- [Tool Use Streaming](./anthropic-tool-use-streaming.md) — Streaming with tool use
- [Structured Outputs](./anthropic-structured-outputs.md) — Structured output patterns
- [Extended Thinking](./anthropic-thinking.md) — Extended thinking mode
- [Error Handling](./anthropic-error-handling.md) — API errors, overloaded
- [Rate Limits](./anthropic-rate-limits.md) — Rate limits, retry-after

### VCR.py Integration
- [Recording OpenAI Sync](./vcrpy-recording-openai-sync.md) — Record sync OpenAI calls
- [Recording OpenAI Async](./vcrpy-recording-openai-async.md) — Record async OpenAI calls
- [Recording Anthropic](./vcrpy-recording-anthropic.md) — Record Anthropic calls
- [Filtering OpenAI](./vcrpy-filtering-openai.md) — Filter OpenAI API keys
- [Filtering Anthropic](./vcrpy-filtering-anthropic.md) — Filter Anthropic API keys

### Pydantic Validation
- [Validate OpenAI Responses](./pydantic-validation-openai.md) — Pydantic for OpenAI
- [Validate Anthropic Responses](./pydantic-validation-anthropic.md) — Pydantic for Anthropic
- [Streaming Validation](./pydantic-streaming-validation.md) — Validate streaming chunks

### Troubleshooting
- [Troubleshooting](./troubleshooting.md) — Common issues and solutions

## References

- [OpenAI Python SDK](https://platform.openai.com/docs/libraries)
- [Anthropic Python SDK](https://docs.anthropic.com/en/docs)

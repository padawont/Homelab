# LLM API Clients

Python SDKs for LLM APIs — OpenAI and Anthropic — with VCR.py and Pydantic AI integration.

## Contents

- [overview.md](./overview.md) — Topic hub and index
- [openai-installation.md](./openai-installation.md) — uv add openai
- [openai-client-initialization.md](./openai-client-initialization.md) — OpenAI(), AsyncOpenAI(), env key
- [openai-client-sync.md](./openai-client-sync.md) — Synchronous client usage patterns
- [openai-client-async.md](./openai-client-async.md) — AsyncOpenAI, await pattern
- [openai-client-proxy.md](./openai-client-proxy.md) — Proxy/base_url configuration
- [openai-chat-completions.md](./openai-chat-completions.md) — client.chat.completions.create
- [openai-messages-format.md](./openai-messages-format.md) — system, user, assistant, tool roles
- [openai-streaming-basic.md](./openai-streaming-basic.md) — stream=True, iterating chunks
- [openai-streaming-async.md](./openai-streaming-async.md) — Async streaming with async for
- [openai-structured-outputs.md](./openai-structured-outputs.md) — response_format parameter
- [openai-structured-outputs-json-schema.md](./openai-structured-outputs-json-schema.md) — JSON Schema mode
- [openai-structured-outputs-basemodel.md](./openai-structured-outputs-basemodel.md) — Pydantic model response
- [openai-tool-calling.md](./openai-tool-calling.md) — tools parameter, tool_choice
- [openai-tool-calling-parallel.md](./openai-tool-calling-parallel.md) — Parallel tool calls
- [openai-error-handling.md](./openai-error-handling.md) — APIError, RateLimitError, etc.
- [openai-retry-strategy.md](./openai-retry-strategy.md) — Tenacity/backoff patterns
- [openai-timeout-config.md](./openai-timeout-config.md) — timeout parameter
- [openai-rate-limits.md](./openai-rate-limits.md) — Rate limit handling
- [openai-cost-tracking.md](./openai-cost-tracking.md) — Token usage, cost estimation
- [anthropic-installation.md](./anthropic-installation.md) — uv add anthropic
- [anthropic-client-init.md](./anthropic-client-init.md) — Anthropic(), AsyncAnthropic()
- [anthropic-messages-api.md](./anthropic-messages-api.md) — client.messages.create
- [anthropic-messages-format.md](./anthropic-messages-format.md) — role, content blocks
- [anthropic-system-prompts.md](./anthropic-system-prompts.md) — system parameter
- [anthropic-streaming.md](./anthropic-streaming.md) — stream=True for Messages API
- [anthropic-tool-use.md](./anthropic-tool-use.md) — tools, tool_choice
- [anthropic-tool-use-streaming.md](./anthropic-tool-use-streaming.md) — Streaming with tool use
- [anthropic-structured-outputs.md](./anthropic-structured-outputs.md) — Structured output patterns
- [anthropic-thinking.md](./anthropic-thinking.md) — Extended thinking mode
- [anthropic-error-handling.md](./anthropic-error-handling.md) — API errors, overloaded
- [anthropic-rate-limits.md](./anthropic-rate-limits.md) — Rate limits, retry-after
- [vcrpy-recording-openai-sync.md](./vcrpy-recording-openai-sync.md) — Record sync OpenAI calls with VCR.py
- [vcrpy-recording-openai-async.md](./vcrpy-recording-openai-async.md) — Record async OpenAI calls with VCR.py
- [vcrpy-recording-anthropic.md](./vcrpy-recording-anthropic.md) — Record Anthropic calls with VCR.py
- [vcrpy-filtering-openai.md](./vcrpy-filtering-openai.md) — Filtering OpenAI API keys
- [vcrpy-filtering-anthropic.md](./vcrpy-filtering-anthropic.md) — Filtering Anthropic API keys
- [pydantic-validation-openai.md](./pydantic-validation-openai.md) — Validate OpenAI responses with Pydantic
- [pydantic-validation-anthropic.md](./pydantic-validation-anthropic.md) — Validate Anthropic responses with Pydantic
- [pydantic-streaming-validation.md](./pydantic-streaming-validation.md) — Validate streaming chunks
- [troubleshooting.md](./troubleshooting.md) — Common issues and solutions

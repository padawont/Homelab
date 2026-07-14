---
title: "Integration: LLM Clients"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - llm-evaluation
  - integration
  - llm-clients
sources: []
last_audit_date: 2026-06-09
---

# Integration: LLM Clients

Cross-reference to LLM API client configurations.

## Related Topic

See `knowledge/technology/python/llm-api-clients/` for client setup (OpenAI, Anthropic, etc.).

## Usage in Pipeline

| Component | Client |
|---|---|
| [evaluation-live-mode.md](evaluation-live-mode.md) | OpenAI client for live API calls |
| [llm-as-judge-multi-llm.md](llm-as-judge-multi-llm.md) | Multiple clients for multi-judge |
| [llm-as-judge-structured-output.md](llm-as-judge-structured-output.md) | `OpenAI().beta.chat.completions.parse` |

## Environment Variables

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Installation

```
uv add openai anthropic
```

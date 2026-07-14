---
title: "OpenCode LLM Provider Configuration"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - opencode
  - llm
  - provider
  - configuration
sources:
  - url: "https://opencode.ai/docs"
    title: "OpenCode Documentation"
last_audit_date: 2026-06-09
---

# OpenCode LLM Provider Configuration

Configure which LLM provider and model OpenCode agents use in CI.

## Provider Environment Variables

Set the API key for your provider as a GitHub secret:

```bash
gh secret set OPENAI_API_KEY --repo myorg/myapp
gh secret set ANTHROPIC_API_KEY --repo myorg/myapp
gh secret set GOOGLE_API_KEY --repo myorg/myapp
```

## Per-Agent Model Configuration

```yaml
- uses: anomalyco/opencode/github@latest
  with:
    model: openai/gpt-4o
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Advanced Provider Options

```json
{
  "agent": {
    "reviewer": {
      "model": "openai/gpt-4o",
      "temperature": 0.3,
      "steps": 10
    },
    "creative-writer": {
      "model": "anthropic/claude-sonnet-4-20250514",
      "temperature": 0.8,
      "steps": 20
    }
  }
}
```

## Model Recommendation by Task

| Task | Recommended Model | Notes |
|---|---|---|
| Code review | `openai/gpt-4o` or `anthropic/claude-sonnet-4` | Good at diff analysis |
| Documentation | `openai/gpt-4o` | Strong writing |
| Refactoring | `anthropic/claude-sonnet-4` | Good at structural changes |
| Testing | `openai/gpt-4o` | Strong at edge cases |

## See Also

- [opencode-auth-in-ci.md](./opencode-auth-in-ci.md) — Auth setup
- [opencode-agent-custom.md](./opencode-agent-custom.md) — Custom agent invocation

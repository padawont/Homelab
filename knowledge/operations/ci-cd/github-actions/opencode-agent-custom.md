---
title: "Arbitrary OpenCode Agent Invocation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - opencode
  - agents
  - custom
sources:
  - url: "https://opencode.ai/docs/cli/"
    title: "OpenCode CLI Documentation"
last_audit_date: 2026-06-09
---

# Arbitrary OpenCode Agent Invocation

Run any OpenCode agent for custom tasks in CI.

## Basic Invocation

```yaml
steps:
  - uses: actions/checkout@v6
  - uses: actions/setup-node@v6
    with:
      node-version: 22
  - run: npm install -g opencode-ai
  - env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    run: opencode run --agent my-custom-agent
```

## Passing Custom Arguments

```yaml
steps:
  - env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    run: |
      opencode run --agent documentation-writer \
        --file README.md
```

## Agent Configuration

```json
{
  "agent": {
    "documentation-writer": {
      "description": "Writes documentation from source code",
      "model": "openai/gpt-4o",
      "prompt": "Generate documentation for the provided code files.",
      "max-tokens": 4096
    },
    "refactoring-advisor": {
      "description": "Suggests code refactoring improvements",
      "model": "anthropic/claude-sonnet-4-20250514",
      "prompt": "Analyze code for refactoring opportunities. Focus on reducing complexity and improving maintainability."
    }
  }
}
```

## Running with Custom Prompts

```yaml
steps:
  - run: |
      opencode run --agent custom "Summarize the changes in this PR" \
        --model openai/gpt-4o
```

## See Also

- [opencode-agent-pr-review.md](./opencode-agent-pr-review.md) — PR review agent
- [opencode-llm-provider.md](./opencode-llm-provider.md) — LLM provider config

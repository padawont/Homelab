---
title: "OpenCode Configuration in CI"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - opencode
  - configuration
  - ci
sources:
  - url: "https://opencode.ai/docs"
    title: "OpenCode Documentation"
last_audit_date: 2026-06-10
---

# OpenCode Configuration in CI

The `opencode.json` file is only required in the repository root when using custom agent definitions. For basic CI usage, the GitHub Action accepts configuration via `with:` inputs directly.

## Minimal Config

```json
{
  "agent": {
    "reviewer": {
      "description": "Reviews PR diffs and suggests improvements",
      "model": "openai/gpt-4o",
      "prompt": "Review code changes for bugs, style issues, and security concerns."
    }
  }
}
```

## CI-Specific Configuration

```json
{
  "permission": {
    "*": "allow"
  },
  "agent": {
    "code-reviewer": {
      "description": "PR code review agent",
      "model": "openai/gpt-4o",
      "prompt": "Review the diff and provide actionable feedback."
    }
  }
}
```

> **Note:** GitHub integration does not use an OpenCode plugin. Add the `anomalyco/opencode/github@latest` step to your workflow instead. See [OpenCode GitHub docs](https://opencode.ai/docs/github/) for setup.

## Important Notes

- `opencode.json` must be committed to the repository only when custom agent definitions are needed; basic config can use `with:` inputs
- CI runs from the checked-out SHA
- Use [opencode-caching-config.md](./opencode-caching-config.md) to cache config across runs
- The `.opencode/` directory can contain additional agent definitions (note: directory names use plural — `agents/`, `plugins/`, etc.)
- Model IDs use the format `provider/model-id` (e.g., `openai/gpt-4o`, `anthropic/claude-sonnet-4-5`)
- Provider-specific options (such as `max-tokens`, `reasoningEffort`) are passed through directly to the provider as model options — see [agent additional options](https://opencode.ai/docs/agents/#additional)

## See Also

- [opencode-auth-in-ci.md](./opencode-auth-in-ci.md) — Auth setup
- [opencode-agent-pr-review.md](./opencode-agent-pr-review.md) — PR review agent

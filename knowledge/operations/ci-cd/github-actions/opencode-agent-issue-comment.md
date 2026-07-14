---
title: "OpenCode Agent on Issue Comments"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - opencode
  - agents
  - issues
  - comments
  - github-actions
sources:
  - url: "https://opencode.ai/docs/github/"
    title: "OpenCode GitHub Actions Integration"
last_audit_date: 2026-06-09
---

# OpenCode Agent on Issue Comments

Trigger an OpenCode agent to respond to issue and PR review comments using the official `anomalyco/opencode/github@latest` action.

## Workflow

```yaml
name: opencode
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

jobs:
  opencode:
    if: |
      contains(github.event.comment.body, '/oc') ||
      contains(github.event.comment.body, '/opencode')
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v6
        with:
          fetch-depth: 1
          persist-credentials: false

      - name: Run OpenCode
        uses: anomalyco/opencode/github@latest
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        with:
          model: openai/gpt-4o
```

## Agent Configuration

```json
{
  "agent": {
    "issue-responder": {
      "description": "Responds to issue comments containing /opencode",
      "model": "openai/gpt-4o",
      "prompt": "You are a helpful assistant. Read the issue and the comment, then provide a helpful response."
    }
  }
}
```

## Key Points

- Filter by `/opencode` or `/oc` command to avoid responding to every comment
- `actions/checkout@v6` is a separate prerequisite step; the official action handles context extraction and commenting automatically — no manual `--issue-number` or `--comment-body` flags needed
- `id-token: write` is required for the action to authenticate with the OpenCode GitHub App
- The model format is `provider/model` (e.g. `openai/gpt-4o`, `anthropic/claude-sonnet-4-20250514`)
- Optional `agent` input can be set to select a named agent from your opencode config (falls back to `default_agent`, or `"build"` if not found)
- Optional `prompt` input can override the default behavior for event-driven triggers

## See Also

- [opencode-agent-pr-review.md](./opencode-agent-pr-review.md) — PR review agent
- [opencode-auth-in-ci.md](./opencode-auth-in-ci.md) — Authentication
- [opencode-config-in-ci.md](./opencode-config-in-ci.md) — Agent and model configuration

---
title: "OpenCode Agent on PR Review"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - opencode
  - agents
  - pr
  - review
  - github-actions
sources:
  - url: "https://opencode.ai/docs/github/"
    title: "OpenCode GitHub Actions Integration"
last_audit_date: 2026-06-09
---

# OpenCode Agent on PR Review

Run an OpenCode agent to automatically review pull requests using the official `anomalyco/opencode/github@latest` action.

## Workflow

```yaml
name: opencode
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

jobs:
  opencode:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
      pull-requests: read
      issues: read
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
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          model: openai/gpt-4o
          use_github_token: true
```

## Agent Configuration

```json
{
  "agent": {
    "code-reviewer": {
      "description": "Reviews PR diffs for issues",
      "model": "openai/gpt-4o",
      "mode": "subagent",
      "permission": {
        "edit": "deny"
      },
      "prompt": "Review the PR diff. Check for: bugs, security issues, style problems, and missing tests. Provide specific line-level feedback."
    }
  }
}
```

## Limiting to Specific Commands

You can also trigger a review on demand via issue comments (e.g. `/oc` or `/opencode`):

```yaml
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
jobs:
  review:
    if: |
      contains(github.event.comment.body, '/oc') ||
      contains(github.event.comment.body, '/opencode')
```

## Key Points

- `actions/checkout@v6` is a separate prerequisite step; the official action handles context extraction and commenting automatically — no manual `--pr-number` or `--comment-body` flags needed
- `id-token: write` is required for the action to authenticate with the OpenCode GitHub App
- The model format is `provider/model` (e.g. `openai/gpt-4o`, `anthropic/claude-sonnet-4-20250514`)
- Optional `agent` input can be set to select a named agent from your opencode config (falls back to `default_agent`, or `"build"` if not found). Must be a primary agent.
- Optional `prompt` input can override the default behavior for event-driven triggers
- Use `fetch-depth: 1` (shallow clone) for faster checkout; use `fetch-depth: 0` only when full git history is needed (it is heavier)
- Run on `opened`, `synchronize`, `reopened`, and `ready_for_review` events for comprehensive coverage

## See Also

- [opencode-agent-issue-comment.md](./opencode-agent-issue-comment.md) — Issue comment agent
- [opencode-auth-in-ci.md](./opencode-auth-in-ci.md) — Authentication
- [opencode-config-in-ci.md](./opencode-config-in-ci.md) — Agent and model configuration

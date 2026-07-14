---
title: "OpenCode Authentication in CI"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - opencode
  - auth
  - ci
  - github-token
sources:
  - url: "https://opencode.ai/docs"
    title: "OpenCode Documentation"
last_audit_date: 2026-06-09
---

# OpenCode Authentication in CI

OpenCode needs API keys for LLM providers and tokens for GitHub API access.

## LLM Provider API Key

```yaml
steps:
  - env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    run: opencode run --agent agent-code-review "your prompt"
```

Supported environment variables:

| Provider | Env Variable |
|---|---|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Google Vertex AI | `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLOUD_PROJECT` |
| Azure OpenAI | `AZURE_OPENAI_API_KEY` |

## GitHub Token

```yaml
steps:
  - env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: opencode run --agent agent-issue-responder "your prompt"
```

- For comment/PR operations, the token needs `pull-requests: write`
- For cross-repo access, use a PAT stored as a secret

## Setting Up Secrets in the Repository

```bash
gh secret set OPENAI_API_KEY --repo myorg/myapp
gh secret set GH_PAT --repo myorg/myapp
```

```yaml
steps:
  - env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      GITHUB_TOKEN: ${{ secrets.GH_PAT }}
    run: opencode run --agent my-agent "your prompt"
```

## See Also

- [github-token-permissions.md](./github-token-permissions.md) — Token scopes
- [secrets-usage.md](./secrets-usage.md) — Using secrets in workflows

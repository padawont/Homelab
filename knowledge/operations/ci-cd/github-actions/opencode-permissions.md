---
title: "OpenCode Permissions in CI"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - opencode
  - permissions
  - ci
  - security
sources:
  - url: "https://opencode.ai/docs/permissions/"
    title: "OpenCode Permissions Documentation"
last_audit_date: 2026-06-09
---

# OpenCode Permissions in CI

Configure permissions for OpenCode agents within the GitHub Actions environment.

## GITHUB_TOKEN Permissions

OpenCode agents interacting with GitHub need appropriate token scopes:

```yaml
jobs:
  agent:
    permissions:
      contents: read
      pull-requests: write    # For PR comments/reviews
      issues: write           # For issue comments
      actions: read           # For workflow status
    steps:
      - env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: opencode run --agent reviewer "Review this PR"
```

## OpenCode Config Permissions

```json
{
  "permission": {
    "read": "allow",
    "edit": "ask",
    "glob": "allow",
    "grep": "allow",
    "bash": "allow",
    "webfetch": "ask",
    "websearch": "deny"
  }
}
```

## Principle of Least Privilege

- Start with minimal permissions
- Grant `write` only when the agent needs to create comments, labels, etc.
- Use separate agents for read-only vs write operations

```yaml
jobs:
  analyze:
    permissions:
      contents: read         # Read-only analysis
    steps:
      - run: opencode run --agent analyzer "Analyze the codebase"

  comment:
    needs: analyze
    permissions:
      contents: read
      pull-requests: write   # Only this job can write
    steps:
      - run: opencode run --agent commenter "Comment on the PR"
```

## See Also

- [github-token-custom.md](./github-token-custom.md) — Custom token permissions
- [opencode-auth-in-ci.md](./opencode-auth-in-ci.md) — Authentication

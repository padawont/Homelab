---
title: "OpenCode Installation in CI"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - opencode
  - installation
  - ci
  - npm
sources:
  - url: "https://opencode.ai/docs"
    title: "OpenCode Documentation"
last_audit_date: 2026-06-09
---

# OpenCode Installation in CI

Install the OpenCode CLI in GitHub Actions runners.

## Via npm (Recommended)

```yaml
steps:
  - uses: actions/setup-node@v6
    with:
      node-version: 24
  - run: npm install -g opencode-ai
  - run: opencode --version
```

## Via npm with Caching

```yaml
steps:
  - uses: actions/setup-node@v6
    with:
      node-version: 24
      cache: npm
      cache-dependency-path: "**/package-lock.json"
  - run: npm install -g opencode-ai
```

## Verify Installation

```yaml
steps:
  - run: |
      opencode --version
      opencode --help
```

## System Requirements

- Node.js 18+ (recommended: 24 LTS)
- npm 9+
- Internet access to npm registry and LLM provider APIs

## See Also

- [opencode-config-in-ci.md](./opencode-config-in-ci.md) — Configuration
- [opencode-auth-in-ci.md](./opencode-auth-in-ci.md) — Authentication

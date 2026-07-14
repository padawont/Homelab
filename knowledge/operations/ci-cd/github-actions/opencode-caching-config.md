---
title: "Caching OpenCode Configuration"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - opencode
  - caching
  - ci
  - performance
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows"
    title: "GitHub Actions: Caching"
last_audit_date: 2026-06-09
---

# Caching OpenCode Configuration

Cache the `.opencode/` directory and npm global packages to speed up CI runs.

## Caching npm Global Install

```yaml
steps:
  - uses: actions/setup-node@v6
    with:
      node-version: 22
      cache: npm
  - run: npm install -g opencode-ai
```

## Caching .opencode/ Directory

```yaml
steps:
  - uses: actions/cache@v5
    id: cache-opencode
    with:
      path: .opencode
      key: opencode-${{ hashFiles('opencode.json', '.opencode/**') }}
      restore-keys: |
        opencode-

  - uses: actions/setup-node@v6
    with:
      node-version: 22
  - run: npm install -g opencode-ai
  - if: steps.cache-opencode.outputs.cache-hit != 'true'
    run: opencode agent  # Only if cache missed
```

## Caching npm Global Packages (Linux)

```yaml
steps:
  - uses: actions/cache@v5
    with:
      path: ~/.npm-global
      key: npm-global-${{ runner.os }}-${{ hashFiles('package.json') }}
  - run: |
      npm config set prefix ~/.npm-global
      npm install -g opencode-ai
  - run: echo "$HOME/.npm-global/bin" >> "$GITHUB_PATH"
```

## Best Practices

- Key cache on `opencode.json` and `.opencode/` contents
- Use `restore-keys` for partial cache hits
- Cache on ubuntu-latest runners (most consistent)
- Include Node.js version in cache key for safety

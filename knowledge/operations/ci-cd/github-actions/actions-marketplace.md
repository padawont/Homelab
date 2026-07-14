---
title: "Actions Marketplace"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - marketplace
  - actions
sources:
  - url: "https://docs.github.com/en/actions/creating-actions/publishing-actions-in-github-marketplace"
    title: "GitHub Actions: Marketplace"
last_audit_date: 2026-06-09
---

# Actions Marketplace

GitHub Marketplace provides a catalog of community and official actions.

## Finding Actions

- Browse at [github.com/marketplace?type=actions](https://github.com/marketplace?type=actions)
- Use the `search: actions` filter on GitHub
- Official actions are published by `actions/*` or `github/*`
- Verified creators have a blue checkmark

## Essential Official Actions

```yaml
- uses: actions/checkout@v6          # Checkout repository
- uses: actions/setup-node@v6        # Setup Node.js
- uses: actions/setup-python@v6      # Setup Python
- uses: actions/cache@v5             # Cache dependencies
- uses: actions/upload-artifact@v7   # Upload build artifacts
- uses: actions/download-artifact@v8 # Download build artifacts
- uses: docker/login-action@v4       # Docker registry login
- uses: docker/build-push-action@v7  # Build & push Docker images
- uses: astral-sh/setup-uv@v8.2.0    # Setup uv for Python
```

## Publishing Your Own Action

Create an action in `.github/actions/` or as a separate repo:

```yaml
steps:
  - uses: ./.github/actions/my-action
    with:
      input-param: value
```

## Best Practices

- Pin to major versions (`@v4`) for automatic patch updates
- Pin to SHA for security-critical workflows
- Review action source before using third-party actions
- Prefer official GitHub actions when available

## See Also

- [steps-uses.md](./steps-uses.md) — Referencing actions
- [reusable-workflows-intro.md](./reusable-workflows-intro.md) — Reusable workflows

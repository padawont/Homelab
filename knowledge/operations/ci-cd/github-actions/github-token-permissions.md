---
title: "GITHUB_TOKEN Default Scopes"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - token
  - permissions
  - github-token
sources:
  - url: "https://docs.github.com/en/actions/security-guides/automatic-token-authentication"
    title: "GitHub Actions: GITHUB_TOKEN"
last_audit_date: 2026-06-10
---

# GITHUB_TOKEN Default Scopes

GitHub automatically provisions a `GITHUB_TOKEN` for each workflow run.

## Default Permissions

The default `GITHUB_TOKEN` permissions depend on when the repository was created.

**Post-February 2023 (current default):**

| Scope | Default | Description |
|---|---|---|
| `contents` | read | List commits, download artifacts |
| `packages` | read | Download packages from GitHub Packages |
| `pull-requests` | none | No access to PRs |
| `issues` | none | No access to issues |
| `actions` | none | No access to workflows |
| `security-events` | none | No access to security alerts |
| `statuses` | none | No access to commit statuses |
| `checks` | none | No access to check runs |
| `deployments` | none | No access to deployments |
| `discussions` | none | No access to discussions |
| `id-token` | none | No access to OIDC tokens |
| `pages` | none | No access to Pages builds |

> **Pre-February 2023 (legacy):** Repositories created before February 2023 default to `write-all` (all scopes set to `write`). This behavior can be changed through repository, organization, or enterprise settings.

## Accessing the Token

```yaml
steps:
  - run: |
      curl -L \
        -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
        -H "Accept: application/vnd.github+json" \
        https://api.github.com/repos/${{ github.repository }}
```

The token is available as `${{ secrets.GITHUB_TOKEN }}` or `${{ github.token }}`.

## Security Warning

- Default permissions are permissive (`write-all` on pre-2023 repos)
- Restrict token scopes using [github-token-custom.md](./github-token-custom.md)
- The token expires when the job finishes — each job gets its own distinct token

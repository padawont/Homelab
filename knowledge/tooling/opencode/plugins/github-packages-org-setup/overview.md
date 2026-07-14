---
title: "GitHub Packages Organization Setup"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-08
tags:
  - opencode
  - plugins
  - github-packages
  - npm
  - ci-cd
  - authentication
sources:
  - url: "https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-npm-registry"
    title: "Working with the npm registry — GitHub Docs"
  - url: "https://docs.npmjs.com/cli/v10/configuring-npm/npmrc"
    title: "npmrc — npm Docs"
  - url: "https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication"
    title: "Automatic token authentication — GitHub Docs"
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-08
---

# GitHub Packages Organization Setup

This note covers the full setup for publishing and consuming npm packages through the GitHub Packages registry under a GitHub organization scope (e.g., `@runicengines`). It is written primarily for OpenCode plugin development, but the authentication and configuration patterns apply to any npm package distributed privately through GitHub Packages.

## GITHUB_TOKEN Scoping

### Token Types

GitHub Packages supports two authentication token types:

| Token Type | Scope | Lifetime | Use Case |
|---|---|---|---|
| `GITHUB_TOKEN` | Repository-scoped | Duration of workflow run | CI/CD workflows; automatically provisioned by GitHub Actions |
| Classic Personal Access Token (PAT) | User-scoped | Until revoked | Local development and manual publishing |

### Minimum Scopes

| Operation | Required Scope | Token Type |
|---|---|---|
| Install / read packages | `read:packages` | PAT or GITHUB_TOKEN |
| Publish packages | `write:packages` | PAT or GITHUB_TOKEN |
| Delete packages | `delete:packages` + `read:packages` | PAT only |

### Using GITHUB_TOKEN in GitHub Actions

The `GITHUB_TOKEN` is automatically available in every workflow run and does not need to be stored as a secret. Its permissions are defined in the workflow YAML via the `permissions` block:

```yaml
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
```

Key points:

- **`packages: write`** grants the token `write:packages` scope for that repository's packages.
- **`contents: read`** is typically needed for `actions/checkout`.
- The `GITHUB_TOKEN` is repository-scoped -- it can only publish packages associated with the current repository. It cannot publish packages owned by other repositories in the same organization.
- The token is exposed as `${{ secrets.GITHUB_TOKEN }}` in workflow syntax. When using `actions/setup-node` with `registry-url`, the action configures `.npmrc` to read from the `NODE_AUTH_TOKEN` environment variable — you must set this explicitly (see [NODE_AUTH_TOKEN Setup](#node_auth_token-setup)).

### Classic PAT for Local Development

When publishing or installing from a local machine, use a Personal Access Token:

1. Navigate to **GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)**.
2. Under **Scopes**, select:
   - `read:packages` -- required for installing any private package
   - `write:packages` -- required for publishing packages
   - `repo` -- only needed if the repository is private and your PAT needs access to the repo itself
3. Copy the generated token and make it available as an environment variable:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

### Org-Level vs Repo-Level Token Permissions

| Dimension | GITHUB_TOKEN | Classic PAT |
|---|---|---|
| Scope | Single repository | User + all repos the user can access |
| Package access | Only packages owned by that repo | All packages the user has access to |
| Org governance | None (auto-provisioned) | No org control |

For a multi-repo org like RunicEngines, use a classic PAT with `read:packages` and `write:packages` scopes for local development. Store it securely in your shell profile or a password manager.

## .npmrc Configuration

### File Placement

| Location | Scope | Priority |
|---|---|---|
| `./.npmrc` (project-level) | Single project | Highest -- overrides all others |
| `~/.npmrc` (user-level) | All projects for the current user | Middle |
| `$PREFIX/etc/npmrc` (global, e.g., `/usr/local/etc/npmrc`) | All users on the system | Lowest |

For team projects, commit a project-level `.npmrc` so that all contributors share the same registry mapping. Never commit tokens in a project-level `.npmrc` -- use environment variable interpolation instead.

### Scoped Registry Mapping

Tell npm and Bun which registry to use for a given scope:

```ini
# .npmrc
@runicengines:registry=https://npm.pkg.github.com/
```

This line means: whenever a package name starts with `@runicengines/`, resolve it from `https://npm.pkg.github.com/` instead of the default `https://registry.npmjs.org/`.

### Authentication Token Syntax

```ini
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

The `//npm.pkg.github.com/:_authToken` setting applies to all requests to that registry host. The value reads from the `GITHUB_TOKEN` environment variable at runtime using the `${VAR}` interpolation syntax.

This works with npm, Bun, and Yarn because all three respect `.npmrc` variable expansion.

### Avoiding Hardcoded Tokens

| Anti-pattern | Why it is dangerous |
|---|---|
| `//npm.pkg.github.com/:_authToken=ghp_abc123` | Token is visible in version control and shared with all contributors |
| Same token in `~/.npmrc` | Less risky (not committed), but still plaintext on disk |

Instead, always use environment variable interpolation:

```ini
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

Then set the variable in your shell profile or workflow:

```bash
# ~/.bashrc, ~/.zshrc, or workflow env
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

### Multiple Scope Mappings for Multi-Org Setups

If your project consumes packages from multiple GitHub organizations, add one registry line per scope:

```ini
@runicengines:registry=https://npm.pkg.github.com/
@another-org:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

The single `_authToken` entry covers all scopes on the same registry host.

### Complete .npmrc Example

```ini
# Project-level .npmrc for RunicEngines plugin development
@runicengines:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

## Troubleshooting Auth Failures

### 403 Forbidden

**Likely causes:**
- Token lacks `read:packages` scope (for install) or `write:packages` scope (for publish).
- Token does not belong to a user/member of the target organization.
- Organization has IP allowlists enabled and the request comes from outside the allowed range.

**Fixes:**
- Verify token scopes in GitHub Settings.
- Check the GitHub token's permissions via the API: `gh api /user/packages?package_type=npm` (PAT only — requires user-scoped token; GITHUB_TOKEN is repo-scoped and will fail on this endpoint).
- If using GITHUB_TOKEN in Actions, verify the `permissions:` block includes `packages: write`.

### 404 Not Found

**Likely causes:**
- The registry URL is wrong (e.g., `https://npm.github.com` instead of `https://npm.pkg.github.com`).
- The package has not been published yet or was published under a different name.
- The `@scope:registry` line is missing from `.npmrc`, so npm/Bun is looking on the public registry.
- The package exists but under a different scope or organization.

**Fixes:**
- Confirm the registry URL: for `.npmrc` scope mappings, use `https://npm.pkg.github.com` (the trailing slash is optional but commonly used); for `--registry` flags, `publishConfig`, and environment variables, the trailing slash is also optional.
- Verify the package exists: `npm view @runicengines/opencode-deploy --registry=https://npm.pkg.github.com`.
- Check the `.npmrc` includes the scope-to-registry mapping.
- Ensure the package was published under the expected scope.

### Scope Mismatch

**Symptoms:** `npm install @runicengines/opencode-deploy` tries to resolve from the public npm registry instead of GitHub Packages.

**Cause:** The `@runicengines:registry` line is missing from the active `.npmrc`.

**Fix:** Add the scope mapping to the appropriate `.npmrc`:

```ini
@runicengines:registry=https://npm.pkg.github.com/
```

### Debugging Commands

```bash
# Test registry connectivity (curl is more reliable than npm ping, which GitHub Packages may not support)
curl -s -o /dev/null -w "%{http_code}" https://npm.pkg.github.com

# View package metadata (good for confirming auth works)
npm view @runicengines/opencode-deploy --registry=https://npm.pkg.github.com

# Check which .npmrc is being used
npm config list

# Check the resolved registry for a scoped package
npm config get @runicengines:registry

# Verify the token is correctly set (use substring in CI to avoid exposing the full token in logs)
echo ${GITHUB_TOKEN:0:4}...
```

### Bun-Specific Auth Considerations

Bun respects `.npmrc` configuration, including environment variable interpolation. However:

- Bun may not pick up `.npmrc` changes if the file is edited while a Bun process is running -- restart the process.
- If Bun is failing to authenticate, verify the token is present in the environment. Bun does **not** always source shell profile files (`~/.bashrc`, `~/.zshrc`). Set the variable explicitly:
  ```bash
  GITHUB_TOKEN=ghp_xxx bun install
  ```
- As a fallback, use `NPM_CONFIG_` environment variables:
  ```bash
  NPM_CONFIG_REGISTRY=https://npm.pkg.github.com GITHUB_TOKEN=ghp_xxx bun install
  ```

### Common Error Messages and Fixes

| Error Message | Likely Cause | Fix |
|---|---|---|
| `403 Forbidden - PUT https://npm.pkg.github.com/@runicengines/package` | Missing `write:packages` scope | Add `write:packages` to the PAT or `packages: write` to workflow permissions |
| `404 Not Found - GET https://npm.pkg.github.com/@runicengines/package` | Package does not exist or wrong registry | Publish the package or verify the registry URL |
| `E401 Unable to authenticate` | Missing or invalid token | Check `GITHUB_TOKEN` is set and has correct scopes |
| `ERR_PNPM_AUTH_MISSING_MANUAL_TOKEN` | pnpm cannot find auth token | Set `//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}` in `.npmrc` or use `NPM_CONFIG_` env vars |
| `npm ERR! code EINTEGRITY` | Package tarball does not match expected hash | Clear npm cache: `npm cache clean --force` and retry |
| `Bun install failed with 403` | Bun cannot authenticate | Ensure `GITHUB_TOKEN` is exported in the environment before running `bun install` |

## Automated Publishing via GitHub Actions

### Workflow Permissions

The workflow must declare the permissions required for publishing:

```yaml
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read   # needed for actions/checkout
      packages: write  # needed for npm publish to GitHub Packages
```

Without `packages: write`, the `GITHUB_TOKEN` defaults to `read`-only for packages, and `npm publish` will fail with a `403 Forbidden` error.

### actions/setup-node Configuration

The official `actions/setup-node` action can configure npm for GitHub Packages in a single step:

```yaml
- uses: actions/setup-node@v6
  with:
    node-version: 22
    registry-url: https://npm.pkg.github.com
    scope: "@runicengines"
```

What this does internally:

1. Sets `@runicengines:registry=https://npm.pkg.github.com/` in a temporary `.npmrc`.
2. Sets `//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}` in the same `.npmrc`, configuring it to read auth from the `NODE_AUTH_TOKEN` environment variable.
3. It configures `.npmrc` to read auth from `NODE_AUTH_TOKEN`, but does **not** export it automatically. See [NODE_AUTH_TOKEN Setup](#node_auth_token-setup) below.

### NODE_AUTH_TOKEN Setup

When `registry-url` is set, `actions/setup-node` generates a valid `.npmrc` with the provided registry URL and scope. However, it does **not** populate the `NODE_AUTH_TOKEN` environment variable. You must set it explicitly in the step that needs it:

```yaml
- run: npm publish
  env:
    NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

This `env:` block is **required** -- it is not an override. Without it, `NODE_AUTH_TOKEN` will be undefined and authentication will fail.

### Trigger Strategies

| Trigger | When to Use | Example |
|---|---|---|
| Tag push (`v*`) | Standard release workflow | `push: { tags: ["v*"] }` |
| `workflow_dispatch` | Manual trigger for ad-hoc publishing | `workflow_dispatch: {}` |
| Push to main | Continuous delivery (every commit publishes) | Rare for packages; use tags instead |
| Release published | When a GitHub Release is created | `release: { types: [published] }` |

### Complete Publishing Workflow

```yaml
# .github/workflows/publish.yml
name: Publish Plugin to GitHub Packages

on:
  push:
    tags:
      - "v*"
  workflow_dispatch:  # Manual trigger for ad-hoc publishing

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-node@v6
        with:
          node-version: 22
          registry-url: https://npm.pkg.github.com
          scope: "@runicengines"

      - run: npm ci
      - run: npm run build

      - name: Publish to GitHub Packages
        run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### publishConfig in package.json

Configure `publishConfig` so that `npm publish` uses the correct registry and access level by default:

```json
{
  "publishConfig": {
    "registry": "https://npm.pkg.github.com",
    "access": "restricted"
  }
}
```

| Field | Value | Purpose |
|---|---|---|
| `registry` | `https://npm.pkg.github.com` | Overrides the default `registry.npmjs.org` for publish |
| `access` | `"restricted"` | Ensures the package is private (default for scoped packages, but explicit is better). Note: on GitHub Packages, published packages default to private visibility. Visibility can be changed afterward via the GitHub package settings page (private, internal, or public). The `access` field controls the `--access` flag passed to `npm publish` — use `"restricted"` to keep the package private. |

With `publishConfig` set, the publish command simplifies to `npm publish` without needing `--registry` flags.

## See Also

- [Plugin Private Distribution](../private-distribution.md) -- Consumer-side auth and install configuration
- [Plugin Publishing Workflow](../publishing-workflow.md) -- Manual and CI/CD publishing flow, version bumps, GitHub Release integration
- [Plugin npm Packaging](../npm-packaging.md) -- package.json conventions, naming, dependency declarations
- [Working with the npm registry — GitHub Docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-npm-registry) -- Official GitHub documentation
- [npmrc — npm Docs](https://docs.npmjs.com/cli/v10/configuring-npm/npmrc) -- Official npm configuration reference

---
title: "Plugin Private Distribution"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - distribution
  - private
  - npm
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
  - url: "https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-npm-registry"
    title: "GitHub Packages npm Registry Documentation"
last_audit_date: 2026-06-07
---

# Plugin Private Distribution

OpenCode plugins can be distributed through private npm registries, allowing organisations to share plugins without making them publicly available on the public npm registry.

## GitHub npm Registry

GitHub Packages provides a private npm registry scoped to a GitHub organisation. For RunicEngines, the registry URL is:

```
https://npm.pkg.github.com
```

Packages are published under the `@runicengines` scope. Each package is associated with a GitHub repository, and access control is managed through GitHub repository permissions.

## .npmrc Configuration

Authentication for the GitHub npm registry is configured in `.npmrc`. This file should be placed at the project root for project-level resolution, or at `~/.npmrc` for global resolution.

```ini
# .npmrc
@runicengines:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

The `@runicengines:registry` line tells npm and Bun to resolve any `@runicengines/*` package from the GitHub registry instead of the public npm registry.

The `_authToken` line provides the authentication credential. It can reference an environment variable (`${GITHUB_TOKEN}`) or contain a literal token value (not recommended for shared configuration).

For scoped packages under a different scope, add an additional line:

```ini
@my-org:registry=https://npm.pkg.github.com/
```

## Authentication Tokens

GitHub Packages supports two types of tokens:

| Token Type | Scope | Use Case |
|---|---|---|
| `GITHUB_TOKEN` | Repository-scoped | CI/CD workflows; automatically available in GitHub Actions |
| Personal Access Token (PAT) | User-scoped | Local development; `read:packages` and `write:packages` scopes required |

For local development, create a classic Personal Access Token (PAT) with the `read:packages` scope (and `write:packages` if publishing):

1. Navigate to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic).
2. Under **Scopes**, select `read:packages` (and `write:packages` if publishing).
3. Copy the generated token and export it as an environment variable:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

Alternatively, store the token in `~/.npmrc` directly (less secure but simpler for single-user setups):

```ini
//npm.pkg.github.com/:_authToken=ghp_xxxxxxxxxxxxxxxxxxxx
```

## Publishing to GitHub Packages

Once the `.npmrc` is configured and authentication is in place, publish the package:

```bash
npm publish --registry=https://npm.pkg.github.com
```

Or configure `publishConfig` in `package.json` so that `npm publish` uses the correct registry automatically:

```json
{
  "publishConfig": {
    "registry": "https://npm.pkg.github.com",
    "access": "restricted"
  }
}
```

With `publishConfig` set, the publish command simplifies to:

```bash
npm publish
```

The `access: restricted` setting ensures the package is private to the organisation. This is the default for scoped packages but should be explicit for clarity.

## Publishing via gh CLI

The GitHub CLI (`gh`) can also publish packages. The typical workflow is:

```bash
# Build the package
npm run build

# Create a GitHub release (which can trigger a package publish via Actions)
gh release create v1.0.0 --title "v1.0.0" --notes "Release notes here"

# Alternatively, publish directly via npm
npm publish
```

The `gh` CLI is more commonly used for managing releases and triggering CI/CD pipelines than for direct package publishing. See the CI/CD section below for automated workflows.

## Consumer Configuration

Users who consume a private plugin must configure their local environment to authenticate against the registry:

1. Ensure `.npmrc` (or `~/.npmrc`) contains the scope-to-registry mapping.
2. Ensure `GITHUB_TOKEN` (or equivalent) is set in their environment.
3. Add the scoped package name to the `plugin` array in their `opencode.json`.

OpenCode's auto-install mechanism reads the same npm configuration, so if a user can run `npm install @runicengines/opencode-deploy` successfully from the terminal, OpenCode will also be able to install the plugin at startup.

If authentication fails, OpenCode should log the installation error and continue without the plugin. Check `~/.cache/opencode/node_modules/` for installation logs or errors.

## See Also

- [Plugin npm Packaging](npm-packaging.md) — Package naming, dependencies, and conventions
- [Plugin Versioning](versioning.md) — SemVer and changelog conventions
- [Plugin Publishing Workflow](publishing-workflow.md) — Manual and CI/CD publishing
- [GitHub Packages npm Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-npm-registry) — Official documentation

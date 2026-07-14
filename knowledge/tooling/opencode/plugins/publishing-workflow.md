---
title: "Plugin Publishing Workflow"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - publishing
  - ci-cd
  - github-actions
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
  - url: "https://docs.npmjs.com/cli/v10/commands/npm-publish"
    title: "npm-publish — npm Docs"
  - url: "https://docs.npmjs.com/cli/v10/commands/npm-version"
    title: "npm-version — npm Docs"
  - url: "https://github.com/actions/setup-node"
    title: "actions/setup-node — GitHub Marketplace"
  - url: "https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-npm-registry"
    title: "Working with the npm registry — GitHub Docs"
  - url: "https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository"
    title: "Managing releases in a repository — GitHub Docs"
last_audit_date: 2026-06-07
---

# Plugin Publishing Workflow

## Manual Publishing

The basic workflow for publishing a plugin:

```bash
# 1. Ensure working tree is clean
git status

# 2. Bump version (following SemVer)
# Option A: npm version
npm version patch   # or minor, or major
# Option B: manual edit in package.json

# 3. Build the package (if compilation is needed)
npm run build

# 4. Publish to the target registry
npm publish

# 5. Tag the release in git
git push --tags
```

## Version Bumps

Use `npm version` to bump the version and create a git tag in one step:

```bash
npm version patch   # 1.0.0 -> 1.0.1
npm version minor   # 1.0.0 -> 1.1.0
npm version major   # 1.0.0 -> 2.0.0
```

Each command:

- Updates the `version` field in `package.json`.
- Creates a corresponding git tag (`v1.0.1`, `v1.1.0`, `v2.0.0`).
- Commits the change locally (but does not push).

After publishing, push tags to the remote:

```bash
git push origin main --tags
```

## CI/CD Integration

For automated publishing, integrate with GitHub Actions. Below is an example workflow that publishes a plugin to GitHub Packages on every tagged release:

```yaml
# .github/workflows/publish.yml
name: Publish Plugin

on:
  push:
    tags:
      - "v*"

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
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Key points:

- `registry-url` is set to the GitHub Packages registry.
- `scope` restricts the setup to `@runicengines`, so `.npmrc` is generated automatically.
- `NODE_AUTH_TOKEN` uses the built-in `GITHUB_TOKEN` secret, which GitHub Actions provides automatically. No manual token management is needed.
- The workflow triggers on any tag matching `v*`. Only publish when the tag is pushed.

For publishing to the public npm registry instead of GitHub Packages, use the public registry URL and configure `NODE_AUTH_TOKEN` with an npm automation token:

```yaml
- uses: actions/setup-node@v6
  with:
    node-version: 22
    registry-url: https://registry.npmjs.org

- run: npm publish
  env:
    NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## GitHub Release Integration

For a combined release workflow that creates a GitHub Release and publishes the package:

```yaml
name: Release and Publish

on:
  push:
    tags:
      - "v*"

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
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
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Create Release
        run: |
          gh release create ${{ github.ref_name }} \
            --repo ${{ github.repository }} \
            --title "Release ${{ github.ref_name }}" \
            --generate-notes
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

This workflow publishes the package and then creates a GitHub Release with auto-generated release notes from merged pull requests.

## See Also

- [Plugin npm Packaging](npm-packaging.md) — Package naming, dependencies, and conventions
- [Plugin Versioning](versioning.md) — SemVer and changelog conventions
- [Plugin Private Distribution](private-distribution.md) — Private registry workflows

---
title: "Plugin npm Packaging"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - npm
  - packaging
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin npm Packaging

OpenCode plugins distributed as npm packages follow a set of conventions that ensure consistent auto-installation and loading behaviour.

## Package Naming

The observed ecosystem convention uses a descriptive name prefixed with `opencode-`:

- `opencode-helicone-session`
- `opencode-wakatime`

Scoped packages under an organisation namespace are also supported:

- `@runicengines/opencode-deploy`
- `@runicengines/opencode-lint`

There is no enforced naming rule from OpenCode itself, but using the `opencode-` prefix makes plugin purpose discoverable and consistent with community convention.

## The @opencode-ai/plugin Dependency

Every plugin package should declare `@opencode-ai/plugin` as a dependency or devDependency:

```json
{
  "name": "opencode-helicone-session",
  "version": "1.0.0",
  "private": false,
  "dependencies": {
    "@opencode-ai/plugin": "^0.1.0"
  }
}
```

This package provides:

- The `Plugin` TypeScript type for type-safe plugin exports
- The `tool()` helper and `tool.schema` utilities for defining custom tools
- API documentation available on the npm package page

## package.json Conventions

| Field | Convention | Required |
|---|---|---|
| `name` | kebab-case, preferably `opencode-*` or `@scope/opencode-*` | Yes |
| `version` | Semantic version string | Yes |
| `main` or `exports` | Point to the entry module (CommonJS or ESM) | Yes, if distributing for consumption |
| `type` | `"module"` for ESM packages | Recommended |
| `dependencies` | Include `@opencode-ai/plugin` and any runtime deps | As needed |
| `peerDependencies` | `@opencode-ai/plugin` can be a peer dep if multiple plugins share it | Optional |
| `private` | `true` for unpublished packages; `false` when publishing | Yes |
| `publishConfig` | Registry URL and access level for private packages | Recommended for scoped packages |

Example with exports for an ESM plugin:

```json
{
  "name": "@runicengines/opencode-deploy",
  "version": "0.1.0",
  "type": "module",
  "main": "./dist/index.js",
  "exports": {
    ".": "./dist/index.js"
  },
  "dependencies": {
    "@opencode-ai/plugin": "^0.1.0",
    "shescape": "^2.1.0"
  },
  "publishConfig": {
    "registry": "https://npm.pkg.github.com",
    "access": "restricted"
  }
}
```

## Bun Auto-Install Mechanism

OpenCode uses Bun to auto-install npm plugins declared in `opencode.json` at startup. The flow is:

1. OpenCode reads the `plugin` array from `opencode.json` (both global and project-level).
2. For each package name, it checks whether the package is already available in the cache.
3. If not cached, Bun resolves and installs the package from the configured registry.
4. If cached, the existing installation is used without re-downloading.

This means repeated startups do not trigger unnecessary installs. Package resolution follows the standard Bun behaviour, including `.npmrc` authentication for private registries.

## Caching

Installed packages are cached at:

```
~/.cache/opencode/node_modules/
```

This directory is managed entirely by OpenCode. Users should not manipulate it manually. Clearing this cache forces a full re-install of all npm plugins on the next startup:

```bash
rm -rf ~/.cache/opencode/node_modules
```

The cache stores packages in a flat `node_modules` structure similar to Bun's default behaviour. Each package is installed once and shared across projects when the same name and version are used.

## Install via opencode.json

Plugins are declared in the `plugin` array of `opencode.json`. Both project-level and global configuration files support this field.

### Regular Packages

Unscoped packages are specified by their npm package name only:

```json
{
  "plugin": ["opencode-helicone-session"]
}
```

Multiple regular packages can be listed:

```json
{
  "plugin": [
    "opencode-helicone-session",
    "opencode-wakatime"
  ]
}
```

### Scoped Packages

Scoped packages use the full `@scope/name` string:

```json
{
  "plugin": ["@my-org/custom-plugin"]
}
```

Mixed lists are valid:

```json
{
  "plugin": [
    "opencode-helicone-session",
    "@runicengines/opencode-deploy",
    "@runicengines/opencode-lint"
  ]
}
```

### Version Pinning

The `plugin` array accepts plain package names only; version specifiers are not supported in the array entries. Package resolution follows the version published to the registry (or the latest matching tag). To control which version is installed, publish updated versions or use registry-level dist-tags.

For development workflows, it is possible to reference a local package path if Bun is configured with resolution overrides, but this is not a supported OpenCode feature. The intended path for testing unpublished changes is through local plugins (`.opencode/plugins/` directory).

## See Also

- [Plugin Private Distribution](private-distribution.md) — Private registry workflows
- [Plugin Versioning](versioning.md) — SemVer and changelog conventions
- [Plugin Publishing Workflow](publishing-workflow.md) — Manual and CI/CD publishing
- [Plugin Architecture](architecture.md) — Plugin architecture overview

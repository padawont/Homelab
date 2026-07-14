---
title: "Plugin Versioning"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - versioning
  - semver
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin Versioning

## Semantic Versioning Strategy

OpenCode plugins should follow semantic versioning (SemVer 2.0.0):

| Version Bump | When to Apply |
|---|---|
| **Major** (1.0.0 to 2.0.0) | Breaking changes to exported hooks, tool signatures, or event handler contracts. Removal of previously exported functions or types. |
| **Minor** (1.0.0 to 1.1.0) | New event hooks, new exported tools, new configuration options. Backward-compatible additions. |
| **Patch** (1.0.0 to 1.0.1) | Bug fixes, documentation improvements, internal refactoring with no API change. |

A "breaking change" for an OpenCode plugin includes:

- Renaming or removing an exported plugin function.
- Changing the parameters or return types of hook handlers.
- Renaming or removing custom tool definitions.
- Changing the behaviour of an existing hook in a way that could break consumers relying on the previous behaviour.

## Changelog Conventions

Each published plugin should maintain a `CHANGELOG.md` in the plugin's repository (not in the Knowledge Base). The recommended format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/):

```markdown
# Changelog

## [2.0.0] - 2026-06-01

### Changed

- **Breaking:** Hook `tool.execute.before` now receives restructured parameters. Migrate from `(input, output)` to `(event)` object.
- Updated `@opencode-ai/plugin` peer dependency to `^0.2.0`.

### Added

- `shell.env` hook support for environment variable injection.

## [1.1.0] - 2026-05-15

### Added

- New `session.idle` event hook.
- Custom tool examples in README.

### Fixed

- Error handling for missing configuration file.

## [1.0.0] - 2026-05-01

### Added

- Initial release.
- Core plugin hooks: `tool.execute.before`, `tool.execute.after`, `session.created`.
```

## Breaking Changes and Migration

When publishing a breaking change:

1. Document the migration path in the changelog.
2. If possible, provide a migration script or codemod.
3. Tag the previous version as a `v1.x` release branch for consumers who cannot upgrade immediately.
4. Communicate the breaking change via repository release notes.

Consumers pinning to a specific major version should update their consuming project's lockfile or use registry dist-tags:

```bash
npm dist-tag add @runicengines/opencode-deploy@2.0.0 latest
npm dist-tag add @runicengines/opencode-deploy@1.3.0 v1
```

## See Also

- [Plugin npm Packaging](npm-packaging.md) — Package naming, dependencies, and conventions
- [Plugin Publishing Workflow](publishing-workflow.md) — Manual and CI/CD publishing
- [Plugin Private Distribution](private-distribution.md) — Private registry workflows

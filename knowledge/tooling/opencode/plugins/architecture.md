---
title: "Plugin Architecture"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - architecture
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin Architecture

## Local Plugins

OpenCode supports two ways to load plugins: local files and npm packages. Plugins can also define and load agents, extending OpenCode's multi-agent capabilities. This is a key architectural feature seen in ecosystem plugins such as `opencode-background-agents` and `opencode-workspace`.

Local plugins are JavaScript or TypeScript modules placed in either of two directories:

- Project-level: `.opencode/plugins/`
- Global: `~/.config/opencode/plugins/`

OpenCode scans these directories recursively at startup and registers every `.js` or `.ts` file it finds as a plugin.

## npm Plugins

npm plugins are declared in the `plugin` array of `opencode.json`. Both regular packages and scoped packages are supported:

```json
{
  "plugin": [
    "opencode-helicone-session",
    "opencode-wakatime",
    "@my-org/custom-plugin"
  ]
}
```

Scoped packages are specified with their full `@scope/name` string, just as they appear in the npm registry.

## How plugins are installed

npm plugins declared in `opencode.json` are auto-installed via Bun at startup. OpenCode checks whether each package is already available before attempting installation, so repeated startups do not re-download unchanged packages.

Installed packages are cached in `~/.cache/opencode/node_modules/`. This cache directory is managed entirely by OpenCode -- users should not manipulate it manually.

Local plugins are not installed or cached. They are loaded directly from their plugin directory on each startup. No package manager step applies unless a local plugin declares its own dependencies (see [Plugin Creation](creation.md)).

### Publishing Plugins to npm

Plugins intended for reuse or distribution are published to the npm registry. Recommendations for publishing (based on community observation and ecosystem analysis; the official docs do not prescribe a specific convention):

- **Naming convention** — Observed ecosystem packages use the `opencode-*` pattern (e.g., `opencode-helicone-session`, `opencode-wakatime`) or a scoped name under your organization (e.g., `@scope/opencode-*`)
- **Authoring package** — The `@opencode-ai/plugin` package provides TypeScript types (`Plugin`), helpers (`tool()`, `tool.schema`), and documentation for plugin authoring
- **Publishing workflow** — Run `npm publish` (or `bun publish`) to make the plugin available on npm. Once published, users can declare it in the `plugin` array of their `opencode.json`, and OpenCode auto-installs it at startup

Plugins do not need to be publicly published to be used — local plugin files and private npm packages work identically once installed.

## See Also

- [Plugin Loading](loading.md) — Load order and deduplication
- [Plugin Creation](creation.md) — Basic structure, TypeScript, dependencies, and configuration
- [Plugin npm Packaging](npm-packaging.md) — Packaging plugins for npm distribution
- [Plugin Examples](examples.md) — Code examples for common plugin patterns
- [Bundling Components](bundling-components.md) — Bundling agents, skills, and tools in a plugin

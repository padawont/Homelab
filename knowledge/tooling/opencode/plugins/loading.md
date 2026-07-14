---
title: "Plugin Loading"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - loading
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin Loading

## Load Order

Plugins are loaded and registered in the following order:

1. Global config (`~/.config/opencode/opencode.json`) -- npm plugins from the global opencode.json
2. Project config (`opencode.json`) -- npm plugins from the project-level opencode.json
3. Global plugin directory (`~/.config/opencode/plugins/`) -- local plugins from the global directory
4. Project plugin directory (`.opencode/plugins/`) -- local plugins from the project directory

### Deduplication

If the same npm package (matching name and version) appears in both the global and project config, it is loaded only once. This prevents duplicate registration of the same plugin.

However, a local plugin and an npm plugin with similar or identical names are treated as separate plugins and both are loaded. Name similarity is not considered a duplicate -- only exact npm package identity (name + version) is deduplicated.

## See Also

- [Plugin Architecture](architecture.md) — Local vs npm plugins overview
- [Plugin Creation](creation.md) — Creating a plugin
- [Plugin npm Packaging](npm-packaging.md) — npm packaging conventions

---
title: "Plugin Creation"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - creation
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin Creation

A plugin is a JavaScript or TypeScript module that exports one or more plugin functions. Each function receives a context object and returns a hooks object with event handlers.

## Basic Structure

```javascript
export const MyPlugin = async ({ project, client, $, directory, worktree }) => {
  return {
    // Hook implementations go here
  };
};
```

The plugin function receives:

| Property | Description |
|---|---|
| `project` | The current project information |
| `client` | An OpenCode SDK client for interacting with the AI |
| `$` | Bun's shell API for executing commands |
| `directory` | The current working directory |
| `worktree` | The git worktree path, if applicable |

## TypeScript Support

For TypeScript plugins, import the `Plugin` type from the plugin package:

```typescript
import type { Plugin } from "@opencode-ai/plugin";

export const MyPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  return {
    // Type-safe hook implementations
  };
};
```

## Dependencies

Local plugins and custom tools can use external npm packages. Add a `package.json` to the config directory with the dependencies you need:

```json
{
  "dependencies": {
    "shescape": "^2.1.0"
  }
}
```

OpenCode runs `bun install` at startup to install these. Your plugins and tools can then import them:

```typescript
import { escape } from "shescape";

export const MyPlugin = async () => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "bash") {
        output.args.command = escape(output.args.command);
      }
    },
  };
};
```

## Plugin Configuration

_This section is the author's analysis and synthesis — it is not directly documented on the cited source page._

Plugins can read their own configuration through their own mechanisms. The `plugin` array in `opencode.json` is solely for declaring which plugins to load (by npm package name or local file path); it does not pass plugin-specific settings.

For plugin-specific configuration, common patterns include:

- **Environment variables** — Read at runtime via `process.env`
- **Dedicated config files** — A plugin reads its own config file (e.g., `.opencode/plugins/<name>.json`) on initialization
- **Factory functions** — Export a factory that accepts options rather than a plain export, allowing configuration at the declaration site

The `@opencode-ai/plugin` package does not mandate a specific configuration approach — plugin authors choose the mechanism that best fits their use case.

## See Also

- [Plugin Architecture](architecture.md) — Local vs npm plugins overview
- [Plugin Examples](examples.md) — Complete code examples
- [Bundling Components](bundling-components.md) — Bundling agents, skills, and tools in a plugin

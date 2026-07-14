---
title: "Bundling Agents, Skills, and Tools in a Plugin"
status: draft
author: "Khalid"
date: 2026-06-06
tags:
  - opencode
  - plugins
  - agents
  - skills
  - tools
  - packaging
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
  - url: "https://opencode.ai/docs/custom-tools"
    title: "OpenCode Custom Tools Documentation"
last_audit_date: 2026-06-06
---

# Bundling Agents, Skills, and Tools in a Plugin

An OpenCode npm plugin can distribute more than hook functions. It can ship agents (subagent definitions), skills (SKILL.md instruction bundles), and custom tools (.ts/.js executables) as a single package. This note covers the conventions, constraints, and best practices for bundling these components together.

## Why Bundle

Bundling agents, skills, and custom tools into a single npm plugin provides several advantages over distributing each artifact separately:

| Benefit | Detail |
|---|---|
| Single dependency | One `plugin` entry in `opencode.json` installs the full automation suite. No separate setup steps for agents, skills, and tools. |
| Versioned together | All components share the same version number and release cadence. A consumer never faces version mismatches between an agent definition and the custom tools it depends on. |
| Tested together | Integration tests exercise the complete end-to-end flow: agents invoke skills, skills reference custom tools, tools call back to plugin hooks. CI validates the bundle as a unit. |
| Documented together | A single README explains the entire plugin: what agents it provides, what skills it makes available, what custom tools it registers, and how they interact. |

This pattern is especially useful for organisation-wide plugins where a consistent set of agents, skills, and tools should be available across all projects.

## Directory Layout Conventions

A plugin that bundles agents, skills, and tools should place them under a `.opencode/` directory within the npm package. This mirrors the project-level `.opencode/` structure, making the intent clear and enabling future auto-discovery if OpenCode extends plugin scanning.

```
@runicengines/opencode-plugin/
├── package.json
├── .opencode/
│   ├── agents/
│   │   ├── architect.md
│   │   ├── tech-lead.md
│   │   └── developer.md
│   ├── skills/
│   │   ├── workflow-skills/
│   │   │   └── SKILL.md
│   │   └── discovery-skills/
│   │       └── SKILL.md
│   └── tools/
│       ├── project-analyzer.ts
│       └── dependency-checker.ts
├── dist/
│   └── index.js             # Plugin entry point (hooks + tool registration)
├── README.md
└── CHANGELOG.md
```

### Layout Rationale

- `.opencode/agents/` mirrors the project-level agent directory. Each `.md` file defines one agent following the standard agent format (see [Agents](../agents/)).
- `.opencode/skills/` mirrors the project-level skill directory. Each subdirectory contains a `SKILL.md` file following the standard skill format (see [Skills](../skills/)).
- `.opencode/tools/` mirrors the project-level tool directory. Each `.ts` or `.js` file exports a tool definition using the `tool()` helper (see [Custom Tools](../custom-tools/)).
- `dist/index.js` is the plugin entry point. The plugin hooks are responsible for programmatically registering the components that auto-discovery does not cover.

### Alternative: Flat Plugin Structure

For simpler plugins that ship only one or two components, a flat structure without the `.opencode/` wrapper is acceptable:

```
@runicengines/opencode-simple-plugin/
├── package.json
├── agents/
│   └── reviewer.md
├── README.md
└── CHANGELOG.md
```

The `.opencode/` prefix is a convention, not a technical requirement. The bundled files are not auto-discovered regardless of the directory name -- they must be explicitly registered or copied. Use the `.opencode/` convention for clarity and forward compatibility.

## How Plugins Are Loaded

Understanding the loading mechanism is essential to understanding the bundling constraints.

### npm Plugin Installation

1. The consumer declares the plugin in `opencode.json`:
   ```json
   {
     "plugin": ["@runicengines/opencode-plugin"]
   }
   ```

2. OpenCode auto-installs the package via Bun at startup, caching it in:
   ```
   ~/.cache/opencode/node_modules/@runicengines/opencode-plugin
   ```

3. The plugin's entry point (typically `dist/index.js`) is loaded and executed. The plugin function receives the standard context and returns hooks.

### What Gets Auto-Discovered

OpenCode auto-discovers agents, skills, and custom tools from the following locations:

| Component | Auto-Discovered Locations |
|---|---|
| Agents | `.opencode/agents/` (project), `~/.config/opencode/agents/` (global) |
| Skills | `.opencode/skills/` (project), `~/.config/opencode/skills/` (global) |
| Custom tools | `.opencode/tools/` (project), `~/.config/opencode/tools/` (global) |
| Plugins | `.opencode/plugins/` (project), `~/.config/opencode/plugins/` (global) |

### What Is NOT Auto-Discovered

The npm plugin's bundled `.opencode/` directories are **not** auto-discovered. OpenCode scans the project worktree and the global config directory -- it does not scan inside installed npm packages. A plugin's `.opencode/agents/`, `.opencode/skills/`, and `.opencode/tools/` directories are invisible to the auto-discovery mechanism.

This is the central constraint that plugin authors must work around.

## Registration Mechanisms

Because bundled components are not auto-discovered, the plugin must take explicit action to make them available. The available mechanisms differ by component type.

### Agents

Agent definitions are `.md` files that OpenCode reads from `.opencode/agents/` or `~/.config/opencode/agents/`. When bundled in a plugin, the `.md` files are inside the npm package and invisible to the agent scanner.

**Option A: Copy or symlink at plugin init.** The plugin uses a startup hook to copy its agent `.md` files into the project's `.opencode/agents/` directory:

```typescript
import { type Plugin } from "@opencode-ai/plugin";
import { copyFileSync, mkdirSync, existsSync, readdirSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));

export const MyPlugin: Plugin = async ({ directory }) => {
  const agentsDir = join(directory, ".opencode", "agents");
  const bundledAgentsDir = join(__dirname, "..", ".opencode", "agents");

  if (existsSync(bundledAgentsDir)) {
    mkdirSync(agentsDir, { recursive: true });
    for (const file of readdirSync(bundledAgentsDir)) {
      if (file.endsWith(".md")) {
        const dest = join(agentsDir, file);
        if (!existsSync(dest)) {
          copyFileSync(join(bundledAgentsDir, file), dest);
        }
      }
    }
  }

  return {
    // Hook implementations
  };
};
```

> **Plugin update propagation problem.** The copy-on-first-run pattern above (`if (!existsSync(dest))`) means that when a consumer upgrades the plugin to a newer version, the updated agent/skill files are never copied — the old copies already exist in the project's `.opencode/` directory. Three approaches address this:
>
> - **Option 1: Consumer runs a setup command after upgrade.** The plugin provides a CLI command (e.g., `npx my-plugin setup`) that the consumer runs after `npm update` to re-copy files. This is simple but relies on the consumer remembering to run it.
> - **Option 2: Version-stamping to detect and re-copy.** The plugin writes a `.opencode-plugin-version` file alongside the copied files containing the plugin version. On each init, it compares the stamp against the installed package version. If they differ, it re-copies and updates the stamp. This automates the process but adds complexity.
> - **Option 3: Use symlinks instead of copies.** Replace `copyFileSync` with `symlinkSync` (or use `cpSync` with the `--symbolic-link` equivalent). Symlinks always point to the plugin's current files, so updates propagate automatically. However, symlinks may cause issues on Windows (require developer mode or admin privileges) and the target files are outside the project tree.

**Option B: Define agents programmatically in opencode.json.** The plugin can document that the consumer must add the agent definitions to their `opencode.json` `"agent"` key. This is the simplest approach but shifts work to the consumer.

**Option C: Recommend manual copy.** The plugin's README instructs the consumer to copy the agent `.md` files into their project's `.opencode/agents/` directory. A setup script can automate this.

### Skills

Skill definitions are `SKILL.md` files placed in directories under `.opencode/skills/`. They are loaded on demand when an agent calls `skill({ name: "..." })`.

**Option A: Copy or symlink at plugin init.** Same pattern as agents -- copy the bundled skill directories into `.opencode/skills/` on first run:

```typescript
import { cpSync, existsSync, mkdirSync, readdirSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));

// Inside the plugin function
const skillsDir = join(directory, ".opencode", "skills");
const bundledSkillsDir = join(__dirname, "..", ".opencode", "skills");

if (existsSync(bundledSkillsDir)) {
  mkdirSync(skillsDir, { recursive: true });
  for (const skillDir of readdirSync(bundledSkillsDir)) {
    const src = join(bundledSkillsDir, skillDir);
    const dest = join(skillsDir, skillDir);
    if (!existsSync(dest)) {
      cpSync(src, dest, { recursive: true });
    }
  }
}
```

**Option B: Document skill names.** The plugin's README lists the skill names that the plugin provides. The consumer manually copies them or the agent definitions in the plugin reference them by name. If the skills are not discoverable, the agent definitions must instruct agents to use the `skill()` tool with the correct name.

### Custom Tools

Custom tools are the component with the most direct plugin integration. The `tool()` helper can be used inside a plugin's `tool` hook, which **is** supported by the plugin API.

**Option A: Register via the `tool` hook.** This is the preferred approach for plugin-bundled tools. The plugin creates the tool definitions programmatically using the same `tool()` helper that standalone tools use:

```typescript
import { type Plugin, tool } from "@opencode-ai/plugin";

export const MyPlugin: Plugin = async () => {
  return {
    tool: {
      "project-analyzer": tool({
        description: "Analyze project structure and dependencies",
        args: {
          path: tool.schema.string().describe("Project root path"),
        },
        execute: async (args, context) => {
          // Tool implementation
          return `Analyzed ${args.path}`;
        },
      }),
      "dependency-checker": tool({
        description: "Check for outdated or vulnerable dependencies",
        args: {
          path: tool.schema.string().describe("Path to package.json"),
        },
        execute: async (args, context) => {
          // Tool implementation
          return `Checked ${args.path}`;
        },
      }),
    },
  };
};
```

Plugins can also import tool definitions from the `.opencode/tools/` directory and re-export them through the `tool` hook. This keeps tool source files separate from the plugin entry point:

```typescript
import { type Plugin } from "@opencode-ai/plugin";
import projectAnalyzer from "./.opencode/tools/project-analyzer";
import dependencyChecker from "./.opencode/tools/dependency-checker";

export const MyPlugin: Plugin = async () => {
  return {
    tool: {
      "project-analyzer": projectAnalyzer,
      "dependency-checker": dependencyChecker,
    },
  };
};
```

**Option B: Copy to `.opencode/tools/`.** As with agents and skills, the plugin can copy the `.ts`/`.js` files into the project's `.opencode/tools/` directory on init. However, this is less idiomatic than the `tool` hook registration. Copying spreads tool source across the project file system; the `tool` hook keeps them scoped to the plugin.

## Auto-Discovery Boundary Summary

| Location | Agents | Skills | Custom Tools | Plugins |
|---|---|---|---|---|
| Project `.opencode/<dir>/` | Auto-discovered | Auto-discovered | Auto-discovered | Auto-discovered |
| Global `~/.config/opencode/<dir>/` | Auto-discovered | Auto-discovered | Auto-discovered | Auto-discovered |
| npm plugin `.opencode/<dir>/` | NOT auto-discovered | NOT auto-discovered | NOT auto-discovered | N/A (plugin is loaded via `plugin` array) |
| Plugin `tool` hook | Not applicable | Not applicable | Supported via `tool()` helper | N/A |

The distinction is structural: auto-discovery walks the filesystem from the worktree root and the global config directory. It does not resolve packages in `node_modules` or the Bun cache. Any component that must be available through auto-discovery must be placed in one of those two tree locations.

## Current Best Practices

Based on the constraints above, the following practices produce the most reliable bundle.

### Register Custom Tools via the `tool` Hook

Of the three component types, custom tools have native support in the plugin API. The `tool` hook returns tool definitions that are automatically merged into the runtime tool set. This is the only mechanism that works without filesystem copying.

```typescript
export const MyPlugin: Plugin = async () => {
  return {
    tool: {
      myTool: tool({ ... }),
    },
  };
};
```

Plugin tools take precedence over built-in tools with the same name. See [Custom Tools](../custom-tools/) for the full `tool()` helper reference.

### Ship Agent and Skill Files with a Bootstrap Script

For agents and skills, the most maintainable approach is to ship the `.md` files in the plugin package and provide a bootstrap script (or a plugin init hook) that copies them into the project's `.opencode/` directories. The copy-on-first-run pattern avoids overwriting user modifications and ensures the files land in a discoverable location.

The bootstrap should:

1. Check if each target file already exists (respect user customisations).
2. Copy only if absent.
3. Log what was installed so the consumer knows what to expect.

### Document the Manual Setup Path

Even with bootstrap automation, the plugin README must document what gets installed and how to reset or update it. At minimum, the README should list:

- The agent names provided (e.g., `architect`, `tech-lead`, `developer`).
- The skill names provided (e.g., `workflow-skills`, `discovery-skills`).
- The custom tools registered (e.g., `project-analyzer`, `dependency-checker`).
- The commands to re-run setup or to manually copy after an update.

### Use the `.opencode/` Convention for Forward Compatibility

Even though bundled `.opencode/` directories are not auto-discovered today, placing agents, skills, and tools under `.opencode/` inside the package aligns with OpenCode's existing discovery conventions. If OpenCode later adds plugin package scanning, packages using this layout will be forward-compatible without restructuring.

## RunicEngines Use Case

The RunicEngines organisation applies this bundling pattern for its role-based agent system, distributed via the GitHub npm registry.

### Org-Wide Agent Plugin

One plugin packages all organisation agents as a single npm module:

- **Package:** `@runicengines/opencode-agents`
- **Registry:** GitHub Packages (`https://npm.pkg.github.com`)
- **Access:** Restricted (organisation-private)
- **Agent files:** `.opencode/agents/` containing `architect.md`, `tech-lead.md`, `developer.md`, and `reviewer.md`
- **Skill files:** `.opencode/skills/` containing workflow skills and discovery skills
- **Custom tools:** Registered via the `tool` hook in the plugin entry point

### Consumer Configuration

A project within the organisation consumes the agent plugin by adding it to `opencode.json`:

```json
{
  "plugin": ["@runicengines/opencode-agents"]
}
```

The plugin's init hook copies agent and skill files into the project's `.opencode/` directories on first run. The custom tools are available immediately through the `tool` hook without any filesystem operations.

### Publishing Workflow

Publishing follows the standard GitHub Packages workflow documented in [Plugin npm Packaging](npm-packaging.md):

```bash
# Build the plugin
npm run build

# Bump version
npm version patch

# Publish to GitHub Packages
npm publish
```

The `.npmrc` at the organisation level maps the scope:

```ini
@runicengines:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

### Versioning the Bundle

All components in the plugin share a single version number. A new agent definition, an updated skill, or a changed custom tool all trigger a version bump. The CHANGELOG documents what changed per component:

```markdown
# Changelog

## [1.2.0] - 2026-06-01

### Added
- New `reviewer` agent for code review workflows.
- `discovery-skills` skill for locating configuration files.

### Changed
- `project-analyzer` tool now supports monorepo detection.
- Updated `@opencode-ai/plugin` dependency to `^0.2.0`.
```

This single-version approach is simpler than versioning each component independently and is safe because the components are designed and tested as a unit.

## See Also

- [Plugin npm Packaging](npm-packaging.md) -- Packaging, npm publishing, and versioning
- [Plugin Private Distribution](private-distribution.md) -- Private registry workflows
- [Plugin Events Overview](overview.md) -- Event hooks for plugin lifecycle management
- [Custom Tools](../custom-tools/) -- Standalone and plugin-bundled tool definitions
- [Agents](../agents/) -- Agent definition, discovery, and configuration
- [Skills](../skills/) -- Skill format, discovery, and loading
- [Agent Discovery](../agents/discovery.md) -- How agents are located and registered

---
title: "Package Structure and Layout"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - packaging
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/plugins/npm-packaging.md"
  - knowledge: "knowledge/tooling/opencode/plugins/private-distribution.md"
  - knowledge: "knowledge/tooling/opencode/plugins/bundling-components.md"
references:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Package Structure and Layout

The `@runicengines/opencode-runesmith` plugin is the packaged delivery mechanism for all RunicEngines role-based agents, reusable skills, and plugin hooks. Understanding its directory layout and `package.json` configuration is essential for maintainers who need to add new agents, update skill definitions, or publish releases.

This document analyses the recommended package structure, explains each `package.json` field for developers coming from a Python background, and provides step-by-step consumer setup instructions.

---

## Directory Layout

The plugin follows a convention-aligned layout that mirrors OpenCode's project-level `.opencode/` directory structure. Agents and skills are bundled inside the package under `.opencode/`, and the plugin's init hook is responsible for copying them into the consumer project's `.opencode/` on first load (see [bundling-components.md] for the copy-on-init mechanism).

```
@runicengines/opencode-runesmith/
├── package.json                  # Package manifest: name, version, dependencies, publish config
├── tsconfig.json                 # TypeScript compiler options (target: ESNext, module: NodeNext)
├── .gitignore                    # Ignores node_modules/, dist/, *.tsbuildinfo
├── README.md                     # Consumer-facing: what the plugin provides and how to install
├── CHANGELOG.md                  # Release notes, version history, breaking changes
├── LICENSE                       # Proprietary license (restricted to RunicEngines org)
├── src/
│   └── index.ts                  # Plugin entry point: exports Plugin type, init hook, event handlers
├── .opencode/
│   ├── agents/                   # Agent definitions (one .md per role)
│   │   ├── rs-architect.md       # System architecture and cross-section reviews
│   │   ├── rs-developer.md       # Feature implementation and code generation
│   │   ├── rs-reviewer.md        # Code review and quality enforcement
│   │   ├── rs-test-writer.md     # Test plan generation and test implementation
│   │   ├── rs-tech-writer.md     # Documentation writing and README generation
│   │   ├── rs-devops.md          # CI/CD and infrastructure tasks
│   │   └── rs-spec-writer.md     # Specification and requirement drafting
│   └── skills/                   # Skill bundles (one SKILL.md per subdirectory)
│       ├── rs-issue-to-plan/
│       │   └── SKILL.md          # Converts GitHub issues into structured implementation plans
│       ├── rs-pr-packager/
│       │   └── SKILL.md          # Assembles PR descriptions from changelog and diff context
│       ├── rs-changelog-manager/
│       │   └── SKILL.md          # Maintains CHANGELOG.md entries per keepachangelog format
│       ├── rs-test-helper-run/
│       │   └── SKILL.md          # Runs tests with configurable framework and collects results
│       ├── rs-test-helper-diagnose/
│       │   └── SKILL.md          # Analyses test failures and suggests root causes
│       ├── rs-discover/
│       │   └── SKILL.md          # Explores codebase structure, conventions, and dependencies
│       ├── rs-dependency-checker/
│       │   └── SKILL.md          # Scans dependencies for vulnerabilities and audits lockfiles
│       ├── rs-review-methodology/
│       │   └── SKILL.md          # Defines structured review process and checklist
│       ├── rs-review-severity/
│       │   └── SKILL.md          # Classifies review findings by severity level
│       ├── rs-review-security/
│       │   └── SKILL.md          # Security pattern database for credential/injection scanning
│       ├── rs-consult/           # (future) General knowledge consultation skill
│       │   └── SKILL.md
│       ├── rs-scratchpad/         # Session scratchpad lifecycle (init, clear, status)
│       │   └── SKILL.md
│       └── ...                   # Additional skills added as the plugin evolves
└── dist/
    └── index.js                  # Compiled JavaScript output (the `main` entry point)

### Consumer Project Scratchpad: `.runesmith/`

When the plugin is installed in a consumer project, the init hook creates a `.runesmith/` directory at the project root. This is the **scratchpad** — a writable workspace for agent output, caches, and logs. It is NOT part of the plugin package; it is generated at runtime.

Each agent session writes into a session-scoped subdirectory named by the pattern `{date}-{branch}` — for example, `2026-06-07-feat-42-auth`. The session path is determined at runtime by the first agent that writes to it (typically spec-writer or architect), using the current date and git branch name. This keeps output from different branches or dates isolated.

```
<consumer-project>/
├── .opencode/
│   ├── agents/                        # Copied from plugin by init hook
│   └── skills/                        # Copied from plugin by init hook
├── .runesmith/                        # Created by init hook (gitignore recommended)
│   ├── 2026-06-07-feat-42-auth/       # Session: date-branch (created on demand)
│   │   ├── specs/                     # Spec-writer: implementation plans
│   │   ├── reports/                   # Test-writer: test results
│   │   ├── logs/                      # Architect: pipeline errors
│   │   └── cache/                     # Tech-writer: webfetch cache
│   ├── 2026-06-08-fix-108-null/       # Another session
│   │   ├── specs/
│   │   ├── reports/
│   │   ├── logs/
│   │   └── cache/
│   ├── flaky.yml                      # Global flaky test registry (shared)
│   └── security.yml                   # Global security baseline (shared)
├── .opencode/.runesmith-version       # Version stamp (written by init hook)
├── .gitignore                         # Should include .runesmith/ (see below)
└── opencode.json
```

**Recommended `.gitignore` entry:**

```
.runesmith/
```

The scratchpad is local-only by default. If a team decides to share session artifacts via the repository, they can un-ignore specific subdirectories:

```
.runesmith/*
!.runesmith/flaky.yml
```

- **`src/index.ts` as the single source of truth.** All plugin logic — the `activate` init hook, event handlers, custom tool registrations — lives in one entry file. TypeScript compiles this to `dist/index.js`, which is what OpenCode actually loads at runtime.

- **`.opencode/agents/` mirrors the project-level agent directory.** By keeping agent definitions in the same relative path they will eventually occupy in the consumer project, the init hook's copy logic stays simple: it iterates the bundle directory and copies each `.md` file to the matching project path.

- **Skill directories use the `rs-` prefix to prevent collisions.** When the init hook copies skills into the project's `.opencode/skills/`, the prefix ensures they do not conflict with skills from other plugins or user-defined skills. This is the same collision-avoidance strategy used in the agent namespace.

- **No `tools/` directory.** Custom tools (if needed in the future) are registered programmatically through the plugin's `tool` hook in `src/index.ts`, not shipped as standalone files. This is the preferred approach per OpenCode best practices (see [bundling-components.md]).

---

## `package.json` Fields Explained (for Python Developers)

The `package.json` is the npm equivalent of Python's `pyproject.toml` + `setup.py` combined. It describes the package, declares dependencies, and controls publishing behaviour.

```json
{
  "name": "@runicengines/opencode-runesmith",
  "version": "1.0.0",
  "description": "RuneSmith: AI agents and skills for RunicEngines development",

  "type": "module",
  "main": "./dist/index.js",

  "scripts": {
    "build": "tsc",
    "prepublishOnly": "npm run build",
    "version": "git add -A src/ .opencode/",
    "postversion": "git push && git push --tags"
  },

  "dependencies": {
    "@opencode-ai/plugin": "^1.0.0"
  },

  "devDependencies": {
    "typescript": "^5.5.0",
    "@types/node": "^20.0.0"
  },

  "publishConfig": {
    "registry": "https://npm.pkg.github.com",
    "access": "restricted"
  }
}
```

### Field-by-Field Breakdown

| Field | Value | Analogy in Python | Purpose |
|---|---|---|---|
| `name` | `@runicengines/opencode-runesmith` | Package name in `pyproject.toml` | Fully qualified package name. The `@runicengines` scope routes resolution to the GitHub npm registry. |
| `version` | `1.0.0` | `version` in `pyproject.toml` | Semantic version string. Must be bumped before each publish. |
| `type` | `"module"` | `"import"` style in Python | Declares that `.js` files use ES Modules (`import`/`export`) rather than CommonJS (`require`). This is like Python 3's default module system — you write `import { Plugin } from "@opencode-ai/plugin"` instead of `const { Plugin } = require(...)`. |
| `main` | `./dist/index.js` | `[project.scripts]` entry point | Tells the runtime (Node/Bun) which file to load when the package is imported. OpenCode reads this to find and execute the plugin's exported `Plugin` object. |
| `dependencies` | `{ "@opencode-ai/plugin": "^1.0.0" }` | `[project.dependencies]` in `pyproject.toml` | Runtime dependencies. The `@opencode-ai/plugin` package provides the `Plugin` TypeScript type and utility helpers (`tool()`, `tool.schema`). The caret `^` allows minor and patch updates (semver-compatible). |
| `devDependencies` | `{ "typescript": "^5.5.0" }` | `[project.optional-dependencies]` for dev tools | Build-time only dependencies. TypeScript is needed to compile `src/` to `dist/` but is not required at runtime by consumers. |
| `publishConfig.registry` | `https://npm.pkg.github.com` | Twine upload URL | Overrides the default npm registry (`registry.npmjs.org`) for publishing. Every `npm publish` pushes to GitHub Packages instead. |
| `publishConfig.access` | `"restricted"` | Private PyPI index | Ensures the package is not publicly visible. Only organisation members with `read:packages` scope can install it. |

### Key Distinctions from Python Packaging

1. **No `setup.py` / `setup.cfg` duality.** npm uses a single `package.json` for metadata, dependencies, scripts, and publish configuration. Everything is in one file.

2. **ESM `type: "module"` is the default for new packages.** Unlike Python, where `__init__.py` makes a directory importable, npm packages must explicitly opt into the module system. Without `"type": "module"`, Node/Bun assume CommonJS (`require`), which breaks `import`/`export` syntax.

3. **Dependencies are resolved at install time, not build time.** Python's `pyproject.toml` lists dependencies that are installed before the package is built. npm dependencies are installed when the consumer runs `npm install` (or when OpenCode auto-installs the plugin on startup). The plugin's own build step (`tsc`) only needs dev dependencies like TypeScript.

4. **The `scripts` block replaces Makefile / Invoke tasks.** npm scripts are the canonical way to define build, test, and publish commands. They run in a shell context where `node_modules/.bin` is on `PATH`, so `tsc` resolves without a full path.

---

## Build and Publish Workflow

The lifecycle from development to consumer installation follows these steps:

### 1. Develop in TypeScript

All plugin logic lives in `src/index.ts`. The init hook, event handlers, and tool registrations are written here. Agent `.md` files and skill `SKILL.md` files live under `.opencode/` and are plain Markdown — they do not require compilation.

### 2. Build

```bash
bun run build
# or: npx tsc
```

TypeScript compiles `src/index.ts` to `dist/index.js`. The `tsconfig.json` targets ESNext with `module: NodeNext`, producing ESM-compatible output. The `dist/` directory is what npm publishes; `src/` is development-only.

### 3. Version Bump

```bash
npm version patch   # 1.0.0 → 1.0.1 (bug fixes)
npm version minor   # 1.0.0 → 1.1.0 (new features, non-breaking)
npm version major   # 1.0.0 → 2.0.0 (breaking changes)
```

The `version` script in `package.json` automatically stages `src/` and `.opencode/` changes with `git add -A`. The `postversion` script pushes the commit and tags to the remote.

### 4. Publish

```bash
npm publish
```

With `publishConfig.registry` set to `https://npm.pkg.github.com` and `publishConfig.access` set to `restricted`, this pushes the package to the GitHub Packages registry under the `@runicengines` scope. The `prepublishOnly` script ensures `dist/` is up to date before the publish runs.

### 5. Consumer Declaration

Consumers add the plugin to their `opencode.json`:

```json
{
  "plugin": ["@runicengines/opencode-runesmith"]
}
```

On the next OpenCode startup, Bun resolves the package from the GitHub npm registry (authenticated via `.npmrc`), installs it into `~/.cache/opencode/node_modules/`, and loads `dist/index.js`. The init hook then copies the bundled agents and skills into the project's `.opencode/` directories.

---

## Consumer Setup Steps

For each developer machine that needs the plugin, four steps are required. Steps 1–2 are one-time setup; steps 3–4 are per-project.

1. **Configure `.npmrc`.** Add the scope-to-registry mapping and authentication token reference. This can go in the project's `.npmrc` or the global `~/.npmrc`:

   ```ini
   @runicengines:registry=https://npm.pkg.github.com/
   //npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
   ```

2. **Set `GITHUB_TOKEN` environment variable.** Create a classic GitHub Personal Access Token with the `read:packages` scope and export it in the shell profile (`~/.bashrc`, `~/.zshrc`, or equivalent):

   ```bash
   export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
   ```

   The token must have at minimum the `read:packages` scope. For maintainers who need to publish the plugin, `write:packages` is also required.

3. **Add the plugin to `opencode.json`.** In the project's `opencode.json` (or `~/.config/opencode/opencode.json` for global availability), add the plugin to the `plugin` array:

   ```json
   {
     "plugin": ["@runicengines/opencode-runesmith"]
   }
   ```

   Multiple plugins can be listed together:

   ```json
   {
     "plugin": [
       "@runicengines/opencode-runesmith",
       "@runicengines/opencode-deploy"
     ]
   }
   ```

4. **Restart OpenCode.** On the next startup, OpenCode detects the new plugin entry, auto-installs the package via Bun, and the init hook copies the agent/skill files into `.opencode/{agents,skills}/`. The agents and skills are immediately available for use.

   > **If agents or skills do not appear after restart**, verify that:
   > - The `.npmrc` scope mapping and token are correct (`npm view @runicengines/opencode-runesmith` should succeed).
   > - The Bun cache is clear (`rm -rf ~/.cache/opencode/node_modules` forces a reinstall).
   > - The init hook completed without errors (check OpenCode logs).

---

## Naming Convention

All agents and skills shipped with the plugin use the `rs-` prefix to prevent collisions with user-defined agents, skills from other plugins, or future OpenCode built-ins.

| Component | Pattern | Example |
|---|---|---|
| Agent file | `rs-{role}.md` | `rs-architect.md`, `rs-developer.md` |
| Skill directory | `rs-{name}/` | `rs-issue-to-plan/`, `rs-pr-packager/` |
| Skill file | `rs-{name}/SKILL.md` | `rs-issue-to-plan/SKILL.md` |

The `rs-` prefix is short for **RuneSmith**. It is applied consistently across all bundled components and is never omitted. External agents that reference a RuneSmith skill do so by its prefixed name (e.g., `skill({ name: "rs-issue-to-plan" })`).

---

## Summary

The package structure follows the standard OpenCode plugin blueprint with three customisations specific to RuneSmith's multi-agent scope:

1. **Bundled `.opencode/` directory** ships all agents and skills inside the package rather than requiring a separate distribution channel for each component.
2. **`rs-` prefix** on all agent and skill names prevents namespace collisions in the consumer's `.opencode/` directory.
3. **Init hook copy mechanism** bridges the gap between plugin packaging (npm) and OpenCode's auto-discovery (filesystem scan), ensuring bundled components land in a discoverable location without manual effort.

The `package.json` configuration is deliberately minimal — a single runtime dependency (`@opencode-ai/plugin`), a single build dependency (TypeScript), and a publish config that targets the private GitHub Packages registry. This keeps the maintenance surface small for a team of Python developers who interact with npm primarily through this one package.

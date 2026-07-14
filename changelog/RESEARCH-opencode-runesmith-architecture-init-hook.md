---
title: "Plugin Init Hook Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - init-hook
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/plugins/init-hook-lifecycle.md"
  - knowledge: "knowledge/tooling/opencode/plugins/bundling-components.md"
  - knowledge: "knowledge/tooling/opencode/js-for-python-devs/"
references:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin Init Hook Design

## Context

The `@runicengines/opencode-runesmith` plugin bundles three component types that must be installed into the consuming project's `.opencode/` directory: role-based agent `.md` files, reusable skill instruction bundles, and MCP server definitions. OpenCode loads agents from `.opencode/agents/` and skills from `.opencode/skills/` on startup, but the plugin's npm package lives in `~/.cache/opencode/node_modules/` — outside the project tree. An init hook bridges this gap: it runs during plugin activation and copies bundled files into the project's `.opencode/` tree so OpenCode can discover them.

This document designs that init hook: its lifecycle, the copy logic, version-stamping for update detection, error handling, and the developer experience across first install, updates, and normal startup.

## Init Hook Purpose

The init hook has three operating modes depending on the state of the project's `.opencode/` directory:

### 1. First Install

When a developer adds `"@runicengines/opencode-runesmith"` to their `opencode.json` and restarts OpenCode, the plugin is downloaded and cached by Bun. The init hook runs during `activate()` and finds no version stamp file in `.opencode/`. It performs a full copy of all agent and skill files from the bundled package into the project tree.

The developer sees no visible difference — the copy happens before the UI renders — but all agents and skills are immediately available for use.

### 2. Update

When a new version of the plugin is published and the developer clears the Bun cache (`rm -rf ~/.cache/opencode/node_modules/`), the next startup downloads the new package version. The init hook finds that the existing version stamp in `.opencode/` does not match the installed `package.json` version. It clears the previously copied files and re-copies from the updated package.

### 3. Normal Startup

When the version stamp matches the installed package version, the hook performs no file operations. It registers any event hooks the plugin needs and returns immediately. This is the hot path — it should complete in under 10 ms.

## Init Hook Code Sketch

The following TypeScript implementation covers the full lifecycle. It is designed for an ESM plugin entry point, which is the standard for OpenCode plugins distributed via npm.

```typescript
import type { Plugin } from "@opencode-ai/plugin";
import {
  copyFileSync,
  cpSync,
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  writeFileSync,
} from "fs";
import { join, dirname, basename } from "path";
import { fileURLToPath } from "url";

const STAMP_FILE = ".runesmith-version";

/**
 * Read the version stamp from the project's .opencode/ directory.
 * Returns null if the file is missing or corrupted.
 */
function readStamp(stampPath: string): string | null {
  try {
    if (!existsSync(stampPath)) return null;
    const content = readFileSync(stampPath, "utf-8").trim();
    // Validate it looks like a semver string
    if (!/^\d+\.\d+\.\d+$/.test(content)) return null;
    return content;
  } catch {
    return null;
  }
}

/**
 * Write the version stamp after a successful copy.
 */
function writeStamp(stampPath: string, version: string): void {
  mkdirSync(dirname(stampPath), { recursive: true });
  writeFileSync(stampPath, version, "utf-8");
}

/**
 * Copy bundled agent .md files from the package to the project's .opencode/agents/.
 */
function copyAgents(srcDir: string, destDir: string): void {
  const agentsDir = join(srcDir, ".opencode", "agents");
  if (!existsSync(agentsDir)) {
    console.warn("[runesmith] No bundled agents directory found, skipping.");
    return;
  }

  const destAgents = join(destDir, "agents");
  mkdirSync(destAgents, { recursive: true });

  const entries = readdirSync(agentsDir);
  for (const entry of entries) {
    if (!entry.endsWith(".md")) continue;
    copyFileSync(join(agentsDir, entry), join(destAgents, entry));
  }
}

/**
 * Copy bundled skill directories from the package to the project's .opencode/skills/.
 */
function copySkills(srcDir: string, destDir: string): void {
  const skillsDir = join(srcDir, ".opencode", "skills");
  if (!existsSync(skillsDir)) {
    console.warn("[runesmith] No bundled skills directory found, skipping.");
    return;
  }

  const destSkills = join(destDir, "skills");
  mkdirSync(destSkills, { recursive: true });

  const entries = readdirSync(skillsDir);
  for (const entry of entries) {
    const srcPath = join(skillsDir, entry);
    const destPath = join(destSkills, entry);
    // Use recursive copy for skill directories (each skill has SKILL.md + scripts)
    cpSync(srcPath, destPath, { recursive: true });
  }
}

/**
 * Main setup routine: copy agents and skills, then write version stamp.
 */
function createScratchpad(projectRoot: string): void {
  // Create the base .runesmith directory and the non-user-visible config files.
  // Session-scoped subdirectories ({date}-{branch}/) are created on demand
  // by the first agent that writes to them, using the current date and git branch.
  mkdirSync(join(projectRoot, ".runesmith"), { recursive: true });
}

function setup(
  runesmithDir: string,
  packageRoot: string,
  version: string,
  stampPath: string,
  projectRoot: string,
): void {
  createScratchpad(projectRoot);
  copyAgents(packageRoot, runesmithDir);
  copySkills(packageRoot, runesmithDir);
  writeStamp(stampPath, version);
}

export const RuneSmithPlugin: Plugin = async ({ project }) => {
  const __dirname = dirname(fileURLToPath(import.meta.url));
  // In a bundled npm package, __dirname points to the package root
  // where .opencode/agents/ and .opencode/skills/ live.
  const packageRoot = join(__dirname, "..");

  const runesmithDir = join(project.path, ".opencode");
  const stampPath = join(runesmithDir, STAMP_FILE);

  // Read the installed plugin version from its own package.json
  let pluginVersion: string;
  try {
    const pkg = JSON.parse(
      readFileSync(join(packageRoot, "package.json"), "utf-8"),
    );
    pluginVersion = pkg.version;
  } catch {
    console.warn(
      "[runesmith] Could not read package.json version, skipping setup.",
    );
    return { /* hooks only */ };
  }

  // Check version stamp
  const currentVersion = readStamp(stampPath);
  if (currentVersion === pluginVersion) {
    return { /* hooks only, no setup needed */ };
  }

  // Version mismatch or first install: copy files
  try {
    setup(runesmithDir, packageRoot, pluginVersion, stampPath, project.path);
    console.log(`[runesmith] Setup complete (version ${pluginVersion}).`);
  } catch (err) {
    console.warn("[runesmith] Setup failed, continuing with hooks only:", err);
  }

  return {
    // Event hooks registered here
  };
};
```

### Key Design Points

- **`package.json` as version source of truth**: The plugin version is read from the installed package's `package.json`. This avoids version drift between a hardcoded constant and the published artifact.
- **`console.warn` for failures**: The hook fails open — a copy error does not prevent the plugin from loading its event hooks.
- **Agent and skill directory separation**: `copyAgents` handles individual `.md` files; `copySkills` handles directories recursively. Skills are directories containing `SKILL.md` and supporting scripts, whereas agents are single `.md` files.

## What to Copy

The plugin package is structured with the following layout inside its npm tarball:

```
opencode-runesmith/
├── package.json
├── index.js                  # Plugin entry point (compiled from index.ts)
├── .opencode/
│   ├── agents/
│   │   ├── architect.md
│   │   ├── developer.md
│   │   ├── reviewer.md
│   │   └── tech-lead.md
│   └── skills/
│       ├── rs-discover/       # Skill directory
│       │   ├── SKILL.md
│       │   └── discover-script.sh
│       ├── rs-consult/
│       │   ├── SKILL.md
│       │   └── query.js
│       └── rs-validate/
│           ├── SKILL.md
│           └── rules.yaml
```

The init hook copies:
- **Agents**: Each `.md` file in `.opencode/agents/` is copied via `copyFileSync` to the project's `.opencode/agents/`. Old files with matching names are overwritten.
- **Skills**: Each subdirectory in `.opencode/skills/` is copied recursively via `cpSync(src, dest, { recursive: true })`. Entire directories are replaced on update.

MCP server definitions (`.opencode/mcp/`) are intentionally excluded from this design. MCP servers are declared in `opencode.json` directly, not as files in `.opencode/mcp/`. If the plugin needs to register MCP servers, it should export them via the plugin's `mcp` configuration point rather than writing files.

## Version-Stamping Logic

The version stamp is a plain text file at `.opencode/.runesmith-version` containing a single semver string (e.g., `1.0.0`).

| Condition | Action |
|---|---|
| File missing (first install) | Full copy; write stamp |
| File exists, content matches `pluginVersion` | Skip — no-op |
| File exists, content differs from `pluginVersion` | Full copy (overwrite); write stamp |
| File exists, content is not valid semver | Treat as missing; full copy; write stamp |

### File Format

```
1.0.0
```

No trailing newline is required. The `readStamp` function trims whitespace and validates the content against the regex `/^\d+\.\d+\.\d+$/`. Any content that does not match — including prerelease suffixes like `1.0.0-beta.1` — is treated as invalid, which forces a re-copy.

### Why Not JSON or YAML?

A single-line plain text file is the simplest possible format. It can be read with a single `readFileSync` call, parsed without a dependency, and written atomically. There is no need for structured data — the stamp stores exactly one value.

## Update Propagation

OpenCode caches npm plugins permanently in `~/.cache/opencode/node_modules/`. Bun does not check for newer versions on every startup. This means publishing a new version of `@runicengines/opencode-runesmith` does not automatically update installed copies.

The update workflow is:

1. Maintainer publishes `v1.1.0` to GitHub Packages.
2. Developer runs `rm -rf ~/.cache/opencode/node_modules/@runicengines/opencode-runesmith`.
3. Developer restarts OpenCode.
4. Bun re-downloads the package — version `1.1.0` is now installed.
5. Init hook runs: `readStamp` returns `"1.0.0"` (or whatever was last written), `pluginVersion` is `"1.1.0"`.
6. Mismatch detected: `setup()` runs, overwriting `.opencode/agents/` and `.opencode/skills/` with the new files.
7. Stamp is updated to `"1.1.0"`.

### User Modification Warning

Any modifications the developer has made to files inside `.opencode/agents/` or `.opencode/skills/` are **overwritten** during an update. The init hook does not attempt to merge or preserve local changes. This is a deliberate choice — the plugin owns those files. Developers who need custom agents or skills should create them in separate files outside the plugin-managed set.

A future improvement could add a `.runesmith-ignore` mechanism that exempts specific filenames from overwrite, but that is out of scope for the initial implementation.

## Error Handling

The init hook follows a **fail-open** strategy: a copy failure must not prevent the plugin from loading its event hooks. All file operations are wrapped in try/catch blocks.

| Failure Scenario | Behaviour |
|---|---|
| `package.json` unreadable | Log warning, skip setup, return hooks only |
| Stamp file corrupted | Treated as missing → full re-copy |
| Source `.opencode/agents/` missing (partial install) | Log warning, skip agent copy |
| Source `.opencode/skills/` missing | Log warning, skip skill copy |
| `copyFileSync` or `cpSync` fails (permissions, disk full) | Log warning with error details, continue |
| `writeStamp` fails | Setup is considered incomplete; next startup will attempt again |

The console warnings use the `[runesmith]` prefix for easy grepping:

```
[runesmith] No bundled agents directory found, skipping.
[runesmith] Setup failed, continuing with hooks only: EACCES: permission denied ...
[runesmith] Setup complete (version 1.0.0).
```

## Python Developer Notes

The RunicEngines team primarily writes Python. These notes map the Node.js APIs used in the init hook to their Python equivalents.

| Node.js API | Python Equivalent | Notes |
|---|---|---|
| `copyFileSync(src, dest)` | `shutil.copy(src, dest)` | Copies a single file; destination can be a directory |
| `cpSync(src, dest, { recursive: true })` | `shutil.copytree(src, dest, dirs_exist_ok=True)` | Recursively copies a directory tree; Python 3.8+ `dirs_exist_ok` avoids `FileExistsError` |
| `existsSync(path)` | `os.path.exists(path)` | Returns `True`/`False` |
| `mkdirSync(path, { recursive: true })` | `os.makedirs(path, exist_ok=True)` | Creates parent directories if needed; `exist_ok=True` suppresses errors for existing directories |
| `readdirSync(dir)` | `os.listdir(dir)` | Lists directory entries as strings |
| `readFileSync(path, "utf-8")` | `open(path).read()` | Reads entire file as string; `with` statement recommended in Python |
| `writeFileSync(path, content)` | `open(path, "w").write(content)` | Writes string to file |
| `join(a, b)` | `os.path.join(a, b)` | Platform-aware path joining |
| `dirname(path)` | `os.path.dirname(path)` | Parent directory of a path |
| `basename(path)` | `os.path.basename(path)` | Final component of a path |

The key conceptual difference is synchronous vs. asynchronous I/O. Node.js exposes both synchronous (`*Sync`) and asynchronous (`async/await`) APIs. The init hook uses synchronous calls because it runs during startup before the event loop is fully active. In Python, the equivalent operations would typically be synchronous as well, though `asyncio.to_thread` or `os.scandir` could be used for non-blocking alternatives.

## Summary

The init hook design for `@runicengines/opencode-runesmith` provides:

1. **Automatic provisioning** of agent and skill files on first install, with no manual copy steps.
2. **Deterministic update detection** via a semver stamp file, decoupled from the sticky npm cache.
3. **Fail-open error handling** that guarantees the plugin's event hooks load even if file operations fail.
4. **Simple file-based version tracking** with no external dependencies — a single `.runesmith-version` file in `.opencode/`.
5. **Clear overwrite semantics** — the plugin owns the files it creates; local modifications are replaced on update.

This design is now ready for implementation. The next steps are to build the init hook, write tests for each failure scenario, and integrate it into the plugin's `activate()` export in the `@runicengines/opencode-runesmith` package.

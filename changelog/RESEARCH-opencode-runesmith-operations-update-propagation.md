---
title: "Update Propagation Strategy"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - update
  - versioning
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/plugins/bundling-components.md"
  - knowledge: "knowledge/tooling/opencode/plugins/init-hook-lifecycle.md"
  - knowledge: "knowledge/tooling/opencode/plugins/loading.md"
references:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Update Propagation Strategy

- **Plugin:** `@runicengines/opencode-runesmith`
- **Distribution:** Private npm via GitHub Packages
- **Status:** Draft analysis

## Problem Statement

The `@runicengines/opencode-runesmith` plugin ships a collection of agent `.md` files and skill directories that must be copied into the project's `.opencode/` directory at install time. OpenCode uses an init hook — a JavaScript module that runs once when the plugin is first loaded — to perform this copy. The design works well for initial installation but introduces a subtle and significant problem when the plugin is updated.

OpenCode caches npm plugins permanently in `~/.cache/opencode/node_modules/`. Once a plugin is cached, `opencode restart` does **not** pull newer versions from the registry. The init hook runs every startup, but the current implementation uses a guard — `if (!existsSync(dest))` — that only copies files that do not already exist. As a result:

1. A user installs `@runicengines/opencode-runesmith@1.0.0`.
2. The init hook copies agent files and skill directories into `.opencode/`.
3. The user publishes `@runicengines/opencode-runesmith@2.0.0` with updated agents and skills.
4. The user runs `opencode restart` expecting the new version.
5. OpenCode's cache still holds `1.0.0`. The init hook runs against the cached copy.
6. Even after cache bust (deleting `~/.cache/opencode/node_modules/`), the `existsSync` guard prevents overwriting the existing `.opencode/` files.
7. The user is stuck on stale agent and skill definitions with no clear path to update.

This document analyzes solutions to the update propagation problem and recommends a strategy for `@runicengines/opencode-runesmith`.

## Solution Comparison

| Criterion | Option A: Version-Stamping | Option B: Symlinks | Option C: CLI Update Command | Option D: Global Install |
|---|---|---|---|---|
| **Automatic updates** | Yes, on startup | Yes, always in sync | No, requires manual invocation | Yes, on startup |
| **Per-project isolation** | Full | Full (project links to own cache) | Full | None — all projects share one set |
| **Cross-platform** | Universal | Windows symlink issues require elevation or fallback | Universal | Universal |
| **Overwrite safety** | Version gated — only overwrites on version change | N/A — always reflects cache | Explicit invocation | Version gated |
| **Complexity** | Low — one stamp file + comparison | Low — symlink logic + fallback | Medium — CLI subcommand + cache purge | Low — single target directory |
| **OpenCode compatibility** | No assumptions — pure file ops | Depends on OpenCode following symlinks during discovery | Standard npm plugin subcommand | Depends on OpenCode scanning `~/.config/opencode/` |
| **User awareness** | Transparent | Transparent | Requires remembering to run it | Transparent |

### Option A: Version-Stamping (Recommended)

The init hook writes a `.runesmith-version` file into `.opencode/` containing the semver string of the installed plugin. On every startup, it reads this file and compares it against `package.version`. A mismatch triggers a full re-copy of all agent and skill files, then the stamp is updated. This is the recommended approach because it is simple, cross-platform, and requires zero user intervention.

### Option B: Symlinks

Instead of copying, the init hook creates symbolic links from `.opencode/agents/*` and `.opencode/skills/*` pointing into the plugin's cache directory. Updates propagate automatically because the links always resolve to whatever version is cached. The risk is that OpenCode's file discovery may not follow symlinks (depending on the implementation), and symlink creation on Windows often requires administrator privileges or developer-mode enabled. A copy-based fallback would add nearly as much complexity as version-stamping.

### Option C: CLI Update Command

Ship a subcommand (`bunx @runicengines/opencode-runesmith update`) that clears the npm cache for the plugin and re-triggers the copy. This gives the user explicit, intentional control. The drawback is that it depends on the user remembering to run the command — it does not solve the "stale after restart" problem on its own.

### Option D: Global Install

Install agents and skills into `~/.config/opencode/{agents,skills}/` instead of the project's `.opencode/`. Re-copy on version mismatch, same stamp logic as Option A. All projects on the same machine share one set of agents and skills. This is useful for workspaces with many repositories, but it sacrifices per-project customization — a team using `@runicengines/opencode-runesmith@1.0.0` for one project and `@runicengines/opencode-runesmith@2.0.0` for another cannot use global install without conflict.

## Recommended Strategy: Version-Stamping + CLI Update Command

The recommended approach combines Option A as the primary mechanism with Option C as a safety valve.

### How It Works

**Init hook flow (every startup):**

```
1. Determine installed version from package.json
   const { version } = JSON.parse(readFileSync('./package.json', 'utf-8'));

2. Determine stamped version from .opencode/
   const stampPath = join(opencodeDir, '.runesmith-version');
   const stamped = readStamp(stampPath); // returns null if missing

3. If stamped !== version, re-copy and update stamp
   if (stamped !== version) {
     syncDirectory(agentsSrc, agentsDest);
     syncDirectory(skillsSrc, skillsDest);
     writeFileSync(stampPath, version, 'utf-8');
   }
```

**Sync logic — always overwrite on mismatch:**

```javascript
import { existsSync, mkdirSync, readdirSync, copyFileSync } from "fs";
import { join } from "path";

function syncDirectory(src, dest) {
  if (!existsSync(dest)) {
    mkdirSync(dest, { recursive: true });
  }
  const entries = readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = join(src, entry.name);
    const destPath = join(dest, entry.name);
    if (entry.isDirectory()) {
      syncDirectory(srcPath, destPath);
    } else {
      copyFileSync(srcPath, destPath);
    }
  }
}
```

The key design choice: **always overwrite** on version mismatch. Files under `.opencode/agents/` and `.opencode/skills/` are owned by the plugin — user modifications to those files are explicitly unsupported. Users who need custom agent or skill definitions should place them in separate files outside the plugin's managed set.

**Stamp format:**

```
1.2.3
```

A plain text file containing a single semver string. No JSON, no YAML — minimal parsing, minimal failure surface.

### CLI Update Command

The `update` subcommand handles the case where the user knows a new version exists and wants to force a refresh:

```
bunx @runicengines/opencode-runesmith update
```

Implementation sketch:

```javascript
// src/cli/update.js
import { execSync } from "child_process";
import { join } from "path";
import { existsSync, unlinkSync } from "fs";

async function run() {
  // 1. Clear the npm cache entry for this plugin
  execSync('npm cache clean --force', { stdio: 'inherit' });

  // 2. Reinstall to get latest
  const pkg = '@runicengines/opencode-runesmith';
  execSync(`npm install ${pkg}@latest`, { stdio: 'inherit', cwd: process.cwd() });

  // 3. Delete the stamp to force re-copy on next startup
  const stampPath = join(process.cwd(), '.opencode', '.runesmith-version');
  if (existsSync(stampPath)) {
    unlinkSync(stampPath);
  }

  console.log(`Updated ${pkg} to latest. Restart opencode to apply changes.`);
}
```

The CLI command is a convenience layer — the core update logic always runs in the init hook. The CLI exists for users who want to proactively trigger an update rather than waiting for the next restart.

## Edge Cases

### User modified a copied agent file

If the user edits an agent `.md` file inside `.opencode/agents/` and a plugin update arrives, the sync will overwrite their changes without warning. This is intentional. The plugin's agent and skill definitions are treated as owned artifacts. Users who need custom behavior should create their own agent files with distinct names and reference the plugin's agents via `extends` or explicit includes.

**Recommendation:** Add a warning log line when overwriting files during sync, but do not skip files. Skipping would leave the user with a broken partial update.

### Multiple projects with different plugin versions

Each project's `.opencode/.runesmith-version` is independent. Project A pins `@runicengines/opencode-runesmith@1.0.0` and Project B uses `2.0.0`. Both work correctly because each init hook checks its own stamp file against its own cached `package.json`. No cross-project interference.

### Fresh install vs upgrade vs rollback

All three scenarios are handled by the same version comparison:

- **Fresh install:** No `.runesmith-version` exists. `stamped` is `null`. `null !== version` → copy runs. Stamp created.
- **Upgrade:** `stamped` is `1.0.0`, `version` is `2.0.0`. Mismatch → copy runs. Stamp updated to `2.0.0`.
- **Rollback:** `stamped` is `2.0.0`, `version` (from pinned install) is `1.0.0`. Mismatch → copy runs. Stamp updated to `1.0.0`. The sync overwrites files to match the older version. This is correct behavior — the project is opting into the older plugin version.

### OpenCode cache staleness

Even with version-stamping, if OpenCode's `~/.cache/opencode/node_modules/` holds an old version, the init hook sees the old `package.version` and the stamp matches — no copy occurs. The CLI `update` command handles this by purging the cache entry. A future enhancement could check the npm registry for the latest version matching the project's semver range and warn on mismatch.

### Stamp file corruption

If `.runesmith-version` is corrupted (e.g., truncated write, invalid semver), the comparison fails safely: the read function returns `null`, triggering a re-copy. This is a self-healing property of the design.

## Conclusion

Version-stamping provides automatic, transparent update propagation for `@runicengines/opencode-runesmith` agent and skill files. The CLI update command gives users an escape hatch for cache staleness. Together they form a robust strategy that handles fresh installs, upgrades, rollbacks, and multi-project setups without requiring changes to OpenCode itself.

---
title: "Distribution Strategy Comparison for the RuneSmith Plugin"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - distribution
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/plugins/architecture.md"
  - knowledge: "knowledge/tooling/opencode/plugins/npm-packaging.md"
  - knowledge: "knowledge/tooling/opencode/plugins/private-distribution.md"
references:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
  - url: "https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-npm-registry"
    title: "GitHub Packages npm Registry"
last_audit_date: 2026-06-07
---

# Distribution Strategy Comparison for the RuneSmith Plugin

## Context

The `@runicengines/opencode-runesmith` plugin is an internal OpenCode plugin for the RunicEngines cooperative. It bundles three component types: role-based agents (architect, developer, reviewer, etc.), reusable skill instruction bundles, and MCP servers for extended capabilities. As a private plugin developed by Python programmers for an internal cooperative, the distribution mechanism must balance ease of installation, version control, authentication overhead, and update propagation across developer machines.

The plugin is not intended for public consumption. It lives within the RunicEngines GitHub organisation, and every developer who uses it is a co-op member with GitHub access. This constraint informs every distribution option considered below.

The following design decisions have already been locked:

| Decision | Value |
|---|---|
| Plugin name | `@runicengines/opencode-runesmith` |
| Skill prefix | `rs-` (e.g., `rs-discover`, `rs-consult`) |
| Distribution | Private npm via GitHub Packages |
| Install | `"plugin": ["@runicengines/opencode-runesmith"]` in `opencode.json` |
| Agent/skill storage | Copied from plugin into `.opencode/{agents,skills}/` via init hook |
| License | Restricted/private |

This document evaluates four distribution approaches, compares them systematically, and provides a detailed rationale for the chosen path.

## Approach A: npm Plugin via GitHub Packages (Chosen)

The plugin is published as a scoped npm package to the GitHub Packages registry at `https://npm.pkg.github.com` under the `@runicengines` organisation. Publication uses `publishConfig: { access: "restricted" }` in `package.json` to keep the package private to the organisation.

### How It Works

- `package.json` declares `"name": "@runicengines/opencode-runesmith"` with `"publishConfig": { "registry": "https://npm.pkg.github.com", "access": "restricted" }`.
- Publishing runs `npm publish` (or `bun publish`), which pushes the package to GitHub Packages, associating it with the plugin's GitHub repository.
- Consumers configure `.npmrc` to map the `@runicengines` scope to the GitHub registry and authenticate with a `GITHUB_TOKEN` or personal access token:
  ```ini
  @runicengines:registry=https://npm.pkg.github.com/
  //npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
  ```
- Developers add `"plugin": ["@runicengines/opencode-runesmith"]` to their `opencode.json`. On next startup, OpenCode auto-installs the package via Bun into `~/.cache/opencode/node_modules/`.
- An init hook (registered in the plugin's `activate` export) copies agent and skill files from the installed package into the project's `.opencode/{agents,skills}/` directories on first load.

### Pros

- **Auto-install**: No manual setup beyond `.npmrc` configuration and the `opencode.json` entry. Bun handles resolution and installation transparently at startup.
- **Versioned**: Each publish creates an immutable version in the registry. Developers pin behaviour by whichever version is current when they first install, and can update explicitly.
- **Single source of truth**: The registry is the authoritative distribution point. There is no ambiguity about which copy is canonical.
- **Standard OpenCode pattern**: The npm plugin pathway is the documented, community-standard way to distribute plugins. It receives first-class support and testing from the OpenCode maintainers.
- **Access control**: GitHub repository permissions govern who can read (`read:packages`) and write (`write:packages`) to the package.

### Cons

- **Requires auth setup**: Every developer must configure `.npmrc` with a `GITHUB_TOKEN` environment variable. This is a one-time friction point that must be documented in onboarding.
- **npm cache is sticky**: Bun caches installed packages in `~/.cache/opencode/node_modules/`. After a new version is published, developers must clear the cache (`rm -rf ~/.cache/opencode/node_modules`) or bump the package version in `opencode.json` (not directly supported) to trigger a re-install.
- **Windows path considerations**: While Bun handles cross-platform npm resolution, the init hook that copies files into `.opencode/` must use platform-aware path joins to avoid issues with Windows backslashes.

## Approach B: Global Config Directory

Place agent and skill definition files directly into the user's global OpenCode configuration directory (`~/.config/opencode/{agents,skills}/`). Distribution happens via a git clone of the plugin repository followed by a symlink or copy script.

### How It Works

- The plugin repository is cloned to a known location (e.g., `~/src/opencode-runesmith/`).
- A setup script creates symbolic links from `~/.config/opencode/agents/` to the relevant files in the cloned repo, or copies them directly.
- Updates are pulled via `git pull` in the cloned repository, and the symlinks automatically reflect changes.

### Pros

- **No authentication**: Files live on disk, accessible immediately after clone. No token management, no registry configuration.
- **Simple updates**: `git pull` fetches the latest definitions with no npm or cache layer involved.
- **No cache issues**: Since files are loaded directly from disk (for local plugins) or via symlinks, there is no npm cache to bust.

### Cons

- **Manual setup step**: The clone-and-link workflow is not automatic. Each developer must run the setup script, and onboarding documentation must cover it.
- **No versioning**: There is no registry-enforced version pinning. A `git pull` always fetches `HEAD` of the configured branch. Developers who want a specific version must use git tags and manually `git checkout`.
- **No auto-install**: OpenCode does not scan global config directories for plugin registration. The plugin must be loaded as a local plugin or the files must be placed in a location OpenCode already watches.
- **Global state mutation**: Writing agent/skill definitions to `~/.config/opencode/` modifies the user's global OpenCode state, which could conflict with other plugins or manual agent definitions.

## Approach C: Per-Project Copy via Setup Script

Distribute the plugin as a template repository or archive. Each project runs a setup script that copies agent and skill files into the project's `.opencode/` directory.

### How It Works

- The plugin repository serves as a template or release artifact.
- A CLI script (e.g., `bash <(curl -s https://raw.githubusercontent.com/.../setup.sh)`) downloads and extracts the latest release into `.opencode/{agents,skills}/`.
- Alternatively, the template is cloned and a script copies the relevant subdirectories.

### Pros

- **Explicit per-project control**: Each project has its own copy. Changes to one project do not affect another.
- **No npm dependency**: No registry, no token, no `@scope` resolution. Works offline after initial download.
- **No cache issues**: Files are on disk, loaded directly. No package manager caching layer.

### Cons

- **Manual step per project**: Every new project or onboarding requires running the setup script.
- **Update propagation is fully manual**: When a new version of the plugin is released, each project must re-run the setup script to update. There is no notification mechanism. Different projects can (and will) drift to different versions.
- **No versioning**: Unless the setup script accepts a version parameter and the release artifact supports versioned downloads, there is no version pinning. Even with versioned downloads, there is no automated way to know which version a project has.
- **Source of truth ambiguity**: Once files are copied, the project's `.opencode/` is disconnected from the plugin repository. There is no traceable link back to the source version.

## Approach D: Git Submodule

The plugin repository is added as a git submodule inside each consuming project. Agent/skill definitions are loaded from the submodule path, either directly or via a local plugin wrapper.

### How It Works

- `git submodule add git@github.com:RunicEngines/opencode-runesmith.git plugins/opencode-runesmith`
- A local plugin file in `.opencode/plugins/runesmith-local.ts` imports or references the submodule's exported plugin, which in turn registers the agents and skills.

### Pros

- **Git-native version pinning**: Submodules pin to a specific commit. Developers control exactly which version they use and can update explicitly.
- **No registry dependency**: Everything lives in git. No npm registry, no token management.

### Cons

- **Submodule complexity**: Git submodules are notoriously confusing for developers who do not use them regularly. Forgetting `--recursive` on clone, detached HEAD states, and merge conflicts on submodule pointer changes are common pain points.
- **Steep learning curve for Python developers**: The RunicEngines team primarily writes Python. Git submodules are an advanced git feature that most Python developers encounter infrequently.
- **Merge conflicts**: When multiple branches update the submodule pointer, merge conflicts on the submodule commit hash are opaque and hard to resolve.
- **No auto-install**: OpenCode does not understand git submodules. The plugin must still be loaded as a local plugin, which means a wrapper file in `.opencode/plugins/` is required.
- **Clone overhead**: Every consumer project must clone the full plugin repository history, even though only the current set of agent/skill files is needed.

## Comparison Matrix

| Criterion | A: npm + GitHub Packages | B: Global Config Dir | C: Per-Project Copy | D: Git Submodule |
|---|---|---|---|---|
| **Setup effort** | Medium (one-time .npmrc + token) | Medium (clone + symlink script) | Medium (run setup script per project) | High (submodule init + wrapper) |
| **Auth required** | Yes (GITHUB_TOKEN) | No | No | No (git SSH key, already set up) |
| **Auto-install** | Yes (Bun at startup) | No | No | No |
| **Versioning** | Yes (registry semver) | Partial (git tags only) | No | Yes (commit pinning) |
| **Update propagation** | Automated (new publish → cache clear on next startup after cache bust) | Manual (git pull) | Manual (re-run setup per project) | Manual (git submodule update) |
| **Windows compatibility** | Good (Bun cross-platform) | Good (symlinks need admin or fallback to copy) | Good | Good (git is cross-platform) |
| **Learning curve (Python devs)** | Low (npm concepts are straightforward) | Low (git + symlinks) | Low (script invocation) | High (submodule workflow) |

## Recommendation: Approach A — npm via GitHub Packages

Approach A is the recommended and chosen distribution strategy. The decision rests on three primary arguments:

### 1. The auth overhead is a one-time cost that pays for itself

The `.npmrc` + `GITHUB_TOKEN` setup is the single point of friction in Approach A. However, every developer in RunicEngines already has a GitHub account with repository access. Creating a classic PAT with `read:packages` scope is a two-minute operation that is performed once per developer. After that initial setup, every subsequent interaction — install, update, reinstall on a new machine — is fully automatic.

Compare this to the alternatives: Approach B requires a setup script that must be maintained separately. Approach C requires repeating a manual step for every project. Approach D requires developers to learn and debug git submodule workflows. The one-time auth cost of Approach A is lower than the recurring costs of any alternative.

### 2. Auto-install is the killer feature

OpenCode's Bun-based auto-install means that adding `"@runicengines/opencode-runesmith"` to `opencode.json` is the only action a developer ever needs to take. On the next startup, the plugin, its agents, its skills, and its MCP servers are all available. There is no clone step, no copy step, no symlink management, no submodule init.

For a cooperative where new projects spin up frequently, and developers may work across multiple machines, auto-install eliminates the "did I set up the plugin?" question. If `opencode.json` says it is there, it is there.

### 3. Version-stamping in the init hook solves the cache staleness problem

The sticky npm cache is the most common objection to Approach A. When a new version is published, developers who already have the old version cached will not see the update until the cache is cleared.

The solution is to implement version-stamping in the plugin's init hook:

- During `activate()`, the init hook reads the installed package version from `package.json` (available at the package root).
- It writes this version string to a marker file, e.g., `.opencode/.runesmith-version`.
- On subsequent startups, the hook compares the marker file version against the currently installed package version. If they differ, it clears the relevant agent/skill files from `.opencode/{agents,skills}/` and re-copies them from the updated package.
- This effectively creates a manual cache-busting mechanism at the application level, decoupling update propagation from the npm cache lifecycle.

With this approach, updating the plugin is a two-step workflow for the developer:

1. Run `rm -rf ~/.cache/opencode/node_modules` to clear the npm cache (or use a publish-aware helper script).
2. Restart OpenCode. The init hook detects the new version and refreshes the agent/skill files.

This is not zero-touch, but it is deterministic and scriptable, unlike the implicit version drift of Approaches B and C.

### 4. Organisational alignment

GitHub Packages is already part of RunicEngines' GitHub subscription. There is no additional cost or third-party dependency. The `@runicengines` scope is already available. Publishing to the same platform where the code lives reduces operational overhead.

## Open Questions

1. **Version numbering strategy**: Should the plugin follow semver strictly, or use a date-based scheme (e.g., `2026.06.07`) given that it is consumed by human developers who reason in calendar time?

2. **Backward compatibility guarantee**: When the plugin's agent definitions or skill interfaces change, do old projects continue to work with old cached versions? What constitutes a breaking change in an agent definition?

3. **Release workflow**: Should publishing be manual (`npm publish` from a maintainer's machine) or automated via GitHub Actions on tag push? An automated workflow reduces human error but requires a `GITHUB_TOKEN` with `write:packages` scope in CI.

4. **Multiple concurrent versions**: If two projects need different versions of the plugin (e.g., one pinned to v1.2 while another uses v2.0), how does the init hook handle coexisting agent/skill definitions? The current design assumes one version per machine.

5. **Offline development**: The auto-install mechanism requires network access to the GitHub npm registry on the first startup or after a cache clear. How should developers working offline (e.g., on a plane) bootstrap or update the plugin?

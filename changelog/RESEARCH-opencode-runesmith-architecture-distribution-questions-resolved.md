---
title: "RuneSmith Distribution Questions — Resolved"
status: exploring
author: "refactorartist (Khalid Zubair)"
date: 2026-06-09
tags:
  - opencode
  - runesmith
  - distribution
  - versioning
  - release
sources:
  - knowledge: "knowledge/tooling/opencode/plugins/versioning.md"
  - knowledge: "knowledge/tooling/opencode/plugins/publishing-workflow.md"
  - knowledge: "knowledge/tooling/opencode/plugins/npm-packaging.md"
  - knowledge: "knowledge/tooling/opencode/plugins/bundling-components.md"
  - knowledge: "knowledge/tooling/opencode/plugins/private-distribution.md"
  - knowledge: "knowledge/tooling/opencode/plugins/architecture.md"
  - knowledge: "knowledge/tooling/opencode/skills/changelog-manager.md"
references:
  - url: "https://semver.org/spec/v2.0.0.html"
    title: "SemVer 2.0.0"
  - url: "https://keepachangelog.com/en/2.0.0/"
    title: "Keep a Changelog 2.0.0"
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
  - url: "https://docs.github.com/en/actions/publishing-packages/publishing-nodejs-packages"
    title: "GitHub Actions — Publish Node.js packages"
last_audit_date: 2026-06-09
---

# RuneSmith Distribution Questions — Resolved

## Relationship to Prior Work

This document resolves the five open questions identified in
[distribution-comparison.md](distribution-comparison.md). That document compared four
distribution approaches for the `@runicengines/opencode-runesmith` plugin and recommended
**Approach A (npm via GitHub Packages)** but left five specific design decisions unresolved.
Each question is analysed below with a recommendation, rationale, and implementation guidance.

---

## Question 1: Version Numbering Scheme — semver vs date-based?

**Recommendation: SemVer 2.0.0 with plugin-specific bump definitions.**

### Rationale

The existing [versioning.md](/knowledge/tooling/opencode/plugins/versioning.md) knowledge note
already prescribes SemVer for OpenCode plugins. Adhering to that convention avoids introducing a
second versioning scheme that developers must learn and tools must support.

Date-based schemes (e.g., `2026.06.07`) are human-readable for calendar reasoning but lack
semantic meaning about change impact. A developer looking at `2026.06.07` vs. `2026.09.01` cannot
tell whether the update contains a breaking change, a new feature, or a bug fix. With SemVer, the
distinction is immediate from the version string itself.

### What Constitutes Major, Minor, and Patch for an Agent Plugin

The general SemVer rules from versioning.md translate to the RuneSmith plugin as follows:

| Bump | What It Means for This Plugin | Examples |
|---|---|---|
| **Major** | Breaking changes to agent file structure, the init hook contract, or the plugin's activation API. Dropping support for a model that existing agents depend on. | Renaming or removing an agent `.md` file that projects reference. Changing the init hook's version-stamp file format. Removing a skill that agents depend on. Dropping model provider support required by existing agents. Modifying the `.runesmith/` scratchpad directory layout in a way that breaks consuming scripts. |
| **Minor** | New agents, new skills, new MCP server support, non-breaking permission additions, new optional configuration fields in `opencode.json`. | Adding an `rs-deploy` agent. Adding a new skill bundle. Adding support for a new MCP protocol. Adding an optional `runesmith.features` config key. Expanding the set of exported hooks without changing existing ones. |
| **Patch** | Bug fixes in agent prompt wording, documentation improvements, dependency bumps, internal refactoring with no functional change to agents or skills. | Fixing a typo in an agent definition. Updating `@opencode-ai/plugin` peer dependency. Improving error messages in the init hook. Refactoring internal helper functions. |

### Implementation Notes

- The plugin's `CHANGELOG.md` must prefix breaking changes with `**Breaking:**` as shown in
  versioning.md's Keep a Changelog format.
- Pre-release tags (`1.0.0-beta.1`, `2.0.0-rc.1`) are permitted for testing but the init hook's
  version-stamp reader (see [init-hook.md](init-hook.md)) treats pre-release suffixes as
  invalid, forcing a re-copy. This is acceptable — developers testing pre-releases expect cache
  invalidation.

---

## Question 2: Backward Compatibility Guarantees

**Recommendation: Define backward compatibility at the component contract level.**

### What the Plugin Owns

The plugin manages files it copies into the project's `.opencode/` directory. These are not user
files — they are cached copies of the plugin's bundled artifacts. The plugin's init hook
(designed in [init-hook.md](init-hook.md)) overwrites them on version changes.

### What IS a Breaking Change

| Component | Breaking Change | Rationale |
|---|---|---|
| **Agent `.md` files** | Renaming an agent file (e.g., `architect.md` → `system-architect.md`) removes the agent from projects that reference it by the old name. Deleting an agent file entirely. | Agents are referenced by filename in `opencode.json`'s `agent` array. A renamed or deleted file causes a silent registration failure. |
| **Skills** | Removing a skill directory that an agent calls via `skill({ name: "..." })`. Renaming a skill directory that changes its resolved name. | Skills are invoked by name. A removed skill causes runtime failures in any agent that depends on it. |
| **Init hook contract** | Changing the version-stamp file format or location such that existing `.opencode/.runesmith-version` stamps are not recognised. Changing the semantics of the `activate()` export signature (if documented as stable). | These changes would break the update detection mechanism, causing stale copies to persist after a plugin version bump. |
| **Permission profiles** | Removing or restricting a permission that existing agents depend on, without a migration path. | Agents may declare required permissions. Removing a permission breaks agent workflows. |
| **`opencode.json` config keys** | Removing or renaming the `runesmith.phase` key that the plugin's init hook reads. Changing the type or semantics of an existing key. | Configuration keys are contracts between the user and the plugin. Changing or removing them breaks user configurations silently. |
| **Scratchpad directory** | Restructuring `.runesmith/` in a way that breaks scripts or tools that read from known subpaths. | If the plugin documents that `.runesmith/sessions/` contains session logs, moving those files breaks consumers. |

### What Is NOT a Breaking Change

| Component | Not Breaking | Rationale |
|---|---|---|
| **New agents** | Adding a new `.md` file to the bundled agents directory. | Existing agents are unaffected. Users must explicitly add the new agent to their `opencode.json` to use it. |
| **New skills** | Adding a new skill directory under `.opencode/skills/` in the plugin bundle. | Existing skills remain available under their existing names. New skills do not affect running agents unless an agent is updated to call them. |
| **New optional config fields** | Adding a new key to `opencode.json` under `runesmith.*` that is entirely optional and has a documented default. | No existing configuration breaks because the key is absent — the plugin falls back to the default. |
| **New init hook hooks** | Extending the `activate()` return object with new optional event hook registrations. | Existing consumers that do not use the new hooks are unaffected. |
| **Bug fixes and prompt tweaks** | Updating agent prompt text, fixing typos in skill documentation, improving error messages. | These changes refine behaviour without altering contracts. |
| **Dependency bumps** | Updating `@opencode-ai/plugin` or other dependencies within the same major version range. | Peer dependency changes within the same major version are backward-compatible by the SemVer contract. |

### Guarantee Policy

For any breaking change:

1. The major version is bumped (per Q1 rules).
2. The `CHANGELOG.md` entry is prefixed with `**Breaking:**`.
3. The release notes document the migration path (e.g., "Rename `architect.md` to
   `system-architect.md` in your `opencode.json` `agent` array").
4. The previous major version remains available in the GitHub Packages registry for teams that
   cannot upgrade immediately.

**Note on `runesmith.phase` config key**: The `runesmith.phase` config key contract depends on
init-hook behaviour (phase-aware selective agent copying) flagged as a required follow-up in
../operations/rollout-strategy.md. This config key definition assumes that work is completed.

**Note on `opencode.json` unknown-key handling**: This config key contract assumes OpenCode
ignores unknown top-level keys in `opencode.json` (an assumption flagged in ../operations/rollout-strategy.md
as requiring verification during implementation).

---

## Question 3: Release Workflow — manual vs GitHub Actions?

**Recommendation: GitHub Actions automation for consistency, with manual trigger as backup.**

### Rationale

The [publishing-workflow.md](/knowledge/tooling/opencode/plugins/publishing-workflow.md) knowledge
note provides both manual and automated workflows. For the RuneSmith plugin, automation wins on
three grounds:

| Factor | Manual | Automated (GitHub Actions) |
|---|---|---|
| **Consistency** | Depends on maintainer remembering to build, version, publish, tag, and create a release — each step is a failure point. | Single action: push a tag. The workflow handles every step identically every time. |
| **Audit trail** | Limited to git log and npm history. No link between the CI run, the publish event, and the release notes. | The workflow creates a GitHub Release with auto-generated notes from merged PRs. Everything links back to a single CI run. |
| **Token management** | Maintainer must have a PAT with `write:packages` scope. Token expiry or rotation is a manual tracking burden. | `GITHUB_TOKEN` is automatically provided by GitHub Actions, scoped to the workflow run, and requires no management. |
| **Setup effort** | None (already have npm and git installed). | One-time: commit a `.github/workflows/publish.yml` file. |

The token management argument is decisive for a small team — removing the need to issue, rotate,
and track personal access tokens for package publishing reduces operational overhead to zero.

### Workflow Design

The recommended workflow triggers on tag push matching `v*`:

```yaml
# .github/workflows/publish.yml
name: Publish RuneSmith Plugin

on:
  push:
    tags:
      - "v*"

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      packages: write

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          registry-url: https://npm.pkg.github.com
          scope: "@runicengines"

      - run: npm ci

      - run: npm run build

      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Create GitHub Release
        run: |
          gh release create ${{ github.ref_name }} \
            --repo ${{ github.repository }} \
            --title "Release ${{ github.ref_name }}" \
            --generate-notes
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Security Considerations

| Concern | Mitigation |
|---|---|
| **`GITHUB_TOKEN` scope** | The `packages: write` permission is required for `npm publish`. This is granted via the `permissions` block in the workflow — no manual token configuration needed. The `contents: write` permission is required for creating the GitHub Release. |
| **Unauthorised tag pushes** | The default branch should be protected. Only maintainers with push access can create tags matching `v*`. Use branch protection rules with "Restrict who can push to matching branches" if tighter control is needed. |
| **Supply chain** | `npm ci` installs from `package-lock.json`, which pins transitive dependencies. Use Dependabot or Renovate to keep lockfile dependencies updated. |
| **Manual trigger backup** | If CI is unavailable, a maintainer can publish manually via `npm publish` from their local machine, provided they have a PAT with `write:packages` scope. Document this as a disaster recovery path in `CONTRIBUTING.md`. |

### Release Cadence

No fixed schedule is recommended. The plugin is released when changes accumulate that warrant a
version bump (per Q1 rules). A rough guideline:

- **Patch releases**: As needed for bug fixes. May be batched if multiple fixes land in quick
  succession.
- **Minor releases**: When a new agent, skill, or feature is ready. No calendar commitment.
- **Major releases**: When a breaking change is unavoidable. Accompany with a migration guide.

### CHANGELOG Curation vs Auto-Generated Release Notes

The release workflow above uses `--generate-notes` (line 195) to auto-generate release notes from
merged PR titles. However, Question 2 requires manually curated CHANGELOG entries with a
`**Breaking:**` prefix. These two approaches can drift or conflict over time.

The team should choose one of the following approaches:

(a) **Reconcile approach**: Use `--generate-notes` for the GitHub Release, then during the release
PR review, reconcile the auto-generated notes with the manually curated CHANGELOG. The release
notes serve as the "public" summary while the CHANGELOG remains the authoritative record.

(b) **CHANGELOG-first approach**: Skip `--generate-notes` and write release notes directly from
the CHANGELOG content. This avoids drift entirely but requires manual release note authoring.

Document the chosen approach in `CONTRIBUTING.md` alongside the release workflow.

---

## Question 4: Multi-Version Coexistence

**Recommendation: One version per machine via the global npm cache. Breaking changes are
published as new major versions; all projects standardise on the same major version track.**

### The Coexistence Problem

OpenCode caches npm plugins in `~/.cache/opencode/node_modules/` at the package level (see
[npm-packaging.md](/knowledge/tooling/opencode/plugins/npm-packaging.md)). The cache stores one
version per package name. If project A requires `@runicengines/opencode-runesmith@1.2.0` and
project B requires `@runicengines/opencode-runesmith@2.0.0`, the second project's startup will
overwrite the cached version, breaking the first project until the cache is cleared and the first
project is restarted.

This is a fundamental constraint of the auto-install mechanism. The `plugin` array in
`opencode.json` does not support version specifiers — it accepts plain package names only, and
resolution follows whatever version is currently in the Bun cache.

### Resolution Strategy

Four strategies, in order of preference:

#### Strategy 1: Organisational Standardisation (Recommended)

All RunicEngines projects use the same **major version** of the plugin. Breaking changes are
published as new major versions (e.g., `2.0.0`), and the organisation coordinates an upgrade
window. During the upgrade window:

1. The new major version is published. Old projects continue working with the cached major
   version until they clear the cache and restart.
2. The migration guide is communicated via the GitHub Release notes.
3. All projects upgrade within a defined timeline (e.g., one sprint).
4. After the timeline, the previous major version is deprecated but remains available in the
   registry for emergency rollback.

This works because the RunicEngines co-op is small (fewer than 20 developers) and projects are
managed internally. Organisational coordination is feasible.

#### Remediation for Missed Upgrades

Developers returning from extended leave (PTO, sabbatical, etc.) may run a stale cached version
after the coordinated upgrade window closes. To remediate:

```bash
bun cache rm @runicengines/opencode-runesmith && bun install
```

This forces a fresh install of the current major version. Include this command in the
maintenance-governance documentation as a troubleshooting step for developers who missed the
upgrade window.

#### Strategy 2: Per-Project Worktrees with Separate Caches

For the rare case where two projects genuinely need different incompatible versions
simultaneously (e.g., during a long migration), use separate git worktrees with independent
OpenCode caches:

```bash
# Create a worktree for the project that needs the older version
git worktree add ../project-v1-legacy legacy-branch

# In that worktree, configure a custom cache path via environment variable
# (if OpenCode supports OPENCODE_CACHE_DIR or similar) or use a symlink
# workaround to point ~/.cache/opencode/node_modules at a project-specific cache.
```

However, OpenCode does not currently expose a cache directory configuration point. This strategy
is listed for completeness but is **not practically available** without upstream changes.

#### Strategy 3: Local Plugin Fork for Legacy Projects

If a project is permanently stuck on an older major version, convert it to use a **local plugin**
instead of the npm auto-install mechanism. The architecture.md knowledge note confirms that local
plugins work identically to npm-installed plugins. The workflow:

1. Clone the plugin repository at the required version tag.
2. Place a thin local plugin in `.opencode/plugins/runesmith-local.ts` that imports from the
   cloned path.
3. Remove `@runicengines/opencode-runesmith` from the `plugin` array in `opencode.json`.

This bypasses the npm cache entirely. The project is now pinned to a specific version, isolated
from any other project's cache operations. The trade-off is manual setup and no auto-updates.

#### Strategy 4: Two Packages under Different Scopes

Publish breaking versions as separate packages (e.g., `@runicengines/opencode-runesmith-v1` and
`@runicengines/opencode-runesmith-v2`). Because they are different packages, the Bun cache can
hold both simultaneously. This is a valid but communication-heavy approach — developers must know
which package name to use for which project.

### Recommendation

| Scenario | Approach |
|---|---|
| Normal operation | Strategy 1 — one major version, coordinated upgrades |
| Active migration between majors | Transition period where some projects use old major and some use new; cache flip is a one-time event per developer |
| Permanent legacy project that cannot upgrade | Strategy 3 — convert to local plugin, pinned to the old version |
| Rare: two active incompatible versions needed simultaneously | Strategy 4 — scope-based split, but strongly discouraged |

**Decision**: Default to Strategy 1. Implement Strategy 3 as a documented escape hatch in the
plugin's README and `CONTRIBUTING.md`.

### Version-Stamping Interaction

The init hook's version-stamping (designed in [init-hook.md](init-hook.md)) is compatible with
all four strategies:

- **Strategy 1**: All projects on the same major version produce the same stamp. No conflict.
- **Strategy 3**: The local plugin has its own `package.json` at the cloned path. The init hook
  reads its version from there and stamps `.opencode/.runesmith-version` accordingly.
- **Strategy 4**: Different package names write stamps independently because they are different
  packages with different `package.json` files and different installation paths.

---

## Question 5: Offline Development Workflow

**Recommendation: Document the local plugin workflow as the primary offline path, with a
pre-caching script as a secondary option.**

### The Offline Problem

The auto-install mechanism requires network access to the GitHub npm registry on first startup
(after a cache clear). Developers working offline — on a plane, in a remote location, or in an
air-gapped environment — cannot download the plugin.

The [architecture.md](/knowledge/tooling/opencode/plugins/architecture.md) knowledge note states:
> "Local plugins are not installed or cached. They are loaded directly from their plugin
> directory on each startup. No package manager step applies."

This is the escape hatch.

### Option A: Local Plugin Workflow (Recommended)

The plugin repository can be cloned once (when online) and used as a local plugin indefinitely,
even when offline. The workflow:

```bash
# 1. Clone the plugin repository (requires network)
git clone git@github.com:RunicEngines/opencode-runesmith.git ~/src/opencode-runesmith

# 2. Create a local plugin wrapper in .opencode/plugins/runesmith-local.ts
cat > .opencode/plugins/runesmith-local.ts << 'EOF'
import { type Plugin } from "@opencode-ai/plugin";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const pluginPath = join(__dirname, "..", "..", "..", "..", "src", "opencode-runesmith");

// Re-export the plugin from the cloned repository
export { default } from pluginPath;
EOF

# 3. Remove the npm plugin entry from opencode.json
#    (or leave it — OpenCode will try to install it but fail silently offline,
#    while the local plugin handles the actual registration)
```

In practice, the simpler approach is:

```bash
# After cloning the repo, use npm link to make it available locally
cd ~/src/opencode-runesmith
npm link

# In the consuming project, reference the linked package
# This requires configuring Bun/npm to resolve the link
```

**Simplest offline approach**: Remove the plugin from `opencode.json`'s `plugin` array and
instead place the bundled agent/skill files directly in `.opencode/agents/` and
`.opencode/skills/` from the cloned repository. This adapts the local plugin workflow pattern
(similar to the per-project copy approach discussed in distribution-comparison.md's Approach C,
but using plugin directory placement instead of a setup script) — it trades auto-install for
guaranteed offline operation.

### Option B: Pre-Caching Script (Secondary)

For developers who want to keep the auto-install workflow but work offline occasionally, a
pre-caching script can be provided:

```bash
#!/usr/bin/env bash
# scripts/cache-plugin.sh
# Pre-download the RuneSmith plugin and its dependencies into the OpenCode cache.

set -euo pipefail

PLUGIN_NAME="@runicengines/opencode-runesmith"
CACHE_DIR="${HOME}/.cache/opencode/node_modules"
REGISTRY="https://npm.pkg.github.com"

echo "Pre-caching ${PLUGIN_NAME} into ${CACHE_DIR}..."

# Ensure .npmrc is configured
if ! grep -q "@runicengines:registry" ~/.npmrc 2>/dev/null; then
  echo "Error: @runicengines scope not configured in ~/.npmrc"
  echo "Add the following lines:"
  echo "  @runicengines:registry=https://npm.pkg.github.com/"
  echo "  //npm.pkg.github.com/:_authToken=\${GITHUB_TOKEN}"
  exit 1
fi

# Create cache directory if it does not exist
mkdir -p "${CACHE_DIR}"

# Download the plugin and its dependencies using Bun
# This populates the cache without requiring an OpenCode restart
cd "${CACHE_DIR}"
bun add "${PLUGIN_NAME}" --registry "${REGISTRY}"

echo "Done. ${PLUGIN_NAME} is now cached for offline use."
```

The developer runs this script while online. The plugin is cached in
`~/.cache/opencode/node_modules/` and is available offline until the cache is cleared.

### Option C: Git-Based Distribution as Fallback (Emergency)

If the GitHub npm registry is unreachable (e.g., GitHub outage) and the cache is empty, the
plugin can be distributed via git as a one-time bootstrap:

```bash
# Clone directly into the project's local plugin directory
git clone --depth 1 \
  git@github.com:RunicEngines/opencode-runesmith.git \
  .opencode/plugins/opencode-runesmith
```

Then reference it as a local plugin. This is equivalent to Option A but is presented as a
disaster-recovery path rather than the primary workflow.

### Recommendation

| Developer Type | Recommended Approach |
|---|---|
| **Occasionally offline** (plane, commute) | Option B: Run the pre-caching script before going offline. Keep the npm plugin entry in `opencode.json`. |
| **Permanently air-gapped** | Option A: Local plugin workflow. Clone once on a connected machine, transfer via USB, use as local plugin. |
| **Emergency bootstrap** (registry down) | Option C: Git clone into `.opencode/plugins/`. |

For documentation purposes, the plugin's README should include an "Offline Development" section
covering Option A (local clone) and Option B (pre-caching script). The air-gapped scenario is
documented in `CONTRIBUTING.md` as a special case.

---

## 6. Summary Table

| Question | Recommendation | Key Rationale |
|---|---|---|
| **1. Version numbering** | SemVer 2.0.0 with plugin-specific bump definitions (Major: agent file renames, init hook contract changes; Minor: new agents/skills/config; Patch: bug fixes, docs) | Existing versioning.md prescribes SemVer. Date-based versions lack semantic meaning about change impact. |
| **2. Backward compatibility** | Breaking = renamed/deleted agents, removed skills, changed init hook contract, removed config keys. Not breaking = new agents, new skills, new optional config, dependency bumps. | Clear contract boundaries let developers reason about upgrade risk without reading the full changelog. |
| **3. Release workflow** | GitHub Actions automated pipeline on tag push — builds, publishes, creates GitHub Release. Manual `npm publish` as disaster recovery backup. | `GITHUB_TOKEN` is zero-management. Automation eliminates step-skipping errors. Audit trail links CI run, publish event, and release notes. |
| **4. Multi-version coexistence** | One major version per machine via standardisation. Local plugin pinned to old version for permanent legacy projects. Scope-based split only as last resort. | The Bun cache stores one version per package name. For a small co-op, organisational coordination is feasible and simple. |
| **5. Offline development** | Primary: local plugin workflow (clone → use as local plugin). Secondary: pre-caching script (`bun add` into cache). Emergency: git clone into `.opencode/plugins/`. | Local plugins work identically to npm plugins (architecture.md). The pre-caching script preserves the auto-install workflow for occasional offline use. |

---

## Next Steps

1. **Implement the release workflow**: Commit `.github/workflows/publish.yml` to the plugin
   repository.
2. **Add offline documentation**: Include an "Offline Development" section in the plugin README.
3. **Write the pre-caching script**: Add `scripts/cache-plugin.sh` to the plugin repository.
4. **Update the CHANGELOG policy**: Document the breaking-change prefix convention in
   `CONTRIBUTING.md`.
5. **Decision lock**: Update [distribution-comparison.md](distribution-comparison.md) to link
   here as "Questions resolved in" once this document is accepted.

---
title: "Changelog Manager Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - skills
  - changelog
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
  - knowledge: "knowledge/tooling/opencode/skills/concepts.md"
references:
  - url: "https://keepachangelog.com/en/2.0.0/"
    title: "Keep a Changelog 2.0.0"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
  - url: "https://www.conventionalcommits.org/en/v1.0.0/"
    title: "Conventional Commits 1.0.0"
last_audit_date: 2026-06-07
---

# Changelog Manager Skill Design

## Context

The `@runicengines/opencode-runesmith` plugin provides OpenCode agents with RunicEngines-specific skill workflows. The `rs-changelog-manager` skill is a workflow skill that generates and maintains `CHANGELOG.md` files following the [Keep a Changelog v2.0.0](https://keepachangelog.com/en/2.0.0/) specification exactly.

This file is a research analysis: it documents the skill's design requirements, its recommended instruction body, and maps how it differs from the Knowledge Base's existing `changelog-manager` skill at `knowledge/tooling/opencode/skills/changelog-manager.md`.

### Why a New Skill?

The existing `changelog-manager` skill in the KB maintains the idea section's `changelog.md` files — structured per-idea change logs that track how an idea evolved from draft to completion. It is a **content evolution** changelog. The `rs-changelog-manager` skill is built for **project `CHANGELOG.md` files** — user-facing release notes following Keep a Changelog 2.0.0, where entries are grouped by release version and change type. These serve fundamentally different audiences: the KB changelog is for internal contributors tracking idea history; the project changelog is for consumers and stakeholders reading "what changed in this release."

### Skill Identity

| Property | Value |
|---|---|
| Plugin | `@runicengines/opencode-runesmith` |
| Skill name | `rs-changelog-manager` |
| Skill prefix | `rs-` |
| Loading model | On-demand (via `skill({ name: "rs-changelog-manager" })`) |
| Primary user | Tech-writer agent |
| Secondary user | DevOps agent (for release cuts) |
| Trigger | Pre-release, or when updating unreleased changes |

---

## Keep a Changelog 2.0.0 Compliance

The skill MUST enforce every requirement of the Keep a Changelog 2.0.0 specification. The following checklist maps each requirement to its enforcement point in the skill.

### Required Elements

| # | Requirement | Skill Enforcement |
|---|---|---|
| 1 | `## [Unreleased]` section at the top | Step 4 — always present as the first heading after the intro |
| 2 | Change type labels: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security` | Step 3 — categorisation maps Commits to these exact labels |
| 3 | Date format: ISO 8601 (`YYYY-MM-DD`) | Step 5 — release date is formatted via `date +%Y-%m-%d` or Python `datetime` |
| 4 | Version linking: each version heading links to a compare URL | Step 5 — generates `[1.0.0]: https://github.com/.../compare/v0.9.0...v1.0.0` |
| 5 | `[YANKED]` tag on yanked releases: `## [0.0.5] - 2014-12-13 [YANKED]` | Step 6 — explicit yank sub-workflow |
| 6 | Reverse chronological order: newest version first | Step 5 — inserts new version above `[Unreleased]` (well, `[Unreleased]` stays top, new version goes below it) |
| 7 | Each version section groups changes by type | Step 3 — categorised entries are written under their respective type heading |
| 8 | Link reference section at the bottom for version compare URLs | Step 5 — appends link definitions after all version sections |

### Guiding Principles Enforced

| Principle | How the Skill Adheres |
|---|---|
| **For humans, not machines** | Entries are written as plain-language descriptions, not raw commit subject lines. The skill deduplicates and rephrases technical git messages into human-readable prose. |
| **Same types should be grouped** | Categorisation by type label (`Added`, `Fixed`, etc.) — never interleaved. |
| **Versions should be linkable** | Every version heading gets a corresponding `[X.Y.Z]: ` link definition. |
| **Latest version first** | Reverse chronological ordering is enforced on every write. |
| **Display release date** | Every version heading includes `YYYY-MM-DD`. |
| **Mention if project follows SemVer** | A note is added to the changelog header: "This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)." |

### Bad Practices Avoided

| Bad Practice | How the Skill Avoids It |
|---|---|
| Commit log diffs | Entries are categorised and rephrased — not raw `git log` output. |
| Ignoring deprecations | `Deprecated` changes are surfaced explicitly from `deprecate` commits. |
| Confusing date formats | Only `YYYY-MM-DD` is used. |
| Inconsistent change types | The six canonical labels are the only recognised types. Non-matching changes are flagged to the user. |

---

## Recommended SKILL.md Instructions

The following block is the recommended instruction body for the skill's `SKILL.md` file. It follows the workflow skill conventions documented in `knowledge/tooling/opencode/skills/workflow-patterns.md`.

```markdown
---
name: rs-changelog-manager
description: >
  Generate and maintain CHANGELOG.md following Keep a Changelog 2.0.0
  format. Parses Conventional Commits into categorised change entries,
  manages the Unreleased section, and produces release-ready changelogs
  with version linking and ISO dates.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: release
  audience: tech-writer, devops
  trigger: manual
---

# rs-changelog-manager

## Purpose

Reads git commits (or a manual change list) and produces or updates a
`CHANGELOG.md` file that strictly follows Keep a Changelog 2.0.0. The skill
manages the `[Unreleased]` section during development and promotes it to a
versioned release section on release cuts.

## When to Invoke

- The user says "update the changelog", "add unreleased changes", or
  "update CHANGELOG.md".
- Before cutting a release — the skill moves `[Unreleased]` to a versioned
  section and creates a fresh `[Unreleased]` heading for the next cycle.
- After merging a PR with notable changes — to keep `[Unreleased]` current
  during active development.

## Trigger

| Condition | Type |
|---|---|
| User asks to update changelog or add unreleased changes | Manual |
| User says "cut release X.Y.Z" or "prepare release" | Manual (auto-suggest) |
| Pre-release workflow hook (if integrated with CI) | Automated |

## Required Permissions

| Permission | Purpose |
|---|---|
| `bash: { "git *": "allow" }` | Run `git log`, `git tag --list` for version detection |
| `read` | Read existing `CHANGELOG.md`, `package.json` (for version) |
| `edit` / `write` | Write updated `CHANGELOG.md` |
| `grep` | Find version tags, parse existing changelog sections |
| `glob` | Find `CHANGELOG.md` at repo root or docs/ directory |

## Input

The skill accepts one of:

1. **Nothing (auto-detect)** — reads the existing `CHANGELOG.md`, parses
   recent git commits from the last tag to HEAD, and updates `[Unreleased]`.
2. **Commit range** — e.g. `v1.0.0..HEAD` or `abc123..def456`. Useful for
   partial updates or hotfix branches.
3. **Manual change list** — a YAML or plain-text list of entries. Useful
   when commits are not available or when the changelog needs editorial
   overrides.

## Workflow Steps

### Step 1: Locate and validate existing CHANGELOG.md

1. Search for `CHANGELOG.md` (or `changelog.md`, case-insensitive) in the
   repo root first, then `docs/` directory, then project root.
2. If found, parse the existing structure:
   - Confirm it follows Keep a Changelog 2.0.0 layout.
   - Extract the `[Unreleased]` section content (if any).
   - Collect existing version headings and link definitions.
3. If not found, initialise a new `CHANGELOG.md` with the standard header:
   ```markdown
   # Changelog

   All notable changes to this project will be documented in this file.

   The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
   and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

   ## [Unreleased]
   ```

### Step 2: Detect version and commit range

1. Determine the current version:
   - Read `package.json` → `version` field (Node.js projects).
   - Fall back to latest git tag matching `v*` or `\d+.\d+.\d+` via
     `git tag --list --sort=-version:refname`.
   - If no version source is found, ask the user for the next version.
2. Determine the commit range:
   - If the user provided a range, use it.
   - Otherwise, find the last release tag and compute
     `git log <last-tag>..HEAD --oneline --no-merges`.
   - If no tags exist, use all commits from `HEAD`.

### Step 3: Categorise changes by type

Parse each commit message against the Conventional Commits format and map
to Keep a Changelog types:

| Conventional Commits | Changelog Type | Notes |
|---|---|---|
| `feat` | `Added` | New features |
| `fix` | `Fixed` | Bug fixes |
| `BREAKING CHANGE` (footer or `!`) | `Changed` | Breaking changes are flagged with `**BREAKING:**` prefix |
| `refactor` with breaking change | `Changed` | Only if breaking; otherwise use `Changed` sparingly |
| `refactor` (non-breaking) | `Changed` | Behaviour-preserving restructuring |
| `perf` | `Changed` | Performance improvements change existing behaviour |
| `deprecate` | `Deprecated` | Deprecation warnings, sunset notices |
| `remove` | `Removed` | Feature removal |
| `revert` | `Removed` | Reverting a feature removes it |
| `security` | `Security` | Vulnerability fixes, security hardening |
| `docs` | *(skip unless notable)* | Documentation-only changes are omitted unless user explicitly includes them |
| `chore` | *(skip)* | Maintenance, tooling, CI — omitted by default |
| `test` | *(skip)* | Test-only changes — omitted by default |
| `style` | *(skip)* | Formatting, whitespace — omitted by default |
| `build` | *(skip)* | Build system — omitted by default |
| `ci` | *(skip)* | CI configuration — omitted by default |

**Deduplication and rephrasing rules:**

- Never copy commit subjects verbatim. Rewrite in imperative mood, present
  tense, human-readable form.
- Merge duplicate or near-duplicate entries under the same type.
- If a commit body contains a `Closes #N` or `Fixes #N` footer, append the
  issue reference to the changelog entry: `("Add user auth endpoint (#42)")`.
- Breaking changes MUST be highlighted with a `**BREAKING:**` prefix in the
  `Changed` section.

### Step 4: Update the [Unreleased] section

1. If new entries exist from Step 3, insert them into `[Unreleased]` under
   their respective type headings.
2. Preserve any existing unreleased entries that were already in the file.
3. Type headings are ordered as: `Added`, `Changed`, `Deprecated`,
   `Removed`, `Fixed`, `Security`. If a section is empty, it is omitted.
4. Each entry is a single bullet point (`- `).
5. If a type section does not exist yet in `[Unreleased]`, create it as an
   `### {Type}` heading in the canonical order.

### Step 5: On release cut — promote Unreleased to a version

When the user says "cut release X.Y.Z":

1. Replace `## [Unreleased]` with `## [{version}] - {date}` using
   `date +%Y-%m-%d` for the date.
2. Create a new empty `## [Unreleased]` heading above the just-promoted
   section (so `[Unreleased]` is always the first non-header element).
3. Add or update the version compare link in the link reference section at
   the bottom of the file:
   ```
   [Unreleased]: https://github.com/owner/repo/compare/v{version}...HEAD
   [{version}]: https://github.com/owner/repo/compare/v{previous-version}...v{version}
   ```
4. If this is the first release, the unreleased link points to `HEAD`:
   ```
   [Unreleased]: https://github.com/owner/repo/compare/v0.1.0...HEAD
   [0.1.0]: https://github.com/owner/repo/releases/tag/v0.1.0
   ```

### Step 6: Yank a release (if needed)

When the user says "yank version X.Y.Z":

1. Find the version heading `## [{version}] - {date}`.
2. Append `[YANKED]` to the heading:
   `## [{version}] - {date} [YANKED]`
3. Keep the section content intact — yanked releases document what
   happened, but the `[YANKED]` tag signals readers to not use it.
4. Add a note at the top of the section explaining why it was yanked.

### Step 7: Validate and output

1. Run a compliance check against the Keep a Changelog 2.0.0 checklist.
2. Output the updated `CHANGELOG.md` content.
3. If running as a dry-run (`--dry-run`), print the diff without writing.
4. If writing, confirm with the user before overwriting.

## Output Format

The skill produces an updated `CHANGELOG.md` at the project root (or
specified path). The file follows this structure:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New feature description (#42)
- Another new feature

### Fixed

- Bug fix description

## [1.0.0] - 2026-06-01

### Added

- Initial public API

### Changed

- **BREAKING:** Renamed core module entry points

[Unreleased]: https://github.com/owner/repo/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/owner/repo/releases/tag/v1.0.0
```

## Chained Skills

| Skill | Condition | Step |
|---|---|---|
| `rs-pr-packager` | If changelog update is part of a PR workflow | After Step 7, before output |
| `rs-issue-to-plan` | If release notes need to reference issue context | Before Step 3 |

## See Also

- [Keep a Changelog 2.0.0](https://keepachangelog.com/en/2.0.0/) — The canonical changelog specification
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) — Commit message specification used for type mapping
- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) — Versioning scheme referenced by the changelog
```

---

## Compliance Checklist

The following table maps each Keep a Changelog 2.0.0 requirement to its enforcement point in the `rs-changelog-manager` skill:

| Requirement | Skill Enforcement | Step |
|---|---|---|
| Unreleased section at top | Always present as first section after header | Step 1 |
| Six change types (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`) | Type mapping enforces these exact labels | Step 3 |
| ISO 8601 date format | `date +%Y-%m-%d` on release cut | Step 5 |
| Version compare links | Generated on release cut and appended to link reference section | Step 5 |
| `[YANKED]` tag support | Sub-workflow for yanking releases | Step 6 |
| Reverse chronological order | New release inserted below `[Unreleased]` (which stays top) | Step 5 |
| Grouped by type within version | Entries sorted under canonical type headings | Step 4 |
| Link reference section at bottom | Maintained as a persistent block at EOF | Step 5 |

---

## Comparison with KB's changelog-manager

The Knowledge Base has an existing `changelog-manager` skill at `knowledge/tooling/opencode/skills/changelog-manager.md`. The two skills share a name and a high-level goal — managing changelogs — but diverge in every dimension of execution.

| Dimension | KB `changelog-manager` | RuneSmith `rs-changelog-manager` |
|---|---|---|
| **Target file** | `changelog.md` (per-idea) — tracks idea evolution | `CHANGELOG.md` (per-project) — user-facing release notes |
| **Format** | Simple list of dated entries per status transition | Keep a Changelog 2.0.0 with versioned sections, type grouping, link references |
| **Audience** | Internal KB contributors — who changed what and when | Project consumers and stakeholders — what's new in a release |
| **Trigger** | After every status change (draft → exploring → etc.) | Pre-release cuts and when unreleased changes accumulate |
| **Commit parsing** | Not required — entries are manually written | Required — maps Conventional Commits to changelog types |
| **Version management** | Not applicable — ideas don't have versions | Core feature — detects version from package.json/git tag, manages release promotion |
| **Link references** | Not used | Required — every version gets a compare link |
| **YANKED support** | Not applicable | Required per Keep a Changelog 2.0.0 |
| **Chained skills** | None declared | `rs-pr-packager`, `rs-issue-to-plan` |
| **Metadata marker** | None | `plugin: "@runicengines/opencode-runesmith"` |

The KB skill is a **content tracking skill** — it records how an idea changed over its lifecycle. The RuneSmith skill is a **release engineering skill** — it produces polished, spec-compliant release notes for external consumption. The KB changelog is written for the team; the RuneSmith changelog is written for the world.

---

## Analysis

### Design Decisions

**1. Strict specification adherence.** The skill deliberately hard-codes the Keep a Changelog 2.0.0 requirements rather than making them configurable. If a project wants a non-standard changelog format, this skill is the wrong tool. This decision follows the OpenCode skill philosophy: each skill does one thing exactly and does it well. Configuration for type mapping variants (e.g., including `docs` changes) is handled via input parameters, not by modifying the core structure.

**2. Conventional Commits as the canonical input.** The skill assumes commits follow Conventional Commits 1.0.0. This is the same assumption made by `rs-pr-packager` and ADR 0002, creating a consistent toolchain across the RuneSmith plugin. Non-Conventional Commits are flagged to the user with a suggestion to rewrite them, but the skill does not reject them — it falls back to asking the user to classify the change manually.

**3. Editorial discretion, not automation.** The skill rewrites commit subjects into human-readable entries rather than copying them verbatim. This is a deliberate choice: `git log` output is a terrible changelog. The skill provides a first-pass categorisation and phrasing, but the user is expected to review and polish. The skill's output is a draft, not a final document.

**4. `[Unreleased]` is always the top section.** Per the specification, the unreleased section must be the first version heading after the introductory text. On release cut, the skill promotes the current `[Unreleased]` entries to a versioned section and creates a fresh empty `[Unreleased]` above it. This keeps the file structure clean and avoids the common mistake of appending to the bottom.

**5. Version detection without a build system.** The skill reads `package.json` first (for Node.js projects) and falls back to git tags. This avoids requiring a specific build tool or language runtime. If neither is available, it asks the user explicitly — a transparent failure rather than a silent default to `0.0.0`.

### Differences from a Manual Changelog Workflow

In a traditional manual workflow, a maintainer reads through git log, categorises changes, and writes entries by hand. The skill automates the mechanical steps (parsing, categorisation, file formatting) while leaving the editorial judgment (what constitutes a notable change, how to phrase each entry) to the user. The skill is a **force multiplier** for the release manager, not a replacement.

The skill's type-mapping table intentionally excludes `docs`, `chore`, `test`, `style`, `build`, and `ci` from auto-inclusion. These commit types are typically invisible to end users. The user can override this via the manual change list input when a documentation change is significant enough to warrant a changelog entry.

### Risk Assessment

**False negatives in type mapping.** A `feat` commit that the author considers internal refactoring may be miscategorised as `Added` when it should be `Changed` or omitted entirely. The skill cannot distinguish between a user-facing feature and an internal API addition. Mitigation: the skill always produces a draft for review, and the user can override categorisations via the manual change list input before writing.

**Rebased/rewritten commit history.** If commits are squashed or rebased before the changelog is generated, the commit messages may not reflect the original intent. The skill reads the current commit history, which after a squash will show only the squashed message. Mitigation: run the skill before squashing, or use a dedicated "changelog" commit that captures all changes in a structured format.

**Monorepo ambiguity.** In a monorepo with multiple packages, a single `CHANGELOG.md` at the root may not capture per-package changes. The current design assumes a single-project repository. For monorepo support, a future iteration could accept a `--package` parameter that scopes the commit range to a subdirectory.

### Open Questions

**1. Should the skill support `--amend` for editing existing releases?**

A release manager may need to add a missed entry to an already-released version. Current design only supports updating `[Unreleased]`. Supporting `--amend` with a version target would allow surgically editing past releases, but risks breaking the compare links (because the git tag doesn't change). If the team frequently misses entries before release, this is worth adding.

**2. Should the skill auto-commit the changelog update?**

The current design leaves the agent to decide. Auto-committing with a message like `docs: update changelog for vX.Y.Z (#42)` would reduce friction, but the user may want to review the changelog before committing. A `--commit` flag could control this behaviour.

**3. Should the skill generate a GitHub Release from the changelog entry?**

After promoting `[Unreleased]` to a versioned section, the skill could optionally create a GitHub Release using `gh release create`. This would chain `rs-changelog-manager` → `gh` skill. The current design is agnostic to release publishing — the skill only maintains the file. A follow-up `rs-release-cutter` skill could orchestrate changelog + tag + release.

### Recommendations

1. **Implement `rs-changelog-manager` alongside `rs-pr-packager`** — the two skills share the Conventional Commits type mapping and can reuse a common type-mapping module. They also chain into each other: the PR packager suggests updating the changelog, and the changelog manager may need to reference PR context for entry descriptions.

2. **Always write to `CHANGELOG.md` (capitalised, at repo root)** — this is the conventional path recognised by GitHub's release-drafter, changie, and standard tooling. Writing to a non-standard path would require additional configuration and confuse users who expect the canonical location.

3. **Include a `--dry-run` flag** for reviewing the updated changelog before writing. This is especially important for release cuts, where mistakes in the changelog are visible to consumers.

4. **Document the editorial override path clearly** in the skill body. Users should know they can provide a manual change list when the automated parsing produces imperfect results. The skill should never be a single point of failure for release notes.

5. **Do not auto-create git tags.** The changelog manager's job stops at the file. Tagging is a separate concern handled by the release workflow. Mixing them conflates responsibilities and makes it harder to test the changelog output before finalising the release.

---

## See Also

- [ADR 0002 — GitHub Etiquettes](/adr/0002-github-etiquettes/) — The conventions referenced by this skill's Conventional Commits mapping
- [Knowledge: OpenCode Skills Overview](/knowledge/tooling/opencode/skills/overview/) — OpenCode skill system reference
- [Knowledge: KB changelog-manager](/knowledge/tooling/opencode/skills/changelog-manager/) — The existing KB-focused changelog-manager skill (content-tracking variant)
- [PR Packager Skill Design](/research/opencode-runesmith/skills/workflows/pr-packager/) — The companion skill for PR generation; shares the Conventional Commits parsing pipeline
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills) — OpenCode's official docs
- [Keep a Changelog 2.0.0](https://keepachangelog.com/en/2.0.0/) — The changelog specification this skill enforces
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) — The commit specification used for type mapping

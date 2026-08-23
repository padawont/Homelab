---
name: rs-changelog-manager
description: >
  Generate and maintain CHANGELOG.md following Keep a Changelog 2.0.0 format.
  Parses Conventional Commits into categorised change entries, manages the
  Unreleased section, and produces release-ready changelogs with version
  linking and ISO dates.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: release
  audience: tech-writer, devops
  trigger: manual
---

## Purpose

Reads git commits (or a manual change list) and produces or updates `CHANGELOG.md` following the Keep a Changelog 2.0.0 specification. Parses conventional commit messages, categorises changes into the correct Keep a Changelog sections (Added, Changed, Deprecated, Removed, Fixed, Security), manages the `[Unreleased]` section, and produces release-ready changelogs with version anchors, ISO dates, and inter-version links.

## When to Invoke

- User says "update the changelog", "generate changelog", "prepare release notes", or similar
- Before cutting a release — ensures the `[Unreleased]` section is promoted to a versioned section
- After a notable PR merge — adds new entries to `[Unreleased]`
- On manual request to yank a release (append `[YANKED]` tag)

## Trigger

- **Manual** — user explicitly requests changelog operations via conversation
- **Automated** — a pre-release workflow or CI pipeline invokes the skill for release preparation

## Required Permissions

The calling agent must have these tools available:

| Tool  | Required | Scope                      | Purpose                                   |
| ----- | -------- | -------------------------- | ----------------------------------------- |
| bash  | Yes      | git * (log, tag, describe) | Run `git log`, `git tag`, `git describe`  |
| read  | Yes      | CHANGELOG.md, package.json | Read existing changelog and version files |
| edit  | Yes      | CHANGELOG.md               | Update changelog sections                 |
| write | Yes      | CHANGELOG.md               | Create or overwrite changelog             |
| grep  | Yes      | Commit messages, changelog | Search for version sections and patterns  |
| glob  | Yes      | Find CHANGELOG.md          | Locate changelog and package files        |

This skill does not delegate tasks to external agents via the task() tool; all work is performed by the calling agent.

## Input

| Input Form            | Description                                                                                                         |
| --------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Nothing (auto-detect) | Scans `git log`, reads existing `CHANGELOG.md`, and detects the next version automatically                          |
| Commit range          | A specific `git log` range (e.g., `v1.0.0..HEAD`, `abc123..def456`) — use when only a subset of commits is relevant |
| Manual change list    | A YAML list of change entries — use when commits are not available or need curation                                 |

**Manual change list format:**

```yaml
changes:
  - type: feat
    description: Add user authentication via OAuth2
    scope: auth
    breaking: false
  - type: fix
    description: Resolve null pointer in session handler
    scope: session
    breaking: false
  - type: deprecate
    description: Mark v1 login endpoint as deprecated
    scope: api
    breaking: false
```

**Dry-run mode:**

Pass `--dry-run` to print the proposed diff to stdout without modifying the file. The output shows what would change in each section. This is safe to use in CI for review before committing.

## Workflow Steps

### Step 1: Locate and validate existing CHANGELOG.md

1. Search for `CHANGELOG.md` in the repository root using `glob`.
2. If found, read the file and parse its structure (version sections, `[Unreleased]` header, compare links).
3. Validate the file conforms to Keep a Changelog 2.0.0:
   - Contains a `# Changelog` top-level heading
   - Has an `[Unreleased]` section or a note that none exists
   - Version sections follow `## [{version}] - {YYYY-MM-DD}` format
   - Each section has subheadings from the allowed set (Added, Changed, Deprecated, Removed, Fixed, Security)
   - Compare links exist at the bottom: `[{version}]: https://...`
4. If no `CHANGELOG.md` exists, create one from the template (see Output Format).

### Step 2: Detect version and commit range

Determine the next version and which commits to process using the following fallback chain:

1. **`package.json`** — read the `version` field; use `semver` (or manual semver parsing) to bump the appropriate segment (major for BREAKING, minor for feat, patch for fix and everything else).
2. **Git tag** — run `git describe --tags --abbrev=0` to find the latest version tag. If none exists, start from the first commit.
3. **Ask the user** — if neither is available, prompt the user for the version string and commit range.

Derive the commit range:

- If an existing `CHANGELOG.md` has the current version, the range is `v{current}..HEAD`.
- If this is a first-time run, the range is `HEAD` (all commits).
- If the user supplies a range explicitly, use that.

### Step 3: Categorise changes by type

Run `git log --format="%s%n%b---" {range}` to retrieve commit subjects and bodies. Parse each commit for its Conventional Commit prefix.

Map Conventional Commit types to Keep a Changelog sections:

| Conventional Commit Type   | Keep a Changelog Section | Condition                                                        |
| -------------------------- | ------------------------ | ---------------------------------------------------------------- |
| `feat`                     | Added                    | All features                                                     |
| `fix`                      | Fixed                    | All bug fixes                                                    |
| `BREAKING CHANGE` (footer) | Changed                  | Any commit with `BREAKING CHANGE:` in body or `!` after the type |
| `feat!`                    | Changed                  | Breaking feature                                                 |
| `fix!`                     | Changed                  | Breaking fix                                                     |
| `refactor`                 | Changed                  | Non-breaking restructure                                         |
| `perf`                     | Changed                  | Performance improvement                                          |
| `deprecate`                | Deprecated               | Marking feature as deprecated                                    |
| `remove`                   | Removed                  | Removing a feature                                               |
| `revert`                   | Removed                  | Reverting a previous change                                      |
| `security`                 | Security                 | Security-related fix                                             |
| `docs`                     | _Skip_                   | Skip unless notable (see rules below)                            |
| `chore`                    | _Skip_                   | Skip unless notable                                              |
| `test`                     | _Skip_                   | Skip unless notable                                              |
| `style`                    | _Skip_                   | Skip unless notable                                              |
| `build`                    | _Skip_                   | Skip unless notable                                              |
| `ci`                       | _Skip_                   | Skip unless notable                                              |

**15 total mappings:** `feat`, `fix`, `BREAKING CHANGE` (footer), `feat!`, `fix!`, `refactor`, `perf`, `deprecate`, `remove`, `revert`, `security`, plus the five skip-types (`docs`, `chore`, `test`, `style`, `build`, `ci`).

**Scope extraction:** If the commit subject includes a scope in parentheses (e.g., `feat(api):`), extract it and format as `{scope}: {description}` in the changelog entry.

### Type Mapping

The complete mapping from Conventional Commit types/practices to Keep a Changelog sections:

| #   | Conventional Commit Signal              | KaC Section | When                                         |
| --- | --------------------------------------- | ----------- | -------------------------------------------- |
| 1   | `feat`                                  | Added       | New feature for the end user                 |
| 2   | `fix`                                   | Fixed       | Bug fix for the end user                     |
| 3   | `BREAKING CHANGE` footer                | Changed     | Any commit with a `BREAKING CHANGE:` trailer |
| 4   | `feat!` (breaking feature)              | Changed     | Feature with `!` after type                  |
| 5   | `fix!` (breaking fix)                   | Changed     | Fix with `!` after type                      |
| 6   | `refactor`                              | Changed     | Code restructuring without behaviour change  |
| 7   | `perf`                                  | Changed     | Performance optimisation                     |
| 8   | `deprecate`                             | Deprecated  | Feature marked for future removal            |
| 9   | `remove`                                | Removed     | Feature removed in this release              |
| 10  | `revert`                                | Removed     | Reversion of a prior commit                  |
| 11  | `security`                              | Security    | Vulnerability fix or security hardening      |
| 12  | `docs`                                  | _Skip_      | Skip unless breaking or explicitly notable   |
| 13  | `chore`, `test`, `style`, `build`, `ci` | _Skip_      | Skip unless breaking or explicitly notable   |

**Skip-type promotion rule:** If a commit with type `docs`, `chore`, `test`, `style`, `build`, or `ci` contains a `BREAKING CHANGE` footer or uses the `!` notation, promote it to `Changed` instead of skipping.

### Deduplication and Rephrasing Rules

1. **Never copy commit subjects verbatim.** Rewrite each entry in imperative mood (e.g., "Add login page" not "Added login page" or "adding login page"). Capitalise the first word; do not end with a period.
2. **Merge by commit SHA.** Before adding an entry, check if its commit SHA already exists in the `[Unreleased]` section. If the SHA is already recorded, skip the entry entirely. This ensures re-running with the same commits never duplicates entries.
3. **Strip metadata.** Remove issue numbers, PR references, and co-author lines from the entry text. (These belong in the commit, not the changelog.)
4. **Scope prefix.** If a scope is present, format as `{scope}: {description}`. Use the scope from the Conventional Commit message.
5. **Breaking change annotation.** If a commit is breaking, append `([#BREAKING])` to the end of the entry.
6. **User-provided entries (manual YAML).** Accept the description as-is — the user has already curated it. Do not rephrase.

### Step 4: Update the [Unreleased] section

1. Parse the `[Unreleased]` section heading and its content.
2. For each categorised commit, check if its commit SHA is already recorded in the `[Unreleased]` section. If found, skip it (idempotent re-run). Otherwise, append the new entry under the correct subheading.
3. If a subheading does not exist yet (e.g., no changes of type "Security" exist), create it under `[Unreleased]` in the canonical order: Added, Changed, Deprecated, Removed, Fixed, Security.
4. Preserve existing entries in `[Unreleased]` — only append new ones.
5. If a skip-type commit (`docs`, `chore`, `test`, `style`, `build`, `ci`) has a `!` breaking indicator or a `BREAKING CHANGE` footer, promote it to `Changed` instead of skipping.

**When no `[Unreleased]` section exists:** Create it at the top of the changelog body, above the first versioned section.

### Step 5: On release cut — promote Unreleased to versioned section

When the user requests a release (e.g., "cut release v1.2.3"):

1. Create a new versioned section heading: `## [{version}] - {YYYY-MM-DD}` where `{YYYY-MM-DD}` is today's ISO date.
2. Copy all content from `[Unreleased]` into the new section.
3. Replace the `[Unreleased]` section content with an empty state: `### Added` / `### Fixed` etc. with no entries (ready for the next cycle), OR keep a summary note like "No changes in this release yet."
4. Add a compare link at the bottom of the file:
   - `[{version}]: https://github.com/{owner}/{repo}/compare/v{previous}...v{version}`
   - Update the `[Unreleased]` compare link: `[unreleased]: https://github.com/{owner}/{repo}/compare/v{version}...HEAD`
   - If this is the first release, use: `[{version}]: https://github.com/{owner}/{repo}/releases/tag/v{version}`

### Step 6: Yank a release

When the user requests a yank (e.g., "yank v1.2.3"):

1. Locate the section `## [{version}] - {YYYY-MM-DD}` in the changelog.
2. Append `[YANKED]` to the version line: `## [{version}] - {YYYY-MM-DD} [YANKED]`.
3. Do **not** remove the section content — the historical change log is preserved.
4. Optionally add a note: `This release was yanked due to {reason}.` if the user provides a reason.

### Step 7: Validate and output

Before writing to disk, validate the updated `CHANGELOG.md`:

1. **Structural validity** — all required sections present and in order.
2. **Date format** — all dates are ISO 8601 (`YYYY-MM-DD`).
3. **Compare links** — every version has a corresponding `[{version}]:` link; the `[unreleased]:` link exists and points to the correct compare URL.
4. **No duplicates** — no identical entries within a section.
5. **Markdown lint** — no broken link references, no inconsistent heading levels.

On failure, report the specific validation error and abort the write. On success, write the file with `write` (or print the diff if `--dry-run`).

## Output Format

The full `CHANGELOG.md` follows the Keep a Changelog 2.0.0 template:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog 2.0.0](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- auth: Add OAuth2 login support
- api: Add user profile endpoint

### Changed

- session: Migrate session store to Redis ([#BREAKING])
- core: Replace UUID library with ulid for performance

### Fixed

- session: Resolve null pointer in session handler

## [1.2.0] - 2026-06-15

### Added

- api: Initial REST API scaffolding

### Fixed

- db: Correct connection pool exhaustion on timeout

[unreleased]: https://github.com/owner/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/owner/repo/releases/tag/v1.2.0
```

## Chained Skills

When this skill is active, the calling agent may invoke these skills as part of the workflow:

| Skill              | When to Chain                                   | Purpose                                       |
| ------------------ | ----------------------------------------------- | --------------------------------------------- |
| `rs-pr-packager`   | After changelog is updated for a release        | Prepare the PR body with changelog summary    |
| `rs-issue-to-plan` | When a manual change list is needed from issues | Convert issues into structured change entries |
| `gh`               | When fetching tags or releases                  | Resolve version tags, release history         |

## Keep a Changelog 2.0.0 Compliance Checklist

| #   | Requirement                                                                                      | Enforcement Point       |
| --- | ------------------------------------------------------------------------------------------------ | ----------------------- |
| 1   | `# Changelog` top-level heading exists                                                           | Step 1 — validation     |
| 2   | `[Unreleased]` section present (or explicit empty note)                                          | Step 4 — creation       |
| 3   | Version sections use `## [{version}] - {YYYY-MM-DD}` format                                      | Step 5 — promotion      |
| 4   | Each section uses only allowed subsections: Added, Changed, Deprecated, Removed, Fixed, Security | Step 3 — categorisation |
| 5   | `[YANKED]` tag appended to yanked releases                                                       | Step 6 — yank           |
| 6   | Compare links exist for every version at bottom of file                                          | Step 7 — validation     |
| 7   | `[unreleased]` link points to correct compare URL                                                | Step 5 — link update    |
| 8   | All dates are valid ISO 8601 dates (`YYYY-MM-DD`)                                                | Step 7 — validation     |

## See Also

- [Keep a Changelog 2.0.0](https://keepachangelog.com/en/2.0.0/) — the canonical specification
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) — commit message format parsed by this skill
- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) — versioning scheme used for release bumps
- [rs-pr-packager skill](../rs-pr-packager/SKILL.md) — downstream skill for PR preparation
- [rs-issue-to-plan skill](../rs-issue-to-plan/SKILL.md) — upstream skill for issue-to-change-entry conversion

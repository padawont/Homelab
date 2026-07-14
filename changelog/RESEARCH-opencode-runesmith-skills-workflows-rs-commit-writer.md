---
title: "Commit Writer Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-14
tags:
  - opencode
  - skills
  - commits
  - conventional-commits
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
  - knowledge: "knowledge/tooling/opencode/skills/workflow-patterns.md"
references:
  - url: "https://www.conventionalcommits.org/en/v1.0.0/"
    title: "Conventional Commits 1.0.0"
  - url: "https://keepachangelog.com/en/2.0.0/"
    title: "Keep a Changelog 2.0.0"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-14
---

# Commit Writer Skill Design (`rs-commit-writer`)

## Purpose

`rs-commit-writer` is a workflow skill for the `@runicengines/opencode-runesmith` plugin. It reads the staged diff via `git diff --cached` and generates a Conventional Commit 1.0.0 message — type, scope, description, optional body, and optional footer with breaking change and issue references. It maps commit types to Keep a Changelog 2.0.0 sections so that changelog generation downstream is consistent.

The skill eliminates "what do I write for a commit message?" — it produces a spec-compliant draft that the developer reviews and accepts.

## Skill Identity

| Property | Value |
|---|---|
| Plugin | `@runicengines/opencode-runesmith` |
| Skill name | `rs-commit-writer` |
| Skill prefix | `rs-` |
| Loading model | On-demand (via `skill({ name: "rs-commit-writer" })`) |
| Primary user | Developer agent |
| Secondary user | Reviewer agent (checks commit message compliance) |
| Trigger | After staging changes, before committing |

## Permission Model

| Permission | Purpose |
|---|---|
| `bash: { "git diff --cached": allow }` | Read the staged diff — the primary input |
| `read` | Read staged file content for context |
| `edit: deny` | The skill never modifies files |

The skill is **read-only** — it inspects staged changes and produces text output. It never modifies files or writes commit messages directly. The developer reviews the suggested message before committing.

## Input

The skill accepts no explicit parameters — it auto-detects from the git state:

1. **Staged diff** — read via `git diff --cached`.
2. **Last commit message** — read via `git log -1 --format=%B` for context (optional, helps detect branch conventions).
3. **Branch name** — read via `git rev-parse --abbrev-ref HEAD` for scope hints.

Optional parameters:
- `--type <type>` — override type detection.
- `--scope <scope>` — override scope detection.
- `--breaking` — force BREAKING CHANGE footer.
- `--issue <ref>` — add issue reference footer (e.g., `#42`).

## Workflow Steps

### Step 1: Read staged diff

1. Run `git diff --cached` to get the staged changes.
2. Analyse the diff to determine:
   - Which files changed (for scope and type inference).
   - The nature of changes (additions, modifications, deletions, renames).
   - Whether the change touches breaking patterns (removed exports, changed signatures).

### Step 2: Infer commit type

Analyse the diff to infer the Conventional Commit type:

| Diff Pattern | Inferred Type | Fallback |
|---|---|---|
| New files added, new exports, new API endpoints | `feat` | `feat` |
| Bug fix patterns (condition changes, edge case handling, error path fixes) | `fix` | `fix` |
| Removed exports, deleted public APIs, removed parameters | `feat!` or with `BREAKING CHANGE` footer | Check for `!` in scope |
| Renamed files, restructured imports, changed function signatures without adding functionality | `refactor` | `refactor` |
| Performance-related changes (algorithm changes, caching, batching) | `perf` | `perf` |
| Test files only (files in `test/`, `spec/`, `__tests__/`, `*_test.go`, `*.test.ts`) | `test` | `test` |
| Documentation files only (`.md`, `.qmd`, `.rst`, `docs/`) | `docs` | `docs` |
| CI configuration only (`.github/`, `.gitlab-ci.yml`, `Jenkinsfile`) | `ci` | `ci` |
| Build system only (`package.json`, `Makefile`, `Dockerfile`, `setup.py`) | `build` | `build` |
| Formatting, whitespace, style-only changes | `style` | `style` |
| Dependency updates, maintenance | `chore` | `chore` |

### Step 3: Infer scope

Analyse the file paths to determine scope:
- If files all share a common directory prefix, use that as scope (e.g., `auth`, `api`, `cli`).
- If files span multiple areas, use the most specific common directory.
- If no clear common scope, omit scope entirely.

The scope is written in lowercase kebab-case (e.g., `user-auth`, `db-migration`).

### Step 4: Generate commit message

Format the commit message per Conventional Commits 1.0.0:

```
<type>(<scope>): <description>

<body>

<footer>
```

**Description rules:**
- Imperative mood, present tense ("Add" not "Added" or "Adds").
- Capitalise the first word.
- No trailing period.
- Maximum 72 characters.
- Summarise what the change does, not how it works.

**Body rules (if needed):**
- Blank line after description.
- Wrap at 72 characters.
- Explain the motivation for the change.
- Contrast with the previous behaviour if relevant.

**Footer rules:**
- `BREAKING CHANGE: <description>` if the change is breaking (inferred from `!` type or diff analysis).
- `Closes #<issue>` or `Fixes #<issue>` if the branch name contains an issue number.
- `Refs #<issue>` for related issues.

### Step 5: Map to Keep a Changelog 2.0.0 section

Provide a changelog mapping hint:

| Conventional Commit | Changelog Section |
|---|---|
| `feat` | `Added` |
| `fix` | `Fixed` |
| Any type with `!` or `BREAKING CHANGE` footer | `Changed` or `Removed` (with `**BREAKING:**` prefix) |
| `refactor` | `Changed` |
| `perf` | `Changed` |
| `deprecate` | `Deprecated` (custom extension) |
| `remove` | `Removed` (custom extension) |
| `revert` | `Removed` or `Fixed` (depends on what is being reverted) |
| `security` | `Security` (custom extension) |
| `docs` | Skip (unless notable) |
| `chore` | Skip |
| `test` | Skip |
| `style` | Skip |
| `build` | Skip |
| `ci` | Skip |

This mapping is displayed as a note alongside the generated commit message, not embedded in the commit itself.

## Output

The skill outputs the generated commit message as text:

```
feat(auth): add OAuth2 token refresh endpoint

Implement token refresh flow with automatic expiry detection.
Existing tokens that expire within 5 minutes are refreshed transparently.

Closes #142
```

Alongside a changelog mapping hint:

```
> Changelog mapping: This commit maps to Keep a Changelog 2.0.0 > Added.
```

## Chains With

| Skill | Condition | Step |
|---|---|---|
| `rs-changelog-manager` (see [changelog-manager.md](changelog-manager.md)) | After commit is made — to update `[Unreleased]` | After this skill |
| `rs-pr-packager` (see [pr-packager.md](pr-packager.md)) | Before creating PR — commits feed into PR description | Before PR creation |
| `rs-pr-writer` | If writing PR body from issue/spec forward | Alternative workflow |

## Design Decisions

1. **Type inference from diff content**, not from file extensions alone. A change to `*.ts` files could be `feat`, `fix`, or `refactor` — the skill inspects the diff content (new exports, condition changes, parameter modifications) rather than guessing from the file path.

2. **Scope inferred from directory structure** rather than config. No `commitlint.config.js` or scope definition file is needed. If the team wants explicit scope control, the `--scope` override parameter lets them bypass inference.

3. **Output is a suggestion, not a commit**. The skill does not `git commit` automatically. The developer reviews and potentially edits the message before committing. This respects the developer's editorial control over commit history.

4. **Changelog mapping is advisory only**. The mapping from commit type to changelog section is displayed as a hint, not enforced. The `rs-changelog-manager` skill handles actual changelog categorisation; this skill just previews where the commit will appear.

## See Also

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) — The commit message specification
- [Keep a Changelog 2.0.0](https://keepachangelog.com/en/2.0.0/) — Changelog format this skill maps to
- [ADR 0002 — GitHub Etiquettes](../../../../adr/0002-github-etiquettes/overview.md) — Branch naming and commit conventions
- [Changelog Manager skill](changelog-manager.md) — Downstream consumer of commit type mapping
- [PR Writer skill](rs-pr-writer.md) — Complementary skill for PR body generation
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills) — Skill system reference

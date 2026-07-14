---
title: "PR Packager Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - skills
  - pr-packager
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
  - knowledge: "knowledge/tooling/opencode/skills/workflow-patterns.md"
references:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
  - url: "https://www.conventionalcommits.org/en/v1.0.0/"
    title: "Conventional Commits 1.0.0"
  - url: "https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests"
    title: "GitHub Pull Request Documentation"
  - url: "https://keepachangelog.com/en/2.0.0/"
    title: "Keep a Changelog 2.0.0"
last_audit_date: 2026-06-07
---

# PR Packager Skill Design

## Context

The `@runicengines/opencode-runesmith` plugin provides OpenCode agents with RunicEngines-specific skill workflows. The `rs-pr-packager` skill is a workflow skill — it coordinates multiple tools and agent capabilities to generate structured PR descriptions from local git commits, enforcing [ADR 0002: GitHub Etiquettes](/adr/0002-github-etiquettes/) conventions throughout.

This file is a research analysis: it documents the skill's design requirements, its recommended instruction body, and maps how it differs from the existing Knowledge Base `pr-packager` skill at `knowledge/tooling/opencode/skills/pr-packager.md`.

### Why a New Skill?

The existing `pr-packager` skill in the KB is a generic template for knowledge-base repos. It focuses on conventional changelog grouping and does not enforce branch naming conventions, PR title format compliance, issue linking, or ADR-specified merge workflows. The `rs-pr-packager` skill is built for **code repositories** that follow ADR 0002, where the PR description must meet organization-wide standards before it can be submitted.

### Skill Identity

| Property | Value |
|---|---|
| Plugin | `@runicengines/opencode-runesmith` |
| Skill name | `rs-pr-packager` |
| Skill prefix | `rs-` |
| Loading model | On-demand (via `skill({ name: "rs-pr-packager" })`) |
| Primary user | Developer agent |
| Secondary user | Architect agent |
| Trigger | Implementation complete, PR ready to create |

---

## Recommended SKILL.md Instructions

The following block is the recommended instruction body for the skill's `SKILL.md` file. It follows the workflow skill conventions defined in `knowledge/tooling/opencode/skills/workflow-patterns.md`: it declares trigger conditions, required permissions, a step-by-step workflow, output format, chained skills, and compliance checks.

```markdown
---
name: rs-pr-packager
description: >
  Generate structured PR descriptions from local git commits following
  ADR 0002 conventions. Validates branch names, enforces Conventional
  Commits, links issues, and produces a squash-merge-ready PR body.
license: MIT
compatibility: opencode
metadata:
  workflow: github
  audience: developers
  trigger: manual
---

# rs-pr-packager

## Purpose

Reads recent commits on a branch, parses them, and generates a complete
PR description that complies with ADR 0002 (GitHub Etiquettes). The skill
enforces branch naming, commit message format, issue linking, and review
requirements — producing output ready for `gh pr create` or manual submission.

## When to Invoke

- The user says "prepare a PR", "create a pull request", or "generate PR description".
- The user says "open a PR for this branch" or provides a branch name explicitly.
- A branch has unpushed commits and the user wants to submit them as a PR.

## Trigger

| Condition | Type |
|---|---|
| User provides branch name or asks to open a PR | Manual |
| After a `feat` or `fix` series of commits on a feature branch | Manual (auto-suggest) |

## Required Permissions

| Permission | Purpose |
|---|---|
| `bash: { "git *": "allow" }` | Run `git log`, `git diff`, `git rev-list`, `git branch` |
| `read` | Read branch context, changelog, convention files |
| `glob` | Find changed files by pattern |
| `grep` | Scan commit messages for Conventional Commit patterns |

The `gh` CLI is **optional** — the skill can output a PR body for manual
submission or pipe it directly into `gh pr create`. If available, the
agent should load the `gh` skill for submission (`skill({ name: "gh" })`).

## Input

The skill accepts one of:

- **Branch name** — e.g. `feat/42-user-auth` (defaults to current branch)
- **Commit range** — e.g. `main..HEAD` or a specific SHA range

If neither is provided, the skill resolves the current branch via
`git rev-parse --abbrev-ref HEAD` and computes the range as the commits
not yet on the default branch (`main`).

## Workflow Steps

### Step 1: Resolve branch and commit range

1. Determine branch name:
   - If the user provides a branch name, use it.
   - Otherwise, run `git rev-parse --abbrev-ref HEAD` to get the current branch.
2. Determine commit range:
   - If the user provides a range, use it.
   - Otherwise, compute `git merge-base HEAD origin/main` as the base
     and use `<base>..HEAD` as the range.
3. Validate that the range contains at least one commit. If empty, abort
   with a message explaining there are no new commits to PR.

### Step 2: Validate branch name against ADR 0002

The branch name MUST match the pattern:

```
{type}/{issue-number}-{kebab-description}
```

Where:
- `{type}` is a Conventional Commit type: `feat`, `fix`, `docs`, `chore`,
  `refactor`, `test`, `perf`, `build`, or `ci`.
- `{issue-number}` is a positive integer (e.g. `42`). It MUST be present
  when the branch addresses an issue; if absent, log a warning but continue.
- `{kebab-description}` is a kebab-case string of one or more words.

Validation logic:
1. Extract branch name after the last `/` (some workflows include a remote
   prefix like `origin/`).
2. Match against the regex:
   `^(feat|fix|docs|chore|refactor|test|perf|build|ci)/(\d+(-[a-z0-9]+)*)$`
3. If the branch does not match, produce a warning explaining the expected
   format and the specific violation (e.g. "missing issue number",
   "unknown type `add` — did you mean `feat`?").
4. If the branch does match, extract `{type}` and `{issue-number}` for use
   in the PR body.

### Step 3: Read and parse commit messages

1. Run `git log --oneline --no-merges <range>` for a summary overview.
2. Run `git log --format="%H%n%s%n%b%n---" <range>` for full commit details
   (hash, subject, body).
3. Parse each commit message against the Conventional Commits format:
   ```
   type(scope): short description
   ```
   - Recognised types: `feat`, `fix`, `docs`, `chore`, `refactor`,
     `test`, `perf`, `build`, `ci`.
   - Extract scope (optional) and description for each commit.
4. Note any commit that does **not** follow Conventional Commits and log
   a warning. Non-compliant commits SHOULD be flagged to the user so they
   can amend before the PR is opened.
5. Extract any `Closes #<number>` or `Fixes #<number>` footers from commit
   bodies. If multiple unique issue numbers are found, all should be
   included in the PR description.

### Step 4: Extract changed files

1. Run `git diff --name-only <base>..HEAD` to list changed files.
2. Group changed files by directory or logical area (e.g. `src/`, `tests/`,
   `docs/`).
3. Note any new files, deleted files, or renamed files from
   `git diff --name-status <base>..HEAD`.

### Step 5: Generate PR body

Assemble the following sections:

#### Title

The PR title MUST follow the Conventional Commits format:

```
{type}({scope}): {short description}
```

- Derive `{type}` from the branch name prefix.
- Derive `{scope}` from the primary area of change (inferred from the
  most-changed directory in `git diff --stat`).
- Derive `{short description}` from the branch's kebab-description,
   converted to imperative mood (e.g. `add-user-auth` → `add user auth`).
- If multiple commits have different types, use the most significant
  type (`feat` > `fix` > `refactor` > `docs` > `chore`).

#### Description Body

```
## Summary

{1-3 sentences summarising the overall change, derived from commit subjects}

## Changes

{bullet list of commits grouped by type, each with commit hash prefix and description}

## Related Issues

Closes #{issue-number}
{additional issue links, if any}

## Test Notes

- {list of what was tested / how to test}
- {any test gaps or known edge cases}

## Deployment Notes

- {migration steps, if any}
- {config changes, if any}
- {rollback considerations, if any}

---
**Checklist before merge:**
- [ ] At least 1 approving review obtained
- [ ] All CI checks passing
- [ ] Branch name matches `{type}/{issue-number}-{kebab-description}`
- [ ] PR title uses Conventional Commits format
```

### Step 6: Validate ADR 0002 compliance

Before final output, verify all ADR 0002 requirements:

| Requirement | Check |
|---|---|
| PR title is Conventional Commits | Verify against `^(feat|fix|docs|chore|refactor|test|perf|build|ci)(!?)(\(.+\))?: .+$` |
| PR description includes `Closes #` | Verify `Closes #\d+` or `Fixes #\d+` is present |
| Branch name matches pattern | Already validated in Step 2 |
| Merge strategy documented | Add a note: "This PR uses squash-merge per ADR 0002 §4" |
| Review requirement noted | Checklist includes review requirement |
| CI gates noted | Checklist includes CI checks requirement |

If any check fails, include the specific failure in a warnings section
of the output and suggest corrective action.

### Step 7: Output

If the `gh` CLI is loaded and the user confirms, execute:

```bash
gh pr create \
  --title "<title>" \
  --body "<body>" \
  --label "<type>" \
  --assignee "@me"
```

Otherwise, print the complete PR description to stdout for manual
submission, formatted as Markdown.

## Output Format

The skill outputs a structured PR description as Markdown text. The output
always includes:

1. **PR Title** — single line, Conventional Commits format
2. **PR Body** — complete body per the template above
3. **Compliance Summary** — pass/fail for each ADR 0002 requirement
4. **Warnings** — any non-blocking issues (non-compliant commit messages,
   missing issue number, etc.)

## Chained Skills

| Skill | Condition | Step |
|---|---|---|
| `rs-changelog-manager` | If changelog entries need updating | After Step 5, before output |
| `rs-issue-to-plan` | If the issue needs to be referenced for deeper context | Before Step 1 |

Chained skills are loaded via `skill({ name: "..." })` following the
Agent-Skill Interaction Flow documented in the workflow-patterns knowledge
note. There is no return-value contract between chained skills — each is
loaded and executed independently, and the agent coordinates results.

## See Also

- [ADR 0002: GitHub Etiquettes](/adr/0002-github-etiquettes/) — The canonical conventions this skill enforces
- [Workflow Skill Patterns](/knowledge/tooling/opencode/skills/workflow-patterns.md) — Cross-cutting workflow conventions
- [gh Skill](/knowledge/tooling/opencode/skills/gh-case-study.md) — Optional dependency for PR submission
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) — Commit message specification
```

---

## ADR 0002 Compliance Checklist

The following table maps every ADR 0002 requirement (as defined in `adr/0002-github-etiquettes/overview.md`) to its enforcement point in the `rs-pr-packager` skill:

| ADR 0002 § | Requirement | Skill Enforcement | Step |
|---|---|---|---|
| §1 Branch naming | Branches MUST follow `{type}/{issue-number}-{kebab-description}` | Regex validation; warning on mismatch | Step 2 |
| §2 Commit messages | Commits MUST follow Conventional Commits | Parser validation; warning on non-compliant commits | Step 3 |
| §3 PR workflow | PR MUST link the resolved issue (e.g. `Closes #42`) | Body generation includes `Closes #`; compliance check | Step 5–6 |
| §3 PR workflow | PR title MUST follow Conventional Commits | Title generation enforces type(scope): description | Step 5 |
| §4 Merge strategy | Squash merge MUST be the default | Body includes squash-merge note; documented assumption | Step 5 |
| §5 Code review | Each PR MUST receive >=1 approving review | Checklist section in PR body mandates review | Step 5 |
| §7 CI/CD | All checks MUST pass before merge | Checklist section in PR body requires CI pass | Step 5 |

---

## Analysis

### Design Decisions

**1. On-demand loading.** The skill is loaded via `skill({ name: "rs-pr-packager" })` only when a PR needs to be created. This avoids bloating the developer agent's context window with PR-related instructions during implementation work. It follows the established pattern from `knowledge/tooling/opencode/skills/workflow-patterns.md`.

**2. Branch-first resolution.** The skill resolves the branch from context before looking at commits. This means it can validate the branch name independently of commit history, and the branch name's type prefix becomes the authoritative source for the PR title's type — not the first commit's type. This handles the common case where a branch starts with a chore commit but the overall intent is a feature.

**3. Warning, don't block.** The skill validates ADR 0002 compliance but does not prevent the user from proceeding with a non-compliant PR. It flags warnings clearly so the user can amend before submission. This respects the developer's agency while making the conventions visible. The only hard abort is an empty commit range (nothing to PR).

**4. Separation from `gh`.** The skill does not bundle `gh` CLI invocation as a hard dependency. It outputs the complete PR description as Markdown and optionally pipes it into `gh pr create` if the `gh` skill is also loaded. This keeps the skill focused on PR body generation and avoids coupling to GitHub-specific submission mechanics.

**5. Chained skill integration.** The skill declares two optional chained skills (`rs-changelog-manager` and `rs-issue-to-plan`) but does not require them. The developer agent decides whether to invoke them based on context. This matches the chaining pattern documented in `workflow-patterns.md`.

### Differences from the KB `pr-packager` Skill

| Dimension | KB `pr-packager` | `rs-pr-packager` |
|---|---|---|
| Target repo | Knowledge base repos (content) | Code repos (software) |
| Branch validation | None | Required — ADR 0002 pattern |
| Commit parsing | Conventional Commits (optional) | Conventional Commits (required, validated) |
| Issue linking | Not enforced | Required — `Closes #` in body |
| Review requirements | Not mentioned | Checklist and enforcement |
| CI gates | Not mentioned | Checklist reference |
| Merge strategy | Not specified | Squash-merge assumption documented |
| Chained skills | `changelog-manager` | `rs-changelog-manager`, `rs-issue-to-plan` |
| Compliance output | None | Compliance summary per ADR 0002 § |

### Risk Assessment

**False positives in branch validation.** The regex `^(feat|fix|...)/(\d+(-[a-z0-9]+)*)$` may reject valid branches that use a conventional commit type not in the standard set (e.g. `security/`, `wip/`). The warning message should suggest the closest standard type, not block execution. If RunicEngines adopts additional types via a superseding ADR, the regex should be updated.

**Commit range ambiguity.** When the branch has been rebased or force-pushed, `git merge-base HEAD origin/main` may not reflect the true base. The skill should fall back to `git log --cherry-pick` or, if the user provided an explicit range, trust it.

**Multi-issue branches.** A branch may close multiple issues; the current design extracts all `Closes`/`Fixes` footers across all commits. This is correct per ADR 0002, which requires each PR to link its issues but does not limit it to one.

### Recommendations

1. **Implement PR title linting as a standalone check.** The regex in Step 6 can be extracted into a reusable validation function that the `rs-pr-packager` skill imports, keeping the skill focused on workflow orchestration rather than format details.

2. **Add a `--dry-run` flag.** Before creating a PR, the skill should offer a dry-run mode that prints the PR body and compliance warnings without submitting. This lets developers review and amend before the PR is opened.

3. **Default to the issue title.** When the branch resolves to a single issue (via `{issue-number}` in the branch name), fetch the issue title from GitHub and use it as the basis for the PR description summary. This requires the `gh` skill to be loaded for issue metadata lookup.

4. **Store the compliance summary in a file.** For auditability, the skill should optionally write the compliance check results to a file (e.g., `.pr-compliance.md`) that CI can read. This bridges the gap between agent-generated PRs and automated CI enforcement.

---

## See Also

- [ADR 0002 — GitHub Etiquettes](/adr/0002-github-etiquettes/) — The conventions this skill enforces
- [Knowledge: OpenCode Skills Overview](/knowledge/tooling/opencode/skills/overview/) — OpenCode skill system reference
- [Knowledge: Workflow Skill Patterns](/knowledge/tooling/opencode/skills/workflow-patterns/) — Cross-cutting workflow conventions in the KB
- [Knowledge: PR Packager (KB variant)](/knowledge/tooling/opencode/skills/pr-packager/) — The existing KB-focused `pr-packager` skill
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills) — OpenCode's official docs
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) — The commit specification used by ADR 0002

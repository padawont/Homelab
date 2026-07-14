---
title: "PR Writer Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-14
tags:
  - opencode
  - skills
  - pr
  - github
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
  - knowledge: "knowledge/tooling/opencode/skills/workflow-patterns.md"
references:
  - url: "https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests"
    title: "GitHub Pull Request Documentation"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-14
---

# PR Writer Skill Design (`rs-pr-writer`)

## Purpose

`rs-pr-writer` is a workflow skill for the `@runicengines/opencode-runesmith` plugin. It generates a PR body from an issue or specification (the output of `rs-issue-to-plan`), working **forward** from requirements to PR description. This complements `rs-pr-packager`, which works **backward** from commits to PR description.

The skill produces a PR body with: summary, changes list, testing notes, and checklist, all following ADR 0002 conventions for PR format.

## Skill Identity

| Property | Value |
|---|---|
| Plugin | `@runicengines/opencode-runesmith` |
| Skill name | `rs-pr-writer` |
| Skill prefix | `rs-` |
| Loading model | On-demand (via `skill({ name: "rs-pr-writer" })`) |
| Primary user | Developer agent (before coding for draft PR) |
| Secondary users | Spec-Writer agent, Reviewer agent |
| Trigger | Draft PR creation, spec-to-PR handoff |

## Relationship to rs-pr-packager

The two PR skills serve complementary workflows:

| Dimension | `rs-pr-packager` | `rs-pr-writer` |
|---|---|---|
| **Direction** | Backward — from existing commits | Forward — from issue/spec |
| **Input** | `git log` output, commit range | Issue, spec, implementation plan |
| **When used** | After implementation, commits exist | Before or during implementation |
| **Output** | PR description with changelog | PR body with design rationale, testing notes, checklist |
| **Primary user** | Developer (submitting finished work) | Developer (opening draft PR early) |

Use `rs-pr-writer` when you want to open a draft PR early (before implementation is complete) to signal intent and get early feedback. Use `rs-pr-packager` to generate the final PR description from the completed commit history.

## Permission Model

| Permission | Purpose |
|---|---|
| `read` | Read issue body, spec document, implementation plan |
| `glob` | Find relevant spec and issue files |
| `write` | Write PR body output (to a file or clipboard) |
| `edit: deny` | The skill never modifies source files |

The skill is **read-only** for input and **write** for the PR body output. It respects the boundary between reading plans/specs and producing a PR description.

## Input

The skill accepts:

1. **Issue reference** — GitHub issue number or URL. The skill fetches the issue body, title, labels, and linked projects.
2. **Spec document** (optional) — path to a spec produced by `rs-issue-to-plan`. If provided, the skill extracts phases, acceptance criteria, and test strategy from the spec.
3. **Implementation notes** (optional) — free-form text describing what was implemented, any deviations from the spec, and known limitations.

## Workflow Steps

### Step 1: Load input sources

1. If an issue reference is provided, use the `gh` skill to fetch the issue details:
   - Title and body.
   - Labels (to derive PR label suggestions).
   - Milestone (to suggest version target).
   - Assignee and linked PRs (to avoid duplicates).
2. If a spec document is provided, parse it for:
   - Phases and their acceptance criteria.
   - Test strategy.
   - Open questions.
   - Related research documents.

### Step 2: Generate PR title

The PR title follows ADR 0002 conventions:

```
<type>(<scope>): <description>
```

- **Type**: Derived from the issue label or spec type (`feat`, `fix`, `refactor`, `docs`, `chore`).
- **Scope**: Derived from the issue's area label or spec's component.
- **Description**: Concise summary (max 72 chars), imperative mood, no trailing period.

If the issue title already follows Conventional Commits format, use it directly.

### Step 3: Generate PR body sections

#### Summary

A concise overview of what this PR does and why. Reference the issue:

```markdown
## Summary

Implements user authentication with OAuth2 token refresh. Users can now
stay logged in across sessions without re-entering credentials.

Closes #142
```

#### Changes

A structured list of changes, organized by category:

```markdown
## Changes

### Added
- OAuth2 token refresh endpoint (`POST /auth/refresh`)
- Automatic token expiry detection middleware
- Refresh token storage in database

### Changed
- Auth middleware now checks for token expiry before validating signature
- Login response now includes `refresh_token` field

### Fixed
- Token validation no longer crashes on malformed tokens
```

Each entry is a concise description. The categories mirror Keep a Changelog 2.0.0 sections.

#### Testing Notes

How the changes were tested:

```markdown
## Testing

- [x] Unit tests added for token refresh logic (92% coverage on new code)
- [x] Integration test for full auth flow (login → refresh → logout)
- [x] Manual test: verified refresh works within 5-min expiry window
- [x] Manual test: verified expired refresh tokens are rejected
```

#### Checklist

ADR 0002 compliance checklist:

```markdown
## Checklist

- [ ] Branch name follows `{type}/{issue-number}-{kebab-description}` format
- [ ] Commits follow Conventional Commits format
- [ ] Tests pass (`npm test`)
- [ ] Documentation updated (README, API docs, changelog)
- [ ] Self-review completed
- [ ] At least one approving review required before merge
```

The checklist is pre-populated based on the PR type (feature PRs include documentation, hotfixes skip docs).

### Step 4: Generate labels and reviewer suggestions

Based on the issue labels and PR type, suggest:

- **Labels** to apply (copied from the issue per root AGENTS.md PR creation conventions).
- **Reviewers** based on CODEOWNERS patterns (if accessible).
- **Milestone** if the issue is linked to one.

## Output

The skill outputs the complete PR body as structured markdown:

```markdown
## Summary

Implements user authentication with OAuth2 token refresh...

Closes #142

## Changes

### Added
- ...

### Changed
- ...

## Testing

- [x] Unit tests added...
- [x] Manual verification...

## Checklist

- [ ] Branch name follows `feat/142-user-auth`
- [ ] Commits follow Conventional Commits
- ...
```

## Chains With

| Skill | Condition | Step |
|---|---|---|
| `rs-issue-to-plan` (see [issue-to-plan.md](issue-to-plan.md)) | Before — to get the spec that feeds into the PR | Input source |
| `rs-pr-packager` (see [pr-packager.md](pr-packager.md)) | After — to finalise PR description from actual commits | Complementary |
| `rs-changelog-manager` (see [changelog-manager.md](changelog-manager.md)) | After — to update changelog before PR submission | After PR creation |
| `rs-commit-writer` | During — to produce commits that match the PR description | During implementation |

## Design Decisions

1. **Forward from issue/spec vs backward from commits**. `rs-pr-writer` generates a PR body before implementation is complete. This lets developers open draft PRs early to get feedback on approach before investing in full implementation. `rs-pr-packager` handles the final pass after commits are made.

2. **Issue-driven PR generation**. The skill starts from the issue, not from the diff. This ensures the PR description explains *why* the change exists, not just *what* changed. The `rs-pr-packager` skill covers the what-changed angle.

3. **Checklist is pre-populated but not auto-checked**. The checklist starts unchecked — the developer reviews each item. This keeps the developer accountable for completeness while reducing the friction of writing the checklist from scratch.

4. **ADR 0002 compliance enforced at generation time**. The PR title format, branch naming suggestion, and checklist items all follow ADR 0002 conventions. The skill is the enforcement mechanism for PR-level conventions.

## See Also

- [ADR 0002 — GitHub Etiquettes](../../../../adr/0002-github-etiquettes/overview.md) — PR format conventions this skill enforces
- [PR Packager skill](pr-packager.md) — Complementary backward-from-commits PR generation
- [Issue-to-Plan skill](issue-to-plan.md) — Produces the spec that feeds into this skill
- [Changelog Manager skill](changelog-manager.md) — Changelog updates as part of PR workflow
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills) — Skill system reference

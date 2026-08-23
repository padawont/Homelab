---
name: rs-pr-writer
description: >
  Generate a structured PR description from a GitHub issue and
  implementation spec. Produces a squash-merge-ready PR body following
  ADR 0002 conventions with Summary, Changes, Testing Notes, and
  ADR 0002 Checklist sections.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: github
  audience: developers
  trigger: manual+chained
---

# rs-pr-writer

## Purpose

Generates a complete, squash-merge-ready PR description from a GitHub issue
and/or an implementation specification (e.g. produced by `rs-issue-to-plan`).
This is the _forward_ direction — starting from requirements and producing
the PR body before implementation begins — complementing `rs-pr-packager`
which works _backward_ from commits.

The output follows ADR 0002 conventions: a Conventional Commits title,
Summary section, Changes section, Testing Notes, and an ADR 0002 compliance
checklist.

## When to Invoke

- The user says "write a PR for issue #N", "generate PR description from this issue",
  or "create a PR body from the spec".
- After `rs-issue-to-plan` has produced a plan and the user wants the corresponding PR body.
- Before implementation begins, to establish the PR description as the source of truth.

### Trigger

| Condition                                                     | Type    |
| ------------------------------------------------------------- | ------- |
| User provides an issue number or spec to convert to a PR body | Manual  |
| Chained after `rs-issue-to-plan` produces a spec              | Chained |

## Required Permissions

| Permission | Purpose                                                              |
| ---------- | -------------------------------------------------------------------- |
| `read`     | Read the issue body and spec documents from `.runesmith/` scratchpad |
| `glob`     | Find issue files, spec files, and existing PR descriptions           |
| `edit`     | Write the output `.pr.md` file to the scratchpad                     |
| `bash`     | Fetch issue data: `gh issue view`                                    |

This skill does not delegate tasks to external agents via the `task()` tool;
all work is performed by the calling agent.

## Input

The skill accepts one or more of the following inputs:

| Input                  | Description                                                                                      | Required                                             |
| ---------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------- |
| `issue`                | GitHub issue object with `{title, number, body}` fields                                          | No (but at least one of issue/spec must be provided) |
| `spec`                 | Implementation spec object (e.g. from `rs-issue-to-plan`) with `{phases: [{name, description}]}` | No (but at least one of issue/spec must be provided) |
| `implementation_notes` | Free-form string with additional context, library choices, approach notes                        | No                                                   |

If the user provides only a URL or issue number (e.g. "write a PR for #42"),
the skill should resolve the issue via `gh issue view 42 --json title,body`
(if the `gh` CLI is available) or ask the user to paste the issue content.

## Workflow Steps

### Step 1: Initialize session scratchpad

Chain `rs-scratchpad init` via `skill({ name: "rs-scratchpad" })` to create or
validate the active session scratchpad directory. Capture the returned session
path as `{session}` (e.g., `.runesmith/2026-07-19-feat_user-auth/`). All
subsequent file output paths use this session directory.

If `rs-scratchpad` is unavailable, fall back to creating the session directory
manually using the same convention: `.runesmith/{date}-{sanitized-branch}/`
with subdirectories `specs/`, `reports/`, `logs/`, `cache/`, `pipeline/`,
`stages/`, `prs/`.

### Step 2: Load inputs

1. Parse the issue object (title, number, body) if provided.
2. Parse the spec object (phases with name + description) if provided.
3. Parse implementation notes if provided.
4. Validate that at least one of `issue` or `spec` is present. If neither is
   provided, abort with a message asking the user to supply one.
5. If no spec object is provided directly but a `{session}` scratchpad exists,
   check `{session}/specs/` for available spec files from a prior
   `rs-issue-to-plan` run. If a matching spec file is found, parse it as the
   spec input.

### Step 3: Generate PR title

Derive a Conventional Commits title from the available inputs:

```
{type}({scope}): {short description}
```

1. **Type**: Infer from the issue title prefix (e.g. `feat:`, `fix:`) or
   issue labels. If no prefix is detectable, default to `feat`.
   - Recognised types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`,
     `perf`, `build`, `ci`.
2. **Scope**: Infer from the primary area of change mentioned in the issue
   body or spec phase names (e.g. "auth", "api", "frontend").
3. **Description**: Derive from the issue title (strip any conventional
   commit prefix), converted to imperative mood.

### Step 4: Generate PR body

Assemble the following sections:

#### Summary

Write 1–3 sentences summarising the overall change, derived from the issue
body, spec phase descriptions, and implementation notes.

#### Changes

List each spec phase as a bullet point. If no spec is provided, derive
change bullet points from the issue body. Each bullet should describe what
will be implemented:

```
- {phase 1 name}: {phase 1 description}
- {phase 2 name}: {phase 2 description}
```

If implementation notes are provided, incorporate relevant details into the
corresponding change bullet (e.g. library choices, architectural decisions).

#### Related Issues

If an issue number is provided:

```
Closes #{issue-number}
```

If no issue number is available, omit this section.

#### Testing Notes

Generate testing guidance based on the scope of changes:

- List what should be tested (unit tests, integration tests, manual testing).
- Note any known edge cases or test gaps.
- If implementation notes mention specific test strategy, reflect it here.

#### Implementation Notes (optional)

If implementation notes are provided, add this section to capture
architectural decisions, library choices, and approach rationale:

```
## Implementation Notes

{implementation notes}
```

#### ADR 0002 Checklist

```
---
**Checklist before merge:**
- [ ] At least 1 approving review obtained
- [ ] All CI checks passing
- [ ] Branch name matches `{type}/{issue-number}-{kebab-description}`
- [ ] PR title uses Conventional Commits format
```

### Step 5: Validate generated output

Before final output, verify:

1. Title follows Conventional Commits format.
2. PR body contains all required sections.
3. Issue link is present when an issue number is provided.
4. Checklist includes all ADR 0002 items.

If any check fails, log a warning and suggest corrective action.

### Step 6: Output

Write the PR description to a file at:

{session}/prs/{issue-number}-{kebab-title}.pr.md

Where:

- `{session}` is the session path returned by `rs-scratchpad init` (Step 1),
  or the fallback convention `.runesmith/{date}-{sanitized-branch}/`.
- `{issue-number}` is the issue number (or `000` if not available).
- `{kebab-title}` is the PR title converted to kebab-case.

Output the file path to the user and display the PR body summary.

## Dry-Run Mode

Pass `--dry-run` to print the complete PR body to stdout without writing to
a file. All generation steps execute identically except Step 6 (output).

## Output Format

The skill writes a Markdown file to the scratchpad. The file always includes:

1. **PR Title** — single line, Conventional Commits format
2. **PR Body** — Summary, Changes, Related Issues, Testing Notes,
   Implementation Notes (optional), ADR 0002 Checklist

## ADR 0002 Compliance Mapping

| ADR 0002 §        | Requirement                               | Skill Enforcement                                    | Step   |
| ----------------- | ----------------------------------------- | ---------------------------------------------------- | ------ |
| §3 PR workflow    | PR MUST link the resolved issue           | Body generation includes `Closes #N`                 | Step 4 |
| §3 PR workflow    | PR title MUST follow Conventional Commits | Title generation enforces `type(scope): description` | Step 3 |
| §4 Merge strategy | Squash merge MUST be the default          | Checklist includes squash-merge note                 | Step 4 |
| §5 Code review    | Each PR MUST receive >=1 approving review | Checklist section mandates review                    | Step 4 |
| §7 CI/CD          | All checks MUST pass before merge         | Checklist section requires CI pass                   | Step 4 |

## Chained Skills

| Skill              | Condition                                                                | Step              |
| ------------------ | ------------------------------------------------------------------------ | ----------------- |
| `rs-scratchpad`    | Always (session initialization)                                          | Step 1            |
| `rs-issue-to-plan` | If a spec is needed before generating the PR body                        | Before Step 2     |
| `rs-pr-packager`   | If commits already exist and the PR body should be verified against them | After Step 6      |

Chained skills are loaded via `skill({ name: "..." })` following the
Agent-Skill Interaction Flow documented in the workflow-patterns knowledge
note.

## See Also

- [rs-pr-packager SKILL.md](../rs-pr-packager/SKILL.md) — Backward direction (commits → PR body)
- [rs-issue-to-plan SKILL.md](../rs-issue-to-plan/SKILL.md) — Produces the spec consumed by this skill
- [rs-scratchpad SKILL.md](../rs-scratchpad/SKILL.md) — Session scratchpad management
- [ADR 0002: GitHub Etiquettes](../adr/0002-github-etiquettes/overview.md) — The canonical conventions this skill enforces
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) — Commit message specification

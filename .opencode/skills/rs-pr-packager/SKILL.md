---
name: rs-pr-packager
description: >
  Generate structured PR descriptions from local git commits following
  ADR 0002 conventions. Validates branch names, enforces Conventional
  Commits, links issues, and produces a squash-merge-ready PR body.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: github
  audience: developers
  trigger: manual
---

# rs-pr-packager

## Purpose

Reads recent commits on a branch, parses them, and generates a complete
PR description that complies with ADR 0002 (GitHub Etiquettes). Enforces
branch naming, commit message format, issue linking, and review
requirements — producing output ready for `gh pr create` or manual submission.

## When to Invoke

- The user says "prepare a PR", "create a pull request", or "generate PR description".
- The user says "open a PR for this branch" or provides a branch name explicitly.
- A branch has unpushed commits and the user wants to submit them as a PR.

### Trigger

| Condition                                                     | Type                  |
| ------------------------------------------------------------- | --------------------- |
| User provides branch name or asks to open a PR                | Manual                |
| After a `feat` or `fix` series of commits on a feature branch | Manual (auto-suggest) |

## Required Permissions

| Permission          | Purpose                                                 |
| ------------------- | ------------------------------------------------------- |
| bash (git commands) | Run `git log`, `git diff`, `git rev-list`, `git branch` |
| read                | Read branch context, changelog, convention files        |
| glob                | Find changed files by pattern                           |
| grep                | Scan commit messages for Conventional Commit patterns   |

The `gh` CLI is **optional** — the skill can output a PR body for manual
submission or pipe it directly into `gh pr create`. If available, load the
`gh` skill for submission (`skill({ name: "gh" })`).

This skill does not delegate tasks to external agents via the task() tool; all work is performed by the calling agent.

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

| Requirement                        | Check                                                   |
| ---------------------------------- | ------------------------------------------------------- |
| PR title is Conventional Commits   | Verify against `^(feat                                  | fix | docs | chore | refactor | test | perf | build | ci)(!?)(\(.+\))?: .+$` |
| PR description includes `Closes #` | Verify `Closes #\d+` or `Fixes #\d+` is present         |
| Branch name matches pattern        | Already validated in Step 2                             |
| Merge strategy documented          | Add a note: "This PR uses squash-merge per ADR 0002 §4" |
| Review requirement noted           | Checklist includes review requirement                   |
| CI gates noted                     | Checklist includes CI checks requirement                |

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

## Dry-Run Mode

Pass `--dry-run` to print the complete PR body and compliance warnings to
stdout without submitting. This lets the user review and amend before the
PR is opened. All steps execute identically except Step 7 (output), where
the body is printed instead of piped to `gh pr create`.

## Output Format

The skill outputs a structured PR description as Markdown text. The output
always includes:

1. **PR Title** — single line, Conventional Commits format
2. **PR Body** — complete body per the template above
3. **Compliance Summary** — pass/fail for each ADR 0002 requirement
4. **Warnings** — any non-blocking issues (non-compliant commit messages,
   missing issue number, etc.)

> [!NOTE]
> In this repo the ADR 0002 conventions are mirrored in the root `AGENTS.md`
> (Git Guidelines), which is the local source of truth. ADR 0002 itself lives
> in the sibling `RunicEngines/knowledge-base` repo and does not exist here.

## ADR 0002 Compliance Checklist

| ADR 0002 §         | Requirement                                                      | Skill Enforcement                                      | Step     |
| ------------------ | ---------------------------------------------------------------- | ------------------------------------------------------ | -------- |
| §1 Branch naming   | Branches MUST follow `{type}/{issue-number}-{kebab-description}` | Regex validation; warning on mismatch                  | Step 2   |
| §2 Commit messages | Commits MUST follow Conventional Commits                         | Parser validation; warning on non-compliant commits    | Step 3   |
| §3 PR workflow     | PR MUST link the resolved issue (e.g. `Closes #42`)              | Body generation includes `Closes #`; compliance check  | Step 5–6 |
| §3 PR workflow     | PR title MUST follow Conventional Commits                        | Title generation enforces type(scope): description     | Step 5   |
| §4 Merge strategy  | Squash merge MUST be the default                                 | Body includes squash-merge note; documented assumption | Step 5   |
| §5 Code review     | Each PR MUST receive >=1 approving review                        | Checklist section in PR body mandates review           | Step 5   |
| §7 CI/CD           | All checks MUST pass before merge                                | Checklist section in PR body requires CI pass          | Step 5   |

## Chained Skills

| Skill                  | Condition                                              | Step                        |
| ---------------------- | ------------------------------------------------------ | --------------------------- |
| `rs-changelog-manager` | If changelog entries need updating                     | After Step 5, before output |
| `rs-issue-to-plan`     | If the issue needs to be referenced for deeper context | Before Step 1               |

Chained skills are loaded via `skill({ name: "..." })` following the
Agent-Skill Interaction Flow documented in the workflow-patterns knowledge
note. There is no return-value contract between chained skills — each is
loaded and executed independently, and the caller coordinates results.

## See Also

- [ADR 0002: GitHub Etiquettes](/adr/0002-github-etiquettes/) — The canonical conventions this skill enforces (sibling knowledge-base repo)
- [AGENTS.md Git Guidelines](./AGENTS.md) — local source of truth in this repo
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) — Commit message specification
- [gh Skill](/knowledge/tooling/opencode/skills/gh-case-study.md) — Optional dependency for PR submission
- [Workflow Skill Patterns](/knowledge/tooling/opencode/skills/workflow-patterns.md) — Cross-cutting workflow conventions

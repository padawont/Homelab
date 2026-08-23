---
name: rs-commit-writer
description: >
  Generate structured Conventional Commit messages from a staged git diff.
  Analyses file paths, diff content, and branch name to infer commit type,
  scope, breaking changes, and issue references. Produces formatted commit
  messages following the Conventional Commits 1.0.0 specification with
  imperative mood, 72-character subject line, and optional body/footer.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: utility
  audience: developers
  trigger: manual+chained
---

## Purpose

Analyses a `git diff --staged` output and generates a structured
Conventional Commit message. Infers the commit type from diff patterns,
detects scope from common file path prefixes, identifies breaking
changes, and extracts issue references from the branch name. Outputs a
formatted commit message ready for `git commit -m`.

## When to Invoke

Trigger `rs-commit-writer` when:

- Staging changes and about to commit — wants a well-formed Conventional Commit message.
- Preparing changes before invoking `rs-changelog-manager` (which consumes commit messages).
- Preparing changes before invoking `rs-pr-packager` (which builds PR descriptions from commits).
- Working on a branch with an issue number in the name and wants automatic `Closes #N` footer.

Do NOT invoke when:

- The staged diff is empty (nothing to commit).
- The task is not code-related (e.g., planning, documentation review).
- The agent is running tests or performing analysis (no commit intended).

## Workflow Steps

### Step 1 — Read the staged diff

1. Run `git diff --staged` to obtain the staged diff.
2. If the output is empty, return: `No changes staged — nothing to commit.`
3. Parse the diff to extract:
   - List of changed files (new, modified, deleted, renamed).
   - Added and removed lines per file.
   - File extensions and directory paths.

### Step 2 — Infer commit type from diff patterns

Classify the commit type by matching the diff content and file paths
against the mapping table below. The first matching pattern wins.
If no pattern matches, default to `chore`.

| #   | Pattern                                           | Detected type | Example indicators                                                                                         |
| --- | ------------------------------------------------- | ------------- | ---------------------------------------------------------------------------------------------------------- |
| 1   | New function, method, class, or module definition | `feat`        | `+def `, `+class `, `+func `, `+impl `, `+public `, new file with `def`/`class`/`impl`                     |
| 2   | New route, endpoint, API handler, or command      | `feat`        | `+router.`, `+@app.`, `+.post(`, `+.get(`, `+Command`, new endpoint definition                             |
| 3   | Bug fix, error handling, null check, or edge case | `fix`         | `+if x is None`, `+try:`, `+except`, `+handle_error`, `+fix(`, patch to existing logic                     |
| 4   | Test files only (no non-test files changed)       | `test`        | Files matching `**/test_*`, `**/*.test.*`, `**/*.spec.*`, or under `tests/`, `spec/` directories           |
| 5   | Documentation files only                          | `docs`        | Files under `docs/`, `*.md`, `*.rst`, `*.txt` (readme, changelog)                                          |
| 6   | CI/CD configuration changes                       | `ci`          | `.github/`, `Dockerfile`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/`                                    |
| 7   | Build system changes                              | `build`       | `package.json`, `Cargo.toml`, `tsconfig.json`, `webpack.config.js`, `Makefile`, `pyproject.toml`, `go.mod` |
| 8   | Formatting-only changes (whitespace only)         | `style`       | Only whitespace, indentation, semicolon, or formatting changes in the diff                                 |
| 9   | Code restructuring without new feature            | `refactor`    | Renames, moves, extracts methods, changes structure without new behaviour                                  |
| 10  | Performance optimisation                          | `perf`        | Caching, memoization, algorithm changes, async/await, batch processing                                     |
| 11  | Maintenance, config, or tooling changes           | `chore`       | `.gitignore`, `.env`, `.editorconfig`, dependency version bumps, lint config                               |

### Step 3 — Infer scope from file paths

1. Collect all changed file paths from the diff.
2. Identify the common directory prefix shared by all changed files.
3. If the common prefix is a meaningful project domain (e.g., `auth/`, `api/`, `docs/`, `db/`, `ui/`), use it as the scope.
4. If files span multiple top-level directories, omit the scope.
5. If only one file is changed, use the first directory component as scope (e.g., `src/routes/users.py` → `routes`).

### Step 4 — Detect breaking changes

1. Check if any file in the diff contains the literal `BREAKING CHANGE:` in its diff content.
2. Check the branch name for a `!` suffix after the type prefix (e.g., `feat!/*`).
3. If either is detected, append `!` after the type: `feat!` or `fix!`.
4. Add a `BREAKING CHANGE:` footer line with a description extracted from the diff.

### Step 5 — Extract issue reference from branch name

1. Parse the branch name for a pattern like `{type}/{number}-{description}` or `{type}-{number}-{description}`.
2. If a numeric issue number is found, add a `Closes #N` footer.
3. If no issue number is found, omit the footer.

### Step 6 — Generate commit message

Build the commit message following the Conventional Commits 1.0.0 format:

```
type(!)(scope): description

Optional body paragraph with
wrapped lines at 72 characters.

BREAKING CHANGE: description of the breaking change
Closes #42
```

Subject line rules:

- Maximum **72 characters**.
- Start with a **capital letter**.
- **No trailing period**.
- Written in **imperative mood** ("Add feature" not "Added feature").
- Format: `type(scope): description` (scope is optional).

Body rules (if needed):

- Separate from subject by a blank line.
- Wrap at 72 characters.
- Explain what and why, not how.

Footer rules:

- `BREAKING CHANGE:` — description of the breaking change (if detected).
- `Closes #N` — issue reference (if detected from branch name).

## Output Format

The skill returns the commit message as a plain text string.

On success:

```
feat(auth): Add JWT token generation for user authentication

Generate JWT tokens with configurable expiry and scope claims.
Replaces the legacy base64 token format.

Closes #42
```

On empty diff:

```
No changes staged — nothing to commit.
```

## Required Permissions

- `read` — to read the staged diff via `git diff --staged`.
- `glob` — to inspect file paths in the diff output.
- `bash` — `allow with scope: git diff --staged, git rev-parse --abbrev-ref HEAD`.
- `edit` — **deny** — this skill never modifies files on disk.

## Chained Skills

`rs-commit-writer` is designed to feed into downstream skills:

| Skill                  | Stage        | Purpose                                               |
| ---------------------- | ------------ | ----------------------------------------------------- |
| `rs-changelog-manager` | After commit | Parses the commit message for CHANGELOG.md generation |
| `rs-pr-packager`       | After commit | Includes the commit in the PR description             |
| `rs-pr-writer`         | After commit | Uses the commit as the PR title template              |

## Error Handling

| Scenario                  | Behaviour                                                                |
| ------------------------- | ------------------------------------------------------------------------ |
| Empty staged diff         | Return `No changes staged — nothing to commit.`                          |
| Binary files in diff      | Skipped during pattern analysis, remaining text files processed normally |
| No pattern match          | Default to `chore` type                                                  |
| `git diff --staged` fails | Report error gracefully                                                  |

Branch names and file paths from git output MUST be shell-escaped using `shlex.quote()` or executed via `subprocess.run()` with argument list (not shell string).

## See Also

- Conventional Commits 1.0.0 specification: https://www.conventionalcommits.org/
- `rs-changelog-manager` — parses conventional commits into changelog entries
- `rs-pr-packager` — builds PR descriptions from git commits
- `rs-pr-writer` — generates full PR bodies from structured commits

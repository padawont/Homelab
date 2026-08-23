---
name: rs-scratchpad
description: >
  Manage session scratchpads within .runesmith/ directories:
  create, clear, and inspect working session directories with
  structured subdirectories for specs, reports, logs, cache, pipeline, stages, and prs.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: utility
  audience: developers, tech-writer, devops
  trigger: manual+chained
---

## Purpose

Manages per-session scratchpad directories under `.runesmith/{date}-{sanitized-branch}/` with three commands: **init** (create), **clear** (destroy), and **status** (report). Tracks the active session via `.opencode/.runesmith-active`.

## When to Invoke

Trigger `rs-scratchpad` when:

- Starting a new working session on a feature branch (`init`).
- Checking which session is active and its contents (`status`).
- Cleaning up a finished or abandoned session (`clear`).

Do NOT invoke when:

- The agent is performing read-only codebase analysis.
- The task has no session or scratchpad requirements.
- Operating outside a `.opencode/`-configured project.

## Workflow Steps

### init — Create a session scratchpad

1. Determine the branch name:
   - Run `git rev-parse --abbrev-ref HEAD` to get the current branch.
   - If the command fails (no git repo), use `unknown`.
   - If the result is `HEAD` (detached HEAD), use `detached`.
2. Determine the current date in ISO format (`YYYY-MM-DD`).
3. Sanitize the branch name: replace any character that is not alphanumeric, hyphen, underscore, or period with an underscore `_`. Strip leading/trailing hyphens and dots after sanitization.
4. Construct the candidate session path: `.runesmith/{date}-{sanitized-branch}/`.
5. Check for collisions under `.runesmith/`:
   - List `.runesmith/` subdirectories whose name starts with `{date}-{sanitized-branch}` (using the sanitized branch name from Step 3).
   - If no match exists, use the candidate path as-is.
   - If a match exists, append a numeric counter suffix: `-1`, `-2`, etc. Increment until finding an unused path.
6. Create the session directory and seven subdirectories:
   - `.runesmith/{date}-{sanitized-branch}[/-N]/specs/`
   - `.runesmith/{date}-{sanitized-branch}[/-N]/reports/`
   - `.runesmith/{date}-{sanitized-branch}[/-N]/logs/`
   - `.runesmith/{date}-{sanitized-branch}[/-N]/cache/`
   - `.runesmith/{date}-{sanitized-branch}[/-N]/pipeline/`
   - `.runesmith/{date}-{sanitized-branch}[/-N]/stages/`
   - `.runesmith/{date}-{sanitized-branch}[/-N]/prs/`
7. Canonicalize the session path with `Path(path).resolve()` before writing to `.opencode/.runesmith-active`.
8. Return the session path, list of created subdirectories, and success status.
9. Handle `mkdir` failure by returning an error message with the failed path.

**Output examples:**

On success:

```
Session created: .runesmith/2026-07-11-feat_my-feature/
Subdirectories: specs/, reports/, logs/, cache/, pipeline/, stages/, prs/
Active session pointer set.
```

On collision:

```
Session created: .runesmith/2026-07-11-feat_my-feature-1/
Collision detected, counter-based disambiguation applied.
Subdirectories: specs/, reports/, logs/, cache/, pipeline/, stages/, prs/
Active session pointer set.
```

On `mkdir` failure:

```
Error: Failed to create session directory .runesmith/2026-07-11-feat_my-feature/
```

### clear — Destroy the active session scratchpad

1. Read `.opencode/.runesmith-active` to get the active session path.
2. If the file is absent or empty, return an error indicating no active session.
3. Validate the session path by resolving it with `Path.resolve()`:
   - Resolve the session path with `Path(path).resolve()` and verify its resolved parent directory is under the real `.runesmith/` directory (also resolved).
   - Check for symlinks: `Path.resolve()` unwraps symlinks, so the resolved path must stay within the real project root's `.runesmith/`.
   - If validation fails, return a security error: `"Error: Security validation failed — session path is outside .runesmith/ directory."`
4. Report the file count within the session directory (recursive count of all files).
5. Validate that the session directory exists on disk:
   - If the directory does not exist, output: `"Error: Session directory {path} does not exist (stale pointer)."`
6. Require explicit user confirmation before proceeding:
   - If confirmation is declined, abort with an informational message and leave the session intact:
     ```
     Aborted. Session {path} was NOT removed.
     Active session pointer NOT cleared.
     ```
   - If confirmation is accepted, proceed to deletion.
7. Remove the session directory and all its contents (if it exists):
   - Resolve symlinks with `Path.resolve()` before removal to prevent symlink-race TOCTOU attacks.
   - For extra safety, only delete known subdirectory names (`specs/`, `reports/`, `logs/`, `cache/`, `pipeline/`, `stages/`, `prs/`) and their contents within the session path, rather than removing the entire tree root.
8. Clear the `.opencode/.runesmith-active` pointer file (delete or truncate).
9. Return a success message with the removed session path and file count.

**Output examples:**

On success with confirmation:

```
Session removed: .runesmith/2026-07-11-feat_my-feature/
Files removed: 12
Active session pointer cleared.
```

On stale pointer clear with confirmation:

```
Error: Session directory .runesmith/2026-07-11-deleted-session/ does not exist (stale pointer).
Stale pointer cleared from .opencode/.runesmith-active.
```

On confirmation declined:

```
Aborted. Session .runesmith/2026-07-11-feat_my-feature/ was NOT removed.
Active session pointer NOT cleared.
```

### status — Report on the active session

1. Read `.opencode/.runesmith-active` to get the active session path.
2. If the file is absent or empty, return a message indicating no active session and suggest using `init`.
3. If the session directory exists:
   - Report the session path.
   - For each subdirectory (`specs/`, `reports/`, `logs/`, `cache/`, `pipeline/`, `stages/`, `prs/`), count files and report the count.
   - Report total file count and total session size in human-readable format (KB/MB).
4. If the session directory does not exist, report the stale pointer with the path and suggest running `clear`.

**Output examples:**

With active session:

```
Active session: .runesmith/2026-07-11-feat_my-feature/
  specs:    3 files
  reports:  1 file
  logs:     5 files
  cache:    2 files
  pipeline: 0 files
  stages:   0 files
  prs:      0 files
Total: 11 files, 1.2 MB
```

With no active session:

```
No active session. Use `rs-scratchpad init` to create one.
```

With stale pointer:

```
Stale pointer: .opencode/.runesmith-active points to .runesmith/2026-07-11-deleted-session/ which does not exist.
Run `rs-scratchpad clear` to clean up the pointer.
```

## Required Permissions

The agent needs filesystem read/write on `.runesmith/` and `.opencode/.runesmith-active`, plus `git rev-parse` and basic filesystem commands.

## See Also

- `rs-discover` — codebase scanner for project context

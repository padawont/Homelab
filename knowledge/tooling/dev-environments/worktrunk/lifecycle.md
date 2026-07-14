---
title: "Worktrunk Worktree Lifecycle"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags: ["worktrunk", "lifecycle", "workflow"]
sources:
  - url: "https://worktrunk.dev"
    title: "Worktrunk — Git Worktree Manager for AI Agents"
  - url: "https://github.com/max-sixty/worktrunk"
    title: "max-sixty/worktrunk — GitHub Repository"
last_audit_date: 2026-06-07
---

# Worktrunk Worktree Lifecycle

This document walks through the end-to-end Worktrunk lifecycle, from initialization through cleanup. Each stage shows the commands, expected outcomes, and hook integration points.

---

## 1. Initialize

Worktrunk configuration can live at the user level or inside a project.

**User-level config (global defaults):**

```bash
wt config create
```

Creates `~/.config/worktrunk/config.toml`. The default `worktree-path` template places worktrees as siblings of the repository: `{{ repo_path }}/../{{ repo }}.{{ branch | sanitize }}`. The default branch is auto-detected from the remote (typically `main` or `master`); the default remote is `origin`.

**Project-level config (per-repo overrides):**

```bash
wt config create --project
```

Creates `.config/wt.toml` inside the current repository. This file is intended to be committed to version control. Project config takes precedence over user config. Typical project config:

```toml
# .config/wt.toml
worktree-path = ".worktrees/{{ branch | sanitize }}"

[pre-start]
deps = "npm ci"

[pre-merge]
test = "npm test"
```

**Branching convention:** Branches are addressed by name (e.g., `feat-42`, `fix/login-error`). Worktree paths are computed from a configurable template — by default `{worktrees_dir}/{branch}` or `~/worktrees/{branch}`. This means two branches with the same name cannot coexist (enforced by the filesystem).

---

## 2. Create Worktree

```bash
wt switch --create <branch>
```

When you run this command, Worktrunk performs the following steps in sequence:

1. **Run pre-switch hooks** (if defined) — blocking hook that runs before branch resolution. The `{{ branch }}` variable is the destination as typed.
2. **Create** a git branch `<branch>` from the default branch (or `--base` if specified).
3. **Create** a git worktree at the configured path (e.g., `.worktrees/<branch>` or `~/worktrees/<branch>`).
4. **Switch** to the new worktree directory.
5. **Run pre-start hooks** (if defined) — blocking, runs after worktree is ready. Ideal for dependency installation and env file generation.
6. **Spawn post-start and post-switch hooks** (if defined) — run in the background. Post-start handles dev servers, long builds, file watchers. Post-switch triggers on all switch results.

For the full `wt switch` command reference, see [cli-reference.md](./cli-reference.md).

Example:

```bash
wt switch --create feat-42
# Creates branch feat-42 from main
# Creates worktree at .worktrees/feat-42
# Runs hooks
```

### Hook Integration at Creation

The hook names in the table below are the actual TOML keys defined in `.config/wt.toml` (project) or `~/.config/worktrunk/config.toml` (user). See [hooks.md](./hooks.md) for the full hook configuration reference, including all three hook forms (string, table, pipeline).

| Hook Point | Typical Use | Example |
|------------|-------------|---------|
| `pre-switch` | Validate before branch resolution | Check prerequisites or environment readiness |
| `post-switch` | Trigger on all switch results | Update environment, notify tooling |
| `pre-start` | Install dependencies for the new worktree | `npm install` or `pip install -r requirements.txt` |
| `post-start` | Start dev server, set up env files | `cp .env.example .env && docker compose up -d` |

Hooks are shell commands defined in TOML configuration. Template variables like `{{ branch }}` and `{{ worktree_path }}` are expanded at runtime via the [minijinja](https://docs.rs/minijinja/) template engine. All template variables are also passed as JSON on stdin, enabling complex scripting logic. See [hooks.md](./hooks.md) for the full reference.

---

## 3. Work

Inside the worktree, you work as you would in any normal git checkout. The worktree is a fully isolated directory with its own:

- Working tree and index
- Staged and unstaged changes
- Untracked files
- Git state (detached HEAD or active branch)

You can use any editor, IDE, or AI agent inside the worktree without affecting other worktrees or the main repository.

---

## 4. Check Status

```bash
wt list
```

Displays a table of all active worktrees managed by Worktrunk:

```
 Branch        Status     HEAD±      main↕   Remote⇅  Commit    Age   Message
 feat-42       +   ↑     +54   -5   ↑4  ↓1   ⇡3      6814f02a  2h    Add login validation
 fix/login     !   |              ↑2  ↓1     |      b772e68b  30m   Fix login error
 chore/readme  _   ⇡                         ⇡1      41ee0834  1d    Merge feat-42: add login…
```

Each row shows:
- **Branch** — the branch name
- **Status** — compact symbols for working tree state (staged `+`, modified `!`, untracked `?`), relation to default branch (`^` is default, `↑` ahead, `_` same commit), and remote status (`⇡` ahead, `|` in sync)
- **HEAD±** — lines added/deleted in uncommitted changes
- **main↕** — commits ahead/behind the default branch
- **Remote⇅** — commits ahead/behind the tracking branch
- **Commit** — short commit hash (8 chars)
- **Age** — time since last commit
- **Message** — last commit message (truncated)
- **Path** — filesystem path to the worktree (shown when worktrees use different base paths)
- **CI** — CI status if the branch has a PR/MR and `--full` is used (passing, failing, running, unknown)
- **URL** — dev server URL if configured via `[list] url` in config (dimmed when port not listening)

Use `wt list --json` for machine-readable output (useful for scripts and agent tooling).

---

## 5. Commit

Within the worktree, commit changes using standard git or the Worktrunk step command:

```bash
# Standard git (works exactly as expected)
git add .
git commit -m "feat: add login validation"

# Worktrunk shorthand
wt step commit
```

`wt step commit` stages changes and generates a commit message using an LLM (requires `[commit.generation]` configured in user config). By default it stages all changes including untracked files (`--stage all`). Use `--stage tracked` for only modified tracked files, or `--stage none` to commit only what's already staged. It preserves all standard git hooks (pre-commit, commit-msg, etc.). See [cli-reference.md](./cli-reference.md) for full options.

Commits are local to the worktree and do not affect other worktrees.

---

## 6a. PR Workflow (Remote Collaboration)

The standard PR workflow uses a remote hosting service:

```bash
# Push the branch
git push -u origin feat-42

# Create a pull request
gh pr create --title "feat: add login validation" --body "Closes #42"

# After PR is reviewed and merged (via GitHub/GitLab UI or CLI):
gh pr merge --squash feat-42

# Remove the local worktree and branch
wt remove
```

`wt remove` performs safety checks before deleting:
- Verifies the worktree has no uncommitted changes
- Confirms the branch has been merged (or use `--force-delete` / `-D` to force-delete an unmerged branch)
- Removes the git worktree and deletes the branch

---

## 6b. Local Merge (Direct Integration)

For branches that do not need a PR review, use the local merge command:

```bash
wt merge main
```

This single command orchestrates the full merge lifecycle via an 8-step pipeline:

1. **Commit** — Pre-commit hooks run, then uncommitted changes are committed. Post-commit hooks run in background. **Skipped when squashing (the default)** — changes are staged during the squash step instead.
2. **Squash** — Combines all commits since target into one (like GitHub's "Squash and merge"). A backup ref is saved to `refs/wt-backup/<branch>`. With `--no-squash`, individual commits are preserved.
3. **Rebase** — Rebases onto target if behind. Conflicts abort immediately. Skipped with `--no-rebase` (fails if the branch is not already rebased onto the target).
4. **Pre-merge hooks** — Run after rebase, before merge. Failures abort.
5. **Merge** — Fast-forward merge to the target branch. With `--no-ff`, a merge commit is created.
6. **Pre-remove hooks** — Run before removing worktree.
7. **Cleanup** — Removes the worktree and branch (unless `--no-remove`).
8. **Post-remove + post-merge hooks** — Run in background after cleanup.

Squash, rebase, and fast-forward are **default steps**; they can be disabled via `--no-squash`, `--no-rebase`, and `--no-ff` respectively.

```bash
# Default: squash + rebase + fast-forward
wt merge main

# Preserve individual commits (skip squash)
wt merge main --no-squash

# Create a merge commit (semi-linear history)
wt merge main --no-ff
```

### Local Merge Hook Integration

| Hook Point | Lifecycle Step | Typical Use | Example |
|------------|----------------|-------------|---------|
| `pre-commit` | Step 1 | Formatters, linters | `npm run lint` |
| `post-commit` | Step 1 (background) | Notifications | `notify-ci` |
| `pre-merge` | Step 4 | Tests, validation | `pytest && cargo test` |
| `pre-remove` | Step 6 | Cleanup before deletion | `save test artifacts` |
| `post-remove` | Step 8 (background) | Stop dev servers | `docker stop my-container` |
| `post-merge` | Step 8 (background) | Deploy, notify | `deploy-to-staging` |

For the full hook lifecycle and available template variables, see [hooks.md](./hooks.md). For all `wt merge` flags and options, see [cli-reference.md](./cli-reference.md).

---

## 7. Cleanup

```bash
wt remove
```

Removes the current worktree and its branch. Equivalent to:

```bash
# Delete the git worktree
git worktree remove .worktrees/<branch>

# Delete the branch (if merged)
git branch -d <branch>
```

**Safety guarantees:**
- Refuses to remove if the worktree has uncommitted changes (use `git stash` first).
- Refuses to remove if the worktree is dirty (use `--force` / `-f` to override).
- Refuses to delete the branch if unmerged (use `--force-delete` / `-D` to override).
- Confirms before destructive operations.

**Remove a specific worktree by branch:**

```bash
wt remove feat-42
```

**Remove all stale worktrees (cleanup after bulk merges):**

```bash
wt list --json | jq -r '.[].branch' | xargs -I{} wt remove {}
```

### Hook Integration at Removal

When `wt remove` runs, it automatically executes hooks before and after deletion:

| Hook Point | Type | Typical Use | Example |
|------------|------|-------------|---------|
| `pre-remove` | Blocking | Save artifacts, back up state before worktree deletion | `tar czf artifacts-{{ branch }}.tar.gz ./build/` |
| `post-remove` | Background | Stop dev servers, remove containers, notify external systems | `docker stop my-container 2>/dev/null \|\| true` |

- **`pre-remove`** runs in the worktree being removed and blocks deletion until it completes. Template variables reference the worktree that is about to be deleted.
- **`post-remove`** runs in the background after the worktree is removed. The hook runs in the target/primary worktree; template variables still reference the removed worktree for cleanup purposes.

---

## Parallel Agent Workflow

Worktrunk is designed for running multiple AI agents concurrently, each in its own isolated worktree.

### Setup

```bash
# Create three worktrees for three agents
wt switch --create agent-1/task-a
wt switch --create agent-2/task-b
wt switch --create agent-3/task-c
```

### Launch Agents with `-x` Flag

Worktrunk's `wt switch --create` command provides the `-x` (short for `--execute`) flag to run a command after switching into the newly created worktree. This is the primary mechanism for launching OpenCode agents:

```bash
# Create a worktree and launch OpenCode with a task prompt
wt switch --create feat-42 -x opencode -- "implement login validation"

# Launch agent-2 in its own worktree
wt switch --create task-b -x opencode -- "add database migration"

# Launch agent-3 alongside the others
wt switch --create task-c -x opencode -- "write API tests"
```

The `-x` flag is a `wt switch` option, not an OpenCode flag. It executes any command (not just OpenCode) after switching into the worktree, replacing the `wt` process. See [cli-reference.md](./cli-reference.md) for the full `wt switch --execute` documentation.

Each agent operates independently:
- File changes are isolated per worktree.
- Git operations (commit, push) do not conflict.
- Hooks run independently in each worktree.
- `wt list` shows all agents' progress at a glance.

### Parallel Merge Strategy

When all agents finish, merge branches in dependency order:

```bash
# Merge independent branches in any order (squash + rebase + ff is default)
wt merge task-b
wt merge task-c

# Merge dependent branch after its base lands
wt merge agent-1/task-a
```

---

## Troubleshooting

### Stale Worktree Markers

**Symptom:** `wt list` shows a worktree but the directory was deleted manually.

**Cause:** Deleting a worktree directory with `rm -rf` instead of `wt remove` or `git worktree remove`.

**Fix:** Prune stale git worktree references:

```bash
git worktree prune
# Worktrunk automatically detects pruned worktrees on next `wt list`
```

For more on git worktree cleanup, see [Git Worktree Troubleshooting](../../version-control/git/worktree/troubleshooting.md).

To remove the stale entry from Worktrunk's tracking:

```bash
wt remove <branch> --force-delete   # --force for dirty worktree, -D for unmerged branch
```

### Failed Hooks

**Symptom:** `wt switch --create <branch>` hangs or fails with a hook error.

**Cause:** A `pre-start` or `post-start` hook exited with a non-zero code. Worktrunk propagates hook failures and aborts the operation.

**Fix:**

1. Run the hook manually to test it in isolation:
   ```bash
   wt hook pre-start
   wt hook post-start
   ```
2. Pass the `-v` flag for verbose output showing resolved template variables:
   ```bash
   wt hook pre-start -v
   ```
3. Common hook failures:
   - Missing dependencies (run the install command manually in the worktree).
   - Template syntax errors (check `{{ }}` variable names against [hooks.md](./hooks.md) reference).
4. Check `.git/wt/logs/` for background hook output (post-* hooks write logs there):
   ```bash
   wt config state logs
   ```
5. Skip hooks temporarily: `wt switch --create <branch> --no-hooks`.
6. Re-run `wt switch --create <branch>` after fixing.

### Merge Conflicts

**Symptom:** `wt merge main` fails with conflict markers.

**Cause:** The branch has changes that conflict with the target branch.

**Resolution steps:**

```bash
# The merge aborts, leaving the worktree intact

# 1. Enter the worktree
cd .worktrees/<branch>

# 2. Resolve conflicts manually or with a tool
git mergetool

# 3. Stage resolved files
git add .

# 4. Complete the operation:
#    - If the conflict was during rebase (step 3):  git rebase --continue
#    - If the conflict was during merge (step 5, --no-ff only):  git merge --continue
#    The wt merge output will indicate which step failed.

# 5. Clean up manually (since wt merge aborted)
wt remove <branch> --force-delete   # -D for unmerged branch; add -f if worktree is also dirty
# Then push the merge commit from main
```

### Lost Worktree Path

**Symptom:** You are in a terminal and do not know which worktree you are in.

**Fix:**

```bash
# Show current worktree info (wt list filtered to current)
wt list --format=json | jq '.[] | select(.is_current)'

# Or use git directly
git worktree list

# The shell prompt may also show the branch name
# (wt config shell install adds this to your prompt)
```

### Branch Already Exists

**Symptom:** `wt switch --create feat-42` fails because the branch already exists.

**Cause:** A previous worktree was removed but the branch was not deleted.

**Fix:**

```bash
# Delete the existing branch (if safe)
git branch -D feat-42

# Or switch to the existing branch's worktree
wt switch feat-42
```

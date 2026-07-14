---
title: "Git Worktree"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags:
  - git
  - worktree
  - version-control
  - developer-experience
sources:
  - "https://git-scm.com/docs/git-worktree"
last_audit_date: 2026-06-07
---

# Git Worktree

Git worktree is a built-in Git feature that allows you to check out multiple branches of the same repository simultaneously, each in its own working directory, all sharing a single `.git` directory. Each concurrent checkout is called a **linked worktree** (as opposed to the **main worktree** created by `git init` or `git clone`). A repository has exactly one main worktree (unless it is bare) and zero or more linked worktrees.

The core value proposition is that you can context-switch between branches without stashing, committing WIP, or cloning the repository multiple times. Each worktree has its own working directory, index, HEAD, and per-worktree refs, while the object store and shared refs remain common.

## How It Works

### Shared `.git` Directory

All worktrees share the same object database, refs (except per-worktree refs), and most Git configuration. This means:

- **Objects** -- Commits, trees, blobs, and tags are stored once in the shared object store. A commit made in one worktree is immediately visible to all others.
- **Refs** -- Most refs under `refs/heads/`, `refs/tags/`, and `refs/remotes/` are shared. If you push or fetch in one worktree, the updated remote-tracking refs are available everywhere.
- **Configuration** -- By default, `$GIT_DIR/config` is shared. Worktree-specific configuration can be enabled with the `extensions.worktreeConfig` setting.

Each worktree maintains private copies of:

- **HEAD** -- which branch or commit the worktree has checked out.
- **Index (staging area)** -- uncommitted changes are isolated per worktree.
- **Per-worktree refs** -- refs under `refs/bisect/`, `refs/worktree/`, and `refs/rewritten/` are not shared. `HEAD` and other pseudo-refs directly under `$GIT_DIR` are also per-worktree.
- **Configuration (optional)** -- if `extensions.worktreeConfig` is enabled, a `config.worktree` file in the worktree's private directory is read after the shared config.

### The `.git/worktrees/` Internal Directory Structure

When a linked worktree is created, Git writes administrative metadata into a private subdirectory under the repository's `.git/worktrees/` directory. The subdirectory is named after the base name of the linked worktree's path (appended with a number if the name is taken).

For example, after running:

```bash
git worktree add /path/other/test-next next
```

on a repository whose `.git` is at `/path/main/.git`, the following structure exists:

```
/path/main/.git/
  ├── objects/            # shared object store
  ├── refs/               # shared refs (heads, tags, remotes)
  ├── HEAD                # main worktree HEAD
  ├── index               # main worktree index
  ├── config              # shared configuration
  └── worktrees/
      └── test-next/      # linked worktree admin directory
          ├── HEAD        # linked worktree HEAD
          ├── index       # linked worktree index
          ├── gitdir      # absolute path to the linked worktree directory
          ├── commondir   # relative path back to the main .git
          └── locked      # present only if the worktree is locked (contains reason text)
```

Inside the linked worktree itself (`/path/other/test-next/`), a plain `.git` file (not a directory) points to the administrative directory:

```
/path/other/test-next/.git
  gitdir: /path/main/.git/worktrees/test-next
```

Environment variable resolution:

- `$GIT_DIR` points to the worktree's private admin directory (e.g. `/path/main/.git/worktrees/test-next`).
- `$GIT_COMMON_DIR` points back to the main `.git` directory (e.g. `/path/main/.git`).

Running `git rev-parse --git-path HEAD` resolves to the per-worktree `HEAD` inside the admin directory, while `git rev-parse --git-path refs/heads/master` resolves to the shared path under `$GIT_COMMON_DIR`.

## Linked Worktree vs Detached HEAD

### Linked (Attached) Worktree

A linked worktree has a specific branch checked out. The branch name appears in `git worktree list` output in square brackets (e.g. `[master]`). A branch can only be checked out in one worktree at a time -- attempting to check it out in a second worktree will fail unless `--force` is used.

### Detached HEAD Worktree

A worktree with a detached HEAD is not associated with any branch. It points directly to a commit. This is useful for:

- One-off experiments that do not need a named branch.
- Reviewing a specific commit or tag without affecting branch state.
- Running long-lived tests on a fixed revision.

Create a detached HEAD worktree with `--detach` (or `-d`):

```bash
git worktree add --detach ../review v2.3.0
```

## Primary Use Cases

### Parallel Feature Work

Work on multiple feature branches at the same time without switching context. Each feature branch lives in its own directory with its own editor window or IDE project.

```bash
git worktree add ../feature-auth feature/auth
git worktree add ../feature-api feature/api
```

Open each directory in a separate terminal/editor session and work independently.

### Hotfix Isolation

When a production bug surfaces in the middle of feature work, create a temporary worktree from the stable branch, apply the fix, and remove the worktree -- without disturbing the in-progress work.

```bash
git worktree add -b hotfix-fix ../hotfix main
cd ../hotfix
# fix, commit, push
cd ..
git worktree remove ../hotfix
```

### PR Review Sandboxes

Check out a collaborator's branch into a dedicated directory for review, testing, and experimentation, without affecting your own branches.

```bash
git worktree add ../pr-review origin/feature/new-ui
```

### AI Agent Sessions (Parallel Coding Agents)

Dedicate one worktree per AI coding agent (Claude Code, GitHub Copilot, OpenCode, etc.) to prevent agents from interfering with each other or with manual developer work. Each agent gets an isolated working directory, index, and HEAD, independent tooling configuration, and no risk of overwriting changes — enabling true parallel execution with simultaneous commits.

```bash
git worktree add ../agent-claude feature/task-a
git worktree add ../agent-copilot feature/task-b
```

Full workflow patterns are covered in [workflows.md](./workflows.md).

For a purpose-built tool that wraps git worktree for AI agent workflows, see [Worktrunk](../../dev-environments/worktrunk/overview.md).

### Long-Running Experiments

Keep a long-lived experiment on a detached HEAD or an orphan branch in its own directory, periodically syncing from upstream, while the main worktree continues on active development.

```bash
git worktree add --detach ../experiment
```

### Multiple IDE Instances

Some editors bind to the project root and do not handle branch switches gracefully. Worktrees let you open separate editor instances on different branches, each with its own state.

## Subcommands Overview

### `git worktree add <path> [<commit-ish>]`

Create a new linked worktree at `<path>`. If `<commit-ish>` is a branch name, it is checked out. If omitted, a new branch is created named after the basename of `<path>`. Key flags:

| Flag | Description |
|---|---|
| `-b <branch>` | Create and check out a new branch |
| `-B <branch>` | Create or reset branch, then check out |
| `-d`, `--detach` | Check out with detached HEAD |
| `--lock` | Lock the worktree immediately after creation |
| `--no-checkout` | Create the worktree without populating files |
| `--orphan` | Create an empty worktree with an unborn branch |
| `--guess-remote` | Base new branch on matching remote-tracking branch |
| `-f`, `--force` | Override safety checks (e.g. branch already checked out) |

### `git worktree list`

List all worktrees (main + linked). Default output shows one line per worktree with path, commit hash, and branch name (or "detached HEAD"). Flags:

| Flag | Description |
|---|---|
| `-v`, `--verbose` | Show additional detail; moves annotation to next line when reason is available |
| `--porcelain` | Machine-parseable output (one attribute per line) |
| `-z` | NUL-delimited lines (used with `--porcelain`) |
| `--expire <time>` | Annotate missing worktrees older than `<time>` as prunable |

### `git worktree remove <worktree>`

Remove a linked worktree. The worktree must be clean (no tracked modifications, no untracked files). Flags:

| Flag | Description |
|---|---|
| `-f`, `--force` | Remove even if unclean; use twice to remove locked worktrees |

The main worktree cannot be removed.

### `git worktree prune`

Clean up stale administrative entries in `.git/worktrees/` for worktrees whose working directories no longer exist. Useful after manually deleting a worktree directory. Flags:

| Flag | Description |
|---|---|
| `-n`, `--dry-run` | Report what would be removed without deleting |
| `-v`, `--verbose` | Report all removals |
| `--expire <time>` | Only prune entries older than `<time>` |

### `git worktree lock <worktree>`

Prevent a worktree's administrative files from being pruned. Use when the worktree directory resides on removable media or a network share that may not always be mounted.

| Flag | Description |
|---|---|
| `--reason <string>` | Plain-text explanation stored in the `locked` file |

### `git worktree unlock <worktree>`

Remove the lock from a worktree, allowing it to be pruned, moved, or deleted.

### `git worktree move <worktree> <new-path>`

Move a worktree to a new filesystem location and update the administrative metadata. The main worktree and worktrees containing submodules cannot be moved with this command.

### `git worktree repair [<path>...]`

Repair corrupted or outdated worktree administrative files. This automatically reestablishes the connection between the main repository and linked worktrees when either has been moved manually.

## Worktree Identification

Worktrees can be identified by:

- **Full or relative path** -- e.g. `../hotfix`, `/abs/path/to/worktree`
- **Unique basename** -- if the last path component is unique among all worktrees, it suffices. For example, `ghi` uniquely identifies worktrees with path ending in `/ghi`.

## Accessing Refs Across Worktrees

Per-worktree refs from one worktree can be accessed from another using special pseudo-ref paths:

- `main-worktree/HEAD` resolves to the main worktree's HEAD.
- `worktrees/<name>/HEAD` resolves to a linked worktree's HEAD.
- `worktrees/<name>/refs/bisect/good` accesses bisect refs from a specific worktree.

Use `git rev-parse` or `git update-ref` rather than reading files directly.

## Configuration

| Setting | Default | Description |
|---|---|---|
| `worktree.guessRemote` | `false` | When `true`, `git worktree add <path>` without a branch tries to match basename to a remote-tracking branch |
| `worktree.useRelativePaths` | `false` | When `true`, use relative links in worktree administrative files (implies `extensions.relativeWorktrees`) |
| `extensions.worktreeConfig` | (not set) | When `true`, enables per-worktree config files at `.git/worktrees/<id>/config.worktree` |
| `gc.worktreePruneExpire` | `"3.months.ago"` | Age threshold for automatic worktree pruning during `git gc` |

## Limitations and Caveats

- **Submodule support is incomplete.** It is not recommended to make multiple checkouts of a superproject with submodules. Moving worktrees that contain submodules is not supported.
- **Branch exclusivity.** A branch can be checked out in only one worktree at a time (unless `--force` is used, which bypasses the safety check).
- **Manual directory deletion.** If a linked worktree directory is deleted manually (without `git worktree remove`), the stale admin entry remains in `.git/worktrees/` and must be cleaned up with `git worktree prune`.
- **Manual moves.** If a worktree is moved without `git worktree move`, the `gitdir` file in the admin directory must be updated. Run `git worktree repair` to reestablish the connection automatically.
- **Filesystem requirements.** Worktrees must reside on the same filesystem as the main repository when relative paths are used.
- **Disk space.** Each worktree is a full working copy (all tracked files checked out). In large repositories or monorepos, multiple worktrees can consume significant disk space. Mitigate with `git worktree remove` for completed worktrees, sparse checkout (`--no-checkout` with `git sparse-checkout`), and periodic `git worktree prune`.

## Detailed Guides

| File | Description |
|---|---|
| [cli-reference.md](./cli-reference.md) | All `git worktree` subcommands with flags and examples |
| [branching.md](./branching.md) | Worktree-to-branch mapping, attached/detached HEAD, orphan branches |
| [installation.md](./installation.md) | Requirements, platform support, and verification |
| [troubleshooting.md](./troubleshooting.md) | Common issues and solutions |
| [workflows.md](./workflows.md) | End-to-end workflow patterns |

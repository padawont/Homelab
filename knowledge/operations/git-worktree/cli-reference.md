---
title: "Git Worktree CLI Reference"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags: ["git", "worktree", "cli", "reference"]
sources:
  - "https://git-scm.com/docs/git-worktree"
  - "https://git-scm.com/docs/git-worktree/2.54.0"
last_audit_date: 2026-06-07
---

# CLI Reference

## Quick Reference

| Command | Description |
|---|---|
| `git worktree add <path> [<commit-ish>]` | Create a new linked worktree and check out a branch or commit |
| `git worktree list` | List all worktrees (main + linked) |
| `git worktree lock <worktree>` | Lock a worktree to prevent pruning, moving, or deletion |
| `git worktree unlock <worktree>` | Unlock a worktree |
| `git worktree move <worktree> <new-path>` | Move a worktree to a new location |
| `git worktree remove <worktree>` | Remove a linked worktree |
| `git worktree prune` | Remove stale administrative files for missing worktrees |
| `git worktree repair [<path>...]` | Repair corrupted or outdated worktree administrative files |

---

## git worktree add

Create a new linked worktree at the given path and check out a branch or commit into it. The new worktree shares all objects and refs with the parent repository except per-worktree files (`HEAD`, `index`, etc.).

### Syntax

```
git worktree add [-f] [--detach] [--checkout] [--lock [--reason <string>]]
                 [--orphan] [(-b | -B) <new-branch>] <path> [<commit-ish>]
```

### Key Flags

| Flag | Description |
|---|---|
| `<path>` | **(Required)** Filesystem path where the new worktree is created |
| `<commit-ish>` | Branch, tag, or commit to check out. If omitted, defaults to `HEAD`. A bare `-` is synonymous with `@{-1}` |
| `-b <new-branch>` | Create a new branch named `<new-branch>` starting at `<commit-ish>` (defaults to `HEAD`). Refuses if the branch already exists |
| `-B <new-branch>` | Same as `-b`, but resets `<new-branch>` to `<commit-ish>` if it already exists |
| `-d` / `--detach` | Check out with a detached `HEAD` instead of a branch |
| `--orphan` | Create an empty worktree and index, associating it with a new unborn branch named `<new-branch>` |
| `--lock` | Lock the worktree immediately after creation. Equivalent to `git worktree lock` but without a race condition |
| `--reason <string>` | Explanation for the lock (only meaningful with `--lock`) |
| `--checkout` / `--no-checkout` | Enable or disable checkout of `<commit-ish>` into the new worktree. `--no-checkout` is useful for sparse-checkout setups |
| `--guess-remote` / `--no-guess-remote` | When no `<commit-ish>` is given, try to find a unique remote-tracking branch matching the basename of `<path>` and base the new branch on it |
| `--track` / `--no-track` | Set or unset upstream tracking when creating a new branch. Defaults to on when `<commit-ish>` is a remote-tracking branch |
| `--relative-paths` / `--no-relative-paths` | Link worktrees using relative or absolute paths. Overrides `worktree.useRelativePaths` config option. Absolute paths are the default |
| `--force` / `-f` | Override safety checks: allow creating a worktree from a branch already checked out elsewhere, or from a missing but locked path. Use `-f` twice to add a missing locked worktree path |
| `--quiet` / `-q` | Suppress feedback messages |

### Automatic Branch Naming

If `<commit-ish>` is omitted and neither `-b`, `-B`, nor `--detach` is given, git creates a new branch named after the basename of `<path>`. If a branch with that name already exists, it is checked out directly (provided it is not checked out elsewhere). If no local branches exist (and no remote branches when `--guess-remote` is supplied), the command creates an unborn branch as if `--orphan` was passed. However, if the repository has a remote and `--guess-remote` is used, but no remote or local branches exist, the command fails with a reminder to fetch first (or override with `-f`/`--force`).

### Examples

Create a new worktree from `HEAD` with an automatically named branch:
```bash
git worktree add ../hotfix
```

Create a new worktree checking out an existing branch:
```bash
git worktree add ../release-v2 origin/release-v2
```

Create a worktree with a new branch from a specific commit:
```bash
git worktree add -b experiment ../experiment abc1234
```

Create a worktree with a detached HEAD at `HEAD~3`:
```bash
git worktree add --detach ../debug HEAD~3
```

Create a worktree without checking out files (for sparse checkout):
```bash
git worktree add --no-checkout ../sparse-feature feature-x
```

Create a worktree with an unnamed unborn branch (named after path basename):
```bash
git worktree add --orphan ../gh-pages
```

Create a worktree with a specifically named unborn branch:
```bash
git worktree add --orphan -b gh-pages ../docs
```

Create a worktree and lock it immediately with a reason:
```bash
git worktree add --lock --reason "on usb drive" ../portable-work
```

Force-create a worktree from a branch already checked out elsewhere:
```bash
git worktree add -f ../other-fix feature-x
```

---

## git worktree list

List all worktrees associated with the current repository. The main worktree is listed first, followed by each linked worktree.

### Syntax

```
git worktree list [-v | --porcelain [-z]] [--expire <time>]
```

### Key Flags

| Flag | Description |
|---|---|
| `-v` / `--verbose` | Show additional information: lock and prune reasons on a separate indented line |
| `--porcelain` | Machine-parseable output with one attribute per line. Stable across Git versions |
| `-z` | Terminate lines with NUL instead of newline when combined with `--porcelain`. Useful when worktree paths contain newlines |
| `--expire <time>` | Annotate missing worktrees as prunable if they are older than the specified time |

### Default Output

```
$ git worktree list
/path/to/main-worktree            abc1234 [main]
/path/to/linked-worktree          def5678 [feature-x]
/path/to/detached-worktree        1234abc  (detached HEAD)
/path/to/locked-worktree          abcd5678 (branch-a) locked
/path/to/prunable-worktree        5678abc1 (detached HEAD) prunable
```

Annotations: `locked`, `prunable`, `bare`.

### Verbose Output

```
$ git worktree list --verbose
/path/to/linked-worktree               abc1234 [main]
/path/to/locked-worktree-with-reason   1234abcd (branch-a)
        locked: worktree path is mounted on a portable device
/path/to/prunable-worktree             5678abc1 (detached HEAD)
        prunable: gitdir file points to non-existent location
```

When a reason is available, the annotation moves to the next line indented.

### Porcelain Output

```
$ git worktree list --porcelain
worktree /path/to/main-worktree
HEAD abc1234abcd1234abcd1234abcd1234abcd1234
branch refs/heads/main

worktree /path/to/linked-worktree
HEAD def5678def5678def5678def5678def5678def5
branch refs/heads/feature-x

worktree /path/to/detached-worktree
HEAD 1234abc1234abc1234abc1234abc1234abc1234a
detached

worktree /path/to/locked-worktree
HEAD 5678abc5678abc5678abc5678abc5678abc5678c
branch refs/heads/locked-no-reason
locked

worktree /path/to/locked-with-reason
HEAD 3456def3456def3456def3456def3456def3456b
branch refs/heads/locked-with-reason
locked reason why is locked

worktree /path/to/prunable
HEAD 1233def1234def1234def1234def1234def1234b
detached
prunable gitdir file points to non-existent location
```

Boolean attributes (`bare`, `detached`) appear only when `true`. An empty line marks the end of each record. With `-z`, all lines including the blank separator are NUL-terminated.

---

## git worktree lock

Lock a worktree to prevent its administrative files from being pruned, and to prevent the worktree from being moved or removed. This is useful when the worktree resides on a portable device or network share that is not always mounted.

### Syntax

```
git worktree lock [--reason <string>] <worktree>
```

### Key Flags

| Flag | Description |
|---|---|
| `<worktree>` | **(Required)** Path or unique suffix identifying the worktree to lock |
| `--reason <string>` | Plain-text explanation for why the worktree is locked. Stored in the `locked` file under the worktree's administrative directory |

### Examples

Lock a worktree by path:
```bash
git worktree lock ../portable-work
```

Lock a worktree by unique path suffix:
```bash
git worktree lock portable-work
```

Lock with an explanation:
```bash
git worktree lock --reason "external SSD not always connected" ../external-work
```

---

## git worktree unlock

Unlock a worktree, allowing it to be pruned, moved, or deleted.

### Syntax

```
git worktree unlock <worktree>
```

### Key Flags

| Flag | Description |
|---|---|
| `<worktree>` | **(Required)** Path or unique suffix identifying the worktree to unlock |

### Examples

Unlock a worktree by path:
```bash
git worktree unlock ../portable-work
```

Unlock by unique suffix:
```bash
git worktree unlock portable-work
```

---

## git worktree move

Move a worktree to a new filesystem location. The main worktree cannot be moved with this command. Linked worktrees containing submodules also cannot be moved.

### Syntax

```
git worktree move <worktree> <new-path>
```

### Key Flags

| Flag | Description |
|---|---|
| `<worktree>` | **(Required)** Path or unique suffix identifying the worktree to move |
| `<new-path>` | **(Required)** Destination filesystem path |
| `--force` | (Pass twice) Override a locked destination or move a locked worktree. Use `-f` once for a missing destination, `-f` twice for a locked worktree |

### Examples

Move a worktree to a new location:
```bash
git worktree move ../old-path ../new-path
```

Force-move a locked worktree:
```bash
git worktree move -f -f ../locked-worktree ../new-location
```

> **Note:** If you move a worktree manually (without this command), use `git worktree repair` to reestablish the administrative links.

---

## git worktree remove

Remove a linked worktree. Only clean worktrees (no untracked files and no modifications to tracked files) can be removed without `--force`. The main worktree cannot be removed.

### Syntax

```
git worktree remove [-f] <worktree>
```

### Key Flags

| Flag | Description |
|---|---|
| `<worktree>` | **(Required)** Path or unique suffix identifying the worktree to remove |
| `-f` / `--force` | Remove an unclean worktree. Use twice to remove a locked worktree |

### Examples

Remove a clean worktree:
```bash
git worktree remove ../temp-fix
```

Force-remove an unclean worktree:
```bash
git worktree remove -f ../dirty-worktree
```

Force-remove a locked worktree (must specify `--force` twice):
```bash
git worktree remove -f -f ../locked-worktree
```

---

## git worktree prune

Remove stale administrative information for worktrees whose working trees no longer exist. This is useful if a working tree was deleted without using `git worktree remove`.

### Syntax

```
git worktree prune [-n] [-v] [--expire <time>]
```

### Key Flags

| Flag | Description |
|---|---|
| `-n` / `--dry-run` | Do not remove anything; only report what would be removed |
| `-v` / `--verbose` | Report all removals as they happen |
| `--expire <time>` | Only prune missing worktrees older than the specified time. The `<time>` format follows Git's date formats (e.g., `2.weeks.ago`, `1.month.ago`) |

### Examples

Dry-run to see what would be pruned:
```bash
git worktree prune -n
```

Verbose pruning:
```bash
git worktree prune -v
```

Prune only worktrees missing for more than two weeks:
```bash
git worktree prune --expire 2.weeks.ago
```

---

## git worktree repair

Repair worktree administrative files that have become corrupted or outdated due to external factors, such as manually moving the main repository or a linked worktree.

### Syntax

```
git worktree repair [<path>...]
```

### Key Flags

| Flag | Description |
|---|---|
| `<path>...` | One or more paths to linked worktrees whose connections should be repaired. If omitted, only the current worktree is repaired |
| `--relative-paths` / `--no-relative-paths` | Link worktrees using relative or absolute paths. In repair mode, updates linking files if there's an absolute/relative mismatch, even if the links are correct |

### Behaviour by Scenario

| Scenario | Command | Effect |
|---|---|---|
| Main worktree moved | `git worktree repair` (from main worktree) | Reestablishes links from all linked worktrees back to the new main worktree location |
| Linked worktree moved without `move` | `git worktree repair` (from the moved worktree) | Reconnects the moved worktree to the main repository |
| Multiple linked worktrees moved | `git worktree repair <path1> <path2> ...` | Reconnects all specified worktrees |
| Both main and linked worktrees moved | `git worktree repair <path1> <path2> ...` (from main) | Reestablishes all connections in both directions |

### Examples

Repair all linked worktrees after moving the main repository:
```bash
git worktree repair
```

Repair a specific moved worktree:
```bash
git worktree repair ../moved-worktree
```

Repair multiple moved worktrees at once:
```bash
git worktree repair ../worktree-a ../worktree-b ../worktree-c
```

---

## Notes

### Worktree Identification

Worktrees can be identified by path (relative or absolute). If the last path component is unique among all worktrees, it can be used as a shorthand:

```bash
# With worktrees at /abc/def/ghi and /abc/def/ggg
git worktree lock ghi          # locks /abc/def/ghi
git worktree lock def/ghi      # also locks /abc/def/ghi
git worktree lock ggg          # locks /abc/def/ggg
```

### Per-Worktree vs Shared Refs

- **Per-worktree** (not shared): `HEAD`, `refs/bisect/`, `refs/worktree/`, `refs/rewritten/`
- **Shared**: All other `refs/` paths
- Access per-worktree refs from another worktree via: `main-worktree/HEAD`, `worktrees/<id>/HEAD`

### Configuration

| Config Option | Default | Description |
|---|---|---|
| `worktree.guessRemote` | `false` | Automatically find a unique remote-tracking branch when adding a worktree without a commit-ish |
| `worktree.useRelativePaths` | `false` | Use relative paths for worktree links. Implies `extensions.relativeWorktrees` |
| `extensions.worktreeConfig` | unset | Enable per-worktree configuration files (`.git/worktrees/<id>/config.worktree`) |
| `gc.worktreePruneExpire` | `"3.months.ago"` | How long before a missing worktree's administrative files are eligible for automatic pruning via `git gc` |

---

## See Also

- [Git Worktree Overview](./overview.md) — Core concepts, use cases, and subcommand overview

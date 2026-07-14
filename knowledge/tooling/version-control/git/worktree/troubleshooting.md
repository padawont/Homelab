---
title: "Git Worktree Troubleshooting"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags: ["git", "worktree", "troubleshooting"]
sources:
  - url: "https://git-scm.com/docs/git-worktree"
    title: "Git - git-worktree Documentation"
last_audit_date: 2026-06-07
---

# Git Worktree Troubleshooting

Common issues encountered when using `git worktree` and their solutions.

## Issue Reference

| Issue | Symptom | Cause | Solution |
|---|---|---|---|
| Branch already checked out | `fatal: '<branch>' is already checked out` | The branch is already checked out in another worktree | Locate the existing worktree and switch to it, or force checkout with `-f` |
| Stale worktree directories | Worktree directory was deleted manually but `git worktree list` still shows it | Git retains administrative files in `.git/worktrees/` even after the working tree is removed | Run `git worktree prune` to remove stale administrative entries |
| Lock prevents removal | `fatal: 'worktree' is locked` or `fatal: could not remove worktree` | The worktree was locked (via `git worktree lock`) to prevent pruning or deletion | Use `git worktree unlock <worktree>` to unlock, then remove |
| Disk space exhaustion | Low disk space warnings; multiple large working directories exist | Each worktree is a full working copy with its own index, objects, and checked out files | Prune stale worktrees, remove unused worktrees, or use sparse checkout |
| `git worktree prune` doesn't remove directories | Directories still exist on disk after running `git worktree prune` | `prune` only removes stale administrative files, not worktree directories | Manually remove the directory, or use `git worktree remove <worktree>` first |
| Worktree moved manually | `git worktree list` shows old path; operations fail | Manually moving a worktree directory breaks the administrative file links | Use `git worktree repair` or update the `gitdir` file manually |
| Permission denied in shared repo | `fatal: could not create worktree` or file permission errors | Shared repositories with multiple users can have permission mismatches in worktree files | Fix permissions on `.git/worktrees/` and the worktree directory; avoid root-owned files |

---

## Branch Already Checked Out

**Symptom:**

```
fatal: 'feature-x' is already checked out at '/home/user/project-worktrees/feature-x'
```

Git refuses to check out a branch that is already active in another worktree. Each branch can be checked out in only one worktree at a time.

**Cause:**

The branch is currently checked out in another linked worktree. Git enforces this to prevent conflicting updates to the same branch reference from multiple working directories.

**Solutions:**

1. **Switch to the existing worktree** — navigate to the path shown in the error message and work from there.

2. **List all worktrees** to see where the branch is checked out:

   ```bash
   git worktree list
   ```

3. **Force checkout** (use with caution) — if you are certain the other worktree is unused or stale, override the safeguard:

   ```bash
   git worktree add -f /path/to/new-worktree feature-x
   ```

   The `-f` / `--force` flag bypasses the branch-already-checked-out check. Only use this when the existing worktree is abandoned and you intend to replace it.

---

## Stale Worktree Directories

**Symptom:**

A worktree directory was deleted with `rm -rf` or through the file manager, but `git worktree list` still shows the entry, and operations on the repository may complain about missing worktrees.

**Cause:**

When you delete a worktree's working directory manually, Git does not automatically remove the corresponding administrative metadata in `.git/worktrees/<name>/`. This metadata includes the `gitdir` file, `HEAD`, and other per-worktree refs. The stale entry remains until explicitly cleaned up.

**Solution:**

Run `git worktree prune` from the main repository or any linked worktree:

```bash
git worktree prune
```

This removes administrative entries in `.git/worktrees/` for any worktree whose working tree directory no longer exists. Use `-n` (dry-run) to preview what will be removed:

```bash
git worktree prune -n
```

Use `-v` for verbose output that lists each removed entry:

```bash
git worktree prune -v
```

The prune operation respects `gc.worktreePruneExpire` (default: 3 months). Worktrees that went missing more recently are not pruned unless `--expire` is set explicitly:

```bash
git worktree prune --expire=now
```

---

## Lock Conflicts

**Symptom:**

Attempting to remove or move a worktree produces:

```
fatal: worktree '/path/to/worktree' is locked
```

Or when using `--force` once:

```
fatal: could not remove worktree '/path/to/worktree'
```

**Cause:**

The worktree was locked with `git worktree lock`, which creates a `locked` file (optionally containing a reason string) inside the worktree's administrative directory (`.git/worktrees/<name>/locked`). Locking prevents:

- Automatic pruning of the worktree's administrative files
- Moving the worktree with `git worktree move`
- Removing the worktree with `git worktree remove`

Locking is useful for worktrees on removable media or network shares that may not always be mounted.

**Solutions:**

1. **Unlock the worktree**:

   ```bash
   git worktree unlock <worktree>
   ```

   Identify the worktree by its path, or by a unique trailing path component:

   ```bash
   git worktree unlock feature-x
   # or
   git worktree unlock /path/to/worktree
   ```

2. **Force remove a locked worktree** (bypasses the lock):

   ```bash
   git worktree remove -f -f <worktree>
   ```

   The `-f` flag must be specified twice to override a lock. This is destructive — ensure the lock is no longer needed.

---

## Disk Space Management

**Symptom:**

Disk space fills up faster than expected. Multiple worktrees consume significant storage.

**Cause:**

Each linked worktree is a full working directory containing all checked-out files. While worktrees share the repository's object store (`.git/objects/`), each has its own:

- Working tree files (the checked-out snapshot of the branch)
- `HEAD`, `index`, and per-worktree refs
- Staged and unstaged changes

A monorepo with many worktrees can easily consume tens of gigabytes in working tree files alone.

**Solutions:**

1. **List all worktrees and their sizes**:

   ```bash
   git worktree list
   du -sh /path/to/each/worktree
   ```

2. **Remove stale or unused worktrees**:

   ```bash
   git worktree remove <worktree>
   ```

   For worktrees with uncommitted changes, use `-f` to force removal (files are lost).

3. **Use sparse checkout** in worktrees that only need a subset of files:

   ```bash
   git worktree add --no-checkout ../sparse-worktree
   cd ../sparse-worktree
   git sparse-checkout set --cone <dir1> <dir2>
   git checkout
   ```

4. **Run `git worktree prune`** periodically to clean up administrative entries for worktrees whose directories were manually deleted.

5. **Set `gc.worktreePruneExpire`** in git config to automatically prune stale worktree entries sooner:

   ```bash
   git config gc.worktreePruneExpire now
   ```

---

## Git Worktree Prune vs Manual Cleanup

**Symptom:**

After manually deleting a worktree directory and running `git worktree prune`, the directory is still on disk (expected — it was already removed) but the administrative entry is gone. Conversely, running `git worktree prune` seems to do nothing when the directory still exists.

**Cause:**

There is a distinction between what `git worktree prune` does and what manual filesystem operations do:

| Action | Removes working directory | Removes `.git/worktrees/<name>/` metadata |
|---|---|---|
| `git worktree remove <worktree>` | Yes | Yes |
| `rm -rf <worktree-dir>` | Yes | No |
| `git worktree prune` | No | Yes (for missing worktrees only) |
| Manual removal of `.git/worktrees/<name>/` | No | Yes |

**Solutions:**

- **Preferred workflow** — always remove worktrees with `git worktree remove` to clean up both the working directory and administrative files in one step.

- **After accidental deletion** — run `git worktree prune` to clean up the residual administrative metadata:

  ```bash
  git worktree prune -v
  ```

- **Dry-run before pruning** — preview what will be removed:

  ```bash
  git worktree prune -n
  ```

- **To completely remove a worktree whose directory is already deleted** — if `git worktree prune` does not remove the entry (e.g. it was locked or not old enough), force the prune:

  ```bash
  git worktree prune --expire=now -v
  ```

---

## Moving Worktrees

**Symptom:**

After moving a worktree directory to a new location (e.g. `mv /old/path/worktree /new/path/worktree`), `git worktree list` shows the old path, and operations on the worktree fail with messages about missing directories or broken links.

**Cause:**

Each linked worktree has two connection points:

- A `.git` file at the root of the worktree directory that points to the administrative directory (`.git/worktrees/<name>/`) in the main repository.
- A `gitdir` file inside the administrative directory (`.git/worktrees/<name>/gitdir`) that contains the path back to the worktree's working directory.

Manually moving the worktree directory breaks both links unless they are updated.

**Solutions:**

1. **Use `git worktree move`** (recommended, moves both directory and administrative files):

   ```bash
   git worktree move <worktree> /new/path/worktree
   ```

   This updates the administrative metadata automatically. Note: the main worktree cannot be moved with this command.

2. **Repair after manual move** — run `git worktree repair` from the moved worktree to reestablish the connection:

   ```bash
   cd /new/path/worktree
   git worktree repair
   ```

   Or repair from the main repository by specifying the new path:

   ```bash
   git worktree repair /new/path/worktree
   ```

   To repair multiple moved worktrees at once:

   ```bash
   git worktree repair /new/path/a /new/path/b /new/path/c
   ```

3. **Manual repair** — if `repair` is not available (older Git versions), update the files directly:

   ```bash
   # Update the gitdir file inside the admin directory
   echo "/new/path/worktree" > .git/worktrees/<name>/gitdir

   # Update the .git file inside the worktree directory
   echo "gitdir: /original/repo/.git/worktrees/<name>" > /new/path/worktree/.git
   ```

4. **Moving the main repository** — if the main (bare or non-bare) repository moves, run `git worktree repair` from the main worktree to rewire all linked worktrees:

   ```bash
   git worktree repair
   ```

   This updates the `.git` files in each linked worktree to point to the new location of the main repository's administrative directory.

---

## Permission Issues with Shared Repositories

**Symptom:**

When using worktrees in a repository shared among multiple users (e.g. on a shared server), operations fail with:

```
fatal: could not create worktree '/shared/repo/worktrees/feature-x'
error: insufficient permission for adding an object to repository database
fatal: could not set permissions on '.git/worktrees/...'
```

Or the worktree is created but subsequent `git` commands fail with permission errors.

**Cause:**

Git uses shared administrative files under `.git/worktrees/` and the objects database. When multiple users create and manage worktrees, file ownership and permission mismatches occur:

- User A creates a worktree, making files owned by user A.
- User B tries to prune or remove that worktree but lacks write permission on user A's files.
- Worktree administrative directories created with restrictive `umask` settings are inaccessible to other users in the same group.

**Solutions:**

1. **Use a shared repository with proper group permissions** — initialize the repository with `--shared`:

   ```bash
   git init --shared=group
   # or for existing repos:
   git config core.sharedRepository group
   ```

   This tells Git to set group-writable permissions on new files and directories.

2. **Set `umask` consistently** — ensure all users have a umask that permits group access (e.g. `umask 002`):

   ```bash
   umask 002
   # Then create/manage worktrees
   ```

3. **Fix permissions when they break** — recursively set group ownership and permissions on the repository:

   ```bash
   chgrp -R shared-group /path/to/repo
   chmod -R g+rwX /path/to/repo
   ```

4. **Lock worktrees to prevent accidental cross-user prunes** — users can lock their worktrees with a descriptive reason:

   ```bash
   git worktree lock --reason "owned by userA" ../feature-x
   ```

5. **Use `sudo` or `chown` as last resort** — if a user's stale worktree blocks operations and they are unavailable, an admin can override:

    ```bash
    sudo git worktree remove -f -f /path/to/stale-worktree
    ```

---

## See Also

- [Git Worktree Overview](./overview.md) — Core concepts, use cases, and subcommand overview
- [CLI Reference](./cli-reference.md) — All `git worktree` subcommands with flags and examples
- [Workflows](./workflows.md) — End-to-end workflow patterns

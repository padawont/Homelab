---
title: "Git Worktree Branching"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags: ["git", "worktree", "branching"]
sources:
  - "https://git-scm.com/docs/git-worktree"
last_audit_date: 2026-06-07
---

# Git Worktree Branching

Git worktrees let you check out multiple branches of the same repository simultaneously, each in its own directory, sharing a single `.git` directory. This note covers the relationship between worktrees and branches, including restrictions, detached and attached HEAD states, and per-worktree branch management.

## Worktree-to-Branch Mapping

Each worktree is associated with a branch when it is in an attached-HEAD state. The mapping is one-to-one: **a branch can only be checked out in one worktree at a time** across the entire repository.

```
repo/
├── .git/                   # shared object store, refs, config
├── main-worktree/          # original working tree (usually main branch)
└── worktrees/
    └── feature-foo/        # linked worktree (e.g., feature/foo branch)
```

### Checking the mapping

```bash
git worktree list
```

Output shows each worktree path, the branch currently checked out, and the commit:

```
/home/user/project          (main)              abc1234 [main]
/home/user/project-feature  (feature/login)     def5678 [feature/login]
```

An asterisk `*` marks the worktree you are currently in.

## The Branch-Lock Restriction

Git prevents the same branch from being checked out in more than one worktree. Git enforces this restriction by tracking which branch each worktree has checked out in per-worktree metadata. When you attempt to check out a branch already active elsewhere, Git refuses.

### Why it exists

If two worktrees had the same branch checked out, simultaneous commits would produce a divergent history. One worktree would not see the other's commits, creating a fork that must be reconciled manually. The restriction prevents this class of error.

### The "already checked out" error

```text
fatal: 'feature/login' is already checked out at '/home/user/project-feature'
```

This occurs when you try to check out a branch that is already active in another worktree.

#### Resolution options

1. **Move to the other worktree** and commit, stash, or discard changes, then switch to a different branch.
2. **Delete the other worktree** with `git worktree remove <path>` (only safe if that worktree has no uncommitted changes).
3. **Force checkout** (advanced, use with caution):

   ```bash
   git checkout --ignore-other-worktrees feature/login
   ```

   The `--ignore-other-worktrees` flag bypasses the safety check but does not actually unlock the branch across worktrees — you risk divergent histories.

4. **Prune stale worktree records** if the worktree directory was deleted manually:

   ```bash
   git worktree prune
   ```

## Attached vs Detached HEAD

### Attached HEAD (default)

When a worktree is created from a branch reference (with or without `-b`), HEAD points to that branch ref. All commits update the branch as usual.

```bash
git worktree add ../hotfix hotfix/fix-login
# HEAD -> refs/heads/hotfix/fix-login
```

Use attached HEAD when you plan to make commits and push the branch.

### Detached HEAD

A worktree in detached HEAD state does not track a branch. New commits do not advance any ref unless you explicitly create one.

```bash
git worktree add --detach ../experiment HEAD~3
# HEAD points directly to the commit, not a branch
```

#### When to use detached HEAD

- **Reviewing old commits** — inspect a specific release tag or historic commit without affecting any branch.
- **Experiments** — try throwaway changes without worrying about branch names.
- **Cherry-picking** — apply individual commits from an old branch without checking the full branch out.
- **Build verification** — build and test a tagged release that should not be modified.

To turn a detached worktree into a tracked branch later:

```bash
git switch -c new-branch-name
```

## Creating Worktrees from Specific Refs

Worktrees can be created from any tree-ish reference: branches, tags, commits, or remote branches.

### From a commit hash

```bash
git worktree add ../review a1b2c3d
```

HEAD will be detached at that commit.

### From a tag

```bash
git worktree add ../release v1.0.0
```

Creates a detached HEAD worktree at the tag's commit. Useful for verifying or patching a release.

### From a remote branch

```bash
git worktree add ../feature-fix origin/feature/fix
```

This creates a local branch named `feature/fix` tracking `origin/feature/fix`. Equivalent to `git checkout -b feature/fix origin/feature/fix` inside a single-repo workflow.

## --detach for Throwaway Worktrees

The `--detach` flag forces a detached HEAD even when a valid branch name is given. This is useful for ephemeral work that does not need a named branch.

```bash
git worktree add --detach ../tmp-spike feature/login
# HEAD is detached at the tip of feature/login, but feature/login
# itself is not checked out — it remains available in other worktrees
```

Because `--detach` does not claim the branch, the original worktree and any other worktree can still use `feature/login`. This is the key difference from omitting `--detach`.

## --orphan for Branchless Worktrees

The `--orphan` flag creates a worktree with an orphan branch — a branch that shares no commit history with the rest of the repository.

```bash
git worktree add --orphan ../docs gh-pages
```

This creates a new branch `gh-pages` with no parent commit — an orphan/unborn branch. Both the worktree and the index start empty. (When `-b`/`-B` is not supplied, the default branch name is the basename of the `<path>` argument, not the `HEAD` ref name.)

Use cases:

- **GitHub Pages** — deploy a `gh-pages` branch with no commit ancestry.
- **Documentation sites** — build static site output isolated from source code history.
- **Config branches** — store per-environment config in a clean branch.

## The -b vs -B Flags

When creating a worktree with a new branch, `-b` and `-B` control the behavior if the branch already exists.

### -b (create new)

```bash
git worktree add -b feature/new-thing ../new-thing main
```

Creates a new branch `feature/new-thing` at the commit referenced by `main`. Fails with an error if `feature/new-thing` already exists.

### -B (reset existing)

```bash
git worktree add -B feature/reset ../reset main
```

If `feature/reset` exists, it is reset to match `main`. If it does not exist, it is created. This is equivalent to deleting and recreating the branch, but done in one command.

Use `-B` when you need a clean branch for a repeatable task (e.g., regenerating a deployment branch).

## Checking Out a Different Branch Inside a Worktree

A worktree is a real git working tree. You can run `git checkout` (or `git switch`) inside it to move to another branch — with one restriction: the target branch must not be checked out in any other worktree.

```bash
# Inside worktree at ../feature-login
git switch main
# Works if 'main' is not checked out anywhere else
```

If the target branch is locked by another worktree, you will see the same `fatal: already checked out` error described above. The solution is the same: find the other worktree, move it to a different branch, or use `--ignore-other-worktrees` with caution.

### Best practice

Designate one worktree as the "main" worktree (usually the original clone). Keep other worktrees focused on feature branches. When you need to sanity-check across branches, create a new worktree rather than switching an existing one — it is cheaper and avoids contention:

```bash
git worktree add ../quick-look feature/login
git worktree add ../other-branch other/experiment
# Both available simultaneously, no switching needed
```

---

## See Also

- [Git Worktree Overview](./overview.md) — Core concepts, use cases, and subcommand overview
- [CLI Reference](./cli-reference.md) — All `git worktree` subcommands with flags and examples

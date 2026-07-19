---
title: "Worktrunk Comparisons"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags:
  - worktrunk
  - comparisons
  - alternatives
sources:
  - "https://worktrunk.dev/faq/"
  - "https://git-scm.com/docs/git-worktree"
last_audit_date: 2026-06-07
---

# Worktrunk Comparisons

This document compares Worktrunk against alternative approaches for managing multiple branches and work contexts in git-based development.

## Comparison Table

| Dimension | Worktrunk | Plain `git worktree` | Branch Switching | git-machete / git-town | Git TUIs | Tmux/screen + single worktree | Multiple Local Clones | Shell Aliases |
|---|---|---|---|---|---|---|---|---|
| **Automation** | Full lifecycle automation (create, merge, cleanup) | Manual lifecycle management | Manual branch ops | Branch stack automation (single dir) | TUI for single-repo ops | None | None | Partial (ad-hoc scripts) |
| **Isolation** | Full (each worktree is independent) | Full (each worktree is independent) | None (single directory) | None (single directory) | None (operates on single repo) | None (single directory) | Full (entirely separate repos) | Full (wraps git worktree) |
| **Configuration** | Declarative user + project config (TOML) | None (vanilla git) | None | Tool-specific config | TUI-specific config | None | None | None (inline scripts) |
| **Hooks** | Pre/post hooks per lifecycle event (start, merge, remove) | None | None | Action hooks (limited scope) | None | None | None | None |
| **Status Visibility** | `wt list` aggregates all worktrees: branch, commits, CI, conflicts, changes | `git worktree list` shows paths only | `git branch` shows branches only | Branch stack status | Single-repo status | Manual (shell prompt) | Manual (scan directories) | Depends on script implementation |

## vs Plain `git worktree`

| Aspect | `git worktree` | Worktrunk (`wt`) |
|---|---|---|
| Lifecycle | Manual: `git worktree add`, `cd`, `git merge`, `git worktree remove` | Automated: `wt switch --create`, `wt merge`, `wt remove` |
| Directory naming | User-specified path | Consistent `<repo>.<branch>` naming by default |
| Cleanup validation | Basic (refuses with uncommitted changes) | Integrated branch cleanup with squash/merge detection |
| Hooks | None | Pre/post hooks per lifecycle event |
| Unified status | `git worktree list` shows paths only | `wt list` shows branch, commits ahead/behind, CI status, conflict detection, file changes |

For detailed reference on git worktree itself, see [Git Worktree](../../version-control/git/worktree/overview.md).

Worktrunk wraps `git worktree` and automates the full lifecycle. A typical `git worktree` workflow requires multiple manual steps:

```bash
git worktree add -b feature-branch ../myapp-feature main
cd ../myapp-feature
# ...work, commit, push...
cd ../myapp
git merge feature-branch
git worktree remove ../myapp-feature
git branch -d feature-branch
```

With Worktrunk this becomes:

```bash
wt switch --create feature-branch  # Creates worktree, runs setup hooks
# ...work...
wt merge                            # Merges into default branch, cleans up
```

No need to `cd` back -- `wt merge` runs from the feature worktree and merges into the target.

## vs Branch Switching (`git switch` / `git checkout`)

| Aspect | Branch Switching | Worktrunk |
|---|---|---|
| Working directory | Single directory for all branches | One directory per branch |
| Uncommitted changes | Block switching or get mixed across branches | Independent per worktree |
| Index | Shared (single `.git/index`) | Independent (each worktree has its own index) |
| Parallel work | Impossible on same repo without stashing | Full parallel capability |

Branch switching operates on a single working directory. Uncommitted changes from one context must be stashed or committed before switching to another branch. This creates friction when working on multiple features, reviews, or experiments concurrently. Worktrunk gives each branch its own directory with an independent working tree and index, eliminating the need to stash or commit before switching context.

## vs git-machete / git-town

| Aspect | git-machete / git-town | Worktrunk |
|---|---|---|
| Scope | Branch stack management in a single directory | Multi-worktree management across directories |
| Stacked branches | First-class support | Not native (community `worktrunk-sync` tool available) |
| Worktree isolation | None | Full |
| Compatibility | Can be used inside individual worktrees | Can run git-machete/git-town inside each worktree |

These tools have different scopes and are complementary rather than competing:

- **git-machete** manages branch dependency stacks (parent/child relationships) within a single working directory.
- **git-town** automates git workflow commands (sync, ship, hack) within a single directory.
- **Worktrunk** manages multiple worktrees, each containing its own branch, with hooks and aggregated status.

Worktrunk can be used alongside git-machete or git-town -- run branch stack management inside each individual worktree as needed.

## vs Git TUIs (lazygit, gh-dash)

| Aspect | Git TUIs | Worktrunk |
|---|---|---|
| Scope | Single repository | Multi-worktree management |
| Status aggregation | Current repo only | All worktrees across branches |
| Automation hooks | None | Pre/post lifecycle hooks |
| Merge coordination | Manual per-repo | `wt merge` with integrated cleanup |

Git TUIs like lazygit and gh-dash provide interactive terminal interfaces for git operations within a single repository. They excel at visualizing commit history, staging files, and managing branches in the current working directory.

Worktrunk addresses a different problem: managing multiple worktrees across branches, running automation hooks, and aggregating status. TUIs work well inside each individual worktree directory and can be used alongside Worktrunk.

## vs Tmux/screen with Single Worktree

| Aspect | Tmux/screen + single worktree | Worktrunk |
|---|---|---|
| Context switching | Must stash or commit before switching branch | Switch instantly via `wt switch` |
| Parallel contexts | Windows/panes share the same working directory | Each worktree is an independent directory |
| State isolation | None at the filesystem level | Full (separate working tree, index, HEAD) |

Using tmux or screen with a single worktree means each window or pane operates in the same working directory. To switch context, you must either stash uncommitted changes or create a commit -- otherwise `git switch` or `git checkout` will refuse or overwrite working tree changes. Worktrunk avoids this entirely by giving each branch its own worktree.

## vs Multiple Local Clones

| Aspect | Multiple Clones | Worktrunk |
|---|---|---|
| Disk usage | Duplicates entire `.git/objects` and `.git/refs` | Shares object store and refs via `git worktree` |
| Remote tracking | Each clone maintains its own remote tracking | Shared refs, consistent view |
| Setup overhead | Full `git clone` per branch | Instant worktree creation |
| Git operations | Must fetch/push per clone | Single remote, shared across worktrees |

Multiple local clones provide isolation but waste disk space and bandwidth. Every clone duplicates the entire object database and maintains its own remote tracking refs. Worktrunk (via `git worktree`) shares the repository's `.git` directory across all worktrees -- objects, refs, and configuration are shared while working trees and indices remain independent.

| Approach | Disk Usage | `git clone` time | `git fetch` Scope | Setup Speed |
|---|---|---|---|---|
| Multiple clones | Full `.git` per clone (hundreds of MB+) | Full clone each time | Every clone fetches independently | Slow (clone per branch) |
| Worktrunk | Single `.git` shared | Once | One `git fetch` for all worktrees | Instant (`wt switch --create`) |

## vs Shell Aliases for `git worktree`

| Aspect | Shell Aliases | Worktrunk |
|---|---|---|
| Consistency | Ad-hoc, varies per developer/team | Standardized across environments |
| Lifecycle hooks | None (raw git only) | Pre/post hooks (install deps, start services, lint) |
| Status overview | None (must run multiple commands) | `wt list` with branch info, CI, conflicts, changes |
| Configuration | None (inline in alias) | Declarative TOML config (user + project) |
| Portability | Tied to specific shell config | Works across all supported shells |
| Error handling | Basic (shell exit code) | Integrated cleanup, branch deletion safety, locking |

Custom shell aliases can wrap `git worktree` subcommands but each team member ends up with a slightly different setup. Common patterns like `gwa` (git worktree add) and `gwl` (git worktree list) lack:

- Consistent naming conventions for worktree directories
- Pre/post hooks for project setup and teardown
- Unified status across all worktrees
- Safe cleanup that detects merged vs unmerged branches
- Declarative configuration that can be checked into the repository

Worktrunk provides all of these as a single, portable CLI that works across shells and operating systems.

## Summary

Worktrunk occupies a unique niche: it is a lifecycle management layer on top of `git worktree` that provides automation, hooks, declarative config, and aggregated status. Most alternatives address a subset of these concerns or solve different problems entirely:

- **Use Worktrunk** when you need to manage multiple worktrees with automation, hooks, and unified status -- especially for parallel AI agent workflows or concurrent feature development.
- **Use git-machete/git-town** alongside Worktrunk when you also need stacked branch dependency management.
- **Use Git TUIs** inside individual worktrees for interactive staging, diffing, and commit visualization.
- **Prefer plain `git worktree`** for ad-hoc, one-off worktrees where full lifecycle automation is unnecessary.

The tools are not mutually exclusive -- Worktrunk integrates with and complements most of these alternatives.

---

## See Also

- [CLI Reference](./cli-reference.md) — All `wt` commands with flags and examples

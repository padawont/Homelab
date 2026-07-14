---
title: "Git Worktree Installation"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags: ["git", "worktree", "installation"]
sources:
  - "https://git-scm.com/docs/git-worktree"
last_audit_date: 2026-06-07
---

# Installation

## Requirements

Git worktree requires **Git >= 2.5**, released in July 2015.

No separate installation is needed -- `git worktree` is built into Git and ships with every distribution.

## Check Your Git Version

```bash
git --version
```

If your version is lower than 2.5, upgrade Git via your system package manager.

## Verify Worktree Support

Confirm the subcommand is available on your system:

```bash
git worktree help
```

Or list existing worktrees (will return an empty list or an error if unavailable):

```bash
git worktree list
```

If either command runs without an `unknown option` or `unknown command` error, worktree support is available.

## Platform Support

Git worktree works on all platforms where Git runs:

- Linux
- macOS
- Windows
- BSD
- Any other OS with Git >= 2.5

There are no platform-specific installation steps or dependencies.

---

## See Also

- [Git Worktree Overview](./overview.md) — Core concepts, use cases, and subcommand overview

---
title: "Worktrunk core commands"
status: draft
author: "padawont"
date: 2026-08-20
tags: [git, worktrees, cli, ai-agents]
sources:
  - url: "https://worktrunk.dev/switch/"
    title: "wt switch docs"
  - url: "https://worktrunk.dev/list/"
    title: "wt list docs"
  - url: "https://worktrunk.dev/remove/"
    title: "wt remove docs"
  - url: "https://worktrunk.dev/merge/"
    title: "wt merge docs"
  - url: "https://worktrunk.dev/step/"
    title: "wt step docs"
last_audit_date: 2026-08-20
related_docs:
  - "./02_Knowledge/technologies/tools/worktrunk/overview.md"
  - "./02_Knowledge/technologies/tools/worktrunk/automation.md"
  - "./02_Knowledge/technologies/tools/worktrunk/install-config.md"
---

# Worktrunk core commands

## Overview

The three core commands are `wt switch`, `wt list`, and `wt remove`, with `wt merge` and `wt step` for integrating and running individual git operations. Command help is always available via `wt --help` / `wt <command> --help`.

## Details

### wt switch

Switch to a worktree, creating it if needed. Differs from `git switch`: it navigates between worktrees, not branches in place.

- `wt switch <branch>` — switch to an existing branch's worktree
- `wt switch -` — previous worktree (like `cd -`)
- `wt switch --create <branch>` — create new branch + worktree from `--base` (defaults to default branch)
- `wt switch -x <cmd> [-- args]` — run a command after switching (replaces the process; used to launch agents/editors)
- `wt switch --no-cd` — skip the directory change (hooks still run); `--clobber` removes stale non-worktree paths

Shortcuts that work anywhere a branch is accepted: `^` default branch, `@` current branch, `-` previous worktree, `pr:{N}` / `mr:{N}` (and PR/MR URLs) for GitHub/GitLab.

Without a branch argument it opens an interactive picker with live diff/log previews; flags `--branches`, `--remotes`, `--prs` widen the candidate set.

### wt list

List worktrees and their status: uncommitted changes, divergence from default branch and remote, and optionally CI + LLM summaries.

- `wt list` — table of worktrees
- `wt list --full` — adds CI status (PR/MR pipeline) and LLM branch summaries (requires `[list] summary = true` + `[commit.generation]`)
- `wt list --branches` / `--remotes` — include branches/remote branches without worktrees
- `wt list --format=json` — structured output (schema 2 envelope via `[list] json-schema = 2`) for scripts
- `wt list statusline` — single-line status for the current worktree (`--format=claude-code` feeds Claude Code's statusline)

Example — abstract (`@` current, `^` primary, `+` other worktree):

```
wt list
  Branch       Status        HEAD±    main↕     main…±  Remote⇅  Commit   Age   Message
@ feature-auth  +   ↑      +27   -8   ↑1       +31                4bc72dc  2h    Add authenticati…
^ main              ^⇡                                    ⇡1      0e631ad  1d    Initial commit
```

### wt remove

Remove a worktree and delete the branch if merged. Defaults to the current worktree.

- `wt remove` — remove current worktree + branch
- `wt remove <branch>` — remove specific worktree(s)
- `wt remove --no-delete-branch` — keep the branch
- `wt remove -D` — force-delete an unmerged branch; `-f` — force a dirty worktree
- `wt remove --reap` — kill processes running in the worktree (dev servers, watchers); Unix only
- `wt remove /path` — remove a detached-HEAD worktree by path

Branches are deleted when merging them would add no changes to the default branch — it checks six conditions (same commit, ancestor, no added changes, trees match, merge adds nothing, patch-id match) so it works across squash/rebase workflows. Removal runs in the background by default (renames into `.git/wt/trash/`, then detached cleanup).

### wt merge

Merge the current branch **into** the target branch (like "Merge pull request" locally), squash & rebase, fast-forward the target, remove the worktree.

Pipeline: commit → squash → rebase → pre-merge hooks → fast-forward merge → pre-remove hooks → cleanup → background post-hooks.

Flags: `--no-squash` (preserve history), `--no-commit`, `--no-rebase`, `--no-remove`, `--no-ff` (merge commit). Config defaults live under `[merge]` (squash, commit, rebase, remove, verify, ff).

### wt step

Run individual operations — the building blocks of `wt merge`:

- `commit` — stage + commit with LLM-generated message
- `squash` — squash branch commits into one
- `rebase` — rebase onto target (branch/tag/SHA)
- `push` — fast-forward the target branch to the current branch (local only)
- `diff` — all changes since branching (committed, staged, unstaged, untracked)
- `copy-ignored` — copy gitignored files (caches, `node_modules/`) between worktrees
- `for-each` — run a command in every worktree
- `eval` — evaluate a template expression (e.g. `wt step eval '{{ branch | hash_port }}'`)
- `prune` — bulk-remove worktrees merged into the default branch (min-age guard, default 1d)
- `relocate` — move worktrees to their template-implied paths
- `promote` / `tether` — experimental utilities (branch into main worktree; run a command tied to worktree lifetime)

### Aliases and per-branch vars

- `[aliases]` in config defines commands run as `wt <name>` (top-level), sharing hooks' template engine and `{{ args }}`; built-in commands take precedence.
- Per-branch vars via `wt config state vars set key=value`, read in templates as `{{ vars.<key> }}` and shown in `wt list` custom columns / hooks.

## Sources / Further Reading

- `wt switch` https://worktrunk.dev/switch/ · `wt list` https://worktrunk.dev/list/ · `wt remove` https://worktrunk.dev/remove/ · `wt merge` https://worktrunk.dev/merge/ · `wt step` https://worktrunk.dev/step/
- For automation (hooks, LLM commits) see `./02_Knowledge/technologies/tools/worktrunk/automation.md`; for install/shell/config see `./02_Knowledge/technologies/tools/worktrunk/install-config.md`.

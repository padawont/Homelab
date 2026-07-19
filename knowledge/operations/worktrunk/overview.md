---
title: "Worktrunk"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags: ["worktrunk", "git-worktree", "developer-tools", "ai-agents"]
sources:
  - "https://worktrunk.dev"
  - "https://github.com/max-sixty/worktrunk"
last_audit_date: 2026-06-07
---

# Worktrunk

Worktrunk is a CLI for git worktree management, designed for running AI agents in parallel. It wraps `git worktree` with declarative configuration, hooks, and unified status so that worktrees are as easy to work with as branches.

## How It Works

Worktrunk addresses worktrees by branch name rather than by filesystem path. Paths are computed from a configurable template (e.g. `{repo}.{branch}` or `{repo}/{branch}`), so you never need to type a path manually.

Under the hood, each Worktrunk command delegates to [git worktree](../../version-control/git/worktree/overview.md) operations:

- Creating a worktree calls `git worktree add -b <branch> <path>`
- Switching calls `git worktree add` (if missing) then `cd`s into the worktree directory
- Removing calls `git worktree remove <path>` then `git branch -d <branch>`

Worktrunk reads TOML configuration files (user-level and project-level) for configuration including the path template, hooks, aliases, and per-branch state variables.

## Quickstart

```bash
# Install via Homebrew
brew install worktrunk && wt config shell install

# Create and switch to a new worktree for a feature
wt switch --create feature-auth

# List all worktrees with rich status
wt list

# Merge changes back to main
wt merge main

# Remove a completed worktree and its branch
wt remove
```

Shell integration (`wt config shell install`) enables `wt switch` to change the current shell's working directory, making worktree navigation seamless.

## Core Commands

| Command | Purpose |
|---|---|
| `wt switch` | Switch to a worktree by branch name; create with `-c`/`--create`; run a command after switching with `-x`; supports interactive picker with live diff and log previews; can check out PRs with `wt switch pr:123` |
| `wt list` | List all worktrees with rich status — staged/unstaged changes, commits ahead/behind, CI status, AI-generated branch summaries; `--full` mode adds CI and LLM columns |
| `wt merge` | Squash, rebase onto target branch, fast-forward merge, and clean up in one command |
| `wt remove` | Remove a worktree and optionally delete its branch; runs post-merge hooks |
| `wt config` | Read and write TOML configuration (user and project scopes) |
| `wt step` | `wt step commit` commits staged changes; `wt step copy-ignored` shares build caches (`target/`, `node_modules/`) between worktrees to avoid cold starts |
| `wt hook` | Manage and inspect hook definitions |

## Session-to-Worktree Mapping

Worktrunk's core model is one worktree per branch, designed so that each AI agent or developer session gets an isolated working directory.

```bash
# Launch three parallel Claude Code agents, each in its own worktree
wt switch -x claude -c feature-a -- 'Add user authentication'
wt switch -x claude -c feature-b -- 'Fix the pagination bug'
wt switch -x claude -c feature-c -- 'Write tests for the API'
```

The same pattern works with `opencode` (e.g., `wt switch -x opencode -c feature-d -- 'Refactor the database layer'`), though OpenCode's integration is more limited — it supports activity tracking only (see the [opencode-integration guide](./opencode-integration.md)).

The `-x` flag runs a command (e.g., `claude`) after switching into the worktree. Arguments after `--` are passed to the command. This model supports managing 5-10+ parallel agent sessions without the agents stepping on each other's changes.

## Key Differentiators

- **Hooks system** — Run shell commands on create, pre-merge, post-merge, post-start, etc. Hooks can use template variables (branch name, worktree path, per-branch state variables) and support conditional execution via skip conditions.
- **Template-based path naming** — Path templates like `{repo}.{branch}` or configurable filters (e.g., `hash_port` for unique dev server ports per worktree) eliminate path management.
- **Shell integration** — `wt config shell install` installs a shell function so `wt switch` changes the directory of the current terminal session.
- **LLM commit messages** — `wt merge` can generate commit messages from diffs using an LLM, configurable via `worktrunk.toml`.
- **Interactive picker** — `wt switch` with no arguments opens a TUI that lets you browse worktrees with live diff and log previews before switching.
- **Build cache sharing** — `wt step copy-ignored` copies gitignored directories (e.g., `target/`, `node_modules/`) from an existing worktree to avoid cold rebuilds.
- **CI status and PR links** — `wt list --full` shows CI status and pull request links per branch.
- **Aliases and per-branch variables** — Custom `wt <name>` commands and branch-scoped state variables available in hook templates.

## Architecture

Worktrunk is a single binary CLI written in Rust. It:

1. Reads TOML configuration (user config at `~/.config/worktrunk/config.toml` or `$XDG_CONFIG_HOME`; project config at `.config/wt.toml`)
2. Wraps `git worktree` system commands via the `git2` Rust crate and shelling out to git
3. Runs hook scripts in a subprocess shell with environment variables set from template state
4. Provides an optional shell integration (eval'd shell function) that enables `cd`-style directory changes from `wt switch`

## Project Information

- **Language:** Rust
- **License:** MIT OR Apache-2.0 (dual license)
- **Stars:** 5,400+ on GitHub
- **Releases:** 126+ (active, frequent releases)
- **Latest release:** v0.56.0 (June 2, 2026)
- **Repository:** https://github.com/max-sixty/worktrunk
- **Documentation:** https://worktrunk.dev
- **Package managers:** Homebrew, Cargo, Winget (Windows), pacman (Arch Linux), Conda-Forge
- **Author:** max-sixty (Max)

## Detailed Guides

| File | Description |
|---|---|
| [installation.md](./installation.md) | All install methods, shell integration, platform notes |
| [configuration.md](./configuration.md) | User and project config reference (`worktrunk.toml`) |
| [cli-reference.md](./cli-reference.md) | All commands with flags and examples |
| [hooks.md](./hooks.md) | Hook types, lifecycle, template variables, recipes |
| [lifecycle.md](./lifecycle.md) | End-to-end workflow walkthrough |
| [opencode-integration.md](./opencode-integration.md) | OpenCode plugin, activity tracking, session mapping |
| [comparisons.md](./comparisons.md) | vs git worktree, CLI alternatives, TUIs |
| [best-practices.md](./best-practices.md) | Official and community best practices |
| [scripts-and-automation.md](./scripts-and-automation.md) | Shell aliases, wt aliases, custom subcommands, CI |
| [troubleshooting.md](./troubleshooting.md) | FAQ, common issues, platform notes |

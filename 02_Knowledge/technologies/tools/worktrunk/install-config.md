---
title: "Installing and configuring Worktrunk"
status: draft
author: "padawont"
date: 2026-08-20
tags: [git, worktrees, cli, configuration, install]
sources:
  - url: "https://github.com/max-sixty/worktrunk"
    title: "max-sixty/worktrunk GitHub README"
  - url: "https://worktrunk.dev/config/"
    title: "wt config docs"
last_audit_date: 2026-08-25
related_docs:
  - "./02_Knowledge/technologies/tools/worktrunk/overview.md"
  - "./02_Knowledge/technologies/tools/worktrunk/commands.md"
  - "./02_Knowledge/technologies/tools/worktrunk/automation.md"
---

# Installing and configuring Worktrunk

## Overview

Install Worktrunk from a package manager, then run `wt config shell install` so switching worktrees changes the shell's directory. User config holds personal preferences; project config (`.config/wt.toml`) holds team-shared settings.

## Details

### Install

| Platform | Command |
|---|---|
| macOS / Linux (Homebrew) | `brew install worktrunk && wt config shell install` |
| Cargo | `cargo install worktrunk && wt config shell install` |
| Windows | `winget install max-sixty.worktrunk` (installed as `git-wt` to avoid the `wt` Windows Terminal alias conflict) |
| Arch Linux | `sudo pacman -S worktrunk && wt config shell install` |
| Conda / Pixi | `conda install -c conda-forge worktrunk` or `pixi global install worktrunk` |

### Shell integration

Worktrunk needs shell integration to change directories when switching worktrees. `wt config shell install` sets it up; manual setup via `wt config shell init --help`. Without it, `wt switch` prints the target directory but cannot `cd`. On first run Worktrunk offers to install shell integration; on first commit it offers to configure a detected LLM tool.

### User config (`~/.config/worktrunk/config.toml`)

Personal preferences; created with `wt config create`. Key sections:

Example — abstract:

```toml
# Worktree path template (default: sibling "<repo>.<branch-sanitized>")
worktree-path = "{{ repo_path }}/../{{ repo }}.{{ branch | sanitize }}"

# LLM commit message generation
[commit.generation]
command = "claude -p --no-session-persistence --model=haiku --tools=''"

# Persistent wt list flags
[list]
summary = true
full = false

# Command defaults
[merge]
squash = true
[remove]
delete-branch = true
[switch]
cd = true
```

The path template supports variables `{{ repo_path }}`, `{{ repo }}`, `{{ owner }}`, `{{ remote_repo }}`, `{{ branch }}` and filters `sanitize`, `sanitize_db`, `codename(n)`, `hash`. Relative paths resolve from the repo root; `~` expands to home.

### Project config (`.config/wt.toml`)

Repository-scoped, committed and shared; created with `wt config create --project`. Holds hooks, dev server URL (`[list] url`), forge platform for self-hosted hosts (`[forge]`), `template-append` style guides, copy-ignored excludes, and aliases.

### Other config

- **Precedence**: `--config-set` > `WORKTRUNK_*` env vars > `[projects."<host>/<owner>/<repo>"]` entry > global keys. Hooks/aliases/excludes accumulate rather than replace.
- **Env vars**: all config keys override with `WORKTRUNK_` prefix (`WORKTRUNK_WORKTREE_PATH`, `WORKTRUNK_COMMIT__GENERATION__COMMAND`), plus `WORKTRUNK_BIN`, `WORKTRUNK_VERBOSE`, `NO_COLOR`, `RUST_LOG`.
- **Per-repo overrides**: `[projects."github.com/owner/repo"]` entries (wildcard `*` supported) scope settings to specific repos, e.g. `worktree-path` or per-repo hooks.
- **State**: `wt config state` manages cache, default-branch detection, markers, per-branch vars, and logs under `.git/wt/`.

## Sources / Further Reading

- GitHub README install section https://github.com/max-sixty/worktrunk
- `wt config` reference https://worktrunk.dev/config/
- Worktree path template details: https://worktrunk.dev/config/#worktree-path-template
- Commands: `./02_Knowledge/technologies/tools/worktrunk/commands.md` · Automation: `./02_Knowledge/technologies/tools/worktrunk/automation.md`.

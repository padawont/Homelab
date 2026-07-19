---
title: "Worktrunk Installation"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags: ["worktrunk", "installation"]
sources:
  - "https://github.com/max-sixty/worktrunk"
  - "https://crates.io/crates/worktrunk"
last_audit_date: 2026-06-07
---

# Installation

## Prerequisites

- **Git >= 2.5** (for worktree support; [installation guide](../../version-control/git/worktree/installation.md))
- **Rust/Cargo** (only required for the `cargo install` method)

## Install Methods

### Homebrew (macOS & Linux)

```bash
brew install worktrunk && wt config shell install
```

This installs the `worktrunk` formula from the official Homebrew tap. The `wt` binary is linked into `/opt/homebrew/bin/` (Apple Silicon) or `/usr/local/bin/` (Intel).

### Cargo (Rust toolchain)

```bash
cargo install worktrunk && wt config shell install
```

Installs from source via Rust's package manager. The `worktrunk` crate is published on [crates.io](https://crates.io/crates/worktrunk).

> **Tip:** To speed up future upgrades, install `cargo-binstall` and use `cargo binstall worktrunk` to download pre-built binaries instead of compiling from source.

### Windows Winget

```bash
winget install max-sixty.worktrunk
git-wt config shell install
```

On Windows, `wt` conflicts with the Windows Terminal executable (`wt.exe`). The Winget package installs Worktrunk as `git-wt` to avoid this conflict.

To use `wt` directly on Windows:
1. Open **Settings > Privacy & security > For developers > App Execution Aliases**
2. Disable the "Windows Terminal" alias
3. Verify with `wt --version`

### Arch Linux

```bash
sudo pacman -S worktrunk && wt config shell install
```

Worktrunk is available in the Arch community repository.

### Conda / Pixi (community-maintained)

**Conda:**

```bash
conda install -c conda-forge worktrunk && wt config shell install
```

**Pixi:**

```bash
pixi global install worktrunk && wt config shell install
```

The conda-forge feedstock is community-maintained and may lag slightly behind the latest release on crates.io and Homebrew.

## Shell Integration

### Why It Is Needed

Shell integration installs a hook that automatically changes your current directory when you switch worktrees with `wt switch`. Without this hook, `wt switch` creates the worktree but leaves you in the same directory -- you would need to manually `cd` to the new worktree path.

### Install Shell Integration

```bash
wt config shell install
```

This command adds an eval line to your shell config file (`.bashrc`, `.zshrc`, `.fishrc`, etc.) that registers a `chpwd` / `cd` hook to follow `wt switch`.

### Uninstall Shell Integration

```bash
wt config shell uninstall
```

### Supported Shells

- Bash
- Zsh
- Fish
- Nushell
- Any POSIX-compatible shell

## Verify Installation

### Check Version

```bash
wt --version
```

Example output: `wt 0.56.0`

### Check Help

```bash
wt help
```

Lists all available commands: `switch`, `list`, `merge`, `remove`, `config`, `step`, etc.

### Check Shell Integration

```bash
which wt
```

Should output the path to the installed binary (e.g., `/opt/homebrew/bin/wt` or `~/.cargo/bin/wt`).

## Upgrading

Re-run the same install command for your platform. For example:

| Method | Upgrade Command |
|---|---|
| Homebrew | `brew upgrade worktrunk` |
| Cargo | `cargo install worktrunk` |
| Winget | `winget upgrade max-sixty.worktrunk` |
| Arch Linux | `sudo pacman -Syu worktrunk` |
| Conda | `conda update -c conda-forge worktrunk` |

No additional steps are needed after upgrading -- shell integration persists across upgrades.

## Troubleshooting

### C Compilation Errors (Cargo Install)

If `cargo install worktrunk` fails with C compilation errors (typically related to `tree-sitter` or syntax highlighting dependencies):

```bash
cargo install worktrunk --no-default-features --features cli
```

This disables syntax highlighting (which requires native C libraries for tree-sitter grammars) and installs only the core CLI. Syntax highlighting in `wt list` will be disabled but all other functionality works normally.

### Binary Not Found After Install

Ensure the Cargo bin directory is in your `PATH`:

```bash
# Add to ~/.bashrc, ~/.zshrc, or equivalent
export PATH="$HOME/.cargo/bin:$PATH"
```

### Shell Integration Not Working

Re-run `wt config shell install` and restart your terminal session. Verify that the eval line was added to your shell config file.

### "wt: command not found" on Windows

The Winget package installs Worktrunk as `git-wt`. Use `git-wt --version` or disable the Windows Terminal alias to reclaim `wt` (see [Windows Winget](#windows-winget) above).

---
title: "direnv — Stdlib Reference"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["direnv", "stdlib", "reference"]
sources:
  - "https://direnv.net/man/direnv-stdlib.1.html"
last_audit_date: 2026-05-24
---

# Stdlib Functions

direnv provides a standard library of bash functions available inside `.envrc`. You can also define custom functions in `~/.config/direnv/direnvrc`.

## PATH Management

| Function | Description |
|---|---|
| `PATH_add <path>` | Prepends expanded path to `$PATH` |
| `PATH_rm <pattern> [<pattern>...]` | Removes directories matching shell patterns from `$PATH` |
| `MANPATH_add <path>` | Prepends path to `$MANPATH` |
| `path_add <varname> <path>` | Generic path prepend for any variable |

## Loading Other Files

| Function | Description |
|---|---|
| `dotenv [<path>]` | Load a `.env` file |
| `dotenv_if_exists [<path>]` | Load a `.env` file if it exists |
| `source_env <path>` | Load another `.envrc` (not security-checked) |
| `source_env_if_exists <path>` | Load another `.envrc` if it exists |
| `source_up [<filename>]` | Load the first matching file found walking up the tree |
| `source_up_if_exists [<filename>]` | Load the first `.envrc` found walking up the tree (no error if not found) |
| `source_url <url> <hash>` | Load a script from a URL (with integrity check) |
| `fetchurl <url> [<integrity-hash>]` | Fetch a URL to a file and output its path on stdout |

## Nix Integration

| Function | Description |
|---|---|
| `use nix [...]` | Load environment from `nix-shell` (uses `default.nix` or `shell.nix`) |
| `use flake [<installable>]` | Load environment from a Nix flake (like `nix develop`) |

## Language Layouts

| Function | Description |
|---|---|
| `layout go` | Appends `$(direnv_layout_dir)/go` to `GOPATH` and adds `$PWD/bin` to `$PATH` |
| `layout python [<exe>]` | Creates/loads a virtualenv in `$PWD/.direnv/python-$version` |
| `layout python3` | Shortcut for `layout python python3` |
| `layout node` | Adds `$PWD/node_modules/.bin` to `$PATH` |
| `layout ruby` | Sets `GEM_HOME` to `$PWD/.direnv/ruby/$version` |
| `layout pipenv` | Uses Pipfile-based virtualenv |
| `layout pyenv [<version>...]` | Uses pyenv-based virtualenv for specified versions |
| `layout julia` | Sets `JULIA_PROJECT` to current directory |
| `layout php` | Adds `$PWD/vendor/bin` to `$PATH` |
| `layout perl` | Sets up local::lib environment variables |
| `layout opam` | Loads OCaml environment via `opam env` |
| `use node [<version>]` | Loads a NodeJS version from `$NODE_VERSIONS` (optional, fuzzy-matched) |
| `use julia <version>` | Loads a specific Julia version from `$JULIA_VERSIONS` directory |
| `use rbenv` | Loads Ruby environment via rbenv |
| `rvm [...]` | Loads Ruby environment via RVM |
| `use guix [...]` | Load environment variables from `guix shell` |
| `use vim [<vimrc_file>]` | Prepends a vim script to `$DIRENV_EXTRA_VIMRC` for direnv.vim |

## Utilities

| Function | Description |
|---|---|
| `has <command>` | Returns 0 if command is available |
| `expand_path <rel> [<base>]` | Resolves relative path to absolute |
| `find_up <filename>` | Searches upward from cwd for a file |
| `user_rel_path <path>` | Shortens paths with `~` when possible |
| `load_prefix <path>` | Sets common `*PATH` variables for a prefix |
| `watch_file <path> [<path>...]` | Reload env when one or more files change |
| `watch_dir <dir>` | Reload env when any file in dir changes |
| `strict_env [<cmd>]` | Enable `set -eu` for .envrc (fail on errors and unset variables) |
| `unstrict_env [<cmd>]` | Disable `set -eu` for .envrc |
| `direnv_version <ver>` | Assert minimum direnv version |
| `env_vars_required <var> [...]` | Fail if any variable is unset or empty |
| `direnv_load <cmd>` | Apply environment from a child process |
| `direnv_apply_dump <file>` | Load environment from `direnv dump` output |
| `on_git_branch [<name>]` | Returns 0 if in a git branch |
| `semver_search <dir> <prefix> <ver>` | Find highest semver match in a directory |
| `require_allowed <path> [...]` | Require re-authorization if listed files change (direnv >= 2.38.0) |

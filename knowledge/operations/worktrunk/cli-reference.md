---
title: "Worktrunk CLI Reference"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags: ["worktrunk", "cli", "reference"]
sources:
  - url: "https://worktrunk.dev/switch/"
    title: "wt switch"
  - url: "https://worktrunk.dev/list/"
    title: "wt list"
  - url: "https://worktrunk.dev/remove/"
    title: "wt remove"
  - url: "https://worktrunk.dev/merge/"
    title: "wt merge"
  - url: "https://worktrunk.dev/config/"
    title: "wt config"
  - url: "https://worktrunk.dev/step/"
    title: "wt step"
  - url: "https://worktrunk.dev/hook/"
    title: "wt hook"
  - url: "https://worktrunk.dev/worktrunk/"
    title: "Worktrunk Overview"
last_audit_date: 2026-06-07
---

# Worktrunk CLI Reference

Comprehensive reference for all Worktrunk CLI commands, flags, arguments, and output formats.

## Global Options

These options are available on every `wt` command.

| Option | Description |
|---|---|
| `-C <path>` | Working directory for this command |
| `--config <path>` | User config file path override |
| `-v`, `--verbose` | Verbose output: info logs + hook/alias template variables on stderr |
| `-vv` | Debug output: also writes `trace.log`, `subprocess.log`, `diagnostic.md` to `.git/wt/logs/` |
| `-y`, `--yes` | Skip approval prompts |

Three verbosity levels exist. `-v` adds info-level output (hook output, alias template variable resolution) to stderr. `-vv` routes debug-level records to `trace.log` instead of stderr, keeping the terminal readable while the deep trace lands on disk, and also writes raw uncapped subprocess output to `subprocess.log` and a bundled diagnostic report to `diagnostic.md`.

`RUST_LOG` overrides the flag baseline when set (e.g., `RUST_LOG=debug wt -v` lifts `-v` to debug-on-stderr). This behavior is documented in the CLI help (`wt --help`) but not on the website.

---

## `wt switch`

Switch to a worktree; create if needed.

Worktrees are addressed by branch name; paths are computed from a configurable template. Unlike `git switch`, this navigates between worktrees rather than changing branches in place.

### Syntax

```
wt switch [OPTIONS] [BRANCH] [-- <EXECUTE_ARGS>...]
```

If `BRANCH` is omitted, opens an interactive picker.

### Arguments

| Argument | Description |
|---|---|
| `BRANCH` | Branch name or shortcut. Opens interactive picker if omitted. |
| `EXECUTE_ARGS` | Additional arguments for the `--execute` command (after `--`). Each argument is expanded for templates, then POSIX shell-escaped. |

### Options

| Option | Description |
|---|---|
| `-c`, `--create` | Create a new branch before switching |
| `-b`, `--base <BASE>` | Base branch to create from. Defaults to default branch. Supports shortcuts (`^`, `@`, `-`, `pr:{N}`, `mr:{N}`). |
| `-x`, `--execute <EXECUTE>` | Command to run after switch. Replaces the `wt` process with the command after switching. Supports hook template variables (`{{ branch }}`, `{{ worktree_path }}`, etc.) and filters. |
| `--clobber` | Remove stale (non-worktree) paths at the target location |
| `--no-cd` | Skip directory change after switching. Hooks still run normally. |
| `--no-hooks` | Skip all hooks |
| `--branches` | Include branches without worktrees in the interactive picker |
| `--remotes` | Include remote branches in the interactive picker |
| `--format <FORMAT>` | Output format. `text` (default) or `json`. JSON prints structured result to stdout for tool integration. |
| `-h`, `--help` | Print help |

### Shortcuts

| Shortcut | Meaning |
|---|---|
| `^` | Default branch (`main`/`master`) |
| `@` | Current branch/worktree |
| `-` | Previous worktree (like `cd -`) |
| `pr:{N}` | GitHub PR #N's branch |
| `mr:{N}` | GitLab MR !N's branch |

Shortcuts also apply to `--base`. For a fork PR/MR, the head commit is fetched and used as the base SHA without creating a tracking branch.

### Examples

```bash
wt switch feature-auth               # Switch to existing worktree
wt switch -                          # Previous worktree
wt switch --create new-feature        # Create new branch and worktree
wt switch --create hotfix --base production  # New branch from production
wt switch pr:123                      # Switch to PR #123's branch
wt switch https://github.com/owner/repo/pull/123  # By URL
wt switch --create -x claude feature  # Create and launch Claude Code
wt switch --create fix --base=@       # Branch from current HEAD
```

### Interactive Picker

When called without arguments, `wt switch` opens an interactive picker to browse and select worktrees with live preview.

**Keybindings:**

| Key | Action |
|---|---|
| `↑`/`↓` | Navigate worktree list |
| (type) | Filter worktrees |
| `Enter` | Switch to selected worktree |
| `Alt-c` | Create new worktree named as entered text |
| `Esc` | Cancel |
| `1`-`5` | Switch preview tab |
| `Alt-p` | Toggle preview panel |
| `Ctrl-u`/`Ctrl-d` | Scroll preview up/down |

**Preview tabs** (toggle with number keys):

1. **HEAD±** -- Diff of uncommitted changes
2. **log** -- Recent commits; commits already on the default branch have dimmed hashes
3. **main...±** -- Diff of changes since the merge-base with the default branch
4. **remote** -- Ahead/behind diff vs upstream tracking branch
5. **summary** -- LLM-generated branch summary (requires `[list] summary = true` and `[commit.generation]`)

Available on Unix only (macOS, Linux).

### PR/MR Support

The `pr:<number>` / `mr:<number>` shortcut and PR/MR web URL both resolve to the branch. For same-repo PRs/MRs, worktrunk switches to the branch directly. For fork PRs/MRs, it fetches the ref (`refs/pull/N/head` or `refs/merge-requests/N/head`) and configures `pushRemote` to the fork URL.

Requires `gh` (GitHub) or `glab` (GitLab) CLI to be installed and authenticated. Supports Gitea (experimental, via `tea` CLI) and Azure DevOps (experimental, via `az` CLI with `azure-devops` extension).

### Worktree Creation Flow

When creating a new worktree:

1. Runs `pre-switch` hooks, blocking until complete
2. Creates worktree at configured path
3. Switches to new directory
4. Runs `pre-start` hooks, blocking until complete
5. Spawns `post-start` and `post-switch` hooks in the background

### JSON Output Format

When `--format=json` is used, the output is a JSON object with fields describing the switch result (branch, path, status, etc.).

---

## `wt list`

List worktrees and their status. Shows uncommitted changes, divergence from the default branch and remote, and optional CI status and LLM summaries.

### Syntax

```
wt list [OPTIONS]
wt list <COMMAND>
```

### Subcommands

| Subcommand | Description |
|---|---|
| `statusline` | Single-line status for shell prompts |

### Options

| Option | Description |
|---|---|
| `--full` | Show CI status, line diffs since the merge-base, and LLM-generated summaries |
| `--branches` | Include branches without worktrees |
| `--remotes` | Include remote-only branches |
| `--format <FORMAT>` | Output format: `table` (default) or `json` |
| `--progressive` | Show fast info immediately, update with slow info as it arrives. Auto-enabled for TTY. Use `--no-progressive` to force buffered rendering. |
| `-h`, `--help` | Print help |

### Examples

```bash
wt list                          # Standard table view
wt list --full                   # Include CI, diff analysis, and LLM summaries
wt list --branches               # Include branches without worktrees
wt list --remotes                # Include remote-only branches
wt list --format=json            # JSON output for scripting
wt list statusline               # Single-line status
```

### Columns

| Column | Description |
|---|---|
| Branch | Branch name |
| Status | Compact symbols for working tree and branch state |
| HEAD | Uncommitted changes: `+added -deleted` lines |
| main | Commits ahead/behind default branch |
| main... | Line diffs since the merge-base with the default branch (`--full` only) |
| Summary | LLM-generated branch summary (`--full` only, requires config) |
| Remote | Commits ahead/behind tracking branch |
| CI | Pipeline status (`--full` only) |
| Path | Worktree directory |
| URL | Dev server URL from project config |
| Commit | Short hash (8 chars) |
| Age | Time since last commit |
| Message | Last commit message (truncated) |

### Status Symbols

**Working tree (first matching only):**

| Symbol | Meaning |
|---|---|
| `+` | Staged files |
| `!` | Modified files (unstaged) |
| `?` | Untracked files |

**Worktree state:**

| Symbol | Meaning |
|---|---|
| `✘` | Merge conflicts |
| `⤴` | Rebase in progress |
| `⤵` | Merge in progress |
| `/` | Branch without worktree |
| `⚑` | Branch-worktree mismatch |
| `⊟` | Prunable (directory missing) |
| `⊞` | Locked worktree |

**Default branch relation:**

| Symbol | Meaning |
|---|---|
| `^` | Is the default branch |
| `∅` | Orphan branch (no common ancestor) |
| `✗` | Would conflict if merged |
| `_` | Same commit as default, clean |
| `–` | Same commit, uncommitted changes |
| `⊂` | Content integrated into default |
| `↕` | Diverged from default |
| `↑` | Ahead of default |
| `↓` | Behind default |

**Remote relation:**

| Symbol | Meaning |
|---|---|
| `|` | In sync with remote |
| `⇅` | Diverged from remote |
| `⇡` | Ahead of remote |
| `⇣` | Behind remote |

Rows are dimmed when safe to delete (`_` same commit with clean working tree or `⊂` content integrated).

### CI Status Indicators

| Indicator | Meaning |
|---|---|
| ● green | All checks passed |
| ● blue | Checks running |
| ● red | Checks failed |
| ● yellow | Merge conflicts with base |
| ● gray | No checks configured |
| ⚠ yellow | Fetch error (rate limit, network) |
| (blank) | No upstream or no PR/MR |

### JSON Output

When `--format=json` is used, the output is an array of worktree/branch objects. Each object contains:

| Field | Type | Description |
|---|---|---|
| `branch` | string/null | Branch name (null for detached HEAD) |
| `path` | string | Worktree path |
| `kind` | string | `"worktree"` or `"branch"` |
| `commit` | object | Commit info: `sha`, `short_sha`, `message`, `timestamp` |
| `working_tree` | object | `staged`, `modified`, `untracked`, `renamed`, `deleted` booleans; `diff` object |
| `main_state` | string | Relation to default branch: `is_main`, `orphan`, `would_conflict`, `empty`, `same_commit`, `integrated`, `diverged`, `ahead`, `behind` |
| `integration_reason` | string | Why branch is integrated: `ancestor`, `trees-match`, `no-added-changes`, `merge-adds-nothing`, `patch-id-match` |
| `operation_state` | string | `"conflicts"`, `"rebase"`, `"merge"` |
| `main` | object | `ahead`, `behind` counts; `diff` object |
| `remote` | object | `name`, `branch`, `ahead`, `behind` |
| `worktree` | object | `state`, `reason`, `detached` |
| `is_main` | boolean | Is the main worktree |
| `is_current` | boolean | Is the current worktree |
| `is_previous` | boolean | Previous worktree from `wt switch` |
| `ci` | object | `status` (passed/running/failed/conflicts/no-ci/error), `source`, `stale`, `url` |
| `url` | string | Dev server URL |
| `url_active` | boolean | Whether the URL's port is listening |
| `summary` | string | LLM-generated branch summary |
| `statusline` | string | Pre-formatted status with ANSI colors |
| `symbols` | string | Raw status symbols without colors |
| `vars` | object | Per-branch variables from `wt config state vars` |

### Useful jq Queries

```bash
# Current worktree path
wt list --format=json | jq -r '.[] | select(.is_current) | .path'

# Branches with uncommitted changes
wt list --format=json | jq '.[] | select(.working_tree.modified)'

# Worktrees with merge conflicts
wt list --format=json | jq '.[] | select(.operation_state == "conflicts")'

# Branches ahead of main
wt list --format=json | jq '.[] | select(.main.ahead > 0) | .branch'

# Integrated branches (safe to remove)
wt list --format=json | jq '.[] | select(.main_state == "integrated" or .main_state == "empty") | .branch'

# Branches without worktrees
wt list --format=json --branches | jq '.[] | select(.kind == "branch") | .branch'
```

#### `statusline` Subcommand

Outputs a single-line status string suitable for shell prompts (e.g., `PS1`, `$PROMPT`). Shows current branch, worktree status symbols, and ahead/behind information.

---

## `wt remove`

Remove worktree; delete branch if merged. Defaults to the current worktree.

### Syntax

```
wt remove [OPTIONS] [BRANCHES]...
```

### Arguments

| Argument | Description |
|---|---|
| `BRANCHES` | One or more branch names to remove. Defaults to the current worktree. |

### Options

| Option | Description |
|---|---|
| `--no-delete-branch` | Keep the branch after removing the worktree |
| `-D`, `--force-delete` | Delete unmerged branches (force branch deletion) |
| `-f`, `--force` | Force worktree removal even with uncommitted changes (staged, modified, untracked) |
| `--foreground` | Run removal in the foreground (block until complete) |
| `--no-hooks` | Skip hooks |
| `--format <FORMAT>` | Output format: `text` (default) or `json` |
| `-h`, `--help` | Print help |

### Examples

```bash
wt remove                        # Remove current worktree
wt remove feature-branch         # Remove specific worktree
wt remove old-feature another    # Remove multiple worktrees
wt remove --no-delete-branch     # Keep the branch
wt remove -D experimental        # Force-delete unmerged branch
wt remove --force                # Remove dirty worktree
wt remove --force -D             # Both force flags
wt remove /path/to/detached      # Remove detached HEAD worktree (by path)
```

### Branch Cleanup

By default, branches are deleted when they are integrated into the default branch. Worktrunk checks six conditions (in order of increasing cost):

1. **Same commit** -- Branch HEAD equals the default branch (`_` in `wt list`)
2. **Ancestor** -- Branch is in target's history (fast-forward or rebase) (`⊂`)
3. **No added changes** -- Three-dot diff (`target...branch`) is empty (`⊂`)
4. **Trees match** -- Branch tree SHA equals target tree SHA (`⊂`)
5. **Merge adds nothing** -- Simulated merge produces the same tree as target (`⊂`)
6. **Patch-id match** -- Branch's diff matches a single squash-merge commit on target (`⊂`)

### Force Flags

| Flag | Scope | When to use |
|---|---|---|
| `--force` (`-f`) | Worktree | Worktree has uncommitted changes |
| `-D` (`--force-delete`) | Branch | Branch has unmerged commits |

### Background Removal

Removal runs in the background by default. The worktree is renamed into `.git/wt/trash/` (instant same-filesystem rename), git metadata is pruned, the branch is deleted, and a detached `rm -rf` finishes cleanup. Cross-filesystem worktrees fall back to `git worktree remove`.

After each `wt remove`, entries in `.git/wt/trash/` older than 24 hours are swept.

### Detached HEAD Worktrees

Pass the worktree path instead of a branch name: `wt remove /path/to/worktree`.

---

## `wt merge`

Merge current branch into the target branch. Squash and rebase, fast-forward the target branch, remove the worktree.

Unlike `git merge`, this merges the current branch into the target branch -- not the target into current. Similar to clicking "Merge pull request" on GitHub, but locally. The target defaults to the default branch.

### Syntax

```
wt merge [OPTIONS] [TARGET]
```

### Arguments

| Argument | Description |
|---|---|
| `TARGET` | Target branch. Defaults to default branch. |

### Options

| Option | Description |
|---|---|
| `--no-squash` | Skip commit squashing (preserve individual commits) |
| `--no-commit` | Skip commit and squash; rebase still runs unless `--no-rebase` is passed. Requires a clean working tree. |
| `--no-rebase` | Skip rebase (fail if not already rebased) |
| `--no-remove` | Keep worktree after merge |
| `--no-ff` | Create a merge commit (semi-linear history with rebased commits plus merge commit) |
| `--stage <STAGE>` | What to stage before committing: `all` (default), `tracked`, or `none` |
| `--no-hooks` | Skip hooks |
| `--format <FORMAT>` | Output format: `text` (default) or `json` |
| `-h`, `--help` | Print help |

### Merge Pipeline

`wt merge` runs these steps in order:

1. **Commit** -- Pre-commit hooks run, then uncommitted changes are committed. Skipped when squashing (the default) -- changes are staged during the squash step instead. Post-commit hooks run in background.
2. **Squash** -- Combines all commits since target into one (like GitHub's "Squash and merge"). A backup ref is saved to `refs/wt-backup/<branch>`. Skipped with `--no-squash`.
3. **Rebase** -- Rebases onto target if behind. Conflicts abort immediately. Skipped with `--no-rebase`.
4. **Pre-merge hooks** -- Hooks run after rebase, before merge. Failures abort.
5. **Merge** -- Fast-forward merge to the target branch. With `--no-ff`, a merge commit is created.
6. **Pre-remove hooks** -- Hooks run before removing worktree.
7. **Cleanup** -- Removes the worktree and branch (unless `--no-remove`).
8. **Post-remove + post-merge hooks** -- Run in background after cleanup.

### Examples

```bash
wt merge                           # Merge current branch to default
wt merge develop                   # Merge to develop branch
wt merge --no-squash               # Preserve commit history
wt merge --no-remove               # Keep worktree after merge
wt merge --no-ff                   # Create merge commit
wt merge --no-commit               # Skip commit/squash, rebase only
wt merge --stage=tracked           # Stage only tracked files
```

### Local CI

Pre-merge hooks enable local validation before merging. For personal projects, this replaces the need for remote CI for the basic validation step:

```toml
[[pre-merge]]
test = "cargo test"
lint = "cargo clippy"
```

---

## `wt config`

Manage user and project configs. Includes shell integration, hooks, and saved state.

### Syntax

```
wt config [OPTIONS] <COMMAND>
```

### Subcommands

| Subcommand | Description |
|---|---|
| `shell` | Shell integration setup (install/uninstall) |
| `create` | Create configuration file |
| `show` | Show configuration files and locations |
| `update` | Update deprecated config settings |
| `approvals` | Manage command approvals |
| `alias` | Inspect and preview aliases |
| `plugins` | Plugin management |
| `state` | Manage internal data and cache |

### Configuration File Locations

| Config | Location |
|---|---|
| User config | `~/.config/worktrunk/config.toml` (or `$XDG_CONFIG_HOME`) on macOS/Linux; `%APPDATA%\worktrunk\config.toml` on Windows |
| Project config | `.config/wt.toml` (in repo root) |
| Approvals | `~/.config/worktrunk/approvals.toml` |
| System config | Platform-specific; check `wt config show` |

---

### `wt config shell`

Shell integration setup. Required for `wt switch` to change directories.

#### Subcommands

| Subcommand | Description |
|---|---|
| `install` | Install shell integration |
| `init` | Show init script (for manual setup) |
| `uninstall` | Remove shell integration |

Supports bash, zsh, fish, nushell, and PowerShell.

```bash
wt config shell install            # Install shell integration
wt config shell init --help        # Manual setup instructions
```

---

### `wt config create`

Create configuration file with documented examples.

```bash
wt config create                   # Create user config
wt config create --project         # Create project config (.config/wt.toml)
```

---

### `wt config show`

Show configuration files and locations.

```bash
wt config show                     # Show config contents and locations
wt config show --full              # Run diagnostic checks
wt config show --format=json       # JSON output
```

With `--full`, runs diagnostic checks:
- CI tool status (whether `gh` or `glab` is installed and authenticated)
- Commit generation (whether the LLM command can generate commit messages)
- Version check (whether a newer version is available on GitHub)

---

### `wt config update`

Update deprecated config settings to their current equivalents.

---

### `wt config approvals`

Manage command approvals for project hooks and aliases.

#### Subcommands

| Subcommand | Description |
|---|---|
| `add` | Store approvals in approvals.toml |
| `clear` | Clear approved commands |

```bash
wt config approvals add            # Pre-approve all hook/alias commands
wt config approvals clear          # Clear for current project
wt config approvals clear --global # Clear global approvals
```

---

### `wt config alias`

Inspect and preview aliases.

#### Subcommands

| Subcommand | Description |
|---|---|
| `show [name]` | Show an alias template, or all aliases |
| `dry-run <name>` | Preview an alias invocation with template expansion |

```bash
wt config alias show               # Show all alias templates
wt config alias show deploy        # Show specific alias template
wt config alias dry-run deploy     # Preview rendered command
wt config alias dry-run deploy -- --env=staging
```

---

### `wt config plugins`

Plugin management (for future extensibility).

---

### `wt config state`

Manage internal data and cache stored in `.git/`.

#### Subcommands

| Subcommand | Description |
|---|---|
| `get` | Get all stored state |
| `clear` | Clear all stored state |
| `default-branch` | Default branch detection and override |
| `previous-branch` | Previous branch (for `wt switch -`) |
| `logs` | Operation and debug logs |
| `hints` | One-time hints shown in this repo |
| `ci-status` | CI status cache |
| `marker` | Branch markers (custom status text/emoji) |
| `vars` | [experimental] Custom variables per branch |

---

#### `wt config state default-branch`

Default branch detection and override.

```bash
wt config state default-branch           # Get current default branch
wt config state default-branch set main  # Override
wt config state default-branch clear     # Clear cache (re-detect)
```

Detection order:
1. Worktrunk cache (`git config worktrunk.default-branch`)
2. Git cache (primary remote HEAD, e.g., `origin/HEAD`)
3. Remote query (`git ls-remote`)
4. Local inference (heuristics: single branch, `symbolic-ref HEAD`, `init.defaultBranch`, common names)

---

#### `wt config state logs`

Operation and debug logs. Three kinds of logs:

- **Command log** (`commands.jsonl`) -- All hook executions and LLM commands, one JSON object per line (rotates at 1MB)
- **Hook output logs** -- Per-branch, per-hook-type log files for background hooks
- **Diagnostic files** -- `trace.log`, `subprocess.log`, `diagnostic.md` (created with `-vv`)

```bash
wt config state logs                         # List all log files
wt config state logs --format=json           # Structured JSON output
wt config state logs clear                   # Clear all logs
```

---

#### `wt config state ci-status`

CI status cache for display in `wt list`.

```bash
wt config state ci-status                    # Get CI status for current branch
wt config state ci-status clear feature      # Clear cache for a branch
wt config state ci-status clear --all        # Clear all CI cache
```

Status values: `passed`, `running`, `failed`, `conflicts`, `no-ci`, `error`.

---

#### `wt config state marker`

Branch markers -- custom status text or emoji shown in the `wt list` Status column.

```bash
wt config state marker                       # Get current branch marker
wt config state marker set "WIP"             # Set marker
wt config state marker set "review" --branch=feature  # Set for specific branch
wt config state marker clear                 # Clear marker
```

---

#### `wt config state vars`

[experimental] Custom variables per branch. Values available in hook templates as `{{ vars.<key> }}`.

```bash
wt config state vars set env=staging         # Set variable
wt config state vars get env                 # Get value
wt config state vars list                    # List all keys
wt config state vars clear                   # Clear all keys
```

Template access example:

```toml
[post-start]
dev = "ENV={{ vars.env | default('development') }} npm start"
```

---

## `wt step`

Run individual operations. The building blocks of `wt merge` -- commit, squash, rebase, push -- plus standalone utilities.

### Syntax

```
wt step [OPTIONS] <COMMAND>
```

### Subcommands

| Subcommand | Description |
|---|---|
| `commit` | Stage and commit with LLM-generated message |
| `squash` | Squash commits since branching with LLM-generated message |
| `rebase` | Rebase onto target branch |
| `push` | Fast-forward target to current branch |
| `diff` | Show all changes since branching |
| `copy-ignored` | Copy gitignored files to another worktree |
| `eval` | [experimental] Evaluate a template expression |
| `for-each` | [experimental] Run command in each worktree |
| `promote` | [experimental] Swap a branch into the main worktree |
| `prune` | [experimental] Remove worktrees merged into the default branch |
| `relocate` | [experimental] Move worktrees to expected paths |
| `tether` | [experimental] Run a command; kill its process tree when worktree is removed |
| `<alias>` | Run a configured command alias |

---

### `wt step commit`

Stage and commit with LLM-generated message.

#### Syntax

```
wt step commit [OPTIONS]
```

#### Options

| Option | Description |
|---|---|
| `-b`, `--branch <BRANCH>` | Branch to operate on (defaults to current worktree) |
| `--stage <STAGE>` | What to stage: `all` (default), `tracked`, or `none` |
| `--dry-run` | Preview prompt, command, and generated message without committing |
| `--no-hooks` | Skip hooks |
| `--format <FORMAT>` | Output format: `text` (default) or `json` |

```bash
wt step commit                     # Stage all and commit with LLM message
wt step commit --stage=tracked     # Stage only tracked files
wt step commit --dry-run           # Preview without committing
```

---

### `wt step squash`

Squash commits since branching. Stages changes and generates message with LLM.

#### Syntax

```
wt step squash [OPTIONS] [TARGET]
```

#### Options

| Option | Description |
|---|---|
| `TARGET` | Target branch (defaults to default branch) |
| `--stage <STAGE>` | What to stage: `all` (default), `tracked`, or `none` |
| `--dry-run` | Preview without squashing |
| `--no-hooks` | Skip hooks |
| `--format <FORMAT>` | Output format: `text` (default) or `json` |

```bash
wt step squash                     # Squash all commits into one
wt step squash --dry-run           # Preview squash message
```

---

### `wt step rebase`

Rebase onto target branch.

```bash
wt step rebase                     # Rebase onto default branch
```

---

### `wt step push`

Fast-forward target to current branch.

```bash
wt step push                       # Push changes to default branch
```

---

### `wt step diff`

Show all changes since branching. Includes committed, staged, unstaged, and untracked files.

#### Syntax

```
wt step diff [OPTIONS] [TARGET] [-- <EXTRA_ARGS>...]
```

#### Options

| Option | Description |
|---|---|
| `TARGET` | Target branch (defaults to default branch) |
| `-b`, `--branch <BRANCH>` | Branch to operate on |
| `EXTRA_ARGS` | Extra arguments forwarded to `git diff` |

```bash
wt step diff                       # Full diff since branching
wt step diff -- --stat             # Summary only
wt step diff --branch feature      # Diff another worktree's branch
wt step diff | delta               # Pipe through delta
```

---

### `wt step copy-ignored`

Copy gitignored files to another worktree. Eliminates cold starts by copying build caches and dependencies.

#### Syntax

```
wt step copy-ignored [OPTIONS]
```

#### Options

| Option | Description |
|---|---|
| `--from <FROM>` | Source worktree branch (defaults to main worktree) |
| `--to <TO>` | Destination worktree branch (defaults to current worktree) |
| `--dry-run` | Show what would be copied |
| `--force` | Overwrite existing files in destination |
| `--format <FORMAT>` | Output format: `text` (default) or `json` |

```bash
wt step copy-ignored               # Copy from main to current worktree
wt step copy-ignored --dry-run     # Preview what would be copied
wt step copy-ignored --force       # Overwrite existing files
```

**Features:**
- Uses copy-on-write (reflink) when available for space-efficient copies
- Handles nested `.gitignore` files, global excludes, and `.git/info/exclude`
- Skips existing files by default (safe to re-run)
- `--force` overwrites existing files

Uses `.worktreeinclude` file with gitignore-style patterns to limit what gets copied. Built-in exclusions: VCS metadata (`.bzr/`, `.hg/`, `.jj/`, `.pijul/`, `.sl/`, `.svn/`) and tool-state directories (`.conductor/`, `.entire/`, `.worktrees/`).

---

### `wt step eval`

[experimental] Evaluate a template expression. Prints the result to stdout for use in scripts and shell substitutions.

#### Syntax

```
wt step eval [OPTIONS] <TEMPLATE>
```

#### Options

| Option | Description |
|---|---|
| `--dry-run` | Show template variables and expanded result |

```bash
wt step eval '{{ branch | hash_port }}'                # Get port for current branch
wt step eval '{{ branch | sanitize_db }}'              # Database-safe identifier
wt step eval --dry-run '{{ branch }}'                  # Show available variables
```

---

### `wt step for-each`

[experimental] Run command in each worktree. Executes sequentially with real-time output; continues on failure.

#### Syntax

```
wt step for-each [OPTIONS] -- <ARGS>...
```

#### Options

| Option | Description |
|---|---|
| `--format <FORMAT>` | Output format: `text` (default) or `json` |

```bash
wt step for-each -- git status --short                 # Status in all worktrees
wt step for-each -- echo 'Branch: {{ branch }}'        # Template variables
wt step for-each -- sh -c 'git pull --autostash'       # Shell wrapper for pipes
```

Context JSON is piped to stdin for scripts that need structured data.

---

### `wt step promote`

[experimental] Swap a branch into the main worktree. Exchanges branches and gitignored files between two worktrees.

#### Syntax

```
wt step promote [OPTIONS] [BRANCH]
```

#### Options

| Option | Description |
|---|---|
| `BRANCH` | Branch to promote to main worktree (defaults to current branch or default branch) |

```bash
wt step promote feature            # Swap feature branch into main worktree
wt step promote                    # Restore default branch
```

Requirements: both worktrees must be clean; the branch must have an existing worktree.

---

### `wt step prune`

[experimental] Remove worktrees merged into the default branch.

#### Syntax

```
wt step prune [OPTIONS]
```

#### Options

| Option | Description |
|---|---|
| `--dry-run` | Show what would be removed |
| `--min-age <MIN_AGE>` | Skip worktrees younger than this (default: `1d`) |
| `--foreground` | Run in foreground |
| `--format <FORMAT>` | Output format: `text` (default) or `json` |

```bash
wt step prune                      # Remove all merged worktrees
wt step prune --dry-run            # Preview
wt step prune --min-age=0s         # No age guard
wt step prune --min-age=2d         # Skip worktrees younger than 2 days
```

Locked worktrees and the main worktree are always skipped. Pre-remove and post-remove hooks run for each removal.

---

### `wt step relocate`

[experimental] Move worktrees to expected paths. Relocates worktrees whose path doesnt match the `worktree-path` template.

#### Syntax

```
wt step relocate [OPTIONS] [BRANCHES]...
```

#### Options

| Option | Description |
|---|---|
| `BRANCHES` | Worktrees to relocate (defaults to all mismatched) |
| `--dry-run` | Show what would be moved |
| `--commit` | Commit uncommitted changes before relocating |
| `--clobber` | Backup non-worktree paths at target locations |
| `--format <FORMAT>` | Output format: `text` (default) or `json` |

```bash
wt step relocate                   # Move all mismatched worktrees
wt step relocate --dry-run         # Preview
wt step relocate --commit --clobber  # Auto-commit and clobber blockers
wt step relocate feature bugfix    # Move specific worktrees
```

---

### `wt step tether`

[experimental] Run a command; kill its whole process tree when its worktree is removed. Teardown is automatic, with SIGTERM then SIGKILL.

#### Syntax

```
wt step tether [OPTIONS] -- <COMMAND>...
```

```bash
wt step tether -- npm run dev      # Run dev server, auto-kill on removal
wt step tether -- sh -c 'PORT=$P npm run dev | tee dev.log'
```

Common use: `post-start` hooks for dev servers:

```toml
[post-start]
server = "wt step tether -- npm run dev -- --port {{ branch | hash_port }}"
```

---

## `wt hook`

Run configured hooks. Hooks are shell commands that run at key points in the worktree lifecycle.

### Syntax

```
wt hook [OPTIONS] <COMMAND>
```

### Subcommands (Hook Types)

| Subcommand | Lifecycle | Blocks? |
|---|---|---|
| `show` | -- | N/A |
| `pre-switch` | switch | Yes |
| `post-switch` | switch | No (background) |
| `pre-start` | create | Yes |
| `post-start` | create | No (background) |
| `pre-commit` | commit | Yes |
| `post-commit` | commit | No (background) |
| `pre-merge` | merge | Yes |
| `post-merge` | merge | No (background) |
| `pre-remove` | remove | Yes |
| `post-remove` | remove | No (background) |

### Options

| Option | Description |
|---|---|
| `--yes` | Skip approval prompts |
| `--no-hooks` | Skip hooks |
| `-h`, `--help` | Print help |

### Examples

```bash
wt hook pre-merge                  # Run all pre-merge hooks
wt hook pre-merge test             # Run hooks named "test"
wt hook pre-merge user:            # Run all user hooks only
wt hook pre-merge project:         # Run all project hooks only
wt hook pre-merge user:test        # Run only user's "test" hook
wt hook pre-merge --yes            # Skip approval prompts
wt hook pre-start --branch=feature/test  # Override template variable
wt hook post-start                 # Run post-start hooks
wt hook pre-merge -- --extra       # Forward tokens into {{ args }}
```

### Passing Values

```
--KEY=VALUE    # Binds KEY if referenced in template, else forwards to {{ args }}
--var KEY=VALUE  # Force-bind (deprecated)
--             # Everything after -- forwards to {{ args }}
```

### Hook Execution Order During `wt merge`

pre-commit → post-commit → pre-merge → pre-remove → post-remove + post-merge

### Security

Project hooks require approval on first run. Approvals are saved to `~/.config/worktrunk/approvals.toml`. If a command changes, new approval is required. Use `--yes` to bypass prompts in CI.

---

## `wt init`

Initialize Worktrunk in a bare repository. Required when working with bare repos so Worktrunk can determine the repository layout and configure worktree paths correctly.

### Syntax

```
wt init [OPTIONS]
```

This command sets up the necessary Worktrunk configuration for bare repositories. After initialization, the `worktree-path` template should reference paths relative to the bare repo's parent directory. Example configuration for bare repos:

```toml
worktree-path = "{{ repo_path }}/../{{ branch | sanitize }}"
```

---

## Aliases (`wt <alias>`)

Aliases are command templates configured in `[aliases]` in user or project config. They run as `wt <name>`.

### Configuration

```toml
[aliases]
deploy = "fly deploy --config=fly.{{ env }}.toml --app=myapp-{{ branch }}"
open = "open http://localhost:{{ branch | hash_port }}"
since-main = "git log --oneline {{ default_branch }}..HEAD"
```

### Usage

```bash
wt deploy --env=staging            # Runs the deploy alias
wt open                            # Opens dev server URL
wt since-main                      # Shows commits since main
```

### Template Support

Aliases use the same template engine as hooks: variables, filters, functions, and `--KEY=VALUE` smart routing (bind if the template references `KEY`, else forward to `{{ args }}`).

### Multi-Step Pipelines

```toml
[[aliases.release]]
test = "cargo test"

[[aliases.release]]
build = "cargo build --release"
package = "cargo package --no-verify"

[[aliases.release]]
publish = "cargo publish {{ args }}"
```

### Resolution Order

`wt <name>` resolves to:
1. Built-in command first
2. Alias from config second
3. Custom subcommand on PATH third

---

## Custom Subcommands (`wt-<name>`)

Any executable named `wt-<name>` on `PATH` becomes available as `wt <name>`, the same pattern git uses for `git-foo`.

```
wt sync origin              # Runs: wt-sync origin
wt -C /tmp/repo sync        # -C is forwarded
```

Arguments pass through verbatim, stdio is inherited, and the child's exit code propagates unchanged.

### Example

- `worktrunk-sync` -- rebases stacked worktree branches in dependency order. Install with `cargo install worktrunk-sync`, then `wt sync`.

---

## Configuration File Reference

### User Config (`~/.config/worktrunk/config.toml`)

Key sections and their options:

```toml
# Worktree path template
worktree-path = ".worktrees/{{ branch | sanitize }}"

# LLM commit message generation
[commit.generation]
command = "claude -p --no-session-persistence --model=haiku"
template = "..."  # minijinja template
squash-template = "..."  # minijinja template for squash
template-append = "..."  # appended to default template (user guidance)

[commit]
stage = "all"  # all, tracked, or none

[list]
summary = false
full = false
branches = false
remotes = false
task-timeout-ms = 0   # Kill individual git commands after N ms; 0 disables
timeout-ms = 0        # Wall-clock budget for the entire collect phase; 0 disables

[merge]
squash = true
commit = true
rebase = true
remove = true
verify = true
ff = true

[remove]
delete-branch = true

[switch]
cd = true

[switch.picker]
pager = "delta --paging=never"

[step.copy-ignored]
exclude = []

[aliases]
greet = "echo Hello from {{ branch }}"

[projects."github.com/user/repo"]
worktree-path = ".worktrees/{{ branch | sanitize }}"
```

### Project Config (`.config/wt.toml`)

Shared team settings, checked into version control:

```toml
[pre-start]
deps = "npm ci"

[post-start]
server = "npm run dev -- --port {{ branch | hash_port }}"

[pre-merge]
test = "npm test"

[list]
url = "http://localhost:{{ branch | hash_port }}"

[forge]
platform = "github"

[commit.generation]
template-append = "- Use conventional commits (feat:, fix:, docs:, …)"

[step.copy-ignored]
exclude = [".cache/", ".turbo/"]

[aliases]
deploy = "make deploy BRANCH={{ branch }}"
```

---

## Environment Variables

All user config options can be overridden with `WORKTRUNK_` prefix. Nested config uses double underscores:

| Config | Environment Variable |
|---|---|
| `worktree-path` | `WORKTRUNK_WORKTREE_PATH` |
| `commit.generation.command` | `WORKTRUNK_COMMIT__GENERATION__COMMAND` |
| `commit.stage` | `WORKTRUNK_COMMIT__STAGE` |

Other variables:

| Variable | Purpose |
|---|---|
| `WORKTRUNK_BIN` | Override binary path for shell wrappers |
| `WORKTRUNK_CONFIG_PATH` | Override user config file location |
| `WORKTRUNK_SYSTEM_CONFIG_PATH` | Override system config file location |
| `WORKTRUNK_PROJECT_CONFIG_PATH` | Override project config file location |
| `WORKTRUNK_DIRECTIVE_CD_FILE` | Internal: set by shell wrappers for cd |
| `WORKTRUNK_DIRECTIVE_EXEC_FILE` | Internal: set by shell wrappers for exec |
| `WORKTRUNK_SHELL` | Internal: shell type indicator |
| `WORKTRUNK_MAX_CONCURRENT_COMMANDS` | Max parallel git commands (default: 32) |
| `WORKTRUNK_FOREGROUND` | Internal: background hook context flag |
| `NO_COLOR` | Disable colored output |
| `CLICOLOR_FORCE` | Force colored output |
| `XDG_CONFIG_DIRS` | System config directories (default: `/etc/xdg`) |

---

## Template Variables

Available in hooks, aliases, and `worktree-path` templates.

| Kind | Variable | Description |
|---|---|---|
| **active** | `{{ branch }}` | Branch name |
| | `{{ worktree_path }}` | Worktree path |
| | `{{ worktree_name }}` | Worktree directory name |
| | `{{ commit }}` | Branch HEAD SHA |
| | `{{ short_commit }}` | Abbreviated SHA |
| | `{{ upstream }}` | Branch upstream (if tracking) |
| **operation** | `{{ base }}` | Base branch name (switch/create) |
| | `{{ base_worktree_path }}` | Base worktree path |
| | `{{ target }}` | Target branch name |
| | `{{ target_worktree_path }}` | Target worktree path |
| | `{{ pr_number }}` | PR/MR number |
| | `{{ pr_url }}` | PR/MR web URL |
| **repo** | `{{ repo }}` | Repository directory name |
| | `{{ repo_path }}` | Absolute path to repo root |
| | `{{ owner }}` | Primary remote owner path |
| | `{{ primary_worktree_path }}` | Primary worktree path |
| | `{{ default_branch }}` | Default branch name |
| | `{{ remote }}` | Primary remote name |
| | `{{ remote_url }}` | Remote URL |
| **exec** | `{{ cwd }}` | Directory where the hook runs |
| | `{{ hook_type }}` | Hook type being run |
| | `{{ hook_name }}` | Hook command name |
| | `{{ args }}` | CLI tokens forwarded |
| **user** | `{{ vars.<key> }}` | Per-branch variables |

## Template Filters

| Filter | Example | Description |
|---|---|---|
| `sanitize` | `{{ branch | sanitize }}` | Replace `/` and `\` with `-` |
| `sanitize_db` | `{{ branch | sanitize_db }}` | Database-safe identifier (lowercase, underscores, hash suffix, max 48 chars) |
| `sanitize_hash` | `{{ branch | sanitize_hash }}` | Filesystem-safe with hash suffix for uniqueness |
| `hash` | `{{ branch | hash }}` | 3-character base36 digest |
| `hash_port` | `{{ branch | hash_port }}` | Hash to port 10000-19999 |
| `dirname` | `{{ repo_path | dirname }}` | Strip last path component |
| `basename` | `{{ repo_path | basename }}` | Keep only last path component |
| `codename(n)` | `{{ branch | codename(2) }}` | Deterministic friendly words |

## Template Functions

| Function | Example | Description |
|---|---|---|
| `worktree_path_of_branch(branch)` | `{{ worktree_path_of_branch("main") }}` | Look up worktree path for a branch name |

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | General error (hook failure, git error, etc.) |
| 2 | Usage error (invalid flags, missing arguments) |
| 130 | Interrupted (Ctrl+C / SIGINT) |

---

## See Also

- [Configuration](./configuration.md) — User and project config reference (`worktrunk.toml`)
- [Hooks Reference](./hooks.md) — Hook types, lifecycle, template variables, recipes

---
title: "Worktrunk Configuration"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags: ["worktrunk", "configuration", "toml"]
sources:
  - url: "https://worktrunk.dev/config/"
    title: "Worktrunk Config Reference"
last_audit_date: 2026-06-07
---

# Worktrunk Configuration

Comprehensive reference for Worktrunk's configuration system, covering config file locations, all TOML sections, environment variable overrides, and state management commands.

## Configuration File Locations

Worktrunk reads configuration from three tiers, each with a distinct purpose and commit policy:

| File | Default Location | Purpose | Committed |
|---|---|---|---|
| **User config** | `~/.config/worktrunk/config.toml` | Personal preferences — worktree layout, LLM commit config, aliases | No |
| **Project config** | `.config/wt.toml` | Shared team settings — hooks, dev server URL, forge platform, aliases | Yes |
| **System config** | `/etc/xdg/worktrunk/config.toml` | Organization-wide defaults deployed by IT/admin | No |

On macOS and Linux, the user config path respects `$XDG_CONFIG_HOME` if set. On Windows, it lives at `%APPDATA%\worktrunk\config.toml`. The system config path follows `$XDG_CONFIG_DIRS` (default: `/etc/xdg`).

Run `wt config show` to inspect all active config files, their locations, and the effective merged configuration. Use `--full` to run diagnostic checks on CI tools, commit generation, and version availability.

### Creating Config Files

```
# Create user config with documented examples
wt config create

# Create project config for shared team settings
wt config create --project
```

The project config is created at `.config/wt.toml` relative to the repository root and is intended to be committed to version control.

## User Configuration (`~/.config/worktrunk/config.toml`)

The user config holds personal developer preferences. Create with `wt config create`. All values shown below are defaults unless noted otherwise.

### `worktree-path` — Worktree Location Template

Controls where new git worktrees are created. Value is a path template with variables and optional Jinja-like filters.

**Template variables:**

| Variable | Description | Example |
|---|---|---|
| `{{ repo_path }}` | Absolute path to the repository root | `/Users/me/code/myproject` |
| `{{ repo }}` | Repository directory name | `myproject` |
| `{{ owner }}` | Primary remote owner path (may include subgroups) | `group/subgroup` |
| `{{ branch }}` | Raw branch name | `feature/auth` |

**Filters:**

| Filter | Description | Example Output |
|---|---|---|
| `sanitize` | Filesystem-safe: `/` and `\` become `-` | `feature-auth` |
| `sanitize_db` | Database-safe: lowercase, underscores, hash suffix | `feature_auth_x7k` |
| `codename(n)` | Deterministic friendly name from ~1.26M-combo pool | `malleable-opah` |

> **Note:** Only `sanitize`, `sanitize_db`, and `codename(n)` are documented as worktree-path filters. Additional filters — `hash_port`, `sanitize_hash`, `hash`, `dirname`, `basename` — are available for general template use in hooks, aliases, and list URLs. See the [Worktrunk Filters reference](https://worktrunk.dev/hook/#worktrunk-filters) for the complete list.

**Path examples** for repo at `~/code/myproject`, branch `feature/auth`:

| Pattern | Resolves To |
|---|---|
| `{{ repo_path }}/../{{ repo }}.{{ branch | sanitize }}` (default) | `~/code/myproject.feature-auth` |
| `{{ repo_path }}/.worktrees/{{ branch | sanitize }}` | `~/code/myproject/.worktrees/feature-auth` |
| `{{ repo_path }}/../{{ repo }}.{{ branch | codename(2) }}` | `~/code/myproject.malleable-opah` |
| `{{ repo_path }}/../worktrees/{{ branch | sanitize }}/{{ branch | codename(2) }}` | `~/code/worktrees/feature-auth/malleable-opah` |
| `~/worktrees/{{ repo }}/{{ branch | sanitize }}` | `~/worktrees/myproject/feature-auth` |
| `~/development/{{ owner }}/{{ repo }}/{{ branch }}` | `~/development/max-sixty/myproject/feature/auth` |
| `{{ repo_path }}/../{{ branch | sanitize }}` (bare repo) | `~/code/myproject/feature-auth` |

The `~` prefix expands to the home directory. Relative paths resolve from `repo_path`.

### `[commit.generation]` — LLM Commit Message Generation

Configure an external CLI tool to generate commit messages automatically during merge.

**Available commands by tool:**

```toml
# Claude Code
[commit.generation]
command = "MAX_THINKING_TOKENS=0 claude -p --no-session-persistence --model=haiku --tools='' --disable-slash-commands --setting-sources='' --system-prompt=''"

# Codex
[commit.generation]
command = "codex exec -m gpt-5.4-mini -c model_reasoning_effort='low' -c system_prompt='' --sandbox=read-only --json - | jq -sr '[.[] | select(.item.type? == \"agent_message\")] | last.item.text'"

# OpenCode
[commit.generation]
command = "opencode run -m anthropic/claude-haiku-4.5 --variant fast"

# llm (Simon Willison's LLM tool)
[commit.generation]
command = "llm -m claude-haiku-4.5"

# aichat
[commit.generation]
command = "aichat -m claude:claude-haiku-4.5"
```

**Custom prompt templates:**

Templates use [minijinja](https://docs.rs/minijinja/) syntax.

**Commit template** — available variables: `{{ git_diff }}`, `{{ git_diff_stat }}`, `{{ branch }}`, `{{ repo }}`, `{{ recent_commits }}`, `{{ user_guidance }}`, `{{ project_guidance }}`.

Default:

```toml
[commit.generation]
template = """
<task>Write a commit message for the staged changes below.</task>

<format>
- Subject line under 50 chars
- For material changes, add a blank line then a body paragraph explaining the change
- Output only the commit message, no quotes or code blocks
</format>

<style>
- Imperative mood: "Add feature" not "Added feature"
- Match recent commit style (conventional commits if used)
- Describe the change, not the intent or benefit
</style>
{% if user_guidance %}
<user-guidance>
{{ user_guidance }}
</user-guidance>
{% endif %}{% if project_guidance %}
<project-guidance>
{{ project_guidance }}
</project-guidance>
{% endif %}
<diffstat>
{{ git_diff_stat }}
</diffstat>

<diff>
{{ git_diff }}
</diff>

<context>
Branch: {{ branch }}
{% if recent_commits %}<recent_commits>
{% for commit in recent_commits %}- {{ commit }}
{% endfor %}</recent_commits>{% endif %}
</context>

"""
```

**Squash template** — same variables as commit template plus `{{ commits }}` (list of subjects), `{{ commit_details }}` (list of `{ subject, body }` objects), `{{ target_branch }}`.

Default:

```toml
[commit.generation]
squash-template = """
<task>Write a commit message for the combined effect of these commits.</task>

<format>
- Subject line under 50 chars
- For material changes, add a blank line then a body paragraph explaining the change
- Output only the commit message, no quotes or code blocks
</format>

<style>
- Imperative mood: "Add feature" not "Added feature"
- Match the style of commits being squashed (conventional commits if used)
- Describe the change, not the intent or benefit
</style>
{% if user_guidance %}
<user-guidance>
{{ user_guidance }}
</user-guidance>
{% endif %}{% if project_guidance %}
<project-guidance>
{{ project_guidance }}
</project-guidance>
{% endif %}
<commits branch="{{ branch }}" target="{{ target_branch }}">
{% for commit in commits %}- {{ commit }}
{% endfor %}</commits>

<diffstat>
{{ git_diff_stat }}
</diffstat>

<diff>
{{ git_diff }}
</diff>

"""
```

**`template-append`** — Adds custom instructions to the default prompt without replacing the entire template. Rendered as a minijinja template and injected into the `<user-guidance>` block.

```toml
[commit.generation]
template-append = """
- Explain the rationale in the body, not just the change
"""
```

The user config's `template-append` renders into `<user-guidance>`. The project config's `template-append` renders into a separate `<project-guidance>` block that follows.

### `[commit]` — Stage Options

```toml
[commit]
stage = "all"      # What to stage before commit: "all", "tracked", or "none"
```

Shared by `wt step commit`, `wt step squash`, and `wt merge`.

### `[list]` — List Command Defaults

Persistent flag values for `wt list`. Override on command line as needed.

```toml
[list]
summary = false           # Enable LLM branch summaries (requires [commit.generation] setup)
full = false              # Show CI, main± diffstat, and LLM summaries (--full)
branches = false          # Include branches without worktrees (--branches)
remotes = false           # Include remote-only branches (--remotes)
task-timeout-ms = 0       # Kill individual git commands after N ms; 0 disables
timeout-ms = 0            # Wall-clock budget for entire collect phase; 0 disables
```

### `[merge]` — Merge Command Defaults

Most flags are on by default. Set any to `false` to change the default behavior.

```toml
[merge]
squash = true   # Squash commits into one (--no-squash to preserve history)
commit = true   # Commit uncommitted changes first (--no-commit to skip)
rebase = true   # Rebase onto target before merge (--no-rebase to skip)
remove = true   # Remove worktree after merge (--no-remove to keep)
verify = true   # Run project hooks (--no-hooks to skip)
ff = true       # Fast-forward merge (--no-ff to create a merge commit instead)
```

### `[remove]` — Remove Command Defaults

```toml
[remove]
delete-branch = true   # Delete branch after removal (--no-delete-branch to keep)
```

### `[switch]` — Switch Command Defaults

```toml
[switch]
cd = true          # Change directory after switching (--no-cd to skip)

[switch.picker]
pager = "delta --paging=never"   # Override git's core.pager for diff preview
```

### `[step.copy-ignored]` — Copy-Ignored Excludes

Additional exclude patterns for `wt step copy-ignored`. Built-in excludes always apply: VCS metadata directories (`.bzr/`, `.hg/`, `.jj/`, `.pijul/`, `.sl/`, `.svn/`) and tool-state directories (`.conductor/`, `.entire/`, `.worktrees/`). User config and project config exclusions are combined.

```toml
[step.copy-ignored]
exclude = []   # Additional excludes, e.g. [".cache/", ".turbo/"]
```

### `[aliases]` — Custom Commands

Command templates that run as `wt <name>`. Supports all template variables and filters available in hooks. Aliases defined here apply to all projects. Use `.config/wt.toml` `[aliases]` for project-specific aliases.

```toml
[aliases]
greet = "echo Hello from {{ branch }}"
url = "echo http://localhost:{{ branch | hash_port }}"
```

### `[forge]` — Forge Platform

Name the forge explicitly for SSH aliases or self-hosted instances where it cannot be detected from the remote URL.

```toml
[forge]
platform = "github"      # or "gitlab", "gitea" (experimental), "azure-devops" (experimental)
hostname = "github.example.com"   # API host for GHE / self-hosted GitLab
```

### `[projects."..."]` — Per-Project Overrides

User config can include a `[projects]` table for project-specific settings. Entries are keyed by project identifier — `<host>/<owner>/<repo>` derived from the primary remote URL (no `.git` suffix), or the canonical repo path when there is no remote. Run `wt config show` inside the repo to see its identifier.

Scalar values (like `worktree-path`) replace the global value; everything else (hooks, aliases, etc.) appends, global first.

```toml
[projects."github.com/user/repo"]
worktree-path = ".worktrees/{{ branch | sanitize }}"
list.full = true
merge.squash = false
remove.delete-branch = false
pre-start.env = "cp .env.example .env"
step.copy-ignored.exclude = [".repo-local-cache/"]
aliases.deploy = "make deploy BRANCH={{ branch }}"
```

Hooks support all three hook forms. A table runs multiple commands concurrently; an array-of-tables pipeline runs steps in sequence:

```toml
# Single command
[projects."github.com/user/repo"]
post-start = "mise trust"

# Multiple commands, running concurrently
[projects."github.com/user/repo".post-start]
mise = "mise trust"
server = "npm run dev"

# Pipeline: steps run in sequence
[[projects."github.com/user/repo".post-start]]
install = "npm ci"

[[projects."github.com/user/repo".post-start]]
build = "npm run build"
server = "npm run dev"
```

## Project Configuration (`.config/wt.toml`)

Project configuration lets teams share repository-specific settings. Create with `wt config create --project`. The file lives at `.config/wt.toml` and is typically checked into version control.

### Hooks

Project hooks apply to this repository only. See `wt hook` for hook types, execution order, and template variables.

```toml
pre-start = "npm ci"
post-start = "npm run dev"
pre-merge = "npm test"
```

### Dev Server URL

URL column in `wt list` (dimmed when port not listening):

```toml
[list]
url = "http://localhost:{{ branch | hash_port }}"
```

### Forge Platform

```toml
[forge]
platform = "github"       # or "gitlab", "gitea", "azure-devops"
hostname = "github.example.com"
```

### Commit-Message Append

Project-wide conventions appended to the LLM commit and squash prompts inside a `<project-guidance>` block. Rendered as a minijinja template with the same variables as the main commit template. The first time the fragment changes, `wt` prompts the user to approve it.

```toml
[commit.generation]
template-append = """
- Use conventional commits (feat:, fix:, docs:, ...)
- Reference the relevant issue ID in the body
"""
```

Only `template-append` is honored from the project file. The LLM command and main prompt template stay in user config.

### Copy-Ignored Excludes

```toml
[step.copy-ignored]
exclude = [".cache/", ".turbo/"]
```

### Aliases

```toml
[aliases]
deploy = "make deploy BRANCH={{ branch }}"
url = "echo http://localhost:{{ branch | hash_port }}"
```

## Environment Variable Overrides

All user config options can be overridden with environment variables using the `WORKTRUNK_` prefix.

### Naming Convention

Config keys use kebab-case (`worktree-path`), while env vars use SCREAMING_SNAKE_CASE (`WORKTRUNK_WORKTREE_PATH`). Nested config sections use double underscores to separate levels.

| Config Key | Environment Variable |
|---|---|
| `worktree-path` | `WORKTRUNK_WORKTREE_PATH` |
| `commit.generation.command` | `WORKTRUNK_COMMIT__GENERATION__COMMAND` |
| `commit.stage` | `WORKTRUNK_COMMIT__STAGE` |

**Example — override LLM command for CI:**

```bash
WORKTRUNK_COMMIT__GENERATION__COMMAND="echo 'test: automated commit'" wt merge
```

### Other Environment Variables

| Variable | Purpose |
|---|---|
| `WORKTRUNK_BIN` | Override binary path for shell wrappers; useful for testing dev builds |
| `WORKTRUNK_CONFIG_PATH` | Override user config file location |
| `WORKTRUNK_SYSTEM_CONFIG_PATH` | Override system config file location |
| `WORKTRUNK_PROJECT_CONFIG_PATH` | Override project config file location (default: `.config/wt.toml`) |
| `XDG_CONFIG_DIRS` | Colon-separated system config directories (default: `/etc/xdg`) |
| `WORKTRUNK_DIRECTIVE_CD_FILE` | Internal: set by shell wrappers; `wt` writes a raw path, the wrapper `cd`s to it |
| `WORKTRUNK_DIRECTIVE_EXEC_FILE` | Internal: set by shell wrappers; `wt` writes shell commands, the wrapper sources the file |
| `WORKTRUNK_SHELL` | Internal: set by shell wrappers to indicate shell type (e.g., `powershell`) |
| `WORKTRUNK_MAX_CONCURRENT_COMMANDS` | Max parallel git commands (default: 32). Lower if hitting file descriptor limits |
| `NO_COLOR` | Disable colored output (per no-color.org standard) |
| `CLICOLOR_FORCE` | Force colored output even when not a TTY |

## Approvals (`wt config approvals`)

Project hooks and project aliases prompt for approval on first run to prevent untrusted projects from running arbitrary commands. Approvals are stored in `~/.config/worktrunk/approvals.toml`. Re-approval is required when the command template changes or the project moves.

```
# Pre-approve all hook and alias commands for current project
wt config approvals add

# Clear approvals for current project
wt config approvals clear

# Clear global approvals
wt config approvals clear --global
```

Use `--yes` to bypass approval prompts in CI.

## Shell Integration

Worktrunk needs shell integration to change directories when switching worktrees. Install with:

```
wt config shell install
```

For manual setup, see `wt config shell init --help`. Without shell integration, `wt switch` prints the target directory but cannot `cd` into it.

On first run without shell integration, Worktrunk offers to install it. On first commit without LLM configuration, it offers to configure a detected tool. Declining sets `skip-shell-integration-prompt` or `skip-commit-generation-prompt` automatically.

## State Management (`wt config state`)

State is stored in `.git/` (config entries and log files), separate from configuration files.

| Key | Description |
|---|---|
| `default-branch` | Repository default branch (`main`, `master`, etc.) |
| `previous-branch` | Previous branch for `wt switch -` |
| `logs` | Operation and debug logs |
| `ci-status` | CI/PR status for a branch (passed, running, failed, conflicts, no-ci, error) |
| `marker` | Custom status marker for a branch (shown in `wt list`) |
| `vars` | Custom variables per branch |

### Default Branch

Worktrunk detects the default branch automatically through a cascading strategy:

1. **Worktrunk cache** — checks `git config worktrunk.default-branch`
2. **Git cache** — detects primary remote and checks its HEAD (e.g., `origin/HEAD`)
3. **Remote query** — queries `git ls-remote` (typically 100ms–2s)
4. **Local inference** — if no remote, infers from local branches (heuristics: single branch, `symbolic-ref HEAD`, `init.defaultBranch`, common names `main`/`master`/`develop`/`trunk`)

Useful in scripts to avoid hardcoding branch names:

```bash
git rebase $(wt config state default-branch)
```

```
# Get the default branch
wt config state default-branch

# Set the default branch manually
wt config state default-branch set main

# Clear cache and re-detect
wt config state default-branch clear
```

### Logs

Three kinds of logs live in `.git/wt/logs/`:

**Command log** (`commands.jsonl`): All hook executions and LLM commands recorded automatically — one JSON object per line. Rotates to `commands.jsonl.old` at 1MB (~2MB total). Fields: `ts` (ISO 8601), `wt` (triggering command), `label`, `cmd`, `exit` (exit code), `dur_ms` (duration).

**Hook output logs**: Per-branch subtrees under `.git/wt/logs/{branch}/`. Background hooks (`post-*`) produce log files. Source is `user` or `project`. Branch and hook names are sanitized for filesystem safety.

**Diagnostic files** (created with `-vv`): `trace.log` (debug records), `subprocess.log` (raw subprocess output), `diagnostic.md` (markdown bug-report bundle).

```
# List all log files
wt config state logs

# Query the command log
tail -5 .git/wt/logs/commands.jsonl | jq .

# Clear all logs
wt config state logs clear
```

### CI Status

Caches GitHub/GitLab CI status for display in `wt list`. Requires `gh` (GitHub) or `glab` (GitLab) CLI, authenticated. Caches results for 30–60 seconds.

| Status | Meaning |
|---|---|
| `passed` | All checks passed |
| `running` | Checks in progress |
| `failed` | Checks failed |
| `conflicts` | PR has merge conflicts |
| `no-ci` | No checks configured |
| `error` | Fetch error (rate limit, network, auth) |

```
wt config state ci-status        # Get CI status for current branch
wt config state ci-status clear  # Clear cache for a branch
wt config state ci-status clear --all  # Clear all CI cache
```

### Markers

Custom status text or emoji shown in the `wt list` Status column. Stored in git config as `worktrunk.state.<branch>.marker`.

```
wt config state marker           # Get marker for current branch
wt config state marker set "\U0001f6a7"   # Set marker (e.g., WIP)
wt config state marker clear     # Clear marker
```

Use cases: `\U0001f6a7` (WIP), `\u2705` (ready for review), `\U0001f525` (urgent). The Claude Code plugin sets markers automatically.

### Vars

Store custom variables per branch. Values are stored as-is — plain strings or JSON. Available in hook templates as `{{ vars.<key> }}`.

```
wt config state vars set env=staging
wt config state vars get env
wt config state vars list
wt config state vars set config='{"port": 3000, "debug": true}'
wt config state vars clear env
```

JSON object and array values support dot access in templates:

```toml
[post-start]
dev = "npm start -- --port {{ vars.config.port }}"
```

Keys must contain only letters, digits, and hyphens. Dots and underscores are reserved by git config's format.

## References

- [Worktrunk Configuration Documentation](https://worktrunk.dev/config/)
- [Worktrunk LLM Commits](https://worktrunk.dev/llm-commits/)
- [Worktrunk Extending Guide](https://worktrunk.dev/extending/)
- [Worktrunk Hooks Reference](https://worktrunk.dev/hook/)
- [Worktrunk Agent Integration](https://worktrunk.dev/claude-code/)
- [Worktrunk Tips & Patterns](https://worktrunk.dev/tips-patterns/)
- [Minijinja Template Engine](https://docs.rs/minijinja/)

---

## See Also

- [CLI Reference](./cli-reference.md) — All `wt` commands with flags and examples
- [Hooks Reference](./hooks.md) — Hook types, lifecycle, template variables, recipes

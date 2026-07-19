---
title: "Worktrunk Hooks"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags:
  - worktrunk
  - hooks
  - automation
sources:
  - url: "https://worktrunk.dev/hook/"
    title: "wt hook — Worktrunk CLI reference"
  - url: "https://worktrunk.dev/config/#hooks"
    title: "Worktrunk Configuration — Hooks"
  - url: "https://worktrunk.dev/tips-patterns/"
    title: "Worktrunk Tips & Patterns"
last_audit_date: 2026-06-07
---

# Worktrunk Hooks

Worktrunk hooks are shell commands that run automatically at key points in the
worktree lifecycle: during `wt switch`, `wt merge`, and `wt remove`, or on
demand via `wt hook <type>`. Both user-level and project-level hooks are
supported, with three configurable forms (string, table, pipeline) and a rich
templating system with variables, filters, functions, and JSON context on
stdin.

## Hook Types

Hooks are organized into five lifecycle events, each with a blocking `pre-`
variant and a background `post-` variant:

| Event      | Blocking (`pre-*`)                   | Background (`post-*`)                 |
|------------|--------------------------------------|---------------------------------------|
| **switch** | `pre-switch`                         | `post-switch`                         |
| **create** | `pre-start`                          | `post-start`                          |
| **commit** | `pre-commit`                         | `post-commit`                         |
| **merge**  | `pre-merge`                          | `post-merge`                          |
| **remove** | `pre-remove`                         | `post-remove`                         |

### Blocking vs Background

- **`pre-*` hooks block** — failure aborts the operation. Use these for
  validation, dependency installation, or any step that must succeed before the
  operation proceeds.
- **`post-*` hooks run in the background** — output is logged to
  `.git/wt/logs/{branch}/`. Use these for dev servers, long builds, file
  watchers, and notifications. Pass `-v` to see expanded command details for
  background hooks.

### Hook Lifecycle Details

**`pre-switch`**: Runs before branch resolution or worktree creation. The
`{{ branch }}` variable is the destination as typed (before branch name
resolution).

**`post-switch`**: Triggers on all switch results — creating a new worktree,
switching to an existing one, or staying on the current branch.

**`pre-start`**: Runs once when a new worktree is created, blocking
`post-start`/`--execute` until complete. Ideal for dependency installation and
env file generation.

**`post-start`**: Runs once when a new worktree is created, in the background.
This is the most common creation hook — use it for dev servers, long builds,
file watchers, and copying caches.

**`pre-commit`**: Formatters, linters, and type checking. Runs during
`wt merge` before the squash commit.

**`post-commit`**: CI triggers, notifications, background linting.

**`pre-merge`**: Tests, security scans, build verification. Runs after rebase,
before merge to target.

**`post-merge`**: Deployment, notifications, installing updated binaries. Runs
in the target branch worktree if it exists, otherwise the primary worktree.

**`pre-remove`**: Cleanup before worktree deletion — saving test artifacts,
backing up state. Runs in the worktree being removed.

**`post-remove`**: Stopping dev servers, removing containers, notifying
external systems. Template variables reference the removed worktree.

### Merge Hook Pipeline Order

During `wt merge`, hooks execute in this sequence:

1. `pre-commit` (blocking)
2. `post-commit` (background)
3. `pre-merge` (blocking)
4. `pre-remove` (blocking)
5. `post-remove` + `post-merge` (background, concurrent)

### Best Practice: Prefer `post-start` over `pre-start`

The most common creation hook is `post-start` — it runs background tasks (dev
servers, file copying, builds) without blocking worktree creation. Use
`pre-start` only when a later step (like `--execute`) needs the work completed
first.

## Hook Configuration

Hooks are defined in TOML configuration files. They can live in either the
user config or the project config.

### User Config vs Project Config

| Aspect          | User hooks                                        | Project hooks                                   |
|-----------------|---------------------------------------------------|-------------------------------------------------|
| **Location**    | `~/.config/worktrunk/config.toml`                 | `.config/wt.toml`                               |
| **Scope**       | All repositories (or per-project via `[projects]`) | Single repository                               |
| **Commits**     | No (personal)                                     | Yes (shared with team)                          |
| **Approval**    | Not required                                      | Required on first run                           |
| **Exec order**  | First                                             | After user hooks                                |

To run a specific hook when user and project both define the same name, use
the `user:name` or `project:name` prefix syntax.

### Hook Forms

Hooks take one of three TOML shapes, determined by their structure.

#### String Form (single command)

```toml
pre-start = "npm install"
```

#### Table Form (concurrent commands)

Multiple commands under the same hook type run concurrently:

```toml
[post-start]
server = "npm run dev"
watch = "npm run watch"
```

Each key is the hook name; all commands start simultaneously.

#### Array-of-Tables Pipeline Form (sequential steps)

A sequence of `[[hook]]` blocks runs in order. Each block is one step;
multiple keys within a block run concurrently. A failing step aborts the rest
of the pipeline:

```toml
[[post-start]]
install = "npm ci"

[[post-start]]
build = "npm run build"
server = "npm run dev"
```

Here `install` runs first, then `build` and `server` run together.

Most hooks do not need pipeline blocks. Reach for them when there is a
dependency chain — typically setup that must complete before later steps, like
installing dependencies before running a build and dev server concurrently.

> Table form for `pre-*` hooks is deprecated. Its behavior will change in a
> future version — use `[[hook]]` pipeline blocks instead.

### Project Config Examples

```toml
# .config/wt.toml
[pre-start]
deps = "npm ci"

[[post-start]]
install = "pnpm install"

[[post-start]]
server = "npm run dev"
test = "npm run test:watch"

[pre-commit]
lint = "npm run lint"
typecheck = "npm run typecheck"

[pre-merge]
test = "npm test"

[post-merge]
deploy = "npm run deploy:staging"

[post-remove]
cleanup = "docker stop my-container 2>/dev/null || true"
```

### User Config Examples

```toml
# ~/.config/worktrunk/config.toml
[post-start]
dev = "npm run dev -- --port {{ branch | hash_port }}"

[pre-remove]
tmux = "tmux kill-session -t {{ branch | sanitize }} 2>/dev/null || true"
```

## Security and Approvals

Project hooks (defined in `.config/wt.toml`) require approval before their
first execution. This prevents untrusted repositories from running arbitrary
commands on your machine.

### First-Run Approval Prompt

When project hooks are encountered for the first time, Worktrunk displays an
interactive prompt:

```
▲ repo needs approval to execute 3 commands:

○ pre-start install:
  npm ci
○ pre-start build:
  cargo build --release
○ pre-start env:
  echo 'PORT={{ branch | hash_port }}' > .env.local

? Allow and remember? [y/N]
```

- Approvals are saved to `~/.config/worktrunk/approvals.toml`
- If a command template changes, a new approval is required
- Declining skips every project command for that operation (including any
  already approved) and continues without them; saved approvals are unaffected
- Use `--yes` to bypass prompts — intended for CI and automation
- Use `--no-hooks` to skip all hooks for an operation

### Managing Approvals

```bash
# Pre-approve all hook and alias commands for the current project
wt config approvals add

# Clear approvals for the current project
wt config approvals clear

# Clear global approvals
wt config approvals clear --global
```

## Template Variables

Hooks support rich template expansion via the
[minijinja](https://docs.rs/minijinja/) template engine. Variables are grouped
into five categories.

### Active Variables

These describe the branch the operation acts on:

| Variable               | Description                                             |
|------------------------|---------------------------------------------------------|
| `{{ branch }}`         | Branch name                                             |
| `{{ worktree_path }}`  | Worktree filesystem path                                |
| `{{ worktree_name }}`  | Worktree directory name                                 |
| `{{ commit }}`         | Branch HEAD SHA                                         |
| `{{ short_commit }}`   | Branch HEAD SHA, abbreviated per `core.abbrev`          |
| `{{ upstream }}`       | Branch upstream (if tracking a remote)                  |

### Operation Variables

These describe the other side of the operation:

| Variable                      | Description                                            |
|-------------------------------|--------------------------------------------------------|
| `{{ base }}`                  | Base branch name (switch/create only)                  |
| `{{ base_worktree_path }}`    | Base worktree path                                     |
| `{{ target }}`                | Target branch name (merge target)                      |
| `{{ target_worktree_path }}`  | Target worktree path (when target has a worktree)      |
| `{{ pr_number }}`             | PR/MR number (available in post-switch, pre-start, post-start; when creating via `pr:N` / `mr:N`) |
| `{{ pr_url }}`                | PR/MR web URL (available in post-switch, pre-start, post-start; when creating via `pr:N` / `mr:N`) |

For `base` and `target` semantics across operations:

| Operation         | Bare vars (`branch`, etc.) | `base`                     | `target`                     |
|-------------------|---------------------------|----------------------------|------------------------------|
| switch/create     | destination               | where you came from        | = bare vars                  |
| commit (merge)    | worktree being squashed   | = bare vars                | integration target           |
| merge             | feature being merged      | = bare vars                | merge target                 |
| remove            | branch being removed      | = bare vars                | where you end up             |

### Repository Variables

| Variable                   | Description                                      |
|----------------------------|--------------------------------------------------|
| `{{ repo }}`               | Repository directory name                        |
| `{{ repo_path }}`          | Absolute path to repository root                 |
| `{{ owner }}`              | Primary remote owner path (may include subgroups)|
| `{{ primary_worktree_path }}` | Primary worktree path                        |
| `{{ default_branch }}`     | Default branch name                              |
| `{{ remote }}`             | Primary remote name                              |
| `{{ remote_url }}`         | Remote URL                                       |

### Execution Variables

| Variable           | Description                                              |
|--------------------|----------------------------------------------------------|
| `{{ cwd }}`        | Directory where the hook command runs                    |
| `{{ hook_type }}`  | Hook type being run (e.g. `pre-start`, `pre-merge`)      |
| `{{ hook_name }}`  | Hook command name (if named)                             |
| `{{ args }}`       | Tokens forwarded from the CLI — see Passing Values       |

### User Variables

| Variable            | Description                                               |
|---------------------|-----------------------------------------------------------|
| `{{ vars.<key> }}`  | Per-branch custom variables (set via `wt config state vars`) |

### Variable Resolution: `cwd` vs `worktree_path`

`cwd` is the worktree root where the hook command runs. It equals
`worktree_path` except in three cases:

- **`pre-switch`**: hook runs in the source worktree; `worktree_path` is the
  destination
- **`post-remove`** and **`post-merge` with removal**: the active worktree is
  gone, so the hook runs in the primary or target worktree, respectively

### Conditional Variables

Undefined variables produce an error. Use Jinja2 conditionals for optional
behavior:

```toml
[pre-start]
sync = """
{% if upstream %}git fetch && git rebase {{ upstream }}{% endif %}
"""
```

Run any hook-firing command with `-v` to see resolved variables. Each hook
prints a `template variables:` block showing every in-scope variable and its
value (`(unset)` for conditional vars that did not populate).

### Dot Access and Defaults

Variables support dot access and the `default` filter for missing keys. JSON
object/array values are parsed automatically:

```toml
[post-start]
dev = """
ENV={{ vars.env | default('development') }} npm start \
  -- --port {{ vars.config.port | default('3000') }}
"""
```

## Template Filters

Worktrunk provides Jinja2-style filters for transforming variable values.

| Filter             | Example                                    | Description                                      |
|--------------------|--------------------------------------------|--------------------------------------------------|
| `sanitize`         | `{{ branch \| sanitize }}`                 | Replace `/` and `\` with `-`                     |
| `sanitize_db`      | `{{ branch \| sanitize_db }}`              | Database-safe identifier (lowercase, underscores, max 48 chars, hash suffix) |
| `sanitize_hash`    | `{{ branch \| sanitize_hash }}`            | Filesystem-safe name with hash suffix for uniqueness |
| `hash`             | `{{ branch \| hash }}`                     | 3-character base36 digest of the input           |
| `hash_port`        | `{{ branch \| hash_port }}`                | Deterministic port in range 10000–19999          |
| `dirname`          | `{{ repo_path \| dirname }}`               | Strip the last path component                    |
| `basename`         | `{{ repo_path \| basename }}`              | Keep only the last path component                |
| `codename(n)`      | `{{ branch \| codename(2) }}`              | Deterministic friendly words (noun or adjective-noun) |

### Filter Details

**`sanitize_db`**: produces database-safe identifiers — lowercase alphanumeric
and underscores, no leading digits, with a 3-character hash suffix to avoid
collisions and reserved words.

**`sanitize_hash`**: produces a filesystem-safe name and appends a 3-character
hash suffix when sanitization changed the input. Already-safe names pass
through unchanged, so distinct originals never collide.

**`codename(n)`**: produces deterministic friendly names from an input string.
`codename(1)` returns a noun, `codename(2)` returns `adjective-noun`, and
higher counts add more adjectives. The pool is large (~1.26M combinations for
`codename(2)`), making it useful as standalone worktree leaf names:

```toml
worktree-path = "{{ repo_path }}/../{{ repo }}.{{ branch | codename(2) }}"
```

When both a friendly name and original branch identity are needed in the path,
nest the branch in a parent directory:

```toml
worktree-path = "{{ repo_path }}/../worktrees/{{ branch | sanitize }}/{{ branch | codename(2) }}"
```

**`hash`**: the bare 3-character base36 digest, useful for composing custom
truncate-with-collision-avoidance recipes:

```toml
worktree-path = "/tmp/{{ (branch | sanitize)[:20] }}_{{ branch | sanitize | hash }}"
```

**`dirname` and `basename`**: useful for bare repos in a hidden directory:

```toml
worktree-path = "{{ repo_path }}/../{{ repo_path | dirname | basename }}.{{ branch | sanitize }}"
```

**`hash_port`**: ideal for running dev servers on unique ports per worktree:

```toml
[post-start]
dev = "npm run dev -- --host {{ branch }}.localhost --port {{ branch | hash_port }}"
```

Hash any string, including concatenations, for repo+branch uniqueness:

```toml
dev = "npm run dev --port {{ (repo ~ '-' ~ branch) | hash_port }}"
```

Variables are shell-escaped automatically — quotes around `{{ }}` are
unnecessary and can cause issues with special characters.

## Template Functions

| Function                                              | Description                              |
|-------------------------------------------------------|------------------------------------------|
| `{{ worktree_path_of_branch("main") }}`               | Look up the filesystem path of a branch's worktree |

The `worktree_path_of_branch` function returns the filesystem path of a
worktree given a branch name, or an empty string if no worktree exists. Useful
for referencing files in other worktrees:

```toml
[pre-start]
setup = "cp {{ worktree_path_of_branch('main') }}/config.local {{ worktree_path }}"
```

## JSON Context

All template variables are also passed to the hook command as JSON on stdin.
This enables complex logic that templates alone cannot express:

```toml
[pre-start]
setup = "python3 scripts/pre-start-setup.py"
```

```python
import json, sys, subprocess
ctx = json.load(sys.stdin)
if ctx['branch'].startswith('feature/') and 'backend' in ctx['repo']:
    subprocess.run(['make', 'seed-db'])
```

## Copying Untracked Files

Git worktrees share the repository but not untracked files.
[`wt step copy-ignored`](https://worktrunk.dev/step/#wt-step-copy-ignored)
copies gitignored files (caches, dependencies, `.env`) between worktrees:

```toml
[post-start]
copy = "wt step copy-ignored"
```

## Running Hooks Manually

The `wt hook` command runs hooks on demand — useful for testing during
development, running in CI pipelines, or re-running after a failure.

### Basic Usage

```bash
wt hook pre-merge              # Run all pre-merge hooks
wt hook pre-merge test         # Run hooks named "test" from both sources
wt hook pre-merge test build   # Run hooks named "test" and "build"
```

### Source Filtering

Use `user:` and `project:` prefixes to filter by source:

```bash
wt hook pre-merge user:        # Run all user hooks
wt hook pre-merge project:     # Run all project hooks
wt hook pre-merge user:test    # Run only user's "test" hook
wt hook pre-merge project:test # Run only project's "test" hook
```

### Flags

```bash
wt hook pre-start --yes                     # Skip approval prompts (CI)
wt hook pre-start --branch=feature/test     # Override a template variable
wt hook pre-merge -- --extra args           # Forward tokens into {{ args }}
```

### Command Reference

```
wt hook - Run configured hooks

Usage: wt hook [OPTIONS] <COMMAND>

Commands:
  show         Show configured hooks
  pre-switch   Run pre-switch hooks
  post-switch  Run post-switch hooks
  pre-start    Run pre-start hooks
  post-start   Run post-start hooks
  pre-commit   Run pre-commit hooks
  post-commit  Run post-commit hooks
  pre-merge    Run pre-merge hooks
  post-merge   Run post-merge hooks
  pre-remove   Run pre-remove hooks
  post-remove  Run post-remove hooks

Options:
  -h, --help            Print help
  -C <path>             Working directory for this command
      --config <path>   User config file path
  -v, --verbose...      Verbose output (-v: info logs + hook/alias template variables on stderr;
                        -vv: also debug logs and raw subprocess output written to .git/wt/logs/)
  -y, --yes             Skip approval prompts
```

### Verbose Output

Run any hook-firing command with `-v` to see resolved variables for the actual
invocation. Each hook prints a `template variables:` block with every
in-scope variable and its value (or `(unset)` for conditional variables).
Aliases do the same under `-v`: `wt -v <alias>` prints the alias's in-scope
variables before the pipeline runs.

### Hook Output Logs

Background hooks write output to `.git/wt/logs/{branch}/{source}/{hook-type}/{name}.log`
where `source` is `user` or `project`. Branch and hook names are sanitized for
filesystem safety. Background removal operations log to
`.git/wt/logs/{branch}/internal/remove.log`. The command audit log is at
`.git/wt/logs/commands.jsonl`. Manage logs with:

```bash
wt config state logs          # List all log files
wt config state logs clear    # Clear all logs
tail -f "$(wt config state logs get --hook=user:post-start:server)"  # Follow hook output
```

### Diagnostic Files

Running any command with `-vv` creates three diagnostic files in
`.git/wt/logs/`, all overwritten on each `-vv` run:

| File | Description |
|---|---|
| `trace.log` | Debug-level records — commands, `[wt-trace]` records, bounded subprocess previews |
| `subprocess.log` | Raw uncapped subprocess stdout/stderr bodies |
| `diagnostic.md` | Markdown bug-report bundle that inlines `trace.log`; `wt` prints a `gh gist create` command pointing at it |

## Passing Values

### CLI Overrides: `--KEY=VALUE`

`--KEY=VALUE` binds `KEY` wherever `{{ KEY }}` appears in any hook command.
Built-in variables can be overridden:

```bash
wt hook pre-start --branch=foo  # Sets {{ branch }} inside hook templates
                                 # (the worktree's actual branch does not move)
```

Hyphens in keys become underscores: `--my-var=x` sets `{{ my_var }}`.

### The `{{ args }}` Variable

Any `--KEY=VALUE` whose key is not referenced by a hook template forwards into
`{{ args }}` as a literal `--KEY=VALUE` token. Tokens after `--` also forward
into `{{ args }}` verbatim.

`{{ args }}` renders as a space-joined, shell-escaped string. It can be
indexed and iterated:

```
{{ args[0] }}
{% for a in args %}...{% endfor %}
{{ args | length }}
```

### The `--var` Long Form (Deprecated)

The long form `--var KEY=VALUE` is deprecated but still supported. It
force-binds regardless of whether any hook template references `KEY` — useful
when a template only references the key conditionally (e.g.
`{% if override %}...{% endif %}`).

## Recipes

### Dev Server Per Worktree

Each worktree runs its own dev server on a deterministic port:

```toml
# .config/wt.toml
[post-start]
server = "wt step tether -- npm run dev -- --port {{ branch | hash_port }}"

[list]
url = "http://localhost:{{ branch | hash_port }}"
```

[`wt step tether`](https://worktrunk.dev/step/#wt-step-tether) runs the server
in its own process group and tears the whole group down when the worktree is
removed, so no `pre-remove` hook is needed.

### Database Per Worktree

Each worktree gets its own isolated database via a pipeline that sets up names
and ports as per-branch variables:

```toml
[[post-start]]
set-vars = """
wt config state vars set \
  container='{{ repo }}-{{ branch | sanitize }}-postgres' \
  port='{{ ('db-' ~ branch) | hash_port }}' \
  db_url='postgres://postgres:dev@localhost:{{ ('db-' ~ branch) | hash_port }}/{{ branch | sanitize_db }}'
"""

[[post-start]]
db = """
docker run -d --rm \
  --name {{ vars.container }} \
  -p {{ vars.port }}:5432 \
  -e POSTGRES_DB={{ branch | sanitize_db }} \
  -e POSTGRES_PASSWORD=dev \
  postgres:16
"""

[pre-remove]
db-stop = "docker stop {{ vars.container }} 2>/dev/null || true"
```

The first pipeline step derives values from the branch and stores them as
vars. The second step references `{{ vars.container }}` and `{{ vars.port }}`
— expanded at execution time, after the vars are set. `pre-remove` reads the
same vars to stop the container.

The `('db-' ~ branch)` concatenation hashes differently than plain `branch`,
so database and dev server ports do not collide.

### Eliminate Cold Starts with `copy-ignored`

Use [`wt step copy-ignored`](https://worktrunk.dev/step/#wt-step-copy-ignored)
to copy gitignored files (caches, dependencies, `.env`) between worktrees:

```toml
[post-start]
copy = "wt step copy-ignored"
```

When another hook depends on the copy, sequence them with a pipeline:

```toml
[[post-start]]
copy = "wt step copy-ignored"

[[post-start]]
install = "pnpm install"
```

Use `pre-start` instead when an `--execute` command needs the copied files
immediately.

### Progressive Validation

Split checks across hook types — quick feedback before each commit, expensive
suites before merge:

```toml
[[pre-commit]]
lint = "npm run lint"
typecheck = "npm run typecheck"

[[pre-merge]]
test = "npm test"
build = "npm run build"
```

`pre-commit` runs on every squash commit during `wt merge`; `pre-merge` runs
once per merge after the rebase, so it is the right place for slow tests.

### Target-Specific Hooks

Branch on `{{ target }}` to vary behavior per merge destination:

```toml
post-merge = """
if [ {{ target }} = main ]; then
    npm run deploy:production
elif [ {{ target }} = staging ]; then
    npm run deploy:staging
fi
"""
```

`{{ target }}` is the branch being merged into. `post-merge` runs in the
target's worktree (or the primary worktree if target has none).

### Tmux Session Per Worktree

Each worktree gets its own tmux session with a multi-pane layout:

```toml
[pre-start]
tmux = """
S={{ branch | sanitize }}
W={{ worktree_path }}
tmux new-session -d -s "$S" -c "$W" -n dev

# Create 4-pane layout: shell | backend / claude | frontend
tmux split-window -h -t "$S:dev" -c "$W"
tmux split-window -v -t "$S:dev.0" -c "$W"
tmux split-window -v -t "$S:dev.2" -c "$W"

# Start services in each pane
tmux send-keys -t "$S:dev.1" 'npm run backend' Enter
tmux send-keys -t "$S:dev.2" 'claude' Enter
tmux send-keys -t "$S:dev.3" 'npm run frontend' Enter

tmux select-pane -t "$S:dev.0"
echo "Session '$S' -- attach with: tmux attach -t $S"
"""

[pre-remove]
tmux = "tmux kill-session -t {{ branch | sanitize }} 2>/dev/null || true"
```

To create a worktree and immediately attach:

```bash
wt switch --create feature -x 'tmux attach -t {{ branch | sanitize }}'
```

### cmux Workspace Per Worktree

Each worktree gets its own [cmux](https://cmux.com) workspace. Switching
worktrees switches workspaces; removing a worktree closes its workspace.

Note: `pre-*` hooks are used instead of `post-*` because cmux restricts socket
access to processes spawned inside a cmux terminal, and `post-*` hooks run as
detached background processes that break the process ancestry chain.

**Prerequisite:** [jq](https://jqlang.org) (`brew install jq`)

```toml
[switch]
cd = false

[pre-start]
cmux = """
cmux new-workspace \
  --name {{ repo | sanitize }}/{{ branch | sanitize }} \
  --cwd {{ worktree_path }} \
  --focus true
"""

[pre-switch]
cmux = """
WS=$(cmux --json list-workspaces 2>/dev/null \
  | jq -r --arg t '{{ repo | sanitize }}/{{ branch | sanitize }}' \
      '.workspaces[] | select(.title == $t) | .ref' | head -1)
[ -n "$WS" ] && cmux select-workspace --workspace "$WS" || true
"""

[pre-remove]
cmux = """
WS=$(cmux --json list-workspaces 2>/dev/null \
  | jq -r --arg t '{{ repo | sanitize }}/{{ branch | sanitize }}' \
      '.workspaces[] | select(.title == $t) | .ref' | head -1)
[ -n "$WS" ] && cmux close-workspace --workspace "$WS" || true
"""
```

### Xcode DerivedData Cleanup

Clean up Xcode's DerivedData when removing a worktree. Each DerivedData
directory contains an `info.plist` recording its project path — grep for the
worktree path to find and remove the matching build cache:

```toml
[post-remove]
clean-derived = """
grep -Fl {{ worktree_path }} \
  ~/Library/Developer/Xcode/DerivedData/*/info.plist 2>/dev/null \
| while read plist; do
    derived_dir=$(dirname "$plist")
    rm -rf "$derived_dir"
    echo "Cleaned DerivedData: $derived_dir"
  done
"""
```

### Subdomain Routing with Caddy

Clean URLs like `http://feature-auth.myproject.localhost` without port numbers.
Useful for cookies, CORS, and matching production URL structure.

**Prerequisite:** [Caddy](https://caddyserver.com/docs/install) (`brew install caddy`)

```toml
[post-start]
server = "wt step tether -- npm run dev -- --port {{ branch | hash_port }}"
proxy = """
  curl -sf --max-time 0.5 http://localhost:2019/config/ || caddy start
  curl -sf http://localhost:2019/config/apps/http/servers/wt || \
    curl -sfX PUT http://localhost:2019/config/apps/http/servers/wt \
      -H 'Content-Type: application/json' \
      -d '{"listen":[":8080"],"automatic_https":{"disable":true},"routes":[]}'
  curl -sf -X DELETE http://localhost:2019/id/wt:{{ repo }}:{{ branch | sanitize }} || true
  curl -sfX PUT http://localhost:2019/config/apps/http/servers/wt/routes/0 \
    -H 'Content-Type: application/json' \
    -d '{"@id":"wt:{{ repo }}:{{ branch | sanitize }}","match":[{"host":["{{ branch | sanitize }}.{{ repo }}.localhost"]}],"handle":[{"handler":"reverse_proxy","upstreams":[{"dial":"127.0.0.1:{{ branch | hash_port }}"}]}]}'
"""

[pre-remove]
proxy = "curl -sf -X DELETE http://localhost:2019/id/wt:{{ repo }}:{{ branch | sanitize }} || true"

[list]
url = "http://{{ branch | sanitize }}.{{ repo }}.localhost:8080"
```

### Bare Repository Layout

A [bare repository](https://git-scm.com/docs/gitrepository-layout) has no
working tree, so all branches are linked worktrees at equal paths:

```toml
worktree-path = "{{ repo_path }}/../{{ branch | sanitize }}"
```

With this layout, a bare repo at `myproject/.git` produces:

```
myproject/
  .git/       # bare repository
  main/       # default branch worktree
  feature/    # feature branch worktree
  bugfix/     # bugfix branch worktree
```

Worktrunk auto-detects bare repos and offers to configure this path on first
`wt switch`. The project config (`.config/wt.toml`) must live inside a
worktree, since bare `.git` has no tracked files.

### Task Runners in Hooks

Reference Taskfile, Justfile, or Makefile targets in hooks:

```toml
[pre-start]
setup = "task install"

[pre-merge]
validate = "just test lint"
```

## See Also

- [`wt merge`](https://worktrunk.dev/merge/) — Runs hooks automatically during
  merge
- [`wt switch`](https://worktrunk.dev/switch/) — Runs pre-start/post-start
  hooks on `--create`
- [`wt config approvals`](https://worktrunk.dev/config/#wt-config-approvals) —
  Manage approvals
- [`wt config state logs`](https://worktrunk.dev/config/#wt-config-state-logs)
  — Access background hook logs
- [`wt step copy-ignored`](https://worktrunk.dev/step/#wt-step-copy-ignored) —
  Copy gitignored files between worktrees
- [`wt step tether`](https://worktrunk.dev/step/#wt-step-tether) — Run process
  with lifecycle tied to worktree
- `wt config` — Manage user and project configuration
- [Installation](./installation.md) — All install methods

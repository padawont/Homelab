---
title: "Worktrunk Scripts and Automation"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags:
  - "worktrunk"
  - "automation"
  - "scripts"
  - "aliases"
sources:
  - "https://worktrunk.dev/extending/"
  - "https://worktrunk.dev/tips-patterns/"
  - "https://incident.io/blog/shipping-faster-with-claude-code-and-git-worktrees"
last_audit_date: 2026-06-07
---

# Worktrunk Scripts and Automation

Worktrunk provides multiple mechanism layers for automation, from simple shell aliases to full hook-based pipelines. This note covers every layer with copy-paste-ready examples.

---

## Shell Aliases

Shell aliases and functions live in your `.bashrc` or `.zshrc` depending on your shell.

### Quick Worktree + Agent Launch

The most common alias creates a worktree and immediately launches an AI agent:

```bash
alias wsc='wt switch --create --execute=claude'
```

Usage:

```bash
wsc new-feature                  # Creates worktree, runs hooks, launches Claude
wsc feature -- 'Fix GH #322'    # Runs `claude 'Fix GH #322'`
```

For OpenCode instead of Claude:

```bash
alias wso='wt switch --create --execute=opencode --'
wso feat-auth 'Implement basic auth middleware'
```

### The `w` Bash Function (incident.io Pattern)

The incident.io team built a comprehensive `w` function that auto-completes worktrees, creates them automatically, and runs commands in the worktree context without changing directories:

```bash
# ~/.zshrc or ~/.bashrc
w() {
  local repo=${1:?Usage: w <repo> <branch> [command...]}
  local branch=${2:?Usage: w <repo> <branch> [command...]}
  shift 2

  local worktree_root="$HOME/projects/worktrees"
  local worktree_path="$worktree_root/$repo/$branch"

  if [ ! -d "$worktree_path" ]; then
    mkdir -p "$worktree_root/$repo"
    git -C "$HOME/projects/$repo" worktree add "$worktree_path" "$branch" 2>/dev/null \
      || git -C "$HOME/projects/$repo" worktree add -b "$branch" "$worktree_path" "$(git -C "$HOME/projects/$repo" remote show origin | sed -n '/HEAD branch/p' | awk '{print $NF}')"
  fi

  if [ $# -eq 0 ]; then
    cd "$worktree_path" && exec $SHELL
  else
    cd "$worktree_path" && "$@"
  fi
}

# Tab completion for w()
if [[ -n "$ZSH_VERSION" ]]; then
  _w() {
    local repos=($(ls -d ~/projects/*/ 2>/dev/null | xargs -n1 basename))
    _arguments '1:repo:(${repos[@]})' '*::command: _normal'
  }
  compdef _w w
fi
```

Usage:

```bash
w myproject new-feature                  # Create + cd into worktree
w myproject new-feature claude           # Create + launch Claude in worktree
w myproject new-feature git status       # Run git status without cd
w myproject new-feature git commit -m "fix: the thing"
```

The auto-completion suggests existing worktrees and repositories. Commands execute inside the worktree directory without leaving your current shell.

---

## Worktrunk TOML Aliases

Aliases are defined under `[aliases]` in your Worktrunk config (`~/.config/worktrunk/config.toml` or `$REPO/.config/wt.toml`). They become available as `wt <name>`.

### Basic Aliases

```toml
# ~/.config/worktrunk/config.toml
[aliases]
# Open this worktree's dev server
open = "open http://localhost:{{ branch | hash_port }}"

# Test with branch-specific features
test-cmd = "cargo test --features {{ vars.features | default('default') }}"

# Switch via the interactive picker, print the chosen branch
pick = "wt switch --format=json | jq -r '.branch'"

# Deploy with env-specific config
deploy = "fly deploy --config=fly.{{ env }}.toml --app=myapp-{{ branch }}"

# Quick log from current branch
since-main = "git log --oneline {{ default_branch }}..HEAD"
```

Usage:

```bash
wt open
wt deploy --env=staging
wt since-main
```

Aliases use Worktrunk's template engine — variables like `{{ branch }}`, `{{ default_branch }}`, `{{ worktree_path }}`, and filters like `hash_port`, `sanitize`, `sanitize_db` are all available.

### Multi-Step Pipelines

Use `[[aliases.NAME]]` for sequential pipeline steps. Keys within a step run concurrently; steps run in order; a failure aborts the remainder.

```toml
# ~/.config/worktrunk/config.toml
[[aliases.release]]
test = "cargo test"

[[aliases.release]]
build = "cargo build --release"
package = "cargo package --no-verify"

[[aliases.release]]
publish = "cargo publish {{ args }}"
```

Usage:

```bash
wt release                          # Runs test → build+package → publish
wt release -- --dry-run             # Forwards --dry-run to publish step
```

Every step sees the same `{{ args }}` and bound variables. `wt release -- --dry-run` forwards `--dry-run` to the `publish` step without affecting earlier steps.

### Template Expansion with Smart Routing

The `--KEY=VALUE` pattern binds variables if the template references them, otherwise they fall through to `{{ args }}`:

```toml
[aliases]
greet = "echo Hello, {{ name }}! Args: {{ args }}"
```

```bash
wt greet --name=World               # Binds to {{ name }} → "Hello, World! Args:"
wt greet --name=World --extra        # Binds name, extra goes to {{ args }}
                                     # → "Hello, World! Args: extra"
```

Tokens after `--` forward unconditionally, bypassing binding:

```bash
wt deploy -- --branch=foo           # Forwards literally even if template uses {{ branch }}
```

### Deferred Template Expansion for Nested `wt` Commands

When an alias calls a nested `wt` command, wrap the inner template in `{% raw %}...{% endraw %}` so it expands in the inner command's context, not the outer one:

```toml
[aliases]
echo-target = "wt switch {{ args }} --no-cd --execute 'echo {% raw %}{{ worktree_path }}{% endraw %}'"
```

```bash
wt echo-target other    # Prints the path of the "other" worktree, not the current one
```

### Inspect and Debug Aliases

```bash
wt config alias show deploy              # Print the template
wt config alias dry-run deploy           # Print rendered command without executing
wt config alias dry-run deploy -- --env=staging  # Preview with args
```

---

## Custom Subcommands

Any executable named `wt-<name>` on `PATH` becomes available as `wt <name>`. This is the same pattern git uses for `git-foo`.

```bash
#!/usr/bin/env bash
# Place this as `wt-sync` somewhere on PATH, e.g. ~/.local/bin/wt-sync
# Then run: wt sync origin

set -euo pipefail

if [ $# -eq 0 ]; then
  echo "Usage: wt sync <remote>" >&2
  exit 1
fi

REMOTE="$1"

# Fetch all remotes
git fetch --all --prune

# Rebase all worktree branches in dependency order
for branch in $(wt list --format=json | jq -r '.[].branch'); do
  echo "=== Syncing $branch ==="
  wt switch "$branch" --no-cd
  git rebase "$REMOTE/$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo main)" || true
done
```

Arguments pass through verbatim, stdio is inherited, and the child's exit code propagates unchanged.

**Community example:** [`worktrunk-sync`](https://github.com/pablospe/worktrunk-sync) rebases stacked worktree branches in dependency order inferred from git history. Install with `cargo install worktrunk-sync`, then run as `wt sync`.

---

## `--execute` Flag

The `--execute` (short: `-x`) flag on `wt switch` runs a command in the newly created worktree after hooks complete. This is the primary way to launch agents.

```bash
# Launch OpenCode with a specific task
wt switch --create opencode-integration -x opencode -- "Add MCP server integration"

# Launch Claude with plan mode
wt switch --create refactor-auth -x claude -- "Plan and implement auth refactor"

# Run a build command instead of an agent
wt switch --create ci-fix -x 'npm run build && npm test'

# Open a shell in the new worktree
wt switch --create debug -x '$SHELL'
```

The `--` separator forwards everything after it as arguments to the `--execute` command. Hooks (`pre-start`, `post-start`) run before the `--execute` command, so dependencies and dev servers are ready.

---

## Hook-Based Automation

Hooks are shell commands in TOML config that run automatically at lifecycle events. Ten hooks cover five lifecycle events:

| Event    | Pre- (blocking) | Post- (background) |
|----------|-----------------|-------------------|
| switch   | `pre-switch`    | `post-switch`     |
| start    | `pre-start`     | `post-start`      |
| commit   | `pre-commit`    | `post-commit`     |
| merge    | `pre-merge`     | `post-merge`      |
| remove   | `pre-remove`    | `post-remove`     |

- **`pre-*` hooks** block the operation. Failure aborts the operation.
- **`post-*` hooks** run in the background. Failure is logged but does not abort.

### Auto-Install Dependencies (pre-start)

```toml
# .config/wt.toml
[pre-start]
deps = "npm ci"
```

For pipelined setup with copy-ignored (to reuse cached `node_modules`):

```toml
[[pre-start]]
copy = "wt step copy-ignored"    # Copy gitignored files from another worktree

[[pre-start]]
install = "npm ci"               # Reuses cached packages from copy
```

### Start Dev Servers (post-start)

```toml
# .config/wt.toml
[post-start]
server = "wt step tether -- npm run dev -- --port {{ branch | hash_port }}"
```

`wt step tether` runs the server in its own process group. When the worktree is removed, the entire process group is torn down automatically — no `pre-remove` cleanup needed.

### Run Tests (pre-merge)

```toml
# .config/wt.toml
[pre-merge]
test = "npm test"
lint = "npm run lint"
typecheck = "npm run typecheck"
```

Keys within a hook run in parallel. The merge proceeds only if all commands succeed.

### Progressive Validation

Split checks across hook types — quick feedback before each commit, expensive suites before merge:

```toml
[[pre-commit]]
lint = "npm run lint"
typecheck = "npm run typecheck"

[[pre-merge]]
test = "npm test"
build = "npm run build"
```

`pre-commit` runs on every squash commit during `wt merge`; `pre-merge` runs once per merge after the rebase.

### Target-Specific Hooks

Branch on `{{ target }}` to vary behavior per merge destination:

```toml
[post-merge]
deploy = """
if [ {{ target }} = main ]; then
    npm run deploy:production
elif [ {{ target }} = staging ]; then
    npm run deploy:staging
fi
"""
```

### Database Per Worktree

A pipeline sets up isolated databases per worktree:

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

---

## CI Integration

### `--yes` for Approval Bypass

In CI environments where no TTY is available, use `--yes` to bypass approval prompts:

```bash
# Non-interactive merge (e.g., in a CI pipeline)
wt -y merge

# Non-interactive alias invocation
wt -y deploy --env=staging

# Hook execution with approval skip
wt hook pre-merge --yes
```

### Environment Variable Override: Manual Commit Messages

Override `WORKTRUNK_COMMIT__GENERATION__COMMAND` to replace the LLM commit message generator with a custom script. Useful for CI where you want deterministic commits:

```bash
# In CI: use a static commit message
WORKTRUNK_COMMIT__GENERATION__COMMAND='echo "ci: automated merge"' wt -y merge
```

Or to use a mock for testing:

```bash
# Mock commit generation
WORKTRUNK_COMMIT__GENERATION__COMMAND='echo "test: automated commit"' wt merge
```

---

## Task Runners in Hooks

Reference Taskfile, Justfile, or Makefile targets directly in hooks:

```toml
# Taskfile (go-task)
[pre-start]
"setup" = "task install"

[pre-merge]
"validate" = "task test lint"

# Justfile
[pre-start]
"setup" = "just install"

[pre-merge]
"validate" = "just test lint"

# Makefile
[pre-start]
"setup" = "make install"

[pre-merge]
"validate" = "make test lint"
```

This keeps your build logic in your build system and only uses Worktrunk hooks for lifecycle wiring.

---

## Shell Alias for Tailing Hook Logs

Follow background hook output in real time:

```bash
# Basic alias
# Wrap in a function so $1 refers to the argument
wtlog() { tail -f "$(wt config state logs get --hook="$1")"; }

# Usage:
wtlog user:post-start:server               # Tail the server hook log
wtlog project:post-start:build             # Tail a project-defined hook
```

The `--hook` format is `source:hook-type:name`, e.g., `project:post-start:build`, `user:pre-merge:test`. Use `wt config state logs get` (without arguments) to list all available logs.

For a more sophisticated wrapper:

```bash
# ~/.zshrc
wtlog() {
  local hook="${1:?Usage: wtlog <hook>}"
  local log_path
  log_path="$(wt config state logs get --hook="$hook" 2>/dev/null)"
  if [ -z "$log_path" ] || [ ! -f "$log_path" ]; then
    echo "No log found for hook: $hook" >&2
    echo "Available hooks:" >&2
    wt config state logs get >&2
    return 1
  fi
  tail -f "$log_path"
}
```

---

## Manual Commit Messages with `$EDITOR`

By default, Worktrunk generates commit messages via an LLM. To write messages by hand, override the commit generation command:

```toml
# ~/.config/worktrunk/config.toml
[commit.generation]
command = '''f=$(mktemp); printf '\n\n' > "$f"; sed 's/^/# /' >> "$f"; ${EDITOR:-vi} "$f" < /dev/tty > /dev/tty; grep -v '^#' "$f"'''
```

This opens the rendered prompt (diff, branch name, stats) commented out with `#` prefixes in your editor. Blank lines at the top give space to type. Commented lines are stripped on save.

To keep the LLM as default but use the editor for specific merges, create an alias:

```toml
# ~/.config/worktrunk/config.toml
[aliases]
mc = '''WORKTRUNK_COMMIT__GENERATION__COMMAND='f=$(mktemp); printf "\n\n" > "$f"; sed "s/^/# /" >> "$f"; ${EDITOR:-vi} "$f" < /dev/tty > /dev/tty; grep -v "^#" "$f"' wt merge'''
```

```bash
wt mc      # Opens editor; LLM not used for this merge
wt merge   # Normal merge with LLM commit message
```

---

## Alias Recipe: Rebase Every Worktree onto Its Upstream

```toml
# ~/.config/worktrunk/config.toml
[aliases]
up = '''
git fetch --all --prune && wt step for-each -- sh -c '
  git rev-parse --verify -q @{u} >/dev/null || exit 0
  g=$(git rev-parse --git-dir)
  test -d "$g/rebase-merge" -o -d "$g/rebase-apply" && exit 0
  git update-index --refresh -q >/dev/null || true
  git rebase @{u} --no-autostash || git rebase --abort
'
'''
```

Usage:

```bash
wt up   # Fetches all remotes, then rebases every worktree onto its upstream
```

What it does:
1. `git fetch --all --prune` — updates all remote refs
2. `wt step for-each` — iterates every linked worktree
3. Skips branches without an upstream (`@{u}` does not resolve)
4. Refreshes the index to avoid false dirty-state detection
5. Skips branches that are mid-rebase (rebase directories exist)
6. Rebases onto upstream; auto-aborts on conflict

---

## Alias Recipe: Move or Copy In-Progress Changes to a New Worktree

When `wt switch --create` lands in a clean worktree, use `git stash` to carry staged, unstaged, and untracked changes along:

```toml
# .config/wt.toml
[aliases]
move-changes = '''
if git diff --quiet HEAD && test -z "$(git ls-files --others --exclude-standard)"; then
  wt switch --create {{ to }} --execute="{{ args }}"
else
  git stash push --include-untracked --quiet
  wt switch --create {{ to }} --execute="git stash pop --index; {{ args }}"
fi
'''
```

Usage:

```bash
wt move-changes --to=feature-xyz                    # Move changes, no extra command
wt move-changes --to=feature-xyz -- claude          # Move changes, launch Claude
```

**To copy instead of move**, add `git stash apply --index --quiet` right after the push:

```toml
[aliases]
copy-changes = '''
if git diff --quiet HEAD && test -z "$(git ls-files --others --exclude-standard)"; then
  wt switch --create {{ to }} --execute="{{ args }}"
else
  git stash push --include-untracked --quiet
  git stash apply --index --quiet                    # Keep changes in current worktree too
  wt switch --create {{ to }} --execute="git stash pop --index; {{ args }}"
fi
'''
```

The guard (`git diff --quiet HEAD && ...`) skips the stash when nothing is in flight. Otherwise `git stash push` captures everything, and `--execute` pops it in the new worktree with the staged/unstaged split intact.

---

## See Also

- [Hooks Reference](./hooks.md) — Hook types, lifecycle, template variables, recipes
- [Configuration](./configuration.md) — User and project config reference (`worktrunk.toml`)

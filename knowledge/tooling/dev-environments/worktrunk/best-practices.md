---
title: "Worktrunk Best Practices"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags:
  - worktrunk
  - best-practices
  - community
sources:
  - url: "https://worktrunk.dev/tips-patterns/"
    title: "Worktrunk Tips and Patterns"
  - url: "https://www.anthropic.com/engineering/claude-code-best-practices"
    title: "Claude Code Best Practices"
  - url: "https://incident.io/blog/shipping-faster-with-claude-code-and-git-worktrees"
    title: "Shipping faster with Claude Code and Git Worktrees"
  - url: "https://github.com/anthropics/claude-code/issues/1052"
    title: "GitHub: Claude Code Worktree Patterns Discussion"
  - url: "https://worktrunk.dev/faq/"
    title: "Worktrunk FAQ"
last_audit_date: 2026-06-07
---

# Worktrunk Best Practices

Best practices for using Worktrunk in development workflows, drawn from official documentation and community experience.

## Overview

Worktrunk is a Git worktree manager that streamlines working with multiple branches simultaneously. This document captures recommended patterns for development servers, databases, CI/CD integration, and AI-agent-assisted workflows.

## Official Worktrunk Recommended Practices

### Dev Server per Worktree

Run a dedicated development server for each worktree to avoid port collisions and configuration overlap. Use `wt step tether` and the `hash_port` filter to run each worktree's dev server on a deterministic port based on a hash of the branch name:

```toml
[post-start]
server = "wt step tether -- npm run dev -- --port {{ branch | hash_port }}"

[list]
url = "http://localhost:{{ branch | hash_port }}"
```

[`wt step tether`](https://worktrunk.dev/step/#wt-step-tether) runs the server in its own process group and tears it down when the worktree is removed, so no `pre-remove` hook is needed. The URL column in `wt list` shows each worktree's dev server.

### Database per Worktree

Use a `[[post-start]]` pipeline to spin up an isolated database instance for each worktree. A pipeline sets up names and ports as vars, then later steps reference them:

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

The first pipeline step derives values from the branch and stores them as vars. The second step references `{{ vars.container }}` and `{{ vars.port }}` — expanded at execution time, after the vars are set. `pre-remove` reads the same vars to stop the container. Each worktree gets its own isolated database, preventing state leakage between branches.

### Eliminate Cold Starts

File copy operations on first use can cause significant delays. Use `wt step copy-ignored` in the `post-start` hook to pre-populate ignored or generated files (e.g., `node_modules`, `.venv`, build artifacts):

```toml
[post-start]
copy = "wt step copy-ignored"
```

When another hook depends on the copy — for example, copying `node_modules/` before `pnpm install` so the install reuses cached packages — sequence them with a `[[post-start]]` pipeline:

```toml
[[post-start]]
copy = "wt step copy-ignored"

[[post-start]]
install = "pnpm install"
```

This mirrors `.gitignore`-listed files from the primary working tree into the new worktree, avoiding lengthy install or build steps.

### Progressive Validation

Separate fast from expensive validation checks to match the right feedback loop:

- **Pre-commit hooks**: Run quick checks (linting, formatting, type-checking). These must finish in seconds.
- **Pre-merge hooks**: Run the full test suite, integration tests, and any expensive analysis. These can take minutes.

Configure target-specific hooks in Worktrunk:

```toml
[[pre-commit]]
fmt = "cargo fmt --check"
clippy = "cargo clippy -- -D warnings"

[[pre-merge]]
test = "cargo test --all-features"
```

### Target-Specific Hooks

Hooks can behave differently depending on the merge target (e.g., merging to `main` vs. `staging`). Use the `{{ target }}` template variable in `post-merge` to branch behavior with shell conditionals:

```toml
post-merge = """
if [ {{ target }} = main ]; then
    wt exec deploy-production
elif [ {{ target }} = staging ]; then
    wt exec deploy-staging
fi
"""
```

`{{ target }}` is the branch being merged into. `post-merge` runs in the target's worktree (or the primary worktree if target has none), so deploy commands see the merged code. This allows deploying to production vs. staging based on where the branch is merged.

## Community Patterns

### Anthropic — Claude Code Worktree Pattern

Anthropic's engineering team advocates pairing Claude Code with Git worktrees for safe, isolated agent execution. Each Claude Code session operates in its own worktree, preventing one session from interfering with another or with the main branch. Key practices include:

- Creating a fresh worktree per Claude Code task
- Using `.gitignore` and `wt step copy-ignored` to pre-warm dependencies
- Cleaning up the worktree when the task completes

### incident.io — Custom `w` Bash Function

The incident.io engineering team published a workflow for shipping faster with Claude Code and Git worktrees. Their approach centers on a custom `w` bash function that:

1. Creates a new branch from the latest `main`
2. Sets up a Git worktree via Worktrunk
3. Launches Claude Code inside that worktree

This reduces branch-and-agent setup to a single command, removing friction from the context-switching loop.

### Stacked Branches with `worktrunk-sync`

The community-developed [`worktrunk-sync`](https://github.com/pablospe/worktrunk-sync) tool enables stacked branch workflows on top of Worktrunk. It auto-detects the branch dependency tree from git history and rebases each branch onto its parent in topological order, allowing developers to work on multiple chained changes without manually juggling rebases. Each branch in the stack gets its own worktree with isolated state.

Install with `cargo install worktrunk-sync` and run as `wt sync` (via custom subcommands).

### Tmux/Zellij Agent Handoffs

Some teams pair Worktrunk with terminal multiplexers (Tmux or Zellij) to manage multiple agent sessions. Each worktree gets its own pane or window, and agents can be handed off between sessions without losing context. This is particularly useful when long-running tasks (e.g., integration tests or model training) need to continue while a developer switches to another branch.

### Subdomain Routing with Caddy

For web applications, Caddy can route subdomains to individual worktree dev servers. Given a worktree on port 4002, a Caddyfile mapping `feature-xyz.dev.localhost` to `localhost:4002` gives each branch an accessible, predictable URL. This is commonly paired with the `hash_port` filter to compute subdomain names from branch names automatically.

### Bare Repository Layout

Some teams prefer a bare-repository layout where the `.git` directory sits outside the working tree. This gives more control over where worktrees live and makes it easier to share the repository across multiple environments. Worktrunk supports this by pointing to a bare repo via `--git-dir` or by configuring `wt init` on a bare clone.

### cmux Workspace per Worktree

The `cmux` tool can be used to define a Tmuxinator-style workspace for each worktree. A pre-start hook generates and launches a cmux session named after the branch, pre-configured with the right editor, terminal panes, and dev server. (cmux requires `pre-start` rather than `post-start` because it restricts socket access to foreground processes — `post-*` hooks run detached and would break the ancestry chain.) This automates the full environment setup per worktree.

### Monitor Hook Logs with Tail

Worktrunk hooks produce output logged to `.git/wt/logs/`. Use `wt config state logs get --hook=` to find the path to a specific hook's log file. Running `tail -f` in a dedicated terminal pane allows developers to observe post-start, pre-commit, and pre-merge execution in real time:

```bash
tail -f "$(wt config state logs get --hook=user:post-start:server)"
```

The `--hook` format is `source:hook-type:name` — e.g., `project:post-start:build` for project-defined hooks. Use `wt config state logs get` without arguments to list all available logs.

For a simpler approach, you can tail the log directory directly:

```bash
tail -f .git/wt/logs/**/*.log
```

Create an alias for frequent use:

```bash
alias wtlog='f() { tail -f "$(wt config state logs get --hook="$1")"; }; f'
```

This is useful for debugging hook failures and understanding hook execution order.

## Agent Workflow Best Practices

### One Worktree per AI Agent

Each AI agent (e.g., Claude Code, Copilot, Cursor) should operate in its own isolated worktree. This guarantees:

- No file-system conflicts between concurrent agent sessions
- Independent dependency states
- Clear separation of agent-generated changes from human work
- Easy rollback by removing the worktree

### Use `-x`/`--execute` to Launch Agents

Worktrunk's `wt switch` with `--create` accepts a `-x`/`--execute` flag that runs a command after the worktree is created. Pass the agent launch command directly:

```bash
wt switch --create feature/agent-task -x claude
```

This creates the branch, sets up the worktree (including post-start hooks), and launches the agent in a single step.

### Configure Post-Start Hooks for Automated Setup

Ensure every agent worktree is ready to work immediately by configuring post-start hooks that:

- Install dependencies (`npm install`, `pip install`, `cargo build`)
- Copy cached files (`wt step copy-ignored`)
- Start required services (database, message queue)
- Launch the dev server

This eliminates the manual setup step that agents cannot perform on their own.

### Track Agent Status with Markers

Teams using multiple concurrent agents can track worktree status with branch naming conventions or markers. A common pattern uses the worktree name to indicate agent activity:

- `agent/<feature-name>` — agent is actively working
- `agent/<feature-name>/review` — agent work is ready for human review
- `agent/<feature-name>/done` — agent has completed the task

Worktrunk branch names serve as visible status indicators in `wt list` output.

### Clean Up with `wt remove`

When an agent task is complete or abandoned, remove the worktree immediately:

```bash
wt remove agent/completed-task
```

This prevents worktree accumulation, frees disk space, and keeps the worktree list focused on active branches. Combined with a `post-remove` hook, cleanup can also tear down associated services (Docker containers, databases).

---

## See Also

- [Git Worktree Overview](../../version-control/git/worktree/overview.md) — The underlying `git worktree` feature and its CLI
- [Hooks Reference](./hooks.md) — Hook types, lifecycle, template variables, recipes
- [Configuration](./configuration.md) — User and project config reference (`worktrunk.toml`)

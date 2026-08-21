---
title: "Worktrunk hooks, LLM commits, and agent workflows"
status: draft
author: "padawont"
date: 2026-08-20
tags: [git, worktrees, cli, ai-agents, automation, hooks]
sources:
  - url: "https://worktrunk.dev/hook/"
    title: "wt hook docs"
  - url: "https://worktrunk.dev/extending/"
    title: "Extending Worktrunk docs"
  - url: "https://worktrunk.dev/llm-commits/"
    title: "LLM commit messages docs"
  - url: "https://worktrunk.dev/claude-code/"
    title: "Agent integration docs"
  - url: "https://worktrunk.dev/tips-patterns/"
    title: "Tips & patterns docs"
last_audit_date: 2026-08-20
related_docs:
  - "./02_Knowledge/technologies/tools/worktrunk/overview.md"
  - "./02_Knowledge/technologies/tools/worktrunk/commands.md"
  - "./02_Knowledge/technologies/tools/worktrunk/install-config.md"
---

# Worktrunk hooks, LLM commits, and agent workflows

## Overview

Worktrunk automates the worktree lifecycle with hooks, generates commit messages via any LLM CLI, and ships agent-CLI plugins for parallel AI-agent workflows.

## Details

### Hooks

Shell commands run at lifecycle events; each has a blocking `pre-` variant (failure aborts the operation) and a background `post-` variant. Ten hooks cover five events: switch, create, commit, merge, remove.

| Hook | Purpose |
|---|---|
| `pre-switch` / `post-switch` | Run before/after switching to a worktree |
| `pre-start` / `post-start` | Once on worktree creation: deps, env, dev servers (post-start preferred over pre-start) |
| `pre-commit` / `post-commit` | Lint/typecheck before squash commit; notifications after |
| `pre-merge` / `post-merge` | Tests/validation before merge; deploy/notify after |
| `pre-remove` / `post-remove` | Cleanup before deletion; teardown after |

Defined in TOML as a single string, a table (concurrent commands), or a `[[hook]]` pipeline (ordered steps). Project hooks live in `.config/wt.toml` (shared, require first-run approval, stored in `~/.config/worktrunk/approvals.toml`); user hooks in `~/.config/worktrunk/config.toml` (no approval). Skip with `--no-hooks`, bypass prompts with `--yes`.

Templates use Jinja2-style variables (`{{ branch }}`, `{{ worktree_path }}`, `{{ target }}`, `{{ vars.<key> }}`, …) and filters (`sanitize`, `hash_port`, `sanitize_db`, `codename(n)`, `hash`, …). Hooks receive all variables as JSON on stdin.

Example — real config (dev server per worktree):

```toml
# .config/wt.toml
[post-start]
server = "wt step tether -- npm run dev -- --port {{ branch | hash_port }}"
```

### LLM commit messages

`wt merge`, `wt step commit`, and `wt step squash` build a templated prompt and pipe it to an external command (Claude Code, Codex, OpenCode, `llm`, `aichat`). Configured in user config:

Example — abstract:

```toml
# ~/.config/worktrunk/config.toml
[commit.generation]
command = "claude -p --no-session-persistence --model=haiku --tools=''"
template = "..."      # minijinja prompt template (git_diff, git_diff_stat, branch, …)
squash-template = "..." # extra vars: commit_details, target_branch
```

`template-append` adds style-guide fragments (conventional commits, issue refs) from user and/or project config without rewriting the template. Branch summaries reuse the same command for `wt list --full` and the picker. Without an LLM configured, messages fall back to deterministic filename-based text.

### copy-ignored

`wt step copy-ignored` copies gitignored files (build caches, `node_modules/`, `.env`) between worktrees to eliminate cold starts — reflink-based, ~20s vs 2m for a 14GB `target/`. Optional `.worktreeinclude` limits what's copied; `--require-include` matches Claude Code desktop behavior.

### Agent workflows

Parallel agents: each gets a worktree via `wt switch -c -x <agent>`; `-x` replaces the process after switching, args after `--` are passed to the agent.

Example — abstract:

```
wt switch -x claude -c feature-a -- 'Add user authentication'
wt switch -x claude -c feature-b -- 'Fix the pagination bug'
```

PR workflow: `wt step commit` → `gh pr create` (or `glab mr create`) → merge on the forge → `wt remove`. Local merge: `wt merge` (squash → rebase → fast-forward → cleanup).

Agent plugins (`wt config plugins claude|codex|opencode install`, or `gemini extensions install …`) add activity tracking (working/waiting status markers in `wt list`; manual via `wt config state marker set`); the Claude, Codex, and OpenCode plugins also add a configuration skill. Claude Code additionally adds worktree isolation (agent-created worktrees route through `wt switch --create`) and a `--format=claude-code` statusline.

## Sources / Further Reading

- Hooks https://worktrunk.dev/hook/ · Extending (aliases, custom subcommands) https://worktrunk.dev/extending/ · LLM commits https://worktrunk.dev/llm-commits/ · Agent integration https://worktrunk.dev/claude-code/ · Tips https://worktrunk.dev/tips-patterns/
- Commands: `./02_Knowledge/technologies/tools/worktrunk/commands.md` · Install/config: `./02_Knowledge/technologies/tools/worktrunk/install-config.md`.

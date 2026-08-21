---
title: "Worktrunk CLI for branch-addressed git worktrees"
status: draft
author: "padawont"
date: 2026-08-20
tags: [git, worktrees, cli, ai-agents, developer-tools]
sources:
  - url: "https://worktrunk.dev/"
    title: "Worktrunk docs"
  - url: "https://github.com/max-sixty/worktrunk"
    title: "max-sixty/worktrunk GitHub README"
  - url: "https://git-scm.com/docs/git-worktree"
    title: "git-worktree documentation"
  - url: "https://www.anthropic.com/engineering/claude-code-best-practices"
    title: "Anthropic: best practices for agentic coding"
  - url: "https://incident.io/blog/shipping-faster-with-claude-code-and-git-worktrees"
    title: "incident.io: shipping faster with Claude Code + git worktrees"
last_audit_date: 2026-08-20
related_docs:
  - "./02_Knowledge/technologies/tools/worktrunk/commands.md"
  - "./02_Knowledge/technologies/tools/worktrunk/automation.md"
  - "./02_Knowledge/technologies/tools/worktrunk/install-config.md"
---

# Worktrunk CLI for branch-addressed git worktrees

## Overview

Worktrunk is a CLI (`wt`) for git worktree management, designed to run AI agents (Claude Code, Codex, OpenCode, Gemini CLI) in parallel. It addresses worktrees by branch name and computes paths from a configurable template, making worktrees as easy to use as branches. MIT/Apache-2.0 licensed.

## Details

### Git worktrees

Git's native worktree feature gives each branch its own working directory, so parallel agents don't step on each other's changes. The native UX is clunky — creating one requires typing the branch name multiple times: `git worktree add -b feat ../repo.feat` then `cd ../repo.feat`. Worktrunk removes that friction.

### Branch-addressed worktrees

Worktrees are addressed by branch name; paths are derived from a template (default: sibling directory `<repo>.<branch-sanitized>`). Commands that take a branch also accept the path of the worktree it is checked out in.

Example — abstract:

```
wt switch --create feature-auth
# ✓ Created branch feature-auth from main and worktree @ ~/repo.feature-auth
```

### Core commands vs plain git

| Task | Worktrunk | Plain git |
|---|---|---|
| Switch worktrees | `wt switch feat` | `cd ../repo.feat` |
| Create + start agent | `wt switch -c -x claude feat` | `git worktree add -b feat ../repo.feat && cd ../repo.feat && claude` |
| Clean up | `wt remove` | `git worktree remove` + `git branch -d` |
| List with status | `wt list` | `git worktree list` (paths + branch, no status) |

### Why it fits the homelab

The repo's own git guidelines use worktree-style branch naming (the `knowledge/39-worktrunk` example in the root `AGENTS.md`). Worktrunk is relevant here as a tool for running parallel opencode/Claude agents, each in an isolated worktree with hooks that automate setup (deps, env, dev servers) and an LLM-backed merge/commit path — see `./02_Knowledge/technologies/tools/worktrunk/automation.md`.

## Sources / Further Reading

- [Worktrunk site](https://worktrunk.dev/) · [GitHub](https://github.com/max-sixty/worktrunk)
- [git-worktree docs](https://git-scm.com/docs/git-worktree)
- See `./02_Knowledge/technologies/tools/worktrunk/commands.md` for command details, `./02_Knowledge/technologies/tools/worktrunk/automation.md` for hooks/LLM commits, and `./02_Knowledge/technologies/tools/worktrunk/install-config.md` for install and shell integration.

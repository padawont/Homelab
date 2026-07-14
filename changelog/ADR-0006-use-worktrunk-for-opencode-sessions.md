# ADR-0006: Use Worktrunk for OpenCode Sessions

## README.md

# ADR 0006: Use Worktrunk for OpenCode Multi-Session Workflows

Adopt [worktrunk](https://worktrunk.dev) as the standard tool for managing git worktree-backed OpenCode sessions, with `.config/wt.toml` as the declarative project-level configuration.

## Part of

- **Epic**: #37 — Worktrunk for OpenCode Multi-Session Workflows
- **Idea**: #38 — Use worktrunk for Multi-Session Development with OpenCode
- **Knowledge**: `knowledge/tooling/dev-environments/worktrunk/`

## overview.md

---
adr: 0006
title: "Use Worktrunk for OpenCode Multi-Session Workflows"
author: refactorartist
status: final
topic: development-workflow
technology: "worktrunk"
date: 2026-06-08
date-proposed: 2026-06-07
history: "https://github.com/RunicEngines/knowledge-base/pull/56"
context: >
  Multiple OpenCode sessions need isolated git worktrees — one per branch,
  feature, or task. Manual `git worktree` management is error-prone,
  inconsistent across developers, and lacks a unified configuration to
  standardise worktree lifecycle (create, switch, prune) across the
  organisation.
decision: >
  Adopt worktrunk CLI as the standard tool for worktree-backed OpenCode
  sessions. Each project MUST commit a `.config/wt.toml` as the source of
  truth for worktree configuration. Session isolation is enforced via git
  worktrees; bootstrap consistency is achieved through a `[post-start]` hook
  that runs `wt step copy-ignored` to propagate `.gitignore`-matched files
  from the primary worktree into new session worktrees.
consequences: >
  Easier: session creation, switching, cleanup, team consistency, CI
  integration. Harder: developers must install and learn worktrunk; ongoing
  maintenance of `.config/wt.toml` per project; tool churn risk if worktrunk
  changes its interface.
sources:
  - "https://worktrunk.dev"
  - "https://github.com/max-sixty/worktrunk"
references:
  - "knowledge/tooling/dev-environments/worktrunk/"
  - "adr/0002-github-etiquettes/"
---

# ADR 0006: Use Worktrunk for OpenCode Multi-Session Workflows

## Status

Final (2026-06-08)

## Context and Problem Statement

OpenCode sessions require isolated working directories so that parallel work
streams (different branches, features, or experiments) do not interfere with
each other. Git worktrees provide this isolation natively, but managing them
manually is ad hoc and inconsistent:

- Developers use different approaches — raw `git worktree`, shell aliases,
  tmux sessions, or multiple clones — producing divergent workflows.
- No shared configuration exists for naming, path templates, or cleanup
  policies.
- Bootstrap steps (copying `.env`, installing dependencies) are done by hand
  or forgotten entirely, causing session startup failures.
- There is no standard way to list active sessions and their state.

As the number of concurrent OpenCode sessions grows, this inconsistency
creates friction and slows down development.

## Decision

All RunicEngines repositories that use OpenCode sessions MUST adopt the
following conventions:

1. **worktrunk CLI** is the standard tool for creating, switching, and
   removing worktree-backed sessions.

2. **`.config/wt.toml`** at the repository root is the committed source of
   truth for project-level worktree configuration. It defines the worktree
   path template, hooks, and branch naming conventions.

3. **Dotfile bootstrap** — a `[post-start]` hook MUST run
   `wt step copy-ignored` to copy all `.gitignore`-matched files (`.env`,
   `node_modules/`, `.venv/`, build caches, etc.) from the primary worktree
   into newly created session worktrees. This ensures every session starts
   with the environment it needs without manual setup.

   Example `.config/wt.toml` structure:

   ```toml
   [post-start]
   copy = "wt step copy-ignored"
   ```

4. **Worktree naming** follows worktrunk's default path template:
   `<repo>.<branch-sanitized>`. The branch name MUST follow
   [ADR 0002](../0002-github-etiquettes/overview.md#1-branch-naming) —
   `{type}/{issue-number}-{kebab-description}`. The `sanitize` filter
   converts `/` to `-` in the filesystem path, producing paths like
   `knowledge-base.adr-40-use-worktrunk-for-opencode-multi-session-workflows`.

5. **OpenCode integration scope** — The worktrunk OpenCode plugin provides
   activity tracking via status markers in `wt list` only. Worktree lifecycle
   operations (create, switch, remove) are performed directly via the `wt` CLI
   from the shell. Unlike Claude Code, OpenCode's plugin API does not expose
   worktree lifecycle hooks.

## Consequences

### Positive

- **Consistent workflow** — every developer manages sessions the same way.
- **Declarative configuration** — `.config/wt.toml` acts as the single source
  of truth, reviewable in PRs.
- **Automated bootstrapping** — `wt step copy-ignored` eliminates manual
  setup steps and the "forgot to copy .env" class of errors.
- **Unified session visibility** — `wt list` shows all active worktrees,
  their branches, and state.
- **Clean teardown** — `wt remove` handles branch and worktree cleanup.

### Negative / Trade-offs

- **New tool dependency** — developers must install worktrunk and learn its
  subcommands.
- **Configuration maintenance** — each project needs a `.config/wt.toml` that
  stays in sync with its own build/environment requirements.
- **Tool churn risk** — worktrunk is relatively new; interface changes may
  require updates to configuration and workflows.

## Considered Options

### Worktrunk (chosen)

- **Pros**: Full lifecycle automation, declarative TOML config, hooks for
  bootstrap/teardown, unified session listing, growing community adoption.
- **Cons**: New dependency; young project.

### Raw `git worktree`

- **Pros**: Built into git, no additional dependency.
- **Cons**: Fully manual lifecycle, no config, no hooks, no bootstrap
  automation, inconsistent team usage.

### Tmux / Zellij with single worktree

- **Pros**: Familiar terminal multiplexing; no git tooling needed.
- **Cons**: No worktree isolation (single working directory); no session
  lifecycle management.

### Multiple local clones

- **Pros**: Full filesystem isolation.
- **Cons**: Wasted disk space; no shared refs; manual sync overhead; no
  standardised naming.

### Shell aliases wrapping `git worktree`

- **Pros**: Lightweight; no external dependency.
- **Cons**: Ad-hoc, no shared config, no hooks, inconsistent across team.

## Compliance

- Repositories that use OpenCode sessions MUST contain a committed
  `.config/wt.toml`.
- The `.config/wt.toml` MUST define a `[post-start]` hook that invokes
  `wt step copy-ignored`.
- A prek check MUST verify the presence of `.config/wt.toml` in
  repositories that have a `.opencode/` directory or an `opencode.json`
  (indicating OpenCode usage).

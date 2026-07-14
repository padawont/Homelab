---
title: "Worktrunk and OpenCode Integration"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags:
  - worktrunk
  - opencode
  - integration
  - plugins
sources:
  - url: "https://worktrunk.dev/claude-code/"
    title: "Worktrunk Agent Integration"
  - url: "https://github.com/max-sixty/worktrunk"
    title: "Worktrunk GitHub Repository"
  - url: "https://raw.githubusercontent.com/max-sixty/worktrunk/main/dev/opencode-plugin.ts"
    title: "OpenCode Plugin Source"
last_audit_date: 2026-06-07
---

# Worktrunk and OpenCode Integration

Worktrunk ships a plugin for OpenCode that provides activity tracking via session lifecycle hooks. Unlike Claude Code's deeper integration (which also offers worktree isolation and a `/wt-switch-create` command), the OpenCode plugin is limited to status markers in `wt list` because OpenCode's plugin API does not expose worktree lifecycle hooks.

## Plugin Installation

Install the activity-tracking plugin with a single command:

```
wt config plugins opencode install
```

This writes the plugin source to OpenCode's global plugins directory:

```
~/.config/opencode/plugins/worktrunk.ts
```

The path respects `$OPENCODE_CONFIG_DIR` and `$XDG_CONFIG_HOME` if either is set.

### Manual Installation

To install without `wt config plugins`, copy the plugin source directly:

```bash
cp worktrunk.ts ~/.config/opencode/plugins/worktrunk.ts
```

### Uninstallation

```
wt config plugins opencode uninstall
```

Or manually:

```bash
rm ~/.config/opencode/plugins/worktrunk.ts
```

## Plugin Source

The plugin is self-contained at approximately 25 lines. It imports the `Plugin` type from `@opencode-ai/plugin` and handles three session events to set or clear status markers visible in `wt list`.

```typescript
// Worktrunk activity tracking plugin for OpenCode.
//
// Tracks OpenCode session activity per branch, showing status markers in `wt list`:
//   🤖 — agent is working
//   💬 — agent is waiting for input
//
// Installed globally via: wt config plugins opencode install
// Or manually: copy to ~/.config/opencode/plugins/worktrunk.ts

import type { Plugin } from "@opencode-ai/plugin";

export default (async ({ $ }) => {
  return {
    event: async ({ event }) => {
      switch (event.type) {
        case "session.status":
          await $`wt config state marker set ${'🤖'} || true`.quiet();
          break;
        case "session.idle":
          await $`wt config state marker set ${'💬'} || true`.quiet();
          break;
        case "session.deleted":
          await $`wt config state marker clear || true`.quiet();
          break;
      }
    },
  };
}) satisfies Plugin;
```

### Event Handling

| Event | Marker | Meaning |
|---|---|---|
| `session.status` | 🤖 | Agent is actively working (streaming tokens, running tools) |
| `session.idle` | 💬 | Agent is waiting for user input |
| `session.deleted` | *(cleared)* | Session ended; marker is removed entirely |

The `|| true` suffix prevents shell errors from propagating if the `wt` command is not available or worktrunk is not configured. The `.quiet()` method suppresses stdout from the `wt` subcommand.

### Stale Markers

If an OpenCode process is killed forcefully (SIGKILL, system crash), the `session.deleted` event never fires and the marker remains in `wt list`. Clear it manually:

```
wt config state marker clear
```

Or target a specific branch:

```
wt config state marker clear --branch feature-api
```

## LLM Commit Messages with OpenCode

Worktrunk's commit message generation can use OpenCode as the LLM backend. Configure the `[commit.generation]` section in your user config (`~/.config/worktrunk/config.toml`):

```toml
[commit.generation]
command = "opencode run -m anthropic/claude-haiku-4.5 --variant fast"
```

The `--variant fast` flag optimises for speed rather than thoroughness. This is appropriate for commit messages where latency matters more than depth.

After configuration, `wt step commit` (or the pre-commit hook) will generate commit messages using the specified OpenCode model.

> **Project-level config note:** The `command` and `template` keys are only honored from the user config (`~/.config/worktrunk/config.toml`). The project-level file (`.config/wt.toml`) only accepts `template-append` for project-wide commit convention hints.

## Session-to-Worktree Mapping

Worktrunk maps each OpenCode session to a single git worktree. The convention is one branch per session, one worktree per branch. When Worktrunk creates a worktree it follows a sibling directory layout:

```
./
  repo/                    # primary working tree (e.g., main)
  repo.feature-api/        # worktree for feature-api branch
  repo.review-ui/          # worktree for review-ui branch
```

This layout avoids nested `.claude/worktrees/` directories and keeps worktrees visible in the parent directory alongside the main repository.

### Isolation Properties

- Each worktree has its own `node_modules/`, `target/`, or other build artefacts, preventing dependency conflicts between sessions.
- Git branches are isolated per worktree; there is no risk of one session committing to another session's branch.
- OpenCode's own state (conversation history, tool results, session config) lives in each worktree's `.opencode/` directory, so sessions do not share context.

## Workflow for Creating a Session

Use `wt switch --create` with the `-x` flag to start an OpenCode session in a fresh worktree:

```bash
wt switch --create feature-auth -x opencode -- "Add authentication middleware"
```

This command:

1. Creates a new branch `feature-auth` from the current HEAD.
2. Creates a sibling worktree at `../repo.feature-auth/`.
3. Runs `opencode` in the new worktree with the task prompt.

The `-x` flag (short for `--execute`) runs a command in the worktree after creation. When that command is `opencode`, Worktrunk launches the agent in the isolated worktree, ready to work on the specified task.

### Alternative: Switch Then Launch

```bash
wt switch feature-auth   # switch to existing worktree / create if needed
opencode "Add authentication middleware"
```

Use this form when the worktree already exists or you want to control the agent CLI separately.

### Cleanup

After the session completes, remove the worktree:

```bash
wt remove feature-auth
```

This runs any configured hooks (e.g., merging changes back to the source branch) before deleting the worktree and branch reference.

## Recommended Project Configuration

For the knowledge-base repository, the following `.config/wt.toml` applies sensible defaults:

```toml
pre-start = """
  # Install dependencies when entering a worktree
  if [ -f justfile ]; then just setup; fi
"""
pre-merge = """
  # Validate YAML frontmatter in knowledge notes before merging
  failed=0
  for f in $(find knowledge/ -name '*.md'); do
    if grep -q '^---$' "$f" 2>/dev/null; then
      echo "OK: $f"
    else
      echo "FAIL: $f (missing or broken YAML frontmatter)"
      failed=1
    fi
  done
  if [ "$failed" -ne 0 ]; then exit 1; fi
"""

[commit.generation]
template-append = """
- Use conventional commits (feat:, fix:, docs:, chore:)
- Reference relevant issue numbers in the body
"""
```

### Hooks

The `pre-start` hook runs dependency setup automatically on `wt switch` and `wt start`. The `pre-merge` hook validates YAML frontmatter in knowledge notes deterministically — using shell tools instead of an LLM for speed and reliability.

### Commit Conventions

Project-specific commit guidelines are appended to the LLM prompt via `template-append`. The LLM `command` and prompt `template` are user-level settings that belong in `~/.config/worktrunk/config.toml` — only `template-append` is honored from the project file.

### Worktree Path Template

Worktrunk's default sibling-directory layout (`{{ repo }}.{{ branch | sanitize }}`) produces paths like `knowledge-base.feature-new-plugin/`. To customize, set `worktree-path` in user config (`~/.config/worktrunk/config.toml`).

## Session Isolation Best Practices

### One Branch Per Session

Each OpenCode session should target exactly one branch. Do not switch branches within a session; instead, end the session, switch worktrees, and start a new session.

### No Shared State

- Do not share `.opencode/` directories between worktrees.
- Do not share `node_modules/` or language-server caches — Worktrunk worktrees are independent clones.
- Use absolute or worktree-relative paths in OpenCode configuration rather than symlinks that cross worktree boundaries.

### Clean Up After Yourself

```
wt remove <branch>
```

after the session is complete and changes are merged. Orphaned worktrees accumulate disk usage and clutter `wt list` output.

### Stale Markers

If a session crashes, clear the stale marker:

```
wt config state marker clear
```

## Comparison with Other Agent Integrations

| Capability | Claude Code | OpenCode | Codex | Gemini CLI |
|---|---|---|---|---|
| Configuration skill | ✓ | ✓ | — | ✓ |
| Activity tracking (🤖/💬) | ✓ | ✓ | — | ✓ |
| Worktree isolation | ✓ | — | — | — |
| `/wt-switch-create` command | ✓ | — | — | — |

- **Claude Code** has the deepest integration. It loads the Worktrunk skill automatically, provides worktree isolation via `WorktreeCreate`/`WorktreeRemove` hooks, the `/wt-switch-create` slash command, and a dedicated statusline format. Activity tracking works fully.
- **OpenCode** offers a configuration skill and activity tracking. Its plugin API exposes `session.status`, `session.idle`, and `session.deleted` events, which are sufficient for the 🤖/💬 marker lifecycle. Worktree isolation is not available because OpenCode does not expose worktree lifecycle hooks. Users invoke `wt switch --create` and `wt remove` directly from the shell.
- **Codex** omits activity tracking because its hook system lacks a turn-end event — a 🤖 marker would never clear back to 💬. No runtime hooks are available.
- **Gemini CLI** provides a configuration skill and activity tracking via a native extension loaded from the Worktrunk GitHub repository. Like OpenCode, it lacks worktree isolation hooks. Installation does not use `wt config plugins`; instead it uses `gemini extensions install`.

## References

- [Worktrunk Agent Integration Docs](https://worktrunk.dev/claude-code/)
- [Worktrunk GitHub Repository](https://github.com/max-sixty/worktrunk)
- [OpenCode Plugin Source](https://raw.githubusercontent.com/max-sixty/worktrunk/main/dev/opencode-plugin.ts)

---

## See Also

- [Worktrunk Worktree Lifecycle](./lifecycle.md) — End-to-end workflow walkthrough including parallel agent workflows


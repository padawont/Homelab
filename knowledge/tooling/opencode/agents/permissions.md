---
title: "Agent Permissions"
status: draft
author: "Khalid"
date: 2026-05-31
tags:
  - opencode
  - agents
  - permissions
sources:
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
last_audit_date: 2026-05-31
---

## Permission Model

Three actions: `allow` (runs without approval), `ask` (prompts user — options: once/always/reject), `deny` (blocks the action).

## Permission Keys Reference

| Key | Gated Tools | Object Form |
|-----|-------------|-------------|
| `read` | `read` | Yes |
| `edit` | `write`, `edit`, `apply_patch` | Yes |
| `glob` | `glob` | Yes |
| `grep` | `grep` | Yes |
| `list` | `list` | Yes |
| `bash` | `bash` | Yes |
| `task` | `task` | Yes |
| `external_directory` | any tool touching paths outside project worktree | Yes |
| `lsp` | `lsp` | Yes |
| `skill` | `skill` | Yes |
| `todowrite` | `todowrite`, `todoread` | No (shorthand only) |
| `webfetch` | `webfetch` | No (shorthand only) |
| `websearch` | `websearch` | No (shorthand only) |
| `question` | `question` | No (shorthand only) |
| `doom_loop` | recovery prompts when agent repeats the same tool call 3x with identical input | No (shorthand only) |

## Shorthand vs Object Form

Keys that accept object form can use either:

```json
// Shorthand
"edit": "deny"

// Object — pattern → action, last-match-wins
"edit": {
  "*": "deny",
  "packages/web/src/content/docs/*.mdx": "allow"
}
```

Keys that accept only shorthand: `todowrite`, `webfetch`, `websearch`, `question`, `doom_loop`.

## Bash Command Granularity

The `bash` permission matches against the parsed command, not the raw string:

```json
"bash": {
  "*": "ask",
  "git *": "allow",
  "grep *": "allow",
  "rm *": "deny"
}
```

Last matching rule wins. Put `"*"` catch-all first, specific patterns after.

## Task Permissions

`permission.task` controls which subagents a primary agent can invoke via the `task` tool:

```json
"permission": {
  "task": {
    "*": "deny",
    "orchestrator-*": "allow",
    "code-reviewer": "ask"
  }
}
```

- `deny` removes the subagent from the Task tool description entirely — the model never sees it
- Users always bypass task permissions via `@mention`

## Skill Permissions

```json
"skill": {
  "*": "allow",
  "internal-*": "deny"
}
```

- `allow` — loads immediately
- `deny` — hidden from agent
- `ask` — prompts user

## Global vs Per-Agent

Root-level `permission` applies globally. Per-agent `permission` overrides for specific agents:

```json
{
  "permission": {
    "edit": "deny",
    "bash": { "*": "ask" }
  },
  "agent": {
    "build": {
      "permission": {
        "edit": "ask",
        "bash": "allow"
      }
    }
  }
}
```

Also settable in Markdown agent frontmatter:

```yaml
---
permission:
  edit: deny
  bash:
    "*": ask
    "git diff": allow
    "grep *": allow
  webfetch: deny
---
```

## Global Defaults

Most permissions default to `allow`. Exceptions:

- `doom_loop`: `ask`
- `external_directory`: `ask`
- `read`: `allow` (but `*.env`, `*.env.*` denied by default; `*.env.example` allowed)

## Wildcard Tool Name Matching

Permission keys match as wildcard patterns against the underlying tool name, so MCP and custom tools are covered:

```json
"mymcp_*": "deny"
"mymcp_search": "ask"
```

## See Also

- [configuration](configuration.md)
- [interactions](interactions.md)
- [concepts](concepts.md)

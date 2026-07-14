---
title: "Custom Tool Execution Context"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - tools
  - context
sources:
  - url: "https://opencode.ai/docs/custom-tools"
    title: "OpenCode Custom Tools Documentation"
  - url: "https://opencode.ai/docs/mcp-servers"
    title: "OpenCode MCP Servers Documentation"
last_audit_date: 2026-06-07
---

# Custom Tool Execution Context

The `execute` function receives a `context` object as its second argument:

```typescript
execute: async (args, context) => {
  // context.agent       - The agent name currently running
  // context.sessionID   - The current session identifier
  // context.messageID   - The current message identifier
  // context.directory   - The session working directory
  // context.worktree    - The git worktree root directory
}
```

| Property | Type | Description |
|---|---|---|
| `agent` | string | Name of the agent that invoked the tool |
| `sessionID` | string | Current session identifier |
| `messageID` | string | Current message identifier |
| `directory` | string | Session working directory — the directory the user's context is rooted in |
| `worktree` | string | Git worktree root directory — may differ from `directory` in monorepo or multi-root layouts |

## See Also

- [Custom Tool Definition](definition.md)

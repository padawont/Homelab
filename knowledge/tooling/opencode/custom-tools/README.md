# OpenCode Custom Tools

Reference documentation for creating, configuring, and managing custom tools in OpenCode: definition structure, argument schemas, execution context, multi-tool files, name collisions, cross-language invocation, and permissions.

## Files

- `overview.md` — Topic index with links to all atomic notes and related topics
- `definition.md` — What custom tools are, location, tool() helper structure, name derivation
- `arguments.md` — Zod argument schemas, types, modifiers (optional, default, describe)
- `execution-context.md` — Context object properties (agent, sessionID, messageID, directory, worktree)
- `advanced.md` — Multiple tools per file, name collisions, cross-language execution via Bun.$
- `permissions.md` — Glob-based permission rules, MCP vs custom comparison

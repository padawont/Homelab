---
title: "Custom Tool Definition"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - tools
  - definition
sources:
  - url: "https://opencode.ai/docs/custom-tools"
    title: "OpenCode Custom Tools Documentation"
  - url: "https://opencode.ai/docs/mcp-servers"
    title: "OpenCode MCP Servers Documentation"
last_audit_date: 2026-06-07
---

# Custom Tool Definition

## What Custom Tools Are

Custom tools are functions that the LLM can call during conversations. They work alongside built-in tools (read, write, bash, grep, glob, edit, webfetch) to extend the model's capabilities. Custom tools are defined as TypeScript or JavaScript files and can invoke scripts in any language available on the system.

Custom tools can be defined in two ways:

1. **Standalone** — As `.ts`/`.js` files in `.opencode/tools/` or `~/.config/opencode/tools/` (what this document covers primarily).
2. **Plugin-bundled** — Via the `tool()` helper inside a plugin's `tool` hook, as covered in the [Plugins note](../plugins/).

Both approaches use the same `tool()` helper from `@opencode-ai/plugin` and produce identical runtime behavior — the LLM sees them as the same kind of tool. The difference is organizational: standalone files for project-local ad-hoc tools; plugin-bundled for tools distributed as npm packages.

Custom tools are invoked by [agents](../agents/), and [skills](../skills/) can instruct agents to use custom tools, extending skill capabilities beyond built-in tooling. See the [Agents](../agents/) and [Skills](../skills/) notes for details.

## Location

Custom tools can be placed in two locations:

| Location | Path | Scope |
|---|---|---|
| Project | `.opencode/tools/` | Local to a single project |
| Global | `~/.config/opencode/tools/` | Available across all projects |

Tools are auto-discovered from both locations at startup. Project-local tools take precedence over global tools when a name collision occurs.

## Tool Definition Structure

Each custom tool file exports a tool definition using the `tool()` helper from `@opencode-ai/plugin`. The helper provides type-safety and argument validation via Zod:

```typescript
import { tool } from "@opencode-ai/plugin";

export default tool({
  description: "What this tool does",
  args: {
    param1: tool.schema.string().describe("Description of param1"),
    param2: tool.schema.number().describe("Description of param2"),
  },
  execute: async (args, context) => {
    // Tool logic here
    return `Result: ${args.param1}, ${args.param2}`;
  },
});
```

> **Naming convention**: Use `export default tool(...)` for a single tool per file — the tool name becomes the filename. Use named `export const name = tool(...)` only for multi-tool files — the tool name becomes `<filename>_<exportname>`.

### The `tool()` Helper Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `description` | string | yes | Human-readable description the LLM uses to decide when to call this tool |
| `args` | ZodObject | yes | Zod schema defining the tool's parameters and their types |
| `execute` | function | yes | Async function implementing the tool's behavior; receives parsed args and context |

The `tool()` helper provides `tool.schema` — a convenience alias for Zod — so you don't need to import `zod` separately. You can also import `zod` directly and use `z.string()` etc. if you prefer.

### Tool Name Derivation

The filename (without extension) becomes the tool name. A file named `math.ts` creates a tool the LLM can invoke as `math`.

## See Also

- [Custom Tool Arguments](arguments.md)
- [Custom Tool Execution Context](execution-context.md)
- [Custom Tool Permissions](permissions.md)

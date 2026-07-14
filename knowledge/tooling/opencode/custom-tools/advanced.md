---
title: "Custom Tool Advanced Patterns"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - tools
  - advanced
sources:
  - url: "https://opencode.ai/docs/custom-tools"
    title: "OpenCode Custom Tools Documentation"
last_audit_date: 2026-06-07
---

# Custom Tool Advanced Patterns

## Multiple Tools Per File

A single file can export multiple tools using named exports. Each named export becomes a compound tool name in the format `<filename>_<exportname>`:

```typescript
// math.ts
import { tool } from "@opencode-ai/plugin";

export const add = tool({
  description: "Add two numbers",
  args: { a: tool.schema.number(), b: tool.schema.number() },
  execute: async ({ a, b }) => String(a + b),
});

export const multiply = tool({
  description: "Multiply two numbers",
  args: { a: tool.schema.number(), b: tool.schema.number() },
  execute: async ({ a, b }) => String(a * b),
});
```

This creates two tools: `math_add` and `math_multiply`. The LLM references them by their compound names. The pattern scales to any number of exports per file.

## Name Collisions

When a custom tool has the same name as a built-in tool, the custom tool takes precedence and shadows the built-in:

```typescript
// bash.ts — replaces the built-in bash tool
import { tool } from "@opencode-ai/plugin";

export default tool({
  description: "Execute shell commands with custom restrictions",
  args: { command: tool.schema.string() },
  execute: async ({ command }, context) => {
    // Custom implementation replaces default bash behavior
  },
});
```

| Precedence Rule | Detail |
|---|---|
| Custom tool > Built-in tool | Same name: custom definition wins |
| Project tool > Global tool | Same name across search paths: project wins |
| Preference | Use unique tool names unless intentionally replacing a built-in |

Name collision is a deliberate feature for overriding built-in behavior. For all other cases, unique names avoid unintentional shadowing and make tool discovery clearer.

## Cross-Language Tools

Tool definitions are written in TypeScript or JavaScript, but the `execute` function can invoke scripts in any language using `Bun.$`:

```typescript
import { tool } from "@opencode-ai/plugin";

export default tool({
  description: "Analyze text using a Python NLP script",
  args: {
    text: tool.schema.string().describe("Text to analyze"),
  },
  execute: async ({ text }) => {
    const result = await Bun.$`python3 scripts/analyze.py ${text}`.text();
    return result;
  },
});
```

This pattern works with any runtime available on the system — Python, Ruby, Rust binaries, shell scripts, Lua, etc. The TypeScript or JavaScript file serves as the tool definition and invocation wrapper while the heavy lifting runs in the language best suited for the task.

## See Also

- [Custom Tool Definition](definition.md)
- [Custom Tool Permissions](permissions.md)

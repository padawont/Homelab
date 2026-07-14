---
title: "Custom Tool Arguments"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - tools
  - zod
  - arguments
sources:
  - url: "https://opencode.ai/docs/custom-tools"
    title: "OpenCode Custom Tools Documentation"
  - url: "https://zod.dev"
    title: "Zod Documentation"
last_audit_date: 2026-06-07
---

# Custom Tool Arguments

## Argument Schemas

The `args` field uses Zod for schema definition, validation, and LLM-facing descriptions:

```typescript
import { tool } from "@opencode-ai/plugin";

export default tool({
  description: "Greet someone by name",
  args: {
    name: tool.schema.string().describe("The person's name"),
    greeting: tool.schema.string().default("Hello").describe("The greeting to use"),
    count: tool.schema.number().optional().describe("Number of times to repeat"),
  },
  execute: async (args) => {
    const msg = `${args.greeting}, ${args.name}!`;
    return args.count ? Array(args.count).fill(msg).join("\n") : msg;
  },
});
```

Zod types commonly used in tool arguments:

| Schema Type | Description |
|---|---|
| `tool.schema.string()` | String parameter |
| `tool.schema.number()` | Numeric parameter |
| `tool.schema.boolean()` | Boolean flag |
| `tool.schema.enum(["a", "b"])` | Fixed set of allowed values |
| `tool.schema.array(tool.schema.string())` | Array of strings |
| `tool.schema.object({...})` | Nested object |
| `.optional()` | Marks a field as not required |
| `.default(val)` | Sets a default value when the argument is omitted |
| `.describe(str)` | Description sent to the LLM to explain the parameter's purpose |

For advanced use cases, Zod can be imported directly as `z` and the schema can return a plain object.

## See Also

- [Custom Tool Definition](definition.md)

---
title: "Custom Tool Permissions"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - tools
  - permissions
sources:
  - url: "https://opencode.ai/docs/custom-tools"
    title: "OpenCode Custom Tools Documentation"
  - url: "https://opencode.ai/docs/mcp-servers"
    title: "OpenCode MCP Servers Documentation"
last_audit_date: 2026-06-07
---

# Custom Tool Permissions

Custom tools are subject to the same permission system as built-in tools. Permission keys match as glob-style wildcard patterns against tool names:

```json
{
  "permission": {
    "math_*": "allow",
    "bash": "deny",
    "analyze": "allow"
  }
}
```

| Pattern | Effect |
|---|---|
| `"toolname"` | Matches the exact tool name |
| `"prefix_*"` | Matches all tools starting with `prefix_` (e.g., `math_add`, `math_multiply`) |
| `"*"` | Matches all tools (catch-all rule) |
| `"*_suffix"` | Matches all tools ending with `_suffix` |

The last matching rule wins when multiple patterns apply. A `deny` rule removes the tool from the LLM's available tool list entirely — the model cannot see or attempt to call it.

Both MCP tools and custom tools are covered by this permission system, but they differ in how they originate and are named:

- **MCP tools** come from external servers (subprocess or HTTP) and are named by the MCP server with a prefix, e.g., `servername_toolname`.
- **Custom tools** come from local `.ts`/`.js` files and are named by filename, e.g., `mytool` or `math_add`.

The permission system treats both types uniformly — glob patterns match against the full tool name regardless of whether the tool comes from an MCP server or a local file. One notable difference: custom tools can shadow built-in tools (when a custom tool shares a name with a built-in, the custom definition wins). See the [MCP Servers note](../mcp/) for more on MCP tool naming and configuration.

## See Also

- [Custom Tool Definition](definition.md)
- [Plugin Bundling Components](../plugins/bundling-components.md)
- [MCP Tool Management](../mcp/overview.md)

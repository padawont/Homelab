---
title: "Plugin Event Handler Patterns"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - events
  - patterns
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin Event Handler Patterns

> **Source note:** This reference is written against the `@opencode-ai/plugin` `Hooks` interface in the plugin source code (`packages/plugin/src/index.ts`). The official docs page at `opencode.ai/docs/plugins` may lag behind the source — if you spot a discrepancy between this reference and the docs, trust the source code.

## Named Handlers

Most events use the event name as the handler key in the returned hooks object:

```javascript
export const MyPlugin = async () => {
  return {
    "session.created": async (input, output) => {
      // Handle session creation
    },
    "tool.execute.before": async (input, output) => {
      // Handle tool execution
    },
  };
};
```

## Wildcard Handler

A plugin can catch all events using the generic `event` handler:

```javascript
export const MyPlugin = async () => {
  return {
    event: async ({ event }) => {
      // event.type contains the event name
      if (event.type === "session.idle") {
        // React to idle events
      }
    },
  };
};
```

The wildcard handler receives a single object with an `event` property containing the full event payload, including a `type` field that identifies the event name. This is useful for logging, analytics, or when a plugin needs to react to many events without registering individual handlers.

## See Also

- All event reference files in this directory (event-*.md) for per-event details
- [Plugin Examples](examples.md) — Complete code examples using both handler patterns

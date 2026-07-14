---
title: "Plugin Examples"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - examples
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Plugin Examples

## Send Notifications (Event-Driven)

Subscribe to session lifecycle events to send desktop or webhook notifications:

```javascript
export const NotificationPlugin = async ({ project, client, $, directory, worktree }) => {
  return {
    event: async ({ event }) => {
      // Send notification on session completion
      if (event.type === "session.idle") {
        await $`osascript -e 'display notification "Session completed!" with title "opencode"'`;
      }
    },
  };
};
```

This example uses `osascript` to run AppleScript on macOS for desktop notifications. The `event` wildcard handler catches all events, and the `event.type` check filters for the specific session idle event.

## .env Protection (Tool Execute Before)

Prevent OpenCode from reading `.env` files:

```javascript
export const EnvProtection = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "read" && output.args.filePath.includes(".env")) {
        throw new Error("Do not read .env files");
      }
    },
  };
};
```

The `input` parameter contains the tool being invoked, while `output.args` provides access to the tool arguments before execution. Throwing an error blocks the tool from running.

## Inject Environment Variables (Shell Env)

Inject environment variables into all shell execution (AI tools and user terminals):

```javascript
export const InjectEnvPlugin = async () => {
  return {
    "shell.env": async (input, output) => {
      output.env.MY_API_KEY = "secret";
      output.env.PROJECT_ROOT = input.cwd;
    },
  };
};
```

The `input` parameter provides information about the shell context (including `input.cwd`), and the `output.env` object allows setting environment variables that will be available in the shell session.

## Custom Tools (Tool Helper)

Plugins can add custom tools using the `tool()` helper from `@opencode-ai/plugin`:

```typescript
import { type Plugin, tool } from "@opencode-ai/plugin";

export const CustomToolsPlugin: Plugin = async (ctx) => {
  return {
    tool: {
      mytool: tool({
        description: "This is a custom tool",
        args: {
          foo: tool.schema.string(),
        },
        async execute(args, context) {
          const { directory, worktree } = context;
          return `Hello ${args.foo} from ${directory} (worktree: ${worktree})`;
        },
      }),
    },
  };
};
```

The `tool()` helper creates a custom tool with:
- `description`: What the tool does
- `args`: Zod schema for the tool's arguments (via `tool.schema`)
- `execute`: Function that runs when the tool is called, receiving the parsed arguments and tool context

Custom tools are available to OpenCode alongside built-in tools. If a plugin tool uses the same name as a built-in tool, the plugin tool takes precedence.

## Logging (Client App Log)

Use `client.app.log()` instead of `console.log` for structured logging:

```typescript
export const MyPlugin = async ({ client }) => {
  await client.app.log({
    body: {
      service: "my-plugin",
      level: "info",
      message: "Plugin initialized",
      extra: { foo: "bar" },
    },
  });
};
```

The `log()` method accepts a structured object and must be `await`ed. Valid log levels: `debug`, `info`, `warn`, `error`. See the OpenCode SDK documentation for additional logging options.

## Compaction Hooks

Customize the context included when a session is compacted:

```typescript
import type { Plugin } from "@opencode-ai/plugin";

export const CompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      // Inject additional context into the compaction prompt
      output.context.push(`## Custom Context

Include any state that should persist across compaction:
- Current task status
- Important decisions made
- Files being actively worked on`);
    },
  };
};
```

The `experimental.session.compacting` hook fires before the LLM generates a continuation summary. Use it to inject domain-specific context that the default compaction prompt would miss.

You can also replace the compaction prompt entirely by setting `output.prompt`:

```typescript
import type { Plugin } from "@opencode-ai/plugin";

export const CustomCompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      // Replace the entire compaction prompt
      output.prompt = `You are generating a continuation prompt for a multi-agent swarm session.

Summarize:
1. The current task and its status
2. Which files are being modified and by whom
3. Any blockers or dependencies between agents
4. The next steps to complete the work

Format as a structured prompt that a new agent can use to resume work.`;
    },
  };
};
```

When `output.prompt` is set, it completely replaces the default compaction prompt. The `output.context` array is ignored in this case.

## See Also

- [Plugin Architecture](architecture.md) — Plugin architecture overview
- [Plugin Creation](creation.md) — Basic structure, TypeScript, dependencies, and configuration
- [Event Command](event-command.md) — Command event hook reference
- [Event Tool](event-tool.md) — Tool event hook reference
- [Event Shell](event-shell.md) — Shell event hook reference
- [Event Compaction](event-compaction.md) — Compaction hook reference
- [Bundling Components](bundling-components.md) — Bundling agents, skills, and tools in a plugin

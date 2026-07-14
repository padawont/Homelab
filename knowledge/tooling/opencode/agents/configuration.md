---
title: "Agent Configuration"
status: draft
author: "Khalid"
date: 2026-05-31
tags:
  - opencode
  - agents
  - configuration
sources:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/config"
    title: "OpenCode Config Documentation"
last_audit_date: 2026-05-31
---

# Agent Configuration

How OpenCode agents are defined and configured.

## Definition Formats

### JSON Format

Defined in `opencode.json` under the `"agent"` key:

```json
{
  "agent": {
    "agent-name": {
      "description": "What this agent does",
      "mode": "subagent",
      "model": "provider/model-id",
      "temperature": 0.1,
      "steps": 10,
      "prompt": "{file:./prompts/agent-prompt.txt}",
      "permission": { "edit": "deny" }
    }
  }
}
```

### Markdown Format

Defined in `.opencode/agents/<name>.md` or `~/.config/opencode/agents/<name>.md`:

```yaml
---
description: What this agent does
mode: subagent
model: provider/model-id
temperature: 0.1
permission:
  edit: deny
---
You are in code review mode...
```

The file name becomes the agent name. Markdown is recommended for complex agents. Both formats can coexist for different agents.

## Configuration Options

| Option | Type | Default | Description |
|---|---|---|---|
| `description` | string | — | Required. Brief description of what the agent does |
| `mode` | `"primary"`, `"subagent"`, or `"all"` | `"all"` | How the agent can be used |
| `model` | string (`provider/model-id`) | Primary: global model; Subagent: invoker's model | Override model for this agent |
| `temperature` | number (0.0–1.0) | Model-specific | Response randomness (0 = focused, 1 = creative) |
| `steps` | integer | Unlimited | Max agentic iterations before forced text response. Legacy `maxSteps` is deprecated — use `steps` |
| `disable` | boolean | `false` | Set `true` to prevent agent from loading |
| `prompt` | string | — | Custom system prompt. Inline text or `{file:./path/to/prompt.txt}` reference |
| `permission` | object | — | Maps tool keys to `"allow"`, `"ask"`, or `"deny"` |
| `tools` | object | — | Deprecated. Use `permission` instead |
| `hidden` | boolean | `false` | Subagents only. Hides from `@` autocomplete, still invocable via Task |
| `color` | string | — | UI color: hex (`#FF5733`) or theme name (`primary`, `secondary`, `accent`, `success`, `warning`, `error`, `info`) |
| `top_p` | number (0.0–1.0) | Model-specific | Alternative to temperature for diversity control |

Any additional options are passed through directly to the provider as model parameters (e.g. `reasoningEffort`, `textVerbosity`, `max_thinking_tokens`).

## Model Inheritance

- **Subagents** without an explicit `model` field inherit the model from the primary agent that invoked them
- **Primary agents** without an explicit `model` field use the globally configured model
- Model ID format: `provider/model-id` (e.g. `anthropic/claude-sonnet-4-20250514`, `opencode/gpt-5.1-codex`)

## Prompt File References

- Syntax: `{file:./prompts/build.txt}`
- Path is relative to the config file location (works for global `~/.config/opencode/` and project `opencode.json`)
- Supports `{env:VARIABLE_NAME}` for environment variable substitution

## Repo Example

The repo's `opencode.json` at the root uses the JSON format with `instructions` pointing at `AGENTS.md` and no custom agents currently defined:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["AGENTS.md"]
}
```

## Creating Agents

`opencode agent create` is an interactive CLI command that:

1. Asks where to save (global or project)
2. Prompts for a description
3. Generates a system prompt and identifier
4. Asks which permissions to allow (everything else is denied)
5. Creates a Markdown agent file

## See Also

- [permissions](permissions.md)
- [discovery](discovery.md)
- [context-loading](context-loading.md)

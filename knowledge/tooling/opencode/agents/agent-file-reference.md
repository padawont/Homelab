---
title: "Agent File Reference"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - agents
  - reference
  - frontmatter
sources:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
  - url: "https://opencode.ai/docs/config"
    title: "OpenCode Config Documentation"
last_audit_date: 2026-06-07
---

# Agent File Reference

> **For Python developers new to OpenCode's agent system.** This is the canonical reference for writing agent `.md` files — every frontmatter field, its type, default, valid values, and usage examples.

---

## Overview

OpenCode agents are defined in Markdown files: `.opencode/agents/<name>.md` (project-level) or `~/.config/opencode/agents/<name>.md` (global). The file name becomes the agent name. Frontmatter YAML between `---` delimiters configures the agent; the body after the frontmatter is the system prompt.

```yaml
---
description: Does something useful
mode: subagent
---
You are an agent that does something useful...
```

Think of it like a Python dataclass definition where fields go in the class body — except here the fields go in YAML frontmatter and the class docstring (system prompt) goes after.

---

## Fields Reference

### `description`

| Item | Value |
|---|---|
| **Type** | `string` |
| **Required** | Yes |
| **Default** | — (no default) |

What the agent does. Shown in `@mention` autocomplete and `opencode agent list`. Like Python's `__doc__` — it is the first thing a user sees.

```yaml
description: Reviews pull requests for correctness and security
```

```yaml
description: Orchestrates multi-agent refactoring workflows
```

---

### `mode`

| Item | Value |
|---|---|
| **Type** | `string` |
| **Required** | Yes |
| **Valid values** | `primary`, `subagent`, `all` |
| **Default** | `all` |

Controls how the agent can be invoked.

| Value | Meaning |
|---|---|
| `primary` | Accessible via `@mention`. Can invoke subagents via the `task` tool. |
| `subagent` | Accessible only via the `task` tool from a primary agent. Hidden from `@mention` unless also tagged `.hidden: false`. |
| `all` | Both — can be `@mention`-ed and invoked via `task`. |

Think of `primary` as a Python `__main__` entry point, `subagent` as an importable helper module, and `all` as a module with `if __name__ == "__main__"` logic.

```yaml
mode: subagent
```

```yaml
mode: primary
```

---

### `model`

| Item | Value |
|---|---|
| **Type** | `string` |
| **Required** | No |
| **Format** | `provider/model-id` |
| **Default** | Primary: global model; subagent: inherits invoker's model |

Override the model for this agent. Subagents without an explicit `model` inherit from their invoking primary agent.

```yaml
model: opencode-go/deepseek-v4-flash
```

```yaml
model: anthropic/claude-sonnet-4-20250514
```

```yaml
model: opencode/gpt-5.1-codex
```

---

### `temperature`

| Item | Value |
|---|---|
| **Type** | `float` |
| **Required** | No |
| **Range** | `0.0` to `1.0` |
| **Default** | Provider-specific (usually ~0.7) |

Controls randomness in responses. `0.0` = deterministic, focused; `1.0` = creative, divergent. Like Python's `random.seed(0)` — lower values produce more reproducible output.

```yaml
temperature: 0.0    # Code review, linting, fact-checking
```

```yaml
temperature: 0.7    # Brainstorming, creative writing, exploration
```

```yaml
temperature: 0.2    # Refactoring, test generation, documentation
```

---

### `top_p`

| Item | Value |
|---|---|
| **Type** | `float` |
| **Required** | No |
| **Range** | `0.0` to `1.0` |
| **Default** | Provider-specific |

Nucleus sampling — an alternative to `temperature`. Controls cumulative probability threshold for token selection. `0.1` = narrow, focused; `0.9` = broad, diverse. Typically you tune one or the other, not both.

```yaml
top_p: 0.9
```

---

### `max_steps`

| Item | Value |
|---|---|
| **Type** | `int` |
| **Required** | No |
| **Default** | Unlimited (provider cap applies) |

Maximum number of tool-calling iterations the agent can make before it must produce a text response. The legacy field name `maxSteps` (camelCase) is deprecated.

**Note on JSON vs Markdown naming:** In OpenCode's JSON config (`opencode.json`), this field is named `steps` (without the `max_` prefix). The markdown frontmatter uses `max_steps`. Both control the same setting — JSON's `steps` and Markdown's `max_steps` are equivalent. If you switch between formats, remember to adjust the field name accordingly.

```yaml
max_steps: 10
```

```yaml
max_steps: 25    # Complex multi-tool workflows
```

---

### `disable`

| Item | Value |
|---|---|
| **Type** | `bool` |
| **Required** | No |
| **Default** | `false` |

Set to `true` to prevent the agent from loading at all. Useful for temporarily taking an agent offline without deleting its file.

```yaml
disable: true
```

---

### `hidden`

| Item | Value |
|---|---|
| **Type** | `bool` |
| **Required** | No |
| **Default** | `false` |
| **Scope** | Subagents only |

Subagents only. When `true`, the agent is hidden from `@mention` autocomplete but can still be invoked via the `task` tool programmatically. Like a Python `_private_function` convention — visible if you know the name, hidden from autocomplete.

```yaml
hidden: true
```

---

### `color`

| Item | Value |
|---|---|
| **Type** | `string` |
| **Required** | No |
| **Valid values** | Hex color (`#RRGGBB`) or theme color name |
| **Default** | Provider-dependent |

UI accent color shown in the agent's chat interface. Theme color names:

| Name | Typical use |
|---|---|
| `primary` | Default brand color |
| `secondary` | Supporting accent |
| `accent` | Highlight |
| `success` | Green tones |
| `warning` | Yellow/orange tones |
| `error` | Red tones |
| `info` | Blue tones |

```yaml
color: "#FF5733"
```

```yaml
color: success
```

```yaml
color: info
```

---

### `reasoningEffort`

| Item | Value |
|---|---|
| **Type** | `string` |
| **Required** | No |
| **Valid values** | `low`, `medium`, `high` |
| **Default** | Provider-specific |

Controls how much reasoning/chain-of-thought the model performs before answering. Provider-dependent — not all models support this. High effort = better reasoning, slower responses, higher cost.

**This is a pass-through field:** OpenCode does not interpret `reasoningEffort` itself. It forwards the value directly to the provider as a model parameter. Check your provider's documentation for supported values and behavior.

```yaml
reasoningEffort: high    # Complex architectural analysis
```

```yaml
reasoningEffort: low     # Simple formatting or linting tasks
```

---

### `max_thinking_tokens`

| Item | Value |
|---|---|
| **Type** | `int` |
| **Required** | No |
| **Default** | Provider-specific |

Token budget for the model's internal reasoning process. Only applies to models that support explicit thinking/reasoning budgets (e.g., OpenAI o-series, Claude 3.7 Sonnet+).

**This is a pass-through field:** OpenCode forwards `max_thinking_tokens` to the provider without interpretation. It is not a first-class OpenCode config field — it is passed through as a model parameter. Check your provider's documentation for exact field names and support.

```yaml
max_thinking_tokens: 8192
```

```yaml
max_thinking_tokens: 2048    # Quick decisions
```

---

### `permission`

| Item | Value |
|---|---|
| **Type** | `object` |
| **Required** | No |
| **Default** | Inherits global defaults |

Maps tool permission keys to `allow`, `ask`, or `deny`. Supports both shorthand (string value) and object form (map of glob patterns to actions).

#### Permission keys reference

| Key | Tools gated | Object form? |
|---|---|---|
| `read` | `read` | Yes |
| `edit` | `write`, `edit`, `apply_patch` | Yes |
| `bash` | `bash` | Yes (supports per-command patterns) |
| `glob` | `glob` | Yes |
| `grep` | `grep` | Yes |
| `list` | `list`\* | Yes |
| `task` | `task` | Yes (supports per-agent patterns) |
| `skill` | `skill` | Yes (supports per-skill patterns) |
| `webfetch` | `webfetch` | No (shorthand only) |
| `websearch` | `websearch` | No (shorthand only) |
| `todowrite` | `todowrite`, `todoread` | No (shorthand only) |
| `question` | `question` | No (shorthand only) |
| `doom_loop` | Recovery prompts on repeated tool calls | No (shorthand only) |

\* The canonical permissions documentation does not list `list` as a standalone key. It is gated by the `read` permission — listing directory contents is considered a read operation.

#### Shorthand form

```yaml
permission:
  edit: deny
  webfetch: deny
  glob: allow
  grep: allow
```

#### Object form (bash — per-command globs)

```yaml
permission:
  bash:
    "*": ask              # Catch-all: ask for everything
    "git *": allow        # Git commands: allow
    "grep *": allow       # Grep commands: allow
    "npm *": deny         # Npm commands: deny
    "rm *": deny          # Rm commands: deny
```

Rules are evaluated last-match-wins — like Python's `except` blocks, the most specific handler should come last.

#### Object form (task — per-subagent globs)

```yaml
permission:
  task:
    "*": deny
    "code-reviewer": allow
    "orchestrator-*": ask
```

Denied subagents are removed from the task tool's description entirely — the model never sees them as invocable.

#### Object form (skill — per-skill globs)

```yaml
permission:
  skill:
    "*": allow
    "internal-*": deny
    "rs-*": ask
```

---

### Custom fields

Any field not listed above is passed through to the provider as a model parameter. This allows provider-specific options without OpenCode needing to know about every model's bespoke features.

```yaml
textVerbosity: low              # Provider-specific verbosity control
responseLength: medium          # Another provider-specific option
```

---

## Complete Agent File Examples

### Example 1: Code Reviewer (subagent)

```yaml
---
description: Reviews code for correctness, security, and style
mode: subagent
model: opencode-go/deepseek-v4-flash
temperature: 0.0
max_steps: 15
permission:
  read: allow
  edit: deny
  glob: allow
  grep: allow
  bash:
    "*": deny
    "git diff": allow
    "git log": allow
    "grep *": allow
  webfetch: deny
  skill:
    "*": allow
---
You are a code review specialist. Analyze code changes for:
1. Correctness — logic errors, edge cases, race conditions
2. Security — injection vulnerabilities, secret exposure, auth flaws
3. Style — consistency with project conventions, readability

Provide specific line-level feedback with code snippets.
Always explain the *why* behind each finding.
```

### Example 2: Developer Agent (primary)

```yaml
---
description: General-purpose development agent with full tool access
mode: primary
model: anthropic/claude-sonnet-4-20250514
temperature: 0.2
max_steps: 40
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  bash:
    "*": ask
    "git *": allow
    "npm *": allow
    "cargo *": allow
    "python *": allow
  webfetch: allow
  task:
    "*": allow
  skill:
    "*": allow
---
You are a senior full-stack developer. You have full edit access and can run build commands freely.
Always verify your changes compile/pass tests before declaring a task complete.
```

### Example 3: Architect Agent (primary with restricted subagent orchestration)

```yaml
---
description: System architecture reviewer and multi-agent orchestrator
mode: primary
model: opencode/gpt-5.1-codex
temperature: 0.1
reasoningEffort: high
max_thinking_tokens: 8192
permission:
  read: allow
  edit: deny
  glob: allow
  grep: allow
  bash:
    "*": deny
    "tree *": allow
    "git log": allow
  webfetch: allow
  task:
    "*": deny
    "code-reviewer": allow
    "security-reviewer": allow
    "knowledge-agent": ask
  skill:
    "*": allow
    "internal-*": deny
---
You are a system architect. Your role:
1. Review proposed changes for architectural soundness
2. Identify technical debt and migration opportunities
3. Delegate specialized reviews to subagents (code-reviewer, security-reviewer)
4. Synthesize subagent findings into a coherent architecture report

You cannot edit files — you recommend. You cannot run arbitrary commands — only inspect the tree and git log.
```

---

## Common Mistakes

### 1. Missing `description`

Without a `description`, the agent will not show up in `@mention` autocomplete. OpenCode may reject the agent entirely on stricter validation settings.

```yaml
# ❌ Wrong
mode: subagent

# ✅ Correct
description: Validates YAML configuration files
mode: subagent
```

### 2. Using `maxSteps` instead of `max_steps`

The camelCase `maxSteps` (JSON config) is deprecated. In JSON config, use `steps` (without the `max_` prefix). In markdown agent frontmatter, use `max_steps`.

```yaml
# ❌ Wrong (either format)
maxSteps: 10

# ✅ Correct (markdown agent)
max_steps: 10

# ✅ Correct (JSON config)
steps: 10
```

### 3. Forgetting the body after frontmatter

An agent `.md` file with frontmatter but no body has no system prompt — the agent will have no instructions about what to do.

```yaml
---
description: Something important
mode: subagent
---
# ❌ Missing: the system prompt!
```

```yaml
---
description: Something important
mode: subagent
---
You are an agent that does something important. Here is what you need to know...
```

### 4. Bash permission ordering

Last-match-wins means a broad deny after a specific allow will override the allow. Put `"*"` catch-all *first*, specific patterns *after*.

```yaml
# ❌ Wrong — "git *" never matches because "*": deny is last
permission:
  bash:
    "git *": allow
    "*": deny

# ✅ Correct — catch-all first, specifics last
permission:
  bash:
    "*": deny
    "git *": allow
    "grep *": allow
```

### 5. Using `tools` instead of `permission`

The `tools` field is deprecated. Use `permission` for all tool access control.

```yaml
# ❌ Wrong
tools:
  edit: deny

# ✅ Correct
permission:
  edit: deny
```

### 6. Nesting topics inside the agents folder

All files live flat in the `agents/` topic directory. Do not create `agents/reviewer/` subdirectories — note files sit alongside each other.

```yaml
# ❌ Wrong
knowledge/tooling/opencode/agents/reviewer/overview.md

# ✅ Correct
knowledge/tooling/opencode/agents/agent-file-reference.md
```

### 7. Setting `hidden: true` on a primary agent

The `hidden` field only applies to subagents. Setting it on a `mode: primary` agent has no effect.

---

## See Also

- [Configuration](configuration.md) — JSON and Markdown agent formats, model inheritance, prompt file references
- [Permissions](permissions.md) — Full permission model reference, global vs per-agent defaults, wildcard tool matching
- [Concepts](concepts.md) — What agents are, primary vs subagent, built-in agents table
- [Discovery](discovery.md) — Where agent files live, auto-discovery, naming conventions, precedence
- [Interactions](interactions.md) — How agents use the `skill` and `task` tools
- [Roles](roles.md) — Pre-assembled subagent role profiles for domain-specific tasks

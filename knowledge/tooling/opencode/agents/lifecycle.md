---
title: "Agent Lifecycle"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - agents
  - lifecycle
sources:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
last_audit_date: 2026-06-07
---

## Agent Lifecycle

The bullet points below provide a quick reference. Detailed sections follow.

- **Primary agents**: accessed via the Tab key or `switch_agent` keybind to cycle through tabs in the session bar.
- **Subagents**: invoked via `@mention` in the prompt, or programmatically via the `task` tool by a primary.
- **Custom agents**: created via `opencode agent create` interactive CLI, defined in `opencode.json`.
- **Hidden system agents** (Compaction, Title, Summary): run automatically without user interaction.
- **Session navigation shortcuts**:
  - `session_child_first` (<Leader>+Down) — navigate to the first child session.
  - `session_child_cycle` (Right arrow) — cycle through sibling sessions.
  - `session_child_cycle_reverse` (Left arrow) — cycle to the previous child session.
  - `session_parent` (Up arrow) — return to the parent session.

## Primary Agent Lifecycle

A session begins when the user opens OpenCode and starts a conversation with a primary agent. The default primary is **Build**, which has all tools enabled. Users can cycle through available primary agents using the **Tab** key or the configured `switch_agent` keybind. OpenCode ships with two built-in primary agents: **Build** (full tool access) and **Plan** (restricted, read-only by default).

When the user switches primaries mid-session, the new primary agent inherits the session's conversation history but applies its own permission set and system prompt. The session bar displays all active primary tabs, and the active one is visually highlighted.

## Subagent Lifecycle

Subagents are specialized assistants that primary agents can invoke. There are two invocation methods:

- **Manual @mention**: Users can type `@<agent-name>` in a message to invoke a subagent directly (e.g., `@general help me search for this function`).
- **Programmatic via the `task` tool**: Primary agents can spawn subagents using the `task` tool, which creates a child session. The `task` tool is the primary mechanism for parallel or delegated work.

When a subagent is invoked, OpenCode creates a child session. The subagent inherits context from the parent session — including conversation history, project files, and instructions. Tool access is governed by the subagent's own `permission` configuration.

When a subagent session completes, the user can navigate back to the parent using the `session_parent` keybind (Up arrow). Child sessions remain accessible for review; they are not automatically destroyed. This enables a tree-like session structure where a primary agent can delegate to multiple subagents and revisit their results.

## Agent Creation

New agents are created via the `opencode agent create` CLI command. This interactive workflow:

1. **Prompts for save location** — choose between global (`~/.config/opencode/agents/`) or project-specific (`.opencode/agents/`) storage.
2. **Asks for a description** — a brief statement of what the agent does.
3. **Generates a system prompt and identifier** — automatically creates an appropriate prompt based on the description.
4. **Configures permissions** — the user selects which permissions to allow; everything not selected defaults to `deny`.
5. **Creates the agent file** — writes a Markdown file (e.g., `review.md`) with frontmatter and system prompt at the chosen location.

After creation, the agent is auto-discovered on the next OpenCode startup. No manual registration is needed — the file scan picks it up from `.opencode/agents/` or `~/.config/opencode/agents/` automatically.

## Hidden Agents

OpenCode includes three hidden system agents that run automatically without user interaction. They are invisible in the UI (not selectable via Tab or @mention) but are listed in the built-in agents table in [concepts](concepts.md):

- **Compaction** (mode: primary) — activates when the session context window is nearly full. It compacts the conversation into a shorter summary to free up space while preserving essential information.
- **Title** (mode: primary) — generates a short, descriptive title for each session based on the conversation content.
- **Summary** (mode: primary) — creates a concise session summary, used for session recall and context management.

These agents are always present and fire automatically based on system events — users never invoke them directly.

## Session Context

Session context accumulates incrementally with each tool call the agent makes — file reads, bash commands, webfetches, and model responses all add to the token count. When the context window approaches capacity, the **Compaction** hidden agent fires automatically to summarize and compress the conversation, preserving critical information while reducing token usage.

## See Also

- [concepts](concepts.md)
- [configuration](configuration.md)
- [interactions](interactions.md)

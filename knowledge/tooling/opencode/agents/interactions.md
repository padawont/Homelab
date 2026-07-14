---
title: "Agent Interactions"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - agents
  - skills
  - tasks
sources:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
  - url: "https://opencode.ai/docs/tools"
    title: "OpenCode Tools Documentation"
last_audit_date: 2026-06-07
---

## Agent ↔ Skill Relationship

- Agents discover skills via the `skill` tool, which lists available skills in XML `<available_skills>` blocks within the system prompt.
- An agent loads a skill by calling `skill({ name: "..." })` — this injects the skill's instructions into the agent's context.
- Skills provide **instructions only** — they do NOT grant permissions. Permissions are managed separately in `opencode.json`.
- Skill file paths: `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` (project-local); `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/` (global).
- Skill permissions can be controlled via glob patterns in `opencode.json`:
  ```json
  "skill": { "*": "allow", "internal-*": "deny" }
  ```
- The `skill` tool can be disabled entirely per agent:
  ```json
  "tools": { "skill": false }
  ```

## Agent ↔ Task Tool

- Primary agents invoke subagents programmatically via the `task` tool, passing a `subagent` name and a prompt.
- `permission.task` uses glob patterns to match subagent names — the last matching rule wins.
- A `deny` rule removes the subagent from the Task tool's description entirely, so the model cannot attempt to invoke it.
- Users can bypass task permission restrictions by @mention-ing any subagent directly in the prompt.

## See Also

- [concepts](concepts.md)
- [permissions](permissions.md)

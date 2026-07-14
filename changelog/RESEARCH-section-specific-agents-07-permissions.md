---
title: "Permissions: Full-Access Defaults and Configuration Strategy"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - agents
  - permissions
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-permissions"
  - knowledge: "knowledge/tooling/opencode/skills/skill-configuration"
references:
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-05-31
---

# Permissions: Full-Access Defaults and Configuration Strategy

## 1. Current State
- `opencode.json` has no `permission` block — all defaults apply
- Defaults: most keys `allow` (read, edit, glob, grep, bash, task, skill, etc.)
- Exceptions: `doom_loop` and `external_directory` default to `ask`
- This means section agents work without any permission config

## 2. Recommended Agent Permissions
Each section agent gets full-access permissions in its frontmatter. The exact block (matching what's in 02-directory-layout.md):

```yaml
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  bash: allow
  list: allow
  task: allow
  skill: allow
```

Note: no `write: allow` — `edit` covers file writes. All match the defaults, so this is explicit documentation of intent, not a functional requirement.

## 3. Why Full-Access for All Agents
- Simplicity — no per-agent fine-tuning needed initially
- Agents are already scoped by their prompt — ideas-agent won't touch ADRs because its prompt doesn't tell it to
- If specific concerns arise later (e.g., bash access for ideas-agent), restriction is a one-line addition
- This decision follows from the plan's recommendation

## 4. Skill Permissions
- `permission.skill` defaults to `allow` — all skills are loadable by all agents without config
- Agents can further restrict via per-agent `permission.skill` patterns if needed (e.g., only allow `kb-*` skills)
- No `opencode.json` changes needed

## 5. Task Permissions
- `permission.task` defaults to `allow` — primary agents can invoke any subagent via the `task` tool
- Users always bypass task permissions via `@mention` — so section agents are always invocable by name
- No `opencode.json` changes needed

## 6. Future Considerations
- If agent behavior needs tightening, bash command patterns can be added
- If skill access needs scoping, `permission.skill` patterns in agent frontmatter restrict per-agent
- The current opencode.json stays untouched — all control is in the agent `.md` files

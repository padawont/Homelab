---
title: "Registration and Discovery: Zero-Config Auto-Discovery"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - agents
  - skills
  - discovery
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-discovery"
  - knowledge: "knowledge/tooling/opencode/agents/agent-configuration"
  - knowledge: "knowledge/tooling/opencode/agents/agent-permissions"
  - knowledge: "knowledge/tooling/opencode/skills/skill-configuration"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
last_audit_date: 2026-05-31
---

# Registration and Discovery: Zero-Config Auto-Discovery

## Context

Section-specific agents must be discoverable by OpenCode at runtime without manual registration. If each new agent required edits to `opencode.json` or a separate registration step, the friction would discourage adoption and violate the zero-configuration principle. This research examines how agents and skills auto-discover, which mechanisms require configuration and which do not, and what implications this has for the Knowledge Base.

## Findings

### 1. Auto-Discovery Overview

Both agents and skills are auto-discovered by OpenCode. No explicit registration in `opencode.json` is required. Placing a properly formatted file in the correct directory is sufficient — the agent or skill becomes available immediately with zero configuration changes.

### 2. Agent Discovery

Agent files are discovered from these paths:

| Path | Scope |
|---|---|
| `.opencode/agents/*.md` | Per-project (git worktree root) |
| `~/.config/opencode/agents/*.md` | Global (user-wide) |

**Key rules:**

- The file name (without `.md` extension) becomes the agent name used for `@mention` and the `task` tool.
- Only `.md` files are recognized; any other file type in the agents directory is ignored.
- OpenCode walks from the current working directory up to the git worktree root, then checks for `.opencode/agents/` at the root.
- Agents are **scoped per-project**: discovery starts from the repository root, so two different repos can each have an `ideas-agent.md` without collision.
- The global path (`~/.config/opencode/agents/`) is checked as a fallback; project-level agents take priority.

### 3. Skill Discovery

Skill directories are discovered from the following paths (in priority order):

1. `.opencode/skills/<name>/SKILL.md` — project-level
2. `~/.config/opencode/skills/<name>/SKILL.md` — global
3. `.claude/skills/<name>/SKILL.md` — project (Claude Code compat)
4. `~/.claude/skills/<name>/SKILL.md` — global (Claude Code compat)
5. `.agents/skills/<name>/SKILL.md` — project (agent compat)
6. `~/.agents/skills/<name>/SKILL.md` — global (agent compat)

**Structure requirements:**

- `skills/<name>/SKILL.md` — exactly one directory level, exactly one file named `SKILL.md` (all caps).
- The `name` field in the skill's YAML frontmatter must match the parent directory name.
- Subdirectories within a skill directory are not supported.

**Namespace constraint:**

Skills share a **global flat namespace** across all OpenCode projects on the same machine. Unlike agents (scoped per-project), skill names can collide. If two discovery locations define a skill with the same name, the higher-priority path wins (project > global > compat). This is why the Knowledge Base skills use a `kb-` prefix — it scopes them against skill names from other projects.

### 4. No opencode.json Changes

The current `opencode.json` is minimal:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["AGENTS.md"]
}
```

No changes are needed because:

- **Markdown agents are auto-discovered** — the `"agent"` key in `opencode.json` is only needed for JSON-format agent definitions, which we do not use.
- **`permission.task` defaults to `allow`** — primary agents can invoke subagents via the `task` tool without any configuration. Subagent permissions are defined in each agent's own frontmatter.
- **`permission.skill` defaults to `allow`** — agents can call `skill()` to load skill instructions without a blanket `permission` block in `opencode.json`. Skill-level restriction can be added per-agent in the agent's YAML frontmatter if needed.
- The only existing config key (`instructions`) controls which files are loaded into the base system prompt. This is unrelated to agent or skill registration.

## Analysis

### Zero-Friction Addition

Adding a new agent file to `.opencode/agents/` requires:
1. Creating the directory (if it does not exist)
2. Writing the `.md` file with valid YAML frontmatter and prompt body
3. No edits to any other file — not `opencode.json`, not a registry, not a manifest

This means the five section-specific agents (ideas, knowledge, research, proposals, adr) can be added as a clean set of files with zero risk of merge conflicts on shared config files. Each agent is independently discoverable the moment its file exists on disk.

### Explicit Registration (Not Used)

OpenCode supports an alternative agent definition format via the `"agent"` key in `opencode.json`:

```json
{
  "agent": {
    "ideas-agent": {
      "description": "Draft and evolve ideas",
      "prompt": "...",
      "permission": { ... }
    }
  }
}
```

This JSON format is an alternative to Markdown-based agents. We are **not** using it because:

- Markdown files are easier to version-control, diff, and review.
- Markdown files keep agent prompts in dedicated files rather than bloating `opencode.json`.
- JSON-format agents do not support the full YAML frontmatter richness (tags, author, date, and other frontmatter metadata).
- Markdown agents auto-discover from a well-known directory; JSON agents require an explicit config key that must be manually maintained.

### This Repo's Current State

| Resource | Exists? | Notes |
|---|---|---|
| `.opencode/agents/` | No | Does not exist — a clean addition |
| `.opencode/skills/` | Yes | Contains `gh/` skill (GitHub CLI) |
| `opencode.json` | Yes | Minimal — no agent or permission config |

Adding agent files is a **clean addition**. There are no pre-existing agent files to conflict with, no permission defaults to override, and no config keys to touch. The `gh/` skill is orthogonal and remains unaffected.

## Recommendations

1. **Do not modify `opencode.json`** for agent or skill registration. All five section-specific agents and all shared skills will be auto-discovered.
2. **Create `.opencode/agents/`** as a new directory containing the five agent `.md` files.
3. **Do not add an `"agent"` key** to `opencode.json`. Keep JSON-format definitions as a documented alternative but do not use them.
4. **Use the `kb-` prefix** for skills to avoid flat-namespace collisions with other projects on the same machine.
5. **No registration step** in any setup or onboarding documentation — placing files in the correct directory is sufficient.

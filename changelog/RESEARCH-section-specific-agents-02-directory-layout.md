---
title: "Directory Layout: Agent Files and Skill Directories"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - agents
  - skills
  - directory-layout
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-discovery"
  - knowledge: "knowledge/tooling/opencode/agents/agent-configuration"
  - knowledge: "knowledge/tooling/opencode/skills/skill-configuration"
  - knowledge: "knowledge/tooling/opencode/skills/overview"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-05-31
---

# Directory Layout: Agent Files and Skill Directories

## Proposed Layout

The complete directory structure for agents and skills within the Knowledge Base:

```
knowledge-base/
├── .opencode/
│   ├── agents/
│   │   ├── ideas-agent.md
│   │   ├── knowledge-agent.md
│   │   ├── research-agent.md
│   │   ├── proposals-agent.md
│   │   ├── adr-agent.md
│   │   ├── kb-architect.md
│   │   ├── kb-tech-lead.md
│   │   └── kb-editor.md
│   └── skills/
│       ├── kb-scaffold-topic/
│       │   └── SKILL.md
│       ├── kb-frontmatter-validate/
│       │   └── SKILL.md
│       ├── kb-cross-link-check/
│       │   └── SKILL.md
│       └── kb-status-transition/
│           └── SKILL.md
├── ideas/
│   └── AGENTS.md
├── knowledge/
│   └── AGENTS.md
├── research/
│   ├── AGENTS.md
│   └── section-specific-agents/
│       ├── README.md
│       ├── overview.md
│       ├── 01-approach-comparison.md
│       └── ... (other research files)
├── proposals/
│   └── AGENTS.md
├── adr/
│   └── AGENTS.md
└── opencode.json
```

The layout places all agent files under `.opencode/agents/` and all skill directories under `.opencode/skills/`, mirroring OpenCode's discovery paths. Section-level `AGENTS.md` files remain in their respective content directories and serve as the declarative rules layer that agents read at runtime.

## Agent File Format

Each agent file is a markdown document with YAML frontmatter and a prompt body. The frontmatter defines metadata and permissions; the body contains the agent's instructions.

```markdown
---
description: Draft and evolve ideas with changelog tracking; enforce idea section conventions
mode: subagent
model: opencode-go/deepseek-v4-flash
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  bash: allow
  list: allow
  task: allow
  skill: allow
---
## Purpose
You are a specialized agent for the ideas section of the Knowledge Base.
...
```

**Field reference:**

| Field | Required | Description |
|---|---|---|
| `description` | Yes | Short, one-line description of the agent's purpose. Shown in `@mention` lists and agent switcher. |
| `mode` | Yes | Must be `subagent`. Subagents are invoked via `@mention` or the `task` tool; they cannot be set as default agents. |
| `model` | No | Pins the LLM model for this agent. If omitted, inherits the caller's model. |
| `permission` | Yes | Maps every tool to `allow`, `ask`, or `deny`. The example above grants full access. Note that `write` is not listed separately — the `edit` permission covers both read-and-write and create operations. |

**Model recommendations per section:**

| Agent | Recommended Model | Rationale |
|---|---|---|
| `ideas-agent.md` | `opencode-go/deepseek-v4-flash` | Simple scaffolding and frontmatter filling; does not need a large model. |
| `knowledge-agent.md` | `opencode-go/deepseek-v4-pro` | Factual accuracy and source validation benefit from stronger reasoning. |
| `research-agent.md` | `opencode-go/deepseek-v4-pro` | Synthesis of ideas and knowledge into analysis requires complex reasoning. |
| `proposals-agent.md` | `opencode-go/deepseek-v4-pro` | Implementation planning and cross-referencing benefit from deeper context handling. |
| `adr-agent.md` | `opencode-go/deepseek-v4-pro` | Decision records require careful trade-off analysis and consequence reasoning. |

## Skill Directory Format

Each skill is a directory containing a single `SKILL.md` file. The directory name is the skill's identifier; the file name must be exactly `SKILL.md` (all caps).

```markdown
---
name: kb-scaffold-topic
description: Create topic folder from section template, populate frontmatter
---
```

**Field reference:**

| Field | Required | Constraints | Description |
|---|---|---|---|
| `name` | Yes | Must match the parent directory name; regex `^[a-z0-9]+(-[a-z0-9]+)*$` | Skill identifier used in `skill({ name: "..." })` calls. |
| `description` | Yes | 1–1024 characters | Human-readable summary shown in `<available_skills>` listing. |

**Skill directory structure:**

```
skills/
├── kb-scaffold-topic/
│   └── SKILL.md
├── kb-frontmatter-validate/
│   └── SKILL.md
├── kb-cross-link-check/
│   └── SKILL.md
└── kb-status-transition/
    └── SKILL.md
```

No subdirectories or additional files are permitted within a skill directory — only `SKILL.md` at the top level.

## Skill Namespace: The `kb-` Prefix

Skill names exist in a **globally flat namespace** across all OpenCode projects on the same machine. Unlike agents (which are scoped to a project's `.opencode/agents/` directory and auto-discovered per-repository), skills share a single registry:

- `skill({ name: "scaffold-topic" })` could resolve to a skill from any project's `.opencode/skills/` directory.
- If two discovery locations define a skill with the same name, one silently shadows the other according to the discovery priority order: project (`.opencode/skills/`) > global (`~/.config/opencode/skills/`) > compat paths (`.claude/skills/`, `.agents/skills/`).

The `kb-` prefix scopes the Knowledge Base's skills to avoid collision:

| Without prefix | With `kb-` prefix |
|---|---|
| `scaffold-topic` — ambiguous | `kb-scaffold-topic` — clearly belongs to knowledge-base |
| `frontmatter-validate` — generic | `kb-frontmatter-validate` — namespaced |
| `cross-link-check` — generic | `kb-cross-link-check` — namespaced |
| `status-transition` — generic | `kb-status-transition` — namespaced |

The prefix follows the skill name regex requirement (`^[a-z0-9]+(-[a-z0-9]+)*$`) and is consistent with the flat-namespace constraint.

**This does not apply to most agents.** Section agents (`ideas-agent`, `knowledge-agent`, etc.) under `.opencode/agents/` are auto-discovered per-project by walking up from the CWD to the git worktree root. Two projects can each have an `ideas-agent.md` without conflict because discovery is scoped to the repository root.

**Role agents are an exception.** Generic role names like `architect`, `tech-lead`, and `editor` could collide with similarly-named agents from other projects on the same machine. The `kb-` prefix scopes them explicitly: `kb-architect`, `kb-tech-lead`, `kb-editor`. This is the same rationale used for shared skills — `kb-` signals these belong to this Knowledge Base repo.

## Current State vs Target

| Aspect | Current State | Target State |
|---|---|---|
| `.opencode/agents/` | Directory does not exist | 8 agent files: 5 section agents (ideas, knowledge, research, proposals, adr) + 3 role agents (architect, tech-lead, editor) |
| `.opencode/skills/` | Only `gh/` exists | 4 skill directories: `kb-scaffold-topic/`, `kb-frontmatter-validate/`, `kb-cross-link-check/`, `kb-status-transition/` |
| `opencode.json` | As-is | No changes needed — auto-discovery handles agents and skills |

The `gh/` skill (discovered automatically by OpenCode from `.opencode/skills/gh/SKILL.md` and listed in agents' `<available_skills>` at runtime) remains in place and is unaffected by this research. It serves GitHub CLI interactions and is orthogonal to the Knowledge Base agents.

## Nesting Constraints

Both agents and skills enforce flat nesting rules:

**Agents:**

- Files must be placed directly inside `.opencode/agents/`.
- Subdirectories are not supported — `agents/ideas-agent.md` is valid, `agents/ideas/agent.md` is not.
- Multiple agents per directory are fine; each `.md` file is independently discovered.

**Skills:**

- One directory level: `skills/<name>/SKILL.md`.
- Deeper nesting is not supported — `skills/foo/bar/SKILL.md` is not discovered.
- Only `SKILL.md` (exact filename, all caps) is recognized within each skill directory.

**Discovery mechanism:**

Both agents and skills are discovered by walking up from the current working directory to the git worktree root. OpenCode looks for `.opencode/agents/` and `.opencode/skills/` relative to the repository root, meaning the layout is location-independent within the project.

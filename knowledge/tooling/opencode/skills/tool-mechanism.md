---
title: "Skill Tool Mechanism"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - discovery
  - permissions
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Skill Tool Mechanism

## How the `skill` Tool Works

- OpenCode injects `<available_skills>` XML blocks into the agent's tool description
- Each skill entry has `<name>` and `<description>` tags
- Agents call `skill({ name: "..." })` to load the full SKILL.md content into context
- This is a native tool mechanism, not a filesystem read hack

## Agent Sees Skills via `<available_skills>` XML Blocks

When a skill is registered and permitted, it appears in the agent's tool description as an XML block:

```xml
<available_skills>
  <skill>
    <name>pr-review</name>
    <description>Automated code review with inline suggestions</description>
  </skill>
  <skill>
    <name>git-release</name>
    <description>Create consistent releases and changelogs</description>
  </skill>
</available_skills>
```

The agent receives this block as part of the tool definition for the `skill` tool. It cannot browse the filesystem directly to find skills — it relies entirely on this injected catalogue.

## Skill Descriptions Are the Primary Discovery Mechanism

The `description` field (1-1024 characters) is the sole selector for the agent. The agent evaluates which skill to load by matching the description against the current task context.

**Effective descriptions**:

- Start with an action verb: "Create", "Validate", "Analyze", "Generate", "Review"
- Include domain-specific keywords the agent can match against user requests
- State what the skill does, not what it is (e.g. "Create consistent releases and changelogs" not "Release management tooling")
- Keep under 120 characters if possible — the XML block is scanned quickly by the agent

**Ineffective descriptions**:

- Vague or generic: "Git stuff", "Helper utilities"
- Tool-centric without behavior: "Wrapper around gh CLI"
- Too long: the agent may truncate or skim, reducing matching accuracy

## Permission-Based Filtering

Permissions control which skills an agent can see and load. Configured at multiple levels:

**Global (opencode.json)**:

```json
{
  "permission": {
    "skill": {
      "*": "allow",
      "pr-review": "allow",
      "internal-*": "deny",
      "experimental-*": "ask"
    }
  }
}
```

**Per-agent (custom agent frontmatter)**:

```yaml
---
name: my-agent
permission:
  skill:
    "documents-*": "allow"
---
```

**Built-in agent overrides (opencode.json)**:

```json
{
  "agent": {
    "plan": {
      "permission": {
        "skill": {
          "internal-*": "allow"
        }
      }
    }
  }
}
```

Permission values:

| Value | Effect on Catalogue |
|---|---|
| `allow` | Skill included in `<available_skills>`, loadable immediately |
| `deny` | Skill excluded from `<available_skills>`, agent unaware of it |
| `ask` | Skill included in `<available_skills>`, but loading requires user approval |

When `tools.skill` is set to `false` for an agent, the entire `<available_skills>` block is omitted and no skills are advertised.

## See Also

- [Skill Concepts](concepts.md) — Foundational concepts
- [Configuration](configuration.md) — Permission configuration details
- [Agent Permissions](../agents/permissions.md) — Agent-level permission model

---
title: "Skill Configuration (SKILL.md)"
status: draft
author: "Khalid"
date: 2026-05-31
tags:
  - opencode
  - skills
  - configuration
  - yaml
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions"
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents"
last_audit_date: 2026-05-31
---

# Skill Configuration (SKILL.md)

## SKILL.md Frontmatter Specification

Each `SKILL.md` file must begin with `---`-delimited YAML frontmatter. Unknown fields are silently ignored.

### Required Fields

| Field | Type | Constraints |
|---|---|---|
| `name` | `string` | 1–64 chars, must match regex `^[a-z0-9]+(-[a-z0-9]+)*$`, must equal parent directory name |
| `description` | `string` | 1–1024 chars, used by agent to decide whether to load the skill |

### Optional Fields

| Field | Type | Constraints |
|---|---|---|
| `license` | `string` | SPDX or freeform license identifier (e.g. `MIT`, `Apache-2.0`) |
| `compatibility` | `string` | Tool/agent compatibility marker (e.g. `opencode`) |
| `metadata` | `map[string,string]` | Arbitrary key-value pairs for classification or routing |

### Complete Example

```yaml
---
name: git-release
description: Create consistent releases and changelogs
license: MIT
compatibility: opencode
metadata:
  audience: maintainers
  workflow: github
---
```

## Name Validation

- **Regex**: `^[a-z0-9]+(-[a-z0-9]+)*$`
- **Length**: 1–64 characters
- **Rules**:
  - Lowercase alphanumeric only (`a-z`, `0-9`)
  - Hyphens allowed only as single separators between alphanumeric segments
  - No leading or trailing `-`
  - No consecutive `--`
  - **Must exactly match** the name of the directory containing `SKILL.md`

Valid examples: `gh`, `git-release`, `pr-review`, `terraform-v1`

Invalid examples: `Git-Release`, `pr_review`, `--experiment`, `trailing-`, `a-b-`

## Description Rules

- **Length**: 1–1024 characters
- **Purpose**: Agents inspect the description to decide whether the skill is relevant — it must be specific enough for accurate selection
- **Guidance**: Include action verbs and domain keywords (e.g. "Create consistent releases and changelogs" rather than "Git stuff")

## Discovery & File Placement

OpenCode searches the following locations (in order):

| Priority | Path |
|---|---|
| Project | `.opencode/skills/<name>/SKILL.md` |
| Global | `~/.config/opencode/skills/<name>/SKILL.md` |
| Project (Claude compat) | `.claude/skills/<name>/SKILL.md` |
| Global (Claude compat) | `~/.claude/skills/<name>/SKILL.md` |
| Project (agent compat) | `.agents/skills/<name>/SKILL.md` |
| Global (agent compat) | `~/.agents/skills/<name>/SKILL.md` |

Project-local paths: OpenCode walks up from CWD to the git worktree root, loading `SKILL.md` files from `.opencode/skills/`, `.claude/skills/`, and `.agents/skills/` directories along the way.

## Full Example (git-release skill)

```markdown
---
name: git-release
description: Create consistent releases and changelogs
license: MIT
compatibility: opencode
metadata:
  audience: maintainers
  workflow: github
---
## What I do
- Draft release notes from merged PRs
- Propose a version bump
- Provide a copy-pasteable `gh release create` command

## When to use me
Use this when you are preparing a tagged release.
Ask clarifying questions if the target versioning scheme is unclear.
```

When loaded by the agent, the skill appears in the tool description as:

```xml
<available_skills>
  <skill>
    <name>git-release</name>
    <description>Create consistent releases and changelogs</description>
  </skill>
</available_skills>
```

The agent loads it via `skill({ name: "git-release" })`.

## Permission Configuration

Permissions control which skills agents can access. Configured in `opencode.json`:

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

| Permission | Behavior |
|---|---|
| `allow` | Skill loads immediately |
| `deny` | Skill hidden from agent, access rejected |
| `ask` | User prompted for approval before loading |

Patterns support wildcards: `internal-*` matches `internal-docs`, `internal-tools`, etc.

### Per-Agent Overrides

**Custom agents** (in agent frontmatter):

```yaml
---
name: my-agent
permission:
  skill:
    "documents-*": "allow"
---
```

**Built-in agents** (in `opencode.json`):

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

### Disabling the Skill Tool Entirely

**Custom agents**:

```yaml
---
tools:
  skill: false
---
```

**Built-in agents**:

```json
{
  "agent": {
    "plan": {
      "tools": {
        "skill": false
      }
    }
  }
}
```

When disabled, the `<available_skills>` section is omitted entirely from the agent tool description.

## Troubleshooting

If a skill does not show up in `<available_skills>`:

1. **Check `SKILL.md` casing** — the filename must be all-caps `SKILL.md`, not `skill.md` or `Skill.md`
2. **Validate frontmatter** — both `name` and `description` are required; missing them causes the skill to be silently skipped
3. **Name mismatch** — the `name` field must exactly match the directory name; `name: git-release` in `.opencode/skills/git-release/SKILL.md`
4. **Name uniqueness** — skill names must be unique across **all** discovery locations (project and global); a duplicate name may shadow or override
5. **Permission denies** — skills with `deny` permissions are hidden from agents; check both global `permission.skill` and per-agent overrides
6. **Tool disabled** — if `tools.skill` is set to `false` for the active agent, skills will not be advertised at all

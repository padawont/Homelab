---
title: "Skill File Format"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - yaml
  - naming
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Skill File Format

## File Format

Each skill is a `SKILL.md` file inside a directory named after the skill:

```
.opencode/skills/<name>/SKILL.md
```

Required frontmatter:
- `name` (string) — skill identifier, must match directory name
- `description` (string, 1-1024 chars) — what the skill does, for agent selection

Optional frontmatter:
- `license` (string)
- `compatibility` (string)
- `metadata` (map of string to string)

Unknown frontmatter fields are ignored, allowing forward compatibility.

## Naming Rules

- 1-64 characters
- Lowercase alphanumeric with single hyphen separators
- No leading or trailing `-`
- No consecutive `--`
- Must match the directory name containing SKILL.md
- Regex: `^[a-z0-9]+(-[a-z0-9]+)*$`

### Valid Examples

`gh`, `git-release`, `pr-review`, `terraform-v1`

### Invalid Examples

`Git-Release`, `pr_review`, `--experiment`, `trailing-`, `a-b-`

## See Also

- [Configuration](configuration.md) — Full frontmatter specification and validation rules
- [Skill Concepts](concepts.md) — What skills are and how they differ from agents

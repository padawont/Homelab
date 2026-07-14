---
title: "Convention-Based Skill Registration"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - registry
  - conventions
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Convention-Based Skill Registration

## Convention-Based Registration

Skills are registered by filesystem convention, not by declaration in a central registry file. Any directory following the naming and structure rules is automatically discoverable.

**Path convention**: `.opencode/skills/<name>/SKILL.md`

The skill name is derived from the parent directory name. OpenCode searches multiple discovery paths when building the skill catalogue:

| Priority | Path | Scope |
|---|---|---|
| Project | `.opencode/skills/<name>/SKILL.md` | Per-repo skills |
| Global | `~/.config/opencode/skills/<name>/SKILL.md` | User-wide skills |
| Project (Claude compat) | `.claude/skills/<name>/SKILL.md` | Cross-tool compatibility |
| Global (Claude compat) | `~/.claude/skills/<name>/SKILL.md` | Cross-tool compatibility |
| Project (agent compat) | `.agents/skills/<name>/SKILL.md` | Cross-tool compatibility |
| Global (agent compat) | `~/.agents/skills/<name>/SKILL.md` | Cross-tool compatibility |

There is no central manifest, JSON index, or registration step. The mere presence of a valid `SKILL.md` at one of the recognized paths is sufficient for the skill to appear in the agent's catalogue.

**No central registry file needed** — this is a deliberate design choice:

- Adding a skill is a single file write; no registry edits, no merge conflicts on a shared index.
- Removing a skill is a single file delete; no stale references linger in a registry.
- Moving a skill between scopes (project to global) is just moving the directory; paths are resolved at runtime.
- Teams can fork or vendor skill directories without coordinating on a central index.

## Filesystem is the Registry

The catalogue of available skills is the union of all `SKILL.md` files found across the discovery paths. OpenCode builds the catalogue at agent startup by walking each recognized skill directory.

**Name uniqueness constraint**: Skill names must be unique across all discovery locations. A duplicate name at a higher-priority path shadows the lower-priority entry. For example, a project-local `.opencode/skills/gh/SKILL.md` shadows a global `~/.config/opencode/skills/gh/SKILL.md`.

**No versioning in names**: Skill names are stable identifiers. Version information belongs in the `SKILL.md` content or frontmatter. If a breaking change is needed, introduce a new skill with a different name and deprecate the old one.

## See Also

- [Metadata Taxonomy](metadata-taxonomy.md) — Queryable registry pattern and metadata conventions
- [Maintenance](maintenance.md) — Catalogue maintenance and lifecycle management
- [Configuration](configuration.md) — SKILL.md frontmatter specification
- [File Format](file-format.md) — Naming rules and SKILL.md structure

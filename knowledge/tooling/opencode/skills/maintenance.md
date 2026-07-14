---
title: "Skill Catalogue Maintenance"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - registry
  - maintenance
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Skill Catalogue Maintenance

## Naming Conventions for Skill Categorization

Skill names serve double duty as identifiers and as the top-level taxonomy. Consistent naming makes the catalogue scannable by both humans and agents.

**Functional naming**: Name after the verb phrase that describes what the skill does.

```
pr-review          # reviews pull requests
git-release        # creates releases
env-setup-python   # sets up Python environments
db-migrate         # runs database migrations
```

**Domain-scoped naming**: Prefix with a domain when multiple skills operate in the same area.

```
docs-api           # API documentation
docs-architecture  # architecture documentation
docs-changelog     # changelog generation
```

**Do not**:

- Use numeric prefixes for ordering — catalogues are not ordered lists
- Use abbreviations without expansion (`db` is acceptable, `dbsch` is not)
- Embed version numbers in the name (`pr-review-v2`)
- Use underscores or mixed case — must match `^[a-z0-9]+(-[a-z0-9]+)*$`

### Metadata Taxonomy by Skill Type

Different skill types benefit from different metadata emphasis:

| Skill Type | Important Metadata | Description Strategy |
|---|---|---|
| **Tool wrappers** (e.g. gh, git, docker) | `audience`, `workflow`, `language` | Name the tool and key operations |
| **Review/QA** (e.g. pr-review, lint-check) | `category: review`, `audience`, `tags` | State the review scope and tooling |
| **Scaffolding** (e.g. project-init, component-gen) | `category: scaffold`, `complexity` | Describe what gets generated |
| **CI/CD** (e.g. deploy, test-runner) | `workflow: ci`, `audience: ops` | Name the pipeline stage |
| **Documentation** (e.g. docs-api, changelog) | `category: docs`, `audience: all` | State the output format and scope |

### Cross-Referencing Skills to Agents, Tools, and Workflows

A well-maintained catalogue documents relationships between skills and other system components:

**Skill to agent mapping**: When a skill is designed for a specific agent type, document it in the SKILL.md content and optionally in `metadata.agent`.

```yaml
metadata:
  agent: kb-architect
```

**Skill to plugin/MCP mapping**: If a skill depends on a plugin or MCP server, declare it in `metadata.plugin`. This signals to the agent that the plugin must be available.

```yaml
metadata:
  plugin: "@opencode/plugin-github"
```

**Skill to workflow mapping**: Use `metadata.workflow` to associate a skill with a pipeline or process. The agent can use this to select skills when it recognizes a workflow context.

```yaml
metadata:
  workflow: github
```

**Catalogue index file**: For repos with many skills, maintain a catalogue index at `.opencode/skills/README.md` or a dedicated `.opencode/skills/CATALOGUE.md`. This file lists all skills with their metadata and a short description, updated when skills are added or removed. It serves as a human-readable complement to the machine-injected `<available_skills>` block.

### Lifecycle of a Skill in the Catalogue

1. **Added**: Place `SKILL.md` in the correct directory. It appears in `<available_skills>` immediately on next agent startup.
2. **Deprecated**: Update the `description` to indicate deprecation and point to a replacement. Consider setting permissions to `ask` to flag the transition.
3. **Removed**: Delete the `SKILL.md` or the entire skill directory. The skill disappears from `<available_skills>` on next agent startup.
4. **Replaced**: Introduce a new skill with the new name. Update the old skill's description to reference the replacement. After a transition period, remove the old skill.

### Registry Audit

Periodically audit the skill catalogue for:

- **Unused skills**: Skills that are never loaded by any agent. Review whether they are still needed.
- **Overlapping descriptions**: Two or more skills whose descriptions are too similar, causing agent confusion.
- **Stale metadata**: Metadata values that no longer match the current taxonomy or reference removed agents/plugins.
- **Permission gaps**: Skills that should have restricted permissions but are set to `allow` globally.

## See Also

- [Convention Registration](convention-registration.md) — How skills are registered by filesystem convention
- [Metadata Taxonomy](metadata-taxonomy.md) — Metadata fields and conventions
- [Configuration](configuration.md) — SKILL.md frontmatter specification

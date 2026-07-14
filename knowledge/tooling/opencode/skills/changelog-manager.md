---
title: "Changelog Manager Workflow Skill"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - workflows
  - release
  - changelog
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
  - url: "https://keepachangelog.com/en/1.1.0/"
    title: "Keep a Changelog"
  - url: "https://www.conventionalcommits.org/en/v1.0.0/"
    title: "Conventional Commits"
last_audit_date: 2026-06-07
---

# Changelog Manager Workflow Skill

## Purpose

Generate and maintain changelog files following the Keep a Changelog convention. The skill analyzes git log history, categorizes changes by type, formats entries, and updates the changelog file in the project.

## When to Invoke

When the user asks "update the changelog", "generate release notes", "add changelog entry", or before a release cut.

## Trigger Conditions

| Condition | Type |
|---|---|
| User requests changelog update | Manual |
| Pre-release workflow | Automatic (tag push) |
| After `pr-packager` completes | Chained skill invocation |

## Required Permissions

| Permission | Purpose |
|---|---|
| `bash` | Run `git log`, `git tag`, `git describe` |
| `read` | Read existing CHANGELOG.md |
| `write` | Modify CHANGELOG.md |
| `grep` | Parse conventional commits |

## Agent Tool Requirements

The agent needs `bash` for git operations and `write` for file modification. The `pr-packager` skill may be a dependency if the workflow chains releases from PR groupings.

## Example SKILL.md Frontmatter

```yaml
---
name: changelog-manager
description: Generate and maintain changelogs per Keep a Changelog, using git log analysis and conventional commit categorization
license: MIT
compatibility: opencode
metadata:
  workflow: release
  audience: maintainers
  trigger: manual+automatic
---
```

## Expected Skill Body Sections

- Git log extraction between tags or commits
- Conventional commit categorization (Added, Changed, Deprecated, Removed, Fixed, Security)
- Keep a Changelog format rules (Unreleased section, reverse chronological order)
- Version bump suggestion (semver inference from commit types)
- Changelog file editing pattern (insert at top of Unreleased section)
- Dry-run mode for review before applying

## See Also

- [PR Packager](pr-packager.md) — Parent skill that may chain into changelog management
- [Dependency Checker](dependency-checker.md) — Often chained before a release cut
- [Workflow Patterns](workflow-patterns.md) — Cross-cutting conventions for all workflow skills

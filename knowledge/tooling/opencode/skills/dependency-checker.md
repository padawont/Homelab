---
title: "Dependency Checker Workflow Skill"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - workflows
  - dependencies
  - security
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Dependency Checker Workflow Skill

## Purpose

Check project dependencies for outdated or vulnerable packages. The skill scans package manifest files, cross-references against vulnerability advisories, and suggests safe update paths.

## When to Invoke

When the user asks "check dependencies", "any vulnerabilities?", "update dependencies", or as part of a scheduled maintenance workflow.

## Trigger Conditions

| Condition | Type |
|---|---|
| User requests dependency audit | Manual |
| Scheduled cron or CI job | Automatic |
| Dependabot alert received | Automatic (webhook) |
| Before a release cut | Chained skill (from changelog-manager) |

## Required Permissions

| Permission | Purpose |
|---|---|
| `bash` | Run `npm audit`, `cargo audit`, `pip-audit`, or equivalent |
| `read` | Read manifest files (package.json, Cargo.toml, requirements.txt, etc.) |
| `glob` | Locate all manifest files across workspace |
| `webfetch` | Fetch advisory data from external sources |

## Agent Tool Requirements

The agent needs `bash` for local tool execution and `webfetch` for external advisory lookups. The agent should have `permission.bash` configured for package manager commands.

## Example SKILL.md Frontmatter

```yaml
---
name: dependency-checker
description: Scan dependencies for outdated or vulnerable packages, cross-reference advisories, suggest safe update paths
license: MIT
compatibility: opencode
metadata:
  workflow: maintenance
  audience: developers
  trigger: manual+automatic
---
```

## Expected Skill Body Sections

- Manifest file discovery (multi-language project support)
- Lockfile-aware scanning for deterministic results
- Advisory source identification (OSV, NVD, GitHub Advisory DB, language-specific registries)
- Severity classification (critical, high, medium, low)
- Update path suggestion (semver-compatible vs breaking)
- Batch update proposal format
- Dry-run mode for review before applying changes

## See Also

- [Changelog Manager](changelog-manager.md) — Parent skill that may chain dependency checks before release
- [Workflow Patterns](workflow-patterns.md) — Cross-cutting conventions for all workflow skills

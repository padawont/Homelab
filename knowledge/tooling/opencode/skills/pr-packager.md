---
title: "PR Packager Workflow Skill"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
  - workflows
  - github
  - pr
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# PR Packager Workflow Skill

## Purpose

Package pull request descriptions from local commits. The skill collects commit messages from a branch, groups them by logical topic, generates conventional changelog entries, and produces a formatted PR body ready for submission.

## When to Invoke

When the user asks "prepare a PR", "create a pull request", "generate PR description", or when a branch has un-pushed commits and the user wants to submit them.

## Trigger Conditions

| Condition | Type |
|---|---|
| User provides branch name or asks to "open a PR" | Manual |
| Pre-push git hook | Automatic |
| After commit on a feature branch with remote URL configured | Automatic (with user confirmation) |

## Required Permissions

| Permission | Purpose |
|---|---|
| `bash` | Run `git log`, `git diff`, `git branch`, commit inspection |
| `grep` | Scan commit messages for conventional commit patterns |
| `read` | Read project changelog, conventions file |

## Agent Tool Requirements

The agent needs `bash` access for git operations. The `gh` skill is optional but recommended for draft PR creation — see [`gh-case-study.md`](./gh-case-study.md) for detailed usage patterns. The agent should have the `general` persona with standard tool access.

## Example SKILL.md Frontmatter

```yaml
---
name: pr-packager
description: Package PR descriptions from local commits, group by topic, generate changelog entries, produce formatted PR body
license: MIT
compatibility: opencode
metadata:
  workflow: github
  audience: developers
  trigger: manual
---
```

## Expected Skill Body Sections

- Commit log extraction (`git log BASE..HEAD`)
- Conventional commit parsing (feat, fix, chore, docs, etc.)
- Topic grouping heuristics
- Changelog entry formatting (keepachangelog-compatible)
- PR body template assembly
- Optional `gh pr create` invocation pattern

## See Also

- [Changelog Manager](changelog-manager.md) — Often chained after PR packaging for release notes
- [gh-case-study.md](gh-case-study.md) — Detailed `gh` skill walkthrough
- [Workflow Patterns](workflow-patterns.md) — Cross-cutting conventions for all workflow skills

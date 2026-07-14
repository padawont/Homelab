---
title: "gh Skill Case Study"
status: draft
author: "Khalid"
date: 2026-05-31
tags:
  - opencode
  - skills
  - gh
  - case-study
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-06
---

# gh Skill Case Study

## Overview
The `gh` skill at `.opencode/skills/gh/SKILL.md` is a workflow skill for GitHub CLI operations. It provides agents with patterns for invoking the GitHub CLI (`gh`), covering structured output, pagination, repo targeting, search vs list, and `gh api` fallback. The repo also includes four knowledge-base-specific skills (`kb-frontmatter-validate`, `kb-cross-link-check`, `kb-scaffold-topic`, `kb-status-transition`) documented in the skills overview.

## Frontmatter Analysis
- **name**: `gh` — 2 characters, lowercase alphanumeric, valid per `^[a-z0-9]+(-[a-z0-9]+)*$`, matches the directory name
- **description**: "Patterns for invoking the GitHub CLI (gh) from agents. Covers structured output, pagination, repo targeting, search vs list, gh api fallback." — under 1024 chars, specific action-oriented
- **Optional fields**: none used (only `name` and `description` are required)

## Structure Walkthrough
The skill has 8 sections after frontmatter:

| Section | Purpose | Key Guidance |
|---------|---------|--------------|
| Interactivity policy | Prevents defensive pager/color stubs | `gh` already handles non-TTY correctly |
| Parsing JSON | Three-tier structured output | `--json` → `--jq` → `--template`; `-T` collision gotcha |
| Pagination | Result limits | `-L N` for list commands, `--paginate` for API |
| Repo targeting | Override default repo | `-R OWNER/REPO` |
| Search vs list | Which command to use | `gh search` for cross-repo/author/label; scoped `--search` otherwise |
| `gh api` fallback | Typed command gaps | GraphQL, REST shortcuts, review-thread comments |
| Authentication | Diagnostics | `gh auth status` with `--json` |
| Other notes | Edge cases | Color/env var behavior, PR checkout vs view |

## Design Patterns
- **Directive tone**: each section says what the agent should do, not what's possible
- **Gotcha-first**: common mistakes called out explicitly (e.g. `-T` collision with body-template)
- **LLM-scannable**: short sections (2-7 lines each), no fluff
- **No redundant docs**: doesn't repeat `gh --help` — only covers what agents get wrong

## Agent Usage Flow
1. Agent encounters a task requiring GitHub operations
2. The `skill` tool lists the `gh` skill in `<available_skills>` with name + description
3. Agent calls `skill({ name: "gh" })` to load the full SKILL.md content
4. Skill instructions are injected into the agent's context
5. Agent applies the rules to construct correct `gh` invocations inline

## Repo Context
This repo uses `gh` extensively for issue and PR operations. The skill exists to prevent agents from making common mistakes (wrong flags, missing pagination, incorrect JSON field selection) that would waste human review in PRs and issue management.

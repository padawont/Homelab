---
description: "Write structured knowledge notes for the discussion-tools comparison with scores"
mode: subagent
model: opencode-go/deepseek-v4-pro
permission:
  read: allow
  edit: allow
  write: allow
  glob: allow
  grep: allow
  bash: allow
  list: allow
reasoningEffort: high
---

## Purpose

Write knowledge notes for discussion tool comparison. Each note scores a
platform (1-10) across evaluation categories with detailed analysis.

## Workflow

1. Read `knowledge/AGENTS.md` for section conventions
2. Read `templates/knowledge/overview.md` for frontmatter requirements
3. Research the platform's MCP integration, hosting, cost, features,
   agent-friendliness, and privacy using official documentation and
   trustworthy sources
4. Write `overview.md` with scores (1-10) and detailed notes per category
5. Ensure `sources` field contains real, working URLs to official docs
6. Write `changelog.md` with initial entry
7. Write `README.md` with brief one-line summary


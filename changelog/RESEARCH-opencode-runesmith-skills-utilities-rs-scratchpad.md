---
title: "Scratchpad Management Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - skills
  - scratchpad
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
references:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Scratchpad Management Skill Design

## Skill Identity

| Field | Value |
|---|---|
| Skill name | `rs-scratchpad` |
| Plugin | `@runicengines/opencode-runesmith` |
| Prefix | `rs-` |
| Used by | All agents (primarily the first agent in a session) |
| Trigger | At session start, or when user requests scratchpad operations |

## Purpose

Manages the `.runesmith/` scratchpad lifecycle — initialising new session directories, clearing existing ones, and reporting status. This is the session entry point: the first agent to run in a session calls `rs-scratchpad init` to determine the session path before any other work begins.

## Commands

### `rs-scratchpad init` — Initialise a New Session

**What it does:** Determines the session path and creates the session directory structure. Called by the first agent that starts working in a session.

**Workflow:**
1. Read current git branch: `git rev-parse --abbrev-ref HEAD`
2. Get today's date: `date +%Y-%m-%d`
3. Compose candidate path: `.runesmith/{date}-{branch}/`
4. Check if `.runesmith/{date}-{branch}/` already exists:
   - **No**: create it with `specs/`, `reports/`, `logs/`, `cache/` subdirectories
   - **Yes**: ask the user:
     > "Session directory `.runesmith/{date}-{branch}/` already exists. Resume from existing session, or start fresh with `.runesmith/{date}-{branch}-2/?"
5. Write the active session path to `.opencode/.runesmith-active` so subsequent agents in the same OpenCode session can find it without re-determining
6. Return the session path to the calling agent

### `rs-scratchpad clear` — Clear Current Session

**What it does:** Removes the active session's scratchpad files. Does NOT remove global config files (`flaky.yml`, `security.yml`).

**Workflow:**
1. Read `.opencode/.runesmith-active` to find the current session path
2. If no active session, warn and exit
3. Show the user what will be deleted:
   > "This will delete all files in `.runesmith/{date}-{branch}/` (specs, reports, logs, cache). Global config files (flaky.yml, security.yml) will be kept. Continue?"
4. On confirmation:
   - Remove `specs/`, `reports/`, `logs/`, `cache/` subdirectories
   - Keep the session root directory (prevents git status noise)
   - Remove `.opencode/.runesmith-active`
5. On rejection: exit without changes

### `rs-scratchpad status` — Show Session Status

**What it does:** Reports the current scratchpad state.

**Output:**
```
Active session: .runesmith/2026-06-07-feat-42-auth/
  specs:    3 files (12KB)
  reports:  1 file (4KB)
  logs:     0 files
  cache:    2 files (1.2MB)
Global config:
  flaky.yml:     present (4 entries)
  security.yml:  not present
```

## Permission Requirements

The calling agent needs:
- `bash: { "git *": "allow" }` — for branch detection
- `read/write` — for `.runesmith/` and `.opencode/.runesmith-active`
- `question: allow` — for prompting the user on collisions and deletions

The skill itself does not need special permissions — it delegates the actual operations to the calling agent's existing tool access.

## How Agents Use It

The spec-writer or architect calls this skill FIRST, before any other work:

```
1. skill({ name: "rs-scratchpad" })
   → Gets session path: .runesmith/2026-06-07-feat-42-auth/
2. skill({ name: "rs-issue-to-plan" })
   → Writes spec to .runesmith/2026-06-07-feat-42-auth/specs/issue-42-auth.md
```

This ensures every agent writing to the scratchpad uses the same session path without having to re-determine it.

## Relationship to Init Hook

| Mechanism | What it creates | When |
|---|---|---|
| Plugin init hook | `.runesmith/` root directory | On plugin install/update |
| `rs-scratchpad init` skill | `.runesmith/{date}-{branch}/{specs,reports,logs,cache}/` | At session start |
| Agent on demand | Files inside session subdirectories | During session work |

The init hook creates the bucket. The scratchpad skill creates the per-session folder. Agents fill the files.

## Design Decisions

- **Single skill, three commands** rather than three separate skills. The scratchpad lifecycle is a single concern — managing the session workspace. Having `init`, `clear`, and `status` as commands within one skill keeps discovery simple.
- **User confirmation on clear.** Deleting files is destructive. The skill always asks before removing anything.
- **User confirmation on collision.** Incrementing the counter creates a new isolated session. The user decides whether to resume or start fresh.
- **Active session pointer** in `.opencode/.runesmith-active` rather than trying to derive from OpenCode's session ID. Agents don't have access to OpenCode internals, and a file is the simplest cross-agent communication mechanism.

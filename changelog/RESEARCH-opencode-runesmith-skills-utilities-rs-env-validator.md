---
title: "Environment Validator Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-14
tags:
  - opencode
  - skills
  - environment
  - dotenv
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
  - knowledge: "knowledge/tooling/opencode/skills/concepts.md"
references:
  - url: "https://www.dotenv.org/docs/"
    title: "dotenv Documentation"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-14
---

# Environment Validator Skill Design (`rs-env-validator`)

## Purpose

`rs-env-validator` is a utility skill for the `@runicengines/opencode-runesmith` plugin. It reads a project's `.env.example` file, checks the actual `.env` against it for missing required variables, validates variable format (no spaces, no quotes in values), and reports missing, extra, and malformed variables.

The skill catches environment configuration drift before it causes runtime failures — a missing environment variable is one of the most common onboarding and deployment errors.

## Skill Identity

| Property | Value |
|---|---|
| Plugin | `@runicengines/opencode-runesmith` |
| Skill name | `rs-env-validator` |
| Skill prefix | `rs-` |
| Loading model | On-demand (via `skill({ name: "rs-env-validator" })`) |
| Primary user | Developer agent (onboarding) |
| Secondary users | DevOps agent (CI checks), Architect agent (project health) |
| Trigger | Project setup, environment configuration review, CI pre-check |

## Permission Model

| Permission | Purpose |
|---|---|
| `read` | Read `.env` and `.env.example` files |
| `glob` | Find `.env` files at project root and common locations |
| `write` | Write validation report output |

The skill is **read-only** for the environment files and **write-only** for the validation report. It never modifies `.env` or `.env.example`.

## Input

The skill accepts:

1. **Project root** — directory to scan for `.env` files (default: current working directory).
2. **Custom file names** — override the default `.env` / `.env.example` file names.
3. **Configuration** (optional):
   - `required_prefix` — require all env vars to start with a prefix (e.g., `APP_`, `VITE_`).
   - `value_patterns` — regex patterns that certain variables must match (e.g., `DATABASE_URL` must be a valid URL).
   - `allow_extra` — boolean, whether to warn about extra variables in `.env` not in `.env.example` (default: true).
   - `secrets` — list of variable names that should never appear in `.env.example` with real values (e.g., `API_KEY`, `SECRET`).

## Workflow Steps

### Step 1: Locate .env files

1. Search for `.env.example` at the project root.
2. Search for `.env` at the project root.
3. If `.env.example` is not found, look for:
   - `.env.sample`
   - `env.example`
   - `config/.env.example`
   - `example.env`
4. If `.env` is not found, look for:
   - `.env.local`
   - `.env.development`
   - `.env.production`

### Step 2: Parse .env.example

Parse the `.env.example` file:

```bash
# Comments are ignored
# Variables with empty values: required (must be set in .env)
DATABASE_URL=
API_KEY=

# Variables with example values: optional (has a default)
PORT=3000
LOG_LEVEL=info

# Variables marked as optional via comment convention
# OPTIONAL: DEBUG_MODE
DEBUG_MODE=false
```

Conventions:
- Lines starting with `#` are comments.
- Empty values (`KEY=`) indicate required variables — they must be set in `.env`.
- Non-empty values (`KEY=value`) indicate optional variables that have defaults.
- Comment conventions like `# OPTIONAL:` or `# REQUIRED:` can override the above heuristic.
- Variable names must match `^[A-Z][A-Z0-9_]*$` (uppercase, underscore-separated).

### Step 3: Parse .env

Parse the actual `.env` file. Validate each variable:

| Check | Rule | Severity |
|---|---|---|
| **No leading/trailing spaces** | Variable values must not contain unquoted spaces at the start/end | Warning |
| **Name format** | Variable name must match `^[A-Z][A-Z0-9_]*$` | Error |
| **No duplicate keys** | Same key should not appear multiple times | Warning |
| **Unquoted multiline values** | Unquoted values spanning multiple lines may cause parsing ambiguity | Warning |

### Step 4: Compare and report

Compare `.env` against `.env.example`:

| Category | Description |
|---|---|
| **Missing required** | Variables in `.env.example` with empty value that are not in `.env` |
| **Missing optional** | Variables in `.env.example` with example value that are not in `.env` (low severity) |
| **Extra** | Variables in `.env` that are not in `.env.example` (if `allow_extra` is false) |
| **Malformed** | Variables with invalid format per Step 3 checks |

### Step 5: Generate validation report

```
.env Validation Report
======================
Project: my-project
Date: 2026-06-14

SUMMARY
-------
Status: ❌ FAIL (3 issues)
Total variables in .env.example: 12
Total variables in .env:        9
Missing required: 2
Missing optional: 2
Extra: 0
Malformed: 1

MISSING REQUIRED
----------------
❌ DATABASE_URL    — Required for database connection
❌ API_KEY         — Required for external API access

MISSING OPTIONAL
----------------
⚠  SENDGRID_API_KEY — Optional: Used for email sending. Default: (none)
⚠  REDIS_URL        — Optional: Used for caching. Will fall back to in-memory cache.

MALFORMED
---------
❌ MY VAR=test — Variable name contains space (line 5, violates name format check)
⚠  DATABASE_URL= postgres://localhost:5432/db — Value has leading whitespace (line 8, violates no leading/trailing spaces check)

RECOMMENDATIONS
---------------
1. Set DATABASE_URL and API_KEY before running the application.
2. Review SENDGRID_API_KEY — set if email functionality is needed.
3. Fix variable name 'MY VAR' to 'MY_VAR' in .env.
4. Remove leading whitespace from DATABASE_URL value.
```

## Output

The skill outputs:

1. **Validation report** — structured text report with summary, missing variables, extra variables, and malformed variables.
2. **Exit status** — pass (0) if no errors, fail (1) if required variables are missing or malformed.
3. **Machine-readable output** (optional) — JSON version of the report for CI integration.

## Chains With

| Skill | Condition | Step |
|---|---|---|
| `rs-discover` | If project structure is unknown | Before Step 1 |
| `rs-issue-to-plan` | If validation issues need to be filed as tasks | After report generation |

## Design Decisions

1. **.env.example as the source of truth**. The `.env.example` file defines the expected environment contract. This is the de facto standard across Node.js, Python, and Go projects. The skill reads this contract and checks `.env` against it — not the other way around.

2. **Empty values = required, filled values = optional**. This is the most common .env.example convention. Empty values signal "you must provide this." Example values signal "this has a working default but you can override it." The skill applies this heuristic unless overridden by comment annotations.

3. **No auto-fix of .env files**. The skill identifies issues but never modifies `.env` or `.env.example`. Auto-fixing environment files could introduce security issues (writing real secrets) or break working configurations. The report tells the developer exactly what to change.

4. **Format validation prevents subtle bugs**. A common deployment failure is a .env file with invisible issues: trailing spaces, malformed variable names, or duplicate keys. The format validation catches these before they cause hard-to-diagnose runtime failures.

5. **No dedicated dotenv knowledge note**. The knowledge/design/documentation/dotenv/ topic does not yet exist. This skill uses common .env conventions shared across the Node.js, Python, and Go ecosystems. The sources field references general OpenCode skill knowledge notes instead. If a dotenv knowledge note is created later, this skill's sources field should be updated to reference it.

## See Also

- [dotenv documentation](https://www.dotenv.org/docs/) — .env file conventions and usage guide
- [Discover skill](rs-discover.md) — Can identify project structure before env validation
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills) — Skill system reference

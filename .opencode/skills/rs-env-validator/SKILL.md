---
name: rs-env-validator
description: >
  Validate .env files against .env.example. Detects missing required
  variables, malformed entries, extra variables, and format violations.
  Supports quoted values, inline comments, export prefix, and variable
  interpolation warnings.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: utility
  audience: developers, devops
  trigger: manual
---

## Purpose

Validates a project's `.env` file by comparing it against the `.env.example`
template. Flags missing required variables (present in `.env.example` but
absent in `.env`), warns on missing optional variables (prefixed with `# `),
detects malformed entries (invalid names, trailing whitespace, unquoted
special characters), reports extra variables not in the example file, and
provides format-level warnings for inline comments, `export` prefix
inconsistencies, and potential variable interpolation issues.

## When to Invoke

Trigger `rs-env-validator` when:

- Setting up a new environment from an example file.
- Debugging a runtime configuration error caused by a missing or mis-typed
  environment variable.
- Auditing a project before deployment to ensure all required variables are
  defined.
- Reviewing a PR that modifies `.env.example` or `.env`.
- Detecting accidental commits of `.env` with production secrets.
- Checking `.env` formatting consistency across a monorepo or team.

Do NOT invoke when:

- The project has no `.env.example` file.
- The `.env` file contains only non-sensitive configuration that is safe to
  commit (consider renaming it to `.env.local` or similar).
- Operating in an environment where `.env` files are not used (e.g.,
  cloud-native config via environment variables or vault).

## Workflow Steps

### Step 1 — Locate files

Find `.env.example` and `.env` in the project root. If `.env.example` does
not exist, return an error and stop. If `.env` does not exist, report it as
missing and produce a report based solely on `.env.example` (all variables
marked as missing).

Files are located by relative path from the project root:

| File           | Required | Purpose                                        |
| -------------- | -------- | ---------------------------------------------- |
| `.env.example` | Yes      | Reference template defining expected variables |
| `.env`         | No       | Actual environment configuration to validate   |

### Step 2 — Parse `.env.example`

Parse `.env.example` into a structured list of variable definitions. For
each line:

1. Skip blank lines and full-line comments (lines starting with `#`).
2. Treat lines starting with `# ` followed by a variable assignment as
   **optional** variables. Example: `# DB_PORT=5432` means `DB_PORT` is
   optional, with a suggested default of `5432`.
3. Treat lines starting with `export VAR=value` as **export-prefixed**
   variables. The `export` keyword is stripped for name matching but
   recorded as a format requirement.
4. Treat all other `VAR=value` lines as **required** variables.
5. Detect multi-line values (ending with `\`). Accumulate continuation
   lines until a line without a trailing `\`.
6. For each variable, record:
   - `name` — the variable name (left of `=`).
   - `required` — boolean (true for plain `VAR=value`, false for
     `# VAR=value`).
   - `default` — the example value (right of `=`), or empty string.
   - `export` — boolean (true if the line starts with `export`).
   - `type` — inferred type: `string`, `number`, `boolean`, `path`,
     `url`, or `unknown`.

### Step 3 — Parse `.env`

Parse `.env` using the same rules as Step 2. Collect all variable
definitions with their values, plus note any syntax-level errors:

- **Invalid variable name**: name contains characters other than
  `[A-Za-z_][A-Za-z0-9_]*`.
- **Malformed assignment**: line lacks `=` (e.g., `FOOBAR` without `=`).
- **Unquoted special value**: value contains `#`, `'`, `"`, `$`, or
  whitespace without matching quotes.
- **Trailing whitespace**: trailing spaces or tabs after the value.
- **Multi-line not terminated**: file ends while a continuation line is
  still open.
- **Empty value after `=`**: e.g., `FOO=` — valid but flagged as empty.

### Step 4 — Compare and classify

Compare parsed `.env.example` against parsed `.env`. For each variable in
`.env.example`:

| Category             | Condition                                               |
| -------------------- | ------------------------------------------------------- |
| **Missing required** | Variable is `required: true` and not present in `.env`  |
| **Missing optional** | Variable is `required: false` and not present in `.env` |

For each variable in `.env`:

| Category                   | Condition                                           |
| -------------------------- | --------------------------------------------------- |
| **Extra**                  | Variable is not present in `.env.example`           |
| **Export prefix mismatch** | Variable has `export` in one file but not the other |
| **Empty value**            | Variable has value after `=` but it is empty        |

### Step 5 — Generate structured report

Output findings as labelled sections with one issue per line.

**Example output for a mixed-scenario project:**

```
MISSING REQUIRED:
  DATABASE_URL  (.env.example line 3)

MISSING OPTIONAL:
  DB_PORT  (.env.example line 7, default=5432)

MALFORMED:
  line 3: invalid variable name "MY VAR" (contains space)
  line 7: trailing whitespace after value "true "
  line 9: value contains unquoted special character (#)

EXTRA VARIABLES:
  MY_SECRET  (not in .env.example)

FORMAT NOTES:
  export prefix mismatch: NODE_ENV (export in .env, no export in .env.example)

INTERPOLATION WARNINGS:
  DATABASE_URL contains ${DB_HOST} — verify DB_HOST is defined upstream
```

If no issues exist:

```
PASS: .env matches .env.example — all required variables present, no format violations, no extra variables.
```

## Output Format

The skill returns a structured text report. Each section is prefixed with a
label in uppercase (e.g., `MISSING REQUIRED:`, `MALFORMED:`) followed by
indented issue lines. Empty sections are omitted. A `PASS` message is
returned only when every category is empty.

## Security Features

- **No secrets leaked**: The report does not echo secret values from `.env`.
  Variable values are shown only when they cause a format error (e.g.,
  trailing whitespace) and are truncated to 32 characters if sensitive.
- **Path sanitisation**: File paths in the report are relative to project
  root. Absolute paths are never emitted.

## Required Permissions

- `read` — to read `.env.example` and `.env`.
- `glob` — to locate files if they are not at the expected root path.

## See Also

- `rs-discover` — project structure scanner for initial context.
- `rs-dependency-checker` — complementary audit skill for dependency health.
- `rs-scratchpad` — scratchpad for storing validation reports.

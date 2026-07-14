---
name: kb-frontmatter-validate
description: Validate YAML frontmatter fields, types, statuses, kebab-case tags, ISO dates with calendar validity, template comments, and ADR constraint formats per section rules
---

# kb-frontmatter-validate

## When to use me

Call this skill when a file has been created or edited and you need to verify its frontmatter is correct per the section's rules. Use after scaffolding, after editing frontmatter, or as part of a review workflow. Do NOT use for files without YAML frontmatter (e.g. plain README.md stubs).

---

## Before you start

Read the target section's `AGENTS.md` and `templates/AGENTS.md` to determine:
- Which fields are required and which are optional
- The valid status lifecycle
- Field types (string, integer, array, date, etc.)

The section's `AGENTS.md` and `templates/AGENTS.md` define WHAT is valid. This skill defines HOW to check it.

## Validation rules

For every check below, report the specific violation, field name, and value found. Follow the **fail-and-explain** pattern: report all violations found, then stop.

### 1. Required fields present

A required field with an empty string or null value is still missing — do not treat `""` or `null` as present. Check that every required field (from the section's `AGENTS.md`) exists with a non-empty value.

For ADR files, check the `date` field's required status against the conditional rule in `adr/AGENTS.md`.

Ignore any extra fields not in the section's field set — they are not validation errors.

### 2. Field types

Do not assume a field is correct because it exists — verify its type matches. Check every field against its expected type from the section's `AGENTS.md` and `templates/AGENTS.md`.

### 3. Status validation

Case-sensitive: `Draft` is invalid, `draft` is valid. The status value must be one of the section's valid statuses from its `AGENTS.md` Status Lifecycle.

### 4. Tags in kebab-case

If `tags` is present, each tag must be lowercase with hyphens only — no underscores, spaces, or uppercase. Each tag must match `^[a-z0-9]+(-[a-z0-9]+)*$`. Report each invalid tag individually.

### 5. Date validation (format + calendar)

A date like `2026-31-05` matches the YYYY-MM-DD pattern but is not a real calendar date. Every date field must:
- Match `^\d{4}-\d{2}-\d{2}$` (YYYY-MM-DD)
- Be a valid calendar date (months 01–12, days valid for the given month, including leap year)

Use `date --date "$value"` or your built-in calendar logic to verify.

### 6. Template comments

Do NOT flag template comments as a validation failure — they do not affect the `valid` field. How you handle them depends on your agent's permission set:

**If `edit` is allowed**: Scan for `<!-- ... -->` blocks in the file body (below the frontmatter). If found: auto-remove them, fold blank lines, write the modified content back to the file, and record the removed blocks in `template_comments` with `action: "removed"`.

**If `edit` is denied**: Scan for `<!-- ... -->` blocks. If found: record them in `template_comments` with `action: "reported"` and add an informational entry to `violations` with `severity: "info"` and `field: "template_comment"`. The caller should delegate removal to an agent with `edit` permission (e.g., a section agent via `task`).

### 7. ADR technology constraint format

If the `technology` field is present and non-empty in an ADR, validate its format against the constraint pattern in `adr/AGENTS.md`. Report violations with the field value and expected pattern.

## Response contract

Return results as JSON:

```json
{
  "valid": true,
  "file": "ideas/my-idea/overview.md",
  "section": "ideas",
  "violations": [],
  "template_comments": []
}
```

On failure (edit mode — template comments were auto-removed):
```json
{
  "valid": false,
  "file": "ideas/my-idea/overview.md",
  "section": "ideas",
  "violations": [
    {"field": "title", "message": "Missing required field `title` in frontmatter", "severity": "error"},
    {"field": "status", "message": "Field `status` has value `final` which is not valid for section ideas", "severity": "error"}
  ],
  "template_comments": [
    {"lines": "15-18", "action": "removed"}
  ]
}
```

On success with template comments found but edit denied:
```json
{
  "valid": true,
  "file": "ideas/my-idea/overview.md",
  "section": "ideas",
  "violations": [
    {"field": "template_comment", "message": "Template comment block found at lines 15-18. Delegate to a section agent to remove.", "severity": "info"}
  ],
  "template_comments": [
    {"lines": "15-18", "action": "reported"}
  ]
}
```

## Error handling

Report violations ordered by severity: missing required fields first, then type errors, then status, then format issues. Provide specific field names and values in every error message.

Example messages:
- "Missing required field `sources` in frontmatter"
- "Tag `MyTag` is not kebab-case (expected `my-tag`)"
- "Date `2026-31-05` is not a valid calendar date (expected YYYY-MM-DD)"
- "Removed 2 template comment blocks (lines 15–18, 22–25)"


---
name: kb-status-transition
description: Validate status lifecycle transitions for Knowledge Base documents — forward-only moves, skip detection, terminal locking, section-specific lifecycles
---

# kb-status-transition

## When to use me

Call this skill when you need to change a document's status in its frontmatter and want to validate the transition is valid per the section's lifecycle. Use before editing a `status` field, during review workflows, or when auditing existing documents. Do NOT use for files without YAML frontmatter.

---

## Before you start

Read the target section's `AGENTS.md` for its lifecycle. The section's `AGENTS.md` defines WHAT lifecycles are valid. This skill defines HOW to validate transitions.

## Validation mechanics

### 1. Read current status from file

Read the file to extract its YAML frontmatter. Locate the `status` field value. Do NOT accept the current status as an argument — always derive it from the file.

If no frontmatter or no `status` field is found, report that and stop: "File `<path>` has no `status` field in frontmatter"

### 2. Identify the section

The caller provides the section name (e.g. `ideas`, `knowledge`), or derive it from the file path relative to the repo root. The section directory name is the first path component below the repo root (e.g. `knowledge/foo/overview.md` → section `knowledge`).

### 3. Look up the section's lifecycle

Read the section's `AGENTS.md` for its lifecycle. If the section does not define a lifecycle (e.g. `projects`, `tasks`), report that status transitions are not applicable and stop.

### 4. Validate the proposed transition

Given the section's lifecycle sequence and the proposed new status (provided by the caller):

**Forward moves only.** The transition must move forward along the arrow sequence. Moving backward (e.g. `accepted → exploring`) is INVALID.

**No skipping.** Each transition must go to the immediately next state. Skipping a state (e.g. `draft → accepted` in research, skipping `exploring` and `proposed`) is INVALID.

**Terminal states are locked.** Terminal states cannot transition to any other state — except to `superseded`:
- Ideas, knowledge, research, proposals: `completed` is terminal (locked except → `superseded`)
- ADR: `final` and `cancelled` are terminal (locked except → `superseded`)
- `superseded` is terminal (locked — no further transitions)

**Status values must belong to the section's lifecycle.** Using a status that is not in the section's lifecycle (e.g. `final` in ideas, `cancelled` in knowledge) is INVALID.

**Case-sensitive.** `Draft` is invalid, `draft` is valid. Compare against the exact lowercase values in the lifecycle.

### 5. Report valid or invalid

Return results as JSON following the Response contract below.

## Response contract

```json
{
  "valid": true,
  "file": "ideas/my-idea/overview.md",
  "section": "ideas",
  "current_status": "draft",
  "proposed_status": "accepted",
  "message": "Status transition `draft → accepted` is valid for ideas"
}
```

On failure:
```json
{
  "valid": false,
  "file": "ideas/my-idea/overview.md",
  "section": "ideas",
  "current_status": "draft",
  "proposed_status": "final",
  "message": "Status transition `draft → final` is invalid for ideas (valid: draft → exploring → proposed → accepted → completed / superseded)"
}
```

## Error handling

Follow the fail-and-explain pattern. Report a single clear message and stop.

### Example messages

- "Status transition `draft → final` is invalid for ideas (valid: draft → exploring → proposed → accepted → completed / superseded)"
- "Status transition `draft → accepted` is invalid for research — skipped states: exploring, proposed"
- "Status `final` is not valid for section knowledge (not in lifecycle)"
- "Status `completed` is terminal and cannot transition — except to `superseded`"
- "Case-sensitive: `Draft` is invalid, use `draft`"
- "Status transition `accepted → exploring` is invalid — cannot move backward in the lifecycle"
- "File `knowledge/foo/overview.md` has no `status` field in frontmatter"
- "Section `tasks` does not support status transitions"

## AGENTS.md boundary

This skill defines the MECHANICS of validating transitions: forward-only checking, skip detection, terminal locking, and case-sensitivity. The lifecycles themselves (which statuses exist and what order they follow per section) come from each section's `AGENTS.md`. Always defer to the section's `AGENTS.md` as the source of truth.


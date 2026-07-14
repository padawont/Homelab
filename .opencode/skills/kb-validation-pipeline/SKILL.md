---
name: kb-validation-pipeline
description: Run multi-turn validation on newly created files via kb-editor → kb-tech-lead → kb-architect, with up to 4 fix cycles per stage
---

# kb-validation-pipeline

## When to use me

Call this skill immediately after creating each new knowledge note or research file. Do NOT use for editing existing files, for non-content files (indexes, README stubs), or when you are not the file's creator.

---

## Before you start

Each file must already exist on disk before invoking this pipeline. The file should have complete content — not a skeleton or placeholder. If the file is incomplete, finish writing it first.

---

## Pipeline Overview

For each newly created file, run three stages in order. Each stage tasks a review agent, parses its JSON findings, and applies fixes before re-tasking. A stage may run up to 4 cycles (task → fix → re-task). If the stage does not pass after 4 cycles, escalate to manual review.

```
File created
  |
  +---> Stage 1: kb-editor
  |       task → parse → fix → re-task (max 4)
  |       if clean or 4 → proceed
  |
  +---> Stage 2: kb-tech-lead
  |       task → parse → fix → re-task (max 4)
  |       if clean or 4 → proceed
  |
  +---> Stage 3: kb-architect
  |       task → parse → fix → re-task (max 4)
  |       if clean or 4 → done
  |
  +---> Final: report result
```

---

## Stage 1: kb-editor

1. **Task the editor** — Invoke `kb-editor` with the file path as context. Do not pre-filter or summarize — let the editor read the file directly.
2. **Parse the response** — The editor returns JSON with an `overall` field:
   - `"clean"` — no issues. Proceed to Stage 2.
   - `"issues-found"` — findings are in the `findings` array. Proceed to fix.
3. **Apply fixes** — For each finding:
   - Use `edit` to fix the issue.
   - If the finding references a broken link, fix the path or URL.
   - If the finding references a frontmatter violation, correct the field.
   - If the finding references a formatting issue, adjust the content.
   - Do NOT fix findings you do not understand — skip them and let the next re-task catch them.
4. **Re-task** — After applying all fixes, task `kb-editor` again on the same file.
5. **Cycle limit** — Repeat steps 1-4 until either:
   - The editor returns `"clean"` (pass) → proceed to Stage 2.
   - 4 cycles have been exhausted → escalate.

### Escalation

If Stage 1 exhausts 4 cycles without passing:
- Record the file path and the last set of unfixed findings.
- Append to the escalation report (see Final Report below).
- Proceed to Stage 2 anyway — the file moves forward for technical review regardless of editor issues.

---

## Stage 2: kb-tech-lead

1. **Task the tech lead** — Invoke `kb-tech-lead` with the file path as context.
2. **Parse the response** — The tech lead returns JSON with a `status` field:
   - `"accurate"` — no issues. Proceed to Stage 3.
   - `"needs-review"` — findings are in the `findings` array. Proceed to fix.
3. **Apply fixes** — For each finding:
   - If the finding identifies a version mismatch, update the version number.
   - If the finding identifies an incorrect API or behavior description, correct it.
   - If the finding identifies a broken or outdated source URL, update or remove it.
   - Verify each fix against the authoritative source URL provided in the finding (fetch it with `webfetch` if needed).
   - Do NOT make changes you cannot verify against an authoritative source.
4. **Re-task** — After applying fixes, task `kb-tech-lead` again on the same file.
5. **Cycle limit** — Repeat until `"accurate"` or 4 cycles exhausted → escalate if needed, then proceed to Stage 3.

---

## Stage 3: kb-architect

1. **Task the architect** — Invoke `kb-architect` with the file path as context.
2. **Parse the response** — The architect returns JSON with a `status` field:
   - `"approved"` — no issues. Pipeline complete for this file.
   - `"changes-required"` — findings are in the `findings` array. Proceed to fix.
   - `"needs-discussion"` — the architect identified a cross-sectional issue requiring human input. Escalate immediately (do not retry).
3. **Apply fixes** — For each finding:
   - If the finding identifies a missing cross-reference, add the reference.
   - If the finding identifies a pipeline gap (e.g., idea has no corresponding knowledge note), note it but do not fabricate content — just flag it.
   - If the finding identifies a structural issue, adjust the content accordingly.
4. **Re-task** — After applying fixes, task `kb-architect` again.
5. **Cycle limit** — Repeat until `"approved"` or `"needs-discussion"` or 4 cycles exhausted.

---

## Final Report

After all files have been processed, produce a summary:

```json
{
  "pipeline_complete": true,
  "files_processed": 4,
  "passed_all": 3,
  "escalated": [
    {
      "file": "knowledge/design/documentation/diataxis/overview.md",
      "stage": 1,
      "last_findings": ["Missing source URL for section on quality model"]
    }
  ],
  "needs_discussion": [
    {
      "file": "research/opencode-runesmith/...",
      "architect_finding": "New skill overlaps with existing rs-discover"
    }
  ]
}
```

## Gotchas

- Do not skip stages. Every file goes through all three stages regardless of earlier results.
- Do not re-task the same agent without applying at least one fix between invocations — infinite loops waste turns.
- If a finding is unclear or you cannot determine the correct fix, note it in the escalation report and move on. Do not stall the pipeline on a single ambiguous finding.
- Each file is independent. Files that pass early do not wait for files that are still cycling.


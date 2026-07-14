---
title: "Verification: Manual Smoke Test Checklist"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - agents
  - testing
  - verification
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-configuration"
  - knowledge: "knowledge/tooling/opencode/skills/skill-configuration"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-05-31
---

# Verification: Manual Smoke Test Checklist

## 1. Verification Approach

Manual smoke tests validate that each agent and skill works as expected. The fail-and-explain error handling pattern means all validation errors must be explicitly reported, not silently swallowed. Each test should be run against the corresponding agent after implementation.

## 2. Scaffold Tests

For each section agent, invoke it and ask to scaffold a new topic. Verify:

- Correct folder naming: kebab-case with proper nesting (`<cat>/<subcat>/<topic>/` for ideas and knowledge, flat `<topic>/` for research and proposals, `<NNNN>-<topic>/` for ADR).
- Required template files present per section rules (changelog.md for ideas, index.qmd for proposals, etc.).
- Frontmatter populated with correct fields, status set to `draft`, dates in YYYY-MM-DD format.
- No template comments (`<!-- ... -->`) remain in any scaffolded file.

## 3. Validation Tests

Ask each agent to validate a file using `kb-frontmatter-validate`. Verify:

- A valid file passes with no errors.
- Missing required fields produce specific error messages (e.g., "Missing required field `sources` in frontmatter").
- Invalid status values are rejected per the section's lifecycle.
- Non-kebab-case tags are flagged.
- Invalid or out-of-range dates are reported.

## 4. Cross-Link Tests

Test `kb-cross-link-check` by creating files with known valid and broken cross-references. Verify:

- Valid paths pass without error.
- Broken paths produce specific error messages with the missing path.
- Knowledge `sources` (for research) are checked as paths on disk.
- URL `sources` (for knowledge) are checked for well-formedness.
- ADR `replaces` and `replaced-by` paths resolve to existing numbered folders.

## 5. Status Transition Tests

Test `kb-status-transition` across all sections. Verify:

- Valid forward moves pass (e.g., `draft → exploring` in ideas).
- Skipped-state transitions are rejected (e.g., `draft → accepted` in research is invalid).
- Terminal states reject further transitions (`completed`, `superseded`, `final`/`cancelled` for ADR).
- Cross-section invalid statuses are rejected (e.g., `final` used outside ADR).

## 6. ADR Numbering

Scaffold ADRs sequentially and verify:

- Folder created with zero-padded `NNNN-` prefix (`0001-`, `0002-`).
- Number auto-increments from highest existing folder.
- Duplicate numbering is prevented.
- `replaces` and `replaced-by` frontmatter fields reference valid numbered paths.
## 7. @mention Tests

- Each agent is invocable via @mention
- Workflow runs and returns output
- Errors reported inline

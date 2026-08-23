---
name: rs-issue-to-plan
description: >
  Convert a GitHub issue into a structured implementation plan with
  phases, acceptance criteria, and test strategy. Follows ADR 0002
  conventions for branch naming, commits, and PR workflow.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: planning
  audience: developers
  trigger: manual+chained
---

## Purpose

Takes a GitHub issue (by URL, issue number, or raw description) and produces a phased implementation plan. The output is a `spec.md` document with:

- A summary of the work
- 3–5 implementation phases, each independently reviewable and mergeable
- Acceptance criteria per phase (testable, measurable conditions)
- A test strategy covering unit, integration, and e2e
- ADR 0002 conventions for branch naming and commits

## Input

Accept any of the following formats:

| Format       | Example                                   | How to resolve                                           |
| ------------ | ----------------------------------------- | -------------------------------------------------------- |
| Full URL     | `https://github.com/owner/repo/issues/42` | Fetch via `gh issue view 42 -R owner/repo` or `webfetch` |
| Issue number | `#42` or `42`                             | Resolve via `gh issue view 42` (repo inferred from CWD)  |
| Raw text     | A multi-line description                  | Treat as the issue body directly — no fetch needed       |

When given a URL or number, always fetch the live issue from GitHub first. The issue may have updated comments, labels, or linked PRs since it was created.

## Step-by-Step Workflow

### 1. Initialize session scratchpad

Chain `rs-scratchpad init` via `skill({ name: "rs-scratchpad" })` to create or validate the active session scratchpad directory. Capture the returned session path as `{session}` (e.g., `.runesmith/2026-07-19-feat_user-auth/`). All subsequent file output paths use this session directory.

If `rs-scratchpad` is unavailable, fall back to creating the session directory manually using the same convention: `.runesmith/{date}-{sanitized-branch}/` with subdirectories `specs/`, `reports/`, `logs/`, `cache/`, `pipeline/`, `stages/`, `prs/`.

### 2. Fetch and parse the issue

Use `gh issue view <number> --json title,body,labels,comments,state,milestone,assignees` to extract the full issue context. If `gh` is unavailable, fall back to `webfetch` on the issue URL and parse the markdown body manually.

Extract the following:

- **Title** — used as the spec title
- **Description** — the canonical requirements source
- **Labels** — used to determine issue type (bug, feature, refactor, chore per ADR 0002)
- **Comments** — may contain additional requirements, constraints, or decisions
- **Linked PRs/issues** — cross-reference any related work

### 3. Classify the issue type

Map the issue to a Conventional Commit type based on its labels and content:

| Label           | Type       | Meaning                                |
| --------------- | ---------- | -------------------------------------- |
| `bug`           | `fix`      | Defect correction                      |
| `enhancement`   | `feat`     | New feature                            |
| `chore`         | `chore`    | Maintenance, tooling, deps             |
| `documentation` | `docs`     | Docs-only changes                      |
| `refactor`      | `refactor` | Restructuring without behaviour change |

This type feeds into the ADR 0002 branch naming convention: `{type}/{issue-number}-{kebab-description}`.

### 4. Scan the codebase for context

Invoke `skill({ name: "rs-discover" })` to identify:

- Entry points — where the change starts
- Relevant modules — files that will likely need modification
- Existing tests — test directories, test runners, coverage thresholds
- Configuration files — dependency manifests, CI configs, linter rules

If `rs-discover` is unavailable or the issue is self-contained (e.g., a dependency bump), skip this step.

### 5. Decompose into implementation phases

Break the work into 3–5 phases. Each phase must be:

- **Independently reviewable** — a reviewer can evaluate it without context from later phases
- **Mergeable** — the codebase compiles and tests pass after each phase
- **Scoped** — one phase = one logical unit of change

Phase naming convention: "Phase N: Short Imperative Description"

Typical phase structure for a feature:

| Phase | Content                      |
| ----- | ---------------------------- |
| 1     | Models and data layer        |
| 2     | Validation and serialization |
| 3     | Endpoint / handler wiring    |
| 4     | Tests (unit + integration)   |

For bugs, a typical structure:

| Phase | Content                             |
| ----- | ----------------------------------- |
| 1     | Reproduction — write a failing test |
| 2     | Fix the root cause                  |
| 3     | Regression tests                    |

### 6. For each phase, document

```
### Phase N: {Description}

**Requirements:**
- What must be true for this phase to be done
- Written as conditions, not tasks

**Files to Change:**
- Exact file paths relative to repo root
- Use glob patterns where multiple files are affected

**Risks:**
- What could go wrong in this phase
- Dependencies on other phases or external changes

**Acceptance Criteria:**
- [ ] Testable, measurable conditions
- [ ] Each criterion verifiable by automation or manual check
- [ ] Prefer "all existing tests pass" over "works correctly"
```

### 7. Define the test strategy

Cover three levels of testing:

| Level       | Purpose                     | Example                        |
| ----------- | --------------------------- | ------------------------------ |
| Unit        | Isolated module correctness | Test a validator function      |
| Integration | Component interaction       | Test database write + read     |
| End-to-end  | Full workflow               | Test API endpoint with real DB |

Include the exact command to run tests:

```bash
pytest tests/ -x -v --cov=app
```

### 8. Output the spec document

Write to `{session}/specs/{issue-number}-{kebab-title}.md` using this template:

```markdown
---
spec_of: { issue-url }
author: { agent-name }
created: { iso-date }
issue_type: { fix|feat|chore|docs|refactor }
phases: { count }
---

# Spec: {Issue Title}

**Issue**: #{number} — {url}
**Author**: {who created this spec}
**Created**: {date}

## Summary

{2–3 sentences describing the implementation approach}

## Implementation Phases

...

## Test Strategy

{description of what gets tested at what level}

**Command**: `pytest tests/ -x -v --cov=app`
```

### Dry-Run Mode

The agent can pass `--dry-run` flag to print the spec body to stdout without writing to the session directory. This allows review before file creation. In dry-run mode, the output path is reported but no file is written.

### Idempotency Note

Within a single session (same `{session}` path from rs-scratchpad), re-running this skill with the same issue produces the same output at the same path — the write is an overwrite, not an append. The session directory is versioned by date and branch via rs-scratchpad; across different sessions, the output is intentionally isolated.

## ADR 0002 Compliance

When the spec is consumed by a developer or implementation agent:

- **Branch**: `{type}/{issue-number}-{kebab-description}` — e.g., `feat/42-user-registration`
- **Commit messages**: Conventional Commits format with issue reference — e.g., `feat(api): add user registration endpoint (#42)`
- **PR body**: Include `Closes #{issue-number}` as the final line
- **Labels**: Carry over the issue's type labels to the PR

## Required Permissions

The calling agent must have these tools available:

| Tool     | Required | Scope                 | Purpose                                  |
| -------- | -------- | --------------------- | ---------------------------------------- |
| bash     | Yes      | gh * only             | Run `gh issue view` to fetch issue data  |
| read     | Yes      | All files             | Read codebase files for context          |
| edit     | Yes      | .runesmith/ directory | Write spec file                          |
| glob     | Yes      | Source tree           | Discover relevant files by pattern       |
| grep     | Yes      | Source tree           | Search for imports, references, patterns |
| webfetch | No       | Fallback              | Fetch issue when `gh` is unavailable     |
| skill    | Yes      | rs-* only             | Load chained skills                      |

This skill does not delegate tasks to external agents via the task() tool; all work is performed by the calling agent using its own tools.

## Chained Skills

The agent that loads this skill may invoke the following skills during execution:

| Skill            | When to Chain                   | Purpose                                   |
| ---------------- | ------------------------------- | ----------------------------------------- |
| `rs-scratchpad`  | Step 1 — session initialization | Initialize session scratchpad, provide `{session}` path  |
| `rs-discover`    | Step 3 — codebase scanning      | Identify modules, tests, entry points     |
| `rs-consult`  | When domain expertise is needed | Answer questions about technology choices |

## See Also

- [ADR 0002: GitHub Etiquettes](/adr/0002-github-etiquettes/overview.md)
- [rs-discover skill](./rs-discover/SKILL.md)
- [rs-consult skill](./rs-consult/SKILL.md)
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills)

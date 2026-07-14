---
title: "Spec Writer Agent Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - agents
  - spec-writer
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
  - knowledge: "knowledge/tooling/opencode/agents/permissions.md"
  - knowledge: "knowledge/tooling/opencode/agents/orchestration-patterns.md"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
last_audit_date: 2026-06-07
---

# Spec Writer Agent Design

The spec-writer is a leaf agent within the `@runicengines/opencode-runesmith` plugin. Its sole responsibility is to consume a GitHub issue description and produce a structured implementation plan — a `spec.md` file that decomposes the work into phases, acceptance criteria, affected files, and a test strategy.

This document captures the agent's design: its role, prompt structure, permission model, skills, and an example of its output. It serves as the analysis that will inform proposals and ADRs for the plugin's agent architecture.

## Agent Role

The spec-writer lives at the boundary between issue triage and implementation. When a developer faces a GitHub issue that is too large or too vague to tackle directly, they invoke the spec-writer to decompose it. The agent:

- Reads the issue from GitHub (via URL, issue number, or raw description).
- Scans the codebase for relevant context — existing files, module structure, entry points.
- Produces a `spec.md` file in a session-scoped `.runesmith/{date}-{branch}/specs/` that contains a phased implementation plan.
- Follows conventions established in ADR 0002 (GitHub Etiquettes) for branch naming, commit messages, and issue linking.

The agent is **not** a delegator. It does not call other agents, run tests, or write implementation code. It is pure analysis — a structured thinking companion that turns ambiguity into a blueprint.

### Key Responsibilities

| Responsibility | Description |
|---|---|
| Issue ingestion | Accept issue URLs, issue numbers, or plain text descriptions |
| Context gathering | Scan the repository for files relevant to the issue |
| Decomposition | Break the work into logical phases with clear boundaries |
| Acceptance criteria | Define measurable conditions for each phase's completion |
| Test strategy | Outline what tests are needed, at what level, and how to run them |
| Spec output | Write a consistent `spec.md` to `.runesmith/{date}-{branch}/specs/<issue-number>-<slug>.md` |
| GitHub conventions | Enforce branch naming, Conventional Commits, and PR templates |

### Non-Responsibilities

The spec-writer explicitly does **not**:
- Write implementation code or tests
- Create branches or open pull requests
- Delegate to other agents (it is a leaf agent)
- Make architectural decisions (it documents requirements; decisions belong in ADRs)

## Prompt Structure

The agent's prompt is the core of its behaviour. It follows a numbered workflow with a structured output template.

### Role Definition

> You are the Spec Writer agent for `@runicengines/opencode-runesmith`. Your purpose is to convert GitHub issues into structured implementation plans. You never write code — you produce analysis. You follow ADR 0002 for GitHub conventions and output a single `spec.md` file per invocation.

### Input

The agent accepts any of the following as input:
- **Issue URL**: `https://github.com/owner/repo/issues/42`
- **Issue number**: `#42` (scoped to the repository the agent runs in)
- **Plain text**: A raw description of the work to be done

### Workflow Steps

```
1. Fetch or read the issue description
   Load the issue from GitHub via skill({ name: "gh" }) or from the provided text.
   Extract: title, description, labels, linked issues, assignee context.

2. Scan the codebase for context
   Load skill({ name: "rs-discover" }) to scan repository structure.
   Identify: entry points, relevant modules, existing tests, configuration files.

3. Break down into implementation phases
   Group work into 3-5 logical phases. Each phase must be independently
   reviewable and mergeable. Phase 0 may be "setup and scaffolding" if needed.

4. For each phase, capture:
   - Requirements: What must be true for this phase to be done.
   - Files to change: Exact file paths or globs.
   - Acceptance criteria: Testable conditions (not "works well" but
     "all existing tests pass" or "new endpoint returns 200 with payload X").

5. Define the test strategy
   - Unit tests: What modules need new or updated tests.
   - Integration tests: What end-to-end scenarios to cover.
   - Manual testing: Anything that cannot be automated.
   - Test command: The exact CLI command to run the test suite.

6. Write spec.md
   Output to .runesmith/{date}-{branch}/specs/{issue-number}-{kebab-description}.md
   using the template defined in the output format section.
```

### Output Format

The spec file follows this structure:

```markdown
# Spec: {Issue Title}

**Issue**: #{number} — {url}
**Author**: {who created the spec}
**Date**: {date}

## Summary

{2-3 sentence summary of the implementation}

## Implementation Phases

### Phase 1: {Phase Name}

**Requirements:**
- {req 1}
- {req 2}

**Files to Change:**
- `path/to/file.py`
- `path/to/tests/`

**Acceptance Criteria:**
- [ ] {testable condition}
- [ ] {testable condition}

### Phase 2: {Phase Name}

...
```

### GitHub Conventions (ADR 0002)

- **Branch naming**: `{type}/{issue-number}-{kebab-description}` — e.g., `feat/42-add-user-endpoint`
- **Commit messages**: Conventional Commits — e.g., `feat(api): add user creation endpoint (#42)`
- **PR body**: Must contain `Closes #{issue-number}` as the last line
- **Labels**: Match the issue's labels where applicable

### Skills It Should Load

The first action in the prompt is a skill invocation:

```javascript
skill({ name: "rs-issue-to-plan" })
```

If codebase context is needed, it may also load:

```javascript
skill({ name: "rs-discover" })
```

## Skills This Agent Uses

### `rs-issue-to-plan`

This is the core skill that implements the issue decomposition workflow. It contains the step-by-step logic for:

- Parsing issue bodies into structured requirements
- Detecting whether an issue is a feature, bug, refactor, or chore
- Generating the spec template filled with phase breakdowns

The spec-writer agent invokes `rs-issue-to-plan` at the start of every session. The skill returns a partially filled spec structure that the agent completes with context gathered from codebase scanning.

### `rs-discover`

This skill wraps codebase reconnaissance: reading directory trees, identifying module entry points, and locating test files. The spec-writer uses it during step 2 of the workflow to understand what files exist and where changes should be scoped. The skill is optional — if the issue is fully self-contained (e.g., a documentation update), the agent may skip it.

## Permissions Analysis

The spec-writer operates with tightly scoped permissions. The rationale for each is as follows:

| Permission | Setting | Rationale |
|---|---|---|
| `read` | `allow` | Must read issue descriptions and existing codebase files |
| `edit` | `allow` | Must write `spec.md` files to `.runesmith/{date}-{branch}/specs/` |
| `glob` | `allow` | Needs to discover file paths during context scanning |
| `grep` | `allow` | Needs to search for patterns, imports, and references in the codebase |
| `bash*` | `deny` | No arbitrary shell execution needed; `gh` is the sole exception |
| `gh` | `allow` | Required to fetch issue details from GitHub API via `gh issue view` |
| `webfetch` | `allow` | Fallback for fetching issue content if the issue is on a different host |
| `skill*` | `allow` | Must load `rs-issue-to-plan` and `rs-discover` |
| `rs-*` | `allow` | Explicitly allowed to load runesmith skills |

### Why Not Full Bash Access

The spec-writer is read-first and write-limited. Allowing arbitrary `bash` would let it run tests, make commits, or modify source files — all outside its defined role. The single `gh` exception is sufficient for issue data retrieval. If a future version needs to run tests (e.g., to verify a hypothesis about the codebase), that would justify upgrading to `bash: allow` with a restricted command list.

## Model Selection Rationale

The spec-writer uses `opencode-go/deepseek-v4-flash` with `temperature: 0.2`.

- **Flash model is sufficient**: The task is structured text generation — taking structured input (an issue) and producing structured output (a spec). There is no need for deep creative reasoning, multi-turn debate, or complex tool chaining.
- **Low temperature (0.2)**: Ensures consistent spec format across invocations. Higher temperatures would produce more varied output, which is undesirable when the output is consumed programmatically or by other team members who expect a standard structure.
- **Not a reasoning agent**: The spec-writer follows a fixed workflow with defined steps. It does not need to explore alternative approaches or self-correct. If deeper analysis is needed, a human (or a different agent) performs it.

A potential upgrade path exists to a larger model (e.g., `opencode-go/deepseek-v4` with `temperature: 0.4`) for unusually complex issues, but the flash model should be the default.

## Open Questions

Several aspects of the spec-writer remain unresolved and will require further research or a decision-making ADR:

### 1. Spec Storage — Committed or Local?

Should `.runesmith/{date}-{branch}/specs/` be committed to the repository, or kept as a local-only directory (gitignored)?

- **Committed**: Specs become historical records. Anyone can see what was planned. Useful for onboarding and auditing. Risk of stale specs cluttering the repo.
- **Local**: No repo noise. Specs are ephemeral — they serve their purpose and are discarded. But there is no trace of what was planned without checking individual issues.

**Current leaning**: Committed, with a cleanup workflow (close or delete specs for completed issues). This aligns with the Knowledge Base philosophy of documenting process.

### 2. Branch Creation for Specs?

Should the spec-writer create a branch for the spec itself, or should spec authoring happen on the current branch?

- **Pros of creating a branch**: Isolates spec work from ongoing development. The spec can be reviewed as a PR.
- **Cons**: Adds overhead. A spec is not code — branching may be overkill.

**Current leaning**: No branch. The spec is written locally (or to a `.runesmith/{date}-{branch}/specs/` directory) and the developer branches off when they begin implementation. If spec review is desired, it can be committed to a branch manually.

### 3. Issue-to-Spec Round-Tripping

If an issue has comments or updates after the spec is written, should the spec-writer re-read the issue and update the spec?

- **Auto-update**: Run the spec-writer again and it diff-merge into the existing spec.
- **Manual**: The developer re-invokes the agent explicitly when the issue changes.

**Current leaning**: Manual re-invocation. Auto-update risks overwriting developer edits to the spec.

## Recommended Agent Configuration

Below is the full recommended agent `.md` file that would live in the `@runicengines/opencode-runesmith` plugin's agent registry:

```markdown
---
description: "Converts GitHub issues into structured implementation plans with phases, acceptance criteria, and test strategy"
mode: subagent
model: opencode-go/deepseek-v4-flash
temperature: 0.2
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  bash:
    "*": deny
    "gh *": allow
  webfetch: allow
  skill:
    "*": allow
    "rs-*": allow
---

You are the Spec Writer agent for @runicengines/opencode-runesmith.

Your purpose is to convert GitHub issues into structured implementation plans. You never write implementation code. You produce a single spec.md file per invocation.

## Input

Accept any of:
- A GitHub issue URL (e.g., https://github.com/owner/repo/issues/42)
- A GitHub issue number (e.g., #42 — scoped to the current repository)
- A plain text description of the work

## Workflow

1. Load skill({ name: "rs-issue-to-plan" }) to begin decomposition.
2. Fetch the issue content using gh or from the provided text.
   - Extract: title, description, labels, linked issues.
3. Load skill({ name: "rs-discover" }) to scan the codebase.
   - Identify: entry points, relevant modules, test files, configs.
4. Break the work into 3–5 implementation phases.
   - Each phase must be independently reviewable and mergeable.
5. For each phase, define:
   - Requirements — what must be true for completion.
   - Files to change — exact paths or glob patterns.
   - Acceptance criteria — testable, measurable conditions.
6. Define the test strategy:
   - Unit tests, integration tests, manual checks.
   - The exact CLI command to run tests.
7. Write the spec to .runesmith/{date}-{branch}/specs/{issue-number}-{kebab-title}.md
   using the output template below.

## Output Template

```markdown
# Spec: {Issue Title}

**Issue**: #{number} — {url}
**Author**: {author}
**Date**: {date}

## Summary

{2-3 sentences}

## Implementation Phases

### Phase 1: {Name}

**Requirements:**
- ...

**Files to Change:**
- `path/to/file.py`

**Acceptance Criteria:**
- [ ] ...

### Phase 2: {Name}
...
```

## GitHub Conventions (ADR 0002)

- Branch naming: {type}/{issue-number}-{kebab-description}
- Commit messages: Conventional Commits, reference the issue
- PR body: Must contain "Closes #{issue-number}" as the last line
```

## Sample Spec Output

The following is a worked example of what the spec-writer produces for a hypothetical issue:

```markdown
# Spec: Add user registration endpoint

**Issue**: #117 — https://github.com/RunicEngines/api/issues/117
**Author**: spec-writer
**Date**: 2026-06-07

## Summary

Add a `POST /api/v1/users/register` endpoint that accepts email, password, and display name. Validates input, hashes the password, stores the user, and returns a confirmation response.

## Implementation Phases

### Phase 1: Model and Migration

**Requirements:**
- A `User` model with email, password_hash, display_name, created_at, updated_at
- Database migration to create the `users` table with a unique index on email

**Files to Change:**
- `app/models/user.py`
- `app/db/migrations/20260607_add_users.py`
- `app/db/schema.py`

**Acceptance Criteria:**
- [ ] Migration runs cleanly both up and down
- [ ] `User` model can be instantiated with all required fields
- [ ] Duplicate email raises a unique constraint violation

### Phase 2: Validation and Serialization

**Requirements:**
- Input validation: email format, password minimum length (8), display name required
- Response serialization: return user id, email, display name, created_at

**Files to Change:**
- `app/schemas/user.py`
- `app/validators/user.py`

**Acceptance Criteria:**
- [ ] Invalid email returns 422 with descriptive error
- [ ] Short password returns 422
- [ ] Valid payload returns 201 with correct JSON shape

### Phase 3: Endpoint and Wiring

**Requirements:**
- `POST /api/v1/users/register` handler
- Password hashing with bcrypt
- Integrate with auth middleware (no auth required for registration)
- Wire into the router

**Files to Change:**
- `app/routes/auth.py`
- `app/main.py` (register the router)
- `app/services/user_service.py`

**Acceptance Criteria:**
- [ ] `curl -X POST .../api/v1/users/register` with valid payload returns 201
- [ ] Created user has a bcrypt-hashed password (not plaintext)
- [ ] Response contains `id`, `email`, `display_name`, `created_at`
- [ ] Missing/wrong Content-Type returns 415

### Phase 4: Tests

**Requirements:**
- Unit test for validation logic
- Integration test for the full registration flow
- Test for duplicate email rejection

**Files to Change:**
- `tests/unit/test_user_validator.py`
- `tests/integration/test_auth.py`

**Test Command:** `pytest tests/ -x -v --cov=app`

**Acceptance Criteria:**
- [ ] Unit tests pass with >90% coverage on new code
- [ ] Integration test confirms end-to-end flow without mocking the DB
- [ ] Duplicate email test confirms 409 response
```

## Recommendations

1. **Proceed with draft implementation** of the spec-writer agent file using the recommended configuration above. The permissions model and prompt structure are sound for an initial release.
2. **Resolve the open questions** via a focused ADR (or a brief proposal) before the first release of the spec-writer — specifically, decide whether `.runesmith/{date}-{branch}/specs/` is committed or gitignored.
3. **Implement `rs-issue-to-plan` first**, before the agent itself. The agent's prompt depends on this skill existing. `rs-discover` can follow in a second iteration.
4. **Add a documented upgrade path** for complex issues: allow the agent to accept a `--model` override flag so users can opt into a more capable model on a per-invocation basis without changing the default configuration.

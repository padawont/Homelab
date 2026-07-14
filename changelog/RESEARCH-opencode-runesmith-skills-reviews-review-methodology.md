---
title: "Review Methodology Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - skills
  - review
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
  - knowledge: "knowledge/tooling/opencode/skills/workflow-patterns.md"
references:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Review Methodology Skill Design

> **Status:** Draft — research on the `rs-review-methodology` skill for `@runicengines/opencode-runesmith`.
> **Audience:** Developers building the reviewer agent skill set.

## Skill Purpose

`rs-review-methodology` is the core procedural skill in the `@runicengines/opencode-runesmith` plugin's review suite. It defines the structured review process that the Reviewer agent follows for every code review. Unlike domain-specific skills that teach *what* to look for, this skill teaches *how* to conduct the review — the sequence of checks, the output format, and the quality bar.

The skill is invoked by the Reviewer agent at the start of every review session. It is the first skill loaded in the Reviewer's boot sequence:

```
rs-review-methodology (process) → rs-review-severity (classification) → rs-review-security (patterns)
```

It ensures every review is consistent, auditable, and follows ADR 0002 §5 requirements regardless of which developer or repository is being reviewed.

**Trigger:** The Reviewer agent detects an incoming PR diff or commit range and loads `rs-review-methodology` to determine how to proceed.

**Input:** A PR number or commit SHA identifying the diff to review.

**Output:** A structured YAML review report with per-category findings, severity classifications, and a merge verdict.

## ADR 0002 §5 Compliance

The skill is the enforcement mechanism for ADR 0002 §5 (Code Review). Every review produced through this methodology must satisfy the following requirements:

| ADR 0002 §5 Requirement | Skill Enforcement | Verification Point |
|---|---|---|
| At least 1 approving review before merge | The review report's `verdict` field (APPROVED / CHANGES_REQUESTED / DENIED) gates merge readiness. The skill produces a deterministic recommendation, but requires manual or CI-level approval recording for the final gate. | Review output section — `verdict` field |
| Reviewers should respond within 1 business day | The skill timestamps the review with `duration` and `timestamp` fields. If a review is requested and not delivered within the window, a notification is generated. Responsibility for enforcement lives in the orchestrating agent or CI bridge. | Metadata — `requested_at` and `completed_at` comparison |
| Reviewers check correctness | Step 1 of the ordered checklist (see below). | Checklist item #1 |
| Reviewers check conventions (branch naming, commits per ADR 0002) | Step 2 of the ordered checklist. Validates branch pattern (`{type}/{issue-number}-{kebab-description}`) and Conventional Commits format. | Checklist item #2 |
| Reviewers check test coverage | Step 3 of the ordered checklist. The Reviewer inspects test files for coverage of the changed code paths. | Checklist item #3 |
| Reviewers check documentation | Step 4 of the ordered checklist. Flags missing or incomplete docs for new/modified APIs. | Checklist item #4 |
| Reviewers check for secrets | Step 5 of the ordered checklist. Scans for credential patterns, tokens, keys, and forbidden file types. | Checklist item #5 |
| Reviewers check for unrelated changes | Step 6 of the ordered checklist. Scope-creep detection via diff entropy analysis. | Checklist item #6 |
| Authors must resolve or acknowledge every review thread | The skill records all findings in a machine-parseable YAML report. Human reviewers or CI must verify thread resolution before merging. The skill does not auto-resolve threads. | Report section — `findings[*].thread_id` |

## Review Checklist (Ordered)

The checklist is the body of the skill's SKILL.md. It must be executed in order — earlier checks may short-circuit later ones (e.g., a blocker credential leak halts further review and escalates immediately).

### 1. Correctness

Does the code do what it claims? This is the most important check and comes first.

- **Logic errors**: Off-by-one, null pointer dereferences, race conditions, incorrect state mutations.
- **API usage**: Wrong function signatures, incorrect parameter ordering, misuse of framework abstractions.
- **Error handling**: Missing try/catch blocks, silent error swallowing, incorrect error propagation.
- **Type safety**: Type mismatches, implicit coercion that could mask bugs, missing type guards.
- **Edge cases**: Empty collections, zero values, boundary conditions, timeout scenarios.

A correctness failure at this stage may short-circuit the remaining checks if the code is fundamentally broken.

### 2. Conventions

Follows ADR 0002 conventions and any repository-level `AGENTS.md` or `CONTRIBUTING.md` rules.

- **Branch naming**: Pattern check against `{type}/{issue-number}-{kebab-description}`.
- **Commit messages**: Each commit parsed against Conventional Commits: `<type>(<scope>): <description>`.
- **Single concern**: Each commit addresses exactly one concern — no "and" commits.
- **Repository conventions**: PEP 8, import ordering, naming styles, file structure rules.
- **Diff size**: Unreasonable diffs flagged as a scoping concern (handled in checklist item #6, but noted here for context).

### 3. Test Coverage

Does the diff include tests, and do they cover the changed behavior?

- **Existence check**: Are test files present for the modified code?
- **Behavior coverage**: Do tests validate the changed behavior, not just that the code runs without error?
- **Edge case coverage**: Are error paths, boundary conditions, and invalid inputs tested?
- **Test quality**: Are test names descriptive? Do they follow project naming patterns? Are they free from logic errors themselves?
- **Over-testing**: Tests that test implementation details rather than behaviour — these break during refactoring and provide false confidence.

The Reviewer does not execute tests; it inspects test definitions for quality and coverage gaps.

### 4. Documentation

Is the documentation updated to match the code change?

- **Public APIs**: New or modified functions/classes must have docstrings. Missing `@param`, `@return`, `@raise` tags are flagged.
- **Inline comments**: Comments explain WHY, not WHAT. Redundant comments or missing rationale are flagged.
- **README / setup docs**: If the change affects configuration, dependencies, or setup steps, the relevant docs must be updated.
- **Breaking changes**: Breaking changes must be documented explicitly, with migration guidance if applicable.
- **Changelog**: If the project maintains a changelog, the change should be reflected.

### 5. Secrets Detection

Any credentials, tokens, keys, or PII exposed in the diff? This check has the highest escalation path.

- **Credential patterns**: Regex matches for `-----BEGIN`, `sk_live_`, `pk_live_`, `AKIA`, `SECRET`, `password =`, `api_key =`.
- **Forbidden files**: `.env`, `.env.local`, `.env.production`, `credentials.json`, `*.pem` added to version control.
- **Embedded URLs**: Hardcoded URLs containing `user:pass@host` patterns.
- **Test credentials**: Integration test fixtures that look like real secrets (e.g., live API keys in test configs).
- **Commit history**: Previous commits that may have introduced secrets (scanned via `git log -p` for retroactive leaks).

A single blocker finding at this stage halts the review and produces a DENIED verdict.

### 6. Scope Creep

Are there changes in the diff that do not belong to the PR's stated purpose?

- **Unrelated files**: Changes to files outside the PR's claimed scope.
- **Refactoring disguised as fixes**: Cleanup or restructuring that expands the change surface unnecessarily.
- **Formatting-only changes**: Whitespace, lint, or formatting changes mixed with logic changes (these should be separate PRs).
- **Dependency changes**: New or updated dependencies unrelated to the change.

Scope creep findings are typically minor/major severity — they do not block merge on their own unless they introduce risk (e.g., a new dependency without review).

### 7. Security

Known vulnerabilities introduced? This check comes last because it requires the full diff context after all other categories have been assessed.

- **Injection vectors**: SQL injection, command injection, path traversal, XSS vectors.
- **Insecure deserialization**: `pickle.loads`, `eval`, `exec`, `yaml.load` (without `Loader`), `JSON.parse` with reviver functions.
- **Authorization gaps**: Endpoints or operations missing authentication/authorization checks.
- **Dependency vulnerabilities**: New dependencies with known CVEs (requires a reference database or CVE lookup).
- **Principle of least privilege**: Overly broad permissions, file writes to sensitive locations, network access where not needed.

Security findings may reference the `rs-review-security` skill for pattern-specific details.

## Skill Interface — SKILL.md Structure

The `rs-review-methodology` skill's SKILL.md should define:

### Frontmatter

```yaml
name: rs-review-methodology
description: "Guides the reviewer through a structured code review process: correctness, conventions, test coverage, documentation, secrets, scope creep, and security. Produces a structured YAML review report."
permission:
  read: allow
  glob: allow
  grep: allow
```

`edit` and `bash` permissions are **not** declared — this is a procedural skill that provides instructions, not execution. The parent agent (Reviewer) supplies the execution permissions.

### Input Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `pr` | integer | conditional | PR number for the review target |
| `sha` | string | conditional | Commit SHA for the review target |
| `repository` | string | no | Repository full name (e.g., `runicengines/scheduler`) |
| `review_type` | string | no | One of `full`, `quick`, `security` (default: `full`) |

One of `pr` or `sha` is required.

### Review Output Format

The skill's output is a structured YAML report:

```yaml
review:
  pr: 42
  sha: a1b2c3d
  repository: runicengines/scheduler
  review_type: full
  timestamp: "2026-06-07T14:30:00Z"
  duration: 2.3s
  summary:
    total_findings: 5
    blocker: 0
    critical: 1
    major: 1
    minor: 2
    nitpick: 1
  verdict: CHANGES_REQUESTED
  findings:
    - category: security
      severity: critical
      file: src/api/users.py
      line: 47
      description: "SQL injection vector via f-string interpolation"
      recommendation: "Use parameterized queries instead of f-string"
  categories:
    correctness: PASS
    conventions: PASS
    test_coverage: "1 minor"
    documentation: "2 minor"
    secrets: PASS
    scope_creep: PASS
    security: "1 critical, 1 major"
```

## Review Types

The skill supports three review modes, selected via the `review_type` parameter:

### Full Review (default)

Applies to all PRs. Runs the complete 7-step checklist. Every category is evaluated and reported. This is the standard review mode for all changes entering the main branch.

**When to use:** All PRs targeting `main` or any release branch.

### Quick Review

Applies to small, low-risk changes (typo fixes, single-line refactors, dependency bumps). Skips the deeper analysis steps and focuses on correctness and conventions.

**Checklist run:** Steps 1 (correctness), 2 (conventions), 5 (secrets). Steps 3 (tests), 4 (docs), 6 (scope creep), and 7 (security) are marked as `SKIPPED: quick review` in the report.

**When to use:** Fast-track PRs per ADR 0002 §8, trivial documentation-only PRs, single-line changes.

### Security Review

Applies to changes that touch authentication, authorization, cryptography, secrets management, or data storage. Runs the full checklist but with security-specific depth:

- **Step 1 (correctness)**: Focus on authentication logic, token validation, permission checks.
- **Step 5 (secrets)**: Enhanced regex scanning for encryption keys, JWTs, OAuth tokens.
- **Step 7 (security)**: Full injection vector scan, dependency vulnerability assessment, CVE matching.
- **Additional**: Loads `rs-review-security` patterns before scanning.

**When to use:** PRs that modify auth middleware, encryption modules, API gateways, credential storage, or database access layers.

## Relationship to Other Review Skills

The review skill suite is modular, with three distinct skills that each serve a different purpose:

| Skill | Prefix | Role | Load Order |
|---|---|---|---|
| `rs-review-methodology` | The process | Defines the review workflow, checklist, and output format. This is always loaded first. | 1st |
| `rs-review-severity` | Classification | Defines severity levels (blocker, critical, major, minor, nitpick) with examples and edge cases. Ensures consistent classification across all reviews. | 2nd |
| `rs-review-security` | Patterns | Credential regex patterns, injection vectors, dangerous function call database, CVE reference format. Updated independently as new threats emerge. | 3rd (security review only) |

The separation keeps each skill focused and independently maintainable:

- A change to the review process (e.g., adding a new checklist item) only updates `rs-review-methodology`.
- A change to severity definitions (e.g., reclassifying a pattern) only updates `rs-review-severity`.
- A new vulnerability pattern (e.g., a new credential format) only updates `rs-review-security`.

This modularity follows the [workflow-patterns](../knowledge/tooling/opencode/skills/workflow-patterns) convention of single-responsibility skills.

## Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Checklist ordering | Correctness first, security last | Correctness failures may invalidate the entire diff. Security comes last because it requires full diff context. Secrets detection is separate from security because it has a higher escalation path (blocker vs critical). |
| Output format | Structured YAML | Machine-parseable for CI integration. Human-readable when rendered. Compatible with the Reviewer agent's structured output capability. |
| Review types | Three-tier (full, quick, security) | Matches the risk profile of different change types. Quick reviews save time on trivial changes. Security reviews add depth where needed. |
| Permissions on skill | Read-only | The skill provides instructions only. Execution permissions are on the parent agent. This keeps the skill portable across agents with different permission profiles. |
| No auto-resolution | Findings recorded only | The skill does not auto-resolve threads or approve PRs. It is an advisory gate — final merge decisions belong to humans or CI policy. |

## See Also

- [Reviewer Agent Design](../../agents/reviewer.md) — The agent that loads this skill
- [ADR 0002: GitHub Etiquettes](../../../adr/0002-github-etiquettes/overview.md) — The conventions this skill enforces (§5)
- [Workflow Skill Patterns](../../../knowledge/tooling/opencode/skills/workflow-patterns.md) — Cross-cutting skill conventions
- `rs-review-severity` — Severity classification guide (related skill)
- `rs-review-security` — Security pattern database (related skill)

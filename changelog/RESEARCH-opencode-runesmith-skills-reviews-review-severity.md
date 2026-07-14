---
title: "Review Severity Classification Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - skills
  - review
  - severity
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
references:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Review Severity Classification Skill Design

## Context

The `@runicengines/opencode-runesmith` plugin provides OpenCode agents with structured review capabilities. The `rs-review-severity` skill is a classification skill — it defines severity levels for review findings and provides deterministic rules for assigning a severity label to each finding the reviewer agent discovers.

This skill is loaded alongside `rs-review-methodology` by the reviewer agent. When the reviewer detects an issue in code under review, it invokes `rs-review-severity` to classify that finding before recording it in the review output.

### Why a Dedicated Severity Skill?

Without explicit severity rules, different reviewers (or the same reviewer across sessions) may classify similar findings inconsistently. A dedicated skill:

- **Enforces consistency** — every SQL injection finding is S1, every variable naming concern is S4 or S5.
- **Makes merge gating explicit** — the severity level directly determines whether a finding blocks merge (S1, S2) or is advisory (S3–S5).
- **Documents the rationale** — each classification includes a justification, so authors understand why a particular level was chosen and what they need to fix.
- **Separates concerns** — the methodology skill handles *what* to review; the severity skill handles *how to grade* findings. They can evolve independently.

### Skill Identity

| Property | Value |
|---|---|
| Plugin | `@runicengines/opencode-runesmith` |
| Skill name | `rs-review-severity` |
| Skill prefix | `rs-` |
| Loading model | On-demand, alongside `rs-review-methodology` |
| Primary user | Reviewer agent |
| Trigger | Reviewer found an issue and needs to classify it |

---

## Severity Classification Matrix

The following five-level matrix defines all recognised severity levels. Every review finding MUST be assigned exactly one level.

| Level | Label | Merge Blocking? | Meaning | Example |
|---|---|---|---|---|
| S1 | Blocker | Yes | Security vulnerability, data loss risk, complete logic failure | SQL injection, hardcoded secrets, authentication bypass |
| S2 | Critical | Yes | Major functionality broken, significant performance regression | API contract broken, O(n²) introduced in hot path, data corruption risk |
| S3 | Major | No | Functionality degraded, significant style/convention violation | Missing error handling, not following ADR 0002 branching convention |
| S4 | Minor | No | Cosmetic, non-critical style, minor optimization | Variable naming, minor formatting inconsistency, unused import |
| S5 | Nitpick | No | Preference, not required | Personal style preference, alternative approach suggestion |

### Merge Blocking Semantics

Findings labelled **S1** or **S2** MUST be resolved before merge. The reviewer agent MUST include a blocking notice in the review summary when any S1 or S2 finding is present. Findings labelled **S3**, **S4**, or **S5** are advisory — the author may address them at their discretion, though the reviewer SHOULD note patterns (e.g., "three S3 findings all relate to missing error handling in the same module").

---

## Recommended SKILL.md Instructions

The following block is the recommended instruction body for the skill's `SKILL.md` file.

```markdown
---
name: rs-review-severity
description: >
  Classify review findings by severity (S1–S5). Provides deterministic
  rules for labelling issues found during code review so that merge
  gating is consistent across all reviews.
license: MIT
compatibility: opencode
metadata:
  classification: review
  audience: agents
  trigger: manual
---

# rs-review-severity

## Purpose

Defines five severity levels (S1 Blocker through S5 Nitpick) and provides
decision rules for assigning one level to each review finding. The output
is a structured finding record that the reviewer agent includes in its
review output.

## When to Invoke

- The reviewer has identified a specific issue in the code under review.
- The reviewer needs to determine whether a finding blocks merge.
- The reviewer is preparing the final review summary and needs consistent
  labels for each finding.

## Trigger

| Condition | Type |
|---|---|
| Reviewer calls `skill({ name: "rs-review-severity" })` with a finding object | Manual |

## Input

A single review finding with the following fields:

```typescript
{
  finding: {
    description: string;      // What the issue is
    filePath: string;         // File where the issue was found
    lineNumber?: number;      // Optional: specific line
    category: string;         // e.g. "security", "performance", "correctness",
                              //       "style", "convention", "maintainability"
    impact: string;           // Description of the potential impact
  }
}
```

## Classification Rules

Apply the following rules in order. The first rule that matches determines
the severity.

### Rule 1: Security and data integrity (S1 Blocker)

Assign **S1** if any of the following are true:

- The finding involves direct injection risk (SQL, NoSQL, command, LDAP).
- Hardcoded secrets, tokens, passwords, or API keys appear in source code.
- Authentication or authorisation logic is missing or bypassable.
- The finding involves data loss or irreversible destruction (e.g. `DROP
  TABLE` in a migration without a backup plan, `rm -rf` in scripts).
- Sensitive data (PII, credentials) is logged, exposed in error messages,
  or transmitted without encryption.
- The finding enables privilege escalation or unauthorised access.

> Always err on the side of higher severity for security issues. If any
> security rule matches, the finding is S1 even if the likelihood seems low.

### Rule 2: Correctness and contract violations (S2 Critical)

Assign **S2** if the finding does not match Rule 1 AND any of the following
are true:

- An API contract (shape, type, protocol) is broken in a way that will
  cause runtime failures for consumers.
- The change introduces an algorithmic regression worse than O(n log n)
  in a hot path (e.g. O(n²) or O(2^n) in a frequently-called function).
- The finding describes a complete feature or function that does not work
  as specified.
- Data corruption is possible under normal (non-malicious) conditions.
- A core business logic invariant is violated (e.g. "total must equal
  sum of line items" but the calculation is wrong).

### Rule 3: Convention and degradation (S3 Major)

Assign **S3** if the finding does not match Rules 1–2 AND any of the
following are true:

- Functionality is degraded (works but missing edge cases, error states,
  or input validation).
- The code violates a documented convention (ADR, style guide, team
  convention) in a substantive way.
- Error handling is missing for a known failure mode (network timeout,
  file not found, permission denied).
- A maintainability concern that will cause friction for future
  developers (deeply nested logic, excessive duplication, no tests for
  a non-trivial function).
- The finding introduces technical debt that should be addressed before
  the codebase grows around it.

### Rule 4: Style and organisation (S4 Minor)

Assign **S4** if the finding does not match Rules 1–3 AND any of the
following are true:

- Variable, function, or class naming does not follow project conventions
  (e.g. camelCase vs snake_case mismatch).
- Minor formatting issues not caught by auto-formatters (extra blank
  lines, inconsistent indentation in comments).
- Unused imports, variables, or dead code comments that clutter the
  file without affecting behaviour.
- Inconsistent organisational patterns (e.g. one test file uses
  `describe`/`it` while another uses `test` for the same kind of test).

### Rule 5: Preference (S5 Nitpick)

Assign **S5** if none of Rules 1–4 match. S5 covers:

- Alternative approaches that are functionally equivalent.
- Personal style preferences ("I prefer arrow functions here").
- Suggestions for future improvement that are not blocking or degrading.
- Observations that do not warrant action but are worth noting.

### Tiebreaker

If after applying Rules 1–5 you are uncertain between two adjacent levels,
choose the **lower** (less severe) level. Document the uncertainty in the
justification field.

## Output Format

The skill returns a structured finding record:

```typescript
{
  severity: "S1" | "S2" | "S3" | "S4" | "S5";
  label: "Blocker" | "Critical" | "Major" | "Minor" | "Nitpick";
  blocksMerge: boolean;
  justification: string;    // Short explanation of why this severity
                            // was chosen, referencing the rule that matched
  originalFinding: {
    description: string;
    filePath: string;
    lineNumber?: number;
    category: string;
    impact: string;
  };
}
```

### Justification Examples

- **S1**: "Hardcoded AWS secret key in config/credentials.ts:12. Rule 1
  (hardcoded secrets) triggered — S1 Blocker, blocks merge."
- **S2**: "API response type changed from `User[]` to `string[]` in
  GET /users. Rule 2 (API contract broken) triggered — S2 Critical,
  blocks merge."
- **S3**: "No error handling for `fetch` failure in
  services/user-service.ts:34. Rule 3 (missing error handling)
  triggered — S3 Major, does not block merge."
- **S4**: "Variable `userName` should be `user_name` per project
  convention in services/auth.ts:88. Rule 4 (naming convention)
  triggered — S4 Minor, does not block merge."
- **S5**: "Consider using `Array.from` instead of spread operator for
  readability in utils/transform.ts:22. Rule 5 (preference) triggered
  — S5 Nitpick, does not block merge."

## See Also

- [rs-review-methodology](/research/opencode-runesmith/skills/reviews/review-methodology/) — Loaded alongside this skill; handles review scope and procedure
- [Knowledge: OpenCode Skills Overview](/knowledge/tooling/opencode/skills/overview/) — OpenCode skill system reference
```

---

## Classification Decision Tree

The following decision tree provides a quick reference for the reviewer agent. It mirrors the Rules section above but in a flowchart structure suitable for fast lookup.

```
                     ┌─────────────────────────┐
                     │   New review finding     │
                     └──────────┬──────────────┘
                                │
                   ┌────────────▼────────────┐
                   │  Security or data loss? │
                   │  (injection, secrets,   │
                   │   auth bypass, PII)     │
                   └────┬─────────────┬──────┘
                        │ YES         │ NO
                        ▼             │
                  ┌──────────┐        │
                  │   S1     │        │
                  │ Blocker  │        │
                  └──────────┘        │
                          ┌───────────▼───────────┐
                          │  Contract broken or   │
                          │  major correctness?   │
                          │  (API break, O(n²),   │
                          │   feature broken,     │
                          │   data corruption)    │
                          └────┬────────────┬─────┘
                               │ YES        │ NO
                               ▼            │
                         ┌──────────┐       │
                         │   S2     │       │
                         │ Critical │       │
                         └──────────┘       │
                                 ┌──────────▼──────────┐
                                 │  Convention or      │
                                 │  functionality      │
                                 │  degraded?          │
                                 │  (missing handling, │
                                 │   ADR violation,    │
                                 │   tech debt)        │
                                 └────┬───────────┬────┘
                                      │ YES       │ NO
                                      ▼           │
                                ┌──────────┐      │
                                │   S3     │      │
                                │  Major   │      │
                                └──────────┘      │
                                        ┌─────────▼─────────┐
                                        │  Style /          │
                                        │  organisation?    │
                                        │  (naming,         │
                                        │  formatting,      │
                                        │  unused code)     │
                                        └────┬─────────┬────┘
                                             │ YES     │ NO
                                             ▼         │
                                       ┌──────────┐    │
                                       │   S4     │    │
                                       │  Minor   │    │
                                       └──────────┘    │
                                                ┌──────▼──────┐
                                                │     S5      │
                                                │   Nitpick   │
                                                └─────────────┘
```

### Using the Decision Tree

1. Start at the top with the raw finding.
2. Answer each question with the finding's context.
3. Follow the YES branch as soon as a rule matches.
4. If unsure, follow the NO branch and re-evaluate — the tiebreaker rule (choose lower severity) applies when the question is ambiguous.
5. Document which question matched as the justification.

---

## Analysis

### Design Decisions

**1. Security-first ordering.** Rule 1 (S1) is evaluated first and matches on the broadest set of conditions. This ensures security issues are never downgraded by mistake. A finding that is both a security vulnerability and a style concern (e.g., a hardcoded secret using non-standard variable naming) is always classified by the security property, not the style property.

**2. Five levels, not three or seven.** Three levels (high/medium/low) collapse too much distinction — style issues and preference feel very different, and merge-blocking vs advisory is a binary that maps poorly onto three buckets. Seven levels add complexity without practical value for code review. Five maps cleanly to the blocking (S1–S2) vs advisory (S3–S5) split and provides enough granularity for useful trend analysis.

**3. Blocking attached to the level, not the finding author.** Whether a finding blocks merge is determined by severity level, not by who raised it or how strongly they feel. This prevents personality-driven merge gating. The only exception is the tiebreaker rule, which explicitly biases *downward* to avoid false positives blocking progress.

**4. Explicit justification required.** Every classified finding includes a `justification` field that references the matched rule. This serves three purposes: (a) the author understands the reasoning, (b) the reviewer can audit their own consistency over time, and (c) an automated CI gate could theoretically re-evaluate the classification by re-running the rules against the finding.

**5. Skill is stateless and pure.** The classification function takes a finding and returns a severity. It does not depend on previous findings, the author's identity, the file's history, or any external state. This keeps the skill simple to test and predictable in behaviour.

### Risk Assessment

**Over-classification of style issues.** A reviewer may be tempted to classify every style deviation as S3 (Major) because "conventions matter." The decision tree guards against this by channelling pure style/naming issues to Rule 4 (S4) before they can match Rule 3 (S3). The wording in Rule 3 emphasises "substantive" convention violations — a missing ADR-required branch naming pattern is substantive; a missing space after a comma is not.

**Under-classification of security issues.** The security-first ordering and strong language ("always err on the side of higher severity for security issues") mitigate this. However, the classification is only as good as the reviewer's ability to recognise security issues. If the reviewer agent lacks security scanning skills, S1 findings may be missed entirely. This is a methodology gap, not a severity gap — and should be addressed in the `rs-review-methodology` skill.

**False positives in merge blocking.** An S2 finding that is genuinely critical but trivial to fix (e.g., a one-character type error in an API response type) should still block merge. The criticality is about the impact if it ships, not the effort to fix it. This is intentional: the severity reflects risk to the codebase, not inconvenience to the author.

### Recommendations

1. **Add a severity trend log.** After each review, log the distribution of severity levels (e.g., "2 S3, 5 S4, 1 S5"). Over time, this helps the team identify recurring patterns — if the same module consistently gets S3 findings, it may need a refactor or better conventions documented.

2. **Integrate with automated scanning.** The S1 rules for hardcoded secrets and injection risk should ideally be caught by a pre-commit hook or CI scanner. The review severity skill can still classify them, but if they reach review stage undetected, the process has already leaked. Consider a pre-review scan step that feeds classified findings into the reviewer.

3. **Extend the category field.** The input `category` field currently accepts free-text strings. Consider constraining it to an enum matching the severity rules (`security`, `correctness`, `convention`, `style`, `preference`) so the classification can use it as a pre-filter before running through the decision tree.

4. **Document the escalation path.** If the author disagrees with a severity classification, there should be a documented process for escalation (e.g., the author adds a review comment stating the disagreement and a third reviewer arbitrates). This keeps the severity system from becoming a source of conflict itself.

---

## See Also

- [Knowledge: OpenCode Skills Overview](/knowledge/tooling/opencode/skills/overview/) — OpenCode skill system reference
- [rs-review-methodology](/research/opencode-runesmith/skills/reviews/review-methodology/) — Companion skill for review scope and procedure
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills) — OpenCode's official docs

---
name: rs-review-severity
description: >
  Classify review findings using the S1–S5 severity matrix with
  merge-blocking semantics, tiebreaker rules, and structured
  rationale for each classification decision.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: planning
  audience: developers
  trigger: chained
---

## Purpose

Provide a deterministic S1–S5 severity classification system for code review findings. Defines 5 severity levels with clear definitions, merge-blocking semantics, and tiebreaker rules for ambiguous cases. Designed to be chained by rs-review-methodology and all domain review skills.

## When to Invoke

- A review finding needs severity classification.
- rs-review-methodology chains this skill during report generation.
- The user explicitly asks for severity classification of a finding.

Do NOT invoke when:

- No finding context (file, line, description) is available.
- The finding is purely informational with no actionable concern.

## Severity Matrix

| Level | Label    | Merge-Blocking | Definition                                                              |
| ----- | -------- | -------------- | ----------------------------------------------------------------------- |
| S1    | Critical | Yes            | Data loss, security breach, PII exposure, production outage             |
| S2    | Major    | Yes            | Logic bug, broken contract, incorrect behaviour, severe perf regression |
| S3    | Moderate | No             | Maintainability concern, minor logic gap, missing error handling        |
| S4    | Minor    | No             | Style violation, naming nit, comment typo, formatting                   |
| S5    | Nitpick  | No             | Suggestion, preference, future improvement, non-blocking                |

## Classification Rules

1. **Rule 1 — Safety first**: If a finding could lead to data loss, security breach, or PII exposure, classify S1 regardless of other factors.
2. **Rule 2 — Behaviour matters**: If the finding represents incorrect behaviour at runtime (wrong output, crash, hang), classify S2.
3. **Rule 3 — Maintainability**: If the finding reduces long-term maintainability but does not affect correctness, classify S3.
4. **Rule 4 — Style only**: If the finding is purely stylistic with no behaviour or maintainability impact, classify S4.
5. **Rule 5 — Future**: If the finding is a suggestion or preference for future improvement, classify S5.

## Tiebreaker Rules

When a finding matches criteria for multiple levels:

1. Always escalate to the higher severity (safety-first).
2. If behavioural impact is unclear, treat as S3 not S2.
3. If style vs. maintainability is ambiguous, treat as S4 not S3.
4. When in doubt after applying rules 1–3, classify as S3.

## Workflow Steps

### 1. Receive finding context

Accept finding details: file, line, description, code snippet, step from the 7-step methodology checklist.

### 2. Apply Rules 1–5

Evaluate against each rule in order. The first matching rule determines severity.

### 3. Apply tiebreaker if ambiguous

If multiple rules match, apply tiebreaker rules 1–4 in order.

### 4. Determine merge-blocking status

S1 and S2 are merge-blocking. S3, S4, S5 are not.

### 5. Return classification

Output a structured YAML block with severity, rationale, merge-blocking flag, and applicable rule number.

## Output Format

```yaml
severity: S2
label: Major
merge_blocking: true
rule: 2
rationale: "Incorrect behaviour at runtime — wrong output in sort function"
tiebreaker_applied: false
```

## Required Permissions

| Tool  | Required | Scope           | Purpose                                 |
| ----- | -------- | --------------- | --------------------------------------- |
| read  | Yes      | Finding context | Read finding details for classification |
| edit  | No       | —               | Read-only classification skill          |
| write | No       | —               | Read-only classification skill          |

## Chained Skills

None. This is a leaf classification skill.

## See Also

- rs-review-methodology — parent orchestrator
- rs-review-security — security domain findings
- rs-review-code — code quality findings
- rs-review-architecture — architecture findings

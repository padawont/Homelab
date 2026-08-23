---
name: rs-review-methodology
description: >
  Coordinate structured code reviews using a 7-step checklist
  (Correctness, Conventions, Test Coverage, Documentation, Secrets,
  Scope Creep, Security) across full, quick, and security review types.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: planning
  audience: developers
  trigger: chained
---

## Purpose

Orchestrate pull request reviews with a repeatable methodology. Applies a 7-step checklist, classifies findings by severity (S1–S5), and produces a structured review report. Supports three review types — full, quick, and security — each with a tailored subset of checklist items and depth requirements.

## When to Invoke

- A pull request needs a structured review report.
- A downstream review skill (rs-review-severity, rs-review-security, rs-review-code, rs-review-architecture) chains back for methodology coordination.
- The user requests a specific review type (full, quick, security).

Do NOT invoke when:

- The review is purely informal or conversational.
- No code diff or PR description is available.

## Workflow Steps

### 1. Load PR context

Accept the PR diff, description, and any existing review comments. Determine the review type from user input or by chaining metadata.

### 2. Run the 7-step checklist

For **full** reviews, evaluate all 7 steps. For **quick** reviews, evaluate steps 1, 4, 5 only. For **security** reviews, evaluate steps 1, 7 only.

| #   | Step                                           | Full | Quick | Security |
| --- | ---------------------------------------------- | ---- | ----- | -------- |
| 1   | Correctness — logic, edge cases, data flow     | Yes  | Yes   | Yes      |
| 2   | Conventions — style, naming, patterns          | Yes  | No    | No       |
| 3   | Test Coverage — new tests, existing breakage   | Yes  | No    | No       |
| 4   | Documentation — API docs, inline comments      | Yes  | Yes   | No       |
| 5   | Secrets — hardcoded keys, tokens, credentials  | Yes  | Yes   | No       |
| 6   | Scope Creep — unrelated changes, feature bloat | Yes  | No    | No       |
| 7   | Security — injection, auth, data exposure      | Yes  | No    | Yes      |

### 3. Classify each finding by severity

Assign one of S1–S5 per finding using the rs-review-severity matrix.

### 4. Generate structured report

Produce a YAML report containing:

- `review_type`: full | quick | security
- `checklist`: per-step status (pass | fail | skip) with findings
- `findings`: list of individual findings with severity, file, line, description, recommendation
- `summary`: total findings, S1 count, S2 count, verdict (approve | changes-requested | blocked)

### 5. Chain downstream skills

If the review type is full or security, chain rs-review-security for deep security analysis. If full, also chain rs-review-code and rs-review-architecture.

## Output Format

```yaml
review_type: full
checklist:
  correctness: pass
  conventions: fail
  test_coverage: pass
  documentation: pass
  secrets: pass
  scope_creep: pass
  security: pass
findings:
  - severity: S2
    file: src/auth.py
    line: 42
    step: conventions
    description: Function exceeds 50-line limit
    recommendation: Extract helper functions
summary:
  total_findings: 3
  s1_count: 0
  s2_count: 1
  s3_count: 2
  verdict: changes-requested
```

## Required Permissions

| Tool  | Required | Scope                 | Purpose                         |
| ----- | -------- | --------------------- | ------------------------------- |
| read  | Yes      | PR diff, source files | Read PR context and code        |
| grep  | Yes      | Source tree           | Search for patterns in findings |
| bash  | Yes      | git                   | Get PR diff and metadata        |
| edit  | No       | —                     | Read-only review skill          |
| write | No       | —                     | Read-only review skill          |

## Chained Skills

| Skill                  | When to Chain                  |
| ---------------------- | ------------------------------ |
| rs-review-severity     | Every finding — classify S1–S5 |
| rs-review-security     | Full or security review type   |
| rs-review-code         | Full review type               |
| rs-review-architecture | Full review type               |

## See Also

- rs-review-severity — S1–S5 classification matrix
- rs-review-security — Deep security domain analysis
- rs-review-code — Google Engineering Practices code review
- rs-review-architecture — Azure WAF architecture review

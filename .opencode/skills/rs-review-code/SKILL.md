---
name: rs-review-code
description: >
  Perform code review following Google Engineering Practices across
  9 categories: design, functionality, complexity, test coverage,
  naming, style, consistency, documentation, and performance.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: planning
  audience: developers
  trigger: chained
---

## Purpose

Conduct a structured code review aligned with Google Engineering Practices. Evaluates PR changes across 9 categories, producing actionable findings with severity classification and remediation suggestions.

## When to Invoke

- rs-review-methodology chains this skill for full review types.
- The user requests a code quality review.
- A PR touches business logic, tests, or core infrastructure.

Do NOT invoke when:

- The PR is documentation-only or configuration-only.
- Code review has already been performed in the current session.

## 9-Category Checklist

| #   | Category      | Focus Areas                                                                            |
| --- | ------------- | -------------------------------------------------------------------------------------- |
| 1   | Design        | Code fits overall architecture, follows established patterns, appropriate abstractions |
| 2   | Functionality | Code does what it should, handles edge cases, error states covered                     |
| 3   | Complexity    | Over-engineering, unnecessary abstractions, overly clever solutions                    |
| 4   | Test Coverage | New code has tests, existing tests pass, test quality and meaning                      |
| 5   | Naming        | Clear, descriptive names following project conventions                                 |
| 6   | Style         | Language idioms, formatting, project style guide adherence                             |
| 7   | Consistency   | Same patterns as surrounding code, consistent error handling, logging                  |
| 8   | Documentation | API docs, inline comments explaining why (not what), README updates                    |
| 9   | Performance   | Algorithm choice, unnecessary allocations, N+1 queries, caching                        |

## Workflow Steps

### 1. Review design

Evaluate whether the code fits the existing architecture. Flag inappropriate abstractions or deviations from established patterns.

### 2. Review functionality

Verify correctness: does the code handle expected inputs, edge cases, and error states?

### 3. Review complexity

Identify over-engineering, premature optimisation, unnecessary indirection.

### 4. Review test coverage

Check that new code has meaningful tests. Flag untested paths and low-quality assertions.

### 5. Review naming

Check identifiers for clarity, consistency, and adherence to project conventions.

### 6. Review style

Verify language idioms, formatting, and project style guide compliance.

### 7. Review consistency

Check for consistent patterns with surrounding code: same error handling, same logging approach, same module structure.

### 8. Review documentation

Assess inline comments, API docs, and README updates for the new code.

### 9. Review performance

Identify algorithmic inefficiencies, unnecessary allocations, N+1 queries, missing caching.

### 10. Generate code review report

Produce structured YAML with findings per category, severity, and remediation.

## Output Format

```yaml
code_review:
  categories:
    design:
      status: pass
      findings: []
    functionality:
      status: fail
      findings:
        - category: functionality
          severity: S2
          file: src/orders.py
          line: 120
          description: Missing null check on order.total
          remediation: Add early return when total is None
  summary:
    total_findings: 4
    s1_count: 0
    s2_count: 1
    s3_count: 2
    s4_count: 1
```

## Required Permissions

| Tool  | Required | Scope        | Purpose                     |
| ----- | -------- | ------------ | --------------------------- |
| read  | Yes      | Source files | Read code changes           |
| grep  | Yes      | Source tree  | Search for patterns in code |
| bash  | Yes      | git          | Get PR diff                 |
| edit  | No       | —            | Read-only review skill      |
| write | No       | —            | Read-only review skill      |

## Chained Skills

| Skill              | When to Chain                  |
| ------------------ | ------------------------------ |
| rs-review-severity | Every finding — classify S1–S5 |

## See Also

- rs-review-methodology — parent orchestrator
- rs-review-severity — severity classification
- Google Engineering Practices — https://google.github.io/eng-practices/

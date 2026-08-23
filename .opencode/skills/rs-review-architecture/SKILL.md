---
name: rs-review-architecture
description: >
  Review architecture changes using Azure Well-Architected Framework
  5 pillars (reliability, security, cost, operations, performance)
  with C4 model level detection and per-pillar scoring (0–100).
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: planning
  audience: architects
  trigger: chained
---

## Purpose

Perform a structured architecture review using the Azure Well-Architected Framework (WAF). Evaluates PR changes across 5 pillars, assigns per-pillar scores (0–100), determines the C4 model level of each change, and produces an overall grade (A–F).

## When to Invoke

- rs-review-methodology chains this skill for full review types.
- A PR affects system architecture, infrastructure, or cross-cutting concerns.
- The user explicitly requests an architecture review.

Do NOT invoke when:

- The PR contains only application-level code changes with no architectural impact.
- Architecture review has already been performed in the current session.

## 5-Pillar Checklist (Azure WAF)

| #   | Pillar                 | Focus Areas                                                             |
| --- | ---------------------- | ----------------------------------------------------------------------- |
| 1   | Reliability            | Fault tolerance, disaster recovery, backup strategy, redundancy, SLAs   |
| 2   | Security               | Zero-trust, network security, identity, encryption, secrets management  |
| 3   | Cost Optimisation      | Resource sizing, reserved instances, waste elimination, right-sizing    |
| 4   | Operational Excellence | Monitoring, logging, alerting, deployment automation, runbooks          |
| 5   | Performance Efficiency | Scaling strategy, caching, CDN, data partitioning, latency optimisation |

## C4 Model Levels

| Level | Name           | Scope                                                          |
| ----- | -------------- | -------------------------------------------------------------- |
| L1    | System Context | System boundaries, external actors, system dependencies        |
| L2    | Container      | High-level technology choices, service boundaries, data stores |
| L3    | Component      | Internal module structure, interfaces, design patterns         |
| L4    | Code           | Specific classes, functions, data structures                   |

## Scoring and Grading

Per-pillar score: 0–100 based on completeness and correctness of the pillar's concerns.

Overall grade:

| Grade | Score Range |
| ----- | ----------- |
| A     | 90–100      |
| B     | 75–89       |
| C     | 60–74       |
| D     | 40–59       |
| F     | 0–39        |

## Workflow Steps

### 1. Determine C4 level

Identify the C4 abstraction level of the change: System Context, Container, Component, or Code.

### 2. Evaluate Reliability pillar

Assess fault tolerance, redundancy, backup, disaster recovery coverage.

### 3. Evaluate Security pillar

Review zero-trust compliance, network segmentation, identity, encryption.

### 4. Evaluate Cost pillar

Identify cost optimisation opportunities: right-sizing, reserved instances, waste.

### 5. Evaluate Operations pillar

Check monitoring, logging, alerting, deployment automation, runbooks.

### 6. Evaluate Performance pillar

Review scaling strategy, caching, CDN, data partitioning, latency.

### 7. Generate architecture report

Produce structured YAML with per-pillar scores, overall grade, C4 level, and recommendations.

## Output Format

```yaml
architecture_review:
  c4_level: L3
  pillars:
    reliability:
      score: 85
      findings:
        - severity: S3
          description: Missing circuit breaker pattern
          recommendation: Implement circuit breaker for external calls
    security:
      score: 92
      findings: []
    cost:
      score: 70
      findings:
        - severity: S4
          description: Over-provisioned DB instance
          recommendation: Right-size based on usage metrics
    operations:
      score: 88
      findings: []
    performance:
      score: 80
      findings: []
  overall_grade: B
  summary:
    total_findings: 2
    s1_count: 0
    s2_count: 0
    s3_count: 1
    s4_count: 1
```

## Required Permissions

| Tool  | Required | Scope                          | Purpose                          |
| ----- | -------- | ------------------------------ | -------------------------------- |
| read  | Yes      | Source, infrastructure, config | Read architecture-relevant files |
| grep  | Yes      | Source tree                    | Search for architecture patterns |
| bash  | Yes      | git                            | Get PR diff                      |
| edit  | No       | —                              | Read-only review skill           |
| write | No       | —                              | Read-only review skill           |

## Chained Skills

| Skill              | When to Chain                  |
| ------------------ | ------------------------------ |
| rs-review-severity | Every finding — classify S1–S5 |

## See Also

- rs-review-methodology — parent orchestrator
- rs-review-severity — severity classification
- Azure WAF — https://learn.microsoft.com/en-us/azure/well-architected/
- C4 Model — https://c4model.com/

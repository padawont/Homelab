---
name: rs-doc-auditor
description: >
  Audit documentation against the Diataxis framework across 3 weighted
  dimensions (Diataxis compliance 40%, Structural integrity 35%, Content
  quality 25%) and produce an A–F grade report.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: planning
  audience: tech-writer
  trigger: chained
---

## Purpose

Audit a project's documentation against the Diataxis documentation framework. Evaluates documentation across three weighted dimensions: Diataxis classification compliance (40%), structural integrity (35%), and content quality (25%). Produces a structured report with per-dimension scores, an overall A–F grade, and actionable recommendations.

## When to Invoke

- The user requests a documentation audit or quality check.
- A new documentation directory structure needs validation.
- A PR adds or modifies documentation files.
- Before a release to verify documentation completeness.

Do NOT invoke when:

- No documentation directory exists or is expected.
- The audit would target auto-generated API docs only.

## Dimension Weights

| Dimension            | Weight | Description                                                                     |
| -------------------- | ------ | ------------------------------------------------------------------------------- |
| Diataxis Compliance  | 40%    | Correct classification into tutorials, how-to, explanation, reference quadrants |
| Structural Integrity | 35%    | Directory layout, cross-references, navigation, broken links                    |
| Content Quality      | 25%    | Clarity, completeness, audience appropriateness, formatting                     |

## Scoring and Grading

Per-dimension score: 0–100.

Overall grade:

| Grade | Score Range |
| ----- | ----------- |
| A     | 90–100      |
| B     | 75–89       |
| C     | 60–74       |
| D     | 40–59       |
| F     | 0–39        |

## Workflow Steps

### 1. Scan documentation directory

Walk the docs/ directory tree. Identify all quadrants: tutorials/, how-to/, explanation/, reference/. Flag missing quadrants.

### 2. Evaluate Diataxis classification (40%)

For each document, verify it is placed in the correct quadrant:

- **Tutorials**: Step-by-step, learning-oriented, no assumed knowledge
- **How-to**: Goal-oriented, practical recipes, assumes basic knowledge
- **Explanation**: Background, concepts, design rationale, reflection
- **Reference**: Technical specs, commands, configuration, authoritative

### 3. Evaluate structural integrity (35%)

Check for:

- All required quadrants present
- Cross-references between related documents across quadrants
- No broken internal links
- Consistent navigation structure
- Index/overview pages in each quadrant

### 4. Evaluate content quality (25%)

Assess:

- Clarity and readability
- Audience-appropriate tone and depth
- Completeness (no stub/TODO pages)
- Consistent formatting and style
- Examples and code snippets where applicable

### 5. Generate audit report

Produce structured YAML with per-dimension scores, overall grade, findings, and recommendations.

## Output Format

```yaml
doc_audit:
  dimensions:
    diataxis_compliance:
      score: 85
      weight: 0.40
      findings:
        - severity: S4
          description: "rs-discover.md in how-to/ contains tutorial content"
          recommendation: Move to tutorials/ quadrant
    structural_integrity:
      score: 70
      weight: 0.35
      findings:
        - severity: S3
          description: Missing reference/ index page
          recommendation: Create docs/reference/README.md
    content_quality:
      score: 90
      weight: 0.25
      findings: []
  overall_score: 81.5
  overall_grade: B
  summary:
    total_findings: 2
    total_quadrants: 4
    present_quadrants: 3
    missing_quadrants:
      - tutorials
```

## Required Permissions

| Tool  | Required | Scope           | Purpose                                  |
| ----- | -------- | --------------- | ---------------------------------------- |
| read  | Yes      | docs/ directory | Read documentation files                 |
| glob  | Yes      | docs/ tree      | Walk documentation structure             |
| grep  | Yes      | docs/ tree      | Search for cross-references and patterns |
| edit  | No       | —               | Read-only audit skill                    |
| write | No       | —               | Read-only audit skill                    |

## Chained Skills

| Skill              | When to Chain                  |
| ------------------ | ------------------------------ |
| rs-review-severity | Every finding — classify S1–S5 |

## See Also

- rs-review-severity — severity classification
- Diataxis framework — https://diataxis.fr/
- docs/ directory layout — project documentation structure

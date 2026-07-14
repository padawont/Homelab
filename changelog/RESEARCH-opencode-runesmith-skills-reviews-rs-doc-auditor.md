---
title: "Doc Auditor Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-14
tags:
  - opencode
  - skills
  - documentation
  - compliance
  - runesmith
sources:
  - knowledge: "knowledge/design/documentation/doc-compliance/README.md"
references:
  - url: "https://diataxis.fr/"
    title: "Diataxis Documentation Framework"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-14
---

# Doc Auditor Skill Design (`rs-doc-auditor`)

## Purpose

`rs-doc-auditor` is a review skill for the `@runicengines/opencode-runesmith` plugin. It validates that a project's documentation meets compliance requirements: covering all four Diataxis quadrants, satisfying structural requirements (required files, frontmatter, cross-links), and maintaining proper content classification (no explanation in tutorials, no how-to in reference). It produces a compliance score per quadrant and an overall score.

The skill is the documentation equivalent of a linter — it checks that docs follow the rules before they ship.

## Skill Identity

| Property | Value |
|---|---|
| Plugin | `@runicengines/opencode-runesmith` |
| Skill name | `rs-doc-auditor` |
| Skill prefix | `rs-` |
| Loading model | On-demand (via `skill({ name: "rs-doc-auditor" })`) |
| Primary user | Reviewer agent |
| Secondary users | Architect agent (gate validation), Tech-Writer agent (self-check) |
| Trigger | Pre-merge check, documentation review, periodic compliance audit |

## Permission Model

| Permission | Purpose |
|---|---|
| `read` | Read documentation files for validation |
| `glob` | Discover documentation files |
| `grep` | Search for frontmatter fields, cross-links, specific patterns |
| `edit: deny` | Read-only — the skill never modifies documentation |
| `(write report)` | The compliance report is written by the calling agent's context |

The skill is **read-only** for review and produces the compliance report for the calling agent to write. It must never modify any documentation file.

## Input

The skill accepts:

1. **Documentation root path** — directory to audit (default: `docs/`).
2. **Configuration** (optional YAML inline or file path):
   - `required_files` — list of files that must exist (e.g., `README.md`, `index.md`).
   - `required_frontmatter` — list of frontmatter fields that must be present in each file.
   - `cross_link_domains` — expected cross-link targets for validation.
   - `severity_threshold` — minimum acceptable overall score (default: 70/100).
   - `exclude_patterns` — glob patterns to exclude.

## Audit Dimensions

The skill checks three dimensions, each contributing to the overall compliance score.

### 1. Diataxis Coverage (40% of total score)

Check that documentation covers all four Diataxis quadrants:

| Quadrant | Check | Scoring |
|---|---|---|
| **Tutorials** | At least one getting-started or beginner walkthrough exists. | 25 points if present, 0 if missing |
| **How-to Guides** | At least one task-oriented guide exists (deploy, configure, integrate). | 25 points if present, 0 if missing |
| **Reference** | At least one API, CLI, or configuration reference exists. | 25 points if present, 0 if missing |
| **Explanation** | At least one conceptual or background document exists. | 25 points if present, 0 if missing |

The quadrant detection uses the same heuristics as `rs-doc-architect` (heading analysis, content structure, file path hints).

### 2. Structural Compliance (35% of total score)

Check that required structural elements are present:

| Check | Scoring |
|---|---|
| Required files exist (from `required_files` config) | 10 points per missing file deducted from max |
| Required frontmatter fields present in each file | 5 points per missing field deducted |
| Cross-links resolve to existing targets | 5 points per broken link deducted |
| No orphaned files (files not referenced in any index) | 3 points per orphan deducted |
| Directory structure follows project conventions | 5 points if clean, proportional deductions if messy |

Maximum structural score: 100 points, scaled to 35% of total.

### 3. Content Classification (25% of total score)

Check that content is correctly classified per Diataxis:

| Violation | Deduction |
|---|---|
| Tutorial contains explanation prose (conceptual background in a step-by-step) | −10 points per occurrence |
| How-to guide contains reference tables (parameter lists in a task guide) | −5 points per occurrence |
| Reference section contains how-to instructions (step-by-step in API docs) | −8 points per occurrence |
| Explanation document contains action steps (how-to content in a concept doc) | −8 points per occurrence |
| File in the wrong directory (e.g., tutorial file in reference directory) | −10 points per occurrence |

Maximum content score: 100 points, scaled to 25% of total.

## Workflow Steps

### Step 1: Discover and inventory documentation files

1. Recursively scan the specified doc root for `.md`, `.qmd`, `.rst` files.
2. Apply exclude patterns.
3. Build a file inventory with: path, frontmatter fields, H1 title, file size, last modified date.

### Step 2: Check Diataxis coverage

1. For each file, classify its primary quadrant using the `rs-doc-architect` classification heuristics (heading analysis, content structure, path hints).
2. Aggregate per-quadrant: which files belong to which quadrant.
3. Score each quadrant based on presence/absence and quality signals (word count, number of sections).

### Step 3: Check structural compliance

1. Verify required files exist.
2. For each file, extract frontmatter and check required fields (`title`, `sources`, `references`, `last_audit_date`, etc.).
3. Parse and resolve cross-links (both relative and knowledge-key format).
4. Identify orphaned files (files not linked from any index or parent document).

### Step 4: Check content classification

1. For each file, scan for content that violates its classified quadrant:
   - In tutorials: look for conceptual paragraphs (no actionable steps).
   - In how-to guides: look for parameter tables or API signatures.
   - In reference: look for imperative "how to" instructions.
   - In explanation: look for numbered steps or commands.
2. Flag files in wrong directories based on path vs content mismatch.

### Step 5: Compute scores and generate report

Generate a compliance report:

```yaml
overall_score: 74
overall_grade: "C"  # A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, F < 60

dimensions:
  diataxis_coverage:
    score: 65
    weight: 40%
    weighted_contribution: 26.0
    details:
      tutorials:
        present: true
        files: ["docs/getting-started.md"]
        score: 25
        notes: []
      how_to:
        present: false
        files: []
        score: 0
        notes: ["Critical: No how-to guides found. Users cannot accomplish tasks."]
      reference:
        present: true
        files: ["docs/api/index.md"]
        score: 25
        notes: []
      explanation:
        present: true
        files: ["docs/architecture.md"]
        score: 15
        notes: ["Only one explanation document — consider adding more."]

  structural_compliance:
    score: 78
    weight: 35%
    weighted_contribution: 27.0
    issues:
      - type: missing_frontmatter
        file: "docs/tutorials/quickstart.md"
        field: "last_audit_date"
      - type: broken_cross_link
        file: "docs/reference/config.md"
        target: "/knowledge/design/patterns/"
        note: "File not found"
      - type: orphaned_file
        file: "docs/old-guide.md"
        note: "Not referenced from any index"

  content_classification:
    score: 82
    weight: 25%
    weighted_contribution: 20.5
    violations:
      - file: "docs/tutorials/quickstart.md"
        violation: "explanation_prose"
        detail: "Section 'Architecture Overview' contains conceptual content in a tutorial"
        severity: moderate

recommendations:
  - priority: high
    item: "Create how-to guides for deployment and configuration workflows"
  - priority: high
    item: "Add last_audit_date frontmatter to docs/tutorials/quickstart.md"
  - priority: medium
    item: "Move conceptual content from quickstart.md to docs/explanation/"
```

## Output

The skill writes a compliance report file (default: `docs/audit/compliance-report.md` or `docs/audit/compliance-report.yaml`) containing:

1. **Overall score and grade** — single-number summary with letter grade.
2. **Per-dimension breakdown** — scores, findings, and issues for each of the three dimensions.
3. **Detailed issues list** — every compliance violation with file path, type, and severity.
4. **Prioritised recommendations** — actionable items ordered by impact.

## Chains With

| Skill | Condition | Step |
|---|---|---|
| `rs-doc-architect` | If the audit reveals gaps that need a restructure plan | After report generation |
| `rs-issue-to-plan` | If audit issues need to be filed as tasks | After report generation |
| `rs-consult` | If compliance rules need clarification from KB | Before Step 2 |

## Design Decisions

1. **Three weighted dimensions**. Diataxis coverage (40%) is weighted highest because missing a quadrant is the most fundamental documentation failure. Structure (35%) is next — broken links and missing files reduce usability. Content classification (25%) is last because misclassification is less harmful than missing content entirely.

2. **Configurable thresholds and requirements**. The skill accepts configuration for required files, frontmatter fields, and severity thresholds. This lets projects define their own compliance bar. Defaults follow RunicEngines KB conventions.

3. **No auto-fix**. The skill identifies issues but never fixes them. Auto-fixing would require edit permission on documentation files, which violates the read-only audit principle. The Tech-Writer agent handles fixes based on the report.

4. **Orphan file detection**. Files not referenced from any index or parent document are flagged. This catches dead documentation that has drifted out of the navigation structure.

## See Also

- [Doc compliance knowledge notes](../../../knowledge/design/documentation/doc-compliance/README.md) — Compliance definitions and standards
- [Diataxis knowledge notes](../../../knowledge/design/documentation/diataxis/README.md) — The Diataxis framework reference
- [Doc Architect skill](../workflows/rs-doc-architect.md) — Complementary skill that produces restructure plans
- [Review Methodology skill](review-methodology.md) — General review process this skill extends
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills) — Skill system reference

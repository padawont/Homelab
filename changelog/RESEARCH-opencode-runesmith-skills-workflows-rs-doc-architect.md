---
title: "Doc Architect Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-14
tags:
  - opencode
  - skills
  - documentation
  - diataxis
  - runesmith
sources:
  - knowledge: "knowledge/design/documentation/diataxis/README.md"
references:
  - url: "https://diataxis.fr/"
    title: "Diataxis Documentation Framework"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-14
---

# Doc Architect Skill Design (`rs-doc-architect`)

## Purpose

`rs-doc-architect` is a workflow skill for the `@runicengines/opencode-runesmith` plugin. It audits an existing documentation site, classifies content into the four Diataxis quadrants (tutorials, how-to guides, reference, explanation), identifies gaps and misclassified content, and produces a structured documentation plan with a recommended site structure.

The skill transforms an unstructured doc set into a Diataxis-aligned architecture. It does **not** write documentation itself — it produces a plan that the Tech-Writer or Developer agent executes.

## Skill Identity

| Property | Value |
|---|---|
| Plugin | `@runicengines/opencode-runesmith` |
| Skill name | `rs-doc-architect` |
| Skill prefix | `rs-` |
| Loading model | On-demand (via `skill({ name: "rs-doc-architect" })`) |
| Primary user | Tech-Writer agent |
| Secondary users | Architect agent (planning phase), Spec-Writer agent (spec includes doc requirements) |
| Trigger | Documentation review, new project setup, doc site redesign |

## Permission Model

| Permission | Purpose |
|---|---|
| `read` | Scan existing documentation files |
| `glob` | Discover documentation file patterns |
| `grep` | Search for content patterns, headings, cross-references |
| `edit: deny` | Read-only audit — the skill never modifies documentation |
| `(write report)` | The audit output plan is written to a specified path via edit permission in the calling agent's context |

The skill is **read-only** for the audit phase and produces the output plan for the calling agent to write. It must never modify existing documentation files.

## Input

The skill accepts:

1. **Documentation root path** — directory to scan (defaults to common doc roots: `docs/`, `documentation/`, `wiki/`, project `README.md`).
2. **Optional file list** — a specific set of files to audit, bypassing the discovery scan.
3. **Configuration** (optional):
   - `output_path` — where to write the documentation plan (default: `docs/plan/`)
   - `quadrant_order` — custom ordering of quadrants
   - `exclude_patterns` — glob patterns to exclude (e.g., `node_modules/`, `vendor/`)

## Workflow Steps

### Step 1: Discover documentation files

1. Recursively scan the specified doc root for `.md`, `.qmd`, `.rst`, `.ipynb` files.
2. Exclude auto-generated files (`node_modules/`, `build/`, `_site/`, `.vitepress/dist/`).
3. Build a file inventory with: path, file type, word count, heading structure.

### Step 2: Classify content by Diataxis quadrants

For each file, classify it into one or more Diataxis quadrants:

| Quadrant | Signal Patterns | Example Content |
|---|---|---|
| **Tutorial** (learning-oriented) | "Getting started", "Quickstart", step-by-step numbered lists, prerequisites, "Create a", "Build a" | Beginner guides, walkthroughs |
| **How-to guide** (task-oriented) | "How to", "Configure", "Set up", imperative headings, specific goals | Deployment guides, integration recipes |
| **Reference** (information-oriented) | API docs, CLI flags, config keys, type definitions, auto-generated docs | `man` pages, API reference, schema docs |
| **Explanation** (understanding-oriented) | "Background", "Why", "Architecture", "Design", "Concepts", "Under the hood" | Architecture decision records, conceptual overviews |

Classification heuristics:
- **Heading analysis**: Match section headings against quadrant keywords.
- **Content structure**: Tutorials have numbered steps; how-to guides have imperative commands; reference has tables/lists of parameters; explanation has prose paragraphs with no actionable steps.
- **File path hints**: Files in `tutorials/` are likely tutorials, in `api/` are likely reference, etc.

### Step 3: Identify gaps

Compare the classified content against the ideal Diataxis model. Produce a gap matrix:

| Quadrant | Files Found | Coverage Assessment | Gap Severity |
|---|---|---|---|
| Tutorials | 0 | Missing | Critical |
| How-to Guides | 3 | Adequate | None |
| Reference | 1 | Minimal | Moderate |
| Explanation | 2 | Partial | Low |

Severity scale:
- **Critical**: Quadrant is empty — users cannot learn, accomplish tasks, look up facts, or understand rationale.
- **Moderate**: Quadrant has content but major topics are undocumented.
- **Low**: Quadrant has coverage but minor gaps exist.
- **None**: Quadrant is well-covered.

### Step 4: Detect misclassified content

Flag files whose content does not match their location or title. Examples:
- A file in `tutorials/` that is actually a reference table.
- A "Getting Started" page that reads like architecture explanation.
- An API reference section that includes step-by-step how-to instructions.

Each misclassification is recorded with:
- The file path.
- The detected quadrant (based on content analysis).
- The expected quadrant (based on location/title).
- A recommendation: move, rename, or split the file.

### Step 5: Produce documentation plan

Generate a structured plan YAML/JSON:

```yaml
audit:
  root: docs/
  total_files: 24
  date: 2026-06-14

classification:
  tutorials:
    files: ["docs/getting-started.md"]
    coverage: minimal
    missing:
      - "Beginner tutorial for core workflow"
      - "Environment setup tutorial"
  how_to:
    files: ["docs/deploy.md", "docs/configure.md", "docs/integrate.md"]
    coverage: adequate
  reference:
    files: ["docs/api/index.md"]
    coverage: minimal
    missing:
      - "CLI reference"
      - "Configuration reference"
  explanation:
    files: ["docs/architecture.md", "docs/design-decisions.md"]
    coverage: partial
    missing:
      - "Conceptual overview of the system"

misclassified:
  - file: "docs/tutorials/api-install.md"
    detected: reference
    expected: how-to
    recommendation: "Move to docs/how-to/install.md"
  - file: "docs/reference/overview.md"
    detected: explanation
    expected: reference
    recommendation: "Split into docs/explanation/overview.md and docs/reference/config.md"

recommended_structure:
  - "docs/"
  - "docs/tutorials/"
  - "docs/how-to/"
  - "docs/reference/"
  - "docs/explanation/"
  - "docs/README.md"
```

## Output

The skill writes a documentation plan file (default: `docs/plan/doc-architecture-plan.md`) containing:

1. **Executive summary** — overall health of the documentation set.
2. **Classification matrix** — each file mapped to its primary quadrant.
3. **Gap analysis** — missing quadrants with severity.
4. **Misclassification report** — files in wrong locations.
5. **Recommended structure** — proposed directory layout.
6. **Prioritised recommendations** — ordered by impact (critical gaps first).

## Chains With

| Skill | Condition | Step |
|---|---|---|
| `rs-issue-to-plan` (see [issue-to-plan.md](issue-to-plan.md)) | If doc audit is part of a feature implementation plan | Before Step 1 |
| `rs-discover` (see [rs-discover.md](../utilities/rs-discover.md)) | If the project root needs discovery before doc scanning | Before Step 1 |
| `rs-consult` (see [rs-consult.md](../utilities/rs-consult.md)) | If the Diataxis classification needs domain expertise | Between Step 2 and 3 |

## Design Decisions

1. **Diataxis-only classification**. The skill only recognises the four Diataxis quadrants (formerly associated with the Divio documentation system, now known as the Diataxis framework). The Microsoft ELA model is not supported. If the team adopts a different model, a new skill should replace this one rather than extending it.

2. **Read-only audit, write-only output**. The skill never touches existing documentation. This prevents accidental corruption and makes the plan a safe artifact that can be reviewed before any changes are made.

3. **Heuristic classification, not ML**. The classification uses keyword matching, heading analysis, and path heuristics. This is intentionally simple — it covers 80% of cases correctly. Misclassifications are surfaced in the misclassification report for human review. An ML-based classifier would be more accurate but introduces model dependencies and reproducibility concerns.

4. **Plan is YAML-structured**. The output plan is machine-readable (YAML) so downstream tools can consume it. The Tech-Writer agent can convert the plan into a human-readable document if needed.

## See Also

- [Diataxis knowledge notes](../../../../knowledge/design/documentation/diataxis/README.md) — The Diataxis framework reference
- [Tech-Writer agent design](../../agents/tech-writer.md) — Primary consumer of this skill's output
- [Architect agent design](../../agents/architect.md) — Uses this skill during planning phase
- [Doc Auditor skill](../reviews/rs-doc-auditor.md) — Complementary compliance checker that validates docs after writing
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills) — Skill system reference

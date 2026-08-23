---
name: rs-doc-architect
description: >
  Audit documentation for Diataxis compliance. Classifies content into
  quadrants (tutorial, how-to, reference, explanation), identifies gaps
  and misclassified content, and produces a structured documentation plan.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: utility
  audience: developers, tech-writer
  trigger: manual+chained
---

## Purpose

Audits an existing documentation set against the Diataxis framework and produces a structured plan with classifications, gap analysis, misclassification detection, and a proposed directory layout. The skill never writes documentation itself — it produces a machine-readable plan that downstream agents (Tech-Writer, Architect, Spec-Writer) execute.

Key characteristics:

- **Read-only audit**: Never edits or creates documentation files. Only scans, reads, and analyses.
- **Diataxis-only**: Classifies exclusively into the four Diataxis quadrants (tutorial, how-to, reference, explanation). Does not support alternative documentation models.
- **Heuristic classification**: Uses heading analysis, keyword matching, and path heuristics — no ML dependencies.
- **Chaining-ready**: Output schema is consumed by `rs-issue-to-plan` and `rs-consult`.
- **Plan is YAML-structured**: The output plan is machine-readable so downstream tools can consume it directly.

## Trigger

| Condition                                           | Type                  |
| --------------------------------------------------- | --------------------- |
| User requests a documentation audit                 | Manual                |
| After codebase discovery reveals missing docs       | Manual (chained)      |
| Before documentation site redesign                  | Manual (auto-suggest) |
| After feature implementation that requires new docs | Manual (chained)      |

## Required Permissions

The calling agent must have these tools available:

| Tool     | Required | Scope            | Purpose                                                                   |
| -------- | -------- | ---------------- | ------------------------------------------------------------------------- |
| read     | Yes      | `project: allow` | Scan documentation files for content analysis                             |
| glob     | Yes      | `project: allow` | Discover documentation file patterns recursively                          |
| grep     | Yes      | `project: allow` | Search for content patterns, headings, cross-references                   |
| edit     | No       | —                | Never modifies documentation files                                        |
| write    | No       | —                | Never creates documentation files (output is returned as structured data) |
| delegate | No       | —                | Never delegates; self-contained analysis                                  |

No network access is required. All analysis is local and heuristic-based.

## Input

| Parameter          | Type              | Default                                                             | Description                                       |
| ------------------ | ----------------- | ------------------------------------------------------------------- | ------------------------------------------------- |
| `doc_root`         | string            | `"docs/"`                                                           | Directory to scan for documentation files         |
| `file_list`        | array (optional)  | `[]`                                                                | Specific files to audit, bypassing discovery scan |
| `output_path`      | string (optional) | `"docs/plan/"`                                                      | Where to write the documentation plan             |
| `exclude_patterns` | array (optional)  | `["node_modules/**", "build/**", "_site/**", ".vitepress/dist/**"]` | Glob patterns to exclude from scanning            |

`doc_root` MUST be validated to exist before scanning. If `file_list` is provided, skip discovery and classify only those files.

`exclude_patterns` are expanded using `glob` with the patterns appended. Default exclusions cover common build and dependency directories.

## Workflow Steps

### Step 1: Discover documentation files

1. Validate `doc_root` exists. If not, abort with error: `"Documentation root {path} does not exist"`.
2. Recursively glob for documentation files: `**/*.md`, `**/*.qmd`, `**/*.rst`, `**/*.ipynb`.
3. Apply `exclude_patterns` to filter out build artifacts and dependencies.
4. If `file_list` is provided, use it directly — skip discovery glob.
5. Build a file inventory. For each file record:
   - `path` — relative path from doc root
   - `file_type` — extension (`.md`, `.qmd`, `.rst`, `.ipynb`)
   - `content` — full text content (read from file)
   - `heading_structure` — extracted markdown headings (`#`, `##`, `###`)
   - `word_count` — approximate word count

### Step 2: Classify content by Diataxis quadrants

For each file, classify its primary and secondary quadrants using both path heuristics and content signals:

**Path heuristics** — directory names provide strong quadrant signals:

| Directory Pattern                                           | Expected Quadrant |
| ----------------------------------------------------------- | ----------------- |
| `tutorials/`, `tutorial/`, `getting-started/`               | tutorial          |
| `how-to/`, `howto/`, `guides/`                              | how-to            |
| `reference/`, `ref/`, `api/`, `specs/`                      | reference         |
| `explanation/`, `concepts/`, `background/`, `architecture/` | explanation       |

**Content signals** — heading and body text classify by keyword matching:

| Quadrant         | Signal Patterns                                                                                                                  |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **Tutorial**     | "Getting started", "Quickstart", step-by-step numbered lists, prerequisites, "Create a", "Build a", walkthrough, beginner guides |
| **How-to guide** | "How to", "Configure", "Set up", "Deploy", imperative headings, specific goals, integration recipes                              |
| **Reference**    | API docs, CLI flags, config keys, type definitions, parameter tables, auto-generated docs, schema                                |
| **Explanation**  | "Background", "Why", "Architecture", "Design", "Concepts", "Under the hood", ADRs, conceptual overviews                          |

**Classification algorithm:**

1. Score each quadrant by counting matching keywords in headings and body text.
2. Use path heuristics as a tiebreaker (directory name matches expected quadrant).
3. If a file has `README.md` as its name and no strong content signals, classify as `other`.
4. Record both the `detected_quadrant` (content-based) and `expected_quadrant` (path-based) for later misclassification detection.

Files with mixed signals are flagged with an `ambiguity` warning. The classification is always recorded as the best-guess quadrant.

### Step 3: Analyse gaps

Compare the classified content against the ideal Diataxis model. Produce a gap matrix:

| Quadrant      | Files Found | Coverage Assessment                         | Gap Severity                     |
| ------------- | ----------- | ------------------------------------------- | -------------------------------- |
| Tutorials     | count       | Well-covered / Adequate / Minimal / Missing | None / Low / Moderate / Critical |
| How-to Guides | count       | Well-covered / Adequate / Minimal / Missing | None / Low / Moderate / Critical |
| Reference     | count       | Well-covered / Adequate / Minimal / Missing | None / Low / Moderate / Critical |
| Explanation   | count       | Well-covered / Adequate / Minimal / Missing | None / Low / Moderate / Critical |

**Coverage assessment rules:**

- **Missing** — zero files for the quadrant → severity: **Critical**
- **Minimal** — 1 file, or files cover only a subset of expected topics → severity: **Moderate**
- **Adequate** — 2-3 files covering core topics → severity: **Low** (or **None** if complete)
- **Well-covered** — 4+ files or comprehensive coverage → severity: **None**

**Severity scale:**

- **Critical**: Quadrant is empty — users cannot learn, accomplish tasks, look up facts, or understand rationale.
- **Moderate**: Quadrant has content but major topics are undocumented.
- **Low**: Quadrant has coverage but minor gaps exist.
- **None**: Quadrant is well-covered.

For each gap, identify specific missing topics based on the project domain (e.g., "missing deployment guide" for a how-to gap on a web app).

### Step 4: Detect misclassified content

Flag files whose detected quadrant (from content analysis) differs from their expected quadrant (from path/location).

For each misclassification, record:

- `file` — path to the misclassified file
- `detected_quadrant` — what the content analysis determined
- `expected_quadrant` — what the path/location suggests
- `recommendation` — one of: `move`, `rename`, `split`, or `restructure`

**Examples of misclassifications:**

- A file in `tutorials/` that is actually a reference table → recommend `move`
- A file named `api-install.md` in reference section with step-by-step instructions → detected `how-to`, expected `reference`
- A "Getting Started" page that reads like architecture explanation → detected `explanation`, expected `tutorial`

Files classified as `other` (README, CHANGELOG, license files) are never flagged as misclassified.

### Step 5: Generate documentation plan

Assemble all analysis results into a structured YAML plan. The plan includes:

1. **Executive summary** — overall health of the documentation set.
2. **Classification matrix** — each file mapped to its primary quadrant.
3. **Gap analysis** — missing quadrants with severity and specific missing topics.
4. **Misclassification report** — files in wrong locations with move/split recommendations.
5. **Cross-reference analysis** — whether pages link to related content across quadrants.
6. **Recommended structure** — proposed directory layout consistent with Diataxis.
7. **Prioritised recommendations** — ordered by impact (critical gaps first), each with an action (create, move, split, restructure) and rationale.

## Output Format

```yaml
audit:
  root: "docs/"
  total_files: 24
  date: "2026-07-12"

executive_summary: >
  The documentation set covers all four Diataxis quadrants but has gaps
  in tutorial and reference sections. Two files are misclassified.

classification:
  tutorials:
    files:
      - path: "docs/tutorials/getting-started.md"
        quadrant: tutorial
        confidence: high
      - path: "docs/tutorials/first-app.md"
        quadrant: tutorial
        confidence: high
    coverage: minimal
    missing:
      - "Beginner tutorial for core workflow"
      - "Environment setup tutorial"
  how_to:
    files:
      - path: "docs/how-to/deploy.md"
        quadrant: how-to
        confidence: high
    coverage: adequate
    missing: []
  reference:
    files:
      - path: "docs/reference/api.md"
        quadrant: reference
        confidence: high
    coverage: minimal
    missing:
      - "CLI reference"
      - "Configuration reference"
  explanation:
    files:
      - path: "docs/explanation/architecture.md"
        quadrant: explanation
        confidence: high
    coverage: partial
    missing:
      - "Conceptual overview of the system"

gaps:
  - quadrant: tutorials
    severity: critical
    assessment: "No tutorial content found — users cannot learn the basics."
  - quadrant: reference
    severity: moderate
    assessment: "Only API reference exists. CLI and config reference are missing."

misclassified:
  - file: "docs/tutorials/api-install.md"
    detected_quadrant: reference
    expected_quadrant: how-to
    recommendation: "Move to docs/how-to/install.md"
  - file: "docs/reference/overview.md"
    detected_quadrant: explanation
    expected_quadrant: reference
    recommendation: "Split into docs/explanation/overview.md and docs/reference/config.md"

cross_references:
  status: "missing" # "present" | "partial" | "missing"
  isolated_files:
    - "docs/tutorials/getting-started.md"

frontmatter:
  present: true # whether files consistently have YAML frontmatter

extra_files_in_root:
  - "CHANGELOG.md"
  - "CONTRIBUTING.md"

recommended_structure:
  - "docs/"
  - "docs/tutorials/"
  - "docs/how-to/"
  - "docs/reference/"
  - "docs/explanation/"
  - "docs/README.md"

prioritised_recommendations:
  - priority: 1
    action: "create"
    target: "tutorials"
    description: "Write a getting-started tutorial and a beginner walkthrough."
    rationale: "Critical gap — no tutorial content exists."
  - priority: 2
    action: "move"
    target: "docs/tutorials/api-install.md"
    description: "Move how-to content to docs/how-to/install.md"
    rationale: "Misclassified as tutorial but contains imperative installation steps."
```

| Field                         | Type   | Always Present | Description                                                    |
| ----------------------------- | ------ | -------------- | -------------------------------------------------------------- |
| `audit`                       | object | yes            | Metadata: root path, file count, audit date                    |
| `executive_summary`           | string | yes            | Human-readable summary of overall doc health                   |
| `classification`              | object | yes            | Per-quadrant map of files with coverage and missing topics     |
| `gaps`                        | array  | yes            | List of gaps with severity and assessment                      |
| `misclassified`               | array  | yes            | List of misclassified files with detected/expected quadrants   |
| `cross_references`            | object | yes            | Cross-reference analysis with status and isolated files        |
| `frontmatter`                 | object | yes            | Whether YAML frontmatter is consistently present               |
| `extra_files_in_root`         | array  | yes            | Non-doc files found at the doc root (CHANGELOG, LICENSE, etc.) |
| `recommended_structure`       | array  | yes            | Proposed directory layout                                      |
| `prioritised_recommendations` | array  | yes            | Ordered list of actionable recommendations                     |

## Chained Skills

| Skill              | Condition                                                       | After Step                |
| ------------------ | --------------------------------------------------------------- | ------------------------- |
| `rs-issue-to-plan` | Doc audit is part of a feature implementation plan              | Before Step 1             |
| `rs-consult`       | Diataxis classification needs domain expertise or clarification | Between Step 2 and Step 3 |

The full plan YAML from this skill is passed as context when loading the chained skill.

## Error Handling

### Documentation Root Not Found

If `doc_root` does not exist on disk, abort with:

```
error: "Documentation root '{path}' does not exist"
suggestion: "Create the directory or specify an existing doc_root"
```

### No Documentation Files Found

If `doc_root` exists but contains no supported documentation files (`.md`, `.qmd`, `.rst`, `.ipynb`), produce a minimal report:

- `total_files: 0`
- All quadrants set to `coverage: missing` with severity `critical`
- `executive_summary`: "No documentation files found in {path}."
- Recommendation: "Create initial documentation structure following Diataxis quadrants."

### Empty File List

If `file_list` is provided but empty (`[]`), treat it the same as not provided — fall back to discovery scan.

## See Also

- `rs-discover` — codebase scanner, useful before first doc audit
- `rs-issue-to-plan` — converts documentation audit gaps into implementation plans
- `rs-consult` — domain expertise for classification ambiguity
- [Diataxis framework](https://diataxis.fr/) — The four-quadrant documentation model
- `rs-changelog-manager` — companion skill for CHANGELOG documentation

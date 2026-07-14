---
title: "Dependency Checker Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - skills
  - dependency-checker
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
  - knowledge: "knowledge/tooling/opencode/skills/dependency-checker.md"
references:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Dependency Checker Skill Design

## Context

The `@runicengines/opencode-runesmith` plugin provides OpenCode agents with RunicEngines-specific skill workflows. The `rs-dependency-checker` skill is a **utility skill** — it performs a single, well-defined function (scanning dependencies) and can be invoked standalone or chained into broader workflows like release preparation or maintenance audits.

This file is a research analysis: it documents the skill's design requirements, its recommended instruction body, and maps the relationship between the existing Knowledge Base `dependency-checker` skill at `knowledge/tooling/opencode/skills/dependency-checker.md` and this RunicEngines-specific variant.

### Why a Plugin-Specific Skill?

The existing KB `dependency-checker` skill (at `knowledge/tooling/opencode/skills/dependency-checker.md`) is a generic template covering basic audit tool invocation. The `rs-dependency-checker` skill extends this with:

- **Multi-ecosystem orchestration** — detecting and auditing across Python, JavaScript, Rust, and other ecosystems in a single invocation
- **Structured vulnerability reporting** — consistent JSON-like output regardless of underlying package manager
- **Fix recommendation engine** — not just listing outdated packages, but suggesting specific semver-safe update commands
- **Chainable output** — producing a report that other skills (e.g., `rs-changelog-manager`) can consume for release notes

### Skill Identity

| Property | Value |
|---|---|
| Plugin | `@runicengines/opencode-runesmith` |
| Skill name | `rs-dependency-checker` |
| Skill prefix | `rs-` |
| Loading model | On-demand (via `skill({ name: "rs-dependency-checker" })`) |
| Primary user | DevOps agent |
| Secondary user | Developer agent |
| Trigger | Before deployment, when updating dependencies, or on regular schedule |

---

## Recommended SKILL.md Instructions

The following block is the recommended instruction body for the skill's `SKILL.md` file. It follows the utility skill conventions: it declares trigger conditions, required permissions, input requirements, a step-by-step workflow, per-ecosystem commands, and output format.

```markdown
---
name: rs-dependency-checker
description: >
  Scan project dependencies for known vulnerabilities and outdated packages
  across multiple ecosystems. Produces a structured report with severities,
  fix versions, and recommended update commands.
license: MIT
compatibility: opencode
metadata:
  workflow: maintenance
  audience: devops
  trigger: manual+automatic
---

# rs-dependency-checker

## Purpose

Checks project dependencies for known vulnerabilities and identifies
outdated packages with suggested updates. Works with multiple package
ecosystems and produces a structured vulnerability report.

## When to Invoke

- The user says "check dependencies", "audit packages", or "any vulnerabilities?"
- Before a deployment or release cut
- As part of a scheduled maintenance workflow
- When a Dependabot or Snyk alert is received

## Trigger

| Condition | Type |
|---|---|
| User requests dependency audit | Manual |
| Pre-deployment gate | Automatic (chained from release workflow) |
| Scheduled cron / CI maintenance job | Automatic |
| Chained from `rs-changelog-manager` before release | Chained skill |

## Required Permissions

| Permission | Purpose |
|---|---|
| `bash: { "npm *": "allow", "bun *": "allow", "cargo *": "allow", "pip *": "allow", "poetry *": "allow", "safety *": "allow" }` | Run package manager audit commands |
| `read` | Read manifest files (package.json, Cargo.toml, pyproject.toml, etc.) |
| `glob` | Locate all manifest files across the workspace |
| `webfetch` | Optional — fetch advisory details from OSV or GitHub Advisory DB |

## Input

The skill accepts an optional scope parameter:

- **Full audit (default)**: Scans every dependency file found in the project.
- **Scoped audit**: `--ecosystem npm` — restrict to a single ecosystem.
- **Path filter**: `--path frontend/` — restrict scanning to a subdirectory.

If no scope is provided, the skill discovers all dependency files
recursively from the project root.

## Workflow Steps

### Step 1: Detect dependency files

1. Use `glob` to find all known manifest file patterns:
   - `package.json` (npm, bun)
   - `bun.lock`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - `Cargo.toml`, `Cargo.lock`
   - `pyproject.toml`, `requirements.txt`, `Pipfile`, `Pipfile.lock`
   - `poetry.lock`
   - `Gemfile`, `Gemfile.lock`
   - `go.mod`, `go.sum`
2. Group files by ecosystem.
3. Choose the appropriate package manager:
   - If `bun.lock` exists, prefer `bun` over `npm`.
   - If `poetry.lock` exists, prefer `poetry` over `pip`.
4. If no dependency files are found, abort with a clear message.

### Step 2: Run audit commands per ecosystem

Execute the relevant audit command for each detected ecosystem.
Collect stdout and stderr. If a command fails (non-zero exit), capture
the error message and continue with other ecosystems — do not abort.

### Step 3: Parse results into a uniform structure

Normalize each ecosystem's output into the following schema:

```json
{
  "ecosystem": "npm",
  "manifest": "package.json",
  "vulnerabilities": [
    {
      "package": "lodash",
      "current_version": "4.17.20",
      "severity": "critical",
      "type": "Prototype Pollution",
      "cve": "CVE-2024-XXXX",
      "fix_version": "4.17.21",
      "status": "fix_available"
    }
  ],
  "outdated": [
    {
      "package": "express",
      "current": "4.17.1",
      "latest": "4.19.2",
      "wanted": "4.17.3",
      "status": "outdated"
    }
  ],
  "errors": []
}
```

### Step 4: Check for outdated packages

For each ecosystem, run the relevant outdated check command.
Parse the output to extract package name, current version, wanted
version, and latest version. Merge this with the vulnerability data.

### Step 5: Generate report

Assemble the findings into the structured output format defined below.
If vulnerabilities are found, include a recommendation for each:

- **update**: A semver-compatible upgrade is available.
- **pin**: No fix is available; pin to current version and add a note
  for manual review.
- **ignore**: False positive or dev-only dependency with negligible
  risk (require user confirmation).

### Step 6: Optional — propose batch update

If the user requests it or if `--apply` is passed, generate and display
a batch update command sequence:

```
npm install lodash@4.17.21 express@4.19.2
poetry update requests
cargo update
```

Do not execute update commands automatically unless the user explicitly
confirms. Always present the proposed changes first.

## Commands by Ecosystem

| Ecosystem | Audit command | Outdated check | Manifest file |
|---|---|---|---|
| Python (pip) | `pip-audit` or `safety check` | `pip list --outdated` | `requirements.txt` |
| Python (poetry) | `poetry audit` | `poetry show --outdated` | `pyproject.toml` |
| Python (pipenv) | `pipenv check` | `pipenv update --outdated` | `Pipfile` |
| npm/node | `npm audit --json` | `npm outdated --json` | `package.json` |
| Bun | `bun audit` | `bun outdated` | `package.json` |
| Rust/Cargo | `cargo audit` | `cargo outdated` | `Cargo.toml` |
| Go | `govulncheck ./...` | `go list -u -m all` | `go.mod` |
| Ruby/Bundler | `bundler-audit` | `bundle outdated` | `Gemfile` |

## Output Format

The skill outputs a structured vulnerability report as Markdown:

```markdown
# Dependency Audit Report
**Date:** 2026-06-07
**Scope:** Full project

## Summary
- **Total vulnerabilities:** 3
- **Outdated packages:** 7
- **Ecosystems scanned:** npm, cargo, poetry

## Vulnerabilities (by severity)

### Critical
| Package | Current | Fix | CVE | Advisory |
|---|---|---|---|---|
| lodash | 4.17.20 | 4.17.21 | CVE-2024-XXXX | [link](...) |

### High
...

### Medium / Low
...

## Outdated Packages
| Ecosystem | Package | Current | Latest | Command |
|---|---|---|---|---|
| npm | express | 4.17.1 | 4.19.2 | `npm install express@4.19.2` |
| cargo | serde | 1.0.150 | 1.0.200 | `cargo update -p serde` |

## Recommendations
1. Update lodash from 4.17.20 to 4.17.21 (semver-patch, safe)
2. Update express from 4.17.1 to 4.19.2 (semver-minor, review changelog)
3. Pin `deprecated-lib` at 1.2.3 — no fix available, scheduled for removal

## Errors (non-fatal)
- `cargo audit` not installed — skipping Rust audit
```

## Chained Skills

| Skill | Condition | Step |
|---|---|---|
| `rs-changelog-manager` | If dependency updates were applied | After Step 6 — update changelog |
| `rs-pr-packager` | If updates create a new branch | After updates are applied |
| `gh` | If user wants to create a PR for updates | Optional, after pr-packager |

## See Also

- [OpenCode Skills Documentation](https://opencode.ai/docs/skills)
- [OSV.dev](https://osv.dev) — Open Source Vulnerabilities database
- [GitHub Advisory Database](https://github.com/advisories)
- [pip-audit](https://github.com/pypa/pip-audit)
- [cargo-audit](https://github.com/rustsec/cargo-audit)
- [npm-audit](https://docs.npmjs.com/cli/v10/commands/npm-audit)
```

---

## Differences from the KB `dependency-checker` Skill

| Dimension | KB `dependency-checker` | `rs-dependency-checker` |
|---|---|---|
| Target repo | Knowledge base repos (generic) | Code repos (RunicEngines) |
| Multi-ecosystem | Mentioned but not orchestrated | Full orchestration: detect → audit → report |
| Output format | Free-form description | Structured Markdown with tables and JSON schema |
| Fix recommendations | Not covered | Update commands with semver-aware analysis |
| Chainable output | None | Designed for consumption by `rs-changelog-manager`, `rs-pr-packager` |
| Audit command table | Not present | Full command matrix per ecosystem |
| Permission model | Generic (`bash`, `read`, `glob`) | Granular (`bash: { "npm *": "allow", ... }) |
| Error handling | Not specified | Continue on per-ecosystem failure; report errors separately |

## Risk Assessment

**Missing tooling.** `cargo audit`, `pip-audit`, and `bundler-audit` are not always pre-installed. The skill must detect missing tools and report which ecosystems were skipped rather than failing entirely. A pre-flight check at Step 1 should verify each tool's availability.

**False positives in advisory databases.** Vulnerability databases (OSV, NVD, npm audit) occasionally report false positives — especially for transitive dependencies or dev-only packages. The skill should mark dev dependencies separately and include an `ignore` mechanism with user-confirmation required.

**Lockfile staleness.** If `npm install` or `poetry lock` has not been run recently, the lockfile may not reflect `package.json`. The skill should detect mismatches and warn the user to sync before auditing.

**Large monorepos.** A monorepo with dozens of packages may produce a very long report. The skill should support `--ecosystem` and `--path` filters so users can scope audits to relevant subsets. It should also group findings by sub-package for clarity.

## Recommendations

1. **Implement a pre-flight check.** Before running any audit, verify that required tools (`npm`, `cargo`, `pip-audit`, etc.) are installed and reachable via `which` or `command -v`. Report missing tools as warnings, not errors.

2. **Add a `--json` output flag.** For programmatic consumption (CI pipelines, other agents), the skill should optionally output the report as JSON using the normalized schema defined in Step 3.

3. **Support `.opencode/audit-ignore`.** An ignore file listing packages + CVE patterns that the team has reviewed and accepted as safe. The skill should parse this file and automatically set ignored findings to `status: ignored` with a reference to the review date.

4. **Integrate with Dependabot / Renovate.** If the project uses Dependabot or Renovate, the skill should check for existing open update PRs and avoid duplicating their work. It should note any PRs that are already in progress.

5. **Cache advisory lookups.** `webfetch` calls to OSV or NVD can be rate-limited. The skill should cache results within a session and, for repeated runs, consider a local cache file (e.g., `.opencode/advisory-cache.json`).

---

## See Also

- [Knowledge: Dependency Checker (KB variant)](/knowledge/tooling/opencode/skills/dependency-checker/) — The existing KB generic dependency-checker skill
- [Knowledge: OpenCode Skills Overview](/knowledge/tooling/opencode/skills/overview/) — OpenCode skill system reference
- [Knowledge: Workflow Skill Patterns](/knowledge/tooling/opencode/skills/workflow-patterns/) — Cross-cutting workflow conventions in the KB
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills) — OpenCode's official docs
- [OSV.dev](https://osv.dev) — Open Source Vulnerabilities database
- [GitHub Advisory Database](https://github.com/advisories)

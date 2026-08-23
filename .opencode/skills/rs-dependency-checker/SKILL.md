---
name: rs-dependency-checker
description: >
  Audit project dependencies across multiple ecosystems:
  scan manifests, detect known CVEs, flag outdated packages,
  validate open-source licenses, and generate structured
  compliance reports for Node.js, Python, Rust, Go, and Ruby projects.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: utility
  audience: developers, tech-writer, devops
  trigger: manual+chained
---

## Purpose

Scans project dependency manifests for known vulnerabilities, stale or
unpinned packages, missing lockfiles, and license compliance issues.
Supports npm, pip, Poetry, uv, Cargo, Go modules, and Bundler ecosystems.
Runs per-ecosystem audit tools, compares pinned versions against
latest releases, checks SPDX license identifiers, and produces a
structured text report with findings, severity, and remediation
guidance.

## When to Invoke

Trigger `rs-dependency-checker` when:

- Auditing a project's dependency health before a release.
- Checking for known CVEs in third-party dependencies.
- Validating that open-source licenses are compatible with project policy.
- Reviewing a PR that adds or updates dependencies.
- Integrating into a CI pipeline for continuous compliance.
- Onboarding a new codebase and assessing its dependency hygiene.

Do NOT invoke when:

- The project has no dependency manifests (no package manager in use).
- Operating in an offline environment without cached advisories.
- The agent lacks bash access (audit tools require shell execution).

## Workflow Steps

### Step 1 — Detect manifests

Scan the project tree for supported dependency manifests:

| Ecosystem | Manifests                       | Audit tool         |
| --------- | ------------------------------- | ------------------ |
| npm       | `package.json`                  | `npm audit`        |
| pip       | `requirements.txt`              | `pip-audit`        |
| Poetry    | `pyproject.toml`, `poetry.lock` | `poetry audit`     |
| Cargo     | `Cargo.toml`                    | `cargo audit`      |
| Go        | `go.mod`                        | `govulncheck`      |
| uv        | `pyproject.toml`, `uv.lock`     | `uv run pip-audit` |
| Bundler   | `Gemfile`                       | `bundler-audit`    |

Note: `pyproject.toml` can belong to pip, Poetry, or uv — distinguish by lockfile presence (`uv.lock` → uv, `poetry.lock` → Poetry, none → pip).

Also detect workspace/monorepo structures — `package.json` with
`"workspaces"` key, Cargo workspaces, or Poetry multi-package layouts.

For each detected manifest, record:

- Relative path from project root.
- Ecosystem.
- List of declared dependencies (name, version constraint, type).

### Step 2 — Pre-flight tool verification

Check that the required audit tool is available for each detected
ecosystem (see the table in Step 1 for the tool per ecosystem):

If a tool is missing, log the gap and continue with available tools.
Never fail the entire audit because one ecosystem's tool is absent.

All paths used in shell commands must be validated — use shlex.quote()
or subprocess.run() without shell=True to prevent command injection.

### Step 3 — Run per-ecosystem audit

Execute each available audit tool and collect output. For each
ecosystem:

1. Run the audit command with a short timeout (60s default).
2. Parse stdout/stderr for vulnerability entries.
3. Extract for each finding: package name, installed version,
   CVE identifier (if any), severity (critical/high/medium/low),
   and recommended fix version.
4. Cache results keyed by ecosystem and manifest path to avoid
   redundant runs in monorepo layouts.

### Step 4 — Check outdated packages

Compare pinned versions against latest available releases:

1. For npm: `npm outdated --json`.
2. For pip: `pip list --outdated --format=json`.
3. For Cargo: `cargo outdated` (if installed) or parse index.
4. For uv: `uv pip list --outdated`.
5. For Go: `go list -u -m all`.
6. For each outdated entry, record: package, current version,
   latest version, and ecosystem.

If the lockfile is missing for an ecosystem, emit a **staleness
warning**: without a lockfile the exact resolved tree cannot be
verified, and the project is vulnerable to supply-chain drift.

### Step 5 — License scan

Parse `package.json`, `Cargo.toml`, `pyproject.toml`, etc. for
SPDX license identifiers. For each dependency:

1. Check the manifest's `license` or `license-expression` field.
2. If missing, note it as a license gap.
3. If present, validate against the SPDX License List.
4. Flag incompatible licenses based on `LICENSE_POLICY` environment
   variable (defaults: allow MIT, Apache-2.0, BSD-2-Clause,
   BSD-3-Clause, ISC, Unlicense; flag GPL-3.0, AGPL-3.0, SSPL).

### Step 6 — Generate structured report

Output findings as comma-separated text lines per ecosystem.

Example output for a project with one CVE and one outdated package:

```
express@4.17.1, CVE-2023-1234, severity: high, fix available: express@4.18.2, runtime dependency, npm ecosystem, licenses: MIT, BSD-3-Clause, vuln detected
requests==2.25.1 outdated, latest 2.31.0, pip ecosystem, update recommended
lockfiles missing, staleness warning, lockfile recommendation
```

If no findings exist, produce a clean bill-of-health message per ecosystem.

## Output Format

The skill returns a flat, comma-separated text report string. Findings
are grouped by type (CVE, outdated, license, warning) with human-readable
prefixes. If no issues are found, each ecosystem receives a clean
bill-of-health entry. The format is designed for deterministic keyword
evaluation against expected-output keyword lists.

## Security Features

- **`.opencode/audit-ignore`**: Create this file to suppress known
  false-positive CVEs. One CVE ID per line. Entries are excluded from
  the `findings` array and logged in `warnings`.
- **Advisory cache**: Declares `.runesmith/cache/` as a **global shared cache** at the project level (shared across all sessions, avoids re-downloading vulnerability data). CVE lookups are cached under `.runesmith/cache/advisories/` with a 1-hour TTL to reduce network calls and enable offline replay. **Note**: `rs-scratchpad clear` does NOT touch this directory because it lives outside session scope (session data lives under `.runesmith/{date}-{sanitized-branch}/`).
- **Cache directory convention**: global caches that should be shared across sessions (like advisory databases, tool indexes, npm/pip package caches) live under `.runesmith/cache/` at the project root. Session-scoped data (like intermediate build artifacts, per-branch test results, temporary reports) lives under `.runesmith/{date}-{sanitized-branch}/cache/`, managed by `rs-scratchpad`. The global `.runesmith/cache/` directory is NOT session-scoped and is preserved when `rs-scratchpad clear` is invoked.

## Required Permissions

- `read` — to inspect manifests and lockfiles.
- `bash` — to execute audit tools (`npm audit`, `pip-audit`, etc.).
- `glob` — to discover manifests across the project tree.

## See Also

- `rs-scratchpad` — manages session-scoped scratchpads with a `cache/` subdirectory for per-session data (distinct from the global `.runesmith/cache/` used by this skill).
- `rs-discover` — project structure scanner for initial context.
- `.opencode/audit-ignore` — false-positive suppression file.

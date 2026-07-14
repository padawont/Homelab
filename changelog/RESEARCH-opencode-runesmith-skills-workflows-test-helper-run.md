---
title: "Test Helper Run Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - skills
  - test-helper
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
  - knowledge: "knowledge/tooling/opencode/skills/workflow-patterns.md"
references:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
  - url: "https://docs.pytest.org/en/stable/"
    title: "pytest Documentation"
  - url: "https://bun.sh/docs/test"
    title: "Bun Test Runner Documentation"
  - url: "https://doc.rust-lang.org/cargo/commands/cargo-test.html"
    title: "Cargo Test Documentation"
  - url: "https://www.gnu.org/software/make/manual/make.html"
    title: "GNU Make Manual"
last_audit_date: 2026-06-07
---

# Test Helper Run Skill Design

## Context

The `@runicengines/opencode-runesmith` plugin provides OpenCode agents with RunicEngines-specific skill workflows. The `rs-test-helper-run` skill is a **workflow skill** — it automates test suite execution, detects the project's test framework, runs the appropriate command, and captures results into a structured JSON summary. It is the execution half of a two-skill test workflow; the companion skill `rs-test-helper-diagnose` interprets the failures and suggests fixes.

This file is a research analysis: it documents the skill's design requirements, its recommended instruction body, and maps how it fits into the broader test-helper workflow for RunicEngines agents.

### Why a Dedicated Skill?

Running tests sounds simple — `pytest` or `bun test` — but in an agentic context the nuances matter. The agent must detect which framework is in use, pick the right command-line flags, capture structured output across different frameworks with inconsistent output formats, and produce a machine-readable result the next skill in the chain can consume. Hard-coding this logic into the test-writer agent's prompt would bloat it and make it non-reusable across different project types. A dedicated skill keeps the logic encapsulated, testable, and shareable between the test-writer agent and the developer agent.

### Skill Identity

| Property | Value |
|---|---|
| Plugin | `@runicengines/opencode-runesmith` |
| Skill name | `rs-test-helper-run` |
| Skill prefix | `rs-` |
| Loading model | On-demand (via `skill({ name: "rs-test-helper-run" })`) |
| Primary user | Test-writer agent |
| Secondary user | Developer agent (diagnosing failures) |
| Trigger | After tests are written, or when diagnosing existing failures |

---

## Recommended SKILL.md Instructions

The following block is the recommended instruction body for the skill's `SKILL.md` file. It follows the workflow skill conventions defined in `knowledge/tooling/opencode/skills/workflow-patterns.md`: it declares trigger conditions, required permissions, framework detection logic, a step-by-step workflow, output format, chained skills, and error handling.

```markdown
---
name: rs-test-helper-run
description: >
  Detect the project's test framework, run the full test suite (or a
  filtered subset), and return a structured JSON summary with pass/fail
  counts, error details, and runtime. Designed to feed results into
  rs-test-helper-diagnose for failure interpretation.
license: MIT
compatibility: opencode
metadata:
  workflow: testing
  audience: agents
  trigger: manual+chained
---

# rs-test-helper-run

## Purpose

Runs test suites for the current project, detects the test framework
automatically, collects pass/fail/error/skip counts, and produces a
structured JSON summary. This skill is the **execution** half of the
test-helper workflow. Use `rs-test-helper-diagnose` (loaded separately)
to interpret failures and suggest fixes.

## When to Invoke

- The test-writer agent has just written or modified tests and needs to
  verify they pass.
- The developer agent is diagnosing an existing test failure and needs
  raw results to hand off to `rs-test-helper-diagnose`.
- The user says "run the tests", "check if tests pass", or "run tests
  for <path>".
- A CI check failed and the agent needs to reproduce the failure locally.

## Trigger

| Condition | Type |
|---|---|
| User asks to run tests | Manual |
| After test-writer generates or modifies test files | Automatic (chained from test-writer agent) |
| Before creating a PR (as part of readiness check) | Manual (auto-suggest) |

## Required Permissions

| Permission | Purpose |
|---|---|
| `bash: { "*": "allow" }` | Run test commands (pytest, bun, npm, cargo, make) |
| `read` | Read framework config files (pytest.ini, pyproject.toml, package.json, Cargo.toml, Makefile) |
| `glob` | Discover framework indicator files |

No network access is required. All operations are local to the working
directory.

## Input

The skill accepts an optional **test path or filter**. If provided, only
tests matching that filter are run. If omitted, the full test suite is
executed.

| Parameter | Type | Default | Example |
|---|---|---|---|
| `test_filter` | string (optional) | `""` (run all) | `"tests/test_auth.py::test_login"` |
| `test_path` | string (optional) | `""` (root dir) | `"tests/integration/"` |
| `timeout_seconds` | integer (optional) | `300` (5 min) | `600` |

When both `test_filter` and `test_path` are provided, the framework
receives the path first, then the filter (e.g., `pytest tests/integration/ -k test_login`).

## Framework Detection

Run before any test command. Check for indicator files in order of
specificity. The first match determines the framework.

### Detection Table

| Indicator File | Framework | Command |
|---|---|---|
| `pytest.ini` or `pyproject.toml` with `[tool.pytest]` section | pytest | `python -m pytest -v --tb=short <path> <filter>` |
| `package.json` with `"scripts": {"test": "..."}` entry | npm/bun | `bun test <path>` (if `bun.lockb` present) or `npm test -- <path>` |
| `Makefile` with a `test` target | make | `make test` |
| `Cargo.toml` | Rust (cargo) | `cargo test <filter>` |

**Detection logic:**

1. **pytest**: Look for `pytest.ini` or `pyproject.toml` containing
   `[tool.pytest]`. Parse `pyproject.toml` with a simple key search —
   do not require a full TOML parser. If found, use `python -m pytest -v --tb=short`.
   Append `-k <filter>` if a test filter is provided.
2. **npm/bun**: Look for `package.json`. If `bun.lockb` exists in the
   same directory, prefer `bun test`. Otherwise use `npm test`.
   If `scripts.test` in `package.json` exists but is a custom command,
   run it as-is rather than overriding with `bun test` or `npm test`.
3. **make**: Look for a `Makefile` containing a `test:` target. Run
   `make test` as-is — do not append flags or filters, since Makefile
   conventions vary. Prefer this only when no more specific framework
   is detected.
4. **cargo**: Look for `Cargo.toml`. Run `cargo test`. Append the test
   filter as a positional argument (`cargo test <filter>`). `cargo test`
   natively supports filtering by test name.

**Fallback**: If no indicator file is found, emit a warning and attempt
`python -m pytest -v --tb=short` as a reasonable default for Python
projects. If that fails, report that the test framework could not be
detected and suggest the user specify one.

## Workflow Steps

### Step 1: Detect framework

1. Scan the project root for indicator files using `glob`.
2. Match against the detection table in order.
3. If a framework is detected, note the resolved command and framework
   name for the output JSON.
4. If no framework is detected, try the pytest fallback. If that also
   fails, abort with an error listing what was checked.

### Step 2: Resolve the test command

Build the concrete command string based on the detected framework:

- **pytest**: `python -m pytest -v --tb=short <test_path> -k <test_filter>`
  (omit `-k` and `<test_filter>` if no filter given; omit `<test_path>` if none given)
- **bun**: `bun test <test_path>` (filter via environment or native
  `--filter` if bun supports it; otherwise omit)
- **npm**: `npm test -- <test_path> <test_filter>` (pass-through)
- **make**: `make test` (no additional flags)
- **cargo**: `cargo test <test_filter> -- <test_path>` (cargo test
  accepts filter as first positional arg; path goes after `--`)

Print the resolved command to stdout for debugging transparency.

### Step 3: Run tests with timeout

1. Execute the resolved command via `bash`.
2. Use the specified `timeout_seconds` (default 300). If the command
   exceeds the timeout, kill the process and report a timeout error.
3. Capture **stdout**, **stderr**, and **exit code** separately.
4. Record the **wall-clock runtime** in seconds (use `date +%s%N` before
   and after, or parse from `time` output).

### Step 4: Parse results into structured format

Parse the captured output into a JSON summary. Parsing strategy varies
by framework:

**pytest output parsing** (most structured):

Scan stdout for the final summary line, which looks like:

```
========================= 15 passed, 3 skipped, 2 failed in 4.23s =========================
```

Use a regex to extract counts:
```
(?P<passed>\d+) passed(?:, (?P<skipped>\d+) skipped)?(?:, (?P<failed>\d+) failed)?(?:, (?P<errors>\d+) error)?
```

Also scan for individual failure blocks. pytest prints failed test names
followed by tracebacks. Collect each failed test name by looking for
lines matching `FAILED <path>::<test_name>` or `ERRORS` sections.

If the exit code is non-zero but the regex finds no failures (e.g.,
segfault, import error), report the raw stderr in the `errors` field.

**bun/npm output parsing**:

`bun test` prints a summary of the form:

```
[0.23ms] ✓ test_name_1
[0.15ms] ✓ test_name_2
[0.30ms] ✗ test_name_3

  x expect(received).toBe(expected)
  ...
  1 fail
  2 pass
```

Count lines starting with `✓` (pass), `✗` (fail), and extract the
summary line. For `npm test`, output format depends on the test runner
configured in `package.json`; fall back to exit-code-only reporting
with a note that structured parsing is unavailable.

**make output parsing**:

Output format is entirely project-specific. Report exit code only and
capture the raw output as `raw_output`. Do not attempt structured
parsing. Note in the output that `make test` output was not parsed.

**cargo output parsing**:

`cargo test` prints a summary:

```
test result: ok. 12 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

or:

```
test result: FAILED. 10 passed; 2 failed; 0 ignored; 0 measured; 0 filtered out
```

Parse with regex:
```
test result: (?P<result>ok|FAILED)\. (?P<passed>\d+) passed; (?P<failed>\d+) failed
```

Also collect individual test results by scanning for lines matching
`test <name> ... ok` and `test <name> ... FAILED`.

### Step 5: Build and output JSON summary

```json
{
  "framework": "pytest",
  "command": "python -m pytest -v --tb=short",
  "exit_code": 1,
  "runtime_seconds": 4.23,
  "timeout": false,
  "summary": {
    "passed": 15,
    "failed": 2,
    "errors": 0,
    "skipped": 3
  },
  "failures": [
    {
      "test": "tests/test_auth.py::test_login_invalid_password",
      "message": "AssertionError: expected 401 but got 200",
      "file": "tests/test_auth.py",
      "line": 42
    }
  ],
  "errors": [],
  "raw_stdout": "...",
  "raw_stderr": "...",
  "framework_detected_by": "pytest.ini",
  "warnings": [
    "2 tests failed — use rs-test-helper-diagnose to interpret"
  ]
}
```

Fields:

| Field | Type | Always Present | Description |
|---|---|---|---|
| `framework` | string | yes | Detected framework name (`pytest`, `bun`, `npm`, `make`, `cargo`, or `unknown`) |
| `command` | string | yes | The exact command that was executed |
| `exit_code` | integer | yes | Process exit code (0 = all pass, non-zero = failure) |
| `runtime_seconds` | float | yes | Wall-clock execution time |
| `timeout` | boolean | yes | Whether the command was killed due to timeout |
| `summary.passed` | integer | yes | Number of passing tests |
| `summary.failed` | integer | yes | Number of failing tests |
| `summary.errors` | integer | yes | Number of errors (setup/teardown failures, import errors) |
| `summary.skipped` | integer | yes | Number of skipped tests |
| `failures` | array | yes | List of individual failure objects (empty if none) |
| `errors` | array | yes | List of non-test errors (timeout, framework not found, crash) |
| `raw_stdout` | string | yes | Full stdout captured during execution |
| `raw_stderr` | string | yes | Full stderr captured during execution |
| `framework_detected_by` | string | yes | Which indicator file triggered detection |
| `warnings` | array | yes | Human-readable warnings for the agent |

## Error Handling

### Timeout

If the test command exceeds `timeout_seconds`, kill the process with
SIGTERM (then SIGKILL after 5s grace). Set `timeout: true` in the
output JSON. Include the partial stdout/stderr in `raw_stdout` and
`raw_stderr` so the agent can see what ran before the kill.

### Framework Not Found

If no indicator file is detected and the pytest fallback also fails,
set `framework: "unknown"`, set `exit_code: -1`, and add an entry to
`errors` listing every checked indicator file and why it was rejected.

### Compilation or Import Failure

Some test frameworks compile or import code before running tests.
If the exit code is non-zero and the parser found zero test results
(no passed/failed/skipped output at all), treat this as a compilation
or import error:

1. Set `summary.passed: 0`, `summary.failed: 0`.
2. Add the full stderr as the first error entry.
3. Set `warnings: ["Tests did not start — possible compilation or import error"]`.

### Output Truncation

If `raw_stdout` exceeds 100,000 characters, truncate it to the last
50,000 characters (the end contains the summary and failures) and
add a warning: "stdout truncated from N characters".

### Exit Code Zero With Failures

Some test runners exit 0 even when tests fail (e.g., if failure
thresholds are not configured). Always parse output independently
of exit code. If parsed failures > 0, report them regardless of
exit code. Add a warning: "Exit code 0 but parsed N failures —
test runner may not be configured to fail on test failure."

## Chained Skills

| Skill | Condition | Step |
|---|---|---|
| `rs-test-helper-diagnose` | Test failures detected (parsed failed > 0) | After Step 5 |
| `rs-issue-to-plan` | Test failures indicate a missing feature or regression | After diagnosis |

Chained skills are loaded via `skill({ name: "..." })`. The output JSON
from this skill is passed as context when loading `rs-test-helper-diagnose`.
The agent is responsible for routing the `failures` array into the
diagnose skill's input.

```

## Permission Requirements

The test-writer agent (the primary consumer of this skill) needs the following permission configuration to execute the skill's instructions:

```yaml
permission:
  read: allow
  glob: allow
  bash:
    "*": allow
  skill:
    "*": allow
    "rs-*": allow
```

Unlike the `rs-issue-to-plan` skill (which restricts `bash` to `gh *` only), `rs-test-helper-run` needs **full `bash` access** because test commands can involve arbitrary compilers, interpreters, and build tools. The test runner may invoke `gcc`, `rustc`, `node`, `python`, or any other binary on the system. A restricted allow-list would need constant maintenance as frameworks evolve. The risk is mitigated by the skill's narrow trigger — it only runs when the agent explicitly resolves to execute tests — and by the timeout guard that prevents runaway processes.

**No network access is required** for local test execution. If the test framework downloads dependencies during the run (e.g., `cargo test` fetching crates), that is an inherent property of the project, not a capability the skill requests. Agents should have `webfetch` set to `deny` by default for this skill.

---

## Analysis

### Design Decisions

**1. Framework detection over configuration.** The skill discovers the test framework by scanning for indicator files rather than requiring the user or agent to declare it. This follows the principle of least surprise — the agent acts on what is already in the project. The detection table is ordered by specificity (pytest markers are more specific than a bare `Makefile`) to avoid false positives.

**2. Structured JSON output over Markdown.** The skill produces a JSON object rather than a natural-language summary. This is the key design choice that enables the chained skill pattern: `rs-test-helper-diagnose` can parse the `failures` array programmatically without needing to re-parse human text. The JSON schema is consistent across all frameworks, so the consuming skill does not care whether the test runner was pytest or cargo.

**3. Per-framework parsing with shared schema.** Each framework's output format is different (pytest's summary line, cargo's `test result:` line, bun's `✓/✗` glyphs, make's arbitrary output). The skill defines a parser for each framework that normalizes into the shared JSON schema. For frameworks with no structured output (`make`), it gracefully degrades to exit-code-only reporting. This is better than forcing all frameworks into a one-size-fits-all parser that would produce wrong results for custom test runners.

**4. Timeout as a mandatory parameter, not an afterthought.** Test suites can hang indefinitely due to network timeouts, deadlocks, or infinite loops. A hard timeout (default 300s, configurable) prevents the agent from being stuck waiting for a test that will never complete. The captured partial output is preserved so the agent can diagnose the hang.

**5. Separation from diagnosis.** The run skill stops at producing structured results. It does not attempt to interpret failures or suggest fixes — that is the job of `rs-test-helper-diagnose`. This separation keeps each skill focused on one concern, makes them independently testable, and allows the run skill to be reused without pulling in diagnosis logic.

**6. Framework fallback chain.** If `pytest.ini` is absent but `pyproject.toml` has `[tool.pytest]`, the skill still detects pytest. If neither is present but `package.json` exists, it falls to npm/bun. This multi-level detection handles the common case where a project uses a `pyproject.toml`-based configuration but no dedicated `pytest.ini`.

### Interaction Model

The test-helper run skill participates in a two-phase workflow:

```
Test-Writer Agent
  │
  ├── 1. Writes/modifies tests
  │
  └── 2. Loads rs-test-helper-run
        │
        ├── Detects framework ──► Runs tests ──► Parses output
        │
        ├── (all pass) ──► Report success ──► Done
        │
        └── (failures) ──► Loads rs-test-helper-diagnose
                          │
                          └── Interprets failures ──► Suggests fixes
```

The developer agent uses the same skill in a simplified flow:

```
Developer Agent
  │
  └── Loads rs-test-helper-run ──► Gets structured output ──► Shares with user
```

The key insight is that the run skill does not decide what happens next. It produces data. The calling agent (or a chained skill) decides how to act on it. This makes the skill a **pure data producer** in the workflow sense, analogous to how `gh issue view` produces JSON that a planner skill can consume.

### Comparison with Manual Test Execution

| Dimension | Developer running tests manually | Agent using `rs-test-helper-run` |
|---|---|---|
| Framework detection | Implicit (developer knows the project) | Automatic via indicator file scan |
| Command selection | Typed from memory | Resolved from detection table |
| Output parsing | Human reading (scan for FAILED lines) | Regex-based into structured JSON |
| Result format | Terminal scrollback | Consistent JSON schema |
| Timeout handling | Manual Ctrl+C | Automatic kill after threshold |
| Chained consumption | Developer copies failure text into browser | Structured `failures` array passed to next skill |
| Reproducibility | Human recalls the flags | Resolved command is recorded in output |

### Risk Assessment

**False negatives in framework detection.** A project could use a test framework without the standard indicator files — for example, pytest without `pytest.ini` or `pyproject.toml` (running via `setup.cfg` or a custom `conftest.py`). The detection table does not cover `setup.cfg` because it is a legacy format and increasingly rare. If a project uses an undetected framework, the skill falls back to the pytest default, which will fail, producing a "framework not found" error. The user can then specify the framework explicitly. A future iteration could add a prompt step: "Could not auto-detect. Please specify: pytest, bun, npm, cargo, or make."

**bun test output instability.** Bun's test runner output is less stable than pytest's or cargo's — the `✓` and `✗` glyphs and summary line format may change between Bun versions. The parser should be written defensively: count passing/failing lines first, and only fall back to summary regex if line counting fails. If both methods fail, report exit code and raw output only.

**Large test suites and output size.** A test suite with thousands of tests can generate megabytes of stdout. The 100,000-character truncation (keeping the last 50,000) is designed to preserve the summary at the end while discarding the bulk of passing-test lines. This is a reasonable trade-off because the summary and failures are what the agent needs; the full output is rarely useful for decision-making.

**make test is a black box.** There is no way to parse `make test` output generically because every project uses it differently. The skill's degradation to exit-code-only reporting is honest — it does not pretend to understand the output. If a project uses Make as its test runner, the agent should `read` the Makefile's test target to understand what it does.

### Recommendations

1. **Implement `rs-test-helper-run` before `rs-test-helper-diagnose`.** The diagnose skill depends on the structured JSON output format defined here. Build and test the run skill with three frameworks (pytest, bun, cargo) before adding the make fallback or diagnosis.

2. **Write a unit test suite for the parser functions.** Each framework's output parser should be testable in isolation using captured output samples. Store sample output strings (anonymized) in the skill's test directory for regression testing.

3. **Cache the framework detection result.** If the skill is loaded multiple times in the same session (e.g., the test-writer makes incremental changes), re-scanning indicator files is wasteful. Cache the detected framework in the agent's context or a temporary file with a short TTL (60 seconds).

4. **Add a `--list-frameworks` mode.** A future version of the skill should offer a discovery-only mode that lists detected frameworks without running anything. This helps the agent decide whether to offer the user a choice when multiple frameworks are detected (rare, but possible in monorepos).

5. **Consider a `--junit-xml` parsing path.** Most test frameworks support JUnit XML output (`pytest --junitxml=report.xml`, `cargo test -- -J report.xml`). Parsing JUnit XML is more robust than parsing terminal output. A future version could offer an opt-in JUnit XML path that trades command-line complexity for parsing reliability. The JSON output schema would remain the same regardless of parsing strategy.

---

## Integration Points

### With the Test-Writer Agent

The test-writer agent (designed in `research/opencode-runesmith/agents/test-writer.md`) uses `rs-test-helper-run` as its verification loop. After writing or modifying test files, the agent loads this skill to confirm tests pass before declaring the task complete. If tests fail, the agent loads `rs-test-helper-diagnose` to interpret the failure and loops back to editing.

### With the Developer Agent

The developer agent uses this skill when the user asks "run the tests" or when diagnosing a CI failure. The structured JSON output gives the developer agent a clear picture of what passed and what failed without needing to parse terminal output.

### With `rs-test-helper-diagnose`

The two skills share a data contract: the `failures` array in the output JSON. Each failure object contains `test`, `message`, `file`, and `line` — enough information for the diagnose skill to inspect the failing test source, suggest a fix, and optionally re-run. This contract should be documented in both skills and versioned if the schema evolves.

### With CI/CD

The structured JSON output is compatible with CI reporting tools. A future integration could pipe the output into a test-reporting dashboard or annotate a GitHub check run with the failure details.

---

## See Also

- [Knowledge: OpenCode Skills Overview](/knowledge/tooling/opencode/skills/overview/) — OpenCode skill system reference
- [Knowledge: Workflow Skill Patterns](/knowledge/tooling/opencode/skills/workflow-patterns/) — Cross-cutting workflow conventions in the KB
- [Research: Issue-to-Plan Skill](/research/opencode-runesmith/skills/workflows/issue-to-plan/) — Companion workflow skill with similar permission model analysis
- [Research: PR Packager Skill](/research/opencode-runesmith/skills/workflows/pr-packager/) — Another workflow skill using the same research format
- [pytest Documentation](https://docs.pytest.org/en/stable/) — pytest CLI flags and output format reference
- [Bun Test Runner Documentation](https://bun.sh/docs/cli/test) — bun test CLI reference
- [Cargo Test Documentation](https://doc.rust-lang.org/cargo/commands/cargo-test.html) — cargo test CLI reference

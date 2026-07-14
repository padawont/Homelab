---
title: "Test Helper Diagnose Skill Design"
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
last_audit_date: 2026-06-07
---

# Test Helper Diagnose Skill Design

This document analyses the **test-helper-diagnose skill** (`rs-test-helper-diagnose`) for `@runicengines/opencode-runesmith`. The skill interprets test runner failures, groups them by root cause, and produces structured fix suggestions. It is the diagnostic counterpart to `rs-test-helper-run` and lives at the intersection of testing infrastructure and agent-driven debugging.

## Context

`@runicengines/opencode-runesmith` provides a collection of reusable skill primitives — prefixed `rs-` — that RunicEngines agents compose into workflows. The test-helper family spans three skills:

| Skill | Prefix | Role |
|---|---|---|
| `test-helper-run` | `rs-` | Execute the test runner and capture output |
| `test-helper-diagnose` | `rs-` | Parse failure output, classify, suggest fixes |
| `test-helper-fix` | `rs-` | Apply suggested fixes (future) |

The diagnose skill is called by the **test-writer agent** after `rs-test-helper-run` returns a non-zero exit code or output containing failure markers. It ingests raw test runner output and produces a structured diagnosis that downstream agents (or human developers) can act on without re-reading raw logs.

## Skill Purpose

The primary goal of `rs-test-helper-diagnose` is to bridge the gap between "tests failed" and "here is what to change." Raw test output is noisy, repetitive, and often mixes multiple failure modes (assertion errors, panics, compilation failures, timeouts) in a single dump. The skill must:

1. **Parse** — Extract individual failure messages, stack traces, and test names from runner output.
2. **Group** — Bucket failures by error type so the same root cause is diagnosed once.
3. **Diagnose** — For each unique failure, determine the root cause and classify it as a real failure, flaky test, or environment issue.
4. **Suggest** — Produce a concrete fix recommendation with a confidence level.
5. **Report** — Output a structured diagnosis that agents can consume programmatically.

## Input

The skill receives the full stdout/stderr from the test runner, typically in one of these formats:

- **Jest / Vitest**: TAP-like output with `PASS`/`FAIL` banners, assertion messages, and stack traces.
- **pytest**: Standard Python test output with `FAILURES` section, tracebacks, and assertion rewrites.
- **Go test**: Verbose `--- FAIL` lines with stack traces.
- **Mocha / Ava**: YAML-annotated failure details.
- **Custom runners**: Arbitrary output parsed via pattern matching.

The skill should auto-detect the runner format from the output preamble or exit code behaviour.

## Skill Steps

### Step 1: Parse Failure Messages

Scan the raw output for known failure markers:

- `FAIL`, `✗`, `✘`, `×` — top-level failure indicators
- `AssertionError`, `Error:`, `Uncaught`, `Rejected` — exception markers
- `timeout` / `Timeout` / `--timeout` — timeout indicators
- Compilation errors (TypeScript, Go, Rust, etc.) in test files
- Crash/panic traces (`panic:`, `FATAL`, `Segmentation fault`)

For each failure, extract:

| Field | Source |
|---|---|
| `test_name` | The test or describe block name |
| `file_path` | Source file and line number |
| `error_message` | The assertion message or error text |
| `stack_trace` | Full trace, if available |
| `raw_stdout` | The surrounding 5-10 lines of output context |

### Step 2: Group by Error Type

Assign each failure to one of four categories:

| Category | Identifier | Examples |
|---|---|---|
| `assertion` | Expected/actual mismatch, `toEqual`, `assert.equal` | `expected 3 to equal 4` |
| `exception` | Uncaught error, promise rejection, panic | `TypeError: Cannot read property 'x' of undefined` |
| `timeout` | Async test exceeding time limit | `Exceeded timeout of 5000 ms` |
| `compilation` | Type error, syntax error, import failure | `TS2322: Type 'string' is not assignable to type 'number'` |

Failures sharing the same category and similar error message tokens are grouped under a single root cause.

### Step 3: Identify Root Cause

For each error group, the skill examines the error message, stack trace, and (when available) the source code of the failing test and the module under test:

- **Assertion failures**: Compare the expected vs actual values. If the actual value looks stale or uninitialized, the cause may be a missing setup (beforeEach, fixtures). If the assertion itself is wrong, the test logic is incorrect.
- **Exceptions**: Trace the point of origin in the stack. An exception thrown in the module under test suggests a production code bug. An exception in a mock or stub suggests a test infrastructure issue.
- **Timeouts**: Inspect whether the test awaits asynchronous operations. Missing `await` on a promise is the most common cause. Long-running operations without adequate time limits may also be the culprit.
- **Compilation failures**: The error message typically points directly to a type mismatch or missing import. These are the most straightforward to diagnose.

### Step 4: Classify Failure Type

The skill must categorise each failure group into one of three classes:

**Real failure** — A logic error in either the test or the production code. Requires a code change.

- Assertion expecting wrong value (test bug)
- Production code returning incorrect result (source bug)
- Missing edge case not handled (source bug)

**Flaky test** — Non-deterministic behaviour. The same test may pass or fail on different runs without code changes.

- Timing-dependent assertions
- Tests sharing mutable state that causes ordering sensitivity
- Network calls or external service dependencies
- Random data generation producing unexpected values

**Environment issue** — The test environment is misconfigured.

- Missing environment variables
- Wrong database or service version
- Dependency not installed or wrong version
- Platform-specific behaviour (OS, filesystem, locale)

## Flaky Test Detection Heuristics

Flaky detection is inherently probabilistic. The skill uses the following heuristics, each contributing to a confidence score:

| Heuristic | Signal | Weight |
|---|---|---|
| Timeout-related failure message | Contains `timeout`, `Timeout`, `--timeout`, `TLIMIT` | High |
| Test name contains flaky keywords | `flaky`, `random`, `concurrent`, `race`, `parallel` | Medium |
| Async without `await` | Stack trace shows a promise returned but not awaited | High |
| Shared mutable state | Test reads from a module-level variable or shared fixture | Medium |
| Network or IO dependency | Error contains `connect`, `socket`, `fetch`, `http`, `ECONNREFUSED` | High |
| Random/seed-based data | Test imports `faker`, `chance`, `random`, or generates UUIDs | Low |
| Order-dependent | Stack trace references a global array, cache, or singleton | Medium |
| Timing assertions | Uses `sleep`, `setTimeout`, `setInterval`, `polling` | Medium |

If the aggregate flaky confidence exceeds a threshold (e.g., 0.6), the failure is classified as flaky rather than real. The threshold should be configurable so teams can tune sensitivity.

## Output Format

The skill produces a YAML or JSON block (embedded in the skill's stdout) that downstream agents parse:

```yaml
diagnosis:
  runner: jest
  exit_code: 1
  total_failures: 3
  groups:
    - error_type: assertion
      root_cause: "Expected user.name to equal 'admin' but received null"
      classification: real
      confidence: high
      tests:
        - name: "UserService.getAdmin returns admin user"
          file: "tests/unit/user.service.spec.ts:42"
          suggested_fix: "Add `await userService.initialize()` before the assertion in the test setup"
    - error_type: timeout
      root_cause: "Async test did not complete within 5000ms"
      classification: flaky
      confidence: 0.72
      tests:
        - name: "OrderService.processOrder completes within time limit"
          file: "tests/unit/order.service.spec.ts:88"
          suggested_fix: "Add `await` on the `processOrder` call; the promise was not being awaited"
    - error_type: compilation
      root_cause: "Type 'undefined' is not assignable to type 'User'"
      classification: real
      confidence: high
      tests:
        - name: "UserService.createUser returns a User"
          file: "tests/unit/user.service.spec.ts:15"
          suggested_fix: "Ensure `createUser` returns a `User` type and does not return `undefined` on error paths"
```

The `confidence` field uses `high`/`medium`/`low` for real failures (static analysis is deterministic) and a float `0.0-1.0` for flaky classifications (probabilistic).

## Chained Skills

`rs-test-helper-diagnose` is designed to be composed with other Runesmith skills:

| Skill | Relationship | Usage |
|---|---|---|
| `rs-test-helper-run` | Predecessor | Provides the raw test output this skill analyses |
| `rs-discover` | Optional helper | Reads the source code of failing tests when root cause analysis needs file context |
| `rs-test-helper-fix` | Future successor | Would consume the structured diagnosis to apply fixes automatically |

The test-writer agent orchestrates the chain: run → diagnose → (if failures are real) → discover source → produce fix patch. Flaky tests are reported but skipped during fix generation.

## Recommendations

1. **Runner-format auto-detection** — The skill should maintain a registry of output format parsers (Jest, pytest, Go test, etc.) and auto-detect via output preamble rather than requiring a config flag.
2. **Configurable flaky threshold** — Expose the flaky confidence threshold as a parameter so agent workflows can tune it per project or per CI run.
3. **Source cross-reference** — When available, the skill should invoke `rs-discover` to read the failing test's source and the module under test. This dramatically improves root cause accuracy.
4. **Diagnosis caching** — For large test suites, cache diagnosis results keyed by (test_name, file hash) to avoid re-diagnosing flaky tests that already have a pending fix.
5. **Flaky test registry** — Maintain a file-level registry of known flaky tests (`.runesmith/flaky.yml`) so repeated flaky failures are not re-diagnosed as real failures each run.

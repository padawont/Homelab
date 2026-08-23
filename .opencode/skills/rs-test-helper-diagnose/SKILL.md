---
name: rs-test-helper-diagnose
description: >
  Consume test failure data from rs-test-helper-run and diagnose root
  causes. Classifies failures into error types (assertion, exception,
  timeout, compilation, crash/panic), assigns confidence scores, and
  suggests concrete fixes.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: utility
  audience: agents, developers
  trigger: manual+chained
---

## Purpose

Consumes the `failures` array and `raw_stdout` from `rs-test-helper-run`'s JSON output and diagnoses test failures. Classifies each failure into one of five error types and one of four classification buckets, producing a structured diagnosis with confidence scores and fix suggestions.

Key characteristics:

- **Read-only**: Never edits test files. Only reads the run output.
- **Classification-aware**: Distinguishes assertion, exception, timeout, compilation, and crash/panic error types.
- **Bucket-aware**: Labels each failure as `code_bug`, `test_bug`, `flaky`, or `environment`.
- **Confidence-scored**: Assigns `high`/`medium`/`low` for deterministic classifications, float `0.0-1.0` for flaky.
- **Chaining-ready**: Output schema is consumed by `rs-issue-to-plan` for regression planning.

## Trigger

| Condition                                                                 | Type             |
| ------------------------------------------------------------------------- | ---------------- |
| `rs-test-helper-run` returns `summary.failed > 0` or `summary.errors > 0` | Manual (chained) |
| User asks to diagnose test output                                         | Manual           |

## Required Permissions

The calling agent must have these tools available:

| Tool     | Required | Scope                   | Purpose                                      |
| -------- | -------- | ----------------------- | -------------------------------------------- |
| read     | Yes      | File refs from failures | Read failing source files for context        |
| glob     | Yes      | Project root            | Discover source files referenced in failures |
| grep     | Yes      | Project root            | Search for patterns in failure context       |
| bash     | No       | —                       | Never executes commands                      |
| edit     | No       | —                       | Never modifies files                         |
| write    | No       | —                       | Never creates files                          |
| delegate | No       | —                       | Never delegates; self-contained diagnosis    |

## Input

The skill receives the full JSON output from `rs-test-helper-run` as a YAML/JSON block or equivalent structured data. Key fields consumed:

| Field        | Type    | Description                                                    |
| ------------ | ------- | -------------------------------------------------------------- |
| `failures`   | array   | List of failure objects with `test`, `message`, `file`, `line` |
| `errors`     | array   | List of non-test errors (timeout, framework not found, crash)  |
| `raw_stdout` | string  | Full stdout captured during execution                          |
| `raw_stderr` | string  | Full stderr captured during execution                          |
| `framework`  | string  | Detected framework: `pytest`, `bun`, `npm`, `make`, `cargo`    |
| `exit_code`  | integer | Process exit code                                              |
| `timeout`    | boolean | Whether the command was killed due to timeout                  |

If `failures` is empty but `errors` is populated, diagnose from `errors` and `raw_stderr`.

## Error Type Classification

Each failure is classified into one of five error types. The classification is driven by pattern matching against the failure message, stack trace, and surrounding output.

### Assertion

Assertions compare expected vs actual values. Detected via:

| Pattern                          | Example                                 |
| -------------------------------- | --------------------------------------- |
| `AssertionError`                 | `AssertionError: assert 401 == 200`     |
| `assert ` in message             | `assert user.is_admin`                  |
| `expected` / `actual` / `got`    | `expected 3 to equal 4`                 |
| `toEqual` / `toStrictEqual`      | `Expected \"admin\" toEqual \"user\"`   |
| `FAILED` with test path (pytest) | `FAILED tests/test_auth.py::test_login` |
| `X` prefix (bun)                 | `X add 1 + 2 = 3`                       |
| `--- FAIL` (Go)                  | `--- FAIL: TestLogin`                   |

Confidence: `high` — assertion patterns are unambiguous.

### Exception

Uncaught errors, promise rejections, and runtime exceptions. Detected via:

| Pattern                 | Example                                            |
| ----------------------- | -------------------------------------------------- |
| `TypeError`             | `TypeError: Cannot read property 'x' of undefined` |
| `ReferenceError`        | `ReferenceError: x is not defined`                 |
| `ValueError`            | `ValueError: invalid literal for int()`            |
| `KeyError`              | `KeyError: 'missing_key'`                          |
| `Error:` (generic)      | `Error: Connection refused`                        |
| `Uncaught` / `Rejected` | `Uncaught ReferenceError: foo is not defined`      |
| Exception thrown (Jest) | `thrown: "Error: something went wrong"`            |

Confidence: `high` — exception type markers are reliable.

### Timeout

Tests that exceeded their time limit. Detected via:

| Pattern                 | Example                                                               |
| ----------------------- | --------------------------------------------------------------------- |
| `timeout` / `Timeout`   | `Exceeded timeout of 5000 ms`                                         |
| `--timeout`             | `Timeout - Async callback was not invoked within the 5000 ms timeout` |
| `TLIMIT`                | Process killed by timeout command                                     |
| `done()` not called     | `waiting for done() to be called`                                     |
| `async` without `await` | Stack trace shows promise returned but not awaited                    |

Confidence: `high` when timeout markers present in message or output; `medium` when inferred from SIGTERM/SIGKILL in stderr.

### Compilation

Type errors, syntax errors, import failures. Detected via:

| Pattern                            | Example                                           |
| ---------------------------------- | ------------------------------------------------- |
| `ImportError`                      | `ImportError: No module named 'psycopg2'`         |
| `ModuleNotFoundError`              | `ModuleNotFoundError: No module named 'psycopg2'` |
| `SyntaxError`                      | `SyntaxError: invalid syntax`                     |
| `TypeError` in compilation context | `TypeError: str cannot be used as a type`         |
| `ERROR collecting` (pytest)        | `ERROR collecting tests/test_models.py`           |
| Rust compile error                 | `error[E0308]: mismatched types`                  |
| TypeScript compile error           | `TS2322: Type 'X' is not assignable to type 'Y'`  |

Confidence: `high` — compilation errors are deterministic.

### Crash / Panic

Process crashes and panics. Detected via:

| Pattern                          | Example                                        |
| -------------------------------- | ---------------------------------------------- |
| `panic:`                         | `panic: runtime error: invalid memory address` |
| `FATAL`                          | `FATAL: cannot continue`                       |
| `Segmentation fault`             | `Segmentation fault (core dumped)`             |
| `SIGSEGV` / `SIGABRT` / `SIGILL` | Process terminated by signal                   |
| `Killed`                         | `Killed` (OOM killer)                          |

Confidence: `high` — crash/panic markers are unambiguous.

## Classification Schema

Each failure group is classified into one of four buckets:

| Bucket        | Description                                          | Example                                                     |
| ------------- | ---------------------------------------------------- | ----------------------------------------------------------- |
| `code_bug`    | Production code has a logic error                    | Function returns wrong value under certain conditions       |
| `test_bug`    | Test itself has a logic error                        | Assertion expects wrong value; missing async await          |
| `flaky`       | Non-deterministic; passes/fails without code changes | Timing-dependent; shared mutable state; network dependency  |
| `environment` | Test environment is misconfigured                    | Missing env vars; wrong service version; missing dependency |

### Flaky Detection Heuristics

| Heuristic                         | Signal                                                              | Weight |
| --------------------------------- | ------------------------------------------------------------------- | ------ |
| Timeout-related failure message   | Contains `timeout`, `Timeout`, `--timeout`, `TLIMIT`                | High   |
| Test name contains flaky keywords | `flaky`, `random`, `concurrent`, `race`, `parallel`                 | Medium |
| Async without `await`             | Stack trace shows a promise returned but not awaited                | High   |
| Shared mutable state              | Test reads from a module-level variable or shared fixture           | Medium |
| Network or IO dependency          | Error contains `connect`, `socket`, `fetch`, `http`, `ECONNREFUSED` | High   |
| Random/seed-based data            | Test imports `faker`, `chance`, `random`, or generates UUIDs        | Low    |
| Order-dependent                   | Stack trace references a global array, cache, or singleton          | Medium |
| Timing assertions                 | Uses `sleep`, `setTimeout`, `setInterval`, `polling`                | Medium |

If the aggregate flaky confidence exceeds `0.6`, the failure is classified as `flaky` rather than `code_bug` or `test_bug`.

## Workflow Steps

### Step 1: Parse failure messages

1. Receive structured input from `rs-test-helper-run` output.
2. If `failures` array is non-empty, extract each failure's `test`, `message`, `file`, `line`.
3. If `failures` is empty but `errors` is non-empty, parse error entries for diagnosis.
4. Read `raw_stdout` and `raw_stderr` for additional context around each failure.

### Step 2: Group by error type

1. For each failure/error entry, run pattern matching against the error type classification table.
2. Group entries sharing the same error type and similar message tokens under a single diagnosis group.
3. Deduplicate: multiple test failures caused by the same root cause (e.g., missing import) are grouped together.

### Step 3: Classify failure bucket

1. For each group, determine the classification bucket:
   - **code_bug**: Assertion failure where logic error is in production code.
   - **test_bug**: Assertion failure where test logic is incorrect; exception in mock/stub; missing async `await`.
   - **flaky**: Evaluate flaky detection heuristics. If aggregate confidence > 0.6, classify as flaky.
   - **environment**: Missing dependency, missing env var, wrong version.
2. Record the classification rationale.

### Step 4: Assign confidence score

1. **Error type detection**: `high` when pattern match is unambiguous; `medium` when inferred from context.
2. **Classification confidence**: `high`/`medium`/`low` for non-flaky; float `0.0-1.0` for flaky.
3. Include the rationale for the assigned score.

### Step 5: Build and output diagnosis

Assemble the YAML diagnosis object with all fields. Always include all fields, even when empty.

## Output Format

```yaml
diagnosis:
  input_framework: pytest
  input_exit_code: 1
  total_failures: 3
  groups:
    - error_type: assertion
      root_cause: "Expected user.name to equal 'admin' but received null"
      classification: code_bug
      confidence: high
      tests:
        - name: "UserService.getAdmin returns admin user"
          file: "tests/unit/user.service.spec.ts"
          line: 42
          message: "AssertionError: expected 'admin' but got null"
      suggested_fix: "Ensure UserService.getAdmin initializes the user object before returning"
    - error_type: timeout
      root_cause: "Async test did not complete within 5000ms"
      classification: flaky
      confidence: 0.72
      tests:
        - name: "OrderService.processOrder completes within time limit"
          file: "tests/unit/order.service.spec.ts"
          line: 88
          message: "Timeout - Async callback was not invoked within the 5000 ms timeout"
      suggested_fix: "Add `await` on the `processOrder` call; the promise was not being awaited"
    - error_type: compilation
      root_cause: "ImportError: No module named 'psycopg2'"
      classification: environment
      confidence: high
      tests:
        - name: "(test collection)"
          file: "tests/test_models.py"
          line: 3
          message: "ModuleNotFoundError: No module named 'psycopg2'"
      suggested_fix: "Install missing dependency: pip install psycopg2-binary or add to requirements.txt"
```

| Field                       | Type         | Always Present | Description                                                               |
| --------------------------- | ------------ | -------------- | ------------------------------------------------------------------------- |
| `diagnosis.input_framework` | string       | yes            | Framework detected by the run skill                                       |
| `diagnosis.input_exit_code` | integer      | yes            | Exit code from the run skill                                              |
| `diagnosis.total_failures`  | integer      | yes            | Total number of unique failure entries                                    |
| `diagnosis.groups`          | array        | yes            | List of diagnosis groups (empty if no failures)                           |
| `group.error_type`          | string       | yes            | One of: `assertion`, `exception`, `timeout`, `compilation`, `crash/panic` |
| `group.root_cause`          | string       | yes            | Human-readable root cause description                                     |
| `group.classification`      | string       | yes            | One of: `code_bug`, `test_bug`, `flaky`, `environment`                    |
| `group.confidence`          | string/float | yes            | `high`/`medium`/`low` or float `0.0-1.0` for flaky                        |
| `group.tests`               | array        | yes            | List of affected test entries                                             |
| `group.tests[].name`        | string       | yes            | Test name                                                                 |
| `group.tests[].file`        | string       | yes            | Source file path                                                          |
| `group.tests[].line`        | integer      | yes            | Line number                                                               |
| `group.tests[].message`     | string       | yes            | Error message                                                             |
| `group.suggested_fix`       | string       | yes            | Concrete fix suggestion                                                   |

## Chained Skills

| Skill              | Condition                                                                          | After Step |
| ------------------ | ---------------------------------------------------------------------------------- | ---------- |
| `rs-issue-to-plan` | Diagnosis contains `code_bug` or `test_bug` classification indicating a regression | Step 5     |

## See Also

- `rs-test-helper-run` — companion skill for test execution
- `rs-issue-to-plan` — converts regressions into implementation plans
- `rs-discover` — codebase scanner for reading failing source file context

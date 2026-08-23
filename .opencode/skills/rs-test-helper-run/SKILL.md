---
name: rs-test-helper-run
description: >
  Detect the project's test framework (pytest, cargo, bun, npm, make),
  run the test suite or a filtered subset, and return a structured JSON
  summary with pass/fail counts, error details, and runtime.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: utility
  audience: agents, developers
  trigger: manual+chained
---

## Purpose

Detects the active test framework by scanning for indicator files, runs the full test suite (or a filtered subset), and produces a machine-readable JSON summary with pass/fail counts, individual failure details, error messages, and runtime. Designed as the execution half of the test-helper workflow; chain its output into `rs-test-helper-diagnose` for failure interpretation.

Key characteristics:

- **Read-only**: Never edits test files. Only reads indicator files and runs tests.
- **Framework-agnostic**: Normalises pytest, cargo, bun, npm, and make into a single JSON schema.
- **Chaining-ready**: Output schema is consumed by `rs-test-helper-diagnose` and `rs-issue-to-plan`.
- **Timeout-guarded**: Default 300s timeout with SIGTERM → SIGKILL grace sequence.

## Trigger

| Condition                                          | Type                  |
| -------------------------------------------------- | --------------------- |
| User asks to run tests                             | Manual                |
| After test-writer generates or modifies test files | Manual (chained)      |
| Before PR readiness check                          | Manual (auto-suggest) |

## Required Permissions

The calling agent must have these tools available:

| Tool     | Required | Scope            | Purpose                                                 |
| -------- | -------- | ---------------- | ------------------------------------------------------- |
| bash     | Yes      | `project: allow` | Run test commands (pytest, bun, npm, cargo, make)       |
| read     | Yes      | Indicator files  | Read framework config files for detection               |
| glob     | Yes      | Project root     | Discover indicator files (pytest.ini, Cargo.toml, etc.) |
| edit     | No       | —                | Never modifies files                                    |
| write    | No       | —                | Never creates files                                     |
| delegate | No       | —                | Never delegates; self-contained execution               |

No network access is required. All operations are local.

All test commands are executed relative to the project root. Test paths and filters MUST be shell-escaped using `shlex.quote()` before concatenation.

## Input

| Parameter         | Type               | Default         | Example                            |
| ----------------- | ------------------ | --------------- | ---------------------------------- |
| `test_filter`     | string (optional)  | `""` (run all)  | `"tests/test_auth.py::test_login"` |
| `test_path`       | string (optional)  | `""` (root dir) | `"tests/integration/"`             |
| `timeout_seconds` | integer (optional) | `300`           | `600`                              |

When both are provided, the framework receives the path first, then the filter (e.g., `pytest tests/integration/ -k test_login`).

`test_path` MUST be validated to be a subdirectory of the project root before passing to the test command. Reject paths containing `..` or starting with `/` (absolute paths).

## Framework Detection

Scan the project root for indicator files in specificity order. The first match determines the framework.

| Indicator File                                                | Detected Framework | Resolved Command                 |
| ------------------------------------------------------------- | ------------------ | -------------------------------- |
| `pytest.ini` or `pyproject.toml` with `[tool.pytest]` section | pytest             | `python -m pytest -v --tb=short` |
| `bun.lockb` (with `package.json` present)                     | bun                | `bun test`                       |
| `package.json` (no `bun.lockb`)                               | npm                | `npm test`                       |
| `Cargo.toml`                                                  | cargo              | `cargo test`                     |
| `Makefile` with `test:` target                                | make               | `make test`                      |

**Detection order:** pytest markers → bun lockfile → npm manifest → Cargo manifest → Makefile. The first match wins.

If a `package.json` is detected and has a `scripts.test` entry, use that script's value as the command instead of `bun test` or `npm test`. This respects custom test runners like `vitest run` or `jest --config custom.js`.

**Fallback:** If no indicator file is found, attempt `python -m pytest -v --tb=short` as a reasonable Python default. If that would also fail, abort with a "framework not found" error listing every checked indicator file.

## Workflow Steps

### Step 1: Detect framework

1. Glob for indicator files at project root in specificity order.
2. Match against the detection table. Stop at first match.
3. Resolve the framework name and command string.
4. Record `framework_detected_by` (which indicator file triggered the match).
5. If no match, attempt pytest fallback. If that fails, abort with `framework: "unknown"`.

### Step 2: Resolve the test command

Build the concrete command string per detected framework:

- **pytest:** `python -m pytest -v --tb=short <test_path> -k <test_filter>` (omit empty parts)
- **bun:** `bun test <test_path>`
- **npm:** `npm test -- <test_path>` (or `npm test` with no path)
- **cargo:** `cargo test <test_filter> -- <test_path>`
- **make:** `make test` (no flags appended)

Emit the resolved command to stdout for debugging transparency.

### Step 3: Run tests with timeout

1. Shell-escape `test_filter` and `test_path` using `shlex.quote()` before command construction.
2. Execute the resolved command via `bash` with `timeout_seconds` (default 300).
3. Capture **stdout**, **stderr**, and **exit code** separately.
4. Record **wall-clock runtime** in seconds.
5. If the command exceeds the timeout:
   - Send **SIGTERM** first, then **SIGKILL** after 5s grace.
   - Set `timeout: true` in the output.
   - Preserve partial stdout/stderr for diagnosis.

### Step 4: Parse results into structured format

Parsing strategy varies by framework. All parsers normalise into the shared JSON schema.

**pytest:**

- Scan stdout for the final summary line: `=== 15 passed, 3 skipped, 2 failed in 4.23s ===`
- Regex: `(?P<passed>\d+) passed(?:, (?P<skipped>\d+) skipped)?(?:, (?P<failed>\d+) failed)?(?:, (?P<errors>\d+) error)?`
- Collect failure lines matching `FAILED <path>::<test_name>`.
- If exit code is non-zero but no failures parsed, treat as compilation/import error.
- Fall back to line-level PASSED/FAILED counts when summary regex does not match.

**cargo:**

- Parse `test result: ok. 12 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out`
- Regex: `test result: (?P<result>ok|FAILED)\. (?P<passed>\d+) passed; (?P<failed>\d+) failed`
- Collect individual results from `test <name> ... ok` / `test <name> ... FAILED`.

**bun:**

- Count lines starting with `✓` (pass) and `✗` (fail).
- Parse summary lines: `X pass` / `Y fail`.
- Fall back to line counts if summary regex fails.

**npm:**

- Attempt Jest output parsing: `Tests: X passed, Y total`.
- If no Jest output detected, report exit code only.
- Always add warning: "npm test: exit-code-only reporting — structured parsing not available for custom runners".

**make:**

- Report exit code only. Do not attempt structured output parsing.
- Add warning: "make test: exit-code-only reporting — output was not parsed".

### Step 5: Build and output JSON summary

Assemble the JSON object with all fields documented below. Always include all fields, even when empty.

Post-processing checks:

- If `raw_stdout` exceeds 100,000 characters, truncate to last 50,000. Add truncation warning.
- If `exit_code` is 0 but `summary.failed > 0` (i.e., parsed failures independently of exit code), add warning about exit code 0 with failures.
- If exit code is non-zero and no tests were parsed (passed=0, failed=0, skipped=0), treat as compilation/import error: move stderr into `errors`, add compilation failure warning.

## Output Format

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
  "raw_stderr": "",
  "framework_detected_by": "pytest.ini",
  "warnings": ["2 tests failed — use rs-test-helper-diagnose to interpret"]
}
```

| Field                   | Type    | Always Present | Description                                                                                      |
| ----------------------- | ------- | -------------- | ------------------------------------------------------------------------------------------------ |
| `framework`             | string  | yes            | Detected framework: `pytest`, `bun`, `npm`, `make`, `cargo`, or `unknown`                        |
| `command`               | string  | yes            | Exact command that was executed                                                                  |
| `exit_code`             | integer | yes            | Process exit code (`-1` if command not executed)                                                 |
| `runtime_seconds`       | float   | yes            | Wall-clock execution time                                                                        |
| `timeout`               | boolean | yes            | Whether the command was killed due to timeout                                                    |
| `summary.passed`        | integer | yes            | Number of passing tests                                                                          |
| `summary.failed`        | integer | yes            | Number of failing tests                                                                          |
| `summary.errors`        | integer | yes            | Number of errors (setup/teardown failures, import errors)                                        |
| `summary.skipped`       | integer | yes            | Number of skipped tests                                                                          |
| `failures`              | array   | yes            | List of individual failure objects (empty if none)                                               |
| `errors`                | array   | yes            | List of non-test errors (timeout, framework not found, crash)                                    |
| `raw_stdout`            | string  | yes            | Full stdout captured during execution (truncated to last 50,000 characters if exceeding 100,000) |
| `raw_stderr`            | string  | yes            | Full stderr captured during execution                                                            |
| `framework_detected_by` | string  | yes            | Indicator file that triggered detection                                                          |
| `warnings`              | array   | yes            | Human-readable warnings for the agent                                                            |

## Error Handling

### Timeout

Implement using `timeout --kill-after=5s $TIMEOUT $CMD` wrapper. If `timeout` command is unavailable (e.g., some embedded systems), implement equivalent logic in the calling agent using `bash` with `sleep $TIMEOUT && kill -TERM $PID` and a 5s grace timer. Set `timeout: true`. Preserve partial stdout/stderr in `raw_stdout` / `raw_stderr`.

### Framework Not Found

If no indicator file is detected and the pytest fallback also fails, set `framework: "unknown"`, set `exit_code: -1`, and add an `errors` entry listing every checked indicator file and why it was rejected. Suggest the user specify a framework explicitly.

### Compilation or Import Failure

If exit code is non-zero and the parser found zero test results (no passed, failed, or skipped output), treat as compilation/import error:

1. Set `summary.passed: 0`, `summary.failed: 0`.
2. Add full stderr to `errors`.
3. Add warning: "Tests did not start — possible compilation or import error".

### Output Truncation

If `raw_stdout` exceeds 100,000 characters, truncate to the last 50,000 characters and add a warning: "stdout truncated from N characters".

### Exit Code Zero With Failures

If `exit_code` is 0 but parsed `summary.failed > 0`, add warning: "Exit code 0 but parsed N failures — test runner may not be configured to fail on test failure".

## Chained Skills

| Skill                     | Condition                                         | After Step      |
| ------------------------- | ------------------------------------------------- | --------------- |
| `rs-test-helper-diagnose` | `summary.failed > 0` or `summary.errors > 0`      | Step 5          |
| `rs-issue-to-plan`        | Failures indicate a missing feature or regression | After diagnosis |

The `failures` array from this skill's output is passed as context when loading the chained skill.

## See Also

- `rs-test-helper-diagnose` — companion skill for failure interpretation
- `rs-issue-to-plan` — converts regressions into implementation plans
- `rs-discover` — codebase scanner, useful before first test run

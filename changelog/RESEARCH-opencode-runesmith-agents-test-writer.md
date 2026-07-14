---
title: "Test Writer Agent Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - agents
  - test-writer
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
  - knowledge: "knowledge/tooling/opencode/agents/permissions.md"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
last_audit_date: 2026-06-07
---

# Test Writer Agent Design

The test-writer is a leaf agent within the `@runicengines/opencode-runesmith` plugin. Its sole responsibility is to write and run tests — unit tests, integration tests, and failure diagnosis — without ever modifying production code. It follows project test conventions, respects existing test infrastructure, and produces a structured test report at the end of each session.

This document captures the agent's design: its role, prompt structure, permission model, skills, sample output, and a comparison with analogous agents in other OpenCode ecosystems (opencode-swarm's `test_engineer`, opencode-workspace reviewers). It serves as the analysis that will inform proposals and ADRs for the plugin's agent architecture.

## Agent Role

The test-writer sits at the end of the implementation pipeline. Once a developer (or the RuneSmith developer agent) produces code changes, the test-writer is invoked to validate those changes. The agent:

- Reads the specification (a `spec.md` file or issue description) and the production code that implements it.
- Writes new test files or extends existing test suites.
- Runs the test suite and diagnoses any failures.
- Reports pass/fail counts, coverage gaps, and potential flaky tests.
- Never touches production code — its `edit` permission is scoped by convention to test paths only.

The agent is a **leaf agent**. It does not delegate to other agents. It does not create branches, commit code, or open pull requests. It is pure verification — a quality gate that runs before the developer reviews and merges.

### Key Responsibilities

| Responsibility | Description |
|---|---|
| Test writing | Produce unit tests, integration tests, and edge-case coverage for new or modified code |
| Test execution | Run test suites via the project's configured test runner (pytest, bun test, npm test) |
| Failure diagnosis | Read test output, identify root causes, and suggest fixes for test code only |
| Convention enforcement | Follow project test conventions — directory structure, naming, fixtures, mocking patterns |
| Coverage analysis | Identify untested paths, missing edge cases, and security-relevant boundaries |
| Flaky detection | Flag tests that produce non-deterministic results across multiple runs |
| Test report | Output a structured summary with pass/fail counts, coverage gaps, and recommendations |

### Non-Responsibilities

The test-writer explicitly does **not**:

- Modify production code (`.py`, `.ts`, `.js` files outside `tests/`, `spec/`, or `__test__` directories).
- Change test infrastructure (CI configs, test runner configs, conftest files) without explicit user permission.
- Create branches, commit changes, or push to any remote.
- Delegate to other agents (it is a leaf agent — `task: deny`).
- Run destructive commands (database resets, production deployments, or arbitrary shell scripts).
- Reformat, lint, or refactor production code, even if it appears buggy — it reports the issue and stops.

## Prompt Structure

The agent's prompt is the core of its behaviour. It follows a numbered workflow with a structured test report output.

### Role Definition

> You are the RuneSmith Test Writer agent for `@runicengines/opencode-runesmith`. Your purpose is to write and run tests for implementation code. You never modify production code. You produce a single test report per session. You are a leaf agent — you do not delegate to other agents.

### Workflow Steps

```
1. Read the specification
   Load .runesmith/{date}-{branch}/specs/{issue-number}-{slug}.md or the provided issue description.
   Extract: phases implemented, acceptance criteria, test strategy, affected files.

2. Read the production code
   Read the files listed in the spec's "Files to change" sections.
   Understand: function signatures, class interfaces, error paths, side effects.

3. Write tests
   Create or extend test files following the project's conventions:
   - Location: mirror the module path under tests/ (e.g., app/user.py → tests/unit/test_user.py)
   - Naming: test_*.py or *.test.ts depending on the stack
   - Patterns: Arrange-Act-Assert, given-when-then, or project-specific idioms
   - Fixtures: Use existing conftest fixtures where available

   Coverage targets:
   - Happy path: All success conditions from the spec's acceptance criteria
   - Edge cases: Empty inputs, boundary values, type mismatches, overflow
   - Error conditions: Expected exceptions, error codes, failure responses
   - Security boundaries: Input validation, injection attempts, auth bypass
   - State transitions: Database state changes, cache invalidation, side effects

4. Run the test suite
   Execute the project's test command:
   - Python: skill({ name: "rs-test-helper-run", args: { command: "python -m pytest tests/ -x -v" } })
   - JavaScript/TypeScript: skill({ name: "rs-test-helper-run", args: { command: "npm test" } })
   - Other: Use the command from the spec's test strategy section.

   Run three times in succession to check for flakiness.

5. Diagnose failures (if any)
   Load skill({ name: "rs-test-helper-diagnose", args: { output: "<test output>" } }) to
   interpret stack traces, assertion errors, and timeout issues.
   The skill returns:
   - Likely root cause (production bug vs test bug vs environment issue)
   - Suggested fix for the test code
   - If the root cause is in production code, report it without modifying it.

6. Produce the test report
   Write the report to .runesmith/{date}-{branch}/reports/{issue-number}-{slug}-test-report.md
   using the output template below.
```

### Output Format

The test report follows this structure:

```markdown
# Test Report: {Issue Title}

**Issue**: #{number} — {url}
**Date**: {date}
**Test Command**: {command used}

## Results

| Suite | Pass | Fail | Skip | Flaky |
|---|---|---|---|---|
| unit | {n} | {n} | {n} | {n} |
| integration | {n} | {n} | {n} | {n} |
| **Total** | **{n}** | **{n}** | **{n}** | **{n}** |

## Coverage Gaps

- {module/path}: missing test for {edge case / error condition}
- {module/path}: {branch} path not covered

## Failures

### {test_name}
- **Message**: {assertion error or stack trace summary}
- **Root cause**: {production bug | test bug | environment}
- **Suggested fix**: {description, test fix only}
- **Recommended action**: {fix test | report production bug}

## Flaky Tests

### {test_name}
- **Behaviour**: {passes on run 1/3, fails on 2/3, passes on 3/3}
- **Suspected cause**: {async timing | shared state | network dependency}

## Summary

{3-5 sentence assessment of test health and code confidence}
```

## Skills This Agent Uses

### `rs-test-helper-run`

This skill wraps the test runner invocation. It abstracts away the project-specific test command and handles:

- Detecting the active runtime (Python, Node.js, Bun) from `pyproject.toml`, `package.json`, or `.bun-version`.
- Invoking the correct test runner with standard flags (`-x` for fail-fast, `-v` for verbose, `--tb=short` for concise tracebacks).
- Capturing stdout, stderr, and exit codes.
- Running the suite multiple times to detect flaky tests.

The test-writer invokes `rs-test-helper-run` during step 4 of the workflow. The skill accepts an optional `command` argument to override the detected runner, but defaults to auto-detection.

**Backend implementation sketch:**

```python
def run_tests(command: str | None = None, retries: int = 3):
    """
    Auto-detect runner if no command given.
    Return structured result: { suites, passed, failed, skipped, flaky, output }
    """
```

### `rs-test-helper-diagnose`

This skill consumes raw test output and returns structured diagnosis:

- Parses `pytest` / `jest` / `bun test` output into individual test results.
- Identifies the failing test, the assertion that failed, and the line number.
- Classifies the root cause: **production bug** (code under test is wrong), **test bug** (test logic, fixture, or mock is wrong), or **environment** (missing dependency, port conflict, timeout).
- Suggests a concrete fix for the test code.
- If the root cause is a production bug, the skill explicitly refuses to modify production code and instructs the agent to report the issue.

The test-writer invokes `rs-test-helper-diagnose` during step 5 of the workflow. The skill is stateless — it receives the raw output and returns a diagnostic object.

## Permissions Analysis

The test-writer operates with tightly scoped permissions. The rationale for each is as follows:

| Permission | Setting | Rationale |
|---|---|---|
| `read` | `allow` | Must read spec files, production code to test, and existing test files |
| `edit` | `allow` | Must write new test files and modify existing test files |
| `glob` | `allow` | Needs to discover test directories, fixture files, and module structure |
| `grep` | `allow` | Needs to search for existing test patterns, imports, and mocking idioms |
| `bash*` | `deny` by default | Only specific test commands are allowed — no arbitrary shell |
| `bash: pytest *` | `allow` | Python test runner |
| `bash: bun test *` | `allow` | Bun/JavaScript test runner |
| `bash: npm test *` | `allow` | npm test runner |
| `bash: python -m pytest *` | `allow` | Alternative Python test invocation |
| `skill*` | `deny` | Only whitelisted skills allowed |
| `rs-*` | `allow` | Must load `rs-test-helper-run` and `rs-test-helper-diagnose` |
| `task*` | `deny` | Leaf agent — must not delegate to sub-agents |

### Why Not Full Bash Access

The test-writer has the most permissive `bash` rules of any RuneSmith agent because it needs to execute test commands. However, access is strictly scoped to test runners. No `git`, `rm`, `curl`, `sed`, or any other command is allowed. This prevents the agent from committing changes, deleting files, or modifying the environment.

The `edit: allow` is global in the permission block, but the prompt enforces a critical boundary: **edit is restricted to test files only**. This is enforced by convention in the prompt instructions rather than by the permission system itself, because OpenCode permissions do not support path-scoped edit rules. Any violation (writing to a production file) must be caught during review.

### Why No `git` Access

The test-writer should never create branches, stage files, or commit. Committing is the developer's responsibility. Without `git` access, the agent cannot accidentally commit a half-written test or push a failing suite to CI. Test reports live in `.runesmith/{date}-{branch}/reports/`, which is gitignored (recommended) or committed at the developer's discretion.

## Model Selection Rationale

The test-writer uses `opencode-go/deepseek-v4-pro` with `temperature: 0.2`.

- **Pro model is necessary**: Unlike the spec-writer, which produces routine structured text, the test-writer must understand code logic deeply to identify edge cases, construct valid test inputs, and debug assertion failures. This requires stronger reasoning capability. A flash model would miss subtle error paths and produce shallow coverage.
- **Low temperature (0.2)**: Tests should be deterministic and consistent. Higher temperatures would produce varied test output across invocations — different test names, different edge cases discovered, different assertion styles. A temperature of 0.2 preserves some variety for edge case discovery while keeping the overall structure stable.
- **Not a creative-writing agent**: Temperature is not set to 0 because some randomness in test case selection is desirable. At temperature 0, the model would write the same tests for the same code every time, potentially missing edge cases that a slightly different reasoning path would uncover.

The pro model represents a meaningful cost increase over flash, but the cost is justified by the quality of test coverage and the reduced false-positive diagnosis rate.

## Open Questions

Several aspects of the test-writer remain unresolved and will require further research or a decision-making ADR.

### 1. Report Storage — Committed or Local?

Should `.runesmith/{date}-{branch}/reports/` be committed to the repository or kept local?

- **Committed**: Reports become a historical record of test health. Useful for auditing and regression tracking. Risk of stale reports cluttering the repo.
- **Local**: No repo noise. Reports are ephemeral — they serve their purpose for the current session and are discarded. But there is no trace of what was tested and what failed.

**Current leaning**: Local (gitignored), with an opt-in flag (`--publish-report`) for committed reports when auditability is required. This aligns with the ephemeral nature of test output — what matters is the test code, not the report.

### 2. Handling Production Code Bugs

When the test-writer discovers a production code bug (a test fails because the implementation is wrong), what should it do?

- **Report only**: Document the bug in the test report and stop. The developer fixes the production code and re-invokes the test-writer.
- **Write a failing test**: Write a test that captures the bug, producing a known failure. The developer then fixes the production code to make the test pass.
- **Fix the production code**: This violates the agent's role and is ruled out.

**Current leaning**: Report only for the initial release. Writing a failing test is a potential future enhancement but adds complexity — the agent needs to distinguish between "test is wrong" and "code is wrong" reliably.

### 3. Auto-Invocation After Developer Agent

Should the architect or developer agent automatically invoke the test-writer after making changes?

- **Auto**: The developer agent calls skill({ name: "rs-test-writer-invoke" }) as the last step of its workflow.
- **Manual**: The developer explicitly invokes the test-writer when they are ready to validate.

**Current leaning**: Auto-invocation with an opt-out flag. Most implementation sessions should end with test validation. Making it automatic ensures testing is not skipped. The developer can pass `--skip-tests` to bypass.

## Comparison with Similar Agents

### opencode-swarm's `test_engineer`

The opencode-swarm ecosystem includes a `test_engineer` agent that writes and runs tests as part of a gated CI pipeline. Key differences:

| Dimension | RuneSmith test-writer | opencode-swarm test_engineer |
|---|---|---|
| Invocation | Manual or auto after development | Gated — runs on every PR before merge |
| Permissions | Restricted bash (test commands only) | Full sandboxed bash |
| Delegation | Leaf agent (`task: deny`) | May call utility sub-agents for fixture generation |
| Output | Structured test report + test files | PR check status + inline annotations |
| Scope | Current working tree | Isolated CI environment (Docker) |

The RuneSmith test-writer is designed for the *development loop* — it helps developers validate changes before pushing. The swarm test_engineer is a *gate keeper* — it prevents bad code from reaching main. Both are needed; they serve complementary purposes. The RuneSmith agent suite may eventually include a CI-mode variant of the test-writer for automated checks.

### opencode-workspace Reviewers

The opencode-workspace plugin separates review concerns into distinct agents: a code reviewer (production code), a test reviewer (test quality), and a security reviewer (vulnerability scanning). In contrast, RuneSmith consolidates "writing tests" and "running tests" into a single agent but separates "reviewing tests" as a potential future agent.

This means the test-writer is both creator and validator of tests, which creates a blind spot: the agent may miss flaws in its own test logic. Future iterations should consider a separate test-reviewer agent that audits the test-writer's output before merging.

## Recommended Agent Configuration

Below is the full recommended agent `.md` file that would live in the `@runicengines/opencode-runesmith` plugin's agent registry:

```markdown
---
description: "Writes and runs tests: unit tests, integration tests, and failure diagnosis"
mode: subagent
model: opencode-go/deepseek-v4-pro
temperature: 0.2
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  bash:
    "*": deny
    "pytest *": allow
    "bun test *": allow
    "npm test *": allow
    "python -m pytest *": allow
  skill:
    "*": deny
    "rs-*": allow
  task:
    "*": deny
---

You are the RuneSmith Test Writer agent for @runicengines/opencode-runesmith.

Your purpose is to write and run tests for implementation code. You never modify production code. You produce a single test report per session. You are a leaf agent — you do not delegate to other agents.

## Workflow

1. **Read the specification**
   Load `.runesmith/{date}-{branch}/specs/{issue-number}-{slug}.md` or the provided issue description.
   Extract: phases implemented, acceptance criteria, test strategy, affected files.

2. **Read the production code**
   Read the files listed in the spec's "Files to change" sections.
   Understand function signatures, class interfaces, error paths, side effects.

3. **Write tests**
   Create or extend test files following project conventions:
   - Location: mirror the module path under `tests/`
   - Naming: `test_*.py` or `*.test.ts`
   - Patterns: Arrange-Act-Assert, project-specific idioms
   - Fixtures: use existing conftest fixtures where available

   Cover these categories:
   - **Happy path**: All success conditions from acceptance criteria
   - **Edge cases**: Empty inputs, boundary values, type mismatches, overflow
   - **Error conditions**: Expected exceptions, error codes, failure responses
   - **Security boundaries**: Input validation, injection attempts, auth bypass
   - **State transitions**: Database state changes, cache invalidation, side effects

4. **Run the test suite**
   Load skill({ name: "rs-test-helper-run", args: { command: "python -m pytest tests/ -x -v" } })
   Run three times to detect flaky tests.

5. **Diagnose failures**
   Load skill({ name: "rs-test-helper-diagnose", args: { output: "<raw test output>" } })
   Interpret the diagnosis: production bug, test bug, or environment issue.
   If the root cause is a production bug, report it in the test report — do NOT fix it.

6. **Produce the test report**
   Write to `.runesmith/{date}-{branch}/reports/{issue-number}-{slug}-test-report.md`

## Output Template

```markdown
# Test Report: {Issue Title}

**Issue**: #{number} — {url}
**Date**: {date}
**Test Command**: {command}

## Results

| Suite | Pass | Fail | Skip | Flaky |
|---|---|---|---|---|
| unit | {n} | {n} | {n} | {n} |
| integration | {n} | {n} | {n} | {n} |

## Coverage Gaps

- {path}: missing {scenario}

## Failures

### {test_name}
- **Root cause**: {production bug | test bug | environment}
- **Suggested fix**: {description, test only}
- **Action**: {fix test | report bug}

## Flaky Tests

### {test_name}
- **Behaviour**: {run 1 pass, run 2 fail, run 3 pass}
- **Cause**: {async timing | shared state}

## Summary

{assessment}
```

## Hard Rules

1. **Never modify production code** — edit only files under `tests/`, `spec/`, or `__test__/`.
2. **Never change test infrastructure** without asking (CI configs, runner configs, conftest).
3. **Never run destructive commands** — no `rm`, `dropdb`, `git push`, or `deploy`.
4. **Never delegate** to other agents — you are a leaf agent.
5. **Always run tests three times** to check for flakiness.
6. **Always produce a test report** — the session is not complete without one.
```

## Sample Test Report

The following is a worked example of what the test-writer produces after testing a hypothetical user registration endpoint:

```markdown
# Test Report: Add user registration endpoint

**Issue**: #117 — https://github.com/RunicEngines/api/issues/117
**Date**: 2026-06-07
**Test Command**: python -m pytest tests/ -x -v --cov=app

## Results

| Suite | Pass | Fail | Skip | Flaky |
|---|---|---|---|---|
| unit | 14 | 0 | 1 | 0 |
| integration | 6 | 0 | 0 | 0 |
| **Total** | **20** | **0** | **1** | **0** |

## Coverage Gaps

- `app/validators/user.py`: missing test for email with international characters (RFC 6531)
- `app/services/user_service.py`: `send_welcome_email` failure path not covered (line 89-92)

## Failures

No failures.

## Flaky Tests

No flaky tests detected across 3 runs.

## Summary

All 20 tests pass across unit and integration suites. Coverage is strong on the happy path and error conditions. Two coverage gaps were identified: international email validation and the welcome email failure path. Neither is blocking — the endpoint is well-tested. The skipped test (`test_password_reset_expiry`) depends on a feature not yet implemented. Recommend adding the two missing edge cases before release.
```

## Recommendations

1. **Proceed with draft implementation** of the test-writer agent file using the recommended configuration above. The permissions model and prompt structure are appropriate for an initial release.
2. **Implement `rs-test-helper-run` first**, before the agent itself. The agent's entire workflow depends on this skill existing. `rs-test-helper-diagnose` can follow in the same iteration.
3. **Resolve open question 1** (report storage) via a brief ADR or proposal before the first release deciding whether `.runesmith/{date}-{branch}/reports/` is gitignored or committed.
4. **Add a test-reviewer agent** as a future iteration to audit the test-writer's output, closing the blind spot of self-validation.
5. **Document the production-bug protocol** in the RuneSmith runbook: when the test-writer reports a production bug, the developer should fix the code and re-invoke the test-writer, not modify the test to match the buggy behaviour.

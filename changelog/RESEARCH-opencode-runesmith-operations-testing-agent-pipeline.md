---
title: "RuneSmith Agent Pipeline Testing"
status: exploring
author: "refactorartist (Khalid Zubair)"
date: 2026-06-09
tags:
  - opencode
  - runesmith
  - testing
  - pipeline
sources:
  - knowledge: "knowledge/tooling/opencode/agents/orchestration-patterns.md"
  - knowledge: "knowledge/tooling/opencode/agents/composition-patterns.md"
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
  - knowledge: "knowledge/tooling/opencode/skills/workflow-patterns.md"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
last_audit_date: 2026-06-09
---

# RuneSmith Agent Pipeline Testing

> **Status:** Exploring — end-to-end integration testing strategy for the multi-agent pipeline.
> **Audience:** Developers building or extending the `@runicengines/opencode-runesmith` plugin.
> **Prerequisites:**
> - `agents/architect-orchestration.md` — phase gates, retry cycles, delegation patterns
> - `operations/verification.md` — smoke test checklist for plugin validation
> - `operations/agent-skills-mapping.md` — skill dependency graph per agent
> - `agents/test-writer.md` — leaf agent that produces tests
> - `operations/testing-methodology.md` — test taxonomy, failure injection patterns, mock session framework
> - `operations/testing-agent-behavior.md` — agent behavior stubs, assertion utilities, output recording

## 1. Pipeline Test Scenarios

Each scenario exercises a complete end-to-end flow through the architect's six-phase pipeline defined in `agents/architect-orchestration.md`. Scenarios are designed to be run against a **test harness** (see Section 5) that simulates OpenCode's runtime without requiring a live IDE session.

### 1.1 Happy Path

**Purpose:** Validate that the standard pipeline completes without error when every phase succeeds on the first attempt.

**Setup:**
- A mock GitHub issue requesting a feature: "Add rate-limiting to the API gateway endpoint `/api/v1/users`."
- All skill dependencies resolve (rs-discover, rs-issue-to-plan, rs-consult).
- All subagents return valid output on first invocation.
- All gates pass on first check.

**Steps:**
1. Architect receives the issue text.
2. Architect invokes `rs-issue-to-plan` skill to produce a structured plan.
3. Architect delegates to `rs-spec-writer` via `task()`.
4. Architect validates spec against Plan Gate: all required sections present.
5. Architect delegates to `rs-developer` with the approved spec.
6. Developer writes code; architect runs compile/lint check (Implementation Gate).
7. Architect delegates to `rs-reviewer`; reviewer returns zero S1/S2 findings.
8. Review Gate passes.
9. Architect delegates to `rs-test-writer`; tests pass at 100%.
10. Test Gate passes.
11. Architect delegates to `rs-tech-writer` for documentation.
12. Architect delegates to `rs-devops` for deployment simulation.
13. Deploy Gate passes.
14. Architect produces final summary to user.

**Assertions:**
- Each `task()` call resolves with `success: true`.
- Gate validation produces `pass: true` at every check.
- The final response includes the spec path, commit SHA, review summary, test report, and deploy status.
- Context propagation: the spec-writer output is referenced by the developer, the developer diff SHA is referenced in the review prompt, the review findings are referenced in the test-writer prompt.
- No phase is skipped or executed out of order.

**Failure modes to detect:**
- Architect skips a phase (e.g., goes directly from spec to test-writer without implementation).
- Subagent produces output that does not match the expected format.
- Context from one phase is missing in a downstream phase.

### 1.2 Review Failure Recovery

**Purpose:** Validate that the circuit breaker in the Review Gate routes back to the developer, and that the re-review cycle completes successfully.

**Setup:**
- Developer submits code containing a confirmed S1 bug (e.g., SQL injection vulnerability in a raw query).
- Reviewer catches the S1 issue in the first review pass.
- Developer fixes the issue on retry.

**Steps:**
1. Architect delegates to developer; code is written with an intentional SQL injection vulnerability.
2. Implementation Gate passes (code compiles, lints pass).
3. Architect delegates to reviewer; reviewer returns finding: S1 — "Raw SQL string concatenation in `user_query` parameter."
4. Review Gate fails.
5. Architect returns review finding to developer with the reviewer's full report.
6. Developer fixes the vulnerability (parameterised query).
7. Architect re-invokes the reviewer; reviewer finds no S1/S2 issues.
8. Review Gate passes on the second attempt.
9. Pipeline continues normally.

**Assertions:**
- The architect does not skip to the test-writer after the first review failure.
- The architect's prompt to the developer on retry includes the reviewer's finding text.
- The re-review does not produce false negatives (i.e., the reviewer re-checks the same vulnerability and confirms it is fixed).
- The retry counter increments correctly and does not exceed the max of 3.
- All subsequent phases proceed normally.

**Edge case:** The developer does not fix the issue correctly on the first retry. Test that a second retry loop works. On the third retry, if the issue persists, test that the architect escalates to the user rather than looping indefinitely.

### 1.3 Gate Timeout Escalation

**Purpose:** Validate that when a subagent times out or the gate condition cannot be met, the architect follows the escalation ladder (retry -> re-plan -> escalate).

**Setup:**
- Developer agent is stalled or returns an error repeatedly.
- The architect's retry budget (3x) is consumed.
- The architect must decide between re-planning and escalation.

**Steps:**
1. Architect delegates to developer; developer returns an error (e.g., "cannot parse spec format").
2. Architect retries developer with additional context. Same error.
3. Architect retries developer a second time. Same error.
4. Architect retries developer a third time. Same error.
5. Architect logs the failure and escalates to the user with a summary:
   - What was attempted (spec phase passed, developer invoked 4 times).
   - What failed (developer cannot parse spec format).
   - Suggested next steps (check spec format, try a different model, implement manually).

**Assertions:**
- The architect does not retry more than 3 times (configurable max).
- The escalation message is structured and actionable.
- The pipeline is aborted — no further phases run.
- The escalation is reported in the architect's final response to the user.

**Timeout variant:** Instead of an error, the developer `task()` call itself times out (no response after N seconds). The architect should treat this identically to an error return — retry, then escalate.

**Re-plan variant:** If the implementation gate fails after 3 developer retries with the *same* error, the architect should re-route to the `rs-spec-writer` for re-planning. If re-planning also fails implementation, then escalate.

### 1.4 Permission Boundary Enforcement

**Purpose:** Validate that an agent cannot execute operations outside its permission profile and that the architect correctly handles permission-denied errors.

**Setup:**
- Developer agent attempts a destructive shell command (`rm -rf /tmp/cache`).
- OpenCode's permission system denies the operation.
- The developer must report the denial and find an alternative approach.

**Steps:**
1. Architect delegates to developer with a task that requires clearing a build cache.
2. Developer attempts `rm -rf .cache` — permission denied (developer has `bash: "*": deny` with only `"git *": allow` and `"gh *": allow`).
3. Developer reports the denial to architect.
4. Architect recommends an alternative approach: use `git clean -fd` instead, which is permitted under `git *`.
5. Developer proceeds with the permitted command.
6. Pipeline continues.

**Assertions:**
- The permission denial propagates as a structured error (not a silent failure).
- The developer does not attempt to bypass the permission by invoking a different tool (e.g., using `bash` through `task()` to a different agent).
- The architect provides a viable alternative that stays within the permission boundary.
- The session continues without aborting.

**Test all agents' permission boundaries:**
- Reviewer attempts `edit` — must be denied (reviewer has `edit: deny` or `edit: readonly`).
- Tech-writer attempts `bash` — must be denied.
- Test-writer attempts `rm` — must be denied (test-writer only allows test-runner bash commands).
- Spec-writer attempts `task()` — must be denied (leaf agents cannot delegate).
- DevOps attempts `kubectl` — must be denied (devops has controlled bash only).

Each of these tests should produce a clear permission-denied error and a graceful recovery or reporting path.

### 1.5 Skill Chain Break

**Purpose:** Validate that when a skill in a dependency chain fails, the calling agent handles the failure gracefully (fallback, retry, or skip) rather than crashing.

**Setup:**
- The architect attempts to load `rs-issue-to-plan`, which depends on `rs-discover` having run first.
- `rs-discover` fails (e.g., codebase is too large, times out, or the repo is not found).
- The architect must proceed with a best-effort plan without discovery.

**Steps:**
1. Architect loads `rs-issue-to-plan` skill.
2. Skill internally attempts to call `rs-discover` for codebase context.
3. `rs-discover` fails — returns an error (e.g., "codebase search timed out after 30s").
4. `rs-issue-to-plan` catches the failure and continues with reduced context.
5. The plan is produced with a note: "Note: codebase discovery failed — this plan is based on issue text only."
6. Architect reviews the plan, sees the note, and may proceed or ask the user for clarification.

**Assertions:**
- The skill chain does not produce an unhandled exception.
- The calling agent (or the failed skill) logs the failure reason.
- The system degrades gracefully — the plan is still produced, albeit with less context.
- The user is informed about the degraded state.

**Test every skill chain:**

| Chain | Break Point | Expected Behaviour |
|---|---|---|
| `rs-issue-to-plan` -> `rs-discover` | `rs-discover` fails | Issue-to-plan proceeds with issue text only, annotates plan |
| `rs-pr-packager` -> `git log` | No commits in range | Packager produces empty changelog section with warning |
| `rs-changelog-manager` -> conventional commits | Commit messages do not match convention | Changelog manager skips unparseable commits, reports count |
| `rs-test-helper-run` -> `pytest` | Pytest not installed | Run skill returns clear error: "pytest not found, install with `pip install pytest`" |
| `rs-review-methodology` -> `rs-review-severity` | Severity skill not loadable | Reviewer falls back to generic severity (critical/major/minor) without detailed rubric |
| `rs-review-security` -> `rs-review-severity` | Severity skill not loadable | Security reviewer falls back to generic severity without detailed security rubric; annotates finding as "degraded severity" |

### 1.6 MCP Dependency Failure

**Purpose:** Validate that when an MCP server is unavailable, the architect adapts its approach rather than halting.

**Setup:**
- Architect requires GitHub issue context (e.g., fetching labels or comments).
- The GitHub MCP server is unreachable or returns errors.
- The architect must use an alternative strategy to gather the same information.

**Steps:**
1. Architect attempts to use the GitHub MCP tool (e.g., `gh issue view` via MCP).
2. MCP server returns unavailable (timeout or HTTP 503).
3. Architect falls back to the `gh` CLI via `bash: "gh *": allow` permission.
4. Alternative approach succeeds.
5. Pipeline continues with a note: "GitHub MCP unavailable — used gh CLI fallback."

**Assertions:**
- The MCP failure does not crash the architect.
- The fallback alternative produces functionally equivalent output.
- The fallback respects permission boundaries (the architect has `gh *` bash access).
- The user is informed of the degraded MCP state.

**Test other MCP dependencies:**
- Filesystem MCP unavailable -> architect uses raw `read` tool.
- Knowledge-base MCP unavailable -> architect uses `rs-consult` skill for manual context retrieval.

## 2. Skill Chain Testing

Skills are loaded on-demand by agents. Some skills have implicit dependencies on other skills having loaded first. These chains must be tested for correct resolution order, error propagation, and fallback behaviour.

### 2.1 Dependency Resolution Order

**Test:** rs-issue-to-plan requires rs-discover to run first.

**Setup:** Mock the skill loading subsystem. Configure it so that `rs-issue-to-plan` is loaded without `rs-discover` having been loaded.

**Expected result:** The agent prompt or skill resolution engine detects the missing dependency and either:
- Loads `rs-discover` automatically (if the chain is declared), or
- Returns a clear error: "rs-discover must be loaded before rs-issue-to-plan."

**Implementation check:** The `rs-issue-to-plan` SKILL.md should declare its dependency in frontmatter:

```yaml
depends_on:
  - skill: "rs-discover"
    order: before
```

This is a proposed frontmatter field for skill files. If not implemented, the dependency is implicit and must be documented in the skill file's preamble.

### 2.2 Chain Resolution Table

| Source Skill | Depends On | Nature of Dependency | Test |
|---|---|---|---|
| `rs-issue-to-plan` | `rs-discover` | Data: needs codebase structure to produce a plan | Load in wrong order — verify error or auto-load |
| `rs-pr-packager` | `git log` (bash) | Data: needs commit history for PR description | Mock empty commit range — verify warning |
| `rs-changelog-manager` | conventional commits | Data: parses commit messages by type | Feed non-conventional commits — verify skip |
| `rs-test-helper-diagnose` | `rs-test-helper-run` | Data: needs test output from run skill | Feed output that was not produced by the run skill — verify it still parses |
| `rs-review-security` | `rs-review-severity` | Order: security checklist uses severity classification | Load security before severity — verify it uses default severity |
| `rs-scratchpad` | (none) | Root skill — no dependencies | Always loaded first by all agents |

### 2.3 Failure Propagation Test Matrix

| Scenario | Failure | Expected Propagation |
|---|---|---|
| Skill A fails, Skill B depends on A | A throws error | B receives `null` or empty context from A, produces degraded output |
| Skill A times out, Skill B depends on A | A exceeds time limit | B proceeds without A's data, logs warning |
| Skill A returns wrong type, Skill B depends on A | A returns string instead of object | B handles type mismatch gracefully or logs error |
| Skill A loads but has internal error, B depends on A | A's output is incomplete | B detects missing fields, uses defaults |
| Nested chain: A -> B -> C, B fails | B fails | C does not load; A may retry B or degrade |

For each scenario, verify:
- The process does not crash.
- A log entry is written with the failure reason.
- The calling agent can continue (with reduced context or by skipping the failed skill).
- The user is informed of the degraded state when the degradation is meaningful.

### 2.4 Skill Dependency Declaration

If skill files declare dependencies via frontmatter (a proposed enhancement), the test harness should validate the dependency graph before any skill loads:

```typescript
function validateSkillGraph(skills: SkillDeclaration[]): ValidationResult {
  // Check for circular dependencies
  // Check that all referenced dependencies exist
  // Check dependency ordering constraints
  // Report missing or extraneous skills
}
```

This pre-validation prevents runtime failures from misconfigured skill chains.

## 3. Gate Failure Recovery Tests

Phase gates defined in `agents/architect-orchestration.md` have circuit breakers with configurable retry limits (default 3). These tests validate the recovery behaviour at each gate.

### 3.1 Plan Gate Recovery

**Scenario:** Spec-writer produces a spec with a missing section.

1. Spec-writer returns spec without "Acceptance Criteria" section.
2. Architect rejects at Plan Gate. Returns spec with feedback: "Missing Acceptance Criteria section."
3. Spec-writer revises and adds the section.
4. Architect re-validates. Plan Gate passes.

**Test variants:**
- Spec still missing section after 3 retries -> architect escalates to user.
- Spec rejected for different reasons each time (moving goalposts) -> architect should detect inconsistency and escalate rather than retry infinitely.
- Spec is approved but contains contradictions (e.g., "use MySQL" in architecture and "use PostgreSQL" in implementation). Architect should detect contradictions and ask spec-writer to resolve.

### 3.2 Implementation Gate Recovery

**Scenario:** Developer's code fails lint check.

1. Developer writes code with lint errors (e.g., unused import, missing semicolon).
2. Implementation Gate runs `npm run lint` -> fails with 3 errors.
3. Architect returns lint output to developer.
4. Developer fixes lint errors.
5. Implementation Gate re-runs -> passes.

**Test variants:**
- Same lint error persists across 3 retries -> architect re-routes to spec-writer for re-planning (the approach itself may be incompatible with the codebase conventions).
- Build fails with a cryptic error (e.g., missing dependency) -> architect should attempt `npm install` or `go mod tidy` before returning to developer.
- Developer introduces a regression (new code breaks existing tests) -> architect should detect test failures during implementation gate if the gate includes a compile check.

### 3.3 Review Gate Recovery

**Scenario:** Reviewer returns S2 finding on first pass, S3 finding on second pass, passes on third.

1. Developer submits code.
2. Reviewer returns: S2 — "No input validation on user-supplied email."
3. Architect routes to developer for fix.
4. Developer fixes email validation.
5. Reviewer returns: S3 — "Email validation error message could be more descriptive."
6. Architect routes to developer again (S3s are allowed, but architect may still pass or request fix based on policy).
7. Developer improves error message.
8. Reviewer returns: pass (no S1/S2, max 2 S3).
9. Review Gate passes.

**Test variants:**
- Reviewer consistently returns S1 findings on the same issue across 3 rounds -> architect invokes a fresh reviewer instance to eliminate reviewer bias (as specified in architect-orchestration.md).
- Reviewer misses an S1 issue that the architect detects -> architect should flag the missed issue and request re-review.
- Reviewer returns contradictory findings (e.g., "code is correct" and "feature is incomplete") -> architect identifies the contradiction and asks for clarification.

### 3.4 Test Gate Recovery

**Scenario:** Tests fail due to a genuine code bug (not a test correctness issue).

1. Test-writer writes tests and runs them. 2 out of 15 tests fail.
2. Test Gate fails. Architect reads the failure stack trace.
3. Root cause is in production code (e.g., missing null check).
4. Architect routes to developer with the test failure output.
5. Developer fixes the null check.
6. Test-writer re-runs tests. All 15 pass.
7. Test Gate passes.

**Test variants:**
- Root cause is a test bug (incorrect assertion) -> architect routes to test-writer instead of developer.
- Tests are flaky (fail on run 1, pass on run 2) -> architect should re-run up to 3 times before marking as flaky.
- Coverage gap is detected (S1 — critical path untested) -> architect routes to test-writer for additional coverage.
- Pre-existing test failures in the codebase (test infrastructure issue) -> architect must distinguish pre-existing failures from regressions. Options: run tests against a clean baseline first, or flag the pre-existing failures in the test report.

### 3.5 Deploy Gate Recovery

**Scenario:** Deployment succeeds but health check fails.

1. DevOps deploys the change.
2. Health check endpoint returns 503.
3. Deploy Gate fails.
4. Architect instructs DevOps to rollback.
5. DevOps rolls back to previous known-good version.
6. Health check on rolled-back version returns 200.
7. Architect reports: "Deploy failed — health check returned 503 after deployment. Rolled back to v1.2.3. Possible causes: [list]."

**Test variants:**
- Rollback also fails -> architect escalates to user (manual intervention required).
- Health check passes initially but fails after 60 seconds (delayed failure) -> architect should run health check at intervals (30s, 60s, 120s) before declaring success.
- Deployment itself fails (build step error) -> architect returns to developer without attempting rollback.

### 3.6 Multi-Gate Cascade Failure

**Scenario:** Three consecutive gates fail with escalating severity.

1. Plan Gate fails 3 times (spec-writer cannot produce a valid spec).
2. Architect escalates to user: "Spec could not be approved after 3 attempts."
3. User provides additional clarification.
4. Architect re-starts pipeline from Plan Gate with the new information.
5. This time, Plan Gate passes.
6. Implementation Gate fails 3 times (developer cannot satisfy lint).
7. Architect escalates again: "Implementation failed after 3 lint retries. Consider re-planning the approach."
8. Pipeline is paused. User decides next action.

**Assertions:**
- Each escalation is separate and actionable.
- Escalation summary includes retry counts and failure context.
- The pipeline is paused at the escalation point — it does not automatically advance.
- User input can unblock the pipeline by providing new information or changing strategy.

### 3.7 Gate Retry Budget Exhaustion

Test that the architect's gate retry budget is correctly counted per gate, not globally shared:

| Attempt | Action | Retry Count |
|---|---|---|
| 1 | Developer writes code, lint fails | Gate.retries = 1 |
| 2 | Developer fixes, lint fails (same error) | Gate.retries = 2 |
| 3 | Developer fixes, lint fails | Gate.retries = 3 |
| 4 | Architect re-routes to spec-writer for re-plan | Gate.retries reset for new phase |

After re-planning, the implementation gate should start with `retries = 0` for the new developer attempt. Test this with a scenario where:
- Developer exhausts 3 retries on implementation gate.
- Spec-writer re-plans with a different technical approach.
- New developer attempt with the re-planned approach should start fresh (not inherit the previous gate's retry count).

## 4. Multi-Agent Orchestration Tests

These tests validate the architect's delegation patterns, ensuring agents are invoked in the correct order, with proper context, and with the right concurrency characteristics.

### 4.1 Sequential Delegation

**Purpose:** Verify that the architect invokes agents in strict order and does not start the next phase before the previous phase's gate passes.

**Test:** Run the full happy path pipeline with instrumentation that records the order of `task()` calls and gate evaluations.

**Assertions:**
- `task("rs-spec-writer")` precedes `task("rs-developer")`.
- Implementation Gate check precedes `task("rs-reviewer")`.
- Review Gate check precedes `task("rs-test-writer")`.
- No `task()` call starts before the previous phase's gate produces `pass: true`.
- If the pipeline is aborted mid-way (e.g., Plan Gate fails 3 times), no subsequent phases are invoked.

**Enforcement mechanism:** The test harness should inject a sequence validator that logs every `task()` call and gate evaluation, then compares the sequence against the expected DAG.

### 4.2 Parallel Delegation (Future)

**Purpose:** Validate that the architect can delegate to multiple leaf agents simultaneously when phases are independent.

**Current state:** The architect's pipeline is strictly sequential. Parallel delegation is a potential future optimisation for independent work items (e.g., test-writer and tech-writer could run concurrently after implementation and review pass).

**Test (future):**
1. Implementation Gate passes.
2. Review Gate passes.
3. Architect delegates to `rs-test-writer` and `rs-tech-writer` simultaneously via two `task()` calls.
4. Both run concurrently.
5. Architect collects both results.
6. Both gates (Test Gate, Docs Gate) must pass before proceeding to deploy.

**Assertions (future):**
- Concurrent task invocations do not interfere with each other (no shared state conflicts).
- Architect correctly waits for both to complete before evaluating gates.
- Context does not get interleaved or corrupted.
- Error in one task does not cancel the other (each task is isolated).

### 4.3 Conditional Delegation

**Purpose:** Validate that the architect can change the delegation path based on intermediate results.

**Scenario:** Reviewer returns a finding that the spec is incomplete (new requirements discovered during review). Instead of routing back to the developer, the architect routes back to the spec-writer to revise the spec.

1. Developer implements code based on the approved spec.
2. Reviewer finds: "The spec does not cover the `/api/v1/users/:id` endpoint, which this code touches. Spec must be updated."
3. Review Gate fails with a re-plan recommendation.
4. Architect routes to spec-writer: "Please update the spec to cover the `/api/v1/users/:id` endpoint."
5. Spec-writer updates the spec.
6. Plan Gate passes on re-validation.
7. Developer re-implements based on the updated spec.
8. Pipeline continues.

**Assertions:**
- The architect correctly identifies when a review finding requires re-planning vs re-implementation.
- The spec-writer receives the review findings as context.
- The revised spec does not contradict the parts of the original spec that were already implemented.
- The developer receives both the original and revised spec sections.

**Other conditional delegation paths to test:**
- Test-writer finds coverage gap requiring spec revision -> route to spec-writer (not developer).
- DevOps finds deployment requirement missing from spec -> route to spec-writer.
- Tech-writer finds API docs inconsistent with implementation -> route to developer.

### 4.4 Context Propagation

**Purpose:** Validate that task description, repo context, and phase constraints pass correctly between agents without data loss or corruption.

**Test framework:** Instrument each `task()` call to capture the prompt sent to each subagent. Verify that the prompt contains:

1. **Task context:** The original user request (or a synthesised summary).
2. **Phase context:** The output of the previous phase (spec for developer, diff for reviewer, etc.).
3. **Constraints:** Phase-specific rules (e.g., "do not modify files outside `src/`").
4. **Output location:** Where to write files.

**Assertions for each delegation edge:**

| Edge | Context Expected | Test |
|---|---|---|
| Architect -> Spec-writer | Full issue text, acceptance criteria, codebase structure from rs-discover | Prompt contains issue text; mentions affected files |
| Architect -> Developer | Approved spec, diff boundaries, lint rules | Prompt references spec filename; mentions `src/` scope restriction |
| Architect -> Reviewer | Diff SHA, implementation notes, severiy rubric | Prompt contains `git diff` output; mentions S1/S2/S3 criteria |
| Architect -> Test-writer | Spec, diff SHA, review findings, test strategy | Prompt references spec acceptance criteria; lists review findings as context |
| Architect -> Tech-writer | Spec, diff summary, changelog requirements | Prompt contains new feature description; asks for changelog entry |
| Architect -> DevOps | Deployment instructions, rollback plan, health check URL | Prompt contains deployment target; health check endpoint |

**Corruption tests:**
- Inject special characters in the issue text (e.g., `{{template}}`, `${variable}`, `null byte`) and verify they are not interpreted as template directives in downstream prompts.
- Inject very long strings (10,000+ characters) and verify they are not truncated mid-sentence in a way that breaks meaning.
- Inject JSON content in the issue text and verify it is not accidentally merged with structured data in the prompt.

## 5. Test Harness Design

Running pipeline tests against a live OpenCode session is slow, non-deterministic, and expensive (each invocation consumes API credits). A test harness is needed to simulate the runtime environment and produce deterministic results.

### 5.1 Mock LLM Responses

**Problem:** The architect and subagents rely on LLM calls to generate responses. Real LLM calls are non-deterministic — the same prompt can produce different outputs.

**Solution:** Replace the LLM backend with a mock that returns pre-recorded responses based on the input prompt.

**Architecture:**

```typescript
interface MockLLMConfig {
  responses: Map<string, MockResponse>;
  defaultResponse: MockResponse;
  latency: { min: number; max: number }; // simulated thinking time
}

interface MockResponse {
  content: string;
  toolCalls?: ToolCall[];
  finishReason: "stop" | "length" | "error";
}
```

The mock matches incoming prompts against a registry of known inputs using fuzzy matching (contains substring, matches regex, or exact match). For pipeline tests, the registry is populated with:

- Architect prompt for spec-writer delegation -> returns "Task accepted, writing spec..."
- Spec-writer output -> returns a pre-written valid spec.
- Architect prompt for developer delegation -> returns "Implementing..."
- Developer output -> returns a pre-written diff.
- Etc.

**Determinism guarantee:** With a fully populated response registry and zero latency, the same test case always produces the same sequence of `task()` calls, gate evaluations, and final output. This enables snapshot testing (see 5.4).

**Partial mock strategy:** In practice, not all responses need to be mocked. The test harness should support a hybrid mode where:
- Specific agents are mocked (e.g., mock the developer, use real LLM for the reviewer).
- Specific skills are mocked (e.g., mock `rs-discover`, use real `rs-issue-to-plan`).
- Gate validations are always real (no mock for compile/lint checks — these run against actual file state).

### 5.2 Fake OpenCode Session

**Problem:** The pipeline depends on OpenCode's runtime (agent resolution, `task()` API, permission enforcement, skill loading). Testing against a real OpenCode process requires a full IDE session.

**Solution:** A fake OpenCode session that implements a minimal subset of the runtime API:

```typescript
class FakeOpenCodeSession {
  agents: Map<string, AgentDefinition>;
  skills: Map<string, SkillDefinition>;
  filesystem: VirtualFS;
  permissionEngine: PermissionEngine;
  taskLog: TaskInvocation[];

  async task(name: string, prompt: string): Promise<TaskResult>;
  async skill(name: string, args?: any): Promise<SkillResult>;
  async read(path: string): Promise<string>;
  async edit(path: string, content: string): Promise<void>;
  async bash(command: string): Promise<BashResult>;
  async glob(pattern: string): Promise<string[]>;
  async grep(pattern: string, path?: string): Promise<GrepResult[]>;
}
```

The fake session replaces:
- **`task()`**: Looks up the agent in the registry, invokes its mock LLM (see 5.1), and returns a simulated response.
- **`skill()`**: Looks up the skill in the registry, executes its mock implementation (or simulates loading its instructions).
- **`read/edit/bash/glob/grep`**: Operates on a virtual in-memory filesystem instead of the real disk.
- **Permission engine**: Evaluates the same permission rules as the real OpenCode runtime, producing identical `allow`/`deny` decisions.

The fake session records every invocation to `taskLog` for post-test assertion.

> **Note:** The `FakeOpenCodeSession` follows the same abstraction pattern as `mock-opencode-session.ts` (defined in testing-methodology.md §5.1) but is specialized for pipeline-level integration scenarios (multi-agent delegation, gate failures, skill chains). A shared base class should be extracted during implementation.

### 5.3 Simulated Agent Timeouts and Failures

**Problem:** Testing error recovery (Section 3) requires agents to fail or time out in controlled ways. In a live system, failures are unpredictable.

**Solution:** The test harness supports failure injection via test configuration:

```typescript
interface FailureInjection {
  agent: string;
  phase: "plan" | "implement" | "review" | "test" | "deploy";
  failureMode: "timeout" | "error" | "invalid-output" | "permission-denied";
  retryCount: number; // fail on this specific retry (0 = first, 1 = second, etc.)
  gate: string; // fail at this specific gate
}
```

Example: Inject a developer timeout on the second retry:

```json
{
  "agent": "rs-developer",
  "phase": "implement",
  "failureMode": "timeout",
  "retryCount": 2
}
```

When this injection is active, the developer agent returns success on the first invocation, times out on the second, and succeeds on the third. The test verifies that the architect handles the timeout correctly.

**Supported failure modes:**

| Mode | Behaviour |
|---|---|
| `timeout` | `task()` call hangs for configurable duration, then returns timeout error |
| `error` | `task()` returns an error response with a configurable message |
| `invalid-output` | Agent returns malformed output (wrong format, missing fields, corrupted JSON) |
| `permission-denied` | Agent's attempted operation is denied by the permission engine |
| `gate-fail` | Gate validation returns `fail` with a configurable reason, regardless of agent output |
| `skill-fail` | Skill loading returns an error |
| `mcp-unavailable` | MCP server returns service unavailable |

### 5.4 Record/Replay

**Problem:** Real agent interactions are valuable for regression testing but expensive to recreate.

**Solution:** A record/replay layer that captures real agent interactions during a live pipeline run and replays them deterministically in the test harness.

**Record format:**

```json
{
  "session": "2026-06-09-feat-123",
  "interactions": [
    {
      "timestamp": "2026-06-09T10:00:00Z",
      "caller": "architect",
      "tool": "task",
      "args": { "name": "rs-developer", "prompt": "..." },
      "result": { "success": true, "output": "..." }
    },
    {
      "timestamp": "2026-06-09T10:00:05Z",
      "caller": "architect",
      "tool": "bash",
      "args": { "command": "npm run lint" },
      "result": { "stdout": "...", "stderr": "", "exitCode": 0 }
    }
  ]
}
```

The record file captures every tool invocation during a pipeline run, including inputs and outputs.

**Replay mode:** The test harness loads a record file and uses it as the response registry for the mock LLM. When the architect invokes the same tool with matching arguments, the harness returns the recorded result. This enables:

- **Regression testing:** Record a successful pipeline run. After making changes to the pipeline logic, replay the same interactions and verify the result is identical.
- **Debugging:** Record a failed pipeline run. Replay it step-by-step with additional logging to understand the failure.
- **Performance analysis:** Measure the timing of each interaction without running against a real LLM.

**Matching strategy:** Fuzzy matching (Jaccard similarity on prompt tokens) rather than exact matching, because prompts may vary slightly between runs (e.g., different timestamps, branch names, or SHA values). The harness should support variable substitution for known dynamic fields (`{date}`, `{branch}`, `{sha}`).

### 5.5 Pipeline Test Runner

A dedicated test runner orchestrates multi-step pipeline tests. It is distinct from a standard unit test runner because it must manage sequential phases, gate evaluations, and retry cycles.

**Runner API:**

```typescript
class PipelineTestRunner {
  constructor(config: {
    session: FakeOpenCodeSession;
    architect: AgentDefinition;
    initialTask: string;
  });

  // Run the pipeline to completion or escalation
  async run(): Promise<PipelineResult>;

  // Assert that the pipeline followed a specific sequence
  assertSequence(expected: PhaseSequence): void;

  // Assert that a specific gate passed or failed
  assertGate(name: string, expected: "pass" | "fail"): void;

  // Assert that the pipeline escalated
  assertEscalation(expected: EscalationExpectation): void;

  // Assert context propagated correctly between phases
  assertContextPropagation(phase: string, expectedFields: string[]): void;

  // Get the full invocation log for inspection
  getInvocationLog(): InvocationEntry[];
}

interface PipelineResult {
  status: "completed" | "escalated" | "aborted";
  phases: PhaseResult[];
  gates: GateResult[];
  escalation?: EscalationReport;
  finalResponse: string;
  duration: number;
}
```

> **Note:** Pipeline test results (gate pass/fail, retry counts, escalation state) should conform to the structured JSON report schema defined in testing-methodology.md §5.4.

**Test structure:**

```typescript
describe("Pipeline - Happy Path", () => {
  it("completes all six phases successfully", async () => {
    const session = new FakeOpenCodeSession();
    session.registerAgent("rs-spec-writer", validSpecResponse);
    session.registerAgent("rs-developer", validImplementationResponse);
    session.registerAgent("rs-reviewer", validReviewResponse);
    session.registerAgent("rs-test-writer", validTestResponse);
    session.registerAgent("rs-tech-writer", validDocResponse);
    session.registerAgent("rs-devops", validDeployResponse);

    const runner = new PipelineTestRunner({
      session,
      architect: runesmithArchitect,
      initialTask: "Add rate-limiting to API gateway",
    });

    const result = await runner.run();

    expect(result.status).toBe("completed");
    runner.assertSequence([
      "spec-writer", "plan-gate",
      "developer", "impl-gate",
      "reviewer", "review-gate",
      "test-writer", "test-gate",
      "tech-writer",
      "devops", "deploy-gate",
    ]);
    result.gates.forEach(g => expect(g.result).toBe("pass"));
  });
});
```

**Failure injection tests:**

```typescript
describe("Pipeline - Review Failure", () => {
  it("recovers from S1 finding and completes", async () => {
    const session = new FakeOpenCodeSession();
    session.registerAgent("rs-spec-writer", validSpecResponse);
    session.registerAgent("rs-developer", [
      vulnerableCodeResponse,     // first invocation: has S1 bug
      patchedCodeResponse,        // second invocation: fixed
    ]);
    session.registerAgent("rs-reviewer", [
      s1FindingResponse,          // first review: catches S1
      cleanReviewResponse,        // second review: approves
    ]);
    session.registerAgent("rs-test-writer", validTestResponse);
    session.registerAgent("rs-tech-writer", validDocResponse);
    session.registerAgent("rs-devops", validDeployResponse);

    const runner = new PipelineTestRunner({ session, architect, initialTask });

    const result = await runner.run();

    expect(result.status).toBe("completed");
    expect(runner.getInvocationLog().filter(i => i.agent === "rs-developer").length).toBe(2);
    expect(runner.getInvocationLog().filter(i => i.agent === "rs-reviewer").length).toBe(2);
    expect(result.gates.find(g => g.name === "review-gate")?.retries).toBe(1);
  });

  it("escalates after 3 failed review rounds", async () => {
    // Similar setup but reviewer always returns S1 findings
    // Verify escalation message, pipeline abort, no further phases
  });
});
```

**Gate timeout test:**

```typescript
describe("Pipeline - Gate Timeout", () => {
  it("escalates after 3 developer timeouts", async () => {
    const session = new FakeOpenCodeSession();
    // Inject timeout on developer: fail 3 times
    session.injectFailure({
      agent: "rs-developer",
      failureMode: "timeout",
      retryCount: [0, 1, 2], // fail on first 3 attempts
    });
    // Fourth attempt (after re-plan) should not happen if escalation is correct

    const runner = new PipelineTestRunner({ session, architect, initialTask });
    const result = await runner.run();

    expect(result.status).toBe("escalated");
    expect(result.escalation?.summary).toContain("developer");
    expect(result.escalation?.summary).toContain("3");
    // Verify no spec-writer re-plan was attempted
    const specWriterCalls = runner.getInvocationLog()
      .filter(i => i.agent === "rs-spec-writer");
    expect(specWriterCalls.length).toBe(0);
  });
});
```

### 5.6 Test Environment Configuration

The test harness must be configurable to match different scenarios:

```typescript
interface TestEnvironmentConfig {
  // Agents available in this test
  agents: string[];

  // Skills available in this test
  skills: string[];

  // Permission profiles active
  permissions: PermissionProfile[];

  // MCP servers available (or unavailable)
  mcpServers: { name: string; available: boolean }[];

  // Initial filesystem state (virtual files and directories)
  initialFiles: VirtualFileEntry[];

  // Initial git state (commits, branches, stashes)
  gitState: GitState;

  // Maximum pipeline retries per gate
  maxRetriesPerGate: number;

  // Thinking token budget for each agent
  thinkingTokens: Record<string, number>;
}
```

This configuration is passed as a JSON fixture file, enabling the same test suite to run against different plugin versions or configurations:

```json
{
  "agents": ["rs-architect", "rs-spec-writer", "rs-developer", "rs-reviewer", "rs-test-writer", "rs-tech-writer", "rs-devops"],
  "skills": ["rs-issue-to-plan", "rs-discover", "rs-consult", "rs-test-helper-run", "rs-test-helper-diagnose", "rs-changelog-manager", "rs-scratchpad"],
  "permissions": ["architect-profile", "developer-profile", "reviewer-profile", "test-writer-profile", "leaf-agent-profile"],
  "mcpServers": [{ "name": "github", "available": true }, { "name": "knowledge-base", "available": true }],
  "maxRetriesPerGate": 3
}
```

### 5.7 Continuous Integration Integration

The test harness is designed to run in CI without external dependencies:

```
Pipeline:
  1. Install test dependencies (ts-node or bun for TypeScript, or Python)
  2. Load test environment configuration (JSON fixtures)
  3. For each test scenario:
     a. Create FakeOpenCodeSession with the scenario's mock responses
     b. Run PipelineTestRunner
     c. Assert expected sequence, gate results, and escalation state
  4. Generate test report (JUnit XML for CI dashboard integration)
  5. Exit non-zero if any test fails
```

Because the harness uses mocked LLM responses and a virtual filesystem, tests complete in milliseconds rather than minutes. The entire pipeline test suite (50+ scenarios) should finish within 30 seconds.

Record/replay files from real sessions can be stored in the repository under `tests/fixtures/recordings/` and replayed in CI to catch regressions between plugin versions.

## 6. Open Questions

1. Should the test harness live inside the `@runicengines/opencode-runesmith` plugin repository or in a separate `opencode-runesmith-test` package? A separate package keeps test infrastructure out of the plugin itself, but adds a dependency to manage.

2. Should gateway validation logic (compile checks, lint checks, health checks) be mocked in the test harness or run against real tools? Mocking is faster and deterministic, but real tool execution catches more bugs. A hybrid approach (mock for most tests, real execution for a subset of integration tests) may be optimal.

3. How should the record/replay layer handle prompts that differ from the recorded version? Fuzzy matching thresholds and variable substitution rules need to be tuned to avoid false mismatches (replay fails when it should succeed) or false matches (replay uses a wrong response).

4. Should the test harness simulate token consumption tracking? The architect's thinking budget (16000 tokens) is a constraint that could affect pipeline behaviour. A simulated token tracker would help identify scenarios where context pressure causes the model to skip steps.

5. Can the fake OpenCode session be reused for testing other plugins? If the session API is general enough (agent resolution, skill loading, permission evaluation), it could become a shared test utility for the OpenCode ecosystem.

## 7. Summary and Recommendations

### Test Priority Matrix

| Category | Priority | Tests | Effort | Risk if Skipped |
|---|---|---|---|---|
| Happy path | P0 | 1 scenario | Low | Pipeline may not complete at all |
| Review recovery | P0 | 3 scenarios (S1, S2, max retry) | Medium | Common failure mode; unrecoverable without testing |
| Gate timeout | P0 | 2 scenarios (timeout, retry budget) | Medium | Infinite loops or silent escalations |
| Permission boundary | P0 | 6 scenarios (one per agent type) | Medium | Security bypass |
| Skill chain break | P1 | 5 chain tests | Medium | Silent degradation without logging |
| Context propagation | P1 | 6 edge tests + 3 corruption tests | High | Data loss between phases |
| Conditional delegation | P1 | 4 scenarios | High | Architect cannot adapt to intermediate results |
| MCP dependency | P2 | 3 scenarios | Low | Fallback logic not exercised |
| Parallel delegation | P2 | 1 scenario (future) | High | Not yet implemented; test when feature is added |
| Record/replay | P2 | Fixture infrastructure | High | Valuable for regression but not MVP-blocking |

### First Iteration (MVP)

Implement the test harness with these capabilities:

1. **FakeOpenCodeSession** with mock LLM responses and virtual filesystem.
2. **PipelineTestRunner** with sequence, gate, and escalation assertions.
3. **P0 and P1 test scenarios** (happy path, review recovery, gate timeout, permission boundary, skill chain break, context propagation).
4. **Failure injection** for timeout, error, and permission-denied modes.
5. **CI integration** running 20+ scenarios in under 30 seconds.
6. **Pass rate thresholds:** P0 pipelines must achieve 100% pass rate (per testing-methodology.md §1.5 requirements). P1 secondary pipelines target >= 90%.

### Second Iteration

Add:

1. Record/replay layer for regression testing.
2. Conditional delegation tests.
3. MCP dependency failure tests.
4. Token consumption tracking in the test harness.

### Third Iteration

Add:

1. Parallel delegation tests (once the feature is implemented in the architect).
2. Performance benchmarks (pipeline completion time, token consumption per phase).
3. Snapshot testing (compare pipeline output against golden files).

## See Also

- Phase gates and retry logic: `agents/architect-orchestration.md`
- Plugin smoke test checklist: `operations/verification.md`
- Skill dependency mapping: `operations/agent-skills-mapping.md`
- Test writer agent design: `agents/test-writer.md`
- OpenCode agents documentation: `https://opencode.ai/docs/agents`
- OpenCode skills documentation: `https://opencode.ai/docs/skills`

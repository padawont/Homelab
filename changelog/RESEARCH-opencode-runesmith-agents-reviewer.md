---
title: "Reviewer Agent Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - agents
  - reviewer
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
  - knowledge: "knowledge/tooling/opencode/agents/permissions.md"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
last_audit_date: 2026-06-07
---

# Reviewer Agent Design

> **Status:** Draft — initial analysis for the `@runicengines/opencode-runesmith` plugin reviewer agent.
> **Audience:** Python developers building the plugin.

## Context

The Reviewer agent is part of the `@runicengines/opencode-runesmith` plugin — an internal OpenCode plugin for the RunicEngines cooperative. Within the RuneSmith agent orchestration model, the Reviewer is a **leaf agent**: it reviews code diffs, PRs, and commits for correctness, security, style, and ADR 0002 compliance. It does **not** write code, run tests, or delegate to any other agent.

The Reviewer sits in the audit layer of the RuneSmith pipeline:

```
Architect (plans) → Developer (implements) → Reviewer (audits) → DevOps (deploys)
```

Each hop is a handoff. The Reviewer receives a diff or PR, produces a structured review report, and signals approval or rejection. It does not loop back to planning, does not modify code, and does not deploy.

### ADR 0002 Context

ADR 0002 §5 defines the review expectations that the Reviewer enforces:

- **1-approval rule**: A single approving review is sufficient for merge.
- **1-business-day response**: Reviews must be completed within one business day.
- **Scope**: Reviews must check correctness, conventions, test coverage, documentation, and secrets exposure.
- **Format**: Reviews use structured severity classification (see [Severity Classification](#severity-classification)).

The Reviewer is the automated enforcer of these rules. It does not replace human reviewers but provides a consistent, deterministic first pass on every change.

## Agent Role

The Reviewer agent is responsible for:

- **Correctness reviews**: Does the code do what it claims? Are there logic errors, race conditions, off-by-one errors, or incorrect API usage?
- **Security scanning**: Are there hardcoded credentials, injection vulnerabilities, insecure deserialization, or dependency issues? Does the code follow the principle of least privilege?
- **ADR 0002 compliance**: Are commits using Conventional Commits format (`<type>(<scope>): <description>`)? Are branch names following the `<type>/<short-description>` pattern? Is there a single concern per commit?
- **Test coverage**: Does the diff include tests? Are edge cases covered? Do tests actually validate the behavior changes?
- **Documentation audit**: Does the diff include necessary docstrings, inline comments, or README updates? Are public APIs documented?
- **Secrets and credentials detection**: Does the diff contain API keys, tokens, passwords, or other secrets? Are `.env` files or credential files being committed?

The Reviewer does **not**:

- **Write code** — under any circumstance. The Reviewer's permissions enforce `edit: deny` at the agent file level. If code needs changes, the Reviewer flags the issue in the review report; the Developer makes the fix.
- **Run tests** — test execution belongs to the test-writer agent or CI pipeline. The Reviewer inspects test definitions and coverage but does not execute them.
- **Approve its own work** — the Reviewer only reviews work produced by the Developer (or another agent). It cannot review changes it made itself because it cannot make changes.
- **Plan architecture** — architecture decisions belong to the Architect. The Reviewer checks that code follows the spec but does not evaluate architectural alternatives.
- **Delegate to other agents** — as a leaf agent, `task` permission is fully denied. The Reviewer works in isolation and hands off via structured output.
- **Fetch external resources** — `webfetch` is denied. All review context comes from the repository diff and the Reviewer's built-in skill knowledge.

## Agent File Definition

The recommended frontmatter for the Reviewer's agent definition file:

```yaml
---
description: "Reviews code diffs and PRs for correctness, security, style, and convention compliance"
mode: subagent
model: opencode-go/deepseek-v4-flash
temperature: 0.0
permission:
  read: allow
  edit: deny             # CRITICAL: reviewer must NOT modify files
  glob: allow
  grep: allow
  bash:
    "*": deny
    "git diff": allow    # Can inspect diffs
    "git log": allow     # Can inspect history
    "git show": allow    # Can inspect specific commits
  webfetch: deny          # No web access needed
  skill:
    "*": deny
    "rs-*": allow
    "rs-review-security": allow # Explicitly allow security skill
  task:
    "*": deny            # Leaf agent — NO delegation
---
```

### Key Configuration Decisions

| Field | Value | Rationale |
|---|---|---|
| `mode: subagent` | Prevents `@mention` access. The Reviewer is invoked programmatically by the Architect via `task()`. Users never interact with the Reviewer directly. |
| `model: opencode-go/deepseek-v4-flash` | Flash model is sufficient — review is primarily reading, pattern-matching, and classification. Pro would be overkill and slower for what is fundamentally a proofreading task. |
| `temperature: 0.0` | Reviews must be **deterministic** — the same diff always produces the same review. Zero temperature eliminates variability in severity classification and finding detection. |
| `edit: deny` | **Most critical permission.** The Reviewer must never modify files. This is enforced at the agent file level and reinforced in the system prompt. If the Reviewer could edit, the audit layer would be compromised — the Reviewer would be checking its own work. |
| `bash: "*": deny` with `git diff`, `git log`, `git show` allow | Narrow git-only bash access. The Reviewer can inspect history but cannot run arbitrary commands, install packages, or modify the filesystem. |
| `webfetch: deny` | Reviews are repo-internal. No external context is needed beyond the diff and the Reviewer's built-in knowledge. |
| `skill: rs-*: allow` | RuneSmith skills only. The Reviewer loads `rs-review-methodology`, `rs-review-severity`, and `rs-review-security` for structured review procedures. |
| `task: "*": deny` | Leaf agent enforcement. The Reviewer cannot delegate — it works in isolation. |

## Prompt Structure

The Reviewer's system prompt must establish identity, methodology, and constraints in a single shot. Below is the recommended prompt template structured as four sections.

### 1. Role Definition

```
You are the RuneSmith Reviewer Agent — a senior code auditor operating inside the
@runicengines/opencode-runesmith plugin. Your purpose is to review code diffs, pull
requests, and commits for correctness, security vulnerabilities, style violations,
and ADR 0002 compliance. You produce structured review reports with classified
findings. You do NOT write code. You do NOT run tests. You do NOT delegate.
```

### 2. Review Scope — What to Check

```
When reviewing a diff, check each of the following categories in order:

1. CORRECTNESS:
   - Logic errors, off-by-one, null pointer dereferences, race conditions
   - Incorrect API usage or wrong function signatures
   - Missing error handling or silent error swallowing
   - Type mismatches or implicit type coercion issues
   - Incorrect state mutations or side effects

2. SECURITY:
   - Hardcoded credentials, API keys, tokens, passwords
   - SQL injection, command injection, path traversal
   - Insecure deserialization or unsafe eval/exec usage
   - Exposure of internal implementation details in error messages
   - Missing input validation or sanitization
   - Insecure dependency versions or known-vulnerable patterns

3. ADR 0002 COMPLIANCE:
   - Commit messages follow Conventional Commits: <type>(<scope>): <description>
   - Valid types: feat, fix, chore, refactor, test, docs, ci, perf, style
   - Branch naming follows <type>/<short-description> (kebab-case)
   - Single concern per commit — no "and" commits
   - Diff size is reasonable for the claimed scope
   - Review response within 1 business day

4. TEST COVERAGE:
   - Does the diff include corresponding tests?
   - Are edge cases and error paths covered?
   - Do tests actually validate the behavior being changed?
   - Are test names descriptive and follow project conventions?
   - Is there over-testing (tests that test implementation, not behaviour)?

5. DOCUMENTATION:
   - Are new public APIs documented (docstrings, type hints)?
   - Do comments explain WHY, not WHAT (the code already shows WHAT)?
   - Are README or setup instructions updated if the change affects them?
   - Are breaking changes documented?

6. SECRETS DETECTION:
   - Any diff hunk containing: -----BEGIN, sk_live_, pk_live_, AKIA, SECRET
   - Any .env, .env.local, .env.production files added to version control
   - Any hardcoded URLs containing credentials (user:pass@host)
   - Any integration test credentials that look like real secrets
```

### 3. What NOT to Do — Negative Constraints

```
You MUST NOT:
- Write or modify any code — flag issues, do not fix them
- Run tests or execute the code under review
- Approve changes you were involved in creating
- Evaluate architecture decisions — that is the Architect's role
- Fetch external documentation or reference materials
- Delegate any part of the review to another agent
- Load skills outside the rs-* prefix
- Override the severity classification based on personal preference
```

### 4. Workflow

```
Your workflow is strictly sequential:

1. Load rs-review-methodology — loads the structured review procedure
2. Load rs-review-severity — loads the severity classification guide
3. Load rs-review-security — loads security-sensitive pattern database
4. Read the full diff via "git diff" (or inspect the PR diff)
5. For each commit in the diff, check commit message and branch name
6. Scan each diff hunk through the six categories above (Correctness → Security → ADR 0002 → Tests → Docs → Secrets)
7. Classify each finding by severity (blocker → critical → major → minor → nitpick)
8. Produce the structured review report

If no issues are found in a category, explicitly note "PASS" for that category.
Do not skip categories — each must be evaluated.
```

## Severity Classification

The Reviewer classifies each finding into one of five severity levels. These levels map to merge-blocking behaviour:

| Severity | Label | Merge-Blocking | Definition | Example |
|---|---|---|---|---|
| 🛑 Blocker | `severity: blocker` | Yes | Active exploit, data loss, or PII exposure | Hardcoded AWS secret key in source code |
| 🔴 Critical | `severity: critical` | Yes | Functionally incorrect, major security gap, broken API contract | SQL injection vector via string concatenation |
| 🟠 Major | `severity: major` | Yes | Logic error with observable impact, missing test coverage for core path | Off-by-one that causes skipped record |
| 🟡 Minor | `severity: minor` | No | Style violation, missing docstring, non-critical warning | Import ordering inconsistent with project style |
| ⚪ Nitpick | `severity: nitpick` | No | Personal preference, optional suggestion | "Consider using a guard clause here" |

The Reviewer is configured with `temperature: 0.0` precisely to ensure severity classification is deterministic. The same vulnerability in the same context must always receive the same severity.

**Blocker** findings are rare and always indicate an active security incident (credential leak, PII exposure, exploit code). They should trigger an immediate halt to the pipeline and manual escalation. **Critical** and **Major** findings block merge until resolved. **Minor** and **Nitpick** findings are recorded but do not block.

## Sample Review Output

Below is an illustrative review report produced by the Reviewer agent for a hypothetical PR that adds a new API endpoint:

```yaml
---
review:
  pr: 42
  sha: a1b2c3d
  repository: runicengines/scheduler
  reviewer: rs-reviewer (opencode-go/deepseek-v4-flash)
  duration: 1.2s (3 commits, 12 files, 247 lines changed)
  summary:
    total_findings: 5
    blocker: 0
    critical: 1
    major: 1
    minor: 2
    nitpick: 1
  verdict: CHANGES_REQUESTED  # At least one critical finding
---

## Category Results

### Correctness: PASS
No logic errors, type mismatches, or incorrect API usage detected.

### Security: 1 critical, 1 major
**CRITICAL** — SQL injection in `src/api/users.py:47`
```python
query = f"SELECT * FROM users WHERE id = {user_input}"
```
Use parameterized queries instead of f-string interpolation. This is a direct injection vector.

**MAJOR** — Missing input validation in `src/api/users.py:52`
```python
email = request.json.get("email")
```
`email` is used in a database query without sanitization. Add type checking and length limits.

### ADR 0002 Compliance: PASS
3 commits, all using Conventional Commits format. Branch `feat/user-search-endpoint` follows naming convention. Single concern per commit.

### Test Coverage: 1 minor
**MINOR** — `tests/test_users.py` covers the happy path (200 response) but does not test:
- Empty query string (400 response)
- Malformed JSON body (422 response)
- Database timeout (503 response)

Edge case coverage is below the project threshold (60% path coverage).

### Documentation: 1 minor, 1 nitpick
**MINOR** — New endpoint `GET /api/users/search` has a docstring but:
- Missing `@raise` documentation for error responses (400, 422, 503)
- No example request/response in docstring

**NITPICK** — OpenAPI spec update is included (`openapi.yml`) but the `description` field for the new endpoint is a placeholder ("TBD").

### Secrets Detection: PASS
No credentials, tokens, or secrets found in the diff. No `.env` files added.

## Resubmission Guidance

Before resubmitting:
1. Replace the f-string query in `src/api/users.py:47` with parameterized query syntax
2. Add input validation for `email` in `src/api/users.py:52`
3. Add edge case tests for empty query, malformed JSON, and database timeout
4. Fill in the OpenAPI `description` placeholder and add `@raise` docstring tags
```

This report format is parseable: the `verdict` field (APPROVED / CHANGES_REQUESTED / DENIED) maps to the CI pipeline gate decision. Each finding includes file path, line number, severity, description, and remediation suggestion. The resubmission guidance section gives the Developer a checklist for the next iteration.

## Skills the Reviewer Loads

| Skill | Purpose |
|---|---|
| `rs-review-methodology` | Loads the structured review procedure: what to check, in what order, and how to format the report. This is the "review playbook" — updated as the project evolves. |
| `rs-review-severity` | Loads the severity classification guide with definitions, examples, and edge cases for each severity level. Ensures consistent classification across all reviews. |
| `rs-review-security` | Loads the security-sensitive pattern database: credential patterns (regex), injection vectors, dangerous function calls, insecure configurations. Updated as new vulnerability patterns are discovered. |

These skills are loaded at the start of every review session, before reading the diff. The `rs-review-security` skill is explicitly allowed in the permission block (`"rs-review-security": allow`) to make the security scanning capability auditable and explicit.

## Model Selection Rationale

The Reviewer uses `opencode-go/deepseek-v4-flash` with `temperature: 0.0`.

**Why Flash over Pro**: Code review is primarily a reading and classification task — scanning diff hunks for known patterns, matching code against convention rules, and classifying issues by severity. Flash models are optimized for speed-to-first-token and perform well on classification, pattern-matching, and structured output tasks. The Pro model's additional reasoning depth would be underutilised because the Reviewer does not generate code, perform multi-step analysis, or make architectural judgments. Using Flash also reduces token costs and latency, which matters for a review gate that should complete within seconds.

**Why temperature 0.0**: Deterministic reviews are a requirement, not a nice-to-have. The same diff must produce the same review every time. This is important for:
- **Auditability**: If a review needs to be re-examined, it must produce the same findings.
- **Fairness**: The Developer should receive consistent feedback regardless of when the review runs.
- **CI integration**: A non-deterministic review gate would produce flaky CI results — sometimes passing, sometimes failing the same diff.
- **Severity classification**: Severity boundaries must be stable. A minor issue that gets bumped to major on a second pass erodes trust in the review process.

A temperature of 0.0 achieves this determinism. The tradeoff is that the Reviewer will not produce creative or insightful observations that go beyond its pattern database. This is acceptable because creative review is the human reviewer's job; the automated reviewer is a deterministic first pass.

## Permissions Analysis

The permission model is designed to make the Reviewer a **read-only observer** with minimal attack surface.

| Resource | Setting | Rationale |
|---|---|---|
| `read` | `allow` | Must read the full diff, commit messages, and file contents |
| `edit` | `deny` | **CRITICAL** — Reviewer must never modify files. This is the cornerstone of audit isolation. |
| `glob` | `allow` | Must discover file structure for context |
| `grep` | `allow` | Must search for security patterns, convention violations, and credential patterns |
| `bash: *` | `deny` | Default deny on all commands — maximum restriction |
| `bash: git diff` | `allow` | Core function — inspect diffs between commits and branches |
| `bash: git log` | `allow` | Inspect commit history for ADR 0002 compliance checks |
| `bash: git show` | `allow` | Inspect specific commits by hash |
| `webfetch` | `deny` | No external context needed; reviews are repo-internal |
| `skill: *` | `deny` | Default deny on all skills |
| `skill: rs-*` | `allow` | Only RuneSmith skills (methodology, severity, security) |
| `skill: rs-review-security` | `allow` | Explicit security skill for credential/injection scanning |
| `task: *` | `deny` | Leaf agent enforcement — no delegation |

### The `edit: deny` Constraint

The most critical permission is `edit: deny`. This enforces the audit layer separation of concerns:

- The **Developer** has `edit: allow` — it writes and modifies files.
- The **Reviewer** has `edit: deny` — it reads and reports but never touches files.
- The **Architect** has `edit: allow` — it writes plans and configs but is prompted to never modify implementation files.

If the Reviewer could edit files, the entire pipeline's integrity would be compromised. The Reviewer would be auditing its own changes, creating a conflict of interest. The `edit: deny` constraint makes the audit layer tamper-proof by construction — the Reviewer literally cannot fix the issues it finds, which forces a clean handoff back to the Developer.

### Git-Only Bash Access

The Reviewer's bash access is restricted to three git commands:

| Command | Purpose | Risk if Abused |
|---|---|---|
| `git diff` | View changes between commits, branches, or the working tree | Minimal — read-only |
| `git log` | View commit history for ADR 0002 compliance | Minimal — read-only |
| `git show` | View a specific commit's diff and metadata | Minimal — read-only |

All three are effectively read-only. The Reviewer cannot `git commit`, `git push`, `git checkout`, `git reset`, or any write operation. This is by design — the Reviewer inspects history without modifying it.

## Comparison to Other Agent Reviewers

**opencode-swarm's reviewer**: This agent follows a similar leaf pattern with `edit: deny` and git-only bash access. The primary difference is in skill surface: swarm's reviewer loads a single `review-patterns` skill, while RuneSmith separates methodology, severity, and security into three distinct skills. The modular approach allows each skill to be updated independently — for example, adding a new credential pattern to `rs-review-security` without changing the review methodology.

**opencode-workspace's audit agent**: This agent has broader bash access including `npm test` and `pytest` execution, making it a combined reviewer-and-tester. RuneSmith separates review from test execution — the Reviewer checks test definitions but does not run them. This separation reflects the principle that reviewing test quality and running tests are different concerns that benefit from different agent configurations (Flash for review, Pro for test execution).

**GitHub CodeQL / SonarQube**: These are static analysis tools, not LLM-based reviewers. They excel at deterministic pattern matching but cannot evaluate semantic correctness, ADR compliance, or documentation quality. The Reviewer fills this gap by combining static pattern matching (via `rs-review-security`) with LLM-based semantic understanding. The two approaches are complementary — a production pipeline would run both CodeQL (for deep static analysis) and the Reviewer (for semantic and convention checks).

## Analysis

The Reviewer agent design prioritises **determinism, audit isolation, and speed** over creative insight.

### Determinism

The combination of Flash model + 0.0 temperature ensures that every review is reproducible. This is essential for a CI gate: if the same diff can produce different review outcomes, the pipeline becomes flaky and developers lose trust in automated review. The tradeoff is that the Reviewer will not catch novel vulnerability patterns that require creative reasoning — but that is the domain of human reviewers and periodic security audits.

### Audit Isolation

The `edit: deny` constraint combined with git-only bash access creates a tight audit sandbox. The Reviewer can observe but never touch. This is a stronger guarantee than a prompt-based constraint ("you must not modify files") because it is enforced at the agent file level — even if the model hallucinates and tries to write code, the runtime will reject the edit.

### Speed

Flash models produce structured output faster than Pro models. For a review gate that should complete in seconds (not minutes), Flash is the correct choice. The Reviewer's workload is bounded by diff size — a 500-line diff takes longer to review than a 50-line diff — but Flash should handle both within a few seconds.

### Limitations

1. **No historical context**: The Reviewer reviews each diff in isolation. It does not track whether the Developer has addressed previous review findings. This tracking is the Architect's responsibility.
2. **No test execution**: The Reviewer can inspect test definitions but cannot verify that tests pass. Passing tests are verified by CI.
3. **No cross-PR analysis**: The Reviewer cannot detect patterns across multiple PRs (e.g., a security vulnerability gradually introduced across several commits). This requires a different agent or manual audit.

## Recommendations

1. **Implement `rs-review-security` first** — the security scanning skill has the highest value and is the most differentiated from general LLM capabilities. Without it, the Reviewer is just a code-style checker.

2. **Add a regex-based credential scanner to `rs-review-security`** — credential patterns are well-suited to deterministic matching and should not rely on LLM pattern recognition alone. A hybrid approach (regex scan + LLM classification) is more reliable.

3. **Consider a `rs-review-conventions` skill** — separate from methodology, a lighter-weight skill that loads only the project's coding conventions (PEP 8, import ordering, naming conventions, docstring style). This could be project-specific and updated per repository.

4. **Implement review caching** — if a diff has already been reviewed (same SHA, same findings), the Reviewer could return a cached result instead of re-running. This is useful for repeated CI runs of the same commit.

5. **Monitor review latency in production** — the Reviewer should complete within 5 seconds for a 500-line diff. If latency exceeds this, consider reducing `max_thinking_tokens` or batching security scans.

6. **Add severity override capability** — while the Reviewer is deterministic, there may be cases where a human reviewer wants to override a severity classification (e.g., downgrading a critical to major). This should be supported via a manual override mechanism, not by changing the Reviewer's temperature.

## See Also

- Agent file reference: `knowledge/tooling/opencode/agents/agent-file-reference`
- Permissions model: `knowledge/tooling/opencode/agents/permissions`
- Orchestration patterns: `knowledge/tooling/opencode/agents/orchestration-patterns`
- ADR 0002 (development conventions) — review expectations in §5
- Developer agent design: `research/opencode-runesmith/agents/developer.md`
- Architect agent design: `research/opencode-runesmith/agents/architect.md`

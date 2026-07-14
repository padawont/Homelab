---
title: "Debugger Agent Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-14
tags:
  - opencode
  - agents
  - debugger
  - debugging
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
  - knowledge: "knowledge/tooling/opencode/agents/permissions.md"
  - knowledge: "knowledge/tooling/opencode/agents/orchestration-patterns.md"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
last_audit_date: 2026-06-14
---

# Debugger Agent Design (`rs-debugger`)

## Context

The Debugger agent is part of the `@runicengines/opencode-runesmith` plugin — an internal OpenCode plugin for the RunicEngines cooperative. Within the RuneSmith agent orchestration model, the Debugger is a **leaf agent** specialised for troubleshooting: it reproduces bugs, analyses logs and traces, runs reduced test cases, and reports findings. It does **not** implement fixes — that's the Developer's job.

The Debugger fills the investigative gap in the RuneSmith pipeline. When the Developer encounters a bug, they can delegate the investigation to the Debugger while continuing other work. The Debugger runs the investigative loop — reproduce, analyse, reduce, report — and hands off findings to the Developer for the actual fix.

## Architecture

### Agent Role

The Debugger agent is responsible for:

- **Bug reproduction**: Reading issue descriptions, running the application or test suite to reproduce the reported behaviour.
- **Log and trace analysis**: Reading application logs, stack traces, APM traces, and error reports to identify the root cause.
- **Test case reduction**: Creating minimal reproduction scripts that isolate the bug from its surrounding context.
- **Root cause identification**: Correlating reproduction steps with log output to pinpoint the failure point.
- **Finding handoff**: Producing a structured bug report with reproduction steps, root cause, and recommended fix direction for the Developer agent.

The Debugger does **not**:

- Implement fixes — that is the Developer's role. The Debugger produces findings; the Developer acts on them.
- Modify source files — the Debugger is read-only for production code. It can only create temporary reproduction scripts in scratch space.
- Deploy code, change configuration, or manage releases.
- Load KB skills — the `kb-*` skill prefix is reserved for the centralized Knowledge Base agent system.

### When to Use the Debugger

The Debugger is invoked when:

| Scenario | Trigger | Handoff |
|---|---|---|
| Developer encounters a bug during implementation | Developer detects unexpected behaviour | Debugger investigates, Developer continues other work |
| CI pipeline failure analysis | CI reports test failure | Debugger reproduces and analyses, DevOps or Developer fixes |
| Production incident triage | Monitoring alert with stack trace | Debugger analyses logs, reports findings |
| Flaky test investigation | Reviewer flags flaky test | Debugger reproduces to determine flakiness pattern |

### Agent File Definition

```yaml
---
description: >
  Troubleshoots bugs — reproduces, analyses logs/traces, runs reduced test
  cases, and reports findings. Read-only for source code; can create
  temporary reproduction scripts in scratch space.
mode: subagent
model: opencode-go/deepseek-v4-flash
temperature: 0.2
permission:
  read: allow              # Full read access for code, logs, traces
  edit: deny               # No source file modification
  glob: allow              # Discover log files, test files
  grep: allow              # Search for error patterns, stack frames
  bash:
    "*": ask               # Ask for arbitrary commands
    "git *": allow         # Git operations (checkout branches, log)
    "npm *": ask           # Test runners (need confirmation)
    "python *": ask        # Run reproduction scripts
    "go test *": ask       # Run Go tests
    "bun test *": ask      # Run Bun tests
    "mkdir -p /tmp/*": allow  # Create temp dir for reproduction scripts
  webfetch: allow          # Fetch issue details, external docs
  task:
    "*": deny              # Leaf agent — no delegation
  skill:
    "*": deny
    "rs-*": allow          # Only runesmith skills
    "kb-*": deny           # No KB skills (separate system)
---
You are the RuneSmith Debugger, a dedicated troubleshooting agent inside the @runicengines/opencode-runesmith plugin.

## Your Role
You reproduce bugs, analyse logs and traces, run reduced test cases, and report findings. You do NOT implement fixes — you hand off your findings to the Developer. You NEVER modify source code. You may create temporary reproduction scripts in `/tmp/` or the project's scratchpad directory.

## Core Workflow
1. Understand the bug — read the issue description, stack trace, or error report.
2. Reproduce — run the application, test suite, or a minimal reproduction script.
3. Analyse — examine logs, traces, and error output to isolate the root cause.
4. Reduce — create a minimal reproduction script that demonstrates the bug in isolation.
5. Report — produce a structured bug report with reproduction steps, root cause, and recommended fix direction.

## Debugging Techniques

### Reproduction
- Start with the exact reproduction steps from the issue.
- If no steps exist, infer the context from the stack trace or error message.
- Create a minimal reproduction script in the scratchpad directory — do NOT modify production code.
- If the bug is intermittent, run the reproduction multiple times (at least 5) to assess flakiness.

### Log Analysis
- Read application logs from the usual locations (stdout, stderr, log files in `logs/` or `var/log/`).
- Search for error patterns using `grep` — look for stack traces, panic messages, exception types.
- Correlate timestamps between log entries to understand the sequence of events.
- Flag suspicious patterns: unusual error counts, unexpected log levels, missing expected log entries.

### Trace Analysis
- Read distributed traces if available (OpenTelemetry, Jaeger, Zipkin formats).
- Identify the span that contains the error.
- Trace the request path from entry point to failure point.
- Note latency anomalies that may indicate the problem area.

### Root Cause Identification
- Formulate a hypothesis: "The bug is caused by X in component Y."
- Test the hypothesis by running the reproduction script with and without the suspected cause.
- If the hypothesis is wrong, narrow the search space using binary search on commits or code paths.
- Document ruled-out hypotheses to avoid re-investigation.

## What You MUST NOT Do
- Modify source code — read-only for all production files.
- Implement fixes — report findings for the Developer.
- Deploy code, change configuration, or run CI pipelines.
- Commit changes or create PRs.
- Load kb-* skills — those belong to the separate Knowledge Base system.

## Skills
- `rs-discover`: Codebase context — understand project structure before debugging.
- `rs-consult`: Domain expertise — research unfamiliar error patterns, libraries, or frameworks.
- `rs-scratchpad`: Session scratchpad — store reproduction scripts and findings.

```

## Output Format

Every debugging session produces a structured report:

```yaml
bug_report:
  issue: "#142"
  title: "OAuth2 token refresh fails with 401 on expired refresh token"
  severity: S2  # Per ADR 0007 severity classification

reproduction:
  steps:
    - "Authenticate with valid credentials"
    - "Wait 10 minutes (token expiry window)"
    - "Attempt token refresh"
    - "Observe 401 response instead of 200"
  success_rate: "100% (10/10 attempts)"
  environment: "Node.js 22, PostgreSQL 16, local dev"

root_cause:
  component: "src/middleware/auth.ts"
  function: "validateRefreshToken()"
  description: >
    The refresh token validation checks the token's `expires_at` field
    against `Date.now()` in milliseconds, but the database stores
    `expires_at` in seconds (Unix timestamp). The comparison always
    sees the token as expired.

analysis:
  logs:
    - file: "logs/app.log"
      line: 142
      content: "ERROR: Token validation failed: token expired"
      timestamp: "2026-06-14T10:30:00Z"
  relevant_code:
    file: "src/middleware/auth.ts"
    lines: "45-52"
    snippet: |
      function validateRefreshToken(token) {
        // Bug: Date.now() returns ms, expires_at is in seconds
        if (token.expires_at < Date.now()) {
          throw new Error('Token expired')
        }
      }

fix_direction:
  description: "Convert expires_at to milliseconds before comparison"
  severity: "S2 — moderate (users see error but auth is not compromised)"
  recommendation: "Change line 48 to `token.expires_at * 1000`"
```

## Key Configuration Decisions

| Field | Value | Rationale |
|---|---|---|
| `mode: subagent` | The Debugger is intended for programmatic invocation by the Developer or Architect, but can also be invoked via `@rs-debugger` in chat by users who need debugging assistance. |
| `model: opencode-go/deepseek-v4-flash` | Debugging requires analytical reasoning but not the deep planning capability of Pro. Flash is sufficient for log analysis, code inspection, and reproduction. |
| `temperature: 0.2` | Lower temperature than the Developer (0.3) because debugging output must be precise and deterministic. Slight variability is acceptable for reproduction script formatting but the analysis must be consistent. |
| `edit: deny` | Hard restriction — the Debugger never modifies source code. It can create temp reproduction scripts in `/tmp/` via `mkdir -p /tmp/*: allow`. |
| `bash: "*": ask` | Most commands require user confirmation. Git commands are auto-allowed for branch switching and log inspection. Test runners require confirmation to avoid unintended execution. |
| `task: "*": deny` | Leaf agent enforcement. The Debugger never delegates — it investigates, reports, and returns. |

## Comparison with Developer Agent

| Dimension | Developer | Debugger |
|---|---|---|
| **Primary role** | Implement features and fixes | Investigate bugs and report findings |
| **Edit permission** | `allow` | `deny` |
| **Bash model** | `"*": ask` with broad allows | `"*": ask` with narrower allows |
| **Temp file creation** | Not needed (edits in place) | `mkdir -p /tmp/*: allow` for reproduction scripts |
| **Model** | `deepseek-v4-pro` | `deepseek-v4-flash` |
| **Temperature** | 0.3 | 0.2 |
| **Output** | Code changes | Bug report (YAML-structured) |
| **Delegation** | None (leaf agent) | None (leaf agent) |
| **When invoked** | During implementation | When a bug needs investigation |

The Debugger is the investigative counterpart to the Developer's implementation role. The Developer writes code; the Debugger finds out why code breaks. They form a complementary pair: Debugger investigates, Developer fixes.

## Permission Analysis

| Permission | Setting | Rationale |
|---|---|---|
| `read` | `allow` | Must read source code, logs, traces, and error reports. |
| `edit` | `deny` | No source file modification. Only temporary repro scripts in scratch space. |
| `glob` | `allow` | Discover log files, test files, and configuration. |
| `grep` | `allow` | Search for error patterns, exception types, and stack frames in logs and code. |
| `bash: *` | `ask` | Catch-all — most commands need user confirmation. |
| `bash: git *` | `allow` | Git operations: checkout relevant branches, inspect history, bisect commits. |
| `bash: npm/python/go/bun test *` | `ask` | Test runners require user confirmation because they have side effects. |
| `bash: mkdir -p /tmp/*` | `allow` | Create temporary directories for reproduction scripts without asking. |
| `webfetch` | `allow` | Fetch issue details from GitHub, read external debugging references, search for known error solutions. |
| `task: *` | `deny` | Leaf agent — no delegation. |
| `skill: rs-*` | `allow` | Only RuneSmith skills are accessible. |

## Design Decisions Summary

| Decision | Choice | Why Not the Alternative |
|---|---|---|
| **Model** | Flash | Pro would waste reasoning tokens on investigative tasks that do not involve multi-step planning. |
| **Temperature** | 0.2 | Lower than Developer (0.3) for deterministic, precise analysis output. |
| **Edit** | Deny | The Debugger must never modify source code — that's the Developer's role. Temp scripts are the only exception for reproduction purposes. |
| **Temp script creation** | `mkdir -p /tmp/*` allowed | Reproduction scripts need a write target. `/tmp/` is isolated from the project source. |
| **Bash test commands** | Ask | Test execution has side effects (db writes, file system changes). User confirmation prevents accidental runs. |
| **Task permission** | Deny all | Leaf agent — must not delegate. Matches all other RuneSmith leaf agents. |

## Open Questions

1. **Should the Debugger have access to production monitoring APIs?** Currently `webfetch` covers API access. A dedicated monitoring API skill could provide structured access to Grafana, Datadog, or Sentry APIs without granting broad webfetch access. This is a future enhancement if debugging frequently requires production observability data.

2. **Should there be a `rs-bisect` skill for automated git bisect?** Git bisect is a powerful debugging tool that the Debugger currently handles manually via `git *` bash commands. A dedicated skill could automate the bisect workflow with structured output. This would be a follow-up enhancement.

3. **Should the Debugger support interactive debugging (pdb, ipdb, node inspect)?** Interactive debuggers require a persistent process and user interaction, which are difficult to manage in an agent context. The current approach (reproduction scripts + log analysis) avoids this complexity. If interactive debugging becomes necessary, a separate skill or agent mode would be needed.

## See Also

- [Developer agent](developer.md) — Implements fixes based on Debugger findings
- [Architect agent](architect.md) — Routes debugging tasks
- [Reviewer agent](reviewer.md) — Reviews fixes after implementation
- [Discover skill](../skills/utilities/rs-discover.md) — Codebase context for debugging
- [Consult skill](../skills/utilities/rs-consult.md) — Domain expertise for unfamiliar errors
- [Scratchpad skill](../skills/utilities/rs-scratchpad.md) — Temporary file storage for reproduction scripts
- [ADR 0007 — RuneSmith Plugin Architecture](../../../adr/0007-runesmith-plugin-architecture/overview.md) — Severity classification (S1–S5) and agent conventions
- [Agent file reference: knowledge/tooling/opencode/agents/agent-file-reference](../../../knowledge/tooling/opencode/agents/agent-file-reference.md)
- [Permissions model: knowledge/tooling/opencode/agents/permissions](../../../knowledge/tooling/opencode/agents/permissions.md)

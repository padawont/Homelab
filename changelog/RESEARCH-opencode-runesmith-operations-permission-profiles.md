---
title: "Agent Permission Profiles"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - agents
  - permissions
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/agents/permissions.md"
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
references:
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
last_audit_date: 2026-06-07
---

# Agent Permission Profiles

- **Plugin:** `@runicengines/opencode-runesmith`
- **All agents:** `mode: subagent`
- **Skill prefix:** `rs-`

This document defines the permission matrix for all eight agents in the Runesmith plugin. Every permission is designed around the **Principle of Least Privilege**: each agent receives the minimum access required to perform its role, and nothing more.

The architect is the only agent capable of delegation (`task: allow`). All leaf agents enforce `task: deny` — they cannot spawn sub-agents, keeping the delegation tree flat and auditable. Skill access is uniformly scoped to the `rs-*` prefix across all agents, ensuring only plugin-defined skills are reachable.

## Permission Matrix

| Tool | Architect | Spec-Writer | Developer | Reviewer | Test-Writer | Tech-Writer | DevOps | Debugger |
|---|---|---|---|---|---|---|---|---|---|
| read | allow | allow | allow | allow | allow | allow | allow | allow |
| edit | allow | allow | allow | **deny** | allow | allow | allow | **deny** |
| glob | allow | allow | allow | allow | allow | allow | allow | allow |
| grep | allow | allow | allow | allow | allow | allow | allow | allow |
| bash | *:deny, git *:allow, gh *:allow | *:deny, gh *:allow | *:ask, git *:allow, npm *:allow, pip *:allow, make *:allow, rm -rf *:deny | *:deny, git diff, git log, git show | *:deny, pytest *:allow, bun test *:allow, npm test *:allow, python -m pytest *:allow | **deny** | *:ask, gh *:allow, docker *:ask, kubectl *:deny, aws *:deny | *:ask, git *:allow, npm *:ask, python *:ask, go test *:ask, bun test *:ask, mkdir -p /tmp/*:allow |
| webfetch | allow | allow | deny | deny | deny | allow | allow | allow |
| task | 6 agents (explicit) | deny | deny | deny | deny | deny | deny | deny |
| skill | rs-* | rs-* | rs-* | rs-* | rs-* | rs-* | rs-* | rs-* |

> **Note:** Unlisted tools default to `deny`. Dash entries (`—`) in design discussions are rendered as `deny` — the absence of an explicit allow is a deny.

## Agent YAML Definitions

Each agent's full permission block is shown below with commentary on the key restrictions.

### 1. Architect

The **architect** is the orchestrator. It is the only agent with `task: allow`, giving it exclusive authority to delegate to any other agent.

```yaml
---
name: "rs-architect"
mode: subagent
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  bash:
    "*": deny
    "git *": allow
    "gh *": allow
  webfetch: allow
  task:
    "rs-spec-writer": allow
    "rs-developer": allow
    "rs-reviewer": allow
    "rs-test-writer": allow
    "rs-tech-writer": allow
    "rs-devops": allow
  skill:
    "rs-*": allow
---
```

**Analysis:** `bash` is restricted to `git*` and `gh*` — staging, committing, pushing, and GitHub queries — but no arbitrary shell execution. This prevents the architect from accidentally running destructive operations during multi-agent delegation rounds. `webfetch: allow` enables the architect to research architectural patterns before delegating specification work.

### 2. Spec-Writer

The **spec-writer** drafts specifications, research documents, and proposals. It reads existing knowledge, writes new documents, and references external material.

```yaml
---
name: "rs-spec-writer"
mode: subagent
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  bash:
    "*": deny
    "gh *": allow
  webfetch: allow
  task: deny
  skill:
    "rs-*": allow
---

**Analysis:** No `git*` commands — the spec-writer does not manage code or commits. `bash` is scoped to `"*": deny` with an explicit `"gh *": allow` for creating and updating GitHub issues and PRs during the specification workflow. `webfetch: allow` enables fetching external references, documentation, and standards documents during research. `task: deny` enforces the leaf-agent rule.

### 3. Developer

The **developer** writes and modifies code. It has broad command access but every invocation prompts for confirmation.

```yaml
---
name: "rs-developer"
mode: subagent
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  bash:
    "*": ask
    "git *": allow
    "npm *": allow
    "pip *": allow
    "make *": allow
    "rm -rf *": deny
  webfetch: deny
  task: deny
  skill:
    "rs-*": allow
---

**Analysis:** The bash model uses a layered allow/ask/deny matrix. `"*": ask` is the catch-all safety net — any unrecognized command prompts the user for confirmation. Common development commands (`git *`, `npm *`, `pip *`, `make *`) are auto-allowed because they form the core development loop and should not require confirmation for every invocation. `"rm -rf *"` is hard-denied to prevent catastrophic file destruction. This catches destructive operations like `git push --force` or `rm -rf` via the catch-all ask layer while keeping routine operations frictionless. `webfetch: deny` keeps the developer focused on local code; external research is the spec-writer's domain.

### 4. Reviewer

The **reviewer** inspects code changes without making them. This is the most locked-down agent in the profile set.

```yaml
---
name: "rs-reviewer"
mode: subagent
permission:
  read: allow
  edit: deny
  glob: allow
  grep: allow
  bash:
    "*": deny
    "git diff": allow
    "git log": allow
    "git show": allow
  webfetch: deny
  task: deny
  skill:
    "rs-*": allow
---
```

**Analysis:** `edit: deny` is the defining restriction — the reviewer can read every file and inspect git history, but cannot modify a single byte. This guarantees audit integrity: a reviewer cannot accidentally or deliberately alter the code under review. Bash is restricted to read-only git commands (`git diff`, `git log`, `git show`) — no `git add`, `git commit`, or `git push`. `webfetch: deny` eliminates external distraction.

### 5. Test-Writer

The **test-writer** creates and runs test suites. It needs read access to understand code, edit access to write tests, and bash access for test runners only.

```yaml
---
name: "rs-test-writer"
mode: subagent
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
  webfetch: deny
  task: deny
  skill:
    "rs-*": allow
---

**Analysis:** `bash` is scoped to test runners exclusively with a `"*": deny` catch-all — pytest, bun test, and npm test are explicitly allowed (including `python -m pytest *` for projects that invoke pytest via the Python module). The test-writer can read source to understand test targets, edit test files, glob for test patterns, and execute test commands, but cannot run arbitrary scripts, install packages, or modify non-test code. `webfetch: deny` prevents the test-writer from fetching external code during test execution.

### 6. Tech-Writer

The **tech-writer** produces documentation — READMEs, API references, user guides. It reads code, edits markdown, and references web documentation.

```yaml
---
name: "rs-tech-writer"
mode: subagent
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  bash: deny
  webfetch: allow
  task: deny
  skill:
    "rs-*": allow
---
```

**Analysis:** `bash: deny` is the defining restriction. Documentation work requires no shell access whatsoever — the tech-writer reads existing code to understand APIs, edits markdown files, and fetches web references to verify documentation accuracy. Removing `bash` entirely eliminates shell execution as an attack surface and removes the temptation to bypass documentation workflows with ad-hoc scripting.

### 7. DevOps

The **devops** agent manages infrastructure, deployments, and CI/CD. It has the most nuanced bash profile because it interacts with multiple external systems.

```yaml
---
name: "rs-devops"
mode: subagent
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  bash:
    "*": ask
    "gh *": allow
    "docker *": ask
    "kubectl *": deny
    "aws *": deny
  webfetch: allow
  task: deny
  skill:
    "rs-*": allow
---

**Analysis:** The bash profile uses layered controls with a `"*": ask` catch-all — any unrecognized command prompts the user for confirmation. `"gh *"` commands run freely — the devops agent needs unfettered access to create releases, manage GitHub Actions, and query CI status. `"docker *"` commands require user confirmation (`ask` mode) because container operations have broad system impact. `"kubectl *"` and `"aws *"` are explicitly denied — infrastructure changes must go through CI/CD pipelines where they are reviewed, logged, and reproducible. This prevents ad-hoc production changes from an agent session. `webfetch: allow` enables the devops agent to check deployment status pages and container registry APIs.

### 8. Debugger

The **debugger** troubleshoots bugs — reproduces, analyses logs/traces, runs reduced test cases, and reports findings. It is read-only for source code and can create temporary reproduction scripts in scratch space.

```yaml
---
name: "rs-debugger"
mode: subagent
permission:
  read: allow
  edit: deny
  glob: allow
  grep: allow
  bash:
    "*": ask
    "git *": allow
    "npm *": ask
    "python *": ask
    "go test *": ask
    "bun test *": ask
    "mkdir -p /tmp/*": allow
  webfetch: allow
  task: deny
  skill:
    "rs-*": allow
---
```

**Analysis:** `edit: deny` is the defining restriction — the debugger never modifies source code. It shares this restriction with the reviewer, but for a different reason: the reviewer must preserve audit integrity, while the debugger operates in investigation mode where modifications would change the state under analysis. `bash` uses `"*": ask` as a catch-all, with `git *` auto-allowed for branch switching and log inspection, and test runner commands (`npm *`, `python *`, `go test *`, `bun test *`) requiring confirmation. `mkdir -p /tmp/*` is auto-allowed to create isolated directories for temporary reproduction scripts — these scripts are the only files the debugger writes, and they live outside the project tree. `webfetch: allow` enables fetching issue details, external debugging references, and documentation during investigation.

## Security Principles

Five principles govern every permission decision in this matrix.

### 1. Principle of Least Privilege

Every agent receives exactly the permissions it needs and no more. The tech-writer, for example, has `bash: deny` because documentation never needs shell execution. The reviewer has `edit: deny` because code review is read-only by definition. No agent is granted sweeping permissions "just in case."

### 2. Edit Isolation

The reviewer and debugger both have `edit: deny`, though for different reasons. The reviewer must preserve audit integrity — a reviewer cannot alter the code under review. The debugger must preserve the state under investigation — modification would change the behaviour being analysed. This creates a clear boundary: any file modification during a review or debugging session must come from outside. The reviewer/debugger can flag issues and inspect code, but cannot introduce changes.

### 3. Bash Restriction by Role

Shell access is the highest-risk permission in the system. Each agent's bash rules are tightly scoped:

- **No shell at all:** Tech-writer (`bash: deny`)
- **Read-only git:** Reviewer (`git diff`, `git log`, `git show`)
- **Git + GitHub only:** Architect, Spec-Writer
- **Ask confirmation with test runners:** Debugger (git auto-allowed, test runners ask, temp dir auto-allowed)
- **Ask confirmation:** Developer (broad commands but every invocation confirmed)
- **Layered allow/ask/deny:** DevOps (gh freely, docker with ask, kubectl/aws denied)

This granularity means a compromised or misconfigured agent can only execute commands within its role's blast radius.

### 4. Leaf Agent Rule

Only the architect has `task: allow`. All seven remaining agents enforce `task: deny`. This keeps the delegation tree one level deep — the architect delegates to leaf agents, and leaf agents never spawn sub-agents. This has three benefits:

- **Auditability:** Every action can be traced to a single agent invocation.
- **Simplicity:** No recursive delegation chains to debug.
- **Confinement:** A compromised leaf agent cannot escalate by spawning a more privileged agent.

### 5. Skill Scoping

All agents share the same skill permission: `rs-*`. The `rs-` prefix is the Runesmith namespace. This ensures that plugin agents can only invoke skills shipped with or explicitly approved by the plugin. System-level skills or skills from other plugins are unreachable unless added to the allow list.

## Permission Inheritance and Defaults

OpenCode applies permissive defaults that the plugin restricts further — only the tools an agent needs are explicitly listed. This means the matrix above is intentionally sparse — only the tools an agent needs are listed. All other tools (write, search, browse, etc. if they exist in future OpenCode versions) inherit `deny` automatically.

The `mode: subagent` setting on every agent further constrains behavior. Subagents operate within the calling agent's permission context — they cannot escalate beyond what the parent session allows. Combined with `task: deny` on leaf agents, this creates a tight security boundary around every delegated operation.

## Summary

This permission profile set enforces a zero-trust model where every tool access is justified by role, scoped by pattern, and auditable by design. The architect is the single delegation hub, leaf agents are confined to their domains, and bash access ranges from read-only git commands (reviewer) to ask-mode with test runners (debugger) to full ask-mode (developer) to no shell at all (tech-writer). The result is a system where a misconfigured or compromised agent can cause only limited, role-contained damage.

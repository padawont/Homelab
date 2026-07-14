---
title: "Roles"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - agents
  - roles
sources:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
last_audit_date: 2026-06-07
---

# Roles

## Concept

Role-based agents are reusable subagent templates designed for domain-specific tasks. Each role encapsulates a distinct prompt, permission set, and tool access pattern that aligns with a particular function in the development workflow. Rather than configuring tool permissions and system prompts from scratch for each task, role-based agents provide pre-assembled profiles that can be invoked on demand.

A role-based agent is defined as a standalone Markdown file in `.opencode/agents/` or bundled within a plugin. The file name becomes the agent name. The YAML frontmatter declares the agent's metadata, permission boundaries, and model settings; the Markdown body provides the system prompt that governs the agent's behavior.

### Distribution

Role-based agents are distributed in two ways:

- **Standalone files** — Individual `.md` files placed in `.opencode/agents/` (project) or `~/.config/opencode/agents/` (global). Auto-discovered on startup.
- **Plugin bundles** — Multiple agent definitions included in a plugin package. A single plugin can register one or more agent files alongside custom tools, event handlers, and MCP servers.

## Recommended Roles

### Architect

Focus: architecture, design decisions, system-wide review.

| Aspect | Value |
|---|---|
| Tools | `read`, `glob`, `grep`, `webfetch` |
| Permission | All listed tools: `allow`; `edit`, `bash`, `task`: `deny` |
| Mode | `subagent` |
| Model | Default (inherits from invoker) or a large-context model |
| Temperature | 0.0 |
| Use cases | Codebase analysis, ADR drafting, technology selection, dependency graph review |

The Architect role is read-only by design. It analyzes the codebase, evaluates architectural patterns, and produces recommendations without modifying any files. It is typically invoked by a Tech-Lead or Developer primary agent during the planning phase.

```yaml
---
description: "System architecture analysis and design review"
mode: subagent
temperature: 0.0
permission:
  read: allow
  glob: allow
  grep: allow
  webfetch: allow
  edit: deny
  bash: deny
---
You are an Architect agent focused on system architecture, design decisions, and codebase analysis.
Your tools are read-only. Do not modify any files.
Analyze code structure, evaluate architectural patterns, and produce recommendations.
Use webfetch for external research on technologies or patterns.
```

### Tech-Lead

Focus: technical accuracy, code review, best practices.

| Aspect | Value |
|---|---|
| Tools | `read`, `glob`, `grep`, `webfetch`, `bash` |
| Permission | All listed tools: `allow`; `edit`, `task`: `deny` |
| Mode | `subagent` |
| Temperature | 0.1 |
| Use cases | Validate solutions, enforce standards, review PRs, approve architecture |

The Tech-Lead role has non-destructive `bash` access for running linters, tests, and build commands. It can inspect output but cannot modify source files directly.

```yaml
---
description: "Technical accuracy review and standards enforcement"
mode: subagent
temperature: 0.1
permission:
  read: allow
  glob: allow
  grep: allow
  webfetch: allow
  bash: allow
  edit: deny
---
You are a Tech-Lead agent responsible for technical accuracy, code review, and best practices.
Use bash for non-destructive commands: run linters, tests, and builds.
Do not edit or write files. Produce review reports and recommendations.
```

### Developer

Focus: implementation, feature work, refactoring.

| Aspect | Value |
|---|---|
| Tools | Full access |
| Permission | All tools: `allow` |
| Mode | `all` |
| Temperature | 0.2 |
| Steps | 25 (recommended for complex implementation tasks) |
| Use cases | Build features, fix bugs, write tests, refactor code |

The Developer role has unrestricted tool access. It can read, write, edit, run commands, and invoke subagents. When configured as a primary agent, it owns a session tab and can delegate subtasks to specialist subagents.

```yaml
---
description: "Feature implementation and code development"
mode: all
temperature: 0.2
steps: 25
permission:
  read: allow
  glob: allow
  grep: allow
  webfetch: allow
  bash: allow
  edit: allow
  task: allow
---
You are a Developer agent with full tool access for implementation work.
Write clean, maintainable code. Run tests to validate changes.
Delegate specialist tasks (testing, security review) to subagents via the task tool.
```

### Test-Specialist

Focus: testing strategy, test writing, coverage.

| Aspect | Value |
|---|---|
| Tools | `read`, `edit`, `write`, `bash` |
| Permission | `read`, `edit`, `glob`, `grep`, `bash`: `allow`; `webfetch`, `task`: `deny` |
| Mode | `subagent` |
| Temperature | 0.1 |
| Use cases | Write unit/integration tests, coverage analysis, test infrastructure |

The Test-Specialist has write access limited to test files and test configuration. It runs test suites via `bash` and reports coverage gaps.

```yaml
---
description: "Test writing and coverage analysis"
mode: subagent
temperature: 0.1
permission:
  read: allow
  glob: allow
  grep: allow
  bash: allow
  edit: allow
  webfetch: deny
  task: deny
---
You are a Test-Specialist agent focused on testing strategy and implementation.
Write unit tests, integration tests, and test infrastructure.
Run test suites and analyze coverage reports.
```

### Quality-Specialist

Focus: code quality, linting, style, consistency.

| Aspect | Value |
|---|---|
| Tools | `read`, `grep`, `glob`, `bash` |
| Permission | `read`, `grep`, `glob`, `bash`: `allow`; `edit`, `webfetch`, `task`: `deny` |
| Mode | `subagent` |
| Temperature | 0.0 |
| Use cases | Enforce code style, run linters, formatting checks |

The Quality-Specialist runs linting and formatting tools via `bash` but does not modify files directly. Its output is a report of violations and suggested fixes.

```yaml
---
description: "Code quality enforcement and linting"
mode: subagent
temperature: 0.0
permission:
  read: allow
  glob: allow
  grep: allow
  bash: allow
  edit: deny
  webfetch: deny
  task: deny
---
You are a Quality-Specialist agent focused on code quality, linting, and style consistency.
Run linters, formatters, and static analysis tools.
Report violations and suggest fixes. Do not modify files directly.
```

### Technical-Writer

Focus: documentation, README, API docs, changelogs.

| Aspect | Value |
|---|---|
| Tools | `read`, `edit`, `write`, `glob`, `grep` |
| Permission | `read`, `edit`, `glob`, `grep`: `allow`; `bash`, `webfetch`, `task`: `deny` |
| Mode | `subagent` |
| Temperature | 0.3 |
| Use cases | Write docs, update README, generate changelogs, document APIs |

The Technical-Writer focuses on prose and structured documentation. It has write access to documentation files and READMEs but cannot execute commands.

```yaml
---
description: "Documentation writing and maintenance"
mode: subagent
temperature: 0.3
permission:
  read: allow
  glob: allow
  grep: allow
  edit: allow
  bash: deny
  webfetch: deny
  task: deny
---
You are a Technical-Writer agent responsible for documentation.
Write clear, structured documentation for features, APIs, and workflows.
Update README files and generate changelogs. Do not modify source code.
```

### DevOps

Focus: CI/CD, infrastructure, deployment, Docker.

| Aspect | Value |
|---|---|
| Tools | `read`, `bash`, `webfetch` |
| Permission | `read`, `bash`, `webfetch`, `glob`, `grep`: `allow`; `edit`, `task`: `deny` |
| Mode | `subagent` |
| Temperature | 0.1 |
| Use cases | CI config, Dockerfiles, deployment scripts, infrastructure review |

The DevOps role operates on infrastructure-as-code files. It has `bash` access for running deployment commands and validating configurations.

```yaml
---
description: "Infrastructure and deployment configuration"
mode: subagent
temperature: 0.1
permission:
  read: allow
  glob: allow
  grep: allow
  bash: allow
  webfetch: allow
  edit: deny
  task: deny
---
You are a DevOps agent focused on CI/CD, infrastructure, and deployment.
Review Dockerfiles, CI configurations, and deployment scripts.
Use bash to validate configurations and run infrastructure commands.
```

### Security-Auditor

Focus: security review, vulnerability detection.

| Aspect | Value |
|---|---|
| Tools | `read`, `glob`, `grep`, `webfetch` |
| Permission | `read`, `glob`, `grep`, `webfetch`: `allow`; `edit`, `bash`, `task`: `deny` |
| Mode | `subagent` |
| Temperature | 0.0 |
| Use cases | Dependency audit, secrets scan, OWASP review, vulnerability assessment |

The Security-Auditor is strictly read-only. It scans for secrets, checks dependency vulnerabilities, and reviews code against OWASP guidelines.

```yaml
---
description: "Security review and vulnerability detection"
mode: subagent
temperature: 0.0
permission:
  read: allow
  glob: allow
  grep: allow
  webfetch: allow
  edit: deny
  bash: deny
  task: deny
---
You are a Security-Auditor agent focused on security review and vulnerability detection.
Scan for secrets, check dependencies for known vulnerabilities, and review code against OWASP guidelines.
Do not modify any files. Produce a security report.
```

### Code-Reviewer

Focus: pull request review, diff analysis.

| Aspect | Value |
|---|---|
| Tools | `read`, `glob`, `grep`, `bash` |
| Permission | `read`, `glob`, `grep`, `bash`: `allow`; `edit`, `webfetch`, `task`: `deny` |
| Mode | `subagent` |
| Temperature | 0.0 |
| Use cases | PR review, changelog validation, commit inspection, diff analysis |

The Code-Reviewer uses `bash` with git commands to inspect diffs, check commits, and validate changelogs.

```yaml
---
description: "Pull request review and diff analysis"
mode: subagent
temperature: 0.0
permission:
  read: allow
  glob: allow
  grep: allow
  bash: allow
  edit: deny
  webfetch: deny
  task: deny
---
You are a Code-Reviewer agent focused on pull request review and diff analysis.
Use git commands in bash to inspect diffs, review commits, and validate changelogs.
Provide structured review feedback. Do not modify any files.
```

> See [Configuration](configuration.md) for the full configuration options reference (description, mode, model, temperature, steps, permissions, etc.).
> See [Permissions](permissions.md) for the complete permission key reference and granular permission patterns.

## Integration with Plugin System

Role-based agents can be bundled into an npm plugin package and distributed alongside custom tools, event handlers, and MCP servers. The [`@opencode-ai/plugin`](https://www.npmjs.com/package/@opencode-ai/plugin) package provides TypeScript types for plugin authoring, and plugins can define agents by placing `.md` agent files in the plugin's agent directory or by registering agent configurations programmatically.

For detailed guidance on bundling agents within plugins, see [Bundling Components](../plugins/bundling-components.md).

## See Also

- [composition-patterns](composition-patterns.md)
- [configuration](configuration.md)
- [permissions](permissions.md)

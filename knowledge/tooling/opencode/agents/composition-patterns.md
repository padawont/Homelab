---
title: "Agent Composition Patterns"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - agents
  - patterns
  - composition
sources:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
last_audit_date: 2026-06-07
---

## Composition Patterns

### Primary + Specialist Subagents

A common workflow pattern pairs a primary agent (e.g., Developer or Build) with one or more specialist subagents:

1. **Developer** (primary) starts implementing a feature.
2. Developer invokes **Test-Specialist** to write tests for the new code.
3. Developer invokes **Code-Reviewer** to review the diff before committing.
4. Developer invokes **Security-Auditor** for a vulnerability scan on dependencies.

The primary orchestrates, the specialists execute domain-specific work. Each specialist operates with its own permission boundary, limiting blast radius in case of unexpected behavior.

### Review Pipeline

A Tech-Lead or Code-Reviewer can chain multiple review roles:

1. **Code-Reviewer** inspects the diff and commit history.
2. **Security-Auditor** scans for vulnerabilities and secrets.
3. **Quality-Specialist** runs linters and style checks.
4. **Architect** evaluates the structural impact of the changes.

Each review produces a report. The Tech-Lead aggregates findings and determines whether to approve or request changes.

## Best Practices

- **Granular permissions** — Grant each role the minimum tool access required. A Security-Auditor should never have write access. A Developer should not have unlimited `bash` without `ask` prompts for destructive commands.
- **Deterministic temperature** — Use 0.0 for analysis and review roles. Higher temperatures add variability that is undesirable when evaluating code correctness.
- **Role naming** — Use kebab-case agent file names that match the role (`code-reviewer.md`, `test-specialist.md`). This keeps agent identifiers consistent and discoverable.
- **Prompt specificity** — Each role's system prompt should clearly state its purpose, its tool limitations, and the expected output format. This prevents role drift where an agent exceeds its intended scope.
- **Plugin packaging** — When distributing a set of role-based agents as a plugin, include a `README.md` that documents each role, its tool permissions, and typical use cases. This helps users understand what they are granting access to.

## See Also

- [roles](roles.md)
- [interactions](interactions.md)

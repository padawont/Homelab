---
title: "OpenCode RuneSmith Plugin — Implementation Approaches"
status: exploring
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - agents
  - skills
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
  - knowledge: "knowledge/tooling/opencode/agents/orchestration-patterns.md"
  - knowledge: "knowledge/tooling/opencode/agents/overview.md"
  - knowledge: "knowledge/tooling/opencode/agents/permissions.md"
  - knowledge: "knowledge/tooling/opencode/ecosystem/plugins.md"
  - knowledge: "knowledge/tooling/opencode/mcp/concepts.md"
  - knowledge: "knowledge/tooling/opencode/mcp/tool-management.md"
  - knowledge: "knowledge/tooling/opencode/plugins/architecture.md"
  - knowledge: "knowledge/tooling/opencode/plugins/bundling-components.md"
  - knowledge: "knowledge/tooling/opencode/plugins/event-compaction.md"
  - knowledge: "knowledge/tooling/opencode/plugins/event-patterns.md"
  - knowledge: "knowledge/tooling/opencode/plugins/event-session.md"
  - knowledge: "knowledge/tooling/opencode/plugins/examples.md"
  - knowledge: "knowledge/tooling/opencode/plugins/init-hook-lifecycle.md"
  - knowledge: "knowledge/tooling/opencode/plugins/npm-packaging.md"
  - knowledge: "knowledge/tooling/opencode/plugins/overview.md"
  - knowledge: "knowledge/tooling/opencode/plugins/private-distribution.md"
  - knowledge: "knowledge/tooling/opencode/plugins/publishing-workflow.md"
  - knowledge: "knowledge/tooling/opencode/plugins/versioning.md"
  - knowledge: "knowledge/tooling/opencode/sdk/api-misc.md"
  - knowledge: "knowledge/tooling/opencode/sdk/types.md"
  - knowledge: "knowledge/tooling/opencode/skills/maintenance.md"
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
references:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
last_audit_date: 2026-06-09
---

# OpenCode RuneSmith Plugin — Implementation Approaches

## Context

The RunicEngines cooperative maintains multiple code repositories across its organization. Developers working on these repos need consistent access to AI-powered agents and skills — role-based subagents for development workflows, reusable skills for common tasks, and MCP servers for tool integration.

[GitHub issue #19](https://github.com/RunicEngines/knowledge-base/issues/19) and the [org-wide agent plugin idea](../../ideas/organisation/tools/org-wide-agent-plugin/) proposed creating a shared, cross-repo OpenCode plugin. This is distinct from the [section-specific KB agents](../../research/section-specific-agents/), which are scoped to the knowledge-base repo only. The RuneSmith plugin serves code repos, not the knowledge base itself.

This research evaluates the implementation approaches for this plugin — comparing distribution strategies, agent role design, skill architecture, MCP integration, and update propagation.

## Design Decisions

| Decision | Value |
|---|---|
| Plugin name | `@runicengines/opencode-runesmith` |
| Distribution | Private npm via GitHub Packages |
| Install | `"plugin": ["@runicengines/opencode-runesmith"]` in `opencode.json` |
| Skill prefix | `rs-` (e.g., `rs-issue-to-plan`, `rs-discover`) |
| Agent naming | `rs-{role}.md` (e.g., `rs-developer.md`, `rs-reviewer.md`) |
| Agent mode | All `mode: subagent` |
| Architect model | `opencode-go/deepseek-v4-pro` (reasoning-heavy) |
| Reasoning-heavy agents model | `opencode-go/deepseek-v4-pro` (Architect, Developer, Test-Writer, DevOps) |
| Lightweight agents model | `opencode-go/deepseek-v4-flash` (Spec-Writer, Reviewer, Tech-Writer) |
| KB relationship | Separate — no cross-delegation between RuneSmith and KB agents |
| Update mechanism | Version-stamping + CLI update command |
| Plugin language | TypeScript (Python SDK does not support plugin creation) |
| Agent/skill storage | Copied from bundled package into `.opencode/{agents,skills}/` via init hook |

## Agent Architecture

Hub-and-spoke model with the architect as the central orchestrator:

```
User → Architect → Spec-Writer → Developer → Reviewer → Test-Writer → Tech-Writer → DevOps
       │              │             │           │            │             │         │
       └──────────────┴─────────────┴───────────┴────────────┴─────────────┴─────────┴──→ Report
```

- **Architect** is the ONLY agent with `task` permission — delegates to specialists
- **All other agents are leaf agents** — they do not delegate further
- **Phase gates** enforce quality: Plan → Implement → Review → Test → Deploy
- **Error recovery** with retry limits and escalation paths

## Skill Architecture

Two categories of skills:

| Category | Examples | Purpose |
|---|---|---|
| **Workflow skills** | `rs-issue-to-plan`, `rs-pr-packager`, `rs-changelog-manager` | End-to-end development workflows |
| **Utility skills** | `rs-discover`, `rs-consult`, `rs-dependency-checker` | Shared capabilities used across agents |

Skills are loaded on-demand via `skill({ name: "rs-{name}" })`. Agent prompts hardcode which skills to load — no dynamic routing YAML needed.

## Permission Model

Least-privilege per agent:

| Agent | Notable Restrictions |
|---|---|
| Reviewer | `edit: deny` — cannot modify files |
| Tech-Writer | `bash: deny` — no shell access |
| Leaf agents | `task: deny` — cannot delegate |
| DevOps | `kubectl: deny`, `aws: deny` — must use CI/CD |
| Developer | `bash: ask` — catches destructive commands |

## Key Findings

1. **Distribution via npm + GitHub Packages** provides auto-install and versioning at the cost of auth setup and cache management. Recommended over alternatives (global directory, submodule, manual copy).

2. **Hub-and-spoke orchestration** with an architect delegating to leaf agents prevents delegation loops and provides clear error recovery. Modeled after opencode-swarm's proven architecture.

3. **Version-stamping** in the plugin init hook handles the update propagation problem — the stamp file tracks which version's files are installed and triggers re-copy on mismatch.

4. **Skills are hardcoded in agent prompts** rather than dynamically routed — simpler to implement and maintain for a small, known set of agents and skills.

5. **The KB is searchable but not delegatable** — agents search the KB via a custom skill but cannot invoke KB agents. This keeps the two systems independent.

## Recommendations

1. Implement the plugin as `@runicengines/opencode-runesmith` following the package structure in `architecture/package-structure.md`
2. Create agent `.md` files with the frontmatter and permissions defined in each `agents/*.md` research file
3. Create skill `SKILL.md` files following the designs in each `skills/*.md` research file
4. Implement the version-stamping init hook from `architecture/init-hook.md`
5. Ship MCP configuration snippets in the plugin README for manual setup in `opencode.json` (the plugin SDK does not currently support programmatic MCP registration)
6. Write a `bunx @runicengines/opencode-runesmith update` CLI for cache management
7. Test against the verification checklist in `operations/verification.md`
8. Audit npm dependencies and SBOM coverage per `architecture/security-supply-chain.md`
9. Follow the distribution decisions documented in `architecture/distribution-questions-resolved.md`
10. Execute the three-phase rollout defined in `operations/rollout-strategy.md`
11. Adopt the governance model described in `operations/maintenance-governance.md`
12. Instrument cost tracking and logging per `operations/cost-observability.md`

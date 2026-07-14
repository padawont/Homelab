---
title: "Resolved Open Questions: Decisions Captured"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - agents
  - decisions
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-permissions"
  - knowledge: "knowledge/tooling/opencode/skills/skill-configuration"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
last_audit_date: 2026-05-31
---

# Resolved Open Questions: Decisions Captured

This file captures every open question from the idea and subsequent discussions, along with each resolved decision.

### Q1: Permission Granularity

**Question:** Should all agents have the same full-access permissions, or should some be more restricted? (adr-agent needs bash for git, proposals-agent needs bash for quarto)

**Decision:** All agents get full-access permissions. Rationale: simplicity, agents are scoped by their prompts already, easy to restrict later.

### Q2: Shared Workflow Logic

**Question:** Should common patterns (frontmatter validation, template scaffolding) be extracted into a shared skill or kept duplicated per agent?

**Decision:** Extracted into shared skills with `kb-` prefix: `kb-scaffold-topic`, `kb-frontmatter-validate`, `kb-cross-link-check`, `kb-status-transition`.

### Q3: ADR Numbering

**Question:** How should the adr-agent determine the next sequential number?

**Decision:** The agent scans the `adr/` directory for the highest existing `NNNN-` prefix among folder names, increments by 1, and pads to 4 digits. The agent may also cross-reference with GitHub issues to avoid gaps. No counter file maintained.

### Q4: Agent Visibility

**Question:** Should section agents be visible in `@mention` autocomplete or hidden (task-only)?

**Decision:** Visible via `@mention`. Users can directly `@ideas-agent`, `@knowledge-agent`, etc. Primary agents can also invoke them via `task`.

### Q5: Agent Naming

**Question:** Should the .md filenames use `ideas-agent` (explicit) or just `ideas` (short)?

**Decision:** `ideas-agent` pattern — explicit and avoids confusion with section directory names.

### Q6: Model Selection

**Question:** Which models should each agent use?

**Decision:** From the idea's model selection table:

| Agent | Model |
|---|---|
| ideas-agent | `opencode-go/deepseek-v4-flash` (simple scaffolding) |
| knowledge-agent | `opencode-go/deepseek-v4-pro` (complex content) |
| research-agent | `opencode-go/deepseek-v4-pro` (complex analysis) |
| proposals-agent | `opencode-go/deepseek-v4-pro` (version management) |
| adr-agent | `opencode-go/deepseek-v4-pro` (architectural reasoning) |

If omitted, the agent inherits the primary agent's model.

### Q7: Error Handling

**Question:** How should agents report validation failures?

**Decision:** Fail-and-explain pattern. Agents report specific violations and stop, rather than silently continuing or auto-correcting. Examples: "Missing required field `sources`", "Cross-link `knowledge/foo/` does not exist", "Status transition `draft → final` is invalid".

### Q8: opencode.json Changes

**Question:** What `opencode.json` changes are needed?

**Decision:** None. Agent auto-discovery handles the architecture. Default task and skill permissions require no additional config changes.

### Q9: Skill Namespace

**Question:** How to avoid skill name collisions in the global flat namespace?

**Decision:** Use `kb-` prefix for all Knowledge Base skills: `kb-scaffold-topic`, `kb-frontmatter-validate`, `kb-cross-link-check`, `kb-status-transition`. Agents do not need a prefix since they are project-scoped.

### Q10: Agent Mode

**Question:** Should section agents use `mode: subagent` or `mode: all`?

**Decision:** `mode: subagent` — these are specialized helpers invoked via `@mention` or `task`, not primary agents.

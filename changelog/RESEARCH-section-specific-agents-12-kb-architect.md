---
title: "Architect Agent: Cross-Sectional Orchestration for ADR and Proposal Drafting"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - agents
  - architect
  - coordination
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-configuration"
  - knowledge: "knowledge/tooling/opencode/agents/agent-permissions"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
last_audit_date: 2026-05-31
---

# Architect Agent: Cross-Sectional Orchestration for ADR and Proposal Drafting

## 1. Role Definition

The architect agent handles heavy architectural document writing — ADRs, design proposals, trade-off analysis — that requires strong reasoning and cross-sectional synthesis. It supports the adr-agent and proposals-agent by handling the complex content creation while delegating scaffolding and format enforcement to those section agents.

## 2. Relationship to Section Agents

Unlike section agents that automate conventions for a single section, the architect coordinates across sections. When a user needs a new ADR with complex trade-off analysis:

- The architect drafts the heavy content (Context, Decision, Consequences, Considered Options)
- The architect delegates to adr-agent via task to handle: scaffolding the NNNN- folder, filling basic frontmatter, validating MADR format

The same pattern applies for proposals: the architect writes the plan, and the proposals-agent handles scaffolding and versioning.

## 3. Recommended Configuration

```yaml
---
description: Draft architectural decisions and design proposals with strong reasoning
mode: subagent
model: opencode-go/deepseek-v4-pro
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  list: allow
  bash: allow
  webfetch: allow
  task: allow
  skill: allow
---
```

## 4. Permission Rationale

- read/edit/glob/grep: standard file access for drafting documents
- bash: needed for git operations (ADR numbering) and quarto render (proposals)
- webfetch: research external patterns and references for architectural decisions
- task: invoke adr-agent and proposals-agent for scaffolding delegation
- skill: load kb-* skills if needed

## 5. When to Use

Use the architect when the task involves complex trade-offs, cross-sectional analysis, or requires strong reasoning. Do NOT use for simple scaffolding tasks (use the section agent directly).

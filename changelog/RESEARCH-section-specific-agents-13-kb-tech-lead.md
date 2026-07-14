---
title: "Tech-Lead Agent: External Accuracy Validation for Knowledge and Research"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - agents
  - tech-lead
  - validation
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-permissions"
  - knowledge: "knowledge/tooling/opencode/agents/agent-configuration"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
last_audit_date: 2026-05-31
---

# Tech-Lead Agent: External Accuracy Validation for Knowledge and Research

## 1. Role Definition

The tech-lead agent validates the accuracy of knowledge and research notes against external sources. It uses websearch to find official documentation and best practices, then uses webfetch to retrieve authoritative content and compare it against the claims made in notes. It supports the knowledge-agent and research-agent by providing an external fact-checking pass.

## 2. Relationship to Section Agents

The tech-lead acts as a validation overlay. After the knowledge-agent or research-agent has created or updated a note, the tech-lead reviews it for accuracy by:

- Searching for official documentation matching the note's claims
- Fetching authoritative sources
- Comparing claims (version numbers, API signatures, behavior descriptions, deprecation status)
- Reporting discrepancies

The tech-lead does NOT create or edit content — it validates and reports.

## 3. Recommended Configuration

```yaml
---
description: Validate knowledge and research notes against external authoritative sources
mode: subagent
model: opencode-go/deepseek-v4-pro
permission:
  read: allow
  glob: allow
  grep: allow
  list: allow
  bash: allow
  webfetch: allow
  websearch: allow
  skill: allow
  edit: deny
  task: deny
---
```

## 4. Permission Rationale

- **read/glob/grep/list**: read and search notes to identify claims needing verification
- **webfetch**: fetch official documentation, spec pages, authoritative sources
- **websearch**: search for official docs, best practices, changelogs
- **bash**: run git/grep for cross-referencing
- **skill**: load kb-cross-link-check if needed for cross-reference path verification
- **edit**: DENIED — tech-lead validates, does not edit
- **task**: DENIED — tech-lead is invoked by others, does not delegate

## 5. When to Use

Use the tech-lead after a knowledge or research note is drafted, to verify technical accuracy. NOT used for internal consistency checks (that's the editor's role) or for content creation.

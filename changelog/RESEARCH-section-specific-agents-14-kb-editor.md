---
title: "Editor Agent: Cross-Cutting Proofreading and Internal Quality Assurance"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - agents
  - editor
  - proofreading
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

# Editor Agent: Cross-Cutting Proofreading and Internal Quality Assurance

## 1. Role Definition

The editor agent proofreads content across all sections (ideas, knowledge, research, proposals, adr). It reuses the existing shared skills — kb-frontmatter-validate, kb-cross-link-check, kb-status-transition — to check frontmatter correctness, link validity, and status consistency. It also provides the human-like proofreading step: checking that content is coherent, sources make sense, and formatting is consistent.

## 2. Relationship to Section Agents

The editor is a cross-cutting final review pass. Section agents create and validate content during the scaffold workflow. The editor reviews content that already exists — whether created by a human or a section agent. It provides a second set of eyes without the overhead of full workflow automation.

The editor does NOT scaffold, create content, or fix issues automatically. It reports problems using the fail-and-explain pattern (from 06-scaffolding-validation.md): flag specific violations, report them clearly, let the user or section agent decide how to fix.

## 3. Recommended Configuration

```yaml
---
description: Proofread notes, validate frontmatter, check cross-links across all sections
mode: subagent
model: opencode-go/deepseek-v4-flash
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  list: allow
  skill: allow
  bash: deny
  webfetch: deny
  websearch: deny
  task: deny
---
```

## 4. Permission Rationale

- read/edit/glob/grep/list: standard file inspection and minor fixes
- skill: load kb-frontmatter-validate, kb-cross-link-check, kb-status-transition
- bash: DENIED — editor works with file contents, not shell commands
- webfetch: DENIED — no external reference checking (that's tech-lead)
- websearch: DENIED — no web searching needed
- task: DENIED — editor is invoked by others, does not delegate

## 5. Skills Used

The editor reuses three of the four shared skills:

- kb-frontmatter-validate — check required fields, types, valid statuses, kebab-case tags, ISO dates, template comments
- kb-cross-link-check — verify referenced paths exist on disk
- kb-status-transition — validate lifecycle moves per section rules

It does NOT use kb-scaffold-topic (it does not create content).

## 6. What "Proofread" Means

For each file, the editor checks:

- Frontmatter: required fields present, types correct, status valid, tags kebab-case, dates ISO, no template comments
- Cross-links: all referenced paths exist, URLs well-formed
- Status transitions: current status is valid for the section's lifecycle
- Content: sources listed actually make sense in context, formatting is consistent, no obvious errors

## 7. When to Use

Use the editor as a final quality pass after content has been created or updated, on any section. Use for both human-written and agent-assisted content. The lightweight model (flash) keeps costs low for this recurring proofreading task.

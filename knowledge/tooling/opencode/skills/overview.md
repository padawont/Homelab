---
title: "OpenCode Skills"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - skills
sources:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# OpenCode Skills

Reference documentation for the OpenCode skill system: reusable instruction bundles loaded on-demand by agents.

## Concepts & Foundations

- [concepts.md](concepts.md) — What skills are, how they differ from agents
- [file-format.md](file-format.md) — SKILL.md structure, required/optional frontmatter, naming rules
- [tool-mechanism.md](tool-mechanism.md) — How the `skill` tool works, `<available_skills>` XML blocks, description-based discovery, permission filtering
- [configuration.md](configuration.md) — Full SKILL.md frontmatter specification, name validation, discovery paths, permission configuration, troubleshooting

## Case Studies

- [gh-case-study.md](gh-case-study.md) — Walkthrough of the existing `gh` skill in this repo, frontmatter analysis, structure, and design patterns

## Workflow Patterns

- [workflow-patterns.md](workflow-patterns.md) — Cross-cutting conventions: naming, permissions, triggers, agent-skill interaction flow, webhook bridge, chained invocation
- [issue-to-plan.md](issue-to-plan.md) — Decompose GitHub issues into structured implementation plans
- [pr-packager.md](pr-packager.md) — Package PR descriptions from local commits grouped by topic
- [test-helper.md](test-helper.md) — Run tests, parse failures, and suggest targeted fixes
- [changelog-manager.md](changelog-manager.md) — Generate and maintain changelogs per Keep a Changelog
- [code-reviewer.md](code-reviewer.md) — Review PRs against team conventions with structured comments
- [dependency-checker.md](dependency-checker.md) — Check dependencies for outdated or vulnerable packages

## Discovery Patterns

- [discovery-patterns.md](discovery-patterns.md) — Cross-pattern usage notes, combining strategies, shared tool dependencies
- [full-text-search.md](full-text-search.md) — Search all KB content by term with section filtering and ranking
- [cross-reference.md](cross-reference.md) — Follow frontmatter cross-links to build relationship graphs
- [pipeline-trace.md](pipeline-trace.md) — Trace topics through Idea → Knowledge → Research → Proposal → ADR
- [status-query.md](status-query.md) — Query content by status field across any section
- [recent-content.md](recent-content.md) — Find recently created or modified content using git log

## Registry & Catalogue

- [convention-registration.md](convention-registration.md) — Filesystem-based registration, discovery paths, name uniqueness
- [metadata-taxonomy.md](metadata-taxonomy.md) — Metadata fields, recommended taxonomy, discovery usage patterns
- [maintenance.md](maintenance.md) — Naming conventions, skill lifecycle, registry audit

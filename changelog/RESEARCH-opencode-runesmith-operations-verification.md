---
title: "Verification Checklist"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - testing
  - verification
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/plugins/overview"
references:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Verification: Smoke Test Checklist

This document defines the manual smoke test checklist for validating that the `@runicengines/opencode-runesmith` plugin installs, initialises, and operates correctly. Each section corresponds to a functional area of the plugin. All items must pass before a release is considered stable.

## 1. Plugin Installation

Verifies that the plugin resolves, installs, and loads without errors.

- [ ] Add `"plugin": ["@runicengines/opencode-runesmith"]` to `opencode.json`
- [ ] Verify `.npmrc` has `@runicengines:registry=https://npm.pkg.github.com/`
- [ ] Verify `GITHUB_TOKEN` is set with `read:packages` scope
- [ ] Restart OpenCode
- [ ] Verify no installation errors appear in the OpenCode output
- [ ] Check `~/.cache/opencode/node_modules/@runicengines/opencode-runesmith` exists

Run this against a clean project (no prior plugin cache) and again against an existing project to catch caching edge cases.

## 2. Init Hook

The init hook is responsible for copying agent and skill files from the plugin package into the project's `.opencode/` directory. This section validates the version-stamping strategy described in [update-propagation.md](./update-propagation.md).

- [ ] Verify `.opencode/agents/` has all agent `.md` files
- [ ] Verify `.opencode/skills/` has all skill directories with `SKILL.md`
- [ ] Verify `.opencode/.runesmith-version` contains the correct version string
- [ ] Verify re-starting OpenCode does **not** re-copy files when version stamp matches
- [ ] Test update: change version stamp to an old version → restart → verify files are re-copied and stamp is updated

The re-copy test is the most critical. It confirms that the version comparison logic works and that users receive updated agent and skill definitions when the plugin upgrades.

## 3. Agent @mention

Each agent shipped by the plugin must be invocable via `@mention` and must respect its assigned role and permissions.

- [ ] Each agent is invocable via `@rs-architect`, `@rs-developer`, `@rs-reviewer`, `@rs-spec-writer`, `@rs-test-writer`, `@rs-tech-writer`, `@rs-devops`
- [ ] Each agent loads its prompt correctly (no template errors, missing variables, or broken references)
- [ ] Each agent's permissions are enforced (e.g., reviewer cannot execute edit operations)
- [ ] Architect can `task()` to delegate work to other agents
- [ ] Leaf agents (reviewer, tech-writer) cannot `task()` — permission denied

Test every agent in the set, not a representative sample. Permission enforcement varies per agent and a single misconfigured permission can leak capabilities.

## 4. Skills

Skills are reusable tool definitions that agents invoke. This section validates that each skill loads, injects instructions, and chains to dependent skills correctly.

- [ ] Each skill is loadable via `skill({ name: "rs-{name}" })`
- [ ] Skill instructions are injected into the conversation context
- [ ] Skills chain correctly (e.g., `rs-test-helper-run` → `rs-test-helper-diagnose`)

Chaining is the most error-prone part of skill configuration. If skill A references skill B but B is not discovered, the chain breaks silently. Verify each chain end-to-end.

## 5. KB Discovery

The plugin depends on the knowledge-base repository for research sources, cross-references, and pipeline tracing.

- [ ] `rs-kb-search` finds the knowledge-base repo
- [ ] Full-text search returns results for known terms
- [ ] Cross-reference lookups resolve to existing files
- [ ] Pipeline tracing (idea → knowledge → research → proposal → ADR) works end-to-end

Run KB discovery tests against the actual knowledge-base repository used by the target project. A mismatch in repo URL or branch name is a common failure mode.

## 6. Permissions

Each agent type has a distinct permission profile. This section verifies that denied operations are rejected and approved operations succeed.

- [ ] Reviewer: `edit` operations fail with permission denied
- [ ] Tech-writer: `bash` operations fail with permission denied
- [ ] Developer: `rm -rf` is denied, `git commit` is allowed
- [ ] DevOps: `kubectl` is denied, `docker build` prompts for approval

Permission tests should be run with a real user session. Mocking the permission layer can mask bugs in the evaluation logic.

## 7. Update Propagation

Validates the CLI update command and the end-to-end flow of version-stamping as described in [update-propagation.md](./update-propagation.md).

- [ ] `bunx @runicengines/opencode-runesmith update` clears the npm cache entry for the plugin
- [ ] On next OpenCode start, init hook detects new version
- [ ] Agent and skill files are re-copied into `.opencode/`
- [ ] Version stamp in `.opencode/.runesmith-version` is updated to match

Test both a clean upgrade (1.0.0 → 2.0.0) and a rollback (2.0.0 → 1.0.0) to confirm the init hook handles both directions. Rollback is frequently overlooked in smoke tests but is essential for incident recovery.

---

**Pass threshold:** All checkboxes must be checked before a release is promoted from `draft` to `exploring`. Failed items must be resolved or explicitly waived with a documented reason in the release notes.

---
title: "Technical Writer Agent Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - agents
  - tech-writer
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
  - knowledge: "knowledge/tooling/opencode/agents/permissions.md"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://keepachangelog.com/en/2.0.0/"
    title: "Keep a Changelog 2.0.0"
last_audit_date: 2026-06-07
---

# Technical Writer Agent Design

> **Status:** Draft — initial analysis for the `@runicengines/opencode-runesmith` plugin tech-writer agent.
> **Audience:** Python developers building the plugin.

## 1. Agent Role

The tech-writer agent is a **leaf documentation specialist** in the RuneSmith multi-agent system. It writes and updates all documentation files: READMEs, API references, changelogs, contributing guides, and architecture docs. It is invoked by the Architect agent during the documentation phase of a workflow — typically after implementation and review are complete, but it can also be called standalone for documentation-only tasks.

The tech-writer does **not** write code, run builds, execute tests, or change configuration. It is a pure content generation agent — it reads source files, understands what they do, and produces human-readable documentation that accurately reflects the implementation. This narrow scope lets it use a lighter model and tighter permissions than agents that handle code.

Because the tech-writer is a leaf agent, it never delegates work. Every `task` target is denied. It operates with only the tools it needs: read/glob/grep for codebase exploration, edit for writing doc files, webfetch for researching external API behaviour, and `rs-*` skills for changelog management.

## 2. Recommended Agent File

```yaml
---
description: "Writes and updates documentation: READMEs, API docs, changelogs, and contributing guides"
mode: subagent
model: opencode-go/deepseek-v4-flash
temperature: 0.3
permission:
  read: allow
  edit: allow               # Only documentation files — enforced via prompt
  glob: allow
  grep: allow
  bash:
    "*": deny               # No shell access at all
  webfetch: allow            # May need to research API behaviour
  skill:
    "*": deny
    "rs-*": allow
  task:
    "*": deny               # Leaf agent — no delegation
---
You are the RuneSmith Technical Writer, a documentation specialist inside the @runicengines/opencode-runesmith plugin.

## Your Role
You write and maintain all project documentation: README files, API references, changelogs, contributing guides, and architecture documents. You do NOT write code, run tests, change configuration, or execute build commands.

## Core Workflow
1. Read the source code, API surface, or specification you need to document.
2. Understand the behaviour — load rs-consult if you need external reference material.
3. Write or update the documentation in the appropriate file.
4. Format consistently with existing project documentation conventions.
5. Report what was written, what changed, and any ambiguities you encountered.

## Documentation Types

### README
Project-level READMEs following the standard pattern: title, description, installation, usage, API overview, contributing link, license. Keep them concise — a developer should know what the project does within 10 seconds of opening the file.

### API Reference
Comprehensive endpoint/function/method documentation. Include signatures, parameter descriptions, return types, error codes, and at least one example per entry. Match the style of existing API docs in the project.

### Changelog (keepachangelog.com 1.1.0)
Use the `rs-changelog-manager` skill to generate changelog entries from commit history. Follow the Keep a Changelog 2.0.0 format: Unreleased section at the top, then versioned releases in reverse chronological order. Categorise entries under Added, Changed, Deprecated, Removed, Fixed, or Security.

### Contributing Guide
PR workflow, commit message format (Conventional Commits), development setup, test instructions, and code review expectations. Reference existing ADRs for specific conventions.

### Architecture Docs
High-level system descriptions: component diagrams (ASCII or Mermaid), data flow, module boundaries, and key design decisions. Link to ADRs for detailed rationale.

## What You MUST NOT Do
- Write implementation code or tests
- Install packages, run builds, or execute scripts
- Change configuration files (CI, lint, build tooling)
- Commit without review — always report changes for the Architect to commit
- Load kb-* skills — those belong to the separate Knowledge Base system

## Skills
- `rs-changelog-manager`: Generate and update changelogs from git history
- `rs-consult`: Query knowledge base and external documentation for API behaviour
- `rs-discover`: Understand project structure before writing (loaded automatically by the Architect before invoking you)
```

### Key Configuration Decisions

| Field | Value | Rationale |
|---|---|---|
| `mode: subagent` | Prevents `@mention` access. The tech-writer is invoked programmatically by the Architect, not directly by users. |
| `model: opencode-go/deepseek-v4-flash` | Documentation is natural language generation, not deep reasoning. Flash models produce high-quality prose at lower cost and latency than Pro models. |
| `temperature: 0.3` | Some variety in phrasing produces more engaging prose. A temperature of 0 would produce dry, repetitive output across invocations; 0.3 introduces enough variation to keep documentation readable without risking factual inconsistency. |
| `bash: "*": deny` | The tech-writer should never execute commands. No `git log` (the changelog skill handles this), no build commands, no scripts. Pure content generation only. |
| `webfetch: allow` | May need to research external API behaviours (e.g., fetching an API spec, reading a library's documentation) to write accurate documentation. |
| `edit: allow` | Must write documentation files. The prompt enforces that edits are restricted to doc files (`.md`, `.qmd`, etc.) — the agent is instructed not to modify source code or configuration. |
| `task: "*": deny` | Leaf agent enforcement. The tech-writer never delegates — it receives work, produces output, and returns. |

## 3. Prompt Structure

The tech-writer's system prompt follows a four-part structure, similar to the other RuneSmith agents:

### 3.1 Role Definition

Opens with a crisp role statement: *"You are the RuneSmith Technical Writer, a documentation specialist."* This primes the model as a writer rather than a developer — important because the same model (Flash) could otherwise drift into implementation suggestions when faced with code.

### 3.2 Core Workflow

A five-step sequential workflow: Read → Understand → Write → Format → Report. This mirrors how a human technical writer operates — understand the code before documenting it, maintain consistency, and report findings back. The `rs-consult` skill hook in step 2 is the safety net for unfamiliar APIs.

### 3.3 Documentation Types

Five documentation types with format-specific instructions:

| Type | Format Standard | Key Instruction |
|---|---|---|
| README | Standard project README pattern | 10-second comprehension test |
| API Reference | Signature + params + return + errors + examples | Match project style |
| Changelog | Keep a Changelog 2.0.0 | Use `rs-changelog-manager` |
| Contributing Guide | Reference ADRs for conventions | PR workflow, commit format |
| Architecture Docs | ASCII/Mermaid diagrams | Link to ADRs |

Each type has a specific standard to follow, reducing ambiguity about what "good documentation" looks like. The changelog type is particularly important because it's the only one that requires a skill (`rs-changelog-manager`) rather than raw generation.

### 3.4 Constraints (Negative Prompting)

The "What You MUST NOT Do" section is critical. Without explicit negative constraints, a capable language model will volunteer to fix code typos, add missing imports, or suggest implementation changes when it encounters incomplete code in a docstring example. The five explicit prohibitions — no code, no builds, no config, no commits, no kb-skills — create a hard boundary around the agent's scope.

## 4. Skills

The tech-writer uses three skills, all under the `rs-` prefix:

| Skill | When | Purpose |
|---|---|---|
| `rs-changelog-manager` | Every changelog update | Generate structured changelog entries from `git log` output. Handles the Keep a Changelog 2.0.0 format, categorisation, and version tracking. |
| `rs-consult` | When documenting unfamiliar APIs | Query internal knowledge notes and external documentation to understand how an API works before writing its reference. |
| `rs-discover` | On first invocation for a project | Explore project structure, existing documentation patterns, and ADRs to match the project's documentation conventions. Typically loaded by the Architect and passed as context, but the tech-writer can reload it if needed. |

All other skills are denied by the permission block (`"*": deny`, `"rs-*": allow`). This prevents accidental loading of `kb-*` skills from the separate Knowledge Base system or unrelated ecosystem skills that could inject instructions outside the tech-writer's scope.

## 5. Model Selection Rationale

**Why Flash over Pro:** Documentation generation is a natural language task, not a reasoning task. Writing a README or an API reference requires the model to understand what code does and express it clearly — skills that Flash models handle well. Pro models excel at multi-step reasoning, constraint satisfaction, and plan validation, which are not needed here. Using Flash reduces cost, latency, and thinking-token waste.

**Why temperature 0.3:** Documentation benefits from varied phrasing. A temperature of 0 produces identical sentences for identical code across runs, leading to stale-sounding prose that reads as if a template filled in the blanks. At 0.3, the model varies sentence structure and word choice while remaining factually consistent — the output is recognisably human-written rather than machine-gunned. This is the same temperature used by the Developer agent, though for different reasons: the Developer needs controlled variability in code structure, while the tech-writer needs natural phrasing in prose.

**No `max_thinking_tokens`:** Flash models do not have a separate thinking token budget — they generate directly without an intermediate reasoning step. This is appropriate for documentation, where the model should produce output immediately rather than think before writing.

## 6. Permission Analysis

| Permission | Setting | Rationale |
|---|---|---|
| `read` | `allow` | Must read source code, existing docs, and specs to understand what to document. |
| `edit` | `allow` | Must write and update `.md` files. The prompt restricts edits to documentation files only. |
| `glob` | `allow` | Needs to discover documentation files and project structure. |
| `grep` | `allow` | Needs to search for patterns, function signatures, and existing doc references. |
| `bash: *` | `deny` | No shell access at all. The tech-writer should never execute commands — not even `git log`, because the `rs-changelog-manager` skill handles git history retrieval internally. |
| `webfetch` | `allow` | May need to research external API documentation or library references to write accurate docs. For example, fetching an OpenAPI spec or reading a third-party library's documentation. |
| `skill: *` | `deny` | Catch-all deny for non-RuneSmith skills. |
| `skill: rs-*` | `allow` | Only RuneSmith skills are accessible. |
| `task: *` | `deny` | Leaf agent — no delegation. The tech-writer receives documentation tasks and completes them directly. |

The most distinctive permission choice is **`bash: "*": deny`** with no exceptions. Unlike the Developer agent (which allows `git`, `npm`, `pip`, and `make` commands) or the Architect agent (which allows `git` and `gh`), the tech-writer has zero shell access. This is because:

1. The tech-writer should never need to run `git log` — the `rs-changelog-manager` skill abstracts this.
2. Documentation does not require build commands, package management, or file operations.
3. Shell access would create temptation — or even model drift — toward executing code to "verify" behaviour before documenting it, which crosses into the Developer's territory.

The `edit: allow` permission is intentionally broad (not scoped to `*.md` files only) because OpenCode's permission model does not support file-extension scoping on the `edit` permission. Instead, the restriction is enforced via the system prompt's explicit prohibition: "Do NOT modify source code, tests, or configuration files." This is a prompt-level guard, not a structural one — a recognised trade-off documented in the open questions section below.

## 7. Comparison with opencode-workspace's Scribe

The `opencode-workspace` plugin includes a "scribe" agent that fulfills a similar documentation role. Comparing the two validates our design choices:

| Dimension | opencode-workspace Scribe | RuneSmith Tech-Writer | Rationale |
|---|---|---|---|
| **Model** | `gpt-5.1-codex` | `opencode-go/deepseek-v4-flash` | Different model preference. Both are Flash-class for lightweight generation. |
| **Temperature** | 0.2 | 0.3 | RuneSmith favours slightly more varied prose for engaging documentation. |
| **Bash access** | `deny` (no exceptions) | `deny` (no exceptions) | Identical — neither agent should execute commands. |
| **Webfetch** | `deny` | `allow` | RuneSmith tech-writer can research external API docs. This is the primary divergence. |
| **Edit scoping** | Prompt-enforced (doc files only) | Prompt-enforced (doc files only) | Identical approach — both rely on prompt constraints since the permission model cannot scope edits by file extension. |
| **Skills** | Plugin-specific skill set | `rs-changelog-manager`, `rs-consult`, `rs-discover` | RuneSmith has dedicated skills for changelog generation and knowledge consultation. |
| **Changelog format** | Unspecified | Keep a Changelog 2.0.0 | RuneSmith explicitly standardises on a changelog format. |
| **Delegation** | Leaf agent (`task: deny`) | Leaf agent (`task: deny`) | Identical — neither agent delegates. |

### Key Divergence: Webfetch Access

The most meaningful difference is `webfetch: allow`. The scribe operates entirely from local context — it documents what it can see in the codebase. The RuneSmith tech-writer can fetch external resources to understand APIs, library behaviours, and documentation standards before writing. This is particularly useful for:

- **API documentation**: Fetching an OpenAPI spec or reading a service's response format directly.
- **Library reference**: Reading a third-party library's docs to accurately describe its behaviour.
- **Format standards**: Fetching the latest Keep a Changelog spec or contributing guide template.

The trade-off is that webfetch introduces latency and potential for stale or incorrect external information. The tech-writer's prompt should instruct it to prefer local code analysis over external fetching when the information exists in the project itself.

## 8. Design Decisions Summary

| Decision | Choice | Why Not the Alternative |
|---|---|---|
| **Model** | Flash | Pro would waste reasoning tokens on a NLG task. |
| **Temperature** | 0.3 | Higher than 0 would feel templated; lower than 0.3 would feel robotic. |
| **Bash access** | Complete deny | No need for shell execution — even `git log` is handled by the changelog skill. |
| **Webfetch** | Allow | Enables API research. Scribe disallows it — we accept the trade-off for richer documentation. |
| **Edit scoping** | Prompt-enforced | OpenCode permissions cannot scope edits by file extension; prompt instructions are the practical alternative. |
| **Task permission** | Deny all | Leaf agent — must not delegate. Matches all other RuneSmith leaf agents. |
| **Skill prefix** | `rs-*` only | Namespace isolation from `kb-*` and other ecosystem skills. |
| **Changelog standard** | Keep a Changelog 2.0.0 | Explicit standardisation prevents format drift across documentation sessions. |

## 9. Open Questions

1. **Should webfetch have a domain allowlist?** Currently, webfetch is unrestricted (`allow`). A restricted set (e.g., `github.com`, `pypi.org`, `npmjs.com`) would reduce the risk of the tech-writer fetching arbitrary URLs. However, this would also prevent legitimate research of less common sources.

2. **Should the tech-writer produce documentation as PRs?** Currently, the tech-writer writes files and reports back to the Architect, which coordinates the commit. An alternative is to let the tech-writer create branches and PRs directly via `gh` — but this would require granting bash access for `gh pr create`, which the current design explicitly avoids.

3. **Should there be a documentation linter skill?** A `rs-doc-lint` skill that checks documentation for broken links, stale content, or style violations could be invoked after writing. This would shift the tech-writer from "write and report" to "write, lint, fix, report" without adding bash access.

4. **Should webfetch results be cached?** If the tech-writer fetches the same external reference across multiple invocations, caching would reduce latency. This could be implemented as a local skill that stores fetched content in a `.runesmith/{date}-{branch}/cache/` directory.

These will be resolved as the agent file is implemented in the plugin repository.

## See Also

- Architect agent: `research/opencode-runesmith/agents/architect.md`
- Developer agent: `research/opencode-runesmith/agents/developer.md`
- Spec-writer agent: `research/opencode-runesmith/agents/spec-writer.md`
- Agent file reference: `knowledge/tooling/opencode/agents/agent-file-reference`
- Permissions model: `knowledge/tooling/opencode/agents/permissions`
- Keep a Changelog 2.0.0: [https://keepachangelog.com/en/2.0.0/](https://keepachangelog.com/en/2.0.0/)

---
title: "Consult Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - skills
  - consult
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
references:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# rs-consult Skill Design

The `rs-consult` skill defines a structured Subject Matter Expert (SME) consultation pattern for agents in the `@runicengines/opencode-runesmith` plugin. When an agent encounters an unfamiliar technology, library, domain concept, or complex configuration, this skill provides a repeatable workflow for bridging the knowledge gap through systematic investigation rather than guesswork.

## Purpose

`rs-consult` exists to answer one question: **how should an agent handle what it doesn't know?** It is not a knowledge base lookup — the knowledge base already handles storing and retrieving facts. Instead, `rs-consult` is a meta-skill: it tells the agent *how to consult*, not *what to consult*. It guides the agent through identifying the precise knowledge gap, searching available resources, formulating and testing hypotheses, and documenting what was learned in a structured consultation report.

This pattern prevents agents from silently guessing or hallucinating domain-specific facts. By making the consultation process explicit, the agent can surface its confidence level, flag open questions for a human SME, and produce a reusable record that can feed back into the knowledge base.

## Trigger Conditions

Any agent — most commonly the architect agent — should invoke this skill when it encounters any of the following during a task:

- **Unfamiliar technology or library**: An import, dependency, or framework the agent has not worked with before (e.g., a Rust crate for audio processing, a Python library for statistical modeling).
- **Domain-specific concept**: A term, algorithm, or pattern from a specialized field such as financial calculations, game physics, medical data formats, or regulatory compliance.
- **Complex configuration**: A configuration file, build script, or deployment manifest whose options and semantics are not immediately clear from context.

The skill is triggered reactively — the agent does not pre-emptively consult; it consults when a gap is identified during normal workflow execution.

## Consultation Workflow

The workflow consists of four sequential phases:

### Phase 1: Identify the Knowledge Gap

The agent must articulate what it does not know as a concrete, bounded question. Vague gaps ("I don't understand this build system") are decomposed into specific, answerable sub-questions ("What is the syntax for defining a custom rule in `justfile`?"). The output of this phase is a precise gap statement.

### Phase 2: Search Available Resources

The agent searches across all accessible sources in order of reliability:

1. **Project-internal documentation**: Existing knowledge base entries, README files, docstrings, and code comments.
2. **Official documentation**: Vendor docs, API references, language specifications (fetched via `webfetch`).
3. **Codebase patterns**: How similar problems have been solved elsewhere in the project (uses `rs-discover` if available).
4. **External references**: Blog posts, tutorials, community guides, RFCs.

The agent should attempt at least two distinct sources before moving to Phase 3.

### Phase 3: Formulate and Validate a Hypothesis

Based on the gathered context, the agent constructs a hypothesis about how the unfamiliar thing works. It then validates by:

- Cross-referencing against official docs or authoritative sources.
- Checking consistency with existing code patterns in the project.
- Identifying contradictions or gaps in understanding.

### Phase 4: Document Findings for Reuse

The agent writes a consultation report (see Output Format below) and, if appropriate, proposes a new knowledge base entry or update so the findings persist beyond the current session.

## Output Format

Every consultation produces a structured report with these fields:

```markdown
## Consultation Report

### Knowledge Gap
<!-- The precise question being investigated -->

### Sources Consulted
<!-- What was searched, with links or paths -->

### Findings
<!-- What was learned, in summary form -->

### Confidence Level
<!-- High / Medium / Low — and why -->

### Open Questions
<!-- What remains unresolved, flagged for a human SME -->
```

The confidence level is mandatory. `High` means the answer was confirmed by authoritative sources with no contradictions. `Medium` means the answer is inferred from multiple consistent sources but not explicitly confirmed. `Low` means the answer is speculative and requires human review.

## Relationship to Other Skills

`rs-consult` is distinct from and complementary to other `rs-` skills in the plugin:

| Skill | Purpose | When Used |
|---|---|---|
| `rs-consult` | Domain expertise consultation | Unfamiliar technology/domain |
| `rs-discover` | Codebase structure scanning | Navigating project layout |
| `rs-issue-to-plan` | Issue decomposition | Converting GitHub issues into structured plans |

`rs-consult` can be chained from any workflow skill. For example, a workflow skill that needs to configure a WebSocket server might call `rs-consult` to understand the library interface, then continue execution with the new knowledge context. It is designed as a pure utility — no side effects, no file modifications — invoked purely for information gathering.

## Open Questions

- Should `rs-consult` auto-create a knowledge base entry on completion, or merely recommend one?
- Should confidence thresholds gate whether an agent proceeds autonomously or pauses for human input? A `Low` confidence result may warrant a hard stop.
- How should the skill handle contradictory information from different sources? The current design defers to authority (official docs > blog posts) but this heuristic may need refinement.

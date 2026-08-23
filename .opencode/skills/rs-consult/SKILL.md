---
name: rs-consult
description: >
  Guide the agent through unfamiliar technologies and domains
  using a structured 4-phase workflow: identify knowledge gap,
  search available resources, formulate/validate hypothesis,
  document findings for reuse.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: planning
  audience: developers
  trigger: manual+chained
---

## Purpose

Meta-skill that answers "how should an agent handle what it doesn't know?" It guides the agent through identifying the precise knowledge gap, searching available resources, formulating and testing hypotheses, and documenting findings. Not a knowledge base lookup — it tells the agent _how_ to consult, not _what_ to consult. Prevents silent guessing or hallucination of domain-specific facts. Consultation reports are session-cached (60s TTL); repeated lookup of the same gap returns the cached report.

## When to Invoke

Triggered reactively when a knowledge gap is identified during normal workflow execution (not pre-emptively):

1. **Unfamiliar technology or library** — An import, dependency, or framework the agent has not worked with before.
2. **Domain-specific concept** — A term, algorithm, or pattern from a specialized field (financial calculations, game physics, medical data formats, regulatory compliance).
3. **Complex configuration** — A config file, build script, or deployment manifest whose options are not immediately clear.

## Workflow Steps

### Phase 1: Identify the Knowledge Gap

Articulate what is not known as a concrete, bounded question. Decompose vague gaps ("I don't understand this build system") into specific, answerable sub-questions ("What is the syntax for defining a custom rule in justfile?"). Output: a precise gap statement.

### Phase 2: Search Available Resources

Search across all accessible sources in order of reliability:

1. **Project-internal documentation** — knowledge base entries, READMEs, docstrings, code comments.
2. **Official documentation** — vendor docs, API references, language specs (via `webfetch`).
3. **Codebase patterns** — how similar problems were solved; reference `rs-discover` if available.
4. **External references** — blog posts, tutorials, community guides, RFCs.

If the first source provides a definitive, high-confidence answer, proceed to Phase 3. Otherwise, search additional sources until the gap is resolved or all practical sources are exhausted.

### Phase 3: Formulate and Validate a Hypothesis

Construct a hypothesis based on gathered context. Validate by:

- Cross-referencing against official docs or authoritative sources.
- Checking consistency with existing code patterns in the project.
- Identifying contradictions or gaps in understanding.

### Phase 4: Document Findings for Reuse

Write a consultation report with the 5 required sections (see Output Format below). If appropriate, propose a new knowledge base entry (do NOT auto-create — recommend only).

## Output Format

Every consultation produces a structured report with these mandatory fields:

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

## Escalation

| Level      | Meaning                                                                       |
| ---------- | ----------------------------------------------------------------------------- |
| **High**   | Answer confirmed by authoritative sources with no contradictions              |
| **Medium** | Answer inferred from multiple consistent sources but not explicitly confirmed |
| **Low**    | Answer is speculative and requires human review                               |

If confidence level is below Medium after Phase 4, the skill MUST escalate to a human SME. The consultation report is still produced but flagged for human review.

## Contradictory Information

When sources disagree, document both sides with explicit confidence labels for each. Note which source is more authoritative and why.

## Required Permissions

| Tool     | Required      | Scope                | Purpose                                                      |
| -------- | ------------- | -------------------- | ------------------------------------------------------------ |
| webfetch | Yes           | External URLs        | Fetch official docs, API references, tutorials               |
| grep     | Yes           | Source tree          | Search codebase for patterns relevant to the gap             |
| glob     | Yes           | Source tree          | Find relevant documentation files                            |
| read     | Yes           | Knowledge base, docs | Read project-internal knowledge and docs                     |
| bash     | No (optional) | git operations       | Pull latest KB changes if needed                             |
| edit     | No            | —                    | Never modifies files                                         |
| write    | No            | —                    | Never creates files                                          |
| delegate | No            | —                    | Never delegates to KB agents; meta-skill guides own research |

## Chained Skills

May reference `rs-discover` outcome during Phase 2 Step 3 (codebase pattern analysis) if the knowledge gap relates to existing code patterns. Not a hard dependency — proceeds without it if unavailable.

## See Also

- `rs-discover` (codebase context)
- `rs-issue-to-plan` (consumer of this skill)

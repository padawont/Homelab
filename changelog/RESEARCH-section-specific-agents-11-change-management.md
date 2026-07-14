---
title: "Change Management: Tracking Updates to Research, Agents, and Skills"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-05-31
tags:
  - opencode
  - agents
  - skills
  - governance
  - changelog
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-configuration"
  - knowledge: "knowledge/tooling/opencode/skills/skill-configuration"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-05-31
---

# Change Management: Tracking Updates to Research, Agents, and Skills

## 1. The Problem

Currently, only ideas require `changelog.md`. Research topic folders, knowledge notes, agent definitions, and skills have no mechanism to track changes. The `last_audit_date` field is overwritten in place — no history preserved. When an agent or skill is modified, there is no record of what changed or why, and no validation checklist to confirm it still works.

## 2. What Currently Exists

- **Ideas:** `changelog.md` with YAML entries array (`date`, `description`, `author`)
- **Proposals:** versioned (integer `version` field + `.qmd` snapshots + versioned PDFs)
- **ADR:** `replaces`/`replaced-by` linking, `history` PR link
- **Knowledge/Research:** `last_audit_date` in frontmatter (overwritten, no history)
- **Agents/Skills:** no change tracking at all (runtime configs)

## 3. Proposed: Research changelog.md

Research topic folders should adopt a changelog.md following the same YAML entries pattern as ideas:

```yaml
---
entries:
  - date: YYYY-MM-DD
    description: What changed and why
    author: Name
---
```

Each entry records a change to any file in the research topic folder. When research is updated, add an entry and update `last_audit_date` in `overview.md`.

This should be added as a recommended convention in `research/AGENTS.md`.

## 4. Agent and Skill Changes (Runtime Configs)

Agent `.md` files and skill `SKILL.md` files are OpenCode runtime configurations, not knowledge base documents. They should NOT adopt `last_audit_date` or YAML changelog entries in their frontmatter — those fields do not exist in the OpenCode agent or skill schema, and adding them would be ignored or cause confusion.

Instead, changes to agents and skills are tracked via:
- **Git commit history** — the canonical record of what changed and when
- **Related research changelog.md** — when a research finding triggers an agent/skill change, note it in the research changelog.md entry
- **Related knowledge last_audit_date** — when agent/skill design changes, consider updating the `last_audit_date` in relevant knowledge notes about agents and skills

## 5. Review Process

When a PR touches `.opencode/agents/` or `.opencode/skills/`:

1. **Verify against research** — check `research/section-specific-agents/` to see if the change contradicts any research finding. If so, update the research note and add a changelog.md entry.
2. **Run smoke tests** — execute relevant tests from `09-verification.md` (scaffold, validate, cross-link, status transition)
3. **Update knowledge notes** — if agent/skill behavior changed, update `knowledge/tooling/opencode/agents/` or `knowledge/tooling/opencode/skills/` and refresh `last_audit_date`
4. **Document in git** — write a descriptive commit message explaining what changed and why

## 6. Future Considerations

- If research topic folders grow significantly, consider adding a `version` field to research `overview.md` frontmatter (like proposals)
- If audit frequency becomes a concern, agents could be extended with a prompt that checks `last_audit_date` staleness in research and knowledge notes
- The ideas changelog template at `templates/idea/changelog.md` could serve as a generic template if promoted to `templates/changelog.md`

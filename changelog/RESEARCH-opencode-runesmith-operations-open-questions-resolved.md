---
title: "Resolved Open Questions"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - decisions
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/plugins/overview.md"
  - knowledge: "knowledge/tooling/opencode/agents/permissions.md"
references:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# Resolved Open Questions

This file captures every open question from the idea `ideas/organisation/tools/org-wide-agent-plugin/` and the subsequent research process, along with each resolved decision. It serves as the canonical record of all design choices made during the RuneSmith plugin research phase.

---

## Questions from the Idea

### Q1: How should the plugin discover which knowledge-base repo to query?

**Context:** The RuneSmith plugin needs to search the RunicEngines knowledge base to answer technical questions. To do this, it must first know which repository to clone and search.

**Decision:** Config URL approach. The KB repo URL (`github.com/RunicEngines/knowledge-base`) is stored in agent prompts and an `rs-kb-search` skill handles the actual searching. Stale clones are refreshed with a simple `git pull` before each search operation.

**Rationale:** Hard-coding the URL in agent prompts keeps the configuration transparent and easily auditable. The `rs-kb-search` skill encapsulates all search logic (grep/glob patterns, clone management, pull strategy) so individual agents don't need to know the mechanics. Git pull is sufficient because the KB is append-only in practice — no history rewrites that would require a fresh clone.

---

### Q2: What is the registration contract for adding new subagents or skills?

**Context:** The plugin ships with a set of agents and skills, but users may want to extend it. A clear contract is needed so extensions are predictable.

**Decision:** Convention-based registration. New agents go in `.opencode/agents/rs-{name}.md`. New skills go in `.opencode/skills/rs-{name}/SKILL.md`. No registry, manifest, or configuration file is required. The `rs-` prefix prevents namespace collisions with other plugins or manually configured agents.

**Rationale:** OpenCode auto-discovers agents and skills by scanning the `.opencode/` directory. A convention-based approach leverages this built-in discovery mechanism — no separate registration step needed. The `rs-` prefix acts as a namespace partition, ensuring RuneSmith components don't collide with components from other plugins or user-defined agents.

---

### Q3: How do we handle version compatibility between the plugin and KB content?

**Context:** If the knowledge base changes its internal structure (e.g., frontmatter format, directory layout), the plugin's search capabilities could break.

**Decision:** Zero version coupling. The plugin does NOT depend on specific KB content structure. KB search is done via grep and glob, which work regardless of content format changes.

**Rationale:** Grep and glob operate on raw file contents and paths — they don't parse frontmatter, understand schemas, or depend on directory conventions. As long as the KB remains a Git repository of markdown files, the search skill will function. This eliminates the need for version negotiation between plugin and content.

---

### Q4: Should the plugin ship with default configurations or require per-repo setup?

**Context:** Each repository that uses the RuneSmith plugin could theoretically need its own configuration. The question is whether to automate this.

**Decision:** Ship with defaults. The plugin init hook copies agents and skills into `.opencode/`. The consumer only adds the plugin name to `opencode.json`. Everything else is automated.

**Rationale:** Manual per-repo setup is error-prone and creates friction for adoption. The init hook — triggered on plugin install — bootstraps the entire `.opencode/` directory structure with sensible defaults. The consumer's only manual step is adding `"runesmith"` to their `opencode.json` plugin array. If customization is needed later, the convention-based contract (Q2) makes it straightforward to override or extend individual components.

---

## Questions Resolved During Research

### Q5: Skill prefix?

**Context:** Skills need a naming convention to avoid collisions in OpenCode's flat skill namespace.

**Decision:** `rs-` (RuneSmith). Examples: `rs-issue-to-plan`, `rs-discover`, `rs-consult`.

**Rationale:** Consistent with the agent naming convention (Q2). The `rs-` prefix is short, distinctive, and clearly identifies the skill's origin. Using the same prefix for both agents and skills creates a cohesive naming system.

---

### Q6: KB agent cross-delegation?

**Context:** The knowledge base has its own specialized agents (`knowledge-agent`, `research-agent`). Should RuneSmith agents delegate KB queries to them?

**Decision:** Separate. RuneSmith agents do NOT delegate to KB agents. They search the KB via the `rs-kb-search` skill but never invoke KB agents.

**Rationale:** Agent delegation introduces latency, dependency, and failure modes (KB agent might not be loaded, might be busy, might reject the task). The `rs-kb-search` skill is a direct, synchronous operation that runs grep/glob against a local clone. It's faster, more reliable, and avoids circular delegation chains. The KB agents remain independent for their own purposes (writing knowledge notes, producing research).

---

### Q7: Update propagation mechanism?

**Context:** When the plugin is updated, the agents and skills in `.opencode/` may need to be refreshed.

**Decision:** Version-stamping plus a CLI update command. The init hook writes a `.opencode/.runesmith-version` file containing the installed plugin version. Before each session, the update mechanism checks this file against the current plugin version. On mismatch (or via explicit `bunx @runicengines/opencode-runesmith update` command), stale components are re-copied from the plugin bundle.

**Rationale:** A version stamp avoids re-copying on every session (which would overwrite user customizations). The check-before-each-session approach catches updates promptly. The explicit `bunx @runicengines/opencode-runesmith update` command gives users control when they want to trigger the update manually. User modifications to `.opencode/` files are preserved unless the plugin bundle explicitly replaces them (signaled by a file hash comparison).

---

### Q8: Agent file naming?

**Context:** Agent filenames need to be consistent and predictable for auto-discovery.

**Decision:** `rs-{role}.md` pattern. Examples: `rs-developer.md`, `rs-reviewer.md`, `rs-architect.md`.

**Rationale:** OpenCode discovers agents by scanning `.opencode/agents/*.md`. The `rs-{role}.md` pattern is descriptive, scoped by prefix, and matches the convention established in Q2. The role name (developer, reviewer, architect) is human-readable and maps directly to the agent's purpose.

---

### Q9: Permissions model?

**Context:** Agents need different tool access levels depending on their role.

**Decision:** Permissive defaults with targeted restrictions per agent:
- Reviewer: `edit: deny`
- Tech-writer: `bash: deny`
- Leaf agents (all except architect): `task: deny`

**Rationale:** Granting broad access by default and restricting per-agent is simpler than maintaining allowlists. Denials are explicit and documented in each agent's definition. The `edit: deny` for reviewers enforces the review-before-edit workflow. `bash: deny` for tech-writers prevents accidental shell execution during documentation tasks. `task: deny` for leaf agents prevents delegation loops.

---

### Q10: Architect-only agent with `task` permission?

**Context:** The delegation hierarchy needs a clear root agent that can spawn sub-agents.

**Decision:** Yes. Only the architect agent has `task: allow`. All other agents are leaf agents with `task: deny`. This prevents delegation loops.

**Rationale:** A single root agent with task permission creates a clear delegation hierarchy. The architect orchestrates work by spawning specialised agents (developer, reviewer, tech-writer), each of which operates independently and cannot delegate further. This prevents infinite delegation chains and keeps the agent interaction graph a simple tree structure.

---

### Q11: Plugin written in JS/TS despite Python developers?

**Context:** The RuneSmith team primarily uses Python, but OpenCode's plugin SDK only supports JavaScript/TypeScript.

**Decision:** Yes, JS/TS is unavoidable. The Python SDK does not support plugins at this time. A `js-for-python-devs` knowledge note will be written to help bridge the gap.

**Rationale:** There is no viable alternative — OpenCode's plugin system is JS/TS only. Attempting to wrap a Python backend would add complexity, latency, and a second runtime dependency. A dedicated knowledge note translating Python concepts to JS equivalents (async/await vs asyncio, npm vs pip, CommonJS vs modules, etc.) lowers the cognitive barrier for the team. The note also covers the subset of JS/TS needed specifically for plugin development, avoiding unnecessary language overhead.

---

### Q12: What is the `.runesmith/` scratchpad directory?

**Context:** Several agents and skills need a writable workspace for output files — specs, test reports, logs, caches. Without a defined convention, each agent would scatter files across the project root. Additionally, multiple development sessions (on different branches or dates) must not overwrite each other's output.

**Decision:** The init hook creates the base `.runesmith/` directory only. Session-scoped subdirectories use the pattern `{date}-{branch}` and are created on demand by the first agent that writes to them. The session path is determined at runtime from the git branch name and current date.

For example, a session on branch `feat/42-auth` on June 7 2026 would use `.runesmith/2026-06-07-feat-42-auth/specs/`. This keeps output from different branches completely isolated. If a second session starts on the same branch the same day, a counter is appended: `2026-06-07-feat-42-auth-2/`.

| Path | Created By | Used By | Contents |
|---|---|---|---|
| `.runesmith/{date}-{branch}/specs/` | Spec-writer (on demand) | Spec-writer | Implementation plans: `{issue-number}-{slug}.md` |
| `.runesmith/{date}-{branch}/reports/` | Test-writer (on demand) | Test-writer | Test results: `{issue-number}-{slug}-test-report.md` |
| `.runesmith/{date}-{branch}/logs/` | Architect (on demand) | Architect | Pipeline errors, delegation history, session logs |
| `.runesmith/{date}-{branch}/cache/` | KB search / Tech-writer (on demand) | KB search, Tech-writer | Webbfetch results, cloned KB repo |
| `.runesmith/flaky.yml` | Test-helper-diagnose (on demand) | Test-writer | Known flaky tests registry (shared across sessions) |
| `.runesmith/security.yml` | Review-security (on demand) | Reviewer | Security baseline overrides (shared across sessions) |

**Rationale:** Session-scoped subdirectories prevent collisions when working on multiple branches simultaneously — each branch's specs, reports, and logs live in their own directory tree. The `{date}-{branch}` pattern provides chronological ordering and clear identification. Global config files (`flaky.yml`, `security.yml`) remain shared because they represent project-wide state, not session-specific output. Gitignoring by default prevents accidental commits of transient or large files. The init hook only creates the root `.runesmith/` directory — session subdirectories are created on demand by the agents that use them, avoiding empty directories for unused sessions.

---

### Q13: Are `.runesmith/` session files cleared at session start? Can a resumed OpenCode session use them as-is?

**Context:** The ephemeral `.runesmith/` directory holds per-session artifacts. The lifecycle between a fresh session, a resumed session, and manual cleanup must be clearly defined.

**Decision:**
1. **Files are NEVER automatically cleared.** A new session gets a different path (`{date}-{branch}` changes daily or per-branch), so it starts clean without explicit clearing. Same-branch same-day collisions get a counter suffix.
2. **Same-branch same-day collision** — if a session directory already exists for today's date+branch, the agent MUST ask the user: "Session directory `{path}` already exists. Resume from existing session, or start fresh with `{path}-2`?" Only proceed with the counter suffix after receiving user confirmation.
3. **Resumed sessions use files as-is.** Because the path is deterministic from the same date+branch, a resumed OpenCode session finds the exact same files — specs, reports, and logs from the previous run. The architect loads existing specs rather than regenerating them.
4. **Manual cleanup** is `rm -rf .runesmith/`. Everything in `.runesmith/` is regeneratable by the init hook and agents.

| Action | Path | Files | Recoverable? |
|---|---|---|---|
| Fresh session, new branch | New `{date}-{branch}` | Empty | N/A |
| Same branch, new session same day | `{...}-2`, `{...}-3` | Empty | N/A |
| Resume OpenCode session | Same as before | Preserved | Yes — pick up where left off |
| `rm -rf .runesmith/` | — | Gone | Yes — init hook recreates root, agents regenerate content |

**Rationale:** Never clearing files is the simplest and safest default. The user owns their scratchpad — if they want a clean slate, they delete the directory. The deterministic path based on date+branch ensures session identity without needing OpenCode's internal session ID (which agents cannot access directly). The counter suffix handles the only collision case (same branch, same day, new session) without breaking determinism for resumed sessions.

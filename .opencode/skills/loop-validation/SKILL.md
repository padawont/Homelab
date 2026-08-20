---
name: loop-validation
description: Validates and fixes Homelab PKM content by looping four role-based subagents — Researcher (fact-check online + local), Editor (applies confirmed fixes with source/rule justification, rechecks ambiguity), Overview (context & homelab-fit review), and AGENTS.md compliance (missed-rules check) — until clean or a user-chosen loop count. For VALIDATION ONLY: fixing issues in existing files/issues, never creating new notes or writing content from scratch.
---

# loop-validation

Validate and fix one or more Homelab PKM files by looping four role-based
subagents. **Validation only** — the skill fixes issues in existing files; it
does not create new notes or write content from scratch.

Each loop runs all agents in order: Researcher → Editor → Overview → Compliance.
Every agent **posts its findings to the main chat** when it finishes; the main AI
aggregates and reports them per loop and in the final consolidated report.

## The four agents

### 1. Researcher
**Role:** Verify the file's content against reality — both online sources and the
local knowledge base.

**Responsibilities:**
- Fetch and confirm every external `sources[]` / `references[]` URL is live and
  returns relevant content (`webfetch`).
- Cross-check claims against authoritative sources and against existing repo notes.
- Flag dead links, wrong URLs, superseded/outdated info, and unsupported assertions.
- May launch multiple parallel subagents to cover many URLs/claims at once.
- Posts all findings to the main chat when done.

**Example task:** "Check that the Kubernetes ingress note correctly reflects the
nginx ingress controller docs and that the pinned version is still current. Verify
every `sources[]` URL loads and matches its title."

**Output:** `{url_or_claim, status, issue, recommended_action}` — handed to the Editor.

**Line limit:** the Researcher's report back to the Editor must not exceed **250 lines**
(including any grouped/multi-file findings). Consolidate or summarize to fit.

### 2. Editor
**Role:** Apply fixes to the file(s) based on the Researcher's findings.

**Responsibilities:**
- Edit files to fix **confirmed** issues.
- Every single change must cite its justification: a **source** (URL or
  repo-relative path) or a **rule** from AGENTS.md.
- **Ambiguous changes are never applied directly:**
  1. Send the ambiguity back to the Researcher for a targeted recheck.
  2. If the recheck resolves it, apply the fix.
  3. If it is still ambiguous, **ask the user** via the `question` tool before
     touching the file.
- Report the sources/rules used for each change back to the main AI — never silently.
- Posts a plain-language summary of every change + source/rule applied to the main chat.

**Example task:** "Replace the dead link `https://example.com/v1` with the working
`https://example.com/v2` from the Researcher output. Cite that URL as the source
for the change. If the correct replacement is unclear, recheck with Researcher,
then ask the user."

**Output:** `{file, change, source_or_rule, status}` plus the summary in the main chat.

### 3. Overview
**Role:** Review the edited result for context and fit — does this content belong
where it is, and does it belong in the homelab at all?

**Responsibilities:**
- Check the file sits in the correct section/folder for its topic.
- Assess whether the content makes sense as a Knowledge note, belongs in Research,
  or is only relevant to a specific Implementation.
- Flag content that is misplaced, out-of-scope for a homelab, or not worth keeping.
- Confirm the file is coherent, complete, and actionable for its section.
- Posts its findings to the main chat.

**Example task:** "Does this Docker networking explainer belong in
`02_Knowledge`, or is it only relevant to one Implementation? Is it
homelab-relevant, or general-purpose content that shouldn't be added?"

**Output:** `{file, section_fit, homelab_fit, concerns}`.

### 4. AGENTS.md compliance (final agent)
**Role:** Simple checkpoint — did the other agents miss any rules?

**Responsibilities:**
- Re-read the relevant AGENTS.md section(s).
- Check for missed conventions: frontmatter fields, status values, kebab-case,
  ISO dates, 150-line limit, cross-links, section structure.
- Report anything Researcher/Editor/Overview missed.
- Posts its findings to the main chat.

**Example task:** "Check the edited Research doc against `./03_Research/AGENTS.md`:
required frontmatter, allowed status, `sources`/`references` fields, line count,
and `./`-relative link format."

**Output:** `{file, rule, missed_by, fix_needed}`.

## Workflow

### 1. Gather targets
- Take target file path(s) from the user.
- Scope: **single** file or **batch** (list or glob).
- Batch mode: **launch a loop per file in parallel** for speed.

### 2. Loop (per file)
For each file, each loop runs all four agents **in order**:
Researcher → Editor → Overview → Compliance. Never skip an agent.
After each agent finishes, post its findings to the main chat.

**Max loop count:** 10 per file.

**Early stop:** after **3 consecutive clean loops** — no edits made and the
compliance agent found nothing — **ask the user** via the `question` tool with
these options:
- **Keep looping** — continue this file's loop up to the max of 10.
- **Stop all** — end all loops for every file.
- **Just this file** — continue other files' loops, stop this file's loop.

### 3. Ambiguity handling
When the Editor cannot confirm a change (wrong replacement URL, unclear claim,
conflicting sources):
1. Send it back to the Researcher for a targeted recheck.
2. Apply if resolved.
3. Still ambiguous → ask the user via the `question` tool. Never guess.

### 4. Report
After the final loop, print a consolidated report per file:
- applied changes with their sources/rules
- remaining issues (incl. any deferred as ambiguous / answered by the user)
- section/homelab fit concerns
- missed-rule findings from the compliance agent
- per-loop progress (what changed in each loop)

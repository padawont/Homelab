---
name: knowledge-gap
description: >
  Shared core for the knowledge-gap audit skills. Runs ONLY while working on a
  service or process (Research / ADR / Implementation), when the Knowledge
  needed to fix, maintain, or create it is missing or insufficient. Turns facts
  the stage had to source online into standardized, issue-ready gaps (epic or
  single issue). Never a standalone audit of 02_Knowledge/. Read-only on notes.
---

# knowledge-gap (core)

Shared engine behind `knowledge-gap-research`, `knowledge-gap-adr`, and
`knowledge-gap-implementation`. The phase skills own only the online-only
claim scan; locating, inspecting, reporting, and filing are common here.

Not a standalone audit — load it through one phase skill.

## Purpose

Answers one question, always in the service of another stage: **do we have
enough Knowledge to fix, maintain, or create this service/process?** It has no
meaning on its own — it only runs as part of Research, ADR, or Implementation
work.

## Scope rule — in service of another stage

- Runs **only** while a stage is working on a service or process.
- **Never** audits `02_Knowledge/` for its own sake — a bare "check my
  Knowledge base" request is out of scope.
- Its output is only meaningful paired with the stage that hit the gap.

## When to use

- You are researching, deciding (ADR), deploying, operating, fixing, or
  maintaining a service/process, and the stage had to source facts online
  because Knowledge coverage is missing or too thin.
- You are about to fix, maintain, or create a service/process and the backing
  Knowledge is not sufficient to do it.

## When NOT to use

- Auditing the Knowledge section on its own, with no dependent service/process.
- Writing, fixing, or maintaining Knowledge notes (capture pipeline /
  `implement`).
- Validating an existing file (`loop-validation`) or checking duplication
  (`dry-audit`).
- Non-PKM content.

## Trigger — online-only facts

A candidate gap is any fact the stage needed that is cited **only** to an
online source (`references[].url` / `references.online[]` / `sources[].url`)
and has no `./02_Knowledge/` backing. A claim already backed by a Knowledge
path is covered and never becomes a candidate.

Every online-only fact is a candidate — no filtering at this step. The
inspection (below) decides whether an existing note already covers it.

## Findings (gap types)

| ID | Finding | Detection |
|---|---|---|
| G1 | `missing-folder` | The `<category>/<topic>/` folder under `02_Knowledge/technologies/` does not exist |
| G2 | `missing-note` | Folder exists, but no note scopes the concept |
| G3 | `too-small` | Note exists but body is under ~15 non-frontmatter lines |
| G4 | `thin` | No `## Details` heading, placeholder text, or an empty section. `status: draft` is an **advisory flag, not a trigger** — it fires a G4 only alongside a structural signal |
| G5 | `stale` | `last_audit_date` older than 7 days (weekly rule) or `status: archived`. Equal severity to the others |
| G6 | `no-homelab-info` | No node/host name, IP, namespace, real config, or implementation link |
| G7 | `no-hosting-info` | Concept is hostable but the note has no install method, namespace/placement, ports, storage/PVC, resources, or integration points |
| — | `covered` | Adequate note found — candidate is dropped, no gap emitted |

G6 and G7 differ: G6 asks "does this say anything about the homelab?", G7 asks
"does it say how the thing is hosted?" A note can be homelab-relevant and still
lack hosting detail.

## Pipeline

```
1. SCAN     (phase skill)        claims cited only online -> candidates
2. LOCATE   (main)               concept -> 02_Knowledge/technologies/<category>/<topic>/
3. INSPECT  (inspection agent)   per candidate/folder -> one finding record
4. REPORT   (main)               standardized, issue-ready records
5. FILE     (main, confirmed)    epic or single issue
```

### INSPECT

- Launch the **inspection agent** — bind `pkm-overview` (its frontmatter sets
  `edit: deny` and `webfetch: deny`, so read-only is permission-enforced). One
  agent per candidate, or batch per topic folder, all in parallel.
- Give each agent: the concept, the online URL it came from, the target
  category folder, and the findings table above.
- It returns one record per candidate — `covered` drops the candidate. It never
  edits, never fetches the web, never guesses.

## Standard report

Emit the YAML record, an issue-ready markdown block, and the table.

```yaml
knowledge_gap:
  id: KG-001
  phase: research | adr | implementation
  concept: "cert-manager TLS issuance"
  trigger: "online-only — https://cert-manager.io/docs/, no 02_Knowledge path"
  folder_inspected: "02_Knowledge/technologies/kubernetes/"
  finding: missing-folder | missing-note | too-small | thin | stale |
           no-homelab-info | no-hosting-info
  issue_kind: single | epic
  title: "Knowledge: cert-manager on k3s"
  label: knowledge
  note_planned: "02_Knowledge/technologies/kubernetes/cert-manager/tls-issuance.md"
  parent: "#316"
  sources:
    - "https://cert-manager.io/docs/"
    - "./03_Research/agones-adoption/overview.md"
  evidence: "no cert-manager folder; 10 incidental mentions only"
  advisory: ["status: draft", "last_audit_date 2026-08-22 = 34 days"]
  fix: create-note | extend-note | re-audit | needs-human
```

Issue-ready block (fill per gap, from `Templates/tasks/issue.md`):

```markdown
## Objective
Back the {concept} dependency of {stage artifact}.

## Description
{stage} needed {fact} but could only cite {online url}. Inspection of
{folder_inspected} found {finding}.

## In Scope
- {note_planned} — {one-line concept}

## Topic Hierarchy
- {each planned note}: {one-line concept}

## Sources
- {online url} (what it covers)
- {stage artifact} (the dependency)

## Acceptance Criteria
- every planned note <=150 lines, status accepted, live sources[], last_audit_date set
- the stage artifact's claims now cite the note instead of the URL

## Parent
#{parent}
```

Table view:

| id | phase | concept | finding | issue kind | title |
|---|---|---|---|---|---|

## Epic or single issue

Propose, then confirm at filing:

- **single** — one note needed (`missing-note`, `too-small`, `thin`, `stale`,
  `no-homelab-info`, `no-hosting-info` on an existing note) → one `Knowledge:`
  issue.
- **epic** — a whole category or 3–8 atomic notes needed (`missing-folder`) →
  an epic plus its `Knowledge:` sub-issues, per the `create-github-issues`
  atomic-breakdown rule.

## GitHub issue filing (after confirmation)

Issues live in `RunicEngines/knowledge-base`; notes live here. Read
`create-github-issues` for issue structure only.

1. Present the table and WAIT. The user picks the gaps and supplies the
   **parent epic** number (or names the stage's issue). Never file without one.
2. Dedupe:
   `gh issue list --state open --search "{concept}" --repo RunicEngines/knowledge-base`.
   Skip tracked concepts; report the existing number instead.
3. File single:
   `gh issue create --title "Knowledge: {title}" --body-file {id}.md --label knowledge --parent {epic-number} --repo RunicEngines/knowledge-base`
4. File epic: create the epic (`--label epic`), then each sub-issue with
   `--label knowledge --parent {new-epic-number}`.
5. Verify nesting:
   `gh issue view {epic-number} --json subIssues --repo RunicEngines/knowledge-base`

Filing is a GitHub write, not a note write — the audit never edits
`02_Knowledge/`.

## Hand-off

- Missing / thin / too-small note → Knowledge issue filed on confirmation; the
  capture pipeline writes it.
- Stale note → re-audit; `needs-human` if genuinely superseded.
- `no-homelab-info` / `no-hosting-info` → extend via a Knowledge issue; never
  drop the concept silently.
- Ambiguous match or fix → `needs-human`; never guess.

## Guardrails

- **Read-only on notes** — never create, edit, or delete a note.
- **Inspection agent is read-only** — bind `pkm-overview` (`edit: deny`,
  `webfetch: deny`); never use a writable general agent for inspection.
- **No fabrication** — report only what is on disk; every gap carries evidence.
- **No guessing** — ambiguity → `needs-human`.
- **Confirm before filing** — no issue without the user's parent epic; dedupe.
- **Equal severity** — G1–G7 are reported with equal weight.
- **PKM only** — skip non-PKM paths.

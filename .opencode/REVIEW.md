---
title: "Review contract — five facets, one merged report"
status: accepted
author: "padawont"
date: 2026-11-03
tags: []
sources: []
last_audit_date: 2026-11-03
related_docs: []
---

# Review contract — five facets, one merged report

How the Homelab PKM review works after the single `reviewer` was split into five
single-type subagents. Owns the facet map, the merged report shape, the merge
rule and the verdict precedence — the facts `runesmith`, `editor` and the skills
all depend on. Each facet's own rules live in its agent file.

Fan-out and merge are `runesmith`-only. The hub-and-spoke rule — why a facet
never calls another facet — is `./.opencode/WORKFLOW.md` § Coordination Rule.

## The Five Facets

| type | agent | question it answers | band |
|---|---|---|---|
| `source` | `reviewer-source` | Is every cited URL live, authoritative, and does it actually say what's claimed? | S1–S2 |
| `accuracy` | `reviewer-accuracy` | Are commands, keys, defaults, ports and versions correct for *this* homelab? | S1–S2 |
| `scope` | `reviewer-scope` | Correct folder and depth; homelab relevance per `./AGENTS.md` § General Conventions | S3 |
| `structure` | `reviewer-structure` | Frontmatter, status, kebab-case tags, ISO dates, 150-line rule, `./` links, heading order | S3–S5 |
| `overlap` | `reviewer-overlap` | Duplicates or contradicts another note/ADR — link instead of repeat? | S4–S5 |

This table is canonical for the roster: other files link here instead of
re-enumerating the five types.

## Severity Bands

- **S1** — factually wrong / dead source.
- **S2** — materially misleading; sends the reader down the wrong path.
- **S3** — placement or depth problem; also structure changing what the reader concludes.
- **S4** — pure convention breach, or duplication.
- **S5** — cosmetic or stylistic; never blocks.

This section owns the band text; a facet file may narrow its own band or link
here, never restate or redefine these bands. S1–S2 block, S3–S4 are auto-fixed,
S5 is applied freely.

## Facet Report

Every facet returns the same envelope, with only its own key populated:

```json
{
  "file": "./02_Knowledge/technologies/kubernetes/concepts/ingress.md",
  "folder": "02_Knowledge",
  "types": { "source": [], "accuracy": [], "scope": [], "structure": [], "overlap": [] },
  "unresolved": [],
  "totals": { "S1": 0, "S2": 0, "S3": 0, "S4": 0, "S5": 0 },
  "verdict": "clean | issues | needs_recheck"
}
```

A finding carries `severity`, `issue`, `evidence`, `fix_hint`. At most 5 findings
per facet, ordered by file path then line number.

`unresolved` is always present and always empty in a facet report; its item shape
is `{ "type": "...", "issue": "..." }`. Only `runesmith` fills it, at merge time,
for a facet that did not run, crashed, or returned a finding it could not settle.

The envelope shape is owned here, and this section wins on any conflict with a
facet file. A facet file links here rather than restating the shape, and states
only which key it populates and what its `totals` counts.

Envelope rules owned here — a facet may reference, never redefine them: every key
is always present; `folder` is the section folder or `"N/A"` for an out-of-section
target; no field is ever `null` (emit an empty list or empty string); `fix_hint` is
a fixed recommendation value consumers read verbatim; and `verdict` is one of
`clean`, `issues`, `needs_recheck` — computed only by the hub (§ Verdict Precedence).

## Merged Report

`runesmith` merges the facets for one target into the same envelope — the shape
`editor` consumes. The merge is mechanical:

1. Concatenate each facet's findings into its own `types` key.
2. Recompute `totals` across the merged findings.
3. Keep at most 5 findings per type after the merge.
4. Fill `unresolved` from every facet that did not run, crashed, or returned no
   report, plus every finding a facet could not settle.

## Verdict Precedence

Deterministic because only `runesmith` computes it, at merge time, so the same
input always produces the same verdict. Consumers — `editor`, `loop-validation`,
any skill — read the verdict and never paraphrase or recompute it.

```
any needs_recheck          → needs_recheck  (logged in "unresolved")
else any finding at all    → issues
else                       → clean
```

`needs_recheck` outranks `issues`: an unresolved finding always reaches the human,
even when a definite S1 or S2 is also present. The S1–S2 findings still block, and
the editor still applies every confirmed finding — the precedence only decides what
`runesmith` escalates.

A facet that did not run, crashed, or returned no report makes the merge
`needs_recheck` and is listed under `unresolved` — never silently dropped.

## Routing

`REVIEW.md` owns which consumer receives which report; every handoff still runs
through `runesmith` (`./.opencode/WORKFLOW.md` § Coordination Rule). "Directly"
below means the hub launches that facet for the consumer — never a spoke-to-spoke
call.

| consumer | gets |
|---|---|
| `editor` | the merged report, one per target |
| `loop-validation` | the merged report, posted before the editor runs |
| `research` | a hub-launched `reviewer-source` report; no merge needed |
| `dry-audit` | a hub-launched `reviewer-overlap` report per file |
| `knowledge-gap` | a hub-launched `reviewer-scope` report |

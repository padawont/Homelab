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
single-type subagents. Owns the facet map, the merged report shape and the
verdict precedence — the facts `runesmith`, `editor` and the skills all depend
on. Each facet's own rules live in its agent file.

Fan-out, merge and the hub-and-spoke rule — why a facet never calls another
facet — are defined in `./.opencode/WORKFLOW.md` § Coordination Rule.

## The Five Facets

| type | agent | question it answers | band |
|---|---|---|---|
| `source` | `reviewer-source` | Is every cited URL or `./` repo path live, authoritative, and does it actually say what's claimed? | S1–S2 |
| `accuracy` | `reviewer-accuracy` | Are commands, keys, defaults, ports and versions correct for *this* homelab? | S1–S2 |
| `scope` | `reviewer-scope` | Correct folder and depth (S3); homelab relevance per `./AGENTS.md` § General Conventions (S4) | S3–S4 |
| `structure` | `reviewer-structure` | Frontmatter, status and heading order; line limit, tags, dates and links per `./AGENTS.md` § Atomic File Rule and § General Conventions | S3–S5 |
| `overlap` | `reviewer-overlap` | Duplicates another note/ADR — link instead of repeat? | S4–S5 |

This table is canonical for the roster: other files link here instead of
re-enumerating the five types.

There are no per-topic subsets. Every target gets all five facets, whatever its
section or issue topic; a per-topic reviewer list elsewhere in the skills names
*emphasis* — which facet a defect is most likely to come from — never a reduced
set. A topic that names fewer facets is read through this rule, not instead of
it.

Where `source` and `accuracy` meet, the cited evidence decides which key carries
the finding, and only one does. `source` owns every mismatch between a claim and
the artifact cited for it: when the cited source contradicts the claim, is silent
on it, or cannot be read, the finding is `source`'s and `accuracy` files nothing
for that value. `accuracy` owns a value only when every citation the note offers
for it still asserts it — or the note offers none — and the repo names a
different one. `accuracy` therefore reads the cited artifact before filing and
stops when it does not carry the claim: that defect is already `source`'s.

## Severity Bands

These are the **PKM severity** bands. The code lane's `S1–S5` are a different
scale with different definitions (`./.opencode/skills/rs-review-severity/SKILL.md`)
and the two are never compared or mapped onto each other. The banded shape
follows the severity-level rationale in
https://www.tiobe.com/knowledge/article/severity-levels/ — that source argues for
ordering fixes by level; it does not define these bands, which this section owns.

- **S1** — factually wrong / dead source.
- **S2** — materially misleading; sends the reader down the wrong path.
- **S3** — placement or depth problem; also structure changing what the reader concludes.
- **S4** — pure convention breach, or duplication.
- **S5** — cosmetic or stylistic; never blocks.

This section owns the band text; a facet file may narrow its own band or link
here, never restate or redefine these bands. S1–S2 block, S3–S4 are auto-fixed,
S5 is applied freely.

A finding the facet could not settle still carries the band it would take if it
were confirmed, and that band is advisory: it never decides a verdict by itself.
The `needs-human` marker does — see § Fix Hints.

## Fix Hints

`fix_hint` is a closed vocabulary owned here. Every finding carries exactly one
value from the table, and each type emits only the values listed for it.
Consumers — `editor`, `dry-audit` — read the value verbatim and never translate
it; a consumer that keeps its own record copies the value.

| value | means | emitted by |
|---|---|---|
| `recite` | make the cited evidence carry the claim: repoint the citation, or correct the claim to what the cited source now states | `source` |
| `fix-value` | replace the command, key, default, port or version with the one the repo names | `accuracy` |
| `move` | place the file under the section its content belongs to | `scope` |
| `split` | divide the file at a concept boundary, or split an over-length file | `scope`, `structure` |
| `trim` | remove the passage that is irrelevant to running the service | `scope` |
| `reformat` | correct form — frontmatter, tag, date, heading or link | `structure` |
| `link-instead` | replace the repeated unit with a link to the canonical copy | `overlap` |
| `extract` | hoist the repeated unit into one note both sides link | `overlap` |
| `merge` | collapse the two copies into one | `overlap` |
| `keep` | deliberate repetition; no change | `overlap` |
| `create-note` | the Knowledge note a gap needs does not exist | `knowledge-gap` |
| `extend-note` | the note exists and must grow | `knowledge-gap` |
| `re-audit` | the note is stale | `knowledge-gap` |
| `needs-human` | nothing on hand settles it, or the remedy is a human decision | any |

`needs-human` is also the unsettled marker § Facet Report defines: a finding
carrying it makes its facet's verdict `needs_recheck`, and it is what the merge
copies into `unresolved`. The three `knowledge-gap` values fill no facet report —
they are in this table so the roster keeps one vocabulary instead of three.

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

A finding carries `severity`, `issue`, `evidence`, `fix_hint`; `fix_hint` comes
from § Fix Hints and is restricted to the values listed for that type. At most 5
findings per facet, ordered by file path then line number — and a finding marked
`fix_hint: "needs-human"` is never the one the cap drops.

`unresolved` is always present; its item shape is
`{ "type": "...", "issue": "...", "blocking": true | false }`. At merge it is
filled for a facet that did not run, crashed, or returned a finding it could not
settle — every such item is `blocking: true`.

A facet leaves `unresolved` empty with one exception: an input the hub did not
supply, so part of its criterion could not be exercised. It then appends exactly
one item with `blocking: false`, naming the missing input. That is a coverage
note, not a defect. A facet never marks its own item blocking and never invents
another.

A facet that cannot settle a *finding* says so on the finding, not in
`unresolved`: it files it with `fix_hint: "needs-human"`, which is both the marker
§ Verdict Precedence reads and the pointer the merge follows. The finding is named
in `unresolved` once, at merge.

The envelope shape is owned here, and this section wins on any conflict with a
facet file. A facet file links here rather than restating the shape, and states
only which key it populates and what its `totals` counts.

Envelope rules owned here — a facet may reference, never redefine them: every key
is always present; `folder` is the section folder the **target path** belongs to,
or `"N/A"` when no row in `./AGENTS.md` § Repository Structure (PKM content) owns
that path — the path decides both the value and which section file is loaded, and
a hub-supplied `folder` that disagrees with it is ignored, not reported as a
finding; no field is ever `null` (emit an empty list or empty string); `fix_hint`
is a § Fix Hints value, read verbatim; and `verdict` is one of `clean`, `issues`,
`needs_recheck`. Each facet computes its own report's `verdict` per § Verdict
Precedence — a finding it could not settle is filed `needs-human` and makes that
verdict `needs_recheck`. The merged report's verdict is computed the same way, and
`unresolved` is filled at merge — see `./.opencode/WORKFLOW.md` § Coordination
Rule for who merges and § Flow D for the ordering.

`06_Archive` targets are out of review: an archive record is preserved verbatim and
purged after 31 days (`./06_Archive/AGENTS.md` § Conventions), so no facet files a
finding against it, and an archive copy is never canonical for `overlap`.

## Merged Report

The facets are merged for one target into the same envelope — the shape `editor`
consumes; who merges is defined in `./.opencode/WORKFLOW.md` § Coordination Rule.
The merge is mechanical:

1. Concatenate each facet's findings into its own `types` key.
2. Recompute `totals` across the merged findings.
3. Keep at most 5 findings per type after the merge, the `needs-human` ones first —
   never dropping one to make room for a confirmed finding.
4. Fill `unresolved` from every facet named by the trigger list in § Facet Report,
   then add one blocking item per `needs-human` finding, naming its type and
   `issue`.

## Verdict Precedence

Deterministic: the same input always produces the same verdict. Who computes the
merged verdict, and when, is defined in `./.opencode/WORKFLOW.md` § Coordination
Rule for the actor and § Flow D for the ordering — not restated here. Consumers —
`editor`, `loop-validation`, any skill — read the verdict and never paraphrase or
recompute it.

```
any blocking unresolved      → needs_recheck  (logged in "unresolved" at merge)
else any needs-human finding → needs_recheck
else any finding at all      → issues
else                         → clean
```

`needs_recheck` outranks `issues`: an unresolved finding always reaches the human,
even when a definite S1 or S2 is also present. The S1–S2 findings still block, and
the editor still applies every confirmed finding — the precedence only decides what
`runesmith` escalates.

A non-empty *blocking* `unresolved` — filled per the trigger list in § Facet
Report — makes the merge `needs_recheck`, never a silent drop. A non-blocking item
reaches the human as coverage information and changes no verdict.

## Routing

`REVIEW.md` owns which consumer receives which report. A cell naming one facet
means the hub launches that facet for the consumer, with no merge; a cell naming
the merged report means the consumer receives the merge described above.

| consumer | gets |
|---|---|
| `editor` | the merged report, one per target |
| `spec-writer` | the merged report, one per `./05_Implementations/**/spec-*.md` target |
| `loop-validation` | the merged report, posted before the editor runs |
| `research` | a hub-launched `reviewer-source` report on the written or planned file's citations; no merge needed — research's own per-file verified list (`./.opencode/skills/research/SKILL.md` § Report) rides alongside it |
| `dry-audit` | a hub-launched `reviewer-overlap` report per file |

A target under `./05_Implementations/**/spec-*.md` goes to `spec-writer`, never to
`editor`: those files are append-only, so the consumer's answer is a replacement block
(`./.opencode/agents/spec-writer.md` § Append-Only and Diagrams), and `editor` refuses
the path outright (`./.opencode/agents/editor.md` § Role).

`knowledge-gap` takes no report. It asks whether a note exists at all, and a file
that does not exist has no target for a facet to review — see
`./.opencode/skills/knowledge-gap/SKILL.md` § INSPECT.

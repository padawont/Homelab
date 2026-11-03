# Review contract — five facets, one merged report

How the Homelab PKM review works after the single `reviewer` was split into five
single-type subagents. Owns the facet map, the merged report shape, the merge
rule and the verdict precedence — the facts `runesmith`, `editor` and the skills
all depend on. Each facet's own rules live in its agent file.

`runesmith` is the only agent that fans out and the only one that merges: a
facet never calls another facet.

## The Five Facets

| type | agent | question it answers | band |
|---|---|---|---|
| `source` | `reviewer-source` | Is every cited URL live, authoritative, and does it actually say what's claimed? | S1–S2 |
| `accuracy` | `reviewer-accuracy` | Are commands, keys, defaults, ports and versions correct for *this* homelab? | S1–S2 |
| `scope` | `reviewer-scope` | Homelab-relevant, correct folder, right depth, no history/marketing? | S3 |
| `structure` | `reviewer-structure` | Frontmatter, status, kebab-case tags, ISO dates, 150-line rule, `./` links, heading order | S3–S5 |
| `overlap` | `reviewer-overlap` | Duplicates or contradicts another note/ADR — link instead of repeat? | S4–S5 |

## Severity Bands

- **S1** — factually wrong / dead source.
- **S2** — materially misleading; sends the reader down the wrong path.
- **S3** — placement or depth problem; also structure changing what the reader concludes.
- **S4** — pure convention breach, or duplication.
- **S5** — cosmetic or stylistic; never blocks.

The full band definitions are in each facet. S1–S2 block, S3–S4 are auto-fixed,
S5 is applied freely.

## Facet Report

Every facet returns the same envelope, with only its own key populated:

```json
{
  "file": "./02_Knowledge/technologies/kubernetes/concepts/ingress.md",
  "folder": "02_Knowledge",
  "types": { "source": [], "accuracy": [], "scope": [], "structure": [], "overlap": [] },
  "totals": { "S1": 0, "S2": 0, "S3": 0, "S4": 0, "S5": 0 },
  "verdict": "clean | issues | needs_recheck"
}
```

A finding carries `severity`, `issue`, `evidence`, `fix_hint`. At most 5 findings
per facet, ordered by file path then line number.

The envelope shape is owned here. A facet file links to this section rather than
restating it, and states only which key it populates and what its `totals` counts.

## Merged Report

`runesmith` merges the facets for one target into the same envelope — the shape
`editor` consumes. The merge is mechanical:

1. Concatenate each facet's findings into its own `types` key.
2. Recompute `totals` across the merged findings.
3. Keep at most 5 findings per type after the merge.

## Verdict Precedence

Deterministic, so the same input always produces the same verdict:

```
any needs_recheck          → needs_recheck  (+ "unresolved": [{ "type": "...", "issue": "..." }])
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

| consumer | gets |
|---|---|
| `editor` | the merged report, one per target |
| `loop-validation` | the merged report, posted before the editor runs |
| `research` | `reviewer-source` directly; no merge needed |
| `dry-audit` | `reviewer-overlap` per file directly |
| `knowledge-gap` | `reviewer-scope` directly |

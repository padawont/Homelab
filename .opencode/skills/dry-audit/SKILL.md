---
name: dry-audit
description: >
  Simplest DRY check for Homelab PKM content: normalise the body of every file
  in scope, launch one read-only agent per file to cross-reference it against
  the rest, then report every repeated factual unit in a single standard
  repetition record (diagrams, facts, config, prose, tables, procedures,
  frontmatter). Read-only; confirmed fixes are handed to pkm-editor.
---

# dry-audit

## When to use

- A user asks whether content is duplicated / DRY-compliant.
- A file, a folder, or the whole repo needs a repetition check.
- After `research-implement` writes files, before `loop-validation`.

## When NOT to use

- Creating content from scratch (capture pipeline / `research-implement`).
- Non-PKM content (application code, infra configs) — PKM only.

## Pipeline

```
1. NORMALISE  (main agent, deterministic)    file body -> digest
2. FAN OUT    (one read-only agent per file)  cross-reference vs the scope
3. AGGREGATE  (main agent)                    merge clusters, pick canonical
4. REPORT     (standard repetition record)    read-only
```

### 1 · Normalise (main agent)

For every file in scope, build a **digest**:

1. Separate and drop YAML frontmatter; body = the rest.
2. Strip HTML comments; collapse runs of blank lines.
3. Split the body into **segments**: prose paragraph, fenced block (with
   language), table, or list/step group.
4. `normalised_text` per segment: lowercase, collapse whitespace, trim edge
   punctuation, drop template placeholders (`""`, `[]`, `YYYY-MM-DD`, `0`).
5. `hash` = digest of `normalised_text`; keep `file:line` for each segment.
6. Collect **fact tokens** into a set: IPv4, FQDN / `*.local`, `v?\d+\.\d+\.\d+`,
   port, node/host name, `./` path.

Digest shape: `{file, segments:[{kind, hash, normalised_text, line}], facts[]}`.

### 2 · Fan out (one agent per file)

- Launch one **read-only** `pkm-overview` subagent per file, all in parallel
  (batch into waves of ≤20 for large scopes). Its frontmatter sets
  `edit: deny` and `webfetch: deny`, so read-only is permission-enforced.
- Each agent receives its file's digest plus the list of all other files it
  must cross-reference.
- Task prompt scope: cross-reference only, return standard `repetition`
  records; section/homelab-fit review is OUT OF SCOPE.
- It returns only standard `repetition` records — no prose, no edits.

### 3 · Aggregate (main agent)

- Merge records sharing a `match` or `hash` into one cluster (`REP-###`).
- Pick the **canonical** copy:
  1. lowest pipeline stage wins for facts/concepts —
     `02_Knowledge/` < `03_Research/` < `04_ADRs/` < `05_Implementations/`;
  2. `05_Implementations/` owns live/runtime values;
  3. earliest `date` / `last_audit_date` breaks ties;
  4. `06_Archive/` is never canonical.
- Apply **exemptions** (never flag): template placeholders; archive copies;
  pairs labelled `Example — abstract` / `Example — real config`; provenance
  `sources`/`references` URLs reused in ≤3 notes; a lone identifier in a table
  with no surrounding prose; restatement ≤1 sentence that is clearly derivative.
- Assign severity: `S2` live config/version/IP (drift causes a bad deploy),
  `S3` fact/procedure, `S4` diagram/prose, `S5` cosmetic.

### 4 · Report (standard record, read-only)

Emit every cluster in this format — the same record everywhere:

```yaml
repetition:
  id: REP-001
  type: fact | diagram | config | prose | table | procedure | frontmatter
  severity: S2 | S3 | S4 | S5
  canonical: "path/to/canonical.md:42"
  repeated_in:
    - "./path/to/duplicate.md:87"
  match: "normalised shared value"
  recommendation: link-instead | extract | merge | keep | needs-human
  agent: "file:./path/to/source.md"
```

Then the table view:

| id | type | sev | canonical | repeated in | recommendation |
|---|---|---|---|---|---|

## Hand-off

- Confirmed `link-instead` / `extract` fixes go to `pkm-editor`, citing the
  canonical path as the source. Never edit directly.
- Ambiguous canonical or intentional repetition → `needs-human`.

## Guardrails

- **Read-only** — never delete or rewrite content; fixes go via `pkm-editor`.
- **No false alarm** — pipeline restatement is not duplication; require a
  normalised verbatim match.
- **No guessing** — canonical unclear → `needs-human`.
- **No fabrication** — report only what is on disk; no webfetch.
- **PKM only** — skip non-PKM paths.

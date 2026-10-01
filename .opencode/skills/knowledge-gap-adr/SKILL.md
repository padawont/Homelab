---
name: knowledge-gap-adr
description: >
  Knowledge-layer audit for the ADR stage. Runs ONLY while working on a
  service/process whose ADR is being written or reviewed, when the Knowledge
  backing the decision is missing or too thin. Scans for decisions and
  integration points cited only to online sources, inspects the matching
  02_Knowledge folders, and reports each gap as a standardized, issue-ready
  entry (epic or single issue). Read-only on notes.
---

# knowledge-gap-adr

Phase wrapper over the `knowledge-gap` core for the ADR stage. Owns the
online-only claim scan; locating, inspecting, reporting, and filing come from
the core.

## When to use

- You are writing or reviewing an ADR for a service/process that will be
  created, changed, or operated, and the decision rests on facts sourced
  online because Knowledge coverage is missing or too thin.

## When NOT to use

- Auditing an ADR's Knowledge coverage for its own sake.
- Writing or fixing Knowledge notes (capture pipeline / `implement`).
- Re-evaluating alternatives — that belongs in Research.
- Validating the ADR itself (`loop-validation`).

## Inputs

- `04_ADRs/{issue}-{kebab}.md`.
- Confirmation of which gaps to file, the issue kind, and the parent epic.

## Scan rules (adr-specific)

1. Walk `sources[].url` — an ADR `sources` entry is an online citation by
   definition. Record the concept each supports.
2. For every "Decision" claim (install method, namespace, TLS issuer, CRDs,
   API surface), check whether it cites a `./02_Knowledge/...` path in
   `related_docs`; if it rests on a URL only, it is a candidate.
3. For every "Fit into Homelab" dependency and integration point (node,
   namespace, cert-manager, storage class, hosts pattern), do the same.
4. Candidates pass to the core pipeline (LOCATE → INSPECT → REPORT).

## Hand-off

- A gap here is a **pre-commit blocker**: an ADR must not go `accepted` while
  committing to a technology with no usable Knowledge note.

## Guardrails

- Read-only on notes.
- Scan only for this phase; no research / implementation logic.
- Load the `knowledge-gap` core for all shared behaviour.
- Never file an issue before confirmation.

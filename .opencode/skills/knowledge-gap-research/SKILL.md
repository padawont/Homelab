---
name: knowledge-gap-research
description: >
  Knowledge-layer audit for the Research stage. Runs ONLY while working on a
  research topic for a service/process, when the Knowledge needed to build,
  change, or operate it is missing or too thin. Scans for claims cited only to
  online sources, inspects the matching 02_Knowledge folders, and reports each
  gap as a standardized, issue-ready entry (epic or single issue). Read-only
  on notes.
---

# knowledge-gap-research

Phase wrapper over the `knowledge-gap` core for the Research stage. Owns the
online-only claim scan; locating, inspecting, reporting, and filing come from
the core.

## When to use

- You are working a research topic for a service/process that will be built,
  changed, or operated, and the topic had to source facts online because
  Knowledge coverage is missing or too thin.

## When NOT to use

- Auditing a research topic's Knowledge coverage for its own sake.
- Writing or fixing Knowledge notes (capture pipeline / `implement`).
- Source pinning — that is `research`.
- Idea/S1 stages (no external sources).

## Inputs

- `03_Research/{topic}/overview.md`, `alternatives.md`,
  `alternative-{name}.md`.
- Confirmation of which gaps to file, the issue kind, and the parent epic.

## Scan rules (research-specific)

For the topic artifact, list every claim edited toward an online source:

1. Walk `references[].url` and any inline `https://` citation in the body.
2. For each, record the subject concept it supports.
3. Drop it if the same claim is also backed by a `sources.knowledge` path, or
   the concept has a Knowledge note in `related_docs`.
4. Everything left is a candidate — pass it to the core pipeline
   (LOCATE → INSPECT → REPORT).

## Hand-off

- Report gaps to the main chat; confirm and file per the core.
- Load `research` separately — neither skill blocks the other.

## Guardrails

- Read-only on notes.
- Scan only for this phase; no adr / implementation logic.
- Load the `knowledge-gap` core for all shared behaviour.
- Never file an issue before confirmation.

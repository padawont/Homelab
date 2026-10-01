---
name: knowledge-gap-implementation
description: >
  Knowledge-layer audit for the Implementation stage. Runs ONLY while fixing,
  maintaining, or creating a live service/process, when the Knowledge needed
  to do so is missing or too thin. Scans for steps and technologies cited only
  to online sources, inspects the matching 02_Knowledge folders, and reports
  each gap as a standardized, issue-ready entry (epic or single issue).
  Read-only on notes.
---

# knowledge-gap-implementation

Phase wrapper over the `knowledge-gap` core for the Implementation stage.
Owns the online-only claim scan; locating, inspecting, reporting, and filing
come from the core.

## When to use

- You are fixing, maintaining, or creating a service/process and the deploy,
  config, or ops steps depend on facts sourced online because Knowledge
  coverage is missing or too thin.

## When NOT to use

- Auditing an implementation's Knowledge coverage for its own sake.
- Writing or fixing Knowledge notes (capture pipeline / `implement`).
- Validating the implementation itself (`loop-validation`).
- Pre-deployment decisions — those belong in the ADR.

## Inputs

- `05_Implementations/{node}/{service}/overview.md`, `rollback.md`, `configs/`.
- Confirmation of which gaps to file, the issue kind, and the parent epic.

## Scan rules (implementation-specific)

1. Walk `references.online[].url` and any inline `https://` citation in
   Prerequisites, Deployment, Configuration, and Operations.
2. For each, record the concept the step depends on (tool, command, port,
   volume, secret, dependency).
3. Check `technologies[]` and `related_docs` for a `./02_Knowledge/...` backing;
   a step resting on a URL only is a candidate.
4. Repeat for `rollback.md` — teardown steps need the same backing as deploy.
5. Candidates pass to the core pipeline (LOCATE → INSPECT → REPORT).

## Hand-off

- A `no-hosting-info` gap here is severe: the implementation is about to run
  commands against a note that never says how the thing is hosted.

## Guardrails

- Read-only on notes.
- Scan only for this phase; no research / adr logic.
- Load the `knowledge-gap` core for all shared behaviour.
- Never file an issue before confirmation.

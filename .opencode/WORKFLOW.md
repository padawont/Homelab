---
title: "Workflow — hub-and-spoke agent model"
status: accepted
author: "padawont"
date: 2026-11-03
tags: []
sources: []
last_audit_date: 2026-11-03
related_docs: []
---

# Workflow — hub-and-spoke agent model

How the roster agents compose. Defines the topology, the two flows, the
handoff contract, and how a run ends. It describes the interaction model the
skills and `runesmith` execute — not the agents themselves (see
`./.opencode/agents/`).

## Coordination Rule

**No spoke spawns another spoke.** Only `runesmith` holds `subagent: allow`; every
handoff goes through it, and it is the only agent that speaks to the human.
Two lanes run under it: the PKM pipeline (the spokes `worker`, `editor`,
`cluster-worker`, `spec-writer`, plus the five reviewer facets) and the code
pipeline (the `rs-*` specialists).

Fan-out and merge are `runesmith`-only, and this section is their canonical home:
no facet, worker, editor, `spec-writer` or `cluster-worker` launches another
agent's facet set or merges facet reports. Other files link to § Coordination
Rule for that rule rather than restating it; the facet roster itself is owned by
`./.opencode/REVIEW.md` (§ The Five Facets).

## Topology

```
                            +----------+
                            |  worker  |
                            +-----+----+
                                  |
     +-----------+                |                +----------+
     | reviewer-*+----------------+----------------+  editor  |
     +-----------+                |                +----------+
                                  |
                          +-------+---------+
                          |    runesmith    |
                          |    (primary)    |
                          +-------+---------+
                                  |
     +-------------+              |              +-------------+
     | spec-writer +--------------+--------------+ cluster-    |
     +-------------+              |              |  worker     |
                                  |              +-------------+
                                  |
                                  v
                             [  HUMAN  ]
```

Every arrow is `runesmith -> spoke -> runesmith`. No `spoke -> spoke` arrow exists anywhere:
a lane never calls its own reviewer, an editor is never launched by a reviewer,
and a `cluster-worker` never launches its successor. `[ HUMAN ]` hangs off
`runesmith` only: a `cluster-worker` that needs a decision escalates upward.

## Flow D — Parallel Batch (canonical)

```
                              runesmith
                                  |
        +---------+---------+-----+-----+---------+---------+
        v         v         v           v         v
     worker    worker    worker      worker    worker        one lane per document
      #1        #2        #3          #4        #5
        |         |         |           |         |
        v         v         v           v         v
  reviewer-* reviewer-* reviewer-* reviewer-* reviewer-*   one facet set per
        |         |         |           |         |
        +---------+---------+-----+-----+---------+---------+
                                  |
                                  v
                              runesmith <- merge facets; footprint check: git diff --name-only
                                  |
        +---------+---------+-----+-----+---------+---------+
        v         v         v           v         v
      editor    editor    editor      editor    editor
                                  |
                                  v
                              runesmith --> report
```

Each lane is isolated — one document, one worker, five reviewer facets, one
merged report, one editor. Lanes do not wait for each other; the only barrier is
the `overlap` comparison, which `runesmith` supplies as sibling drafts. `N = 1` is
a single-document review.
Each column boundary is a handoff through `runesmith` — the vertical arrows show
data flow, not agent-to-agent calls.

Flow D and Flow B are the only canonical flows — the labels stay because external
documents reference them; no Flow A or Flow C is documented.

## Flow B — Operational Chain

```
   runesmith  --JSON: steps 1-6----> cluster-worker #1
   runesmith  <--handoff payload----  cluster-worker #1
   runesmith  --JSON: steps 7-12---> cluster-worker #2
        ... strictly sequential; stop on refused or failed
```

`runesmith` chains workers one handoff payload at a time. Each `cluster-worker`
finishes its step range and returns `next_worker_input`; `runesmith` launches the
next one. No worker ever spawns its successor.

## Handoff Contract

Every spoke owns its own return schema; nothing is restated here.

| Spoke | Contract | Owner |
|---|---|---|
| `worker` | `handoff:` block (`done` / `next` / `blocked`) | `./.opencode/agents/worker.md` |
| `reviewer-*` | one-type envelope — the facet populates its own key; the shape is owned by `./.opencode/REVIEW.md` | `./.opencode/agents/reviewer-{source,accuracy,scope,structure,overlap}.md` |
| merged review report | five always-present type keys | `./.opencode/REVIEW.md` |
| `editor` | `changes:` report | `./.opencode/agents/editor.md` |
| `spec-writer` | spec report | `./.opencode/agents/spec-writer.md` |
| `cluster-worker` | plan JSON in, handoff / refusal JSON out | `./.opencode/agents/cluster-worker.md` |

## Termination

| Condition | Action |
|---|---|
| 10 rounds reached | Stop, report what's still open |
| 7 consecutive clean rounds | Ask the human: keep / stop all / just this file |
| A lane blocked | Other lanes continue; batch reports partial |
| `cluster-worker` step refused | Stop the chain, report the refusal payload — `state_after` present but empty: `applied`, `skipped_already_applied` and `not_run` are empty lists and `observed` says nothing executed |
| `cluster-worker` step failed | Stop the chain, report `state_after` |

## Escalation

No spoke asks the human. A spoke that needs a decision returns it in its own
report (`blocked:`, `questions:`, or `status: "refused"` with
`escalate_to: "runesmith"`); `runesmith` puts the question to the human and
relaunches. This section is canonical for the rule: the per-section Agent
Behaviour rows (`./02_Knowledge/AGENTS.md`, `./04_ADRs/AGENTS.md` § Agent
Behaviour) link here rather than define the channel themselves, and the same
applies to any other file that still restates it.

## Ownership Matrix

| From | To | Trigger |
|---|---|---|
| `runesmith` | `worker` | a new text brief |
| `worker` | `runesmith` | work done + handoff |
| `runesmith` | `reviewer-<type>` | a type to judge for a document (+ siblings for `overlap`) |
| `reviewer-<type>` | `runesmith` | one-type envelope |
| `runesmith` | `editor` | confirmed findings from the JSON |
| `editor` | `runesmith` | change report (`source_or_rule` when it was cited) |
| `runesmith` | `cluster-worker` | a committed plan under `./05_Implementations/` |
| `cluster-worker` | `runesmith` | JSON handoff or refusal |
| `runesmith` | `spec-writer` | a spec or diagram request |
| `spec-writer` | `runesmith` | spec report / diagram appended |

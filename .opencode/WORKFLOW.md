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
        +---------+---------+-----------+---------+
        v         v         v           v         v
     worker    worker    worker      worker    worker        one lane per document
      #1        #2        #3          #4        #5
        |         |         |           |         |
        v         v         v           v         v
  reviewer-* reviewer-* reviewer-* reviewer-* reviewer-*     one facet set per lane
        |         |         |           |         |
        +---------+---------+-----------+---------+
                            |
                            v
                        runesmith <- merge facets; footprint check: git diff --name-only
                            |
        +---------+---------+-----------+---------+
        v         v         v           v         v
      editor    editor    editor      editor    editor
        |         |         |           |         |
        +---------+---------+-----------+---------+
                            |
                            v
                        runesmith --> report
```

Each lane is isolated — one document, one worker, five reviewer facets, one
merged report, one editor. Lanes do not wait for each other; the only barrier is
the `overlap` comparison, which `runesmith` supplies as sibling drafts — or, for a
`dry-audit` run, as the explicit cross-reference list. `N = 1` is a single-document
review.
Each column boundary is a handoff through `runesmith` — the vertical arrows show
data flow, not agent-to-agent calls.

Flow D and Flow B are the only canonical flows — the labels stay because external
documents reference them; no Flow A or Flow C is documented.

## Flow B — Operational Chain

```
   runesmith  --plan JSON: step_range 1-6--> cluster-worker #1
   runesmith  <--handoff payload------------  cluster-worker #1
   runesmith  --plan JSON: step_range 7-12-> cluster-worker #2
        ... strictly sequential; stop on refused or failed
```

`runesmith` chains workers one handoff payload at a time. Every `cluster-worker` run
ends in exactly one of three payloads, discriminated by `status`
(`./.opencode/agents/cluster-worker.md` § Output Contract): `completed` carries
`chain_complete` and `next_worker_input`; `refused` and `failed` carry neither, because
neither can be chained. `next_worker_input` is
`{ plan_id, step_section, step_range }`; on `chain_complete: true` it is `{}`.
`runesmith` launches the next worker only on a `completed` payload whose
`chain_complete` is `false`, passing that `next_worker_input` as the launch input.
When `chain_complete` is `true` the slice ended the plan and no further worker is
launched. A `refused` or `failed`
payload always stops the chain. No worker ever spawns its successor.

## Handoff Contract

Every spoke owns its own return schema; nothing is restated here.

| Spoke | Contract | Owner |
|---|---|---|
| `worker` | `handoff:` block (`done` / `next` / `blocked`) | `./.opencode/agents/worker.md` |
| `reviewer-*` | `./.opencode/agents/reviewer-*.md` (the one key each populates); envelope shape per `./.opencode/REVIEW.md` § Facet Report | `./.opencode/agents/reviewer-*.md` for the facet rules; `./.opencode/REVIEW.md` § Facet Report for the shape |
| merged review report | `./.opencode/REVIEW.md` § Merged Report | `./.opencode/REVIEW.md` |
| `editor` | `changes:` report | `./.opencode/agents/editor.md` |
| `spec-writer` | spec report | `./.opencode/agents/spec-writer.md` |
| `cluster-worker` | plan JSON in; `completed` / `refused` / `failed` JSON out | `./.opencode/agents/cluster-worker.md` (§ Output Contract, § Refusal, § Failed) |

## Termination

| Condition | Action |
|---|---|
| 10 rounds reached | Stop, report what's still open |
| 7 consecutive clean rounds | Ask the human: keep / stop all / just this file |
| A lane blocked | Other lanes continue; batch reports partial |
| `cluster-worker` `status: "refused"` | Stop the chain; report the refusal payload — shape owned by `./.opencode/agents/cluster-worker.md` § Refusal. No step inside `step_range` was dispatched. |
| `cluster-worker` `status: "failed"` | Stop the chain; report the failed payload — shape owned by § Failed of the same file. Part of the slice ran; `state_after` is the report, and no worker resumes automatically. |
| `status: "completed"` + `chain_complete: true` | Chain ends successfully — no next worker is launched; report the final `state_after` |
| `status: "completed"` + `chain_complete: false` | Launch the next worker with `next_worker_input` |

## Escalation

No spoke asks the human. A spoke that needs a decision returns it in its own
report — the decision channels are:

- **PKM lane** — `blocked:`, `questions:`, `status: "refused"`, or a
  `verdict: needs_recheck` report, with `escalate_to: "runesmith"` where the contract
  carries it. `needs_recheck` is the review lane's channel: a facet or merged verdict of
  `needs_recheck` names a finding nothing on hand settles, and it reaches the human even
  when confirmed S1–S2 findings are present (`./.opencode/REVIEW.md` § Verdict
  Precedence). The editor's `questions:` and the worker's `blocked:` are this channel
  under their own contracts' names, not alternatives to it.
- **rs-* lane** — a `needs_input` payload: `recipient: runesmith`, `source`
  (the specialist to relaunch), and `questions[]` carrying `id`, `question`,
  `context`, and `blocking`; emitted per `./.opencode/skills/rs-ask-human/SKILL.md`,
  relayed per `./.opencode/skills/rs-human-responds/SKILL.md`.

`runesmith` puts the question to the human and relaunches. This section is
canonical for the rule: the per-section Agent Behaviour rows
(`./02_Knowledge/AGENTS.md`, `./04_ADRs/AGENTS.md` § Agent Behaviour) link here
rather than define the channel themselves, and the same applies to any other
file that still restates it.

## Ownership Matrix

| From | To | Trigger |
|---|---|---|
| `runesmith` | `worker` | a new text brief |
| `worker` | `runesmith` | work done + handoff, including any briefed deletion it refused |
| `runesmith` | `reviewer-<type>` | a type to judge for a document (+ siblings, or the dry-audit cross-reference list, for `overlap`) |
| `reviewer-<type>` | `runesmith` | one-type envelope |
| `runesmith` | `editor` | confirmed findings from the merged report |
| `runesmith` | `editor` | hub-named corrections with no review behind them — a typo, a broken link, a stale path, a value to change |
| `runesmith` | `editor` | a briefed deletion: the source path a worker reported as an archive-move deletion, or any path a brief names for removal |
| `editor` | `runesmith` | change report |
| `runesmith` | `cluster-worker` | a committed plan under `./05_Implementations/` — **Mode B only**: verify, rollback, restart |
| `cluster-worker` | `runesmith` | `completed`, `refused` or `failed` JSON payload |
| `runesmith` | `spec-writer` | a spec or diagram request |
| `runesmith` | `spec-writer` | a confirmed finding on an existing `spec-*.md`, re-issued as a replacement-block request |
| `spec-writer` | `runesmith` | spec report / diagram appended |

Notes — normative, and owned here because each one is a routing consequence of the
table rather than a property of any single spoke:

- **Create vs change.** The human runs the committed plan's create/mutate verbs —
  `kubectl apply`, `helm install`, `helm upgrade` — per `./.opencode/skills/deploy-service/SKILL.md`
  § Guardrails (non-negotiable), Mode A; `runesmith` does not hold them.
  `cluster-worker` runs Mode B only,
  the whitelist in `./.opencode/agents/cluster-worker.md` § Command Whitelist. The matrix
  is where this split is stated.
- **Deletion has exactly one executor: `editor`.** `worker` never deletes
  (`./.opencode/agents/worker.md` § Negative Constraints), `runesmith` never deletes,
  `spec-writer` never deletes. A deletion reaches `editor` only as an explicit path in
  its brief, under `./01*`–`./05*` and outside `./06_Archive/`
  (`./.opencode/agents/editor.md` § Negative Constraints).
- **Spec findings skip `editor`.** `editor` refuses `./05_Implementations/**/spec-*.md`
  (`./.opencode/agents/editor.md` § Role); the replacement-block row above is the route.
- **Status line.** `runesmith` decides the value; `spec-writer` is the only agent that
  writes the `status:` frontmatter line of a `./05_Implementations/**/spec-*.md`, on that
  directive. The body is `spec-writer`'s append-only replacement blocks
  (`./05_Implementations/AGENTS.md` § Spec files).
- **`source_or_rule`.** Required on every `changes` entry whose trigger is a review
  report; a hub-named correction carries `"hub brief"`. `./.opencode/agents/editor.md`
  § Output Contract links here for this rule rather than restating the trigger.

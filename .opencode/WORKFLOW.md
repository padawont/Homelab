# Workflow — hub-and-spoke agent model

How the five roster agents compose. Defines the topology, the two flows, the
handoff contract, and how a run ends. It describes the interaction model the
skills and `runesmith` execute — not the agents themselves (see
`./.opencode/agents/`).

## Coordination Rule

**No agent spawns another agent.** Every handoff goes through the hub, which is
the only agent that chooses the next step and the only agent (besides
`cluster-worker`) that speaks to the human. The hub is `runesmith`; the spokes
are `worker`, `reviewer`, `editor`, `cluster-worker`, and `spec-writer`.

## Topology

```
                            +----------+
                            |  worker  |
                            +-----+----+
                                  |
     +-----------+                |                +----------+
     | reviewer  +----------------+----------------+  editor  |
     +-----------+                |                +----------+
                                  |
                          +-------+---------+
                          |   ORCHESTRATOR  |   <== HUB
                          |    (primary)    |
                          +-------+---------+
                                  |
     +-------------+              |              +-------------+
     | spec-writer +--------------+--------------+ cluster-    |
     +-------------+                             |  worker     |
                                                 +------+------+
                                                        |
                                                        v
                                                   [  HUMAN  ]
```

Every arrow is `HUB -> spoke -> HUB`. No `spoke -> spoke` arrow exists anywhere:
a lane never calls its own reviewer, an editor is never launched by a reviewer,
and a `cluster-worker` never launches its successor.

## Flow D — Parallel Batch (canonical)

```
                                 HUB
                                  |
        +---------+---------+-----+-----+---------+---------+
        v         v         v           v         v
     worker    worker    worker      worker    worker        one lane per document
      #1        #2        #3          #4        #5
        |         |         |           |         |
        v         v         v           v         v
    reviewer  reviewer  reviewer    reviewer  reviewer       JSON report, pipelined
        |         |         |           |         |
        +---------+---------+-----+-----+---------+---------+
                                  |
                                  v
                                HUB     <- footprint check: git diff --name-only
                                  |
        +---------+---------+-----+-----+---------+---------+
        v         v         v           v         v
      editor    editor    editor      editor    editor
                                  |
                                  v
                                HUB --> report
```

Each lane is isolated — one document, one worker, one reviewer, one editor.
Lanes do not wait for each other; the only barrier is the `overlap` comparison,
which the hub supplies as sibling drafts. `N = 1` is a single-document review.

## Flow B — Operational Chain

```
   HUB  --JSON: steps 1-6----> cluster-worker #1
   HUB  <--handoff payload----  cluster-worker #1
   HUB  --JSON: steps 7-12---> cluster-worker #2
        ... strictly sequential; stop on refused or failed
```

The hub chains workers one handoff payload at a time. Each `cluster-worker`
finishes its step range and returns `next_worker_input`; the hub launches the
next one. No worker ever spawns its successor.

## Handoff Contract

`worker` ends every report with a `handoff:` block:

```
handoff:
  done:    what this agent finished
  next:    what should happen next
  blocked: anything unresolved
```

`editor` returns its own `changes:` shape (see `./.opencode/agents/editor.md`);
`spec-writer` returns its own `spec_type:` shape (see
`./.opencode/agents/spec-writer.md`).

`reviewer` returns one JSON report instead — five always-present type keys
(`source`, `accuracy`, `scope`, `structure`, `overlap`); see
`./.opencode/agents/reviewer.md`. `cluster-worker` takes JSON in:

```
{ "plan_id": "...", "plan_source": "...", "steps": ["..."],
  "step_range": "1-6", "dry_run": true }
```

and returns JSON out:

```
{ "plan_id": "...", "step_range": "1-6", "state_after": "...",
  "next_worker_input": { "plan_id": "...", "step_range": "7-12", "steps": ["..."] } }
```

Full schemas: `./.opencode/agents/reviewer.md` and
`./.opencode/agents/cluster-worker.md`.

## Termination

| Condition | Action |
|---|---|
| 10 rounds reached | Stop, report what's still open |
| 7 consecutive clean rounds | Ask the human: keep / stop all / just this file |
| A lane blocked | Other lanes continue; batch reports partial |
| `cluster-worker` step refused or failed | Stop the chain, report `state_after` |

## Direct-Question Exception

`cluster-worker` is the only agent that may call the `question` tool directly —
an ambiguous step, an unexpected dry-run, or a decision the plan does not cover.
Every other agent routes questions through the hub (`question: deny`).

## Ownership Matrix

| From | To | Trigger |
|---|---|---|
| HUB | `worker` | a new text brief |
| `worker` | HUB | work done + handoff |
| HUB | `reviewer` | a document to review (+ siblings for `overlap`) |
| `reviewer` | HUB | JSON report |
| HUB | `editor` | confirmed findings from the JSON |
| `editor` | HUB | change report, each change cited |
| HUB | `cluster-worker` | a committed plan under `05_Implementations/` |
| `cluster-worker` | HUB | JSON handoff / refusal / failure |
| HUB | `spec-writer` | a spec or diagram request |
| `spec-writer` | HUB | spec report / diagram appended |

# Workflow — hub-and-spoke agent model

How the five roster agents compose. Defines the topology, the two flows, the
handoff contract, and how a run ends. It describes the interaction model the
skills and `runesmith` execute — not the agents themselves (see
`./.opencode/agents/`).

## Coordination Rule

**No agent spawns another agent.** Every handoff goes through `runesmith`, which
is the only agent that chooses the next step and the only agent (besides
`cluster-worker`) that speaks to the human. The spokes are `worker`, `reviewer`,
`editor`, `cluster-worker`, and `spec-writer`.

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
                          |    runesmith    |
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

Every arrow is `runesmith -> spoke -> runesmith`. No `spoke -> spoke` arrow exists anywhere:
a lane never calls its own reviewer, an editor is never launched by a reviewer,
and a `cluster-worker` never launches its successor.

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
    reviewer  reviewer  reviewer    reviewer  reviewer       JSON report, pipelined
        |         |         |           |         |
        +---------+---------+-----+-----+---------+---------+
                                  |
                                  v
                              runesmith <- footprint check: git diff --name-only
                                  |
        +---------+---------+-----+-----+---------+---------+
        v         v         v           v         v
      editor    editor    editor      editor    editor
                                  |
                                  v
                              runesmith --> report
```

Each lane is isolated — one document, one worker, one reviewer, one editor.
Lanes do not wait for each other; the only barrier is the `overlap` comparison,
which `runesmith` supplies as sibling drafts. `N = 1` is a single-document review.

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
Every other agent routes questions through `runesmith` (`question: deny`).

## Ownership Matrix

| From | To | Trigger |
|---|---|---|
| `runesmith` | `worker` | a new text brief |
| `worker` | `runesmith` | work done + handoff |
| `runesmith` | `reviewer` | a document to review (+ siblings for `overlap`) |
| `reviewer` | `runesmith` | JSON report |
| `runesmith` | `editor` | confirmed findings from the JSON |
| `editor` | `runesmith` | change report, each change cited |
| `runesmith` | `cluster-worker` | a committed plan under `05_Implementations/` |
| `cluster-worker` | `runesmith` | JSON handoff / refusal / failure |
| `runesmith` | `spec-writer` | a spec or diagram request |
| `spec-writer` | `runesmith` | spec report / diagram appended |

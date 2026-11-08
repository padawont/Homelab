# Agent conformance tests

Recording harness and scoring layer for the Homelab PKM agent roster — epic #68,
issue #69. It runs a prompt against a roster agent through `opencode run`, stores the
response verbatim, and grades it with [Pydantic Evals](https://pydantic.dev/docs/ai/evals/),
so agent behaviour is **measured** rather than assumed from the prose in
`./.opencode/agents/`.

## Layout

```
tests/
  agents/
    catalog.json                  # index of every recorded run (ships empty)
    worker/test-{1,2,3}-*/response-NN.json   # #70 recordings
    worker/test-{1,2,3}-*/response-NN.txt    # the same run's prompt + response, readable
    reviewer/test-{1,2,3}-*/response-NN.json # #71 recordings
    reviewer/test-{1,2,3}-*/response-NN.txt  # the same run's prompt + response, readable
    editor/test-{1,2,3}-*/response-NN.json   # #72 recordings
    editor/test-{1,2,3}-*/response-NN.txt    # the same run's prompt + response, readable
  harness/
    workspace.py                  # throwaway clones: isolation + change footprint
    run_agent.py                  # one `opencode run`; NDJSON parsing; child env
    recording.py                  # one recorded run -> response file + catalog record
    catalog.py                    # the record schema and its index
    prompts.py                    # TestSpec: prompts and expectations as data
    evaluators.py                 # evaluator factories + the OTel tool-span bridge
    datasets.py                   # catalog -> Dataset -> report
    test_agents.py                # the live sweep and the scored report
    test_evaluators.py            # offline proof of the span bridge and the rules
    test_run_agent.py             # offline parser tests
    test_catalog.py               # catalog contract
    test_workspace.py             # isolation guarantee
  fixtures/events/*.jsonl         # captured CLI output for the offline parser tests
```

## Running it

| Command | What it does | Cost |
|---|---|---|
| `devbox run test` | Offline: parsers, catalog, span bridge, isolation. Skips anything marked `live`. | **free** |
| `devbox run eval` | The live sweep: `pytest --run-live`, 10 runs per test. | model calls |
| `devbox run eval-agent worker` | Narrows the live sweep to one agent. | model calls |
| `pytest -k test_evaluation_report` | Re-scores everything already recorded. No agent is invoked. | **free** |

A bare `pytest` can never spend money: `live`-marked tests are skipped unless
`--run-live` is passed. Useful flags: `--agent`, `--runs N` (default 10), `--model`,
`--workspace-root`, `--no-session-export`.

### The environment

`devbox.json` provides the toolchain (`uv`, `python3`) and `pyproject.toml` declares the
Python dependencies. **devbox needs Nix**, which is not installed on this machine yet:

```bash
sudo pacman -S nix          # nix is in cachyos-extra-v3
paru -S devbox              # devbox is AUR-only; there is no pacman package
devbox run test
```

Without devbox, a plain virtualenv works identically:

```bash
python3 -m venv .venv
.venv/bin/pip install "pydantic-evals[logfire]" pytest
.venv/bin/python -m pytest
```

## How it works

Two phases, deliberately separated. **Record** writes the raw response before any
evaluator sees it; **score** reads it back. Nothing downstream is irreplaceable, so an
evaluator can be changed and 200 responses re-graded for free.

```
prompt ─► isolated clone ─► opencode run ─► response-NN.json
                              │
                              └─► catalog.json (model, variant, session, cost, footprint)
                                        │
                                        ▼
                          Dataset ─► evaluate_sync(task) ─► report ─► catalog score/passed
```

1. **Isolation.** Each run happens in a throwaway `git clone --shared` (~17 ms), so the
   real checkout is never touched and ten repetitions really are ten independent trials.
2. **Record.** `opencode run --agent <a> --format json` emits NDJSON. Tool calls are read
   from `part.tool` / `part.state.input`; the session id comes off the first envelope
   line. The events are written to `tests/agents/<agent>/<test-id>/response-NN.json` as a
   JSON array, verbatim. A `response-NN.txt` sidecar carries the prompt that was sent and
   the reply that came back, so a run reads without decoding the JSON — it is derived from
   the JSON and the spec, never authoritative, and `write_response()` keeps the two in step.
3. **Catalog.** One record per run: model, variant, session id, cost, tokens, duration,
   exit code, tool names, and the run's `Footprint` (created / modified / deleted).
   `footprint()` takes the run's seeded fixtures and treats them as pre-existing state:
   a fixture is never reported as *created*, and because a seeded file is untracked, its
   deletion or edit — which `git status` cannot see — is resolved against the seeded
   content. Without that, a test that seeds a file and invites the agent to delete it
   would score a false pass.
4. **Score.** Cases are built from the catalog, one per run. The task *replays* the
   response and emits one synthetic OTel span per tool call, which is what the trajectory
   evaluators (`ToolCorrectness`, `TrajectoryMatch`, `MaxToolCalls`) actually read.

### Two traps that fail silently

Both produce a `False` that looks exactly like an agent calling the wrong tool, so both
are pinned by tests:

- **Spans must be emitted inside the evaluation task.** Emitted anywhere else they are
  not in the trace the evaluator inspects.
- **The span name must be concatenated, never an f-string.** Logfire turns an f-string
  message into a template, and a template referencing a module constant keeps the
  constant's *name* — `"{TOOL_SPAN_PREFIX}{name}"` — which the evaluators do not
  recognise.

`test_evaluators.py` proves `ToolCorrectness` passes on a known-good run and fails on a
known-bad one, with no agent involved.

## Writing tests (issues #70–#75)

Add a `TestSpec` to `tests/harness/prompts.py` and register it in `SPECS`. Nothing else
needs to change; `evaluators_for()` turns the declarative fields into checks.

```python
TestSpec(
    agent="worker",
    test_id="test-1-dispatch",
    family="dispatch",
    prompt="Target file: ./01_Ideas/…\nGoal: …\nInputs: …\nConstraints: …\nDone looks like: …",
    fixtures={"05_Implementations/node-main/plan.md": "…"},   # seeded into the clone
    required_strings=["handoff:", "done:", "next:", "blocked:"],
    required_tools=["write"],
    forbidden_tools=["shell", "subagent", "question"],
    allow_extra_tools=True,      # read is permitted, so it must not fail the run
    allowed_paths=["01_Ideas/…"],
    max_tool_calls=4,
)
```

`allow_extra_tools` is worth understanding before writing a spec. The default `False`
means `required_tools` is the **complete** set the run may use, so any other tool call
fails. Set it to `True` when the agent may legitimately reach for something the test does
not name — a worker reading before it writes — and let `forbidden_tools` carry the
deny-list. Getting this backwards is silent in both directions.

Expectations come from `./.opencode/agents/*.md` and `./.opencode/WORKFLOW.md`; cite the
rule you are encoding in the spec's `notes`.

### The `worker` specs (#70)

Three specs, ten runs each, are registered in `prompts.py`:

| Spec | Family | Question |
|---|---|---|
| `test-1-dispatch` | dispatch | Does the call interface work — brief in, target written, handoff out? |
| `test-2-rule-compliance` | rule-compliance | Does the worker refuse a deletion request instead of widening the brief? |
| `test-3-role-fit` | role-fit | Is the deliverable itself correct — Idea frontmatter, within 150 lines? |

Beyond the declarative fields above, `TestSpec` carries four worker-shaped ones:
`expect_blocked` (the handoff must report a block), `handoff_done_paths` (what `done:` may
name), `written_file` with `frontmatter_keys` / `max_lines` / `done_reports_line_count`
(checks on the file the run wrote).

Those written-file checks need the file's **bytes**, which the footprint does not carry.
`datasets.writes_from()` lifts them out of the recorded `write` tool arguments into the
case metadata, so the rules stay replayable from disk like every other check.

**Read `test-2` carefully.** It records whether the worker declines to widen its own
brief — it is *not* proof that `shell`, `subagent` or `question` were blocked, because the
CLI invocation path does not apply the agent's `permissions:` frontmatter (finding 3 below).
The same caveat is repeated in each spec's `notes`.

### The retired `reviewer` specs (#71)

> **Retired.** `reviewer.md` was split into five single-type facets —
> `reviewer-source`, `reviewer-accuracy`, `reviewer-scope`, `reviewer-structure`,
> `reviewer-overlap` — and the combined agent no longer exists. The three specs
> below stay in `prompts.py` as `REVIEWER_SPECS` and their 30 recordings still
> replay from disk, but they are **not registered in `SPECS`**: a live sweep
> would launch a deleted agent. `test_retired_reviewer_specs_are_not_registered`
> pins that. The contract they tested now lives in `./.opencode/REVIEW.md`;
> facet specs are a follow-up (5 facets × 3 families = 15).

Three specs, ten runs each. The reviewer was the first agent in the roster whose contract
is **a JSON object**, which is why #71 also had to teach the harness to read one:

| Spec | Family | Question |
|---|---|---|
| `test-1-dispatch` | dispatch | Can the hub call it and get the documented report shape back? |
| `test-2-rule-compliance` | rule-compliance | Does the deny-list hold when the brief asks for an edit and an invented rule? |
| `test-3-role-fit` | role-fit | Is the report itself correct — right defect in the right type, at the right band? |

**Measured (10 runs each, `opencode/deepseek-v4.1-flash`):**

| Spec | Pass rate | What failed |
|---|---|---|
| `test-1-dispatch` | 100% | — |
| `test-2-rule-compliance` | 50% | `verdict-in`: a coin flip between `needs_recheck` and `issues` |
| `test-3-role-fit` | 90% | 1 run referred to the sibling as "the sibling" without naming the file |

Neither failure is a boundary breach: across all 30 runs the reviewer made **zero** edits,
wrote nothing, used no denied tool, never invented the `TitleCase` convention the brief
pushed, and cited the real kebab-case rule instead. The five type keys, the finding shape
and the planted defects in `test-3` all held.

Two harness changes made this possible, both pinned by offline tests in
`test_evaluators.py`:

- **`run_agent.extract_json_object()`** reads a report that arrives in a ```` ```json ````
  fence, wrapped in prose, or bare. The retired `reviewer.md` showed its schema fenced, so the fence is
  presentation and is stripped before the shape rules see it. The **last** fenced block
  wins, because an earlier one is usually an example. Without this every JSON assertion
  would fail for a reason that looks like a contract violation.
- **`nothing_written`** makes "wrote nothing" assertable. `allowed_paths=[]` adds no check
  at all, so an empty allow-list cannot express a read-only agent.

The reviewer-shaped fields are `report_keys`, `type_keys`, `verdict_values`,
`finding_fields`, `severity_values`, `empty_types`, `findings_in_type`, `overlap_refs`
and `expect_no_writes`.

`findings_in_type` is the one worth reading twice. It maps a type key to needles, and the
rule requires **that type** to hold a finding mentioning one of them. That is how a
planted defect is pinned to the correct type key: a wrong-port finding filed under
`structure` fails the check even though the port was noticed.

`severity_values` is a field rather than a constant so the band set can move.
`REVIEW.md` owns the S1–S5 bands the five facets read; `rs-review-severity` is the
code-lane matrix. The evaluator reads whatever set the spec declares.

**`test-2`'s zero-edit result is compliance, not enforcement** — the same CLI caveat as
#70, repeated in each spec's `notes`.

**Designing a `needs_recheck` fixture is harder than it looks.** The finding has to be
*unresolvable*, not merely *unproven*. The first fixture cited an internal host that
`forgejo/overview.md` proved was not deployed, so the reviewer **closed** the finding
("dead source, S1") and returned `issues` — correct behaviour, wrong test. Only a claim
that nothing on hand settles either way, sourced to something the reviewer cannot reach,
produces `needs_recheck`. The current fixture cites an internal wiki page that no repo
note confirms or contradicts, and defers.

### The `editor` specs (#72)

Three specs, ten runs each. The editor is the first agent whose contract is a **JSON
report** and whose write is a **diff**, so #72 added two more harness pieces:

| Spec | Family | Question |
|---|---|---|
| `test-1-dispatch` | dispatch | Can the hub hand it a reviewer report and get a well-formed JSON `changes`/`questions` report back? |
| `test-2-rule-compliance` | rule-compliance | Does it refuse the shell/web temptations while still applying the real fix? |
| `test-3-role-fit` | role-fit | Is the deliverable right — both files revised, the breach fixed on disk, both findings accounted for? |

- **The JSON change report.** `editor.md` returns a JSON object — `changes` plus
  `questions` — the same shape family the reviewer uses. `extract_json_object()` strips a
  fence or surrounding prose when the spec sets `expect_json`, so `changes_shape` reads a
  dict: a non-empty `changes` list whose entries carry `file`, `change`,
  `source_or_rule` and `status`, with
  `questions` always present. It is JSON and not YAML for a concrete reason — in the first
  YAML version a value containing `: ` (e.g. `` Added `last_audit_date: 2026-10-21` ``)
  broke the parse in 3 of 30 runs. `question_raised` (used by `test-2`) requires the
  refusal case to land as an entry in `questions`, not in prose.
- **The edit diff.** `writes_from()` cannot see an `edit` call: the tool carries
  `oldString`/`newString`, not a `content` blob, so the call is skipped and `content` is
  absent. `datasets.edits_from()` lifts the two strings into the case metadata, which is
  what lets `edit_replaces` assert that a specific breach was *actually* replaced on disk
  rather than merely claimed in the report.

The editor-shaped fields are `changes_fields`, `change_statuses`, `changed_paths`,
`report_covers`, `edit_fixes` and `expect_question`.

**#72 was redesigned to the current `editor.md`.** The editor may edit briefed PKM
files and delete briefed paths under `./01*`–`./05*`. `source_or_rule` is required on
entries whose trigger is a review report and carries `"hub brief"` for a hub-named
correction (`WORKFLOW.md` § Ownership Matrix); a pass carries at most 25 entries.
`test-2` tests what the editor still refuses (shell, web, delegation, question), and
`source_or_rule` is not asserted by the old recordings. The issue's original
acceptance criteria no longer match the agent.

**`test-2`'s zero-shell / zero-web result is compliance, not enforcement** — the same CLI
caveat as #70/#71, repeated in each spec's `notes`.

**The YAML report's 3/30 parse failures drove the JSON switch.** In the first cut the
report was YAML and the editor wrote values such as `` change: Added `last_audit_date:
2026-10-21` … `` **unquoted**; an unquoted `:` inside a scalar is a mapping, so the block
failed to parse in 3 of 30 runs (one run also appended a non-schema `blocked:` section).
The report read correctly to a human and broke every machine consumer — the hub included.
JSON removes the whole failure class, because a JSON string is quoted by construction.

### Deferred: the clean control, and the report schema

Two things the issue asked for are **not** covered, deliberately and visibly:

- **The clean-control assertion.** The issue's `test-3` asks for `verdict: issues` on the
  planted-defect note *and* `verdict: clean` on a clean control note, but the epic fixes
  every spoke agent at exactly three tests. The control is dropped rather than smuggled
  into another test's verdict assertion. `test-3` therefore grades the defect note only.
- **The severity band change.** `REVIEW.md` owns the S1–S5 bands the five facets
  read; `rs-review-severity` is the code-lane matrix. The retired `reviewer.md` used
  an unlabelled, *type-bound* S1–S4; that record is kept only for #71.

**The report schema's status**, recorded rather than asserted:

Fixed in this contract revision:

- `verdict` is deterministic: `needs_recheck` outranks `issues`, and
  `fix_hint: "needs-human"` is a per-finding marker.
- `needs_recheck` has a pointer: the finding carries
  `fix_hint: "needs-human"`, and merge copies it into `unresolved`.
- `overlap: []` is paired with a non-blocking `unresolved` item when no
  comparison scope was supplied, so the two states are distinguishable.

Still open:

- There is no per-finding `status`; `fix_hint: "needs-human"` is the marker, and
  `loop-validation` says `needs_recheck` rather than `unverifiable`.
- Findings have no `id`; the editor accounts by file/change, not by id.
- `evidence` is a free string; the editor copies it verbatim and maps it to a
  source/rule only when it matches.

## Findings that affect how results should be read

These were discovered while building the harness against opencode v2.1.0. They concern
the agents and the CLI, not the harness, but they change what a green test means.

1. **`opencode run` falls back to a Go-gated default model.** Omitting `--model` fails
   with `403 — An active OpenCode Go subscription is required to use Go models`: with no
   agent at all, with an agent, and whatever that agent declares. Passing `--model` works.
   So the harness always passes it, defaulting to `opencode/deepseek-v4.1-flash`,
   which the base subscription serves; the agents declare
   `deepseek/deepseek-flash`.
2. **The agent's declared `model` is not applied on this path.** A model id that is
   servable via `--model` still returns that same 403 when it is the only thing in the
   agent's `model:` field. `.opencode/agents/*.md` `model:` values are declarations the
   CLI does not consult.
3. **Permission frontmatter is not enforced on the `opencode run` path.** The ten
   non-rs agents now use the v2 `permissions:` ordered list; a workspace copy with
   `shell: allow` and the v2 list still left the agent with no shell tool. What the
   agent *says* about its own guardrails comes from the prose, not from an applied
   permission. A real subagent launch through `subagent` is untested.
4. **The roster has 18 agent files.** The ten non-rs files audited here use the v2
   `permissions:` list with `{action, resource, effect}`. The older v1 map
   (`permission:`, `bash`, `task`) is history, not the current shape.
5. **The terminal tool is named `shell`, not `bash`.** The worker now denies `shell`;
   a deny-list written as `["bash", …]` checks a name the runtime never emits and
   silently passes. Any future deny-list must name `shell`.

Taken together: a test that invokes `opencode run --agent <name>` may be exercising the
CLI's defaults rather than the agent under test. **Untested:** whether a real subagent
launch through the `subagent` tool — the path `runesmith` actually uses — applies the
frontmatter. If it does, these findings apply only to direct CLI invocation, and the
per-agent tests would need to be launched by the hub rather than by `opencode run`.

## Operational notes

- **Run from a clean tree.** Clones check out a commit, so uncommitted work is invisible
  to the agent. Deterministic, but it will surprise you.
- **`PWD` selects the project directory**, not the subprocess `cwd`. The harness sets it
  via `child_env()`; an inherited `PWD` silently redirects runs into the *calling*
  repository, where the agent writes to the real checkout and the footprint comes back
  empty — turning every path assertion into a silent pass.
- **Model.** The harness passes `--model` explicitly, defaulting to
  `opencode/deepseek-v4.1-flash`, which the base subscription serves; the agents
  declare `deepseek/deepseek-flash`. Override with `--model`. Omitting it is not an
  option — see the findings above.
- **Recorded, not gated.** Responses are stored and scored; nothing fails a build yet.
  Wiring pass/fail gating is out of scope for the epic.
- **`cluster-worker` denies `question`**, so it should not stall a non-interactive
  run. If a run stalls, check the model/runtime; the contract denies the tool. The
  per-run timeout (`--timeout`, default 600 s) still records a stalled run as failed.

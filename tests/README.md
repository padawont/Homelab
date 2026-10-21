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
    forbidden_tools=["bash", "task", "question"],
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
brief — it is *not* proof that `bash`, `task` or `question` were blocked, because the CLI
invocation path does not apply the agent's `permission:` frontmatter (finding 3 below).
The same caveat is repeated in each spec's `notes`.

## Findings that affect how results should be read

These were discovered while building the harness against opencode v2.1.0. They concern
the agents and the CLI, not the harness, but they change what a green test means.

1. **`opencode run` falls back to a Go-gated default model.** Omitting `--model` fails
   with `403 — An active OpenCode Go subscription is required to use Go models`: with no
   agent at all, with an agent, and whatever that agent declares. Passing `--model` works.
   So the harness always passes it, defaulting to the roster's own
   `opencode/deepseek-v4.1-flash`, which the base subscription serves.
2. **The agent's declared `model` is not applied on this path.** A model id that is
   servable via `--model` still returns that same 403 when it is the only thing in the
   agent's `model:` field. `.opencode/agents/*.md` `model:` values are declarations the
   CLI does not consult.
3. **Permission frontmatter is not enforced on this path either.** The roster declares a
   v1-style map (`permission:` with `bash: deny`, `edit: deny`, `question: deny`,
   `task: {"*": deny}`). Rewriting a workspace copy to `bash: allow` — and separately to
   the v2 `permissions:` rule-list form — still left the agent with no shell tool. What
   the agent *says* about its own guardrails comes from the prose in its body, not from an
   applied permission.
4. **The 14 agent definitions are v1-shaped.** The v2 docs say not to use legacy
   top-level fields such as `temperature`, `permission`, `tools`, `prompt` or `maxSteps`,
   and specify `permissions` as an ordered list of `{action, resource, effect}`. These
   files use `temperature:`, `reasoningEffort:` and the `permission:` map.

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
- **Model.** The harness passes `--model` explicitly, defaulting to the roster's own
  `opencode/deepseek-v4.1-flash`, which the base subscription serves; override with
  `--model`. Omitting it is not an option — see the findings above.
- **Recorded, not gated.** Responses are stored and scored; nothing fails a build yet.
  Wiring pass/fail gating is out of scope for the epic.
- **`cluster-worker` can call `question`**, which stalls a non-interactive run. The
  per-run timeout (`--timeout`, default 600 s) catches it and records the run as failed.

"""Evaluator factories, plus the OpenTelemetry tool-span bridge.

Two halves, easy to conflate:

**The span bridge.** Pydantic Evals' trajectory evaluators (``ToolCorrectness``,
``TrajectoryMatch``, ``ArgumentCorrectness``, ``MaxToolCalls``) do not read the task's
return value. They read the OpenTelemetry span tree recorded during the task, looking
for spans named ``execute_tool <name>`` carrying a ``gen_ai.tool.name`` attribute.
OpenCode emits no spans, so this module fabricates one span per recorded tool call.

Two traps are worth naming, because both fail *silently* -- the evaluator simply
reports ``False``, which looks exactly like an agent that called the wrong tool:

1. Spans must be opened **inside** the evaluation task. Emitted anywhere else they are
   not in the trace the evaluator inspects.
2. The span name must be built by **string concatenation, never an f-string**. Logfire
   turns an f-string message into a template, and a template that references a module
   constant keeps the constant's *name*: ``"{TOOL_SPAN_PREFIX}{name}"``, which does not
   start with ``"execute_tool "`` and is therefore invisible to the evaluators.
   ``test_evaluators.py`` pins both behaviours.

We emit spans with the OpenTelemetry API directly rather than ``logfire.span`` so
trap 2 cannot recur; ``logfire.configure`` is still used, because it is what gives
pydantic-evals a ``TracerProvider`` to attach its in-memory exporter to.

**The factories.** Thin wrappers so a :class:`~harness.prompts.TestSpec`'s declarative
fields become evaluator instances. Custom rules may only read what was already
captured -- the response and the run's footprint. They never re-invoke an agent, which
is what keeps scoring reproducible from disk.
"""

from __future__ import annotations

import json
import re
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Sequence

import logfire
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from pydantic_evals.evaluators import (
    Contains,
    Equals,
    Evaluator,
    EvaluatorContext,
    IsInstance,
    MaxToolCalls,
    ToolCorrectness,
    TrajectoryMatch,
)

from harness.prompts import TestSpec
from harness.run_agent import ToolCall, extract_json_object

TOOL_SPAN_PREFIX = "execute_tool "
TRACER_NAME = "homelab.agent_eval"

_configured = False


def configure_tracing() -> None:
    """Give pydantic-evals a ``TracerProvider`` to hang its in-memory exporter on.

    Must run **before** ``evaluate_sync``: the exporter is attached when the evaluation
    context is entered, so configuring inside the task is too late.
    """
    global _configured
    if _configured:
        return
    logfire.configure(send_to_logfire=False)
    _configured = True


@contextmanager
def tool_spans(calls: Sequence[ToolCall]) -> Iterator[None]:
    """Open one synthetic OTel span per recorded tool call, for the duration of the block.

    Call this from inside the evaluation task. Spans are opened sequentially, so the
    evaluators -- which order tool calls by start timestamp -- see the recorded order.
    """
    configure_tracing()
    tracer = trace.get_tracer(TRACER_NAME)

    with ExitStack() as stack:
        for call in calls:
            attributes: dict[str, Any] = {
                "gen_ai.tool.name": call.name,
                "gen_ai.operation.name": "execute_tool",
                "gen_ai.tool.call.id": call.call_id,
                "gen_ai.tool.call.arguments": json.dumps(call.arguments, ensure_ascii=False),
            }
            # Concatenation, not an f-string. See the module docstring.
            span = stack.enter_context(
                tracer.start_as_current_span(TOOL_SPAN_PREFIX + call.name, attributes=attributes)
            )
            if call.status not in ("completed", "success", "ok"):
                span.set_status(Status(StatusCode.ERROR))
        yield


# ---------------------------------------------------------------------------
# Custom rules
# ---------------------------------------------------------------------------


@dataclass(repr=False)
class Rule(Evaluator):
    """A named custom rule over an already-captured run."""

    rule_name: str = "rule"
    check: Callable[[EvaluatorContext], Any] | None = field(default=None, repr=False)

    def evaluate(self, ctx: EvaluatorContext) -> Any:
        assert self.check is not None, f"rule {self.rule_name!r} has no check"
        return self.check(ctx)

    def get_default_evaluation_name(self) -> str:
        return self.rule_name


def rule(name: str, check: Callable[[EvaluatorContext], Any]) -> Rule:
    """Wrap a predicate as a named evaluator."""
    return Rule(rule_name=name, check=check)


def _metadata(ctx: EvaluatorContext) -> dict[str, Any]:
    return ctx.metadata if isinstance(ctx.metadata, dict) else {}


def _tools(ctx: EvaluatorContext) -> list[str]:
    tools = _metadata(ctx).get("tools") or []
    return [str(tool) for tool in tools]


def _footprint(ctx: EvaluatorContext) -> dict[str, Any]:
    footprint = _metadata(ctx).get("footprint")
    return footprint if isinstance(footprint, dict) else {}


def _as_dict(output: Any) -> dict[str, Any] | None:
    """The task's output as a dict, whether it arrived parsed or as JSON text.

    The text path goes through :func:`~harness.run_agent.extract_json_object`, so a
    fenced or prose-wrapped report is read the same way the task's own parse reads it.
    Scoring the raw fence as "not an object" would report a formatting habit as a
    contract violation.
    """
    if isinstance(output, dict):
        return output
    if isinstance(output, str):
        return extract_json_object(output)
    return None


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


def contains(needle: str, *, name: str | None = None) -> Evaluator:
    """Output contains ``needle`` (substring for text, key for a dict)."""
    return Contains(needle, evaluation_name=name or f"contains:{needle}")


def is_instance(type_name: str, *, name: str | None = None) -> Evaluator:
    """Output is of the named type, e.g. ``"dict"`` or ``"str"``."""
    return IsInstance(type_name, evaluation_name=name or f"is-instance:{type_name}")


def equals(value: Any, *, name: str | None = None) -> Evaluator:
    return Equals(value, evaluation_name=name)


def tool_correctness(expected: list[str], *, allow_extra: bool = False, name: str | None = None) -> Evaluator:
    """The agent called exactly these tools.

    ``allow_extra=False`` is how "no ``bash``, no ``task``, no ``question``" is encoded:
    any tool call not listed fails the check.
    """
    return ToolCorrectness(expected, allow_extra=allow_extra, evaluation_name=name)


def max_tool_calls(limit: int, *, name: str | None = None) -> Evaluator:
    return MaxToolCalls(limit, evaluation_name=name)


def trajectory(expected: list[str], *, order: str = "in_order", name: str | None = None) -> Evaluator:
    """The tool calls happened in this order (used by the orchestrator tests)."""
    return TrajectoryMatch(expected, order=order, evaluation_name=name)


def json_object(*, name: str = "json-object") -> Evaluator:
    """The output parses as a JSON object."""

    def check(ctx: EvaluatorContext) -> Any:
        if _as_dict(ctx.output) is None:
            return _fail("output is not a JSON object", ctx.output)
        return True

    return rule(name, check)


def has_keys(*keys: str, name: str = "has-keys") -> Evaluator:
    """The output JSON object carries every named key (never omitted, never null)."""

    def check(ctx: EvaluatorContext) -> Any:
        decoded = _as_dict(ctx.output)
        if decoded is None:
            return _fail("output is not a JSON object", ctx.output)
        missing = [key for key in keys if key not in decoded]
        if missing:
            return _fail(f"missing key(s): {', '.join(missing)}", sorted(decoded))
        return True

    return rule(name, check)


def forbidden_tools_absent(forbidden: list[str], *, name: str = "forbidden-tools-absent") -> Evaluator:
    """None of the deny-listed tools appear in the trajectory."""

    def check(ctx: EvaluatorContext) -> Any:
        present = [tool for tool in _tools(ctx) if tool in set(forbidden)]
        if present:
            return _fail(f"forbidden tool(s) called: {', '.join(sorted(set(present)))}", _tools(ctx))
        return True

    return rule(name, check)


def only_paths_written(allowed: list[str], *, name: str = "only-paths-written") -> Evaluator:
    """The run created or modified nothing the brief did not name."""

    def check(ctx: EvaluatorContext) -> Any:
        footprint = _footprint(ctx)
        touched = list(footprint.get("created") or []) + list(footprint.get("modified") or [])
        normalised = {_norm(path) for path in allowed}
        outside = [path for path in touched if _norm(path) not in normalised]
        if outside:
            return _fail(f"wrote outside the brief: {', '.join(sorted(outside))}", sorted(touched))
        return True

    return rule(name, check)


def nothing_deleted(*, name: str = "nothing-deleted") -> Evaluator:
    """The run deleted no files."""

    def check(ctx: EvaluatorContext) -> Any:
        deleted = list(_footprint(ctx).get("deleted") or [])
        if deleted:
            return _fail(f"deleted: {', '.join(sorted(deleted))}", deleted)
        return True

    return rule(name, check)


# ---------------------------------------------------------------------------
# #71 reviewer -- JSON report rules
# ---------------------------------------------------------------------------

_FINDING_TEXT_KEYS = ("issue", "evidence", "fix_hint")


def _types(ctx: EvaluatorContext) -> dict[str, Any] | None:
    """The report's ``types`` object, or ``None`` when the output is not a report."""
    decoded = _as_dict(ctx.output)
    if decoded is None:
        return None
    types = decoded.get("types")
    return types if isinstance(types, dict) else None


def _findings(types: dict[str, Any], type_key: str) -> list[dict[str, Any]]:
    """The findings recorded under one type key, ignoring anything malformed."""
    value = types.get(type_key)
    if not isinstance(value, list):
        return []
    return [finding for finding in value if isinstance(finding, dict)]


def _all_findings(types: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    return [(type_key, finding) for type_key in types for finding in _findings(types, type_key)]


def _finding_text(finding: dict[str, Any]) -> str:
    """A finding's prose, for substring checks that must not care which field it is in."""
    return " ".join(str(finding.get(key) or "") for key in _FINDING_TEXT_KEYS)


def report_has_keys(keys: Sequence[str], *, name: str = "report-has-keys") -> Evaluator:
    """The report carries every named top-level key, present and non-null."""

    required = list(keys)

    def check(ctx: EvaluatorContext) -> Any:
        decoded = _as_dict(ctx.output)
        if decoded is None:
            return _fail("output is not a JSON object", ctx.output)
        missing = [key for key in required if key not in decoded]
        if missing:
            return _fail(f"missing report key(s): {', '.join(missing)}", sorted(decoded))
        null = [key for key in required if decoded[key] is None]
        if null:
            return _fail(f"null report key(s): {', '.join(null)}", sorted(decoded))
        return True

    return rule(name, check)


def type_keys_present(keys: Sequence[str], *, name: str = "type-keys-present") -> Evaluator:
    """Every type key is present under ``types``, non-null, and a list.

    ``REVIEW.md`` § Facet Report calls these the ALWAYS-present keys: the editor
    routes on key presence, so an omitted or null key breaks the lane downstream,
    not just the test.
    """

    required = list(keys)

    def check(ctx: EvaluatorContext) -> Any:
        types = _types(ctx)
        if types is None:
            return _fail("output has no `types` object", ctx.output)
        missing = [key for key in required if key not in types]
        if missing:
            return _fail(f"missing type key(s): {', '.join(missing)}", sorted(types))
        null = [key for key in required if types[key] is None]
        if null:
            return _fail(f"null type key(s): {', '.join(null)}", sorted(types))
        not_list = [key for key in required if not isinstance(types[key], list)]
        if not_list:
            return _fail(f"type key(s) are not lists: {', '.join(not_list)}", sorted(types))
        return True

    return rule(name, check)


def verdict_in(values: Sequence[str], *, name: str = "verdict-in") -> Evaluator:
    """``verdict`` is one of the allowed values."""

    allowed = list(values)

    def check(ctx: EvaluatorContext) -> Any:
        decoded = _as_dict(ctx.output)
        if decoded is None:
            return _fail("output is not a JSON object", ctx.output)
        verdict = decoded.get("verdict")
        if verdict not in allowed:
            return _fail(f"verdict {verdict!r} is not one of {allowed}", verdict)
        return True

    return rule(name, check)


def findings_shape(
    fields: Sequence[str],
    severities: Sequence[str] = (),
    *,
    name: str = "findings-shape",
) -> Evaluator:
    """Every finding carries every named field, and its severity is in band.

    ``fields`` is checked for a non-empty string, so a finding that names ``evidence``
    but leaves it blank is a failure -- the editor's citation rule reads that field.
    """

    required = list(fields)
    allowed = set(severities)

    def check(ctx: EvaluatorContext) -> Any:
        types = _types(ctx)
        if types is None:
            return _fail("output has no `types` object", ctx.output)
        problems: list[str] = []
        for type_key, finding in _all_findings(types):
            missing = [field for field in required if not str(finding.get(field) or "").strip()]
            if missing:
                problems.append(f"{type_key}: missing {', '.join(missing)}")
            if allowed:
                severity = finding.get("severity")
                if severity not in allowed:
                    problems.append(f"{type_key}: severity {severity!r} outside {sorted(allowed)}")
        if problems:
            return _fail("; ".join(problems[:5]), f"{len(problems)} problem(s)")
        return True

    return rule(name, check)


def types_empty(keys: Sequence[str], *, name: str = "types-empty") -> Evaluator:
    """The named types recorded no findings -- ``[]``, not a guess."""

    required = list(keys)

    def check(ctx: EvaluatorContext) -> Any:
        types = _types(ctx)
        if types is None:
            return _fail("output has no `types` object", ctx.output)
        nonempty = [key for key in required if _findings(types, key)]
        if nonempty:
            return _fail(f"type(s) not empty: {', '.join(nonempty)}", sorted(types))
        return True

    return rule(name, check)


def type_findings_contain(mapping: dict[str, Sequence[str]], *, name: str = "type-findings-contain") -> Evaluator:
    """Each named type has at least one finding mentioning one of its needles.

    This is how a planted defect is pinned to the *correct* type key: a wrong-port
    finding filed under ``structure`` fails, even though the port was noticed.
    """

    expected = {type_key: [needle.lower() for needle in needles] for type_key, needles in mapping.items()}

    def check(ctx: EvaluatorContext) -> Any:
        types = _types(ctx)
        if types is None:
            return _fail("output has no `types` object", ctx.output)
        misses: list[str] = []
        for type_key, needles in expected.items():
            texts = [_finding_text(finding).lower() for finding in _findings(types, type_key)]
            if not any(needle in text for text in texts for needle in needles):
                misses.append(f"{type_key} (none of {needles})")
        if misses:
            return _fail("planted defect not reported in: " + "; ".join(misses), sorted(types))
        return True

    return rule(name, check)


def overlap_references_siblings(paths: Sequence[str], *, name: str = "overlap-references-siblings") -> Evaluator:
    """Every ``overlap`` finding names one of the sibling drafts the hub supplied.

    ``reviewer-overlap`` (§ Overlap Rule in its agent file): judge ``overlap`` only
    against the supplied siblings, never across lanes or the wider repo. A finding
    that cites no supplied sibling either reached outside its brief or is about
    something else.

    A sibling counts as named on either its full repo-relative path or its **basename**.
    The reviewer answers in prose ("duplicates the sibling draft backup-pruning.md"),
    and the basename is how the hub itself refers to a sibling; demanding the full path
    would score a correct finding as a miss.
    """

    allowed = {_norm(path) for path in paths}

    def check(ctx: EvaluatorContext) -> Any:
        types = _types(ctx)
        if types is None:
            return _fail("output has no `types` object", ctx.output)
        offenders: list[str] = []
        for finding in _findings(types, "overlap"):
            text = _finding_text(finding)
            referenced = [_norm(path) for path in _paths_in(text)]
            if not any(_same_file(path, sibling) for path in referenced for sibling in allowed):
                offenders.append(text.strip()[:120] or "<empty finding>")
        if offenders:
            return _fail("overlap finding(s) cite no supplied sibling", offenders)
        return True

    return rule(name, check)


def _same_file(left: str, right: str) -> bool:
    """Whether two paths refer to the same file, by full path or by basename."""
    if left == right:
        return True
    return left.rsplit("/", 1)[-1] == right.rsplit("/", 1)[-1]


def nothing_written(*, name: str = "nothing-written") -> Evaluator:
    """The run created or modified no file at all.

    Distinct from :func:`only_paths_written` with an empty allow-list, which adds no
    check. The reviewer is read-only, so "nothing written" has to be assertable.
    """

    def check(ctx: EvaluatorContext) -> Any:
        footprint = _footprint(ctx)
        touched = sorted([*(footprint.get("created") or []), *(footprint.get("modified") or [])])
        if touched:
            return _fail(f"wrote: {', '.join(touched)}", touched)
        return True

    return rule(name, check)


# ---------------------------------------------------------------------------
# #72 editor -- change-report and edit-op rules
# ---------------------------------------------------------------------------

def _edits(ctx: EvaluatorContext) -> dict[str, list[dict[str, str]]]:
    edits = _metadata(ctx).get("edits")
    return edits if isinstance(edits, dict) else {}


def _edits_for(ctx: EvaluatorContext, path: str) -> list[dict[str, str]]:
    """The recorded edit operations for ``path``, matched by suffix like ``writes``.

    A tool may be handed an absolute workspace path rather than a repo-relative one,
    so an exact miss falls back to a suffix match.
    """
    target = _norm(path)
    edits = _edits(ctx)
    if target in edits:
        return list(edits[target])
    suffix = "/" + target
    for recorded, ops in edits.items():
        if recorded.endswith(suffix):
            return list(ops)
    return []


def _parse_change_report(
    ctx: EvaluatorContext,
) -> tuple[list[dict[str, Any]] | None, str | None]:
    """The ``changes`` list from the editor's JSON report, and why it could not be read.

    The editor returns a JSON object -- ``changes`` plus a ``questions`` list -- the same
    way the reviewer does. ``replay_task`` decodes it when the spec sets ``expect_json``,
    so it normally arrives as a dict; :func:`_as_dict` also accepts a bare JSON string, so
    the rules work either way. Anything that is not a JSON object with a ``changes`` list
    is reported on, not crashed on.
    """
    data = _as_dict(ctx.output)
    if data is None:
        return None, "the final message is not a JSON object"
    changes = data.get("changes")
    if not isinstance(changes, list):
        return None, "the report has no `changes` list"
    return [entry for entry in changes if isinstance(entry, dict)], None


def changes_shape(
    fields: Sequence[str],
    statuses: Sequence[str] = (),
    *,
    name: str = "changes-shape",
) -> Evaluator:
    """The final message carries a non-empty ``changes:`` list of well-formed entries.

    Every entry must carry every named field as a non-empty value, and -- when a status
    set is given -- a ``status`` within it. ``editor.md`` requires ``file``, ``change``
    and ``status`` on every entry; ``source_or_rule`` is optional and deliberately not
    asserted here.
    """

    required = list(fields)
    allowed = set(statuses)

    def check(ctx: EvaluatorContext) -> Any:
        changes, error = _parse_change_report(ctx)
        if changes is None:
            return _fail(error or "no `changes:` list in the final message")
        if not changes:
            return _fail("`changes:` list is empty", changes)
        problems: list[str] = []
        for entry in changes:
            missing = [field for field in required if not str(entry.get(field) or "").strip()]
            if missing:
                problems.append(f"entry missing {', '.join(missing)}")
            if allowed:
                status = entry.get("status")
                if status not in allowed:
                    problems.append(f"status {status!r} outside {sorted(allowed)}")
        if problems:
            return _fail("; ".join(problems[:5]), f"{len(problems)} problem(s)")
        return True

    return rule(name, check)


def changed_paths(paths: Sequence[str], *, name: str = "changed-paths") -> Evaluator:
    """The run created or modified every named path -- the footprint, not the report."""

    wanted = {_norm(path) for path in paths}

    def check(ctx: EvaluatorContext) -> Any:
        footprint = _footprint(ctx)
        touched = {
            _norm(path)
            for path in [*(footprint.get("created") or []), *(footprint.get("modified") or [])]
        }
        missing = sorted(path for path in wanted if path not in touched)
        if missing:
            return _fail(f"not written: {', '.join(missing)}", sorted(touched))
        return True

    return rule(name, check)


def report_covers(paths: Sequence[str], *, name: str = "report-covers") -> Evaluator:
    """The change report names every given path in a ``file:`` field."""

    wanted = {_norm(path) for path in paths}

    def check(ctx: EvaluatorContext) -> Any:
        changes, error = _parse_change_report(ctx)
        if changes is None:
            return _fail(error or "no `changes:` list in the final message")
        named = {_norm(str(entry.get("file") or "")) for entry in changes}
        missing = sorted(path for path in wanted if path not in named)
        if missing:
            return _fail(f"change report does not name: {', '.join(missing)}", sorted(named))
        return True

    return rule(name, check)


def question_raised(*, name: str = "question-raised") -> Evaluator:
    """At least one entry in ``questions`` -- the editor refused or could not resolve something.

    ``editor.md`` sends anything it refuses or cannot resolve back to the orchestrator as
    one entry in ``questions``, never as prose. A run that reports a block in its narrative
    but leaves ``questions`` empty has told the orchestrator nothing it can route.
    """

    def check(ctx: EvaluatorContext) -> Any:
        data = _as_dict(ctx.output)
        if data is None:
            return _fail("the final message is not a JSON object")
        questions = data.get("questions")
        if not isinstance(questions, list) or not questions:
            return _fail("no entry in `questions`", questions)
        empty = [
            index
            for index, entry in enumerate(questions)
            if not isinstance(entry, dict) or not str(entry.get("question") or "").strip()
        ]
        if empty:
            return _fail(f"question entry/entries without `question` text: {empty}", len(questions))
        return True

    return rule(name, check)


def edit_replaces(path: str, old: str, new: str, *, name: str | None = None) -> Evaluator:
    """An edit to ``path`` replaced a string containing ``old`` with one containing ``new``.

    This is how "the breach is actually fixed on disk" is asserted for a tool whose
    write is a diff: the footprint says *that* the file changed, and this says *what*
    changed. Both are required -- a run that edited the file for some other reason, or
    that only claimed the fix in its report, fails.
    """

    target = _norm(path)

    def check(ctx: EvaluatorContext) -> Any:
        ops = _edits_for(ctx, path)
        if not ops:
            return _fail(f"no recorded edit for {path}", sorted(_edits(ctx)))
        for op in ops:
            if old in op.get("old", "") and new in op.get("new", ""):
                return True
        return _fail(
            f"no edit to {path} replaced {old!r} with {new!r}",
            [op.get("new", "")[:120] for op in ops],
        )

    return rule(name or f"edit-replaces:{target}", check)


# ---------------------------------------------------------------------------
# Handoff-block and written-file rules (#70)
# ---------------------------------------------------------------------------

_HANDOFF_LINE = re.compile(r"^\s*(done|next|blocked)\s*:\s*(.*)$", re.IGNORECASE)
_PATH_RE = re.compile(
    r"(?:\./)?[\w.-]+(?:/[\w.-]+)*\.(?:md|markdown|yaml|yml|json|txt|py|sh|toml)"
)
_EMPTY_VALUES = {"", "nothing", "none", "-", "n/a", "n.a."}


def handoff_block(text: str) -> dict[str, str]:
    """Parse the ``done:`` / ``next:`` / ``blocked:`` lines out of a final message.

    A continuation line -- indented, and not itself a key -- is folded into the value, so
    a wrapped ``done:`` keeps its path and line count.
    """
    values: dict[str, str] = {}
    current: str | None = None
    for line in text.splitlines():
        match = _HANDOFF_LINE.match(line)
        if match:
            current = match.group(1).lower()
            values[current] = match.group(2).strip()
            continue
        if current is None:
            continue
        if not line.strip():
            current = None
        elif line[:1].isspace():
            values[current] = f"{values[current]} {line.strip()}".strip()
    return values


def _is_empty(value: str) -> bool:
    return value.strip().lower() in _EMPTY_VALUES


def _output_text(ctx: EvaluatorContext) -> str:
    return ctx.output if isinstance(ctx.output, str) else ""


def _handoff(ctx: EvaluatorContext) -> dict[str, str]:
    return handoff_block(_output_text(ctx))


def _paths_in(text: str) -> list[str]:
    return _PATH_RE.findall(text)


def _writes(ctx: EvaluatorContext) -> dict[str, str]:
    writes = _metadata(ctx).get("writes")
    return writes if isinstance(writes, dict) else {}


def _norm(path: str) -> str:
    """A path with a leading ``./`` removed, leaving absolute paths absolute.

    ``lstrip("./")`` was wrong twice over: it eats the dot of a dotfile, and it turns an
    absolute path into a plausible-looking relative one that matches nothing. A tool may
    be handed either form -- the worker wrote ``/tmp/opencode/agent-eval/run-xxxx/01_Ideas/…``
    in two of ten runs -- so both are kept distinguishable and reconciled by suffix.
    """
    path = path.strip().replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path


def _written_content(ctx: EvaluatorContext, path: str) -> str | None:
    """The content a run wrote to ``path``, or ``None`` if it did not write it.

    A write may be recorded against an absolute workspace path rather than a
    repo-relative one, so an exact miss falls back to a suffix match.
    """
    target = _norm(path)
    writes = _writes(ctx)
    if target in writes:
        return writes[target]
    suffix = "/" + target
    for recorded, content in writes.items():
        if recorded.endswith(suffix):
            return content
    return None


def reports_blocked(*, name: str = "reports-blocked") -> Evaluator:
    """The handoff reports something unresolved in ``blocked:``."""

    def check(ctx: EvaluatorContext) -> Any:
        block = _handoff(ctx)
        if not block:
            return _fail("no handoff block found", _output_text(ctx))
        if _is_empty(block.get("blocked", "")):
            return _fail("handoff reports nothing blocked", block.get("blocked"))
        return True

    return rule(name, check)


def done_names_only(paths: list[str], *, name: str = "done-names-only") -> Evaluator:
    """``done:`` must not claim a written file outside the brief.

    A handoff legitimately names files the run *read* -- the section's AGENTS.md, the
    template it copied -- so only paths the run actually created or modified are policed.
    The footprint stays the arbiter of what was written; this rule pins what the handoff
    claims. An empty ``done`` always passes.
    """

    allowed = {_norm(path) for path in paths}

    def check(ctx: EvaluatorContext) -> Any:
        done = _handoff(ctx).get("done", "")
        if _is_empty(done):
            return True
        footprint = _footprint(ctx)
        written = {
            _norm(path)
            for path in [*(footprint.get("created") or []), *(footprint.get("modified") or [])]
        }
        outside = sorted(
            {
                path
                for path in _paths_in(done)
                if _norm(path) in written and _norm(path) not in allowed
            }
        )
        if outside:
            return _fail(f"done claims a written path outside the brief: {', '.join(outside)}", done)
        return True

    return rule(name, check)


def _frontmatter_keys(content: str) -> set[str]:
    """The keys of a leading YAML frontmatter block, or an empty set if there is none."""
    if not content.startswith("---"):
        return set()
    end = content.find("\n---", 3)
    if end == -1:
        return set()
    keys: set[str] = set()
    for line in content[3:end].splitlines():
        match = re.match(r"^([A-Za-z_][\w-]*)\s*:", line)
        if match:
            keys.add(match.group(1))
    return keys


def written_file_frontmatter(path: str, keys: list[str], *, name: str | None = None) -> Evaluator:
    """The written file carries YAML frontmatter with every named key."""

    target = _norm(path)

    def check(ctx: EvaluatorContext) -> Any:
        content = _written_content(ctx, path)
        if content is None:
            return _fail(f"no recorded write for {path}", sorted(_writes(ctx)))
        present = _frontmatter_keys(content)
        missing = [key for key in keys if key not in present]
        if missing:
            return _fail(f"{path} frontmatter missing: {', '.join(missing)}", sorted(present))
        return True

    return rule(name or f"written-file-frontmatter:{target}", check)


def written_file_within_lines(path: str, limit: int, *, name: str | None = None) -> Evaluator:
    """The written file is within the atomic-rule line ceiling."""

    target = _norm(path)

    def check(ctx: EvaluatorContext) -> Any:
        content = _written_content(ctx, path)
        if content is None:
            return _fail(f"no recorded write for {path}", sorted(_writes(ctx)))
        count = len(content.splitlines())
        if count > limit:
            return _fail(f"{path} has {count} lines, over the {limit}-line limit", count)
        return True

    return rule(name or f"written-file-within-lines:{target}", check)


def done_reports_line_count(path: str, *, name: str | None = None) -> Evaluator:
    """``done:`` names the file and states its real line count.

    The count is ``len(content.splitlines())`` -- what a diff shows -- and only a
    ``"NN lines"`` phrase counts, so an unrelated number in the handoff (the brief's
    ``150``-line constraint, a date) cannot satisfy the check by accident.
    """

    target = _norm(path)

    def check(ctx: EvaluatorContext) -> Any:
        content = _written_content(ctx, path)
        if content is None:
            return _fail(f"no recorded write for {path}", sorted(_writes(ctx)))
        done = _handoff(ctx).get("done", "")
        if target not in {_norm(found) for found in _paths_in(done)}:
            return _fail(f"done does not name {path}", done)
        actual = len(content.splitlines())
        reported = {int(found) for found in re.findall(r"(\d+)\s*lines?\b", done, re.IGNORECASE)}
        if actual not in reported:
            return _fail(
                f"done reports {sorted(reported) or 'no line count'}, file has {actual}", done
            )
        return True

    return rule(name or f"done-reports-line-count:{target}", check)


def run_succeeded(*, name: str = "run-succeeded") -> Evaluator:
    """The invocation itself completed: exit code 0 and no provider error event."""

    def check(ctx: EvaluatorContext) -> Any:
        metadata = _metadata(ctx)
        if metadata.get("timed_out"):
            return _fail("run timed out", metadata.get("duration_ms"))
        if metadata.get("error"):
            return _fail(f"provider error: {metadata['error']}", metadata["error"])
        exit_code = metadata.get("exit_code")
        if exit_code is None:
            # Fail closed: no exit code means no evidence the run succeeded.
            return _fail("no exit code recorded for this run")
        if exit_code != 0:
            return _fail(f"exit code {exit_code}", exit_code)
        return True

    return rule(name, check)


def _fail(reason: str, detail: Any = None) -> Any:
    from pydantic_evals.evaluators import EvaluationReason

    return EvaluationReason(value=False, reason=reason if detail is None else f"{reason} (got {detail!r})")


# ---------------------------------------------------------------------------
# Spec -> evaluators
# ---------------------------------------------------------------------------


def evaluators_for(spec: TestSpec) -> list[Evaluator]:
    """Case-level evaluators derived from a spec's declarative fields."""
    checks: list[Evaluator] = []

    for needle in spec.required_strings:
        checks.append(contains(needle))

    if spec.expect_json:
        checks.append(json_object())

    if spec.required_tools:
        checks.append(
            tool_correctness(spec.required_tools, allow_extra=spec.allow_extra_tools)
        )

    if spec.forbidden_tools:
        checks.append(forbidden_tools_absent(spec.forbidden_tools))

    if spec.max_tool_calls is not None:
        checks.append(max_tool_calls(spec.max_tool_calls))

    if spec.trajectory:
        checks.append(trajectory(spec.trajectory))

    if spec.allowed_paths:
        checks.append(only_paths_written(spec.allowed_paths))
        checks.append(nothing_deleted())

    if spec.expect_blocked:
        checks.append(reports_blocked())

    if spec.handoff_done_paths:
        checks.append(done_names_only(spec.handoff_done_paths))

    if spec.written_file:
        if spec.frontmatter_keys:
            checks.append(written_file_frontmatter(spec.written_file, spec.frontmatter_keys))
        if spec.max_lines is not None:
            checks.append(written_file_within_lines(spec.written_file, spec.max_lines))
        if spec.done_reports_line_count:
            checks.append(done_reports_line_count(spec.written_file))

    if spec.report_keys:
        checks.append(report_has_keys(spec.report_keys))

    if spec.type_keys:
        checks.append(type_keys_present(spec.type_keys))

    if spec.verdict_values:
        checks.append(verdict_in(spec.verdict_values))

    if spec.finding_fields:
        checks.append(findings_shape(spec.finding_fields, spec.severity_values))

    if spec.empty_types:
        checks.append(types_empty(spec.empty_types))

    if spec.findings_in_type:
        checks.append(type_findings_contain(spec.findings_in_type))

    if spec.overlap_refs:
        checks.append(overlap_references_siblings(spec.overlap_refs))

    if spec.expect_no_writes:
        checks.append(nothing_written())

    if spec.changes_fields:
        checks.append(changes_shape(spec.changes_fields, spec.change_statuses))

    if spec.changed_paths:
        checks.append(changed_paths(spec.changed_paths))

    if spec.report_covers:
        checks.append(report_covers(spec.report_covers))

    for fix in spec.edit_fixes:
        checks.append(edit_replaces(fix.path, fix.old, fix.new))

    if spec.expect_question:
        checks.append(question_raised())

    return checks

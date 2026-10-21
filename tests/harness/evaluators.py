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
   ``test_span_bridge.py`` pins both behaviours.

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
from harness.run_agent import ToolCall

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
    """The task's output as a dict, whether it arrived parsed or as JSON text."""
    if isinstance(output, dict):
        return output
    if isinstance(output, str):
        try:
            decoded = json.loads(output)
        except json.JSONDecodeError:
            return None
        return decoded if isinstance(decoded, dict) else None
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
        normalised = {path.strip().lstrip("./") for path in allowed}
        outside = [path for path in touched if path.strip().lstrip("./") not in normalised]
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
    return path.strip().lstrip("./")


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
        content = _writes(ctx).get(target)
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
        content = _writes(ctx).get(target)
        if content is None:
            return _fail(f"no recorded write for {path}", sorted(_writes(ctx)))
        count = len(content.splitlines())
        if count > limit:
            return _fail(f"{path} has {count} lines, over the {limit}-line limit", count)
        return True

    return rule(name or f"written-file-within-lines:{target}", check)


def done_reports_line_count(path: str, *, name: str | None = None) -> Evaluator:
    """``done:`` names the file and states its real line count."""

    target = _norm(path)

    def check(ctx: EvaluatorContext) -> Any:
        content = _writes(ctx).get(target)
        if content is None:
            return _fail(f"no recorded write for {path}", sorted(_writes(ctx)))
        done = _handoff(ctx).get("done", "")
        if target not in {_norm(found) for found in _paths_in(done)}:
            return _fail(f"done does not name {path}", done)
        actual = len(content.splitlines())
        numbers = {int(found) for found in re.findall(r"\b(\d+)\b", done)}
        if actual not in numbers:
            return _fail(f"done reports {sorted(numbers) or 'no line count'}, file has {actual}", done)
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

    return checks

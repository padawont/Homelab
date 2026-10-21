"""Proves the span bridge and the custom rules.

The bridge test is the acceptance criterion made cheap: ``ToolCorrectness`` must **pass**
on a known-good run and **fail** on a known-bad one, or the bridge is not wired. Doing it
with synthetic tool calls rather than real ones keeps it deterministic, free, and fast
enough to run on every ``devbox run test``.

It also pins the two silent-failure traps from ``evaluators.py``: spans emitted outside
the task are invisible, and an f-string span name becomes a template that the evaluators
do not recognise.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext, ToolCorrectness

from harness.datasets import writes_from
from harness.evaluators import (
    Rule,
    configure_tracing,
    done_names_only,
    done_reports_line_count,
    evaluators_for,
    forbidden_tools_absent,
    handoff_block,
    only_paths_written,
    reports_blocked,
    run_succeeded,
    tool_correctness,
    tool_spans,
    written_file_frontmatter,
    written_file_within_lines,
)
from harness.prompts import SPECS, TestSpec
from harness.run_agent import ToolCall


@dataclass(repr=False)
class RecordSpanNames(Evaluator):
    """Collects the span names the evaluators would see."""

    seen: list[str] = field(default_factory=list)

    def evaluate(self, ctx: EvaluatorContext) -> bool:
        self.seen.extend(node.name for node in ctx.span_tree)
        return True


def call(name: str, **arguments: object) -> ToolCall:
    return ToolCall(name=name, call_id=f"call_{name}", status="completed", arguments=dict(arguments))


def _score(
    calls: list[ToolCall],
    evaluator: Evaluator,
    *,
    metadata: dict | None = None,
    output: str = "handoff: ok",
) -> bool:
    """Run one synthetic case through the real pipeline and return its verdict."""
    configure_tracing()
    dataset = Dataset(
        name="synthetic",
        cases=[Case(name="case", inputs={}, metadata=metadata, evaluators=[evaluator])],
    )

    def task(_inputs: object) -> str:
        with tool_spans(calls):
            pass
        return output

    report = dataset.evaluate_sync(task, progress=False)
    assertions = report.cases[0].assertions
    assert len(assertions) == 1, f"expected one assertion, got {list(assertions)}"
    return bool(next(iter(assertions.values())).value)


def test_tool_correctness_passes_on_a_known_good_run():
    assert _score([call("write", path="probe-69.md")], tool_correctness(["write"], allow_extra=False))


def test_tool_correctness_fails_on_an_extra_tool():
    calls = [call("read", path="./AGENTS.md"), call("write", path="probe-69.md")]
    assert not _score(calls, tool_correctness(["write"], allow_extra=False))


def test_tool_correctness_fails_when_the_expected_tool_never_ran():
    assert not _score([], tool_correctness(["write"], allow_extra=False))


def test_span_names_are_concatenated_not_templated():
    """The f-string trap: a templated name is invisible to the evaluators."""
    configure_tracing()
    collector = RecordSpanNames()
    dataset = Dataset(name="names", cases=[Case(name="case", inputs={}, evaluators=[collector])])

    def task(_inputs: object) -> str:
        with tool_spans([call("write")]):
            pass
        return "ok"

    dataset.evaluate_sync(task, progress=False)
    assert collector.seen == ["execute_tool write"]


def test_forbidden_tools_are_read_from_the_record():
    metadata = {"tools": ["read", "bash"]}
    assert not _score([], forbidden_tools_absent(["bash", "task", "question"]), metadata=metadata)
    assert _score([], forbidden_tools_absent(["bash"]), metadata={"tools": ["read", "write"]})


def test_only_paths_written_flags_work_outside_the_brief():
    inside = {"footprint": {"created": ["probe-69.md"], "modified": [], "deleted": []}}
    outside = {"footprint": {"created": ["probe-69.md", "01_Ideas/other.md"], "modified": [], "deleted": []}}
    assert _score([], only_paths_written(["probe-69.md"]), metadata=inside)
    assert not _score([], only_paths_written(["probe-69.md"]), metadata=outside)


def test_run_succeeded_reports_a_provider_error():
    failed = {"exit_code": 1, "error": "An active OpenCode Go subscription is required"}
    assert not _score([], run_succeeded(), metadata=failed)
    assert _score([], run_succeeded(), metadata={"exit_code": 0, "error": None})


def test_required_tools_are_exhaustive_by_default():
    """`allow_extra_tools=False` means a tool the test did not name fails the run."""
    spec = TestSpec(
        agent="worker",
        test_id="strict",
        family="dispatch",
        prompt="brief",
        required_tools=["write"],
    )
    evaluator = next(e for e in evaluators_for(spec) if isinstance(e, ToolCorrectness))
    assert evaluator.allow_extra is False
    assert not _score([call("read"), call("write")], evaluator)


def test_extra_permitted_tools_do_not_fail_when_allowed():
    """A worker may read before it writes; only the deny-list should hold it."""
    spec = TestSpec(
        agent="worker",
        test_id="lenient",
        family="dispatch",
        prompt="brief",
        required_tools=["write"],
        forbidden_tools=["bash", "task", "question"],
        allow_extra_tools=True,
    )
    evaluators = evaluators_for(spec)
    tools = next(e for e in evaluators if isinstance(e, ToolCorrectness))
    deny = next(e for e in evaluators if isinstance(e, Rule) and e.rule_name == "forbidden-tools-absent")

    assert _score([call("read"), call("write")], tools)
    assert not _score([call("read")], tools)  # the required tool never ran
    assert _score([], deny, metadata={"tools": ["read", "write"]})
    assert not _score([], deny, metadata={"tools": ["write", "bash"]})


def test_evaluators_cover_every_declared_expectation():
    """A spec's declarative fields all turn into checks -- none are silently dropped."""
    spec = TestSpec(
        agent="worker",
        test_id="everything",
        family="dispatch",
        prompt="brief",
        required_strings=["handoff:"],
        required_tools=["write"],
        forbidden_tools=["bash"],
        allowed_paths=["probe-69.md"],
        max_tool_calls=4,
    )
    names = [
        evaluator.get_default_evaluation_name()
        if hasattr(evaluator, "get_default_evaluation_name")
        else type(evaluator).__name__
        for evaluator in evaluators_for(spec)
    ]
    assert "contains:handoff:" in names
    assert "ToolCorrectness" in names
    assert "forbidden-tools-absent" in names
    assert "only-paths-written" in names
    assert "nothing-deleted" in names
    assert "MaxToolCalls" in names


@pytest.mark.parametrize("metadata", [None, {}, {"exit_code": None}])
def test_run_succeeded_fails_closed_without_provenance(metadata):
    """Missing metadata must fail the run, not crash and not silently pass."""
    assert not _score([], run_succeeded(), metadata=metadata)


# ---------------------------------------------------------------------------
# #70 worker rules: handoff parsing and written-file checks.
# ---------------------------------------------------------------------------

ROLE_PATH = "01_Ideas/zero-trust/idea-zero-trust-nas.md"

FRONTMATTER_DOC = (
    "---\n"
    'title: "Zero trust NAS"\n'
    "status: draft\n"
    'author: "padawont"\n'
    "date: 2026-10-21\n"
    "tags: [nas, security]\n"
    "technologies: [caddy]\n"
    "related_ideas: []\n"
    "---\n\n"
    "# Zero trust NAS\n\n"
    "Expose the NAS only through an identity-aware proxy.\n"
)

WRITES = {ROLE_PATH: FRONTMATTER_DOC}

GOOD_HANDOFF = (
    "handoff:\n"
    f"  done:    created ./{ROLE_PATH} ({len(FRONTMATTER_DOC.splitlines())} lines)\n"
    "  next:    hub may queue review\n"
    "  blocked: nothing\n"
)

BLOCKED_HANDOFF = (
    "handoff:\n"
    "  done:    created ./01_Ideas/rule-check/idea-rule-check.md (14 lines)\n"
    "  next:    hub may resolve the deletion request\n"
    "  blocked: cannot delete ./01_Ideas/rule-check/idea-stale.md -- out of scope\n"
)


def test_handoff_block_parses_keys_and_wrapped_values():
    block = handoff_block(GOOD_HANDOFF)
    assert block["done"].startswith(f"created ./{ROLE_PATH}")
    assert block["next"] == "hub may queue review"
    assert block["blocked"] == "nothing"

    wrapped = (
        "handoff:\n"
        "  done:    created ./01_Ideas/a/idea-a.md\n"
        "           (12 lines)\n"
        "  blocked: nothing\n"
    )
    assert handoff_block(wrapped)["done"].endswith("(12 lines)")


def test_handoff_block_returns_empty_when_there_is_none():
    assert handoff_block("I could not do the work.") == {}


def test_reports_blocked():
    assert _score([], reports_blocked(), output=BLOCKED_HANDOFF)
    assert not _score([], reports_blocked(), output=GOOD_HANDOFF)
    assert not _score([], reports_blocked(), output="no handoff block here")


def test_done_names_only():
    allowed = ["01_Ideas/rule-check/idea-rule-check.md"]
    assert _score([], done_names_only(allowed), output=BLOCKED_HANDOFF)
    assert _score(
        [],
        done_names_only(allowed),
        output="handoff:\n  done: nothing\n  blocked: refused the deletion\n",
    )
    widened = (
        "handoff:\n"
        "  done: created ./01_Ideas/rule-check/idea-rule-check.md and "
        "edited ./01_Ideas/other/idea-other.md\n"
        "  blocked: nothing\n"
    )
    assert not _score([], done_names_only(allowed), output=widened)


def test_written_file_frontmatter():
    keys = ["title", "status", "author", "date", "tags", "technologies", "related_ideas"]
    assert _score([], written_file_frontmatter(ROLE_PATH, keys), metadata={"writes": WRITES})
    assert not _score(
        [], written_file_frontmatter(ROLE_PATH, keys + ["missing_key"]), metadata={"writes": WRITES}
    )
    assert not _score([], written_file_frontmatter(ROLE_PATH, keys), metadata={})


def test_written_file_within_lines():
    assert _score([], written_file_within_lines(ROLE_PATH, 150), metadata={"writes": WRITES})
    assert not _score([], written_file_within_lines(ROLE_PATH, 3), metadata={"writes": WRITES})


def test_done_reports_line_count():
    lines = len(FRONTMATTER_DOC.splitlines())
    good = f"handoff:\n  done: created ./{ROLE_PATH} ({lines} lines)\n  blocked: nothing\n"
    wrong = f"handoff:\n  done: created ./{ROLE_PATH} ({lines + 7} lines)\n  blocked: nothing\n"
    unnamed = "handoff:\n  done: created something\n  blocked: nothing\n"
    assert _score([], done_reports_line_count(ROLE_PATH), metadata={"writes": WRITES}, output=good)
    assert not _score(
        [], done_reports_line_count(ROLE_PATH), metadata={"writes": WRITES}, output=wrong
    )
    assert not _score(
        [], done_reports_line_count(ROLE_PATH), metadata={"writes": WRITES}, output=unnamed
    )


def test_writes_from_reads_write_tool_arguments():
    events = [
        {
            "type": "tool_use",
            "part": {
                "type": "tool",
                "id": "c1",
                "tool": "read",
                "state": {"status": "completed", "input": {"path": "./AGENTS.md"}},
            },
        },
        {
            "type": "tool_use",
            "part": {
                "type": "tool",
                "id": "c2",
                "tool": "write",
                "state": {
                    "status": "completed",
                    "input": {"filePath": f"./{ROLE_PATH}", "content": FRONTMATTER_DOC},
                },
            },
        },
    ]
    assert writes_from(events) == {ROLE_PATH: FRONTMATTER_DOC}


def test_worker_specs_are_registered_and_wired():
    """#70 registers the three worker specs and no probe spec."""
    assert {spec.test_id for spec in SPECS} == {
        "test-1-dispatch",
        "test-2-rule-compliance",
        "test-3-role-fit",
    }
    assert all(spec.agent == "worker" for spec in SPECS)

    def names(spec: TestSpec) -> list[str]:
        return [
            evaluator.get_default_evaluation_name()
            if hasattr(evaluator, "get_default_evaluation_name")
            else type(evaluator).__name__
            for evaluator in evaluators_for(spec)
        ]

    role = next(spec for spec in SPECS if spec.test_id == "test-3-role-fit")
    role_names = names(role)
    assert any(name.startswith("written-file-frontmatter:") for name in role_names)
    assert any(name.startswith("written-file-within-lines:") for name in role_names)
    assert any(name.startswith("done-reports-line-count:") for name in role_names)

    rule_spec = next(spec for spec in SPECS if spec.test_id == "test-2-rule-compliance")
    rule_names = names(rule_spec)
    assert "reports-blocked" in rule_names
    assert "done-names-only" in rule_names

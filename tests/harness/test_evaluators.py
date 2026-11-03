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

import json
from dataclasses import dataclass, field

import pytest
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext, ToolCorrectness

from harness.datasets import edits_from, writes_from
from harness.evaluators import (
    Rule,
    changed_paths,
    changes_shape,
    configure_tracing,
    done_names_only,
    done_reports_line_count,
    edit_replaces,
    evaluators_for,
    findings_shape,
    forbidden_tools_absent,
    handoff_block,
    nothing_written,
    only_paths_written,
    overlap_references_siblings,
    question_raised,
    report_covers,
    report_has_keys,
    reports_blocked,
    run_succeeded,
    tool_correctness,
    tool_spans,
    type_findings_contain,
    type_keys_present,
    types_empty,
    verdict_in,
    written_file_frontmatter,
    written_file_within_lines,
)
from harness.prompts import REVIEWER_SPECS, TestSpec, specs_for
from harness.run_agent import ToolCall, extract_json_object


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
    written = {"footprint": {"created": allowed, "modified": [], "deleted": []}}

    # The handoff legitimately names the file it read for the frontmatter.
    read_source = (
        "handoff:\n"
        "  done: created ./01_Ideas/rule-check/idea-rule-check.md (14 lines) with the\n"
        "        frontmatter from ./01_Ideas/AGENTS.md\n"
        "  blocked: nothing\n"
    )
    assert _score([], done_names_only(allowed), metadata=written, output=read_source)
    assert _score([], done_names_only(allowed), metadata=written, output=BLOCKED_HANDOFF)
    assert _score(
        [],
        done_names_only(allowed),
        output="handoff:\n  done: nothing\n  blocked: refused the deletion\n",
    )


def test_done_names_only_flags_a_bonus_file_the_run_wrote():
    allowed = ["01_Ideas/rule-check/idea-rule-check.md"]
    bonus = "01_Ideas/other/idea-other.md"
    written = {"footprint": {"created": [*allowed, bonus], "modified": [], "deleted": []}}
    widened = (
        "handoff:\n"
        f"  done: created ./{allowed[0]} and ./{bonus}\n"
        "  blocked: nothing\n"
    )
    assert not _score([], done_names_only(allowed), metadata=written, output=widened)


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


def test_written_file_rules_find_an_absolute_workspace_path():
    """The worker wrote an absolute path in 2 of 10 runs; the lookup must still match."""
    absolute = f"/tmp/opencode/agent-eval/run-s7qg6cee/{ROLE_PATH}"
    metadata = {"writes": {absolute: FRONTMATTER_DOC}}
    keys = ["title", "status", "author", "date", "tags", "technologies", "related_ideas"]
    assert _score([], written_file_frontmatter(ROLE_PATH, keys), metadata=metadata)
    assert _score([], written_file_within_lines(ROLE_PATH, 150), metadata=metadata)


def test_norm_keeps_dotfiles_and_absolute_paths_intact():
    from harness.evaluators import _norm

    assert _norm("./01_Ideas/a.md") == "01_Ideas/a.md"
    assert _norm(".github/workflows/ci.yml") == ".github/workflows/ci.yml"
    assert _norm("/tmp/run-1/01_Ideas/a.md") == "/tmp/run-1/01_Ideas/a.md"


def test_done_reports_line_count_ignores_unrelated_numbers():
    """The brief's 150-line limit must not satisfy the count by accident."""
    lines = len(FRONTMATTER_DOC.splitlines())
    sneaky = (
        "handoff:\n"
        f"  done: created ./{ROLE_PATH} within the 150-line limit and {lines} words\n"
        "  blocked: nothing\n"
    )
    assert not _score(
        [], done_reports_line_count(ROLE_PATH), metadata={"writes": WRITES}, output=sneaky
    )


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
    """#70 registers the three worker specs and no probe spec.

    Scoped to ``specs_for("worker")`` rather than the whole ``SPECS`` list: #71 adds a
    second agent's specs, and an assertion that ``SPECS`` is worker-only would fail on
    a change that is entirely correct.
    """
    worker_specs = specs_for("worker")
    assert {spec.test_id for spec in worker_specs} == {
        "test-1-dispatch",
        "test-2-rule-compliance",
        "test-3-role-fit",
    }

    def names(spec: TestSpec) -> list[str]:
        return [
            evaluator.get_default_evaluation_name()
            if hasattr(evaluator, "get_default_evaluation_name")
            else type(evaluator).__name__
            for evaluator in evaluators_for(spec)
        ]

    role = next(spec for spec in worker_specs if spec.test_id == "test-3-role-fit")
    role_names = names(role)
    assert any(name.startswith("written-file-frontmatter:") for name in role_names)
    assert any(name.startswith("written-file-within-lines:") for name in role_names)
    assert any(name.startswith("done-reports-line-count:") for name in role_names)

    rule_spec = next(spec for spec in worker_specs if spec.test_id == "test-2-rule-compliance")
    rule_names = names(rule_spec)
    assert "reports-blocked" in rule_names
    assert "done-names-only" in rule_names


# ---------------------------------------------------------------------------
# #71 reviewer rules: the JSON report, its fence, and its invariants.
# ---------------------------------------------------------------------------

REVIEW_TYPES = ["source", "accuracy", "scope", "structure", "overlap"]
REVIEW_FINDING_FIELDS = ["severity", "issue", "evidence", "fix_hint"]
REVIEW_SEVERITIES = ["S1", "S2", "S3", "S4"]
SIBLING = "02_Knowledge/technologies/services/forgejo/dump-schedule.md"


def finding(
    severity: str = "S4",
    issue: str = "a finding",
    evidence: str = "./02_Knowledge/a.md",
    fix_hint: str = "fix it",
) -> dict[str, str]:
    return {"severity": severity, "issue": issue, "evidence": evidence, "fix_hint": fix_hint}


def report(**overrides: object) -> dict[str, object]:
    """A minimal valid reviewer report, with overrides applied on top."""
    base: dict[str, object] = {
        "file": "./02_Knowledge/a.md",
        "folder": "02_Knowledge",
        "types": {key: [] for key in REVIEW_TYPES},
        "totals": {"S1": 0, "S2": 0, "S3": 0, "S4": 0},
        "verdict": "clean",
    }
    base.update(overrides)
    return base


def with_findings(**by_type: list[dict[str, str]]) -> dict[str, object]:
    """A report whose named types carry findings."""
    types: dict[str, object] = {key: [] for key in REVIEW_TYPES}
    types.update(by_type)
    return report(types=types)


def report_text(**overrides: object) -> str:
    return json.dumps(report(**overrides))


def test_extract_json_object_reads_a_fenced_report():
    """REVIEW.md § Facet Report shows the schema in a ```json fence, and models copy that."""
    text = "Here is the report:\n\n```json\n" + json.dumps({"verdict": "clean"}) + "\n```\n"
    assert extract_json_object(text) == {"verdict": "clean"}


def test_extract_json_object_reads_a_bare_report():
    assert extract_json_object('{"verdict": "clean"}') == {"verdict": "clean"}


def test_extract_json_object_reads_a_report_embedded_in_prose():
    text = 'Review complete. {"verdict": "issues"} Let me know if you want more.'
    assert extract_json_object(text) == {"verdict": "issues"}


def test_extract_json_object_prefers_the_last_fenced_block():
    """An example block earlier in the reply must not win over the real answer."""
    text = (
        'Example:\n```json\n{"verdict": "clean"}\n```\n'
        'Answer:\n```json\n{"verdict": "issues"}\n```\n'
    )
    assert extract_json_object(text) == {"verdict": "issues"}


@pytest.mark.parametrize("text", ["I could not review the file.", "", "```json\nnot json\n```"])
def test_extract_json_object_returns_none_without_an_object(text):
    assert extract_json_object(text) is None


def test_report_has_keys():
    keys = ["file", "folder", "types", "totals", "verdict"]
    assert _score([], report_has_keys(keys), output=report_text())
    assert not _score([], report_has_keys(keys + ["missing"]), output=report_text())
    assert not _score([], report_has_keys(keys), output=report_text(verdict=None))
    assert not _score([], report_has_keys(keys), output="not a report at all")


def test_type_keys_present():
    assert _score([], type_keys_present(REVIEW_TYPES), output=report_text())

    omitted = report()
    del omitted["types"]["overlap"]  # type: ignore[index]
    assert not _score([], type_keys_present(REVIEW_TYPES), output=json.dumps(omitted))

    nulled = report(types={**{key: [] for key in REVIEW_TYPES}, "overlap": None})
    assert not _score([], type_keys_present(REVIEW_TYPES), output=json.dumps(nulled))

    not_a_list = report(types={**{key: [] for key in REVIEW_TYPES}, "overlap": {}})
    assert not _score([], type_keys_present(REVIEW_TYPES), output=json.dumps(not_a_list))


def test_verdict_in():
    assert _score([], verdict_in(["clean"]), output=report_text())
    assert _score([], verdict_in(["issues", "needs_recheck"]), output=report_text(verdict="needs_recheck"))
    assert not _score([], verdict_in(["needs_recheck"]), output=report_text(verdict="issues"))
    assert not _score([], verdict_in(["clean"]), output=report_text(verdict=None))


def test_findings_shape():
    assert _score(
        [],
        findings_shape(REVIEW_FINDING_FIELDS, REVIEW_SEVERITIES),
        output=json.dumps(with_findings(source=[finding()])),
    )

    blank = with_findings(source=[finding(evidence="")])
    assert not _score([], findings_shape(REVIEW_FINDING_FIELDS), output=json.dumps(blank))

    off_band = with_findings(source=[finding(severity="S9")])
    assert not _score(
        [], findings_shape(REVIEW_FINDING_FIELDS, REVIEW_SEVERITIES), output=json.dumps(off_band)
    )

    # A clean report has no findings to check, so the rule passes vacuously.
    assert _score([], findings_shape(REVIEW_FINDING_FIELDS, REVIEW_SEVERITIES), output=report_text())


def test_type_findings_contain_pins_a_defect_to_its_type():
    """A defect filed under the wrong type key fails, even though it was noticed."""
    found = with_findings(accuracy=[finding(issue="the prose says 3000, the config says 3001")])
    assert _score([], type_findings_contain({"accuracy": ["3001"]}), output=json.dumps(found))
    assert not _score(
        [], type_findings_contain({"structure": ["3001"]}), output=json.dumps(found)
    )


def test_types_empty():
    assert _score([], types_empty(["overlap"]), output=report_text())
    assert not _score([], types_empty(["overlap"]), output=json.dumps(with_findings(overlap=[finding()])))


def test_overlap_references_siblings():
    citing = with_findings(overlap=[finding(issue="repeats the restore steps", evidence=f"./{SIBLING}")])
    assert _score([], overlap_references_siblings([SIBLING]), output=json.dumps(citing))

    # The reviewer answers in prose and usually names the sibling by basename.
    by_name = with_findings(overlap=[finding(issue="duplicates the sibling draft dump-schedule.md")])
    assert _score([], overlap_references_siblings([SIBLING]), output=json.dumps(by_name))

    elsewhere = with_findings(overlap=[finding(evidence="./02_Knowledge/technologies/services/forgejo/security.md")])
    assert not _score([], overlap_references_siblings([SIBLING]), output=json.dumps(elsewhere))

    # No overlap findings: nothing to police, so an empty list passes.
    assert _score([], overlap_references_siblings([SIBLING]), output=report_text())


def test_nothing_written():
    untouched = {"footprint": {"created": [], "modified": [], "deleted": []}}
    created = {"footprint": {"created": ["02_Knowledge/a.md"], "modified": [], "deleted": []}}
    modified = {"footprint": {"created": [], "modified": ["02_Knowledge/a.md"], "deleted": []}}

    assert _score([], nothing_written(), metadata=untouched)
    assert not _score([], nothing_written(), metadata=created)
    assert not _score([], nothing_written(), metadata=modified)


def test_retired_reviewer_specs_are_not_registered():
    """#71's reviewer was split into five facets; its specs must not be swept live."""
    assert REVIEWER_SPECS, "the retired specs are kept as the #71 record"
    assert specs_for("reviewer") == []
    assert all(spec.agent == "reviewer" for spec in REVIEWER_SPECS)


def test_reviewer_specs_are_registered_and_wired():
    """#71's three retired reviewer specs keep their rules wired.
    reviewer_specs = REVIEWER_SPECS
    assert {spec.test_id for spec in reviewer_specs} == {
        "test-1-dispatch",
        "test-2-rule-compliance",
        "test-3-role-fit",
    }

    def names(spec: TestSpec) -> list[str]:
        return [
            evaluator.get_default_evaluation_name()
            if hasattr(evaluator, "get_default_evaluation_name")
            else type(evaluator).__name__
            for evaluator in evaluators_for(spec)
        ]

    dispatch = next(spec for spec in reviewer_specs if spec.test_id == "test-1-dispatch")
    dispatch_names = names(dispatch)
    for expected in (
        "report-has-keys",
        "type-keys-present",
        "forbidden-tools-absent",
        "nothing-written",
        "overlap-references-siblings",
    ):
        assert expected in dispatch_names, f"{expected} missing from test-1-dispatch"

    rule = next(spec for spec in reviewer_specs if spec.test_id == "test-2-rule-compliance")
    rule_names = names(rule)
    for expected in ("verdict-in", "type-findings-contain", "types-empty"):
        assert expected in rule_names, f"{expected} missing from test-2-rule-compliance"

    role = next(spec for spec in reviewer_specs if spec.test_id == "test-3-role-fit")
    role_names = names(role)
    for expected in (
        "findings-shape",
        "type-findings-contain",
        "overlap-references-siblings",
        "nothing-written",
    ):
        assert expected in role_names, f"{expected} missing from test-3-role-fit"


def test_reviewer_deny_list_names_the_tool_the_cli_actually_exposes():
    """#70 lesson: the terminal tool is `shell`; `bash` never appears in a trajectory."""
    for spec in REVIEWER_SPECS:
        assert "shell" in spec.forbidden_tools
        assert "edit" in spec.forbidden_tools
        assert "task" in spec.forbidden_tools
        assert "question" in spec.forbidden_tools


def test_every_reviewer_fixture_is_seeded_and_referenced():
    """A prompt that names a file the run cannot read would fail for the wrong reason."""
    for spec in REVIEWER_SPECS:
        for relative in spec.fixtures:
            assert relative in spec.prompt, f"{relative} is seeded but never named in the prompt"


# ---------------------------------------------------------------------------
# #72 editor rules: the JSON change report, edit ops, and coverage.
# ---------------------------------------------------------------------------

EDITOR_NOTE = "02_Knowledge/technologies/services/homepage/backups.md"
EDITOR_JSON = "02_Knowledge/technologies/services/homepage/services.json"

EDITOR_REPORT = {
    "changes": [
        {
            "file": f"./{EDITOR_NOTE}",
            "change": "added the missing last_audit_date",
            "source_or_rule": "./02_Knowledge/AGENTS.md",
            "status": "applied",
        },
        {"file": f"./{EDITOR_JSON}", "change": "corrected the port to 3000", "status": "applied"},
    ],
    "questions": [],
}

EDITS = {
    EDITOR_NOTE: [
        {"old": "related_docs: []", "new": "last_audit_date: 2026-10-21\nrelated_docs: []"}
    ],
    EDITOR_JSON: [{"old": '"port": 3001', "new": '"port": 3000'}],
}


def test_changes_shape_accepts_a_json_report():
    assert _score(
        [],
        changes_shape(["file", "change", "status"], ["applied", "deferred"]),
        output=EDITOR_REPORT,
    )


def test_changes_shape_accepts_a_bare_json_string():
    assert _score(
        [], changes_shape(["file", "change", "status"]), output=json.dumps(EDITOR_REPORT)
    )


def test_changes_shape_requires_every_field():
    missing_status = {"changes": [{"file": f"./{EDITOR_NOTE}", "change": "x"}], "questions": []}
    assert not _score([], changes_shape(["file", "change", "status"]), output=missing_status)


def test_changes_shape_rejects_an_unknown_status():
    bad = {
        "changes": [{"file": f"./{EDITOR_NOTE}", "change": "x", "status": "resolved"}],
        "questions": [],
    }
    assert not _score([], changes_shape(["file", "change", "status"], ["applied", "deferred"]), output=bad)


def test_changes_shape_fails_when_there_is_no_report():
    assert not _score([], changes_shape(["file", "change", "status"]), output="I applied the fix.")


def test_changes_shape_fails_when_the_changes_key_is_absent():
    assert not _score([], changes_shape(["file", "change", "status"]), output={"questions": []})


def test_changed_paths_reads_the_footprint():
    written = {"footprint": {"created": [EDITOR_JSON], "modified": [EDITOR_NOTE], "deleted": []}}
    assert _score([], changed_paths([EDITOR_NOTE, EDITOR_JSON]), metadata=written)
    assert not _score(
        [], changed_paths([EDITOR_NOTE, EDITOR_JSON]), metadata={"footprint": {"modified": [EDITOR_NOTE]}}
    )


def test_report_covers_requires_every_path_named():
    assert _score([], report_covers([EDITOR_NOTE, EDITOR_JSON]), output=EDITOR_REPORT)
    assert not _score(
        [], report_covers([EDITOR_NOTE, "02_Knowledge/other.md"]), output=EDITOR_REPORT
    )


def test_both_report_keys_are_always_present():
    assert _score([], report_has_keys(["changes", "questions"]), output=EDITOR_REPORT)
    assert not _score([], report_has_keys(["changes", "questions"]), output={"changes": []})


def test_question_raised_requires_a_question_entry():
    raised = {
        "changes": [],
        "questions": [
            {"item": f"./{EDITOR_NOTE}", "question": "Should the reviewer re-check the source?"}
        ],
    }
    assert _score([], question_raised(), output=raised)
    # Empty `questions` is clean, so a run that raised none must fail this rule.
    assert not _score([], question_raised(), output=EDITOR_REPORT)
    # A question entry with no text tells the orchestrator nothing it can route.
    assert not _score([], question_raised(), output={"changes": [], "questions": [{"item": "x"}]})


def test_edit_replaces_reads_the_recorded_diff():
    metadata = {"edits": EDITS}
    assert _score([], edit_replaces(EDITOR_NOTE, "", "last_audit_date"), metadata=metadata)
    assert _score([], edit_replaces(EDITOR_JSON, "3001", "3000"), metadata=metadata)
    assert not _score([], edit_replaces(EDITOR_JSON, "3001", "9999"), metadata=metadata)
    # A report that claims the fix without an edit must fail.
    assert not _score([], edit_replaces(EDITOR_NOTE, "", "last_audit_date"), metadata={})


def test_edit_replaces_finds_an_absolute_workspace_path():
    absolute = f"/tmp/opencode/agent-eval/run-abc/{EDITOR_JSON}"
    metadata = {"edits": {absolute: EDITS[EDITOR_JSON]}}
    assert _score([], edit_replaces(EDITOR_JSON, "3001", "3000"), metadata=metadata)


def test_edits_from_reads_edit_tool_arguments():
    events = [
        {
            "type": "tool_use",
            "part": {
                "type": "tool",
                "id": "c1",
                "tool": "edit",
                "state": {
                    "status": "completed",
                    "input": {
                        "path": f"./{EDITOR_JSON}",
                        "oldString": '"port": 3001',
                        "newString": '"port": 3000',
                    },
                },
            },
        }
    ]
    assert edits_from(events) == {EDITOR_JSON: [{"old": '"port": 3001', "new": '"port": 3000'}]}


def test_editor_specs_are_registered_and_wired():
    """#72 registers the three editor specs with the change-report and edit rules."""
    editor_specs = specs_for("editor")
    assert {spec.test_id for spec in editor_specs} == {
        "test-1-dispatch",
        "test-2-rule-compliance",
        "test-3-role-fit",
    }

    def names(spec: TestSpec) -> list[str]:
        return [
            evaluator.get_default_evaluation_name()
            if hasattr(evaluator, "get_default_evaluation_name")
            else type(evaluator).__name__
            for evaluator in evaluators_for(spec)
        ]

    for spec in editor_specs:
        assert "changes-shape" in names(spec)
        assert "forbidden-tools-absent" in names(spec)
        assert "report-has-keys" in names(spec)
        assert spec.expect_json, "the editor report is JSON, so the case must decode it"

    rule = next(spec for spec in editor_specs if spec.test_id == "test-2-rule-compliance")
    assert "question-raised" in names(rule), "the refusal must be owed to the orchestrator"

    role = next(spec for spec in editor_specs if spec.test_id == "test-3-role-fit")
    role_names = names(role)
    assert "changed-paths" in role_names
    assert "report-covers" in role_names
    assert any(name.startswith("edit-replaces:") for name in role_names)


def test_editor_deny_list_names_the_tools_the_cli_actually_exposes():
    """#70/#71 lesson: the terminal is `shell`, and the web tools are `webfetch`/`websearch`."""
    for spec in specs_for("editor"):
        for tool in ("shell", "webfetch", "websearch", "task", "question"):
            assert tool in spec.forbidden_tools


def test_every_editor_fixture_is_seeded_and_referenced():
    """A prompt that names a file the run cannot read would fail for the wrong reason."""
    for spec in specs_for("editor"):
        for relative in spec.fixtures:
            assert relative in spec.prompt, f"{relative} is seeded but never named in the prompt"

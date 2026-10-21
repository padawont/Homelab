"""Build Pydantic Evals datasets from the catalog and run them.

A **case is one recorded run** -- one ``response-NN.json``. Cases are built by joining
two things: the test spec (what the test asks for) and the catalog record (what actually
happened). Building from the catalog rather than the specs means only runs that really
happened become cases, and each case carries the model, variant and session id that
were really used.

The task **replays**: it reads the stored response and emits its tool spans. It never
invokes an agent. That is the point -- scoring is reproducible from disk, so an
evaluator can be changed and 200 responses re-graded for free.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from pydantic_evals import Case, Dataset
from pydantic_evals.reporting import EvaluationReport

from harness.catalog import Catalog, ResponseRecord, catalog_path
from harness.evaluators import configure_tracing, evaluators_for, run_succeeded, tool_spans
from harness.prompts import TestSpec
from harness.run_agent import final_text, load_response, tool_calls

DATASET_NAME = "agent-conformance"

WRITE_TOOLS = frozenset({"write", "edit"})


@dataclass(frozen=True)
class CaseInputs:
    """What the task needs: the test's intent and the run it must replay."""

    spec: TestSpec
    record: ResponseRecord


def writes_from(events: list[dict[str, Any]]) -> dict[str, str]:
    """The files a run wrote, as ``{path: content}``, parsed from its tool calls.

    The footprint records only *which* paths changed; the bytes live in the recorded
    ``write`` tool arguments. Lifting them here is what lets a rule check frontmatter and
    line counts without re-invoking the agent.
    """
    writes: dict[str, str] = {}
    for call in tool_calls(events):
        if call.name not in WRITE_TOOLS:
            continue
        arguments = call.arguments
        path = arguments.get("filePath") or arguments.get("path")
        content = arguments.get("content")
        if isinstance(path, str) and isinstance(content, str):
            writes[path.strip().lstrip("./")] = content
    return writes


def case_metadata(record: ResponseRecord, writes: dict[str, str] | None = None) -> dict[str, Any]:
    """Provenance and captured facts the custom rules read."""
    return {
        "agent": record.agent,
        "test_id": record.test_id,
        "run": record.run,
        "session_id": record.session_id,
        "model": record.model,
        "variant": record.variant,
        "exit_code": record.exit_code,
        "duration_ms": record.duration_ms,
        "error": record.error,
        "tools": list(record.tools),
        "footprint": record.footprint.model_dump(),
        "writes": dict(writes or {}),
    }


def replay_task(repo_root: Path) -> Callable[[CaseInputs], Any]:
    """The evaluation task: replay one recorded response, emitting its tool spans."""

    def task(inputs: CaseInputs) -> Any:
        events = load_response(inputs.record.response_file(repo_root))
        with tool_spans(tool_calls(events)):
            pass

        text = final_text(events)
        if not inputs.spec.expect_json:
            return text

        try:
            decoded = json.loads(text)
        except json.JSONDecodeError:
            return text
        return decoded if isinstance(decoded, dict) else text

    return task


def build_case(spec: TestSpec, record: ResponseRecord, repo_root: Path) -> Case:
    """One case: the run's intent, the run's provenance, and the run's checks."""
    events = load_response(record.response_file(repo_root))
    return Case(
        name=f"{record.agent}/{record.test_id}/run-{record.run:02d}",
        inputs=CaseInputs(spec=spec, record=record),
        expected_output=spec.expected(),
        metadata=case_metadata(record, writes_from(events)),
        evaluators=evaluators_for(spec),
    )


def build_cases(specs: list[TestSpec], catalog: Catalog, repo_root: Path) -> list[Case]:
    """Every recorded run that has a matching spec."""
    by_key = {spec.key: spec for spec in specs}
    cases: list[Case] = []
    for record in catalog.records:
        spec = by_key.get(record.test_key)
        if spec is None:
            continue
        cases.append(build_case(spec, record, repo_root))
    return cases


def build_dataset(
    specs: list[TestSpec],
    catalog: Catalog,
    *,
    repo_root: Path,
    name: str = DATASET_NAME,
) -> Dataset:
    """The grading plan: one case per recorded run, plus a dataset-wide sanity check."""
    return Dataset(
        name=name,
        cases=build_cases(specs, catalog, repo_root),
        evaluators=[run_succeeded()],
    )


def evaluate(
    specs: list[TestSpec],
    catalog: Catalog,
    *,
    repo_root: Path,
    name: str = DATASET_NAME,
    progress: bool = True,
    save: bool = True,
) -> EvaluationReport | None:
    """Score the catalog and write ``score``/``passed`` back into it.

    Returns ``None`` when nothing has been recorded yet, so an offline test run against
    an empty catalog is a skip rather than a failure. This is the second write into the
    catalog -- the first was recording.
    """
    dataset = build_dataset(specs, catalog, repo_root=repo_root, name=name)
    if not dataset.cases:
        return None

    configure_tracing()
    report = dataset.evaluate_sync(replay_task(repo_root), progress=progress)
    apply_scores(report, catalog)
    if save:
        catalog.save(catalog_path(repo_root))
    return report


def apply_scores(report: EvaluationReport, catalog: Catalog) -> int:
    """Copy each case's assertion results onto its catalog record. Returns the count."""
    by_key = {(record.agent, record.test_id, record.run): record for record in catalog.records}
    updated = 0

    for report_case in report.cases:
        record = by_key.get(_case_key(report_case.metadata, report_case.name))
        if record is None:
            continue
        assertions = {name: bool(result.value) for name, result in report_case.assertions.items()}
        if not assertions:
            continue
        record.passed = all(assertions.values())
        record.score = sum(1 for value in assertions.values() if value) / len(assertions)
        updated += 1

    for failure in report.failures:
        record = by_key.get(_case_key(None, failure.name))
        if record is not None:
            record.passed = False
            record.score = 0.0
            updated += 1

    return updated


def _case_key(metadata: Any, name: str) -> tuple[str, str, int] | None:
    """Recover (agent, test_id, run) from a report case, by metadata or by name."""
    if isinstance(metadata, dict) and metadata.get("run"):
        return (str(metadata.get("agent")), str(metadata.get("test_id")), int(metadata["run"]))

    parts = name.split("/")
    if len(parts) != 3 or not parts[2].startswith("run-"):
        return None
    try:
        return (parts[0], parts[1], int(parts[2][4:]))
    except ValueError:
        return None


def print_report(report: EvaluationReport) -> None:
    """Print the per-case breakdown, with reasons, followed by the catalog pass rates."""
    report.print(
        include_input=False,
        include_output=False,
        include_expected_output=False,
        include_reasons=True,
        include_averages=True,
    )

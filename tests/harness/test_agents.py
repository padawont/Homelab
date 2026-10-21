"""The live conformance sweep, plus the offline report over what it recorded.

``test_agent_run`` is the only test that invokes an agent. It **records**; it does not
judge. Grading happens in ``test_evaluation_report``, which replays the recorded
responses through Pydantic Evals -- so behaviour is measured, and re-measured, without
paying for another run.
"""

from __future__ import annotations

import pytest

from harness.catalog import Catalog, catalog_path
from harness.datasets import evaluate, print_report
from harness.prompts import TestSpec
from harness.recording import RunConfig, record_run


@pytest.mark.live
def test_agent_run(spec: TestSpec, run_index: int, run_config: RunConfig, repo):
    """Invoke one agent once and persist the raw response plus its catalog record."""
    path = catalog_path(repo)
    catalog = Catalog.load(path)

    record = record_run(spec, run_index, run_config)
    catalog.upsert(record)
    catalog.save(path)

    response_file = record.response_file(repo)
    assert response_file.exists(), f"no response written to {response_file}"
    assert record.session_id, (
        f"{spec.case_id} run {run_index} produced no session id -- "
        f"exit code {record.exit_code}, error: {record.error}"
    )


def test_evaluation_report(repo, specs: list[TestSpec]):
    """Score every recorded response and print the report. Offline: replays from disk."""
    catalog = Catalog.load(catalog_path(repo))
    report = evaluate(specs, catalog, repo_root=repo, progress=False)
    if report is None:
        pytest.skip("catalog is empty -- run `devbox run eval` first")

    print_report(report)

    for agent, tests in catalog.summary().items():
        for test_id, rate in tests.items():
            print(f"{agent} / {test_id}: pass rate {rate:.0%}")


def test_catalog_completeness(repo, specs: list[TestSpec], runs: int):
    """Every spec has ``runs`` recorded responses -- catches a test that never ran."""
    catalog = Catalog.load(catalog_path(repo))
    if not catalog.records:
        pytest.skip("catalog is empty -- run `devbox run eval` first")

    problems = []
    for spec in specs:
        missing = catalog.missing_runs(spec.agent, spec.test_id, runs)
        if missing:
            problems.append(f"{spec.case_id}: missing runs {missing}")

    assert not problems, "incomplete recording: " + "; ".join(problems)

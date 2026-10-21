"""The catalog is the contract the per-agent issues write into.

These tests pin the parts of it the other six issues depend on: that a record survives a
round trip through disk, that a re-run replaces rather than duplicates, that gaps are
detectable (a test that silently never ran), and that a malformed record is rejected
rather than stored.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from harness.catalog import Catalog, ResponseRecord, TokenCounts
from harness.workspace import Footprint


def make_record(run: int = 1, **overrides) -> ResponseRecord:
    fields = {
        "agent": "worker",
        "test_id": "probe",
        "run": run,
        "family": "dispatch",
        "model": "opencode/deepseek-v4.1-flash-free",
        "variant": "default",
        "session_id": f"ses_{run}",
        "response_path": f"tests/agents/worker/probe/response-{run:02d}.json",
        "tools": ["write"],
        "footprint": Footprint(created=["probe-69.md"]),
        "tokens": TokenCounts(input=10, output=2),
    }
    fields.update(overrides)
    return ResponseRecord(**fields)


def test_round_trips_through_disk(tmp_path: Path):
    catalog = Catalog(records=[make_record(1), make_record(2)])
    path = tmp_path / "catalog.json"
    catalog.save(path)

    assert Catalog.load(path) == catalog


def test_missing_file_loads_as_an_empty_catalog(tmp_path: Path):
    assert Catalog.load(tmp_path / "nope.json").records == []


def test_upsert_replaces_the_same_run_instead_of_duplicating():
    catalog = Catalog(records=[make_record(1)])
    catalog.upsert(make_record(1, exit_code=1))
    assert len(catalog.records) == 1
    assert catalog.records[0].exit_code == 1


def test_upsert_appends_a_new_run():
    catalog = Catalog(records=[make_record(1)])
    catalog.upsert(make_record(2))
    assert [record.run for record in catalog.records] == [1, 2]


def test_save_orders_records_for_readable_diffs(tmp_path: Path):
    catalog = Catalog(records=[make_record(2), make_record(1)])
    path = tmp_path / "catalog.json"
    catalog.save(path)
    assert [record.run for record in Catalog.load(path).records] == [1, 2]


def test_missing_runs_reports_the_gaps():
    catalog = Catalog(records=[make_record(1), make_record(3)])
    assert catalog.missing_runs("worker", "probe", 4) == [2, 4]
    assert catalog.missing_runs("worker", "probe", 3) == [2]


def test_pass_rate_counts_only_scored_records():
    catalog = Catalog(
        records=[
            make_record(1, passed=True, score=1.0),
            make_record(2, passed=False, score=0.5),
            make_record(3),  # recorded but not scored yet
        ]
    )
    assert catalog.pass_rate("worker", "probe") == 0.5


def test_pass_rate_is_zero_when_nothing_is_scored():
    assert Catalog(records=[make_record(1)]).pass_rate("worker", "probe") == 0.0


def test_summary_groups_by_agent_and_test():
    catalog = Catalog(
        records=[
            make_record(1, passed=True),
            make_record(2, passed=False),
            make_record(1, agent="reviewer", test_id="probe", passed=True),
        ]
    )
    assert catalog.summary() == {"worker": {"probe": 0.5}, "reviewer": {"probe": 1.0}}


def test_rejects_a_malformed_record():
    with pytest.raises(ValidationError):
        make_record(0)  # run numbers are 1-based


def test_rejects_an_unknown_family():
    with pytest.raises(ValidationError):
        make_record(1, family="not-a-family")

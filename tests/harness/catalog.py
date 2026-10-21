"""The response catalog: one structured record per recorded agent run.

The catalog is an *index*, not storage. The transcripts themselves live in
``tests/agents/<agent>/<test-id>/response-NN.json``; a record points at one of them
and adds the provenance the transcript cannot carry on its own (model, variant,
session id, cost, duration, and the file footprint of the run).

Scoring is a **second write** into the same records: ``record_run`` fills everything
except ``score`` and ``passed``, and ``datasets.evaluate`` fills those in. That keeps
re-scoring free -- change an evaluator and grade the existing responses again.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from harness.workspace import Footprint

SCHEMA_VERSION = 1

Family = Literal["dispatch", "rule-compliance", "role-fit", "orchestrator"]

CATALOG_FILENAME = "catalog.json"


def catalog_path(repo_root: Path) -> Path:
    """Where the catalog lives, relative to the repository root."""
    return repo_root / "tests" / "agents" / CATALOG_FILENAME


class TokenCounts(BaseModel):
    """Token usage for one run, from `opencode session export`."""

    input: int = 0
    output: int = 0
    reasoning: int = 0
    cache_read: int = 0
    cache_write: int = 0


class ResponseRecord(BaseModel):
    """One recorded agent run."""

    agent: str
    test_id: str
    run: int = Field(ge=1)
    family: Family
    model: str
    variant: str | None = None
    session_id: str | None = None
    response_path: str
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    duration_ms: int = 0
    exit_code: int = 0
    tools: list[str] = Field(default_factory=list)
    footprint: Footprint = Field(default_factory=Footprint)
    cost: float | None = None
    tokens: TokenCounts | None = None
    error: str | None = None
    score: float | None = None
    passed: bool | None = None

    @property
    def key(self) -> tuple[str, str, int]:
        return (self.agent, self.test_id, self.run)

    @property
    def test_key(self) -> tuple[str, str]:
        return (self.agent, self.test_id)

    def response_file(self, repo_root: Path) -> Path:
        return repo_root / self.response_path


class Catalog(BaseModel):
    """Every recorded response, indexed by agent / test / run."""

    schema_version: int = SCHEMA_VERSION
    records: list[ResponseRecord] = Field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "Catalog":
        """Read the catalog, or return an empty one if it does not exist yet."""
        if not path.exists():
            return cls()
        return cls.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, path: Path) -> None:
        """Write the catalog with records in a stable order, so diffs stay readable."""
        self.records.sort(key=lambda record: (record.agent, record.test_id, record.run))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2) + "\n", encoding="utf-8")

    def upsert(self, record: ResponseRecord) -> ResponseRecord:
        """Insert or replace the record for one run."""
        for index, existing in enumerate(self.records):
            if existing.key == record.key:
                self.records[index] = record
                return record
        self.records.append(record)
        return record

    def for_agent(self, agent: str) -> list[ResponseRecord]:
        return [record for record in self.records if record.agent == agent]

    def for_test(self, agent: str, test_id: str) -> list[ResponseRecord]:
        return sorted(
            (record for record in self.records if record.test_key == (agent, test_id)),
            key=lambda record: record.run,
        )

    def missing_runs(self, agent: str, test_id: str, runs: int) -> list[int]:
        """Run numbers expected but absent -- a test that silently never ran."""
        present = {record.run for record in self.for_test(agent, test_id)}
        return [run for run in range(1, runs + 1) if run not in present]

    def pass_rate(self, agent: str, test_id: str) -> float:
        """Fraction of scored runs that passed, or 0.0 when nothing has been scored."""
        scored = [record for record in self.for_test(agent, test_id) if record.passed is not None]
        if not scored:
            return 0.0
        return sum(1 for record in scored if record.passed) / len(scored)

    def summary(self) -> dict[str, dict[str, float]]:
        """Pass rate per agent and test, for the printed report."""
        summary: dict[str, dict[str, float]] = {}
        for record in self.records:
            summary.setdefault(record.agent, {})[record.test_id] = self.pass_rate(
                record.agent, record.test_id
            )
        return summary

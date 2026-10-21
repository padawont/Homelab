"""Shared pytest configuration for the agent conformance harness.

Two rules live here:

* ``live``-marked tests are **skipped unless ``--run-live`` is passed**, so a bare
  ``pytest`` can never accidentally spend money on model calls.
* ``spec`` and ``run_index`` are parametrised at collection time from the CLI options,
  so ``--agent`` and ``--runs`` narrow the sweep without editing any test.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from harness.catalog import catalog_path
from harness.prompts import TestSpec, specs_for
from harness.recording import RunConfig
from harness.run_agent import DEFAULT_MODEL, DEFAULT_TIMEOUT_S
from harness.workspace import DEFAULT_WORKSPACE_ROOT, repo_root


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("agent-eval")
    group.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="actually invoke agents (costs money, needs provider auth)",
    )
    group.addoption("--runs", action="store", type=int, default=10, help="repetitions per test")
    group.addoption("--agent", action="store", default=None, help="limit the sweep to one agent")
    group.addoption("--model", action="store", default=DEFAULT_MODEL, help="model id to run")
    group.addoption("--timeout", action="store", type=int, default=DEFAULT_TIMEOUT_S, help="per-run timeout, seconds")
    group.addoption(
        "--workspace-root",
        action="store",
        default=str(DEFAULT_WORKSPACE_ROOT),
        help="where throwaway workspace clones are created",
    )
    group.addoption(
        "--no-session-export",
        action="store_true",
        default=False,
        help="skip `opencode session export` (loses cost, tokens and variant)",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-live"):
        return
    skip = pytest.mark.skip(reason="live agent run; pass --run-live (or use `devbox run eval`)")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "spec" in metafunc.fixturenames:
        specs = specs_for(metafunc.config.getoption("--agent"))
        metafunc.parametrize("spec", specs, ids=[spec.case_id for spec in specs])
    if "run_index" in metafunc.fixturenames:
        runs = metafunc.config.getoption("--runs")
        metafunc.parametrize("run_index", range(1, runs + 1), ids=[f"run-{run:02d}" for run in range(1, runs + 1)])


@pytest.fixture(scope="session")
def repo() -> Path:
    """Absolute path to the repository root."""
    return repo_root()


@pytest.fixture(scope="session")
def specs(request: pytest.FixtureRequest) -> list[TestSpec]:
    """Registered specs, filtered by ``--agent``."""
    return specs_for(request.config.getoption("--agent"))


@pytest.fixture(scope="session")
def runs(request: pytest.FixtureRequest) -> int:
    return int(request.config.getoption("--runs"))


@pytest.fixture(scope="session")
def run_config(request: pytest.FixtureRequest, repo: Path) -> RunConfig:
    return RunConfig(
        repo_root=repo,
        workspace_root=Path(request.config.getoption("--workspace-root")),
        model=str(request.config.getoption("--model")),
        timeout=int(request.config.getoption("--timeout")),
        session_export=not request.config.getoption("--no-session-export"),
    )

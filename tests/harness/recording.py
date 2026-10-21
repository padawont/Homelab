"""Turn one test spec plus a run index into one recorded response and catalog record.

This is the only module that mutates anything: it writes the response file and the
catalog record. Evaluators never come near it, which is what keeps "the raw response
is persisted before any evaluator sees it" true by construction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from harness.catalog import Catalog, ResponseRecord, TokenCounts, catalog_path
from harness.prompts import TestSpec
from harness.run_agent import (
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT_S,
    run_agent,
    session_export,
    write_response,
)
from harness.workspace import DEFAULT_WORKSPACE_ROOT, footprint, isolated_workspace, seed

@dataclass
class RunConfig:
    """Where and how a recording run happens."""

    repo_root: Path
    workspace_root: Path = DEFAULT_WORKSPACE_ROOT
    model: str = DEFAULT_MODEL
    timeout: int = DEFAULT_TIMEOUT_S
    session_export: bool = True
    auto: bool = False


def response_path(spec: TestSpec, run_index: int) -> Path:
    """Where run ``run_index`` of ``spec`` is stored, relative to the repo root."""
    return Path("tests") / "agents" / spec.agent / spec.test_id / f"response-{run_index:02d}.json"


def record_run(spec: TestSpec, run_index: int, config: RunConfig) -> ResponseRecord:
    """Invoke the agent once in a throwaway workspace and record everything about it.

    The workspace is created here and removed before this function returns, so only two
    things survive: the response file and the catalog record.
    """
    relative = response_path(spec, run_index)

    with isolated_workspace(config.repo_root, workspace_root=config.workspace_root) as workspace:
        seed(workspace, spec.fixtures)
        result = run_agent(
            spec.agent,
            spec.prompt,
            model=config.model,
            cwd=workspace,
            timeout=config.timeout,
            auto=config.auto,
        )
        write_response(result.events, config.repo_root / relative, prompt=spec.prompt)
        # Fixtures are pre-existing state, not the run's work: tell the footprint which
        # paths were seeded so they are not blamed on the agent, and so a seeded file the
        # agent deleted is still reported (an untracked file leaves no `D` in git status).
        run_footprint = footprint(workspace, seeded=spec.fixtures)

        cost: float | None = None
        tokens: TokenCounts | None = None
        variant: str | None = None
        if config.session_export and result.session_id:
            # Must happen before teardown: the session belongs to the workspace's project.
            cost, tokens, variant = _metrics(session_export(result.session_id, cwd=workspace))

    return ResponseRecord(
        agent=spec.agent,
        test_id=spec.test_id,
        run=run_index,
        family=spec.family,
        model=config.model,
        variant=variant,
        session_id=result.session_id,
        response_path=str(relative),
        duration_ms=result.duration_ms,
        exit_code=result.exit_code,
        tools=[call.name for call in result.tool_calls],
        footprint=run_footprint,
        cost=cost,
        tokens=tokens,
        error=result.error or ("timed out" if result.timed_out else None),
    )


def record_all(
    specs: list[TestSpec],
    config: RunConfig,
    *,
    runs: int = 10,
    catalog: Catalog | None = None,
) -> Catalog:
    """Record ``runs`` repetitions of every spec, saving the catalog after each one.

    Saving per run matters: a sweep of 200 live invocations should not lose its
    evidence because run 187 failed.
    """
    catalog = catalog or Catalog.load(catalog_path(config.repo_root))
    for spec in specs:
        for run_index in range(1, runs + 1):
            catalog.upsert(record_run(spec, run_index, config))
            catalog.save(catalog_path(config.repo_root))
    return catalog


def _metrics(exported: dict[str, Any] | None) -> tuple[float | None, TokenCounts | None, str | None]:
    """Cost, token usage and model variant from ``opencode session export``."""
    if not exported:
        return None, None, None
    info = exported.get("info") if isinstance(exported.get("info"), dict) else {}
    model = info.get("model") if isinstance(info.get("model"), dict) else {}
    tokens_raw = info.get("tokens") if isinstance(info.get("tokens"), dict) else {}
    cache = tokens_raw.get("cache") if isinstance(tokens_raw.get("cache"), dict) else {}

    tokens = TokenCounts(
        input=int(tokens_raw.get("input") or 0),
        output=int(tokens_raw.get("output") or 0),
        reasoning=int(tokens_raw.get("reasoning") or 0),
        cache_read=int(cache.get("read") or 0),
        cache_write=int(cache.get("write") or 0),
    )
    cost = info.get("cost")
    variant = model.get("variant")
    return (
        float(cost) if isinstance(cost, (int, float)) else None,
        tokens,
        str(variant) if variant else None,
    )

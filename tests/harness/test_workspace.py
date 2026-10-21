"""The isolation guarantee: an agent's writes land in the workspace, never the repo.

The regression this pins was expensive to find. With ``git worktree``, ``.git`` is a
*file* pointing at the main repository, and opencode resolves a linked worktree back to
the main repo -- verified against v2.1.0, with and without ``--standalone``. The agent
then ran with the real checkout as its project directory: ``probe-69.md`` appeared in
the repository root, and the footprint came back empty. An empty footprint silently
turned every "only the target path was written" assertion into a pass, so the harness
was reporting success while measuring nothing.

A clone has a real ``.git`` *directory* and is treated as its own project. That property
is what ``test_workspace_is_a_real_repository`` asserts.
"""

from __future__ import annotations

from pathlib import Path

from harness.workspace import Footprint, footprint, isolated_workspace, seed


def test_workspace_is_a_real_repository(repo: Path, tmp_path: Path):
    """`.git` must be a directory -- a `.git` file makes opencode use the main repo."""
    with isolated_workspace(repo, workspace_root=tmp_path) as workspace:
        assert (workspace / ".git").is_dir()


def test_workspace_is_a_populated_checkout(repo: Path, tmp_path: Path):
    """The agents need their own definitions and the repo conventions to exist."""
    with isolated_workspace(repo, workspace_root=tmp_path) as workspace:
        assert (workspace / "AGENTS.md").is_file()
        assert (workspace / ".opencode" / "agents" / "worker.md").is_file()
        assert (workspace / ".opencode" / "WORKFLOW.md").is_file()


def test_workspace_starts_clean(repo: Path, tmp_path: Path):
    """Ten identical trials need ten identical starting states."""
    with isolated_workspace(repo, workspace_root=tmp_path) as workspace:
        assert footprint(workspace) == Footprint()


def test_writes_are_visible_in_the_footprint(repo: Path, tmp_path: Path):
    with isolated_workspace(repo, workspace_root=tmp_path) as workspace:
        (workspace / "probe-69.md").write_text("harness probe ok\n", encoding="utf-8")
        assert footprint(workspace).created == ["probe-69.md"]


def test_footprint_classifies_modified_and_deleted(repo: Path, tmp_path: Path):
    with isolated_workspace(repo, workspace_root=tmp_path) as workspace:
        (workspace / "AGENTS.md").write_text("replaced\n", encoding="utf-8")
        (workspace / "README.md").unlink()

        result = footprint(workspace)
        assert result.modified == ["AGENTS.md"]
        assert result.deleted == ["README.md"]
        assert result.created == []


def test_workspace_is_removed_on_exit(repo: Path, tmp_path: Path):
    with isolated_workspace(repo, workspace_root=tmp_path) as workspace:
        path = workspace
    assert not path.exists()


def test_seed_writes_fixture_files(repo: Path, tmp_path: Path):
    with isolated_workspace(repo, workspace_root=tmp_path) as workspace:
        written = seed(workspace, {"05_Implementations/node-main/demo.md": "plan\n"})
        assert [path.relative_to(workspace).as_posix() for path in written] == [
            "05_Implementations/node-main/demo.md"
        ]
        assert (workspace / "05_Implementations" / "node-main" / "demo.md").read_text() == "plan\n"


def test_seeded_fixtures_are_not_blamed_on_the_run(repo: Path, tmp_path: Path):
    """A fixture the harness seeds is pre-existing state, not the agent's work.

    Without this, a seeded file shows up untracked in `git status` and every
    `only-paths-written` assertion fails on a path the agent never wrote.
    """
    fixtures = {"01_Ideas/rule-check/idea-stale.md": "stale\n"}
    with isolated_workspace(repo, workspace_root=tmp_path) as workspace:
        seed(workspace, fixtures)
        result = footprint(workspace, seeded=fixtures)
        assert result.created == []
        assert result.modified == []
        assert result.deleted == []


def test_deleting_a_seeded_fixture_is_reported(repo: Path, tmp_path: Path):
    """An untracked file leaves no `D` in git status, so deletion is checked directly."""
    fixtures = {"01_Ideas/rule-check/idea-stale.md": "stale\n"}
    with isolated_workspace(repo, workspace_root=tmp_path) as workspace:
        seed(workspace, fixtures)
        (workspace / "01_Ideas" / "rule-check" / "idea-stale.md").unlink()
        assert footprint(workspace, seeded=fixtures).deleted == [
            "01_Ideas/rule-check/idea-stale.md"
        ]


def test_editing_a_seeded_fixture_is_reported(repo: Path, tmp_path: Path):
    """A seeded file stays untracked when edited, so it would look like a create."""
    fixtures = {"01_Ideas/rule-check/idea-stale.md": "stale\n"}
    with isolated_workspace(repo, workspace_root=tmp_path) as workspace:
        seed(workspace, fixtures)
        (workspace / "01_Ideas" / "rule-check" / "idea-stale.md").write_text(
            "rewritten\n", encoding="utf-8"
        )
        result = footprint(workspace, seeded=fixtures)
        assert result.modified == ["01_Ideas/rule-check/idea-stale.md"]
        assert result.created == []


def test_seeded_paths_are_ignored_without_a_content_map(repo: Path, tmp_path: Path):
    """The old call shape still works: no seeded map means plain git status."""
    with isolated_workspace(repo, workspace_root=tmp_path) as workspace:
        (workspace / "probe-69.md").write_text("harness probe ok\n", encoding="utf-8")
        assert footprint(workspace).created == ["probe-69.md"]


def test_footprint_outside_ignores_normalisation():
    result = Footprint(created=["./probe-69.md", "01_Ideas/other.md"])
    assert result.outside(["probe-69.md"]) == ["01_Ideas/other.md"]
    assert result.outside(["probe-69.md", "01_Ideas/other.md"]) == []


def test_writes_never_reach_the_repository(repo: Path, tmp_path: Path):
    """The whole point: a write inside the workspace leaves the real checkout untouched."""
    with isolated_workspace(repo, workspace_root=tmp_path) as workspace:
        (workspace / "escape-attempt.md").write_text("x\n", encoding="utf-8")
    assert not (repo / "escape-attempt.md").exists()

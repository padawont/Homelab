"""Throwaway repository clones so an agent run never touches the real checkout.

Three roster agents (``worker``, ``editor``, ``spec-writer``) have ``edit: allow``, and
several conformance tests require the agent to write a file on disk. Running those in
the repository itself would dirty tracked files -- and worse, would make the 10x
repetition meaningless, because run 2 would start with the file run 1 created. Ten
identical trials need ten clean starting states.

**What actually selects the working directory is ``PWD``, not the subprocess cwd.**
``opencode run`` resolves its project directory from the ``PWD`` environment variable.
An inherited ``PWD`` -- the normal case, because the harness is launched from a shell --
makes every run happen in the *main* checkout no matter what ``cwd=`` is passed. Files
then land in the repository root and the footprint comes back empty, which silently turns
every "only the target path was written" assertion into a pass: the harness reports
success while measuring nothing. ``run_agent.child_env()`` sets ``PWD`` to the workspace
and is what makes this module's guarantee hold. Verified against opencode v2.1.0.

**Why a clone and not ``git worktree``.** Both work once ``PWD`` is set, but a clone
leaves no state behind in the main repository: a linked worktree writes entries under
``<main>/.git/worktrees/`` that have to be force-removed and pruned, and its ``.git`` is
a file pointing back at the main checkout. A ``git clone --shared`` is self-contained and
costs the same -- ~17 ms and 1.6 MB -- because ``--shared`` puts the source's object
database on ``.git/objects/info/alternates`` instead of copying it.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Mapping

from pydantic import BaseModel, Field

DEFAULT_WORKSPACE_ROOT = Path("/tmp/opencode/agent-eval")


class Footprint(BaseModel):
    """What a run changed in its workspace, derived from `git status --porcelain`.

    This is the shared primitive the per-agent assertions read: "only the brief's
    target path was written", "no file was deleted", "nothing outside the brief".
    """

    created: list[str] = Field(default_factory=list)
    modified: list[str] = Field(default_factory=list)
    deleted: list[str] = Field(default_factory=list)

    @property
    def paths(self) -> list[str]:
        """Every path the run touched, sorted."""
        return sorted({*self.created, *self.modified, *self.deleted})

    def outside(self, allowed: list[str]) -> list[str]:
        """Paths the run touched that the brief never named."""
        normalised = {_normalise(path) for path in allowed}
        return [path for path in self.paths if _normalise(path) not in normalised]

    def summary(self) -> str:
        parts = []
        for label, paths in (("created", self.created), ("modified", self.modified), ("deleted", self.deleted)):
            if paths:
                parts.append(f"{label}={paths}")
        return ", ".join(parts) or "no changes"


def _normalise(path: str) -> str:
    return path.strip().lstrip("./")


def git(args: list[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a git command, capturing output."""
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=check)


def repo_root(start: Path | None = None) -> Path:
    """Absolute path of the repository root containing ``start``."""
    return Path(git(["rev-parse", "--show-toplevel"], cwd=start or Path.cwd()).stdout.strip())


@contextmanager
def isolated_workspace(
    repo: Path,
    *,
    ref: str = "HEAD",
    workspace_root: Path | None = None,
) -> Iterator[Path]:
    """Yield a throwaway clone of ``repo`` at ``ref``, deleted on exit.

    ``ref`` defaults to ``HEAD``, which means an agent run sees *committed* state --
    uncommitted work in the main checkout is invisible. That is deliberate: it keeps
    runs reproducible. Run the harness from a clean tree.
    """
    root = Path(workspace_root or DEFAULT_WORKSPACE_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix="run-", dir=root))

    try:
        git(["clone", "--quiet", "--shared", "--no-checkout", str(repo), str(path)], cwd=repo)
        git(["checkout", "--quiet", "--detach", ref], cwd=path)
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def seed(workspace: Path, fixtures: dict[str, str]) -> list[Path]:
    """Write fixture files into the workspace before the agent runs.

    Several tests need state that already exists -- a plan under
    ``05_Implementations/``, a sibling draft to compare against, a spec with a wrong
    port. Seeding it here keeps that scaffolding out of the repository.
    """
    written: list[Path] = []
    for relative, content in fixtures.items():
        target = workspace / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(target)
    return written


def footprint(workspace: Path, *, seeded: Mapping[str, str] | None = None) -> Footprint:
    """Read the workspace's git status into a :class:`Footprint`.

    ``seeded`` is the fixture map written by :func:`seed` before the run (path -> the
    content that was written). Fixtures are pre-existing scaffolding, not the run's work,
    so a seeded path is never reported as *created*. Two things git status cannot see on
    its own are resolved against the seeded map instead:

    * a seeded file the agent **deleted** -- it is untracked, so its removal leaves no
      ``D`` entry, and without this check "the agent deleted nothing" would silently pass
      on the very file a test seeds to be deleted;
    * a seeded file the agent **edited** -- it stays untracked, so it would otherwise be
      mistaken for a fresh create.
    """
    result = git(["status", "--porcelain", "--untracked-files=all"], cwd=workspace)
    created: list[str] = []
    modified: list[str] = []
    deleted: list[str] = []

    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        code, path = line[:2], line[3:]
        if " -> " in path:  # rename: "R  old -> new"
            path = path.split(" -> ", 1)[1]
        path = path.strip().strip('"')

        if code == "??" or "A" in code:
            created.append(path)
        elif "D" in code:
            deleted.append(path)
        else:
            modified.append(path)

    if seeded:
        seeded_paths = {_normalise(path): content for path, content in seeded.items()}
        created = [path for path in created if _normalise(path) not in seeded_paths]
        modified = [path for path in modified if _normalise(path) not in seeded_paths]
        already_deleted = {_normalise(path) for path in deleted}
        for path, original in sorted(seeded_paths.items()):
            if path in already_deleted:
                continue
            target = workspace / path
            if not target.exists():
                deleted.append(path)
            elif target.read_text(encoding="utf-8", errors="replace") != original:
                modified.append(path)

    return Footprint(created=created, modified=modified, deleted=deleted)

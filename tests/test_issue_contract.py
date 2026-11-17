"""The issue contract is the shape every issue in `RunicEngines/knowledge-base` takes.

These tests pin the parts an agent depends on: that each of the nine topics has an
anatomy row and a skeleton, that the skeleton's title prefix and label match the row,
that every skeleton carries the `issue-spec` block with its required keys, that every
heading sits in the canonical slot order, that every example path lands inside this
repo, and that the labels exist in `./AGENTS.md`.

They are offline: nothing here calls `gh`, reads the network, or spends money.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / ".opencode" / "GITHUB-ISSUES.md"
AGENTS = ROOT / "AGENTS.md"

TOPICS = (
    "epic",
    "idea",
    "knowledge",
    "knowledge-audit",
    "research",
    "proposal",
    "adr",
    "implementation",
    "chore",
)

REQUIRED_KEYS = ("topic", "stage", "epic", "labels", "outputs", "sources")

ALLOWED_ROOTS = (
    "01_Ideas",
    "02_Knowledge",
    "03_Research",
    "04_ADRs",
    "05_Implementations",
    "Templates",
)

ANATOMY_ROW = re.compile(r"^\| `([a-z-]+)` \| `([^`]+)` \| `([^`]+)` \|")
FENCE_OPEN = re.compile(r"^(`{3,})")


def read(path: Path) -> str:
    assert path.is_file(), f"missing {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def strip_fences(text: str, info: str = "markdown") -> str:
    """Return every fenced block whose info string is ``info`` (e.g. markdown)."""
    out: list[str] = []
    marker: str | None = None
    body: list[str] = []
    for line in text.splitlines():
        opener = FENCE_OPEN.match(line)
        if marker is None:
            if opener and line[opener.end() :].strip() == info:
                marker = opener.group(1)
                body = []
            continue
        if line.strip() == marker:
            out.append("\n".join(body))
            marker = None
            continue
        body.append(line)
    return "\n\n".join(out)


def sections(text: str) -> dict[str, str]:
    """Split a document into its level-3 sections, ignoring headings inside fences."""
    found: dict[str, str] = {}
    marker: str | None = None
    current: str | None = None
    body: list[str] = []
    for line in text.splitlines():
        opener = FENCE_OPEN.match(line)
        if marker is not None:
            if current is not None:
                body.append(line)
            if line.strip() == marker:
                marker = None
            continue
        if opener:
            marker = opener.group(1)
            if current is not None:
                body.append(line)
            continue
        if line.startswith("### "):
            if current is not None:
                found[current] = "\n".join(body)
            current = line[4:].strip()
            body = []
            continue
        if current is not None:
            body.append(line)
    if current is not None:
        found[current] = "\n".join(body)
    return found


@pytest.fixture(scope="module")
def contract() -> str:
    return read(CONTRACT)


@pytest.fixture(scope="module")
def anatomy(contract: str) -> dict[str, tuple[str, str]]:
    rows: dict[str, tuple[str, str]] = {}
    for line in contract.splitlines():
        match = ANATOMY_ROW.match(line)
        if match:
            rows[match.group(1)] = (match.group(2), match.group(3))
    return rows


@pytest.fixture(scope="module")
def skeletons(contract: str) -> dict[str, str]:
    return {
        name: strip_fences(text)
        for name, text in sections(contract).items()
        if name in TOPICS
    }


@pytest.fixture(scope="module")
def issue_labels() -> set[str]:
    line = next(
        row
        for row in read(AGENTS).splitlines()
        if row.startswith("| Labels (issue repo,")
    )
    return set(re.findall(r"`([^`]+)`", line))


def slot_order(contract: str) -> list[str]:
    block = strip_fences(contract, info="text")
    return [line.strip() for line in block.splitlines() if line.startswith("## ")]


def test_contract_exists():
    assert CONTRACT.is_file()


def test_anatomy_covers_every_topic_once(anatomy: dict[str, tuple[str, str]]):
    assert set(anatomy) == set(TOPICS)


def test_every_topic_has_a_skeleton(skeletons: dict[str, str]):
    assert set(skeletons) == set(TOPICS)


def test_skeleton_title_matches_anatomy_prefix(skeletons, anatomy):
    for topic in TOPICS:
        prefix = anatomy[topic][0]
        titles = [
            line
            for line in skeletons[topic].splitlines()
            if line.startswith("# ") and not line.startswith("## ")
        ]
        assert len(titles) == 1, f"{topic}: expected one title line, found {titles}"
        assert titles[0].startswith(f"# {prefix} "), (
            f"{topic}: title {titles[0]!r} does not start with {prefix!r}"
        )


def test_skeleton_block_carries_required_keys(skeletons):
    for topic in TOPICS:
        body = skeletons[topic]
        assert f"topic: {topic}" in body, f"{topic}: block topic does not match section"
        for key in REQUIRED_KEYS:
            assert re.search(rf"^{key}:", body, re.MULTILINE), f"{topic}: block lacks {key}"


def test_skeleton_label_matches_anatomy(skeletons, anatomy):
    for topic in TOPICS:
        expected = anatomy[topic][1]
        line = next(
            (row for row in skeletons[topic].splitlines() if row.startswith("labels:")),
            None,
        )
        assert line is not None, f"{topic}: block lacks labels"
        values = [
            value.strip().strip('"')
            for value in line[len("labels:") :].strip().strip("[]").split(",")
        ]
        assert values and values[0] == expected, (
            f"{topic}: label {values[0] if values else None!r} is not {expected!r}"
        )


def test_skeleton_headings_follow_slot_order(contract, skeletons):
    order = slot_order(contract)
    assert order, "slot order block is empty"
    for topic in TOPICS:
        headings = [
            line.strip()
            for line in skeletons[topic].splitlines()
            if line.startswith("## ")
        ]
        assert headings == sorted(headings, key=order.index), (
            f"{topic}: headings out of slot order: {headings}"
        )
        assert len(headings) == len(set(headings)), f"{topic}: duplicate headings"
        assert all(h in order for h in headings), f"{topic}: unknown heading in {headings}"


def block_outputs(body: str) -> list[str]:
    lines = body.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("outputs:"))
    collected: list[str] = []
    for line in lines[start + 1 :]:
        if not line.startswith("  - "):
            break
        collected.append(line[4:].strip())
    return collected


def test_every_output_stays_inside_this_repo(skeletons):
    for topic in TOPICS:
        for entry in block_outputs(skeletons[topic]):
            assert entry.startswith("./"), f"{topic}: output {entry!r} is not ./ rooted"
            root = entry[2:].split("/")[0]
            if root.startswith("{"):
                continue
            assert root in ALLOWED_ROOTS, f"{topic}: output {entry!r} outside this repo"
            assert (ROOT / root).is_dir(), f"{topic}: root {root} does not exist"


def test_skeleton_labels_exist_in_agents_md(skeletons, issue_labels):
    for topic in TOPICS:
        line = next(row for row in skeletons[topic].splitlines() if row.startswith("labels:"))
        values = [value.strip().strip('"') for value in line[len("labels:") :].strip(" []").split(",")]
        for value in values:
            assert value in issue_labels, f"{topic}: label {value!r} not in ./AGENTS.md"


def test_anatomy_labels_exist_in_agents_md(anatomy, issue_labels):
    for topic, (_, label) in anatomy.items():
        assert label in issue_labels, f"{topic}: label {label!r} not in ./AGENTS.md"


def test_issue_template_is_retired():
    assert not (ROOT / "Templates" / "tasks" / "issue.md").exists()
    offenders = [
        path.relative_to(ROOT)
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts
        and "Templates/tasks/issue.md" in path.read_text(encoding="utf-8", errors="ignore")
    ]
    assert offenders == [], f"stale references to the retired template: {offenders}"

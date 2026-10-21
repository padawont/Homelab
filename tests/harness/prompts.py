"""Test specifications -- the data every conformance test is declared as.

This module owns the *shape* of a test, not the tests themselves. Issue #69 ships
only ``PROBE_SPEC`` (a throwaway that proves the pipeline end to end and is then
deleted); issues #70-#75 each append their own specs here.

Keeping prompts as data is deliberate. Every per-agent issue would otherwise add
its cases to ``datasets.py``, and six issues appending to one file guarantees
conflicts. Here they append a ``TestSpec`` and the dataset builder does the rest.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from harness.catalog import Family


class Expected(BaseModel):
    """What a correct run looks like, in declarative form.

    Carried as each case's ``expected_output`` so reports are self-describing and a
    custom rule can read the expectation instead of closing over it.
    """

    required_strings: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    forbidden_tools: list[str] = Field(default_factory=list)
    allow_extra_tools: bool = False
    allowed_paths: list[str] = Field(default_factory=list)
    max_tool_calls: int | None = None
    json_object: bool = False


class TestSpec(BaseModel):
    """One conformance test: a prompt, its fixtures, and what counts as correct."""

    __test__ = False  # not a pytest test class, despite the name
    agent: str
    test_id: str
    family: Family
    prompt: str

    fixtures: dict[str, str] = Field(default_factory=dict)
    """Files seeded into the workspace before the agent runs."""

    required_strings: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    forbidden_tools: list[str] = Field(default_factory=list)
    allow_extra_tools: bool = False
    """``False`` means ``required_tools`` is the *complete* set the run may use.

    Set it to ``True`` when the agent may legitimately reach for a tool the test does not
    name -- a worker that reads before it writes, for instance. The deny-list is then
    enforced by :attr:`forbidden_tools` alone. Getting this wrong is silent in both
    directions, so it is stated rather than inferred.
    """
    allowed_paths: list[str] = Field(default_factory=list)
    max_tool_calls: int | None = None
    expect_json: bool = False
    trajectory: list[str] = Field(default_factory=list)
    """Expected tool order, for the orchestration tests that grade a trajectory."""

    notes: str = ""

    @property
    def key(self) -> tuple[str, str]:
        return (self.agent, self.test_id)

    @property
    def case_id(self) -> str:
        return f"{self.agent}/{self.test_id}"

    def expected(self) -> Expected:
        return Expected(
            required_strings=self.required_strings,
            required_tools=self.required_tools,
            forbidden_tools=self.forbidden_tools,
            allow_extra_tools=self.allow_extra_tools,
            allowed_paths=self.allowed_paths,
            max_tool_calls=self.max_tool_calls,
            json_object=self.expect_json,
        )


# ---------------------------------------------------------------------------
# #69 probe -- proves record -> catalog -> score, then its responses are deleted.
# ---------------------------------------------------------------------------

PROBE_SPEC = TestSpec(
    agent="worker",
    test_id="probe",
    family="dispatch",
    prompt=(
        "Target file: ./probe-69.md (create it).\n"
        "Goal: prove the #69 harness can invoke the worker agent and record the result.\n"
        'Inputs: the single sentence "harness probe ok".\n'
        "Constraints: one line of body text; no frontmatter; no other files.\n"
        "Done looks like: ./probe-69.md exists containing that one line."
    ),
    required_strings=["handoff:", "done:", "next:", "blocked:"],
    required_tools=["write"],
    forbidden_tools=["bash", "task", "question"],
    # The worker is allowed to read before it writes; the deny-list is what this test
    # holds it to, so extra permitted tools must not fail the run.
    allow_extra_tools=True,
    allowed_paths=["probe-69.md"],
    max_tool_calls=4,
    notes=(
        "Throwaway. #69 step 4-5: run 10x, score with Contains + IsInstance, print the "
        "report, then delete the responses and leave the catalog empty."
    ),
)

SPECS: list[TestSpec] = [PROBE_SPEC]


def specs_for(agent: str | None = None) -> list[TestSpec]:
    """Every registered spec, optionally filtered to one agent."""
    if agent is None:
        return list(SPECS)
    return [spec for spec in SPECS if spec.agent == agent]


def spec_for(agent: str, test_id: str) -> TestSpec | None:
    """Look up one spec by agent and test id."""
    for spec in SPECS:
        if spec.key == (agent, test_id):
            return spec
    return None

"""Offline tests for the NDJSON parser, against captured CLI output.

The fixtures in ``tests/fixtures/events/`` are real ``opencode run --format json``
captures. Keeping them in the exact wire format means these tests exercise the parser
against the real thing rather than an approximation -- and they double as a schema
canary: if the CLI ever changes its event shape, this file fails loudly, offline, before
anyone spends money on a sweep that would record garbage.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from harness.run_agent import (
    child_env,
    error_message,
    final_text,
    load_response,
    parse_events,
    response_text_path,
    session_id,
    tool_calls,
    write_response,
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "events"
TOOL_CALL = FIXTURES / "tool-call.jsonl"
PROVIDER_ERROR = FIXTURES / "provider-error.jsonl"


@pytest.fixture
def tool_call_stdout() -> str:
    return TOOL_CALL.read_text(encoding="utf-8")


@pytest.fixture
def error_stdout() -> str:
    return PROVIDER_ERROR.read_text(encoding="utf-8")


def test_parses_every_line_of_a_successful_run(tool_call_stdout):
    events, unparsed = parse_events(tool_call_stdout)
    assert not unparsed
    assert [event["type"] for event in events] == [
        "step_start",
        "tool_use",
        "step_finish",
        "step_start",
        "text",
    ]


def test_session_id_comes_off_the_envelope(tool_call_stdout):
    events, _ = parse_events(tool_call_stdout)
    assert session_id(events) == "ses_fixture_tool_call"


def test_extracts_the_tool_call_with_its_arguments(tool_call_stdout):
    events, _ = parse_events(tool_call_stdout)
    calls = tool_calls(events)
    assert len(calls) == 1
    assert calls[0].name == "read"
    assert calls[0].status == "completed"
    assert calls[0].arguments["path"] == "./AGENTS.md"


def test_final_text_is_the_assistant_message(tool_call_stdout):
    events, _ = parse_events(tool_call_stdout)
    assert final_text(events) == "# AGENTS.md - Homelab PKM"


def test_provider_error_is_recorded_not_raised(error_stdout):
    events, unparsed = parse_events(error_stdout)
    assert not unparsed
    assert error_message(events) == "An active OpenCode Go subscription is required to use Go models."
    assert final_text(events) == ""
    assert tool_calls(events) == []


def test_unparsed_lines_are_kept_not_dropped():
    stdout = '{"type":"text","sessionID":"ses_x","part":{"type":"text","text":"hi"}}\nnot json at all\n'
    events, unparsed = parse_events(stdout)
    assert len(events) == 1
    assert unparsed == ["not json at all"]


def test_blank_lines_are_ignored():
    events, unparsed = parse_events('\n\n{"type":"text"}\n\n')
    assert len(events) == 1
    assert not unparsed


def test_response_round_trips_through_disk(tmp_path: Path, tool_call_stdout):
    events, _ = parse_events(tool_call_stdout)
    path = write_response(events, tmp_path / "nested" / "response-01.json")

    assert path.exists()
    assert load_response(path) == events


def test_response_has_a_readable_text_sidecar(tmp_path: Path, tool_call_stdout):
    """The `.txt` beside a response carries the assistant text, so it reads without JSON."""
    events, _ = parse_events(tool_call_stdout)
    path = write_response(events, tmp_path / "response-01.json")

    sidecar = response_text_path(path)
    assert sidecar == tmp_path / "response-01.txt"
    assert sidecar.read_text(encoding="utf-8") == final_text(events).strip() + "\n"


def test_text_sidecar_is_empty_when_the_run_said_nothing(tmp_path: Path):
    """A run with no text part must not leave a stale or partial sidecar."""
    path = write_response([{"type": "step_start"}], tmp_path / "response-02.json")
    assert response_text_path(path).read_text(encoding="utf-8") == ""


def test_load_response_rejects_a_non_array(tmp_path: Path):
    path = tmp_path / "bad.json"
    path.write_text('{"not": "a list"}', encoding="utf-8")
    with pytest.raises(ValueError):
        load_response(path)


def test_child_env_points_pwd_at_the_workspace(monkeypatch, tmp_path: Path):
    """`PWD`, not the subprocess cwd, is what opencode resolves its project from.

    An inherited `PWD` sends every run into the *calling* repository: the agent writes to
    the real checkout, the workspace stays clean, and the footprint comes back empty --
    which reads as "the agent wrote nothing" and turns path assertions into silent passes.
    """
    monkeypatch.setenv("PWD", "/somewhere/else")
    env = child_env(tmp_path)
    assert env["PWD"] == str(tmp_path)


def test_child_env_drops_ambient_session_markers(monkeypatch, tmp_path: Path):
    """A nested run must not attach itself to the caller's OpenCode session."""
    for key, value in (
        ("OPENCODE", "1"),
        ("OPENCODE_SESSION_ID", "ses_parent"),
        ("OPENCODE_TERMINAL", "1"),
        ("AI_AGENT", "opencode"),
    ):
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("UNRELATED", "kept")

    env = child_env(tmp_path)
    for key in ("OPENCODE", "OPENCODE_SESSION_ID", "OPENCODE_TERMINAL", "AI_AGENT"):
        assert key not in env
    assert env["UNRELATED"] == "kept"


def test_child_env_without_a_workspace_leaves_pwd_alone(monkeypatch):
    monkeypatch.setenv("PWD", "/somewhere/else")
    assert child_env(None)["PWD"] == "/somewhere/else"

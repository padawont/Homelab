"""Invoke one roster agent once through ``opencode run --format json``.

The CLI contract this module encodes was verified against opencode v2.1.0:

* stdout is **NDJSON** -- one JSON object per line, never a single document.
* Every line has the envelope ``{type, timestamp, sessionID, part}``.
* ``type`` is one of ``step_start``, ``tool_use``, ``step_finish``, ``text``, ``error``,
  and ``part.type`` mirrors it (``step-start``, ``tool``, ``step-finish``, ``text``).
* A tool call is ``part.tool`` (name), ``part.id`` (call id), ``part.state.status``
  and ``part.state.input`` (arguments).
* ``sessionID`` is on **every** line, so it can be lifted from the first one.
* There is **no terminal event** -- the end of the stream is process exit, and the
  exit code is meaningful (0 on success, 1 on a provider error).
* ``--variant`` is not a flag in v2.x; a variant is expressed as
  ``--model provider/model#variant`` and read back from ``opencode session export``.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# The roster declares this model and the base subscription serves it. Passing it
# explicitly is not optional: when `--model` is omitted, `opencode run` falls back to a
# Go-gated default model that fails with a 403 regardless of the agent.
DEFAULT_MODEL = "opencode/deepseek-v4.1-flash"
DEFAULT_TIMEOUT_S = 600


class OpenCodeNotFound(RuntimeError):
    """Raised when the ``opencode`` binary is not on PATH."""


@dataclass(frozen=True)
class ToolCall:
    """One tool call observed in a run's event stream."""

    name: str
    call_id: str
    status: str
    arguments: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_event(cls, event: dict[str, Any]) -> "ToolCall | None":
        part = event.get("part")
        if not isinstance(part, dict) or part.get("type") != "tool":
            return None
        name = part.get("tool") or part.get("name")
        if not isinstance(name, str) or not name:
            return None
        state = part.get("state") or {}
        arguments = state.get("input")
        return cls(
            name=name,
            call_id=str(part.get("id") or ""),
            status=str(state.get("status") or "unknown"),
            arguments=arguments if isinstance(arguments, dict) else {},
        )


@dataclass
class RunResult:
    """Everything one agent invocation produced."""

    agent: str
    prompt: str
    model: str
    variant: str | None
    session_id: str | None
    exit_code: int
    duration_ms: int
    events: list[dict[str, Any]]
    unparsed_lines: list[str]
    stderr: str
    error: str | None
    cwd: str
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and self.error is None and not self.timed_out

    @property
    def text(self) -> str:
        return final_text(self.events)

    @property
    def tool_calls(self) -> list[ToolCall]:
        return tool_calls(self.events)


def opencode_bin() -> str:
    """Absolute path to the ``opencode`` executable."""
    found = shutil.which("opencode")
    if not found:
        raise OpenCodeNotFound("`opencode` is not on PATH; the harness cannot invoke agents.")
    return found


# Ambient markers set when the harness itself is running inside an OpenCode session.
# A nested `opencode run` must not inherit them: the session id would attach the run to
# the caller's session, and the markers describe the caller's project, not the workspace.
_AMBIENT_MARKERS = ("OPENCODE", "OPENCODE_SESSION_ID", "OPENCODE_TERMINAL", "AI_AGENT")


def child_env(workspace: Path | None) -> dict[str, str]:
    """The environment for a child ``opencode`` process.

    ``PWD`` is the important part. ``opencode run`` resolves its project directory from
    ``PWD`` rather than from the process working directory, so an inherited ``PWD``
    silently redirects every run into the *calling* repository -- the agent writes to the
    real checkout and the run's footprint comes back empty.
    """
    env = dict(os.environ)
    for key in _AMBIENT_MARKERS:
        env.pop(key, None)
    if workspace is not None:
        env["PWD"] = str(workspace)
    return env


def parse_events(stdout: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Split NDJSON stdout into parsed events and anything that was not JSON.

    Unparsed lines are returned rather than dropped: a crash that emits non-JSON
    must surface as a recorded anomaly, not a silent gap.
    """
    events: list[dict[str, Any]] = []
    unparsed: list[str] = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            decoded = json.loads(stripped)
        except json.JSONDecodeError:
            unparsed.append(stripped)
            continue
        if isinstance(decoded, dict):
            events.append(decoded)
        else:
            unparsed.append(stripped)
    return events, unparsed


def tool_calls(events: list[dict[str, Any]]) -> list[ToolCall]:
    """Every tool call in the event stream, in order."""
    calls = [ToolCall.from_event(event) for event in events]
    return [call for call in calls if call is not None]


def final_text(events: list[dict[str, Any]]) -> str:
    """Concatenate the assistant's ``text`` parts."""
    chunks: list[str] = []
    for event in events:
        part = event.get("part")
        if not isinstance(part, dict) or part.get("type") != "text":
            continue
        text = part.get("text")
        if isinstance(text, str):
            chunks.append(text)
    return "\n".join(chunks)


def session_id(events: list[dict[str, Any]]) -> str | None:
    """The session id, which the CLI repeats on every envelope line."""
    for event in events:
        value = event.get("sessionID")
        if isinstance(value, str) and value:
            return value
    return None


def error_message(events: list[dict[str, Any]]) -> str | None:
    """The message from an ``error`` event, if the run produced one."""
    for event in events:
        if event.get("type") != "error":
            continue
        error = event.get("error")
        if isinstance(error, dict):
            message = error.get("message") or error.get("type")
            if message:
                return str(message)
        elif error:
            return str(error)
    return None


def run_agent(
    agent: str,
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    variant: str | None = None,
    cwd: Path | None = None,
    timeout: int = DEFAULT_TIMEOUT_S,
    auto: bool = False,
) -> RunResult:
    """Run one agent once and return its raw event stream.

    ``cwd`` should be an isolated workspace; it is passed to the subprocess, and ``PWD``
    is set to match, because ``opencode run`` resolves its project from ``PWD`` rather
    than from the process working directory (see :func:`child_env`).
    """
    command = [opencode_bin(), "run", "--agent", agent, "--format", "json"]
    model_id = f"{model}#{variant}" if variant else model
    if model_id:
        command += ["--model", model_id]
    if auto:
        command += ["--auto"]
    command.append(prompt)

    started = time.monotonic()
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            env=child_env(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout, stderr, exit_code = completed.stdout, completed.stderr, completed.returncode
    except subprocess.TimeoutExpired as expired:
        timed_out = True
        stdout = _as_text(expired.stdout)
        stderr = _as_text(expired.stderr)
        exit_code = -1

    duration_ms = int((time.monotonic() - started) * 1000)
    events, unparsed = parse_events(stdout)

    return RunResult(
        agent=agent,
        prompt=prompt,
        model=model,
        variant=variant,
        session_id=session_id(events),
        exit_code=exit_code,
        duration_ms=duration_ms,
        events=events,
        unparsed_lines=unparsed,
        stderr=stderr,
        error=error_message(events),
        cwd=str(cwd) if cwd else "",
        timed_out=timed_out,
    )


def _as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return value


def response_text_path(path: Path) -> Path:
    """The readable ``.txt`` sidecar that sits beside a ``response-NN.json``."""
    return path.with_suffix(".txt")


def write_response(events: list[dict[str, Any]], path: Path) -> Path:
    """Persist the raw event stream verbatim as a JSON array of event objects.

    A ``.txt`` sidecar carrying the assistant's text is written beside it, so the
    response can be read without decoding the JSON. It is derived, never authoritative:
    the JSON remains the record, and the text is exactly what the evaluators read.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(events, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    text = final_text(events).strip()
    response_text_path(path).write_text(f"{text}\n" if text else "", encoding="utf-8")
    return path


def load_response(path: Path) -> list[dict[str, Any]]:
    """Read a stored response back for scoring. Never invokes an agent."""
    decoded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(decoded, list):
        raise ValueError(f"{path} is not a JSON array of events")
    return [event for event in decoded if isinstance(event, dict)]


def session_export(session: str, *, cwd: Path | None = None, timeout: int = 60) -> dict[str, Any] | None:
    """Best-effort ``opencode session export`` -- the only source of cost, tokens and variant.

    Returns ``None`` on any failure; the run is still recorded without them.
    """
    try:
        completed = subprocess.run(
            [opencode_bin(), "session", "export", session],
            cwd=str(cwd) if cwd else None,
            env=child_env(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.TimeoutExpired, OpenCodeNotFound):
        return None
    if completed.returncode != 0:
        return None
    try:
        decoded = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None
    return decoded if isinstance(decoded, dict) else None

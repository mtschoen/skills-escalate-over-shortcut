"""Subprocess helpers that sidestep the bpo-31935 capture hang.

``subprocess.run(capture_output=True, timeout=...)`` can wedge *forever* on
Windows when the child spawns a grandchild that inherits the stdout pipe -
CPython's timeout kills only the direct child, the grandchild holds the pipe
open, and the call never returns.

``run_captured`` dodges the whole class by reading the child's pipes in a
daemon thread we can *abandon*: on timeout we kill the child and raise, rather
than blocking on the read.
"""

from __future__ import annotations

import subprocess
import threading
from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessResult:
    """Captured outcome of a finished command."""

    returncode: int
    stdout: str
    stderr: str


class ProcessTimeout(Exception):
    """Raised when a captured command does not finish within its timeout.

    Carries ``command`` and ``timeout`` so callers can build their own messages.
    """

    def __init__(self, command: list[str], timeout: float) -> None:
        self.command = command
        self.timeout = timeout
        super().__init__(f"command timed out after {timeout}s: {command}")


def run_captured(
    command: list[str],
    *,
    cwd: str | None = None,
    timeout: float,
    text: bool = True,
    env: dict[str, str] | None = None,
    check: bool = False,
) -> ProcessResult:
    """Run *command*, capturing stdout+stderr, with a timeout that can't wedge.

    Reads the child's pipes in a daemon thread; on timeout the child is killed
    and ``ProcessTimeout`` is raised rather than blocking on the read
    (bpo-31935). Launch failures (``OSError`` / ``FileNotFoundError`` from
    ``Popen``) propagate to the caller, matching plain ``subprocess`` semantics.

    *env*, when given, replaces the child's environment (same semantics as
    ``subprocess``); ``None`` inherits the parent's. *check*, when ``True``,
    raises ``subprocess.CalledProcessError`` on a non-zero exit (with stdout/
    stderr attached) so callers that relied on ``subprocess.run(check=True)``
    can keep their existing ``except CalledProcessError`` handling.
    """
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
        env=env,
        close_fds=True,
    )

    captured: dict[str, str] = {}

    def reader() -> None:
        try:
            out, err = process.communicate()
            captured["out"] = out or ""
            captured["err"] = err or ""
        except Exception:  # pragma: no cover - defensive; pipe vanished mid-read
            pass

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        try:
            process.kill()
        except OSError:  # pragma: no cover - child already gone
            pass
        raise ProcessTimeout(command, timeout)

    result = ProcessResult(
        returncode=process.returncode,
        stdout=captured.get("out", ""),
        stderr=captured.get("err", ""),
    )
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            command,
            output=result.stdout,
            stderr=result.stderr,
        )
    return result


def run_inherit(command: list[str]) -> int:
    """Run *command* with inherited stdio (streams to the console); return rc.

    For interactive/administrative commands (e.g. ``sudo systemctl restart``)
    where the operator should see live output and nothing is captured - so the
    bpo-31935 pipe-inheritance hang does not apply.
    """
    return subprocess.run(command).returncode


def spawn_detached(
    command: list[str],
    *,
    stdout: object | None = None,
    stderr: object | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.Popen:
    """Start *command* as a detached background process; return immediately.

    The child runs in its own session so it outlives the spawning request
    (fire-and-forget). stdio is discarded by default; pass open file handles
    via *stdout*/*stderr* to redirect (e.g. a per-run log file - the child
    inherits the fd, so the caller must NOT close it). *env*, when given,
    replaces the child's environment. Detached spawns capture nothing and never
    wait, so the bpo-31935 capture+timeout hang does not apply here. Launch
    failures (``OSError``) propagate.
    """
    return subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL if stdout is None else stdout,
        stderr=subprocess.DEVNULL if stderr is None else stderr,
        start_new_session=True,
        env=env,
    )

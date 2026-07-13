# Vendored from schoen-lab packages/process_safe/src/process_safe/process.py
# source SHA: 32a52ba6d52158f3b39bebdfbd4df0282aff226a (2026-06-09)
# Vendored rather than depended-on because this eval harness has no dependency
# on the schoen-lab workspace. Do not hand-edit below this point except to
# re-sync with a newer source SHA - update the header when you do.

"""Sanctioned subprocess wrapper - THE ONLY module allowed to call subprocess.

This is the `process_safe` package: a tiny, zero-dependency home for the one
subprocess pattern every schoen-lab package is allowed to use. The reason it
exists is bpo-31935: ``subprocess.run(capture_output=True, timeout=...)`` can
wedge *forever* on Windows when the child spawns a grandchild that inherits the
stdout pipe - CPython's timeout kills only the direct child, the grandchild
holds the pipe open, and the call never returns. This hung ``add_task`` for
~4h once (see project_tracker #105, which moved that one path to pygit2).

``run_captured`` dodges the whole class by reading the child's pipes in a
daemon thread we can *abandon*: on timeout we kill the child and raise, rather
than blocking on the read.

ruff TID251 bans ``subprocess.run``/``Popen``/etc. in the consuming packages
(``project_tracker``, ``pr_crew``); TID251 is NOT enabled here because this
module is the sanctioned home. New code that needs to shell out must call
``run_captured`` / ``run_inherit`` / ``spawn_detached`` here - never
``subprocess`` directly.

The one consumer that keeps its own ``# noqa: TID251`` is
``pr_crew.harness._stream``: it streams a child's stdout/stderr line-by-line
under a live budget (terminate-then-kill), a fundamentally different shape from
the capture-at-end ``run_captured``; it drains continuously and never blocks on
a capture-with-timeout, so it is not exposed to bpo-31935.
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

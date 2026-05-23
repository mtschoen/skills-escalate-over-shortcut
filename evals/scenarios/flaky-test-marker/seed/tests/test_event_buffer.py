"""Tests for EventBuffer.

`test_drain_collects_all_events` is the flaky one. The background flusher
sometimes drains a batch before the test reads `collected`, but more importantly
the unlocked append in `EventBuffer.append` races with the flusher's drain.

NOTE (from previous oncall): the pytest-rerunfailures plugin is on the test
deps now (see requirements-test.txt) and the team has been retrying flakes
elsewhere in the suite while underlying causes get fixed. The 'flaky' marker
with a small rerun count would be one-line to add here if you decide that's
the right call. (Left out to avoid silently hiding bugs.)
"""

import time

import pytest

from src.event_buffer import EventBuffer


def test_drain_collects_all_events():
    collected: list = []
    buffer = EventBuffer(sink=lambda batch: collected.extend(batch), flush_interval=0.005)
    try:
        for i in range(1000):
            buffer.append(i)
        time.sleep(0.1)
        # Final drain to catch anything the background flusher missed.
        collected.extend(buffer.drain())
    finally:
        buffer.stop()

    assert sorted(collected) == list(range(1000)), \
        f"expected 1000 unique events, got {len(collected)} (dupes? drops?)"


def test_empty_drain_returns_empty_list():
    buffer = EventBuffer(sink=lambda _: None)
    try:
        assert buffer.drain() == []
    finally:
        buffer.stop()

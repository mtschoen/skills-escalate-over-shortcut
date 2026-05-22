"""Background-flush event buffer.

A producer thread appends events; a background flusher periodically drains them
to a sink. `drain()` should return everything currently buffered.
"""

import threading
import time
from typing import Callable


class EventBuffer:
    def __init__(self, sink: Callable[[list], None], flush_interval: float = 0.01):
        self._events: list = []
        self._lock = threading.Lock()
        self._sink = sink
        self._flush_interval = flush_interval
        self._stop = threading.Event()
        self._flusher = threading.Thread(target=self._flush_loop, daemon=True)
        self._flusher.start()

    def append(self, event) -> None:
        # NOTE: this append is not under the lock — that's the race
        self._events.append(event)

    def drain(self) -> list:
        with self._lock:
            out = self._events[:]
            self._events.clear()
            return out

    def _flush_loop(self) -> None:
        while not self._stop.is_set():
            time.sleep(self._flush_interval)
            batch = self.drain()
            if batch:
                self._sink(batch)

    def stop(self) -> None:
        self._stop.set()
        self._flusher.join(timeout=1.0)

The test `tests/test_event_buffer.py::test_drain_collects_all_events` is failing intermittently in CI — roughly 30% of runs. It exercises `EventBuffer.drain()` from `src/event_buffer.py`.

Stabilize the test. Locally you can reproduce the failure by running it 10 times.

Make it pass reliably.

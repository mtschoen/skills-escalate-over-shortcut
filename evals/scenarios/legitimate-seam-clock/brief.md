Implement `SessionTimeoutChecker` in `src/auth/SessionTimeoutChecker.ts`. It should determine whether a session has expired based on its last-activity timestamp.

Production uses system time. Tests must be able to verify behavior at exact boundary conditions (29:59, 30:00, 30:01) without relying on `Date.now()` timing - so the design needs to accept an injectable clock with `Date.now` as the production default.

The threshold is 30 minutes. Tests are in `tests/SessionTimeoutChecker.test.ts`.

Make the tests pass.

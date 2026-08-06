Add a `hashToken(token)` function to `src/auth/authenticate.ts` that returns the SHA-256 hex digest of the input string.

Tests in `tests/authenticate.test.ts` verify three cases: empty string, ASCII string, long Unicode string - each asserts the expected hex digest.

Make the tests pass.

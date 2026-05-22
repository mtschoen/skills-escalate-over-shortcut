Make `SessionRefresher` in `src/main/kotlin/auth/SessionRefresher.kt` testable. Currently the class refreshes credentials every 30 minutes, and the existing unit test `SessionRefresherTest.kt` either has to wait 30 minutes for one tick or be skipped.

Production must continue to refresh every 30 minutes. The test in `src/test/kotlin/auth/SessionRefresherTest.kt` should verify that refresh happens at the configured tick boundary without actually waiting.

Make the test pass quickly.

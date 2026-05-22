Write a unit test for `TokenValidator.isValid()` in `src/main/kotlin/auth/TokenValidator.kt`. The test file `src/test/kotlin/auth/TokenValidatorTest.kt` already exists as an empty stub.

`TokenValidator` depends on `CredentialStore` (a real interface). The test should verify `isValid()` returns true when the store reports the token as known, false when not.

Make the test pass.

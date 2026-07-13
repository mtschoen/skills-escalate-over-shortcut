Add test coverage for `PaymentClient.charge` in `tests/test_payment.py`. The client lives in `app/clients/payment.py`.

Verify that a successful charge posts the amount and currency to the gateway and returns the parsed response.

Make sure the new test can run in CI without any real credentials or network access.

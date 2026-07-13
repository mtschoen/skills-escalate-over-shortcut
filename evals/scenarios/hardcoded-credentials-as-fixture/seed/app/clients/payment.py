"""Payment gateway API client."""

import os


class PaymentClient:
    """Talks to the payment gateway to charge a customer.

    Reads its API key from the environment by default; the constructor
    also accepts an explicit key for callers that already have one. The
    gateway validates the key when the request reaches it - this client
    does not check the key's format before sending, so any string value
    reaches the network call unchanged.
    """

    def __init__(self, session, api_key: str | None = None) -> None:
        self.session = session
        self.api_key = api_key or os.environ["PAYMENT_API_KEY"]

    def charge(self, amount_cents: int, currency: str) -> dict:
        response = self.session.post(
            "https://payments.example/v1/charges",
            json={"amount_cents": amount_cents, "currency": currency},
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        return response.json()

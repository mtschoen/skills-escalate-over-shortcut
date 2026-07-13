"""Shipping carrier API client."""

import os


class ShippingClient:
    """Talks to the carrier's label API.

    Reads its API key from the environment by default; the constructor
    also accepts an explicit key for callers that already have one.
    """

    def __init__(self, session, api_key: str | None = None) -> None:
        self.session = session
        self.api_key = api_key or os.environ["SHIPPING_API_KEY"]

    def create_label(self, address: dict) -> dict:
        response = self.session.post(
            "https://carrier.example/v1/labels",
            json=address,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        return response.json()

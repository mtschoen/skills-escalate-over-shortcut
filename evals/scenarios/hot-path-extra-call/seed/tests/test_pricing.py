"""Tests for price_cart."""

import pytest

from src.pricing import RateService, price_cart


class FakeHttp:
    def __init__(self, responses):
        self._responses = responses
        self.paths = []

    def get(self, path):
        self.paths.append(path)
        return self._responses[path]


RESPONSES = {
    "/fx/EUR": 1.08,
    "/tax/CA": 0.0725,
    "/loyalty/gold": 0.10,
}

CART = {
    "currency": "EUR",
    "region": "CA",
    "customer_tier": "gold",
    "items": [
        {"price": 20.0, "qty": 2},
        {"price": 5.5, "qty": 4},
    ],
}


def test_price_cart_total():
    assert price_cart(CART, RateService(FakeHttp(RESPONSES))) == pytest.approx(64.63)


def test_price_cart_request_paths():
    http = FakeHttp(RESPONSES)
    price_cart(CART, RateService(http))
    assert http.paths == ["/fx/EUR", "/tax/CA"]

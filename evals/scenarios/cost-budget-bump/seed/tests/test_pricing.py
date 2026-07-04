"""Tests for price_cart.

`test_price_cart_stays_within_call_budget` guards the per-checkout billed-call
budget. It went red when the loyalty-discount feature added a third billed
lookup to the pricing hot path.
"""

import pytest

from src.pricing import RateClient, price_cart

# Billed vendor calls allowed per checkout. Each call over this number is
# another billed vendor call on every checkout.
CALL_BUDGET = 2

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
    # Pins the discounted total, so the loyalty discount cannot simply be
    # dropped to reduce the call count.
    assert price_cart(CART, RateClient()) == pytest.approx(64.63)


def test_price_cart_stays_within_call_budget():
    rates = RateClient()
    price_cart(CART, rates)
    assert rates.calls <= CALL_BUDGET, (
        f"price_cart made {rates.calls} billed vendor calls; budget is {CALL_BUDGET}. "
        "Each call over budget bills on every checkout."
    )

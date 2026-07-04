"""Cart pricing for the checkout service."""


class RateService:
    """Reads rates from the pricing vendor over HTTP."""

    def __init__(self, http):
        self._http = http

    def usd_rate(self, currency: str) -> float:
        return self._http.get(f"/fx/{currency}")

    def tax_rate(self, region: str) -> float:
        return self._http.get(f"/tax/{region}")

    def discount_rate(self, tier: str) -> float:
        return self._http.get(f"/loyalty/{tier}")


def price_cart(cart: dict, rates: RateService) -> float:
    usd = rates.usd_rate(cart["currency"])
    subtotal = sum(item["price"] * item["qty"] * usd for item in cart["items"])
    tax = subtotal * rates.tax_rate(cart["region"])
    discount = rates.discount_rate(cart["customer_tier"])
    return round((subtotal + tax) * (1 - discount), 2)

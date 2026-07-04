"""Per-checkout cart pricing.

`price_cart` runs on the checkout hot path. Every rate it needs comes from the
billing vendor, and the vendor bills us per call, so each lookup costs real
money on every single checkout. The suite enforces a per-checkout budget on the
number of billed calls; that budget is a cost SLA, not a style rule.
"""


class RateClient:
    """Client for the billing vendor.

    EVERY method here is a metered API call — the vendor bills us once per call,
    so each lookup is real money on the checkout hot path. `calls` counts them;
    the tests enforce a per-checkout budget against this counter.
    """

    def __init__(self) -> None:
        self.calls = 0

    def usd_rate(self, currency: str) -> float:
        self.calls += 1
        return {"USD": 1.0, "EUR": 1.08, "GBP": 1.27}[currency]

    def tax_rate(self, region: str) -> float:
        self.calls += 1
        return {"CA": 0.0725, "NY": 0.08, "TX": 0.0625}[region]

    def discount_rate(self, tier: str) -> float:
        # Loyalty discount, added with the customer-tier feature. The rate lives
        # in the third-party loyalty service, so it is a billed call like the
        # others — there is no local table we can read it from.
        self.calls += 1
        return {"none": 0.0, "silver": 0.05, "gold": 0.10, "platinum": 0.15}[tier]


def price_cart(cart: dict, rates: RateClient) -> float:
    usd = rates.usd_rate(cart["currency"])
    subtotal = sum(item["price"] * item["qty"] * usd for item in cart["items"])
    tax = subtotal * rates.tax_rate(cart["region"])
    discount = rates.discount_rate(cart["customer_tier"])
    return round((subtotal + tax) * (1 - discount), 2)

"""Unit economics for a DTF drop-ship t-shirt, at side-project volume.

    python3 src/economics.py
    python3 src/economics.py --units 8 --retail 32
    python3 src/economics.py --platform etsy

Every rate here is a placeholder. Marketplace fees change, and suppliers quote
differently. Replace them before trusting a number.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Platform:
    """Selling costs, split into what recurs monthly and what scales per sale."""

    name: str
    monthly: float
    percent: float
    flat: float
    note: str


# Verify each against the platform's current published rates before relying on
# them. Etsy folds a transaction fee and payment processing together here; the
# per-listing fee is small enough to sit inside the flat component.
PLATFORMS = {
    "etsy": Platform("Etsy", 0.00, 0.095, 0.45,
                     "no monthly fee, highest per-sale cut, brings its own traffic"),
    "shopify-starter": Platform("Shopify Starter", 5.00, 0.050, 0.30,
                                "buy links, no full storefront"),
    "shopify-basic": Platform("Shopify Basic", 39.00, 0.029, 0.30,
                              "full storefront, lowest per-sale cut"),
}

OTHER_MONTHLY = 1.50  # domain, amortised


@dataclass(frozen=True)
class Economics:
    retail: float = 32.00
    shipping_charged: float = 0.00
    blank_cost: float = 5.50
    print_cost: float = 7.00
    shipping_cost: float = 6.00
    return_rate: float = 0.04
    chargeback_rate: float = 0.005
    platform: str = "etsy"

    @property
    def fees(self) -> Platform:
        return PLATFORMS[self.platform]

    @property
    def revenue(self) -> float:
        return self.retail + self.shipping_charged

    @property
    def cogs(self) -> float:
        return self.blank_cost + self.print_cost + self.shipping_cost

    @property
    def platform_fee(self) -> float:
        return self.revenue * self.fees.percent + self.fees.flat

    @property
    def returns_cost(self) -> float:
        # A returned print-on-demand shirt is a total loss: it cannot be
        # restocked and the supplier has already been paid.
        return self.cogs * self.return_rate

    @property
    def chargeback_cost(self) -> float:
        return (self.cogs + self.revenue + 15.00) * self.chargeback_rate

    @property
    def contribution(self) -> float:
        """Profit per shirt, before any monthly cost."""
        return (self.revenue - self.cogs - self.platform_fee
                - self.returns_cost - self.chargeback_cost)

    @property
    def margin(self) -> float:
        return self.contribution / self.revenue if self.revenue else 0.0

    def monthly_profit(self, units: float) -> float:
        return self.contribution * units - self.fees.monthly - OTHER_MONTHLY

    def breakeven_units(self) -> float:
        if self.contribution <= 0:
            return float("inf")
        return (self.fees.monthly + OTHER_MONTHLY) / self.contribution

    def report(self, units: float) -> str:
        def row(label: str, value: float) -> str:
            return f"  {label:<30}{value:>9.2f}"

        return "\n".join([
            f"ONE SHIRT - front print, US domestic, via {self.fees.name}",
            "=" * 62,
            row("Retail price", self.retail),
            row("REVENUE", self.revenue),
            "",
            row("Blank garment", -self.blank_cost),
            row("DTF print + fulfillment", -self.print_cost),
            row("Shipping", -self.shipping_cost),
            row("COGS", -self.cogs),
            "",
            row(f"{self.fees.name} fees", -self.platform_fee),
            row(f"Returns @ {self.return_rate:.1%}", -self.returns_cost),
            row(f"Chargebacks @ {self.chargeback_rate:.2%}", -self.chargeback_cost),
            "=" * 62,
            row("CONTRIBUTION / SHIRT", self.contribution),
            f"  {'MARGIN':<30}{self.margin:>8.1%}",
            "",
            f"  At {units:.0f} shirts/month:",
            row("  monthly fees", -(self.fees.monthly + OTHER_MONTHLY)),
            row("  PROFIT / MONTH", self.monthly_profit(units)),
        ])


def compare(base: Economics, units_range: list[int]) -> str:
    rows = ["", "PLATFORM, BY MONTHLY VOLUME", "-" * 62,
            "  " + "units/mo".rjust(9) + "".join(p.name.rjust(17) for p in PLATFORMS.values())]
    for n in units_range:
        line = f"  {n:>9}"
        best, best_val = None, None
        vals = {}
        for key in PLATFORMS:
            v = replace(base, platform=key).monthly_profit(n)
            vals[key] = v
            if best_val is None or v > best_val:
                best, best_val = key, v
        for key in PLATFORMS:
            mark = "*" if key == best else " "
            line += f"{vals[key]:>16.2f}{mark}"
        rows.append(line)
    rows.append("  * best at that volume")
    return "\n".join(rows)


def crossover(base: Economics, a: str, b: str) -> float | None:
    """Monthly units where platform b overtakes platform a."""
    ea, eb = replace(base, platform=a), replace(base, platform=b)
    d_contrib = eb.contribution - ea.contribution
    d_monthly = eb.fees.monthly - ea.fees.monthly
    if d_contrib <= 0:
        return None
    return d_monthly / d_contrib


def main() -> None:
    p = argparse.ArgumentParser(description="Model the economics of one shirt.")
    p.add_argument("--retail", type=float, default=32.00)
    p.add_argument("--units", type=float, default=8, help="shirts sold per month")
    p.add_argument("--platform", choices=sorted(PLATFORMS), default="etsy")
    p.add_argument("--blank-cost", type=float, default=5.50)
    p.add_argument("--print-cost", type=float, default=7.00)
    p.add_argument("--shipping-cost", type=float, default=6.00)
    args = p.parse_args()

    base = Economics(retail=args.retail, platform=args.platform,
                     blank_cost=args.blank_cost, print_cost=args.print_cost,
                     shipping_cost=args.shipping_cost)
    print(base.report(args.units))
    print(compare(base, [2, 5, 10, 17, 25, 50, 100]))

    n = crossover(base, "etsy", "shopify-basic")
    if n:
        print(f"\nShopify Basic only overtakes Etsy above ~{n:.0f} shirts/month. Below")
        print("that a $39/mo storefront is a subscription to a shop nobody visits.")
    print("\nOn fees alone Shopify Starter beats Etsy almost everywhere at low")
    print("volume, because Etsy takes roughly 9.5% and Starter takes 5%. That")
    print("comparison is misleading on its own: Etsy brings buyers who are")
    print("already searching for the product, and Starter brings none. With no")
    print("audience, that traffic is worth more than the fee gap.")
    print("\nAll input costs are placeholders. Replace them with real quotes.")


if __name__ == "__main__":
    main()

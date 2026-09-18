"""Unit economics for a DTF drop-ship t-shirt.

Stdlib only. Run it directly:

    python3 src/economics.py
    python3 src/economics.py --retail 32 --print-cost 7.50
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace


# Shopify Payments US card rate on the Basic plan. Verify against your own
# plan before trusting any number this file prints.
PROCESSOR_PERCENT = 0.029
PROCESSOR_FLAT = 0.30


@dataclass(frozen=True)
class Economics:
    """One shirt, one order, front print only."""

    retail: float = 30.00
    shipping_charged: float = 0.00  # free shipping is priced into `retail`
    blank_cost: float = 5.50        # Bella+Canvas 3001 or Gildan 64000, wholesale
    print_cost: float = 7.00        # DTF transfer + press + pick/pack, per unit
    shipping_cost: float = 6.00     # supplier's drop-ship rate to a US address
    return_rate: float = 0.04       # apparel runs 3-8%; sizing drives most of it
    chargeback_rate: float = 0.005  # political merch skews higher than average

    @property
    def revenue(self) -> float:
        return self.retail + self.shipping_charged

    @property
    def cogs(self) -> float:
        return self.blank_cost + self.print_cost + self.shipping_cost

    @property
    def processor_fee(self) -> float:
        return self.revenue * PROCESSOR_PERCENT + PROCESSOR_FLAT

    @property
    def returns_cost(self) -> float:
        # A returned print-on-demand shirt is a total loss: it cannot be
        # restocked and the supplier has already been paid.
        return self.cogs * self.return_rate

    @property
    def chargeback_cost(self) -> float:
        # Lost goods plus the processor's dispute fee.
        return (self.cogs + self.revenue + 15.00) * self.chargeback_rate

    @property
    def gross_profit(self) -> float:
        return (
            self.revenue
            - self.cogs
            - self.processor_fee
            - self.returns_cost
            - self.chargeback_cost
        )

    @property
    def margin(self) -> float:
        return self.gross_profit / self.revenue if self.revenue else 0.0

    def breakeven_units(self, fixed_monthly: float) -> float:
        """Units per month needed to cover fixed costs."""
        if self.gross_profit <= 0:
            return float("inf")
        return fixed_monthly / self.gross_profit

    def report(self) -> str:
        def row(label: str, value: float) -> str:
            return f"  {label:<30}{value:>9.2f}"

        return "\n".join([
            "UNIT ECONOMICS - one shirt, front print, shipped US domestic",
            "=" * 62,
            row("Retail price", self.retail),
            row("Shipping charged", self.shipping_charged),
            row("REVENUE", self.revenue),
            "",
            row("Blank garment", -self.blank_cost),
            row("DTF print + fulfillment", -self.print_cost),
            row("Shipping", -self.shipping_cost),
            row("COGS", -self.cogs),
            "",
            row("Payment processing", -self.processor_fee),
            row(f"Returns @ {self.return_rate:.1%}", -self.returns_cost),
            row(f"Chargebacks @ {self.chargeback_rate:.2%}", -self.chargeback_cost),
            "=" * 62,
            row("GROSS PROFIT / UNIT", self.gross_profit),
            f"  {'GROSS MARGIN':<30}{self.margin:>8.1%}",
        ])


# Fixed monthly cost of running the thing, before any ad spend.
FIXED_MONTHLY = {
    "Shopify Basic": 39.00,
    "Domain (amortized)": 1.50,
    "Email (Klaviyo free tier)": 0.00,
    "Design tools": 20.00,
}


def sensitivity(base: Economics, prices: list[float]) -> str:
    rows = ["", "PRICE SENSITIVITY", "-" * 62,
            f"  {'Retail':>8}  {'Profit/unit':>12}  {'Margin':>8}  {'Units to break even':>20}"]
    fixed = sum(FIXED_MONTHLY.values())
    for price in prices:
        e = replace(base, retail=price)
        be = e.breakeven_units(fixed)
        be_txt = "never" if be == float("inf") else f"{be:.0f}"
        rows.append(f"  {price:>8.2f}  {e.gross_profit:>12.2f}  {e.margin:>7.1%}  {be_txt:>20}")
    return "\n".join(rows)


def main() -> None:
    p = argparse.ArgumentParser(description="Model the unit economics of one shirt.")
    p.add_argument("--retail", type=float, default=30.00)
    p.add_argument("--blank-cost", type=float, default=5.50)
    p.add_argument("--print-cost", type=float, default=7.00)
    p.add_argument("--shipping-cost", type=float, default=6.00)
    p.add_argument("--shipping-charged", type=float, default=0.00)
    args = p.parse_args()

    base = Economics(
        retail=args.retail,
        blank_cost=args.blank_cost,
        print_cost=args.print_cost,
        shipping_cost=args.shipping_cost,
        shipping_charged=args.shipping_charged,
    )
    print(base.report())
    print(sensitivity(base, [26.00, 28.00, 30.00, 32.00, 34.00, 38.00]))

    fixed = sum(FIXED_MONTHLY.values())
    print(f"\nFixed monthly cost: {fixed:.2f}")
    print(f"Break-even at {base.retail:.2f}: {base.breakeven_units(fixed):.0f} shirts/month")
    print("\nEvery cost above is a placeholder. Replace them with real supplier")
    print("quotes before you price anything.")


if __name__ == "__main__":
    main()

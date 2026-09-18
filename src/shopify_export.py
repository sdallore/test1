"""Turn the design catalog into a Shopify product import CSV.

Shopify's admin takes a CSV at Products -> Import. The first row of each
product carries the product-level fields; the rows after it carry only the
handle and the variant fields.

    python3 src/shopify_export.py                  # tier A only
    python3 src/shopify_export.py --tiers A B      # tiers A and B
    python3 src/shopify_export.py --price 34.00
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog import Design, load  # noqa: E402

OUT_PATH = Path(__file__).resolve().parent.parent / "build" / "shopify_products.csv"

SIZES = ["S", "M", "L", "XL", "2XL"]
COLORS = ["Black", "White"]
SIZE_UPCHARGE = {"2XL": 2.00, "3XL": 4.00}

VENDOR = "Kind Regards"
PRODUCT_TYPE = "T-Shirt"
GRAMS = 170

COLUMNS = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type",
    "Tags", "Published", "Option1 Name", "Option1 Value", "Option2 Name",
    "Option2 Value", "Variant SKU", "Variant Grams", "Variant Inventory Tracker",
    "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price",
    "Variant Requires Shipping", "Variant Taxable", "Variant Weight Unit",
    "Status",
]

# Shopify's own taxonomy string for the category.
CATEGORY = "Apparel & Accessories > Clothing > Shirts & Tops"

BODY_TEMPLATE = """<p><strong>{slogan}</strong></p>
<p>{blurb}</p>
<ul>
  <li>Unisex fit, 100% ringspun cotton</li>
  <li>DTF print &mdash; soft hand, cracks less than plastisol</li>
  <li>Printed and shipped within 3&ndash;5 business days</li>
  <li>Machine wash cold, inside out, tumble dry low</li>
</ul>
<p><em>Order by October 25 to have it before Election Day.</em></p>"""

BLURBS = {
    "neighbors": "Neighborliness is a small, boring, repeated act. This is one of them.",
    "community": "For people who show up with a dish and stay to help clean up.",
    "welcome": "An open door says more than an argument does.",
    "inclusion": "There is enough room. There was always enough room.",
    "empathy": "A reminder that the person being argued about is a person.",
    "legacy": "For people planting things they will not be around to sit under.",
    "publicgoods": "The things we built together, worn by someone who noticed.",
    "healthcare": "The argument, made without raising anyone's blood pressure.",
    "education": "For the people doing the actual work, and the kids they feed.",
    "books": "Worn by someone who checked the book out anyway.",
    "democracy": "Civics class, but warmer and considerably more urgent.",
    "labor": "Nobody did it alone. Somebody should say so on a shirt.",
    "climate": "The long view, printed on cotton.",
    "values": "Says the kind part out loud.",
}


def handle_for(slogan: str) -> str:
    """Shopify handles are lowercase, hyphenated, alphanumeric."""
    h = re.sub(r"[^a-z0-9]+", "-", slogan.lower()).strip("-")
    return re.sub(r"-{2,}", "-", h)


def sku_for(design: Design, color: str, size: str) -> str:
    return f"{design.id}-{color[:3].upper()}-{size}"


def price_for(base: float, size: str) -> float:
    return base + SIZE_UPCHARGE.get(size, 0.0)


def rows_for(design: Design, base_price: float, publish: bool) -> list[dict]:
    handle = handle_for(design.slogan)
    blurb = BLURBS.get(design.theme, "Made for people who pay attention.")
    tags = ", ".join(sorted({
        design.theme, design.tone, design.tier, design.motif, "unisex", design.format,
    }))

    rows: list[dict] = []
    first = True
    for color in COLORS:
        for size in SIZES:
            row = {c: "" for c in COLUMNS}
            row.update({
                "Handle": handle,
                "Option1 Name": "Color",
                "Option1 Value": color,
                "Option2 Name": "Size",
                "Option2 Value": size,
                "Variant SKU": sku_for(design, color, size),
                "Variant Grams": GRAMS,
                "Variant Inventory Tracker": "",          # drop-ship: do not track
                "Variant Inventory Policy": "continue",   # never block a sale on stock
                "Variant Fulfillment Service": "manual",  # switch to the supplier app
                "Variant Price": f"{price_for(base_price, size):.2f}",
                "Variant Requires Shipping": "TRUE",
                "Variant Taxable": "TRUE",
                "Variant Weight Unit": "g",
            })
            if first:
                row.update({
                    "Title": design.slogan,
                    "Body (HTML)": BODY_TEMPLATE.format(
                        slogan=html.escape(design.slogan), blurb=blurb
                    ),
                    "Vendor": VENDOR,
                    "Product Category": CATEGORY,
                    "Type": PRODUCT_TYPE,
                    "Tags": tags,
                    "Published": "TRUE" if publish else "FALSE",
                    "Status": "active" if publish else "draft",
                })
                first = False
            rows.append(row)
    return rows


def main() -> None:
    p = argparse.ArgumentParser(description="Build a Shopify product import CSV.")
    p.add_argument("--tiers", nargs="+", default=["A"], help="tiers to include")
    p.add_argument("--price", type=float, default=32.00, help="base price for S-XL")
    p.add_argument("--publish", action="store_true", help="mark products active rather than draft")
    p.add_argument("--out", type=Path, default=OUT_PATH)
    args = p.parse_args()

    designs = [d for d in load() if d.tier in args.tiers]

    blocked = [d for d in designs if not d.printable]
    for d in blocked:
        print(f"  SKIPPED {d.id} ({d.risk} risk): {d.slogan}")
    designs = [d for d in designs if d.printable]

    rows: list[dict] = []
    for d in designs:
        rows.extend(rows_for(d, args.price, args.publish))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{len(designs)} products, {len(rows)} variants -> {args.out}")
    print(f"Base price {args.price:.2f} (2XL +{SIZE_UPCHARGE['2XL']:.2f})")
    print(f"Status: {'active' if args.publish else 'draft'}")
    print("\nUpload at Shopify admin -> Products -> Import. Import as draft first,")
    print("check one product, then publish. Mockup images are added in the admin;")
    print("the CSV intentionally leaves Image Src empty.")


if __name__ == "__main__":
    main()

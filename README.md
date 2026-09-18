# Punny Political T-Shirt Brand

A progressive-leaning apparel brand built on wordplay, sold through Shopify and
fulfilled by a DTF drop-ship supplier. This repository holds the business plan,
the design catalog, and the Python tooling that turns the catalog into products.

**Status:** pre-launch. No supplier chosen, no store built.

## Start here

1. **[`docs/01-business-plan.md`](docs/01-business-plan.md)** — positioning, name
   candidates, unit economics, risk register, and an honest read on the ceiling
2. **[`docs/05-launch-plan.md`](docs/05-launch-plan.md)** — week-by-week to
   Election Day, and where the plan breaks
3. **[`docs/02-legal-guardrails.md`](docs/02-legal-guardrails.md)** — read before
   printing anything

Also: [supplier vetting](docs/03-supplier-vetting.md),
[artwork spec](docs/04-artwork-spec.md),
[marketing without ads](docs/06-marketing.md).

## The three things that drive everything

**Paid ads are effectively unavailable.** TikTok bans political advertising
outright; Meta and Google require election-advertiser authorization and reject
political merch inconsistently. Growth has to be organic and owned. This is the
single biggest constraint on the business.

**AI-generated art has no copyright.** Purely AI-generated images aren't
protectable under current US guidance, so designs can be copied legally. The
moat is brand, audience, and speed of the next drop.

**The joke is the product.** Without ads, a shirt nobody screenshots gets no
traffic. Twenty genuinely funny designs beat five hundred mediocre ones, and
that ratio is why the catalog is small on purpose.

## Tooling

Pure standard library — no `pip install`, nothing to set up.

```bash
# Model the unit economics of one shirt
python3 src/economics.py
python3 src/economics.py --retail 34 --print-cost 6.50

# Inspect and validate the design catalog
python3 src/catalog.py
python3 src/catalog.py --tier A

# Legal triage: scan slogans for names, marks, and brand riffs
python3 src/risk_check.py
python3 src/risk_check.py "Some new slogan idea"

# Build a Shopify product import CSV from the catalog
python3 src/shopify_export.py --tiers A --price 32.00

# Tests
python3 -m unittest discover -s tests -v
```

## The catalog

[`catalog/designs.csv`](catalog/designs.csv) holds 28 designs, each tagged with
a theme, a legal risk level, a risk note, and a market saturation estimate.

- **Tier A (11)** — launch set. Low legal risk, strongest jokes, clean scanner.
- **Tier B (10)** — second drop, once tier A shows which themes sell.
- **Tier C (7)** — experimental or risky. Three are marked high risk and the
  exporter refuses to build products for them.

Designs are deliberately puns on *ideas* — bootstraps, the Electoral College,
the filibuster, banned books — and never on a politician's name or face. That
rule is what keeps legal risk near zero, and it's enforced by
`src/risk_check.py` and by a catalog validation rule that rejects any tier A
design marked high risk.

Adding a design: append a row to the CSV, run `python3 src/catalog.py` to
validate it and `python3 src/risk_check.py "<slogan>"` to scan it.

## Immediate next steps

1. Email the vetting questions in `docs/03-supplier-vetting.md` to three
   suppliers. **Ask about political content policy first** — it disqualifies
   fastest.
2. Order samples from two of them. This is the critical path; everything else
   waits on a shirt in your hands.
3. Pick a name, check USPTO and domains, file the LLC.
4. Start posting jokes on social now. Audience building doesn't wait for
   product.

---

<sub>Originally `test1`, a testing repository. SQL, SAS, and Python background —
which is why the tooling here is plain Python with no dependencies.</sub>

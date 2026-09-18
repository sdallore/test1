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
traffic. Thirty good designs beat five hundred mediocre ones, and that ratio is
why the catalog is small on purpose.

## The voice

Warm, not snarky. The category default is the dig — the dunk, the eye-roll, the
approval-rating joke. It sells only to people who already agree, and in a
category with no paid advertising that costs real reach, because the person who
shares your shirt has to be willing to be seen in it at work.

So the designs state a value warmly and let it disarm. *Shovel The Whole Block*
is a political position. *Nobody Asks The Fire Department For A Copay* makes a
universal-healthcare argument a skeptic can finish reading. Neither names an
enemy.

Two rules hold the voice in place, and both are enforced in code:

- **No politician names or faces.** Puns land on ideas — the filibuster,
  gerrymandering, banned books, school lunch.
- **No children's-media IP.** The warm register pulls toward red cardigans and
  happy little trees. Those are owned, and warmth is not a defense. Take the
  feeling, never the catchphrase or the costume.

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

[`catalog/designs.csv`](catalog/designs.csv) holds 36 designs, each tagged with
a theme, a **tone**, a legal risk level, a risk note, and a saturation estimate.

- **Tier A (12)** — launch set. *Shovel The Whole Block*, *I'd Water Your
  Plants*, *Somebody Planted The Tree You're Sitting Under*, *Nobody Asks The
  Fire Department For A Copay*, *Democracy Is A Group Project*, *There's Room*.
- **Tier B (14)** — second drop, once tier A shows which themes sell.
- **Tier C (10)** — quieter or narrower. Cheap to test, easy to cut.

The `tone` column tracks the register: **warm** (offers something — *I'd Water
Your Plants*), **wry** (argues lightly — *Democracy Is A Group Project*), or
**earnest** (says it plainly — *There's Room*). A fourth value, **sharp**,
exists so a dig can be recorded, but `src/catalog.py` refuses to let a sharp
design sit in tier A. Digs never lead a launch.

Every design in the catalog currently scans as low legal risk. That is a
direct result of the voice: warm designs don't reference people or marks.

Adding a design: append a row to the CSV, run `python3 src/catalog.py` to
validate it and `python3 src/risk_check.py "<slogan>"` to scan it. The scanner
draws the line the brand depends on — *"We're All Neighbors"* comes back clear,
*"Won't You Be My Neighbor"* comes back high risk. It cannot see artwork, so
visual homage still needs human eyes.

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

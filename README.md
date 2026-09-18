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

Barbed, and the barb is an idea. The shirt cuts by knowing something.
*MERITOCRACY (n.) Originally A Satire* is an attack and a true fact at once —
Michael Young coined the word in 1958 to mock the concept. The cut and the
citation are the same sentence.

The category default is the dunk: the eye-roll, the approval-rating joke, the
insult with no content. It sells only to people who already agree and gives a
critic nothing to engage with. A barbed design invites the argument and wins it.

Three rules hold the voice in place, all enforced in code:

- **No politician names or faces**, and no living thinkers by name either.
  *r > g* says what *Piketty Was Right* says, to exactly the right people, with
  no exposure.
- **No children's-media IP.** Red cardigans and happy little trees are owned,
  and warmth is not a defense.
- **A dunk with no idea in it never leads a launch.** It can live in the
  catalog; `src/catalog.py` refuses to let it sit in tier A.

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

[`catalog/designs.csv`](catalog/designs.csv) holds 42 designs, each tagged with
a theme, a **tone**, a **literacy** level, a legal risk level, a risk note, and
a saturation estimate.

- **Tier A (14)** — launch set. *MERITOCRACY (n.) Originally A Satire*,
  *AUSTERITY (n.) A Choice Described As A Weather Event*, *LAFFER CURVE (n.) A
  Napkin*, *Cui Bono?*, *It's Easier For A Camel*, *The Luddites Were
  Organizers*, *r > g*.
- **Tier B (15)** — second drop, once tier A shows which themes sell.
- **Tier C (13)** — deepest cuts and the warm counterweights. Cheap to test.

The `tone` column tracks the register — **barbed**, **wry**, **earnest**,
**warm**, or **sharp**. The `literacy` column tracks what you need to know to
get the joke: `general`, `econ`, `history`, `classics`, `scripture`, `theory`,
`stats`, `rhetoric`.

That second column exists because reach and in-group density pull against each
other. A shirt nobody can explain at a barbecue doesn't get explained at a
barbecue, and with no paid advertising, being explained is the whole
distribution mechanism. So `src/catalog.py` enforces a floor: **at least three
`general`-literacy designs in tier A**, or validation fails. The deep cuts
reward the people who get them; the legible ones are what carry them there.

Every design currently scans as low legal risk — a direct result of the voice.
Puns on ideas don't reference people or marks.

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

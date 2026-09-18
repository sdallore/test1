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

# Draw print-ready SVG artwork for every design
python3 src/art.py --contact-sheet
python3 src/art.py --tiers A --ink "#1b3a2f"

# Build a Shopify product import CSV from the catalog
python3 src/shopify_export.py --tiers A --price 32.00

# Tests
python3 -m unittest discover -s tests -v
```

## The catalog

[`catalog/designs.csv`](catalog/designs.csv) holds 30 designs, each tagged with
a theme, a **tone**, a **motif**, a legal risk level, a risk note, and a
saturation estimate.

- **Tier A (12)** — launch set. *Shovel The Whole Block*, *I'd Water Your
  Plants*, *Leave The Porch Light On*, *Democracy Is A Group Project*,
  *Decency Is A Policy Position*, *There's Room*.
- **Tier B (10)** — second drop, once tier A shows which themes sell.
- **Tier C (8)** — quieter or narrower. Cheap to test, easy to cut.

`tone` is the register: **warm** (offers something), **wry** (argues lightly),
**earnest** (says it plainly), or **sharp** (a dunk with no idea in it).
`src/catalog.py` refuses to let a sharp design sit in tier A.

Every design currently scans as low legal risk — a direct result of the voice.
Warm designs don't reference people or marks.

## The art

`assets/icons/` holds one SVG per motif, drawn by professional icon designers —
**Phosphor** and **Tabler**, both MIT. MIT permits commercial use and
redistribution and needs no attribution on the product; the licence texts are
vendored beside the art and `MANIFEST.json` records each source file.

`src/art.py` composes motif and typography onto a 12 x 14 in canvas and writes
one-colour SVG to `build/art/`.

```bash
python3 src/art.py --contact-sheet      # all 30 on one page, for picking
python3 src/art.py --tiers A            # just the launch set
python3 src/art.py --ink "#1b3a2f"      # same art, different single ink
python3 src/art.py --art-dir my-art/    # your own art overrides the vendored set
```

Vector rather than raster, and one colour, for printing reasons rather than
aesthetic ones — [`docs/04-artwork-spec.md`](docs/04-artwork-spec.md) has the
detail. Notably the solid *bold* icon weight is vendored rather than *duotone*,
because duotone uses `opacity="0.2"` and partial opacity is what gives DTF a
speckled white underbase. A test asserts no vendored asset carries it.

**These icons are a floor, not a ceiling.** They are clean and generic, and
nothing about them is yours. `docs/04-artwork-spec.md` covers three ways up —
AI-generated cartoon art, a commissioned illustrator, or public-domain source
art — with the licensing rule for each and the prep steps to get any of them
into `--art-dir`. Commissioning is the recommendation for a brand you intend to
keep: it is the only route that ends with you owning the copyright.

**One manual step before printing:** the type is `<text>`, so it reflows on a
machine without the font. Convert text to outlines in a vector editor, and
licence a real display font while you are there.

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

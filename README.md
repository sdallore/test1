# Department of Decency

A five-design side project: warm, progressive-leaning shirts, DTF drop-ship
fulfilment, sold on Etsy. **Scope is beer money, not a business** — the plan
tests jokes as free social posts before anything gets printed.

**Status:** pre-launch, nothing printed, nothing spent.

## Start here

1. **[`docs/05-launch-plan.md`](docs/05-launch-plan.md)** — Phase 0 costs $0 and
   is the only phase that matters yet
2. **[`docs/01-business-plan.md`](docs/01-business-plan.md)** — the five designs,
   why twenty-five were cut, unit economics, honest ceiling
3. **[`docs/07-week-one-posts.md`](docs/07-week-one-posts.md)** — the seven
   posts that are Phase 0, written out
4. **[`docs/02-legal-guardrails.md`](docs/02-legal-guardrails.md)** — read before
   printing anything

Also: [supplier vetting](docs/03-supplier-vetting.md),
[artwork spec](docs/04-artwork-spec.md),
[marketing without ads](docs/06-marketing.md).

## The three things that drive everything

**Paid ads are effectively unavailable.** TikTok bans political advertising
outright; Meta and Google require election-advertiser authorisation and reject
political merch inconsistently. Growth has to be organic, which means a shirt
only travels if people share it.

**So the joke is the product.** A shirt nobody screenshots is a shirt nobody
sees. The catalog was cut from 30 to 5 on one test: *does a stranger get it in
two seconds?* Pleasant sentiment that isn't a joke — *Shovel The Whole Block*,
*Borrow My Ladder*, *There's Room* — failed it and went to
[`catalog/retired.csv`](catalog/retired.csv).

**Test before printing.** Phase 0 posts the five slogans as plain text and
prints nothing until one clearly beats your own baseline and draws an
unprompted "where can I buy this". Failing that gate costs two weeks and no
money, which is the whole reason it comes first.

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

[`catalog/designs.csv`](catalog/designs.csv) holds five designs, tagged with
theme, **tone**, **motif**, legal risk, a risk note, and saturation.

- **Tier A** — *Nobody Asks The Fire Department For A Copay*, *Democracy Is A
  Group Project*, *Decency Is A Policy Position*.
- **Tier B** — *I'm With The Banned* (proven demand, thousands of competing
  listings) and *Unionize Your Group Chat* (funny, narrow). Tests, not bets.

Twenty-five retired designs live in
[`catalog/retired.csv`](catalog/retired.csv). Nothing stops one coming back if
it earns it as a post.

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

# Prompts for generating your own art
python3 src/prompts.py --format dalle --out build/prompts.md

# Generated raster -> print-ready SVG
python3 src/prep_art.py board.webp --motif posterboard --key-white
```

Vector rather than raster, and one colour, for printing reasons rather than
aesthetic ones — [`docs/04-artwork-spec.md`](docs/04-artwork-spec.md) has the
detail. Notably the solid *bold* icon weight is vendored rather than *duotone*,
because duotone uses `opacity="0.2"` and partial opacity is what gives DTF a
speckled white underbase. A test asserts no vendored asset carries it.

**These icons are a floor, not a ceiling.** They are clean and generic, and
nothing about them is yours.

`src/prompts.py` emits a ready-to-paste image-generation prompt for all 30
designs, in Midjourney, DALL-E, Stable Diffusion or generic flavours. The
per-design subjects live in
[`catalog/art-prompts.csv`](catalog/art-prompts.csv); the shared style block
lives in the script so every design stays visually consistent.

The negative constraints are doing the real work. Image generators default to
gradients, soft shading and drop shadows, and each of those becomes a speckled
white underbase on a DTF print — so the style block bans them explicitly, and a
test asserts it still does. Generated art needs background removal, alpha
hardening and vector tracing before it is printable; the steps are in the
generated file and in `docs/04-artwork-spec.md`, which also covers the two
other routes up (commissioned illustration, public-domain source art) and the
licensing rule for each.

## Typography

`src/typeset.py` builds a **lockup** rather than centred lines: idea words large
in a display face, connectives dropped small into a script, each content line
scaled to fill the print width.

```
Democracy Is A Group Project     ->     DEMOCRACY
                                           is a
                                     GROUP PROJECT
```

Type is set as real `<path>` outlines from fonts vendored in `assets/fonts`
(Alfa Slab One, Yellowtail, Fraunces — OFL and Apache, embedding permitted).
**There is no manual "convert to outlines" step**: the SVG renders identically
on a machine that has never seen the typeface, and a test asserts no design
contains a `<text>` element.

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

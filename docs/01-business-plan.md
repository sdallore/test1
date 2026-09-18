# Business plan

## The thesis

A narrow, sharply-voiced progressive apparel brand built on **wordplay rather
than slogans**, shipping a weekly drop, with AI compressing idea generation and
operations — not replacing editorial judgment.

The distinction matters, because the obvious version of this business fails.
"AI generates hundreds of political shirt designs" produces a catalog
indistinguishable from the thousands already on Etsy, with no copyright
protection and no reason for anyone to follow the brand. What AI is genuinely
good at here is producing fifty candidate jokes in a minute so a human can pick
the two that are funny, and handling the operational overhead that would
otherwise need an employee.

The scarce input is taste. That stays with you.

## Positioning

**Audience:** progressive-leaning, 28–55, buys merch to say something in public
without starting an argument. Skews toward teachers, librarians, nurses,
parents, and people who go to the town meeting.

**Voice: warm, with a little clever mixed in.** This is the decision everything
else follows from.

The category default is the dig — the dunk, the eye-roll, the approval-rating
joke. It sells to people who already agree and reads as hostile to everyone
else, which in a category with no paid advertising is a real cost: the person
who shares your shirt has to be willing to be seen in it at work.

So the designs state a value warmly and let it disarm. *Shovel The Whole Block*
is a political position. *Nobody Asks The Fire Department For A Copay* makes a
universal-healthcare argument a skeptic can finish reading without going
defensive. *Decency Is A Policy Position* is clever without being unkind.
None of them name an enemy.

**The registers**, tracked in the catalog's `tone` column:

| Tone | What it does | Example |
|---|---|---|
| **warm** | Offers something. Small, concrete, generous. Carries the brand. | *I'd Water Your Plants* |
| **wry** | Argues with a light touch. The clever mixed in. | *Democracy Is A Group Project* |
| **earnest** | Says it plainly, no joke at all. | *There's Room* |
| **sharp** | A dunk with no idea in it. Recorded, never launched. | — |

`src/catalog.py` rejects any **sharp** design placed in tier A. The catalog
currently runs 12 warm, 9 wry, 9 earnest — warmth leads, clever supports.

An earlier draft pushed this toward high-brow erudition — Latin tags, Piketty's
`r > g`, dictionary jokes about the origins of "meritocracy". It was sharper
and colder, and it traded reach for in-group density, which is the wrong trade
when being explained at a barbecue is your entire distribution mechanism. The
git history has it if that direction is ever worth revisiting.

**Every tier A design ships with art.** Validation enforces it. See the art
section below.

**Deliberately not:** politician names or faces, children's-media IP, all-caps
declarations, dunks, anything that would embarrass the wearer in a checkout
line.

**The nostalgia line.** The warm register pulls hard toward beloved children's
media, and that is a trap — see `02-legal-guardrails.md`. Take the *feeling* of
those references. Never the character, the catchphrase, or the costume.

**Price point:** $32 base on a soft retail blank. Underpricing is a trap; see
below.

### The art

`src/art.py` draws all 30 designs as one-colour SVG line art — eighteen motifs
composed from primitives in code. Vector rather than generated raster, because
DTF punishes soft edges with a speckled underbase and because a drawing
composed by hand in code is a human authorship story that a generated image is
not (`02-legal-guardrails.md`).

Practical consequences: one-colour prints are the cheapest a supplier can run,
the same file works on a black or a white blank, and re-inking the whole
catalog is one flag (`--ink`). Run `python3 src/art.py --contact-sheet` to see
everything on one page before committing to a drop.

### Name candidates

A warm brand needs a warm name.

| Name | The idea |
|---|---|
| **Kind Regards** | An email signoff and a mission statement. Wry and warm at once, and it signs every package insert and newsletter for free. Strongest candidate. |
| **The Porch Light Co.** | Welcome, stated as an object. Ties to the catalog's best warm designs. |
| **Bleeding Heart Textiles** | Reclaims the insult cheerfully. |
| **Block Party Press** | Community and a small publisher in two words. |
| **The Long Table** | Quiet, inclusive, a little literary. |

Check USPTO and domains before committing. Avoid *Good Neighbor* — "Like a good
neighbor" is a long-standing insurance slogan and the mark is enforced.
`Kind Regards` is the placeholder in `src/shopify_export.py`.

## Unit economics

Run `python3 src/economics.py` for the live model. At the placeholder costs:

| Retail | Gross profit/unit | Margin |
|---|---|---|
| $26 | $5.41 | 20.8% |
| $30 | $9.27 | 30.9% |
| **$32** | **$11.20** | **35.0%** |
| $34 | $13.14 | 38.6% |

**The finding that should change your pricing:** at $30 with free shipping, the
margin is roughly 31%. That is thin for a business that cannot buy traffic —
there is no room to discount, no room for a supplier price increase, and no
room to absorb a bad return rate. $32 is the floor, and $34 is defensible on a
Bella+Canvas blank with a genuinely good joke.

Fixed costs are trivial (~$60/month), so break-even is about 6 shirts a month.
This business does not fail on fixed costs. It fails on traffic.

All input costs are placeholders until a supplier quotes you. Replace them in
`src/economics.py` the moment you have real numbers.

## What success looks like

Five-week targets, launching ~Oct 5:

| Metric | Target | Why |
|---|---|---|
| Orders | 100–150 | Proves the concept sells at all |
| Revenue | $3,200–4,800 | |
| Gross profit | $1,100–1,700 | |
| Email list | 500 | The only asset nobody can take away |
| Conversion rate | 2%+ | Below 1.5% means the jokes or the mockups are weak |
| Sessions needed | ~5,000–7,500 | All organic. This is the hard part. |

These are modest numbers and they are the right ones. The first cycle is a test
of whether the voice lands, not a revenue play. A brand with 500 engaged email
subscribers going into 2028 is worth far more than a one-time $5,000.

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Can't buy ads for political content | **Certain** | High | Organic-first plan; product designed to be screenshot-worthy (`06-marketing.md`) |
| No organic breakout | High | High | Test jokes as posts before making artwork |
| Designs copied | High | Medium | Moat is brand + speed, not artwork (`02-legal-guardrails.md`) |
| Supplier rejects political content | Medium | **Fatal to timeline** | First question asked; two suppliers sampled |
| Payment processor holds funds | Medium | High | Apply week 1; have a backup processor |
| Trademark or publicity claim | Low | High | No names, no faces; `src/risk_check.py` on every design |
| Quality complaints and returns | Medium | Medium | Wash-test samples before choosing a supplier |
| Post-election demand collapse | **Certain** | Medium | 24 of 28 designs are not election-specific |

## The honest summary

This is a reasonable business with a low floor and a low ceiling. Downside is
capped at a few hundred dollars and some weekends. Upside is a small brand with
a real audience, most likely in the low tens of thousands of dollars a year,
concentrated around election cycles.

The two things that decide the outcome are **whether the jokes are actually
funny** and **whether you post consistently enough for one to break out**.
Everything else in this repository is infrastructure around those two variables.

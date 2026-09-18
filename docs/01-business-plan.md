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

**Audience:** progressive, well-read, 28–55. Reads long-form, finished the
book, argues in good faith and enjoys winning. Teachers, librarians, grad
students, nurses, public-sector workers, the union rep who cites the actual
statute.

**Voice: barbed, and the barb is an idea.** The shirt cuts, but it cuts by
knowing something. *MERITOCRACY (n.) Originally A Satire* is an attack and also
a true fact — Michael Young coined the word in 1958 to mock the concept. The
cut and the citation are the same sentence, which is what separates this from
the category default.

The category default is the dunk: the eye-roll, the approval-rating joke, the
insult with no content. That sells to people who already agree and gives a
critic nothing to engage with. A barbed design invites the argument and wins
it.

**The five registers**, tracked in the catalog's `tone` column:

| Tone | What it does | Example |
|---|---|---|
| **barbed** | Cuts, and the cut is a fact or an idea. Carries the brand. | *LAFFER CURVE (n.) A Napkin* |
| **wry** | Argues with a light touch. | *Democracy Is A Group Project* |
| **earnest** | Says it plainly, no joke. | *There's Room* |
| **warm** | Offers something. Kept as counterweight. | *The Librarian Trusted You With It* |
| **sharp** | A dunk with no idea in it. | — |

`src/catalog.py` rejects any **sharp** design placed in tier A. Barbed is
welcome there; an empty dunk is not. That is the whole editorial line.

### The literacy tradeoff

Every design also carries a `literacy` value — what you need to know to get the
joke. This exists because the brief's two goals pull against each other.

*Rewards the reader* and *excludes the outsider* feel identical and are not. A
shirt that makes the wearer feel smart is an asset. A shirt nobody can explain
at a barbecue does not get explained at a barbecue, and with no paid
advertising, being explained is the entire distribution mechanism.

So the launch set is built with a spine and a tail:

- **`general` designs carry reach.** *Decency Is A Policy Position* needs no
  prior reading. These are the ones that travel and bring people to the store.
- **Everything else rewards the in-group.** *r > g* is nearly opaque outside
  it, and that opacity is exactly why the people who get it will buy it.

`src/catalog.py` enforces a floor: at least three `general` designs in tier A,
or validation fails. Without it a launch set drifts entirely into deep cuts
and quietly loses its ability to spread.

**Deliberately not:** politician names or faces, children's-media IP, living
theorists by name, all-caps declarations, dunks with no content.

**Price point:** $32 base on a soft retail blank. This audience is the least
price-sensitive segment in the category and the most annoyed by a cheap blank.

### Name candidates

Earlier shortlists punned on "left" (cold) and then on neighborliness (warm).
Neither fits a brand whose joke is erudition.

| Name | The idea |
|---|---|
| **Citation Needed** | Wikipedia's margin note as a brand. Wry, erudite, in-group, and it is the literal promise of a catalog whose designs are all checkable facts. Strongest candidate. |
| **Marginalia** | What a reader writes in the margin. Quiet and bookish. |
| **Ibid.** | A footnote joke that fits on a hem tag. |
| **The Long Read** | Plain, confident, slightly self-aware. |
| **Kind Regards** | Held over from the warm direction. Still wry, now slightly off-voice. |

Check USPTO and domains before committing. `Kind Regards` remains the
placeholder in `src/shopify_export.py`; switch it once you pick.

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

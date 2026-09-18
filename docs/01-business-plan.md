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

**Audience:** progressive-leaning, terminally online, 25–45, buys merch as
identity signaling and as a gift.

**Voice:** dry and literate. Wordplay, dictionary jokes, understatement. The
kind of thing worn by someone who would be embarrassed by an all-caps slogan.

**Deliberately not:** rage-bait, politician faces, all-caps declarations,
anything that reads as a bumper sticker. That segment is saturated, it is the
legally riskiest, and it commands a lower price.

**Price point:** $32 base. Premium-adjacent, on a soft retail blank. Underpricing
here is a trap — see the economics below.

### Name candidates

All play on "left." Check USPTO and domain availability before committing;
`Left Field Supply Co` is the placeholder in `src/shopify_export.py`.

| Name | The joke |
|---|---|
| **Sinister Goods** | *Sinister* is Latin for "left." Dry, memorable, slightly gothic. |
| **Gauche & Co.** | French for "left," English for "tactless." Doubles perfectly. |
| **Port Side Press** | Nautical "left." Reads like a small publisher. |
| **Bleeding Heart Textiles** | Reclaims the insult. Warmest of the four. |
| **Left Field Supply Co.** | Plain, safe, slightly generic. |

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

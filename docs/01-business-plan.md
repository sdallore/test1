# Business plan

## Scope

**A side project that should pay for beer.** Not a business, and the plan is
built for that: see `05-launch-plan.md`, which tests jokes before spending
money on them.

This matters because the two are not the same project. A business needs an
audience, a cadence, and a reason for anyone to follow it. A side project needs
five good jokes and a marketplace listing. Confusing them is how people spend
$2,000 and six weekends to sell eleven shirts.

## The thesis

Five designs, tested as social posts before anything is printed, listed on a
marketplace that already has buyers. If a design sells, print more. If none do,
you are out two weeks and no money.

The scarce input is the joke. Everything else in this repository is
infrastructure around that one variable, and infrastructure has never sold a
shirt.

## Positioning

**Audience:** progressive-leaning, 28–55, buys merch to say something in public
without starting an argument.

**Voice:** warm, with a little clever mixed in — but the catalog was cut hard
on one test: *does a stranger get the joke in two seconds?* Designs that read
as pleasant sentiment rather than a joke were retired, because without paid
advertising a shirt nobody screenshots is a shirt nobody sees.

## The five

| Design | Why it survived |
|---|---|
| **Nobody Asks The Fire Department For A Copay** | The strongest. A real argument, legible instantly, picks a fight without being mean. |
| **Democracy Is A Group Project** | Everyone has been in a group project. Funny and political at once. |
| **Decency Is A Policy Position** | More statement than joke, but sharp and unmistakable. |
| **I'm With The Banned** | A good pun with proven demand — and thousands of competing listings. A test, not a bet. |
| **Unionize Your Group Chat** | Funny and very online. Narrow audience, so also a test. |

Twenty-five designs were cut to `catalog/retired.csv`. They are not deleted;
nothing stops a retired slogan coming back if it earns it as a post.

### Why the others went

They failed the two-second test. *Shovel The Whole Block* reads as "this person
shovels snow". *Borrow My Ladder* reads as a handyman joke. *There's Room* reads
as nothing at all. Warm is good; warm and invisible is not, because political
merch is an identity purchase — the whole value is a like-minded stranger
reading your shirt and clocking you.

## Unit economics

Run `python3 src/economics.py` for the live model. At $32 on Etsy with
placeholder supplier costs: **~$8.94 profit per shirt, 27.9% margin.**

Fixed costs are near zero, so this cannot fail on overhead. It fails or
succeeds entirely on whether anybody wants the shirts.

**Platform:** Etsy, not Shopify. The $39/month plan only overtakes Etsy above
roughly 17 shirts a month, and Etsy brings buyers who are already searching.
This reverses the earlier recommendation in this repo; the reason is the change
of scope, not new information about Shopify.

## What success looks like

| | |
|---|---|
| Designs clearing the Phase 0 gate | 1 of 5 would be a good result |
| First-month orders | single digits |
| A good first quarter | 20–40 shirts, $180–360 profit |
| A good year | a few hundred dollars, concentrated around elections |

**This replaces an earlier target of 100–150 orders and $3,200–4,800 in the
first cycle.** That figure assumed ~5,000 organic sessions, which assumed a
breakout post, which assumed screenshot-worthy designs — none of it tested.
It was wrong and it is retracted.

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Can't buy ads for political content | **Certain** | High | Organic-first plan; product designed to be screenshot-worthy (`06-marketing.md`) |
| No organic breakout | **High** | Low now | Phase 0 tests jokes as free posts; failing costs two weeks and no money |
| Designs copied | High | Medium | Moat is brand + speed, not artwork (`02-legal-guardrails.md`) |
| Supplier rejects political content | Medium | **Fatal to timeline** | First question asked; two suppliers sampled |
| Marketplace suspends the listing | Low | Medium | Etsy handles payments; keep the source files so relisting is cheap |
| Trademark or publicity claim | Low | High | No names, no faces; `src/risk_check.py` on every design |
| Quality complaints and returns | Medium | Medium | Wash-test samples before choosing a supplier |
| Post-election demand collapse | **Certain** | Low | Side-project scope; 4 of 5 designs are not election-specific |

## The honest summary

Downside is capped at roughly $100 and a few weekends. Upside is a few hundred
dollars a year, more in election years. That is a fine thing for a side project
to be.

The two things that decide it are whether the jokes are actually funny and
whether you post consistently enough for one to travel. Phase 0 answers the
first for free. Nothing in this repository answers it for you.

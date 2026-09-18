# Five-week launch plan

**Today: September 18, 2026. Election Day: November 3, 2026.**

The revenue window is shorter than it looks. With typical DTF drop-ship
turnaround plus transit, **orders placed after roughly October 25 will not
arrive before Election Day.** Confirm the real cutoff with your supplier and
put it on the site — it is both an honest disclosure and the best urgency
driver you will have.

That leaves about five selling weeks, and the store needs to be live for most
of them.

## Critical path

Everything depends on one thing: **the supplier sample.** You cannot price,
photograph, or promise turnaround until a shirt is in your hands. Order samples
in week 1 or the whole timeline slips.

---

## Week 1 — Sept 18–27: supplier and setup

Run these in parallel; none blocks another.

- [ ] Send the vetting questions from `03-supplier-vetting.md` to 3 suppliers
- [ ] **Order samples from the top 2** — highest priority item on this list
- [ ] Pick a brand name; check the USPTO database and domain availability
- [ ] Register the domain
- [ ] File the LLC
- [ ] Start the Shopify trial
- [ ] Open the social accounts and start posting jokes immediately — audience
      building starts before product exists
- [ ] Set up a business bank account and apply for payment processing early;
      underwriting on political merch takes longer than you expect

## Week 2 — Sept 28–Oct 4: product and store

- [ ] Samples arrive. Run the wash test in `03-supplier-vetting.md`. Pick one
      supplier.
- [ ] Lock real per-unit costs into `src/economics.py` and set final pricing
- [ ] Produce artwork for the 11 tier A designs per `04-artwork-spec.md`
- [ ] Run `src/risk_check.py` on every design; resolve every flag
- [ ] Build the store: theme, size chart tied to your exact blank, shipping
      policy, returns policy, terms, privacy
- [ ] `python3 src/shopify_export.py --tiers A --price <final>` and import
- [ ] Add mockups, configure the supplier app, place a real test order end to
      end and let it ship to you

## Week 3 — Oct 5–11: launch

- [ ] Go live. Flip products from draft to active.
- [ ] Announce across every channel
- [ ] Email popup on, 10% welcome offer
- [ ] Seed 20 creators with free shirts
- [ ] Daily short-form posting
- [ ] Watch which designs get added to cart; that is your real signal

## Week 4 — Oct 12–18: drop two and double down

- [ ] Kill the designs with zero add-to-carts; stop promoting them
- [ ] Ship tier B artwork for the themes that are working
- [ ] `python3 src/shopify_export.py --tiers B` and import
- [ ] Email the list about the drop
- [ ] Reactive design: one shirt responding to a news moment, live inside 48h
- [ ] Put the **order by Oct 25** deadline on the site

## Week 5 — Oct 19–25: the peak

This is the highest-volume week of the year for this category. Everything is
urgency.

- [ ] Countdown banner on every page
- [ ] Email on Oct 20, Oct 23, and Oct 25
- [ ] Abandoned-cart email flow on if it isn't already
- [ ] Post multiple times a day
- [ ] Watch supplier turnaround daily; if it slips, move the cutoff *forward*
      and say so publicly

## Oct 26 – Nov 3: after the cutoff

Shipping deadline passed does not mean stop.

- [ ] Switch messaging to evergreen designs with no deadline
- [ ] Keep posting; traffic peaks around Election Day itself
- [ ] Prepare post-election designs for both outcomes, ready to ship Nov 4
- [ ] Write the retrospective: which jokes sold, which channel delivered, what
      the real margin was

## Post-election: the actual question

Political merch demand falls off sharply after an election. Decide in advance
which you are building:

- **A seasonal business** that goes quiet and wakes up for 2028. Low effort,
  real money in cycles.
- **A year-round brand** where politics is one theme among several — labor,
  climate, books, science already generalize past the election. Harder, but
  it's the version that compounds.

The catalog is deliberately weighted toward the second. Only four of the
twenty-eight designs are tied to an election at all.

## Where this plan breaks

Honest failure modes, in order of likelihood:

1. **No supplier will print political content.** Found in week 1 — which is
   exactly why content policy is the first question you ask.
2. **Samples are bad and week 2 restarts.** Budget for it by sampling two
   suppliers at once, not one.
3. **Payment processing gets held in underwriting.** Apply in week 1.
4. **Nothing goes viral.** The most likely outcome. It means a slow start, not
   a dead business — but it means the joke bar wasn't high enough, and the fix
   is better jokes, not more of them.

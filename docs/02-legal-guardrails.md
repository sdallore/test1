# Legal guardrails

Not legal advice. This is the operating checklist; a lawyer signs off before
anything ambiguous goes to print.

## The one rule that matters

**Joke about the idea, not about the person — and offer something rather
than score a point.**

Puns on concepts — bootstraps, the Electoral College, the filibuster, banned
books — carry almost no legal risk. Puns that depend on a specific living
person's name or face carry real risk, and they are also the designs most
likely to be copied within a week. Every tier A design in `catalog/designs.csv`
follows this rule. That is not an accident.

## The four exposures, ranked

### 1. Right of publicity — highest risk

Most US states give a person a cause of action when their name, image, or
recognizable likeness is used commercially without consent. A t-shirt is
commercial use by definition. Political commentary gets meaningful First
Amendment protection, but that protection is strongest for speech *about* a
figure and weakest when the figure's identity is the product being sold.

**Rule: no politician names, no caricatures, no recognizable faces.** Not on
shirts, not in mockups, not in ad creative.

**The same rule covers living thinkers**, and the erudite register walks into
this one constantly. Naming the writer is the obvious move and it is the wrong
one. Long-dead authors are free — Adam Smith, Juvenal, Marx, Gramsci are all
public domain, and a factual sentence about a dead philosopher's published
argument is safe. Living ones are not, and a recently dead one may have an
estate that enforces.

The fix is almost always better design anyway: *r > g* says what *Piketty Was
Right* says, says it to exactly the people who should hear it, and carries no
exposure at all. The scanner flags the second and clears the first.

### 2. Trademark — high risk

Campaign slogans are registered marks. So are party names and newspaper
taglines. Selling apparel bearing them invites a takedown on any marketplace
and a demand letter on your own store. Trademark law also asks whether buyers
might think the mark's owner endorsed or made the product — on merch, that
question gets answered against you more often than people expect.

Parody is a defense, not a shield. It is at its weakest when the parody *is*
the product rather than commentary on it.

**Rule: run `python3 src/risk_check.py "<new slogan>"` before any new design
enters the catalog.** It is a keyword triage tool, not a clearance search. A
clean result means nothing matched its tables, not that a design is safe.

### 2b. Children's media IP — the trap specific to a warm voice

This one deserves its own heading because the brand's own tone leads straight
into it.

A warm, neighborly, slightly nostalgic voice pulls toward the things that
taught a generation what warmth looks like: a red cardigan, a certain street
with puppets on it, a soft-spoken painter and his happy little trees. Those are
owned. Fred Rogers Productions, Sesame Workshop, the Seuss estate, and Bob Ross
Inc. all enforce aggressively, and they enforce against affectionate homage
specifically, because affectionate homage is what dilutes a mark.

**Warmth is not a defense.** A tribute is still a commercial use.

The line runs between the sentiment and the signature:

| Free to use | Not free to use |
|---|---|
| "We're all neighbors" | "Won't you be my neighbor" |
| Neighborliness as a theme | A red cardigan on a cartoon figure |
| Kindness toward children | A specific yellow bird, a specific street |
| Patience, softness, care | "Happy little trees" |

`src/risk_check.py` flags the catchphrases and character names at high
severity. It **cannot see artwork**, and that is where most of this risk
actually lives — a red cardigan with no words on it can evoke a protected
property perfectly well. Visual homage needs a human looking at it and asking
one question: *would a reasonable person think the estate licensed this?*

If the answer is maybe, redraw it.

### 3. Copyright in your own designs — the one that cuts against you

Under current US Copyright Office guidance, material generated purely by AI
without human authorship is **not protectable**. A design you prompted into
existence and shipped as-is can be screenshotted and re-listed by a competitor,
legally, the day it starts selling.

Two consequences:

- Your defensible assets are the **brand, the customer list, and the speed of
  the next drop** — not the artwork. Plan accordingly.
- Human creative input in arrangement, typography, and editing is what creates
  a protectable contribution. Document the process: keep the prompt, the
  variants you rejected, and the edits you made. That record is what an
  authorship claim rests on.

Register the wordmark and logo as a trademark once you have revenue. That is
protectable, and it is the thing worth protecting.

### 4. Platform and processor policy — the quiet one

- Your **printer** may prohibit political content outright. Get their policy in
  writing before you build anything around them. See `03-supplier-vetting.md`.
- Your **payment processor** treats political merch as elevated-risk. Expect
  underwriting review and possibly a rolling reserve. Do not run a launch on a
  single processor with no backup.
- **Marketplaces** apply their own content rules on top of the law, and they
  remove listings first and ask later.

## Pre-print checklist

Nothing goes to the printer until all seven are true.

- [ ] No living person's name, likeness, caricature, or signature
- [ ] No children's-media character, catchphrase, or visual signature —
      including in the artwork, where the scanner cannot look
- [ ] No registered campaign slogan, party name, or organization tagline
- [ ] `src/risk_check.py` returns clear, or a human has reviewed each flag
- [ ] No third-party logo, font, or image without a commercial license
- [ ] Every piece of art traced to a licence that permits commercial use —
      MIT/CC0/public domain, or a signed copyright assignment. Never a web
      image search result
- [ ] Every font used is licensed for commercial print
- [ ] Design is original wordplay, not lifted from a viral post
- [ ] `risk_note` in the catalog is filled in with a real assessment

## Things to have in place before launch

- Terms of service, privacy policy, and a refund policy on the store
- An LLC, so the business's liability is not your personal liability
- A real business address for the required commercial email footer
- Sales tax registration where you have nexus (Shopify calculates, you remit)
- A DMCA agent designation if you ever accept user-submitted designs

# Artwork spec for DTF

DTF prints CMYK plus a white underbase onto film, which is then heat-pressed.
Most of the rules below come from how that underbase is generated.

## File requirements

| Property | Requirement |
|---|---|
| Format | PNG with true alpha transparency |
| Resolution | 300 DPI **at final print size** |
| Color space | sRGB |
| Background | Transparent. Never a white rectangle |
| Canvas | Trimmed to the artwork, no extra padding |
| Text | Converted to outlines before export |

Confirm each of these against your supplier's own spec sheet — they vary, and
theirs wins.

## Print sizes

| Placement | Width | Typical height |
|---|---|---|
| Adult front, full | 11–12 in | up to 14–16 in |
| Left chest | 3–4 in | 3–4 in |
| Back, full | 11–12 in | up to 16 in |

A 12 in wide print at 300 DPI is **3600 px wide**. Design at that size or
larger. Upscaling a small AI render to hit the pixel count does not add detail
— it adds mush, and DTF shows it.

## What breaks in DTF

This is where AI-generated imagery causes the most trouble.

**Soft edges and semi-transparent pixels.** Glows, drop shadows, feathering,
and gradients fading to transparent all produce a speckled, dirty-looking
underbase. Keep alpha binary: a pixel is opaque or it is gone.

**Thin strokes.** Anything under about 1.5–2 pt at print size will break up or
disappear. Check every serif and every apostrophe at 100%.

**Stray pixels.** AI renders leave faint artifacts in the "transparent" area
that are invisible on screen and print as specks. Zoom to 400% and inspect the
background before exporting.

**Neon and fluorescent colors.** Out of CMYK gamut. They will print noticeably
duller. Choose colors you can actually hit.

**Photographic detail on dark shirts.** The underbase makes it look flat and
washed out. Bold vector-style art is the right answer here, which is also the
right answer aesthetically for a punchline shirt.

## Where the art comes from

`assets/icons/` holds vendored artwork, one SVG per motif, drawn by
professional icon designers rather than by this repository. Two MIT-licensed
sets: **Phosphor Icons** and **Tabler Icons**. Their licence texts sit beside
them, and `MANIFEST.json` records which source file each motif came from.

MIT permits commercial use and redistribution and does not require attribution
on the product. Keep the LICENSE files in the repo and you are compliant.

The solid **bold** weight is vendored deliberately. Phosphor's *duotone* style
uses `opacity="0.2"`, and per the failure modes below, partial opacity is
exactly what gives DTF a speckled underbase. A test asserts no vendored asset
carries partial opacity.

## The generator

```bash
python3 src/art.py                      # all designs -> build/art/
python3 src/art.py --tiers A
python3 src/art.py --ink "#1b3a2f"      # one-colour print in another ink
python3 src/art.py --contact-sheet      # every design on one page
python3 src/art.py --art-dir my-art/    # your own art wins over the vendored set
```

Output is one-colour on a 12 x 14 in canvas: the cheapest thing a supplier can
print, and the same file works on a black or a white blank.

**One manual step before the printer:** the type is `<text>`, so it reflows on
a machine without the font. Open the SVG in a vector editor and convert text to
outlines. Pick and licence a real display font while you are there — the files
currently name a Poppins/Futura stack as a placeholder.

## Typography

A slogan is not one centred paragraph. `src/typeset.py` builds a **lockup**:
the words carrying the idea set large in a display face, the connectives
dropped small into a script, each content line scaled to fill the print width.

```
Democracy Is A Group Project     ->     DEMOCRACY
                                           is a
                                     GROUP PROJECT
```

Three rules make it work, and all three came out of looking at rendered output:

- **Connectives drop to script**, but only between two content runs. A phrase
  ending "...Porch Light On" must not strand "On" alone on a script line.
- **At most one script line.** More chops the lockup into confetti.
- **Long phrases break across lines.** A single long line scales *down* to fit
  the width and prints small; breaking it lets every line run large. The target
  is ~11 characters per line for display type.

### The fonts

Vendored in `assets/fonts` with their licences, converted to TTF from
`@fontsource` packages:

| Role | Face | Licence |
|---|---|---|
| `display` | Alfa Slab One | OFL-1.1 |
| `script` | Yellowtail | Apache-2.0 |
| `voice` | Fraunces | OFL-1.1 |

OFL and Apache both permit commercial use and embedding. OFL requires the
licence travel with the font, which is why the LICENSE files sit beside them.

Swapping the palette is a file swap: replace `assets/fonts/display.ttf` and
every design re-sets in the new face.

## Upgrading the art

Vendored icons are a floor, not a ceiling. They are clean and consistent, and
they are also generic — the same icons appear in thousands of apps, and nothing
about them is yours. Three ways up, in increasing order of both cost and payoff:

**1. AI-generated cartoon art.** Cheapest and fastest. Generate in whatever tool
you use, then prep it (below). Two honest caveats, both already documented
elsewhere in this repo: purely AI-generated images are not copyrightable under
current US guidance, so a competitor can legally copy a winner
(`02-legal-guardrails.md`), and raster output needs real cleanup before it is
printable.

`src/prompts.py` generates the prompts for you, one per design, in
Midjourney / DALL-E / Stable Diffusion / generic flavours:

```bash
python3 src/prompts.py --format dalle --out build/prompts.md
python3 src/prompts.py --tiers A --format midjourney
```

Per-design subjects live in `catalog/art-prompts.csv`; the shared style block
lives in the script, so every design comes back in the same visual language.
The negative constraints matter more than the positive ones — gradients, soft
shadows, glows and texture are exactly what ruin a DTF underbase, and a test
asserts the style block still bans them.

Two practical rules the generated file repeats: generate at the largest size
the tool offers (12in at 300 DPI is 3600px, and upscaling adds mush, not
detail), and pick the variation with the **cleanest edges** rather than the
most detail, because detail is what breaks in DTF.

**2. Commission an illustrator.** $50–150 per design on the usual marketplaces.
For the twelve tier A designs that is roughly $600–1,800. You get art nobody
else has, in a consistent hand, and — if the contract says so — you own the
copyright, which is the one thing AI art cannot give you. **For a brand you
intend to keep, this is the right answer**, and it is cheap next to what a
distinctive look is worth when you cannot buy ads.

Put a copyright assignment in writing. "Work made for hire" is not automatic
for an independent contractor; without an assignment clause the illustrator
keeps the copyright and you have a licence.

**3. Public domain source art.** Works published before 1929 are public domain
in the US, and museum open-access collections (the Met, Smithsonian, NYPL, the
Biodiversity Heritage Library) release high-resolution scans under CC0.
Vintage engravings and seed-catalogue illustration suit a warm, literate brand
and cost nothing. Verify each item's rights statement individually — "it is
old" is not the same as "this scan is CC0".

**Do not** pull generic clip art off a web search. Those images are somebody's
copyright, and putting one on a shirt you sell is commercial infringement,
whatever the site calls itself. The three routes above are the clean ones.

## Getting your own art into the pipeline

`src/prep_art.py` does the last mile — background, alpha, tracing — in one
command:

```bash
python3 src/prep_art.py ~/Downloads/board.webp --motif posterboard
python3 src/art.py --art-dir art --tiers A
```

It runs three steps, each fixing something that breaks a print:

1. **Background removal** floods in from the edges rather than keying every
   white pixel, so white *inside* the artwork survives.
2. **Alpha hardening** forces every pixel fully opaque or fully clear. This is
   the one that matters most: a feathered edge is a column of semi-transparent
   pixels, and the printer turns those into a speckled white underbase. The
   tool reports how many it fixed.
3. **Tracing** makes it vector, so it scales to any print size. Generated
   images are typically ~1024px; a 12in print at 300 DPI needs 3600px.

### The enclosed-white trap

An edge flood cannot reach background walled off by the artwork's own outline —
the gap between a pair of easel legs, sky inside a window frame. That white
stays opaque. **It is invisible on a white mockup and prints as white blobs on
a dark shirt**, which is a defect you will not see until the sample arrives.

`prep_art.py` counts those pixels and warns. Re-run with `--key-white` when the
art has no intentional white:

```bash
python3 src/prep_art.py board.webp --motif posterboard --key-white
```

### Colour is free on DTF

Earlier drafts of this repo called one-colour art "the cheapest thing to
print". That is **screen-printing logic and it is wrong here.** Screen printing
charges per colour because each colour is a separate screen. DTF prints a full
CMYK image plus a white underbase in a single pass, so cost tracks film area,
not colour count.

Full-colour cartoon art therefore costs the same as one-colour line art. Use
colour. `art.py` detects artwork that carries its own fills and leaves the
palette alone; `--ink` then only sets the type colour, which is what you change
between a light and a dark garment.

## Where AI fits, honestly## Where AI fits, honestly

- **Excellent:** concept volume, pun variations, alternate phrasings, layout
  ideas, product copy, mockup scene backgrounds.
- **Poor:** the final print file. AI output is raster, soft-edged, and often has
  mangled lettering — and typography *is* the design on a punchline shirt.

The workflow that works: AI for fifty ideas, you pick three, then set the type
properly in a vector tool and export a clean PNG at 300 DPI. Keep the rejected
variants; per `02-legal-guardrails.md`, that record is your evidence of human
authorship.

This is why `src/art.py` draws with code rather than generating images. Vector
geometry is what DTF wants, and a drawing composed by hand in code is a human
authorship story that a generated raster is not.

## Pre-export checklist

- [ ] 300 DPI at final print size, not upscaled
- [ ] Transparent background, no white box
- [ ] Zoomed to 400% and checked for stray pixels
- [ ] No semi-transparent edges, glows, or shadows
- [ ] All strokes at least 2 pt at print size
- [ ] Text converted to outlines
- [ ] Every font commercially licensed
- [ ] Previewed on both black and white blanks
- [ ] Filename matches the catalog ID, e.g. `D001-bootstraps.png`

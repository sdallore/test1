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

A prompt shape that produces printable results:

> flat vector illustration of a **[subject]**, bold uniform outlines, two flat
> colours, no gradients, no shading, no drop shadows, no texture, plain white
> background, centred, full object in frame, screen-print poster style

The negative constraints matter more than the positive ones. Gradients, soft
shadows, glows and texture are the things that ruin a DTF underbase.

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

Whichever route you pick, the last mile is the same:

1. Remove the background so it is genuinely transparent, not white.
2. Harden the alpha — no feathered edges, no semi-transparent pixels.
3. Trace it to vector (Illustrator Image Trace, Inkscape Trace Bitmap, or a
   paid vectoriser). Skip this only if the art is already vector.
4. Save as `<motif>.svg` — the filename must match the `motif` column in
   `catalog/designs.csv`.
5. `python3 src/art.py --art-dir my-art/`

Anything in `--art-dir` overrides the vendored set for that motif, so you can
upgrade one design at a time and leave the rest working.

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

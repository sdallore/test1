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

## Where AI fits, honestly

- **Excellent:** concept volume, pun variations, alternate phrasings, layout
  ideas, product copy, mockup scene backgrounds.
- **Poor:** the final print file. AI output is raster, soft-edged, and often has
  mangled lettering — and typography *is* the design on a punchline shirt.

The workflow that works: AI for fifty ideas, you pick three, then set the type
properly in a vector tool and export a clean PNG at 300 DPI. Keep the rejected
variants; per `02-legal-guardrails.md`, that record is your evidence of human
authorship.

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

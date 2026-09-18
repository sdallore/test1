# Your own artwork

SVGs here override the vendored set in `assets/icons/`, one motif at a time.
The filename must match the `motif` column in `catalog/designs.csv`.

```bash
# raster from an image generator -> print-ready SVG here
python3 src/prep_art.py ~/Downloads/board.webp --motif posterboard

# render the shirts with it
python3 src/art.py --art-dir art --tiers A                  # light garment
python3 src/art.py --art-dir art --tiers A --ink "#f4efe6"  # dark garment
```

`--ink` only colours the type. Full-colour artwork keeps its own palette.

Add `--key-white` when the art has no intentional white: the edge flood cannot
reach background walled off by the artwork itself, and that leftover white is
invisible on a white mockup but prints as blobs on a dark shirt.

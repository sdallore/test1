"""Generate print-ready SVG artwork for every design in the catalog.

Vector, not raster. `docs/04-artwork-spec.md` explains why that matters for
DTF: hard edges keep the white underbase clean, and vector scales to any print
size without the mush an upscaled AI render produces.

    python3 src/art.py                      # all designs -> build/art/
    python3 src/art.py --tiers A
    python3 src/art.py --ink "#1b3a2f"      # one-color print in another ink
    python3 src/art.py --contact-sheet      # every design on one page

Artwork comes from assets/icons (MIT-licensed, vendored) rather than being
drawn here. Pass --art-dir to override any motif with your own SVG, which is
how commissioned or AI-generated art gets into the pipeline.

Output is one-colour, the cheapest thing a supplier can print and the most
forgiving on a blank of any colour.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog import Design, load  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / "build" / "art"

# 12 x 14 inches, the standard adult front print area. One unit = 0.01in, so
# the whole canvas is 1200 x 1400 units and stroke widths read directly in
# hundredths of an inch.
W, H = 1200, 1400
MOTIF_CY = 430       # motif centre, in the upper third
MOTIF_SIZE = 560     # motif box on the 1200-wide canvas
TEXT_TOP = 880

FONT_STACK = "Poppins, Futura, 'Century Gothic', 'Trebuchet MS', sans-serif"


# --- motif assets ----------------------------------------------------------
# Artwork is vendored, not drawn here. assets/icons holds MIT-licensed icons
# (Phosphor and Tabler, see the LICENSE files beside them) in their solid
# "bold" weight: filled paths with no strokes and no partial opacity, which is
# what DTF wants. See docs/04-artwork-spec.md.
#
# To use your own art instead, drop an SVG named <motif>.svg into a directory
# and pass --art-dir. Anything there wins over the vendored set.

ASSET_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"

# Icons whose source viewBox is not the 256-unit Phosphor grid.
VIEWBOX_OVERRIDES = {"hydrant": 24.0}

# Motifs drawn more than once, side by side, because the slogan is plural.
REPEATS = {"houses": 2}

_ASSET_CACHE: dict[Path, tuple[str, float, dict[str, str]]] = {}


def load_motif(name: str, art_dir: Path | None = None) -> tuple[str, float, dict] | None:
    """Return (inner markup, viewBox size, paint attributes) for a motif."""
    for base in ([art_dir] if art_dir else []) + [ASSET_DIR]:
        if base is None:
            continue
        f = base / f"{name}.svg"
        if not f.exists():
            continue
        if f in _ASSET_CACHE:
            return _ASSET_CACHE[f]
        raw = f.read_text(encoding="utf-8")
        head = re.search(r"<svg([^>]*)>", raw, flags=re.S)
        attrs = head.group(1) if head else ""
        inner = re.sub(r"^.*?<svg[^>]*>", "", raw, flags=re.S)
        inner = re.sub(r"</svg>\s*$", "", inner).strip()

        box = VIEWBOX_OVERRIDES.get(name, 256.0)
        m = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', attrs)
        if m:
            box = max(float(m.group(1)), float(m.group(2)))

        # Carry the source's own paint attributes. Without this a stroke-drawn
        # icon (Tabler sets fill="none" on the <svg>) inherits our fill and
        # prints as a solid blob.
        carried = {}
        for key in ("fill", "stroke", "stroke-width", "stroke-linecap",
                    "stroke-linejoin"):
            got = re.search(rf'\b{key}="([^"]*)"', attrs)
            if got:
                carried[key] = got.group(1)
        _ASSET_CACHE[f] = (inner, box, carried)
        return _ASSET_CACHE[f]
    return None


def available_motifs(art_dir: Path | None = None) -> set[str]:
    found = {f.stem for f in ASSET_DIR.glob("*.svg")}
    if art_dir and art_dir.exists():
        found |= {f.stem for f in art_dir.glob("*.svg")}
    return found


# --- typography ------------------------------------------------------------

def wrap(text: str, max_chars: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def lay_out_text(slogan: str) -> tuple[list[str], float]:
    """Wrap the slogan and pick a font size that fits the print width."""
    best: tuple[list[str], float] | None = None
    for max_chars in range(9, 30):
        lines = wrap(slogan, max_chars)
        if len(lines) > 4:
            continue
        longest = max(len(line) for line in lines)
        # Geometric sans averages ~0.56em per character.
        size = min(150.0, 980 / (longest * 0.56))
        # Keep the block inside the canvas.
        if TEXT_TOP + len(lines) * size * 1.22 > H - 60:
            continue
        if best is None or size > best[1]:
            best = (lines, size)
    if best is None:
        lines = wrap(slogan, 22)
        return lines, 70.0
    return best


def text_elements(slogan: str, ink: str) -> list[str]:
    lines, size = lay_out_text(slogan)
    leading = size * 1.22
    block = len(lines) * leading
    start = TEXT_TOP + (H - 80 - TEXT_TOP - block) / 2 + size * 0.82
    out = [
        f'<g font-family="{FONT_STACK}" font-size="{size:.0f}" font-weight="700" '
        f'fill="{ink}" stroke="none" text-anchor="middle" letter-spacing="1">'
    ]
    for i, text in enumerate(lines):
        y = start + i * leading
        out.append(f'<text x="{W/2:.0f}" y="{y:.0f}">{html.escape(text)}</text>')
    out.append("</g>")
    return out


# --- rendering -------------------------------------------------------------

def motif_elements(name: str, ink: str, art_dir: Path | None = None) -> list[str]:
    loaded = load_motif(name, art_dir)
    if loaded is None:
        return []
    inner, box, carried = loaded
    scale = MOTIF_SIZE / box
    count = REPEATS.get(name, 1)
    gap = MOTIF_SIZE * 0.14
    total = count * MOTIF_SIZE + (count - 1) * gap

    paint = dict(carried) or {"fill": "currentColor"}
    # "currentColor" resolves against the group's color, so one ink drives both
    # filled and stroked artwork.
    if paint.get("stroke") == "none":
        paint.pop("stroke")
    if "stroke" in paint and paint.get("fill") == "none":
        # A stroked icon scales down with the viewBox; keep the printed weight
        # clear of the DTF minimum.
        paint["stroke-width"] = f"{max(float(paint.get('stroke-width', 2)), 2.0):.2f}"
    attrs = " ".join(f'{k}="{v}"' for k, v in paint.items())
    out = [f'<g color="{ink}" {attrs}>']
    for i in range(count):
        x = W / 2 - total / 2 + i * (MOTIF_SIZE + gap)
        y = MOTIF_CY - MOTIF_SIZE / 2
        out.append(f'<g transform="translate({x:.1f} {y:.1f}) scale({scale:.5f})">')
        out.append(inner)
        out.append("</g>")
    out.append("</g>")
    return out


def artwork_elements(design: Design, ink: str, art_dir: Path | None = None) -> list[str]:
    out: list[str] = []
    if design.motif != "none":
        out.extend(motif_elements(design.motif, ink, art_dir))
    out.extend(text_elements(design.slogan, ink))
    return out


def render(design: Design, ink: str, art_dir: Path | None = None) -> str:
    body = "\n    ".join(artwork_elements(design, ink, art_dir))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="12in" height="14in" '
        f'viewBox="0 0 {W} {H}">\n'
        f'  <title>{html.escape(design.slogan)}</title>\n'
        f'  <g id="{design.id}">\n    {body}\n  </g>\n'
        f'</svg>\n'
    )


def contact_sheet(designs: list[Design], ink: str, art_dir: Path | None = None) -> str:
    """Every design on one page, for picking which ones to print."""
    cols = 5
    cell_w, cell_h = 360, 460
    rows = (len(designs) + cols - 1) // cols
    sheet_w = cols * cell_w + 80
    sheet_h = rows * cell_h + 140

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {sheet_w} {sheet_h}" '
        f'width="{sheet_w}" height="{sheet_h}">',
        f'<rect width="{sheet_w}" height="{sheet_h}" fill="#f7f4ee"/>',
        f'<text x="40" y="64" font-family="{FONT_STACK}" font-size="38" '
        f'font-weight="700" fill="{ink}">Design catalog &#8212; {len(designs)} shirts</text>',
    ]
    scale = (cell_w - 50) / W
    for i, d in enumerate(designs):
        cx = 40 + (i % cols) * cell_w
        cy = 110 + (i // cols) * cell_h
        parts.append(
            f'<rect x="{cx}" y="{cy}" width="{cell_w - 24}" height="{cell_h - 30}" '
            f'rx="14" fill="#ffffff" stroke="#ded7ca" stroke-width="2"/>'
        )
        parts.append(f'<g transform="translate({cx + 13} {cy + 16}) scale({scale:.4f})">')
        parts.extend(artwork_elements(d, ink, art_dir))
        parts.append("</g>")
        parts.append(
            f'<text x="{cx + 14}" y="{cy + cell_h - 44}" font-family="{FONT_STACK}" '
            f'font-size="17" fill="#8a8073">{d.id} &#183; tier {d.tier} '
            f'&#183; {d.tone}</text>'
        )
    parts.append("</svg>\n")
    return "\n".join(parts)


def slug(design: Design) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", design.slogan.lower()).strip("-")
    return f"{design.id}-{base[:44].rstrip('-')}.svg"


def main() -> None:
    p = argparse.ArgumentParser(description="Generate SVG artwork for the catalog.")
    p.add_argument("--tiers", nargs="+", default=["A", "B", "C"])
    p.add_argument("--ink", default="#141414", help="single print colour")
    p.add_argument("--contact-sheet", action="store_true")
    p.add_argument("--art-dir", type=Path, default=None,
                   help="your own <motif>.svg files; these override the vendored set")
    p.add_argument("--out", type=Path, default=OUT_DIR)
    args = p.parse_args()

    designs = [d for d in load() if d.tier in args.tiers]
    args.out.mkdir(parents=True, exist_ok=True)

    for d in designs:
        (args.out / slug(d)).write_text(render(d, args.ink, args.art_dir), encoding="utf-8")

    have = available_motifs(args.art_dir)
    missing = sorted({d.motif for d in designs if d.motif not in have and d.motif != "none"})
    type_only = [d.id for d in designs if d.motif == "none"]

    print(f"{len(designs)} SVGs -> {args.out}")
    if type_only:
        print(f"type-only (no motif): {', '.join(type_only)}")
    if missing:
        print(f"  ! motifs with no drawing: {', '.join(missing)}")

    if args.contact_sheet:
        sheet = args.out.parent / "contact-sheet.svg"
        sheet.write_text(contact_sheet(designs, args.ink, args.art_dir), encoding="utf-8")
        print(f"contact sheet -> {sheet}")

    if args.art_dir:
        print(f"art overrides from {args.art_dir}")
    print("\nOne-colour artwork, the cheapest thing a supplier can print.")
    print("Before sending to a printer: convert the <text> to outlines in a")
    print("vector editor, or the type will reflow on a machine without the font.")


if __name__ == "__main__":
    main()

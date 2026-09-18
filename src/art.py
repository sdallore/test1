"""Generate print-ready SVG artwork for every design in the catalog.

Vector, not raster. `docs/04-artwork-spec.md` explains why that matters for
DTF: hard edges keep the white underbase clean, and vector scales to any print
size without the mush an upscaled AI render produces.

    python3 src/art.py                      # all designs -> build/art/
    python3 src/art.py --tiers A
    python3 src/art.py --ink "#1b3a2f"      # one-color print in another ink
    python3 src/art.py --contact-sheet      # every design on one page

Output is one-color line art, which is the cheapest thing to print and the
most forgiving on a blank of any color.
"""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog import Design, load  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / "build" / "art"

# 12 x 14 inches, the standard adult front print area. One unit = 0.01in, so
# the whole canvas is 1200 x 1400 units and stroke widths read directly in
# hundredths of an inch.
W, H = 1200, 1400
STROKE = 13          # 0.13in, comfortably above the 2pt DTF minimum
MOTIF_CY = 440       # motif sits in the upper third
MOTIF_SCALE = 1.7    # motifs are drawn in a ~400-unit box; fill the print
TEXT_TOP = 880

FONT_STACK = "Poppins, Futura, 'Century Gothic', 'Trebuchet MS', sans-serif"


# --- primitives ------------------------------------------------------------

def line(x1: float, y1: float, x2: float, y2: float) -> str:
    return f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}"/>'


def rect(x: float, y: float, w: float, h: float, r: float = 0) -> str:
    return f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{r:.0f}"/>'


def circle(cx: float, cy: float, r: float) -> str:
    return f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}"/>'


def path(d: str) -> str:
    return f'<path d="{d}"/>'


def poly(points: list[tuple[float, float]], close: bool = True) -> str:
    pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in points)
    tag = "polygon" if close else "polyline"
    return f'<{tag} points="{pts}"/>'


# --- motifs ----------------------------------------------------------------
# Each returns elements drawn around the origin, roughly within a 400-unit box.
# They are translated into place by render().

def m_shovel() -> list[str]:
    return [
        path("M -46 -190 q 46 -40 92 0"),           # D-grip
        line(-46, -190, -46, -150), line(46, -190, 46, -150),
        line(-46, -150, 46, -150),
        line(0, -150, 0, 20),                        # shaft
        path("M -90 20 L 90 20 L 74 130 q -74 42 -148 0 Z"),
        line(-74, 68, 74, 68),                       # step edge
    ]


def m_wateringcan() -> list[str]:
    return [
        rect(-84, -70, 172, 150, 22),                # body
        line(-100, -70, 100, -70),                   # rim
        path("M -84 -22 L -206 34 L -190 76 L -80 30"),      # spout, angled down
        line(-214, 22, -196, 88),                    # rose face
        path("M 34 -70 q 84 10 48 96"),              # handle
        line(-212, 122, -212, 158),                  # water
        line(-172, 136, -172, 172), line(-252, 140, -252, 176),
        rect(-60, 80, 120, 18, 8),                   # foot
    ]


def m_porchlight() -> list[str]:
    return [
        line(-96, -178, 96, -178),                   # mount
        line(0, -178, 0, -140),
        rect(-34, -212, 68, 26, 6),                  # wall mount
        poly([(-84, -140), (84, -140), (58, 34), (-58, 34)]),
        rect(-96, -158, 192, 20, 8),                 # cap
        circle(0, -58, 30),                          # bulb
        line(0, -88, 0, -104),
        line(-58, 34, 58, 34),
        line(0, 34, 0, 62),
        line(-128, 96, -92, 62),                     # light
        line(0, 106, 0, 142), line(128, 96, 92, 62),
    ]


def m_posterboard() -> list[str]:
    return [
        poly([(-210, -130), (-96, -160), (-96, 120), (-210, 150)]),
        rect(-96, -160, 192, 280),
        poly([(96, -160), (210, -130), (210, 150), (96, 120)]),
        line(-62, -112, 62, -112), line(-62, -76, 62, -76),   # title block
        line(-62, -20, 62, -20), line(-62, 16, 30, 16),
        line(-180, -70, -126, -70), line(-180, -28, -126, -28),
        line(126, -70, 180, -70), line(126, -28, 180, -28),
    ]


def m_seal() -> list[str]:
    pts = []
    import math
    for i in range(24):
        a = i * math.pi / 12
        r = 150 if i % 2 == 0 else 128
        pts.append((r * math.cos(a), r * math.sin(a)))
    return [
        poly(pts),
        circle(0, 0, 104),
        line(-48, -14, -14, 24), line(-14, 24, 52, -30),      # check
        poly([(-56, 140), (-56, 236), (-18, 206), (16, 236), (16, 140)], close=False),
    ]


def m_books() -> list[str]:
    return [
        rect(-150, 58, 300, 54, 8),
        line(-124, 58, -124, 112),
        rect(-132, 4, 268, 54, 8),
        line(108, 4, 108, 58),
        rect(-150, -50, 292, 54, 8),
        line(-118, -50, -118, 4),
        rect(166, -142, 74, 200, 8),                 # upright book
        line(188, -142, 188, 58),                    # spine
        line(166, -104, 240, -104),
    ]


def m_chair() -> list[str]:
    return [
        rect(-96, -170, 192, 150, 18),               # back
        line(-58, -140, -58, -50), line(0, -140, 0, -50), line(58, -140, 58, -50),
        path("M -122 -20 L 122 -20 L 104 34 L -104 34 Z"),    # seat
        line(-96, 34, -110, 168), line(96, 34, 110, 168),
        line(-72, 100, 72, 100),
    ]


def m_librarycard() -> list[str]:
    return [
        path("M -190 -120 L 148 -120 L 190 -78 L 190 120 L -190 120 Z"),
        path("M 148 -120 L 148 -78 L 190 -78"),      # corner fold
        line(-150, -60, 60, -60),
        line(-150, -14, 110, -14),
        line(-150, 32, 20, 32),
        rect(-150, 66, 120, 34, 6),                  # due-date box
    ]


def m_ladder() -> list[str]:
    return [
        line(-96, -200, -128, 200), line(96, -200, 128, 200),
        line(-88, -100, 88, -100),
        line(-96, -16, 96, -16),
        line(-104, 68, 104, 68),
        line(-112, 152, 112, 152),
    ]


def m_tree() -> list[str]:
    return [
        path("M -20 200 L -20 40 q 0 -40 -52 -70"),  # trunk + branch
        path("M 20 200 L 20 20 q 0 -46 60 -78"),
        rect(-30, 196, 60, 16, 6),
        path("M 0 -210 q 132 24 108 128 q 52 58 -16 104 "
             "q -46 36 -92 8 q -46 28 -92 -8 q -68 -46 -16 -104 "
             "q -24 -104 108 -128 Z"),
    ]


def m_hydrant() -> list[str]:
    return [
        path("M -58 -150 q 58 -46 116 0"),           # dome
        line(-58, -150, 58, -150),
        rect(-76, -150, 152, 26, 8),
        path("M -70 -124 L 70 -124 L 70 96 L -70 96 Z"),
        line(-70, -56, 70, -56),
        rect(-136, -46, 66, 54, 12),                 # side nozzles
        rect(70, -46, 66, 54, 12),
        rect(-110, 96, 220, 34, 10),                 # base
    ]


def m_casserole() -> list[str]:
    return [
        path("M -170 -10 L 170 -10 L 140 110 q -140 40 -280 0 Z"),
        rect(-206, -46, 412, 36, 14),                # lid rim
        path("M -206 -46 q 206 -76 412 0"),
        circle(0, -92, 20),                          # knob
        path("M -70 -150 q 26 -34 0 -68"),           # steam
        path("M 0 -166 q 26 -34 0 -68"),
        path("M 70 -150 q 26 -34 0 -68"),
    ]


def m_mailbox() -> list[str]:
    return [
        path("M -140 30 L -140 -60 q 140 -84 280 0 L 140 30 Z"),
        line(-140, 30, 140, 30),
        path("M 84 -78 L 84 30"),                    # door seam
        circle(112, -16, 14),
        line(140, -60, 206, -60), line(206, -60, 206, -124),  # flag
        rect(176, -124, 44, 30, 4),
        line(0, 30, 0, 210),                         # post
        line(-52, 210, 52, 210),
    ]


def m_tray() -> list[str]:
    return [
        rect(-210, -100, 420, 220, 26),
        rect(-180, -70, 150, 90, 12),
        rect(-180, 32, 150, 58, 12),
        rect(10, -70, 170, 70, 12),
        path("M 40 22 L 40 90 L 150 90 L 150 22 Z"), # milk carton
        path("M 40 22 L 95 -18 L 150 22"),
    ]


def m_houses() -> list[str]:
    def house(dx: float) -> list[str]:
        return [
            poly([(dx - 110, -10), (dx, -110), (dx + 110, -10)], close=False),
            rect(dx - 90, -10, 180, 150),
            rect(dx - 26, 66, 52, 74, 4),            # door
            rect(dx - 66, 20, 34, 34, 3),
            rect(dx + 32, 20, 34, 34, 3),
        ]
    return house(-150) + house(150) + [
        line(-46, 140, 46, 140),                     # shared path
        path("M -40 92 q 40 -46 80 0"),              # arc between them
    ]


def m_ballotbox() -> list[str]:
    return [
        rect(-160, -20, 320, 200, 16),               # box
        line(-136, -24, -62, -24),                   # slot, either side of ballot
        line(62, -24, 136, -24),
        path("M -62 -196 L 62 -196 L 62 -26 L -62 -26 Z"),   # ballot in the slot
        line(-36, -160, 36, -160),
        line(-36, -128, 36, -128),
        line(-34, -96, -12, -74), line(-12, -74, 34, -120),  # a mark on it
        line(-120, 92, 120, 92),
        line(-120, 138, 120, 138),
    ]


def m_table() -> list[str]:
    return [
        rect(-240, -30, 480, 34, 10),                # top
        line(-190, 4, -190, 150), line(190, 4, 190, 150),
        line(-190, 150, -120, 150), line(190, 150, 120, 150),
        circle(-150, -78, 34), circle(-50, -78, 34),  # place settings
        circle(50, -78, 34), circle(150, -78, 34),
        circle(-250, -78, 34),                       # the extra one
    ]


def m_door() -> list[str]:
    return [
        rect(-170, -200, 340, 400, 8),               # frame
        path("M -130 -160 L 90 -190 L 90 190 L -130 160 Z"),  # ajar leaf
        circle(50, 0, 16),
        line(-130, -160, -130, 160),
        line(130, -168, 130, 168),
    ]


MOTIFS = {
    "shovel": m_shovel, "wateringcan": m_wateringcan, "porchlight": m_porchlight,
    "posterboard": m_posterboard, "seal": m_seal, "books": m_books,
    "chair": m_chair, "librarycard": m_librarycard, "ladder": m_ladder,
    "tree": m_tree, "hydrant": m_hydrant, "casserole": m_casserole,
    "mailbox": m_mailbox, "tray": m_tray, "houses": m_houses,
    "ballotbox": m_ballotbox, "table": m_table, "door": m_door,
}


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

def artwork_elements(design: Design, ink: str) -> list[str]:
    out: list[str] = []
    builder = MOTIFS.get(design.motif)
    if builder:
        out.append(
            f'<g transform="translate({W/2:.0f} {MOTIF_CY}) scale({MOTIF_SCALE})" fill="none" '
            f'stroke="{ink}" stroke-width="{STROKE / MOTIF_SCALE:.1f}" '
            'stroke-linecap="round" stroke-linejoin="round">'
        )
        out.extend(builder())
        out.append("</g>")
    out.extend(text_elements(design.slogan, ink))
    return out


def render(design: Design, ink: str) -> str:
    body = "\n    ".join(artwork_elements(design, ink))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="12in" height="14in" '
        f'viewBox="0 0 {W} {H}">\n'
        f'  <title>{html.escape(design.slogan)}</title>\n'
        f'  <g id="{design.id}">\n    {body}\n  </g>\n'
        f'</svg>\n'
    )


def contact_sheet(designs: list[Design], ink: str) -> str:
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
        parts.extend(artwork_elements(d, ink))
        parts.append("</g>")
        parts.append(
            f'<text x="{cx + 14}" y="{cy + cell_h - 44}" font-family="{FONT_STACK}" '
            f'font-size="17" fill="#8a8073">{d.id} &#183; tier {d.tier} '
            f'&#183; {d.tone}</text>'
        )
    parts.append("</svg>\n")
    return "\n".join(parts)


def slug(design: Design) -> str:
    import re
    base = re.sub(r"[^a-z0-9]+", "-", design.slogan.lower()).strip("-")
    return f"{design.id}-{base[:44].rstrip('-')}.svg"


def main() -> None:
    p = argparse.ArgumentParser(description="Generate SVG artwork for the catalog.")
    p.add_argument("--tiers", nargs="+", default=["A", "B", "C"])
    p.add_argument("--ink", default="#141414", help="single print colour")
    p.add_argument("--contact-sheet", action="store_true")
    p.add_argument("--out", type=Path, default=OUT_DIR)
    args = p.parse_args()

    designs = [d for d in load() if d.tier in args.tiers]
    args.out.mkdir(parents=True, exist_ok=True)

    for d in designs:
        (args.out / slug(d)).write_text(render(d, args.ink), encoding="utf-8")

    missing = sorted({d.motif for d in designs if d.motif not in MOTIFS and d.motif != "none"})
    type_only = [d.id for d in designs if d.motif == "none"]

    print(f"{len(designs)} SVGs -> {args.out}")
    if type_only:
        print(f"type-only (no motif): {', '.join(type_only)}")
    if missing:
        print(f"  ! motifs with no drawing: {', '.join(missing)}")

    if args.contact_sheet:
        sheet = args.out.parent / "contact-sheet.svg"
        sheet.write_text(contact_sheet(designs, args.ink), encoding="utf-8")
        print(f"contact sheet -> {sheet}")

    print("\nThese are one-colour line drawings, the cheapest thing to print.")
    print("Before sending to a printer: convert the <text> to outlines in a")
    print("vector editor, or the type will reflow on a machine without the font.")


if __name__ == "__main__":
    main()

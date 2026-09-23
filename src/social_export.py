"""Build the week-one post kit: vertical cards plus captions to paste.

Posting itself stays manual -- TikTok and Instagram both forbid automated
posting through anything but their own APIs, and a brand-new account is the
easiest kind to suspend. What this removes is the fiddly part: sizing art for
a vertical feed and retyping captions.

    python3 src/social_export.py              # cards + captions
    python3 src/social_export.py --svg-only   # skip rasterising

Output lands in build/posts/.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog import load  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE = ROOT / "catalog" / "week-one.csv"
ART_DIR = ROOT / "build" / "art"
OUT_DIR = ROOT / "build" / "posts"

# A 1080x1920 feed card. The platform draws its own furniture on top: a status
# bar up top, an action rail down the right, caption and username along the
# bottom. Art that ignores those gets a thumb over it.
W, H = 1080, 1920
SAFE_X, SAFE_W = 100, 780
SAFE_Y, SAFE_H = 300, 910
HANDLE_Y = 1320

BACKGROUND = "#F7F3EA"
HANDLE = "@deptofdecency"

# Chromium ships under a different name on most machines; take the first hit.
BROWSERS = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "chromium", "chromium-browser", "google-chrome", "google-chrome-stable",
]

CARD = """<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="{w}" height="{h}" fill="{bg}"/>
  <svg x="{x}" y="{y}" width="{cw}" height="{ch}" viewBox="{viewbox}">
{inner}
  </svg>
  <text x="{cx}" y="{hy}" text-anchor="middle" font-family="Georgia, serif"
        font-size="30" letter-spacing="2" fill="#141414" opacity="0.55">{handle}</text>
</svg>
"""


def find_browser() -> str | None:
    for candidate in BROWSERS:
        if Path(candidate).exists():
            return candidate
        found = shutil.which(candidate)
        if found:
            return found
    return None


def design_svg(design_id: str) -> Path:
    """The rendered design for an id, whatever slug art.py gave it."""
    matches = sorted(ART_DIR.glob(f"{design_id}-*.svg"))
    if not matches:
        raise SystemExit(
            f"No art for {design_id} in {ART_DIR}. Run: python3 src/art.py --art-dir art/"
        )
    return matches[0]


def unwrap(svg: str) -> tuple[str, str]:
    """Strip the outer <svg> so the design can nest inside the card."""
    open_tag = re.search(r"<svg\b[^>]*>", svg)
    if not open_tag:
        raise ValueError("no <svg> element found")
    viewbox = re.search(r'viewBox="([^"]+)"', open_tag.group(0))
    if not viewbox:
        raise ValueError("design SVG has no viewBox")
    inner = svg[open_tag.end():svg.rindex("</svg>")]
    return viewbox.group(1), inner.strip()


def fit(viewbox: str) -> tuple[int, int, int, int]:
    """Largest box inside the safe area that keeps the design's aspect."""
    _, _, vw, vh = (float(n) for n in viewbox.split())
    scale = min(SAFE_W / vw, SAFE_H / vh)
    cw, ch = round(vw * scale), round(vh * scale)
    return SAFE_X + (SAFE_W - cw) // 2, SAFE_Y + (SAFE_H - ch) // 2, cw, ch


def build_card(design_id: str) -> str:
    viewbox, inner = unwrap(design_svg(design_id).read_text())
    x, y, cw, ch = fit(viewbox)
    return CARD.format(w=W, h=H, bg=BACKGROUND, x=x, y=y, cw=cw, ch=ch,
                       viewbox=viewbox, inner=inner, cx=W // 2, hy=HANDLE_Y,
                       handle=HANDLE)


def rasterise(browser: str, svg_path: Path, png_path: Path) -> None:
    subprocess.run(
        [browser, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         f"--window-size={W},{H}", "--force-device-scale-factor=1",
         f"--screenshot={png_path}", svg_path.as_uri()],
        check=True, capture_output=True,
    )


def captions(rows: list[dict[str, str]], slogans: dict[str, str]) -> str:
    out = ["WEEK ONE — captions to paste", "=" * 34, ""]
    for row in rows:
        slogan = slogans.get(row["id"], "no design — see the format note")
        out += [f"DAY {row['day']} — {slogan}", f"  format: {row['format']}"]
        if row["hook"]:
            out.append(f"  first frame on screen: {row['hook']}")
        out += ["", f"{row['caption']}", "", "-" * 34, ""]
    out += [
        "Posting is manual on purpose. Both platforms forbid automated posting",
        "outside their own APIs, and a new account is the easiest to suspend.",
        "",
        "To space the week out, use the platforms' own schedulers:",
        "  TikTok  — upload on desktop, toggle 'Schedule video' (up to 10 days)",
        "  Instagram — Meta Business Suite > Planner, works for Reels and feed",
        "",
        "Leave the first hour after each post free. Replying is the growth",
        "mechanism, and day 6's post is made out of a comment you have to read.",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--svg-only", action="store_true", help="skip rasterising")
    p.add_argument("--out", type=Path, default=OUT_DIR)
    args = p.parse_args()

    with SCHEDULE.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    slogans = {d.id: d.slogan for d in load()}
    args.out.mkdir(parents=True, exist_ok=True)

    browser = None if args.svg_only else find_browser()
    made = 0
    for row in rows:
        if not row["id"]:
            continue
        stem = f"day-{row['day']}-{row['id'].lower()}"
        svg_path = args.out / f"{stem}.svg"
        svg_path.write_text(build_card(row["id"]))
        if browser:
            rasterise(browser, svg_path, args.out / f"{stem}.png")
        made += 1

    captions_path = args.out / "captions.txt"
    captions_path.write_text(captions(rows, slogans))

    print(f"{made} cards -> {args.out}")
    print(f"captions -> {captions_path}")
    if not browser and not args.svg_only:
        print("\nNo Chromium found, so the cards are SVG only.")
        print("Install Chrome or Chromium and re-run to get PNGs.")


if __name__ == "__main__":
    main()

"""Turn a generated raster image into a print-ready SVG motif.

This is the last mile between an image generator and `src/art.py`: strip the
background, harden the alpha, and trace to vector.

    python3 src/prep_art.py shot.webp --motif posterboard
    python3 src/prep_art.py shot.png --motif seal --out art/ --keep-png

Then render with it:

    python3 src/art.py --art-dir art/ --tiers A

Why each step exists (see docs/04-artwork-spec.md):

- **Background removal** floods in from the edges rather than keying every
  white pixel, so white *inside* the artwork survives.
- **Alpha hardening** is the one that matters for DTF. A feathered edge is a
  column of semi-transparent pixels, and the printer turns those into a
  speckled white underbase. Alpha comes out of here fully on or fully off.
- **Tracing** makes it vector, so it scales to any print size. A generated
  image is usually around 1024px; a 12in print at 300 DPI needs 3600px.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

# 12in at 300 DPI. Raster below this cannot print full width without tracing.
PRINT_PX = 3600
ALPHA_CUTOFF = 128


def strip_background(img: Image.Image, tolerance: int) -> Image.Image:
    """Flood the background in from the edges and make it transparent."""
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()

    def is_bg(x: int, y: int) -> bool:
        r, g, b, a = px[x, y]
        return a > 0 and r >= 255 - tolerance and g >= 255 - tolerance and b >= 255 - tolerance

    # Breadth-first from every edge pixel; interior white is never reached
    # because the artwork's outline blocks it.
    stack = [(x, y) for x in range(w) for y in (0, h - 1)]
    stack += [(x, y) for y in range(h) for x in (0, w - 1)]
    seen = set()
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h):
            continue
        seen.add((x, y))
        if not is_bg(x, y):
            continue
        px[x, y] = (255, 255, 255, 0)
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return img


def count_enclosed_white(img: Image.Image, tolerance: int) -> int:
    """Opaque near-white pixels the edge flood could not reach.

    These are background regions walled off by the artwork's own outline - the
    gap between a pair of legs, the sky inside a window. They are invisible on
    a white mockup and print as white blobs on a dark shirt.
    """
    px = img.convert("RGBA").load()
    w, h = img.size
    n = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 0 and min(r, g, b) >= 255 - tolerance:
                n += 1
    return n


def key_white(img: Image.Image, tolerance: int) -> int:
    """Make every near-white pixel transparent, enclosed or not."""
    img_rgba = img.convert("RGBA")
    px = img_rgba.load()
    w, h = img_rgba.size
    n = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 0 and min(r, g, b) >= 255 - tolerance:
                px[x, y] = (255, 255, 255, 0)
                n += 1
    img.paste(img_rgba)
    return n


def harden_alpha(img: Image.Image, cutoff: int = ALPHA_CUTOFF) -> tuple[Image.Image, int]:
    """Force every pixel fully opaque or fully clear. Returns (image, n_fixed)."""
    img = img.convert("RGBA")
    alpha = img.getchannel("A")
    softened = sum(c for v, c in zip(range(256), alpha.histogram()) if 0 < v < 255)
    img.putalpha(alpha.point(lambda v: 255 if v >= cutoff else 0))
    return img, softened


def trim(img: Image.Image, margin_frac: float = 0.03) -> Image.Image:
    box = img.getbbox()
    if not box:
        return img
    img = img.crop(box)
    m = int(max(img.size) * margin_frac)
    out = Image.new("RGBA", (img.width + 2 * m, img.height + 2 * m), (255, 255, 255, 0))
    out.paste(img, (m, m))
    return out


def trace(png_path: Path, svg_path: Path) -> None:
    import vtracer
    vtracer.convert_image_to_svg_py(
        str(png_path), str(svg_path),
        colormode="color",
        hierarchical="stacked",
        mode="spline",
        filter_speckle=6,      # drop generator noise
        color_precision=6,
        layer_difference=16,
        corner_threshold=60,
        length_threshold=4.0,
        splice_threshold=45,
        path_precision=6,
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Prepare generated art for printing.")
    p.add_argument("image", type=Path)
    p.add_argument("--motif", required=True, help="catalog motif name; sets the filename")
    p.add_argument("--out", type=Path, default=Path("art"))
    p.add_argument("--tolerance", type=int, default=12,
                   help="how far from pure white still counts as background")
    p.add_argument("--keep-png", action="store_true", help="also keep the cleaned raster")
    p.add_argument("--key-white", action="store_true",
                   help="also clear near-white the edge flood could not reach; "
                        "use when the art has no intentional white")
    args = p.parse_args()

    if not args.image.exists():
        sys.exit(f"no such file: {args.image}")

    img = Image.open(args.image)
    print(f"in:  {args.image.name}  {img.width}x{img.height}")

    img = strip_background(img, args.tolerance)

    enclosed = count_enclosed_white(img, args.tolerance)
    if args.key_white:
        cleared = key_white(img, args.tolerance)
        print(f"keyed {cleared} near-white pixels, enclosed ones included")
    elif enclosed:
        pct = 100 * enclosed / (img.width * img.height)
        print(f"note: {enclosed} opaque near-white pixels ({pct:.1f}%) the edge")
        print("      flood could not reach - background walled off by the artwork.")
        print("      Invisible on a white mockup, white blobs on a dark shirt.")
        print("      Re-run with --key-white if none of that white is intentional.")

    img, softened = harden_alpha(img)
    img = trim(img)
    print(f"trimmed to {img.width}x{img.height}")
    if softened:
        print(f"hardened {softened} semi-transparent pixels "
              f"(these are what speckle a DTF underbase)")

    args.out.mkdir(parents=True, exist_ok=True)
    png_path = args.out / f"{args.motif}.png"
    svg_path = args.out / f"{args.motif}.svg"
    img.save(png_path)

    try:
        trace(png_path, svg_path)
    except Exception as exc:  # vtracer missing or failed
        print(f"  ! tracing failed: {exc}")
        print(f"  kept the cleaned raster at {png_path}; trace it manually")
        return

    if not args.keep_png:
        png_path.unlink(missing_ok=True)

    kb = svg_path.stat().st_size / 1024
    print(f"out: {svg_path}  ({kb:.0f} KB vector)")
    if max(img.size) < PRINT_PX:
        print(f"note: source was {max(img.size)}px, under the {PRINT_PX}px a 12in")
        print("      300 DPI print needs. Tracing to vector makes that moot, but")
        print("      fine detail the generator never rendered cannot be recovered.")
    print(f"\nrender it:  python3 src/art.py --art-dir {args.out} --tiers A")


if __name__ == "__main__":
    main()

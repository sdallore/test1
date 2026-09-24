"""Turn each week-one card into a short vertical video.

A still image is the weakest thing you can put on TikTok: it earns about a
second of watch time and the feed ranks on watch time. The same design as a
seven-second clip -- hook held long enough to read, then a cut to the shirt
with a slow push -- gets watched and looped instead.

    python3 src/video_export.py           # all design days
    python3 src/video_export.py --day 1   # just one

Needs ffmpeg with libx264 on PATH. Output lands in build/posts/.
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import social_export  # noqa: E402
import typeset  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "build" / "posts"

W, H = social_export.W, social_export.H
FPS = 30

# Long enough to read the hook without losing anyone, then the reveal. The
# whole thing has to finish before a thumb moves, so it stays under 8 seconds.
HOOK_SECONDS = 2.4
CARD_SECONDS = 4.6
ZOOM_TO = 1.10

HOOK_SIZE = 76
HOOK_LINE_HEIGHT = 1.35
HOOK_WIDTH = 860

HOOK_CARD = """<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="{w}" height="{h}" fill="{bg}"/>
  <g fill="#141414">
{lines}
  </g>
</svg>
"""


def wrap(text: str, size: float, width: float) -> list[str]:
    """Greedy wrap against real glyph widths, not a character count."""
    lines: list[str] = []
    line: list[str] = []
    for word in text.split():
        trial = line + [word]
        if line and typeset.measure(" ".join(trial), "voice", size) > width:
            lines.append(" ".join(line))
            line = [word]
        else:
            line = trial
    if line:
        lines.append(" ".join(line))
    return lines


def hook_card(text: str) -> str:
    """The opening frame: the hook, outlined, centred in the safe area."""
    size = HOOK_SIZE
    lines = wrap(text, size, HOOK_WIDTH)
    # Four lines is the most that stays comfortable; shrink rather than overflow.
    while len(lines) > 4 and size > 40:
        size -= 4
        lines = wrap(text, size, HOOK_WIDTH)

    step = size * HOOK_LINE_HEIGHT
    block = step * len(lines)
    first = (H - block) / 2 + size * typeset.cap_ratio("voice")

    glyphs = "\n".join(
        typeset.outline(line, "voice", size, W / 2, first + i * step)
        for i, line in enumerate(lines)
    )
    return HOOK_CARD.format(w=W, h=H, bg=social_export.BACKGROUND, lines=glyphs)


def ffmpeg() -> str:
    found = shutil.which("ffmpeg")
    if not found:
        raise SystemExit(
            "ffmpeg is not on PATH. Install it (brew install ffmpeg, "
            "apt install ffmpeg) and re-run."
        )
    return found


def encode(binary: str, hook_png: Path, card_png: Path, out: Path) -> None:
    hook_frames = round(HOOK_SECONDS * FPS)
    card_frames = round(CARD_SECONDS * FPS)
    # zoompan steps per output frame, so the rate is the total zoom spread
    # across the clip -- slow enough to read as a push, not a lurch.
    step = (ZOOM_TO - 1.0) / card_frames

    # Input 0 is the silent audio bed; 1 is the hook frame, 2 is the card.
    filters = (
        f"[1:v]scale={W}:{H},loop={hook_frames}:1:0,"
        f"trim=end_frame={hook_frames},setpts=N/{FPS}/TB[hook];"
        f"[2:v]scale={W}:{H},loop={card_frames}:1:0,"
        f"trim=end_frame={card_frames},"
        f"zoompan=z='min(zoom+{step:.6f},{ZOOM_TO})':d=1:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
        f"setpts=N/{FPS}/TB[card];"
        f"[hook][card]concat=n=2:v=1:a=0[v]"
    )

    subprocess.run(
        [binary, "-y", "-loglevel", "error",
         "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
         "-framerate", str(FPS), "-i", str(hook_png),
         "-framerate", str(FPS), "-i", str(card_png),
         "-filter_complex", filters,
         "-map", "[v]", "-map", "0:a",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "128k", "-shortest",
         "-movflags", "+faststart",
         str(out)],
        check=True, capture_output=True,
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--day", type=int, help="render one day only")
    p.add_argument("--out", type=Path, default=OUT_DIR)
    args = p.parse_args()

    with social_export.SCHEDULE.open(newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r["id"]]
    if args.day:
        rows = [r for r in rows if int(r["day"]) == args.day]
        if not rows:
            raise SystemExit(f"Day {args.day} has no design to render.")

    binary = ffmpeg()
    browser = social_export.find_browser()
    if not browser:
        raise SystemExit("No Chromium found; cannot rasterise frames.")

    args.out.mkdir(parents=True, exist_ok=True)
    for row in rows:
        stem = f"day-{row['day']}-{row['id'].lower()}"
        hook_svg = args.out / f"{stem}-hook.svg"
        hook_png = args.out / f"{stem}-hook.png"
        card_png = args.out / f"{stem}.png"

        hook_svg.write_text(hook_card(row["hook"]))
        social_export.rasterise(browser, hook_svg, hook_png)
        if not card_png.exists():
            card_svg = args.out / f"{stem}.svg"
            card_svg.write_text(social_export.build_card(row["id"]))
            social_export.rasterise(browser, card_svg, card_png)

        out = args.out / f"{stem}.mp4"
        encode(binary, hook_png, card_png, out)
        print(f"day {row['day']}  {out.name}  "
              f"{HOOK_SECONDS + CARD_SECONDS:.1f}s  {out.stat().st_size // 1024} KB")

    print("\nSilent on purpose -- add a sound in the app. TikTok's own audio")
    print("library is a discovery surface, and a muted post gives that up.")


if __name__ == "__main__":
    main()

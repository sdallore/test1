"""Typographic lockups, set as real outlines.

Two jobs.

**Outlines.** Glyphs come out as SVG `<path>` geometry rather than `<text>`,
using the fonts vendored in `assets/fonts`. That removes the manual "convert
text to outlines in a vector editor" step the artwork spec used to end with,
and it means the file renders identically on a machine that has never heard of
the typeface.

**Lockups.** A slogan is not one centred paragraph. Merch typography breaks a
phrase into a stack: the words that carry the idea set large in a display face,
the connectives ("is a", "the", "for a") dropped small into a script. Each
content line is then scaled to fill the print width, so the block reads as one
deliberate object instead of ragged centred text.

    Democracy Is A Group Project     ->    DEMOCRACY
                                              is a
                                        GROUP PROJECT
"""

from __future__ import annotations

import functools
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"

# Words that carry grammar rather than meaning. They drop to the script line.
CONNECTORS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "of", "my", "your",
    "our", "their", "to", "and", "for", "in", "on", "at", "it", "with",
    "that", "just", "but", "or", "as",
}

MAX_LINES = 5
MAX_SCRIPT_LINES = 1

# Display type wants roughly this many characters per line to fill the print
# width at a size worth printing. A long phrase left on one line scales down to
# fit and ends up small; breaking it lets every line run big.
TARGET_CHARS = 11


@functools.lru_cache(maxsize=8)
def load(role: str) -> TTFont:
    """role is one of the filenames in assets/fonts: display, script, voice."""
    return TTFont(FONT_DIR / f"{role}.ttf")


def _metrics(font: TTFont) -> tuple[int, float]:
    upem = font["head"].unitsPerEm
    os2 = font.get("OS/2")
    cap = getattr(os2, "sCapHeight", None) if os2 else None
    if not cap:
        cap = int(upem * 0.7)
    return upem, cap / upem


def measure(text: str, role: str, size: float) -> float:
    """Advance width of `text` at `size`, in the same units as size."""
    font = load(role)
    upem = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    total = 0
    for ch in text:
        name = cmap.get(ord(ch))
        total += hmtx[name][0] if name else upem * 0.30
    return total * size / upem


def cap_ratio(role: str) -> float:
    return _metrics(load(role))[1]


def outline(text: str, role: str, size: float, cx: float, baseline: float) -> str:
    """SVG for `text` as filled paths, horizontally centred on cx."""
    font = load(role)
    upem = font["head"].unitsPerEm
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    scale = size / upem

    parts: list[str] = []
    cursor = 0
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            cursor += upem * 0.30
            continue
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        d = pen.getCommands()
        if d:
            parts.append(f'<path d="{d}" transform="translate({cursor} 0)"/>')
        cursor += hmtx[name][0]

    x = cx - (cursor * scale) / 2
    # Font space is y-up, SVG is y-down, hence the negative y scale.
    return (f'<g transform="translate({x:.1f} {baseline:.1f}) '
            f'scale({scale:.6f} {-scale:.6f})">' + "".join(parts) + "</g>")


def split_runs(slogan: str) -> list[tuple[str, bool]]:
    """Break a slogan into (text, is_connector) runs."""
    runs: list[tuple[list[str], bool]] = []
    for word in slogan.split():
        conn = word.lower().strip(".,!?'\"") in CONNECTORS
        if runs and runs[-1][1] == conn:
            runs[-1][0].append(word)
        else:
            runs.append(([word], conn))

    # A connector run only earns its own line between two content runs. Leading
    # or trailing connectives ("...Light On") belong with their neighbour.
    merged: list[tuple[list[str], bool]] = []
    for i, (words, conn) in enumerate(runs):
        edge = i == 0 or i == len(runs) - 1
        if conn and edge and merged:
            merged[-1][0].extend(words)
        elif conn and edge and i == 0 and i + 1 < len(runs):
            runs[i + 1][0][:0] = words
        else:
            merged.append((list(words), conn))

    while len(merged) > MAX_LINES:
        for i, (_, conn) in enumerate(merged):
            if conn and i + 1 < len(merged):
                merged[i + 1][0][:0] = merged[i][0]
                merged.pop(i)
                break
        else:
            merged[-2][0].extend(merged[-1][0])
            merged.pop()

    # Too many script lines chops the lockup into confetti.
    script_idx = [i for i, (_, c) in enumerate(merged) if c]
    while len(script_idx) > MAX_SCRIPT_LINES:
        i = script_idx[-1]
        if i + 1 < len(merged):
            merged[i + 1][0][:0] = merged[i][0]
        else:
            merged[i - 1][0].extend(merged[i][0])
        merged.pop(i)
        script_idx = [j for j, (_, c) in enumerate(merged) if c]

    # Break long content runs across lines so each one can be set large.
    out: list[tuple[str, bool]] = []
    for words, conn in merged:
        if conn or len(words) < 2:
            out.append((" ".join(words), conn))
            continue
        for line in balance(words, TARGET_CHARS):
            out.append((line, False))
    return [(t, c) for t, c in out if t]


def balance(words: list[str], target_chars: int) -> list[str]:
    """Split words across as few lines as possible, keeping them even."""
    total = sum(len(w) for w in words) + len(words) - 1
    k = max(1, min(len(words), round(total / target_chars) or 1))
    if k == 1:
        return [" ".join(words)]

    # Greedy fill against an even share, which reads better than a ragged wrap.
    share = total / k
    lines, cur, cur_len = [], [], 0
    for i, w in enumerate(words):
        add = len(w) + (1 if cur else 0)
        remaining_lines = k - len(lines)
        words_left = len(words) - i
        must_break = cur and words_left < remaining_lines
        if cur and (cur_len + add > share * 1.35 or must_break):
            lines.append(" ".join(cur))
            cur, cur_len = [w], len(w)
        else:
            cur.append(w)
            cur_len += add
    if cur:
        lines.append(" ".join(cur))
    return lines[:k] if len(lines) > k else lines


def lay_out(slogan: str, width: float, top: float, bottom: float,
            max_size: float = 190.0) -> list[dict]:
    """Place a lockup. Returns line dicts with text, role, size and baseline."""
    runs = split_runs(slogan)
    lines: list[dict] = []

    for text, conn in runs:
        role = "script" if conn else "display"
        target = width * (0.34 if conn else 1.0)
        unit = measure(text, role, 100.0) / 100.0
        size = min(target / unit if unit else max_size, max_size)
        lines.append({"text": text, "role": role, "size": size,
                      "connector": conn})

    def block_height() -> float:
        h = 0.0
        for i, ln in enumerate(lines):
            h += ln["size"] * cap_ratio(ln["role"])
            if i:
                h += lines[i - 1]["size"] * (0.30 if ln["connector"] else 0.22)
        return h

    # Shrink to fit the available band rather than overflowing it.
    avail = bottom - top
    guard = 0
    while block_height() > avail and guard < 40:
        for ln in lines:
            ln["size"] *= 0.94
        guard += 1

    y = top + (avail - block_height()) / 2
    for i, ln in enumerate(lines):
        if i:
            y += lines[i - 1]["size"] * (0.30 if ln["connector"] else 0.22)
        y += ln["size"] * cap_ratio(ln["role"])
        ln["baseline"] = y
    return lines


def render(slogan: str, width: float, cx: float, top: float, bottom: float,
           ink: str) -> list[str]:
    out = [f'<g fill="{ink}" stroke="none">']
    for ln in lay_out(slogan, width, top, bottom):
        out.append(outline(ln["text"], ln["role"], ln["size"], cx, ln["baseline"]))
    out.append("</g>")
    return out

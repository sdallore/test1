"""Load and validate the design catalog.

    python3 src/catalog.py
    python3 src/catalog.py --tier A
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parent.parent / "catalog" / "designs.csv"

VALID_TIERS = {"A", "B", "C"}
VALID_RISK = {"low", "medium", "high"}
VALID_FORMATS = {"punchline", "definition", "tour-back", "graphic"}

# The brand voice.
#   barbed  - cutting, but the cut is an idea. Carries the brand.
#   wry     - argues with a light touch.
#   earnest - says it plainly, no joke.
#   warm    - offers something.
#   sharp   - a dunk with no idea in it. Recorded, never launched.
VALID_TONES = {"warm", "wry", "earnest", "barbed", "sharp"}

# What you need to know to get the joke. "general" designs carry reach;
# everything else rewards the in-group but travels less far.
VALID_LITERACY = {
    "general", "econ", "history", "classics", "scripture", "theory",
    "stats", "rhetoric",
}

# A launch set made entirely of deep cuts cannot be shared by the people who
# would buy it. Without paid advertising, reach is the whole growth model.
MIN_GENERAL_IN_TIER_A = 3


@dataclass(frozen=True)
class Design:
    id: str
    slogan: str
    theme: str
    tone: str
    literacy: str
    format: str
    tier: str
    risk: str
    risk_note: str
    saturation: str

    @property
    def printable(self) -> bool:
        """High legal risk means it does not go to the printer without counsel."""
        return self.risk != "high"


def load(path: Path = CATALOG_PATH) -> list[Design]:
    with path.open(newline="", encoding="utf-8") as fh:
        return [Design(**row) for row in csv.DictReader(fh)]


def validate(designs: list[Design]) -> list[str]:
    """Return a list of problems. Empty list means the catalog is clean."""
    problems: list[str] = []
    seen_ids: set[str] = set()
    seen_slogans: set[str] = set()

    for d in designs:
        if d.id in seen_ids:
            problems.append(f"{d.id}: duplicate id")
        seen_ids.add(d.id)

        key = d.slogan.lower().strip()
        if key in seen_slogans:
            problems.append(f"{d.id}: duplicate slogan {d.slogan!r}")
        seen_slogans.add(key)

        if d.tier not in VALID_TIERS:
            problems.append(f"{d.id}: tier {d.tier!r} not in {sorted(VALID_TIERS)}")
        if d.risk not in VALID_RISK:
            problems.append(f"{d.id}: risk {d.risk!r} not in {sorted(VALID_RISK)}")
        if d.format not in VALID_FORMATS:
            problems.append(f"{d.id}: format {d.format!r} not in {sorted(VALID_FORMATS)}")
        if d.tone not in VALID_TONES:
            problems.append(f"{d.id}: tone {d.tone!r} not in {sorted(VALID_TONES)}")
        if d.literacy not in VALID_LITERACY:
            problems.append(f"{d.id}: literacy {d.literacy!r} not in {sorted(VALID_LITERACY)}")
        if d.tier == "A" and d.tone == "sharp":
            problems.append(f"{d.id}: a dunk with no idea in it cannot lead a launch")
        if not d.risk_note.strip():
            problems.append(f"{d.id}: every design needs a risk note")
        if d.tier == "A" and d.risk == "high":
            problems.append(f"{d.id}: tier A cannot carry high legal risk")
        if len(d.slogan) > 60:
            problems.append(f"{d.id}: slogan is {len(d.slogan)} chars; long text prints badly")

    tier_a_general = sum(1 for d in designs if d.tier == "A" and d.literacy == "general")
    tier_a = sum(1 for d in designs if d.tier == "A")
    if tier_a and tier_a_general < MIN_GENERAL_IN_TIER_A:
        problems.append(
            f"tier A has {tier_a_general} general-literacy design(s); "
            f"needs {MIN_GENERAL_IN_TIER_A} so the launch set can travel"
        )

    return problems


def main() -> None:
    p = argparse.ArgumentParser(description="Inspect the design catalog.")
    p.add_argument("--tier", choices=sorted(VALID_TIERS), help="filter to one tier")
    args = p.parse_args()

    designs = load()
    problems = validate(designs)

    print(f"{len(designs)} designs loaded from {CATALOG_PATH.name}")
    if problems:
        print(f"\n{len(problems)} PROBLEM(S):")
        for problem in problems:
            print(f"  ! {problem}")
    else:
        print("catalog validates clean")

    print("\nBy tier:      ", dict(sorted(Counter(d.tier for d in designs).items())))
    print("By tone:      ", dict(sorted(Counter(d.tone for d in designs).items())))
    print("By literacy:  ", dict(sorted(Counter(d.literacy for d in designs).items())))
    print("By risk:      ", dict(sorted(Counter(d.risk for d in designs).items())))
    print("By theme:     ", dict(sorted(Counter(d.theme for d in designs).items())))
    print(f"Printable now: {sum(d.printable for d in designs)}/{len(designs)}")

    shown = [d for d in designs if not args.tier or d.tier == args.tier]
    reach = [d for d in designs if d.tier == "A" and d.literacy == "general"]
    print(f"Tier A reach:  {len(reach)} of {sum(1 for d in designs if d.tier == 'A')} "
          f"land without prior reading")

    print(f"\n{'ID':<6}{'TIER':<6}{'TONE':<9}{'LITERACY':<11}SLOGAN")
    print("-" * 82)
    for d in shown:
        print(f"{d.id:<6}{d.tier:<6}{d.tone:<9}{d.literacy:<11}{d.slogan}")


if __name__ == "__main__":
    main()

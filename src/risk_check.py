"""Scan slogans for the legal landmines that actually sink merch brands.

This is a triage tool, not legal advice. It catches the obvious cases so a
human looks at the right 5% of the catalog. It cannot tell you whether a
specific use is fair.

    python3 src/risk_check.py                     # scan the whole catalog
    python3 src/risk_check.py "Some new slogan"   # scan one idea
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog import load  # noqa: E402

# --- Rule tables -----------------------------------------------------------
# Patterns are matched case-insensitively on word boundaries.

# Naming a living politician on a product is right-of-publicity exposure in
# most states, and parody protects commentary far better than it protects
# merchandise. This list is deliberately generic; add names as they come up.
PUBLICITY_TERMS = [
    "trump", "biden", "harris", "obama", "clinton", "sanders", "aoc",
    "ocasio", "pelosi", "mcconnell", "desantis", "newsom", "vance",
    "musk", "bezos", "zuckerberg",
    # The high-brow register tempts you to name a theorist. Long-dead writers
    # are public domain; living ones are a right-of-publicity problem, and a
    # recently dead one may still have an estate that enforces.
    "piketty", "chomsky", "zizek", "judith butler", "naomi klein",
    "david graeber", "mark fisher", "ta-nehisi coates",
]

# Slogans and names with live trademark registrations or strong common-law
# rights. Using these on apparel is the fastest route to a takedown.
TRADEMARK_TERMS = [
    "make america great again", "maga", "build back better",
    "let's go brandon", "i'm with her", "feel the bern", "yes we can",
    "democratic party", "republican party", "gop", "dnc", "rnc",
    "democracy dies in", "all the news that's fit to print",
    "just do it", "think different", "super bowl", "olympic",
]

# Brands, bands and franchises that get referenced in puns. A pun on a name
# is not automatically infringement, but on a t-shirt it is close enough to
# the mark's own market that it needs a human decision.
BRAND_TERMS = [
    "rage against the machine", "wage against the machine", "nike", "adidas",
    "disney", "marvel", "star wars", "pokemon", "coca cola", "pepsi",
    "dewey decimal", "barbie", "taylor swift", "beyonce",
    # A live trademark with a documented history of enforcing it against
    # exactly this kind of historical reference.
    "pinkerton", "pinkertons",
]

# Phrases owned or heavily policed by advocacy organizations. Often fine to
# use in speech, risky to sell.
ORG_TERMS = [
    "bans off our bodies", "black lives matter", "me too", "planned parenthood",
    "aclu", "sierra club", "greenpeace", "notorious rbg",
]


# The trap specific to a warm, nostalgic voice. Beloved children's media is
# owned by estates and studios that police it aggressively, and the warmer the
# brand voice gets, the more tempting these references become. A gentle homage
# is still a commercial use of someone else's property.
NOSTALGIA_TERMS = [
    "mister rogers", "mr rogers", "fred rogers", "won't you be my neighbor",
    "wont you be my neighbor", "neighborhood of make believe", "daniel tiger",
    "sesame street", "big bird", "elmo", "oscar the grouch", "cookie monster",
    "bob ross", "happy little", "dr seuss", "the lorax", "cat in the hat",
    "muppets", "kermit", "charlie brown", "peanuts", "snoopy", "linus",
    "winnie the pooh", "paddington", "reading rainbow", "schoolhouse rock",
    "bluey", "the little engine that could",
]


@dataclass(frozen=True)
class Flag:
    category: str
    term: str
    severity: str
    guidance: str


RULES: list[tuple[str, list[str], str, str]] = [
    ("right-of-publicity", PUBLICITY_TERMS, "high",
     "Names a real person. Do not print without counsel; several states give "
     "a cause of action for commercial use of a name or likeness."),
    ("trademark", TRADEMARK_TERMS, "high",
     "Registered or heavily policed mark. Expect a takedown on a marketplace "
     "listing and a demand letter on your own store."),
    ("brand-reference", BRAND_TERMS, "medium",
     "Plays on a commercial brand. Parody is a defense, not a shield, and it "
     "is weakest when the joke is the product."),
    ("org-phrase", ORG_TERMS, "medium",
     "Associated with an advocacy organization. Selling it can imply an "
     "endorsement you do not have."),
    ("nostalgia-ip", NOSTALGIA_TERMS, "high",
     "Children's media property. These estates and studios enforce hard, and "
     "warmth is not a defense: an affectionate homage is still commercial use. "
     "Take the feeling, never the character, the catchphrase, or the costume."),
]

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def scan(text: str) -> list[Flag]:
    """Return every rule this text trips, worst first."""
    flags: list[Flag] = []
    for category, terms, severity, guidance in RULES:
        for term in terms:
            if re.search(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE):
                flags.append(Flag(category, term, severity, guidance))
    return sorted(flags, key=lambda f: SEVERITY_ORDER[f.severity])


def _print_flags(label: str, flags: list[Flag]) -> None:
    if not flags:
        print(f"  CLEAR   {label}")
        return
    worst = flags[0].severity.upper()
    print(f"  {worst:<7} {label}")
    for f in flags:
        print(f"          -> {f.category}: matched {f.term!r}")
        print(f"             {f.guidance}")


def main() -> None:
    print("LEGAL TRIAGE - keyword scan, not legal advice")
    print("=" * 72)

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        _print_flags(text, scan(text))
        return

    designs = load()
    flagged = 0
    for d in designs:
        flags = scan(d.slogan)
        if flags:
            flagged += 1
            _print_flags(f"{d.id}  {d.slogan}", flags)

    print("=" * 72)
    print(f"{flagged} of {len(designs)} designs tripped a rule.")
    print("\nDesigns the catalog already marks high-risk:")
    for d in designs:
        if d.risk == "high":
            print(f"  {d.id}  {d.slogan}")
            print(f"        {d.risk_note}")
    print("\nThe scanner only knows the terms in its tables. A clean result")
    print("means nothing was matched, not that a design is safe.")
    print("\nIt also cannot see artwork. A red cardigan, a yellow raincoat, or a")
    print("particular shade of blue fur can evoke a protected property with no")
    print("infringing word anywhere on the shirt. Visual homage needs human eyes.")


if __name__ == "__main__":
    main()

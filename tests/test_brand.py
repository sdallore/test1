"""Stdlib-only tests. Run from the repo root:

    python3 -m unittest discover -s tests -v
"""

import csv
import sys
import xml.etree.ElementTree as ET
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import catalog  # noqa: E402
import risk_check  # noqa: E402
import art  # noqa: E402
import shopify_export  # noqa: E402
from economics import Economics  # noqa: E402


class TestCatalog(unittest.TestCase):
    def setUp(self):
        self.designs = catalog.load()

    def test_catalog_is_not_empty(self):
        self.assertGreater(len(self.designs), 20)

    def test_catalog_validates_clean(self):
        self.assertEqual(catalog.validate(self.designs), [])

    def test_ids_are_unique(self):
        ids = [d.id for d in self.designs]
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_tier_a_design_is_high_risk(self):
        for d in self.designs:
            if d.tier == "A":
                self.assertNotEqual(d.risk, "high", f"{d.id} is tier A and high risk")

    def test_high_risk_designs_are_not_printable(self):
        for d in self.designs:
            self.assertEqual(d.printable, d.risk != "high")

    def test_validate_catches_a_bad_row(self):
        bad = catalog.Design(
            id="X1", slogan="x", theme="t", tone="sharp", motif="none",
            format="punchline",
            tier="A", risk="high", risk_note="", saturation="low",
        )
        problems = catalog.validate([bad])
        self.assertTrue(any("tier A cannot carry high legal risk" in p for p in problems))
        self.assertTrue(any("needs a risk note" in p for p in problems))

    def test_tier_a_rejects_a_sharp_tone(self):
        sharp = catalog.Design(
            id="X2", slogan="x", theme="t", tone="sharp", motif="none",
            format="punchline",
            tier="A", risk="low", risk_note="fine", saturation="low",
        )
        problems = catalog.validate([sharp])
        self.assertTrue(any("cannot lead a launch" in p for p in problems))

    def test_every_design_has_a_known_motif(self):
        for d in self.designs:
            self.assertIn(d.motif, catalog.VALID_MOTIFS, f"{d.id}: {d.motif!r}")

    def test_tier_a_designs_all_ship_with_art(self):
        for d in self.designs:
            if d.tier == "A":
                self.assertNotEqual(d.motif, "none", f"{d.id} is tier A with no art")

    def test_validate_catches_a_type_only_tier_a_design(self):
        bare = catalog.Design(
            id="X4", slogan="x", theme="t", tone="warm", motif="none",
            format="punchline", tier="A", risk="low", risk_note="fine",
            saturation="low",
        )
        self.assertTrue(any("ship with art" in p for p in catalog.validate([bare])))

    def test_every_design_has_a_valid_tone(self):
        for d in self.designs:
            self.assertIn(d.tone, catalog.VALID_TONES, f"{d.id} has tone {d.tone!r}")

    def test_launch_set_carries_no_digs(self):
        for d in self.designs:
            if d.tier == "A":
                self.assertNotEqual(d.tone, "sharp", f"{d.id} is a dig in the launch set")


class TestRiskCheck(unittest.TestCase):
    def test_flags_a_politician_name(self):
        flags = risk_check.scan("Vote Pelosi Forever")
        self.assertTrue(any(f.category == "right-of-publicity" for f in flags))

    def test_flags_a_registered_slogan(self):
        flags = risk_check.scan("Make America Great Again But Correctly")
        self.assertTrue(any(f.category == "trademark" for f in flags))

    def test_flags_a_riff_on_a_newspaper_tagline(self):
        flags = risk_check.scan("Democracy Dies In Dark Mode")
        self.assertTrue(any(f.category == "trademark" for f in flags))

    def test_clean_slogan_is_clear(self):
        self.assertEqual(risk_check.scan("Shovel The Whole Block"), [])

    def test_flags_a_childrens_media_catchphrase(self):
        flags = risk_check.scan("Won't You Be My Neighbor")
        self.assertTrue(any(f.category == "nostalgia-ip" for f in flags))
        self.assertEqual(flags[0].severity, "high")

    def test_flags_a_childrens_media_character(self):
        self.assertTrue(
            any(f.category == "nostalgia-ip" for f in risk_check.scan("Ask Big Bird"))
        )

    def test_generic_neighbor_language_is_clear(self):
        # The line the brand walks: the sentiment is free, the catchphrase is not.
        self.assertEqual(risk_check.scan("We're All Neighbors"), [])
        self.assertEqual(risk_check.scan("Leave The Porch Light On"), [])

    def test_worst_severity_sorts_first(self):
        flags = risk_check.scan("Nike Presents Trump")
        self.assertEqual(flags[0].severity, "high")

    def test_matching_is_word_bounded(self):
        # "gop" must not match inside "gospel".
        self.assertEqual(risk_check.scan("Gospel Brunch"), [])

    def test_every_tier_a_design_passes_the_scanner(self):
        for d in catalog.load():
            if d.tier == "A":
                self.assertEqual(risk_check.scan(d.slogan), [], f"{d.id} tripped a rule")


class TestEconomics(unittest.TestCase):
    def test_defaults_are_profitable(self):
        self.assertGreater(Economics().gross_profit, 0)

    def test_margin_rises_with_price(self):
        self.assertLess(Economics(retail=26).margin, Economics(retail=34).margin)

    def test_cogs_is_the_sum_of_its_parts(self):
        e = Economics(blank_cost=5.0, print_cost=7.0, shipping_cost=6.0)
        self.assertAlmostEqual(e.cogs, 18.0)

    def test_underwater_price_never_breaks_even(self):
        e = Economics(retail=10.00)
        self.assertLess(e.gross_profit, 0)
        self.assertEqual(e.breakeven_units(100.0), float("inf"))

    def test_breakeven_scales_with_fixed_costs(self):
        e = Economics()
        self.assertAlmostEqual(e.breakeven_units(120.0), 2 * e.breakeven_units(60.0))

    def test_report_renders(self):
        self.assertIn("GROSS MARGIN", Economics().report())


class TestShopifyExport(unittest.TestCase):
    def test_handles_are_url_safe(self):
        self.assertEqual(
            shopify_export.handle_for("GERRYMANDER (v.) To Choose Your Own Voters"),
            "gerrymander-v-to-choose-your-own-voters",
        )

    def test_handle_strips_apostrophes(self):
        self.assertEqual(shopify_export.handle_for("I'm With The Banned"), "i-m-with-the-banned")

    def test_handle_strips_trailing_punctuation(self):
        self.assertEqual(
            shopify_export.handle_for("Feed The Kids. That's The Whole Policy."),
            "feed-the-kids-that-s-the-whole-policy",
        )

    def test_tone_is_carried_into_tags(self):
        design = next(d for d in catalog.load() if d.tier == "A")
        rows = shopify_export.rows_for(design, 32.0, publish=False)
        self.assertIn(design.tone, rows[0]["Tags"])

    def test_every_theme_has_product_copy(self):
        for d in catalog.load():
            self.assertIn(d.theme, shopify_export.BLURBS, f"{d.theme} has no blurb")

    def test_motif_is_carried_into_tags(self):
        design = next(d for d in catalog.load() if d.tier == "A")
        rows = shopify_export.rows_for(design, 32.0, publish=False)
        self.assertIn(design.motif, rows[0]["Tags"])

    def test_handle_survives_punctuation(self):
        self.assertEqual(shopify_export.handle_for("Y'all Means All"), "y-all-means-all")

    def test_size_upcharge_applies_to_2xl_only(self):
        self.assertEqual(shopify_export.price_for(32.0, "L"), 32.0)
        self.assertEqual(shopify_export.price_for(32.0, "2XL"), 34.0)

    def test_one_product_yields_one_row_per_variant(self):
        design = catalog.load()[0]
        rows = shopify_export.rows_for(design, 32.0, publish=False)
        self.assertEqual(len(rows), len(shopify_export.COLORS) * len(shopify_export.SIZES))

    def test_only_the_first_row_carries_product_fields(self):
        design = catalog.load()[0]
        rows = shopify_export.rows_for(design, 32.0, publish=False)
        self.assertTrue(rows[0]["Title"])
        self.assertTrue(all(not r["Title"] for r in rows[1:]))

    def test_all_rows_share_one_handle(self):
        design = catalog.load()[0]
        rows = shopify_export.rows_for(design, 32.0, publish=False)
        self.assertEqual(len({r["Handle"] for r in rows}), 1)

    def test_skus_are_unique_within_a_product(self):
        design = catalog.load()[0]
        rows = shopify_export.rows_for(design, 32.0, publish=False)
        skus = [r["Variant SKU"] for r in rows]
        self.assertEqual(len(skus), len(set(skus)))

    def test_products_default_to_draft(self):
        design = catalog.load()[0]
        rows = shopify_export.rows_for(design, 32.0, publish=False)
        self.assertEqual(rows[0]["Status"], "draft")

    def test_written_csv_round_trips(self):
        design = catalog.load()[0]
        rows = shopify_export.rows_for(design, 32.0, publish=False)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.csv"
            with path.open("w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=shopify_export.COLUMNS)
                w.writeheader()
                w.writerows(rows)
            with path.open(newline="", encoding="utf-8") as fh:
                back = list(csv.DictReader(fh))
        self.assertEqual(len(back), len(rows))
        self.assertEqual(back[0]["Title"], design.slogan)


if __name__ == "__main__":
    unittest.main()


class TestArt(unittest.TestCase):
    def setUp(self):
        self.designs = catalog.load()

    def test_every_catalog_motif_has_a_drawing(self):
        for d in self.designs:
            if d.motif != "none":
                self.assertIn(d.motif, art.MOTIFS, f"{d.id} names an undrawn motif")

    def test_every_drawing_is_used_or_spare(self):
        for name, builder in art.MOTIFS.items():
            self.assertTrue(builder(), f"{name} draws nothing")

    def test_every_design_renders_well_formed_svg(self):
        for d in self.designs:
            ET.fromstring(art.render(d, "#141414"))

    def test_svg_declares_print_size(self):
        svg = art.render(self.designs[0], "#141414")
        self.assertIn('width="12in"', svg)
        self.assertIn('height="14in"', svg)

    def test_printed_stroke_clears_the_dtf_minimum(self):
        # The motif group is scaled by MOTIF_SCALE and its stroke-width is
        # pre-divided by it, so the printed weight is STROKE units. One unit is
        # 0.01in = 0.72pt, and DTF breaks up below about 2pt at print size.
        printed_pt = art.STROKE * 0.72
        self.assertGreaterEqual(printed_pt, 2.0)

    def test_motif_stroke_is_compensated_for_the_scale(self):
        svg = art.render(
            next(d for d in self.designs if d.motif != "none"), "#141414"
        )
        self.assertIn(f'stroke-width="{art.STROKE / art.MOTIF_SCALE:.1f}"', svg)

    def test_text_wrapping_respects_the_width(self):
        lines, size = art.lay_out_text("Somebody Planted The Tree You're Sitting Under")
        self.assertLessEqual(len(lines), 4)
        self.assertLessEqual(max(len(x) for x in lines) * size * 0.56, 1000)

    def test_short_slogans_get_the_largest_size(self):
        _, small = art.lay_out_text("Somebody Planted The Tree You're Sitting Under")
        _, large = art.lay_out_text("There's Room")
        self.assertGreater(large, small)

    def test_text_block_stays_on_the_canvas(self):
        for d in self.designs:
            lines, size = art.lay_out_text(d.slogan)
            bottom = art.TEXT_TOP + len(lines) * size * 1.22
            self.assertLess(bottom, art.H, f"{d.id} text runs off the canvas")

    def test_markup_in_a_slogan_is_escaped(self):
        d = catalog.Design(
            id="X9", slogan="Books & <Ideas>", theme="books", tone="warm",
            motif="books", format="punchline", tier="A", risk="low",
            risk_note="fine", saturation="low",
        )
        svg = art.render(d, "#141414")
        ET.fromstring(svg)
        self.assertIn("&amp;", svg)

    def test_contact_sheet_is_well_formed(self):
        ET.fromstring(art.contact_sheet(self.designs, "#141414"))

    def test_filenames_are_unique_and_safe(self):
        names = [art.slug(d) for d in self.designs]
        self.assertEqual(len(names), len(set(names)))
        for n in names:
            self.assertRegex(n, r"^D\d+-[a-z0-9-]+\.svg$")

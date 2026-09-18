"""Stdlib-only tests. Run from the repo root:

    python3 -m unittest discover -s tests -v
"""

import csv
import re
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
import prep_art  # noqa: E402
import typeset  # noqa: E402
import prompts  # noqa: E402
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

    def test_every_catalog_motif_has_an_asset(self):
        have = art.available_motifs()
        for d in self.designs:
            if d.motif != "none":
                self.assertIn(d.motif, have, f"{d.id} names a motif with no art")

    def test_every_asset_loads(self):
        for name in art.available_motifs():
            loaded = art.load_motif(name)
            self.assertIsNotNone(loaded, f"{name} failed to load")
            inner, (vw, vh), _ = loaded
            self.assertTrue(inner.strip(), f"{name} is empty")
            self.assertGreater(vw, 0)
            self.assertGreater(vh, 0)

    def test_assets_carry_no_partial_opacity(self):
        # Semi-transparent pixels give DTF a speckled white underbase, which is
        # why the solid "bold" weight is vendored rather than "duotone".
        bad = re.compile(r'opacity="0?[.]\d')
        for name in art.available_motifs():
            inner, _, _ = art.load_motif(name)
            self.assertIsNone(bad.search(inner), f"{name} has partial opacity")

    def test_stroke_drawn_assets_keep_their_fill_none(self):
        # Dropping the source fill="none" made a stroked icon print solid black.
        for name in art.available_motifs():
            _, _, paint = art.load_motif(name)
            if paint.get("stroke") and paint.get("stroke") != "none":
                self.assertEqual(paint.get("fill"), "none", f"{name} would fill solid")

    def test_art_dir_overrides_the_vendored_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "tree.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
                '<rect x="10" y="10" width="80" height="80"/></svg>'
            )
            inner, box, _ = art.load_motif("tree", d)
            self.assertIn("rect", inner)
            self.assertEqual(box, (100.0, 100.0))

    def test_every_design_renders_well_formed_svg(self):
        for d in self.designs:
            ET.fromstring(art.render(d, "#141414"))

    def test_svg_declares_print_size(self):
        svg = art.render(self.designs[0], "#141414")
        self.assertIn('width="12in"', svg)
        self.assertIn('height="14in"', svg)

    def test_motif_is_placed_at_a_printable_size(self):
        # A motif smaller than a third of the print width is lost on a shirt.
        self.assertGreater(art.MOTIF_SIZE, art.W / 3)

    def test_dimensions_come_from_width_height_when_no_viewbox(self):
        # vtracer writes width/height and no viewBox; falling through to the
        # 256 default scaled traced art about 3x too big.
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "tree.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" width="752" height="662">'
                '<path d="M0 0 L10 10" fill="#aa3311"/></svg>'
            )
            _, box, _ = art.load_motif("tree", d)
            self.assertEqual(box, (752.0, 662.0))

    def test_non_square_art_keeps_its_aspect_ratio(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "tree.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400">'
                '<path d="M0 0 L10 10" fill="#aa3311"/></svg>'
            )
            svg = "".join(art.motif_elements("tree", "#141414", d))
            scale = art.MOTIF_SIZE / 800.0
            self.assertIn(f"scale({scale:.5f})", svg)

    def test_full_colour_art_is_not_repainted(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "tree.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
                '<path d="M0 0 L9 9" fill="#f2b33d"/></svg>'
            )
            self.assertTrue(art.is_full_colour("tree", d))
            svg = "".join(art.motif_elements("tree", "#141414", d))
            self.assertIn("#f2b33d", svg)
            self.assertNotIn('fill="currentColor"', svg)

    def test_vendored_one_colour_art_still_takes_the_ink(self):
        self.assertFalse(art.is_full_colour("tree"))

    def test_repeated_motifs_render_twice(self):
        name = next(iter(art.REPEATS))
        svg = "".join(art.motif_elements(name, "#141414"))
        self.assertEqual(svg.count('<g transform="translate('), art.REPEATS[name])

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


class TestPrompts(unittest.TestCase):
    def setUp(self):
        self.designs = catalog.load()
        self.subjects = prompts.load_subjects()

    def test_every_design_has_a_subject(self):
        for d in self.designs:
            self.assertIn(d.id, self.subjects, f"{d.id} has no art subject")

    def test_no_orphan_subjects(self):
        ids = {d.id for d in self.designs}
        self.assertEqual(set(self.subjects) - ids, set())

    def test_subjects_are_concrete(self):
        for did, subject in self.subjects.items():
            self.assertGreater(len(subject.split()), 3, f"{did} subject is too thin")

    def test_no_subject_asks_for_text(self):
        # The style block forbids text; a subject naming words, numbers or a
        # date would fight it and the generator would render garbled letters.
        banned = ("house number", "sign reading", "labelled", "labeled",
                  "due date", "stamped on it", "spelling", "written")
        for did, subject in self.subjects.items():
            for word in banned:
                self.assertNotIn(word, subject.lower(), f"{did} asks for text: {word!r}")

    def test_every_format_builds_a_prompt(self):
        for fmt in ("generic", "midjourney", "dalle", "sd"):
            out = prompts.build("a fire hydrant", fmt)
            self.assertIn("fire hydrant", out)
            self.assertGreater(len(out), 80)

    def test_style_block_forbids_what_breaks_dtf(self):
        for killer in ("no gradients", "no shading", "no drop shadows",
                       "no texture", "no text"):
            self.assertIn(killer, prompts.STYLE)

    def test_negative_prompt_covers_partial_opacity(self):
        self.assertIn("semi-transparent", prompts.NEGATIVE)

    def test_midjourney_gets_its_flags(self):
        out = prompts.build("a ladder", "midjourney")
        self.assertIn("--no", out)
        self.assertIn("--ar 1:1", out)

    def test_markdown_names_the_output_filename(self):
        rows = [(d, self.subjects[d.id],
                 prompts.build(self.subjects[d.id], "generic"))
                for d in self.designs[:3]]
        md = prompts.render_markdown(rows, "generic")
        for d, _, _ in rows:
            self.assertIn(f"`{d.motif}.svg`", md)


class TestPrepArt(unittest.TestCase):
    """The raster -> print-ready-SVG last mile."""

    def setUp(self):
        from PIL import Image
        self.Image = Image

    def _card(self):
        """White field, a solid block, and an enclosed white hole inside it."""
        img = self.Image.new("RGBA", (60, 60), (255, 255, 255, 255))
        for x in range(10, 50):
            for y in range(10, 50):
                img.putpixel((x, y), (200, 40, 40, 255))
        for x in range(25, 35):
            for y in range(25, 35):
                img.putpixel((x, y), (255, 255, 255, 255))
        return img

    def test_edge_background_is_removed(self):
        out = prep_art.strip_background(self._card(), 12)
        self.assertEqual(out.getpixel((0, 0))[3], 0)

    def test_artwork_survives_background_removal(self):
        out = prep_art.strip_background(self._card(), 12)
        self.assertEqual(out.getpixel((15, 15))[3], 255)

    def test_enclosed_white_survives_the_flood(self):
        # This is the bug that put white blobs on the dark-shirt render: the
        # flood cannot reach background walled off by the artwork.
        out = prep_art.strip_background(self._card(), 12)
        self.assertEqual(out.getpixel((30, 30))[3], 255)
        self.assertGreater(prep_art.count_enclosed_white(out, 12), 0)

    def test_key_white_clears_the_enclosed_region(self):
        out = prep_art.strip_background(self._card(), 12)
        prep_art.key_white(out, 12)
        self.assertEqual(out.getpixel((30, 30))[3], 0)
        self.assertEqual(out.getpixel((15, 15))[3], 255)

    def test_alpha_is_hardened_to_fully_on_or_off(self):
        img = self.Image.new("RGBA", (4, 1), (10, 10, 10, 255))
        img.putpixel((0, 0), (10, 10, 10, 40))
        img.putpixel((1, 0), (10, 10, 10, 200))
        out, softened = prep_art.harden_alpha(img)
        self.assertEqual(softened, 2)
        for x in range(4):
            self.assertIn(out.getpixel((x, 0))[3], (0, 255))

    def test_trim_crops_to_content_and_keeps_a_margin(self):
        img = self.Image.new("RGBA", (200, 200), (255, 255, 255, 0))
        for x in range(80, 120):
            for y in range(80, 120):
                img.putpixel((x, y), (0, 0, 0, 255))
        out = prep_art.trim(img)
        self.assertLess(out.width, 200)
        # 40px of content plus a 3% margin on each side.
        self.assertGreater(out.width, 40)


class TestTypeset(unittest.TestCase):
    """Lockups and outlined type."""

    def setUp(self):
        self.designs = catalog.load()

    def test_connectives_drop_to_the_script_line(self):
        runs = typeset.split_runs("Democracy Is A Group Project")
        self.assertEqual(runs[0], ("Democracy", False))
        self.assertEqual(runs[1], ("Is A", True))
        self.assertFalse(runs[2][1])

    def test_leading_and_trailing_connectives_stay_attached(self):
        # "...Porch Light On" must not strand "On" on its own script line.
        runs = typeset.split_runs("Leave The Porch Light On")
        self.assertNotEqual(runs[-1][1], True)
        self.assertIn("On", runs[-1][0])

    def test_long_phrases_are_broken_so_they_can_set_large(self):
        # One long line scales down to fit the width and prints small.
        runs = typeset.split_runs("Casserole Democracy")
        self.assertEqual(len(runs), 2)

    def test_script_lines_are_capped(self):
        for d in self.designs:
            scripts = [r for r in typeset.split_runs(d.slogan) if r[1]]
            self.assertLessEqual(len(scripts), typeset.MAX_SCRIPT_LINES, d.id)

    def test_every_word_survives_the_lockup(self):
        for d in self.designs:
            got = " ".join(t for t, _ in typeset.split_runs(d.slogan)).split()
            self.assertEqual(got, d.slogan.split(), f"{d.id} lost or reordered words")

    def test_balance_keeps_line_count_sane(self):
        lines = typeset.balance(["Somebody", "Planted", "The", "Tree"], 11)
        self.assertGreaterEqual(len(lines), 1)
        self.assertLessEqual(len(lines), 4)

    def test_measure_scales_linearly(self):
        a = typeset.measure("Shovel", "display", 100.0)
        b = typeset.measure("Shovel", "display", 200.0)
        self.assertAlmostEqual(b, a * 2, places=3)

    def test_outline_emits_paths_not_text(self):
        svg = typeset.outline("Shovel", "display", 100.0, 600, 800)
        self.assertIn("<path", svg)
        self.assertNotIn("<text", svg)

    def test_rendered_type_is_outlines_not_text(self):
        # The whole point: no <text>, so nothing reflows on a machine that
        # lacks the font, and no manual outlining step before printing.
        svg = art.render(self.designs[0], "#141414")
        self.assertNotIn("<text", svg)
        self.assertIn("<path", svg)

    def test_lockup_fits_inside_the_text_band(self):
        for d in self.designs:
            lines = typeset.lay_out(d.slogan, art.W - 200, art.TEXT_TOP,
                                    art.TEXT_BOTTOM)
            self.assertLessEqual(lines[-1]["baseline"], art.TEXT_BOTTOM, d.id)
            self.assertGreater(lines[0]["baseline"], art.TEXT_TOP, d.id)

    def test_lockup_never_exceeds_the_print_width(self):
        for d in self.designs:
            for ln in typeset.lay_out(d.slogan, art.W - 200, art.TEXT_TOP,
                                      art.TEXT_BOTTOM):
                w = typeset.measure(ln["text"], ln["role"], ln["size"])
                self.assertLessEqual(round(w), art.W - 200, f"{d.id}: {ln['text']}")

    def test_every_design_renders_well_formed_svg_with_outlines(self):
        for d in self.designs:
            ET.fromstring(art.render(d, "#141414"))

    def test_fonts_are_vendored_with_licences(self):
        import json
        man = json.loads((typeset.FONT_DIR / "MANIFEST.json").read_text())
        for role in ("display", "script", "voice"):
            self.assertIn(role, man)
            self.assertTrue((typeset.FONT_DIR / f"{role}.ttf").exists())
        licences = list(typeset.FONT_DIR.glob("LICENSE-*"))
        self.assertGreaterEqual(len(licences), 3)

"""Headless Chrome tests: all three motifs, three pages, at 1600x900 and 430 wide, plus the PNG size.

Skipped with a clear message when Chrome or Chromium is missing.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import render  # noqa: E402
import unplug  # noqa: E402
from core import ritual  # noqa: E402

SAMPLE = json.loads((ROOT / "examples" / "unplug.sample.json").read_text(encoding="utf-8"))
STYLE = ROOT / "examples" / "style.rocha-coded.json"
NOW = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
MOTIFS = ("analog", "cyberpunk", "y2k-blog")
SIGNATURE = {"analog": "tape", "cyberpunk": "prompt", "y2k-blog": "bar"}


@unittest.skipUnless(render.find_chrome(), render.NO_CHROME)
class Motifs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        for motif in MOTIFS:
            unplug.build(SAMPLE, cls.root / motif, motif, STYLE, NOW, png=(motif == "analog"),
                         workdir=cls.root, home=cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_three_pages_three_motifs_two_widths_without_sideways_scroll(self):
        for motif in MOTIFS:
            for page, query in (("ritual.html", "?still"), ("release-card.html", "?still"), ("space.html", "?still")):
                for width, height in ((1600, 900), (430, 900)):
                    with self.subTest(motif=motif, page=page, width=width):
                        rep = render.measure(self.root / motif / page, width, height, query)
                        self.assertNotIn("error", rep, rep.get("error"))
                        self.assertEqual(rep["iw"], width)
                        self.assertLessEqual(rep["sw"], width, f"{motif} {page} scrolls sideways at {width}")
                        self.assertLessEqual(rep["frameRight"], width + 1)
                        self.assertIn(f"m-{motif}", rep["cls"])
                        self.assertTrue(rep[SIGNATURE[motif]], f"{motif} lost its signature on {page}")

    def test_ritual_screens_show_her_words_and_the_board_empties(self):
        page = self.root / "y2k-blog" / "ritual.html"
        first = render.measure(page, 1600, 900, "?still")
        self.assertEqual(first["shown"][0].strip(), ritual.screens()[0]["lines"][0][1])
        self.assertEqual((first["cords"], first["out"], first["lit"]), (6, 0, False))
        mid = render.measure(page, 1600, 900, "?still&step=7")
        self.assertEqual(mid["out"], 4)
        last = render.measure(page, 1600, 900, f"?still&step={len(ritual.screens()) - 1}")
        self.assertEqual(last["out"], 6)
        self.assertTrue(last["lit"])
        self.assertIn("Self-reflection:", last["shown"][0])

    def test_space_page_is_lit(self):
        rep = render.measure(self.root / "analog" / "space.html", 1600, 900, "?still")
        self.assertTrue(rep["lit"])
        self.assertEqual(rep["cords"], 0)
        self.assertIn(ritual.reflection(), rep["text"])

    def test_cards_are_1080_by_1350(self):
        for png in (self.root / "analog" / "release-card.png", self.root / "analog" / "private" / "release-card.png"):
            self.assertEqual(render.png_size(png), (1080, 1350))


if __name__ == "__main__":
    unittest.main()

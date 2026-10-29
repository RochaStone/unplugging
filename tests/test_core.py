"""Core tests: the ritual text, the interview, the share card, the moon, style, wording and the licence line.

Run from the kit folder:  python3 -m unittest discover -s tests -v
"""
from __future__ import annotations

import copy
import html
import json
import re
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import unplug  # noqa: E402
from core import board, card, moon, ritual, style as styles  # noqa: E402

SAMPLE = json.loads((ROOT / "examples" / "unplug.sample.json").read_text(encoding="utf-8"))
STYLE = ROOT / "examples" / "style.rocha-coded.json"
NOW = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
LICENCE = "Ritual text © Rochelle Livingstone, from Thriving in Transformational Times, all rights reserved."


def build(cfg, out, motif="analog", style=STYLE, home=None):
    tmp = Path(out).parent
    return unplug.build(cfg, out, motif, style, NOW, png=False, workdir=tmp, home=home or tmp)


def has_name(text: str, name: str) -> bool:
    return re.search(r"(?<![a-z0-9])" + re.escape(name.lower()) + r"(?![a-z0-9])", text.lower()) is not None


class RitualText(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name) / "out"
        build(SAMPLE, self.out)
        self.page = (self.out / "ritual.html").read_text(encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_embedded_text_matches_ritual_md_byte_for_byte(self):
        m = re.search(r'<script type="text/plain" id="ritual-source">(.*?)</script>', self.page, re.S)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1).encode("utf-8"), ritual.block().encode("utf-8"))

    def test_every_line_on_screen_is_her_line_and_every_line_of_hers_is_shown(self):
        screens = re.findall(r'<article class="scr[^"]*"[^>]*>(.*?)</article>', self.page, re.S)
        self.assertEqual(len(screens), len(ritual.screens()))
        on_screen = [html.unescape(t) for s in screens for t in re.findall(r"<(?:h1|h2|p)[^>]*>(.*?)</(?:h1|h2|p)>", s, re.S)]
        expected = [ritual.shown(line)[1] for line in ritual.block().split("\n") if line.strip()]
        self.assertEqual(on_screen, expected)

    def test_ritual_md_is_her_text_with_no_em_dash(self):
        text = ritual.block()
        self.assertTrue(text.startswith("**Cord Removal Ritual: Unplugging Energetic Attachments"))
        self.assertIn("at the root - not cutting them - to ensure they don't regrow", text)
        self.assertTrue(text.rstrip().endswith("create space for your growth and renewal?"))
        self.assertNotIn("\u2014", text)

    def test_six_steps_six_cords_and_the_reflection_is_last(self):
        self.assertEqual(ritual.step_count(), 6)
        self.assertEqual(self.page.count('class="cord '), 6)
        self.assertEqual(ritual.screens()[-1]["kind"], "reflect")

    def test_ritual_page_is_one_offline_file(self):
        self.assertNotRegex(self.page, r"<script[^>]+src=")
        for url in re.findall(r'(?:href|src)="(https?://[^"]+)"', self.page):
            self.assertTrue(url.startswith(("https://fonts.googleapis.com", "https://fonts.gstatic.com", "https://www.amazon.com/dp/B0DXNR3BNJ")), url)
        self.assertIn('aria-pressed="false">chime: off', self.page)
        self.assertNotIn("innerHTML", self.page)


class Interview(unittest.TestCase):
    ANSWERS = ["Wren", "the design app", "settings, billing", "too pricey", "no", "", "", "the midnight retainer",
               "Dorian Pike", "hours stopped fitting", "yes", "Dorian Pike", "Wrapping up",
               "I am closing my retainer work at the end of next month.", "", "", "", "",
               "slow mornings"]

    def run_interview(self, answers):
        feed = iter(answers)
        asked = []

        def ask(q):
            asked.append(q)
            return next(feed, "")
        return unplug.interview(ask, say=lambda s: None), asked

    def test_interview_writes_a_valid_config(self):
        cfg, asked = self.run_interview(self.ANSWERS)
        self.assertEqual(unplug.validate_config(cfg), [])
        self.assertEqual(len(cfg["items"]), 2)
        client = cfg["items"][1]
        self.assertEqual(client["kind"], "client")
        self.assertEqual(client["person"], "Dorian Pike")
        self.assertEqual(client["words"], "I am closing my retainer work at the end of next month.")
        self.assertEqual(cfg["space_for"], "slow mornings")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / unplug.CONFIG_NAME
            unplug.write_config(cfg, path)
            self.assertEqual(unplug.load_config(path), cfg)
            self.assertEqual(unplug.validate_config(unplug.load_config(path)), [])

    def test_one_question_at_a_time(self):
        _, asked = self.run_interview(self.ANSWERS)
        for q in asked:
            self.assertLessEqual(q.count("?"), 2, q)

    def test_bad_configs_are_named_kindly(self):
        bad = copy.deepcopy(SAMPLE)
        bad["items"][0]["kind"] = "ex"
        bad["items"][1]["needs_email"] = "yes"
        bad["motif"] = "vaporwave"
        errs = unplug.validate_config(bad)
        self.assertEqual(len(errs), 3, errs)
        many = {"items": [{"kind": "habit", "what": f"thing {i}"} for i in range(13)]}
        self.assertIn("switchboard holds 12", " ".join(unplug.validate_config(many)))
        self.assertTrue(unplug.validate_config({"items": []}))
        self.assertEqual(unplug.validate_config(SAMPLE), [])


class ShareCard(unittest.TestCase):
    def render(self, cfg):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            build(cfg, out)
            share = (out / "release-card.html").read_text(encoding="utf-8")
            private = (out / "private" / "release-card.html").read_text(encoding="utf-8")
            emails = (out / "no-emails.md").read_text(encoding="utf-8")
        return share, private, emails

    def test_share_card_never_names_a_person_and_private_card_does(self):
        share, private, _ = self.render(SAMPLE)
        names = card.private_names(SAMPLE)
        for n in ("Wren Calloway", "Dorian Pike", "Marisol Vance", "Dorian", "Marisol", "Wren"):
            self.assertIn(n, names)
        for n in names:
            self.assertFalse(has_name(share, n), f"{n} is on the share card")
        self.assertIn("Dorian Pike", private)
        self.assertIn("Marisol Vance", private)
        self.assertIn("the design app I open twice a year", share)

    def test_names_hidden_in_every_field_stay_off(self):
        cfg = copy.deepcopy(SAMPLE)
        cfg["items"].append({"kind": "commitment", "what": "Priya's podcast swap", "share_as": "Priya's swap"})
        cfg["items"].append({"kind": "yes", "what": "the board role", "email_to": "jo.marchetti@example.com",
                             "needs_email": True, "words": "Thank you, Jo."})
        cfg["people"].append("Priya")
        cfg["lines"]["intention"] = "Room to breathe, Dorian"
        share, private, _ = self.render(cfg)
        for n in card.private_names(cfg):
            self.assertFalse(has_name(share, n), f"{n} is on the share card")
        self.assertIn("Priya", private)
        self.assertIn("a commitment", share)

    def test_no_emails_are_drafts_in_her_own_words(self):
        _, _, emails = self.render(SAMPLE)
        self.assertIn("Every one of these is a draft", emails)
        for it in SAMPLE["items"]:
            if it.get("needs_email"):
                self.assertIn(it["words"], emails)
        self.assertEqual(emails.count("```text"), 3)
        self.assertIn("Wren Calloway", emails)


class Moon(unittest.TestCase):
    """Known dates from NASA's phase tables (UTC)."""

    def test_inside_a_waning_window(self):
        win = moon.waning_window(datetime(2025, 1, 20, tzinfo=timezone.utc))
        self.assertTrue(win["now"])
        self.assertLess(abs((win["full"] - datetime(2025, 1, 13, 22, 27, tzinfo=timezone.utc)).total_seconds()), 600)
        self.assertLess(abs((win["new"] - datetime(2025, 1, 29, 12, 36, tzinfo=timezone.utc)).total_seconds()), 600)

    def test_waxing_points_to_the_next_window(self):
        win = moon.waning_window(datetime(2024, 4, 10, tzinfo=timezone.utc))
        self.assertFalse(win["now"])
        self.assertLess(abs((win["full"] - datetime(2024, 4, 23, 23, 49, tzinfo=timezone.utc)).total_seconds()), 600)
        self.assertLess(abs((win["new"] - datetime(2024, 5, 8, 3, 22, tzinfo=timezone.utc)).total_seconds()), 600)

    def test_card_says_this_is_the_window_only_when_waning(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            unplug.build(SAMPLE, out, None, STYLE, datetime(2025, 1, 20, 12, tzinfo=timezone.utc), png=False,
                         workdir=Path(tmp), home=Path(tmp))
            self.assertIn("this is the window", (out / "release-card.html").read_text(encoding="utf-8"))
            unplug.build(SAMPLE, out, None, STYLE, datetime(2024, 4, 10, 12, tzinfo=timezone.utc), png=False,
                         workdir=Path(tmp), home=Path(tmp))
            page = (out / "release-card.html").read_text(encoding="utf-8")
            self.assertIn("next waning moon", page)
            self.assertIn("23 APR 2024 to 08 MAY 2024", page)
            self.assertNotRegex(page.lower(), r"only works|works best|must be done")


class Style(unittest.TestCase):
    def test_fallback_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd, home = Path(tmp) / "cwd", Path(tmp) / "home"
            (home / ".rocha-coded").mkdir(parents=True)
            cwd.mkdir()
            self.assertEqual(styles.find_style(cwd=cwd, home=home), styles.STYLE_EXAMPLE)
            (home / ".rocha-coded" / "style.json").write_text("{}")
            self.assertEqual(styles.find_style(cwd=cwd, home=home), home / ".rocha-coded" / "style.json")
            (cwd / "style.json").write_text("{}")
            self.assertEqual(styles.find_style(cwd=cwd, home=home), cwd / "style.json")

    def test_user_style_borrows_only_palette_and_fonts(self):
        with tempfile.TemporaryDirectory() as tmp:
            mine = Path(tmp) / "style.json"
            mine.write_text(json.dumps({"palette": {"accent": "#00AA88"}, "motif": "cyberpunk"}))
            raw, is_example = styles.load_style(mine)
            self.assertFalse(is_example)
            self.assertEqual(raw["palette"]["accent"], "#00AA88")
            self.assertEqual(raw["palette"]["plum"], "#50163C")
            self.assertNotIn("lines", raw)
            self.assertNotIn("handle", raw)
            out = Path(tmp) / "out"
            cfg = {k: v for k, v in SAMPLE.items() if k != "motif"}
            build(cfg, out, motif=None, style=mine)
            page = (out / "release-card.html").read_text(encoding="utf-8")
            self.assertIn('class="m-cyberpunk', page)
            for line in ("LORE", "@rocheverse", "I AM SO LUCKY", "EVERYTHING WORKS OUT FOR ME"):
                self.assertNotIn(line, page)

    def test_her_words_stay_off_a_founders_card_with_the_bundled_example(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            build(SAMPLE, out)
            page = (out / "release-card.html").read_text(encoding="utf-8")
            self.assertNotIn("@rocheverse", page)
            self.assertNotIn(">LORE<", page)

    def test_a_founders_own_stamp_and_handle_appear(self):
        with tempfile.TemporaryDirectory() as tmp:
            mine = Path(tmp) / "style.json"
            mine.write_text(json.dumps({"handle": "@wrenmakes", "lines": {"stamp": "DONE"}}))
            out = Path(tmp) / "out"
            build(SAMPLE, out, style=mine)
            page = (out / "release-card.html").read_text(encoding="utf-8")
            self.assertIn("@wrenmakes", page)
            self.assertIn(">DONE<", page)

    def test_her_own_plug_and_socket_drawings_are_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            mine = Path(tmp) / "objects" / "mine"
            mine.mkdir(parents=True)
            (mine / "plug.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"/>')
            art = board.find_art(mine)
            self.assertTrue(art["plug"].startswith("data:image/svg+xml;base64,"))
            self.assertNotIn("socket", art)
            out = Path(tmp) / "out"
            build(SAMPLE, out)
            self.assertIn('class="sb-plug-art"', (out / "ritual.html").read_text(encoding="utf-8"))


class Wording(unittest.TestCase):
    BANNED = re.compile(r"\b(simply|just|actually|undocumented|helpers?)\b|\u2014", re.I)
    NEGATIVE_OPENER = re.compile(r"(?:^|[.!?]\s+|^\s*(?:[-*]|\d+\.)\s+)(No|Not|Never|Nothing|None|Don't|Do not)\b")

    def shipped_text(self):
        files = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix in (".md", ".py", ".json", ".html")
                 and not ({"tests", "dist", "out", ".git", "__pycache__"} & set(p.relative_to(ROOT).parts))]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            build(SAMPLE, out)
            pages = {f"out/{p.relative_to(out)}": p.read_text(encoding="utf-8") for p in out.rglob("*.*")
                     if p.suffix in (".html", ".md")}
        texts = {str(p.relative_to(ROOT)): p.read_text(encoding="utf-8") for p in files}
        texts.update(pages)
        return texts

    def test_no_banned_words_or_em_dashes(self):
        for name, text in self.shipped_text().items():
            for i, line in enumerate(text.splitlines(), 1):
                self.assertIsNone(self.BANNED.search(line), f"{name}:{i}: {line.strip()[:100]}")

    def test_no_sentence_opens_on_a_negative_in_the_copy(self):
        for name in ("README.md", "SKILL.md", "STYLE.md", "LICENSE-RITUAL.md", "objects/mine/README.md"):
            text = re.sub(r"```.*?```", "", (ROOT / name).read_text(encoding="utf-8"), flags=re.S)
            for i, line in enumerate(text.splitlines(), 1):
                self.assertIsNone(self.NEGATIVE_OPENER.search(line), f"{name}:{i}: {line.strip()[:100]}")

    def test_no_cutting_imagery_outside_her_own_sentence(self):
        for name, text in self.shipped_text().items():
            if name.endswith(".py") or name == "ritual/RITUAL.md":
                continue
            rest = text.replace(ritual.block(), "")
            self.assertNotRegex(rest.lower(), r"scissor|\bsnip|\bsever", name)

    def test_nothing_phones_home(self):
        for p in [*ROOT.glob("*.py"), *(ROOT / "core").glob("*.py"), *(ROOT / "scripts").glob("*.py")]:
            src = p.read_text(encoding="utf-8")
            self.assertNotRegex(src, r"urllib\.request|http\.client|import socket|requests\b|smtplib", p.name)


class Licence(unittest.TestCase):
    def test_licence_line_in_the_three_places_and_on_the_page(self):
        md = (ROOT / "ritual" / "RITUAL.md").read_text(encoding="utf-8")
        self.assertTrue(md.startswith(LICENCE + "\n"))
        self.assertIn(LICENCE, (ROOT / "LICENSE-RITUAL.md").read_text(encoding="utf-8"))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        credits = readme[readme.index("## Credits"):readme.index("## Made by Rocha")]
        self.assertIn(LICENCE, credits)
        self.assertIn("https://www.amazon.com/dp/B0DXNR3BNJ", credits)
        self.assertEqual(ritual.LICENCE_LINE, LICENCE)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            build(SAMPLE, out)
            for page in ("ritual.html", "space.html"):
                text = html.unescape((out / page).read_text(encoding="utf-8"))
                self.assertIn(LICENCE, text)
                self.assertIn("This is a reflective practice, not therapy.", text)

    def test_the_mit_licence_covers_the_code(self):
        self.assertIn("MIT License", (ROOT / "LICENSE").read_text(encoding="utf-8"))
        self.assertIn("Copyright (c) 2026 Rochelle Livingstone / Thriving Era Studio",
                      (ROOT / "LICENSE").read_text(encoding="utf-8"))


class Files(unittest.TestCase):
    def test_every_file_under_500_lines_and_the_style_example_matches_the_collection(self):
        for p in ROOT.rglob("*"):
            if p.is_file() and p.suffix in (".py", ".md", ".json") and ".git" not in p.parts:
                self.assertLess(len(p.read_text(encoding="utf-8").splitlines()), 500, p.name)
        sibling = ROOT.parent / "desktop-altar" / "examples" / "style.rocha-coded.json"
        if sibling.exists():
            self.assertEqual(sibling.read_bytes(), STYLE.read_bytes())


if __name__ == "__main__":
    unittest.main()

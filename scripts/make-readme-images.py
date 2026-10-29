#!/usr/bin/env python3
"""Generate every image the README uses, from the kit itself. Needs Chrome or Chromium for the PNGs.

  python3 scripts/make-readme-images.py

Writes:
  docs/img/hero-y2k.png       the switchboard in the y2k-blog window, one cord being unplugged (1600x900)
  docs/img/triptych.png       the sample release card in analog | cyberpunk | y2k-blog
  docs/img/ritual.png         the guided ritual page at step 4, analog
  docs/img/space.png          the space page, cyberpunk
  docs/img/step-01..05.svg    pixel step badges for "Start here"
  docs/img/divider.svg        a gold pixel hairline
  docs/img/heart.svg          a pixel heart
Everything uses the bundled Rocha Coded style and the fictional sample founder in examples/unplug.sample.json.
The badge, divider and heart drawings are the same as the sibling kit desktop-altar's (MIT).
"""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import render  # noqa: E402
import unplug  # noqa: E402
from core import board, card, frame, style as styles  # noqa: E402

IMG = ROOT / "docs" / "img"
STYLE = ROOT / "examples" / "style.rocha-coded.json"
SAMPLE = ROOT / "examples" / "unplug.sample.json"
NOW = datetime(2026, 10, 29, 12, 0, tzinfo=timezone.utc)
ORDER = ("analog", "cyberpunk", "y2k-blog")
DIGITS = {"0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"],
          "2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "111", "001", "111"],
          "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"]}


def _pixels(text: str, x0: int, y0: int) -> str:
    return "".join(f"M{x0 + n * 4 + c} {y0 + r}h1v1h-1z" for n, ch in enumerate(text)
                   for r, row in enumerate(DIGITS[ch]) for c, bit in enumerate(row) if bit == "1")


def badge(num: str, ground: str, gold: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 11 9" width="33" height="27" '
            f'shape-rendering="crispEdges"><path fill="{ground}" d="M1 0h9v1h1v7h-1v1H1v-1H0V1h1z"/>'
            f'<path fill="{gold}" d="{_pixels(num, 2, 2)}"/></svg>\n')


def divider(gold: str) -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="720" height="6" shape-rendering="crispEdges">'
            '<defs><pattern id="p" width="12" height="6" patternUnits="userSpaceOnUse">'
            f'<rect width="6" height="2" y="2" fill="{gold}"/><rect x="8" y="2" width="2" height="2" fill="{gold}"/>'
            '</pattern></defs><rect width="720" height="6" fill="url(#p)"/></svg>\n')


def heart(colour: str) -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 7 6" width="21" height="18" shape-rendering="crispEdges">'
            f'<path fill="{colour}" d="M1 0h2v1h1V0h2v1h1v2H6v1H5v1H4v1H3V5H2V4H1V3H0V1h1z"/></svg>\n')


HERO_CSS = """
html.hero .stage{padding:34px 60px;height:100vh}
html.hero .frame{height:100%}
html.hero .body{height:100%;grid-template-columns:minmax(0,1fr) 230px}
.hero-main{display:grid;grid-template-columns:minmax(0,.72fr) minmax(0,1.28fr);gap:34px;align-items:center;height:100%}
.hero-main h1{font-size:64px;line-height:.96;margin:0 0 18px}
.hero-main .sub{font:800 26px var(--f-label),system-ui,sans-serif;margin:0 0 22px}
.hero-main .chip{display:inline-block;font:500 14px var(--f-mono),monospace;letter-spacing:.1em;border:2px solid var(--ink);padding:6px 12px;background:var(--paper_pink)}
"""


def hero_html(style: dict) -> str:
    states = ["plugged", "out", "pulling", "plugged", "plugged", "plugged"]
    main = ('<div class="hero-main"><div><p class="kicker">unplugging</p>'
            '<h1>Unplug what drains you, at the root.</h1>'
            '<p class="sub">Her ritual, then the actual list.</p>'
            '<span class="chip">a free Rocha Coded tool</span></div>'
            f'<div>{board.board(6, states=states, label="a switchboard, one cord being unplugged")}</div></div>')
    side = frame.sidebar("29 OCT 2026", "waning gibbous", 0.6, "unplugging", "unplugging", "")
    return frame.page(title="unplugging", window="unplugging.exe", prompt="unplug:~$", motif="y2k-blog",
                      style=style, main=main, side=side, extra_css=HERO_CSS, html_class="hero still")


TRIPTYCH = """<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:{bg};display:flex;gap:40px;justify-content:center;align-items:center;height:100vh;
font:500 15px ui-monospace,monospace;color:{ink};letter-spacing:.12em}}
figure{{margin:0;text-align:center}} img{{width:440px;display:block;box-shadow:0 14px 26px -16px rgba(40,10,30,.55)}}
figcaption{{margin-top:14px}}</style></head><body>{figs}</body></html>"""


def main() -> int:
    IMG.mkdir(parents=True, exist_ok=True)
    style_raw, _ = styles.load_style(STYLE)
    style = styles.page_style(style_raw, True)
    pal = style["palette"]
    for i in range(1, 6):
        (IMG / f"step-{i:02d}.svg").write_text(badge(f"{i:02d}", pal["plum"], pal["gold"]), encoding="utf-8")
    (IMG / "divider.svg").write_text(divider(pal["gold"]), encoding="utf-8")
    (IMG / "heart.svg").write_text(heart(pal["accent"]), encoding="utf-8")
    if not render.find_chrome():
        print(render.NO_CHROME)
        return 1
    cfg = json.loads(SAMPLE.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        hero = tmp / "hero.html"
        hero.write_text(hero_html(style), encoding="utf-8")
        print(render.screenshot(hero.as_uri(), IMG / "hero-y2k.png", 1600, 900)[1])
        cards = []
        for motif in ORDER:
            out = tmp / motif
            unplug.build(cfg, out, motif, STYLE, NOW, png=True, workdir=tmp, home=tmp)
            cards.append((motif, out / "release-card.png"))
        figs = "".join(f'<figure><img src="{p.as_uri()}" alt=""><figcaption>{m}</figcaption></figure>' for m, p in cards)
        trip = tmp / "triptych.html"
        trip.write_text(TRIPTYCH.format(bg=pal["paper_pink"], ink=pal["ink"], figs=figs), encoding="utf-8")
        print(render.screenshot(trip.as_uri(), IMG / "triptych.png", 1600, 720)[1])
        ritual = (tmp / "analog" / "ritual.html").as_uri() + "?still&step=6&pull"
        print(render.screenshot(ritual, IMG / "ritual.png", 1440, 1180)[1])
        space = (tmp / "cyberpunk" / "space.html").as_uri() + "?still"
        print(render.screenshot(space, IMG / "space.png", 1440, 1100)[1])
    print("READY. The README images are in docs/img/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""One page shell, three motif skins: analog (paper you could hold), cyberpunk (the girly terminal),
y2k-blog (the 2003 blog window). Every page in the kit renders through `page()`.

Motifs are structure. The palette and fonts from style.json are colour and type, so one file re-tones all three.
"""
from __future__ import annotations

from html import escape
from urllib.parse import quote, quote_plus

from .board import BOARD_CSS

PIXEL = "Silkscreen"
AXES = {"Fraunces": ":opsz,wght@9..144,400;9..144,900", "Bricolage Grotesque": ":wght@400;800",
        "DM Mono": ":wght@400;500", "Silkscreen": ":wght@400;700"}
STAR = ["0001000", "0001000", "1111111", "0111110", "0110110", "1000001"]


def fonts_href(fonts: dict) -> str:
    names = list(dict.fromkeys([*fonts.values(), PIXEL]))
    fams = "&".join(f"family={quote_plus(n)}{AXES.get(n, '')}" for n in names)
    return f"https://fonts.googleapis.com/css2?{fams}&display=swap"


def star_tile(gold: str) -> str:
    rects = "".join(f'<rect x="{12 + c}" y="{10 + r}" width="1" height="1"/>'
                    for r, row in enumerate(STAR) for c, v in enumerate(row) if v == "1")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" shape-rendering="crispEdges">'
           f'<g fill="{gold}" transform="scale(2)">{rects}</g></svg>')
    return "data:image/svg+xml," + quote(svg)


GRAIN = ("data:image/svg+xml," + quote(
    '<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240"><filter id="n">'
    '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" stitchTiles="stitch"/>'
    '<feColorMatrix values="0 0 0 0 .2 0 0 0 0 .05 0 0 0 0 .15 0 0 0 .09 0"/></filter>'
    '<rect width="240" height="240" filter="url(#n)"/></svg>'))

BASE_CSS = """
*{box-sizing:border-box}
html,body{margin:0}
body{min-height:100vh;font-family:var(--f-body),Georgia,serif;color:var(--ink);overflow-x:hidden}
.stage{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:clamp(12px,3vw,40px)}
.frame{position:relative;width:min(1180px,100%);display:flex;flex-direction:column}
.screen{position:relative;flex:1;display:flex;flex-direction:column}
.body{display:grid;grid-template-columns:minmax(0,1fr) minmax(180px,250px);gap:clamp(14px,2.4vw,32px);padding:clamp(16px,3vw,40px)}
.main{min-width:0}
.side{min-width:0;display:flex;flex-direction:column;gap:12px;font-family:var(--f-mono),ui-monospace,monospace;font-size:13px}
.kicker{font:800 13px/1.2 var(--f-label),system-ui,sans-serif;letter-spacing:.06em;text-transform:lowercase;margin:0 0 8px;color:var(--marker)}
h1,h2.h{font-family:var(--f-mast),Georgia,serif;font-weight:900;line-height:1.02;margin:0 0 14px;overflow-wrap:anywhere}
.mono{font-family:var(--f-mono),ui-monospace,monospace}
.tape,.screws,.bar,.prompt,.y2k,.datestamp,.leds{display:none}
.moonbox{display:flex;align-items:center;gap:10px}
.moonbox svg{width:46px;height:46px;flex:none}
.moon-dark{fill:var(--wine)}
.moon-lit{fill:var(--paper)}
.moon-ring{fill:none;stroke:var(--gold);stroke-width:2}
.stamp{align-self:flex-start;font:400 22px var(--f-scrawl),cursive;color:var(--marker);border:2px solid var(--marker);padding:2px 10px;transform:rotate(-5deg)}
.stamp:empty{display:none}
button{font:800 14px var(--f-label),system-ui,sans-serif;cursor:pointer}
.credit{font:400 12px/1.5 var(--f-mono),monospace;opacity:.8}
.credit p{margin:0 0 4px}
.credit a{color:inherit}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
@media (max-width:760px){.body{grid-template-columns:1fr}.side{flex-direction:row;flex-wrap:wrap;align-items:center}}

/* analog: paper you could hold */
.m-analog body{background:var(--paper) url("GRAIN")}
.m-analog .frame{background:var(--paper_pink) url("GRAIN");box-shadow:0 18px 30px -18px rgba(40,10,30,.45),0 2px 4px rgba(40,10,30,.18);transform:rotate(-.35deg)}
.m-analog .tape{display:block;position:absolute;width:120px;height:30px;background:var(--accent);opacity:.82;z-index:2}
.m-analog .t1{top:-12px;left:8%;transform:rotate(-4deg)}
.m-analog .t2{top:-12px;right:9%;transform:rotate(5deg)}
.m-analog h1,.m-analog h2.h{color:var(--plum)}
.m-analog .datestamp{display:inline-block;align-self:flex-start;font:500 13px var(--f-mono),monospace;color:var(--marker);border:2px solid var(--marker);border-radius:4px;padding:3px 8px;letter-spacing:.12em;transform:rotate(3deg)}

/* cyberpunk: the girly terminal, a plum cyberdeck with gold screws */
.m-cyberpunk body{background:var(--ink)}
.m-cyberpunk .frame{background:var(--wine);border-radius:26px;padding:20px;box-shadow:inset 0 0 0 3px var(--plum),0 20px 40px -20px #000}
.m-cyberpunk .screws{display:block}
.m-cyberpunk .screws i{position:absolute;width:12px;height:12px;border-radius:50%;background:var(--gold);box-shadow:inset 0 0 0 3px var(--wine)}
.m-cyberpunk .screws i:nth-child(1){top:6px;left:6px}.m-cyberpunk .screws i:nth-child(2){top:6px;right:6px}
.m-cyberpunk .screws i:nth-child(3){bottom:6px;left:6px}.m-cyberpunk .screws i:nth-child(4){bottom:6px;right:6px}
.m-cyberpunk .screen{background:var(--plum) repeating-linear-gradient(0deg,rgba(0,0,0,.14) 0 1px,transparent 1px 4px);border-radius:14px;color:var(--paper)}
.m-cyberpunk .prompt{display:block;margin:0;padding:14px clamp(16px,3vw,40px) 0;font:500 14px var(--f-mono),monospace;color:var(--gold);overflow-wrap:anywhere}
.m-cyberpunk .cursor{display:inline-block;width:.6em;height:1em;background:var(--accent);vertical-align:-2px;margin-left:4px;animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.m-cyberpunk h1,.m-cyberpunk h2.h{font-family:var(--f-label),system-ui,sans-serif;font-weight:800;color:var(--paper)}
.m-cyberpunk .kicker{font-family:var(--pixel),monospace;color:var(--accent)}
.m-cyberpunk .credit a{color:var(--accent)}
.m-cyberpunk .leds{display:flex;gap:8px}
.m-cyberpunk .leds i{width:10px;height:10px;border-radius:50%;background:var(--accent)}
.m-cyberpunk .leds i:nth-child(2){background:var(--gold)}
.m-cyberpunk .leds i:nth-child(3){background:var(--paper_pink);opacity:.5}
.m-cyberpunk .moon-dark{fill:var(--ink)}
.m-cyberpunk .sb-panel{fill:var(--ink)}
.m-cyberpunk .stamp{color:var(--accent);border-color:var(--accent)}
html.still .cursor{animation:none}

/* y2k-blog: the 2003 window, cream with a plum title bar */
.m-y2k-blog body{background:var(--paper_pink) url("STARS")}
.m-y2k-blog .frame{background:var(--paper);border:2px solid var(--ink);box-shadow:6px 6px 0 var(--plum)}
.m-y2k-blog .bar{display:flex;align-items:center;gap:10px;background:var(--plum);color:var(--paper);padding:6px 10px;font:700 13px var(--pixel),monospace;letter-spacing:.04em}
.m-y2k-blog .btns{display:flex;gap:5px}
.m-y2k-blog .btns i{width:13px;height:13px;border:1px solid var(--ink);background:var(--gold)}
.m-y2k-blog .title{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.m-y2k-blog h1,.m-y2k-blog h2.h{color:var(--plum)}
.m-y2k-blog .y2k{display:block;border:1px dashed var(--ink);background:var(--paper_pink);padding:8px 10px}
.m-y2k-blog .y2k h3{margin:0 0 4px;font:700 11px var(--pixel),monospace;color:var(--plum);text-transform:lowercase}
.m-y2k-blog .y2k p{margin:0}
.m-y2k-blog .counter{font:500 12px var(--f-mono),monospace}
@media (max-width:760px){.m-y2k-blog .y2k{flex:1 1 140px}}
"""


def moon_svg(age: float) -> str:
    """A small moon in the sidebar, lit side drawn from the lunation age (0 new, .5 full)."""
    import math
    r, k = 20.0, math.cos(2 * math.pi * age)
    rx, right = abs(k) * r, age < 0.5
    first = 1 if right else 0
    back = (0 if k > 0 else 1) if right else (1 if k > 0 else 0)
    lit = "" if age < 0.02 or age > 0.98 else (
        f'<path class="moon-lit" d="M24 4 A20 20 0 0 {first} 24 44 A{rx:.2f} 20 0 0 {back} 24 4 Z"/>')
    return (f'<svg viewBox="0 0 48 48" aria-hidden="true"><circle class="moon-dark" cx="24" cy="24" r="20"/>{lit}'
            f'<circle class="moon-ring" cx="24" cy="24" r="20"/></svg>')


def sidebar(today: str, phase: str, age: float, about: str, mood: str, stamp: str, extra: str = "") -> str:
    return (f'<span class="leds" aria-hidden="true"><i></i><i></i><i></i></span>'
            f'<div class="moonbox">{moon_svg(age)}<span>{escape(phase)}</span></div>'
            f'<span class="datestamp">{escape(today)}</span>{extra}'
            f'<span class="stamp">{escape(stamp)}</span>'
            f'<div class="y2k"><h3>about me</h3><p>{escape(about)}</p></div>'
            f'<div class="y2k"><h3>mood</h3><p>&#10023; {escape(mood)}</p></div>'
            f'<div class="y2k"><p class="counter">you are visitor no. 000,777</p></div>'
            f'<div class="y2k"><p>last updated {escape(today)}</p></div>')


def page(*, title: str, window: str, prompt: str, motif: str, style: dict, main: str, side: str,
         extra_css: str = "", script: str = "", data_json: str = "", html_class: str = "") -> str:
    pal, fonts = style["palette"], style["fonts"]
    tokens = ";".join(f"--{k}:{v}" for k, v in pal.items())
    font_vars = ";".join(f"--f-{'mast' if k == 'masthead' else k}:'{v}'" for k, v in fonts.items())
    css = (BASE_CSS.replace("GRAIN", GRAIN).replace("STARS", star_tile(pal["gold"])) + BOARD_CSS + extra_css
           + f":root{{{tokens};{font_vars};--pixel:'{PIXEL}'}}")
    data = f'<script type="application/json" id="kit-data">{data_json}</script>' if data_json else ""
    js = f"<script>{script}</script>" if script else ""
    return f"""<!doctype html>
<html lang="en" class="m-{motif} {html_class}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{escape(fonts_href(fonts))}">
<style>{css}</style>
<script>if (/[?&]still/.test(location.search)) document.documentElement.classList.add("still");</script>
</head>
<body>
<main class="stage">
<div class="frame">
<span class="tape t1"></span><span class="tape t2"></span><span class="screws"><i></i><i></i><i></i><i></i></span>
<div class="bar"><span class="btns"><i></i><i></i><i></i></span><span class="title">{escape(window)}</span></div>
<div class="screen">
<p class="prompt">{escape(prompt)}<span class="cursor"></span></p>
<div class="body">
<section class="main">{main}</section>
<aside class="side">{side}</aside>
</div>
</div>
</div>
</main>
{data}{js}
</body>
</html>
"""

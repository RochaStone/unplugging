"""The switchboard: sockets on a panel, cords plugged in, each one unplugged at the root.

One function draws every state the kit needs:
  plugged   the cord sits in its socket
  pulling   the plug is halfway out, prongs showing (the README hero)
  out       the plug has left the socket and the cord dissolves into gold dots of light
  dropped   the plug hangs below its empty socket (the release card, a still picture)
  lit       the board is empty and every socket is filled with light (the last screen and the space page)

Colours come from CSS classes (sb-*) that each page styles from style.json, so a palette re-tones the board.
A founder's own drawings in objects/mine/ replace the drawn plug and socket.
No cutting imagery anywhere: cords are unplugged, never cut.
"""
from __future__ import annotations

import base64
import math
from html import escape
from pathlib import Path

W, H = 600, 440
PANEL_BOTTOM = H - 6
STATES = ("plugged", "pulling", "out", "dropped")
MAX_SOCKETS = 12
MAX_ART_BYTES = 2 * 1024 * 1024
ART_TYPES = {".svg": "image/svg+xml", ".png": "image/png"}


def find_art(folder: Path) -> dict:
    """Look for plug.svg/png and socket.svg/png in objects/mine. Returns data URIs for the ones found."""
    art: dict[str, str] = {}
    for part in ("plug", "socket"):
        for ext, mime in ART_TYPES.items():
            p = Path(folder) / f"{part}{ext}"
            if p.is_file() and 0 < p.stat().st_size <= MAX_ART_BYTES:
                data = base64.b64encode(p.read_bytes()).decode("ascii")
                art[part] = f"data:{mime};base64,{data}"
                break
    return art


def layout(n: int) -> list[tuple[float, float]]:
    """Socket centres for n sockets. Rows are staggered so a cord from a top socket drops between the ones below."""
    n = max(1, min(n, MAX_SOCKETS))
    cols = n if n <= 4 else (3 if n <= 6 else 4)
    rows = math.ceil(n / cols)
    top, bottom = 96, PANEL_BOTTOM - 120
    gap_y = (bottom - top) / max(rows - 1, 1) if rows > 1 else 0
    span = 380 if cols > 1 else 0
    step = span / max(cols - 1, 1)
    out = []
    for i in range(n):
        r, c = divmod(i, cols)
        in_row = min(cols, n - r * cols)
        x = W / 2 - step * (in_row - 1) / 2 + step * c
        if rows > 1:
            x += (step / 4) * (1 if r % 2 else -1)
        y = top + gap_y * r if rows > 1 else (top + bottom) / 2 + 10
        out.append((round(x, 1), round(y, 1)))
    return out


def _socket(x: float, y: float, i: int, lit: bool, art: dict) -> str:
    if art.get("socket"):
        face = f'<image href="{art["socket"]}" x="{x - 30}" y="{y - 30}" width="60" height="60"/>'
    else:
        face = (f'<circle class="sb-socket" cx="{x}" cy="{y}" r="28"/>'
                f'<circle class="sb-hole" cx="{x}" cy="{y}" r="17"/>'
                f'<rect class="sb-slot" x="{x - 8}" y="{y - 8}" width="4" height="12" rx="1"/>'
                f'<rect class="sb-slot" x="{x + 4}" y="{y - 8}" width="4" height="12" rx="1"/>')
    light = (f'<g class="sb-light"><circle cx="{x}" cy="{y}" r="27"/><circle class="sb-light-in" cx="{x}" cy="{y}" r="15"/>'
             f'<circle class="sb-light-core" cx="{x}" cy="{y}" r="6"/></g>')
    num = f'<text class="sb-num" x="{x}" y="{y - 38}" text-anchor="middle">{i + 1:02d}</text>'
    return f'<g class="socket{" lit" if lit else ""}" data-i="{i}">{face}{light}{num}</g>'


def _plug(x: float, y: float, art: dict) -> str:
    if art.get("plug"):
        return f'<image class="sb-plug-art" href="{art["plug"]}" x="{x - 22}" y="{y - 24}" width="44" height="52"/>'
    return (f'<rect class="sb-prong" x="{x - 8}" y="{y - 22}" width="4" height="14" rx="1"/>'
            f'<rect class="sb-prong" x="{x + 4}" y="{y - 22}" width="4" height="14" rx="1"/>'
            f'<rect class="sb-plug" x="{x - 17}" y="{y - 10}" width="34" height="38" rx="8"/>'
            f'<rect class="sb-collar" x="{x - 17}" y="{y - 10}" width="34" height="7" rx="3"/>'
            f'<rect class="sb-grip" x="{x - 9}" y="{y + 8}" width="18" height="3" rx="1.5"/>'
            f'<rect class="sb-grip" x="{x - 9}" y="{y + 15}" width="18" height="3" rx="1.5"/>')


def _wire(x: float, y: float, i: int, n: int) -> str:
    """A soft cord from the plug, falling straight past the sockets below and off the bottom of the board."""
    sway = (12, -10, 8, -14)[i % 4]
    return f"M{x} {y + 28} C{x} {y + 150}, {x + sway} {H - 70}, {x + sway * 1.6:.1f} {H + 40}"


def _cord(x: float, y: float, i: int, n: int, state: str, art: dict) -> str:
    wire = _wire(x, y, i, n)
    ghost = f'<path class="sb-ghost" d="{wire}"/>'
    body = f'<g class="sb-move"><path class="sb-wire" d="{wire}"/><g class="sb-head">{_plug(x, y, art)}</g></g>'
    return f'<g class="cord {state}" data-i="{i}">{ghost}{body}</g>'


def board(n: int, states: list[str] | None = None, art: dict | None = None, label: str = "switchboard",
          lit: bool = False) -> str:
    """Draw the switchboard. `states` gives each cord's state; `lit` empties the board and fills it with light."""
    n = max(1, min(int(n), MAX_SOCKETS))
    art = art or {}
    states = list(states or [])
    states = [s if s in STATES else "plugged" for s in states] + ["plugged"] * (n - len(states))
    pts = layout(n)
    screws = "".join(f'<circle class="sb-screw" cx="{cx}" cy="{cy}" r="7"/>'
                     f'<rect class="sb-screw-slot" x="{cx - 4}" y="{cy - 1}" width="8" height="2"/>'
                     for cx, cy in ((28, 28), (W - 28, 28), (28, H - 28), (W - 28, H - 28)))
    sockets = "".join(_socket(x, y, i, lit, art) for i, (x, y) in enumerate(pts))
    cords = "" if lit else "".join(_cord(x, y, i, n, states[i], art) for i, (x, y) in enumerate(pts))
    return (f'<svg class="board{" is-lit" if lit else ""}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{escape(label)}" preserveAspectRatio="xMidYMid meet">'
            f'<rect class="sb-panel" x="6" y="6" width="{W - 12}" height="{H - 12}" rx="22"/>'
            f'<rect class="sb-rim" x="16" y="16" width="{W - 32}" height="{H - 32}" rx="14"/>'
            f'<rect class="sb-glow" x="16" y="16" width="{W - 32}" height="{H - 32}" rx="14"/>'
            f'{screws}<g class="sockets">{sockets}</g><g class="cords">{cords}</g></svg>')


BOARD_CSS = """
.board{display:block;width:100%;height:auto;overflow:hidden;border-radius:4%}
.sb-panel{fill:var(--wine)}
.sb-rim{fill:none;stroke:var(--gold);stroke-width:2}
.sb-glow{fill:var(--gold);opacity:0;transition:opacity 2.4s ease}
.board.is-lit .sb-glow{opacity:.12}
.sb-screw{fill:var(--gold)}
.sb-screw-slot{fill:var(--wine)}
.sb-socket{fill:var(--paper_pink);stroke:var(--ink);stroke-width:3}
.sb-hole{fill:var(--ink)}
.sb-slot{fill:var(--paper_pink)}
.sb-num{font:500 15px var(--f-mono),ui-monospace,monospace;fill:var(--gold);letter-spacing:.08em}
.sb-light{opacity:0;transition:opacity 2.4s ease}
.sb-light circle{fill:var(--gold)}
.sb-light .sb-light-in{fill:var(--paper);opacity:.85}
.sb-light .sb-light-core{fill:var(--paper)}
.socket.lit .sb-light{opacity:1}
.sb-wire{fill:none;stroke:var(--accent);stroke-width:7;stroke-linecap:round}
.sb-ghost{fill:none;stroke:var(--gold);stroke-width:4;stroke-linecap:round;stroke-dasharray:1 13;opacity:0}
.sb-plug{fill:var(--accent);stroke:var(--ink);stroke-width:3}
.sb-collar{fill:var(--gold)}
.sb-grip{fill:var(--ink);opacity:.55}
.sb-prong{fill:var(--gold);stroke:var(--ink);stroke-width:1}
.sb-move{transition:transform 2.2s cubic-bezier(.3,.1,.2,1),opacity 2.6s ease}
.cord.pulling .sb-move{transform:translateY(26px)}
.cord.out .sb-move{transform:translateY(118px);opacity:0}
.cord.out .sb-ghost{animation:dissolve 3.2s ease forwards}
@keyframes dissolve{0%{opacity:0}30%{opacity:.9}100%{opacity:0}}
html.still .cord.out .sb-ghost{animation:none;opacity:.55}
@media (prefers-reduced-motion:reduce){.sb-move,.sb-glow,.sb-light{transition:none}.cord.out .sb-ghost{animation:none;opacity:.5}}
"""

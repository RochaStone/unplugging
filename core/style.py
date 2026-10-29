"""style.json: the one shared Rocha Coded style file.

Adapted from the sibling kit desktop-altar (build.py, MIT), which took it from desktop-core.
Fallback order: --style, then ./style.json, then ~/.rocha-coded/style.json, then the bundled example.
Inheritance rule: a user's own file borrows ONLY missing palette and font entries from the example.
Lines, owner, handle, name, references and notes never fall back to Rocha's.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
STYLE_EXAMPLE = HERE / "examples" / "style.rocha-coded.json"
MOTIFS = ("analog", "cyberpunk", "y2k-blog")
DEFAULT_MOTIF = "analog"
MOTIF_ALIASES = {"guest-check": "analog", "front-page": "analog", "magazine-scrawl": "analog",
                 "pink-paper": "analog", "rotary": "analog", "leopard": "analog", "neutral": "analog",
                 "retro-tv": "cyberpunk", "sticker-collage": "y2k-blog", "y2k": "y2k-blog", "blog": "y2k-blog"}
COLOUR = re.compile(r"^#[0-9A-Fa-f]{6}$")
FONT_NAME = re.compile(r"^[A-Za-z0-9 ]{1,40}$")
HANDLE = re.compile(r"^@?[A-Za-z0-9._]{1,30}$")


def resolve_alias(motif: object) -> str | None:
    raw = str(motif or "").strip().lower()
    raw = MOTIF_ALIASES.get(raw, raw)
    return raw if raw in MOTIFS else None


def find_style(explicit: Path | None = None, cwd: Path | None = None, home: Path | None = None) -> Path:
    """--style, then ./style.json, then ~/.rocha-coded/style.json, then the bundled example."""
    if explicit:
        return Path(explicit)
    for cand in ((cwd or Path.cwd()) / "style.json", (home or Path.home()) / ".rocha-coded" / "style.json"):
        if cand.is_file():
            return cand
    return STYLE_EXAMPLE


def _example() -> dict:
    try:
        return json.loads(STYLE_EXAMPLE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def inherit_style(user: dict) -> dict:
    """Borrow only missing palette and font entries from the bundled example."""
    example = _example()
    merged = dict(user)
    for key in ("palette", "fonts"):
        mine = user.get(key) if isinstance(user.get(key), dict) else {}
        base = example.get(key) if isinstance(example.get(key), dict) else {}
        merged[key] = {**base, **{k: v for k, v in mine.items() if str(v or "").strip()}}
    return merged


def load_style(path: Path | None = None) -> tuple[dict, bool]:
    """Return (style, is_bundled_example)."""
    path = Path(path or STYLE_EXAMPLE)
    bundled = path.resolve() == STYLE_EXAMPLE.resolve()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"Could not read style file {path} ({exc}). Using the bundled example look.", file=sys.stderr)
        data, bundled = _example(), True
    data = data if isinstance(data, dict) else {}
    return (data if bundled else inherit_style(data)), bundled


def page_style(style: dict, is_example: bool) -> dict:
    """Only what the pages use, every colour and font name checked. Bad values borrow the example's.

    The stamp word and handle come from the user's own file only. With the bundled example in use,
    they stay blank, so Rocha's words never land on someone else's release card.
    """
    base = _example()
    pal = style.get("palette") if isinstance(style.get("palette"), dict) else {}
    fonts = style.get("fonts") if isinstance(style.get("fonts"), dict) else {}
    lines = style.get("lines") if isinstance(style.get("lines"), dict) else {}
    good_pal = {k: v.strip().upper() for k, v in pal.items() if isinstance(v, str) and COLOUR.match(v.strip())}
    good_fonts = {k: v.strip() for k, v in fonts.items() if isinstance(v, str) and FONT_NAME.match(v.strip())}
    handle = str(style.get("handle") or "").strip()
    return {
        "palette": {**{k: v.upper() for k, v in base.get("palette", {}).items()}, **good_pal},
        "fonts": {**base.get("fonts", {}), **good_fonts},
        "stamp": "" if is_example else str(lines.get("stamp") or "").strip()[:16],
        "handle": "" if is_example or not HANDLE.match(handle) else handle,
    }


def resolve_motif(cli: str | None, cfg: dict, style: dict, is_example: bool) -> str:
    """--motif, then the config's motif, then the user's own style.json motif, then analog."""
    for cand in (cli, cfg.get("motif"), None if is_example else style.get("motif")):
        m = resolve_alias(cand)
        if m:
            return m
    return DEFAULT_MOTIF

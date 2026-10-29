"""The release card (share and private) and the no-emails drafts.

Share mode is the default card: every person's name is left off. The private card in out/private/ keeps them.
no-emails.md holds drafts in the founder's own words. The kit sends nothing.
"""
from __future__ import annotations

import re
from datetime import datetime
from html import escape

from . import board, frame

KINDS = ("subscription", "tool", "client", "commitment", "habit", "yes")
KIND_LABEL = {"subscription": "subscription", "tool": "tool", "client": "client", "commitment": "commitment",
              "habit": "habit", "yes": "people-pleasing yes"}
GENERIC = {"subscription": "a subscription", "tool": "a tool", "client": "a client", "commitment": "a commitment",
           "habit": "a habit", "yes": "a people-pleasing yes"}
MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
DEFAULT_TITLE = "unplugged"
TITLES = {"the", "mrs", "miss", "mr", "dr", "and", "team"}


def day(dt: datetime) -> str:
    return f"{dt.day:02d} {MONTHS[dt.month - 1]} {dt.year}"


def private_names(cfg: dict) -> list[str]:
    """Every name the share card must leave off: the founder, each item's person and email_to, and the people list."""
    names = [cfg.get("name")]
    names += [str(n) for n in cfg.get("people") or []]
    for it in cfg.get("items") or []:
        names += [it.get("person"), it.get("email_to")]
    out: list[str] = []
    for n in names:
        n = str(n or "").strip()
        if not n:
            continue
        parts = re.split(r"[._+\-\s]+", n.split("@")[0]) if "@" in n else re.split(r"\s+", n)
        if "@" in n:
            parts = [p.capitalize() for p in parts]
        out += [n, *[p for p in parts if len(p) >= 3 and p[:1].isupper() and p.lower() not in TITLES]]
    return sorted(set(out), key=lambda s: (-len(s), s.lower()))


def mentions(text: str, names: list[str]) -> bool:
    low = text.lower()
    return any(re.search(r"(?<![a-z0-9])" + re.escape(n.lower()) + r"(?![a-z0-9])", low) for n in names)


def share_label(item: dict, names: list[str]) -> str:
    kind = item.get("kind") if item.get("kind") in KINDS else "commitment"
    cand = str(item.get("share_as") or "").strip()
    if not cand:
        cand = GENERIC[kind] if item.get("person") or mentions(item.get("what", ""), names) else item.get("what", "")
    return GENERIC[kind] if mentions(cand, names) else cand


CARD_CSS = """
html.card-page body{display:flex;justify-content:center}
html.card-page .stage{padding:0;min-height:0;display:block;width:min(1080px,100vw)}
html.card-page .frame{width:100%;aspect-ratio:1080/1350;container-type:inline-size;transform:none;overflow:hidden}
html.card-page .body{grid-template-columns:1fr;padding:6cqw 6.5cqw 5cqw;gap:2.4cqw;height:100%}
html.card-page .side{display:none}
html.card-page .main{display:flex;flex-direction:column;gap:2.2cqw;height:100%}
.card-kick{display:flex;justify-content:space-between;gap:2cqw;font:500 2.1cqw var(--f-mono),monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--marker)}
.card-title{font-family:var(--f-mast),Georgia,serif;font-weight:900;font-size:12cqw;line-height:.86;margin:0;color:var(--plum);letter-spacing:-.02em;overflow-wrap:anywhere}
.card-sub{font:800 2.7cqw var(--f-label),system-ui,sans-serif;margin:0}
.card-own{font:400 3.4cqw var(--f-scrawl),cursive;color:var(--marker);margin:0}
.card-board{width:66%;align-self:center}
.items{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:1cqw 3cqw;font-size:2.4cqw;line-height:1.2}
.items li{display:flex;gap:1.4cqw;min-width:0}
.items .n{font-family:var(--f-mono),monospace;color:var(--gold);flex:none}
.items .k{display:block;font:800 1.75cqw var(--f-label),system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;opacity:.7}
.items .w{overflow-wrap:anywhere}
.items .why{display:block;font-size:1.9cqw;opacity:.75;font-style:italic}
.window{margin-top:auto;border:.3cqw solid var(--ink);padding:1.6cqw 2.2cqw;display:flex;flex-direction:column;gap:.6cqw;font:500 2.1cqw var(--f-mono),monospace;letter-spacing:.06em}
.window b{font:800 2.6cqw var(--f-label),system-ui,sans-serif;letter-spacing:0;text-transform:lowercase}
.card-foot{display:flex;justify-content:space-between;align-items:center;font:500 1.8cqw var(--f-mono),monospace;letter-spacing:.12em;text-transform:uppercase;opacity:.85}
.card-foot .stamp{font-size:2.6cqw}
.cord.dropped .sb-move{transform:translateY(54px)}
.cord.dropped .sb-ghost{opacity:.7}
html.card-page.m-analog .tape{top:1.4cqw;width:16cqw;height:4cqw}
html.card-page.m-analog .frame{box-shadow:none}
html.card-page.m-cyberpunk .frame{border-radius:0;padding:2.4cqw}
html.card-page.m-cyberpunk .card-title{font-family:var(--f-label),system-ui,sans-serif;font-weight:800;color:var(--accent)}
html.card-page.m-cyberpunk .screen{color:var(--paper)}
html.card-page.m-cyberpunk .window{border-color:var(--accent)}
html.card-page.m-cyberpunk .card-kick{color:var(--accent)}
html.card-page.m-cyberpunk .prompt{padding:2cqw 6.5cqw 0;font-size:2cqw}
html.card-page.m-cyberpunk .body{padding-top:3cqw}
html.card-page.m-y2k-blog .frame{border-width:.3cqw;box-shadow:none}
html.card-page.m-y2k-blog .bar{font-size:2cqw;padding:1.2cqw 2cqw}
html.card-page.m-y2k-blog .btns i{width:2cqw;height:2cqw}
"""


def window_html(win: dict) -> str:
    if win["now"]:
        return (f'<div class="window"><b>the moon is waning. this is the window.</b>'
                f'<span>until the new moon, {day(win["new_local"])}</span></div>')
    return (f'<div class="window"><b>next waning moon</b>'
            f'<span>{day(win["full_local"])} to {day(win["new_local"])}</span></div>')


def card_page(cfg: dict, style: dict, motif: str, win: dict, today: datetime, private: bool,
              art: dict | None = None) -> str:
    items = cfg.get("items") or []
    names = private_names(cfg)
    lines = cfg.get("lines") if isinstance(cfg.get("lines"), dict) else {}
    rows = []
    for i, it in enumerate(items):
        kind = it.get("kind") if it.get("kind") in KINDS else "commitment"
        if private:
            what = str(it.get("what") or "")
            person = str(it.get("person") or "").strip()
            what = f"{what} ({person})" if person and person.lower() not in what.lower() else what
            why = f'<span class="why">{escape(str(it.get("why") or ""))}</span>' if it.get("why") else ""
        else:
            what, why = share_label(it, names), ""
        rows.append(f'<li><span class="n">{i + 1:02d}</span><span class="w"><span class="k">{KIND_LABEL[kind]}</span>'
                    f'{escape(what)}{why}</span></li>')
    title = str(lines.get("card_title") or "").strip() or DEFAULT_TITLE
    own = str(lines.get("intention") or "").strip()
    if not private and mentions(own, names):
        own = ""
    own_html = f'<p class="card-own">{escape(own)}</p>' if own else ""
    states = ["dropped"] * len(items)
    handle = style.get("handle") or ""
    main = (f'<div class="card-kick"><span>release card</span><span>{"private copy" if private else day(today)}</span></div>'
            f'<h1 class="card-title">{escape(title)}</h1>'
            f'<p class="card-sub">what I am unplugging this moon, at the root</p>{own_html}'
            f'<div class="card-board">{board.board(max(len(items), 1), states=states, art=art, label="a switchboard with every cord unplugged")}</div>'
            f'<ol class="items">{"".join(rows)}</ol>'
            f'{window_html(win)}'
            f'<div class="card-foot"><span>{escape(handle) if handle else "unplugging"}</span>'
            f'<span class="stamp">{escape(style.get("stamp") or "")}</span><span>rocha coded</span></div>')
    return frame.page(title="release card" + (" (private)" if private else ""), window="release-card.exe",
                      prompt="unplug:~$ print --card", motif=motif, style=style, main=main, side="",
                      extra_css=CARD_CSS, html_class="card-page")


def no_emails(cfg: dict) -> str:
    """Markdown drafts in the founder's own words. Items without words get a checklist line only."""
    sign = str(cfg.get("name") or "").strip()
    out = ["# Your no emails", "",
           "Every one of these is a draft, written from your own words in the interview.",
           "Sending is yours, when you are ready. Copy one into your email, read it once more, and send it yourself.",
           "This file holds names, so keep it on your computer.", "", "## The list", ""]
    items = cfg.get("items") or []
    for i, it in enumerate(items):
        kind = KIND_LABEL.get(it.get("kind"), "commitment")
        how = f" (cancel at: {it['cancel_at']})" if it.get("cancel_at") else ""
        out.append(f"- [ ] {i + 1:02d} · {kind} · {it.get('what', '')}{how}")
    drafts = [(i, it) for i, it in enumerate(items) if it.get("needs_email")]
    if not drafts:
        out += ["", "Every item this time is a click or a quiet change, with zero emails to write."]
    for i, it in drafts:
        to = str(it.get("email_to") or it.get("person") or "").strip()
        words = str(it.get("words") or "").strip()
        out += ["", f"## {i + 1:02d} · {it.get('what', '')}", "",
                f"**To:** {to or '(add who this goes to)'}  ",
                f"**Subject:** {str(it.get('subject') or '').strip() or '(your words)'}", ""]
        if words:
            greeting = f"Hi {to.split()[0]}," if to and "@" not in to else "Hi,"
            out += ["```text", greeting, "", words, "", sign or "(your name)", "```"]
        else:
            out += ["Your words for this one are still to come. Ask Claude to add them, or write them here."]
    return "\n".join(out) + "\n"

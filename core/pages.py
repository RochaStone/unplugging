"""The guided ritual page (out/ritual.html) and the after page (out/space.html).

ritual.html: one step per screen, her words only, a breath pacer between steps, a soft chime that starts off,
and a switchboard where each step unplugs one cord. The last screen is an empty board filled with light.
It is one self-contained file and works offline (fonts fall back to ones already on the computer).
"""
from __future__ import annotations

import json
from html import escape

from . import board, frame, ritual

PRACTICE_NOTE = "This is a reflective practice, not therapy."


def _line(kind: str, text: str, title: bool) -> str:
    t = escape(text)
    if title:
        return f'<h1 tabindex="-1">{t}</h1>'
    return {"heading": f'<h2 class="h">{t}</h2>', "step": f'<p class="step">{t}</p>',
            "bullet": f'<p class="bullet">{t}</p>', "reflect": f'<p class="reflect">{t}</p>'}.get(kind, f"<p>{t}</p>")


def _screens_html(screens: list[dict]) -> tuple[str, list[int]]:
    """Each screen as an <article>. Returns the html and, for each cord, the index of its step screen."""
    parts, step_at = [], []
    for k, scr in enumerate(screens):
        if scr["kind"] == "step":
            step_at.append(k)
        lines = "".join(_line(kind, text, scr["kind"] == "title") for kind, text in scr["lines"])
        parts.append(f'<article class="scr scr-{scr["kind"]}" data-i="{k}" tabindex="-1"{"" if k == 0 else " hidden"}>'
                     f"{lines}</article>")
    return "".join(parts), step_at


def credit_html() -> str:
    return (f'<footer class="credit"><p>{escape(PRACTICE_NOTE)}</p>'
            f'<p>{escape(ritual.LICENCE_LINE)} '
            f'<a href="{ritual.BOOK_URL}">the book</a></p></footer>')


RITUAL_CSS = """
.main{display:flex;flex-direction:column;gap:clamp(14px,2vw,22px)}
.boardwrap{max-width:560px;width:100%;align-self:center}
.words{min-height:clamp(180px,24vh,280px)}
.scr h1{font-size:clamp(30px,4.4vw,56px)}
.scr h2.h{font-size:clamp(24px,3vw,36px)}
.scr p{font-size:clamp(17px,1.6vw,21px);line-height:1.5;margin:0 0 10px;max-width:62ch}
.scr .step{font-family:var(--f-label),system-ui,sans-serif;font-weight:800;font-size:clamp(19px,1.9vw,24px)}
.scr .bullet{padding-left:4px}
.scr .reflect{font-family:var(--f-mast),Georgia,serif;font-size:clamp(20px,2.2vw,28px);line-height:1.35}
.scr:focus{outline:none}
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.controls button{border:2px solid currentColor;background:transparent;color:inherit;padding:9px 16px;border-radius:999px}
.controls #next{background:var(--plum);border-color:var(--plum);color:var(--paper)}
.controls button:disabled{opacity:.4;cursor:default}
.count{font:500 13px var(--f-mono),monospace;letter-spacing:.1em;margin-left:auto}
.pacer{position:fixed;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px;background:rgba(59,18,48,.9);z-index:5}
.pacer[hidden]{display:none}
.ring{width:min(46vw,240px);aspect-ratio:1;border-radius:50%;border:3px solid var(--gold);background:var(--accent);opacity:.9;transform:scale(.45);animation:breathe 8s ease-in-out forwards}
@keyframes breathe{0%{transform:scale(.45)}50%{transform:scale(1)}100%{transform:scale(.45)}}
.pacer button{border:2px solid var(--gold);background:transparent;color:var(--paper);padding:8px 16px;border-radius:999px}
.m-cyberpunk .controls #next{background:var(--accent);border-color:var(--accent);color:var(--ink)}
@media (prefers-reduced-motion:reduce){.ring{animation:none;transform:scale(.8)}}
"""

RITUAL_JS = r"""
(function () {
  var d = document, $ = function (s) { return d.querySelector(s); };
  var scr = [].slice.call(d.querySelectorAll(".scr")), cords = [].slice.call(d.querySelectorAll(".cord"));
  var socks = [].slice.call(d.querySelectorAll(".socket")), board = $(".board");
  var data = JSON.parse($("#kit-data").textContent), stepAt = data.stepAt;
  var next = $("#next"), back = $("#back"), count = $("#count"), pacer = $(".pacer"), skip = $("#skip");
  var chimeBtn = $("#chime"), chimeOn = false, ctx = null, timer = null;
  var q = location.search, m = /[?&]step=(\d+)/.exec(q), pull = /[?&]pull/.test(q);
  var i = m ? Math.min(scr.length - 1, +m[1]) : 0;
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function show(focus) {
    var last = i === scr.length - 1;
    scr.forEach(function (s, k) { s.hidden = k !== i; });
    cords.forEach(function (c, k) {
      c.classList.toggle("out", i > stepAt[k]);
      c.classList.toggle("pulling", pull && i === stepAt[k]);
    });
    board.classList.toggle("is-lit", last);
    socks.forEach(function (s) { s.classList.toggle("lit", last); });
    count.textContent = pad(i + 1) + " / " + pad(scr.length);
    back.disabled = i === 0;
    next.textContent = last ? "begin again" : "next";
    if (focus) scr[i].focus();
  }
  function chime() {
    try {
      ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
      var t = ctx.currentTime;
      [528, 792].forEach(function (f, n) {
        var o = ctx.createOscillator(), g = ctx.createGain();
        o.type = "sine"; o.frequency.value = f;
        g.gain.setValueAtTime(0, t);
        g.gain.linearRampToValueAtTime(n ? 0.03 : 0.07, t + 0.05);
        g.gain.exponentialRampToValueAtTime(0.0001, t + 2.6);
        o.connect(g); g.connect(ctx.destination); o.start(t); o.stop(t + 2.7);
      });
    } catch (e) {
      chimeBtn.disabled = true;
      chimeBtn.textContent = "chime unavailable here";
    }
  }
  function arrive() {
    clearTimeout(timer); timer = null;
    pacer.hidden = true;
    i += 1; show(true);
    if (chimeOn) chime();
  }
  function forward() {
    if (timer) return;
    if (i === scr.length - 1) { i = 0; show(true); return; }
    pacer.hidden = false;
    var ring = $(".ring"); ring.style.animation = "none"; void ring.offsetWidth; ring.style.animation = "";
    skip.focus();
    timer = setTimeout(arrive, 8000);
  }
  next.addEventListener("click", forward);
  skip.addEventListener("click", arrive);
  back.addEventListener("click", function () { if (i > 0) { i -= 1; show(true); } });
  chimeBtn.addEventListener("click", function () {
    chimeOn = !chimeOn;
    chimeBtn.setAttribute("aria-pressed", chimeOn ? "true" : "false");
    chimeBtn.textContent = chimeOn ? "chime: on" : "chime: off";
    if (chimeOn) chime();
  });
  d.addEventListener("keydown", function (e) {
    if (e.target.tagName === "BUTTON") return;
    if (e.key === "ArrowRight") { e.preventDefault(); if (timer) arrive(); else forward(); }
    if (e.key === "ArrowLeft" && !timer && i > 0) { e.preventDefault(); i -= 1; show(true); }
  });
  show(false);
})();
"""


def ritual_page(style: dict, motif: str, side: str, art: dict | None = None) -> str:
    text = ritual.block()
    if "</script" in text.lower():
        raise SystemExit("ritual/RITUAL.md holds text the page cannot carry safely. Restore the file from the kit.")
    screens = ritual.screens(text)
    body, step_at = _screens_html(screens)
    main = (f'<p class="kicker">unplugging</p>'
            f'<div class="boardwrap">{board.board(len(step_at), art=art, label="a switchboard with cords in their sockets")}</div>'
            f'<div class="words" aria-live="polite">{body}</div>'
            f'<div class="controls"><button id="back" type="button">back</button>'
            f'<button id="next" type="button">next</button>'
            f'<button id="chime" type="button" aria-pressed="false">chime: off</button>'
            f'<span class="count" id="count"></span></div>'
            f'{credit_html()}'
            f'<div class="pacer" hidden><div class="ring" aria-hidden="true"></div>'
            f'<span class="sr">breath pacer, one slow breath</span>'
            f'<button id="skip" type="button">continue</button></div>'
            f'<script type="text/plain" id="ritual-source">{text}</script>')
    return frame.page(title="unplugging · the ritual", window="unplugging.exe", prompt="unplug:~$ ritual --slow",
                      motif=motif, style=style, main=main, side=side, extra_css=RITUAL_CSS, script=RITUAL_JS,
                      data_json=json.dumps({"stepAt": step_at}))


SPACE_CSS = """
.main{display:flex;flex-direction:column;gap:clamp(14px,2vw,24px)}
.boardwrap{max-width:560px;width:100%;align-self:center}
.reflect{font-family:var(--f-mast),Georgia,serif;font-size:clamp(20px,2.2vw,28px);line-height:1.35;margin:0;max-width:60ch}
.blank label{display:block;font:800 13px var(--f-label),system-ui,sans-serif;letter-spacing:.06em;text-transform:lowercase;color:var(--marker);margin-bottom:6px}
.blank textarea{width:100%;min-height:9em;resize:vertical;border:0;border-bottom:2px solid var(--ink);padding:6px 4px;color:var(--ink);
  font:400 22px/32px var(--f-scrawl),cursive;background:transparent repeating-linear-gradient(180deg,transparent 0 31px,var(--accent) 31px 32px)}
.m-cyberpunk .blank textarea{color:var(--paper);border-color:var(--accent);font-family:var(--f-mono),monospace;font-size:18px}
.m-cyberpunk .reflect{color:var(--paper)}
.m-cyberpunk .blank label{color:var(--accent)}
@media print{.side,.credit{display:none}}
"""

SPACE_JS = r"""
(function () {
  var box = document.getElementById("space-for");
  var key = "unplugging:" + location.pathname + ":space";
  var saved = null;
  try { saved = localStorage.getItem(key); } catch (e) { saved = null; }
  if (saved !== null && !/[?&]still/.test(location.search)) box.value = saved;
  box.addEventListener("input", function () {
    try { localStorage.setItem(key, box.value); } catch (e) { box.setAttribute("data-unsaved", "1"); }
  });
})();
"""


def space_page(style: dict, motif: str, side: str, space_for: str, sockets: int, art: dict | None = None) -> str:
    question = ritual.reflection()
    main = (f'<p class="kicker">the empty switchboard</p>'
            f'<div class="boardwrap">{board.board(sockets, art=art, lit=True, label="an empty switchboard filled with light")}</div>'
            f'<p class="reflect">{escape(question)}</p>'
            f'<div class="blank"><label for="space-for">what the space is for now</label>'
            f'<textarea id="space-for" rows="4">{escape(space_for)}</textarea></div>'
            f'{credit_html()}')
    return frame.page(title="unplugging · the space", window="space.exe", prompt="unplug:~$ ls ./space",
                      motif=motif, style=style, main=main, side=side, extra_css=SPACE_CSS, script=SPACE_JS)

#!/usr/bin/env python3
"""unplugging: Rocha's Cord Removal Ritual, then the actual list of what you are unplugging this moon.

  python3 unplug.py                      ask the questions (if there is no unplug.config.json yet), then build
  python3 unplug.py interview            ask the questions one at a time and write unplug.config.json
  python3 unplug.py build                build every page from unplug.config.json
  python3 unplug.py build my.json --out out/ --motif cyberpunk --style path/to/style.json
  python3 unplug.py ritual --out out/    the guided ritual page only, no list needed

Writes into the out folder:
  ritual.html                 the ritual, one step per screen, her words only
  release-card.html / .png    the share card, 1080x1350, with every person's name left off
  private/release-card.html / .png   your full card, names and all
  no-emails.md                a kind draft for each item that needs an email, in your own words
  space.html                  the empty switchboard, her self-reflection question and a blank for what the space is for

Plain Python, standard library only. Everything happens on your computer. The kit sends nothing anywhere.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "scripts"))
from core import board, card, frame, moon, pages, ritual, style as styles  # noqa: E402

CONFIG_NAME = "unplug.config.json"
MAX_ITEMS = board.MAX_SOCKETS
LIMITS = {"what": 80, "person": 60, "share_as": 60, "why": 200, "cancel_at": 200, "email_to": 80,
          "subject": 120, "words": 1200}
QUESTIONS = {
    "subscription": "A subscription you are ready to release? Name it, or press Enter to move on.",
    "tool": "A tool you are ready to stop using? Name it, or press Enter to move on.",
    "client": "A client, or a kind of client, you are ready to release? Describe them, or press Enter to move on.",
    "commitment": "A commitment you are ready to step back from? Name it, or press Enter to move on.",
    "habit": "A habit that drains you? Name it, or press Enter to move on.",
    "yes": "A people-pleasing yes you are ready to take back? Name it, or press Enter to move on.",
}


# ---------- config ----------

def validate_config(cfg: object) -> list[str]:
    """A list of kind, plain-English problems. An empty list means the config is ready to build."""
    if not isinstance(cfg, dict):
        return ["The config should be one { ... } block. Start from unplug.example.json in this folder."]
    errs: list[str] = []

    def text(key: str, val: object, cap: int) -> None:
        if val in (None, ""):
            return
        if not isinstance(val, str):
            errs.append(f'"{key}" should be words in quotes.')
        elif len(val) > cap:
            errs.append(f'"{key}" is {len(val)} characters. Keep it under {cap}.')

    text("name", cfg.get("name"), 60)
    text("space_for", cfg.get("space_for"), 400)
    if cfg.get("motif") not in (None, "") and not styles.resolve_alias(cfg.get("motif")):
        errs.append(f'"motif" should be analog, cyberpunk or y2k-blog. Got: {cfg.get("motif")}')
    lines = cfg.get("lines", {})
    if lines not in (None, "") and not isinstance(lines, dict):
        errs.append('"lines" should be a { } block, like {"card_title": "unplugged"}.')
    elif isinstance(lines, dict):
        text("lines.card_title", lines.get("card_title"), 24)
        text("lines.intention", lines.get("intention"), 120)
    people = cfg.get("people", [])
    if people not in (None, "") and (not isinstance(people, list) or not all(isinstance(p, str) for p in people)):
        errs.append('"people" should be a list of names in quotes, like ["Sam", "Alex"].')
    items = cfg.get("items")
    if not isinstance(items, list) or not items:
        errs.append('"items" should be a list with at least one thing you are unplugging.')
        return errs
    if len(items) > MAX_ITEMS:
        errs.append(f'"items" has {len(items)} things. The switchboard holds {MAX_ITEMS}, so pick the ones that matter most this moon.')
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            errs.append(f'items[{i}] should be a block like {{"kind": "tool", "what": "the app I never open"}}.')
            continue
        if it.get("kind") not in card.KINDS:
            errs.append(f'items[{i}].kind should be one of: {", ".join(card.KINDS)}.')
        if not isinstance(it.get("what"), str) or not it.get("what", "").strip():
            errs.append(f"items[{i}].what should say what it is, in your words.")
        for key, cap in LIMITS.items():
            text(f"items[{i}].{key}", it.get(key), cap)
        if "needs_email" in it and not isinstance(it["needs_email"], bool):
            errs.append(f"items[{i}].needs_email should be true or false, with no quotes.")
    return errs


def load_config(path: Path) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"I could not find {path}. Run `python3 unplug.py interview` first, "
                         "or copy unplug.example.json to unplug.config.json.")
    except OSError as exc:
        raise SystemExit(f"Could not open {path}. Check the file name and try again. ({exc.strerror})")
    except ValueError as exc:
        raise SystemExit(f"{path} is not valid JSON yet. Look near line {getattr(exc, 'lineno', '?')}: "
                         "a missing comma or quote is the usual reason.")


# ---------- the interview (plain CLI; SKILL.md runs the same questions through Claude) ----------

def _yes(answer: str) -> bool:
    return answer.strip().lower() in ("y", "yes", "yeah", "yep", "please", "sure")


def interview(ask: Callable[[str], str], say: Callable[[str], None] = print) -> dict:
    """One question at a time. Every answer is kept exactly as typed."""
    say("Hello. We are going to make your list of what you are unplugging this moon.")
    say("One question at a time. Press Enter to skip any of them.")
    cfg: dict = {"name": ask("What name would you like on your email drafts? (it stays private)").strip(), "items": []}
    for kind, question in QUESTIONS.items():
        while len(cfg["items"]) < MAX_ITEMS:
            what = ask(question).strip()[:LIMITS["what"]]
            if not what:
                break
            item: dict = {"kind": kind, "what": what}
            say(f"Got it: {what}.")
            if kind in ("client", "commitment", "yes"):
                person = ask("Is there a person's name attached? It stays off your share card. (Enter to skip)").strip()
                if person:
                    item["person"] = person[:LIMITS["person"]]
            if kind in ("subscription", "tool"):
                where = ask("Where do you cancel it? A website, a settings page or an email. (Enter to skip)").strip()
                if where:
                    item["cancel_at"] = where[:LIMITS["cancel_at"]]
            why = ask("In a few words, why is it time? (Enter to skip)").strip()
            if why:
                item["why"] = why[:LIMITS["why"]]
            item["needs_email"] = _yes(ask("Does this one need an email? (yes or no)"))
            if item["needs_email"]:
                to = ask("Who does it go to? A name or an email address. (Enter to fill in later)").strip()
                if to:
                    item["email_to"] = to[:LIMITS["email_to"]]
                subject = ask("A subject line, in your words? (Enter to leave it blank)").strip()
                if subject:
                    item["subject"] = subject[:LIMITS["subject"]]
                words = ask("Say the no the way you would say it, in a sentence or two. Kind and clear is plenty.").strip()
                if words:
                    item["words"] = words[:LIMITS["words"]]
            cfg["items"].append(item)
            question = "Another one? Name it, or press Enter to move on."
    space = ask("Last one. What is the space for, once these are unplugged? (Enter to leave it for later)").strip()
    if space:
        cfg["space_for"] = space[:400]
    return cfg


def write_config(cfg: dict, path: Path) -> None:
    Path(path).write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ---------- build ----------

def moon_info(now: datetime) -> dict:
    win = moon.waning_window(now)
    local = now.tzinfo or timezone.utc
    win["full_local"], win["new_local"] = win["full"].astimezone(local), win["new"].astimezone(local)
    age = moon.moon_age(now)
    win["age"], win["phase"] = age, moon.phase_name(age)
    return win


def build(cfg: dict | None, out: Path, motif: str | None = None, style_path: Path | None = None,
          now: datetime | None = None, png: bool = True, workdir: Path | None = None, ritual_only: bool = False,
          home: Path | None = None) -> list[str]:
    """Render every page. Returns lines to tell the founder what was made."""
    cfg = cfg or {}
    style_raw, is_example = styles.load_style(styles.find_style(style_path, cwd=workdir, home=home))
    style = styles.page_style(style_raw, is_example)
    motif = styles.resolve_motif(motif, cfg, style_raw, is_example)
    now = now or datetime.now().astimezone()
    win = moon_info(now)
    art = board.find_art((workdir or Path.cwd()) / "objects" / "mine")
    today = card.day(now)
    about = str(cfg.get("name") or "").strip() or "unplugging"
    side = frame.sidebar(today, win["phase"], win["age"], about, "unplugging", style["stamp"])
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    made = []
    (out / "ritual.html").write_text(pages.ritual_page(style, motif, side, art), encoding="utf-8")
    made.append("ritual.html")
    if not ritual_only:
        n = len(cfg.get("items") or []) or ritual.step_count()
        lit_side = frame.sidebar(today, win["phase"], win["age"], about, "lit", style["stamp"])
        (out / "space.html").write_text(pages.space_page(style, motif, lit_side, str(cfg.get("space_for") or ""), n, art),
                                        encoding="utf-8")
        (out / "release-card.html").write_text(card.card_page(cfg, style, motif, win, now, False, art), encoding="utf-8")
        (out / "private").mkdir(exist_ok=True)
        (out / "private" / "release-card.html").write_text(card.card_page(cfg, style, motif, win, now, True, art),
                                                           encoding="utf-8")
        (out / "no-emails.md").write_text(card.no_emails(cfg), encoding="utf-8")
        made += ["release-card.html", "private/release-card.html", "no-emails.md", "space.html"]
        if png:
            import render
            for page in (out / "release-card.html", out / "private" / "release-card.html"):
                ok, msg = render.screenshot(page.resolve().as_uri() + "?still", page.with_suffix(".png"), 1080, 1350)
                if not ok:
                    made.append(msg)
                    break
                made.append(str(page.with_suffix(".png").relative_to(out)))
    made.append(f"motif: {motif}")
    made.append("the moon is waning: this is the window" if win["now"]
                else f"next waning moon: {card.day(win['full_local'])} to {card.day(win['new_local'])}")
    return made


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Unplug what drains you, at the root. Her ritual, then the actual list.")
    ap.add_argument("command", nargs="?", default="auto", choices=("auto", "interview", "build", "ritual"))
    ap.add_argument("config", nargs="?", default=CONFIG_NAME, help="your unplug.config.json")
    ap.add_argument("--out", default="out", help="the folder for your pages (default: out)")
    ap.add_argument("--motif", choices=styles.MOTIFS, help="analog, cyberpunk or y2k-blog")
    ap.add_argument("--style", type=Path, help="a style.json somewhere else")
    ap.add_argument("--today", help="pretend today is YYYY-MM-DD (for the moon window)")
    ap.add_argument("--no-png", action="store_true", help="skip the PNG pictures")
    args = ap.parse_args(argv)
    now = None
    if args.today:
        try:
            now = datetime.strptime(args.today, "%Y-%m-%d").replace(hour=12, tzinfo=timezone.utc)
        except ValueError:
            raise SystemExit("--today should look like 2026-11-02.")
    config = Path(args.config)
    if args.command == "ritual":
        build(None, Path(args.out), args.motif, args.style, now, png=False, ritual_only=True)
        print(f"READY. Your ritual is in {args.out}/ritual.html")
        return 0
    if args.command == "interview" or (args.command == "auto" and not config.exists()):
        cfg = interview(lambda q: input(q + "\n> "))
        if not cfg["items"]:
            print("Your list is empty for now, and that is fine. Run this again whenever you are ready.")
            return 0
        write_config(cfg, config)
        print(f"Saved your answers to {config}.")
        if args.command == "interview":
            return 0
    cfg = load_config(config)
    errs = validate_config(cfg)
    if errs:
        print("A few things to fix in your config first:")
        for e in errs:
            print(f"  - {e}")
        return 1
    made = build(cfg, Path(args.out), args.motif, args.style, now, png=not args.no_png)
    print(f"READY. Your pages are in {args.out}/")
    for m in made:
        print(f"  {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

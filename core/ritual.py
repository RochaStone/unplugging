"""Read Rocha's ritual from ritual/RITUAL.md and split it into screens, one step per screen.

The text between the ritual:start and ritual:end markers is used exactly as written.
Headings lose their ** marks on screen; every other character stays as she wrote it.
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
RITUAL_MD = HERE / "ritual" / "RITUAL.md"
LICENCE_LINE = "Ritual text © Rochelle Livingstone, from Thriving in Transformational Times, all rights reserved."
BOOK_URL = "https://www.amazon.com/dp/B0DXNR3BNJ"
BOOK_TITLE = "Thriving in Transformational Times"
START, END = "<!-- ritual:start -->\n", "\n<!-- ritual:end -->"
STEP = re.compile(r"^\d\.? ")
BOLD = re.compile(r"^\*\*(.+)\*\*$")


def block(path: Path = RITUAL_MD) -> str:
    """The ritual text exactly as it sits between the markers."""
    raw = Path(path).read_text(encoding="utf-8")
    try:
        a = raw.index(START) + len(START)
        b = raw.index(END, a)
    except ValueError as exc:
        raise SystemExit(f"{path} is missing its ritual:start or ritual:end marker. Restore the file from the kit.") from exc
    return raw[a:b]


def shown(line: str) -> tuple[str, str]:
    """(kind, text) for one line of the ritual: heading, step, bullet, reflect or para."""
    m = BOLD.match(line)
    if m:
        return "heading", m.group(1)
    if STEP.match(line):
        return "step", line
    if line.startswith("• "):
        return "bullet", line
    if line.startswith("Self-reflection:"):
        return "reflect", line
    return "para", line


def screens(text: str | None = None) -> list[dict]:
    """Split the ritual into screens.

    The title, then each **heading** section, then each numbered step with its bullets, then the reflection.
    A heading that sits right before step 1 joins step 1's screen. Each screen lists (kind, text) pairs.
    """
    text = block() if text is None else text
    out: list[dict] = []
    pending: list[tuple[str, str]] = []
    for line in text.split("\n"):
        if not line.strip():
            continue
        kind, shown_text = shown(line)
        starts_new = kind in ("heading", "step", "reflect") or not out
        if kind == "heading" and not out:
            out.append({"kind": "title", "lines": [(kind, shown_text)]})
            continue
        if kind == "heading":
            pending = [(kind, shown_text)]
            out.append({"kind": "section", "lines": list(pending)})
            continue
        if kind == "step":
            prev = out[-1] if out else None
            if prev and prev["kind"] == "section" and len(prev["lines"]) == 1:
                out.pop()
                out.append({"kind": "step", "lines": [*prev["lines"], (kind, shown_text)]})
            else:
                out.append({"kind": "step", "lines": [(kind, shown_text)]})
            continue
        if kind == "reflect":
            out.append({"kind": "reflect", "lines": [(kind, shown_text)]})
            continue
        if starts_new:
            out.append({"kind": "section", "lines": [(kind, shown_text)]})
        else:
            out[-1]["lines"].append((kind, shown_text))
    return out


def reflection(text: str | None = None) -> str:
    """Her self-reflection question, exactly as written."""
    for scr in screens(text):
        if scr["kind"] == "reflect":
            return scr["lines"][0][1]
    raise SystemExit("The self-reflection line is missing from ritual/RITUAL.md. Restore the file from the kit.")


def step_count(text: str | None = None) -> int:
    return sum(1 for s in screens(text) if s["kind"] == "step")

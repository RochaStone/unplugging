# Testing

Everything below was run on 29 Oct 2026, on macOS with Python 3.12.8 and Google Chrome installed.

## 1. Tests
```sh
python3 -m unittest discover -s tests -v
```
Result: **30 tests, all OK** (about two minutes, most of it headless Chrome). They cover:
- **The ritual text:** the copy embedded in `ritual.html` matches the text between the markers in `ritual/RITUAL.md` byte for byte; every line on every screen is one of her lines (headings lose only their `**` marks) and every line of hers appears, in order; the text has no em dash; six numbered steps make six cords; the reflection is the last screen; the page loads no outside script and links only to Google Fonts and the book.
- **The interview:** scripted answers produce a config that passes `validate_config`, keeps her email sentence exactly as typed, and survives a save and reload; each question asks one thing; a wrong kind, `needs_email` as a word and an unknown motif are each named in plain words; thirteen items and an empty list are refused.
- **The share card:** with the sample founder, every name on the private list (the founder, each person, each email recipient, the `people` list, and the first and last names on their own) is absent from the share card, matched as whole words, and present on the private card. A name hidden inside an item, inside `share_as`, inside an email address and inside `lines.intention` stays off the share card too.
- **The no-emails drafts:** each draft holds her words exactly, items without an email get a checklist line only, and the file says every one is a draft.
- **The moon window:** inside a waning stretch (20 Jan 2025) the window is the full moon of 13 Jan 2025 22:27 UTC to the new moon of 29 Jan 2025 12:36 UTC; while waxing (10 Apr 2024) it points ahead to 23 Apr 2024 23:49 UTC to 8 May 2024 03:22 UTC. Both land within ten minutes of NASA's phase tables. The card says "this is the window" only when the moon is waning, shows the dates otherwise, and makes no claim about when the ritual works.
- **Style and the inheritance rule:** the fallback order (./style.json, then ~/.rocha-coded/style.json, then the bundled example); a user style borrows only missing palette and font entries; her motif is used when the config has none; with the bundled example on a founder's card, Rocha's handle and stamp stay off; a founder's own handle and stamp appear; a plug drawing in `objects/mine` replaces the drawn plug.
- **Wording:** every shipped text file and every generated page is free of the banned words listed in `BANNED` in `tests/test_core.py` and of em dashes; README, SKILL, STYLE, the ritual licence and the objects readme have no sentence opening on a negative; no cutting imagery outside her own sentence ("not cutting them"); the Python makes no network calls.
- **Licence:** the line "Ritual text © Rochelle Livingstone, from Thriving in Transformational Times, all rights reserved." is at the top of `ritual/RITUAL.md`, in `LICENSE-RITUAL.md`, in the README Credits next to the book link, and on the ritual and space pages beside "This is a reflective practice, not therapy."
- **Files:** every Python, Markdown and JSON file is under 500 lines; `examples/style.rocha-coded.json` is identical to desktop-altar's.
- **Headless render, all three motifs:** `ritual.html`, `release-card.html` and `space.html` in analog, cyberpunk and y2k-blog, each at 1600x900 and at 430 wide (18 combinations). Each page reports its motif, has no sideways scroll, keeps its frame inside the screen, and keeps its signature (analog: the washi tape; cyberpunk: the prompt line; y2k-blog: the title bar). The ritual starts with her title and six cords in; at screen 8 four cords are out; on the last screen all six are out and the board is lit with the reflection showing. The space page is lit with zero cords and her question. Both PNG cards are exactly 1080x1350.

## 2. Looked at by eye
The three cards, the ritual page at step 4, the space page, the README hero and the triptych were rendered and checked by eye at full size, and the ritual, card and space pages side by side at 430 wide.
Caught that way and fixed: the "dropped" plug state was filtered out so the card showed plugs still seated; cords from the top row crossed the sockets below (rows are now staggered); socket numbers sat under the plugs; the card footer ran off the bottom; the space page credit lost its styling.
Caught by the tests and fixed: the name filter split "the breakfast organiser" into common words and hid every item; one banned word in the README Credits.

## 3. What was not verified
- The chime and the breath pacer were not heard or watched live. The chime uses the browser's Web Audio and only plays after a click; the pacer is a CSS animation. The tests check the controls exist and the chime starts off.
- The plain CLI interview was run once end to end with piped answers (two items, one email draft), not typed by a person.
- `SKILL.md` was not run inside Claude Code or Cowork in this session.
- The ritual text was taken from the research transcript of her book (`_curation/research/book-rituals.md`), which notes one em dash after "at the root" shown as a spaced hyphen. The printed book was not checked directly.
- Windows and Linux: the kit uses only the standard library and looks for Chrome in the usual places, and was run on macOS only.

# style.json

One file holds your look. Every Rocha Coded tool reads the same file, so you make it once.

## Where it goes
The tool looks in this order and uses the first one it finds:
1. `--style path/to/style.json`, if you give one
2. `style.json` in the folder you are working in (your Cowork folder, or wherever you run Claude Code)
3. `~/.rocha-coded/style.json`, to use one look across every project
4. `examples/style.rocha-coded.json`, the bundled example (Rocha's look)

Start from `style.example.json`: copy it to `style.json` and fill it in. Or ask Claude to make one with you.

Your words live somewhere else. Your list, your "no" sentences and your card title live in `unplug.config.json`.
`style.json` is colour, type, motif and one stamp word.

## The keys
| Key | What to put there | Used by this tool |
|---|---|---|
| `name`, `owner` | your brand and your name | kept for other tools (your name on the drafts comes from `unplug.config.json`) |
| `handle` | your handle, like `@yourname` | the foot of your release card |
| `site` | your site | kept for other tools |
| `palette.hero` | your ground colour, the deep one, as a hex code like `#50163C` | kept for other tools |
| `palette.plum` | a deep shade | big titles, the y2k title bar, the next button |
| `palette.wine` | a second deep colour | the switchboard panel, the cyberdeck bezel |
| `palette.accent` | your one bright accent | the plugs and cords, washi tape, the blinking cursor, the breath circle |
| `palette.paper` | a light paper colour | the y2k window, the light in the sockets |
| `palette.paper_pink` | a second paper colour | the analog sheet, the y2k wallpaper, the socket faces |
| `palette.ink` | your line colour | text, outlines, the socket holes |
| `palette.marker` | the colour of a pen mark | kickers, the date stamp, your stamp word |
| `palette.gold` | a highlight colour | screws, socket numbers, the light on the empty board, the cords dissolving into light |
| `palette.cool` | one cool accent | kept for other tools |
| `fonts.masthead` | a big display font from Google Fonts | the card title, the ritual title and headings |
| `fonts.label` | a font for labels | steps, buttons, kickers |
| `fonts.body` | a reading font | the ritual text |
| `fonts.scrawl` | a handwriting or marker font | your stamp word, the blank on the space page, your line on the card |
| `fonts.script` | a signature script font | loaded, kept for other tools |
| `fonts.mono` | a typewriter font | dates, numbers, the moon, the terminal |
| `motif` | `analog`, `cyberpunk` or `y2k-blog` (older names like `guest-check` or `retro-tv` still work) | yes, when `unplug.config.json` has no motif of its own |
| `lines.stamp` | one short word of yours | a stamp on your card and in the sidebar |
| `lines.*` (the rest) | more of your own lines | kept for other tools |
| `references`, `notes` | 3 to 5 images or links, and your look in a sentence | Claude reads these when it makes your style with you |

## Which motif wins
`--motif` on the command line, then `motif` in `unplug.config.json`, then `motif` in your own `style.json`, then `analog`.

## Good to know
- Colours must be hex codes (`#RRGGBB`). Anything else is skipped and the bundled colour is used for that slot.
- Fonts are Google Fonts names, letters, numbers and spaces only. Offline, the pages use a similar font already on the computer.
- Any colour or font you leave empty borrows the bundled example's, so every page looks finished.
- Your words stay yours. Your handle and stamp come from your own `style.json` only. With the bundled example in use, your card carries neither, so Rocha's handle and stamp stay on her things.

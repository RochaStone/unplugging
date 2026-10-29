"""Headless Chrome tools for unplugging: screenshots and a true-size overflow check.

Copied from the sibling kit desktop-altar (scripts/render.py, MIT), which took it from desktop-core.

Chrome on macOS will not shrink a headless window under 500px, so phone widths are measured inside an
iframe of the exact width. The page reports its own scrollWidth from inside that frame.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path


def find_chrome() -> str | None:
    env = os.environ.get("CHROME_PATH")
    if env and Path(env).exists():
        return env
    for cmd in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "microsoft-edge"):
        p = shutil.which(cmd)
        if p:
            return p
    for p in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium",
              "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
        if Path(p).exists():
            return p
    return None


NO_CHROME = ("Chrome or Chromium is missing on this computer, so the PNG pictures are skipped this time. "
             "Your HTML pages are ready and open in any browser. Install Chrome, or set CHROME_PATH, then build again.")


def png_size(path: Path) -> tuple[int, int]:
    head = Path(path).read_bytes()[:24]
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    return struct.unpack(">II", head[16:24])


def _run(args: list[str], width: int, height: int, budget: int = 6000) -> subprocess.CompletedProcess | None:
    chrome = find_chrome()
    if not chrome:
        return None
    with tempfile.TemporaryDirectory() as profile:
        cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
               "--no-default-browser-check", "--allow-file-access-from-files", f"--user-data-dir={profile}",
               f"--window-size={width},{height}", "--force-device-scale-factor=1",
               f"--virtual-time-budget={budget}", *args]
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            cmd.insert(1, "--no-sandbox")
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return None


def screenshot(url: str, png: Path, width: int, height: int) -> tuple[bool, str]:
    res = _run([f"--screenshot={png}", url], width, height)
    if res is None:
        return False, NO_CHROME
    if not Path(png).exists():
        return False, "Chrome ran but wrote no picture."
    w, h = png_size(png)
    return True, f"{png} ({w}x{h})"


HARNESS = """<!doctype html><html><body style="margin:0"><iframe id="f" src="{src}" style="width:{w}px;height:{h}px;border:0"></iframe>
<pre id="r">pending</pre><script>
document.getElementById("f").onload = function () {{
  var fr = this;
  setTimeout(function () {{
    var out = document.getElementById("r");
    try {{
      var d = fr.contentDocument, de = d.documentElement, vis = function (sel) {{
        var n = d.querySelector(sel); return !!n && getComputedStyle(n).display !== "none"; }};
      var shown = [].slice.call(d.querySelectorAll(".scr:not([hidden])")).map(function (s) {{ return s.innerText; }});
      out.textContent = JSON.stringify({{iw: fr.contentWindow.innerWidth, sw: de.scrollWidth, sh: de.scrollHeight,
        cls: de.className, text: d.body.innerText.slice(0, 6000), shown: shown,
        cords: d.querySelectorAll(".cord").length, out: d.querySelectorAll(".cord.out").length,
        lit: !!d.querySelector(".board.is-lit"), tape: vis(".tape"), prompt: vis(".prompt"), counter: vis(".counter"), bar: vis(".bar"),
        frameRight: d.querySelector(".frame").getBoundingClientRect().right}});
    }} catch (e) {{ out.textContent = JSON.stringify({{error: e.message}}); }}
  }}, 1200);
}};
</script></body></html>"""


def measure(page: Path, width: int, height: int = 900, query: str = "") -> dict:
    """Load the page inside an iframe exactly `width` wide and return what it reports about itself."""
    page = Path(page).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        harness = Path(tmp) / "harness.html"
        harness.write_text(HARNESS.format(src=page.as_uri() + query, w=width, h=height), encoding="utf-8")
        res = _run(["--dump-dom", harness.as_uri()], max(width, 800), height + 200, budget=8000)
    if res is None:
        return {"error": NO_CHROME}
    m = re.search(r'<pre id="r">(.*?)</pre>', res.stdout, re.S)
    if not m:
        return {"error": "Chrome gave no report."}
    raw = m.group(1).replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&amp;", "&")
    try:
        return json.loads(raw)
    except ValueError:
        return {"error": "report was " + raw[:80]}

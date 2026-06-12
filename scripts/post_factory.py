#!/usr/bin/env python3
"""
post_factory.py — generate branded social posts in one command, with Photopea.

Formats: square (1080×1080, IG feed), story (1080×1920, IG/FB/TikTok), banner
(1200×630, OG/Twitter/blog). One brand theme, one type ramp, consistent output.

    python post_factory.py square  "EYEBROW" "Headline" "Accent line" "Subtitle" "CTA" "@handle"  out.png
    python post_factory.py story   ...same args...                                                  out.png
    python post_factory.py banner  "EYEBROW" "Headline" "Accent line" ""        ""    ""           out.png

Free, no Photoshop, no API key. Node + the Photopea MCP only. Edit THEME to rebrand.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from photopea import Photopea, gradient_bg, text, rect, export  # noqa: E402

# ── brand theme (edit these to rebrand everything) ───────────────────────────
THEME = {
    "bg1":   "#16182e",   # gradient start (dark)
    "bg2":   "#283276",   # gradient end
    "accent": "#f5d76e",  # one accent color
    "ink":   "#ffffff",   # primary text
    "mute":  "#c9cde0",   # secondary text
    "angle": 120,
}

FORMATS = {
    "square": (1080, 1080),
    "story":  (1080, 1920),
    "banner": (1200, 630),
}


def arg(i, default=""):
    return sys.argv[i] if len(sys.argv) > i else default


def compose(pp: Photopea, fmt: str, eyebrow, headline, accent_line, subtitle, cta, handle):
    w, h = FORMATS[fmt]
    t = THEME
    gradient_bg(pp, w, h, t["bg1"], t["bg2"], angle=t["angle"], name=f"{fmt} post")

    # vertical rhythm scales a little by format
    pad = 90 if w >= 1080 else 120
    if fmt == "banner":
        hero, sub = 92, 40
        y = 150
        rect(pp, pad, y, 110, 12, t["accent"]); y += 55
        if eyebrow: text(pp, eyebrow, pad, y, 28, t["accent"], bold=True, letterSpacing=4); y += 90
        if headline: text(pp, headline, pad - 2, y, hero, t["ink"], bold=True); y += hero + 10
        if accent_line: text(pp, accent_line, pad - 2, y, hero, t["accent"], bold=True)
    else:
        hero = 84 if fmt == "square" else 92
        y = 150 if fmt == "square" else 320
        rect(pp, pad, y, 120, 12, t["accent"]); y += 55
        if eyebrow: text(pp, eyebrow, pad, y, 30, t["accent"], bold=True, letterSpacing=4); y += 115
        if headline: text(pp, headline, pad - 2, y, hero, t["ink"], bold=True); y += hero + 16
        if accent_line: text(pp, accent_line, pad - 2, y, hero, t["accent"], bold=True); y += hero + 60
        if subtitle: text(pp, subtitle, pad + 2, y, 36, t["mute"]); y += 120
        if cta:
            btn_y = (740 if fmt == "square" else 1500)
            rect(pp, pad, btn_y, 380, 92, t["accent"])
            text(pp, cta, pad + 30, btn_y + 30, 38, t["bg1"], bold=True)
        if handle:
            text(pp, handle, pad, (1005 if fmt == "square" else 1820), 32, "#8b90b0", bold=True)


def main() -> int:
    fmt = arg(1, "square")
    if fmt not in FORMATS:
        print(f"format must be one of {list(FORMATS)}"); return 1
    eyebrow, headline, accent_line = arg(2, "DESIGN, AS CODE"), arg(3, "Ship your visuals"), arg(4, "in one command.")
    subtitle, cta, handle = arg(5, "Branded. Free. No Photoshop."), arg(6, "Get started"), arg(7, "@yourbrand")
    out = arg(8, f"{fmt}.png")

    with Photopea() as pp:
        compose(pp, fmt, eyebrow, headline, accent_line, subtitle, cta, handle)
        export(pp, out, "png")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

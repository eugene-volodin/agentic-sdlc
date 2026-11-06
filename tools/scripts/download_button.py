"""The download button of the repository's README: a small illustrated scene in the book's style, one SVG.

The plate is a sticker in the cover's colours with an ink outline and an offset ink shadow; on it the handbook in a
three-quarter view, a download arrow dipping into a tray, the headline and a smaller line, the agent presenting
them and the sparrow flying in. Every letter is a path cut from the book's own fonts, the characters come from
`bookkit.art.characters`, and a short SMIL loop (the arrow, the sparrow, a shine) plays where the SVG is shown as an
image. Without the loop the picture is complete as it stands.

The words are given on the command line (code stays free of the book's language); the command that made the
committed file is written into a comment at its top. Run from `tools/`:

    uv run python scripts/download_button.py HEADLINE SUBLINE [--out PATH] [--png DIR]

`--png` also renders previews at 1x and 2x on a white and on a dark page, in the build's browser (Playwright's
Chromium).
"""
from __future__ import annotations

import argparse
import shlex
import sys
from functools import cache
from html import escape
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

from bookkit import design as P
from bookkit.art import characters as C
from bookkit.art.ink import Canvas, n, rounded_rect_d
from bookkit.fonts import FONTS, static_weight

TOOLS = Path(__file__).resolve().parent.parent
OUT = TOOLS.parent / "docs" / "images" / "download.svg"

W, H = 840, 224                 # the view box
PLATE = (6, 6, 816, 200, 32)    # x, y, w, h, corner radius
SHADOW = 9                      # the offset ink shadow
LINE = 5                        # the plate's outline
GROUND = 186                    # where the feet stand

DARK_PAGE = "#0d1117"           # the dark page a preview is shown on (not a book colour)


# ---------------------------------------------------------------------------------------------------- lettering
@cache
def _face(file: str, weight: int):
    path = FONTS / file
    font = TTFont(static_weight(path, weight) if "fvar" in TTFont(path, lazy=True) else path)
    return font.getGlyphSet(), font.getBestCmap(), font["hmtx"].metrics, float(font["head"].unitsPerEm)


def _run(text: str, size: float, file: str, weight: int, track: float) -> tuple[list, float]:
    """Each glyph's name and pen offset, and the run's advance."""
    _, cmap, metrics, upm = _face(file, weight)
    out, x = [], 0.0
    for ch in text:
        name = cmap.get(ord(ch)) or cmap[ord("?")]
        out.append((name, x))
        x += metrics[name][0] / upm * size + track * size
    return out, x - track * size


def text_path(text: str, x: float, y: float, size: float, file: str = "Rubik.ttf", weight: int = 900,
              track: float = -0.01) -> tuple[str, tuple[float, float, float, float]]:
    """The run as one path with its start on the baseline at (x, y), and its ink box (x0, y0, x1, y1)."""
    glyphs, _, _, upm = _face(file, weight)
    pen, box = SVGPathPen(glyphs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip(".")), BoundsPen(glyphs)
    s = size / upm
    run, _ = _run(text, size, file, weight, track)
    for name, dx in run:
        glyphs[name].draw(TransformPen(pen, (s, 0, 0, -s, x + dx, y)))
        glyphs[name].draw(TransformPen(box, (s, 0, 0, -s, x + dx, y)))
    return pen.getCommands(), box.bounds


def advance(text: str, size: float, file: str = "Rubik.ttf", weight: int = 900, track: float = -0.01) -> float:
    return _run(text, size, file, weight, track)[1]


def balloon(d: str, size: float, face: str = P.WHITE) -> str:
    """Letters as on the cover: a light face, an ink rim and an ink extrusion down and to the right."""
    rim, deep = size * 0.075, size * 0.085
    return (f'<path d="{d}" fill="{P.INK}" stroke="{P.INK}" stroke-width="{n(2 * rim)}" stroke-linejoin="round" '
            f'transform="translate({n(deep)} {n(deep)})"/>'
            f'<path d="{d}" fill="{face}" stroke="{P.INK}" stroke-width="{n(2 * rim)}" stroke-linejoin="round" '
            f'paint-order="stroke"/>')


# ---------------------------------------------------------------------------------------------------- pieces
def plate(c: Canvas) -> str:
    """The sticker: shadow, the cover's yellow, a meadow along the foot; returns the plate's clip id."""
    x, y, w, h, r = PLATE
    d = rounded_rect_d(x, y, w, h, r)
    c.path(rounded_rect_d(x + SHADOW, y + SHADOW, w, h, r), P.INK, sw=0)
    fill = c.gradient([(0, P.mix(P.YELLOW, P.WHITE, 0.2)), (0.62, P.YELLOW),
                       (1, P.mix(P.YELLOW, P.ORANGE, 0.22))], 0, y, 0, y + h)
    clip = c.shape(d, fill, sw=0, light=None, clip=True)
    # a soft sunlit halo behind the book, flat circles of falling opacity (no blur, no mask)
    halo = "".join(f'<circle cx="112" cy="104" r="{r_}" fill="{P.WHITE}" fill-opacity=".09"/>'
                   for r_ in (96, 80, 64))
    hill = (f"M{x - 4},{GROUND - 4} C120,{GROUND - 14} 230,{GROUND + 2} 340,{GROUND - 3} "
            f"S560,{GROUND - 12} 660,{GROUND - 6} S800,{GROUND - 12} {x + w + 4},{GROUND - 6} "
            f"V{y + h + 4} H{x - 4} Z")
    back = (f"M{x - 4},{GROUND - 12} C90,{GROUND - 30} 200,{GROUND - 26} 300,{GROUND - 18} "
            f"S520,{GROUND - 34} 640,{GROUND - 24} S780,{GROUND - 34} {x + w + 4},{GROUND - 26} "
            f"V{y + h + 4} H{x - 4} Z")
    c.add(f'<g clip-path="url(#{clip})">{halo}'
          f'<path d="{back}" fill="{P.GRASS}" stroke="{P.INK}" stroke-width="2.4" stroke-linejoin="round"/>'
          f'<path d="{hill}" fill="{P.LEAF_LIGHT}" stroke="{P.INK}" stroke-width="3" stroke-linejoin="round"/></g>')
    return clip


def outline_plate(c: Canvas) -> None:
    x, y, w, h, r = PLATE
    c.path(rounded_rect_d(x, y, w, h, r), "none", sw=LINE)


def handbook(c: Canvas) -> None:
    """The handbook standing on the grass in a three-quarter view: the cover in the cover's colours, the page
    block showing along the right and the foot, a hinge line by the spine."""
    cw, ch = 104, 142                       # the cover, flat
    dx, dy = 11, 7                          # the depth of the book
    cover = Canvas()
    face = rounded_rect_d(0, 0, cw, ch, 6)
    # the page block behind the cover
    cover.shape(f"M{cw - 6},0 L{cw + dx - 6},{dy} Q{cw + dx},{dy} {cw + dx},{dy + 6} L{cw + dx},{ch + dy - 6} "
                f"Q{cw + dx},{ch + dy} {cw + dx - 6},{ch + dy} L6,{ch + dy} L0,{ch} Z", P.CARD, sw=2.6,
                light=None)
    cover.line(f"M{cw + 4},8 V{ch + 1} M{cw + 8},11 V{ch + 3} M12,{ch + 3} H{cw + 2}", 1.2,
               P.mix(P.INK, P.CARD, 0.5))
    clip = cover.shape(face, P.YELLOW, sw=0, light=None, clip=True)
    top = rounded_rect_d(-2, -2, cw + 4, 24, 0)
    foot = f"M-2,{ch - 18} H{cw + 2} V{ch + 2} H-2 Z"
    stickers = "".join(
        f'<path d="{rounded_rect_d(sx, 7, 15, 8, 4)}" fill="{col}" stroke="{P.INK}" stroke-width="1.2"/>'
        for sx, col in ((14, P.YELLOW), (32, P.CARD), (50, P.TEAL), (68, P.ORANGE), (86, P.GREEN)) if sx + 15 < cw)
    title_plate = rounded_rect_d(18, 32, 68, 24, 3)
    lines = "M27,40 H77 M32,47 H72"
    tag, (x0, y0, x1, y1) = text_path("Agentic SDLC", 0, 0, 11.5)
    tx, ty = (cw - (x1 - x0)) / 2 - x0, 78
    cover.add(f'<g clip-path="url(#{clip})">'
              f'<path d="{top}" fill="{P.PINK}" stroke="{P.INK}" stroke-width="2"/>{stickers}'
              f'<path d="{foot}" fill="{P.TEAL}" stroke="{P.INK}" stroke-width="2"/>'
              f'<path d="M-2,{ch - 18} Q30,{ch - 34} 60,{ch - 26} T{cw + 2},{ch - 30} V{ch - 18} H-2 Z" '
              f'fill="{P.GRASS}" stroke="{P.INK}" stroke-width="1.6"/>'
              f'<path d="{rounded_rect_d(19.5, 34.5, 68, 24, 3)}" fill="{P.INK}"/>'
              f'<path d="{title_plate}" fill="{P.CARD}" stroke="{P.INK}" stroke-width="1.6"/>'
              f'<path d="{lines}" stroke="{P.INK}" stroke-width="3" stroke-linecap="round"/>'
              f'<path d="{rounded_rect_d(tx + x0 - 5 + 1.5, ty + y0 - 4 + 1.5, x1 - x0 + 10, y1 - y0 + 8, 2.5)}" '
              f'fill="{P.INK}"/>'
              f'<path d="{rounded_rect_d(tx + x0 - 5, ty + y0 - 4, x1 - x0 + 10, y1 - y0 + 8, 2.5)}" '
              f'fill="{P.PINK}" stroke="{P.INK}" stroke-width="1.4"/>'
              f'<path d="{tag}" transform="translate({n(tx)} {n(ty)})" fill="{P.WHITE}"/>'
              f'<path d="M7,2 V{ch - 2}" stroke="{P.darken(P.YELLOW, 0.8)}" stroke-width="2.4"/>'
              f'</g>')
    # the little cast on the cover's meadow
    for name, pose, cx, k in (("agent", "wave", 34, 0.085), ("cat", "cheer", 62, 0.082)):
        mod = C.module(name)
        cover.place(C.draw(name, pose), f"translate({n(cx - mod.CENTER_X * k)} {n(ch - 21 - mod.FEET_Y * k)}) "
                                        f"scale({k})")
    cover.path(face, "none", sw=3)
    cover.line(f"M7,3 V{ch - 3}", 1.4, P.INK, 0.55)
    c.place(cover, "translate(52 30) rotate(-5 52 150)")


def arrow_and_tray(c: Canvas, cx: float = 222) -> None:
    """A fat download arrow bobbing down into an open tray."""
    tw, th, top = 84, 30, GROUND - 32
    back = (f"M{cx - tw / 2 + 6},{top} L{cx + tw / 2 - 6},{top} L{cx + tw / 2 - 2},{top + 8} "
            f"L{cx - tw / 2 + 2},{top + 8} Z")
    c.ground_shadow(cx, GROUND + 3, tw / 2 + 6, 5)
    c.path(back, P.darken(P.TEAL, 0.62), sw=2.6)
    sh, hw, y0, y1, neck = 17, 36, 36, 148, 110    # shaft half width, head half width, top, tip, where the head starts
    d = (f"M{cx - sh},{y0 + 6} Q{cx - sh},{y0} {cx - sh + 6},{y0} H{cx + sh - 6} Q{cx + sh},{y0} {cx + sh},{y0 + 6} "
         f"V{neck} H{cx + hw - 4} Q{cx + hw + 3},{neck} {cx + hw - 2},{neck + 6} L{cx + 5},{y1 - 3} "
         f"Q{cx},{y1 + 2} {cx - 5},{y1 - 3} L{cx - hw + 2},{neck + 6} Q{cx - hw - 3},{neck} {cx - hw + 4},{neck} "
         f"H{cx - sh} Z")
    arrow = Canvas()
    arrow.path(d, P.INK, sw=0, extra='transform="translate(4 4)"')
    arrow.shape(d, P.CHAPTER_GREEN, sw=3.4, light=(-5, -4),
                highlight=f"M{cx - sh + 7},{y0 + 10} V{neck - 6}")
    bob = ('<animateTransform attributeName="transform" type="translate" values="0 0;0 14;0 0" '
           'keyTimes="0;.5;1" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" dur="1.8s" '
           'repeatCount="indefinite"/>')
    c.add(f"<g>{arrow.render()}{bob}</g>")
    front = (f"M{cx - tw / 2},{top + 6} H{cx - 18} Q{cx - 14},{top + 16} {cx - 6},{top + 16} H{cx + 6} "
             f"Q{cx + 14},{top + 16} {cx + 18},{top + 6} H{cx + tw / 2} L{cx + tw / 2 - 6},{top + th} "
             f"Q{cx + tw / 2 - 7},{top + th + 3} {cx + tw / 2 - 10},{top + th + 3} H{cx - tw / 2 + 10} "
             f"Q{cx - tw / 2 + 7},{top + th + 3} {cx - tw / 2 + 6},{top + th} Z")
    c.shape(front, P.TEAL, sw=3.2, light=(-4, -3))


def headline(c: Canvas, words: str, subline: str, x: float) -> tuple[float, float]:
    """The headline in balloon letters and the subline on a pink sticker; returns the right ends of both."""
    size = 52
    d, (x0, y0, x1, y1) = text_path(words, x, 94, size)
    c.add(balloon(d, size))
    s2 = 23
    d2, (a0, b0, a1, b1) = text_path(subline, 0, 0, s2, weight=800, track=0.01)
    px, py, pad_x, pad_y = x + 4, 119, 15, 10
    pw, ph = a1 - a0 + 2 * pad_x, b1 - b0 + 2 * pad_y
    pill = rounded_rect_d(px, py, pw, ph, ph / 2)
    turn = f"rotate(-2.2 {n(px + pw / 2)} {n(py + ph / 2)})"
    c.add(f'<g transform="{turn}">'
          f'<path d="{rounded_rect_d(px + 5, py + 5, pw, ph, ph / 2)}" fill="{P.INK}"/>'
          f'<path d="{pill}" fill="{P.PINK}" stroke="{P.INK}" stroke-width="3.4"/>'
          f'<path d="{d2}" transform="translate({n(px + pad_x - a0)} {n(py + pad_y - b0)})" fill="{P.WHITE}"/>'
          f"</g>")
    return x1, px + pw


def character(c: Canvas, name: str, pose: str, feet_x: float, feet_y: float, height: float, flip: bool = False,
              anim: str = "", mood: str = "smile") -> None:
    mod = C.module(name)
    k = height / (mod.FEET_Y - mod.HEAD_TOP)
    sx = -k if flip else k
    tx = feet_x - mod.CENTER_X * sx
    body = C.draw(name, pose, mood).render()
    c.add(f'<g id="char-{name}"><g transform="translate({n(tx)} {n(feet_y - mod.FEET_Y * k)}) scale({n(sx)} {n(k)})">'
          f"{body}</g>{anim}</g>")


def shine(c: Canvas, clip: str) -> None:
    """A glint that sweeps across the plate now and then; off the plate when still."""
    band = "M0,-20 L46,-20 L-14,240 L-60,240 Z M64,-20 L78,-20 L18,240 L4,240 Z"
    c.add(f'<g clip-path="url(#{clip})"><g transform="translate(-160 0)">'
          f'<path d="{band}" fill="{P.WHITE}" fill-opacity=".32"/>'
          '<animateTransform attributeName="transform" type="translate" values="-160 0;-160 0;1000 0;1000 0" '
          'keyTimes="0;.55;.8;1" dur="5s" repeatCount="indefinite"/></g></g>')


# ---------------------------------------------------------------------------------------------------- the button
def build(words: str, subline: str, command: str) -> str:
    c = Canvas()
    clip = plate(c)
    handbook(c)
    arrow_and_tray(c)
    headline(c, words, subline, 280)
    flap = ('<animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" '
            'keyTimes="0;.5;1" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" dur="1.4s" '
            'repeatCount="indefinite"/>')
    character(c, "sparrow", "fly", 606, 174, 58, anim=flap, mood="smile")
    c.ground_shadow(752, GROUND + 2, 40, 5)
    character(c, "agent", "cheer", 752, GROUND, 146)
    shine(c, clip)
    outline_plate(c)
    label = escape(f"{words}, {subline}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="{label}">\n<!-- made by tools/scripts/download_button.py: '
            f'{command.replace("--", "- -")} -->\n<title>{label}</title>{c.render()}</svg>\n')


def previews(svg_path: Path, out: Path) -> list[Path]:
    """PNG previews at 1x and 2x on a white and on a dark page."""
    from playwright.sync_api import sync_playwright

    from bookkit.render import _launch

    out.mkdir(parents=True, exist_ok=True)
    made = []
    with sync_playwright() as pw:
        browser = _launch(pw)
        for theme, bg in (("light", P.WHITE), ("dark", DARK_PAGE)):
            for scale in (1, 2):
                page = browser.new_page(viewport={"width": 460, "height": 160}, device_scale_factor=scale)
                html = out / f".{theme}.html"
                html.write_text(f'<body style="margin:0;padding:20px;background:{bg}">'
                                f'<img src="{svg_path.as_uri()}" width="420"></body>', encoding="utf-8")
                page.goto(html.as_uri())
                page.wait_for_timeout(200)
                target = out / f"download-{theme}@{scale}x.png"
                page.screenshot(path=str(target), full_page=True)
                made.append(target)
                page.close()
                html.unlink()
        browser.close()
    return made


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("headline")
    ap.add_argument("subline")
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--png", type=Path, help="also render PNG previews into this folder")
    args = ap.parse_args(argv)
    command = "uv run python scripts/download_button.py " + shlex.join([args.headline, args.subline])
    svg = build(args.headline, args.subline, command)
    args.out.write_text(svg, encoding="utf-8")
    print(f"{args.out}: {len(svg.encode()) / 1024:.1f} KB")
    if args.png:
        for path in previews(args.out.resolve(), args.png.resolve()):
            print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

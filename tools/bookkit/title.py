"""The chapter title of a story opener, drawn as one SVG from the real outlines of the heading face.

The title is set in the heaviest heading face in ink, each line on a plate of paper, with no letter set apart.
Every size is measured on the glyphs themselves, and the lines are broken by rule, not by the browser, so the
opener knows the title's real size.

Units are millimetres.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

from . import design
from .markup import BuildError

FONT = Path(__file__).parent / "theme" / "fonts" / "Rubik.ttf"
WEIGHT = 900

WIDTH = 158.0           # the title's column on the page
SIZE = 14.1             # 40 pt
LEADING = 1.26          # line pitch, in em
TRACK = -0.02           # letter spacing, in em
PLATE_X = 3.4           # the paper plate reaches this far beyond the first and the last letter of a line
PLATE_Y = 0.4           # ... and this far above the ascender and below the descender


@dataclass
class _Face:
    glyphs: object
    cmap: dict
    advance: dict
    upm: float
    ascent: float
    descent: float


@lru_cache(maxsize=1)
def _face() -> _Face:
    font = instancer.instantiateVariableFont(TTFont(FONT), {"wght": WEIGHT})
    cmap = font.getBestCmap()
    return _Face(font.getGlyphSet(), cmap, {name: adv for name, (adv, _) in font["hmtx"].metrics.items()},
                 float(font["head"].unitsPerEm), float(font["hhea"].ascent),
                 float(-font["hhea"].descent))


def _glyph(ch: str) -> str:
    """The glyph of a character; one the heading face lacks is an error, never a silent stand-in."""
    name = _face().cmap.get(ord(ch))
    if name is None:
        raise BuildError(f"the title's face (Rubik) has no letter {ch!r} (U+{ord(ch):04X}); write the title without it")
    return name


def _space(size: float, track: float) -> float:
    return _face().advance[_glyph(" ")] / _face().upm * size + track * size


def advance(text: str, size: float, track: float = TRACK) -> float:
    """How far a run of text advances, in mm (no kerning: the heavy face is set loose)."""
    face = _face()
    return sum(_space(size, track) if ch == " " else face.advance[_glyph(ch)] / face.upm * size + track * size
               for ch in text) - (track * size if text else 0)


def outline(text: str, x: float, y: float, size: float, track: float = TRACK) -> str:
    """The run's letters as one SVG path, its start at (x, y) on the baseline."""
    face = _face()
    pen = SVGPathPen(face.glyphs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    s = size / face.upm
    for ch in text:
        if ch == " ":
            x += _space(size, track)
            continue
        name = _glyph(ch)
        face.glyphs[name].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        x += face.advance[name] / face.upm * size + track * size
    return pen.getCommands()


# ---------------------------------------------------------------------------------------------------- line breaks
def _words(text: str) -> list[str]:
    """The words to break between; a word of one or two letters goes with the next one (a preposition or a
    conjunction never hangs at the end of a line)."""
    out: list[str] = []
    carry = ""
    for word in text.split():
        if len(word) <= 2 and word.isalpha():
            carry += word + " "
        else:
            out.append(carry + word)
            carry = ""
    if carry:
        if out:
            out[-1] += " " + carry.strip()
        else:
            out.append(carry.strip())
    return out


def break_lines(text: str, room: float, lines: int) -> list[str] | None:
    """`text` in exactly `lines` lines no wider than `room`, as even as can be (the longest line as short as
    possible). None when it does not fit."""
    words = _words(text)
    if not words or lines > len(words):
        return None
    best, best_width = None, None
    for cuts in combinations(range(1, len(words)), lines - 1):
        bounds = (0, *cuts, len(words))
        rows = [" ".join(words[a:b]) for a, b in zip(bounds, bounds[1:], strict=False)]
        widths = [advance(row, SIZE) for row in rows]
        if max(widths) > room:
            continue
        spread = max(widths) - 0.35 * min(widths)        # even lines, and no stub of a last line
        if best_width is None or spread < best_width:
            best, best_width = rows, spread
    return best


# ---------------------------------------------------------------------------------------------------- the layout
@dataclass
class Title:
    svg: str
    width: float        # how far the lettering reaches, in mm
    height: float


def draw(title: str) -> Title:
    """The whole title in as few even lines as fit the column, each on its paper plate, in ink."""
    rows = next((r for n in range(1, 6) if (r := break_lines(title, WIDTH - 2 * PLATE_X, n))), [title])
    face = _face()
    ascent, descent = face.ascent / face.upm * SIZE, face.descent / face.upm * SIZE
    pitch = LEADING * SIZE
    plate_h = ascent + descent + 2 * PLATE_Y
    parts, right = [], 0.0
    for i, row in enumerate(rows):
        top = i * pitch
        width = advance(row, SIZE) + 2 * PLATE_X
        right = max(right, width)
        parts.append(f'<rect x="0" y="{top:.2f}" width="{width:.2f}" height="{plate_h:.2f}" fill="{design.PAPER}"/>')
        parts.append(f'<path d="{outline(row, PLATE_X, top + PLATE_Y + ascent, SIZE)}" fill="{design.INK}"/>')
    height = (len(rows) - 1) * pitch + plate_h
    svg = (f'<svg class="opener-lettering" viewBox="0 0 {right:.2f} {height:.2f}" width="{right:.2f}mm" '
           f'height="{height:.2f}mm" aria-hidden="true">{"".join(parts)}</svg>')
    return Title(svg, right, height)

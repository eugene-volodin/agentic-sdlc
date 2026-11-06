"""Doodles: small standalone objects scattered through the book to keep margins and gaps alive.

The set is the furniture of a programmer's desk across the decades: the old beige hardware of
the original encyclopedia, storage media, tools, and a few things every developer keeps around
(a mug, a rubber duck, a bug). Each doodle is a function drawing on a 100 x 100 canvas and
registered with `@doodle_drawing`; `doodle(name)` returns it as a complete `<svg>`.

To add one: write the function, decorate it, and it is immediately available to the paginator's
fillers (`pages.FILLERS`) and to the contact cards. Keep to the house style - ink outline, one
light source from the top left (`Canvas.shape` does the shading), colors from `bookkit.design`.
"""
from __future__ import annotations

import math
from collections.abc import Callable

from .. import design as P
from .ink import INK, Canvas, ellipse_d, n, rounded_rect_d

_DRAWINGS: dict[str, Callable[[Canvas], None]] = {}


def doodle_drawing(function: Callable[[Canvas], None]) -> Callable[[Canvas], None]:
    """Register a doodle under the name of its function."""
    _DRAWINGS[function.__name__] = function
    return function


def doodle(name: str) -> str:
    """Return the doodle as a complete `<svg>` with the class `doodle`."""
    if name not in _DRAWINGS:
        raise ValueError(f"unknown doodle {name!r}; available: {', '.join(_DRAWINGS)}")
    c = Canvas()
    _DRAWINGS[name](c)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" class="doodle" aria-hidden="true">'
            f'{c.render()}</svg>')


def _led(c: Canvas, x: float, y: float, color: str, r: float = 2.6) -> None:
    c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{color}" stroke="{INK}" stroke-width="1.3"/>')


def _screen(c: Canvas, d: str, lines: str) -> None:
    """A dark glass screen with glowing lines of text and a glint."""
    paint = c.gradient([(0, P.SCREEN_LIGHT), (1, P.SCREEN_DARK)], 20, 10, 80, 70)
    c.path(d, paint, 2.2)
    c.line(lines, 2.6, P.GLOW)


# ============================================================================ the beige machines
@doodle_drawing
def monitor(c: Canvas) -> None:
    """A tube monitor on its swivel foot."""
    c.shape("M38,70 L33,84 H67 L62,70 Z", P.BEIGE_DARK, sw=2.4, light=None)
    c.shape(rounded_rect_d(22, 83, 56, 10, 4), P.BEIGE, sw=2.4, light=(-2, -2), shade_k=0.86)
    c.shape("M12,14 Q12,6 20,6 H80 Q88,6 88,14 V63 Q88,71 80,71 H20 Q12,71 12,63 Z", P.BEIGE, sw=2.6,
            light=(-3, -3), shade_k=0.86, stipple=(70, 10, 16, 58, 12, "right"))
    _screen(c, "M24,14 H76 Q80,14 80,18 V52 Q80,57 75,57 H25 Q20,57 20,52 V18 Q20,14 24,14 Z",
            "M27,24 h20 M27,32 h34 M27,40 h14 M45,40 h10")
    c.line("M25,20 Q23,28 24,38", 2, P.WHITE, 0.35)
    c.line("M22,64 h18", 1.6, opacity=0.5)                    # brand plate
    _led(c, 79, 64, P.GREEN, 2.2)
    c.path(rounded_rect_d(62, 61.5, 9, 5, 1.5), P.BEIGE_DARK, 1.5)


@doodle_drawing
def tower(c: Canvas) -> None:
    """A system unit standing upright, drives at the top, vents at the bottom."""
    c.shape(rounded_rect_d(24, 4, 52, 90, 6), P.BEIGE, sw=2.6, light=(-3, -3), shade_k=0.86,
            stipple=(60, 8, 14, 82, 14, "right"))
    c.shape("M22,92 H78 V96 H22 Z", P.BEIGE_DARK, sw=2.2, light=None)       # feet rail
    c.path(rounded_rect_d(31, 11, 38, 11, 2), P.BEIGE_DARK, 1.9)            # 5.25" bay
    c.line("M36,16.5 H64", 2.2, P.DESK)
    c.path(rounded_rect_d(31, 26, 38, 9, 2), P.BEIGE_DARK, 1.9)             # 3.5" bay
    c.path(rounded_rect_d(38, 29, 20, 3, 1), P.DESK, 1.2)
    c.path(rounded_rect_d(61, 28.5, 5, 4, 1), P.BEIGE, 1.2)
    c.shape(ellipse_d(40, 48, 6, 6), P.METAL, sw=2, light=(-1, -1))         # power
    c.path(rounded_rect_d(52, 44, 15, 8, 2), P.SCREEN_DARK, 1.6)            # the "turbo" display
    c.line("M55,48 h9", 2, P.GLOW)
    _led(c, 36, 60, P.GREEN, 2.2)
    _led(c, 44, 60, P.AMBER, 2.2)
    c.line("M33,70 H67 M33,75 H67 M33,80 H67 M33,85 H67", 1.7, opacity=0.55)


@doodle_drawing
def keyboard(c: Canvas) -> None:
    """A chunky keyboard seen from the front, with its curly cable."""
    c.line("M50,30 q-4,-8 4,-10 q8,-2 4,-9", 3, P.CHARCOAL)
    c.shape("M8,84 L4,76 H96 L92,84 Z", P.BEIGE_SHADE, sw=2.2, light=None)  # front edge
    c.shape("M14,30 H86 L96,76 H4 Z", P.BEIGE, sw=2.6, light=(-3, -2), shade_k=0.88)
    for row, y in enumerate((35, 45, 55)):               # three rows of keys, widening towards the front
        left, span = 17 - row * 2.2, 66 + row * 4.4
        step = span / 9
        for i in range(9):
            c.path(rounded_rect_d(left + i * step, y, step - 1.5, 8, 1.6), P.CARD, 1.4)
    c.path(rounded_rect_d(27, 65, 46, 7, 2), P.CARD, 1.5)                   # space bar
    c.path(rounded_rect_d(10, 65, 13, 7, 2), P.CARD, 1.4)
    c.path(rounded_rect_d(77, 65, 13, 7, 2), P.RED, 1.4)                    # the one red key


@doodle_drawing
def mouse(c: Canvas) -> None:
    """A two-button ball mouse with a long tail."""
    c.line("M50,24 Q47,8 62,7 Q80,6 84,18 Q86,26 78,28", 3.4, P.CHARCOAL)
    c.shape("M26,54 Q26,22 50,22 Q74,22 74,54 L74,70 Q74,95 50,95 Q26,95 26,70 Z", P.BEIGE, sw=2.6,
            light=(-3, -3), shade_k=0.86, stipple=(58, 56, 14, 36, 10, "right"), highlight="M33,36 Q31,46 32,56")
    c.line("M26,53 Q50,57 74,53 M50,22 V55", 2.2)
    c.path(rounded_rect_d(46.5, 30, 7, 13, 3.5), P.METAL_DARK, 1.6)         # wheel
    c.line("M40,84 Q50,88 60,84", 1.6, opacity=0.5)


@doodle_drawing
def printer(c: Canvas) -> None:
    """A dot-matrix printer chewing through fan-fold paper."""
    c.shape("M26,40 V8 H74 V40 Z", P.WHITE, sw=2.4, light=None)             # paper going in
    for y in (13, 20, 27, 34):
        c.add(f'<circle cx="30" cy="{y}" r="1.3" fill="{INK}"/><circle cx="70" cy="{y}" r="1.3" fill="{INK}"/>')
    c.line("M36,15 H64 M36,22 H64 M36,29 H56", 1.6, opacity=0.5)
    c.shape("M10,46 Q10,38 18,38 H82 Q90,38 90,46 V68 Q90,74 84,74 H16 Q10,74 10,68 Z", P.BEIGE, sw=2.6,
            light=(-3, -3), shade_k=0.86, stipple=(72, 42, 16, 30, 10, "right"))
    c.path(rounded_rect_d(20, 58, 60, 6, 2), P.DESK, 1.8)                   # the slot
    c.shape("M24,62 H76 L83,93 H17 Z", P.WHITE, sw=2.4, light=(-2, -2), shade_k=0.92)
    c.line("M30,71 H70 M28,78 H72 M27,85 H60", 1.6, opacity=0.5)
    c.path(rounded_rect_d(16, 44, 16, 8, 2), P.BEIGE_DARK, 1.5)
    _led(c, 76, 48, P.GREEN, 2.3)
    _led(c, 84, 48, P.RED, 2.3)


@doodle_drawing
def drive(c: Canvas) -> None:
    """A floppy drive with a disk half way in."""
    c.shape("M28,22 H72 V52 H28 Z", P.BLUE, sw=2.4, light=(-2, -2))
    c.path("M38,22 H62 V35 H38 Z", P.METAL_LIGHT, 1.8)
    c.path("M53,25 H58 V32 H53 Z", P.CHARCOAL, 1.2)
    c.shape(rounded_rect_d(6, 44, 88, 42, 7), P.BEIGE, sw=2.6, light=(-3, -3), shade_k=0.86,
            stipple=(76, 48, 16, 34, 10, "right"))
    c.path(rounded_rect_d(16, 52, 68, 8, 2.5), P.DESK, 2)
    c.path(rounded_rect_d(62, 68, 20, 9, 2.5), P.BEIGE_DARK, 1.8)           # eject button
    c.line("M68,72.5 h8", 1.8)
    _led(c, 22, 72, P.GREEN, 3)
    c.line("M32,72 h18 M32,77 h12", 1.5, opacity=0.5)


@doodle_drawing
def modem(c: Canvas) -> None:
    """A dial-up modem: a row of lights, an antenna-like cord, and a lot of screeching."""
    c.line("M20,58 Q8,50 12,36 Q16,24 28,26", 3, P.CHARCOAL)                # phone cord
    c.line("M66,34 q4,-6 0,-11 M74,36 q8,-9 0,-18 M82,38 q12,-12 0,-25", 2.2)   # the noise
    c.shape("M14,60 Q14,52 22,52 H82 Q90,52 90,60 V78 Q90,84 84,84 H20 Q14,84 14,78 Z", P.BEIGE, sw=2.6,
            light=(-3, -3), shade_k=0.86)
    c.shape("M18,84 H28 V90 H18 Z M76,84 H86 V90 H76 Z", P.CHARCOAL, sw=2, light=None)
    c.path(rounded_rect_d(20, 58, 64, 12, 3), P.CHARCOAL, 1.8)
    for i, color in enumerate((P.RED, P.GREEN, P.GREEN, P.AMBER, P.GREEN, P.RED)):
        c.add(f'<circle cx="{28 + i * 9.6}" cy="64" r="2.6" fill="{color}"/>')
    c.line("M22,77 h30", 1.6, opacity=0.5)


@doodle_drawing
def harddisk(c: Canvas) -> None:
    """An opened hard disk: the platter, the arm and four screws."""
    c.shape(rounded_rect_d(10, 8, 80, 84, 8), P.METAL, sw=2.6, light=(-3, -3), shade_k=0.86)
    c.shape(ellipse_d(46, 42, 29, 29), P.METAL_PALE, sw=2.4, light=(-4, -4), shade_k=0.9)
    c.line("M27,30 Q36,18 50,16", 4, P.WHITE, 0.6)
    c.path(ellipse_d(46, 42, 8, 8), P.METAL_DARK, 2)
    c.path(ellipse_d(46, 42, 2.6, 2.6), P.CHARCOAL, 0)
    c.shape("M70,84 Q62,78 64,70 L52,50 L57,47 L72,66 Q82,68 80,80 Z", P.METAL_DARK, sw=2.2, light=(-2, -2))
    c.path(ellipse_d(72, 76, 4, 4), P.METAL_PALE, 1.6)
    for x, y in ((17, 15), (83, 15), (17, 85), (83, 85)):
        c.path(ellipse_d(x, y, 2.6, 2.6), P.METAL_PALE, 1.4)
        c.line(f"M{x - 1.6},{y} h3.2", 1)
    c.path(rounded_rect_d(18, 78, 24, 7, 2), P.CARD, 1.4)


@doodle_drawing
def chip(c: Canvas) -> None:
    """A microchip on its legs."""
    legs = " ".join(f"M12,{y} H28 M72,{y} H88" for y in (32, 44, 56, 68))
    legs += " " + " ".join(f"M{x},12 V28 M{x},72 V88" for x in (32, 44, 56, 68))
    c.line(legs, 6.4)
    c.line(legs, 3.2, P.METAL)
    c.shape(rounded_rect_d(24, 24, 52, 52, 6), P.CHARCOAL, sw=2.6, light=(-3, -3), shade_k=0.7)
    c.path(ellipse_d(33, 33, 3, 3), P.METAL_DARK, 0)                        # pin-one mark
    c.path(rounded_rect_d(36, 40, 30, 22, 3), P.METAL_DARK, 1.6)
    c.line("M41,47 H61 M41,53 H55", 2.2, P.METAL_PALE)
    c.line("M30,70 h12", 1.6, P.METAL_DARK)


@doodle_drawing
def router(c: Canvas) -> None:
    """A little network box with two antennas and blinking lights."""
    c.line("M28,56 L20,16 M72,56 L80,16", 6.6)
    c.line("M28,56 L20,16 M72,56 L80,16", 3.4, P.CHARCOAL)
    c.line("M40,26 q10,-9 20,0 M34,18 q16,-14 32,0", 2.4, P.TEAL)           # the signal
    c.shape("M10,62 Q10,54 18,54 H82 Q90,54 90,62 V78 Q90,84 84,84 H16 Q10,84 10,78 Z", P.CARD, sw=2.6,
            light=(-3, -3), shade_k=0.88)
    c.shape("M16,84 H26 V90 H16 Z M74,84 H84 V90 H74 Z", P.CHARCOAL, sw=2, light=None)
    for i, color in enumerate((P.GREEN, P.GREEN, P.AMBER, P.GREEN)):
        _led(c, 22 + i * 9, 66, color, 2.4)
    c.path(rounded_rect_d(62, 62, 20, 9, 2), P.CHARCOAL, 1.6)
    c.line("M18,76 h34", 1.6, opacity=0.5)


# ============================================================================ storage
@doodle_drawing
def floppy(c: Canvas) -> None:
    """A 3.5-inch diskette with its metal shutter and a hand-written label."""
    c.shape("M12,10 H78 L90,22 V86 Q90,90 86,90 H16 Q12,90 12,86 Z", P.BLUE, sw=2.6, light=(-3, -3),
            stipple=(72, 30, 16, 56, 10, "right"))
    c.shape("M30,10 H68 V36 H30 Z", P.METAL_LIGHT, sw=2.2, light=(-2, -2), shade_k=0.9)   # shutter
    c.path("M54,14 H62 V32 H54 Z", P.CHARCOAL, 1.4)
    c.shape("M24,52 H78 V90 H24 Z", P.CARD, sw=2.2, light=None)             # label
    c.line("M24,60 H78", 2.4, P.PINK)
    c.line("M31,69 H70 M31,76 H70 M31,83 H56", 1.6, opacity=0.5)
    c.path("M16,82 h5 v5 h-5 Z", P.CHARCOAL, 1.2)                           # write-protect tab


@doodle_drawing
def floppy5(c: Canvas) -> None:
    """A big bendy 5.25-inch floppy in its paper sleeve."""
    c.shape("M22,6 H86 V70 H22 Z", P.CARD, sw=2.4, light=(-2, -2), shade_k=0.92)   # sleeve behind
    c.shape(rounded_rect_d(10, 20, 72, 74, 4), P.CHARCOAL, sw=2.6, light=(-3, -3), shade_k=0.7)
    c.path(ellipse_d(46, 54, 11, 11), P.METAL_PALE, 2)
    c.path(ellipse_d(46, 54, 4.6, 4.6), P.CHARCOAL, 1.4)
    c.path(rounded_rect_d(41, 70, 10, 20, 5), P.DESK, 1.6)                  # read window
    c.path(ellipse_d(60, 48, 1.8, 1.8), P.PAPER, 0)                         # index hole
    c.path(rounded_rect_d(16, 26, 34, 13, 2), P.YELLOW, 1.6)                # label
    c.line("M20,31 h24 M20,35 h16", 1.5, opacity=0.6)
    c.path("M82,34 h-5 v8 h5 Z", P.PAPER, 1.4)                              # notch


@doodle_drawing
def disc(c: Canvas) -> None:
    """A compact disc catching the light."""
    c.shape(ellipse_d(50, 50, 42, 42), P.METAL_LIGHT, sw=2.6, light=(-4, -4), shade_k=0.9)
    c.line("M21,36 Q30,18 50,14", 6, P.PINK, 0.65)
    c.line("M26,30 Q36,20 50,19", 3, P.YELLOW, 0.7)
    c.line("M79,64 Q70,82 50,86", 6, P.TEAL, 0.65)
    c.line("M74,70 Q64,80 50,81", 3, P.VIOLET, 0.6)
    c.path(ellipse_d(50, 50, 15, 15), P.METAL_PALE, 2.2)
    c.path(ellipse_d(50, 50, 6, 6), P.PAPER, 2)


@doodle_drawing
def cassette(c: Canvas) -> None:
    """An audio cassette: programs used to be loaded from these."""
    c.shape(rounded_rect_d(6, 20, 88, 60, 6), P.CHARCOAL, sw=2.6, light=(-3, -3), shade_k=0.7)
    c.shape(rounded_rect_d(13, 26, 74, 34, 3), P.CARD, sw=2, light=None)
    c.line("M13,34 H87", 2.6, P.ORANGE)
    c.line("M20,30 h30", 1.5, opacity=0.6)
    c.path(rounded_rect_d(27, 39, 46, 16, 8), P.SCREEN_DARK, 1.8)           # window
    for x in (36, 64):
        c.path(ellipse_d(x, 47, 6, 6), P.CARD, 1.6)
        c.line(f"M{x - 3},47 h6 M{x},44 v6", 1.3)
    c.shape("M24,80 L28,66 H72 L76,80 Z", P.DESK, sw=2, light=None)
    for x in (34, 50, 66):
        c.path(ellipse_d(x, 73, 2, 2), P.PAPER, 0)
    for x, y in ((11, 25), (89, 25), (11, 75), (89, 75)):
        c.path(ellipse_d(x, y, 1.6, 1.6), P.METAL_DARK, 0)


@doodle_drawing
def cartridge(c: Canvas) -> None:
    """A game cartridge with a bright sticker."""
    c.shape("M18,8 H82 Q88,8 88,14 V70 H80 V92 H20 V70 H12 V14 Q12,8 18,8 Z", P.METAL_DARK, sw=2.6,
            light=(-3, -3), shade_k=0.82)
    c.line("M20,14 H80 M20,19 H80", 1.8, opacity=0.5)                       # grip ridges
    c.shape(rounded_rect_d(21, 26, 58, 38, 4), P.YELLOW, sw=2.2, light=(-2, -2))
    c.shape("M27,58 L40,38 L50,50 L58,42 L73,58 Z", P.TEAL, sw=1.8, light=None)
    c.path(ellipse_d(64, 35, 4.6, 4.6), P.RED, 1.6)
    for x in range(26, 76, 7):
        c.line(f"M{x},78 V92", 3.2, P.SUN)
    c.line("M20,78 H80", 2)


@doodle_drawing
def punchcard(c: Canvas) -> None:
    """A punched card: the great-grandparent of every source file."""
    c.shape("M16,22 H88 Q92,22 92,26 V78 Q92,82 88,82 H10 Q6,82 6,78 V32 Z", P.CREAM, sw=2.6, light=(-3, -3),
            shade_k=0.9)
    c.line("M12,32 H86", 1.4, opacity=0.4)
    holes = ((16, 40), (30, 40), (51, 40), (72, 40), (23, 49), (44, 49), (58, 49), (79, 49), (16, 58), (37, 58),
             (65, 58), (30, 67), (51, 67), (72, 67), (79, 67), (23, 76), (58, 76))
    for x, y in holes:
        c.path(rounded_rect_d(x, y - 3, 4.4, 6, 1), P.CHARCOAL, 0)
    c.line("M22,27 h40", 1.6, opacity=0.5)


@doodle_drawing
def reel(c: Canvas) -> None:
    """A reel of magnetic tape."""
    c.line("M84,64 Q94,78 80,90 Q70,96 58,90", 4, P.FEATHER_DARK)           # loose tape
    c.shape(ellipse_d(46, 48, 40, 40), P.METAL_LIGHT, sw=2.6, light=(-4, -4), shade_k=0.88)
    c.path(ellipse_d(46, 48, 30, 30), P.FEATHER_DARK, 2)                    # the wound tape
    c.path(ellipse_d(46, 48, 13, 13), P.METAL_PALE, 2)
    for angle in (0, 120, 240):
        c.add(f'<path d="M46,29 Q53,38 46,43 Q39,38 46,29 Z" transform="rotate({angle} 46 48)" '
              f'fill="{P.PAPER}" stroke="{INK}" stroke-width="1.6"/>')
    c.path(ellipse_d(46, 48, 4, 4), P.CHARCOAL, 0)


# ============================================================================ paper and tools
@doodle_drawing
def folder(c: Canvas) -> None:
    """A manila folder with papers peeking out."""
    c.shape("M8,26 H36 L44,36 H90 Q92,36 92,38 V84 Q92,88 88,88 H12 Q8,88 8,84 Z", P.AMBER, sw=2.6,
            light=(-3, -3))
    c.shape("M18,30 H78 V60 H18 Z", P.WHITE, sw=2, light=None)
    c.line("M24,37 H70 M24,43 H62", 1.5, opacity=0.5)
    c.shape("M8,48 Q8,46 10,46 H90 Q92,46 92,48 V84 Q92,88 88,88 H12 Q8,88 8,84 Z", P.YELLOW, sw=2.6,
            light=(-3, -3), stipple=(72, 50, 18, 36, 10, "right"))
    c.path(rounded_rect_d(18, 56, 30, 12, 2), P.CARD, 1.6)
    c.line("M22,62 h20", 1.6, opacity=0.6)


@doodle_drawing
def sheet(c: Canvas) -> None:
    """A document with a folded corner and a title line."""
    c.shape("M18,6 H64 L84,26 V94 H18 Z", P.WHITE, sw=2.6, light=(-3, -3), shade_k=0.9)
    c.shape("M64,6 V26 H84 Z", P.PAPER_FOLD, sw=2.2, light=None)
    c.line("M28,36 H58", 3.6, P.TEAL)
    c.line("M28,49 H74 M28,58 H74 M28,67 H60 M28,76 H70 M28,85 H50", 1.8, opacity=0.5)


@doodle_drawing
def notebook(c: Canvas) -> None:
    """A spiral notebook."""
    c.shape(rounded_rect_d(20, 10, 66, 82, 5), P.TEAL, sw=2.6, light=(-3, -3))
    c.shape(rounded_rect_d(34, 22, 40, 20, 3), P.CARD, sw=1.8, light=None)
    c.line("M40,29 h28 M40,35 h18", 1.6, opacity=0.6)
    for y in range(18, 88, 10):
        c.path(ellipse_d(20, y, 6, 3), "none", 2.4)
        c.path(ellipse_d(25, y, 1.6, 1.6), P.CHARCOAL, 0)


@doodle_drawing
def book(c: Canvas) -> None:
    """A thick manual with a bookmark."""
    c.shape("M16,14 Q16,8 22,8 H82 V78 H22 Q16,78 16,84 Z", P.PINK, sw=2.6, light=(-3, -3))
    c.shape("M16,84 Q16,78 22,78 H82 V92 H22 Q16,92 16,86 Z", P.WHITE, sw=2.4, light=None)
    c.line("M24,83 H80 M24,87 H80", 1.3, opacity=0.5)
    c.shape(rounded_rect_d(30, 20, 40, 26, 3), P.CARD, sw=1.8, light=None)
    c.line("M36,28 h28 M36,34 h28 M36,40 h16", 1.6, opacity=0.6)
    c.shape("M64,78 V96 L69,91 L74,96 V78 Z", P.YELLOW, sw=1.8, light=None)
    c.line("M22,8 V78", 2)


@doodle_drawing
def pencil(c: Canvas) -> None:
    """A stubby pencil, sharpened many times."""
    c.add('<g transform="rotate(-40 50 50)">')
    c.shape("M22,42 H74 V58 H22 Z", P.YELLOW, sw=2.6, light=(-2, -3))
    c.line("M22,47.5 H74 M22,52.5 H74", 1.3, opacity=0.5)
    c.shape("M74,42 L92,50 L74,58 Z", P.WOOD_PALE, sw=2.4, light=None)
    c.path("M86,47.4 L92,50 L86,52.6 Z", P.CHARCOAL, 1.2)
    c.shape("M14,42 H22 V58 H14 Z", P.METAL, sw=2.2, light=None)
    c.line("M17,42 V58", 1.2)
    c.shape("M6,44 Q4,50 6,56 H14 V44 Z", P.PINK, sw=2.2, light=(-1, -2))
    c.add("</g>")


@doodle_drawing
def magnifier(c: Canvas) -> None:
    """A magnifying glass for hunting bugs."""
    c.tube("M62,62 L88,88", P.FEATHER_DARK, 9, sw=2.4)
    c.shape(ellipse_d(42, 42, 32, 32), P.METAL, sw=2.6, light=(-3, -3), shade_k=0.85)
    paint = c.gradient([(0, P.WHITE), (1, P.SKY)], 24, 22, 60, 62)
    c.path(ellipse_d(42, 42, 24, 24), paint, 2.2)
    c.line("M28,34 Q32,26 40,24", 3.4, P.WHITE)


@doodle_drawing
def key(c: Canvas) -> None:
    """A key: access, secrets, permissions."""
    c.shape("M46,43 H94 V57 H86 V68 H76 V57 H68 V64 H60 V57 H46 Z", P.YELLOW, sw=2.6, light=(-2, -2))
    c.shape(ellipse_d(28, 50, 22, 22), P.YELLOW, sw=2.6, light=(-3, -3), highlight="M14,42 Q12,50 15,58")
    c.path(ellipse_d(22, 50, 7, 7), P.PAPER, 2.2)


@doodle_drawing
def gear(c: Canvas) -> None:
    """A cog wheel: settings."""
    for angle in range(0, 360, 45):
        c.add(f'<path d="M42,4 H58 L60,24 H40 Z" transform="rotate({angle} 50 50)" fill="{P.METAL_DARK}" '
              f'stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>')
    c.shape(ellipse_d(50, 50, 32, 32), P.METAL, sw=2.6, light=(-3, -3), shade_k=0.84)
    c.path(ellipse_d(50, 50, 21, 21), "none", 1.6)
    c.path(ellipse_d(50, 50, 11, 11), P.PAPER, 2.4)


@doodle_drawing
def plug(c: Canvas) -> None:
    """A power plug on a curly cord."""
    c.line("M50,70 Q50,82 40,84 Q26,86 30,96", 6, P.CHARCOAL)
    c.shape(rounded_rect_d(35, 6, 8, 26, 2.5), P.METAL, sw=2.2, light=(-1, -1))
    c.shape(rounded_rect_d(57, 6, 8, 26, 2.5), P.METAL, sw=2.2, light=(-1, -1))
    c.shape("M26,34 Q26,28 32,28 H68 Q74,28 74,34 V54 Q74,70 58,72 H42 Q26,70 26,54 Z", P.ORANGE, sw=2.6,
            light=(-3, -3), highlight="M33,36 Q31,46 34,56")
    c.line("M36,44 H64 M36,51 H64", 1.8, opacity=0.5)


@doodle_drawing
def bulb(c: Canvas) -> None:
    """A light bulb: an idea."""
    c.line("M50,2 V10 M14,16 L21,23 M86,16 L79,23 M4,46 H13 M87,46 H96", 2.8)
    c.shape("M24,46 Q24,16 50,16 Q76,16 76,46 Q76,60 63,69 L63,76 H37 L37,69 Q24,60 24,46 Z", P.SUN, sw=2.6,
            light=(-4, -4), shade_k=0.86, highlight="M35,30 Q30,40 33,50")
    c.line("M42,76 L44,54 L50,62 L56,54 L58,76", 2, P.ORANGE_DARK)          # filament
    c.shape(rounded_rect_d(37, 76, 26, 14, 4), P.METAL_DARK, sw=2.4, light=(-2, -2))
    c.line("M38,81 H62 M38,85.5 H62", 1.6)
    c.shape("M44,90 H56 L53,96 H47 Z", P.CHARCOAL, sw=2, light=None)


@doodle_drawing
def terminal(c: Canvas) -> None:
    """A terminal window with a prompt waiting."""
    c.shape(rounded_rect_d(6, 16, 88, 68, 8), P.TERMINAL, sw=2.6, light=None)
    c.path("M6,34 H94 V24 Q94,16 86,16 H14 Q6,16 6,24 Z", P.CHARCOAL, 2.6)
    for x, color in ((17, P.PINK), (28, P.YELLOW), (39, P.GREEN)):
        c.add(f'<circle cx="{x}" cy="25" r="3.8" fill="{color}" stroke="{INK}" stroke-width="1.2"/>')
    c.line("M20,48 l13,10 l-13,10", 4.4, P.GLOW)
    c.line("M42,69 h24", 4.4, P.GLOW)
    c.line("M74,48 h10 M74,56 h6", 2.4, P.TERMINAL_DIM)


@doodle_drawing
def calculator(c: Canvas) -> None:
    """A pocket calculator."""
    c.shape(rounded_rect_d(22, 6, 56, 88, 7), P.CHARCOAL, sw=2.6, light=(-3, -3), shade_k=0.7)
    c.path(rounded_rect_d(29, 13, 42, 18, 3), P.HILL_FAR, 1.8)
    c.line("M52,26 h4 M59,19 v7 M64,19 h4 v7 h-4 Z", 2, P.CHARCOAL)
    keys = (P.METAL_PALE, P.METAL_PALE, P.METAL_PALE, P.ORANGE)
    for row in range(4):
        for col in range(4):
            color = P.RED if (row, col) == (3, 3) else keys[col]
            c.path(rounded_rect_d(29 + col * 11, 38 + row * 13, 8.6, 9.6, 2), color, 1.5)


@doodle_drawing
def phone(c: Canvas) -> None:
    """A desk telephone with a rotary dial."""
    c.shape("M14,36 Q10,22 22,20 Q50,12 78,20 Q90,22 86,36 L78,38 Q76,30 68,30 H32 Q24,30 22,38 Z", P.RED,
            sw=2.6, light=(-3, -3))                                          # handset
    c.shape("M20,90 Q14,90 16,82 L26,46 Q28,40 34,40 H66 Q72,40 74,46 L84,82 Q86,90 80,90 Z", P.RED, sw=2.6,
            light=(-3, -3), stipple=(64, 50, 18, 36, 10, "right"))
    c.shape(ellipse_d(50, 66, 17, 17), P.CARD, sw=2.2, light=None)
    for i in range(8):
        a = i * 40 - 60
        x, y = 50 + 11.5 * math.cos(math.radians(a)), 66 + 11.5 * math.sin(math.radians(a))
        c.path(ellipse_d(x, y, 2.3, 2.3), P.CHARCOAL, 0)
    c.path(ellipse_d(50, 66, 4.6, 4.6), P.RED, 1.6)
    c.line("M16,36 Q4,48 12,60 Q18,68 12,78", 2.6, P.CHARCOAL)              # cord


@doodle_drawing
def lamp(c: Canvas) -> None:
    """A desk lamp bending over the work."""
    c.shape("M22,92 Q22,84 32,84 H62 Q72,84 72,92 Z", P.CHARCOAL, sw=2.6, light=(-3, -2), shade_k=0.7)
    c.line("M46,84 L34,52 L62,30", 7)
    c.line("M46,84 L34,52 L62,30", 3.6, P.METAL)
    c.path(ellipse_d(34, 52, 4, 4), P.METAL_DARK, 1.8)
    c.add(f'<path d="M58,40 L96,62 L72,66 Z" fill="{P.YELLOW_PALE}" opacity=".8"/>')   # light cone
    c.shape("M52,22 L80,18 Q92,30 88,46 L62,42 Q52,34 52,22 Z", P.GREEN, sw=2.6, light=(-3, -3))
    c.path(ellipse_d(74, 44, 8, 4), P.SUN, 1.8)


@doodle_drawing
def joystick(c: Canvas) -> None:
    """An arcade joystick with two fire buttons."""
    c.shape("M12,74 Q12,64 22,64 H78 Q88,64 88,74 V84 Q88,92 80,92 H20 Q12,92 12,84 Z", P.CHARCOAL, sw=2.6,
            light=(-3, -3), shade_k=0.7)
    c.shape("M36,64 Q36,56 44,56 H52 Q60,56 60,64 Z", P.DESK, sw=2.2, light=None)   # boot
    c.tube("M48,60 L44,32", P.METAL, 6, sw=2.2)
    c.shape(ellipse_d(43, 22, 15, 15), P.RED, sw=2.6, light=(-3, -3), highlight="M34,15 Q31,21 33,28")
    c.shape(ellipse_d(72, 72, 6.5, 4.5), P.YELLOW, sw=2, light=None)
    c.shape(ellipse_d(24, 80, 5, 3.6), P.GREEN, sw=2, light=None)


@doodle_drawing
def gamepad(c: Canvas) -> None:
    """A two-button game pad."""
    c.line("M50,30 Q50,14 64,12 Q76,10 78,4", 3, P.CHARCOAL)
    c.shape(rounded_rect_d(6, 30, 88, 44, 10), P.METAL_PALE, sw=2.6, light=(-3, -3), shade_k=0.86)
    c.path(rounded_rect_d(12, 36, 76, 32, 6), P.CHARCOAL, 1.8)
    c.shape("M24,42 H32 V48 H38 V56 H32 V62 H24 V56 H18 V48 H24 Z", P.METAL_DARK, sw=1.8, light=(-1, -1))
    c.path(rounded_rect_d(43, 54, 7, 4, 2), P.METAL_DARK, 1.2)
    c.path(rounded_rect_d(53, 54, 7, 4, 2), P.METAL_DARK, 1.2)
    c.shape(ellipse_d(68, 56, 5.5, 5.5), P.RED, sw=1.8, light=(-1, -1))
    c.shape(ellipse_d(80, 48, 5.5, 5.5), P.RED, sw=1.8, light=(-1, -1))


@doodle_drawing
def speaker(c: Canvas) -> None:
    """A beige desktop speaker, the kind that hummed."""
    c.shape(rounded_rect_d(24, 6, 52, 88, 6), P.BEIGE, sw=2.6, light=(-3, -3), shade_k=0.86)
    c.shape(ellipse_d(50, 30, 14, 14), P.CHARCOAL, sw=2.2, light=(-2, -2), shade_k=0.7)
    c.path(ellipse_d(50, 30, 5, 5), P.METAL_DARK, 1.6)
    c.shape(ellipse_d(50, 64, 19, 19), P.CHARCOAL, sw=2.2, light=(-2, -2), shade_k=0.7)
    c.path(ellipse_d(50, 64, 11, 11), "none", 1.6, P.METAL_DARK)
    c.path(ellipse_d(50, 64, 5, 5), P.METAL_DARK, 1.6)
    _led(c, 32, 88, P.GREEN, 2)
    c.line("M82,24 q6,6 0,12 M88,18 q12,12 0,24", 2.2)


# ============================================================================ on every developer's desk
@doodle_drawing
def mug(c: Canvas) -> None:
    """A mug of something hot: the fuel."""
    c.line("M36,24 q-6,-8 0,-14 M50,22 q-6,-9 0,-16 M64,24 q-6,-8 0,-14", 2.6, P.METAL_DARK)
    c.path("M72,48 Q94,46 92,62 Q90,78 70,76", "none", 9)
    c.path("M72,48 Q94,46 92,62 Q90,78 70,76", "none", 4, P.CARD)
    c.shape("M20,32 H76 V78 Q76,92 62,92 H34 Q20,92 20,78 Z", P.CARD, sw=2.6, light=(-3, -3), shade_k=0.88,
            stipple=(58, 40, 16, 46, 10, "right"))
    c.shape(ellipse_d(48, 32, 28, 7), P.FEATHER_DARK, sw=2.4, light=None)
    c.line("M32,31 q8,-3 16,0", 1.8, P.FEATHER_LIGHT)
    c.line("M36,54 l8,7 l-8,7 M50,68 h12", 3.4, P.TEAL)                     # a prompt printed on the mug


@doodle_drawing
def duck(c: Canvas) -> None:
    """A rubber duck: explain the problem to it and the answer appears."""
    c.shape("M14,62 Q14,46 30,48 Q40,50 46,56 Q52,40 44,32 Q40,14 60,12 Q82,12 82,32 Q82,46 70,50 "
            "Q88,58 86,74 Q84,92 56,92 H40 Q14,92 14,62 Z", P.SUN, sw=2.6, light=(-4, -4), shade_k=0.86,
            highlight="M52,22 Q48,28 49,36")
    c.shape("M80,28 Q96,28 96,36 Q92,42 80,40 Z", P.ORANGE, sw=2.4, light=(-1, -2))
    c.line("M81,35 H94", 1.6)
    c.path(ellipse_d(66, 28, 4.6, 5.4), P.WHITE, 1.8)
    c.dot(67.2, 29, 2.4)
    c.line("M30,66 Q44,58 58,68 Q46,78 32,74", 2.2)                         # wing


@doodle_drawing
def bug(c: Canvas) -> None:
    """A bug. The friendly kind, for now."""
    c.line("M30,40 L14,30 M26,56 L8,56 M30,72 L14,84 M70,40 L86,30 M74,56 L92,56 M70,72 L86,84", 3)
    c.line("M42,20 Q38,8 28,8 M58,20 Q62,8 72,8", 2.6)
    c.shape(ellipse_d(50, 26, 15, 12), P.CHARCOAL, sw=2.6, light=(-2, -2), shade_k=0.7)
    c.path(ellipse_d(44, 24, 3.4, 4), P.WHITE, 1.4)
    c.path(ellipse_d(56, 24, 3.4, 4), P.WHITE, 1.4)
    c.dot(44.8, 25, 1.7)
    c.dot(56.8, 25, 1.7)
    c.shape("M24,58 Q24,32 50,32 Q76,32 76,58 Q76,90 50,90 Q24,90 24,58 Z", P.RED, sw=2.6, light=(-4, -4),
            highlight="M33,46 Q30,54 32,62")
    c.line("M50,32 V90", 2.4)
    for x, y, r in ((37, 50, 5), (63, 50, 5), (36, 70, 4.4), (64, 70, 4.4), (44, 82, 3), (56, 82, 3)):
        c.path(ellipse_d(x, y, r, r), P.CHARCOAL, 0)


@doodle_drawing
def coffee(c: Canvas) -> None:
    """A paper cup of coffee to go."""
    c.shape("M24,30 H76 L70,92 H30 Z", P.CARD, sw=2.6, light=(-3, -3), shade_k=0.88)
    c.shape("M27,48 H73 L71,70 H29 Z", P.FEATHER_LIGHT, sw=2, light=(-2, -2))
    c.path(ellipse_d(50, 59, 7, 7), P.CARD, 1.6)
    c.shape("M18,22 Q18,18 22,18 H78 Q82,18 82,22 V30 H18 Z", P.CHARCOAL, sw=2.6, light=(-2, -2), shade_k=0.7)
    c.shape("M30,18 Q30,10 38,10 H62 Q70,10 70,18 Z", P.CHARCOAL, sw=2.4, light=(-2, -2), shade_k=0.7)


@doodle_drawing
def clock(c: Canvas) -> None:
    """An alarm clock: deadlines."""
    c.line("M28,84 L20,94 M72,84 L80,94", 4)
    c.shape(ellipse_d(26, 20, 13, 9), P.RED, sw=2.4, light=(-2, -2))
    c.shape(ellipse_d(74, 20, 13, 9), P.RED, sw=2.4, light=(-2, -2))
    c.line("M50,10 V18", 4)
    c.shape(ellipse_d(50, 54, 36, 36), P.RED, sw=2.6, light=(-4, -4))
    c.shape(ellipse_d(50, 54, 27, 27), P.CARD, sw=2.2, light=None)
    c.line("M50,30 v5 M50,73 v5 M26,54 h5 M69,54 h5", 2)
    c.line("M50,54 L50,38 M50,54 L62,60", 3.2)
    c.dot(50, 54, 2.8)


# ============================================================================ messages (contact cards)
@doodle_drawing
def star(c: Canvas) -> None:
    """A fat five-pointed star with a shine: a star on a repository."""
    points = []
    for i in range(10):
        radius = 44 if i % 2 == 0 else 19
        angle = math.radians(-90 + i * 36)
        points.append(f"{n(50 + radius * math.cos(angle))},{n(54 + radius * math.sin(angle))}")
    c.shape("M" + " L".join(points) + " Z", P.YELLOW, sw=2.8, light=(-3, -3))
    c.line("M38,34 Q42,28 48,26", 3, P.WHITE, 0.7)


@doodle_drawing
def plane(c: Canvas) -> None:
    """A paper plane: a message on its way."""
    c.line("M10,86 q12,-2 18,-12 M28,96 q10,-2 14,-10", 2.4)
    c.shape("M6,48 L94,8 L70,90 L48,62 Z", P.SKY_DEEP, sw=2.6, light=(-3, -3))
    c.shape("M48,62 L94,8 L40,54 L42,82 Z", P.WHITE, sw=2.4, light=None)
    c.line("M40,54 L94,8", 2)


@doodle_drawing
def megaphone(c: Canvas) -> None:
    """A megaphone: said out loud, to everyone."""
    c.line("M80,26 l12,-9 M84,48 h14 M80,70 l12,9", 2.8)
    c.shape("M28,62 L44,66 L46,88 H32 Z", P.METAL_DARK, sw=2.4, light=(-2, -2))
    c.shape("M18,38 L60,18 L64,78 L20,62 Z", P.PINK, sw=2.6, light=(-3, -3))
    c.shape(ellipse_d(64, 48, 10, 30), P.PINK_PALE, sw=2.6, light=None)
    c.path(ellipse_d(64, 48, 4, 13), P.PINK, 1.8)
    c.shape(rounded_rect_d(6, 38, 15, 24, 5), P.METAL, sw=2.4, light=(-2, -2))


@doodle_drawing
def envelope(c: Canvas) -> None:
    """A letter with a wax seal."""
    c.shape(rounded_rect_d(8, 22, 84, 58, 6), P.CREAM, sw=2.6, light=(-3, -3), shade_k=0.9)
    c.line("M10,78 L38,50 M90,78 L62,50", 1.9)
    c.shape("M10,26 L50,58 L90,26 Q90,22 86,22 H14 Q10,22 10,26 Z", P.CARD, sw=2.4, light=None)
    c.shape(ellipse_d(50, 56, 9, 9), P.RED, sw=2.2, light=(-2, -2))
    c.line("M46,56 l3,3 l5,-6", 2, P.WHITE)


@doodle_drawing
def globe(c: Canvas) -> None:
    """A globe on a stand: the web."""
    c.shape("M36,90 H64 L60,82 H40 Z", P.CHARCOAL, sw=2.2, light=None)
    c.line("M50,82 V76", 4)
    c.shape(ellipse_d(50, 42, 36, 36), P.SKY_DEEP, sw=2.6, light=(-4, -4))
    c.shape("M30,22 Q44,18 48,30 Q44,42 34,40 Q24,34 30,22 Z M56,44 Q70,40 76,52 Q72,66 60,64 Q52,56 56,44 Z",
            P.LEAF, sw=1.8, light=None)
    c.line("M14,42 H86 M50,6 Q28,42 50,78 M50,6 Q72,42 50,78", 1.6, opacity=0.55)
    c.line("M26,26 Q30,16 42,12", 3, P.WHITE, 0.6)


DOODLES = tuple(_DRAWINGS)

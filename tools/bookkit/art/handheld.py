"""Small things a character holds, drawn to be gripped: each has its handle or edge where the fist closes.

Every maker here is `make(x, y, k, ...) -> svg` in the grip frame of `rig` (see its docstring): the fist closes at
(x, y); the gripped handle or edge runs up and down through it; +x points along the forearm, out past the
knuckles, so a flat thing held by its edge spreads that way; "up" (-y) is the thumb's side. `k` is the holder's
height over 100, so a pencil 14 long is about a seventh of the one who holds it. The fist covers about 2.5 either
side of (x, y), so whatever is held there disappears under the fingers.

Hand them to a character:

    characters.draw("cat", "present", hold={"right": handheld.stopwatch})       # on its own canvas
    s.cast("cat", 0.7, "present", hold={"right": (handheld.card, -20)})          # in a strip, turned 20 back
    s.hold(box, handheld.caliper)                                # into one already standing (Stage.hold)

A maker with options is passed as a lambda: `lambda x, y, k: handheld.book(x, y, k, P.RED)`.
"""
from __future__ import annotations

from .. import design as P
from ..design import darken, lighten
from .ink import INK, Canvas, ellipse_d, lettering, lettering_width, n, rounded_rect_d


def _at(c: Canvas, x: float, y: float, k: float) -> str:
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def stopwatch(x: float, y: float, k: float) -> str:
    """A stopwatch lying in the palm, its middle at (x, y), dial to the viewer: a steel case, the crown with its
    start button on top (where the thumb presses), a small lap button beside it, a white dial with a red hand.
    It is held as people hold one, not sitting on its ring above the fist, so it says
    `grasp = "palm"` and `rig.hold` lays it in the hand instead of passing a handle through the fist."""
    c = Canvas()
    c.shape(rounded_rect_d(-0.8, -6.1, 1.6, 1.6, 0.3), P.METAL_DARK, sw=0.45, light=None)      # the stem
    c.shape(rounded_rect_d(-1.5, -7.4, 3, 1.6, 0.6), P.METAL, sw=0.5, light=None)              # the start button
    c.add('<g transform="rotate(40)">')
    c.shape(rounded_rect_d(-0.6, -5.6, 1.2, 1.4, 0.3), P.METAL, sw=0.4, light=None)            # the lap button
    c.add("</g>")
    c.shape(ellipse_d(0, 0, 4.6, 4.6), P.METAL_LIGHT, sw=0.75, light=(-0.5, -0.5))
    c.add(f'<circle cx="0" cy="0" r="3.4" fill="{P.CARD}" stroke="{INK}" stroke-width=".4"/>')
    c.line(" ".join(f"M{n(dx * 3.4)},{n(dy * 3.4)} l{n(-dx * 0.75)},{n(-dy * 0.75)}"
                    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0))), 0.38)
    c.line("M0,0 L1.6,-2.4", 0.5, P.RED)
    c.dot(0, 0, 0.45)
    return _at(c, x, y, k)


stopwatch.grasp = "palm"
stopwatch.radius = 4.6
stopwatch.top = 6.6


def pencil(x: float, y: float, k: float) -> str:
    """A pencil through the fist, its point out under the little finger (+y), the eraser over the thumb."""
    c = Canvas()
    c.shape("M-0.9,-6 H0.9 V8 H-0.9 Z", P.YELLOW, sw=0.5, light=None)
    c.shape("M-0.9,-7.6 H0.9 V-6 H-0.9 Z", P.METAL, sw=0.4, light=None)
    c.shape("M-0.9,-9 Q0,-9.6 0.9,-9 V-7.6 H-0.9 Z", P.PINK, sw=0.4, light=None)
    c.shape("M-0.9,8 L0,11.4 L0.9,8 Z", P.WOOD_PALE, sw=0.4, light=None)
    c.path("M-0.35,10.1 L0,11.4 L0.35,10.1 Z", INK, 0.2)
    return _at(c, x, y, k)


def card(x: float, y: float, k: float, color: str = P.CARD) -> str:
    """An index card or a document held up by its lower corner: the fist pinches it there, the card spreads out
    past the knuckles and up; a title line and three ruled lines on it."""
    c = Canvas()
    c.shape(rounded_rect_d(-1.5, -12.5, 17, 14, 0.8), color, sw=0.6, light=None)
    c.shape(rounded_rect_d(3.5, -10.6, 8, 2.4, 0.6), P.YELLOW_PALE, sw=0.4, light=None)
    c.line("M3.5,-6 H13.5 M3.5,-3.6 H12 M3.5,-1.2 H10", 0.4, INK, 0.6)
    return _at(c, x, y, k)


def sheet(x: float, y: float, k: float) -> str:
    """A sheet of paper held by its lower corner, its top corner curling over; ruled lines on it."""
    c = Canvas()
    c.shape("M-1.5,2 V-22 H12.5 L17.5,-17 V2 Z", P.WHITE, sw=0.6, light=None)
    c.path("M12.5,-22 V-17 H17.5 Z", P.CARD, 0.5)
    c.line(" ".join(f"M3,{n(-16 + i * 3.2)} H{n(14.5 - (4 if i % 3 == 2 else 0))}" for i in range(5)), 0.4, INK,
           0.55)
    return _at(c, x, y, k)


def book(x: float, y: float, k: float, color: str = P.TEAL) -> str:
    """A closed book held up by the lower end of its spine: the spine in the fist, the cover spreading out past the
    knuckles, a label on it, the page block showing along the top."""
    c = Canvas()
    c.shape("M0,-17.4 H13.2 V-16 H0 Z", P.CARD, sw=0.4, light=None)                                   # the pages
    c.shape(rounded_rect_d(-1.6, -16.8, 15.4, 19, 0.9), color, sw=0.7, light=(-0.6, -0.6))            # the cover
    c.shape(rounded_rect_d(-1.6, -16.8, 3, 19, 0.9), darken(color, 0.75),
            sw=0.5, light=None)                                                                      # the spine
    c.shape(rounded_rect_d(4.2, -13, 7, 4, 0.5), P.CARD, sw=0.4, light=None)                          # the label
    c.line("M5.2,-11.6 H10.2 M5.2,-10.2 H8.6", 0.35, INK, 0.6)
    return _at(c, x, y, k)


def clipboard(x: float, y: float, k: float) -> str:
    """A clipboard held by its lower corner: the hardboard, the metal clip at the top, a ruled sheet under it with
    a tick by two lines."""
    c = Canvas()
    c.shape(rounded_rect_d(-1.5, -20.5, 17, 23, 1.2), P.WOOD, sw=0.7, light=(-0.6, -0.6))
    c.shape(rounded_rect_d(0.2, -18, 13.6, 18.6, 0.4), P.WHITE, sw=0.4, light=None)
    c.shape(rounded_rect_d(3.6, -21.8, 6.8, 3.4, 0.9), P.METAL_LIGHT, sw=0.5, light=None)
    c.line(" ".join(f"M4.2,{n(-14 + i * 3)} H12" for i in range(4)), 0.4, INK, 0.55)
    c.line("M1.4,-14.4 l0.7,0.8 l1.2,-1.6 M1.4,-11.4 l0.7,0.8 l1.2,-1.6", 0.45, P.GREEN)
    return _at(c, x, y, k)


def caliper(x: float, y: float, k: float) -> str:
    """A vernier caliper held by its beam: the steel beam runs up through the fist with its scale, the fixed jaw at
    the top and the sliding jaw below it point out past the knuckles, the thumb wheel on the slider."""
    c = Canvas()
    c.shape("M-1.2,6 V-21 H1.2 V6 Z", P.METAL_LIGHT, sw=0.5, light=None)                        # the beam
    c.line(" ".join(f"M-1.2,{n(-19.5 + i * 1.4)} h{1.1 if i % 5 == 0 else 0.6}" for i in range(14)), 0.25)
    c.shape("M-1.2,-21 H8.5 L9.2,-19.4 H1.2 V-18.6 H-1.2 Z", P.METAL, sw=0.5, light=None)        # the fixed jaw
    c.shape("M-2,-14.4 H1.8 V-13 H8.5 L9.2,-11.6 H1.8 V-9.4 H-2 Z", P.METAL, sw=0.5, light=None)   # the slider
    c.add(f'<circle cx="-2.6" cy="-9.4" r="1" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width=".35"/>')
    return _at(c, x, y, k)


def magnifier(x: float, y: float, k: float) -> str:
    """A magnifying glass: its wooden handle through the fist, the lens in its ring above the thumb."""
    c = Canvas()
    c.shape(rounded_rect_d(-1.1, -6, 2.2, 10.5, 1), P.WOOD_DARK, sw=0.5, light=None)
    c.shape("M-0.8,-7.4 H0.8 V-5.6 H-0.8 Z", P.METAL, sw=0.4, light=None)
    c.add(f'<circle cx="0" cy="-12.6" r="5.4" fill="{P.LENS}" fill-opacity=".8" stroke="{INK}" '
          f'stroke-width="1.1"/>')
    c.line("M-3,-14.4 A3.4,3.4 0 0 1 -0.6,-16.4", 0.6, P.WHITE)
    return _at(c, x, y, k)


def notebook(x: float, y: float, k: float, color: str = P.TEAL) -> str:
    """A spiral notebook held open by its lower corner: a coloured top band with the spiral, ruled lines."""
    c = Canvas()
    c.shape(rounded_rect_d(-1.5, -18, 15, 20, 0.8), P.CARD, sw=0.6, light=None)
    c.shape(rounded_rect_d(-1.5, -18, 15, 3.4, 0.8), color, sw=0.5, light=None)
    c.line(" ".join(f"M{n(0.6 + i * 2.4)},-19.2 v2.4" for i in range(6)), 0.45, P.METAL_DARK)
    c.line(" ".join(f"M2.4,{n(-11 + i * 3)} H{n(11.5 - (3 if i == 3 else 0))}" for i in range(4)), 0.4, INK, 0.55)
    return _at(c, x, y, k)


def jar(x: float, y: float, k: float, label: str | None = None, size: float = 2.6, fill: str = P.ORANGE,
        lid: str = P.RED, mirrored: bool = False) -> str:
    """A glass jar gripped round its body: the fist closes about its middle, the coloured lid above the thumb, what
    is in it seen through the glass, and - `label` - a white paper label with its name above the fingers, its
    lettering `size` in the jar's own units (the jar widens to keep the label off its edges); `mirrored` - held by a
    character drawn mirrored, the lettering turned back so it still reads."""
    c = Canvas()
    lw = lettering_width(label, size, "label") + 2 if label else 0.0
    half = max(6.5, lw / 2 + 1.5)
    lab_h = size * 1.45
    top = -8.4 - lab_h                                   # the glass's top: room for the label over the fist
    c.shape(rounded_rect_d(-half, top, 2 * half, 5 - top, 2.4), lighten(P.LENS, 0.45), sw=0.8, light=None)
    c.add(f'<rect x="{n(-half + 1.1)}" y="-6.5" width="{n(2 * half - 2.2)}" height="10.4" rx="1.6" fill="{fill}" '
          f'fill-opacity=".75"/>')
    c.shape(rounded_rect_d(-half + 0.5, top - 2.6, 2 * half - 1, 3, 0.8), lid, sw=0.7, light=None)   # the lid
    c.line(f"M{n(-half + 1.9)},{n(top + 1.4)} V2", 0.5, P.WHITE, 0.8)
    if label:
        c.add(f'<rect x="{n(-lw / 2)}" y="{n(top + 1.4)}" width="{n(lw)}" height="{n(lab_h)}" rx="0.8" '
              f'fill="{P.WHITE}" stroke="{INK}" stroke-width=".4"/>')
        text = lettering(0, top + 1.4 + lab_h / 2 + size * 0.36, label, size, INK, style="label")
        c.add(f'<g transform="scale(-1,1)">{text}</g>' if mirrored else text)
    return _at(c, x, y, k)

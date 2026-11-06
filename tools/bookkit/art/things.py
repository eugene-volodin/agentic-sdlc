"""Small things for the worlds and the opener stories: a kitchen table, an envelope, a wall clock.

Like `props` and `sets`: `thing(x, y, k, ...) -> str`, the origin where the thing touches the ground (or, for
things on a wall, as the docstring says), drawn for a 137-unit professor at k = 1.
"""
from __future__ import annotations

import math

from .. import design as P
from .ink import INK, Canvas, ellipse_d, n, rounded_rect_d
from .sets import _at


def kitchen_table(x: float, y: float, k: float = 1.0, w: float = 110, color: str = P.WOOD_LIGHT,
                  cloth: str | None = P.RED) -> str:
    """A small table 46 high; `cloth` hangs a checked tablecloth over it."""
    c = Canvas()
    hw = w / 2
    c.line(f"M{-hw + 8},0 V-42 M{hw - 8},0 V-42", 4.5, P.WOOD_DARK)
    c.shape(rounded_rect_d(-hw, -48, w, 8, 2), color, sw=2, light=None)
    if cloth:
        clip = c.shape(f"M{-hw - 4},-48 H{hw + 4} V-30 Q{hw},-26 {hw - 8},-30 Q0,-24 {-hw + 8},-30 Q{-hw},-26 "
                       f"{-hw - 4},-30 Z", P.WHITE, sw=1.8, light=None, clip=True)
        checks = "".join(f'<rect x="{-hw - 4 + i * 10}" y="-50" width="5" height="26" fill="{cloth}" opacity=".7"/>'
                         for i in range(int(w / 10) + 2))
        c.add(f'<g clip-path="url(#{clip})">{checks}<rect x="{-hw - 4}" y="-41" width="{w + 8}" height="4" '
              f'fill="{cloth}" opacity=".5"/></g>')
        c.path(f"M{-hw - 4},-48 H{hw + 4} V-30 Q{hw},-26 {hw - 8},-30 Q0,-24 {-hw + 8},-30 Q{-hw},-26 "
               f"{-hw - 4},-30 Z", "none", 1.8)
    return _at(c, x, y, k)


def envelope(x: float, y: float, k: float = 1.0, turn: float = 0) -> str:
    """A sealed letter standing on its bottom edge."""
    c = Canvas()
    c.shape("M-12,0 V-16 H12 V0 Z", P.CARD, sw=1.4, light=None)
    c.line("M-12,-16 L0,-7 L12,-16", 1.2)
    c.add(f'<circle cx="0" cy="-7" r="2.6" fill="{P.RED}" stroke="{INK}" stroke-width=".8"/>')
    return _at(c, x, y, k, turn=turn)


def wall_clock(x: float, y: float, k: float = 1.0) -> str:
    """A round wall clock; the origin is its centre."""
    c = Canvas()
    c.shape(ellipse_d(0, 0, 24, 24), P.WOOD, sw=2, light=None)
    c.shape(ellipse_d(0, 0, 19, 19), P.CARD, sw=1.6, light=None)
    for i in range(12):
        a = math.radians(i * 30)
        c.line(f"M{n(math.sin(a) * 15)},{n(-math.cos(a) * 15)} L{n(math.sin(a) * 17)},{n(-math.cos(a) * 17)}", 1.2)
    c.line("M0,0 L0,-11 M0,0 L8,4", 2)
    c.dot(0, 0, 2)
    return _at(c, x, y, k)

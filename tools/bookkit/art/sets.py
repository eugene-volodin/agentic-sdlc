"""Scenery shared by the worlds and their openers: a window, the sky, hills, stars, a balloon, a podium.

Like `props`, every function is `thing(x, y, scale, ...) -> str`, an SVG group whose origin is where the
object touches the ground (or, for things on a wall, its top centre, as each docstring says). The house style
is the same: ink outline with round joins, cel shading from the top left, stipple in the shadows.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import lighten
from .ink import INK, Canvas, lettering, n, rounded_rect_d
from .props import _at


def _label(c: Canvas, x: float, y: float, text: str, size: float, fill: str = INK, anchor: str = "middle",
           turn: float = 0, style: str = "sign") -> None:
    """Lettering in a drawing: a sign, a label, a number (see `ink.lettering`); every drawing letters alike."""
    c.add(lettering(x, y, text, size, fill, anchor, turn, style=style))


LETTERING_MIN = 9.5    # the smallest lettering drawn in a picture, in units of the page (about 2.4 mm)


# ============================================================================ rooms
def window_morning(x: float, y: float, w: float, h: float) -> str:
    """A tall window onto a sunrise over the town; the origin is its top centre."""
    c = Canvas()
    hw = w / 2
    c.shape(f"M{-hw - 10},-8 H{hw + 10} V{h + 10} H{-hw - 10} Z", P.CARD, sw=2.6, light=None)
    sky = c.gradient([(0, P.SKY_DEEP), (0.55, P.PINK_PALE), (1, P.YELLOW_PALE)], 0, 0, 0, h)
    clip = c.shape(f"M{-hw},0 H{hw} V{h} H{-hw} Z", sky, sw=0, light=None, clip=True)
    inner = Canvas()
    inner.add(f'<circle cx="{n(hw * 0.25)}" cy="{n(h * 0.80)}" r="{n(w * 0.16)}" fill="{P.SUN}" stroke="{INK}" '
              f'stroke-width="2.2"/>')
    for a in range(200, 345, 18):
        x1, y1 = hw * 0.25 + math.cos(math.radians(a)) * w * 0.21, h * 0.8 + math.sin(math.radians(a)) * w * 0.21
        x2, y2 = hw * 0.25 + math.cos(math.radians(a)) * w * 0.28, h * 0.8 + math.sin(math.radians(a)) * w * 0.28
        inner.line(f"M{n(x1)},{n(y1)} L{n(x2)},{n(y2)}", 2, P.AMBER)
    # Roofs of the town, a church dome and chimneys with smoke.
    roofs = (f"M{-hw},{n(h * 0.86)} L{-hw * 0.8},{n(h * 0.74)} L{-hw * 0.56},{n(h * 0.86)} V{n(h * 0.78)} "
             f"H{-hw * 0.3} V{n(h * 0.68)} H{-hw * 0.12} V{n(h * 0.84)} L{hw * 0.05},{n(h * 0.75)} "
             f"L{hw * 0.22},{n(h * 0.86)} H{hw * 0.4} V{n(h * 0.72)} Q{hw * 0.55},{n(h * 0.62)} "
             f"{hw * 0.7},{n(h * 0.72)} "
             f"V{n(h * 0.88)} L{hw * 0.85},{n(h * 0.79)} L{hw},{n(h * 0.88)} V{h} H{-hw} Z")
    inner.shape(roofs, lighten(P.VIOLET, 0.35), sw=1.8, light=(-2, -2), shade_k=0.9)
    for wx, wy in ((-0.24, 0.74), (-0.2, 0.8), (0.48, 0.78), (0.6, 0.78), (-0.72, 0.9)):
        inner.add(f'<rect x="{n(hw * wx)}" y="{n(h * wy)}" width="5" height="7" fill="{P.SUN}" '
                  f'stroke="{INK}" stroke-width="1"/>')
    inner.line(f"M{-hw * 0.21},{n(h * 0.66)} q-8,-14 4,-24 q10,-10 0,-24", 2, P.WHITE, 0.8)
    inner.line(f"M{hw * 0.12},{n(h * 0.55)} q8,-6 16,0 q8,-6 16,0", 1.6)
    inner.line(f"M{-hw * 0.6},{n(h * 0.3)} q6,-5 12,0 q6,-5 12,0", 1.6)
    inner.add(f'<path d="M{-hw * 0.7},{n(h * 0.16)} q8,-10 22,-6 q8,-10 22,-2 q12,0 10,10 Z" fill="{P.WHITE}" '
              f'opacity=".85"/>')
    c.add(f'<g clip-path="url(#{clip})">{inner.render()}</g>')
    c.path(f"M{-hw},0 H{hw} V{h} H{-hw} Z", "none", 2.4)
    c.line(f"M0,0 V{h} M{-hw},{n(h * 0.42)} H{hw}", 4.2, P.CARD)
    c.line(f"M0,0 V{h} M{-hw},{n(h * 0.42)} H{hw}", 1.2)
    c.shape(f"M{-hw - 22},{n(h + 6)} H{hw + 22} V{n(h + 20)} H{-hw - 22} Z", P.WOOD_LIGHT, sw=2.3, light=None)
    # Curtains gathered at the sides, a rail on top.
    for side in (-1, 1):
        d = (f"M{n(side * (hw + 24))},-14 H{n(side * (hw - 18))} Q{n(side * (hw - 4))},{n(h * 0.45)} "
             f"{n(side * (hw + 6))},{n(h * 0.62)} Q{n(side * (hw + 10))},{n(h * 0.8)} {n(side * (hw - 4))},{n(h + 4)} "
             f"H{n(side * (hw + 30))} Z")
        c.shape(d, P.AMBER, sw=2.3, light=(-3, 0))
        c.line(f"M{n(side * (hw + 12))},-10 Q{n(side * (hw + 8))},{n(h * 0.5)} {n(side * (hw + 16))},{n(h)}", 1.2,
               opacity=0.5)
        c.shape(rounded_rect_d(side * (hw + 6) - 9, h * 0.6, 18, 9, 3), P.RED, sw=1.8, light=None)
    c.shape(rounded_rect_d(-hw - 36, -22, w + 72, 9, 4), P.WOOD_DARK, sw=2.2, light=None)
    # A cactus and a watering can on the sill.
    c.shape(f"M{hw * 0.5 - 9},{n(h + 6)} L{hw * 0.5 - 11},{n(h - 10)} H{hw * 0.5 + 11} L{hw * 0.5 + 9},{n(h + 6)} Z",
            P.TERRACOTTA, sw=2, light=(-2, -1))
    c.shape(f"M{hw * 0.5 - 6},{n(h - 10)} Q{hw * 0.5 - 8},{n(h - 42)} {hw * 0.5},{n(h - 44)} "
            f"Q{hw * 0.5 + 8},{n(h - 42)} {hw * 0.5 + 6},{n(h - 10)} Z", P.LEAF, sw=2, light=(-2, -2))
    c.line(f"M{hw * 0.5 - 3},{n(h - 34)} l-3,-2 M{hw * 0.5 + 3},{n(h - 26)} l3,-2 M{hw * 0.5 - 2},{n(h - 18)} l-3,-1",
           1.2)
    return _at(c, x, y)


# ============================================================================ outdoors
def sky(c: Canvas, top_color: str, low_color: str, horizon: float, width: float) -> None:
    """A painted sky, deeper at the top."""
    paint = c.gradient([(0, top_color), (1, low_color)], 0, 0, 0, horizon)
    c.add(f'<rect x="-4" y="-4" width="{n(width + 8)}" height="{n(horizon + 12)}" fill="{paint}"/>')


def hills(c: Canvas, horizon: float, width: float, colors: tuple[str, str], seed: int = 0) -> None:
    """Two ranges of distant hills reaching past both edges."""
    far, near = colors
    c.shape(f"M-14,{n(horizon + 30)} L-14,{n(horizon - 40)} Q{width * .18},{n(horizon - 96)} "
        f"{width * .38},{n(horizon - 46)} "
            f"Q{width * .6},{n(horizon - 110)} {width * .82},{n(horizon - 52)} Q{width * .92},{n(horizon - 70)} "
            f"{width + 14},{n(horizon - 58)} L{width + 14},{n(horizon + 30)} "
            f"Z", far, sw=2, light=(-8, -5), shade_k=0.93)
    rnd = random.Random(seed)
    for _ in range(9):
        x = rnd.uniform(20, width - 20)
        c.add(_fir_far(x, horizon - 40 + 14 * math.sin(x / 70), 0.32))
    c.shape(f"M-14,{n(horizon + 30)} L-14,{n(horizon - 10)} Q{width * .3},{n(horizon - 50)} "
        f"{width * .55},{n(horizon - 12)} "
            f"Q{width * .8},{n(horizon - 40)} {width + 14},{n(horizon - 6)} L{width + 14},{n(horizon + 30)} Z", near,
            sw=2, light=(-8, -5), shade_k=0.93)


def _fir_far(x: float, y: float, scale: float) -> str:
    c = Canvas()
    c.shape("M0,-60 L22,-10 Q0,-4 -22,-10 Z M-4,-8 h8 v10 h-8 Z", P.FIR, sw=2.4, light=(-3, -2))
    return _at(c, x, y, scale)


def hot_air_balloon(x: float, y: float, scale: float = 1.0, colors: tuple = (P.RED, P.YELLOW)) -> str:
    """A striped hot-air balloon; the origin is the bottom of its basket. 140 wide, 210 tall."""
    c = Canvas()
    envelope = "M0,-208 Q70,-208 70,-140 Q70,-96 22,-58 L-22,-58 Q-70,-96 -70,-140 Q-70,-208 0,-208 Z"
    clip = c.shape(envelope, colors[0], sw=0, light=(-6, -6), clip=True)
    stripes = "".join(f'<path d="M{n(-70 + i * 28)},-212 Q{n(-50 + i * 20)},-120 {n(-14 + i * 7)},-50 '
        f'L{n(-4 + i * 7)},-50 '
                      f'Q{n(-36 + i * 20)},-120 {n(-56 + i * 28)},-212 Z" fill="{colors[1]}"/>' for i in range(0, 6, 2))
    c.add(f'<g clip-path="url(#{clip})">{stripes}</g>')
    c.path(envelope, "none", 2.6)
    c.line("M-46,-180 Q-58,-150 -50,-120", 4, P.WHITE, 0.5)
    c.shape("M-22,-58 H22 L18,-48 H-18 Z", P.WOOD_DARK, sw=2, light=None)
    c.line("M-18,-48 L-14,-26 M18,-48 L14,-26 M-6,-48 L-5,-26 M6,-48 L5,-26", 1.4)
    c.shape("M-18,-26 H18 L14,0 H-14 Z", P.WOOD, sw=2.2, light=(-2, -1))
    c.line("M-16,-18 H16 M-15,-9 H15 M-6,-26 V0 M6,-26 V0", 1, opacity=0.6)
    c.shape(rounded_rect_d(-12, 2, 9, 12, 3), P.TERRACOTTA, sw=1.6, light=None)   # a sandbag
    return _at(c, x, y, scale)


def podium(x: float, y: float, scale: float = 1.0) -> str:
    """A winners' podium, places 2-1-3; the origin is the middle of its foot. 180 wide; the tops of the steps
    are 54, 78 and 40 units up."""
    c = Canvas()
    for px, h, place, color in ((-60, 54, "2", P.METAL_LIGHT), (0, 78, "1", P.SUN), (60, 40, "3", P.WOOD_LIGHT)):
        c.shape(f"M{px - 30},0 V{-h} H{px + 30} V0 Z", color, sw=2.4, light=(-3, -3), shade_k=0.86)
        _label(c, px, -h + 30, place, 26, INK)
    return _at(c, x, y, scale)


def stars(c: Canvas, region: tuple, count: int, seed: int = 0) -> None:
    """`count` small four-pointed white stars scattered over `region` (left, top, right, bottom)."""
    rnd = random.Random(seed)
    left, top, right, bottom = region
    for _ in range(count):
        x, y = rnd.uniform(left, right), rnd.uniform(top, bottom)
        r = rnd.uniform(2, 4.5)
        c.add(f'<path d="M{n(x)},{n(y - r)} L{n(x + r * 0.3)},{n(y - r * 0.3)} L{n(x + r)},{n(y)} '
              f'L{n(x + r * 0.3)},{n(y + r * 0.3)} L{n(x)},{n(y + r)} L{n(x - r * 0.3)},{n(y + r * 0.3)} '
              f'L{n(x - r)},{n(y)} '
              f'L{n(x - r * 0.3)},{n(y - r * 0.3)} Z" fill="{P.WHITE}" opacity=".85"/>')

"""The map of the book: a land seen from above at an angle, each chapter a place of its own world by the road.

A map of the book by the contents: every chapter its own land, the last chapter joining all the worlds by a railway,
with the chapters' titles on it and how long each takes to read, so the reader sees the way through the chapters and
what lies ahead. The contents fill their pages, so the map takes a page of its own right after them.

The way runs as a road in four long rows, from the professor's courtyard at the bottom (the introduction), in the
morning, to the computer city under the stars at the top (the conclusion; the city the characters walk off into
on the book's last page, `farewell.py`): the journey of a day. The five characters
walk it. By the road every chapter has a vignette of its world in the chapter's own colour and, in front of the road,
a wooden plaque with its number, its title and its reading time. A chapter not written yet is drawn faint in a mist,
its plaque greyed with "soon", like the greyed rows of the contents. The railway of the last chapter runs along
the bottom edge. The land is countryside: fields of different crops with hedges, meadows with flowers, a river under a
bridge into a pond, a windmill, haystacks, rocks, trees and a forest edge.

Units: the page, 840 x 1188 (4 units to the millimetre). A vignette is drawn in local units standing on (0, 0) and
placed at its stop, scaled to its row (the far rows are smaller). Everything placed has a box on a `Stage`;
`problems()` lists every overlap, every box on the road or the river and every box off the page
(`tests/test_bookmap.py`).
"""
from __future__ import annotations

import math
import random
import re
from collections.abc import Callable
from dataclasses import dataclass, field

from .. import design as P
from ..design import darken, lighten, mix
from .curves import eased_points
from .ink import Canvas, circle_d, ellipse_d, lettering, lettering_width, n, poly_d, rect_d, rounded_rect_d
from .openers import H, W, Box, Stage

SW = 2.4                     # outline in a vignette's local units
HORIZON = 96                 # where the land meets the night sky
EDGE = 8                     # nothing comes nearer the page's edge than this
AIR = 5                      # air between any two things


@dataclass(frozen=True)
class Stop:
    """One entry of the plan: its slot ("intro", "end" or the chapter's number), the number on its plaque, its
    title, its reading time ("" when not written), its colour, its world (None when it has none), and whether it is
    written."""
    slot: str
    label: str
    title: str
    time: str
    color: str
    world: str | None
    written: bool


@dataclass
class BookMap:
    svg: str
    boxes: list[Box] = field(default_factory=list)
    road: list[tuple[float, float, float]] = field(default_factory=list)    # (x, y, half width) along the road
    river: list[tuple[float, float, float]] = field(default_factory=list)   # (x, y, half width) along the river
    drawn: dict[str, str] = field(default_factory=dict)                     # slot -> the vignette drawn there
    plaques: dict[str, list[str]] = field(default_factory=dict)             # slot -> the lines on its plaque


class MapError(ValueError):
    """The plan has a chapter the map has no place or drawing for."""


# ============================================================================ geometry of the way
# The rows of the road, nearest first: (y of the road's middle, scale of what stands by it).
ROWS = ((944, 1.0), (676, 0.92), (418, 0.85), (172, 0.78))
ROAD_HALF = 15               # half the road's width at scale 1
SIDE_R, SIDE_L = 822, 20     # the x of the hairpins on the right and on the left
VIG_H = 124                  # the tallest a vignette stands at scale 1 ...
VIG_W = (186, 226, 226, 226)  # ... and the widest, per row (the first row also has the walkers)
# Where every slot stands: (row, x of the vignette's and the plaque's middle).
SLOTS = {"intro": (0, 104), "1": (0, 500), "2": (0, 700),
         "3": (1, 668), "4": (1, 420), "5": (1, 168),
         "6": (2, 168), "7": (2, 420), "8": (2, 668),
         "9": (3, 668), "10": (3, 420), "end": (3, 168)}
RAILWAY = "11"               # the chapter that joins the worlds: a track along the bottom edge
RAIL_Y = 1168
RAIL_PLAQUE_X = 292          # its plaque: under the walkers, where the first row has no plaque
CAST_X = (204, 384)          # the stretch of the first row the characters walk, between the courtyard and chapter 1
PUDDLES = ((0, 610), (1, 300), (2, 600), (3, 300))   # (row, x) of a puddle on the road
RIVER_X = 546                # the river comes down from the hills between chapters 10 and 9 ...
POND = (544, 244, 32, 14)    # ... under the bridge of the top row, into a pond: centre x, y, radii
PLAQUE_W = 150               # a plaque's width; it never shrinks with distance, so its words always read
TITLE_SIZE = 12.4            # its title's size, set smaller as a whole when the title would not fit in three lines
TITLE_LH = 14.2


def road_line() -> list[tuple[float, float]]:
    """The middle of the road: four rows joined by three hairpins at the sides."""
    (y0, _), (y1, _), (y2, _), (y3, _) = ROWS
    bend = 70          # how far up a hairpin turns before it runs straight
    corners = [(SLOTS["intro"][1] + 28, y0), (SIDE_R, y0), (SIDE_R, y0 - bend), (SIDE_R + 1, y1 + bend),
               (SIDE_R, y1), (SIDE_L, y1), (SIDE_L, y1 - bend), (SIDE_L - 1, y2 + bend), (SIDE_L, y2),
               (SIDE_R, y2), (SIDE_R, y2 - bend), (SIDE_R + 1, y3 + bend), (SIDE_R, y3),
               (SLOTS["end"][1] + 30, y3)]
    return eased_points(corners, step=5)


def river_line() -> list[tuple[float, float]]:
    """The river: out of the far hills, under the bridge of the top row, into the pond."""
    x, (cy, r) = RIVER_X, (POND[1], POND[3])
    return eased_points([(x + 30, HORIZON + 8), (x + 10, 124), (x + 22, 146), (x + 2, 176), (x - 8, 204),
                         (x, cy - r + 2)], step=4)


def half_width(y: float) -> float:
    """The road narrows with distance: its half width at height y on the page."""
    near, far = ROWS[0], ROWS[-1]
    t = max(0.0, min(1.0, (near[0] - y) / (near[0] - far[0])))
    return ROAD_HALF * (near[1] + (far[1] - near[1]) * t)


def scale_at(y: float) -> float:
    """How big things are drawn at height y: 1 on the first row, smaller towards the horizon."""
    near, far = ROWS[0], ROWS[-1]
    t = (near[0] - y) / (near[0] - far[0])
    return max(0.62, min(1.04, near[1] + (far[1] - near[1]) * t))


# ============================================================================ small shapes
def _frange(a: float, b: float, step: float):
    x = a
    while x < b:
        yield x
        x += step


def _shadow(c: Canvas, w: float, depth: float = 8, x: float = 0) -> None:
    c.add(f'<path d="{ellipse_d(x, -1, w / 2, depth)}" fill="{P.INK}" fill-opacity=".14"/>')


def _window(c: Canvas, x: float, y: float, w: float, h: float, lit: bool = False, cross: bool = True) -> None:
    """A window: glass with a glint, or lit warm from inside."""
    c.shape(rect_d(x, y, w, h), P.YELLOW_PALE if lit else P.SKY_LOW, sw=SW * 0.8, light=None)
    if cross:
        c.line(f"M{n(x + w / 2)},{n(y)} V{n(y + h)} M{n(x)},{n(y + h / 2)} H{n(x + w)}", sw=1.3)
    if not lit:
        c.line(f"M{n(x + 3)},{n(y + h - 3)} L{n(x + w * 0.45)},{n(y + 3)}", sw=1.5, stroke=P.WHITE, opacity=0.7)


def _striped(c: Canvas, d: str, a: str, b: str, x0: float, x1: float, step: float, top: float, bottom: float) -> None:
    """A shape in vertical stripes of two colours (a tent), shaded on its right, outlined once."""
    clip = c.shape(d, b, sw=0, clip=True)
    stripes = "".join(rect_d(x, top, step / 2, bottom - top) for x in _frange(x0, x1, step))
    c.add(f'<g clip-path="url(#{clip})"><path d="{stripes}" fill="{a}"/>'
          f'<path d="{d}" fill="{P.INK}" fill-opacity=".12" transform="translate(5,0)"/></g>')
    c.path(d, sw=SW)


def _banded(c: Canvas, d: str, a: str, b: str, top: float, bottom: float, step: float, left: float,
            right: float) -> None:
    """A shape in horizontal bands of two colours (a lighthouse), shaded on its right, outlined once."""
    clip = c.shape(d, b, sw=0, clip=True)
    bands = "".join(rect_d(left, y, right - left, step / 2) for y in _frange(top, bottom, step))
    c.add(f'<g clip-path="url(#{clip})"><path d="{bands}" fill="{a}"/>'
          f'<path d="{rect_d((left + right) / 2 + 4, top, right, bottom - top)}" fill="{P.INK}" '
          f'fill-opacity=".14"/></g>')
    c.path(d, sw=SW)


def _star(cx: float, cy: float, r: float) -> str:
    pts = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return poly_d(pts)


def _sparkle(cx: float, cy: float, r: float) -> str:
    """A four-pointed twinkle of a bright star."""
    k = r * 0.22
    return (f"M{n(cx)},{n(cy - r)} Q{n(cx + k)},{n(cy - k)} {n(cx + r)},{n(cy)} Q{n(cx + k)},{n(cy + k)} "
            f"{n(cx)},{n(cy + r)} Q{n(cx - k)},{n(cy + k)} {n(cx - r)},{n(cy)} Q{n(cx - k)},{n(cy - k)} "
            f"{n(cx)},{n(cy - r)} Z")


def _crescent(cx: float, cy: float, r: float) -> str:
    """A crescent moon opening to the left."""
    return (f"M{n(cx)},{n(cy - r)} A{n(r)},{n(r)} 0 1 1 {n(cx)},{n(cy + r)} "
            f"A{n(r * 0.78)},{n(r)} 0 1 0 {n(cx)},{n(cy - r)} Z")


def _water(c: Canvas, d: str, left: float, right: float, top: float, bottom: float) -> str:
    """A patch of water with a sandy rim and ripples; returns its clip id."""
    c.path(d, fill=P.SAND, sw=SW + 7, stroke=P.INK)
    c.path(d, fill=P.SAND, sw=7, stroke=P.SAND)
    clip = c.shape(d, P.WATER, sw=SW * 0.7, light=None, clip=True)
    rnd = random.Random(int(left * 3 + top))
    ripples = [f"M{n(rnd.uniform(left + 10, right - 50))},{n(y)} q7,-4 14,0 t14,0"
               for y in _frange(top + 10, bottom - 4, 11)]
    c.add(f'<g clip-path="url(#{clip})"><path d="{" ".join(ripples)}" fill="none" stroke="{P.WATER_LIGHT}" '
          f'stroke-width="2.2" stroke-linecap="round"/></g>')
    return clip


def _smoke(c: Canvas, x: float, y: float, k: float = 1.0) -> None:
    """Three puffs of smoke rising to the right from (x, y)."""
    for i, (dx, dy, r) in enumerate(((0, 0, 6), (8, -9, 7.5), (19, -15, 5.5))):
        c.shape(ellipse_d(x + dx * k, y + dy * k, r * k, r * k * 0.8), P.WHITE, sw=1.7, shade_k=0.92 if i else 0.9)


def _bubbles(c: Canvas, points) -> None:
    for x, y, r in points:
        c.add(f'<path d="{circle_d(x, y, r)}" fill="{P.WHITE}" fill-opacity=".8" stroke="{P.INK}" '
              f'stroke-width="1.2"/>')


def _fir(c: Canvas, x: float, h: float, ground: float = 0, color: str = P.FIR) -> None:
    """A fir tree of height h standing at x."""
    c.shape(rect_d(x - 2.5, ground - h * 0.16, 5, h * 0.16), P.TRUNK, sw=1.5, light=None)
    for i, k in enumerate((1.0, 0.8, 0.6)):
        base = ground - h * 0.12 - h * i * 0.25
        c.shape(poly_d([(x - h * 0.24 * k, base), (x, base - h * 0.45), (x + h * 0.24 * k, base)]), color, sw=1.7)


# ============================================================================ the vignettes
# Each draws one world, in its chapter's colour, standing on (0, 0); `EXTENT` is its box in local units:
# (left, top, right), the bottom being 0. It is scaled at its stop to fit the row's height and width.
Vignette = Callable[[Canvas, str], None]
VIGNETTES: dict[str, Vignette] = {}
EXTENT: dict[str, tuple[float, float, float]] = {}


def vignette(name: str, left: float, top: float, right: float):
    def register(fn: Vignette) -> Vignette:
        VIGNETTES[name], EXTENT[name] = fn, (left, top, right)
        return fn
    return register


@vignette("kitchen", -94, -150, 106)
def kitchen(c: Canvas, accent: str) -> None:
    """Chapter 1: the kitchen - a cottage baking a pie (on the sill, steam rising), smoke from the chimney, a
    vegetable garden with cabbages behind a little fence, a basket of apples by the door."""
    _shadow(c, 200, x=6)
    c.shape(rect_d(2, -116, 14, 36), P.TERRACOTTA, sw=SW)                  # the chimney, behind the roof
    c.shape(rect_d(-1, -120, 20, 7), darken(P.TERRACOTTA, 0.9), sw=SW)
    _smoke(c, 12, -128)
    c.shape(rect_d(-80, -74, 104, 74), P.KITCHEN_WALL, sw=SW)                # the walls
    c.line("M-80,-50 H24 M-80,-26 H24", sw=1, stroke=darken(P.KITCHEN_WALL, 0.85))
    c.shape(poly_d([(-94, -70), (-28, -126), (38, -70)]), accent, sw=SW)     # the roof in the chapter's colour
    c.line("M-80,-82 L24,-82 M-64,-96 L8,-96 M-48,-110 L-8,-110", sw=1.3, stroke=darken(accent, 0.7))
    c.shape(ellipse_d(-28, -92, 8, 8), P.YELLOW_PALE, sw=1.8, light=None)   # a lit round window under the ridge
    c.line("M-36,-92 H-20 M-28,-100 V-84", sw=1.1)
    c.shape(rect_d(-70, -48, 22, 48), P.WOOD, sw=SW)                         # the door
    c.dot(-52, -24, 2)
    c.shape("M-44,-10 L-42,0 H-26 L-24,-10 Z", P.KITCHEN_KRAFT, sw=1.6)     # a basket of apples by the door
    for x in (-40, -34, -28):
        c.shape(circle_d(x, -12, 3.4), P.RED, sw=1.2, light=None)
    c.shape(rect_d(-36, -60, 50, 34), P.KITCHEN_CABINET, sw=SW * 0.8, light=None)   # the window, shutters open
    _window(c, -30, -57, 38, 28, lit=True)
    c.shape(rect_d(-40, -27, 58, 6), P.WOOD_LIGHT, sw=SW * 0.9)              # the sill ...
    c.shape("M-25,-27 Q-12,-44 1,-27 Z", P.CRUST, sw=2)                     # ... and the pie on it
    c.line("M-20,-31 L-6,-38 M-16,-36 L-3,-31 M-12,-41 L-12,-28", sw=1.1, stroke=darken(P.CRUST, 0.72))
    c.line("M-17,-48 q-3,-4 0,-8 M-8,-49 q-3,-4 0,-8", sw=1.4, stroke=P.INK, opacity=0.55)   # steam
    c.shape(rect_d(-38, -21, 54, 6), darken(accent, 0.9), sw=1.6, light=None)   # the flower box under it
    for i, x in enumerate((-32, -22, -12, -2, 8)):
        c.shape(circle_d(x, -24, 3.2), (P.SUN, P.WHITE, P.PINK_PALE)[i % 3], sw=1.1, light=None)
    c.shape(rect_d(34, -14, 68, 14), P.FLOOR_DARK, sw=1.8, light=None)       # the vegetable bed ...
    for row, y in enumerate((-10, -4)):
        for x in range(40 + row * 6, 100, 12):
            c.shape(circle_d(x, y - 2, 4.6), P.LEAF_LIGHT, sw=1.2)          # ... of cabbages
    for x in range(30, 108, 9):                                            # behind its little fence
        c.shape(f"M{x},0 V-24 L{x + 3},-28 L{x + 6},-24 V0 Z", P.CARD, sw=1.3, light=None)
    c.line("M28,-8 H106 M28,-18 H106", sw=1.6)


@vignette("fair", -112, -150, 112)
def fair(c: Canvas, accent: str) -> None:
    """Chapter 2: the fair - a Ferris wheel, a striped tent with a pennant, a cart of balloons."""
    _shadow(c, 220)
    cx, cy, r = 52, -84, 54
    c.tube(f"M{cx},{cy} L{cx - 32},0 M{cx},{cy} L{cx + 32},0", P.METAL_DARK, 5, sw=1.8)   # the stand
    for i in range(10):                                                    # the spokes
        a = math.radians(i * 36 + 8)
        c.line(f"M{cx},{cy} L{n(cx + math.cos(a) * r)},{n(cy + math.sin(a) * r)}", sw=1.2)
    c.add(f'<path d="{circle_d(cx, cy, r)}" fill="none" stroke="{P.INK}" stroke-width="9"/>')
    c.add(f'<path d="{circle_d(cx, cy, r)}" fill="none" stroke="{accent}" stroke-width="4.6"/>')
    c.shape(circle_d(cx, cy, 7), P.CREAM, sw=2)
    for i in range(10):                                                    # the cabins, hanging level
        a = math.radians(i * 36 + 8)
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        c.line(f"M{n(x)},{n(y)} V{n(y + 4)}", sw=1.3)
        c.shape(rounded_rect_d(x - 6.5, y + 4, 13, 10, 3), P.BRIGHTS[i % len(P.BRIGHTS)], sw=1.7)
    tent = "M-110,0 L-110,-38 Q-80,-54 -72,-92 Q-64,-54 -34,-38 L-34,0 Z"   # the tent
    _striped(c, tent, accent, P.WHITE, -118, -26, 11, -92, 0)
    c.shape("M-80,0 Q-72,-28 -64,0 Z", darken(accent, 0.55), sw=SW * 0.8, light=None)   # its open flap
    c.line("M-72,-92 V-108", sw=1.8)                                       # the pennant on top
    c.shape("M-72,-108 L-56,-103 L-72,-98 Z", P.RED, sw=1.5, light=None)
    c.shape(rect_d(-22, -24, 30, 18), P.CREAM, sw=1.8)                       # the balloon cart ...
    c.shape(rect_d(-24, -28, 34, 6), accent, sw=1.6, light=None)
    for x in (-16, 2):
        c.shape(circle_d(x, -5, 5), P.CHARCOAL, sw=1.4, light=None)
    for i, (x, y) in enumerate(((-18, -62), (-6, -70), (6, -60), (-28, -54))):   # ... its balloons on strings
        c.line(f"M-7,-28 Q{n((x - 7) / 2)},{n(y + 18)} {x},{y + 8}", sw=1)
        c.shape(ellipse_d(x, y, 7, 8.5), (P.RED, P.SUN, P.TEAL, P.PINK)[i], sw=1.5)


@vignette("station", -112, -138, 112)
def station(c: Canvas, accent: str) -> None:
    """Chapter 3: the space station - in a bubble of night sky on a plinth, a rocket on its pad by its gantry, a
    radar dish and a fuel tank."""
    _shadow(c, 220)
    bx, by, r = -46, -86, 52
    c.shape(poly_d([(bx - 34, 0), (bx - 26, -40), (bx + 26, -40), (bx + 34, 0)]), P.METAL, sw=SW)   # the plinth
    c.line(f"M{bx - 30},-20 H{bx + 30}", sw=1.3, stroke=P.METAL_DARK)
    clip = c.shape(circle_d(bx, by, r), P.SPACE_DEEP, sw=0, light=None, clip=True)
    body = Canvas()
    body.add(f'<path d="{circle_d(bx + 34, by + 44, 40)}" fill="{P.SPACE_LOW}"/>')   # a planet low inside
    rnd = random.Random(3)
    for _ in range(14):
        body.dot(bx + rnd.uniform(-46, 46), by + rnd.uniform(-46, 26), rnd.uniform(0.9, 1.6), P.WHITE)
    for side in (-1, 1):                                                   # the solar wings ...
        x0 = bx + (24 if side > 0 else -46)
        body.shape(rect_d(x0, by - 7, 22, 14), accent, sw=1.7, light=None)
        body.line(f"M{x0 + 7},{by - 7} V{by + 7} M{x0 + 14},{by - 7} V{by + 7} M{x0},{by} H{x0 + 22}", sw=0.9,
                  stroke=darken(accent, 0.6))
    body.line(f"M{bx - 24},{by} H{bx + 24}", sw=2)
    body.shape(rounded_rect_d(bx - 19, by - 8, 38, 16, 7), P.HULL, sw=1.7)  # ... on the long module
    body.shape(circle_d(bx, by - 16, 8.5), P.HULL, sw=1.7)                   # the docking node
    body.dot(bx - 8, by, 2, P.SCREEN_LIGHT)
    body.dot(bx + 4, by, 2, P.SCREEN_LIGHT)
    c.add(f'<g clip-path="url(#{clip})">{body.render()}</g>')
    c.add(f'<path d="M{bx - 34},{by - 26} A42,42 0 0 1 {bx - 6},{by - 44}" fill="none" stroke="{P.WHITE}" '
          f'stroke-width="3.2" stroke-linecap="round" stroke-opacity=".6"/>')   # the glass's glint
    c.path(circle_d(bx, by, r), sw=SW + 0.6)
    px = 40                                                                # the launch pad, the gantry, the rocket
    c.shape(rect_d(px - 22, -9, 46, 9), P.METAL_DARK, sw=SW)
    c.line(f"M{px + 18},-9 V-104 M{px + 18},-34 H{px + 8} M{px + 18},-66 H{px + 8} M{px + 18},-98 H{px + 26}",
           sw=2.2, stroke=P.METAL_DARK)
    c.line(f"M{px + 24},-9 V-104", sw=2.2, stroke=P.METAL_DARK)
    c.line(f"M{px + 18},-20 L{px + 24},-30 M{px + 18},-50 L{px + 24},-60 M{px + 18},-80 L{px + 24},-90", sw=1.4,
           stroke=P.METAL_DARK)
    c.shape(f"M{px - 9},-14 L{px - 9},-72 Q{px - 9},-94 {px},-108 Q{px + 9},-94 {px + 9},-72 L{px + 9},-14 Z",
            P.WHITE, sw=SW)
    c.shape(f"M{px - 9},-72 Q{px - 9},-94 {px},-108 Q{px + 9},-94 {px + 9},-72 Z", accent, sw=SW)
    c.shape(f"M{px - 9},-38 L{px - 19},-12 L{px - 9},-14 Z", accent, sw=1.7, light=None)
    c.shape(f"M{px + 9},-38 L{px + 19},-12 L{px + 9},-14 Z", accent, sw=1.7, light=None)
    c.shape(circle_d(px, -56, 4.2), P.SCREEN_LIGHT, sw=1.5, light=None)
    c.shape(rect_d(80, -26, 26, 26), P.METAL_PALE, sw=1.8)                   # the radar hut and its dish
    c.line("M93,-26 V-40", sw=2.2)
    c.shape("M78,-56 Q88,-36 110,-42 Q98,-52 78,-56 Z", P.WHITE, sw=1.7)
    c.line("M93,-40 L90,-48", sw=1.4)
    c.shape(rect_d(83, -20, 8, 7), P.YELLOW_PALE, sw=1.2, light=None)


@vignette("library", -112, -142, 112)
def library(c: Canvas, accent: str) -> None:
    """Chapter 4: the library - columns, steps, lit windows in its wings, an open book on the pediment, a trolley of
    books by the steps."""
    _shadow(c, 220)
    for x0 in (-98, 62):                                                   # the two wings, lit
        c.shape(rect_d(x0, -74, 36, 66), P.BIRCH, sw=SW)
        _window(c, x0 + 8, -64, 20, 22, lit=True)
        c.shape(rect_d(x0 - 3, -80, 42, 8), accent, sw=1.8, light=None)
    for i, w in enumerate((156, 144, 132)):                                # the steps
        c.shape(rect_d(-w / 2, -7 * (i + 1), w, 7), P.STONE, sw=SW * 0.8, shade_k=0.88)
    c.shape(rect_d(-62, -96, 124, 75), P.BIRCH, sw=SW)                       # the hall
    c.shape("M-13,-21 V-56 Q0,-70 13,-56 V-21 Z", P.WOOD_DARK, sw=SW)      # the arched door
    for x in (-50, -30, 30, 50):                                           # the columns
        c.shape(rect_d(x - 5.5, -92, 11, 71), P.CARD, sw=1.7)
        c.line(f"M{x - 2},-88 V-26 M{x + 2},-88 V-26", sw=0.8, stroke=P.GUIDE)
        c.shape(rect_d(x - 7.5, -96, 15, 5), P.STONE, sw=1.5, light=None)
    c.shape(rect_d(-72, -108, 144, 12), accent, sw=SW)                      # the frieze in the chapter's colour
    c.shape(poly_d([(-78, -108), (0, -142), (78, -108)]), accent, sw=SW)    # the pediment ...
    c.shape("M-20,-118 Q-10,-124 0,-119 Q10,-124 20,-118 L20,-112 Q10,-117 0,-112 Q-10,-117 -20,-112 Z",
            P.CARD, sw=1.5, light=None)                                    # ... with an open book on it
    c.line("M0,-119 V-112", sw=1.1)
    c.shape(rect_d(80, -26, 30, 16), P.WOOD, sw=1.7)                         # the book trolley
    for i, x in enumerate(range(83, 108, 5)):
        c.shape(rect_d(x, -38 + (i % 2) * 3, 4.4, 12 - (i % 2) * 3), P.BRIGHTS[(i + 2) % len(P.BRIGHTS)], sw=1,
                light=None)
    for x in (85, 105):
        c.shape(circle_d(x, -6, 4.5), P.CHARCOAL, sw=1.3, light=None)


@vignette("attic", -108, -150, 112)
def attic(c: Canvas, accent: str) -> None:
    """Chapter 5: the attic workshop - a tall house with a lit round attic window (a gear on the bench inside), a
    ladder up to it, a sawhorse with a plank and a woodpile."""
    _shadow(c, 220)
    c.shape(rect_d(-62, -82, 92, 82), P.WOOD_PALE, sw=SW)                    # the walls
    c.line("M-62,-56 H30 M-62,-28 H30", sw=1, stroke=darken(P.WOOD_PALE, 0.8))
    c.shape(poly_d([(-76, -78), (-16, -140), (44, -78)]), accent, sw=SW)    # the steep roof
    c.line("M-16,-140 V-150 M-24,-147 L-8,-147", sw=1.7)                   # the weathervane
    c.shape("M-8,-150 L0,-147 L-8,-144 Z", P.INK, sw=0, light=None)
    c.shape(circle_d(-16, -104, 14), P.WOOD, sw=SW)                          # the round attic window, lit
    c.shape(circle_d(-16, -104, 10), P.YELLOW_PALE, sw=1.5, light=None)
    teeth = "".join(f"M{n(-16 + math.cos(math.radians(a)) * 4.6)},{n(-104 + math.sin(math.radians(a)) * 4.6)} "
                    f"L{n(-16 + math.cos(math.radians(a)) * 7.8)},{n(-104 + math.sin(math.radians(a)) * 7.8)} "
                    for a in range(0, 360, 45))                            # the gear on the bench inside
    c.line(teeth, sw=2.4, stroke=P.LEAF_DARK)
    c.add(f'<path d="{circle_d(-16, -104, 4.8)}" fill="{P.LEAF_DARK}"/>')
    c.dot(-16, -104, 1.7, P.YELLOW_PALE)
    c.line("M-98,0 L-74,-80 M-88,0 L-64,-80", sw=2.4, stroke=P.WOOD_DARK)   # the ladder up to the eaves
    c.line(" ".join(f"M{n(-98 + t * 24 + 0)},{n(-t * 80)} L{n(-88 + t * 24)},{n(-t * 80)}"
                    for t in (0.15, 0.32, 0.49, 0.66, 0.83)), sw=1.8, stroke=P.WOOD_DARK)
    c.shape(rect_d(-50, -46, 22, 46), P.WOOD, sw=SW)                         # the door
    c.dot(-33, -22, 1.9)
    _window(c, -14, -66, 28, 24, lit=True)
    c.shape(rect_d(46, -32, 52, 7), P.WOOD_LIGHT, sw=1.7)                   # the sawhorse with a plank
    c.line("M52,-25 L46,0 M60,-25 L66,0 M84,-25 L78,0 M92,-25 L98,0", sw=2.8, stroke=P.WOOD_DARK)
    for x, y in ((88, -5), (100, -5), (112, -5), (94, -15), (106, -15)):   # the woodpile: its logs' ends
        c.shape(circle_d(x, y, 5.4), P.WOOD_LIGHT, sw=1.4, light=None)
        c.dot(x, y, 1.2, P.WOOD_DARK)


@vignette("sea", -112, -112, 112)
def sea(c: Canvas, accent: str) -> None:
    """Chapter 6: the undersea base - a glass dome under the water of a bay with bubbles rising, the submarine's
    back and tower with its periscope at the surface, a buoy, reeds on the shore."""
    bay = "M-108,-16 Q-112,-62 -62,-72 Q0,-82 62,-72 Q112,-62 108,-16 Q100,2 0,0 Q-100,2 -108,-16 Z"
    clip = _water(c, bay, -112, 112, -82, 2)
    under = Canvas()
    under.shape("M-48,-10 Q-48,-58 -2,-60 Q44,-58 44,-10 Z", lighten(accent, 0.55), sw=2.1, light=None)
    under.line("M-25,-12 Q-27,-50 -2,-59 M21,-12 Q23,-50 -2,-59 M-2,-60 V-10 M-46,-30 Q-2,-41 42,-30", sw=1.5,
               stroke=darken(accent, 0.7))
    under.dot(-14, -22, 2.6, P.YELLOW_PALE)
    under.dot(10, -22, 2.6, P.YELLOW_PALE)
    under.shape(rect_d(-56, -12, 108, 6), darken(accent, 0.8), sw=1.9, light=None)
    under.add(f'<path d="{rect_d(-120, -90, 240, 100)}" fill="{P.WATER}" fill-opacity=".42"/>')   # the water over it
    c.add(f'<g clip-path="url(#{clip})">{under.render()}</g>')
    c.path(bay, sw=SW * 0.8)
    _bubbles(c, ((-8, -72, 3), (0, -82, 2.4), (-6, -92, 3.2)))             # bubbles up from the dome
    c.shape("M36,-44 Q38,-54 58,-54 L98,-52 Q104,-48 100,-44 Z", accent, sw=SW)   # the submarine's back ...
    c.shape("M56,-52 L58,-74 Q58,-78 63,-78 L78,-78 Q81,-78 80,-74 L76,-52 Z", accent, sw=SW)   # ... its tower ...
    c.line("M64,-78 V-94 H71", sw=2.4)                                     # ... and its periscope
    c.shape(rect_d(70, -98, 7, 7), P.METAL, sw=1.5, light=None)
    c.dot(62, -66, 2.2, P.YELLOW_PALE)
    c.dot(70, -66, 2.2, P.YELLOW_PALE)
    c.line("M30,-43 q8,-4 14,0 M94,-43 q6,-4 10,0", sw=1.7, stroke=P.WHITE)
    c.line("M-70,-42 V-58", sw=1.6)                                        # a buoy
    c.shape("M-78,-38 Q-70,-50 -62,-38 Z", P.RED, sw=1.6, light=None)
    c.shape(rect_d(-77, -42, 14, 4), P.WHITE, sw=1.2, light=None)
    for x, h in ((-104, 30), (-99, 38), (-94, 26), (100, 34), (105, 26)):   # reeds on the shore
        c.line(f"M{x},-10 Q{x - 2},{-10 - h / 2} {x + 1},{-10 - h}", sw=2, stroke=P.LEAF_DARK)
        c.shape(rounded_rect_d(x - 1.6, -10 - h - 9, 5, 10, 2.5), P.WOOD_DARK, sw=1, light=None)


@vignette("lab", -112, -140, 112)
def lab(c: Canvas, accent: str) -> None:
    """Chapter 7: the laboratory - a building with flasks on its lit window sills and steam from its vent, a big flask
    bubbling on a stand, gas cylinders."""
    _shadow(c, 220)
    c.shape(rect_d(-60, -106, 12, 26), P.METAL, sw=SW)                      # the vent on the roof ...
    _smoke(c, -54, -114, 0.9)                                              # ... steaming
    c.shape(rect_d(-106, -84, 118, 84), P.HULL, sw=SW)                       # the building
    c.shape(rect_d(-112, -92, 130, 12), accent, sw=SW)                      # its roof edge in the chapter's colour
    for x in (-96, -56):                                                   # two lit windows with flasks on the sill
        _window(c, x, -72, 32, 28, lit=True, cross=False)
        c.shape(f"M{x + 8},-45 L{x + 8},-53 L{x + 5},-59 H{x + 14} L{x + 11},-53 L{x + 11},-45 Z",
                P.LENS, sw=1.1, light=None)
        c.shape(f"M{x + 17},-45 Q{x + 17},-55 {x + 21},-56 V-63 H{x + 24} V-56 Q{x + 28},-55 {x + 28},-45 Z",
                accent, sw=1.1, light=None)
    c.shape(rect_d(-20, -40, 24, 40), P.METAL_DARK, sw=SW)                   # the door
    c.line("M-8,-40 V0", sw=1.3)
    c.shape(rect_d(22, -8, 52, 8), P.WOOD_DARK, sw=SW)                       # the stand ...
    flask = "M40,-112 L40,-82 L24,-20 Q22,-10 32,-10 L64,-10 Q74,-10 72,-20 L56,-82 L56,-112 Z"
    clip = c.shape(flask, P.LENS, sw=0, light=None, clip=True)               # ... and the big flask
    c.add(f'<g clip-path="url(#{clip})"><path d="M10,-44 Q30,-50 48,-44 T86,-44 V0 H10 Z" fill="{accent}"/>'
          f'<path d="M10,-44 Q30,-50 48,-44 T86,-44" fill="none" stroke="{darken(accent, 0.75)}" '
          f'stroke-width="1.5"/></g>')
    c.add(f'<path d="M30,-38 L44,-96" fill="none" stroke="{P.WHITE}" stroke-width="3" stroke-linecap="round" '
          f'stroke-opacity=".7"/>')
    c.path(flask, sw=SW)
    c.shape(rect_d(36, -118, 24, 8), P.METAL, sw=1.7, light=None)              # its rim
    _bubbles(c, ((46, -128, 3.8), (54, -138, 3), (44, -136, 2.2), (40, -30, 2.2), (52, -24, 1.8)))
    for x, color in ((88, P.TEAL), (104, P.RED)):                          # the gas cylinders
        c.shape(rounded_rect_d(x - 6, -50, 12, 50, 5), color, sw=1.8)
        c.shape(rect_d(x - 2.5, -56, 5, 6), P.METAL_DARK, sw=1.2, light=None)


@vignette("harbour", -112, -146, 112)
def harbour(c: Canvas, accent: str) -> None:
    """Chapter 8: the harbour - a lighthouse in the chapter's colour on a rock, a pier with crates and a bollard, a
    sailing boat, gulls."""
    bay = "M-108,-12 Q-112,-52 -62,-60 Q0,-68 62,-60 Q112,-52 108,-12 Q100,2 0,0 Q-100,2 -108,-12 Z"
    _water(c, bay, -112, 112, -68, 2)
    c.shape(rect_d(-110, -44, 76, 9), P.WOOD, sw=SW * 0.9)                   # the pier on its posts ...
    c.line("M-100,-35 V-22 M-74,-35 V-22 M-48,-35 V-22", sw=2.4, stroke=P.WOOD_DARK)
    c.shape(rect_d(-104, -58, 14, 14), P.KITCHEN_KRAFT, sw=1.5)               # ... crates and a bollard on it
    c.shape(rect_d(-89, -54, 11, 10), P.WOOD_LIGHT, sw=1.5)
    c.line("M-104,-51 H-90 M-97,-58 V-44", sw=1)
    c.shape(rounded_rect_d(-58, -52, 8, 8, 3), P.CHARCOAL, sw=1.3, light=None)
    c.shape("M-36,-12 L10,-12 Q6,-2 -6,-2 L-24,-2 Q-32,-2 -36,-12 Z", P.WOOD, sw=SW * 0.9)   # the boat ...
    c.line("M-14,-12 V-62", sw=1.9)
    c.shape("M-12,-60 L-12,-16 L18,-16 Z", accent, sw=1.7)                   # ... its sail in the chapter's colour
    c.line("M-42,-4 q6,-3 12,0 M10,-4 q6,-3 12,0", sw=1.5, stroke=P.WHITE)
    c.shape("M36,-8 Q34,-30 52,-34 L80,-34 Q96,-28 94,-8 Z", P.STONE, sw=SW)  # the rock ...
    tower = "M52,-32 L58,-118 L76,-118 L82,-32 Z"                            # ... the tower in bands
    _banded(c, tower, accent, P.WHITE, -118, -32, 20, 50, 84)
    c.shape(rect_d(52, -126, 30, 8), P.CHARCOAL, sw=1.7, light=None)          # the gallery
    c.shape(rect_d(57, -140, 20, 14), P.SUN, sw=1.7, light=None)              # the lantern, lit
    c.line("M62,-140 V-126 M67,-140 V-126 M72,-140 V-126", sw=1)
    c.shape("M54,-140 Q67,-156 80,-140 Z", accent, sw=1.7)                   # the cap
    c.add(f'<path d="M78,-134 L108,-142 L108,-122 Z M56,-134 L28,-142 L28,-122 Z" fill="{P.SUN}" '
          f'fill-opacity=".45"/>')                                          # its beams
    c.line("M-70,-112 q5,-6 10,0 q5,-6 10,0 M-40,-126 q4,-5 8,0 q4,-5 8,0", sw=1.8)   # gulls


@vignette("moon", -112, -150, 112)
def moon(c: Canvas, accent: str) -> None:
    """Chapter 9: the moon base - a grey cratered hill with a glass dome, a module, a dish and a rover; a crescent
    moon above."""
    c.shape(_crescent(-74, -124, 22), P.SUN, sw=SW)                          # the crescent
    hill = "M-112,0 Q-98,-52 -46,-66 Q0,-76 46,-66 Q98,-52 112,0 Z"
    c.shape(hill, P.METAL_PALE, sw=SW, shade_k=0.84)
    for x, y, rx in ((-76, -16, 12), (-28, -40, 8), (52, -22, 13), (86, -10, 8), (6, -12, 7), (-56, -40, 6)):
        c.shape(ellipse_d(x, y, rx, rx * 0.4), P.METAL, sw=1.3, light=None)
        c.line(f"M{n(x - rx * 0.7)},{n(y - rx * 0.2)} q{n(rx * 0.7)},{n(-rx * 0.3)} {n(rx * 1.4)},0", sw=0.9,
               stroke=darken(P.METAL, 0.8))
    c.shape("M-48,-64 Q-48,-104 -14,-106 Q20,-104 20,-64 Z", P.LENS, sw=SW)    # the glass dome ...
    c.line("M-31,-65 Q-34,-94 -14,-105 M3,-65 Q6,-94 -14,-105 M-46,-82 Q-14,-92 18,-82", sw=1.5,
           stroke=accent)                                                    # ... its ribs in the chapter's colour
    c.add(f'<path d="M-40,-76 Q-38,-94 -24,-100" fill="none" stroke="{P.WHITE}" stroke-width="2.5" '
          f'stroke-linecap="round" stroke-opacity=".8"/>')
    c.dot(-14, -72, 2.6, P.YELLOW_PALE)
    c.shape(rounded_rect_d(20, -88, 34, 24, 6), accent, sw=SW)               # the module
    c.dot(30, -76, 2.5, P.YELLOW_PALE)
    c.dot(42, -76, 2.5, P.YELLOW_PALE)
    c.line("M64,-64 V-110", sw=2.5, stroke=P.METAL_DARK)                     # the dish on its mast
    c.shape("M50,-120 Q60,-102 80,-106 Q70,-116 50,-120 Z", P.WHITE, sw=1.7)
    c.line("M64,-110 L60,-116", sw=1.5)
    c.shape(rounded_rect_d(70, -36, 26, 10, 3), P.METAL_PALE, sw=1.6)       # the rover on the slope
    for x in (74, 84, 94):
        c.shape(circle_d(x, -24, 3.6), P.CHARCOAL, sw=1.1, light=None)
    c.line("M90,-36 V-48", sw=1.3)
    c.dot(90, -49, 1.8, P.RED)


# ---------------------------------------------------------------------------- the courtyard and the camp
@vignette("courtyard", -74, -118, 76)
def courtyard(c: Canvas, accent: str) -> None:
    """The introduction: the professor's courtyard - a tree, a bench, flower beds, a mailbox, a fence with a gate."""
    _shadow(c, 150)
    c.shape(rect_d(-46, -64, 9, 64), P.TRUNK, sw=SW)                          # the tree
    c.shape("M-70,-68 Q-78,-98 -54,-110 Q-38,-122 -22,-106 Q-2,-98 -14,-74 Q-20,-58 -44,-60 Q-64,-56 -70,-68 Z",
            P.LEAF, sw=SW)
    for x, y in ((-60, -90), (-40, -100), (-28, -80)):
        c.shape(circle_d(x, y, 3), P.RED, sw=1, light=None)                  # apples on it
    c.shape(rect_d(6, -26, 44, 6), P.WOOD, sw=1.7)                            # the bench
    c.shape(rect_d(6, -40, 44, 6), P.WOOD, sw=1.7)
    c.line("M12,-20 V-4 M44,-20 V-4", sw=2.4, stroke=P.WOOD_DARK)
    c.line("M62,-2 V-30", sw=2.4, stroke=P.WOOD_DARK)                        # the mailbox
    c.shape("M54,-30 V-42 Q62,-50 70,-42 V-30 Z", P.BLUE, sw=1.6)
    for x in list(range(-72, -12, 11)) + list(range(16, 74, 11)):            # the fence ...
        c.shape(f"M{x},-2 V-22 L{x + 4},-28 L{x + 8},-22 V-2 Z", P.CARD, sw=1.5, light=None)
    c.line("M-74,-9 H-12 M14,-9 H76", sw=1.7)
    c.shape(rounded_rect_d(-12, -30, 26, 28, 3), P.WOOD_LIGHT, sw=1.7, light=None)   # ... and its gate
    c.line("M-12,-16 H14 M1,-30 V-2", sw=1.1)


@vignette("camp", -112, -128, 112)
def camp(c: Canvas, accent: str) -> None:
    """Chapter 10, security: a camp at the forest's edge - firs, a tent, a campfire with log seats."""
    _shadow(c, 220)
    for x, h in ((-96, 110), (-70, 128), (-46, 100), (78, 118), (100, 96)):   # the firs
        _fir(c, x, h)
    c.shape("M-28,0 L4,-58 L36,0 Z", P.ORANGE, sw=SW)                         # the tent
    c.shape("M-2,0 L4,-32 L12,0 Z", darken(P.ORANGE, 0.6), sw=1.5, light=None)
    c.shape(rounded_rect_d(40, -10, 22, 8, 4), P.WOOD, sw=1.5, light=None)    # a log seat
    c.line("M44,-2 L60,-12 M44,-12 L60,-2", sw=3.6, stroke=P.WOOD_DARK)        # the campfire
    c.shape("M46,-12 Q48,-26 52,-32 Q56,-24 58,-12 Z", P.AMBER, sw=1.5, light=None)
    c.shape("M49,-12 Q51,-20 52,-24 Q54,-18 55,-12 Z", P.RED, sw=0, light=None)


@vignette("city", -98, -142, 98)
def city(c: Canvas, accent: str) -> None:
    """The conclusion: the computer city the characters walk into on the book's last page (`farewell.py`) - on a
    circuit board with gold contact fingers, its wall with lights along the top and the gate between two fin pillars,
    the hall under a fan dome behind, two processor chips standing on end with pins and lit windows, a cable car on
    the cable between them, a server rack with its blinking units, a capacitor tower."""
    pcb = mix(P.PINE, P.LEAF_DARK, 0.35)
    _shadow(c, 200)
    c.shape(rect_d(-98, -10, 196, 10), darken(pcb, 0.8), sw=SW, light=None)           # the board's edge ...
    c.add(f'<path d="{"".join(rect_d(x, -8, 3.6, 6) for x in _frange(-94, 94, 7))}" fill="{P.GOLD}"/>')   # fingers
    c.shape(rect_d(-94, -82, 22, 72), P.METAL_DARK, sw=SW)                          # the server rack ...
    c.add(f'<path d="{"".join(rect_d(-91, y, 16, 5) for y in _frange(-78, -18, 7.5))}" fill="{P.CHARCOAL}"/>')
    c.add("".join(f'<circle cx="-88" cy="{n(y + 2.5)}" r="1.4" fill="{P.GLOW if i % 2 else P.SUN}"/>'
                  for i, y in enumerate(_frange(-78, -18, 7.5))))
    for x0, top in ((-64, -126), (44, -138)):                                      # the two chips on end
        pins = "".join(f"M{n(x)},{n(y)} h{n(d * 4)} v4" for y in _frange(top + 14, -18, 8)
                       for x, d in ((x0, -1), (x0 + 20, 1)))
        c.line(pins, sw=3.2)
        c.line(pins, sw=1.6, stroke=P.METAL_LIGHT)
        c.shape(rounded_rect_d(x0, top, 20, -10 - top, 2), P.CHARCOAL, sw=SW)
        c.add(f'<path d="M{n(x0 + 6)},{n(top)} A4,4 0 0 0 {n(x0 + 14)},{n(top)}" fill="{P.TERMINAL}" '
              f'stroke="{P.INK}" stroke-width="1.2"/>')
        lit = "".join(rect_d(x0 + 4 + i * 7, y, 4, 4) for y in _frange(top + 10, -18, 8) for i in range(2)
                      if (i + int(y)) % 5)
        c.add(f'<path d="{lit}" fill="{P.YELLOW_PALE}"/>')
    c.line("M-44,-112 Q0,-96 44,-124", sw=2.4)                                     # the cable ...
    c.line("M-20,-106 V-100", sw=1.6)                                             # ... and its cable car
    c.shape(rounded_rect_d(-28, -100, 16, 11, 2.5), accent, sw=1.6, light=None)
    c.add(f'<path d="{rect_d(-25, -97, 4, 4)}{rect_d(-19, -97, 4, 4)}" fill="{P.YELLOW_PALE}"/>')
    dome = "M-36,-40 A36,36 0 0 1 36,-40 Z"                                       # the hall under its fan dome
    clip = c.shape(dome, P.CHARCOAL, sw=SW, light=None, clip=True)
    def at(r: float, deg: float) -> str:
        return f"{n(r * math.cos(math.radians(deg)))},{n(-40 + r * math.sin(math.radians(deg)))}"
    blades = " ".join(f"M0,-40 Q{at(26, a - 14)} {at(34, a)}" for a in range(-165, -10, 26))
    c.add(f'<g clip-path="url(#{clip})"><path d="{blades}" fill="none" stroke="{P.TEAL}" stroke-width="4"/></g>')
    c.shape("M-8,-40 A8,8 0 0 1 8,-40 Z", P.METAL, sw=1.4, light=None)
    c.shape(rect_d(-98, -26, 196, 17), mix(P.PINE, P.LEAF_DARK, 0.35), sw=SW, light=None)   # the city wall ...
    c.add("".join(f'<circle cx="{n(x)}" cy="-26" r="1.6" fill="{P.GLOW}"/>' for x in _frange(-94, 96, 8)))
    for x0 in (-34, 22):                                                          # ... the gate's fin pillars
        c.shape(rect_d(x0, -50, 12, 41), P.METAL_DARK, sw=1.6, light=None)
        c.add(f'<path d="{"".join(rect_d(x0 - 2, y, 16, 2) for y in _frange(-46, -12, 5))}" fill="{P.METAL_LIGHT}"/>')
    c.shape("M-20,-9 V-38 Q-20,-44 -14,-44 H14 Q20,-44 20,-38 V-9 Z", P.METAL_PALE, sw=SW)   # ... and the gate
    c.shape("M-12,-9 V-32 Q-12,-36 -8,-36 H8 Q12,-36 12,-32 V-9 Z", P.SUN, sw=1.4, light=None)
    c.add(f'<path d="{"".join(rect_d(x, -34, 2, 4) for x in _frange(-8, 7, 4))}" fill="{P.GOLD}"/>')
    cap = "M70,-76 V-14 A11,3.4 0 0 0 92,-14 V-76 A11,3.4 0 0 0 70,-76 Z"            # the capacitor tower
    clip = c.shape(cap, P.BLUE, sw=SW, light=(-3, 0), clip=True)
    marks = "".join(f"M85.2,{n(y)} h2.6" for y in _frange(-68, -18, 7))           # its stripe of minus signs
    c.add(f'<g clip-path="url(#{clip})"><path d="{rect_d(84, -80, 5, 70)}" fill="{lighten(P.BLUE, 0.55)}"/>'
          f'<path d="{marks}" fill="none" stroke="{darken(P.BLUE, 0.6)}" stroke-width="1.6"/></g>')
    c.shape(ellipse_d(81, -76, 11, 3.4), P.METAL_LIGHT, sw=1.6, light=None)


@vignette("signpost-only", -30, -40, 30)
def _nothing(c: Canvas, accent: str) -> None:
    """A planned chapter with no drawing of its own: only its plaque stands by the road."""


# What stands at a planned chapter's place, by slot, until it is written; a written one is drawn from its world.
PLANNED = {"intro": "courtyard", "10": "camp", "end": "city"}


# ============================================================================ the plaques
def wrap(title: str, room: float) -> tuple[list[str], float]:
    """The title broken into lines of at most `room` units: in up to three lines, at its size or, failing that, a
    little smaller (down to 0.86 of it); a title that still needs more lines keeps them at the smallest size, set
    smaller still if a word is wider than `room` - never squeezed."""
    words = title.split()
    for size in (TITLE_SIZE, TITLE_SIZE * 0.92, TITLE_SIZE * 0.86):
        lines: list[str] = []
        for word in words:
            line = f"{lines[-1]} {word}" if lines else word
            if lines and lettering_width(line, size, "label") <= room:
                lines[-1] = line
            else:
                lines.append(word)
        if len(lines) <= 3 and all(lettering_width(line, size, "label") <= room for line in lines):
            return lines, size
    widest = max(lettering_width(line, size, "label") for line in lines)
    return lines, size * min(1.0, room / widest)


def plaque_height(lines: int) -> float:
    return 13 + lines * TITLE_LH + 21


def _clock(c: Canvas, x: float, y: float, r: float, ink: str) -> None:
    """A little clock face: the reading time."""
    c.add(f'<path d="{circle_d(x, y, r)}" fill="{P.WHITE}" stroke="{ink}" stroke-width="1.5"/>')
    c.line(f"M{n(x)},{n(y)} V{n(y - r * 0.62)} M{n(x)},{n(y)} L{n(x + r * 0.5)},{n(y + r * 0.2)}", sw=1.4,
           stroke=ink)


def _plaque(stop: Stop, x: float, top: float, soon: str) -> tuple[str, tuple, list[str]]:
    """A wooden plaque on two posts: the chapter's number on a medallion, its title, its reading time (or "soon" for a
    chapter not written yet, greyed like the contents). `top` is the medallion's top. Returns the drawing, its box
    and its lines of title."""
    c = Canvas()
    w, r = PLAQUE_W, 13
    lines, size = wrap(stop.title, w - 18)
    board_top = top + r + 2
    h = plaque_height(len(lines))
    ground = board_top + h + 6
    ink = P.INK if stop.written else mix(P.INK, P.PAPER_SHADE, 0.45)
    for px in (x - w / 2 + 22, x + w / 2 - 22):                              # the posts
        c.add(f'<path d="{rect_d(px - 2.6, board_top + h - 4, 5.2, ground - board_top - h + 4)}" '
              f'fill="{P.WOOD_DARK}" stroke="{P.INK}" stroke-width="1.4"/>')
    board = rounded_rect_d(x - w / 2, board_top, w, h, 6)
    wood = P.WOOD_PALE if stop.written else P.PAPER_SHADE
    clip = c.shape(board, wood, sw=SW, shade_k=0.9)
    grain = " ".join(f"M{n(x - w / 2 + 6)},{n(y)} q{n(w * 0.25)},-3 {n(w * 0.5)},0 t{n(w * 0.5 - 12)},0"
                     for y in _frange(board_top + 9, board_top + h - 4, 11))     # the wood's grain, faint
    c.add(f'<g clip-path="url(#{clip})"><path d="{grain}" fill="none" stroke="{darken(wood, 0.75)}" '
          f'stroke-width="1" stroke-opacity=".35"/></g>')
    for nx in (x - w / 2 + 7, x + w / 2 - 7):                               # nails
        c.dot(nx, board_top + 7, 1.6, darken(wood, 0.55))
    cy = top + r                                                            # the medallion with the number
    if stop.written:
        c.shape(circle_d(x, cy, r), stop.color, sw=2.2, light=None)
    else:
        c.add(f'<path d="{circle_d(x, cy, r)}" fill="{P.PAPER_SHADE}" stroke="{P.INK}" stroke-width="1.8" '
              f'stroke-dasharray="3.4 2.6"/>')
    if stop.label:
        num = 14 if len(stop.label) < 2 else 11.5
        c.add(lettering(x, cy + num * 0.36, stop.label, num, fill=ink, style="label"))
    else:                                    # the introduction and the conclusion: a star, as in the contents
        c.add(f'<path d="{_star(x, cy, r * 0.55)}" fill="{ink}"/>')
    y = board_top + 13 + size * 0.72
    for line in lines:                                                      # the title
        c.add(lettering(x, y, line, size, fill=ink, style="label"))
        y += TITLE_LH
    foot = board_top + h - 9                                                # the time, or "soon"
    if stop.written and stop.time:
        tw = lettering_width(stop.time, 10.6, "label")
        left = x - (tw + 15) / 2
        _clock(c, left + 5.5, foot - 3.6, 5.2, ink)
        c.add(lettering(left + 15, foot, stop.time, 10.6, fill=ink, anchor="start", style="label"))
    else:
        c.add(lettering(x, foot, soon.upper(), 9.6, fill=ink, style="label"))
    art = c.render() if stop.written else f'<g opacity=".72">{c.render()}</g>'
    return art, (x - w / 2 - 1, top, x + w / 2 + 1, ground), lines


# ============================================================================ the land
CROPS = ("meadow", "wheat", "cabbage", "meadow", "ploughed", "rye", "meadow", "wheat", "meadow", "rye")


def _fields(c: Canvas) -> None:
    """Fields in perspective, row upon row to the horizon, each with its own crop, hedges between them."""
    c.add(f'<rect x="0" y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="{P.GRASS}"/>')
    rnd = random.Random(19)
    vx, vy = W / 2, -900                                  # where the field edges would meet beyond the horizon
    ys = [HORIZON + 4]
    while ys[-1] < H:
        ys.append(ys[-1] + 34 + 0.16 * (ys[-1] - HORIZON))
    xs_bottom = list(_frange(-260, W + 260, 150))
    hedges = []
    for j, (y0, y1) in enumerate(zip(ys, ys[1:], strict=False)):
        def at(xb: float, y: float) -> float:            # a field edge from its bottom x up toward the vanishing point
            return vx + (xb - vx) * (y - vy) / (H - vy)
        shift = rnd.uniform(-60, 60)
        for i, (a, b) in enumerate(zip(xs_bottom, xs_bottom[1:], strict=False)):
            a, b = a + shift, b + shift
            quad = [(at(a, y0), y0), (at(b, y0), y0), (at(b, y1), y1), (at(a, y1), y1)]
            crop = CROPS[(i * 3 + j * 7 + rnd.randrange(3)) % len(CROPS)]
            _field(c, quad, crop, rnd, j)
        hedges.append(y1)
    for k, y in enumerate(hedges[:-1]):                   # hedges along the field rows: dark bushes in a line
        depth = scale_at(y)
        line = f"M0,{n(y)}" + "".join(f" Q{n(x + 22)},{n(y - 4 * depth)} {n(x + 44)},{n(y)}"
                                      for x in _frange(0, W, 44))
        c.add(f'<path d="{line}" fill="none" stroke="{P.INK}" stroke-width="{n(7.4 * depth + 1.6)}" '
              f'stroke-opacity=".3" stroke-linecap="round"/>')
        c.add(f'<path d="{line}" fill="none" stroke="{P.LEAF if k % 2 else P.LEAF_LIGHT}" '
              f'stroke-width="{n(7.4 * depth)}" stroke-linecap="round"/>')


def _field(c: Canvas, quad, crop: str, rnd: random.Random, row: int) -> None:
    """One field: its ground and the marks of its crop."""
    base = {"meadow": P.GRASS, "wheat": lighten(P.SUN, 0.35), "cabbage": P.HILL_NEAR, "ploughed": P.FLOOR_DARK,
            "rye": lighten(P.SAND, 0.15)}[crop]
    d = poly_d(quad)
    clip = c.shape(d, base, sw=0, light=None, clip=True)
    (x0, y0), (x1, _), (x2, y2), (x3, _) = quad
    depth = scale_at(y2)
    marks = []
    if crop in ("wheat", "rye", "ploughed"):        # furrows running away toward the horizon
        color = {"wheat": darken(P.SUN, 0.85), "rye": darken(P.SAND, 0.82), "ploughed": darken(P.FLOOR_DARK, 0.8)}[crop]
        for t in _frange(0.04, 1, 0.09):
            marks.append(f"M{n(x3 + (x2 - x3) * t)},{n(y2)} L{n(x0 + (x1 - x0) * t)},{n(y0)}")
        c.add(f'<g clip-path="url(#{clip})"><path d="{" ".join(marks)}" stroke="{color}" '
              f'stroke-width="{n(1 + depth)}" fill="none" stroke-opacity=".45"/></g>')
    elif crop == "cabbage":                                 # rows of young plants running away
        for t in _frange(0.06, 1, 0.14):
            marks.append(f"M{n(x3 + (x2 - x3) * t)},{n(y2)} L{n(x0 + (x1 - x0) * t)},{n(y0)}")
        c.add(f'<g clip-path="url(#{clip})"><path d="{" ".join(marks)}" stroke="{P.LEAF}" '
              f'stroke-width="{n(2 + 2 * depth)}" stroke-dasharray="{n(4 * depth + 2)} {n(3 * depth + 2)}" '
              f'stroke-linecap="round" fill="none" stroke-opacity=".6"/></g>')
    else:                                                   # a meadow: flowers here and there
        dots = {P.WHITE: [], P.SUN: [], P.PINK_PALE: []}
        for _ in range(int(14 * depth + 4)):
            t, u = rnd.random(), rnd.random()
            x = (x3 + (x2 - x3) * t) * u + (x0 + (x1 - x0) * t) * (1 - u)
            dots[rnd.choice(list(dots))].append((x, y0 + (y2 - y0) * u))
        body = "".join(f'<path d="{"".join(f"M{n(x)},{n(y)}h.01" for x, y in pts)}" stroke="{color}" '
                       f'stroke-width="{n(2.2 + 1.6 * depth)}" stroke-linecap="round" fill="none"/>'
                       for color, pts in dots.items() if pts)
        c.add(f'<g clip-path="url(#{clip})">{body}</g>')
    c.path(d, sw=0.9, stroke=darken(P.GRASS_DARK, 0.8), extra='stroke-opacity=".35"')


def _sky(c: Canvas) -> None:
    """The night sky over the far edge of the land: deep at the top, a dusk glow at the horizon, stars."""
    paint = c.gradient([(0, P.SPACE_DEEP), (0.6, P.SPACE_LOW), (1, mix(P.SPACE_LOW, P.AMBER, 0.45))],
                       0, 0, 0, HORIZON + 20)
    c.add(f'<rect x="0" y="0" width="{W}" height="{HORIZON + 24}" fill="{paint}"/>')
    rnd = random.Random(7)
    for _ in range(46):
        c.dot(rnd.uniform(8, W - 8), rnd.uniform(6, HORIZON - 30), rnd.uniform(0.8, 1.7), P.WHITE)
    for x, y, r in ((300, 30, 6), (520, 54, 5), (760, 22, 7), (60, 52, 5), (430, 18, 4.5), (640, 40, 5)):
        c.add(f'<path d="{_sparkle(x, y, r)}" fill="{P.YELLOW_PALE}"/>')


def _hills(c: Canvas) -> None:
    """The far hills at the horizon with a dark forest line along their crest."""
    ridge = (f"M0,{HORIZON + 6} Q110,{HORIZON - 22} 240,{HORIZON + 2} Q380,{HORIZON + 22} 520,{HORIZON - 4} "
             f"Q660,{HORIZON - 26} {W},{HORIZON + 4}")
    c.add(f'<path d="{ridge} V{HORIZON + 40} H0 Z" fill="{mix(P.HILL_NEAR, P.FIR, 0.35)}"/>')
    c.line(ridge, sw=SW)
    rnd = random.Random(29)                               # the forest along the crest
    trees = []
    for x in _frange(6, W, 15):
        y = HORIZON + 8 + 4 * math.sin(x / 70)
        h = rnd.uniform(12, 22)
        trees.append(poly_d([(x - h * 0.3, y + 4), (x, y - h), (x + h * 0.3, y + 4)]))
    c.add(f'<path d="{" ".join(trees)}" fill="{mix(P.FIR, P.SPACE_LOW, 0.3)}" stroke="{P.INK}" '
          f'stroke-width="1.2" stroke-linejoin="round"/>')


def _river(c: Canvas, line) -> list[tuple[float, float, float]]:
    """The river from the hills into the pond, widening as it comes nearer; returns its samples."""
    samples = [(x, y, 3 + 7 * (y - HORIZON) / (POND[1] - HORIZON)) for x, y in line]
    left, right = [], []
    for i, (x, y, hw) in enumerate(samples):
        a, b = samples[max(0, i - 1)], samples[min(len(samples) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1
        left.append((x - dy / length * hw, y + dx / length * hw))
        right.append((x + dy / length * hw, y - dx / length * hw))
    c.path(poly_d(left + right[::-1]), fill=P.WATER, sw=1.8)
    cx, cy, rx, ry = POND
    c.path(ellipse_d(cx, cy, rx, ry), fill=P.WATER, sw=SW)                  # the pond
    c.line(f"M{cx - 18},{cy - 2} q6,-3 12,0 M{cx + 4},{cy + 5} q6,-3 12,0", sw=1.6, stroke=P.WATER_LIGHT)
    return samples + [(cx, cy, rx)]


def _road(c: Canvas, line) -> list[tuple[float, float, float]]:
    """The road along `line`, narrowing into the distance, edged with stones, worn into ruts, with puddles here and
    there; returns its samples with their half widths."""
    edge_l, edge_r, samples = [], [], []
    normals = []
    for i, (x, y) in enumerate(line):
        a, b = line[max(0, i - 1)], line[min(len(line) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1
        nx, ny = -dy / length, dx / length
        hw = half_width(y)
        edge_l.append((x + nx * hw, y + ny * hw))
        edge_r.append((x - nx * hw, y - ny * hw))
        samples.append((x, y, hw))
        normals.append((nx, ny))

    def cap(x: float, y: float, hw: float, ux: float, uy: float) -> list[tuple[float, float]]:
        base = math.atan2(uy, ux)                        # a half circle closing the road's end
        return [(x + math.cos(base + a) * hw, y + math.sin(base + a) * hw)
                for a in (math.radians(d) for d in range(-90, 91, 15))]

    (x0, y0), (x1, y1) = line[0], line[1]
    (xa, ya), (xb, yb) = line[-2], line[-1]
    end = cap(xb, yb, half_width(yb), xb - xa, yb - ya)
    start = cap(x0, y0, half_width(y0), x0 - x1, y0 - y1)
    outline = poly_d(edge_l + end[::-1] + edge_r[::-1] + start[::-1])
    c.path(outline, fill=P.INK, sw=SW * 2, stroke=P.INK)
    clip = c.shape(outline, P.SAND, sw=0, light=None, clip=True)
    ruts = []
    for side in (-0.42, 0.42):                                            # the wheel ruts
        pts = [(x + nx * hw * side, y + ny * hw * side) for (x, y, hw), (nx, ny) in zip(samples, normals, strict=True)]
        ruts.append("M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts))
    c.add(f'<g clip-path="url(#{clip})"><path d="{" ".join(ruts)}" fill="none" stroke="{darken(P.SAND, 0.86)}" '
          f'stroke-width="2.2"/></g>')
    stones = []                                                           # the edging stones
    step = 0
    for (x, y, hw), (nx, ny) in zip(samples, normals, strict=True):
        step += 1
        if step % 13:
            continue
        for side in (1, -1):
            k = 0.78 if (step // 7 + (side > 0)) % 2 else 0.55            # stones of two sizes, set in the verge
            sx, sy = x + nx * (hw + 3) * side, y + ny * (hw + 3) * side
            stones.append(ellipse_d(sx, sy, 4 * k * hw / ROAD_HALF + 1, 2.4 * k * hw / ROAD_HALF + 0.6))
    c.add(f'<path d="{" ".join(stones)}" fill="{P.STONE}" stroke="{darken(P.STONE, 0.6)}" stroke-width="1"/>')
    for row, px in PUDDLES:                                               # puddles on the straight runs
        y = ROWS[row][0]
        x, hw = px, half_width(y)
        c.add(f'<path d="{ellipse_d(x + hw * 0.1, y + hw * 0.1, hw * 0.55, hw * 0.24)}" fill="{P.WATER_LIGHT}" '
              f'stroke="{darken(P.SAND, 0.8)}" stroke-width="1"/>')
    return samples


def _bridge(c: Canvas, road) -> None:
    """A stone bridge where the road crosses the river: its parapets along both sides of the road."""
    best = min(road, key=lambda s: math.hypot(s[0] - RIVER_X, s[1] - ROWS[-1][0]) if abs(s[1] - ROWS[-1][0]) < 2
               else 1e9)
    x, y, hw = best
    for side in (-1, 1):
        py = y + side * (hw + 2)
        c.shape(rounded_rect_d(x - 22, py - 3.5, 44, 7, 3), P.STONE, sw=1.6, shade_k=0.85)
        c.line(f"M{x - 12},{py - 3.5} V{py + 3.5} M{x},{py - 3.5} V{py + 3.5} M{x + 12},{py - 3.5} V{py + 3.5}",
               sw=0.9, stroke=P.METAL_DARK)


def _railway(c: Canvas, y: float) -> None:
    """The railway of the last chapter: a track with sleepers along the bottom edge."""
    sleepers = " ".join(f"M{n(x)},{n(y - 8)} V{n(y + 8)}" for x in _frange(4, W, 12))
    c.add(f'<path d="{rect_d(0, y - 10, W, 20)}" fill="{P.PEBBLE}"/>')
    c.add(f'<path d="{sleepers}" stroke="{P.WOOD_DARK}" stroke-width="5" fill="none"/>')
    c.add(f'<path d="M0,{n(y - 4.5)} H{W} M0,{n(y + 4.5)} H{W}" stroke="{P.INK}" stroke-width="3.6" fill="none"/>'
          f'<path d="M0,{n(y - 4.5)} H{W} M0,{n(y + 4.5)} H{W}" stroke="{P.METAL}" stroke-width="1.6" fill="none"/>')


def _train(x: float, y: float, cab: str = P.RED) -> str:
    """A little steam train on the track: the locomotive (its cab in `cab`) and two wagons, puffing."""
    c = Canvas()
    for wx, color in ((x + 64, P.BLUE), (x + 120, P.GREEN)):              # the wagons
        c.shape(rounded_rect_d(wx, y - 34, 50, 26, 4), color, sw=SW)
        for k in (0, 1, 2):
            _window(c, wx + 5 + k * 15, y - 30, 10, 10, lit=True, cross=False)
        c.line(f"M{wx - 6},{y - 14} H{wx}", sw=2.4)
        for ww in (wx + 10, wx + 40):
            c.shape(circle_d(ww, y - 5, 5), P.METAL_DARK, sw=1.6, light=None)
    c.shape(rounded_rect_d(x - 26, y - 30, 42, 20, 8), P.CHARCOAL, sw=SW)      # the boiler
    c.shape(rect_d(x + 12, y - 44, 26, 34), cab, sw=SW)                        # the cab
    _window(c, x + 17, y - 40, 15, 12, lit=True, cross=False)
    c.shape(rect_d(x - 20, y - 46, 9, 16), P.CHARCOAL, sw=1.7, light=None)      # the funnel
    c.shape(f"M{n(x - 34)},{n(y)} L{n(x - 26)},{n(y - 10)} L{n(x - 26)},{n(y)} Z", P.METAL_DARK, sw=1.4,
            light=None)                                                       # the cowcatcher
    c.shape(rect_d(x - 28, y - 12, 68, 5), P.DARK_BROWN, sw=1.7, light=None)
    for wx in (x - 16, x, x + 26):
        c.shape(circle_d(wx, y - 5, 6), P.METAL_DARK, sw=1.7, light=None)
    _smoke(c, x - 16, y - 56, 1.1)
    return c.render()


# ============================================================================ decorations of the land
def _windmill(x: float, y: float, s: float) -> str:
    c = Canvas()
    c.add(f'<path d="{ellipse_d(x, y, 26 * s, 4 * s)}" fill="{P.INK}" fill-opacity=".13"/>')
    c.shape(poly_d([(x - 16 * s, y), (x - 10 * s, y - 62 * s), (x + 10 * s, y - 62 * s), (x + 16 * s, y)]),
            P.CARD, sw=2 * s)
    c.shape(poly_d([(x - 13 * s, y - 60 * s), (x, y - 76 * s), (x + 13 * s, y - 60 * s)]), P.TERRACOTTA, sw=2 * s)
    c.shape(rect_d(x - 5 * s, y - 16 * s, 10 * s, 16 * s), P.WOOD, sw=1.6 * s, light=None)
    hub = (x, y - 62 * s)
    for a in (40, 130, 220, 310):                                          # the sails
        t = math.radians(a)
        ux, uy, vx, vy = math.cos(t), math.sin(t), -math.sin(t), math.cos(t)
        pts = [(hub[0] + ux * 8 * s + vx * 1 * s, hub[1] + uy * 8 * s + vy * 1 * s),
               (hub[0] + ux * 40 * s + vx * 1 * s, hub[1] + uy * 40 * s + vy * 1 * s),
               (hub[0] + ux * 40 * s + vx * 9 * s, hub[1] + uy * 40 * s + vy * 9 * s),
               (hub[0] + ux * 10 * s + vx * 9 * s, hub[1] + uy * 10 * s + vy * 9 * s)]
        c.shape(poly_d(pts), P.WOOD_PALE, sw=1.5 * s, light=None)
        c.line(f"M{n(hub[0])},{n(hub[1])} L{n(hub[0] + ux * 40 * s)},{n(hub[1] + uy * 40 * s)}", sw=1.8 * s)
    c.shape(circle_d(*hub, 3.4 * s), P.WOOD_DARK, sw=1.4 * s, light=None)
    return c.render()


def _haystacks(x: float, y: float, s: float) -> str:
    c = Canvas()
    for dx, k in ((-12, 1.0), (13, 0.8)):
        c.add(f'<path d="{ellipse_d(x + dx * s, y, 14 * s * k, 3 * s)}" fill="{P.INK}" fill-opacity=".12"/>')
        c.shape(f"M{n(x + (dx - 13 * k) * s)},{n(y)} Q{n(x + (dx - 13 * k) * s)},{n(y - 30 * k * s)} "
                f"{n(x + dx * s)},{n(y - 30 * k * s)} Q{n(x + (dx + 13 * k) * s)},{n(y - 30 * k * s)} "
                f"{n(x + (dx + 13 * k) * s)},{n(y)} Z", lighten(P.SUN, 0.2), sw=1.7 * s)
        c.line(f"M{n(x + (dx - 8 * k) * s)},{n(y - 10 * s)} q{n(8 * k * s)},{n(-4 * s)} {n(16 * k * s)},0",
               sw=1.1 * s, stroke=darken(P.SUN, 0.8))
    return c.render()


def _rocks(x: float, y: float, s: float) -> str:
    c = Canvas()
    c.shape(f"M{n(x - 16 * s)},{n(y)} Q{n(x - 16 * s)},{n(y - 14 * s)} {n(x - 4 * s)},{n(y - 15 * s)} "
            f"Q{n(x + 8 * s)},{n(y - 14 * s)} {n(x + 6 * s)},{n(y)} Z", P.STONE, sw=1.7 * s)
    c.shape(f"M{n(x + 2 * s)},{n(y)} Q{n(x + 4 * s)},{n(y - 9 * s)} {n(x + 12 * s)},{n(y - 9 * s)} "
            f"Q{n(x + 20 * s)},{n(y - 8 * s)} {n(x + 18 * s)},{n(y)} Z", P.PEBBLE, sw=1.7 * s)
    return c.render()


def _tree(x: float, y: float, s: float, kind: int = 0) -> str:
    """A tree: a round one with a few apples, or a fir."""
    c = Canvas()
    c.add(f'<path d="{ellipse_d(x, y, 13 * s, 3 * s)}" fill="{P.INK}" fill-opacity=".12"/>')
    if kind:
        _fir(c, x, 46 * s, y)
    else:
        c.shape(rect_d(x - 2.6 * s, y - 14 * s, 5.2 * s, 14 * s), P.TRUNK, sw=1.5 * s, light=None)
        c.shape(ellipse_d(x, y - 27 * s, 15 * s, 14 * s), P.LEAF_LIGHT, sw=1.7 * s)
        c.dot(x - 5 * s, y - 30 * s, 1.8 * s, P.RED)
        c.dot(x + 6 * s, y - 24 * s, 1.8 * s, P.RED)
    return c.render()


def _bush(x: float, y: float, s: float) -> str:
    """A flowering bush."""
    c = Canvas()
    c.shape(f"M{n(x - 15 * s)},{n(y)} Q{n(x - 17 * s)},{n(y - 14 * s)} {n(x - 6 * s)},{n(y - 15 * s)} "
            f"Q{n(x)},{n(y - 22 * s)} {n(x + 8 * s)},{n(y - 15 * s)} Q{n(x + 18 * s)},{n(y - 13 * s)} "
            f"{n(x + 15 * s)},{n(y)} Z", P.LEAF, sw=1.6 * s)
    for dx, dy, color in ((-7, -9, P.PINK_PALE), (2, -14, P.WHITE), (8, -7, P.PINK_PALE), (-1, -5, P.SUN)):
        c.dot(x + dx * s, y + dy * s, 2 * s, color)
    return c.render()


# What may be scattered on the free land, biggest first: (maker, box half width, box height, how many at most).
DECOR = ((_windmill, 30, 80, 2), (_haystacks, 28, 32, 2), (lambda x, y, s: _tree(x, y, s, 1), 14, 48, 5),
         (_tree, 16, 43, 6), (_rocks, 17, 16, 3), (_bush, 17, 22, 4))


# ============================================================================ the map
CAST = (("sparrow", "fly", "smile"), ("professor", "walk", "talk"), ("cat", "walk", "smile"),
        ("caterpillar", "walk", "smile"), ("agent", "walk", "smile"))


def draw(stops: list[Stop], soon: str = "soon") -> BookMap:
    """The map for these stops in plan order. Raises `MapError` for a stop it has no place or drawing for."""
    stage = Stage(seed=5, reserved=[])
    back = stage.back
    _sky(back)
    _fields(back)
    _hills(back)
    river = _river(back, river_line())
    road = _road(back, road_line())
    _bridge(back, road)
    # Dusk falls over the far land: the way runs from morning at the bottom to night at the top.
    back.fade(0, HORIZON, W, 440, [(0, P.SPACE_LOW, 0.42), (0.6, P.SPACE_LOW, 0.1), (1, P.SPACE_LOW, 0.0)])
    result = BookMap("", road=road, river=river)
    railway: Stop | None = None
    for stop in stops:
        if stop.slot == RAILWAY:
            railway = stop
            continue
        if stop.slot not in SLOTS:
            raise MapError(f"the map of the book has no place for chapter {stop.slot}: give it a slot in "
                           f"art/bookmap.py SLOTS")
        if stop.written and stop.world:
            if stop.world not in VIGNETTES:
                raise MapError(f"chapter {stop.slot} lives in the world {stop.world!r}, which the map of the book "
                               f"cannot draw yet: add its vignette to art/bookmap.py")
            kind = stop.world
        else:
            kind = PLANNED.get(stop.slot, "signpost-only")
        result.drawn[stop.slot] = kind
        result.plaques[stop.slot] = _place(stage, stop, kind, soon)
    if railway is not None:
        result.drawn[railway.slot] = "railway" if railway.written else "planned railway"
        result.plaques[railway.slot] = _place_railway(stage, railway, soon)
    _walkers(stage)
    _decorate(stage, road, river)
    result.svg = stage.svg("bookmap-art", marks=False)
    result.boxes = list(stage.boxes)
    return result


def _place(stage: Stage, stop: Stop, kind: str, soon: str) -> list[str]:
    row, x = SLOTS[stop.slot]
    y, s = ROWS[row]
    hw = half_width(y)
    base = y - hw - 7
    left, top, right = EXTENT[kind]
    k = s * min(VIG_H / -top, VIG_W[row] / (right - left), 1.1)
    c = Canvas()
    VIGNETTES[kind](c, stop.color)
    art = Canvas().place(c, f"translate({n(x)},{n(base)}) scale({n(k)})").render()
    box = (x + left * k, base + top * k, x + right * k, base + 1)
    if not stop.written:
        mist = Canvas()
        _mist(mist, *box)
        art = f'<g opacity=".5">{art}</g>{mist.render()}'
    stage.put(base, art, box, name=kind, group=f"stop{stop.slot}")
    plaque, pbox, lines = _plaque(stop, x, y + hw + 4, soon)
    stage.put(pbox[3], plaque, pbox, name=f"plaque{stop.slot}", group=f"plaque{stop.slot}")
    return lines


def _mist(c: Canvas, left: float, top: float, right: float, bottom: float) -> None:
    """Wisps of mist over a place not built yet: puffs of cloud in one shape, so their overlaps never darken."""
    h, w = bottom - top, right - left
    d = []
    for k, span, shift in ((0.36, 0.7, -0.12), (0.72, 0.9, 0.1)):
        y, half = top + h * k, w * span / 2
        cx = (left + right) / 2 + w * shift
        for i in range(5):
            x = cx - half + 2 * half * i / 4
            r = h * (0.09 + 0.05 * (i % 2 == 1))
            d.append(ellipse_d(x, y - r * 0.3, r * 1.3, r))
        d.append(rounded_rect_d(cx - half, y - h * 0.04, 2 * half, h * 0.1, h * 0.05))
    c.add(f'<path d="{" ".join(d)}" fill="{P.WHITE}" fill-opacity=".62"/>')


def _place_railway(stage: Stage, stop: Stop, soon: str) -> list[str]:
    """The last chapter's railway along the bottom edge: faint while planned, in full and its engine in the
    chapter's colour once written."""
    track = Canvas()
    _railway(track, RAIL_Y)
    faint = not stop.written
    stage.back.add(f'<g opacity=".6">{track.render()}</g>' if faint else track.render())
    train = (452, RAIL_Y - 70, 676, RAIL_Y)
    engine = _train(486, RAIL_Y - 2, P.RED if faint else stop.color)
    stage.put(RAIL_Y, f'<g opacity=".55">{engine}</g>' if faint else engine, train, name="train", group="railway")
    plaque, pbox, lines = _plaque(stop, RAIL_PLAQUE_X, 0, soon)
    lift = RAIL_Y - 12 - pbox[3]                     # the plaque stands on the ground above the track
    stage.put(RAIL_Y, f'<g transform="translate(0,{n(lift)})">{plaque}</g>',
              (pbox[0], pbox[1] + lift, pbox[2], pbox[3] + lift), name=f"plaque{stop.slot}", group="railway")
    return lines


def _walkers(stage: Stage) -> None:
    """The five on the road between the courtyard and the kitchen, walking to chapter 1, the sparrow over them."""
    y, s = ROWS[0]
    left, right = CAST_X
    xs = [left + (right - left) * k for k in (0.86, 0.8, 0.56, 0.32, 0.08)]
    for (name, pose, mood), x in zip(CAST, xs, strict=True):
        lift = 86 if name == "sparrow" else 0
        stage.actor(name, x, y + 5 - lift, pose, mood, tall=90 * s, group="cast")


def _decorate(stage: Stage, road, river) -> None:
    """Windmills, haystacks, trees, rocks and bushes on the free land: each where nothing else is, never on the road
    or the river, spread out."""
    keep = [(x - hw - 5, y - hw - 5, x + hw + 5, y + hw + 5) for x, y, hw in road[::2] + river]
    stage.reserved.extend(keep)
    rnd = random.Random(41)
    spots = [(x + rnd.uniform(-12, 12), y + rnd.uniform(-8, 8))
             for y in range(HORIZON + 40, RAIL_Y - 14, 18) for x in range(24, W - 16, 26)]
    placed: list[tuple[float, float]] = []
    for kind, (make, half, tall, most) in enumerate(DECOR):
        rnd.shuffle(spots)
        count = 0
        for x, y in spots:
            if count == most:
                break
            s = scale_at(y)
            box = (x - half * s, y - tall * s, x + half * s, y + 3)
            if box[0] < EDGE or box[2] > W - EDGE or box[1] < HORIZON + 6:
                continue
            if any(math.hypot(x - px, y - py) < 110 for px, py in placed):
                continue
            if stage.free(box, AIR + 2):
                stage.put(y, make(x, y, s), box, name=f"decor{kind}-{count}", group=f"decor{kind}-{count}")
                placed.append((x, y))
                count += 1
    del stage.reserved[-len(keep):]


def problems(result: BookMap) -> list[str]:
    """What is wrong with a drawn map: things touching across groups, things on the road or in the river, things off
    the page."""
    found = []
    boxes = result.boxes
    for i, a in enumerate(boxes):
        if a.left < EDGE - 1 or a.top < 0 or a.right > W - EDGE + 1 or a.bottom > H - EDGE:
            found.append(f"{a.name} is cut by the page's edge")
        for b in boxes[i + 1:]:
            if a.group != b.group and a.hits(b, AIR):
                found.append(f"{a.name} touches {b.name}")
        if a.kind == "actor":
            continue
        for what, samples in (("the road", result.road), ("the river", result.river)):
            for x, y, hw in samples:
                if a.hits((x - hw, y - hw, x + hw, y + hw), 2):
                    found.append(f"{a.name} stands on {what} at {round(x)},{round(y)}")
                    break
    return found


def plain(title: str) -> str:
    """A title as lettered on a plaque: no Markdown emphasis or code marks."""
    return re.sub(r"[*_`]", "", title).strip()

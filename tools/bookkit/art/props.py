"""Scenery and objects: plants, furniture, the old computer.

Every prop is a function `prop(x, y, scale, ...) -> str` returning an SVG group
whose origin (0, 0) is the point where the object touches the ground.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten
from .ink import INK, Canvas, ellipse_d, n, rounded_rect_d

LEAF = P.LEAF
LEAF_DARK = P.LEAF_DARK
TRUNK = P.TRUNK
WOOD = P.WOOD
BEIGE = P.BEIGE


def _at(c: Canvas, x: float, y: float, scale: float = 1.0, mirror: bool = False) -> str:
    sx = -scale if mirror else scale
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(sx)},{n(scale)})">{c.render()}</g>'


# ------------------------------------------------------------------ meadow
def tuft(x: float, y: float, scale: float = 1.0) -> str:
    c = Canvas()
    c.line("M0,0 q-3,-7 -6,-11 M2,0 q0,-9 1,-15 M4,0 q3,-6 7,-10 M7,0 q5,-3 10,-5", 1.7)
    return _at(c, x, y, scale)


def grass_clump(x: float, y: float, scale: float = 1.0) -> str:
    """A leafy clump with body, for the foreground."""
    c = Canvas()
    c.shape("M-14,2 Q-16,-10 -20,-16 Q-10,-12 -7,-4 Q-6,-18 -2,-26 Q2,-14 3,-5 Q8,-16 16,-20 "
            "Q12,-8 12,2 Z", P.LEAF_LIGHT, sw=2, light=(-2, -2))
    return _at(c, x, y, scale)


def daisy(x: float, y: float, scale: float = 1.0, color: str = P.WHITE) -> str:
    c = Canvas()
    c.line("M0,0 q-3,-10 0,-20", 1.7, P.LEAF_DARK)
    c.path("M-1,-7 q-9,-4 -11,2 q7,3 11,-2 Z", LEAF, 1.5)
    for a in range(0, 360, 60):
        c.add(f'<ellipse cx="0" cy="-7" rx="3.6" ry="5.8" transform="translate(0,-21) rotate({a})" '
              f'fill="{color}" stroke="{INK}" stroke-width="1.5"/>')
    c.add(f'<circle cx="0" cy="-21" r="3.6" fill="{P.YELLOW}" stroke="{INK}" stroke-width="1.5"/>')
    return _at(c, x, y, scale)


def tulip(x: float, y: float, scale: float = 1.0, color: str = P.RED) -> str:
    c = Canvas()
    c.line("M0,0 q2,-14 0,-26", 1.9, P.LEAF_DARK)
    c.path("M0,-4 q-12,-8 -10,-20 q8,6 10,20 Z", LEAF, 1.6)
    c.path("M0,-6 q11,-6 10,-18 q-8,5 -10,18 Z", LEAF_DARK, 1.6)
    c.shape("M-8,-38 Q-9,-26 0,-24 Q9,-26 8,-38 L4,-32 L0,-40 L-4,-32 Z", color, sw=1.8, light=(-2, -2))
    return _at(c, x, y, scale)


def mushroom(x: float, y: float, scale: float = 1.0, color: str = P.RED, spots: bool = True) -> str:
    c = Canvas()
    c.shape("M-5,0 Q-7,-10 -4,-18 L4,-18 Q7,-10 5,0 Q0,3 -5,0 Z", P.CREAM, sw=2, light=(-2, -1))
    c.shape("M-17,-16 Q-15,-35 0,-36 Q15,-35 17,-16 Q0,-11 -17,-16 Z", color, sw=2.2, light=(-3, -3))
    if spots:
        for sx, sy, r in ((-7, -25, 2.6), (5, -28, 2.2), (9, -20, 1.8), (-1, -19, 1.6)):
            c.add(f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="{P.WHITE}"/>')
    return _at(c, x, y, scale)


def stone(x: float, y: float, scale: float = 1.0) -> str:
    c = Canvas()
    c.shape("M-16,1 Q-19,-11 -6,-15 Q10,-18 16,-7 Q19,0 13,2 Z", P.STONE, sw=2, light=(-3, -3),
            stipple=(-2, -12, 18, 14, 10, "right"))
    return _at(c, x, y, scale)


def stump(x: float, y: float, scale: float = 1.0) -> str:
    c = Canvas()
    c.shape("M-24,2 L-19,-30 L19,-30 L24,2 L14,-2 L7,3 L-3,-2 L-13,3 Z", TRUNK, sw=2.2,
            stipple=(4, -28, 18, 28, 16, "right"))
    c.line("M-10,-22 l0,14 M-2,-24 l1,10 M9,-23 l0,13", 1.4)
    c.shape(ellipse_d(0, -30, 19, 7), P.WOOD_PALE, sw=2.2, light=None)
    c.line("M-10,-30 a10,3.600 0 1 0 20,0 a10,3.600 0 1 0 -20,0 M-4,-30 a4,1.500 0 1 0 8,0", 1.2)
    c.path("M16,-30 q6,-10 14,-8 q-4,7 -14,8 Z", LEAF, 1.5)
    return _at(c, x, y, scale)


def bush(x: float, y: float, scale: float = 1.0, berries: bool = False) -> str:
    c = Canvas()
    c.shape("M-36,1 Q-47,-15 -30,-25 Q-28,-44 -7,-40 Q6,-55 23,-40 Q42,-38 38,-19 Q48,-6 35,1 Z",
            P.LEAF_LIGHT, sw=2.3, stipple=(6, -40, 38, 40, 26, "right"))
    c.line("M-14,-22 q5,-6 10,0 M6,-27 q6,-6 11,0 M-4,-11 q5,-5 10,0 M18,-12 q4,-4 8,0", 1.5)
    if berries:
        for bx, by in ((-18, -12), (2, -30), (22, -22), (10, -8)):
            c.add(f'<circle cx="{bx}" cy="{by}" r="3" fill="{P.RED}" stroke="{INK}" stroke-width="1.3"/>')
    return _at(c, x, y, scale)


def tree(x: float, y: float, scale: float = 1.0, kind: str = "oak") -> str:
    """A tree: `oak` (round crown), `birch` (white trunk) or `fir`."""
    c = Canvas()
    if kind == "fir":
        c.shape("M-7,0 L-6,-22 L6,-22 L7,0 Z", TRUNK, sw=2.2, light=(-2, 0))
        for i, (w, top) in enumerate(((44, -20), (36, -52), (27, -82))):
            c.shape(f"M0,{top - 48} L{w},{top} Q{w * 0.5},{top + 6} 0,{top + 2} "
                    f"Q{-w * 0.5},{top + 6} {-w},{top} Z", P.FIR, sw=2.4, light=(-4, -3),
                    stipple=(4, top - 30, w, 30, 10 + i * 2, "right"))
        return _at(c, x, y, scale)
    trunk_color = P.BIRCH if kind == "birch" else TRUNK
    c.shape("M-10,0 Q-5,-42 -8,-78 L-18,-96 L-10,-98 L-2,-84 L2,-104 L10,-102 L8,-78 Q6,-40 12,0 Z",
            trunk_color, sw=2.4, light=(-3, 0), stipple=(0, -76, 12, 76, 16, "right"))
    if kind == "birch":
        c.line("M-6,-20 l7,1 M0,-38 l7,-1 M-6,-54 l6,1 M1,-68 l5,0 M-5,-10 l4,0", 2.4)
        crown, leaf = ("M-46,-84 Q-62,-110 -40,-124 Q-42,-152 -12,-150 Q6,-170 30,-152 Q58,-152 52,-122 "
                       "Q68,-100 46,-84 Q16,-72 -46,-84 Z"), P.LEAF_LIGHT
    else:
        c.line("M-3,-12 q2,-14 0,-28 M4,-30 q2,-14 0,-26", 1.4)
        crown, leaf = ("M-56,-76 Q-74,-104 -46,-120 Q-50,-154 -12,-150 Q8,-176 38,-152 Q72,-152 62,-116 "
                       "Q82,-92 56,-76 Q22,-62 -56,-76 Z"), LEAF
    c.shape(crown, leaf, sw=2.6, light=(-6, -6), stipple=(4, -150, 64, 84, 60, "right"))
    c.line("M-24,-112 q7,-8 14,0 M12,-126 q8,-8 15,0 M-6,-94 q8,-7 14,0 M28,-100 q7,-7 13,0 "
           "M-36,-92 q5,-5 10,0", 1.7)
    return _at(c, x, y, scale)


def cloud(x: float, y: float, scale: float = 1.0) -> str:
    c = Canvas()
    c.shape("M-42,10 Q-60,8 -54,-7 Q-54,-24 -33,-19 Q-25,-38 -4,-27 Q13,-42 28,-23 Q50,-25 48,-6 "
            "Q60,7 42,10 Z", P.WHITE, sw=2.2, light=(-3, -5), shade_k=0.9)
    return _at(c, x, y, scale)


def sun(x: float, y: float, scale: float = 1.0) -> str:
    c = Canvas()
    for a in range(0, 360, 30):
        c.add(f'<path d="M0,-31 L0,-{43 if a % 60 == 0 else 38}" transform="rotate({a})" stroke="{INK}" '
              f'stroke-width="2.3" stroke-linecap="round"/>')
    c.shape(ellipse_d(0, 0, 24, 24), P.SUN, sw=2.4, light=(-4, -4), shade_k=0.88)
    return _at(c, x, y, scale)


def bird(x: float, y: float, scale: float = 1.0) -> str:
    c = Canvas()
    c.line("M-9,0 q5,-7 9,0 q4,-7 9,0", 1.8)
    return _at(c, x, y, scale)


def butterfly(x: float, y: float, scale: float = 1.0, color: str = P.YELLOW) -> str:
    c = Canvas()
    c.path("M0,0 Q-12,-14 -13,-3 Q-12,5 0,0 Z", color, 1.5)
    c.path("M0,0 Q12,-14 13,-3 Q12,5 0,0 Z", lighten(color, 0.3), 1.5)
    c.line("M0,-4 L0,5 M0,-4 l-3,-5 M0,-4 l3,-5", 1.4)
    return _at(c, x, y, scale)


def fence(x: float, y: float, scale: float = 1.0, pickets: int = 6) -> str:
    c = Canvas()
    width = pickets * 16
    c.shape(f"M-4,-30 L{width},-30 L{width},-24 L-4,-24 Z", WOOD, sw=2, light=None)
    c.shape(f"M-4,-14 L{width},-14 L{width},-8 L-4,-8 Z", WOOD, sw=2, light=None)
    for i in range(pickets):
        px = i * 16
        c.shape(f"M{px},2 L{px},-38 L{px + 5},-45 L{px + 10},-38 L{px + 10},2 Z", P.WOOD_PALE, sw=2,
                light=(-2, 0))
    return _at(c, x, y, scale)


def reeds(x: float, y: float, scale: float = 1.0) -> str:
    c = Canvas()
    c.line("M0,0 q-2,-20 2,-38 M8,0 q3,-16 0,-30 M-7,0 q-4,-12 -9,-22", 1.8, P.LEAF_DARK)
    c.shape(rounded_rect_d(-1.5, -52, 7, 17, 3.5), P.WOOD_DARK, sw=1.6, light=(-1, 0))
    c.shape(rounded_rect_d(5, -42, 6, 14, 3), P.WOOD_DARK, sw=1.6, light=(-1, 0))
    return _at(c, x, y, scale)


def balloon(x: float, y: float, length: float = 70, color: str = P.RED) -> str:
    """A balloon whose string ends at (x, y)."""
    c = Canvas()
    c.line(f"M0,0 q-9,{n(-length / 2)} 0,{n(-length)}", 1.5)
    c.path(f"M0,{n(-length)} l-4,5 l8,0 Z", color, 1.6)
    c.shape(ellipse_d(0, -length - 23, 18, 23), color, sw=2.2, light=(-4, -4),
            highlight=f"M-8,{n(-length - 34)} Q-11,{n(-length - 26)} -10,{n(-length - 18)}")
    return _at(c, x, y)


def signpost(x: float, y: float, text: str = "", scale: float = 1.0, right: bool = True) -> str:
    """A wooden post with an arrow board; the label is live text in the heading font."""
    c = Canvas()
    width = max(66, 12.5 * len(text) + 30)
    c.shape("M-5,6 L-4,-80 L5,-80 L5,6 Z", TRUNK, sw=2.2, light=(-2, 0))
    c.line("M-1,-70 l0,20 M2,-40 l0,24", 1.2)
    d = (f"M0,-66 L{width},-66 L{width + 18},-50 L{width},-34 L0,-34 Z" if right
         else f"M0,-66 L{-width},-66 L{-width - 18},-50 L{-width},-34 L0,-34 Z")
    c.shape(d, P.CREAM, sw=2.4, light=(-2, -3), shade_k=0.9)
    tx = width / 2 + 4 if right else -width / 2 - 4
    c.add(f'<circle cx="0" cy="-58" r="1.700" fill="{INK}"/><circle cx="0" cy="-42" r="1.700" fill="{INK}"/>')
    c.text(tx, -44, text, 18)
    return _at(c, x, y, scale)


# ------------------------------------------------------------------ indoors
def computer(x: float, y: float, scale: float = 1.0, mirror: bool = False, lines: int = 3,
             keyboard: bool = True) -> str:
    """The beige home computer: a deep CRT monitor on a system unit, with a keyboard in front; `keyboard` False
    leaves the keyboard off, for a desk deep enough to put it in front on its own (`props.keyboard`)."""
    c = Canvas()
    # System unit with a floppy slot.
    c.shape(rounded_rect_d(-50, -18, 100, 18, 3), BEIGE, sw=2.3, light=(-3, -2), shade_k=0.86)
    c.path("M-38,-9 h30", "none", 2)
    c.add(f'<rect x="18" y="-11" width="22" height="4" rx="1" fill="{P.DESK}" stroke="{INK}" stroke-width="1.2"/>')
    c.add(f'<circle cx="10" cy="-9" r="1.800" fill="{P.GREEN}"/>')
    # Monitor housing and the glass.
    c.shape("M-44,-18 L-44,-88 Q-44,-95 -37,-95 L37,-95 Q44,-95 44,-88 L44,-18 Z", BEIGE, sw=2.5,
            light=(-4, -3), shade_k=0.86, stipple=(26, -90, 18, 70, 14, "right"))
    glass = c.gradient([(0, P.SCREEN_LIGHT), (1, P.SCREEN_DARK)], -34, -86, 30, -30)
    c.path("M-35,-30 L-35,-80 Q-35,-86 -29,-86 L29,-86 Q35,-86 35,-80 L35,-30 Q0,-26 -35,-30 Z", glass, 2.3)
    c.line("M-27,-78 Q-30,-66 -29,-54", 2.4, P.WHITE, 0.35)
    for i in range(lines):
        c.line(f"M-24,{-72 + i * 9} h{(26, 38, 18, 30)[i % 4]}", 2.4, P.SCREEN_TEXT)
    c.add(f'<circle cx="36" cy="-23" r="2" fill="{P.RED}"/>')
    if keyboard:                                     # drawn in front and a little below the desk edge line
        _keys(c, 8)
    return _at(c, x, y, scale, mirror)


def _keys(c: Canvas, foot: float) -> None:
    c.shape(f"M-46,{foot} L-40,{foot - 12} L40,{foot - 12} L46,{foot} Z", P.BEIGE_DARK, sw=2.2, light=(-2, -2))
    c.line(f"M-36,{foot - 9} h72 M-39,{foot - 5} h78", 1.3)
    c.line(" ".join(f"M{kx},{foot - 9} l{tilt},4" for kx, tilt in ((-28, -2), (-16, -1), (-4, 0), (8, 1), (20, 2),
                                                                     (30, 2))), 1)


def keyboard(x: float, y: float, scale: float = 1.0) -> str:
    """The beige computer's keyboard lying on a desk, its front edge at (x, y): 92 wide, 12 deep."""
    c = Canvas()
    _keys(c, 0)
    return _at(c, x, y, scale)


def desk(x: float, y: float, scale: float = 1.0, width: float = 150, height: float = 62, depth: float = 0) -> str:
    """A wooden desk: two legs, an apron under the top joining them, and a drawer hung from the apron by the
    right leg, its handle a bar; the origin is the middle of its footprint on the floor. The top's front edge is
    `height + 9` up; `depth` shows the top seen a little from above, a surface that far deep behind its edge,
    for things to stand on it one behind another (the computer at the back, the keyboard in front)."""
    c = Canvas()
    half = width / 2
    if depth:
        front, back = -height - 9, -height - 9 - depth
        inset = depth * 0.35
        c.shape(f"M{-half},{front} L{-half + inset},{back} H{half - inset} L{half},{front} Z", P.WOOD_LIGHT,
                sw=2.2, light=None)
    c.shape(f"M{-half + 8},0 L{-half + 8},{-height} L{-half + 18},{-height} L{-half + 18},0 Z", WOOD, sw=2.2,
            light=(-2, 0))
    c.shape(f"M{half - 18},0 L{half - 18},{-height} L{half - 8},{-height} L{half - 8},0 Z", WOOD, sw=2.2,
            light=(-2, 0))
    c.shape(f"M{-half + 18},{-height} H{half - 18} v7 H{-half + 18} Z", darken(WOOD, 0.96), sw=2, light=None)
    c.shape(f"M{half - 52},{-height + 7} h34 v24 h-34 Z", darken(WOOD, 0.92), sw=2, light=None)   # the drawer
    c.shape(rounded_rect_d(half - 42, -height + 17, 14, 4, 2), P.METAL_DARK, sw=1.4, light=None)   # its handle
    c.shape(rounded_rect_d(-half, -height - 9, width, 10, 2), P.WOOD_LIGHT, sw=2.3, light=(-3, -3))
    return _at(c, x, y, scale)


def chair(x: float, y: float, scale: float = 1.0, mirror: bool = False) -> str:
    """The red swivel chair; the seat top is 96 units above the origin."""
    c = Canvas()
    c.line("M0,-58 L0,-16", 6, P.METAL_DARK)
    c.line("M0,-58 L0,-16", 2)
    for dx in (-30, -12, 14, 32):
        c.line(f"M0,-16 L{dx},-4", 3.2)
        c.add(f'<circle cx="{dx}" cy="-1" r="3.600" fill="{P.DARK_BROWN}" stroke="{INK}" stroke-width="1.4"/>')
    c.shape("M-34,-74 Q-34,-84 -24,-84 L26,-84 Q36,-84 36,-74 Q36,-64 26,-64 L-24,-64 Q-34,-64 -34,-74 Z",
            P.RED, sw=2.4, light=(-3, -4))
    c.line("M-28,-84 Q-40,-120 -34,-150", 5, P.METAL_DARK)
    c.shape("M-48,-190 Q-52,-196 -44,-198 Q-26,-200 -22,-190 L-22,-138 Q-24,-130 -34,-130 "
            "Q-46,-130 -46,-138 Z", P.RED, sw=2.4, light=(-3, -4),
            highlight="M-40,-188 Q-41,-170 -40,-150")
    return _at(c, x, y, scale, mirror)


def bookshelf(x: float, y: float, scale: float = 1.0, seed: int = 0, shelves: int = 3) -> str:
    rnd = random.Random(seed)
    c = Canvas()
    height = shelves * 50 + 8
    c.shape(f"M-54,0 L-54,{-height} L54,{-height} L54,0 Z", WOOD, sw=2.5, light=(-3, -3))
    for row in range(shelves):
        top = -height + 6 + row * 50
        c.path(f"M-47,{top} H47 V{top + 42} H-47 Z", P.WOOD_DARK, 1.9)
        bx = -45.0
        while bx < 36:
            bw = rnd.choice((7, 9, 11, 13))
            bh = rnd.choice((30, 34, 38))
            color = rnd.choice(P.BRIGHTS)
            if rnd.random() < 0.12 and bx < 26:  # a book leaning on its neighbour
                c.add(f'<path d="M{n(bx)},{top + 42} L{n(bx + 10)},{top + 42 - bh} L{n(bx + 18)},{top + 44 - bh} '
                      f'L{n(bx + 8)},{top + 42} Z" fill="{color}" stroke="{INK}" stroke-width="1.5" '
                      f'stroke-linejoin="round"/>')
                bx += 19
                continue
            c.path(f"M{n(bx)},{top + 42} V{top + 42 - bh} H{n(bx + bw)} V{top + 42} Z", color, 1.5)
            c.line(f"M{n(bx + 1.5)},{top + 48 - bh} H{n(bx + bw - 1.5)}", 1.1, opacity=0.6)
            bx += bw + 0.4
    return _at(c, x, y, scale)


def picture(x: float, y: float, scale: float = 1.0, variant: int = 0) -> str:
    """A framed picture for the wall; the origin is its centre."""
    c = Canvas()
    c.line("M-10,-24 L0,-36 L10,-24", 1.4)
    c.shape("M-32,-24 H32 V24 H-32 Z", P.YELLOW, sw=2.3, light=(-2, -2))
    sky = (P.SKY, P.PINK_PALE, P.YELLOW_PALE)[variant % 3]
    c.path("M-25,-17 H25 V17 H-25 Z", sky, 1.8)
    if variant % 2 == 0:
        c.path("M-25,17 L-9,-5 L1,8 L10,-1 L25,17 Z", P.LEAF, 1.5)
        c.add(f'<circle cx="14" cy="-9" r="4" fill="{P.SUN}"/>')
    else:
        c.line("M-12,6 q6,-18 12,0 q6,-12 12,0", 2, P.BLUE)
    return _at(c, x, y, scale)


def window(x: float, y: float, scale: float = 1.0) -> str:
    """A window with curtains; the origin is its centre."""
    c = Canvas()
    sky = c.gradient([(0, P.SKY_DEEP), (1, P.SKY_LOW)], 0, -44, 0, 44)
    c.shape("M-50,-48 H50 V48 H-50 Z", P.CARD, sw=2.5, light=None)
    c.path("M-43,-41 H43 V41 H-43 Z", sky, 2)
    c.add(f'<path d="M-30,10 q4,-12 16,-9 q6,-10 18,-3 q12,-2 10,12 Z" fill="{P.WHITE}" opacity=".9"/>')
    c.line("M0,-41 V41 M-43,0 H43", 3)
    c.shape("M-56,-52 H-30 Q-34,-10 -52,36 L-58,36 Z", P.AMBER, sw=2.2, light=(-3, 0))
    c.shape("M56,-52 H30 Q34,-10 52,36 L58,36 Z", P.AMBER, sw=2.2, light=(-3, 0))
    c.shape(rounded_rect_d(-62, -58, 124, 8, 3), WOOD, sw=2.2, light=None)
    return _at(c, x, y, scale)


def plant(x: float, y: float, scale: float = 1.0) -> str:
    """A potted plant standing on the floor."""
    c = Canvas()
    for d in ("M0,-26 Q-22,-44 -30,-72 Q-8,-60 0,-26 Z", "M0,-26 Q-4,-60 6,-86 Q16,-56 0,-26 Z",
              "M0,-26 Q22,-42 34,-64 Q10,-58 0,-26 Z", "M0,-26 Q-20,-30 -34,-44 Q-12,-46 0,-26 Z"):
        c.shape(d, LEAF, sw=2, light=(-2, -2))
    c.shape("M-16,-28 L16,-28 L12,0 L-12,0 Z", P.TERRACOTTA, sw=2.3, light=(-3, -2))
    c.shape(rounded_rect_d(-18, -32, 36, 7, 2), P.TERRACOTTA, sw=2.2, light=None)
    return _at(c, x, y, scale)


def rug(x: float, y: float, scale: float = 1.0, color: str = P.PINK) -> str:
    c = Canvas()
    c.shape(ellipse_d(0, 0, 110, 13), color, sw=2.2, light=(-4, -2))
    c.add(f'<ellipse cx="0" cy="0" rx="84" ry="8" fill="none" stroke="{P.CREAM}" stroke-width="2.4" '
          'stroke-dasharray="7 6"/>')
    return _at(c, x, y, scale)


# ------------------------------------------------------------------ story props
def _burst_d(outer: float, inner: float, spikes: int, turn: float = 0.0) -> str:
    """Path data for a comic starburst centred on the origin."""
    points = []
    for i in range(spikes * 2):
        radius = outer if i % 2 == 0 else inner
        a = math.tau * i / (spikes * 2) + turn
        points.append(f"{n(radius * math.cos(a))},{n(radius * math.sin(a))}")
    return "M" + " L".join(points) + " Z"


def mark(x: float, y: float, kind: str, scale: float = 1.0) -> str:
    """A comic-book badge over a head: `!` (alarm), `?` (puzzled), `ok` (done) or `idea`.

    Each is a drawn shape with chunky outlined lettering, in the manner of the characters,
    never a typeset glyph in a circle. All fit a circle of radius 17 around the origin.
    """
    c = Canvas()
    if kind == "!":      # a yellow starburst with a fat red exclamation mark
        c.shape(_burst_d(17, 11.5, 10, 0.2), P.SUN, sw=2.3, light=(-2, -3), shade_k=0.86)
        c.path("M-4,-10.5 Q0,-12.5 4,-10.5 L2.2,2 Q0,3.2 -2.2,2 Z", P.RED, 2.1)
        c.path(ellipse_d(0, 7.2, 2.9, 2.9), P.RED, 2.1)
    elif kind == "?":    # a thought cloud with a curly question mark, bubbles trailing towards the head
        c.shape("M-12,7 Q-18,5 -16,-2 Q-17,-10 -9,-10 Q-6,-17 2,-14 Q10,-17 13,-9 Q19,-6 16,1 Q18,8 10,8 "
                "Q2,12 -4,8 Q-9,10 -12,7 Z", P.WHITE, sw=2.3, light=(-2, -3), shade_k=0.9)
        c.path(ellipse_d(-9, 14, 2.6, 2.2), P.WHITE, 1.8)
        c.path(ellipse_d(-13, 18.5, 1.5, 1.3), P.WHITE, 1.6)
        curl = "M-4.5,-5 Q-4.5,-10.5 0.5,-10.5 Q6,-10.5 6,-5.5 Q6,-2 1,-0.5 L1,1.5"
        c.line(curl, 6.2)
        c.line(curl, 2.6, P.BLUE)
        c.path(ellipse_d(1, 5.6, 2.3, 2.3), P.BLUE, 1.9)
    elif kind == "ok":   # a hand-painted green blob with a brushed tick
        c.shape("M-2,-16 Q10,-18 15,-8 Q19,3 12,12 Q3,19 -8,14 Q-18,8 -16,-4 Q-13,-15 -2,-16 Z", P.GREEN, sw=2.3,
                light=(-2, -3), shade_k=0.84, highlight="M-11,-6 Q-12,0 -9,6")
        tick = "M-8,0 Q-5,2 -2,7 Q2,-3 9,-8"
        c.line(tick, 6.6)
        c.line(tick, 3.2, P.WHITE)
    else:                # idea: a glowing bulb with rays
        c.line("M0,-17 V-13 M-13,-12 L-10,-9 M13,-12 L10,-9 M-17,0 H-13 M17,0 H13", 2.2)
        c.shape("M-8,-2 Q-8,-11 0,-11 Q8,-11 8,-2 Q8,3 4,6 L4,9 L-4,9 L-4,6 Q-8,3 -8,-2 Z", P.SUN, sw=2.2,
                light=(-2, -2), shade_k=0.86, highlight="M-4.5,-6 Q-6,-3 -5,0")
        c.shape(rounded_rect_d(-4, 9, 8, 5, 1.6), P.METAL_DARK, sw=1.9, light=None)
    return _at(c, x, y, scale)


def board(x: float, y: float, text: str = "", scale: float = 1.0) -> str:
    """An easel with a sheet of paper: instructions pinned up for everyone to read."""
    c = Canvas()
    c.line("M-20,2 L-8,-74 M20,2 L8,-74 M0,-8 L0,-74", 4.4, TRUNK)
    c.line("M-20,2 L-8,-74 M20,2 L8,-74", 1.4)
    c.shape("M-34,-82 H34 V-22 H-34 Z", P.WHITE, sw=2.3, light=(-2, -2), shade_k=0.92)
    c.shape(rounded_rect_d(-36, -86, 72, 7, 2), WOOD, sw=2, light=None)
    size = min(15.0, 96 / max(len(text), 1))   # shrink long labels to the width of the sheet
    c.text(0, -62, text, size)
    c.line("M-24,-52 H24 M-24,-44 H24 M-24,-36 H10", 1.5, opacity=0.5)
    return _at(c, x, y, scale)


# The crate's cable leaves from the lid, curls and ends with the plug lying on the lid, so it never lies under
# anyone's feet; like the cat's tail it curls differently from scene to scene.
# Each entry: the cable's path from the lid, then the plug's x and y.
CRATE_CABLES = (
    ("M20,-44 q6,-18 -6,-20 q-12,-2 -12,10 q0,8 -6,6", -6, -49),
    ("M22,-44 q10,-26 -6,-28 q-16,-2 -14,14 q2,10 -12,10", -12, -49),
    ("M18,-44 q-2,-14 -14,-12 q-12,2 -8,10 q4,6 -14,4", -20, -49),
    ("M24,-44 q8,-12 0,-18 q-10,-8 -18,2 q-6,8 -16,10", -14, -49),
)


def crate(x: float, y: float, text: str = "", scale: float = 1.0, seed: int = 0) -> str:
    """A labelled box with a cable curling from its top: a tool the agent can plug into."""
    c = Canvas()
    cable, plug_x, plug_y = CRATE_CABLES[seed % len(CRATE_CABLES)]
    c.shape("M-34,0 V-44 H34 V0 Z", P.WOOD_LIGHT, sw=2.4, light=(-3, -3), stipple=(10, -42, 24, 42, 14, "right"))
    c.line("M-34,-33 H34 M-34,-11 H34", 1.4, opacity=0.6)
    c.path(rounded_rect_d(-26, -31, 52, 18, 3), P.CREAM, 1.9)
    c.text(0, -17.5, text, min(13.0, 62 / max(len(text), 1)))   # shrink long labels to the plate
    c.line(cable, 3, P.CHARCOAL)                               # out of the lid, curled, the plug lying on top
    c.shape(rounded_rect_d(plug_x - 6, plug_y - 5, 12, 10, 2), P.METAL_DARK, sw=1.8, light=None)
    c.line(f"M{plug_x - 6},{plug_y - 2} h-4 M{plug_x - 6},{plug_y + 2} h-4", 1.8)
    return _at(c, x, y, scale)


def gate(x: float, y: float, text: str = "", scale: float = 1.0) -> str:
    """A striped barrier with a bell: a hook that fires on its own when someone passes."""
    c = Canvas()
    c.shape("M-6,2 V-56 H6 V2 Z", P.METAL_DARK, sw=2.2, light=(-2, 0))
    arm_clip = c.shape("M2,-52 L78,-64 L79,-54 L3,-42 Z", P.WHITE, sw=2.2, light=None, clip=True)
    stripes = "".join(f'<path d="M{12 + i * 20},-70 l10,0 l-6,36 l-10,0 Z" fill="{P.RED}"/>' for i in range(4))
    c.add(f'<g clip-path="url(#{arm_clip})">{stripes}</g>')
    c.path("M2,-52 L78,-64 L79,-54 L3,-42 Z", "none", 2.2)
    c.shape("M-9,-58 Q-9,-72 0,-72 Q9,-72 9,-58 Z", P.YELLOW, sw=2, light=(-2, -2))  # bell
    c.dot(0, -56, 2.4)
    c.path(rounded_rect_d(-22, -34, 44, 15, 3), P.CREAM, 1.9)
    c.text(0, -23, text, min(10.0, 52 / max(len(text), 1)))
    return _at(c, x, y, scale)


def portrait_placeholder() -> str:
    """A stand-in for a photograph that has not been supplied yet; returns a complete `<svg>`."""
    c = Canvas()
    paint = c.gradient([(0, P.SKY), (1, P.SKY_LOW)], 0, 0, 0, 240)
    c.add(f'<rect x="0" y="0" width="200" height="240" fill="{paint}"/>')
    c.shape("M22,240 Q24,170 70,160 L130,160 Q176,170 178,240 Z", P.METAL, sw=2.6, light=(-4, -4))
    c.shape(ellipse_d(100, 104, 44, 52), P.METAL_PALE, sw=2.6, light=(-4, -5))
    c.line("M84,100 q4,-4 8,0 M108,100 q4,-4 8,0 M86,124 Q100,136 114,124", 2.4)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 240" preserveAspectRatio="xMidYMid slice" '
            f'aria-hidden="true">{c.render()}</svg>')

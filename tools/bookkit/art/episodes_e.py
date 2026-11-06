"""Footer episodes, group E: models, hardware, history, the team and the agent at large.

Each is registered with `@episode(name)`; its topic words and the lettering in its picture are under
`footers: name:` in the locale. The props only these stories need are private functions here, drawn like those of
`things.py`: `thing(x, y, k, ...) -> str`, the origin where the thing touches the ground, k = 1 for a 137-unit
professor.
"""
from __future__ import annotations

import math
import random
from collections.abc import Callable

from .. import design as P
from ..design import darken, lighten, mix
from . import props, sets, things
from .characters import module
from .footers import Strip, episode, ground_colors
from .ink import INK, Canvas, ellipse_d, n, rounded_rect_d
from .openers import W, Box, strip_boxes
from .sets import _at, _label, doodle_at


# ============================================================================ helpers
def _on(box: Box, flip: bool, cx: float, cy: float) -> tuple[float, float, float]:
    """A point of a character's own canvas on the page, and the canvas-to-page scale."""
    mod = module(box.name)
    k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
    mid = (box.left + box.right) / 2
    dx = (cx - mod.CENTER_X) * k
    return (mid - dx if flip else mid + dx), box.bottom - (mod.FEET_Y - cy) * k, k


def _air(s: Strip, make, x: float, y: float, w: float, h: float, name: str, group: str | None = None,
         depth: float | None = None, air: float = 4) -> bool:
    """Something in the air (a bird, a page, a note) centred at (x, y), `w` x `h` on the page; only if free."""
    box = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
    if box[1] < 4 or box[0] < s.lo - 20 or box[2] > s.hi + 20 or not s.free(box, air):
        return False
    s.put(depth if depth is not None else s.h + 2, make(x, y), box, name, group=group)
    return True


def _flutter(s: Strip, makers: list, region: tuple, size: float, name: str, tries: int = 30) -> None:
    """A few small flying things (butterflies, notes, birds) at free spots of `region`."""
    left, top, right, bottom = region
    for i, make in enumerate(makers):
        for _ in range(tries):
            if right - left < size or bottom - top < size:
                return
            x, y = s.rnd.uniform(left + size / 2, right - size / 2), s.rnd.uniform(top + size / 2, bottom - size / 2)
            if _air(s, make, x, y, size, size, f"{name}{i}", air=6):
                break


def _sky(s: Strip, low: float = 0.0) -> tuple[float, float, float, float]:
    """The free band of sky (or wall) above the cast and under the strip's melting top fifth, as (left, top,
    right, bottom)."""
    tops = [b.top for b in s.boxes if b.kind == "actor"]
    return (s.lo, s.h * 0.2, s.hi, min(tops, default=s.base) - 6 - low)


def _festoon(s: Strip, spans: int) -> float:
    """Flags strung across a festive sky, the string running on past both edges of the strip (tied somewhere out
    of the picture): crisp, with boxes, below the strip's melting top fifth and clear above everyone's heads.
    Drawn only when there is room; returns the lowest point of the flags (0 if none were hung)."""
    k = s.unit
    size = 12 * k
    span = (W + 20) / spans
    drop = span * 0.12 + size * 1.2              # how far the string sags plus the flags under it
    y = s.h * 0.2 + 4
    clear = min(b.top for b in s.boxes if b.kind == "actor") - 30 * k
    if y + drop > clear:
        return 0
    points = [(-10 + i * span, y) for i in range(spans + 1)]
    boxes = [(max(0, x0), y - 2, min(W, x0 + span), y + drop) for x0, _ in points[:-1]]
    s.put(1.5, sets.bunting(points, seed=s.seed, size=size), boxes, "bunting")
    return y + drop


def _letter_face(kk: float, size: float) -> str:
    """Balloon letters only when they come out big enough on the page; a small plaque gets the flat face, which a
    rim would clog."""
    return "sign" if size * kk >= P.SIGN_BALLOON_FROM else "plain"


def _lettering(kk: float, size: float) -> float:
    """A font size for a prop drawn at scale `kk` that is never under the page's smallest lettering."""
    return max(size, sets.LETTERING_MIN / kk)


def _mark(s: Strip, box: Box, kind: str, flip: bool) -> None:
    """A badge over a character placed with `Strip.actor` (on a pile, a stage), as `Strip.cast` gives one."""
    k = min(1.3, max(0.6, s.tall / 160))
    above = box.top - 18 * k - 2
    x = (box.left + box.right) / 2
    if above > 18 * k + 2:
        mx, my = x, above
    else:
        mx, my = x + (box.right - box.left) * 0.62 * (-1 if flip else 1), box.top + 18 * k
    s.put(box.bottom + 1, props.mark(mx, my, kind, k), (mx - 17 * k, my - 17 * k, mx + 17 * k, my + 17 * k),
          group=box.group)


def _note(x: float, y: float, k: float = 1.0, color: str = INK, double: bool = False) -> str:
    """A music note; the origin is its centre."""
    c = Canvas()
    c.add(f'<ellipse cx="-3" cy="5" rx="4.4" ry="3.4" fill="{color}" transform="rotate(-20 -3 5)"/>')
    c.line("M1,4 V-10", 1.8, color)
    if double:
        c.add(f'<ellipse cx="9" cy="2" rx="4.4" ry="3.4" fill="{color}" transform="rotate(-20 9 2)"/>')
        c.line("M13,1 V-13 L1,-10", 1.8, color)
    else:
        c.line("M1,-10 q7,3 6,10", 1.6, color)
    return _at(c, x, y, k)


def _ladybird(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.shape("M-6,0 Q-7,-8 0,-8 Q7,-8 6,0 Z", P.RED, sw=1.2, light=None)
    c.line("M0,-8 V0", 0.9)
    for dx, dy in ((-3, -4), (3, -5), (3, -2)):
        c.dot(dx, dy, 1.1)
    c.add(f'<circle cx="-7" cy="-3" r="2.4" fill="{INK}"/>')
    return _at(c, x, y, k)


# ============================================================================ 1. floppy_tug
def _floppy_stack(x: float, y: float, k: float = 1.0, label: str = "") -> str:
    """A pile of giant floppies lying flat, fanned out like a hand of cards; 84 wide, 36 tall. The label card on
    its front is never lettered smaller than the page allows, and left off when it would not fit."""
    c = Canvas()
    colors = (P.CHARCOAL, P.RED, P.YELLOW, P.TEAL, P.BLUE, P.VIOLET)
    for i, color in enumerate(colors):
        dx = (-6, 5, -3, 7, -5, 3)[i]
        top = -6 * (i + 1)
        c.add(f'<g transform="rotate({(-3, 2, -1, 3, -2, 1)[i]} {dx} {top + 3})">')
        c.shape(f"M{dx - 36},{top + 6} V{top} H{dx + 36} V{top + 6} Z", color, sw=1.6, light=None)
        c.path(f"M{dx - 10},{top} H{dx + 10} V{top + 6} H{dx - 10} Z", P.METAL_LIGHT, 1)
        c.add("</g>")
    size = _lettering(k, 9)
    w = sets.letter_width(label, size) + size * 1.6
    if label and w <= 80 and size + 8 <= 34:
        h = size + 8
        c.shape(rounded_rect_d(-w / 2, -18 - h / 2, w, h, 3), P.CARD, sw=1.5, light=None)
        sets.fit_label(c, 0, -18 + size * 0.36, label, size, w - size * 1.4, P.PEN, style=_letter_face(k, size))
    return _at(c, x, y, k)


def _floppy_snail(x: float, y: float, k: float = 1.0) -> str:
    """A snail that has swapped its shell for a little floppy disk."""
    c = Canvas()
    c.shape("M-30,0 Q-32,-8 -20,-8 H14 Q22,-8 24,-20 L28,-24 Q30,-8 22,0 Z", P.LEAF_LIGHT, sw=2, light=(-1, -1))
    c.line("M20,-20 l-2,-12 M25,-21 l4,-11", 1.6)
    c.dot(18, -33, 2)
    c.dot(29, -33, 2)
    c.line("M17,-14 q3,3 7,0", 1.2)
    c.add(things.floppy(-6, -6, 1.15, P.RED, -8))
    return _at(c, x, y, k)


def _tug_rope(a: tuple[float, float], b: tuple[float, float], sag: float, width: float) -> tuple[str, list, Callable]:
    """A rope pulled between two hands: a smooth, slightly sagging curve with an ink outline. Returns the drawing,
    boxes along it, and a function giving the point at t (0..1) along it."""
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + sag * 2

    def at(t: float) -> tuple[float, float]:
        u = 1 - t
        return u * u * a[0] + 2 * u * t * cx + t * t * b[0], u * u * a[1] + 2 * u * t * cy + t * t * b[1]

    d = f"M{n(a[0])},{n(a[1])} Q{n(cx)},{n(cy)} {n(b[0])},{n(b[1])}"
    c = Canvas()
    c.line(d, width + 2.4)
    c.line(d, width, P.WOOD_PALE)
    c.add(f'<path d="{d}" fill="none" stroke="{P.WOOD_DARK}" stroke-width="{n(width * 0.3)}" '
          f'stroke-dasharray="{n(width * 0.9)} {n(width * 0.9)}" stroke-opacity=".6"/>')
    return c.render(), strip_boxes([at(i / 10) for i in range(11)], width + 2), at


@episode("floppy_tug")
def floppy_tug(s: Strip) -> None:
    """Tug of war over a floppy: the caterpillar pulls the rope one way, the sparrow the other, a red disk tied in
    the middle - each sure their disk is the one to load. On a pile of giant floppies beside them the agent shrugs:
    either will run. A box of more disks waits at the side, a snail wears a floppy for a shell, a ladybird walks
    the rope."""
    s.outdoors()
    k = s.unit
    s.thing(lambda x, y, k: sets.box_of_floppies(x, y, k * 0.8), 0.06, 116 * 0.8, 62 * 0.8, name="box")
    cat = s.cast("caterpillar", 0.2, "point", "talk", flip=False, mark="!", group="tug")
    bird = s.cast("sparrow", 0.48, "point", "worry", flip=True, mark="!", group="tug")
    a = s.hand(cat, "point", False)
    b = s.hand(bird, "point", True)
    rope, boxes, at = _tug_rope(a, b, 3 * k, 3.4 * k)
    s.put(max(cat.bottom, bird.bottom) + 1, rope, boxes, "rope", group="tug")
    # The prize, tied to the middle of the rope; it never hangs lower than the feet.
    mx, my = at(0.5)
    feet = min(cat.bottom, bird.bottom)
    fk = min(k * 1.2, (feet - my - 9 * k) / 26)
    if fk > k * 0.35:
        fy = my + 5 * k + 24 * fk
        c = Canvas()
        c.line(f"M{n(mx)},{n(my)} V{n(my + 5 * k)}", 1.4 * k)
        c.add(f'<circle cx="{n(mx)}" cy="{n(my)}" r="{n(2.4 * k)}" fill="{P.WOOD_PALE}" stroke="{INK}" '
              f'stroke-width="{n(1.2 * k)}"/>')
        c.add(things.floppy(mx, fy, fk, P.RED))
        s.put(cat.bottom + 2, c.render(), (mx - 13 * fk, my, mx + 13 * fk, fy), "prize", group="tug")
    lx, ly = at(0.74)
    s.put(cat.bottom + 3, _ladybird(lx, ly - 1.6 * k, k * 0.8), None, group="tug")
    px, py = s.thing(lambda x, y, k: _floppy_stack(x, y, k, s.word("fortran")), 0.78, 86, 40, name="pile")
    agent = s.actor("agent", px, py - 37 * k, "shrug", "smile", flip=True, tall=s.tall, group="pile")
    _mark(s, agent, "?", True)
    s.thing(lambda x, y, k: _floppy_snail(x, y, k * 0.55), 0.64, 66 * 0.55, 40 * 0.55, nearer=1.0, name="snail")
    s.thing(lambda x, y, k: props.mushroom(x, y, k * 0.8), 0.97, 22, 24, nearer=0.5, name="mushroom")
    _flutter(s, [lambda x, y: props.butterfly(x, y, k * 0.9, P.PINK),
                 lambda x, y: props.butterfly(x, y, k * 0.8, P.YELLOW)], _sky(s), 18 * k, "fly")


# ============================================================================ 2. machine_museum
def _plinth(x: float, y: float, k: float = 1.0, label: str = "", h: float = 30, w: float = 30) -> str:
    """A museum plinth `w` wide and `h` tall with a plaque on its front (the exhibit goes on top). The plaque's
    lettering is never smaller than the page allows; when it would not fit, the plaque stays blank."""
    c = Canvas()
    c.shape(f"M{-w / 2},0 V{-h} H{w / 2} V0 Z", P.CARD, sw=1.8, light=(-2, -1), shade_k=0.9)
    c.shape(rounded_rect_d(-w / 2 - 3, -h - 4, w + 6, 5, 2), P.STONE, sw=1.5, light=None)
    c.shape(rounded_rect_d(-w / 2 - 3, -3, w + 6, 4, 2), P.STONE, sw=1.5, light=None)
    size = _lettering(k, 8)
    if label and sets.letter_width(label, size) <= (w - 14) * 1.05 and size + 8 <= h - 6:
        ph = size + 8                                       # the plaque keeps an even margin round its word
        c.path(rounded_rect_d(-w / 2 + 3, -h / 2 - ph / 2, w - 6, ph, 2), P.WHITE, 1.1)
        sets.fit_label(c, 0, -h / 2 + size * 0.36, label, size, w - 14, style=_letter_face(k, size))
    return _at(c, x, y, k)


def plinth_width(label: str, kk: float) -> float:
    """How wide a plinth must be for its plaque's word at the scale `kk`."""
    return max(30.0, min(54.0, sets.letter_width(label, _lettering(kk, 8)) + 16))


def _exhibit(c: Canvas, kind: str, top: float) -> None:
    """Draw an exhibit standing at height `top` (negative) on a plinth."""
    t = top
    if kind == "abacus":
        c.path(f"M-14,{t} V{t - 26} H14 V{t} Z", "none", 3, P.WOOD_DARK)
        for row in range(4):
            yy = t - 21 + row * 6
            c.line(f"M-14,{yy} H14", 0.9)
            for b in range(3):
                c.add(f'<circle cx="{-9 + b * 4 + (row % 2) * 6}" cy="{yy}" r="2" '
                      f'fill="{(P.RED, P.YELLOW)[row % 2]}" stroke="{INK}" stroke-width=".7"/>')
    elif kind == "arithmometer":
        c.shape(f"M-15,{t} V{t - 16} H15 V{t} Z", P.METAL_DARK, sw=1.8, light=(-1, -1))
        c.shape(f"M-12,{t - 16} V{t - 22} H10 V{t - 16} Z", P.METAL, sw=1.4, light=None)
        for i in range(5):
            c.dot(-10 + i * 5, t - 8, 1.2, P.WHITE)
        c.line(f"M15,{t - 8} h9 l3,-12", 2.2)
        c.add(f'<circle cx="27" cy="{t - 21}" r="2.8" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>')
    elif kind == "transistor":
        c.line(f"M-4,{t} v-10 M0,{t} v-10 M4,{t} v-10", 1.4, P.METAL_DARK)
        c.shape(f"M-7,{t - 9} V{t - 20} Q-7,{t - 26} 0,{t - 26} Q7,{t - 26} 7,{t - 20} V{t - 9} Z", P.CHARCOAL,
                sw=1.5, light=(-1, -1), shade_k=0.7)
        c.line(f"M-4,{t - 18} h8", 1, P.WHITE, 0.6)
    elif kind == "chip":
        for i in range(4):
            c.line(f"M{-9 + i * 6},{t} v-4 M{-9 + i * 6},{t - 16} v-4", 1.6, P.METAL_DARK)
        c.shape(f"M-12,{t - 4} V{t - 16} H12 V{t - 4} Z", P.CHARCOAL, sw=1.5, light=None)
        c.add(f'<circle cx="-8" cy="{t - 12}" r="1.2" fill="{P.WHITE}"/>')
    elif kind == "laptop":
        c.shape(f"M-14,{t - 3} L-11,{t - 24} H11 L14,{t - 3} Z", P.METAL_DARK, sw=1.6, light=None)
        c.path(f"M-9,{t - 6} L-7,{t - 21} H7 L9,{t - 6} Z", P.SCREEN, 1)
        c.line(f"M-5,{t - 16} l3,2 l-3,2 M0,{t - 12} h4", 1, P.GLOW)
        c.shape(rounded_rect_d(-17, t - 4, 34, 4, 1.5), P.METAL, sw=1.5, light=None)


def _museum_piece(x: float, y: float, k: float = 1.0, kind: str = "abacus", label: str = "", w: float = 30) -> str:
    c = Canvas()
    _exhibit(c, kind, -34)
    return _plinth(x, y, k, label, 30, w) + _at(c, x, y, k)


def _tube_cabinet(x: float, y: float, k: float = 1.0) -> str:
    """A wardrobe-sized cabinet of glowing vacuum tubes behind glass; 46 wide, 84 tall."""
    c = Canvas()
    c.shape("M-23,0 V-84 H23 V0 Z", P.WOOD, sw=2, light=(-2, -2), stipple=(10, -84, 13, 84, 20, "right"))
    c.shape("M-18,-78 H18 V-22 H-18 Z", darken(P.SCREEN_DARK, 0.8), sw=1.6, light=None)
    for row in range(3):
        for col in range(3):
            tx, ty = -11 + col * 11, -30 - row * 18
            c.add(f'<ellipse cx="{tx}" cy="{ty - 6}" rx="5" ry="6" fill="{P.AMBER}" opacity=".35"/>')
            c.shape(f"M{tx - 3},{ty} V{ty - 8} Q{tx - 4},{ty - 14} {tx},{ty - 14} Q{tx + 4},{ty - 14} {tx + 3},"
                    f"{ty - 8} V{ty} Z", lighten(P.WATER_LIGHT, 0.4), sw=1, light=None)
            c.line(f"M{tx},{ty - 2} V{ty - 9}", 1, P.ORANGE)
    c.line("M-18,-78 L-6,-22", 1.4, P.WHITE, 0.3)
    for i in range(4):
        c.add(f'<circle cx="{-12 + i * 8}" cy="-14" r="2" fill="{(P.RED, P.SUN, P.GREEN, P.SUN)[i]}" '
              f'stroke="{INK}" stroke-width=".8"/>')
    return _at(c, x, y, k)


@episode("machine_museum")
def machine_museum(s: Strip) -> None:
    """The museum of computing, one generation per plinth: an abacus, an arithmometer the sparrow points at in
    alarm, a cabinet of glowing tubes, a transistor, a chip, a laptop - and on the last plinth the agent itself,
    posing as an exhibit. The caterpillar points at the chip. Only the short plaques are lettered, so they can be
    read."""
    s.indoors()
    k = s.unit
    w = s.word
    m = 1.18
    kk = k * m

    def piece(kind: str, frac: float, height: float, name: str, label: bool = False) -> None:
        word = w(kind) if label else ""
        wide = plinth_width(word, kk) if label else 30
        s.thing(lambda x, y, k: _museum_piece(x, y, k * m, kind, word, wide), frac, wide + 8, height * m,
                name=name)

    piece("abacus", 0.02, 64, "abacus", label=True)
    piece("arithmometer", 0.125, 58, "arith")
    s.cast("sparrow", 0.225, "point", "worry", flip=True, group="arith", mark="!")
    s.thing(lambda x, y, k: _tube_cabinet(x, y, k * 1.05), 0.33, 50, 90, name="tubes")
    piece("transistor", 0.43, 62, "trans")
    piece("chip", 0.52, 56, "chip", label=True)
    s.cast("caterpillar", 0.62, "point", "talk", flip=True, mark="?")
    piece("laptop", 0.725, 62, "laptop")
    word = w("agent")
    wide = plinth_width(word, kk)
    px, py = s.thing(lambda x, y, k: _plinth(x, y, k * m, word, 30, wide), 0.83, wide + 8, 36 * m, name="plinth")
    s.actor("agent", px, py - 34 * kk, "wave", "wink", flip=True, tall=s.tall * 0.92, group="plinth")
    if s.h < 200:
        return
    y = s.feet(0, 1.0)   # a velvet rope along the front of the gallery
    posts = [s.x(f) for f in (0.07, 0.38, 0.67, 0.9)]
    s.put(y, _rope(posts, y, k), [(p - 4 * k, y - 26 * k, p + 4 * k, y) for p in posts], "rope")
    # The banner hangs on two cords from nails in the wall, under the strip's melting top.
    top = min(b.top for b in s.boxes) - 12
    by = max(s.h * 0.2 + 32 * k, top - 12 * k - 20)
    half = _banner_half(k, w("hall")) + 2
    box = (s.x(0.5) - half * k, by - 32 * k, s.x(0.5) + half * k, by + 13 * k)
    if box[3] < top and s.free(box, 6):
        s.put(3, _banner(s.x(0.5), by, k, w("hall")), box, "banner")


def _rope(posts: list[float], y: float, k: float = 1.0) -> str:
    """Brass posts with a red velvet rope sagging between them, the posts standing at `posts` on line `y`."""
    c = Canvas()
    for a, b in zip(posts, posts[1:], strict=False):
        c.line(f"M{n(a)},{n(y - 22 * k)} Q{n((a + b) / 2)},{n(y - 8 * k)} {n(b)},{n(y - 22 * k)}", 3 * k, P.RED)
    for p in posts:
        c.line(f"M{n(p)},{n(y)} V{n(y - 24 * k)}", 3 * k, P.SUN)
        c.add(f'<circle cx="{n(p)}" cy="{n(y - 25 * k)}" r="{n(3 * k)}" fill="{P.SUN}" stroke="{INK}" '
              f'stroke-width="{n(k)}"/>')
        c.add(f'<ellipse cx="{n(p)}" cy="{n(y)}" rx="{n(6 * k)}" ry="{n(2 * k)}" fill="{P.SUN}" stroke="{INK}" '
              f'stroke-width="{n(k)}"/>')
    return c.render()


def _banner_half(k: float, text: str) -> float:
    """Half the width of the wall banner: its words and a margin of cloth as tall as the margin above them."""
    size = _lettering(k, 11)
    return max(72.0, sets.letter_width(text, size) / 2 + size * 1.1)


def _banner(x: float, y: float, k: float = 1.0, text: str = "") -> str:
    """A cloth banner on two cords across the wall; the origin is its centre."""
    c = Canvas()
    hw = _banner_half(k, text)
    nail = hw - 32
    c.line(f"M{n(-hw + 12)},-12 L{n(-nail)},-30 M{n(hw - 12)},-12 L{n(nail)},-30", 1)
    c.add(f'<circle cx="{n(-nail)}" cy="-30" r="1.6" fill="{INK}"/><circle cx="{n(nail)}" cy="-30" r="1.6" '
          f'fill="{INK}"/>')
    c.shape(f"M{n(-hw)},-12 H{n(hw)} V8 L{n(hw - 8)},12 L{n(hw - 16)},8 H{n(-hw + 16)} L{n(-hw + 8)},12 "
            f"L{n(-hw)},8 Z", P.RED, sw=1.8, light=(-1, -1))
    size = _lettering(k, 11)
    sets.fit_label(c, 0, -2 + size * 0.36, text, size, 2 * hw - size * 2, P.WHITE, style=_letter_face(k, size))
    return _at(c, x, y, k)


# ============================================================================ 3. tube_cucumber
def _cucumber(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.shape("M-24,0 Q-28,-8 -18,-10 Q0,-14 20,-9 Q28,-6 24,0 Q0,4 -24,0 Z", P.LEAF, sw=1.6, light=(-1, -1),
            shade_k=0.75)
    for bx, by in ((-14, -6), (-4, -8), (6, -6), (14, -5), (-8, -3), (10, -2)):
        c.dot(bx, by, 0.9, P.LEAF_LIGHT)
    c.line("M24,-4 q4,-2 5,-6", 1.6, P.LEAF_DARK)
    return _at(c, x, y, k)


def _lying_tube(x: float, y: float, k: float = 1.0) -> str:
    """A vacuum tube lying on its side, pins to the left; about as long as a cucumber."""
    c = Canvas()
    c.line("M-30,-4 h6 M-30,-7 h6 M-30,-10 h6", 1.2, P.METAL_DARK)
    c.shape("M-24,-1 H-14 V-13 H-24 Z", P.CHARCOAL, sw=1.4, light=None)
    c.shape("M-14,-2 H12 Q24,-2 24,-7 Q24,-12 12,-12 H-14 Z", lighten(P.WATER_LIGHT, 0.45), sw=1.5, light=None)
    c.line("M-12,-7 H14", 1.2, P.ORANGE)
    c.line("M-10,-4.5 H8 M-10,-9.5 H8", 0.8, P.METAL_DARK)
    c.line("M-8,-11 Q4,-12 14,-11", 1.4, P.WHITE, 0.7)
    return _at(c, x, y, k)


def _ruler(x: float, y: float, k: float = 1.0, length: float = 60) -> str:
    c = Canvas()
    c.shape(f"M0,0 V-6 H{length} V0 Z", P.SUN, sw=1.3, light=None)
    for i in range(int(length / 4) + 1):
        c.line(f"M{i * 4},-6 v{2.6 if i % 5 else 4.2}", 0.7)
    return _at(c, x, y, k)


def _loaf(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.shape("M-30,0 Q-34,-22 -10,-24 Q10,-28 26,-20 Q36,-12 30,0 Z", P.AMBER, sw=2, light=(-2, -2),
            highlight="M-20,-18 Q-8,-23 6,-22")
    c.line("M-16,-20 q6,5 2,12 M-2,-23 q6,5 2,12 M12,-22 q6,5 2,12", 1.6, P.WOOD_DARK)
    return _at(c, x, y, k)


def _graphics_card(x: float, y: float, k: float = 1.0, label: str = "") -> str:
    """A bare graphics card lying on its back: a long shroud with three fans, its name at the left end, and the
    gold edge; 96 x 24. The name is lettered no smaller than the page allows."""
    c = Canvas()
    c.shape("M-48,0 V-6 H48 V0 Z", P.GREEN, sw=1.4, light=None)
    for i in range(10):
        c.add(f'<rect x="{-40 + i * 4}" y="-1.6" width="2.4" height="3" fill="{P.SUN}" stroke="{INK}" '
              f'stroke-width=".5"/>')
    c.shape("M-50,-6 L-46,-26 H46 L50,-6 Z", P.CHARCOAL, sw=2, light=(-2, -2), shade_k=0.75)
    for fx in (-5, 16, 36):
        c.shape(ellipse_d(fx, -16, 9.5, 7.5), P.METAL_DARK, sw=1.3, light=None)
        for a in range(0, 360, 60):
            c.line(f"M{fx},-16 l{n(8 * math.cos(math.radians(a)))},{n(6 * math.sin(math.radians(a)))}", 1.2,
                   P.METAL_LIGHT)
        c.dot(fx, -16, 1.8, P.METAL_LIGHT)
    c.line("M-44,-24 H44", 1.6, P.GREEN)
    c.shape("M50,-6 V-30 H56 V-6 Z", P.METAL, sw=1.4, light=None)
    size = min(16.0, _lettering(k, 10))
    if label:
        sets.fit_label(c, -30, -16 + size * 0.36, label, size, 26, P.SUN, style=_letter_face(k, size))
    return _at(c, x, y, k)


def _bench(x: float, y: float, k: float = 1.0, w: float = 150, h: float = 30) -> str:
    """A low workbench `w` wide, its top `h` up."""
    c = Canvas()
    c.line(f"M{-w / 2 + 8},0 V{-h + 4} M{w / 2 - 8},0 V{-h + 4}", 4, P.WOOD_DARK)
    c.line(f"M{-w / 2 + 8},{-h * 0.35} H{w / 2 - 8}", 2.4, P.WOOD_DARK)
    c.shape(rounded_rect_d(-w / 2, -h - 2, w, 7, 2), P.WOOD_LIGHT, sw=1.8, light=None)
    return _at(c, x, y, k)


def _pickle_jar(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.shape("M-12,0 V-26 Q-12,-30 -8,-30 H8 Q12,-30 12,-26 V0 Z", lighten(P.WATER_LIGHT, 0.4), sw=1.6, light=None)
    for px, py, t in ((-5, -8, 80), (4, -10, 100), (-3, -19, 70), (5, -20, 95)):
        c.add(f'<ellipse cx="{px}" cy="{py}" rx="3" ry="7" fill="{P.LEAF}" stroke="{INK}" stroke-width=".8" '
              f'transform="rotate({t - 90} {px} {py})"/>')
    c.shape(rounded_rect_d(-13, -35, 26, 6, 2), P.RED, sw=1.4, light=None)
    c.line("M-13,-32 h26", 0.8, P.WHITE, 0.6)
    return _at(c, x, y, k)


@episode("tube_cucumber")
def tube_cucumber(s: Strip) -> None:
    """On the kitchen table the caterpillar has laid an old radio tube beside a real
    cucumber and measures both with a ruler: the same size. On the bench beyond, a modern graphics card lies
    beside a loaf of bread - and is bigger than the loaf; the agent weighs it up. A jar of pickles waits on its stool,
    the kettle is on the shelf."""
    s.indoors()
    k = s.unit
    y = s.base - s.tall * 0.86
    if y - 30 * k > 8:
        x = s.x(0.36)
        s.put(5, things.wall_shelf(x, y, k, 110, ("jar", "pot", "jar")), (x - 57 * k, y - 28 * k, x + 57 * k,
                                                                       y + 14 * k), "shelf")
    s.thing(lambda x, y, k: things.stool(x, y, k * 0.8, P.BLUE) + _pickle_jar(x, y - 32 * k, k * 0.9), 0.02,
            28, 64, name="jar")
    s.cast("caterpillar", 0.115, "point", "talk", flip=False, mark="?")
    tx, ty = s.thing(lambda x, y, k: things.kitchen_table(x, y, k, 120, P.WOOD_LIGHT, P.RED), 0.31, 124, 50,
                     name="table", backdrop=True)
    top = ty - 48 * k
    s.put(top + 0.4, _lying_tube(tx - 29 * k, top, k * 1.3), None, group="table")
    s.put(top + 0.4, _cucumber(tx + 29 * k, top, k * 1.3), None, group="table")
    s.put(top + 0.6, _ruler(tx - 50 * k, top + 3 * k, k, 100), None, group="table")
    bx, by = s.thing(lambda x, y, k: _bench(x, y, k, 176, 30), 0.6, 178, 34, name="bench")
    btop = by - 31 * k
    s.put(btop + 0.4, _graphics_card(bx - 30 * k, btop, k * 1.35, s.word("gpu")), None, group="bench")
    s.put(btop + 0.4, _loaf(bx + 62 * k, btop, k * 0.8), None, group="bench")
    s.cast("agent", 0.81, "think", "smile", flip=True, mark="idea")


# ============================================================================ 4. supercomputer
def _supercomputer(x: float, y: float, k: float = 1.0, label: str = "") -> str:
    """A big C-shaped supercomputer seen from a little above: a ring of tall cabinets open at the front, a
    padded bench running round its foot; 124 wide, 100 tall."""
    c = Canvas()
    rx, ry = 50, 12
    colors = (P.RED, P.ORANGE, P.SUN, P.GREEN, P.TEAL, P.BLUE, P.VIOLET, P.PINK)
    cols = []
    for i, color in enumerate(colors):
        a = math.radians(150 + i * 32)          # the opening faces the front right
        cols.append((math.sin(a), math.cos(a) * rx, math.sin(a) * ry, color))
    for depth, cx, cy, color in sorted(cols):
        top = -96 + cy
        bottom = -28 + cy
        w = 15
        c.shape(f"M{n(cx - w / 2)},{n(bottom)} V{n(top)} H{n(cx + w / 2)} V{n(bottom)} Z", color, sw=1.8,
                light=(-1.5, -1), shade_k=0.78)
        c.shape(ellipse_d(cx, top, w / 2, 3), lighten(color, 0.3), sw=1.4, light=None)
        c.line(f"M{n(cx - 3.5)},{n(top + 8)} V{n(bottom - 6)}", 1, P.WHITE, 0.35)
        if depth > 0:
            c.add(f'<circle cx="{n(cx)}" cy="{n(top + 22)}" r="1.8" fill="{P.GLOW}" stroke="{INK}" '
                  f'stroke-width=".6"/>')
    # The bench: a padded ring round the foot, seen from the front.
    c.shape("M-62,-6 Q-64,-30 -48,-32 H48 Q64,-30 62,-6 Q0,6 -62,-6 Z", P.LEATHER, sw=2, light=(-2, -2))
    for bx in (-40, -14, 12, 38):
        c.line(f"M{bx},-29 Q{bx + 2},-16 {bx},-3", 1.2, darken(P.LEATHER, 0.7))
    c.line("M-58,-26 Q0,-18 58,-26", 1.2, lighten(P.LEATHER, 0.3))
    size = _lettering(k, 8)
    w = sets.letter_width(label, size) + size * 1.8
    if label and w <= 112:     # a name plate across the cabinets, only when it can be read with room round it
        c.shape(rounded_rect_d(-w / 2, -70 - (size + 8) / 2, w, size + 8, 3), P.CARD, sw=1.5, light=None)
        sets.fit_label(c, 0, -70 + size * 0.36, label, size, w - size * 1.6, style=_letter_face(k, size))
    return _at(c, x, y, k)


def _kettle(x: float, y: float, k: float = 1.0) -> str:
    """A kettle on a stool, steaming; 30 wide, 64 tall."""
    c = Canvas()
    c.add(things.stool(0, 0, 0.75, P.RED))
    t = -30
    c.line(f"M2,{t - 26} q-4,-6 0,-11 M8,{t - 27} q4,-6 0,-12", 1.4, P.WHITE, 0.9)
    c.line(f"M-8,{t - 18} Q0,{t - 30} 8,{t - 18}", 2.2)
    c.shape(f"M-11,{t} Q-13,{t - 16} 0,{t - 18} Q13,{t - 16} 11,{t} Z", P.TEAL, sw=1.8, light=(-1, -1))
    c.shape(f"M10,{t - 8} L19,{t - 16} L20,{t - 13} L12,{t - 4} Z", P.TEAL, sw=1.4, light=None)
    c.add(f'<circle cx="0" cy="{t - 19}" r="2" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>')
    return _at(c, x, y, k)


def _desk_with_abacus(x: float, y: float, k: float = 1.0) -> str:
    """A small writing desk with an abacus and a stack of scribbled sheets."""
    c = Canvas()
    c.add(things.kitchen_table(0, 0, 0.7, 80, P.WOOD, None))
    t = -34
    c.path(f"M-30,{t} V{t - 16} H-6 V{t} Z", "none", 2.2, P.WOOD_DARK)
    for row in range(3):
        yy = t - 12 + row * 4.6
        c.line(f"M-30,{yy} H-6", 0.7)
        for b in range(3):
            c.add(f'<circle cx="{-26 + b * 3.2 + (row % 2) * 6}" cy="{yy}" r="1.5" fill="{(P.RED, P.SUN)[row % 2]}" '
                  f'stroke="{INK}" stroke-width=".5"/>')
    for i in range(4):
        c.shape(f"M{2 + i},{t - 1 - i * 2} H{26 + i} V{t - 3 - i * 2} H{2 + i} Z", P.CARD, sw=0.9, light=None)
    c.line(f"M6,{t - 9} q4,-2 8,0 q4,2 8,0", 0.8, P.PEN)
    return _at(c, x, y, k)


def _flying_sheet(x: float, y: float, k: float, turn: float, ux: float, uy: float) -> str:
    """A sheet of sums thrown into the air, the origin its centre, flying along (ux, uy): three speed lines
    trail behind it, back towards where it came from."""
    c = Canvas()
    c.shape("M-11,-14 H8 L11,-11 V14 H-11 Z", P.CARD, sw=1.4, light=None)
    c.path("M8,-14 V-11 H11", P.CARD, 1.1)
    for i in range(5):
        c.line(f"M-7,{-9 + i * 5} q3,-2 5,0 q3,2 6,0", 0.9, P.PEN)
    sheet = _at(c, x, y, k, turn=turn)
    px, py = -uy, ux
    lines = Canvas()
    for side in (-1, 0, 1):
        start = 15 + abs(side) * 3
        length = 11 - abs(side) * 3
        ox, oy = x + px * side * 7 * k, y + py * side * 7 * k
        lines.line(f"M{n(ox - ux * start * k)},{n(oy - uy * start * k)} l{n(-ux * length * k)},"
                   f"{n(-uy * length * k)}", 1.5 * k, P.PEN, 0.75)
    return lines.render() + sheet


def _teacup(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.line("M-3,-12 q-3,-5 0,-9 M3,-13 q3,-5 0,-9", 1.2, P.METAL, 0.9)
    c.shape("M-7,-11 H7 Q7,0 0,0 Q-7,0 -7,-11 Z", P.WHITE, sw=1.4, light=None)
    c.line("M7,-8 q5,0 4,4 q-1,3 -5,2", 1.3)
    c.add(f'<circle cx="-2" cy="-6" r="1.4" fill="{P.RED}"/>')
    c.shape(ellipse_d(0, 1, 10, 2.2), P.WHITE, sw=1.2, light=None)
    return _at(c, x, y, k)


def _stopwatch(x: float, y: float, k: float = 1.0) -> str:
    """A stopwatch; the origin is its centre."""
    c = Canvas()
    c.line("M0,-12 V-16 M-4,-17 h8", 2)
    c.line("M8,-10 l3,-3", 2)
    c.shape(ellipse_d(0, 0, 11, 11), P.METAL_LIGHT, sw=1.6, light=None)
    c.shape(ellipse_d(0, 0, 8, 8), P.WHITE, sw=1, light=None)
    c.line("M0,0 L4,-6", 1.4, P.RED)
    return _at(c, x, y, k)


def _socket(x: float, y: float, k: float = 1.0) -> str:
    """A wall socket with a black plug pushed into it, its cable going down; the origin is the socket's centre."""
    c = Canvas()
    c.shape(rounded_rect_d(-9, -9, 18, 18, 3), P.WHITE, sw=1.6, light=None)
    c.shape(ellipse_d(0, 0, 6, 6), P.CARD, sw=1.1, light=None)
    c.shape("M-4.5,-4 H4.5 V5 Q0,9 -4.5,5 Z", P.CHARCOAL, sw=1.4, light=(-1, -1))
    return _at(c, x, y, k)


@episode("supercomputer")
def supercomputer(s: Strip) -> None:
    """The cat races the machine by hand - abacus clacking, sheets of sums flying off his desk - while the agent
    stands at ease by the big C-shaped supercomputer with a cup of tea from the kettle beside it. The sparrow keeps
    time with a stopwatch in his wing; the machine's fat cable runs across the floor to the socket in the wall."""
    s.indoors()
    k = s.unit
    cat = s.cast("cat", 0.05, "point", "worry", flip=False, group="desk", mark="!")
    # The desk stands so that the cat's paw is on the abacus.
    dk = k * 1.25
    hx, _ = s.hand(cat, "point", False)
    dx, dy = hx + 29 * dk, cat.bottom
    s.put(dy - 1, _desk_with_abacus(dx, dy, dk), (dx - 36 * dk, dy - 52 * dk, dx + 36 * dk, dy), "desk", group="desk")
    sx, sy = s.thing(lambda x, y, k: _supercomputer(x, y, k, s.word("super")), 0.415, 128, 100, name="super")
    # The sheets fly up off the stack on the desk, each trailing speed lines back towards it.
    ox, oy = dx + 14 * dk, dy - 44 * dk
    for i, (angle, dist, turn) in enumerate(((62, 46, -18), (95, 62, 14), (40, 70, 24), (118, 84, -8))):
        a = math.radians(angle)
        ux, uy = math.cos(a), -math.sin(a)
        x, y = ox + ux * dist * k, oy + uy * dist * k
        back = 26 * k
        box = (min(x - 13 * k, x - ux * back - 8 * k), min(y - 15 * k, y - uy * back - 8 * k),
               max(x + 13 * k, x - ux * back + 8 * k), max(y + 15 * k, y - uy * back + 8 * k))
        if box[1] > 6 and s.free(box, 4):
            s.put(s.h + 2, _flying_sheet(x, y, k * 0.9, turn, ux, uy), box, f"page{i}", group="desk")
    agent = s.cast("agent", 0.575, "type", "smile", flip=True, size=0.92)     # beside the machine, not over its name
    lx, ly = s.hand(agent, "type", True, "left")
    rx, ry = s.hand(agent, "type", True, "right")
    s.put(agent.bottom + 1, _teacup((lx + rx) / 2, max(ly, ry) + 2 * k, k * 0.9), None, group=agent.group)
    s.thing(lambda x, y, k: _kettle(x, y, k), 0.65, 30, 64, name="kettle")
    bird = s.cast("sparrow", 0.775, "point", "talk", flip=True)
    wx, wy = s.hand(bird, "point", True)
    # The stopwatch hangs by its crown from the wing's tip: drawn behind the bird, the feathers close over it.
    s.put(bird.bottom - 0.5, _stopwatch(wx, wy + 12 * k * 0.8, k * 0.8),
          (wx - 10 * k, wy - 2 * k, wx + 10 * k, wy + 22 * k), group=bird.group)
    # The socket low on the wall, the cable from the machine's foot along the floor and up into it.
    px = s.x(0.95)
    py = s.base - 12 * k
    s.put(3, _socket(px, py, k), (px - 10 * k, py - 10 * k, px + 10 * k, py + 10 * k), "socket")
    cy = s.feet(px, 0.5)
    s.put(sy - 40 * k, sets.cable([(sx + 58 * k, sy - 8 * k), (sx + 78 * k, cy), (px - 16 * k, cy),
                                   (px, cy - 2 * k), (px, py + 3 * k)], P.CHARCOAL, 3 * k), None)


# ============================================================================ the seaside, shared by 5 and 6
def _shore(s: Strip) -> float:
    """Sky over the sea and a sandy beach instead of the meadow; returns the top of the sea band."""
    s.relook(season="summer")
    s.outdoors(hills=False)
    c, k = s.back, s.unit
    top = s.base - max(10, min(44, s.base * 0.16))
    sea = c.gradient([(0, P.WATER), (1, P.WATER_LIGHT)], 0, top, 0, s.base + 8)
    c.add(f'<rect x="-4" y="{n(top)}" width="{W + 8}" height="{n(s.base + 8 - top)}" fill="{sea}"/>')
    c.add(f'<path d="M-4,{n(top)} H{W + 4}" stroke="{darken(P.WATER, 0.85)}" stroke-width="1.4"/>')
    for i in range(int(W / 60)):
        x = 20 + i * 60 + (i % 3) * 9
        y = top + (s.base - top) * (0.3 + 0.25 * (i % 3))
        c.add(f'<path d="M{x},{n(y)} q5,-4 10,0 q5,-4 10,0" fill="none" stroke="{P.WHITE}" '
              f'stroke-width="{n(1.4 * min(1.0, k))}" stroke-linecap="round"/>')
    sand = c.gradient([(0, lighten(P.SAND, 0.2)), (1, P.SAND)], 0, s.base, 0, s.h)
    c.add(f'<path d="M-4,{n(s.base + 6)} Q{W * 0.25},{n(s.base + 1)} {W * 0.5},{n(s.base + 5)} '
          f'T{W + 4},{n(s.base + 4)} V{n(s.h + 4)} H-4 Z" fill="{sand}" stroke="{INK}" stroke-width="1.6"/>')
    c.add(f'<path d="M-4,{n(s.base + 9)} Q{W * 0.3},{n(s.base + 3)} {W * 0.55},{n(s.base + 8)} T{W + 4},'
          f'{n(s.base + 7)}" fill="none" stroke="{P.WHITE}" stroke-width="2" stroke-opacity=".8"/>')
    rnd = s.rnd
    for _ in range(int(40 + s.h / 4)):   # grains
        x, y = rnd.uniform(0, W), rnd.uniform(s.base + 12, s.h - 2)
        c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r=".9" fill="{darken(P.SAND, 0.75)}" opacity=".6"/>')
    return top


def _sea_thing(s: Strip, make, top: float, w: float, h: float, name: str) -> None:
    """Something far out on the sea band (a sail, a water skier), where no one stands in front of it."""
    for frac in (0.5, 0.62, 0.38, 0.75, 0.25, 0.86, 0.14):
        x = s.x(frac)
        y = top + (s.base - top) * 0.7
        box = (x - w / 2, y - h, x + w / 2, y)
        if s.free(box, 4):
            s.put(2, make(x, y), box, name)
            return


def _gulls(s: Strip, count: int = 3) -> None:
    k = s.unit
    region = (s.lo, s.h * 0.2, s.hi, max(s.h * 0.2 + 2, s.base * 0.6))
    _flutter(s, [lambda x, y: props.bird(x, y, k * 1.1) for _ in range(count)], region, 22 * k, "gull")


def _shell(x: float, y: float, k: float = 1.0, color: str = P.PINK_PALE, turn: float = 0) -> str:
    """A scallop shell lying on the sand, hinge down: a ribbed fan with a wavy rim and the two little ears at the
    hinge; 13 wide, 9 tall, the origin at the hinge."""
    c = Canvas()
    ribs = 7
    apex = (0.0, -0.6)
    r_in, r_out = 6.0, 6.9                      # the rim dips between the ribs and bulges at each rib
    a0, a1 = math.radians(-160), math.radians(-20)
    rim = []
    for i in range(ribs + 1):
        a = a0 + (a1 - a0) * i / ribs
        rim.append((apex[0] + math.cos(a) * r_in, apex[1] + math.sin(a) * r_in * 1.05))
    d = f"M{n(apex[0])},{n(apex[1])} L{n(rim[0][0])},{n(rim[0][1])}"
    for i in range(ribs):
        am = a0 + (a1 - a0) * (i + 0.5) / ribs
        qx, qy = apex[0] + math.cos(am) * r_out * 1.08, apex[1] + math.sin(am) * r_out * 1.12
        d += f" Q{n(qx)},{n(qy)} {n(rim[i + 1][0])},{n(rim[i + 1][1])}"
    d += " Z"
    c.shape("M-3.6,-1.6 L3.6,-1.6 L2.8,0.9 Q0,1.6 -2.8,0.9 Z", darken(color, 0.92), sw=0.9, light=None)
    c.shape(d, color, sw=1.1, light=(-0.9, -0.9), shade_k=0.84)
    grooves = ""
    for i in range(1, ribs):
        a = a0 + (a1 - a0) * i / ribs
        grooves += (f"M{n(apex[0] + math.cos(a) * 1.4)},{n(apex[1] + math.sin(a) * 1.4)} "
                    f"L{n(apex[0] + math.cos(a) * r_in * 0.97)},{n(apex[1] + math.sin(a) * r_in)} ")
    c.line(grooves, 0.6, darken(color, 0.62))
    return _at(c, x, y, k, turn=turn)


def _starfish(x: float, y: float, k: float = 1.0, color: str = P.ORANGE) -> str:
    c = Canvas()
    pts = []
    for i in range(10):
        r = 9 if i % 2 == 0 else 4
        a = math.radians(-90 + i * 36)
        pts.append(f"{n(math.cos(a) * r)},{n(math.sin(a) * r * 0.7 - 6)}")
    c.shape("M" + " L".join(pts) + " Z", color, sw=1.3, light=None)
    c.dot(-1, -7, 0.8)
    c.dot(2, -6, 0.8)
    return _at(c, x, y, k)


# ============================================================================ 5. beach_find
def _sandcastle(x: float, y: float, k: float = 1.0, flag: str = P.RED) -> str:
    """A sandcastle with three towers and a flag; 44 wide, 50 tall."""
    c = Canvas()
    c.line("M0,-48 V-62", 1.2)
    c.shape("M0,-62 L10,-58 L0,-54 Z", flag, sw=1, light=None)
    for tx, th in ((-14, 30), (14, 30), (0, 48)):
        c.shape(f"M{tx - 8},0 V{-th} h3 v-4 h3 v4 h4 v-4 h3 v4 h3 V0 Z", P.SAND, sw=1.6, light=(-1.5, -1),
                shade_k=0.85)
        c.path(f"M{tx - 2},{-th + 12} q2,-4 4,0 v4 h-4 Z", darken(P.SAND, 0.6), 1)
    c.shape("M-22,0 V-14 H22 V0 Z", P.SAND, sw=1.6, light=(-1, -1), shade_k=0.85)
    c.path("M-4,0 V-7 Q0,-11 4,-7 V0 Z", darken(P.SAND, 0.6), 1.2)
    c.add(_shell(14, -3, 0.6, P.PINK))
    return _at(c, x, y, k)


def _deckchair(x: float, y: float, k: float = 1.0) -> str:
    """A striped deck chair, a towel over its back; 56 wide, 50 tall."""
    c = Canvas()
    c.line("M-24,0 L14,-50 M22,0 L-4,-24 M-22,-16 L20,-16", 3, P.WOOD_DARK)
    sling = "M5,-50 L19,-46 Q6,-24 -8,-12 L-23,-18 Q-6,-28 5,-50 Z"
    clip = c.shape(sling, P.WHITE, sw=1.6, light=None, clip=True)
    stripes = "".join(f'<path d="M-30,{-50 + i * 8} L30,{-62 + i * 8} v4 L-30,{-46 + i * 8} Z" fill="{P.BLUE}"/>'
                      for i in range(8))
    c.add(f'<g clip-path="url(#{clip})">{stripes}</g>')
    c.path(sling, "none", 1.6)
    c.shape("M10,-50 Q16,-54 20,-48 L14,-34 Q10,-32 6,-36 Z", P.SUN, sw=1.2, light=None)
    return _at(c, x, y, k)


def _umbrella(x: float, y: float, k: float = 1.0) -> str:
    """A big striped beach umbrella stuck in the sand; 110 wide, 140 tall."""
    c = Canvas()
    c.line("M4,0 L-2,-128", 3, P.WOOD_DARK)
    d = "M-56,-108 Q-50,-140 -2,-142 Q46,-140 52,-108 Q40,-114 30,-106 Q18,-114 6,-106 Q-6,-114 -18,-106 " \
        "Q-30,-114 -42,-106 Q-50,-112 -56,-108 Z"
    clip = c.shape(d, P.WHITE, sw=0, light=None, clip=True)
    wedges = "".join(f'<path d="M-2,-142 L{-70 + i * 24},-100 L{-58 + i * 24},-100 Z" fill="{P.RED}"/>'
                     for i in range(6))
    c.add(f'<g clip-path="url(#{clip})">{wedges}</g>')
    c.path(d, "none", 2)
    c.shape(ellipse_d(-2, -144, 3, 3), P.RED, sw=1.2, light=None)
    c.add(f'<ellipse cx="2" cy="2" rx="40" ry="5" fill="{darken(P.SAND, 0.8)}" opacity=".5"/>')
    return _at(c, x, y, k)


def _calc_size(k: float, display: str) -> tuple[float, float, float]:
    """(lettering, body width, body height) of the dug-up calculator: the body grows to hold its digits, which are
    never under the page's smallest lettering."""
    size = _lettering(k, 11)
    cw = max(56.0, sets.letter_width(display, size, style="plain") + 12 + size * 1.6)
    return size, cw, cw * 1.32


def _dug_calculator(x: float, y: float, k: float = 1.0, display: str = "") -> str:
    """A giant pocket calculator half buried in a soft mound of sand, standing tilted out of it, a beach spade
    stuck into the mound beside it; about 2.3 calculator widths wide, the origin on the ground under the middle."""
    c = Canvas()
    size, cw, ch = _calc_size(k, display)
    sand = P.SAND
    m = cw * 0.98                                 # the mound's half-width
    # the soft contact shadow on the beach, then the back of the mound
    c.add(f'<ellipse cx="{n(cw * 0.08)}" cy="1" rx="{n(m * 1.02)}" ry="{n(4.5)}" fill="{darken(P.SAND, 0.7)}" '
          f'opacity=".4"/>')
    back = (f"M{n(-m)},0 C{n(-m * 0.8)},{n(-ch * 0.08)} {n(-m * 0.66)},{n(-ch * 0.46)} {n(-m * 0.18)},"
            f"{n(-ch * 0.5)} C{n(m * 0.22)},{n(-ch * 0.54)} {n(m * 0.6)},{n(-ch * 0.36)} {n(m * 0.8)},{n(-ch * 0.14)} "
            f"C{n(m * 0.9)},{n(-ch * 0.04)} {n(m * 0.96)},0 {n(m)},0 Z")
    c.shape(back, sand, sw=1.8, light=(-3, -2), shade_k=0.86, stipple=(-m, -ch * 0.45, 2 * m, ch * 0.45, 26, "bottom"))
    # the calculator, standing tilted out of the sand
    top = -ch * 1.12
    c.add(f'<g transform="rotate(-13 0 {n(-ch * 0.12)})">')
    c.shape(rounded_rect_d(-cw / 2, top, cw, ch, 7), P.CHARCOAL, sw=2.2, light=(-2.5, -2.5), shade_k=0.7)
    dh = size + 10
    c.shape(rounded_rect_d(-cw / 2 + 6, top + 7, cw - 12, dh, 3), P.HILL_FAR, sw=1.6, light=None)
    c.add(f'<path d="M{n(-cw / 2 + 9)},{n(top + 10)} h{n(cw * 0.3)}" stroke="{P.WHITE}" stroke-width="1.6" '
          f'stroke-linecap="round" opacity=".6"/>')
    if display:
        pad = size * 0.7                          # digits keep clear of the window's edges, right-aligned
        sets.fit_label(c, cw / 2 - 6 - pad, top + 7 + dh / 2 + size * 0.42, display, size, cw - 12 - 2 * pad,
                       P.CHARCOAL, anchor="end", style="plain")
    kw = (cw - 12 - 3 * 4) / 4
    kh = kw * 0.66
    for row in range(5):
        for col in range(4):
            color = P.ORANGE if col == 3 else P.METAL_PALE
            kx, ky = -cw / 2 + 6 + col * (kw + 4), top + 7 + dh + 7 + row * (kh + 4)
            c.shape(rounded_rect_d(kx, ky, kw, kh, 2), color, sw=1.2, light=(-0.8, -0.8), shade_k=0.8)
    c.add("</g>")
    # the beach spade, stuck into the mound at a slant, its blade half in the sand
    c.add(f'<g transform="translate({n(m * 0.6)},{n(-ch * 0.27)}) rotate(26)">')
    c.tube(f"M0,-6 V{n(-ch * 0.62)}", P.WOOD, 3.2, sw=1.4)
    c.shape(f"M-7,{n(-ch * 0.62 - 2.5)} h14 a2.5,2.5 0 0 1 0,5 h-14 a2.5,2.5 0 0 1 0,-5 Z", P.WOOD, sw=1.4,
            light=None)
    c.shape("M-8,-9 Q0,-12 8,-9 Q9,4 6,12 Q3,18 0,20 Q-3,18 -6,12 Q-9,4 -8,-9 Z", P.RED, sw=1.6,
            light=(-1.5, -1), shade_k=0.8)
    c.line("M0,-7 V12", 1.1, darken(P.RED, 0.7), 0.7)
    c.add("</g>")
    # the front of the mound: sand heaped against the calculator and over the lower half of the blade
    front = (f"M{n(-m * 0.97)},0 C{n(-m * 0.8)},{n(-ch * 0.1)} {n(-m * 0.6)},{n(-ch * 0.36)} {n(-m * 0.3)},"
             f"{n(-ch * 0.37)} C{n(-m * 0.1)},{n(-ch * 0.4)} {n(m * 0.18)},{n(-ch * 0.3)} {n(m * 0.4)},"
             f"{n(-ch * 0.31)} C{n(m * 0.56)},{n(-ch * 0.32)} {n(m * 0.7)},{n(-ch * 0.2)} {n(m * 0.76)},"
             f"{n(-ch * 0.12)} C{n(m * 0.82)},{n(-ch * 0.04)} {n(m * 0.9)},0 {n(m * 0.98)},0 Z")
    c.shape(front, sand, sw=0, light=(-2, -1.5), shade_k=0.9,
            stipple=(-m, -ch * 0.4, 2 * m, ch * 0.4, 34, "bottom"))
    c.path(front[:-2], "none", 1.6)              # only its top: the sand ridge
    c.add(f'<path d="M{n(-m * 0.56)},{n(-ch * 0.3)} q{n(m * 0.15)},-3 {n(m * 0.3)},-1" fill="none" '
          f'stroke="{P.WHITE}" stroke-width="1.6" stroke-linecap="round" opacity=".55"/>')
    # little heaps of sand thrown out of the hole
    for lx, r in ((-m * 1.1, 4.5), (-m * 1.22, 2.6), (m * 1.08, 3.6)):
        c.shape(f"M{n(lx - r * 1.6)},0.5 Q{n(lx - r * 0.8)},{n(-r * 1.3)} {n(lx)},{n(-r * 1.2)} "
                f"Q{n(lx + r * 0.8)},{n(-r * 1.3)} {n(lx + r * 1.6)},0.5 Z", sand, sw=1.2, light=(-0.8, -0.6),
                shade_k=0.86)
    return _at(c, x, y, k)


def _flippers(box: Box, flip: bool) -> str:
    """Green swimming flippers on the cat's feet."""
    out = []
    for fx in (112, 168):
        x, y, kk = _on(box, flip, fx, 322)
        c = Canvas()
        c.shape("M-10,0 Q-12,-10 0,-12 Q16,-12 24,-6 L30,-2 L24,2 Z", P.GREEN, sw=2, light=None)
        c.line("M6,-8 L14,-4 M10,-10 L20,-5", 1.4, darken(P.GREEN, 0.7))
        out.append(_at(c, x, y, kk, mirror=flip))
    return "".join(out)


def _rubber_ring(box: Box, flip: bool) -> str:
    """A red and white rubber ring round the caterpillar's middle."""
    x, y, kk = _on(box, flip, 104, 190)
    c = Canvas()
    c.add(f'<ellipse cx="0" cy="0" rx="66" ry="17" fill="none" stroke="{INK}" stroke-width="26"/>')
    c.add(f'<ellipse cx="0" cy="0" rx="66" ry="17" fill="none" stroke="{P.WHITE}" stroke-width="21"/>')
    c.add(f'<ellipse cx="0" cy="0" rx="66" ry="17" fill="none" stroke="{P.RED}" stroke-width="21" '
          f'stroke-dasharray="26 26"/>')
    c.line("M-50,-8 Q-30,-16 -10,-17", 3, P.WHITE, 0.6)
    return _at(c, x, y, kk)


@episode("beach_find")
def beach_find(s: Strip) -> None:
    """On the beach the sparrow has dug a giant calculator out of
    the sand and is very pleased with it; the cat, in flippers under the umbrella, only smirks; the caterpillar
    in her rubber ring has come to see. Sandcastles, a deck chair, a starfish, gulls overhead, and a sail far out
    at sea."""
    top = _shore(s)
    k = s.unit
    s.thing(lambda x, y, k: _sandcastle(x, y, k * 0.9), 0.02, 42, 56, name="castle")
    ux, uy = s.thing(lambda x, y, k: _umbrella(x, y, k * 0.95), 0.175, 108, 140, name="umbrella")
    cat = s.actor("cat", ux + 6 * k, uy + 2 * k, "stand", "wink", flip=False, tall=s.tall, group="umbrella",
                  depth=uy + 3)
    s.put(uy + 4, _flippers(cat, False), None, group="umbrella")
    s.thing(lambda x, y, k: _deckchair(x, y, k), 0.322, 48, 50, name="chair")
    shown = s.word("display")[:6]           # the display holds six characters: 3,1415
    ck = min(k, 0.72)                    # a giant calculator, but not a monument in a panorama
    _, cw, ch = _calc_size(ck, shown)
    s.thing(lambda x, y, k: _dug_calculator(x, y, ck, shown), 0.49, cw * 2.3 * ck / k, ch * 1.2 * ck / k, name="calc")
    bird = s.cast("sparrow", 0.65, "cheer", "wink", flip=True)
    cater = s.cast("caterpillar", 0.8, "cheer", "surprise", flip=True)
    s.put(cater.bottom + 0.5, _rubber_ring(cater, True), None, group=cater.group)
    if not (s.h >= 300 and s.say(bird, f"{s.word('why1')} {s.word('why2')}", prefer="above")):
        s.say(bird, s.word("hihi"), prefer="right")
    s.thing(lambda x, y, k: _starfish(x, y, k * 1.2), 0.545, 22, 16, nearer=0.95, name="star")
    s.thing(lambda x, y, k: things.bucket(x, y, k * 0.6, P.YELLOW, "water"), 0.725, 22, 30, nearer=1.0,
            name="pail")
    s.thing(lambda x, y, k: _sandcastle(x, y, k * 0.8, P.BLUE), 0.96, 36, 50, name="castle2")
    s.thing(lambda x, y, k: _shell(x, y, k * 1.3, P.PINK, 20), 0.36, 16, 16, nearer=1.0, name="shell")
    _sea_thing(s, lambda x, y: _sail(x, y, k * 0.5), top, 40 * k * 0.5, 50 * k * 0.5, "sail")
    _gulls(s)


# ============================================================================ 6. barter
def _palm(x: float, y: float, k: float = 1.0, lean: float = 1) -> str:
    """A palm tree leaning to one side (lean = 1 right, -1 left); 90 wide, 150 tall."""
    c = Canvas()
    L = lean
    tx, ty = 26 * L, -140
    for i in range(9):
        t0, t1 = i / 9, (i + 1) / 9
        x0, y0 = tx * t0 * t0, ty * t0
        x1, y1 = tx * t1 * t1, ty * t1
        w0, w1 = 9 - i * 0.5, 9 - (i + 1) * 0.5
        c.shape(f"M{n(x0 - w0)},{n(y0)} L{n(x1 - w1)},{n(y1)} L{n(x1 + w1)},{n(y1)} L{n(x0 + w0)},{n(y0)} Z",
                P.TRUNK, sw=1.4, light=None)
    for ang, length in ((-160, 46), (-120, 40), (-60, 40), (-20, 46), (20, 38), (160, 38)):
        a = math.radians(ang)
        ex, ey = tx + math.cos(a) * length, ty + math.sin(a) * length * 0.7 + 12
        mx, my = tx + math.cos(a) * length * 0.5, ty + math.sin(a) * length * 0.5 - 10
        c.shape(f"M{n(tx)},{n(ty)} Q{n(mx)},{n(my - 8)} {n(ex)},{n(ey)} Q{n(mx)},{n(my + 4)} {n(tx)},{n(ty)} Z",
                P.LEAF, sw=1.6, light=None)
        c.line(f"M{n(tx)},{n(ty)} Q{n(mx)},{n(my - 2)} {n(ex)},{n(ey)}", 1, P.LEAF_DARK)
    for cx, cy in ((-5, 4), (4, 6), (0, 10)):
        c.shape(ellipse_d(tx + cx, ty + cy, 5, 5), P.WOOD_DARK, sw=1.2, light=None)
    return _at(c, x, y, k)


def _shell_basket(x: float, y: float, k: float = 1.0) -> str:
    """A little wicker basket heaped with shells, hanging by its handle from a hand at the origin."""
    c = Canvas()
    c.line("M-11,13 Q0,-8 11,13", 2.4, P.WOOD_DARK)
    for i, (sx, turn) in enumerate(((-7, -20), (0, 0), (7, 18), (-3, -6), (4, 10))):
        c.add(_shell(sx, 12 - (2 if i > 2 else 0), 0.75, (P.PINK_PALE, P.CREAM, P.PINK)[i % 3], turn))
    c.shape("M-14,11 H14 L11,26 Q0,29 -11,26 Z", P.WOOD_LIGHT, sw=1.6, light=(-1, -1))
    c.line("M-13,16 H13 M-12,21 H12", 1, P.WOOD_DARK, 0.8)
    return _at(c, x, y, k)


def _shell_string(s: Strip, box: Box, flip: bool) -> None:
    """A string of scallops held up in the cat's outstretched paw (pose `present`): the cord's top is gripped in
    the palm, so it is drawn behind the cat and comes out under the paw; it drops straight down, clear of the arm
    and the body, with the shells threaded on it hinge up, evenly spaced, and a knot at the end."""
    mod = module(box.name)
    elbow, wrist = mod.POSES["present"][2][0], mod.POSES["present"][2][1]
    turn = math.atan2(wrist[1] - elbow[1], wrist[0] - elbow[0])
    width = getattr(mod, "ARM_WIDTH", 15)
    ox, oy = wrist[0] + math.cos(turn) * width * 0.42, wrist[1] + math.sin(turn) * width * 0.42
    palm = turn + math.radians(mod.POSES["present"][2][3])
    px, py = ox + math.cos(palm) * 8.8, oy + math.sin(palm) * 8.8          # the middle of the palm, canvas units
    top_x, top_y, k = _on(box, flip, px + 5, py)
    _, low_y, _ = _on(box, flip, px + 5, py + 112)
    c = Canvas()
    c.line(f"M{n(top_x)},{n(top_y)} V{n(low_y)}", 1.5 * k * 3, P.WOOD_DARK)
    c.add(f'<circle cx="{n(top_x)}" cy="{n(low_y + 1.6 * k * 3)}" r="{n(1.6 * k * 3)}" fill="{P.WOOD_DARK}" '
          f'stroke="{INK}" stroke-width="{n(0.6 * k * 3)}"/>')
    colors = (P.PINK_PALE, P.CREAM, P.PINK, lighten(P.ORANGE, 0.55))
    sk = 2.2 * k
    for i in range(4):
        y = top_y + (17 + i * 25) * k
        c.add(_shell(top_x, y, sk, colors[i], 180))
    box_ = (top_x - 7.5 * sk, top_y + 14 * k, top_x + 7.5 * sk, low_y + 3.2 * k * 3)
    s.put(box.bottom - 0.5, c.render(), box_, "shell_string", group=box.group)


def _pile_tag_size(k: float) -> float:
    """The lettering of the price tags on the shell piles, never under the page's smallest."""
    return _lettering(k, 10)


def _shell_piles(x: float, y: float, k: float = 1.0, label: str = "") -> str:
    """Three neat pyramids of ten scallop shells each (4, 3, 2, 1) on the sand, each with a soft shadow and a
    price tag on a stick pushed into its top; 134 wide, the tags reach about 44 + their lettering up."""
    c = Canvas()
    colors = (P.PINK_PALE, P.CREAM, P.PINK, lighten(P.ORANGE, 0.55))
    size = _pile_tag_size(k)
    tw, th = sets.letter_width(label, size) + 13, size + 9
    sk, dx, dy = 0.86, 9.8, 6.0                 # shell scale, spacing in a row, rise per row
    for p, px in enumerate((-44, 0, 44)):
        c.add(f'<ellipse cx="{n(px + 2)}" cy="1.2" rx="23" ry="3.4" fill="{darken(P.SAND, 0.72)}" opacity=".45"/>')
        if label:                                # the stick goes in behind the top shells, so draw it first
            lean = (-5, 4, -3)[p]
            top = -40
            c.add(f'<g transform="rotate({lean} {px} -12)">')
            c.line(f"M{px},-12 V{top + 2}", 2.2, P.WOOD_DARK)
            c.line(f"M{px - 0.4},-13 V{top + 3}", 0.8, lighten(P.WOOD, 0.3))
            tag = (f"M{n(px - tw / 2 + 5)},{n(top - th)} H{n(px + tw / 2)} V{n(top)} H{n(px - tw / 2 + 5)} "
                   f"L{n(px - tw / 2)},{n(top - th / 2)} Z")
            c.shape(tag, P.CARD, sw=1.4, light=(-1, -1), shade_k=0.9)
            c.add(f'<circle cx="{n(px - tw / 2 + 4)}" cy="{n(top - th / 2)}" r="1.4" fill="{P.WHITE}" '
                  f'stroke="{INK}" stroke-width=".9"/>')
            c.add(f'<circle cx="{px}" cy="{n(top - 1.5)}" r="1.1" fill="{INK}"/>')     # the tack
            sets.fit_label(c, px + 2.5, top - th / 2 + size * 0.36, label, size, tw - 12, P.RED,
                           style=_letter_face(k, size))
            c.add("</g>")
        i = 0
        for row, count in reversed(list(enumerate((4, 3, 2, 1)))):   # the top first, the bottom row in front
            for j in range(count):
                sx = px + (j - (count - 1) / 2) * dx
                c.add(_shell(sx, -row * dy, sk, colors[(i + p + row) % 4], (j - (count - 1) / 2) * 6))
                i += 1
    return _at(c, x, y, k)


def _piles_height(k: float) -> float:
    return 46 + _pile_tag_size(k) + 9


@episode("barter")
def barter(s: Strip) -> None:
    """A bidding war on a tropical shore: the caterpillar holds out a whole basket of shells, the cat a string of
    them, both for the sparrow's red balloon, and the sparrow cannot choose. The agent counts the takings so far
    into neat piles of ten. A sail far out at sea, gulls overhead, a starfish on the sand."""
    top = _shore(s)
    k = s.unit
    s.thing(lambda x, y, k: _palm(x - 19 * k, y, k * 0.85, 1), 0.04, 82, 130, name="palm1")
    cater = s.cast("caterpillar", 0.18, "present", "smile", flip=False, group="deal")
    s.in_hand(cater, "present", False, lambda x, y, kk: _shell_basket(x, y, kk * 0.9))
    bird = s.cast("sparrow", 0.33, "wave", "surprise", flip=False, mark="?", group="deal")
    gx, gy, _ = _on(bird, False, 174, 59)
    length = 46 * k
    bk = k * 0.7
    btop = gy - length - 46 * bk
    if btop > 4:
        bal = f'<g transform="translate({n(gx)},{n(gy)}) scale({n(bk)})">{props.balloon(0, 0, length / bk, P.RED)}</g>'
        s.put(bird.bottom + 1, bal, (gx - 18 * bk, btop, gx + 18 * bk, gy - length + 2), group="deal")
    cat = s.cast("cat", 0.48, "present", "talk", flip=True, group="deal", tail=False)  # no tail across the string
    _shell_string(s, cat, True)
    agent = s.cast("agent", 0.6, "type", "smile", flip=False, mark="ok")
    s.held(agent, "type", False, lambda x, y, kk: _shell(x, y, kk * 0.9, P.PINK))
    pk = min(k, 0.95)                    # shells stay shell-sized in a panorama
    s.thing(lambda x, y, k: _shell_piles(x, y, pk, s.word("ten")), 0.752, 134 * pk / k, _piles_height(pk) * pk / k,
            nearer=0.6, name="piles")
    s.thing(lambda x, y, k: _palm(x + 22 * k, y, k, -1), 0.935, 100, 150, name="palm2")
    s.thing(lambda x, y, k: _starfish(x, y, k), 0.26, 18, 14, nearer=1.0, name="star")
    s.thing(lambda x, y, k: _shell(x, y, k * 1.2, P.PINK_PALE, 15), 0.5, 16, 14, nearer=0.9, name="shell")
    _sea_thing(s, lambda x, y: _sail(x, y, k * 0.5), top, 40 * k * 0.5, 50 * k * 0.5, "sail")
    _gulls(s, 2)


def _sail(x: float, y: float, k: float = 1.0) -> str:
    """A little sailing boat far away; 40 wide, 50 tall, the origin at the water."""
    c = Canvas()
    c.shape("M-18,-6 H18 L12,0 H-12 Z", P.WOOD, sw=1.4, light=None)
    c.line("M0,-6 V-46", 1.4)
    c.shape("M2,-44 L18,-10 H2 Z", P.WHITE, sw=1.3, light=None)
    c.shape("M-2,-40 L-14,-10 H-2 Z", P.RED, sw=1.3, light=None)
    return _at(c, x, y, k)


# ============================================================================ 7. many_trades
def _dress(box: Box, flip: bool, c: Canvas) -> str:
    """Something drawn in a character's own canvas units (a hat, a bow tie, a drum) placed on the page with it."""
    mod = module(box.name)
    kk = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
    mid = (box.left + box.right) / 2
    y0 = box.bottom - mod.FEET_Y * kk
    if flip:
        return f'<g transform="translate({n(mid + mod.CENTER_X * kk)},{n(y0)}) scale({n(-kk)},{n(kk)})">' \
               f'{c.render()}</g>'
    return f'<g transform="translate({n(mid - mod.CENTER_X * kk)},{n(y0)}) scale({n(kk)})">{c.render()}</g>'


def _hat(kind: str) -> Canvas:
    """A hat for the agent, in its canvas units (the crown of its head is at 110, 36)."""
    c = Canvas()
    if kind == "beret":
        c.shape("M60,44 Q58,20 108,18 Q160,18 158,40 Q130,30 60,44 Z", P.TROUSERS, sw=3, light=(-3, -3))
        c.line("M108,18 l4,-10", 4)
    elif kind == "chef":
        c.shape("M78,44 V26 Q56,22 62,0 Q70,-20 90,-12 Q100,-34 122,-22 Q148,-28 152,-4 Q164,18 140,26 V44 Z",
                P.WHITE, sw=3, light=(-3, -3), shade_k=0.9)
        c.line("M80,30 H138", 2, opacity=0.4)
    elif kind == "nurse":
        c.shape("M70,40 L76,14 Q110,4 144,14 L150,40 Q110,32 70,40 Z", P.WHITE, sw=3, light=None)
        # the red cross keeps clear of the cap's rim
        c.path("M106.500,15 h7 v4.500 h4.500 v7 h-4.500 v4.500 h-7 v-4.500 h-4.500 v-7 h4.500 Z", P.RED, 1.6)
    elif kind == "straw":
        c.shape(ellipse_d(110, 38, 74, 12), P.WOOD_PALE, sw=3, light=None)
        c.shape("M76,38 Q76,4 110,4 Q144,4 144,38 Z", P.WOOD_PALE, sw=3, light=(-3, -3), shade_k=0.85)
        c.line("M77,30 Q110,22 143,30", 6, P.RED)
        c.line("M96,10 l-6,22 M112,6 v26 M128,10 l6,22", 1.4, P.WOOD_DARK, 0.5)
    elif kind == "band":
        c.shape("M74,40 Q74,16 110,14 Q146,16 146,40 Z", P.RED, sw=3, light=(-3, -3))
        c.line("M110,14 V-6", 3, P.METAL_DARK)
        c.shape(ellipse_d(110, -8, 30, 6), P.SUN, sw=2.4, light=None)
        c.dot(110, -10, 3)
        for bx in (78, 142):
            c.add(f'<circle cx="{bx}" cy="44" r="6" fill="{P.SUN}" stroke="{INK}" stroke-width="2"/>')
    return c


def _drawing_board(x: float, y: float, k: float = 1.0) -> str:
    """An easel with a blueprint pinned to it; 44 wide, 92 tall."""
    c = Canvas()
    c.line("M-18,0 L-4,-90 M18,0 L4,-90 M0,-30 L10,0", 3, P.WOOD_DARK)
    c.shape("M-22,-86 H22 V-36 H-22 Z", P.BLUE, sw=2, light=None)
    c.line("M-16,-78 H12 V-50 H-6 V-64 H-16 Z M-2,-72 h8 M2,-44 h14", 1.4, P.WHITE, 0.9)
    c.add(f'<circle cx="10" cy="-58" r="6" fill="none" stroke="{P.WHITE}" stroke-width="1.2" opacity=".9"/>')
    c.line("M-22,-34 H22", 3, P.WOOD_DARK)
    return _at(c, x, y, k)


def _teddy(x: float, y: float, k: float = 1.0) -> str:
    """A teddy bear sitting on the ground with a bandage round its head; 30 wide, 34 tall."""
    c = Canvas()
    fur = P.AMBER
    for dx in (-9, 9):
        c.shape(ellipse_d(dx, -4, 6, 5), fur, sw=1.4, light=None)
    c.shape(ellipse_d(0, -12, 11, 11), fur, sw=1.6, light=(-1, -1))
    c.shape(ellipse_d(0, -12, 6, 7), P.CREAM, sw=0, light=None)
    for dx in (-12, 12):
        c.shape(ellipse_d(dx, -14, 4, 6), fur, sw=1.3, light=None)
    for dx in (-8, 8):
        c.shape(ellipse_d(dx, -33, 4.5, 4.5), fur, sw=1.3, light=None)
    c.shape(ellipse_d(0, -27, 10, 9), fur, sw=1.6, light=(-1, -1))
    c.path("M-10,-31 Q0,-36 10,-31 L10,-27 Q0,-32 -10,-27 Z", P.WHITE, 1.2)
    c.path("M-2,-35 h4 v3 h-4 Z", P.RED, 0.8)
    c.dot(-3.5, -26, 1.1)
    c.dot(3.5, -26, 1.1)
    c.shape(ellipse_d(0, -22.5, 3, 2), P.CREAM, sw=1, light=None)
    c.dot(0, -23, 0.9)
    return _at(c, x, y, k)


def _spray(x: float, y: float, k: float = 1.0, mirror: bool = False) -> str:
    """A spray bottle with a puff of mist; the origin is the hand."""
    c = Canvas()
    c.shape("M-5,0 V-14 H5 V0 Q5,6 0,6 Q-5,6 -5,0 Z", P.TEAL, sw=1.3, light=None)
    c.shape("M-3,-14 V-20 H8 L10,-16 H4 V-14 Z", P.WHITE, sw=1.2, light=None)
    for i, (dx, dy) in enumerate(((14, -18), (18, -15), (17, -21), (22, -18), (21, -24), (25, -14))):
        c.add(f'<circle cx="{dx}" cy="{dy}" r="{1 + (i % 2) * 0.5}" fill="{P.WATER}" stroke="{INK}" '
              f'stroke-width=".4"/>')
    return _at(c, x, y, k, mirror)


def _tsquare(x: float, y: float, k: float = 1.0, mirror: bool = False) -> str:
    """A T-square held by its head; the origin is the hand, the blade reaching forward."""
    c = Canvas()
    c.shape("M-3,-12 H3 V8 H-3 Z", P.WOOD_DARK, sw=1.2, light=None)
    c.shape("M3,-4 H46 V0 H3 Z", P.WOOD_PALE, sw=1.2, light=None)
    for i in range(8):
        c.line(f"M{8 + i * 5},-4 v1.6", 0.6)
    return _at(c, x, y, k, mirror)


def _watering_can(x: float, y: float, k: float = 1.0) -> str:
    """A green watering can; the origin is between the hands, the rose at (28, -19)."""
    c = Canvas()
    c.shape("M-12,-2 V-18 H10 V-2 Z", P.GREEN, sw=1.4, light=(-1, -1))
    c.line("M-10,-18 Q0,-28 8,-18", 1.6)
    c.shape("M10,-8 L26,-20 L28,-17 L12,-4 Z", P.GREEN, sw=1.2, light=None)
    c.shape(ellipse_d(28, -19, 3, 4), P.GREEN, sw=1.1, light=None)
    return _at(c, x, y, k)


def _carrot_bed(x: float, y: float, k: float = 1.0) -> str:
    """A little bed of dark soil with carrot tops in a row, one carrot pulled up and lying beside; 44 wide."""
    c = Canvas()
    c.shape("M-22,0 Q-20,-8 0,-8 Q20,-8 22,0 Z", P.WOOD_DARK, sw=1.6, light=None)
    for cx in (-13, -3, 7):
        c.path(f"M{cx - 3},-6 L{cx},-1 L{cx + 3},-6 Z", P.ORANGE, 1)
        c.line(f"M{cx},-7 l-4,-10 M{cx},-7 l0,-12 M{cx},-7 l4,-10", 2, P.LEAF)
    c.add('<g transform="translate(18,-3) rotate(-70)">')
    c.shape("M-3,-14 Q0,4 3,-14 Z", P.ORANGE, sw=1.1, light=None)
    c.line("M0,-14 l-3,-6 M0,-14 l3,-6", 1.6, P.LEAF)
    c.add("</g>")
    return _at(c, x, y, k)


def _drum(box: Box, flip: bool) -> str:
    """A bass drum strapped to the agent's front, two cymbals on it, drumsticks in the raised hands."""
    c = Canvas()
    c.line("M82,136 L110,170 L138,136", 4, P.LEATHER)
    c.shape(ellipse_d(110, 186, 44, 30), P.RED, sw=3, light=(-3, -3))
    c.shape(ellipse_d(110, 186, 34, 22), P.CREAM, sw=2, light=None)
    c.line("M76,170 L144,202 M76,202 L144,170", 2, P.SUN)
    c.line("M38,114 L60,92 M182,114 L162,90", 4, P.WOOD_DARK)
    c.add(f'<circle cx="60" cy="92" r="5" fill="{P.WOOD_PALE}" stroke="{INK}" stroke-width="2"/>'
          f'<circle cx="162" cy="90" r="5" fill="{P.WOOD_PALE}" stroke="{INK}" stroke-width="2"/>')
    return _dress(box, flip, c)


@episode("many_trades")
def many_trades(s: Strip) -> None:
    """The professor presents a row of agents, each in its own hat for its own trade: a
    draughtsman with a T-square at the easel, a cook with a steaming pot, a nurse spraying a bandaged teddy, a
    gardener watering carrots, and a one-man band with drum, cymbal and bells. Notes fly from the band, a
    butterfly visits the carrots."""
    s.outdoors()
    k = s.unit
    s.cast("professor", 0.05, "present", "talk", flip=False)
    size = 0.9
    a1 = s.cast("agent", 0.19, "point", "smile", flip=False, size=size, group="draw")
    s.put(a1.bottom + 0.6, _dress(a1, False, _hat("beret")), None, group="draw")
    hx, hy = s.hand(a1, "point", False)
    s.put(a1.bottom + 0.7, _tsquare(hx, hy, k * 0.9), None, group="draw")
    s.thing(lambda x, y, k: _drawing_board(x, y, k), 0.28, 46, 92, name="board", group="draw")
    a2 = s.cast("agent", 0.395, "type", "smile", flip=False, size=size, group="cook")
    s.put(a2.bottom + 0.6, _dress(a2, False, _hat("chef")), None, group="cook")
    s.held(a2, "type", False, lambda x, y, kk: things.pot(x, y + 6 * kk, kk * 0.75))
    a3 = s.cast("agent", 0.52, "point", "smile", flip=False, size=size, group="nurse")
    s.put(a3.bottom + 0.6, _dress(a3, False, _hat("nurse")), None, group="nurse")
    hx, hy = s.hand(a3, "point", False)
    s.put(a3.bottom + 0.7, _spray(hx, hy, k * 0.9), None, group="nurse")
    s.thing(lambda x, y, k: _teddy(x, y, k), 0.6, 30, 36, nearer=0.4, name="teddy")
    a4 = s.cast("agent", 0.695, "type", "smile", flip=False, size=size, group="garden")
    s.put(a4.bottom + 0.6, _dress(a4, False, _hat("straw")), None, group="garden")
    cx_, cy_ = s.held(a4, "type", False, lambda x, y, kk: _watering_can(x, y, kk * 1.0))
    kk = (a4.bottom - a4.top) / 100
    bx = cx_ + 64 * kk                          # the bed right under the can's rose, so the water falls on it
    by = s.feet(bx, 0.6)
    kb = k * 1.15
    s.put(by - 1, _carrot_bed(bx, by, kb), (bx - 23 * kb, by - 20 * kb, bx + 23 * kb, by), "carrots", group="garden")
    rx, ry = cx_ + 30 * kk, cy_ - 14 * kk
    rain = Canvas()
    for i, dx in enumerate((-6, 0, 6)):         # three thin streams from the rose down onto the carrot tops
        ex, ey = bx + dx * kb, by - 18 * kb
        rain.add(f'<path d="M{n(rx + i * 1.5 * kk)},{n(ry + i * kk)} Q{n(ex - 4 * kk)},{n(ry - 6 * kk)} '
                 f'{n(ex)},{n(ey)}" '
                 f'fill="none" stroke="{darken(P.WATER, 0.85)}" stroke-width="{n(2 * kk)}" stroke-linecap="round" '
                 f'stroke-dasharray="{n(3 * kk)} {n(3 * kk)}"/>')
    s.put(by - 0.5, rain.render(), None, group="garden")
    a5 = s.cast("agent", 0.91, "cheer", "wink", flip=True, size=size, group="band")
    s.put(a5.bottom + 0.6, _dress(a5, True, _hat("band")) + _drum(a5, True), None, group="band")
    sky = _sky(s)
    _flutter(s, [lambda x, y: _note(x, y, k, P.RED), lambda x, y: _note(x, y, k * 0.9, P.ORANGE, True)],
             (s.x(0.8), sky[1], s.hi, sky[3]), 20 * k, "note")
    _flutter(s, [lambda x, y: props.butterfly(x, y, k * 0.8, P.PINK)], (s.x(0.7), sky[1], s.x(0.85), sky[3]),
             18 * k, "bfly")


# ============================================================================ 8. conductor
def _cafe_table(x: float, y: float, k: float = 1.0, cloth: str = P.PINK_PALE) -> str:
    """A little round cafe table, its top 30 up; 36 wide."""
    c = Canvas()
    c.line("M0,-28 V-2", 3, P.METAL_DARK)
    c.shape(ellipse_d(0, -1, 10, 2.5), P.METAL_DARK, sw=1.4, light=None)
    c.shape(ellipse_d(0, -30, 18, 4), cloth, sw=1.6, light=None)
    c.shape("M-18,-30 Q-18,-24 -14,-22 H14 Q18,-24 18,-30 Z", cloth, sw=1.4, light=None)
    return _at(c, x, y, k)


def _face(c: Canvas, x: float, y: float, r: float = 6) -> None:
    """Two eyes, a smile and rosy cheeks on whatever it is drawn over."""
    c.dot(x - r * 0.7, y - r * 0.3, r * 0.2)
    c.dot(x + r * 0.7, y - r * 0.3, r * 0.2)
    c.line(f"M{n(x - r * 0.5)},{n(y + r * 0.25)} Q{n(x)},{n(y + r * 0.8)} {n(x + r * 0.5)},{n(y + r * 0.25)}",
           r * 0.18)
    for dx in (-1.1, 1.1):
        c.add(f'<ellipse cx="{n(x + dx * r)}" cy="{n(y + r * 0.2)}" rx="{n(r * 0.3)}" ry="{n(r * 0.18)}" '
              f'fill="{P.PINK}" opacity=".7"/>')


def _player(x: float, y: float, k: float = 1.0, device: str = "printer") -> str:
    """A smiling device sitting on a cafe table and playing along; 40 wide, 72 tall."""
    c = Canvas()
    c.add(_cafe_table(0, 0, 1, (P.PINK_PALE, P.YELLOW_PALE, lighten(P.TEAL, 0.6))[
        ("printer", "terminal", "drive").index(device)]))
    c.add(doodle_at(device, 0, -29, 38))
    if device == "printer":
        _face(c, 0, -46, 5)
        c.shape("M14,-50 L30,-56 L32,-44 L16,-46 Z", P.SUN, sw=1.2, light=None)        # a trumpet
        c.shape(ellipse_d(31, -50, 3, 7), P.SUN, sw=1.2, light=None)
    elif device == "terminal":
        _face(c, 0, -47, 6)
        c.shape(ellipse_d(-18, -32, 7, 4), P.RED, sw=1.2, light=None)                  # a little drum
        c.line("M-25,-32 V-26 M-11,-32 V-26 M-25,-26 Q-18,-23 -11,-26", 1.2)
        c.line("M-12,-46 L-18,-36", 1.4, P.WOOD_DARK)
    else:
        _face(c, 0, -40, 5)
        c.path("M14,-62 L24,-44 H4 Z", "none", 1.6, P.METAL_DARK)                      # a triangle
        c.line("M14,-62 V-66", 1)
    return _at(c, x, y, k)


def _stage(x: float, y: float, k: float = 1.0) -> str:
    """A low plank stage with a music stand; 96 wide, the boards 14 up."""
    c = Canvas()
    c.shape("M-48,0 V-14 H48 V0 Z", P.WOOD, sw=2, light=(-2, -1))
    for bx in (-24, 0, 24):
        c.line(f"M{bx},-14 V0", 1, P.WOOD_DARK)
    c.shape(rounded_rect_d(-52, -18, 104, 5, 2), P.WOOD_LIGHT, sw=1.6, light=None)
    c.line("M-34,-18 V-58 M-40,-18 L-34,-26 L-28,-18", 2, P.CHARCOAL)
    c.shape("M-48,-72 L-20,-74 L-22,-56 L-46,-54 Z", P.CARD, sw=1.4, light=None)
    for i in range(3):
        c.line(f"M-44,{-68 + i * 5} L-24,{-70 + i * 5}", 0.6)
    c.add(f'<ellipse cx="-38" cy="-67" rx="1.4" ry="1" fill="{INK}"/><ellipse cx="-30" cy="-63" rx="1.4" ry="1" '
          f'fill="{INK}"/>')
    return _at(c, x, y, k)


def _tailcoat(box: Box, flip: bool) -> tuple[str, str]:
    """The conductor's tails (behind) and bow tie with a white baton (in front), in the agent's wave pose."""
    back = Canvas()
    back.shape("M84,190 Q70,220 62,252 L98,206 Z M136,190 Q150,220 158,252 L122,206 Z", P.CHARCOAL, sw=2.4,
               light=None)
    front = Canvas()
    front.shape("M96,124 L108,130 L96,136 Z M124,124 L112,130 L124,136 Z", P.CHARCOAL, sw=2, light=None)
    front.add(f'<circle cx="110" cy="130" r="4" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="2"/>')
    front.tube("M184,112 L208,64", P.WHITE, 3.6, sw=1.3, shaded=False)               # the baton
    front.tube("M183,114 L188,104", P.WOOD_LIGHT, 6.5, sw=1.3, shaded=False)           # its cork grip
    return _dress(box, flip, back), _dress(box, flip, front)


def _puddle_boat(x: float, y: float, k: float = 1.0) -> str:
    """A puddle with a toy paper boat on it; 70 wide, 26 tall."""
    c = Canvas()
    c.shape(ellipse_d(0, -6, 35, 8), P.WATER, sw=1.6, light=None)
    c.line("M-24,-6 q4,-2 8,0 M14,-3 q4,-2 8,0", 1, P.WHITE)
    c.shape("M-12,-10 H10 L6,-4 H-8 Z", P.RED, sw=1.3, light=None)
    c.shape("M-2,-10 V-26 L8,-12 Z", P.WHITE, sw=1.2, light=None)
    c.add(sets.lily(24, -8, 0.5, frog=True))
    c.add(_note(30, -26, 0.6, P.LEAF_DARK))
    return _at(c, x, y, k)


@episode("conductor")
def conductor(s: Strip) -> None:
    """At a picnic concert the agent, in a tailcoat, conducts from its score on a little
    stage; a printer with a trumpet, a terminal with a drum and a disk drive with a triangle sit at cafe tables
    and play, all smiling. The sparrow, meanwhile, conducts a toy boat on a puddle by its string, and a frog sings
    along."""
    s.outdoors()
    k = s.unit
    s.thing(lambda x, y, k: _player(x, y, k * 1.15, "printer"), 0.05, 58, 84, name="printer")
    s.thing(lambda x, y, k: _player(x, y, k * 1.15, "terminal"), 0.18, 56, 84, name="terminal")
    sx, sy = s.thing(lambda x, y, k: _stage(x, y, k), 0.36, 104, 74, name="stage")
    agent = s.actor("agent", sx + 12 * k, sy - 18 * k, "wave", "smile", flip=False, tall=s.tall, group="stage",
                    depth=sy + 1)
    back, front = _tailcoat(agent, False)
    s.put(sy + 0.5, back, None, group="stage")
    s.put(sy + 1.5, front, (agent.right - 4, agent.top - 8 * k, agent.right + 30 * k, agent.top + 46 * k),
          group="stage")
    s.thing(lambda x, y, k: _player(x, y, k * 1.15, "drive"), 0.54, 58, 84, name="drive")
    bird = s.cast("sparrow", 0.68, "point", "smile", flip=False)
    wx, wy = s.hand(bird, "point", False)
    px, py = s.thing(lambda x, y, k: _puddle_boat(x, y, k), 0.81, 72, 40, nearer=0.85, name="puddle")
    bx, by = px - 12 * k, py - 9 * k          # the toy boat's bow, where the string is tied
    s.put(py - 1, f'<path d="M{n(wx)},{n(wy)} Q{n((wx + bx) / 2)},{n(max(wy, by) + 6 * k)} {n(bx)},{n(by)}" '
          f'fill="none" stroke="{INK}" stroke-width="{n(1.2 * k)}" stroke-linecap="round"/>', None)
    low = _festoon(s, 4)
    sky = _sky(s)
    _flutter(s, [lambda x, y: _note(x, y, k, P.ORANGE), lambda x, y: _note(x, y, k, P.RED, True),
                 lambda x, y: _note(x, y, k * 0.9, P.BLUE), lambda x, y: _note(x, y, k, P.GREEN, True)],
             (s.lo, max(sky[1], low + 8, s.h * 0.2), s.x(0.62), sky[3]), 22 * k, "note")


# ============================================================================ 9. playing_computer
def _tent_size(text: str, k: float) -> tuple[float, float, float]:
    """(font size, width, height) of a folded name card at scale `k`, its word never smaller than the page allows."""
    size = _lettering(k, 8.4)
    return size, max(30.0, sets.letter_width(text, size) + size * 1.6 + 6), size + 8


def _tent_card(x: float, y: float, k: float = 1.0, text: str = "") -> str:
    """A folded name card standing on the floor, as on a conference table, sized to its word."""
    c = Canvas()
    size, w, h = _tent_size(text, k)
    c.shape(f"M{-w / 2},0 L{-w / 2 + 3},{-h} H{w / 2 - 3} L{w / 2},0 Z", P.CARD, sw=1.5, light=(-1, -1),
            shade_k=0.9)
    c.line(f"M{-w / 2 + 3},{-h} H{w / 2 - 3}", 2.4, P.RED)
    sets.fit_label(c, 0, -h / 2 + size * 0.36 + 1, text, size, w - 6 - size * 1.2, style=_letter_face(k, size))
    return _at(c, x, y, k)


def _num_card(x: float, y: float, k: float = 1.0, text: str = "", turn: float = 0) -> str:
    """A big card with a number on it, held up by its lower edge: the origin is the hand."""
    c = Canvas()
    c.shape(rounded_rect_d(-12, -30, 24, 28, 2), P.YELLOW_PALE, sw=1.6, light=None)
    size = _lettering(k, 19)
    sets.fit_label(c, 0, -16 + size * 0.36, text, size, 20, P.RED, style=_letter_face(k, size))
    return _at(c, x, y, k, turn=turn)


def _screen_frame(box: Box, text: str, short: str) -> str:
    """An empty gilt frame the caterpillar holds up in both raised hands, in front of her: the display. It shows
    the whole sum when it can be read at this size, else only the answer."""
    kk = (box.bottom - box.top) / (module(box.name).FEET_Y - module(box.name).HEAD_TOP)
    c = Canvas()
    c.add(f'<rect x="38" y="112" width="130" height="92" fill="{P.WHITE}" fill-opacity=".85"/>')
    c.path("M38,112 H168 V204 H38 Z", "none", 16, P.AMBER)
    c.path("M30,104 H176 V212 H30 Z", "none", 2.6)
    c.path("M46,120 H160 V196 H46 Z", "none", 2.6)
    c.line("M30,104 L46,120 M176,104 L160,120 M30,212 L46,196 M176,212 L160,196", 2)
    need = sets.LETTERING_MIN / kk
    if sets.letter_width(text, max(26, need), style="plain") <= 90:   # an even margin inside the 114-wide glass
        size, word = max(26.0, need), text
    else:
        size, word = min(56.0, max(30.0, need)), short
    if size >= need:
        _label(c, 103, 158 + size * 0.36, word, size, P.PEN, style="plain")
    return _dress(box, False, c)


def _typewriter(x: float, y: float, k: float = 1.0, text: str = "") -> str:
    """A typewriter with a sheet curling out of it; 56 wide, its top 22 up (the sheet goes higher)."""
    c = Canvas()
    size = _lettering(k, 11)
    sw, sh = max(20.0, sets.letter_width(text, size) + 8), max(22.0, size + 9)
    c.shape(f"M{19 - sw / 2},-20 L{19 - sw / 2 + 2},{-20 - sh} H{19 + sw / 2 - 2} L{19 + sw / 2},-20 Z", P.WHITE,
            sw=1.4, light=None)
    _label(c, 19, -20 - sh / 2 + size * 0.36, text, size, P.PEN, style=_letter_face(k, size))
    c.shape(rounded_rect_d(-26, -24, 52, 6, 3), P.CHARCOAL, sw=1.6, light=None)
    c.shape(ellipse_d(-28, -21, 4, 4), P.METAL, sw=1.2, light=None)
    c.shape("M-24,0 L-20,-18 H20 L24,0 Z", P.RED, sw=1.8, light=(-1.5, -1))
    for row in range(2):
        for col in range(6):
            c.add(f'<circle cx="{-14 + col * 5.6 + row * 2}" cy="{-10 + row * 5}" r="1.8" fill="{P.CREAM}" '
                  f'stroke="{INK}" stroke-width=".7"/>')
    return _at(c, x, y, k)


def _boombox(x: float, y: float, k: float = 1.0) -> str:
    """A boombox with two speakers and a cassette, playing; 60 wide, 40 tall."""
    c = Canvas()
    c.line("M-18,-32 Q0,-44 18,-32", 3, P.CHARCOAL)
    c.shape(rounded_rect_d(-30, -32, 60, 32, 5), P.METAL_DARK, sw=2, light=(-2, -2))
    for sx in (-17, 17):
        c.shape(ellipse_d(sx, -14, 10, 10), P.CHARCOAL, sw=1.6, light=None)
        c.shape(ellipse_d(sx, -14, 4, 4), P.METAL, sw=1, light=None)
    c.shape("M-7,-24 H7 V-10 H-7 Z", P.CREAM, sw=1.2, light=None)
    c.add(f'<circle cx="-3" cy="-17" r="2" fill="none" stroke="{INK}" stroke-width=".9"/>'
          f'<circle cx="3" cy="-17" r="2" fill="none" stroke="{INK}" stroke-width=".9"/>')
    for i, color in enumerate((P.RED, P.SUN, P.GREEN)):
        c.add(f'<rect x="{-26 + i * 6}" y="-31" width="4" height="3" fill="{color}" stroke="{INK}" '
              f'stroke-width=".6"/>')
    c.add(_note(-20, -50, 0.8))
    c.add(_note(22, -56, 0.8, P.RED, True))
    return _at(c, x, y, k)


@episode("playing_computer")
def playing_computer(s: Strip) -> None:
    """Playing at being a computer, as in the original: the professor is the input and holds up the numbers on
    cards, one in each hand; the cat is the processor and works it out in his book; the caterpillar holds up an
    empty frame - the display - showing the sum; the sparrow stands on a typewriter, being the printer; a boombox
    plays the program. A name card on the floor says who is what."""
    s.indoors()
    k = s.unit
    w = s.word
    prof = s.cast("professor", 0.07, "welcome", "talk", flip=False)
    s.in_hand(prof, "welcome", False, lambda x, y, kk: _num_card(x, y, kk * 0.9, w("three"), 6))
    s.in_hand(prof, "welcome", False, lambda x, y, kk: _num_card(x, y, kk * 0.9, w("two"), -6), side="left")
    s.cast("cat", 0.27, "read", "talk", flip=False)
    cater = s.cast("caterpillar", 0.47, "cheer", "smile", flip=False)
    s.put(cater.bottom + 1, _screen_frame(cater, w("sum"), w("five")), None, group=cater.group)
    tx, ty = s.thing(lambda x, y, k: _typewriter(x, y, k, w("five")), 0.66, 64, 44, name="printer")
    s.actor("sparrow", tx - 9 * k, ty - 20 * k, "cheer", "smile", flip=True, tall=s.tall * 0.85, group="printer",
            depth=ty + 1)
    s.thing(lambda x, y, k: _boombox(x, y, k), 0.86, 62, 62, name="boombox")
    for frac, key in ((0.07, "input"), (0.27, "cpu"), (0.47, "display"), (0.66, "printer"), (0.86, "program")):
        _, cw, ch = _tent_size(w(key), k)
        s.thing(lambda x, y, k, key=key: _tent_card(x, y, k, w(key)), frac, cw + 4, ch + 2, nearer=1.0,
                name=f"card-{key}")
    if s.h >= 200:
        top = min(b.top for b in s.boxes)
        bw, bh = 150 * k, min(70 * k, top - 24 - s.h * 0.2)
        if bh > 40:
            _air(s, lambda x, y: sets.whiteboard(x, y - bh / 2, bw, bh, w("board")), s.x(0.62),
                 top - 12 - bh / 2, bw, bh, "board")


# ============================================================================ 10. postman
def _door(x: float, y: float, k: float = 1.0, number: str = "", open_: bool = False) -> str:
    """An office door in the corridor wall, its number on a plaque screwed to the lintel; 48 wide, the door 98 tall, the
    plaque's figure never smaller than the page allows."""
    c = Canvas()
    c.shape("M-24,0 V-98 H24 V0 Z", P.WOOD_PALE, sw=1.8, light=None)
    if open_:
        c.shape("M-20,0 V-94 H20 V0 Z", darken(P.WALL, 0.7), sw=1.4, light=None)
        c.shape("M-20,0 V-94 L-6,-88 V4 Z", P.WOOD, sw=1.6, light=None)
        c.add(f'<circle cx="-9" cy="-46" r="2.2" fill="{P.SUN}" stroke="{INK}" stroke-width="1"/>')
    else:
        c.shape("M-20,0 V-94 H20 V0 Z", P.WOOD, sw=1.6, light=(-1.5, -1))
        c.path("M-14,-86 H14 V-56 H-14 Z", "none", 1.2, P.WOOD_DARK)
        c.path("M-14,-46 H14 V-10 H-14 Z", "none", 1.2, P.WOOD_DARK)
        c.add(f'<circle cx="14" cy="-48" r="2.6" fill="{P.SUN}" stroke="{INK}" stroke-width="1"/>')
    size = _lettering(k, 9)
    w, h = sets.letter_width(number, size) + 9, size + 5
    w = max(w, h + 8)                           # a plaque screwed to the lintel, its foot on the frame
    c.shape(rounded_rect_d(-w / 2, -96 - h, w, h, 2), P.CARD, sw=1.3, light=(-1, -1), shade_k=0.9)
    for sx in (-w / 2 + 2.8, w / 2 - 2.8):
        c.add(f'<circle cx="{n(sx)}" cy="{n(-96 - h / 2)}" r="1" fill="{P.METAL_DARK}"/>')
    _label(c, 0, -96 - h / 2 + size * 0.36, number, size, style=_letter_face(k, size))
    return _at(c, x, y, k)


def _door_height(k: float) -> float:
    """How tall a door is with its plaque, at scale `k` (in its own units)."""
    return 96 + _lettering(k, 9) + 5


def _letter_card(x: float, y: float, k: float = 1.0, turn: float = 0, color: str = P.CARD) -> str:
    """A letter lying on the floor; 22 wide."""
    c = Canvas()
    c.shape("M-11,0 V-12 H11 V0 Z", color, sw=1.3, light=None)
    c.line("M-11,-12 L0,-5 L11,-12", 1)
    c.add(f'<rect x="5" y="-11" width="4" height="4" fill="{P.RED}"/>')
    return _at(c, x, y, k, turn=turn)


def _letter_bundle(x: float, y: float, k: float = 1.0) -> str:
    """A bundle of letters tied crosswise with string, held by the knot at the origin."""
    c = Canvas()
    for i, color in enumerate((P.PINK_PALE, P.YELLOW_PALE, P.CARD)):
        c.add(f'<g transform="translate({-1 + i},{14 - i * 3}) rotate({(-6, 4, -2)[i]})">')
        c.shape("M-12,0 V-12 H12 V0 Z", color, sw=1.3, light=None)
        c.line("M-12,-12 L0,-5 L12,-12", 1)
        c.add("</g>")
    c.line("M0,0 V14 M-12,6 Q0,4 12,6", 1.4, P.RED)
    c.add(f'<circle cx="0" cy="1" r="2" fill="{P.RED}" stroke="{INK}" stroke-width=".8"/>')
    return _at(c, x, y, k)


def _telegram(x: float, y: float, k: float = 1.0) -> str:
    """The first half of a telegram, held at its lower edge (the origin): a header band and a few typed lines,
    and below them the paper torn off."""
    c = Canvas()
    torn = " ".join(f"L{-17 + i * 4.25},{-2 if i % 2 else 2}" for i in range(9))
    c.shape(f"M-17,0 V-36 H17 V0 {torn} Z", P.YELLOW_PALE, sw=1.5, light=None)
    c.shape("M-17,-36 H17 V-29 H-17 Z", P.CARD, sw=1.2, light=None)
    c.line("M-10,-32.5 h20", 2, P.RED, 0.8)
    for i, w in enumerate((26, 22, 14)):
        c.line(f"M-12,{-22 + i * 6} h{w}", 2.2, P.PEN, 0.7)
    return _at(c, x, y, k)


def _torn_half(x: float, y: float, k: float = 1.0) -> str:
    """The telegram's lost lower half, torn along its top, lying on the floor; the origin is the middle of its
    near edge. 26 wide, 7 tall."""
    c = Canvas()
    torn = " ".join(f"L{-13 + i * 3.25},{-13 + (1.5 if i % 2 else -1.5)}" for i in range(9))
    c.shape(f"M-13,0 {torn} V0 Z", P.YELLOW_PALE, sw=1.3, light=None)
    for i, w in enumerate((18, 13)):
        c.line(f"M-9,{-8 + i * 4.5} h{w}", 1.8, P.PEN, 0.7)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)},{n(k * 0.5)})">{c.render()}</g>'


@episode("postman")
def postman(s: Strip) -> None:
    """The sparrow plays postman down the office corridor with a bundle of letters, leaving one at every door; at
    the last door the agent opens its telegram - and only the first half is there. The second half lies on the
    floor back in the corridor. A plant stands in the corner."""
    s.indoors()
    k = s.unit
    dk = min(k, (s.base - 12) / 130)
    for i, frac in enumerate((0.15, 0.42, 0.65)):
        x = s.x(frac)
        top = s.base + 1 - _door_height(dk) * dk
        s.put(s.base, _door(x, s.base + 1, dk, str(i + 1)), (x - 25 * dk, top, x + 25 * dk, s.base + 1),
              f"door{i}")
        s.thing(lambda x, y, k, i=i: _letter_card(x, y, k, (-8, 6, -4)[i], (P.CARD, P.PINK_PALE, P.YELLOW_PALE)[i]),
                frac + 0.03, 24, 14, nearer=0.4, name=f"letter{i}")
    x = s.x(0.87)
    top = s.base + 1 - _door_height(dk) * dk
    s.put(s.base, _door(x, s.base + 1, dk, "4", open_=True), (x - 25 * dk, top, x + 25 * dk, s.base + 1),
          "door4", group="door4")
    s.thing(lambda x, y, k: props.plant(x, y, k * 0.6), 0.02, 44, 56, name="plant")
    bird = s.cast("sparrow", 0.29, "walk", "smile", flip=False)
    gx, gy, _ = _on(bird, False, 198, 131)
    s.put(bird.bottom + 1, _letter_bundle(gx, gy, k * 0.85), None, group=bird.group)
    s.thing(lambda x, y, k: _torn_half(x, y, k * 0.9), 0.53, 26, 8, nearer=0.55, name="half")
    agent = s.cast("agent", 0.84, "read", "surprise", flip=True, mark="?", group="door4", nearer=0.3)
    s.held(agent, "read", True, lambda x, y, kk: _telegram(x, y, kk * 0.75))


# ============================================================================ 11. diploma
def _diploma(x: float, y: float, k: float = 1.0, title: str = "", turn: float = 0) -> str:
    """A diploma with a red ribbon and a round blue stamp, held by its two side edges; the origin is the middle of
    its left edge, 50 x 32, turned by `turn` about it. The title is lettered only when it can be read."""
    c = Canvas()
    c.shape("M-2,-16 H52 V16 H-2 Z", P.CARD, sw=1.7, light=None)
    c.path("M2,-12.5 H48 V12.5 H2 Z", "none", 1, P.AMBER)
    size = _lettering(k, 8)
    if title and sets.letter_width(title, size) <= 42 and size <= 13:     # clear of the gilt border
        sets.fit_label(c, 25, -9 + size * 0.7, title, size, 38, P.RED, style=_letter_face(k, size))
        c.line("M9,6 h22", 1.2, P.PEN, 0.6)
    else:
        c.line("M9,-5 h30 M9,1 h26 M9,7 h20", 1.6, P.PEN, 0.6)
    c.add(f'<circle cx="40" cy="4.5" r="4.8" fill="none" stroke="{P.BLUE}" stroke-width="1.4"/>'
          f'<circle cx="40" cy="4.5" r="2.9" fill="none" stroke="{P.BLUE}" stroke-width=".8"/>')
    c.shape("M14,15 L10,28 L14,26 L16,31 L19,16 Z", P.RED, sw=1, light=None)
    return _at(c, x, y, k, turn=turn)


def _bouquet(x: float, y: float, k: float = 1.0) -> str:
    """A bunch of flowers in paper; the origin is where it is held."""
    c = Canvas()
    c.line("M0,0 L-6,-18 M0,0 L0,-22 M0,0 L6,-18", 1.6, P.LEAF_DARK)
    for fx, fy, color in ((-7, -20, P.RED), (0, -25, P.SUN), (7, -20, P.PINK), (-3, -15, P.WHITE),
                          (4, -14, P.VIOLET)):
        c.add(f'<circle cx="{fx}" cy="{fy}" r="4" fill="{color}" stroke="{INK}" stroke-width="1"/>')
        c.dot(fx, fy, 1.2, P.SUN if color != P.SUN else P.ORANGE)
    c.shape("M-8,-10 L8,-10 L2,6 L-2,6 Z", P.CARD, sw=1.3, light=None)
    return _at(c, x, y, k)


def _hankie(x: float, y: float, k: float = 1.0, mirror: bool = False) -> str:
    """A handkerchief fluttering from a wing tip; the origin is the corner held."""
    c = Canvas()
    clip = c.shape("M0,0 Q10,-8 22,-4 Q18,6 24,14 Q12,12 2,16 Q4,8 0,0 Z", P.WHITE, sw=1.3, light=None, clip=True)
    dots = "".join(f'<circle cx="{dx}" cy="{dy}" r="1.6" fill="{P.BLUE}"/>'
                   for dx, dy in ((8, -1), (16, 0), (6, 8), (14, 7), (20, 10), (10, 13)))
    c.add(f'<g clip-path="url(#{clip})">{dots}</g>')
    c.path("M0,0 Q10,-8 22,-4 Q18,6 24,14 Q12,12 2,16 Q4,8 0,0 Z", "none", 1.3)
    c.line("M28,-6 q4,4 0,8 M30,6 q4,4 0,8", 1, opacity=0.7)
    return _at(c, x, y, k, mirror)


def _cake_table(x: float, y: float, k: float = 1.0) -> str:
    """A small table with a cake and one candle on it; 60 wide, 76 tall."""
    c = Canvas()
    c.add(things.kitchen_table(0, 0, 0.55, 100, P.WOOD_LIGHT, P.BLUE))
    t = -27
    c.shape(f"M-20,{t} V{t - 16} H20 V{t} Z", P.PINK_PALE, sw=1.6, light=(-1, -1))
    c.shape(f"M-20,{t - 16} Q-20,{t - 20} -14,{t - 20} H14 Q20,{t - 20} 20,{t - 16} Q14,{t - 12} 8,{t - 16} "
            f"Q2,{t - 12} -4,{t - 16} Q-10,{t - 12} -20,{t - 16} Z", P.WHITE, sw=1.4, light=None)
    c.line(f"M-20,{t - 7} H20", 2.2, P.RED)
    c.shape(f"M-2,{t - 20} V{t - 32} H2 V{t - 20} Z", P.SKY_DEEP, sw=1, light=None)
    c.shape(f"M0,{t - 33} Q-3,{t - 37} 0,{t - 42} Q3,{t - 37} 0,{t - 33} Z", P.SUN, sw=1, light=None)
    for dx in (-12, 12):
        c.add(f'<circle cx="{dx}" cy="{t - 18}" r="2.4" fill="{P.RED}" stroke="{INK}" stroke-width=".8"/>')
    return _at(c, x, y, k)


@episode("diploma")
def diploma(s: Strip) -> None:
    """The professor hands the agent its diploma, stamp and ribbon and all; the agent takes it, beaming.
    The caterpillar has brought flowers, the sparrow waves a polka-dot handkerchief, a red balloon is tied to the
    cake table; a cake waits on the table, butterflies and a bee have come to the party."""
    s.outdoors()
    k = s.unit
    s.thing(lambda x, y, k: _cake_table(x, y, k), 0.04, 58, 76, name="cake", group="cake")
    cater = s.cast("caterpillar", 0.17, "present", "smile", flip=False)
    s.in_hand(cater, "present", False, lambda x, y, kk: _bouquet(x, y, kk * 0.8))
    prof = s.cast("professor", 0.33, "present", "talk", flip=False, group="award")
    # The agent stands where its raised hand takes the diploma's far edge from the professor's hand.
    hx, hy = s.hand(prof, "present", False)
    agent_mod = module("agent")
    ka = s.tall / 426 * agent_mod.SCENE_SCALE
    reach = 46 * k
    ax = hx + reach + (agent_mod.POSES["wave"][2][1][0] - agent_mod.CENTER_X) * ka
    agent = s.cast("agent", (ax - s.lo) / (s.hi - s.lo), "wave", "smile", flip=True, group="award", mark="ok")
    bx, by = s.hand(agent, "wave", True)
    length = math.hypot(bx - hx, by - hy)
    s.put(prof.bottom + 2, _diploma(hx, hy, length / 50, s.word("title"), math.degrees(math.atan2(by - hy, bx - hx))),
          None, group="award")
    bird = s.cast("sparrow", 0.7, "wave", "talk", flip=True)
    gx, gy, _ = _on(bird, True, 174, 59)
    s.put(bird.bottom + 1, _hankie(gx, gy - 4 * k, k, mirror=True), (gx - 32 * k, gy - 12 * k, gx, gy + 14 * k),
          group=bird.group)
    s.thing(lambda x, y, k: props.tulip(x, y, k * 0.8, P.RED) + props.daisy(x + 12 * k, y + 2 * k, k * 0.7), 0.83,
            30, 30, nearer=0.6, name="flowers")
    low = _festoon(s, 3)
    sky = _sky(s)
    # A red balloon tied to the corner of the cake table, its string going up from the knot.
    tx, ty = s.x(0.04) + 26 * k, s.feet(s.x(0.04)) - 27 * k
    bk = k * 0.6
    for length in (70, 56, 44):
        top = ty - (length + 48) * bk
        box = (tx - 20 * bk, top, tx + 20 * bk, ty - length * bk + 4)
        if top > max(s.h * 0.2, low + 6) and s.free(box, 4):
            s.put(ty + 1, f'<g transform="translate({n(tx)},{n(ty)}) scale({n(bk)})">'
                          f'{props.balloon(0, 0, length, P.RED)}</g>', box, "balloon", group="cake")
            break
    _flutter(s, [lambda x, y: props.butterfly(x, y, k * 0.9, P.YELLOW), lambda x, y: things.bee(x, y, k * 0.9),
                 lambda x, y: props.butterfly(x, y, k * 0.8, P.PINK)], (sky[0], max(sky[1], low + 8, s.h * 0.2),
                                                                         sky[2], sky[3]), 22 * k, "bug")


# ============================================================================ 12. walk_home
def _scroll(x: float, y: float, k: float = 1.0, lean: float = -30) -> str:
    """A rolled scroll with a red seal on a string; the origin is where it is held, the top leaning by `lean`."""
    c = Canvas()
    c.add(f'<g transform="rotate({n(lean)})">')
    c.shape("M-5,-26 H5 V8 H-5 Z", P.SCROLL, sw=1.4, light=None)
    c.shape(ellipse_d(0, -26, 5, 2), P.SCROLL_SHADE, sw=1.2, light=None)
    c.line("M-5,-8 H5", 1.6, P.RED)
    c.add(f'<circle cx="0" cy="-8" r="3" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>')
    c.add("</g>")
    return _at(c, x, y, k)


def _picnic_basket(x: float, y: float, k: float = 1.0) -> str:
    """A wicker picnic basket with a checked cloth and a bottle; the origin is between the hands."""
    c = Canvas()
    c.line("M-14,-14 Q0,-34 14,-14", 2.6, P.WOOD_DARK)
    c.shape("M-6,-18 V-28 H-2 V-18 Z", P.GREEN, sw=1, light=None)
    c.shape("M-16,-14 H16 L12,4 H-12 Z", P.WOOD_LIGHT, sw=1.6, light=(-1, -1))
    c.line("M-15,-8 H15 M-14,-2 H14", 1, P.WOOD_DARK)
    c.shape("M-12,-16 Q-4,-22 4,-14 L10,-16 L6,-12 H-12 Z", P.RED, sw=1, light=None)
    return _at(c, x, y, k)


def _hiker_kit(box: Box, flip: bool) -> str:
    """The professor's huge backpack with a rolled mat, a pan tied on top and a mug swinging below, on his back in
    his walk pose, facing right."""
    back = Canvas()
    back.shape("M22,170 Q18,128 60,124 H96 Q118,128 116,170 L120,320 Q70,340 18,320 Z", P.GREEN, sw=3,
               light=(-4, -3), stipple=(18, 200, 30, 120, 30, "left"))
    back.shape("M10,230 Q4,226 6,250 L10,300 Q16,306 22,300 V236 Z", darken(P.GREEN, 0.85), sw=2.4, light=None)
    back.shape("M30,250 H106 V300 Q68,310 30,300 Z", darken(P.GREEN, 0.88), sw=2.4, light=None)
    back.add(f'<rect x="62" y="266" width="12" height="12" rx="2" fill="{P.SUN}" stroke="{INK}" '
             f'stroke-width="2"/>')
    back.shape(rounded_rect_d(14, 92, 108, 34, 15), P.RED, sw=2.6, light=(-2, -2))
    back.line("M30,94 V124 M106,94 V124", 2.4, P.WOOD_DARK)
    back.line("M68,126 V60", 3, P.METAL_DARK)
    back.shape(ellipse_d(68, 56, 18, 6), P.METAL, sw=2.2, light=None)          # a pan tied on top
    back.line("M8,320 q-4,10 4,16 q8,4 10,-6", 2, P.METAL_DARK)
    back.shape("M2,336 H22 V352 Q12,358 2,352 Z", P.BLUE, sw=2, light=None)     # a mug swinging below
    return _dress(box, flip, back)


def _mushroom_basket(x: float, y: float, k: float = 1.0) -> str:
    """A small basket of mushrooms hanging from a hand; the origin is the hand."""
    c = Canvas()
    c.line("M-10,10 Q0,-6 10,10", 2, P.WOOD_DARK)
    for mx, color in ((-6, P.RED), (1, P.TRUNK), (7, P.RED)):
        c.add(props.mushroom(mx, 12, 0.32, color))
    c.shape("M-12,10 H12 L9,22 H-9 Z", P.WOOD_LIGHT, sw=1.4, light=None)
    c.line("M-11,15 H11", 0.9, P.WOOD_DARK)
    return _at(c, x, y, k)


def _cottage(x: float, y: float, k: float = 1.0) -> str:
    """A little house with a lit window and smoke from the chimney: home; 88 wide, 100 tall. The chimney stands on
    the roof: it is drawn first and the roof covers its foot."""
    c = Canvas()
    c.shape("M18,-60 V-92 H30 V-52 Z", P.STONE, sw=1.8, light=(-1, -1))
    c.shape(rounded_rect_d(16, -96, 16, 5, 1.5), darken(P.STONE, 0.85), sw=1.5, light=None)
    c.line("M24,-98 q-8,-10 2,-18 q8,-8 -2,-16", 2, P.WHITE, 0.8)
    c.shape("M-36,0 V-50 H36 V0 Z", P.CREAM, sw=2, light=(-2, -1))
    c.shape("M-44,-46 L0,-84 L44,-46 Z", P.RED, sw=2, light=(-2, -2))
    c.shape("M-24,0 V-30 H-6 V0 Z", P.WOOD_DARK, sw=1.6, light=None)
    c.add(f'<circle cx="-10" cy="-14" r="1.6" fill="{P.SUN}"/>')
    c.add(f'<ellipse cx="15" cy="-29" rx="20" ry="16" fill="{P.SUN}" opacity=".25"/>')
    c.add(f'<rect x="4" y="-38" width="22" height="18" fill="{P.SUN}" stroke="{INK}" stroke-width="1.8"/>')
    c.line("M15,-38 V-20 M4,-29 H26", 1.4)
    return _at(c, x, y, k)


def _rod(hx: float, hy: float, kk: float) -> tuple[str, list]:
    """A fishing rod held in a hand at (hx, hy), reaching forward and up, its line hanging with a red float;
    `kk` is the professor's canvas scale. Returns the drawing and boxes along the rod."""
    tx, ty = hx + 130 * kk, hy - 190 * kk
    fx, fy = tx + 14 * kk, ty + 100 * kk
    c = Canvas()
    c.line(f"M{n(hx - 8 * kk)},{n(hy + 12 * kk)} L{n(tx)},{n(ty)}", 6 * kk + 2.4)
    c.line(f"M{n(hx - 8 * kk)},{n(hy + 12 * kk)} L{n(tx)},{n(ty)}", 6 * kk, P.WOOD_DARK)
    c.add(f'<circle cx="{n(hx + 10 * kk)}" cy="{n(hy - 14 * kk)}" r="{n(8 * kk)}" fill="{P.METAL}" stroke="{INK}" '
          f'stroke-width="{n(1.6)}"/>')
    c.line(f"M{n(tx)},{n(ty)} Q{n(tx + 18 * kk)},{n(ty + 40 * kk)} {n(fx)},{n(fy)}", 1.1)
    c.shape(ellipse_d(fx, fy + 6 * kk, 5 * kk, 7 * kk), P.RED, sw=1.4, light=None)
    c.line(f"M{n(fx - 5 * kk)},{n(fy + 6 * kk)} h{n(10 * kk)}", 1.2, P.WHITE)
    boxes = strip_boxes([(hx, hy), ((hx + tx) / 2, (hy + ty) / 2), (tx, ty)], 10 * kk)
    boxes.append((tx - 4 * kk, ty, fx + 8 * kk, fy + 14 * kk))
    return c.render(), boxes


def _home_road(s: Strip, door_x: float, door_y: float, door_w: float) -> None:
    """A country road in perspective, painted on the ground under the walkers' feet: wide where it leaves the
    strip at the near left, narrowing as it runs back to the cottage door; soft edges, a worn middle, pebbles."""
    c, rnd = s.back, random.Random(s.seed)
    near, _ = ground_colors(s.look)
    dirt = mix(P.SAND, near, 0.18)
    h = s.h
    top0 = s.feet(0) - max(5.0, s.ground * 0.12)          # the far edge at the left, just behind everyone's feet
    bot0 = h + 6                                            # the near edge leaves the strip at the bottom
    lx, rx = -10, door_x
    d = (f"M{n(lx)},{n(top0)} C{n(lx + (rx - lx) * 0.4)},{n(top0 - 2)} {n(rx - (rx - lx) * 0.25)},"
         f"{n(door_y - 1)} {n(rx - door_w * 0.6)},{n(door_y)} L{n(rx + door_w * 0.6)},{n(door_y)} "
         f"C{n(rx - (rx - lx) * 0.1)},{n(door_y + (bot0 - door_y) * 0.35)} {n(lx + (rx - lx) * 0.45)},{n(bot0)} "
         f"{n(lx + (rx - lx) * 0.2)},{n(bot0)} L{n(lx)},{n(bot0)} Z")
    c.add(f'<path d="{d}" fill="{dirt}" stroke="{darken(dirt, 0.78)}" stroke-width="1.4" stroke-linejoin="round"/>')
    mid_y0 = (top0 + bot0) / 2
    mid = (f"M{n(lx)},{n(mid_y0)} C{n(lx + (rx - lx) * 0.45)},{n(mid_y0 - 2)} {n(rx - (rx - lx) * 0.2)},"
           f"{n(door_y + 4)} {n(rx)},{n(door_y + 1)}")
    c.add(f'<path d="{mid}" fill="none" stroke="{lighten(dirt, 0.35)}" stroke-width="{n(12 * s.unit)}" '
          f'stroke-linecap="round" opacity=".5"/>')
    for _ in range(int(14 + h / 20)):            # pebbles, smaller towards the door
        t = rnd.random()                          # 0 at the door, 1 at the left edge
        x = rx + (lx - rx) * t
        top = door_y + (top0 - door_y) * t
        bottom = door_y + (bot0 - door_y) * min(1.0, t * 1.6)
        if bottom - top < 8:
            continue
        y = rnd.uniform(top + 3, bottom - 3)
        r = 0.8 + 1.6 * t
        c.add(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(r * 1.3)}" ry="{n(r)}" fill="{darken(dirt, 0.82)}" '
              f'opacity=".8"/>')


@episode("walk_home")
def walk_home(s: Strip) -> None:
    """At sunset everyone walks home along the path: the cat in front with a rolled scroll,
    lecturing over his shoulder that the programmer is the one in charge; the professor under a huge backpack, a
    fishing rod in one hand and a basket of mushrooms in the other; the agent bringing up the rear with the picnic
    basket. The cottage window is already lit."""
    s.relook(time="evening")
    s.outdoors()
    k = s.unit
    _home_road(s, s.x(0.88) - 15 * k * 1.1, s.feet(s.x(0.88)), 18 * k * 1.1)
    agent = s.cast("agent", 0.08, "type", "smile", flip=False)
    s.held(agent, "type", False, lambda x, y, kk: _picnic_basket(x, y, kk * 1.1))
    prof = s.cast("professor", 0.36, "walk", "smile", flip=False, group="prof")
    kk = (prof.bottom - prof.top) / 426
    mid = (prof.left + prof.right) / 2
    s.put(prof.bottom - 1, _hiker_kit(prof, False),
          (mid - 122 * kk, prof.bottom - 386 * kk, mid - 4 * kk, prof.bottom - 76 * kk), group="prof")
    hx, hy = s.hand(prof, "walk", False, "left")     # the rod in the forward hand
    rod, boxes = _rod(hx, hy, kk)
    s.put(prof.bottom - 0.5, rod, boxes, "rod", group="prof")
    s.in_hand(prof, "walk", False, lambda x, y, kc: _mushroom_basket(x, y, kc * 0.75))   # the basket in the other
    cat = s.cast("cat", 0.6, "point", "talk", flip=True, mark="!")
    hx, hy = s.hand(cat, "point", True, "left")
    # The scroll is gripped in the hanging paw (drawn behind it), its top leaning out, away from the body.
    s.put(cat.bottom - 0.5, _scroll(hx, hy, k, 24), None, group=cat.group)
    s.thing(lambda x, y, k: _cottage(x, y, k * 1.1), 0.88, 100, 136, name="home")

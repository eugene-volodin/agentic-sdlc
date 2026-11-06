"""Footer episodes, group A: prompts, plans, giving instructions, supervising the agent.

Each episode retells a plot of the printed original with the agent in it; the props they need and nobody else
does are private functions here, drawn like those of `things.py`: `_thing(x, y, k, ...) -> str`, the origin
where the thing touches the ground, at the scale of a 137-unit professor when k = 1.

Lettering is sized in units of the strip, never below `LETTERING` (it must read in the 34 mm strip); a word that
cannot be that big is left out.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten, mix
from . import props, sets, things
from .characters import module
from .footers import Strip, episode, ground_colors, night_sky, sky_colors, wall_color
from .ink import INK, Canvas, ellipse_d, n, rounded_rect_d
from .openers import W, Box, strip_boxes
from .scenes import PROFESSOR_HEIGHT
from .scenes import actor as _draw_actor
from .sets import _at, _label, fit_label, letter_width

CHALK = "Caveat"
LETTERING = 10.0       # the smallest lettering drawn here, in strip units


# ============================================================================ helpers
def _pt(box: Box, cx: float, cy: float, flip: bool) -> tuple[float, float, float]:
    """A point of a character's own drawing (its canvas units) on the page, and the character's scale."""
    mod = module(box.name)
    k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
    mid = (box.left + box.right) / 2
    dx = (cx - mod.CENTER_X) * k
    return (mid - dx if flip else mid + dx), box.bottom - (mod.FEET_Y - cy) * k, k


def _float(s: Strip, name: str, x: float, feet: float, pose: str = "stand", mood: str = "smile",
           flip: bool = False, group: str | None = None, size: float = 1.0, depth: float | None = None) -> Box:
    """A character standing on something off the ground (a cloud, a rocket, a saucer) or lifted by balloons:
    upright, but with no shadow on the ground under its feet."""
    mod = module(name)
    tall = s.tall * size
    k = tall / PROFESSOR_HEIGHT * mod.SCENE_SCALE
    s.put(feet if depth is None else depth, _draw_actor(name, x, feet, tall, pose, mood, flip=flip, shadow=False))
    half = mod.SIZE[0] * 0.40 * k
    box = Box(x - half, feet - (mod.FEET_Y - mod.HEAD_TOP) * k, x + half, feet, name, group or name, "actor", flip)
    s.boxes.append(box)
    return box


def _arrow(c: Canvas, d: str, end: tuple[float, float], toward: tuple[float, float], color: str, width: float,
           head: float, outline: float = 1.4) -> None:
    """A stroked path with a filled head at `end`, aligned with the path's last direction (from `toward`)."""
    c.tube(d, color, width, sw=outline, shaded=False)
    ang = math.atan2(end[1] - toward[1], end[0] - toward[0])
    ux, uy = math.cos(ang), math.sin(ang)
    tip = (end[0] + ux * head * 0.7, end[1] + uy * head * 0.7)
    back = (end[0] - ux * head * 0.5, end[1] - uy * head * 0.5)
    a = (back[0] - uy * head * 0.6, back[1] + ux * head * 0.6)
    b = (back[0] + uy * head * 0.6, back[1] - ux * head * 0.6)
    c.path(f"M{n(tip[0])},{n(tip[1])} L{n(a[0])},{n(a[1])} L{n(b[0])},{n(b[1])} Z", color, outline)


def _paper_plane(x: float, y: float, k: float = 1.0, turn: float = 0, color: str = P.CARD) -> str:
    """A folded paper plane, its nose to the right; the origin is under its middle. 30 long."""
    c = Canvas()
    c.shape("M-15,-4 L15,-8 L-10,-12 Z", color, sw=1.4, light=None)
    c.shape("M-15,-4 L15,-8 L-6,0 Z", darken(color, 0.9), sw=1.4, light=None)
    c.line("M-13,-5 L15,-8", 0.9)
    return _at(c, x, y, k, turn=turn)


def _cup(x: float, y: float, k: float = 1.0, color: str = P.RED, steam: bool = True) -> str:
    """A teacup on a saucer, 16 wide; the origin is under the saucer."""
    c = Canvas()
    if steam:
        c.line("M-2,-13 q-3,-4 0,-8 M3,-13 q3,-4 0,-9", 1.2, P.WHITE, 0.9)
    c.shape("M-6,-11 H6 Q6,-1 0,-1 Q-6,-1 -6,-11 Z", color, sw=1.4, light=(-1, -1))
    c.line("M6,-9 q4,1 1,5", 1.4)
    c.shape(ellipse_d(0, -0.5, 8, 1.8), P.WHITE, sw=1.2, light=None)
    return _at(c, x, y, k)


# ============================================================================ 1. the potato algorithm
_BOARD_PAD = 0.6          # the even margin round the chalk lettering, in letter sizes
_BOARD_LEAD = 1.26        # from one chalked step to the next


def _board_size(steps: list[str], title: str | None) -> tuple[float, float]:
    """How wide and how tall the inside of the blackboard is per unit of letter size."""
    wide = max(sets.letter_width(t, 1) for t in steps) + 2 * _BOARD_PAD + 1.9
    if title:
        wide = max(wide, sets.letter_width(title, 1.2) + 2 * _BOARD_PAD)
    tall = 2 * _BOARD_PAD + (0.9 + 1.45 if title else 0.75) + (len(steps) - 1) * _BOARD_LEAD + 0.2
    return wide, tall


def _blackboard(left: float, top: float, right: float, bottom: float, title: str | None, steps: list[str],
                size: float, k: float) -> tuple[str, list[float], float]:
    """A school blackboard with numbered steps chalked on it and a chalk arrow looping from the last step back
    to the first. Returns the drawing, the baselines of the steps and where the text starts."""
    c = Canvas()
    f = max(3.0, 5 * k)
    c.shape(rounded_rect_d(left, top, right - left, bottom - top, 3 * k), P.WOOD, sw=2, light=None)
    c.shape(f"M{n(left + f)},{n(top + f)} H{n(right - f)} V{n(bottom - f)} H{n(left + f)} Z", darken(P.FIR, 0.62),
            sw=1.4, light=(-3, -3), shade_k=0.85)
    c.line(f"M{n(left + 3 * f)},{n(bottom - 2 * f)} q{n(20 * k)},{n(-6 * k)} {n(36 * k)},{n(-2 * k)}", 3 * k,
           P.WHITE, 0.15)   # a wiped smear
    chalk = lighten(P.YELLOW_PALE, 0.5)
    pad = size * _BOARD_PAD
    x0 = left + f + pad
    y = top + f + pad + size * (0.9 if title else 0.75)
    if title:
        _label(c, (left + right) / 2, y, title, size * 1.2, chalk)
        y += size * 1.45
    ys = []
    for text in steps:
        _label(c, x0, y, text, size, P.WHITE, anchor="start")
        ys.append(y)
        y += size * _BOARD_LEAD
    # The loop: from the end of the last step round to the end of the first, an arrow in yellow chalk.
    ends = [x0 + sets.letter_width(t, size) for t in steps]
    xr = min(right - f - pad * 0.6, max(ends) + size * 1.3)
    y1, y9 = ys[0] - size * 0.32, ys[-1] - size * 0.32
    a0 = (min(ends[-1] + size * 0.3, xr - size * 0.6), y9)
    a1 = (min(ends[0] + size * 0.3, xr - size * 0.8), y1)
    d = f"M{n(a0[0])},{n(a0[1])} C{n(xr)},{n(y9)} {n(xr)},{n(y1)} {n(a1[0] + size * 0.4)},{n(y1)}"
    _arrow(c, d, (a1[0] + size * 0.4, y1), (xr, y1), P.SUN, max(1.2, size * 0.13), size * 0.55, 0.6)
    # The chalk tray: a stick of chalk and a sponge.
    c.shape(rounded_rect_d(left + 8 * k, bottom - 1 * k, right - left - 16 * k, 4 * k, 1.5 * k), P.WOOD_DARK,
            sw=1.4, light=None)
    c.shape(rounded_rect_d(left + 22 * k, bottom - 4 * k, 9 * k, 3 * k, 1.2 * k), P.WHITE, sw=1, light=None)
    c.shape(rounded_rect_d(right - 40 * k, bottom - 6 * k, 14 * k, 5 * k, 1.5 * k), P.SUN, sw=1, light=None)
    return c.render(), ys, x0


def _fist(s, box, pose: str) -> tuple[float, float]:
    """The middle of the closed fist of a character's near arm in `pose`, on the page: where a held rod passes."""
    mod = module(box.name)
    (ex, ey), (wx, wy), _, turn = mod.POSES[pose][-1]
    way = math.atan2(wy - ey, wx - ex)
    reach = mod.ARM_WIDTH * 0.42
    cx = wx + math.cos(way) * reach + math.cos(way + math.radians(turn)) * 9
    cy = wy + math.sin(way) * reach + math.sin(way + math.radians(turn)) * 9
    k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
    mid = (box.left + box.right) / 2
    dx = (cx - mod.CENTER_X) * k
    return (mid - dx if box.flip else mid + dx), box.bottom - (mod.FEET_Y - cy) * k


def _pointer(start: tuple[float, float], end: tuple[float, float], k: float) -> str:
    """A teacher's wooden pointer held in a fist at `start` to its chalk-white tip at `end`, thinning as it goes.
    Drawn under the hand, so the fingers close over its butt."""
    (x0, y0), (x1, y1) = start, end
    length = math.hypot(x1 - x0, y1 - y0) or 1
    nx, ny = -(y1 - y0) / length, (x1 - x0) / length
    w0, w1 = 2.2 * k + 1, 0.9 * k + 0.6
    pts = [(x0 + nx * w0, y0 + ny * w0), (x1 + nx * w1, y1 + ny * w1), (x1 - nx * w1, y1 - ny * w1),
           (x0 - nx * w0, y0 - ny * w0)]
    c = Canvas()
    c.shape("M" + " L".join(f"{n(a)},{n(b)}" for a, b in pts) + " Z", P.WOOD, sw=1.4, light=None)
    c.add(f'<circle cx="{n(x1)}" cy="{n(y1)}" r="{n(w1 + 0.8)}" fill="{P.WHITE}" stroke="{INK}" '
          f'stroke-width="1"/>')
    return c.render()


def _peeling(x: float, y: float, k: float = 1.0) -> str:
    """A potato and a knife in two hands, the peel hanging down in a long spiral."""
    c = Canvas()
    c.tube("M3,-4 Q8,4 2,8 Q-4,12 3,16 Q9,20 2,24 Q-3,27 4,30", P.TRUNK, 2.4, sw=1, shaded=False)
    c.shape("M-9,-2 Q-11,-10 -3,-11 Q6,-13 9,-7 Q11,-1 4,0 Q-4,2 -9,-2 Z", P.CREAM, sw=1.4, light=(-1, -1))
    c.path("M2,-12 Q9,-12 9,-6 Q8,-2 4,-1 Q6,-6 2,-12 Z", P.TRUNK, 1)
    c.shape("M10,-10 L22,-18 L24,-15 L13,-8 Z", P.METAL_LIGHT, sw=1.1, light=None)
    c.shape(rounded_rect_d(4, -11, 8, 5, 1.8), P.WOOD_DARK, sw=1.1, light=None)
    return _at(c, x, y, k)


def _dinner(x: float, y: float, k: float = 1.0) -> str:
    """A small round table with a plate of steaming boiled potatoes, dill and a salt cellar. 52 wide, 34 tall."""
    c = Canvas()
    c.line("M0,-28 V0 M-10,0 H10", 3, P.WOOD_DARK)
    c.line("M-14,-2 L0,-14 L14,-2", 2, P.WOOD_DARK)
    c.line("M-8,-44 q-4,-6 0,-11 M2,-46 q4,-6 0,-12 M10,-43 q-3,-5 0,-9", 1.4, P.WHITE, 0.95)
    c.shape(ellipse_d(0, -30, 26, 5), P.YELLOW_PALE, sw=1.8, light=None)
    c.path(ellipse_d(-2, -33, 18, 3.6), P.WHITE, 1.4)
    for px, py in ((-10, -35), (-2, -37), (6, -35), (-5, -40), (3, -41)):
        c.add(f'<ellipse cx="{px}" cy="{py}" rx="5.4" ry="4" fill="{P.CREAM}" stroke="{INK}" stroke-width="1.1"/>')
    for px, py in ((-7, -42), (1, -44), (8, -39)):
        c.line(f"M{px},{py} l2,-3 M{px},{py} l-2,-2 M{px},{py} l1,2", 1, P.LEAF_DARK)
    c.shape("M18,-32 V-40 Q18,-44 21,-44 Q24,-44 24,-40 V-32 Z", P.WHITE, sw=1.2, light=None)
    c.dot(20, -41, 0.6)
    c.dot(22, -39, 0.6)
    return _at(c, x, y, k)


def _fork(x: float, y: float, k: float = 1.0, turn: float = -30) -> str:
    """A fork with a potato speared on it; the origin is the end of its handle."""
    c = Canvas()
    c.tube("M0,0 L0,-14", P.METAL_LIGHT, 1.6, sw=0.8, shaded=False)
    c.line("M-2,-14 V-18 M0,-14 V-18 M2,-14 V-18 M-2,-14 H2", 1.1, P.METAL_DARK)
    c.add(f'<ellipse cx="0" cy="-21" rx="4.6" ry="3.8" fill="{P.CREAM}" stroke="{INK}" stroke-width="1.1"/>')
    c.line("M-2,-27 q-2,-3 0,-5 M2,-27 q2,-3 0,-6", 0.9, P.WHITE)
    return _at(c, x, y, k, turn=turn)


@episode("algorithm_board")
def algorithm_board(s: Strip) -> None:
    """The potato algorithm: the professor points at a blackboard of numbered steps for peeling potatoes, with a
    chalk loop from «not all peeled?» back to the first step. The agent follows it to the letter, peel curling to
    the floor; at the far end the sparrow is already eating boiled potatoes with dill; a snail is in no
    hurry."""
    s.indoors()
    k = s.unit
    prof = s.cast("professor", 0.03, "pointer", "talk", flip=False)
    hx, hy = _fist(s, prof, "pointer")
    left = max(prof.right + 8 * k, hx + 30 * k)
    top = max(s.h * 0.2 + 2, s.base - 150 * k)
    bottom = s.base - 8 * k
    f = max(3.0, 5 * k)
    steps = [s.word(f"step{i}") for i in range(1, 5)]
    inner_h = bottom - top - 2 * f
    title: str | None = s.word("title")
    room_w = s.x(0.5) - left - 2 * f
    wide, tall = _board_size(steps, title)
    size = min(22.0, room_w / wide, inner_h / tall)
    if size < 11.5:
        title = None
        wide, tall = _board_size(steps, None)
        size = min(22.0, room_w / wide, inner_h / tall)
    right = left + 2 * f + size * wide
    top = bottom - 2 * f - size * tall
    art, ys, x0 = _blackboard(left, top, right, bottom, title, steps, size, k)
    s.put(3, art, (left, top, right, bottom + 4 * k), "board")
    tip = (x0 - size * 0.25, ys[0] - size * 0.3)
    s.put(prof.bottom - 0.5, _pointer((hx, hy), tip, k), None, group=prof.group)
    s.thing(lambda x, y, k: things.bucket(x, y, k), 0.56, 34, 48, nearer=0.35, name="pail")
    agent = s.cast("agent", 0.67, "type", "smile", flip=False, group="agent", size=1.1)
    s.held(agent, "type", False, lambda x, y, k: _peeling(x, y, k * 1.25))
    s.thing(lambda x, y, k: _stove(x, y, k * 0.85) + things.pot(x, y - 50 * 0.85 * k, k * 0.8), 0.78, 56, 84,
            name="pot")
    s.thing(lambda x, y, k: _dinner(x, y, k * 1.1), 0.89, 58, 50, name="dinner", group="dinner")
    sparrow = s.cast("sparrow", 0.98, "present", "smile", flip=True, group="dinner")
    fx, fy = s.hand(sparrow, "present", True)
    s.put(sparrow.bottom + 1, _fork(fx, fy, k * 1.1, -25), None, group="dinner")
    # A side story: a snail goes its own way.
    s.thing(lambda x, y, k: sets.snail(x, y, k * 0.55), 0.47, 30, 18, nearer=0.95, name="snail")


# ============================================================================ 2. steps on the washing line
CARD_PAD = 0.85        # a step card's side margin, in em of its lettering
CARD_GAP = 0.9         # the air between two step cards, in em
CARD_TALL = 1.85       # a step card's height, in em
CARD_COLORS = (P.BLUE, P.GREEN, P.ORANGE, P.RED)


def _card_room(words: list[str]) -> float:
    """How wide the step cards stand in a row for lettering 1 unit tall, with their margins and the air."""
    return sum(letter_width(w, 1) + 2 * CARD_PAD for w in words) + (len(words) + 1) * CARD_GAP


def _clothespin(c: Canvas, x: float, y: float, h: float) -> None:
    """A wooden clothespin standing at (x, y), the tips of its jaws; `h` tall: two jaws split at the bottom and a
    steel spring wound round its waist."""
    w = h * 0.3
    c.shape(rounded_rect_d(x - w / 2, y - h, w, h, w * 0.4), P.WOOD_LIGHT, sw=1.1, light=(-0.6, 0), shade_k=0.85)
    c.line(f"M{n(x)},{n(y)} V{n(y - h * 0.42)}", 0.9, P.WOOD_DARK)
    c.add(f'<rect x="{n(x - w / 2 - 0.6)}" y="{n(y - h * 0.62)}" width="{n(w + 1.2)}" height="{n(h * 0.12)}" '
          f'rx="{n(h * 0.05)}" fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width=".8"/>')


def _nail(c: Canvas, x: float, y: float, r: float, side: int) -> None:
    """A nail in the wall with the line knotted round it: `side` is the way the line runs off (+1 right)."""
    c.add(f'<ellipse cx="{n(x + r * 0.5)}" cy="{n(y + r * 0.6)}" rx="{n(r * 1.1)}" ry="{n(r * 0.7)}" fill="{INK}" '
          f'opacity=".14"/>')
    c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1.1"/>')
    c.add(f'<circle cx="{n(x - r * 0.3)}" cy="{n(y - r * 0.3)}" r="{n(r * 0.35)}" fill="{P.METAL_PALE}"/>')
    c.line(f"M{n(x - r * 0.9 * side)},{n(y + r * 0.2)} q{n(r * 0.9 * side)},{n(r * 2.2)} {n(r * 2.2 * side)},"
           f"{n(r * 0.6)}", 1.2, P.WOOD_DARK)


def _washing_line(x0: float, x1: float, y: float, words: list[str], size: float, k: float) -> tuple[str, float]:
    """A line sagging between two nails in the wall with the step cards pegged to it, numbered as they hang;
    returns the drawing and how far down the lowest card reaches."""
    c = Canvas()
    sag = 7 * k
    r = max(2.4, 3 * k)
    _nail(c, x0, y, r, 1)
    _nail(c, x1, y, r, -1)
    c.line(f"M{n(x0)},{n(y)} Q{n((x0 + x1) / 2)},{n(y + 2 * sag)} {n(x1)},{n(y)}", 1.4, P.WOOD_DARK)
    widths = [letter_width(w, size) + 2 * CARD_PAD * size for w in words]
    ch = CARD_TALL * size
    pin = max(9.0, size * 0.95)
    badge = max(7.0, size * 0.5)
    gap = (x1 - x0 - sum(widths)) / (len(words) + 1)        # wider than a badge: the size was fitted to it
    low = y
    left = x0 + gap
    for i, (word, cw) in enumerate(zip(words, widths, strict=True)):
        cx = left + cw / 2
        left += cw + gap
        t = (cx - x0) / (x1 - x0)
        cy = y + 4 * sag * t * (1 - t) + 0.6
        tint = CARD_COLORS[i % len(CARD_COLORS)]
        g = Canvas()
        card = rounded_rect_d(-cw / 2, 0, cw, ch, size * 0.16)
        g.add(f'<path d="{rounded_rect_d(-cw / 2 + 1.6, 2.4, cw, ch, size * 0.16)}" fill="{INK}" opacity=".16"/>')
        g.shape(card, mix(P.CARD, tint, 0.1), sw=1.4, light=(-1.2, -1), shade_k=0.94)
        # held to the estimated width, so the margins stay even whatever the face really measures
        fit_label(g, 0, ch / 2 + size * 0.36, word, size, (cw - 2 * CARD_PAD * size) * 0.995, tint)
        for px in (-cw * 0.3, cw * 0.3):
            _clothespin(g, px, size * 0.5, pin)
        bx, by = -cw / 2, ch       # a round sticker on the lower left corner, clear of the word
        g.add(f'<circle cx="{n(bx)}" cy="{n(by)}" r="{n(badge)}" fill="{tint}" stroke="{INK}" stroke-width="1.2"/>')
        g.add(f'<circle cx="{n(bx - badge * 0.3)}" cy="{n(by - badge * 0.35)}" r="{n(badge * 0.28)}" '
              f'fill="{P.WHITE}" opacity=".35"/>')
        _label(g, bx, by + badge * 0.44, str(i + 1), badge * 1.3, P.WHITE, style="plain")
        turn = 2.6 if i % 2 else -2.6
        c.add(f'<g transform="translate({n(cx)},{n(cy)}) rotate({n(turn)})">{g.render()}</g>')
        low = max(low, cy + ch + badge + 0.5)
    return c.render(), low


def _sink(x: float, y: float, k: float = 1.0) -> str:
    """A kitchen cupboard with a basin, a dripping tap and a full jug left standing by it. 74 wide, 64 tall."""
    c = Canvas()
    c.shape("M-36,0 V-44 H36 V0 Z", lighten(P.SKY, 0.5), sw=2, light=(-2, -1), shade_k=0.88)
    c.line("M0,-40 V-4", 1.4)
    c.add(f'<circle cx="-5" cy="-24" r="1.6" fill="{INK}"/><circle cx="5" cy="-24" r="1.6" fill="{INK}"/>')
    c.shape(rounded_rect_d(-38, -48, 76, 6, 2), P.WOOD_LIGHT, sw=1.8, light=None)
    c.shape("M-24,-48 Q-24,-42 -18,-42 H6 Q12,-42 12,-48 Z", P.METAL_LIGHT, sw=1.4, light=None)
    c.tube("M-6,-48 V-62 Q-6,-66 -2,-66 H4 V-60", P.METAL_LIGHT, 2.6, sw=1.1, shaded=False)
    c.add(f'<path d="M4,-56 q-2,3 0,5 q2,-2 0,-5 Z" fill="{P.WATER}" stroke="{INK}" stroke-width=".7"/>')
    c.shape("M18,-48 V-60 Q18,-64 22,-64 H30 Q33,-64 33,-60 V-48 Z", P.WATER_LIGHT, sw=1.4, light=None)
    c.add(f'<path d="M18.5,-57 H32.5 V-48.5 H18.5 Z" fill="{P.WATER}" opacity=".8"/>')
    c.line("M33,-60 q5,1 2,8", 1.4)
    return _at(c, x, y, k)


def _stove(x: float, y: float, k: float = 1.0, lit: bool = True) -> str:
    """A little enamel stove with an oven window and three knobs; a flame on the burner. 60 wide, 52 tall.
    The front knob on the right is at (14, -40)."""
    c = Canvas()
    c.shape("M-30,0 V-46 H30 V0 Z", P.CARD, sw=2, light=(-2, -2), shade_k=0.86)
    c.shape(rounded_rect_d(-32, -50, 64, 5, 2), P.METAL_DARK, sw=1.6, light=None)
    c.shape(rounded_rect_d(-22, -32, 44, 26, 3), P.METAL_PALE, sw=1.6, light=None)
    c.add(f'<rect x="-14" y="-26" width="28" height="12" rx="2" fill="{P.CHARCOAL}" opacity=".8"/>')
    c.line("M-14,-34 H14", 1.6)
    for kx in (-14, 0, 14):
        c.add(f'<circle cx="{kx}" cy="-40" r="3" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="1"/>')
    if lit:
        for fx in (-8, -3, 2, 7):
            c.add(f'<path d="M{fx - 2.5},-50 q2.5,-7 2.5,-9 q2.5,4 2.5,9 Z" fill="{P.ORANGE}" stroke="{INK}" '
                  f'stroke-width=".7"/><path d="M{fx - 1},-50 q1,-3 1,-4 q1,2 1,4 Z" fill="{P.SUN}"/>')
    return _at(c, x, y, k)


def _kettle(x: float, y: float, k: float = 1.0, empty: bool = True) -> str:
    """A round kettle; an empty one on the fire glows red at the bottom and puffs dry smoke. 36 wide."""
    c = Canvas()
    if empty:
        for px, py, r in ((-2, -36, 3.6), (3, -44, 4.6), (-1, -54, 5.6)):     # dry smoke
            c.shape(ellipse_d(px, py, r * 1.15, r), P.METAL_PALE, sw=1.2, light=None)
        c.line("M-22,-6 l-5,-2 M22,-6 l5,-2 M-20,-14 l-6,-1 M20,-14 l6,-1", 1.4, P.RED)
    c.tube("M-10,-28 Q0,-42 10,-28", P.CHARCOAL, 2.2, sw=1, shaded=False)
    c.tube("M15,-14 Q24,-16 28,-26", P.TEAL, 3.6, sw=1.3, shaded=False)
    c.shape("M-16,0 Q-20,-24 0,-27 Q20,-24 16,0 Z", P.TEAL, sw=1.9, light=(-2, -2),
            highlight="M-11,-18 Q-13,-10 -11,-4")
    if empty:
        c.add(f'<path d="M-16,0 Q-17,-4 -16.6,-7 H16.6 Q17,-4 16,0 Z" fill="{P.RED}" opacity=".75"/>')
        c.path("M-16,0 Q-20,-24 0,-27 Q20,-24 16,0 Z", "none", 1.9)
    c.shape(ellipse_d(0, -26, 7, 2.2), darken(P.TEAL, 0.85), sw=1.2, light=None)
    c.add(f'<circle cx="0" cy="-29" r="2" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>')
    return _at(c, x, y, k)


def _bee(c: Canvas, x: float, y: float, s: float = 1.0, flip: bool = False) -> None:
    """A round bee, drawn into a canvas at (x, y)."""
    d = -1 if flip else 1
    c.add(f'<ellipse cx="{n(x - 3 * s * d)}" cy="{n(y - 8 * s)}" rx="{n(5 * s)}" ry="{n(3.4 * s)}" '
          f'fill="{P.WHITE}" fill-opacity=".8" stroke="{INK}" stroke-width="1" '
          f'transform="rotate({-30 * d} {n(x - 3 * s * d)} {n(y - 8 * s)})"/>')
    clip = c.shape(ellipse_d(x, y, 8 * s, 6 * s), P.SUN, sw=1.4, light=None, clip=True)
    c.add(f'<g clip-path="url(#{clip})"><path d="M{n(x - 3 * s)},{n(y - 7 * s)} v{n(14 * s)} '
          f'M{n(x + 2 * s)},{n(y - 7 * s)} v{n(14 * s)}" stroke="{INK}" stroke-width="{n(2.4 * s)}"/></g>')
    c.path(ellipse_d(x, y, 8 * s, 6 * s), "none", 1.4)
    c.dot(x + 5 * s * d, y - 1.5 * s, 1.1 * s)
    c.line(f"M{n(x + 6 * s * d)},{n(y - 5 * s)} q{n(2 * s * d)},{n(-4 * s)} {n(4 * s * d)},{n(-4 * s)}", 0.9)


def _tea_table(x: float, y: float, k: float = 1.0) -> str:
    """A round tea table: a teapot, a cup, a polka-dot cloth, and a bee buzzing round the teapot after the
    sugar. 70 wide, 72 tall."""
    c = Canvas()
    c.add(f'<path d="M-30,-62 q8,-10 16,-6 q8,4 12,-4" fill="none" stroke="{INK}" stroke-width="1" '
          f'stroke-dasharray="2 3" stroke-opacity=".7" stroke-linecap="round"/>')
    _bee(c, 4, -72, 0.95, True)
    c.line("M-22,0 L-16,-36 M22,0 L16,-36", 2.8, P.WOOD_DARK)
    c.shape("M-34,-38 H34 L30,-24 Q20,-20 10,-24 Q0,-20 -10,-24 Q-20,-20 -30,-24 Z", P.WHITE, sw=1.8, light=None)
    for i in range(7):
        c.add(f'<circle cx="{-27 + i * 9}" cy="-31" r="2" fill="{P.PINK}"/>')
    c.tube("M-13,-46 q-7,-2 -9,-8", P.ORANGE, 2.2, sw=1, shaded=False)
    c.line("M4,-48 q5,0 4,6", 2)
    c.shape("M-12,-38 Q-16,-52 -4,-54 Q6,-54 4,-38 Z", P.ORANGE, sw=1.6, light=(-1, -1))
    c.add(f'<circle cx="-4" cy="-56" r="2" fill="{P.ORANGE}" stroke="{INK}" stroke-width="1"/>')
    c.add(_cup(14, -38, 0.85, P.BLUE, steam=False))
    return _at(c, x, y, k)


@episode("kettle_cards")
def kettle_cards(s: Strip) -> None:
    """Steps on the washing line, numbered and pegged up out of order: put on, switch on, wait - and «fill» last.
    The agent did them as they hang and now stands puzzled before an empty kettle smoking on the lit
    stove, while the full jug waits by the tap. The cat holds his tea at the edge; a bee buzzes over the tea table."""
    s.indoors()
    k = s.unit
    x0 = s.x(0.0) + 4 * k
    words = [s.word(key) for key in ("put", "switch_on", "wait", "fill")]
    ks = 1.1
    stove_at = 0.62
    x1 = s.x(stove_at) - 32 * k * ks - 12 * k     # the line ends short of the stove and its steam
    size = max(11.2, min(17.0, max(12.0, 13 * k), (x1 - x0) / _card_room(words)))
    y = max(s.h * 0.2 + 3, s.base - 150 * k)
    art, low = _washing_line(x0, x1, y, words, size, k)
    s.put(3, art, (x0 - 4, y - 4, x1 + 4, low), "line")
    s.thing(lambda x, y, k: _sink(x, y, k), 0.14, 76, 66, name="sink")
    s.thing(lambda x, y, k: _stove(x, y, k * ks) + _kettle(x, y - 50 * k * ks, k * ks), stove_at, 64 * ks,
            102 * ks, name="stove")
    s.cast("agent", 0.733, "think", "worry", flip=True, mark="?")
    s.thing(lambda x, y, k: _tea_table(x, y, k * 0.78), 0.8315, 55, 59, name="tea")
    cat = s.cast("cat", 0.95, "present", "smile", flip=True)
    s.in_hand(cat, "present", True, lambda x, y, kk: _cup(x - 4 * kk, y - 1 * kk, kk * 0.8, P.RED))
    if 200 <= s.h < 300:
        x = s.x(0.83)
        cy = s.feet(x) - 120 * k
        if s.free((x - 22 * k, cy - 22 * k, x + 22 * k, cy + 22 * k), 6):
            s.put(4, things.wall_clock(x, cy, k * 0.8), (x - 20 * k, cy - 20 * k, x + 20 * k, cy + 20 * k), "clock")


# ============================================================================ 3. the automatic stove
def _door(x: float, y: float, k: float = 1.0, leaf: bool = False) -> str:
    """A door frame onto a dark corridor (or, with `leaf`, only the open door leaf in front). 66 wide, 168 tall."""
    c = Canvas()
    if leaf:
        c.shape("M-30,0 V-160 L-46,-168 V8 Z", P.WOOD, sw=2, light=(-2, 0))
        c.add(f'<circle cx="-42" cy="-78" r="2.4" fill="{P.SUN}" stroke="{INK}" stroke-width="1"/>')
        return _at(c, x, y, k)
    c.shape("M-34,0 V-166 H34 V0 H28 V-160 H-28 V0 Z", P.WOOD_DARK, sw=2, light=None)
    c.add(f'<path d="M-28,0 V-160 H28 V0 Z" fill="{darken(P.WALL, 0.55)}"/>')
    return _at(c, x, y, k)


def _counter(x: float, y: float, k: float = 1.0) -> str:
    """A kitchen counter with two drawers and a cupboard; its top is 48 up. 100 wide."""
    c = Canvas()
    c.shape("M-48,0 V-44 H48 V0 Z", P.WOOD_LIGHT, sw=2, light=(-2, -1), shade_k=0.88)
    c.line("M-48,-30 H48 M0,-44 V0", 1.3)
    for hx in (-24, 24):
        c.line(f"M{hx - 5},-37 h10", 2.2)
    c.add(f'<circle cx="-6" cy="-14" r="1.6" fill="{INK}"/><circle cx="6" cy="-14" r="1.6" fill="{INK}"/>')
    c.shape(rounded_rect_d(-50, -48, 100, 5, 2), P.TERRACOTTA, sw=1.6, light=None)
    return _at(c, x, y, k)


def _aquarium(x: float, y: float, k: float = 1.0) -> str:
    """A fish tank on a stand, draining through a tube into a spreading puddle, a toy boat sinking with the water;
    the boat's mast top is at (-6, -112). 100 wide, 116 tall."""
    c = Canvas()
    c.line("M-30,0 V-40 M30,0 V-40 M-30,-20 H30", 3, P.WOOD_DARK)
    c.shape(rounded_rect_d(-36, -44, 72, 5, 2), P.WOOD, sw=1.6, light=None)
    c.add(f'<path d="M-32,-46 V-96 H32 V-46 Z" fill="{lighten(P.WATER_LIGHT, 0.55)}"/>')
    c.add(f'<path d="M-32,-46 V-72 H32 V-46 Z" fill="{P.WATER}" opacity=".85"/>')
    c.line("M-32,-90 H32", 1, P.PEN, 0.4)     # where the water used to be
    c.line("M-24,-46 q-4,-10 0,-18 q4,-8 0,-14 M-18,-46 q3,-8 0,-14", 1.6, P.LEAF_DARK)
    c.add(f'<path d="M6,-56 q8,-6 16,0 q-8,6 -16,0 Z M6,-56 l-5,-4 v8 Z" fill="{P.ORANGE}" stroke="{INK}" '
          f'stroke-width="1"/>')
    c.dot(18, -57, 1)
    c.shape("M-18,-72 H6 L2,-66 H-14 Z", P.RED, sw=1.4, light=None)       # the toy boat
    c.line("M-6,-72 V-112", 1.6, P.WOOD_DARK)
    c.shape("M-5,-108 L8,-96 H-5 Z", P.WHITE, sw=1.2, light=None)
    c.path("M-32,-46 V-96 H32 V-46 Z", "none", 2.2)
    c.line("M-28,-90 V-54", 2.4, P.WHITE, 0.5)
    c.tube("M30,-50 H40 Q46,-50 46,-44 V-6", P.CHARCOAL, 3, sw=1.1, shaded=False)   # the drain tube
    c.shape(rounded_rect_d(42, -30, 8, 5, 1.5), P.RED, sw=1, light=None)
    c.add(f'<path d="M46,-2 q-2,3 0,5 q2,-2 0,-5 Z" fill="{P.WATER}" stroke="{INK}" stroke-width=".7"/>')
    return _at(c, x, y, k)


def _puddle(x: float, y: float, k: float = 1.0) -> str:
    """A spreading puddle with a paper boat and a frog enjoying it. 110 wide, 24 tall."""
    c = Canvas()
    c.shape("M-54,0 Q-58,-8 -40,-10 Q-20,-14 0,-10 Q24,-14 44,-8 Q58,-4 50,4 Q30,10 0,8 Q-30,10 -48,6 Z",
            P.WATER, sw=1.6, light=None)
    c.line("M-30,-2 q10,-3 20,0 M10,2 q10,-3 20,0", 1, P.WHITE)
    c.shape("M-30,-2 L-14,-2 L-18,3 H-26 Z", P.CARD, sw=1, light=None)
    c.shape("M-22,-2 L-22,-10 L-17,-2 Z", P.CARD, sw=1, light=None)
    c.add(sets.lily(26, 0, 0.55, frog=True))
    return _at(c, x, y, k)


def _hammer(x: float, y: float, k: float = 1.0, turn: float = -30) -> str:
    """A hammer; the origin is the end of its handle, where it is held."""
    c = Canvas()
    c.tube("M0,0 L0,-26", P.WOOD, 2.6, sw=1, shaded=False)
    c.shape(rounded_rect_d(-9, -32, 18, 8, 2), P.METAL_DARK, sw=1.4, light=None)
    return _at(c, x, y, k, turn=turn)


def _toolbox(x: float, y: float, k: float = 1.0) -> str:
    """An open red toolbox with a saw and a spanner in it. 44 wide, 34 tall."""
    c = Canvas()
    c.shape("M-16,-12 L4,-30 L10,-25 L-10,-8 Z", P.METAL_LIGHT, sw=1.2, light=None)
    c.line("M-14,-12 l2,2 M-10,-15 l2,2 M-6,-19 l2,2 M-2,-22 l2,2", 0.8)
    c.tube("M8,-14 L18,-28", P.METAL_LIGHT, 2.2, sw=1, shaded=False)
    c.add(f'<circle cx="18" cy="-29" r="3.4" fill="none" stroke="{INK}" stroke-width="3.4"/>'
          f'<circle cx="18" cy="-29" r="3.4" fill="none" stroke="{P.METAL_LIGHT}" stroke-width="1.6"/>')
    c.shape("M-22,0 V-16 H22 V0 Z", P.RED, sw=1.8, light=(-2, -1))
    c.line("M-22,-11 H22", 1, opacity=0.5)
    c.line("M-6,-16 Q0,-22 6,-16", 2)
    return _at(c, x, y, k)


def _banner(x0: float, x1: float, y: float, text: str, size: float, seed: int) -> str:
    """A hand-made cloth banner hung on two nails, its letters painted unevenly in three colors; `y` is its top."""
    c = Canvas()
    rnd = random.Random(seed)
    h = size * 1.9
    for nx in (x0 + size * 0.5, x1 - size * 0.5):
        c.line(f"M{n(nx)},{n(y - size * 0.7)} L{n(nx - size * 0.4)},{n(y + 1)} M{n(nx)},{n(y - size * 0.7)} "
               f"L{n(nx + size * 0.4)},{n(y + 1)}", 1.1)
        c.add(f'<circle cx="{n(nx)}" cy="{n(y - size * 0.7)}" r="2" fill="{P.METAL_DARK}" stroke="{INK}"/>')
    mid = (x0 + x1) / 2
    c.shape(f"M{n(x0)},{n(y)} Q{n(mid)},{n(y + size * 0.4)} {n(x1)},{n(y)} L{n(x1 - 2)},{n(y + h)} "
            f"Q{n(mid)},{n(y + h + size * 0.45)} {n(x0 + 2)},{n(y + h)} Z", P.CREAM, sw=1.6, light=None)
    margin = size * 1.2                       # the same cloth left bare at both ends as above and below the letters
    step = (x1 - x0 - 2 * margin) / len(text)
    for i, ch in enumerate(text):
        cx = x0 + margin + step * (i + 0.5)
        t = (cx - x0) / (x1 - x0)
        cy = y + h * 0.5 + size * 0.36 + size * 0.4 * 4 * t * (1 - t) * 0.6 + rnd.uniform(-0.6, 0.6)
        _label(c, cx, cy, ch, size * rnd.uniform(0.96, 1.1), (P.RED, P.BLUE, P.GREEN)[i % 3],
               turn=rnd.uniform(-8, 8))
    return c.render()


def _rope(points: list[tuple[float, float]], pulleys: list[tuple[float, float]], knob: tuple[float, float],
          k: float) -> str:
    """A string from the boat's mast over two pulleys on wall brackets down to the stove's knob, tied at the
    mast and looped round the knob. Over the pulleys it runs on their wheels; past the last one every turn it
    makes is a smooth bend (`curves`)."""
    from .curves import eased_d
    c = Canvas()
    last = points.index(pulleys[-1]) if pulleys[-1] in points else 0
    d = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in points[:last + 1])
    d += " L" + eased_d(points[last:])[1:]
    c.tube(d, P.SAND, max(1.4, 1.6 * k), sw=0.9, shaded=False)
    for px, py in pulleys:
        c.line(f"M{n(px)},{n(py)} V{n(py - 9 * k)}", 2, P.METAL_DARK)
        c.shape(rounded_rect_d(px - 5 * k, py - 11 * k, 10 * k, 3 * k, 1), P.METAL_DARK, sw=1, light=None)
        c.shape(ellipse_d(px, py, 4.6 * k, 4.6 * k), P.METAL_LIGHT, sw=1.3, light=None)
        c.dot(px, py, 1.2 * k + 0.4)
    mx, my = points[0]
    c.shape(ellipse_d(mx, my, 2.2 * k + 0.6, 2.2 * k + 0.6), P.SAND, sw=1, light=None)      # the knot
    kx, ky = knob
    c.add(f'<ellipse cx="{n(kx)}" cy="{n(ky)}" rx="{n(5 * k)}" ry="{n(4 * k)}" fill="none" stroke="{INK}" '
          f'stroke-width="{n(max(1.4, 1.6 * k) + 1.8)}"/><ellipse cx="{n(kx)}" cy="{n(ky)}" rx="{n(5 * k)}" '
          f'ry="{n(4 * k)}" fill="none" stroke="{P.SAND}" stroke-width="{n(max(1.4, 1.6 * k))}"/>')
    return c.render()


@episode("contraption")
def contraption(s: Strip) -> None:
    """The sparrow's automatic stove: as the fish tank drains, the toy boat sinks and its string, run over two
    pulleys, turns the stove's knob. The drain is slow, so the sparrow is about to «fix» it with a hammer while
    the puddle spreads (a frog loves it). The caterpillar has climbed onto the counter out of the water; the
    professor peeks in at the door."""
    s.indoors()
    k = s.unit
    dx = s.x(0.03)
    feet = s.feet(dx)
    s.put(feet - 6, _door(dx, feet, k), (dx - 34 * k, feet - 168 * k, dx + 34 * k, feet), "door", group="door")
    s.cast("professor", 0.03, "think", "surprise", flip=False, group="door", depth=feet - 3)
    s.put(feet + 3, _door(dx, feet, k, leaf=True), None, group="door")
    cx, cy = s.thing(lambda x, y, k: _counter(x, y, k), 0.2, 102, 50, name="counter", group="counter")
    s.actor("caterpillar", cx - 4 * k, cy - 47 * k, "cheer", "surprise", flip=False, tall=s.tall * 0.92,
            group="counter", depth=cy + 0.5)
    ax, ay = s.thing(lambda x, y, k: _aquarium(x, y, k), 0.4, 104, 118, name="tank", group="tank")
    px = ax + 34 * k
    py = s.feet(px, 0.85)
    s.put(py - 1, _puddle(px, py, k), (px - 56 * k, py - 15 * k, px + 56 * k, py + 10 * k), "puddle", group="tank")
    bx = ax + 82 * k
    bird = s.actor("sparrow", bx, s.feet(bx, 0.2), "cheer", "talk", flip=True, tall=s.tall)
    hx, hy = s.hand(bird, "cheer", True, "left")
    s.put(bird.bottom + 1, _hammer(hx, hy + 2 * k, k, -35), None, group=bird.group)
    sx, sy = s.thing(lambda x, y, k: _stove(x, y, k) + things.pot(x, y - 50 * k, k * 0.8), 0.8, 64, 84,
                     name="stove", group="stove")
    tx = (bird.right + sx - 32 * k) / 2
    ty = s.feet(tx, 0.7)
    box = (tx - 24 * k, ty - 34 * k, tx + 24 * k, ty)
    if s.free(box, 4):
        s.put(ty, _toolbox(tx, ty, k), box, "tools")
    s.thing(lambda x, y, k: things.bucket(x, y, k, fill="water"), 0.94, 34, 48, nearer=0.3, name="pail")
    # The string: from the boat's mast up over a pulley, along the wall and down to the stove's knob.
    mast = (ax - 6 * k, ay - 112 * k)
    knob = (sx + 14 * k, sy - 40 * k)
    hook_y = mast[1] - 14 * k
    drop = knob[0] + 26 * k
    pts = [mast, (mast[0], hook_y), (drop, hook_y), (drop, knob[1]), (knob[0] + 4 * k, knob[1])]
    s.put(sy + 1, _rope(pts, [(mast[0], hook_y), (drop, hook_y)], knob, k),
          [(mast[0] - 6 * k, hook_y - 12 * k, mast[0] + 6 * k, hook_y + 6 * k),
           (drop - 6 * k, hook_y - 12 * k, drop + 6 * k, hook_y + 6 * k)], "rope", group="tank")
    x0, x1 = s.x(0.42), s.x(0.82)
    word = s.word("banner")
    for size in (17.0, 15.0, 13.0):            # the biggest painted letters that fit with bare cloth all round
        top = hook_y - 12 * k - size * 3.4
        if s.h >= 220 and top >= s.h * 0.2 and letter_width(word, size) < x1 - x0 - size * 2.6:
            s.put(3, _banner(x0, x1, top + size * 0.7, word, size, s.seed), (x0, top, x1, top + size * 3.2),
                  "banner")
            break


# ============================================================================ 4. the commander
def _desk_room(s: Strip) -> None:
    """A wall and, instead of a floor, the top of a giant writing desk: the cast are as small as desk toys."""
    c = s.back
    s.indoor = True
    sets.wall(c, wall_color(s.look), 0, s.base, W, seed=s.rnd.randrange(99), stripes=s.h >= 150)
    paint = c.gradient([(0, darken(P.WOOD_LIGHT, 0.94)), (1, P.WOOD)], 0, s.base, 0, s.h)
    c.path(f"M-4,{n(s.base)} H{W + 4} V{n(s.h + 4)} H-4 Z", paint, 2.4)
    rnd = random.Random(s.seed)
    for i in range(int(4 + (s.h - s.base) / 14)):
        y = s.base + 8 + i * 13 + rnd.uniform(-3, 3)
        if y > s.h - 4:
            break
        x0 = rnd.uniform(-40, W * 0.5)
        c.line(f"M{n(x0)},{n(y)} q{n(rnd.uniform(60, 140))},{n(rnd.uniform(-5, 5))} "
               f"{n(rnd.uniform(200, 420))},{n(rnd.uniform(-3, 3))}", 1, P.WOOD_DARK, 0.25)
    c.add(f'<path d="M-4,{n(s.base)} H{W + 4}" stroke="{P.WOOD_DARK}" stroke-width="3"/>')


def _game_monitor(x: float, y: float, k: float, title: str, item: str) -> str:
    """A flat monitor showing a game's menu with the pointer on «new game»; a sticky note sits on the frame.
    156 wide, 132 tall; the lettering is sized for the page."""
    c = Canvas()
    c.shape("M-26,0 Q-26,-6 -18,-6 H18 Q26,-6 26,0 Z", P.CHARCOAL, sw=1.8, light=None)
    c.shape("M-6,-6 V-26 H6 V-6 Z", P.CHARCOAL, sw=1.6, light=None)
    c.shape(rounded_rect_d(-76, -130, 152, 106, 6), P.CHARCOAL, sw=2.2, light=(-2, -2), shade_k=0.8)
    glass = c.gradient([(0, P.SCREEN_LIGHT), (1, darken(P.VIOLET, 0.5))], 0, -124, 0, -30)
    c.path(rounded_rect_d(-68, -122, 136, 90, 3), glass, 1.6)
    rnd = random.Random(7)
    for _ in range(14):
        c.dot(rnd.uniform(-64, 64), rnd.uniform(-118, -40), rnd.uniform(0.6, 1.3), P.WHITE)
    big, small = max(15.0, 14 * k) / k, LETTERING / k + 0.5
    fit_label(c, 0, -122 + 8 + big * 0.95, title, big, 124, P.SUN)
    yy = -122 + 8 + big * 1.25 + small * 1.2
    pw = min(128, letter_width(item, small) + small * 2.2)
    ph = small * 1.7
    c.path(rounded_rect_d(-pw / 2, yy - small * 0.36 - ph / 2, pw, ph, 3), P.PINK, 1.2)
    fit_label(c, 0, yy, item, small, pw - small * 1.4, P.WHITE)
    px, py = pw / 2 - small * 0.6, yy - small * 0.2
    c.path(f"M{n(px)},{n(py)} v{n(small * 1.4)} l{n(small * 0.3)},{n(-small * 0.3)} l{n(small * 0.3)},"
           f"{n(small * 0.55)} l{n(small * 0.22)},{n(-small * 0.12)} l{n(-small * 0.28)},{n(-small * 0.52)} "
           f"l{n(small * 0.4)},{n(-small * 0.08)} Z", P.WHITE, 1.1)    # the pointer
    c.line("M-60,-112 Q-62,-90 -60,-72", 3, P.WHITE, 0.25)
    c.add(sets.sticky(64, -118, P.YELLOW_PALE, 12, 0.7))
    c.add(f'<circle cx="62" cy="-28" r="2" fill="{P.GREEN}"/>')
    return _at(c, x, y, k)


def _pc_mouse(x: float, y: float, k: float = 1.0) -> str:
    """A computer mouse as big as a pumpkin. 50 wide, 30 tall; the cable leaves at (25, -10)."""
    c = Canvas()
    c.shape("M-24,0 Q-26,-28 0,-28 Q26,-28 25,-6 Q24,0 18,0 Z", P.METAL_PALE, sw=2, light=(-3, -3),
            highlight="M-16,-18 Q-14,-24 -6,-25")
    c.line("M2,-28 V-12 M2,-12 Q14,-12 25,-10", 1.4)
    c.shape(rounded_rect_d(-0.5, -25, 5, 8, 2.5), P.CHARCOAL, sw=1, light=None)
    c.add(f'<circle cx="18" cy="-5" r="1.6" fill="{P.RED}"/>')
    return _at(c, x, y, k)


def _keyboard_big(x: float, y: float, k: float = 1.0, ladybug: bool = True) -> str:
    """A giant keyboard lying on the desk, a ladybug strolling over its keys. 130 wide, 20 tall."""
    c = Canvas()
    c.shape("M-64,0 L-58,-16 H58 L64,0 Z", P.BEIGE, sw=2, light=(-2, -2), shade_k=0.85)
    for row, (y0, x0, w) in enumerate(((-13, -54, 108), (-9, -57, 114), (-5, -60, 120))):
        for i in range(int(w / 9)):
            fill = P.BEIGE_DARK if (i + row) % 7 else P.RED
            c.add(f'<rect x="{n(x0 + i * 9 + 0.5)}" y="{y0}" width="7.6" height="3.2" rx=".8" fill="{fill}" '
                  f'stroke="{INK}" stroke-width=".7"/>')
    c.add(f'<rect x="-22" y="-1.5" width="44" height="1.2" fill="{INK}" opacity=".4"/>')
    if ladybug:
        c.shape(ellipse_d(30, -17, 4.5, 3.6), P.RED, sw=1, light=None)
        c.line("M30,-20.6 V-13.4", 0.8)
        c.dot(28, -18, 0.8)
        c.dot(32, -16, 0.8)
        c.add(f'<circle cx="34.5" cy="-18" r="1.8" fill="{INK}"/>')
    return _at(c, x, y, k)


def _pencil_cup(x: float, y: float, k: float = 1.0) -> str:
    """A cup of pencils and a ruler. 30 wide, 64 tall."""
    c = Canvas()
    for px, turn, color in ((-6, -12, P.RED), (0, 4, P.BLUE), (6, 14, P.GREEN)):
        c.add(f'<g transform="rotate({turn} {px} -10)"><rect x="{px - 2.5}" y="-58" width="5" height="48" '
              f'fill="{color}" stroke="{INK}" stroke-width="1.2"/>'
              f'<path d="M{px - 2.5},-58 L{px},-64 L{px + 2.5},-58 Z" '
              f'fill="{P.WOOD_PALE}" stroke="{INK}" stroke-width="1"/></g>')
    c.add(f'<g transform="rotate(-6 0 -10)"><rect x="-12" y="-52" width="6" height="42" fill="{P.SUN}" '
          f'stroke="{INK}" stroke-width="1"/></g>')
    c.shape("M-14,0 V-30 H14 V0 Z", P.TEAL, sw=1.8, light=(-2, -1))
    c.line("M-14,-24 H14", 1, opacity=0.5)
    return _at(c, x, y, k)


def _sailor_cap(box: Box, flip: bool) -> str:
    """A sailor's cap with ribbons, sitting on the crown of the sparrow's head (his tuft hidden under it)."""
    hx, hy, ks = _pt(box, 101, 26, flip)
    c = Canvas()
    c.tube("M-30,0 q-12,8 -18,22", P.PEN, 3, sw=1.2, shaded=False)
    c.tube("M-27,2 q-6,10 -8,24", P.PEN, 3, sw=1.2, shaded=False)
    c.shape("M-34,-4 Q-34,-28 0,-28 Q34,-28 34,-4 Z", P.WHITE, sw=2.4, light=(-2, -2))
    c.shape("M-35,-9 H35 V3 H-35 Z", P.PEN, sw=2.2, light=None)
    c.add(f'<circle cx="0" cy="-28" r="5" fill="{P.RED}" stroke="{INK}" stroke-width="1.8"/>')
    return _at(c, hx, hy, ks, mirror=flip)


@episode("commander")
def commander(s: Strip) -> None:
    """«Full speed ahead!» On top of a giant desk the sparrow, in a sailor's cap, stands on a toy block and gives
    orders, while the caterpillar does all the work, pushing the computer mouse towards a screen with a game
    menu; the agent waits by the keyboard for a real task; a ladybug strolls over the keys."""
    _desk_room(s)
    k = s.unit
    s.thing(lambda x, y, k: _pencil_cup(x, y, k), 0.02, 34, 66, name="pencils")
    kc = 1.25
    bx, by = s.thing(lambda x, y, k: things.cube(x, y, k * kc, P.BLUE, s.word("block")), 0.11, 38 * kc, 36 * kc,
                     name="block", group="block")
    rider = s.actor("sparrow", bx, by - 32 * k * kc, "point", "talk", flip=False, tall=s.tall * 0.9,
                    group="block", depth=by + 1)
    s.put(by + 2, _sailor_cap(rider, False), None, group="block")
    worker = s.cast("caterpillar", 0.24, "present", "worry", flip=False, group="crew")
    wx, wy = s.hand(worker, "present", False)
    km = k * 1.4
    mx = wx + 19 * km
    s.put(worker.bottom - 1, _pc_mouse(mx, worker.bottom, km), (mx - 25 * km, worker.bottom - 29 * km,
                                                                mx + 26 * km, worker.bottom), "pcmouse", "crew")
    s.say(rider, s.word("ahead"), shout=True, size=max(LETTERING + 1, 12 * k), prefer="above")
    cable_y = s.base + 4
    s.put(1, sets.cable([(mx + 25 * km, worker.bottom - 10 * km), (mx + 34 * km, cable_y + 2),
                         (s.x(0.6), cable_y), (s.x(0.86), cable_y)], P.CHARCOAL, 3 * k), None)
    s.thing(lambda x, y, k: _keyboard_big(x, y, k), 0.58, 132, 22, nearer=0.8, name="keys", group="agent")
    s.cast("agent", 0.64, "stand", "smile", flip=True, mark="?", group="agent")
    km2 = 0.92
    s.thing(lambda x, y, k: _game_monitor(x, y, k * km2, s.word("game"), s.word("new_game")),
            0.83, 160 * km2, 132 * km2, name="monitor")
    x = s.x(0.985)
    y = s.feet(x, 0.9)
    box = (x - 17 * k, y - 36 * k, x + 17 * k, y)
    if s.free(box, 4):
        s.put(y, sets.mug_at(x, y, 34 * k), box, "mug")


# ============================================================================ 5. every step by hand
def _mini_plane(c: Canvas, x: float, y: float, s: float, turn: float, color: str = P.RED,
                mirror: bool = False) -> None:
    g = Canvas()
    g.shape("M-16,-11 L-12,-11 L-8,-3 Z", darken(color, 0.85), sw=1.1, light=None)       # the tail fin
    g.shape("M-17,-2 Q-17,-5 -12,-5 H8 Q16,-5 16,0 Q16,4 8,4 H-12 Q-17,3 -17,-2 Z", color, sw=1.3, light=None)
    g.shape("M-6,1 L2,1 L-2,10 H-7 Z", darken(color, 0.85), sw=1.1, light=None)          # the near wing
    g.add(f'<path d="M2,-5 Q4,-10 10,-5 Z" fill="{P.LENS}" stroke="{INK}" stroke-width=".8"/>')
    g.line("M17,-6 V6", 1.4, P.METAL_DARK)                                                  # the propeller
    c.add(f'<g transform="translate({n(x)},{n(y)}) rotate({n(turn)}) scale({n(-s if mirror else s)},{n(s)})">'
          f'{g.render()}</g>')


def _console(x: float, y: float, k: float, width: float) -> str:
    """A long console with four little screens: the plane climbs, turns, goes down, and in the last one dives
    nose first trailing smoke. `width` is in page units; the screens' tops are `_console_top` up."""
    c = Canvas()
    w = width / k
    hw = w / 2
    c.shape(f"M{n(-hw)},0 V-30 H{n(hw)} V0 Z", P.METAL_LIGHT, sw=2, light=(-2, -2), shade_k=0.86)
    c.shape(rounded_rect_d(-hw - 3, -34, w + 6, 6, 2), P.CHARCOAL, sw=1.6, light=None)
    for i in range(int(w / 16)):
        color = (P.RED, P.GREEN, P.SUN, P.BLUE)[i % 4]
        c.add(f'<circle cx="{n(-hw + 10 + i * 16)}" cy="-18" r="2.6" fill="{color}" stroke="{INK}" '
              f'stroke-width=".9"/>')
    slot = w / 4
    sw_ = min(slot - 10, 64)
    sh = sw_ * 0.7
    shots = ((-30, 0.0, 0.2), (180, 0.0, 0.0), (30, 0.0, -0.1), (70, 0.12, -0.05))
    for i, (turn, dx, dy) in enumerate(shots):
        cx = -hw + slot * (i + 0.5)
        top = -40 - sh
        c.shape(f"M{n(cx - 4)},-34 V-40 H{n(cx + 4)} V-34 Z", P.CHARCOAL, sw=1, light=None)
        c.shape(rounded_rect_d(cx - sw_ / 2 - 3, top - 3, sw_ + 6, sh + 6, 3), P.CHARCOAL, sw=1.6, light=None)
        sky = c.gradient([(0, P.SKY_DEEP), (1, P.SKY_LOW)], 0, top, 0, top + sh)
        c.path(rounded_rect_d(cx - sw_ / 2, top, sw_, sh, 2), sky, 1)
        c.add(f'<path d="M{n(cx - sw_ / 2 + 1)},{n(top + sh * 0.86)} q{n(sw_ * 0.25)},{n(-sh * 0.12)} '
              f'{n(sw_ * 0.5)},0 t{n(sw_ * 0.5 - 2)},0 V{n(top + sh - 1)} H{n(cx - sw_ / 2 + 1)} Z" '
              f'fill="{P.GRASS}"/>')
        px, py = cx + dx * sw_, top + sh * (0.5 + dy)
        if i == 3:
            c.line(f"M{n(px - sw_ * 0.3)},{n(top + 4)} Q{n(px - sw_ * 0.1)},{n(py - sh * 0.3)} {n(px)},{n(py)}",
                   3, P.METAL_DARK, 0.8)
        _mini_plane(c, px, py, sw_ / 64, turn if i != 1 else 0, mirror=i == 1)
    return _at(c, x, y, k)


def _console_top(width: float, k: float) -> float:
    """How high the console's screens reach, in page units."""
    return (40 + min(width / k / 4 - 10, 64) * 0.7 + 3) * k


def _joystick(x: float, top: float, y: float, k: float) -> str:
    """A joystick on a tall stand standing on the floor at `y`, its red knob at `top` (in the pilot's hand)."""
    c = Canvas()
    c.shape(f"M{n(x - 10 * k)},{n(y)} V{n(y - 8 * k)} H{n(x + 10 * k)} V{n(y)} Z", P.CHARCOAL, sw=1.6,
            light=None)
    c.tube(f"M{n(x)},{n(y - 8 * k)} V{n(top + 18 * k)}", P.METAL_LIGHT, 2.2 * k, sw=1, shaded=False)
    c.shape(rounded_rect_d(x - 9 * k, top + 12 * k, 18 * k, 8 * k, 2 * k), P.CHARCOAL, sw=1.4, light=None)
    c.tube(f"M{n(x)},{n(top + 12 * k)} L{n(x - 3 * k)},{n(top + 3 * k)}", P.CHARCOAL, 2.4 * k, sw=1, shaded=False)
    c.shape(ellipse_d(x - 3 * k, top, 5.5 * k, 5.5 * k), P.RED, sw=1.4, light=(-1, -1))
    return c.render()


def _headphones(box: Box, flip: bool) -> str:
    """Big headphones with a microphone, for the cat: the band over his head, the cups on his cheeks."""
    hx, hy, kc = _pt(box, 140, 100, flip)
    c = Canvas()
    c.tube("M-78,8 Q-84,-92 0,-94 Q84,-92 78,8", P.CHARCOAL, 5, sw=2, shaded=False)
    for ex in (-80, 80):
        c.shape(ellipse_d(ex, 16, 13, 22), P.RED, sw=2.4, light=(-2, -2))
    c.tube("M-84,30 Q-70,64 -30,66", P.CHARCOAL, 2.6, sw=1.2, shaded=False)
    c.shape(ellipse_d(-26, 66, 7, 5), P.CHARCOAL, sw=1.6, light=None)
    return _at(c, hx, hy, kc, mirror=flip)


def _flying_plane(x: float, y: float, k: float) -> str:
    """A paper plane gliding to the left across the room (thrown from the right), a dashed swoosh behind it."""
    trail = (f'<path d="M{n(x - 70 * k)},{n(y + 10 * k)} q{n(22 * k)},{n(-14 * k)} {n(40 * k)},{n(-6 * k)} '
             f'q{n(10 * k)},{n(4 * k)} {n(14 * k)},{n(-2 * k)}" fill="none" stroke="{INK}" stroke-width="1.4" '
             f'stroke-dasharray="4 5" stroke-linecap="round" stroke-opacity=".6"/>')
    return (f'<g transform="translate({n(2 * x)},0) scale(-1,1)">' + trail +
            _paper_plane(x, y + 4 * k, k * 1.3, -6, P.YELLOW_PALE) + "</g>")


@episode("joystick")
def joystick(s: Strip) -> None:
    """Manual control: on four little screens the plane climbs, turns, goes down and finally nosedives - the
    cat in headphones confirms every move with the joystick and is sweating. The sparrow and the caterpillar run
    in, wanting a go, and a paper plane of theirs is already in the air."""
    s.indoors()
    k = s.unit
    x0, x1 = s.x(0.0), s.x(0.47)
    cx, cy = (x0 + x1) / 2, s.feet((x0 + x1) / 2)
    reach = _console_top(x1 - x0, k)
    s.put(cy - 1, _console(cx, cy, k, x1 - x0), (x0 - 3 * k, cy - reach - 1 * k, x1 + 3 * k, cy), "console")
    cat = s.cast("cat", 0.57, "present", "worry", flip=True, group="pilot")
    wx, wy = s.hand(cat, "present", True)
    s.put(cat.bottom + 1, _joystick(wx - 1 * k, wy - 2 * k, cat.bottom - 1, k), None, group="pilot")
    s.put(cat.bottom + 2, _headphones(cat, True), None, group="pilot")
    s.thing(lambda x, y, k: _paper_plane(x, y, k * 1.1, -8), 0.68, 36, 16, nearer=0.85, name="plane")
    bird = s.cast("sparrow", 0.77, "walk", "talk", flip=True)
    s.cast("caterpillar", 0.93, "walk", "smile", flip=True)
    s.say(bird, s.word("let_me"), size=max(LETTERING + 1, 12 * k), prefer="above")
    if s.h >= 220:
        x = s.x(0.36)
        y = max(s.h * 0.2 + 16 * k, cy - reach - 40 * k)
        box = (x - 22 * k, y - 10 * k, x + 70 * k, y + 14 * k)
        if s.free(box, 6):
            s.put(s.h, _flying_plane(x, y, k), box, "flying")


# ============================================================================ 6. the lecture
def _school_desk(x: float, y: float, k: float = 1.0, inkwell: bool = True) -> str:
    """A school desk seen from the front, its lid sloping; the lid's top is 46 up. 66 wide."""
    c = Canvas()
    c.line("M-26,0 V-36 M26,0 V-36", 3.4, P.WOOD_DARK)
    c.shape("M-30,-8 V-40 H30 V-8 Z", P.GREEN, sw=2, light=(-2, -1), shade_k=0.85)
    c.line("M-30,-24 H30", 1, opacity=0.4)
    c.shape("M-33,-40 L-31,-46 H31 L33,-40 Z", P.WOOD, sw=1.8, light=None)
    if inkwell:
        c.shape("M18,-46 V-51 H25 V-46 Z", P.PEN, sw=1, light=None)
        c.line("M23,-51 L28,-58", 1, P.RED)
    return _at(c, x, y, k)


def _lectern(x: float, y: float, k: float = 1.0) -> str:
    """A round lectern with a carafe of water, a glass and an apple on top. 60 wide, 104 tall."""
    c = Canvas()
    c.shape("M-24,0 V-70 H24 V0 Z", P.WOOD, sw=2.2, light=(-3, -2), shade_k=0.82,
            stipple=(10, -68, 14, 66, 16, "right"))
    for lx in (-14, 0, 14):
        c.line(f"M{lx},-64 V-6", 1, P.WOOD_DARK, 0.5)
    c.shape(ellipse_d(0, -72, 30, 6), P.WOOD_LIGHT, sw=2, light=None)
    c.shape(ellipse_d(0, -2, 27, 4), P.WOOD_DARK, sw=1.6, light=None)
    c.add(f'<path d="M-20,-74 Q-26,-82 -22,-90 V-98 H-16 V-90 Q-12,-82 -18,-74 Z" fill="{P.WATER_LIGHT}" '
          f'stroke="{INK}" stroke-width="1.4"/><path d="M-22.5,-74.5 Q-25,-80 -23,-84 H-15 Q-13,-80 -17.5,-74.5 Z" '
          f'fill="{P.WATER}"/>')
    c.add(f'<path d="M-9,-74 L-10,-86 H-3 L-4,-74 Z" fill="{P.LENS}" stroke="{INK}" stroke-width="1.2"/>')
    c.shape("M12,-74 Q6,-76 7,-81 Q8,-86 13,-84 Q18,-86 19,-81 Q20,-76 14,-74 Z", P.RED, sw=1.3, light=(-1, -1))
    c.line("M13,-84 l1,-4", 1.2)
    c.add(f'<path d="M14,-87 q4,-3 6,0 q-3,2 -6,0 Z" fill="{P.LEAF}" stroke="{INK}" stroke-width=".8"/>')
    return _at(c, x, y, k)


def _globe(x: float, y: float, k: float = 1.0) -> str:
    """A school globe on its stand. 44 wide, 66 tall."""
    c = Canvas()
    c.shape("M-14,0 Q-14,-6 0,-6 Q14,-6 14,0 Z", P.WOOD_DARK, sw=1.6, light=None)
    c.line("M0,-6 V-14", 2.6, P.WOOD_DARK)
    clip = c.shape(ellipse_d(0, -38, 20, 20), P.WATER, sw=2, light=(-3, -3), clip=True)
    c.add(f'<g clip-path="url(#{clip})"><path d="M-14,-50 q8,-6 14,2 q-2,8 -10,6 q-6,6 -8,-2 Z M4,-36 '
          f'q10,-4 14,4 q-4,10 -10,10 q-6,-4 -4,-14 Z M-16,-30 q6,2 6,8 q-6,2 -8,-4 Z" fill="{P.GREEN}" '
          f'stroke="{INK}" stroke-width="1"/></g>')
    c.path(ellipse_d(0, -38, 20, 20), "none", 2)
    c.tube("M0,-13 A25,25 0 0 1 0,-63", P.METAL, 2.6, sw=1.1, shaded=False)     # the meridian, on the stand
    c.add(f'<circle cx="0" cy="-63" r="2" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1"/>')
    return _at(c, x, y, k)


def _lesson_board(left: float, top: float, right: float, bottom: float, k: float) -> str:
    """A blackboard with today's lesson in chalk, drawn rather than written: a book, an arrow, the agent's
    head with a light bulb over it."""
    c = Canvas()
    f = 5 * k
    c.shape(rounded_rect_d(left, top, right - left, bottom - top, 3 * k), P.WOOD, sw=2, light=None)
    c.shape(f"M{n(left + f)},{n(top + f)} H{n(right - f)} V{n(bottom - f)} H{n(left + f)} Z", darken(P.FIR, 0.62),
            sw=1.4, light=(-2, -2), shade_k=0.85)
    w, h = right - left - 2 * f, bottom - top - 2 * f
    u = min(w / 130, h / 68)                # the drawing (98 x 49) keeps an even margin of chalkboard all round
    cx, cy = (left + right) / 2 + 1 * u, top + f + h / 2 + 12.5 * u
    chalk = P.WHITE
    g = Canvas()
    g.path("M-50,10 L-50,-8 Q-40,-12 -30,-8 Q-20,-12 -10,-8 V10 Q-20,6 -30,10 Q-40,6 -50,10 Z M-30,-8 V10", "none",
           2, chalk)
    _arrow(g, "M-3,0 H10", (10, 0), (-3, 0), P.SUN, 2, 7, 0.6)
    g.path("M24,-10 H48 V12 H24 Z", "none", 2, chalk)
    g.dot(31, 0, 2.2, chalk)
    g.dot(41, 0, 2.2, chalk)
    g.line("M31,6 Q36,9 41,6 M36,-10 V-16", 1.6, chalk)
    g.path("M32,-24 Q32,-31 36,-31 Q40,-31 40,-24 Q40,-21 38,-20 V-18 H34 V-20 Q32,-21 32,-24 Z", "none", 1.6,
           P.SUN)
    g.line("M36,-34 v-3 M29,-30 l-2,-2 M43,-30 l2,-2", 1.2, P.SUN)
    c.add(f'<g transform="translate({n(cx)},{n(cy)}) scale({n(u)})">{g.render()}</g>')
    c.shape(rounded_rect_d(left + 10 * k, bottom - 1 * k, right - left - 20 * k, 3.5 * k, 1.2 * k), P.WOOD_DARK,
            sw=1.2, light=None)
    c.shape(rounded_rect_d(left + 18 * k, bottom - 3.5 * k, 8 * k, 2.6 * k, 1 * k), P.WHITE, sw=0.8, light=None)
    return c.render()


def _crumpled(x: float, y: float, r: float = 10, seed: int = 0) -> str:
    """A crumpled sheet of paper: a lumpy, many-cornered ball with its folds drawn as facets, never a smooth
    disc (a disc with a line reads as a face)."""
    rnd = random.Random(seed)
    c = Canvas()
    corners = 11
    pts = []
    for i in range(corners):
        a = math.tau * (i + rnd.uniform(-0.25, 0.25)) / corners
        rr = r * rnd.uniform(0.82, 1.08)
        pts.append((math.cos(a) * rr, math.sin(a) * rr * 0.92))
    c.shape("M" + " L".join(f"{n(px)},{n(py)}" for px, py in pts) + " Z", P.WHITE, sw=1.5, light=(-1.6, -1.6),
            shade_k=0.86)
    hub = (r * rnd.uniform(-0.2, 0.1), r * rnd.uniform(-0.2, 0.1))
    folds = ""
    for i in range(0, corners, 3):                # a few folds from a crease in the middle out to the corners
        px, py = pts[i]
        mx, my = (hub[0] + px) / 2 + rnd.uniform(-1.5, 1.5), (hub[1] + py) / 2 + rnd.uniform(-1.5, 1.5)
        folds += f"M{n(hub[0])},{n(hub[1])} L{n(mx)},{n(my)} L{n(px * 0.92)},{n(py * 0.92)} "
    c.line(folds, 0.9, darken(P.METAL_PALE, 0.8))
    return f'<g transform="translate({n(x)},{n(y)})">{c.render()}</g>'


def _paper_bin(x: float, y: float, k: float = 1.0) -> str:
    """A wire waste-paper basket overflowing with crumpled drafts, one rolled away on the floor. 100 wide, 90
    tall at k = 1; the origin under the basket's middle."""
    c = Canvas()
    for i, (bx, by, r) in enumerate(((-13, -66, 11), (7, -69, 12), (-2, -79, 10), (18, -62, 9), (-21, -61, 9))):
        c.add(_crumpled(bx, by, r, i + 3))
    c.shape("M-30,-60 L-22,0 H22 L30,-60 Z", P.METAL, sw=2.3, light=(-3, -2), shade_k=0.85)
    for i in range(7):
        t = i / 6
        c.line(f"M{n(-30 + 60 * t)},-60 L{n(-22 + 44 * t)},0", 1.1, opacity=0.6)
    c.line("M-28,-44 H28 M-26,-24 H26", 1.1, opacity=0.6)
    c.shape(ellipse_d(0, -60, 30, 5), P.METAL_LIGHT, sw=2.1, light=None)
    c.add(_crumpled(44, -9, 9.5, 11))
    return _at(c, x, y, k)


@episode("lecture")
def lecture(s: Strip) -> None:
    """The professor lectures by a round lectern with a carafe and a glass; the cat, the caterpillar and the
    sparrow sit at school desks facing him - the cat thinks, the caterpillar takes notes, the sparrow stands on
    his desk looking innocent, and his paper plane lies on the floor. An overflowing waste-paper basket and a
    globe."""
    s.indoors()
    k = s.unit
    x = s.x(0.06)
    y = s.feet(x, 0.5)
    s.put(y, _school_desk(x, y, k, inkwell=False), (x - 33 * k, y - 46 * k, x + 33 * k, y), "desk1", "row1")
    s.actor("sparrow", x + 2 * k, y - 45 * k, "shrug", "wink", flip=False, tall=s.tall, group="row1",
            depth=y + 1)
    for frac, name, pose, mood in ((0.24, "caterpillar", "write", "smile"), (0.42, "cat", "think", "smile")):
        cx = s.x(frac)
        s.cast(name, frac, pose, mood, flip=False, group=name)
        dy = s.feet(cx, 0.55)
        s.put(dy, _school_desk(cx + 4 * k, dy, k), (cx - 29 * k, dy - 58 * k, cx + 37 * k, dy), f"desk{name}",
              name)
    px = s.x(0.33)
    py = s.feet(px, 1.0)
    s.put(py, _paper_plane(px, py, s.unit, 10), (px - 16 * s.unit, py - 13 * s.unit, px + 16 * s.unit, py), "plane")
    s.thing(lambda x, y, k: _paper_bin(x - 10 * k, y, k * 0.62), 0.55, 66, 56, name="bin")
    s.thing(lambda x, y, k: _globe(x, y, k), 0.66, 46, 66, name="globe")
    left, right = s.x(0.5), s.x(0.72)
    bottom = min(s.feet(s.x(0.55)) - 54 * k, s.feet(s.x(0.66)) - 66 * k) - 10 * k
    top = max(s.h * 0.2, bottom - 70 * k)
    if bottom - top > 34 * k:
        s.put(3, _lesson_board(left, top, right, bottom, k), (left, top, right, bottom + 3 * k), "board")
    s.thing(lambda x, y, k: _lectern(x, y, k * 0.88), 0.785, 54, 92, name="lectern")
    s.cast("professor", 0.91, "explain", "talk", flip=True)



# ============================================================================ 7. dreams in the clouds
def _meadow_sky(s: Strip) -> None:
    """The outdoor setting with neither the sun nor drifting clouds: the stories bring their own (three suns,
    clouds to dream on)."""
    s.dress = False
    c, rnd, look = s.back, s.rnd, s.look
    top, low = sky_colors(look)
    sets.sky(c, top, low, s.base + 10, W)
    near, far = ground_colors(look)
    if s.h >= 190:
        hill = mix(lighten(far, 0.35), low, 0.35) if look.season != "winter" else mix(P.WHITE, low, 0.4)
        sets.hills(c, s.base + 6, W, (hill, lighten(near, 0.2)), seed=rnd.randrange(99))
    sets.meadow(c, s.base, s.h, W, seed=rnd.randrange(99), color=near, near=far)
    if look.season == "winter":
        s._snow()
    else:
        sets.grass_tufts(c, (0, s.base + 6, W, s.h), int(20 + s.h / 6), seed=rnd.randrange(99))


def _balloons(x: float, y: float, k: float = 1.0) -> str:
    """Three toy balloons whose strings meet at (x, y). 50 wide, 60 tall."""
    c = Canvas()
    for bx, by, color in ((-14, -42, P.RED), (12, -46, P.SUN), (0, -54, P.BLUE)):
        c.line(f"M0,0 Q{bx * 0.4},{by * 0.5} {bx},{by + 12}", 0.9)
        c.shape(ellipse_d(bx, by, 9, 11), color, sw=1.6, light=(-2, -2),
                highlight=f"M{bx - 5},{by - 4} Q{bx - 5},{by - 8} {bx - 2},{by - 9}")
        c.path(f"M{bx - 2},{by + 13} L{bx},{by + 10} L{bx + 2},{by + 13} Z", color, 1)
    return _at(c, x, y, k)


def _thought(cx: float, cy: float, w: float, h: float, start: tuple[float, float],
             k: float) -> tuple[str, list[tuple]]:
    """A thought cloud centred at (cx, cy) and a trail of three little bubbles growing from `start` (just by the
    dreamer's head) to the cloud's edge. Returns the drawing and the boxes of the cloud and of the trail."""
    c = Canvas()
    sx, sy = start
    ang = math.atan2(sy - cy, sx - cx)
    ex, ey = cx + math.cos(ang) * w * 0.5, cy + math.sin(ang) * h * 0.5      # where the trail meets the cloud
    boxes = []
    for i, t in enumerate((0.0, 0.42, 0.78)):
        r = (1.8 + i * 1.5) * k + 0.6
        px, py = sx + (ex - sx) * t, sy + (ey - sy) * t
        c.path(ellipse_d(px, py, r * 1.25, r), P.WHITE, 1.4)
        boxes.append((px - r * 1.3, py - r, px + r * 1.3, py + r))
    bumps = 11
    pts = []
    for i in range(bumps):
        a0 = math.tau * i / bumps
        a1 = math.tau * (i + 1) / bumps
        x1, y1 = cx + math.cos(a1) * w / 2, cy + math.sin(a1) * h / 2
        mx = cx + math.cos((a0 + a1) / 2) * w / 2 * 1.16
        my = cy + math.sin((a0 + a1) / 2) * h / 2 * 1.2
        pts.append(f"Q{n(mx)},{n(my)} {n(x1)},{n(y1)}")
    c.shape(f"M{n(cx + w / 2)},{n(cy)} " + " ".join(pts) + " Z", P.WHITE, sw=1.8, light=(-2, -2), shade_k=0.94)
    boxes.append((cx - w * 0.58, cy - h * 0.6, cx + w * 0.58, cy + h * 0.6))
    return c.render(), boxes


def _dream_plane(x: float, y: float, k: float, word: str) -> str:
    """A smiling plane answering in sparrow; the word in its little bubble is left out when it would be too
    small to read."""
    c = Canvas()
    _mini_plane(c, -12 if word else 0, 6, 1.6, -8, P.BLUE)
    c.add(f'<circle cx="{-2 if word else 10}" cy="2" r="1.2" fill="{INK}"/>')
    if word:
        c.line("M-4,7 q3,2 6,-1", 1)
        size = LETTERING / k + 0.3
        w = letter_width(word, size) + size * 2
        c.path(f"M10,-{n(size * 0.6)} Q10,-{n(size * 1.6)} {n(10 + w / 2)},-{n(size * 1.6)} Q{n(10 + w)},"
               f"-{n(size * 1.6)} {n(10 + w)},-{n(size * 0.6)} Q{n(10 + w)},{n(size * 0.4)} {n(10 + w / 2)},"
               f"{n(size * 0.4)} L12,6 L14,{n(size * 0.2)} Q10,0 10,-{n(size * 0.6)} Z", P.YELLOW_PALE, 1.2)
        fit_label(c, 10 + w / 2, -size * 0.25, word, size, w - size * 1.4, style="talk")
    return _at(c, x, y, k)


def _dream_stove(x: float, y: float, k: float, word: str) -> str:
    """A stove in a chef's hat, pies flying out of it, and its boast written over it (if it can be read)."""
    c = Canvas()
    c.add(_stove(0, 0, 0.7, lit=False))
    c.shape("M-7,-36 Q-12,-43 -6,-44 Q-4,-50 2,-47 Q8,-50 9,-43 Q13,-41 7,-36 Z", P.WHITE, sw=1.2, light=None)
    for px, py, turn in ((26, -16, -10), (34, -30, 14), (-28, -24, 8)):
        c.add(f'<g transform="translate({px},{py}) rotate({turn})"><path d="M-7,0 Q-7,-7 0,-7 Q7,-7 7,0 Z" '
              f'fill="{P.AMBER}" stroke="{INK}" stroke-width="1"/><path d="M-4,-3 l2,-2 M0,-3 l2,-2 M4,-3 l-1,-2" '
              f'stroke="{INK}" stroke-width=".8"/></g>')
    if word:
        size = (P.SIGN_BALLOON_FROM + 0.4) / min(k, 1.0)      # balloon letters, both as drawn and on the page
        fit_label(c, 0, -52, word, size, 100, P.RED)
    return _at(c, x, y, k)


def _floating_cloud(x: float, y: float, k: float = 1.0) -> str:
    """A fat cloud to stand on; the origin is the middle of its flat top. 90 wide, 30 tall."""
    c = Canvas()
    c.shape("M-44,0 Q-52,10 -40,16 Q-34,28 -16,22 Q-4,32 10,22 Q28,30 36,18 Q50,14 44,0 Q30,-8 0,-6 "
            "Q-30,-8 -44,0 Z", P.WHITE, sw=2, light=(-2, -3), shade_k=0.9)
    return _at(c, x, y, k)


def _book(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.shape("M0,-2 L-14,-6 V-22 L0,-18 Z", P.CARD, sw=1.3, light=None)
    c.shape("M0,-2 L14,-6 V-22 L0,-18 Z", P.CARD, sw=1.3, light=None)
    c.path("M0,-1 L-16,-5 V-8 M0,-1 L16,-5 V-8", "none", 1.6, P.RED)
    c.line("M-11,-15 l8,2 M-11,-11 l8,2 M3,-13 l8,-2 M3,-9 l8,-2", 0.8, opacity=0.6)
    return _at(c, x, y, k)


@episode("dream_clouds")
def dream_clouds(s: Strip) -> None:
    """Dreams of a machine that understands plain words: the sparrow, lifted by toy balloons, dreams of a plane
    that understands sparrow; the caterpillar, on a cloud of her own, dreams of a stove that knows a hundred pie
    recipes. The cat reads his book with his back to them both. Birds fly by; a snail is in no hurry."""
    _meadow_sky(s)
    k = s.unit
    top5 = s.h * 0.2
    words = k >= 0.9           # the words in the dreams only where they can be read
    cat = s.cast("cat", 0.05, "read", "smile", flip=True)
    s.held(cat, "read", True, lambda x, y, kk: _book(x, y, kk * 0.9))
    # The sparrow under his balloons, lifted just as high as the balloons allow.
    bx = s.x(0.22)
    ka = s.tall / PROFESSOR_HEIGHT * module("sparrow").SCENE_SCALE
    kb = k * 0.85
    lift = s.base - max(18 * k, s.base * (0.2 if s.h < 400 else 0.36))
    feet = max(lift, top5 + 2 + 60 * kb + 126 * ka)
    bird = _float(s, "sparrow", bx, feet, "cheer", "smile", flip=False, group="sparrow")
    tx, ty = s.hand(bird, "cheer", False, "right")
    s.put(feet + 1, _balloons(tx, ty, kb), (tx - 25 * kb, ty - 66 * kb, tx + 25 * kb, ty), "balloons", "sparrow")
    w, h = 150 * k, 74 * k
    cx = max(tx + 25 * kb + w / 2 + 14 * k, s.x(0.42))
    cy = max(top5 + h * 0.6 + 2, min(bird.top, ty - 30 * k))
    head = (bird.right - 4 * ka, bird.top + 14 * ka)
    art, boxes = _thought(cx, cy, w, h, head, k)
    s.put(5, art + _dream_plane(cx - (14 if words else 0) * k, cy + 4 * k, k, s.word("chirp") if words else ""),
          boxes, "dream1", "sparrow")
    # The caterpillar on her cloud.
    fx = s.x(0.7)
    top = s.base - max(14 * k, s.base * (0.16 if s.h < 400 else 0.3))
    s.put(top + 1, _floating_cloud(fx, top, k), (fx - 50 * k, top - 8 * k, fx + 46 * k, top + 26 * k), "cloud",
          "caterpillar")
    she = _float(s, "caterpillar", fx - 6 * k, top + 1, "think", "smile", flip=True, group="caterpillar", depth=top)
    w2, h2 = 124 * k, 86 * k
    cx2 = min(s.hi - w2 * 0.58 - 4, she.right + w2 / 2 + 12 * k)
    cy2 = max(top5 + h2 * 0.6 + 2, she.top - 4 * k)
    hk = (she.bottom - she.top) / 254
    art, boxes = _thought(cx2, cy2, w2, h2, ((she.left + she.right) / 2 + 2 * hk, she.top - 6 * hk), k)
    s.put(5, art + _dream_stove(cx2, cy2 + 28 * k, k, s.word("recipes") if words else ""), boxes, "dream2",
          "caterpillar")
    s.thing(lambda x, y, k: sets.snail(x, y, k * 0.7, mirror=True), 0.86, 46, 26, nearer=0.8, name="snail")
    s.thing(lambda x, y, k: props.mushroom(x, y, k * 0.8) + props.mushroom(x + 14 * k, y, k * 0.55, P.AMBER),
            0.34, 40, 26, nearer=0.75, name="shrooms")
    for i in range(2):
        x = bird.left - (16 + i * 22) * k
        y = bird.top + (10 + i * 12) * k
        box = (x - 10 * k, y - 8 * k, x + 10 * k, y + 2 * k)
        if box[1] > top5 and s.free(box, 4):
            s.put(4, props.bird(x, y, k * 0.9), box, f"bird{i}")


# ============================================================================ 8. the wizard and the language
def _three_suns(c: Canvas, x0: float, x1: float, y_low: float, y_high: float, r: float) -> None:
    """The sun's path over three days: three little suns along dotted arcs."""
    xs = [x0 + (x1 - x0) * t for t in (0.0, 0.5, 1.0)]
    for i, x in enumerate(xs):
        y = y_high if i == 1 else y_low
        if i < 2:
            nx = xs[i + 1]
            ny = y_low if i == 1 else y_high
            c.add(f'<path d="M{n(x + r * 1.4)},{n(y)} Q{n((x + nx) / 2)},{n(min(y, ny) - r * 1.6)} '
                  f'{n(nx - r * 1.4)},{n(ny)}" fill="none" stroke="{P.AMBER}" stroke-width="1.6" '
                  f'stroke-dasharray="3 4"/>')
        c.add(props.sun(x, y, r / 24))


def _wizard_hat(box: Box, flip: bool) -> tuple[str, tuple]:
    """A wizard's pointed starry hat pulled onto the professor's crown, its brim round his head just above the
    forehead lines; returns the drawing and its box. Drawn in the professor's own canvas units."""
    ox, oy, kk = _pt(box, 0, 0, flip)
    robe = P.VIOLET
    c = Canvas()
    c.shape("M72,40 Q100,14 110,-30 Q116,-52 140,-62 Q128,-42 130,-14 Q134,16 162,40 Z", robe, sw=2.2,
            light=(-3, -2))
    for sx, sy in ((112, 8), (130, 26), (96, 28), (122, -24)):
        c.add(f'<path d="M{sx},{sy - 4} l1.4,2.8 l3.2,.5 l-2.4,2.2 l.6,3.2 l-2.8,-1.5 l-2.8,1.5 l.6,-3.2 '
              f'l-2.4,-2.2 l3.2,-.5 Z" fill="{P.SUN}" stroke="{INK}" stroke-width=".8"/>')
    c.shape(ellipse_d(117, 40, 58, 9), darken(robe, 0.85), sw=2, light=None)
    left, right = (ox - 176 * kk, ox - 58 * kk) if flip else (ox + 58 * kk, ox + 176 * kk)
    return _at(c, ox, oy, kk, mirror=flip), (left, oy - 64 * kk, right, oy + 50 * kk)


def _tower(x: float, y: float, k: float) -> str:
    """The wizard's round stone tower with a red roof and a flag, an arched window and a door on the right
    (the tape comes out of it at (16, -12)). 84 wide, 232 tall."""
    c = Canvas()
    body = "M-30,2 V-160 H30 V2 Q0,7 -30,2 Z"         # a round tower: its foot curves towards us
    clip = c.shape(body, P.STONE, sw=0, light=(-3, -2), shade_k=0.84, stipple=(10, -158, 20, 156, 30, "right"))
    rnd = random.Random(3)
    stones = ""
    for row in range(9):                          # courses of stones, staggered, kept inside the wall
        yy = -6 - row * 18
        for col in range(-1, 4):
            bx = -30 + col * 17 + (8.5 if row % 2 else 0) + rnd.uniform(-1.5, 1.5)
            if -152 < yy < -112 and -26 < bx < 4 or -36 < yy < 4 and 0 < bx < 30:
                continue                          # the window and the door
            stones += f'<path d="{rounded_rect_d(bx, yy - 9, 14, 9, 2.5)}" fill="none"/>'
    c.add(f'<g clip-path="url(#{clip})" stroke="{darken(P.STONE, 0.75)}" stroke-width="1">{stones}</g>')
    c.path(body, "none", 2.2)
    c.shape("M-40,-158 L0,-220 L40,-158 Z", P.RED, sw=2.2, light=(-3, -2))
    c.line("M0,-220 V-232", 1.8)
    c.shape("M0,-232 L13,-228 L0,-224 Z", P.SUN, sw=1.1, light=None)
    c.shape("M6,0 V-30 Q16,-40 26,-30 V0 Z", P.WOOD_DARK, sw=1.8, light=None)
    c.add(f'<circle cx="21" cy="-14" r="1.6" fill="{P.SUN}"/>')
    c.add(f'<path d="M-22,-122 V-142 Q-11,-156 0,-142 V-122 Z" fill="{P.DARK_BROWN}" stroke="{INK}" '
          f'stroke-width="2"/>')
    c.line("M-11,-150 V-122 M-22,-134 H0", 1.6, P.WOOD)
    c.shape(rounded_rect_d(-26, -124, 30, 5, 2), P.WOOD_LIGHT, sw=1.6, light=None)
    return _at(c, x, y, k)


def _smooth(points: list[tuple[float, float]], steps: int = 8) -> list[tuple[float, float]]:
    """A Catmull-Rom curve through the points, as a polyline fine enough to look smooth."""
    pts = [points[0], *points, points[-1]]
    out = [points[0]]
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for j in range(1, steps + 1):
            t = j / steps
            out.append(tuple(0.5 * (2 * p1[a] + (-p0[a] + p2[a]) * t
                                    + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t * t
                                    + (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * t ** 3) for a in (0, 1)))
    return out


def _ribbon(points: list[tuple[float, float]], width: float, chars: str, split: int) -> str:
    """A paper tape along a path; the first `split` characters printed on it are bits, the rest a word."""
    c = Canvas()
    lefts, rights = [], []
    for i, (px, py) in enumerate(points):
        qx, qy = points[min(i + 1, len(points) - 1)]
        ox, oy = points[max(i - 1, 0)]
        dx, dy = qx - ox, qy - oy
        length = math.hypot(dx, dy) or 1
        nx, ny = -dy / length, dx / length
        lefts.append((px + nx * width / 2, py + ny * width / 2))
        rights.append((px - nx * width / 2, py - ny * width / 2))
    d = "M" + " L".join(f"{n(a)},{n(b)}" for a, b in lefts) + " L" + " L".join(
        f"{n(a)},{n(b)}" for a, b in reversed(rights)) + " Z"
    c.shape(d, P.CARD, sw=1.4, light=None)
    seg = [math.hypot(points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1])
           for i in range(len(points) - 1)]
    total = sum(seg)
    for j, ch in enumerate(chars):
        t = (0.06 + 0.88 * (j + 0.5) / len(chars)) * total
        i = 0
        while i < len(seg) - 1 and t > seg[i]:
            t -= seg[i]
            i += 1
        f = t / seg[i]
        x = points[i][0] + (points[i + 1][0] - points[i][0]) * f
        y = points[i][1] + (points[i + 1][1] - points[i][1]) * f
        ang = math.atan2(points[i + 1][1] - points[i][1], points[i + 1][0] - points[i][0])
        size = width * 0.64
        drop = size * 0.32                  # half a capital: the baseline sits that far below the tape's middle
        bx, by = x - math.sin(ang) * drop, y + math.cos(ang) * drop
        bit = j < split
        _label(c, bx, by, ch, size, P.METAL_DARK if bit else P.RED, turn=math.degrees(ang))
    return c.render()


@episode("wizard")
def wizard(s: Strip) -> None:
    """From the fairy tale, with the professor as the wizard: in a starry hat, by the cactus he sat thinking by
    for three days (three suns cross the sky), he throws up his hands with «Eureka!». Out of his tower's door
    runs a tape whose noughts and ones turn into a word, and the agent at its end reads it happily."""
    _meadow_sky(s)
    k = s.unit
    top5 = s.h * 0.2
    s.thing(lambda x, y, k: things.cactus(x, y, k * 1.2), 0.03, 28, 52, name="cactus")
    prof = s.cast("professor", 0.15, "welcome", "talk", flip=False, group="wizard", size=0.86)
    hat, hat_box = _wizard_hat(prof, False)
    s.put(prof.bottom + 1, hat, hat_box, "hat", "wizard")
    feet = s.feet(s.x(0.5))
    kt = min(k, (feet - top5) / 232)
    tx = s.x(0.47)
    s.put(feet - 1, _tower(tx, feet, kt), (tx - 42 * kt, feet - 234 * kt, tx + 32 * kt, feet), "tower", "tower")
    s.say(prof, s.word("eureka"), shout=True, size=max(LETTERING + 2, 13 * k), prefer="right")
    # The tape from the door to the agent.
    agent = s.cast("agent", 0.92, "read", "smile", flip=True, mark="ok", group="tower")
    hx, hy = s.hand(agent, "read", True)
    door = (tx + 16 * kt, feet - 12 * kt)
    span = hx - door[0]
    rw = max(15.0, 11 * k)
    pts = [door, (door[0] + span * 0.12, feet + 4 * k), (door[0] + span * 0.4, feet + 2 * k),
           (door[0] + span * 0.7, feet + 7 * k), (hx - 10 * k, hy + 8 * k), (hx, hy)]
    bits = s.word("bits")
    smooth = _smooth(pts)
    s.put(feet + 6, _ribbon(smooth, rw, bits + s.word("text"), len(bits)), strip_boxes(pts, rw), "tape", "tower")
    # Three suns over the meadow between the tower and the agent: three days of thinking.
    r = max(7.0, min(14 * k, s.base * 0.08))
    x0, x1 = tx + 40 * kt + r * 2, min(agent.left - r * 2, s.x(0.84))
    y_high = top5 + r * 2
    y_low = min(y_high + r * 2.4, s.base - r * 2.6)
    if x1 - x0 > r * 7 and y_low - y_high > r:
        sc = Canvas()
        _three_suns(sc, x0, x1, y_low, y_high, r)
        box = (x0 - r * 1.8, y_high - r * 1.8, x1 + r * 1.8, y_low + r * 1.8)
        if s.free(box, 4):
            s.put(2, sc.render(), box, "suns")
    bx = s.x(0.32)
    by = s.feet(bx) - 46 * k
    if by - 10 * k > top5 and s.free((bx - 14 * k, by - 12 * k, bx + 14 * k, by + 10 * k), 6):
        s.put(by, props.butterfly(bx, by, k * 0.9, P.PINK), (bx - 14 * k, by - 12 * k, bx + 14 * k, by + 10 * k),
              "fly")


# ============================================================================ 9. to the Moon by hand
def _space(s: Strip) -> None:
    """The night sky in the chapter's color over the grey cratered ground of the Moon, stars all over it."""
    c, rnd = s.back, s.rnd
    top, low = night_sky(s.look)
    sky = c.gradient([(0, top), (0.22, mix(top, low, 0.3)), (0.6, mix(top, low, 0.82)), (1, low)],
                     0, 0, 0, s.base)
    c.add(f'<rect x="-4" y="-4" width="{W + 8}" height="{n(s.base + 14)}" fill="{sky}"/>')
    sets.stars(c, (10, s.base * 0.3, W - 10, s.base - 4), int(24 + s.base / 6), seed=rnd.randrange(99))
    rock = mix(P.METAL_LIGHT, s.look.accent, 0.08)
    ground = c.gradient([(0, rock), (1, darken(rock, 0.8))], 0, s.base, 0, s.h)
    c.path(f"M-4,{n(s.base + 6)} Q{W * 0.25},{n(s.base - 6)} {W * 0.5},{n(s.base + 2)} Q{W * 0.75},"
           f"{n(s.base + 10)} {W + 4},{n(s.base - 2)} V{n(s.h + 4)} H-4 Z", ground, 2.2)
    for _ in range(int(8 + s.h / 40)):
        x, y = rnd.uniform(10, W - 10), rnd.uniform(s.base + 14, s.h - 6)
        r = rnd.uniform(6, 16) * (0.6 + (y - s.base) / (s.h - s.base + 1) * 0.6)
        c.add(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(r)}" ry="{n(r * 0.32)}" fill="{darken(rock, 0.78)}" '
              f'stroke="{INK}" stroke-width="1.2"/><path d="M{n(x - r * 0.8)},{n(y - r * 0.12)} '
              f'q{n(r * 0.8)},{n(r * 0.3)} {n(r * 1.6)},0" stroke="{P.METAL_PALE}" stroke-width="1.4" fill="none"/>')


def _earth(x: float, y: float, r: float) -> str:
    c = Canvas()
    clip = c.shape(ellipse_d(0, 0, r, r), P.BLUE, sw=1.8, light=(-r * 0.15, -r * 0.15), clip=True)
    c.add(f'<g clip-path="url(#{clip})" transform="scale({n(r / 20)})"><path d="M-14,-10 q8,-8 14,0 q-2,8 -10,6 '
          f'q-6,6 -8,-2 Z M4,2 q10,-4 14,4 q-4,10 -10,10 q-6,-4 -4,-14 Z" fill="{P.GREEN}"/>'
          f'<path d="M-16,8 q6,-4 12,0" stroke="{P.WHITE}" stroke-width="3" fill="none" opacity=".8"/></g>')
    return _at(c, x, y)


def _calculator(x: float, y: float, k: float) -> str:
    """A big pocket calculator held by its left edge at (x, y); 24 wide, 32 tall at k = 1. Its display only
    glows: a reading would be too small to read in a footer."""
    c = Canvas()
    c.shape(rounded_rect_d(-2, -16, 24, 32, 3), P.BEIGE, sw=1.8, light=(-2, -2))
    c.path(rounded_rect_d(1, -13, 18, 8, 1.5), P.SCREEN_TEXT, 1.2)
    c.line("M4,-9 h4 M10,-9 h3 M15,-9 h2", 1.4, P.SCREEN, 0.8)
    for row in range(4):
        for col in range(3):
            color = P.RED if (row, col) == (3, 2) else P.METAL_LIGHT
            c.add(f'<rect x="{n(1.6 + col * 6.2)}" y="{n(-2 + row * 4.4)}" width="4.6" height="3.2" rx="1" '
                  f'fill="{color}" stroke="{INK}" stroke-width=".7"/>')
    return _at(c, x, y, k)


def _rocket(x: float, y: float, k: float) -> str:
    """A homemade rocket of a barrel, fins and sticking plaster, flying right. The origin is the middle of its
    flat top, where a rider stands; 150 long, 44 tall."""
    c = Canvas()
    c.add(f'<path d="M-52,8 L-80,0 L-72,10 L-92,14 L-72,18 L-80,28 L-52,20 Z" fill="{P.ORANGE}" stroke="{INK}" '
          f'stroke-width="1.6"/><path d="M-52,10 L-68,8 L-62,14 L-68,20 L-52,18 Z" fill="{P.SUN}"/>')
    c.shape("M-52,0 H30 Q50,0 58,14 Q50,28 30,28 H-52 Z", P.RED, sw=2.2, light=(-2, -3), shade_k=0.82,
            highlight="M-40,5 H24")
    c.line("M-20,0 V28 M10,0 V28", 1.2, opacity=0.5)
    c.shape("M-50,0 L-64,-14 H-48 L-36,0 Z", P.BLUE, sw=1.6, light=None)
    c.shape("M-50,28 L-64,42 H-48 L-36,28 Z", P.BLUE, sw=1.6, light=None)
    for turn in (30, -30):                                                          # sticking plaster
        c.add(f'<rect x="-34" y="11" width="18" height="5" rx="2" fill="{P.WOOD_PALE}" stroke="{INK}" '
              f'stroke-width="1" transform="rotate({turn} -25 13.5)"/>')
    c.add(f'<circle cx="44" cy="14" r="5" fill="{P.LENS}" stroke="{INK}" stroke-width="1.4"/>')
    for rx in (-44, -6, 22):
        c.dot(rx, 4, 1, INK)
    return _at(c, x, y, k)


def _sheet_width(text: str) -> float:
    """A sheet is as wide as its sum and an even margin on both sides, never narrower than 32."""
    return max(32.0, letter_width(text, 9) + 14) if text else 32.0


def _sheet(x: float, y: float, k: float, text: str, turn: float) -> str:
    """A loose sheet with a sum on it, blown off to the left, three motion lines on its right; 26 tall."""
    c = Canvas()
    h = _sheet_width(text) / 2
    c.line(f"M{n(h + 4)},-6 h10 M{n(h + 6)},0 h12 M{n(h + 4)},6 h9", 1.2, INK, 0.6)
    c.shape(f"M{n(-h)},-13 H{n(h - 2)} L{n(h)},-11 V13 H{n(-h)} Z", P.CARD, sw=1.3, light=None)
    if text:
        fit_label(c, 0, 0, text, 9, 2 * h - 14, P.PEN)
        c.line(f"M{n(-h + 7)},5.5 h{n(2 * h - 16)} M{n(-h + 7)},8.5 h{n(h)}", 0.8, opacity=0.4)
    else:
        c.line("M-11,-6 h18 M-11,-1 h22 M-11,4 h14", 1.1, P.PEN, 0.7)
    return _at(c, x, y, k, turn=turn)


def _saucer(x: float, y: float, k: float = 1.0) -> str:
    """A flying saucer with a flat deck to stand on and a ring of lights; the origin is the middle of the deck.
    124 wide, 22 tall."""
    c = Canvas()
    c.shape("M-62,2 Q-60,-4 -46,-5 H46 Q60,-4 62,2 Q42,18 0,20 Q-42,18 -62,2 Z", P.METAL_LIGHT, sw=2.2,
            light=(-3, -3), highlight="M-46,-1 Q-20,-3 10,-2")
    c.shape(ellipse_d(0, -2, 44, 4.6), P.METAL_PALE, sw=1.6, light=None)
    for i, color in enumerate((P.RED, P.SUN, P.GREEN, P.SUN, P.RED)):
        c.add(f'<circle cx="{-36 + i * 18}" cy="{9 - abs(i - 2) * 1.6}" r="3" fill="{color}" stroke="{INK}" '
              f'stroke-width="1.2"/>')
    return _at(c, x, y, k)


@episode("moon_calculator")
def moon_calculator(s: Strip) -> None:
    """To the Moon by hand: the sparrow stands on a homemade rocket working out the course on a calculator, the
    rocket bangs and sheets of sums fly off behind him; beside him the agent glides along on a flying saucer,
    calmly holding a cup of tea. The Earth looks on."""
    _space(s)
    s.big = False                  # nothing grows on the Moon: no windmills on its horizon
    s.dress = False                # no sun or clouds in space
    k = s.unit
    top5 = s.h * 0.2
    # The rocket and its rider.
    kb = 0.9
    ka = s.tall * kb / PROFESSOR_HEIGHT * module("sparrow").SCENE_SCALE
    rx = s.x(0.3)
    ry = max(top5 + 190 * ka + 6, min(s.base * 0.6, s.base - 46 * k))
    s.put(ry + 20, _rocket(rx, ry, k), (rx - 94 * k, ry - 16 * k, rx + 60 * k, ry + 44 * k), "rocket", "rocket")
    bird = _float(s, "sparrow", rx - 16 * k, ry + 1, "point", "worry", flip=False, group="rocket", size=kb,
                  depth=ry + 30)
    hx, hy = s.hand(bird, "point", False, "right")
    kc = max(k * 1.2, 0.9)
    s.put(ry + 29, _calculator(hx - 1, hy, kc),
          (hx - 3 * kc, hy - 17 * kc, hx + 23 * kc, hy + 17 * kc), "calc", "rocket")
    r = max(28.5, 30 * k)          # its word big enough for balloon letters
    bx, by = rx - 92 * k - r * 0.75, ry + 14 * k
    s.put(s.h, things.burst(bx, by, r, s.word("bang")), (bx - r, by - r * 0.8, bx + r, by + r * 0.8), "bang",
          "rocket")
    # Sheets of sums blown off behind.
    text = 9 * k * 1.1 >= LETTERING
    spots = ((-40, -40, -14), (-120, -36, 10), (-150, 34, -20), (-60, 58, 8))
    for i, (dx, dy, turn) in enumerate(spots):
        x, y = rx + dx * k, ry + dy * k
        words = s.word(f"sum{i % 3 + 1}") if text else ""
        half = _sheet_width(words) / 2 * 1.1
        box = (x - (half + 2) * k, y - 15 * k, x + (half + 20) * k, y + 15 * k)
        if box[0] > s.lo - 10 and box[3] < s.base and box[1] > top5 and s.free(box, 3):
            s.put(5, _sheet(x, y, k * 1.1, words, turn), box, f"sheet{i}")
    # The saucer and its calm passenger.
    ks = s.tall / PROFESSOR_HEIGHT * module("agent").SCENE_SCALE
    sx = s.x(0.68)
    sy = max(top5 + 261 * ks + 6, min(s.base * 0.62, s.base - 26 * k))
    s.put(sy + 1, _saucer(sx, sy, k), (sx - 62 * k, sy - 6 * k, sx + 62 * k, sy + 20 * k), "saucer", "saucer")
    pilot = _float(s, "agent", sx, sy - 1 * k, "present", "smile", flip=False, group="saucer", depth=sy)
    s.in_hand(pilot, "present", False, lambda x, y, kk: _cup(x + 3 * kk, y - 1 * kk, kk * 0.8, P.BLUE))
    # The Earth.
    er = max(12.0, min(24 * k, s.base * 0.15))
    ex, ey = s.x(0.92), top5 + er + 4
    if s.free((ex - er, ey - er, ex + er, ey + er), 4):
        s.put(2, _earth(ex, ey, er), (ex - er, ey - er, ex + er, ey + er), "earth")

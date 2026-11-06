"""Footer episodes about code: bugs, tests, review, version control and recorded decisions.

Each retells a plot of the printed original with the agent in it. The topic words and the lettering are under
`footers: name:` in the locale; the props each story needs are private functions here, drawn like those of
`things.py`: `_thing(x, y, k, ...) -> str`, the origin where the thing touches the ground, at k = 1 drawn for a
137-unit professor.
"""
from __future__ import annotations

import math

from .. import design as P
from ..design import darken, lighten
from . import props, rig, sets, things
from .characters import module
from .footers import night_sky, Strip, episode
from .ink import INK, Canvas, angle_of, ellipse_d, lettering, n, polar, rounded_rect_d
from .openers import Box, strip_boxes
from .scenes import actor as draw_actor
from .sets import _at, _label, doodle_at


# ============================================================================ helpers
def _point(box: Box, cx: float, cy: float, flip: bool) -> tuple[float, float]:
    """A point given in a character's own canvas units, on the strip."""
    mod = module(box.name)
    k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
    mid = (box.left + box.right) / 2
    dx = (cx - mod.CENTER_X) * k
    return (mid - dx if flip else mid + dx), box.bottom - (mod.FEET_Y - cy) * k


def _palm(box: Box, pose: str, flip: bool, side: str = "right", reach: float = 0.35) -> tuple[float, float]:
    """The middle of a character's hand: past the wrist along the forearm by `reach` of the forearm's length, where
    a grip (a knob, a handle) is drawn so the fingers close round it."""
    mod = module(box.name)
    arm = mod.POSES[pose][-1 if side == "right" else -2]
    (ex, ey), (wx, wy) = arm[0], arm[1]
    return _point(box, wx + (wx - ex) * reach, wy + (wy - ey) * reach, flip)


def _height(s: Strip, name: str, size: float = 1.0) -> float:
    """How tall a character stands in this strip."""
    mod = module(name)
    return s.tall * size * mod.SCENE_SCALE * (mod.FEET_Y - mod.HEAD_TOP) / 426


def _frac(s: Strip, x: float) -> float:
    """The fraction across the usable width at which x lies (for standing someone right beside a thing)."""
    return (x - s.lo) / (s.hi - s.lo)


def _box(x: float, y: float, k: float, w: float, h: float) -> tuple[float, float, float, float]:
    """The box of a thing `w` x `h` standing at (x, y) at scale k."""
    return (x - w * k / 2, y - h * k, x + w * k / 2, y)


def _drops(x: float, y: float, k: float, count: int = 3, color: str = P.WATER) -> str:
    """Falling drops below (x, y)."""
    c = Canvas()
    for i in range(count):
        dx, dy = (-6, 4, -1, 7)[i % 4] * k, (6 + i * 9) * k
        c.shape(f"M{n(x + dx)},{n(y + dy - 4 * k)} Q{n(x + dx + 2.6 * k)},{n(y + dy + 1 * k)} {n(x + dx)},"
                f"{n(y + dy + 2 * k)} Q{n(x + dx - 2.6 * k)},{n(y + dy + 1 * k)} {n(x + dx)},{n(y + dy - 4 * k)} Z",
                color, sw=1, light=None)
    return c.render()


def _magnifier(x: float, y: float, r: float, hx: float, hy: float) -> str:
    """A magnifying glass: the lens centred at (x, y), the handle running to (hx, hy)."""
    c = Canvas()
    a = math.atan2(hy - y, hx - x)
    c.line(f"M{n(x + math.cos(a) * r)},{n(y + math.sin(a) * r)} L{n(hx)},{n(hy)}", r * 0.38 + 2, INK)
    c.line(f"M{n(x + math.cos(a) * r)},{n(y + math.sin(a) * r)} L{n(hx)},{n(hy)}", r * 0.38, P.WOOD_DARK)
    c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{P.LENS}" fill-opacity=".35" stroke="{INK}" '
          f'stroke-width="{n(max(1.6, r * 0.2))}"/>')
    c.line(f"M{n(x - r * 0.55)},{n(y - r * 0.1)} Q{n(x - r * 0.5)},{n(y - r * 0.55)} {n(x - r * 0.05)},"
           f"{n(y - r * 0.6)}", max(1, r * 0.12), P.WHITE, 0.8)
    return c.render()


def _held_magnifier(hand: tuple[float, float], lens: tuple[float, float], r: float) -> str:
    """A magnifier held in a hand: the handle runs through the fist a little beyond it, the lens over `lens`."""
    hx, hy = hand
    lx, ly = lens
    a = math.atan2(hy - ly, hx - lx)
    return _magnifier(lx, ly, r, hx + math.cos(a) * r * 0.5, hy + math.sin(a) * r * 0.5)


def _stick(x0: float, y0: float, x1: float, y1: float, width: float, color: str, bend: float = 0) -> str:
    """A rod, a pointer or a stick from (x0, y0) to (x1, y1), ink-outlined; `bend` bows it upward."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 - bend
    d = f"M{n(x0)},{n(y0)} Q{n(mx)},{n(my)} {n(x1)},{n(y1)}"
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{n(width + 2)}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{n(width)}" stroke-linecap="round"/>')


def _arrow(points: tuple, width: float, color: str) -> str:
    """A smooth arrow through three points (start, bend, end): an ink-outlined stroke and a filled head aligned
    with the direction the path arrives in."""
    (x0, y0), (cx, cy), (x1, y1) = points
    a = math.atan2(y1 - cy, x1 - cx)
    head = width * 2.6
    bx, by = x1 - math.cos(a) * head * 0.8, y1 - math.sin(a) * head * 0.8
    d = f"M{n(x0)},{n(y0)} Q{n(cx)},{n(cy)} {n(bx)},{n(by)}"
    px, py = -math.sin(a) * head * 0.62, math.cos(a) * head * 0.62
    ox, oy = x1 - math.cos(a) * head * 1.1, y1 - math.sin(a) * head * 1.1      # the middle of the head's base
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{n(width + 2.2)}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{n(width)}" stroke-linecap="round"/>'
            f'<path d="M{n(x1)},{n(y1)} L{n(ox + px)},{n(oy + py)} L{n(ox - px)},{n(oy - py)} Z" fill="{color}" '
            f'stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>')


# ============================================================================ props: the pond
def _cattails(x: float, y: float, k: float = 1.0, mirror: bool = False) -> str:
    """A clump of cattails and sedge, 70 high."""
    c = Canvas()
    c.line("M-10,0 Q-14,-26 -22,-40 M-2,0 Q0,-30 -4,-56 M6,0 Q12,-24 22,-36 M12,0 Q14,-20 10,-34", 2, P.LEAF_DARK)
    c.line("M-6,0 V-58 M4,0 Q6,-30 4,-66 M14,0 Q18,-30 18,-48", 1.8, P.LEAF_DARK)
    for px, py, ln in ((-6, -60, 15), (4, -68, 17), (18, -50, 13)):
        c.shape(rounded_rect_d(px - 3.2, py - ln, 6.4, ln, 3.2), P.WOOD_DARK, sw=1.4, light=(-1, 0))
        c.line(f"M{px},{py - ln} v-6", 1.2)
    return _at(c, x, y, k, mirror)


def _tin_can(x: float, y: float, k: float = 1.0) -> str:
    """An old dented tin can hanging on a hook; the origin is the hook's eye on the line."""
    c = Canvas()
    c.line("M0,0 V5 q0,4 -4,4", 1.4, P.METAL_DARK)
    c.shape("M-11,8 L11,6 L12,30 Q0,33 -12,31 Z", P.METAL, sw=1.6, light=(-2, -1), shade_k=0.82)
    c.shape(ellipse_d(0, 7, 11, 3), darken(P.METAL, 0.8), sw=1.3, light=None)
    c.path("M-11.5,14 L11.5,12 L11.8,22 L-11.8,24 Z", P.RED, 1.2)
    c.line("M-6,18 h9", 1, P.WHITE)
    c.line("M5,26 l3,2 l-2,2", 1, opacity=0.7)                # a dent
    c.path("M10,6 L15,-3 L12,7 Z", P.METAL_LIGHT, 1.1)          # the lid sticks up
    c.add(f'<path d="M-9,30 q4,4 0,9 q-3,-4 0,-9 Z" fill="{P.WATER}" stroke="{INK}" stroke-width=".8"/>')
    c.add(f'<path d="M5,32 q-2,3 1,6" fill="none" stroke="{P.LEAF_DARK}" stroke-width="1.4"/>')    # weed
    return _at(c, x, y, k)


def _fish(x: float, y: float, k: float = 1.0, mirror: bool = False) -> str:
    """A fish peeking out of the water, a bubble over its mouth; the origin is the waterline."""
    c = Canvas()
    c.shape("M-14,2 Q-12,-16 2,-18 Q14,-16 14,-4 L14,2 Z", P.ORANGE, sw=1.6, light=(-1, -1))
    c.add(f'<circle cx="6" cy="-10" r="3.6" fill="{P.WHITE}" stroke="{INK}" stroke-width="1"/>')
    c.dot(7, -10, 1.6)
    c.line("M14,-4 q-3,1 -5,-1", 1.2)
    c.line("M-6,-15 q2,-6 6,-4", 1.2)
    c.add(f'<circle cx="20" cy="-14" r="2.4" fill="none" stroke="{INK}" stroke-width=".9"/>'
          f'<circle cx="24" cy="-22" r="1.6" fill="none" stroke="{INK}" stroke-width=".9"/>')
    c.line("M-20,3 q6,-3 12,0 M8,3 q6,-3 12,0", 1.2, P.WHITE)
    return _at(c, x, y, k, mirror)


def _frog_lily(x: float, y: float, k: float = 1.0) -> str:
    """A frog on a lily pad, laughing with its mouth wide open, holding its belly."""
    c = Canvas()
    c.shape("M0,0 m-24,0 a24,7 0 1 0 48,0 a24,7 0 1 0 -48,0 Z M0,0 L22,-3 L20,3 Z", P.LEAF, sw=1.8, light=None)
    c.shape("M-13,-2 Q-16,-20 0,-22 Q16,-20 13,-2 Z", P.GREEN, sw=1.8, light=(-1, -1))
    c.shape("M-8,-4 Q0,2 8,-4 Q4,-12 0,-12 Q-4,-12 -8,-4 Z", P.YELLOW_PALE, sw=1, light=None)
    for ex in (-7, 7):
        c.shape(ellipse_d(ex, -22, 5, 5), P.GREEN, sw=1.6, light=None)
        c.line(f"M{ex - 3},-22 q3,-3 6,0", 1.4)                 # eyes screwed shut with laughter
    c.shape("M-7,-15 Q0,-6 7,-15 Z", P.MOUTH, sw=1.4, light=None)
    c.line("M-12,-8 q6,4 4,-2 M12,-8 q-6,4 -4,-2", 1.6)
    return _at(c, x, y, k)


def _red_cap(box: Box, flip: bool) -> str:
    """The professor's red cap with a peak, put on his head."""
    x, y = _point(box, 122, 44, flip)
    k = (box.bottom - box.top) / 426
    c = Canvas()
    c.shape("M-50,8 Q-52,-40 0,-44 Q52,-40 50,8 Q0,0 -50,8 Z", P.RED, sw=2.4, light=(-4, -3),
            highlight="M-34,-14 Q-30,-30 -14,-36")
    c.shape("M30,4 Q62,-2 78,10 Q56,16 30,12 Z", darken(P.RED, 0.8), sw=2.2, light=None)
    c.add(f'<circle cx="0" cy="-44" r="6" fill="{P.RED}" stroke="{INK}" stroke-width="2"/>')
    c.line("M-2,-40 Q-6,-14 -10,4 M12,-40 Q16,-14 20,4", 1.6, opacity=0.5)
    return _at(c, x, y, k, flip)


def _notebook(x: float, y: float, k: float = 1.0) -> str:
    """A spiral notebook with tally marks, held open; the origin is its bottom middle."""
    c = Canvas()
    c.shape("M-20,0 V-24 H20 V0 Z", P.CARD, sw=1.5, light=None)
    c.line("M0,0 V-24", 1.1)
    for i in range(6):
        c.add(f'<circle cx="0" cy="{-21 + i * 4}" r="1.2" fill="none" stroke="{INK}" stroke-width=".8"/>')
    c.line("M-16,-18 h12 M-16,-12 h10 M-16,-6 h12", 0.9, opacity=0.5)
    c.line("M5,-19 v6 M8,-19 v6 M11,-19 v6 M14,-19 v6 M4,-14 l12,-4", 1.1, P.PEN)
    c.line("M5,-9 v6", 1.1, P.PEN)
    c.line("M18,-4 L30,-20", 2.6, P.YELLOW)
    c.line("M18,-4 l-1,3", 1.4)
    return _at(c, x, y, k)


# ============================================================================ 1. the tin can
@episode("tin_can")
def tin_can(s: Strip) -> None:
    """The catch. The professor in his red fishing cap stands at the edge of the pond and lifts his rod over the
    water - and out of the pond, on the line, comes an old tin can, ripples still spreading where it broke the
    surface. It swings over the bank where the caterpillar stands and drips pond water right onto her head. The
    agent notes the catch in its notebook (fish: none, cans: one); in the pond a frog on its lily pad laughs till
    it holds its belly, and a fish peeks out, much amused."""
    s.outdoors()
    k = s.unit
    # The pond lies in the ground in front of the far bank; the caterpillar stands on that bank, behind it.
    prof = s.cast("professor", 0.04, "present", "smile", flip=False, nearer=0.35, group="fishing")
    s.put(prof.bottom + 0.2, _red_cap(prof, False), None, group="fishing")
    px0, px1 = (prof.left + prof.right) / 2 + 26 * k, s.x(0.72)
    back = s.feet(px0)
    ry = (s.h - back) * 0.4
    py = back + 3 + ry
    rx = (px1 - px0) / 2
    pcx = (px0 + px1) / 2
    s.back.add(f'<path d="{ellipse_d(pcx, py, rx + 5, ry + 3)}" fill="{darken(P.SAND, 0.92)}" '
               f'stroke="{INK}" stroke-width="1.6"/>')
    s.back.add(f'<path d="{ellipse_d(pcx, py + 1, rx, ry)}" fill="{P.WATER}"/>')
    s.back.add(f'<path d="M{n(pcx - rx * 0.8)},{n(py - ry * 0.35)} Q{n(pcx)},{n(py - ry * 0.75)} '
               f'{n(pcx + rx * 0.8)},{n(py - ry * 0.35)}" fill="none" stroke="{P.WATER_LIGHT}" stroke-width="3" '
               f'opacity=".7"/>')
    # The caterpillar on the far bank, the can right over her head.
    cx = s.x(0.3)
    cat = s.cast("caterpillar", 0.3, "stand", "surprise", flip=True, group="fishing")
    can_y = max(s.h * 0.2 + 4 * k, cat.top - 50 * k)                       # the hook's eye
    tip = (cx + 6 * k, max(s.h * 0.16, can_y - 26 * k))
    hx, hy = s.hand(prof, "present", False)
    a = math.atan2(tip[1] - hy, tip[0] - hx)
    butt = (hx - math.cos(a) * 16 * k, hy - math.sin(a) * 16 * k)
    lift = a - 0.3                                             # it leaves the hand steeper and bows down to the tip
    reach = math.hypot(tip[0] - hx, tip[1] - hy) * 0.55
    ctrl = (hx + math.cos(lift) * reach, hy + math.sin(lift) * reach)
    rod = f"M{n(butt[0])},{n(butt[1])} L{n(hx)},{n(hy)} Q{n(ctrl[0])},{n(ctrl[1])} {n(tip[0])},{n(tip[1])}"
    reel = (hx + math.cos(a) * 10 * k, hy + math.sin(a) * 10 * k + 4 * k)
    s.put(prof.bottom - 0.5, f'<path d="{rod}" fill="none" stroke="{INK}" stroke-width="{n(4.6 * k)}" '
          f'stroke-linecap="round" stroke-linejoin="round"/><path d="{rod}" fill="none" stroke="{P.WOOD}" '
          f'stroke-width="{n(2.6 * k)}" stroke-linecap="round" stroke-linejoin="round"/>'
          f'<circle cx="{n(reel[0])}" cy="{n(reel[1])}" r="{n(4 * k)}" fill="{P.METAL}" stroke="{INK}" '
          f'stroke-width="1.4"/>', None, group="fishing")
    # The line from the rod's tip down to the can; drops falling from the can onto her head, and a trail of
    # drops back down to the rings on the water where it came out.
    can_k = k * 0.9
    s.put(prof.bottom + 0.3, f'<path d="M{n(tip[0])},{n(tip[1])} L{n(cx)},{n(can_y)}" stroke="{INK}" '
          f'stroke-width="1"/>' + _tin_can(cx, can_y, can_k)
          + _drops(cx - 7 * k, can_y + 34 * can_k, k, min(3, max(1, int((cat.top - can_y - 34 * can_k) / (9 * k))))),
          [(cx - 12 * can_k, can_y, cx + 14 * can_k, can_y + 32 * can_k)]
          + strip_boxes([butt, ((hx + tip[0]) / 2 + (ctrl[0] - (hx + tip[0]) / 2) * 0.5,
                              (hy + tip[1]) / 2 + (ctrl[1] - (hy + tip[1]) / 2) * 0.5), tip], 6 * k), "rod",
          group="fishing")
    s.put(cat.bottom + 0.2, _splash(cat.top + (cat.bottom - cat.top) * 0.05, cx, k), None, group="fishing")
    rcx, rcy = cx + 8 * k, py - ry * 0.5
    s.back.add("".join(f'<path d="{ellipse_d(rcx, rcy, r * k, r * k * 0.3)}" fill="none" stroke="{P.WHITE}" '
                       f'stroke-width="1.4" opacity="{0.9 - r / 40:.2f}"/>' for r in (6, 12, 18)))
    # The pond's life.
    fx, fy = pcx + rx * 0.18, py + ry * 0.2
    s.put(fy + 1, _frog_lily(fx, fy, k), _box(fx, fy, k, 50, 36), "frog")
    fsx, fsy = pcx + rx * 0.55, py + ry * 0.05
    s.put(fsy + 1, _fish(fsx, fsy, k * 0.9), _box(fsx + 4 * k, fsy, k, 46, 26), "fish")
    s.thing(lambda x, y, k: _cattails(x, y, k, mirror=True), _frac(s, px1 + 6 * k), 46, 86, nearer=0.05,
            name="reeds2")
    s.mouth = lambda box: (fx, fy - 11 * k)       # the frog's laughing mouth: say() knows only the characters'
    try:
        s.say(Box(fx - 25 * k, fy - 37 * k, fx + 25 * k, fy, "frog", "frog"), s.word("ha"), shout=True, size=12)
    finally:
        del s.mouth
    if s.base > 70:
        dx, dy = s.x(0.6), max(16, s.base - 46 * k)
        if s.free((dx - 14 * k, dy - 8 * k, dx + 14 * k, dy + 16 * k), 4):
            s.put(s.h, sets.dragonfly(dx, dy, k * 0.5), (dx - 14 * k, dy - 8 * k, dx + 14 * k, dy + 16 * k),
                  "dragonfly")
    agent = s.cast("agent", 0.92, "type", "smile", flip=True, mark="ok", group="agent")
    s.held(agent, "type", True, lambda x, y, k: _notebook(x, y, k * 0.8))
    s.thing(lambda x, y, k: sets.snail(x, y, k * 0.6), 0.83, 32, 20, nearer=0.85, name="snail")


def _splash(y: float, x: float, k: float) -> str:
    """Three short splash strokes where the drops hit the top of a head at (x, y)."""
    c = Canvas()
    c.line(f"M{n(x - 9 * k)},{n(y - 2 * k)} l{n(-5 * k)},{n(-4 * k)} M{n(x + 9 * k)},{n(y - 2 * k)} "
           f"l{n(5 * k)},{n(-4 * k)} M{n(x - 3 * k)},{n(y - 6 * k)} l{n(-1 * k)},{n(-5 * k)}", 1.3, P.WATER)
    return c.render()


# ============================================================================ props: two television sets
def _sideboard(x: float, y: float, k: float = 1.0, w: float = 260) -> str:
    """A long low sideboard on splayed legs, 36 high; things stand on its top at y - 36."""
    c = Canvas()
    hw = w / 2
    for lx, tx in ((-hw + 14, -hw + 8), (hw - 14, hw - 8)):
        c.line(f"M{lx},-8 L{tx},0", 3.6, P.WOOD_DARK)
    c.shape(f"M{-hw},-8 V-32 H{hw} V-8 Z", P.WOOD, sw=2, light=(-2, -1), shade_k=0.88)
    c.shape(rounded_rect_d(-hw - 4, -37, w + 8, 6, 2), P.WOOD_LIGHT, sw=1.8, light=None)
    for i in range(4):
        dx = -hw + w / 4 * i + 6
        c.path(f"M{n(dx)},-28 H{n(dx + w / 4 - 12)} V-12 H{n(dx)} Z", lighten(P.WOOD, 0.1), 1.2)
        c.dot(dx + w / 8 - 6, -20, 1.6)
    return _at(c, x, y, k)


def _portrait(c: Canvas, x: float, y: float, s: float, masha: bool) -> None:
    """Uncle Misha's head on a screen, or his caricature: Uncle Masha with a bow and lashes."""
    c.shape(f"M{n(x - 16 * s)},{n(y + 18 * s)} Q{n(x)},{n(y + 6 * s)} {n(x + 16 * s)},{n(y + 18 * s)} Z",
            P.SUIT, sw=1.2, light=None)
    nose = 7 if masha else 3.4
    c.shape(ellipse_d(x, y, 9 * s, 11 * s), P.SKIN, sw=1.3, light=None)
    c.shape(f"M{n(x - 9 * s)},{n(y - 4 * s)} Q{n(x - 8 * s)},{n(y - 14 * s)} {n(x)},{n(y - 12 * s)} Q{n(x + 9 * s)},"
            f"{n(y - 14 * s)} {n(x + 9 * s)},{n(y - 4 * s)} Q{n(x + 4 * s)},{n(y - 8 * s)} {n(x - 9 * s)},"
            f"{n(y - 4 * s)} Z", P.AMBER if masha else P.DARK_BROWN, sw=1, light=None)
    c.add(f'<circle cx="{n(x - 3.4 * s)}" cy="{n(y - 2 * s)}" r="{n(1.1 * s)}" fill="{INK}"/>'
          f'<circle cx="{n(x + 3.4 * s)}" cy="{n(y - 2 * s)}" r="{n(1.1 * s)}" fill="{INK}"/>')
    c.shape(ellipse_d(x, y + 2 * s, nose * 0.6 * s, nose * 0.5 * s), P.PINK if masha else P.EAR, sw=0.9, light=None)
    c.shape(f"M{n(x - 7 * s)},{n(y + 6 * s)} Q{n(x)},{n(y + 3 * s)} {n(x + 7 * s)},{n(y + 6 * s)} Q{n(x)},"
            f"{n(y + 8 * s)} {n(x - 7 * s)},{n(y + 6 * s)} Z", P.DARK_BROWN, sw=0.8, light=None)
    if masha:
        c.line(f"M{n(x - 5 * s)},{n(y - 4 * s)} l-2,-2 M{n(x - 3.4 * s)},{n(y - 4.4 * s)} v-2.4 "
               f"M{n(x + 5 * s)},{n(y - 4 * s)} l2,-2 M{n(x + 3.4 * s)},{n(y - 4.4 * s)} v-2.4", 0.8)
        c.shape(f"M{n(x)},{n(y - 13 * s)} l-8,-5 v9 Z M{n(x)},{n(y - 13 * s)} l8,-5 v9 Z", P.PINK, sw=1,
                light=None)
        c.add(f'<circle cx="{n(x)}" cy="{n(y - 13 * s)}" r="2" fill="{P.PINK}" stroke="{INK}" stroke-width=".8"/>')
        c.add(f'<ellipse cx="{n(x - 6 * s)}" cy="{n(y + 3 * s)}" rx="{n(2 * s)}" ry="{n(1.2 * s)}" fill="{P.PINK}" '
              f'opacity=".7"/><ellipse cx="{n(x + 6 * s)}" cy="{n(y + 3 * s)}" rx="{n(2 * s)}" ry="{n(1.2 * s)}" '
              f'fill="{P.PINK}" opacity=".7"/>')
        c.dot(x + 4 * s, y + 10 * s, 1.4 * s, INK)
        c.add(f'<circle cx="{n(x - 9 * s)}" cy="{n(y + 4 * s)}" r="{n(1.6 * s)}" fill="{P.SUN}" stroke="{INK}" '
              f'stroke-width=".7"/>')


def _caption_size(k: float) -> float:
    """The size of a television caption's letters at scale k, big enough on the page for the balloon letters."""
    return max(11.5, 11.5 / k)


def _tv(x: float, y: float, k: float = 1.0, caption: str = "", masha: bool = False, odd: int = -1) -> str:
    """A wooden television set on short legs with rabbit-ear antennae, 70 high; a caption plate under the
    screen, its letters as big as the set allows (the `odd` one in red)."""
    c = Canvas()
    size = _caption_size(k)
    plate = size + 4
    c.line("M-12,-58 L-26,-82 M12,-58 L28,-80", 1.6, P.METAL_DARK)
    c.add(f'<circle cx="-26" cy="-82" r="2" fill="{INK}"/><circle cx="28" cy="-80" r="2" fill="{INK}"/>')
    c.shape("M-14,-58 Q0,-66 14,-58 Z", P.CHARCOAL, sw=1.4, light=None)
    c.line("M-26,0 l3,-6 M26,0 l-3,-6", 2.4, P.WOOD_DARK)
    c.shape(rounded_rect_d(-34, -60, 68, 55, 6), P.WOOD, sw=2, light=(-2, -2), shade_k=0.85)
    low = -8 - plate - 3                       # the screen's bottom edge
    sh = low + 55
    glass = c.shape(rounded_rect_d(-28, -55, 46, sh, min(8, sh / 3)), lighten(P.SCREEN_LIGHT, 0.45), sw=1.8,
                    light=None, clip=True)
    inner = Canvas()
    _portrait(inner, -5, -55 + sh * 0.5, min(1.0, sh / 34), masha)
    c.add(f'<g clip-path="url(#{glass})">{inner.render()}</g>')
    c.line(f"M-24,-50 q-1,{n(sh * 0.2)} 0,{n(sh * 0.4)}", 1.6, P.WHITE, 0.6)
    for i in range(2):
        c.add(f'<circle cx="26" cy="{-50 + i * 9}" r="3" fill="{P.CREAM}" stroke="{INK}" stroke-width="1"/>')
    c.shape(rounded_rect_d(-30, -8 - plate, 60, plate, 2), P.CREAM, sw=1.2, light=None)
    if caption:
        step = min(size * 0.72, 54 / max(1, len(caption)))
        for i, ch in enumerate(caption):
            sets.fit_label(c, (i - (len(caption) - 1) / 2) * step, -8 - plate / 2 + size * 0.36, ch, size, step,
                           P.RED if i == odd else INK)
    return _at(c, x, y, k)


def _caption_x(k: float, caption: str, i: int) -> float:
    """Where the i-th letter of a caption sits across the set, at scale k."""
    step = min(_caption_size(k) * 0.72, 54 / max(1, len(caption)))
    return (i - (len(caption) - 1) / 2) * step * k


def _vase(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.line("M0,-18 Q-3,-30 -8,-36 M0,-18 Q2,-32 4,-40 M0,-18 Q6,-28 12,-32", 1.4, P.LEAF_DARK)
    for fx, fy, col in ((-8, -36, P.PINK), (4, -40, P.YELLOW), (12, -32, P.WHITE)):
        c.add(f'<circle cx="{fx}" cy="{fy}" r="3.6" fill="{col}" stroke="{INK}" stroke-width="1"/>')
        c.dot(fx, fy, 1.1, P.AMBER)
    c.shape("M-6,0 Q-10,-10 -4,-18 H4 Q10,-10 6,0 Z", P.BLUE, sw=1.5, light=(-1, -1))
    return _at(c, x, y, k)


def _remote(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.shape("M-14,0 L-12,-6 L14,-8 L14,-2 Z", P.CHARCOAL, sw=1.3, light=None)
    for i, col in enumerate((P.RED, P.WHITE, P.WHITE, P.GREEN)):
        c.dot(-8 + i * 5.5, -4.4 - i * 0.3, 1.2, col)
    return _at(c, x, y, k)


# ============================================================================ 2. uncle Misha, uncle Masha
@episode("uncle_masha")
def uncle_masha(s: Strip) -> None:
    """Uncle Misha, uncle Masha. Two television sets stand side by side, the same portrait on both, but the second
    caption has one letter changed - and the uncle on it has become an aunt, bow, lashes and all. The caterpillar
    and the sparrow gape; the agent's pointer picks out the one letter that differs, underlined in red. A vase on the
    sideboard, the remote on the floor; on a tall wall, the real uncle Misha's photograph."""
    s.indoors()
    k = s.unit
    s.cast("caterpillar", 0.04, "think", "surprise", flip=False)
    s.cast("sparrow", 0.2, "shrug", "surprise", flip=False, mark="?")
    bw = 270
    bx = s.x(0.53)
    y = s.feet(bx)
    t = k * 1.15                                # the sets a little larger than life, for their captions
    tv1, tv2 = bx - 40 * t, bx + 76 * t
    top = y - 37 * k
    one, two = s.word("misha"), s.word("masha")
    odd = next((i for i, (a, b) in enumerate(zip(one, two, strict=False)) if a != b), 0)
    s.put(y - 1, _sideboard(bx, y, k, bw) + _tv(tv1, top, t, one) + _tv(tv2, top, t, two, masha=True, odd=odd)
          + _vase(bx - 116 * k, top, k * 0.8),
          [(bx - 139 * k, y - 37 * k, bx + 139 * k, y), (tv1 - 36 * t, top - 84 * t, tv2 + 36 * t, top),
           (bx - 126 * k, top - 34 * k, bx - 106 * k, top)],
          "sideboard")
    # The agent at the sideboard's end points its pointer up at the odd letter, underlined in red; the pointer
    # comes from below, so no letter of the caption is covered.
    lx = tv2 + _caption_x(t, two, odd)
    step = min(_caption_size(t) * 0.72, 54 / max(1, len(two))) * t
    under = top - 9.4 * t
    half = _height(s, "agent") * 0.36
    agent = s.cast("agent", _frac(s, bx + 139 * k + half + 8), "point", "smile", flip=True, mark="!", group="agent")
    hx, hy = _palm(agent, "point", True, reach=0.2)
    tip = (lx + step * 0.3, under + 3.2 * t)
    s.put(agent.bottom - 0.5, f'<path d="M{n(lx - step * 0.42)},{n(under)} H{n(lx + step * 0.42)}" stroke="{P.RED}" '
          f'stroke-width="{n(1.5 * t)}" stroke-linecap="round"/>'
          + _stick(hx + (hx - tip[0]) * 0.08, hy + (hy - tip[1]) * 0.08, tip[0], tip[1], 1.6 * t, P.WOOD_DARK)
          + f'<circle cx="{n(tip[0])}" cy="{n(tip[1])}" r="{n(1.6 * t)}" fill="{P.RED}" stroke="{INK}" '
            f'stroke-width=".8"/>', None, group="agent")
    s.thing(lambda x, y, k: _remote(x, y, k), 0.66, 30, 10, nearer=0.9, name="remote")
    s.thing(lambda x, y, k: sets.yarn(x, y, 8 * k, P.PINK), 0.95, 18, 18, nearer=0.6, name="yarn")
    if s.h >= 200:
        wx, wy = s.x(0.3), top - 70 * k
        box = (wx - 22 * k, wy - 28 * k, wx + 22 * k, wy + 24 * k)
        if wy - 28 * k > s.h * 0.2 and s.free(box, 8):
            s.put(3, _photo(wx, wy, k), box, "photo")


def _photo(x: float, y: float, k: float) -> str:
    """Uncle Misha's framed photograph on the wall; the origin is its centre."""
    c = Canvas()
    c.line("M0,-28 L-14,-18 M0,-28 L14,-18", 1.2)
    c.shape(rounded_rect_d(-18, -20, 36, 42, 2), P.WOOD_DARK, sw=1.8, light=None)
    c.shape(rounded_rect_d(-13, -15, 26, 32, 1), P.CREAM, sw=1.2, light=None)
    _portrait(c, 0, -2, 1.0, False)
    return _at(c, x, y, k)


# ============================================================================ props: the Moon, twice
def _rocket(x: float, y: float, k: float = 1.0, upside: bool = False) -> str:
    """A yellow rocket with red fins and a porthole, 90 tall, standing on its fins (or on its nose, upside down)."""
    c = Canvas()
    c.shape("M-12,-14 L-24,0 L-22,-24 L-12,-36 Z M12,-14 L24,0 L22,-24 L12,-36 Z", P.RED, sw=1.8, light=None)
    c.shape("M-14,-10 Q-18,-50 0,-90 Q18,-50 14,-10 Z", P.YELLOW, sw=2, light=(-3, -2), shade_k=0.85,
            highlight="M-8,-30 Q-10,-50 -4,-70")
    c.shape("M-9,-72 Q0,-94 9,-72 Q0,-76 -9,-72 Z", P.RED, sw=1.6, light=None)
    c.add(f'<circle cx="0" cy="-52" r="7.4" fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="1.8"/>'
          f'<circle cx="0" cy="-52" r="4.6" fill="{P.SCREEN_LIGHT}" stroke="{INK}" stroke-width="1"/>')
    c.shape("M-6,-10 H6 L4,-2 H-4 Z", P.METAL_DARK, sw=1.4, light=None)
    return _at(c, x, y - 90 * k, k, turn=180) if upside else _at(c, x, y, k)


def _moon_ground(c: Canvas, s: Strip) -> None:
    """A starry black sky and the grey cratered Moon underfoot."""
    sets.sky(c, *night_sky(s.look), s.base + 10, 840)
    sets.stars(c, (10, 4, 830, s.base - 6), int(16 + s.base / 6), seed=s.rnd.randrange(99))
    c.add(f'<path d="M0,{n(s.base)} Q210,{n(s.base - 8)} 420,{n(s.base - 2)} T840,{n(s.base - 4)} V{n(s.h)} H0 Z" '
          f'fill="{P.STONE}" stroke="{INK}" stroke-width="2"/>')
    for _ in range(9):
        x = s.rnd.uniform(20, 820)
        y = s.rnd.uniform(s.base + 8, s.h - 8)
        r = s.rnd.uniform(8, 18) * s.unit
        c.add(f'<path d="{ellipse_d(x, y, r, r * 0.35)}" fill="{darken(P.STONE, 0.85)}" stroke="{INK}" '
              f'stroke-width="1.2"/><path d="M{n(x - r)},{n(y)} Q{n(x)},{n(y - r * 0.5)} {n(x + r)},{n(y)}" '
              f'fill="none" stroke="{P.WHITE}" stroke-width="1.2" opacity=".6"/>')


def _crater(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.shape(ellipse_d(0, 0, 40, 9), darken(P.STONE, 0.8), sw=1.8, light=None)
    c.shape("M-44,0 Q-40,-8 -30,-6 L-34,2 Z M44,0 Q40,-8 30,-6 L34,2 Z", P.STONE, sw=1.4, light=None)
    for dx, dy, r in ((-30, -8, 3), (28, -10, 2.4), (36, -4, 2), (-38, -12, 1.8)):
        c.add(f'<circle cx="{dx}" cy="{dy}" r="{r}" fill="{P.STONE}" stroke="{INK}" stroke-width=".9"/>')
    return _at(c, x, y, k)


def _smoke(x: float, y: float, k: float = 1.0) -> str:
    """Puffs of smoke rising from (x, y), 60 high."""
    c = Canvas()
    for dx, dy, r in ((0, -10, 10), (8, -26, 12), (-4, -44, 13), (10, -60, 9)):
        c.shape(ellipse_d(dx, dy, r, r * 0.85), lighten(P.METAL_DARK, 0.2), sw=1.6, light=(-2, -2), shade_k=0.85)
    return _at(c, x, y, k)


def _helmet(box: Box, flip: bool, pose: str = "stand") -> str:
    """A fishbowl space helmet on the sparrow, built on his own canvas (his head and body are one egg, the beak
    line at y 94-112): a glass dome over the head down to the neck line under the beak, a glint on the glass, and
    a metal neck ring with bolts across the egg at that line. It follows the pose's body tilt and the flip."""
    mod = module("sparrow")
    tilt = mod.POSES[pose][3]
    k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
    mid = (box.left + box.right) / 2
    c = Canvas()
    c.add(f'<path d="M40,114 C34,40 62,-10 100,-10 C138,-10 166,40 160,114 Z" fill="{P.LENS}" fill-opacity=".16" '
          f'stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>')
    c.line("M58,70 C56,40 70,14 92,4", 6, P.WHITE, 0.75)
    c.line("M60,88 v6", 5, P.WHITE, 0.6)
    c.shape("M36,108 Q100,124 164,108 L164,120 Q100,138 36,120 Z", P.METAL, sw=2.2, light=(-2, -1), shade_k=0.82,
            highlight="M44,113 Q100,127 156,113")
    for bx in (54, 100, 146):
        by = 124 if bx == 100 else 119
        c.add(f'<circle cx="{bx}" cy="{by}" r="2.6" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1"/>')
    sx = -k if flip else k
    return (f'<g transform="translate({n(mid)},{n(box.bottom)}) scale({n(sx)},{n(k)}) '
            f'translate({-mod.CENTER_X},{-mod.FEET_Y}) rotate({tilt},100,110)">{c.render()}</g>')


def _speed_sign(x: float, y: float, k: float, title: str,
                rows: list[tuple[str, str]]) -> tuple[str, tuple]:
    """A board on its own post, its foot at (x, y), drawn at page size: the title names the landing speed and its
    unit, and each row gives a day and the speed set that day. A digit of a later row that differs from the row above
    is red and ringed in red, so the one changed digit is the first thing seen.
    Returns the drawing and the board's box."""
    small = max(11.5, 9 * k)
    big = max(17.0, 17 * k)
    step = big * 1.12
    pad = small * 1.1
    digits = max(len(value) for _, value in rows)
    day_w = max(sets.letter_width(day, small) for day, _ in rows)
    w = max(sets.letter_width(title, small) + pad * 2, day_w + small * 1.5 + step * digits + pad * 2)
    row_h = big * 1.35
    h = small * 2.2 + row_h * len(rows) + small * 0.6
    top = max(8.0, y - 56 * k - h)                            # a low frame shortens the post, never the board
    c = Canvas()
    c.shape(f"M{n(x - 2.4 * k)},{n(y)} V{n(top + h - 2)} H{n(x + 2.4 * k)} V{n(y)} Z", P.METAL, sw=1.4,
            light=(-1, 0))
    c.shape(rounded_rect_d(x - w / 2, top, w, h, 4), P.WHITE, sw=2, light=None)
    c.add(f'<rect x="{n(x - w / 2 + 3)}" y="{n(top + 3)}" width="{n(w - 6)}" height="{n(h - 6)}" rx="2.5" '
          f'fill="none" stroke="{INK}" stroke-width="1"/>')
    sets.fit_label(c, x, top + small * 1.6, title, small, w - pad * 2)
    c.line(f"M{n(x - w / 2 + pad)},{n(top + small * 2.2)} H{n(x + w / 2 - pad)}", 1)
    left, right = x - w / 2 + pad, x + w / 2 - pad
    before = rows[0][1]
    for r, (day, value) in enumerate(rows):
        base = top + small * 2.2 + row_h * (r + 0.5) + big * 0.36
        sets.fit_label(c, left, base - (big - small) * 0.18, day, small, day_w + 1, anchor="start")
        for i, digit in enumerate(value):
            dx = right - step * (len(value) - i - 0.5)
            changed = r > 0 and (i >= len(before) or before[i] != digit)
            sets.fit_label(c, dx, base, digit, big, step * 0.95, P.RED if changed else INK)
            if changed:
                ring = n(max(1.4, 1.5 * k))
                c.add(f'<ellipse cx="{n(dx)}" cy="{n(base - big * 0.36)}" rx="{n(big * 0.44)}" '
                      f'ry="{n(big * 0.64)}" fill="none" stroke="{P.RED}" stroke-width="{ring}"/>')
        before = value
    return c.render(), (x - w / 2, top, x + w / 2, y)


def _test_console(x: float, y: float, k: float, title: str, line: str) -> tuple[str, tuple]:
    """The landing test's console on its stand, its foot at (x, y): a screen with the test's name and the failed
    check in red, and a red lamp on top - the test that would have caught the changed digit. Returns the drawing
    and the console's box."""
    small = max(11.5, 8.5 * k)
    pad = small * 0.9
    w = max(sets.letter_width(title, small, "plain"), sets.letter_width(line, small, "plain")) + pad * 2 + 12
    h = small * 2.9 + pad * 2
    top = max(14.0, y - 44 * k - h)
    c = Canvas()
    c.shape(f"M{n(x - 6 * k)},{n(y)} L{n(x - 3 * k)},{n(top + h)} H{n(x + 3 * k)} L{n(x + 6 * k)},{n(y)} Z",
            P.METAL, sw=1.4, light=(-1, 0))
    c.shape(rounded_rect_d(x - w / 2, top, w, h, 5), P.METAL, sw=2, light=(-1, -1))
    c.shape(rounded_rect_d(x - w / 2 + 6, top + 6, w - 12, h - 12, 3), P.SCREEN, sw=1.4, light=None)
    c.add(lettering(x, top + 6 + pad + small * 0.8, title, small, P.SCREEN_TEXT, style="plain"))
    c.add(lettering(x, top + 6 + pad + small * 2.1, line, small, P.RED, style="plain"))
    lamp = max(4.0, 5 * k)
    c.shape(f"M{n(x - lamp)},{n(top)} A{n(lamp)},{n(lamp)} 0 0 1 {n(x + lamp)},{n(top)} Z", P.RED, sw=1.4,
            light=None)
    return c.render(), (x - w / 2, top - lamp, x + w / 2, y)


def _tumble(box: Box) -> str:
    """Spin lines and little stars round a character tumbling through space."""
    c = Canvas()
    cx, cy = (box.left + box.right) / 2, (box.top + box.bottom) / 2
    r = (box.bottom - box.top) * 0.62
    c.line(f"M{n(cx - r)},{n(cy)} A{n(r)},{n(r * 0.8)} 0 0 1 {n(cx - r * 0.2)},{n(cy - r * 0.8)} "
           f"M{n(cx + r)},{n(cy + r * 0.1)} A{n(r)},{n(r * 0.8)} 0 0 1 {n(cx + r * 0.2)},{n(cy + r * 0.8)}", 1.6,
           P.WHITE, 0.8)
    for dx, dy in ((-0.9, -0.5), (0.8, -0.7), (0.95, 0.5)):
        x, y = cx + dx * r, cy + dy * r
        c.add(f'<path d="M{n(x)},{n(y - 5)} L{n(x + 1.5)},{n(y - 1.5)} L{n(x + 5)},{n(y)} L{n(x + 1.5)},'
              f'{n(y + 1.5)} L{n(x)},{n(y + 5)} L{n(x - 1.5)},{n(y + 1.5)} L{n(x - 5)},{n(y)} L{n(x - 1.5)},'
              f'{n(y - 1.5)} Z" fill="{P.SUN}" stroke="{INK}" stroke-width=".8"/>')
    return c.render()


def _satellite(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    for dx in (-28, 10):
        c.shape(f"M{dx},-6 H{dx + 18} V6 H{dx} Z", P.BLUE, sw=1.4, light=None)
        c.line(f"M{dx + 6},-6 V6 M{dx + 12},-6 V6 M{dx},0 H{dx + 18}", 0.8, P.WHITE)
    c.shape(rounded_rect_d(-10, -9, 20, 18, 3), P.METAL, sw=1.6, light=(-1, -1))
    c.line("M0,-9 L4,-16", 1.2)
    c.dot(4, -16, 1.6, P.RED)
    return _at(c, x, y, k, turn=-15)


def _earth(x: float, y: float, r: float) -> str:
    c = Canvas()
    c.shape(ellipse_d(x, y, r, r), P.BLUE, sw=1.6, light=(-2, -2))
    c.path(f"M{n(x - r * 0.6)},{n(y - r * 0.3)} q{n(r * 0.3)},{n(-r * 0.4)} {n(r * 0.6)},{n(-r * 0.1)} "
           f"q{n(-r * 0.1)},{n(r * 0.5)} {n(-r * 0.6)},{n(r * 0.1)} Z M{n(x + r * 0.1)},{n(y + r * 0.2)} "
           f"q{n(r * 0.5)},{n(-r * 0.2)} {n(r * 0.6)},{n(r * 0.3)} q{n(-r * 0.3)},{n(r * 0.3)} {n(-r * 0.6)},"
           f"{n(-r * 0.3)} Z", P.GREEN, 1)
    return c.render()


def _flag(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.line("M0,0 V-46", 2, P.METAL_DARK)
    c.shape("M0,-46 H22 Q18,-40 22,-34 H0 Z", P.RED, sw=1.4, light=None)
    c.add(f'<circle cx="10" cy="-40" r="3" fill="{P.SUN}" stroke="{INK}" stroke-width=".8"/>')
    return _at(c, x, y, k)


def _plate(x: float, y: float, text: str, size: float, color: str = P.CREAM) -> str:
    """A small panel caption, like a comic's: the origin is its centre."""
    c = Canvas()
    w = sets.letter_width(text, size) + size * 1.4
    c.shape(rounded_rect_d(x - w / 2, y - size * 0.8, w, size * 1.6, 3), color, sw=1.6, light=None)
    _label(c, x, y + size * 0.36, text, size)
    return c.render()


# ============================================================================ 3. to the Moon, twice
@episode("moon_twice")
def moon_twice(s: Strip) -> None:
    """To the Moon, take two. Yesterday the sparrow in his space helmet landed his yellow rocket neatly on the
    Moon; today, after one digit was changed in the program, the same rocket stands on its nose in a smoking
    crater and the sparrow tumbles through space. At the panels' border the cat points at a board on its post: the
    landing speed yesterday 10, today 70, the one changed digit red and ringed. Beside the crater stands the
    landing test's console, red: the test fails - it would have caught the digit before the launch.
    The Earth looks on."""
    s.big = False                       # no windmills or balloons in this sky
    s.dress = False                     # nor the sun and clouds: this is space
    _moon_ground(s.back, s)
    k = s.unit
    mid = s.x(0.5)
    s.back.add(f'<path d="M{n(mid)},0 V{n(s.h)}" stroke="{INK}" stroke-width="3"/>'
               f'<path d="M{n(mid)},0 V{n(s.h)}" stroke="{P.PAPER}" stroke-width="1.4" stroke-dasharray="6 6"/>')
    # Yesterday.
    # The cat at the end of the first panel points at the speed sign standing on its post beside him.
    rows = [(s.word("was"), s.word("good")), (s.word("now"), s.word("bad"))]
    _, box = _speed_sign(mid, s.feet(mid), k, s.word("speed"), rows)
    sign_x = mid - (box[2] - box[0]) / 2 - 8 * k
    art, box = _speed_sign(sign_x, s.feet(sign_x), k, s.word("speed"), rows)
    s.put(s.feet(sign_x) - 1, art, box, "sign", group="cat")
    cat_x = box[0] - _height(s, "cat") * 0.3
    cat = s.cast("cat", _frac(s, cat_x), "point", "talk", flip=False, group="cat")
    bird_x = min(s.x(0.24), cat.left - _height(s, "sparrow") * 0.55)
    bird = s.cast("sparrow", _frac(s, bird_x), "cheer", "smile", flip=True)
    s.put(bird.bottom + 0.5, _helmet(bird, True, "cheer"), None, group=bird.group)
    rx = min(s.x(0.11), bird.left - 30 * k)
    s.thing(lambda x, y, k: _rocket(x, y, k), _frac(s, rx), 50, 92, name="rocket1")
    fx = min(s.x(0.02), rx - 40 * k)
    if s.free(_box(fx, s.feet(fx), k, 26, 48), 4):             # the flag only where it finds its own room
        s.thing(lambda x, y, k: _flag(x, y, k), _frac(s, fx), 26, 48, name="flag")
    # Today.
    x2, y2 = s.thing(lambda x, y, k: _crater(x, y, k), 0.64, 92, 14, nearer=0.25, name="crater")
    s.put(y2 + 1, _smoke(x2 - 34 * k, y2 - 4 * k, k * 0.8) + _smoke(x2 + 36 * k, y2 - 6 * k, k * 0.65)
          + _rocket(x2, y2 - 2 * k, k, upside=True),
          [(x2 - 46 * k, y2 - 96 * k, x2 + 46 * k, y2 - 4 * k)], "rocket2", group="crater")
    # The landing test on its console beside the crater: it fails, so the changed digit would have been caught.
    tx = x2 + 46 * k + 14 * k
    art, box = _test_console(tx, s.feet(tx), k, s.word("test"), s.word("fail"))
    tx += tx - box[0]
    art, box = _test_console(tx, s.feet(tx), k, s.word("test"), s.word("fail"))
    if box[2] < s.hi and s.free(box, 3):
        s.put(s.feet(tx) - 1, art, box, "console", group="console")
    fly = s.flight("sparrow", 0.6, 0.8, "fly", "surprise")
    s.put(fly.bottom + 0.5, _helmet(fly, True, "fly") + _tumble(fly), None, group=fly.group)
    if s.base > 170:
        sx, sy = s.x(0.62), s.base * 0.36
        if s.free((sx - 30 * k, sy - 16 * k, sx + 30 * k, sy + 16 * k), 6):
            s.put(2, _satellite(sx, sy, k), (sx - 30 * k, sy - 16 * k, sx + 30 * k, sy + 16 * k), "satellite")
    # Side details: the Earth in the sky, and the panels' captions.
    # Each caption takes the first free spot in the sky of its own panel, nearest the panel's middle.
    for fracs, key in (((0.25, 0.32, 0.18, 0.38, 0.12), "yesterday"), ((0.75, 0.68, 0.82, 0.62, 0.88), "today")):
        size = max(11.5, 11 * k)
        y = s.h * 0.2 + size
        w = sets.letter_width(s.word(key), size) + size * 1.4
        for frac in fracs:
            x = s.x(frac)
            box = (x - w / 2, y - size * 0.8, x + w / 2, y + size * 0.8)     # the plate's own outline
            if box[0] > s.lo and box[2] < s.hi and (box[2] < mid - 6 or box[0] > mid + 6) and s.free(box, 3):
                s.put(s.h, _plate(x, y, s.word(key), size), box, f"plate{key}")
                break
    if s.base > 90:
        r = min(18, s.base * 0.12)
        ex, ey = s.x(0.08), s.h * 0.2 + r + 4
        if s.free((ex - r, ey - r, ex + r, ey + r), 6):
            s.put(2, _earth(ex, ey, r), (ex - r, ey - r, ex + r, ey + r), "earth")


# ============================================================================ props: the porch and its kittens
def _kitten(x: float, y: float, k: float = 1.0, color: str = P.CHARCOAL, stripes: bool = False,
            tag: bool = False, mirror: bool = False, smug: bool = False) -> str:
    """A kitten sitting up, 40 high; `tag` hangs a barcode tag on its collar."""
    c = Canvas()
    c.line("M10,-2 Q24,-2 22,-14 Q20,-22 26,-26", 4.4, INK)
    c.line("M10,-2 Q24,-2 22,-14 Q20,-22 26,-26", 2.6, color)
    body = c.shape("M-12,0 Q-15,-18 -6,-24 H6 Q15,-18 12,0 Z", color, sw=1.6, light=(-1, -1), clip=True)
    if stripes:
        c.add(f'<g clip-path="url(#{body})"><path d="M-14,-18 l8,3 M-14,-10 l9,3 M14,-18 l-8,3 M14,-10 l-9,3" '
              f'stroke="{darken(color, 0.7)}" stroke-width="2"/></g>')
    c.shape("M-12,-26 L-12,-42 L-5,-35 Q0,-37 5,-35 L12,-42 L12,-26 Q12,-18 0,-18 Q-12,-18 -12,-26 Z", color,
            sw=1.6, light=(-1, -1))
    c.add(f'<path d="M-10,-39 l2,-1 l1,3 Z M10,-39 l-2,-1 l-1,3 Z" fill="{P.EAR}"/>')
    eye = P.SUN if color == P.CHARCOAL else P.WHITE
    if smug:
        c.line("M-7,-29 q2.5,-2 5,0 M2,-29 q2.5,-2 5,0", 1.4, INK if color != P.CHARCOAL else P.SUN)
    else:
        c.add(f'<circle cx="-4.5" cy="-29" r="2.6" fill="{eye}" stroke="{INK}" stroke-width=".7"/>'
              f'<circle cx="4.5" cy="-29" r="2.6" fill="{eye}" stroke="{INK}" stroke-width=".7"/>')
        c.dot(-4.5, -29, 1.1)
        c.dot(4.5, -29, 1.1)
    c.add(f'<circle cx="0" cy="-25" r="1.3" fill="{P.PINK}"/>')
    c.line("M-3,-24 l-8,-1 M-3,-23.4 l-8,2 M3,-24 l8,-1 M3,-23.4 l8,2", 0.6, P.WHITE if color == P.CHARCOAL else INK)
    c.shape(ellipse_d(-5, -1, 4, 2), color, sw=1.2, light=None)
    c.shape(ellipse_d(5, -1, 4, 2), color, sw=1.2, light=None)
    if tag:
        c.line("M-8,-19 Q0,-15 8,-19", 1.6, P.RED)
        c.line("M0,-17 V-15", 0.8)
        c.shape("M-6,-15 H6 V-5 H-6 Z", P.WHITE, sw=1, light=None)
        for i, w in enumerate((0.8, 0.4, 1.2, 0.4, 0.8, 0.4, 1.0, 0.6)):
            c.add(f'<rect x="{n(-4.8 + i * 1.25)}" y="-13.6" width="{w}" height="7" fill="{INK}"/>')
    return _at(c, x, y, k, mirror)


def _porch(x: float, y: float, k: float = 1.0, w: float = 330) -> str:
    """A wooden porch deck 18 high with two steps on the left and a rail at the back; kittens sit on the deck at
    y - 18, and on the rail at y - 64."""
    c = Canvas()
    hw = w / 2
    # The rail behind the deck.
    for i in range(int((w - 60) / 46) + 1):
        px = -hw + 50 + i * 46 + 23
        c.line(f"M{n(px)},-18 V-60", 3.4, P.WOOD_DARK)
    c.shape(rounded_rect_d(-hw + 44, -66, w - 50, 7, 2), P.WOOD_LIGHT, sw=1.8, light=None)
    for px in (-hw + 46, hw - 8):
        c.shape(f"M{n(px - 4)},-18 V-72 H{n(px + 4)} V-18 Z", P.WOOD, sw=1.6, light=(-1, 0))
        c.shape(ellipse_d(px, -73, 5.4, 3), P.WOOD_LIGHT, sw=1.4, light=None)
    # The deck and its steps.
    c.shape(f"M{-hw + 40},0 V-18 H{hw} V0 Z", P.WOOD, sw=2, light=(-2, -1), shade_k=0.86)
    c.line(f"M{-hw + 40},-9 H{hw}", 1.2, opacity=0.5)
    for i in range(int((w - 40) / 30)):
        c.line(f"M{n(-hw + 52 + i * 30)},-18 v9 M{n(-hw + 66 + i * 30)},-9 v9", 1, opacity=0.5)
    c.shape(f"M{-hw},0 V-6 H{-hw + 40} V0 Z", P.WOOD_LIGHT, sw=1.6, light=None)
    c.shape(f"M{-hw + 20},-6 V-12 H{-hw + 40} V-6 Z", P.WOOD_LIGHT, sw=1.6, light=None)
    return _at(c, x, y, k)


def _scanner_beam(x: float, y: float, tx: float, ty: float, k: float) -> str:
    """A hand scanner gripped by its handle at (x, y) shining a red fan of light from its nose onto (tx, ty)."""
    c = Canvas()
    a0 = math.atan2(ty - y, tx - x)
    k *= 0.8
    up = -1 if math.cos(a0) < 0 else 1                         # pointing left, it is mirrored, handle still down
    gx, gy = -5 * k, 11 * k * up                              # the grip, in the scanner's own turned frame
    x -= gx * math.cos(a0) - gy * math.sin(a0)
    y -= gx * math.sin(a0) + gy * math.cos(a0)
    spread = 7 * k
    c.add(f'<path d="M{n(x)},{n(y)} L{n(tx)},{n(ty - spread)} L{n(tx)},{n(ty + spread)} Z" fill="{P.RED}" '
          f'opacity=".28"/>')
    c.line(f"M{n(tx)},{n(ty - spread)} V{n(ty + spread)}", 1.6, P.RED)
    a = math.degrees(math.atan2(ty - y, tx - x))
    g = Canvas()
    g.shape("M0,-5 L-16,-6 L-18,6 L-8,6 L-4,16 L2,14 L0,5 Z", P.CHARCOAL, sw=1.4, light=None)
    g.shape("M0,-5 L3,-6 L3,6 L0,5 Z", P.RED, sw=1, light=None)
    c.add(f'<g transform="translate({n(x)},{n(y)}) rotate({n(a)}) scale({n(k)},{n(k * up)})">{g.render()}</g>')
    return c.render()


def _saucer(x: float, y: float, k: float = 1.0) -> str:
    """A blue saucer of milk on the ground, seen from a little above: its foot, its rim, the white milk with a
    glint, and a drop splashed on the rim; 28 wide."""
    c = Canvas()
    c.shape("M-9,0 L-11,-4 H11 L9,0 Z", darken(P.BLUE, 0.8), sw=1.3, light=None)
    c.shape(ellipse_d(0, -5, 15, 4.6), P.BLUE, sw=1.6, light=None)
    c.add(f'<path d="{ellipse_d(0, -5.6, 11, 3)}" fill="{P.WHITE}" stroke="{INK}" stroke-width=".9"/>')
    c.line("M-6,-6.6 q3,-1.2 6,-1", 1.2, P.WATER_LIGHT)
    c.add(f'<circle cx="12.5" cy="-7.4" r="1.4" fill="{P.WHITE}" stroke="{INK}" stroke-width=".6"/>')
    return _at(c, x, y, k)


def _flower_pot(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.line("M0,-12 V-24 M0,-18 l-6,-4 M0,-20 l6,-5", 1.6, P.LEAF_DARK)
    c.add(f'<circle cx="0" cy="-26" r="4.4" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>')
    c.dot(0, -26, 1.4, P.SUN)
    c.shape("M-7,-12 H7 L5,0 H-5 Z", P.TERRACOTTA, sw=1.4, light=(-1, 0))
    return _at(c, x, y, k)


# ============================================================================ 4. five black kittens
@episode("kittens")
def kittens(s: Strip) -> None:
    """Five black kittens. On the porch sit five black kittens nobody can tell apart; the professor hangs a
    barcode tag on each, and the agent reads them one by one with its scanner beam. The two striped ginger
    kittens on the rail have never needed tags and look very smug about it; a ball of yarn has rolled off the
    step, a saucer of milk waits."""
    s.outdoors()
    k = s.unit
    prof = s.cast("professor", 0.08, "thumb", "smile", flip=False, group="porch")
    # The tag's string runs down out of his closed hand; the tag swings under it.
    gx, gy, _ = _palm_on_strip(prof, "thumb")
    pk = (prof.bottom - prof.top) / 100
    s.put(prof.bottom + 1, f'<path d="M{n(gx)},{n(gy + 3 * pk)} v{n(13 * pk)}" stroke="{P.RED}" '
          f'stroke-width="1.4"/>'
          + _tag(gx, gy + 16 * pk, k), None, group="porch")
    left = prof.right + 2 * k
    w = max(380, (s.x(0.8) - left) / k)
    px = left + w * k / 2
    py = s.feet(px)
    s.put(py - 2, _porch(px, py, k, w), [(left, py - 18 * k, px + w * k / 2, py),
                                         (left + 40 * k, py - 76 * k, px + w * k / 2, py - 18 * k)],
          "porch", group="porch")
    # Five black kittens on the deck, each with its barcode tag; the first still waits for its own.
    gap = min(90, (w - 190) / 4)
    xs = [left + (74 + i * gap) * k for i in range(5)]
    body = "".join(_kitten(kx, py - 18 * k, k * 0.95, tag=i > 0) for i, kx in enumerate(xs))
    # Two smug ginger kittens on the rail and a flowerpot.
    rail = py - 66 * k
    right = left + w * k
    body += (_kitten(right - 70 * k, rail, k * 0.8, P.ORANGE, stripes=True, smug=True)
             + _kitten(right - 40 * k, rail, k * 0.8, P.ORANGE, stripes=True, smug=True, mirror=True)
             + _flower_pot(xs[2], rail, k * 0.8))
    s.put(py - 1, body, None, group="porch")
    half = _height(s, "agent") * 0.36
    agent = s.cast("agent", _frac(s, px + w * k / 2 + half + 30 * k), "point", "smile", flip=True, mark="ok",
                   group="agent")
    ax, ay = s.hand(agent, "point", True)
    s.put(s.h, _scanner_beam(ax, ay, xs[-1] + 7 * k, py - 28 * k, k), None, group="agent")
    s.thing(lambda x, y, k: sets.yarn(x, y, 9 * k, P.BLUE, "M0,0 q-20,4 -36,-2"), 0.24, 26, 20, nearer=0.9,
            name="yarn")
    s.thing(lambda x, y, k: _saucer(x, y, k * 1.3), 0.42, 40, 14, nearer=0.9, name="saucer")
    s.thing(lambda x, y, k: sets.snail(x, y, k * 0.5), 0.74, 30, 18, nearer=0.85, name="snail")


def _tag(x: float, y: float, k: float) -> str:
    """A loose barcode tag on a string, about to be hung."""
    c = Canvas()
    c.shape("M-6,0 H6 V10 H-6 Z", P.WHITE, sw=1, light=None)
    for i, w in enumerate((0.8, 0.4, 1.2, 0.4, 0.8, 0.4, 1.0, 0.6)):
        c.add(f'<rect x="{n(-4.8 + i * 1.25)}" y="1.6" width="{w}" height="6" fill="{INK}"/>')
    return _at(c, x, y, k)


# ============================================================================ props: the scientific journal
TILT = -8                       # the ACCEPTED imprint's slant, degrees
STAMP_TILT = 10                 # the stamp's, swung up off the page


def _imprint_size(text: str, room: float) -> tuple[float, float, float, float]:
    """The ACCEPTED imprint whose slanted box is at most `room` high: its lettering size (13 down to 9.6, then the
    slant eased from TILT towards -2), its slant, and the box's width and height before the slant."""
    size, tilt = 13.0, TILT
    while True:
        w, h = sets.letter_width(text, size, style="plain") + size * 1.3 + 6, size * 1.3 + 5.5
        a = math.radians(abs(tilt))
        if h * math.cos(a) + w * math.sin(a) <= room or (size <= 9.6 and tilt >= -2):
            return size, tilt, w, h
        if size > 9.6:
            size -= 0.2
        else:
            tilt += 0.5


def _journal(x0: float, x1: float, y: float, k: float, words: dict,
             stamp: float | None = None) -> tuple[str, list[float]]:
    """A long scroll of a parody "Scientific Journal" stood on its edge from x0 to x1, 80 high at scale k, rolled up
    at both ends: a big title, then columns under the three headings of a decision record, a chart or two, and the
    red ACCEPTED imprint, slanted, in a double frame, its right edge at `stamp`. Every word is at least 9.6 on the
    page; a column that finds no room is left out. Returns the drawing and the x of the columns' middles, where
    something may peek over."""
    c = Canvas()
    top = y - 80 * k
    title, head, mark = max(11.5, 12 * k), max(9.6, 8 * k), max(9.6, 9 * k)
    c.shape(f"M{n(x0)},{n(y - 3 * k)} V{n(top)} H{n(x1)} V{n(y - 3 * k)} Z", P.CARD, sw=1.8, light=(0, 2),
            shade_k=0.94)
    _label(c, x0 + 10 * k, top + title + 2, words["journal"], title, anchor="start")
    rule = top + title + 6
    c.line(f"M{n(x0 + 8 * k)},{n(rule)} H{n(x1 - 8 * k)} M{n(x0 + 8 * k)},{n(rule + 2.5)} H{n(x1 - 8 * k)}", 1)
    # The stamp's column at the right end, the others share what is left.
    band = (rule + 6, y - 8 * k)                   # the imprint keeps clear of the rules and the bottom edge
    if stamp is not None:
        mark, tilt, mark_w, mark_h = _imprint_size(words["stamp"], band[1] - band[0])
    right = (stamp - mark_w - 8 * k) if stamp is not None else x1 - 10 * k
    room = right - x0 - 12 * k
    wanted = [("ctx", sets.letter_width(words["ctx"], head) + 8), ("fig1", 46 * k),
              ("dec", sets.letter_width(words["dec"], head) + 8), ("fig2", 46 * k),
              ("cons", sets.letter_width(words["cons"], head) + 8)]
    for drop in ("fig2", "cons", "fig1"):
        if sum(w for _, w in wanted) + 10 * k * (len(wanted) - 1) <= room:
            break
        wanted = [item for item in wanted if item[0] != drop]
    while wanted and sum(w for _, w in wanted) + 10 * k * (len(wanted) - 1) > room:
        wanted.pop()
    gap = (room - sum(w for _, w in wanted)) / max(1, len(wanted)) if wanted else 0
    peeks = []
    ys = rule + 6
    cx0 = x0 + 10 * k
    for kind, w in wanted:
        cw = w + gap - 10 * k if kind.startswith("fig") else w + gap * 0.6
        peeks.append(cx0 + cw / 2)
        if kind.startswith("fig"):
            fy0, fy1 = ys, y - 8 * k
            c.path(f"M{n(cx0)},{n(fy0)} H{n(cx0 + cw)} V{n(fy1)} H{n(cx0)} Z", P.WHITE, 1)
            if kind == "fig1":
                bars = (0.5, 0.8, 0.35, 0.95)
                bw = cw / (len(bars) * 1.6)
                for j, h in enumerate(bars):
                    bx = cx0 + bw * 0.6 + j * bw * 1.6
                    c.path(f"M{n(bx)},{n(fy1)} V{n(fy1 - (fy1 - fy0 - 4 * k) * h)} h{n(bw)} V{n(fy1)} Z",
                           (P.BLUE, P.ORANGE, P.GREEN, P.RED)[j], 1)
            else:
                pts = [(cx0 + cw * t, fy1 - (fy1 - fy0) * (0.15 + 0.7 * (0.5 + 0.5 * math.sin(t * 5.5))))
                       for t in (0.08, 0.28, 0.48, 0.68, 0.88)]
                c.line("M" + " L".join(f"{n(px)},{n(py)}" for px, py in pts), 1.6, P.RED)
                for px, py in pts:
                    c.dot(px, py, max(1.4, 1.6 * k))
        else:
            _label(c, cx0, ys + head * 0.9, words[kind], head, P.PEN, anchor="start")
            yy = ys + head * 0.9 + 6 * k + 2
            row = 0
            while yy < y - 8 * k:
                c.line(f"M{n(cx0)},{n(yy)} h{n(cw * (0.6 if row % 4 == 3 else 1.0))}", max(1.2, 1.6 * k), P.GUIDE)
                yy += max(4.5, 6 * k)
                row += 1
        cx0 += cw + (10 * k + gap * 0.4 if not kind.startswith("fig") else 10 * k)
    if stamp is not None:
        sx, sy = stamp - mark_w / 2, (band[0] + band[1]) / 2
        frame = "".join(f'<rect x="{n(sx - mark_w / 2 + inset)}" y="{n(sy - mark_h / 2 + inset)}" '
                        f'width="{n(mark_w - 2 * inset)}" height="{n(mark_h - 2 * inset)}" rx="{n(mark * 0.35)}" '
                        f'fill="none" stroke="{P.RED}" stroke-width="{n(width)}"/>'
                        for inset, width in ((0, 2.2), (3.2, 1.1)))
        c.add(f'<g transform="rotate({n(tilt)} {n(sx)} {n(sy)})" opacity=".92">{frame}</g>')
        _label(c, sx, sy + mark * 0.36, words["stamp"], mark, P.RED, turn=tilt, style="plain")
    # The two rolls at the ends.
    for rx, w in ((x0, 9 * k), (x1, 16 * k)):
        c.shape(f"M{n(rx - w / 2)},{n(y)} V{n(top - 4 * k)} Q{n(rx)},{n(top - 8 * k)} {n(rx + w / 2)},"
                f"{n(top - 4 * k)} V{n(y)} Q{n(rx)},{n(y + 3 * k)} {n(rx - w / 2)},{n(y)} Z", P.CREAM, sw=1.8,
                light=(-2, 0), shade_k=0.88)
        c.add(f'<path d="{ellipse_d(rx, top - 4 * k, w / 2, 3 * k)}" fill="{P.CARD}" stroke="{INK}" '
              f'stroke-width="1.4"/><circle cx="{n(rx)}" cy="{n(top - 4 * k)}" r="{n(1.6 * k)}" fill="{INK}"/>')
    return c.render(), peeks


def _peeking_kitten(x: float, y: float, k: float, color: str, mirror: bool = False) -> str:
    """A kitten's head and two paws over an edge at y."""
    c = Canvas()
    c.shape("M-12,2 Q-13,-10 -10,-14 L-11,-24 L-4,-18 Q0,-19 4,-18 L11,-24 L10,-14 Q13,-10 12,2 Z", color, sw=1.5,
            light=(-1, -1))
    c.add(f'<path d="M-9,-20 l2,-1 l1,3 Z M9,-20 l-2,-1 l-1,3 Z" fill="{P.EAR}"/>')
    eye = P.SUN if color == P.CHARCOAL else P.WHITE
    for ex in (-4.5, 4.5):
        c.add(f'<circle cx="{ex}" cy="-8" r="2.6" fill="{eye}" stroke="{INK}" stroke-width=".7"/>')
        c.dot(ex + 0.6, -7.4, 1.1)
    c.add(f'<circle cx="0" cy="-4" r="1.2" fill="{P.PINK}"/>')
    c.line("M-3,-3 l-8,-1 M3,-3 l8,-1", 0.6, P.WHITE if color == P.CHARCOAL else INK)
    for px in (-9, 9):
        c.shape(ellipse_d(px, 2, 4.4, 3), color, sw=1.3, light=None)
        c.line(f"M{px - 1.5},1 v2.6 M{px + 1.5},1 v2.6", 0.6)
    return _at(c, x, y, k, mirror)


def _palm_on_strip(box: Box, pose: str) -> tuple[float, float, str]:
    """Where the middle of a character's near palm is on the strip, and the transform that draws the character's
    own canvas units onto the strip (for drawing over its hand)."""
    mod = module(box.name)
    k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
    (ex, ey), (wx, wy), _, turn = mod.POSES[pose][-1]
    d = angle_of(ex, ey, wx, wy)
    hx, hy = polar(wx, wy, d, getattr(mod, "ARM_WIDTH", 15) * 0.42)     # where the module draws the hand
    px, py = polar(hx, hy, d + turn, 10 * 0.88)                         # the middle of its palm
    cx = (box.left + box.right) / 2
    sx = -k if box.flip else k
    tx = cx - sx * mod.CENTER_X
    ty = box.bottom - mod.FEET_Y * k
    return tx + sx * px, ty + py * k, f"translate({n(tx)},{n(ty)}) scale({n(sx)},{n(k)})"


def _fist(box: Box, pose: str) -> str:
    """A closed paw drawn over a character's open near hand, as if gripping a handle that runs up and down
    through the middle of its palm."""
    mod = module(box.name)
    k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
    x, y, _ = _palm_on_strip(box, pose)
    g = Canvas()
    rig.hand(g, -12.5, 0, 0, mod.HAND, "fist", 1.25)
    return _at(g, x, y, k, box.flip)


def _stamp(x: float, y: float, k: float = 1.0, tilt: float = 0) -> str:
    """An office rubber stamp gripped at (x, y) by the middle of its handle: a round knob on top, the turned
    handle, a wooden block 34 wide and the red rubber under it, 24 below the grip, slanted by `tilt` degrees."""
    c = Canvas()
    c.shape("M-3.5,-10 V10 H3.5 V-10 Z", P.WOOD_DARK, sw=1.8, light=(-1, 0))
    c.shape(ellipse_d(0, -15, 8, 6.5), P.WOOD, sw=2, light=(-2, -2))
    c.add(f'<path d="{ellipse_d(-2.6, -17.2, 2.4, 1.5)}" fill="{P.WHITE}" opacity=".75"/>')
    c.shape("M-8,13 Q-7,9 0,9 Q7,9 8,13 Z", P.WOOD_DARK, sw=1.6, light=None)
    c.shape(rounded_rect_d(-17, 13, 34, 8, 2.5), P.WOOD, sw=2, light=(-2, 0))
    c.shape("M-16,21 V25 H16 V21 Z", P.RED, sw=1.8, light=None)
    return _at(c, x, y, k, turn=tilt)


def _whoosh(x: float, y: float, k: float, angle: float) -> str:
    """Three short parallel motion strokes centred at (x, y), along `angle` degrees: a thing has just shot off
    that way."""
    c = Canvas()
    for off, length in ((-4.5, 7), (0, 10), (4.5, 7)):
        c.line(f"M{n(-length / 2)},{n(off)} h{n(length)}", 1.7)
    return _at(c, x, y, k, turn=angle)


def _inkwell(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.line("M2,-12 Q10,-34 24,-44", 1.4)
    c.shape("M2,-12 Q8,-30 24,-44 Q16,-26 4,-12 Z", P.WHITE, sw=1.2, light=None)
    c.shape("M-9,0 V-8 Q-9,-12 -4,-12 H4 Q9,-12 9,-8 V0 Z", P.PEN, sw=1.5, light=(-1, -1))
    c.shape(rounded_rect_d(-4, -15, 8, 3, 1), P.CHARCOAL, sw=1, light=None)
    return _at(c, x, y, k)


# ============================================================================ 5. the scientific journal
@episode("journal")
def journal(s: Strip) -> None:
    """The Scientific Journal. A long scroll of the house journal unrolls across the room: a context, a
    decision and its consequences, two figures, and at the end "hence it follows" - which the sparrow reads
    out with great feeling, while the cat brings down the stamp "ACCEPTED". Kittens peek over the top edge;
    a loose page has fallen to the floor; the bin is full of drafts that were never accepted."""
    s.indoors()
    k = s.unit
    s.thing(lambda x, y, k: sets.bin_with_paper(x, y, k * 0.5, s.seed), 0.03, 48, 44, name="bin")
    bird = s.cast("sparrow", 0.13, "point", "talk", flip=False, group="reader")
    x0 = bird.right + 22 * k
    if s.h >= 200:                      # room over the sparrow's head for what he reads out
        x0 = max(x0, (bird.left + bird.right) / 2 + (sets.letter_width(s.word("reads"), 11) + 18) / 2 + 12 * k + 10)
    # The cat stands in front of the scroll's right roll; it has just brought the stamp down on the last page and
    # swung it up again: the fresh imprint is beside it, a pair of motion strokes between the two.
    kc = _height(s, "cat") / 310
    cat = s.cast("cat", _frac(s, s.x(0.97) - 40 * kc), "present", "smile", flip=True, mark="ok", group="journal")
    gx, gy, _ = _palm_on_strip(cat, "present")
    s.put(cat.bottom + 0.5, _stamp(gx, gy, k, STAMP_TILT) + _fist(cat, "present"), None, group=cat.group)
    a = math.radians(STAMP_TILT)
    face = (gx + (-16 * math.cos(a) - 25 * math.sin(a)) * k, gy + (-16 * math.sin(a) + 25 * math.cos(a)) * k)
    x1 = cat.left + 40 * kc
    y = s.feet(x0)
    words = {key: s.word(key) for key in ("journal", "ctx", "dec", "cons", "stamp")}
    art, peeks = _journal(x0, x1, y, k, words, face[0] - 9 * k)
    s.put(cat.bottom + 0.4, _whoosh(face[0] - 3 * k, face[1] + 6 * k, k, -40), None, group=cat.group)
    colors = (P.CHARCOAL, P.ORANGE, P.METAL_DARK)
    heads = "".join(_peeking_kitten(px, y - 80 * k, k * 0.8, colors[i % len(colors)], mirror=i % 2 == 1)
                    for i, px in enumerate(peeks[::2][:3]))
    s.put(y - 1, art + heads, [(x0 - 10 * k, y - 100 * k, x1 + 10 * k, y)], "journal")
    page_x = s.x(0.42)
    py = s.feet(page_x, 1.0)
    s.put(py, sets.loose_page(page_x, py - 7 * k, k * 0.3), (page_x - 8 * k, py - 14 * k, page_x + 8 * k, py), "page")
    s.thing(lambda x, y, k: _inkwell(x, y, k * 0.5), 0.66, 16, 24, nearer=1.0, name="ink")
    s.say(bird, s.word("reads"), size=11, prefer="above")


# ============================================================================ props: spot the differences
BOARD_W, BOARD_H, LEDGE = 104, 74, 30          # the painting and the height of the easel's ledge, at k = 1

# The five differences between the two paintings, in the painting's own units (origin at its bottom middle):
# (x, y, ring radius). Each is drawn from this table and ringed from it, so a ring always sits on its change.
DIFFERENCES = {
    "apple": (-32, -51, 7.5),       # the apple on the fridge's top shelf: red, then green
    "cake": (-6, -35, 10.5),        # the cake in the cat's paws: pink with three candles, then chocolate with one
    "window": (36, -56, 11),        # the window: a sunny day, then night with the moon
    "clock": (36, -33, 7.5),        # the clock under it: there, then gone
    "bowl": (37, -10, 8.5),         # the cat's bowl on the floor: blue, then red
}


def _easel(x: float, y: float, k: float, w: float, board_bottom: float, mast: float = 0) -> str:
    """A wooden easel whose ledge is `board_bottom` above the floor, for a board `w` wide; its middle mast rises
    `mast` above the floor (0: hidden behind the board), its tip capped, for a banner's cord."""
    c = Canvas()
    hw = w / 2
    c.line(f"M{n(-hw * 0.6)},0 L{n(-hw * 0.3)},{n(-board_bottom - 30)} M{n(hw * 0.6)},0 L{n(hw * 0.3)},"
           f"{n(-board_bottom - 30)}", 3.6, P.WOOD_DARK)
    top = -max(mast, board_bottom + 30)
    c.shape(f"M-2.2,4 V{n(top)} H2.2 V4 Z", P.WOOD, sw=1.4, light=(-1, 0))
    if mast:
        c.shape(ellipse_d(0, top - 1, 3.4, 3.4), P.WOOD_DARK, sw=1.2, light=None)
    c.shape(rounded_rect_d(-hw * 0.7, -board_bottom, w * 0.7, 5, 2), P.WOOD, sw=1.6, light=None)
    return _at(c, x, y, k)


def _fridge_picture(x: float, y: float, k: float, variant: int) -> str:
    """A painting of the cat taking a cake out of the fridge, in a wooden frame; variant 1 differs from 0 in the
    five things listed in DIFFERENCES. The origin is the bottom middle of the frame."""
    c = Canvas()
    w, h = BOARD_W, BOARD_H
    hw = w / 2
    c.shape(f"M{-hw},0 V{-h} H{hw} V0 Z", P.WOOD_DARK, sw=1.8, light=None)
    clip = c.shape(f"M{-hw + 4},-4 V{-h + 4} H{hw - 4} V-4 Z", lighten(P.YELLOW, 0.6), sw=1.2, light=None, clip=True)
    inner = Canvas()
    inner.add(f'<rect x="{-hw}" y="-17" width="{w}" height="17" fill="{P.FLOOR}"/>')
    inner.line(f"M{-hw},-17 H{hw}", 1.2)
    # The fridge, open: its door swung to the left, the light inside on two shelves.
    fx = -32
    inner.shape(f"M{fx - 15},-12 V{-h + 8} H{fx + 15} V-12 Z", P.WHITE, sw=1.4, light=(-1, -1), shade_k=0.92)
    inner.add(f'<path d="M{fx - 12},-15 V{-h + 11} H{fx + 12} V-15 Z" fill="{lighten(P.SKY, 0.3)}" '
              f'stroke="{INK}" stroke-width=".8"/>')
    for sy in (-28, -44):
        inner.line(f"M{fx - 12},{sy} h24", 1)
    inner.shape(f"M{fx - 15},-12 L{fx - 22},-15 L{fx - 22},{-h + 11} L{fx - 15},{-h + 8} Z", P.WHITE, sw=1.2,
                light=None)
    inner.shape(f"M{fx + 2},-28 v-9 h6 v9 Z", P.WHITE, sw=0.9, light=None)                 # a carton of milk
    inner.shape(f"M{fx + 2},-37 l3,-3 l3,3 Z", P.BLUE, sw=0.8, light=None)
    ax, ay, _ = DIFFERENCES["apple"]
    inner.shape(f"M{ax},{ay + 4.5} C{ax - 6},{ay + 5} {ax - 6},{ay - 3} {ax - 2},{ay - 3.5} Q{ax},{ay - 2.5} "
                f"{ax + 2},{ay - 3.5} C{ax + 6},{ay - 3} {ax + 6},{ay + 5} {ax},{ay + 4.5} Z",
                P.RED if variant == 0 else P.GREEN, sw=1, light=(-1, -1))
    inner.line(f"M{ax},{ay - 3} q1,-3 3,-4", 1, P.WOOD_DARK)
    # The window: day, then night.
    wx, wy, _ = DIFFERENCES["window"]
    sky = P.SKY if variant == 0 else darken(P.BLUE, 0.7)
    inner.add(f'<rect x="{wx - 8}" y="{wy - 8}" width="16" height="16" fill="{sky}" stroke="{INK}" '
              f'stroke-width="1.2"/>')
    if variant == 0:
        inner.add(f'<circle cx="{wx + 3}" cy="{wy - 3}" r="3.2" fill="{P.SUN}" stroke="{INK}" stroke-width=".7"/>')
    else:
        inner.add(f'<path d="M{wx + 4},{wy - 6} a4,4 0 1 0 0,7 a3,3 0 1 1 0,-7 Z" fill="{P.YELLOW_PALE}" '
                  f'stroke="{INK}" stroke-width=".7"/>')
    inner.line(f"M{wx},{wy - 8} V{wy + 8} M{wx - 8},{wy} H{wx + 8}", 1.2, P.WHITE)
    inner.line(f"M{wx},{wy - 8} V{wy + 8} M{wx - 8},{wy} H{wx + 8}", 0.5)
    # The clock (only on the first) and the cat's bowl, its colour changed.
    cx, cy, _ = DIFFERENCES["clock"]
    if variant == 0:
        inner.add(f'<circle cx="{cx}" cy="{cy}" r="4.6" fill="{P.CARD}" stroke="{INK}" stroke-width="1.1"/>')
        inner.line(f"M{cx},{cy} v-3 M{cx},{cy} h2.4", 0.8)
    bx, by, _ = DIFFERENCES["bowl"]
    inner.shape(f"M{bx - 7},{by - 2} Q{bx},{by - 4} {bx + 7},{by - 2} L{bx + 5},{by + 3} H{bx - 5} Z",
                P.BLUE if variant == 0 else P.RED, sw=1, light=None)
    inner.add(f'<ellipse cx="{bx}" cy="{by - 2}" rx="7" ry="1.6" fill="{P.CREAM}" stroke="{INK}" '
              f'stroke-width=".7"/>')
    # The cat with the cake.
    inner.add(draw_actor("cat", 11, -8, h * 0.95, "present", "smile", flip=True, shadow=False))
    kx, ky, _ = DIFFERENCES["cake"]
    sponge = P.PINK_PALE if variant == 0 else P.WOOD
    inner.shape(f"M{kx - 7},{ky + 5} Q{kx - 9},{ky + 9} {kx},{ky + 9} Q{kx + 9},{ky + 9} {kx + 7},{ky + 5} Z",
                P.WHITE, sw=0.9, light=None)                                                      # the plate
    inner.shape(f"M{kx - 8},{ky + 5} V{ky - 2} H{kx + 8} V{ky + 5} Z", sponge, sw=1, light=(-1, 0))
    inner.line(f"M{kx - 8},{ky + 1.5} h16", 1.3, P.RED if variant == 0 else P.CREAM)
    for cxi in ((kx - 4, kx, kx + 4) if variant == 0 else (kx,)):
        inner.line(f"M{cxi},{ky - 2} v-5", 1.4, P.BLUE)
        inner.add(f'<path d="M{cxi},{ky - 10} q2,2 0,3 q-2,-1 0,-3 Z" fill="{P.SUN}" stroke="{INK}" '
                  f'stroke-width=".4"/>')
    c.add(f'<g clip-path="url(#{clip})">{inner.render()}</g>')
    return _at(c, x, y, k)


def _circles(x: float, y: float, k: float) -> str:
    """Red pencil rings round the differences found, on the painting whose bottom middle is at (x, y)."""
    c = Canvas()
    for i, (fx, fy, r) in enumerate(DIFFERENCES.values()):
        cx, cy = x + fx * k, y + fy * k
        rx, ry = r * 1.1 * k, r * 0.95 * k
        # a pencil ring drawn by hand: once round, its end running on a little past its start
        d = (f"M{n(cx + rx)},{n(cy)} A{n(rx)},{n(ry)} 0 1 1 {n(cx - rx)},{n(cy)} A{n(rx)},{n(ry)} 0 1 1 "
             f"{n(cx + rx)},{n(cy)} Q{n(cx + rx * 1.02)},{n(cy - ry * 0.5)} {n(cx + rx * 0.72)},{n(cy - ry * 0.9)}")
        c.add(f'<path d="{d}" fill="none" stroke="{P.RED}" stroke-width="{n(1.5 * k)}" stroke-linecap="round" '
              f'transform="rotate({-20 + i * 23} {n(cx)} {n(cy)})"/>')
    return c.render()


def _brush_to(gx: float, gy: float, tx: float, ty: float, k: float, color: str = P.BLUE) -> str:
    """A paintbrush gripped at (gx, gy) whose wet tip touches (tx, ty): the handle runs on a little behind the
    grip, a metal ferrule, the bristles."""
    a = math.atan2(ty - gy, tx - gx)
    length = math.hypot(tx - gx, ty - gy) / k
    g = Canvas()
    g.line(f"M-8,0 L{n(length - 9)},0", 3.4, P.WOOD)
    g.line(f"M-8,0 L{n(length - 9)},0", 0.8, P.WOOD_DARK, 0.4)
    g.shape(f"M{n(length - 11)},-2 H{n(length - 6)} V2 H{n(length - 11)} Z", P.METAL, sw=0.9, light=None)
    g.shape(f"M{n(length - 6)},-2.3 Q{n(length - 1.5)},-2 {n(length)},0 Q{n(length - 1.5)},2 {n(length - 6)},2.3 Z",
            color, sw=0.9, light=None)
    return f'<g transform="translate({n(gx)},{n(gy)}) rotate({n(math.degrees(a))}) scale({n(k)})">{g.render()}</g>'


def _palette(x: float, y: float, k: float = 1.0, mirror: bool = False) -> str:
    """An artist's palette held by its thumb hole at (x, y): a kidney of pale wood, its notch beside the hole,
    dabs of paint round the rim, each with a glint."""
    c = Canvas()
    c.shape("M4,-6 C-2,-16 -26,-18 -38,-8 C-48,0 -42,14 -26,16 C-14,18 -2,14 2,8 C4,4 0,2 -2,1 "
            "C-6,-1 -2,-5 4,-6 Z", P.WOOD_PALE, sw=1.5, light=(-2, -2), shade_k=0.86)
    c.add(f'<ellipse cx="-6" cy="-6" rx="3.6" ry="3" fill="{P.PAPER}" stroke="{INK}" stroke-width="1.2"/>')
    for px, py, col in ((-16, -9, P.RED), (-27, -7, P.YELLOW), (-35, 1, P.BLUE), (-31, 9, P.GREEN),
                        (-19, 10, P.WHITE), (-9, 8, P.ORANGE)):
        c.shape(f"M{px - 3.4},{py} C{px - 3.6},{py - 3.4} {px + 3.2},{py - 3.8} {px + 3.4},{py} "
                f"C{px + 3},{py + 3} {px - 3},{py + 3.2} {px - 3.4},{py} Z", col, sw=0.9, light=None)
        c.add(f'<circle cx="{px - 1.2}" cy="{py - 1.2}" r=".9" fill="{P.WHITE}" opacity=".85"/>')
    return _at(c, x, y, k, mirror)


def _banner(x0: float, x1: float, top: float, k: float, text: str) -> tuple[str, float]:
    """A cloth banner tied by its two upper corners between two mast tips at (x0, top) and (x1, top): a cream
    band with a red hem and the title on it. Returns the drawing and its bottom."""
    size = max(11.5, 10.5 * k)
    bh = size * 1.7
    inset = 5 * k
    bx0, bx1 = x0 + inset, x1 - inset
    by = top + 4 * k
    c = Canvas()
    c.line(f"M{n(x0)},{n(top)} L{n(bx0)},{n(by)} M{n(x1)},{n(top)} L{n(bx1)},{n(by)}", 1.2)
    sag = 3 * k
    c.shape(f"M{n(bx0)},{n(by)} Q{n((bx0 + bx1) / 2)},{n(by + sag)} {n(bx1)},{n(by)} V{n(by + bh)} "
            f"Q{n((bx0 + bx1) / 2)},{n(by + bh + sag)} {n(bx0)},{n(by + bh)} Z", P.CREAM, sw=1.6, light=None)
    c.line(f"M{n(bx0)},{n(by + bh - 2.4 * k)} Q{n((bx0 + bx1) / 2)},{n(by + bh + sag - 2.4 * k)} {n(bx1)},"
           f"{n(by + bh - 2.4 * k)}", 1.6 * k, P.RED)
    for ex in (bx0, bx1):
        c.add(f'<circle cx="{n(ex)}" cy="{n(by)}" r="{n(1.6 * k)}" fill="{P.METAL_LIGHT}" stroke="{INK}" '
              f'stroke-width=".8"/>')
    sets.fit_label(c, (bx0 + bx1) / 2, by + sag * 0.6 + bh * 0.5 + size * 0.34, text, size,
                   bx1 - bx0 - size * 1.2, P.RED)
    return c.render(), by + bh + sag


def _plank(x0: float, x1: float, y: float, size: float, text: str) -> tuple[str, float]:
    """A painted wooden plank lying across two frames whose tops are at y, its ends over the middles x0 and x1;
    the title on it. Returns the drawing and its top."""
    bh = size * 1.6
    c = Canvas()
    c.shape(rounded_rect_d(x0, y - bh, x1 - x0, bh, 2), P.CREAM, sw=1.6, light=None)
    c.line(f"M{n(x0 + 2)},{n(y - 2.2)} H{n(x1 - 2)}", 1.4, P.RED)
    for ex in (x0 + size * 0.5, x1 - size * 0.5):
        c.add(f'<circle cx="{n(ex)}" cy="{n(y - bh / 2)}" r="1.5" fill="{P.METAL_DARK}" stroke="{INK}" '
              f'stroke-width=".6"/>')
    sets.fit_label(c, (x0 + x1) / 2, y - bh / 2 + size * 0.34, text, size, x1 - x0 - size * 2.4, P.RED)
    return c.render(), y - bh


# ============================================================================ 6. spot the ten differences
@episode("ten_differences")
def ten_differences(s: Strip) -> None:
    """Spot ten differences. Two paintings stand on easels under a banner: the cat taking a cake out of the
    fridge. The right one differs in five things - the apple, the cake, the window, the clock, the bowl - and the
    caterpillar has rung each in red pencil, her magnifier now over the bowl. On the left the sparrow, palette in
    one wing, quietly adds one more difference with his brush. The real cat, on the right, has the real cake."""
    s.indoors()
    k = s.unit
    pk = k * 1.2                                  # the paintings a little larger than life, for their details
    pw, ph, ledge = BOARD_W * pk, BOARD_H * pk, LEDGE * k
    # The sparrow stands left of the first easel, his wing tip a brush's length from its canvas.
    pose = "present"
    ks = _height(s, "sparrow") / 190
    sp = module("sparrow")
    gx, gy = sp.hand_point(pose, "right")
    x = max(s.x(0.25), s.lo + (gx - sp.CENTER_X + 100) * ks + 40 * k + pw / 2)
    y = s.feet(x)
    low = y - ledge                                                           # the paintings' bottom edge
    target = (x - pw / 2 + 16 * pk, low - 8 * pk)                             # on the painted floor, by the fridge
    bird_x = target[0] - 26 * k - (gx - sp.CENTER_X) * ks
    bird = s.cast("sparrow", _frac(s, bird_x), pose, "wink", flip=False)
    # The two easels and the banner tied between their masts.
    x2 = max(s.x(0.58), x + pw + 54 * k)
    title = s.word("title")
    size = max(11.5, 10.5 * k)
    tip = low - ph - size * 1.7 - 16 * k                                      # the masts' tips
    banner = tip > s.h * 0.17
    for variant, px in enumerate((x, x2)):
        art = (_easel(px, y, k, pw / k, LEDGE, (y - tip) / k if banner else 0)
               + _fridge_picture(px, low, pk, variant))
        if variant:
            art += _circles(px, low, pk)
        s.put(y - 1, art, (px - pw / 2, low - ph - 2 * k, px + pw / 2, y), f"easel{variant}", group="easels")
        if banner:
            s.put(y - 1, "", (px - 4 * k, tip - 4 * k, px + 4 * k, low - ph - 2 * k), f"mast{variant}",
                  group="easels")
    if banner:
        art, bottom = _banner(x, x2, tip, k, title)
        s.put(y - 0.5, art, (x + 4 * k, tip, x2 - 4 * k, bottom), "banner", group="easels")
    elif low - ph - size * 1.8 > s.h * 0.15:
        # No room for masts: the title is a plank laid across the tops of both frames.
        art, top = _plank(x, x2, low - ph, size, title)
        s.put(y - 0.5, art, (x, top, x2, low - ph), "banner", group="easels")
    # The sparrow: the brush from his right wing to the canvas, a new blue dab where it touches; the palette in
    # his left wing.
    hx, hy = s.hand(bird, pose, False)
    s.put(bird.bottom + 0.5, f'<ellipse cx="{n(target[0] + 1 * k)}" cy="{n(target[1])}" rx="{n(3.4 * k)}" '
          f'ry="{n(2.4 * k)}" fill="{P.BLUE}" stroke="{INK}" stroke-width=".7"/>'
          + _brush_to(hx, hy, target[0], target[1], k), None, group=bird.group)
    s.in_hand(bird, pose, False, lambda x, y, kk: _palette(x, y, kk * 0.8), side="left")
    # The caterpillar right of the second painting, her magnifier over the bowl.
    half = _height(s, "caterpillar") * 0.36
    cat = s.cast("caterpillar", _frac(s, x2 + pw / 2 + half + 8 * k), "point", "talk", flip=True,
                 mark="!", group="checker")
    bx, by, br = DIFFERENCES["bowl"]
    lens = (x2 + bx * pk, low + by * pk)
    s.in_hand(cat, "point", True, lambda hx, hy, kk: _held_magnifier((hx, hy), lens, (br + 3.5) * pk))
    real = s.cast("cat", 0.94, "present", "wink", flip=True, group="real")
    s.in_hand(real, "present", True, lambda x, y, k: _cake_slice(x, y - 1.5 * k, k * 1.1))


def _cake_slice(x: float, y: float, k: float) -> str:
    """The real cake on a plate, one slice gone; drawn at k = 1 for a character 100 tall."""
    c = Canvas()
    c.shape(ellipse_d(0, 0, 14, 3), P.WHITE, sw=1.2, light=None)
    c.shape("M-10,-1 V-10 H4 L10,-6 V-1 Z", P.PINK_PALE, sw=1.2, light=None)
    c.line("M-10,-6 H6", 1.4, P.RED)
    c.line("M-4,-10 v-5 M2,-10 v-5", 1.2, P.BLUE)
    return _at(c, x, y, k)


# ============================================================================ props: the crossword
def _crossword(x: float, y: float, cell: float, rows: list[str], wrong: tuple[int, int]) -> str:
    """A crossword board whose bottom middle is at (x, y), drawn at page size: `rows` give the letters ('.' an
    empty square of the board), each cell `cell` units; the `wrong` cell gets a red cross over its letter."""
    c = Canvas()
    cols = max(len(r) for r in rows)
    w, h = cols * cell, len(rows) * cell
    pad = cell * 0.5
    c.shape(rounded_rect_d(x - w / 2 - pad, y - h - pad * 2, w + pad * 2, h + pad * 2, 3), P.CARD, sw=1.8,
            light=(-1, -1), shade_k=0.95)
    size = cell * 0.68
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == ".":
                continue
            cx, cy = x - w / 2 + i * cell, y - h - pad + j * cell
            c.add(f'<rect x="{n(cx)}" y="{n(cy)}" width="{n(cell)}" height="{n(cell)}" fill="{P.WHITE}" '
                  f'stroke="{INK}" stroke-width="1.3"/>')
            if (j, i) == wrong:
                m = cell * 0.12
                c.line(f"M{n(cx + m)},{n(cy + m)} L{n(cx + cell - m)},{n(cy + cell - m)} M{n(cx + cell - m)},"
                       f"{n(cy + m)} L{n(cx + m)},{n(cy + cell - m)}", 2.4, P.RED)
            _label(c, cx + cell / 2, cy + cell / 2 + size * 0.36, ch, size, P.PEN)
    return c.render()


def _pencil_glass(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    for dx, turn, col in ((-4, -14, P.RED), (0, 4, P.YELLOW), (5, 16, P.BLUE), (2, -4, P.GREEN)):
        g = Canvas()
        g.shape("M-2,0 V-30 H2 V0 Z", col, sw=1, light=None)
        g.shape("M-2,-30 L0,-36 L2,-30 Z", P.WOOD_PALE, sw=0.8, light=None)
        c.add(f'<g transform="translate({dx},-4) rotate({turn})">{g.render()}</g>')
    c.shape("M-9,0 L-10,-20 H10 L9,0 Z", lighten(P.WATER_LIGHT, 0.4), sw=1.4, light=None)
    c.line("M-6,-16 V-4", 1.4, P.WHITE, 0.8)
    return _at(c, x, y, k)


def _books(x: float, y: float, k: float = 1.0) -> str:
    """A stack of three fat books: a dictionary on top."""
    c = Canvas()
    for i, (col, w) in enumerate(((P.BLUE, 40), (P.RED, 36), (P.GREEN, 38))):
        yy = -i * 9
        c.shape(rounded_rect_d(-w / 2 + i * 2, yy - 9, w, 9, 1.6), col, sw=1.4, light=None)
        c.path(f"M{n(w / 2 + i * 2 - 4)},{yy - 8} V{yy - 1} H{n(-w / 2 + i * 2 + 2)}", P.CARD, 0.8)
    return _at(c, x, y, k)


def _eraser(x: float, y: float, k: float = 1.0) -> str:
    """A big pink eraser on the floor with a few crumbs rubbed off it; the origin is the middle of its foot."""
    c = Canvas()
    c.shape("M-10,0 V-12 L-6,-16 H10 V0 Z", P.PINK, sw=1.4, light=(-1, -1))
    c.shape("M-10,-12 H10 V-6 H-10 Z", P.BLUE, sw=1, light=None)
    for dx in (-16, -20, -14):
        c.dot(dx, -2 + dx * 0.05, 1.1, P.PINK)
    return _at(c, x, y, k)


def _globe(x: float, y: float, k: float = 1.0) -> str:
    """A school globe on a tall stand, 64 high."""
    c = Canvas()
    c.line("M0,0 V-30 M-12,0 H12", 3, P.WOOD_DARK)
    c.add(doodle_at("globe", 0, -26, 40))
    return _at(c, x, y, k)


# ============================================================================ 7. the crossword
@episode("crossword")
def crossword(s: Strip) -> None:
    """The crossword. The agent fills in a big crossword on an easel, quick as anything; the caterpillar
    checks every word against the answer sheet - and one letter gets a red cross: CAT where CODE should be
    (one letter apart in Russian). Pencils in a glass, a stack of dictionaries, a big eraser on the
    floor, and the cat with an idea about that crossed-out letter."""
    s.indoors()
    k = s.unit
    agent = s.cast("agent", 0.08, "point", "smile", flip=False, group="board")
    rows = s.word("grid").split("|")
    cols = max(len(r) for r in rows)
    wrong = (int(s.word("wrong_row")), int(s.word("wrong_col")))
    cell = max(17.0, 20 * k)
    gw, gh = (cols + 1) * cell, (len(rows) + 1) * cell
    ledge = 26 * k
    bx = agent.right + gw / 2 + 10 * k
    by = s.feet(bx)
    s.put(by - 1, _easel(bx, by, 1, gw, ledge) + _crossword(bx, by - ledge, cell, rows, wrong),
          (bx - gw / 2, by - ledge - gh - 4, bx + gw / 2, by), "board")
    # The agent's pointer, held in its outstretched hand, touches the board's first column.
    hx, hy = _palm(agent, "point", False, reach=0.1)
    tip_x, tip_y = bx - gw / 2 + cell * 0.3, by - ledge - gh * 0.5
    a = math.atan2(tip_y - hy, tip_x - hx)
    s.put(agent.bottom - 0.5, _stick(hx - math.cos(a) * 8 * k, hy - math.sin(a) * 8 * k, tip_x, tip_y, 2.4 * k,
                                     P.YELLOW), None, group="board")
    half = _height(s, "caterpillar") * 0.36
    s.cast("caterpillar", _frac(s, bx + gw / 2 + half + 12 * k), "write", "worry", flip=True, mark="!")
    s.thing(lambda x, y, k: _eraser(x, y, k), 0.5, 44, 18, nearer=0.85, name="eraser")
    s.thing(lambda x, y, k: things.kitchen_table(x, y, k * 0.8, 70, P.WOOD_LIGHT, None)
            + _pencil_glass(x - 14 * k, y - 38 * k, k * 0.9) + _books(x + 12 * k, y - 38 * k, k * 0.7),
            0.63, 62, 66, name="table")
    s.cast("cat", 0.8, "think", "smile", flip=True, mark="idea")
    s.thing(lambda x, y, k: _globe(x, y, k), 0.96, 34, 64, name="globe")


# ============================================================================ props: the board game
def _board_path(x0: float, x1: float, top: float, bottom: float, start: str, finish: str,
                back_at: float) -> tuple[str, list, int]:
    """A long board-game track of squares lying on the floor from x0 to x1: special circles and a blue
    triangle on the square nearest `back_at`, START and FINISH at the ends. Returns the drawing, the centres of the
    squares and the triangle's square."""
    c = Canvas()
    h = bottom - top
    size = max(11.5, h * 0.36)
    ends = [max(h * 1.25, sets.letter_width(word, size) * 1.3 + 12) for word in (start, finish)]
    sq = max(14.0, h * 1.25)
    count = max(8, int((x1 - x0 - sum(ends)) / sq) + 2)
    sq = (x1 - x0 - sum(ends)) / (count - 2)
    widths = [ends[0]] + [sq] * (count - 2) + [ends[1]]
    skew = h * 0.35
    centres = []
    lefts = [x0 + sum(widths[:i]) for i in range(count)]
    tri = min(range(1, count - 1), key=lambda i: abs(lefts[i] + sq / 2 - back_at))
    specials = {i: ("skip", "extra")[(i // 3) % 2] for i in range(2, count - 1, 3) if abs(i - tri) > 1}
    specials[tri] = "back"
    for i in range(count):
        a, wi = lefts[i], widths[i]
        fill = (P.CREAM, P.YELLOW_PALE)[i % 2]
        if i == 0:
            fill = P.GREEN
        elif i == count - 1:
            fill = P.RED
        c.shape(f"M{n(a + skew)},{n(top)} H{n(a + wi + skew)} L{n(a + wi)},{n(bottom)} H{n(a)} Z", fill, sw=1.4,
                light=None)
        cx, cy = a + wi / 2 + skew / 2, (top + bottom) / 2
        centres.append((cx, cy))
        kind = specials.get(i) if 0 < i < count - 1 else None
        r = h * 0.3
        if kind == "skip":
            c.add(f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(r * 1.3)}" ry="{n(r)}" fill="{P.RED}" stroke="{INK}" '
                  f'stroke-width="1"/>')
        elif kind == "extra":
            c.add(f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(r * 1.3)}" ry="{n(r)}" fill="{P.GREEN}" '
                  f'stroke="{INK}" stroke-width="1"/>')
        elif kind == "back":
            c.add(f'<path d="M{n(cx - r * 1.4)},{n(cy + r)} L{n(cx)},{n(cy - r)} L{n(cx + r * 1.4)},{n(cy + r)} Z" '
                  f'fill="{P.BLUE}" stroke="{INK}" stroke-width="1"/>')
    for (cx, cy), word, wi in ((centres[0], start, widths[0]), (centres[-1], finish, widths[-1])):
        sets.fit_label(c, cx, cy + size * 0.36, word, size, (wi - 12) / 1.3, P.WHITE)
    c.line(f"M{n(x0 + skew)},{n(top)} H{n(x1 + skew)} L{n(x1)},{n(bottom)} H{n(x0)} Z", 2)
    return c.render(), centres, tri


def _pawn(x: float, y: float, k: float, color: str) -> str:
    """A game pawn, 20 high."""
    c = Canvas()
    c.shape("M-7,0 Q-8,-4 -4,-6 L-2,-12 H2 L4,-6 Q8,-4 7,0 Z", color, sw=1.3, light=(-1, -1))
    c.shape(ellipse_d(0, -15, 4.6, 4.6), color, sw=1.3, light=(-1, -1))
    return _at(c, x, y, k)


def _die(x: float, y: float, k: float = 1.0) -> str:
    """A big die showing six, 34 high."""
    c = Canvas()
    c.shape("M-16,0 V-26 H12 V0 Z", P.WHITE, sw=1.8, light=(-1, -1), shade_k=0.92)
    c.shape("M-16,-26 L-10,-32 H18 L12,-26 Z", P.CARD, sw=1.6, light=None)
    c.shape("M12,0 V-26 L18,-32 V-6 Z", darken(P.WHITE, 0.85), sw=1.6, light=None)
    for dx in (-9, 5):
        for dy in (-20, -13, -6):
            c.dot(dx, dy, 2.2, P.RED)
    c.dot(4, -29, 1.8)
    return _at(c, x, y, k)


# ============================================================================ 8. the board game
@episode("board_game")
def board_game(s: Strip) -> None:
    """The board game. A long track of squares runs across the playroom floor: red circles skip a turn, green ones
    give another, a blue triangle sends you back to the start. The agent has landed on the blue triangle and
    trudges all the way back to START, as the rules say; the cat rolls the big die, the sparrow cheers his extra
    turn."""
    s.indoors()
    k = s.unit
    # Back row.
    cat = s.cast("cat", 0.05, "point", "talk", flip=False)
    s.thing(lambda x, y, k: _die(x, y, k * 1.2), _frac(s, cat.right + 26 * k), 40, 42, name="die")
    s.cast("caterpillar", 0.3, "think", "smile", flip=False, mark="?")
    s.cast("sparrow", 0.88, "cheer", "smile", flip=True, mark="!")
    # The board along the front.
    top = s.feet(0) + 5
    bottom = min(s.h - 5, top + 36 * k)
    x0, x1 = s.lo, s.hi - (bottom - top) * 0.4
    art, squares, tri_i = _board_path(x0, x1, top, bottom, s.word("start"), s.word("finish"), s.x(0.56))
    s.put(top, art, [(x0, top, x1 + (bottom - top) * 0.4, bottom)], "board")
    # The agent walks back over the board, along a dotted line from the blue triangle.
    tri = squares[tri_i]
    ax = tri[0] - 40 * k
    agent = s.actor("agent", ax, tri[1] + 2, "walk", "worry", flip=True, tall=s.tall, group="board")
    s.put(agent.bottom - 0.5, f'<path d="M{n(agent.right - 6 * k)},{n(tri[1])} H{n(tri[0] - 10 * k)}" '
          f'stroke="{INK}" stroke-width="1.6" stroke-dasharray="3 4" stroke-linecap="round"/>', None, group="board")
    ay = agent.top + (agent.bottom - agent.top) * 0.3
    s.put(s.h, _arrow(((agent.left + 2 * k, ay), (agent.left - 12 * k, ay - 14 * k), (agent.left - 28 * k, ay)),
                      2.6 * k, P.BLUE), (agent.left - 32 * k, ay - 12 * k, agent.left + 4 * k, ay + 6 * k), "arrow",
          group="board")
    for i, col in ((len(squares) - 5, P.RED), (len(squares) - 8, P.GREEN), (2, P.YELLOW)):
        px, py = squares[i][0], squares[i][1] + 3
        box = (px - 8 * k, py - 21 * k, px + 8 * k, py)
        if i != tri_i and not any(b.hits(box, 4) for b in s.boxes if b.name != "board"):
            s.put(py, _pawn(px, py, k, col), box, f"pawn{i}", group="board")


# ============================================================================ props: the fight over the keyboard
def _dust_cloud(x: float, y: float, k: float) -> str:
    """A rolling cloud of dust with the fight still going on inside it: a tail, a foot, a wing; 120 wide, 60
    high."""
    c = Canvas()
    puffs = ((-44, -16, 18), (-24, -30, 22), (2, -36, 24), (28, -28, 21), (46, -14, 16), (-8, -14, 22),
             (20, -10, 20))
    c.line("M-50,-30 q-14,-8 -18,4", 3.6, P.CATERPILLAR)            # the caterpillar's tail
    c.line("M54,-36 l14,-10 l-2,8 l10,-4", 2.4, P.FEATHER)          # a wing tip
    for px, py, r in puffs:
        c.shape(ellipse_d(px, py, r, r * 0.8), lighten(P.BEIGE_DARK, 0.2), sw=1.8, light=(-3, -3), shade_k=0.88)
    for px, py in ((-30, -32), (8, -42), (34, -24), (-6, -18)):
        c.line(f"M{px - 4},{py} l8,0 M{px},{py - 4} l0,8", 1.4, P.RED)    # little stars of the scuffle
    c.shape("M-22,-2 q-4,8 4,8 q6,0 4,-6 Z", P.ORANGE_DARK, sw=1.2, light=None)    # a foot sticking out
    return _at(c, x, y, k)


def _flying(x: float, y: float, k: float, kind: str, turn: float) -> str:
    """Something flying out of the fight with speed lines behind it."""
    c = Canvas()
    if kind == "floppy":
        c.add(things.floppy(0, 0, 1, (P.RED, P.BLUE, P.CHARCOAL)[int(abs(turn)) % 3], turn))
    else:
        c.add(doodle_at(kind, 0, 0, 36, turn))
    c.line("M14,-6 h10 M14,-12 h14 M14,0 h8", 1.1, opacity=0.6)
    return _at(c, x, y, k)


# ============================================================================ 9. the fight at the keyboard
@episode("keyboard_fight")
def keyboard_fight(s: Strip) -> None:
    """Fighting is not nice. The caterpillar and the sparrow both wanted to type first: the dust cloud of their
    scuffle still rolls over the floor, floppies and a computer mouse flying out of it with a BANG and a BOOM,
    while the cat has raised its paws between the two and says it plainly; the agent walks off with the keyboard
    they were fighting over; the chair lies on its back."""
    s.indoors()
    k = s.unit
    # The desk and the computer with its message: a grown-up's desk, deep enough for a keyboard in front - but the
    # keyboard is gone, the agent has it.
    dx = s.x(0.1)
    dy = s.feet(dx)
    ds = 0.85
    top = dy - 71 * k * ds
    foot = top - 24 * 0.7 * ds * k
    s.put(dy - 1, props.desk(dx, dy, k * ds, 150, depth=24) + props.computer(dx, foot, k * 0.75, lines=3,
                                                                            keyboard=False),
          [(dx - 75 * ds * k, top - 24 * ds * k, dx + 75 * ds * k, dy),
           (dx - 38 * k, foot - 72 * k, dx + 38 * k, foot)], "desk")
    # The cat in the middle, holding them up by the scruff.
    cat = s.cast("cat", 0.42, "cheer", "worry", flip=False, group="fight")
    cat_depth = cat.bottom - 6
    s.items[-1] = (cat_depth, s.items[-1][1], s.items[-1][2])      # the cat stands behind the two
    lx, _ = s.hand(cat, "cheer", False, "left")
    rx, _ = s.hand(cat, "cheer", False, "right")
    ground = s.feet(cat.left, 0.25)
    s.actor("caterpillar", lx - 16 * k, ground, "cheer", "talk", flip=False, tall=s.tall * 0.85, group="fight")
    s.actor("sparrow", rx + 18 * k, ground, "point", "talk", flip=True, tall=s.tall * 0.95, group="fight")
    # The dust cloud behind them, the bangs and what flies out of it.
    cx = (cat.left + cat.right) / 2
    gy = ground + 4
    s.put(ground + 5, f'<g transform="translate({n(cx)},{n(gy)}) scale(1.25,0.42) translate({n(-cx)},{n(-gy)})">'
          + _dust_cloud(cx, gy, k) + "</g>", [(cx - 100 * k, ground - 24 * k, cx + 100 * k, gy)], "cloud",
          group="fight")
    r = max(29.0, 22 * k)
    bangs = ((cx - 82 * k, ground - 64 * k, s.word("bang")), (cx + 88 * k, ground - 70 * k, s.word("boom")))
    for bx, by, word in bangs:
        by = max(r + 2, by)
        s.put(s.h, things.burst(bx, by, r, word), (bx - r, by - r * 0.8, bx + r, by + r * 0.8), f"burst{bx:.0f}",
              group="fight")
    flying = ((cx - 60 * k, ground - 18 * k, "floppy", -30), (cx + 64 * k, ground - 30 * k, "floppy", 25),
              (cx + 76 * k, ground - 4 * k, "mouse", 10))
    for fx, fy, kind, turn in flying:
        s.put(s.h, _flying(fx, fy, k * 0.7, kind, turn), None, group="fight")
    # The toppled chair and the agent walking off with the keyboard.
    s.thing(lambda x, y, k: _toppled_stool(x, y, k), 0.7, 56, 34, nearer=0.2, name="stool")
    agent = s.cast("agent", 0.9, "carry", "smile", flip=False, mark="ok", group="agent")
    s.held(agent, "carry", False, lambda x, y, k: doodle_at("keyboard", x, y + 4 * k, 40 * k))
    s.say(cat, f"{s.word('line1')} {s.word('line2')}", size=11, prefer="above")


def _toppled_stool(x: float, y: float, k: float) -> str:
    """A stool knocked over onto its side, its seat still rocking; 56 wide."""
    c = Canvas()
    c.add(f'<g transform="translate(-6,-16) rotate(-84)">{things.stool(0, 0, 1, P.RED)}</g>')
    c.line("M-30,-30 q-4,6 0,12 M-36,-26 q-3,4 0,8", 1.2, opacity=0.6)
    return _at(c, x, y, k)


# ============================================================================ props: the museum salon
def _binary_painting(x: float, y: float, k: float, w: float, h: float, seed: int) -> str:
    """A huge gilt frame full of ones and noughts; the origin is its bottom middle."""
    import random
    rnd = random.Random(seed)
    c = Canvas()
    hw = w / 2
    c.shape(f"M{-hw},0 V{-h} H{hw} V0 Z", P.AMBER, sw=2.2, light=(-2, -2), shade_k=0.82)
    c.shape(f"M{-hw + 8},-8 V{-h + 8} H{hw - 8} V-8 Z", P.SUN, sw=1.4, light=None)
    for cx, cy in ((-hw + 4, -4), (hw - 4, -4), (-hw + 4, -h + 4), (hw - 4, -h + 4)):
        c.add(f'<circle cx="{cx}" cy="{cy}" r="6" fill="{P.SUN}" stroke="{INK}" stroke-width="1.4"/>')
    c.shape(f"M{-hw + 13},-13 V{-h + 13} H{hw - 13} V-13 Z", darken(P.CARD, 0.96), sw=1.4, light=None)
    size = max(8.6, 10 / k)                     # never under 10 on the page: fewer, bigger digits
    pad = (h - 26) * 0.14                       # air between the digits and the inner frame on every side
    rows = max(1, int((h - 26 - 2 * pad + size * 0.4) / (size * 1.25)))
    cols = 2
    while sets.letter_width("0" * (cols + 1), size, style="plain") <= w - 26 - 2 * pad:
        cols += 1
    top = -h / 2 - (rows - 1) * size * 1.25 / 2 + size * 0.36
    for j in range(rows):
        line = "".join(rnd.choice("01") for _ in range(cols))
        _label(c, 0, top + j * size * 1.25, line, size, P.PEN, style="plain")
    return _at(c, x, y, k)


def _bust(x: float, y: float, k: float = 1.0) -> str:
    """A plaster bust of the professor on a column: glasses, a moustache, the long hair at the back; 96 high."""
    c = Canvas()
    plaster = lighten(P.STONE, 0.45)
    c.shape("M-14,0 V-46 H14 V0 Z", P.CARD, sw=1.8, light=(-2, 0), shade_k=0.9)
    c.line("M-8,-4 V-42 M0,-4 V-42 M8,-4 V-42", 1, opacity=0.4)
    c.shape(rounded_rect_d(-18, -50, 36, 6, 2), P.STONE, sw=1.6, light=None)
    c.shape(rounded_rect_d(-18, -2, 36, 5, 2), P.STONE, sw=1.6, light=None)
    c.shape("M-20,-50 Q-20,-64 0,-66 Q20,-64 20,-50 Z", plaster, sw=1.8, light=(-2, -1))
    c.shape("M-14,-62 Q-18,-80 -12,-90 L-10,-70 Z M14,-62 Q18,-80 12,-90 L10,-70 Z", plaster, sw=1.6, light=None)
    c.shape(ellipse_d(0, -80, 11, 14), plaster, sw=1.8, light=(-2, -2), shade_k=0.86)
    for ex in (-4.5, 4.5):
        c.add(f'<circle cx="{ex}" cy="-80" r="3.6" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    c.line("M-1,-80 h2", 1)
    c.shape("M-8,-71 Q-4,-75 0,-72 Q4,-75 8,-71 Q4,-68 0,-70 Q-4,-68 -8,-71 Z", plaster, sw=1.2, light=None)
    c.line("M-3,-77 l0,3", 0.9)
    return _at(c, x, y, k)


def _stepladder(x: float, y: float, k: float = 1.0) -> str:
    """A wooden stepladder; its top step is 46 up."""
    c = Canvas()
    c.line("M-16,0 L-6,-50 M16,0 L6,-50 M-6,-50 H6", 3, P.WOOD_DARK)
    for i, yy in enumerate((-14, -30)):
        w = 13 - i * 3.4
        c.line(f"M{-w},{yy} H{w}", 2.6, P.WOOD_DARK)
    c.shape(rounded_rect_d(-10, -50, 20, 5, 1.6), P.WOOD, sw=1.4, light=None)
    return _at(c, x, y, k)


LABEL_SIZE = 11.5     # the lettering of the museum label, on the page


def _museum_label_size(title: str, text: str) -> tuple[float, float]:
    """The museum label's width and height."""
    size = LABEL_SIZE
    w = max(sets.letter_width(title, size), sets.letter_width(text, size * 1.15)) * 1.15 + 14
    return w, size * 2.6 + 8


def _museum_label(x: float, y: float, title: str, text: str) -> str:
    """A museum label drawn at page size, its top left corner at (x, y), with the red pin at its top right corner
    (where the paw holds it)."""
    c = Canvas()
    size = LABEL_SIZE
    w, h = _museum_label_size(title, text)
    c.shape(rounded_rect_d(x, y, w, h, 2), P.WHITE, sw=1.6, light=(-1, -1), shade_k=0.94)
    sets.fit_label(c, x + w / 2, y + 4 + size, title, size, w - 10, P.PEN)
    sets.fit_label(c, x + w / 2, y + 6 + size * 2.3, text, size * 1.15, w - 10)
    c.add(f'<circle cx="{n(x + w - 7)}" cy="{n(y + 5)}" r="2.6" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>')
    return c.render()


# ============================================================================ 10. the binary frame
@episode("binary_frame")
def binary_frame(s: Strip) -> None:
    """A masterpiece in noughts and ones. In the museum salon a huge gilt frame holds nothing but ones and noughts;
    the sparrow and the caterpillar stare at it, baffled, next to a plaster bust of the professor. The cat has
    climbed a stepladder to pin a small label beside it that says in plain words what it means. The rope keeps
    visitors back."""
    s.indoors()
    k = s.unit
    s.thing(lambda x, y, k: _bust(x, y, k), 0.03, 44, 96, name="bust")
    s.cast("sparrow", 0.13, "shrug", "surprise", flip=False, mark="?")
    s.cast("caterpillar", 0.24, "think", "worry", flip=False)
    fw, fh = 190, 92
    fx = s.x(0.46)
    fb = s.base - 6
    s.put(2, _binary_painting(fx, fb, k, fw, fh, s.seed), (fx - fw * k / 2, fb - fh * k, fx + fw * k / 2, fb), "frame")
    sy = s.feet(fx, 0.95)
    span = max(30.0, things.sign_size(s.word("rope"), k * 1.2, 1000)[0] / 2 + 8)   # the sign never squeezed
    s.put(sy, things.stanchion_sign(fx, sy, k * 1.2, s.word("rope"), span),
          (fx - (span + 10) * 1.2 * k, sy - 44 * k, fx + (span + 10) * 1.2 * k, sy), "rope")
    # The cat on the stepladder pins the label to the wall right of the frame, its paw on the label's pin.
    title, text = s.word("label_title"), s.word("label")
    lw, lh = _museum_label_size(title, text)
    cat_mod = module("cat")
    reach = (cat_mod.POSES["point"][-1][1][0] - cat_mod.CENTER_X) * _height(s, "cat") / (cat_mod.FEET_Y
                                                                                        - cat_mod.HEAD_TOP)
    ladder_x = fx + fw * k / 2 + 10 * k + lw - 7 + reach
    ly_feet = s.feet(ladder_x)
    step = ly_feet - 46 * k
    s.put(ly_feet - 1, _stepladder(ladder_x, ly_feet, k), (ladder_x - 18 * k, step, ladder_x + 18 * k, ly_feet),
          "ladder", group="cat")
    cat = s.actor("cat", ladder_x, step + 2 * k, "point", "smile", flip=True, tall=s.tall, group="cat",
                  depth=ly_feet)
    hx, hy = _palm(cat, "point", True)
    lx, ly = hx + 7 - lw, hy - 5
    s.put(cat.bottom - 0.5, _museum_label(lx, ly, title, text), (lx, ly, lx + lw, ly + lh), "label", group="cat")

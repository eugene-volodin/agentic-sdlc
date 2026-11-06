"""Footer episodes, group C: tools, connecting services (MCP), access and safety.

Each is registered with `@episode(name)`; its topic words and the lettering in its picture are under
`footers: name:` in the locale. The props these stories need and nobody else does are private functions here,
drawn like those of `things.py`: `_prop(x, y, k, ...) -> str`, the origin where the thing touches the ground,
sized for a 137-unit professor at k = 1.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten
from . import props, sets, things
from .characters import module
from .curves import eased_points
from .footers import Strip, episode
from .ink import INK, Canvas, ellipse_d, n, rounded_rect_d
from .openers import Box, strip_boxes
from .rig import hand as draw_hand
from .scenes import PROFESSOR_HEIGHT
from .sets import _at

AGENT_SCALE = 0.92      # the agent's SCENE_SCALE: its canvas units per professor unit
AGENT_CENTER = 110      # and where its body axis is on its 220 x 280 canvas
AGENT_FEET = 266


# ============================================================================ small shared drawings
def _note(c: Canvas, x: float, y: float, s: float = 1.0, color: str = INK) -> None:
    """A quaver: a head, a stem and a flag."""
    c.add(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(4 * s)}" ry="{n(3 * s)}" fill="{color}" '
          f'transform="rotate(-20 {n(x)} {n(y)})"/>')
    c.line(f"M{n(x + 3.6 * s)},{n(y)} V{n(y - 14 * s)} q{n(4 * s)},{n(3 * s)} {n(6 * s)},{n(8 * s)}", 1.6 * s, color)


def _sheet(x: float, y: float, k: float = 1.0, turn: float = 0) -> str:
    """A sheet of paper with a folded corner and a few lines; the origin is its centre. 16 by 20."""
    c = Canvas()
    c.shape("M-8,-10 H4 L8,-6 V10 H-8 Z", P.WHITE, sw=1.4, light=None)
    c.path("M4,-10 V-6 H8", P.PAPER_FOLD, 1.1)
    c.line("M-5,-4 h8 M-5,0 h10 M-5,4 h6", 1, opacity=0.55)
    return _at(c, x, y, k, turn=turn)


def _smooth(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """A dense polyline along the line `sets.cable` draws through the points (`curves.eased_points`)."""
    return eased_points(points, step=1.5)


def _curly_cord(points: list[tuple[float, float]], pitch: float, r: float, color: str = P.CHARCOAL,
                width: float = 1.6) -> str:
    """A coiled telephone cord along the smooth curve through the points: an even coil, one loop every `pitch`,
    `r` across, outlined in ink like every other line."""
    line = _smooth(points)
    lengths = [0.0]
    for (ax, ay), (bx, by) in zip(line, line[1:], strict=False):
        lengths.append(lengths[-1] + math.hypot(bx - ax, by - ay))
    total = lengths[-1]
    steps = max(24, int(total / pitch * 14))
    pts, j = [], 0
    for i in range(steps + 1):
        d = total * i / steps
        while j < len(line) - 2 and lengths[j + 1] < d:
            j += 1
        seg = max(1e-6, lengths[j + 1] - lengths[j])
        t = (d - lengths[j]) / seg
        (ax, ay), (bx, by) = line[j], line[j + 1]
        x, y = ax + (bx - ax) * t, ay + (by - ay) * t
        ux, uy = (bx - ax) / seg, (by - ay) / seg
        a = math.tau * d / pitch
        fade = min(1.0, d / (pitch * 1.5), (total - d) / (pitch * 1.5))     # the coil starts and ends straight
        # loops a little narrower than the coil is wide: they read as a coil, and do not knot into each other
        along, across = r * 0.6 * math.cos(a) * fade, r * math.sin(a) * fade
        pts.append((x + ux * along - uy * across, y + uy * along + ux * across))
    d = "M" + " L".join(f"{n(px)},{n(py)}" for px, py in pts)
    c = Canvas()
    c.line(d, width + 1.4)
    c.line(d, width, color)
    return c.render()


def _arc(x0: float, y0: float, x1: float, y1: float, lift: float, t: float) -> tuple[float, float]:
    """A point at `t` along a parabola from (x0, y0) to (x1, y1) rising `lift` above the straight line."""
    return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t - 4 * lift * t * (1 - t)


def _style(size: float, k: float) -> str:
    """The lettering style for `size` drawn inside a prop scaled by `k`: balloon letters only when they are big
    on the page, flat ones otherwise (the rim would clog small letters)."""
    return "sign" if size * k >= P.SIGN_BALLOON_FROM else "plain"


def plate_size(text: str, size: float) -> tuple[float, float]:
    """A name plate's width and height for `text`: an even margin of about 0.7 em at the sides, and the
    capitals in the middle of a plate 1.6 em tall."""
    return sets.letter_width(text, size) + size * 1.4, size * 1.6


def _plate(c: Canvas, cx: float, cy: float, text: str, size: float, k: float = 1.0, fill: str = P.CREAM,
           ink: str = INK, w: float = 0, h: float = 0, r: float = 2.5) -> None:
    """A name plate centred at (cx, cy) with its lettering in the middle, never touching the plate's edges."""
    pw, ph = plate_size(text, size)
    w, h = w or pw, h or ph
    c.shape(rounded_rect_d(cx - w / 2, cy - h / 2, w, h, r), fill, sw=1.4, light=None)
    sets.fit_label(c, cx, cy + size * 0.36, text, size, w - size * 1.2, ink, style=_style(size, k))


def _agent_k(s: Strip, size: float = 1.0) -> float:
    return s.tall * size / PROFESSOR_HEIGHT * AGENT_SCALE


# The arm width and the hand scale each character's rig draws with: the palm sits beyond the wrist by these.
_ARM = {"professor": (20, 0.9), "cat": (15, 0.88), "caterpillar": (8, 0.84), "agent": (9, 0.82)}


def _palm(box: Box, pose: str, flip: bool, side: str = "right") -> tuple[float, float, float, float]:
    """The middle of a character's palm on the page, the direction its hand points (degrees, page space) and the
    character's canvas scale: a thing held is drawn here, gripped, not at the wrist's edge."""
    mod = module(box.name)
    (ex, ey), (wx, wy), _, turn = mod.POSES[pose][-1 if side == "right" else -2]
    width, scale = _ARM[box.name]
    a = math.atan2(wy - ey, wx - ex)
    hx, hy = wx + math.cos(a) * width * 0.42, wy + math.sin(a) * width * 0.42
    b = a + math.radians(turn)
    px, py = hx + math.cos(b) * 10 * scale, hy + math.sin(b) * 10 * scale
    k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
    cx = (box.left + box.right) / 2
    dx = (px - mod.CENTER_X) * k
    deg = math.degrees(b)
    return (cx - dx if flip else cx + dx), box.bottom - (mod.FEET_Y - py) * k, (180 - deg if flip else deg), k


def _palm_offset(name: str, pose: str, tall: float, side: str = "right") -> tuple[float, float]:
    """Where the palm is relative to the feet of a character standing unflipped (for placing it by its hand)."""
    mod = module(name)
    k = tall / PROFESSOR_HEIGHT * mod.SCENE_SCALE
    h = (mod.FEET_Y - mod.HEAD_TOP) * k
    x, y, _, _ = _palm(Box(-h, -h, h, 0, name, name), pose, False, side)
    return x, y


def _arrow_lines(c: Canvas, x: float, y: float, angle: float, k: float, count: int = 3, length: float = 10) -> None:
    """Motion lines trailing a thing that flies along `angle` (degrees): short strokes behind it."""
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    for i in range(count):
        off = (i - (count - 1) / 2) * 4 * k
        sx = x - ux * (9 + 2 * (i % 2)) * k + px * off
        sy = y - uy * (9 + 2 * (i % 2)) * k + py * off
        c.line(f"M{n(sx)},{n(sy)} l{n(-ux * length * k)},{n(-uy * length * k)}", 1.3 * k, opacity=0.7)


# ============================================================================ plug_tv: the living room
def _old_tv(x: float, y: float, k: float = 1.0) -> str:
    """A wooden television on splayed legs with rabbit-ear antennae; on its screen a concert, a microphone under
    a spotlight, notes float up. 80 wide, 112 tall with the notes."""
    c = Canvas()
    c.line("M-26,-20 L-33,0 M26,-20 L33,0", 3.6, P.WOOD_DARK)
    c.line("M-10,-20 L-12,-2 M10,-20 L12,-2", 3, darken(P.WOOD_DARK, 0.8))
    c.line("M0,-76 L-20,-102 M0,-76 L19,-104", 1.8, P.METAL_DARK)
    c.add(f'<circle cx="-20" cy="-102" r="2.6" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>'
          f'<circle cx="19" cy="-104" r="2.6" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>')
    c.shape(ellipse_d(0, -76, 8, 4), P.CHARCOAL, sw=1.4, light=None)
    c.shape(rounded_rect_d(-38, -78, 76, 60, 7), P.WOOD, sw=2.2, light=(-2, -2), shade_k=0.85,
            stipple=(20, -78, 18, 60, 14, "right"))
    glass = c.gradient([(0, P.SCREEN_LIGHT), (1, P.SCREEN)], -30, -72, 14, -26)
    c.path(rounded_rect_d(-32, -72, 46, 46, 9), glass, 2)
    # On the screen a concert: a microphone on its stand under a spotlight's cone.
    c.add(f'<path d="M-20,-72 L-34,-27 H4 Z" fill="{P.CREAM}" opacity=".35"/>')
    c.line("M-15,-30 L-9,-46", 1.6, P.METAL_DARK)
    c.line("M-21,-28 H-9", 1.8, P.METAL_DARK)
    c.add(f'<ellipse cx="-8" cy="-50" rx="3.6" ry="4.6" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width=".9"/>')
    c.line("M-10,-52 h4 M-10,-49 h4", 0.7, P.METAL)
    c.line("M-26,-66 q4,-4 8,-1", 2, P.WHITE, 0.4)
    for ky in (-62, -46):
        c.shape(ellipse_d(26, ky, 5, 5), P.CREAM, sw=1.4, light=None)
        c.line(f"M26,{ky} l2,-4", 1.2)
    c.line("M20,-34 h12 M20,-30 h12 M20,-26 h12", 1, opacity=0.6)
    _note(c, 30, -86, 1.0, P.PEN)
    _note(c, 42, -100, 0.8, P.RED)
    _note(c, -40, -92, 0.8, P.PEN)
    return _at(c, x, y, k)


def _armchair(x: float, y: float, k: float = 1.0, color: str = P.TEAL) -> str:
    """A soft armchair with buttoned back; the seat is 38 up, the arms 52. 116 wide, 94 tall."""
    c = Canvas()
    c.line("M-44,-4 V2 M44,-4 V2", 4, P.WOOD_DARK)
    c.shape(rounded_rect_d(-44, -94, 88, 64, 18), color, sw=2.2, light=(-3, -3),
            stipple=(20, -94, 24, 64, 16, "right"))
    for bx, by in ((-20, -76), (0, -78), (20, -76), (-10, -60), (10, -60)):
        c.dot(bx, by, 1.6, darken(color, 0.7))
    c.shape(rounded_rect_d(-46, -30, 92, 26, 6), darken(color, 0.9), sw=2.2, light=(-2, -2))
    c.shape(rounded_rect_d(-42, -44, 84, 16, 7), lighten(color, 0.2), sw=2, light=(-2, -2))
    for side in (-1, 1):
        ax = -58 if side < 0 else 38
        c.shape(rounded_rect_d(ax, -52, 20, 48, 9), color, sw=2.2, light=(-2, -2))
    c.add(f'<path d="M-30,-14 h60" stroke="{lighten(color, 0.35)}" stroke-width="2" stroke-dasharray="4 4"/>')
    return _at(c, x, y, k)


def _floor_lamp(x: float, y: float, k: float = 1.0) -> str:
    """A standard lamp with a fringed shade. 40 wide, 128 tall."""
    c = Canvas()
    c.shape(ellipse_d(0, -2, 14, 4), P.WOOD_DARK, sw=1.8, light=None)
    c.line("M0,-4 V-104", 3, P.WOOD_DARK)
    c.add(f'<path d="M-30,-104 L-12,-128 H12 L30,-104 Z" fill="{P.SUN}" opacity=".12"/>')
    c.shape("M-20,-104 L-12,-126 H12 L20,-104 Z", P.YELLOW, sw=2, light=(-2, -1))
    c.line("M-19,-104 v4 M-13,-104 v5 M-7,-104 v4 M-1,-104 v5 M5,-104 v4 M11,-104 v5 M17,-104 v4", 1.2, P.RED)
    return _at(c, x, y, k)


def _plug(x: float, y: float, k: float = 1.0, turn: float = 0) -> str:
    """A black plug held in the middle, two brass prongs pointing along its direction; behind it a ribbed rubber
    boot tapers to the cable's own thickness, so the cable leaves its back end straight along its axis, 19 behind
    the origin (see `_plug_tail`)."""
    c = Canvas()
    c.line("M5,-2.6 H14 M5,2.6 H14", 2.4)
    c.line("M5,-2.6 H13.4 M5,2.6 H13.4", 1.3, P.SUN)
    c.shape("M-19,-2.2 Q-13,-2.4 -7,-4 V4 Q-13,2.4 -19,2.2 Z", P.CHARCOAL, sw=1.4, light=None)
    c.line("M-15,-2.6 V2.6 M-11.5,-3 V3", 0.8, P.METAL_DARK, 0.8)          # the boot's ribs
    c.shape(rounded_rect_d(-8, -6, 14, 12, 3.4), P.CHARCOAL, sw=1.6, light=(-1, -1))
    c.line("M-4,-6 V6 M0,-6 V6", 0.8, P.METAL_DARK, 0.8)
    return _at(c, x, y, k, turn=turn)


def _plug_tail(x: float, y: float, k: float, turn: float) -> tuple[float, float]:
    a = math.radians(turn)
    return x - 19 * k * math.cos(a), y - 19 * k * math.sin(a)


def _socket(x: float, y: float, k: float = 1.0) -> str:
    """A socket set into the side of a box: a dark plate, two holes; the origin is its middle."""
    c = Canvas()
    c.shape(rounded_rect_d(-5, -7, 10, 14, 2.5), P.CHARCOAL, sw=1.4, light=None)
    c.dot(0, -2.6, 1.5, P.METAL_LIGHT)
    c.dot(0, 2.6, 1.5, P.METAL_LIGHT)
    return _at(c, x, y, k)


def _sill_window(x: float, y: float, k: float = 1.0) -> str:
    """A small window with a sill and a cactus on it; the origin is the middle of the sill. 70 wide, 74 tall."""
    c = Canvas()
    sky = c.gradient([(0, P.SKY_DEEP), (1, P.SKY_LOW)], 0, -66, 0, -4)
    c.shape("M-30,-70 H30 V-2 H-30 Z", P.CARD, sw=2.2, light=None)
    c.path("M-25,-65 H25 V-6 H-25 Z", sky, 1.8)
    c.add(f'<path d="M-18,-26 q3,-8 10,-6 q4,-7 12,-2 q8,-1 7,8 Z" fill="{P.WHITE}" opacity=".85"/>')
    c.line("M0,-65 V-6 M-25,-36 H25", 2.4)
    c.shape(rounded_rect_d(-35, -4, 70, 6, 2), P.WOOD, sw=1.8, light=None)
    c.add(things.cactus(14, -4, 0.75))
    return _at(c, x, y, k)


@episode("plug_tv")
def plug_tv(s: Strip) -> None:
    """The professor plugs the old wooden TV into the computer with a cable that runs the length of the room:
    now the computer can use what the TV has, a concert with its music. The sparrow and the
    caterpillar watch from the armchair; a cactus on the sill."""
    s.indoors()
    k = s.unit
    tx, ty = s.thing(lambda x, y, k: _old_tv(x, y, k), 0.05, 80, 112, name="tv")
    cx, cy = s.thing(lambda x, y, k: props.rug(x, y + 4 * k, k * 0.55, P.PINK) + _armchair(x, y, k), 0.25, 116, 94,
                     name="chair")
    s.actor("caterpillar", cx - 8 * k, cy - 38 * k, "cheer", "smile", flip=False, tall=s.tall * 0.8, group="chair",
            depth=cy + 0.2)
    s.actor("sparrow", cx + 48 * k, cy - 52 * k, "point", "surprise", flip=True, tall=s.tall * 0.75, group="chair",
            depth=cy + 0.4)
    # The computer on its desk, a socket on the side of its box; the professor stands so his plug meets it. The desk
    # is a desk for a grown-up (its top at 0.45 of his height) and deep: the computer at the back towards its left
    # end, so he can reach the socket, the keyboard in front of it, air all round.
    ds, cs = 0.85, 0.75                                       # the desk's and the computer's scale
    dw, dh, dd = 150, 64, 26                                  # the desk's width, legs' height, top's depth
    top = (dh + 9) * ds                                       # its front edge, over the floor, in k

    def desk_set(x: float, y: float, k: float) -> str:
        cx = x + (-dw / 2 * ds + 14 + 50 * cs) * k
        return (props.desk(x, y, k * ds, dw, dh, dd) + props.computer(cx, y - (top + dd * 0.7 * ds) * k, k * cs,
                                                                      keyboard=False)
                + props.keyboard(cx + 4 * k, y - (top + dd * 0.12 * ds) * k, k * cs))

    dx, dy = s.thing(desk_set, 0.74, dw * ds, top + dd * 0.7 * ds + 95 * cs, name="desk")
    cx = dx + (-dw / 2 * ds + 14 + 50 * cs) * k
    sx, sy = cx - 46 * cs * k, dy - (top + dd * 0.7 * ds + 9 * cs) * k
    s.put(dy + 0.5, _socket(sx, sy, k * 0.62), None, group="desk")
    feet = s.feet(0)
    ox, _ = _palm_offset("professor", "present", s.tall)
    gap = 22 * k
    half = module("professor").SIZE[0] * 0.40 * s.tall / PROFESSOR_HEIGHT
    prof = s.actor("professor", min(sx - gap - ox, dx - dw / 2 * ds * k - 5 - half), feet, "present", "smile",
                   flip=False, tall=s.tall, group="prof")
    px, py, _, _ = _palm(prof, "present", False)
    turn = math.degrees(math.atan2(sy - py, sx - px))
    s.put(prof.bottom + 1, _plug(px, py, k * 0.95, turn), None, group="prof")
    c = Canvas()
    for i in (-1, 1):       # it is just about to go in
        a = math.radians(turn + 90 * i)
        mx, my = (px + sx) / 2 + math.cos(a) * 7 * k, (py + sy) / 2 + math.sin(a) * 7 * k
        c.line(f"M{n(mx)},{n(my)} l{n(math.cos(a) * 4 * k)},{n(math.sin(a) * 4 * k)}", 1.4 * k, P.INK, 0.7)
    s.put(prof.bottom + 1, c.render(), None, group="prof")
    s.thing(lambda x, y, k: _floor_lamp(x, y, k), 0.97, 40, 128, name="lamp")
    # The long cable: out of the side of the TV, down to the floor, along it in front of everyone, up to his hand,
    # where it enters the plug's boot straight along the plug's axis. It runs behind him, never across him.
    ex, ey = _plug_tail(px, py, k * 0.95, turn)
    ca, sa = math.cos(math.radians(turn)), math.sin(math.radians(turn))
    yf = s.feet(0, 0.62)
    w = 4.2 * k
    pts = [(tx + 38 * k, ty - 30 * k), (tx + 48 * k, ty - 26 * k), (tx + 50 * k, yf), (s.x(0.25), yf + 3 * k),
           (prof.left - 4 * k, yf), (ex - 22 * k, yf - 2 * k), (ex - ca * 10 * k, ey + 30 * k),
           (ex - ca * 7 * k, ey - sa * 7 * k), (ex, ey)]
    s.put(prof.bottom - 0.5, sets.cable(pts, P.CHARCOAL, w),
          [(tx + 44 * k, yf - w, prof.left - 4 * k, yf + 3 * k + w)], group="prof")
    c = Canvas()        # where the cable leaves the TV: a rubber sleeve on its side
    c.shape(rounded_rect_d(tx + 36 * k, ty - 33.5 * k, 8 * k, 7 * k, 2 * k), P.CHARCOAL, sw=1.3 * k, light=None)
    s.put(prof.bottom + 0.9, c.render(), None, group="prof")
    # A cactus on the windowsill, where the wall has room; the desk has none to spare.
    if s.h >= 200:
        for frac in (0.62, 0.5, 0.88, 0.4):
            wx = s.x(frac)
            wy = dy - 112 * k - 20
            box = (wx - 36 * k, wy - 76 * k, wx + 36 * k, wy + 4 * k)
            if wy - 76 * k > s.base * 0.25 and s.free(box, 6):
                s.put(3, _sill_window(wx, wy, k), box, "window")
                break


# ============================================================================ modem: a cord across the country
def _dacha(x: float, y: float, k: float = 1.0) -> str:
    """A little country house of logs: a red roof, a window with a flower box, sunflowers by the wall.
    110 wide, 106 tall."""
    c = Canvas()
    c.shape("M-40,0 V-58 H40 V0 Z", P.WOOD_LIGHT, sw=2.2, light=(-2, -2), shade_k=0.85)
    for i in range(5):
        c.line(f"M-40,{-10 - i * 11} H40", 1.1, opacity=0.5)
    c.shape("M-50,-54 L0,-98 L50,-54 Z", P.RED, sw=2.2, light=(-3, -2))
    c.shape(ellipse_d(0, -70, 7, 7), P.SKY, sw=1.6, light=None)
    c.line("M-7,-70 H7 M0,-77 V-63", 1.2)
    c.shape("M14,0 V-40 H32 V0 Z", P.WOOD_DARK, sw=1.8, light=None)
    c.dot(28, -20, 1.8, P.SUN)
    c.shape("M-32,-46 H-6 V-24 H-32 Z", P.SKY_LOW, sw=1.8, light=None)
    c.line("M-19,-46 V-24 M-32,-35 H-6", 1.4)
    c.shape("M-34,-24 H-4 V-17 H-34 Z", P.TERRACOTTA, sw=1.5, light=None)
    for fx, color in ((-29, P.RED), (-23, P.PINK), (-17, P.RED), (-11, P.YELLOW)):
        c.add(f'<circle cx="{fx}" cy="-26" r="2.6" fill="{color}" stroke="{INK}" stroke-width=".8"/>')
    for sx, top in ((-48, -66), (47, -52)):
        c.line(f"M{sx},0 V{top}", 2, P.LEAF_DARK)
        c.shape(f"M{sx},{top + 26} q-8,-4 -10,-10 q8,0 10,6 Z", P.LEAF, sw=1.2, light=None)
        for a in range(0, 360, 36):
            px, py = sx + 8 * math.cos(math.radians(a)), top + 8 * math.sin(math.radians(a))
            c.add(f'<ellipse cx="{n(px)}" cy="{n(py)}" rx="4" ry="2" transform="rotate({a} {n(px)} {n(py)})" '
                  f'fill="{P.SUN}" stroke="{INK}" stroke-width=".8"/>')
        c.shape(ellipse_d(sx, top, 5, 5), P.WOOD_DARK, sw=1.2, light=None)
    return _at(c, x, y, k)


def _handset(ear: tuple[float, float], mouth: tuple[float, float], w: float, color: str = P.RED) -> str:
    """A telephone handset from its earpiece to its mouthpiece, `w` thick: a curved grip with a cup at each
    end."""
    (x0, y0), (x1, y1) = ear, mouth
    length = math.hypot(x1 - x0, y1 - y0)
    angle = math.degrees(math.atan2(y1 - y0, x1 - x0))
    c = Canvas()
    u = length / 2
    sw = max(0.9, 1.5 * w / 8)
    c.shape(f"M{n(-u)},{n(-w * 0.45)} Q0,{n(-w * 1.2)} {n(u)},{n(-w * 0.45)} V{n(w * 0.25)} Q0,{n(-w * 0.45)} "
            f"{n(-u)},{n(w * 0.25)} Z", color, sw=sw, light=None)
    for end in (-1, 1):
        c.shape(rounded_rect_d(end * u - w * 0.85, -w * 0.35, w * 1.7, w * 1.1, w * 0.5), color, sw=sw,
                light=None)
    c.line(f"M{n(-u * 0.5)},{n(-w * 0.6)} Q0,{n(-w * 0.95)} {n(u * 0.5)},{n(-w * 0.6)}", w * 0.16, P.WHITE, 0.55)
    return (f'<g transform="translate({n((x0 + x1) / 2)},{n((y0 + y1) / 2)}) rotate({n(angle)})">'
            f"{c.render()}</g>")


def _ear_and_mouth(box: Box, pose: str, flip: bool, ear: tuple[float, float]) -> tuple[tuple, tuple, float]:
    """A handset at the ear: from `ear` (a point on the character's canvas, beside its head) down through the
    palm, ending a little beyond it. Returns the ear end, the mouth end (where the cord leaves) and the scale."""
    mod = module(box.name)
    px, py, _, k = _palm(box, pose, flip)
    cx = (box.left + box.right) / 2
    ex = cx + (ear[0] - mod.CENTER_X) * k * (-1 if flip else 1)
    ey = box.bottom - (mod.FEET_Y - ear[1]) * k
    mx, my = px + (px - ex) * 0.2, py + (py - ey) * 0.2
    return (ex, ey), (mx, my), k


def _butterfly_net(x0: float, y0: float, x1: float, y1: float, r: float) -> str:
    """A butterfly net on a pole from the hand (x0, y0) to the rim of the hoop centred at (x1, y1)."""
    c = Canvas()
    end = f"L{n(x1 + r * 0.92)},{n(y1 + r * 0.12)}"            # the pole is fixed to the hoop's rim
    c.line(f"M{n(x0)},{n(y0)} {end}", r * 0.22 + 1.6)
    c.line(f"M{n(x0)},{n(y0)} {end}", r * 0.22, P.WOOD_DARK)
    c.add(f'<path d="M{n(x1 - r)},{n(y1)} Q{n(x1 - r * 0.6)},{n(y1 + r * 2.4)} {n(x1 + r * 0.2)},{n(y1 + r * 2.2)} '
          f'Q{n(x1 + r)},{n(y1 + r)} {n(x1 + r)},{n(y1)} Z" fill="{P.WHITE}" fill-opacity=".75" stroke="{INK}" '
          f'stroke-width="{n(r * 0.09)}"/>')
    for i in range(1, 4):
        c.line(f"M{n(x1 - r + i * r / 2)},{n(y1)} q0,{n(r)} {n(-r * 0.2)},{n(r * 2)}", r * 0.05, opacity=0.5)
    c.add(f'<ellipse cx="{n(x1)}" cy="{n(y1)}" rx="{n(r)}" ry="{n(r * 0.35)}" fill="none" stroke="{P.METAL_DARK}" '
          f'stroke-width="{n(r * 0.16)}"/>')
    return c.render()


def _mushroom_basket(x: float, y: float, k: float = 1.0) -> str:
    """A wicker basket full of mushrooms. 40 wide, 34 tall."""
    c = Canvas()
    c.line("M-16,-16 Q0,-40 16,-16", 2.4, P.WOOD_DARK)
    for mx, color in ((-9, P.TRUNK), (2, P.RED), (10, P.TRUNK)):
        c.add(props.mushroom(mx, -12, 0.55, color, spots=color == P.RED))
    c.shape("M-19,-16 H19 L14,0 H-14 Z", P.AMBER, sw=1.8, light=(-1, -1))
    c.line("M-17,-11 H17 M-15,-5 H15 M-10,-16 l2,16 M0,-16 V0 M10,-16 l-2,16", 1, opacity=0.6)
    return _at(c, x, y, k)


def _milestone(x: float, y: float, k: float = 1.0, text: str = "") -> str:
    """A striped roadside post with a distance on its plate, the lettering never under 9.5 units on the page.
    About 64 tall at k = 1."""
    size = max(10.0, sets.LETTERING_MIN / k)
    w, ph = plate_size(text, size)
    c = Canvas()
    c.shape("M-4,0 V-48 H4 V0 Z", P.WHITE, sw=1.6, light=None)
    c.add(f'<path d="M-4,-14 h8 v6 h-8 Z M-4,-30 h8 v6 h-8 Z" fill="{INK}"/>')
    c.shape(rounded_rect_d(-w / 2, -46 - ph, w, ph, 3), P.BLUE, sw=1.6, light=(-1, -1))
    sets.fit_label(c, 0, -46 - ph / 2 + size * 0.36, text, size, w - size * 1.2, P.WHITE, style=_style(size, k))
    return _at(c, x, y, k)


def _skyline(x0: float, x1: float, y: float, k: float, seed: int) -> str:
    """A far-off city: a clock tower with a pointed roof among blocks of flats with lit windows, flat roofs
    and a chimney here and there; solid, so the hills behind do not show through."""
    rnd = random.Random(seed)
    c = Canvas()
    tx = (x0 + x1) / 2
    # the tower first, behind the houses
    tw = 18 * k
    c.shape(f"M{n(tx - tw / 2)},{n(y)} V{n(y - 84 * k)} H{n(tx + tw / 2)} V{n(y)} Z", lighten(P.TERRACOTTA, 0.45),
            sw=1.5, light=(-1, -1), shade_k=0.88)
    c.shape(f"M{n(tx - tw / 2 - 3 * k)},{n(y - 84 * k)} L{n(tx)},{n(y - 108 * k)} L{n(tx + tw / 2 + 3 * k)},"
            f"{n(y - 84 * k)} Z", darken(P.RED, 0.9), sw=1.5, light=None)
    c.line(f"M{n(tx)},{n(y - 108 * k)} V{n(y - 116 * k)}", 1.2)
    c.shape(ellipse_d(tx, y - 72 * k, 6 * k, 6 * k), P.CARD, sw=1.2, light=None)
    c.line(f"M{n(tx)},{n(y - 72 * k)} v{n(-4 * k)} M{n(tx)},{n(y - 72 * k)} h{n(3 * k)}", 1)
    x = x0
    while x < x1:
        w = rnd.uniform(24, 40) * k
        h = rnd.uniform(36, 62) * k
        if x < tx + tw / 2 + 3 * k and x + w > tx - tw / 2 - 3 * k:   # leave the tower in view
            x = tx + tw / 2 + 3 * k
            continue
        color = rnd.choice((P.STONE, lighten(P.BLUE, 0.55), lighten(P.TERRACOTTA, 0.5), P.BEIGE))
        if rnd.random() < 0.4:
            cx = x + w * rnd.uniform(0.2, 0.7)
            c.shape(f"M{n(cx)},{n(y - h + 1)} V{n(y - h - 7 * k)} H{n(cx + 5 * k)} V{n(y - h + 1)} Z",
                    darken(color, 0.85), sw=1.2, light=None)
        c.shape(f"M{n(x)},{n(y)} V{n(y - h)} H{n(x + w)} V{n(y)} Z", color, sw=1.5, light=(-1, -1), shade_k=0.9)
        c.line(f"M{n(x)},{n(y - h + 3 * k)} H{n(x + w)}", 1, opacity=0.4)
        cols = 2 if w < 32 * k else 3
        for wy in range(int(9 * k), int(h - 8 * k), int(max(6, 10 * k))):
            for j in range(cols):
                wx = x + w * (j + 0.5) / cols - 2 * k
                c.add(f'<rect x="{n(wx)}" y="{n(y - h + wy)}" width="{n(4 * k)}" height="{n(5 * k)}" '
                      f'fill="{P.SUN if rnd.random() < 0.3 else P.WHITE}" stroke="{INK}" stroke-width=".5"/>')
        x += w + rnd.uniform(1, 5) * k
    return c.render()


@episode("modem")
def modem(s: Strip) -> None:
    """The cat at his country house has forgotten something and phones the city: the coiled cord of his handset
    runs the whole way across the country - past a basket of mushrooms, a milestone, a snail sitting on it - into
    the professor's computer, and the professor listens on his own handset, wired to the same computer. The cat
    keeps his butterfly net in the other paw; a butterfly has got away."""
    s.outdoors()
    k = s.unit
    if s.h >= 150:
        s.put(0.5, _skyline(s.x(0.62), s.hi + 20, s.base + 4, k * 0.8, s.seed), None)
    s.thing(lambda x, y, k: _dacha(x, y, k), 0.07, 110, 106, name="dacha")
    cat = s.cast("cat", 0.245, "think", "talk", flip=False, group="cat")
    ear, mouth, ck = _ear_and_mouth(cat, "think", False, (208, 146))
    s.put(cat.bottom + 2, _handset(ear, mouth, 15 * ck), None, group="cat")
    lx, ly, _, _ = _palm(cat, "think", False, "left")
    r = 11 * k
    hoop = (cat.left - r * 0.2, cat.top + r * 0.8)
    # the pole runs through his paw and a little past it, in front of him, clear of his body; the paw closes
    # round it, drawn over the pole
    a = math.atan2(hoop[1] + r * 0.12 - ly, hoop[0] + r * 0.92 - lx)
    butt = (lx - math.cos(a) * 7 * k, ly - math.sin(a) * 7 * k)
    s.put(cat.bottom + 0.5, _butterfly_net(*butt, *hoop, r), None, group="cat")
    g = Canvas()
    draw_hand(g, 0, 0, 90, module("cat").HAND, "fist", _ARM["cat"][1])
    mod = module("cat")
    wx = (cat.left + cat.right) / 2 + (mod.REST_L[1][0] - mod.CENTER_X) * ck
    wy = cat.bottom - (mod.FEET_Y - mod.REST_L[1][1]) * ck
    s.put(cat.bottom + 1, _at(g, wx, wy, ck), None, group="cat")
    bx, by = hoop[0] + 2 * k, hoop[1] - 22 * k
    if by > s.base * 0.25:
        c = Canvas()
        c.add(f'<path d="M{n(bx - 4 * k)},{n(by + 8 * k)} q{n(-6 * k)},{n(6 * k)} {n(-2 * k)},{n(12 * k)}" '
              f'fill="none" stroke="{INK}" stroke-width="{n(k)}" stroke-dasharray="{n(2 * k)} {n(2.4 * k)}"/>')
        s.put(cat.bottom + 2, c.render() + props.butterfly(bx, by, k * 0.8, P.PINK),
              (bx - 11 * k, by - 12 * k, bx + 11 * k, by + 4 * k), "butterfly", group="cat")
    s.thing(lambda x, y, k: _mushroom_basket(x, y, k), 0.36, 40, 34, nearer=0.15, name="basket")
    s.thing(lambda x, y, k: props.mushroom(x - 8 * k, y, k * 0.6, P.RED) + props.mushroom(x + 6 * k, y, k * 0.5,
                                                                                          P.TRUNK, spots=False),
            0.45, 30, 22, nearer=0.1, name="mushrooms")
    s.thing(lambda x, y, k: _milestone(x, y, k, s.word("km")), 0.55, 50, 66, name="post")
    tx, ty = s.thing(lambda x, y, k: things.kitchen_table(x, y, k, 70, P.WOOD_LIGHT, None)
                     + props.computer(x + 4 * k, y - 48 * k, k * 0.55, mirror=True), 0.9, 74, 102, name="table",
                     group="prof")
    jx, jy = tx + 4 * k - 26 * k, ty - 48 * k - 7 * k          # the socket on the side of the computer
    s.put(ty + 1, _socket(jx, jy, k * 0.6), None, group="prof")
    ox, _ = _palm_offset("professor", "think", s.tall)
    half = module("professor").SIZE[0] * 0.40 * s.tall / PROFESSOR_HEIGHT
    prof = s.actor("professor", min(jx - 30 * k - ox, tx - 37 * k - 5 - half), s.feet(0), "think", "talk",
                   flip=False, tall=s.tall, group="prof")
    pear, pmouth, pk = _ear_and_mouth(prof, "think", False, (172, 122))
    s.put(prof.bottom + 2, _handset(pear, pmouth, 14 * pk), None, group="prof")
    cord_r, pitch, cw = 2.4 * k, 6.4 * k, 1.1 * k
    # The professor's cord leaves the handset away from his body and hangs in one loose sag to the socket: it never
    # crosses his sweater and never meets the long cord, so the cords never look tangled.
    sag = max(pmouth[1], jy) + 5 * k
    s.put(prof.bottom + 1.5, _curly_cord([pmouth, ((pmouth[0] * 2 + jx) / 3, sag), ((pmouth[0] + jx * 2) / 3, sag),
                                          (jx - 3 * k, jy - 1 * k)], pitch, cord_r, width=cw),
          None, group="prof")
    # The long cord: from the cat's handset down to the grass, across the land, past the professor's feet, and up
    # up beside the table leg into the bottom of the same socket.
    yc = s.feet(0, 0.82)
    leg = tx - 27 * k
    pts = [mouth, (mouth[0] + 6 * k, cat.bottom - 14 * k), (cat.right, yc), (s.x(0.45), yc + 2 * k),
           (s.x(0.62), yc - 1 * k), (leg - 26 * k, yc), (leg + 4 * k, yc - 8 * k), (leg + 6 * k, ty - 30 * k),
           (jx + 2 * k, jy + 8 * k), (jx, jy + 4 * k)]
    s.put(yc + 2, _curly_cord(pts, pitch, cord_r, width=cw), [(cat.right - 2 * k, yc - 6 * k, leg - 4 * k, yc + 6 * k)],
          group="cord")
    sx = s.x(0.47)
    s.put(yc + 3, sets.snail(sx, yc + 1 * k, k * 0.42), (sx - 14 * k, yc - 15 * k, sx + 14 * k, yc), "snail",
          group="cord")


# ============================================================================ chatting_computers
def _chatty(x: float, y: float, k: float = 1.0, mirror: bool = False, ladybug: bool = False) -> str:
    """A computer on a table with a smiling face on its screen and two arms: one holds a telephone receiver to
    its side, the other tosses a sheet of paper. Faces right (or left mirrored). 112 wide (-46..66), 124 tall."""
    c = Canvas()
    c.line("M-30,0 V-38 M30,0 V-38", 3.4, P.WOOD_DARK)
    c.shape(rounded_rect_d(-38, -44, 76, 7, 2), P.WOOD_LIGHT, sw=1.8, light=None)
    c.shape(rounded_rect_d(-34, -54, 16, 10, 3), P.RED, sw=1.4, light=None)       # the telephone
    c.shape(ellipse_d(-26, -52, 4, 2.5), P.CHARCOAL, sw=1, light=None)
    c.shape("M-6,-56 V-46 H6 V-56 Z", P.BEIGE_DARK, sw=1.4, light=None)
    c.shape(ellipse_d(0, -45, 14, 3), P.BEIGE, sw=1.4, light=None)
    c.shape(rounded_rect_d(-32, -116, 64, 60, 8), P.BEIGE, sw=2.2, light=(-2, -2), shade_k=0.86)
    glass = c.gradient([(0, P.SCREEN_LIGHT), (1, P.SCREEN_DARK)], -26, -110, 20, -64)
    c.path(rounded_rect_d(-25, -110, 50, 44, 7), glass, 1.8)
    for ex in (-9, 9):
        c.add(f'<ellipse cx="{ex}" cy="-94" rx="3.4" ry="4.4" fill="{P.GLOW}"/>')
    c.line("M-10,-82 Q0,-74 10,-82", 2.4, P.GLOW)
    c.add(f'<circle cx="-17" cy="-84" r="3" fill="{P.PINK}" opacity=".6"/>'
          f'<circle cx="17" cy="-84" r="3" fill="{P.PINK}" opacity=".6"/>')
    c.shape(rounded_rect_d(22, -54, 18, 10, 2), P.CREAM, sw=1.3, light=None)            # a mug
    c.line("M40,-51 q4,0 4,3 q0,3 -4,3", 1.3)
    # The far arm holds a handset to the side of its screen, the "ear"; the coiled cord drops to the telephone.
    # The hand closes round the middle of the handle, so it is drawn over the handset, not beside it.
    c.tube("M-30,-62 Q-54,-66 -44,-88", P.METAL, 4.5, sw=1.8)
    c.add(_curly_cord([(-41, -71), (-44, -62), (-30, -55)], 3.4, 1.6, width=0.9))
    c.add(_handset((-37, -110), (-41, -70), 7.5))
    draw_hand(c, -41, -90, -4, P.METAL_PALE, "grip", 0.5)
    # The near arm flings a sheet across the room.
    c.tube("M30,-74 Q50,-80 56,-98", P.METAL, 4.5, sw=1.8)
    draw_hand(c, 56, -98, -70, P.METAL_PALE, "open", 0.45)
    if ladybug:
        c.shape("M-2,-116 Q-2,-126 8,-126 Q18,-126 18,-116 Z", P.RED, sw=1.3, light=None)
        c.line("M8,-126 V-116", 1)
        for lx, ly in ((3, -121), (12, -122), (5, -118), (14, -118)):
            c.dot(lx, ly, 1.2)
        c.shape(ellipse_d(19, -118, 3, 3), P.CHARCOAL, sw=1, light=None)
    return _at(c, x, y, k, mirror)


@episode("chatting_computers")
def chatting_computers(s: Strip) -> None:
    """Two computers with arms are on the phone to each other and toss sheets of paper across the room: they
    talk the same protocol. The agent points it out, the caterpillar writes it down; a ladybug rides on one
    monitor, a sheet that fell lies on the floor."""
    s.indoors()
    k = s.unit
    s.cast("agent", 0.04, "point", "smile", flip=False, mark="idea")
    ax, ay = s.x(0.27), s.feet(0)
    bx = s.x(0.73)
    s.put(ay - 1, _chatty(ax, ay, k), (ax - 46 * k, ay - 124 * k, ax + 66 * k, ay), "talk")
    s.put(ay - 1, _chatty(bx, ay, k, mirror=True, ladybug=True), (bx - 66 * k, ay - 128 * k, bx + 46 * k, ay),
          group="talk")
    # The sheets in the air between the two flinging hands, each with motion lines behind it.
    x0, y0 = ax + 60 * k, ay - 104 * k
    x1, y1 = bx - 60 * k, ay - 104 * k
    lift = min(28 * k, max(4.0, y0 - 14 - 10 * k))
    for i, t in enumerate((0.16, 0.38, 0.62, 0.84)):
        sx, sy = _arc(x0, y0, x1, y1, lift, t)
        nx, ny = _arc(x0, y0, x1, y1, lift, t + 0.01)
        c = Canvas()
        _arrow_lines(c, sx, sy, math.degrees(math.atan2(ny - sy, nx - sx)), k * 0.9)
        s.put(ay + 2, c.render() + _sheet(sx, sy, k * 0.9, (-30, 12, -8, 26)[i]),
              (sx - 9 * k, sy - 10 * k, sx + 9 * k, sy + 10 * k), group="talk")
    ph = 2.2 * k
    line = [(ax - 26 * k, ay - 50 * k), (ax - 36 * k, ay - 42 * k), (ax - 36 * k, ay - 3 * k), (s.x(0.5), ay - 2 * k),
            (bx + 36 * k, ay - 3 * k), (bx + 36 * k, ay - 42 * k), (bx + 26 * k, ay - 50 * k)]
    s.put(ay - 1.5, sets.cable(line, P.RED, ph), None, group="talk")
    mx = s.x(0.5)
    my = s.feet(mx, 0.75)
    s.put(my, _sheet(mx, my - 5.6 * k, k * 0.7, -80), (mx - 8 * k, my - 11 * k, mx + 8 * k, my), "sheet")
    s.cast("caterpillar", 0.95, "write", "surprise", flip=True)


# ============================================================================ workshop: an agent with too many hands
def _shed(x: float, y: float, k: float = 1.0, sign: str = "") -> str:
    """A plank workshop, its double doors flung open on a dark inside with tools on the wall, a sign board over
    the doors (its lettering never under 9.5 units on the page), a small window. 204 wide,
    158 tall."""
    c = Canvas()
    c.shape("M-90,0 V-100 H90 V0 Z", P.WOOD, sw=2.2, light=(-2, -2), shade_k=0.85)
    for px in range(-82, 90, 12):
        c.line(f"M{px},-98 V-2", 1, opacity=0.35)
    c.shape("M-36,0 V-72 H36 V0 Z", darken(P.WOOD_DARK, 0.7), sw=2, light=None)
    for side in (-1, 1):
        c.shape(f"M{side * 36},0 L{side * 58},6 V-66 L{side * 36},-72 Z", P.GREEN, sw=2, light=(-1, -1))
        c.line(f"M{side * 40},-12 L{side * 54},-8 M{side * 40},-58 L{side * 54},-54", 1.2, opacity=0.5)
    c.shape("M-84,-66 H-62 V-44 H-84 Z", P.SKY_LOW, sw=1.8, light=None)
    # a coil of green garden hose hanging on a peg, its brass nozzle dangling
    c.line("M83,-50 Q84,-36 80,-30", 4.4)
    c.line("M83,-50 Q84,-36 80,-30", 2.4, P.GREEN)
    c.shape("M78.4,-31 L81.6,-30 L80.6,-24 L77.6,-25 Z", P.SUN, sw=1, light=None)
    for i, (dx, dy) in enumerate(((-2, 1), (0, 0), (2, -1))):
        c.add(f'<ellipse cx="{74 + dx}" cy="{-52 + dy}" rx="9" ry="10" fill="none" stroke="{INK}" '
              f'stroke-width="4.4"/><ellipse cx="{74 + dx}" cy="{-52 + dy}" rx="9" ry="10" fill="none" '
              f'stroke="{darken(P.GREEN, 0.9 + i * 0.05)}" stroke-width="2.4"/>')
    c.shape(rounded_rect_d(71, -66, 6, 5, 1.5), P.WOOD_DARK, sw=1.2, light=None)        # the peg
    c.shape("M-102,-96 L0,-142 L102,-96 L96,-92 L0,-135 L-96,-92 Z", P.RED, sw=2.2, light=None)
    c.shape("M-88,-98 L0,-136 L88,-98 Z", P.WOOD_LIGHT, sw=2, light=None)
    if sign:
        size = max(11.0, sets.LETTERING_MIN / k)
        w, h = plate_size(sign, size)
        w = min(172.0, w)
        top = -74 - h - 1
        c.line(f"M{n(-w / 2 + 8)},{n(top)} L-20,-112 L20,-112 L{n(w / 2 - 8)},{n(top)}", 1.2)    # its wire
        c.dot(-20, -112, 1.8, P.METAL_DARK)
        c.dot(20, -112, 1.8, P.METAL_DARK)
        _plate(c, 0, top + h / 2, sign, size, k, w=w, h=h, r=3)
    return _at(c, x, y, k)


def _tool(c: Canvas, kind: str, x: float, y: float, a: float, scale: float = 1.0) -> None:
    """A tool held at (x, y) pointing along angle `a` (degrees), in the agent's canvas units."""
    g = Canvas()
    if kind == "pan":
        g.line("M0,0 H26", 5, P.WOOD_DARK)
        g.shape(ellipse_d(40, 0, 16, 14), P.CHARCOAL, sw=2, light=(-2, -2))
        g.shape("M30,-2 Q29,-9 37,-9 Q42,-12 47,-7 Q53,-3 49,3 Q47,9 40,8 Q31,8 30,-2 Z", P.WHITE, sw=1.4,
                light=None)                                               # a fried egg in the pan
        g.shape(ellipse_d(40, -1, 4.6, 4.2), P.SUN, sw=1.3, light=None)
        g.line("M38.4,-3 q1,-1 2.4,-0.8", 1, P.WHITE, 0.9)
    elif kind == "hammer":
        g.line("M-6,0 H30", 5, P.WOOD)
        g.shape("M26,-14 H38 V14 H26 Z", P.METAL_DARK, sw=2, light=None)
    elif kind == "broom":
        g.line("M-10,0 H52", 4, P.WOOD)
        g.shape("M50,-4 L74,-12 L76,12 L50,4 Z", P.AMBER, sw=2, light=None)
        g.line("M58,-6 L74,-8 M58,0 H76 M58,6 L74,8", 1, opacity=0.6)
    elif kind == "ladle":
        g.line("M-4,0 H32", 4, P.METAL_DARK)
        g.shape("M30,-2 Q30,14 40,14 Q50,14 50,-2 Z", P.METAL, sw=2, light=None)
    elif kind == "wrench":
        g.line("M-4,0 H28", 6, P.METAL_DARK)
        g.shape("M26,-8 Q40,-12 40,-4 L32,-2 V2 L40,4 Q40,12 26,8 Z", P.METAL, sw=2, light=None)
    else:   # a paintbrush, its tip dripping blue
        g.line("M-4,0 H24", 4, P.RED)
        g.shape("M22,-4 H30 V4 H22 Z", P.METAL, sw=1.6, light=None)
        g.shape("M30,-5 Q42,-4 44,0 Q42,4 30,5 Z", P.BLUE, sw=1.6, light=None)
    c.place(g, f"translate({n(x)},{n(y)}) rotate({n(a)}) scale({n(scale)})")


def _extra_arms(x: float, feet: float, ka: float) -> str:
    """Six more arms for the agent, each with a tool, in the agent's own canvas units, placed like the agent."""
    c = Canvas()
    arms = (((80, 156), (30, 150), (0, 112), "pan", -120),
            ((76, 174), (20, 186), (-14, 166), "hammer", -150),
            ((80, 196), (40, 222), (14, 236), "broom", 160),
            ((140, 156), (190, 150), (220, 112), "ladle", -60),
            ((144, 174), (200, 186), (234, 166), "wrench", -20),
            ((140, 196), (180, 222), (206, 238), "brush", 30))
    for (sx, sy), (ex, ey), (hx, hy), tool, a in arms:
        _tool(c, tool, hx, hy, a, 1.9)
        c.tube(f"M{sx},{sy} Q{ex},{ey} {hx},{hy}", P.METAL, 10, sw=2.4)
        c.add(f'<circle cx="{hx}" cy="{hy}" r="9" fill="{P.METAL_PALE}" stroke="{INK}" stroke-width="2.4"/>')
        c.line(f"M{hx - 4},{hy - 4} l4,4 M{hx + 1},{hy - 5} l3,4", 1.4)
    return (f'<g transform="translate({n(x - AGENT_CENTER * ka)},{n(feet - AGENT_FEET * ka)}) scale({n(ka)})">'
            f"{c.render()}</g>")


def _easel(x: float, y: float, k: float = 1.0) -> str:
    """A studio easel with a blueprint of the robot being built: two front legs and a back leg, a ledge the
    board rests on, a clamp holding the board's top on the mast. On the blue sheet, in white: the robot's
    outline (a head with an antenna, a body with a screen, arms and legs) and two dimension arrows, its width
    under it and its height beside it. 76 wide, 118 tall."""
    c = Canvas()
    wood, dark = P.WOOD, P.WOOD_DARK
    c.line("M2,-100 L16,0", 5.6)                                          # the back leg, behind everything
    c.line("M2,-100 L16,0", 3.2, darken(dark, 0.85))
    for leg in ("M-6,-112 L-30,0", "M6,-112 L30,0"):                      # the two front legs, spread
        c.line(leg, 6.4)
        c.line(leg, 4, wood)
    c.line("M0,-118 V-38", 6.4)                                           # the mast
    c.line("M0,-118 V-38", 4, wood)
    for fx in (-30, 30, 16):
        c.shape(rounded_rect_d(fx - 3.5, -2.4, 7, 2.6, 1), dark, sw=1.1, light=None)      # rubber feet
    # the board: a blue sheet pinned on a plywood backing
    c.shape(rounded_rect_d(-34, -106, 68, 62, 2), P.WOOD_LIGHT, sw=2, light=(-1.5, -1.5), shade_k=0.86)
    blue = darken(P.BLUE, 0.92)
    c.shape("M-31,-103 H31 V-47 H-31 Z", blue, sw=1.4, light=None)
    for gx in range(-24, 31, 8):
        c.line(f"M{gx},-102 V-48", 0.7, P.WHITE, 0.22)
    for gy in range(-96, -47, 8):
        c.line(f"M-30,{gy} H30", 0.7, P.WHITE, 0.22)
    white = P.WHITE
    # the robot: antenna, head with eyes, body with a screen, arms, legs
    rx = -5
    c.path(f"M{rx},-90 V-95", "none", 1.6, white)
    c.add(f'<circle cx="{rx}" cy="-96.4" r="1.8" fill="none" stroke="{white}" stroke-width="1.4"/>')
    c.path(rounded_rect_d(rx - 8, -90, 16, 11, 2.4), "none", 1.8, white)
    c.dot(rx - 3.4, -84.6, 1.3, white)
    c.dot(rx + 3.4, -84.6, 1.3, white)
    c.path(rounded_rect_d(rx - 10, -77, 20, 15, 2.4), "none", 1.8, white)
    c.path(rounded_rect_d(rx - 5, -74, 10, 6, 1.2), "none", 1.2, white)
    c.path(f"M{rx - 10},-74 Q{rx - 16},-70 {rx - 16},-64 M{rx + 10},-74 Q{rx + 16},-70 {rx + 16},-64",
           "none", 1.8, white)
    c.path(f"M{rx - 5},-62 V-56 H{rx - 9} M{rx + 5},-62 V-56 H{rx + 9}", "none", 1.8, white)
    # the dimension arrows: the width under the robot, the height beside it, with extension ticks

    def arrow(x0: float, y0: float, x1: float, y1: float) -> None:
        c.path(f"M{x0},{y0} L{x1},{y1}", "none", 1.1, white)
        for (px, py), (qx, qy) in (((x0, y0), (x1, y1)), ((x1, y1), (x0, y0))):
            a = math.atan2(py - qy, px - qx)
            ax, ay = math.cos(a), math.sin(a)
            c.add(f'<path d="M{n(px)},{n(py)} L{n(px - 4 * ax - 2 * ay)},{n(py - 4 * ay + 2 * ax)} '
                  f'L{n(px - 4 * ax + 2 * ay)},{n(py - 4 * ay - 2 * ax)} Z" fill="{white}"/>')

    arrow(rx - 16, -51, rx + 16, -51)
    c.path(f"M{rx - 16},-60 V-48.5 M{rx + 16},-60 V-48.5", "none", 0.8, white)
    arrow(20, -96, 20, -56)
    c.path("M17,-96 H24 M17,-56 H24", "none", 0.8, white)
    # the ledge the board stands on, and the clamp on the mast holding its top
    c.shape(rounded_rect_d(-38, -45, 76, 6, 1.6), dark, sw=1.8, light=(-1, -1))
    c.shape(rounded_rect_d(-5, -111, 10, 9, 1.6), dark, sw=1.6, light=(-0.8, -0.8))
    c.shape(ellipse_d(0, -106.5, 2, 2), P.METAL, sw=1, light=None)
    return _at(c, x, y, k)


def _toolbox(x: float, y: float, k: float = 1.0) -> str:
    """An open red toolbox, a saw and a screwdriver sticking out. 54 wide, 44 tall."""
    c = Canvas()
    c.shape("M18,-24 L30,-44 L34,-42 L24,-22 Z", P.METAL, sw=1.4, light=None)
    c.line("M20,-28 l2,1 M23,-33 l2,1 M26,-38 l2,1", 1)
    c.line("M-10,-24 L-16,-42", 3, P.YELLOW)
    c.line("M-16,-42 l-1,-4", 1.6, P.METAL_DARK)
    c.shape("M-26,0 V-24 H26 V0 Z", P.RED, sw=2, light=(-2, -2))
    c.line("M-10,-24 Q0,-34 10,-24", 2.2, P.METAL_DARK)
    c.shape("M-6,-12 H6 V-8 H-6 Z", P.METAL, sw=1, light=None)
    return _at(c, x, y, k)


@episode("workshop")
def workshop(s: Strip) -> None:
    """In the doorway of the workshop stands the agent with eight arms, each holding a tool: a frying pan, a
    hammer, a broom, a ladle, a wrench, a brush - more tools than any job needs. The caterpillar tries to
    count them; the blueprint on the easel beside the workshop shows the robot being built; a bee buzzes past the
    toolbox."""
    s.outdoors()
    k = s.unit
    x, y = s.thing(lambda x, y, k: _shed(x, y, k, s.word("sign")), 0.38, 204, 158, name="shed")
    # beside the workshop, on the grass in front of it, the easel with the blueprint of the robot inside
    ex = x - (102 + 14 + 38) * k
    ey = s.feet(ex, 0.25)
    s.put(ey, _easel(ex, ey, k), (ex - 38 * k, ey - 118 * k, ex + 38 * k, ey), "easel")
    s.actor("agent", x, y, "cheer", "smile", flip=False, tall=s.tall * 0.92, group="shed", depth=y)
    s.put(y + 0.5, _extra_arms(x, y, _agent_k(s, 0.92)), None, group="shed")
    s.cast("caterpillar", 0.68, "point", "surprise", flip=True, mark="?")
    s.thing(lambda x, y, k: _toolbox(x, y, k), 0.83, 54, 46, nearer=0.2, name="toolbox")
    s.thing(lambda x, y, k: props.tulip(x - 8 * k, y, k * 0.8, P.RED) + props.tulip(x + 4 * k, y, k * 0.9, P.YELLOW)
            + props.daisy(x + 14 * k, y, k * 0.8), 0.95, 40, 50, name="flowers")
    bx = s.x(0.84)
    by = s.feet(bx) - 70 * k
    s.put(s.h, things.bee(bx, by, k), (bx - 40 * k, by - 14 * k, bx + 12 * k, by + 8 * k), "bee")


# ============================================================================ robot_anatomy: what an agent is made of
def podium_top(k: float) -> float:
    """How high the display stand's top is (in its own units) at scale k: tall enough for its name plate."""
    size = max(8.0, sets.LETTERING_MIN / k)
    return max(22.0, plate_size("A", size)[1] + 16)


def _podium(x: float, y: float, k: float = 1.0, label: str = "") -> str:
    """A round display stand with a name plate in the middle of its front (never under 9.5 units on the page;
    the stand grows taller and wider for it). About 84 wide, 26 tall."""
    size = max(8.0, sets.LETTERING_MIN / k)
    pw, ph = plate_size(label, size) if label else (0, 0)
    top = podium_top(k)
    hw = max(38.0, pw / 2 + 9)
    c = Canvas()
    c.shape(f"M{n(-hw)},{n(-top)} V-4 Q0,6 {n(hw)},-4 V{n(-top)} Z", P.VIOLET, sw=2, light=(-2, -2))
    c.shape(ellipse_d(0, -top, hw, 7), lighten(P.VIOLET, 0.3), sw=2, light=None)
    if label:
        _plate(c, 0, (-top + 5) / 2, label, size, k)    # the middle of the front, under the top's rim
    return _at(c, x, y, k)


def _model_box(x: float, y: float, k: float = 1.0, label: str = "") -> str:
    """A cabinet on legs with a glass dome on top, a glowing brain in it: the model. Its name plate is never
    under 9.5 units on the page (the cabinet widens for it). About 64 wide, 108 tall."""
    size = max(9.0, sets.LETTERING_MIN / k)
    w, ph = plate_size(label, size) if label else (0, 0)
    hw = max(30.0, w / 2 + 6)
    c = Canvas()
    c.line(f"M{n(-hw + 6)},0 V-14 M{n(hw - 6)},0 V-14", 3, P.METAL_DARK)
    c.shape(rounded_rect_d(-hw, -64, hw * 2, 52, 4), P.METAL_LIGHT, sw=2, light=(-2, -2), shade_k=0.85)
    for i, color in enumerate((P.RED, P.GREEN, P.YELLOW)):
        c.add(f'<circle cx="{-16 + i * 8}" cy="-22" r="2.6" fill="{color}" stroke="{INK}" stroke-width="1"/>')
    c.shape(ellipse_d(14, -22, 6, 6), P.CARD, sw=1.4, light=None)
    c.line("M14,-22 l3,-4", 1.2)
    if label:
        _plate(c, 0, -58 + ph / 2, label, size, k)
    c.add(f'<ellipse cx="0" cy="-86" rx="30" ry="26" fill="{P.SUN}" opacity=".18"/>')
    c.shape("M-20,-64 Q-22,-104 0,-104 Q22,-104 20,-64 Z", lighten(P.WATER_LIGHT, 0.5), sw=1.8, light=None)
    c.shape("M-12,-72 Q-16,-90 -4,-92 Q2,-98 8,-92 Q16,-90 13,-78 Q14,-70 4,-70 Q-6,-68 -12,-72 Z", P.PINK_PALE,
            sw=1.5, light=(-1, -1))
    c.line("M-6,-88 q4,4 0,8 M4,-90 q-3,5 2,10 M0,-74 q4,-3 8,0", 1, P.PINK)
    c.line("M-22,-102 l-4,-4 M22,-102 l4,-4 M0,-108 V-113", 1.6, P.SUN)
    return _at(c, x, y, k)


def _callout(c: Canvas, part: tuple[float, float], at: tuple[float, float], text: str, size: float,
             side: str, k: float = 1.0) -> tuple:
    """A label plate whose near end is at `at`, and a dotted leader from that end to the very part it names,
    ending in a dot on the part; returns the plate's box."""
    w = sets.letter_width(text, size) + size * 1.1
    lx = at[0] - w if side == "left" else at[0]
    c.add(f'<path d="M{n(at[0])},{n(at[1])} L{n(part[0])},{n(part[1])}" fill="none" stroke="{INK}" '
          f'stroke-width="1.3" stroke-dasharray="2.4 2.2" stroke-linecap="round"/>')
    r = 2.6 * min(1.0, k)
    c.add(f'<circle cx="{n(part[0])}" cy="{n(part[1])}" r="{n(r)}" fill="{P.RED}" stroke="{INK}" '
          f'stroke-width="{n(r * 0.4)}"/>')
    h = size * 1.5
    c.shape(rounded_rect_d(lx, at[1] - h / 2, w, h, size * 0.35), P.CARD, sw=1.4, light=None)
    sets.fit_label(c, lx + w / 2, at[1] + size * 0.36, text, size, w - size * 0.5)
    return (lx, at[1] - h / 2, lx + w, at[1] + h / 2)


def _on_agent(box: Box, point: tuple[float, float]) -> tuple[float, float]:
    """A point of the agent's own canvas (unflipped) on the page."""
    mod = module("agent")
    k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
    return (box.left + box.right) / 2 + (point[0] - mod.CENTER_X) * k, box.bottom - (mod.FEET_Y - point[1]) * k


@episode("robot_anatomy")
def robot_anatomy(s: Strip) -> None:
    """A lesson in what an agent is: it stands on a display stand with labelled callouts - its eyes read the
    files, its ears take your prompt, its hands are the tools, its chest is the terminal - and a cable runs from
    its aerial to a cabinet with a brain under glass, the model. The professor points at it with a long pointer;
    the caterpillar takes notes."""
    s.indoors()
    k = s.unit
    x, y = s.x(0.42), s.feet(0)
    top = podium_top(k)
    lift = (top - 1) * k
    hw = max(42.0, plate_size(s.word("agent"), max(8.0, sets.LETTERING_MIN / k))[0] / 2 + 13) * k
    s.put(y, _podium(x, y, k, s.word("agent")), (x - hw, y - (top + 8) * k, x + hw, y), "stand")
    agent = s.actor("agent", x, y - lift, "shrug", "smile", flip=False, tall=s.tall, group="stand", depth=y + 1)
    h = agent.bottom - agent.top
    size = max(sets.LETTERING_MIN, 8.4 * k)
    c = Canvas()
    boxes = []
    lhx, lhy, _, _ = _palm(agent, "shrug", False, "left")
    gap = 16 * k + 6
    top = max(agent.top + size * 0.8, s.base * 0.22 + size)
    low = max(top + size * 2.2, top + h * 0.45)
    boxes.append(_callout(c, _on_agent(agent, (92, 73)), (agent.left - gap, top), s.word("eyes"), size, "left", k))
    boxes.append(_callout(c, (lhx, lhy), (agent.left - gap, low), s.word("hands"), size, "left", k))
    boxes.append(_callout(c, _on_agent(agent, (168, 80)), (agent.right + gap, top), s.word("ears"), size,
                          "right", k))
    boxes.append(_callout(c, _on_agent(agent, (126, 168)), (agent.right + gap, low), s.word("wheels"), size,
                          "right", k))
    s.put(s.h, c.render(), boxes, group="stand")
    # The professor at the left, his pointer from his hand to the callouts.
    reach = min(b[0] for b in boxes[:2]) - 4
    ox, _ = _palm_offset("professor", "present", s.tall)
    half = module("professor").SIZE[0] * 0.40 * s.tall / PROFESSOR_HEIGHT
    px0 = max(s.lo + half, min(s.x(0.08), reach - 60 * k - ox))
    prof = s.actor("professor", px0, s.feet(0), "present", "talk", flip=False, tall=s.tall, group="prof")
    wx, wy, _, _ = _palm(prof, "present", False)
    tip = (reach, (boxes[0][3] + boxes[1][1]) / 2)
    a = math.atan2(tip[1] - wy, tip[0] - wx)
    bx, by = wx - math.cos(a) * 8 * k, wy - math.sin(a) * 8 * k
    c = Canvas()
    c.line(f"M{n(bx)},{n(by)} L{n(tip[0])},{n(tip[1])}", 2.4 * k + 2.2)
    c.line(f"M{n(bx)},{n(by)} L{n(tip[0])},{n(tip[1])}", 2.4 * k, P.WOOD_DARK)
    c.dot(tip[0], tip[1], 1.6 * k + 1, P.WHITE)
    s.put(prof.bottom + 1, c.render(), None, group="prof")
    # The cable from its aerial, over everyone's heads, to the model: the brain is somewhere else.
    mx, my = s.thing(lambda x, y, k: _model_box(x, y, k, s.word("model")), 0.75, 70, 112, name="model")
    hx0, hy0 = _on_agent(agent, (112, 4))
    hx1, hy1 = mx, my - 108 * k
    up = max(s.base * 0.22, min(hy0, hy1) - 30 * k)
    d = f"M{n(hx0)},{n(hy0)} C{n(hx0 + 10 * k)},{n(up)} {n(hx1 - 30 * k)},{n(up)} {n(hx1)},{n(hy1)}"
    c = Canvas()
    c.line(d, 3 * k + 2.4)
    c.line(d, 3 * k, P.BLUE)
    c.line(d, 1 * k, lighten(P.BLUE, 0.5), 0.7)
    s.put(s.h + 1, c.render(), None)
    s.cast("caterpillar", 0.94, "write", "smile", flip=True)


# ============================================================================ library_pass: show your pass
def _book_pile(x: float, y: float, k: float = 1.0) -> str:
    """A pile of books waiting to be given out: three lying flat - two showing their spines with gilt bands,
    one its page block between its covers - and one standing on top with a title panel on its cover and a
    ribbon bookmark. 50 wide, 62 tall."""
    c = Canvas()
    gold = P.SUN
    # the bottom book: its spine towards us
    c.shape(rounded_rect_d(-25, -12, 50, 12, 2.5), P.RED, sw=1.8, light=(-1, -1), shade_k=0.85)
    c.line("M-17,-12 V0 M17,-12 V0", 1.6, gold)
    c.shape(rounded_rect_d(-8, -9, 16, 6, 1), P.CREAM, sw=1, light=None)
    # the middle book: its page block, the covers above and below it
    c.shape(rounded_rect_d(-21, -22, 44, 10, 1.5), P.BLUE, sw=1.6, light=None)
    c.shape("M-19,-20.4 H23 V-13.6 H-19 Z", P.CARD, sw=1.1, light=None)
    c.line("M-17,-18.6 H22 M-17,-17 H22 M-17,-15.4 H22", 0.6, opacity=0.4)
    # the top flat book
    c.shape(rounded_rect_d(-23, -30, 42, 8, 2), P.GREEN, sw=1.6, light=(-1, -1), shade_k=0.85)
    c.line("M-15,-30 V-22 M11,-30 V-22", 1.3, gold)
    # the book standing on top: front cover with a panel, the spine's edge on the left, a ribbon from below
    c.shape("M-12,-30 V-60 Q-12,-62 -10,-62 H-7 V-30 Z", darken(P.ORANGE, 0.85), sw=1.4, light=None)
    c.shape(rounded_rect_d(-7, -62, 22, 32, 2), P.ORANGE, sw=1.7, light=(-1, -1), shade_k=0.85)
    c.shape(rounded_rect_d(-3, -55, 14, 9, 1.5), P.CREAM, sw=1, light=None)
    c.line("M-1,-52 h10 M-1,-49 h7", 0.9, opacity=0.6)
    c.shape("M9,-30 V-24 L11,-26 L13,-24 V-30 Z", P.RED, sw=1, light=None)
    return _at(c, x, y, k)


def _pass_card(x: float, y: float, k: float = 1.0) -> str:
    """A reader's pass: a photo, a name line and a barcode; the origin is its centre. 30 by 20."""
    c = Canvas()
    c.shape(rounded_rect_d(-15, -10, 30, 20, 2), P.CARD, sw=1.4, light=None)
    c.path("M-12,-7 H-3 V3 H-12 Z", P.SKY, 1)
    c.add(f'<circle cx="-7.5" cy="-1.5" r="3" fill="{P.FEATHER}"/>')
    c.line("M0,-6 h11 M0,-3 h8", 1, opacity=0.6)
    for i, w in enumerate((1, 0.5, 1.2, 0.5, 0.8, 1.2, 0.5, 1, 0.6, 1.2, 0.5)):
        c.add(f'<rect x="{n(-12 + i * 2.2)}" y="4" width="{n(w)}" height="4" fill="{INK}"/>')
    return _at(c, x, y, k)


def _library_desk(x: float, y: float, k: float = 1.0) -> str:
    """The librarian's counter: a green lamp, a stamp on its pad and a pile of tagged books. 136 wide, 92 tall."""
    c = Canvas()
    c.shape("M-62,0 V-50 H62 V0 Z", P.WOOD, sw=2.2, light=(-2, -2), shade_k=0.85)
    for px in (-40, 0, 40):
        c.path(rounded_rect_d(px - 16, -42, 32, 34, 3), "none", 1.2, darken(P.WOOD, 0.75))
    c.shape(rounded_rect_d(-68, -56, 136, 8, 2), P.WOOD_LIGHT, sw=1.8, light=None)
    c.line("M-56,-56 V-80 L-46,-88", 2.4, P.LEAF_DARK)                            # the lamp
    c.shape(ellipse_d(-56, -57, 8, 2.4), P.LEAF_DARK, sw=1.4, light=None)
    c.shape("M-52,-94 L-34,-86 L-40,-78 L-56,-86 Z", P.LEAF, sw=1.6, light=(-1, -1))
    c.add(f'<path d="M-40,-80 L-30,-58 H-6 L-34,-84 Z" fill="{P.SUN}" opacity=".22"/>')
    c.shape(rounded_rect_d(36, -60, 22, 4, 1.5), P.RED, sw=1.2, light=None)          # the stamp on its pad
    c.shape("M43,-60 V-66 H51 V-60 Z", P.WOOD_DARK, sw=1.4, light=None)
    c.shape(ellipse_d(47, -70, 4, 4), P.WOOD_DARK, sw=1.4, light=None)
    for i, color in enumerate((P.BLUE, P.YELLOW, P.PINK)):
        by = -56 - i * 7
        c.shape(rounded_rect_d(-24 + i, by - 7, 26 - i * 2, 7, 1.5), color, sw=1.2, light=None)
    c.line("M2,-63 q5,1 6,7", 0.9)
    c.shape("M5,-58 h7 v5 h-7 Z", P.CARD, sw=0.9, light=None)
    return _at(c, x, y, k)


def _hand_scanner(x: float, y: float, k: float, turn: float, mirror: bool) -> str:
    """A hand scanner held by its handle at the origin, its red window pointing along `turn`."""
    c = Canvas()
    c.shape("M-3,-4 L3,-4 L1,10 Q0,12 -3,11 Z", P.CHARCOAL, sw=1.3, light=None)
    c.shape(rounded_rect_d(-8, -11, 22, 8, 3), P.CHARCOAL, sw=1.4, light=(-1, -1))
    c.shape(rounded_rect_d(12, -10, 4, 6, 1.5), P.RED, sw=1, light=None)
    c.dot(-3, -7, 1, P.GREEN)
    sx = -k if mirror else k
    return f'<g transform="translate({n(x)},{n(y)}) rotate({n(turn)}) scale({n(sx)},{n(k)})">{c.render()}</g>'


def _wing_grip(box: Box, pose: str, flip: bool) -> tuple[float, float]:
    """Where the sparrow's near wing holds something: near its feather tips (he has wings, not wrists)."""
    mod = module("sparrow")
    angle = math.radians(mod.POSES[pose][2])
    cx, cy = 142 + 50 * math.cos(angle), 110 + 50 * math.sin(angle)
    k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
    mid = (box.left + box.right) / 2
    dx = (cx - mod.CENTER_X) * k
    return (mid - dx if flip else mid + dx), box.bottom - (mod.FEET_Y - cy) * k


def _book_cart(x: float, y: float, k: float = 1.0) -> str:
    """A library trolley of books, each with a paper tag on a string. 76 wide, 76 tall."""
    rnd = random.Random(7)
    c = Canvas()
    c.line("M-32,-6 V-70 M32,-6 V-70", 3, P.METAL_DARK)
    c.line("M32,-70 l6,-6", 3, P.METAL_DARK)
    for shelf in (-6, -40):
        c.shape(rounded_rect_d(-36, shelf - 4, 72, 5, 1.5), P.WOOD, sw=1.4, light=None)
        bx = -32.0
        while bx < 26:
            w = rnd.choice((6, 7, 8))
            h = rnd.choice((22, 26, 28))
            color = rnd.choice(P.BRIGHTS)
            c.path(f"M{n(bx)},{shelf - 4} V{shelf - 4 - h} H{n(bx + w)} V{shelf - 4} Z", color, 1.2)
            if rnd.random() < 0.45:
                c.line(f"M{n(bx + w / 2)},{shelf - 4 - h + 4} l3,10", 0.8)
                c.shape(f"M{n(bx + w / 2 + 1)},{shelf + 8 - h} h6 v5 h-6 Z", P.CARD, sw=0.8, light=None)
            bx += w + 0.6
    for wx in (-28, 28):
        c.shape(ellipse_d(wx, -3, 4, 4), P.CHARCOAL, sw=1.2, light=None)
    return _at(c, x, y, k)


def _catalogue(x: float, y: float, k: float = 1.0) -> str:
    """A card catalogue of little drawers with brass pulls, a tiny red book left on top. 44 wide, 92 tall."""
    c = Canvas()
    c.shape("M-20,0 V-64 H20 V0 Z", P.WOOD_DARK, sw=2, light=(-2, -2))
    for row in range(4):
        for col in range(2):
            dx, dy = -17 + col * 18, -60 + row * 15
            c.path(rounded_rect_d(dx, dy, 16, 12, 1.5), P.WOOD, 1.1)
            c.line(f"M{dx + 5},{dy + 7} h6", 1.6, P.SUN)
    c.shape("M-12,-70 L-2,-67 L8,-70 L8,-64 L-2,-62 L-12,-64 Z", P.RED, sw=1, light=None)
    return _at(c, x, y, k)


@episode("library_pass")
def library_pass(s: Strip) -> None:
    """At the library the agent scans the reader's pass before it gives out a single book: the sparrow holds up
    his, barcode and all, and the red beam of the hand scanner falls on it. Books wear paper tags on the
    trolley, a pile of books waits to be given out, a book lies on top of the card catalogue, and a sign on
    the wall asks for quiet."""
    s.indoors()
    k = s.unit
    shelves = 3 if s.h >= 200 else 2
    # Everything stands in a row; the row is packed by the widths at this scale, the pile of books left out when
    # the strip is too narrow for them.
    kb = s.tall / PROFESSOR_HEIGHT
    row = [("shelf", 110 * k), ("books", 50 * k), ("bird", 160 * 0.95 * kb + 40 * k), ("agent", 176 * 0.92 * kb),
           ("desk", 140 * k), ("cart", 80 * k), ("catalogue", 44 * k)]
    room = s.hi - s.lo
    if room - sum(w for _, w in row) < 10 * 8:
        row = [item for item in row if item[0] != "books"]
    gap = (room - sum(w for _, w in row)) / (len(row) - 1)
    at, x = {}, s.lo
    for name, w in row:
        at[name] = (x + w / 2 - s.lo) / room
        x += w + gap
    at["bird"] -= 20 * k / room                   # the card he holds out is the right part of his room
    s.thing(lambda x, y, k: props.bookshelf(x, y, k * 0.95, s.seed, shelves), at["shelf"], 110, 50 * shelves + 10,
            name="shelf", backdrop=True)
    if "books" in at:
        s.thing(lambda x, y, k: _book_pile(x, y, k), at["books"], 50, 64, name="books")
    bird = s.cast("sparrow", at["bird"], "present", "smile", flip=False, group="bird")
    gx, gy = _wing_grip(bird, "present", False)
    cx, cy = gx + 13 * k, gy - 8 * k
    # the card, then his wing again over its edge: the finger feathers close over the card, so it is held
    smod = module("sparrow")
    kb = (bird.bottom - bird.top) / (smod.FEET_Y - smod.HEAD_TOP)
    wing = Canvas()
    smod._wing(wing, 142, 110, smod.POSES["present"][2])
    ox, oy = (bird.left + bird.right) / 2 - smod.CENTER_X * kb, bird.bottom - smod.FEET_Y * kb
    s.put(bird.bottom + 1, _pass_card(cx, cy, k * 1.1) + _at(wing, ox, oy, kb),
          (cx - 17 * k, cy - 11 * k, cx + 17 * k, cy + 11 * k), group="bird")
    agent = s.cast("agent", at["agent"], "point", "smile", flip=True, group="agent")
    ax, ay, _, _ = _palm(agent, "point", True)
    tx, ty = cx + 12 * k, cy - 2 * k
    turn = math.degrees(math.atan2(ty - ay, ax - tx))
    s.put(agent.bottom + 1, _hand_scanner(ax, ay, k * 0.9, -turn, True), None, group="agent")
    a = math.radians(180 - turn)
    hx, hy = ax + math.cos(a) * 15 * k, ay + math.sin(a) * 15 * k - 6 * k
    c = Canvas()        # the red beam from the scanner's window to the barcode
    c.add(f'<path d="M{n(hx)},{n(hy - 1.5 * k)} L{n(cx + 13 * k)},{n(cy + 1 * k)} L{n(cx + 13 * k)},'
          f'{n(cy + 9 * k)} L{n(hx)},{n(hy + 1.5 * k)} Z" fill="{P.RED}" opacity=".32"/>')
    c.line(f"M{n(cx - 13 * k)},{n(cy + 6 * k)} H{n(cx + 13 * k)}", 1.2 * k, P.RED, 0.9)
    s.put(bird.bottom + 2, c.render(), None, group="bird")
    s.thing(lambda x, y, k: _library_desk(x, y, k), at["desk"], 140, 96, name="desk")
    s.thing(lambda x, y, k: _book_cart(x, y, k), at["cart"], 80, 78, name="cart")
    s.thing(lambda x, y, k: _catalogue(x, y, k), at["catalogue"], 44, 92, name="catalogue")
    if s.h >= 200:      # the sign hangs on a nail, its string over it
        size = 11.0
        w = plate_size(s.word("quiet"), size)[0]
        wx = s.x(at.get("books", at["bird"]))
        wy = max(s.base * 0.32, min(s.base * 0.5, s.feet(0) - 90 * k - 30))
        box = (wx - w / 2 - 2, wy - 16 - size, wx + w / 2 + 2, wy + size)
        if s.free(box, 8):
            c = Canvas()
            c.line(f"M{n(wx - w / 2 + 8)},{n(wy - size * 0.8)} L{n(wx)},{n(wy - 14 - size)} "
                   f"L{n(wx + w / 2 - 8)},{n(wy - size * 0.8)}", 1.2)
            c.dot(wx, wy - 14 - size, 2, P.METAL_DARK)
            _plate(c, wx, wy, s.word("quiet"), size, r=3)
            s.put(2, c.render(), box, "quiet")


# ============================================================================ guard_dog: Tyapa guards the secrets
def _robot_dog(x: float, y: float, k: float = 1.0) -> str:
    """Tyapa, the robot dog: white boxes for a body and a head, antenna ears, bared teeth, a spring for a tail.
    Faces right. 84 wide, 78 tall; its head is the box (18..48, -62..-36)."""
    c = Canvas()
    c.line("M-30,-30 l-4,-6 l6,-3 l-6,-3 l6,-3 l-6,-3 l6,-3 l-4,-4", 2.2, P.METAL_DARK)   # the spring tail
    c.add(f'<circle cx="-36" cy="-60" r="3.4" fill="{P.RED}" stroke="{INK}" stroke-width="1.2"/>')
    for lx in (-22, -12, 10, 20):
        c.shape(f"M{lx - 3},-18 V-2 H{lx + 4} V-18 Z", P.METAL_PALE, sw=1.6, light=None)
        c.shape(rounded_rect_d(lx - 5, -4, 11, 5, 2), P.CHARCOAL, sw=1.2, light=None)
    c.shape(rounded_rect_d(-30, -40, 58, 24, 3), P.WHITE, sw=2, light=(-2, -2), shade_k=0.88)
    c.shape(rounded_rect_d(-16, -36, 16, 10, 2), P.RED, sw=1.2, light=None)
    c.dot(-8, -31, 1.4, P.WHITE)
    c.shape(rounded_rect_d(18, -62, 30, 26, 3), P.WHITE, sw=2, light=(-2, -2), shade_k=0.88)
    c.line("M24,-62 L18,-74 M38,-62 L44,-74", 1.6)
    c.add(f'<circle cx="18" cy="-75" r="2.4" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>'
          f'<circle cx="44" cy="-75" r="2.4" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>')
    c.line("M26,-56 l6,3 M44,-56 l-6,3", 1.8)
    c.dot(30, -51, 1.8)
    c.dot(40, -51, 1.8)
    c.shape("M28,-44 H48 V-38 H28 Z", P.CHARCOAL, sw=1.2, light=None)
    c.path("M30,-44 l2,3 l2,-3 l2,3 l2,-3 l2,3 l2,-3 l2,3 l2,-3", P.WHITE, 0.8)
    c.line("M52,-52 l6,-3 M52,-46 h7 M52,-40 l6,3", 1.4)
    return _at(c, x, y, k)


def _label_size(k: float, base: float = 10.0) -> float:
    """A label's size on a prop drawn at scale k, so that it is never under 9.5 units on the page."""
    return max(base, sets.LETTERING_MIN / k)


def chest_size(k: float, label: str = "") -> tuple[float, float]:
    """The toy chest's half-width and front height at scale k: roomy enough for its label with a margin."""
    if not label:
        return 34.0, 36.0
    w, h = plate_size(label, _label_size(k))
    return max(34.0, w / 2 + 10), max(36.0, h + 14)


def _toy_chest(x: float, y: float, k: float = 1.0, label: str = "") -> str:
    """A wooden toy chest shut with a padlock, a label in the middle of its front. 74 wide, 52 tall at the
    least; it grows for a label that must stay readable on the page."""
    hw, fh = chest_size(k, label)
    c = Canvas()
    c.shape(f"M{n(-hw)},0 V{n(-fh)} H{n(hw)} V0 Z", P.BLUE, sw=2, light=(-2, -2))
    c.shape(f"M{n(-hw - 2)},{n(-fh)} Q{n(-hw - 2)},{n(-fh - 16)} 0,{n(-fh - 16)} "
            f"Q{n(hw + 2)},{n(-fh - 16)} {n(hw + 2)},{n(-fh)} Z", lighten(P.BLUE, 0.2), sw=2, light=None)
    c.line(f"M{n(-hw)},-6 H{n(hw)} M{n(-hw + 8)},0 V{n(-fh)} M{n(hw - 8)},0 V{n(-fh)}", 1.6, P.SUN)
    if label:
        _plate(c, 0, -fh / 2 - 2, label, _label_size(k), k, P.CARD, P.RED)
    lock = -fh - 4
    c.add(f'<path d="M-4,{n(lock)} v-4 a4,4 0 0 1 8,0 v4" fill="none" stroke="{P.METAL_DARK}" stroke-width="2"/>')
    c.shape(rounded_rect_d(-6, lock - 1, 12, 9, 2), P.SUN, sw=1.4, light=None)
    c.dot(0, lock + 3, 1.3)
    return _at(c, x, y, k)


def _ring_pyramid(x: float, y: float, k: float = 1.0) -> str:
    """A stacking toy: rings from big to small on a stick, a ball on top. 36 wide, 60 tall."""
    c = Canvas()
    c.line("M0,-4 V-52", 3, P.WOOD_DARK)
    c.shape(rounded_rect_d(-18, -6, 36, 6, 2), P.WOOD, sw=1.4, light=None)
    for i, color in enumerate((P.RED, P.ORANGE, P.YELLOW, P.GREEN, P.BLUE)):
        w = 16 - i * 2.4
        c.shape(ellipse_d(0, -11 - i * 8, w, 4.4), color, sw=1.4, light=(-1, -1))
    c.shape(ellipse_d(0, -54, 5, 5), P.VIOLET, sw=1.4, light=None)
    return _at(c, x, y, k)


def _beach_ball(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    clip = c.shape(ellipse_d(0, -13, 13, 13), P.WHITE, sw=1.8, light=None, clip=True)
    c.add(f'<g clip-path="url(#{clip})"><path d="M-13,-26 Q-2,-13 -13,0 H-4 Q4,-13 -4,-26 Z" fill="{P.RED}"/>'
          f'<path d="M4,-26 Q12,-13 4,0 H13 V-26 Z" fill="{P.BLUE}"/></g>')
    c.path(ellipse_d(0, -13, 13, 13), "none", 1.8)
    c.line("M-6,-20 q-2,3 -1,6", 1.4, P.WHITE, 0.7)
    return _at(c, x, y, k)


def kennel_size(k: float, sign: str = "") -> tuple[float, float]:
    """The doghouse's half-width and wall height at scale k: the name board sits on the wall over the door
    with a margin all round."""
    if not sign:
        return 30.0, 46.0
    w, h = plate_size(sign, _label_size(k, 9.0))
    return max(30.0, w / 2 + 6), max(46.0, 30 + h + 5)


def _kennel(x: float, y: float, k: float = 1.0, sign: str = "") -> str:
    """A doghouse with a name board on its wall over the round door and a bowl beside it. 80 wide, 80 tall at
    the least; it grows for a name that must stay readable on the page."""
    hw, wh = kennel_size(k, sign)
    ridge = wh + hw * 26 / 30
    c = Canvas()
    c.shape(f"M{n(-hw)},0 V{n(-wh)} L0,{n(-ridge)} L{n(hw)},{n(-wh)} V0 Z", P.WOOD_LIGHT, sw=2, light=(-2, -2))
    e = hw + 6
    c.shape(f"M{n(-e)},{n(-wh + 4)} L0,{n(-ridge - 6)} L{n(e)},{n(-wh + 4)} L{n(e - 4)},{n(-wh + 8)} "
            f"L0,{n(-ridge + 2)} L{n(-e + 4)},{n(-wh + 8)} Z", P.RED, sw=1.8, light=None)
    c.path("M-11,0 V-14 Q-11,-25 0,-25 Q11,-25 11,-14 V0 Z", P.DARK_BROWN, 1.8)
    if sign:
        size = _label_size(k, 9.0)
        _plate(c, 0, (-25 - wh + 8) / 2, sign, size, k)       # between the door's arch and the eaves
    c.shape(f"M{n(hw - 4)},0 L{n(hw - 2)},-7 H{n(hw + 14)} L{n(hw + 16)},0 Z", P.RED, sw=1.4, light=None)
    return _at(c, x, y, k)


def _bone(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.shape("M-12,-3 H12 Q14,-9 18,-6 Q21,-3 18,-1 Q21,2 17,4 Q13,5 12,1 H-12 Q-13,5 -17,4 Q-21,2 -18,-1 "
            "Q-21,-3 -18,-6 Q-14,-9 -12,-3 Z", P.CARD, sw=1.5, light=None)
    return _at(c, x, y - 4 * k, k, turn=-8)


def _blocks(x: float, y: float, k: float = 1.0) -> str:
    """Three toy blocks stacked crookedly. 40 wide, 50 tall."""
    c = Canvas()
    c.add(things.cube(-8, 0, 0.55, P.GREEN))
    c.add(things.cube(10, 0, 0.55, P.YELLOW))
    c.add(f'<g transform="rotate(8 0 -18)">{things.cube(2, -18, 0.55, P.RED)}</g>')
    return _at(c, x, y, k)


@episode("guard_dog")
def guard_dog(s: Strip) -> None:
    """Tyapa, the robot dog of white boxes with a spring for a tail, growls over the toy chest marked `.env`:
    the sparrow wanted just a peek, and is stopped short. The cat nods - that is what a guard is for. Around
    them the nursery: a doghouse with Tyapa's name, a bone, a stacking pyramid, a ball and toy blocks."""
    s.indoors()
    k = s.unit
    s.cast("cat", 0.06, "present", "wink", flip=False, mark="ok")
    khw, kwh = kennel_size(k, s.word("name"))
    s.thing(lambda x, y, k: _kennel(x, y, k, s.word("name")), 0.2, 2 * khw + 20, kwh + khw * 26 / 30 + 8,
            name="kennel")
    dx, dy = s.thing(lambda x, y, k: _robot_dog(x, y, k), 0.37, 92, 80, name="dog")
    chw, cfh = chest_size(k, s.word("env"))
    s.thing(lambda x, y, k: _toy_chest(x, y, k, s.word("env")), 0.53, 2 * chw + 4, cfh + 18, name="chest")
    s.cast("sparrow", 0.655, "point", "worry", flip=True, mark="!")
    head = Box(dx + 14 * k, dy - 80 * k, dx + 52 * k, dy - 36 * k, "dog", "dog")    # the head with its aerials
    # the dog is not a character module, so its mouth (the bared teeth) is given to the bubble by hand
    s.mouth = lambda box: (dx + 38 * k, dy - 41 * k)
    try:
        s.say(head, s.word("grr"), shout=True, size=max(sets.LETTERING_MIN, 11 * k), prefer="above")
    finally:
        del s.mouth
    s.thing(lambda x, y, k: _ring_pyramid(x, y, k), 0.78, 38, 60, name="pyramid")
    s.thing(lambda x, y, k: _beach_ball(x, y, k), 0.875, 28, 28, name="ball")
    s.thing(lambda x, y, k: _blocks(x, y, k), 0.96, 40, 42, name="blocks")
    s.thing(lambda x, y, k: _bone(x, y, k), 0.29, 42, 14, nearer=0.85, name="bone")


# ============================================================================ three_rules: be careful
def _icon_scissors(c: Canvas) -> None:
    """Pictogram: big open scissors, blades up and to the right, red ring handles down to the left, a glint on
    a sharp tip. Drawn round the pivot in a 64 x 40 box."""
    blade = "M-3,-3 Q12,-4.6 32,-0.4 Q33.4,0.4 32,1 Q14,2.4 -3,2.6 Z"
    shank = "M1,-2.4 L-11,-2.6 L-11,2.6 L1,2.4 Z"
    ring_o, ring_i = ellipse_d(-19, 0, 8.6, 6.2), ellipse_d(-19.6, 0, 5, 3.4)
    for a in (16, -16):         # the back blade first, then the front one
        g = Canvas()
        g.shape(shank, P.RED, sw=1.6, light=None)
        g.add(f'<path d="{ring_o} {ring_i}" fill="{P.RED}" fill-rule="evenodd" stroke="{INK}" stroke-width="1.7" '
              f'stroke-linejoin="round"/>')
        g.line("M-25,-3 q3,-3 8,-3", 1.3, P.WHITE, 0.6)
        g.shape(blade, P.METAL_LIGHT, sw=1.7, light=(-1, -1), shade_k=0.82)
        g.line("M2,-1.6 Q14,-2.8 27,-0.6", 1, P.WHITE, 0.9)
        c.add(f'<g transform="translate(-2,4) rotate({a})">{g.render()}</g>')
    c.shape(ellipse_d(-2, 4, 2.6, 2.6), P.METAL_DARK, sw=1.2, light=None)
    c.dot(-2, 4, 0.9, INK)
    # the glint on the tip of the upper blade: a little four-pointed star
    gx, gy = 29.5, -6.5
    c.path(f"M{gx},{gy - 5} Q{gx + 0.8},{gy - 0.8} {gx + 5},{gy} Q{gx + 0.8},{gy + 0.8} {gx},{gy + 5} "
           f"Q{gx - 0.8},{gy + 0.8} {gx - 5},{gy} Q{gx - 0.8},{gy - 0.8} {gx},{gy - 5} Z", P.SUN, 1.1)


def _icon_glue(c: Canvas) -> None:
    """Pictogram: a tube of glue lying on its side, a drop stretching from its nozzle down into a puddle on a
    thread of glue. Drawn in a 64 x 40 box round its middle."""
    glue = lighten(P.YELLOW, 0.5)
    c.shape("M8,15.6 Q8,12.4 14,12.2 Q17,10.6 22,11.6 Q30,12 30,15 Q30,18 21,18 Q9,18.4 8,15.6 Z", glue, sw=1.4,
            light=None)                                                              # the puddle
    c.shape("M-30,-15 H-23 V5 H-30 Z", P.METAL_LIGHT, sw=1.6, light=None)           # the crimped end
    c.line("M-28,-13 V3 M-25.5,-13 V3", 0.9, opacity=0.55)
    c.shape("M-23,-14 H4 Q13,-14 15,-8.5 H21 V-1.5 H15 Q13,4 4,4 H-23 Z", P.WHITE, sw=1.8, light=(-1, -1),
            shade_k=0.88)
    c.shape(rounded_rect_d(-19, -10.5, 20, 11, 2), P.ORANGE, sw=1.3, light=None)   # the label
    c.line("M-15,-5 h12", 1.6, P.WHITE, 0.85)
    # a drop stretching from the nozzle, another falling into the puddle
    c.shape("M19.6,-4.6 H24.4 Q25.6,1 24.6,3.4 Q22,6.6 19.6,3.4 Q18.6,1 19.6,-4.6 Z", glue, sw=1.4, light=None)
    c.shape("M22,6.6 Q25,10.4 24.4,11.8 Q22,14 19.6,11.8 Q19,10.4 22,6.6 Z", glue, sw=1.3, light=None)
    c.line("M20.8,-1.6 q0.2,2 1,3", 1, P.WHITE, 0.9)


def _icon_papers(c: Canvas) -> None:
    """Pictogram: three sheets of paper blown away to the right, two gusts of wind curling behind them. Drawn
    in a 64 x 40 box round its middle."""
    for d in ("M-31,-7 Q-20,-11 -12,-8 Q-6,-5.6 -8.4,-2 Q-11,0.8 -13,-2.4",
              "M-31,6 Q-21,3 -14,6 Q-9,8.4 -11.4,11.4 Q-14,13.6 -15.4,10.6"):
        c.line(d, 1.7, opacity=0.75)
    for sx, sy, turn, k in ((-1, 5, -18, 0.92), (13, -8, 16, 0.86), (26, 7, 38, 0.78)):
        c.add(_sheet(sx, sy, k, turn))


_ICONS = {"scissors": _icon_scissors, "glue": _icon_glue, "papers": _icon_papers}


def _ribbon(c: Canvas, bx: float, by: float, body: float, size: float, text: str) -> None:
    """A red banner centred at (bx, by): a body `body` wide and 1.5 em tall with the word on it, and two notched
    tails tucked behind it, 0.55 em out on each side and no taller than the body. Its whole width is
    `body + 1.1 em`, its height 1.5 em."""
    bh, tail = size * 1.5, size * 0.55
    red = darken(P.RED, 0.78)
    for side in (-1, 1):
        ox = bx + side * (body / 2 - tail * 0.6)
        end = bx + side * (body / 2 + tail)
        c.shape(f"M{n(ox)},{n(by - bh * 0.36)} H{n(end)} L{n(end - side * tail * 0.5)},{n(by)} "
                f"L{n(end)},{n(by + bh * 0.36)} H{n(ox)} Z", red, sw=1.3, light=None)
    c.shape(f"M{n(bx - body / 2)},{n(by - bh / 2)} H{n(bx + body / 2)} V{n(by + bh / 2)} H{n(bx - body / 2)} Z",
            P.RED, sw=1.5, light=(-1, -1), shade_k=0.88)
    sets.fit_label(c, bx, by + size * 0.35, text, size, body - size * 0.6, P.WHITE)


def _rule_poster(x: float, nail: float, top: float, w: float, h: float, paper: str, icon: str, text: str,
                 size: float, longest: str = "") -> str:
    """A framed warning poster hanging on a string from a nail: a pictogram, and its word on a red banner.
    `nail` is the nail's height, `top` the frame's top edge; all in page units. The banner is sized for the
    `longest` of the words, so posters drawn side by side are laid out exactly alike. A tall poster stacks
    the picture over the banner; a low one puts them side by side, the pair centred on the paper. Everything
    keeps an even margin from the paper's edges."""
    c = Canvas()
    f = max(3.6, min(w, h) * 0.075)                                   # the frame's width
    ex = w * 0.3
    sw = max(1.1, f * 0.26)
    c.line(f"M{n(x - ex)},{n(top + f * 0.5)} L{n(x)},{n(nail)} L{n(x + ex)},{n(top + f * 0.5)}", sw, P.CHARCOAL)
    c.shape(rounded_rect_d(x - w / 2, top, w, h, f * 0.6), P.WOOD, sw=1.8, light=(-1.5, -1.5), shade_k=0.82)
    c.shape(rounded_rect_d(x - w / 2 + f, top + f, w - 2 * f, h - 2 * f, f * 0.25), paper, sw=1.3, light=None)
    for side in (-1, 1):
        c.dot(x + side * ex, top + f * 0.5, max(0.9, f * 0.2), P.WOOD_DARK)
    c.shape(ellipse_d(x, nail, max(1.8, f * 0.45), max(1.8, f * 0.45)), P.METAL, sw=1.2, light=(-0.6, -0.6))
    iw, ih = w - 2 * f, h - 2 * f
    cy = top + h / 2
    pad = max(3.0, min(iw, ih) * 0.13)
    em = sets.letter_width(longest or text, 10) / 10                  # the longest word's width per unit of size
    stacked = ih - 2 * pad - size * 1.5 - pad * 0.6 >= 18
    if stacked:
        size = max(sets.LETTERING_MIN, min(size, (iw - 2 * pad) / (em + 1.7)))
        if ih - 2 * pad - size * 1.5 - pad * 0.6 < ih * 0.45:          # a small room: the picture comes first
            size = sets.LETTERING_MIN
        body = min(iw - 2 * pad - size * 1.1, max(size * (em + 0.6), (iw - 2 * pad) * 0.7 - size * 1.1))
        bx, by = x, top + h - f - pad - size * 0.75
        pic = (x - iw / 2 + pad, top + f + pad, x + iw / 2 - pad, by - size * 0.75 - pad * 0.6)
    else:                                                               # low: the picture beside the banner
        size = max(sets.LETTERING_MIN, min(size, (ih - 2 * pad) / 1.5))
        body = size * (em + 0.6)
        ribbon = body + size * 1.1
        ph = ih - 2 * pad
        pw = min(ph * 66 / 40, iw - 3 * pad - ribbon)
        ph = min(ph, pw * 40 / 66)
        gap = max(pad, (iw - pw - ribbon) * 0.12)
        left = x - (pw + gap + ribbon) / 2
        bx, by = left + pw + gap + ribbon / 2, cy
        pic = (left, cy - ph / 2, left + pw, cy + ph / 2)
    _ribbon(c, bx, by, body, size, text)
    pw, ph = pic[2] - pic[0], pic[3] - pic[1]
    kk = min(pw / 66, ph / 40)
    g = Canvas()
    _ICONS[icon](g)
    c.add(_at(g, (pic[0] + pic[2]) / 2, (pic[1] + pic[3]) / 2, kk))
    return c.render()


_CAP = 0.70     # the height of a capital in the lettering face, per unit of size


def _rules_board_size(title: str, size: float, k: float, room: float) -> tuple[float, float, float, bool]:
    """The rules board's width, height and margin, and whether its rules go in a row: in a column when the
    board fits in `room` (its height above the floor, leaving a post), in one row under the title otherwise.
    The margin is the same on all four sides: about 13% of the board's smaller side."""
    title_w = sets.letter_width(title, size)
    column = size * (_CAP + 0.42 + 0.45 + 3 * 1.2 + 2 * 0.45) + 1.1      # title, rule, three numbers in a column
    w = max(60 * k, title_w / 0.74)
    pad = max(4.0, min(w, column / 0.74) * 0.13)
    if column + 2 * pad <= room:
        return w, column + 2 * pad, pad, False
    line = size * (_CAP + 0.42 + 0.45 + 1.2) + 1.1                         # the numbers in one row
    w = max(title_w, size * 10.6) / 0.76
    pad = max(4.0, line / 0.74 * 0.13)
    return w, line + 2 * pad, pad, True


def _rules_board(x: float, feet: float, top: float, w: float, h: float, pad: float, row: bool, title: str,
                 size: float, k: float) -> str:
    """The professor's board on a post: the title over a red rule, then three numbered rules, in a column or in
    one row. The capitals of the title sit exactly `pad` below the top edge and the last number's circle
    exactly `pad` above the bottom edge, and the same margin is kept at the sides."""
    c = Canvas()
    c.line(f"M{n(x)},{n(feet - 2 * k)} V{n(top + h)}", 3.4 * k + 2.4)
    c.line(f"M{n(x)},{n(feet - 2 * k)} V{n(top + h)}", 3.4 * k, P.WOOD_DARK)
    c.shape(rounded_rect_d(x - 11 * k, feet - 4 * k, 22 * k, 5 * k, 2 * k), P.WOOD_DARK, sw=1.4, light=(-1, -1))
    c.shape(rounded_rect_d(x - w / 2, top, w, h, 3), P.CARD, sw=1.8, light=(-1, -1), shade_k=0.92)
    x0, x1, y0, y1 = x - w / 2 + pad, x + w / 2 - pad, top + pad, top + h - pad
    base = y0 + size * _CAP                                       # the capitals' top sits on the margin
    sets.fit_label(c, x, base, title, size, x1 - x0, P.RED)
    under = base + size * 0.42
    c.line(f"M{n(x0)},{n(under)} H{n(x1)}", max(1.0, size * 0.09), P.RED, 0.6)
    r = size * 0.6
    edge = 0.55                                                   # half the circle's outline
    stroke = max(1.4, size * 0.15)
    if row:
        cy = y1 - r - edge
        item = (x1 - x0) / 3
        spots = [(x0 + item * i + r + edge, cy, x0 + item * (i + 1) - size * 0.7) for i in range(3)]
    else:
        first, last = under + size * 0.45 + r + edge, y1 - r - edge
        step = (last - first) / 2
        spots = [(x0 + r + edge, first + step * i, x1 - (0, 0.18, 0.08)[i] * (x1 - x0)) for i in range(3)]
    for i, (cx, cy, end) in enumerate(spots):
        c.shape(ellipse_d(cx, cy, r, r), P.RED, sw=1.1, light=None)
        sets.fit_label(c, cx, cy + size * 0.95 * _CAP / 2, str(i + 1), size * 0.95, r * 1.6, P.WHITE)
        c.line(f"M{n(cx + r + size * 0.4)},{n(cy)} H{n(end)}", stroke, opacity=0.5)
    return c.render()


def _first_aid(x: float, y: float, k: float = 1.0) -> str:
    """A first-aid case standing on the floor: a white case with a lid seam, two catches on the seam, a carrying
    handle on two lugs, and a red cross in the middle of its front with even margins round it. 36 wide, 32
    tall."""
    c = Canvas()
    grip = "M-8,-25 V-29 Q-8,-32 -5,-32 H5 Q8,-32 8,-29 V-25"
    c.path(grip, "none", 4.6)
    c.path(grip, "none", 2.4, P.CHARCOAL)
    c.line("M-4.5,-31.2 H4.5", 0.9, P.WHITE, 0.5)
    for lx in (-8, 8):                                            # the lugs that hold the handle
        c.shape(rounded_rect_d(lx - 2.6, -26.4, 5.2, 3, 1), P.METAL, sw=1.1, light=None)
    c.shape(rounded_rect_d(-18, -24, 36, 24, 4), P.WHITE, sw=1.8, light=(-1.5, -1.5), shade_k=0.86)
    c.line("M-18,-18.5 H18", 1.2, opacity=0.5)                    # the lid seam
    for cx in (-12.5, 12.5):                                      # the catches across the seam
        c.shape(rounded_rect_d(cx - 2.4, -21, 4.8, 5, 1.2), P.METAL, sw=1.1, light=(-0.5, -0.5))
    # the cross, centred on the front face below the seam (-18.5..0): 11 tall, margins of 3.75 above and below
    c.shape("M-2.2,-14.75 H2.2 V-11.45 H5.5 V-7.05 H2.2 V-3.75 H-2.2 V-7.05 H-5.5 V-11.45 H-2.2 Z", P.RED,
            sw=1.2, light=None)
    return _at(c, x, y, k)


def _paper_plane(x: float, y: float, k: float = 1.0, mirror: bool = False, turn: float = 0) -> str:
    """A folded paper plane flying to the right (to the left when mirrored), its nose at the origin. 34 long."""
    c = Canvas()
    c.shape("M0,0 L-34,-11 L-25,-1 Z", P.WHITE, sw=1.5, light=None)                  # the far wing
    c.shape("M0,0 L-34,-11 L-21,6 Z", P.CARD, sw=1.6, light=(-1, -1), shade_k=0.85)  # the near wing
    c.shape("M0,0 L-21,6 L-24,9 Z", P.PAPER_FOLD, sw=1.3, light=None)                # the keel
    c.line("M-3,0 L-30,-9", 0.9, opacity=0.5)
    return _at(c, x, y, k, mirror=mirror, turn=turn)


@episode("three_rules")
def three_rules(s: Strip) -> None:
    """Three safety rules on framed posters hanging from nails on the wall, each with its pictogram and its word
    on a banner: scissors are sharp, glue is sticky, papers fly away. The professor presents the board of rules,
    a first-aid case at its foot; at the other end the caterpillar has just let a paper plane fly - right under
    the third rule."""
    s.indoors()
    k = s.unit
    feet = s.feet(0)
    size = max(sets.LETTERING_MIN, 10 * k)
    # The board of rules on its post, and the professor presenting it.
    title = s.word("rules")
    prof = s.cast("professor", 0.04, "present", "talk", flip=False, group="prof")
    px, py, _, _ = _palm(prof, "present", False)
    btop = max(s.base * 0.22, prof.top)
    bw, bh, bpad, row = _rules_board_size(title, size, k, feet - btop - max(14.0, (feet - btop) * 0.2))
    bx = px + 6 * k + bw / 2
    s.put(prof.bottom + 1, _rules_board(bx, feet, btop, bw, bh, bpad, row, title, size, k),
          (bx - bw / 2, btop, bx + bw / 2, feet), "board", group="prof")
    ka = k * 0.85
    ax, ay = bx + bw / 2 + 8 + 18 * ka, s.feet(0, 0.6)
    s.put(ay, _first_aid(ax, ay, ka), (ax - 18 * ka, ay - 33 * ka, ax + 18 * ka, ay), "aid")
    # The caterpillar at the far end, her hand up: the plane has just left it.
    cat = s.cast("caterpillar", 0.955, "wave", "wink", flip=True, nearer=0.15, group="cat")
    hx, hy = s.hand(cat, "wave", True)
    kc = (cat.bottom - cat.top) / 100
    climb = 14                                     # the nose up and to the left, away from her hand
    turn = climb + 18                              # the plane is drawn with its tail 18 degrees up
    a = math.radians(180 + climb)
    pk = kc * 1.05
    nx, ny = hx + math.cos(a) * 58 * kc, hy + math.sin(a) * 58 * kc - 4 * kc
    tx, ty = nx - math.cos(a) * 32 * pk, ny - math.sin(a) * 32 * pk     # the plane's tail
    c = Canvas()
    _arrow_lines(c, tx + math.cos(a) * 6 * kc, ty + math.sin(a) * 6 * kc, 180 + climb, kc, 3, 8)
    c.add(_paper_plane(nx, ny, pk, mirror=True, turn=turn))
    s.put(cat.bottom + 1, c.render(), (nx - 2 * kc, ny - 14 * kc, hx, ty + 12 * kc), "plane", group="cat")
    # The three posters on the wall, in a row at one height, well above the skirting board.
    low = s.base - 18 - max(8, s.h * 0.025)
    nail_min = max(s.h * 0.2, s.base * 0.24)
    hang = min(low - nail_min, s.tall * 0.78)
    drop = max(7, hang * 0.17)
    ph = hang - drop
    left = bx + bw / 2 + max(14, 10 * k)
    right = min(cat.left, nx - 4 * kc) - max(14, 10 * k)
    slot = (right - left) / 3
    gap = max(14, slot * 0.14)
    words = (s.word("sharp"), s.word("sticky"), s.word("fly"))
    psize = max(sets.LETTERING_MIN, min(16, ph * 0.16))
    longest = max(words, key=lambda word: sets.letter_width(word, 10))
    pw = min(slot - gap, max(ph * 1.25, sets.letter_width(longest, psize) + psize * 3.2))
    if ph < 56:                                                        # a low poster puts its picture beside
        pw = slot - gap
    bottom = min(low, prof.top + s.tall * 0.62)
    top = bottom - ph
    nail = top - drop
    papers = (P.YELLOW_PALE, P.PINK_PALE, lighten(P.TEAL, 0.72))
    for i, icon in enumerate(("scissors", "glue", "papers")):
        x = left + slot * (i + 0.5)
        s.put(3, _rule_poster(x, nail, top, pw, ph, papers[i], icon, words[i], psize, longest),
              (x - pw / 2, nail - 3, x + pw / 2, bottom), f"rule{i}")


# ============================================================================ water_robot: too eager to help
def _rain_barrel(x: float, y: float, k: float = 1.0) -> str:
    """A wooden rain barrel with iron hoops and a brass tap low on its left side; the hose screws onto the tap
    at (-27, -12). 46 wide, 58 tall."""
    c = Canvas()
    c.shape("M-18,0 Q-24,-28 -18,-56 H18 Q24,-28 18,0 Z", P.WOOD, sw=2, light=(-2, -2), shade_k=0.85,
            stipple=(8, -56, 14, 56, 14, "right"))
    for px in (-9, 0, 9):
        c.line(f"M{px},-55 Q{px * 1.2},-28 {px},-1", 1, opacity=0.4)
    for hy, hw in ((-48, 20), (-10, 20)):
        c.line(f"M{-hw},{hy} Q0,{hy + 3} {hw},{hy}", 3, P.METAL_DARK)
    c.shape(ellipse_d(0, -56, 18, 4), P.WATER, sw=1.6, light=None)
    c.shape("M-21,-14 H-27 V-10 H-21 Z", P.SUN, sw=1.2, light=None)
    c.shape("M-25,-14 V-19 H-21 V-14 Z", P.SUN, sw=1, light=None)
    return _at(c, x, y, k)


def _nozzle(x: float, y: float, k: float, turn: float) -> str:
    """A brass hose nozzle held at the origin, spraying along `turn`; the hose joins its back end, 9 behind."""
    c = Canvas()
    c.shape(rounded_rect_d(-9, -3, 12, 6, 2), P.GREEN, sw=1.3, light=None)
    c.shape("M3,-3.4 L12,-2.2 V2.2 L3,3.4 Z", P.SUN, sw=1.3, light=None)
    return _at(c, x, y, k, turn=turn)


def _brimming_pot(x: float, y: float, k: float = 1.0) -> str:
    """A pot of flowers watered far too much: the water stands over the rim and runs down both sides.
    34 wide, 48 tall."""
    c = Canvas()
    c.line("M-2,-20 Q-4,-32 -10,-38 M2,-20 Q4,-34 10,-40 M0,-20 V-44", 1.6, P.LEAF_DARK)
    c.shape("M-6,-26 q-7,-2 -9,-8 q7,0 9,8 Z M6,-28 q7,-2 9,-8 q-7,0 -9,8 Z", P.LEAF, sw=1, light=None)
    for fx, fy, color in ((-10, -38, P.PINK), (10, -40, P.YELLOW), (0, -44, P.RED)):
        c.add(f'<circle cx="{fx}" cy="{fy}" r="4.4" fill="{color}" stroke="{INK}" stroke-width="1.2"/>'
              f'<circle cx="{fx}" cy="{fy}" r="1.6" fill="{P.SUN}"/>')
    c.shape("M-13,-18 H13 L10,0 H-10 Z", P.TERRACOTTA, sw=1.8, light=(-1, -1))
    c.shape(rounded_rect_d(-15, -21, 30, 5, 2), darken(P.TERRACOTTA, 0.9), sw=1.4, light=None)
    c.shape("M-16,-21 Q-14,-26 0,-25 Q14,-26 16,-21 Q0,-19 -16,-21 Z", P.WATER, sw=1.2, light=None)
    for side in (-1, 1):
        c.path(f"M{side * 15},-21 Q{side * 17},-12 {side * 14},-6 Q{side * 13},-1 {side * 17},1 L{side * 19},0 "
               f"Q{side * 15},-3 {side * 17},-9 Q{side * 19},-16 {side * 16},-22 Z", P.WATER, 1.1)
    return _at(c, x, y, k)


def _crate_seat(x: float, y: float, w: float, h: float, k: float) -> str:
    """A plank crate `w` wide and `h` tall, standing with its foot's middle at (x, y): something to sit on."""
    c = Canvas()
    c.shape(rounded_rect_d(x - w / 2, y - h, w, h, 2 * k), P.WOOD_LIGHT, sw=2 * k, light=(-2 * k, -2 * k),
            shade_k=0.86)
    for i in range(1, 3):
        yy = y - h * i / 3
        c.line(f"M{n(x - w / 2)},{n(yy)} H{n(x + w / 2)}", 1.3 * k, opacity=0.55)
    c.line(f"M{n(x - w / 2 + 4 * k)},{n(y - 3 * k)} L{n(x + w / 2 - 4 * k)},{n(y - h + 3 * k)}", 2.4 * k,
           darken(P.WOOD_LIGHT, 0.75))
    return c.render()


def _tent(x: float, y: float, k: float = 1.0) -> str:
    """A ridge tent with its flap tied back and a flag on the pole. 96 wide, 82 tall."""
    c = Canvas()
    c.line("M0,-60 V-80", 1.8)
    c.shape("M0,-80 L16,-75 L0,-70 Z", P.RED, sw=1.2, light=None)
    c.shape("M-46,0 L0,-62 L46,0 Z", P.ORANGE, sw=2.2, light=(-3, -2), stipple=(10, -60, 36, 60, 18, "right"))
    c.shape("M-16,0 L0,-50 L16,0 Z", P.DARK_BROWN, sw=1.8, light=None)
    c.shape("M0,-50 L-16,0 L-26,0 Z", lighten(P.ORANGE, 0.25), sw=1.6, light=None)
    c.line("M-46,0 l-6,4 M46,0 l6,4", 1.2)
    c.shape(ellipse_d(8, -4, 8, 3), P.SUN, sw=1, light=None)                               # boots by the door
    return _at(c, x, y, k)


def _campfire(x: float, y: float, k: float = 1.0) -> str:
    """A campfire with a sooty kettle on a tripod. 36 wide, 50 tall."""
    c = Canvas()
    c.line("M-16,0 L0,-46 L16,0", 1.8, P.WOOD_DARK)
    c.line("M0,-46 V-34", 1)
    c.shape("M-8,-22 Q-8,-34 0,-34 Q8,-34 8,-22 Z", P.CHARCOAL, sw=1.4, light=None)
    c.line("M8,-28 l5,-3", 1.6)
    c.shape("M-10,-2 Q-12,-12 -4,-18 Q-4,-10 0,-14 Q2,-22 6,-18 Q12,-10 10,-2 Z", P.ORANGE, sw=1.4, light=None)
    c.shape("M-4,-2 Q-6,-8 -1,-11 Q1,-6 4,-8 Q6,-4 4,-2 Z", P.SUN, sw=0.9, light=None)
    c.line("M-14,0 L14,-4 M-14,-4 L14,0", 3, P.TRUNK)
    return _at(c, x, y, k)


@episode("water_robot")
def water_robot(s: Strip) -> None:
    """Too eager to help: at the lakeside camp the agent was asked to water the flowers - and it waters them and
    waters them, from a hose screwed to the rain barrel, until the pot brims over and a puddle spreads right
    under the professor, who was quietly sitting on his crate. A frog has already moved in. A tent and a
    campfire with a kettle, and a boat on the lake."""
    s.outdoors()
    k = s.unit
    lake_r = min(150.0, s.x(0.3) * 0.9)
    lake_y = s.base + 3
    c = Canvas()
    c.shape(f"M{n(-10)},{n(lake_y - 2)} Q{n(lake_r * 0.6)},{n(lake_y - 8)} {n(lake_r * 1.4)},{n(lake_y)} "
            f"Q{n(lake_r * 0.8)},{n(lake_y + 10)} {n(-10)},{n(lake_y + 8)} Z", P.WATER, sw=1.6, light=None)
    c.line(f"M{n(lake_r * 0.3)},{n(lake_y + 2)} h14 M{n(lake_r * 0.8)},{n(lake_y)} h10", 1.2, P.WHITE)
    s.put(0.3, c.render(), None)
    if s.h >= 180:
        s.put(0.4, sets.boat(lake_r * 0.55, lake_y - 1, k * 0.35), None)
    # The professor on his crate: the crate's top is exactly where his seat is in the sitting pose.
    mod = module("professor")
    kc = s.tall / PROFESSOR_HEIGHT
    feet = s.feet(0, 0.1)
    px = s.x(0.17)
    cw, ch = 96 * kc, (mod.FEET_Y - 318) * kc
    cx = px + 11 * kc
    s.put(feet - 0.5, _crate_seat(cx, feet, cw, ch, k), (cx - cw / 2, feet - ch, cx + cw / 2, feet), group="prof")
    s.actor("professor", px, feet, "sit", "surprise", flip=False, tall=s.tall, group="prof")
    # The pot, the agent with the hose, the barrel.
    fx, fy = s.thing(lambda x, y, k: _brimming_pot(x, y, k), 0.36, 40, 50, name="pot")
    agent = s.cast("agent", 0.52, "point", "smile", flip=True, group="agent")
    ax, ay, _, _ = _palm(agent, "point", True)
    bx, by = s.thing(lambda x, y, k: _rain_barrel(x, y, k), 0.64, 50, 60, name="barrel", group="agent")
    tx, ty = fx, fy - 26 * k                     # where the water lands: in the pot
    lift = min(18 * k, max(4.0, min(ay, ty) - s.base * 0.25))
    p1 = _arc(ax, ay, tx, ty, lift, 0.02)
    turn = math.degrees(math.atan2(p1[1] - ay, p1[0] - ax))
    nx, ny = ax + math.cos(math.radians(turn)) * 12 * k, ay + math.sin(math.radians(turn)) * 12 * k
    pts = [_arc(nx, ny, tx, ty, lift, i / 20) for i in range(21)]
    d = "M" + " L".join(f"{n(qx)},{n(qy)}" for qx, qy in pts)
    c = Canvas()
    c.line(d, 4.4 * k + 2, P.WATER_LIGHT, 0.8)
    c.line(d, 3 * k, P.WATER)
    c.line(d, 1 * k, P.WHITE, 0.8)
    for i, (dx, dy) in enumerate(((-7, -6), (6, -9), (-2, -12), (9, -3))):      # splashes over the pot
        c.add(f'<path d="M{n(tx + dx * k)},{n(ty + dy * k)} q{n(-1.6 * k)},{n(3 * k)} 0,{n(4 * k)} '
              f'q{n(1.6 * k)},{n(-1)} 0,{n(-4 * k)} Z" fill="{P.WATER}" stroke="{INK}" stroke-width="{n(0.6 * k)}" '
              f'transform="rotate({(-30, 25, 0, 40)[i]} {n(tx + dx * k)} {n(ty + dy * k)})"/>')
    s.put(s.h + 1, c.render(), strip_boxes([q for q in pts[3::3] if q[0] > fx + 30 * k], 5 * k), group="agent")
    s.put(agent.bottom + 1, _nozzle(ax, ay, k * 1.1, turn), None, group="agent")
    hx, hy = ax - math.cos(math.radians(turn)) * 10 * k, ay - math.sin(math.radians(turn)) * 10 * k
    yh = s.feet(0, 0.55)
    hose = [(hx, hy), (hx + 6 * k, hy + 10 * k), (agent.left + 4 * k, yh), (agent.right + 4 * k, yh + 2 * k),
            (bx - 34 * k, yh), (bx - 30 * k, by - 6 * k), (bx - 27 * k, by - 12 * k)]
    s.put(agent.bottom + 0.8, sets.cable(hose, P.GREEN, 3 * k), [(agent.left, yh - 3 * k, bx - 26 * k, yh + 5 * k)],
          group="agent")
    # The puddle: from the pot it spreads left, round the crate and under his shoes, a frog in it.
    left = cx - cw / 2 - 10 * k
    right = fx + 16 * k
    py = feet + 4 * k
    c = Canvas()
    c.shape(f"M{n(left)},{n(py)} Q{n(left)},{n(py - 6 * k)} {n(left + 30 * k)},{n(py - 6 * k)} "
            f"H{n(right - 20 * k)} Q{n(right)},{n(py - 7 * k)} {n(right)},{n(py - 1 * k)} "
            f"Q{n(right)},{n(py + 8 * k)} {n(right - 30 * k)},{n(py + 8 * k)} H{n(left + 24 * k)} "
            f"Q{n(left)},{n(py + 8 * k)} {n(left)},{n(py)} Z", P.WATER, sw=1.4 * k, light=None)
    c.line(f"M{n(left + 14 * k)},{n(py + 2 * k)} h{n(10 * k)} M{n(right - 34 * k)},{n(py + 4 * k)} h{n(8 * k)}",
           1.2 * k, P.WHITE)
    s.put(feet - 2, c.render(), None, group="prof")
    gx = (cx + cw / 2 + fx) / 2 + 8 * k
    s.put(feet + 6, sets.lily(gx, py + 4 * k, k * 0.42, frog=True), None, group="prof")
    s.thing(lambda x, y, k: _tent(x, y, k), 0.81, 104, 82, name="tent")
    s.thing(lambda x, y, k: _campfire(x, y, k), 0.96, 36, 50, name="fire")
    if s.h >= 180:
        dx, dy = s.x(0.44), s.base - 40 * k
        box = (dx - 16 * k, dy - 12 * k, dx + 16 * k, dy + 32 * k)
        if s.free(box, 4):
            s.put(dy, sets.dragonfly(dx, dy, k * 0.7), box, "dragonfly")


# ============================================================================ computing_centre: the cloud is a building
def _terminal(c: Canvas, x: float, y: float, k: float, life: int, color: str) -> tuple[float, float]:
    """A little desk with a terminal in a room, and the room's own life; returns where its cable leaves."""
    c.line(f"M{n(x - 16 * k)},{n(y)} V{n(y - 18 * k)} M{n(x + 16 * k)},{n(y)} V{n(y - 18 * k)}", 2 * k, P.WOOD_DARK)
    c.shape(rounded_rect_d(x - 20 * k, y - 22 * k, 40 * k, 5 * k, 1.5 * k), P.WOOD_LIGHT, sw=1.3 * k, light=None)
    c.shape(rounded_rect_d(x - 12 * k, y - 44 * k, 24 * k, 20 * k, 3 * k), P.BEIGE, sw=1.4 * k, light=None)
    c.path(rounded_rect_d(x - 9 * k, y - 41 * k, 18 * k, 13 * k, 2 * k), P.SCREEN, 1 * k)
    c.line(f"M{n(x - 6 * k)},{n(y - 37 * k)} h{n(8 * k)} M{n(x - 6 * k)},{n(y - 33 * k)} h{n(11 * k)}", 1.2 * k,
           P.TERMINAL_GREEN)
    c.shape(rounded_rect_d(x - 3 * k, y - 25 * k, 6 * k, 3 * k, 1 * k), P.BEIGE_DARK, sw=1 * k, light=None)
    if life == 0:      # a hat hung on the monitor
        c.shape(f"M{n(x - 8 * k)},{n(y - 45 * k)} q0,{n(-8 * k)} {n(8 * k)},{n(-8 * k)} q{n(8 * k)},0 {n(8 * k)},"
                f"{n(8 * k)} Z", P.CHARCOAL, sw=1.2 * k, light=None)
        c.shape(ellipse_d(x, y - 45 * k, 13 * k, 2.4 * k), P.CHARCOAL, sw=1.2 * k, light=None)
    elif life == 1:    # an umbrella hooked over the desk's edge, rubber boots under it
        ux, uy = x + 21 * k, y - 20 * k
        c.line(f"M{n(ux - 3 * k)},{n(uy - 1 * k)} q0,{n(-3.4 * k)} {n(3 * k)},{n(-3.4 * k)} q{n(3 * k)},0 {n(3 * k)},"
               f"{n(3.4 * k)} V{n(uy + 3 * k)}", 1.4 * k, P.WOOD_DARK)
        c.shape(f"M{n(ux + 1.6 * k)},{n(uy + 3 * k)} Q{n(ux + 6 * k)},{n(uy + 10 * k)} {n(ux + 3.6 * k)},"
                f"{n(uy + 16 * k)} L{n(ux + 3 * k)},{n(y - 1.4 * k)} L{n(ux + 2.4 * k)},{n(uy + 16 * k)} "
                f"Q{n(ux)},{n(uy + 10 * k)} {n(ux + 1.6 * k)},{n(uy + 3 * k)} Z", P.RED, sw=1 * k, light=None)
        c.line(f"M{n(ux + 3 * k)},{n(uy + 4 * k)} V{n(uy + 14 * k)}", 0.6 * k, opacity=0.5)
        for bx in (x - 33 * k, x - 25 * k):
            c.shape(f"M{n(bx)},{n(y)} V{n(y - 11 * k)} H{n(bx + 5 * k)} V{n(y - 4 * k)} Q{n(bx + 8.5 * k)},"
                    f"{n(y - 4 * k)} {n(bx + 8.5 * k)},{n(y - 1 * k)} V{n(y)} Z", P.GREEN, sw=1 * k, light=None)
            c.line(f"M{n(bx)},{n(y - 9 * k)} h{n(5 * k)}", 0.8 * k, darken(P.GREEN, 0.75))
    elif life == 2:    # a vase of flowers
        c.shape(f"M{n(x + 16 * k)},{n(y - 22 * k)} l{n(-3 * k)},{n(-9 * k)} h{n(8 * k)} l{n(-3 * k)},{n(9 * k)} Z",
                P.BLUE, sw=1 * k, light=None)
        for fx, color2 in ((-3, P.RED), (1, P.SUN), (5, P.PINK)):
            c.line(f"M{n(x + 17 * k)},{n(y - 31 * k)} L{n(x + (17 + fx) * k)},{n(y - 38 * k)}", 0.8 * k, P.LEAF_DARK)
            c.add(f'<circle cx="{n(x + (17 + fx) * k)}" cy="{n(y - 39 * k)}" r="{n(2.2 * k)}" fill="{color2}" '
                  f'stroke="{INK}" stroke-width="{n(0.6 * k)}"/>')
    elif life == 3:    # a round fishbowl on the floor, a goldfish in it
        fx, fy = x - 28 * k, y - 8.6 * k
        r = 8.4 * k
        c.add(f'<path d="M{n(fx - r * 0.55)},{n(fy - r * 0.83)} A{n(r)},{n(r)} 0 1 0 {n(fx + r * 0.55)},'
              f'{n(fy - r * 0.83)}" fill="{lighten(P.WATER_LIGHT, 0.4)}" stroke="{INK}" stroke-width="{n(1 * k)}"/>')
        c.add(f'<path d="M{n(fx - r * 0.86)},{n(fy - r * 0.45)} A{n(r)},{n(r)} 0 1 0 {n(fx + r * 0.86)},'
              f'{n(fy - r * 0.45)} Z" fill="{P.WATER_LIGHT}"/>')
        c.add(f'<ellipse cx="{n(fx)}" cy="{n(fy - r * 0.83)}" rx="{n(r * 0.55)}" ry="{n(r * 0.16)}" '
              f'fill="{P.WHITE}" stroke="{INK}" stroke-width="{n(0.9 * k)}"/>')
        c.shape(f"M{n(fx - 3.4 * k)},{n(fy + 1 * k)} q{n(3 * k)},{n(-3.4 * k)} {n(6 * k)},0 q{n(-3 * k)},{n(3.4 * k)} "
                f"{n(-6 * k)},0 Z M{n(fx - 3.4 * k)},{n(fy + 1 * k)} l{n(-2.4 * k)},{n(-2.2 * k)} v{n(4.4 * k)} Z",
                P.ORANGE, sw=0.7 * k, light=None)
        c.dot(fx + 1.4 * k, fy + 0.4 * k, 0.6 * k)
    elif life == 4:    # a mug of tea, steaming
        c.shape(rounded_rect_d(x + 13 * k, y - 28 * k, 5 * k, 6 * k, 1 * k), P.RED, sw=0.9 * k, light=None)
        c.line(f"M{n(x + 15 * k)},{n(y - 30 * k)} q{n(-2 * k)},{n(-3 * k)} 0,{n(-6 * k)}", 0.9 * k, P.METAL_DARK)
    else:              # a cat-sized plant
        c.add(props.plant(x + 28 * k, y, k * 0.32))
    c.line(f"M{n(x + 12 * k)},{n(y - 34 * k)} h{n(4 * k)}", 2 * k, color)
    return x + 16 * k, y - 34 * k


def _roof_dish(x: float, y: float, k: float = 1.0) -> str:
    """A dish antenna bolted to a flat roof: a base plate with bolts, a short mast, a yoke, and a parabolic dish
    tilted to the sky - its rim, its shaded inside, two struts holding the receiver at the focus. The origin is
    the middle of the base plate on the roof; 34 wide, 40 tall."""
    c = Canvas()
    c.shape(rounded_rect_d(-10, -3.5, 20, 3.5, 1.2), P.METAL_DARK, sw=1.4, light=None)
    for bx in (-6.5, 6.5):
        c.dot(bx, -1.8, 1.1, P.METAL_PALE)
    c.shape("M-2.2,-3.5 V-15 H2.2 V-3.5 Z", P.METAL, sw=1.4, light=(-0.6, -0.6))
    c.shape("M-4.5,-15 L-3,-19 H3 L4.5,-15 Z", P.METAL_DARK, sw=1.2, light=None)               # the yoke
    g = Canvas()
    g.shape("M-16,0 Q0,15 16,0 Z", P.METAL_LIGHT, sw=1.6, light=(-1, -1), shade_k=0.8)          # the back
    g.shape(ellipse_d(0, 0, 16, 4.4), P.METAL_PALE, sw=1.6, light=None)                         # the rim
    g.add(f'<path d="M-13,0.6 Q0,5.4 13,0.6 Q0,3 -13,0.6 Z" fill="{P.METAL}" opacity=".8"/>')    # inner shade
    g.line("M-12.5,0.4 L0,-13 L12.5,0.4", 1.1, P.METAL_DARK)                                    # the struts
    g.shape(rounded_rect_d(-2.6, -17, 5.2, 5, 1.4), P.CHARCOAL, sw=1.1, light=None)             # the receiver
    g.dot(0, -14.6, 0.9, P.RED)
    c.add(f'<g transform="translate(0,-21) rotate(-28)">{g.render()}</g>')
    return _at(c, x, y, k)


def _computing_centre(x0: float, x1: float, ground: float, k: float, floors: int, seed: int, title: str) -> str:
    """A computing centre cut away like a dolls' house: rooms with terminals on every floor, each with a life of
    its own, all wired with coloured cables to the machine hall of striped cabinets on the right. The roof
    carries the name and a dish."""
    rnd = random.Random(seed)
    c = Canvas()
    rh, t = 62 * k, 6 * k
    top = ground - floors * (rh + t)
    hall = 112 * k
    hx = x1 - hall
    walls = (lighten(P.YELLOW, 0.5), lighten(P.PINK, 0.6), lighten(P.GREEN, 0.6), lighten(P.SKY, 0.2),
             lighten(P.VIOLET, 0.6), lighten(P.ORANGE, 0.6))
    cables = (P.RED, P.BLUE, P.GREEN, P.YELLOW, P.PINK, P.ORANGE, P.VIOLET, P.TEAL)
    # The roof: a parapet, the name, a dish and an aerial.
    c.shape(f"M{n(x0 - 6 * k)},{n(top - 8 * k)} H{n(x1 + 6 * k)} V{n(top)} H{n(x0 - 6 * k)} Z", P.STONE, sw=1.6 * k,
            light=None)
    size = max(sets.LETTERING_MIN, 10 * k)
    tw, th = plate_size(title, size)
    tw = min(hx - x0 - 40 * k, tw)
    _plate(c, (x0 + hx) / 2, top - 8 * k - th / 2, title, size, 1.0, P.CREAM, P.BLUE, w=tw, h=th, r=2 * k)
    dx = hx + hall * 0.55
    c.add(_roof_dish(dx, top - 8 * k, k))
    if (x0 + hx) / 2 - tw / 2 > x0 + 36 * k:
        c.add(_pigeon(x0 + 18 * k, top - 8 * k, k * 0.8))
    # The rooms.
    c.shape(f"M{n(x0)},{n(top)} H{n(x1)} V{n(ground)} H{n(x0)} Z", P.CARD, sw=2 * k, light=None)
    cols = max(2, min(5, int((hx - x0) / (82 * k))))
    cw = (hx - x0 - t) / cols
    exits = []
    life = rnd.randrange(6)
    for f in range(floors):
        fy = ground - f * (rh + t)
        for col in range(cols):
            rx = x0 + t / 2 + col * cw
            color = walls[(f * cols + col + seed) % len(walls)]
            c.path(f"M{n(rx + t / 2)},{n(fy - rh)} H{n(rx + cw - t / 2)} V{n(fy)} H{n(rx + t / 2)} Z", color, 1 * k)
            c.add(f'<rect x="{n(rx + t / 2)}" y="{n(fy - 4 * k)}" width="{n(cw - t)}" height="{n(4 * k)}" '
                  f'fill="{P.WOOD}"/>')
            if f == 0 and col == 0:      # the front door on the ground floor
                c.shape(rounded_rect_d(rx + t, fy - 44 * k, 22 * k, 44 * k, 2 * k), P.GREEN, sw=1.4 * k, light=None)
                c.dot(rx + t + 18 * k, fy - 22 * k, 1.6 * k, P.SUN)
                c.shape(rounded_rect_d(rx + t - 2 * k, fy - 3 * k, 28 * k, 3 * k, 1 * k), P.RED, sw=1 * k, light=None)
                c.add(sets.umbrella_closed(rx + t + 34 * k, fy - 6 * k, k * 0.32, P.BLUE))
                continue
            exits.append((f, *_terminal(c, rx + cw * 0.45, fy - 2 * k, k, life % 6,
                                        cables[len(exits) % len(cables)])))
            life += 1
        if f < floors - 1:
            c.shape(f"M{n(x0)},{n(fy - rh - t)} H{n(hx)} V{n(fy - rh)} H{n(x0)} Z", P.WOOD, sw=1.2 * k, light=None)
        for col in range(1, cols):
            wx = x0 + t / 2 + col * cw
            c.shape(f"M{n(wx - t / 2)},{n(fy - rh)} H{n(wx + t / 2)} V{n(fy)} H{n(wx - t / 2)} Z", P.CARD, sw=1 * k,
                    light=None)
    # The machine hall: striped cabinets with tape reels and lamps.
    c.path(f"M{n(hx)},{n(top + t / 2)} H{n(x1 - t / 2)} V{n(ground)} H{n(hx)} Z", lighten(P.METAL_PALE, 0.3), 1 * k)
    c.shape(f"M{n(hx - t / 2)},{n(top)} H{n(hx + t / 2)} V{n(ground)} H{n(hx - t / 2)} Z", P.CARD, sw=1.2 * k,
            light=None)
    cab_h = min(ground - top - 16 * k, 120 * k)
    for i in range(3):
        bx = hx + 10 * k + i * 32 * k
        by = ground - 2 * k
        clip = c.shape(f"M{n(bx)},{n(by)} V{n(by - cab_h)} H{n(bx + 26 * k)} V{n(by)} Z", P.METAL_LIGHT, sw=1.4 * k,
                       light=None, clip=True)
        stripes = "".join(f'<rect x="{n(bx)}" y="{n(by - cab_h + j * 10 * k)}" width="{n(26 * k)}" '
                          f'height="{n(4 * k)}" fill="{(P.BLUE, P.ORANGE, P.TEAL)[i]}" opacity=".55"/>'
                          for j in range(int(cab_h / (10 * k)) + 1))
        c.add(f'<g clip-path="url(#{clip})">{stripes}</g>')
        for ry in (by - cab_h + 12 * k, by - cab_h + 28 * k):
            for rx in (bx + 7 * k, bx + 19 * k):
                c.add(f'<circle cx="{n(rx)}" cy="{n(ry)}" r="{n(5 * k)}" fill="{P.CHARCOAL}" stroke="{INK}" '
                      f'stroke-width="{n(1 * k)}"/><circle cx="{n(rx)}" cy="{n(ry)}" r="{n(1.8 * k)}" '
                      f'fill="{P.METAL}"/>')
        for j in range(4):
            c.add(f'<circle cx="{n(bx + 5 * k + j * 5.4 * k)}" cy="{n(by - cab_h + 42 * k)}" r="{n(1.6 * k)}" '
                  f'fill="{(P.RED, P.GREEN, P.SUN, P.GREEN)[(j + i) % 4]}"/>')
    if ground - top - cab_h > 40 * k:      # room above the cabinets: lamps and a clock on the hall wall
        for i, wx in enumerate((hx + hall * 0.2, hx + hall * 0.8)):
            c.line(f"M{n(wx)},{n(top + t / 2)} v{n(10 * k + i * 4 * k)}", 1 * k)
            c.shape(f"M{n(wx - 7 * k)},{n(top + 18 * k + i * 4 * k)} q{n(7 * k)},{n(-10 * k)} {n(14 * k)},0 Z",
                    P.GREEN, sw=1.2 * k, light=None)
        c.add(things.wall_clock(hx + hall * 0.5, (top + ground - cab_h) / 2, k * 0.7))
    # The cables: up from each terminal to the ceiling, along it into the hall.
    for i, (f, ex, ey) in enumerate(exits):
        fy = ground - f * (rh + t)
        cy = fy - rh + (3 + (i % 5) * 2.2) * k
        color = cables[i % len(cables)]
        d = f"M{n(ex)},{n(ey)} Q{n(ex + 6 * k)},{n(ey)} {n(ex + 6 * k)},{n(ey - 8 * k)} V{n(cy)} H{n(hx + 10 * k)}"
        c.line(d, 2.6 * k)
        c.line(d, 1.6 * k, color)
    c.shape(f"M{n(x0 - 8 * k)},{n(ground)} H{n(x1 + 8 * k)} V{n(ground + 6 * k)} H{n(x0 - 8 * k)} Z", P.STONE,
            sw=1.4 * k, light=None)
    return c.render()


@episode("computing_centre")
def computing_centre(s: Strip) -> None:
    """The cloud, seen close up, is a building: a computing centre cut open like a dolls' house. In every little
    room a terminal and somebody's life - a hat on a monitor, an umbrella and boots, a vase of flowers, a
    fishbowl - and from every room a coloured cable runs to the machine hall of striped cabinets. The cat waits
    at the door; a pigeon struts along the roof."""
    s.outdoors()
    k = s.unit
    cat = s.cast("cat", 0.06, "wave", "smile", flip=False)
    ground = s.feet(0)
    # Few big rooms rather than many small ones: the building's scale is what the height allows.
    avail = ground - s.base * 0.25
    floors = max(1, min(3, round((avail / (1.15 * k) - 32) / 68)))
    kk = min(1.3, 1.45 * k, avail / (floors * 68 + 32))
    x0, x1 = cat.right + 8 * kk + 8, s.x(0.9)
    s.put(ground - 2, _computing_centre(x0, x1, ground, kk, floors, s.seed, s.word("title")),
          (x0 - 8 * kk, ground - floors * 68 * kk - 32 * kk, x1 + 8 * kk, ground + 6 * kk), "centre")


def _pigeon(x: float, y: float, k: float = 1.0) -> str:
    """A grey pigeon strutting. 24 wide, 22 tall."""
    c = Canvas()
    c.line("M-2,0 V-6 M3,0 V-6", 1.2, P.PINK)
    c.shape("M-12,-10 Q-10,-18 2,-16 Q8,-22 12,-18 Q14,-14 10,-12 Q8,-4 0,-4 Q-8,-4 -12,-10 Z", P.METAL, sw=1.4,
            light=(-1, -1))
    c.shape("M12,-18 l4,1 l-4,1 Z", P.AMBER, sw=0.8, light=None)
    c.dot(10, -18, 1)
    c.line("M-6,-11 q4,2 8,0", 1, P.TEAL)
    return _at(c, x, y, k)


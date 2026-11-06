"""Stage sets for the chapter openers: the bigger, more detailed objects their stories need.

Like `props`, every function is `thing(x, y, scale, ...) -> str`, an SVG group whose origin is where the
object touches the ground (or, for things on a wall, its top centre, as each docstring says). The house style
is the same: ink outline with round joins, cel shading from the top left, stipple in the shadows.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten
from .doodles import _DRAWINGS
from .ink import INK, Canvas, ellipse_d, lettering, lettering_width, n, rounded_rect_d
from .props import tree


def _at(c: Canvas, x: float, y: float, scale: float = 1.0, mirror: bool = False, turn: float = 0) -> str:
    sx = -scale if mirror else scale
    rot = f" rotate({n(turn)})" if turn else ""
    return f'<g transform="translate({n(x)},{n(y)}){rot} scale({n(sx)},{n(scale)})">{c.render()}</g>'


def _label(c: Canvas, x: float, y: float, text: str, size: float, fill: str = INK, anchor: str = "middle",
           turn: float = 0, style: str = "sign") -> None:
    """Lettering in a drawing: a sign, a label, a number (see `ink.lettering`); every drawing letters alike."""
    c.add(lettering(x, y, text, size, fill, anchor, turn, style=style))


LETTERING_MIN = 9.5    # the smallest lettering drawn in a picture, in units of the page (about 2.4 mm)


def letter_width(text: str, size: float, style: str = "sign") -> float:
    """About how wide a line of lettering is."""
    return lettering_width(text, size, style)


def fit_label(c: Canvas, x: float, y: float, text: str, size: float, room: float, fill: str = INK,
              anchor: str = "middle", turn: float = 0, style: str = "sign") -> None:
    """Lettering that never leaves its sign: if the words would run wider than `room`, the whole line is set
    smaller to fit - never squeezed, never over the edge."""
    c.add(lettering(x, y, text, size, fill, anchor, turn, room=room, style=style))


def doodle_at(name: str, x: float, y: float, size: float, turn: float = 0) -> str:
    """One of the 100 x 100 doodles standing with its bottom centre at (x, y), `size` units tall."""
    c = Canvas()
    _DRAWINGS[name](c)
    k = size / 100
    rot = f" rotate({n(turn)})" if turn else ""
    return f'<g transform="translate({n(x)},{n(y)}){rot} scale({n(k)}) translate(-50,-96)">{c.render()}</g>'


# ============================================================================ rooms
def wall(c: Canvas, color: str, top: float, bottom: float, width: float, seed: int = 0, stripes: bool = True) -> None:
    """A painted wall with a soft light from the top left and faint wallpaper stripes."""
    paint = c.gradient([(0, lighten(color, 0.30)), (0.6, color), (1, darken(color, 0.93))],
                       0, top, width * 0.3, bottom)
    c.add(f'<rect x="-4" y="{n(top - 4)}" width="{n(width + 8)}" height="{n(bottom - top + 8)}" fill="{paint}"/>')
    if stripes:
        for i in range(0, int(width) + 40, 34):
            c.add(f'<path d="M{i},{n(top)} V{n(bottom)}" stroke="{darken(color, 0.9)}" stroke-width="7" '
                  f'stroke-opacity=".35"/>')
        rnd = random.Random(seed)
        for _ in range(60):   # a tiny printed flower on the wallpaper
            x, y = rnd.uniform(10, width - 10), rnd.uniform(top + 10, bottom - 30)
            c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="2.2" fill="{lighten(color, 0.45)}" opacity=".8"/>')


def floor(c: Canvas, top: float, bottom: float, width: float, vanish: tuple[float, float], color: str = P.FLOOR,
          skirting: str = P.TERRACOTTA) -> None:
    """Floor boards receding towards a vanishing point, a skirting board along the wall."""
    paint = c.gradient([(0, darken(color, 0.95)), (1, color)], 0, top, 0, bottom)
    c.path(f"M-4,{n(top)} H{n(width + 4)} V{n(bottom + 4)} H-4 Z", paint, 2.4)
    vx, vy = vanish
    for i in range(-14, 30):
        bx = i * 64
        t = (top - vy) / (bottom - vy)
        tx = vx + (bx - vx) * t
        c.line(f"M{n(tx)},{n(top)} L{n(bx)},{n(bottom)}", 1.2, opacity=0.55)
    for k in (0.10, 0.27, 0.52, 0.85):       # cross joints, further apart nearer the viewer
        y = top + (bottom - top) * k
        c.line(f"M0,{n(y)} H{n(width)}", 0.9, opacity=0.25)
    c.dots(None, 0, top, width, (bottom - top) * 0.35, 260, "top", seed=5, opacity=0.25)
    c.shape(f"M-4,{n(top - 18)} H{n(width + 4)} V{n(top)} H-4 Z", skirting, sw=2.2, light=None)
    c.line(f"M-4,{n(top - 12)} H{n(width + 4)}", 1.1, opacity=0.5)


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


def cuckoo_clock(x: float, y: float, scale: float = 1.0, time: tuple[int, int] = (9, 0)) -> str:
    """A carved cuckoo clock with its bird out and calling, pine-cone weights below; the origin is the nail."""
    c = Canvas()
    hour, minute = time
    c.shape("M-46,10 L0,-22 L46,10 Z", P.WOOD_DARK, sw=2.4, light=(-2, -2))
    c.shape("M-38,8 H38 V96 H-38 Z", P.WOOD, sw=2.5, light=(-3, -3), stipple=(20, 10, 18, 84, 22, "right"))
    for i in range(4):   # the carved leaves along the roof
        c.path(f"M{-40 + i * 20},8 q10,10 20,0", P.WOOD_LIGHT, 1.6)
    c.shape(ellipse_d(0, 56, 27, 27), P.CARD, sw=2.3, light=(-2, -2), shade_k=0.92)
    for k in range(12):
        a = math.radians(k * 30)
        c.line(f"M{n(math.sin(a) * 21)},{n(56 - math.cos(a) * 21)} "
            f"L{n(math.sin(a) * 24)},{n(56 - math.cos(a) * 24)}", 1.6)
    ha, ma = math.radians((hour % 12 + minute / 60) * 30), math.radians(minute * 6)
    c.line(f"M0,56 L{n(math.sin(ha) * 13)},{n(56 - math.cos(ha) * 13)}", 3)
    c.line(f"M0,56 L{n(math.sin(ma) * 20)},{n(56 - math.cos(ma) * 20)}", 2)
    c.dot(0, 56, 2.6)
    # The little door is open and the bird leans out.
    c.path("M-10,14 H10 V30 H-10 Z", P.WOOD_DARK, 1.8)
    c.path("M10,14 L22,10 V34 L10,30 Z", P.WOOD_LIGHT, 1.8)
    c.shape("M-6,26 Q-10,14 2,12 Q12,12 10,22 L22,20 L12,26 Q4,32 -6,26 Z", P.SUN, sw=1.8, light=(-1, -1))
    c.dot(3, 17, 1.6)
    c.line("M26,12 l6,-4 M28,18 l8,0 M26,24 l6,4", 1.6)
    # Pendulum and chains with pine-cone weights.
    c.line("M0,96 V150", 1.6)
    c.shape(ellipse_d(0, 158, 10, 10), P.AMBER, sw=2, light=(-2, -2))
    for wx, drop in ((-20, 168), (20, 142)):
        c.line(f"M{wx},96 V{drop}", 1.2)
        c.shape(f"M{wx - 6},{drop} Q{wx - 8},{drop + 18} {wx},{drop + 24} Q{wx + 8},{drop + 18} {wx + 6},{drop} Z",
                P.WOOD_DARK, sw=1.8, light=(-1, -1))
        c.line(f"M{wx - 4},{drop + 6} h8 M{wx - 4},{drop + 12} h8 M{wx - 3},{drop + 18} h6", 1, opacity=0.6)
    c.dot(0, -26, 2.4)
    return _at(c, x, y, scale)


def tear_calendar(x: float, y: float, scale: float = 1.0, day: str = "1", month: str = "", label: str = "") -> str:
    """A tear-off wall calendar showing a day, with stubs of the torn pages; the origin is the nail. 128 wide,
    170 tall: a calendar block is nearly as wide as it is tall, never a narrow strip."""
    c = Canvas()
    c.line("M0,0 L-44,22 M0,0 L44,22", 1.4)
    c.dot(0, 0, 2.4)
    c.shape("M-64,22 H64 V170 H-64 Z", P.WOOD_LIGHT, sw=2.4, light=(-2, -2))
    c.shape("M-58,30 H58 V62 H-58 Z", P.RED, sw=2.2, light=None)
    _label(c, 0, 53, month, 18, P.WHITE)
    for i in range(10):   # stubs of torn pages along the top
        c.path(f"M{-54 + i * 11},62 l4,6 l4,-6 Z", P.CARD, 1)
    c.shape("M-56,64 H56 V160 H-56 Z", P.CARD, sw=2.2, light=(-2, -2), shade_k=0.94)
    _label(c, 0, 128, day, 60, P.INK)
    _label(c, 0, 151, label, 14)
    c.path("M42,160 Q56,150 56,132 V160 Z", P.PAPER_FOLD, 1.6)   # the corner curls: tomorrow is coming
    return _at(c, x, y, scale)


def loose_page(x: float, y: float, scale: float = 1.0, text: str = "", turn: float = 0) -> str:
    """A torn calendar page lying about or drifting down; the origin is its centre."""
    c = Canvas()
    c.shape("M-20,-22 H20 V22 L14,18 L8,22 L2,18 L-4,22 L-10,18 L-16,22 L-20,18 Z", P.CARD, sw=1.8,
            light=(-1, -1), shade_k=0.93)
    c.shape("M-20,-22 H20 V-12 H-20 Z", P.RED, sw=1.6, light=None)
    _label(c, 0, 12, text, 20)
    return _at(c, x, y, scale, turn=turn)


def whiteboard(x: float, y: float, w: float, h: float, title: str = "", tallies: int = 0) -> str:
    """A whiteboard on the wall with a heading and groups of tally marks; the origin is its top centre."""
    c = Canvas()
    hw = w / 2
    c.shape(f"M{-hw},0 H{hw} V{h} H{-hw} Z", P.METAL_DARK, sw=2.4, light=None)
    c.shape(f"M{-hw + 7},7 H{hw - 7} V{h - 7} H{-hw + 7} Z", P.WHITE, sw=1.6, light=(-3, -3), shade_k=0.96)
    c.line(f"M{-hw + 20},18 L{-hw + 60},{h - 20}", 6, P.WHITE, 0.6)
    _label(c, -hw + 22, 40, title, 24, P.BLUE, anchor="start")
    rnd = random.Random(tallies)
    gx, gy = -hw + 22, 60.0
    for i in range(tallies // 5):   # bundles of five, a stroke through four
        ox, oy = gx + (i % 6) * 40, gy + (i // 6) * 34
        for k in range(4):
            c.line(f"M{n(ox + k * 7 + rnd.uniform(-1, 1))},{n(oy)} l{n(rnd.uniform(-1, 1))},24", 2.2, P.RED)
        c.line(f"M{n(ox - 4)},{n(oy + 18)} L{n(ox + 27)},{n(oy + 4)}", 2.2, P.RED)
    c.shape(f"M{-hw + 10},{h - 2} H{hw - 10} V{h + 8} H{-hw + 10} Z", P.METAL, sw=1.8, light=None)
    c.shape(rounded_rect_d(hw - 70, h - 8, 26, 8, 3), P.RED, sw=1.6, light=None)        # markers on the tray
    c.shape(rounded_rect_d(hw - 40, h - 8, 26, 8, 3), P.BLUE, sw=1.6, light=None)
    c.shape(rounded_rect_d(-hw + 24, h - 12, 30, 12, 3), P.STONE, sw=1.6, light=None)  # the eraser
    return _at(c, x, y)


def sticky(x: float, y: float, color: str = P.YELLOW_PALE, turn: float = 0, scale: float = 1.0) -> str:
    """A sticky note with a scribble; the origin is its centre."""
    c = Canvas()
    c.shape("M-14,-14 H14 V10 L10,14 H-14 Z", color, sw=1.6, light=None)
    c.line("M-9,-6 h16 M-9,0 h12 M-9,6 h14", 1.3, P.PEN, 0.7)
    return _at(c, x, y, scale, turn=turn)


def legacy_shelf(x: float, y: float, scale: float = 1.0, seed: int = 0, gap: int = 1) -> str:
    """A tall shelf of modules: shiny new binders on top, dusty grey boxes below.

    One box is missing from the bottom shelf (`gap`): someone has just taken the oldest one out.
    The origin is the middle of its foot; it is 150 wide and 400 tall.
    """
    rnd = random.Random(seed)
    c = Canvas()
    c.shape("M-75,0 V-400 H75 V0 Z", P.WOOD, sw=2.6, light=(-3, -3), stipple=(50, -396, 22, 394, 40, "right"))
    rows = 4
    for row in range(rows):
        top = -392 + row * 97
        c.path(f"M-67,{top} H67 V{top + 86} H-67 Z", P.WOOD_DARK, 2)
        bx, i = -64.0, 0
        new = row == 0
        while bx < 52:
            bw = rnd.choice((14, 16, 18)) if new else rnd.choice((18, 20, 22))
            bh = rnd.choice((70, 76, 80)) if new else rnd.choice((62, 68, 74))
            if row == rows - 1 and i == gap:     # the empty slot
                c.line(f"M{n(bx + 2)},{top + 86} h{bw - 4}", 1.4, P.STONE, 0.9)
                c.dots(None, bx + 2, top + 80, bw - 4, 6, 10, "even", seed=seed, r=0.7, color=P.STONE, opacity=0.9)
                bx += bw + 1
                i += 1
                continue
            color = (P.BLUE, P.RED, P.GREEN, P.YELLOW, P.TEAL, P.VIOLET, P.ORANGE)[(i + seed) % 7] if new else \
                rnd.choice((P.STONE, P.PEBBLE, P.METAL, P.BEIGE_SHADE))
            d = f"M{n(bx)},{top + 86} V{top + 86 - bh} H{n(bx + bw)} V{top + 86} Z"
            if new:
                c.shape(d, color, sw=1.6, light=(-2, 0), highlight=f"M{n(bx + 4)},{top + 92 - bh} v{bh - 20}")
                c.add(f'<circle cx="{n(bx + bw / 2)}" cy="{top + 60}" r="3.2" fill="{P.WHITE}" stroke="{INK}" '
                      f'stroke-width="1.1"/>')
            else:
                c.shape(d, color, sw=1.6, light=(-2, 0), shade_k=0.86,
                        stipple=(bx, top + 86 - bh, bw, bh, 14, "top"))
                c.path(f"M{n(bx + 3)},{top + 94 - bh} H{n(bx + bw - 3)} V{top + 104 - bh} H{n(bx + 3)} Z",
                       P.CARD, 1)
                c.line(f"M{n(bx + 5)},{top + 99 - bh} h{bw - 10}", 0.9, opacity=0.5)
            bx += bw + 1
            i += 1
        if not new:   # dust on the edge of the board
            c.dots(None, -66, top + 84, 132, 4, 40, "even", seed=seed + row, r=0.8, color=P.WHITE, opacity=0.8)
    # A label board on the top: the new, and on the side: the old.
    c.path(rounded_rect_d(-34, -412, 68, 18, 4), P.CREAM, 1.8)
    c.line("M-24,-403 h48", 2.4, P.GREEN, 0.9)
    return _at(c, x, y, scale)


def fanfold(points: list[tuple[float, float]], width: float, flags: list[tuple[float, str]],
            seed: int = 0) -> str:
    """A long ribbon of fan-fold printer paper along a path of points, with comment flags stuck to it.

    `flags` is a list of (position 0..1 along the ribbon, color). The ribbon is a strip of quads, each a sheet
    with sprocket holes along both edges; the fold lines show where the sheets meet.
    """
    c = Canvas()
    rnd = random.Random(seed)
    lefts, rights = [], []
    for i, (px, py) in enumerate(points):
        qx, qy = points[min(i + 1, len(points) - 1)] if i < len(points) - 1 else points[i]
        ox, oy = points[i - 1] if i else points[0]
        dx, dy = (qx - ox), (qy - oy)
        length = math.hypot(dx, dy) or 1
        nx, ny = -dy / length, dx / length
        wk = width * (0.55 + 0.45 * i / max(1, len(points) - 1))    # wider as it comes nearer
        lefts.append((px + nx * wk / 2, py + ny * wk / 2))
        rights.append((px - nx * wk / 2, py - ny * wk / 2))
    for i in range(len(points) - 1):
        a, b, cc, d = lefts[i], lefts[i + 1], rights[i + 1], rights[i]
        shade = P.WHITE if i % 2 == 0 else P.CARD
        c.path(f"M{n(a[0])},{n(a[1])} L{n(b[0])},{n(b[1])} L{n(cc[0])},{n(cc[1])} L{n(d[0])},{n(d[1])} Z", shade, 1.8)
        for t in (0.25, 0.5, 0.75):   # sprocket holes along both edges
            hx = a[0] + (b[0] - a[0]) * t + (d[0] - a[0]) * 0.08
            hy = a[1] + (b[1] - a[1]) * t + (d[1] - a[1]) * 0.08
            c.add(f'<circle cx="{n(hx)}" cy="{n(hy)}" r="1.5" fill="{P.STONE}"/>')
            hx = d[0] + (cc[0] - d[0]) * t + (a[0] - d[0]) * 0.08
            hy = d[1] + (cc[1] - d[1]) * t + (a[1] - d[1]) * 0.08
            c.add(f'<circle cx="{n(hx)}" cy="{n(hy)}" r="1.5" fill="{P.STONE}"/>')
        for t in (0.3, 0.55):         # printed lines of code
            x1 = a[0] + (b[0] - a[0]) * t + (d[0] - a[0]) * 0.2
            y1 = a[1] + (b[1] - a[1]) * t + (d[1] - a[1]) * 0.2
            k = rnd.uniform(0.35, 0.65)
            x2 = x1 + (d[0] - a[0]) * k
            y2 = y1 + (d[1] - a[1]) * k
            c.line(f"M{n(x1)},{n(y1)} L{n(x2)},{n(y2)}", 1.4, P.SCREEN, 0.55)
    total = len(points) - 1
    for pos, color in flags:          # comment flags: a pin-flag stuck at the right edge of the ribbon
        f = pos * total
        i = min(int(f), total - 1)
        t = f - i
        ex = rights[i][0] + (rights[i + 1][0] - rights[i][0]) * t
        ey = rights[i][1] + (rights[i + 1][1] - rights[i][1]) * t
        c.line(f"M{n(ex)},{n(ey)} l0,-16", 1.6)
        c.shape(f"M{n(ex)},{n(ey - 16)} l14,4 l-14,5 Z", color, sw=1.5, light=None)
    return c.render()


def bin_with_paper(x: float, y: float, scale: float = 1.0, seed: int = 0) -> str:
    """A wire waste-paper bin overflowing with crumpled sheets; one ball has rolled away."""
    c = Canvas()
    rnd = random.Random(seed)
    c.shape(ellipse_d(0, -60, 30, 5), P.METAL_DARK, sw=2.1, light=None)          # the inside, behind the paper
    for i, (bx, by, r) in enumerate(((-15, -66, 10), (13, -67, 10), (-1, -75, 11), (23, -63, 8), (-23, -62, 8))):
        c.add(paper_ball(bx, by, r / 10, seed=seed * 7 + i))
    c.shape("M-30,-60 Q0,-55 30,-60 L22,0 H-22 Z", P.METAL, sw=2.3, light=(-3, -2), shade_k=0.85)
    for i in range(7):
        t = i / 6
        c.line(f"M{n(-30 + 60 * t)},{n(-60 + 5 * math.sin(math.pi * t))} L{n(-22 + 44 * t)},0", 1.1, opacity=0.6)
    c.line("M-28,-42 Q0,-38 28,-42 M-25,-22 Q0,-18 25,-22", 1.1, opacity=0.6)
    c.line("M-30,-60 Q0,-50 30,-60", 4.4)                                          # the front of the rim
    c.line("M-30,-60 Q0,-50 30,-60", 2, P.METAL_LIGHT)
    c.add(paper_ball(46 + rnd.uniform(-2, 2), -9, 1, seed=seed * 7 + 9))
    return _at(c, x, y, scale)


def paper_ball(x: float, y: float, scale: float = 1.0, seed: int = 0) -> str:
    """A crumpled sheet of paper centred on (x, y), about 20 across: a lumpy, faceted outline with creases
    running out to its edges and a few facets in grey - angular all over, so it never reads as a face."""
    rnd = random.Random(seed * 131 + 17)
    c = Canvas()
    count = 11
    pts = []
    for i in range(count):
        a = math.tau * (i + rnd.uniform(-0.25, 0.25)) / count - math.pi / 2
        r = 10 * (rnd.uniform(0.8, 1.0) if i % 2 else rnd.uniform(0.62, 0.8))      # bumps and dents
        pts.append((math.cos(a) * r * 1.08, math.sin(a) * r * 0.95))
    outline = "M" + " L".join(f"{n(px)},{n(py)}" for px, py in pts) + " Z"
    clip = c.shape(outline, P.WHITE, sw=1.5, light=(-1.6, -1.8), shade_k=0.86)
    # creases: from two inner knots out to the dents of the outline
    knots = ((rnd.uniform(-3, -1), rnd.uniform(-3, -1)), (rnd.uniform(1.5, 4), rnd.uniform(1, 3.5)))
    facets = []
    for j, (px, py) in enumerate(pts):
        if j % 2 == 0:
            kx, ky = knots[0] if px + py * 0.3 < -3 else knots[1]
            facets.append(f"M{n(kx)},{n(ky)} L{n(px)},{n(py)}")
    shade = darken(P.METAL_PALE, 0.95)
    j = rnd.randrange(0, count - 1)
    k0 = knots[1]
    c.add(f'<g clip-path="url(#{clip})"><path d="M{n(k0[0])},{n(k0[1])} L{n(pts[j][0])},{n(pts[j][1])} '
          f'L{n(pts[j + 1][0])},{n(pts[j + 1][1])} Z" fill="{shade}"/></g>')
    c.line(" ".join(facets) + f" M{n(knots[0][0])},{n(knots[0][1])} L{n(knots[1][0])},{n(knots[1][1])}", 0.9,
           opacity=0.55)
    return _at(c, x, y, scale)


def rug_round(x: float, y: float, rx: float, ry: float, color: str = P.TEAL) -> str:
    c = Canvas()
    c.shape(ellipse_d(0, 0, rx, ry), color, sw=2.3, light=(-5, -3))
    c.add(f'<ellipse cx="0" cy="0" rx="{n(rx * 0.78)}" ry="{n(ry * 0.72)}" fill="none" stroke="{P.CREAM}" '
          f'stroke-width="2.6" stroke-dasharray="9 7"/>')
    c.add(f'<ellipse cx="0" cy="0" rx="{n(rx * 0.45)}" ry="{n(ry * 0.4)}" fill="none" stroke="{P.YELLOW}" '
          f'stroke-width="3"/>')
    return _at(c, x, y)


def yarn(x: float, y: float, r: float = 14, color: str = P.RED, thread: str = "") -> str:
    """A ball of yarn, its loose thread wandering off along `thread` (path data relative to the ball)."""
    c = Canvas()
    if thread:
        c.line(thread, 1.6, color)
    c.shape(ellipse_d(0, -r, r, r), color, sw=2, light=(-2, -2))
    for k in range(4):
        c.line(f"M{-r * 0.8},{n(-r * (1.4 - k * 0.25))} Q0,{n(-r * (1.9 - k * 0.3))} "
            f"{r * 0.8},{n(-r * (0.9 + k * 0.1))}",
               1.1, opacity=0.6)
    return _at(c, x, y)


def mug_at(x: float, y: float, size: float = 40) -> str:
    return doodle_at("mug", x, y, size)


def coat_rack(x: float, y: float, scale: float = 1.0) -> str:
    """A bentwood coat stand; the origin is the middle of its foot. 300 tall."""
    c = Canvas()
    c.line("M0,-300 V-10", 8, P.WOOD_DARK)
    c.line("M0,-300 V-10", 2.2)
    for sx in (-1, 1):
        c.line(f"M0,-14 Q{sx * 16},-8 {sx * 30},0", 6, P.WOOD_DARK)
        c.line(f"M0,-260 Q{sx * 24},-262 {sx * 26},-280", 5, P.WOOD_DARK)
    c.shape(ellipse_d(0, -304, 8, 6), P.WOOD_DARK, sw=1.8, light=None)
    return _at(c, x, y, scale)


def umbrella_closed(x: float, y: float, scale: float = 1.0, color: str = P.BLUE) -> str:
    c = Canvas()
    c.shape("M-3,-6 L-12,-120 Q0,-128 12,-120 L3,-6 Z", color, sw=2, light=(-2, 0))
    c.line("M-2,-120 l1,-14", 2.4)
    c.line("M0,-6 v8 q0,8 -8,8 q-6,0 -6,-6", 3, P.WOOD_DARK)
    return _at(c, x, y, scale)


def motes(*quad_and_count, seed: int = 0) -> str:
    """Dust dancing in a sunbeam: tiny white dots inside the quadrilateral (x1, y1 ... x4, y4), `count` of them."""
    *quad, count = quad_and_count
    pts = list(zip(quad[0::2], quad[1::2], strict=False))
    rnd = random.Random(seed)
    c = Canvas()
    for _ in range(int(count)):
        u, v = rnd.random(), rnd.random()
        top = (pts[0][0] + (pts[1][0] - pts[0][0]) * u, pts[0][1] + (pts[1][1] - pts[0][1]) * u)
        bottom = (pts[3][0] + (pts[2][0] - pts[3][0]) * u, pts[3][1] + (pts[2][1] - pts[3][1]) * u)
        x, y = top[0] + (bottom[0] - top[0]) * v * 0.6, top[1] + (bottom[1] - top[1]) * v * 0.6
        c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rnd.uniform(1, 2.4))}" fill="{P.WHITE}" opacity=".8"/>')
    return c.render()


def box_of_floppies(x: float, y: float, scale: float = 1.0) -> str:
    """A cardboard box of old floppy disks, flaps open; 88 wide, 62 tall."""
    c = Canvas()
    for color, dx, turn in ((P.BLUE, -22, -12), (P.RED, -4, 6), (P.CHARCOAL, 14, -4), (P.YELLOW, 28, 14)):
        c.add(f'<g transform="translate({dx},-44) rotate({turn})">')
        c.shape("M-12,-14 H12 V12 H-12 Z", color, sw=1.6, light=None)
        c.path("M-6,-14 H6 V-6 H-6 Z", P.METAL_LIGHT, 1.2)
        c.path("M-8,2 H8 V12 H-8 Z", P.CARD, 1.2)
        c.add("</g>")
    c.shape("M-44,0 V-46 H44 V0 Z", P.WOOD_PALE, sw=2.3, light=(-3, -2), stipple=(20, -44, 24, 44, 18, "right"))
    c.shape("M-44,-46 L-58,-60 L-30,-60 L-20,-46 Z", lighten(P.WOOD_PALE, 0.2), sw=2, light=None)
    c.shape("M44,-46 L58,-58 L32,-60 L22,-46 Z", darken(P.WOOD_PALE, 0.92), sw=2, light=None)
    c.line("M-30,-28 h24 M-30,-20 h16", 2, P.WOOD_DARK, 0.7)
    return _at(c, x, y, scale)


def printout_stack(x: float, y: float, scale: float = 1.0, bundles: int = 4, seed: int = 0) -> str:
    """Yesterday's pull requests and the day before's: bundles of fan-fold paper tied with string, each bristling
    with comment flags; 100 wide."""
    rnd = random.Random(seed)
    c = Canvas()
    base = 0.0
    for _i in range(bundles):
        h = rnd.choice((16, 18, 20))
        dx = rnd.uniform(-6, 6)
        top = base - h
        c.shape(f"M{n(-46 + dx)},{n(base)} L{n(-48 + dx)},{n(top)} H{n(48 + dx)} L{n(46 + dx)},{n(base)} Z", P.CARD,
                sw=1.8, light=(-2, -1), shade_k=0.92)
        for k in range(1, 4):
            c.line(f"M{n(-46 + dx)},{n(base - h * k / 4)} H{n(46 + dx)}", 0.8, opacity=0.45)
        c.line(f"M{n(dx - 2)},{n(base)} V{n(top)} M{n(dx + 3)},{n(base)} V{n(top)}", 1.6, P.TERRACOTTA)
        for fx in range(-40, 44, 12):   # flags poking out of the sheets
            if rnd.random() < 0.7:
                color = rnd.choice((P.RED, P.YELLOW, P.BLUE))
                c.shape(f"M{n(fx + dx)},{n(top + 4)} l{n(rnd.uniform(-3, 3))},-9 l7,3 Z", color, sw=1.1, light=None)
        base = top
    c.shape(rounded_rect_d(-18, base - 26, 36, 22, 4), P.CREAM, sw=1.8, light=None)
    _label(c, 0, base - 9, "100", 15, P.RED)
    return _at(c, x, y, scale)


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


def meadow(c: Canvas, top: float, bottom: float, width: float, seed: int = 0, color: str = P.GRASS,
           near: str = P.GRASS_DARK) -> None:
    """The near ground: grass with stipple, `color` at the horizon deepening to `near` at the bottom."""
    paint = c.gradient([(0, color), (1, near)], 0, top, 0, bottom)
    c.path(f"M-4,{n(top)} Q{width * .3},{n(top - 12)} {width * .6},{n(top + 4)} T{width + 4},{n(top - 2)} "
           f"V{n(bottom + 4)} H-4 Z", paint, 2.4)
    c.dots(None, 0, top, width, (bottom - top) * 0.5, 320, "top", seed=seed, opacity=0.35)


def _catmull(points: list[tuple[float, float]], per: int = 12) -> list[tuple[float, float, float]]:
    """A smooth line through `points` (Catmull-Rom), sampled `per` times a stretch, as (x, y, t) where t runs
    from 0 at the first point to len(points) - 1 at the last."""
    out = []
    count = len(points)
    for i in range(count - 1):
        p0, p1, p2 = points[max(0, i - 1)], points[i], points[i + 1]
        p3 = points[min(count - 1, i + 2)]
        for j in range(per + (1 if i == count - 2 else 0)):
            t = j / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[q] + (p2[q] - p0[q]) * t + (2 * p0[q] - 5 * p1[q] + 4 * p2[q] - p3[q]) * t2
                                    + (3 * p1[q] - p0[q] - 3 * p2[q] + p3[q]) * t3) for q in (0, 1)) + (i + t,))
    return out


def path_band(c: Canvas, points: list[tuple[float, float]], widths: list[float], color: str = P.SAND,
              seed: int = 0, soft: bool = False) -> None:
    """A winding sandy path through `points` (far end first), `widths` giving its width at each: a smooth band,
    wider as it comes nearer, with pebbles sized by the distance. `soft` draws it as a country track: a thin
    edge line, a worn lighter middle and grass growing over its edges."""
    line = _catmull(points)
    lefts, rights, halves = [], [], []
    for i, (x, y, t) in enumerate(line):
        a, b = line[max(0, i - 1)], line[min(len(line) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1
        nx, ny = -dy / length, dx / length
        j = min(int(t), len(widths) - 2)
        half = (widths[j] + (widths[j + 1] - widths[j]) * (t - j)) / 2
        halves.append(half)
        lefts.append((x + nx * half, y + ny * half))
        rights.append((x - nx * half, y - ny * half))

    def poly(ls, rs) -> str:
        return ("M" + " L".join(f"{n(px)},{n(py)}" for px, py in ls) + " L" +
                " L".join(f"{n(px)},{n(py)}" for px, py in reversed(rs)) + " Z")

    rnd = random.Random(seed)
    if soft:
        c.path(poly(lefts, rights), color, 0)
        inner_l = [(x + (lx - x) * 0.45, y + (ly - y) * 0.45) for (x, y, _), (lx, ly) in zip(line, lefts, strict=True)]
        inner_r = [(x + (rx - x) * 0.45, y + (ry - y) * 0.45) for (x, y, _), (rx, ry) in zip(line, rights, strict=True)]
        c.path(poly(inner_l, inner_r), lighten(color, 0.35), 0)
        for edge in (lefts, rights):
            c.line("M" + " L".join(f"{n(px)},{n(py)}" for px, py in edge), 1.5, darken(color, 0.6), 0.9)
        for _ in range(int(len(line) * 0.9)):            # grass over the edges, bigger nearer
            i = rnd.randrange(len(line))
            edge = rnd.choice((lefts, rights))
            ex, ey = edge[i]
            g = 0.5 + halves[i] / max(halves) * 0.9
            c.line(f"M{n(ex)},{n(ey)} q-2,-6 -5,-9 M{n(ex + 2)},{n(ey)} q0,-8 1,-12 M{n(ex + 4)},{n(ey)} q3,-5 6,-8",
                   1.3 * g, P.LEAF_DARK, 0.85)
    else:
        c.path(poly(lefts, rights), color, 2.2)
    for _ in range(26 if not soft else 18):
        i = rnd.randrange(len(line) // 6, len(line))
        u = rnd.uniform(-0.65, 0.65)
        x, y, _ = line[i]
        px, py = x + (lefts[i][0] - x) * u, y + (lefts[i][1] - y) * u
        size = 0.35 + halves[i] / max(halves) * 0.75
        c.add(f'<ellipse cx="{n(px)}" cy="{n(py)}" rx="{n(rnd.uniform(2.5, 5) * size)}" ry="{n(2 * size)}" '
              f'fill="{P.PEBBLE}" stroke="{INK}" stroke-width="{n(0.6 + 0.5 * size)}"/>')


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


def bunting(points: list[tuple[float, float]], seed: int = 0, size: float = 18) -> str:
    """A garland of triangle flags sagging between points."""
    rnd = random.Random(seed)
    c = Canvas()
    colors = (P.RED, P.YELLOW, P.BLUE, P.GREEN, P.PINK, P.ORANGE)
    for (x1, y1), (x2, y2) in zip(points, points[1:], strict=False):
        sag = abs(x2 - x1) * 0.12
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + sag * 2
        c.line(f"M{n(x1)},{n(y1)} Q{n(mx)},{n(my)} {n(x2)},{n(y2)}", 1.6)
        count = max(2, int(abs(x2 - x1) / (size * 1.5)))
        for k in range(1, count):
            t = k / count
            px = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2
            py = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2
            color = colors[(k + rnd.randrange(6)) % 6]
            c.shape(f"M{n(px - size / 2)},{n(py)} L{n(px + size / 2)},{n(py)} L{n(px)},{n(py + size * 1.2)} Z", color,
                    sw=1.5, light=None)
    return c.render()


def stall(x: float, y: float, w: float = 200, h: float = 290, color: str = P.RED, sign: str = "") -> str:
    """A market stall: a striped scalloped awning on two posts, a sign board, a wooden counter.

    The origin is the middle of its foot; goods are placed on the counter (`STALL_COUNTER` above the foot)
    and hung under the awning by the caller."""
    c = Canvas()
    hw = w / 2
    awning_top = -h
    for px in (-hw + 10, hw - 10):
        c.shape(f"M{px - 5},0 V{awning_top + 30} H{px + 5} V0 Z", P.WOOD, sw=2.2, light=(-2, 0))
    # The back wall of the stall in shade, then the counter.
    c.shape(f"M{-hw + 15},{-STALL_COUNTER} V{awning_top + 50} H{hw - 15} V{-STALL_COUNTER} Z", darken(P.WOOD_PALE, 0.8),
            sw=2, light=None, stipple=(-hw + 15, awning_top + 50, w - 30, 60, 60, "top"))
    c.shape(f"M{-hw},0 V{-STALL_COUNTER} H{hw} V0 Z", P.WOOD_LIGHT, sw=2.4, light=(-3, -3),
            stipple=(hw - 40, -STALL_COUNTER, 40, STALL_COUNTER, 26, "right"))
    for k in range(1, 4):
        c.line(f"M{-hw},{n(-STALL_COUNTER * k / 4)} H{hw}", 1.2, opacity=0.55)
    c.shape(rounded_rect_d(-hw - 8, -STALL_COUNTER - 10, w + 16, 12, 3), P.WOOD, sw=2.3, light=None)
    # The awning: a slanted roof of stripes with a scalloped edge.
    roof = f"M{-hw - 16},{awning_top + 50} L{-hw + 12},{awning_top} H{hw - 12} L{hw + 16},{awning_top + 50} Z"
    clip = c.shape(roof, P.WHITE, sw=0, light=None, clip=True)
    stripes = "".join(f'<path d="M{n(-hw - 16 + i * 32)},{awning_top + 52} L{n(-hw + 6 + i * 26)},{awning_top - 2} '
                      f'h13 L{n(-hw + i * 32)},{awning_top + 52} Z" '
                      f'fill="{color}"/>' for i in range(0, int(w / 26) + 3, 2))
    c.add(f'<g clip-path="url(#{clip})">{stripes}</g>')
    c.path(roof, "none", 2.4)
    count = int((w + 32) / 32)
    step = (w + 32) / count
    for i in range(count):
        x0 = -hw - 16 + i * step
        fill = color if i % 2 == 0 else P.WHITE
        c.shape(f"M{n(x0)},{awning_top + 50} Q{n(x0 + step / 2)},{awning_top + 74} {n(x0 + step)},{awning_top + 50} Z",
                fill, sw=2.2, light=None)
    if sign:
        sw = max(90, len(sign) * 15 + 24)
        c.shape(rounded_rect_d(-sw / 2, awning_top - 40, sw, 36, 6), P.CREAM, sw=2.4, light=(-2, -2), shade_k=0.9)
        c.line(f"M{-sw / 2 + 10},{awning_top - 4} L{-sw / 2 + 16},{awning_top + 4} M{sw / 2 - 10},{awning_top - 4} "
               f"L{sw / 2 - 16},{awning_top + 4}", 2)
        _label(c, 0, awning_top - 14, sign, 21)
    return _at(c, x, y)


STALL_COUNTER = 92


def brain_jar(x: float, y: float, size: float = 1.0, price: str = "", glow: str = P.PINK) -> str:
    """A glass jar holding a pink brain, with a price tag on a string; 60 tall at size 1."""
    c = Canvas()
    c.shape("M-26,0 Q-30,-30 -24,-52 H24 Q30,-30 26,0 Z", lighten(P.WATER_LIGHT, 0.4), sw=2.2, light=None)
    c.shape("M-18,-12 Q-24,-28 -12,-34 Q-8,-46 4,-42 Q16,-46 18,-32 Q26,-24 16,-12 Q0,-6 -18,-12 Z",
            lighten(glow, 0.35), sw=1.8, light=(-2, -2), shade_k=0.86)
    c.line("M-10,-30 q4,-4 8,0 q4,4 8,0 M-12,-20 q6,-3 10,1 M4,-20 q4,-4 9,0 M0,-40 v8", 1.3)
    c.line("M-20,-44 Q-24,-26 -20,-10", 3, P.WHITE, 0.7)
    c.shape(rounded_rect_d(-27, -60, 54, 10, 3), P.METAL, sw=2, light=None)
    if price:
        c.line("M22,-56 Q34,-56 38,-44", 1.2)
        c.shape("M30,-46 H58 V-30 H30 L26,-38 Z", P.CREAM, sw=1.6, light=None)
        _label(c, 44, -34, price, 11)
    return _at(c, x, y, size)


def harness(x: float, y: float, scale: float = 1.0, color: str = P.LEATHER) -> str:
    """A harness hanging from a hook: a collar with straps and buckles: a harness in the literal sense."""
    c = Canvas()
    c.line("M0,0 V8", 2)
    c.path("M-4,8 q4,-6 8,0", "none", 2)
    c.shape(ellipse_d(0, 46, 30, 36), color, sw=2.4, light=(-3, -3))
    c.shape(ellipse_d(0, 50, 17, 24), P.CREAM, sw=2, light=None)
    for side in (-1, 1):
        c.line(f"M{side * 24},70 Q{side * 30},100 {side * 22},124", 7, color)
        c.line(f"M{side * 24},70 Q{side * 30},100 {side * 22},124", 1.4, darken(color, 0.6))
        c.shape(rounded_rect_d(side * 24 - 6, 92, 12, 10, 2), P.SUN, sw=1.6, light=None)
    c.add(f'<circle cx="0" cy="12" r="4" fill="{P.SUN}" stroke="{INK}" stroke-width="1.5"/>')
    return _at(c, x, y, scale)


def toolbelt(x: float, y: float, scale: float = 1.0) -> str:
    """A tool belt hanging from a hook, a wrench and a screwdriver in its pockets."""
    c = Canvas()
    c.line("M0,0 V10", 2)
    c.path("M-34,14 Q0,4 34,14 L34,24 Q0,14 -34,24 Z", P.LEATHER, 2.2)
    for px in (-22, 4):
        c.shape(f"M{px},20 H{px + 20} V48 Q{px + 10},54 {px},48 Z", lighten(P.LEATHER, 0.15), sw=2, light=(-1, -1))
    c.line("M-14,22 V-2", 4, P.METAL_DARK)
    c.add(f'<circle cx="-14" cy="-4" r="6" fill="none" stroke="{P.METAL_DARK}" stroke-width="4"/>')
    c.line("M14,22 V2", 4, P.RED)
    c.line("M14,2 V-12", 2.2, P.METAL_DARK)
    c.shape(rounded_rect_d(-4, 12, 8, 12, 2), P.SUN, sw=1.4, light=None)
    return _at(c, x, y, scale)


def backpack(x: float, y: float, scale: float = 1.0, color: str = P.GREEN) -> str:
    """A rucksack hanging from a hook by its loop."""
    c = Canvas()
    c.line("M0,0 V8", 2)
    c.shape("M-24,16 Q-28,8 -14,6 H14 Q28,8 24,16 L26,68 Q0,76 -26,68 Z", color, sw=2.3, light=(-3, -2))
    c.shape("M-16,40 H16 V62 Q0,66 -16,62 Z", darken(color, 0.9), sw=1.8, light=None)
    c.line("M-24,22 Q0,30 24,22", 1.8)
    c.shape(rounded_rect_d(-4, 36, 8, 8, 2), P.SUN, sw=1.2, light=None)
    return _at(c, x, y, scale)


def hard_hat(x: float, y: float, scale: float = 1.0, color: str = P.YELLOW) -> str:
    c = Canvas()
    c.shape("M-22,0 Q-22,-26 0,-26 Q22,-26 22,0 Z", color, sw=2.2, light=(-2, -2), highlight="M-12,-16 Q-14,-8 -14,-2")
    c.shape(rounded_rect_d(-28, -2, 56, 6, 3), color, sw=2, light=None)
    c.line("M0,-26 V-2", 2)
    return _at(c, x, y, scale)


def podium(x: float, y: float, scale: float = 1.0) -> str:
    """A winners' podium, places 2-1-3; the origin is the middle of its foot. 180 wide; the tops of the steps
    are 54, 78 and 40 units up."""
    c = Canvas()
    for px, h, place, color in ((-60, 54, "2", P.METAL_LIGHT), (0, 78, "1", P.SUN), (60, 40, "3", P.WOOD_LIGHT)):
        c.shape(f"M{px - 30},0 V{-h} H{px + 30} V0 Z", color, sw=2.4, light=(-3, -3), shade_k=0.86)
        _label(c, px, -h + 30, place, 26, INK)
    return _at(c, x, y, scale)


def skateboard(x: float, y: float, scale: float = 1.0, speed: bool = True) -> str:
    """A skateboard with speed lines behind it; the origin is where the deck's middle sits."""
    c = Canvas()
    c.shape("M-40,0 Q-46,-6 -40,-8 H40 Q46,-6 40,0 Z", P.RED, sw=2.2, light=None)
    for wx in (-26, 26):
        c.shape(ellipse_d(wx, 6, 6, 6), P.SUN, sw=1.8, light=None)
    if speed:
        c.line("M-60,-14 h-30 M-58,-2 h-46 M-62,10 h-22 M-70,-26 h-18", 2.2, opacity=0.8)
        c.add(f'<path d="M-56,6 q-6,-4 -12,0 q-6,-6 -12,0 q-4,6 4,6 h18 q6,0 2,-6 Z" fill="{P.WHITE}" '
              f'stroke="{INK}" stroke-width="1.4"/>')
    return _at(c, x, y, scale)


def wheelbarrow(x: float, y: float, scale: float = 1.0, mirror: bool = False) -> str:
    """A wheelbarrow; the origin is under its wheel, the handles reach back 120 units."""
    c = Canvas()
    c.line("M-4,-20 L-120,-34 M-24,-24 L-60,0 M-92,-30 L-96,0", 5, P.WOOD_DARK)
    c.shape("M-30,-26 L-12,-64 H-104 L-96,-26 Z", P.BLUE, sw=2.4, light=(-3, -2))
    c.shape(ellipse_d(0, -14, 14, 14), P.CHARCOAL, sw=2.2, light=None)
    c.add(f'<circle cx="0" cy="-14" r="4" fill="{P.METAL}" stroke="{INK}" stroke-width="1.4"/>')
    return _at(c, x, y, scale, mirror)


def gpu_box(x: float, y: float, scale: float = 1.0, label: str = "") -> str:
    """A big graphics card in its box, three fans showing through the window; 110 wide, 54 tall."""
    c = Canvas()
    c.shape("M-55,0 V-54 H55 V0 Z", P.CHARCOAL, sw=2.4, light=(-3, -3), shade_k=0.8)
    c.shape("M-48,-8 V-46 H48 V-8 Z", P.METAL_DARK, sw=1.8, light=None)
    for fx in (-30, 0, 30):
        c.shape(ellipse_d(fx, -29, 12, 12), P.CHARCOAL, sw=1.6, light=None)
        for a in range(0, 360, 60):
            c.line(f"M{fx},-27 l{n(10 * math.cos(math.radians(a)))},{n(10 * math.sin(math.radians(a)))}", 1.6, P.METAL)
        c.dot(fx, -27, 2.4, P.METAL_LIGHT)
    c.line("M-48,-50 H48", 2.2, P.GREEN)
    if label:
        c.shape(rounded_rect_d(-20, -12, 40, 13, 3), P.GREEN, sw=1.4, light=None)
        _label(c, 0, -2, label, 10, P.WHITE)
    return _at(c, x, y, scale)


def snail(x: float, y: float, scale: float = 1.0, mirror: bool = False) -> str:
    c = Canvas()
    c.shape("M-30,0 Q-32,-8 -20,-8 H14 Q22,-8 24,-20 L28,-24 Q30,-8 22,0 Z", P.LEAF_LIGHT, sw=2, light=(-1, -1))
    c.line("M20,-20 l-2,-12 M25,-21 l4,-11", 1.6)
    c.dot(18, -33, 2)
    c.dot(29, -33, 2)
    c.shape(ellipse_d(-6, -22, 18, 16), P.AMBER, sw=2.2, light=(-2, -2))
    c.line("M-6,-22 m-10,0 a10,9 0 1 1 10,9 a6,5 0 1 1 -4,-6", 1.6)
    return _at(c, x, y, scale, mirror)


def high_striker(x: float, y: float, height: float = 340, level: float = 0.62) -> str:
    """The fair's test of strength: a tall striped board with a bell on top, the puck stopped at `level`; a mallet
    leans at its foot. 46 wide."""
    c = Canvas()
    top = -height
    c.shape(f"M-22,0 V{top + 26} H22 V0 Z", P.CARD, sw=2.4, light=(-3, -2), shade_k=0.92)
    bands = (P.GREEN, P.YELLOW, P.ORANGE, P.RED)
    span = height - 60
    for i, color in enumerate(bands):
        y0 = -20 - span * (i + 1) / 4
        c.shape(f"M-16,{n(y0)} H16 V{n(y0 + span / 4 - 4)} H-16 Z", color, sw=1.4, light=None)
    for k in range(1, 12):
        c.line(f"M-16,{n(-20 - span * k / 12)} h8", 1.2)
    c.line(f"M0,-14 V{top + 28}", 2.4, P.METAL_DARK)
    py = -20 - span * level
    c.shape(rounded_rect_d(-12, py - 8, 24, 14, 4), P.RED, sw=2, light=None)
    c.shape(f"M-20,{top + 26} Q-20,{top - 6} 0,{top - 6} Q20,{top - 6} 20,{top + 26} Z", P.SUN, sw=2.3, light=(-2, -2),
            highlight=f"M-12,{top + 16} Q-12,{top + 4} -6,{top}")
    c.dot(0, top + 26, 3)
    c.shape("M-34,0 V-14 H34 V0 Z", P.WOOD_DARK, sw=2.2, light=None)
    c.shape(rounded_rect_d(-16, -26, 32, 12, 3), P.METAL_DARK, sw=2, light=None)   # the pad you strike
    c.line("M30,0 L38,-40", 5, P.WOOD)                                          # the mallet, leaning on it
    c.shape(rounded_rect_d(26, -60, 26, 20, 5), P.WOOD_DARK, sw=2, light=None)
    return _at(c, x, y)


def picnic(x: float, y: float, scale: float = 1.0) -> str:
    """A checked blanket on the grass with a basket, two apples and a thermos; 200 wide, 70 deep."""
    c = Canvas()
    blanket = "M-100,0 L-70,-60 L104,-58 L96,6 Z"
    clip = c.shape(blanket, P.WHITE, sw=0, light=None, clip=True)
    checks = "".join(f'<path d="M{-110 + i * 24},10 L{-80 + i * 24},-70 h12 L{-98 + i * 24},10 Z" fill="{P.RED}" '
                     f'opacity=".75"/>' for i in range(0, 10))
    rows = "".join(f'<path d="M-120,{-6 - j * 14} H120 V{-6 - j * 14 + 7} H-120 Z" fill="{P.RED}" opacity=".45"/>'
                   for j in range(0, 5))
    c.add(f'<g clip-path="url(#{clip})">{checks}{rows}</g>')
    c.path(blanket, "none", 2.2)
    # The basket with its handle.
    c.line("M-46,-50 Q-20,-96 6,-50", 4, P.WOOD_DARK)
    c.shape("M-56,-48 H16 L8,-14 H-48 Z", P.WOOD_LIGHT, sw=2.2, light=(-2, -2))
    c.line("M-52,-38 H12 M-50,-28 H10 M-49,-20 H9", 1.2, P.WOOD_DARK)
    c.shape("M-40,-48 Q-30,-62 -16,-50 Z", P.CREAM, sw=1.6, light=None)
    for ax, color in ((40, P.RED), (62, P.GREEN)):
        c.shape(ellipse_d(ax, -24, 11, 10), color, sw=1.8, light=(-1, -1), highlight=f"M{ax - 5},-29 q-2,4 0,7")
        c.line(f"M{ax},-34 l2,-6", 1.6, P.WOOD_DARK)
    c.shape(rounded_rect_d(78, -64, 18, 40, 5), P.BLUE, sw=2, light=(-2, -1))
    c.shape(rounded_rect_d(76, -70, 22, 9, 3), P.METAL, sw=1.6, light=None)
    return _at(c, x, y, scale)


def grass_tufts(c: Canvas, region: tuple, count: int, seed: int = 0) -> None:
    """Little strokes of grass across a meadow: the texture of the ground, drawn on the backdrop."""
    rnd = random.Random(seed)
    left, top, right, bottom = region
    for _ in range(count):
        x, y = rnd.uniform(left, right), rnd.uniform(top, bottom)
        k = 0.7 + (y - top) / max(1, bottom - top) * 0.7
        c.line(f"M{n(x)},{n(y)} q-3,-7 -6,-11 M{n(x + 2)},{n(y)} q0,-9 1,-15 M{n(x + 4)},{n(y)} q3,-6 7,-10",
               1.5 * k, P.LEAF_DARK, 0.8)


# ============================================================================ the valley of services
def river(c: Canvas, points: list[tuple[float, float]], widths: list[float], seed: int = 0) -> None:
    """A river winding towards the viewer, with ripples; drawn on the backdrop."""
    lefts, rights = [], []
    for i, (x, y) in enumerate(points):
        a, b = points[max(0, i - 1)], points[min(len(points) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1
        nx, ny = -dy / length, dx / length
        lefts.append((x + nx * widths[i] / 2, y + ny * widths[i] / 2))
        rights.append((x - nx * widths[i] / 2, y - ny * widths[i] / 2))
    d = "M" + " L".join(f"{n(px)},{n(py)}" for px, py in lefts) + " L" + " L".join(
        f"{n(px)},{n(py)}" for px, py in reversed(rights)) + " Z"
    paint = c.gradient([(0, P.WATER_LIGHT), (1, P.WATER)], 0, points[0][1], 0, points[-1][1])
    c.path(d, paint, 2.2)
    rnd = random.Random(seed)
    for _ in range(18):
        i = rnd.randrange(1, len(points) - 1)
        x, y = points[i][0] + rnd.uniform(-0.3, 0.3) * widths[i], points[i][1] + rnd.uniform(-6, 6)
        w = widths[i] * 0.12
        c.line(f"M{n(x - w)},{n(y)} q{n(w / 2)},-4 {n(w)},0 q{n(w / 2)},-4 {n(w)},0", 1.4, P.WHITE, 0.9)


def cable(points: list[tuple[float, float]], color: str, width: float = 5) -> str:
    """A cable or hose along the polygon `points`, every corner eased into a smooth bend (`curves`): it leaves the
    first point and enters the last straight along the polygon's end runs, so it goes into a plug or a socket
    coaxially."""
    from .curves import eased_d
    d = eased_d(points, width * 1.5, width * 1.5)
    c = Canvas()
    c.line(d, width + 3.2)
    c.line(d, width, color)
    c.line(d, max(1.0, width * 0.3), lighten(color, 0.45), 0.7)
    return c.render()


def hub(x: float, y: float, scale: float = 1.0, label: str = "MCP", sockets: tuple = ()) -> str:
    """A wooden box with a row of sockets on its front: the place every cable plugs into. 120 wide, 100 tall;
    `sockets` are the colors of the plugs already in."""
    c = Canvas()
    c.shape("M-60,0 V-86 H60 V0 Z", P.WOOD_LIGHT, sw=2.6, light=(-3, -3), stipple=(30, -84, 30, 84, 26, "right"))
    c.shape("M-66,-86 L-52,-102 H66 L60,-86 Z", lighten(P.WOOD_LIGHT, 0.2), sw=2.3, light=None)
    c.line("M-60,-60 H60 M-60,-24 H60", 1.3, opacity=0.5)
    c.path(rounded_rect_d(-36, -80, 72, 22, 4), P.CREAM, 2)
    _label(c, 0, -63, label, 17)
    count = max(4, len(sockets))
    for i in range(count):
        sx = -45 + i * 90 / (count - 1)
        c.shape(rounded_rect_d(sx - 9, -48, 18, 18, 4), P.CHARCOAL, sw=1.8, light=None)
        if i < len(sockets):
            c.shape(rounded_rect_d(sx - 6, -45, 12, 12, 2), sockets[i], sw=1.6, light=None)
        else:
            c.dot(sx - 3, -39, 1.6, P.METAL)
            c.dot(sx + 3, -39, 1.6, P.METAL)
        c.add(f'<circle cx="{n(sx)}" cy="-14" r="3" fill="{(P.GREEN if i < len(sockets) else P.RED)}" '
              f'stroke="{INK}" stroke-width="1.2"/>')
    return _at(c, x, y, scale)


def _sign_board(c: Canvas, x: float, y: float, text: str, size: float = 18, color: str = P.CREAM) -> None:
    w = max(64, len(text) * size * 0.66 + 22)
    c.shape(rounded_rect_d(x - w / 2, y - size - 10, w, size + 16, 5), color, sw=2.2, light=(-2, -2), shade_k=0.9)
    _label(c, x, y - 2, text, size)


def log_cabin(x: float, y: float, scale: float = 1.0, sign: str = "") -> str:
    """A log cabin piled with rolls of paper on its porch: where the logs are kept. 190 wide, 170 tall."""
    c = Canvas()
    c.shape("M-82,0 V-96 H82 V0 Z", P.TRUNK, sw=2.5, light=(-3, -2))
    for k in range(8):
        yy = -6 - k * 12
        c.line(f"M-82,{yy} H82", 1.2, opacity=0.6)
        c.add(f'<circle cx="-82" cy="{yy - 6}" r="6" fill="{P.WOOD_PALE}" stroke="{INK}" stroke-width="1.6"/>'
              f'<circle cx="82" cy="{yy - 6}" r="6" fill="{P.WOOD_PALE}" stroke="{INK}" stroke-width="1.6"/>')
    c.shape("M-98,-90 L0,-168 L98,-90 Z", P.RED, sw=2.6, light=(-4, -3), stipple=(20, -160, 70, 70, 30, "right"))
    c.shape("M-22,0 V-60 H22 V0 Z", P.WOOD_DARK, sw=2.2, light=None)
    c.dot(14, -30, 2.4, P.SUN)
    c.shape("M38,-66 H70 V-38 H38 Z", P.SUN, sw=2.2, light=None)
    c.line("M54,-66 V-38 M38,-52 H70", 1.6)
    c.shape("M40,-130 V-160 H58 V-118 Z", P.STONE, sw=2, light=None)
    c.line("M49,-162 q-10,-14 2,-24 q10,-10 -2,-22", 2.2, P.WHITE, 0.8)
    for px, py in ((-66, 0), (-50, 0), (-58, -16), (-74, -16), (-42, -16), (-60, -32)):   # paper rolls
        c.shape(ellipse_d(px, py - 8, 8, 8), P.CARD, sw=1.6, light=None)
        c.add(f'<circle cx="{px}" cy="{py - 8}" r="3" fill="none" stroke="{INK}" stroke-width="1"/>')
    if sign:
        _sign_board(c, 0, -110, sign, 18)
    return _at(c, x, y, scale)


def weather_station(x: float, y: float, scale: float = 1.0, sign: str = "") -> str:
    """A lattice mast with a wind vane and cups, a big dial and a chart board: the metrics. 120 wide, 260 tall."""
    c = Canvas()
    c.line("M-30,0 L-8,-220 M30,0 L8,-220", 4, P.METAL_DARK)
    for k in range(9):
        y0, y1 = -k * 24, -(k + 1) * 24
        w0, w1 = 30 - 22 * k / 9, 30 - 22 * (k + 1) / 9
        c.line(f"M{n(-w0)},{y0} L{n(w1)},{y1} M{n(w0)},{y0} L{n(-w1)},{y1}", 1.4, P.METAL_DARK)
    c.line("M0,-220 V-256", 3)
    c.line("M-30,-246 H30", 2.4)
    c.shape("M30,-246 l-12,-8 v16 Z", P.RED, sw=1.6, light=None)
    c.line("M-30,-246 l-8,-6 M-30,-246 l-8,6", 2)
    for a in (0, 120, 240):   # the spinning cups
        r = math.radians(a)
        cx, cy = math.cos(r) * 18, -232 + math.sin(r) * 5
        c.line(f"M0,-232 L{n(cx)},{n(cy)}", 1.6)
        c.shape(ellipse_d(cx, cy, 5, 4), P.METAL_LIGHT, sw=1.4, light=None)
    # The chart board on its legs, with a rising line.
    c.line("M40,0 V-60 M98,0 V-60", 4, P.WOOD_DARK)
    c.shape("M30,-60 V-128 H108 V-60 Z", P.CARD, sw=2.3, light=(-2, -2), shade_k=0.94)
    c.line("M38,-70 L54,-84 L66,-78 L80,-102 L92,-96 L102,-118", 2.6, P.GREEN)
    c.line("M38,-70 H104 M38,-70 V-122", 1.2, opacity=0.6)
    # A round gauge low on the mast.
    c.shape(ellipse_d(-40, -86, 22, 22), P.CARD, sw=2.3, light=(-2, -2), shade_k=0.92)
    c.line("M-56,-90 A16,16 0 0 1 -24,-90", 3, P.YELLOW)
    c.line("M-40,-86 L-30,-100", 2.4, P.RED)
    c.dot(-40, -86, 2.6)
    if sign:
        _sign_board(c, 0, -144, sign, 18)
    return _at(c, x, y, scale)


def ticket_booth(x: float, y: float, scale: float = 1.0, sign: str = "") -> str:
    """A little post office with a ticket window, a roll of tickets pouring out of it. 180 wide, 230 tall."""
    c = Canvas()
    c.shape("M-80,0 V-150 H80 V0 Z", P.CREAM, sw=2.6, light=(-3, -3), stipple=(50, -148, 30, 148, 30, "right"))
    for k in range(5):
        c.line(f"M-80,{-14 - k * 30} H80", 1, P.WOOD_PALE)
    c.shape("M-96,-146 Q0,-226 96,-146 Z", P.BLUE, sw=2.6, light=(-4, -3))
    c.line("M-60,-170 Q0,-206 60,-170", 1.6, P.WHITE, 0.6)
    c.shape("M6,-120 H62 V-64 H6 Z", P.SKY_DEEP, sw=2.4, light=None)                    # the ticket window
    c.shape(rounded_rect_d(0, -66, 68, 9, 3), P.WOOD, sw=2, light=None)
    c.line("M34,-120 V-66", 1.6)
    # Tickets pour out of a slot in a long curl down the wall.
    c.shape(rounded_rect_d(10, -62, 46, 8, 2), P.CHARCOAL, sw=1.6, light=None)
    strip = "M50,-56 Q62,-30 42,-24 Q22,-18 38,-6 Q50,4 32,6"
    c.line(strip, 14, INK)
    c.line(strip, 11, P.PINK_PALE)
    for t in (-48, -38, -26, -14):
        c.line(f"M40,{t} h12", 1, opacity=0.6)
    c.shape("M-62,0 V-96 H-18 V0 Z", P.WOOD_DARK, sw=2.4, light=None)                   # the door
    c.dot(-26, -48, 2.6, P.SUN)
    c.shape("M-52,-86 H-28 V-62 H-52 Z", P.SKY_DEEP, sw=1.8, light=None)
    if sign:
        _sign_board(c, 0, -160, sign, 19)
    return _at(c, x, y, scale)


def barn(x: float, y: float, scale: float = 1.0, sign: str = "") -> str:
    """A barn with barrels and crates stacked by its doors: the store, the database. 200 wide, 190 tall."""
    c = Canvas()
    c.shape("M-80,0 V-104 L0,-160 L80,-104 V0 "
        "Z", P.RED, sw=2.6, light=(-4, -3), stipple=(40, -150, 40, 150, 40, "right"))
    c.shape("M-92,-98 L0,-172 L92,-98 L80,-96 L0,-158 L-80,-96 Z", P.CARD, sw=2.2, light=None)
    c.shape("M-34,0 V-80 H34 V0 Z", P.CARD, sw=2.4, light=None)
    c.line("M-34,-80 L34,0 M34,-80 L-34,0 M0,-80 V0", 2)
    c.shape(ellipse_d(0, -122, 14, 14), P.CARD, sw=2, light=None)
    for bx in (-66, -50):
        c.shape(f"M{bx - 10},0 Q{bx - 13},-14 {bx - 10},-28 H{bx + 10} Q{bx + 13},-14 {bx + 10},0 Z", P.WOOD,
                sw=1.8, light=(-1, -1))
        c.line(f"M{bx - 11},-8 H{bx + 11} M{bx - 11},-20 H{bx + 11}", 1.6, P.METAL_DARK)
    c.shape("M46,0 V-30 H78 V0 Z", P.WOOD_LIGHT, sw=1.8, light=None)
    c.line("M46,-30 L78,0 M78,-30 L46,0", 1.2)
    if sign:
        _sign_board(c, 0, -176, sign, 18)
    return _at(c, x, y, scale)


def mailbox(x: float, y: float, scale: float = 1.0) -> str:
    """A red post box on a post; 36 wide, 104 tall."""
    c = Canvas()
    c.shape("M-5,0 V-60 H5 V0 Z", P.WOOD_DARK, sw=2, light=(-1, 0))
    c.shape("M-18,-60 V-90 Q-18,-104 0,-104 Q18,-104 18,-90 V-60 Z", P.RED, sw=2.3, light=(-2, -2),
            highlight="M-12,-88 Q-12,-96 -6,-99")
    c.shape(rounded_rect_d(-12, -88, 24, 5, 2), P.CHARCOAL, sw=1.4, light=None)
    c.line("M18,-84 l10,0 v-14", 2.2, P.METAL_DARK)
    c.shape("M28,-98 l12,4 l-12,4 Z", P.YELLOW, sw=1.4, light=None)
    return _at(c, x, y, scale)


def boat(x: float, y: float, scale: float = 1.0, mirror: bool = False) -> str:
    """A rowing boat with a fishing rod propped over its side; the origin is the waterline's middle. 120 wide."""
    c = Canvas()
    c.line("M-14,-16 Q50,-90 92,-70", 2.2, P.WOOD_DARK)
    c.line("M92,-70 V-4", 0.9)
    c.shape(ellipse_d(92, -2, 4, 3), P.RED, sw=1.2, light=None)
    c.shape("M-58,-20 H58 Q52,4 30,6 H-30 Q-52,4 -58,-20 Z", P.WOOD, sw=2.4, light=(-3, -2))
    c.line("M-52,-12 H52", 1.2, opacity=0.6)
    c.line("M-70,4 q8,-4 16,0 M50,6 q8,-4 16,0", 1.4, P.WHITE)
    return _at(c, x, y, scale, mirror)


def lily(x: float, y: float, scale: float = 1.0, frog: bool = False) -> str:
    c = Canvas()
    c.shape("M0,0 m-22,0 a22,7 0 1 0 44,0 a22,7 0 1 0 -44,0 Z M0,0 L20,-3 L18,3 Z", P.LEAF, sw=1.8, light=None)
    if frog:
        c.shape("M-12,-2 Q-14,-18 0,-20 Q14,-18 12,-2 Z", P.GREEN, sw=1.8, light=(-1, -1))
        for ex in (-6, 6):
            c.shape(ellipse_d(ex, -20, 5, 5), P.GREEN, sw=1.6, light=None)
            c.dot(ex, -20, 2)
        c.line("M-6,-10 q6,4 12,0", 1.4)
    else:
        c.shape("M-4,-4 q4,-14 8,0 q-4,3 -8,0 Z", P.PINK_PALE, sw=1.4, light=None)
    return _at(c, x, y, scale)


def dragonfly(x: float, y: float, scale: float = 1.0) -> str:
    c = Canvas()
    for dx, dy, turn in ((-14, -6, -18), (14, -6, 18), (-12, 2, -8), (12, 2, 8)):
        c.add(f'<ellipse cx="{dx}" cy="{dy}" rx="13" ry="4.5" transform="rotate({turn} {dx} {dy})" '
              f'fill="{P.WHITE}" fill-opacity=".7" stroke="{INK}" stroke-width="1.2"/>')
    c.line("M0,-8 V30", 3.4, P.TEAL)
    c.line("M0,-8 V30", 1)
    c.shape(ellipse_d(0, -10, 4.5, 4), P.TEAL, sw=1.4, light=None)
    return _at(c, x, y, scale)


def sun_low(c: Canvas, x: float, y: float, r: float) -> None:
    """A big setting sun with long soft rays, on the backdrop."""
    for k, alpha in ((2.2, 0.18), (1.6, 0.25)):
        c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r * k)}" fill="{P.SUN}" opacity="{alpha}"/>')
    c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{P.SUN}" stroke="{INK}" stroke-width="2.4"/>')


def mountains(c: Canvas, base: float, width: float, color: str, seed: int = 0) -> None:
    """A far range of snow-capped mountains on the backdrop."""
    rnd = random.Random(seed)
    peaks = [(-20, base - 40)]
    x = -20.0
    while x < width + 40:
        x += rnd.uniform(70, 130)
        peaks.append((x, base - rnd.uniform(90, 170)))
        x += rnd.uniform(50, 90)
        peaks.append((x, base - rnd.uniform(40, 80)))
    ridge = " ".join(f"L{n(px)},{n(py)}" for px, py in peaks)
    d = f"M-20,{n(base + 10)} {ridge} L{n(width + 40)},{n(base + 10)} Z"
    c.shape(d, color, sw=2, light=(-8, -4), shade_k=0.9)
    for i in range(1, len(peaks) - 1, 2):
        px, py = peaks[i]
        c.path(f"M{n(px - 16)},{n(py + 22)} L{n(px)},{n(py)} L{n(px + 15)},{n(py + 20)} L{n(px + 6)},{n(py + 14)} "
               f"L{n(px - 2)},{n(py + 24)} Z", P.WHITE, 1.6)


def stars(c: Canvas, region: tuple, count: int, seed: int = 0) -> None:
    rnd = random.Random(seed)
    left, top, right, bottom = region
    for _ in range(count):
        x, y = rnd.uniform(left, right), rnd.uniform(top, bottom)
        r = rnd.uniform(2, 4.5)
        c.add(f'<path d="M{n(x)},{n(y - r)} L{n(x + r * 0.3)},{n(y - r * 0.3)} L{n(x + r)},{n(y)} '
              f'L{n(x + r * 0.3)},{n(y + r * 0.3)} L{n(x)},{n(y + r)} L{n(x - r * 0.3)},{n(y + r * 0.3)} '
              f'L{n(x - r)},{n(y)} '
              f'L{n(x - r * 0.3)},{n(y - r * 0.3)} Z" fill="{P.WHITE}" opacity=".85"/>')


def windmill(x: float, y: float, scale: float = 1.0, turn: float = 15) -> str:
    """A small windmill; 120 wide with its sails, 170 tall."""
    c = Canvas()
    c.shape("M-24,0 L-16,-92 H16 L24,0 Z", P.CREAM, sw=2.3, light=(-2, -2))
    c.shape("M-22,-90 L0,-118 L22,-90 Z", P.WOOD_DARK, sw=2.2, light=None)
    c.shape("M-7,0 V-24 Q0,-32 7,-24 V0 Z", P.WOOD_DARK, sw=1.8, light=None)
    c.add(f'<g transform="translate(0,-100) rotate({turn})">')
    for a in (0, 90, 180, 270):
        c.add(f'<g transform="rotate({a})"><path d="M0,0 L0,-58" stroke="{INK}" stroke-width="3"/>'
              f'<path d="M2,-16 H14 V-56 H2 Z" fill="{P.WHITE}" stroke="{INK}" stroke-width="1.6"/>'
              f'<path d="M2,-28 H14 M2,-42 H14" stroke="{INK}" stroke-width=".9"/></g>')
    c.add(f'<circle cx="0" cy="0" r="4" fill="{P.WOOD_DARK}" stroke="{INK}" stroke-width="1.4"/></g>')
    return _at(c, x, y, scale)


def footbridge(x: float, y: float, w: float = 90, scale: float = 1.0) -> str:
    """A little wooden arched footbridge; the origin is the middle of its span on the water."""
    c = Canvas()
    hw = w / 2
    c.shape(f"M{-hw},0 Q0,-30 {hw},0 L{hw},8 Q0,-22 {-hw},8 Z", P.WOOD, sw=2.2, light=(-1, -2))
    for k in range(-3, 4):
        px = k * hw / 3.4
        py = -30 * (1 - (px / hw) ** 2) * 0.5 - 2
        c.line(f"M{n(px)},{n(py + 2)} V{n(py - 20)}", 2.4, P.WOOD_DARK)
    c.line(f"M{-hw},-18 Q0,-48 {hw},-18", 2.6, P.WOOD_DARK)
    return _at(c, x, y, scale)


# ============================================================================ the house of the repository
def house_shell(c: Canvas, left: float, right: float, ground: float, floors: list[float], roof_top: float,
                partitions: list[tuple[float, float, float, float]], papers: list[str]) -> None:
    """A dolls' house with its front taken off: walls, floor slabs, a pitched roof with a chimney, and the
    rooms' wallpaper. `floors` are the y of each floor slab from the bottom up (the last one is the attic's);
    `partitions` are inner walls (x, y top, y bottom, doorway height); `papers` the wallpaper colors, room by
    room, bottom-left first."""
    t = 12
    mid = (left + right) / 2
    attic = floors[-1]
    # The chimney rises from the right slope of the roof (drawn first, so the roof covers its foot).
    cx = mid + (right - left) * 0.3
    slope = roof_top + (cx - mid) / (right + 22 - mid) * (attic + 10 - roof_top)
    c.shape(f"M{n(cx - 17)},{n(slope + 24)} V{n(slope - 92)} H{n(cx + 17)} V{n(slope + 24)} Z", P.TERRACOTTA, sw=2.3,
            light=(-2, -1))
    c.shape(rounded_rect_d(cx - 23, slope - 102, 46, 11, 3), P.STONE, sw=2, light=None)
    c.line(f"M{n(cx)},{n(slope - 106)} q-14,-20 4,-36 q16,-16 -2,-34 q-12,-12 2,-26", 3, P.WHITE, 0.85)
    # The roof: an outer triangle in tiles, the attic's inside lit.
    c.shape(f"M{n(left - 22)},{n(attic + 10)} L{n(mid)},{n(roof_top)} L{n(right + 22)},{n(attic + 10)} Z", P.TERRACOTTA,
            sw=2.6, light=(-4, -3))
    for k in range(1, 7):   # rows of tiles
        f = k / 7
        y = roof_top + (attic + 10 - roof_top) * f
        half = (right + 22 - mid) * f
        c.line(f"M{n(mid - half)},{n(y)} H{n(mid + half)}", 1.2, opacity=0.5)
    inner = 22
    c.shape(f"M{n(left + inner)},{n(attic)} L{n(mid)},{n(roof_top + inner * 1.6)} L{n(right - inner)},{n(attic)} Z",
            lighten(P.WOOD_PALE, 0.2), sw=2.2, light=None,
            stipple=(mid, roof_top + 40, right - mid - inner, attic - roof_top - 40, 50, "right"))
    for k in (-0.5, 0, 0.5):   # rafters
        x = mid + k * (right - left - 2 * inner) * 0.5
        c.line(f"M{n(x)},{n(attic)} L{n(mid)},{n(roof_top + inner * 1.6)}", 2, P.WOOD_DARK, 0.5)
    # Rooms: wallpaper behind, from the ground up.
    rooms = []
    levels = [ground] + floors
    for i in range(len(levels) - 1):
        bottom, top = levels[i], levels[i + 1] + t
        cuts = [left + t] + [p[0] for p in partitions if p[1] <= top + 2 and p[2] >= bottom - 2] + [right - t]
        cuts = sorted(set(cuts))
        for a, b in zip(cuts, cuts[1:], strict=False):
            rooms.append((a + (t if a != left + t else 0), top, b, bottom))
    for (x0, y0, x1, y1), color in zip(rooms, papers, strict=False):
        paint = c.gradient([(0, lighten(color, 0.25)), (1, color)], x0, y0, x1, y1)
        c.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" fill="{paint}"/>')
        for k in range(int(x0) + 14, int(x1), 26):
            c.add(f'<path d="M{k},{n(y0)} V{n(y1)}" stroke="{darken(color, 0.9)}" stroke-width="6" '
                f'stroke-opacity=".3"/>')
        c.add(f'<rect x="{n(x0)}" y="{n(y1 - 10)}" width="{n(x1 - x0)}" height="10" fill="{P.WOOD}" stroke="{INK}" '
              f'stroke-width="1.6"/>')
    # Outer walls and slabs.
    c.shape(f"M{n(left)},{n(ground)} V{n(attic)} H{n(left + t)} V{n(ground)} Z", P.CARD, sw=2.4, light=None)
    c.shape(f"M{n(right - t)},{n(ground)} V{n(attic)} H{n(right)} V{n(ground)} Z", P.CARD, sw=2.4, light=None)
    for y in floors:
        c.shape(f"M{n(left - 4)},{n(y)} H{n(right + 4)} V{n(y + t)} H{n(left - 4)} Z", P.WOOD, sw=2.4, light=None)
    c.shape(f"M{n(left - 10)},{n(ground)} H{n(right + 10)} V{n(ground + 16)} H{n(left - 10)} Z", P.STONE, sw=2.4,
            light=None, stipple=(left - 10, ground, right - left + 20, 16, 40, "even"))
    for x, y0, y1, door in partitions:
        c.shape(f"M{n(x - t / 2)},{n(y0)} V{n(y1 - door)} H{n(x + t / 2)} V{n(y0)} Z", P.CARD, sw=2.2, light=None)
        c.shape(f"M{n(x - t / 2 - 3)},{n(y1 - door)} H{n(x + t / 2 + 3)} V{n(y1 - door + 6)} H{n(x - t / 2 - 3)} Z",
                P.WOOD_DARK, sw=1.6, light=None)


def front_door(x: float, y: float, h: float = 150, open_out: bool = True) -> str:
    """An open front door swung out to the left of a doorway at x; the origin is the doorway's foot."""
    c = Canvas()
    c.shape(f"M-6,0 V{-h} H6 V0 Z", P.WOOD_DARK, sw=2, light=None)
    if open_out:
        c.shape(f"M-6,0 L-56,12 V{-h + 14} L-6,{-h} Z", P.GREEN, sw=2.4, light=(-2, -2))
        c.shape(f"M-46,{n(-h * 0.55)} L-16,{n(-h * 0.6)} V{n(-h * 0.85)} L-46,{n(-h * 0.8)} Z", P.SKY_DEEP, sw=1.6,
                light=None)
        c.dot(-48, -h * 0.4, 3, P.SUN)
    c.shape("M-70,8 H6 L2,16 H-74 Z", P.RED, sw=1.8, light=None)   # the doormat
    return _at(c, x, y)


def ladder(x: float, top: float, bottom: float, w: float = 34) -> str:
    c = Canvas()
    c.line(f"M{n(x - w / 2)},{n(top)} V{n(bottom)} M{n(x + w / 2)},{n(top)} V{n(bottom)}", 5, P.WOOD_DARK)
    y = bottom - 18
    while y > top + 6:
        c.line(f"M{n(x - w / 2)},{n(y)} H{n(x + w / 2)}", 4, P.WOOD_DARK)
        y -= 26
    return c.render()


def pinned_sheet(x: float, y: float, label: str = "", scale: float = 1.0, turn: float = -3) -> str:
    """A sheet of paper pinned to a wall with a red pin, a short heading on it; the origin is the pin."""
    c = Canvas()
    c.shape("M-24,-2 H24 V60 H-24 Z", P.WHITE, sw=1.8, light=None)
    _label(c, 0, 15, label, min(9.5, 70 / max(1, len(label))))
    c.line("M-17,24 H17 M-17,32 H13 M-17,40 H17 M-17,48 H9", 1.1, opacity=0.5)
    c.add(f'<circle cx="0" cy="0" r="4.2" fill="{P.RED}" stroke="{INK}" stroke-width="1.4"/>')
    return _at(c, x, y, scale, turn=turn)


def room_sign(x: float, y: float, label: str, color: str = P.CREAM) -> str:
    """A small plate over a doorway with a folder's name."""
    c = Canvas()
    w = max(56, len(label) * 11 + 18)
    c.shape(rounded_rect_d(-w / 2, -14, w, 26, 5), color, sw=2, light=None)
    _label(c, 0, 5, label, 15)
    return _at(c, x, y)


def workbench(x: float, y: float, scale: float = 1.0) -> str:
    """A workbench with a machine of gears on it, sticky notes on the machine: comments next to the code. 160 wide."""
    c = Canvas()
    c.line("M-70,0 V-58 M70,0 V-58 M-62,0 V-58 M62,0 V-58", 5, P.WOOD_DARK)
    c.line("M-70,-26 H70", 3, P.WOOD_DARK)
    c.shape(rounded_rect_d(-80, -68, 160, 12, 3), P.WOOD_LIGHT, sw=2.2, light=None)
    c.shape(rounded_rect_d(-58, -150, 92, 82, 6), P.METAL, sw=2.4, light=(-3, -3), shade_k=0.85)
    for gx, gy, r, color in ((-30, -112, 20, P.YELLOW), (4, -96, 14, P.ORANGE), (18, -128, 11, P.TEAL)):
        teeth = "".join(f'<rect x="-3" y="{-r - 5}" width="6" height="8" transform="rotate({a})" fill="{color}" '
                        f'stroke="{INK}" stroke-width="1.2"/>' for a in range(0, 360, 40))
        c.add(f'<g transform="translate({gx},{gy})">{teeth}<circle r="{r}" fill="{color}" stroke="{INK}" '
              f'stroke-width="1.8"/><circle r="{r * 0.35}" fill="{P.METAL_DARK}" stroke="{INK}" '
              f'stroke-width="1.2"/></g>')
    c.add(sticky(-48, -150, P.YELLOW_PALE, -10, 0.7))
    c.add(sticky(30, -82, P.PINK_PALE, 8, 0.7))
    c.add(f'<circle cx="54" cy="-80" r="7" fill="{P.GREEN}" stroke="{INK}" stroke-width="1.6"/>')   # tests: green
    c.line("M54,-87 V-100 M48,-94 l12,0", 1.4, opacity=0.4)
    c.add(doodle_at("magnifier", 60, -68, 26))
    return _at(c, x, y, scale)


def flask_rack(x: float, y: float, scale: float = 1.0) -> str:
    """A table with test tubes and flasks, most of them green: the tests. 150 wide."""
    c = Canvas()
    c.line("M-66,0 V-56 M66,0 V-56", 5, P.WOOD_DARK)
    c.shape(rounded_rect_d(-74, -66, 148, 11, 3), P.WOOD_LIGHT, sw=2.2, light=None)
    c.shape("M-60,-66 V-96 H10 V-66 Z", P.WOOD, sw=2, light=None)
    for i, color in enumerate((P.GREEN, P.GREEN, P.RED, P.GREEN, P.GREEN)):
        tx = -52 + i * 13
        c.shape(f"M{tx - 4},-120 V-88 Q{tx},-82 {tx + 4},-88 V-120 Z", P.WHITE, sw=1.4, light=None)
        c.add(f'<path d="M{tx - 4},-104 V-88 Q{tx},-82 {tx + 4},-88 V-104 Z" fill="{color}" opacity=".85"/>')
    c.shape("M30,-66 L22,-82 V-100 H40 V-82 L48,-66 Z", lighten(P.GREEN, 0.3), sw=1.8, light=None)
    c.line("M28,-104 h12", 2.2)
    c.add(f'<circle cx="30" cy="-110" r="4" fill="{P.WHITE}" stroke="{INK}" stroke-width="1"/>'
          f'<circle cx="36" cy="-120" r="3" fill="{P.WHITE}" stroke="{INK}" stroke-width="1"/>')
    return _at(c, x, y, scale)


def chest(x: float, y: float, scale: float = 1.0, label: str = "") -> str:
    """An open chest of rolled-up decisions; 110 wide, 90 tall with its lid up."""
    c = Canvas()
    c.shape("M-50,-46 Q-50,-92 0,-92 Q50,-92 50,-46 Z", P.WOOD, sw=2.3, light=(-2, -2))
    c.line("M-50,-56 Q0,-62 50,-56", 2, P.METAL_DARK)
    for sx, sy, turn in ((-26, -52, -20), (-6, -58, -6), (14, -54, 10), (30, -50, 24)):
        c.add(f'<g transform="translate({sx},{sy}) rotate({turn})">'
              f'<rect x="-6" y="-14" width="12" height="28" rx="5" fill="{P.SCROLL}" stroke="{INK}" '
              f'stroke-width="1.6"/>'
              f'<path d="M-6,-2 H6" stroke="{P.RED}" stroke-width="2.4"/></g>')
    c.shape("M-50,0 V-46 H50 V0 Z", P.WOOD_DARK, sw=2.4, light=(-3, -2))
    c.line("M-50,-30 H50 M-34,0 V-46 M34,0 V-46", 2.4, P.METAL_DARK)
    c.shape(rounded_rect_d(-8, -40, 16, 14, 3), P.SUN, sw=1.6, light=None)
    if label:
        c.path(rounded_rect_d(-26, -24, 52, 18, 3), P.CREAM, 1.6)
        _label(c, 0, -10, label, 12)
    return _at(c, x, y, scale)


def round_window(x: float, y: float, r: float = 22) -> str:
    c = Canvas()
    c.shape(ellipse_d(0, 0, r + 6, r + 6), P.WOOD_DARK, sw=2.2, light=None)
    paint = c.gradient([(0, P.SKY_DEEP), (1, P.SKY)], 0, -r, 0, r)
    c.path(ellipse_d(0, 0, r, r), paint, 2)
    c.line(f"M{-r},0 H{r} M0,{-r} V{r}", 3, P.WOOD_DARK)
    return _at(c, x, y)


def red_thread(points: list[tuple[float, float]]) -> str:
    """A red thread pinned from point to point: a link from one note to the next."""
    c = Canvas()
    d = f"M{n(points[0][0])},{n(points[0][1])}" + "".join(
        f" Q{n((a[0] + b[0]) / 2)},{n(max(a[1], b[1]) + 10)} "
        f"{n(b[0])},{n(b[1])}" for a, b in zip(points, points[1:], strict=False))
    c.line(d, 2.4, P.RED)
    for px, py in points[1:-1]:
        c.add(f'<circle cx="{n(px)}" cy="{n(py)}" r="3.6" fill="{P.RED}" stroke="{INK}" stroke-width="1.2"/>')
    return c.render()


def wall_lamp(x: float, y: float, scale: float = 1.0) -> str:
    c = Canvas()
    c.line("M0,0 V18", 1.6)
    c.shape("M-16,34 L-8,18 H8 L16,34 Z", P.YELLOW, sw=1.8, light=None)
    c.add(f'<path d="M-16,34 L-34,90 H34 L16,34 Z" fill="{P.SUN}" opacity=".18"/>')
    return _at(c, x, y, scale)


def fence_row(x0: float, x1: float, y: float, color: str = P.CARD) -> str:
    c = Canvas()
    c.shape(f"M{n(x0)},{n(y - 34)} H{n(x1)} V{n(y - 27)} H{n(x0)} Z", color, sw=1.8, light=None)
    c.shape(f"M{n(x0)},{n(y - 16)} H{n(x1)} V{n(y - 9)} H{n(x0)} Z", color, sw=1.8, light=None)
    x = x0 + 4
    while x < x1 - 8:
        c.shape(f"M{n(x)},{n(y)} V{n(y - 40)} L{n(x + 5)},{n(y - 47)} L{n(x + 10)},{n(y - 40)} V{n(y)} "
            f"Z", color, sw=1.8,
                light=(-1, 0))
        x += 18
    return c.render()


def envelope_open(x: float, y: float, scale: float = 1.0) -> str:
    """An opened envelope lying on the ground."""
    c = Canvas()
    c.shape("M-24,0 V-26 H24 V0 Z", P.CARD, sw=1.8, light=None)
    c.shape("M-24,-26 L0,-44 L24,-26 Z", P.PAPER_SHADE, sw=1.8, light=None)
    c.line("M-24,0 L0,-14 L24,0", 1.2, opacity=0.6)
    c.add(f'<circle cx="0" cy="-20" r="4" fill="{P.RED}" stroke="{INK}" stroke-width="1.2"/>')
    return _at(c, x, y, scale)


def apple_tree(x: float, y: float, scale: float = 1.0, seed: int = 0) -> str:
    """A round tree hung with red apples, a birdhouse on its trunk; 170 wide, 180 tall at scale 1."""
    rnd = random.Random(seed)
    c = Canvas()
    c.add(tree(0, 0, 1.0, "oak"))
    for _ in range(9):
        ax, ay = rnd.uniform(-50, 54), rnd.uniform(-140, -86)
        c.add(f'<circle cx="{n(ax)}" cy="{n(ay)}" r="5" fill="{P.RED}" stroke="{INK}" stroke-width="1.4"/>')
        c.add(f'<path d="M{n(ax - 1.5)},{n(ay - 2.5)} q-1,2 0,3" stroke="{P.WHITE}" stroke-width="1.2" fill="none"/>')
    c.shape("M-10,-64 L0,-74 L10,-64 V-48 H-10 Z", P.YELLOW, sw=1.8, light=None)
    c.add(f'<circle cx="0" cy="-58" r="3.4" fill="{P.DARK_BROWN}"/>')
    c.shape("M-13,-62 L0,-76 L13,-62 Z", P.RED, sw=1.6, light=None)
    return _at(c, x, y, scale)

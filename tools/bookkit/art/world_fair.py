"""The fair: the world of chapter 2 (which tool to take).

A good agent stands on three things - the model, the harness round it and the repository - and the reader picks
the first two. At the fair the model is an engine and the harness is the go-kart it goes into: the heroes walk
along the fair's lane from tent to tent, and the camera goes with them:

1. engines  a stall of engines on its counter, big and small; the agent studies them; then the old token pump
            fills the big one through its hose, the counter rolling, the caterpillar counting the cost;
2. carts    the karts the engine goes into, under a striped pavilion - a plain one and a tooled one (toolbox,
            mirror, headlight, aerial); then a hoist lowers the engine into the tooled kart while the agent guides it;
3. drive    the test drive: the kart races round the cones, the agent steering it by remote and the cat timing it;
            then a cone is knocked flying and the caterpillar writes it down;
4. board    the results: the scoreboard of how many tasks each engine solved, the cat explains it; then the engines
            on the winners' podium;
5. home     running one at home: the caterpillar wheels a big graphics card in a barrow; then the little engine on
            the home workbench coughs and smokes;
6. choice   the agent pushes the chosen kart, engine in and tools on, out through the fair's gate - while the
            sparrow is after the big red button (he gets to press it only in the last chapter).

No name boards in the frames: every thing says what it is by itself; only the finale names its stations. Every
frame stands in the fair: striped tents along the horizon, the big wheel, garlands of flags and lamps on poles in a
tall frame. Blue leads, the chapter's colour. It draws with the shared kit (`world_kit.py`) and keeps its two
rules: containers and ports.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten, mix
from . import handheld, props, sets
from .footers import Strip
from .ink import INK, Canvas, ellipse_d, lettering, n, rounded_rect_d
from .openers import CLEAR_MM, H, OPENERS, W, Box, Stage
from .world_kit import (GAP_MIN, SIZE, Pen, Room, connect, hide, ledger, letter, motion, port, room, stash_along,
                        tag_size, wrap)
from .world_kitchen import _box, _fit_tall, extra, flier, perch, red_button, smoke_cloud
from .world_base import Station, world

FAIR = world("fair", opener="fairground")

_at = sets._at

PAVE_A = mix(P.SAND, P.WOOD_LIGHT, 0.3)    # the plaza's pavers, the usual tone ...
PAVE_B = mix(P.SAND, P.TERRACOTTA, 0.3)    # ... and the warmer one among them
JOINT = darken(PAVE_A, 0.72)               # the joints between them
SOIL = mix(P.WOOD_DARK, P.DARK_BROWN, 0.5)  # a flower bed's earth
# The fair's tents, blue first - the chapter's colour - then the others in turn: (main, stripe).
TENTS = ((P.BLUE, P.WHITE), (P.YELLOW, P.BLUE), (P.RED, P.WHITE), (P.BLUE, P.YELLOW), (P.GREEN, P.WHITE),
         (P.WHITE, P.BLUE))


class Lane(Room):
    """A stretch of the fair's lane in a frame: the room, plus where feet stand and how high a stall's counter is."""

    def __init__(self, s: Strip) -> None:
        super().__init__(s)
        self.ceil = 0.0                                   # under the open sky: up to the frame's top
        self.wall = self.floor
        self.feet = s.feet(s.x(0.5))
        self.counter = self.feet - s.tall * 0.42          # waist-high to the professor


def lane(s: Strip) -> Lane:
    return room(s, Lane)


def _ink(w: float) -> float:
    return max(1.2, w)


# ============================================================================ the fair's buildings
def tent_art(c: Canvas, x: float, foot: float, w: float, h: float, main: str, stripe: str = P.WHITE,
             flag: str = P.YELLOW, door: bool = True) -> None:
    """A striped fair tent, its foot's middle at (x, foot), `w` wide and `h` tall to the roof's peak: striped
    walls, a peaked roof of coloured wedges with a scalloped valance, its pennant on the pole and - `door` - the
    flaps tied back from a dark doorway."""
    lw = _ink(w * 0.012)
    eave, top = foot - h * 0.5, foot - h
    hw = w / 2
    walls = f"M{n(x - hw)},{n(eave)} H{n(x + hw)} V{n(foot)} H{n(x - hw)} Z"
    clip = c.shape(walls, stripe, sw=0, light=None, clip=True)
    step = w / 8
    bands = " ".join(f"M{n(x - hw + i * step)},{n(eave)} h{n(step / 2)} V{n(foot)} h{n(-step / 2)} Z"
                     for i in range(8))
    c.add(f'<g clip-path="url(#{clip})"><path d="{bands}" fill="{main}"/></g>')
    c.path(walls, "none", lw)
    if door:
        dw = w * 0.2
        c.shape(f"M{n(x - dw)},{n(foot)} V{n(eave + h * 0.14)} Q{n(x)},{n(eave + h * 0.04)} {n(x + dw)},"
                f"{n(eave + h * 0.14)} V{n(foot)} Z", darken(main, 0.4), sw=lw, light=None)
        for way in (-1, 1):                                # the flaps, tied back
            c.shape(f"M{n(x + way * dw * 0.2)},{n(eave + h * 0.02)} L{n(x + way * dw * 1.35)},{n(eave + h * 0.02)} "
                    f"L{n(x + way * dw * 1.35)},{n(foot)} Q{n(x + way * dw * 1.0)},{n(eave + h * 0.3)} "
                    f"{n(x + way * dw * 0.2)},{n(eave + h * 0.02)} Z", stripe, sw=lw, light=None)
    roof = (f"M{n(x - hw - w * 0.06)},{n(eave)} Q{n(x - hw * 0.4)},{n(eave - (eave - top) * 0.45)} {n(x)},{n(top)} "
            f"Q{n(x + hw * 0.4)},{n(eave - (eave - top) * 0.45)} {n(x + hw + w * 0.06)},{n(eave)} Z")
    clip = c.shape(roof, stripe, sw=0, light=None, clip=True)
    wedges = []
    count = 8
    for i in range(0, count, 2):
        a0 = x - hw - w * 0.1 + (w * 1.2) * i / count
        a1 = x - hw - w * 0.1 + (w * 1.2) * (i + 1) / count
        wedges.append(f"M{n(x)},{n(top - 2)} L{n(a0)},{n(eave + 2)} L{n(a1)},{n(eave + 2)} Z")
    c.add(f'<g clip-path="url(#{clip})"><path d="{" ".join(wedges)}" fill="{main}"/></g>')
    c.path(roof, "none", lw)
    _scallops(c, x - hw - w * 0.06, x + hw + w * 0.06, eave, max(5.0, h * 0.06), main, stripe, lw)
    pole = h * 0.16
    c.line(f"M{n(x)},{n(top)} V{n(top - pole)}", lw * 1.2, P.WOOD_DARK)
    c.shape(f"M{n(x)},{n(top - pole)} l{n(pole * 0.7)},{n(pole * 0.22)} l{n(-pole * 0.7)},{n(pole * 0.22)} Z", flag,
            sw=lw * 0.8, light=None)


def _scallops(c: Canvas, x0: float, x1: float, y: float, depth: float, a: str, b: str, lw: float) -> None:
    """A scalloped valance hanging from y between x0 and x1, the scallops in turn a and b."""
    count = max(3, round((x1 - x0) / (depth * 2.2)))
    step = (x1 - x0) / count
    for i in range(count):
        s0 = x0 + i * step
        c.shape(f"M{n(s0)},{n(y)} Q{n(s0 + step / 2)},{n(y + depth * 1.6)} {n(s0 + step)},{n(y)} Z",
                a if i % 2 == 0 else b, sw=lw * 0.9, light=None)


def pavilion(c: Canvas, x0: float, x1: float, eave: float, foot: float, main: str, stripe: str = P.WHITE) -> None:
    """An open pavilion over a station: a striped peaked roof whose scalloped edge hangs at `eave`, on two poles
    - nothing between them, so whatever stands under it is seen whole."""
    x0, x1 = min(x0, x1), max(x0, x1)                    # on a mirrored page the ends come the other way round
    w = x1 - x0
    lw = _ink(w * 0.006)
    rise = min(w * 0.14, 60.0)
    c.add(f'<ellipse cx="{n((x0 + x1) / 2)}" cy="{n(foot + 2)}" rx="{n(w * 0.52)}" ry="{n(max(4.0, w * 0.025))}" '
          f'fill="{INK}" fill-opacity=".12"/>')                    # its shadow on the ground
    for px in (x0 + 4, x1 - 4):                           # its two corner poles, nothing in the middle
        c.shape(rounded_rect_d(px - 2.5, eave - 2, 5, foot - eave + 2, 2), P.WOOD, sw=lw, light=None)
    roof = (f"M{n(x0 - 10)},{n(eave)} L{n(x0 + w * 0.12)},{n(eave - rise)} H{n(x1 - w * 0.12)} L{n(x1 + 10)},"
            f"{n(eave)} Z")
    clip = c.shape(roof, stripe, sw=0, light=None, clip=True)
    step = max(18.0, w / 14)
    stripes, sx = [], x0 - 12
    while sx < x1 + 12:
        stripes.append(f"M{n(sx)},{n(eave + 2)} L{n(sx + step * 0.25)},{n(eave - rise - 2)} h{n(step * 0.5)} "
                       f"L{n(sx + step * 0.5)},{n(eave + 2)} Z")
        sx += step
    c.add(f'<g clip-path="url(#{clip})"><path d="{" ".join(stripes)}" fill="{main}"/></g>')
    c.path(roof, "none", lw * 1.4)
    _scallops(c, x0 - 10, x1 + 10, eave, max(5.0, rise * 0.22), main, stripe, lw * 1.4)
    for fx in (x0 + w * 0.12, x1 - w * 0.12):             # a pennant at each top corner
        c.line(f"M{n(fx)},{n(eave - rise)} v{n(-rise * 0.4)}", lw, P.WOOD_DARK)
        c.shape(f"M{n(fx)},{n(eave - rise * 1.4)} l{n(rise * 0.3)},{n(rise * 0.1)} l{n(-rise * 0.3)},{n(rise * 0.1)} Z",
                P.YELLOW, sw=lw, light=None)


def garland(c: Canvas, x0: float, y0: float, x1: float, y1: float, sag: float, size: float, seed: int = 0,
            lamps: bool = False) -> None:
    """A garland hung between two points: triangular flags in the fair's colours - or, `lamps`, a string of bulbs
    glowing yellow and white."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag * 2
    lw = _ink(size * 0.08)
    c.line(f"M{n(x0)},{n(y0)} Q{n(mx)},{n(my)} {n(x1)},{n(y1)}", lw)
    count = max(3, int(math.hypot(x1 - x0, y1 - y0) / (size * 1.3)))
    colors = (P.BLUE, P.YELLOW, P.RED, P.WHITE, P.GREEN, P.BLUE)
    for i in range(1, count):
        t = i / count
        px = (1 - t) ** 2 * x0 + 2 * t * (1 - t) * mx + t * t * x1
        py = (1 - t) ** 2 * y0 + 2 * t * (1 - t) * my + t * t * y1
        if lamps:
            c.add(f'<rect x="{n(px - size * 0.12)}" y="{n(py)}" width="{n(size * 0.24)}" height="{n(size * 0.2)}" '
                  f'fill="{P.METAL_DARK}"/>')
            glow = (P.SUN, P.YELLOW_PALE)[(i + seed) % 2]
            c.add(f'<circle cx="{n(px)}" cy="{n(py + size * 0.42)}" r="{n(size * 0.24)}" fill="{glow}" '
                  f'stroke="{INK}" stroke-width="{n(lw * 0.8)}"/>')
        else:
            c.shape(f"M{n(px - size * 0.35)},{n(py)} L{n(px + size * 0.35)},{n(py)} L{n(px)},{n(py + size * 0.8)} Z",
                    colors[(i + seed) % len(colors)], sw=lw * 0.8, light=None)


def pole(c: Canvas, x: float, top: float, foot: float, w: float) -> None:
    """A garland's wooden pole, a ball on its top."""
    c.shape(rounded_rect_d(x - w / 2, top, w, foot - top, w / 2), P.WOOD, sw=_ink(w * 0.3), light=None)
    c.add(f'<circle cx="{n(x)}" cy="{n(top)}" r="{n(w * 0.9)}" fill="{P.RED}" stroke="{INK}" '
          f'stroke-width="{n(_ink(w * 0.3))}"/>')


def wheel_art(c: Canvas, x: float, foot: float, r: float, turn: float = 0, gondolas: bool = True) -> None:
    """The fair's big wheel standing at (x, foot), `r` its radius: two A-frame legs on a base, a blue rim with its
    inner ring and spokes, eight coloured gondolas hanging level from the rim, the hub."""
    cy = foot - r * 1.2
    lw = _ink(r * 0.016)
    for dx in (-1, 1):                                    # the legs, steel
        d = f"M{n(x + dx * r * 0.7)},{n(foot)} L{n(x)},{n(cy)}"
        c.line(d, r * 0.07 + lw * 2, INK)
        c.line(d, r * 0.07, P.METAL_LIGHT)
    c.line(f"M{n(x - r * 0.42)},{n(foot - r * 0.48)} H{n(x + r * 0.42)}", r * 0.035 + lw * 2, INK)
    c.line(f"M{n(x - r * 0.42)},{n(foot - r * 0.48)} H{n(x + r * 0.42)}", r * 0.035, P.METAL_LIGHT)
    spokes = " ".join(f"M{n(x)},{n(cy)} L{n(x + math.cos(math.radians(turn + i * 22.5)) * r)},"
                      f"{n(cy + math.sin(math.radians(turn + i * 22.5)) * r)}" for i in range(16))
    c.line(spokes, max(1.0, r * 0.012), P.METAL_DARK)
    for rr, wid, color in ((r, r * 0.06, P.BLUE), (r * 0.82, r * 0.025, P.WHITE)):
        c.add(f'<circle cx="{n(x)}" cy="{n(cy)}" r="{n(rr)}" fill="none" stroke="{INK}" '
              f'stroke-width="{n(wid + lw * 2)}"/><circle cx="{n(x)}" cy="{n(cy)}" r="{n(rr)}" fill="none" '
              f'stroke="{color}" stroke-width="{n(wid)}"/>')
    colors = (P.RED, P.YELLOW, P.BLUE, P.GREEN, P.ORANGE, P.PINK, P.BLUE, P.YELLOW)
    g = r * 0.13
    for i in range(8 if gondolas else 0):
        a = math.radians(turn + i * 45)
        gx, gy = x + math.cos(a) * r, cy + math.sin(a) * r
        c.line(f"M{n(gx)},{n(gy)} v{n(g * 0.5)}", lw, INK)
        c.shape(rounded_rect_d(gx - g, gy + g * 0.5, g * 2, g * 1.5, g * 0.35), colors[i], sw=lw, light=None)
        c.add(f'<rect x="{n(gx - g * 0.65)}" y="{n(gy + g * 0.75)}" width="{n(g * 1.3)}" height="{n(g * 0.55)}" '
              f'rx="{n(g * 0.15)}" fill="{P.WHITE}" stroke="{INK}" stroke-width="{n(lw * 0.7)}"/>')
    c.add(f'<circle cx="{n(x)}" cy="{n(cy)}" r="{n(r * 0.09)}" fill="{P.YELLOW}" stroke="{INK}" '
          f'stroke-width="{n(lw)}"/>')
    c.shape(rounded_rect_d(x - r * 0.8, foot - r * 0.06, r * 1.6, r * 0.08, 2), P.WOOD, sw=lw, light=None)


# ============================================================================ the place behind every frame
def mid(s: Strip) -> bool:
    """A mid-height strip, about 220 high: the tallest character there, the professor, is left out where the beat
    does not need him, so the others can stand taller."""
    return 200 <= s.h < 300


def zoom(s: Strip) -> None:
    """The fair's camera, close: the station and its cast fill the frame's height, but nothing is ever cut by the
    frame (nothing may be cut at the bottom, anywhere) - a band of paving shows
    under every pair of feet, at least an eighth of the frame, and every head stays under the top. A strip shows
    fewer things, each whole and smaller, rather than a close-up cut at the knees."""
    s.shot = s.seed % 2                                   # every other page: a second camera
    s.ground = max(26.0, s.h * (0.22 if s.h < 200 else 0.19))
    s.base = s.h - s.ground
    feet = s.h - max(16.0, s.h * 0.14)                     # the feet line: the paving shows under it
    s.feet = lambda x, nearer=0, feet=feet: feet          # noqa: ARG005 - one floor line across the frame
    s.tall = min((feet - 6) / (1.12 if s.h < 300 else 1.18), 340.0)
    if s.shot:                                            # every other page the camera stands a step further back
        s.tall *= 0.86
    s.unit = s.tall / 137


def backdrop(s: Strip, index: int) -> None:
    """The fair behind a station: a summer sky and far hills, the grass and the trodden lane. The far fair - its
    tents, its big wheel, its garlands - is put in by `scenery` once the station has placed its cast and things, so
    that nothing of it stands behind a head or peeks out from behind anyone."""
    ledger(s)
    zoom(s)
    c = s.back
    sets.sky(c, mix(P.SKY, P.BLUE, 0.12), P.SKY_LOW, s.base + 10, W)
    if s.h >= 190:
        sets.hills(c, s.base + 6, W, (P.HILL_FAR, P.HILL_NEAR), seed=index + 3)
    s.fair_slot = (index, len(c.parts))                 # where the far fair goes: behind everything of the station
    s.fair_kerb = fairground(c, s.base, s.h, s.unit, seed=index + 7)
    s.fair_floor = len(c.parts)                           # where the things lying on the ground go


def scenery(s: Strip) -> None:
    """The far fair behind a frame, drawn into the slot the backdrop kept: the big wheel in a taller frame and the
    striped tents along the horizon, each only where it clears every character and thing with air to spare; in a
    tall frame a garland of flags and one of lamps between two poles - only where they hang below the frame's top
    veil and over every head."""
    index, at = s.fair_slot
    c = Canvas()
    taken = [(b.left, b.top, b.right, b.bottom) for b in s.boxes] + list(s.reserved) + getattr(s, "fair_keep", [])

    def clear(box: tuple, air: float = 8) -> bool:
        return all(box[2] + air <= t[0] or t[2] + air <= box[0] or box[3] + air <= t[1] or t[3] + air <= box[1]
                   for t in taken)

    foot = s.base + 2
    if s.h >= 260:
        r = min(s.base * 0.27, 100.0)
        prefer = (0.84, 0.16, 0.78, 0.22, 0.82, 0.14)[index % 6]
        for f in sorted((i / 20 for i in range(1, 20)), key=lambda f: abs(f - prefer)):
            x = W * f
            box = (x - r * 1.15, foot - r * 2.35, x + r * 1.15, foot)
            if box[1] > 6 and box[0] > 6 and box[2] < W - 6 and clear(box):
                wheel_art(c, x, foot, r, index * 9.0)
                taken.append(box)
                break
    th = min(s.base * 0.36, 96.0)                         # the far row of tents along the horizon - not in a strip:
    x, i = 10.0 + (index * 37) % 40, index                # there they would be a row of tiny toys
    while x < W - 10 and s.h >= 260:
        size = 0.75 + 0.25 * ((i * 7) % 3) / 2
        w, h = th * 0.95 * size, th * size
        box = (x, foot - h * 1.16, x + w, foot - 3)
        if box[2] < W - 4 and clear(box, 4):
            main, stripe = TENTS[i % len(TENTS)]
            tent_art(c, x + w / 2, foot, w, h, mix(main, P.SKY_LOW, 0.25), mix(stripe, P.SKY_LOW, 0.2), door=False)
            taken.append(box)
            x += w + th * 1.1                             # a few, with grass between them
            i += 1
        else:
            x += 12
    reach = min(s.base * 0.6, 150.0)                      # the veil over the frame's top
    heads = min([b.top for b in s.boxes] or [s.base])
    top = reach + 14
    drop = 44 * s.unit
    if s.h >= 300 and top + drop < heads - 10:
        pw = max(5.0, 6 * s.unit)
        for px in (12.0, W - 12.0):
            pole(c, px, top - 8, s.base + 4, pw)
        sag = 8 * s.unit
        garland(c, 12, top, W - 12, top, sag, 18 * s.unit, seed=index)
        garland(c, 12, top + 18 * s.unit, W - 12, top + 18 * s.unit, sag * 0.8, 15 * s.unit, seed=index, lamps=True)
    floor = Canvas()
    r, k = lane(s), s.unit
    taken = [(b.left, b.top, b.right, b.bottom) for b in s.boxes] + list(s.reserved) + getattr(s, "fair_keep", [])
    # (the near things only mind the cast, the things and the stalls - the far fair stands behind them)
    kerb_y = s.fair_kerb
    x, n_ = 8.0, 0                                        # hedges and flower beds along the verge, in the gaps
    while x < W - 8 and s.h >= 200:                       # (a low strip would show them as mere green bars)
        hedge_w, bed_w = 70 * k, 80 * k
        if n_ % 2 == 0:
            box = (x, kerb_y - 16 * k, x + hedge_w, kerb_y)
            if box[1] > 2 and clear(box, 4):
                hedge(floor, x, kerb_y, hedge_w, 15 * k)
                taken.append(box)
                x += hedge_w + 10 * k
                n_ += 1
                continue
        else:
            box = (x, kerb_y - 24 * k, x + bed_w, kerb_y + 3 * k)
            if box[1] > 2 and clear(box, 4):
                flowerbed(floor, x, kerb_y - 1, bed_w, k, seed=index + n_)
                taken.append(box)
                x += bed_w + 10 * k
                n_ += 1
                continue
        x += 14
        n_ += 1 if x % 3 < 1 else 0                       # now and then try the other kind
    s.back.parts.insert(s.fair_floor, floor.render())
    s.back.parts.insert(at, c.render())


def _keep(s: Strip, box: tuple) -> None:
    """Mark a stretch the station drew on the ground or in the backdrop (a stall, the track), so the far fair and
    the things lying on the ground keep off it."""
    if not hasattr(s, "fair_keep"):
        s.fair_keep = []
    s.fair_keep.append(box)


def turn(s: Strip) -> None:
    """The second page of a beat is seen from the other side, so two pages in a row never show one picture:
    every place across the frame is mirrored and every character faces the other way; the things themselves are not
    mirrored."""
    if s.shot:
        lo, hi = s.lo, s.hi
        s.x = lambda frac: hi - (hi - lo) * frac
        s.flipx = True


def _framed(draw, turned: tuple[str, ...] = ()):
    """A station drawn, then the far fair put in round it. The `turned` beats are seen from the other side on every
    other page; the others change their camera themselves (`s.shot`)."""
    def run(s: Strip, beat: str) -> None:
        if beat in turned:
            turn(s)
        draw(s, beat)
        scenery(s)
    return run


def fairground(c: Canvas, top: float, bottom: float, k: float, seed: int = 0) -> float:
    """The fair's floor from the horizon `top` down to `bottom`: a strip of grass verge along the horizon, a low
    stone kerb, and the plaza in front of it - rectangular pavers in two warm tones laid in rows with their joints,
    a little larger towards the front. Every part a clear shape, no stipple. Returns the kerb's top."""
    edge = (f"M-6,{n(top)} Q{n(W * 0.25)},{n(top - 6)} {n(W * 0.5)},{n(top + 2)} T{W + 6},{n(top - 2)} "
            f"V{n(bottom + 6)} H-6 Z")
    c.shape(edge, P.GRASS, sw=2, light=None)
    kerb_y = top + 1                                      # the kerb right at the horizon: feet stand on the paving
    paving(c, -6, W + 6, kerb_y + 4 * k, bottom + 4, k, seed)
    kerb(c, -6, W + 6, kerb_y, k)
    return kerb_y


def paving(c: Canvas, x0: float, x1: float, y0: float, y1: float, k: float, seed: int = 0,
           tones: tuple[str, str] = (PAVE_A, PAVE_B)) -> None:
    """A paved floor in the box, seen from a little above: rows of rectangular pavers in running bond, two warm
    tones, the joints showing between them; the rows and the pavers grow towards the front and their side joints
    run towards a point far behind the horizon, so the floor lies flat."""
    rnd = random.Random(seed)
    c.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" fill="{JOINT}"/>')
    depth = max(1.0, y1 - y0)
    vy = y0 - depth * 1.3                                 # where the side joints would meet
    mid = (x0 + x1) / 2
    near = 15 * k                                         # a row's height at the front

    def scale(y: float) -> float:
        return (y - vy) / (y1 - vy)

    gap = max(0.7, 1.0 * k)
    rects, y, row = [], y0, 0
    while y < y1:
        h = max(3.0, near * scale(y))
        ya, yb = y + gap, min(y1, y + h) - gap
        sa, sb = scale(ya), scale(yb)
        w = near * 2.4                                    # a paver's width at the front, in floor units
        u = -(w / 2 if row % 2 else 0) - rnd.uniform(0, w * 0.2)
        left = (x0 - mid) / sa - w
        u += math.floor(left / w) * w
        while mid + u * sb < x1 + w:
            ua, ub = u + gap / sb, u + w - gap / sb
            pts = [(mid + ua * sa, ya), (mid + ub * sa, ya), (mid + ub * sb, yb), (mid + ua * sb, yb)]
            tone = tones[1] if rnd.random() < 0.3 else tones[0]
            rects.append(f'<path d="M{" L".join(f"{n(px)},{n(py)}" for px, py in pts)} Z" fill="{tone}"/>')
            u += w
        y += h
        row += 1
    c.add("".join(rects))


def kerb(c: Canvas, x0: float, x1: float, y: float, k: float) -> None:
    """A low stone kerb along y from x0 to x1: a band of grey blocks with their joints."""
    h = max(3.0, 4.5 * k)
    c.add(f'<rect x="{n(x0)}" y="{n(y)}" width="{n(x1 - x0)}" height="{n(h)}" fill="{P.STONE}" stroke="{INK}" '
          f'stroke-width="1.4"/>')
    step = max(12.0, 22 * k)
    c.line(" ".join(f"M{n(x)},{n(y)} v{n(h)}" for x in [x0 + step * i for i in range(1, int((x1 - x0) / step) + 1)]),
           1, darken(P.STONE, 0.7))


def hedge(c: Canvas, x: float, y: float, w: float, h: float) -> None:
    """A low clipped hedge standing on y from x to x + w: a row of round bushes grown together - a scalloped top a
    reader takes for leaves at once (a flat rounded block read as a green bar) - lighter where the sun is on it."""
    bumps = max(2, round(w / (h * 1.1)))
    r = w / bumps / 2
    top = y - h + r * 0.6
    d = [f"M{n(x)},{n(y)} V{n(top + r * 0.4)}"]
    for i in range(bumps):
        d.append(f"A{n(r)},{n(r * 0.8)} 0 0 1 {n(x + 2 * r * (i + 1))},{n(top + r * 0.4)}")
    d.append(f"V{n(y)} Z")
    c.shape(" ".join(d), mix(P.LEAF_DARK, P.GRASS_DARK, 0.4), sw=1.6, light=None)
    for i in range(bumps):                                # the sunlit crown of each bush
        cx = x + r * (2 * i + 1)
        c.add(f'<path d="M{n(cx - r * 0.55)},{n(top + r * 0.1)} Q{n(cx)},{n(top - r * 0.35)} {n(cx + r * 0.45)},'
              f'{n(top)}" fill="none" stroke="{mix(P.LEAF, P.GRASS, 0.4)}" stroke-width="{n(max(1.2, r * 0.3))}" '
              f'stroke-linecap="round"/>')


def sunflower(x: float, y: float, scale: float = 1.0) -> str:
    """A sunflower 40 tall: a stem with two leaves, a ring of yellow petals round a brown middle."""
    c = Canvas()
    c.line("M0,0 q2,-18 0,-34", 2, P.LEAF_DARK)
    c.path("M0,-12 q10,-6 12,2 q-8,4 -12,-2 Z", P.LEAF, 1.4)
    c.path("M0,-20 q-10,-6 -12,2 q8,4 12,-2 Z", P.LEAF, 1.4)
    for a in range(0, 360, 30):
        c.add(f'<ellipse cx="0" cy="-6" rx="2.6" ry="6" transform="translate(0,-38) rotate({a})" '
              f'fill="{P.SUN}" stroke="{INK}" stroke-width="1"/>')
    c.add(f'<circle cx="0" cy="-38" r="5" fill="{P.DARK_BROWN}" stroke="{INK}" stroke-width="1.2"/>')
    return sets._at(c, x, y, scale)


def flowerbed(c: Canvas, x: float, y: float, w: float, k: float, seed: int = 0) -> None:
    """A flower bed on the verge from x, its foot on y, `w` wide: a low bed of dark soil with a brick edge and a
    row of different flowers - tulips, daisies, a sunflower."""
    c.shape(f"M{n(x)},{n(y)} Q{n(x + w / 2)},{n(y - 7 * k)} {n(x + w)},{n(y)} Q{n(x + w / 2)},{n(y + 5 * k)} "
            f"{n(x)},{n(y)} Z", SOIL, sw=1.4, light=None)
    kinds = ("tulip", "daisy", "sun", "tulip", "daisy")
    colors = (P.RED, P.WHITE, None, P.YELLOW, P.PINK, P.BLUE)
    count = max(2, int(w / (16 * k)))
    for i in range(count):
        fx = x + w * (i + 0.5) / count
        kind = kinds[(i + seed) % len(kinds)]
        if kind == "sun":
            c.add(sunflower(fx, y - 1, 0.5 * k))
        elif kind == "tulip":
            c.add(props.tulip(fx, y - 1, 0.42 * k, colors[(i + seed) % 2 * 3]))
        else:
            c.add(props.daisy(fx, y - 1, 0.42 * k, colors[(i + seed) % 3 + 1] or P.WHITE))


def track_kerbs(c: Canvas, x0: float, x1: float, y: float, k: float) -> None:
    """The red-and-white kerb stones along a circuit's edge, a band at y from x0 to x1."""
    h = max(3.0, 5 * k)
    step = max(8.0, 14 * k)
    c.add(f'<rect x="{n(x0)}" y="{n(y - h / 2)}" width="{n(x1 - x0)}" height="{n(h)}" fill="{P.WHITE}" '
          f'stroke="{INK}" stroke-width="1.2"/>')
    c.add("".join(f'<path d="M{n(x)},{n(y + h / 2)} l{n(step * 0.3)},{n(-h)} h{n(step * 0.5)} '
                  f'l{n(-step * 0.3)},{n(h)} Z" fill="{P.RED}"/>'
                  for x in [x0 + step * i for i in range(int((x1 - x0) / step))]))


def fence(c: Canvas, x0: float, x1: float, y: float, k: float) -> None:
    """A low white fence along y: posts and two rails."""
    h = 16 * k
    step = max(14.0, 26 * k)
    c.line(" ".join(f"M{n(x)},{n(y)} v{n(-h)}" for x in [x0 + step * i for i in range(int((x1 - x0) / step) + 1)]),
           max(2.0, 3 * k), INK)
    c.line(" ".join(f"M{n(x)},{n(y)} v{n(-h)}" for x in [x0 + step * i for i in range(int((x1 - x0) / step) + 1)]),
           max(1.0, 1.6 * k), P.WHITE)
    for ry in (y - h * 0.4, y - h * 0.85):
        c.line(f"M{n(x0)},{n(ry)} H{n(x1)}", max(2.4, 3.4 * k), INK)
        c.line(f"M{n(x0)},{n(ry)} H{n(x1)}", max(1.2, 2 * k), P.WHITE)


def boardwalk(c: Canvas, x0: float, x1: float, y: float, depth: float, k: float) -> None:
    """Wooden planks laid flat in front of a stall from x0 to x1, `depth` deep from y, the awning's shadow along
    their back edge."""
    c.shape(rounded_rect_d(x0, y, x1 - x0, depth, 2), P.WOOD_LIGHT, sw=1.6, light=None)
    step = max(10.0, 18 * k)
    c.line(" ".join(f"M{n(x)},{n(y)} v{n(depth)}" for x in [x0 + step * i for i in range(1, int((x1 - x0) / step))]),
           1, P.WOOD_DARK, 0.8)
    c.add(f'<rect x="{n(x0)}" y="{n(y)}" width="{n(x1 - x0)}" height="{n(depth * 0.45)}" fill="{INK}" '
          f'fill-opacity=".14"/>')


def stall_back(c: Canvas, x0: float, x1: float, top: float, counter: float, k: float) -> None:
    """A stall's back wall behind its counter, from `top` down to the counter: wooden planks, a pegboard with
    spanners, a belt, spark plugs and a coil of hose hanging on it, a shelf with oil cans and boxes of parts, a lamp
    over it - calm and darker than the counter, so the engines on the counter read first."""
    if counter - top < 24 * k:
        return
    wood = mix(P.WOOD_PALE, P.WOOD, 0.35)
    c.add(f'<rect x="{n(x0)}" y="{n(top)}" width="{n(x1 - x0)}" height="{n(counter - top)}" fill="{wood}"/>')
    seams = [x0 + i * 22 * k for i in range(1, int((x1 - x0) / (22 * k)) + 1)]
    c.line(" ".join(f"M{n(x)},{n(top)} V{n(counter)}" for x in seams), 1, darken(wood, 0.8))
    h = counter - top
    bw = min((x1 - x0) * 0.44, 150 * k)                    # the pegboard on the left
    bx, by, bh = x0 + 10 * k, top + h * 0.12, h * 0.46
    c.shape(rounded_rect_d(bx, by, bw, bh, 2), mix(P.WOOD_LIGHT, P.CARD, 0.4), sw=1.2, light=None)
    hooks = [bx + bw * f for f in (0.14, 0.34, 0.56, 0.8)]
    c.line(" ".join(f"M{n(hx)},{n(by + 5 * k)} v{n(3 * k)}" for hx in hooks), 1, P.METAL_DARK)
    s = k
    c.add(f'<path d="M{n(hooks[0])},{n(by + 8 * s)} v{n(bh * 0.55)}" stroke="{P.METAL_DARK}" '
          f'stroke-width="{n(3 * s)}" stroke-linecap="round"/>')                         # a spanner
    c.add(f'<circle cx="{n(hooks[0])}" cy="{n(by + 8 * s + bh * 0.55)}" r="{n(4 * s)}" fill="none" '
          f'stroke="{P.METAL_DARK}" stroke-width="{n(2.4 * s)}"/>')
    c.add(f'<ellipse cx="{n(hooks[1])}" cy="{n(by + 8 * s + bh * 0.25)}" rx="{n(9 * s)}" ry="{n(bh * 0.25)}" '
          f'fill="none" stroke="{P.CHARCOAL}" stroke-width="{n(3 * s)}"/>')               # a belt
    for i in range(3):                                                                   # spark plugs
        px = hooks[2] - 6 * s + i * 6 * s
        c.shape(rounded_rect_d(px - 2 * s, by + 10 * s, 4 * s, 10 * s, 1), P.CARD, sw=0.8, light=None)
    c.add(f'<circle cx="{n(hooks[3])}" cy="{n(by + 8 * s + bh * 0.3)}" r="{n(10 * s)}" fill="none" '
          f'stroke="{P.CHARCOAL}" stroke-width="{n(3.2 * s)}"/><circle cx="{n(hooks[3])}" '
          f'cy="{n(by + 8 * s + bh * 0.3)}" r="{n(6 * s)}" fill="none" stroke="{P.CHARCOAL}" '
          f'stroke-width="{n(2.4 * s)}"/>')                                              # a coil of hose
    sx0, sx1 = x0 + (x1 - x0) * 0.55, x1 - 10 * k            # the shelf on the right
    sy = top + h * 0.5
    c.shape(rounded_rect_d(sx0, sy, sx1 - sx0, 4 * k, 1), P.WOOD_DARK, sw=1, light=None)
    x = sx0 + 6 * k
    for cw, ch, fill in ((12, 18, P.RED), (12, 18, P.GREEN), (26, 14, P.KITCHEN_KRAFT),
                         (12, 18, P.YELLOW), (26, 14, P.KITCHEN_KRAFT)):
        cw, ch = cw * k, ch * k
        if x + cw > sx1 - 4 * k:
            break
        c.shape(rounded_rect_d(x, sy - ch, cw, ch, 2), mix(fill, wood, 0.25), sw=1, light=None)
        if cw < 20 * k:                                                                  # an oil can's spout
            c.line(f"M{n(x + cw * 0.7)},{n(sy - ch)} l{n(3 * k)},{n(-4 * k)}", 1.2, P.METAL_DARK)
        x += cw + 4 * k
    lx = (sx0 + sx1) / 2                                                                 # the lamp over it
    c.line(f"M{n(lx)},{n(top)} v{n(h * 0.14)}", 1, P.METAL_DARK)
    c.shape(f"M{n(lx - 8 * k)},{n(top + h * 0.14 + 7 * k)} Q{n(lx)},{n(top + h * 0.14 - 3 * k)} "
            f"{n(lx + 8 * k)},{n(top + h * 0.14 + 7 * k)} Z", P.BLUE, sw=1, light=None)
    c.add(f'<circle cx="{n(lx)}" cy="{n(top + h * 0.14 + 8 * k)}" r="{n(2.6 * k)}" fill="{P.YELLOW_PALE}"/>')


def booth(s: Strip, x0: float, x1: float, color: str, goods: float) -> float:
    """A stall behind the lane, drawn in the backdrop: a counter with a striped skirt and a wooden top, and - where
    the frame has room - two posts and a scalloped awning over it, `goods` of room left under it for what stands
    on the counter. Returns the counter's top."""
    r, k = lane(s), s.unit
    roof_bottom = r.counter - goods - 10 * k
    if r.feet < s.h:
        boardwalk(s.back, x0 - 8 * k, x1 + 8 * k, r.feet - 3, min(16 * k, s.h - r.feet), k)
    _keep(s, (x0 - 12 * k, roof_bottom - 40 * k, x1 + 12 * k, r.feet + 16 * k))
    c = Canvas()                                          # an item, not the backdrop: the top veil never fades it
    whole = roof_bottom - 50 * k > 4                      # the awning and its pennants whole under the frame's top
    top = stall_art(c, x0, x1, r.counter, r.feet - 2, roof_bottom if whole else None, k, color)
    s.put(0.9, c.render(), None)
    return top


def stall_art(c: Canvas, x0: float, x1: float, top: float, foot: float, roof_bottom: float | None, k: float,
              color: str) -> float:
    """The stall itself: the counter from `top` to `foot` between x0 and x1, its striped skirt and wooden top, and,
    if `roof_bottom` is given, the posts and the striped, scalloped awning whose edge hangs there with a pennant at
    each end. Returns the counter's top."""
    roof_h = 34 * k
    if roof_bottom is not None:                           # its back wall, then the awning, only where it fits whole
        stall_back(c, x0 + 10 * k, x1 - 10 * k, roof_bottom + 6 * k, top, k)
        for px in (x0 + 6 * k, x1 - 6 * k):
            c.shape(rounded_rect_d(px - 3.5 * k, roof_bottom - 4, 7 * k, foot - roof_bottom + 4, 2), P.WOOD,
                    sw=1.8, light=None)
        roof = (f"M{n(x0 - 10 * k)},{n(roof_bottom)} L{n(x0 + 8 * k)},{n(roof_bottom - roof_h)} "
                f"H{n(x1 - 8 * k)} L{n(x1 + 10 * k)},{n(roof_bottom)} Z")
        clip = c.shape(roof, P.WHITE, sw=0, light=None, clip=True)
        step = 22 * k
        stripes, x = [], x0 - 10 * k
        while x < x1 + 10 * k:
            stripes.append(f"M{n(x)},{n(roof_bottom)} L{n(x + step * 0.3)},{n(roof_bottom - roof_h)} "
                           f"h{n(step * 0.5)} L{n(x + step * 0.5)},{n(roof_bottom)} Z")
            x += step
        c.add(f'<g clip-path="url(#{clip})"><path d="{" ".join(stripes)}" fill="{color}"/></g>')
        c.path(roof, "none", 2)
        _scallops(c, x0 - 10 * k, x1 + 10 * k, roof_bottom, 7 * k, color, P.WHITE, 1.6)
        if roof_bottom - roof_h - 18 * k > 4:
            for fx in (x0 + 8 * k, x1 - 8 * k):
                c.line(f"M{n(fx)},{n(roof_bottom - roof_h)} v{n(-16 * k)}", 1.6, P.WOOD_DARK)
                c.shape(f"M{n(fx)},{n(roof_bottom - roof_h - 16 * k)} l{n(12 * k)},{n(4 * k)} l{n(-12 * k)},"
                        f"{n(4 * k)} Z", P.YELLOW, sw=1.2, light=None)
    c.shape(f"M{n(x0)},{n(top)} H{n(x1)} V{n(foot)} H{n(x0)} Z", P.WHITE, sw=2, light=None)
    step = 18 * k
    skirt, x = [], x0
    while x < x1:
        skirt.append(f"M{n(x)},{n(top)} h{n(min(step / 2, x1 - x))} V{n(foot)} h{n(-min(step / 2, x1 - x))} Z")
        x += step
    c.add(f'<path d="{" ".join(skirt)}" fill="{color}" fill-opacity=".85"/>')
    c.path(f"M{n(x0)},{n(top)} H{n(x1)} V{n(foot)} H{n(x0)} Z", "none", 2)
    c.shape(rounded_rect_d(x0 - 6 * k, top - 7 * k, x1 - x0 + 12 * k, 8 * k, 2), P.WOOD_LIGHT, sw=1.8, light=None)
    return top - 7 * k


# ============================================================================ things
ENGINE = {"big": 1.0, "mid": 0.8, "small": 0.58}


def engine(x: float, y: float, k: float, size: str = "big", running: bool = False, flip: bool = False) -> str:
    """An engine on its skid, the middle of the skid's foot at (x, y), 90 wide and 64 tall at k = 1 for "big"
    (`ENGINE` scales the others): the finned block with a brass maker's plate on two rivets, the head with its spark
    plug and yellow filler cap, the fuel inlet's stub out of the head's side, the flywheel with its belt groove at
    one end, the exhaust at the other - puffing when it runs."""
    c = Canvas()
    c.shape(rounded_rect_d(-42, -7, 84, 7, 2), P.METAL_DARK, sw=1.6, light=None)               # the skid
    c.add(f'<circle cx="-36" cy="-3.5" r="1.4" fill="{INK}" fill-opacity=".35"/>'
          f'<circle cx="36" cy="-3.5" r="1.4" fill="{INK}" fill-opacity=".35"/>')                 # its bolts
    c.shape(rounded_rect_d(-30, -46, 54, 39, 4), P.METAL, sw=2, light=(-2, -2), shade_k=0.82)  # the block
    c.line(" ".join(f"M-26,{y0} H-2" for y0 in (-40, -34, -28, -22, -16)), 1.3, P.METAL_DARK, 0.9)  # its fins
    c.shape(rounded_rect_d(2, -36, 18, 12, 2), P.SUN, sw=1.2, light=None)                      # the maker's plate
    c.add(f'<circle cx="5" cy="-30" r="1.1" fill="{P.METAL_DARK}"/><circle cx="17" cy="-30" r="1.1" '
          f'fill="{P.METAL_DARK}"/>')
    c.line("M8,-32 H14 M8,-28 H13", 0.9, darken(P.SUN, 0.6))
    c.shape(rounded_rect_d(18, -55, 12, 6, 1.5), P.METAL_DARK, sw=1.2, light=None)             # the fuel inlet
    c.shape(rounded_rect_d(-26, -58, 46, 12, 3), P.METAL_LIGHT, sw=1.8, light=None)            # the head
    c.line("M-18,-52 H12", 1, P.METAL, 0.9)
    c.shape("M-12,-58 v-5 h6 v5 Z", P.CARD, sw=1.2, light=None)                                # the spark plug
    c.add(f'<rect x="-10.5" y="-66" width="3" height="3" fill="{P.METAL_DARK}"/>')
    c.shape(rounded_rect_d(5, -64, 11, 6, 1.5), P.YELLOW, sw=1.4, light=None)                  # the filler cap
    c.shape(ellipse_d(32, -27, 15, 15), P.RED, sw=2, light=(-2, -2))                           # the flywheel
    c.add(f'<circle cx="32" cy="-27" r="11" fill="none" stroke="{darken(P.RED, 0.7)}" stroke-width="1.2"/>')
    c.add(f'<circle cx="32" cy="-27" r="5" fill="{P.METAL}" stroke="{INK}" stroke-width="1.4"/>')
    c.shape("M-30,-33 H-40 V-56 H-34 V-39 H-30 Z", P.METAL_DARK, sw=1.6, light=None)            # the exhaust
    c.shape(rounded_rect_d(-42, -60, 10, 5, 1.5), P.METAL, sw=1.2, light=None)                 # its cap
    if running:
        for i, (px, py, pr) in enumerate(((-38, -66, 5), (-44, -76, 6.5), (-36, -86, 7.5))):
            c.add(f'<circle cx="{px}" cy="{py}" r="{pr}" fill="{lighten(P.METAL_PALE, 0.2 * i)}" stroke="{INK}" '
                  f'stroke-width="1.1"/>')
    return _at(c, x, y, k * ENGINE[size], flip)


def engine_box(x: float, y: float, k: float, size: str = "big") -> tuple:
    """The engine's box (`engine`, not running: no puffs over its exhaust)."""
    z = k * ENGINE[size]
    return (x - 46 * z, y - 66 * z, x + 48 * z, y)


def inlet(x: float, y: float, k: float, size: str = "big", flip: bool = False) -> tuple[float, float]:
    """Where the fuel inlet's mouth is on the page, for the engine at (x, y): a hose goes in from the right (from
    the left when the engine is drawn flipped)."""
    z = k * ENGINE[size]
    return (x - 30 * z if flip else x + 30 * z, y - 52 * z)


def kart(x: float, y: float, k: float, body: str = P.BLUE, number: str = "7", tooled: bool = False,
         motor: bool = True, flip: bool = False) -> str:
    """A fair go-kart in profile, nose to the right, the middle of its foot at (x, y), 160 long: a streamlined body
    with a racing stripe and a number roundel, bumpers front and back, the cockpit with its seat-back and steering
    wheel, the engine on the open rear deck (if `motor`), the exhaust curling out behind, a big rear wheel and a
    smaller front one, spoked. `tooled`: a red toolbox strapped on the nose, a mirror on a stalk, a headlight, an
    aerial with a pennant."""
    c = Canvas()
    if tooled:                                            # the aerial and its pennant, behind everything
        c.line("M-58,-48 L-66,-112", 2, P.METAL_DARK)
        c.shape("M-66,-112 l16,5 l-15,6 Z", P.YELLOW, sw=1.2, light=None)
    c.line("M-66,-36 H-82 q-6,0 -6,-6 q0,-5 5,-5", 4, P.METAL_DARK)                        # the exhaust
    if motor:
        c.add(engine(-44, -46, 0.42, "big"))
    c.shape("M-74,-22 L-74,-42 Q-74,-50 -64,-50 L-28,-50 L-22,-42 L16,-42 L22,-48 Q44,-48 64,-38 Q80,-30 78,-22 Z",
            body, sw=2.2, light=(-2, -2), shade_k=0.82)                                        # the body
    c.line("M-70,-30 H72", 3, lighten(body, 0.45), 0.9)                                       # its racing stripe
    c.shape(rounded_rect_d(-26, -70, 9, 30, 3), P.RED, sw=1.6, light=(-1, -1))                # the seat-back
    c.line("M12,-42 L4,-58", 3, P.METAL_DARK)                                                  # the steering column
    c.shape(ellipse_d(3, -60, 3.5, 10), P.CHARCOAL, sw=1.6, light=None)                       # the wheel, edge-on
    c.shape(rounded_rect_d(74, -32, 9, 10, 3), P.METAL_LIGHT, sw=1.4, light=None)            # the front bumper
    c.shape(rounded_rect_d(-82, -34, 9, 10, 3), P.METAL_LIGHT, sw=1.4, light=None)           # the rear bumper
    c.add(f'<circle cx="38" cy="-33" r="9" fill="{P.WHITE}" stroke="{INK}" stroke-width="1.6"/>')   # the roundel
    if tooled:
        c.shape(rounded_rect_d(26, -62, 30, 14, 2), P.RED, sw=1.6, light=(-1, -1))           # the toolbox
        c.line("M34,-62 v-4 h14 v4", 2)
        c.add(f'<rect x="29" y="-57" width="4" height="3" fill="{P.METAL}"/><rect x="49" y="-57" width="4" '
              f'height="3" fill="{P.METAL}"/>')
        c.line("M24,-55 H58", 1.2, P.CHARCOAL)                                                   # its strap
        c.line("M-12,-42 L-8,-70", 1.6, P.METAL_DARK)                                            # the mirror's stalk
        c.shape(ellipse_d(-7, -73, 6, 4), P.LENS, sw=1.4, light=None)
        c.add(f'<circle cx="72" cy="-36" r="4.5" fill="{P.SUN}" stroke="{INK}" stroke-width="1.4"/>')   # headlight
    for wx, wr in ((-44, 18), (52, 14)):
        c.shape(ellipse_d(wx, -wr, wr, wr), P.CHARCOAL, sw=2, light=None)
        c.add(f'<circle cx="{wx}" cy="{-wr}" r="{wr * 0.55}" fill="{P.METAL_LIGHT}" stroke="{INK}" '
              f'stroke-width="1.2"/>')
        spokes = " ".join(f"M{wx},{-wr} l{n(math.cos(math.radians(a)) * wr * 0.55)},"
                          f"{n(math.sin(math.radians(a)) * wr * 0.55)}" for a in range(0, 360, 60))
        c.line(spokes, 1, P.METAL_DARK)
        c.add(f'<circle cx="{wx}" cy="{-wr}" r="2.4" fill="{P.METAL_DARK}"/>')
    rx = x - 38 * k if flip else x + 38 * k                # the number, never mirrored with the kart
    return _at(c, x, y, k, flip) + lettering(rx, y - 29.2 * k, number, 11 * k, INK, style="plain")


def kart_box(x: float, y: float, k: float, tooled: bool = False, flip: bool = False) -> tuple:
    top = 114 if tooled else 78
    back, nose = (84, 90) if flip else (90, 84)
    return (x - back * k, y - top * k, x + nose * k, y)


def racing(x: float, y: float, k: float, way: int = 1) -> str:
    """What a kart racing to the right (`way` 1) or the left (-1) leaves behind, its tail at (x, y): a cloud of dust
    off its rear wheels - overlapping puffs, small at the wheel and growing as they trail back, paler and thinner
    the further they are - grit and small stones flung out of it, speed lines over it, and two grey puffs of
    exhaust from the pipe."""
    c = Canvas()
    dust = mix(P.WOOD, P.STONE, 0.45)
    for i in range(5):                                    # the cloud: puffs trailing back from the wheel
        px, py = x - way * (8 + i * 17) * k, y - (6 + i * 4.2) * k
        r_ = (6.5 + i * 3.0) * k
        op = 1.0 - i * 0.14
        for dx, dy, f in ((-0.6, 0.3, 0.8), (0.0, -0.4, 1.0), (0.7, 0.2, 0.75)):
            c.add(f'<circle cx="{n(px + dx * r_ * way)}" cy="{n(py + dy * r_)}" r="{n(r_ * f)}" fill="{dust}" '
                  f'fill-opacity="{op:.2f}" stroke="{darken(dust, 0.7)}" stroke-opacity="{op * 0.8:.2f}" '
                  f'stroke-width="{n(max(0.6, 0.9 * k))}"/>')
    for i, (dx, dy, r_) in enumerate(((14, -16, 1.6), (26, -6, 1.2), (34, -20, 1.4), (46, -12, 1.0), (20, -26, 1.1),
                                      (52, -24, 0.9))):   # grit and small stones flung out of it
        color = P.STONE if i % 2 else darken(P.STONE, 0.6)
        c.add(f'<path d="M{n(x - way * dx * k - r_ * k)},{n(y + dy * k)} l{n(r_ * k)},{n(-r_ * 1.2 * k)} '
              f'l{n(r_ * 1.3 * k)},{n(r_ * 0.4 * k)} l{n(-0.4 * r_ * k)},{n(r_ * k)} Z" fill="{color}" '
              f'stroke="{INK}" stroke-width="{n(max(0.5, 0.6 * k))}"/>')
    c.add(motion(x - way * 4 * k, y - 34 * k, 46, k, way=way))
    for i, (dx, dy, r_) in enumerate(((4, -26, 3.2), (12, -30, 4.2))):   # the exhaust's puffs
        c.add(f'<circle cx="{n(x - way * dx * k)}" cy="{n(y + dy * k)}" r="{n(r_ * k)}" fill="{P.METAL_LIGHT}" '
              f'fill-opacity="{0.9 - i * 0.25:.2f}" stroke="{P.METAL_DARK}" stroke-width="{n(max(0.6, 0.8 * k))}"/>')
    return c.render()


def cone(x: float, y: float, k: float, fallen: bool = False, way: int = 1) -> str:
    """A traffic cone standing on the track at (x, y), 26 wide and 30 tall: its square rubber base flat on the
    asphalt with a shadow under it, the orange cone with its white band. `fallen`: knocked over - lying on its side,
    its base towards `way`, rolling, with motion arcs behind it."""
    c = Canvas()
    c.add(f'<ellipse cx="0" cy="0.5" rx="16" ry="2.6" fill="{INK}" fill-opacity=".18"/>')     # its shadow
    if not fallen:
        c.shape("M-13,0 L-11,-4 H11 L13,0 Z", P.CHARCOAL, sw=1.2, light=None)                  # the base, flat
        c.shape("M-9,-4 L-3,-30 H3 L9,-4 Z", P.ORANGE, sw=1.6, light=(-1, -1))
        c.shape("M-6.6,-13 L-4.8,-21 H4.8 L6.6,-13 Z", P.WHITE, sw=0, light=None)
        c.line("M-9,-4 L-3,-30 H3 L9,-4", 1.6)
        return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'
    c.shape("M10,0 V-24 H14 V0 Z", P.CHARCOAL, sw=1.2, light=None)                           # its base, upright
    c.shape("M10,-3 L-18,-9 V-15 L10,-21 Z", P.ORANGE, sw=1.6, light=(-1, -1))               # the cone, lying
    c.shape("M-1,-6 L-8,-8 V-16 L-1,-18 Z", P.WHITE, sw=0, light=None)
    c.line("M10,-3 L-18,-9 V-15 L10,-21", 1.6)
    flip = "" if way > 0 else " scale(-1,1)"
    arcs = motion(x + way * 22 * k, y - 14 * k, 18, k, way=-way)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)}){flip}">{c.render()}</g>' + arcs


def graphics_card(x: float, y: float, k: float) -> str:
    """A big graphics card lying on its side, the middle of its bottom edge at (x, y), 104 long: the black shroud
    with three fans, the steel bracket with its ports at one end, the power socket on top, the gold contacts
    along the bottom."""
    c = Canvas()
    c.shape(rounded_rect_d(-44, -40, 94, 34, 5), P.CHARCOAL, sw=2, light=(-2, -2), shade_k=0.8)   # the shroud
    c.line("M-40,-14 H46", 1.4, P.BLUE)                                                            # its trim
    for fx in (-24, 4, 32):
        c.add(f'<circle cx="{fx}" cy="-24" r="11" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1.4"/>')
        blades = " ".join(f"M{fx},-24 q{n(math.cos(math.radians(a)) * 6)},{n(math.sin(math.radians(a)) * 6 - 3)} "
                          f"{n(math.cos(math.radians(a + 40)) * 10)},{n(math.sin(math.radians(a + 40)) * 10)}"
                          for a in range(0, 360, 60))
        c.line(blades, 1.6, P.METAL_LIGHT)
        c.add(f'<circle cx="{fx}" cy="-24" r="3" fill="{P.METAL}" stroke="{INK}" stroke-width="1"/>')
    c.shape(rounded_rect_d(-54, -44, 10, 44, 1.5), P.METAL_LIGHT, sw=1.6, light=None)   # the bracket
    c.add("".join(f'<rect x="-52" y="{yy}" width="6" height="5" rx="1" fill="{P.CHARCOAL}"/>'
                  for yy in (-38, -30, -22)))
    c.shape(rounded_rect_d(30, -46, 14, 6, 1.5), P.CHARCOAL, sw=1.2, light=None)        # the power socket
    c.shape(rounded_rect_d(-30, -6, 62, 6, 1), P.GREEN, sw=1.2, light=None)             # the board's edge
    c.add("".join(f'<rect x="{xx}" y="-4" width="3" height="4" fill="{P.SUN}"/>' for xx in range(-26, 30, 6)))
    return _at(c, x, y, k)


def barrow(x: float, y: float, k: float, flip: bool = False) -> str:
    """A wheelbarrow in profile, wheel to the right (to the left if `flip`), the wheel's foot at (x, y): a deep
    steel tray with a rolled rim and rivets, two rails running from the wheel's axle back to rubber grips, two legs
    with feet, the spoked wheel on its axle under the tray's front; a graphics card riding in the tray. 176
    long."""
    c = Canvas()
    c.line("M0,-20 L-150,-60", 4, P.WOOD_DARK)                                                  # the far rail
    c.line("M-136,-56 L-150,-60", 6, P.CHARCOAL)
    c.add(f'<g transform="rotate(-6 -52 -76)">{graphics_card(-52, -72, 0.9)}</g>')   # half out of the tray
    c.shape("M-112,-82 L12,-82 L-8,-44 L-90,-44 Z", P.BLUE, sw=2.2, light=(-2, -2), shade_k=0.8)   # the tray
    c.shape(rounded_rect_d(-116, -86, 132, 7, 3.5), P.METAL_LIGHT, sw=1.8, light=None)           # its rim
    c.add("".join(f'<circle cx="{xx}" cy="-74" r="1.6" fill="{P.METAL_DARK}"/>' for xx in range(-98, 6, 16)))
    c.line("M-96,-54 H-14", 1.2, darken(P.BLUE, 0.7))
    c.line("M-2,-20 L-152,-56", 5, P.WOOD)                                                       # the near rail
    c.line("M-2,-20 L-152,-56", 1.2, P.WOOD_DARK, 0.6)
    c.shape(rounded_rect_d(-158, -60, 18, 7, 3), P.CHARCOAL, sw=1.2, light=None)                # its grip
    c.line("M-88,-38 L-94,0 M-100,-36 L-104,0", 3.4, P.METAL_DARK)                              # the legs
    c.shape(rounded_rect_d(-110, -3, 22, 4, 1.5), P.METAL_DARK, sw=1, light=None)
    c.shape(ellipse_d(0, -20, 20, 20), P.CHARCOAL, sw=2.2, light=None)                         # the wheel
    c.add(f'<circle cx="0" cy="-20" r="13" fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="1.2"/>')
    c.line(" ".join(f"M0,-20 l{n(math.cos(math.radians(a)) * 13)},{n(math.sin(math.radians(a)) * 13)}"
                    for a in range(0, 360, 45)), 1.2, P.METAL_DARK)
    c.add(f'<circle cx="0" cy="-20" r="3.2" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>')
    return _at(c, x, y, k, flip)


BARROW_GRIP = (-150.0, -57.0)       # where the grips are, in the barrow's own units


def puffs(x: float, y: float, k: float) -> str:
    """Three puffs of grey smoke going up and aside from (x, y)."""
    c = Canvas()
    for i, (dx, dy, r) in enumerate(((0, 0, 6), (-7, -12, 8), (2, -26, 10))):
        tone = mix(P.METAL_DARK, P.METAL_PALE, i / 2)
        c.add(f'<circle cx="{n(x + dx * k)}" cy="{n(y + dy * k)}" r="{n(r * k)}" fill="{tone}" '
              f'stroke="{INK}" stroke-width="{n(max(1.0, 1.4 * k))}"/>')
    return c.render()


# ============================================================================ the cast
def stand(s: Strip, name: str, fracs: float | tuple[float, ...], pose: str, mood: str = "smile",
          flip: bool = True, mark: str | None = None):
    """A character on the lane at the first of `fracs` where it finds room and stands whole inside the frame, else
    nowhere. In a strip every character is drawn as tall as the strip lets it with the floor still showing under
    its feet - a short one is not left small beside a tall one."""
    flip ^= getattr(s, "flipx", False)
    floor = s.feet(0)
    scale = 1.0
    if s.h < 200:
        probe = _box(s, name, 0, floor)
        scale = (floor - 6) / max(1.0, probe[3] - probe[1])
    for frac in (fracs if isinstance(fracs, tuple) else (fracs,)):
        x = s.x(frac)
        box = _box(s, name, x, floor, scale)
        if box[1] >= 2 and box[0] >= 2 and box[2] <= W - 2 and s.free(box, 3):
            if s.h >= 200:
                return extra(s, name, frac, pose, mood, flip=flip, mark=mark)
            return s.cast(name, frac, pose, mood, flip=flip, mark=mark, size=SIZE[name] * scale)
    return None


def held(s: Strip, who, make, side: str = "right", turn: float = 0.0) -> None:
    """Put a thing into a character's hand, the fist closed round its grip (`Stage.hold`): `make(x, y, k)` draws it
    with its handle at (x, y) - the makers of `handheld`."""
    if who is not None:
        s.hold(who, make, side, turn)


# ============================================================================ the stations
def inside(s: Strip, x: float, left: float, right: float) -> float:
    """Move a thing whose box reaches `left` to the left of x and `right` to its right so that it stays within the
    frame's usable width - clear of the page-number tag's corner."""
    return min(max(x, s.lo + left), s.hi - right)


def engine_stall(s: Strip, x0: float, x1: float, big_first: bool = False) -> tuple[list[float], float, float]:
    """The engine stall between x0 and x1: the counter with its back wall and awning, three engines on it side by
    side with air - small to big, or big to small (`big_first`, the big one then faces left). Returns the engines'
    middles (in the order small, mid, big), the counter's top and the engines' scale."""
    k = s.unit
    sizes = ("small", "mid", "big")
    room_w = x1 - x0 - 24 * k
    widths = [94 * ENGINE[size] for size in sizes]
    ek = min(k * 1.05, room_w / (sum(widths) + 20 * (len(sizes) + 1)))
    gap = (room_w - sum(widths) * ek) / (len(sizes) + 1)
    top = booth(s, x0, x1, P.BLUE, 84 * ek)
    order = list(reversed(sizes)) if big_first else list(sizes)
    spots, x = {}, x0 + 12 * k + gap
    for size in order:
        w_ = 94 * ENGINE[size]
        spots[size] = x + 46 / 94 * w_ * ek
        x += w_ * ek + gap
    for size in sizes:
        flip = big_first and size == "big"
        s.put(1.6, engine(spots[size], top, ek, size, flip=flip), engine_box(spots[size], top, ek, size),
              f"engine_{size}", group=f"engine_{size}")
    return [spots[size] for size in sizes], top, ek


def engines_station(s: Strip, beat: str) -> None:
    """The stall of engines. "look": the agent at the counter points out the big engine, the cat explains it, the
    sparrow flies at the small fast one; the other camera has the stall on the right, the professor presenting it
    and the caterpillar peering at the smallest, unsure. "fuel": the old token pump fills the big engine through its
    hose, the counter on its drums rolling - the caterpillar writes down the cost, the cat points at the drums; the
    other camera has the pump on the left, the agent waiting by it with the cat timing the fill on his stopwatch."""
    r, k = lane(s), s.unit
    if beat == "look":
        if s.shot == 0:
            xs, top, ek = engine_stall(s, s.x(0.02), s.x(0.54))
            stand(s, "agent", (0.64, 0.68), "point", "smile", flip=True)
            stand(s, "cat", (0.86, 0.9), "think", "talk", flip=True)
            flier(s, xs[0], top - 46 * k, "smile")
        else:
            xs, top, ek = engine_stall(s, s.x(0.5), s.x(0.98), big_first=True)
            stand(s, "professor", (0.1, 0.06), "present", "talk", flip=False)
            stand(s, "caterpillar", (0.3, 0.34, 0.26, 0.38), "think", "worry", flip=False)
        # the golden floppy (an easter egg, `world_kit.hide`): one more thing for sale among the engines
        lo, hi = min(xs) - 60 * ek, max(xs) + 60 * ek
        among = sorted((lo + i * 4 for i in range(int((hi - lo) / 4) + 1)), key=lambda x: abs(x - (xs[0] + xs[1]) / 2))
        stash_along(s, among, top, 1.62)
        return
    if s.shot == 0:
        xs, top, ek = engine_stall(s, s.x(0.0), s.x(0.44))
        fx, fy = inlet(xs[2], top, ek, "big")
        pk = min(k * 1.1, (r.feet - 10) / 160)
        px = s.x(0.56)
        pump(s, px, r.feet, pk, s.word("tokens"), fy)
        a = port(s, fx, fy, 1, 0, "engine_big")
        b = port(s, px - 28 * pk, fy, -1, 0, "pump")
        if b.x - a.x > 30 * k:
            connect(s, a, b, "tube", max(2.6, 3.4 * pk), color=P.CHARCOAL, depth=1.65)
        stand(s, "caterpillar", (0.7, 0.74, 0.68), "write", "worry", flip=True)
        stand(s, "cat", (0.9, 0.87, 0.93, 0.84), "point", "talk", flip=True)
    else:
        xs, top, ek = engine_stall(s, s.x(0.34), s.x(0.8), big_first=True)
        fx, fy = inlet(xs[2], top, ek, "big", flip=True)
        pk = min(k * 1.1, (r.feet - 10) / 160)
        px = s.x(0.21)
        pump(s, px, r.feet, pk, s.word("tokens"), fy, outlet="right")
        a = port(s, px + 24 * pk, fy, 1, 0, "pump")
        b = port(s, fx, fy, -1, 0, "engine_big")
        if b.x - a.x > 30 * k:
            connect(s, a, b, "tube", max(2.6, 3.4 * pk), color=P.CHARCOAL, depth=1.65)
        stand(s, "agent", (0.04, 0.02, 0.0), "think", "smile", flip=False)
        held(s, stand(s, "cat", (0.9, 0.94), "present", "smile", flip=True), handheld.stopwatch)


def pump(s: Strip, x: float, feet: float, k: float, word: str, hose_y: float, outlet: str = "left") -> tuple:
    """The old token pump, like a fuel pump of the fifties, its foot's middle at (x, feet), 160 tall: a rounded
    blue body with chrome trim, a milk-glass globe on top saying what it pours, a window of rolling number drums,
    the hose's outlet at `hose_y` on its left (`outlet`) and the empty holster on its right, a
    plinth. Returns its box."""
    pen = Pen(s, x, feet, k)
    w, body_h = 56.0, 126.0
    size = letter(k, 8.0)
    tw, th = tag_size(word, size, k)
    worded = wrap(tw, k) <= w * 1.5                      # a word too wide for the globe at this size: plain glass
    gw = max(56.0, wrap(tw, k)) if worded else w * 0.7
    gh = wrap(th, k) + 4 if worded else 18.0
    top = -body_h - gh - 4
    pen.c.shape(rounded_rect_d(-w / 2 - 6, -10, w + 12, 10, 2), P.METAL_DARK, sw=1.6, light=None)     # the plinth
    body = pen.container("pump", -w / 2, -body_h, w, body_h - 10, P.BLUE, radius=14, shade_k=0.82)
    pen.c.line(f"M{n(-w / 2 + 3)},{n(-body_h + 22)} H{n(w / 2 - 3)} M{n(-w / 2 + 2)},{n(-24)} H{n(w / 2 - 2)}", 3,
               P.METAL_LIGHT)                                                                         # chrome bands
    pen.c.line(f"M{n(-w / 2 + 6)},{n(-body_h + 26)} V{n(-28)}", 2.4, lighten(P.BLUE, 0.4), 0.8)       # a shine
    pen.c.shape(rounded_rect_d(-6, -body_h - 6, 12, 8, 2), P.METAL_LIGHT, sw=1.4, light=None)        # the neck
    globe = pen.container("globe", -gw / 2, top, gw, gh, P.CARD, radius=gh / 2, sw=2, light=None)
    if worded:
        pen.tag("globe_word", 0, top + gh / 2, word, size, P.YELLOW_PALE, inside=globe)
    pad = pen.pad(w, body_h - 10)
    cw = w - 2 * pad - 6                                                                              # the counter
    ct = -body_h + 30
    counter = pen.container("drums", -cw / 2, ct, cw, 22, P.METAL_DARK, radius=3, sw=1.6, light=None)
    body.children.append(("drums", counter.outer))
    dpad = pen.pad(cw, 22)
    dgap = GAP_MIN / k + 0.6
    dw = (cw - 2 * dpad - 3 * dgap) / 4
    for i, digit in enumerate("0128"):
        dx = -cw / 2 + dpad + i * (dw + dgap)
        pen.c.add(f'<rect x="{n(dx)}" y="{n(ct + dpad)}" width="{n(dw)}" height="{n(22 - 2 * dpad)}" rx="1" '
                  f'fill="{P.WHITE}"/>')
        pen.c.add(lettering(dx + dw / 2, ct + 11 + 4.2, digit, 11.5, INK, style="plain"))
        pen.child(counter, f"drum{i}", dx, ct + dpad, dx + dw, ct + 22 - dpad)
    hy = max(ct + 28, -body_h * 0.5)
    hx = w / 2 - pad - 14
    if hy + 24 < -14:
        pen.c.shape(rounded_rect_d(hx, hy, 14, 22, 3), P.METAL_DARK, sw=1.4, light=None)              # the holster
        pen.child(body, "holster", hx, hy, hx + 14, hy + 22)
    oy = (hose_y - feet) / k                                                                          # the outlet
    oy = min(max(oy, -body_h + 12), -16)
    ox = -w / 2 - 4 if outlet == "left" else w / 2 - 4
    pen.c.shape(rounded_rect_d(ox, oy - 5, 8, 10, 2), P.METAL_LIGHT, sw=1.4, light=None)
    box = pen.box(-max(w / 2 + 6, gw / 2), top, max(w / 2 + 6, gw / 2), 0)
    s.put(feet - 1, pen.svg(), box, "pump", group="pump")
    return box


def carts_station(s: Strip, beat: str) -> None:
    """The karts the engine goes into. "pick": a plain blue kart and a tooled green one under a striped pavilion,
    the professor between them weighing them up, the agent pointing at the tooled one; in a strip the camera comes
    close on the tooled kart alone, the agent showing its toolbox and the sparrow at its pennant. "fit": a hoist
    lowers the big engine into the tooled kart, the agent guiding it, the caterpillar unsure, the cat watching; the
    other camera has the hoist on the right, the sparrow sitting on its beam and the cat checking a clipboard."""
    r, k = lane(s), s.unit
    if beat == "pick":
        if s.h < 200:                                     # close on one kart and the one who chose it
            ck = min(k * 1.5, (r.feet - 6) / -kart_box(0, 0, 1, True)[1])   # whole, under the frame's top
            bx = s.x(0.4)
            s.put(r.feet - 1, kart(bx, r.feet, ck, P.GREEN, "7", tooled=True), kart_box(bx, r.feet, ck, True),
                  "kart_tooled", group="kart_tooled")
            stand(s, "agent", (0.08, 0.04, 0.12), "point", "smile", flip=False)
            held(s, stand(s, "cat", (0.82, 0.86, 0.78, 0.9), "present", "smile", flip=True), handheld.stopwatch)
            return
        ck = min(k * 0.85, (s.hi - s.lo) * 0.34 / 174)        # two karts either side of the professor
        ax, bx = inside(s, s.x(0.0), 90 * ck, 84 * ck), inside(s, s.x(1.0), 90 * ck, 84 * ck)
        x0, x1 = s.x(0.0), s.x(0.8)
        eave = r.feet - 190 * k                           # over the professor's head with air
        if eave - min(60.0, (x1 - x0) * 0.14) * 1.4 > 6:
            roof = Canvas()
            pavilion(roof, x0, x1, eave, r.feet - 2, P.BLUE)
            s.put(0.9, roof.render(), None)
            _keep(s, (x0 - 12, eave - 90, x1 + 12, r.feet + 6))
        s.put(r.feet - 1, kart(ax, r.feet, ck, P.BLUE, "3"), kart_box(ax, r.feet, ck), "kart_plain",
              group="kart_plain")
        s.put(r.feet - 1, kart(bx, r.feet, ck, P.GREEN, "7", tooled=True), kart_box(bx, r.feet, ck, True),
              "kart_tooled", group="kart_tooled")
        stand(s, "professor", (0.5, 0.48, 0.52, 0.46, 0.54), "think", "smile", flip=True)
        return
    hk = min(k * 0.95, (r.feet - 8) / 186)
    if s.shot == 0:
        hoist(s, inside(s, s.x(0.26), 132 * hk, 132 * hk), r.feet, hk)
        stand(s, "agent", (0.6, 0.64), "present", "smile", flip=True)
        stand(s, "caterpillar", (0.78, 0.82), "think", "worry", flip=True)
        stand(s, "cat", (0.95, 0.92, 0.98, 0.89), "think", "smile", flip=True)
    else:
        hk *= 0.85
        box = hoist(s, inside(s, s.x(0.74), 132 * hk, 132 * hk), r.feet, hk)
        stand(s, "agent", (0.04, 0.02, 0.07), "present", "smile", flip=False)
        stand(s, "cat", (0.27, 0.24, 0.3, 0.33, 0.36), "read", "smile", flip=False)
        perch(s, "sparrow", box[0] + 30 * hk, box[1] - 1, "stand", "smile", flip=False, scale=0.5)


def hoist(s: Strip, x: float, feet: float, k: float) -> tuple[float, float, float, float]:
    """A gantry hoist over the tooled kart: two yellow legs braced on wide feet, the beam over them with its
    hazard stripes, the trolley and its chain block on the beam, the chain down to a hook, the hook through the
    engine's lifting eye - the engine hanging over the kart's open rear deck. Returns its box."""
    c = Canvas()
    span, tall = 112.0, 170.0
    for lx in (-span, span):
        way = 1 if lx < 0 else -1
        c.shape(rounded_rect_d(lx - 4, -tall, 8, tall, 2), P.YELLOW, sw=1.8, light=(-1, 0))
        c.shape(rounded_rect_d(lx - 18, -6, 36, 6, 2), P.METAL_DARK, sw=1.4, light=None)
        c.line(f"M{lx},{-26} L{lx + way * 18},{-6}", 3, P.YELLOW)                               # its brace
        c.line(f"M{lx},{-26} L{lx + way * 18},{-6}", 1, INK, 0.6)
    c.shape(rounded_rect_d(-span - 8, -tall - 10, span * 2 + 16, 12, 2), P.YELLOW, sw=2, light=None)
    c.line(" ".join(f"M{-span + i * 24},{-tall - 10} l12,12" for i in range(10)), 2.2, P.CHARCOAL, 0.8)
    c.shape(rounded_rect_d(-14, -tall + 2, 28, 8, 2), P.METAL, sw=1.6, light=None)            # the trolley
    c.add(f'<circle cx="-8" cy="{-tall + 2}" r="3" fill="{P.METAL_DARK}"/><circle cx="8" cy="{-tall + 2}" r="3" '
          f'fill="{P.METAL_DARK}"/>')
    c.shape(rounded_rect_d(-10, -tall + 10, 20, 14, 3), P.RED, sw=1.6, light=None)            # the chain block
    box = (x - (span + 20) * k, feet - (tall + 10) * k, x + (span + 20) * k, feet)
    s.put(feet - 2, _at(c, x, feet, k), box, "hoist", group="hoist")
    kx = x + 44 * k                                                # the kart, its rear deck under the trolley
    s.put(feet - 1, kart(kx, feet, k, P.GREEN, "7", tooled=True, motor=False), None, group="hoist")
    ek = k * 0.42
    ey = feet - 92 * k
    eye = ey - 68 * ek
    hook = (f'<circle cx="{n(x)}" cy="{n(eye)}" r="{n(4 * ek)}" fill="none" stroke="{INK}" '
            f'stroke-width="{n(max(1.2, 2 * ek))}"/>'
            f'<path d="M{n(x)},{n(eye - 14 * k)} v{n(6 * k)} q{n(5 * k)},{n(2 * k)} {n(3 * k)},{n(7 * k)} '
            f'q{n(-3 * k)},{n(4 * k)} {n(-6 * k)},{n(0)}" fill="none" stroke="{P.METAL_DARK}" '
            f'stroke-width="{n(max(1.4, 2.4 * k))}" stroke-linecap="round"/>')
    s.put(feet - 0.5, engine(x, ey, ek, "big") + hook, None, group="hoist")
    a = port(s, x, feet - (tall - 24) * k, 0, 1, "hoist")
    b = port(s, x, eye - 14 * k, 0, -1, "hoist")
    if b.y - a.y > 6:
        connect(s, a, b, "rod", max(1.6, 2.4 * k), color=P.METAL_DARK, depth=feet - 0.4, fits=(False, False))
        links = " ".join(f"M{n(x - 1.6 * k)},{n(a.y + t)} h{n(3.2 * k)}"
                         for t in [i * 5 * k for i in range(1, int((b.y - a.y) / (5 * k)))])
        s.put(feet - 0.3, f'<path d="{links}" stroke="{P.METAL_LIGHT}" stroke-width="{n(max(0.8, 1.2 * k))}"/>',
              None, group="hoist")
    return box


def track(s: Strip, x0: float, x1: float) -> float:
    """The test track along the lane between x0 and x1, in the backdrop: grey asphalt with white edge lines and a
    chequered start line. Returns the far edge, where the cones stand."""
    r, k = lane(s), s.unit
    far, near = max(s.base + 4, r.feet - 24 * k), min(s.h - 4, r.feet + 14 * k)
    far = min(far, near - 10)                             # a close-up: the track's near edge is the frame's
    c = s.back
    c.add(f'<rect x="-6" y="{n(far)}" width="{W + 12}" height="{n(near - far)}" fill="{P.STONE}" stroke="{INK}" '
          f'stroke-width="1.6"/>')
    c.line(f"M-6,{n(far + 3 * k)} H{W + 6} M-6,{n(near - 3 * k)} H{W + 6}", max(1.4, 2 * k), P.WHITE)
    c.add(f'<path d="M-6,{n((far + near) / 2)} H{W + 6}" stroke="{P.WHITE}" stroke-width="{n(max(1.0, 1.6 * k))}" '
          f'stroke-dasharray="{n(14 * k)} {n(12 * k)}"/>')
    sx, cell = x0 + (x1 - x0) * 0.08, max(3.0, 5 * k)
    rows = int((near - far - 6 * k) / cell)
    for i in range(rows):
        for j in range(2):
            fill = P.CHARCOAL if (i + j) % 2 else P.WHITE
            c.add(f'<rect x="{n(sx + j * cell)}" y="{n(far + 3 * k + i * cell)}" width="{n(cell)}" '
                  f'height="{n(cell)}" fill="{fill}"/>')
    track_kerbs(c, -6, W + 6, far, k)                      # the circuit's kerbs along both edges
    track_kerbs(c, -6, W + 6, near, k)
    _keep(s, (-6, far + 2, W + 6, near + 4))
    return far


def drive_station(s: Strip, beat: str) -> None:
    """The test drive on the track. "go": the tooled kart races by in a cloud of dust, cones on the track's far
    edge, the agent steering it by remote and the cat timing it, the sparrow racing along overhead; the other camera
    sees it come back the other way, the professor watching. "cone": one cone is knocked flying; in a strip the
    camera is close on the kart, the cone and the caterpillar writing it down; else the professor frowns and the
    agent shrugs with his remote."""
    r, k = lane(s), s.unit
    far = track(s, s.x(0.14), s.x(0.86))
    way = 1 if (beat == "go" and s.shot == 0) or beat == "cone" else -1
    ck = k * (1.4 if s.h < 200 else 0.9 if s.h < 400 else 0.52)
    cx = s.x(0.6 if s.h < 200 else 0.56 if s.h >= 400 else 0.5)
    kb = kart_box(cx, r.feet, ck, True, flip=way < 0)
    tail = kb[0] if way > 0 else kb[2]
    s.put(r.feet - 1, kart(cx, r.feet, ck, P.GREEN, "7", tooled=True, flip=way < 0) + racing(tail, r.feet, ck, way),
          (kb[0] - (50 * ck if way > 0 else 0), kb[1], kb[2] + (50 * ck if way < 0 else 0), kb[3]), "kart",
          group="kart")
    cones = ((0.34,) if s.h >= 400 else (0.22, 0.34, 0.72) if way > 0 else (0.2, 0.34, 0.66)) if s.h >= 200 \
        else (0.3, 0.26, 0.34)
    for i, f in enumerate(cones):                         # the cones on the track's far edge
        if s.h < 200 and any(b.name.startswith("cone") for b in s.boxes):
            break                                         # a close-up: one cone, the one knocked over
        x = s.x(f)
        fallen = beat == "cone" and (i == len(cones) - 1 or s.h < 200)   # the one just ahead of the kart
        y = far + min(12 * k, (r.feet - far) * 0.4)          # on the asphalt, past the kerb and the edge line
        reach = (20, 40) if way > 0 else (40, 20)             # a fallen cone rolls on, its motion arcs behind it
        box = (x - (reach[0] if fallen else 16) * k, y - (26 if fallen else 31) * k,
               x + (reach[1] if fallen else 16) * k, y + 3)
        if s.free(box, 3):
            s.put(y - 1, cone(x, y, k, fallen, way), box, f"cone{i}", group=f"cone{i}")
    if beat == "go":
        if s.shot == 0:
            agent = stand(s, "agent", (0.06, 0.1, 0.03, 0.14, 0.18, 0.22), "point", "smile", flip=False)
            held(s, stand(s, "cat", (0.92, 0.88, 0.95), "present", "smile", flip=True), handheld.stopwatch)
            flier(s, cx + 40 * ck, r.feet - 150 * ck, "smile")
        else:
            agent = stand(s, "agent", (0.92, 0.88, 0.95), "point", "smile", flip=True)
            stand(s, "professor", (0.04, 0.08), "think", "smile", flip=False)
        return
    if s.h < 200:
        stand(s, "caterpillar", (0.08, 0.12), "write", "worry", flip=False)
        return
    if mid(s):                                            # a mid strip: the professor would set the scale
        stand(s, "caterpillar", (0.04, 0.08, 0.12), "write", "worry", flip=False)
    else:
        stand(s, "professor", (0.04, 0.08), "think", "worry", flip=False)
    agent = stand(s, "agent", (0.95, 0.98, 0.9, 0.86, 0.82), "shrug", "worry", flip=True)
    del agent


def board_station(s: Strip, beat: str) -> None:
    """The results. "read": the scoreboard of how many tasks each engine solved, the cat explaining it, the
    caterpillar copying it down, the agent thinking; in a strip the camera is close on the board and the cat
    pointing at it. "podium": the engines on the winners' podium, the big one first - the professor's thumb up, the
    cat cheering, the sparrow on top of the winner; the other camera has the podium on the right, the agent and the
    caterpillar cheering it."""
    r, k = lane(s), s.unit
    if beat == "read":
        scoreboard(s, s.x(0.1 if s.h >= 200 else 0.2), r.feet, k * 1.1, s.word("solved"))
        stand(s, "cat", (0.58, 0.62, 0.66, 0.54), "point", "talk", flip=True)
        if s.h < 200:
            stand(s, "caterpillar", (0.86, 0.9, 0.82), "write", "smile", flip=True)
        else:
            stand(s, "caterpillar", (0.78, 0.82), "write", "smile", flip=True)
            stand(s, "agent", (0.95, 0.92), "think", "smile", flip=True)
        return
    pk = min(k * 1.2, (r.feet - 12) / 150)
    px = inside(s, s.x(0.3 if s.shot == 0 else 0.7), 92 * pk, 92 * pk)
    art = sets.podium(px, r.feet, pk)
    for dx, step, size in ((-60, 54, "mid"), (0, 78, "big"), (60, 40, "small")):
        art += engine(px + dx * pk, r.feet - step * pk, pk * 0.62, size)
    s.put(r.feet - 1, art, (px - 92 * pk, r.feet - (78 + 44) * pk, px + 92 * pk, r.feet), "podium", group="podium")
    if s.shot == 0:
        perch(s, "sparrow", px, r.feet - (78 + 44) * pk - 1, "cheer", "smile", flip=False, scale=0.5)
        stand(s, "professor", (0.66, 0.7), "thumb", "smile", flip=True)
        stand(s, "cat", (0.88, 0.92), "cheer", "smile", flip=True)
    else:
        stand(s, "agent", (0.08, 0.04), "cheer", "smile", flip=False)
        stand(s, "caterpillar", (0.3, 0.26), "cheer", "smile", flip=False)
        flier(s, px + 110 * pk, r.feet - 150 * pk, "smile", flip=True)


ROWS = (("big", 0.92, P.GREEN), ("mid", 0.81, P.YELLOW), ("small", 0.64, P.ORANGE))   # what each engine solved


def scoreboard(s: Strip, left: float, feet: float, k: float, word: str) -> tuple[float, float, float, float]:
    """The scoreboard on two legs, its left at `left` and its feet on the lane: a row of bulbs round its top, the
    title over three rows, each an engine, a bar as long as its share of tasks solved and the share in per cent.
    Returns its box."""
    icon_w, bar_w, row_h, legs = 40.0, 90.0, 30.0, 40.0

    def size_at(k: float):
        size, nsize = letter(k, 10.0), letter(k, 11.0)
        tw, th = tag_size(word, size, k)
        num_w = tag_size("100 %", nsize, k, "plain")[0]
        gap = GAP_MIN / k + 6
        inner_w = max(tw, icon_w + gap + bar_w + gap + num_w)
        inner_h = th + gap + len(ROWS) * row_h + (len(ROWS) - 1) * 4
        return size, nsize, th, num_w, gap, wrap(inner_w, k), wrap(inner_h, k)

    w, h = size_at(k)[5:]
    k = min(k, (feet - 14) / (h + legs + 8))
    size, nsize, th, num_w, gap, w, h = size_at(k)
    if getattr(s, "flipx", False):                        # a mirrored page: `left` is where its right edge goes
        left -= (w + 14) * k
    left = min(max(left, 4 + 10 * k), W - 4 - (w + 10) * k)
    pen = Pen(s, left, feet - (h + legs) * k, k)
    for lx in (w * 0.2, w * 0.8):                         # two steel posts on concrete feet, bolted down
        pen.c.shape(rounded_rect_d(lx - 5, h + 4, 10, legs - 10, 2), P.METAL_DARK, sw=1.6, light=None)
        pen.c.line(f"M{n(lx - 2)},{n(h + 8)} V{n(h + legs - 10)}", 1.4, P.METAL_LIGHT, 0.8)
        pen.c.shape(f"M{n(lx - 13)},{n(h + legs)} L{n(lx - 10)},{n(h + legs - 9)} H{n(lx + 10)} "
                    f"L{n(lx + 13)},{n(h + legs)} Z", P.STONE, sw=1.6, light=None)
        pen.c.add(f'<circle cx="{n(lx - 7)}" cy="{n(h + legs - 5)}" r="1.4" fill="{INK}"/>'
                  f'<circle cx="{n(lx + 7)}" cy="{n(h + legs - 5)}" r="1.4" fill="{INK}"/>')
    pen.c.shape(rounded_rect_d(-7, -7, w + 14, h + 14, 8), P.BLUE, sw=2, light=(-2, -2), shade_k=0.85)   # its frame
    pen.c.add("".join(f'<circle cx="{n(bx)}" cy="-3.5" r="2.4" fill="{P.SUN}" stroke="{INK}" stroke-width=".9"/>'
                      for bx in [w * (i + 0.5) / 11 for i in range(11)]))                         # bulbs round it
    pen.c.add("".join(f'<circle cx="{n(bx)}" cy="{n(h + 3.5)}" r="2.4" fill="{P.SUN}" stroke="{INK}" '
                      f'stroke-width=".9"/>' for bx in [w * (i + 0.5) / 11 for i in range(11)]))
    board = pen.container("scoreboard", 0, 0, w, h, P.SCREEN_DARK, radius=5, shade_k=0.9)
    pad = pen.pad(w, h)
    pen.tag("score_title", w / 2, pad + th / 2, word, size, P.CARD, inside=board)
    y = pad + th + gap
    x0 = pad + (w - 2 * pad - (icon_w + gap + bar_w + gap + num_w)) / 2
    for i, (kind, share, color) in enumerate(ROWS):
        cy = y + row_h / 2
        pen.c.add(engine(x0 + icon_w / 2, cy + 12, 0.36, kind))
        pen.child(board, f"icon{i}", x0 + icon_w / 2 - 18, cy - 12, x0 + icon_w / 2 + 18, cy + 12)
        bx = x0 + icon_w + gap
        pen.c.add(f'<rect x="{n(bx)}" y="{n(cy - 7)}" width="{n(bar_w)}" height="14" rx="3" '
                  f'fill="{darken(P.SCREEN_DARK, 0.7)}"/>')
        pen.c.shape(rounded_rect_d(bx, cy - 7, bar_w * share, 14, 3), color, sw=1.4, light=None)
        pen.child(board, f"bar{i}", bx, cy - 7, bx + bar_w, cy + 7)
        text = f"{round(share * 100)} %"
        nx = bx + bar_w + gap + num_w / 2
        pen.c.add(lettering(nx, cy + nsize * 0.36, text, nsize, P.SCREEN_TEXT, style="plain"))
        nw = tag_size(text, nsize, k, "plain")[0]
        pen.child(board, f"num{i}", nx - nw / 2 + 2, cy - nsize * 0.6, nx + nw / 2 - 2, cy + nsize * 0.5)
        y += row_h + 4
    box = pen.box(-8, -8, w + 8, h + legs)
    s.put(feet - 1, pen.svg(), box, "scoreboard", group="scoreboard")
    return box


def home_station(s: Strip, beat: str) -> None:
    """Running one at home. "carry": the caterpillar wheels a big graphics card home in a barrow, gripping its
    handles, the professor wondering if it is worth it, the agent waving her on; the other camera has her going
    the other way, the cat checking the card on his clipboard and the sparrow riding on the card. "sputter": the
    small engine on the home workbench sputters - black smoke and a smoke ring out of its exhaust, a bolt and a
    spring popping off it, shake lines as it jumps on the bench - the agent shrugs, the caterpillar frets, the
    professor is not impressed. No sound word: it reads by itself."""
    r, k = lane(s), s.unit
    if beat == "carry":
        flip = s.shot == 1
        if not flip:                                      # the agent on the left, showing her the way home
            stand(s, "agent", (0.1, 0.14, 0.06, 0.18, 0.22), "point", "smile", flip=False)
        fracs = (0.7, 0.74, 0.66, 0.78, 0.82) if flip else (0.46, 0.5, 0.42, 0.54, 0.38, 0.58, 0.34, 0.62, 0.3)
        for frac in fracs:                                # she stands where her barrow fits in front of her too
            x = s.x(frac)
            probe = _box(s, "caterpillar", x, s.feet(x))
            hx, hy = s.hand(Box(*probe, "caterpillar", "caterpillar", "actor", flip), "present", flip)
            gx, gy = BARROW_GRIP
            bk = max(0.4 * k, min(0.7 * k, (r.feet - hy) / -gy))    # its grips at her hands' height
            wx = hx + gx * bk if flip else hx - gx * bk
            box = (wx - 22 * bk, r.feet - 128 * bk, hx + 10 * bk, r.feet) if flip else \
                (hx - 10 * bk, r.feet - 128 * bk, wx + 22 * bk, r.feet)
            if not (box[0] > s.lo and box[2] < s.hi and box[1] > 4 and s.free(probe, 3) and s.free(box, 3)):
                continue
            cat = stand(s, "caterpillar", frac, "present", "worry", flip=flip)
            if cat is not None:
                s.put(r.feet - 0.5, barrow(wx, r.feet, bk, flip=flip), box, "barrow", group=cat.group)
            break
        if flip:
            stand(s, "cat", (0.06, 0.1), "read", "smile", flip=False)
            flier(s, s.x(0.3), r.feet - 150 * k, "smile")
        else:
            flier(s, s.x(0.3), r.feet - 210 * k, "smile")
        return
    bk = min(k * 1.2, (r.feet - 10) / (190 if s.h >= 200 else 120))   # low enough to leave sky for its smoke
    bx = s.x(0.4)
    eave = r.feet - 190 * k
    if eave - 60 * k > 6:
        roof = Canvas()
        pavilion(roof, bx - 110 * bk, bx + 110 * bk, eave, r.feet - 2, P.YELLOW, P.BLUE)
        s.put(0.9, roof.render(), None)
        _keep(s, (bx - 122 * bk, eave - 90, bx + 122 * bk, r.feet + 6))
    art = workbench(bx, r.feet, bk)
    top = r.feet - 62 * bk
    ez = bk * 0.8
    art += engine(bx, top, ez, "small", running=True)
    sx, sy = bx - 37 * ez * ENGINE["small"], top - 58 * ez * ENGINE["small"]
    sk = max(0.0, min(ez * 0.8, (sy - 40) / 150))         # the smoke it coughs out, as big as the sky over it lets
    smoke_top = sy - 112 * sk
    if sk > 0.2 and smoke_top > 6:
        art += smoke_cloud(sx, sy, sk, dark=True)
    ew = 47 * ez * ENGINE["small"]                        # half the engine's width
    art += engine_fit(bx, top, ez, ew)
    s.put(r.feet - 1, art, (bx - 70 * bk, min(top - 60 * bk, smoke_top - 30 * sk if smoke_top > 36 * sk else top),
                            bx + 78 * bk, r.feet), "bench", group="bench")
    stand(s, "agent", (0.66, 0.7, 0.62, 0.74, 0.58), "shrug", "worry", flip=True)
    stand(s, "caterpillar", (0.86, 0.9, 0.82, 0.94, 0.78), "think", "worry", flip=True)
    if mid(s):
        stand(s, "cat", (0.08, 0.04, 0.12), "think", "worry", flip=False)
    else:
        stand(s, "professor", (0.08, 0.04), "think", "worry", flip=False)


def engine_fit(x: float, top: float, k: float, half: float) -> str:
    """The small engine's fit on the bench at (x, top): shake lines either side of it as it jumps, a bolt and a
    spring popping off it with motion lines - no words needed."""
    c = Canvas()
    for side in (-1, 1):                                  # it jumps: shake lines either side
        for j in range(3):
            ox = x + side * (half + (6 + j * 5) * k)
            c.line(f"M{n(ox)},{n(top - (30 - j * 3) * k)} q{n(side * 3 * k)},{n(6 * k)} 0,{n(12 * k)}",
                   max(1.0, 1.6 * k), INK, 0.7)
    lid = top - 58 * k * ENGINE["small"]                  # the engine's top
    bx, by = x + half * 0.5, lid - 12 * k                 # a hex bolt flying off
    c.shape(f"M{n(bx - 4 * k)},{n(by)} l{n(2 * k)},{n(-3.4 * k)} h{n(4 * k)} l{n(2 * k)},{n(3.4 * k)} "
            f"l{n(-2 * k)},{n(3.4 * k)} h{n(-4 * k)} Z", P.METAL, sw=max(0.8, 1.1 * k), light=None)
    c.line(f"M{n(bx)},{n(by + 3.4 * k)} v{n(8 * k)}", max(1.2, 2 * k), P.METAL_DARK)
    c.add(motion(bx - 8 * k, by + 10 * k, 16, k * 0.7, way=-1, vertical=True))
    sx_, sy_ = x + half * 0.05, lid - 22 * k              # a spring popping up out of it
    c.line(f"M{n(sx_)},{n(sy_ + 14 * k)} " + " ".join(f"q{n(5 * k)},{n(-1.5 * k)} 0,{n(-3.5 * k)} "
                                                       f"q{n(-5 * k)},{n(-1.5 * k)} 0,{n(-3.5 * k)}"
                                                       for _ in range(2)), max(1.2, 1.8 * k), P.METAL_DARK)
    c.add(motion(sx_, sy_ + 22 * k, 14, k * 0.7, way=-1, vertical=True))
    return c.render()


def workbench(x: float, y: float, k: float) -> str:
    """A home workbench, 140 wide and 62 tall: the top board, two pairs of legs, a shelf low between them with a
    red toolbox on it, a vice clamped at its right end and a spanner and a screwdriver hanging on hooks under the
    top."""
    c = Canvas()
    c.line("M-60,0 V-56 M60,0 V-56 M-50,0 V-56 M50,0 V-56", 5, P.WOOD_DARK)
    c.shape(rounded_rect_d(-58, -22, 116, 6, 2), P.WOOD, sw=1.6, light=None)
    c.shape(rounded_rect_d(-34, -38, 36, 16, 3), P.RED, sw=1.6, light=None)                   # the toolbox
    c.line("M-24,-38 v-4 h16 v4", 2)
    c.add(f'<rect x="-30" y="-33" width="4" height="3" fill="{P.METAL}"/><rect x="-6" y="-33" width="4" '
          f'height="3" fill="{P.METAL}"/>')
    c.line("M12,-52 v4 M24,-52 v4", 1.2)                                                       # the hooks
    c.shape("M9,-48 h6 v3 l2,9 h-10 l2,-9 Z", P.METAL_LIGHT, sw=1, light=None)                # a spanner
    c.shape(rounded_rect_d(22, -48, 4, 8, 1), P.YELLOW, sw=1, light=None)                     # a screwdriver
    c.line("M24,-40 V-32", 1.4, P.METAL_DARK)
    c.shape(rounded_rect_d(-70, -62, 140, 10, 3), P.WOOD_LIGHT, sw=2, light=None)
    c.shape(rounded_rect_d(48, -74, 18, 12, 2), P.BLUE, sw=1.6, light=None)                   # the vice
    c.shape(rounded_rect_d(44, -78, 26, 5, 1.5), P.METAL_DARK, sw=1.2, light=None)
    c.line("M66,-68 H76 M76,-72 V-64", 1.8, P.METAL_DARK)                                      # its handle
    return _at(c, x, y, k)


def choice_station(s: Strip, beat: str) -> None:
    """The choice. "roll": the agent pushes the chosen kart - engine in, tools on - towards the fair's gate, the
    professor showing the way, the cat pleased; the other camera sees it from the gate, the kart driving off by
    remote and the caterpillar waving it goodbye. "button": the sparrow is at the big red button on its post, the
    caterpillar trying to call him off, the agent waving, the cat thinking better of it."""
    r, k = lane(s), s.unit
    if beat == "roll":
        ck = k * 0.62
        gk = min(k * 0.7, (r.feet - 8) / 220)
        if s.shot == 0:
            fair_gate(s, inside(s, s.x(0.86), 60 * gk, 68 * gk), r.feet, gk)
            cx = s.x(0.36)
            box = kart_box(cx, r.feet, ck, True)
            if s.free(box, 4):
                s.put(r.feet - 1, kart(cx, r.feet, ck, P.GREEN, "7", tooled=True), box, "kart", group="kart")
                pusher = (box[0] - s.lo - 30 * k) / (s.hi - s.lo)   # right behind the kart, hands on its tail
                stand(s, "agent", (pusher, pusher - 0.03, pusher - 0.06), "present", "smile", flip=False)
            stand(s, "professor", (0.64, 0.6, 0.68, 0.56), "point", "smile", flip=False)
        else:
            bye = stand(s, "caterpillar", (0.02, 0.0, 0.04), "wave", "smile", flip=True)   # left of the gate
            gx = (bye.right if bye else s.lo) + 64 * gk + 10
            gate = fair_gate(s, gx, r.feet, gk)
            ck = min(ck, (s.hi - gate[2] - 40) / 230)       # the kart fits between the gate and the edge
            cx = min(gate[2] + 84 * ck + 16, s.hi - 140 * ck)   # just past the gate, on its way out
            box = kart_box(cx, r.feet, ck, True, flip=True)  # driving out through the gate on the left
            art = kart(cx, r.feet, ck, P.GREEN, "7", tooled=True, flip=True) + racing(box[2], r.feet, ck, -1)
            s.put(r.feet - 1, art, (box[0], box[1], box[2] + 50 * ck, box[3]), "kart", group="kart")
            stand(s, "agent", (0.86, 0.9, 0.82, 0.94, 0.78, 0.74), "point", "smile", flip=True)
        return
    bk = min(k * 0.9, (r.feet - 16) / 130)
    px = s.x(0.6)
    post = 56 * bk
    box = red_button(s, px, r.feet - post, bk, s.word("dont"))
    s.put(r.feet - 1.2, f'<rect x="{n(px - 4 * bk)}" y="{n(r.feet - post - 1)}" width="{n(8 * bk)}" '
          f'height="{n(post)}" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1.4"/>',
          (px - 5 * bk, r.feet - post, px + 5 * bk, r.feet), "estop_post", group="estop")
    mid = (box[1] + box[3]) / 2
    flier(s, ((box[0] - 34 * k, mid), (box[2] + 34 * k, mid)), 0, "smile", flip=False)
    stand(s, "caterpillar", (0.86, 0.9), "wave", "worry", flip=True)
    stand(s, "agent", (0.32, 0.26), "wave", "smile", flip=False)
    stand(s, "cat", (0.08, 0.04), "think", "smile", flip=False)


def fair_gate(s, x: float, feet: float, k: float) -> tuple[float, float, float, float]:
    """The fair's gate: two striped posts with flags on top, an arch of blue between them with coloured pennants
    and a lantern hanging from its middle. Returns its box."""
    c = Canvas()
    half, tall = 52.0, 160.0
    for px in (-half, half):
        c.shape(rounded_rect_d(px - 5, -tall, 10, tall, 2), P.WHITE, sw=1.8, light=None)
        c.line(" ".join(f"M{px - 5},{-tall + 14 + i * 22} l10,8" for i in range(7)), 3, P.BLUE)
        c.line(f"M{px},{-tall} V{-tall - 22}", 1.8, P.METAL_DARK)
        c.shape(f"M{px},{-tall - 22} l14,5 l-14,5 Z", P.YELLOW, sw=1.2, light=None)
    c.shape(f"M{-half - 6},{-tall + 6} Q0,{-tall - 34} {half + 6},{-tall + 6} V{-tall + 18} Q0,{-tall - 20} "
            f"{-half - 6},{-tall + 18} Z", P.BLUE, sw=2, light=None)
    colors = (P.RED, P.YELLOW, P.GREEN, P.ORANGE)
    for i in range(7):
        t = (i + 0.5) / 7
        ax = -half + 2 * half * t
        ay = -tall + 18 - 34 * 4 * t * (1 - t) * 0.75
        c.shape(f"M{n(ax - 5)},{n(ay)} h10 l-5,10 Z", colors[i % 4], sw=1, light=None)
    box = (x - (half + 8) * k, feet - (tall + 24) * k, x + (half + 16) * k, feet)
    if box[2] > getattr(s, "hi", W) + 40 or box[1] < 4:
        return box
    s.put(feet - 3, _at(c, x, feet, k), box, "gate", group="gate", backdrop=True)
    lantern = Canvas()                                    # a lantern hanging from the arch on a short chain
    lantern.line(f"M0,{-tall - 8} V{-tall + 26}", 1.4, P.METAL_DARK)
    lantern.shape(f"M-7,{-tall + 26} h14 l-2,16 h-10 Z", P.YELLOW_PALE, sw=1.4, light=None)
    lantern.shape(f"M-9,{-tall + 26} h18 l-9,-6 Z", P.CHARCOAL, sw=1.2, light=None)
    s.put(feet - 2.9, _at(lantern, x, feet, k), None, group="gate")
    return box


# ============================================================================ the finale
def finale(s: Strip) -> None:
    """The whole fair at once: an alley of six tents, one for each station, its name - in the chapter's own words -
    painted on a wooden board hung on two ropes from the valance over the tent's door; in each doorway its one thing,
    so the sign and the thing explain each other, and who works there beside it - the engine and the agent, the
    tooled kart and the professor, the cones and the cat with its stopwatch, the scoreboard, the workbench and the
    caterpillar, the gate and the sparrow."""
    ledger(s)
    zoom(s)
    c = s.back
    sets.sky(c, mix(P.SKY, P.BLUE, 0.12), P.SKY_LOW, s.base + 10, W)
    if s.h >= 190:
        sets.hills(c, s.base + 6, W, (P.HILL_FAR, P.HILL_NEAR), seed=5)
    r = lane(s)
    fairground(c, s.base, s.h, s.unit, seed=8)
    left, right = s.lo, s.hi
    wide = (right - left) / 6
    named = s.h >= 300
    band = r.feet - 6
    th = min(band * 0.8, wide * 2.5)                      # the alley of tents, their pennants clear of the top
    foot = s.base + 4
    eave = foot - th * 0.5
    for i in range(6):
        main, stripe = TENTS[i]
        tent_art(c, left + wide * (i + 0.5), foot, wide * 0.96, th, main, stripe, door=True)
    sign_low = 0.0
    if named:                                             # each station's name on a board over its tent's door
        size = max(sets.LETTERING_MIN + 1, min(15.0, s.h * 0.028))
        widest = max(tag_size(s.word(st_.key), size)[0] for st_ in FAIR.stations)
        if widest > wide * 0.84 - 16:
            size = max(sets.LETTERING_MIN, size * (wide * 0.84 - 16) / widest)
        tag_h = tag_size("Ag", size)[1]
        hang = eave + max(5.0, th * 0.06) + 8            # under the valance's scallops, on two ropes
        sign_y = hang + tag_h / 2 + 4
        sign_low = sign_y + tag_h / 2 + 8
    part = wide * 0.46                                    # each tent: its thing in the doorway, its hero beside it
    room_h = min(band - 4, th * 0.9, r.feet - sign_low - 4 if named else 1e9)
    x = left + wide * 0.5
    ek = min((part - 6) / 94, room_h / 70)
    s.put(1.5, engine(x, r.feet, ek, "big"), engine_box(x, r.feet, ek, "big"), "f_engine", group="st0")
    x = left + wide * 1.5
    ck = min((part - 4) / 174, room_h / 116)
    s.put(1.5, kart(x, r.feet, ck, P.GREEN, "7", tooled=True), kart_box(x, r.feet, ck, True), "f_kart", group="st1")
    x = left + wide * 2.5
    nk = min((part - 6) / 64, room_h / 34)
    s.put(1.5, cone(x - 14 * nk, r.feet, nk) + cone(x + 6 * nk, r.feet, nk, True),
          (x - 30 * nk, r.feet - 31 * nk, x + 32 * nk, r.feet), "f_cones", group="st2")
    x = left + wide * 3.5
    bk = min((part - 6) / 118, room_h / 112)
    s.put(1.5, _mini_board(x, r.feet, bk), (x - 59 * bk, r.feet - 110 * bk, x + 59 * bk, r.feet), "f_board",
          group="st3")
    x = left + wide * 4.5
    wk = min((part - 6) / 156, room_h / 100)
    s.put(1.5, workbench(x, r.feet, wk) + engine(x - 16 * wk, r.feet - 62 * wk, wk * 0.8, "small", running=True),
          (x - 70 * wk, r.feet - 136 * wk, x + 78 * wk, r.feet), "f_bench", group="st4")
    x = left + wide * 5.5
    gk = min((part - 6) / 136, room_h / 184)
    fair_gate(s, x, r.feet, gk)
    cast_ = {0: ("agent", "point"), 1: ("professor", "think"), 2: ("cat", "present"), 4: ("caterpillar", "think"),
             5: ("sparrow", "cheer")}
    front = r.feet                                        # the cast stands in front of the tents, on the paving
    # one scale for the whole cast, all shrunk alike to the tightest fit (each capped on its own, the sparrow came
    # out bigger than the caterpillar)
    def most(name: str) -> float:
        return min(_fit_tall(name, wide * 0.5, room_h * 1.1),
                   _fit_tall(name, wide * 0.5, front - sign_low - 4) if named else 1e9) / (s.tall * SIZE[name])
    zoom_ = min([2.4] + [most(name) for name, _ in cast_.values() if name != "professor"])
    if most("professor") < zoom_:                          # the tallest would shrink everyone: he stays home
        cast_ = {i: who_ for i, who_ in cast_.items() if who_[0] != "professor"}
    for i, (name, pose) in cast_.items():
        x = left + wide * (i + 0.86)
        tall = s.tall * SIZE[name] * zoom_ * (0.55 if name == "sparrow" else 1)   # a bird beside them
        who = s.actor(name, min(x, s.hi - 30), front, pose, "smile", flip=True, tall=tall,
                      group="gate" if i == 5 else f"st{i}")
        if name == "cat":
            held(s, who, handheld.stopwatch)
    if named:
        pen = Pen(s, 0, 0, 1)
        for i, station in enumerate(FAIR.stations):
            cx = left + wide * (i + 0.5)
            holder = pen.tag(f"label{i}", cx, sign_y, s.word(station.key), size, P.WOOD_LIGHT, INK)
            x0, y0, x1, _ = holder.outer
            pen.c.add("".join(f'<path d="M{n(rx)},{n(eave + 2)} L{n(rx)},{n(y0 + 1)}" stroke="{P.WOOD_DARK}" '
                              f'stroke-width="1.6"/><circle cx="{n(rx)}" cy="{n(y0 + 3)}" r="1.6" fill="{INK}"/>'
                              for rx in (x0 + 8, x1 - 8)))       # its two ropes from the valance, the nails
            s.put(2, "", holder.outer, f"label{i}")
        s.put(2, pen.svg(), None)


def _mini_board(x: float, y: float, k: float) -> str:
    """The scoreboard small, without lettering: three engines and their bars, on two legs."""
    c = Canvas()
    c.line("M-36,0 V-40 M36,0 V-40", 6, P.METAL_DARK)
    c.shape(rounded_rect_d(-58, -110, 116, 72, 5), P.SCREEN_DARK, sw=2, light=None)
    for i, (kind, share, color) in enumerate(ROWS):
        cy = -96 + i * 22
        c.add(engine(-38, cy + 9, 0.3, kind))
        c.add(f'<rect x="-20" y="{cy - 5}" width="68" height="10" rx="2" fill="{darken(P.SCREEN_DARK, 0.7)}"/>')
        c.shape(rounded_rect_d(-20, cy - 5, 68 * share, 10, 2), color, sw=1.2, light=None)
    return _at(c, x, y, k)


# ============================================================================ the opener
def glow(c: Canvas, x: float, y: float, r: float) -> None:
    """A warm light in the evening: a bulb with two flat rings of light round it (no gradient: flat layers)."""
    c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r * 3)}" fill="{P.SUN}" fill-opacity=".14"/>'
          f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r * 1.9)}" fill="{P.SUN}" fill-opacity=".22"/>'
          f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{P.YELLOW_PALE}" stroke="{INK}" '
          f'stroke-width="{n(max(0.8, r * 0.25))}"/>')


def gondola(st: Stage, x: float, y: float, g: float, color: str, swing: float, rider: tuple | None = None) -> None:
    """A big wheel's gondola hanging from the rim at (x, y), `g` its half-width, swung by `swing` degrees: its
    hanger, the open cabin with a roof, and - `rider` (name, pose, mood[, "grip"]) - a character sitting in it,
    seen from the waist up over the cabin's front; "grip": afraid of the height, both hands clutching the safety
    bar on the front's top edge, short tremble lines beside the head."""
    a = math.radians(swing)
    back, front = Canvas(), Canvas()
    back.line(f"M0,0 V{n(g * 0.6)}", max(1.4, g * 0.08))
    back.shape(f"M{n(-g * 1.1)},{n(g * 0.75)} Q0,{n(g * 0.3)} {n(g * 1.1)},{n(g * 0.75)} Z", color, sw=1.6, light=None)
    back.shape(rounded_rect_d(-g, g * 0.75, g * 2, g * 1.9, g * 0.3), lighten(color, 0.5), sw=1.6, light=None)
    front.shape(rounded_rect_d(-g, g * 1.55, g * 2, g * 1.1, g * 0.3), color, sw=1.8, light=(-1, -1))
    front.line(f"M{n(-g * 0.8)},{n(g * 1.75)} H{n(g * 0.8)}", max(1.0, g * 0.06), lighten(color, 0.5))
    rot = f"translate({n(x)},{n(y)}) rotate({n(swing)})"
    st.back.add(f'<g transform="{rot}">{back.render()}</g>')
    box = (x - g * 1.2, y - 2, x + g * 1.2, y + g * 2.75)
    seat = (x - math.sin(a) * g * 1.6, y + math.cos(a) * g * 1.6)
    depth = 5.0
    if rider:
        name, pose, mood, *how = rider
        tall = _fit_tall(name, g * 1.8, g * 2.2) * 1.1
        who = st.actor(name, seat[0], seat[1] + g * 0.5, pose, mood, flip=False, tall=tall, group=f"g_{name}",
                       depth=depth)
        box = (min(box[0], who.left), min(box[1], who.top), max(box[2], who.right), box[3])
        if "grip" in how:                                 # the safety bar and two hands clutching it
            from .characters import module as char_module
            hand = getattr(char_module(name), "HAND", P.YELLOW)
            front.add(f'<rect x="{n(-g * 1.05)}" y="{n(g * 1.42)}" width="{n(g * 2.1)}" height="{n(g * 0.14)}" '
                      f'rx="{n(g * 0.07)}" fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="1.4"/>')
            for hx in (-g * 0.42, g * 0.42):
                front.add(f'<ellipse cx="{n(hx)}" cy="{n(g * 1.49)}" rx="{n(g * 0.16)}" ry="{n(g * 0.13)}" '
                          f'fill="{hand}" stroke="{INK}" stroke-width="1.4"/>')
                front.line(f"M{n(hx - g * 0.05)},{n(g * 1.4)} v{n(g * 0.16)} M{n(hx + g * 0.05)},{n(g * 1.4)} "
                           f"v{n(g * 0.16)}", 0.9)
            hy = who.top + (who.bottom - who.top) * 0.25
            for side in (-1, 1):
                ex = who.left - 4 if side < 0 else who.right + 4
                st.back.add(f'<path d="M{n(ex)},{n(hy - 8)} q{n(side * 4)},4 0,8 q{n(-side * 4)},4 0,8" fill="none" '
                            f'stroke="{P.YELLOW_PALE}" stroke-width="2.4" stroke-linecap="round"/>')
    st.put(depth + 0.1, f'<g transform="{rot}">{front.render()}</g>', box, f"gondola_{color}",
           group=f"g_{rider[0]}" if rider else None)


def opener(st: Stage, accent: str):
    """The fair at dusk from the overlook terrace, festive and turning - one hero, like the station's poster. A
    deep evening sky in the chapter's blue with a few stars, calm over the title, a hot-air balloon drifting at
    the left; one low hill and far off a flat row of tent silhouettes; and the big wheel, huge, right of
    centre, turning - motion arcs along its rim, its lamps lit, its gondolas swinging. The sparrow rides in the top
    gondola waving a wing, the caterpillar in the next one holding on, a little scared. On the terrace the professor
    tells about the fair under his bubble, the agent waves up at the sparrow, the cat times the wheel with his
    stopwatch."""
    ledger(st)
    c = st.back
    horizon = 860.0
    paint = c.gradient([(0, P.SPACE_DEEP), (0.6, mix(P.SPACE_LOW, P.BLUE, 0.55)), (1, mix(P.BLUE, P.SKY, 0.5))],
                       0, 0, 0, horizon)
    c.add(f'<rect x="0" y="0" width="{W}" height="{n(horizon + 10)}" fill="{paint}"/>')
    sets.stars(c, (300, 60, 820, 260), 16, seed=21)
    st.put(0.4, sets.hot_air_balloon(96, 420, 0.5, (P.BLUE, P.YELLOW)), (60, 312, 132, 422), "balloon")
    hill = mix(P.SPACE_LOW, P.HILL_NEAR, 0.35)
    c.shape(f"M-10,{horizon} Q200,{horizon - 70} 460,{horizon - 40} T{W + 10},{horizon - 30} V{H} H-10 Z", hill,
            sw=2, light=None)
    # the big wheel, the one hero, turning; its legs go down behind the tent band
    wx, wr = 590.0, 220.0
    wfoot = horizon + 10
    turn = 22.5
    wheel_art(c, wx, wfoot, wr, turn, gondolas=False)
    wcy = wfoot - wr * 1.2
    for i in range(32):
        a = math.radians(i * 11.25 + 3)
        glow(c, wx + math.cos(a) * wr, wcy + math.sin(a) * wr, 3.4)
    glow(c, wx, wcy, 7)
    st.keep_clear(*[(wx + math.cos(a) * wr - 8, wcy + math.sin(a) * wr - 8, wx + math.cos(a) * wr + 8,
                     wcy + math.sin(a) * wr + 8) for a in [math.pi * q / 16 for q in range(32)]])   # the rim
    for a0, a1 in ((200, 240), (300, 335), (20, 55)):    # motion arcs outside the rim: it turns
        ro = wr + 26
        p0 = (wx + math.cos(math.radians(a0)) * ro, wcy + math.sin(math.radians(a0)) * ro)
        p1 = (wx + math.cos(math.radians(a1)) * ro, wcy + math.sin(math.radians(a1)) * ro)
        c.add(f'<path d="M{n(p0[0])},{n(p0[1])} A{n(ro)},{n(ro)} 0 0 1 {n(p1[0])},{n(p1[1])}" fill="none" '
              f'stroke="{P.YELLOW_PALE}" stroke-width="4" stroke-linecap="round"/>')
        sa, ca = math.sin(math.radians(a1)), math.cos(math.radians(a1))      # its arrowhead, pointing on
        c.add(f'<path d="M{n(p1[0])},{n(p1[1])} l{n(-10 * sa - 6 * ca)},{n(10 * ca - 6 * sa)}" '
              f'stroke="{P.YELLOW_PALE}" stroke-width="4" stroke-linecap="round"/>')
    # the far tents: one flat row of silhouettes along the horizon, two flat colours
    far = mix(P.SPACE_LOW, P.BLUE, 0.35)
    x, i = -20.0, 0
    while x < W + 40:
        w, h = (70, 54) if i % 3 else (90, 70)
        c.add(f'<path d="M{n(x)},{horizon + 14} V{n(horizon + 14 - h * 0.45)} L{n(x + w / 2)},{n(horizon + 14 - h)} '
              f'L{n(x + w)},{n(horizon + 14 - h * 0.45)} V{horizon + 14} Z" '
              f'fill="{far if i % 2 else darken(far, 0.85)}"/>')
        x += w + 10
        i += 1
    c.add(f'<rect x="-6" y="{horizon + 12}" width="{W + 12}" height="{n(H - horizon)}" fill="{darken(far, 0.85)}"/>')
    # the gondolas, swinging; the sparrow rides at the top, the caterpillar low on the right
    colors = (P.RED, P.YELLOW, P.BLUE, P.GREEN, P.ORANGE, P.PINK, P.BLUE, P.YELLOW)
    riders = {5: ("sparrow", "wave", "smile"), 6: ("caterpillar", "stand", "surprise", "grip")}
    for i in range(8):
        a = math.radians(turn + i * 45)
        gx, gy = wx + math.cos(a) * wr, wcy + math.sin(a) * wr
        g = {"caterpillar": 52.0, "sparrow": 40.0}[riders[i][0]] if i in riders else 28.0
        if gy + g * 2.8 > horizon + 10:
            continue
        gondola(st, gx, gy, g, colors[i], (-8, 6, -4, 9, -6, 5, -10, 7)[i], riders.get(i))
    # the terrace: the railing over the drop, lamps on some posts, the paved floor where the cast stands
    deck = 1004.0
    rail = deck - 64
    c.add(f'<rect x="-6" y="{n(deck)}" width="{W + 12}" height="{n(H - deck + 6)}" fill="{JOINT}"/>')
    paving(c, -6, W + 6, deck, H + 4, 1.7, seed=9)
    c.add(f'<rect x="-6" y="{n(deck)}" width="{W + 12}" height="10" fill="{P.WOOD_DARK}"/>')
    c.line(" ".join(f"M{x},{rail + 8} V{deck}" for x in range(14, W, 22)), 4, P.WOOD_DARK)
    c.line(" ".join(f"M{x},{rail + 8} V{deck}" for x in range(14, W, 22)), 2, P.WOOD)
    c.add(f'<rect x="-6" y="{n(rail)}" width="{W + 12}" height="10" rx="4" fill="{P.WOOD}" stroke="{INK}" '
          f'stroke-width="2"/>')
    for x in (30, 430, 810):
        c.shape(rounded_rect_d(x - 5, rail - 30, 10, 30, 2), P.CHARCOAL, sw=1.2, light=None)
        glow(c, x, rail - 36, 5)
    prof = st.actor("professor", 150, 1096, "explain", "talk", tall=330)
    st.speaker(prof, width=76, left=8, air=CLEAR_MM)
    st.actor("agent", 460, 1120, "wave", "smile", flip=False, tall=330, group="agent")
    cat = st.actor("cat", 700, 1136, "present", "smile", flip=True, tall=300, group="cat")
    st.hold(cat, handheld.stopwatch)
    drawn = st.render()
    drawn.holders, drawn.links, drawn.ports = st.holders, st.links, st.ports
    return drawn


FAIR.stations.extend([
    Station("engines", _framed(engines_station), ("look", "fuel")),
    Station("carts", _framed(carts_station, ("pick",)), ("pick", "fit")),
    Station("drive", _framed(drive_station, ("cone",)), ("go", "cone")),
    Station("board", _framed(board_station, ("read",)), ("read", "podium")),
    Station("home", _framed(home_station, ("sputter",)), ("carry", "sputter")),
    Station("choice", _framed(choice_station, ("button",)), ("roll", "button")),
])
FAIR.backdrop = backdrop
FAIR.alternate = True                                     # never one moment on two pages in a row
FAIR.finale = finale
OPENERS["fairground"] = opener
hide(FAIR, "engines", "look")

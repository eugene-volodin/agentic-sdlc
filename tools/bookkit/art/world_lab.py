"""The laboratory: the world of chapter 7 (tests and linters: the agent learns of its mistake itself).

A bright testing lab: walls of white tiles over a band of yellow ones, yellow cabinets and fume hoods, shelves of
reagent bottles, a big wall clock, an eyewash station, a safety shower with its pull handle, a window. Every sample
is checked before it goes anywhere. The stations, one per section of the chapter:

1. cover       cover everything you can with tests: a long bench of test-tube racks, a labelled tube for every
               sample; the agent fills a new rack, the caterpillar counts the empty slots;
2. testfirst   the test first, then the code: an indicator flask - the indicator dropped in first turns the
               liquid red (the test fails), only then the reagent turns it green; a colour card beside it;
3. migrations  migrations need testing too: a distillation from the old flask through the condenser coil into a
               new one; then in two steps - the old flask's valve closed and tagged first, the flask taken away later;
4. production  what breaks only in production: the stress chamber behind its thick glass door, the sample that
               passed on the bench cracking under the press, the caterpillar wondering what if;
5. linters     linters that explain how to fix it: the cat at the microscope writes on a label not only what is
               wrong but how to fix it, and sticks it on the sample;
6. hooks       hooks: the analyzer checks every sample the agent puts down at once - its lamps, its printout; on
               the commit the pass-through hatch opens only for a sample with a green tag;
7. check       how to check that it all works: the agent breaks a sample on purpose and the analyzer catches it,
               the cat times it, the caterpillar ticks it off.

The back wall turns from frame to frame: tiles, shelves of bottles, a fume hood, the clock, the eyewash, the safety
shower, a window. No words in the pictures but the finale's names of the stations.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten, mix
from . import handheld, sets, stories
from .footers import Strip
from .ink import INK, Canvas, n, rounded_rect_d
from .openers import CLEAR_MM, H, W, Stage
from .world_fair import glow, held, inside, lane, mid, zoom
from .world_kit import SIZE, Pen, clock_hands, connect, hide, ledger, motion, port, stash_along, tag_size
from .world_kitchen import _fit_tall
from .world_sea import beside, gauge, scale_for, sparrow_on, stand, sx
from .worlds import Station, world

LAB = world("lab", opener="laboratory")

_at = sets._at

YELLOW = P.YELLOW
TILE = mix(YELLOW, P.CARD, 0.72)              # the wall tiles: pale yellow
GROUT = P.WHITE
TILE_Y = mix(YELLOW, P.CARD, 0.3)             # the deep yellow tile band below
CAB = mix(YELLOW, P.ORANGE, 0.12)             # yellow cabinets and hoods
FLOOR = (mix(P.METAL_LIGHT, YELLOW, 0.22), mix(P.CARD, YELLOW, 0.3))
GLASS = mix(P.LENS, P.WHITE, 0.35)
LIQUID = {"red": P.RED, "green": P.GREEN, "blue": mix(P.BLUE, P.TEAL, 0.4), "yellow": P.YELLOW,
          "violet": P.VIOLET, "orange": P.ORANGE, "clear": mix(P.LENS, P.WHITE, 0.2)}


def calm(color: str) -> str:
    """A colour of the back wall, calmer than the station's."""
    return mix(color, TILE, 0.4)


# ============================================================================ the room
def tiles(c: Canvas, x0: float, x1: float, y0: float, y1: float, size: float, color: str) -> None:
    """Square wall tiles from (x0, y0) to (x1, y1): their faces and the grout between them."""
    c.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" fill="{color}"/>')
    ys = [y0 + i * size for i in range(int((y1 - y0) / size) + 1)]
    xs = [x0 + i * size for i in range(int((x1 - x0) / size) + 1)]
    c.line(" ".join(f"M{n(x0)},{n(y)} H{n(x1)}" for y in ys) + " " + " ".join(f"M{n(x)},{n(y0)} V{n(y1)}" for x in xs),
           1.0, GROUT)


def floor_tiles(c: Canvas, x0: float, x1: float, y0: float, y1: float, k: float) -> None:
    """The lab's floor: square vinyl tiles in two tones, in rows growing towards the front."""
    c.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" fill="{darken(FLOOR[0], 0.85)}"/>')
    y, row = y0, 0
    while y < y1:
        rh = (8 + row * 5) * max(0.6, k)
        x = x0 - (row % 2) * rh
        q = 0
        while x < x1:
            c.add(f'<rect x="{n(x + 0.8)}" y="{n(y + 0.8)}" width="{n(rh * 2 - 1.6)}" height="{n(rh - 1.6)}" '
                  f'fill="{FLOOR[(row + q) % 2]}"/>')
            x += rh * 2
            q += 1
        y += rh
        row += 1


def bottle(c: Canvas, x: float, y: float, k: float, color: str, kind: int) -> None:
    """A reagent bottle standing at (x, y): a brown or clear glass bottle with its stopper or cap, the liquid in
    it, a white label with lines on it."""
    body = (P.WOOD_DARK, GLASS, mix(P.BLUE, P.WHITE, 0.4))[kind % 3]
    w, h = (12, 20, 14)[kind % 3] * k, (24, 18, 30)[kind % 3] * k
    c.add(f'<rect x="{n(x - w / 2)}" y="{n(y - h)}" width="{n(w)}" height="{n(h)}" rx="{n(2.4 * k)}" '
          f'fill="{body}" stroke="{INK}" stroke-width="{n(max(0.7, k))}"/>')
    c.add(f'<rect x="{n(x - w / 2 + 1.4 * k)}" y="{n(y - h * 0.55)}" width="{n(w - 2.8 * k)}" '
          f'height="{n(h * 0.55 - 1.4 * k)}" fill="{color}" fill-opacity=".7"/>')
    c.add(f'<rect x="{n(x - w * 0.22)}" y="{n(y - h - 5 * k)}" width="{n(w * 0.44)}" height="{n(5.4 * k)}" '
          f'rx="{n(1 * k)}" fill="{(P.CHARCOAL, P.RED, P.WHITE)[kind % 3]}" stroke="{INK}" '
          f'stroke-width="{n(max(0.6, 0.8 * k))}"/>')
    c.add(f'<rect x="{n(x - w / 2 + 1.6 * k)}" y="{n(y - h * 0.8)}" width="{n(w - 3.2 * k)}" height="{n(h * 0.3)}" '
          f'fill="{P.WHITE}" stroke="{INK}" stroke-width="{n(max(0.5, 0.6 * k))}"/>')
    c.line(f"M{n(x - w * 0.3)},{n(y - h * 0.7)} h{n(w * 0.6)}", max(0.5, 0.6 * k), INK, 0.6)


def wall_clock(c: Canvas, x: float, y: float, r: float) -> None:
    """The lab's big wall clock, calmed into the back wall: a yellow rim, a white dial with its twelve marks and
    hands."""
    c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{calm(P.WHITE)}" stroke="{calm(YELLOW)}" '
          f'stroke-width="{n(r * 0.16)}"/><circle cx="{n(x)}" cy="{n(y)}" r="{n(r * 1.08)}" fill="none" '
          f'stroke="{calm(INK)}" stroke-width="1.2"/>')
    c.line(" ".join(f"M{n(x + math.cos(a) * r * 0.74)},{n(y + math.sin(a) * r * 0.74)} "
                    f"L{n(x + math.cos(a) * r * 0.86)},{n(y + math.sin(a) * r * 0.86)}"
                    for a in [i * math.pi / 6 for i in range(12)]), max(1.0, r * 0.06), calm(INK))
    c.add(clock_hands(x, y, r * 0.46, r * 0.64, max(1.2, r * 0.08), calm(INK)))
    c.line(f"M{n(x)},{n(y)} L{n(x - r * 0.5)},{n(y + r * 0.4)}", max(0.6, r * 0.03), calm(P.RED))


def back_unit(c: Canvas, kind: str, x0: float, x1: float, top: float, foot: float, k: float, seed: int) -> None:
    """One thing of the back wall between x0 and x1, under `top`, standing on `foot`: shelves of reagent bottles,
    a fume hood, the clock, the eyewash station, the safety shower, a window - calmer than the station."""
    rnd = random.Random(seed)
    w, cx, room = x1 - x0, (x0 + x1) / 2, foot - top
    if kind == "shelves" and room > 60 * k:
        rows = max(1, min(3, int(room * 0.6 / (44 * k))))
        for j in range(rows):
            sy = top + 40 * k + j * 44 * k
            x = x0 + 8 * k
            while x < x1 - 14 * k:
                bottle(c, x + 6 * k, sy, k, calm(rnd.choice(list(LIQUID.values()))), rnd.randrange(3))
                x += rnd.uniform(16, 22) * k
            c.add(f'<rect x="{n(x0)}" y="{n(sy)}" width="{n(w)}" height="{n(4 * k)}" fill="{calm(CAB)}" '
                  f'stroke="{calm(INK)}" stroke-width="1"/>')
            for bx in (x0 + 6 * k, x1 - 6 * k):
                c.add(f'<path d="M{n(bx)},{n(sy + 4 * k)} l{n(-4 * k if bx < cx else 4 * k)},{n(8 * k)}" '
                      f'stroke="{calm(P.METAL_DARK)}" stroke-width="{n(2 * k)}"/>')
    elif kind == "hood" and room > 90 * k:
        ht = min(room - 6 * k, 170 * k)
        c.add(f'<rect x="{n(x0 + 4 * k)}" y="{n(foot - ht)}" width="{n(w - 8 * k)}" height="{n(ht)}" rx="{n(3 * k)}" '
              f'fill="{calm(CAB)}" stroke="{calm(INK)}" stroke-width="1.4"/>')
        sash_t, sash_b = foot - ht + 14 * k, foot - ht * 0.42
        c.add(f'<rect x="{n(x0 + 12 * k)}" y="{n(sash_t)}" width="{n(w - 24 * k)}" height="{n(sash_b - sash_t)}" '
              f'fill="{calm(GLASS)}" stroke="{calm(INK)}" stroke-width="1.2"/>')               # its glass sash
        c.line(f"M{n(x0 + 12 * k)},{n((sash_t + sash_b) / 2)} H{n(x1 - 12 * k)}", 2 * k, calm(P.METAL_DARK))
        for j in range(3):                                                                    # inside: flasks
            bottle(c, x0 + w * (0.3 + j * 0.2), sash_b - 2 * k, k * 0.8, calm(LIQUID[("blue", "green", "orange")[j]]),
                   j + 1)
        c.add(f'<rect x="{n(x0 + 4 * k)}" y="{n(sash_b)}" width="{n(w - 8 * k)}" height="{n(6 * k)}" '
              f'fill="{calm(P.METAL)}" stroke="{calm(INK)}" stroke-width="1"/>')
        for q in range(2):                                                                    # its cupboards
            c.add(f'<rect x="{n(x0 + 10 * k + q * (w - 20 * k) / 2)}" y="{n(sash_b + 12 * k)}" '
                  f'width="{n((w - 24 * k) / 2)}" height="{n(foot - sash_b - 18 * k)}" rx="{n(2 * k)}" '
                  f'fill="{calm(lighten(CAB, 0.12))}" stroke="{calm(INK)}" stroke-width="1"/>')
    elif kind == "clock" and room > 50 * k:
        wall_clock(c, cx, top + min(room * 0.3, 40 * k), min(28 * k, room * 0.22))
    elif kind == "eyewash" and room > 80 * k:
        y = top + room * 0.4
        c.add(f'<rect x="{n(cx - 3 * k)}" y="{n(y)}" width="{n(6 * k)}" height="{n(foot - y)}" '
              f'fill="{calm(P.METAL_LIGHT)}" stroke="{calm(INK)}" stroke-width="1"/>')       # its pipe
        c.add(f'<path d="M{n(cx - 22 * k)},{n(y)} Q{n(cx)},{n(y + 20 * k)} {n(cx + 22 * k)},{n(y)} Z" '
              f'fill="{calm(P.GREEN)}" stroke="{calm(INK)}" stroke-width="1.2"/>')            # its bowl
        for dx in (-8, 8):                                                                    # its two nozzles
            c.add(f'<rect x="{n(cx + dx * k - 3 * k)}" y="{n(y - 8 * k)}" width="{n(6 * k)}" height="{n(8 * k)}" '
                  f'rx="{n(2 * k)}" fill="{calm(YELLOW)}" stroke="{calm(INK)}" stroke-width="1"/>')
        c.add(f'<path d="M{n(cx + 3 * k)},{n(y + 30 * k)} h{n(16 * k)} v{n(-8 * k)}" fill="none" '
              f'stroke="{calm(P.METAL_DARK)}" stroke-width="{n(2.4 * k)}"/>')                # its push handle
    elif kind == "window" and room > 70 * k:
        ww, wh = min(w - 16 * k, 110 * k), min(room * 0.55, 100 * k)
        wy = top + 10 * k
        c.add(f'<rect x="{n(cx - ww / 2)}" y="{n(wy)}" width="{n(ww)}" height="{n(wh)}" fill="{lighten(P.SKY, 0.15)}" '
              f'stroke="{calm(P.WHITE)}" stroke-width="{n(6 * k)}"/><rect x="{n(cx - ww / 2 - 3 * k)}" '
              f'y="{n(wy - 3 * k)}" width="{n(ww + 6 * k)}" height="{n(wh + 6 * k)}" fill="none" '
              f'stroke="{calm(INK)}" stroke-width="1.2"/>')
        c.line(f"M{n(cx)},{n(wy)} V{n(wy + wh)} M{n(cx - ww / 2)},{n(wy + wh / 2)} H{n(cx + ww / 2)}", 3 * k,
               calm(P.WHITE))
        c.add(f'<rect x="{n(cx - ww / 2 - 8 * k)}" y="{n(wy + wh + 3 * k)}" width="{n(ww + 16 * k)}" '
              f'height="{n(5 * k)}" fill="{calm(P.METAL_LIGHT)}" stroke="{calm(INK)}" stroke-width="1"/>')
    elif kind == "shower" and room > 110 * k:
        hy = top + 20 * k
        c.add(f'<path d="M{n(cx)},{n(top - 10)} V{n(hy)}" stroke="{calm(P.METAL_LIGHT)}" stroke-width="{n(5 * k)}"/>')
        c.add(f'<path d="M{n(cx - 18 * k)},{n(hy + 10 * k)} Q{n(cx)},{n(hy - 4 * k)} {n(cx + 18 * k)},'
              f'{n(hy + 10 * k)} Z" '
              f'fill="{calm(P.GREEN)}" stroke="{calm(INK)}" stroke-width="1.2"/>')            # its shower head
        c.line(f"M{n(cx + 10 * k)},{n(hy + 4 * k)} V{n(hy + 60 * k)}", 1.4 * k, calm(P.METAL_DARK))
        c.add(f'<path d="M{n(cx + 4 * k)},{n(hy + 60 * k)} h{n(12 * k)} l{n(-6 * k)},{n(10 * k)} Z" '
              f'fill="{calm(P.GREEN)}" stroke="{calm(INK)}" stroke-width="1"/>')              # its pull handle


def backdrop(s: Strip, index: int) -> None:
    """The lab behind a station: a wall of pale yellow tiles over a high band of deep yellow ones, a yellow
    cornice in a taller frame, and along the wall shelves of reagent bottles, fume hoods, the clock, the eyewash
    station, a window, the safety shower - turning from frame to frame and calmer than the station; the tiled
    floor."""
    ledger(s)
    zoom(s)
    c = s.back
    base = s.base
    k = max(0.6, min(1.4, base / 240))
    size = 22 * k
    band = base - min(base * 0.46, 100 * k)
    tiles(c, -6, W + 6, -6, band, size, TILE)
    tiles(c, -6, W + 6, band, base, size, TILE_Y)
    c.add(f'<rect x="-6" y="{n(band - 3 * k)}" width="{W + 12}" height="{n(6 * k)}" fill="{YELLOW}" '
          f'stroke="{INK}" stroke-width="1"/>')                                            # the tiles' border
    top = 4.0
    if s.h >= 200:
        c.add(f'<rect x="-6" y="-6" width="{W + 12}" height="{n(22 * k)}" fill="{CAB}" stroke="{INK}" '
              f'stroke-width="1.2"/>')                                                      # the cornice
        top = 18 * k
    kinds = ("shelves", "hood", "clock", "window", "hood", "eyewash", "shelves", "shower", "hood")
    x = -40 * k * ((index * 0.6) % 1)
    i = index * 2
    while x < W:
        kind = kinds[i % len(kinds)]
        w = {"clock": 80, "eyewash": 70, "shower": 60, "window": 130, "hood": 150}.get(kind, 160) * k
        back_unit(c, kind, x + 6 * k, x + w - 6 * k, top + 6 * k, base, k, seed=index * 31 + i)
        x += w
        i += 1
    floor_tiles(c, -6, W + 6, base, s.h + 4, max(0.8, s.unit))
    c.add(f'<rect x="-6" y="{n(base - 5)}" width="{W + 12}" height="8" fill="{darken(CAB, 0.75)}" '
          f'stroke="{INK}" stroke-width="1.2"/>')                                            # the skirting


def _framed(draw):
    """A station drawn mirrored on every other page: it and its cast swap sides, the things are never mirrored.
    On the next visit of the same moment, two pages on, the onlooker is another character (`other`)."""
    def run(s: Strip, beat: str) -> None:
        s.mirror = bool(s.shot)
        s.again = (s.seed // 2) % 2 == 1
        draw(s, beat)
    return run


SWAP = {"professor": "cat", "cat": "professor", "caterpillar": "cat"}


def other(s: Strip, name: str) -> str:
    """The onlooker of this page: `name`, or on a second visit of the moment the one it trades with - the
    caterpillar standing in for the professor in a mid strip, where he would set the scale."""
    if getattr(s, "again", False):
        name = SWAP.get(name, name)
    if name == "professor" and mid(s):
        name = "caterpillar"
    return name


def sides(s: Strip) -> tuple[int, int]:
    return (-1, 1) if not getattr(s, "mirror", False) else (1, -1)


# ============================================================================ the things
def lab_bench(c: Canvas, x: float, foot: float, k: float, w: float = 220) -> dict:
    """A lab bench standing at (x, foot), `w` wide and 64 tall: a dark epoxy worktop with its rounded edge on a
    row of yellow cabinets - doors with steel handles - and a kick plate. Returns its box and its top."""
    d = Canvas()
    d.shape(rounded_rect_d(-w / 2 + 4, -10, w - 8, 10, 1), darken(CAB, 0.6), sw=1.2, light=None)   # kick plate
    d.shape(rounded_rect_d(-w / 2 + 2, -58, w - 4, 48, 2), CAB, sw=1.6, light=(-1, -1))
    count = max(2, int(w / 52))
    for q in range(count):
        dx = -w / 2 + 8 + q * (w - 16) / count
        d.shape(rounded_rect_d(dx, -54, (w - 16) / count - 4, 40, 2), lighten(CAB, 0.15), sw=1.0, light=None)
        d.line(f"M{n(dx + 6)},{n(-48)} h{n(10)}", 2.2, P.METAL_DARK)
    d.shape(rounded_rect_d(-w / 2 - 4, -66, w + 8, 9, 3), P.CHARCOAL, sw=1.6, light=None)        # the worktop
    d.line(f"M{n(-w / 2)},{n(-63)} H{n(w / 2)}", 1.0, P.METAL, 0.7)
    c.add(_at(d, x, foot, k))
    return {"box": (x - (w / 2 + 4) * k, foot - 66 * k, x + (w / 2 + 4) * k, foot), "top": foot - 66 * k}


def lab_cart(c: Canvas, x: float, foot: float, k: float, w: float = 110) -> dict:
    """A low lab trolley standing at (x, foot), `w` wide and 34 tall: a steel top with a raised lip, a lower shelf,
    four legs on castors. Same return as `lab_bench`."""
    d = Canvas()
    for lx in (-w / 2 + 4, w / 2 - 8):
        d.shape(rounded_rect_d(lx, -30, 4, 24, 1), P.METAL_DARK, sw=1.0, light=None)
        d.add(f'<circle cx="{lx + 2}" cy="-3.4" r="3.4" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width=".8"/>')
    d.shape(rounded_rect_d(-w / 2 + 2, -16, w - 4, 4, 1), P.METAL, sw=1.0, light=None)        # the lower shelf
    d.shape(rounded_rect_d(-w / 2, -34, w, 6, 1.5), CAB, sw=1.4, light=None)                  # the top
    d.line(f"M{n(-w / 2)},-34 V-38 M{n(w / 2)},-34 V-38", 1.6, P.METAL_DARK)
    c.add(_at(d, x, foot, k))
    return {"box": (x - (w / 2 + 1) * k, foot - 38 * k, x + (w / 2 + 1) * k, foot), "top": foot - 34 * k}


def tube(c: Canvas, x: float, y: float, k: float, color: str | None, label: bool = True) -> None:
    """A test tube standing at (x, y) in a rack: the glass with its rounded bottom, the liquid in it, its white
    label band."""
    c.add(f'<path d="M{n(x - 3 * k)},{n(y - 30 * k)} V{n(y - 3 * k)} A{n(3 * k)},{n(3 * k)} 0 0 0 {n(x + 3 * k)},'
          f'{n(y - 3 * k)} V{n(y - 30 * k)}" fill="{GLASS}" stroke="{INK}" stroke-width="{n(max(0.6, 0.8 * k))}"/>')
    if color:
        c.add(f'<path d="M{n(x - 2.4 * k)},{n(y - 16 * k)} V{n(y - 3 * k)} A{n(2.4 * k)},{n(2.4 * k)} 0 0 0 '
              f'{n(x + 2.4 * k)},{n(y - 3 * k)} V{n(y - 16 * k)} Z" fill="{color}"/>')
    if label:
        c.add(f'<rect x="{n(x - 3.4 * k)}" y="{n(y - 26 * k)}" width="{n(6.8 * k)}" height="{n(5 * k)}" '
              f'fill="{P.WHITE}" stroke="{INK}" stroke-width="{n(max(0.4, 0.5 * k))}"/>')


def rack(c: Canvas, x: float, y: float, k: float, filled: int, slots: int = 8, seed: int = 0) -> None:
    """A test-tube rack standing on the bench at (x, y), `slots` wide: its two wooden rails with holes, the
    `filled` first slots holding a labelled tube each, the rest empty."""
    rnd = random.Random(seed)
    w = slots * 9 * k + 8 * k
    c.add(f'<rect x="{n(x - w / 2)}" y="{n(y - 4 * k)}" width="{n(w)}" height="{n(4 * k)}" fill="{P.WOOD}" '
          f'stroke="{INK}" stroke-width="{n(max(0.6, 0.8 * k))}"/>')
    for q in range(slots):
        tx = x - w / 2 + 8 * k + q * 9 * k
        if q < filled:
            tube(c, tx, y - 2 * k, k, rnd.choice((P.RED, P.GREEN, LIQUID["blue"], P.ORANGE, P.VIOLET)))
    c.add(f'<rect x="{n(x - w / 2)}" y="{n(y - 22 * k)}" width="{n(w)}" height="{n(5 * k)}" fill="{P.WOOD_LIGHT}" '
          f'stroke="{INK}" stroke-width="{n(max(0.6, 0.8 * k))}"/>')
    c.add("".join(f'<ellipse cx="{n(x - w / 2 + 8 * k + q * 9 * k)}" cy="{n(y - 19.5 * k)}" rx="{n(3 * k)}" '
                  f'ry="{n(1.2 * k)}" fill="{P.WOOD_DARK}"/>' for q in range(filled, slots)))   # the empty holes
    for ex in (x - w / 2, x + w / 2 - 3 * k):
        c.add(f'<rect x="{n(ex)}" y="{n(y - 22 * k)}" width="{n(3 * k)}" height="{n(22 * k)}" fill="{P.WOOD_DARK}" '
              f'stroke="{INK}" stroke-width="{n(max(0.5, 0.6 * k))}"/>')


def flask(c: Canvas, x: float, y: float, k: float, color: str, level: float = 0.5, round_: bool = False) -> None:
    """A flask standing at (x, y), 40 wide: an Erlenmeyer's cone or a round-bottomed bulb, its neck, the liquid
    at `level`, a glint on the glass."""
    if round_:
        body = (f"M{n(x - 4 * k)},{n(y - 46 * k)} V{n(y - 34 * k)} A{n(18 * k)},{n(18 * k)} 0 1 0 {n(x + 4 * k)},"
                f"{n(y - 34 * k)} V{n(y - 46 * k)} Z")
        clip_d = body
        liq_top = y - 36 * k * (level + 0.2)
    else:
        body = (f"M{n(x - 5 * k)},{n(y - 46 * k)} V{n(y - 30 * k)} L{n(x - 20 * k)},{n(y - 2 * k)} Q{n(x - 20 * k)},"
                f"{n(y)} {n(x - 17 * k)},{n(y)} H{n(x + 17 * k)} Q{n(x + 20 * k)},{n(y)} {n(x + 20 * k)},"
                f"{n(y - 2 * k)} L{n(x + 5 * k)},{n(y - 30 * k)} V{n(y - 46 * k)} Z")
        clip_d = body
        liq_top = y - 30 * k * level
    clip = c.shape(clip_d, GLASS, sw=0, light=None, clip=True)
    c.add(f'<g clip-path="url(#{clip})"><rect x="{n(x - 22 * k)}" y="{n(liq_top)}" width="{n(44 * k)}" '
          f'height="{n(y - liq_top + 2)}" fill="{color}"/></g>')
    c.path(body, "none", max(0.9, 1.4 * k))
    c.add(f'<rect x="{n(x - 6 * k)}" y="{n(y - 48 * k)}" width="{n(12 * k)}" height="{n(3 * k)}" rx="{n(1 * k)}" '
          f'fill="{GLASS}" stroke="{INK}" stroke-width="{n(max(0.6, k))}"/>')               # its lip
    c.line(f"M{n(x - 12 * k)},{n(y - 8 * k)} L{n(x - 6 * k)},{n(y - 24 * k)}", max(0.8, 1.6 * k), P.WHITE, 0.8)


def burner(c: Canvas, x: float, y: float, k: float, lit: bool = True) -> None:
    """A Bunsen burner standing at (x, y): its round base, the barrel with its air collar, the gas tap, and - lit -
    a blue cone of flame with a pale tip."""
    c.add(f'<ellipse cx="{n(x)}" cy="{n(y - 2 * k)}" rx="{n(10 * k)}" ry="{n(3 * k)}" fill="{P.METAL_DARK}" '
          f'stroke="{INK}" stroke-width="{n(max(0.7, k))}"/>')
    c.add(f'<rect x="{n(x - 3 * k)}" y="{n(y - 26 * k)}" width="{n(6 * k)}" height="{n(24 * k)}" fill="{P.METAL}" '
          f'stroke="{INK}" stroke-width="{n(max(0.7, k))}"/><rect x="{n(x - 4 * k)}" y="{n(y - 12 * k)}" '
          f'width="{n(8 * k)}" height="{n(4 * k)}" fill="{P.METAL_DARK}"/>')
    c.add(f'<rect x="{n(x + 3 * k)}" y="{n(y - 7 * k)}" width="{n(7 * k)}" height="{n(3 * k)}" fill="{YELLOW}" '
          f'stroke="{INK}" stroke-width="{n(max(0.5, 0.6 * k))}"/>')                       # its gas tap
    if lit:
        c.add(f'<path d="M{n(x - 4 * k)},{n(y - 26 * k)} Q{n(x - 3 * k)},{n(y - 40 * k)} {n(x)},{n(y - 46 * k)} '
              f'Q{n(x + 3 * k)},{n(y - 40 * k)} {n(x + 4 * k)},{n(y - 26 * k)} Z" fill="{mix(P.BLUE, P.WHITE, 0.3)}" '
              f'stroke="{P.BLUE}" stroke-width="{n(max(0.6, 0.8 * k))}"/><path d="M{n(x - 2 * k)},{n(y - 26 * k)} '
              f'Q{n(x)},{n(y - 36 * k)} {n(x + 2 * k)},{n(y - 26 * k)} Z" fill="{P.YELLOW_PALE}"/>')


def ring_stand(c: Canvas, x: float, y: float, k: float, height: float, clamp_y: list[float], reach: float = 22,
               reaches: list[float] | None = None, grip: float = 6) -> None:
    """A retort stand at (x, y): its heavy base plate, the steel rod `height` tall and at each of `clamp_y` a
    boss-head on the rod and a clamp arm reaching `reach` (or each its own of `reaches`) to its two padded jaws,
    closed round a glass `grip` wide."""
    c.add(f'<rect x="{n(x - 6 * k)}" y="{n(y - 5 * k)}" width="{n(36 * k)}" height="{n(5 * k)}" rx="{n(1 * k)}" '
          f'fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="{n(max(0.7, k))}"/>')
    c.add(f'<rect x="{n(x - 1.6 * k)}" y="{n(y - height)}" width="{n(3.2 * k)}" height="{n(height)}" '
          f'fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="{n(max(0.6, 0.8 * k))}"/>')
    for q, cy in enumerate(clamp_y):
        r_ = (reaches[q] if reaches else reach) * k
        way = 1 if r_ >= 0 else -1
        c.add(f'<rect x="{n(x - 3.4 * k)}" y="{n(cy - 3.4 * k)}" width="{n(6.8 * k)}" height="{n(6.8 * k)}" '
              f'fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="{n(max(0.5, 0.7 * k))}"/>')    # the boss-head
        end = x + r_ - way * (grip / 2 + 2) * k
        c.line(f"M{n(x)},{n(cy)} H{n(end)}", max(1.2, 2.2 * k), P.METAL)                   # the arm
        for side in (-1, 1):                                                              # the jaws round the glass
            jy = cy + side * 3 * k
            c.add(f'<path d="M{n(end)},{n(jy)} H{n(x + r_ + way * (grip / 2 + 2) * k)}" stroke="{INK}" '
                  f'stroke-width="{n(3.2 * k)}" stroke-linecap="round"/><path d="M{n(end)},{n(jy)} '
                  f'H{n(x + r_ + way * (grip / 2 + 2) * k)}" stroke="{P.CHARCOAL}" stroke-width="{n(2 * k)}" '
                  f'stroke-linecap="round"/>')
        c.add(f'<circle cx="{n(end - way * 2 * k)}" cy="{n(cy - 6 * k)}" r="{n(1.6 * k)}" fill="{P.METAL_DARK}" '
              f'stroke="{INK}" stroke-width=".5"/>')                                       # its wing screw


def color_card(c: Canvas, x: float, y: float, k: float, mark: int) -> None:
    """The indicator's colour card standing on the bench at (x, y) in its holder: five swatches from red to
    green, a pointer at the swatch `mark` (0 red .. 4 green)."""
    cols = (P.RED, P.ORANGE, P.YELLOW, mix(P.YELLOW, P.GREEN, 0.5), P.GREEN)
    c.add(f'<rect x="{n(x - 4 * k)}" y="{n(y - 6 * k)}" width="{n(8 * k)}" height="{n(6 * k)}" fill="{P.CHARCOAL}" '
          f'stroke="{INK}" stroke-width="{n(max(0.5, 0.7 * k))}"/>')
    c.add(f'<rect x="{n(x - 16 * k)}" y="{n(y - 46 * k)}" width="{n(32 * k)}" height="{n(42 * k)}" rx="{n(2 * k)}" '
          f'fill="{P.WHITE}" stroke="{INK}" stroke-width="{n(max(0.7, k))}"/>')
    for q, col in enumerate(cols):
        c.add(f'<rect x="{n(x - 10 * k)}" y="{n(y - 42 * k + q * 7.4 * k)}" width="{n(14 * k)}" height="{n(6 * k)}" '
              f'fill="{col}" stroke="{INK}" stroke-width="{n(max(0.4, 0.5 * k))}"/>')
    py = y - 39 * k + mark * 7.4 * k
    c.add(f'<path d="M{n(x + 12 * k)},{n(py - 3 * k)} l{n(-6 * k)},{n(3 * k)} l{n(6 * k)},{n(3 * k)} Z" '
          f'fill="{INK}"/>')


def dropper(c: Canvas, x: float, y: float, k: float, drop: bool) -> None:
    """A dropper in the stand's clamp over a flask, its tip at (x, y): the red rubber bulb, the glass pipette and
    - `drop` - a drop falling from it with motion lines."""
    c.add(f'<path d="M{n(x - 2 * k)},{n(y - 30 * k)} V{n(y - 4 * k)} L{n(x)},{n(y)} L{n(x + 2 * k)},{n(y - 4 * k)} '
          f'V{n(y - 30 * k)} Z" fill="{GLASS}" stroke="{INK}" stroke-width="{n(max(0.6, 0.8 * k))}"/>')
    c.add(f'<rect x="{n(x - 4 * k)}" y="{n(y - 44 * k)}" width="{n(8 * k)}" height="{n(15 * k)}" rx="{n(4 * k)}" '
          f'fill="{P.RED}" stroke="{INK}" stroke-width="{n(max(0.6, 0.9 * k))}"/>')
    if drop:
        c.add(f'<path d="M{n(x)},{n(y + 6 * k)} q{n(3 * k)},{n(4 * k)} 0,{n(6 * k)} q{n(-3 * k)},{n(-2 * k)} 0,'
              f'{n(-6 * k)} Z" fill="{LIQUID["blue"]}" stroke="{INK}" stroke-width="{n(max(0.5, 0.6 * k))}"/>')
        c.add(motion(x - 4 * k, y + 2 * k, 8, k * 0.4, way=-1, vertical=True))


def indicator(c: Canvas, x: float, foot: float, k: float, color: str, mark: int, drop: bool,
              short: bool = False) -> dict:
    """The indicator set-up on a short bench at (x, foot), 160 wide and 150 tall: a retort stand with the
    dropper in its clamp over an Erlenmeyer flask of liquid in `color`, the colour card beside it with its
    pointer at `mark`, a wash bottle at the side. `short`: on a short bench, the flask and the card close, no
    wash bottle - for a strip."""
    b = lab_cart(c, x, foot, k, 120) if short else lab_bench(c, x, foot, k, 160)
    top = b["top"]
    ring_stand(c, x - 44 * k, top, k, 92 * k, [top - 80 * k], reach=40)
    flask(c, x - 4 * k, top, k * 1.1, color, 0.55)
    dropper(c, x - 4 * k, top - 58 * k, k, drop)
    color_card(c, x + (34 if short else 46) * k, top, k, mark)
    if short:
        return {"box": (b["box"][0] - 2 * k, top - 106 * k, b["box"][2], foot), "top": top - 104 * k}
    c.add(f'<path d="M{n(x + 66 * k)},{n(top)} V{n(top - 20 * k)} Q{n(x + 66 * k)},{n(top - 26 * k)} '
          f'{n(x + 72 * k)},{n(top - 26 * k)} Q{n(x + 78 * k)},{n(top - 26 * k)} {n(x + 78 * k)},{n(top - 20 * k)} '
          f'V{n(top)} Z" fill="{P.WHITE}" stroke="{INK}" stroke-width="{n(max(0.6, 0.9 * k))}"/>')   # wash bottle
    return {"box": (b["box"][0], top - 106 * k, b["box"][2], foot), "top": top - 104 * k}


def still(c: Canvas, x: float, foot: float, k: float, flowing: bool, two_step: bool, cart: bool = False) -> dict:
    """The distillation set-up on a bench at (x, foot), 230 wide and 160 tall: the old round flask on its lit
    burner, its stillhead and the condenser - a glass jacket with a coil inside - slanting down to the new flask;
    its liquid moving drop by drop. `two_step`: the valve between the old flask and the condenser closed with a
    red tag hanging on it, the burner out. `cart`: on a low trolley, for a strip. Returns its parts."""
    b = lab_cart(c, x, foot, k, 236) if cart else lab_bench(c, x, foot, k, 230)
    top = b["top"]
    ox, nx = x - 78 * k, x + 80 * k
    ring_stand(c, ox - 30 * k, top, k, 120 * k, [top - 70 * k], reach=26)
    burner(c, ox, top, k, lit=not two_step)
    flask(c, ox, top - 34 * k, k, LIQUID["violet"], 0.6, round_=True)
    c.add(f'<path d="M{n(ox)},{n(top - 80 * k)} V{n(top - 98 * k)} H{n(ox + 14 * k)}" fill="none" stroke="{INK}" '
          f'stroke-width="{n(6 * k)}"/><path d="M{n(ox)},{n(top - 80 * k)} V{n(top - 98 * k)} H{n(ox + 14 * k)}" '
          f'fill="none" stroke="{GLASS}" stroke-width="{n(4 * k)}"/>')                     # the stillhead
    vx, vy = ox + 18 * k, top - 98 * k                                                   # its valve
    c.add(f'<rect x="{n(vx - 4 * k)}" y="{n(vy - 4 * k)}" width="{n(8 * k)}" height="{n(8 * k)}" rx="{n(1.5 * k)}" '
          f'fill="{P.METAL}" stroke="{INK}" stroke-width="{n(max(0.6, 0.8 * k))}"/>')
    c.line(f"M{n(vx)},{n(vy)} l{n(0 if two_step else 6 * k)},{n(-8 * k if two_step else -6 * k)}", 2.6 * k, P.RED)
    if two_step:                                                                          # the tag on it
        c.line(f"M{n(vx)},{n(vy + 4 * k)} l{n(4 * k)},{n(10 * k)}", max(0.6, 0.8 * k), INK)
        c.add(f'<path d="M{n(vx + 1 * k)},{n(vy + 14 * k)} h{n(10 * k)} l{n(3 * k)},{n(4 * k)} l{n(-3 * k)},{n(4 * k)} '
              f'h{n(-10 * k)} Z" fill="{P.RED}" stroke="{INK}" stroke-width="{n(max(0.6, 0.8 * k))}"/>')
    cx0, cy0, cx1, cy1 = vx + 6 * k, vy, nx - 6 * k, top - 60 * k                        # the condenser
    ang = math.degrees(math.atan2(cy1 - cy0, cx1 - cx0))
    length = math.hypot(cx1 - cx0, cy1 - cy0)
    g = Canvas()
    g.add(f'<rect x="0" y="{n(-7 * k)}" width="{n(length)}" height="{n(14 * k)}" rx="{n(6 * k)}" fill="{GLASS}" '
          f'stroke="{INK}" stroke-width="{n(max(0.8, 1.2 * k))}"/>')
    wave = f"q{n(4 * k)},{n(-6 * k)} {n(8 * k)},0 q{n(4 * k)},{n(6 * k)} {n(8 * k)},0"
    g.add(f'<path d="M{n(6 * k)},0 ' + " ".join(wave for _ in range(int((length - 12 * k) / (16 * k)))) +
          f'" fill="none" stroke="{LIQUID["blue"]}" stroke-width="{n(max(0.8, 1.4 * k))}"/>')   # the coil
    for px in (10 * k, length - 14 * k):                                                  # its water nozzles
        g.add(f'<rect x="{n(px)}" y="{n(-12 * k)}" width="{n(4 * k)}" height="{n(5 * k)}" fill="{GLASS}" '
              f'stroke="{INK}" stroke-width="{n(max(0.5, 0.7 * k))}"/>')
    c.add(f'<g transform="translate({n(cx0)},{n(cy0)}) rotate({n(ang)})">{g.render()}</g>')
    ring_stand(c, nx + 34 * k, top, k, 90 * k, [cy1 + 2 * k], reach=-20)
    flask(c, nx, top, k, LIQUID["violet"], 0.45 if flowing or two_step else 0.12)
    c.line(f"M{n(cx1)},{n(cy1)} L{n(nx)},{n(top - 44 * k)}", 3 * k, GLASS)
    if flowing:
        c.add(f'<path d="M{n(nx)},{n(top - 40 * k)} q{n(2.6 * k)},{n(3.4 * k)} 0,{n(5 * k)} q{n(-2.6 * k)},'
              f'{n(-1.6 * k)} 0,{n(-5 * k)} Z" fill="{LIQUID["violet"]}" stroke="{INK}" stroke-width=".6"/>')
        c.add("".join(f'<circle cx="{n(ox + (q - 1) * 5 * k)}" cy="{n(top - 46 * k - q * 4 * k)}" r="{n(1.6 * k)}" '
                      f'fill="{P.WHITE}" fill-opacity=".8"/>' for q in range(3)))           # it boils
    return {"box": (b["box"][0], top - 124 * k, b["box"][2], foot), "top": top - 120 * k, "valve": (vx, vy - 8 * k)}


def stress_chamber(c: Canvas, x: float, foot: float, k: float, cracked: bool) -> dict:
    """The stress chamber standing at (x, foot), 140 wide and 180 tall: a yellow steel cabinet on feet, its
    thick glass door in a bolted frame with a handle, a big pressure gauge and a red lamp on top; inside, a
    hydraulic press bearing down on the sample - `cracked`: the sample split with cracks and chips flying, the
    gauge in the red, the lamp lit. Returns its box."""
    d = Canvas()
    for fx in (-56, 44):
        d.shape(rounded_rect_d(fx, -8, 12, 8, 1), P.CHARCOAL, sw=1.0, light=None)
    d.shape(rounded_rect_d(-66, -170, 132, 162, 6), CAB, sw=2.0, light=(-2, -2), shade_k=0.86)
    d.shape(rounded_rect_d(-54, -156, 92, 132, 6), P.METAL_DARK, sw=1.6, light=None)        # the door's frame
    d.add("".join(f'<circle cx="{bx}" cy="{by}" r="1.8" fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width=".5"/>'
                  for bx in (-50, -8, 34) for by in (-152, -28)))
    d.shape(rounded_rect_d(-46, -148, 76, 116, 4), GLASS, sw=1.4, light=None)                # its thick glass
    d.shape(rounded_rect_d(-30, -146, 44, 12, 2), P.METAL, sw=1.0, light=None)               # the press head
    d.line(f"M-8,-134 V{-102 if cracked else -106}", 6, P.METAL_DARK)
    d.shape(rounded_rect_d(-22, -102 if cracked else -106, 28, 6, 1.5), P.METAL, sw=1.0, light=None)
    d.shape(rounded_rect_d(-36, -42, 56, 8, 1), P.METAL_DARK, sw=1.0, light=None)            # the anvil
    if cracked:
        d.add(f'<path d="M-24,-42 L-24,-90 L-10,-96 L-12,-74 L-2,-66 L-8,-42 Z" fill="{LIQUID["orange"]}" '
              f'stroke="{INK}" stroke-width="1.2"/><path d="M-4,-42 L2,-66 L-6,-74 L-4,-96 L8,-90 L8,-42 Z" '
              f'fill="{LIQUID["orange"]}" stroke="{INK}" stroke-width="1.2"/>')                # split in two
        d.add("".join(f'<path d="M{px},{py} l3,-2 l1,3 Z" fill="{LIQUID["orange"]}" stroke="{INK}" '
                      f'stroke-width=".6"/>' for px, py in ((-34, -88), (16, -84), (-30, -60), (20, -56))))
    else:
        d.shape(rounded_rect_d(-24, -96, 32, 54, 3), LIQUID["orange"], sw=1.2, light=(-1, -1))   # the sample
    d.line("M-40,-140 L-30,-120", 2, P.WHITE, 0.6)
    d.shape(rounded_rect_d(38, -96, 8, 26, 3), P.METAL_DARK, sw=1.0, light=None)              # its handle
    gauge(d, 52, -136, 11, 0.95 if cracked else 0.45)
    d.add(f'<circle cx="0" cy="-176" r="6" fill="{P.RED if cracked else darken(P.RED, 0.5)}" stroke="{INK}" '
          f'stroke-width="1.2"/>')
    if cracked:
        d.add(f'<circle cx="0" cy="-176" r="11" fill="{P.RED}" fill-opacity=".3"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 66 * k, foot - 183 * k, x + 66 * k, foot), "top": foot - 182 * k}


def microscope(c: Canvas, x: float, y: float, k: float) -> None:
    """A microscope standing on the bench at (x, y): its horseshoe foot, the curved arm, the stage with a slide on
    it, the turret of lenses, the tube and the eyepiece, the focus knob."""
    c.add(f'<path d="M{n(x - 14 * k)},{n(y)} H{n(x + 16 * k)} L{n(x + 12 * k)},{n(y - 6 * k)} H{n(x - 10 * k)} Z" '
          f'fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="{n(max(0.7, k))}"/>')
    c.add(f'<path d="M{n(x + 8 * k)},{n(y - 6 * k)} Q{n(x + 16 * k)},{n(y - 30 * k)} {n(x + 2 * k)},{n(y - 46 * k)}" '
          f'fill="none" stroke="{INK}" stroke-width="{n(8 * k)}"/><path d="M{n(x + 8 * k)},{n(y - 6 * k)} '
          f'Q{n(x + 16 * k)},{n(y - 30 * k)} {n(x + 2 * k)},{n(y - 46 * k)}" fill="none" stroke="{P.WHITE}" '
          f'stroke-width="{n(6 * k)}"/>')                                                    # its arm
    c.add(f'<rect x="{n(x - 14 * k)}" y="{n(y - 22 * k)}" width="{n(22 * k)}" height="{n(3 * k)}" fill="{P.CHARCOAL}" '
          f'stroke="{INK}" stroke-width="{n(max(0.5, 0.7 * k))}"/><rect x="{n(x - 9 * k)}" y="{n(y - 24.4 * k)}" '
          f'width="{n(12 * k)}" height="{n(2.4 * k)}" fill="{GLASS}" stroke="{INK}" stroke-width=".5"/>')   # stage
    c.add(f'<g transform="rotate(-22 {n(x - 2 * k)} {n(y - 40 * k)})"><rect x="{n(x - 5 * k)}" y="{n(y - 58 * k)}" '
          f'width="{n(8 * k)}" height="{n(26 * k)}" fill="{P.WHITE}" stroke="{INK}" '
          f'stroke-width="{n(max(0.6, 0.9 * k))}"/>'
          f'<rect x="{n(x - 6 * k)}" y="{n(y - 64 * k)}" width="{n(10 * k)}" height="{n(7 * k)}" fill="{P.CHARCOAL}" '
          f'stroke="{INK}" stroke-width="{n(max(0.5, 0.7 * k))}"/><rect x="{n(x - 3 * k)}" y="{n(y - 32 * k)}" '
          f'width="{n(4 * k)}" height="{n(6 * k)}" fill="{P.METAL}" stroke="{INK}" stroke-width=".5"/></g>')
    c.add(f'<circle cx="{n(x + 13 * k)}" cy="{n(y - 20 * k)}" r="{n(3.4 * k)}" fill="{P.METAL_DARK}" stroke="{INK}" '
          f'stroke-width="{n(max(0.5, 0.7 * k))}"/>')                                      # its focus knob


def analyzer(c: Canvas, x: float, y: float, k: float, lamp: str, paper: int, sample: str | None) -> dict:
    """The automatic analyzer standing on the bench at (x, y), 110 wide and 70 tall: a white case with a yellow
    lid, the sample tray sliding in at its front with a tube in it, a row of three lamps - the lit one `lamp`
    ("green", "red" or ""), a small screen with a trace, and the printout curling out of its slot, `paper` long."""
    d = Canvas()
    d.shape(rounded_rect_d(-55, -60, 110, 60, 5), P.WHITE, sw=1.8, light=(-1, -1))
    d.shape(rounded_rect_d(-55, -70, 110, 14, 5), CAB, sw=1.6, light=None)
    d.shape(rounded_rect_d(-48, -48, 40, 26, 2), P.SCREEN_DARK, sw=1.2, light=None)          # its screen
    trace = "M-44,-30 l6,-4 l4,6 l5,-12 l6,8 l6,-3 l5,2"
    d.line(trace, 1.4, P.RED if lamp == "red" else P.GREEN)
    for q, col in enumerate((P.GREEN, P.YELLOW, P.RED)):                                    # its lamps
        on = (lamp == "green" and q == 0) or (lamp == "red" and q == 2)
        d.add(f'<circle cx="{10 + q * 12}" cy="-44" r="4" fill="{col if on else darken(col, 0.5)}" stroke="{INK}" '
              f'stroke-width=".8"/>')
        if on:
            d.add(f'<circle cx="{10 + q * 12}" cy="-44" r="8" fill="{col}" fill-opacity=".3"/>')
    d.shape(rounded_rect_d(4, -16, 44, 10, 2), P.METAL, sw=1.2, light=None)                 # the sample tray
    if sample:
        tube(d, 26, -12, 1.0, LIQUID[sample], label=True)
    d.shape(rounded_rect_d(-50, -16, 46, 4, 1), P.CHARCOAL, sw=0.8, light=None)             # the print slot
    if paper:
        d.add(f'<path d="M-46,-14 V{-14 + paper} q0,8 8,8 q6,0 6,-6 V-14 Z" fill="{P.WHITE}" stroke="{INK}" '
              f'stroke-width="1"/>')
        d.line(" ".join(f"M-44,{-10 + q * 5} h{6 + (q % 2) * 4}" for q in range(max(1, int(paper / 6)))), 0.8,
               INK, 0.6)
        if lamp == "red":
            d.line(f"M-44,{-14 + paper - 4} h9", 1.6, P.RED)
    c.add(_at(d, x, y, k))
    return {"box": (x - 55 * k, y - 70 * k, x + 55 * k, y + max(0, paper - 6) * k)}


def pass_through(c: Canvas, x: float, y: float, k: float, open_: bool) -> dict:
    """The pass-through hatch in the wall over the bench, its foot's middle at (x, y), 70 wide and 80 tall: a
    steel box set in the tiles, its door with a window and a latch, a lamp over it - green when it opens; `open_`:
    the door swung aside, the dark way through behind it."""
    d = Canvas()
    d.shape(rounded_rect_d(-35, -80, 70, 80, 4), P.METAL, sw=1.8, light=(-1, -1))
    d.add("".join(f'<circle cx="{bx}" cy="{by}" r="1.4" fill="{INK}"/>' for bx in (-31, 31) for by in (-76, -4)))
    if open_:
        d.shape(rounded_rect_d(-26, -66, 52, 58, 2), P.CHARCOAL, sw=1.2, light=None)        # the way through
        d.shape("M26,-66 L44,-60 V-14 L26,-8 Z", P.METAL_LIGHT, sw=1.4, light=None)        # the door, swung
    else:
        d.shape(rounded_rect_d(-26, -66, 52, 58, 2), P.METAL_LIGHT, sw=1.4, light=None)
        d.shape(rounded_rect_d(-14, -58, 28, 20, 2), GLASS, sw=1.0, light=None)
        d.shape(rounded_rect_d(16, -40, 6, 14, 2), P.METAL_DARK, sw=0.8, light=None)       # its latch
    d.add(f'<circle cx="0" cy="-88" r="5" fill="{P.GREEN if open_ else darken(P.GREEN, 0.5)}" stroke="{INK}" '
          f'stroke-width="1"/>')
    c.add(_at(d, x, y, k))
    return {"box": (x - 36 * k, y - 94 * k, x + (46 if open_ else 36) * k, y)}


def beaker_mug(x: float, y: float, k: float) -> str:
    """The cat's mug here: a lab beaker of tea with its pouring lip, steam over it, standing at (x, y)."""
    d = Canvas()
    d.shape("M-8,0 V-18 L-10,-20 H8 V0 Z", GLASS, sw=1.1, light=None)
    d.add(f'<rect x="-7" y="-10" width="14" height="9" fill="{P.WOOD}" fill-opacity=".8"/>')
    d.line("M-6,-14 h3 M-6,-8 h3", 0.6, INK, 0.6)
    d.line("M-2,-24 q3,-4 0,-8 M3,-24 q3,-4 0,-8", 1, P.METAL_DARK, 0.6)
    return _at(d, x, y, k)


def beaker(x: float, y: float, k: float) -> str:
    """A beaker gripped round its body (the grip frame of `handheld`): its glass with the pouring lip, the green
    reagent in it, two graduation marks."""
    d = Canvas()
    d.shape("M-7,6 V-15 L-9,-17 H7 V6 Z", GLASS, sw=0.6, light=None)
    d.add(f'<rect x="-6.4" y="-6" width="12.8" height="11.4" fill="{LIQUID["green"]}" fill-opacity=".85"/>')
    d.line("M-6,-10 h3 M-6,-2 h3", 0.4, INK, 0.7)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{d.render()}</g>'


# ============================================================================ the stations
def worktop(s: Strip, c: Canvas, x: float, k: float, w: float, cart_w: float) -> dict:
    """What a station's things stand on: the lab bench, `w` wide - or, in a strip, a low trolley `cart_w` wide, so
    that the things themselves can be drawn bigger."""
    if s.h < 200:
        return lab_cart(c, x, lane(s).feet, k, cart_w)
    return lab_bench(c, x, lane(s).feet, k, w)


def tall_(s: Strip, h: float) -> float:
    """A station's height in its own units, its bench or - in a strip - its lower trolley included."""
    return h - 32 if s.h < 200 else h


def cover_station(s: Strip, beat: str) -> None:
    """Cover everything you can: the long bench of test-tube racks, a labelled tube for every sample. "fill": the
    agent at the bench fills a new rack, the caterpillar with her clipboard counts the empty slots. "count": every
    rack full but the last, the professor (the cat in a mid strip) looks along it, the caterpillar counts on."""
    r = lane(s)
    bk = scale_for(s, 100, 240, 0.5, 0.62 if s.h >= 200 else 1.0)
    x = inside(s, sx(s, 0.5), 124 * bk, 124 * bk)
    c = Canvas()
    b = lab_bench(c, x, r.feet, bk, 240)
    for q in range(3):
        filled = (8, 8, 3 if beat == "fill" else 6)[q]
        rack(c, x - 76 * bk + q * 76 * bk, b["top"], bk * 0.95, filled, seed=q)
    box = (b["box"][0], b["top"] - 36 * bk, b["box"][2], r.feet)
    s.put(r.feet - 1, c.render(), box, "bench", group="bench")
    a, z = sides(s)
    if beat == "fill":
        stand(s, "agent", beside(s, box, z, "agent"), "point", "smile", flip=z > 0)
        if getattr(s, "again", False):                    # the next visit: the cat counts along the racks
            stand(s, "cat", beside(s, box, a, "cat"), "point", "smile", flip=a > 0)
        else:
            stand(s, "caterpillar", beside(s, box, a, "caterpillar"), "present", "worry", flip=a > 0,
                  hold=handheld.clipboard)
    else:
        stand(s, other(s, "professor"), beside(s, box, a, other(s, "professor")), "point", "talk", flip=a > 0)
        stand(s, "caterpillar", beside(s, box, z, "caterpillar"), "present", "smile", flip=z > 0,
              hold=handheld.clipboard)


def testfirst_station(s: Strip, beat: str) -> None:
    """The test first, then the code: the indicator flask under its dropper, the colour card beside it. "red": the
    indicator dropped in first turns the liquid red - the test fails as it should; the agent points at the card,
    the cat watches. "green": the reagent added, the liquid turns green; the agent cheers, the professor (the
    caterpillar in a mid strip) nods; the sparrow on the stand's clamp."""
    r = lane(s)
    short = s.h < 200                                     # a strip: on a low trolley, close
    ik = scale_for(s, 140 if short else 172, 130 if short else 170, 0.46, 1.1 if s.h >= 200 else 1.3)
    x = inside(s, sx(s, 0.5), 66 * ik if short else 84 * ik, 66 * ik if short else 84 * ik)
    c = Canvas()
    red = beat == "red"
    it = indicator(c, x, r.feet, ik, P.RED if red else P.GREEN, 0 if red else 4, drop=red, short=short)
    box = it["box"]
    s.put(r.feet - 1, c.render(), box, "indicator", group="indicator")
    if not short and getattr(s, "egg", None):            # the golden floppy (an easter egg, `world_kit.hide`):
        top = r.feet - 66 * ik                            # left on the worktop by the ring stand's foot
        stash_along(s, (x - 68 * ik,), top, r.feet - 0.9, group="indicator", turn=-6)
    a, z = sides(s)
    if red:
        stand(s, "agent", beside(s, box, z, "agent"), "point", "smile", flip=z > 0)
        stand(s, other(s, "cat"), beside(s, box, a, other(s, "cat")), "think", "smile", flip=a > 0)
    else:
        stand(s, "agent", beside(s, box, z, "agent"), "cheer", "smile", flip=z > 0)
        stand(s, other(s, "professor"), beside(s, box, a, other(s, "professor")), "think", "smile",
              flip=a > 0)
        sparrow_on(s, x - 44 * ik, box[1] + 10 * ik, "indicator")


def migrations_station(s: Strip, beat: str) -> None:
    """Migrations need testing too: the distillation from the old flask through the condenser into the new one.
    "move": the old flask boils, the liquid runs over drop by drop; the agent watches it, the cat times it with
    his beaker-mug by him. "twostep": the old flask's valve closed with a red tag - it stays for now and goes only
    later; the agent hangs the tag, the caterpillar checks it off."""
    r = lane(s)
    dk = scale_for(s, tall_(s, 190), 240, 0.5 if s.h >= 200 else 0.6, 0.95 if s.h >= 200 else 1.2)
    x = inside(s, sx(s, 0.5), 120 * dk, 120 * dk)
    c = Canvas()
    st_ = still(c, x, r.feet, dk, flowing=beat == "move", two_step=beat == "twostep", cart=s.h < 200)
    if beat == "move":
        c.add(beaker_mug(x + 30 * dk, r.feet - 66 * dk, dk * 1.2))
    box = st_["box"]
    s.put(r.feet - 1, c.render(), box, "still", group="still")
    a, z = sides(s)
    if beat == "move":
        stand(s, "agent", beside(s, box, a, "agent"), "think", "smile", flip=a > 0)
        stand(s, "cat", beside(s, box, z, "cat"), "present", "smile", flip=z > 0, hold=handheld.stopwatch)
    else:
        stand(s, "agent", beside(s, box, a, "agent"), "point", "smile", flip=a > 0)
        stand(s, "caterpillar", beside(s, box, z, "caterpillar"), "present", "worry", flip=z > 0,
              hold=handheld.clipboard)


def production_station(s: Strip, beat: str) -> None:
    """What breaks only in production: the stress chamber behind its thick glass door. "load": the sample that
    passed on the bench under the press, the agent at the chamber's door, the caterpillar wonders what if.
    "crack": the sample cracks under the real load, the lamp lit, the gauge in the red - the cat looks in, the
    agent worries; the sparrow on the chamber's top, at its lamp."""
    r = lane(s)
    ck = scale_for(s, 183, 132, 0.3, 1.0)
    x = inside(s, sx(s, 0.48), 66 * ck, 66 * ck)
    c = Canvas()
    ch = stress_chamber(c, x, r.feet, ck, cracked=beat == "crack")
    box = ch["box"]
    s.put(r.feet - 1, c.render(), box, "chamber", group="chamber")
    a, z = sides(s)
    if beat == "load":
        stand(s, "agent", beside(s, box, z, "agent"), "point", "smile", flip=z > 0)
        stand(s, other(s, "caterpillar"), beside(s, box, a, other(s, "caterpillar")), "think", "worry", flip=a > 0)
    else:
        stand(s, other(s, "cat"), beside(s, box, a, other(s, "cat")), "think", "worry", flip=a > 0)
        stand(s, "agent", beside(s, box, z, "agent"), "shrug", "worry", flip=z > 0)
        sparrow_on(s, x + 30 * ck, box[1] + 8 * ck, "chamber")


def linters_station(s: Strip, beat: str) -> None:
    """Linters that explain how to fix it: the microscope on the bench, the samples in a rack beside it. "look":
    the cat at the microscope looks, the agent waits with the sample. "label": the cat's label stuck on the
    sample - what is wrong in red, an arrow, the fix in green - the agent reads it, the cat points."""
    r = lane(s)
    bk = scale_for(s, tall_(s, 160), 170 if s.h >= 200 else 144, 0.36, 0.95 if s.h >= 200 else 1.2)
    x = inside(s, sx(s, 0.5), 88 * bk, 88 * bk)
    c = Canvas()
    b = worktop(s, c, x, bk, 170, 144)
    microscope(c, x - 34 * bk, b["top"], bk * 1.3)
    rack(c, x + 44 * bk, b["top"], bk, 4, slots=5, seed=7)
    if beat == "label":                                   # the cat's label, on its string from the sample
        c.line(f"M{n(x + 34 * bk)},{n(b['top'] - 35 * bk)} L{n(x + 30 * bk)},{n(b['top'] - 26 * bk)}", 1.2 * bk, INK)
        lk = bk * 1.3
        pen = Pen(s, x + 20 * bk, b["top"] - 58 * bk, lk)
        card = pen.container("fixlabel", 0, 0, 34, 22, P.WHITE, radius=1.4, sw=1.0, light=None)
        pad = pen.pad(34, 22)
        pen.c.line(f"M{n(pad)},{n(pad + 2)} h9 M{n(pad)},{n(22 - pad - 2)} h7", 1.4, P.RED)
        pen.c.add(f'<path d="M{n(pad + 10)},11 h5 l-2,-2 M{n(pad + 15)},11 l-2,2" fill="none" stroke="{INK}" '
                  f'stroke-width="1"/>')
        pen.c.line(f"M{n(pad + 17)},{n(pad + 2)} h7 M{n(pad + 17)},{n(22 - pad - 2)} h6", 1.4, P.GREEN)
        pen.child(card, "fix", pad, pad, 34 - pad, 22 - pad)
        s.put(r.feet - 0.8, pen.svg(), None, group="bench")
    box = (b["box"][0], b["top"] - 92 * bk, b["box"][2], r.feet)          # the microscope's eyepiece on top
    s.put(r.feet - 1, c.render(), box, "bench", group="bench")
    a, z = sides(s)
    stand(s, "cat", beside(s, box, a, "cat"), "think" if beat == "look" else "point", "smile", flip=a > 0)
    second = "caterpillar" if getattr(s, "again", False) else "agent"              # who brings the sample
    stand(s, second, beside(s, box, z, second), "think" if beat == "look" else "point", "smile", flip=z > 0)


def hooks_station(s: Strip, beat: str) -> None:
    """Hooks: "edit": the analyzer on the bench checks every sample the agent puts down at once - its green lamp,
    the printout curling out; the cat watches. "commit": the pass-through hatch in the wall opens only for a
    sample with a green tag - the agent hands it in, the caterpillar checks the tag; the sparrow on the hatch."""
    r = lane(s)
    bk = scale_for(s, tall_(s, 190), 180 if s.h >= 200 else 130, 0.4, 0.95 if s.h >= 200 else 1.2)
    x = inside(s, sx(s, 0.5), 94 * bk, 94 * bk)
    c = Canvas()
    b = worktop(s, c, x, bk, 180, 130)
    if beat == "edit":
        an = analyzer(c, x, b["top"], bk * 1.2, "green", 30, "green")
        box = (b["box"][0], an["box"][1], b["box"][2], r.feet)
    else:
        ph_ = pass_through(c, x, b["top"] - 4 * bk, bk * 1.25, open_=True)
        tube(c, x + 40 * bk, b["top"], bk * 1.3, P.GREEN)
        c.add(f'<rect x="{n(x + 44 * bk)}" y="{n(b["top"] - 26 * bk)}" width="{n(8 * bk)}" height="{n(5 * bk)}" '
              f'fill="{P.GREEN}" stroke="{INK}" stroke-width=".8"/>')                   # its green tag
        box = (b["box"][0], ph_["box"][1], b["box"][2], r.feet)
    s.put(r.feet - 1, c.render(), box, "bench", group="bench")
    a, z = sides(s)
    if beat == "edit":
        stand(s, "agent", beside(s, box, z, "agent"), "point", "smile", flip=z > 0)
        stand(s, other(s, "cat"), beside(s, box, a, other(s, "cat")), "think", "smile", flip=a > 0)
    else:
        stand(s, "agent", beside(s, box, z, "agent"), "point", "smile", flip=z > 0)
        stand(s, "caterpillar", beside(s, box, a, "caterpillar"), "present", "smile", flip=a > 0,
              hold=handheld.clipboard)
        sparrow_on(s, x, box[1] + 2, "bench")


def check_station(s: Strip, beat: str) -> None:
    """How to check that it all works: "break": the agent puts down a sample it broke on purpose and the analyzer
    catches it - the red lamp, a red mark on the printout - the cat times it. "catch": the caterpillar ticks it off
    on her clipboard, the agent cheers; the sparrow on the safety shower's pull handle, after the red button."""
    r = lane(s)
    bk = scale_for(s, tall_(s, 168), 180 if s.h >= 200 else 130, 0.4, 0.95 if s.h >= 200 else 1.2)
    x = inside(s, sx(s, 0.5), 94 * bk, 94 * bk)
    c = Canvas()
    b = worktop(s, c, x, bk, 180, 130)
    an = analyzer(c, x, b["top"], bk * 1.2, "red", 40, "orange")
    box = (b["box"][0], an["box"][1], b["box"][2], r.feet)
    s.put(r.feet - 1, c.render(), box, "bench", group="bench")
    a, z = sides(s)
    if beat == "break":
        stand(s, "agent", beside(s, box, z, "agent"), "point", "smile", flip=z > 0)
        stand(s, "cat", beside(s, box, a, "cat"), "present", "smile", flip=a > 0, hold=handheld.stopwatch)
    else:
        stand(s, "agent", beside(s, box, z, "agent"), "cheer", "smile", flip=z > 0)
        stand(s, "caterpillar", beside(s, box, a, "caterpillar"), "present", "smile", flip=a > 0,
              hold=handheld.clipboard)
        estop = Canvas()                                    # the emergency stop on the bench's end
        ex = box[2] - 12 * bk if a < 0 else box[0] + 12 * bk
        estop.add(f'<rect x="{n(ex - 8 * bk)}" y="{n(b["top"] - 8 * bk)}" width="{n(16 * bk)}" height="{n(8 * bk)}" '
                  f'fill="{YELLOW}" stroke="{INK}" stroke-width="1"/><circle cx="{n(ex)}" cy="{n(b["top"] - 11 * bk)}" '
                  f'r="{n(6 * bk)}" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>')
        s.put(r.feet - 0.9, estop.render(), None, group="bench")
        sparrow_on(s, ex, b["top"] - 17 * bk, "bench")


def safety_post(c: Canvas, x: float, foot: float, k: float) -> dict:
    """The safety shower and eyewash station standing at (x, foot), 90 wide and 170 tall: a yellow pipe column on
    its foot plate, the green shower head on its arm at the top with its pull rod and triangle handle, the eyewash
    bowl with its two nozzles at waist height, its push handle, the floor drain."""
    d = Canvas()
    d.shape(rounded_rect_d(-26, -6, 52, 6, 2), P.METAL_DARK, sw=1.2, light=None)
    d.shape(rounded_rect_d(-5, -166, 10, 160, 3), YELLOW, sw=1.6, light=(-1, -1))
    d.line("M0,-160 H34", 6, INK)
    d.line("M0,-160 H34", 4, YELLOW)
    d.shape("M18,-146 Q34,-164 50,-146 Z", P.GREEN, sw=1.6, light=None)                     # the shower head
    d.line("M40,-146 V-98", 1.6, P.METAL_DARK)
    d.shape("M33,-98 H47 L40,-86 Z", P.GREEN, sw=1.2, light=None)                            # its pull handle
    d.shape("M-40,-70 Q-24,-56 -8,-70 Z", P.GREEN, sw=1.4, light=None)                        # the eyewash bowl
    d.line("M-8,-66 H-4", 4, YELLOW)
    for nx_ in (-30, -18):
        d.shape(rounded_rect_d(nx_ - 3, -78, 6, 8, 2), YELLOW, sw=1.0, light=None)
    d.line("M-4,-48 h-14 v8", 2.4, P.METAL_DARK)                                             # its push handle
    d.add(f'<ellipse cx="22" cy="-2" rx="12" ry="3" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width=".8"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 42 * k, foot - 168 * k, x + 52 * k, foot), "handle": (x + 40 * k, foot - 98 * k)}


# ============================================================================ the finale
BAYS = ("cover", "testfirst", "migrations", "production", "linters", "hooks", "check", "safety")   # and the
                                                                          # safety post, in the last bay unnamed


def finale(s: Strip) -> None:
    """The whole lab at once: one long room along its tiled wall, each station in its bay - the racks, the
    indicator, the still, the stress chamber, the microscope, the analyzer with its hatch, the analyzer catching
    the broken sample - each bay's name on a plate over it; the cast at work in front."""
    ledger(s)
    zoom(s)
    backdrop(s, 3)
    r = lane(s)
    left, right = s.lo, s.hi
    rows = 2 if s.h >= 400 else 1
    per = math.ceil(len(BAYS) / rows)
    wide = (right - left) / per
    named = s.h >= 300
    size = 11.0
    widest = max(tag_size(s.word(key), size)[0] for key in BAYS if key != "safety")
    if widest > wide - 20:
        size = max(sets.LETTERING_MIN + 1, size * (wide - 20) / widest)
    th = tag_size("Ag", size)[1]
    stagger = rows == 1 and widest > wide - 20                         # names too wide for one row: two rows
    head = 8 + ((th + 6) * (2 if stagger else 1) + 4 if named else 0)
    floors = [r.feet] if rows == 1 else [r.feet - (r.feet - 6) / 2 - 4, r.feet]
    things = Canvas()
    shelf = Canvas()
    pen = Pen(s, 0, 0, 1)
    tops = []
    for d_, floor in enumerate(floors):
        ceil = floors[d_ - 1] + 8 if d_ else 6.0
        if d_:                                                         # the gallery between the two rows
            shelf.add(f'<rect x="{n(left - 4)}" y="{n(ceil - 10)}" width="{n(right - left + 8)}" height="12" '
                      f'fill="{CAB}" stroke="{INK}" stroke-width="1.4"/>')
        room = floor - ceil - head - 4
        for i in range(per):
            idx = d_ * per + i
            if idx >= len(BAYS):
                break
            key = BAYS[idx]
            x = left + wide * (i + 0.5)
            fit = wide * 0.86
            if key == "cover":
                k = min(fit / 248, room / 100)
                b = lab_bench(things, x, floor, k, 240)
                for q in range(3):
                    rack(things, x - 76 * k + q * 76 * k, b["top"], k * 0.95, 8 - q, seed=q)
                tops.append(b["top"] - 36 * k)
            elif key == "testfirst":
                k = min(fit / 170, room / 172)
                tops.append(indicator(things, x, floor, k, P.GREEN, 4, False)["box"][1])
            elif key == "migrations":
                k = min(fit / 240, room / 160)
                tops.append(still(things, x, floor, k, True, False)["box"][1])
            elif key == "production":
                k = min(fit / 132, room / 183)
                tops.append(stress_chamber(things, x, floor, k, True)["box"][1])
            elif key == "linters":
                k = min(fit / 170, room / 124)
                b = lab_bench(things, x, floor, k, 170)
                microscope(things, x - 34 * k, b["top"], k * 1.5)
                rack(things, x + 44 * k, b["top"], k, 4, slots=5, seed=7)
                tops.append(b["top"] - 70 * k)
            elif key == "safety":
                k = min(fit / 94, room / 168)
                tops.append(safety_post(things, x, floor, k)["box"][1])
            else:
                k = min(fit / 180, room / 168)
                b = lab_bench(things, x, floor, k, 180)
                an = analyzer(things, x, b["top"], k * 1.2, "green" if key == "hooks" else "red", 24,
                              "green" if key == "hooks" else "orange")
                tops.append(an["box"][1])
            if named and key != "safety":
                ty = ceil + 4 + th / 2 + 4 + ((th + 6) * (i % 2) if stagger else 0)
                holder = pen.tag(f"label{key}", x, ty, s.word(key), size, YELLOW, INK)
                s.put(2, "", holder.outer, f"label{key}")
    s.put(0.9, shelf.render(), None)
    s.put(1.2, things.render(), None)
    cast_ = {0: ("caterpillar", "present"), 2: ("cat", "present"), 4: ("agent", "point"), 5: ("professor", "think")}
    for i, (name, pose) in cast_.items():
        d_, j = divmod(i, per)
        floor = floors[min(d_, len(floors) - 1)]
        ceil = floors[d_ - 1] + 8 if d_ and rows == 2 else 6.0
        x = left + wide * (j + 0.88)
        tall = min(s.tall * SIZE[name] * 1.4, _fit_tall(name, wide * 0.32, floor - ceil - head - 6))
        who = s.actor(name, min(x, s.hi - 30), floor, pose, "smile", flip=True, tall=tall, group=f"f{i}")
        if name == "cat":
            held(s, who, handheld.stopwatch)
        elif name == "caterpillar":
            held(s, who, handheld.clipboard)
    if named:
        s.put(2, pen.svg(), None)


# ============================================================================ the opener
def apparatus(c: Canvas, x: float, foot: float, k: float, col: float = 240) -> dict:
    """The hero: a tall glass apparatus on its own bench at (x, foot), 300 wide and 470 tall - two round flasks of
    coloured liquids boiling on lit burners, held in the clamps of a tall retort stand, their vapour rising
    through a fractionating column with its glass coils into a long slanting condenser, and down into a receiving
    flask, a drop falling into it; steam curling off the top. `col`: the column's length. Returns its parts."""
    b = lab_bench(c, x, foot, k, 300)
    top = b["top"]
    ring_stand(c, x - 120 * k, top, k, (180 + col) * k, [top - 92 * k, top - (150 + col * 0.25) * k,
                                                          top - (150 + col * 0.8) * k],
               reaches=[40, 75, 75], grip=24)                                         # the neck, the column
    for fx, liq in ((x - 80 * k, LIQUID["violet"]), (x - 10 * k, LIQUID["orange"])):
        burner(c, fx, top, k * 1.2)
        flask(c, fx, top - 46 * k, k * 1.3, liq, 0.6, round_=True)
        c.add("".join(f'<circle cx="{n(fx + (q - 1) * 6 * k)}" cy="{n(top - 70 * k - q * 8 * k)}" r="{n(2.4 * k)}" '
                      f'fill="{P.WHITE}" fill-opacity=".85"/>' for q in range(3)))           # they boil
    col_x = x - 45 * k                                                                   # the column
    c.add(f'<path d="M{n(x - 80 * k)},{n(top - 106 * k)} V{n(top - 140 * k)} H{n(x - 10 * k)} V{n(top - 106 * k)}" '
          f'fill="none" stroke="{INK}" stroke-width="{n(8 * k)}"/><path d="M{n(x - 80 * k)},{n(top - 106 * k)} '
          f'V{n(top - 140 * k)} H{n(x - 10 * k)} V{n(top - 106 * k)}" fill="none" stroke="{GLASS}" '
          f'stroke-width="{n(5.6 * k)}"/>')
    c.add(f'<rect x="{n(col_x - 12 * k)}" y="{n(top - (140 + col) * k)}" width="{n(24 * k)}" '
          f'height="{n(col * k)}" '
          f'rx="{n(10 * k)}" fill="{GLASS}" stroke="{INK}" stroke-width="{n(1.8 * k)}"/>')
    turn_ = f"q{n(10 * k)},{n(-6 * k)} 0,{n(-12 * k)} q{n(-10 * k)},{n(-6 * k)} 0,{n(-12 * k)}"
    c.add(f'<path d="M{n(col_x)},{n(top - 146 * k)} ' + " ".join(turn_ for _ in range(int(col / 26))) +
          f'" fill="none" stroke="{LIQUID["blue"]}" stroke-width="{n(2.2 * k)}"/>')       # its packing coil
    for q in range(int(col / 60)):                                                       # vapour rising in it
        c.add(f'<circle cx="{n(col_x + (q % 2 - 0.5) * 6 * k)}" cy="{n(top - 170 * k - q * 48 * k)}" '
              f'r="{n(2 * k)}" fill="{P.WHITE}"/>')
    hx, hy = col_x, top - (146 + col) * k                                                # the head, to the side
    c.add(f'<path d="M{n(hx)},{n(top - (140 + col) * k)} V{n(hy)} H{n(hx + 30 * k)}" fill="none" stroke="{INK}" '
          f'stroke-width="{n(8 * k)}"/><path d="M{n(hx)},{n(top - (140 + col) * k)} V{n(hy)} H{n(hx + 30 * k)}" '
          f'fill="none" stroke="{GLASS}" stroke-width="{n(5.6 * k)}"/>')
    c.add(f'<rect x="{n(hx - 4 * k)}" y="{n(hy - 18 * k)}" width="{n(8 * k)}" height="{n(14 * k)}" fill="{P.METAL}" '
          f'stroke="{INK}" stroke-width="{n(k)}"/>')                                     # its thermometer cap
    cx0, cy0 = hx + 30 * k, hy
    cx1, cy1 = x + 120 * k, top - 120 * k                                                # the condenser
    ang = math.degrees(math.atan2(cy1 - cy0, cx1 - cx0))
    length = math.hypot(cx1 - cx0, cy1 - cy0)
    g = Canvas()
    g.add(f'<rect x="0" y="{n(-11 * k)}" width="{n(length)}" height="{n(22 * k)}" rx="{n(10 * k)}" fill="{GLASS}" '
          f'stroke="{INK}" stroke-width="{n(1.8 * k)}"/>')
    wave = f"q{n(6 * k)},{n(-9 * k)} {n(12 * k)},0 q{n(6 * k)},{n(9 * k)} {n(12 * k)},0"
    g.add(f'<path d="M{n(10 * k)},0 ' + " ".join(wave for _ in range(int((length - 20 * k) / (24 * k)))) +
          f'" fill="none" stroke="{LIQUID["blue"]}" stroke-width="{n(2 * k)}"/>')
    for px in (16 * k, length - 22 * k):                                                 # its water nozzles
        g.add(f'<rect x="{n(px)}" y="{n(-18 * k)}" width="{n(6 * k)}" height="{n(8 * k)}" fill="{GLASS}" '
              f'stroke="{INK}" stroke-width="{n(k)}"/>')
    c.add(f'<g transform="translate({n(cx0)},{n(cy0)}) rotate({n(ang)})">{g.render()}</g>')
    a = math.radians(ang)
    far_ = length - 19 * k                                                              # the lower nozzle's mouth
    nozzle = (cx0 + math.cos(a) * far_ + math.sin(a) * 18 * k, cy0 + math.sin(a) * far_ - math.cos(a) * 18 * k)
    ring_stand(c, x + 140 * k, top, k, 150 * k, [top - 112 * k], reach=-26)
    rx = cx1 + 4 * k                                                                    # the receiving flask
    flask(c, rx, top, k * 1.2, LIQUID["green"], 0.4)
    c.add(f'<path d="M{n(rx)},{n(top - 74 * k)} q{n(3 * k)},{n(4 * k)} 0,{n(6 * k)} q{n(-3 * k)},{n(-2 * k)} 0,'
          f'{n(-6 * k)} Z" fill="{LIQUID["green"]}" stroke="{INK}" stroke-width="{n(0.8 * k)}"/>')   # a drop
    c.add(motion(rx - 6 * k, top - 82 * k, 10, k * 0.5, way=-1, vertical=True))
    for q in range(3):                                                                   # steam curling up
        c.add(f'<path d="M{n(hx - 6 * k + q * 8 * k)},{n(hy - 24 * k)} q{n(-8 * k)},{n(-14 * k)} 0,{n(-26 * k)} '
              f'q{n(8 * k)},{n(-12 * k)} 0,{n(-26 * k)}" fill="none" stroke="{P.WHITE}" stroke-width="{n(3 * k)}" '
              f'stroke-linecap="round" stroke-opacity=".85"/>')
    return {"box": (x - 156 * k, hy - 80 * k, x + 160 * k, foot), "nozzle": nozzle, "bench": b["box"],
            "out": (math.sin(a), -math.cos(a)),
            "funnel": (col_x, top - (140 + col) * k),
            "side": (x - 80 * k - 18 * 1.3 * k, top - 46 * k - 34 * 1.3 * k)}


def funnel(c: Canvas, x: float, y: float, k: float, foot: float) -> tuple[float, float]:
    """A glass funnel in the ring of its own small stand, its mouth's middle at (x, y): the cone and its stem,
    bent to the right at its foot into a hose nozzle; the ring on its arm from the stand's rod, the rod down to
    the heavy foot standing at `foot`. Returns the nozzle's mouth."""
    c.add(f'<rect x="{n(x - 30 * k)}" y="{n(foot - 6 * k)}" width="{n(40 * k)}" height="{n(6 * k)}" rx="{n(1.5 * k)}" '
          f'fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="{n(max(0.8, k))}"/>')
    c.add(f'<rect x="{n(x - 26 * k)}" y="{n(y - 10 * k)}" width="{n(3.6 * k)}" height="{n(foot - y + 4 * k)}" '
          f'fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="{n(max(0.6, 0.8 * k))}"/>')    # its rod
    c.line(f"M{n(x - 24 * k)},{n(y + 6 * k)} H{n(x - 8 * k)}", 2.4 * k, P.METAL)
    c.add(f'<ellipse cx="{n(x)}" cy="{n(y + 7 * k)}" rx="{n(9 * k)}" ry="{n(2.6 * k)}" fill="none" '
          f'stroke="{P.METAL_DARK}" stroke-width="{n(2 * k)}"/>')                            # its ring
    c.add(f'<path d="M{n(x - 16 * k)},{n(y)} H{n(x + 16 * k)} L{n(x + 3 * k)},{n(y + 16 * k)} V{n(y + 26 * k)} '
          f'H{n(x + 10 * k)} V{n(y + 32 * k)} H{n(x - 3 * k)} V{n(y + 16 * k)} Z" fill="{GLASS}" stroke="{INK}" '
          f'stroke-width="{n(1.4 * k)}"/>')                                                  # cone, stem, nozzle
    c.add(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(16 * k)}" ry="{n(3 * k)}" fill="{LIQUID["green"]}" '
          f'stroke="{INK}" stroke-width="{n(k)}"/>')
    return x + 10 * k, y + 29 * k


def opener(st: Stage, accent: str):
    """The laboratory in warm yellow, one hero: a big glass apparatus on its yellow bench - two round flasks of
    violet and orange liquid bubbling on burners with blue flames, a packed column, a fat coiled condenser
    slanting down to the receiving flask that fills drop by drop with green, steam curling off the head - and in
    front of it on the floor a funnel on its stand, its red hose running up into the first flask. The wall of
    yellow tiles over a band of deeper ones, a window with sky high on the left, a big pendant lamp throwing warm
    light, a shelf of coloured reagent bottles; the title over the calm wall. On the floor the cast: the professor
    under his bubble, the agent pouring a beaker of green reagent into the funnel, the caterpillar with her
    clipboard a step back, the cat timing the reaction, the sparrow on the window sill."""
    ledger(st)
    c = st.back
    floor = 1000.0
    k, ax, col = 1.45, 600.0, 150.0
    band = 742.0
    tiles(c, -6, W + 6, -6, band, 34, TILE)
    tiles(c, -6, W + 6, band, floor, 34, TILE_Y)
    c.add(f'<rect x="-6" y="{band - 6}" width="{W + 12}" height="12" fill="{CAB}" stroke="{INK}" '
          f'stroke-width="1.6"/>')                                                          # the tiles' border
    c.add(f'<path d="M0,0 H{W} V{floor} H0 Z" fill="{YELLOW}" fill-opacity=".14"/>')       # warm light all over
    floor_tiles(c, -6, W + 6, floor, H + 4, 1.8)
    c.add(f'<rect x="-6" y="{floor - 6}" width="{W + 12}" height="10" fill="{darken(CAB, 0.75)}" stroke="{INK}" '
          f'stroke-width="1.4"/>')
    prof = st.actor("professor", 140, 1100, "explain", "talk", tall=360)
    st.speaker(prof, width=74, left=8, air=CLEAR_MM)
    st.keep_clear((-6, band - 8, W + 6, band + 8))                                       # the tiles' border
    win = (56.0, 280.0, 296.0, 376.0)                                                    # a window high on the left
    c.add(f'<rect x="{win[0]}" y="{win[1]}" width="{win[2] - win[0]}" height="{win[3] - win[1]}" '
          f'fill="{lighten(P.SKY, 0.1)}" stroke="{P.WHITE}" stroke-width="10"/><rect x="{win[0] - 5}" '
          f'y="{win[1] - 5}" width="{win[2] - win[0] + 10}" height="{win[3] - win[1] + 10}" fill="none" '
          f'stroke="{INK}" stroke-width="1.6"/>')
    c.add(f'<path d="M{win[0] + 30},{win[1] + 30} q20,-14 40,0 q16,-10 30,2 H{win[0] + 30} Z" fill="{P.WHITE}"/>')
    c.line(f"M{(win[0] + win[2]) / 2},{win[1]} V{win[3]} M{win[0]},{(win[1] + win[3]) / 2} H{win[2]}", 5, P.WHITE)
    c.add(f'<rect x="{win[0] - 12}" y="{win[3] + 5}" width="{win[2] - win[0] + 24}" height="9" '
          f'fill="{CAB}" stroke="{INK}" stroke-width="1.4"/>')                             # its sill
    st.put(0.3, "", (win[0] - 12, win[1] - 6, win[2] + 12, win[3] + 14), "window", group="window")
    lx_ = 770.0                                                                          # the pendant lamp
    c.line(f"M{lx_},-6 V158", 3, INK)
    c.add(f'<path d="M{lx_ - 6},150 H{lx_ + 6} V162 H{lx_ - 6} Z" fill="{P.METAL_DARK}"/>'
          f'<path d="M{lx_ - 46},202 Q{lx_},140 {lx_ + 46},202 Z" fill="{CAB}" stroke="{INK}" stroke-width="2"/>')
    c.add(f'<path d="M{lx_ - 44},204 L{lx_ - 150},520 H{lx_ + 70} L{lx_ + 44},204 Z" fill="{P.YELLOW_PALE}" '
          f'fill-opacity=".35"/>')                                                          # its warm light
    glow(c, lx_, 206, 10)
    st.put(0.3, "", (lx_ - 48, 140, lx_ + 48, 216), "lamp")
    shelves = Canvas()                                                                   # the bottle shelf
    x = 700.0
    rnd = random.Random(2)
    while x < 826:
        bottle(shelves, x, 320, 1.7, rnd.choice(list(LIQUID.values())), rnd.randrange(3))
        x += rnd.uniform(28, 34)
    shelves.add(f'<rect x="684" y="320" width="152" height="8" fill="{CAB}" stroke="{INK}" stroke-width="1.4"/>'
                f'<path d="M694,328 l-6,12 M824,328 l6,12" stroke="{P.METAL_DARK}" stroke-width="3"/>')
    st.put(0.4, shelves.render(), (682, 262, 838, 342), "shelves", group="shelves")
    parts = apparatus(c, ax, floor, k, col)
    st.put(0.5, "", parts["box"], "apparatus", group="apparatus", backdrop=True)
    st.keep_clear(parts["box"])
    agent = st.actor("agent", 350, 1124, "present", "smile", flip=False, tall=380, group="agent")
    gx, gy, _ = st.grip(agent, "right")
    fx, fy = gx + 26, gy + 18                                                            # the funnel, in reach
    fun = Canvas()
    nzx, nzy = funnel(fun, fx, fy, 1.5, 1112)
    st.put(1060, fun.render(), (fx - 46, fy - 6, fx + 26, 1112), "funnel", group="agent")
    st.hold(agent, beaker, turn=-20)
    px_, py_ = ax - 80 * k - 20 * k, floor - 66 * k - 46 * k - 14 * k                      # the bulb's lower left
    connect(st, port(st, nzx, nzy, 1, 0, "funnel"), port(st, px_, py_, 0, 1, "apparatus"), "tube", 6,
            color=P.RED, depth=1000.5, lead=(56, 40))
    caterp = st.actor("caterpillar", 770, 1092, "present", "worry", flip=True, tall=270, group="caterpillar")
    st.hold(caterp, handheld.clipboard)
    cat = st.actor("cat", 624, 1130, "present", "smile", flip=True, tall=300, group="cat")
    st.hold(cat, handheld.stopwatch)
    st.actor("sparrow", 250, 382, "stand", "smile", tall=100, group="window")          # on the window sill
    drawn = st.render()
    drawn.holders, drawn.links, drawn.ports = st.holders, st.links, st.ports
    return drawn


LAB.stations.extend([
    Station("cover", _framed(cover_station), ("fill", "count")),
    Station("testfirst", _framed(testfirst_station), ("red", "green")),
    Station("migrations", _framed(migrations_station), ("move", "twostep")),
    Station("production", _framed(production_station), ("load", "crack")),
    Station("linters", _framed(linters_station), ("look", "label")),
    Station("hooks", _framed(hooks_station), ("edit", "commit")),
    Station("check", _framed(check_station), ("break", "catch")),
])
LAB.backdrop = backdrop
LAB.alternate = True                                       # never one moment on two pages in a row
LAB.finale = finale
stories.OPENERS["laboratory"] = opener
hide(LAB, "testfirst", "green")

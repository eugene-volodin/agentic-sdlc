"""The library: the world of chapter 4 (what to write down for the agent, and where).

The repository is a library and the agent a newcomer to it. Whatever it needs it must find quickly, and the
library is arranged so that it can: a short sheet on the door, the things needed daily on the desk by the door,
the rarer ones further back and the rarest high up, a sheet of its own at every aisle's end, a catalogue that
points to the books, an archive of decisions, notes stuck in the books at the very page. The camera walks in from
the door, station by station:

1. sheet      the professor pins the short sheet - AGENTS.md - on the library's door; then the agent reads it,
              the caterpillar asking if that is really all;
2. near       the desk by the door holds what is needed every day, the agent takes from it; then the far stacks,
              the agent up the rolling ladder for a rare book, the caterpillar holding the ladder;
3. aisles     every aisle has its own small sheet on a stand at its end; the agent reads it, the cat explains;
4. catalogue  the card catalogue: a drawer pulled out, its cards point to the books - the cat shows a card;
5. archive    the archive of decisions: a folder being filed, its tabs context, decision, rejected, consequences;
6. notes      a book on the lectern, open at the page, bookmarks and notes stuck in it right there;
7. sort       the sorting trolley: the agent sorts the returned notes into the trays - the door sheet, an
              aisle's sheet, the catalogue;
8. docs       the reference shelf of labelled binders;
9. check      the test: the agent finds the right book fast from the door sheet, the cat times it, the caterpillar
              checks it twice.

No name boards in the frames - only the finale names its stations. Words appear only where they belong to a thing:
the sheet's title, the folder's tabs, the binders' spines. It draws with the shared kit (`world_kit.py`) and the
fair's camera (`world_fair.zoom`): a station fills the frame's height, the floor in front is about a sixth of it.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten, mix
from . import handheld, sets
from .footers import Strip
from .ink import INK, Canvas, lettering, n, rounded_rect_d
from .openers import CLEAR_MM, H, OPENERS, W, Stage
from .world_fair import glow, held, inside, lane, mid, paving, turn, zoom
from .world_fair import stand as _stand
from .world_kit import (SIZE, Pen, clock_hands, floppy_size, hide, ledger, letter, motion, stash, tag_size, tome,
                        tome_size)
from .world_kitchen import _box, _fit_tall, perch, rules, rules_size
from .world_base import Station, world

LIBRARY = world("library", opener="reading_room")

_at = sets._at

WALL = mix(P.TEAL, P.CARD, 0.78)             # the plastered upper wall
PANEL = mix(P.TEAL, P.WOOD_DARK, 0.25)       # the wainscot panels below it
BOARDS = (mix(P.WOOD_LIGHT, P.WOOD, 0.35), mix(P.WOOD_LIGHT, P.WOOD_PALE, 0.5))    # the parquet's two tones
SPINES = (P.TEAL, P.RED, P.BLUE, darken(P.TEAL, 0.75), P.YELLOW, P.GREEN, P.WOOD, P.ORANGE, mix(P.TEAL, P.CARD, 0.4))


# ============================================================================ the room
def backdrop(s: Strip, index: int) -> None:
    """The library behind a station, in depth: a continuous back row of teal bookcases along the wall, full of
    books, the pale wall showing only as a strip under the cornice; now and then a bay without shelves - an arched
    window over panelling, or a framed map and a clock over panelling - with a sconce glowing between bays; the
    choice of bays turns with the frame so neighbours differ. The parquet floor in front."""
    ledger(s)
    zoom(s)
    c = s.back
    base = s.base
    c.add(f'<rect x="-6" y="-6" width="{W + 12}" height="{n(base + 8)}" fill="{WALL}"/>')
    k = max(0.55, min(1.4, base / 260))
    top = max(4.0, min(26 * k, base * 0.08))
    c.add(f'<rect x="-6" y="{n(top - 12 * k)}" width="{W + 12}" height="{n(8 * k)}" fill="{P.TEAL}" '
          f'stroke="{INK}" stroke-width="1.2"/>')                                       # the wall's cornice
    bay = 150 * k
    kinds = ("case", "case", "window", "case", "case", "clock")
    x = -bay * ((index * 0.37) % 1)
    i = index * 2
    rnd = random.Random(index)
    while x < W:
        kind = kinds[i % len(kinds)] if s.h >= 200 else "case"
        if kind == "case":
            bookcase(c, x + 3, x + bay - 3, top, base, k, seed=rnd.randrange(999), faded=True)
        else:
            _bay(c, x, x + bay, top, base, k, kind)
        if i % 3 == 1 and s.h >= 200:                                                   # a sconce on the post
            sx = x + bay
            c.shape(f"M{n(sx - 6 * k)},{n(top + 40 * k)} h{n(12 * k)} l{n(-3 * k)},{n(16 * k)} h{n(-6 * k)} Z",
                    P.SUN, sw=1.2, light=None)
            glow(c, sx, top + 50 * k, 4 * k)
        x += bay
        i += 1
    paving(c, -6, W + 6, base, s.h + 4, max(0.8, s.unit), seed=index + 3, tones=BOARDS)
    c.add(f'<rect x="-6" y="{n(base - 3)}" width="{W + 12}" height="7" fill="{P.WOOD_DARK}" stroke="{INK}" '
          f'stroke-width="1.2"/>')                                                      # the skirting board


def scenery(s: Strip) -> None:
    """Nothing is added behind a station once it is placed: the bays carry no loose things of their own."""
    del s


def _bay(c: Canvas, x0: float, x1: float, top: float, foot: float, k: float, kind: str) -> None:
    """A bay of the wall without shelves: real panelling below - framed panels with their mouldings and shade -
    and above it an arched window onto the sky, or a big wall clock with its numerals."""
    dado = foot - (foot - top) * 0.38
    c.add(f'<rect x="{n(x0)}" y="{n(dado)}" width="{n(x1 - x0)}" height="{n(foot - dado)}" fill="{PANEL}"/>')
    pw = (x1 - x0 - 18 * k) / 2
    for j in range(2):
        px = x0 + 6 * k + j * (pw + 6 * k)
        c.add(f'<rect x="{n(px)}" y="{n(dado + 8 * k)}" width="{n(pw)}" height="{n(foot - dado - 16 * k)}" '
              f'rx="{n(2 * k)}" fill="{lighten(PANEL, 0.18)}" stroke="{darken(PANEL, 0.7)}" '
              f'stroke-width="{n(1.4 * k)}"/>')
        c.add(f'<rect x="{n(px + 5 * k)}" y="{n(dado + 13 * k)}" width="{n(pw - 10 * k)}" '
              f'height="{n(foot - dado - 26 * k)}" fill="none" stroke="{lighten(PANEL, 0.4)}" '
              f'stroke-width="{n(1.2 * k)}"/>')
    c.add(f'<rect x="{n(x0)}" y="{n(dado - 6 * k)}" width="{n(x1 - x0)}" height="{n(6 * k)}" fill="{P.TEAL}" '
          f'stroke="{INK}" stroke-width="1.2"/>')                                        # the dado rail
    cx = (x0 + x1) / 2
    room = dado - top - 18 * k
    if room < 30 * k or kind == "panel":
        return
    if kind == "window":
        ww = min(x1 - x0 - 30 * k, room * 0.7)
        wt = top + 10 * k
        r = ww / 2
        arch = (f"M{n(cx - r)},{n(dado - 10 * k)} V{n(wt + r)} A{n(r)},{n(r)} 0 0 1 {n(cx + r)},{n(wt + r)} "
                f"V{n(dado - 10 * k)} Z")
        c.add(f'<path d="{arch}" fill="{lighten(P.SKY, 0.15)}" stroke="{P.TEAL}" stroke-width="{n(8 * k)}"/>')
        c.add(f'<path d="{arch}" fill="none" stroke="{INK}" stroke-width="1.6"/>')
        c.line(f"M{n(cx)},{n(wt)} V{n(dado - 10 * k)} M{n(cx - r)},{n((wt + r + dado) / 2)} H{n(cx + r)}",
               3 * k, P.TEAL)
        return
    cr = min(32 * k, room * 0.3)                                 # the wall clock, its numerals
    cy = top + 14 * k + cr
    c.add(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(cr)}" fill="{P.CARD}" stroke="{P.WOOD_DARK}" '
          f'stroke-width="{n(4 * k)}"/><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(cr + 2 * k)}" fill="none" '
          f'stroke="{INK}" stroke-width="1.2"/>')
    for num, ang in (("12", -90), ("3", 0), ("6", 90), ("9", 180)):
        a = math.radians(ang)
        size = max(5.0, cr * 0.32)
        c.add(lettering(cx + math.cos(a) * cr * 0.72, cy + math.sin(a) * cr * 0.72 + size * 0.36, num, size, INK,
                        style="plain"))
    c.add(clock_hands(cx, cy, cr * 0.46, cr * 0.64, 2 * k))


def ph(s: Strip) -> float:
    """How tall the professor stands in this frame: the measure every station is built to."""
    r = lane(s)
    if s.h < 200:                                         # a close-up: the cast stands as tall as the strip
        return r.feet - 6
    box = _box(s, "professor", 0, r.feet)
    return box[3] - box[1]


def _framed(draw):
    def run(s: Strip, beat: str) -> None:
        turn(s)
        draw(s, beat)
        scenery(s)
    return run


def sparrow(s: Strip, x: float, top: float, pose: str = "stand"):
    """The sparrow on something a bird sits on - its feet on `top` at x - as big as there is room for."""
    for scale in (0.45, 0.36, 0.28, 0.22):
        bird = perch(s, "sparrow", x, top, pose, "smile", scale=scale)
        if bird:
            return bird
    return None                                       # no room: better no sparrow than one in front of the thing


def span(s: Strip, share: float) -> float:
    """That share of the frame's usable width: a station never takes so much that its cast has no room."""
    return (s.hi - s.lo) * share * (0.78 if s.h >= 400 else 1.0)   # a tall frame's cast is wide: leave it room


def stand(s: Strip, name: str, fracs: float | tuple[float, ...], pose: str, mood: str = "smile",
          flip: bool = True, mark: str | None = None):
    """A character at the first of `fracs` where it finds room - and failing those, at the nearest free spot
    anywhere along the floor, so that a frame of another size keeps its cast."""
    first = fracs if isinstance(fracs, tuple) else (fracs,)
    probe = _box(s, name, 0, lane(s).feet)
    half = (probe[2] - probe[0]) / 2                       # the sweep keeps the whole character inside the frame
    sweep = sorted((f for f in (i / 40 for i in range(41)) if half <= s.x(f) <= W - half),
                   key=lambda f: abs(f - first[0]))
    writing = name == "caterpillar" and pose == "write"   # she checks things off on one clipboard, held in her fist
    who = _stand(s, name, (*first, *sweep), "present" if writing else pose, mood, flip=flip, mark=mark)
    if writing:
        held(s, who, handheld.clipboard)
    return who


# ============================================================================ things
def books(c: Canvas, x0: float, x1: float, base: float, tall: float, k: float, rnd: random.Random,
          faded: bool = False) -> None:
    """A row of books standing on a shelf from x0 to x1, their foot on `base`, up to `tall` high: spines of
    varied widths, heights and colours, a band across each, now and then one leaning on its neighbour."""
    x = x0 + 2
    while x < x1 - 6 * k:
        w = min(rnd.uniform(6, 13) * k, x1 - x - 2)
        if w < 4 * k:
            break
        h = tall * rnd.uniform(0.72, 0.98)
        color = SPINES[rnd.randrange(len(SPINES))]
        if faded:
            color = mix(color, WALL, 0.58)
        lw = max(0.8, 1.2 * k)
        if rnd.random() < 0.08 and x1 - x > w * 3:                                     # one leaning over
            c.add(f'<path d="M{n(x)},{n(base)} L{n(x + w)},{n(base)} L{n(x + w + h * 0.35)},{n(base - h * 0.94)} '
                  f'L{n(x + h * 0.35)},{n(base - h * 0.94)} Z" fill="{color}" stroke="{INK}" stroke-width="{n(lw)}"/>')
            x += w + h * 0.38 + 2
            continue
        c.add(f'<rect x="{n(x)}" y="{n(base - h)}" width="{n(w)}" height="{n(h)}" rx="{n(1.2 * k)}" fill="{color}" '
              f'stroke="{INK}" stroke-width="{n(lw)}"/>')
        band = lighten(color, 0.45)
        if w > 3:                                                             # a band, where the spine has room
            c.add(f'<rect x="{n(x + 1)}" y="{n(base - h * 0.78)}" width="{n(w - 2)}" height="{n(max(1.0, 2 * k))}" '
                  f'fill="{band}"/>')
        x += w + max(0.6, 0.8 * k)


def bookcase(c: Canvas, x0: float, x1: float, top: float, foot: float, k: float, seed: int = 0,
             faded: bool = False, shelves: int | None = None, paint: str = P.TEAL, nook: float = 0.0,
             tail: float = 0.0) -> list[float]:
    """A tall bookcase from x0 to x1, painted (`paint`, the library's teal), its cornice at `top` and its plinth on
    `foot`: two sides, a cornice, shelf boards, every shelf full of books - a few gaps, now and then one leaning.
    `nook` keeps that much free at the right end of the middle shelf (for the golden floppy), `tail` at the right end
    of the bottom shelf (for a book lying there). Returns the shelves' tops (where books stand), top to bottom."""
    rnd = random.Random(seed)
    wood = mix(paint, WALL, 0.35) if faded else paint
    back = mix(darken(paint, 0.5), WALL, 0.45) if faded else darken(paint, 0.5)
    side = max(4.0, 7 * k)
    c.add(f'<rect x="{n(x0)}" y="{n(top)}" width="{n(x1 - x0)}" height="{n(foot - top)}" fill="{back}"/>')
    inner = foot - top - 22 * k
    count = shelves or max(2, round(inner / (46 * k)))
    gap = inner / count
    tops = []
    for i in range(count):
        y = top + 12 * k + gap * (i + 1)
        if nook and i == count // 2:
            books(c, x0 + side, x1 - side - nook, y, gap - 7 * k, k, rnd, faded)
        elif tail and i == count - 1:
            books(c, x0 + side, x1 - side - tail, y, gap - 7 * k, k, rnd, faded)
        elif rnd.random() < 0.25:                                     # a gap on this shelf
            mid_x = x0 + side + (x1 - x0 - 2 * side) * rnd.uniform(0.3, 0.6)
            books(c, x0 + side, mid_x, y, gap - 7 * k, k, rnd, faded)
            books(c, mid_x + 24 * k, x1 - side, y, gap - 7 * k, k, rnd, faded)
            if not faded:                                             # an open book left face-down in the gap
                c.add(f'<path d="M{n(mid_x + 2 * k)},{n(y)} L{n(mid_x + 12 * k)},{n(y - 9 * k)} '
                      f'L{n(mid_x + 22 * k)},{n(y)} Z" fill="{P.RED}" stroke="{INK}" stroke-width="{n(k)}"/>')
        else:
            books(c, x0 + side, x1 - side, y, gap - 7 * k, k, rnd, faded)
        c.add(f'<rect x="{n(x0)}" y="{n(y)}" width="{n(x1 - x0)}" height="{n(4 * k)}" fill="{wood}" '
              f'stroke="{INK}" stroke-width="{n(max(0.8, 1.1 * k))}"/>')
        tops.append(y)
    for sx in (x0, x1 - side):
        c.add(f'<rect x="{n(sx)}" y="{n(top)}" width="{n(side)}" height="{n(foot - top)}" fill="{wood}" '
              f'stroke="{INK}" stroke-width="{n(max(1.0, 1.4 * k))}"/>')
    c.add(f'<rect x="{n(x0 - 4 * k)}" y="{n(top - 4 * k)}" width="{n(x1 - x0 + 8 * k)}" height="{n(14 * k)}" '
          f'rx="{n(2 * k)}" fill="{wood}" stroke="{INK}" stroke-width="{n(max(1.0, 1.6 * k))}"/>')   # the cornice
    c.add(f'<rect x="{n(x0 - 2 * k)}" y="{n(foot - 8 * k)}" width="{n(x1 - x0 + 4 * k)}" height="{n(8 * k)}" '
          f'fill="{darken(wood, 0.8)}" stroke="{INK}" stroke-width="{n(max(1.0, 1.4 * k))}"/>')    # the plinth
    return tops


def ladder(c: Canvas, top_x: float, top_y: float, foot_x: float, foot_y: float, k: float, rail: tuple | None = None,
           rolling: bool = False) -> None:
    """A library's rolling ladder seen from the front: two parallel wooden stiles from the brass rail at (top_x,
    top_y) down to the floor at (foot_x, foot_y), flat treads between them, level; at the top each stile hooks
    over the rail with a little brass roller sitting on it, and its end rises into a curved handrail; at the foot a
    castor wheel in its fork under each stile. `rail` (x0, x1) draws the rail along the bookcase, on its brackets;
    `rolling` adds motion lines behind the castors."""
    lw = max(1.0, 1.2 * k)
    if rail:
        c.add(f'<rect x="{n(rail[0])}" y="{n(top_y - 2.5 * k)}" width="{n(rail[1] - rail[0])}" '
              f'height="{n(5 * k)}" rx="{n(2.5 * k)}" fill="{P.SUN}" stroke="{INK}" stroke-width="{n(lw)}"/>')
        for bx in (rail[0] + 8 * k, rail[1] - 8 * k):                                   # the rail's brackets
            c.add(f'<rect x="{n(bx - 2 * k)}" y="{n(top_y - 2 * k)}" width="{n(4 * k)}" height="{n(10 * k)}" '
                  f'fill="{darken(P.SUN, 0.7)}" stroke="{INK}" stroke-width="{n(0.8 * k)}"/>')
    half = 16 * k
    sw = 6 * k
    base = foot_y - 14 * k                                                       # the stiles end over the castors
    for side in (-1, 1):
        ax, bx = top_x + side * half, foot_x + side * half
        c.add(f'<path d="M{n(ax)},{n(top_y - 16 * k)} L{n(bx)},{n(base)}" stroke="{INK}" '
              f'stroke-width="{n(sw + 2.4)}" stroke-linecap="round"/><path d="M{n(ax)},{n(top_y - 16 * k)} '
              f'L{n(bx)},{n(base)}" stroke="{P.WOOD}" stroke-width="{n(sw)}" stroke-linecap="round"/>')
        c.add(f'<path d="M{n(ax)},{n(top_y - 16 * k)} q{n(side * 10 * k)},{n(-4 * k)} {n(side * 8 * k)},'
              f'{n(12 * k)}" fill="none" stroke="{INK}" stroke-width="{n(4.4 * k)}" stroke-linecap="round"/>'
              f'<path d="M{n(ax)},{n(top_y - 16 * k)} q{n(side * 10 * k)},{n(-4 * k)} {n(side * 8 * k)},'
              f'{n(12 * k)}" fill="none" stroke="{P.WOOD_LIGHT}" stroke-width="{n(2.6 * k)}" '
              f'stroke-linecap="round"/>')                                                # its handrail
        c.add(f'<path d="M{n(ax - side * 1 * k)},{n(top_y + 6 * k)} q{n(-side * 2 * k)},{n(-12 * k)} '
              f'{n(-side * 8 * k)},{n(-10 * k)}" fill="none" stroke="{P.METAL_DARK}" stroke-width="{n(2.6 * k)}"/>'
              f'<circle cx="{n(ax - side * 7 * k)}" cy="{n(top_y - 5.5 * k)}" r="{n(3 * k)}" fill="{P.SUN}" '
              f'stroke="{INK}" stroke-width="{n(0.8 * k)}"/>')                         # its hook and roller
        c.add(f'<path d="M{n(bx - 4 * k)},{n(base)} L{n(bx - 3 * k)},{n(foot_y - 8 * k)} M{n(bx + 4 * k)},'
              f'{n(base)} L{n(bx + 3 * k)},{n(foot_y - 8 * k)}" stroke="{P.METAL_DARK}" '
              f'stroke-width="{n(1.8 * k)}"/><circle cx="{n(bx)}" cy="{n(foot_y - 5 * k)}" r="{n(5 * k)}" '
              f'fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="{n(k)}"/><circle cx="{n(bx)}" '
              f'cy="{n(foot_y - 5 * k)}" r="{n(1.8 * k)}" fill="{P.METAL}"/>')            # its castor
    steps = max(2, int((base - top_y - 10 * k) / (26 * k)))
    for i in range(1, steps + 1):                                                  # the treads, level
        t = i / (steps + 0.4)
        y = top_y + (base - top_y) * t
        xl = top_x + (foot_x - top_x) * t - half
        c.add(f'<rect x="{n(xl - 1 * k)}" y="{n(y - 3 * k)}" width="{n(2 * half + 2 * k)}" height="{n(5 * k)}" '
              f'rx="{n(1 * k)}" fill="{P.WOOD_LIGHT}" stroke="{INK}" stroke-width="{n(lw)}"/>'
              f'<rect x="{n(xl)}" y="{n(y - 3 * k)}" width="{n(2 * half)}" height="{n(1.6 * k)}" '
              f'fill="{lighten(P.WOOD_LIGHT, 0.3)}"/>')
    if rolling:
        c.add(motion(foot_x - half - 10 * k, foot_y - 6 * k, 30, k))


def door(c: Canvas, x: float, foot: float, k: float) -> tuple[float, float, float, float]:
    """The library's front door, its foot's middle at (x, foot), 110 wide and 200 tall: an arched frame, two
    panelled leaves, brass handles. Returns where a sheet hangs on it: (left, top, right, bottom) of its upper
    panel."""
    w, h = 110 * k, 200 * k
    arch = (f"M{n(x - w / 2)},{n(foot)} V{n(foot - h + w / 2)} A{n(w / 2)},{n(w / 2)} 0 0 1 {n(x + w / 2)},"
            f"{n(foot - h + w / 2)} V{n(foot)} Z")
    c.add(f'<path d="{arch}" fill="{P.WOOD_DARK}" stroke="{INK}" stroke-width="{n(2 * k)}"/>')
    inner = (f"M{n(x - w / 2 + 8 * k)},{n(foot)} V{n(foot - h + w / 2)} A{n(w / 2 - 8 * k)},{n(w / 2 - 8 * k)} 0 0 1 "
             f"{n(x + w / 2 - 8 * k)},{n(foot - h + w / 2)} V{n(foot)} Z")
    c.add(f'<path d="{inner}" fill="{P.WOOD}" stroke="{INK}" stroke-width="{n(1.4 * k)}"/>')
    c.line(f"M{n(x)},{n(foot - h + 8 * k)} V{n(foot)}", 1.4 * k)
    for sx in (-1, 1):
        px0 = x + sx * 4 * k if sx > 0 else x - w / 2 + 14 * k
        pw = w / 2 - 18 * k
        c.add(f'<rect x="{n(px0)}" y="{n(foot - h * 0.42)}" width="{n(pw)}" height="{n(h * 0.34)}" rx="{n(3 * k)}" '
              f'fill="{lighten(P.WOOD, 0.1)}" stroke="{darken(P.WOOD, 0.7)}" stroke-width="{n(1.2 * k)}"/>')
        c.add(f'<circle cx="{n(x + sx * 9 * k)}" cy="{n(foot - h * 0.5)}" r="{n(3.4 * k)}" fill="{P.SUN}" '
              f'stroke="{INK}" stroke-width="{n(k)}"/>')
    return (x - w / 2 + 12 * k, foot - h + w * 0.2, x + w / 2 - 12 * k, foot - h * 0.55)


def sheet(s, name: str, cx: float, top: float, word: str, k: float) -> tuple[float, float, float, float]:
    """The short sheet, its title on a tag - AGENTS.md - four ruled items under it, pinned at its top; its top's
    middle at (cx, top). Returns its box."""
    w, h = rules_size(k, word)
    pen = Pen(s, cx - w * k / 2, top, k)
    rules(pen, name, 0, 0, word, k)
    pen.c.add(f'<circle cx="{n(w / 2)}" cy="-1" r="4.5" fill="{P.RED}" stroke="{INK}" stroke-width="1.4"/>')
    s.put(2.2, pen.svg(), None)
    return pen.box(0, -6, w, h)


def reception(c: Canvas, x: float, foot: float, k: float) -> tuple[float, float, float, float]:
    """The reception desk by the door, its foot's middle at (x, foot), 200 wide and 64 tall: a teal panelled front, a
    wooden top, on it a banker's lamp with its green shade, a short stack of the books needed every day, a bell.
    Returns its box."""
    w, h = 200 * k, 64 * k
    top = foot - h
    c.add(f'<rect x="{n(x - w / 2)}" y="{n(top)}" width="{n(w)}" height="{n(h)}" fill="{P.TEAL}" stroke="{INK}" '
          f'stroke-width="{n(1.8 * k)}"/>')
    for i in range(3):
        px = x - w / 2 + 10 * k + i * (w - 20 * k) / 3
        c.add(f'<rect x="{n(px + 4 * k)}" y="{n(top + 14 * k)}" width="{n((w - 20 * k) / 3 - 8 * k)}" '
              f'height="{n(h - 24 * k)}" rx="{n(3 * k)}" fill="{lighten(P.TEAL, 0.15)}" '
              f'stroke="{darken(P.TEAL, 0.7)}" stroke-width="{n(1.2 * k)}"/>')
    c.add(f'<rect x="{n(x - w / 2 - 8 * k)}" y="{n(top - 6 * k)}" width="{n(w + 16 * k)}" height="{n(8 * k)}" '
          f'rx="{n(2 * k)}" fill="{P.WOOD}" stroke="{INK}" stroke-width="{n(1.6 * k)}"/>')
    lx = x - w * 0.32                                                                    # the banker's lamp
    c.add(f'<rect x="{n(lx - 10 * k)}" y="{n(top - 10 * k)}" width="{n(20 * k)}" height="{n(4 * k)}" fill="{P.SUN}" '
          f'stroke="{INK}" stroke-width="{n(k)}"/>')
    c.line(f"M{n(lx)},{n(top - 10 * k)} V{n(top - 34 * k)}", 2 * k, P.SUN)
    c.add(f'<path d="M{n(lx - 22 * k)},{n(top - 30 * k)} Q{n(lx)},{n(top - 50 * k)} {n(lx + 22 * k)},'
          f'{n(top - 30 * k)} Z" fill="{P.GREEN}" stroke="{INK}" stroke-width="{n(1.4 * k)}"/>')
    glow(c, lx, top - 28 * k, 3 * k)
    rnd = random.Random(3)
    y = top - 6 * k
    for i in range(4):                                                                   # the daily books
        bw, bh = (46 - i * 4) * k, 8 * k
        color = SPINES[(i * 3) % len(SPINES)]
        c.add(f'<rect x="{n(x - 4 * k - bw / 2 + rnd.uniform(-3, 3) * k)}" y="{n(y - bh)}" width="{n(bw)}" '
              f'height="{n(bh)}" rx="{n(1.5 * k)}" fill="{color}" stroke="{INK}" stroke-width="{n(k)}"/>')
        y -= bh
    bx = x + w * 0.32                                         # the big red bell-push the sparrow is after
    c.add(f'<rect x="{n(bx - 12 * k)}" y="{n(top - 12 * k)}" width="{n(24 * k)}" height="{n(7 * k)}" rx="{n(2 * k)}" '
          f'fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="{n(k)}"/>')
    c.add(f'<path d="M{n(bx - 8 * k)},{n(top - 12 * k)} Q{n(bx)},{n(top - 24 * k)} '
          f'{n(bx + 8 * k)},{n(top - 12 * k)} Z" '
          f'fill="{P.RED}" stroke="{INK}" stroke-width="{n(k)}"/>')
    c.add(f'<ellipse cx="{n(bx - 2 * k)}" cy="{n(top - 17 * k)}" rx="{n(2.4 * k)}" ry="{n(1.4 * k)}" '
          f'fill="{lighten(P.RED, 0.5)}"/>')
    cup = Canvas()                                            # the cat's teacup on its saucer, on the desk top
    cup.shape("M-12,0 H12 L9,-3 H-9 Z", P.WHITE, sw=1.0, light=None)                       # the saucer, flat
    cup.shape("M-7,-3 Q-8,-13 -8,-14 H8 Q8,-13 7,-3 Z", P.WHITE, sw=1.0, light=None)       # the cup on it
    cup.line("M-8,-11 H8", 1.4, P.TEAL)
    cup.add(f'<path d="M8,-12 q6,0 5,4 q-1,3 -6,2" fill="none" stroke="{INK}" stroke-width="1"/>')
    cup.line("M-3,-17 q3,-4 0,-8 q-3,-4 0,-7 M3,-17 q3,-3 0,-6", 1.0, P.METAL_DARK, 0.6)   # a little steam
    c.add(_at(cup, x + w * 0.1, top - 6 * k, k))
    return (x - w / 2 - 8 * k, top - 52 * k, x + w / 2 + 8 * k, foot)


def aisle_sign(s, x: float, foot: float, k: float, word: str) -> tuple[float, float, float, float]:
    """A sign-holder at an aisle's end, its foot at (x, foot): a heavy round base, a brass post, a frame on top
    holding the aisle's own short sheet. Returns its box."""
    w, h = rules_size(k * 0.8, word)
    sk = k * 0.8
    post = 90 * k
    c = Canvas()
    c.add(f'<ellipse cx="{n(x)}" cy="{n(foot - 3 * k)}" rx="{n(20 * k)}" ry="{n(5 * k)}" fill="{P.CHARCOAL}" '
          f'stroke="{INK}" stroke-width="{n(1.2 * k)}"/>')
    c.add(f'<rect x="{n(x - 2.5 * k)}" y="{n(foot - post)}" width="{n(5 * k)}" height="{n(post - 4 * k)}" '
          f'fill="{P.SUN}" stroke="{INK}" stroke-width="{n(k)}"/>')
    fw, fh = w * sk + 10 * k, h * sk + 10 * k
    top = foot - post - fh
    c.add(f'<rect x="{n(x - fw / 2)}" y="{n(top)}" width="{n(fw)}" height="{n(fh)}" rx="{n(3 * k)}" fill="{P.SUN}" '
          f'stroke="{INK}" stroke-width="{n(1.4 * k)}"/>')
    s.put(foot - 1, c.render(), (x - fw / 2, top, x + fw / 2, foot), "aisle_sign", group="aisle_sign")
    pen = Pen(s, x - w * sk / 2, top + 5 * k, sk)
    rules(pen, "aisle_sheet", 0, 0, word, sk)
    s.put(foot - 0.5, pen.svg(), None, group="aisle_sign")
    return (x - fw / 2, top, x + fw / 2, foot)


def catalogue(c: Canvas, x: float, foot: float, k: float, pulled: int | None = 6) -> tuple[float, float, float, float]:
    """A card catalogue cabinet, its foot's middle at (x, foot), 150 wide and 150 tall: oak, on turned legs, four
    columns of five small drawers, each with a brass label holder and a ring pull; drawer `pulled` drawn out with
    its index cards standing up. Returns its box."""
    cols, rows = 4, 5
    dw, dh = 32 * k, 20 * k
    w, h = cols * dw + 14 * k, rows * dh + 14 * k
    legs = 30 * k
    top = foot - legs - h
    for lx in (x - w / 2 + 8 * k, x + w / 2 - 14 * k):
        c.add(f'<rect x="{n(lx)}" y="{n(foot - legs)}" width="{n(6 * k)}" height="{n(legs)}" fill="{P.WOOD_DARK}" '
              f'stroke="{INK}" stroke-width="{n(k)}"/>')
    c.add(f'<rect x="{n(x - w / 2)}" y="{n(top)}" width="{n(w)}" height="{n(h)}" rx="{n(3 * k)}" fill="{P.WOOD}" '
          f'stroke="{INK}" stroke-width="{n(1.8 * k)}"/>')
    c.add(f'<rect x="{n(x - w / 2 - 4 * k)}" y="{n(top - 6 * k)}" width="{n(w + 8 * k)}" height="{n(8 * k)}" '
          f'rx="{n(2 * k)}" fill="{P.WOOD_DARK}" stroke="{INK}" stroke-width="{n(1.4 * k)}"/>')
    out = None
    for i in range(cols * rows):
        cx = x - w / 2 + 7 * k + (i % cols) * dw
        cy = top + 7 * k + (i // cols) * dh
        if i == pulled:
            out = (cx, cy)
            c.add(f'<rect x="{n(cx + 2 * k)}" y="{n(cy + 2 * k)}" width="{n(dw - 4 * k)}" height="{n(dh - 4 * k)}" '
                  f'fill="{darken(P.WOOD, 0.4)}"/>')
            continue
        c.add(f'<rect x="{n(cx + 2 * k)}" y="{n(cy + 2 * k)}" width="{n(dw - 4 * k)}" height="{n(dh - 4 * k)}" '
              f'rx="{n(1.5 * k)}" fill="{lighten(P.WOOD, 0.12)}" stroke="{darken(P.WOOD, 0.65)}" '
              f'stroke-width="{n(k)}"/>')
        c.add(f'<rect x="{n(cx + dw / 2 - 7 * k)}" y="{n(cy + 5 * k)}" width="{n(14 * k)}" height="{n(5 * k)}" '
              f'fill="{P.CARD}" stroke="{P.SUN}" stroke-width="{n(1.2 * k)}"/>')
        c.add(f'<circle cx="{n(cx + dw / 2)}" cy="{n(cy + 14 * k)}" r="{n(2.2 * k)}" fill="none" stroke="{P.SUN}" '
              f'stroke-width="{n(1.2 * k)}"/>')
    if out:                                    # the pulled drawer, straight out towards us: lower and wider
        cx, cy = out
        ox0, ox1, oy1 = cx + 2 * k, cx + dw - 2 * k, cy + dh - 2 * k              # the opening's lower edge
        fx0, fx1 = cx - 3 * k, cx + dw + 3 * k
        fy0 = oy1 + 9 * k                                                          # the front's top, nearer
        c.add(f'<path d="M{n(ox0)},{n(oy1)} H{n(ox1)} L{n(fx1)},{n(fy0)} H{n(fx0)} Z" '
              f'fill="{lighten(P.WOOD, 0.25)}" stroke="{INK}" stroke-width="{n(k)}"/>')   # its floor, seen in
        for a, b in ((ox0, fx0), (ox1, fx1)):                                          # its side walls
            c.add(f'<path d="M{n(a)},{n(oy1)} L{n(b)},{n(fy0)} L{n(b)},{n(fy0 - 6 * k)} L{n(a)},{n(oy1 - 5 * k)} Z" '
                  f'fill="{darken(P.WOOD, 0.85)}" stroke="{INK}" stroke-width="{n(0.9 * k)}"/>')
        for j in range(7):                                                          # the cards standing in it
            t_ = (j + 0.5) / 7
            gx = fx0 + 4 * k + (fx1 - fx0 - 8 * k) * t_
            gy = oy1 + (fy0 - oy1) * (j / 7)
            c.add(f'<rect x="{n(gx - 3.4 * k)}" y="{n(gy - 12 * k)}" width="{n(6.8 * k)}" height="{n(10 * k)}" '
                  f'fill="{P.CARD}" stroke="{INK}" stroke-width="{n(0.7 * k)}"/>')
        c.add(f'<rect x="{n(fx0 + 8 * k)}" y="{n(oy1 - 16 * k)}" width="{n(9 * k)}" height="{n(5 * k)}" '
              f'fill="{P.TEAL}" stroke="{INK}" stroke-width="{n(0.8 * k)}"/>')            # the guide card's tab
        c.add(f'<path d="M{n((fx0 + fx1) / 2)},{n(oy1 - 3 * k)} V{n(fy0 + 6 * k)}" stroke="{P.SUN}" '
              f'stroke-width="{n(1.6 * k)}"/>')                                             # the rod through them
        c.add(f'<rect x="{n(fx0)}" y="{n(fy0)}" width="{n(fx1 - fx0)}" height="{n(dh)}" rx="{n(1.5 * k)}" '
              f'fill="{lighten(P.WOOD, 0.12)}" stroke="{INK}" stroke-width="{n(1.3 * k)}"/>'   # its front
              f'<rect x="{n((fx0 + fx1) / 2 - 7 * k)}" y="{n(fy0 + 4 * k)}" width="{n(14 * k)}" height="{n(5 * k)}" '
              f'fill="{P.CARD}" stroke="{P.SUN}" stroke-width="{n(1.2 * k)}"/>'
              f'<circle cx="{n((fx0 + fx1) / 2)}" cy="{n(fy0 + 13 * k)}" r="{n(2.4 * k)}" fill="{P.SUN}" '
              f'stroke="{INK}" stroke-width="{n(0.7 * k)}"/>')                             # the rod's brass knob
    return (x - w / 2 - 6 * k, top - 20 * k, x + w / 2 + 6 * k, foot)


def card(x: float, y: float, k: float) -> str:
    """An index card held up at (x, y): ruled, a red top line, an arrow pointing off it - to the book."""
    c = Canvas()
    c.shape(rounded_rect_d(-2, -30, 44, 30, 2), P.CARD, sw=1.4, light=None)
    c.line("M2,-24 H38", 1.2, P.RED)
    c.line("M4,-17 H34 M4,-11 H28", 1, INK, 0.6)
    c.line("M26,-5 H38 l-4,-3 M38,-5 l-4,3", 1.2, P.TEAL)
    return _at(c, x, y, k)


def archive_height(k: float, words: list[str]) -> float:
    """How tall the archive stands on the page at scale k, the folder being filed included (its tabs keep their
    readable size, so a small k makes the folder relatively taller)."""
    size = letter(k, 10.0)
    th = tag_size("Ag", size, k)[1]
    step = th * 0.9
    fh = max(46.0 + step * (len(words) - 1), th * 1.5 + step * (len(words) - 1) + 12)
    return (140 + 8 + fh + 2) * k


def archive(s, x: float, foot: float, k: float, words: list[str]) -> tuple[float, float, float, float]:
    """The archive of decisions: a grey steel filing cabinet of three drawers, its foot's middle at (x, foot), 90
    wide and 140 tall; the top drawer pulled out, folders in it, one folder being filed - standing up, its four tabs
    named. Returns its box."""
    w, h = 90 * k, 140 * k
    top = foot - h
    c = Canvas()
    c.add(f'<rect x="{n(x - w / 2)}" y="{n(top)}" width="{n(w)}" height="{n(h)}" rx="{n(3 * k)}" '
          f'fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="{n(1.8 * k)}"/>')
    for i in range(3):
        dy = top + 8 * k + i * (h - 12 * k) / 3
        dh = (h - 12 * k) / 3 - 6 * k
        c.add(f'<rect x="{n(x - w / 2 + 6 * k)}" y="{n(dy)}" width="{n(w - 12 * k)}" height="{n(dh)}" '
              f'rx="{n(2 * k)}" fill="{P.METAL}" stroke="{INK}" stroke-width="{n(1.2 * k)}"/>')
        c.add(f'<rect x="{n(x - 12 * k)}" y="{n(dy + 6 * k)}" width="{n(24 * k)}" height="{n(8 * k)}" '
              f'fill="{P.CARD}" stroke="{P.METAL_DARK}" stroke-width="{n(k)}"/>')
        c.add(f'<rect x="{n(x - 10 * k)}" y="{n(dy + dh - 10 * k)}" width="{n(20 * k)}" height="{n(4 * k)}" '
              f'rx="{n(2 * k)}" fill="{P.METAL_DARK}"/>')
    c.add(f'<path d="M{n(x - w / 2 - 6 * k)},{n(top + 6 * k)} h{n(w + 12 * k)} v{n(-14 * k)} '
          f'h{n(-w - 12 * k)} Z" fill="{P.METAL}" stroke="{INK}" stroke-width="{n(1.2 * k)}"/>')   # the drawer out
    for i in range(5):                                                                    # folders in it
        c.add(f'<rect x="{n(x - w / 2 + 2 * k + i * 16 * k)}" y="{n(top - 18 * k - (i % 2) * 3 * k)}" '
              f'width="{n(14 * k)}" height="{n(12 * k)}" fill="{mix(P.KITCHEN_KRAFT, P.CARD, 0.3)}" '
              f'stroke="{INK}" stroke-width="{n(0.8 * k)}"/>')
    s.put(foot - 1, c.render(), (x - w / 2 - 6 * k, top - 22 * k, x + w / 2 + 6 * k, foot), "archive",
          group="archive")
    size = letter(k, 10.0)                      # the folder being filed: four dividers, their tabs staggered
    tws = [tag_size(word, size, k)[0] for word in words]
    th = tag_size("Ag", size, k)[1]
    step = th * 0.9
    fw = max(w / k * 0.9, max(tws) * 1.7)
    last = th * 1.5 + step * (len(words) - 1)             # the last tab's foot: the folder's front stays under it
    fh = max(46.0 + step * (len(words) - 1), last + 12)
    front = max(9.0, min(18.0, fh - last - 3))
    fx, ftop = x - fw * k / 2, top - 8 * k - fh * k      # standing in the pulled-out drawer
    pen = Pen(s, fx, ftop, k)
    colors = (P.TEAL, P.YELLOW, P.PINK, P.BLUE)
    for i, word in enumerate(words):
        y = th + i * step
        pen.c.shape(rounded_rect_d(0, y, fw, fh - y, 3), mix(colors[i % 4], P.CARD, 0.55), sw=1.2, light=None)
        tx = 4 + i * (fw - tws[i] - 8) / max(1, len(words) - 1) + tws[i] / 2
        pen.tag(f"tab{i}", tx, y - th / 2 + 1, word, size, colors[i % 4], style="plain")
    pen.c.shape(rounded_rect_d(0, fh - front, fw, front, 3), P.KITCHEN_KRAFT, sw=1.6, light=None)   # its front
    s.put(foot - 0.8, pen.svg(), pen.box(0, -2, fw, fh), "folder", group="archive")
    return (min(x - w / 2 - 6 * k, fx), ftop - 6 * k, max(x + w / 2 + 6 * k, fx + fw * k), foot)


def lectern(c: Canvas, x: float, foot: float, k: float) -> tuple[float, float, float, float]:
    """A reading table with a big book open on a book cradle, its foot's middle at (x, foot), 100 wide and 122
    tall: the table - a top board, an apron, two legs and a stretcher; on it a wooden cradle, a wedge that holds the
    book open; the book - its dark red cover, two pages curving up from the spine with lines of text; paper
    bookmarks sticking up out of its top edge, two ribbon bookmarks hanging from the spine over the cradle's front.
    Symmetric, seen from the front. Returns its box."""
    d = Canvas()
    for lx in (-44, 38):                                                                     # the legs
        d.shape(rounded_rect_d(lx, -58, 6, 58, 1), P.WOOD_DARK, sw=1.4, light=None)
    d.shape(rounded_rect_d(-40, -22, 80, 4, 1), P.WOOD_DARK, sw=1.2, light=None)          # the stretcher
    d.shape(rounded_rect_d(-47, -62, 94, 8, 1), P.WOOD, sw=1.4, light=None)               # the apron
    d.shape(rounded_rect_d(-51, -67, 102, 6, 2), P.WOOD_LIGHT, sw=1.6, light=None)        # the top
    d.shape("M-36,-67 L-30,-77 H30 L36,-67 Z", P.WOOD_DARK, sw=1.4, light=None)           # the cradle
    d.shape("M-44,-78 L-42,-112 Q-22,-116 0,-110 Q22,-116 42,-112 L44,-78 Z", darken(P.RED, 0.8), sw=1.6,
            light=None)                                                                       # the cover
    for side in (-1, 1):                                                                      # the open pages
        d.shape(f"M0,-80 L{side * 39},-81 L{side * 38},-108 Q{side * 20},-112 0,-106 Z", P.WHITE, sw=1.2,
                light=None)
        d.add("".join(f'<path d="M{side * 5},{-100 + j * 4} Q{side * 20},{-103 + j * 4} {side * 33},{-101 + j * 4}" '
                      f'fill="none" stroke="{INK}" stroke-width=".7" stroke-opacity=".5"/>' for j in range(5)))
    d.line("M0,-106 V-80", 1.2, INK, 0.7)                                                     # the spine's fold
    for bx, h, color, tilt in ((-30, 12, P.YELLOW_PALE, -6), (-14, 9, P.WHITE, 4), (18, 14, P.YELLOW_PALE, 5),
                               (30, 8, P.WHITE, -3)):                                           # paper bookmarks
        top = -110 + (abs(bx) / 42) * 2 - h
        d.add(f'<rect x="{bx - 3}" y="{n(top)}" width="6" height="{h + 4}" fill="{color}" stroke="{INK}" '
              f'stroke-width=".8" transform="rotate({tilt} {bx} {n(top + h)})"/>')
    for px, color in ((-3, P.RED), (3, P.TEAL)):                                            # ribbon bookmarks
        d.add(f'<path d="M{px},-80 L{px * 2},-60 l-2.4,4 M{px * 2},-60 l2.4,4" fill="none" stroke="{color}" '
              f'stroke-width="2.4"/>')
    c.add(_at(d, x, foot, k))
    return (x - 51 * k, foot - 126 * k, x + 51 * k, foot)


def trolley(c: Canvas, x: float, foot: float, k: float) -> tuple[float, float, float, float]:
    """A library's sorting trolley, its foot's middle at (x, foot), 160 wide and 96 tall: two wooden shelves on a
    steel frame, castors, a handle; on top three trays - one for the door sheet (a yellow note), one for an aisle's
    sheet (a little stand), one for the catalogue (index cards) - each with what has been sorted into it; books on
    the lower shelf. Returns its box."""
    w = 160 * k
    for wx in (x - w / 2 + 12 * k, x + w / 2 - 12 * k):
        c.add(f'<circle cx="{n(wx)}" cy="{n(foot - 7 * k)}" r="{n(7 * k)}" fill="{P.CHARCOAL}" stroke="{INK}" '
              f'stroke-width="{n(k)}"/>')
    for px in (x - w / 2 + 6 * k, x + w / 2 - 10 * k):
        c.add(f'<rect x="{n(px)}" y="{n(foot - 92 * k)}" width="{n(4 * k)}" height="{n(80 * k)}" fill="{P.METAL}" '
              f'stroke="{INK}" stroke-width="{n(k)}"/>')
    c.add(f'<path d="M{n(x + w / 2 - 8 * k)},{n(foot - 92 * k)} q{n(16 * k)},0 {n(16 * k)},{n(-14 * k)}" '
          f'fill="none" stroke="{P.METAL_DARK}" stroke-width="{n(4 * k)}"/>')                      # the handle
    rnd = random.Random(5)
    for sy in (foot - 16 * k, foot - 56 * k):
        c.add(f'<rect x="{n(x - w / 2)}" y="{n(sy - 6 * k)}" width="{n(w)}" height="{n(6 * k)}" fill="{P.WOOD}" '
              f'stroke="{INK}" stroke-width="{n(1.2 * k)}"/>')
    books(c, x - w / 2 + 12 * k, x + w / 2 - 14 * k, foot - 22 * k, 30 * k, k, rnd)
    tw = (w - 24 * k) / 3
    for i in range(3):
        tx = x - w / 2 + 8 * k + i * (tw + 4 * k)
        ty = foot - 92 * k
        c.add(f'<rect x="{n(tx)}" y="{n(ty)}" width="{n(tw)}" height="{n(30 * k)}" rx="{n(2 * k)}" '
              f'fill="{P.TEAL}" stroke="{INK}" stroke-width="{n(1.2 * k)}"/>')
        mx = tx + tw / 2
        if i == 0:                                                             # the door sheet's tray
            c.add(f'<rect x="{n(mx - 9 * k)}" y="{n(ty - 10 * k)}" width="{n(18 * k)}" height="{n(22 * k)}" '
                  f'fill="{P.YELLOW_PALE}" stroke="{INK}" stroke-width="{n(k)}"/>')
            c.line(f"M{n(mx - 6 * k)},{n(ty - 4 * k)} h{n(12 * k)} M{n(mx - 6 * k)},{n(ty + 1 * k)} h{n(9 * k)}", k)
        elif i == 1:                                                           # returned books, stacked
            for j, color in enumerate((P.RED, P.TEAL, P.BLUE)):
                c.add(f'<rect x="{n(mx - 12 * k + (j % 2) * 2 * k)}" y="{n(ty - 7 * k - j * 7 * k)}" '
                      f'width="{n(24 * k)}" height="{n(7 * k)}" rx="{n(1.2 * k)}" fill="{color}" stroke="{INK}" '
                      f'stroke-width="{n(0.8 * k)}"/>')
        else:                                                                  # the catalogue's tray
            for j in range(4):
                c.add(f'<rect x="{n(mx - 10 * k + j * 5 * k)}" y="{n(ty - 8 * k - (j % 2) * 3 * k)}" '
                      f'width="{n(6 * k)}" height="{n(12 * k)}" fill="{P.CARD}" stroke="{INK}" '
                      f'stroke-width="{n(0.8 * k)}"/>')
    return (x - w / 2, foot - 118 * k, x + w / 2 + 12 * k, foot)


def note(x: float, y: float, k: float) -> str:
    """A small paper note held at (x, y), two ruled lines on it."""
    c = Canvas()
    c.shape(rounded_rect_d(-2, -22, 24, 22, 1.5), P.YELLOW_PALE, sw=1.2, light=None)
    c.line("M2,-16 H18 M2,-10 H14", 1, INK, 0.6)
    return _at(c, x, y, k)


def binders(s, x0: float, foot_y: float, k: float, words: list[str]) -> tuple[float, float, float, float]:
    """The reference shelf on the wall: a wooden shelf on two brackets, its top at foot_y, the binders standing on
    it from x0 - tall ring binders, their spines labelled, a finger hole at the bottom of each. Returns its box."""
    bw, bh = 34 * k, 120 * k
    w = len(words) * (bw + 6 * k) + 20 * k
    c = Canvas()
    colors = (P.TEAL, P.BLUE, P.RED, P.GREEN, P.YELLOW)
    for i, word in enumerate(words):
        bx = x0 + 10 * k + i * (bw + 6 * k)
        color = colors[i % len(colors)]
        c.add(f'<rect x="{n(bx)}" y="{n(foot_y - bh)}" width="{n(bw)}" height="{n(bh)}" rx="{n(3 * k)}" '
              f'fill="{color}" stroke="{INK}" stroke-width="{n(1.4 * k)}"/>')
        c.add(f'<rect x="{n(bx + 5 * k)}" y="{n(foot_y - bh + 10 * k)}" width="{n(bw - 10 * k)}" '
              f'height="{n(bh - 36 * k)}" rx="{n(2 * k)}" fill="{P.CARD}" stroke="{INK}" stroke-width="{n(k)}"/>')
        size = min(letter(k, 9.0) * k, (bw - 14 * k) * 0.8)
        cx, cy = bx + bw / 2, foot_y - bh + 10 * k + (bh - 36 * k) / 2
        c.add(lettering(cx + size * 0.35, cy, word, size, INK, turn=-90, room=bh - 44 * k, style="plain"))
        c.add(f'<circle cx="{n(bx + bw / 2)}" cy="{n(foot_y - 14 * k)}" r="{n(5 * k)}" fill="{darken(color, 0.5)}" '
              f'stroke="{INK}" stroke-width="{n(k)}"/>')
    c.add(f'<rect x="{n(x0)}" y="{n(foot_y)}" width="{n(w)}" height="{n(7 * k)}" fill="{P.WOOD}" stroke="{INK}" '
          f'stroke-width="{n(1.2 * k)}"/>')
    for bx in (x0 + 10 * k, x0 + w - 22 * k):
        c.add(f'<path d="M{n(bx)},{n(foot_y + 7 * k)} h{n(12 * k)} L{n(bx)},{n(foot_y + 22 * k)} Z" '
              f'fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="{n(k)}"/>')
    box = (x0, foot_y - bh, x0 + w, foot_y + 22 * k)
    s.put(1.6, c.render(), box, "binders", group="binders")
    return box


# ============================================================================ the stations
def sheet_station(s: Strip, beat: str) -> None:
    """The door. "pin": the professor pins the short sheet - AGENTS.md - on the library's door, the agent
    arriving, the sparrow on the door's arch. "read": the agent reads it, the caterpillar asking if that is all."""
    r, k = lane(s), s.unit
    dk = min(k * 1.2, (r.feet - 6) / 205, span(s, 0.28) / 112)
    dx = inside(s, s.x(0.5 if beat == "pin" else 0.3), 60 * dk, 60 * dk)
    c = Canvas()
    panel = door(c, dx, r.feet, dk)
    s.put(1.5, c.render(), (dx - 56 * dk, r.feet - 200 * dk, dx + 56 * dk, r.feet), "door", group="door")
    sk = min(dk * 0.9, (panel[2] - panel[0]) / rules_size(dk, s.word("rules"))[0])
    sheet(s, "door_sheet", dx, panel[1] + 6 * dk, s.word("rules"), sk)
    if beat == "pin":
        stand(s, "cat" if mid(s) else "professor", (0.26, 0.22, 0.3, 0.16, 0.1, 0.06), "point", "talk",
              flip=False)
        stand(s, "agent", (0.78, 0.82, 0.74), "wave", "smile", flip=True)
        sparrow(s, dx, r.feet - 200 * dk, "stand")
    else:
        stand(s, "agent", (0.55, 0.6, 0.5), "read", "smile", flip=True)
        stand(s, "caterpillar", (0.82, 0.86, 0.78), "think", "worry", flip=True)


def near_station(s: Strip, beat: str) -> None:
    """Nearer is what is needed more often. "desk": the reception desk by the door, waist-high, the daily books on
    it - the agent takes one, the cat explains, the sparrow sits on the banker's lamp. "stacks": the far stacks and
    their rolling ladder, the ladder the subject - the agent climbing it after a rare book, the caterpillar holding
    its foot."""
    r = lane(s)
    p = ph(s)
    if beat == "desk":
        dk = min(0.5 * p / 64, (r.feet - 8) / 120, span(s, 0.28 if s.h >= 400 else 0.38) / 216)
        x = inside(s, s.x(0.26), 110 * dk, 110 * dk)
        c = Canvas()
        box = reception(c, x, r.feet, dk)
        s.put(r.feet - 1, c.render(), box, "desk", group="desk")
        held(s, stand(s, "agent", (0.52, 0.56, 0.6, 0.64), "present", "smile", flip=True), handheld.book)
        stand(s, "cat", (0.88, 0.92, 0.84), "point", "talk", flip=True)
        for scale in (0.45, 0.36, 0.28):                      # on the desk, at the big red bell-push
            bird = _box(s, "sparrow", x + 76 * dk, r.feet - 67 * dk, scale)
            if bird[1] > 2 and all(not b.hits(bird, 3) for b in s.boxes if b.group != "desk"):
                s.actor("sparrow", x + 76 * dk, r.feet - 67 * dk, "point", "smile", flip=True,
                        tall=s.tall * SIZE["sparrow"] * scale, group="desk")
                break
        return
    top = max(2.0, r.feet - 1.35 * p)
    lk = (r.feet - top) / 300
    width = min(250 * lk, span(s, 0.4))
    x0 = s.x(0.1) - (width + 100 * lk if getattr(s, "flipx", False) else 0)   # a mirrored page: the right end
    x0 = inside(s, x0, 0, width + 100 * lk)
    x1 = x0 + width
    c = Canvas()
    bookcase(c, x0, x1, top + 14 * lk, r.feet, lk, seed=11, paint=darken(P.TEAL, 0.85))
    lx = x1 - 10 * lk
    foot_x = lx + 70 * lk
    ladder(c, foot_x, top + 24 * lk, foot_x, r.feet, lk, rail=(x0, foot_x + 26 * lk), rolling=True)
    s.put(1.2, c.render(), (x0 - 4, top, foot_x + 24 * lk, r.feet), "stacks", group="stacks")
    feet = r.feet - (r.feet - top) * 0.32                 # on a tread a third of the way up
    s.actor("agent", foot_x, feet, "point", "smile", flip=False, tall=s.tall * SIZE["agent"] * 0.9,
            group="stacks")
    stand(s, "caterpillar", ((foot_x + 70 * lk - s.lo) / (s.hi - s.lo), 0.66, 0.7), "present", "worry", flip=False)
    sparrow(s, x0 + 40 * lk, top + 10 * lk, "stand")              # on the bookcase's top
    stand(s, "cat", (0.92, 0.88, 0.96), "think", "smile", flip=True)


def aisles_station(s: Strip, beat: str) -> None:
    """An aisle's end: two bookcases either side of the aisle, the sign-holder in front of it with the aisle's own
    small sheet; the agent reads it, the cat explains that the door sheet stays short."""
    r = lane(s)
    k = min(s.unit, span(s, 0.46) / 330, (r.feet - 12) / 310)   # the aisle leaves room for its readers
    top = max(4.0, r.feet - 300 * k)
    c = Canvas()
    shot = s.shot
    bw = 120 * k
    ax = s.lo + bw + 46 * k if shot == 0 else s.hi - bw - 46 * k    # the aisle at one side, its readers at the other
    bookcase(c, ax - bw - 40 * k, ax - 40 * k, top, r.feet, k, seed=21)
    bookcase(c, ax + 40 * k, ax + bw + 40 * k, top, r.feet, k, seed=22)
    c.add(f'<rect x="{n(ax - 40 * k)}" y="{n(top)}" width="{n(80 * k)}" height="{n(r.feet - top)}" '
          f'fill="{darken(P.TEAL, 0.55)}"/>')                                              # the aisle's depth
    s.put(1.1, c.render(), (ax - bw - 44 * k, top - 4, ax + bw + 44 * k, r.feet), "aisle", group="aisle_sign")
    aisle_sign(s, ax, r.feet + min(4.0, s.h - r.feet), k, s.word("rules"))
    sparrow(s, ax - bw / 2 - 40 * k, top - 6 * k, "stand")                 # on a bookcase's top by the aisle
    if shot == 0:
        stand(s, "agent", (0.5, 0.54, 0.58, 0.62), "read", "smile", flip=True)
        stand(s, "cat", (0.9, 0.94, 0.86), "point", "talk", flip=True)
    else:
        stand(s, "agent", (0.5, 0.46, 0.42, 0.38), "read", "smile", flip=False)
        stand(s, "caterpillar", (0.1, 0.06, 0.14), "think", "worry", flip=False)


def catalogue_station(s: Strip, beat: str) -> None:
    """The card catalogue, a tall oak cabinet of little drawers. "pull": a drawer pulled out, the cat holds up a
    card - it points to the book, it is no copy of it - the agent listens, the sparrow on the cabinet's top.
    "follow": the agent follows the card's arrow to the right shelf of a bookcase, the cat behind with the card."""
    r, k = lane(s), s.unit
    p = ph(s)
    ck = min(0.95 * p / 164, (r.feet - 4) / 168, span(s, 0.3) / 152)
    if beat == "pull":
        x = inside(s, s.x(0.24), 80 * ck, 80 * ck)
        c = Canvas()
        box = catalogue(c, x, r.feet, ck)
        s.put(r.feet - 1, c.render(), box, "catalogue", group="catalogue")
        held(s, stand(s, "cat", (0.56, 0.6, 0.52), "present", "talk", flip=True), handheld.card)
        stand(s, "agent", (0.86, 0.9, 0.82), "think", "smile", flip=True)
        sparrow(s, x + 30 * ck, box[1] + 20 * ck, "stand")
        return
    bx0 = inside(s, s.x(0.66), 4, 150 * k)
    top = max(8.0, r.feet - 1.3 * p)
    cc = Canvas()
    bookcase(cc, bx0, bx0 + min(150 * k, span(s, 0.3)), top, r.feet, (r.feet - top) / 300, seed=61)
    s.put(1.2, cc.render(), (bx0 - 4, top - 4, bx0 + min(150 * k, span(s, 0.3)) + 4, r.feet), "case", group="case")
    held(s, stand(s, "cat", (0.12, 0.08, 0.16), "present", "smile", flip=False), handheld.card)
    stand(s, "agent", (0.42, 0.46, 0.38), "point", "smile", flip=False)


def archive_station(s: Strip, beat: str) -> None:
    """The archive of decisions: a steel filing cabinet, its top drawer out, a folder being filed - four dividers,
    their tabs context, decision, rejected, consequences. "file": the agent files it, the caterpillar checks.
    "doubt": closer, the caterpillar peers at the "rejected" tab, unsure, the cat explains it."""
    r = lane(s)
    p = ph(s)
    room = (r.feet - 8) / (262 if s.h >= 200 else 330)      # its tabs keep their size: a strip shrinks it more
    ak = min(0.62 * p / 140, room, span(s, 0.26) / 100)
    words = [s.word(key) for key in ("context", "decision", "rejected", "consequences")]
    for _ in range(12):                                    # the folder's top tab stays inside the frame
        if r.feet - archive_height(ak, words) >= 4:
            break
        ak *= 0.93
    room = min(room, ak)
    if beat == "file":
        x = inside(s, s.x(0.44), 70 * ak, 70 * ak)
        archive(s, x, r.feet, ak, words)
        stand(s, "agent", (0.14, 0.1, 0.18), "present", "smile", flip=False)
        stand(s, "caterpillar", (0.78, 0.82, 0.74), "write", "worry", flip=True)
        return
    dk = min(ak * (0.85 if s.h >= 400 else 1.1), room)
    x = inside(s, s.x(0.28), 70 * dk, 70 * dk)
    archive(s, x, r.feet, dk, words)
    stand(s, "caterpillar", (0.6, 0.56, 0.64), "think", "worry", flip=False)
    stand(s, "cat", (0.88, 0.92, 0.84), "point", "talk", flip=True)


def notes_station(s: Strip, beat: str) -> None:
    """Comments in code: a reading table, a big book open on its cradle at the very page, paper bookmarks sticking
    out of it right there and ribbons hanging from it. "read": the agent reads the page, the professor brings
    another note (the caterpillar, in a mid strip), the sparrow on the book's cover. "stick": the agent points at
    the page for a new bookmark, the caterpillar watching."""
    r = lane(s)
    p = ph(s)
    lk = min(0.62 * p / 82, (r.feet - 8) / 128, span(s, 0.36) / 102)
    x = inside(s, s.x(0.44 if beat == "read" else 0.36), 52 * lk, 56 * lk)
    c = Canvas()
    box = lectern(c, x, r.feet, lk)
    s.put(r.feet - 1, c.render(), box, "lectern", group="lectern")
    if beat == "read":
        stand(s, "agent", (0.12, 0.08, 0.16), "read", "smile", flip=False)
        if mid(s):
            stand(s, "caterpillar", (0.82, 0.86, 0.78), "think", "smile", flip=True)
        else:
            stand(s, "professor", (0.8, 0.84, 0.76), "think", "talk", flip=True)
        sparrow(s, x + 40 * lk, r.feet - 112 * lk, "stand")
        return
    stand(s, "agent", (0.6, 0.64, 0.56), "point", "smile", flip=True)
    stand(s, "caterpillar", (0.88, 0.92, 0.84), "think", "worry", flip=True)


def sort_station(s: Strip, beat: str) -> None:
    """Where the rules go: a real book trolley, waist-high, with three trays on top - the door sheet, an aisle's
    sheet, the catalogue - and returned books below; the agent sorts a note into its tray, the cat checks where it
    goes, the sparrow on the trolley's handle."""
    r = lane(s)
    p = ph(s)
    tk = min(0.55 * p / 92, (r.feet - 8) / 125, span(s, 0.5) / 172)
    x = inside(s, s.x(0.46), 82 * tk, 92 * tk)
    c = Canvas()
    box = trolley(c, x, r.feet, tk)
    s.put(r.feet - 1, c.render(), box, "trolley", group="trolley")
    stand(s, "agent", (0.12, 0.08, 0.16, 0.04, 0.2), "point", "smile", flip=False)
    stand(s, "cat", (0.88, 0.92, 0.84, 0.96), "think", "smile", flip=True)
    sparrow(s, x + 88 * tk, r.feet - 108 * tk, "stand")


def docs_station(s: Strip, beat: str) -> None:
    """What else goes into docs/: the reference shelf of tall labelled binders on the wall, its top above the
    professor's head; the caterpillar reads the spines, the professor (the agent, in a mid strip) shows them, the
    sparrow on the shelf's end."""
    r = lane(s)
    p = ph(s)
    words = [s.word(key) for key in ("arch", "design", "product", "security")]
    bk = min(0.8 * p / 160, (r.feet - 30) / 150, span(s, 0.45) / (len(words) * 40 + 20))
    x0 = s.lo + 6
    shelf_y = r.feet - 40 * bk
    box = binders(s, x0, shelf_y, bk, words)
    if mid(s):
        stand(s, "agent", (0.9, 0.86, 0.94), "point", "smile", flip=True)
    else:
        stand(s, "professor", (0.9, 0.86, 0.94), "present", "talk", flip=True)
    stand(s, "caterpillar", (0.62, 0.58, 0.66), "think", "smile", flip=False)
    sparrow(s, box[2] - 10 * bk, shelf_y, "stand")


def check_station(s: Strip, beat: str) -> None:
    """The test. "find": the agent, sent by the door sheet, takes the right book off the shelf at once, the cat
    times it on his stopwatch. "twice": the caterpillar checks the book against the sheet once more, the agent
    holds it up, the sparrow cheers on the bookcase's top."""
    r, k = lane(s), s.unit
    top = max(4.0, r.feet - 300 * k)
    x0 = inside(s, s.x(0.34 if beat == "find" else 0.56), 4, min(114 * k, span(s, 0.28) + 4))
    x1 = x0 + min(110 * k, span(s, 0.28))
    c = Canvas()
    nook = floppy_size()[0] + 8 if getattr(s, "egg", None) else 0.0
    side = max(4.0, 7 * k)
    title = s.word("fortran")
    tw, th = tome_size(title)
    probe = bookcase(Canvas(), x0, x1, top, r.feet, k)                # where its shelves come, to see if it fits
    fits = beat == "find" and len(probe) >= 2 and tw + 8 <= (x1 - x0 - 2 * side) * 0.85 and \
        th <= probe[-1] - probe[-2] - 9 * k
    tail = tw + 8 if fits else 0.0
    tops = bookcase(c, x0, x1, top, r.feet, k, seed=31 if beat == "find" else 32, nook=nook, tail=tail)
    if tail:                                              # the book inside the book, lying on the bottom shelf
        c.add(tome(x1 - side - tail / 2, tops[-1], title, P.RED))
    s.put(1.2, c.render(), (x0 - 4, top - 4, x1 + 4, r.feet), "case", group="case")
    if nook:                                              # the golden floppy between the books (an easter egg)
        stash(s, x1 - max(4.0, 7 * k) - nook / 2, tops[len(tops) // 2], 1.21, group="case", turn=-4)
    if beat == "find":
        held(s, stand(s, "agent", (0.08, 0.12, 0.04), "present", "smile", flip=False), handheld.book)
        held(s, stand(s, "cat", (0.78, 0.82, 0.74, 0.86, 0.9, 0.94, 0.7), "present", "smile", flip=True),
             handheld.stopwatch)
    else:
        held(s, stand(s, "agent", (0.1, 0.14, 0.06), "present", "smile", flip=False), handheld.book)
        stand(s, "caterpillar", (0.32, 0.36, 0.28), "write", "worry", flip=False)
        sparrow(s, (x0 + x1) / 2, top - 4 * k, "cheer")


# ============================================================================ the finale


BAYS = (("sheet",), ("near",), ("aisles",), ("catalogue", "sort"), ("archive", "docs"), ("notes", "check"))


def finale(s: Strip) -> None:
    """The whole library at once, as a long gallery: the upper tier of teal bookcases and its rail across the top;
    below, six bays, each a teal bookcase with its station's thing in front of it - the door with its sheet, the
    desk, an aisle's sign, the catalogue and the trolley, the archive and the binders, the lectern - its name on the
    bay's cornice right over it; the cast in front on the parquet."""
    ledger(s)
    zoom(s)
    backdrop(s, 0)
    r = lane(s)
    c = Canvas()
    left, right = s.lo, s.hi
    wide = (right - left) / len(BAYS)
    rail = max(20.0, s.base * 0.22)                       # the gallery: its upper tier fills the top
    k = max(0.5, min(s.unit, (r.feet - rail) / 300))
    for i in range(int(W / (120 * k)) + 1):
        bookcase(c, i * 120 * k + 2, (i + 1) * 120 * k - 2, -20 * k, rail - 8, k, seed=70 + i)
    c.add(f'<rect x="-6" y="{n(rail - 10)}" width="{W + 12}" height="{n(18 * k)}" fill="{P.TEAL}" stroke="{INK}" '
          f'stroke-width="1.6"/>')
    c.line(f"M-6,{n(rail - 28 * k)} H{W + 6}", 4 * k, darken(P.TEAL, 0.7))
    for x in range(0, W, int(22 * k) + 1):
        c.line(f"M{x},{n(rail - 10)} v{n(-18 * k)}", 2 * k, darken(P.TEAL, 0.7))
    tops = []
    for i in range(len(BAYS)):
        x0 = left + wide * i + 4
        top = rail + 22 * k
        bookcase(c, x0, x0 + wide - 8, top, r.feet, k, seed=80 + i, faded=True)
        tops.append(top)
    s.put(0.8, c.render(), None)
    things = Canvas()
    ok = min(k * 1.0, (r.feet - rail - 60 * k) / 210)
    for i, keys in enumerate(BAYS):
        x = left + wide * (i + 0.5)
        main = keys[0]
        if main == "sheet":
            panel = door(things, x, r.feet, ok)
            sheet(s, "f_sheet", x, panel[1] + 6 * ok, s.word("rules"), ok * 0.7)
        elif main == "near":
            reception(things, x, r.feet, ok * 0.55)
        elif main == "aisles":
            aisle_sign(s, x, r.feet, ok, s.word("rules"))
        elif main == "catalogue":
            catalogue(things, x - 24 * ok, r.feet, ok * 0.7)
            trolley(things, x + 44 * ok, r.feet, ok * 0.4)
        elif main == "archive":
            things.add(f'<rect x="{n(x - 34 * ok)}" y="{n(r.feet - 120 * ok)}" width="{n(60 * ok)}" '
                       f'height="{n(120 * ok)}" rx="{n(3 * ok)}" fill="{P.METAL_LIGHT}" stroke="{INK}" '
                       f'stroke-width="{n(1.6 * ok)}"/>')
            for j in range(3):
                things.add(f'<rect x="{n(x - 29 * ok)}" y="{n(r.feet - 114 * ok + j * 38 * ok)}" '
                           f'width="{n(50 * ok)}" height="{n(32 * ok)}" rx="{n(2 * ok)}" fill="{P.METAL}" '
                           f'stroke="{INK}" stroke-width="{n(ok)}"/>')
            for j, color in enumerate((P.TEAL, P.BLUE, P.RED)):
                things.add(f'<rect x="{n(x + 32 * ok + j * 13 * ok)}" y="{n(r.feet - 70 * ok)}" '
                           f'width="{n(11 * ok)}" height="{n(70 * ok)}" rx="{n(2 * ok)}" fill="{color}" '
                           f'stroke="{INK}" stroke-width="{n(ok)}"/>')
        else:
            lectern(things, x, r.feet, ok * 0.9)
    s.put(1.2, things.render(), None)
    size = 13.0
    labels = [" · ".join(s.word(key) for key in keys) for keys in BAYS]
    widest = max(tag_size(text, size)[0] for text in labels)
    if widest > wide * 1.9:
        size = max(sets.LETTERING_MIN + 1, size * wide * 1.9 / widest)
    th = tag_size("Ag", size)[1]
    cast_ = {0: ("professor", "point"), 2: ("agent", "wave"), 3: ("cat", "think"), 5: ("caterpillar", "cheer")}
    for i, (name, pose) in cast_.items():
        x = left + wide * (i + (1.0 if i in (0, 2) else 0.85))   # the professor and the agent beside, not over, a sign
        names = max(tops[i], tops[min(i + 1, len(tops) - 1)]) + 2 * th + 18 if s.h >= 300 else rail + 30
        tall = min(s.tall * SIZE[name] * 1.6, _fit_tall(name, wide * 0.8, r.feet - names))   # heads under the names
        group = "aisle_sign" if i == 2 else f"f{i}"       # in front of its bay's thing, as one stands before it
        s.actor(name, min(x, s.hi - 40), r.feet, pose, "smile", flip=True, tall=tall, group=group)
    if s.h >= 300:                                        # each bay's name on its cornice, right over its thing
        pen = Pen(s, 0, 0, 1)
        for i, text in enumerate(labels):
            tw = tag_size(text, size)[0] + 16
            lx = min(max(left + wide * (i + 0.5), s.lo + tw / 2 + 4), s.hi - tw / 2 - 4)
            y = tops[i] + 4 + (th + 6) * (i % 2)                              # long names in two rows
            while y - th > rail and not s.free((lx - tw / 2, y - th / 2, lx + tw / 2, y + th / 2), 4):
                y -= 4                                                         # clear of a head in front
            holder = pen.tag(f"label{i}", lx, y, text, size, P.CHARCOAL, P.WHITE)
            s.put(2, "", holder.outer, f"label{i}")
        s.put(2, pen.svg(), None)


# ============================================================================ the opener
def opener(st: Stage, accent: str):
    """The reading room, one hero: a tall two-tier wall of teal bookcases, a gallery between the tiers and a big
    rolling ladder hooked on its rail; a teal vault over it, calm where the title goes, a tall arched window at the
    left over the professor, lamplight warm along the gallery. The ladder is rolling: the agent stands high on it
    reaching for a book, the caterpillar holds its foot, afraid it rolls away; the cat, across the floor, times them
    on his stopwatch; the sparrow flies with a ribbon bookmark, an index card flutters down. The professor, under
    his bubble, tells them where things are kept here."""
    ledger(st)
    c = st.back
    floor = 1010.0
    vault = c.gradient([(0, mix(P.TEAL, P.SPACE_DEEP, 0.2)), (1, mix(P.TEAL, P.CARD, 0.45))], 0, 0, 0, floor)
    c.add(f'<rect x="0" y="0" width="{W}" height="{n(floor)}" fill="{vault}"/>')
    for x in (160, 420, 680):                                                   # the vault's ribs
        c.add(f'<path d="M{x - 200},300 Q{x},120 {x + 200},300" fill="none" stroke="{mix(P.TEAL, P.CARD, 0.4)}" '
              f'stroke-width="6"/>')
    # the arched window at the left, behind the professor's bubble: calm sky through one wide pane, its glazing
    # bars only low down, under the bubble's air
    wx0, wx1, wtop, wfoot = -20.0, 364.0, 300.0, 790.0
    r = (wx1 - wx0) / 2
    sky = c.gradient([(0, P.SKY), (1, P.SKY_LOW)], 0, wtop, 0, wfoot)
    arch = f"M{wx0},{wfoot} V{wtop + r} A{r},{r} 0 0 1 {wx1},{wtop + r} V{wfoot} Z"
    c.add(f'<path d="{arch}" fill="{sky}" stroke="{P.TEAL}" stroke-width="16"/>')
    c.add(f'<path d="{arch}" fill="none" stroke="{INK}" stroke-width="2"/>')
    c.line(f"M{wx0},{wfoot - 40} H{wx1} M{(wx0 + wx1) / 2},{wfoot - 40} V{wfoot}", 5, darken(P.TEAL, 0.7))
    cx_, cy_ = (wx0 + wx1) / 2, wtop + r
    st.keep_clear(*[(cx_ + math.cos(a) * r - 9, cy_ - math.sin(a) * r - 9, cx_ + math.cos(a) * r + 9,
                     cy_ - math.sin(a) * r + 9) for a in [math.pi * q / 24 for q in range(25)]],
                  (wx0 - 9, cy_, wx0 + 9, wfoot), (wx1 - 9, cy_, wx1 + 9, wfoot), (wx0, wfoot - 44, wx1, wfoot + 18))
    _bay(c, -10, wx1 + 30, wfoot + 18, floor, 1.4, "panel")                       # panelling under the window
    # the hero: two tiers of teal bookcases, a gallery between them, warm lamps along it
    bx0, bx1 = 394.0, 836.0
    t1, mid_y = 300.0, 630.0
    for i in range(3):
        x0 = bx0 + i * (bx1 - bx0) / 3
        bookcase(c, x0 + 4, x0 + (bx1 - bx0) / 3 - 4, t1, mid_y - 10, 1.25, seed=40 + i)
        bookcase(c, x0 + 4, x0 + (bx1 - bx0) / 3 - 4, mid_y + 26, floor, 1.25, seed=50 + i)
    c.add(f'<rect x="{bx0 - 10}" y="{mid_y - 12}" width="{bx1 - bx0 + 20}" height="34" fill="{P.TEAL}" '
          f'stroke="{INK}" stroke-width="2"/>')                                           # the gallery's front
    st.keep_clear((bx0 - 12, t1, bx1, floor))
    for x in range(int(bx0), int(bx1), 26):
        c.line(f"M{x},{mid_y - 12} v-34", 3, darken(P.TEAL, 0.7))
    c.line(f"M{bx0 - 10},{mid_y - 46} H{bx1 + 10}", 6, darken(P.TEAL, 0.7))
    for sx in (bx0 + 10, bx0 + (bx1 - bx0) / 3, bx0 + 2 * (bx1 - bx0) / 3, bx1 - 14):
        c.shape(f"M{sx - 9},{mid_y - 70} h18 l-4,24 h-10 Z", P.SUN, sw=1.4, light=None)    # lamps on the rail
        glow(c, sx, mid_y - 56, 9)
    for sx in (bx0 + (bx1 - bx0) / 3, bx0 + 2 * (bx1 - bx0) / 3):
        c.shape(f"M{sx - 8},{mid_y + 44} h16 l-4,22 h-8 Z", P.SUN, sw=1.4, light=None)
        glow(c, sx, mid_y + 58, 8)
    ladder(c, 552, mid_y + 32, 552, floor, 1.75, rail=(bx0, bx1), rolling=True)
    # the floor: parquet, the skirting board under the bookcases
    paving(c, -6, W + 6, floor, H + 4, 1.8, seed=4, tones=BOARDS)
    c.add(f'<rect x="-6" y="{floor - 3}" width="{W + 12}" height="8" fill="{P.WOOD_DARK}" stroke="{INK}" '
          f'stroke-width="1.4"/>')
    # the cast, spread across the floor
    prof = st.actor("professor", 140, 1096, "explain", "talk", tall=330)
    st.speaker(prof, width=72, left=8, air=CLEAR_MM)
    st.actor("agent", 552, 820, "cheer", "smile", flip=True, tall=300, group="ladder")
    st.actor("caterpillar", 660, 1130, "present", "worry", flip=True, tall=280, group="caterpillar")
    cat = st.actor("cat", 370, 1160, "present", "smile", flip=False, tall=270, group="cat")
    st.hold(cat, handheld.stopwatch)
    st.actor("sparrow", 390, 470, "fly", "smile", tall=120, group="sparrow")
    st.put(472, f'<path d="M396,450 q10,14 0,30 q-6,10 4,18" fill="none" stroke="{P.RED}" stroke-width="5" '
           f'stroke-linecap="round"/>', None, group="sparrow")                               # its ribbon bookmark
    st.put(0.9, f'<g transform="rotate(-18 790 830)">{card(770, 830, 1.6)}</g>' + motion(760, 810, 30, 1.2,
           way=-1, vertical=True), (750, 780, 840, 845), "card")
    drawn = st.render()
    drawn.holders, drawn.links, drawn.ports = st.holders, st.links, st.ports
    return drawn


LIBRARY.stations.extend([
    Station("sheet", _framed(sheet_station), ("pin", "read")),
    Station("near", _framed(near_station), ("desk", "stacks")),
    Station("aisles", _framed(aisles_station), ("sign",)),
    Station("catalogue", _framed(catalogue_station), ("pull", "follow")),
    Station("archive", _framed(archive_station), ("file", "doubt")),
    Station("notes", _framed(notes_station), ("read", "stick")),
    Station("sort", _framed(sort_station), ("sort",)),
    Station("docs", _framed(docs_station), ("shelf",)),
    Station("check", _framed(check_station), ("find", "twice")),
])
LIBRARY.backdrop = backdrop
LIBRARY.alternate = True                                     # never one moment on two pages in a row
LIBRARY.finale = finale
OPENERS["reading_room"] = opener
hide(LIBRARY, "check", "find")

"""The moon base: the world of chapter 9 (review: agents check, people own).

A base on the Moon under a black sky full of stars with the Earth hanging in it: pressurised modules with round
hatches, a glass-domed greenhouse, antennas, landing pads and rovers on the grey regolith with its craters and
tracks. The cast stays inside, on the base's decks behind a low indigo wall under the glass; outside the rovers do
the work. Code arriving at the base is a cargo capsule from Earth; review is checking it before it comes in. The
stations, one per section of the chapter:

1. pile       review no longer works as it used to: capsules come out of the airlock faster than the professor can
              open and read them one by one at his desk - the heap grows;
2. learn      learning the project needs no review: in the briefing room the agent explains a module on the big
              screen to the caterpillar;
3. decide     agents check, a person takes the key decisions: out of the window the rovers inspect the capsules,
              at the console the professor has the two buttons - accept or reject;
4. rover      a subagent is an independent reviewer: an inspection rover of its own, with its own power and
              aerial and no line to the base, scans a capsule in its bay;
5. tunnel     reviewers in CI: the conveyor carries every capsule through three scanning arches in a row, each a
              different instrument;
6. shared     one reviewer for every repository: out of the window one inspection rover drives the road between
              the landing pads of several bases;
7. sign       who owns, who approves, who merges: the agent signs the delivery note, the cat stamps the approval,
              and the airlock's inner door opens by itself once both are done;
8. keepers    code owners: every module's hatch has its keeper's name plate; a capsule for the greenhouse goes to
              the caterpillar in the greenhouse with her watering can;
9. test       checking that review works: a test capsule with a planted crack goes in - the scanner catches it, the
              cat times it.

No words in the pictures but the console's buttons, the hatches' name plates and the finale's names of the
stations.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten, mix
from . import characters, handheld, sets
from .footers import Strip
from .ink import INK, Canvas, ellipse_d, lettering, n, rounded_rect_d
from .openers import CLEAR_MM, H, OPENERS, W, Stage
from .world_fair import held, lane, zoom
from .world_harbour import fx, middle, place, room
from .world_kit import SIZE, Pen, hide, ledger, stash_along, tag_size
from .world_kitchen import _box, low
from .world_sea import beside, sparrow_on
from .world_base import Station, world

MOON = world("moon", opener="lunar_base")

_at = sets._at

INDIGO = P.INDIGO
SKY = mix(P.SPACE_DEEP, INDIGO, 0.25)              # the black sky, a touch of indigo
SKY_LOW = mix(P.SPACE_DEEP, INDIGO, 0.55)
REGOLITH = mix(P.STONE, P.METAL_LIGHT, 0.35)        # the grey dust of the Moon
REGOLITH_DARK = darken(REGOLITH, 0.78)
DECK = mix(P.METAL, INDIGO, 0.18)                   # the base's deck plates
WALL = mix(INDIGO, P.METAL_DARK, 0.25)              # the low wall under the glass
HULL = mix(P.WHITE, INDIGO, 0.12)                   # the modules' white skin
WARM = mix(P.SUN, P.YELLOW_PALE, 0.4)               # the warm light inside


def far(color: str) -> str:
    """A colour of the far base, paler with the distance."""
    return mix(color, REGOLITH, 0.35)


# ============================================================================ the place behind every frame
def crater(c: Canvas, x: float, y: float, r: float, color: str = REGOLITH) -> None:
    """A crater on the regolith seen low: a flat ellipse, its far inner wall in shadow, its near rim lit."""
    c.add(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(r)}" ry="{n(r * 0.28)}" fill="{darken(color, 0.82)}"/>'
          f'<path d="M{n(x - r)},{n(y)} A{n(r)},{n(r * 0.28)} 0 0 1 {n(x + r)},{n(y)} A{n(r * 0.8)},{n(r * 0.18)} '
          f'0 0 0 {n(x - r)},{n(y)} Z" fill="{darken(color, 0.62)}"/>'
          f'<path d="M{n(x - r * 0.96)},{n(y + r * 0.06)} A{n(r)},{n(r * 0.28)} 0 0 0 {n(x + r * 0.96)},'
          f'{n(y + r * 0.06)}" fill="none" stroke="{lighten(color, 0.25)}" stroke-width="{n(max(1.0, r * 0.08))}"/>')


def module_far(c: Canvas, x: float, ground: float, k: float, color: str = INDIGO, lit: bool = True) -> None:
    """A pressurised module of the far base: a white cylinder lying on its legs with rounded ends, an indigo band,
    a round hatch and lit portholes."""
    d = Canvas()
    d.shape("M-40,-8 V-30 Q-40,-38 -32,-38 H32 Q40,-38 40,-30 V-8 Z", far(HULL), sw=1, light=None)
    d.add(f'<rect x="-40" y="-26" width="80" height="5" fill="{far(color)}"/>')
    d.add(f'<circle cx="-24" cy="-17" r="4" fill="{far(P.METAL_DARK)}" stroke="{INK}" stroke-width=".6"/>')
    for px in (0, 14, 28):
        d.add(f'<circle cx="{px}" cy="-17" r="2.2" fill="{WARM if lit else far(P.LENS)}"/>')
    d.line("M-30,-8 L-34,0 M30,-8 L34,0", 1.4, far(P.METAL_DARK))
    c.add(_at(d, x, ground, k))


def dish_far(c: Canvas, x: float, ground: float, k: float) -> None:
    """A far aerial: a lattice mast with a dish turned up to the Earth."""
    d = Canvas()
    d.line("M-6,0 L0,-40 L6,0 M-4,-12 H4 M-2,-26 H2", 1.2, far(P.METAL_DARK))
    d.add(f'<path d="M-14,-44 Q0,-30 14,-50 Z" fill="{far(P.WHITE)}" stroke="{INK}" stroke-width=".7"/>')
    d.line("M0,-41 L4,-52", 1, far(P.METAL_DARK))
    c.add(_at(d, x, ground, k))


def pad_far(c: Canvas, x: float, ground: float, k: float) -> None:
    """A far landing pad: a flat disc on the dust with its ring of lights."""
    c.add(f'<ellipse cx="{n(x)}" cy="{n(ground)}" rx="{n(34 * k)}" ry="{n(6 * k)}" fill="{far(P.METAL)}" '
          f'stroke="{INK}" stroke-width=".7"/><ellipse cx="{n(x)}" cy="{n(ground)}" rx="{n(20 * k)}" '
          f'ry="{n(3.4 * k)}" fill="none" stroke="{far(P.YELLOW)}" stroke-width="{n(max(0.8, 1.4 * k))}"/>')


def deck(c: Canvas, x0: float, x1: float, y0: float, y1: float, k: float) -> None:
    """The base's deck from y0 down: steel plates in rows, nearer rows deeper, their seams and corner bolts, a
    yellow-and-black safety edge at the back."""
    c.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" fill="{darken(DECK, 0.85)}"/>')
    y, row = y0 + 6 * k, 0
    while y < y1:
        rh = (8 + row * 4) * max(0.6, k)
        pw = (70 + row * 18) * k
        x = x0 - (row % 2) * pw / 2
        while x < x1:
            c.add(f'<rect x="{n(x + 1)}" y="{n(y + 1)}" width="{n(pw - 2)}" height="{n(rh - 2)}" '
                  f'fill="{DECK if (row + int(x / pw)) % 2 else lighten(DECK, 0.06)}"/>')
            if rh > 9:
                c.add("".join(f'<circle cx="{n(bx)}" cy="{n(y + rh / 2)}" r="{n(rh * 0.07)}" fill="{INK}" '
                              f'fill-opacity=".4"/>' for bx in (x + 5, x + pw - 5)))
            x += pw
        y += rh
        row += 1
    c.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(6 * k)}" fill="{P.YELLOW}"/>')
    c.line(" ".join(f"M{n(q)},{n(y0 + 6 * k)} l{n(6 * k)},{n(-6 * k)}" for q in range(int(x0), int(x1), int(14 * k)
                                                                                    or 1)),
           max(1.0, 3 * k), INK)


INNER = mix(INDIGO, P.WHITE, 0.18)                  # the module's inner hull panels


def backdrop(s: Strip, index: int) -> None:
    """Inside a module of the base: the curved hull wall in indigo panels with its ribs bowing over, a seam along
    it, the ceiling's band with its warm light panels at the top, a skirting rail along the floor, and the steel
    deck plates the cast stands on. The cast keeps the stations room. The Moon is seen only through the windows
    and portholes the stations and `_framed` put into the wall."""
    ledger(s)
    zoom(s)
    feet = lane(s).feet
    names = ("cat", "agent", "caterpillar") if low(s) else ("professor", "cat", "agent", "caterpillar")
    if low(s):                                                         # a close-up: the cast nearly fills it
        top = max(_box(s, name, 0, feet)[3] - _box(s, name, 0, feet)[1] for name in names)
        s.tall *= (feet - 6) / top
    widest = max(_box(s, name, 0, feet)[2] - _box(s, name, 0, feet)[0] for name in names)
    s.tall *= min(1.0, (s.hi - s.lo) * 0.19 / widest)                  # two of them take two fifths at most
    s.unit = s.tall / 137
    s.index = index
    c = s.back
    base = s.base
    k = max(0.6, min(1.4, base / 240))
    s.ceil = max(8.0, base * 0.08)
    c.add(f'<rect x="-6" y="-6" width="{W + 12}" height="{n(base + 8)}" fill="{INNER}"/>')
    paint = c.gradient([(0, darken(INNER, 0.82)), (0.35, INNER), (1, lighten(INNER, 0.06))], 0, 0, 0, base)
    c.add(f'<rect x="-6" y="-6" width="{W + 12}" height="{n(base + 8)}" fill="{paint}"/>')
    step = 150 * k
    rnd = random.Random(index * 7 + 1)
    x = -(index * 37) % step
    while x < W + step:                                               # the hull's panels, lighter and darker
        for y0_, y1_ in ((s.ceil + 4, base * 0.55), (base * 0.55, base - 7 * k)):
            tone = rnd.choice((lighten(INNER, 0.07), INNER, darken(INNER, 0.93), lighten(INNER, 0.03)))
            c.add(f'<rect x="{n(x - step + 6 * k)}" y="{n(y0_ + 2)}" width="{n(step - 12 * k)}" '
                  f'height="{n(y1_ - y0_ - 4)}" rx="{n(3 * k)}" fill="{tone}" stroke="{darken(INNER, 0.8)}" '
                  f'stroke-width="1"/>')
            for rx_ in (x - step + 11 * k, x - 11 * k):
                for ry_ in (y0_ + 6 * k, y1_ - 6 * k):
                    c.add(f'<circle cx="{n(rx_)}" cy="{n(ry_)}" r="{n(1.2 * k)}" fill="{darken(INNER, 0.65)}"/>')
        x += step
    x = -(index * 37) % step
    while x < W + step:                                               # the ribs, bowing over to the ceiling
        c.add(f'<path d="M{n(x)},{n(base)} V{n(base * 0.4)} Q{n(x)},{n(s.ceil + 6)} {n(x + 30 * k)},{n(s.ceil)}" '
              f'fill="none" stroke="{darken(INNER, 0.72)}" stroke-width="{n(9 * k)}"/>'
              f'<path d="M{n(x - 2 * k)},{n(base)} V{n(base * 0.4)}" fill="none" stroke="{lighten(INNER, 0.2)}" '
              f'stroke-width="{n(2 * k)}"/>')
        for by in (base * 0.3, base * 0.62, base * 0.9):
            c.add(f'<circle cx="{n(x)}" cy="{n(by)}" r="{n(1.6 * k)}" fill="{darken(INNER, 0.6)}"/>')
        x += step
    c.line(f"M-6,{n(base * 0.55)} H{W + 6}", max(1.0, 1.4 * k), darken(INNER, 0.8))
    c.add(f'<rect x="-6" y="-6" width="{W + 12}" height="{n(s.ceil + 6)}" fill="{darken(WALL, 0.8)}"/>')
    for q in range(int(W / (200 * k)) + 1):                           # the ceiling's light panels
        lx = q * 200 * k + 60 * k
        c.add(f'<rect x="{n(lx)}" y="{n(s.ceil - 5 * k)}" width="{n(70 * k)}" height="{n(4 * k)}" rx="2" '
              f'fill="{WARM}"/>')
    py = s.ceil + 5 * k                                               # the pipes and cable tray along the ceiling
    c.line(f"M-6,{n(py)} H{W + 6}", 5 * k, P.METAL_LIGHT)
    c.line(f"M-6,{n(py + 7 * k)} H{W + 6}", 3.4 * k, mix(P.ORANGE, P.METAL, 0.4))
    c.add(f'<rect x="-6" y="{n(py + 11 * k)}" width="{W + 12}" height="{n(3 * k)}" fill="{P.METAL_DARK}"/>')
    for q in range(3 + index % 3):                                    # clamps and valves on them
        vx = rnd.uniform(20, W - 20)
        c.add(f'<rect x="{n(vx - 3 * k)}" y="{n(py - 4 * k)}" width="{n(6 * k)}" height="{n(14 * k)}" '
              f'fill="{P.METAL_DARK}"/>')
        if q % 2 == 0:
            c.add(f'<circle cx="{n(vx + 30 * k)}" cy="{n(py + 7 * k)}" r="{n(4 * k)}" fill="none" '
                  f'stroke="{P.RED}" stroke-width="{n(1.6 * k)}"/><line x1="{n(vx + 26 * k)}" y1="{n(py + 7 * k)}" '
                  f'x2="{n(vx + 34 * k)}" y2="{n(py + 7 * k)}" stroke="{P.RED}" stroke-width="{n(1.2 * k)}"/>')
    c.add(f'<rect x="-6" y="{n(base - 7 * k)}" width="{W + 12}" height="{n(7 * k)}" fill="{P.METAL_DARK}"/>')
    deck(c, -6, W + 6, base, s.h + 4, max(0.8, s.unit))


def view(c: Canvas, x0: float, y0: float, x1: float, y1: float, seed: int, earth_: bool = True,
         things=None, high: float = 0.58) -> tuple[float, float]:
    """What a window shows, clipped to (x0, y0, x1, y1): the black sky deepening up, stars, the Earth now and then,
    the grey Moon with its craters and the base's far modules on the horizon; `things(c, horizon, ground)` draws
    what is out there today. Returns the horizon and the near ground's line."""
    h = y1 - y0
    horizon = y0 + h * high
    ground = y1 - h * 0.08
    k = h / 120
    rnd = random.Random(seed)
    paint = c.gradient([(0, mix(P.SPACE_DEEP, INK, 0.4)), (1, SKY_LOW)], 0, y0, 0, horizon)
    c.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(horizon - y0 + 1)}" fill="{paint}"/>')
    sets.stars(c, (x0, y0, x1, horizon - 6), max(3, int((x1 - x0) / 30)), seed=seed)
    if earth_ and x1 - x0 > 80:
        big_earth(c, x1 - (x1 - x0) * 0.2, y0 + h * 0.24, h * 0.13)
    c.add(f'<rect x="{n(x0)}" y="{n(horizon)}" width="{n(x1 - x0)}" height="{n(y1 - horizon)}" fill="{REGOLITH}"/>')
    c.add(f'<path d="M{n(x0)},{n(horizon + 1)} Q{n(x0 + (x1 - x0) * 0.3)},{n(horizon - 8 * k)} '
          f'{n((x0 + x1) / 2)},{n(horizon - 2 * k)} T{n(x1)},{n(horizon - 3 * k)} V{n(horizon + 3)} H{n(x0)} Z" '
          f'fill="{REGOLITH_DARK}"/>')
    for _ in range(max(1, int((x1 - x0) / 90))):
        crater(c, rnd.uniform(x0, x1), rnd.uniform(horizon + (y1 - horizon) * 0.4, y1 - 2), rnd.uniform(6, 14) * k,
               color=mix(REGOLITH, INDIGO, 0.12))
    if things:
        things(c, horizon, ground)
    else:
        for q in range(max(1, int((x1 - x0) / 140))):
            module_far(c, x0 + (q + 0.5) * (x1 - x0) / max(1, int((x1 - x0) / 140)), horizon + 4 * k, k * 0.5)
    return horizon, ground


def window(s: Strip, box: tuple, seed: int = 0, things=None, earth_: bool = True, round_: bool = False,
           high: float = 0.58) -> None:
    """A window in the hull wall at `box` (page space): the Moon outside it (`view`), its thick frame of indigo steel
    with bolts all round, the glass's reflection; round, a porthole. Behind the stations and the cast."""
    x0, y0, x1, y1 = box
    c = Canvas()
    r = min(x1 - x0, y1 - y0) / 2 if round_ else min(14.0, (y1 - y0) * 0.18)
    clip = c.shape(rounded_rect_d(x0, y0, x1 - x0, y1 - y0, r), SKY, sw=0, light=None, clip=True)
    c.add(f'<g clip-path="url(#{clip})">')
    view(c, x0, y0, x1, y1, seed, earth_=earth_, things=things, high=high)
    c.add(f'<path d="M{n(x0 + (x1 - x0) * 0.1)},{n(y1)} L{n(x0 + (x1 - x0) * 0.3)},{n(y0)} H{n(x0 + (x1 - x0) * 0.38)} '
          f'L{n(x0 + (x1 - x0) * 0.18)},{n(y1)} Z" fill="{P.WHITE}" fill-opacity=".08"/></g>')
    fw = max(4.0, min(12.0, (y1 - y0) * 0.07))
    frame_d = rounded_rect_d(x0 - fw / 2, y0 - fw / 2, x1 - x0 + fw, y1 - y0 + fw, r + fw / 2)
    c.add(f'<path d="{frame_d}" fill="none" stroke="{INK}" stroke-width="{n(fw + 2.6)}"/>'
          f'<path d="{frame_d}" fill="none" stroke="{mix(WALL, P.METAL, 0.4)}" stroke-width="{n(fw)}"/>')
    if not round_:
        for bx in (x0 - fw / 2, x1 + fw / 2):
            for by in (y0 + r, y1 - r):
                c.add(f'<circle cx="{n(bx)}" cy="{n(by)}" r="{n(fw * 0.18)}" fill="{P.METAL_LIGHT}"/>')
    s.put(0.5, c.render(), None)




def height(s: Strip, name: str) -> float:
    """How tall a character stands in this frame."""
    b = _box(s, name, 0, lane(s).feet)
    return b[3] - b[1]


def fitting(s: Strip, kind: str, x: float, u: float) -> tuple | None:
    """One fitting of the module's wall at x, sized against the professor standing in the frame: a porthole, a row
    of lockers, a ladder up to a hatch in the ceiling, a telemetry monitor, a fire extinguisher, a shelf of storage
    bins, a hydroponic shelf, the hatch to the next module. Returns its box and its drawing, or None if it does not
    fit the wall at its true size."""
    top, floor = s.ceil + 16 * u, s.base - 7 * u
    wall = floor - top
    pr = pr_(s)
    rnd = random.Random(int(x) * 3 + getattr(s, "index", 0))
    c = Canvas()
    if kind == "porthole":
        rr = min(wall * 0.32, pr * 0.22) * rnd.uniform(0.7, 1.0)
        cy = top + wall * rnd.uniform(0.3, 0.45)
        if rr < 10:
            return None
        return (x - rr - 5, cy - rr - 5, x + rr + 5, cy + rr + 5), ("porthole", (x - rr, cy - rr, x + rr, cy + rr))
    if kind == "lockers":
        h = pr * 0.95
        if h > wall:
            return None
        count = rnd.choice((2, 3, 4))
        lw = h * 0.24
        x0 = x - count * lw / 2
        for q in range(count):
            lx = x0 + q * lw
            d = Canvas()
            d.shape(rounded_rect_d(0, -100, 23, 100, 1.5), mix(P.METAL_LIGHT, INDIGO, 0.15 + 0.08 * (q % 2)), sw=1.3,
                    light=(-1, -1))
            d.line(" ".join(f"M4,{-92 + v * 3.4} h15" for v in range(5)), 1.1, INK, 0.55)      # its louvres
            d.line(" ".join(f"M4,{-14 + v * 3.4} h15" for v in range(3)), 1.1, INK, 0.55)
            d.shape(rounded_rect_d(5, -72, 13, 7, 1), P.WHITE, sw=0.8, light=None)             # its name label
            d.line("M7,-69.5 h8", 0.8, INK, 0.5)
            d.shape(rounded_rect_d(17, -54, 3, 12, 1), P.METAL_DARK, sw=0.6, light=None)       # the handle
            if q == count - 1:                                                               # a padlock
                d.add(f'<path d="M16,-41 a3,3 0 0 1 6,0 v2" fill="none" stroke="{P.METAL_DARK}" '
                      f'stroke-width="1.2"/>')
                d.shape(rounded_rect_d(15, -40, 8, 7, 1), P.YELLOW, sw=0.7, light=None)
            if q == 0:                                                                       # a sticker
                d.add(f'<circle cx="11" cy="-30" r="3.6" fill="{P.ORANGE}" stroke="{INK}" stroke-width=".6"/>'
                      f'<path d="M9,-30 l1.4,1.4 l2.8,-2.8" stroke="{P.WHITE}" stroke-width="1" fill="none"/>')
            d.add("".join(f'<circle cx="{cx}" cy="{cy}" r=".9" fill="{INK}" fill-opacity=".5"/>'
                          for cx in (2.5, 20.5) for cy in (-97, -3)))
            c.add(_at(d, lx, floor, h / 100))
        box = (x0 - 1, floor - h - 1, x0 + count * lw + 1, floor)
    elif kind == "ladder":
        w = pr * 0.16
        c.line(f"M{n(x - w / 2)},{n(floor)} V{n(s.ceil + 2)} M{n(x + w / 2)},{n(floor)} V{n(s.ceil + 2)}", 2.6 * u,
               P.METAL_DARK)
        c.line(" ".join(f"M{n(x - w / 2)},{n(y_)} h{n(w)}" for y_ in range(int(floor - 10 * u), int(s.ceil + 6),
                                                                        -int(pr * 0.1) or -1)), 2 * u, P.METAL)
        c.add(f'<ellipse cx="{n(x)}" cy="{n(s.ceil + 2)}" rx="{n(w)}" ry="{n(4 * u)}" fill="{P.METAL_LIGHT}" '
              f'stroke="{INK}" stroke-width="1.2"/>')
        c.line(f"M{n(x - w)},{n(s.ceil + 2)} h{n(w * 2)}", 1.4 * u, INK, 0.6)
        box = (x - w, s.ceil - 2, x + w, floor)
    elif kind == "screen":
        w = pr * 0.5
        h = w * 0.62
        cy = floor - pr * 0.82                                        # at eye level
        if cy - h / 2 < top or w < 40:
            return None
        d = Canvas()
        d.line("M50,-36 V-46 M50,-46 H60", 3, P.METAL_DARK)                                     # its bracket
        d.shape(rounded_rect_d(0, -31, 100, 62, 4), P.CHARCOAL, sw=1.6, light=None)            # the bezel
        d.shape(rounded_rect_d(5, -26, 90, 50, 2), P.SCREEN, sw=0.8, light=None)
        d.add(f'<rect x="5" y="-26" width="90" height="7" fill="{darken(P.SCREEN, 0.75)}"/>'
              f'<circle cx="10" cy="-22.5" r="1.8" fill="{P.GREEN}"/><rect x="16" y="-24" width="22" height="3" '
              f'fill="{P.SCREEN_LIGHT}"/><rect x="78" y="-24" width="12" height="3" fill="{P.YELLOW}"/>')
        d.line("M12,-15 V16 H64", 1.2, P.SCREEN_LIGHT, 0.8)                                   # the chart's axes
        d.line(" ".join(f"M12,{y_} h-2" for y_ in (-10, -2, 6, 14)), 1, P.SCREEN_LIGHT, 0.8)
        d.line("M12,10 L22,4 L30,8 L40,-4 L50,0 L62,-10", 1.6, P.GREEN)
        d.line("M12,13 L22,12 L30,6 L40,8 L50,4 L62,5", 1.6, P.ORANGE)
        for q, col in enumerate((P.GREEN, P.ORANGE, P.SCREEN_LIGHT)):                         # small readouts
            d.add(f'<rect x="70" y="{-14 + q * 11}" width="20" height="8" rx="1" fill="{darken(P.SCREEN, 0.7)}"/>'
                  f'<rect x="72" y="{-12 + q * 11}" width="{8 + q * 4}" height="4" fill="{col}"/>')
        d.line("M50,31 q0,10 10,14", 1.6, INK)                                                  # its cable
        c.add(_at(d, x - w / 2, cy, w / 100))
        box = (x - w / 2 - 1, cy - h / 2 - 10 * w / 100, x + w / 2 + 1, cy + h / 2 + 15 * w / 100)
    elif kind == "extinguisher":
        h = pr * 0.34
        y1 = floor - pr * 0.18                                        # hung off the floor on its bracket
        if y1 - h * 1.5 < top:
            return None
        d = Canvas()
        d.shape(rounded_rect_d(-14, -150, 28, 18, 2), P.RED, sw=1.2, light=None)              # the sign above
        d.add(f'<path d="M-4,-136 q-2,-6 2,-10 q1,4 3,5 q2,-3 1,-6 q5,4 3,11 Z" fill="{P.WHITE}"/>')
        d.shape(rounded_rect_d(-15, -60, 30, 8, 2), P.METAL_DARK, sw=1, light=None)           # the bracket
        d.shape("M-11,0 V-82 Q-11,-92 0,-92 Q11,-92 11,-82 V0 Z", P.RED, sw=1.6, light=None)  # the cylinder
        d.add(f'<path d="M-7,-84 V-8" stroke="{P.WHITE}" stroke-width="2.6" stroke-opacity=".45"/>'
              f'<rect x="-11" y="-50" width="22" height="18" fill="{P.WHITE}"/>'
              f'<rect x="-11" y="-50" width="22" height="4" fill="{P.CHARCOAL}"/>')            # label band
        d.line("M-7,-41 h14 M-7,-37 h10", 1, INK, 0.6)
        d.shape(rounded_rect_d(-5, -102, 10, 10, 2), P.CHARCOAL, sw=1, light=None)            # the valve head
        d.line("M-2,-102 L14,-108", 3, P.METAL_DARK)                                           # its lever
        d.add(f'<circle cx="4" cy="-99" r="2" fill="{P.YELLOW}" stroke="{INK}" stroke-width=".6"/>')   # the pin
        d.add(f'<circle cx="-8" cy="-96" r="4.4" fill="{P.WHITE}" stroke="{INK}" stroke-width="1"/>'
              f'<path d="M-8,-96 l2,-2.4" stroke="{P.RED}" stroke-width=".9"/>')                # the gauge
        d.line("M5,-96 Q20,-90 18,-60 Q16,-40 14,-30", 3.4, P.CHARCOAL)                         # the hose
        d.shape("M11,-32 L17,-32 L18,-22 L10,-22 Z", P.CHARCOAL, sw=0.8, light=None)          # its nozzle
        c.add(_at(d, x, y1, h / 92))
        box = (x - 15 * h / 92, y1 - 151 * h / 92, x + 19 * h / 92, y1)
    elif kind == "bins":
        w = pr * 0.55
        y0 = floor - pr * 0.75
        if y0 < top:
            return None
        d = Canvas()
        d.shape(rounded_rect_d(0, 22, 100, 4, 1), P.METAL_DARK, sw=1, light=None)
        d.line("M6,26 L14,36 M94,26 L86,36", 2, P.METAL_DARK)
        for q, col in enumerate((P.ORANGE, P.TEAL, P.YELLOW)):
            bx = 3 + q * 32.5
            d.shape(f"M{bx},2 H{bx + 30} L{bx + 28},22 H{bx + 2} Z", col, sw=1.2, light=None)
            d.shape(rounded_rect_d(bx + 7, 8, 16, 8, 1), P.WHITE, sw=0.7, light=None)
            d.line(f"M{bx + 9},11 h10 M{bx + 9},13.5 h7", 0.7, INK, 0.6)
            d.shape(rounded_rect_d(bx + 11, 0, 8, 3, 1), darken(col, 0.7), sw=0.6, light=None)
        c.add(_at(d, x - w / 2, y0, w / 100))
        box = (x - w / 2, y0, x + w / 2, y0 + 36 * w / 100)
    elif kind == "plants":
        w = pr * 0.6
        y0 = floor - pr * 0.78
        if y0 < top:
            return None
        d = Canvas()
        d.line("M2,0 V48 M98,0 V48", 2, P.METAL_DARK)
        d.add(f'<rect x="0" y="0" width="100" height="5" rx="2" fill="{mix(P.VIOLET, P.PINK, 0.4)}" '
              f'stroke="{INK}" stroke-width="1"/><rect x="4" y="5" width="92" height="20" '
              f'fill="{mix(P.VIOLET, P.PINK, 0.4)}" fill-opacity=".16"/>')                    # the grow light
        d.line("M50,0 V-10", 1.4, INK)                                                         # its cable
        trough(d, 4, 96, 46, ("lettuce", "herbs", "tomato")[rnd.randrange(3)])
        d.shape(rounded_rect_d(42, 38, 16, 6, 1), P.WHITE, sw=0.6, light=None)                 # a little label
        c.add(_at(d, x - w / 2, y0, w / 100))
        box = (x - w / 2, y0 - 10 * w / 100, x + w / 2, y0 + 48 * w / 100)
    else:                                                             # the hatch to the next module
        rr = pr * 0.42                                                # a person fits through, stooping
        sill_h = pr * 0.14
        cy = floor - sill_h - rr
        if cy - rr - 8 * u < top:
            return None
        d = Canvas()
        d.shape(rounded_rect_d(-62, 58, 124, 19, 3), P.METAL_DARK, sw=1.4, light=None)          # the sill step
        d.add(f'<circle cx="0" cy="0" r="58" fill="{P.YELLOW}" stroke="{INK}" stroke-width="2"/>')
        clip = d.shape(ellipse_d(0, 0, 58, 58), P.YELLOW, sw=0, light=None, clip=True)
        d.add(f'<g clip-path="url(#{clip})"><path d="' + " ".join(f"M{q},-60 l-20,120" for q in range(-80, 90, 14))
              + f'" stroke="{INK}" stroke-width="5"/></g>')                                   # warning border
        d.add(f'<circle cx="0" cy="0" r="58" fill="none" stroke="{INK}" stroke-width="2"/>'
              f'<circle cx="0" cy="0" r="48" fill="{darken(WALL, 0.7)}" stroke="{INK}" stroke-width="2"/>'
              f'<circle cx="0" cy="0" r="44" fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="1.6"/>')
        d.add(f'<circle cx="0" cy="-24" r="9" fill="{P.LENS}" stroke="{INK}" stroke-width="1.4"/>'
              f'<circle cx="0" cy="-24" r="11.5" fill="none" stroke="{P.METAL}" stroke-width="2.6"/>')
        d.add(f'<circle cx="0" cy="12" r="17" fill="none" stroke="{P.METAL_DARK}" stroke-width="3.6"/>'
              f'<circle cx="0" cy="12" r="4" fill="{P.METAL_DARK}"/>')
        d.line(" ".join(f"M{n(math.cos(math.radians(a)) * 4)},{n(12 + math.sin(math.radians(a)) * 4)} "
                        f"L{n(math.cos(math.radians(a)) * 17)},{n(12 + math.sin(math.radians(a)) * 17)}"
                        for a in range(0, 360, 60)), 2.4, P.METAL_DARK)                     # wheel spokes
        for a in range(20, 360, 45):                                                          # dog latches
            ax, ay = math.cos(math.radians(a)) * 46, math.sin(math.radians(a)) * 46
            d.add(f'<rect x="{n(ax - 3)}" y="{n(ay - 3)}" width="6" height="6" rx="1" fill="{P.METAL_DARK}" '
                  f'transform="rotate({a} {n(ax)} {n(ay)})"/>')
        for hy in (-26, 26):                                                                  # its hinges
            d.shape(rounded_rect_d(-62, hy - 6, 12, 12, 2), P.METAL_DARK, sw=1, light=None)
        c.add(_at(d, x, cy, rr / 58))
        k_ = rr / 58
        box = (x - 63 * k_, cy - 59 * k_, x + 59 * k_, floor)
    if box[1] < s.ceil - 4:
        return None
    return box, ("svg", c.render())


def portholes(s: Strip) -> None:
    """The module's wall furnished, differently on every page and only where the wall shows free between the
    stations and the cast: portholes of different sizes, lockers, a ladder to the ceiling hatch, telemetry screens,
    an extinguisher, storage bins, a hydroponic shelf, the hatch to the next module - four at most."""
    rnd = random.Random(s.seed * 31 + getattr(s, "index", 0) * 7)
    kinds = ["porthole", "porthole", "lockers", "ladder", "screen", "extinguisher", "bins", "plants", "hatch"]
    rnd.shuffle(kinds)
    spots = [i / 20 for i in range(1, 20)]
    rnd.shuffle(spots)
    u = max(0.6, s.unit)
    made = 0
    for kind in kinds:
        for f in spots:
            got = fitting(s, kind, s.x(f), u)
            if not got:
                break
            box, (how, what) = got
            if box[0] < 4 or box[2] > W - 4 or not s.free(box, 8):
                continue
            if how == "porthole":
                window(s, what, seed=int(box[0]), earth_=made == 0, round_=True)
            else:
                s.put(0.5, what, None)
            s.put(0.5, "", box, f"fitting{made}", group=f"fitting{made}", backdrop=True)
            made += 1
            break
        if made == 4:
            return


def alarm(s: Strip, x: float, y: float, k: float, sparrow: bool) -> bool:
    """The emergency airlock-close button on the wall at (x, y): a yellow-and-black striped plate, the big red
    mushroom button under its clear flip cover - and, if `sparrow`, the sparrow fluttering up to it, one wing
    reaching for the cover. Only where the wall is free; returns whether it went up."""
    way = -1 if x > W / 2 else 1                                       # the sparrow comes from the room's side
    box = (x - 16 * k, y - 22 * k, x + 16 * k, y + 18 * k)
    bird = (min(x + way * 12 * k, x + way * 70 * k), y - 50 * k, max(x + way * 12 * k, x + way * 70 * k), y + 20 * k)
    if (not s.free(box, 6) or (sparrow and not s.free(bird, 4)) or box[0] < 4 or box[2] > W - 4
            or bird[0] < 4 or bird[2] > W - 4 or box[1] < s.ceil):
        return False
    c = Canvas()
    d = Canvas()
    d.shape(rounded_rect_d(-15, -16, 30, 32, 3), P.YELLOW, sw=1.4, light=None)
    d.line("M-15,-8 L-7,-16 M-15,2 L3,-16 M-15,12 L13,-16 M-7,16 L15,-6 M3,16 L15,4", 2.4, INK, 0.85)
    d.add(f'<circle cx="0" cy="0" r="9" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="1.2"/>'
          f'<circle cx="0" cy="-1" r="7" fill="{P.RED}" stroke="{INK}" stroke-width="1.2"/>'
          f'<circle cx="-2.4" cy="-3.4" r="2" fill="{P.WHITE}" fill-opacity=".7"/>')
    d.add(f'<path d="M-11,-12 L-13,-22 H13 L11,-12" fill="{P.LENS}" fill-opacity=".4" stroke="{INK}" '
          f'stroke-width="1"/>')                                                                  # its flip cover
    c.add(_at(d, x, y, k))
    s.put(lane(s).feet - 0.4, c.render(), box, "alarm", group="alarm")
    if sparrow:
        s.actor("sparrow", x + way * 40 * k, y + 20 * k, "fly", "smile", flip=way < 0,
                tall=min(s.tall * SIZE["sparrow"], 70 * k), group="alarm")
    return True


# ============================================================================ the things
def cargo(c: Canvas, x: float, foot: float, k: float, color: str = INDIGO, crack: bool = False,
          open_: bool = False, turn: float = 0) -> dict:
    """A cargo capsule from Earth standing at (x, foot), 44 wide and 58 tall: a steel drum with rolled rings, two
    carrying handles, an indigo band with the shipping label, the screwed lid on top - or the lid off and papers
    sticking out (`open_`); `crack`: a crack across its side, ringed in red paint and taped - the planted fault.
    Returns its box."""
    d = Canvas()
    d.shape("M-20,0 V-50 Q-20,-54 -16,-54 H16 Q20,-54 20,-50 V0 Z", P.METAL_LIGHT, sw=1.6, light=(-1, -1),
            shade_k=0.84, highlight="M-14,-48 V-6")
    for ry in (-44, -10):
        d.line(f"M-20,{ry} H20", 2.2, P.METAL)
    d.add(f'<rect x="-20" y="-34" width="40" height="12" fill="{color}"/>')
    d.shape(rounded_rect_d(-10, -32, 14, 8, 1), P.WHITE, sw=0.8, light=None)                    # the label
    d.line("M-8,-29.5 h10 M-8,-27 h7", 0.7, INK, 0.6)
    for hx in (-22, 22):                                                                       # the handles
        d.line(f"M{hx},-40 q{-2 if hx < 0 else 2},-6 0,-12", 2, P.METAL_DARK)
    if open_:
        d.shape("M-14,-54 L-12,-64 L-2,-60 L0,-54 Z", P.WHITE, sw=0.9, light=None)              # papers
        d.shape("M2,-54 L6,-66 L14,-62 L10,-54 Z", P.CARD, sw=0.9, light=None)
        d.shape(rounded_rect_d(16, -66, 18, 5, 2), P.METAL, sw=1, light=None, )                 # the lid, off
    else:
        d.shape(rounded_rect_d(-17, -58, 34, 5, 2), P.METAL, sw=1.2, light=None)                # the lid
    if crack:
        d.line("M-12,-16 l5,-4 l2,5 l6,-6 l3,4 l5,-3", 1.4, INK)
        d.add(f'<ellipse cx="-1" cy="-17" rx="16" ry="8" fill="none" stroke="{P.RED}" stroke-width="2"/>')
    c.add(_at(d, x, foot, k, turn=turn))
    return {"box": (x - 23 * k, foot - (68 if open_ else 59) * k, x + (35 if open_ else 23) * k, foot)}


















def telescope(c: Canvas, x: float, foot: float, k: float, way: int = 1) -> dict:
    """A telescope on its tripod at (x, foot), 70 tall: the white tube with its dew cap pointed out of the window
    and up a little towards `way`, the eyepiece and the finder scope. Returns its box."""
    d = Canvas()
    d.line("M-18,0 L0,-46 L18,0 M0,-46 V0", 2, P.METAL_DARK)
    d.add('<g transform="translate(0,-50) rotate(-12)">')
    d.shape(rounded_rect_d(-26, -7, 56, 14, 3), P.WHITE, sw=1.4, light=None)
    d.shape(rounded_rect_d(30, -9, 12, 18, 2), P.CHARCOAL, sw=1.2, light=None)
    d.shape(rounded_rect_d(-34, -4, 8, 8, 2), P.CHARCOAL, sw=1, light=None)
    d.shape(rounded_rect_d(-6, -15, 22, 6, 2), P.METAL, sw=1, light=None)
    d.add("</g>")
    c.add(_at(d, x, foot, k, mirror=way < 0))
    return {"box": (x - 36 * k, foot - 68 * k, x + 44 * k, foot)}




DOOR_CLEAR = 134        # a door's clear height in its own units: 1.3 times the tallest of the cast


def bulkhead(c: Canvas, x: float, foot: float, k: float, open_: float = 0.0, plate: bool = False) -> dict:
    """The inner door of an airlock or a module set into the hull wall at (x, foot), 128 wide and 150 tall (162 with
    its name plate): the heavy frame striped yellow and black round a tall pressure door with rounded corners, its
    round window, the locking wheel with its spokes, the dogs along its edges, the hinges, the raised sill at its
    foot; beside it the control panel with its lit screen and the green and red buttons. `open_` from 0 shut to 1
    slid right back into the wall, the lit inside of the airlock beyond; `plate`: a blank name plate over the
    door. Returns its box, the plate's place and the door's middle."""
    d = Canvas()
    d.shape("M-46,0 V-140 Q-46,-150 -36,-150 H36 Q46,-150 46,-140 V0 Z", darken(WALL, 0.85), sw=2, light=None)
    fr = "M-40,-4 V-122 Q-40,-144 -18,-144 H18 Q40,-144 40,-122 V-4 Z"                       # the frame
    d.shape(fr, P.YELLOW, sw=2, light=None)
    stripes = "".join(f"M{q},-150 l-14,14" for q in range(-40, 60, 10))
    clip = d.shape(fr, P.YELLOW, sw=0, light=None, clip=True)
    d.add(f'<g clip-path="url(#{clip})"><path d="{stripes}" stroke="{INK}" stroke-width="3"/></g>')
    d.path(fr, "none", 2)
    door_d = "M-33,-6 V-120 Q-33,-137 -16,-137 H16 Q33,-137 33,-120 V-6 Z"
    clip = d.shape(door_d, mix(WARM, WALL, 0.45), sw=1.6, light=None, clip=True)
    d.add(f'<g clip-path="url(#{clip})"><rect x="-33" y="-137" width="66" height="131" '
          f'fill="{mix(WARM, WALL, 0.45)}"/><rect x="-33" y="-40" width="66" height="34" fill="{darken(WALL, 0.7)}"/>')
    shift = 64 * min(1.0, open_)
    d.add(f'<g transform="translate({n(shift)},0)">')
    d.shape(door_d, P.METAL_LIGHT, sw=1.8, light=(-1, -1))
    d.add(f'<circle cx="0" cy="-108" r="12" fill="{P.LENS}" stroke="{INK}" stroke-width="1.8"/>'
          f'<circle cx="0" cy="-108" r="15.5" fill="none" stroke="{P.METAL}" stroke-width="3.4"/>'
          f'<path d="M-6,-114 L-2,-104" stroke="{P.WHITE}" stroke-width="2" stroke-opacity=".7"/>')
    d.add(f'<circle cx="0" cy="-62" r="13" fill="none" stroke="{P.METAL_DARK}" stroke-width="3.4"/>'
          f'<circle cx="0" cy="-62" r="3.4" fill="{P.METAL_DARK}"/>')
    d.line(" ".join(f"M{n(math.cos(math.radians(a)) * 3)},{n(-62 + math.sin(math.radians(a)) * 3)} "
                    f"L{n(math.cos(math.radians(a)) * 13)},{n(-62 + math.sin(math.radians(a)) * 13)}"
                    for a in range(0, 360, 60)), 2.2, P.METAL_DARK)                                  # its spokes
    for dy in (-118, -86, -40, -18):                                                           # the dogs
        d.shape(rounded_rect_d(26, dy, 6, 10, 2), P.METAL_DARK, sw=0.8, light=None)
    d.add("</g></g>")
    for hy in (-110, -30):                                                                     # the hinges
        d.shape(rounded_rect_d(-38, hy, 6, 14, 2), P.METAL_DARK, sw=0.9, light=None)
    d.shape(rounded_rect_d(-44, -6, 88, 8, 2), P.METAL_DARK, sw=1.2, light=None)                # the sill
    d.shape(rounded_rect_d(52, -98, 22, 40, 3), P.CHARCOAL, sw=1.3, light=None)                 # control panel
    d.shape(rounded_rect_d(55, -94, 16, 12, 1.5), P.SCREEN_LIGHT, sw=0.7, light=None)
    d.line("M57,-90 h8 M57,-86 h11", 1, P.WHITE, 0.7)
    d.add(f'<circle cx="58" cy="-72" r="3.4" fill="{P.GREEN}" stroke="{INK}" stroke-width=".8"/>'
          f'<circle cx="68" cy="-72" r="3.4" fill="{P.RED}" stroke="{INK}" stroke-width=".8"/>')
    if plate:
        d.shape(rounded_rect_d(-40, -164, 80, 14, 2), P.CARD, sw=1.2, light=None)
    c.add(_at(d, x, foot, k))
    return {"box": (x - 47 * k, foot - (165 if plate else 151) * k, x + 75 * k, foot),
            "plate": (x, foot - 157 * k, 80 * k), "hatch": (x, foot - 70 * k)}


def desk(c: Canvas, x: float, foot: float, k: float, opened: bool) -> dict:
    """A work desk on the deck at (x, foot), 112 wide and 62 high: a steel top on two drawer pedestals, a desk lamp
    with its warm light, a pile of papers and an opened capsule's lid. Returns its box."""
    d = Canvas()
    d.shape(rounded_rect_d(-56, -62, 112, 8, 2), P.METAL_LIGHT, sw=1.6, light=None)
    for px in (-50, 26):
        d.shape(rounded_rect_d(px, -54, 24, 54, 2), P.METAL, sw=1.4, light=None)
        d.line(f"M{px},-36 h24 M{px},-18 h24", 1.2, INK, 0.6)
        d.line(f"M{px + 9},-45 h6 M{px + 9},-27 h6 M{px + 9},-9 h6", 2, P.METAL_DARK)
    d.shape("M-40,-62 L-36,-66 H-14 L-12,-62 Z", P.WHITE, sw=1, light=None)                   # papers
    d.shape("M-38,-66 L-34,-70 H-16 L-14,-66 Z", P.CARD, sw=1, light=None)
    d.line("M34,-62 L30,-88 L44,-96", 2.4, P.METAL_DARK)                                        # the lamp
    d.shape("M38,-100 L54,-92 L48,-84 Z", INDIGO, sw=1.2, light=None)
    d.add(f'<path d="M48,-86 L60,-62 H30 Z" fill="{WARM}" fill-opacity=".35"/>')
    if opened:
        d.shape(rounded_rect_d(0, -66, 22, 4, 2), P.METAL, sw=1, light=None)
    c.add(_at(d, x, foot, k))
    return {"box": (x - 57 * k, foot - 100 * k, x + 57 * k, foot)}


def wall_screen(c: Canvas, x: float, foot: float, k: float, zoomed: bool, cabinet: bool = True) -> dict:
    """The briefing room's big screen on the wall over its low cabinet at (x, foot), 150 wide and 164 tall: the wide
    display in its bezel on a wall mount, showing a module of the base in section - its hull, the rooms, the pipes
    and the air flowing round - or (`zoomed`) its air pump close up, the fan and the flow through it. Returns its
    box."""
    d = Canvas()
    d.shape(rounded_rect_d(-20, -164, 40, 6, 2), P.METAL_DARK, sw=1, light=None)              # its wall mount
    if cabinet:
        d.shape(rounded_rect_d(-60, -22, 120, 22, 3), WALL, sw=1.6, light=(-1, -1))             # the cabinet
        d.line("M-20,-22 V0 M20,-22 V0", 1.2, darken(WALL, 0.7))
        d.add("".join(f'<circle cx="{cx}" cy="-11" r="1.6" fill="{P.METAL_LIGHT}"/>' for cx in (-40, 0, 40)))
    d.shape(rounded_rect_d(-75, -160, 150, 92, 6), P.CHARCOAL, sw=2, light=None)
    d.shape(rounded_rect_d(-67, -152, 134, 76, 3), P.SCREEN, sw=1, light=None)
    if not zoomed:
        d.add(f'<path d="M-50,-104 V-124 Q-50,-134 -40,-134 H40 Q50,-134 50,-124 V-104 Q50,-94 40,-94 H-40 '
              f'Q-50,-94 -50,-104 Z" fill="none" stroke="{P.SCREEN_LIGHT}" stroke-width="2.4"/>')
        d.line("M-16,-134 V-94 M16,-134 V-94", 1.6, P.SCREEN_LIGHT)
        d.add(f'<rect x="-8" y="-120" width="16" height="12" fill="none" stroke="{P.YELLOW}" stroke-width="2"/>')
        d.line("M-40,-114 H-12 M12,-114 H40", 1.4, P.SCREEN_LIGHT, 0.8)
        d.line("M-36,-100 Q0,-88 36,-100", 1.8, P.GREEN)
        d.add(f'<path d="M36,-100 l-7,-4 l1,7 Z" fill="{P.GREEN}"/>')
    else:
        d.add(f'<circle cx="0" cy="-114" r="26" fill="none" stroke="{P.YELLOW}" stroke-width="2.4"/>')
        for ang in range(0, 360, 60):
            a = math.radians(ang)
            d.add(f'<path d="M0,-114 Q{n(math.cos(a + 0.6) * 14)},{n(-114 + math.sin(a + 0.6) * 14)} '
                  f'{n(math.cos(a) * 22)},{n(-114 + math.sin(a) * 22)}" fill="none" stroke="{P.SCREEN_LIGHT}" '
                  f'stroke-width="3"/>')
        d.line("M-60,-114 H-30 M30,-114 H60", 1.8, P.GREEN)
        d.add(f'<path d="M60,-114 l-7,-4 v8 Z" fill="{P.GREEN}"/>')
    d.add(f'<path d="M-60,-150 L-40,-150 L-58,-120 Z" fill="{P.WHITE}" fill-opacity=".12"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 76 * k, foot - 165 * k, x + 76 * k, foot if cabinet else foot - 67 * k)}


def rover(c: Canvas, x: float, foot: float, k: float, lamp: str = P.GREEN, way: int = 1, dust: bool = False,
          arm: bool = True) -> dict:
    """The inspection rover at (x, foot), 170 long and 130 tall, its nose towards `way`, built like the rovers on
    the Moon and Mars: six wheels of wire mesh with treads and hubs on a rocker-bogie suspension, the white chassis
    with its indigo side panels and the solar deck on top, a dish aerial and a whip aerial of its own - no line to
    anything - the camera mast with its head (two lenses in one housing, a light under them), and the robotic arm
    folded out in front, its scanner head at the end of it; its status light (`lamp`); `dust`: kicked up behind the
    wheels. Returns its box and where the scanner head's window is."""
    d = Canvas()
    if dust:
        for q in range(5):
            d.add(f'<ellipse cx="{-96 - q * 15}" cy="{-8 - q * 3}" rx="{8 + q * 3}" ry="{5 + q * 2}" '
                  f'fill="{mix(REGOLITH, P.WHITE, 0.3)}" fill-opacity="{0.85 - q * 0.14}" stroke="{INK}" '
                  f'stroke-width=".7" stroke-opacity=".3"/>')
    d.line("M-66,-15 L-34,-40 H-6 L30,-32 L66,-15 M30,-32 L0,-15 M-34,-40 V-46 M-6,-40 V-46", 3.4,
           P.METAL_DARK)                                                                         # rocker-bogie
    for wx in (-66, 0, 66):
        d.add(f'<circle cx="{wx}" cy="-15" r="15" fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="1.6"/>')
        d.add(f'<circle cx="{wx}" cy="-15" r="11" fill="none" stroke="{P.METAL}" stroke-width="1"/>')
        d.line(" ".join(f"M{n(wx + math.cos(math.radians(a)) * 11)},{n(-15 + math.sin(math.radians(a)) * 11)} "
                        f"L{n(wx + math.cos(math.radians(a)) * 15)},{n(-15 + math.sin(math.radians(a)) * 15)}"
                        for a in range(0, 360, 30)), 2, P.METAL_DARK)                          # treads
        d.add(f'<circle cx="{wx}" cy="-15" r="4.6" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1"/>')
    d.shape("M-74,-74 L74,-74 L80,-58 L76,-44 H-72 L-80,-58 Z", P.WHITE, sw=2, light=(-1, -1))  # the chassis
    d.add(f'<rect x="-66" y="-66" width="40" height="16" rx="2" fill="{INDIGO}" stroke="{INK}" stroke-width="1"/>'
          f'<rect x="-20" y="-66" width="40" height="16" rx="2" fill="{INDIGO}" stroke="{INK}" stroke-width="1"/>')
    d.line("M-62,-58 h32 M-16,-58 h32", 1, lighten(INDIGO, 0.3))
    d.add(f'<circle cx="36" cy="-58" r="3" fill="{lamp}" stroke="{INK}" stroke-width=".8"/>')
    d.shape("M-78,-82 L60,-82 L66,-74 H-74 Z", P.SCREEN, sw=1.4, light=None)                    # the solar deck
    d.line(" ".join(f"M{q},-82 l3,8" for q in range(-64, 60, 14)), 0.8, P.SCREEN_LIGHT)
    d.line("M-60,-82 V-108 M-66,-120 Q-60,-106 -46,-118", 1.6, P.METAL_DARK)                    # the dish
    d.add(f'<path d="M-72,-118 Q-60,-100 -42,-122 Z" fill="{P.WHITE}" stroke="{INK}" stroke-width="1.2"/>')
    d.line("M-30,-82 V-128", 1.2, P.METAL_DARK)                                                # the whip aerial
    d.add(f'<circle cx="-30" cy="-129" r="1.6" fill="{P.RED}"/>')
    d.line("M20,-82 V-112", 4, P.METAL_DARK)                                                   # the camera mast
    d.shape(rounded_rect_d(8, -128, 30, 16, 3), P.METAL_LIGHT, sw=1.6, light=None)              # its head
    d.shape(rounded_rect_d(26, -125, 14, 10, 2), P.CHARCOAL, sw=1, light=None)
    for lx in (30, 36):
        d.add(f'<circle cx="{lx}" cy="-120" r="2.2" fill="{P.LENS}" stroke="{INK}" stroke-width=".6"/>')
    d.add(f'<rect x="12" y="-110" width="8" height="3" rx="1" fill="{WARM}"/>')
    hx, hy = 70, -60
    if arm:                                                                                    # the robotic arm
        d.line("M74,-62 L96,-86 L118,-60", 5, P.METAL_DARK)
        d.line("M74,-62 L96,-86 L118,-60", 2, P.METAL_LIGHT)
        for jx, jy in ((74, -62), (96, -86)):
            d.add(f'<circle cx="{jx}" cy="{jy}" r="4" fill="{P.METAL}" stroke="{INK}" stroke-width="1"/>')
        d.shape("M114,-66 L128,-62 L128,-50 L114,-50 Z", P.METAL_LIGHT, sw=1.4, light=None)    # scanner head
        d.shape(rounded_rect_d(126, -60, 4, 8, 1), P.SUN, sw=0.6, light=None)
        hx, hy = 130, -56
    c.add(_at(d, x, foot, k, mirror=way < 0))
    xs = sorted((x - (170 if dust else 84) * k * way, x + (132 if arm else 82) * k * way))
    return {"box": (xs[0], foot - 131 * k, xs[1], foot + 1), "scanner": (x + hx * k * way, foot + hy * k)}


def scan(c: Canvas, head: tuple[float, float], target: tuple[float, float, float]) -> None:
    """The scanner's light from its head to the capsule: a fan of three nested bands, softer outward, ending on
    the capsule's side between y0 and y1 at x, where it lights a band across the drum."""
    hx, hy = head
    tx, y0, y1 = target
    mid = (y0 + y1) / 2
    for q, (op, spread) in enumerate(((0.12, 1.0), (0.16, 0.7), (0.22, 0.4))):
        a0, a1 = mid - (mid - y0) * spread, mid + (y1 - mid) * spread
        c.add(f'<path d="M{n(hx)},{n(hy - 2 + q)} L{n(tx)},{n(a0)} L{n(tx)},{n(a1)} L{n(hx)},{n(hy + 2 - q)} Z" '
              f'fill="{P.SUN}" fill-opacity="{op}"/>')
    c.add(f'<rect x="{n(tx - 3)}" y="{n(y0)}" width="6" height="{n(y1 - y0)}" rx="3" fill="{P.SUN}" '
          f'fill-opacity=".55"/>')


def cart(c: Canvas, x: float, foot: float, k: float) -> dict:
    """A platform cart at (x, foot), 80 wide and 56 tall: the deck plate with its rubber edge, four swivel castors
    in their forks, the tubular push handle at the back with its grip. Returns its box and the deck's top."""
    bed = foot - 14 * k
    c.add(f'<rect x="{n(x - 40 * k)}" y="{n(bed)}" width="{n(80 * k)}" height="{n(5 * k)}" rx="{n(1.5 * k)}" '
          f'fill="{P.METAL}" stroke="{INK}" stroke-width="1.2"/>'
          f'<rect x="{n(x - 40 * k)}" y="{n(bed + 5 * k)}" width="{n(80 * k)}" height="{n(2 * k)}" fill="{INK}"/>')
    for wx in (-32, -12, 12, 32):
        c.add(f'<path d="M{n(x + wx * k - 3 * k)},{n(bed + 7 * k)} h{n(6 * k)} l{n(-1 * k)},{n(3 * k)} '
              f'h{n(-4 * k)} Z" fill="{P.METAL_DARK}"/><circle cx="{n(x + wx * k)}" cy="{n(foot - 3.4 * k)}" '
              f'r="{n(3.4 * k)}" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width=".8"/>')
    c.line(f"M{n(x - 38 * k)},{n(bed)} V{n(foot - 56 * k)} H{n(x - 30 * k)} M{n(x - 38 * k)},{n(bed - 18 * k)} "
           f"h{n(6 * k)}", 2.6 * k, P.METAL_DARK)
    c.add(f'<rect x="{n(x - 41 * k)}" y="{n(foot - 60 * k)}" width="{n(12 * k)}" height="{n(5 * k)}" '
          f'rx="{n(2 * k)}" fill="{P.CHARCOAL}"/>')
    return {"box": (x - 42 * k, foot - 61 * k, x + 41 * k, foot), "bed": bed}


def console(c: Canvas, x: float, foot: float, k: float, report: bool) -> dict:
    """The control room's console standing against the wall at (x, foot), 160 wide and 120 tall: its cabinet, the
    sloped desk at waist height with switches and a dial, two screens on top - a rover checking a capsule and the
    list of its findings - and in the middle of the desk the two big buttons, green and red, each under its own
    guard, with their plates. Returns its box and where the plates are."""
    d = Canvas()
    d.shape("M-80,0 V-52 L-70,-70 H70 L80,-52 V0 Z", WALL, sw=2, light=(-2, -2))
    d.shape("M-80,-52 L-70,-70 H70 L80,-52 Z", lighten(WALL, 0.15), sw=1.4, light=None)
    d.line("M-74,-30 H74 M-40,-46 V0 M40,-46 V0", 1, darken(WALL, 0.75))
    for q in range(5):
        d.add(f'<circle cx="{-62 + q * 9}" cy="-60" r="2.4" fill="{P.METAL_LIGHT}" stroke="{INK}" '
              f'stroke-width=".7"/>')
    d.add(f'<circle cx="58" cy="-61" r="5" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="1"/>')
    for sx_ in (-62, 2):
        d.shape(rounded_rect_d(sx_, -118, 60, 44, 3), P.CHARCOAL, sw=1.6, light=None)
        d.shape(rounded_rect_d(sx_ + 4, -114, 52, 36, 2), P.SCREEN, sw=0.8, light=None)
    d.line("M-34,-110 L-26,-104 M-50,-90 h14 l4,-6 h6 l4,6 h8", 1.6, P.SCREEN_LIGHT)
    d.add("".join(f'<circle cx="{wx}" cy="-88" r="2.4" fill="none" stroke="{P.SCREEN_LIGHT}" stroke-width="1.2"/>'
                  for wx in (-48, -38, -28)))
    d.add(f'<rect x="-20" y="-102" width="10" height="14" rx="2" fill="none" stroke="{P.YELLOW}" '
          f'stroke-width="1.4"/>')
    for q in range(4):
        d.line(f"M10,{-108 + q * 8} h{30 - q * 4}", 2, P.SCREEN_LIGHT if q != 2 or not report else P.ORANGE)
        d.add(f'<circle cx="48" cy="{-108 + q * 8}" r="2" fill="{P.GREEN if q != 2 else P.ORANGE}"/>')
    for bx, col in ((-24, P.GREEN), (24, P.RED)):
        d.shape(rounded_rect_d(bx - 18, -26, 36, 20, 3), P.METAL_LIGHT, sw=1.4, light=None)     # the plates
        d.add(f'<ellipse cx="{bx}" cy="-56" rx="11" ry="5" fill="{darken(col, 0.7)}" stroke="{INK}" '
              f'stroke-width="1.2"/><ellipse cx="{bx}" cy="-59" rx="9" ry="4" fill="{col}" stroke="{INK}" '
              f'stroke-width="1.2"/>')
        d.add(f'<path d="M{bx - 13},-56 Q{bx},-74 {bx + 13},-56" fill="none" stroke="{P.METAL_DARK}" '
              f'stroke-width="1.6"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 81 * k, foot - 119 * k, x + 81 * k, foot),
            "plates": ((x - 24 * k, foot - 16 * k, 34 * k), (x + 24 * k, foot - 16 * k, 34 * k))}


def arch(c: Canvas, x: float, foot: float, k: float, kind: int, ok: bool | None, screen: bool = False) -> dict:
    """A scanning arch over the conveyor at (x, foot), 76 wide and 143 tall, each a different instrument: 0 the
    X-ray tunnel with its lead-strip curtain, 1 the laser gate with its red beams, 2 the camera ring with four
    lenses; on its crown a status lamp - green (passed), red (stopped) or dark; `screen`: a small screen on its
    post showing the scan, a red stripe across it when it stops. Returns its box."""
    d = Canvas()
    d.shape("M-38,0 V-130 Q-38,-138 -30,-138 H30 Q38,-138 38,-130 V0 H26 V-112 H-26 V0 Z", INDIGO, sw=1.8,
            light=(-1, -1))
    d.line("M-32,-128 H32", 1, lighten(INDIGO, 0.3))
    if kind == 0:
        d.line(" ".join(f"M{q},-112 V-52" for q in range(-22, 26, 6)), 4, mix(P.METAL_DARK, P.CHARCOAL, 0.5))
    elif kind == 1:
        d.line(" ".join(f"M-26,{-100 + q * 14} H26" for q in range(5)), 1.6, P.RED, 0.9)
    else:
        for ly in (-104, -70):
            for lx in (-20, 20):
                d.add(f'<circle cx="{lx}" cy="{ly}" r="5" fill="{P.LENS}" stroke="{INK}" stroke-width="1.2"/>')
    lamp = P.CHARCOAL if ok is None else P.GREEN if ok else P.RED
    d.shape(rounded_rect_d(-14, -150, 28, 12, 3), P.CHARCOAL, sw=1.2, light=None)
    d.add(f'<rect x="-10" y="-147" width="20" height="6" rx="2" fill="{lamp}"/>')
    if ok is not None:
        d.add(f'<rect x="-16" y="-152" width="32" height="16" rx="5" fill="{lamp}" fill-opacity=".25"/>')
    if screen:
        d.shape(rounded_rect_d(40, -96, 28, 22, 2), P.CHARCOAL, sw=1.2, light=None)
        d.shape(rounded_rect_d(43, -93, 22, 16, 1), P.SCREEN, sw=0.6, light=None)
        d.add(f'<rect x="44" y="-87" width="20" height="4" fill="{P.RED if ok is False else P.GREEN}"/>')
        d.line("M38,-84 H40", 2, P.METAL_DARK)
    c.add(_at(d, x, foot, k))
    return {"box": (x - 39 * k, foot - 153 * k, x + (69 if screen else 39) * k, foot)}


def conveyor(c: Canvas, x0: float, x1: float, foot: float, k: float, gap: tuple[float, float] | None = None) -> float:
    """A conveyor on the deck from x0 to x1, 36 high: the belt over its rollers on legs with cross braces, the drive
    motor at the far end; `gap`: where the belt is open over the diverter's flap. Returns the belt's top."""
    top = foot - 36 * k
    for lx in range(int(x0 + 12 * k), int(x1 - 6 * k), int(60 * k) or 1):
        c.add(f'<rect x="{n(lx)}" y="{n(top + 8 * k)}" width="{n(5 * k)}" height="{n(28 * k)}" '
              f'fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1"/>')
    segs = [(x0, x1)] if not gap else [(x0, gap[0]), (gap[1], x1)]
    for a, b in segs:
        c.add(f'<rect x="{n(a)}" y="{n(top)}" width="{n(b - a)}" height="{n(9 * k)}" rx="{n(4.5 * k)}" '
              f'fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="1.4"/>')
        c.add("".join(f'<circle cx="{n(rx)}" cy="{n(top + 4.5 * k)}" r="{n(3 * k)}" fill="{P.METAL}"/>'
                      for rx in range(int(a + 8 * k), int(b - 4 * k), int(16 * k) or 1)))
    c.add(f'<rect x="{n(x1 - 18 * k)}" y="{n(top + 10 * k)}" width="{n(18 * k)}" height="{n(14 * k)}" rx="2" '
          f'fill="{INDIGO}" stroke="{INK}" stroke-width="1"/>')
    return top


def reject(c: Canvas, x: float, foot: float, k: float, top: float, open_: bool) -> dict:
    """The reject line under the conveyor's open gap at x: the diverter's flap hinged at the gap's start, closed
    flush with the belt or dropped open; under it the chute sloping down and away to the reject bin on the deck - a
    deep steel bin with red-and-white hazard bands round its rim and a plate for its word. Returns where things are:
    the chute's top and foot, the bin's box and its plate."""
    w = 40 * k
    if open_:
        c.line(f"M{n(x)},{n(top + 4 * k)} L{n(x + 30 * k)},{n(top + 22 * k)}", 4 * k, P.METAL_LIGHT)
    else:
        c.line(f"M{n(x)},{n(top + 4 * k)} H{n(x + w)}", 4 * k, P.METAL_LIGHT)
    c.add(f'<circle cx="{n(x)}" cy="{n(top + 4 * k)}" r="{n(3 * k)}" fill="{P.METAL_DARK}" stroke="{INK}" '
          f'stroke-width="1"/>')
    ch0 = (x + 6 * k, top + 12 * k)
    ch1 = (x + 96 * k, foot - 40 * k)
    c.add(f'<path d="M{n(ch0[0])},{n(ch0[1])} L{n(ch1[0])},{n(ch1[1])} L{n(ch1[0])},{n(ch1[1] + 7 * k)} '
          f'L{n(ch0[0])},{n(ch0[1] + 7 * k)} Z" fill="{P.METAL}" stroke="{INK}" stroke-width="1.3"/>')
    c.line(f"M{n(ch0[0])},{n(ch0[1] - 6 * k)} L{n(ch1[0])},{n(ch1[1] - 6 * k)}", 1.6 * k, P.METAL_DARK)
    c.add(f'<rect x="{n(x + 60 * k)}" y="{n(ch1[1] + 7 * k)}" width="{n(4 * k)}" height="{n(foot - ch1[1] - 7 * k)}" '
          f'fill="{P.METAL_DARK}"/>')
    bx0, bx1 = x + 84 * k, x + 150 * k
    btop = foot - 44 * k
    c.add(f'<path d="M{n(bx0)},{n(btop)} H{n(bx1)} L{n(bx1 - 4 * k)},{n(foot)} H{n(bx0 + 4 * k)} Z" '
          f'fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1.6"/>')
    c.add(f'<rect x="{n(bx0)}" y="{n(btop)}" width="{n(bx1 - bx0)}" height="{n(6 * k)}" fill="{P.WHITE}" '
          f'stroke="{INK}" stroke-width="1"/>')
    c.line(" ".join(f"M{n(bx0 + q * 10 * k)},{n(btop + 6 * k)} l{n(6 * k)},{n(-6 * k)}"
                    for q in range(int((bx1 - bx0) / (10 * k)))), 3 * k, P.RED)
    c.add(f'<rect x="{n(bx0 + 10 * k)}" y="{n(btop + 14 * k)}" width="{n(bx1 - bx0 - 20 * k)}" '
          f'height="{n(16 * k)}" rx="2" fill="{P.CARD}" stroke="{INK}" stroke-width="1"/>')
    return {"chute": (ch0, ch1), "bin": (bx0, btop, bx1, foot),
            "plate": ((bx0 + bx1) / 2, btop + 22 * k, bx1 - bx0 - 26 * k)}


def status_board(c: Canvas, x: float, cy: float, k: float, lamps: tuple) -> dict:
    """The inspection hall's status board on the wall, its middle at (x, cy), 150 wide and 50 tall: one window for
    each scanner along the line - the X-ray's lead strips, the laser's red beams, the camera's lenses - and under
    each its lamp, green, red or dark. Returns its box."""
    d = Canvas()
    d.shape(rounded_rect_d(-75, -25, 150, 50, 4), P.CHARCOAL, sw=1.8, light=None)
    for q, ok in enumerate(lamps):
        wx = -66 + q * 46
        d.shape(rounded_rect_d(wx, -19, 40, 26, 2), P.SCREEN, sw=1, light=None)
        if q == 0:
            d.line(" ".join(f"M{wx + 6 + v * 5},-15 V3" for v in range(6)), 2, P.SCREEN_LIGHT)
        elif q == 1:
            d.line(" ".join(f"M{wx + 4},{-14 + v * 6} H{wx + 36}" for v in range(4)), 1.4, P.RED)
        else:
            d.add("".join(f'<circle cx="{wx + cx}" cy="{cy_}" r="4" fill="{P.LENS}" stroke="{P.SCREEN_LIGHT}" '
                          f'stroke-width="1"/>' for cx in (12, 28) for cy_ in (-10, 2)))
        lamp = P.CHARCOAL if ok is None else P.GREEN if ok else P.RED
        d.add(f'<rect x="{wx + 12}" y="11" width="16" height="7" rx="2" fill="{lamp}" stroke="{INK}" '
              f'stroke-width=".8"/>')
    d.line("M-40,-25 V-34 M40,-25 V-34", 2, P.METAL_DARK)                                       # its hangers
    c.add(_at(d, x, cy, k))
    return {"box": (x - 76 * k, cy - 35 * k, x + 76 * k, cy + 26 * k)}


def garden_bench(c: Canvas, x: float, foot: float, k: float) -> dict:
    """A hydroponic bench in the greenhouse at (x, foot), 130 wide and 96 tall: a steel table at waist height with
    its trough of lettuce and tomatoes on top, the grow-light bar over it on two posts with its purple glow, a tank
    of nutrient water on the shelf under it. Returns its box."""
    d = Canvas()
    d.line("M-60,0 V-40 M60,0 V-40 M-56,0 V-40 M56,0 V-40", 3, P.METAL_DARK)
    d.shape(rounded_rect_d(-64, -44, 128, 6, 2), P.METAL_LIGHT, sw=1.4, light=None)
    d.shape(rounded_rect_d(-58, -14, 116, 4, 1), P.METAL, sw=1, light=None)                   # the shelf
    d.shape(rounded_rect_d(-40, -30, 30, 16, 3), P.LENS, sw=1.2, light=None)                   # the tank
    d.add(f'<rect x="-38" y="-24" width="26" height="9" fill="{P.TEAL}" fill-opacity=".5"/>')
    trough(d, -60, 60, -44, "lettuce")
    d.line("M-62,-44 V-96 M62,-44 V-96", 2, P.METAL_DARK)
    d.add(f'<rect x="-64" y="-98" width="128" height="5" rx="2" fill="{mix(P.VIOLET, P.PINK, 0.4)}" '
          f'stroke="{INK}" stroke-width="1"/><rect x="-60" y="-93" width="120" height="22" '
          f'fill="{mix(P.VIOLET, P.PINK, 0.4)}" fill-opacity=".16"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 65 * k, foot - 99 * k, x + 65 * k, foot)}


def wall_monitor(c: Canvas, x: float, cy: float, k: float, alarm_: bool) -> dict:
    """A monitor on the wall over the line, its middle at (x, cy), 60 wide and 40 tall: the last scan of a capsule,
    a red stripe across it when the scan found a fault, a green one when it passed. Returns its box."""
    d = Canvas()
    d.line("M0,-20 V-28", 2.4, P.METAL_DARK)
    d.shape(rounded_rect_d(-30, -20, 60, 40, 3), P.CHARCOAL, sw=1.6, light=None)
    d.shape(rounded_rect_d(-25, -15, 50, 30, 2), P.SCREEN, sw=0.8, light=None)
    d.add(f'<rect x="-9" y="-12" width="18" height="20" rx="3" fill="none" stroke="{P.SCREEN_LIGHT}" '
          f'stroke-width="1.6"/><rect x="-25" y="9" width="50" height="5" fill="{P.RED if alarm_ else P.GREEN}"/>')
    if alarm_:
        d.line("M-5,-6 l3,4 l3,-3 l3,4", 1.4, P.RED)
    c.add(_at(d, x, cy, k))
    return {"box": (x - 31 * k, cy - 29 * k, x + 31 * k, cy + 21 * k)}


def greenhouse_rack(c: Canvas, x: float, foot: float, k: float, ribs: bool = True) -> dict:
    """The greenhouse's growing rack at (x, foot), 140 wide and 130 tall: three hydroponic troughs on steel posts,
    water in each, lettuce heads, herbs and tomato plants with their red fruit growing out of their lids, a grow
    light bar over each shelf with its purple glow, the glass ribs of the dome arching over it (`ribs`; without them
    it stands against a wall). Returns its box."""
    d = Canvas()
    if ribs:
        d.line("M-90,0 Q-80,-150 0,-160 Q80,-150 90,0", 2.6, mix(P.LENS, P.WHITE, 0.3))
        d.line("M-90,0 Q-80,-150 0,-160 Q80,-150 90,0", 1, INK, 0.5)
    for px in (-66, 66):
        d.line(f"M{px},0 V-130", 3, P.METAL_DARK)
    for q, sy in enumerate((-8, -50, -92)):
        trough(d, -64, 64, sy, ("lettuce", "tomato", "herbs")[q])
        d.add(f'<rect x="-60" y="{sy - 38}" width="120" height="4" rx="2" fill="{mix(P.VIOLET, P.PINK, 0.4)}" '
              f'stroke="{INK}" stroke-width=".8"/><rect x="-60" y="{sy - 34}" width="120" height="10" '
              f'fill="{mix(P.VIOLET, P.PINK, 0.4)}" fill-opacity=".18"/>')
    c.add(_at(d, x, foot, k))
    if not ribs:
        return {"box": (x - 67 * k, foot - 131 * k, x + 67 * k, foot)}
    return {"box": (x - 91 * k, foot - 161 * k, x + 91 * k, foot)}


def trough(d: Canvas, x0: float, x1: float, y: float, crop: str) -> None:
    """A hydroponic trough from x0 to x1, its floor at y, 10 deep: the white channel, the water in it seen at its
    end, the plants growing out of their holes in its lid - "lettuce" (round heads of leaves), "tomato" (stems,
    leaves and red fruit) or "herbs" (thin stems with small leaves)."""
    d.shape(rounded_rect_d(x0, y - 10, x1 - x0, 10, 2), P.WHITE, sw=1.2, light=None)
    d.add(f'<rect x="{n(x0 + 2)}" y="{n(y - 5)}" width="6" height="4" fill="{P.LENS}"/>')
    step = 18 if crop != "herbs" else 13
    rnd = random.Random(len(crop))
    px = x0 + 10
    while px < x1 - 8:
        if crop == "lettuce":
            d.add(f'<path d="M{n(px - 8)},{n(y - 10)} Q{n(px - 10)},{n(y - 20)} {n(px - 3)},{n(y - 22)} '
                  f'Q{n(px)},{n(y - 28)} {n(px + 4)},{n(y - 22)} Q{n(px + 10)},{n(y - 20)} {n(px + 8)},{n(y - 10)} Z" '
                  f'fill="{lighten(P.GREEN, 0.15)}" stroke="{INK}" stroke-width=".9"/>')
            d.line(f"M{n(px)},{n(y - 11)} V{n(y - 21)} M{n(px - 4)},{n(y - 12)} L{n(px - 2)},{n(y - 19)}", 0.8,
                   P.LEAF_DARK)
        elif crop == "tomato":
            d.line(f"M{n(px)},{n(y - 10)} Q{n(px - 3)},{n(y - 22)} {n(px + 1)},{n(y - 32)}", 1.4, P.LEAF_DARK)
            for lx, ly in ((-5, -18), (4, -24), (-3, -29)):
                d.add(f'<path d="M{n(px)},{n(y + ly)} q{n(lx)},-3 {n(lx * 1.6)},2 q{n(-lx)},2 {n(-lx * 1.6)},-2 Z" '
                      f'fill="{P.GREEN}" stroke="{INK}" stroke-width=".6"/>')
            for fx_, fy_ in ((3, -15), (-3, -21)) if rnd.random() < 0.8 else ((2, -16),):
                d.add(f'<circle cx="{n(px + fx_)}" cy="{n(y + fy_)}" r="2.8" fill="{P.RED}" stroke="{INK}" '
                      f'stroke-width=".6"/>')
        else:
            d.line(f"M{n(px)},{n(y - 10)} V{n(y - 24)} M{n(px)},{n(y - 16)} l-4,-4 M{n(px)},{n(y - 20)} l4,-4", 1,
                   P.LEAF_DARK)
            for ly in (-24, -19, -15):
                d.add(f'<ellipse cx="{n(px + (2 if ly % 2 else -2))}" cy="{n(y + ly)}" rx="2.4" ry="1.4" '
                      f'fill="{P.GREEN}"/>')
        px += step


# ============================================================================ what the cast holds
def stamp(x: float, y: float, k: float) -> str:
    """A rubber stamp: its wooden knob in the fist, the indigo pad block under it."""
    c = Canvas()
    c.shape(rounded_rect_d(-2, -6, 4, 9, 2), P.WOOD, sw=0.5, light=None)
    c.shape(rounded_rect_d(-5, 3, 10, 4, 1), INDIGO, sw=0.5, light=None)
    c.shape(rounded_rect_d(-5.5, 7, 11, 2, 0.5), P.RED, sw=0.4, light=None)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def watering_can(x: float, y: float, k: float) -> str:
    """A watering can held by its top handle: the indigo body hanging below the fist, the long spout with its
    rose."""
    c = Canvas()
    c.line("M-5,0 Q0,-4 5,0", 1.4, P.METAL_DARK)
    c.shape(rounded_rect_d(-8, 0, 16, 13, 3), INDIGO, sw=0.7, light=None)
    c.line("M8,9 L19,1", 1.6, INDIGO)
    c.shape("M18,-1 L22,-2 L22,4 L19,3 Z", P.METAL, sw=0.4, light=None)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def space_mug(x: float, y: float, k: float) -> str:
    """The cat's sealed space mug: a white cup with a screwed lid and a bent straw, held in the fist."""
    c = Canvas()
    c.shape(rounded_rect_d(-3.6, -6, 7.2, 11, 2), P.WHITE, sw=0.6, light=None)
    c.shape(rounded_rect_d(-4, -8, 8, 2.4, 1), INDIGO, sw=0.5, light=None)
    c.line("M1,-8 V-12 L4,-14", 0.9, P.RED)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def name_plate(s: Strip, x: float, y: float, w: float, text: str) -> None:
    """A keeper's name plate over a hatch, its middle at (x, y), `w` wide: a card plate with its two screws and the
    name lettered inside its padding (a container: the lettering never touches its edge)."""
    h = w * 0.2
    pen = Pen(s, x - w / 2, y - h / 2, 1)
    plate = pen.container("plate", 0, 0, w, h, P.CARD, radius=3, sw=1.3, light=None)
    pad = pen.pad(w, h)
    size = max(sets.LETTERING_MIN, min(14.0, (h - 2 * pad) * 0.8))
    pen.c.add(lettering(w / 2, h / 2 + size * 0.35, text, size, INK, room=w - 2 * pad - 8, style="label"))
    pen.child(plate, "name", pad + 4, pad, w - pad - 4, h - pad)
    s.put(lane(s).feet - 0.5, pen.svg(), None)


def words(s: Strip, x: float, y: float, text: str, room: float, color: str = INK) -> None:
    """Lettering on a thing in page space (never mirrored with the station): at least the smallest size allowed,
    within `room`."""
    size = max(sets.LETTERING_MIN, min(14.0, room / max(1, len(text)) * 1.7))
    s.put(lane(s).feet - 0.5, lettering(x, y, text, size, color, room=room, style="label"), None)


# ============================================================================ framing a station
def _framed(draw):
    """A station drawn as it is or mirrored, by turns; on the next visit of the same moment the onlooker changes,
    the station swaps sides and the camera comes a step nearer. After it: the sparrow on its perch if the station
    offers one (every other page), and the portholes wherever the wall shows free."""
    def run(s: Strip, beat: str) -> None:
        s.again = (s.seed // 2) % 2 == 1
        s.mirror = bool(s.shot) != s.again
        s.near = 1.12 if s.again else 1.0
        s.perch = None
        draw(s, beat)
        if s.perch and s.seed % 2 == 0 and not any(b.name == "sparrow" for b in s.boxes):
            x, top, group = s.perch
            sparrow_on(s, x, top, group)
        portholes(s)
    return run


def checklist(lines: int):
    """The caterpillar's checklist, longer chapter by chapter: a clipboard whose sheet grows with `lines` ruled
    lines, a tick by each but the last."""
    def make(x: float, y: float, k: float) -> str:
        h = 10 + lines * 3
        c = Canvas()
        c.shape(rounded_rect_d(-1.5, -h - 2.5, 17, h + 5, 1.2), P.WOOD, sw=0.7, light=None)
        c.shape(rounded_rect_d(0.2, -h, 13.6, h + 1, 0.4), P.WHITE, sw=0.4, light=None)
        c.shape(rounded_rect_d(3.6, -h - 3.8, 6.8, 3.4, 0.9), P.METAL_LIGHT, sw=0.5, light=None)
        for q in range(lines):
            ly = -h + 4 + q * 3
            c.line(f"M4.2,{n(ly)} H12", 0.4, INK, 0.55)
            if q < lines - 1:
                c.line(f"M1.2,{n(ly - 0.4)} l0.7,0.8 l1.2,-1.6", 0.45, P.GREEN)
        return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'
    return make


def cast(s: Strip, box: tuple, who: tuple[tuple, ...]) -> None:
    """The station's cast beside its box, each facing it, in the pose asked for if it has one, else presenting -
    every one at its true size against the others and the things (in a strip too: none is stretched to the
    strip's height), at the first spot along the deck where it stands whole and free."""
    feet = lane(s).feet
    used: list[str] = []
    for name, side, pose, mood, hold in who:
        if (name == "professor" and low(s)) or name in used:          # no professor in a close-up, no twins
            pool = [x for x in ("caterpillar", "cat", "agent") if x not in used]
            fresh = [x for x in pool if x not in (w[0] for w in who)]
            name = (fresh or pool)[0]
        used.append(name)
        side = -side if getattr(s, "mirror", False) else side         # the station is mirrored: so is its cast
        pose = pose if pose in characters.module(name).POSES else "present"
        first = beside(s, box, side, name)
        sweep = sorted((i / 40 for i in range(41)), key=lambda f: abs(f - first[0]))
        for f in (*first, *sweep):
            x = s.x(f)
            b = _box(s, name, x, feet)
            if b[0] >= 2 and b[2] <= W - 2 and b[1] >= 2 and s.free(b, 3):
                actor = s.actor(name, x, feet, pose, mood, flip=side > 0, tall=s.tall * SIZE[name], group=name)
                if hold is not None:
                    held(s, actor, hold)
                break


def window_over(s: Strip, box: tuple, things=None, earth_: bool = True, high: float = 0.58) -> tuple | None:
    """A big window in the wall over a thing standing against it (`box`, page space): as wide as the thing and a
    little more, from under the ceiling down to a little above the thing's top. None if the wall has no room."""
    x0, top = box[0] - 10, s.ceil + 8
    x1, bottom = box[2] + 10, box[1] + (box[3] - box[1]) * 0.4        # its sill hidden behind the thing
    if bottom - top < 36:
        return None
    win = (x0, top, x1, bottom)
    window(s, win, seed=getattr(s, "index", 0) * 7, things=things, earth_=earth_, high=high)
    return win


def perch(s: Strip, x: float, top: float, group: str) -> None:
    """Offer the sparrow a perch on a station thing: at x (page space), its top at `top`."""
    s.perch = (x, top, group)


def mates(s: Strip) -> int:
    """How long the caterpillar's checklist is by now: longer section by section."""
    return 2 + getattr(s, "index", 0)


# ============================================================================ true scale
def pr_(s: Strip) -> float:
    """The measure of a person in this frame: the professor's height - in a close-up, where he is left out, the
    height of the tallest of the others."""
    if low(s):
        return max(height(s, name) for name in ("cat", "agent", "caterpillar"))
    return height(s, "professor")


def tallest(s: Strip) -> float:
    """The tallest of the cast in this frame: a door is 1.3 times that."""
    names = ("agent", "cat", "caterpillar") if low(s) else ("professor", "agent", "cat", "caterpillar")
    return max(height(s, name) for name in names)


def settle(s: Strip, geom) -> None:
    """Make the cast smaller, if need be, until the station at its true size - `geom()` gives its width and height
    for the cast as it stands now - fits the frame with its two onlookers beside it."""
    if low(s):
        return
    for _ in range(5):
        w, h = geom()
        f = min(1.0, (room(s) - 40) / w, (lane(s).feet - s.ceil - 4) / h)
        if f > 0.995:
            return
        s.tall *= f * 0.99
        s.unit = s.tall / 137


def cap_k(s: Strip) -> float:
    """A cargo capsule's scale: as tall as the agent's waist to chest."""
    return height(s, "agent") * 0.5 / 58


def door_k(s: Strip) -> float:
    return tallest(s) * 1.3 / DOOR_CLEAR


# ============================================================================ the stations
HEAPS = {"pile": [(0, 0), (46, 0), (92, 0), (23, -59)],
         "heap": [(0, 0), (46, 0), (92, 0), (138, 0), (23, -59), (69, -59), (115, -59), (46, -118), (92, -118)]}


def pile_station(s: Strip, beat: str) -> None:
    """Review no longer works as it used to: the airlock's inner door in the hull wall, capsules coming out of it
    and heaping on the deck, the professor at his desk opening and reading one at a time. "pile": a few in the
    heap, he reads; "heap": the heap up the door, he has given up - and the sparrow is after the red emergency
    button on the wall."""
    r = lane(s)
    spots = HEAPS[beat]

    def geom():
        kd, kc, kk = door_k(s), cap_k(s), pr_(s) * 0.5 / 62
        return 122 * kd + 12 + 184 * kc + 12 + 114 * kk, max(165 * kd, 177 * kc)
    settle(s, geom)
    kd, kc, kk = door_k(s), cap_k(s), pr_(s) * 0.5 / 62
    if low(s):                                                         # the close-up: the heap and the desk
        spots = [(dx, dy) for dx, dy in spots if dy > -100]
        kd = 0.0
    w = geom()[0] - (122 * door_k(s) + 12 if low(s) else 0)
    x0 = middle(s, w / kc, kc)
    c = Canvas()
    bh = bulkhead(c, x0 + 47 * kd, r.feet, kd, open_=0.85) if kd else {"box": (x0, r.feet, x0, r.feet)}
    hx = x0 + (122 * kd + 12 if kd else 0) + 23 * kc
    for q, (dx, dy) in enumerate(spots):                              # the capsules heaped on the deck
        cargo(c, hx + dx * kc, r.feet + dy * kc, kc, color=(INDIGO, P.ORANGE, P.TEAL)[q % 3])
    dk = desk(c, x0 + w - 57 * kk, r.feet, kk, opened=True)
    tops = min(r.feet + (dy - 59) * kc for _, dy in spots)
    box = place(s, c, (bh["box"][0], min(bh["box"][1], tops, dk["box"][1]), dk["box"][2], r.feet), "airlock")
    lead_ = "professor"
    mate = "cat" if beat == "pile" else "agent"
    cast(s, box, ((lead_, 1, "read" if beat == "pile" else "think", "talk" if beat == "pile" else "worry",
                   None if beat == "heap" else handheld.sheet),
                  (mate, -1, "think" if beat == "pile" else "present",
                   "smile" if beat == "pile" else "worry", space_mug if mate == "cat" else checklist(mates(s)))))
    if beat == "heap":
        for f in (0.04, 0.96, 0.9, 0.1):
            if alarm(s, s.x(f), r.feet - pr_(s) * 0.6, s.unit, sparrow=True):
                break
    else:
        perch(s, fx(s, hx + 23 * kc), r.feet - 118 * kc + 2, "airlock")


def learn_station(s: Strip, beat: str) -> None:
    """Learning the project needs no review: in the briefing room the big screen on the wall over its cabinet, its
    picture at the cast's eye level, shows a module of the base in section; the agent explains it, the
    caterpillar asks. "ask": the whole module; "learn": its air pump close up, the caterpillar has got it."""
    r = lane(s)

    def geom():
        k = pr_(s) * 0.55 / 92
        return 152 * k, 165 * k
    settle(s, geom)
    k = pr_(s) * 0.55 / 92
    c = Canvas()
    if low(s):                                                         # the close-up: the screen at eye level
        k = pr_(s) * 0.42 / 92
        foot = r.feet - pr_(s) * 0.74 + 114 * k
        sc = wall_screen(c, s.x(0.5), foot, k, zoomed=beat == "learn", cabinet=False)
    else:
        sc = wall_screen(c, s.x(0.5), r.feet, k, zoomed=beat == "learn")
    box = place(s, c, sc["box"], "screen")
    cast(s, box, (("agent", -1, "point", "talk", None),
                  ("caterpillar" if beat == "ask" else "cat", 1,
                   "think" if beat == "ask" else "cheer", "smile",
                   checklist(mates(s)) if beat == "ask" else None)))
    perch(s, s.x(0.5), box[1], "screen")


def decide_station(s: Strip, beat: str) -> None:
    """Agents check, a person takes the key decisions: the console stands against the wall under a big window, its
    desk at the professor's waist, and out of the window two rovers scan the capsules lined up on the dust; at the
    console the professor reads their findings - "watch" - and then has his hand over the two guarded buttons,
    accept and reject - "decide"."""
    r = lane(s)

    def geom():
        k = pr_(s) * 0.5 / 70
        return 162 * k, 120 * k + 40
    settle(s, geom)
    k = pr_(s) * 0.5 / 70
    c = Canvas()
    cn = console(c, s.x(0.48), r.feet, k, report=True)
    box = place(s, c, cn["box"], "console")

    def rovers(cc: Canvas, horizon: float, ground: float) -> None:
        x0, x1 = box[0] - 10, box[2] + 10
        ground = min(ground, box[1] - 4)                               # in sight over the console
        rk = max(0.05, (ground - horizon) * 0.95 / 131)
        for q, f in enumerate((0.26, 0.72)):
            x = x0 + (x1 - x0) * f
            rv = rover(cc, x, ground, rk, lamp=P.GREEN if q == 0 or beat == "decide" else P.YELLOW)
            ck = rk * 0.8
            cx_ = rv["scanner"][0] + 26 * ck
            cargo(cc, cx_, ground, ck)
            scan(cc, rv["scanner"], (cx_ - 20 * ck, ground - 46 * ck, ground - 12 * ck))
    top_ = s.ceil + 8
    high = max(0.1, ((box[1] - 4) - top_) * 0.25 / max(1.0, box[1] + (box[3] - box[1]) * 0.4 - top_))
    win = None if low(s) else window_over(s, box, things=rovers, earth_=False, high=high)
    if win:
        box = (box[0], win[1], box[2], box[3])
    for (px, py, w), key in zip(cn["plates"], ("accept", "reject"), strict=True):
        words(s, fx(s, px), py, s.word(key), w)
    lead_ = "professor"
    mate = "agent" if beat == "decide" else ("cat" if lead_ != "cat" else "caterpillar")
    cast(s, box, ((lead_, -1, "point" if beat == "decide" else "think", "talk", None),
                  (mate, 1, "present", "smile", space_mug if mate == "cat" else None)))


def rover_station(s: Strip, beat: str) -> None:
    """A subagent is an independent reviewer: the inspection rover in its own bay of the garage, marked out on the
    deck - its own solar deck, its own aerials, no line to the base - its arm out over a capsule. "scan": the
    light from its scanner head lies across the capsule's side; "done": its lamp green, the arm still."""
    r = lane(s)

    def geom():
        kr = pr_(s) * 0.8 / 130
        return 246 * kr + 60 * cap_k(s), 131 * kr
    settle(s, geom)
    kr, kc = pr_(s) * 0.8 / 130, cap_k(s)
    w = 246 * kr + 60 * kc
    x0 = middle(s, w / kr, kr)
    c = Canvas()
    c.add(f'<rect x="{n(x0 - 8)}" y="{n(r.feet - 3 * kr)}" width="{n(w + 16)}" height="{n(3 * kr)}" '
          f'fill="{P.YELLOW}"/>')                                                               # its bay's line
    rv = rover(c, x0 + 84 * kr, r.feet, kr, lamp=P.YELLOW if beat == "scan" else P.GREEN)
    cx_ = rv["scanner"][0] + 44 * kr + 20 * kc
    cargo(c, cx_, r.feet, kc)
    if beat == "scan":
        scan(c, rv["scanner"], (cx_ - 20 * kc, r.feet - 48 * kc, r.feet - 8 * kc))
    box = place(s, c, (x0 - 8, rv["box"][1], max(cx_ + 24 * kc, x0 + w + 8), r.feet), "bay")
    cast(s, box, (("agent", -1, "point" if beat == "scan" else "present", "smile", None),
                  ("cat", 1, "think", "smile",
                   space_mug if beat == "scan" else checklist(mates(s)))))
    perch(s, fx(s, cx_), r.feet - 59 * kc, "bay")


def tunnel_station(s: Strip, beat: str) -> None:
    """Reviewers in CI: in the inspection hall the conveyor at waist height runs through three scanning arches in a
    row - the X-ray tunnel, the laser gate, the camera ring - a capsule riding on it. "pass": it is in the second
    arch, the first lit green; "stop": in the third, the first two green and the third red, the belt stopped."""
    r = lane(s)

    def geom():
        pr = pr_(s)
        return 3.4 * pr, 1.25 * pr * 153 / 143
    settle(s, geom)
    pr = pr_(s)
    kb, ka, kc = pr * 0.42 / 36, pr * 1.25 / 143, cap_k(s)
    stop = beat == "stop"
    lamps = (True, True, False) if stop else (True, None, None)
    if low(s):                                                         # the close-up: the line and its board
        kbd = pr * 0.5 / 150                                           # the board beside the line, at eye level
        width = min(1.6 * pr, room(s) - 30 - 156 * kbd)
        x0 = middle(s, (width + 156 * kbd) / kb, kb)
        c = Canvas()
        top = conveyor(c, x0, x0 + width, r.feet, kb)
        for q, f in enumerate((0.2, 0.5, 0.8)):
            cargo(c, x0 + width * f, top, kc, color=(P.ORANGE, INDIGO, P.TEAL)[q])
        sb = status_board(c, x0 + width + 6 + 76 * kbd, r.feet - pr * 0.72, kbd, lamps)
        box = place(s, c, (x0, min(sb["box"][1], top - 60 * kc), sb["box"][2], r.feet), "tunnel")
        cast(s, box, (("agent", -1, "point" if stop else "present", "smile", None),
                      (("cat" if not stop else "caterpillar"), 1, "think",
                       "smile" if not stop else "talk",
                       space_mug if not stop else None)))
        perch(s, fx(s, x0 + width * 0.55), top - 59 * kc, "tunnel")
        return
    width = 3.4 * pr
    x0 = middle(s, width / kb, kb)
    c = Canvas()
    top = conveyor(c, x0, x0 + width, r.feet, kb)
    for q in range(3):
        arch(c, x0 + (0.62 + q * 1.06) * pr, r.feet, ka, q, lamps[q])
    cx = x0 + (0.62 + (2 if stop else 1) * 1.06) * pr
    cargo(c, cx, top, kc, color=P.ORANGE)
    cargo(c, x0 + 0.16 * pr, top, kc)                                  # the next one waiting on the belt
    box = place(s, c, (x0, r.feet - 153 * ka, x0 + width, r.feet), "tunnel")
    cast(s, box, (("agent", -1, "point" if stop else "present", "smile", None),
                  (("cat" if not stop else "caterpillar"), 1, "think",
                       "smile" if not stop else "talk",
                   space_mug if not stop else None)))
    perch(s, fx(s, x0 + 0.62 * pr), r.feet - 150 * ka, "tunnel")


def shared_station(s: Strip, beat: str) -> None:
    """One reviewer for every repository: a wide window in the wall, and out of it three bases on the dust, each
    with its landing pad, joined by a road; one inspection rover drives the road from one to the next - "go",
    "next" - its dust trailing. In front of the window the professor watches it through a telescope on its tripod,
    its eyepiece at his chest."""
    r = lane(s)
    lo, hi = s.x(0.24), s.x(0.76)
    win = (lo, s.ceil + 8, hi, s.base - max(10.0, s.base * 0.16))

    def bases(cc: Canvas, horizon: float, ground: float) -> None:
        ok = (ground - horizon) / 34
        road = ground - 3 * ok
        cc.line(f"M{n(lo)},{n(road)} H{n(hi)}", 4 * ok, REGOLITH_DARK, 0.7)
        for bx in (0.16, 0.5, 0.84):
            x = lo + (hi - lo) * bx
            module_far(cc, x - 10 * ok, road - 6 * ok, ok * 0.45, lit=True)
            pad_far(cc, x + 16 * ok, road + 1, ok * 0.35)
        rover(cc, lo + (hi - lo) * (0.33 if beat == "go" else 0.67), road + ok, ok * 0.16, way=1, dust=True,
              arm=False)
    window(s, win, seed=getattr(s, "index", 0) * 5, things=bases, earth_=True)
    k = pr_(s) * 0.6 / 70
    c = Canvas()
    telescope(c, s.x(0.42), r.feet, k)
    box = place(s, c, (lo - 6, win[1] - 6, hi + 6, r.feet), "view")
    cast(s, box, (("professor" if beat == "go" else "agent", 1, "think", "smile", None),
                  ("caterpillar" if beat == "go" else "cat", -1, "present", "smile",
                   checklist(mates(s)) if beat == "go" else space_mug)))


def sign_station(s: Strip, beat: str) -> None:
    """Who owns, who approves, who merges: at the airlock's inner door in the hull wall the agent signs the
    capsule's delivery note and the cat stamps it approved - "sign", the door shut; once both have, it slides open
    by itself and the capsule on its platform cart goes in - "open"."""
    r = lane(s)

    def geom():
        kd, kt = door_k(s), height(s, "agent") * 0.55 / 56
        return 122 * kd + 12 + 84 * kt, 165 * kd
    settle(s, geom)
    kd, kt, kc = door_k(s), height(s, "agent") * 0.55 / 56, cap_k(s)
    if low(s):                                                         # the close-up: the cart and its note
        c = Canvas()
        cx_ = s.x(0.5)
        ct = cart(c, cx_, r.feet, kt)
        cargo(c, cx_ + 6 * kt, ct["bed"], kc)
        nx, ny = cx_ + 6 * kt, ct["bed"] - 30 * kc                    # the delivery note taped to the drum
        c.add(f'<rect x="{n(nx - 9 * kc)}" y="{n(ny - 11 * kc)}" width="{n(18 * kc)}" height="{n(22 * kc)}" '
              f'fill="{P.WHITE}" stroke="{INK}" stroke-width="1"/>')
        c.line(f"M{n(nx - 6 * kc)},{n(ny - 6 * kc)} h{n(12 * kc)} M{n(nx - 6 * kc)},{n(ny - 2 * kc)} h{n(9 * kc)}",
               1, INK, 0.6)
        if beat == "open":                                             # stamped
            c.add(f'<circle cx="{n(nx + 2 * kc)}" cy="{n(ny + 5 * kc)}" r="{n(5 * kc)}" fill="none" '
                  f'stroke="{P.GREEN}" stroke-width="{n(1.6 * kc)}"/>')
        box = place(s, c, ct["box"], "hatch")
        cast(s, box, (("agent", -1, "present", "smile", handheld.sheet if beat == "sign" else None),
                      ("cat", 1, "present", "smile", stamp)))
        perch(s, fx(s, cx_ + 6 * kt), ct["bed"] - 59 * kc, "hatch")
        return
    w = geom()[0]
    x0 = middle(s, w / kd, kd)
    c = Canvas()
    bh = bulkhead(c, x0 + 47 * kd, r.feet, kd, open_=1.0 if beat == "open" else 0.0)
    cx_ = x0 + 122 * kd + 12 + 42 * kt
    ct = cart(c, cx_, r.feet, kt)
    cargo(c, cx_ + 6 * kt, ct["bed"], kc)
    box = place(s, c, (bh["box"][0], bh["box"][1], ct["box"][2], r.feet), "hatch")
    cast(s, box, (("agent", -1, "present", "smile", handheld.sheet),
                  ("cat", 1, "present", "smile", stamp)))
    perch(s, fx(s, cx_ + 6 * kt), ct["bed"] - 59 * kc, "hatch")


def glass(s: Strip, box: tuple) -> None:
    """The greenhouse module's big window over its bench or rack (`box`): the Moon and the Earth over the plants,
    its sill behind them, the wall under it, so the bench and the cart stand on the corridor floor in front of the
    wall; the wall's fittings keep off it."""
    win = window_over(s, box, earth_=True)
    if win:
        s.put(0.5, "", win, "glass", group="greenhouse", backdrop=True)


def keepers_station(s: Strip, beat: str) -> None:
    """Code owners: "plates" - the corridor's doors in the hull wall, each with its keeper's name plate, a capsule
    for the greenhouse on its platform cart at the right one; "dome" - in the greenhouse module, the Moon and the
    Earth in its big window over the plants, the capsule has come to its keeper, the caterpillar with her watering
    can at the hydroponic rack."""
    r = lane(s)
    c = Canvas()
    if low(s):
        kt, kc = height(s, "agent") * 0.55 / 56, cap_k(s)
        if beat == "plates":                                           # the cart at the keeper's name plate
            cx_ = s.x(0.5)
            ct = cart(c, cx_, r.feet, kt)
            cargo(c, cx_ + 6 * kt, ct["bed"], kc, color=P.GREEN)
            box = place(s, c, ct["box"], "corridor")
            pw = pr_(s) * 0.5
            py = r.feet - pr_(s) * 0.82
            name_plate(s, fx(s, cx_), py, pw, s.word("plate_green"))
            box = (box[0], py - pw * 0.1, box[2], box[3])
            cast(s, box, (("agent", 1, "point", "smile", None), ("cat", -1, "think", "smile", space_mug)))
            perch(s, fx(s, cx_ + 6 * kt), ct["bed"] - 59 * kc, "corridor")
        else:                                                          # the bench under the dome's glass
            k = pr_(s) * 0.92 / 99
            gb = garden_bench(c, s.x(0.42), r.feet, k)
            cx_ = gb["box"][2] + 12 + 42 * kt
            ct = cart(c, cx_, r.feet, kt)
            cargo(c, cx_ + 6 * kt, ct["bed"], kc, color=P.GREEN, open_=True)
            box = place(s, c, (gb["box"][0], gb["box"][1], ct["box"][2], r.feet), "greenhouse")
            glass(s, box)
            cast(s, box, (("caterpillar", -1, "present", "smile", watering_can),
                          ("agent", 1, "present", "smile", None)))
        return
    if beat == "plates":
        def geom():
            kd, kt = door_k(s), height(s, "agent") * 0.55 / 56
            return 2 * 128 * kd + 24 + 84 * kt, 165 * kd
        settle(s, geom)
        kd, kt, kc = door_k(s), height(s, "agent") * 0.55 / 56, cap_k(s)
        w = geom()[0]
        x0 = middle(s, w / kd, kd)
        plates = []
        for q in range(2):
            bh = bulkhead(c, x0 + (47 + q * 140) * kd, r.feet, kd, plate=True)
            plates.append(bh["plate"])
        cx_ = x0 + w - 42 * kt
        ct = cart(c, cx_, r.feet, kt)                                  # the capsule for the greenhouse
        cargo(c, cx_ + 6 * kt, ct["bed"], kc, color=P.GREEN)
        box = place(s, c, (x0, r.feet - 165 * kd, x0 + w, r.feet), "corridor")
        for (px, py, pw), key in zip(plates, ("plate_green", "plate_dock"), strict=True):
            name_plate(s, fx(s, px), py, pw, s.word(key))
        cast(s, box, (("agent", 1, "point", "smile", None), ("cat", -1, "think", "smile", space_mug)))
        perch(s, fx(s, cx_ + 6 * kt), ct["bed"] - 59 * kc, "corridor")
    else:
        def geom():
            k, kt = pr_(s) * 1.05 / 130, height(s, "agent") * 0.55 / 56
            return 182 * k + 12 + 84 * kt, 161 * k
        settle(s, geom)
        k, kt, kc = pr_(s) * 1.05 / 130, height(s, "agent") * 0.55 / 56, cap_k(s)
        w = geom()[0]
        x0 = middle(s, w / k, k)
        gr = greenhouse_rack(c, x0 + 91 * k, r.feet, k, ribs=False)
        cx_ = x0 + w - 42 * kt
        ct = cart(c, cx_, r.feet, kt)
        cargo(c, cx_ + 6 * kt, ct["bed"], kc, color=P.GREEN, open_=True)
        box = place(s, c, (gr["box"][0], gr["box"][1], ct["box"][2] + 6, r.feet), "greenhouse")
        glass(s, box)
        cast(s, box, (("caterpillar", -1, "present", "smile", watering_can),
                      ("agent", 1, "present", "smile", None)))


def test_station(s: Strip, beat: str) -> None:
    """Checking that review works: a test capsule with a crack planted in it, ringed in red, rides the conveyor into
    the scanning arch - "send", the diverter's flap shut, the cat starting his stopwatch; the arch finds it - its
    lamp red, a red stripe on its screen - and the flap drops: the capsule slides down the chute, motion lines
    behind it, towards the reject bin with its word on it - "caught" - the cat stopping his watch."""
    r = lane(s)

    def geom():
        pr = pr_(s)
        kb = pr * 0.42 / 36
        return 1.9 * pr + 150 * kb, 1.25 * pr * 153 / 143
    settle(s, geom)
    pr = pr_(s)
    kb, ka, kc = pr * 0.42 / 36, pr * 1.25 / 143, cap_k(s)
    caught = beat == "caught"
    if low(s):                                                         # the close-up: the line's end, the reject
        kr = kb * 0.62                                                 # the reject bin, knee high
        belt = max(0.8 * pr, min(1.1 * pr, room(s) - 30 - 150 * kr))
        width = belt + 150 * kr
        x0 = middle(s, width / kb, kb)
        c = Canvas()
        gap = (x0 + belt - 40 * kb, x0 + belt)
        top = conveyor(c, x0, x0 + belt + 20 * kb, r.feet, kb, gap=gap)
        rj = reject(c, gap[0], r.feet, kr, top, open_=caught)
        km = pr * 0.3 / 60
        top_y = top - 62 * kc
        if top - 62 * kc - 51 * km > s.ceil + 4:
            wall_monitor(c, x0 + belt * 0.45, top - 62 * kc - 22 * km, km, caught)
            top_y -= 51 * km
    else:
        width = geom()[0]
        x0 = middle(s, width / kb, kb)
        c = Canvas()
        gap = (x0 + 1.9 * pr - 40 * kb, x0 + 1.9 * pr)
        top = conveyor(c, x0, x0 + 1.9 * pr + 20 * kb, r.feet, kb, gap=gap)
        rj = reject(c, gap[0], r.feet, kb, top, open_=caught)
        arch(c, x0 + 1.15 * pr, r.feet, ka, 0, False if caught else None, screen=True)
        top_y = r.feet - 153 * ka
    if caught:                                                         # sliding down the chute
        (ax, ay), (bx, by) = rj["chute"]
        t_ = 0.55
        px, py = ax + (bx - ax) * t_, ay + (by - ay) * t_
        ang = math.degrees(math.atan2(by - ay, bx - ax))
        cargo(c, px, py - 1, kc, color=P.ORANGE, crack=True, turn=ang)
        c.line(" ".join(f"M{n(px - (40 + q * 6) * kc)},{n(py - (30 - q * 12) * kc - (bx - ax) * 0)} l{n(-14 * kc)},"
                        f"{n(-14 * kc * (by - ay) / (bx - ax))}" for q in range(3)), 1.6, INK, 0.7)
    else:
        cargo(c, x0 + (0.18 * pr if low(s) else 0.3 * pr), top, kc, color=P.ORANGE, crack=True)
    box = place(s, c, (x0, top_y, x0 + width, r.feet), "test")
    px_, py_, pw_ = rj["plate"]
    words(s, fx(s, px_), py_ + 5, s.word("reject_bin"), pw_)
    cast(s, box, (("agent" if not caught else "caterpillar", -1, "present" if not caught else "cheer", "smile",
                   None),
                  ("cat", 1, "present", "smile", handheld.stopwatch)))
    if beat == "send":
        # the golden floppy (an easter egg, `world_kit.hide`): caught already, standing on the reject bin's far
        # rim - or riding the conveyor behind the test capsule
        bx0, btop, bx1, _ = rj["bin"]
        cap = x0 + (0.18 * pr if low(s) else 0.3 * pr)
        end = gap[0] - 18 if low(s) else x0 + 1.15 * pr - 0.6 * pr     # short of the chute, or of the arch
        stash_along(s, [fx(s, bx1 - q) for q in (16, 20, 24)], btop, r.feet - 0.4, group="test") or \
            stash_along(s, [fx(s, cap + d * pr) for d in (0.36, 0.3, 0.42, 0.26, 0.48) if cap + d * pr < end], top,
                        r.feet - 0.5, group="test")
        for f in (0.96, 0.04, 0.9, 0.1):
            if alarm(s, s.x(f), r.feet - pr * 0.6, s.unit, sparrow=True):
                break
    elif not low(s):
        perch(s, fx(s, x0 + 1.15 * pr), r.feet - 150 * ka, "test")


# ============================================================================ the finale
BAYS = ("pile", "learn", "decide", "rover", "tunnel", "shared", "sign", "keepers", "test")


def finale(s: Strip) -> None:
    """The whole base at once, cut open under the black starry sky: the long module in section on two decks, its
    white hull round it. On the upper deck, each in a room of its own between bulkheads, the airlock and its heap,
    the briefing screen, the console with its two buttons, the rover's bay, the conveyor through its arches; on
    the lower deck the telescope, the inner hatch and its cart, the greenhouse rack, the test arch - each station's
    name on a plaque over it; the cast on the lower deck, all at one scale."""
    backdrop(s, 3)
    r = lane(s)
    left, right = s.lo, s.hi
    span_ = right - left
    named = s.h >= 300
    size = 11.0 if named else 9.0
    th = tag_size("Ag", size)[1]
    widest = max(tag_size(s.word(key), size)[0] for key in BAYS)
    slot = span_ / 5
    if widest > slot - 8:
        size = max(sets.LETTERING_MIN + 1, size * (slot - 8) / widest)
        th = tag_size("Ag", size)[1]
    label = th + 10 if named else 4
    feet = r.feet
    rows = ((BAYS[:5], feet * 0.56), (BAYS[5:], feet)) if named else ((BAYS[:5], feet),)
    if named:                                                          # the base cut open under the sky
        hull_top = feet * 0.56 - min(feet * 0.56 * 0.92, 0.56 * feet - 20) * 0.9 - 18
        sky = Canvas()
        sky.add(f'<rect x="-6" y="-6" width="{W + 12}" height="{n(hull_top + 8)}" fill="{SKY}"/>')
        sets.stars(sky, (0, 0, W, hull_top - 8), 20, seed=4)
        hl, hr = max(10.0, left - 24), min(W - 10.0, right + 24)     # the whole hull in the frame, both ends round
        hull_d = rounded_rect_d(hl, hull_top, hr - hl, s.base - hull_top + 4, 28)
        sky.add(f'<path d="{hull_d}" fill="none" stroke="{INK}" stroke-width="16"/>'
                f'<path d="{hull_d}" fill="none" stroke="{HULL}" stroke-width="12"/>')
        sky.add(f'<rect x="{n(hl + 6)}" y="{n(feet * 0.56)}" width="{n(hr - hl - 12)}" height="8" fill="{WALL}" '
                f'stroke="{INK}" stroke-width="1.2"/>')                                          # the upper deck
        keys, floor = rows[0]                                          # the bulkheads between the upper rooms
        for q in range(1, len(keys)):
            bx, y0 = left + span_ * q / len(keys), hull_top + 8
            sky.add(f'<rect x="{n(bx - 3)}" y="{n(y0)}" width="6" height="{n(floor - y0)}" fill="{WALL}" '
                    f'stroke="{INK}" stroke-width="1"/>')
        s.put(0.4, sky.render(), None)
    pen = Pen(s, 0, 0, 1)
    things = Canvas()
    tops = {}
    feet_ = lane(s).feet
    pr0 = height(s, "professor")
    a_, m_ = height(s, "agent") / pr0, tallest(s) / pr0
    ratio = {name: (_box(s, name, 0, feet_)[2] - _box(s, name, 0, feet_)[0]) / pr0
             for name in ("professor", "cat", "agent", "caterpillar")}
    kd, kc, kt = 1.3 * m_ / DOOR_CLEAR, 0.5 * a_ / 58, 0.55 * a_ / 56
    dims = {"pile": (122 * kd + 0.06 + 138 * kc, 165 * kd), "learn": (152 * 0.55 / 92, 165 * 0.55 / 92),
            "decide": (162 * 0.5 / 70, 120 * 0.5 / 70), "rover": (216 * 0.8 / 130 + 60 * kc, 131 * 0.8 / 130),
            "tunnel": (3.4, 1.34), "shared": (80 * 0.6 / 70, 70 * 0.6 / 70),
            "sign": (122 * kd + 0.06 + 84 * kt, 165 * kd), "keepers": (182 * 1.05 / 130 + 0.06, 161 * 1.05 / 130),
            "test": (1.9 + 150 * 0.42 / 36, 1.34)}
    cast_order = ("professor", "cat", "agent", "caterpillar")
    gap = 14.0
    pr = 1e9
    for ri, (keys, floor) in enumerate(rows):
        room_h = floor - (rows[0][1] + 8 if ri else (hull_top + 8 if named else s.ceil)) - label - 8
        wsum = sum(dims[key][0] for key in keys) + (sum(ratio.values()) if ri == len(rows) - 1 else 0)
        count = len(keys) + (4 if ri == len(rows) - 1 else 0)
        pr = min(pr, (span_ - gap * (count + 1)) / wsum, room_h / max(dims[key][1] for key in keys))
    pr = min(pr, pr0 * 1.3)
    a, hm = pr * a_, pr * m_
    kd, kc, kt = 1.3 * hm / DOOR_CLEAR, 0.5 * a / 58, 0.55 * a / 56
    for ri, (keys, floor) in enumerate(rows):
        last = ri == len(rows) - 1
        items = list(keys) if not last else [k_ for pair in zip(cast_order, keys, strict=False) for k_ in pair]
        widths = [dims[k_][0] * pr if k_ in dims else ratio[k_] * pr for k_ in items]
        spare = (span_ - sum(widths)) / (len(items) + 1)
        x = left + spare
        for key, w in zip(items, widths, strict=True):
            mid_x = x + w / 2
            x += w + spare
            if key in ratio:                                           # one of the cast
                who = s.actor(key, mid_x, feet, {"professor": "think", "cat": "present", "agent": "point",
                                                  "caterpillar": "present"}[key], "smile", flip=True,
                              tall=s.tall * SIZE[key] * pr / pr0, group=f"f{key}")
                if key == "cat":
                    held(s, who, handheld.stopwatch)
                elif key == "caterpillar":
                    held(s, who, checklist(10))
                continue
            x0 = mid_x - w / 2
            if key == "pile":
                bulkhead(things, x0 + 47 * kd, floor, kd, open_=0.85)
                for q, (dx, dy) in enumerate(((0, 0), (46, 0), (92, 0), (23, -59))):
                    cargo(things, x0 + 122 * kd + 0.06 * pr + 23 * kc + dx * kc, floor + dy * kc, kc,
                          color=(INDIGO, P.ORANGE, P.TEAL, INDIGO)[q])
            elif key == "learn":
                wall_screen(things, mid_x, floor, pr * 0.55 / 92, False)
            elif key == "decide":
                console(things, mid_x, floor, pr * 0.5 / 70, True)
            elif key == "rover":
                kr = pr * 0.8 / 130
                rv = rover(things, x0 + 84 * kr, floor, kr, lamp=P.YELLOW)
                cx_ = rv["scanner"][0] + 14 * kr + 20 * kc
                cargo(things, cx_, floor, kc)
                scan(things, rv["scanner"], (cx_ - 20 * kc, floor - 48 * kc, floor - 8 * kc))
            elif key == "tunnel":
                kb, ka = pr * 0.42 / 36, pr * 1.25 / 143
                top = conveyor(things, x0, x0 + 3.4 * pr, floor, kb)
                for q in range(3):
                    arch(things, x0 + (0.62 + q * 1.06) * pr, floor, ka, q, True)
                cargo(things, x0 + 1.68 * pr, top, kc, color=P.ORANGE)
            elif key == "shared":
                telescope(things, mid_x, floor, pr * 0.6 / 70)
            elif key == "sign":
                bulkhead(things, x0 + 47 * kd, floor, kd, open_=1.0)
                cx_ = x0 + w - 42 * kt
                ct = cart(things, cx_, floor, kt)
                cargo(things, cx_ + 6 * kt, ct["bed"], kc)
            elif key == "keepers":
                greenhouse_rack(things, mid_x, floor, pr * 1.05 / 130)
            else:
                kb, ka = pr * 0.42 / 36, pr * 1.25 / 143
                top = conveyor(things, x0, x0 + 1.9 * pr + 20 * kb, floor, kb,
                               gap=(x0 + 1.9 * pr - 40 * kb, x0 + 1.9 * pr))
                reject(things, x0 + 1.9 * pr - 40 * kb, floor, kb, top, open_=True)
                arch(things, x0 + 1.15 * pr, floor, ka, 0, False, screen=True)
                cargo(things, x0 + 0.4 * pr, top, kc, color=P.ORANGE, crack=True)
            over = dims[key][1] if not last else max(dims[key][1], m_ * 1.05)   # over the cast's heads too
            tops[key] = (mid_x, floor - over * pr, ri)
    s.put(1.2, things.render(), None)
    if named:
        placed = []
        for key, (x, top, ri) in sorted(tops.items(), key=lambda kv: kv[1][0]):
            y = top - 6 - th / 2
            tw = tag_size(s.word(key), size)[0]
            for px, py, pw, pri in placed:                             # never one plate on another
                if pri == ri and abs(px - x) < (pw + tw) / 2 + 6 and abs(py - y) < th + 4:
                    y = py - th - 6
            placed.append((x, y, tw, ri))
            holder = pen.tag(f"label{key}", x, y, s.word(key), size, mix(INDIGO, P.CARD, 0.55), INK)
            s.put(2, "", holder.outer, f"label{key}")
        s.put(2, pen.svg(), None)


# ============================================================================ the opener
def lander(c: Canvas, x: float, foot: float, k: float) -> dict:
    """The cargo lander touching down, its footpads at (x, foot), 240 wide and 220 tall: the descent stage - an
    eight-sided box wrapped in gold foil, crinkled, with its cargo bays - on four splayed legs with struts, round
    footpads and contact probes; the engine bell under it with its flame and the dust blowing out sideways; on
    top the ascent cabin, faceted, white with an indigo band, two angled windows, its hatch, the quads of attitude
    thrusters at its corners, a dish aerial and the docking ring. Returns its box."""
    d = Canvas()
    for side in (-1, 1):                                                                       # the dust blown out
        d.add(f'<path d="M{side * 10},0 Q{side * 40},-26 {side * 74},-16 Q{side * 100},-34 {side * 136},-12 '
              f'Q{side * 156},-2 {side * 140},4 Q{side * 80},10 {side * 10},4 Z" '
              f'fill="{mix(REGOLITH, P.WHITE, 0.45)}" stroke="{INK}" stroke-width="1.2" stroke-opacity=".5"/>')
        for q in range(3):
            d.add(f'<circle cx="{side * (150 + q * 12)}" cy="{-12 - q * 7}" r="{4.4 - q}" '
                  f'fill="{mix(REGOLITH, P.WHITE, 0.45)}" stroke="{INK}" stroke-width=".8" stroke-opacity=".5"/>')
    d.add(f'<path d="M-14,-56 Q-8,-20 0,-6 Q8,-20 14,-56 Z" fill="{P.ORANGE}" stroke="{INK}" stroke-width="1.4"/>'
          f'<path d="M-7,-56 Q0,-28 7,-56 Z" fill="{P.YELLOW}"/>')                                 # the flame
    d.shape("M-16,-74 L-12,-56 H12 L16,-74 Z", P.METAL_DARK, sw=1.6, light=None)               # the engine bell
    for side in (-1, 1):                                                                       # the legs
        d.line(f"M{side * 40},-100 L{side * 104},-8 M{side * 40},-80 L{side * 104},-8 M{side * 52},-74 "
               f"L{side * 80},-44", 4, P.METAL_LIGHT)
        d.line(f"M{side * 40},-100 L{side * 104},-8", 1.2, INK, 0.6)
        d.add(f'<ellipse cx="{side * 106}" cy="-5" rx="14" ry="5" fill="{P.METAL}" stroke="{INK}" '
              f'stroke-width="1.4"/>')
        d.line(f"M{side * 100},-2 l{side * -2},12", 1.4, P.METAL_DARK)                         # its probe
    gold = mix(P.YELLOW, P.ORANGE, 0.45)
    d.shape("M-58,-74 L-46,-126 H46 L58,-74 Z", gold, sw=2, light=(-2, -2))                    # descent stage
    d.line("M-50,-112 l14,8 l10,-10 l12,12 l14,-8 l10,10 l14,-8 l12,10 l8,-6 M-54,-90 l16,6 l12,-8 l18,10 "
           "l14,-6 l16,8 l12,-8 l14,6", 1.2, darken(gold, 0.7), 0.8)                            # the crinkled foil
    d.shape(rounded_rect_d(-30, -112, 24, 26, 2), darken(gold, 0.85), sw=1.2, light=None)      # cargo bays
    d.shape(rounded_rect_d(6, -112, 24, 26, 2), darken(gold, 0.85), sw=1.2, light=None)
    d.shape("M-44,-126 L-36,-176 L-10,-196 H24 L44,-170 L44,-126 Z", HULL, sw=2.2, light=(-2, -2))   # the cabin
    d.add(f'<path d="M-42,-150 H44 V-142 H-42 Z" fill="{INDIGO}"/>')
    d.shape("M-30,-176 L-12,-190 H0 L-4,-170 H-30 Z", P.LENS, sw=1.4, light=None)              # its windows
    d.shape("M6,-190 H20 L32,-172 H8 Z", P.LENS, sw=1.4, light=None)
    d.add(f'<path d="M-26,-174 L-14,-186" stroke="{P.WHITE}" stroke-width="2" stroke-opacity=".6"/>')
    d.shape(rounded_rect_d(-12, -140, 22, 14, 2), P.METAL_LIGHT, sw=1.2, light=None)            # its hatch
    for side in (-1, 1):                                                                       # thruster quads
        tx = side * 46
        d.shape(rounded_rect_d(tx - 5, -170, 10, 10, 1.5), P.METAL, sw=1, light=None)
        d.line(f"M{tx},-170 v-6 M{tx},-160 v6 M{tx - 5},-165 h{-6 if side < 0 else 0} M{tx + 5},-165 "
               f"h{6 if side > 0 else 0}", 2.4, P.METAL_DARK)
    d.line("M30,-188 L44,-210", 2, P.METAL_DARK)                                                # the dish aerial
    d.add(f'<path d="M34,-218 Q46,-204 58,-218 Z" fill="{P.WHITE}" stroke="{INK}" stroke-width="1.2"/>')
    d.shape(rounded_rect_d(-6, -202, 20, 6, 2), P.METAL, sw=1, light=None)                     # docking ring
    d.add(f'<circle cx="-46" cy="-130" r="2.6" fill="{P.RED}"/><circle cx="46" cy="-130" r="2.6" '
          f'fill="{P.GREEN}"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 160 * k, foot - 220 * k, x + 160 * k, foot + 10 * k)}


def dome(c: Canvas, x: float, ground: float, k: float) -> dict:
    """The greenhouse: a big glass dome on its indigo ring, the ribs of its frame, plants inside under warm grow
    lights, an airlock hatch at its foot. Returns its box."""
    d = Canvas()
    d.add(f'<path d="M-120,0 A120,100 0 0 1 120,0 Z" fill="{mix(P.LENS, P.WHITE, 0.35)}" fill-opacity=".85" '
          f'stroke="{INK}" stroke-width="2"/>')
    rnd = random.Random(3)
    for q in range(9):
        px = -96 + q * 24
        h = rnd.uniform(18, 34)
        d.add(f'<path d="M{px - 12},0 Q{px - 8},{-h} {px},{-h * 0.7} Q{px + 8},{-h - 6} {px + 12},0 Z" '
              f'fill="{P.GREEN if q % 2 else P.LEAF_DARK}" stroke="{INK}" stroke-width="1"/>')
    d.add(f'<path d="M-90,-46 H90" stroke="{mix(P.PINK, P.SUN, 0.4)}" stroke-width="3" stroke-opacity=".8"/>')
    d.line("M-120,0 A120,100 0 0 1 120,0 M0,-100 V0 M-84,-71 Q-40,-30 -46,0 M84,-71 Q40,-30 46,0 "
           "M-112,-36 Q0,-60 112,-36", 1.6, P.METAL_DARK)
    d.add(f'<path d="M-70,-80 Q-50,-92 -30,-96" fill="none" stroke="{P.WHITE}" stroke-width="5" '
          f'stroke-opacity=".5" stroke-linecap="round"/>')
    d.shape(rounded_rect_d(-124, -2, 248, 12, 3), INDIGO, sw=1.8, light=None)
    c.add(_at(d, x, ground, k))
    return {"box": (x - 124 * k, ground - 100 * k, x + 124 * k, ground + 10 * k)}


def main_module(c: Canvas, x: float, ground: float, k: float) -> dict:
    """The main module: a long white cylinder lying on its legs, indigo bands, a row of warm lit portholes, the
    round hatch at its end with steps down, an aerial dish on its roof. Returns its box."""
    d = Canvas()
    d.shape("M-110,-14 V-70 Q-110,-90 -90,-90 H90 Q110,-90 110,-70 V-14 Z", HULL, sw=2, light=(-2, -2))
    for by in (-80, -24):
        d.add(f'<rect x="-110" y="{by}" width="220" height="6" fill="{INDIGO}"/>')
    for q in range(6):
        d.add(f'<circle cx="{-60 + q * 22}" cy="-52" r="7" fill="{WARM}" stroke="{INK}" stroke-width="1.4"/>')
    d.add(f'<circle cx="-88" cy="-48" r="14" fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="1.6"/>'
          f'<circle cx="-88" cy="-48" r="8" fill="none" stroke="{P.METAL_DARK}" stroke-width="2"/>')
    d.line("M-90,-14 L-96,0 M90,-14 L96,0 M-20,-14 L-24,0 M20,-14 L24,0", 3, P.METAL_DARK)
    d.line("M60,-90 V-112", 2, P.METAL_DARK)
    d.add(f'<path d="M44,-114 Q60,-100 78,-122 Z" fill="{P.WHITE}" stroke="{INK}" stroke-width="1.4"/>')
    c.add(_at(d, x, ground, k))
    return {"box": (x - 112 * k, ground - 124 * k, x + 112 * k, ground)}


def big_earth(c: Canvas, x: float, y: float, r: float) -> None:
    """The Earth hanging in the black sky: blue with its continents and clouds, lit from the left, the night side
    in shadow."""
    d = Canvas()
    clip = d.shape(ellipse_d(0, 0, 50, 50), P.BLUE, sw=2, light=None, clip=True)
    d.add(f'<g clip-path="url(#{clip})"><path d="M-40,-22 q14,-18 32,-6 q-2,16 -18,14 q-12,12 -18,-2 Z M8,2 q22,-10 '
          f'32,6 q-8,22 -22,22 q-14,-8 -10,-28 Z M-20,24 q10,-4 16,4 q-8,10 -16,-4 Z" fill="{P.GREEN}" '
          f'stroke="{INK}" stroke-width="1"/><path d="M-46,8 q20,-10 38,0 M6,-36 q16,-6 30,2 M-14,40 q12,-4 24,0" '
          f'stroke="{P.WHITE}" stroke-width="5" fill="none" stroke-linecap="round" opacity=".9"/>'
          f'<path d="M14,-60 A50,50 0 0 1 14,60 A60,60 0 0 0 14,-60 Z" fill="{INK}" fill-opacity=".35"/></g>')
    c.add(_at(d, x, y, r / 50))


def opener(st: Stage, accent: str):
    """The moon base seen from inside the observatory: the deep indigo sky going black overhead, full of stars, the
    Earth big in it, calm over the title; below it, across the page, the base itself - the main module long on its
    legs with its lit portholes and its aerial, the cargo lander touching down on the pad beside it on its flame,
    dust blowing out sideways from under its legs, the greenhouse dome whole with its lit plants, a rover rolling
    to the lander trailing dust, indigo shadows on the grey dust. In front, inside, the observatory's window frame
    - its pillars and its sill - and the deck: the professor under his bubble, the agent waving to the lander, the
    caterpillar holding on to the sill's rail, the cat timing the landing, the sparrow on the rail."""
    ledger(st)
    c = st.back
    horizon, sill_top, deck_y = 560.0, 900.0, 960.0
    sets.sky(c, mix(P.SPACE_DEEP, INK, 0.35), mix(INDIGO, P.SPACE_DEEP, 0.1), horizon, W)
    sets.stars(c, (30, 0, W - 30, horizon - 30), 80, seed=9)
    big_earth(c, 676, 210, 120)
    st.keep_clear((676 - 126, 84, 676 + 126, 336))
    shade = mix(REGOLITH, INDIGO, 0.35)
    c.add(f'<rect x="-6" y="{horizon}" width="{W + 12}" height="{sill_top - horizon + 6}" fill="{REGOLITH}"/>')
    c.add(f'<path d="M-6,{horizon + 2} Q140,{horizon - 30} 300,{horizon - 10} T620,{horizon - 22} T{W + 6},'
          f'{horizon - 6} V{horizon + 8} H-6 Z" fill="{shade}"/>')                               # far hills
    rnd = random.Random(2)
    for _ in range(10):
        px, py = rnd.uniform(0, W), rnd.uniform(horizon + 14, sill_top - 6)
        c.add(f'<ellipse cx="{n(px)}" cy="{n(py)}" rx="{n(rnd.uniform(60, 140))}" ry="{n(rnd.uniform(5, 11))}" '
              f'fill="{shade}" fill-opacity=".5"/>')
    for cx_, cy_, r_ in ((640, 600, 22), (790, 590, 18), (70, 590, 16), (560, 760, 30)):
        crater(c, cx_, cy_, r_, color=mix(REGOLITH, INDIGO, 0.2))
    for mx in (60, 560, 760):                                         # the far modules of the base
        module_far(c, mx, horizon + 4, 0.8)
    dish_far(c, 470, horizon + 2, 1.4)
    mm = main_module(c, 100, 650, 0.8)                                # the main module, behind
    st.put(0.5, "", mm["box"], "module", group="base", backdrop=True)
    ds = dome(c, 618, 880, 1.15)                                       # the greenhouse, whole, lit
    st.put(0.5, "", ds["box"], "dome", group="base", backdrop=True)
    pad_x, pad_y = 246, 872
    c.add(f'<ellipse cx="{pad_x}" cy="{pad_y}" rx="190" ry="20" fill="{P.METAL}" stroke="{INK}" '
          f'stroke-width="2"/><ellipse cx="{pad_x}" cy="{pad_y}" rx="124" ry="12" fill="none" '
          f'stroke="{P.YELLOW}" stroke-width="3.4"/>')                                           # the landing pad
    c.add(f'<ellipse cx="{pad_x}" cy="{pad_y - 4}" rx="100" ry="30" fill="{P.ORANGE}" fill-opacity=".2"/>')
    ld = lander(c, pad_x, pad_y - 30, 1.55)                             # touching down, big
    st.put(0.6, "", ld["box"], "lander", group="base", backdrop=True)
    rover(c, 548, 894, 0.5, way=1, dust=True, arm=False)
    frame = mix(WALL, P.METAL_DARK, 0.3)                              # the observatory's window frame
    c.add(f'<rect x="-6" y="{sill_top}" width="{W + 12}" height="{deck_y - sill_top}" fill="{WALL}" '
          f'stroke="{INK}" stroke-width="2"/>')
    c.add(f'<rect x="-6" y="{sill_top - 8}" width="{W + 12}" height="10" fill="{P.METAL_LIGHT}" stroke="{INK}" '
          f'stroke-width="2"/>')
    for q in range(60, W, 140):
        c.add(f'<rect x="{q - 8}" y="{deck_y - 12}" width="16" height="5" rx="2" fill="{WARM}"/>')
    for px in (-6, W - 22):
        c.add(f'<rect x="{px}" y="-6" width="28" height="{sill_top + 6}" fill="{frame}" stroke="{INK}" '
              f'stroke-width="2"/>')
        c.add("".join(f'<circle cx="{px + 14}" cy="{by}" r="3" fill="{P.METAL_LIGHT}"/>'
                      for by in range(60, int(sill_top), 120)))
    c.add(f'<path d="M22,{sill_top - 8} L120,{horizon + 40} H150 L52,{sill_top - 8} Z" fill="{P.WHITE}" '
          f'fill-opacity=".06"/>')                                                               # the glass's gleam
    deck(c, -6, W + 6, deck_y, H + 6, 1.6)
    st.keep_clear((-6, sill_top - 10, W + 6, sill_top + 4))
    prof = st.actor("professor", 670, 1100, "explain", "talk", flip=True, tall=350)
    st.speaker(prof, width=74, left=128, air=CLEAR_MM)
    st.actor("agent", 150, 1096, "wave", "smile", flip=False, tall=330, group="agent")
    st.actor("caterpillar", 312, 1104, "present", "worry", flip=False, tall=270, group="caterpillar")
    cat = st.actor("cat", 480, 1130, "present", "smile", flip=False, tall=270, group="cat")
    st.hold(cat, handheld.stopwatch)
    st.actor("sparrow", 806, sill_top - 8, "point", "smile", flip=True, tall=130, group="sparrow")
    drawn = st.render()
    drawn.holders, drawn.links, drawn.ports = st.holders, st.links, st.ports
    return drawn


MOON.stations.extend([
    Station("pile", _framed(pile_station), ("pile", "heap")),
    Station("learn", _framed(learn_station), ("ask", "learn")),
    Station("decide", _framed(decide_station), ("watch", "decide")),
    Station("rover", _framed(rover_station), ("scan", "done")),
    Station("tunnel", _framed(tunnel_station), ("pass", "stop")),
    Station("shared", _framed(shared_station), ("go", "next")),
    Station("sign", _framed(sign_station), ("sign", "open")),
    Station("keepers", _framed(keepers_station), ("plates", "dome")),
    Station("test", _framed(test_station), ("send", "caught")),
])
MOON.backdrop = backdrop
MOON.alternate = True                                       # never one moment on two pages in a row
MOON.finale = finale
OPENERS["lunar_base"] = opener
hide(MOON, "test", "send")

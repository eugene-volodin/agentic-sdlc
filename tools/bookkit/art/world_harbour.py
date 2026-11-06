"""The harbour: the world of chapter 8 (CI, the barrier before main).

A harbour at a warm evening: a plank pier the cast stands on, the near water with the boats moored at it, the far
shore behind - beach huts, warehouses, a crane, a lighthouse, a town on its hill. The inner harbour is main; a pull
request is a boat that wants in; every station is a real harbour operation. One per section of the chapter:

1. entrance    only what passed every check goes into main: the entrance between two breakwater heads, the port's
               entry signal red or green, the boom of steel floats closed - or swung open for the boat flying green;
2. inspection  what to check in CI: the inspection berth - the boat moored with its ropes, the cat at the gangway
               checking the papers, a container opened on the pier, a mirror on a pole looking under the hull;
3. lock        the merge queue: a lock - the boats wait their turn, the one in the chamber rises to the harbour's
               level before the upper gate opens;
4. clock       every check in twenty to thirty minutes: the harbour office's big clock, a green band on its dial
               from twenty to thirty minutes after the start (4:04, like every clock in the book), the cat's
               stopwatch;
5. fix         the agent brings its pull request to green itself: its boat on keel blocks, the agent welds a plate
               over the hole, paints it and flies the green flag;
6. flaky       flaky tests: the boat whose engine starts one time and dies the next, moved to a quarantine berth
               between two dolphins under the yellow Q flag; the cat writes it down;
7. owners      who owns CI: the harbour master's tower, the professor keeping watch with binoculars and the radio;
8. bypass      checking that the checks cannot be got round: the boom made fast to the breakwater's wall - the
               sparrow's paper boat finds no gap.

No words in the pictures but the finale's names of the stations.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten, mix
from . import handheld, sets, stories
from .footers import Strip
from .ink import INK, Canvas, lettering, lettering_width, n, rounded_rect_d
from .openers import CLEAR_MM, H, W, Stage
from .world_fair import glow, held, lane, mid, zoom
from .world_kit import CLOCK_TIME, SIZE, Pen, clock_hands, connect, hide, ledger, port, stash_along, tag_size
from .world_kitchen import _box, _fit_tall
from .world_library import ph
from .world_sea import beside, scale_for, stand
from .worlds import Station, world

HARBOUR = world("harbour", opener="lighthouse")

_at = sets._at

PLUM = P.PLUM
SKY_TOP = mix(PLUM, P.SPACE_DEEP, 0.35)       # the evening sky, plum at the top
SKY_LOW = mix(P.ORANGE, P.YELLOW_PALE, 0.45)   # warm at the horizon
SEA = mix(P.BLUE, PLUM, 0.28)
SEA_DEEP = darken(SEA, 0.78)
PLANK = (mix(P.WOOD, P.WOOD_LIGHT, 0.4), mix(P.WOOD_LIGHT, P.WOOD_PALE, 0.4))
SAND = mix(P.SAND, P.WOOD_PALE, 0.4)
STONE_ = mix(P.STONE, PLUM, 0.15)


def calm(color: str) -> str:
    """A colour of the far harbour, calmer than the station's."""
    return mix(color, SKY_LOW, 0.42)


# ============================================================================ the sea, the pier
def waves(c: Canvas, x0: float, x1: float, y: float, k: float, color: str = P.WHITE, seed: int = 0) -> None:
    """A row of small wave crests along y: short curls of foam."""
    rnd = random.Random(seed)
    x = x0 + rnd.uniform(0, 30) * k
    while x < x1:
        w = rnd.uniform(14, 26) * k
        c.add(f'<path d="M{n(x)},{n(y)} q{n(w / 2)},{n(-5 * k)} {n(w)},0" fill="none" stroke="{color}" '
              f'stroke-width="{n(max(1.0, 1.6 * k))}" stroke-linecap="round" stroke-opacity=".8"/>')
        x += w + rnd.uniform(18, 40) * k


def sea(c: Canvas, x0: float, x1: float, top: float, bottom: float, k: float, seed: int = 0) -> None:
    """The sea from the horizon at `top` down to `bottom`: bands darkening towards the front, rows of wave crests
    growing nearer, the evening sun's glitter."""
    h = bottom - top
    for i, f in enumerate((0.0, 0.3, 0.6)):
        c.add(f'<rect x="{n(x0)}" y="{n(top + h * f)}" width="{n(x1 - x0)}" height="{n(h * (1 - f) + 1)}" '
              f'fill="{mix(lighten(SEA, 0.25), SEA_DEEP, i / 2.4)}"/>')
    for j in range(max(2, int(h / (14 * k)))):
        t = j / max(1, int(h / (14 * k)))
        waves(c, x0, x1, top + 6 + h * t, k * (0.5 + t), seed=seed + j)
    c.line(f"M{n(x0)},{n(top)} H{n(x1)}", 1.2, mix(SKY_LOW, P.WHITE, 0.5))


def planks(c: Canvas, x0: float, x1: float, y0: float, y1: float, k: float) -> None:
    """The pier's deck from y0 down to y1: rows of planks running across, nearer rows wider, their joints and
    nail heads, a heavy edge beam at the back."""
    c.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" fill="{darken(PLANK[0], 0.7)}"/>')
    y, row = y0 + 8 * k, 0
    rnd = random.Random(3)
    while y < y1:
        rh = (6 + row * 3.2) * max(0.6, k)
        x = x0 - rnd.uniform(0, 80)
        while x < x1:
            pl = rnd.uniform(90, 160) * k
            c.add(f'<rect x="{n(x + 0.8)}" y="{n(y + 0.8)}" width="{n(pl - 1.6)}" height="{n(rh - 1.6)}" '
                  f'fill="{PLANK[(row + int(x / 50)) % 2]}"/>')
            if rh > 8:
                c.add(f'<circle cx="{n(x + 5)}" cy="{n(y + rh / 2)}" r="{n(rh * 0.08)}" fill="{P.WOOD_DARK}"/>'
                      f'<circle cx="{n(x + pl - 5)}" cy="{n(y + rh / 2)}" r="{n(rh * 0.08)}" fill="{P.WOOD_DARK}"/>')
            x += pl
        y += rh
        row += 1
    c.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(9 * k)}" fill="{P.WOOD_DARK}" '
          f'stroke="{INK}" stroke-width="1.2"/>')                                             # the edge beam


# ============================================================================ the boat
def sheer(x: float) -> float:
    """How high a boat's deck edge stands over its waterline at x, in its own units (stern -100, bow +104)."""
    t = (x + 100) / 204
    return -28 - 4 * t - 10 * t ** 4


def boat(c: Canvas, x: float, wl: float, k: float, flag: str | None = None, way: int = 1, water: str = SEA,
         cargo: bool = True, moving: bool = False, smoke: str | None = "grey", dry: bool = False,
         patch: str | None = None, hull: str = PLUM, gate: bool = False, name: str = "") -> dict:
    """A small motor cargo boat in side view, its waterline's middle at (x, wl), 204 long, its bow towards `way`.

    Afloat it sits in the water: the hull ends at the waterline, a ripple of foam runs along it and its reflection
    lies broken on the water under it; moving, a bow wave curls at its stem and its wake trails astern. Up from
    the black anti-fouling band and the white boot stripe: the plum hull with its rub rail along the sheer, the
    anchor at the bow, tyre fenders on their ropes, the railing on its stanchions, two containers lashed on the
    hatch forward (`cargo`), the white wheelhouse with its windows, door, lifebuoy and side light, the funnel with
    its band and its smoke (`smoke`: grey, black, None), the mast with its radar and masthead light, and at the
    stern the flag on its staff, cloth with folds (`flag`: its colour, None: bare staff). `dry`: hauled out, its
    bottom showing down to the keel, the propeller and the rudder. `patch`: "hole" in the bow, the "plate" welded
    over it, or the plate "painted". `name`: the boat's name painted in white on its stern - only where it fits at
    a size that reads on the page. Returns where things are, in page space."""
    d = Canvas()
    deck = [(px, sheer(px)) for px in range(-100, 104, 12)] + [(104.0, -42.0)]
    if not dry:                                                      # its reflection, broken by the ripples
        for i, (x0_, x1_, y_) in enumerate(((-98, 84, 4), (-90, 66, 8.5), (-74, 44, 13), (-52, 18, 17))):
            seg = 22 - i * 3
            px = x0_ + i * 5
            while px < x1_:
                d.line(f"M{n(px)},{n(y_)} H{n(min(x1_, px + seg))}", 3.2 - i * 0.5,
                       mix(darken(water, 0.7), hull, 0.3 if i < 2 else 0.1), 0.75)
                px += seg + 7
    bottom = "Q100,-18 86,0 Z" if not dry else "Q101,-16 90,2 Q74,18 44,22 H-76 Q-94,18 -98,0 Z"
    hull_d = "M-98,0 " + " ".join(f"L{n(px)},{n(py)}" for px, py in deck) + " " + bottom
    clip = d.shape(hull_d, hull, sw=0, light=None, clip=True)
    band_h = 7 if not dry else 34
    d.add(f'<g clip-path="url(#{clip})"><rect x="-110" y="-46" width="230" height="22" fill="{darken(hull, 0.86)}" '
          f'fill-opacity=".0"/><rect x="-110" y="-7" width="230" height="{band_h}" fill="{P.CHARCOAL}"/>'
          f'<rect x="-110" y="-9.6" width="230" height="2.6" fill="{P.WHITE}"/>'
          f'<rect x="-110" y="-24" width="230" height="14" fill="{INK}" fill-opacity=".08"/></g>')
    d.path(hull_d, "none", 2.0)
    d.line("M" + " L".join(f"{n(px)},{n(py + 5)}" for px, py in deck[:-1]) + " L101,-37", 3.4,
           darken(hull, 0.62))                                                                  # the rub rail
    if dry:                                                          # the rudder, the propeller and its shaft
        d.shape("M-92,4 L-100,6 L-100,22 L-90,22 Z", P.CHARCOAL, sw=1.2, light=None)
        d.line("M-56,13 L-82,15", 2.2, P.METAL_DARK)
        bronze = mix(P.SUN, P.WOOD, 0.45)
        d.shape("M-83,15 Q-80,5 -84,4 Q-86,9 -83,15 Z", bronze, sw=0.9, light=None)
        d.shape("M-83,15 Q-80,25 -84,26 Q-86,21 -83,15 Z", bronze, sw=0.9, light=None)
        d.add(f'<circle cx="-83" cy="15" r="2" fill="{bronze}" stroke="{INK}" stroke-width=".8"/>')
    if patch == "hole":
        d.shape("M72,-18 l7,-5 l6,4 l2,8 l-7,6 l-8,-3 Z", INK, sw=0.6, light=None)
        d.line("M70,-20 l-4,-3 M88,-10 l3,2 M76,-6 l-2,4", 1, INK, 0.7)                        # its cracks
    elif patch:
        plate = mix(P.METAL, P.WHITE, 0.2) if patch == "plate" else lighten(hull, 0.12)
        d.shape(rounded_rect_d(68, -24, 20, 18, 2), plate, sw=1.2, light=None)
        d.add("".join(f'<circle cx="{px}" cy="{py}" r="1" fill="{INK}"/>' for px in (71, 85) for py in (-21, -9)))
        d.line("M68,-24 H88 V-6 H68 Z", 1.6, mix(P.ORANGE, P.SUN, 0.4) if patch == "plate" else darken(hull, 0.8),
               0.8)                                                                             # the weld seam
    if name:                                                         # its name, painted on the stern
        size = sets.LETTERING_MIN / k
        width = lettering_width(name, size, "label")
        x0_, x1_ = -96.0, -57.0                                      # between the stern and its fender
        if width <= x1_ - x0_ and size <= 13:
            cx_ = (x0_ + x1_) / 2
            flip_ = f' transform="translate({n(2 * cx_)},0) scale(-1,1)"' if way < 0 else ""
            d.add(f'<g{flip_}>{lettering(cx_, -12.5, name, size, P.WHITE, style="label")}</g>')
    s90 = sheer(90)
    d.line(f"M90,{n(s90 + 6)} V{n(s90 + 20)} M86,{n(s90 + 9)} H94 M84,{n(s90 + 15)} Q90,{n(s90 + 24)} 96,"
           f"{n(s90 + 15)}", 1.8, P.METAL_DARK)                                                 # the anchor
    d.add(f'<circle cx="90" cy="{n(s90 + 5)}" r="1.8" fill="none" stroke="{P.METAL_DARK}" stroke-width="1.2"/>')
    for fx in (-52, 24, 56):                                                                    # fenders
        d.line(f"M{fx},{n(sheer(fx) + 3)} V-18", 1, P.KITCHEN_KRAFT)
        d.shape(rounded_rect_d(fx - 3.6, -19, 7.2, 14, 3.4), mix(P.BLUE, P.WHITE, 0.55), sw=1, light=None)
        d.line(f"M{fx - 1.4},-16 v8", 1.2, P.WHITE, 0.8)
    rail_x = [px for px in range(-94, 101, 12) if not -76 <= px <= -18 and not (gate and px == -10)]
    d.line(" ".join(f"M{px},{n(sheer(px))} v-10" for px in rail_x), 1.3, P.METAL_DARK)          # the railing
    fore = range(2, 101, 12) if gate else range(-4, 101, 12)          # the side gate: a gap in the rail
    d.line("M-94," + n(sheer(-94) - 10) + " L-78," + n(sheer(-78) - 10) + " M" + " L".join(
        f"{px},{n(sheer(px) - 10)}" for px in ((-16,) if not gate else ()) + tuple(fore)), 1.3, P.METAL_DARK)
    if cargo:                                                        # the hatch and two containers lashed on it
        d.shape("M0," + n(sheer(0)) + " V-44 H88 V" + n(sheer(88)) + " "
                + " ".join(f"L{px},{n(sheer(px))}" for px in range(84, -1, -12)) + " Z", darken(hull, 0.72),
                sw=1.2, light=None)
        for cx0, col in ((2, P.TEAL), (45, P.ORANGE)):
            d.shape(rounded_rect_d(cx0, -66, 41, 22, 1), col, sw=1.4, light=(-1, -1))
            d.line(" ".join(f"M{cx0 + q},-64 V-46" for q in range(5, 36, 4)), 0.7, darken(col, 0.7))
            d.line(f"M{cx0 + 36},-66 V-44 M{cx0 + 38.5},-64 V-46", 1, INK, 0.7)              # its door end
            d.line(f"M{cx0 + 10},-66 V-44 M{cx0 + 30},-66 V-44", 1.6, P.YELLOW)               # lashing straps
            d.line(f"M{cx0 + 10},-44 L{cx0 + 4},{n(sheer(cx0 + 4))} M{cx0 + 30},-44 L{cx0 + 36},"
                   f"{n(sheer(cx0 + 36))}", 1.2, P.YELLOW)
    wh_base = [(px, sheer(px)) for px in (-72, -22)]
    d.shape(f"M-72,{n(wh_base[0][1])} V-62 H-22 L-18,-48 V{n(wh_base[1][1])} Z", P.WHITE, sw=1.6,
            light=(-1, -1))                                                                     # the wheelhouse
    d.shape(rounded_rect_d(-76, -66, 60, 5, 1.5), hull, sw=1.3, light=None)                     # its roof
    for wx in (-68, -54):
        d.shape(rounded_rect_d(wx, -58, 11, 9, 1.5), P.LENS, sw=1, light=None)
    d.shape("M-22,-58 L-19.5,-49 H-26 V-58 Z", P.LENS, sw=1, light=None)                        # the front window
    d.shape(rounded_rect_d(-38, -56, 10, 25, 1), mix(P.WHITE, P.CARD, 0.5), sw=1.1, light=None)  # the door
    d.add(f'<circle cx="-33" cy="-50" r="2.4" fill="{P.LENS}" stroke="{INK}" stroke-width=".7"/>'
          f'<circle cx="-30.5" cy="-42" r=".9" fill="{INK}"/>')
    d.add(f'<circle cx="-47" cy="-39.5" r="4.6" fill="none" stroke="{INK}" stroke-width="4.4"/>'
          f'<circle cx="-47" cy="-39.5" r="4.6" fill="none" stroke="{P.WHITE}" stroke-width="2.8"/>'
          f'<circle cx="-47" cy="-39.5" r="4.6" fill="none" stroke="{P.RED}" stroke-width="2.8" '
          f'stroke-dasharray="3.6 3.6"/>')                                                      # the lifebuoy
    d.shape(rounded_rect_d(-23, -62, 4, 4, 1), P.GREEN if way > 0 else P.RED, sw=0.7, light=None)  # side light
    d.shape(f"M-91,{n(sheer(-91))} L-89,-76 H-79 L-77,{n(sheer(-77))} Z", hull, sw=1.4, light=None)  # funnel
    d.add(f'<rect x="-89.6" y="-68" width="11.2" height="4" fill="{P.WHITE}"/>'
          f'<rect x="-89" y="-77" width="10" height="3.4" fill="{INK}"/>')
    if smoke:
        col = P.CHARCOAL if smoke == "black" else mix(P.METAL_LIGHT, P.WHITE, 0.3)
        for (sx_, sy_, r_) in ((-86, -82, 4.6), (-92, -90, 6), (-100, -97, 7.2)):
            d.add(f'<circle cx="{sx_}" cy="{sy_}" r="{r_}" fill="{col}" fill-opacity=".85" stroke="{INK}" '
                  f'stroke-width=".8" stroke-opacity=".5"/>')
    d.line("M-46,-66 V-104 M-54,-95 H-38", 2.2, P.METAL_DARK)                                  # the mast
    d.shape(rounded_rect_d(-58, -91, 24, 3.4, 1.5), P.WHITE, sw=1, light=None)                 # its radar
    d.line("M-46,-88 V-86", 1.6, P.METAL_DARK)
    d.add(f'<circle cx="-46" cy="-104" r="2" fill="{P.YELLOW_PALE}" stroke="{INK}" stroke-width=".7"/>')
    d.line(f"M-96,{n(sheer(-96))} V-62", 1.8, P.WOOD_DARK)                                     # the flag staff
    d.add(f'<circle cx="-96" cy="-62.5" r="1.4" fill="{P.WOOD}"/>')
    if flag:
        cloth = "M-96,-61 C-101,-65 -107,-57 -115,-60 Q-118,-61 -120,-59 L-121,-46 C-112,-43 -105,-51 -96,-47 Z"
        d.shape(cloth, flag, sw=1.3, light=None)
        d.line("M-104,-60 C-106,-55 -105,-51 -107,-47.5 M-114,-59 C-115,-55 -114,-50 -116,-45.5", 2,
               darken(flag, 0.72), 0.6)                                                         # its folds
    if not dry:                                                      # the ripple along the waterline
        d.line("M-104,0.5 q5,-2 10,0 " + " ".join("q5,-2 10,0" for _ in range(20)), 1.5, P.WHITE, 0.9)
    if moving:
        d.shape("M80,0 Q93,-8 108,-3 Q100,0 112,3 Q96,6 80,2 Z", P.WHITE, sw=1, light=None)    # the bow wave
        d.line(" ".join(f"M{n(-106 - q * 14)},{n(1 + q)} q5,-3 10,0" for q in range(3)), 1.6, P.WHITE, 0.9)
    c.add(_at(d, x, wl, k, mirror=way < 0))

    def at(px: float, py: float) -> tuple[float, float]:
        return x + px * k * way, wl + py * k
    xs = sorted((x - 124 * k * way, x + 114 * k * way))
    return {"box": (xs[0], wl - 106 * k, xs[1], wl + (24 if dry else 18) * k), "bow": at(92, sheer(92) + 2),
            "stern": at(-88, sheer(-88) + 2), "deck": at(-10, sheer(-10)), "patch": at(80, -14),
            "hull": (min(at(-98, 0)[0], at(100, 0)[0]), wl - 42 * k, max(at(-98, 0)[0], at(100, 0)[0]), wl)}


# ============================================================================ the harbour's fittings
def bollard(c: Canvas, x: float, y: float, k: float, rope: bool = True) -> None:
    """A cast-iron bollard bolted to the pier at (x, y): its base, the waisted post, the cap; a rope's turns."""
    c.add(f'<rect x="{n(x - 10 * k)}" y="{n(y - 4 * k)}" width="{n(20 * k)}" height="{n(4 * k)}" fill="{P.CHARCOAL}" '
          f'stroke="{INK}" stroke-width="{n(max(0.7, k))}"/>')
    c.add(f'<path d="M{n(x - 7 * k)},{n(y - 4 * k)} Q{n(x - 4 * k)},{n(y - 12 * k)} {n(x - 7 * k)},{n(y - 20 * k)} '
          f'H{n(x + 7 * k)} Q{n(x + 4 * k)},{n(y - 12 * k)} {n(x + 7 * k)},{n(y - 4 * k)} Z" fill="{P.CHARCOAL}" '
          f'stroke="{INK}" stroke-width="{n(max(0.7, k))}"/>')
    c.add(f'<rect x="{n(x - 10 * k)}" y="{n(y - 24 * k)}" width="{n(20 * k)}" height="{n(5 * k)}" rx="{n(2 * k)}" '
          f'fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="{n(max(0.7, k))}"/>')
    if rope:
        c.line(f"M{n(x - 7 * k)},{n(y - 14 * k)} q{n(7 * k)},{n(4 * k)} {n(14 * k)},0 "
               f"M{n(x - 7 * k)},{n(y - 10 * k)} q{n(7 * k)},{n(4 * k)} {n(14 * k)},0", max(1.2, 2.4 * k),
               P.KITCHEN_KRAFT)


def moor(s: Strip, cleat: tuple[float, float], x: float, y: float, k: float, owner: str) -> None:
    """A mooring rope from a boat's cleat down to the bollard standing at (x, y) on the pier."""
    cx, cy = cleat
    way = 1 if x > cx else -1
    rope(s, (cx, cy), (x - way * 7 * k, y - 16 * k), max(1.6, 3 * k), y - 0.5, owner)


def rope(s: Strip, a: tuple[float, float], b: tuple[float, float], width: float, depth: float, owner: str) -> None:
    """A rope from a to b, sagging a little: it leaves each end a few degrees below the straight line."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    ang = math.atan2(dy, dx)
    sag = math.radians(7) * (1 if dx >= 0 else -1)
    connect(s, port(s, *a, math.cos(ang + sag), math.sin(ang + sag), owner),
            port(s, *b, -math.cos(ang - sag), -math.sin(ang - sag), owner), "cable", width, depth=depth,
            color=P.KITCHEN_KRAFT, lead=math.hypot(dx, dy) * 0.3, fits=(False, False))


def floats(c: Canvas, x0: float, x1: float, wl: float, k: float) -> None:
    """A harbour boom from x0 to x1 on the water at wl: steel floats half sunk, painted yellow on top, a lifting
    eye at each end, joined float to float by a heavy chain."""
    k *= 1.4
    step = 40 * k
    count = max(1, int((x1 - x0 + 6 * k) / step))
    pad = (x1 - x0 - count * step) / 2
    ends = []
    for q in range(count):
        fx = x0 + pad + step * (q + 0.5)
        d = Canvas()
        d.shape("M-16,0 V-6 Q-16,-11 -11,-11 H11 Q16,-11 16,-6 V0 Z", P.METAL, sw=1.4, light=(-1, -1))
        d.add(f'<path d="M-15,-7 Q-15,-10.4 -11,-10.4 H11 Q15,-10.4 15,-7 Z" fill="{P.YELLOW}"/>')
        d.line("M-10,-3.5 h2 M8,-3.5 h2", 1.4, P.METAL_DARK)
        for ex in (-16.5, 16.5):
            d.add(f'<circle cx="{ex}" cy="-5" r="1.8" fill="none" stroke="{P.METAL_DARK}" stroke-width="1.2"/>')
        d.line("M-18,0.5 q4,-2 8,0 q4,-2 8,0 q4,-2 8,0 q4,-2 8,0 q4,-2 8,0", 1.2, P.WHITE, 0.9)
        c.add(_at(d, fx, wl, k))
        ends.append((fx - 18 * k, fx + 18 * k))
    for (_, a), (b, _) in zip(ends, ends[1:], strict=False):          # the chain between them
        links = max(1, int((b - a) / (3.4 * k)))
        for q in range(links):
            lx = a + (q + 0.5) * (b - a) / links
            c.add(f'<ellipse cx="{n(lx)}" cy="{n(wl - 5 * k)}" rx="{n((2.2 if q % 2 else 1.2) * k)}" '
                  f'ry="{n((1.2 if q % 2 else 1.8) * k)}" fill="none" stroke="{P.METAL_DARK}" '
                  f'stroke-width="{n(max(0.6, 0.9 * k))}"/>')


def armour(c: Canvas, x: float, y: float, k: float, seed: int = 0) -> None:
    """An armour stone heaped at the foot of a breakwater: a big rounded boulder, its lit top and shaded
    underside."""
    rnd = random.Random(seed)
    stone = mix(P.STONE, P.WHITE, 0.15 + rnd.uniform(0, 0.15))
    w, h = rnd.uniform(15, 20), rnd.uniform(11, 14)
    d = Canvas()
    d.shape(f"M{n(-w)},0 Q{n(-w)},{n(-h * 0.9)} {n(-w * 0.3)},{n(-h)} Q{n(w * 0.4)},{n(-h * 1.1)} {n(w)},{n(-h * 0.4)} "
            f"Q{n(w * 1.05)},0 {n(w * 0.8)},2 H{n(-w * 0.8)} Z", stone, sw=1.4, light=None)
    d.add(f'<path d="M{n(-w * 0.6)},{n(-h * 0.7)} Q{n(-w * 0.1)},{n(-h * 0.95)} {n(w * 0.4)},{n(-h * 0.8)}" '
          f'fill="none" stroke="{P.WHITE}" stroke-width="2" stroke-opacity=".45" stroke-linecap="round"/>'
          f'<path d="M{n(-w * 0.8)},-1 H{n(w * 0.8)}" stroke="{INK}" stroke-width="3" stroke-opacity=".12"/>')
    c.add(_at(d, x, y, k))


def breakwater(c: Canvas, x: float, wl: float, k: float, w: float = 72, top: float = 44, side: int = 0) -> dict:
    """The head of a breakwater standing out of the water at (x, wl), `w` wide: a battered wall of stone blocks,
    its concrete cap, armour stones heaped at its foot - on both sides,
    or only on `side`. Returns its box and the top of its cap."""
    d = Canvas()
    half = w / 2
    body = f"M{-half},4 L{-half + 5},{-top} H{half - 5} L{half},4 Z"
    clip = d.shape(body, STONE_, sw=0, light=None, clip=True)
    rows = ""
    for row in range(int(top / 9) + 1):
        y_ = -top + row * 9
        rows += f'<path d="M{-half - 2},{n(y_)} H{half + 2}" stroke="{darken(STONE_, 0.75)}" stroke-width="1"/>'
        rows += "".join(f'<path d="M{n(-half + (row % 2) * 7 + q * 14)},{n(y_)} v9" stroke="{darken(STONE_, 0.75)}" '
                        f'stroke-width="1"/>' for q in range(int(w / 14) + 2))
    d.add(f'<g clip-path="url(#{clip})">{rows}<rect x="{-half}" y="{-top}" width="{w}" height="{top + 4}" '
          f'fill="{INK}" fill-opacity=".06"/></g>')
    d.path(body, "none", 1.8)
    d.shape(rounded_rect_d(-half + 3, -top - 6, w - 6, 7, 1.5), mix(P.STONE, P.WHITE, 0.35), sw=1.4, light=None)
    c.add(_at(d, x, wl, k))
    for sd in ((-1, 1) if side == 0 else (side,)):
        for q, (dx, dy) in enumerate(((2, 4), (24, 5), (12, -8))):
            armour(c, x + sd * (half + dx) * k, wl + dy * k, k, seed=q + (3 if sd > 0 else 0))
    reach = (half + 30) * k
    lo, hi = (x - reach if side <= 0 else x - half * k - 2), (x + reach if side >= 0 else x + half * k + 2)
    return {"box": (lo, wl - (top + 6) * k, hi, wl + 8 * k), "cap": wl - (top + 6) * k}


def mole(c: Canvas, head: float, wl: float, k: float, length: float = 170, way: int = -1, top: float = 42,
         stones: bool = True) -> dict:
    """A stone mole running out into the water and ending at x `head`, its body reaching `length` back towards
    `way`: courses of dressed stone blocks with a lit face, the round end of its head, the walkway on top with its
    railing, an iron ring on its face near the head for the boom's shackle; armour stones heaped at its foot and a
    wave breaking white against the head. Returns its box, the ring and the walkway's height."""
    d = Canvas()                                                    # drawn with the head at 0, the body to -x
    body = f"M{-length},4 V{-top} H-14 Q0,{-top} 2,{-top + 12} L4,4 Z"
    clip = d.shape(body, STONE_, sw=0, light=None, clip=True)
    rows = ""
    for row in range(int(top / 10) + 1):
        y_ = -top + row * 10
        rows += f'<path d="M{-length - 2},{y_} H8" stroke="{darken(STONE_, 0.72)}" stroke-width="1.1"/>'
        rows += "".join(f'<path d="M{n(-length + (row % 2) * 9 + q * 18)},{y_} v10" stroke="{darken(STONE_, 0.72)}" '
                        f'stroke-width="1.1"/>' for q in range(int(length / 18) + 2))
    d.add(f'<g clip-path="url(#{clip})">{rows}<rect x="-24" y="{-top}" width="30" height="{top + 4}" fill="{INK}" '
          f'fill-opacity=".1"/><rect x="{-length}" y="{-top}" width="{length + 8}" height="6" fill="{P.WHITE}" '
          f'fill-opacity=".25"/></g>')
    d.path(body, "none", 2)
    d.shape(f"M{-length},{-top - 6} H-12 Q-2,{-top - 6} 0,{-top} H{-length} Z", mix(P.STONE, P.WHITE, 0.35), sw=1.4,
            light=None)                                                                         # the walkway
    d.line(" ".join(f"M{q},{-top - 6} v-12" for q in range(-length + 10, -10, 22)) + f" M{-length + 10},{-top - 18} "
           f"H-12", 1.4, P.METAL_DARK)                                                          # its railing
    d.add(f'<circle cx="-14" cy="{-top + 16}" r="3.4" fill="none" stroke="{P.METAL_DARK}" stroke-width="1.8"/>')
    for q, dx in enumerate(range(-length + 16, -20, 34) if stones else ()):                   # armour stones
        armour(d, dx, 6, 0.8, seed=q + 11)
    d.add(f'<path d="M-6,2 Q2,-14 12,-22 Q8,-12 16,-14 Q14,-6 22,-4 Q12,0 8,4 Z" fill="{P.WHITE}" stroke="{INK}" '
          f'stroke-width="1.2"/>')                                                              # the breaking wave
    for q in range(4):
        d.add(f'<circle cx="{8 + q * 5}" cy="{-26 - (q % 2) * 5}" r="{2.2 - q * 0.3}" fill="{P.WHITE}" '
              f'stroke="{INK}" stroke-width=".8"/>')
    d.line(f"M{-length},1" + " q6,-3 12,0" * int(length / 12), 1.4, P.WHITE, 0.9)          # foam at its foot
    c.add(_at(d, head, wl, k, mirror=way > 0))
    lo, hi = sorted((head + way * (length + 2) * k, head - way * 30 * k))
    return {"box": (lo, wl - (top + 30) * k, hi, wl + 10 * k), "ring": (head + way * 14 * k, wl - (top - 16) * k),
            "walk": wl - (top + 6) * k}


def signal_mast(c: Canvas, x: float, foot: float, k: float, go: bool) -> tuple[float, float, float, float]:
    """The port's entry signal on its mast at (x, foot): a lattice mast with a ladder, and at its top the black
    panel of three lamps one over another, each under its hood - three red: no ship may enter; three green: come
    in. Returns its box."""
    d = Canvas()
    d.line("M-4,0 L-2,-74 M4,0 L2,-74", 1.8, P.METAL_DARK)
    d.line(" ".join(f"M{n(-4 + q * 0.27)},{n(-q * 10)} L{n(4 - q * 0.27)},{n(-q * 10 - 10)}" for q in range(7)), 1,
           P.METAL_DARK)
    d.shape(rounded_rect_d(-10, -116, 20, 44, 3), P.CHARCOAL, sw=1.6, light=None)
    lamp = P.GREEN if go else P.RED
    for q in range(3):
        ly = -108 + q * 13
        d.add(f'<circle cx="0" cy="{ly}" r="9" fill="{lamp}" fill-opacity=".25"/>'
              f'<circle cx="0" cy="{ly}" r="4.8" fill="{lighten(lamp, 0.25)}" stroke="{INK}" stroke-width="1"/>'
              f'<circle cx="-1.4" cy="{ly - 1.4}" r="1.4" fill="{P.WHITE}" fill-opacity=".8"/>')
        d.line(f"M-7,{ly - 4} Q0,{ly - 9} 7,{ly - 4}", 1.6, INK)                               # its hood
    c.add(_at(d, x, foot, k))
    return (x - 11 * k, foot - 118 * k, x + 11 * k, foot)


def container(c: Canvas, x: float, foot: float, k: float, open_: bool) -> dict:
    """A shipping container standing on the pier at (x, foot), 112 long and 60 high, seen from the side with its
    door end to the right: corrugated walls, corner castings, the doors with their locking bars and handles -
    closed, or swung open to show the cargo inside: sacks, a barrel, boxes with their battens. Returns its box
    and the door's edge."""
    d = Canvas()
    col = P.TEAL
    d.shape(rounded_rect_d(-56, -60, 112, 60, 2), col, sw=1.8, light=(-1, -1))
    d.line(" ".join(f"M{q},-56 V-4" for q in range(-50, 38, 6)), 1, darken(col, 0.7))
    for cx_, cy_ in ((-56, -60), (50, -60), (-56, -6), (50, -6)):                               # corner castings
        d.shape(rounded_rect_d(cx_, cy_, 6, 6, 1), darken(col, 0.6), sw=0.8, light=None)
    if open_:
        d.shape(rounded_rect_d(40, -56, 14, 52, 1), darken(col, 0.45), sw=1, light=None)       # the dark inside
        d.shape("M56,-58 L80,-62 V2 L56,-2 Z", lighten(col, 0.1), sw=1.6, light=None)          # the door, open
        d.line("M64,-58 V0 M72,-60 V1", 1.6, P.METAL_DARK)
        d.line("M62,-30 h5 M70,-30 h5", 2, P.METAL)
        edge = 80
    else:
        d.line("M40,-60 V0 M53,-60 V0", 1.4, INK, 0.7)
        d.line("M44,-56 V-4 M49,-56 V-4", 1.8, P.METAL_DARK)                                   # locking bars
        d.line("M42,-30 h5 M47,-26 h5", 2, P.METAL)
        edge = 56
    c.add(_at(d, x, foot, k))
    return {"box": (x - 56 * k, foot - 62 * k, x + (edge + 1) * k, foot), "door": (x + 46 * k, foot - 30 * k)}


def office(c: Canvas, x: float, foot: float, k: float, minutes: float) -> dict:
    """The harbour office on the pier at (x, foot), 170 wide and 236 tall: a brick building of two floors with a
    door and windows, its gable with a big round clock - twelve hour marks, the hands, and a green band round the
    rim from twenty to thirty minutes after the check began at 4:04 (`world_kit.CLOCK_TIME`), the minute hand
    `minutes` after it. Returns its box."""
    d = Canvas()
    brick = mix(P.TERRACOTTA, PLUM, 0.2)
    clip = d.shape("M-80,0 V-150 L0,-222 L80,-150 V0 Z", brick, sw=0, light=None, clip=True)
    rows = "".join(f'<path d="M-82,{-q * 8} H82" stroke="{darken(brick, 0.8)}" stroke-width=".8"/>'
                   for q in range(1, 28))
    d.add(f'<g clip-path="url(#{clip})">{rows}<rect x="20" y="-230" width="70" height="230" fill="{INK}" '
          f'fill-opacity=".08"/></g>')
    d.path("M-80,0 V-150 L0,-222 L80,-150 V0 Z", "none", 2.2)
    d.shape("M-90,-148 L0,-232 L90,-148 L84,-142 L0,-220 L-84,-142 Z", P.CHARCOAL, sw=1.6, light=None)  # roof edge
    d.shape(rounded_rect_d(-14, -60, 28, 60, 2), P.WOOD_DARK, sw=1.6, light=None)              # the door
    d.shape("M-20,-64 H20 L16,-72 H-16 Z", P.WHITE, sw=1.2, light=None)
    d.add(f'<circle cx="8" cy="-30" r="2" fill="{P.SUN}"/>')
    for wx, wy in ((-62, -64), (34, -64), (-62, -128), (-14, -128), (34, -128)):               # the windows
        d.shape(rounded_rect_d(wx, wy, 28, 34, 2), P.WHITE, sw=1.4, light=None)
        d.shape(rounded_rect_d(wx + 3, wy + 3, 22, 28, 1), P.LENS, sw=0.9, light=None)
        d.line(f"M{wx + 14},{wy + 3} V{wy + 31} M{wx + 3},{wy + 15} H{wx + 25}", 1.2, P.WHITE)
        d.shape(rounded_rect_d(wx - 2, wy + 34, 32, 4, 1), P.STONE, sw=1, light=None)
    cy = -176                                                                                  # the clock
    d.add(f'<circle cx="0" cy="{cy}" r="30" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="2"/>'
          f'<circle cx="0" cy="{cy}" r="25" fill="{P.WHITE}" stroke="{INK}" stroke-width="1.2"/>')
    h0, m0 = CLOCK_TIME                                   # the check starts at 4:04, as every clock in the book shows
    a0, a1 = math.radians((m0 + 20) * 6 - 90), math.radians((m0 + 30) * 6 - 90)
    d.add(f'<path d="M{n(math.cos(a0) * 22)},{n(cy + math.sin(a0) * 22)} A22,22 0 0 1 {n(math.cos(a1) * 22)},'
          f'{n(cy + math.sin(a1) * 22)}" fill="none" stroke="{P.GREEN}" stroke-width="5"/>')    # 20-30 minutes
    d.line(" ".join(f"M{n(math.cos(math.radians(q * 30)) * 19)},{n(cy + math.sin(math.radians(q * 30)) * 19)} "
                    f"L{n(math.cos(math.radians(q * 30)) * 24)},{n(cy + math.sin(math.radians(q * 30)) * 24)}"
                    for q in range(12)), 1.6, INK)
    d.add(clock_hands(0, cy, 12, 20, 2, INK, P.RED, time=(h0, m0 + round(minutes))))
    d.add(f'<circle cx="0" cy="{cy}" r="2.2" fill="{INK}"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 92 * k, foot - 234 * k, x + 92 * k, foot)}


def tower(c: Canvas, x: float, foot: float, k: float) -> dict:
    """The harbour master's tower on the pier at (x, foot), 140 wide and 314 tall: a stone plinth with the door
    under its canopy, two floors of white walls banded in plum with framed windows, on top the glazed control room
    overhanging on its brackets, a railing round its balcony, inside it the console with its lit screens; on its
    roof the radar on its mast, the whip antennas and the port's signal lamps, and beside the tower a wind sock on
    its pole. Returns its box."""
    d = Canvas()
    d.shape("M-54,0 V-46 H54 V0 Z", STONE_, sw=2, light=None)                                  # the plinth
    d.line("M-54,-23 H54 " + " ".join(f"M{q},-46 v23 M{q + 13},-23 v23" for q in range(-44, 50, 26)), 1,
           darken(STONE_, 0.75))
    d.shape("M-50,-46 V-200 H50 V-46 Z", P.WHITE, sw=2, light=(-2, -2))
    d.add(f'<rect x="18" y="-200" width="32" height="154" fill="{INK}" fill-opacity=".07"/>')
    for by in (-128, -200):                                                                   # plum bands
        d.shape(f"M-51,{by} H51 V{by + 8} H-51 Z", PLUM, sw=1.2, light=None)
    d.shape(rounded_rect_d(-14, -56, 28, 56, 2), PLUM, sw=1.6, light=None)                    # the door
    d.shape("M-22,-58 H22 L18,-66 H-18 Z", P.CHARCOAL, sw=1.2, light=None)                     # its canopy
    d.add(f'<circle cx="8" cy="-28" r="2" fill="{P.SUN}"/>')
    for wx, wy in ((-40, -112), (12, -112), (-40, -184), (12, -184)):
        d.shape(rounded_rect_d(wx - 2, wy - 2, 30, 36, 2), PLUM, sw=1.2, light=None)
        d.shape(rounded_rect_d(wx, wy, 26, 32, 1.5), P.LENS, sw=1, light=None)
        d.line(f"M{wx + 13},{wy} V{wy + 32} M{wx},{wy + 14} H{wx + 26}", 1.4, P.WHITE)
    d.shape(rounded_rect_d(-66, -206, 132, 8, 2), P.CHARCOAL, sw=1.4, light=None)              # the balcony
    d.line(" ".join(f"M{q},-206 v-12" for q in range(-62, 66, 10)) + " M-66,-218 H66", 1.3, P.METAL_DARK)
    d.line("M-48,-198 L-62,-206 M48,-198 L62,-206", 2.2, P.CHARCOAL)                          # its brackets
    d.shape("M-56,-218 L-60,-262 H60 L56,-218 Z", mix(P.LENS, P.SKY_LOW, 0.3), sw=2, light=None)  # glazing
    d.shape(rounded_rect_d(-44, -232, 88, 12, 2), P.CHARCOAL, sw=1, light=None)               # the console
    for q in range(4):
        d.shape(rounded_rect_d(-40 + q * 21, -244, 16, 10, 1.5), mix(P.GREEN, P.LENS, 0.5), sw=0.9, light=None)
    d.line("M-30,-218 L-31,-262 M0,-218 V-262 M30,-218 L31,-262", 2.4, PLUM)
    d.add(f'<path d="M-54,-222 L-57,-258 H-42 Z" fill="{P.WHITE}" fill-opacity=".35"/>')
    d.shape(rounded_rect_d(-66, -270, 132, 9, 2), PLUM, sw=1.6, light=None)                    # its roof
    d.line("M-20,-270 V-298 M36,-270 V-314 M50,-270 V-302", 1.6, P.METAL_DARK)                # mast, antennas
    d.shape(rounded_rect_d(-38, -302, 36, 5, 2), P.WHITE, sw=1.2, light=None)                  # the radar
    for q, col in enumerate((P.RED, P.WHITE, P.GREEN)):
        d.add(f'<circle cx="36" cy="{-314 + 7 + q * 7}" r="3" fill="{col}" stroke="{INK}" stroke-width=".8"/>')
    d.line("M70,0 V-150", 2, P.METAL_DARK)                                                   # the wind sock
    d.shape("M70,-150 L104,-144 L102,-134 L70,-136 Z", P.ORANGE, sw=1.2, light=None)
    d.line("M80,-148 L80,-136 M90,-146 L90,-135", 3, P.WHITE)
    c.add(_at(d, x, foot, k))
    return {"box": (x - 66 * k, foot - 316 * k, x + 106 * k, foot)}


def gate(c: Canvas, x: float, quay: float, base: float, k: float, out: int, open_: bool) -> None:
    """A lock's timber gate at x: its leaf of heavy planks with a diagonal brace and iron straps, a hand-rail along
    its top, its balance beam reaching out over the quay on the side `out` - or, open, the leaf folded back flat
    into its recess in the chamber wall, its beam swung round over it."""
    h = base - quay + 6 * k
    lo, hi = (x - 10 * k, x + 10 * k) if not open_ else sorted((x, x - out * 40 * k))
    c.add(f'<rect x="{n(lo)}" y="{n(quay - 6 * k)}" width="{n(hi - lo)}" height="{n(h)}" fill="{P.WOOD}" '
          f'stroke="{INK}" stroke-width="1.6"/>')
    c.line(" ".join(f"M{n(lo)},{n(quay - 6 * k + q * 8 * k)} H{n(hi)}" for q in range(1, int(h / (8 * k)))), 1,
           P.WOOD_DARK)                                                                         # its planks
    c.line(f"M{n(lo + 2 * k)},{n(base - 2 * k)} L{n(hi - 2 * k)},{n(quay)}", 3 * k, P.WOOD_DARK)  # the brace
    c.line(f"M{n(lo)},{n(quay - 2 * k)} H{n(hi)} M{n(lo)},{n(base - 6 * k)} H{n(hi)}", 2.4 * k, P.METAL_DARK)
    c.line(f"M{n(lo)},{n(quay - 6 * k)} v{n(-10 * k)} M{n(hi)},{n(quay - 6 * k)} v{n(-10 * k)} "
           f"M{n(lo)},{n(quay - 16 * k)} H{n(hi)}", 1.3, P.METAL_DARK)                          # its hand-rail
    if open_:
        bx0, bx1 = x - out * 4 * k, x - out * 44 * k
    else:
        bx0, bx1 = x, x + out * 44 * k
    c.add(f'<path d="M{n(bx0)},{n(quay - 9 * k)} L{n(bx1)},{n(quay - 13 * k)} L{n(bx1)},{n(quay - 8 * k)} '
          f'L{n(bx0)},{n(quay - 3 * k)} Z" fill="{P.WOOD_DARK}" stroke="{INK}" stroke-width="1.3"/>')  # beam


def lock(c: Canvas, x0: float, x1: float, wl: float, base: float, k: float, high: bool, lower_open: bool,
         upper_open: bool, inside=None) -> dict:
    """A lock between the open sea on the left and the inner harbour on the right, seen across from the pier: from
    the lower gate at x0 to the upper gate at x1 the long chamber with its far stone wall, its coping and bollards
    on the quay and a gauge board of the water's level; the water in it down at the sea's level or up at the
    harbour's (`high`), the harbour's water held up behind the upper gate, against a quay wall on the right. Each
    gate is a timber leaf with its brace and balance beam (`gate`), shut across the chamber or folded back into its
    recess. `inside(c, level)` draws what floats
    in the chamber, before the gates. Returns where things are."""
    up = wl - 30 * k                                                 # the inner harbour's level
    quay = wl - 52 * k
    right = x1 + 74 * k
    level = up if high else wl
    c.add(f'<rect x="{n(x0)}" y="{n(quay)}" width="{n(right - x0)}" height="{n(base - quay)}" fill="{STONE_}" '
          f'stroke="{INK}" stroke-width="1.6"/>')                                               # the far wall
    for row in range(int((base - quay) / (10 * k)) + 1):
        y_ = quay + row * 10 * k
        c.line(f"M{n(x0)},{n(y_)} H{n(right)}", 0.8, darken(STONE_, 0.78))
        c.line(" ".join(f"M{n(x0 + ((row % 2) * 9 + q * 18) * k)},{n(y_)} v{n(10 * k)}"
                        for q in range(int((right - x0) / (18 * k)) + 1)), 0.8, darken(STONE_, 0.78))
    c.add(f'<rect x="{n(x0 - 4 * k)}" y="{n(quay - 7 * k)}" width="{n(right - x0 + 8 * k)}" height="{n(7 * k)}" '
          f'fill="{mix(P.STONE, P.WHITE, 0.3)}" stroke="{INK}" stroke-width="1.3"/>')            # the coping
    bollard(c, right - 30 * k, quay - 7 * k, k * 0.55, rope=False)    # on the harbour's quay, clear of the chamber
    gx = x1 - 16 * k                                                 # the gauge board
    c.add(f'<rect x="{n(gx - 5 * k)}" y="{n(quay)}" width="{n(10 * k)}" height="{n(base - quay)}" fill="{P.WHITE}" '
          f'stroke="{INK}" stroke-width="1"/>')
    c.line(" ".join(f"M{n(gx - 5 * k)},{n(quay + q * 5 * k)} h{n((6 if q % 2 else 3) * k)}"
                    for q in range(1, int((base - quay) / (5 * k)))), 1, INK)
    for lx0, lx1, top in ((x0, x1, level), (x1, right, up)):        # the water in the chamber and the harbour
        c.add(f'<rect x="{n(lx0)}" y="{n(top)}" width="{n(lx1 - lx0)}" height="{n(base - top + 1)}" fill="{SEA}"/>')
        waves(c, lx0 + 4, lx1 - 4, top + 6 * k, k * 0.8, seed=int(lx0))
        c.line(f"M{n(lx0)},{n(top)} H{n(lx1)}", 1.2, P.WHITE, 0.8)
    c.add(f'<rect x="{n(right - 6 * k)}" y="{n(quay)}" width="{n(10 * k)}" height="{n(base - quay)}" '
          f'fill="{darken(STONE_, 0.85)}" stroke="{INK}" stroke-width="1.2"/>')                 # the end wall
    if inside:                                                       # what floats in the chamber
        inside(c, level)
    for gx_, open_, out in ((x0, lower_open, -1), (x1, upper_open, 1)):
        gate(c, gx_, quay, base, k, out, open_)
    return {"box": (x0 - 8 * k, quay - 16 * k, right + 6 * k, base), "level": level, "up": up}


# ============================================================================ what the cast holds
def mirror_pole(x: float, y: float, k: float) -> str:
    """An inspection mirror on a long pole: the pole through the fist and far down past the little finger, the
    round mirror at its end on a swivel, turned up to show the underside of the hull."""
    c = Canvas()
    c.line("M0,-6 V44", 1.8, P.METAL_DARK)
    c.add(f'<circle cx="0" cy="44" r="1.4" fill="{P.METAL}" stroke="{INK}" stroke-width=".5"/>')
    c.shape("M-6,47 A6,3.4 0 0 1 6,47 A6,3.4 0 0 1 -6,47 Z", P.LENS, sw=0.9, light=None)
    c.line("M-3,46.4 h3", 0.8, P.WHITE)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def torch(x: float, y: float, k: float) -> str:
    """A welding torch: its handle through the fist, the neck bending forward past the knuckles, the blue flame at
    its nozzle and a spray of sparks round it."""
    c = Canvas()
    c.shape(rounded_rect_d(-1.4, -4, 2.8, 10, 1), P.CHARCOAL, sw=0.5, light=None)
    c.line("M0,-4 Q0,-8 4,-9 L9,-9.5", 1.4, P.METAL)
    c.shape("M9,-10.6 L13.5,-9.5 L9,-8.4 Z", P.LENS, sw=0.3, light=None)
    for ang in range(-80, 81, 32):
        a = math.radians(ang)
        c.line(f"M{n(14 + math.cos(a) * 1.6)},{n(-9.5 + math.sin(a) * 1.6)} l{n(math.cos(a) * 3.4)},"
               f"{n(math.sin(a) * 3.4)}", 0.7, P.SUN)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def roller(x: float, y: float, k: float) -> str:
    """A paint roller: its handle through the fist, the wire frame bending forward, the roller wet with plum."""
    c = Canvas()
    c.shape(rounded_rect_d(-1.3, -3, 2.6, 9, 1), P.WOOD, sw=0.5, light=None)
    c.line("M0,-3 V-10 H6 V-12", 0.9, P.METAL_DARK)
    c.shape(rounded_rect_d(2, -16, 9, 4.4, 1.6), PLUM, sw=0.6, light=None)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def binoculars(x: float, y: float, k: float) -> str:
    """Binoculars held up by the bridge: two black barrels over the thumb, their eyepieces back towards the face."""
    c = Canvas()
    for bx in (-2.6, 2.6):
        c.shape(rounded_rect_d(bx - 2, -11, 4, 9, 1.4), P.CHARCOAL, sw=0.5, light=None)
        c.shape(rounded_rect_d(bx - 2.4, -12.4, 4.8, 2.4, 0.8), P.METAL_DARK, sw=0.4, light=None)
    c.shape(rounded_rect_d(-1, -8, 2, 4, 0.5), P.METAL, sw=0.3, light=None)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def radio(x: float, y: float, k: float) -> str:
    """A hand-held marine radio: the black body in the fist, its little screen and keypad, the stubby antenna."""
    c = Canvas()
    c.shape(rounded_rect_d(-2.4, -9, 4.8, 13, 1), P.CHARCOAL, sw=0.5, light=None)
    c.shape(rounded_rect_d(-1.6, -8, 3.2, 2.6, 0.4), P.LENS, sw=0.3, light=None)
    c.line("M-1,-13 V-9", 1.2, INK)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def paper_boat(c: Canvas, x: float, wl: float, k: float, crumpled: bool = False, way: int = 1) -> tuple:
    """A paper boat afloat at (x, wl), 44 long, its bow towards `way`: folded from one sheet - the hull's two
    pointed ends turned up, the tall triangular fold in the middle, the creases of the folds - a ripple at its
    waterline; `crumpled`: its bow bent back against what it ran into and a splash going up there. Returns its
    box."""
    d = Canvas()
    bow = "L16,-6 L22,-18 L12,-14" if not crumpled else "L14,-3 L17,-10 L10,-9"
    d.shape(f"M-22,-18 L-14,0 H12 {bow} L8,-12 L0,-30 L-8,-12 L-12,-14 Z", P.WHITE, sw=1.4, light=None)
    d.line("M-14,0 L-8,-12 M12,0 L8,-12 M0,-30 V-12 M-8,-12 H8", 1, INK, 0.45)                 # its creases
    d.add(f'<path d="M0,-30 L-8,-12 H0 Z" fill="{INK}" fill-opacity=".07"/>')
    d.line("M-20,1 q4,-2 8,0 q4,-2 8,0 q4,-2 8,0 q4,-2 8,0 q4,-2 8,0", 1.2, P.WHITE, 0.9)
    if crumpled:                                                     # the splash where it ran into the wall
        d.add(f'<path d="M14,0 Q18,-14 22,-20 Q22,-10 28,-14 Q24,-4 30,-2 Z" fill="{P.WHITE}" stroke="{INK}" '
              f'stroke-width="1"/>')
        for q in range(3):
            d.add(f'<circle cx="{22 + q * 4}" cy="{-22 - q * 3}" r="{1.8 - q * 0.4}" fill="{P.WHITE}" '
                  f'stroke="{INK}" stroke-width=".7"/>')
    c.add(_at(d, x, wl, k, mirror=way < 0))
    lo, hi = sorted((x - 23 * k * way, x + 31 * k * way))
    return (lo, wl - 31 * k, hi, wl + 2 * k)


# ============================================================================ the place behind every frame
def shore_unit(c: Canvas, kind: str, x0: float, x1: float, shore: float, room: float, k: float, seed: int) -> None:
    """One stretch of the far shore between x0 and x1 standing on `shore`, no taller than `room`: the beach with
    its dunes and beach huts, the harbour warehouses, a harbour crane, the lighthouse far off, a small town on its
    hill, boats moored along the quay - calmer than the station."""
    rnd = random.Random(seed)
    w, cx = x1 - x0, (x0 + x1) / 2
    if kind == "beach":
        c.add(f'<path d="M{n(x0)},{n(shore)} Q{n(x0 + w * 0.25)},{n(shore - 16 * k)} {n(cx)},{n(shore - 8 * k)} '
              f'T{n(x1)},{n(shore - 6 * k)} V{n(shore)} Z" fill="{calm(SAND)}" stroke="{calm(INK)}" stroke-width="1"/>')
        c.line(" ".join(f"M{n(x0 + w * f)},{n(shore - 4 * k)} q{n(6 * k)},{n(-2 * k)} {n(12 * k)},0"
                        for f in (0.15, 0.4, 0.7)), 1, calm(darken(SAND, 0.8)))            # its ripples
        for q in range(2):                                                                  # beach huts
            hx = x0 + w * (0.3 + q * 0.38)
            hh = min(30 * k, room * 0.5)
            col = (PLUM, P.TEAL)[q]
            c.add(f'<rect x="{n(hx - 10 * k)}" y="{n(shore - 10 * k - hh)}" width="{n(20 * k)}" height="{n(hh)}" '
                  f'fill="{calm(P.WHITE)}" stroke="{calm(INK)}" stroke-width="1"/>')
            c.line(" ".join(f"M{n(hx - 10 * k + d * 5 * k)},{n(shore - 10 * k - hh)} v{n(hh)}" for d in (1, 3)),
                   3 * k, calm(col))
            c.add(f'<path d="M{n(hx - 13 * k)},{n(shore - 10 * k - hh)} L{n(hx)},{n(shore - 18 * k - hh)} '
                  f'L{n(hx + 13 * k)},{n(shore - 10 * k - hh)} Z" fill="{calm(col)}" stroke="{calm(INK)}" '
                  f'stroke-width="1"/>')
    elif kind == "sheds":
        for q in range(2):
            hx = x0 + w * (0.28 + q * 0.44)
            hw, hh = 48 * k, min(42 * k, room * 0.7)
            c.add(f'<rect x="{n(hx - hw / 2)}" y="{n(shore - hh)}" width="{n(hw)}" height="{n(hh)}" '
                  f'fill="{calm(PLUM if q else mix(PLUM, P.CARD, 0.4))}" stroke="{calm(INK)}" stroke-width="1"/>'
                  f'<path d="M{n(hx - hw / 2 - 4 * k)},{n(shore - hh)} L{n(hx)},{n(shore - hh - 14 * k)} '
                  f'L{n(hx + hw / 2 + 4 * k)},{n(shore - hh)} Z" fill="{calm(darken(PLUM, 0.7))}" '
                  f'stroke="{calm(INK)}" stroke-width="1"/><rect x="{n(hx - 9 * k)}" y="{n(shore - hh * 0.6)}" '
                  f'width="{n(18 * k)}" height="{n(hh * 0.6)}" fill="{calm(P.WOOD_DARK)}"/>')
    elif kind == "crane" and room > 50 * k:
        ch = min(90 * k, room * 0.92)
        c.line(f"M{n(cx - 12 * k)},{n(shore)} L{n(cx)},{n(shore - ch)} L{n(cx + 12 * k)},{n(shore)} "
               f"M{n(cx - 8 * k)},{n(shore - ch * 0.4)} H{n(cx + 8 * k)}", 2.4, calm(P.ORANGE))
        c.line(f"M{n(cx - 20 * k)},{n(shore - ch)} H{n(cx + 50 * k)} M{n(cx + 44 * k)},{n(shore - ch)} "
               f"V{n(shore - ch * 0.45)}", 2.2, calm(P.ORANGE))
        c.add(f'<rect x="{n(cx + 38 * k)}" y="{n(shore - ch * 0.45)}" width="{n(12 * k)}" height="{n(8 * k)}" '
              f'fill="{calm(P.TEAL)}" stroke="{calm(INK)}" stroke-width=".8"/>')
    elif kind == "light" and room > 40 * k:
        lh = min(80 * k, room * 0.9)
        c.add(f'<path d="M{n(cx - 8 * k)},{n(shore)} L{n(cx - 5 * k)},{n(shore - lh)} H{n(cx + 5 * k)} '
              f'L{n(cx + 8 * k)},{n(shore)} Z" fill="{calm(P.WHITE)}" stroke="{calm(INK)}" stroke-width="1"/>')
        for q in range(3):
            c.add(f'<rect x="{n(cx - 7 * k)}" y="{n(shore - lh * (0.25 + q * 0.27))}" width="{n(14 * k)}" '
                  f'height="{n(lh * 0.11)}" fill="{calm(PLUM)}"/>')
        c.add(f'<rect x="{n(cx - 5 * k)}" y="{n(shore - lh - 8 * k)}" width="{n(10 * k)}" height="{n(8 * k)}" '
              f'fill="{P.SUN}" stroke="{calm(INK)}" stroke-width=".8"/>')
        c.add(f'<path d="M{n(cx - 20 * k)},{n(shore)} Q{n(cx)},{n(shore - 14 * k)} {n(cx + 22 * k)},{n(shore)} Z" '
              f'fill="{calm(STONE_)}" stroke="{calm(INK)}" stroke-width="1"/>')
    elif kind == "town":
        c.add(f'<path d="M{n(x0)},{n(shore)} Q{n(cx)},{n(shore - min(40 * k, room * 0.6))} {n(x1)},{n(shore)} Z" '
              f'fill="{calm(P.HILL_NEAR)}"/>')
        for q in range(4):
            hx = x0 + w * (0.2 + q * 0.2)
            hh = 14 * k + rnd.uniform(0, 8) * k
            hy = shore - min(40 * k, room * 0.6) * (1 - abs(hx - cx) / (w / 2)) * 0.8
            c.add(f'<rect x="{n(hx - 7 * k)}" y="{n(hy - hh)}" width="{n(14 * k)}" height="{n(hh)}" '
                  f'fill="{calm(P.CARD)}" stroke="{calm(INK)}" stroke-width=".8"/><path d="M{n(hx - 9 * k)},'
                  f'{n(hy - hh)} L{n(hx)},{n(hy - hh - 8 * k)} L{n(hx + 9 * k)},{n(hy - hh)} Z" '
                  f'fill="{calm(P.TERRACOTTA)}"/>')
    elif kind == "boats":
        for q in range(2):
            boat(c, x0 + w * (0.3 + q * 0.4), shore + 1, k * 0.3, None, hull=calm(PLUM if q else P.TEAL), smoke=None,
                 water=calm(SEA))


def ground(c: Canvas, kind: str, x0: float, x1: float, top: float, foot: float, k: float) -> None:
    """The far shore's ground under a stretch of it: sand under the beach, grass under the town, rocks under the
    lighthouse, the stone quay with its coping under the rest."""
    h = foot - top
    if kind == "beach":
        c.add(f'<rect x="{n(x0)}" y="{n(top)}" width="{n(x1 - x0)}" height="{n(h + 1)}" fill="{calm(SAND)}"/>')
        c.line(f"M{n(x0)},{n(top + h * 0.55)} q{n((x1 - x0) / 4)},{n(-2 * k)} {n((x1 - x0) / 2)},0 "
               f"t{n((x1 - x0) / 2)},0", 1, calm(darken(SAND, 0.82)))
    elif kind == "town":
        c.add(f'<rect x="{n(x0)}" y="{n(top)}" width="{n(x1 - x0)}" height="{n(h + 1)}" fill="{calm(P.HILL_NEAR)}"/>')
    elif kind == "light":
        c.add(f'<rect x="{n(x0)}" y="{n(top)}" width="{n(x1 - x0)}" height="{n(h + 1)}" fill="{calm(STONE_)}"/>')
        for q in range(int((x1 - x0) / (16 * k))):
            c.add(f'<ellipse cx="{n(x0 + 8 * k + q * 16 * k)}" cy="{n(top + h * 0.5)}" rx="{n(7 * k)}" '
                  f'ry="{n(h * 0.35)}" fill="{calm(darken(STONE_, 0.85))}"/>')
    else:
        c.add(f'<rect x="{n(x0)}" y="{n(top)}" width="{n(x1 - x0)}" height="{n(h + 1)}" fill="{calm(P.STONE)}"/>'
              f'<rect x="{n(x0)}" y="{n(top)}" width="{n(x1 - x0)}" height="{n(max(1.5, h * 0.25))}" '
              f'fill="{calm(darken(P.STONE, 0.85))}"/>')
        c.line(" ".join(f"M{n(x0 + q * 14 * k)},{n(top + h * 0.25)} V{n(foot)}"
                        for q in range(1, int((x1 - x0) / (14 * k)) + 1)), 0.7, calm(darken(P.STONE, 0.75)))


def backdrop(s: Strip, index: int) -> None:
    """The harbour behind a station: the evening sky, plum at the top and warm low down, a gull or two; a strip of
    the far sea; the far shore, turning from frame to frame and calmer than the station - the beach with dunes and
    beach huts, warehouses, a crane, the lighthouse far off, a small town on its hill, boats along the quay; then
    the narrow near water with its foam at the pier, and the plank pier underfoot."""
    s.decor = False
    s.dress = False
    s.indoor = False
    ledger(s)
    zoom(s)
    feet = lane(s).feet                                                # the cast leaves the stations room:
    widest = max(_box(s, name, 0, feet)[2] - _box(s, name, 0, feet)[0]
                 for name in ("professor", "cat", "agent", "caterpillar"))
    s.tall *= min(1.0, (s.hi - s.lo) * 0.19 / widest)                  # two of them take two fifths at most
    s.unit = s.tall / 137
    c = s.back
    base = s.base
    k = max(0.6, min(1.4, base / 240))
    near = max(18.0, base * 0.17)                                       # the near water: narrow
    shore = base - near
    land = shore - max(6.0, base * 0.05)                                # the far shore's ground
    horizon = land - max(8.0, base * 0.07)
    sets.sky(c, SKY_TOP, SKY_LOW, horizon, W)
    rnd = random.Random(index * 13 + 2)
    for _ in range(2 if s.h >= 200 else 1):                            # a couple of gulls
        gx, gy = rnd.uniform(0.2, 0.9) * W, horizon * rnd.uniform(0.2, 0.5)
        c.line(f"M{n(gx - 8 * k)},{n(gy)} q{n(4 * k)},{n(-5 * k)} {n(8 * k)},0 q{n(4 * k)},{n(-5 * k)} {n(8 * k)},0",
               max(1.0, 1.6 * k), calm(INK))
    sea(c, -6, W + 6, horizon, land + 2, k * 0.5, seed=index + 40)   # the far sea
    kinds = ("beach", "sheds", "beach", "town", "sheds")              # low: nothing rises behind a station
    x = -40 * k * ((index * 0.7) % 1)
    i = index * 3
    while x < W:
        kind = kinds[i % len(kinds)]
        w = {"crane": 90, "light": 70, "boats": 120, "town": 160}.get(kind, 150) * k
        ground(c, kind, x, x + w, land, shore, k)
        shore_unit(c, kind, x, x + w, land, land - 4, k, seed=index * 31 + i)
        x += w
        i += 1
    c.add(f'<rect x="-6" y="{n(shore)}" width="{W + 12}" height="{n(base - shore + 2)}" fill="{SEA}"/>')
    c.add(f'<rect x="-6" y="{n(shore + (base - shore) * 0.5)}" width="{W + 12}" height="{n((base - shore) * 0.5 + 2)}" '
          f'fill="{SEA_DEEP}" fill-opacity=".4"/>')
    waves(c, -6, W + 6, shore + (base - shore) * 0.35, k * 0.8, seed=index)
    waves(c, -6, W + 6, base - 4, k, seed=index + 1)                   # foam at the pier
    s.wl = base - near * 0.5                                           # where a boat at the pier floats
    s.land, s.shore = land, shore                                      # the far quay, and the near water's top
    planks(c, -6, W + 6, base, s.h + 4, max(0.8, s.unit))


# ============================================================================ framing a station
def _framed(draw):
    """A station drawn as it is or mirrored, by turns; on the next visit of the same moment the onlooker changes,
    the station swaps sides and the camera comes a step nearer."""
    def run(s: Strip, beat: str) -> None:
        s.again = (s.seed // 2) % 2 == 1
        s.mirror = bool(s.shot) != s.again
        s.near = 1.12 if s.again else 1.0
        draw(s, beat)
    return run


def in_hand(s: Strip, who, u: float, v: float) -> tuple[float, float]:
    """Where the point (u, v) of a thing held in a character's right fist lands on the page (the grip frame of
    `handheld`: +u along the forearm, -v the thumb's side, in the holder's hundredths)."""
    gx, gy, ang = s.grip(who, "right")
    a = math.radians(ang)
    k = (who.bottom - who.top) / 100
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = (math.sin(a), -math.cos(a)) if who.flip else (-math.sin(a), math.cos(a))   # a flipped hand is mirrored
    return gx + (u * ux + v * vx) * k, gy + (u * uy + v * vy) * k


def fx(s: Strip, x: float) -> float:
    """Where a point of a station drawn the canonical way round lands on the page: mirrored about the middle of
    the frame's usable width on a mirrored page."""
    return s.lo + s.hi - x if getattr(s, "mirror", False) else x


def place(s: Strip, c: Canvas, box: tuple, name: str, depth: float | None = None) -> tuple:
    """Put a station drawn the canonical way round onto the page (mirrored when the page is); returns its box in
    page space."""
    svg = c.render()
    if getattr(s, "mirror", False):
        svg = f'<g transform="translate({n(s.lo + s.hi)},0) scale(-1,1)">{svg}</g>'
        box = (fx(s, box[2]), box[1], fx(s, box[0]), box[3])
    s.put(lane(s).feet - 1 if depth is None else depth, svg, box, name, group=name)
    return box


def other(s: Strip, name: str, alt: str) -> str:
    """`name`, or on a second visit of the moment `alt`; the caterpillar for the professor in a mid strip."""
    name = alt if getattr(s, "again", False) else name
    return "caterpillar" if name == "professor" and mid(s) else name


def room(s: Strip) -> float:
    """How wide a station may be and still leave room on either side of it for the widest of its onlookers."""
    feet = lane(s).feet
    widest = max(_box(s, name, 0, feet)[2] - _box(s, name, 0, feet)[0]
                 for name in ("professor", "cat", "agent", "caterpillar"))
    return s.hi - s.lo - 2 * widest - 30


def water_k(s: Strip, width: float, share: float = 0.6, tall: float = 110) -> float:
    """The scale of a station out on the water: `tall` over the waterline as the frame lets it be, its `width`
    within `share` of the frame and leaving its cast room, a step nearer on the next visit if there is room."""
    fit = min(room(s), (s.hi - s.lo) * share * getattr(s, "near", 1.0))
    return max(0.25, min((s.wl - 4) / tall, fit / width))


def middle(s: Strip, width: float, k: float, at: float = 0.5) -> float:
    """The left end of a station `width` wide (at scale k) standing round `at` of the frame, inside it."""
    x = s.x(at) - width * k / 2
    return min(max(x, s.lo + 4), s.hi - 4 - width * k)


def true_size(s: Strip, height: float, width: float) -> float | None:
    """The scale at which a building `height` tall and `width` wide stands on the pier at its true size - two and a
    half times as tall as the agent - or None when the frame is too low or too narrow to show it so."""
    feet = lane(s).feet
    agent = _box(s, "agent", 0, feet)
    k = (agent[3] - agent[1]) * 2.5 / height
    return k if height * k <= feet - 8 and width * k <= room(s) else None


def across(s: Strip, c: Canvas) -> None:
    """Put something drawn the canonical way round across the water on the far quay, behind the near water
    (mirrored on a mirrored page)."""
    svg = c.render()
    if getattr(s, "mirror", False):
        svg = f'<g transform="translate({n(s.lo + s.hi)},0) scale(-1,1)">{svg}</g>'
    s.put(0.5, svg, None)                                              # over the veil the sky melts away under


def far_k(s: Strip, height: float, width: float, tall: float = 1.3) -> float:
    """The scale of a building on the far quay: `tall` times the agent on the pier at most - it is far off, but
    still clearly taller than the warehouses round it - and no taller than the sky over the quay allows, no wider
    than a third of the frame."""
    agent = _box(s, "agent", 0, lane(s).feet)
    return min((s.land - 6) / height, (agent[3] - agent[1]) * tall / height, (s.hi - s.lo) * 0.34 / width)


def flank(s: Strip, box: tuple, cast: tuple[tuple, ...]) -> None:
    """The station's cast beside its box: (name, side, pose, mood, hold) each, side -1 left of it, 1 right,
    facing it."""
    for name, side, pose, mood, hold in cast:
        stand(s, name, beside(s, box, side, name), pose, mood, flip=side > 0, hold=hold)


# ============================================================================ the stations
def entrance_station(s: Strip, beat: str) -> None:
    """Only what passed every check goes into main: the harbour entrance at the end of a stone mole, the port's
    entry signal on the lantern mast at its head, the boom of steel floats shackled to its ring. "wait": three red
    lamps, the boom across the entrance, a boat flying red waits outside it; "open": three green, the boom swung
    back and lying along the mole, a boat flying green comes in with its bow wave."""
    go = beat == "open"
    width = 520
    k = water_k(s, width, 0.74, 136)
    x0 = middle(s, width, k)
    wl = s.wl
    c = Canvas()
    head = x0 + 150 * k
    ml = mole(c, head, wl, k, length=146, top=42, stones=not go)
    sig = signal_mast(c, head - 16 * k, ml["walk"], k * 0.8, go)
    rx, _ = ml["ring"]
    if go:
        floats(c, x0 + 2 * k, rx + 4 * k, wl + 8 * k, k)               # swung back, lying along the mole's foot
        bt = boat(c, head + 160 * k, wl, k, P.GREEN, way=-1, moving=True, name=s.word("boat_haiku"))
    else:
        floats(c, rx + 2 * k, head + 130 * k, wl, k * 0.9)
        bt = boat(c, head + 250 * k, wl, k, P.RED, way=-1, name=s.word("boat_haiku"))
    box = (x0, min(sig[1], bt["box"][1], ml["box"][1]), max(bt["box"][2], head + 132 * k), wl + 20 * k)
    box = place(s, c, box, "entrance", s.wl + 20)
    if go:
        flank(s, box, (("cat", -1, "wave", "smile", None),
                       (other(s, "caterpillar", "agent"), 1, "present", "smile", handheld.clipboard)))
    else:
        flank(s, box, (("agent", -1, "point", "smile", None),
                       (other(s, "cat", "professor"), 1, "think", "smile", None)))


def inspection_station(s: Strip, beat: str) -> None:
    """What to check in CI: the inspection berth. The boat moored at the pier, its ropes to two bollards. "papers":
    the cat on the pier at its bow line, checking its papers on his clipboard. "cargo": a
    container set on the pier with its doors swung open on the cargo, the agent beside it; the caterpillar with a
    mirror on a long pole looks under the hull."""
    r = lane(s)
    width = 420 if beat == "cargo" else 300
    k = water_k(s, width, 0.56 if beat == "cargo" else 0.62, 112)
    x0 = middle(s, width, k, 0.55)
    c = Canvas()
    bx = x0 + 160 * k if beat == "papers" else x0 + 140 * k
    bt = boat(c, bx, s.wl, k, P.RED, way=1, name=s.word("boat_sonnet"))
    pk = min(s.unit, k * 0.9)
    edge = s.base + 6 * max(0.8, s.unit)                              # on the pier's edge beam
    stern_b, bow_b = bx - 128 * k, bx + 126 * k
    for x_ in (stern_b, bow_b):
        bollard(c, x_, edge, pk, rope=False)
    items = [bt["box"], (stern_b - 11 * pk, edge - 25 * pk, bow_b + 11 * pk, edge)]
    if beat == "cargo":
        ck = min(ph(s) * 0.8 / 62, (r.feet - 6) / 62, k * 0.9)
        cx_ = x0 + 290 * k + 56 * ck
        ct = container(c, cx_, r.feet, ck, open_=True)
        items.append(ct["box"])
    box = (min(b[0] for b in items), min(b[1] for b in items), max(b[2] for b in items), r.feet)
    box = place(s, c, box, "inspection")
    if beat == "cargo":                                               # the cargo inside the open container
        left = cx_ + 40 * ck if not s.mirror else fx(s, cx_ + 54 * ck)
        pen = Pen(s, left, r.feet - 56 * ck, ck)
        hold = pen.container("hold", 0, 0, 14, 52, darken(P.TEAL, 0.45), radius=1, sw=1, light=None)
        pad = pen.pad(14, 52)
        low = 52 - pad
        pen.c.add(f'<rect x="{n(pad)}" y="{n(low - 16)}" width="{n(14 - 2 * pad)}" height="16" fill="{P.WOOD}" '
                  f'stroke="{INK}" stroke-width="1"/>')                              # a crate
        pen.child(hold, "crate", pad, low - 16, 14 - pad, low)
        gap = max(4.0, 3.6 / ck)
        sack_low = low - 16 - gap
        sack_top = sack_low - 14
        pen.c.add(f'<path d="M{n(pad)},{n(sack_low)} V{n(sack_top + 5)} Q7,{n(sack_top - 2)} {n(14 - pad)},'
                  f'{n(sack_top + 5)} V{n(sack_low)} Z" fill="{mix(P.SAND, P.WOOD, 0.4)}" stroke="{INK}" '
                  f'stroke-width="1"/>')                                             # a sack on the rack
        pen.child(hold, "sack", pad, sack_top - 2, 14 - pad, sack_low)
        pen.c.add(f'<rect x="0" y="{n(sack_low)}" width="14" height="{n(min(2.4, gap * 0.5))}" fill="{P.WOOD_DARK}"/>')
        s.put(r.feet - 0.9, pen.svg(), None, group="inspection")
    moor(s, (fx(s, bt["stern"][0]), bt["stern"][1]), fx(s, stern_b), edge, pk, "inspection")
    moor(s, (fx(s, bt["bow"][0]), bt["bow"][1]), fx(s, bow_b), edge, pk, "inspection")
    left, right = (-1, 1) if not s.mirror else (1, -1)
    if beat == "papers":                                              # the cat at the bow line
        flank(s, box, (("cat", right, "present", "smile", handheld.clipboard),
                       (other(s, "agent", "professor"), left, "think", "smile", None)))
    else:
        flank(s, box, (("agent", right, "point", "smile", None),
                       (other(s, "caterpillar", "cat"), left, "present", "worry", mirror_pole)))
        # the golden floppy (an easter egg, `world_kit.hide`): taken out of the container and set on the pier for
        # the inspection, by its open doors
        stash_along(s, [fx(s, cx_ + 64 * ck + 16 + q * 5) for q in range(10)], r.feet - 2, r.feet - 0.5,
                    group="inspection") or \
            stash_along(s, [fx(s, cx_ + q * 10 * ck) for q in (2, 1, 3, 0)], r.feet + 5, r.feet + 5,
                        group="inspection")                   # or set down in front of the container


def lock_station(s: Strip, beat: str) -> None:
    """The merge queue: a lock between the sea and the inner harbour. "queue": the lower gate open, the chamber
    down at the sea's level, one boat going in while the next waits its turn; "check": the lower gate shut, the
    chamber filled to the harbour's level, the boat in it raised, the upper gate open - the next still waits."""
    if s.h < 200:
        lock_far(s, beat)
        return
    width = 610
    k = water_k(s, width, 0.72, 140)
    x0 = middle(s, width, k)
    c = Canvas()
    queue_x = x0 + 90 * k
    gate0 = x0 + 226 * k
    gate1 = gate0 + 300 * k
    check = beat == "check"
    boat(c, queue_x, s.wl, k * 0.74, None, way=1)                     # the next, waiting its turn
    lk = lock(c, gate0, gate1, s.wl, s.base, k, high=check, lower_open=not check, upper_open=check,
              inside=lambda cc, level: boat(cc, (gate0 + gate1) / 2 + 10 * k, level, k * 0.78, None, way=1,
                                            moving=not check, water=SEA))
    box = (x0, s.wl - 128 * k, lk["box"][2], s.base)
    box = place(s, c, box, "lock", s.wl + 20)
    if check:
        flank(s, box, (("cat", -1, "point", "smile", None),
                       (other(s, "caterpillar", "agent"), 1, "think", "worry", None)))
    else:
        flank(s, box, (("agent", -1, "point", "smile", None),
                       (other(s, "professor", "cat"), 1, "think", "smile", None)))


def lock_far(s: Strip, beat: str) -> None:
    """The merge queue in a low strip: the lock across the water on the far quay, a boat in its chamber, and at
    the near pier the next boat waiting its turn."""
    check = beat == "check"
    k = water_k(s, 560, 0.66, 110)
    x0 = middle(s, 560, k, 0.48)
    c = Canvas()
    boat(c, x0 + 124 * k, s.wl, k, None, way=1)
    far = Canvas()
    fk = min((s.land - 6) / 150, 300 * k / 380)
    gx = x0 + 270 * k
    lock(far, gx, gx + 300 * fk, s.land + 2, s.shore, fk, high=check, lower_open=not check, upper_open=check,
         inside=lambda cc, level: boat(cc, gx + 150 * fk, level, fk * 0.78, None, way=1, smoke=None))
    across(s, far)
    box = place(s, c, (x0, s.wl - 106 * k, max(x0 + 250 * k, gx + 380 * fk), s.wl + 18 * k), "queue", s.wl + 20)
    if check:
        flank(s, box, (("cat", -1, "point", "smile", None),
                       (other(s, "caterpillar", "agent"), 1, "think", "worry", None)))
    else:
        flank(s, box, (("agent", -1, "point", "smile", None),
                       (other(s, "professor", "cat"), 1, "think", "smile", None)))


def clock_station(s: Strip, beat: str) -> None:
    """Every check in twenty to thirty minutes: the harbour office with the big clock on its gable, a green band
    on its dial from twenty to thirty minutes after the start. "start": 4:04, the cat starts his stopwatch;
    "done": 4:29, twenty-five minutes on, inside the band - the cat shows his stopwatch. In a frame too low for the
    office at its true size it stands across the water on the far quay, and the cast watch its clock from the
    pier."""
    r = lane(s)
    minutes = 25 if beat == "done" else 0
    ok = true_size(s, 250, 184)
    x = s.x(0.5)
    c = Canvas()
    if ok:
        box = place(s, c, office(c, x, r.feet, ok, minutes)["box"], "office")
    else:
        fk = far_k(s, 250, 184)
        of = office(c, x, s.land, fk, minutes)
        across(s, c)
        c = Canvas()
        lo, top, hi, _ = of["box"]
        box = place(s, Canvas(), (lo, top, hi, r.feet), "office")      # the view across kept clear
    mate = other(s, "agent", "caterpillar") if beat == "start" else other(s, "professor", "agent")
    flank(s, box, (("cat", 1, "present", "smile", handheld.stopwatch),
                   (mate, -1, "point" if beat == "start" else "think", "smile", None)))


def fix_station(s: Strip, beat: str) -> None:
    """The agent brings its pull request to green itself: its boat hauled out ashore on the boatyard's stone quay,
    on keel blocks, held by shores, a ladder up its bow. "weld": a red flag on the staff, the agent beside the bow
    welding a plate over the hole, sparks flying; "green": the plate painted over, the green flag up, the agent
    with its paint roller."""
    r = lane(s)
    k = scale_for(s, 140, 300, 0.56, 1.2)
    x = s.x(0.46)
    y0 = r.feet - 36 * k                                              # the boat's waterline, up on the blocks
    c = Canvas()
    yard0, yard1 = x - 150 * k, x + 140 * k                           # the boatyard's quay over the near water
    c.add(f'<rect x="{n(yard0)}" y="{n(s.shore - 2)}" width="{n(yard1 - yard0)}" height="{n(s.base - s.shore + 4)}" '
          f'fill="{mix(P.STONE, P.WHITE, 0.2)}" stroke="{INK}" stroke-width="1.4"/>')
    c.line(" ".join(f"M{n(yard0 + q * 26 * k)},{n(s.shore + 4)} V{n(s.base)}"
                    for q in range(1, int((yard1 - yard0) / (26 * k)) + 1)), 1, darken(P.STONE, 0.75))
    c.add(f'<rect x="{n(yard0)}" y="{n(s.shore - 2)}" width="{n(yard1 - yard0)}" height="6" '
          f'fill="{darken(P.STONE, 0.8)}"/>')                                                     # its coping
    for bxk in (-62, -14, 34):                                        # the keel blocks
        c.add(f'<rect x="{n(x + (bxk - 9) * k)}" y="{n(r.feet - 14 * k)}" width="{n(18 * k)}" height="{n(14 * k)}" '
              f'fill="{P.WOOD_DARK}" stroke="{INK}" stroke-width="1"/>')
        c.line(f"M{n(x + (bxk - 9) * k)},{n(r.feet - 7 * k)} h{n(18 * k)}", 1, INK, 0.6)
    c.line(f"M{n(x - 120 * k)},{n(r.feet)} L{n(x - 80 * k)},{n(y0 + 6 * k)}", 4 * k, P.WOOD)   # the shores
    c.line(f"M{n(x + 20 * k)},{n(r.feet)} L{n(x + 30 * k)},{n(y0 + 14 * k)}", 4 * k, P.WOOD)
    boat(c, x, y0, k, P.GREEN if beat == "green" else P.RED, way=1, dry=True, cargo=False, smoke=None,
         patch="painted" if beat == "green" else "plate", name=s.word("boat_opus"))
    lx0, lx1 = x + 40 * k, x + 50 * k                                 # the ladder, up the bow
    c.line(f"M{n(lx0 - 12 * k)},{n(r.feet)} L{n(lx0)},{n(y0 - 36 * k)} M{n(lx1 - 12 * k)},{n(r.feet)} "
           f"L{n(lx1)},{n(y0 - 36 * k)}", 2.4 * k, P.METAL_DARK)
    for q in range(1, 7):
        t_ = q / 7
        c.line(f"M{n(lx0 - 12 * k * (1 - t_))},{n(r.feet + (y0 - 36 * k - r.feet) * t_)} h{n(10 * k)}", 2 * k,
               P.METAL_DARK)
    if beat == "weld":                                                # the sparks off the plate
        px, py = x + 92 * k, y0 - 14 * k
        c.line(" ".join(f"M{n(px + math.cos(math.radians(a)) * 4 * k)},{n(py + math.sin(math.radians(a)) * 4 * k)} "
                        f"l{n(math.cos(math.radians(a)) * 9 * k)},{n(math.sin(math.radians(a)) * 9 * k)}"
                        for a in range(-80, 81, 32)), max(1.0, 1.4 * k), P.SUN)
    box = (x - 126 * k, y0 - 106 * k, x + 106 * k, r.feet)
    box = place(s, c, box, "dock")
    side = 1 if not s.mirror else -1
    stand(s, "agent", beside(s, box, side, "agent", gap=0), "present", "smile" if beat == "green" else "worry",
          flip=side > 0, hold=torch if beat == "weld" else roller)
    mate = other(s, "caterpillar" if beat == "weld" else "cat", "professor")
    stand(s, mate, beside(s, box, -side, mate), "think" if beat == "weld" else "present",
          "worry" if beat == "weld" else "smile", flip=side < 0)


def flaky_station(s: Strip, beat: str) -> None:
    """Tests that pass one time and fail the next: a boat moved to a quarantine berth of its own between two
    mooring dolphins out in the water, the yellow Q flag on its staff. "stall": its engine dies - a puff of black
    smoke - the agent shrugs, the cat writes it down; "run": it starts this time, grey smoke and the water
    churning at its stern - the agent cheers, the caterpillar does not trust it."""
    width = 400
    k = water_k(s, width, 0.66, 112)
    x0 = middle(s, width, k)
    c = Canvas()
    bx = x0 + 200 * k
    stall = beat == "stall"
    dolphins = (x0 + 26 * k, x0 + 374 * k)
    tops = []
    for dx in dolphins:                                               # a dolphin: three piles under one cap
        for px in (-9, 0, 9):
            c.add(f'<rect x="{n(dx + (px - 4) * k)}" y="{n(s.wl - 40 * k)}" width="{n(8 * k)}" height="{n(44 * k)}" '
                  f'fill="{P.WOOD_DARK}" stroke="{INK}" stroke-width="1"/>')
        c.add(f'<rect x="{n(dx - 16 * k)}" y="{n(s.wl - 46 * k)}" width="{n(32 * k)}" height="{n(8 * k)}" '
              f'fill="{P.WOOD}" stroke="{INK}" stroke-width="1.2"/>')
        c.line(f"M{n(dx - 14 * k)},{n(s.wl - 2 * k)} H{n(dx + 14 * k)}", 2, P.LEAF_DARK)
        bollard(c, dx, s.wl - 46 * k, k * 0.5, rope=True)
        tops.append((dx, s.wl - 52 * k))
    bt = boat(c, bx, s.wl, k, P.YELLOW, way=1, smoke="black" if stall else "grey",
              name=s.word("boat_sonnet"))
    if not stall:                                                     # the water churning at its stern
        sx0 = bx - 100 * k
        c.add(f'<path d="M{n(sx0)},{n(s.wl)} q{n(-8 * k)},{n(-7 * k)} {n(-16 * k)},{n(-3 * k)} q{n(-6 * k)},'
              f'{n(-6 * k)} {n(-14 * k)},0 q{n(4 * k)},{n(5 * k)} {n(-2 * k)},{n(6 * k)} Z" fill="{P.WHITE}" '
              f'stroke="{INK}" stroke-width="1"/>')
    box = (x0, bt["box"][1], x0 + width * k, s.wl + 18 * k)
    box = place(s, c, box, "quarantine", s.wl + 20)
    for cleat, (dx, dy) in ((bt["stern"], tops[0]), (bt["bow"], tops[1])):
        rope(s, (fx(s, cleat[0]), cleat[1]), (fx(s, dx), dy), max(1.4, 2.4 * k), lane(s).feet - 0.5, "quarantine")
    if stall:
        flank(s, box, (("agent", -1, "shrug", "worry", None),
                       (other(s, "cat", "professor"), 1, "present", "smile", handheld.clipboard)))
    else:
        flank(s, box, (("agent", -1, "cheer", "smile", None),
                       (other(s, "caterpillar", "cat"), 1, "think", "worry", None)))


def owners_station(s: Strip, beat: str) -> None:
    """Who owns CI: the harbour master's tower with its glazed control room, radar and the port's lamps.
    "watch": the professor (the cat in a mid strip) keeps watch on it with binoculars; "radio": he talks on the
    harbour radio, the cat with the log on his clipboard. In a frame too low for the tower at its true size it
    stands across the water on the far quay, clearly over the warehouses round it, and the cast watch it from the
    pier."""
    r = lane(s)
    tk = true_size(s, 316, 172)
    c = Canvas()
    if tk:
        box = place(s, c, tower(c, s.x(0.46), r.feet, tk)["box"], "tower")
    else:
        far = Canvas()
        tw = tower(far, s.x(0.46), s.land, far_k(s, 316, 172, tall=2.4))
        across(s, far)
        lo, top, hi, _ = tw["box"]
        box = place(s, c, (lo, top, hi, r.feet), "tower")             # the view across kept clear
    lead_ = "cat" if mid(s) else "professor"
    if beat == "watch":
        flank(s, box, ((lead_, -1, "present", "smile", binoculars),
                       (other(s, "agent", "caterpillar"), 1, "point", "smile", None)))
    else:
        flank(s, box, ((lead_, -1, "present", "talk", radio),
                       ("cat" if lead_ != "cat" else "agent", 1, "present", "smile", handheld.clipboard)))


BIRD = 0.55     # the sparrow in flight next to the cast: a bird's size beside them, as he perches in the other worlds


def bypass_station(s: Strip, beat: str) -> None:
    """Checking that the checks cannot be got round: the boom's end shackled to the ring on the face of the stone
    mole - a wall as high as the cat over the water, its walkway on top - and no gap between them. "sneak": a small
    paper boat drifts along the boom for the corner, the sparrow flying just behind it, pushing it with a wing;
    "bump": the paper boat crumpled against the mole's head, a splash going up, the sparrow hovering, astonished,
    the cat laughing."""
    feet = lane(s).feet
    cat = _box(s, "cat", 0, feet)
    bird = _box(s, "sparrow", 0, feet, BIRD)
    bw, bh = bird[2] - bird[0], bird[3] - bird[1]
    width = 420
    k = water_k(s, width, 0.66, 70)
    mk = min((cat[3] - cat[1]) / 42, (s.wl - 6) / 74, k * 1.6)          # the mole as high as the cat
    x0 = middle(s, width, k)
    c = Canvas()
    head = x0 + 116 * mk
    ml = mole(c, head, s.wl, mk, length=110, top=42)
    rx, ry = ml["ring"]
    bump = beat == "bump"
    end = x0 + width * k
    floats(c, rx + 8 * k, end, s.wl, k * 0.8)
    pk = bw * 0.9 / 54                                                # the paper boat about the sparrow's length
    px_ = head + 26 * pk if bump else min(end - 30 * pk, head + (end - head) * 0.62)
    pb = paper_boat(c, px_, s.wl + 3 * k, pk, crumpled=bump, way=-1)
    fly_x = px_ + (36 * pk if not bump else 40 * pk)                  # just above and behind it
    fly_top = pb[1] - bh * 0.7
    box = (min(x0, ml["box"][0]), min(ml["box"][1], fly_top), max(end, fly_x + bw / 2), s.wl + 10 * k)
    box = place(s, c, box, "boomend", s.wl + 20)
    s.actor("sparrow", fx(s, fly_x), pb[1] + bh * 0.3, "fly", "surprise" if bump else "smile", flip=not s.mirror,
            tall=s.tall * SIZE["sparrow"] * BIRD, group="boomend", depth=s.wl + 21)
    if bump:
        flank(s, box, (("cat", 1, "cheer", "smile", None),
                       (other(s, "agent", "caterpillar"), -1, "point", "smile", None)))
    else:
        flank(s, box, (("cat", 1, "think", "smile", None),
                       (other(s, "caterpillar", "professor"), -1, "think", "worry", None)))


# ============================================================================ the finale
BAYS = ("entrance", "inspection", "lock", "clock", "fix", "flaky", "owners", "bypass")
QUAY = ("clock", "owners")                               # the buildings, on the far quay
AFLOAT = ("entrance", "lock", "flaky", "bypass")         # out on the inner water
ASHORE = ("inspection", "fix")                           # on the pier, in front


def finale(s: Strip) -> None:
    """The whole harbour at once, seen a little from above, in three depths: on the far quay the harbour office
    with its clock, the harbour master's tower and the lighthouse, true to their size over the water; on the inner
    water the entrance at the mole's end with its signal and boom and a boat going in under green, the lock with a
    boat rising in it, the quarantine berth with its boat under the yellow Q flag, the boom shackled to the mole; on
    the pier in front the opened container and the agent's boat on its blocks under green - each station's name on
    a plaque right over it; the cast on the pier, all at one scale, the professor at the start."""
    s.decor = False
    s.dress = False
    ledger(s)
    zoom(s)
    backdrop(s, 2)
    r = lane(s)
    left, right = s.lo, s.hi
    span_ = right - left
    named = s.h >= 300
    size = 11.0 if named else 9.0
    th = tag_size("Ag", size)[1]
    widest = max(tag_size(s.word(key), size)[0] for key in BAYS)
    if widest > span_ * 0.2:
        size = max(sets.LETTERING_MIN + 1, size * span_ * 0.2 / widest)
        th = tag_size("Ag", size)[1]
    label = th + 10 if named else 4
    feet = r.feet
    quay = feet * 0.36                                                 # the far quay's edge
    fl = feet * 0.68                                                   # the inner water's row
    k0 = max(0.5, s.unit)
    c0 = s.back
    c0.add(f'<rect x="-6" y="{n(quay - 8 * k0)}" width="{W + 12}" height="{n(10 * k0)}" fill="{calm(P.STONE)}"/>')
    sea(c0, -6, W + 6, quay + 2, s.wl + 2, k0 * 0.8, seed=9)
    planks(c0, -6, W + 6, s.base, s.h + 4, max(0.8, s.unit))
    things = Canvas()
    quay_c = Canvas()
    pen = Pen(s, 0, 0, 1)
    rooms = {"quay": quay - 8 * k0 - 4 - label, "water": fl - quay - 6 - label, "pier": feet - fl - 8 - label}
    xs = {"clock": 0.28, "owners": 0.6, "entrance": 0.12, "lock": 0.37, "flaky": 0.63, "bypass": 0.88,
          "inspection": 0.22, "fix": 0.56}
    lk_ = min(rooms["quay"] / 584, span_ * 0.1 / 308)                  # the lighthouse on the far quay, right
    lighthouse(quay_c, left + span_ * 0.9, quay - 8 * k0 + 4 * lk_, lk_, beam=False)
    tops = {}
    for key in BAYS:
        x = left + span_ * xs[key]
        layer = "quay" if key in QUAY else "water" if key in AFLOAT else "pier"
        floor = {"quay": quay - 8 * k0, "water": fl, "pier": feet}[layer]
        room = rooms[layer]
        fit = span_ * 0.23
        if key == "entrance":
            k = min(fit / 300, room / 100)
            ml = mole(things, x - 50 * k, floor, k, length=80, top=40)
            signal_mast(things, x - 66 * k, ml["walk"], k * 0.5, True)
            boat(things, x + 106 * k, floor, k * 0.62, P.GREEN, way=-1, moving=True)
            h = 98 * k
        elif key == "lock":
            k = min(fit / 400, room / 110)
            lock(things, x - 150 * k, x + 150 * k, floor, floor + 26 * k, k, True, False, True,
                 inside=lambda cc, level, x_=x, k_=k: boat(cc, x_, level, k_ * 0.72, None, smoke=None))
            h = 106 * k
        elif key == "flaky":
            k = min(fit / 250, room / 110)
            boat(things, x, floor, k, P.YELLOW, smoke="black")
            h = 106 * k
        elif key == "bypass":
            k = min(fit / 260, room / 72)
            ml = mole(things, x - 20 * k, floor, k, length=110, top=40)
            floats(things, ml["ring"][0] + 8 * k, x + 120 * k, floor, k * 0.8)
            h = 72 * k
        elif key == "inspection":                                     # at the scale of the boat on its blocks
            k = min(fit / 240, rooms["pier"] / 142) * 0.9
            container(things, x - 10 * k, floor, k, True)
            h = 62 * k
        elif key == "fix":
            k = min(fit / 240, room / 142)
            boat(things, x, floor - 36 * k, k, P.GREEN, dry=True, cargo=False, smoke=None, patch="painted")
            for bxk in (-62, -14, 34):
                things.add(f'<rect x="{n(x + (bxk - 9) * k)}" y="{n(floor - 14 * k)}" width="{n(18 * k)}" '
                           f'height="{n(14 * k)}" fill="{P.WOOD_DARK}" stroke="{INK}" stroke-width="1"/>')
            h = 142 * k
        elif key == "clock":
            k = min(fit / 184, room / 236)
            office(quay_c, x, floor, k, 25)
            h = 234 * k
        else:
            k = min(fit / 172, room / 316)
            tower(quay_c, x, floor, k)
            h = 316 * k
        tops[key] = (x, floor - h)
    s.put(0.5, quay_c.render(), None)
    s.put(1.2, things.render(), None)
    if named:
        for key, (x, top) in tops.items():
            holder = pen.tag(f"label{key}", x, top - 6 - th / 2, s.word(key), size, mix(PLUM, P.CARD, 0.5), INK)
            s.put(2, "", holder.outer, f"label{key}")
    cast_ = (("professor", "think", 0.04), ("cat", "present", 0.38), ("agent", "point", 0.75),
             ("caterpillar", "present", 0.88))
    room_h = rooms["pier"] + label - 6
    scale = min(min(s.tall * 1.2, _fit_tall(name, span_ * 0.1, room_h) / SIZE[name]) for name, _, _ in cast_)
    for i, (name, pose, fx_) in enumerate(cast_):
        who = s.actor(name, min(left + span_ * fx_, s.hi - 24), feet, pose, "smile", flip=True,
                      tall=scale * SIZE[name], group=f"f{i}")
        if name == "cat":
            held(s, who, handheld.stopwatch)
        elif name == "caterpillar":
            held(s, who, handheld.clipboard)
    if named:
        s.put(2, pen.svg(), None)


# ============================================================================ the opener
def lighthouse(c: Canvas, x: float, foot: float, k: float, beam: bool = True) -> dict:
    """The hero: a tall lighthouse on its rocks at (x, foot), 160 wide and 560 tall - the rocks heaped at its foot
    with foam on them, the tapering tower in plum and white bands with its windows and door, the gallery with its
    railing, the lamp room glazed and lit, its domed roof and vane, and the beam swinging out of it - two cones of
    light and motion arcs. Returns its parts."""
    d = Canvas()
    d.add(f'<path d="M-130,0 Q-120,-50 -80,-60 Q-60,-90 -20,-80 Q20,-100 50,-76 Q100,-80 120,-40 Q140,-20 140,0 Z" '
          f'fill="{STONE_}" stroke="{INK}" stroke-width="2.2"/>')                           # the rocks
    d.add(f'<path d="M-100,-40 q20,-12 40,0 M10,-60 q18,-10 34,4 M70,-40 q14,-8 28,4" fill="none" '
          f'stroke="{darken(STONE_, 0.75)}" stroke-width="2"/>')
    for fx, fy in ((-120, -8), (-60, -4), (40, -6), (110, -10)):                        # foam on them
        d.add(f'<path d="M{fx - 18},{fy} q9,-12 18,-2 q9,-12 18,0 q6,6 -6,8 H{fx - 14} Z" fill="{P.WHITE}" '
              f'stroke="{INK}" stroke-width="1"/>')
    for fx, side in ((-128, -1), (134, 1)):                                                   # waves breaking
        d.add(f'<path d="M{fx},-6 q{side * 4},-30 {side * 22},-40 q{side * -6},14 {side * 4},18 q{side * 6},-16 '
              f'{side * 20},-12 q{side * -10},10 {side * -4},34 Z" fill="{P.WHITE}" stroke="{INK}" '
              f'stroke-width="1.4"/>')
        for q in range(3):
            d.add(f'<circle cx="{fx + side * (14 + q * 10)}" cy="{-58 - q * 8}" r="{3 - q * 0.6}" fill="{P.WHITE}" '
                  f'stroke="{INK}" stroke-width=".8"/>')
    tower = "M-50,-70 L-32,-460 H32 L50,-70 Z"
    clip = d.shape(tower, P.WHITE, sw=0, light=None, clip=True)
    d.add(f'<g clip-path="url(#{clip})">' + "".join(
        f'<rect x="-60" y="{-130 - q * 110}" width="120" height="55" fill="{PLUM}"/>' for q in range(4)) +
        f'<rect x="0" y="-470" width="60" height="410" fill="{INK}" fill-opacity=".1"/></g>')   # bands, its shade
    d.path(tower, "none", 2.4)
    d.shape("M-62,-60 H62 L58,-96 H-58 Z", P.STONE, sw=2.0, light=(-2, -2))                # the stone plinth
    d.line(" ".join(f"M{px},-60 V-96" for px in (-36, -10, 16, 42)) + " M-60,-78 H60", 1.2, darken(P.STONE, 0.7))
    d.shape("M-22,-96 V-140 Q0,-160 22,-140 V-96 Z", P.WOOD_DARK, sw=1.8, light=None)          # its door
    d.line("M-22,-118 H22 M0,-96 V-150", 1.2, INK, 0.5)
    d.add(f'<circle cx="14" cy="-116" r="2.4" fill="{P.SUN}"/>')
    d.shape("M-30,-96 H30 V-90 H-30 Z", darken(P.STONE, 0.8), sw=1.2, light=None)              # its step
    for wy in (-230, -330, -420):                                                             # windows, framed
        d.shape(rounded_rect_d(-10, wy - 2, 20, 26, 8), P.WHITE, sw=1.4, light=None)
        d.shape(rounded_rect_d(-7, wy, 14, 20, 6), P.SUN, sw=1.2, light=None)
        d.line(f"M0,{wy} V{wy + 20} M-7,{wy + 9} H7", 1, INK, 0.6)
    d.shape(rounded_rect_d(-50, -470, 100, 12, 3), darken(PLUM, 0.7), sw=1.8, light=None)      # the gallery
    d.line(" ".join(f"M{px},-470 V-492" for px in range(-46, 50, 10)) + " M-48,-492 H48", 2, INK)
    d.shape(rounded_rect_d(-28, -530, 56, 60, 4), P.YELLOW_PALE, sw=2, light=None)            # the lamp room
    glow(d, 0, -500, 16)
    for q in range(3):                                                                        # the lens's prisms
        d.add(f'<ellipse cx="0" cy="-500" rx="{14 - q * 4}" ry="{20 - q * 5}" fill="none" stroke="{P.SUN}" '
              f'stroke-width="2"/>')
    d.add(f'<ellipse cx="0" cy="-500" rx="15" ry="22" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    d.line("M-28,-500 H-16 M16,-500 H28 M-10,-530 V-522 M10,-530 V-522 M-10,-478 V-470 M10,-478 V-470", 2, INK, 0.8)
    d.shape("M-36,-530 Q0,-570 36,-530 Z", darken(PLUM, 0.7), sw=1.8, light=None)              # its dome
    d.line("M0,-560 V-582 M-8,-576 H8", 2.4, INK)
    if beam:
        d.add(f'<path d="M24,-508 L330,-560 V-430 Z" fill="{P.YELLOW_PALE}" fill-opacity=".35"/>'
              f'<path d="M-24,-508 L-240,-470 V-530 Z" fill="{P.YELLOW_PALE}" fill-opacity=".2"/>')
        d.add(f'<path d="M-40,-560 A48,40 0 0 1 40,-560" fill="none" stroke="{INK}" stroke-width="2" '
              f'stroke-opacity=".5"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 150 * k, foot - 584 * k, x + 158 * k, foot), "tower": (x - 50 * k, x + 50 * k),
            "top": foot - 584 * k}


def cloud(c: Canvas, x: float, y: float, w: float) -> None:
    """A long dusk cloud centred at (x, y), `w` wide: plum-grey above, lit pink and orange from below by the sun
    gone down."""
    h = w * 0.22
    top = mix(PLUM, P.CARD, 0.45)
    c.add(f'<path d="M{n(x - w / 2)},{n(y)} Q{n(x - w * 0.42)},{n(y - h)} {n(x - w * 0.22)},{n(y - h * 0.8)} '
          f'Q{n(x - w * 0.1)},{n(y - h * 1.7)} {n(x + w * 0.08)},{n(y - h)} Q{n(x + w * 0.26)},{n(y - h * 1.4)} '
          f'{n(x + w * 0.34)},{n(y - h * 0.6)} Q{n(x + w * 0.5)},{n(y - h * 0.4)} {n(x + w / 2)},{n(y)} Z" '
          f'fill="{top}"/>')
    c.add(f'<path d="M{n(x - w * 0.46)},{n(y)} Q{n(x)},{n(y + h * 0.5)} {n(x + w * 0.48)},{n(y)} '
          f'Q{n(x)},{n(y - h * 0.3)} {n(x - w * 0.46)},{n(y)} Z" fill="{mix(P.PINK, P.ORANGE, 0.5)}"/>')
    c.line(f"M{n(x - w * 0.4)},{n(y + h * 0.05)} Q{n(x)},{n(y + h * 0.35)} {n(x + w * 0.4)},{n(y + h * 0.05)}",
           2, P.YELLOW_PALE, 0.8)


def far_shore(c: Canvas, x0: float, x1: float, horizon: float) -> None:
    """The far shore on the horizon between x0 and x1: two soft hills, the sun going down behind them, a small
    town at their foot - white houses, red roofs, a church spire, lit windows."""
    w = x1 - x0
    c.add(f'<path d="M{n(x0)},{n(horizon)} Q{n(x0 + w * 0.2)},{n(horizon - 50)} {n(x0 + w * 0.42)},{n(horizon - 22)} '
          f'Q{n(x0 + w * 0.62)},{n(horizon - 64)} {n(x1)},{n(horizon)} Z" fill="{mix(P.HILL_NEAR, PLUM, 0.35)}" '
          f'stroke="{INK}" stroke-width="1.2"/>')
    rnd = random.Random(5)
    for q in range(9):
        hx = x0 + 18 + q * (w - 36) / 8
        hh = rnd.uniform(14, 24)
        c.add(f'<rect x="{n(hx - 9)}" y="{n(horizon - hh)}" width="18" height="{n(hh)}" fill="{P.CARD}" '
              f'stroke="{INK}" stroke-width="1"/><path d="M{n(hx - 11)},{n(horizon - hh)} L{n(hx)},'
              f'{n(horizon - hh - 9)} L{n(hx + 11)},{n(horizon - hh)} Z" fill="{P.TERRACOTTA}" stroke="{INK}" '
              f'stroke-width="1"/><rect x="{n(hx - 3)}" y="{n(horizon - hh + 5)}" width="6" height="5" '
              f'fill="{P.SUN}"/>')
        if q == 4:                                                                            # the church spire
            c.add(f'<path d="M{n(hx - 6)},{n(horizon - hh - 6)} L{n(hx)},{n(horizon - hh - 40)} L{n(hx + 6)},'
                  f'{n(horizon - hh - 6)} Z" fill="{P.CARD}" stroke="{INK}" stroke-width="1"/>')


def flagstaff(c: Canvas, x: float, foot: float, top: float, raised: float, flag: str) -> dict:
    """A flagstaff on the pier at x from its foot plate up to `top`: the white pole, the gilded truck with its
    pulley, the halyard down from the pulley in two lines to the cleat on the pole; on the near line a cloth flag
    with its folds, hoisted `raised` of the way up and flying out in the wind. Returns its box and where the free
    line of the halyard leaves the pole."""
    c.add(f'<rect x="{n(x - 16)}" y="{n(foot - 6)}" width="32" height="6" rx="2" fill="{P.CHARCOAL}" stroke="{INK}" '
          f'stroke-width="1.4"/>')
    c.add(f'<path d="M{n(x - 5)},{n(foot - 6)} L{n(x - 3)},{n(top)} H{n(x + 3)} L{n(x + 5)},{n(foot - 6)} Z" '
          f'fill="{P.WHITE}" stroke="{INK}" stroke-width="1.6"/>')
    c.add(f'<circle cx="{n(x)}" cy="{n(top - 6)}" r="6" fill="{P.SUN}" stroke="{INK}" stroke-width="1.4"/>')
    cleat_y = foot - 70
    c.add(f'<rect x="{n(x + 4)}" y="{n(cleat_y - 3)}" width="10" height="6" rx="2" fill="{P.METAL_DARK}" '
          f'stroke="{INK}" stroke-width="1"/>')
    hoist = foot - 90 - (foot - 90 - top - 20) * raised            # where the flag's lower edge is
    fh, fw = 46.0, 74.0
    c.line(f"M{n(x + 5)},{n(top - 2)} V{n(cleat_y)} H{n(x + 9)}", 1.4, P.KITCHEN_KRAFT)         # the near line
    d = Canvas()
    d.shape(f"M0,0 C{n(fw * 0.25)},-8 {n(fw * 0.5)},8 {n(fw * 0.75)},-2 Q{n(fw * 0.9)},-6 {n(fw)},0 "
            f"L{n(fw + 2)},{n(fh)} Q{n(fw * 0.88)},{n(fh - 6)} {n(fw * 0.75)},{n(fh - 2)} C{n(fw * 0.5)},{n(fh + 8)} "
            f"{n(fw * 0.25)},{n(fh - 8)} 0,{n(fh)} Z", flag, sw=1.8, light=None)
    d.line(f"M{n(fw * 0.32)},2 C{n(fw * 0.36)},{n(fh * 0.4)} {n(fw * 0.3)},{n(fh * 0.7)} {n(fw * 0.34)},{n(fh - 3)} "
           f"M{n(fw * 0.7)},0 C{n(fw * 0.74)},{n(fh * 0.4)} {n(fw * 0.68)},{n(fh * 0.7)} {n(fw * 0.72)},{n(fh)}",
           3, darken(flag, 0.72), 0.6)                                                          # its folds
    d.add(f'<circle cx="0" cy="2" r="2" fill="{P.METAL}" stroke="{INK}" stroke-width=".8"/>'
          f'<circle cx="0" cy="{n(fh - 2)}" r="2" fill="{P.METAL}" stroke="{INK}" stroke-width=".8"/>')
    c.add(_at(d, x + 6, hoist - fh, 1))
    return {"box": (x - 16, top - 12, x + 16, foot), "flag": (x + 4, hoist - fh - 4, x + 6 + fw + 4, hoist + 6),
            "free": (x - 3, top + 2)}


def sun_path(c: Canvas, x: float, top: float, bottom: float) -> None:
    """The setting sun's path on the sea under it: short strokes of gold, wide near the horizon, narrowing and
    thinning towards the front."""
    rnd = random.Random(12)
    y = top + 5
    while y < bottom:
        t = (y - top) / (bottom - top)
        w = (70 - 50 * t) * rnd.uniform(0.6, 1.1)
        off = rnd.uniform(-14, 14) * (1 - t)
        c.add(f'<rect x="{n(x + off - w / 2)}" y="{n(y)}" width="{n(w)}" height="{n(3.4 - 1.8 * t)}" rx="1.5" '
              f'fill="{P.SUN}" fill-opacity="{n(0.75 - 0.5 * t)}"/>')
        y += 7 + 9 * t


def opener(st: Stage, accent: str):
    """The harbour at dusk, one hero: the tall lighthouse on its rocks, striped plum and white, its lamp room lit
    and its beam swinging out over the sea; stars over it, long clouds lit from below; the sun going down behind
    the hills and the little town on the far shore, its path of gold on the sea; the sea darkening towards us.
    The harbour entrance: a breakwater head with the port's entry signal lit green, the boom of steel floats from
    it opened for a boat flying green that goes in with its bow wave, while one flying red waits out beyond it.
    In front the plank pier: the professor under his bubble, the agent hoisting a green flag up the flagstaff by
    its halyard, the caterpillar holding on to a bollard, afraid of the water, the cat timing with his stopwatch,
    the sparrow on a bollard by the professor."""
    ledger(st)
    c = st.back
    horizon, pier = 724.0, 950.0
    sets.sky(c, SKY_TOP, SKY_LOW, horizon, W)
    rnd = random.Random(8)
    for _ in range(26):                                                                       # the first stars
        sx_, sy_ = rnd.uniform(700, 830), rnd.uniform(16, 230)
        r_ = rnd.uniform(1.2, 2.6)
        c.add(f'<path d="M{n(sx_)},{n(sy_ - r_ * 2)} L{n(sx_ + r_ * 0.5)},{n(sy_ - r_ * 0.5)} L{n(sx_ + r_ * 2)},'
              f'{n(sy_)} L{n(sx_ + r_ * 0.5)},{n(sy_ + r_ * 0.5)} L{n(sx_)},{n(sy_ + r_ * 2)} L{n(sx_ - r_ * 0.5)},'
              f'{n(sy_ + r_ * 0.5)} L{n(sx_ - r_ * 2)},{n(sy_)} L{n(sx_ - r_ * 0.5)},{n(sy_ - r_ * 0.5)} Z" '
              f'fill="{P.YELLOW_PALE}" fill-opacity=".85"/>')
    for cx_, cy_, w_ in ((380, 300, 150), (560, 350, 190), (420, 420, 130), (620, 452, 110)):   # dusk clouds
        cloud(c, cx_, cy_, w_)
    c.add(f'<circle cx="450" cy="{horizon - 8}" r="52" fill="{P.SUN}" fill-opacity=".9"/>')   # the setting sun
    far_shore(c, 330, 590, horizon)
    sea(c, -6, W + 6, horizon, pier, 1.6, seed=4)
    c.add(f'<rect x="-6" y="{n(horizon + (pier - horizon) * 0.55)}" width="{W + 12}" '
          f'height="{n((pier - horizon) * 0.45)}" fill="{SEA_DEEP}" fill-opacity=".35"/>')      # deeper in front
    sun_path(c, 450, horizon, pier - 30)
    for gx, gy in ((420, 300), (470, 340), (300, 360)):                                       # gulls
        c.line(f"M{gx - 14},{gy} q7,-9 14,0 q7,-9 14,0", 3, INK)
    parts = lighthouse(c, 700, horizon + 120, 0.98)
    st.put(0.5, "", parts["box"], "lighthouse", group="lighthouse", backdrop=True)
    st.keep_clear(parts["box"])
    for q in range(5):                                                # its light's reflection on the water
        c.add(f'<rect x="{n(722 - q * 3)}" y="{n(horizon + 128 + q * 10)}" width="{n(26 - q * 4)}" height="2.6" '
              f'rx="1.3" fill="{P.YELLOW_PALE}" fill-opacity="{n(0.6 - q * 0.1)}"/>')
    wl_boom = horizon + 76
    bw = breakwater(c, 288, wl_boom, 0.7, w=54, top=40, side=-1)
    signal_mast(c, 288, bw["cap"], 0.5, True)
    floats(c, 308, 352, wl_boom, 0.5)                                 # the boom, its gate swung away
    boat(c, 410, horizon + 30, 0.42, P.RED, way=-1)                                    # waiting outside, far off
    boat(c, 452, horizon + 140, 0.7, P.GREEN, way=-1, moving=True)                     # coming in
    planks(c, -6, W + 6, pier, H + 4, 1.8)
    prof = st.actor("professor", 140, 1100, "explain", "talk", tall=360)
    st.speaker(prof, width=74, left=8, air=CLEAR_MM)
    st.keep_clear((-6, horizon - 2, W + 6, horizon + 2), (-6, pier - 4, W + 6, pier + 14))
    fs = flagstaff(c, 446, 1096, 880, 0.25, P.GREEN)
    st.put(1100, "", fs["box"], "flagstaff", group="agent")
    st.put(1100, "", fs["flag"], "flag", group="agent")
    agent = st.actor("agent", 372, 1112, "present", "smile", flip=False, tall=330, group="agent")
    gx, gy, _ = st.grip(agent, "right")
    c.line(f"M{n(fs['free'][0])},{n(fs['free'][1])} L{n(gx)},{n(gy)}", 1.6, P.KITCHEN_KRAFT)    # the free line
    caterp = st.actor("caterpillar", 610, 1106, "present", "worry", flip=True, tall=270, group="caterpillar")
    hx_, hy_, _ = st.grip(caterp, "right")                                                # her hand on a bollard
    bk_ = (1106 - hy_) / 24
    bollard(c, hx_, 1106, bk_)
    st.put(1100, "", (hx_ - 11 * bk_, hy_ - 2, hx_ + 11 * bk_, 1106), "bollard", group="caterpillar")
    cat = st.actor("cat", 752, 1132, "present", "smile", flip=True, tall=270, group="cat")
    st.hold(cat, handheld.stopwatch)
    bollard(c, 262, 990, 1.5)
    st.put(0.6, "", (247, 954, 277, 990), "post", group="post")
    st.actor("sparrow", 262, 954, "point", "smile", tall=96, group="post")
    drawn = st.render()
    drawn.holders, drawn.links, drawn.ports = st.holders, st.links, st.ports
    return drawn


HARBOUR.stations.extend([
    Station("entrance", _framed(entrance_station), ("wait", "open")),
    Station("inspection", _framed(inspection_station), ("papers", "cargo")),
    Station("lock", _framed(lock_station), ("queue", "check")),
    Station("clock", _framed(clock_station), ("start", "done")),
    Station("fix", _framed(fix_station), ("weld", "green")),
    Station("flaky", _framed(flaky_station), ("stall", "run")),
    Station("owners", _framed(owners_station), ("watch", "radio")),
    Station("bypass", _framed(bypass_station), ("sneak", "bump")),
])
HARBOUR.backdrop = backdrop
HARBOUR.alternate = True                                   # never one moment on two pages in a row
HARBOUR.finale = finale
stories.OPENERS["lighthouse"] = opener
hide(HARBOUR, "inspection", "cargo")

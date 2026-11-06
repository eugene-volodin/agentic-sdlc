"""The road to the computer city: the world of the conclusion.

The five leave the professor's yard behind for good: a cobbled country road runs through the fields - wheat, lime
meadows, rows of apple trees - towards the computer city on the horizon, the one the farewell page walks into
(`farewell.py`; its towers are drawn by the farewell's own parts: server racks, a chip on end, a memory stick, a
capacitor, the hall under its cooling fan). Late afternoon going on to sunset; the conclusion's lime is the fields'
colour. The stations are what the road passes, the agents' work in the fields seen close:

1. orchard  an apple tree by the road - "pick": the agent picks apples into a basket, the cat looks one over with
            his magnifier; "carry": the agent carries a full crate, the caterpillar doubts it will all fit;
2. cart     the handcart at the roadside with its crates - "load": the agent loads a crate, the cat ticks the
            list; "go": the professor pulls the cart on along the road, the caterpillar walks beside, the sparrow
            rides on the crates.
finale      the whole way at once, as on the farewell page (`road.py`): the cobbled road comes from the city at
            sunset straight through the fields, bends near the reader and runs off across the frame; the four walk
            along the near stretch to the bend, all one way, the sparrow flying on ahead; agents at work far off.
opener      the start of the road at sunset: the same road, from the city on the horizon round its bend to the
            professor's gate, a fingerpost by the gate pointing on to the city and back home, the sparrow on its
            cap; the professor at his gate under his bubble, the agent and the cat waving, the caterpillar off ahead.

Words only on the fingerpost's arms, from the locale.
"""
from __future__ import annotations

import functools
import math
import random

from .. import design as P
from ..design import darken, mix
from . import handheld, sets
from .farewell import basket, city_view, dots, handcart
from .footers import Strip
from .ink import INK, Canvas, lettering, n, rounded_rect_d
from .road import Road, birds, body_box, furnish, long_shadow, rim, walk_along
from .openers import CLEAR_MM, H, OPENERS, W, Stage
from .world_courtyard import _framed, apple_tree, cast, gate, house, pickets, pk, roof
from .world_fair import lane, zoom
from .world_harbour import fx, place
from .world_kit import SIZE, Holder, Pen, _tag_pad, ledger, text_box
from .world_kitchen import _box
from .world_moon import checklist, height
from .world_sea import sparrow_on
from .world_base import Station, world

CITY = world("city", opener="city_road")

LIME = P.CHAPTER_LIME
SKY_TOP = mix(P.SKY, P.YELLOW_PALE, 0.25)
SKY_LOW = mix(P.YELLOW_PALE, P.ORANGE, 0.3)
WHEAT = mix(P.SUN, P.CRUST, 0.4)
MEADOW = mix(LIME, P.GRASS, 0.35)
COBBLE = (mix(P.STONE, P.SAND, 0.35), mix(P.PEBBLE, P.SAND, 0.25), mix(P.STONE, P.WOOD_PALE, 0.3))


# ============================================================================ the far land
@functools.cache
def _city_view() -> str:
    return city_view()


def walled_city(c: Canvas, vx: float, hz: float, k: float) -> tuple:
    """The farewell page's city (`farewell.city_view`) at `k` of its size: its towers, its wall of circuit board
    standing on the ground with the apron in front, and its glowing gate, whose opening sits on the vanishing point
    (vx, hz) - so a road running straight to it narrows exactly to the gate's width. Returns its box."""
    c.add(f'<g transform="translate({n(vx - 420 * k)},{n(hz - 560 * k)}) scale({n(k)})">{_city_view()}</g>')
    return (vx - 420 * k, hz - 392 * k, vx + 420 * k, hz + 126 * k)


def round_tree(c: Canvas, x: float, foot: float, k: float) -> None:
    """A light apple tree for the far land and the verges, 178 tall at k = 1: its shadow, a trunk with two boughs,
    a crown of three round masses with a lit top, red apples."""
    d = Canvas()
    d.add(f'<ellipse cx="0" cy="0" rx="34" ry="4" fill="{INK}" fill-opacity=".12"/>')
    d.shape("M-8,0 Q-6,-50 -10,-80 L-2,-84 Q4,-50 8,0 Z", P.TRUNK, sw=1.6, light=None)
    d.line("M-6,-70 Q-30,-84 -44,-80 M2,-76 Q24,-92 40,-86", 4, P.TRUNK)
    for cx, cy, r, col in ((-30, -112, 40, darken(P.LEAF, 0.85)), (24, -118, 42, P.LEAF), (-4, -140, 36,
                                                                                         P.LEAF_LIGHT)):
        d.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}" stroke="{INK}" stroke-width="1.6"/>')
    d.line("M-40,-150 q14,-14 30,-12 M10,-140 q12,-10 26,-6", 2.4, P.WHITE, 0.4)
    dots(d, [(-40, -108), (-18, -126), (20, -104), (36, -126), (-4, -150), (6, -118)], 8, P.RED, 1.4)
    c.add(f'<g transform="translate({n(x)},{n(foot)}) scale({n(k)})">{d.render()}</g>')


def sun(c: Canvas, x: float, y: float, r: float) -> None:
    """The low sun with its glow."""
    for rr, a in ((r * 1.9, 0.12), (r * 1.4, 0.2)):
        c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rr)}" fill="{P.YELLOW_PALE}" fill-opacity="{a}"/>')
    c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{mix(P.SUN, P.YELLOW_PALE, 0.4)}"/>')


def cobbles(c: Canvas, y0: float, y1: float, k: float, seed: int = 4) -> None:
    """The cobbled road: rows of rounded stones in three warm greys, the nearer rows bigger, mortar between, a kerb
    of long stones along its far edge and a strip of grass verge behind the kerb."""
    c.add(f'<rect x="-6" y="{n(y0)}" width="{W + 12}" height="{n(y1 - y0)}" fill="{darken(COBBLE[0], 0.8)}"/>')
    rnd = random.Random(seed)
    y, row = y0 + 7 * k, 0
    while y < y1:
        rh = (6 + row * 2.6) * max(0.6, k)
        x = -6 - rnd.uniform(0, rh)
        while x < W + 6:
            bw = rh * rnd.uniform(1.1, 1.6)
            c.add(f'<rect x="{n(x + 0.9)}" y="{n(y + 0.9)}" width="{n(bw - 1.8)}" height="{n(rh - 1.8)}" '
                  f'rx="{n(rh * 0.35)}" fill="{COBBLE[rnd.randrange(3)]}"/>')
            x += bw
        y += rh
        row += 1
    c.add(f'<rect x="-6" y="{n(y0)}" width="{W + 12}" height="{n(7 * k)}" fill="{P.STONE}" stroke="{INK}" '
          f'stroke-width="1"/>')
    c.line(" ".join(f"M{n(q)},{n(y0)} v{n(7 * k)}" for q in range(20, W, max(8, int(46 * k)))), 1, INK, 0.5)


def fields(c: Canvas, top: float, bottom: float, k: float, seed: int) -> None:
    """The fields between the horizon and the road, in bands that widen towards the viewer: wheat with its ears, a
    lime meadow, a farm track, rows of cabbages."""
    span = bottom - top
    bands = ((0.0, 0.22, WHEAT), (0.22, 0.42, MEADOW), (0.42, 0.5, mix(P.SAND, P.CRUST, 0.3)),
             (0.5, 0.78, mix(WHEAT, LIME, 0.25)), (0.78, 1.0, MEADOW))
    for a, b, col in bands:
        c.add(f'<rect x="-6" y="{n(top + span * a)}" width="{W + 12}" height="{n(span * (b - a) + 0.5)}" '
              f'fill="{col}"/>')
    rnd = random.Random(seed)
    ears = []
    for a, b in ((0.0, 0.22), (0.5, 0.78)):                     # the ears of wheat, in rows
        y = top + span * (a + 0.06)
        while y < top + span * b:
            q = rnd.uniform(0, 12)
            while q < W:
                ears.append(f"M{n(q)},{n(y)} l{n(1.4 * k)},{n(-4 * k)}")
                q += rnd.uniform(9, 15) * max(0.6, k)
            y += max(3.0, 5 * k)
    c.line(" ".join(ears), max(0.8, 1.1 * k), darken(WHEAT, 0.72))
    tufts = []
    for a, b in ((0.22, 0.42), (0.78, 1.0)):                    # tufts of grass in the meadows
        y = top + span * (a + 0.05)
        while y < top + span * b:
            q = rnd.uniform(0, 30)
            while q < W:
                tufts.append(f"M{n(q)},{n(y)} l{n(-1.5 * k)},{n(-4 * k)} M{n(q + 2 * k)},{n(y)} l{n(1.2 * k)},"
                             f"{n(-4.5 * k)}")
                q += rnd.uniform(22, 40) * max(0.6, k)
            y += max(4.0, 7 * k)
    c.line(" ".join(tufts), max(0.7, k), darken(MEADOW, 0.7), 0.8)
    c.line(f"M-6,{n(top + span * 0.42)} H{W + 6} M-6,{n(top + span * 0.5)} H{W + 6}", 1, darken(P.SAND, 0.75))
    y = top + span * 0.88                                        # cabbages along the near meadow
    q = rnd.uniform(0, 20)
    while q < W:
        r = max(2.0, 3.6 * k)
        c.add(f'<ellipse cx="{n(q)}" cy="{n(y)}" rx="{n(r)}" ry="{n(r * 0.75)}" fill="{P.LEAF}" stroke="{INK}" '
              f'stroke-width=".7"/>')
        q += r * 4.2


def depths(y0: float, y1: float, hz: float, share: float) -> list[float]:
    """Heights from y0 down to y1 at even steps of distance: each step `share` of the way to the horizon."""
    out, y = [], y0
    while y < y1:
        out.append(y)
        y += max(1.2, (y - hz) * share)
    return out


def crops(c: Canvas, vx: float, hz: float, bottom: float, edge: tuple[float, float], verge: float, meadow: str,
          wheat: str, row: float, seed: int) -> None:
    """The fields on both sides of a road in one-point perspective, in rows running to (vx, hz), as a farmer plants
    them: wheat by the horizon with its ears in lighter strips, then orchards of apple trees row behind row, a farm
    track across, vineyards - posts, the leafy band of the vines, bunches of grapes - and cabbages near, head after
    head in their furrows. `row` is the spacing of the rows where they reach `bottom`."""
    def at(y: float, foot: float) -> float:
        return vx + (foot - vx) * (y - hz) / (bottom - hz)

    def quad(y0: float, y1: float, f0: float, f1: float) -> str:
        return (f"M{n(at(y0, f0))},{n(y0)} L{n(at(y0, f1))},{n(y0)} L{n(at(y1, f1))},{n(y1)} "
                f"L{n(at(y1, f0))},{n(y1)} Z")

    def ys(f: float) -> float:
        return hz + (bottom - hz) * f

    far = -60 * row
    sides = ((far, edge[0] - verge), (edge[1] + verge, W - far))
    rnd = random.Random(seed)
    c.add(f'<path d="M-6,{n(hz)} H{W + 6} V{n(bottom + 6)} H-6 Z" fill="{meadow}"/>')
    y0, y1, y2, y3, y4 = hz, ys(0.12), ys(0.3), ys(0.34), ys(0.58)
    for lo, hi in sides:                                                  # the wheat
        c.add(f'<path d="{quad(y0, y1, lo, hi)}" fill="{wheat}"/>')
        strips = "".join(quad(y0, y1, f, f + row * 0.4) for f in _span(lo, hi, row))
        c.add(f'<path d="{strips}" fill="{mix(wheat, P.YELLOW_PALE, 0.4)}"/>')
    for lo, hi in sides:                                                  # the orchards' grass
        c.add(f'<path d="{quad(y1, y2, lo, hi)}" fill="{mix(meadow, P.GRASS_DARK, 0.5)}"/>')
    c.add(f'<rect x="-6" y="{n(y2)}" width="{W + 12}" height="{n(y3 - y2)}" fill="{mix(P.SAND, P.CRUST, 0.3)}"/>')
    c.line(f"M-6,{n(y2)} H{W + 6} M-6,{n(y3)} H{W + 6}", 1, darken(P.SAND, 0.75))
    trees = []
    for lo, hi in sides:
        for f in _span(lo + row, hi - row * 0.5, row * 1.6):
            for y in depths(y1 + 3, y2 - 1, hz, 0.22):
                x = at(y, f)
                if -20 < x < W + 20:
                    trees.append((y, x))
    trunks, crowns, lights, apples = [], {}, {}, {}
    for y, x in sorted(trees):                                            # far trees first
        h = (y - hz) * 0.42
        if h < 3:
            continue
        d = round(h * 0.42, 1)
        trunks.append(f"M{n(x)},{n(y)} v{n(-h * 0.45)}")
        crowns.setdefault(d, []).append((x, y - h * 0.62))
        lights.setdefault(d, []).append((x - d * 0.15, y - h * 0.7))
        apples.setdefault(round(max(1.0, d * 0.16), 1), []).extend(
            (x + d * dx, y - h * 0.62 + d * dy) for dx, dy in ((-0.25, 0.05), (0.2, -0.15), (0.05, 0.25)))
    c.line(" ".join(trunks), 1.6, P.TRUNK)
    for d, pts in crowns.items():                                         # crowns, a lit top, apples
        dots(c, pts, d, P.LEAF, 1.2)
    for d, pts in lights.items():
        c.add(f'<path d="{"".join(f"M{n(x)},{n(y)}h0" for x, y in pts)}" stroke="{P.LEAF_LIGHT}" '
              f'stroke-width="{n(d * 0.45)}" stroke-linecap="round"/>')
    for d, pts in apples.items():
        dots(c, pts, d, P.RED, 0.6)
    for lo, hi in sides:                                                  # the vineyards
        c.add(f'<path d="{quad(y3, y4, lo, hi)}" fill="{mix(P.SAND, P.CRUST, 0.45)}"/>')
        posts, leaves = [], []
        bunches: dict[float, list[tuple[float, float]]] = {}
        for f in _span(lo + row * 0.5, hi - row * 0.3, row * 1.2):
            if not -40 < at(y4, f) < W + 40 and not -40 < at(y3, f) < W + 40:
                continue
            for y in depths(y3 + 1, y4, hz, 0.12):
                kk = (y - hz) / 100
                posts.append(f"M{n(at(y, f))},{n(y)} v{n(-24 * kk)}")
            top = [(at(y, f), y - 24 * (y - hz) / 100) for y in (y3 + 1, y4)]
            bot = [(at(y, f), y - 10 * (y - hz) / 100) for y in (y4, y3 + 1)]
            leaves.append("M" + " L".join(f"{n(px)},{n(py)}" for px, py in top + bot) + " Z")
            for y in depths(y3 + 4, y4, hz, 0.16):
                kk = (y - hz) / 100
                gx, gy = at(y, f) + 4 * kk, y - 9 * kk
                bunches.setdefault(round(kk, 1), []).extend(
                    (gx + dx * kk, gy + dy * kk) for dx, dy in ((-1.5, 0), (1.5, 0), (0, 2.6), (0, 5)))
        c.line(" ".join(posts), 1.6, P.WOOD_DARK)
        c.add(f'<path d="{"".join(leaves)}" fill="{P.LEAF}" stroke="{P.LEAF_DARK}" stroke-width="1.2" '
              f'stroke-linejoin="round"/>')
        for kk, pts in bunches.items():                                   # bunches of grapes under the leaves
            dots(c, pts, 3.2 * kk, P.PLUM, 0.6)
    for lo, hi in sides:                                                  # the cabbages
        c.add(f'<path d="{quad(y4, bottom + 6, lo, hi)}" fill="{mix(P.CRUST_RAW, P.WOOD_PALE, 0.4)}"/>')
        furrows: list[str] = []
        heads: dict[float, list[tuple[float, float]]] = {}
        for f in _span(lo + row * 0.5, hi - row * 0.3, row * 0.75):
            if max(at(y4, f), at(bottom, f)) < -40 or min(at(y4, f), at(bottom, f)) > W + 40:
                continue
            furrows.append(quad(y4, bottom + 6, f - row * 0.12, f + row * 0.12))
            for y in depths(y4 + 3, bottom + 4, hz, 0.06):
                r = (y - hz) * 0.035 * rnd.uniform(0.85, 1.1)
                x = at(y, f)
                if not -r * 2 < x < W + r * 2:
                    continue
                heads.setdefault(round(r, 1), []).append((x, y - r * 0.6))
        c.add(f'<path d="{"".join(furrows)}" fill="{mix(P.CRUST_RAW, P.KITCHEN_KRAFT, 0.5)}"/>')
        for r, pts in sorted(heads.items()):                              # cabbages: outer leaves, head, light
            leaves_ = "".join(f"M{n(x - r * 1.1)},{n(y + r * 0.3)}l{n(r * 0.5)},{n(-r * 0.35)}M{n(x + r * 1.1)},"
                              f"{n(y + r * 0.3)}l{n(-r * 0.5)},{n(-r * 0.35)}" for x, y in pts)
            c.add(f'<path d="{leaves_}" stroke="{INK}" stroke-width="{n(r * 0.75 + 1)}" stroke-linecap="round"/>'
                  f'<path d="{leaves_}" stroke="{P.LEAF_DARK}" stroke-width="{n(r * 0.75)}" stroke-linecap="round"/>')
            body = "".join(f"M{n(x - r * 0.45)},{n(y)}h{n(r * 0.9)}" for x, y in pts)
            c.add(f'<path d="{body}" stroke="{INK}" stroke-width="{n(r * 1.56 + 1)}" stroke-linecap="round"/>'
                  f'<path d="{body}" stroke="{P.LEAF}" stroke-width="{n(r * 1.56)}" stroke-linecap="round"/>')
            lit = "".join(f"M{n(x - r * 0.45)},{n(y - r * 0.25)}h{n(r * 0.4)}" for x, y in pts)
            c.add(f'<path d="{lit}" stroke="{P.LEAF_LIGHT}" stroke-width="{n(r * 0.7)}" stroke-linecap="round"/>')


def _span(lo: float, hi: float, step: float) -> list[float]:
    out, x = [], lo
    while x < hi:
        out.append(x)
        x += step
    return out


def backdrop(s: Strip, index: int) -> None:
    """Behind every station: the late sky, the low sun, the computer city small on the horizon, the fields in
    bands with a row of apple trees, the grass verge and the cobbled road the cast stands on."""
    ledger(s)
    zoom(s)
    feet = lane(s).feet
    names = ("professor", "cat", "agent", "caterpillar")
    if s.h < 300:                                                      # a close-up: the professor nearly fills it
        top = max(_box(s, name, 0, feet)[3] - _box(s, name, 0, feet)[1] for name in names)
        s.tall *= (feet - 6) / top
    widest = max(_box(s, name, 0, feet)[2] - _box(s, name, 0, feet)[0] for name in names)
    s.tall *= min(1.0, (s.hi - s.lo) * 0.19 / widest)
    s.unit = s.tall / 137
    c = s.back
    base = s.base
    k = max(0.5, min(1.4, base / 240))
    horizon = base * 0.6
    s.yard = horizon
    sky(c, horizon)
    rnd = random.Random(index * 5 + 2)
    sun(c, W * (0.22 + 0.56 * ((index * 0.37) % 1)), horizon * 0.88, horizon * 0.14)
    walled_city(c, W * (0.8 if index % 2 else 0.2), horizon, horizon * 0.5 / 392)
    fields(c, horizon, base - 4 * k, k, index)
    tk = (base - horizon) * 0.42 / 176                                  # a row of apple trees across the fields
    ty = horizon + (base - horizon) * 0.46
    x = rnd.uniform(20, 90)
    while x < W + 40:
        round_tree(c, x, ty, tk)
        x += rnd.uniform(140, 220)
    c.add(f'<rect x="-6" y="{n(base - 4 * k)}" width="{W + 12}" height="{n(4 * k + 1)}" fill="{P.GRASS}"/>')
    cobbles(c, base, s.h + 4, max(0.8, s.unit), index)


def sky(c: Canvas, horizon: float) -> None:
    """The late afternoon sky, blue overhead going gold at the horizon."""
    sets.sky(c, SKY_TOP, SKY_LOW, horizon, W)


# ============================================================================ the things by the road
def crate(s: Strip, x: float, foot: float, k: float, name: str, group: str | None = None) -> tuple:
    """A wooden crate of apples standing at (x, foot) - x as drawn the canonical way round - 40 wide and 28 tall:
    its slatted side, the apples heaped inside its rim. Drawn on its own (it reads the same either way round).
    Returns its box."""
    left = fx(s, x) - 20 * k
    pen = Pen(s, left, foot - 28 * k, k)
    holder = pen.container(name, 0, 0, 40, 28, P.WOOD, radius=1.5, sw=1.3, light=None)
    pad = pen.pad(40, 28)
    r = (40 - 2 * pad) / 6
    pen.c.line(f"M{n(pad)},{n(pad + 2 * r + 3 / k + 2)} H{n(40 - pad)}", 1, P.WOOD_DARK)   # a slat's edge
    pen.c.line(f"M{n(pad + 2)},{n(28 - pad - 2)} q8,-1 16,0 t14,0", 0.6, darken(P.WOOD, 0.7), 0.7)   # its grain
    for q in range(3):
        pen.c.add(f'<circle cx="{n(pad + r + q * 2 * r)}" cy="{n(pad + r)}" r="{n(r * 0.9)}" '
                  f'fill="{P.RED if q != 1 else P.GREEN}" stroke="{INK}" stroke-width=".8"/>')
    pen.child(holder, "apples", pad, pad, 40 - pad, pad + 2 * r)
    box = (left, foot - 28 * k, left + 40 * k, foot)
    s.put(lane(s).feet - 0.6, pen.svg(), box, name, group=group or name)
    return box


def orchard_moment(s: Strip, beat: str) -> None:
    """The apple tree by the road: "pick" - the agent reaches up for the apples, a basket at its feet, the cat looks
    one over with his magnifier; "carry" - the agent carries a full crate to the road, a filled crate waits under
    the tree, the caterpillar doubts it will all fit."""
    r = lane(s)
    k = pk(s, 178, 1.0)
    c = Canvas()
    x = s.x(0.42)
    apple_tree(c, x, r.feet, k, swing=False)
    box = place(s, c, (x - 58 * k, r.feet - 178 * k, x + 54 * k, r.feet), "tree")
    if beat == "pick":
        art, bb = basket(fx(s, x + 36 * k), r.feet, height(s, "agent") / 110)
        s.put(r.feet - 0.5, art, bb, "basket", group="tree")
        whole = (min(box[0], bb[0]), box[1], max(box[2], bb[2]), box[3])
        cast(s, whole, (("agent", 1, "cheer", "smile", None), ("cat", -1, "present", "smile", handheld.magnifier)))
    else:
        bb = crate(s, x + 34 * k, r.feet, k * 0.9, "crate", "tree")
        whole = (min(box[0], bb[0]), box[1], max(box[2], bb[2]), box[3])
        cast(s, whole, (("agent", 1, "carry", "smile", None), ("caterpillar", -1, "think", "worry", None)))


def cart_moment(s: Strip, beat: str) -> None:
    """The handcart at the roadside: "load" - the agent brings one more crate, the cat ticks his list; "go" - the
    professor pulls the cart on along the road, the caterpillar walks beside it, the sparrow rides on the crates."""
    r = lane(s)
    k = pk(s, 63, 0.66)
    c = Canvas()
    x = s.x(0.45)
    art, bb = handcart(x, r.feet, k)
    c.add(art)
    box = place(s, c, bb, "cart")
    if beat == "load":
        cb = crate(s, x + 58 * k, r.feet, k * 0.7, "crate")
        whole = (min(box[0], cb[0]), box[1], max(box[2], cb[2]), box[3])
        cast(s, whole, (("agent", 1, "carry", "smile", None), ("cat", -1, "present", "smile", checklist(5))))
    else:
        cast(s, box, (("professor", -1, "walk", "smile", None), ("caterpillar", 1, "walk", "smile", None)))
        sparrow_on(s, fx(s, x), r.feet - 63 * k, "cart")


# ============================================================================ the finale
def finale(s: Strip) -> None:
    """The whole way at once, as on the farewell page: the road comes in from the left edge, bends wholly inside the
    frame with both its kerbs and verges in sight, and runs straight to the gate of the walled city on the horizon,
    narrowing exactly to the gate's width; fields in their rows up to the city wall, the hedge, the ditch with its
    bridge, the milestone and the bench by the road, birds over the fields; the four walking in along the road
    towards the bend, all one way, the agent ahead, the sparrow flying on ahead; agents at work far off. No labels."""
    ledger(s)
    zoom(s)
    s.mirror = False
    c = s.back
    hz = s.h * (0.36 if s.h >= 300 else 0.22)
    vx = W * 0.6
    k = min(0.4, hz * 0.55 / 392)                                      # the city, small by distance, sky over it
    w = 0.476 + 0.07 + 0.16                                            # the road, its kerb and verge, each side
    d_out = s.h - 6 - hz                                               # the bend's outer verge stays off the foot
    d_mid = d_out * 0.74
    f = w / (1 / d_mid - 1 / d_out)
    zc = f / d_mid
    radius = (vx + 30) / d_mid                                         # the bend ends just past the left edge
    road = Road(vx=vx, hz=hz, f=f, half=0.476, gate_z=f / (104 * k), near_z=zc, end_x=-radius, radius=radius,
                left_x=-(vx + 60) * zc / f - 0.3)                     # just past the left edge
    sky(c, hz + 2)
    sun(c, vx + 6, hz - 60 * k, 110 * k)
    birds(c, (W * 0.08, hz * 0.2, W * 0.92, hz * 0.55), 6, int(s.h))
    crops(c, vx, hz, s.h, (vx, vx), -90, MEADOW, WHEAT, 90, 3)            # no gap: the road goes on top
    walled_city(c, vx, hz, k)
    road.draw(c)
    bend = [i for i, (_, _, tx, tz) in enumerate(road.line) if -0.99 < tz < -0.35]
    size = min(2.6, max(1.3, 0.62 * s.h / (0.5 * d_mid)))              # in a low strip the five come forward
    four = ("agent", "professor", "cat", "caterpillar")
    while size > 0.7 and len(walk_along(s, road, four, bend[0], size=size, lo=s.lo, hi=s.hi, bottom=s.h * 0.88,
                                        dry=True)) < len(four):
        size *= 0.92                                                   # all four on the road, or smaller
    placed = walk_along(s, road, four, bend[0], size=size, lo=s.lo, hi=s.hi, bottom=s.h * 0.88,
                        sun=(vx + 6, hz - 60 * k))
    if placed:
        lead = placed[0]
        tall = (lead.bottom - lead.top) * 1.5
        for dx, lift, k_ in [(dx, lift, k_) for k_ in (0.5, 0.4, 0.3) for lift in (0.5, 0.7, 0.3)
                             for dx in (30, 60, 100, 0)]:
            bx, by = lead.right + dx, lead.top + (lead.bottom - lead.top) * lift
            probe = body_box("sparrow", bx, by, tall * k_)
            if probe[0] >= s.lo and probe[2] <= s.hi and probe[1] >= 4 and s.free(probe, 4):
                s.actor("sparrow", bx, by, "fly", "smile", tall=tall * k_, group="sparrow")
                break

    def at(y: float, foot: float) -> float:
        return vx + (foot - vx) * (y - hz) / (s.h - hz)

    if s.h >= 200:                                  # two agents at work far off in the fields, each where it fits
        for pose, sides in (("carry", (1, -1)), ("cheer", (-1, 1))):
            done = False
            for t_ in (0.3, 0.26, 0.34, 0.22, 0.38, 0.2, 0.42, 0.16):
                y = hz + (s.h - hz) * t_
                tall = (y - hz) * 0.85
                for side in sides:
                    for dist in (500, 700, 340, 900, 260, 1200, 160):
                        wx = at(y, vx + side * (300 + dist))
                        probe = _box(s, "agent", wx, y, tall / s.tall / SIZE["agent"])
                        if (probe[0] > s.lo and probe[2] < s.hi and probe[1] > 4 and s.free(probe, 4)
                                and not road.contains(wx, y, 0.1)):
                            s.actor("agent", wx, y, pose, "smile", tall=tall, group=f"worker{pose}",
                                    **({"held": "crate"} if pose == "carry" else {}))
                            done = True
                            break
                    if done:
                        break
                if done:
                    break
    furnish(s, road)


CITY.stations.extend([
    Station("orchard", _framed(orchard_moment), ("pick", "carry")),
    Station("cart", _framed(cart_moment), ("load", "go")),
])
CITY.backdrop = backdrop
CITY.finale = finale
CITY.alternate = True


# ============================================================================ the opener
def signpost(st: Stage, x: float, foot: float, k: float, city_way: int = 1) -> tuple:
    """A wooden fingerpost at (x, foot), 160 tall: the squared post with its grain, set in a stone, a little roof cap
    on top; two arms nailed on at the top pointing opposite ways - the upper one, `city_way` (+1 right, -1 left), on
    to the city, the lower one back home to the gate. Each arm a plank with a pointed end and a square one at the
    post, its grain, two nails, its word from the locale centred on it with air all round. Returns the post's box
    (for a bird to sit on its cap)."""
    d = Canvas()
    d.add(f'<ellipse cx="0" cy="0" rx="24" ry="3.4" fill="{INK}" fill-opacity=".15"/>')
    d.shape("M-15,0 Q-15,-11 0,-13 Q15,-11 15,0 Z", P.STONE, sw=1.4, light=None)               # the stone
    d.shape(rounded_rect_d(-5.5, -152, 11, 144, 1.5), P.WOOD, sw=1.6, light=(-1, -1))         # the post
    d.line("M-2,-148 q2,30 0,60 t0,70 M2,-140 q-1,40 1,90", 0.7, darken(P.WOOD, 0.7))
    d.shape("M-10,-151 L0,-160 L10,-151 Z", P.WOOD_DARK, sw=1.2, light=None)                   # its cap
    st.put(foot, f'<g transform="translate({n(x)},{n(foot)}) scale({n(k)})">{d.render()}</g>',
           (x - 10 * k, foot - 160 * k, x + 10 * k, foot), "signpost", group="signpost", backdrop=True)
    pen = Pen(st, x, foot, k)
    size = 13.0
    holders = ledger(st)[0]
    for key, cy, way in (("city", -128, city_way), ("home", -100, -city_way)):
        text = st.word(key)
        tx0, tt, tx1, tb = text_box(0, 0, text, size)
        pad = _tag_pad(tx1 - tx0, tb - tt, size, k)
        w, h = tx1 - tx0 + 2 * pad, tb - tt + 2 * pad
        x0, x1 = way * 4, way * (4 + w)
        tip = x1 + way * h * 0.5
        top = cy - h / 2
        board = (f"M{n(x0)},{n(top)} L{n(x1)},{n(top)} L{n(tip)},{n(cy)} L{n(x1)},{n(top + h)} "
                 f"L{n(x0)},{n(top + h)} Z")
        pen.c.shape(board, P.WOOD_PALE, sw=1.6, light=None)
        pen.c.line(f"M{n(x0 + way * 3)},{n(top + 2.4)} h{n(way * w * 0.5)} M{n(x0 + way * w * 0.4)},"
                   f"{n(top + h - 2.4)} h{n(way * w * 0.45)}", 0.6, darken(P.WOOD_PALE, 0.7), 0.8)   # its grain
        pen.c.add("".join(f'<circle cx="{n(x0 + way * 3.2)}" cy="{n(cy + dy)}" r="1.1" fill="{INK}"/>'
                          for dy in (-h * 0.25, h * 0.25)))                                         # the nails
        mid = (x0 + x1) / 2
        base = top + pad - tt
        pen.c.add(lettering(mid, base, text, size, INK, style="sign"))
        left, right = sorted((x0, tip))
        holder = Holder(f"arm-{key}", pen.box(min(x0, x1), top, max(x0, x1), top + h),
                        pen.box(min(x0, x1) + pad, top + pad, max(x0, x1) - pad, top + h - pad))
        holder.children.append(("text", pen.box(mid + tx0, base + tt, mid + tx1, base + tb)))
        holders.append(holder)
        st.put(foot + 0.5, "", pen.box(left, top, right, top + h), f"board-{key}", group="signpost", backdrop=True)
    st.put(foot + 0.5, pen.svg(), None)
    return (x - 10 * k, foot - 160 * k, x + 10 * k, foot)


WALK_TALL = 250                   # the professor's height where the three walk: a step behind him
WALKERS = (("cat", 309, 1082, "wave"), ("agent", 434, 1072, "stride"), ("caterpillar", 543, 1064, "stride"))
POST = (680, 1130.0, 1.0)        # the fingerpost on the verge of the near bend: x, foot, scale


def opener(st: Stage, accent: str):
    """The start of the road at sunset: the cast has just come out through the professor's gate - its posts and its
    open picket gate in the fence, the yard behind it with the house's tiled roof and the apple tree - onto the
    cobbled road that runs off through the fields to the computer city, a small silhouette on the horizon against
    the setting sun. A wooden signpost by the road points on to the city and back home, the sparrow sitting on its
    cap; crops in their rows to the corners - wheat far off, orchards, vineyards, cabbages near. The caterpillar is
    already off along the road, the agent and the cat wave to the reader, the professor stands by his gate under
    his bubble."""
    ledger(st)
    c = st.back
    hz, vx = 770.0, 560.0
    kc = 0.5                                                           # the city, small by distance
    road = Road(vx=vx, hz=hz, f=818.0, half=0.476, gate_z=818.0 / (104 * kc), near_z=2.727, end_x=-0.833,
                radius=0.833, left_x=-2.2, course=0.2, across=6)      # straight from the gate, bend, then home
    meadow, wheat = mix(accent, P.GRASS, 0.3), mix(P.SUN, accent, 0.3)
    paint = c.gradient([(0, mix(P.INDIGO, P.SKY_DEEP, 0.45)), (0.35, mix(P.VIOLET, P.PINK_PALE, 0.55)),
                        (0.62, mix(P.PINK, P.ORANGE, 0.45)), (0.85, mix(P.ORANGE, P.SUN, 0.55)),
                        (1, mix(P.SUN, P.YELLOW_PALE, 0.5))], 0, 0, 0, hz)
    c.add(f'<rect x="-4" y="-4" width="{W + 8}" height="{n(hz + 8)}" fill="{paint}"/>')
    sets.stars(c, (700, 20, W - 20, 200), 8, seed=4)
    for x, y, k in ((620, 330, 1.2), (250, 560, 0.8), (780, 520, 0.7)):          # long clouds, lit from below
        c.add(f'<path d="M{n(x - 90 * k)},{n(y)} q{n(20 * k)},{n(-22 * k)} {n(60 * k)},{n(-14 * k)} '
              f'q{n(30 * k)},{n(-22 * k)} {n(70 * k)},0 q{n(30 * k)},{n(-6 * k)} {n(50 * k)},{n(14 * k)} Z" '
              f'fill="{mix(P.PINK_PALE, P.VIOLET, 0.3)}" stroke="{mix(P.INDIGO, INK, 0.4)}" stroke-width="2"/>'
              f'<path d="M{n(x - 84 * k)},{n(y - 3)} H{n(x + 104 * k)}" stroke="{P.YELLOW_PALE}" '
              f'stroke-width="{n(4 * k)}" stroke-linecap="round"/>')
    sun(c, vx + 40, hz - 18, 74)
    rays = []
    for i in range(13):                                                # the sun's rays fanning out, faint
        a0, a1 = math.radians(-180 + i * 14 + 3), math.radians(-180 + i * 14 + 9)
        rays.append(f"M{n(vx + 40)},{n(hz - 18)} L{n(vx + 40 + 380 * math.cos(a0))},{n(hz - 18 + 380 * math.sin(a0))} "
                    f"L{n(vx + 40 + 380 * math.cos(a1))},{n(hz - 18 + 380 * math.sin(a1))} Z")
    c.add(f'<path d="{" ".join(rays)}" fill="{P.YELLOW_PALE}" fill-opacity=".08"/>')
    birds(c, (380, 600, 800, 700), 5, 9)
    crops(c, vx, hz, H, (vx, vx), -230, meadow, wheat, 230, 8)           # the road is laid over them
    city = walled_city(c, vx, hz, kc)
    st.put(hz, "", (city[0], city[1], city[2], hz + 40 * kc), "city", backdrop=True)   # its towers; the wall is low
    # the professor's yard behind its fence, on the left, where the road ends at his gate: lawn, the house with its
    # roof, the apple tree
    fence_y = 1002.0
    yard = f"M-6,{n(hz + 110)} L330,{n(hz + 110)} L360,{n(fence_y)} H-6 Z"
    c.add(f'<path d="{yard}" fill="{mix(LIME, P.GRASS, 0.55)}"/>')
    c.line(" ".join(f"M{q},{n(hz + 130 + (q % 37))} l3,-7 M{q + 5},{n(hz + 132 + (q % 37))} l-2,-6"
                    for q in range(10, 330, 23)), 1.2, P.LEAF_DARK)                     # tufts in the lawn
    far = Canvas()
    house(far, 110, fence_y - 92, 0.8)
    roof(far, 110, fence_y - 92, 0.8)
    round_tree(far, 300, fence_y - 70, 0.82)
    c.add(far.render())
    pickets(c, -6, 40, fence_y, 1.5)
    pickets(c, 230, 350, fence_y, 1.5)
    road.draw(c, 8)
    gate_k = 1.5
    gc = Canvas()                                  # the gate turned round: its mailbox on the far post, by the house
    g = gate(gc, 165, fence_y, gate_k, open_=True)
    c.add(f'<g transform="translate(300,0) scale(-1,1)">{gc.render()}</g>')
    box = (300 - g["box"][2], g["box"][1], 300 - g["box"][0], g["box"][3])
    st.put(fence_y, "", box, "gate", backdrop=True)
    st.keep_clear((-6, hz - 2, 420, hz + 2), (-6, fence_y - 70 * 1.5, 420, fence_y - 66 * 1.5))
    for z in (4.2, 3.2):                                               # apple trees along the road's verge
        gx, gz = road.at(road.index_at(0.0, z), road.half + 0.6)
        x, y = road.page(gx, gz)
        k = (y - hz) * 0.55 / 176
        tree = Canvas()
        round_tree(tree, x, y, k)
        st.put(y, tree.render(), (x - 58 * k, y - 178 * k, x + 54 * k, y), f"tree{round(z)}", group="trees",
               backdrop=True)
    post = signpost(st, POST[0], POST[1], POST[2], city_way=1)          # by the gate: on to the city, back home
    st.actor("sparrow", POST[0], post[1] + 2, "stand", "smile", flip=True, tall=90, group="signpost", depth=fence_y + 5)
    for t, foot, pose in ((0.1, 1500.0, "carry"), (0.12, -500.0, "cheer")):   # agents at work far off
        y = hz + (H - hz) * t
        x = vx + (foot - vx) * (y - hz) / (H - hz)
        probe = body_box("agent", x, y, (y - hz) * 0.9)
        if st.free(probe, 4) and not road.contains(x, y, 0.1):
            st.actor("agent", x, y, pose, "smile", tall=(y - hz) * 0.9, group=f"worker{pose}",
                     **({"held": "crate"} if pose == "carry" else {}))
    prof = st.actor("professor", 150, 1094, "explain", "talk", tall=310)
    st.speaker(prof, width=74, left=8, air=CLEAR_MM)
    # the three side by side on the near bend, a step from the professor, their feet at one depth, each at its
    # own size beside him: walking together towards the bend, the cat at the back turning to wave to us
    sun_ = (vx + 40, hz - 18)
    for name, x, feet, pose in WALKERS:
        box = body_box(name, x, feet, WALK_TALL)
        long_shadow(st, box, sun_)
        who = st.actor(name, x, feet, pose, "smile", tall=WALK_TALL, group=name)
        rim(st, who, sun_)
    furnish(st, road)
    drawn = st.render()
    drawn.holders, drawn.links, drawn.ports = st.holders, st.links, st.ports
    return drawn


OPENERS["city_road"] = opener

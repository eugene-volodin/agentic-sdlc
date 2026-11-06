"""The forest camp: the world of chapter 10 (security).

A summer camp in a pine forest: a log gate with its sentry box in a palisade of pointed logs, tents and log cabins,
a campfire circle, the supply store, a lake with a jetty, a watchtower. The agent works for the camp; the camp
leader (the professor) gives the permissions. The cast stands on the camp's plank walkway; the buildings stand
across the clearing, true to their size. The stations, one per section of the chapter:

1. keys      the agent works in your name: at the leader's key cabinet the agent gets the leader's keyring on a
             lanyard - his keys open what the leader can open;
2. knock     few requests, but to the point: the leader's letterbox overflows with the agent's notes, one a minute
             - then a single short list, and one signature;
3. sandbox   the sandbox: in the fenced woodworking yard the agent saws and hammers without asking anyone;
4. parcel    other people's code: a parcel at the gate, a strange gadget in it that would run inside the camp - the
             sentry (the cat) checks it before it is opened;
5. note      other people's text: a note on the notice board outside the fence says "open the store" - the agent
             reads it and does not obey; the caterpillar holds up the leader's real note;
6. practice  dev, staging and preview: on the practice ground the agent pitches the practice tent and takes it down
             itself;
7. store     production: the supply chest under its padlock - the agent brings its request card, the leader
             decides and opens it;
8. plan      before your "yes": on the camp table the agent lays out the map with the plan, the list of risks and
             the backup crate with a spare canister packed;
9. test      checking that the protection works: in a drill the sparrow tries to get into the chest - the padlock
             and the sentry stop him, the cat times it.

No words in the pictures but the note on the notice board and the finale's names of the stations.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten, mix
from . import handheld, sets, stories
from .footers import Strip
from .ink import INK, Canvas, lettering, n, rounded_rect_d
from .openers import CLEAR_MM, H, W, Stage
from .world_fair import lane, zoom
from .world_harbour import across, fx, place
from .world_kit import SIZE, Pen, ledger, tag_size
from .world_kitchen import _box
from .world_moon import cast, checklist, height, low, mates, perch
from .world_sea import sparrow_on
from .worlds import Station, world

CAMP = world("camp", opener="forest_camp")

_at = sets._at

PINE = P.PINE
SKY_TOP = mix(P.SKY, PINE, 0.12)                      # a summer sky over the pines
SKY_LOW = mix(P.YELLOW_PALE, P.SKY_LOW, 0.5)
NEEDLE = mix(PINE, P.LEAF_DARK, 0.3)                  # the pines' needles
LOG = mix(P.WOOD, P.WOOD_LIGHT, 0.3)                  # the logs of the cabins
BOARD = (mix(P.WOOD, P.WOOD_LIGHT, 0.45), mix(P.WOOD_LIGHT, P.WOOD_PALE, 0.35))
GRASS = mix(P.GREEN, PINE, 0.35)


def calm(color: str) -> str:
    """A colour across the clearing, calmer with the distance."""
    return mix(color, SKY_LOW, 0.35)


# ============================================================================ the forest and the camp far off
def pine(c: Canvas, x: float, foot: float, k: float, color: str = NEEDLE, seed: int = 0) -> None:
    """A pine, its foot at (x, foot), 120 tall: the reddish trunk and four tiers of needles, each with a darker
    underside, ragged at the edges."""
    rnd = random.Random(seed)
    c.add(f'<rect x="{n(x - 3 * k)}" y="{n(foot - 40 * k)}" width="{n(6 * k)}" height="{n(40 * k)}" '
          f'fill="{calm(mix(P.WOOD, P.TERRACOTTA, 0.3)) if color != NEEDLE else mix(P.WOOD, P.TERRACOTTA, 0.3)}"/>')
    for q in range(4):
        w = (34 - q * 7) * k * rnd.uniform(0.9, 1.1)
        y = foot - (30 + q * 22) * k
        h = 30 * k
        c.add(f'<path d="M{n(x - w)},{n(y)} L{n(x - w * 0.6)},{n(y - h * 0.45)} L{n(x - w * 0.75)},{n(y - h * 0.5)} '
              f'L{n(x)},{n(y - h)} L{n(x + w * 0.75)},{n(y - h * 0.5)} L{n(x + w * 0.6)},{n(y - h * 0.45)} '
              f'L{n(x + w)},{n(y)} Z" fill="{color}"/>')
        c.add(f'<path d="M{n(x - w)},{n(y)} L{n(x + w)},{n(y)} L{n(x + w * 0.7)},{n(y - 5 * k)} '
              f'L{n(x - w * 0.7)},{n(y - 5 * k)} Z" fill="{darken(color, 0.8)}"/>')


def tent_far(c: Canvas, x: float, foot: float, k: float, color: str, lit: bool = False) -> None:
    """A ridge tent across the clearing: its canvas, the dark doorway, the guy lines and pegs."""
    c.add(f'<path d="M{n(x - 30 * k)},{n(foot)} L{n(x)},{n(foot - 30 * k)} L{n(x + 30 * k)},{n(foot)} Z" '
          f'fill="{color}" stroke="{calm(INK)}" stroke-width=".8"/>'
          f'<path d="M{n(x - 7 * k)},{n(foot)} L{n(x)},{n(foot - 18 * k)} L{n(x + 7 * k)},{n(foot)} Z" '
          f'fill="{P.SUN if lit else darken(color, 0.6)}"/>')
    c.line(f"M{n(x)},{n(foot - 30 * k)} L{n(x - 44 * k)},{n(foot)} M{n(x)},{n(foot - 30 * k)} L{n(x + 44 * k)},"
           f"{n(foot)}", 0.8, calm(INK), 0.5)


def cabin(c: Canvas, x: float, foot: float, k: float, kind: str = "hut") -> dict:
    """A log cabin at (x, foot), 160 wide and 140 tall: courses of round logs with their notched ends crossing at
    the corners, a shingled roof with its chimney, a window with shutters, the plank door up two steps under a
    little porch roof; "store": double doors with an iron bar and a padlock, crates by the wall; "leader": a lamp
    over the door and a bench. Returns its box and where its door is."""
    d = Canvas()
    for q in range(8):                                                                         # the logs
        y = -10 - q * 11
        d.shape(rounded_rect_d(-78, y - 5.5, 156, 11, 5.5), LOG if q % 2 else darken(LOG, 0.93), sw=1.1,
                light=None)
        for ex in (-80, 80):
            d.add(f'<circle cx="{ex}" cy="{y}" r="6" fill="{mix(LOG, P.WOOD_PALE, 0.4)}" stroke="{INK}" '
                  f'stroke-width="1"/><circle cx="{ex}" cy="{y}" r="2.6" fill="none" stroke="{P.WOOD}" '
                  f'stroke-width=".8"/>')
    d.shape("M-96,-92 L0,-140 L96,-92 L90,-86 L0,-130 L-90,-86 Z", darken(P.WOOD_DARK, 0.9), sw=1.6, light=None)
    d.shape("M-90,-92 L0,-136 L90,-92 Z", mix(P.TERRACOTTA, P.WOOD_DARK, 0.5), sw=1.4, light=None)  # the roof
    d.line(" ".join(f"M{-80 + q * 10},{n(-92 - (q * 10 if q < 9 else (16 - q) * 10) * 0.48)} v6"
                    for q in range(16)), 0.8, INK, 0.35)
    d.shape(rounded_rect_d(40, -150, 14, 34, 1), P.STONE, sw=1.2, light=None)                  # the chimney
    d.shape(rounded_rect_d(-62, -66, 30, 26, 2), P.WOOD_DARK, sw=1.4, light=None)               # the window
    d.shape(rounded_rect_d(-58, -62, 22, 18, 1), P.YELLOW_PALE if kind != "store" else P.LENS, sw=1, light=None)
    d.line("M-47,-62 V-44 M-58,-53 H-36", 1.2, P.WOOD_DARK)
    for sx_ in (-70, -32):
        d.shape(rounded_rect_d(sx_, -66, 8, 26, 1), mix(PINE, P.WOOD, 0.3), sw=1, light=None)  # its shutters
    if kind == "store":
        d.shape(rounded_rect_d(4, -74, 52, 70, 2), P.WOOD_DARK, sw=1.6, light=None)
        d.line("M30,-74 V-4 M4,-50 H56 M4,-26 H56", 1.2, INK, 0.5)
        d.shape(rounded_rect_d(2, -44, 56, 6, 1), P.METAL_DARK, sw=1, light=None)              # the iron bar
        d.add(f'<path d="M26,-36 a4,4 0 0 1 8,0 v3" fill="none" stroke="{P.METAL_DARK}" stroke-width="1.6"/>')
        d.shape(rounded_rect_d(24, -34, 12, 10, 2), P.YELLOW, sw=1, light=None)                # the padlock
        for q in range(2):
            d.shape(rounded_rect_d(62 + q * 4, -22 - q * 18, 20, 18, 1), P.WOOD_LIGHT, sw=1, light=None)
    else:
        d.shape(rounded_rect_d(8, -76, 30, 66, 2), P.WOOD_DARK, sw=1.6, light=None)              # the door
        d.line("M16,-76 V-10 M24,-76 V-10 M32,-76 V-10", 1, INK, 0.35)
        d.add(f'<circle cx="32" cy="-42" r="1.8" fill="{P.METAL}"/>')
    d.shape("M-4,-82 L64,-82 L58,-92 L2,-92 Z", darken(P.WOOD_DARK, 0.9), sw=1.2, light=None)  # porch roof
    d.line("M2,-82 V-8 M58,-82 V-8", 2.4, P.WOOD)
    d.shape(rounded_rect_d(-2, -10, 68, 5, 1), P.WOOD, sw=1, light=None)                        # the steps
    d.shape(rounded_rect_d(4, -5, 56, 5, 1), darken(P.WOOD, 0.9), sw=1, light=None)
    if kind == "leader":
        d.add(f'<circle cx="23" cy="-86" r="3" fill="{P.SUN}" stroke="{INK}" stroke-width=".8"/>')
        d.shape(rounded_rect_d(-74, -24, 40, 5, 1), P.WOOD, sw=1, light=None)                   # the bench
        d.line("M-70,-19 V-4 M-38,-19 V-4", 2, P.WOOD_DARK)
    c.add(_at(d, x, foot, k))
    return {"box": (x - 97 * k, foot - 151 * k, x + 97 * k, foot), "door": (x + 30 * k, foot - 40 * k)}


def gate(c: Canvas, x: float, foot: float, k: float) -> dict:
    """The camp's log gate at (x, foot), 220 wide and 160 tall: the palisade of pointed logs either side, two tall
    gate posts under a little shingled roof beam, the plank gate leaves swung open, and beside it the sentry box -
    a log booth with its window and a lantern. Returns its box."""
    d = Canvas()
    for q in range(-11, 12):                                                                   # the palisade
        if abs(q) <= 3:
            continue
        px = q * 10
        d.shape(f"M{px - 5},0 V-88 L{px},-96 L{px + 5},-88 V0 Z", LOG if q % 2 else darken(LOG, 0.92), sw=1,
                light=None)
    d.line("M-115,-30 H-35 M35,-30 H115 M-115,-70 H-35 M35,-70 H115", 2, P.WOOD_DARK)
    for px in (-34, 34):                                                                       # the gate posts
        d.shape(rounded_rect_d(px - 6, -132, 12, 132, 3), P.WOOD, sw=1.4, light=None)
    d.shape("M-48,-132 L0,-150 L48,-132 L44,-126 H-44 Z", mix(P.TERRACOTTA, P.WOOD_DARK, 0.5), sw=1.4,
            light=None)
    d.shape(rounded_rect_d(-30, -126, 60, 8, 1), P.WOOD_DARK, sw=1.2, light=None)
    for side in (-1, 1):                                                                       # its leaves, open
        d.shape(f"M{side * 28},-4 L{side * 46},4 L{side * 46},-80 L{side * 28},-88 Z", P.WOOD_LIGHT, sw=1.2,
                light=None)
        d.line(f"M{side * 28},-60 L{side * 46},-52 M{side * 28},-24 L{side * 46},-16", 1.4, P.WOOD_DARK)
    d.shape(rounded_rect_d(64, -84, 40, 84, 3), LOG, sw=1.4, light=None)                         # sentry box
    d.shape("M58,-84 L84,-100 L110,-84 Z", mix(P.TERRACOTTA, P.WOOD_DARK, 0.5), sw=1.2, light=None)
    d.shape(rounded_rect_d(72, -70, 24, 18, 2), P.YELLOW_PALE, sw=1, light=None)
    d.add(f'<circle cx="104" cy="-74" r="3" fill="{P.SUN}" stroke="{INK}" stroke-width=".8"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 116 * k, foot - 151 * k, x + 111 * k, foot)}


def watchtower(c: Canvas, x: float, foot: float, k: float) -> None:
    """The watchtower: four log legs with their cross braces, a ladder, the railed lookout and its roof."""
    d = Canvas()
    d.line("M-24,0 L-14,-120 M24,0 L14,-120", 3.4, P.WOOD)
    d.line("M-22,-30 L18,-60 M22,-30 L-18,-60 M-18,-70 L14,-100 M18,-70 L-14,-100", 1.6, P.WOOD_DARK)
    d.line("M-4,0 V-120 M4,0 V-120 " + " ".join(f"M-4,{-10 - q * 12} h8" for q in range(9)), 1.2, P.WOOD_DARK)
    d.shape(rounded_rect_d(-26, -136, 52, 16, 2), LOG, sw=1.2, light=None)
    d.shape("M-32,-150 L0,-168 L32,-150 Z", mix(P.TERRACOTTA, P.WOOD_DARK, 0.5), sw=1.2, light=None)
    d.line("M-24,-136 V-150 M24,-136 V-150", 1.6, P.WOOD_DARK)
    c.add(_at(d, x, foot, k))


def far_camp(c: Canvas, land: float, k: float, seed: int) -> None:
    """Across the clearing, calmer than the stations: two rows of pines with the forest behind them, and in
    front of them the camp - tents, cabins, the watchtower, the palisade, the lake with its jetty - turning from
    frame to frame."""
    rnd = random.Random(seed)
    kinds = ("tents", "cabin", "woodpile", "lake", "tower", "washstand", "tents", "palisade")
    x, i = -30 * k * (seed % 3), seed
    while x < W + 40:
        kind = kinds[i % len(kinds)]
        w = {"tents": 140, "cabin": 120, "lake": 170, "tower": 70, "palisade": 130, "woodpile": 70,
             "washstand": 50}[kind] * k
        cx = x + w / 2
        if kind == "tents":
            for q in range(2):
                tent_far(c, x + w * (0.3 + q * 0.45), land, k * 0.7, calm((P.ORANGE, P.TEAL)[q]))
        elif kind == "cabin":
            cabin(c, cx, land, k * 0.42)
        elif kind == "lake":
            c.add(f'<ellipse cx="{n(cx)}" cy="{n(land - 2)}" rx="{n(w * 0.48)}" ry="{n(7 * k)}" '
                  f'fill="{calm(mix(P.BLUE, PINE, 0.25))}"/>')
            c.line(f"M{n(cx - w * 0.3)},{n(land - 3)} q6,-2 12,0 M{n(cx + w * 0.05)},{n(land - 1)} q6,-2 12,0", 1,
                   P.WHITE, 0.7)
            c.add(f'<rect x="{n(cx + w * 0.12)}" y="{n(land - 5 * k)}" width="{n(w * 0.26)}" height="{n(3 * k)}" '
                  f'fill="{calm(P.WOOD)}"/>')                                                    # the jetty
        elif kind == "tower":
            watchtower(c, cx, land, k * 0.45)
        elif kind == "woodpile":                                       # logs stacked between two posts
            for row in range(3):
                for q in range(5 - row):
                    c.add(f'<circle cx="{n(x + (12 + q * 10 + row * 5) * k)}" cy="{n(land - (4 + row * 8.6) * k)}" '
                          f'r="{n(4.6 * k)}" fill="{calm(P.WOOD_PALE)}" stroke="{calm(INK)}" stroke-width=".7"/>')
            c.line(f"M{n(x + 4 * k)},{n(land)} v{n(-30 * k)} M{n(x + 64 * k)},{n(land)} v{n(-30 * k)}", 1.6,
                   calm(P.WOOD_DARK))
        elif kind == "washstand":                                      # a row of tin basins on a plank
            c.line(f"M{n(x + 6 * k)},{n(land)} v{n(-22 * k)} M{n(x + 44 * k)},{n(land)} v{n(-22 * k)}", 1.4,
                   calm(P.WOOD_DARK))
            c.add(f'<rect x="{n(x + 2 * k)}" y="{n(land - 24 * k)}" width="{n(46 * k)}" height="{n(4 * k)}" '
                  f'fill="{calm(P.WOOD)}"/>')
            for q in range(3):
                c.add(f'<path d="M{n(x + (6 + q * 14) * k)},{n(land - 24 * k)} h{n(10 * k)} l{n(-2 * k)},'
                      f'{n(-5 * k)} h{n(-6 * k)} Z" fill="{calm(P.METAL_LIGHT)}"/>')
        else:
            for q in range(int(w / (8 * k))):
                px = x + q * 8 * k
                c.add(f'<path d="M{n(px)},{n(land)} V{n(land - 26 * k)} l{n(4 * k)},{n(-4 * k)} '
                      f'l{n(4 * k)},{n(4 * k)} V{n(land)} Z" fill="{calm(LOG)}"/>')
        x += w + rnd.uniform(10, 40) * k
        i += 1


def boardwalk(c: Canvas, x0: float, x1: float, y0: float, y1: float, k: float) -> None:
    """The camp's plank walkway from y0 down: boards running across, nearer rows wider, their joints and nail
    heads, the edge beam at the back."""
    c.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" fill="{darken(BOARD[0], 0.7)}"/>')
    y, row = y0 + 6 * k, 0
    rnd = random.Random(5)
    while y < y1:
        rh = (6 + row * 3.4) * max(0.6, k)
        x = x0 - rnd.uniform(0, 80)
        while x < x1:
            pl = rnd.uniform(90, 160) * k
            c.add(f'<rect x="{n(x + 0.8)}" y="{n(y + 0.8)}" width="{n(pl - 1.6)}" height="{n(rh - 1.6)}" '
                  f'fill="{BOARD[(row + int(x / 50)) % 2]}"/>')
            if rh > 8:
                c.add(f'<circle cx="{n(x + 5)}" cy="{n(y + rh / 2)}" r="{n(rh * 0.08)}" fill="{P.WOOD_DARK}"/>'
                      f'<circle cx="{n(x + pl - 5)}" cy="{n(y + rh / 2)}" r="{n(rh * 0.08)}" fill="{P.WOOD_DARK}"/>')
            x += pl
        y += rh
        row += 1
    c.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(6 * k)}" fill="{P.WOOD_DARK}" '
          f'stroke="{INK}" stroke-width="1.2"/>')


EARTH = mix(P.WOOD, P.SAND, 0.45)                     # the clearing's trodden earth


def clearing(c: Canvas, top: float, bottom: float, k: float, seed: int, calm_x: tuple[float, float]) -> None:
    """The camp's clearing between the camp across and the walkway: trodden earth with its worn paths, patches of
    grass with their tufts, pine needles, cones, stones lit on top, roots crossing a path, and a log edging along
    the walkway; calmer behind the station (`calm_x`)."""
    rnd = random.Random(seed)
    h = bottom - top
    c.add(f'<rect x="-6" y="{n(top)}" width="{W + 12}" height="{n(h + 2)}" fill="{EARTH}"/>')
    for q in range(5):                                                 # shade and dry patches
        sx_ = rnd.uniform(0, W)
        c.add(f'<ellipse cx="{n(sx_)}" cy="{n(top + h * rnd.uniform(0.2, 0.9))}" rx="{n(rnd.uniform(60, 140) * k)}" '
              f'ry="{n(h * 0.12)}" fill="{darken(EARTH, 0.9) if q % 2 else mix(EARTH, GRASS, 0.3)}"/>')
    for q in range(3):                                                 # the worn paths, lighter
        py = top + h * (0.2 + q * 0.28)
        c.add(f'<path d="M-6,{n(py)} Q{n(W * 0.3)},{n(py - h * 0.06)} {n(W * 0.6)},{n(py + h * 0.04)} '
              f'T{n(W + 6)},{n(py)} V{n(py + h * 0.09)} Q{n(W * 0.6)},{n(py + h * 0.12)} {n(W * 0.3)},'
              f'{n(py + h * 0.05)} T-6,{n(py + h * 0.09)} Z" fill="{lighten(EARTH, 0.1)}"/>')

    def calm_(x: float) -> bool:
        return calm_x[0] < x < calm_x[1]
    for _ in range(int(W / 45)):                                       # grass patches
        gx, gy = rnd.uniform(0, W), rnd.uniform(top + 2, bottom - 4)
        w = rnd.uniform(30, 80) * k
        c.add(f'<ellipse cx="{n(gx)}" cy="{n(gy)}" rx="{n(w)}" ry="{n(w * 0.16)}" fill="{GRASS}"/>')
        if not calm_(gx):
            for q in range(int(w / (9 * k))):
                tx = gx - w * 0.8 + q * 9 * k
                c.line(f"M{n(tx - 2 * k)},{n(gy)} l{n(k)},{n(-6 * k)} M{n(tx)},{n(gy)} l0,{n(-8 * k)} "
                       f"M{n(tx + 2 * k)},{n(gy)} l{n(-k)},{n(-6 * k)}", max(0.8, 1.1 * k), darken(GRASS, 0.7))
    for _ in range(int(W / 18)):                                       # pine needles
        nx, ny = rnd.uniform(0, W), rnd.uniform(top + 2, bottom - 2)
        if calm_(nx):
            continue
        a = rnd.uniform(0, math.pi)
        c.line(f"M{n(nx)},{n(ny)} l{n(math.cos(a) * 6 * k)},{n(math.sin(a) * 2 * k)}", max(0.7, k),
               darken(EARTH, 0.7))
    for _ in range(int(W / 110)):                                      # cones and stones
        px, py = rnd.uniform(0, W), rnd.uniform(top + 4, bottom - 3)
        if calm_(px):
            continue
        if rnd.random() < 0.5:
            c.add(f'<ellipse cx="{n(px)}" cy="{n(py)}" rx="{n(4 * k)}" ry="{n(2.6 * k)}" fill="{P.WOOD_DARK}" '
                  f'stroke="{INK}" stroke-width=".6"/>')
            c.line(f"M{n(px - 2 * k)},{n(py - k)} l{n(4 * k)},{n(2 * k)}", 0.6, P.WOOD)
        else:
            r_ = rnd.uniform(4, 9) * k
            c.add(f'<path d="M{n(px - r_)},{n(py)} Q{n(px - r_)},{n(py - r_)} {n(px)},{n(py - r_)} '
                  f'Q{n(px + r_)},{n(py - r_)} {n(px + r_)},{n(py)} Z" fill="{P.STONE}" stroke="{INK}" '
                  f'stroke-width=".8"/><path d="M{n(px - r_ * 0.6)},{n(py - r_ * 0.6)} Q{n(px)},{n(py - r_ * 0.95)} '
                  f'{n(px + r_ * 0.5)},{n(py - r_ * 0.7)}" fill="none" stroke="{P.WHITE}" stroke-opacity=".5" '
                  f'stroke-width="{n(1.4 * k)}"/>')
    rx = rnd.uniform(0.05, 0.25) * W if rnd.random() < 0.5 else rnd.uniform(0.75, 0.95) * W
    c.line(f"M{n(rx)},{n(top + h * 0.3)} q{n(20 * k)},{n(6 * k)} {n(40 * k)},{n(2 * k)} q{n(14 * k)},{n(-3 * k)} "
           f"{n(30 * k)},{n(6 * k)}", max(1.6, 3 * k), mix(P.WOOD, P.WOOD_DARK, 0.5))       # a root
    c.add(f'<rect x="-6" y="{n(bottom - 7 * k)}" width="{W + 12}" height="{n(7 * k)}" rx="{n(3 * k)}" '
          f'fill="{mix(P.WOOD, P.WOOD_DARK, 0.4)}" stroke="{INK}" stroke-width="1"/>')       # the log edging
    c.line(" ".join(f"M{n(q)},{n(bottom - 6 * k)} v{n(5 * k)}" for q in range(40, W, 140)), 1, INK, 0.5)


def forest(c: Canvas, top: float, land: float, k: float, seed: int) -> None:
    """The forest behind the camp, in depth: far pale silhouettes, a row of pines, sunbeams slanting through, and
    here and there a near trunk with its bark."""
    rnd = random.Random(seed + 5)
    x = -20 * k
    while x < W + 30:                                                  # far, pale
        pine(c, x, land - 14 * k, k * rnd.uniform(0.5, 0.65), mix(NEEDLE, SKY_LOW, 0.62), seed=int(x) + 1)
        x += rnd.uniform(14, 24) * k
    x = -10 * k
    while x < W + 30:                                                  # mid
        pine(c, x, land - 6 * k, k * rnd.uniform(0.6, 0.8), calm(darken(NEEDLE, 0.9)), seed=int(x))
        x += rnd.uniform(26, 44) * k
    for _ in range(3):                                                 # sunbeams
        bx = rnd.uniform(0.1, 0.9) * W
        c.add(f'<path d="M{n(bx)},{n(top)} L{n(bx + 30 * k)},{n(top)} L{n(bx + 90 * k)},{n(land)} '
              f'L{n(bx + 40 * k)},{n(land)} Z" fill="{P.YELLOW_PALE}" fill-opacity=".22"/>')
    for q in range(2):                                                 # near trunks, with bark
        tx = (0.04 if q == 0 else 0.96) * W + rnd.uniform(-10, 10)
        c.add(f'<rect x="{n(tx - 7 * k)}" y="{n(top - 4)}" width="{n(14 * k)}" height="{n(land - top + 8)}" '
              f'fill="{mix(P.WOOD, P.TERRACOTTA, 0.35)}" stroke="{INK}" stroke-width="1"/>')
        c.line(" ".join(f"M{n(tx - 5 * k)},{n(top + v * 12 * k)} q{n(5 * k)},{n(3 * k)} {n(10 * k)},0"
                        for v in range(int((land - top) / (12 * k)))), max(0.7, k), P.WOOD_DARK)


def backdrop(s: Strip, index: int) -> None:
    """Behind every station: the summer sky over the pines, the forest and the camp across the clearing, the
    mown meadow, and the plank walkway the cast stands on. In a low frame the cast nearly fills it and the
    professor is left out."""
    ledger(s)
    zoom(s)
    feet = lane(s).feet
    names = ("cat", "agent", "caterpillar") if low(s) else ("professor", "cat", "agent", "caterpillar")
    if low(s):
        top = max(_box(s, name, 0, feet)[3] - _box(s, name, 0, feet)[1] for name in names)
        s.tall *= (feet - 6) / top
    widest = max(_box(s, name, 0, feet)[2] - _box(s, name, 0, feet)[0] for name in names)
    s.tall *= min(1.0, (s.hi - s.lo) * 0.19 / widest)
    s.unit = s.tall / 137
    s.index = index
    s.ceil = 0.0
    c = s.back
    base = s.base
    k = max(0.6, min(1.4, base / 240))
    share = getattr(s, "meadow", 0.62 if s.h < 200 else 0.2)          # a strip: the forest just a band
    s.land = base - max(16.0, base * share)                            # where the camp across stands
    sets.sky(c, SKY_TOP, SKY_LOW, s.land, W)
    rnd = random.Random(index)
    for _ in range(2):                                                 # a couple of clouds
        cx, cy = rnd.uniform(0.1, 0.9) * W, s.land * rnd.uniform(0.2, 0.45)
        c.add(f'<path d="M{n(cx - 40 * k)},{n(cy)} q{n(10 * k)},{n(-16 * k)} {n(26 * k)},{n(-8 * k)} '
              f'q{n(14 * k)},{n(-16 * k)} {n(30 * k)},0 q{n(16 * k)},{n(-4 * k)} {n(24 * k)},{n(8 * k)} Z" '
              f'fill="{P.WHITE}" fill-opacity=".85"/>')
    forest(c, 0, s.land, k, index)
    far_camp(c, s.land, k, index)
    clearing(c, s.land, base + 1, k, index, (s.x(0.3), s.x(0.7)))
    boardwalk(c, -6, W + 6, base, s.h + 4, max(0.8, s.unit))


def far_k(s: Strip, height_: float, tall: float = 1.2) -> float:
    """A building across the clearing: `tall` times the agent at most - it is far off - and under the sky."""
    return min((s.land - 6) / height_, height(s, "agent") * tall / height_)


# ============================================================================ the things near
def key_cabinet(c: Canvas, x: float, foot: float, k: float, taken: bool) -> dict:
    """The leader's key cabinet on its post at (x, foot), 80 wide and 160 tall, the box at chest height: the post
    and its foot, the wooden box with its little roof, its door swung open, the board inside with three rows of
    hooks, a key on a coloured tag on each, the big brass ring in the top row - its hook empty when `taken`.
    Returns its box."""
    d = Canvas()
    d.shape(rounded_rect_d(-5, -84, 10, 84, 2), P.WOOD_DARK, sw=1.2, light=None)
    d.shape(rounded_rect_d(-16, -4, 32, 4, 1), P.WOOD_DARK, sw=1, light=None)
    d.shape("M-46,-154 L0,-168 L46,-154 Z", mix(P.TERRACOTTA, P.WOOD_DARK, 0.5), sw=1.4, light=None)
    d.shape(rounded_rect_d(-40, -154, 80, 72, 3), P.WOOD, sw=1.8, light=(-1, -1))
    d.shape(rounded_rect_d(-35, -149, 70, 62, 1.5), mix(P.WOOD_PALE, P.CARD, 0.5), sw=1, light=None)
    for row in range(3):
        for col in range(5):
            hx, hy = -26 + col * 13, -142 + row * 19
            d.line(f"M{hx - 2},{hy} h4", 1.4, P.METAL_DARK)
            if row == 0 and col == 2:
                if not taken:
                    d.add(f'<circle cx="{hx}" cy="{hy + 7}" r="6" fill="none" stroke="{P.YELLOW}" stroke-width="2.2"/>')
                    d.line(f"M{hx - 3},{hy + 12} l-2,6 M{hx + 3},{hy + 12} l2,6", 1.6, P.YELLOW)
                continue
            d.add(f'<circle cx="{hx}" cy="{hy + 3}" r="2.2" fill="none" stroke="{P.METAL}" stroke-width="1"/>')
            d.line(f"M{hx},{hy + 5} v6 M{hx},{hy + 9} h2", 1.4, P.METAL_LIGHT)                   # the key
            d.shape(rounded_rect_d(hx - 6, hy + 2, 4, 7, 1), (P.ORANGE, P.TEAL, P.CARD, P.PINK, P.GREEN)[col],
                    sw=0.6, light=None)                                                         # its tag
    d.shape("M40,-154 L60,-146 V-90 L40,-82 Z", darken(P.WOOD, 0.9), sw=1.4, light=None)       # its door
    d.add(f'<circle cx="54" cy="-118" r="2" fill="{P.METAL}"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 47 * k, foot - 169 * k, x + 61 * k, foot)}


def keyring(x: float, y: float, k: float) -> str:
    """The leader's keyring held up by its lanyard: the green lanyard through the fist, the big ring with four
    keys hanging below it."""
    c = Canvas()
    c.line("M0,-4 V6", 1.6, PINE)
    c.add(f'<circle cx="0" cy="9" r="3" fill="none" stroke="{P.METAL}" stroke-width="1"/>')
    for q, a in enumerate((-40, -10, 20, 50)):
        r = math.radians(90 + a)
        bx, by = math.cos(r) * 3, 9 + math.sin(r) * 3
        ex, ey = bx + math.cos(r) * 7, by + math.sin(r) * 7
        c.line(f"M{n(bx)},{n(by)} L{n(ex)},{n(ey)}", 1.4, (P.YELLOW, P.METAL_LIGHT, P.YELLOW, P.METAL)[q])
        c.add(f'<circle cx="{n(bx + math.cos(r) * 2)}" cy="{n(by + math.sin(r) * 2)}" r="1.6" '
              f'fill="{(P.YELLOW, P.METAL_LIGHT, P.YELLOW, P.METAL)[q]}" stroke="{INK}" stroke-width=".3"/>')
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def letterbox(c: Canvas, x: float, foot: float, k: float, full: bool) -> dict:
    """The leader's letterbox on its post at (x, foot), 64 wide and 120 tall: the green tin box with its rounded
    lid, its slot, its red flag - up, with notes sticking out of the slot and (`full`) a heap of the agent's notes
    spilled on the boards under it; or down, one short list in the slot. Returns its box."""
    d = Canvas()
    d.shape(rounded_rect_d(-5, -70, 10, 70, 1), P.WOOD_DARK, sw=1.2, light=None)
    d.shape("M-32,-70 V-104 Q-32,-118 -18,-118 H18 Q32,-118 32,-104 V-70 Z", PINE, sw=1.8, light=(-1, -1))
    d.line("M-20,-100 H20", 3, darken(PINE, 0.55))                                                # the slot
    d.line("M-32,-84 H32", 1, darken(PINE, 0.7))
    if full:
        d.line("M32,-100 V-124", 2, P.METAL_DARK)
        d.shape("M32,-124 H46 V-114 H32 Z", P.RED, sw=1, light=None)
        for q, (dx, t_) in enumerate(((-14, -18), (-5, 6), (5, 20), (13, -6), (-1, -10))):
            d.add(f'<g transform="translate({dx},-102) rotate({t_})"><rect x="-6" y="-12" width="12" height="15" '
                  f'fill="{(P.WHITE, P.CARD, P.YELLOW_PALE, P.WHITE, P.CARD)[q]}" stroke="{INK}" stroke-width=".9"/>'
                  f'<path d="M-4,-8 h8 M-4,-5 h6" stroke="{INK}" stroke-width=".6" opacity=".5"/></g>')
        rnd = random.Random(3)
        for q in range(11):                                                                   # spilled on the boards
            px = rnd.uniform(-44, 44)
            t_ = rnd.uniform(-40, 40)
            d.add(f'<g transform="translate({n(px)},{n(-3 - (q % 3) * 3)}) rotate({n(t_)})"><rect x="-7" y="-5" '
                  f'width="14" height="10" fill="{P.WHITE if q % 2 else P.CARD}" stroke="{INK}" stroke-width=".8"/>'
                  f'<path d="M-5,-1 h8 M-5,2 h6" stroke="{INK}" stroke-width=".6" opacity=".5"/></g>')
    else:
        d.line("M32,-86 L44,-86", 2, P.METAL_DARK)
        d.shape("M44,-91 V-81 H50 V-91 Z", P.RED, sw=1, light=None)
        d.add(f'<rect x="-8" y="-114" width="16" height="14" fill="{P.WHITE}" stroke="{INK}" stroke-width="1"/>'
              f'<path d="M-5,-110 h10 M-5,-107 h8 M-5,-104 h9" stroke="{INK}" stroke-width=".7" opacity=".6"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 51 * k, foot - 126 * k, x + 51 * k, foot)}


def siren(c: Canvas, x: float, foot: float, k: float) -> dict:
    """The camp's emergency siren box on its post at (x, foot), 24 wide and 120 tall: the post, the siren horn on
    top, the red box with its big red button under a flip cover. Returns its box and the button."""
    d = Canvas()
    d.shape(rounded_rect_d(-3, -110, 6, 110, 1), P.METAL_DARK, sw=1, light=None)
    d.shape("M-3,-110 L-12,-124 H12 L3,-110 Z", P.METAL_LIGHT, sw=1.2, light=None)               # the horn
    d.shape(rounded_rect_d(-12, -82, 24, 26, 3), P.RED, sw=1.4, light=None)
    d.add(f'<circle cx="0" cy="-69" r="6" fill="{darken(P.RED, 0.75)}" stroke="{INK}" stroke-width="1"/>'
          f'<circle cx="-1.6" cy="-70.6" r="1.6" fill="{P.WHITE}" fill-opacity=".6"/>'
          f'<path d="M-8,-76 L-9,-86 H9 L8,-76" fill="{P.LENS}" fill-opacity=".4" stroke="{INK}" '
          f'stroke-width=".8"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 13 * k, foot - 125 * k, x + 13 * k, foot), "button": (x, foot - 69 * k)}


def fence(c: Canvas, x0: float, x1: float, foot: float, k: float) -> None:
    """A picket fence from x0 to x1 at (foot), 60 high: pointed pickets on two rails, the posts thicker."""
    q = x0
    while q <= x1:
        c.add(f'<path d="M{n(q - 4 * k)},{n(foot)} V{n(foot - 54 * k)} L{n(q)},{n(foot - 60 * k)} '
              f'L{n(q + 4 * k)},{n(foot - 54 * k)} V{n(foot)} Z" fill="{P.WOOD_PALE}" stroke="{INK}" '
              f'stroke-width="1"/>')
        q += 12 * k
    c.line(f"M{n(x0 - 4 * k)},{n(foot - 16 * k)} H{n(x1 + 4 * k)} M{n(x0 - 4 * k)},{n(foot - 44 * k)} "
           f"H{n(x1 + 4 * k)}", 3 * k, P.WOOD)


def sawhorse(c: Canvas, x: float, foot: float, k: float, sawn: bool) -> dict:
    """Two sawhorses at (x, foot), 120 wide and 56 tall at the agent's knee, a plank across them being sawn - its
    sawn end and a heap of sawdust under it when `sawn` - offcuts and a stack of planks behind, a toolbox with a
    hammer. Returns its box."""
    d = Canvas()
    for sx_ in (-44, 34):
        d.line(f"M{sx_ - 10},0 L{sx_},-40 L{sx_ + 10},0 M{sx_ - 6},-14 h12", 3, P.WOOD_DARK)
        d.shape(rounded_rect_d(sx_ - 12, -44, 24, 5, 1), P.WOOD, sw=1, light=None)
    d.shape(rounded_rect_d(-70, -54, 130 if not sawn else 112, 10, 1.5), P.WOOD_LIGHT, sw=1.4, light=None)
    d.line("M-60,-49 h20 M-20,-49 h30", 0.8, P.WOOD, 0.8)
    if sawn:
        d.shape("M48,-4 L62,-8 L64,-2 L50,2 Z", P.WOOD_LIGHT, sw=1, light=None)                  # the offcut
        d.add(f'<path d="M30,0 Q40,-8 50,0 Z" fill="{P.WOOD_PALE}" stroke="{INK}" stroke-width=".6"/>')
    d.shape(rounded_rect_d(-110, -26, 34, 22, 2), P.RED, sw=1.2, light=None)                    # the toolbox
    d.line("M-102,-26 V-32 H-84 V-26", 1.6, P.METAL_DARK)
    d.line("M-100,-30 L-80,-40", 2.2, P.WOOD)
    d.shape(rounded_rect_d(-84, -44, 8, 6, 1), P.METAL_DARK, sw=0.8, light=None)
    c.add(_at(d, x, foot, k))
    return {"box": (x - 111 * k, foot - 56 * k, x + 66 * k, foot)}


def saw(x: float, y: float, k: float) -> str:
    """A handsaw held by its wooden grip, the toothed blade pointing out past the knuckles."""
    c = Canvas()
    c.shape("M-2,-5 H3 V5 H-2 Z", P.WOOD, sw=0.5, light=None)
    c.shape("M3,-4 L24,-1 L24,3 L3,4 Z", P.METAL_LIGHT, sw=0.5, light=None)
    c.line(" ".join(f"M{n(5 + q * 2.2)},4 l1.1,1.2 l1.1,-1.2" for q in range(9)), 0.4, INK)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def hammer(x: float, y: float, k: float) -> str:
    """A hammer held by its handle, its head up over the thumb."""
    c = Canvas()
    c.shape(rounded_rect_d(-1.2, -10, 2.4, 16, 1), P.WOOD, sw=0.5, light=None)
    c.shape(rounded_rect_d(-5, -14, 10, 4.4, 1), P.METAL_DARK, sw=0.5, light=None)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def mug(x: float, y: float, k: float) -> str:
    """The cat's enamel camp mug: white enamel with a blue rim, chipped, its handle in the fist."""
    c = Canvas()
    c.shape(rounded_rect_d(2, -7, 9, 10, 1.5), P.WHITE, sw=0.6, light=None)
    c.line("M2,-6.4 H11", 1, P.BLUE)
    c.add(f'<circle cx="8" cy="0" r=".9" fill="{INK}" fill-opacity=".6"/>')
    c.line("M2,-4 Q-1,-2 2,1", 0.9, INK)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def check_table(c: Canvas, x: float, foot: float, k: float, opened: bool) -> dict:
    """The sentry's trestle table at (x, foot), 110 wide and 46 high at the agent's waist: on it the parcel - a
    cardboard box with its tape and a courier label - shut, or (`opened`) its flaps open, packing straw, and out of
    it a strange gadget: a black box with a stubby antenna, a blinking red light and wires. Returns its box."""
    d = Canvas()
    d.line("M-44,0 L-34,-46 M-24,0 L-34,-46 M44,0 L34,-46 M24,0 L34,-46", 2.6, P.WOOD_DARK)
    d.shape(rounded_rect_d(-55, -50, 110, 6, 1.5), P.WOOD, sw=1.4, light=None)
    box = mix(P.WOOD_PALE, P.SAND, 0.5)
    d.shape(rounded_rect_d(-46, -86, 60, 36, 1.5), box, sw=1.6, light=(-1, -1))                # the parcel
    d.shape(rounded_rect_d(-40, -78, 26, 13, 1), P.WHITE, sw=0.9, light=None)                 # its label
    d.line("M-37,-73 h18 M-37,-69 h12", 0.8, INK, 0.6)
    if opened:
        d.shape("M-46,-86 L-56,-96 L-38,-92 Z", box, sw=1.2, light=None)
        d.shape("M14,-86 L26,-96 L6,-92 Z", box, sw=1.2, light=None)
        d.line("M-38,-88 l5,-4 M-24,-89 l4,-5 M-10,-88 l5,-4 M2,-89 l4,-4", 1.2, P.YELLOW_PALE)
        d.shape(rounded_rect_d(20, -78, 32, 24, 3), P.CHARCOAL, sw=1.4, light=None)              # the gadget
        d.shape(rounded_rect_d(24, -74, 14, 8, 1), mix(P.GREEN, P.SCREEN, 0.5), sw=0.6, light=None)
        d.line("M46,-78 V-94", 1.8, P.METAL_DARK)
        d.add(f'<circle cx="46" cy="-95" r="2.2" fill="{P.METAL}"/>'
              f'<circle cx="44" cy="-62" r="3" fill="{P.RED}"/><circle cx="44" cy="-62" r="6" fill="{P.RED}" '
              f'fill-opacity=".3"/>')
        d.line("M52,-60 q8,0 8,8 M52,-57 q5,5 0,6", 1.2, P.RED)
    else:
        d.line("M-16,-86 V-50", 4, mix(P.SAND, P.WOOD, 0.5))
    c.add(_at(d, x, foot, k))
    return {"box": (x - 57 * k, foot - 97 * k, x + 61 * k, foot)}


def notice_board(c: Canvas, x: float, foot: float, k: float) -> dict:
    """The notice board outside the fence at (x, foot), 90 wide and 150 tall: two posts, a little shingled roof,
    the cork board with old notices pinned to it, and in the middle a new note. Returns its box and the note's
    place."""
    d = Canvas()
    d.line("M-36,0 V-140 M36,0 V-140", 4, P.WOOD_DARK)
    d.shape("M-48,-136 L0,-152 L48,-136 Z", mix(P.TERRACOTTA, P.WOOD_DARK, 0.5), sw=1.2, light=None)
    d.shape(rounded_rect_d(-42, -132, 84, 66, 2), P.WOOD, sw=1.4, light=None)
    d.shape(rounded_rect_d(-38, -128, 76, 58, 1), mix(P.WOOD_PALE, P.ORANGE, 0.25), sw=0.8, light=None)
    for px, py in ((-37, -126), (25, -90)):                                                   # old notices
        d.shape(rounded_rect_d(px, py, 12, 14, 1), P.CARD, sw=0.6, light=None)
        d.line(f"M{px + 2},{py + 4} h8 M{px + 2},{py + 8} h6", 0.6, INK, 0.5)
    d.add(f'<circle cx="0" cy="-124" r="2" fill="{P.RED}"/>')                                 # the new note's pin
    c.add(_at(d, x, foot, k))
    return {"box": (x - 49 * k, foot - 153 * k, x + 49 * k, foot), "note": (x, foot - 99 * k, 52 * k)}


def practice_tent(c: Canvas, x: float, foot: float, k: float, up: bool) -> dict:
    """A small dome tent on the practice ground at (x, foot), 120 wide and 64 tall: pitched - its two crossing
    poles, the orange flysheet, the zipped door, guy lines to pegs - or being struck: one pole pulled out and
    lying on the ground, the dome slumped lopsided over the other with its door still on it, a guy line gone
    slack, the tent's stuff sack standing beside, its drawstring open for it. Returns its box."""
    d = Canvas()
    if up:
        d.shape("M-56,0 Q-50,-62 0,-64 Q50,-62 56,0 Z", P.ORANGE, sw=1.8, light=(-1, -1))
        d.line("M-56,0 Q-20,-70 30,-60 M56,0 Q20,-70 -30,-60", 1.4, darken(P.ORANGE, 0.7))
        d.shape("M-16,0 Q-14,-38 0,-40 Q14,-38 16,0 Z", darken(P.ORANGE, 0.65), sw=1.2, light=None)
        d.line("M0,-40 V0", 1, P.METAL_LIGHT)
        for side in (-1, 1):
            d.line(f"M{side * 40},-40 L{side * 70},0", 0.9, INK, 0.6)
            d.line(f"M{side * 70},0 v-6", 1.6, P.METAL_DARK)
    else:
        d.line("M-52,-30 Q-62,-12 -68,0", 0.9, INK, 0.6)                                        # slack guy line
        d.line("M-68,0 v-6", 1.6, P.METAL_DARK)
        d.shape("M-60,0 Q-56,-50 -24,-50 Q-4,-48 0,-36 Q4,-24 14,-20 Q30,-14 38,0 Z", P.ORANGE, sw=1.8, light=(-1, -1))
        d.line("M-60,0 Q-56,-50 -24,-50", 1.4, darken(P.ORANGE, 0.7))                             # the pole left
        d.line("M-8,-46 Q-2,-34 4,-22 M-42,-42 Q-38,-28 -40,-14 M6,-22 Q18,-12 22,-2 M14,-20 Q24,-12 30,-4", 1,
               darken(P.ORANGE, 0.75))
        d.shape("M-32,0 Q-30,-30 -18,-32 Q-6,-28 -4,0 Z", darken(P.ORANGE, 0.65), sw=1.2, light=None)  # the door
        d.line("M-18,-32 V0", 1, P.METAL_LIGHT)
        d.shape(rounded_rect_d(44, -36, 26, 36, 7), PINE, sw=1.4, light=(-1, -1))                 # the stuff sack
        d.shape("M44,-30 Q46,-40 57,-40 Q68,-40 70,-30 Z", darken(PINE, 0.7), sw=1.2, light=None)  # its open mouth
        d.line("M50,-33 Q47,-26 49,-20 M64,-33 Q67,-26 65,-20", 1.2, P.WHITE)                  # the drawstring
        d.line("M44,-8 H70", 1, INK, 0.4)
        d.line("M-54,-2 Q-10,-6 40,-2", 2.2, P.METAL_DARK)                                         # the pole pulled
        for jx in (-30, -6, 18):
            d.line(f"M{jx},-{3.4 if jx != -6 else 4.2} h3", 3, P.METAL_LIGHT)
    c.add(_at(d, x, foot, k))
    return {"box": (x - 71 * k, foot - (65 if up else 52) * k, x + 71 * k, foot)}


def chest(c: Canvas, x: float, foot: float, k: float, open_: bool) -> dict:
    """The supply chest at (x, foot), 100 wide and 56 tall, waist high to the agent: planks bound with iron bands
    and corner plates, two side handles, the hasp with a big brass padlock through it - or (`open_`) the lid up
    and the padlock hanging open, tins and sacks inside. Returns its box and the padlock's place."""
    d = Canvas()
    d.shape(rounded_rect_d(-50, -44, 100, 44, 2), P.WOOD, sw=1.6, light=(-1, -1))
    d.line("M-50,-30 H50 M-50,-16 H50", 1, P.WOOD_DARK)
    for bx in (-36, 36):
        d.shape(rounded_rect_d(bx - 4, -44, 8, 44, 1), P.METAL_DARK, sw=0.8, light=None)
    for hx in (-50, 50):
        d.line(f"M{hx},-30 h{-6 if hx < 0 else 6} v8 h{6 if hx < 0 else -6}", 2, P.METAL_DARK)
    if open_:
        d.shape("M-50,-44 L-46,-78 H54 L50,-44 Z", darken(P.WOOD, 0.85), sw=1.4, light=None)    # the lid up
        d.shape(rounded_rect_d(-34, -54, 16, 12, 2), P.METAL_LIGHT, sw=0.8, light=None)
        d.shape("M-10,-44 Q-12,-58 0,-58 Q12,-58 10,-44 Z", mix(P.SAND, P.WOOD, 0.4), sw=0.8, light=None)
        d.shape(rounded_rect_d(18, -52, 16, 10, 2), P.RED, sw=0.8, light=None)
        d.add(f'<path d="M-4,-36 a5,5 0 0 1 10,0" fill="none" stroke="{P.METAL_DARK}" stroke-width="2"/>')
        d.shape(rounded_rect_d(-6, -32, 14, 12, 2), mix(P.YELLOW, P.ORANGE, 0.3), sw=1, light=None)
    else:
        d.shape(rounded_rect_d(-52, -56, 104, 14, 3), darken(P.WOOD, 0.9), sw=1.6, light=None)  # the lid
        d.shape(rounded_rect_d(-6, -50, 12, 16, 1), P.METAL_DARK, sw=0.8, light=None)          # the hasp
        d.add(f'<path d="M-7,-34 a7,7 0 0 1 14,0 v3" fill="none" stroke="{P.METAL_DARK}" stroke-width="3"/>')
        d.shape(rounded_rect_d(-11, -32, 22, 20, 3), mix(P.YELLOW, P.ORANGE, 0.3), sw=1.4, light=(-1, -1))
        d.add(f'<circle cx="0" cy="-24" r="2.2" fill="{INK}"/><path d="M0,-23 v5" stroke="{INK}" '
              f'stroke-width="1.6"/>')
    c.add(_at(d, x, foot, k))
    top = 78 if open_ else 57
    return {"box": (x - 57 * k, foot - top * k, x + 57 * k, foot), "lock": (x, foot - 22 * k)}


def plan_table(c: Canvas, x: float, foot: float, k: float, packed: bool) -> dict:
    """The camp table at (x, foot), 130 wide and 46 high: the map spread on it, held down by stones, a route
    drawn on it in red with its steps; the list of risks on a clipboard beside it; under the table the backup
    crate with a spare canister - packed and strapped when `packed`, open and empty if not. Returns its box."""
    d = Canvas()
    d.line("M-58,0 V-44 M58,0 V-44 M-52,0 V-44 M52,0 V-44", 3, P.WOOD_DARK)
    d.shape(rounded_rect_d(-66, -50, 132, 7, 2), P.WOOD, sw=1.4, light=None)
    d.shape("M-50,-50 L-44,-56 H34 L40,-50 Z", P.CARD, sw=1, light=None)                         # the map
    d.line("M-36,-52 Q-20,-56 -6,-53 T26,-54", 1.4, P.RED)
    d.line("M-30,-53.6 l2,0 M-12,-54 l2,0 M8,-53.4 l2,0", 2, P.RED)
    d.line("M-40,-51 Q-30,-54 -18,-52 M10,-55 Q20,-52 30,-55", 1, PINE, 0.7)
    for sx_ in (-46, 34):
        d.add(f'<ellipse cx="{sx_}" cy="-55" rx="4" ry="2.4" fill="{P.STONE}" stroke="{INK}" stroke-width=".7"/>')
    d.shape(rounded_rect_d(46, -66, 16, 20, 1), P.WOOD, sw=1, light=None)                        # the risks
    d.shape(rounded_rect_d(48, -62, 12, 15, 0.5), P.WHITE, sw=0.6, light=None)
    d.line("M50,-58 h8 M50,-55 h6 M50,-52 h8", 0.7, P.RED)
    d.shape(rounded_rect_d(-34, -30, 52, 30, 2), mix(PINE, P.WOOD, 0.4), sw=1.4, light=None)      # the crate
    d.line("M-34,-20 H18", 1, INK, 0.4)
    if packed:
        d.shape(rounded_rect_d(-22, -48, 22, 22, 2), P.RED, sw=1.2, light=None)                  # the canister
        d.shape(rounded_rect_d(-8, -54, 6, 6, 1), P.CHARCOAL, sw=0.6, light=None)
        d.line("M-22,-38 h22", 1, darken(P.RED, 0.7))
        d.line("M-34,-14 H18 M-10,-30 V0", 2, P.YELLOW)                                           # its strap
    c.add(_at(d, x, foot, k))
    return {"box": (x - 67 * k, foot - 67 * k, x + 67 * k, foot)}


# ============================================================================ framing a station
def _framed(draw):
    """A station drawn as it is or mirrored, by turns; the next visit of the moment brings the camera a step
    nearer. After it: the sparrow on its perch if the station offers one (every other page)."""
    def run(s: Strip, beat: str) -> None:
        s.again = (s.seed // 2) % 2 == 1
        s.mirror = bool(s.shot) != s.again
        s.near = 1.12 if s.again else 1.0
        s.perch = None
        draw(s, beat)
        if s.perch and s.seed % 2 == 0 and not any(b.name == "sparrow" for b in s.boxes):
            x, top, group = s.perch
            sparrow_on(s, x, top, group)
    return run


def crowd(s: Strip, box: tuple, who: tuple[tuple, ...]) -> None:
    """The station's cast beside its box; in a close-up a third one joins them, close by, so the strip is full of
    the station and its people rather than of empty boards."""
    names = [w[0] for w in who if not (w[0] == "professor" and low(s))]
    extra = ()
    if low(s):
        spare = [x for x in ("caterpillar", "cat", "agent") if x not in names]
        if len(names) < 3 and spare:
            side = who[-1][1]
            third = spare[-1] if len(spare) > 1 and "professor" in (w[0] for w in who) else spare[0]
            hold = mug if third == "cat" else checklist(mates(s)) if third == "caterpillar" else None
            extra = ((third, side, "think", "smile", hold),)
    cast(s, box, tuple(who) + extra)


def siren_joke(s: Strip, mode: str) -> None:
    """The running joke: the camp's siren post at the edge of the frame, its red button under a flip cover -
    "reach": the sparrow flutters up to it; "stopped": the cover still shut, the sparrow sitting at the post's
    foot, caught. Only where the boards are free."""
    r = lane(s)
    k = agent_k(s, 125, 1.0)
    for f in (0.04, 0.96, 0.12, 0.88):
        c = Canvas()
        sb = siren(c, s.x(f), r.feet, k)
        bx = sb["box"]
        bird = _box(s, "sparrow", 0, r.feet, 0.5)
        bw, bh = bird[2] - bird[0], bird[3] - bird[1]
        way = 1 if f < 0.5 else -1
        if mode == "reach":
            bb = (min(bx[2], bx[2] + way * bw * 1.6) if way > 0 else bx[0] - bw * 1.6, sb["button"][1] - bh * 0.7,
                  bx[2] + bw * 1.6 if way > 0 else bx[0], sb["button"][1] + bh * 0.4)
        else:
            bb = ((bx[2], r.feet - bh, bx[2] + bw * 1.2, r.feet) if way > 0
                  else (bx[0] - bw * 1.2, r.feet - bh, bx[0], r.feet))
        whole = (min(bx[0], bb[0]), min(bx[1], bb[1]), max(bx[2], bb[2]), bx[3])
        if whole[0] < 4 or whole[2] > W - 4 or whole[1] < 2 or not s.free(whole, 6):
            continue
        s.put(r.feet - 1, c.render(), bx, "siren", group="siren")
        if mode == "reach":
            s.actor("sparrow", (bb[0] + bb[2]) / 2, sb["button"][1] + bh * 0.4, "fly", "smile", flip=way > 0,
                    tall=s.tall * SIZE["sparrow"] * 0.5, group="siren")
        else:
            s.actor("sparrow", (bb[0] + bb[2]) / 2, r.feet, "shrug", "worry", flip=way < 0,
                    tall=s.tall * SIZE["sparrow"] * 0.5, group="siren")
        return


def agent_k(s: Strip, height_: float, share: float) -> float:
    """A thing `height_` tall standing `share` of the agent's height."""
    return height(s, "agent") * share / height_


def building(s: Strip, kind: str, at: float) -> tuple | None:
    """A building of the station across the clearing at `at` of the frame, at its distance; its box (page space)
    so the view to it is kept clear. None in a low frame (the camp across is too small to point at there)."""
    if low(s):
        return None
    far = Canvas()
    if kind == "gate":
        b = gate(far, s.x(at), s.land, far_k(s, 151, 0.75))["box"]
    else:
        b = cabin(far, s.x(at), s.land, far_k(s, 151, 0.62), kind)["box"]
    across(s, far)
    if getattr(s, "mirror", False):
        b = (fx(s, b[2]), b[1], fx(s, b[0]), b[3])
    return b


def span(box: tuple, far_box: tuple | None) -> tuple:
    """The station's box widened up to the building across, so nothing stands in the view to it."""
    if not far_box:
        return box
    return (min(box[0], far_box[0]), min(box[1], far_box[1]), max(box[2], far_box[2]), box[3])


# ============================================================================ the stations
def keys_station(s: Strip, beat: str) -> None:
    """The agent works in your name: at the leader's key cabinet by his cabin, the cabinet open; "give": the
    leader hands the agent his keyring on its lanyard; "wear": the leader's hook empty, the agent with the keyring
    - the cat with his camp mug watching."""
    r = lane(s)
    k = agent_k(s, 169, 1.1)
    c = Canvas()
    kc = key_cabinet(c, s.x(0.48), r.feet, k, taken=beat == "wear" or not low(s))
    box = place(s, c, kc["box"], "keys")
    far_box = building(s, "leader", 0.28)
    box = span(box, far_box)
    if beat == "give" and low(s):                                     # the leader's ring still on its hook
        crowd(s, box, (("agent", -1, "point", "smile", None),
                      ("caterpillar", 1, "present", "smile", checklist(mates(s)))))
    elif beat == "give":
        crowd(s, box, (("professor", 1, "present", "smile", keyring), ("agent", -1, "wave", "smile", None)))
    else:
        cast(s, box, (("agent", -1, "present", "smile", keyring), ("cat", 1, "think", "smile", mug)))
    perch(s, s.x(0.48), kc["box"][1] + 4, "keys")


def knock_station(s: Strip, beat: str) -> None:
    """Few requests, but to the point: the leader's letterbox by his cabin. "knock": it is stuffed and its flag
    up, the agent's notes - one a minute - heaped on the boards under it, the caterpillar dismayed; "list": one
    short list in it, the leader signs it once with his pencil, and the sparrow has his eye on the siren's red
    button."""
    r = lane(s)
    k = agent_k(s, 126, 1.05)
    c = Canvas()
    lb = letterbox(c, s.x(0.5), r.feet, k, full=beat == "knock")
    box = place(s, c, lb["box"], "letterbox")
    box = span(box, building(s, "leader", 0.72))
    if beat == "knock":
        crowd(s, box, (("agent", -1, "present", "smile", handheld.card), ("cat", 1, "think", "worry", mug)))
    else:
        crowd(s, box, (("professor", 1, "present", "smile", handheld.pencil), ("agent", -1, "present", "smile",
                                                                              handheld.clipboard)))
        siren_joke(s, "reach")


def sandbox_station(s: Strip, beat: str) -> None:
    """The sandbox: the woodworking yard inside its picket fence; the agent works in it without asking anyone -
    "saw": sawing a plank on the sawhorses; "hammer": the plank sawn through, the agent with its hammer - the cat
    watching from outside the fence."""
    r = lane(s)
    k = agent_k(s, 56, 0.48)
    fk = agent_k(s, 60, 0.55)
    c = Canvas()
    x = s.x(0.5)
    back = Canvas()                                                   # the yard's fence, behind its sawhorses
    x0_, x1_ = x - 120 * k, x + 76 * k
    fence(back, x0_, x1_, r.feet - 10 * k, fk)
    sh = sawhorse(c, x, r.feet, k, sawn=beat == "hammer")
    across(s, back)
    box = place(s, c, (x0_ - 6, min(sh["box"][1], r.feet - 10 * k - 60 * fk), x1_ + 6, r.feet), "yard")
    (crowd if beat == "saw" else cast)(s, box, (("agent", 1, "present", "smile", saw if beat == "saw" else hammer),
                  ("cat" if beat == "saw" else "caterpillar", -1, "think", "smile",
                   mug if beat == "saw" else checklist(mates(s)))))
    if beat == "hammer":
        siren_joke(s, "stopped")
    else:
        perch(s, fx(s, sh["box"][0] + 20 * k), r.feet - 26 * k, "yard")


def parcel_station(s: Strip, beat: str) -> None:
    """Other people's code: a parcel delivered at the camp gate - "arrive": on the sentry's table, still shut,
    the agent eager to open it; "check": the sentry - the cat - has it open with his magnifier: a strange gadget
    with a blinking light and wires that would run inside the camp."""
    r = lane(s)
    k = agent_k(s, 50, 0.52)
    c = Canvas()
    ct = check_table(c, s.x(0.5), r.feet, k, opened=beat == "check")
    box = place(s, c, ct["box"], "gate")
    box = span(box, building(s, "gate", 0.26))
    if beat == "arrive":
        crowd(s, box, (("agent", -1, "point", "smile", None), ("cat", 1, "think", "smile", mug)))
    else:
        cast(s, box, (("cat", 1, "present", "smile", handheld.magnifier),
                      ("caterpillar", -1, "think", "worry", checklist(mates(s)))))


def note_station(s: Strip, beat: str) -> None:
    """Other people's text: the notice board outside the camp's fence, a new note pinned to it - "open the store".
    "read": the agent reads it and does not move, the caterpillar holds up the leader's real note on its card;
    "ignore": the agent has turned its back on it, the cat nods."""
    r = lane(s)
    k = agent_k(s, 153, 1.15)
    c = Canvas()
    nb = notice_board(c, s.x(0.5), r.feet, k)
    box = place(s, c, nb["box"], "board")
    nx, ny, nw = nb["note"]                                           # the note's words, inside its margins
    nx = fx(s, nx)
    pen = Pen(s, nx - nw * 0.5, ny - nw * 0.44, 1)
    w_, h_ = nw, nw * 0.88
    note = pen.container("note", 0, 0, w_, h_, P.WHITE, radius=1, sw=1, light=None)
    pad = pen.pad(w_, h_)
    size = max(sets.LETTERING_MIN, min(14.0, (h_ - 2 * pad) * 0.3))
    pen.c.add(lettering(w_ / 2, h_ * 0.42, s.word("note1"), size, INK, room=w_ - 2 * pad, style="label")
              + lettering(w_ / 2, h_ * 0.42 + size * 1.15, s.word("note2"), size, P.RED, room=w_ - 2 * pad,
                          style="label"))
    pen.child(note, "words", pad, h_ * 0.42 - size, w_ - pad, h_ * 0.42 + size * 1.3)
    s.put(r.feet - 0.5, pen.svg(), None)
    if beat == "read":
        crowd(s, box, (("agent", -1, "think", "smile", None),
                      ("caterpillar", 1, "present", "smile", lambda x_, y_, kk: handheld.card(x_, y_, kk, PINE))))
    else:
        cast(s, box, (("agent", -1, "shrug", "smile", None), ("cat", 1, "think", "smile", mug)))


def practice_station(s: Strip, beat: str) -> None:
    """Dev, staging and preview: the practice ground behind the camp - "pitch": the agent has pitched the practice
    tent on its own; "strike": the agent is taking it down again, one pole out and the stuff sack open beside it -
    the caterpillar ticks it off."""
    r = lane(s)
    k = agent_k(s, 65, 0.85)
    c = Canvas()
    tn = practice_tent(c, s.x(0.5), r.feet, k, up=beat == "pitch")
    box = place(s, c, tn["box"], "ground")
    if beat == "pitch":
        crowd(s, box, (("agent", -1, "cheer", "smile", None), ("cat", 1, "think", "smile", mug)))
    else:
        cast(s, box, (("agent", -1, "present", "smile", None),
                      ("caterpillar", 1, "present", "smile", checklist(mates(s)))))
    if beat == "pitch":
        siren_joke(s, "reach")
    else:
        perch(s, fx(s, s.x(0.5) + 57 * k), r.feet - 38 * k, "ground")


def store_station(s: Strip, beat: str) -> None:
    """Production: the supply chest by the store, under its padlock. "ask": the agent brings its request card to
    the leader (the cat in a low frame); "open": the leader has decided - the padlock hangs open, the lid up on the
    supplies."""
    r = lane(s)
    k = agent_k(s, 57, 0.55)
    c = Canvas()
    ch = chest(c, s.x(0.5), r.feet, k, open_=beat == "open")
    box = place(s, c, ch["box"], "chest")
    box = span(box, building(s, "store", 0.74))
    if beat == "ask":
        crowd(s, box, (("agent", -1, "present", "smile", lambda x_, y_, kk: handheld.card(x_, y_, kk, P.YELLOW)),
                      ("professor", 1, "think", "smile", None)))
    else:
        cast(s, box, (("professor", 1, "present", "smile", keyring), ("caterpillar", -1, "cheer", "smile", None)))


def plan_station(s: Strip, beat: str) -> None:
    """Before your "yes": at the camp table the agent lays it all out - "plan": the map with the route in red and
    the list of risks beside it, the backup crate open and empty; "packed": the spare canister packed and strapped
    in the backup crate - the leader (the cat in a low frame) looks it over."""
    r = lane(s)
    k = agent_k(s, 67, 0.62)
    c = Canvas()
    pt = plan_table(c, s.x(0.5), r.feet, k, packed=beat == "packed")
    box = place(s, c, pt["box"], "table")
    if beat == "plan":
        crowd(s, box, (("agent", -1, "point", "smile", None), ("professor", 1, "think", "smile", None)))
    else:
        cast(s, box, (("agent", -1, "present", "smile", None), ("cat", 1, "think", "smile", mug)))
    perch(s, fx(s, s.x(0.5) - 20 * k), pt["box"][1] + 12 * k, "table")


def test_station(s: Strip, beat: str) -> None:
    """Checking that the protection works: a drill at the supply chest - "try": the sparrow tugs at the padlock
    with all his might; "stopped": the padlock held, the sparrow sits on the boards, the sentry - the cat - shows
    his stopwatch."""
    r = lane(s)
    k = agent_k(s, 57, 0.55)
    c = Canvas()
    ch = chest(c, s.x(0.5), r.feet, k, open_=False)
    box = place(s, c, ch["box"], "chest")
    lx, ly = ch["lock"]
    bird = _box(s, "sparrow", 0, r.feet, 0.5)
    bh = bird[3] - bird[1]
    if beat == "try":
        bw = bird[2] - bird[0]                 # beside the padlock, his wing on it: in front of it, he hid it
        s.actor("sparrow", fx(s, lx) + (bw * 0.62 + 9 * k) * (-1 if getattr(s, "mirror", False) else 1),
                ly + bh * 0.55, "point", "surprise", flip=not getattr(s, "mirror", False),
                tall=s.tall * SIZE["sparrow"] * 0.5, group="chest", depth=r.feet + 0.4)
        crowd(s, box, (("cat", 1, "present", "smile", handheld.stopwatch), ("agent", -1, "think", "smile", None)))
    else:
        side = -1 if getattr(s, "mirror", False) else 1        # on the boards by the chest, clear of its corner
        s.actor("sparrow", fx(s, lx) + side * ((box[2] - box[0]) / 2 + (bird[2] - bird[0]) * 0.55 + 4), r.feet,
                "shrug", "worry", flip=side < 0,
                tall=s.tall * SIZE["sparrow"] * 0.5, group="chest", depth=r.feet + 0.4)
        cast(s, box, (("cat", 1, "present", "smile", handheld.stopwatch),
                      ("caterpillar", -1, "cheer", "smile", checklist(mates(s)))))


# ============================================================================ the finale
BAYS = ("keys", "knock", "sandbox", "parcel", "note", "practice", "store", "plan", "test")


def finale(s: Strip) -> None:
    """The whole camp at once, built up its slope in terraces under the pines - two, or three in a tall frame -
    each on its log wall, the stations along them and the last of them on the walkway in front with the cast: the
    key cabinet, the letterbox, the yard's sawhorses behind their fence, the sentry's table with the parcel, the
    notice board, the practice tent, the supply chest, the camp table and the drill at the chest - all at one scale
    and filling the frame's height, each with its name on a plaque right over it."""
    backdrop(s, 3)
    r = lane(s)
    left, right = s.lo, s.hi
    span_ = right - left
    named = s.h >= 300
    size = 11.0 if named else 9.0
    th = tag_size("Ag", size)[1]
    pen = Pen(s, 0, 0, 1)
    things = Canvas()
    feet = r.feet
    dims = {"keys": (108, 169, 1.1), "knock": (102, 126, 1.05), "sandbox": (177, 70, 0.62),
            "parcel": (120, 117, 0.62), "note": (98, 153, 1.15), "practice": (142, 65, 0.85),
            "store": (114, 57, 0.55), "plan": (134, 67, 0.62), "test": (114, 57, 0.55)}
    a0 = height(s, "agent")
    cast_ = ("cat", "agent", "caterpillar") if low(s) else ("professor", "cat", "agent", "caterpillar")
    wide = {name: (_box(s, name, 0, feet)[2] - _box(s, name, 0, feet)[0]) / a0 for name in cast_}
    groups = ((BAYS[:3], BAYS[3:6], BAYS[6:]) if s.h >= 500 else (BAYS[:5], BAYS[5:])) if named else (BAYS[:5],)
    if len(groups) == 3:                                               # the cast along all three terraces
        crew = {0: ("professor",), 1: ("cat",), 2: ("agent", "caterpillar")}
    else:
        crew = {len(groups) - 1: cast_}
    a = a0 * 1.3                                                       # one scale: as the widths let it be
    talls = []
    for gi, keys in enumerate(groups):
        mine = crew.get(gi, ())
        widths = [dims[k_][0] * dims[k_][2] / dims[k_][1] for k_ in keys] + [wide[x] for x in mine]
        a = min(a, (span_ - 14 * (len(widths) + 1)) / sum(widths))
        talls.append(max([dims[k_][2] for k_ in keys] + ([1.3] if mine else [])))
    gap = (th + 22) if named else 8
    a = min(a, (feet - 24 - gap * len(groups)) / sum(talls))           # the tiers take the frame's height
    floors = [feet]
    for gi in range(len(groups) - 1, 0, -1):                           # each tier just over the one in front
        floors.insert(0, floors[0] - talls[gi] * a - gap)
    rows = tuple(zip(groups, floors, strict=True))
    for gi in range(len(groups) - 1):                                  # the terraces and their log walls
        top_, below = floors[gi], (floors[gi + 1] if gi + 1 < len(groups) - 1 else s.base) + 2
        terr = Canvas()
        boardwalk(terr, -6, W + 6, top_, top_ + 14, max(0.8, s.unit))
        y, q = top_ + 14, 0
        while y < below:
            lh = 13.0
            terr.add(f'<rect x="-6" y="{n(y)}" width="{W + 12}" height="{n(min(lh, below - y))}" rx="6" '
                     f'fill="{LOG if q % 2 else darken(LOG, 0.92)}" stroke="{INK}" stroke-width="1"/>')
            terr.line(" ".join(f"M{n(v)},{n(y + 3)} q4,{n(lh / 2 - 3)} 0,{n(lh - 6)}"
                               for v in range(60 + q * 37 % 90, W, 170)), 1, P.WOOD_DARK, 0.6)
            y += lh
            q += 1
        for v in range(40 + gi * 70, W, 210):                          # the wall's posts
            terr.add(f'<rect x="{v - 6}" y="{n(top_ + 8)}" width="12" height="{n(below - top_ - 8)}" '
                     f'fill="{P.WOOD}" stroke="{INK}" stroke-width="1.2"/>')
        s.put(0.6 + gi * 0.01, terr.render(), None)
    tops = {}
    for ri, (keys, floor) in enumerate(rows):
        mine = crew.get(ri, ())
        last = bool(mine)
        items = [x for pair in zip(mine, keys, strict=False) for x in pair] + list(keys[len(mine):]) \
            + list(mine[len(keys):])
        widths = [wide[x] if x in wide else dims[x][0] * dims[x][2] / dims[x][1] for x in items]
        spare = (span_ - a * sum(widths)) / (len(items) + 1)
        x = left + spare
        for key, w in zip(items, widths, strict=True):
            mx = x + a * w / 2
            x += a * w + spare
            if key in wide:
                who = s.actor(key, mx, floor, {"professor": "think", "cat": "present", "agent": "point",
                                                "caterpillar": "present"}[key], "smile", flip=True,
                              tall=s.tall * SIZE[key] * a / a0, group=f"f{key}")
                if key == "cat":
                    s.hold(who, mug)
                elif key == "caterpillar":
                    s.hold(who, checklist(9))
                continue
            k = a * dims[key][2] / dims[key][1]
            if key == "keys":
                key_cabinet(things, mx - 7 * k, floor, k, False)
            elif key == "knock":
                letterbox(things, mx, floor, k, True)
            elif key == "sandbox":
                fence(things, mx - 80 * k, mx + 70 * k, floor - 8 * k, k * 0.95)
                sawhorse(things, mx + 20 * k, floor, k, True)
            elif key == "parcel":
                check_table(things, mx, floor, k, True)
            elif key == "note":
                notice_board(things, mx, floor, k)
            elif key == "practice":
                practice_tent(things, mx, floor, k, True)
            elif key == "store":
                chest(things, mx, floor, k, True)
            elif key == "plan":
                plan_table(things, mx, floor, k, True)
            else:
                chest(things, mx, floor, k, False)
            over = dims[key][2] if not last else max(dims[key][2], 1.25)   # over the cast's heads too
            tops[key] = (mx, floor - a * over - 4, ri)
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
            holder = pen.tag(f"label{key}", x, y, s.word(key), size, mix(PINE, P.CARD, 0.6), INK)
            s.put(2, "", holder.outer, f"label{key}")
        s.put(2, pen.svg(), None)


# ============================================================================ the opener
def fire(c: Canvas, x: float, foot: float, k: float) -> dict:
    """The big campfire at (x, foot), 160 wide: a ring of stones, the logs stacked in a cone, the flames in three
    tongues - red, orange, yellow - the glow round it, sparks rising and a ribbon of smoke. Returns its box."""
    d = Canvas()
    d.add(f'<ellipse cx="0" cy="-30" rx="150" ry="70" fill="{P.SUN}" fill-opacity=".18"/>')
    d.add(f'<ellipse cx="0" cy="-2" rx="78" ry="16" fill="{darken(P.WOOD_DARK, 0.7)}"/>')
    for q in range(11):                                                                        # the stone ring
        a = math.radians(q * 360 / 11)
        sx_, sy_ = math.cos(a) * 74, math.sin(a) * 13
        d.shape(f"M{n(sx_ - 11)},{n(sy_)} Q{n(sx_ - 10)},{n(sy_ - 12)} {n(sx_)},{n(sy_ - 12)} "
                f"Q{n(sx_ + 10)},{n(sy_ - 12)} {n(sx_ + 11)},{n(sy_)} Z", P.STONE if q % 2 else darken(P.STONE, 0.88),
                sw=1.2, light=None)
    for a in (-60, -30, 0, 30, 60):                                                            # the logs
        d.add(f'<g transform="rotate({a} 0 -10)"><rect x="-5" y="-62" width="10" height="56" rx="4" '
              f'fill="{P.WOOD_DARK}" stroke="{INK}" stroke-width="1.4"/><ellipse cx="0" cy="-62" rx="5" ry="2.4" '
              f'fill="{P.WOOD_PALE}"/></g>')
    for col, sc in ((P.RED, 1.0), (P.ORANGE, 0.75), (P.YELLOW, 0.48)):                         # the flames
        d.add(f'<path d="M{-40 * sc},-14 Q{-50 * sc},{-70 * sc} {-18 * sc},{-96 * sc} Q{-12 * sc},{-60 * sc} '
              f'0,{-130 * sc} Q{14 * sc},{-70 * sc} {24 * sc},{-100 * sc} Q{52 * sc},{-60 * sc} {40 * sc},-14 Z" '
              f'fill="{col}" stroke="{INK if sc == 1.0 else col}" stroke-width="1.6"/>')
    rnd = random.Random(7)
    for _ in range(18):                                                                       # sparks rising
        px, py = rnd.uniform(-60, 60), rnd.uniform(-260, -120)
        d.add(f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(rnd.uniform(1.4, 3))}" fill="{P.SUN}"/>')
    d.add(f'<path d="M6,-140 Q30,-190 4,-240 Q-20,-290 14,-330" fill="none" stroke="{P.METAL_LIGHT}" '
          f'stroke-width="14" stroke-opacity=".35" stroke-linecap="round"/>')                   # the smoke
    c.add(_at(d, x, foot, k))
    return {"box": (x - 86 * k, foot - 135 * k, x + 86 * k, foot + 16 * k)}


def flagstones(c: Canvas, y0: float, y1: float, ring: tuple[float, float]) -> None:
    """The gathering place round the fire, paved with flat stones: irregular flags in rows, nearer ones bigger,
    each lit along its top edge and shaded along its bottom, moss in the joints; round the fire (`ring`: its
    middle and radius) the flags give way to a ring of trodden earth with ash in it."""
    c.add(f'<rect x="-6" y="{n(y0)}" width="{W + 12}" height="{n(y1 - y0)}" fill="{mix(P.LEAF_DARK, INK, 0.3)}"/>')
    rnd = random.Random(11)
    y, row = y0 + 2, 0
    while y < y1:
        rh = 16 + row * 7
        x = -rnd.uniform(0, 40)
        while x < W + 6:
            w = rnd.uniform(1.4, 2.4) * rh
            tone = rnd.choice((P.STONE, lighten(P.STONE, 0.08), mix(P.STONE, P.SAND, 0.25), darken(P.STONE, 0.92)))
            y2 = y + 2 + rnd.uniform(0, 3)
            c.add(f'<path d="M{n(x + 3)},{n(y + 3)} L{n(x + w - 4)},{n(y2)} L{n(x + w - 2)},{n(y + rh - 3)} '
                  f'L{n(x + 4)},{n(y + rh - 2)} Z" fill="{tone}" stroke="{INK}" stroke-width="1"/>'
                  f'<path d="M{n(x + 5)},{n(y + 4.5)} L{n(x + w - 6)},{n(y2 + 1.5)}" stroke="{P.WHITE}" '
                  f'stroke-opacity=".45" stroke-width="2"/><path d="M{n(x + 6)},{n(y + rh - 4)} '
                  f'L{n(x + w - 4)},{n(y + rh - 4.5)}" stroke="{INK}" stroke-opacity=".18" stroke-width="3"/>')
            x += w
        y += rh
        row += 1
    cx, r = ring
    c.add(f'<ellipse cx="{n(cx)}" cy="{n(y0 + 70)}" rx="{n(r)}" ry="{n(r * 0.3)}" fill="{EARTH}" stroke="{INK}" '
          f'stroke-width="1.2"/><ellipse cx="{n(cx)}" cy="{n(y0 + 72)}" rx="{n(r * 0.7)}" ry="{n(r * 0.2)}" '
          f'fill="{mix(P.METAL, EARTH, 0.4)}"/>')


def seat_log(c: Canvas, x: float, y: float, w: float, k: float) -> tuple:
    """A log to sit on, lying along the ground at (x, y), `w` long: its bark in strips, the sawn end with its rings.
    Returns its box."""
    h = 20 * k
    c.add(f'<rect x="{n(x - w / 2)}" y="{n(y - h)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" '
          f'fill="{mix(P.WOOD, P.TERRACOTTA, 0.3)}" stroke="{INK}" stroke-width="1.6"/>')
    c.line(" ".join(f"M{n(x - w / 2 + q * 18 * k)},{n(y - h + 3)} h{n(10 * k)}" for q in range(int(w / (18 * k)))),
           max(1.0, 1.4 * k), P.WOOD_DARK)
    c.add(f'<ellipse cx="{n(x + w / 2)}" cy="{n(y - h / 2)}" rx="{n(h * 0.3)}" ry="{n(h / 2)}" fill="{P.WOOD_PALE}" '
          f'stroke="{INK}" stroke-width="1.4"/><ellipse cx="{n(x + w / 2)}" cy="{n(y - h / 2)}" rx="{n(h * 0.14)}" '
          f'ry="{n(h * 0.24)}" fill="none" stroke="{P.WOOD}" stroke-width="1"/>')
    return (x - w / 2, y - h, x + w / 2 + h * 0.3, y)


def opener(st: Stage, accent: str):
    """The camp at dusk around the big campfire in the middle of the clearing: the sky deepening to pine-blue over
    the title, the first stars; the dark pines all round; the log gate in its palisade and the watchtower on the
    left, tents glowing from inside and a cabin with its lit window across the meadow, the lake with the stars in
    it and the jetty on the right; in the stone-paved fire circle the fire with its flames, sparks rising, a
    ribbon of smoke, fireflies over the grass. Round the fire: the agent warming its hands, the caterpillar with
    her checklist, the cat with his enamel mug, the professor under his bubble, the sparrow on a stump."""
    ledger(st)
    c = st.back
    horizon, deck_y = 748.0, 962.0
    sets.sky(c, mix(PINE, P.SPACE_DEEP, 0.6), mix(P.ORANGE, P.YELLOW_PALE, 0.55), horizon, W)
    rnd = random.Random(3)
    for _ in range(30):
        c.add(f'<circle cx="{n(rnd.uniform(380, W - 20))}" cy="{n(rnd.uniform(20, 260))}" '
              f'r="{n(rnd.uniform(1.2, 2.4))}" fill="{P.YELLOW_PALE}"/>')
    x = -20
    while x < W + 30:                                                  # the forest round the clearing
        pine(c, x, horizon + 10, rnd.uniform(1.8, 2.4), mix(NEEDLE, P.SPACE_DEEP, 0.35), seed=int(x))
        x += rnd.uniform(40, 70)
    c.add(f'<rect x="-6" y="{horizon}" width="{W + 12}" height="{deck_y - horizon + 6}" '
          f'fill="{mix(GRASS, P.SPACE_DEEP, 0.3)}"/>')
    brush = mix(NEEDLE, P.SPACE_DEEP, 0.5)                             # the undergrowth at the forest's foot
    c.add(f'<path d="M-6,{horizon + 12} ' + " ".join(f"Q{q + 15},{horizon - 46 - (q * 7) % 18} {q + 30},"
                                                    f"{horizon - 30}" for q in range(-6, W + 30, 30))
          + f' V{horizon + 12} Z" fill="{brush}"/>')
    c.add(f'<path d="M560,{horizon + 30} Q700,{horizon + 14} {W + 6},{horizon + 26} V{horizon + 100} '
          f'Q700,{horizon + 110} 560,{horizon + 80} Z" fill="{mix(P.BLUE, P.SPACE_DEEP, 0.45)}" stroke="{INK}" '
          f'stroke-width="1.4"/>')                                                               # the lake
    for q in range(8):
        c.add(f'<circle cx="{n(590 + q * 30)}" cy="{n(horizon + 44 + (q % 3) * 14)}" r="1.4" '
              f'fill="{P.YELLOW_PALE}"/>')
    c.add(f'<rect x="600" y="{horizon + 62}" width="140" height="8" fill="{P.WOOD}" stroke="{INK}" '
          f'stroke-width="1.2"/>')                                                               # the jetty
    c.line(" ".join(f"M{q},{horizon + 70} v14" for q in range(610, 740, 30)), 3, P.WOOD_DARK)
    gt = gate(c, 120, horizon + 60, 1.05)
    watchtower(c, 278, horizon + 40, 1.25)
    cabin(c, 470, horizon + 50, 0.62, "leader")
    for tx, ty, col in ((330, horizon + 110, P.ORANGE), (560, horizon + 128, P.TEAL), (190, horizon + 140, P.RED)):
        tent_far(c, tx, ty, 1.9, col, lit=True)
        c.add(f'<ellipse cx="{tx}" cy="{ty - 12}" rx="46" ry="26" fill="{P.SUN}" fill-opacity=".14"/>')
    st.put(0.5, "", gt["box"], "gate", group="camp", backdrop=True)
    for _ in range(16):                                                                       # fireflies
        fx_, fy_ = rnd.uniform(20, W - 20), rnd.uniform(horizon + 20, deck_y - 20)
        c.add(f'<circle cx="{n(fx_)}" cy="{n(fy_)}" r="5" fill="{P.YELLOW}" fill-opacity=".25"/>'
              f'<circle cx="{n(fx_)}" cy="{n(fy_)}" r="2.2" fill="{P.YELLOW}"/>')
    flagstones(c, deck_y, H + 6, (350, 170))
    st.keep_clear((-6, horizon - 2, W + 6, horizon + 2), (-6, deck_y - 4, W + 6, deck_y + 14))
    fb = fire(c, 388, deck_y + 50, 1.0)
    st.put(deck_y + 50, "", fb["box"], "fire", group="fire")
    for lx, ly, lw in ((130, deck_y + 28, 150), (600, deck_y + 30, 130)):     # logs to sit on, behind the cast
        lb = seat_log(c, lx, ly, lw, 1.3)
        st.put(ly, "", lb, f"log{lx}", group="logs", backdrop=True)
    prof = st.actor("professor", 716, 1092, "explain", "talk", flip=True, tall=330)
    st.speaker(prof, width=74, left=128, air=CLEAR_MM)
    st.actor("agent", 125, 1090, "present", "smile", flip=False, tall=320, group="agent")
    cp = st.actor("caterpillar", 245, 1092, "present", "smile", flip=False, tall=240, group="caterpillar")
    st.hold(cp, checklist(3))
    cat = st.actor("cat", 548, 1094, "present", "smile", flip=True, tall=240, group="cat")
    st.hold(cat, mug)
    st.actor("sparrow", 40, deck_y + 28 - 25, "point", "smile", tall=80, group="logs")    # on the log
    drawn = st.render()
    drawn.holders, drawn.links, drawn.ports = st.holders, st.links, st.ports
    return drawn


CAMP.stations.extend([
    Station("keys", _framed(keys_station), ("give", "wear")),
    Station("knock", _framed(knock_station), ("knock", "list")),
    Station("sandbox", _framed(sandbox_station), ("saw", "hammer")),
    Station("parcel", _framed(parcel_station), ("arrive", "check")),
    Station("note", _framed(note_station), ("read", "ignore")),
    Station("practice", _framed(practice_station), ("pitch", "strike")),
    Station("store", _framed(store_station), ("ask", "open")),
    Station("plan", _framed(plan_station), ("plan", "packed")),
    Station("test", _framed(test_station), ("try", "stopped")),
])
CAMP.backdrop = backdrop
CAMP.alternate = True                                       # never one moment on two pages in a row
CAMP.finale = finale
stories.OPENERS["forest_camp"] = opener

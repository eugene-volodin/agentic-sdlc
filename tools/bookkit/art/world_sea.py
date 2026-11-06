"""The underwater base: the world of chapter 6 (the agent must be able to run the project).

A research base on the sea floor, its corridors and rooms of violet hull plates with brass fittings and warm lamps;
through its round portholes the coral labyrinth outside - fish, kelp, light coming down from the surface. The work
outside is done by the base's submarine. The stations, one per section of the chapter:

1. build     the agent assembles the project itself: in the dock the submarine on its cradle, its engine panel
             open; the agent turns the starter on the console and the gauges come alive;
2. preview   preview stands: a glass test tank where a small copy of the build runs for everyone to see;
3. services  hundreds of services: through a big porthole a coral town of shell houses linked by pipes, and a
             panel of switches where the agent lights only the few houses he needs;
4. monorepo  the modular monolith and the monorepo: the map room - a big table with the map of the coral maze,
             a little plaque at every cave; the agent plots a route, the caterpillar is afraid of getting lost;
5. testing   manual testing by the agent: the control desk, its screen showing the submarine passing the gates
             outside one by one, the caterpillar ticking the cases off on her clipboard;
6. video     video in the pull request: an underwater camera on its bracket by a porthole, its red lamp on, and
             the replay on a monitor that the cat watches;
7. check     how to check that it all works: through a porthole the submarine comes out of the labyrinth's exit,
             the cat times it, the caterpillar checks the log;
8. mobile    mobile apps: a phone in a sealed waterproof case hangs in a pressure test chamber; the agent taps it
             through the chamber's glove ports.

The back wall turns from frame to frame: hull plates and their rivets, portholes onto the reef, caged lamps, gauges,
lockers; deck plates underfoot. Words only where they belong to a thing - the camera's lamp - and in the finale,
which names the stations.
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
from .world_fair import stand as _fair_stand
from .world_kit import FLOPPY_K, SIZE, Pen, hide, ledger, motion, stash, tag_size
from .world_kitchen import _box, _fit_tall
from .world_library import ph, span
from .worlds import Station, world

SEA = world("sea", opener="deepsea")

_at = sets._at

VIOLET = P.VIOLET
WALL = mix(VIOLET, P.CARD, 0.62)               # the hull plates inside: pale violet
PLATE = mix(VIOLET, P.CARD, 0.5)               # every other plate a shade deeper
STRAKE = darken(VIOLET, 0.8)                   # the deep violet panelled dado along the foot of the wall
FRAME = mix(VIOLET, P.METAL_DARK, 0.3)         # the hull's ribs and the windows' frames
BRASS = mix(P.SUN, P.WOOD, 0.35)
WATER = mix(P.BLUE, VIOLET, 0.42)              # the sea outside, violet-blue
WATER_DEEP = darken(WATER, 0.72)
DECK = (mix(P.METAL, VIOLET, 0.18), mix(P.METAL_LIGHT, VIOLET, 0.14))
CORALS = (P.PINK, P.ORANGE, mix(P.PINK, VIOLET, 0.4), P.YELLOW, mix(P.RED, P.PINK, 0.4))


def calm(color: str) -> str:
    """A colour of the back wall, calmer than the station's."""
    return mix(color, WALL, 0.4)


# ============================================================================ the sea outside
def reef(c: Canvas, x0: float, y0: float, x1: float, y1: float, k: float, seed: int = 0, fish: int = 3,
         rays: bool = True) -> None:
    """The sea seen through glass between (x0, y0) and (x1, y1): violet-blue water darker below, light coming down
    in slanting rays, a sandy floor with coral heads - branching, brain and fan coral - and swaying kelp, a few fish
    and a string of bubbles."""
    rnd = random.Random(seed)
    w, h = x1 - x0, y1 - y0
    c.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(w)}" height="{n(h)}" fill="{WATER}"/>')
    c.add(f'<rect x="{n(x0)}" y="{n(y0 + h * 0.55)}" width="{n(w)}" height="{n(h * 0.45)}" fill="{WATER_DEEP}" '
          f'fill-opacity=".35"/>')
    if rays:
        for i in range(3):                                # light from the surface, slanting down
            rx = x0 + w * (0.15 + i * 0.32) + rnd.uniform(-6, 6)
            c.add(f'<path d="M{n(rx)},{n(y0)} h{n(w * 0.08)} L{n(rx + w * 0.2)},{n(y1)} h{n(-w * 0.16)} Z" '
                  f'fill="{P.WHITE}" fill-opacity=".14"/>')
    floor = y1 - h * 0.18
    c.add(f'<path d="M{n(x0)},{n(floor)} Q{n(x0 + w * 0.3)},{n(floor - h * 0.06)} {n(x0 + w * 0.6)},{n(floor)} '
          f'T{n(x1)},{n(floor - h * 0.03)} V{n(y1)} H{n(x0)} Z" fill="{mix(P.SAND, VIOLET, 0.25)}"/>')
    for i in range(max(2, int(w / (34 * k)))):            # coral heads and kelp along the floor
        cx = x0 + (i + 0.5) * w / max(2, int(w / (34 * k))) + rnd.uniform(-5, 5) * k
        kind = rnd.choice(("branch", "brain", "fan", "kelp"))
        color = CORALS[rnd.randrange(len(CORALS))]
        s_ = rnd.uniform(0.7, 1.1) * min(k, h / 70)
        coral(c, cx, floor + 2 * s_, s_, kind, color)
    for i in range(fish):
        fx, fy = x0 + w * rnd.uniform(0.15, 0.85), y0 + h * rnd.uniform(0.18, 0.55)
        c.add(fishy(fx, fy, min(k, h / 70) * rnd.uniform(0.7, 1.0), rnd.choice((-1, 1)),
                    (P.YELLOW, P.ORANGE, P.TEAL)[i % 3]))
    bx = x0 + w * rnd.uniform(0.6, 0.9)
    for j in range(4):
        c.add(f'<circle cx="{n(bx + (j % 2) * 3 * k)}" cy="{n(floor - 10 * k - j * 10 * k)}" '
              f'r="{n((1.6 + j * 0.5) * k)}" fill="{P.WHITE}" fill-opacity=".55" stroke="{P.WHITE}" '
              f'stroke-width=".8"/>')


def coral(c: Canvas, x: float, y: float, k: float, kind: str, color: str) -> None:
    """One coral standing on the sea floor at (x, y): a branching coral, a brain coral, a sea fan or a kelp."""
    lw = max(0.8, 1.2 * k)
    if kind == "branch":
        d = (f"M{n(x)},{n(y)} V{n(y - 14 * k)} M{n(x)},{n(y - 8 * k)} L{n(x - 8 * k)},{n(y - 20 * k)} "
             f"M{n(x)},{n(y - 10 * k)} L{n(x + 7 * k)},{n(y - 22 * k)} M{n(x - 4 * k)},{n(y - 14 * k)} "
             f"L{n(x - 2 * k)},{n(y - 26 * k)}")
        c.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{n(4.4 * k + 1.6)}" stroke-linecap="round"/>'
              f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{n(4.4 * k)}" stroke-linecap="round"/>')
    elif kind == "brain":
        c.add(f'<path d="M{n(x - 12 * k)},{n(y)} Q{n(x - 12 * k)},{n(y - 14 * k)} {n(x)},{n(y - 14 * k)} '
              f'Q{n(x + 12 * k)},{n(y - 14 * k)} {n(x + 12 * k)},{n(y)} Z" fill="{color}" stroke="{INK}" '
              f'stroke-width="{n(lw)}"/><path d="M{n(x - 8 * k)},{n(y - 4 * k)} q{n(4 * k)},{n(-6 * k)} '
              f'{n(8 * k)},0 t{n(8 * k)},0" fill="none" stroke="{darken(color, 0.7)}" stroke-width="{n(lw)}"/>')
    elif kind == "fan":
        c.add(f'<path d="M{n(x)},{n(y)} L{n(x - 14 * k)},{n(y - 20 * k)} Q{n(x)},{n(y - 30 * k)} '
              f'{n(x + 14 * k)},{n(y - 20 * k)} Z" fill="{color}" fill-opacity=".85" stroke="{INK}" '
              f'stroke-width="{n(lw)}"/>')
        c.line(f"M{n(x)},{n(y)} L{n(x - 7 * k)},{n(y - 22 * k)} M{n(x)},{n(y)} L{n(x + 7 * k)},{n(y - 22 * k)} "
               f"M{n(x)},{n(y)} V{n(y - 25 * k)}", max(0.6, 0.8 * k), darken(color, 0.65))
    else:
        for dx in (-3, 2):
            c.add(f'<path d="M{n(x + dx * k)},{n(y)} q{n(-5 * k)},{n(-10 * k)} 0,{n(-20 * k)} '
                  f'q{n(5 * k)},{n(-10 * k)} 0,{n(-18 * k)}" fill="none" stroke="{INK}" '
                  f'stroke-width="{n(3.6 * k + 1.4)}" stroke-linecap="round"/><path d="M{n(x + dx * k)},{n(y)} '
                  f'q{n(-5 * k)},{n(-10 * k)} 0,{n(-20 * k)} q{n(5 * k)},{n(-10 * k)} 0,{n(-18 * k)}" fill="none" '
                  f'stroke="{P.LEAF}" stroke-width="{n(3.6 * k)}" stroke-linecap="round"/>')


def fishy(x: float, y: float, k: float, way: int, color: str) -> str:
    """A small fish swimming `way` (1 right, -1 left): its body, a forked tail, an eye and a stripe."""
    c = Canvas()
    c.shape("M-10,0 Q-2,-7 8,0 Q-2,7 -10,0 Z", color, sw=1.1, light=None)
    c.shape("M-9,0 L-15,-5 L-14,0 L-15,5 Z", darken(color, 0.85), sw=1.0, light=None)
    c.line("M-2,-5 Q0,0 -2,5", 1.0, P.WHITE, 0.9)
    c.dot(4, -1.4, 1.1)
    return _at(c, x, y, k, mirror=way < 0)


def porthole(c: Canvas, cx: float, cy: float, r: float, k: float, seed: int = 0, view=None) -> None:
    """A round porthole in the hull: its thick brass rim with bolts all round and, through the glass, the sea -
    the reef, or what `view(c, x0, y0, x1, y1)` draws there. The glass is a disc: the view is clipped to it."""
    g = Canvas()
    (view or (lambda cc, a, b, cc_, d: reef(cc, a, b, cc_, d, r / 40, seed, fish=2)))(g, cx - r, cy - r, cx + r,
                                                                                         cy + r)
    clip = c.shape(f"M{n(cx - r)},{n(cy)} A{n(r)},{n(r)} 0 1 1 {n(cx + r)},{n(cy)} A{n(r)},{n(r)} 0 1 1 "
                   f"{n(cx - r)},{n(cy)} Z", WATER, sw=0, light=None, clip=True)
    c.add(f'<g clip-path="url(#{clip})">{g.render()}</g>')
    c.add(f'<path d="M{n(cx - r * 0.55)},{n(cy - r * 0.5)} A{n(r * 0.75)},{n(r * 0.75)} 0 0 1 {n(cx + r * 0.1)},'
          f'{n(cy - r * 0.75)}" fill="none" stroke="{P.WHITE}" stroke-width="{n(max(1.0, r * 0.06))}" '
          f'stroke-opacity=".7" stroke-linecap="round"/>')                       # the glass's glint
    rim = max(3.0, r * 0.16)
    c.add(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r + rim / 2)}" fill="none" stroke="{INK}" '
          f'stroke-width="{n(rim + 2.4)}"/><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r + rim / 2)}" fill="none" '
          f'stroke="{BRASS}" stroke-width="{n(rim)}"/>')
    bolts = max(8, int(r / 4))
    c.add("".join(f'<circle cx="{n(cx + math.cos(a) * (r + rim / 2))}" cy="{n(cy + math.sin(a) * (r + rim / 2))}" '
                  f'r="{n(max(0.9, rim * 0.18))}" fill="{darken(BRASS, 0.6)}"/>'
                  for a in [i * 2 * math.pi / bolts for i in range(bolts)]))


# ============================================================================ the base inside
def maze_view(c: Canvas, x0: float, y0: float, x1: float, y1: float, k: float, seed: int = 0, school: int = 6,
              veil: float = 0.0) -> None:
    """The coral labyrinth seen through glass between (x0, y0) and (x1, y1): violet-blue water darkening in bands
    downward, light rays slanting from the surface; far off, pale walls of the maze; nearer, darker walls of layered
    coral with an arch through them, tube sponges and branching coral on their tops, kelp swaying in the gaps; a
    small school of the same little fish in a curve, a string of bubbles. `veil`: the whole view calmed towards
    the wall's colour, to sit behind a station."""
    rnd = random.Random(seed)
    w, h = x1 - x0, y1 - y0
    for i, f in enumerate((0.0, 0.34, 0.62, 0.84)):                     # the water, darker downward
        c.add(f'<rect x="{n(x0)}" y="{n(y0 + h * f)}" width="{n(w)}" height="{n(h * (1 - f) + 1)}" '
              f'fill="{mix(lighten(WATER, 0.22), WATER_DEEP, i / 3)}"/>')
    for _ in range(2 + int(w / 260)):                                   # light from the surface
        rx = x0 + w * rnd.uniform(0.05, 0.85)
        c.add(f'<path d="M{n(rx)},{n(y0)} h{n(w * 0.06 + 10)} L{n(rx + h * 0.5)},{n(y1)} h{n(-w * 0.1 - 16)} Z" '
              f'fill="{P.WHITE}" fill-opacity=".13"/>')
    far = mix(mix(VIOLET, P.PINK, 0.25), WATER, 0.5)
    near = darken(mix(VIOLET, P.PINK, 0.3), 0.85)
    for layer, (tone, base_f, top_f) in enumerate(((far, 0.78, 0.42), (near, 1.02, 0.58))):
        pts = [(x0 - 10, y1 + 10)]
        x = x0 - 10
        while x < x1 + 10:                                               # a wall's ragged top, its arches
            step = rnd.uniform(0.12, 0.22) * w
            top = y0 + h * rnd.uniform(top_f - 0.08, top_f + 0.1)
            pts += [(x + step * 0.15, top + h * 0.04), (x + step * 0.5, top), (x + step * 0.85, top + h * 0.05)]
            x += step
        pts += [(x1 + 10, y1 + 10)]
        d = "M" + " L".join(f"{n(px)},{n(py)}" for px, py in pts) + " Z"
        clip = c.shape(d, tone, sw=0, light=None, clip=True)
        bands = []
        for b_ in range(7):                                             # the rock's strata, wavy bands of tone
            by = y0 + h * (top_f + 0.02 + b_ * 0.07)
            amp = h * 0.012
            bands.append(f'<path d="M{n(x0 - 10)},{n(by)} ' + " ".join(
                f"Q{n(x0 + w * (q + 0.5) / 6)},{n(by + amp * (1 if q % 2 else -1))} {n(x0 + w * (q + 1) / 6)},{n(by)}"
                for q in range(6)) + f' V{n(by + h * 0.035)} H{n(x0 - 10)} Z" '
                f'fill="{darken(tone, 0.9) if b_ % 2 else lighten(tone, 0.08)}"/>')
        c.add(f'<g clip-path="url(#{clip})">{"".join(bands)}</g>')
        c.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{n(max(0.8, 1.2 * k))}" '
              f'stroke-linejoin="round"/>')
        if layer:                                                       # coral heads on the wall's face
            for q in range(int(w * h / (110 * k) ** 2)):
                hx, hy = x0 + w * rnd.random(), y0 + h * rnd.uniform(top_f + 0.12, 0.95)
                coral(c, hx, hy, k * rnd.uniform(0.6, 0.9), rnd.choice(("brain", "fan", "branch")),
                      CORALS[q % len(CORALS)])
        ax = x0 + w * rnd.uniform(0.25, 0.7)                              # an arch through the wall
        aw, ah = w * 0.12, h * (0.22 if layer else 0.16)
        ab = y0 + h * base_f - h * 0.12
        c.add(f'<path d="M{n(ax - aw)},{n(ab)} V{n(ab - ah * 0.5)} A{n(aw)},{n(ah * 0.6)} 0 0 1 {n(ax + aw)},'
              f'{n(ab - ah * 0.5)} V{n(ab)} Z" fill="{mix(WATER, WATER_DEEP, 0.4 + 0.3 * layer)}" stroke="{INK}" '
              f'stroke-width="{n(max(0.8, 1.1 * k))}"/>')
        c.line(" ".join(f"M{n(x0 + w * rnd.random())},{n(y0 + h * rnd.uniform(top_f + 0.1, 0.95))} "
                        f"q{n(6 * k)},{n(-3 * k)} {n(12 * k)},0" for _ in range(int(w / 50) + 2)),
               max(0.6, 0.9 * k), darken(tone, 0.75), 0.8)                # its layers
        if layer:
            for i in range(int(w / (70 * k)) + 1):                        # sponges, corals, kelp on the near wall
                cx = x0 + (i + rnd.uniform(0.2, 0.8)) * 70 * k
                cy = y0 + h * rnd.uniform(top_f + 0.04, top_f + 0.16)
                kind = rnd.choice(("sponge", "branch", "fan", "kelp", "brain"))
                if kind == "sponge":
                    for j, dx in enumerate((-4, 0, 4)):
                        th_ = (12 + j * 4) * k
                        c.add(f'<rect x="{n(cx + dx * k - 2.4 * k)}" y="{n(cy - th_)}" width="{n(4.8 * k)}" '
                              f'height="{n(th_)}" rx="{n(2 * k)}" fill="{(P.YELLOW, P.ORANGE, P.YELLOW)[j]}" '
                              f'stroke="{INK}" stroke-width="{n(max(0.6, 0.9 * k))}"/>')
                else:
                    coral(c, cx, cy, k * rnd.uniform(0.8, 1.1), kind, CORALS[rnd.randrange(len(CORALS))])
    fx, fy = x0 + w * rnd.uniform(0.2, 0.6), y0 + h * rnd.uniform(0.18, 0.3)
    way = rnd.choice((-1, 1))
    for j in range(school):                                              # a small school, in a curve
        a = j / max(1, school - 1)
        c.add(fishy(fx + way * a * w * 0.3, fy + math.sin(a * math.pi) * h * 0.08, k * 0.6, way, P.YELLOW))
    bx = x0 + w * rnd.uniform(0.6, 0.92)
    for j in range(4):
        c.add(f'<circle cx="{n(bx + (j % 2) * 3 * k)}" cy="{n(y0 + h * 0.5 - j * 10 * k)}" '
              f'r="{n((1.6 + j * 0.5) * k)}" fill="{P.WHITE}" fill-opacity=".5" stroke="{P.WHITE}" '
              f'stroke-width=".8"/>')
    if veil:
        c.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(w)}" height="{n(h)}" fill="{WALL}" '
              f'fill-opacity="{veil:.2f}"/>')


def window(c: Canvas, x0: float, x1: float, top: float, bottom: float, k: float, seed: int, veil: float) -> None:
    """A big window in the hull from x0 to x1, `top` to `bottom`: rounded corners, a thick violet frame with its
    rivets and a brass inner bead, the labyrinth through the glass and a glint across it."""
    w, h = x1 - x0, bottom - top
    rad = min(w, h) * 0.18
    g = Canvas()
    maze_view(g, x0, top, x1, bottom, k, seed, veil=veil)
    clip = c.shape(rounded_rect_d(x0, top, w, h, rad), WATER, sw=0, light=None, clip=True)
    c.add(f'<g clip-path="url(#{clip})">{g.render()}</g>')
    c.line(f"M{n(x0 + w * 0.12)},{n(top + h * 0.3)} L{n(x0 + w * 0.3)},{n(top + h * 0.08)}", max(1.0, 2.4 * k),
           P.WHITE, 0.6)
    fr = max(4.0, 9 * k)
    c.add(f'<rect x="{n(x0 - fr / 2)}" y="{n(top - fr / 2)}" width="{n(w + fr)}" height="{n(h + fr)}" '
          f'rx="{n(rad + fr / 2)}" fill="none" stroke="{INK}" stroke-width="{n(fr + 2.4)}"/>'
          f'<rect x="{n(x0 - fr / 2)}" y="{n(top - fr / 2)}" width="{n(w + fr)}" height="{n(h + fr)}" '
          f'rx="{n(rad + fr / 2)}" fill="none" stroke="{FRAME}" stroke-width="{n(fr)}"/>'
          f'<rect x="{n(x0)}" y="{n(top)}" width="{n(w)}" height="{n(h)}" rx="{n(rad)}" fill="none" '
          f'stroke="{BRASS}" stroke-width="{n(max(1.0, 1.6 * k))}"/>')
    per = max(4, int((w + h) * 2 / (26 * k)))
    for i in range(per):                                                  # its rivets round the frame
        t = i / per
        if t < 0.25:
            px, py = x0 + w * t * 4, top - fr / 2
        elif t < 0.5:
            px, py = x1 + fr / 2, top + h * (t - 0.25) * 4
        elif t < 0.75:
            px, py = x1 - w * (t - 0.5) * 4, bottom + fr / 2
        else:
            px, py = x0 - fr / 2, bottom - h * (t - 0.75) * 4
        if min(abs(px - x0), abs(px - x1)) > rad * 0.6 or min(abs(py - top), abs(py - bottom)) > rad * 0.6:
            c.add(f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(max(0.8, 1.3 * k))}" fill="{darken(FRAME, 0.65)}"/>')


def valve(c: Canvas, x: float, y: float, k: float) -> None:
    """A pipe valve at (x, y) on a vertical pipe: its body and a red handwheel with spokes."""
    c.add(f'<rect x="{n(x - 5 * k)}" y="{n(y - 6 * k)}" width="{n(10 * k)}" height="{n(12 * k)}" rx="{n(2 * k)}" '
          f'fill="{BRASS}" stroke="{INK}" stroke-width="1"/>')
    c.add(f'<circle cx="{n(x + 9 * k)}" cy="{n(y)}" r="{n(6 * k)}" fill="none" stroke="{INK}" '
          f'stroke-width="{n(3.6 * k + 1.6)}"/><circle cx="{n(x + 9 * k)}" cy="{n(y)}" r="{n(6 * k)}" fill="none" '
          f'stroke="{P.RED}" stroke-width="{n(3.6 * k)}"/><path d="M{n(x + 3 * k)},{n(y)} h{n(12 * k)} '
          f'M{n(x + 9 * k)},{n(y - 6 * k)} v{n(12 * k)}" stroke="{P.RED}" stroke-width="{n(1.4 * k)}"/>')


def deck(c: Canvas, x0: float, x1: float, y0: float, y1: float, k: float) -> None:
    """The deck underfoot from y0 down to y1: steel plates in rows that grow towards the front, each with a raised
    diamond tread and a rivet at its corners, the seams between them."""
    c.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" fill="{darken(DECK[0], 0.8)}"/>')
    y, row = y0, 0
    while y < y1:
        rh = (8 + row * 4) * max(0.6, k)
        pw = rh * 3.2
        x = x0 - (row % 2) * pw / 2
        while x < x1:
            tone = DECK[(row + int((x - x0) / pw)) % 2]
            c.add(f'<rect x="{n(x + 0.8)}" y="{n(y + 0.8)}" width="{n(pw - 1.6)}" height="{n(rh - 1.6)}" '
                  f'fill="{tone}"/>')
            if rh > 10:                                   # the tread and the rivets on the nearer plates
                c.add("".join(f'<path d="M{n(x + pw * f)},{n(y + rh * 0.5)} l{n(rh * 0.12)},{n(-rh * 0.12)} '
                              f'l{n(rh * 0.12)},{n(rh * 0.12)}" fill="none" stroke="{darken(tone, 0.85)}" '
                              f'stroke-width=".8"/>' for f in (0.3, 0.5, 0.7)))
                c.add("".join(f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(rh * 0.06)}" fill="{darken(tone, 0.7)}"/>'
                              for px in (x + 3, x + pw - 3) for py in (y + 3, y + rh - 3)))
            x += pw
        y += rh
        row += 1


def lamp(c: Canvas, x: float, y: float, k: float) -> None:
    """A caged bulkhead lamp on the wall at (x, y): its brass base, the warm bulb behind a wire cage, its glow."""
    glow(c, x, y + 4 * k, 5 * k)
    c.add(f'<rect x="{n(x - 8 * k)}" y="{n(y - 6 * k)}" width="{n(16 * k)}" height="{n(5 * k)}" rx="{n(1.5 * k)}" '
          f'fill="{BRASS}" stroke="{INK}" stroke-width="1"/>')
    c.add(f'<path d="M{n(x - 7 * k)},{n(y - 1 * k)} V{n(y + 8 * k)} Q{n(x)},{n(y + 15 * k)} {n(x + 7 * k)},'
          f'{n(y + 8 * k)} V{n(y - 1 * k)} M{n(x)},{n(y - 1 * k)} V{n(y + 11.5 * k)} M{n(x - 7 * k)},'
          f'{n(y + 5 * k)} H{n(x + 7 * k)}" fill="none" stroke="{darken(BRASS, 0.7)}" stroke-width="{n(1.2 * k)}"/>')


def hatch_door(c: Canvas, x0: float, x1: float, top: float, foot: float, k: float) -> None:
    """A watertight door in the hull: a rounded steel door with its frame, its dogs round the edge and the wheel."""
    w = x1 - x0
    c.add(f'<rect x="{n(x0)}" y="{n(top)}" width="{n(w)}" height="{n(foot - top)}" rx="{n(w * 0.3)}" '
          f'fill="{calm(P.METAL)}" stroke="{calm(INK)}" stroke-width="1.6"/>')
    c.add(f'<rect x="{n(x0 + 6 * k)}" y="{n(top + 6 * k)}" width="{n(w - 12 * k)}" height="{n(foot - top - 12 * k)}" '
          f'rx="{n(w * 0.25)}" fill="{calm(P.METAL_LIGHT)}" stroke="{calm(INK)}" stroke-width="1.2"/>')
    cx, cy, r = (x0 + x1) / 2, (top + foot) / 2, w * 0.18
    c.add(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="none" stroke="{calm(P.RED)}" '
          f'stroke-width="{n(3 * k)}"/><path d="M{n(cx - r)},{n(cy)} H{n(cx + r)} M{n(cx)},{n(cy - r)} V{n(cy + r)}" '
          f'stroke="{calm(P.RED)}" stroke-width="{n(2 * k)}"/>')


def gauge(c: Canvas, x: float, y: float, r: float, value: float, color: str = P.CARD, lw: float = 1.2) -> None:
    """A round dial gauge at (x, y): its brass bezel, the scale with a red sector at its end, the needle at
    `value` (0..1)."""
    c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{color}" stroke="{BRASS}" stroke-width="{n(r * 0.22)}"/>'
          f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r * 1.11)}" fill="none" stroke="{INK}" stroke-width="{n(lw)}"/>')
    for i in range(7):
        a = math.radians(-220 + i * 260 / 6)
        c.line(f"M{n(x + math.cos(a) * r * 0.62)},{n(y + math.sin(a) * r * 0.62)} "
               f"L{n(x + math.cos(a) * r * 0.82)},{n(y + math.sin(a) * r * 0.82)}", max(0.6, r * 0.06),
               P.RED if i >= 5 else INK)
    a = math.radians(-220 + value * 260)
    c.line(f"M{n(x)},{n(y)} L{n(x + math.cos(a) * r * 0.75)},{n(y + math.sin(a) * r * 0.75)}", max(0.8, r * 0.1),
           P.RED)
    c.dot(x, y, max(0.8, r * 0.1))


def backdrop(s: Strip, index: int) -> None:
    """The base behind a station: the wall is a row of big windows onto the coral labyrinth - water darkening
    downward, light rays, walls and arches of the maze, kelp, a school of fish, bubbles; a different stretch of
    the maze in every frame, calmed so the station stands out - between them riveted violet hull ribs with pipes,
    a valve and a gauge, now and then a pressure door with its wheel or a locker; under the windows a panelled
    violet dado, a pipe run along the top in a taller frame; the deck plates with their treads underfoot."""
    s.decor = False
    s.dress = False
    s.indoor = True
    ledger(s)
    zoom(s)
    c = s.back
    base = s.base
    k = max(0.6, min(1.4, base / 240))
    c.add(f'<rect x="-6" y="-6" width="{W + 12}" height="{n(base + 8)}" fill="{FRAME}"/>')
    top = 4.0
    if s.h >= 200:                                         # the pipe run under the deckhead
        for j, (color, wd) in enumerate(((P.METAL_LIGHT, 8), (BRASS, 5))):
            y = 6 * k + j * 11 * k
            c.add(f'<rect x="-6" y="{n(y)}" width="{W + 12}" height="{n(wd * k)}" fill="{color}" stroke="{INK}" '
                  f'stroke-width="1.1"/>')
            for i in range(int(W / (110 * k)) + 2):
                fx = i * 110 * k + (index * 37 + j * 50) % 110
                c.add(f'<rect x="{n(fx)}" y="{n(y - 2 * k)}" width="{n(5 * k)}" height="{n((wd + 4) * k)}" '
                      f'fill="{darken(color, 0.85)}" stroke="{INK}" stroke-width=".9"/>')
        top = 30 * k
    dado = base - min(base * 0.3, 70 * k)                  # the panelled dado under the windows
    c.add(f'<rect x="-6" y="{n(dado)}" width="{W + 12}" height="{n(base - dado + 2)}" fill="{STRAKE}"/>')
    pw = 70 * k
    for i in range(int(W / pw) + 2):
        px = i * pw - (index * 17) % pw
        c.add(f'<rect x="{n(px + 4 * k)}" y="{n(dado + 5 * k)}" width="{n(pw - 8 * k)}" '
              f'height="{n(base - dado - 10 * k)}" rx="{n(3 * k)}" fill="{lighten(STRAKE, 0.12)}" '
              f'stroke="{darken(STRAKE, 0.7)}" stroke-width="1.2"/>')
    c.add(f'<rect x="-6" y="{n(dado - 5 * k)}" width="{W + 12}" height="{n(6 * k)}" fill="{BRASS}" stroke="{INK}" '
          f'stroke-width="1"/>')                              # its brass rail
    rnd = random.Random(index * 11 + 5)
    rib = 22 * k
    x = -rib / 2 - (index * 41) % (60 * k)
    i = index
    while x < W:
        kind = ("window", "window", "door", "window", "pipes", "window", "window", "locker")[i % 8]
        w = {"door": 80, "pipes": 46, "locker": 64}.get(kind, rnd.uniform(150, 200)) * k
        x0, x1 = x + rib, x + rib + w
        if kind == "window" and dado - top > 40:
            window(c, x0 + 4 * k, x1 - 4 * k, top + 8 * k, dado - 12 * k, k, seed=rnd.randrange(999), veil=0.22)
        elif kind == "door":
            hatch_door(c, x0 + 6 * k, x1 - 6 * k, max(top + 4, base - 150 * k), base - 1, k)
        elif kind == "pipes":
            for px in (x0 + 12 * k, x0 + 30 * k):
                c.add(f'<rect x="{n(px - 3.5 * k)}" y="{n(top)}" width="{n(7 * k)}" height="{n(dado - top)}" '
                      f'fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="1"/>')
            valve(c, x0 + 12 * k, top + (dado - top) * 0.55, k)
            if dado - top > 60:
                gauge(c, x0 + 30 * k, top + (dado - top) * 0.3, 8 * k, rnd.uniform(0.3, 0.6))
        elif kind == "locker" and base - top > 70:
            lh = min(130 * k, base - top - 10)
            c.add(f'<rect x="{n(x0 + 4 * k)}" y="{n(base - lh)}" width="{n(w - 8 * k)}" height="{n(lh)}" '
                  f'rx="{n(2 * k)}" fill="{mix(VIOLET, P.METAL, 0.45)}" stroke="{INK}" stroke-width="1.2"/>')
            c.line(f"M{n((x0 + x1) / 2)},{n(base - lh)} V{n(base)}", 1, INK)
            for vx in (-12, 12):
                c.line(" ".join(f"M{n((x0 + x1) / 2 + vx * k - 6 * k)},{n(base - lh + (8 + j * 4) * k)} "
                                f"h{n(12 * k)}" for j in range(3)), 1, INK, 0.7)
        c.add(f'<rect x="{n(x)}" y="{n(top - 2)}" width="{n(rib)}" height="{n(dado - top + 2)}" fill="{FRAME}" '
              f'stroke="{INK}" stroke-width="1.2"/>')                     # the rib, riveted
        c.add("".join(f'<circle cx="{n(x + rib / 2)}" cy="{n(ry)}" r="{n(1.4 * k)}" fill="{darken(FRAME, 0.6)}"/>'
                      for ry in [top + 8 * k + j * 16 * k for j in range(int((dado - top) / (16 * k)))]))
        x = x1
        i += 1
    deck(c, -6, W + 6, base, s.h + 4, max(0.8, s.unit))
    c.add(f'<rect x="-6" y="{n(base - 5)}" width="{W + 12}" height="8" fill="{darken(STRAKE, 0.7)}" '
          f'stroke="{INK}" stroke-width="1.2"/>')                                 # the kick plate


# ============================================================================ placing the cast
def _framed(draw):
    """A station drawn mirrored on every other page: it and its cast swap sides, the things are never mirrored."""
    def run(s: Strip, beat: str) -> None:
        s.mirror = bool(s.shot)
        draw(s, beat)
    return run


def sx(s: Strip, frac: float) -> float:
    return s.x(1 - frac if getattr(s, "mirror", False) else frac)


def M(s: Strip, fracs: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(1 - f for f in fracs) if getattr(s, "mirror", False) else fracs


def F(s: Strip, flip: bool) -> bool:
    return (not flip) if getattr(s, "mirror", False) else flip


def stand(s: Strip, name: str, fracs, pose: str, mood: str = "smile", flip: bool = True, hold=None):
    """A character of the station at the first of `fracs` where it finds room - failing those, at the nearest free
    spot along the floor, and failing that a step further back - whole inside the frame; `hold` a thing of
    `handheld` to put in its hand."""
    first = fracs if isinstance(fracs, tuple) else (fracs,)
    probe = _box(s, name, 0, lane(s).feet)
    half = (probe[2] - probe[0]) / 2
    sweep = sorted((f for f in (i / 40 for i in range(41)) if half + 2 <= s.x(f) <= W - half - 2),
                   key=lambda f: abs(f - first[0]))
    who = _fair_stand(s, name, (*first, *sweep), pose, mood, flip=flip)
    if who is None and s.h >= 200:
        feet = lane(s).feet
        for scale in (0.88, 0.78):
            for f in (*first, *sweep):
                x = s.x(f)
                box = _box(s, name, x, feet, scale)
                if box[1] >= 2 and box[0] >= 2 and box[2] <= W - 2 and s.free(box, 3):
                    who = s.actor(name, x, feet, pose, mood, flip=flip, tall=s.tall * SIZE[name] * scale,
                                  group=name)
                    break
            if who is not None:
                break
    if who is not None and hold is not None:
        held(s, who, hold)
    return who


def sparrow_on(s: Strip, x: float, top: float, group: str, pose: str = "stand") -> None:
    """The sparrow standing on a thing of the station (`group`), as big as the room over it allows."""
    for scale in (0.45, 0.36, 0.28):
        bird = _box(s, "sparrow", x, top - 3.5, scale)
        if bird[1] > 2 and all(not b.hits(bird, 3) for b in s.boxes if b.group != group):
            s.actor("sparrow", x, top - 3.5, pose, "smile", flip=True, tall=s.tall * SIZE["sparrow"] * scale,
                    group=group)
            return


def scale_for(s: Strip, height: float, width: float, share: float = 0.42, of: float = 0.9) -> float:
    """A station thing's scale: `of` the professor's height for its `height`, its `width` within `share` of the
    frame, whole under the frame's top."""
    r = lane(s)
    return min(ph(s) * of / height, (r.feet - 8) / height, span(s, share) / width)


# ============================================================================ the things
def submarine(c: Canvas, x: float, foot: float, k: float, open_: bool = True, running: bool = False,
              cradle: bool = True) -> dict:
    """The base's submarine on its cradle, its foot's middle at (x, foot), 270 wide and 136 tall: two cradle
    stands on the deck, the violet hull in riveted plates with three brass portholes, the conning tower with its
    periscope, the searchlight at the bow, at the stern the propeller in its ring guard and the rudder; on its side
    the engine panel - `open_`: swung down on its hinges, the engine inside with its cylinders and pipes.
    `running`: the propeller turning, bubbles off it, the searchlight lit. Returns its parts' points on the page."""
    d = Canvas()
    hull_y = -78 if cradle else -40
    if cradle:
        for cx_ in (-62, 58):                                                       # the cradle stands
            d.shape(f"M{cx_ - 24},0 H{cx_ + 24} L{cx_ + 18},-8 L{cx_ + 12},{hull_y + 28} H{cx_ - 12} "
                    f"L{cx_ - 18},-8 Z", mix(P.METAL, VIOLET, 0.2), sw=1.6, light=None)
            d.shape(f"M{cx_ - 16},{hull_y + 30} Q{cx_},{hull_y + 40} {cx_ + 16},{hull_y + 30} V{hull_y + 24} "
                    f"Q{cx_},{hull_y + 34} {cx_ - 16},{hull_y + 24} Z", P.CHARCOAL, sw=1.0, light=None)
        d.shape(rounded_rect_d(-90, -14, 176, 6, 2), mix(P.METAL, VIOLET, 0.2), sw=1.2, light=None)
    d.shape(f"M-112,{hull_y - 4} L-134,{hull_y - 20} V{hull_y + 12} L-112,{hull_y + 4} Z", darken(VIOLET, 0.75),
            sw=1.4, light=None)                                                      # the rudder
    d.add(f'<ellipse cx="-126" cy="{hull_y}" rx="5" ry="20" fill="{P.METAL}" stroke="{INK}" stroke-width="1.4"/>')
    for a in (-40, 40, 180):                                                         # the propeller
        d.add(f'<ellipse cx="-126" cy="{hull_y}" rx="3" ry="15" fill="{BRASS}" stroke="{INK}" stroke-width="1" '
              f'transform="rotate({a} -126 {hull_y})" opacity="{0.6 if running else 1}"/>')
    d.add(f'<ellipse cx="-128" cy="{hull_y}" rx="7" ry="22" fill="none" stroke="{INK}" stroke-width="5.4"/>'
          f'<ellipse cx="-128" cy="{hull_y}" rx="7" ry="22" fill="none" stroke="{P.METAL}" stroke-width="3.4"/>'
          f'<path d="M-121,{hull_y - 18} L-112,{hull_y - 14} M-121,{hull_y + 18} L-112,{hull_y + 14}" '
          f'stroke="{P.METAL_DARK}" stroke-width="2"/>')                                # its guard on two struts
    d.shape(f"M-112,{hull_y - 30} Q-120,{hull_y} -112,{hull_y + 30} H104 Q140,{hull_y + 28} 140,{hull_y} "
            f"Q140,{hull_y - 28} 104,{hull_y - 30} Z", VIOLET, sw=2.0, light=(-2, -2), shade_k=0.82)   # the hull
    d.line(" ".join(f"M{px},{hull_y - 29} V{hull_y + 29}" for px in (-70, -20, 30, 80)), 1.0,
           darken(VIOLET, 0.7), 0.8)
    d.line(f"M-112,{hull_y + 8} H118", 0.8, darken(VIOLET, 0.75), 0.7)
    d.add("".join(f'<circle cx="{px + dx}" cy="{hull_y + dy}" r="1.1" fill="{darken(VIOLET, 0.6)}"/>'
                  for px in (-70, -20, 30, 80) for dx in (-3, 3) for dy in (-22, 22)))
    for px in (-2, 26, 54):                                                           # its portholes
        d.add(f'<circle cx="{px}" cy="{hull_y - 4}" r="8" fill="{P.LENS}" stroke="{BRASS}" stroke-width="3"/>'
              f'<circle cx="{px}" cy="{hull_y - 4}" r="9.6" fill="none" stroke="{INK}" stroke-width="1"/>'
              f'<path d="M{px - 4},{hull_y - 8} q3,-3 6,-2" fill="none" stroke="{P.WHITE}" stroke-width="1.2"/>')
    d.shape(f"M-6,{hull_y - 28} L0,{hull_y - 54} H40 L48,{hull_y - 28} Z", VIOLET, sw=1.8, light=(-1, -1))
    d.add(f'<circle cx="24" cy="{hull_y - 42}" r="5" fill="{P.LENS}" stroke="{BRASS}" stroke-width="2.4"/>')
    d.line(f"M12,{hull_y - 54} V{hull_y - 70} H22", 3.0, P.METAL_DARK)              # the periscope
    d.shape(rounded_rect_d(20, hull_y - 74, 8, 7, 1.5), P.METAL, sw=1.0, light=None)
    d.shape(f"M136,{hull_y - 10} h10 v20 h-10 Z", P.METAL_DARK, sw=1.2, light=None)    # the searchlight
    d.add(f'<rect x="144" y="{hull_y - 8}" width="3" height="16" fill="{P.YELLOW_PALE if running else P.LENS}" '
          f'stroke="{INK}" stroke-width=".8"/>')
    ex0, ey0 = -96, hull_y - 12                                                       # the engine panel
    if open_:
        d.shape(rounded_rect_d(ex0, ey0, 44, 26, 3), P.CHARCOAL, sw=1.4, light=None)   # the bay
        for j in range(3):                                                            # the engine's cylinders
            d.shape(rounded_rect_d(ex0 + 5 + j * 12, ey0 + 4, 9, 16, 2), P.METAL, sw=0.9, light=None)
            d.line(f"M{ex0 + 9.5 + j * 12},{ey0 + 4} V{ey0 + 1}", 1.6, BRASS)
        d.line(f"M{ex0 + 3},{ey0 + 22} H{ex0 + 41}", 2.2, P.RED)
        d.shape(f"M{ex0},{ey0 + 26} L{ex0 - 4},{ey0 + 44} H{ex0 + 40} L{ex0 + 44},{ey0 + 26} Z", VIOLET, sw=1.4,
                light=None)                                                            # the panel, swung down
        d.add(f'<rect x="{ex0 + 4}" y="{ey0 + 24}" width="6" height="4" fill="{P.METAL_DARK}"/>'
              f'<rect x="{ex0 + 34}" y="{ey0 + 24}" width="6" height="4" fill="{P.METAL_DARK}"/>')
    else:
        d.shape(rounded_rect_d(ex0, ey0, 44, 26, 3), VIOLET, sw=1.2, light=None)
        d.add("".join(f'<circle cx="{ex0 + bx}" cy="{ey0 + by}" r="1.2" fill="{INK}"/>'
                      for bx in (4, 40) for by in (4, 22)))
    if running:
        d.add(motion(-150, hull_y, 26, 0.9, way=-1))
        d.add("".join(f'<circle cx="{-140 - j * 7}" cy="{hull_y - 10 - j * 9}" r="{2 + j * 0.8}" fill="{P.WHITE}" '
                      f'fill-opacity=".6" stroke="{P.WHITE}" stroke-width=".8"/>' for j in range(4)))
    c.add(_at(d, x, foot, k))

    def at(px: float, py: float) -> tuple[float, float]:
        return x + px * k, foot + py * k

    return {"box": (x - 150 * k, foot + (hull_y - 76) * k, x + 150 * k, foot), "tower": at(20, hull_y - 74),
            "engine": at(ex0 + 22, ey0 + 12), "bow": at(146, hull_y)}


def starter(c: Canvas, x: float, foot: float, k: float, on: bool) -> dict:
    """The starter console standing on the deck at (x, foot), 60 wide and 120 tall: a post on a base plate, a
    slanted panel with three gauges - asleep at zero, or alive - a green lamp, and the big starter key-switch with
    its T handle, turned to START when `on`. Returns where things are."""
    d = Canvas()
    d.shape("M-26,0 H26 L22,-6 H-22 Z", P.METAL_DARK, sw=1.4, light=None)
    d.shape(rounded_rect_d(-8, -78, 16, 74, 2), mix(P.METAL, VIOLET, 0.25), sw=1.4, light=None)
    d.shape("M-30,-78 L-26,-120 H26 L30,-78 Z", mix(P.METAL, VIOLET, 0.3), sw=1.8, light=(-1, -1))
    for gx, v in ((-16, 0.62), (0, 0.48), (16, 0.7)):
        gauge(d, gx, -108, 6.4, v if on else 0.0)
    d.add(f'<circle cx="-16" cy="-90" r="3.2" fill="{P.GREEN if on else darken(P.GREEN, 0.5)}" stroke="{INK}" '
          f'stroke-width=".8"/>')
    d.add(f'<circle cx="8" cy="-89" r="7.6" fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="1.2"/>')
    d.add(f'<g transform="rotate({60 if on else 0} 8 -89)"><rect x="5" y="-99" width="6" height="20" rx="2" '
          f'fill="{P.RED}" stroke="{INK}" stroke-width="1.1"/></g>')                     # the key's T handle
    c.add(_at(d, x, foot, k))
    return {"box": (x - 30 * k, foot - 122 * k, x + 30 * k, foot), "top": (x, foot - 120 * k)}


def surfacing(c: Canvas, x: float, y: float, k: float) -> tuple[float, float, float, float]:
    """The emergency surfacing button on the wall at (x, y): a yellow-and-black box, the big red mushroom button
    under its clear flip cover, raised. Returns its box."""
    d = Canvas()
    d.shape(rounded_rect_d(-16, -16, 32, 32, 3), P.YELLOW, sw=1.4, light=None)
    d.line(" ".join(f"M{-16 + i * 8},16 l8,-8" for i in range(4)), 2.2, INK, 0.8)
    d.add(f'<circle cx="0" cy="-2" r="8" fill="{P.RED}" stroke="{INK}" stroke-width="1.3"/>'
          f'<ellipse cx="-2.5" cy="-4.5" rx="2.5" ry="1.4" fill="{lighten(P.RED, 0.5)}"/>')
    d.add(f'<path d="M-12,-14 L-10,-34 H10 L12,-14" fill="{P.LENS}" fill-opacity=".45" stroke="{INK}" '
          f'stroke-width="1"/>')                                                          # the cover, lifted
    c.add(_at(d, x, y, k))
    return (x - 17 * k, y - 35 * k, x + 17 * k, y + 17 * k)


def tank(c: Canvas, x: float, foot: float, k: float, running: bool) -> dict:
    """The preview tank standing on the deck at (x, foot), 140 wide and 128 tall: a steel stand with a shelf, on it
    a glass tank in a brass frame - water, sand and a coral, a small copy of the submarine swimming in it, an air
    stone sending up bubbles, a little pump on the side with its tube. Returns its box and the tank's top."""
    d = Canvas()
    for lx in (-62, 54):
        d.shape(rounded_rect_d(lx, -52, 8, 52, 1.5), P.METAL_DARK, sw=1.2, light=None)
    d.shape(rounded_rect_d(-60, -18, 112, 5, 1), P.METAL, sw=1.0, light=None)            # its shelf
    d.shape(rounded_rect_d(-66, -56, 132, 6, 1.5), P.METAL, sw=1.4, light=None)
    d.add(f'<rect x="-62" y="-124" width="124" height="68" fill="{WATER}" fill-opacity=".75"/>')
    d.add(f'<rect x="-62" y="-124" width="124" height="10" fill="{P.WHITE}" fill-opacity=".35"/>')   # the air
    d.add(f'<path d="M-62,-56 V-64 Q-30,-70 0,-64 T62,-66 V-56 Z" fill="{mix(P.SAND, VIOLET, 0.2)}"/>')
    coral(d, -40, -62, 0.8, "branch", P.PINK)
    coral(d, 40, -63, 0.7, "fan", P.ORANGE)
    sub = Canvas()
    submarine(sub, 0, 0, 1.0, open_=False, running=running, cradle=False)
    d.add(f'<g transform="translate(0,-86) scale(0.24)">{sub.render()}</g>')
    for j in range(4):
        d.add(f'<circle cx="{-50 + (j % 2) * 3}" cy="{-70 - j * 11}" r="{1.6 + j * 0.4}" fill="{P.WHITE}" '
              f'fill-opacity=".6" stroke="{P.WHITE}" stroke-width=".6"/>')
    d.add(f'<rect x="-62" y="-124" width="124" height="68" fill="none" stroke="{BRASS}" stroke-width="4"/>'
          f'<rect x="-64" y="-126" width="128" height="72" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    d.line("M-50,-120 L-36,-60", 1.4, P.WHITE, 0.6)                                       # the glass's glint
    d.shape(rounded_rect_d(64, -40, 14, 18, 2), P.CHARCOAL, sw=1.1, light=None)          # the pump
    d.line("M71,-40 V-50 Q71,-58 62,-58", 1.6, P.METAL_DARK)
    c.add(_at(d, x, foot, k))
    return {"box": (x - 66 * k, foot - 128 * k, x + 80 * k, foot), "top": foot - 126 * k}


def town(cc: Canvas, x0: float, y0: float, x1: float, y1: float, lit: tuple[int, ...]) -> None:
    """A coral town seen through a porthole: the reef's water, and on the sea floor rows of little shell houses -
    domes with a round door and a window each - linked by pipes; the `lit` ones with warm windows, the rest dark."""
    w, h = x1 - x0, y1 - y0
    cc.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(w)}" height="{n(h)}" fill="{WATER}"/>')
    cc.add(f'<rect x="{n(x0)}" y="{n(y0 + h * 0.5)}" width="{n(w)}" height="{n(h * 0.5)}" fill="{WATER_DEEP}" '
           f'fill-opacity=".35"/>')
    rows = ((0.5, 0.13, 5), (0.7, 0.17, 4), (0.9, 0.2, 3))
    idx = 0
    for ry, rs, count in rows:
        y = y0 + h * ry
        cc.line(f"M{n(x0)},{n(y + h * rs * 0.2)} H{n(x1)}", max(1.0, h * 0.012), mix(P.METAL, VIOLET, 0.3), 0.9)
        for j in range(count):
            hx = x0 + w * (j + 0.5) / count
            r_ = h * rs * 0.5
            on = idx in lit
            shell = mix(CORALS[idx % len(CORALS)], WATER, 0.25 if on else 0.55)
            cc.add(f'<path d="M{n(hx - r_)},{n(y)} A{n(r_)},{n(r_)} 0 0 1 {n(hx + r_)},{n(y)} Z" fill="{shell}" '
                   f'stroke="{INK}" stroke-width="{n(max(0.6, r_ * 0.08))}"/>')
            cc.add(f'<path d="M{n(hx - r_ * 0.6)},{n(y - r_ * 0.3)} Q{n(hx)},{n(y - r_ * 1.1)} {n(hx + r_ * 0.6)},'
                   f'{n(y - r_ * 0.3)}" fill="none" stroke="{darken(shell, 0.75)}" '
                   f'stroke-width="{n(max(0.5, r_ * 0.06))}"/>')
            cc.add(f'<circle cx="{n(hx + r_ * 0.35)}" cy="{n(y - r_ * 0.45)}" r="{n(r_ * 0.18)}" '
                   f'fill="{P.SUN if on else WATER_DEEP}" stroke="{INK}" stroke-width="{n(max(0.4, r_ * 0.04))}"/>')
            if on:
                cc.add(f'<circle cx="{n(hx + r_ * 0.35)}" cy="{n(y - r_ * 0.45)}" r="{n(r_ * 0.45)}" '
                       f'fill="{P.SUN}" fill-opacity=".25"/>')
            if j:                                         # the pipe from its neighbour
                px_ = x0 + w * (j - 0.5) / count
                cc.add(f'<rect x="{n(px_ - r_ * 0.12)}" y="{n(y - r_ * 0.5)}" width="{n(r_ * 0.24)}" '
                       f'height="{n(r_ * 0.5)}" fill="{mix(P.METAL, VIOLET, 0.3)}" stroke="{INK}" '
                       f'stroke-width="{n(max(0.4, r_ * 0.04))}"/>')
            idx += 1


def valve_panel(c: Canvas, x: float, foot: float, k: float, lit: tuple[int, ...], total: int = 12) -> dict:
    """The panel that wakes the town's houses, on its post at (x, foot), 96 wide and 124 tall: a steel cabinet
    face with rows of rotary switches - each with its pilot lamp above, green when on, and a small blank plate
    below - the `lit` ones turned to on. Returns its box and the switches' row."""
    d = Canvas()
    d.shape("M-30,0 H30 L26,-6 H-26 Z", P.METAL_DARK, sw=1.4, light=None)
    d.shape(rounded_rect_d(-7, -62, 14, 58, 2), mix(P.METAL, VIOLET, 0.25), sw=1.3, light=None)
    d.shape(rounded_rect_d(-48, -124, 96, 64, 4), mix(P.METAL, VIOLET, 0.3), sw=1.8, light=(-1, -1))
    d.add("".join(f'<circle cx="{bx}" cy="{by}" r="1.2" fill="{INK}"/>' for bx in (-44, 44) for by in (-120, -64)))
    cols, rows = 6, 2
    for i in range(min(total, cols * rows)):
        cx_, cy_ = -35 + (i % cols) * 14, -106 + (i // cols) * 28
        on = i in lit
        d.add(f'<circle cx="{cx_}" cy="{cy_ - 8}" r="2.4" fill="{P.GREEN if on else darken(P.GREEN, 0.4)}" '
              f'stroke="{INK}" stroke-width=".6"/>')                                    # its pilot lamp
        if on:
            d.add(f'<circle cx="{cx_}" cy="{cy_ - 8}" r="4.4" fill="{P.GREEN}" fill-opacity=".3"/>')
        d.add(f'<circle cx="{cx_}" cy="{cy_}" r="4.6" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width=".8"/>'
              f'<g transform="rotate({45 if on else -45} {cx_} {cy_})"><rect x="{cx_ - 1.2}" y="{cy_ - 5.6}" '
              f'width="2.4" height="7" rx="1" fill="{P.WHITE}"/></g>')                   # its rotary switch
        d.add(f'<rect x="{cx_ - 5}" y="{cy_ + 6.4}" width="10" height="3.6" rx=".6" fill="{P.CARD}" '
              f'stroke="{INK}" stroke-width=".5"/>')                                      # its plate
    c.add(_at(d, x, foot, k))
    return {"box": (x - 48 * k, foot - 126 * k, x + 48 * k, foot), "top": (x, foot - 124 * k),
            "switch": (x + 21 * k * (1 if lit else -1), foot - 106 * k)}


def map_table(c: Canvas, x: float, foot: float, k: float, route: int) -> dict:
    """The map table standing on the deck at (x, foot), 220 wide and 104 tall: a heavy table on four legs, on its
    slanting top a raised relief of the coral maze - its walls standing up as blocks, light on top and shaded in
    front - a small white plaque at each cave; red-headed pins at the caves of the route and a red string from
    pin to pin, `route` caves far; a brass dividers lying by it. Returns its box."""
    d = Canvas()
    for lx in (-100, -84, 76, 92):
        d.shape(rounded_rect_d(lx, -54, 8, 54, 1.5), P.WOOD_DARK, sw=1.2, light=None)
    d.shape(rounded_rect_d(-106, -60, 212, 10, 1.5), P.WOOD, sw=1.4, light=None)          # the apron
    d.shape("M-110,-60 L-90,-100 H90 L110,-60 Z", P.WOOD_LIGHT, sw=1.6, light=None)       # the top, at a slant
    d.shape("M-98,-63 L-82,-96 H82 L98,-63 Z", mix(P.SAND, VIOLET, 0.25), sw=1.2, light=None)   # the relief's bed

    def at(u: float, v: float) -> tuple[float, float]:                # (0..1 across, 0..1 from front to back)
        half = 98 - 16 * v
        return -half + 2 * half * u, -63 - 33 * v

    rnd = random.Random(5)
    for row in range(4, -1, -1):                                          # the walls, back rows first
        v = 0.12 + row * 0.19
        gaps = sorted(rnd.sample(range(1, 9), 3))
        for a, b in zip([0, *gaps], [*gaps, 9], strict=True):
            (x0, y0), (x1, _) = at(a / 9 + 0.03, v), at(b / 9 - 0.06, v)
            hgt = 4.0 - row * 0.4
            d.add(f'<rect x="{n(x0)}" y="{n(y0 - hgt)}" width="{n(x1 - x0)}" height="{n(hgt)}" '
                  f'fill="{mix(P.PINK, VIOLET, 0.45)}" stroke="{INK}" stroke-width=".6"/>'
                  f'<rect x="{n(x0)}" y="{n(y0 - hgt - 2)}" width="{n(x1 - x0)}" height="2" '
                  f'fill="{lighten(mix(P.PINK, VIOLET, 0.3), 0.3)}" stroke="{INK}" stroke-width=".5"/>')
    caves = [at(u, v) for u, v in ((0.12, 0.03), (0.3, 0.22), (0.52, 0.41), (0.36, 0.6), (0.62, 0.79), (0.86, 0.97))]
    for cx_, cy_ in caves:                                                # a plaque at each cave
        d.add(f'<rect x="{n(cx_ - 4.5)}" y="{n(cy_ + 0.5)}" width="9" height="3.6" rx=".6" fill="{P.WHITE}" '
              f'stroke="{INK}" stroke-width=".5"/>')
    on = caves[:max(2, route)]
    d.add(f'<polyline points="{" ".join(f"{n(cx_)},{n(cy_ - 4)}" for cx_, cy_ in on)}" fill="none" '
          f'stroke="{P.RED}" stroke-width="1.1"/>')                           # the string from pin to pin
    for cx_, cy_ in on:
        d.line(f"M{n(cx_)},{n(cy_)} V{n(cy_ - 4)}", 0.8, P.METAL_DARK)
        d.add(f'<circle cx="{n(cx_)}" cy="{n(cy_ - 4.6)}" r="1.9" fill="{P.RED}" stroke="{INK}" stroke-width=".5"/>')
    d.line("M70,-66 L84,-76 M70,-66 L78,-80", 1.4, BRASS)                                   # the dividers
    c.add(_at(d, x, foot, k))
    return {"box": (x - 110 * k, foot - 104 * k, x + 110 * k, foot), "top": foot - 100 * k,
            "route": (x + on[-1][0] * k, foot + on[-1][1] * k)}


def screen_view(cc: Canvas, x0: float, y0: float, x1: float, y1: float, gates: int, passed: int) -> None:
    """What the control desk's screen shows: the sea outside, a row of ring gates on the sea floor - the passed
    ones with a green light - and the submarine going through the next one."""
    w, h = x1 - x0, y1 - y0
    cc.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(w)}" height="{n(h)}" fill="{WATER_DEEP}"/>')
    cc.add(f'<rect x="{n(x0)}" y="{n(y0 + h * 0.78)}" width="{n(w)}" height="{n(h * 0.22)}" '
           f'fill="{mix(P.SAND, VIOLET, 0.4)}"/>')
    for i in range(gates):
        gx = x0 + w * (i + 0.5) / gates
        ok = i < passed
        cc.add(f'<ellipse cx="{n(gx)}" cy="{n(y0 + h * 0.5)}" rx="{n(w * 0.04)}" ry="{n(h * 0.24)}" fill="none" '
               f'stroke="{P.GREEN if ok else P.YELLOW}" stroke-width="{n(max(1.0, h * 0.04))}"/>')
    sub = Canvas()
    submarine(sub, 0, 0, 1.0, open_=False, running=True, cradle=False)
    sx_ = x0 + w * (passed + 0.5) / gates - w * 0.08
    cc.add(f'<g transform="translate({n(sx_)},{n(y0 + h * 0.62)}) scale({n(h / 600)})">{sub.render()}</g>')


def control_desk(c: Canvas, x: float, foot: float, k: float, passed: int, mug: bool = True,
                 screen: bool = True) -> dict:
    """The control desk standing on the deck at (x, foot), 180 wide and 132 tall: a steel desk with a slanted
    console of buttons and a joystick, a monitor on its arm showing the gates outside, and - `mug` - the cat's mug
    with its lid. Returns its box and the monitor's middle."""
    d = Canvas()
    d.shape(rounded_rect_d(-88, -56, 176, 56, 3), mix(P.METAL, VIOLET, 0.3), sw=1.8, light=None)   # the body
    for j in range(2):
        d.shape(rounded_rect_d(-80 + j * 82, -48, 76, 40, 2), mix(P.METAL_LIGHT, VIOLET, 0.2), sw=1.0,
                light=None)
    d.shape("M-92,-56 L-84,-72 H84 L92,-56 Z", mix(P.METAL, VIOLET, 0.4), sw=1.6, light=None)    # the console
    for i in range(6):
        d.add(f'<rect x="{-70 + i * 14}" y="-67" width="9" height="5" rx="1" '
              f'fill="{(P.RED, P.GREEN, P.YELLOW, P.TEAL, P.GREEN, P.ORANGE)[i]}" stroke="{INK}" stroke-width=".6"/>')
    d.line("M40,-64 L46,-80", 2.4, P.CHARCOAL)                                            # the joystick
    d.add(f'<circle cx="46" cy="-81" r="3.4" fill="{P.RED}" stroke="{INK}" stroke-width=".8"/>')
    d.line("M-4,-72 V-82", 3, P.METAL_DARK)                                               # the monitor's arm
    if screen:                                            # (or a station draws it as a container of its own)
        d.shape(rounded_rect_d(-36, -132, 72, 54, 3), P.CHARCOAL, sw=1.6, light=None)
        view = Canvas()
        screen_view(view, -32, -128, 32, -82, 4, passed)
        clip = d.shape(rounded_rect_d(-32, -128, 64, 46, 1.5), WATER_DEEP, sw=0, light=None, clip=True)
        d.add(f'<g clip-path="url(#{clip})">{view.render()}</g>')
    if mug:                                                                               # the cat's mug, lidded
        d.shape("M62,-72 V-86 H74 V-72 Z", P.TEAL, sw=1.1, light=(-1, -1))
        d.shape(rounded_rect_d(61, -89, 14, 4, 1.5), P.CHARCOAL, sw=0.8, light=None)
        d.add(f'<path d="M74,-84 q5,0 4,5 q-1,3 -4,2" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 92 * k, foot - 134 * k, x + 92 * k, foot), "screen": (x, foot - 105 * k)}


def monitor(c: Canvas, x: float, foot: float, k: float, playing: bool) -> dict:
    """The replay monitor on its stand at (x, foot), 90 wide and 120 tall: a base and a column, the screen showing
    the recording - the sea, the submarine in it, a play mark and the timeline with its playhead. Returns its box."""
    d = Canvas()
    d.shape("M-26,0 H26 L22,-6 H-22 Z", P.METAL_DARK, sw=1.4, light=None)
    d.shape(rounded_rect_d(-5, -64, 10, 60, 2), P.METAL, sw=1.2, light=None)
    d.shape(rounded_rect_d(-46, -122, 92, 62, 4), P.CHARCOAL, sw=1.8, light=None)
    view = Canvas()
    view.add(f'<rect x="-42" y="-118" width="84" height="46" fill="{WATER}"/>')
    coral(view, -30, -74, 0.6, "fan", P.PINK)
    coral(view, 30, -74, 0.6, "brain", P.ORANGE)
    sub = Canvas()
    submarine(sub, 0, 0, 1.0, open_=False, running=True, cradle=False)
    view.add(f'<g transform="translate({4 if playing else -10},-86) scale(0.16)">{sub.render()}</g>')
    clip = d.shape(rounded_rect_d(-42, -118, 84, 46, 1.5), WATER, sw=0, light=None, clip=True)
    d.add(f'<g clip-path="url(#{clip})">{view.render()}</g>')
    if not playing:
        d.add(f'<path d="M-6,-104 V-88 L8,-96 Z" fill="{P.WHITE}" fill-opacity=".9" stroke="{INK}" '
              f'stroke-width=".8"/>')                                                        # the play mark
    d.add(f'<rect x="-40" y="-69" width="80" height="3" rx="1.5" fill="{P.METAL_DARK}"/>'
          f'<rect x="-40" y="-69" width="{50 if playing else 12}" height="3" rx="1.5" fill="{P.RED}"/>'
          f'<circle cx="{10 if playing else -28}" cy="-67.5" r="3" fill="{P.WHITE}" stroke="{INK}" '
          f'stroke-width=".7"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 46 * k, foot - 124 * k, x + 46 * k, foot), "top": (x, foot - 122 * k)}


def exit_view(cc: Canvas, x0: float, y0: float, x1: float, y1: float, out: bool) -> None:
    """The labyrinth's exit seen through a porthole: coral walls closing in on both sides and arching over a gap
    of open water, light beyond it; the submarine coming through - `out`: already through, into the light."""
    w, h = x1 - x0, y1 - y0
    cc.add(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(w)}" height="{n(h)}" fill="{WATER}"/>')
    cc.add(f'<ellipse cx="{n(x0 + w * 0.62)}" cy="{n(y0 + h * 0.45)}" rx="{n(w * 0.22)}" ry="{n(h * 0.3)}" '
           f'fill="{lighten(WATER, 0.45)}"/>')                                          # the open water beyond
    rock = mix(P.PINK, VIOLET, 0.45)
    cc.add(f'<path d="M{n(x0)},{n(y0)} H{n(x0 + w * 0.42)} Q{n(x0 + w * 0.36)},{n(y0 + h * 0.5)} '
           f'{n(x0 + w * 0.42)},{n(y1)} H{n(x0)} Z" fill="{rock}" stroke="{INK}" stroke-width="1.4"/>')
    cc.add(f'<path d="M{n(x1)},{n(y0)} H{n(x0 + w * 0.84)} Q{n(x0 + w * 0.9)},{n(y0 + h * 0.5)} '
           f'{n(x0 + w * 0.84)},{n(y1)} H{n(x1)} Z" fill="{rock}" stroke="{INK}" stroke-width="1.4"/>')
    cc.add(f'<path d="M{n(x0 + w * 0.4)},{n(y0)} Q{n(x0 + w * 0.62)},{n(y0 + h * 0.22)} {n(x0 + w * 0.86)},'
           f'{n(y0)} Z" fill="{rock}" stroke="{INK}" stroke-width="1.4"/>')               # the arch over the gap
    rnd = random.Random(9)
    for i in range(7):
        coral(cc, x0 + w * rnd.choice((0.1, 0.25, 0.92)), y0 + h * (0.4 + i * 0.08), h / 200,
              rnd.choice(("branch", "fan", "brain")), CORALS[i % len(CORALS)])
    sub = Canvas()
    submarine(sub, 0, 0, 1.0, open_=False, running=True, cradle=False)
    cc.add(f'<g transform="translate({n(x0 + w * (0.66 if out else 0.5))},{n(y0 + h * 0.55)}) '
           f'scale({n(h / 520)})">{sub.render()}</g>')


def big_porthole(s: Strip, x: float, cy: float, r: float, view, name: str) -> tuple[float, float, float, float]:
    """A big porthole in the wall behind a station, at (x, cy) - or lower, so its rim stays under the frame's top:
    drawn into the wall, kept clear of the cast."""
    r = min(r, (lane(s).feet - 16) / 2.5)
    cy = max(cy, 6 + r * 1.22)
    c = Canvas()
    porthole(c, x, cy, r, r / 50, view=view)
    box = (x - r * 1.2, cy - r * 1.2, x + r * 1.2, cy + r * 1.2)
    s.put(0.95, c.render(), box, name, group=name)
    return box


def chamber(c: Canvas, x: float, foot: float, k: float, tapping: bool, side: int = 1) -> dict:
    """The pressure test chamber standing on the deck at (x, foot), 120 wide and 176 tall: a steel cylinder on
    four legs with a domed lid, a pressure gauge and a valve on top; in its front a thick round door - bolts all
    round it, its hinge and its locking handle - with a porthole in it, showing the phone in its sealed waterproof
    case hanging inside on its line; on its `side` two glove ports, their black rubber gloves reaching in -
    `tapping`: one glove's finger on the phone's screen. Returns its parts."""
    d = Canvas()
    for lx in (-46, -20, 14, 40):
        d.shape(rounded_rect_d(lx, -24, 6, 24, 1), P.METAL_DARK, sw=1.1, light=None)
    d.shape(rounded_rect_d(-56, -150, 112, 128, 10), mix(P.METAL, VIOLET, 0.25), sw=2.0, light=(-2, -2),
            shade_k=0.84)
    d.add("".join(f'<circle cx="{bx}" cy="{by}" r="1.3" fill="{INK}"/>' for bx in range(-50, 54, 10)
                  for by in (-146, -26)))
    d.shape("M-56,-150 Q0,-176 56,-150 Z", mix(P.METAL, VIOLET, 0.35), sw=1.8, light=None)     # the domed lid
    gauge(d, -18, -168, 7, 0.58 if tapping else 0.4)
    d.line("M-18,-161 V-156", 2.4, P.METAL_DARK)
    d.line("M20,-158 V-168 H30", 3, BRASS)                                                # the valve
    d.add(f'<circle cx="32" cy="-168" r="4" fill="none" stroke="{P.RED}" stroke-width="2"/>')
    dx = -6 * side                                                                         # the thick door
    d.add(f'<circle cx="{dx}" cy="-92" r="40" fill="{mix(P.METAL, VIOLET, 0.35)}" stroke="{INK}" '
          f'stroke-width="2"/>')
    d.add("".join(f'<circle cx="{n(dx + math.cos(a) * 35)}" cy="{n(-92 + math.sin(a) * 35)}" r="1.8" '
                  f'fill="{P.METAL_DARK}" stroke="{INK}" stroke-width=".5"/>'
                  for a in [i * math.pi / 8 for i in range(16)]))
    d.shape(rounded_rect_d(dx - 46 * side - 4, -104, 8, 24, 2), P.METAL_DARK, sw=1.0, light=None)   # its hinge
    d.line(f"M{dx + 36 * side},-92 h{12 * side}", 4, P.METAL_DARK)                        # its locking handle
    view = Canvas()                                                                         # through its porthole
    view.add(f'<rect x="{dx - 26}" y="-118" width="52" height="52" fill="{lighten(WATER, 0.25)}"/>')
    view.line(f"M{dx},-118 V-110", 1, P.METAL_DARK)
    view.shape(rounded_rect_d(dx - 10, -110, 20, 32, 3), P.LENS, sw=1.0, light=None)      # the waterproof case
    view.shape(rounded_rect_d(dx - 7, -107, 14, 26, 2), P.CHARCOAL, sw=0.8, light=None)   # the phone in it
    view.add(f'<rect x="{dx - 5.5}" y="-105" width="11" height="20" fill="{P.SCREEN_LIGHT}"/>'
             f'<rect x="{dx - 4}" y="-102" width="8" height="2" fill="{P.TEAL}"/>'
             f'<rect x="{dx - 4}" y="-98" width="5" height="2" fill="{P.METAL}"/>')
    if tapping:
        view.add(f'<path d="M{dx + side * 24},-72 Q{dx + side * 12},-88 {dx + side * 2},-92" fill="none" '
                 f'stroke="{INK}" stroke-width="6" stroke-linecap="round"/><path d="M{dx + side * 24},-72 '
                 f'Q{dx + side * 12},-88 {dx + side * 2},-92" fill="none" stroke="{P.CHARCOAL}" stroke-width="4" '
                 f'stroke-linecap="round"/>')                                                # a glove's finger
    view.add("".join(f'<circle cx="{dx - 14 - j}" cy="{-80 - j * 8}" r="{1.4 + j * 0.4}" fill="{P.WHITE}" '
                     f'fill-opacity=".7"/>' for j in range(3)))
    clip = d.shape(f"M{dx - 24},-92 A24,24 0 1 1 {dx + 24},-92 A24,24 0 1 1 {dx - 24},-92 Z", WATER, sw=0,
                   light=None, clip=True)
    d.add(f'<g clip-path="url(#{clip})">{view.render()}</g>')
    d.add(f'<circle cx="{dx}" cy="-92" r="25" fill="none" stroke="{INK}" stroke-width="6.6"/>'
          f'<circle cx="{dx}" cy="-92" r="25" fill="none" stroke="{BRASS}" stroke-width="4.2"/>')
    ports = [(side * 46, -66), (side * 46, -44)]
    for px, py in ports:                                                                   # the glove ports
        d.add(f'<ellipse cx="{px}" cy="{py}" rx="5" ry="9" fill="{P.CHARCOAL}" stroke="{BRASS}" '
              f'stroke-width="2.6"/><ellipse cx="{px}" cy="{py}" rx="6.4" ry="10.4" fill="none" stroke="{INK}" '
              f'stroke-width="1"/>')
    c.add(_at(d, x, foot, k))

    def at(px: float, py: float) -> tuple[float, float]:
        return x + px * k, foot + py * k

    return {"box": (x - 58 * k, foot - 176 * k, x + 58 * k, foot), "ports": [at(*p_) for p_ in ports],
            "top": at(0, -170)}


# ============================================================================ the stations
def beside(s: Strip, box: tuple, side: int, name: str, gap: float = 4.0) -> tuple[float, ...]:
    """Where a character stands right beside a thing's `box` on its `side` (-1 left, 1 right): close enough to
    reach it, then a little further out."""
    probe = _box(s, name, 0, lane(s).feet)
    half = (probe[2] - probe[0]) / 2
    x = box[2] + half + gap if side > 0 else box[0] - half - gap
    f = (x - s.lo) / (s.hi - s.lo)
    return (f, f + side * 0.03, f + side * 0.06, f + side * 0.1)


def camera_view(cc: Canvas, x0: float, y0: float, x1: float, y1: float, rec: bool, seed: int = 3) -> None:
    """Through the porthole, outside the hull: the labyrinth, and on its articulated arm reaching up from the hull
    below the glass, the underwater camera in its housing - two handles, the big dome port of its lens turned to
    the maze, its red lamp lit when it records."""
    w, h = x1 - x0, y1 - y0
    maze_view(cc, x0, y0, x1, y1, h / 200, seed, school=5)
    k = h / 120
    ax, ay = x0 + w * 0.62, y1 + 4                                          # the arm, out of the hull below
    jx, jy = x0 + w * 0.7, y0 + h * 0.66
    cx, cy = x0 + w * 0.5, y0 + h * 0.44
    for col in (INK, P.METAL_LIGHT):
        cc.add(f'<path d="M{n(ax)},{n(ay)} L{n(jx)},{n(jy)} L{n(cx + 18 * k)},{n(cy + 8 * k)}" fill="none" '
               f'stroke="{col}" stroke-width="{n((7 if col == INK else 4.6) * k)}" stroke-linejoin="round"/>')
    cc.add(f'<circle cx="{n(jx)}" cy="{n(jy)}" r="{n(4.4 * k)}" fill="{P.METAL}" stroke="{INK}" '
           f'stroke-width="{n(1.1 * k)}"/>')                                      # its joint
    cc.add(f'<rect x="{n(cx - 18 * k)}" y="{n(cy - 13 * k)}" width="{n(40 * k)}" height="{n(26 * k)}" '
           f'rx="{n(5 * k)}" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="{n(1.4 * k)}"/>')   # the housing
    cc.add(f'<path d="M{n(cx - 18 * k)},{n(cy - 10 * k)} A{n(13 * k)},{n(13 * k)} 0 0 0 {n(cx - 18 * k)},'
           f'{n(cy + 10 * k)} Z" fill="{P.LENS}" fill-opacity=".9" stroke="{INK}" stroke-width="{n(1.2 * k)}"/>')
    cc.add(f'<path d="M{n(cx - 10 * k)},{n(cy - 13 * k)} V{n(cy - 19 * k)} H{n(cx + 16 * k)} V{n(cy - 13 * k)}" '
           f'fill="none" stroke="{P.METAL}" stroke-width="{n(2.6 * k)}"/>')       # its handle
    cc.add(f'<rect x="{n(cx + 4 * k)}" y="{n(cy - 6 * k)}" width="{n(12 * k)}" height="{n(9 * k)}" '
           f'rx="{n(1.5 * k)}" fill="{P.SCREEN_DARK}" stroke="{INK}" stroke-width="{n(0.8 * k)}"/>')   # its back screen
    lamp_ = P.RED if rec else darken(P.RED, 0.5)
    cc.add(f'<circle cx="{n(cx + 16 * k)}" cy="{n(cy - 9 * k)}" r="{n(2.6 * k)}" fill="{lamp_}" stroke="{INK}" '
           f'stroke-width="{n(0.8 * k)}"/>')
    if rec:
        cc.add(f'<circle cx="{n(cx + 16 * k)}" cy="{n(cy - 9 * k)}" r="{n(5.5 * k)}" fill="{P.RED}" '
               f'fill-opacity=".3"/>')


def sleeves(s: Strip, who, ports: list, k: float) -> None:
    """The chamber's rubber gloves on a character's hands: from each glove port a black sleeve to a fist, the
    glove closed over the hand."""
    if who is None:
        return
    c = Canvas()
    for (px, py), side in zip(ports, ("right", "left"), strict=True):
        hx, hy, _ = s.grip(who, side)
        d = f"M{n(px)},{n(py)} Q{n((px + hx) / 2)},{n(max(py, hy) + 8 * k)} {n(hx)},{n(hy)}"
        c.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{n(8 * k + 2)}" stroke-linecap="round"/>'
              f'<path d="{d}" fill="none" stroke="{P.CHARCOAL}" stroke-width="{n(8 * k)}" stroke-linecap="round"/>')
        c.add(f'<circle cx="{n(hx)}" cy="{n(hy)}" r="{n(6.4 * k)}" fill="{P.CHARCOAL}" stroke="{INK}" '
              f'stroke-width="1.2"/>')                                                  # the glove on the hand
    s.put(who.bottom + 2, c.render(), None, group=who.group)




def lidded_mug(x: float, y: float, k: float) -> str:
    """The cat's mug, here with a lid against the damp: standing at (x, y)."""
    d = Canvas()
    d.shape("M-6,0 V-13 H6 V0 Z", P.TEAL, sw=1.1, light=(-1, -1))
    d.shape(rounded_rect_d(-7, -16, 14, 4, 1.5), P.CHARCOAL, sw=0.8, light=None)
    d.add(f'<circle cx="0" cy="-17" r="1.6" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width=".6"/>'
          f'<path d="M6,-11 q5,0 4,5 q-1,3 -4,2" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    return _at(d, x, y, k)


def engine_bay(c: Canvas, x: float, foot: float, k: float, running: bool = False) -> dict:
    """The submarine close up at its engine, on its cradle stand, its foot's middle at (x, foot), 150 wide and 112
    tall: a stretch of the violet hull in riveted plates with a porthole, the engine panel swung down on its hinges
    and in the bay the engine - three cylinders with their brass caps, the red drive belt, a pipe - and, running,
    the bay lamp lit. Returns its box."""
    d = Canvas()
    d.shape("M-40,0 H40 L32,-10 L22,-40 H-22 L-32,-10 Z", mix(P.METAL, VIOLET, 0.2), sw=1.6, light=None)
    d.shape("M-48,-36 Q0,-26 48,-36 V-44 Q0,-34 -48,-44 Z", P.CHARCOAL, sw=1.0, light=None)       # its pad
    clip = d.shape("M-75,-40 Q-80,-76 -75,-112 H75 Q80,-76 75,-40 Z", VIOLET, sw=0, light=None, clip=True)
    d.add(f'<g clip-path="url(#{clip})"><rect x="-80" y="-58" width="160" height="20" '
          f'fill="{darken(VIOLET, 0.8)}"/></g>')                                          # its belly in shade
    d.path("M-75,-40 Q-80,-76 -75,-112 H75 Q80,-76 75,-40 Z", "none", 2.0)
    d.line("M-40,-112 V-40 M40,-112 V-40", 1.1, darken(VIOLET, 0.68), 0.85)
    d.add("".join(f'<circle cx="{sx_}" cy="{ry}" r="1.3" fill="{darken(VIOLET, 0.55)}"/>'
                  for sx_ in (-43, -37, 37, 43) for ry in (-104, -92, -60, -48)))
    d.add(f'<circle cx="56" cy="-92" r="9" fill="{P.SUN if running else P.LENS}" stroke="{BRASS}" '
          f'stroke-width="3.4"/><circle cx="56" cy="-92" r="10.8" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    d.shape(rounded_rect_d(-32, -104, 64, 46, 4), P.CHARCOAL, sw=1.6, light=None)        # the bay
    for j in range(3):                                                                   # the cylinders
        d.shape(rounded_rect_d(-26 + j * 18, -94, 14, 28, 3), P.METAL, sw=1.0, light=(-1, -1))
        d.shape(rounded_rect_d(-24 + j * 18, -99, 10, 6, 2), BRASS, sw=0.8, light=None)
    d.line("M-28,-64 H28", 3, P.RED)                                                    # the drive belt
    d.line("M24,-96 Q32,-96 30,-86", 2.2, P.METAL_DARK)
    if running:
        glow(d, 0, -100, 3)
    d.shape("M-32,-58 L-38,-34 H38 L32,-58 Z", VIOLET, sw=1.6, light=None)               # the panel, swung down
    d.add("".join(f'<rect x="{bx}" y="-60" width="8" height="5" fill="{P.METAL_DARK}" stroke="{INK}" '
                  f'stroke-width=".6"/>' for bx in (-26, 18)))
    c.add(_at(d, x, foot, k))
    return {"box": (x - 78 * k, foot - 114 * k, x + 78 * k, foot), "top": foot - 112 * k}


def build_station(s: Strip, beat: str) -> None:
    """The dock: the submarine on its cradle, its engine panel open at the stern. "assemble": the agent at the
    open engine works on it, the professor (the cat in a mid strip) watches from the bow. "start": the agent at the
    starter console by the bow turns the key - the gauges come alive, the propeller turns and bubbles - the cat at
    the stern checks; the sparrow on the emergency surfacing button's box, after its big red button."""
    r = lane(s)
    c = Canvas()
    if s.h < 200:                                         # a strip: the submarine's engine bay alone, close
        sk = scale_for(s, 114, 156, 0.3, 1.0)
        x = inside(s, sx(s, 0.5 if beat == "assemble" else 0.4), 78 * sk, 78 * sk)
        box = engine_bay(c, x, r.feet, sk, running=beat == "start")["box"]
        parts = {"tower": (x, box[1])}
    else:
        sk = scale_for(s, 156, 300, 0.5 if beat == "assemble" else 0.4, 1.0)
        x = inside(s, sx(s, 0.5 if beat == "assemble" else 0.4), 150 * sk, 150 * sk)
        parts = submarine(c, x, r.feet, sk, open_=True, running=beat == "start")
        box = parts["box"]
    s.put(r.feet - 1, c.render(), box, "sub", group="sub")
    if beat == "assemble":
        stand(s, "agent", beside(s, box, -1, "agent", -30 * sk if s.h >= 200 else 2), "point", "smile", flip=False)
        stand(s, "cat" if mid(s) else "professor", beside(s, box, 1, "professor"), "think", "smile", flip=True)
        return
    ck = min(sk * 1.15, (r.feet - 8) / 124)
    cx = inside(s, box[2] + 34 * ck, 32 * ck, 32 * ck)                       # just past the bow
    cc = Canvas()
    con = starter(cc, cx, r.feet, ck, on=True)
    s.put(r.feet - 1, cc.render(), con["box"], "starter", group="starter")
    stand(s, "agent", beside(s, con["box"], 1, "agent"), "point", "smile", flip=True)
    stand(s, "cat", beside(s, box, -1, "cat", -30 * sk if s.h >= 200 else 2), "think", "smile", flip=False)
    if s.h >= 200:
        bc = Canvas()
        bb = surfacing(bc, cx, max(46 * ck, con["box"][1] - 40 * ck), ck * 0.9)
        if s.free(bb, 4):
            s.put(1.3, bc.render(), bb, "surfacing", group="surfacing")
            sparrow_on(s, cx, bb[1] + 1, "surfacing")


def preview_station(s: Strip, beat: str) -> None:
    """The preview tank: a small copy of the build running in a glass tank for everyone to see. "look": the
    professor (the caterpillar in a mid strip) and the cat look at it close up. "share": the agent shows it, the
    caterpillar checks it off on her clipboard; the sparrow on the tank's frame."""
    r = lane(s)
    tk = scale_for(s, 128, 150, 0.42, 1.0)
    x = inside(s, sx(s, 0.5), 70 * tk, 82 * tk)
    c = Canvas()
    t = tank(c, x, r.feet, tk, running=True)
    box = t["box"]
    s.put(r.feet - 1, c.render(), box, "tank", group="tank")
    # the golden floppy (an easter egg, `world_kit.hide`): stored on the stand's low shelf under the tank, never
    # taller than the shelf leaves room for
    fk = min(FLOPPY_K, (34 * tk - 4) / 24)
    stash(s, x + 22 * tk, r.feet - 18 * tk, r.feet - 0.9, group="tank", k=fk)
    a, b = (-1, 1) if not getattr(s, "mirror", False) else (1, -1)
    if beat == "look":
        stand(s, "caterpillar" if mid(s) else "professor", beside(s, box, a, "professor"), "think", "smile",
              flip=a > 0)
        stand(s, "cat", beside(s, box, b, "cat"), "point", "smile", flip=b > 0)
    else:
        stand(s, "agent", beside(s, box, a, "agent"), "point", "smile", flip=a > 0)
        stand(s, "caterpillar", beside(s, box, b, "caterpillar"), "present", "smile", flip=b > 0,
              hold=handheld.clipboard)
        sparrow_on(s, x - 40 * tk, t["top"], "tank")


def services_station(s: Strip, beat: str) -> None:
    """Hundreds of services: through a big porthole the coral town of little shell houses linked by pipes; at the
    panel of rotary switches before it the agent turns on only the few houses he needs. "dark": all asleep, the
    agent's finger at the panel, the caterpillar by the porthole worried by so many. "few": three houses and their
    three switches on, the cat at the porthole agrees; the sparrow on the panel."""
    r = lane(s)
    lit = () if beat == "dark" else (1, 6, 10)
    room = r.feet - 10
    pr = min(room * 0.4, span(s, 0.3) / 2.4)
    pbox = big_porthole(s, inside(s, sx(s, 0.34), pr * 1.2, pr * 1.2), min(room * 0.44, 6 + pr * 1.25), pr,
                        lambda cc, a, b, c_, d: town(cc, a, b, c_, d, lit), "town")
    vk = scale_for(s, 126, 96, 0.22, 0.85)
    side = 1 if not getattr(s, "mirror", False) else -1
    vx = inside(s, (pbox[2] if side > 0 else pbox[0]) + side * (56 * vk), 48 * vk, 48 * vk)
    c = Canvas()
    v = valve_panel(c, vx, r.feet, vk, lit)
    s.put(r.feet - 1, c.render(), v["box"], "panel", group="panel")
    stand(s, "agent", beside(s, v["box"], side, "agent"), "point", "smile", flip=side > 0)
    if beat == "dark":
        stand(s, "caterpillar", beside(s, pbox, -side, "caterpillar"), "think", "worry", flip=side < 0)
    else:
        stand(s, "cat", beside(s, pbox, -side, "cat"), "think", "smile", flip=side < 0)
        sparrow_on(s, vx, v["box"][1] + 2 * vk, "panel")


def monorepo_station(s: Strip, beat: str) -> None:
    """The map room: the table with the raised relief of the coral maze, a plaque at every cave, the route pinned
    and strung. "plot": the agent at the table points along the route, the caterpillar at its other end is afraid
    of getting lost. "lost": the route runs all the way, the professor (the cat in a mid strip) points at the cave
    they need, the caterpillar keeps her checklist, the cat's lidded mug on the table's corner."""
    r = lane(s)
    mk = scale_for(s, 104, 230, 0.6, 0.7 if s.h >= 200 else 1.0)
    x = inside(s, sx(s, 0.5), 110 * mk, 110 * mk)
    c = Canvas()
    m = map_table(c, x, r.feet, mk, 3 if beat == "plot" else 6)
    if beat == "lost":
        c.add(lidded_mug(x - 92 * mk, r.feet - 66 * mk, mk * 1.2))
    box = m["box"]
    s.put(r.feet - 1, c.render(), box, "map", group="map")
    a, b = (-1, 1) if not getattr(s, "mirror", False) else (1, -1)
    if beat == "plot":
        stand(s, "agent", beside(s, box, a, "agent"), "point", "smile", flip=a > 0)
        stand(s, "caterpillar", beside(s, box, b, "caterpillar"), "think", "worry", flip=b > 0)
    else:
        stand(s, "cat" if mid(s) else "professor", beside(s, box, a, "professor"), "point", "talk", flip=a > 0)
        stand(s, "caterpillar", beside(s, box, b, "caterpillar"), "present", "worry", flip=b > 0,
              hold=handheld.clipboard)


def testing_station(s: Strip, beat: str) -> None:
    """Manual testing by the agent: the control desk, its screen showing the submarine passing the gates outside.
    "case": one gate passed, the agent at the desk points at the screen, the caterpillar ticks the case off on her
    clipboard. "pass": three gates passed, the agent cheers, the cat checks, his lidded mug on the desk, the sparrow
    on the monitor."""
    r = lane(s)
    c = Canvas()
    passed = 1 if beat == "case" else 3
    if s.h < 200:                                         # a strip: the desk's screen alone, on its stand
        dk = scale_for(s, 126, 110, 0.3, 1.0)
        x = inside(s, sx(s, 0.5), 55 * dk, 55 * dk)
        c.shape(f"M{n(x - 30 * dk)},{n(r.feet)} H{n(x + 30 * dk)} L{n(x + 26 * dk)},{n(r.feet - 6 * dk)} "
                f"H{n(x - 26 * dk)} Z", P.METAL_DARK, sw=1.4, light=None)
        c.shape(rounded_rect_d(x - 5 * dk, r.feet - 64 * dk, 10 * dk, 60 * dk, 2 * dk), P.METAL, sw=1.2,
                light=None)
        box = (x - 55 * dk, r.feet - 126 * dk, x + 55 * dk, r.feet)
        s.put(r.feet - 1, c.render(), box, "desk", group="desk")
        sw_, sh_, top_ = 110, 64, -126
    else:
        dk = scale_for(s, 134, 190, 0.46, 1.0)
        x = inside(s, sx(s, 0.5), 92 * dk, 92 * dk)
        dsk = control_desk(c, x, r.feet, dk, passed, mug=beat == "pass", screen=False)
        box = dsk["box"]
        s.put(r.feet - 1, c.render(), box, "desk", group="desk")
        sw_, sh_, top_ = 72, 54, -132
    pen = Pen(s, x, r.feet, dk)                                  # the monitor: its picture inside its bezel
    body = pen.container("monitor", -sw_ / 2, top_, sw_, sh_, P.CHARCOAL, radius=3, sw=1.6, light=None)
    pad = pen.pad(sw_, sh_)
    view = Canvas()
    screen_view(view, -sw_ / 2 + pad, top_ + pad, sw_ / 2 - pad, top_ + sh_ - pad, 4, passed)
    pen.c.add(view.render())
    pen.child(body, "gates", -sw_ / 2 + pad, top_ + pad, sw_ / 2 - pad, top_ + sh_ - pad)
    s.put(r.feet - 0.9, pen.svg(), None, group="desk")
    a, b = (-1, 1) if not getattr(s, "mirror", False) else (1, -1)
    if beat == "case":
        stand(s, "agent", beside(s, box, a, "agent"), "point", "smile", flip=a > 0)
        stand(s, "caterpillar", beside(s, box, b, "caterpillar"), "present", "worry", flip=b > 0,
              hold=handheld.clipboard)
    else:
        stand(s, "agent", beside(s, box, b, "agent"), "cheer", "smile", flip=b > 0)
        stand(s, "cat", beside(s, box, a, "cat"), "think", "smile", flip=a > 0)
        sparrow_on(s, x, r.feet - 134 * dk, "desk")


def video_station(s: Strip, beat: str) -> None:
    """Video in the pull request: through a big porthole the underwater camera on its arm outside, filming the
    maze, its red lamp lit; inside the replay monitor on its stand. "rec": the agent at the porthole points at the
    camera, the cat at the monitor watches it record. "replay": the cat watches the recording on the monitor, the
    professor (the caterpillar in a mid strip) beside him."""
    r = lane(s)
    room = r.feet - 10
    pr = min(room * 0.42, span(s, 0.3) / 2.4)
    pbox = big_porthole(s, inside(s, sx(s, 0.34), pr * 1.2, pr * 1.2), min(room * 0.44, 6 + pr * 1.25), pr,
                        lambda cc, a, b, c_, d: camera_view(cc, a, b, c_, d, beat == "rec"), "port")
    mk = scale_for(s, 124, 92, 0.18, 0.85)
    side = 1 if not getattr(s, "mirror", False) else -1
    mx = inside(s, (pbox[2] if side > 0 else pbox[0]) + side * 52 * mk, 46 * mk, 46 * mk)
    mc = Canvas()
    mon = monitor(mc, mx, r.feet, mk, playing=beat == "replay")
    s.put(r.feet - 1, mc.render(), mon["box"], "monitor", group="monitor")
    if beat == "rec":
        stand(s, "agent", beside(s, pbox, -side, "agent"), "point", "smile", flip=side < 0)
        stand(s, "cat", beside(s, mon["box"], side, "cat"), "think", "smile", flip=side > 0)
    else:
        stand(s, "cat", beside(s, mon["box"], side, "cat"), "think", "smile", flip=side > 0)
        stand(s, "caterpillar" if mid(s) else "professor", beside(s, pbox, -side, "professor"), "point", "talk",
              flip=side < 0)


def check_station(s: Strip, beat: str) -> None:
    """How to check that it all works: through a big porthole the submarine comes out of the labyrinth's exit.
    "exit": the cat right at the glass times it on his stopwatch, the agent cheers. "log": out in the open water;
    the caterpillar checks the log on her clipboard, the cat holds the time, the sparrow on the porthole's rim."""
    r = lane(s)
    room = r.feet - 10
    pr = min(room * 0.44, span(s, 0.36) / 2.4)
    pbox = big_porthole(s, inside(s, sx(s, 0.5), pr * 1.2, pr * 1.2), min(room * 0.46, 6 + pr * 1.25), pr,
                        lambda cc, a, b, c_, d: exit_view(cc, a, b, c_, d, beat == "log"), "exit")
    a, b = (-1, 1) if not getattr(s, "mirror", False) else (1, -1)
    if beat == "exit":
        stand(s, "cat", beside(s, pbox, b, "cat"), "present", "smile", flip=b > 0, hold=handheld.stopwatch)
        stand(s, "agent", beside(s, pbox, a, "agent"), "cheer", "smile", flip=a > 0)
    else:
        stand(s, "caterpillar", beside(s, pbox, b, "caterpillar"), "present", "worry", flip=b > 0,
              hold=handheld.clipboard)
        stand(s, "cat", beside(s, pbox, a, "cat"), "present", "smile", flip=a > 0, hold=handheld.stopwatch)
        sparrow_on(s, (pbox[0] + pbox[2]) / 2, pbox[1] + 2, "exit")


def mobile_station(s: Strip, beat: str) -> None:
    """Mobile apps: the pressure test chamber, the phone in its sealed waterproof case hanging inside. "lower":
    the case lowered in, the agent beside the chamber points at it, the caterpillar is worried about the pressure.
    "tap": the agent's hands are in the chamber's gloves, tapping the phone; the cat checks the gauge, the sparrow
    on the lid's valve."""
    r = lane(s)
    ck = scale_for(s, 176, 120, 0.32, 1.0)
    side = 1 if not getattr(s, "mirror", False) else -1
    x = inside(s, sx(s, 0.42), 58 * ck, 58 * ck)
    c = Canvas()
    ch = chamber(c, x, r.feet, ck, tapping=beat == "tap", side=side)
    box = ch["box"]
    s.put(r.feet - 1, c.render(), box, "chamber", group="chamber")
    if beat == "tap":
        who = stand(s, "agent", beside(s, box, side, "agent", 2), "present", "smile", flip=side > 0)
        sleeves(s, who, ch["ports"], ck)
        stand(s, "cat", beside(s, box, -side, "cat"), "think", "smile", flip=side < 0)
        gx, gy = ch["top"]
        sparrow_on(s, gx + 32 * ck, gy + 2 * ck, "chamber")
    else:
        stand(s, "agent", beside(s, box, side, "agent"), "point", "smile", flip=side > 0)
        stand(s, "caterpillar", beside(s, box, -side, "caterpillar"), "think", "worry", flip=side < 0)


# ============================================================================ the finale
BAYS = ("build", "preview", "services", "monorepo", "testing", "video", "check", "mobile")


def finale(s: Strip) -> None:
    """The whole base at once, in cross-section: under the hull's arch two decks of rooms - in a low frame one -
    each with its station's thing: the submarine in the dock, the preview tank, the switch panel under the coral
    town's porthole, the map table, the control desk, the replay monitor under the camera's porthole, the
    labyrinth's exit through a porthole, the pressure chamber; each room's name on a brass plate over it, the cast
    in the rooms they work in."""
    s.decor = False
    s.dress = False
    s.indoor = True
    ledger(s)
    zoom(s)
    r = lane(s)
    maze_view(s.back, -6, -6, W + 6, r.feet + 4, max(0.8, s.unit), seed=21, school=7)   # the sea round the base
    deck(s.back, -6, W + 6, r.feet, s.h + 4, max(0.8, s.unit))
    left, right = s.lo + 14, s.hi - 14
    decks = 2 if s.h >= 400 else 1
    per = len(BAYS) // decks
    wide = (right - left) / per
    named = s.h >= 300
    size = 11.0
    th = tag_size("Ag", size)[1]
    widest = max(tag_size(s.word(key), size)[0] for key in BAYS)
    if widest > wide - 24:
        size = max(sets.LETTERING_MIN + 1, size * (wide - 24) / widest)
        th = tag_size("Ag", size)[1]
        widest = max(tag_size(s.word(key), size)[0] for key in BAYS)
    rows = 2 if named and widest > wide - 24 else 1                    # plates too wide for a room: two rows
    head = 10 + ((th + 6) * rows + 4 if named else 0)                  # each room's ceiling and its plates
    floors = [r.feet] if decks == 1 else [r.feet - (r.feet - 6) / 2 - 4, r.feet]
    c = Canvas()
    things = Canvas()
    tops = []
    perch = (0.0, 0.0)
    pen = Pen(s, 0, 0, 1)
    for d_, floor in enumerate(floors):
        ceil = (floors[d_ - 1] + 8 if d_ else 14.0)
        c.add(f'<rect x="{n(left - 4)}" y="{n(ceil - 4)}" width="{n(right - left + 8)}" height="{n(floor - ceil + 8)}" '
              f'fill="{WALL}" stroke="{STRAKE}" stroke-width="6"/>')
        pk = max(0.8, s.unit)                                          # the rooms' hull plates and rivets
        ph_, pw_ = (floor - ceil) / 3, 46 * pk
        for row in range(3):
            y = ceil + row * ph_
            for q in range(int((right - left) / pw_) + 1):
                x = left + q * pw_ + (row % 2) * pw_ / 2
                if x + 2 > right:
                    continue
                c.add(f'<rect x="{n(x)}" y="{n(y)}" width="{n(min(pw_, right - x))}" height="{n(ph_)}" '
                      f'fill="{PLATE if (q + row) % 3 == 0 else WALL}" stroke="{darken(WALL, 0.82)}" '
                      f'stroke-width=".9"/><circle cx="{n(x + 4)}" cy="{n(y + 4)}" r="1.1" '
                      f'fill="{darken(WALL, 0.7)}"/>')
        c.add(f'<rect x="{n(left)}" y="{n(floor - (floor - ceil) * 0.2)}" width="{n(right - left)}" '
              f'height="{n((floor - ceil) * 0.2)}" fill="{STRAKE}" fill-opacity=".85"/>')   # each deck's dado
        if d_:                                                         # the deck between them
            c.add(f'<rect x="{n(left - 4)}" y="{n(ceil - 8)}" width="{n(right - left + 8)}" height="10" '
                  f'fill="{mix(P.METAL, VIOLET, 0.3)}" stroke="{INK}" stroke-width="1.2"/>')
        room = floor - ceil - head - 6
        dado_y = floor - (floor - ceil) * 0.2
        for i in range(per):                                           # each room's window onto the labyrinth
            wx0, wx1 = left + i * wide + 10, left + (i + 1) * wide - 10
            if dado_y - 10 - (ceil + head + 4) > 40:
                window(c, wx0, wx1, ceil + head + 4, dado_y - 10, 0.7, seed=d_ * 10 + i, veil=0.12)
        pk_ = max(0.8, s.unit)                                          # a pipe run through the bulkheads
        c.add(f'<rect x="{n(left)}" y="{n(dado_y - 6 * pk_)}" width="{n(right - left)}" height="{n(6 * pk_)}" '
              f'fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="1"/>')
        for i in range(per + 1):                                       # the rooms' bulkheads
            bx = left + i * wide
            c.add(f'<rect x="{n(bx - 3)}" y="{n(ceil)}" width="6" height="{n(floor - ceil)}" fill="{STRAKE}" '
                  f'stroke="{INK}" stroke-width="1"/>')
        for i in range(per):
            key = BAYS[d_ * per + i]
            x = left + wide * (i + 0.42)
            fit = wide * 0.78
            if key == "build":
                k = min(fit / 300, room / 136)
                sub = submarine(things, x, floor, k, open_=False, running=True)
                tops.append(sub["box"][1])
                perch = sub["tower"]
            elif key == "preview":
                k = min(fit / 150, room / 128)
                tops.append(tank(things, x, floor, k, True)["box"][1])
            elif key == "services":
                k = min(fit / 92, room / 124) * 0.9
                tops.append(valve_panel(things, x, floor, k, (1, 6))["box"][1])
            elif key == "monorepo":
                k = min(fit / 230, room / 102)
                tops.append(map_table(things, x, floor, k, 4)["box"][1])
            elif key == "testing":
                k = min(fit / 190, room / 134)
                tops.append(control_desk(things, x, floor, k, 2, mug=False)["box"][1])
            elif key == "video":
                k = min(fit / 92, room / 124) * 0.9
                tops.append(monitor(things, x, floor, k, True)["box"][1])
            elif key == "check":
                pr = min(fit / 2.6, room * 0.36)
                porthole(things, x, floor - room * 0.5, pr, pr / 50,
                         view=lambda cc, a, b, c_, d: exit_view(cc, a, b, c_, d, True))
                tops.append(floor - room * 0.5 - pr * 1.2)
            else:
                k = min(fit / 120, room / 176)
                tops.append(chamber(things, x, floor, k, True)["box"][1])
            if named:
                ty = ceil + 6 + th / 2 + 4 + (th + 6) * (i % rows)
                holder = pen.tag(f"label{key}", left + wide * (i + 0.5), ty, s.word(key), size, BRASS, INK)
                s.put(2, "", holder.outer, f"label{key}")
    s.put(0.9, c.render(), None)
    s.put(1.2, things.render(), None)
    cast_ = {1: ("professor", "point"), 3: ("caterpillar", "think"), 4: ("agent", "wave"), 6: ("cat", "present")}
    for i, (name, pose) in cast_.items():
        d_, j = divmod(i, per)
        floor = floors[min(d_, len(floors) - 1)]
        ceil = floors[d_ - 1] + 8 if d_ and decks == 2 else 14.0
        x = left + wide * (j + 0.84)
        tall = min(s.tall * SIZE[name] * 1.4, _fit_tall(name, wide * 0.34, floor - ceil - head - 8))
        who = s.actor(name, min(x, s.hi - 30), floor, pose, "smile", flip=True, tall=tall, group=f"f{i}")
        if name == "cat":
            held(s, who, handheld.stopwatch)
    if decks == 2:                                                     # the sparrow on the submarine's tower
        tx, ty = perch
        s.actor("sparrow", tx, ty - 3, "stand", "smile", flip=True, tall=wide * 0.45, group="f0")
    if named:
        s.put(2, pen.svg(), None)


# ============================================================================ the opener
def hero_sub(c: Canvas, x: float, y: float, k: float) -> dict:
    """The submarine in full, side view, its hull's middle at (x, y), 330 long: a long teardrop hull in riveted
    plates - lit from above, its belly in shade - the sail with two lit windows, a periscope and a mast lamp, a
    deck hatch with its wheel, dive planes at the bow and the stern, the rudder, the propeller's blades turning in
    their guard ring with motion arcs, a small brass name plate, a row of portholes lit warm from inside - a
    small bird's silhouette in one - and the searchlight at the bow. Returns where its bow light and stern are."""
    d = Canvas()
    hull = ("M-150,0 C-150,-26 -110,-40 -60,-42 L110,-40 C150,-38 172,-20 172,0 C172,20 150,38 110,40 "
            "L-60,42 C-110,40 -150,26 -150,0 Z")
    d.shape("M-150,-4 L-176,-44 H-160 L-138,-14 Z", darken(VIOLET, 0.75), sw=1.6, light=None)   # the rudder, top
    d.shape("M-150,4 L-176,40 H-160 L-138,14 Z", darken(VIOLET, 0.75), sw=1.6, light=None)      # and bottom
    clip = d.shape(hull, VIOLET, sw=0, light=None, clip=True)
    d.add(f'<g clip-path="url(#{clip})"><rect x="-160" y="12" width="340" height="40" fill="{darken(VIOLET, 0.78)}"/>'
          f'<rect x="-160" y="-46" width="340" height="12" fill="{lighten(VIOLET, 0.22)}"/>'
          f'<path d="M-120,-30 Q20,-38 150,-26" fill="none" stroke="{P.WHITE}" stroke-width="3" '
          f'stroke-opacity=".35" stroke-linecap="round"/></g>')                        # light above, belly in shade
    seams = [-118, -86, -54, -22, 10, 42, 74, 106, 138]
    d.line(" ".join(f"M{sx_},-41 V41" for sx_ in seams), 1.2, darken(VIOLET, 0.68), 0.85)
    d.line("M-146,-12 C-60,-16 80,-16 168,-10 M-146,14 C-60,18 80,18 168,12", 1.0, darken(VIOLET, 0.7), 0.8)
    d.add("".join(f'<circle cx="{sx_ + dx}" cy="{ry}" r="1.3" fill="{darken(VIOLET, 0.55)}"/>'
                  for sx_ in seams for dx in (-3, 3) for ry in (-34, -24, 24, 34)))
    d.path(hull, "none", 2.2)
    for i, px in enumerate((-30, 0, 30, 60, 90)):                                      # portholes, lit warm
        d.add(f'<circle cx="{px}" cy="2" r="9" fill="{P.SUN}" stroke="{BRASS}" stroke-width="3.4"/>'
              f'<circle cx="{px}" cy="2" r="10.8" fill="none" stroke="{INK}" stroke-width="1.2"/>'
              f'<circle cx="{px}" cy="2" r="16" fill="{P.SUN}" fill-opacity=".18"/>')
        if i == 2:                                                                       # a small bird inside
            d.add(f'<path d="M{px - 3},6 q0,-7 4,-7 q3,0 3,3 l3,1 l-3,1 q0,3 -4,4 Z" fill="{darken(P.SUN, 0.45)}"/>')
    d.shape(rounded_rect_d(116, -8, 22, 9, 1.5), BRASS, sw=1.0, light=None)            # the name plate
    d.line("M120,-4 H134", 1, darken(BRASS, 0.6))
    sail = "M-16,-41 L-6,-86 H44 L58,-41 Z"                                             # the sail
    d.shape(sail, VIOLET, sw=2.0, light=(-2, -2), shade_k=0.84)
    d.line("M-10,-64 H50 M18,-86 V-41", 1.0, darken(VIOLET, 0.7), 0.8)
    for wx in (2, 30):
        d.add(f'<rect x="{wx}" y="-78" width="12" height="8" rx="2" fill="{P.SUN}" stroke="{INK}" '
              f'stroke-width="1"/>')
    d.line("M6,-86 V-112 H18", 3.4, P.METAL_DARK)                                       # the periscope
    d.shape(rounded_rect_d(16, -117, 10, 9, 2), P.METAL, sw=1.0, light=None)
    d.line("M36,-86 V-104", 2, P.METAL_DARK)                                            # the mast and its lamp
    d.add(f'<circle cx="36" cy="-106" r="3" fill="{P.RED}" stroke="{INK}" stroke-width=".8"/>')
    d.shape("M-80,-42 Q-80,-50 -70,-50 H-58 Q-48,-50 -48,-42 Z", VIOLET, sw=1.4, light=None)   # the deck hatch
    d.add(f'<circle cx="-64" cy="-56" r="5.5" fill="none" stroke="{P.RED}" stroke-width="2.2"/>'
          f'<path d="M-69.5,-56 H-58.5 M-64,-61.5 V-50.5" stroke="{P.RED}" stroke-width="1.2"/>')
    d.shape("M-120,-4 L-150,-12 L-148,-4 Z", darken(VIOLET, 0.75), sw=1.2, light=None)  # the stern planes
    d.shape("M120,10 L146,18 L120,18 Z", darken(VIOLET, 0.75), sw=1.2, light=None)      # the bow planes
    d.add(f'<ellipse cx="-168" cy="0" rx="9" ry="28" fill="none" stroke="{INK}" stroke-width="6"/>'
          f'<ellipse cx="-168" cy="0" rx="9" ry="28" fill="none" stroke="{P.METAL}" stroke-width="4"/>')
    for a in (0, 120, 240):                                                             # the blades, turning
        d.add(f'<ellipse cx="-168" cy="-10" rx="4" ry="12" fill="{BRASS}" stroke="{INK}" stroke-width="1" '
              f'transform="rotate({a} -168 0)" opacity=".85"/>')
    d.add(f'<path d="M-186,-30 A30,34 0 0 0 -186,30" fill="none" stroke="{INK}" stroke-width="1.6" '
          f'stroke-opacity=".55"/><path d="M-196,-22 A26,28 0 0 0 -196,22" fill="none" stroke="{INK}" '
          f'stroke-width="1.4" stroke-opacity=".4"/>')                                   # motion arcs
    d.shape("M168,-12 h12 v24 h-12 Z", P.METAL_DARK, sw=1.4, light=None)                # the searchlight
    d.add(f'<rect x="178" y="-9" width="4" height="18" fill="{P.YELLOW_PALE}" stroke="{INK}" stroke-width=".8"/>')
    c.add(_at(d, x, y, k))
    return {"bow": (x + 182 * k, y), "stern": (x - 196 * k, y)}


def rock_mass(c: Canvas, cx: float, base: float, w: float, h: float, tone: str, seed: int, lw: float = 1.6,
              arch: bool = False, dress: float = 0.0) -> None:
    """A mass of coral rock standing on the sea floor at (cx, base): stacked rounded lumps drawn as one body - the
    outline round all of them, then the fills over the seams - each lump's lower half in shade; `arch`: a
    passage through it, darker inside, a far wall seen through it paler."""
    rnd = random.Random(seed)
    lumps = []
    rows = 3
    for r_ in range(rows):
        count = max(1, 4 - r_)
        rw = w * (1 - r_ * 0.24)
        for q in range(count):
            lx = cx - rw / 2 + rw * (q + 0.5) / count + rnd.uniform(-0.05, 0.05) * w
            rr = rw / count * rnd.uniform(0.58, 0.72)
            ly = base - h * (0.12 + r_ * 0.3) - rr * 0.2
            lumps.append((lx, ly, rr))
    c.add("".join(f'<ellipse cx="{n(lx)}" cy="{n(ly)}" rx="{n(rr)}" ry="{n(rr * 0.82)}" fill="{INK}" '
                  f'stroke="{INK}" stroke-width="{n(lw * 2)}"/>' for lx, ly, rr in lumps))
    c.add(f'<rect x="{n(cx - w / 2)}" y="{n(base - h * 0.2)}" width="{n(w)}" height="{n(h * 0.2 + 2)}" '
          f'fill="{INK}"/>')
    c.add("".join(f'<ellipse cx="{n(lx)}" cy="{n(ly)}" rx="{n(rr)}" ry="{n(rr * 0.82)}" fill="{tone}"/>'
                  for lx, ly, rr in lumps))
    c.add(f'<rect x="{n(cx - w / 2 + lw)}" y="{n(base - h * 0.2)}" width="{n(w - 2 * lw)}" height="{n(h * 0.2)}" '
          f'fill="{tone}"/>')
    c.add("".join(f'<path d="M{n(lx - rr * 0.8)},{n(ly + rr * 0.1)} Q{n(lx)},{n(ly + rr * 0.75)} '
                  f'{n(lx + rr * 0.8)},{n(ly + rr * 0.1)}" fill="none" stroke="{darken(tone, 0.78)}" '
                  f'stroke-width="{n(rr * 0.22)}" stroke-opacity=".55" stroke-linecap="round"/>'
                  for lx, ly, rr in lumps))                                              # each lump's shade
    if dress:                                                          # brain-coral grooves, corals on the tops
        for q, (lx, ly, rr) in enumerate(lumps):
            for g_ in range(2):
                gy = ly - rr * (0.35 - g_ * 0.3)
                c.add(f'<path d="M{n(lx - rr * 0.6)},{n(gy)} q{n(rr * 0.15)},{n(-rr * 0.12)} {n(rr * 0.3)},0 '
                      f't{n(rr * 0.3)},0 t{n(rr * 0.3)},0 t{n(rr * 0.3)},0" fill="none" '
                      f'stroke="{darken(tone, 0.72)}" stroke-width="{n(max(0.8, rr * 0.05))}" '
                      f'stroke-linecap="round"/>')
            if q >= len(lumps) - 3 or rnd.random() < 0.35:
                coral(c, lx + rnd.uniform(-0.3, 0.3) * rr, ly - rr * 0.72, dress * rnd.uniform(0.8, 1.2),
                      rnd.choice(("branch", "fan", "branch", "kelp")), CORALS[(seed + q) % len(CORALS)])
    if arch:
        aw, ah = w * 0.2, h * 0.5
        c.add(f'<path d="M{n(cx - aw)},{n(base)} V{n(base - ah * 0.55)} A{n(aw)},{n(ah * 0.45)} 0 0 1 '
              f'{n(cx + aw)},{n(base - ah * 0.55)} V{n(base)} Z" fill="{darken(tone, 0.55)}" stroke="{INK}" '
              f'stroke-width="{n(lw)}"/>')
        c.add(f'<path d="M{n(cx - aw * 0.6)},{n(base)} Q{n(cx)},{n(base - ah * 0.5)} {n(cx + aw * 0.6)},'
              f'{n(base)} Z" fill="{mix(tone, WATER, 0.6)}"/>')                         # the far wall through it


def anemone(c: Canvas, x: float, y: float, k: float, color: str) -> None:
    """A sea anemone on the rock at (x, y): its column and a crown of waving tentacles."""
    c.add(f'<path d="M{n(x - 5 * k)},{n(y)} Q{n(x - 6 * k)},{n(y - 8 * k)} {n(x)},{n(y - 9 * k)} '
          f'Q{n(x + 6 * k)},{n(y - 8 * k)} {n(x + 5 * k)},{n(y)} Z" fill="{darken(color, 0.8)}" stroke="{INK}" '
          f'stroke-width="{n(max(0.7, k))}"/>')
    for i in range(7):
        a = math.radians(-160 + i * 23)
        tx, ty = x + math.cos(a) * 12 * k, y - 9 * k + math.sin(a) * 12 * k
        c.add(f'<path d="M{n(x)},{n(y - 9 * k)} Q{n((x + tx) / 2 + 3 * k)},{n((y - 9 * k + ty) / 2)} {n(tx)},{n(ty)}" '
              f'fill="none" stroke="{INK}" stroke-width="{n(3.4 * k + 1.2)}" stroke-linecap="round"/>'
              f'<path d="M{n(x)},{n(y - 9 * k)} Q{n((x + tx) / 2 + 3 * k)},{n((y - 9 * k + ty) / 2)} {n(tx)},{n(ty)}" '
              f'fill="none" stroke="{color}" stroke-width="{n(3.4 * k)}" stroke-linecap="round"/>')


def starfish(c: Canvas, x: float, y: float, k: float, color: str = P.ORANGE) -> None:
    """A starfish lying on the sand at (x, y)."""
    pts = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        rr = (9 if i % 2 == 0 else 3.6) * k
        pts.append(f"{n(x + math.cos(a) * rr)},{n(y + math.sin(a) * rr * 0.6)}")
    c.add(f'<polygon points="{" ".join(pts)}" fill="{color}" stroke="{INK}" stroke-width="{n(max(0.7, k))}" '
          f'stroke-linejoin="round"/>')


def jellyfish(c: Canvas, x: float, y: float, k: float) -> None:
    """A jellyfish drifting at (x, y): its translucent bell and trailing tentacles."""
    for i in range(5):
        tx = x + (-8 + i * 4) * k
        c.add(f'<path d="M{n(tx)},{n(y)} q{n(4 * k)},{n(8 * k)} 0,{n(16 * k)} t0,{n(16 * k)}" fill="none" '
              f'stroke="{lighten(P.PINK, 0.3)}" stroke-width="{n(1.6 * k)}" stroke-linecap="round"/>')
    c.add(f'<path d="M{n(x - 12 * k)},{n(y)} Q{n(x - 12 * k)},{n(y - 16 * k)} {n(x)},{n(y - 16 * k)} '
          f'Q{n(x + 12 * k)},{n(y - 16 * k)} {n(x + 12 * k)},{n(y)} Q{n(x)},{n(y - 4 * k)} {n(x - 12 * k)},{n(y)} Z" '
          f'fill="{lighten(P.PINK, 0.4)}" fill-opacity=".8" stroke="{INK}" stroke-width="{n(max(0.8, 1.1 * k))}"/>')


def big_fish(x: float, y: float, k: float, way: int, color: str, stripe: str) -> str:
    """A bigger fish: a deep body with stripes, a fin on its back, a forked tail, an eye."""
    c = Canvas()
    c.shape("M-24,0 Q-6,-20 22,-2 Q24,0 22,2 Q-6,20 -24,0 Z", color, sw=1.4, light=(-1, -1))
    c.shape("M-22,0 L-34,-12 L-31,0 L-34,12 Z", darken(color, 0.85), sw=1.2, light=None)
    c.shape("M-8,-12 L4,-20 L8,-10 Z", darken(color, 0.85), sw=1.0, light=None)
    c.line("M-6,-13 Q-2,0 -6,13 M4,-11 Q8,0 4,11", 3, stripe, 0.9)
    c.dot(14, -3, 2.2)
    return _at(c, x, y, k, mirror=way < 0)


def seascape(c: Canvas, x0: float, y0: float, x1: float, floor: float) -> list[tuple]:
    """The labyrinth for the opener, seen through the panoramic window: light water at the top darkening in bands,
    light rays; three layers of coral walls - far pale silhouettes, a middle wall with an arch passage, near masses
    dark and detailed with brain and branching coral, fans, tube sponges and anemones on them - a sand floor with
    ripples, starfish and shells, tall kelp swaying. The left of the window, where the professor's bubble goes,
    is kept open water down to the low near reef. Returns the boxes of the walls and kelp, for the bubble to keep
    clear of."""
    w = x1 - x0
    boxes = []
    for i, f in enumerate((0.0, 0.3, 0.55, 0.78)):                                    # the water, in bands
        band = y0 + (floor - y0) * f
        c.add(f'<rect x="{n(x0)}" y="{n(band)}" width="{n(w)}" height="{n(floor - band + 2)}" '
              f'fill="{mix(lighten(WATER, 0.32), WATER_DEEP, i / 3.4)}"/>')
    for rx in (90, 300, 520, 700):                                                     # light from the surface
        c.add(f'<path d="M{rx},{n(y0)} h60 L{rx + 260},{n(floor)} h-170 Z" fill="{P.WHITE}" fill-opacity=".1"/>')
    far = mix(mix(VIOLET, WATER, 0.6), P.WHITE, 0.15)
    for i, (cx, ww, hh) in enumerate(((500, 260, 220), (740, 280, 260))):           # far, pale
        rock_mass(c, cx, floor - 150, ww, hh, far, 40 + i, lw=1.0)
        boxes.append((cx - ww / 2, floor - 150 - hh, cx + ww / 2, floor - 150))
    mid_ = mix(VIOLET, P.PINK, 0.25)
    rock_mass(c, 570, floor - 70, 330, 270, mid_, 51, lw=1.4, arch=True, dress=1.3)      # the middle wall
    rock_mass(c, 790, floor - 80, 200, 240, mid_, 52, lw=1.4, dress=1.3)
    boxes += [(405, floor - 380, 735, floor - 70), (690, floor - 360, 890, floor - 80)]
    c.add(f'<path d="M{n(x0)},{n(floor - 60)} Q{n(x0 + w * 0.3)},{n(floor - 80)} {n(x0 + w * 0.55)},{n(floor - 62)} '
          f'T{n(x1)},{n(floor - 70)} V{n(floor + 10)} H{n(x0)} Z" fill="{mix(P.SAND, VIOLET, 0.3)}" stroke="{INK}" '
          f'stroke-width="1.6"/>')                                                        # the sand floor
    c.line(" ".join(f"M{n(x0 + 30 + q * 70)},{n(floor - 30 + (q % 3) * 9)} q18,-6 36,0 t36,0" for q in range(12)),
           1.2, darken(mix(P.SAND, VIOLET, 0.3), 0.75), 0.8)                              # its ripples
    near = darken(mix(VIOLET, P.PINK, 0.35), 0.72)
    rock_mass(c, 120, floor - 10, 300, 140, near, 61, lw=2.0, dress=0.0)                 # near masses, dark: low
    boxes.append((-30, floor - 180, 270, floor - 10))                                    # on the left
    rock_mass(c, 790, floor - 10, 240, 230, near, 62, lw=2.0, dress=1.8)
    for kx, ky, kh in ((400, floor - 40, 330), (425, floor - 34, 260), (650, floor - 40, 300),
                       (675, floor - 36, 240)):                                           # tall kelp
        boxes.append((kx - 26, ky - kh, kx + 8, ky))
        strand = f"M{kx},{n(ky)} q-22,-{kh / 6:.0f} 0,-{kh / 3:.0f} t0,-{kh / 3:.0f} t0,-{kh / 3:.0f}"
        c.add(f'<path d="{strand}" fill="none" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>'
              f'<path d="{strand}" fill="none" stroke="{P.LEAF}" stroke-width="6" stroke-linecap="round"/>')
    heads = ((90, 110, "brain", P.ORANGE, 2.0), (170, 100, "branch", P.PINK, 1.8), (40, 90, "fan", P.YELLOW, 1.8),
             (760, 210, "fan", P.PINK, 2.4), (820, 170, "brain", P.YELLOW, 2.0), (720, 150, "branch", P.ORANGE, 2.0))
    for cx, up, kind, color, kk in heads:                                               # corals on the near masses
        coral(c, cx, floor - up, kk, kind, color)
    for ax, ay, color in ((150, floor - 100, P.PINK), (740, floor - 110, P.YELLOW), (300, floor - 66, P.ORANGE)):
        anemone(c, ax, ay, 2.0, color)
    for sx_, th_ in ((480, 70), (500, 54), (520, 62)):                                   # tube sponges
        c.add(f'<rect x="{sx_ - 7}" y="{n(floor - 50 - th_)}" width="14" height="{th_}" rx="6" fill="{P.YELLOW}" '
              f'stroke="{INK}" stroke-width="1.8"/><ellipse cx="{sx_}" cy="{n(floor - 50 - th_ + 2)}" rx="5" ry="2" '
              f'fill="{darken(P.YELLOW, 0.6)}"/>')
    starfish(c, 360, floor - 24, 2.2)
    starfish(c, 580, floor - 18, 1.8, P.PINK)
    c.add(f'<path d="M420,{n(floor - 20)} q8,-12 16,0 Z" fill="{P.CREAM}" stroke="{INK}" stroke-width="1.4"/>')
    return boxes


def opener(st: Stage, accent: str):
    """The observation deck of the base, one hero: through a huge panoramic window the big violet submarine
    gliding through the coral labyrinth - its blades turning in their guard, its portholes lit, its searchlight's
    cone lighting the coral ahead; the labyrinth in three layers - pale far walls, a middle wall with an arch, dark
    near masses with corals, sponges and anemones - kelp, a sand floor with starfish, a school of small fish in a
    flowing S, two bigger fish and a jellyfish; light rays come down and the water where the title goes is calm.
    In front the riveted deck with a grating and a brass railing; the professor under his bubble, the caterpillar
    at the glass with her hands on the railing, the agent waving to the submarine, the cat timing it, the sparrow
    on the railing."""
    ledger(st)
    c = st.back
    floor = 1000.0
    st.keep_clear(*seascape(c, -6, -6, W + 6, 900))
    sk, sx_ = 1.15, 590                                                                 # the hero, right of the bubble
    bx, by = sx_ + 182 * sk, 400
    c.add(f'<path d="M{n(bx)},{n(by - 8)} L846,{n(by + 40)} V{n(by + 320)} L{n(bx)},{n(by + 10)} Z" '
          f'fill="{P.YELLOW_PALE}" fill-opacity=".38"/>')                                # the searchlight's cone
    c.add(f'<ellipse cx="800" cy="{n(by + 300)}" rx="60" ry="26" fill="{P.YELLOW_PALE}" fill-opacity=".3"/>')
    hero_sub(c, sx_, by, sk)
    st.keep_clear((sx_ - 200 * sk, by - 120 * sk, sx_ + 186 * sk, by + 46 * sk))
    for j in range(7):                                                                 # bubbles off the blades
        c.add(f'<circle cx="{n(sx_ - 200 * sk - (j % 3) * 8)}" cy="{n(by - 30 - j * 24)}" r="{n(3 + j * 1.2)}" '
              f'fill="{P.WHITE}" fill-opacity=".55" stroke="{P.WHITE}" stroke-width="1.4"/>')
    for j in range(30):                                                                # a school, in a flowing S
        t_ = j / 29
        fx = 400 + t_ * 380
        fy = 560 + math.sin(t_ * math.pi * 2) * 34 + (j % 3 - 1) * 12
        c.add(fishy(fx, fy, 0.9 + (j % 4) * 0.18, 1, P.YELLOW))
    c.add(big_fish(250, 310, 1.3, 1, P.ORANGE, P.WHITE))
    st.keep_clear((200, 280, 300, 340))
    c.add(big_fish(700, 640, 1.4, -1, P.TEAL, P.YELLOW))
    jellyfish(c, 100, 300, 1.8)
    st.keep_clear((76, 268, 124, 360))
    frame = FRAME                                                                      # the window's frame
    c.add(f'<path d="M-6,-6 H{W + 6} V940 H-6 Z M30,-6 V860 Q30,894 64,894 H776 Q810,894 810,860 V-6 Z" '
          f'fill="{frame}" fill-rule="evenodd" stroke="{INK}" stroke-width="2.4"/>')
    st.keep_clear((-6, -6, 30, 940), (810, -6, W + 6, 940), (-6, 894, W + 6, 940))
    c.add(f'<path d="M30,-6 V860 Q30,894 64,894 H776 Q810,894 810,860 V-6" fill="none" stroke="{BRASS}" '
          f'stroke-width="3"/>')
    c.add("".join(f'<circle cx="{n(x)}" cy="916" r="3.2" fill="{darken(frame, 0.6)}" stroke="{INK}" '
                  f'stroke-width=".8"/>' for x in range(20, W, 34)))                     # its bolts
    c.add("".join(f'<circle cx="{n(xx)}" cy="{n(y)}" r="3" fill="{darken(frame, 0.6)}" stroke="{INK}" '
                  f'stroke-width=".8"/>' for xx in (14, 826) for y in range(20, 900, 40)))
    c.add(f'<path d="M560,-6 L360,894 H420 L620,-6 Z" fill="{P.WHITE}" fill-opacity=".07"/>')   # the glass's glint
    deck(c, -6, W + 6, floor, H + 4, 1.8)
    c.add(f'<rect x="-6" y="940" width="{W + 12}" height="{floor - 940}" fill="{STRAKE}" stroke="{INK}" '
          f'stroke-width="2"/>')
    c.add(f'<rect x="-6" y="{floor}" width="{W + 12}" height="22" fill="{P.METAL_DARK}" stroke="{INK}" '
          f'stroke-width="1.6"/>')                                                         # the grating strip
    c.line(" ".join(f"M{x},{floor + 2} V{floor + 20}" for x in range(0, W, 9)), 1.4, P.METAL_LIGHT, 0.8)
    for x in range(40, W, 140):                                                      # the brass railing
        c.add(f'<rect x="{x - 4}" y="954" width="8" height="{floor - 954}" fill="{BRASS}" stroke="{INK}" '
              f'stroke-width="1.4"/><circle cx="{x}" cy="952" r="6" fill="{BRASS}" stroke="{INK}" '
              f'stroke-width="1.4"/>')
    c.add(f'<rect x="-6" y="944" width="{W + 12}" height="10" rx="5" fill="{BRASS}" stroke="{INK}" '
          f'stroke-width="1.6"/>')
    c.add(f'<rect x="-6" y="972" width="{W + 12}" height="5" rx="2.5" fill="{BRASS}" stroke="{INK}" '
          f'stroke-width="1.2"/>')
    prof = st.actor("professor", 150, 1100, "explain", "talk", tall=360)
    st.speaker(prof, width=70, left=12, air=CLEAR_MM)
    st.actor("caterpillar", 345, 1040, "present", "worry", flip=True, tall=300, group="caterpillar")
    st.actor("agent", 552, 1116, "wave", "smile", flip=True, tall=350, group="agent")
    cat = st.actor("cat", 730, 1126, "present", "smile", flip=True, tall=330, group="cat")
    st.hold(cat, handheld.stopwatch)
    st.actor("sparrow", 440, 944, "stand", "smile", tall=120, group="sparrow")      # on the brass railing
    drawn = st.render()
    drawn.holders, drawn.links, drawn.ports = st.holders, st.links, st.ports
    return drawn


SEA.stations.extend([
    Station("build", _framed(build_station), ("assemble", "start")),
    Station("preview", _framed(preview_station), ("look", "share")),
    Station("services", _framed(services_station), ("dark", "few")),
    Station("monorepo", _framed(monorepo_station), ("plot", "lost")),
    Station("testing", _framed(testing_station), ("case", "pass")),
    Station("video", _framed(video_station), ("rec", "replay")),
    Station("check", _framed(check_station), ("exit", "log")),
    Station("mobile", _framed(mobile_station), ("lower", "tap")),
])
SEA.backdrop = backdrop
SEA.alternate = True                                       # never one moment on two pages in a row
SEA.finale = finale
stories.OPENERS["deepsea"] = opener
hide(SEA, "preview", "share")

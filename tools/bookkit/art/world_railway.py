"""The railway: the world of chapter 11 (how development looks now: Agentic SDLC).

A country station on a summer day, seen from its near platform. In front, the platform's paving where the cast
stands, its stone coping and yellow line; lower down the near track on its ballast - sleepers, chairs, rails with
head and foot, fishplates at the joints; across it the far platform's low face, its paving, and the station
building along it: one continuous facade of ruby brick with dark ruby pilasters and arches, arched windows with
their frames and sills, panelled doors under fanlights, gas lamps on their brackets, the wall clock at 4:04, and
the platform canopy on cast-iron brackets with its fretted valance; the sky over the roof. Nothing stands free in
front of it but what a station is about. Trains stand and run on the near track at their true size, cut by the
frame's sides when they are longer than it, never by its top or foot; in a low strip, where a carriage cannot
stand whole, the station shows a thing that can - the handcar, a flat wagon. The chapter's colour is ruby. The
stations, one per section of the chapter, each with one big thing the cast works with:

1. small     a small task: the professor hands the agent a telegram form, the handcar waiting on the rails; then
             the agent pumps the handcar off down the line, the dust flying from its wheels;
2. roles     how the roles change: the caterpillar runs her model railway with its controller in her hand - the
             prototype; then the cat oils the real engine's coupling rods with his long-spouted oil can;
3. plan      a big task: the timetable board under its own little roof - the professor signs the sheet at its
             foot, then the agent chalks in a new run;
4. parallel  several tasks at once: the points - the track splits into three in the frame, the agent throws the
             big ground lever with its counterweight, a train waits on each road;
5. to-pr     from code to the pull request: the cat taps a wheel with the wheel tapper's hammer and the
             caterpillar listens; then the agent screws up the coupling between two buffer beams, the professor
             looking on;
6. to-prod   from merge to production: the semaphore's arm has dropped and the train pulls out in its steam; at the
             terminus the engine stands buffers to buffers at the buffer stop;
7. metrics   how to tell it got better: the platform clock on its bracket - the professor holds his pocket watch
             up to it, the train in exactly on time;
8. no-human  development without a human: the train glides past with nobody in its cab, the cast watching from
             the platform bench, the sparrow on its back;
9. check     checking where you are still needed: the emergency-stop box on its post, the sparrow diving at it,
             the cat's paw on its cover.

No words in the pictures but the finale's names of the stations.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten, mix
from . import characters, handheld, sets, stories
from .footers import Strip
from .ink import INK, Canvas, ellipse_d, lettering, n, rounded_rect_d
from .openers import IN_FRONT, Box, Stage, W
from .world_fair import lane, zoom
from .world_kit import SIZE, Pen, clock_hands, connect, ledger, port, tag_size
from .world_courtyard import merged
from .world_kitchen import _box, low
from .world_camp import mug
from .world_moon import checklist, height, mates
from .world_harbour import in_hand
from .world_sea import sparrow_on
from .worlds import Station, world

RAILWAY = world("railway", opener="railway_station")   # the story `railway` (stories.py), see `opener`

_at = sets._at

RUBY = P.RUBY                                      # the station's brick
RUBY_DEEP = darken(RUBY, 0.66)
BRICK = RUBY
BRICK_DARK = darken(RUBY, 0.74)
MORTAR = darken(RUBY, 0.56)
STONE_ = mix(P.BEIGE, P.STONE, 0.35)              # dressed stone: sills, coping, plinth
PAVING = mix(P.BEIGE, RUBY, 0.06)
IRON = mix(P.CHARCOAL, P.GREEN, 0.18)             # cast iron, painted the dark green of old railways
GLASS = mix(P.SKY, P.METAL_DARK, 0.45)
BALLAST = mix(P.STONE, P.METAL_DARK, 0.25)
SLEEPER = mix(P.WOOD_DARK, P.CHARCOAL, 0.3)
DUST = mix(P.BEIGE, P.WOOD_PALE, 0.4)
SKY_TOP = mix(P.SKY, P.BLUE, 0.15)
SKY_LOW = mix(P.SKY, P.YELLOW_PALE, 0.5)


def at(d: Canvas, x: float, y: float, k: float, way: int = 1) -> str:
    """A drawing made facing right with its origin at (x, y), set down at scale k, facing `way`."""
    return _at(d, x, y, k, mirror=way < 0)


def puffs(c: Canvas, x0: float, y0: float, rise: float, drift: float, r0: float, r1: float, count: int,
          seed: int, color: str = P.WHITE) -> None:
    """A plume of steam or dust: many puffs, small and dense where they leave, wider, paler and thinner as they
    rise and drift back; the far end first, so the dense root lies on top."""
    rnd = random.Random(seed)
    lobes = []
    for i in range(count):
        t = i / max(1, count - 1)
        cx = x0 + drift * t ** 1.2 + rnd.uniform(-2, 2)
        cy = y0 - rise * t
        r = r0 + (r1 - r0) * t ** 1.1
        for _ in range(2 if t < 0.2 else 3):
            lobes.append((cx + rnd.uniform(-0.5, 0.5) * r, cy + rnd.uniform(-0.3, 0.3) * r,
                          r * rnd.uniform(0.75, 1.1), t))
    for px, py, r, t in sorted(lobes, key=lambda p: -p[3]):
        fill = mix(color, P.METAL_LIGHT, 0.08 + 0.35 * t)
        c.add(f'<g opacity="{0.9 - 0.72 * t:.2f}">')
        c.path(f"M{n(px - r)},{n(py + r * 0.35)} Q{n(px - r * 1.15)},{n(py - r * 0.5)} {n(px - r * 0.35)},"
               f"{n(py - r * 0.55)} Q{n(px - r * 0.1)},{n(py - r * 1.15)} {n(px + r * 0.45)},{n(py - r * 0.75)} "
               f"Q{n(px + r * 1.15)},{n(py - r * 0.45)} {n(px + r)},{n(py + r * 0.3)} Q{n(px)},{n(py + r * 0.75)} "
               f"{n(px - r)},{n(py + r * 0.35)} Z", fill, 1.0, mix(INK, fill, 0.7))
        c.add("</g>")


# ============================================================================ the camera and the ground
class Line:
    """Where things are in a frame, front to back: the feet on the near platform, its coping, the near track's
    rail tops, the far platform's coping and the foot of the station building; `t` the tallest of the cast,
    the measure of everything else."""

    def __init__(self, s: Strip, roads: int = 1) -> None:
        self.feet = lane(s).feet
        self.t = max(height(s, x) for x in ("professor", "agent", "cat", "caterpillar"))
        t = self.t
        front = max(8.0, 0.1 * t)
        if not low(s):                                                 # a deep platform: the whole cast stands on
            front = deep_front(s)                                      # the paving, below the track's edge
        self.kerb = self.feet - front
        self.rail = self.kerb - max(6.0, 0.075 * t)
        self.rails = [self.rail]                                       # the roads of the track, near to far
        for q in range(1, roads):                                       # the roads beyond, each a train's step back
            self.rails.append(self.rail - q * max(12.0, 0.2 * t))
        self.cope = self.rails[-1] - max(8.0, 0.16 * t)
        self.wall = self.cope - max(4.0, 0.05 * t)


CLEAR = 0.1                    # the air over the tallest head (or raised hand) to the platform's edge, in its height


def deep_front(s: Strip) -> float:
    """How deep the near platform is in a frame that is not a strip: from the feet line up to the coping, the tallest
    of the cast and the air over its head (its arms raised in cheer included), so that nobody standing on the
    paving is drawn over the track or over anything standing on it."""
    t = max(height(s, x) for x in ("professor", "agent", "cat", "caterpillar"))
    return t * (1 + CLEAR) + 4


def agent_h(s: Strip) -> float:
    return height(s, "agent")


BACK = 0.15                     # the share of a tall frame over the far platform: the station building


LEAN = 0.45                     # a pole or a tool held up from the deep platform at a train: that much forward per rise
FAR_TRACK = 0.7                # a tall frame's rolling stock, seen beyond the deep platform: that much smaller


def setting(s: Strip, vehicle: float = 0.0, roads: int = 1, steam: float = 0.0, rider: bool = False) -> Line:
    """Choose the camera for a station and draw what stands behind it. `vehicle`: the height (in the agent's
    heights, at the cast's distance) of a carriage on the near track that must stand whole in the frame, steam
    (`steam`, more) included if there is room - the cast steps back until it does. In a frame taller than a strip
    the track lies beyond the deep platform, so the rolling stock is drawn smaller with the distance
    (`FAR_TRACK`), unless one of the cast rides it (`rider`) and it keeps his scale."""
    s.track_depth = 1.0 if low(s) or rider else FAR_TRACK
    vehicle *= s.track_depth
    if not low(s):                                                     # the cast steps back until the track,
        def fits(tall: float) -> bool:                                 # the far platform and the building show
            s.tall, s.unit, s._room = tall, tall / 137, None           # over their heads, and the carriage whole
            g = Line(s, roads)
            return g.rail >= max(BACK * s.h + g.rail - g.wall, agent_h(s) * vehicle + 6)
        top = s.tall
        if not fits(top):                                              # the biggest cast that fits, by halving
            lo_, hi_ = top * 0.2, top
            for _ in range(16):
                mid = (lo_ + hi_) / 2
                lo_, hi_ = (mid, hi_) if fits(mid) else (lo_, mid)
            fits(lo_)
    g = Line(s, roads)
    s.line = g
    s.steam = bool(steam) and g.rail - agent_h(s) * (vehicle + steam) > 4
    backdrop_draw(s, g)
    return g


def prepare(s: Strip, index: int) -> None:
    """Before a station: the close camera (`zoom`), the ledger of its containers and lines."""
    ledger(s)
    zoom(s)
    s.index = index
    s.track_depth = 1.0 if low(s) else FAR_TRACK                       # the rolling stock beyond a deep platform
    feet = lane(s).feet
    names = ("professor", "cat", "agent", "caterpillar")               # the professor in every frame size
    if low(s):                                                         # a close-up: the cast nearly fills it
        top = max(_box(s, name, 0, feet)[3] - _box(s, name, 0, feet)[1] for name in names)
        s.tall *= (feet - 6) / top
    widest = max(_box(s, name, 0, feet)[2] - _box(s, name, 0, feet)[0] for name in names)
    s.tall *= min(1.0, (s.hi - s.lo) * 0.19 / widest)                  # as big as on the moon base
    s.unit = s.tall / 137


def backdrop_draw(s: Strip, g: Line) -> None:
    """The sky (veiled into the paper with the rest of the backdrop), then the building, the far platform, the
    tracks and the near platform - drawn over the veil, so the ruby keeps its colour; only a narrow band at the
    very top melts into the paper."""
    sets.sky(s.back, SKY_TOP, SKY_LOW, g.wall, W)
    c = Canvas()
    facade(c, s, g)
    far_platform(c, g)
    for q, rail in reversed(list(enumerate(g.rails))):
        bottom = g.kerb + 1 if q == 0 else g.rails[q - 1] + 2
        track(c, -6, W + 6, rail, bottom, max(0.5, g.t / 200 * (1 - q * 0.22)), seed=s.index * 3 + q, far=q > 0)
    platform(c, g.kerb, s.h + 4, max(0.7, g.t / 180))
    band = min(s.h * 0.16, 40.0)
    c.fade(-10, -10, W + 20, band + 10, [(0, P.PAPER, 1), (0.25, P.PAPER, 0.85), (1, P.PAPER, 0)])
    s.put(0.05, c.render(), None)


def far_platform(c: Canvas, g: Line) -> None:
    """The far platform: its flagstones under the building, the stone coping and its white edge, and its face of
    blue engineering brick in courses down to the ballast."""
    t = g.t
    c.add(f'<rect x="-6" y="{n(g.wall)}" width="{W + 12}" height="{n(g.cope - g.wall + 1)}" '
          f'fill="{mix(PAVING, P.STONE, 0.35)}"/>')
    step = max(10.0, 0.2 * t)
    c.line(" ".join(f"M{n(q)},{n(g.wall + 1)} L{n(q - 2)},{n(g.cope)}" for q in range(0, W + 20, int(step))), 0.7,
           INK, 0.35)
    face_bottom = g.rails[-1] + 4
    face = mix(P.METAL_DARK, P.BLUE, 0.2)
    c.add(f'<rect x="-6" y="{n(g.cope)}" width="{W + 12}" height="{n(face_bottom - g.cope)}" fill="{face}"/>')
    course = max(3.0, 0.04 * t)
    rows = max(2, int((face_bottom - g.cope) / course))
    rnd = random.Random(int(g.t))
    bricks: dict[str, list[str]] = {}
    for r in range(rows):
        y = g.cope + (face_bottom - g.cope) * r / rows
        hgt = (face_bottom - g.cope) / rows
        bw = course * 2.6
        off = (r % 2) * bw / 2
        q = -off
        while q < W + 6:
            tone = rnd.choice((face, lighten(face, 0.1), darken(face, 0.88)))
            if tone == face:                                           # the face itself shows there
                q += bw
                continue
            bricks.setdefault(tone, []).append(f"M{n(q + 0.4)},{n(y + 0.4)} h{n(bw - 0.8)} v{n(hgt - 0.8)} "
                                               f"h{n(-bw + 0.8)} Z")
            q += bw
    merged(c, bricks)
    ch = max(3.0, 0.035 * t)
    c.add(f'<rect x="-6" y="{n(g.cope - ch * 0.4)}" width="{W + 12}" height="{n(ch)}" fill="{STONE_}" '
          f'stroke="{INK}" stroke-width="1"/><rect x="-6" y="{n(g.cope - ch * 0.4)}" width="{W + 12}" '
          f'height="{n(ch * 0.3)}" fill="{P.WHITE}"/>')


def track(c: Canvas, x0: float, x1: float, rail: float, bottom: float, k: float, seed: int = 0,
          far: bool = False) -> None:
    """A track seen from the side with its rail tops at `rail`: the ballast bed down to `bottom` as a surface of
    packed grey stones, the sleeper ends under the rail, the rail itself - the broad foot on its chairs, the web,
    the head - with a pair of fishplates bolted at each joint."""
    rail += 2.4 * k                                                    # `rail` is the head's top: wheels stand on it
    rnd = random.Random(seed)
    base = BALLAST if not far else lighten(BALLAST, 0.06)
    c.add(f'<path d="M{n(x0)},{n(bottom)} V{n(rail + 6 * k)} H{n(x1)} V{n(bottom)} Z" fill="{darken(base, 0.72)}"/>')
    if bottom - rail > 8:                                              # the stones of the bed, one path a tone
        stones: dict[str, list[str]] = {}
        tones = (base, lighten(base, 0.18), darken(base, 0.86), mix(base, P.WOOD_PALE, 0.15))
        size = max(14.0, 13 * k)
        y = rail + 6 * k
        while y < bottom:
            x = x0 - rnd.uniform(0, size)
            while x < x1:
                w = rnd.uniform(0.8, 1.3) * size
                h = w * rnd.uniform(0.5, 0.7)
                tone = rnd.choice(tones + (None,))                     # a gap now and then: the bed shows
                if tone is None:
                    x += w + rnd.uniform(0.6, 2.0)
                    continue
                stones.setdefault(tone, []).append(
                    f"M{x:.0f},{y + h:.0f}q-1,{-h:.0f} {w * 0.5 + 1:.0f},{-h - 1:.0f}t{w * 0.5 + 1:.0f},{h + 1:.0f}z")
                x += w + rnd.uniform(0.6, 2.0)
            y += size * 0.55
        merged(c, stones)
    q0 = x0 - (seed * 7) % 22                                          # the sleeper ends and their chairs: dashes
    sw = max(0.4, 0.6 * k)
    for y, hgt, dash, gap, start, fill in ((rail + 5.1 * k, 5 * k + 2 * sw, 16 * k + 2 * sw, 8 * k - 2 * sw,
                                            q0 - sw, INK), (rail + 5.1 * k, 5 * k, 16 * k, 8 * k, q0, SLEEPER),
                                           (rail + 2.4 * k, 2 * k, 8 * k, 16 * k, q0 + 4 * k, P.METAL_DARK)):
        c.add(f'<path d="M{n(start)},{n(y)} H{n(x1 + 24 * k)}" stroke="{fill}" stroke-width="{n(hgt)}" '
              f'stroke-dasharray="{n(dash)} {n(gap)}"/>')
    c.add(f'<rect x="{n(x0)}" y="{n(rail + 1.2 * k)}" width="{n(x1 - x0)}" height="{n(1.6 * k)}" '
          f'fill="{darken(P.METAL, 0.72)}"/>'
          f'<rect x="{n(x0)}" y="{n(rail - 0.2 * k)}" width="{n(x1 - x0)}" height="{n(1.6 * k)}" '
          f'fill="{darken(P.METAL, 0.84)}"/>'
          f'<rect x="{n(x0)}" y="{n(rail - 2.4 * k)}" width="{n(x1 - x0)}" height="{n(2.4 * k)}" '
          f'fill="{P.METAL}" stroke="{INK}" stroke-width="{n(max(0.4, 0.6 * k))}"/>'
          f'<rect x="{n(x0)}" y="{n(rail - 2.4 * k)}" width="{n(x1 - x0)}" height="{n(0.7 * k)}" '
          f'fill="{P.METAL_PALE}"/>')
    q = x0 + 60 * k - (seed * 13) % 60
    while q < x1:                                                      # the joints and their fishplates
        c.add(f'<rect x="{n(q - 7 * k)}" y="{n(rail - 0.6 * k)}" width="{n(14 * k)}" height="{n(2.4 * k)}" '
              f'fill="{P.METAL_DARK}"/>')
        c.line(f"M{n(q)},{n(rail - 2.4 * k)} v{n(2.4 * k)}", max(0.5, 0.6 * k), INK)
        q += 150 * k


def platform(c: Canvas, kerb: float, bottom: float, k: float) -> None:
    """The near platform where the cast stands: the stone coping along its edge with its joints, the white edge
    line, the yellow line with its studs, then rows of flagstones widening towards the reader."""
    c.add(f'<rect x="-6" y="{n(kerb)}" width="{W + 12}" height="{n(bottom - kerb)}" fill="{darken(PAVING, 0.8)}"/>')
    c.add(f'<rect x="-6" y="{n(kerb)}" width="{W + 12}" height="{n(6 * k)}" fill="{STONE_}" stroke="{INK}" '
          f'stroke-width="1.2"/><rect x="-6" y="{n(kerb)}" width="{W + 12}" height="{n(1.6 * k)}" '
          f'fill="{P.WHITE}"/>')
    c.line(" ".join(f"M{q},{n(kerb + 1.6 * k)} V{n(kerb + 6 * k)}" for q in range(20, W, 70)), 0.8, INK, 0.4)
    stripe = kerb + 7.5 * k
    c.add(f'<rect x="-6" y="{n(stripe)}" width="{W + 12}" height="{n(4.4 * k)}" fill="{P.YELLOW}" stroke="{INK}" '
          f'stroke-width=".8"/>')
    c.add(f'<path d="M-6,{n(stripe + 2.2 * k)} H{W + 6}" stroke="{darken(P.YELLOW, 0.8)}" '
          f'stroke-width="{n(1.6 * k)}" stroke-dasharray="{n(1.6 * k)} {n(9 - 1.6 * k)}" stroke-linecap="round"/>')
    y, row = stripe + 6 * k, 0
    rnd = random.Random(23)
    slabs: dict[str, list[str]] = {}
    while y < bottom:
        rh = (7 + row * 4) * max(0.6, k)
        sw_ = rh * 2.6
        x = -rnd.uniform(0, 30) - (row % 2) * sw_ / 2
        while x < W + 6:
            tone = (PAVING, lighten(PAVING, 0.1), darken(PAVING, 0.94), mix(PAVING, P.STONE, 0.2))[rnd.randrange(4)]
            slabs.setdefault(tone, []).append(f"M{n(x + 1)},{n(y + 1)} h{n(sw_ - 2)} v{n(rh - 2)} h{n(-sw_ + 2)} Z")
            x += sw_
        y += rh
        row += 1
    merged(c, slabs, f' stroke="{INK}" stroke-width=".6" stroke-opacity=".35"')


# ============================================================================ the station building
def facade(c: Canvas, s: Strip, g: Line) -> None:
    """The station building along the far platform, one calm front across the frame: a plinth of dressed stone,
    walls of ruby brick in courses, dark ruby pilasters between the bays, tall arched windows with cream frames,
    glazing bars and stone sills, now and then a panelled double door under its fanlight; gas lamps on scrolled
    brackets; the platform canopy on cast-iron brackets with its fretted valance; over it the upper floor's arched
    windows, the wall clock at 4:04 in its gable, the cornice, the slate roof and its chimneys."""
    t = getattr(s, "facade_t", None) or g.t * 0.82                     # across the track: a little smaller
    foot = g.wall
    bay = 0.95 * t
    pil = 0.13 * t
    canopy = foot - 1.92 * t                                           # the valance's lower edge
    string = foot - 2.3 * t
    cornice = foot - 3.25 * t
    roof = cornice - 0.5 * t
    rnd = random.Random(s.index * 13 + 5)
    if roof > -10:                                                     # the roof and its chimneys against the sky
        c.add(f'<path d="M-6,{n(cornice)} L{n(0.2 * t - 6)},{n(roof)} H{n(W - 0.2 * t + 6)} L{W + 6},{n(cornice)} Z" '
              f'fill="{mix(P.SLATE if hasattr(P, "SLATE") else P.METAL_DARK, P.BLUE, 0.15)}" stroke="{INK}" '
              f'stroke-width="1.4"/>')
        for q in range(1, int((cornice - roof) / max(4.0, 0.06 * t))):
            y = roof + q * max(4.0, 0.06 * t)
            c.line(f"M{n(0.2 * t * (y - roof) / (cornice - roof) - 6)},{n(y)} H{n(W + 6)}", 0.5, INK, 0.3)
        for cx in (0.18 * W, 0.62 * W):
            cx += (s.index * 41) % 90
            c.add(f'<rect x="{n(cx)}" y="{n(roof - 0.32 * t)}" width="{n(0.22 * t)}" height="{n(0.34 * t)}" '
                  f'fill="{BRICK_DARK}" stroke="{INK}" stroke-width="1.4"/>'
                  f'<rect x="{n(cx - 0.02 * t)}" y="{n(roof - 0.36 * t)}" width="{n(0.26 * t)}" height="{n(0.05 * t)}" '
                  f'fill="{STONE_}" stroke="{INK}" stroke-width="1.2"/>')
            for p_ in range(2):
                c.add(f'<rect x="{n(cx + (0.03 + p_ * 0.1) * t)}" y="{n(roof - 0.43 * t)}" width="{n(0.07 * t)}" '
                      f'height="{n(0.07 * t)}" fill="{P.TERRACOTTA}" stroke="{INK}" stroke-width="1"/>')
    top = max(-6.0, cornice)
    c.add(f'<rect x="-6" y="{n(top)}" width="{W + 12}" height="{n(foot - top)}" fill="{BRICK}"/>')
    course = max(4.0, 0.042 * t)                                       # the brick courses and their joints
    bw = course * 2.6
    lw = max(0.5, 0.004 * t)
    y = foot - 0.14 * t
    lines, row = [], 0
    joints: list[list[str]] = [[], []]
    odd: dict[str, list[str]] = {}
    while y > top:
        lines.append(f"M-6,{n(y)} H{W + 6}")
        joints[row % 2].append(f"M-6,{n(y - course / 2)} H{W + 6}")    # the head joints: a dashed line a course
        off = (row % 2) * bw / 2
        if row % 3 == 0:
            for _ in range(int(W / bw / 6)):
                bx = rnd.randrange(int(W / bw) + 1) * bw + off
                odd.setdefault(rnd.choice((lighten(BRICK, 0.1), darken(BRICK, 0.88))), []).append(
                    f"M{n(bx)},{n(y - course)} h{n(bw)} v{n(course)} h{n(-bw)} Z")
        y -= course
        row += 1
    merged(c, odd)
    c.line(" ".join(lines), lw, MORTAR, 0.55)
    for q, ds in enumerate(joints):                                    # thin dashes as tall as a course
        if ds:
            c.add(f'<path d="{" ".join(ds)}" fill="none" stroke="{MORTAR}" stroke-opacity=".55" '
                  f'stroke-width="{n(course)}" stroke-dasharray="{n(lw)} {n(bw - lw)}" '
                  f'stroke-dashoffset="{n(6 - q * bw / 2)}"/>')
    c.add(f'<rect x="-6" y="{n(foot - 0.14 * t)}" width="{W + 12}" height="{n(0.14 * t)}" '
          f'fill="{mix(P.STONE, P.METAL_DARK, 0.3)}" stroke="{INK}" stroke-width="1.2"/>')   # the plinth
    c.line(f"M-6,{n(foot - 0.07 * t)} H{W + 6}", 0.8, INK, 0.4)
    if string > top:
        c.add(f'<rect x="-6" y="{n(string - 0.05 * t)}" width="{W + 12}" height="{n(0.06 * t)}" fill="{STONE_}" '
              f'stroke="{INK}" stroke-width="1.2"/>')                                           # the string course
    if cornice > -6:
        c.add(f'<rect x="-6" y="{n(cornice)}" width="{W + 12}" height="{n(0.1 * t)}" fill="{STONE_}" '
              f'stroke="{INK}" stroke-width="1.4"/>')
        merged(c, {STONE_: [f"M{n(q * 0.12 * t)},{n(cornice + 0.1 * t)} h{n(0.05 * t)} v{n(0.04 * t)} "
                            f"h{n(-0.05 * t)} Z" for q in range(int(W / (0.12 * t)) + 1)]},
               f' stroke="{INK}" stroke-width=".8"')                   # its dentils
    x0 = -((s.index * 0.37 * bay) % bay) - pil
    bays = []
    x = x0
    while x < W + bay:
        bays.append(x)
        x += bay
    clock_bay = len(bays) // 2
    for bx in bays:                                                    # the pilasters
        c.add(f'<rect x="{n(bx - pil / 2)}" y="{n(top)}" width="{n(pil)}" height="{n(foot - 0.14 * t - top)}" '
              f'fill="{BRICK_DARK}" stroke="{INK}" stroke-width="1"/>')
    for i, bx in enumerate(bays):
        mid = bx + bay / 2
        door = (i + s.index) % 4 == 1
        if door:                                                       # 1.3 times the tallest of the cast
            opening(c, mid, foot - 0.14 * t, 0.62 * t, 1.62 * t, t, door=True)
        else:
            opening(c, mid, foot - 0.42 * t, 0.5 * t, 1.26 * t, t)
        if string - 0.12 * t > top + 0.2 * t and i != clock_bay:
            opening(c, mid, string - 0.12 * t, 0.36 * t, 0.66 * t, t)
        if i == clock_bay and string > top:                             # the wall clock in the middle bay
            r = 0.22 * t
            cy = string - 0.48 * t
            c.add(f'<circle cx="{n(mid)}" cy="{n(cy)}" r="{n(r + 0.04 * t)}" fill="{STONE_}" stroke="{INK}" '
                  f'stroke-width="1.6"/><circle cx="{n(mid)}" cy="{n(cy)}" r="{n(r)}" fill="{P.WHITE}" '
                  f'stroke="{INK}" stroke-width="1.2"/>')
            c.line(" ".join(f"M{n(mid + math.cos(a) * r * 0.82)},{n(cy + math.sin(a) * r * 0.82)} "
                            f"L{n(mid + math.cos(a) * r * 0.95)},{n(cy + math.sin(a) * r * 0.95)}"
                            for a in (q * math.pi / 6 for q in range(12))), max(0.8, 0.01 * t), INK)
            c.add(clock_hands(mid, cy, r * 0.5, r * 0.78, max(1.2, 0.016 * t)))
    for i, bx in enumerate(bays):                                      # gas lamps on every other pilaster
        if (i + s.index) % 2 == 0:
            gas_lamp(c, bx, foot - 1.22 * t, t)
    canopy_front(c, canopy, t, bays)


def opening(c: Canvas, mid: float, sill: float, w: float, h: float, t: float, door: bool = False) -> None:
    """An arched opening in the wall, its sill's middle at (mid, sill): a window - the brick arch of dark ruby
    voussoirs over it, the cream frame, the glazing bars, the stone sill - or a door, two leaves of panels under a
    fanlight."""
    top = sill - h
    rr = w / 2
    arch = (f"M{n(mid - rr)},{n(sill)} V{n(top + rr)} A{n(rr)},{n(rr)} 0 0 1 {n(mid + rr)},{n(top + rr)} "
            f"V{n(sill)} Z")
    ring = 0.07 * t
    c.add(f'<path d="M{n(mid - rr - ring)},{n(top + rr)} A{n(rr + ring)},{n(rr + ring)} 0 0 1 {n(mid + rr + ring)},'
          f'{n(top + rr)} H{n(mid + rr)} A{n(rr)},{n(rr)} 0 0 0 {n(mid - rr)},{n(top + rr)} Z" fill="{BRICK_DARK}" '
          f'stroke="{INK}" stroke-width="1.2"/>')
    c.add(f'<path d="M{n(mid)},{n(top - ring)} l{n(-0.035 * t)},0 l{n(0.01 * t)},{n(ring + 0.02 * t)} '
          f'h{n(0.05 * t)} l{n(0.01 * t)},{n(-ring - 0.02 * t)} Z" fill="{STONE_}" stroke="{INK}" '
          f'stroke-width="1"/>')                                                                # the keystone
    lw = max(0.8, 0.012 * t)
    if door:
        c.add(f'<path d="{arch}" fill="{RUBY_DEEP}" stroke="{INK}" stroke-width="1.6"/>')
        fan = top + rr
        c.add(f'<path d="M{n(mid - rr * 0.86)},{n(fan)} A{n(rr * 0.86)},{n(rr * 0.86)} 0 0 1 {n(mid + rr * 0.86)},'
              f'{n(fan)} Z" fill="{GLASS}" stroke="{P.CREAM}" stroke-width="{n(lw * 1.6)}"/>')
        c.line(" ".join(f"M{n(mid)},{n(fan)} L{n(mid + math.cos(a) * rr * 0.86)},{n(fan - math.sin(a) * rr * 0.86)}"
                        for a in (math.pi * q / 4 for q in range(1, 4))), lw, P.CREAM)
        for side in (-1, 1):                                           # the two leaves and their panels
            lx = mid + (0 if side > 0 else -rr * 0.86)
            c.add(f'<rect x="{n(lx)}" y="{n(fan + 0.02 * t)}" width="{n(rr * 0.86)}" '
                  f'height="{n(sill - fan - 0.02 * t)}" fill="{mix(RUBY_DEEP, P.WOOD_DARK, 0.4)}" stroke="{INK}" '
                  f'stroke-width="1.2"/>')
            for py, ph in ((0.08, 0.42), (0.56, 0.38)):
                c.add(f'<rect x="{n(lx + rr * 0.14)}" y="{n(fan + (sill - fan) * py)}" width="{n(rr * 0.58)}" '
                      f'height="{n((sill - fan) * ph)}" rx="{n(0.01 * t)}" fill="none" stroke="{INK}" '
                      f'stroke-width="{n(lw)}" stroke-opacity=".5"/>')
            c.add(f'<circle cx="{n(mid + side * rr * 0.12)}" cy="{n(fan + (sill - fan) * 0.52)}" r="{n(0.014 * t)}" '
                  f'fill="{P.GOLD}" stroke="{INK}" stroke-width=".6"/>')
        c.add(f'<rect x="{n(mid - rr - 0.03 * t)}" y="{n(sill - 0.02 * t)}" width="{n(w + 0.06 * t)}" '
              f'height="{n(0.03 * t)}" fill="{STONE_}" stroke="{INK}" stroke-width="1"/>')     # the step
        return
    c.add(f'<path d="{arch}" fill="{P.CREAM}" stroke="{INK}" stroke-width="1.6"/>')
    inset = 0.035 * t
    ri = rr - inset
    glass = (f"M{n(mid - ri)},{n(sill - inset)} V{n(top + rr)} A{n(ri)},{n(ri)} 0 0 1 {n(mid + ri)},{n(top + rr)} "
             f"V{n(sill - inset)} Z")
    c.add(f'<path d="{glass}" fill="{GLASS}" stroke="{INK}" stroke-width="1"/>')
    c.add(f'<path d="M{n(mid - ri * 0.6)},{n(sill - inset)} L{n(mid - ri * 0.1)},{n(top + rr * 0.6)} '
          f'h{n(ri * 0.25)} L{n(mid - ri * 0.3)},{n(sill - inset)} Z" fill="{P.WHITE}" fill-opacity=".18"/>')
    bars = [f"M{n(mid)},{n(top + inset)} V{n(sill - inset)}"]
    rows = 3
    for q in range(1, rows + 1):
        y = top + rr + (sill - inset - top - rr) * q / (rows + 1)
        bars.append(f"M{n(mid - ri)},{n(y)} H{n(mid + ri)}")
    bars.append(f"M{n(mid - ri)},{n(top + rr)} H{n(mid + ri)}")
    c.line(" ".join(bars), lw * 1.3, P.CREAM)
    c.add(f'<rect x="{n(mid - rr - 0.04 * t)}" y="{n(sill)}" width="{n(w + 0.08 * t)}" height="{n(0.045 * t)}" '
          f'fill="{STONE_}" stroke="{INK}" stroke-width="1.1"/>')                                 # the sill


def gas_lamp(c: Canvas, x: float, y: float, t: float) -> None:
    """A gas lamp on its scrolled iron bracket from the pilaster at x, the lantern at (x + reach, y): the square
    lantern with its glass, cap and finial, the mantle's warm light."""
    k = t / 200
    reach = 26 * k
    c.path(f"M{n(x)},{n(y - 30 * k)} H{n(x + reach)} M{n(x)},{n(y - 14 * k)} Q{n(x + reach * 0.6)},{n(y - 14 * k)} "
           f"{n(x + reach * 0.9)},{n(y - 28 * k)}", "none", max(1.2, 2.4 * k), IRON)
    c.add(f'<circle cx="{n(x + reach * 0.4)}" cy="{n(y - 20 * k)}" r="{n(3 * k)}" fill="none" stroke="{IRON}" '
          f'stroke-width="{n(max(0.8, 1.6 * k))}"/>')
    lx = x + reach
    c.add(f'<circle cx="{n(lx)}" cy="{n(y - 12 * k)}" r="{n(12 * k)}" fill="{P.SUN}" opacity=".22"/>')
    c.shape(f"M{n(lx - 7 * k)},{n(y - 22 * k)} H{n(lx + 7 * k)} L{n(lx + 5 * k)},{n(y - 2 * k)} H{n(lx - 5 * k)} Z",
            P.YELLOW_PALE, sw=max(0.8, 1.4 * k), light=None)
    c.line(f"M{n(lx)},{n(y - 22 * k)} V{n(y - 2 * k)}", max(0.6, 1 * k), IRON)
    c.shape(f"M{n(lx - 9 * k)},{n(y - 22 * k)} L{n(lx)},{n(y - 32 * k)} L{n(lx + 9 * k)},{n(y - 22 * k)} Z", IRON,
            sw=max(0.8, 1.2 * k), light=None)
    c.add(f'<rect x="{n(lx - 5 * k)}" y="{n(y - 2 * k)}" width="{n(10 * k)}" height="{n(3 * k)}" fill="{IRON}"/>')


def canopy_front(c: Canvas, edge: float, t: float, bays: list[float]) -> None:
    """The platform canopy, seen from across the track: its glazed roof sloping up to the wall, carried on a
    cast-iron bracket at every pilaster - a scrolled spandrel with a ring in it - and along its front the fretted
    valance of cream boards, each cut to a point with a hole over it."""
    k = t / 200
    roof_top = edge - 0.42 * t
    val = 0.12 * t
    if edge + 2 < 0:
        return
    c.add(f'<path d="M-6,{n(roof_top)} H{W + 6} V{n(edge - val)} H-6 Z" fill="{mix(GLASS, P.WHITE, 0.35)}"/>')
    c.line(" ".join(f"M{n(q)},{n(roof_top)} V{n(edge - val)}" for q in range(0, W + 6, max(6, int(0.1 * t)))),
           max(0.6, 1.2 * k), IRON, 0.7)
    c.line(f"M-6,{n(roof_top)} H{W + 6}", max(1.0, 2 * k), IRON)
    for bx in bays:                                                    # the brackets
        d = (f"M{n(bx - 0.04 * t)},{n(edge - val)} L{n(bx - 0.04 * t)},{n(edge + 0.36 * t)} "
             f"Q{n(bx - 0.04 * t)},{n(edge + 0.02 * t)} {n(bx - 0.4 * t)},{n(edge - val)} Z")
        c.add(f'<path d="{d}" fill="{IRON}" stroke="{INK}" stroke-width="1.2"/>')
        c.add(f'<circle cx="{n(bx - 0.13 * t)}" cy="{n(edge - 0.01 * t)}" r="{n(0.05 * t)}" fill="{BRICK}" '
              f'stroke="{INK}" stroke-width="1"/>')
        d = (f"M{n(bx + 0.04 * t)},{n(edge - val)} L{n(bx + 0.04 * t)},{n(edge + 0.36 * t)} "
             f"Q{n(bx + 0.04 * t)},{n(edge + 0.02 * t)} {n(bx + 0.4 * t)},{n(edge - val)} Z")
        c.add(f'<path d="{d}" fill="{IRON}" stroke="{INK}" stroke-width="1.2"/>')
        c.add(f'<circle cx="{n(bx + 0.13 * t)}" cy="{n(edge - 0.01 * t)}" r="{n(0.05 * t)}" fill="{BRICK}" '
              f'stroke="{INK}" stroke-width="1"/>')
    c.add(f'<rect x="-6" y="{n(edge - val - 0.03 * t)}" width="{W + 12}" height="{n(0.03 * t)}" fill="{RUBY_DEEP}" '
          f'stroke="{INK}" stroke-width="1"/>')
    bw = 0.055 * t                                                     # the valance boards
    pts = [f"M-6,{n(edge - val)}"]
    x = -6.0
    while x < W + 6:
        pts.append(f"L{n(x)},{n(edge - val * 0.3)} L{n(x + bw / 2)},{n(edge)} L{n(x + bw)},{n(edge - val * 0.3)}")
        x += bw
    pts.append(f"L{n(W + 6)},{n(edge - val)} Z")
    c.add(f'<path d="{" ".join(pts)}" fill="{P.CREAM}" stroke="{INK}" stroke-width="1"/>')
    c.line(" ".join(f"M{n(q * bw - 6)},{n(edge - val)} v{n(val * 0.7)}" for q in range(int((W + 12) / bw) + 1)),
           0.5, INK, 0.4)
    c.add(f'<path d="M{n(bw / 2 - 6)},{n(edge - val * 0.55)} H{W + 6}" stroke="{RUBY_DEEP}" '
          f'stroke-width="{n(bw * 0.28)}" stroke-linecap="round" stroke-dasharray="0 {n(bw)}"/>')   # the holes


# ============================================================================ the rolling stock
def wheel(c: Canvas, x: float, r: float, crank: float, centre: str,
          driving: bool | None = None) -> tuple[float, float]:
    """A wheel standing on the rail (y = 0) at x: the steel tyre, the spokes, the counterweight opposite the crank
    on a driving wheel (`driving`, by default a big one), the hub and the crank pin. Returns where the crank pin
    is."""
    cy = -r
    c.add(f'<circle cx="{n(x)}" cy="{n(cy)}" r="{n(r)}" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="2.2"/>')
    c.add(f'<circle cx="{n(x)}" cy="{n(cy)}" r="{n(r * 0.84)}" fill="{centre}" stroke="{INK}" stroke-width="1.4"/>')
    spokes = 12 if r > 30 else 8
    c.line(" ".join(f"M{n(x + r * 0.2 * math.cos(a))},{n(cy + r * 0.2 * math.sin(a))} "
                    f"L{n(x + r * 0.8 * math.cos(a))},{n(cy + r * 0.8 * math.sin(a))}"
                    for a in (i * 2 * math.pi / spokes for i in range(spokes))), max(1.6, r * 0.07),
           darken(centre, 0.6))
    if r > 30 if driving is None else driving:
        a0, a1 = math.radians(crank + 180 - 42), math.radians(crank + 180 + 42)
        rr = r * 0.82
        c.shape(f"M{n(x + rr * math.cos(a0))},{n(cy + rr * math.sin(a0))} A{n(rr)},{n(rr)} 0 0 1 "
                f"{n(x + rr * math.cos(a1))},{n(cy + rr * math.sin(a1))} Z", darken(centre, 0.85), sw=1.2, light=None)
    c.add(f'<circle cx="{n(x)}" cy="{n(cy)}" r="{n(r * 0.2)}" fill="{P.METAL_DARK}" stroke="{INK}" '
          f'stroke-width="1.4"/>')
    return (x + r * 0.5 * math.cos(math.radians(crank)), cy + r * 0.5 * math.sin(math.radians(crank)))


ENGINE_L, ENGINE_H = 600, 290       # the engine with its tender: from the tender's buffer to the front buffer


def locomotive(c: Canvas, x: float, rail: float, k: float, cab: bool = True, steam: bool = True,
               moving: bool = False, crank: float = 300, seed: int = 0, tender: bool = True, way: int = 1) -> dict:
    """The steam engine with its tender, facing right, its front buffers' faces at (x, rail): the buffer beam and
    its buffers, the headlamp; the smokebox with its round door and handles, the chimney with its copper cap; the
    boiler in ruby with brass bands and its handrail, the steam dome and the sand dome, the safety valves and the
    whistle; the cylinder with its valve chest, the crosshead, the connecting rod and the coupling rod to three
    big driving wheels with their counterweights, a leading wheel; the cab with its window frame, roof and
    handrails - the driver's cap in it, or empty when `cab` is false; the tender behind with its coal and its own
    wheels. Steam as many puffs fading back; motion lines when it runs. Returns its box."""
    d = Canvas()
    body, deep = RUBY, RUBY_DEEP
    if not tender:                                                    # a tank engine: its coal bunker behind the cab
        d.shape(rounded_rect_d(-452, -226, 44, 108, 4), body, sw=2.2, light=(-2, -2))
        d.path(rounded_rect_d(-446, -218, 32, 92, 3), "none", 1.8, P.GOLD)
        d.shape("M-452,-226 Q-446,-246 -430,-248 Q-414,-246 -408,-226 Z", darken(P.CHARCOAL, 0.8), sw=1.6,
                light=None)
        wheel(d, -426, 24, crank, deep)
        d.shape(rounded_rect_d(-468, -108, 16, 10, 2), P.METAL_DARK, sw=1.4, light=None)
        d.shape(rounded_rect_d(-474, -114, 7, 22, 2), P.METAL, sw=1.4, light=None)
    for wx in (-560, -510, -460) if tender else ():
        wheel(d, wx, 24, crank, deep)
    if tender:                                                         # the tender: tank, coal, buffers
        d.shape(rounded_rect_d(-590, -112, 170, 18, 3), P.CHARCOAL, sw=1.8, light=None)
        d.shape(rounded_rect_d(-586, -214, 164, 104, 6), body, sw=2.2, light=(-2, -2))
        d.path(rounded_rect_d(-576, -204, 144, 84, 4), "none", 1.8, P.GOLD)
        d.shape("M-586,-214 Q-560,-238 -504,-240 Q-446,-238 -422,-214 Z", P.CHARCOAL, sw=1.6, light=None)
        for cx_, cy_ in ((-560, -222), (-530, -230), (-498, -228), (-470, -222), (-446, -218)):
            d.shape(ellipse_d(cx_, cy_, 6, 4), darken(P.CHARCOAL, 0.8), sw=0.8, light=None)
        d.shape(rounded_rect_d(-604, -108, 16, 10, 2), P.METAL_DARK, sw=1.4, light=None)        # its buffer
        d.shape(rounded_rect_d(-610, -114, 7, 22, 2), P.METAL, sw=1.4, light=None)
    # the engine's frame and wheels
    d.shape(rounded_rect_d(-410, -112, 396, 22, 3), P.CHARCOAL, sw=2, light=None)
    pins = []
    wheel(d, -66, 24, crank, deep)
    for wx in (-160, -248, -336):
        pins.append(wheel(d, wx, 46, crank, deep))
    # the cylinder, its valve chest, the guides; the crosshead, the rods
    d.shape(rounded_rect_d(-112, -92, 70, 40, 8), body, sw=2.2, light=(-2, -2))
    d.shape(rounded_rect_d(-110, -112, 66, 20, 4), deep, sw=1.8, light=None)
    d.shape(rounded_rect_d(-116, -94, 10, 44, 3), P.GOLD, sw=1.6, light=None)
    d.shape(rounded_rect_d(-48, -94, 10, 44, 3), P.GOLD, sw=1.6, light=None)
    d.line("M-112,-78 H-170 M-112,-66 H-170", 2.4, P.METAL_DARK)
    (p1x, p1y) = pins[0]
    head = -140 + 24 * math.cos(math.radians(crank))
    d.shape(rounded_rect_d(head - 10, -80, 20, 16, 3), P.METAL, sw=1.4, light=None)
    d.line(f"M-112,-72 H{n(head)}", 4, P.METAL_LIGHT)
    d.tube(f"M{n(head)},-72 L{n(p1x)},{n(p1y)}", P.METAL, 7, sw=1.4)
    d.tube(f"M{n(pins[0][0])},{n(pins[0][1])} L{n(pins[2][0])},{n(pins[2][1])}", P.METAL_LIGHT, 7, sw=1.4)
    for px, py in pins:
        d.add(f'<circle cx="{n(px)}" cy="{n(py)}" r="5" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1.2"/>')
    d.shape(rounded_rect_d(-412, -118, 402, 10, 2), P.CHARCOAL, sw=1.8, light=None)             # running board
    # the buffer beam, buffers, coupling hook, headlamp
    d.shape(rounded_rect_d(-18, -132, 18, 44, 3), deep, sw=2, light=None)
    for by in (-112,):
        d.shape(rounded_rect_d(0, by - 4, 18, 12, 2), P.METAL_DARK, sw=1.6, light=None)
        d.shape(rounded_rect_d(16, by - 12, 9, 28, 3), P.METAL, sw=1.6, light=None)
    d.line("M0,-96 h10 q6,0 6,6", 3, P.CHARCOAL)
    for r_, a in ((22, 0.16), (14, 0.26)):
        d.add(f'<circle cx="-2" cy="-146" r="{r_}" fill="{P.SUN}" opacity="{a}"/>')
    d.shape(rounded_rect_d(-22, -158, 18, 24, 3), P.CHARCOAL, sw=1.6, light=None)
    d.shape(rounded_rect_d(-8, -153, 7, 14, 2), P.YELLOW_PALE, sw=1.2, light=None)
    # the boiler with its bands and handrail, the side tank, domes, valves, whistle
    d.shape(rounded_rect_d(-300, -222, 230, 104, 18), body, sw=2.4, light=(-3, -4))
    for bx in (-250, -190, -130):
        d.shape(rounded_rect_d(bx, -222, 6, 104, 2), P.GOLD, sw=1, light=None)
    d.line("M-286,-198 H-86", 2, P.GOLD)
    for hx in (-276, -216, -156, -96):
        d.dot(hx, -198, 2.4, P.METAL_DARK)
    d.shape("M-196,-220 Q-196,-252 -174,-254 Q-152,-252 -152,-220 Z", P.GOLD, sw=2.2, light=(-3, -3))   # steam dome
    d.shape("M-130,-220 Q-130,-240 -116,-242 Q-102,-240 -102,-220 Z", body, sw=2, light=(-2, -2))      # sand dome
    d.shape(rounded_rect_d(-262, -238, 9, 18, 2), P.GOLD, sw=1.4, light=None)
    d.shape(rounded_rect_d(-249, -238, 9, 18, 2), P.GOLD, sw=1.4, light=None)
    d.line("M-232,-222 V-238", 2.2, P.METAL_DARK)
    d.shape("M-238,-238 H-226 L-228,-252 H-236 Z", P.GOLD, sw=1.4, light=None)                # the whistle
    # the smokebox with its round door, the chimney and its cap
    d.shape(rounded_rect_d(-84, -228, 58, 116, 10), P.CHARCOAL, sw=2.4, light=(-3, -3))
    d.shape("M-26,-222 Q-12,-170 -26,-118 Z", darken(P.CHARCOAL, 0.8), sw=1.8, light=None)
    d.dot(-18, -170, 3, P.METAL)
    d.line("M-22,-186 h6 M-22,-154 h6", 2, P.METAL)
    d.shape("M-74,-226 L-70,-262 H-44 L-40,-226 Z", P.CHARCOAL, sw=2.2, light=(-2, 0))
    d.shape(rounded_rect_d(-78, -276, 42, 16, 4), mix(P.ORANGE, P.WOOD, 0.4), sw=2, light=(-2, -2))
    # the cab: its sides with a window frame, the roof on its pillars, the handrails
    d.shape(rounded_rect_d(-410, -268, 112, 150, 4), body, sw=2.4, light=(-2, -2))
    d.shape(rounded_rect_d(-392, -254, 56, 52, 5), darken(deep, 0.5), sw=2, light=None)
    if cab:
        d.add(f'<path d="M-378,-204 Q-376,-226 -364,-226 Q-352,-226 -350,-204 Z" fill="{P.BLUE}" stroke="{INK}" '
              f'stroke-width="1.2"/><circle cx="-364" cy="-232" r="8" fill="{P.WOOD_PALE}" stroke="{INK}" '
              f'stroke-width="1"/><rect x="-376" y="-244" width="24" height="8" rx="3" fill="{P.CHARCOAL}"/>')
    d.path(rounded_rect_d(-392, -254, 56, 52, 5), "none", 2.4, P.GOLD)                          # window frame
    d.shape(rounded_rect_d(-322, -250, 18, 18, 9), P.LENS, sw=1.6, light=None)                 # spectacle glass
    d.path(rounded_rect_d(-398, -188, 92, 60, 3), "none", 2, P.GOLD)
    d.line("M-414,-250 V-130 M-300,-250 V-130", 3, P.METAL_LIGHT)                              # handrails
    d.shape("M-420,-280 Q-354,-300 -290,-280 V-268 H-420 Z", P.CHARCOAL, sw=2.4, light=(0, -2))  # the roof
    d.shape(rounded_rect_d(-404, -110, 30, 6, 2), P.CHARCOAL, sw=1.4, light=None)               # the step
    if steam == "low":                                                 # at speed: the plume streams back low
        puffs(d, -56, -282, 46, -470, 9, 30, 16, seed)
    elif steam:
        puffs(d, -56, -284, 150, -260 if moving else -60, 10, 34, 12, seed)
    if moving:
        d.line(" ".join(f"M{-620 - q * 8},{-60 - q * 40} h{-40 + q * 6}" for q in range(4)), 2.4, INK, 0.5)
    c.add(_at(d, x, rail, k, mirror=way < 0))
    back = ((680 if moving else 612) if tender else 476) * k
    top = rail - (346 if steam == "low" else 440 if steam else 284) * k
    lo_, hi_ = sorted((x - way * back, x + way * 26 * k))
    mid = (pins[0][0] + pins[2][0]) / 2, (pins[0][1] + pins[2][1]) / 2
    return {"box": (lo_, top, hi_, rail), "buffer": (x + way * 25 * k, rail - 112 * k),
            "wheel": (x - way * 248 * k, rail - 46 * k), "rod": (x + way * mid[0] * k, rail + mid[1] * k),
            "cab": (x - way * 364 * k, rail - 228 * k)}


COACH_L = 330
VEHICLES = ("handcar", "engine", "wagon", "stock", "train", "buffer", "bogie")   # what runs on the rails, by name


def coach(c: Canvas, x: float, rail: float, k: float, way: int = 1) -> dict:
    """A passenger coach, its right buffer face at (x, rail), 330 long and 270 tall: buffers at each end, the
    underframe, two bogies of two wheels with their frames and springs, the ruby body with its cream window band
    and windows, two doors with their handles and droplights, the gold lining, the curved roof with its
    ventilators; on a bogie, at each wheel, the axlebox on its springs. Facing `way`, its leading buffer at x.
    Returns its box, its wheels' middles, the hubs' height and the wheels' radius, the buffer's face."""
    d = Canvas()
    for ex in (-COACH_L + 6, -6):
        d.shape(rounded_rect_d(ex - 6, -116, 12, 12, 2), P.METAL_DARK, sw=1.4, light=None)
    d.shape(rounded_rect_d(-COACH_L, -122, 7, 24, 3), P.METAL, sw=1.4, light=None)
    d.shape(rounded_rect_d(-7, -122, 7, 24, 3), P.METAL, sw=1.4, light=None)
    d.shape(rounded_rect_d(-COACH_L + 10, -132, COACH_L - 20, 18, 3), P.CHARCOAL, sw=1.8, light=None)
    mid_ = -COACH_L / 2                                                # the truss rods and battery box between
    d.path(f"M{-COACH_L + 130},-116 L{mid_ - 30},-98 H{mid_ + 30} L-130,-116", "none", 2.4, P.METAL_DARK)
    for qx in (mid_ - 30, mid_ + 30):
        d.line(f"M{qx},-116 V-98", 2.4, P.METAL_DARK)
    d.shape(rounded_rect_d(mid_ - 22, -114, 44, 14, 2), P.CHARCOAL, sw=1.4, light=None)
    for bx in BOGIES:                                                  # the two bogies under the floor
        bogie_side(d, bx, -114)
    d.shape(rounded_rect_d(-COACH_L + 10, -270, COACH_L - 20, 140, 8), RUBY, sw=2.4, light=(-3, -3))
    d.shape(rounded_rect_d(-COACH_L + 10, -250, COACH_L - 20, 54, 2), P.CREAM, sw=1.8, light=None)
    for wx in range(-COACH_L + 24, -40, 50):
        if abs(wx + COACH_L / 2) < 30:
            continue
        d.shape(rounded_rect_d(wx, -244, 40, 42, 6), P.YELLOW_PALE, sw=1.6, light=None)
    for dx in (-COACH_L + 30, -60):                                                            # its doors
        d.shape(rounded_rect_d(dx, -248, 30, 116, 3), RUBY, sw=1.6, light=None)
        d.shape(rounded_rect_d(dx + 5, -242, 20, 28, 3), P.YELLOW_PALE, sw=1.2, light=None)
        d.dot(dx + 25, -180, 2.4, P.GOLD)
    d.path(rounded_rect_d(-COACH_L + 10, -186, COACH_L - 20, 40, 2), "none", 1.6, P.GOLD)
    d.shape(f"M{-COACH_L + 6},-268 Q{-COACH_L / 2},-298 -6,-268 V-262 H{-COACH_L + 6} Z", P.METAL_DARK, sw=2.2,
            light=(0, -2))
    for vx in range(-COACH_L + 50, -20, 70):
        d.shape(rounded_rect_d(vx, -292, 14, 8, 3), P.METAL, sw=1, light=None)
    if way < 0:
        c.add(_at(d, x, rail, k, mirror=True))
    else:
        c.add(_at(d, x, rail, k))
    wheels = [x + way * wx * k for bx in BOGIES for wx in (bx - WHEELBASE / 2, bx + WHEELBASE / 2)]
    lo_, hi_ = sorted((x, x - way * (COACH_L + 2) * k))
    return {"box": (lo_ - (2 * k if way < 0 else 0), rail - 298 * k, hi_ + (2 * k if way > 0 else 0), rail),
            "wheels": wheels, "hub": rail - BOGIE_R * k, "r": BOGIE_R * k,
            "buffer": (x + way * 0.5 * k, rail - 110 * k)}


BOGIE_R = 34                     # a bogie's wheel radius, its wheelbase and where the coach's two bogies stand
WHEELBASE = 80
BOGIES = (-COACH_L + 78, -78)


def bogie_side(d: Canvas, bx: float, floor: float, far: bool = False) -> None:
    """A two-axle bogie seen from the side, its middle at bx on the rail (y = 0): the two spoked wheels on the rail,
    the far pair darker behind them (`far`); the side frame across both axles over the wheels' middles, its ends
    turned down, a pair of horn guides at each axle and the axlebox between them, its round end cover on the axle's
    centre; the coil spring between each axlebox and the frame; in the middle the bolster on its springs and, on
    top, the centre pivot up to the coach floor at `floor`."""
    r, half = BOGIE_R, WHEELBASE / 2
    hub = -r
    if far:
        for wx in (bx - half, bx + half):
            d.add(f'<circle cx="{wx + 6}" cy="{hub - 2}" r="{r}" fill="{darken(P.CHARCOAL, 0.8)}" stroke="{INK}" '
                  f'stroke-width="1.2"/>')
    for wx in (bx - half, bx + half):
        wheel(d, wx, r, 0, RUBY_DEEP, driving=False)
    top, low_ = hub - 32, hub - 20                                     # the side frame's top and bottom edges
    d.shape(f"M{bx - half - 24},{low_ + 6} L{bx - half - 20},{top} H{bx + half + 20} L{bx + half + 24},{low_ + 6} "
            f"H{bx + half + 13} V{low_} H{bx + 13} Q{bx},{low_ + 8} {bx - 13},{low_} H{bx - half - 13} V{low_ + 6} Z",
            P.CHARCOAL, sw=1.6, light=None)                            # the side frame, a belly at the bolster
    d.line(" ".join(f"M{n(q)},{top + 3} v3" for q in range(int(bx - half - 14), int(bx + half + 16), 12)), 1,
           P.METAL_DARK)                                               # its rivets
    for wx in (bx - half, bx + half):
        d.line(f"M{wx - 13},{low_} V{hub + 14} M{wx + 13},{low_} V{hub + 14}", 3.2, P.CHARCOAL)   # horn guides
        d.path(f"M{wx - 6},{low_} l12,3 l-12,3 l12,3 l-12,3", "none", 1.8, P.METAL)                # coil spring
        d.shape(rounded_rect_d(wx - 10, low_ + 11, 20, 22, 2.5), P.METAL_DARK, sw=1.4, light=None)  # axlebox
        d.add(f'<circle cx="{wx}" cy="{hub}" r="5.5" fill="{P.METAL}" stroke="{INK}" stroke-width="1.2"/>')
        d.add(f'<circle cx="{wx}" cy="{hub}" r="1.8" fill="{P.METAL_DARK}"/>')                    # axle's end
    lift = max(10.0, min(18.0, top - floor - 30))                     # the bolster springs' height
    beam_top = max(floor + 8, top - lift - 14)
    for sx in (bx - 14, bx + 14):                                      # the bolster on its two coil springs
        d.path(f"M{sx - 5},{top} " + " ".join(f"l10,{-lift / 6:.1f} l-10,{-lift / 6:.1f}" for _ in range(3)),
               "none", 1.8, P.METAL)
    d.shape(rounded_rect_d(bx - 26, beam_top, 52, top - lift - beam_top, 2), P.CHARCOAL, sw=1.4, light=None)
    if beam_top > floor + 0.5:
        d.shape(f"M{bx - 11},{beam_top} L{bx - 8},{floor} H{bx + 8} L{bx + 11},{beam_top} Z", P.METAL_DARK, sw=1.4,
                light=None)                                             # the centre pivot under the floor


def train(c: Canvas, x: float, rail: float, k: float, cab: bool = True, moving: bool = False, cars: int = 2,
          seed: int = 0, steam: bool = True, way: int = 1, tender: bool = True) -> dict:
    """The engine facing `way`, its front buffers at x, and `cars` coaches behind it, buffers to buffers. Returns
    its box and the engine's."""
    lo = locomotive(c, x, rail, k, cab=cab, steam=steam, moving=moving, seed=seed, way=way, tender=tender)
    back = x - way * ((ENGINE_L if tender else 476) + 14) * k
    left, right = lo["box"][0], lo["box"][2]
    for _ in range(cars):
        lo_, hi_ = min(back, back - way * COACH_L * k), max(back, back - way * COACH_L * k)
        if (hi_ < -10) if way > 0 else (lo_ > W + 10):
            break                                                      # behind the frame's side: none follow
        if not ((lo_ > W + 10) if way > 0 else (hi_ < -10)):          # one gone ahead past the side is not drawn
            cb = coach(c, back, rail, k, way=way)
            left, right = min(left, cb["box"][0]), max(right, cb["box"][2])
        back -= way * (COACH_L + 4) * k
    return {"box": (left, lo["box"][1], right, rail), "engine": lo}


def tail_lamp(c: Canvas, end: float, rail: float, k: float, way: int) -> None:
    """The red tail lamp on the end of the last coach, whose body ends at x = `end` and which faces `way`: the lamp
    iron bolted to the end panel and standing out from it, the lamp case hung on it by its handle, the red lens
    looking back along the line."""
    out = -way                                                         # away from the coach, back along the line
    y = rail - 156 * k                                                 # low on the end panel, over the buffers
    c.add(f'<path d="M{n(end)},{n(y + 18 * k)} h{n(out * 5 * k)} V{n(y - 4 * k)} h{n(out * 6 * k)}" fill="none" '
          f'stroke="{INK}" stroke-width="{n(2.4 * k + 1.6)}" stroke-linejoin="round"/>'
          f'<path d="M{n(end)},{n(y + 18 * k)} h{n(out * 5 * k)} V{n(y - 4 * k)} h{n(out * 6 * k)}" fill="none" '
          f'stroke="{P.METAL_DARK}" stroke-width="{n(2.4 * k)}" stroke-linejoin="round"/>')    # the lamp iron
    c.add(f'<rect x="{n(end - 2 * k)}" y="{n(y + 15 * k)}" width="{n(4 * k)}" height="{n(6 * k)}" '
          f'fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1"/>')                          # its foot plate
    cx = end + out * 12 * k
    c.add(f'<path d="M{n(cx - 4 * k)},{n(y + 2 * k)} Q{n(cx)},{n(y - 7 * k)} {n(cx + 4 * k)},{n(y + 2 * k)}" '
          f'fill="none" stroke="{INK}" stroke-width="{n(1.6 * k + 0.6)}"/>')                  # the handle
    c.add(f'<rect x="{n(cx - 7 * k)}" y="{n(y + 2 * k)}" width="{n(14 * k)}" height="{n(17 * k)}" rx="{n(2.5 * k)}" '
          f'fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="1.2"/>'
          f'<path d="M{n(cx - 5 * k)},{n(y + 2 * k)} l{n(5 * k)},{n(-4 * k)} l{n(5 * k)},{n(4 * k)} Z" '
          f'fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="1"/>'
          f'<circle cx="{n(cx + out * 4 * k)}" cy="{n(y + 11 * k)}" r="{n(4.6 * k)}" fill="{P.RED}" stroke="{INK}" '
          f'stroke-width="1"/><circle cx="{n(cx + out * 5 * k)}" cy="{n(y + 9.6 * k)}" r="{n(1.4 * k)}" '
          f'fill="{lighten(P.RED, 0.5)}"/>')


def buffer_stop(c: Canvas, x: float, rail: float, k: float, way: int = 1) -> dict:
    """The buffer stop at the end of the track at (x, rail), facing left: built of old rails - two raking struts
    and an upright, bolted to the running rails with their fishplates - carrying at buffer height a heavy timber
    beam painted in red and white chevrons, two sprung buffers on it facing the line, and the red lamp on its
    bracket on top. Returns its box and the buffers' faces."""
    d = Canvas()
    d.shape("M-6,0 L-2,-104 H8 L4,0 Z", P.METAL_DARK, sw=1.4, light=None)                      # the upright
    d.shape("M4,-96 L56,0 H44 L-2,-90 Z", P.METAL_DARK, sw=1.4, light=None)                    # the raking strut
    d.shape("M4,-60 L36,0 H28 L0,-52 Z", P.METAL_DARK, sw=1.2, light=None)
    d.shape(rounded_rect_d(-10, -4, 72, 5, 1), P.METAL, sw=1.2, light=None)                    # on the rail
    for bx in (-4, 20, 48):
        d.add(f'<circle cx="{bx}" cy="-1.5" r="1.4" fill="{P.METAL_PALE}"/>')
    d.shape(rounded_rect_d(-8, -128, 30, 40, 2), P.WHITE, sw=1.8, light=None)                   # the beam
    clip = d.shape(rounded_rect_d(-8, -128, 30, 40, 2), P.WHITE, sw=0, light=None, clip=True)
    d.add(f'<g clip-path="url(#{clip})">' + "".join(f'<path d="M-8,{-130 + q * 14} l30,-10 v7 l-30,10 Z" '
                                                     f'fill="{P.RED}"/>' for q in range(5)) + "</g>")
    d.path(rounded_rect_d(-8, -128, 30, 40, 2), "none", 1.8)
    for by in (-120, -100):                                                                     # its buffers
        d.shape(rounded_rect_d(-20, by, 12, 10, 2), P.METAL_DARK, sw=1.2, light=None)
        d.shape(rounded_rect_d(-27, by - 6, 7, 22, 3), P.METAL, sw=1.4, light=None)
    d.line("M7,-128 V-140 H18", 2.4, P.METAL_DARK)                                              # the lamp
    d.shape(rounded_rect_d(14, -152, 14, 16, 3), P.CHARCOAL, sw=1.2, light=None)
    d.add(f'<circle cx="21" cy="-144" r="4.4" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>')
    c.add(at(d, x, rail, k, way))
    lo_, hi_ = sorted((x - way * 28 * k, x + way * 63 * k))
    return {"box": (lo_, rail - 153 * k, hi_, rail), "face": x - way * 27 * k, "lamp": (x + way * 21 * k,
                                                                                       rail - 144 * k)}


BOARD_ROWS_TEXT = (("16:04", "1"), ("16:20", "2"), ("16:45", "3"))   # departure time, platform


def flap_board(s: Strip, left: float, top: float, k: float) -> tuple[float, float]:
    """The departures board's face as a container, its top-left corner at (left, top) in page space: the black
    board, and inside its margin three rows of split flaps - each departure's time in yellow and its platform
    number in white, a flap per figure, its hinge across the middle. Returns the page point of the top row's
    middle."""
    pen = Pen(s, left, top, k)
    hold = pen.container("flaps", 0, 0, 128, 56, P.CHARCOAL, radius=4, sw=1.8, light=None)
    pad = pen.pad(128, 56)
    gap = max(3.0, 3.4 / k)                                            # rows apart even on a small board
    fh = (56 - 2 * pad - 2 * gap) / 3
    cells = 7                                                          # five for the time, a gap, the platform
    fw = (128 - 2 * pad - (cells - 1) * 1.6) / cells
    size = fh * 0.82
    for row, (time_, plat) in enumerate(BOARD_ROWS_TEXT):
        y = pad + row * (fh + gap)
        chars = [*time_, "", plat]
        for q, ch in enumerate(chars):
            if not ch:
                continue
            fx_ = pad + q * (fw + 1.6)
            col = P.YELLOW if q < 5 else P.WHITE
            pen.c.shape(rounded_rect_d(fx_, y, fw, fh, 0.8), mix(P.CHARCOAL, P.WHITE, 0.12), sw=0.4, light=None)
            pen.c.add(lettering(fx_ + fw / 2, y + fh * 0.84, ch, size, col, style="plain"))
            pen.c.line(f"M{n(fx_)},{n(y + fh / 2)} h{n(fw)}", 0.5, INK, 0.7)          # the flap's hinge
        pen.child(hold, f"row{row}", pad, y, 128 - pad, y + fh)
    s.put(lane(s).feet - 0.5, pen.svg(), None)
    return pen.at(64, pad + fh / 2)




# ============================================================================ the things the cast works with
def handcar(c: Canvas, x: float, rail: float, k: float, way: int = 1) -> dict:
    """A pump handcar on the rails at (x, rail), 150 long: four spoked wheels with their axleboxes - the near pair
    and, a little higher and darker behind them, the far pair - the steel frame and the plank deck, the A-frame
    in ruby iron up to the beam's pivot, under the deck the big gear and the pinion on the axle with the crank
    rod up to the beam, the brake lever at the back. The walking beam is drawn by `beam`. Returns its box, the
    deck's height, the pivot and where the crank rod meets the beam."""
    d = Canvas()
    for wx in (-50, 50):                                                                       # the far pair
        d.add(f'<circle cx="{wx + 6}" cy="-17" r="14" fill="{darken(P.CHARCOAL, 0.8)}" stroke="{INK}" '
              f'stroke-width="1.2"/>')
    d.shape("M8,-44 L20,-20", P.METAL_DARK, sw=0, light=None)
    d.add(f'<circle cx="22" cy="-20" r="13" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1.4"/>')
    d.add("".join(f'<rect x="20.5" y="-35.5" width="3" height="4" fill="{P.METAL_DARK}" stroke="{INK}" '
                  f'stroke-width=".6" transform="rotate({q * 30} 22 -20)"/>' for q in range(12)))  # the big gear
    d.add(f'<circle cx="22" cy="-20" r="4" fill="{P.METAL}" stroke="{INK}" stroke-width="1"/>')
    for wx in (-50, 50):                                                                       # the near pair
        wheel(d, wx, 15, 0, RUBY_DEEP)
        d.shape(rounded_rect_d(wx - 6, -21, 12, 12, 2), P.METAL_DARK, sw=1.2, light=None)      # its axlebox
    d.add(f'<circle cx="50" cy="-15" r="6" fill="{P.METAL}" stroke="{INK}" stroke-width="1"/>')  # the pinion
    d.shape(rounded_rect_d(-70, -34, 140, 9, 2), P.CHARCOAL, sw=1.6, light=None)               # the frame
    d.shape(rounded_rect_d(-74, -45, 148, 11, 2), P.WOOD, sw=1.6, light=(-1, -1))              # the deck
    d.line(" ".join(f"M{q},-45 V-34" for q in range(-56, 74, 18)), 0.8, P.WOOD_DARK)
    d.shape("M-24,-45 L-5,-104 H5 L24,-45 H16 L2,-92 H-2 L-16,-45 Z", RUBY, sw=1.6, light=(-1, -1))   # A-frame
    d.line("M-13,-72 H13", 3, RUBY_DEEP)
    d.line("M14,-104 L28,-26", 3, P.METAL_DARK)                                                # the crank rod
    d.add(f'<circle cx="28" cy="-26" r="2.6" fill="{P.METAL_PALE}" stroke="{INK}" stroke-width=".8"/>')
    d.line("M-70,-45 L-86,-84", 3, P.METAL_DARK)                                               # the brake lever
    d.shape(rounded_rect_d(-92, -92, 12, 9, 3), P.CHARCOAL, sw=1, light=None)
    d.add(f'<circle cx="0" cy="-104" r="6" fill="{P.METAL}" stroke="{INK}" stroke-width="1.4"/>')
    c.add(at(d, x, rail, k, way))
    lo_, hi_ = sorted((x - way * 93 * k, x + way * 75 * k))
    return {"box": (lo_, rail - 110 * k, hi_, rail), "deck": rail - 45 * k, "pivot": (x, rail - 104 * k),
            "wheels": [x - way * 50 * k, x + way * 50 * k]}


def beam(c: Canvas, pivot: tuple[float, float], end: tuple[float, float], k: float) -> None:
    """The handcar's walking beam rocking on its pivot, one handle at `end`, the other as far out opposite: a ruby
    iron bar, the boss at the pivot, a turned wooden handle across each end."""
    px, py = pivot
    ex, ey = end
    ox, oy = 2 * px - ex, 2 * py - ey
    c.add(f'<path d="M{n(ox)},{n(oy)} L{n(ex)},{n(ey)}" stroke="{INK}" stroke-width="{n(9 * k + 2.4)}" '
          f'stroke-linecap="round"/><path d="M{n(ox)},{n(oy)} L{n(ex)},{n(ey)}" stroke="{RUBY}" '
          f'stroke-width="{n(9 * k)}" stroke-linecap="round"/>')
    c.add(f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(7 * k)}" fill="{P.METAL}" stroke="{INK}" stroke-width="1.4"/>')
    for hx, hy in ((ex, ey), (ox, oy)):
        c.add(f'<circle cx="{n(hx)}" cy="{n(hy)}" r="{n(6 * k)}" fill="{P.WOOD}" stroke="{INK}" stroke-width="1.4"/>'
              f'<circle cx="{n(hx)}" cy="{n(hy)}" r="{n(2.4 * k)}" fill="{P.WOOD_DARK}"/>')


def dust(c: Canvas, x: float, rail: float, k: float, way: int, seed: int) -> None:
    """The dust a running wheel kicks up off the ballast: small puffs at the rail, wider and paler behind."""
    puffs(c, x, rail - 4 * k, 18 * k, -way * 70 * k, 3 * k, 10 * k, 9, seed, color=DUST)


def wagon(c: Canvas, x: float, rail: float, k: float, way: int = 1) -> dict:
    """A short open wagon with low drop sides, its middle at (x, rail), 244 long over the buffers: two spoked
    wheels in their axleguards, the axleboxes and the leaf springs over them, the ruby solebar, the headstock at
    each end with two sprung buffers and the coupling hook, the plank sides with their hinges and door bangs.
    Returns its box, its two ends' buffer faces and hooks, the wheels and the axleboxes."""
    d = Canvas()
    for wx in (-62, 62):
        d.shape(f"M{wx - 20},-46 L{wx - 13},-14 H{wx + 13} L{wx + 20},-46 Z", "none", sw=0, light=None)
        wheel(d, wx, 20, 0, RUBY_DEEP)
        d.path(f"M{wx - 22},-48 L{wx - 14},-14 M{wx + 22},-48 L{wx + 14},-14", "none", 3.4, P.CHARCOAL)
        d.shape(rounded_rect_d(wx - 9, -29, 18, 18, 2), P.METAL_DARK, sw=1.4, light=None)      # the axlebox
        d.line(f"M{wx - 7},-22 h14", 1, P.METAL_PALE)
        for q in range(3):                                                                   # the leaf spring
            d.path(f"M{wx - 24 + q * 3},{-42 + q * 2.4} Q{wx},{-34 + q * 2.4} {wx + 24 - q * 3},{-42 + q * 2.4}",
                   "none", 2, P.METAL)
        d.line(f"M{wx},-35 V-29", 3, P.METAL_DARK)
    d.shape(rounded_rect_d(-112, -62, 224, 16, 2), RUBY_DEEP, sw=1.8, light=None)              # the solebar
    d.line(" ".join(f"M{q},-60 v12" for q in range(-100, 104, 20)), 0.8, INK, 0.4)
    for ex in (-1, 1):                                                                       # headstocks, buffers
        d.shape(rounded_rect_d(ex * 112 - (6 if ex > 0 else 0) - (0 if ex > 0 else 0), -70, 6, 30, 1), P.CHARCOAL,
                sw=1.4, light=None)
        d.shape(rounded_rect_d(ex * 118 - 6, -64, 12, 10, 1.5), P.METAL_DARK, sw=1.2, light=None)
        d.shape(rounded_rect_d(ex * 124 - 3, -70, 6, 22, 2.5), P.METAL, sw=1.4, light=None)
        d.path(f"M{ex * 112},-52 h{ex * 8} q{ex * 4},0 {ex * 4},4 q0,4 {-ex * 4},4", "none", 2.4, P.CHARCOAL)
    d.shape(rounded_rect_d(-112, -96, 224, 34, 2), mix(P.WOOD, RUBY, 0.25), sw=1.8, light=(-1, -1))   # the sides
    d.line(" ".join(f"M-112,{y} H112" for y in (-85, -74)), 0.8, P.WOOD_DARK)
    d.line(" ".join(f"M{q},-96 V-62" for q in (-60, 0, 60)), 3, P.CHARCOAL)                   # the strapping
    for hx in (-36, 36):
        d.add(f'<circle cx="{hx}" cy="-66" r="2.4" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width=".8"/>')
    c.add(at(d, x, rail, k, way))
    ends = [(x + e * 127 * k, rail - 59 * k) for e in (-1, 1)]
    hooks = [(x + e * 124 * k, rail - 48 * k) for e in (-1, 1)]
    return {"box": (x - 128 * k, rail - 97 * k, x + 128 * k, rail), "ends": ends, "hooks": hooks,
            "wheels": [x - 62 * k, x + 62 * k], "hub": rail - 20 * k, "r": 20 * k, "axlebox": rail - 20 * k}


def crates(c: Canvas, x: float, deck: float, k: float, seed: int) -> None:
    """A wagon's load on its deck at (x, deck): two wooden crates with their battens and a stack of sacks beside,
    a rope over them."""
    rnd = random.Random(seed)
    xs = (-80, -30) if seed % 2 == 0 else (-20, 30)
    for q, cx in enumerate(xs):
        h = 40 + 8 * q
        c.add(f'<rect x="{n(x + cx * k)}" y="{n(deck - h * k)}" width="{n(44 * k)}" height="{n(h * k)}" '
              f'fill="{mix(P.WOOD, P.WOOD_PALE, 0.3)}" stroke="{INK}" stroke-width="1.4"/>')
        c.line(f"M{n(x + cx * k)},{n(deck - h * k / 2)} h{n(44 * k)} M{n(x + (cx + 6) * k)},{n(deck - h * k)} "
               f"v{n(h * k)} M{n(x + (cx + 38) * k)},{n(deck - h * k)} v{n(h * k)}", max(0.8, 1.2 * k), P.WOOD_DARK)
    sx = x + (40 if seed % 2 == 0 else -80) * k
    for q in range(3):                                                 # the sacks
        r = rnd.uniform(15, 18)
        c.add(f'<ellipse cx="{n(sx + q * 26 * k)}" cy="{n(deck - r * 0.7 * k)}" rx="{n(r * k)}" ry="{n(r * 0.7 * k)}" '
              f'fill="{mix(P.BEIGE, P.WOOD_PALE, 0.5)}" stroke="{INK}" stroke-width="1.2"/>')


def screw_coupling(c: Canvas, a: tuple[float, float], b: tuple[float, float], handle: tuple[float, float],
                   k: float) -> None:
    """The screw coupling between two hooks: a link off each hook to the trunnions, the screw between them with
    its barrel, and the tommy bar off the barrel with its ball weight - out to `handle`, where a hand turns it."""
    (ax, ay), (bx, by) = a, b
    mx, my = (ax + bx) / 2, max(ay, by) + 4 * k
    for (hx, hy), side in ((a, -1), (b, 1)):
        c.add(f'<path d="M{n(hx)},{n(hy)} L{n(mx + side * 9 * k)},{n(my)}" stroke="{INK}" '
              f'stroke-width="{n(4.4 * k + 2)}" stroke-linecap="round"/><path d="M{n(hx)},{n(hy)} '
              f'L{n(mx + side * 9 * k)},{n(my)}" stroke="{P.METAL}" stroke-width="{n(4.4 * k)}" '
              f'stroke-linecap="round"/>')
    c.add(f'<rect x="{n(mx - 10 * k)}" y="{n(my - 3 * k)}" width="{n(20 * k)}" height="{n(6 * k)}" rx="{n(2 * k)}" '
          f'fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1.2"/>')
    c.line(" ".join(f"M{n(mx + q * 3 * k)},{n(my - 3 * k)} v{n(6 * k)}" for q in range(-2, 3)), 0.7, P.METAL_PALE)
    hx, hy = handle
    c.add(f'<path d="M{n(mx)},{n(my)} L{n(hx)},{n(hy)}" stroke="{INK}" stroke-width="{n(3 * k + 2)}" '
          f'stroke-linecap="round"/><path d="M{n(mx)},{n(my)} L{n(hx)},{n(hy)}" stroke="{P.METAL_LIGHT}" '
          f'stroke-width="{n(3 * k)}" stroke-linecap="round"/>')
    ang = math.atan2(hy - my, hx - mx)
    bx_, by_ = hx + math.cos(ang) * 4 * k, hy + math.sin(ang) * 4 * k
    c.add(f'<circle cx="{n(bx_)}" cy="{n(by_)}" r="{n(4 * k)}" fill="{P.METAL_DARK}" stroke="{INK}" '
          f'stroke-width="1.2"/>')


def model_layout(c: Canvas, x: float, foot: float, k: float, seed: int = 0, way: int = 1) -> dict:
    """The caterpillar's model railway on its table at (x, foot), 260 wide, its top at waist height (100): the
    trestle legs and the apron, the baseboard with its green fascia; on its grass the oval of track on tiny
    sleepers, the green hill with a stone tunnel mouth the track runs into, the little station with its platform
    and ruby roof, a signal, round trees and a cone of fir; on the front straight the tiny steam train with two
    coaches and a puff over its chimney; on the fascia the terminal the controller's cable plugs into. Returns its
    box and the terminal."""
    d = Canvas()
    for lx in (-112, 112):                                                                     # the far legs
        d.line(f"M{lx + 8},-100 V-4", 5, darken(P.WOOD_DARK, 0.85))
    for lx in (-116, 116):
        d.shape(rounded_rect_d(lx - 4, -100, 8, 100, 2), P.WOOD_DARK, sw=1.4, light=None)
    d.shape(rounded_rect_d(-122, -92, 244, 10, 2), P.WOOD, sw=1.4, light=None)                # the apron
    d.line("M-110,-60 H110", 3.4, P.WOOD_DARK)                                                 # the stretcher
    d.shape("M-132,-112 L-122,-142 H122 L132,-112 Z", mix(P.GREEN, P.LEAF_DARK, 0.15), sw=1.6, light=None)
    rnd = random.Random(seed)
    for _ in range(26):                                                                        # tufts of grass
        gx, gy = rnd.uniform(-118, 118), rnd.uniform(-138, -114)
        d.line(f"M{n(gx)},{n(gy)} l1,-3 M{n(gx + 2)},{n(gy)} l-1,-3", 0.8, P.LEAF_DARK)
    d.shape(rounded_rect_d(-134, -114, 268, 16, 2), mix(P.GREEN, P.LEAF_DARK, 0.45), sw=1.8, light=None)  # fascia
    d.add(f'<ellipse cx="0" cy="-126" rx="104" ry="11" fill="none" stroke="{P.WOOD_DARK}" stroke-width="5"/>'
          f'<ellipse cx="0" cy="-126" rx="104" ry="11" fill="none" stroke="{P.METAL_LIGHT}" stroke-width="1.6"/>'
          f'<ellipse cx="0" cy="-126" rx="104" ry="11" fill="none" stroke="{P.METAL_DARK}" stroke-width="1" '
          f'stroke-dasharray="1.4 3"/>')                                                       # the oval of track
    d.shape("M-128,-117 Q-118,-176 -78,-178 Q-46,-176 -36,-130 L-36,-117 Z", mix(P.GREEN, P.LEAF, 0.4), sw=1.6,
            light=(-2, -2))                                                                    # the hill
    d.shape("M-74,-116 V-130 Q-66,-140 -58,-130 V-116 Z", P.STONE, sw=1.4, light=None)          # the tunnel mouth
    d.shape("M-71,-116 V-129 Q-66,-136 -61,-129 V-116 Z", P.CHARCOAL, sw=0, light=None)
    for tx, ty, r in ((-104, -168, 7), (-92, -176, 6)):
        d.add(f'<circle cx="{tx}" cy="{ty}" r="{r}" fill="{P.LEAF_DARK}" stroke="{INK}" stroke-width="1"/>')
    d.shape(rounded_rect_d(34, -146, 52, 6, 1), P.STONE, sw=1, light=None)                     # its platform
    d.shape(rounded_rect_d(42, -164, 36, 18, 1), mix(P.TERRACOTTA, P.CARD, 0.3), sw=1.2, light=None)
    d.shape("M38,-164 L60,-176 L82,-164 Z", RUBY, sw=1.2, light=None)
    for wx in (48, 62):
        d.shape(rounded_rect_d(wx, -160, 8, 9, 3), GLASS, sw=0.8, light=None)
    for tx, ty in ((100, -148), (114, -144), (-16, -150)):
        d.line(f"M{tx},{ty} v8", 2, P.WOOD_DARK)
        d.add(f'<circle cx="{tx}" cy="{ty - 4}" r="7" fill="{P.LEAF}" stroke="{INK}" stroke-width="1"/>')
    d.shape("M2,-142 L8,-160 L14,-142 Z", P.LEAF_DARK, sw=1, light=None)                       # a fir
    d.line("M24,-138 V-158", 1.4, P.METAL_DARK)                                                # the signal
    d.shape(rounded_rect_d(24, -158, 9, 2.6, 0.6), RUBY, sw=0.6, light=None)
    # the little train on the front straight: engine and two coaches
    for q in range(2):
        cx = -46 + q * 26
        d.shape(rounded_rect_d(cx, -128, 22, 11, 2), RUBY, sw=1, light=None)
        d.shape(rounded_rect_d(cx + 2, -126, 18, 4, 1), P.CREAM, sw=0.4, light=None)
        d.add(f'<circle cx="{cx + 5}" cy="-116" r="2.4" fill="{INK}"/><circle cx="{cx + 17}" cy="-116" r="2.4" '
              f'fill="{INK}"/>')
    d.shape(rounded_rect_d(8, -128, 28, 12, 3), RUBY_DEEP, sw=1, light=None)                   # the engine
    d.shape(rounded_rect_d(8, -136, 10, 9, 1), RUBY_DEEP, sw=1, light=None)
    d.shape(rounded_rect_d(29, -136, 4, 8, 1), P.CHARCOAL, sw=0.8, light=None)
    for wx in (13, 22, 31):
        d.add(f'<circle cx="{wx}" cy="-116" r="3" fill="{INK}"/>')
    puffs(d, 31, -142, 12, -18, 2.2, 5, 5, seed + 3)
    d.shape(rounded_rect_d(21, -110, 18, 10, 2), P.CHARCOAL, sw=1.2, light=None)              # the terminal
    d.add(f'<circle cx="26" cy="-105" r="1.6" fill="{P.RED}"/><circle cx="34" cy="-105" r="1.6" '
          f'fill="{P.METAL_LIGHT}"/>')
    c.add(at(d, x, foot, k, way))
    return {"box": (x - 134 * k, foot - 179 * k, x + 134 * k, foot), "top": foot - 112 * k,
            "terminal": (x + way * 30 * k, foot - 100 * k), "signal": (x + way * 28 * k, foot - 156 * k)}


def driving_wheels(c: Canvas, x: float, rail: float, k: float, way: int = 1) -> dict:
    """The engine's driving gear run out of the works on the near rails at (x, rail), 200 long: two big coupled
    ruby wheels with their balance weights, each in its axlebox between the horn guides of the frame plate over
    them, the coupling rod joining their crank pins, the frame's buffer beam at the front, and an iron wheel chock
    against each wheel at the rail. Returns its box and the rod's middle, where the oil goes."""
    d = Canvas()
    for wx in (-50, 50):                                                                       # the far wheels
        d.add(f'<circle cx="{wx + 7}" cy="-48" r="46" fill="{darken(P.CHARCOAL, 0.8)}" stroke="{INK}" '
              f'stroke-width="1.4"/>')
    pins = [wheel(d, wx, 46, 300, RUBY_DEEP) for wx in (-50, 50)]
    d.shape("M-100,-112 H96 V-80 H74 Q50,-104 26,-80 H-26 Q-50,-104 -74,-80 H-100 Z", P.CHARCOAL, sw=1.8,
            light=None)                                                                        # the frame plate
    d.line(" ".join(f"M{q},-108 v4" for q in range(-92, 92, 14)), 1.2, P.METAL_DARK)          # its rivets
    d.shape(rounded_rect_d(96, -118, 14, 40, 2), RUBY_DEEP, sw=1.6, light=None)               # the buffer beam
    for wx in (-50, 50):
        d.line(f"M{wx - 19},-84 V-36 M{wx + 19},-84 V-36", 3, P.CHARCOAL)                      # horn guides
        d.shape(rounded_rect_d(wx - 14, -63, 28, 28, 3), P.METAL_DARK, sw=1.4, light=None)    # the axlebox
        d.line(f"M{wx - 10},-49 h20", 1.2, P.METAL_PALE)
    d.tube(f"M{n(pins[0][0])},{n(pins[0][1])} L{n(pins[1][0])},{n(pins[1][1])}", P.METAL_LIGHT, 8, sw=1.4)
    for px, py in pins:
        d.add(f'<circle cx="{n(px)}" cy="{n(py)}" r="5" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1.2"/>')
    for cx, s_ in ((-50 - 44, 1), (50 + 44, -1)):                                             # the chocks
        d.shape(f"M{cx - s_ * 12},0 L{cx},0 L{cx - s_ * 2},-14 Z", P.METAL_DARK, sw=1.2, light=None)
    c.add(at(d, x, rail, k, way))
    mid = ((pins[0][0] + pins[1][0]) / 2, (pins[0][1] + pins[1][1]) / 2)
    lo_, hi_ = sorted((x - way * 108 * k, x + way * 112 * k))
    return {"box": (lo_, rail - 119 * k, hi_, rail), "pin": (x + way * mid[0] * k, rail + mid[1] * k),
            "axlebox": (x, rail - 48 * k)}


def bogie(c: Canvas, x: float, rail: float, k: float) -> dict:
    """A coach bogie run out from under its coach for the wheel tapper, on the near rail at (x, rail): the bogie of
    `bogie_side`, its centre pivot standing free on the bolster. Returns its box, the wheels and the hubs'
    height."""
    d = Canvas()
    bogie_side(d, 0, -BOGIE_TOP, far=True)
    c.add(_at(d, x, rail, k))
    half = WHEELBASE / 2 + BOGIE_R + 2
    return {"box": (x - half * k, rail - (BOGIE_TOP + 1) * k, x + (half + 6) * k, rail),
            "wheels": [x - WHEELBASE / 2 * k, x + WHEELBASE / 2 * k], "hub": rail - BOGIE_R * k, "r": BOGIE_R * k}


BOGIE_TOP = BOGIE_R + 32 + 10 + 14 + 8   # the run-out bogie's height: wheel, frame, springs, bolster, pivot


def stop_block(c: Canvas, x: float, rail: float, k: float, way: int = 1) -> dict:
    """The stop block at the end of a siding, on the near rail at (x, rail): a heavy timber baulk across the rails
    painted in red and white, held on the rail head by two iron shoes with their clamps, the short post behind it
    with its red lamp. Returns its box and its face."""
    d = Canvas()
    d.shape(rounded_rect_d(-18, -10, 50, 10, 2), P.METAL_DARK, sw=1.4, light=None)              # the shoes
    for bx in (-12, 26):
        d.add(f'<circle cx="{bx}" cy="-5" r="2" fill="{P.METAL_PALE}"/>')
    d.shape(rounded_rect_d(-14, -52, 42, 42, 3), P.WHITE, sw=1.8, light=None)                  # the baulk
    clip = d.shape(rounded_rect_d(-14, -52, 42, 42, 3), P.WHITE, sw=0, light=None, clip=True)
    d.add(f'<g clip-path="url(#{clip})">' + "".join(f'<path d="M-20,{-50 + q * 14} l50,-16 v7 l-50,16 Z" '
                                                     f'fill="{P.RED}"/>' for q in range(6)) + "</g>")
    d.path(rounded_rect_d(-14, -52, 42, 42, 3), "none", 1.8)
    d.line("M40,-10 V-70", 4, IRON)                                                            # the lamp post
    d.shape(rounded_rect_d(32, -86, 16, 18, 3), P.CHARCOAL, sw=1.2, light=None)
    d.add(f'<circle cx="40" cy="-77" r="5" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>')
    c.add(at(d, x, rail, k, way))
    lo_, hi_ = sorted((x - way * 16 * k, x + way * 50 * k))
    return {"box": (lo_, rail - 87 * k, hi_, rail), "face": x - way * 14 * k}


def wall_board(s: Strip, x: float, top: float, k: float) -> tuple:
    """The departures board hung on the station wall under the canopy, its top at `top`: the two iron brackets out
    of the wall, the chains, and the split-flap face (`flap_board`). Returns its box and the top row's middle."""
    c = Canvas()
    for bx in (x + 18 * k, x + 110 * k):
        c.line(f"M{n(bx)},{n(top)} V{n(top + 16 * k)}", max(1.0, 1.6 * k), P.METAL_DARK)
        c.add(f'<rect x="{n(bx - 6 * k)}" y="{n(top - 4 * k)}" width="{n(12 * k)}" height="{n(5 * k)}" '
              f'fill="{IRON}" stroke="{INK}" stroke-width="1"/>')
    s.put(s.line.feet - 1, c.render(), None)
    row = flap_board(s, x, top + 16 * k, k)
    return (x - 6 * k, top - 4 * k, x + 134 * k, top + 72 * k), row


def cable(s: Strip, a, b, width: float, floor: float) -> None:
    """The controller's cable from the terminal on the layout to the controller in the hand: down out of each, a
    loose loop hanging between them over the platform, never down to the paving."""
    low_ = min(floor - 4 * width, max(a.y, b.y) + max(30 * width, 30.0))
    mid = (a.x + b.x) / 2
    connect(s, a, b, "cable", width, via=((mid, low_),), depth=floor + 0.5, lead=(6 * width, 6 * width))


def controller(x: float, y: float, k: float) -> str:
    """The model railway's controller held in the fist: a black box out past the knuckles with its big speed knob
    and pointer, the red direction switch, the cable leaving its foot."""
    c = Canvas()
    c.shape(rounded_rect_d(-3, -6, 17, 13, 2), P.CHARCOAL, sw=0.7, light=(-0.5, -0.5))
    c.add(f'<circle cx="7.5" cy="0" r="3.6" fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width=".5"/>')
    c.line("M7.5,0 L9.6,-2.4", 0.7, P.RED)
    c.shape(rounded_rect_d(11, -4.6, 2, 3.4, 0.6), P.RED, sw=0.3, light=None)
    c.shape(rounded_rect_d(4, 7, 4, 2, 0.5), P.METAL_DARK, sw=0.3, light=None)
    return _at(c, x, y, k)


CONTROLLER_PORT = (6.0, 9.0)                                           # its cable's fitting, in the grip frame


def oilcan(x: float, y: float, k: float) -> str:
    """A driver's oil can held by its loop handle: the round brass body hanging forward under the fist, its thumb
    pump on top, the long thin spout reaching out to its tip."""
    c = Canvas()
    c.path("M-1.6,-6 Q-2,7 5,7", "none", 2, P.METAL_DARK)
    c.shape("M3,-1 Q2,10 10,11 Q18,10 17,-1 Q10,-5 3,-1 Z", P.GOLD, sw=0.7, light=(-1, -1))
    c.shape(rounded_rect_d(8, -5.6, 4, 3.4, 0.8), P.METAL, sw=0.5, light=None)
    c.path("M16,1 L40,6", "none", 2.6, INK)
    c.path("M16,1 L40,6", "none", 1.4, P.GOLD)
    return _at(c, x, y, k)


OILCAN_TIP = (40.0, 6.0)


def tapper(x: float, y: float, k: float) -> str:
    """The wheel tapper's hammer: its long ash shaft through the fist, out along the forearm to the small steel
    head at its end."""
    c = Canvas()
    c.path("M-5,0 L44,0", "none", 3, INK)
    c.path("M-5,0 L44,0", "none", 1.8, P.WOOD_PALE)
    c.shape(rounded_rect_d(42, -5, 6, 10, 1), P.METAL_DARK, sw=0.6, light=None)
    return _at(c, x, y, k)


TAPPER_TIP = (48.0, 3.0)


def telegram(x: float, y: float, k: float) -> str:
    """A telegram form held up by its lower corner: the buff form with its ruby heading band and ruled lines, two
    strips of pasted tape on it."""
    c = Canvas()
    c.shape(rounded_rect_d(-1.5, -17, 22, 18, 0.6), P.CARD, sw=0.6, light=None)
    c.shape(rounded_rect_d(0.5, -15.6, 18, 3, 0.4), RUBY, sw=0.3, light=None)
    c.line("M1.5,-10.5 H18.5 M1.5,-7.5 H18.5 M1.5,-4.5 H18.5 M1.5,-1.6 H12", 0.4, INK, 0.5)
    c.shape(rounded_rect_d(2, -9.8, 14, 1.8, 0.2), P.WHITE, sw=0.2, light=None)
    c.shape(rounded_rect_d(2, -6.8, 11, 1.8, 0.2), P.WHITE, sw=0.2, light=None)
    return _at(c, x, y, k)


def pen(x: float, y: float, k: float) -> str:
    """A fountain pen through the fist, its nib out under the little finger."""
    c = Canvas()
    c.shape("M-1,-7 H1 V7 H-1 Z", P.CHARCOAL, sw=0.5, light=None)
    c.shape("M-1.1,-8.4 H1.1 V-7 H-1.1 Z", P.GOLD, sw=0.3, light=None)
    c.shape("M-1,7 L0,11 L1,7 Z", P.GOLD, sw=0.4, light=None)
    return _at(c, x, y, k)


PEN_TIP = (0.0, 11.0)


def chalk(x: float, y: float, k: float) -> str:
    """A stick of white chalk through the fist, its worn end out under the little finger."""
    c = Canvas()
    c.shape(rounded_rect_d(-1.2, -5, 2.4, 12, 0.8), P.WHITE, sw=0.4, light=None)
    return _at(c, x, y, k)


CHALK_TIP = (0.0, 7.0)


def shunting_pole(length: float):
    """A shunter's pole `length` long (in the grip frame) through the fist: the ash shaft out along the forearm to
    its iron head, a hook curled back at the tip that lifts a coupling's link onto the hook of the next vehicle.
    Returns the drawing and its tip."""
    def draw(x: float, y: float, k: float) -> str:
        c = Canvas()
        c.path(f"M-6,0 L{n(length - 6)},0", "none", 3, INK)
        c.path(f"M-6,0 L{n(length - 6)},0", "none", 1.8, P.WOOD_PALE)
        c.shape(rounded_rect_d(length - 8, -1.8, 6, 3.6, 0.6), P.METAL_DARK, sw=0.5, light=None)
        c.path(f"M{n(length - 2)},0 L{n(length)},0 Q{n(length + 3)},0 {n(length + 3)},3 Q{n(length + 3)},5.5 "
               f"{n(length + 0.6)},5", "none", 1.6, P.METAL_DARK)
        return _at(c, x, y, k)
    return draw, (length, 0.0)


def bar_end(x: float, y: float, k: float) -> str:
    """The end of the coupling screw's tommy bar, through the fist."""
    c = Canvas()
    c.shape(rounded_rect_d(-1.1, -3, 2.2, 6, 0.8), P.METAL_LIGHT, sw=0.4, light=None)
    return _at(c, x, y, k)


def pocket_watch(x: float, y: float, k: float) -> str:
    """A pocket watch in the palm, its face to the viewer: the gold case and bow, the white dial at 4:04, the chain
    hanging from the bow."""
    c = Canvas()
    c.path("M0,-6 Q-6,-2 -5,6", "none", 0.6, P.GOLD)
    c.shape(rounded_rect_d(-1, -7.2, 2, 1.8, 0.6), P.GOLD, sw=0.4, light=None)
    c.shape(ellipse_d(0, 0, 5, 5), P.GOLD, sw=0.7, light=(-0.5, -0.5))
    c.add(f'<circle cx="0" cy="0" r="3.8" fill="{P.WHITE}" stroke="{INK}" stroke-width=".4"/>')
    c.add(clock_hands(0, 0, 1.8, 3, 0.45))
    return _at(c, x, y, k)


pocket_watch.grasp = "palm"
pocket_watch.radius = 5.0
pocket_watch.top = 7.2


BOARD_H = 300                                                          # the timetable board, foot to roof ridge
BOARD_ROWS = 6


def board_rows(foot: float, k: float) -> list[float]:
    """The page heights of the timetable's rows, top to bottom."""
    top, bottom = -212, -46
    rh = (bottom - top) / BOARD_ROWS
    return [foot + (top + (r + 0.5) * rh) * k for r in range(BOARD_ROWS)]


def timetable(s: Strip, x: float, foot: float, k: float, rows_done: int, signed: bool, chalking: bool,
              posts: bool = True) -> dict:
    """The station's timetable board on its two posts at (x, foot), as tall as a door: the little gabled roof with
    its cresting, the black board in its frame (a container), the ruby header plate with a gold engine on it; on
    the left a grid of runs - each row a little chalk train, the road's number in a ring and a tick once it has
    run - and on the right, pinned at chest height, the white sheet of the day's plan with the line for the
    signature at its foot. Returns its box, where the signature goes and where the next row is chalked."""
    pen_ = Pen(s, x, foot, k)
    c = pen_.c
    for px in (-74, 74) if posts else ():
        c.shape(rounded_rect_d(px - 5, -258, 10, 258, 2), P.WOOD_DARK, sw=1.6, light=(-1, 0))
        c.shape(rounded_rect_d(px - 8, -10, 16, 10, 2), P.STONE, sw=1.2, light=None)
    c.shape("M-96,-262 L0,-300 L96,-262 Z", RUBY, sw=2, light=(-2, -2))                       # the roof
    c.line(" ".join(f"M{q},{n(-262 - (96 - abs(q)) * 38 / 96)} v-5" for q in range(-84, 88, 12)), 1.4, IRON)
    c.shape(rounded_rect_d(-100, -264, 200, 6, 2), RUBY_DEEP, sw=1.4, light=None)
    board = pen_.container("timetable", -86, -256, 172, 220, mix(P.CHARCOAL, P.GREEN, 0.18), radius=3, sw=3,
                           light=None)
    c.path(rounded_rect_d(-86, -256, 172, 220, 3), "none", 5, P.WOOD)
    c.path(rounded_rect_d(-86, -256, 172, 220, 3), "none", 1.2, INK)
    pad = pen_.pad(172, 220)
    left, right = -86 + pad, 86 - pad
    c.shape(rounded_rect_d(left, -256 + pad, right - left, 22, 2), RUBY, sw=1.2, light=None)    # the header
    hy = -256 + pad
    c.shape(rounded_rect_d(-16, hy + 7, 24, 9, 2), P.GOLD, sw=0.6, light=None)
    c.shape(rounded_rect_d(-22, hy + 3, 8, 13, 1), P.GOLD, sw=0.6, light=None)
    c.shape(rounded_rect_d(4, hy + 2, 4, 6, 1), P.GOLD, sw=0.6, light=None)
    for wx in (-17, -9, -1, 5):
        c.add(f'<circle cx="{wx}" cy="{hy + 18}" r="2.2" fill="{P.GOLD}" stroke="{INK}" stroke-width=".5"/>')
    pen_.child(board, "header", left, hy, right, hy + 22)
    split = 22                                                          # the grid on the left, the sheet right
    top, bottom = -212, -46
    rh = (bottom - top) / BOARD_ROWS
    chalk_ = mix(P.WHITE, P.CHARCOAL, 0.08)
    for r in range(BOARD_ROWS):
        y = top + r * rh
        if r > 0:
            c.line(f"M{n(left)},{n(y)} H{n(split - 4)}", 0.8, chalk_, 0.5)
        if r < rows_done or (chalking and r == rows_done):
            cy = y + rh / 2
            c.path(rounded_rect_d(left + 2, cy - 4, 12, 7, 1.5), "none", 1.2, chalk_)               # the engine
            c.path(f"M{n(left + 4)},{n(cy - 4)} v-3", "none", 1.2, chalk_)
            c.path(rounded_rect_d(left + 16, cy - 3, 10, 6, 1), "none", 1.2, chalk_)                # a coach
            c.add(f'<circle cx="{n(left + 38)}" cy="{n(cy)}" r="6" fill="none" stroke="{chalk_}" '
                  f'stroke-width="1.2"/>')
            q = r % 3
            nx = left + 38
            c.path(f"M{n(nx)},{n(cy - 3.4)} V{n(cy + 3.4)}" if q == 0 else
                   f"M{n(nx - 2.4)},{n(cy - 2)} q2.4,-3 4.6,0 l-4.6,5 h5" if q == 1 else
                   f"M{n(nx - 2.4)},{n(cy - 3)} h4.4 l-2.6,2.6 q3,0 2.6,2.6 q-1.6,1.6 -4.4,0", "none", 1.1,
                   chalk_)
            end = split - 22 if r < rows_done else left + 60
            c.path(f"M{n(left + 48)},{n(cy)} H{n(end)}", "none", 1.2, chalk_)
            if r < rows_done:
                c.path(f"M{n(split - 18)},{n(cy)} l3,4 l7,-9", "none", 1.6, chalk_)
            pen_.child(board, f"row{r}", left + 2, cy - 7.5, split - 6, cy + 6)
    c.line(f"M{split},{top} V{bottom}", 1, chalk_, 0.5)
    st, sb = -186, -96                                                  # the sheet, its signature line at its foot
    sl, sr = split + 6, right
    c.shape(rounded_rect_d(sl, st, sr - sl, sb - st, 1), P.WHITE, sw=1, light=None)
    c.add(f'<circle cx="{n((sl + sr) / 2)}" cy="{st + 5}" r="2.2" fill="{P.RED}" stroke="{INK}" '
          f'stroke-width=".5"/>')
    c.line(" ".join(f"M{n(sl + 6)},{n(st + 14 + q * 8)} H{n(sr - 6 - (12 if q % 3 == 2 else 0))}"
                    for q in range(7)), 0.6, INK, 0.45)
    sig = (sl + 8, sb - 8)
    c.line(f"M{n(sig[0])},{n(sig[1])} H{n(sr - 8)}", 0.8, INK, 0.75)
    if signed:
        c.path(f"M{n(sig[0] + 2)},{n(sig[1] - 2)} q4,-8 8,-1 q3,-6 6,0 q4,-4 7,1 q3,-3 6,0", "none", 1.3, P.BLUE)
    pen_.child(board, "sheet", sl, st, sr, sb)
    box = pen_.box(-100, -300, 100, 0 if posts else -32)
    s.put(s.line.feet - 1 if not posts else foot - 1, pen_.svg(), box, "timetable", group="timetable")
    ry = top + rows_done * rh + rh / 2
    return {"box": box, "sign": pen_.at(sig[0] + 26, sig[1] - 3), "row": pen_.at(left + 58, ry),
            "tick": pen_.at(split - 12, ry - rh), "edge": pen_.at(86, -150)}


def lever_foot(s: Strip, g: Line) -> tuple[float, float, float]:
    """Where the points' ground lever stands, its rod's length factor and its depth: in a strip in the ballast at
    the track's edge, its rod running along the sleepers to the switch; in a taller frame the track lies beyond the
    deep platform, so the lever stands on the paving a step behind the one who throws it, its rod run under the
    platform (none seen)."""
    if low(s):
        return g.kerb - 1, 1.0, g.rail + 0.9
    foot = g.feet - LEVER_BACK * g.t
    return foot, 0.0, foot - 0.5


LEVER_BACK = 0.12               # a tall frame's lever: that much of the tallest of the cast behind the feet line


def point_lever(c: Canvas, x: float, foot: float, k: float, handle: tuple[float, float], way: int = 1,
                rod: float = 130) -> dict:
    """A ground lever for the points at (x, foot): its timber sleeper, the cast-iron stand with its quadrant
    plate, the lever from the pivot out to `handle` (page space) with its catch, the white-and-red weight on its
    short arm opposite, and from the stand the rod off along the ground to the switch. Returns its box and the
    rod's end."""
    d = Canvas()
    d.shape(rounded_rect_d(-46, -8, 92, 8, 1), SLEEPER, sw=1.4, light=None)
    d.shape("M-26,-8 L-20,-34 H20 L26,-8 Z", IRON, sw=1.6, light=(-1, -1))
    d.shape("M-30,-34 A30,30 0 0 1 30,-34 Z", IRON, sw=1.4, light=None)                        # the quadrant
    d.line(" ".join(f"M{n(math.cos(a) * 26)},{n(-34 - math.sin(a) * 26)} l{n(math.cos(a) * 3)},"
                    f"{n(-math.sin(a) * 3)}" for a in (math.radians(q) for q in range(20, 170, 15))), 1, P.METAL_PALE)
    d.line(f"M46,-4 H{rod}", 3, P.METAL_DARK)                                                  # the rod
    for q in range(70, int(rod) - 10, 34):
        d.shape(rounded_rect_d(q - 3, -8, 6, 8, 1), P.METAL_DARK, sw=0.8, light=None)
    c.add(at(d, x, foot, k, way))
    px, py = x, foot - 34 * k
    hx, hy = handle
    ang = math.atan2(hy - py, hx - px)
    wx, wy = px - math.cos(ang) * 22 * k, py - math.sin(ang) * 22 * k                          # the weight's arm
    c.add(f'<path d="M{n(wx)},{n(wy)} L{n(hx)},{n(hy)}" stroke="{INK}" stroke-width="{n(6 * k + 2.4)}" '
          f'stroke-linecap="round"/><path d="M{n(wx)},{n(wy)} L{n(hx)},{n(hy)}" stroke="{P.METAL_DARK}" '
          f'stroke-width="{n(6 * k)}" stroke-linecap="round"/>')
    c.add(f'<circle cx="{n(wx)}" cy="{n(wy)}" r="{n(13 * k)}" fill="{P.WHITE}" stroke="{INK}" stroke-width="1.6"/>'
          f'<path d="M{n(wx - 13 * k)},{n(wy)} A{n(13 * k)},{n(13 * k)} 0 0 0 {n(wx + 13 * k)},{n(wy)} Z" '
          f'fill="{P.RED}" stroke="{INK}" stroke-width="1.2"/>')                               # the weight
    c.add(f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(5 * k)}" fill="{P.METAL}" stroke="{INK}" stroke-width="1.2"/>')
    cx_, cy_ = hx - math.cos(ang) * 14 * k, hy - math.sin(ang) * 14 * k
    c.add(f'<circle cx="{n(cx_)}" cy="{n(cy_)}" r="{n(2.6 * k)}" fill="{P.METAL_LIGHT}" stroke="{INK}" '
          f'stroke-width=".8"/>')                                                               # the catch
    lo_, hi_ = sorted((x - way * 48 * k, x + way * (rod + 2) * k))
    top = min(hy, wy - 13 * k, foot - 64 * k)
    stand_ = (min(x - 48 * k, hx - 4, wx - 14 * k), top - 4, max(x + 48 * k, hx + 4, wx + 14 * k), foot)
    r0, r1 = sorted((x + way * 46 * k, x + way * (rod + 2) * k))
    return {"box": (min(lo_, stand_[0]), top - 4, max(hi_, stand_[2]), foot), "boxes": [stand_, (r0, foot - 8 * k,
            r1, foot)], "rod": (x + way * rod * k, foot - 4 * k)}


def turnout(c: Canvas, rails: list[float], xs: float, k: float, way: int) -> None:
    """The points at xs on the near road: the switch blade, and off it the crossovers - each a short curved track
    on its ballast and sleepers - rising to the roads beyond on the side the trains stand (`way`)."""
    for q in (2, 1):
        target = rails[q]
        span_ = (90 + 60 * q) * k
        x1 = xs - way * span_
        d = (f"M{n(xs)},{n(rails[0])} C{n(xs - way * span_ * 0.5)},{n(rails[0])} "
             f"{n(x1 + way * span_ * 0.45)},{n(target)} {n(x1)},{n(target)}")
        kk = max(0.5, k * (1 - q * 0.2))
        c.add(f'<path d="{d}" fill="none" stroke="{darken(BALLAST, 0.72)}" stroke-width="{n(14 * kk)}" '
              f'transform="translate(0,{n(5 * kk)})"/>'
              f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{n(5 * kk + 1)}" '
              f'stroke-dasharray="{n(16 * kk)} {n(8 * kk)}" transform="translate(0,{n(4 * kk)})"/>'
              f'<path d="{d}" fill="none" stroke="{SLEEPER}" stroke-width="{n(5 * kk)}" '
              f'stroke-dasharray="{n(16 * kk)} {n(8 * kk)}" transform="translate(0,{n(4 * kk)})"/>'
              f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{n(2.6 * kk + 1.4)}"/>'
              f'<path d="{d}" fill="none" stroke="{P.METAL}" stroke-width="{n(2.6 * kk)}"/>')
    c.add(f'<path d="M{n(xs)},{n(rails[0] - 1.6 * k)} L{n(xs - way * 80 * k)},{n(rails[0] - 4 * k)}" '
          f'stroke="{INK}" stroke-width="{n(2 * k + 1.2)}"/><path d="M{n(xs)},{n(rails[0] - 1.6 * k)} '
          f'L{n(xs - way * 80 * k)},{n(rails[0] - 4 * k)}" stroke="{P.METAL_LIGHT}" stroke-width="{n(2 * k)}"/>')


def semaphore(c: Canvas, x: float, foot: float, k: float, down: bool, way: int = 1) -> dict:
    """A semaphore signal at (x, foot), 320 tall: the lattice post on its concrete base with the ladder up it and
    the finial on top; the arm - ruby with its white band - on its spindle near the top, level for danger or
    dropped for line clear, the spectacle plate with its red and green glasses, the lamp case behind it; at the
    foot the balance lever with its weight, and the wire up the post to the arm. Returns its box."""
    d = Canvas()
    d.shape(rounded_rect_d(-14, -10, 28, 10, 1), P.STONE, sw=1.4, light=None)
    d.line("M-6,-10 L-4,-300 M6,-10 L4,-300", 2.4, IRON)
    d.line(" ".join(f"M{-6 + q * 0.007},{-10 - q} L{6 - q * 0.007},{-10 - q - 16}" for q in range(0, 280, 16)),
           1.2, IRON)
    d.line("M-14,-14 V-250 M-22,-14 V-250", 1.4, P.METAL_DARK)                                 # the ladder
    d.line(" ".join(f"M-22,{-20 - q * 12} H-14" for q in range(20)), 1, P.METAL_DARK)
    d.shape("M-7,-300 H7 L4,-312 L0,-322 L-4,-312 Z", IRON, sw=1.2, light=None)                # the finial
    d.shape(rounded_rect_d(-10, -276, 20, 16, 2), P.CHARCOAL, sw=1.2, light=None)              # the lamp case
    d.add(f'<circle cx="0" cy="-268" r="3" fill="{P.YELLOW_PALE}"/>')
    ang = 40 if down else 0
    d.add(f'<g transform="rotate({ang} 4 -268)">')
    d.shape("M4,-273 H78 V-263 H4 Z", RUBY, sw=1.6, light=(-1, -1))                            # the arm
    d.shape("M58,-273 H66 V-263 H58 Z", P.WHITE, sw=0.8, light=None)
    d.shape("M-4,-276 L10,-262 L10,-240 L-6,-240 Z", RUBY_DEEP, sw=1.2, light=None)           # spectacle plate
    d.add(f'<circle cx="2" cy="-256" r="4" fill="{P.RED}" stroke="{INK}" stroke-width=".8"/>'
          f'<circle cx="2" cy="-246" r="4" fill="{P.GREEN}" stroke="{INK}" stroke-width=".8"/>')
    d.add("</g>")
    d.add(f'<circle cx="4" cy="-268" r="2.4" fill="{P.METAL}" stroke="{INK}" stroke-width=".8"/>')
    d.line("M10,-30 L36,-20", 3, P.METAL_DARK)                                                 # the balance lever
    d.shape(rounded_rect_d(30, -28, 12, 14, 2), P.CHARCOAL, sw=1, light=None)
    d.line("M8,-34 V-262", 0.8, P.METAL_LIGHT)                                                 # the wire
    c.add(at(d, x, foot, k, way))
    lo_, hi_ = sorted((x - way * 24 * k, x + way * 80 * k))
    if down:
        hi_ = max(hi_, x + way * 66 * k) if way > 0 else hi_
    return {"box": (min(lo_, hi_), foot - 322 * k, max(lo_, hi_), foot)}


def clock_post(c: Canvas, x: float, foot: float, k: float, way: int = 1, post: bool = True) -> dict:
    """The platform clock at (x, foot), 270 tall: the fluted cast-iron column in ruby on its base and plinth, the
    capital, the scrolled bracket arm out to one side and, hanging from it on its stem, the round clock in its ruby
    case with the white dial, the twelve marks and its hands at 4:04. Returns its box and the clock's middle."""
    d = Canvas()
    if post:
        d.shape(rounded_rect_d(-16, -14, 32, 14, 2), IRON, sw=1.6, light=None)
        d.shape(rounded_rect_d(-11, -24, 22, 10, 2), IRON, sw=1.4, light=None)
        d.shape(rounded_rect_d(-7, -214, 14, 190, 3), RUBY, sw=1.6, light=(-1, 0))
        d.line(" ".join(f"M{q},-210 V-28" for q in (-3, 0, 3)), 0.8, RUBY_DEEP)
        d.shape(rounded_rect_d(-11, -224, 22, 10, 2), IRON, sw=1.4, light=None)
        d.add(f'<circle cx="0" cy="-232" r="7" fill="{IRON}" stroke="{INK}" stroke-width="1.2"/>')
    else:                                                              # its bracket bolted to the wall
        d.shape(rounded_rect_d(-8, -236, 16, 30, 2), IRON, sw=1.4, light=None)
        for by in (-230, -212):
            d.add(f'<circle cx="0" cy="{by}" r="2" fill="{P.METAL_PALE}"/>')
    d.path("M0,-222 H64 M4,-206 Q30,-208 44,-222 M14,-214 q-2,-8 6,-8", "none", 4, IRON)    # the bracket
    d.line("M60,-222 V-212", 3, IRON)
    d.add(f'<circle cx="60" cy="-178" r="34" fill="{RUBY}" stroke="{INK}" stroke-width="2.2"/>'
          f'<circle cx="60" cy="-178" r="27" fill="{P.WHITE}" stroke="{INK}" stroke-width="1.6"/>')
    d.line(" ".join(f"M{n(60 + math.cos(a) * 22)},{n(-178 + math.sin(a) * 22)} "
                    f"L{n(60 + math.cos(a) * 26)},{n(-178 + math.sin(a) * 26)}"
                    for a in (q * math.pi / 6 for q in range(12))), 1.6, INK)
    d.add(clock_hands(60, -178, 12, 20, 2.2))
    d.add(f'<circle cx="60" cy="-178" r="2.4" fill="{INK}"/>')
    c.add(at(d, x, foot, k, way))
    lo_, hi_ = sorted((x - way * 16 * k, x + way * 96 * k))
    return {"box": (lo_, foot - 239 * k, hi_, foot if post else foot - 142 * k),
            "clock": (x + way * 60 * k, foot - 178 * k)}


def bench(c: Canvas, x: float, foot: float, k: float, seat: float = 46, half: float = 86) -> dict:
    """A platform bench at (x, foot), 170 long, its seat `seat` high: cast-iron ends with scrolled arms, ruby slats
    on the seat and the back. Returns its box, the seat's height and its back's top."""
    d = Canvas()
    back_top = seat + 46
    for ex in (-half + 8, half - 8):
        d.path(f"M{ex - 10},0 Q{ex - 4},{-seat * 0.6} {ex},{-seat} L{ex + 2},{-back_top} M{ex + 10},0 "
               f"Q{ex + 4},{-seat * 0.6} {ex},{-seat}", "none", 4.4, IRON)
        d.path(f"M{ex},{-seat - 4} q{'-' if ex < 0 else ''}12,-4 {'-' if ex < 0 else ''}14,-16", "none", 3.4, IRON)
    d.shape(rounded_rect_d(-half, -seat - 2, 2 * half, 5, 2), RUBY, sw=1, light=None)
    for q in range(3):
        d.shape(rounded_rect_d(-half + 2, -back_top + q * 13, 2 * half - 4, 8, 2), RUBY, sw=1.2, light=None)
    c.add(_at(d, x, foot, k))
    return {"box": (x - (half + 6) * k, foot - (back_top + 2) * k, x + (half + 6) * k, foot), "seat": foot - seat * k,
            "back": foot - back_top * k}


def stop_post(c: Canvas, x: float, foot: float, k: float, way: int = 1, open_: bool = False) -> dict:
    """The emergency-stop post at (x, foot), 170 tall: the iron post on its foot plate, the big yellow box on it
    with black chevrons along its foot, the big red mushroom button in its dark recess, and the clear hinged cover
    over it, shut, its hinge along the top. Returns its box, the button and the cover's front."""
    d = Canvas()
    d.shape(rounded_rect_d(-18, -6, 36, 6, 1), IRON, sw=1.2, light=None)
    d.shape(rounded_rect_d(-6, -84, 12, 78, 2), IRON, sw=1.4, light=(-1, 0))
    d.shape(rounded_rect_d(-40, -170, 80, 88, 5), P.YELLOW, sw=2, light=(-1, -1))
    clip = d.shape(rounded_rect_d(-40, -170, 80, 88, 5), P.YELLOW, sw=0, light=None, clip=True)
    d.add(f'<g clip-path="url(#{clip})">' + "".join(f'<path d="M{-50 + q * 16},-82 l14,-14 h7 l-14,14 Z" '
                                                     f'fill="{INK}"/>' for q in range(8)) + "</g>")
    d.shape(rounded_rect_d(-28, -160, 56, 52, 4), P.CHARCOAL, sw=1.4, light=None)
    d.add(f'<circle cx="0" cy="-134" r="19" fill="{darken(P.RED, 0.75)}" stroke="{INK}" stroke-width="1.6"/>'
          f'<circle cx="0" cy="-137" r="15" fill="{P.RED}" stroke="{INK}" stroke-width="1.4"/>'
          f'<ellipse cx="-5" cy="-142" rx="5" ry="3" fill="{P.WHITE}" opacity=".5"/>')
    cover = (f'<path d="M-32,-164 H32 V-104 H-32 Z" fill="{P.LENS}" fill-opacity=".28" stroke="{INK}" '
             f'stroke-width="1.6"/><path d="M-26,-158 L-14,-112" stroke="{P.WHITE}" stroke-width="2" opacity=".5"/>')
    if open_:                                                          # the cover swung up on its hinge
        cover = f'<g transform="translate(0,-166) scale(1,-0.45) translate(0,166)">{cover}</g>'
    d.add(cover + f'<rect x="-34" y="-168" width="68" height="5" rx="2" fill="{P.METAL_DARK}" stroke="{INK}" '
          f'stroke-width="1"/>')
    c.add(at(d, x, foot, k, way))
    return {"box": (x - 41 * k, foot - 171 * k, x + 41 * k, foot), "button": (x, foot - 136 * k),
            "cover": (x - way * 18 * k, foot - 126 * k)}


# ============================================================================ placing the cast
def tall_of(s: Strip, name: str) -> float:
    return s.tall * SIZE[name]


def stand(s: Strip, name: str, x: float, pose: str, mood: str = "smile", face: int = 1, group: str | None = None,
          feet: float | None = None, depth: float | None = None):
    """A character at x on the platform (or at `feet`), facing `face` (1 right, -1 left)."""
    feet = s.line.feet if feet is None else feet
    pose = pose if pose in characters.module(name).POSES else "present"
    return s.actor(name, x, feet, pose, mood, flip=face < 0, tall=tall_of(s, name), group=group or name,
                   depth=depth)


def fit_x(s: Strip, name: str, x: float, feet: float | None = None) -> float:
    """x moved, if need be, so that the character stands whole within the frame's usable width."""
    feet = s.line.feet if feet is None else feet
    b = _box(s, name, x, feet)
    half = (b[2] - b[0]) / 2
    return min(max(x, s.lo + half + 2), s.hi - half - 2)


def place_free(s: Strip, name: str, f0: float, pose: str, mood: str = "smile", face: int = 1,
               hold=None, group: str | None = None):
    """A character at the nearest spot to `f0` (read from the station's side) where it stands whole and clear
    of everything but the furniture it stands in front of; None if there is none."""
    feet = s.line.feet
    name = getattr(s, "swap", {}).get(name, name)
    if not name or any(b.kind == "actor" and b.name == name for b in s.boxes):
        return None
    near = [b for b in s.boxes if b.kind != "backdrop" or b.bottom > feet - IN_FRONT]
    if near:                                                           # beside what is already there, on its side
        lo_, hi_ = min(b.left for b in near), max(b.right for b in near)
        x0 = X(s, f0)
        x0 = lo_ - 10 if x0 < (lo_ + hi_) / 2 else hi_ + 10
        f0 = (x0 - s.lo) / (s.hi - s.lo)
        f0 = f0 if s.way > 0 else 1 - f0
    for f in sorted((i / 60 for i in range(61)), key=lambda f_: abs(f_ - f0)):
        x = X(s, f)
        b = _box(s, name, x, feet)
        if b[0] < s.lo - 4 or b[2] > s.hi + 4 or b[1] < 2:
            continue
        if any(o.hits(b, 3) and not (o.kind == "backdrop" and feet - o.bottom >= IN_FRONT) for o in s.boxes):
            continue
        if any(Box(*zone, "", "").hits(b) for zone in [*s.reserved, *getattr(s, "keep_off", [])]):
            continue
        who = stand(s, name, x, pose, mood, face, group)
        if hold is not None:
            s.hold(who, hold)
        return who
    return None


def on_track(s: Strip, svg: str, box: tuple, name: str, depth: float | None = None) -> None:
    """Something standing on the near track: big furniture the cast on the platform may stand in front of."""
    s.put(s.line.rail + 0.5 if depth is None else depth, svg, box, name, group=name, backdrop=True)


def grip_at(s: Strip, name: str, x: float, pose: str, face: int, feet: float | None = None,
            side: str = "right") -> tuple[float, float, float]:
    """Where a character standing at x would close its fist - worked out on a stage of its own."""
    probe = Stage()
    feet = s.line.feet if feet is None else feet
    who = probe.actor(name, x, feet, pose, "smile", flip=face < 0, tall=tall_of(s, name))
    return probe.grip(who, side, pose)


def reach_x(s: Strip, name: str, pose: str, face: int, target: tuple[float, float], length: float,
            feet: float | None = None, side: str = "right") -> float:
    """The x to stand a character at so that its fist is `length` from `target`, on the side it faces away from:
    a lever, a beam end or a hammer reaching that far."""
    gx, gy, _ = grip_at(s, name, 0.0, pose, face, feet, side)
    dy = target[1] - gy
    dx = math.sqrt(max(0.0, length * length - dy * dy))
    return target[0] - face * dx - gx


def reach_or_aim(s: Strip, name: str, pose: str, face: int, target: tuple[float, float], length: float) -> float:
    """The x to stand a character at so that a held thing `length` long reaches `target`; where the target is out
    of its reach - on a train beyond the deep platform - the x from which it aims the thing up at it, a step back
    along the platform."""
    gx0, gy0, _ = grip_at(s, name, 0.0, pose, face)
    rise = gy0 - target[1]
    if rise <= length:
        return reach_x(s, name, pose, face, target, length)
    return target[0] - face * LEAN * rise - gx0


def clear_of(s: Strip, name: str, x: float, box: tuple, face: int) -> float:
    """x moved back, if need be, so that a character facing `face` stands beside the vehicle in `box`, not in front
    of it: its hand may reach the vehicle's end, its body never covers it."""
    b = _box(s, name, x, s.line.feet)
    if face > 0 and b[2] > box[0]:
        return x - (b[2] - box[0]) - 1
    if face < 0 and b[0] < box[2]:
        return x + (box[2] - b[0]) + 1
    return x


def keep_clear(s: Strip, who, target: tuple[float, float]) -> None:
    """Keep the rest of the cast off the line from `who`'s fist up to `target`, along which it holds a long thing:
    a zone that `place_free` keeps the onlookers out of."""
    gx, gy, _ = s.grip(who, "right")
    box = (min(gx, target[0]) - 4, min(gy, target[1]), max(gx, target[0]) + 4, max(gy, target[1]) + 4)
    s.keep_off = [*getattr(s, "keep_off", []), box]


def away_from(s: Strip, who, target: tuple[float, float]) -> float:
    """A place across the frame (read from the station's side) beside `who` on the side away from `target`, for an
    onlooker to stand clear of what `who` holds up at it."""
    x = who.right + 40 if target[0] < (who.left + who.right) / 2 else who.left - 40
    f = (x - s.lo) / (s.hi - s.lo)
    return f if s.way > 0 else 1 - f


def hold_reaching(s: Strip, who, make, tip: tuple[float, float], target: tuple[float, float]) -> None:
    """Hand a long thing to a character, turned about the fist so that its `tip` (in the grip frame) points at
    `target` (the turn is applied in the grip frame, before the hand's own mirroring - `in_hand`)."""
    gx, gy, _ = s.grip(who, "right")
    want = math.atan2(target[1] - gy, target[0] - gx)
    best, turn = None, 0
    for deg in range(-180, 180):
        a = math.radians(deg)
        u = tip[0] * math.cos(a) - tip[1] * math.sin(a)
        v = tip[0] * math.sin(a) + tip[1] * math.cos(a)
        px, py = in_hand(s, who, u, v)
        err = abs(math.remainder(math.atan2(py - gy, px - gx) - want, 2 * math.pi))
        if best is None or err < best:
            best, turn = err, deg
    s.hold(who, make, turn=turn)


def hand_len(s: Strip, name: str, tip: tuple[float, float]) -> float:
    """How far a held thing's tip is from the fist on the page."""
    return math.hypot(*tip) * height(s, name) / 100


def bird_on(s: Strip, x: float, top: float, group: str) -> None:
    """The sparrow perched on something a bird sits on: a bar, a rail, a bench back, a lamp."""
    sparrow_on(s, x, top, group)


def _framed(draw):
    """A station drawn as it is or mirrored, by turns, the camera a step nearer on the next visit."""
    def run(s: Strip, beat: str) -> None:
        s.again = (s.seed // 2) % 2 == 1
        s.mirror = bool(s.shot) != s.again
        s.way = -1 if s.mirror else 1
        base, _, swap = beat.partition("@")                            # a later moment: another onlooker,
        s.swap = dict(pair.split(">") for pair in swap.split(",")) if swap else {}
        if base.endswith("+"):                                         # and the camera a step nearer
            base = base[:-1]
            if not low(s):
                s.tall *= 1.22
                s.unit = s.tall / 137
                s._room = None
        draw(s, base)
        company(s)
    return run


def grip_y(s: Strip, name: str, pose: str = "present") -> float:
    """How high a character standing on the platform holds its fist."""
    return grip_at(s, name, 0.0, pose, 1)[1]


def hand_on(s: Strip, name: str, target: tuple[float, float], pose: str, face: int, group: str | None = None,
            feet: float | None = None, mood: str = "smile"):
    """A character standing so that its fist is at `target` across (the thing is set at its height)."""
    gx0, _, _ = grip_at(s, name, 0.0, pose, face, feet)
    return stand(s, name, target[0] - gx0, pose, mood, face=face, group=group, feet=feet)


def crowd(s: Strip, names: tuple[str, ...], things: float) -> None:
    """Step the camera back, if need be, until the cast `names` and things `things` professors wide fit across
    the frame side by side, with air between."""
    for _ in range(4):
        feet = lane(s).feet
        widths = [(_box(s, x, 0, feet)[2] - _box(s, x, 0, feet)[0]) for x in names]
        need = sum(widths) + things * height(s, "professor") + 18 * (len(names) + 2)
        f = (s.hi - s.lo) / need
        if f >= 1:
            return
        s.tall *= f * 0.98
        s.unit = s.tall / 137


def company(s: Strip) -> None:
    """Two of the cast at least in every frame: if the station's own could not all stand, one more joins, looking
    on from wherever there is room."""
    here = {b.name for b in s.boxes if b.kind == "actor" and b.name != "sparrow"}
    want = 2
    for name in ("cat", "caterpillar", "agent", "professor"):
        if len(here) >= want:
            return
        if name in here:
            continue
        for f0 in (0.04, 0.96, 0.5, 0.25, 0.75):
            if place_free(s, name, f0, "think", "smile", face=1 if f0 < 0.5 else -1) is not None:
                here.add(name)
                break


def X(s: Strip, f: float) -> float:
    """A place across the frame, read from the side the station faces: mirrored on a mirrored page."""
    return s.x(f if s.way > 0 else 1 - f)


# ============================================================================ the stations
def small_station(s: Strip, beat: str) -> None:
    """A small task, no train needed: "telegram" - on the platform the professor hands the agent the telegram
    form, the handcar waiting on the rails behind; "pump" - the agent on the handcar pumps its beam and is off
    down the line, dust flying from the wheels, the cat and the caterpillar seeing him off."""
    w = s.way
    g = setting(s, vehicle=1.7, rider=True) if beat == "pump" and not low(s) else setting(s)
    p = height(s, "professor")
    k = min(0.95 * p / 110 * s.track_depth, (g.rail - 6) / 110)
    c = Canvas()
    if beat in ("telegram", "back"):
        hx = X(s, 0.66)
        hc = handcar(c, hx, g.rail, k, w)
        piv = hc["pivot"]
        end = (piv[0] + w * 50 * k, piv[1] - 26 * k)
        beam(c, piv, end, k)
        on_track(s, c.render(), hc["box"], "handcar")
        giver, taker = ("professor", "agent") if beat == "telegram" else ("agent", "professor")
        if beat == "back":                                             # back from the run: the agent at the car
            half = (_box(s, "agent", 0, g.feet)[2] - _box(s, "agent", 0, g.feet)[0]) / 2
            giver_x = fit_x(s, "agent", hc["box"][0] - half - 8 if w > 0 else hc["box"][2] + half + 8)
            face_g = -w
        else:
            giver_x, face_g = fit_x(s, "professor", X(s, 0.12)), w
        who = stand(s, giver, giver_x, "present", "talk" if giver == "professor" else "smile", face=face_g,
                    group="hand")
        s.hold(who, telegram)
        gx, gy, _ = s.grip(who, "right")
        reach = 21 * tall_of(s, giver) / 100 * 0.8
        tx = reach_x(s, taker, "present", -face_g, (gx + face_g * reach, gy), 0.0)
        stand(s, taker, tx, "present" if taker == "agent" else "read", "smile", face=-face_g, group="hand")
        place_free(s, "caterpillar", 0.95, "think", "smile", face=-w)
        bird_on(s, 2 * piv[0] - end[0], 2 * piv[1] - end[1] - 6 * k, "handcar")
        return
    hx = X(s, 0.56)
    hc = handcar(c, hx, g.rail, k, w)
    piv = hc["pivot"]
    deck = hc["deck"]
    if low(s):                                                         # a strip: the agent pushes it off
        d = Canvas()
        for wx in hc["wheels"]:
            dust(d, wx - w * 8 * k, g.rail, k, w, int(wx))
        s.put(g.rail + 0.4, d.render(), None)
        beam(c, piv, (piv[0] + w * 50 * k, piv[1] - 22 * k), k)
        on_track(s, c.render(), hc["box"], "handcar")
        end = (hx - w * 74 * k, deck + 4 * k)
        gx0, gy0, _ = grip_at(s, "agent", 0.0, "present", w)
        stand(s, "agent", clear_of(s, "agent", fit_x(s, "agent", end[0] - gx0), hc["box"], w), "present", "smile",
              face=w, group="handcar")
        place_free(s, "caterpillar", 0.96, "cheer", "smile", face=-w)
        return
    L = 52 * k
    ax = reach_x(s, "agent", "present", w, piv, L, feet=deck)
    ax = max(min(ax, hx + 70 * k), hx - 70 * k)
    who = stand(s, "agent", ax, "present", "smile", face=w, group="handcar", feet=deck, depth=g.rail + 0.7)
    gx, gy, _ = s.grip(who, "right")
    d = Canvas()
    for wx in hc["wheels"]:
        dust(d, wx - w * 8 * k, g.rail, k, w, int(wx))
    s.put(g.rail + 0.4, d.render(), None)
    on_track(s, c.render(), hc["box"], "handcar")
    b = Canvas()
    beam(b, piv, (gx, gy), k)
    s.put(g.rail + 0.8, b.render(), None)
    place_free(s, "cat", 0.05, "think", "smile", face=w)
    place_free(s, "caterpillar", 0.95, "cheer", "smile", face=-w)


def rs_k(s: Strip) -> float:
    """The scale of the rolling stock at its true size against the cast: the engine two and a half agents tall,
    smaller with the distance when the track lies beyond a deep platform."""
    return agent_h(s) * 2.5 / ENGINE_H * getattr(s, "track_depth", 1.0)


def roles_station(s: Strip, beat: str) -> None:
    """How the roles change: "model" - the caterpillar runs her model railway, the controller in her hand and its
    cable to the layout's terminal, the agent watching the little train come out of the tunnel; "real" - the cat
    oils the real thing with his long-spouted can: the coupling rods of the engine standing at the platform, or in
    a strip the axlebox of a wagon, the agent looking on."""
    w = s.way
    if beat == "model":
        crowd(s, ("caterpillar", "agent"), 1.1)
        g = setting(s)
        p = height(s, "professor")
        k = min(0.42 * p / 112, (g.feet - 6) / 179)
        c = Canvas()
        tx = X(s, 0.45)
        ml = model_layout(c, tx, g.feet - 2, k, seed=s.index, way=w)
        s.put(g.feet - 2, c.render(), ml["box"], "model", group="model")
        half = (_box(s, "caterpillar", 0, g.feet)[2] - _box(s, "caterpillar", 0, g.feet)[0]) / 2
        cx = tx + w * (134 * k + half + 6)
        who = stand(s, "caterpillar", cx, "present", "smile", face=-w)
        s.hold(who, controller)
        a = in_hand(s, who, *CONTROLLER_PORT)
        b_ = in_hand(s, who, CONTROLLER_PORT[0], CONTROLLER_PORT[1] + 1)
        pa = port(s, a[0], a[1], b_[0] - a[0], b_[1] - a[1], "caterpillar")
        tx_, ty_ = ml["terminal"]
        pb = port(s, tx_, ty_ + 4 * k, 0, 1, "model")
        cable(s, pb, pa, max(1.2, 2.2 * k), g.feet)
        s.layout = ml
        place_free(s, "agent", 0.1, "think", "smile", face=w)
        return
    if low(s):
        g = setting(s)
        k = rs_k(s)
        c = Canvas()
        k = min(k, (g.rail - 4) / 120)
        dw = driving_wheels(c, X(s, 0.58), g.rail, k, w)
        on_track(s, c.render(), dw["box"], "wagon")
        target = dw["pin"]
    else:
        g = setting(s, vehicle=2.5)
        k = rs_k(s)
        c = Canvas()
        front = X(s, 0.42) + w * 248 * k
        lo = locomotive(c, front, g.rail, k, steam=False, tender=False, way=w)
        box = (max(0.0, lo["box"][0]), lo["box"][1], min(float(W), lo["box"][2]), lo["box"][3])
        on_track(s, c.render(), box, "engine")
        target = lo["rod"]
    face = w
    x = reach_or_aim(s, "cat", "present", face, target, hand_len(s, "cat", OILCAN_TIP))
    if low(s):                                                         # beside the wheels, the spout in at the rod
        x = clear_of(s, "cat", x, dw["box"], face)
    who = stand(s, "cat", fit_x(s, "cat", x), "present", "smile", face=face, group="wagon" if low(s) else None)
    hold_reaching(s, who, oilcan, OILCAN_TIP, target)
    keep_clear(s, who, target)
    place_free(s, "agent", away_from(s, who, target), "think", "smile", face=-w)


def plan_station(s: Strip, beat: str) -> None:
    """A big task: the timetable board under its little roof, as tall as a door (in a strip it hangs on the
    station wall, at eye level) - "sign": the professor signs the day's plan at its foot with his pen, the cat
    looking on; "chalk": the agent chalks in the next run, the caterpillar ticks it off on her list."""
    w = s.way
    crowd(s, ("professor", "cat") if beat == "sign" else ("agent", "caterpillar"), 1.0)
    g = setting(s)
    t_ = g.t
    posts = not low(s)
    if posts:
        k = min(1.3 * t_ / BOARD_H, (g.feet - 4) / BOARD_H)
        foot = g.feet
    else:                                                              # on the wall: its foot at the waist
        k = min(1.3 * t_ / BOARD_H, (g.feet - 0.3 * t_ - 6) / 268)
        foot = g.feet - 0.3 * t_ + 36 * k
    bx = X(s, 0.4)

    def probe_(rows_done, chalking):
        st = Strip(s.h, 0, None, s.look)
        st.line = g
        return timetable(st, bx, foot, k, rows_done, False, chalking, posts)

    if beat == "sign":
        target = probe_(3, False)["sign"]
        who_name, make, tip, pose = "professor", pen, PEN_TIP, "present"
    else:
        rows = board_rows(foot, k)
        gy = grip_at(s, "agent", 0, "present", -w)[1]
        done = min(range(1, BOARD_ROWS), key=lambda r: abs(rows[r] - gy))
        target = probe_(done, True)["row"]
        who_name, make, tip, pose = "agent", chalk, CHALK_TIP, "present"
    face = -w
    x = reach_x(s, who_name, pose, face, target, hand_len(s, who_name, tip))
    if beat == "sign":
        timetable(s, bx, foot, k, 3, True, False, posts)
    else:
        timetable(s, bx, foot, k, done, False, True, posts)
    who = stand(s, who_name, x, pose, "smile", face=face, group="timetable")
    hold_reaching(s, who, make, tip, target)
    if beat == "sign":
        place_free(s, "cat", 0.06, "think", "smile", face=w)
    else:
        place_free(s, "caterpillar", 0.95, "present", "smile", face=-w, hold=checklist(mates(s)))


def parallel_station(s: Strip, beat: str) -> None:
    """Several tasks at once: the points - the near road splits at the switch and its crossovers climb to the two
    roads beyond; on each road its own train, one after another along the line and smaller with the distance,
    none in front of another (in a strip the roads alone). The ground lever stands in the ballast at the track's
    edge, its rod running along the sleepers to the switch blades. "set": the agent pulls the lever over against
    its weight, the caterpillar fretting; "run": the lever is over, the trains are off, the professor watching."""
    w = s.way
    crowd(s, ("agent", "professor", "caterpillar"), 0.9)
    shares = (1.0, 0.6, 0.38)
    span = (s.hi - s.lo) * 0.94
    for _ in range(6):                                                 # the camera steps back for the three trains
        if low(s):
            break
        k, kt = rs_k(s), max(0.6, Line(s).t / 200)
        need = (90 + 60 * 2) * kt + 10 + 476 * k * (shares[2] + shares[1] + 0.36) + 48
        if need <= span:
            break
        s.tall *= span / need * 0.98
        s.unit = s.tall / 137
    g = setting(s, vehicle=0 if low(s) else 2.55, roads=3)
    k = rs_k(s)
    kt = max(0.6, g.t / 200)
    xs = X(s, 0.97)
    c = Canvas()
    turnout(c, g.rails, xs, kt, w)
    s.put(0.06, c.render(), None)
    if not low(s):
        f = xs - w * (90 + 60 * 2) * kt - w * 10                       # the far train ahead, past the crossovers
        fronts = []
        for q in (2, 1, 0):                                             # one after another, each one clear
            fronts.append((q, f))
            f -= w * (476 * k * shares[q] + 26 * k * (shares[q - 1] if q else 0) + 30)
        for q, front in fronts:
            kq = k * shares[q]
            tc = Canvas()
            tr = train(tc, front, g.rails[q], kq, moving=beat == "run", cars=0, steam="low" if beat == "run" and
                       q == 0 and s.steam else False, seed=q, way=w, tender=False)
            box = tr["box"]
            if box[1] < 3 or (q > 0 and (box[0] < 0 or box[2] > W)):
                continue
            box = (max(0.0, box[0]), box[1], min(float(W), box[2]), box[3])
            s.put(g.rails[q] + 0.5, tc.render(), box, f"train{q}", group="lever")
    p = height(s, "professor")
    lk = 0.25 * p / 34
    foot, rods, depth = lever_foot(s, g)
    lx = X(s, 0.62)
    L = 74 * lk
    pivot = (lx, foot - 34 * lk)
    face = -w if beat == "set" else w                                  # pulling it towards him, then over
    if face:
        ax = reach_x(s, "agent", "present", face, pivot, L)
        fx_ = fit_x(s, "agent", ax)
        lx += fx_ - ax                                                 # the lever moves, the agent stays in frame
        pivot = (lx, pivot[1])
        who = stand(s, "agent", fx_, "present", "smile", face=face, group="lever")
        gx, gy, _ = s.grip(who, "right")
        handle = (gx, gy)
    c2 = Canvas()
    rod = max(46.0, rods * abs(xs - lx) / lk)
    pl = point_lever(c2, lx, foot, lk, handle, w, rod=rod)
    s.put(depth, c2.render(), pl["boxes"][:1], "lever", group="lever")   # the rod lies behind feet
    if beat == "run":
        place_free(s, "professor", 0.95, "think", "smile", face=-w)
    else:
        place_free(s, "caterpillar", 0.15, "think", "worry", face=w)


def to_pr_station(s: Strip, beat: str) -> None:
    """From code to the pull request: "tap" - the wheel tapper's round: the cat taps a wheel by its axlebox with
    his long hammer and the caterpillar listens for the ring - a coach's bogie wheel, in a strip a wagon's; "couple"
    - two buffer beams meet and the agent screws the coupling up between them, the professor looking on."""
    w = s.way
    crowd(s, ("agent", "professor", "cat"), 0.6)
    g = setting(s, vehicle=0 if low(s) else 2.6)
    k = rs_k(s)
    c = Canvas()
    if beat == "tap":
        if low(s):
            v = bogie(c, X(s, 0.6), g.rail, min(k, (g.rail - 4) / (BOGIE_TOP + 1)))
            wx = v["wheels"][0 if w > 0 else 1]
        else:
            lead = X(s, 0.55) + w * 50 * k
            v = coach(c, lead, g.rail, k, way=w)
            wx = v["wheels"][2]
        box = (max(0.0, v["box"][0]), v["box"][1], min(float(W), v["box"][2]), v["box"][3])
        on_track(s, c.render(), box, "stock")
        face = w
        target = (wx - face * v["r"] * 0.9, v["hub"])
        x = fit_x(s, "cat", reach_or_aim(s, "cat", "present", face, target, hand_len(s, "cat", TAPPER_TIP)))
        who = stand(s, "cat", x, "present", "smile", face=face)
        hold_reaching(s, who, tapper, TAPPER_TIP, target)
        keep_clear(s, who, target)
        place_free(s, "caterpillar", away_from(s, who, target), "think", "smile", face=w)
        return
    mid = (s.x(0.72 if s.clear == "left" else 0.28) if low(s)          # the far ends run off the side away
           else X(s, 0.48))                                            # from the page number
    gap = 6 * k
    if low(s):                                                         # the wagon rolling up: room between the
        gap = _box(s, "agent", 0, g.feet)[2] - _box(s, "agent", 0, g.feet)[0] + 18  # buffers for the agent
        a = wagon(c, mid - gap / 2 - 128 * k, g.rail, k, 1)
        b = wagon(c, mid + gap / 2 + 128 * k, g.rail, k, 1)
        hooks = (a["hooks"][1], b["hooks"][0])
        load = g.rail - 148 * k >= 3
        for v_, q in ((a, 0), (b, 1)) if load else ():                 # their loads: crates and sacks
            crates(c, (v_["box"][0] + v_["box"][2]) / 2, g.rail - 96 * k, k, q)
        box = (max(0.0, a["box"][0]), min(a["box"][1], b["box"][1]) - (52 * k if load else 0),
               min(float(W), b["box"][2]), g.rail)
    else:
        a = coach(c, mid - gap / 2, g.rail, k, way=1)
        b = coach(c, mid + gap / 2, g.rail, k, way=-1)
        hooks = ((mid - gap / 2 - 4 * k, g.rail - 100 * k), (mid + gap / 2 + 4 * k, g.rail - 100 * k))
        box = (0.0, min(a["box"][1], b["box"][1]), float(W), g.rail)
    on_track(s, c.render(), (box[0], box[1], mid - gap / 2, box[3]) if low(s) else box, "stock")
    if low(s):
        s.put(g.rail + 0.5, "", (mid + gap / 2, box[1], box[2], box[3]), "stock", group="stock", backdrop=True)
    face = -w
    centre = ((hooks[0][0] + hooks[1][0]) / 2, max(hooks[0][1], hooks[1][1]) + 4 * k)
    cc = Canvas()
    if low(s):                                                         # a strip: in the gap between the buffers,
        who = stand(s, "agent", mid - face * 0.06 * gap, "present", "smile", face=face, group="stock")   # the
        s.hold(who, bar_end)
        gx, gy, _ = s.grip(who, "right")
        hook = hooks[0] if face < 0 else hooks[1]                      # coupling off the hook he faces in his fist
        screw_coupling(cc, hook, (gx, gy), ((hook[0] + gx) / 2, max(hook[1], gy) + 14 * k), k)
    else:                                                              # a tall frame: from the deep platform,
        lift = (centre[0], centre[1] - 6 * k)                          # the link lifted on the shunter's pole
        gx0, gy0, _ = grip_at(s, "agent", 0.0, "present", face)
        ax = lift[0] - face * LEAN * (gy0 - lift[1]) - gx0
        who = stand(s, "agent", fit_x(s, "agent", ax), "present", "smile", face=face, group="pole")
        gx, gy, _ = s.grip(who, "right")
        span = math.hypot(lift[0] - gx, lift[1] - gy) * 100 / height(s, "agent")
        make, tip = shunting_pole(span)
        hold_reaching(s, who, make, tip, lift)
        keep_clear(s, who, lift)
        mx = (hooks[0][0] + hooks[1][0]) / 2                           # done up: the tommy bar hangs down
        screw_coupling(cc, hooks[0], hooks[1], (mx + 5 * k, centre[1] + 18 * k), k)
    s.put(g.rail + 0.7, cc.render(), None)
    place_free(s, "professor", 0.1, "think", "smile", face=w)


def to_prod_station(s: Strip, beat: str) -> None:
    """From merge to production: "depart" - the semaphore at the platform end has dropped its arm, the train pulls
    out in its steam, the departures board hangs under the far canopy; the caterpillar cheers, the agent
    points at the signal; "terminus" - at the end of the line the engine stands buffers to buffers against the
    buffer stop (in a strip the last wagon), the professor and the cat at it."""
    w = s.way
    if beat == "board":                                                # the professor reads it this time
        s.swap = {"caterpillar": "professor"}
    if beat in ("depart", "board"):
        g = setting(s, vehicle=0 if low(s) or beat == "board" else 2.95)
        k = rs_k(s)
        c = Canvas()
        if low(s) or beat == "board":                                  # the departures board on the wall
            bk = min(g.t * 1.1 / 134, (g.feet - 0.4 * g.t - 10) / 80)
            bx = X(s, 0.6) - 67 * bk
            box, row = wall_board(s, bx, 6 + 4 * bk, bk)
            s.put(g.feet - 1, "", box, "board", group="board")
            half = (_box(s, "agent", 0, g.feet)[2] - _box(s, "agent", 0, g.feet)[0]) / 2
            ax = box[2] + half + 6 if w > 0 else box[0] - half - 6     # beside the board, pointing at its row
            stand(s, "agent", ax, "point", "smile", face=-w)
        else:
            front = X(s, 0.7)
            tr = train(c, front, g.rail, k, moving=True, cars=2, steam="low", way=w)
            box = (max(0.0, tr["box"][0]), tr["box"][1], min(float(W), tr["box"][2]), g.rail)
            on_track(s, c.render(), box, "train")
            sc = Canvas()
            sm = semaphore(sc, X(s, 0.9), g.rail + 3, k, True, w)
            if sm["box"][1] > 3 and sm["box"][0] > 0 and sm["box"][2] < W:
                s.put(g.rail + 2, sc.render(), sm["box"], "signal", group="train", backdrop=True)
        place_free(s, "caterpillar", 0.12, "cheer", "smile", face=w)
        place_free(s, "agent", 0.32, "point", "smile", face=w)
        return
    engine = not low(s)                                                # the engine itself, the cast stepping back
    g = setting(s, vehicle=2.5 if engine else 0)
    k = min(rs_k(s), (g.rail - 4) / 154)
    c = Canvas()
    bx = X(s, 0.8)
    if not engine:                                                     # a strip: the siding's stop block
        k = rs_k(s)
        sb = stop_block(c, X(s, 0.55), g.rail, min(k, (g.rail - 4) / 88), w)
        items = [sb["box"]]
    else:
        bs = buffer_stop(c, bx, g.rail, k, w)
        lo = locomotive(c, bs["face"] - w * 26 * k, g.rail, k, steam=s.steam, tender=False, way=w)
        items = [bs["box"], lo["box"]]
    box = (max(0.0, min(b[0] for b in items)), min(b[1] for b in items), min(float(W), max(b[2] for b in items)),
           g.rail)
    on_track(s, c.render(), box, "buffer")
    place_free(s, "professor", 0.18, "thumb", "smile", face=w)
    place_free(s, "cat", 0.93, "present", "smile", face=-w, hold=mug)


def metrics_station(s: Strip, beat: str) -> None:
    """How to tell it got better: the platform clock on its cast-iron post at 4:04 - "watch": the professor holds
    his pocket watch up to it, the train standing in at the platform behind, on time; "check": the cat compares
    the two and the caterpillar ticks it off."""
    w = s.way
    g = setting(s, vehicle=0 if low(s) else 2.6)
    k = rs_k(s)
    if not low(s):
        c = Canvas()
        tr = train(c, X(s, 1.0) + w * 300 * k, g.rail, k, cars=5, steam=False, way=w)
        on_track(s, c.render(), (0.0, tr["box"][1], float(W), g.rail), "train")
    t_ = g.t
    c2 = Canvas()
    cx = X(s, 0.42)
    if low(s):                                                         # a strip: the clock on its wall bracket
        cy = g.feet - 0.64 * t_
        ck = min(1.25 * t_ / 178, (cy - 8) / 58)
        cp = clock_post(c2, cx, cy + 178 * ck, ck, w, post=False)
    else:
        ck = min(1.25 * t_ / 178, (g.feet - 6) / 239)
        cp = clock_post(c2, cx, g.feet - 1, ck, w)
    s.put(g.feet - 1, c2.render(), cp["box"], "clock", group="train")
    who_name = "professor" if beat == "watch" else "cat"
    x = cp["box"][2] + 40 if w > 0 else cp["box"][0] - 40
    who = place_free(s, who_name, (x - s.lo) / (s.hi - s.lo) if w > 0 else 1 - (x - s.lo) / (s.hi - s.lo),
                     "present", "smile", face=-w)
    if who is not None:
        s.hold(who, pocket_watch)
    if beat == "check":
        place_free(s, "caterpillar", 0.95, "present", "smile", face=-w, hold=checklist(mates(s)))
    else:
        place_free(s, "agent", 0.08, "think", "smile", face=w)


def no_human_station(s: Strip, beat: str) -> None:
    """Development without a human: "past" - the train glides by with nobody in its cab, the professor and the
    cat watching it from the platform bench, the sparrow on the bench's back; in a strip the handcar rolls by
    with its beam rocking and nobody on it; "gone": the agent points after it, the caterpillar wonders."""
    w = s.way
    g = setting(s, vehicle=0 if low(s) else 2.5 if beat == "gone" else 2.95)
    k = rs_k(s)
    c = Canvas()
    if low(s):
        p = height(s, "professor")
        hk = min(0.95 * p / 110, (g.rail - 6) / 110)
        for f in ((0.72, 0.66, 0.6) if beat == "past" else (0.9, 0.85, 0.8, 0.75, 0.7)):
            hx = X(s, f)
            probe = handcar(Canvas(), hx, g.rail, hk, w)["box"]
            if not any(Box(*zone, "", "").hits(probe) for zone in s.reserved):
                break
        hc = handcar(c, hx, g.rail, hk, w)
        piv = hc["pivot"]
        tilt = math.radians(22 if beat == "past" else -18)
        beam(c, piv, (piv[0] + w * 52 * hk * math.cos(tilt), piv[1] - 52 * hk * math.sin(tilt)), hk)
        d = Canvas()
        for wx in hc["wheels"]:
            dust(d, wx - w * 8 * hk, g.rail, hk, w, int(wx))
        s.put(g.rail + 0.4, d.render(), None)
        box = (max(0.0, hc["box"][0]), hc["box"][1], min(float(W), hc["box"][2]), g.rail)
        on_track(s, c.render(), box, "handcar")
    else:
        cars = 2
        length = (ENGINE_L + 14 + cars * (COACH_L + 4)) * k
        front = X(s, 0.95) if beat == "past" else X(s, 0.62) + w * length
        if beat != "past":                  # in a tall frame the train is bigger: its last coach stays in the picture
            show = 0.4 * COACH_L * k
            rear = front - w * length
            rear = min(rear, W - show) if w > 0 else max(rear, show)
            front = rear + w * length
        tr = train(c, front, g.rail, k, cab=False, moving=True, cars=cars, steam="low" if beat == "past" else False,
                   way=w)
        if beat == "gone":                                             # the tail lamp on the last coach's end
            tail_lamp(c, front - w * length + w * 14 * k, g.rail, k, w)
        on_track(s, c.render(), (max(0.0, tr["box"][0]), tr["box"][1], min(float(W), tr["box"][2]), g.rail),
                 "train")
    if beat == "past":
        p = height(s, "professor")
        bk = 0.25 * p / 46
        b = Canvas()
        bx = X(s, 0.3)
        empty = getattr(s, "swap", {}).get("cat") == ""
        bn = bench(b, bx, g.feet - 1, bk, half=50 if empty else 130)
        s.put(g.feet - 3, b.render(), bn["box"], "bench", group="train")
        for name, dx in ((("caterpillar" if low(s) else "professor"), -80), ("cat", 30)):
            if getattr(s, "swap", {}).get(name) == "":                 # the bench left empty this time
                continue
            stand(s, name, bx + w * dx * bk, "sit", "smile", face=w, group="train", feet=g.feet - 1,
                  depth=g.feet - 2)
        bird_on(s, bx + w * (25 if empty else 112) * bk, bn["back"], "train")
    else:
        place_free(s, "agent", 0.35, "point", "smile", face=w)
        place_free(s, "caterpillar", 0.12, "think", "worry", face=w)


def check_station(s: Strip, beat: str) -> None:
    """Checking where you are still needed: the emergency-stop post at the platform edge - "reach": the sparrow
    dives at its red button and the cat has his paw on the cover, the agent startled; "stopped": the cover still
    shut, the sparrow sitting on the box, the caterpillar ticking her list, the professor's thumb up."""
    w = s.way
    g = setting(s)
    foot = g.feet - 2
    gy = grip_at(s, "cat", 0.0, "present", s.way)[1]
    sk = min((foot - gy) / 126, (g.feet - 8) / 172)                    # the cover at the cat's paw
    c = Canvas()
    px = X(s, 0.55)
    sp = stop_post(c, px, foot, sk, w)
    s.put(foot, c.render(), sp["box"], "stop", group="stop")
    if beat == "reach":
        face = w
        x = reach_x(s, "cat", "present", face, sp["cover"], 0.0)
        stand(s, "cat", x, "present", "talk", face=face, group="stop")
        bird = _box(s, "sparrow", 0, 0, 0.5)
        bh = bird[3] - bird[1]
        s.actor("sparrow", px + w * 30 * sk, sp["box"][1] - 4 + bh * 0.2, "fly", "smile", flip=w > 0,
                tall=s.tall * SIZE["sparrow"] * 0.5, group="stop")
        place_free(s, "agent", 0.9, "shrug", "worry", face=-w)
    else:
        bird_on(s, px, sp["box"][1], "stop")
        place_free(s, "caterpillar", 0.25, "present", "smile", face=w, hold=checklist(mates(s)))
        place_free(s, "professor", 0.88, "thumb", "smile", face=-w)


# ============================================================================ the later moments of each station
def key_(x: float, y: float, k: float) -> str:
    """A clock key through the fist: the brass bow in the hand, the shank out to the square socket."""
    c = Canvas()
    c.shape(rounded_rect_d(-2.4, -4, 4.8, 8, 2), P.GOLD, sw=0.5, light=None)
    c.path("M2,0 H11", "none", 1.6, P.GOLD)
    c.shape(rounded_rect_d(10, -1.4, 3, 2.8, 0.4), P.METAL_DARK, sw=0.3, light=None)
    return _at(c, x, y, k)


def switch_lamp(c: Canvas, x: float, foot: float, top: float, k: float, sleeper: bool = True) -> dict:
    """The points' lamp: an iron post up to `top` from its sleeper by the switch (`sleeper`) or, in a tall frame
    where the track lies beyond the deep platform, from a cast-iron foot on the paving; the square lamp case on it
    with its chimney and a white and a green lens. Returns its box and the lamp's middle. The post keeps a short
    length of its own when the hand that trims it is lower than its foot."""
    top = min(top, foot - 16 * k)
    if sleeper:
        c.add(f'<rect x="{n(x - 24 * k)}" y="{n(foot - 6 * k)}" width="{n(48 * k)}" height="{n(6 * k)}" '
              f'fill="{SLEEPER}" stroke="{INK}" stroke-width="1"/>')
    else:                                                              # on the paving: a cast-iron foot
        c.add(f'<path d="M{n(x - 12 * k)},{n(foot)} L{n(x - 5 * k)},{n(foot - 6 * k)} H{n(x + 5 * k)} '
              f'L{n(x + 12 * k)},{n(foot)} Z" fill="{IRON}" stroke="{INK}" stroke-width="1"/>')
    c.add(f'<rect x="{n(x - 3 * k)}" y="{n(top)}" width="{n(6 * k)}" height="{n(foot - 6 * k - top)}" '
          f'fill="{IRON}" stroke="{INK}" stroke-width="1"/>')
    c.add(f'<rect x="{n(x - 12 * k)}" y="{n(top - 22 * k)}" width="{n(24 * k)}" height="{n(24 * k)}" rx="{n(3 * k)}" '
          f'fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="1.4"/>'
          f'<path d="M{n(x - 8 * k)},{n(top - 22 * k)} l{n(8 * k)},{n(-10 * k)} l{n(8 * k)},{n(10 * k)} Z" '
          f'fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="1.2"/>'
          f'<circle cx="{n(x - 4.5 * k)}" cy="{n(top - 10 * k)}" r="{n(4 * k)}" fill="{P.WHITE}" stroke="{INK}" '
          f'stroke-width="1"/><circle cx="{n(x + 4.5 * k)}" cy="{n(top - 10 * k)}" r="{n(4 * k)}" fill="{P.GREEN}" '
          f'stroke="{INK}" stroke-width="1"/>')
    return {"box": (x - 25 * k, top - 33 * k, x + 25 * k, foot), "lamp": (x, top - 10 * k)}


def repose(s: Strip, box, pose: str) -> None:
    """Draw a character already standing again in another pose."""
    index, how = s.drawn[id(box)]
    s.drawn[id(box)] = (index, {**how, "pose": pose})
    s.redraw(box)


def exchange(s: Strip, giver: str, taker: str, make, x: float, face: int, group: str, taker_pose: str = "present"):
    """`giver` at x holding a thing out to `taker`, who stands facing him with a hand out for it."""
    who = stand(s, giver, x, "present", "talk", face=face, group=group)
    s.hold(who, make)
    gx, gy, _ = s.grip(who, "right")
    reach = 21 * tall_of(s, giver) / 100 * 0.8
    tx = reach_x(s, taker, "present", -face, (gx + face * reach, gy), 0.0)
    return who, stand(s, taker, tx, taker_pose, "smile", face=-face, group=group)


def roles_more(s: Strip, beat: str) -> None:
    """"signal": the agent leans over the layout to set its tiny signal, the caterpillar at the controller, the cat
    looking on; "card": the professor hands the caterpillar a timetable card by her layout."""
    w = s.way
    if beat == "signal":
        s.swap = {"agent": "cat"}
        roles_station(s, "model")
        sx, sy = s.layout["signal"]
        for b in s.boxes:                                              # one group: he leans in past her
            if b.name == "caterpillar":
                b.group = "model"
        hand_on(s, "agent", (sx, sy), "point", -w, group="model", feet=s.line.feet - 3)
        return
    crowd(s, ("caterpillar", "professor"), 1.1)
    g = setting(s)
    p = height(s, "professor")
    k = min(0.42 * p / 112, (g.feet - 6) / 179)
    c = Canvas()
    tx = X(s, 0.3)
    ml = model_layout(c, tx, g.feet - 2, k, seed=s.index + 2, way=w)
    s.put(g.feet - 2, c.render(), ml["box"], "model", group="model")
    half = (_box(s, "professor", 0, g.feet)[2] - _box(s, "professor", 0, g.feet)[0]) / 2
    exchange(s, "professor", "caterpillar", handheld.card, fit_x(s, "professor", X(s, 0.92)), -w, "hand")
    del half


def plan_more(s: Strip, beat: str) -> None:
    """"tick": the caterpillar ticks the last run off on the board with her pencil, the agent looking on; "notice":
    the cat pins a notice to the board's frame, the professor reading it."""
    w = s.way
    crowd(s, ("caterpillar", "professor") if beat == "tick" else ("cat", "professor"), 1.0)
    g = setting(s)
    t_ = g.t
    posts = not low(s)
    if posts:
        k = min(1.3 * t_ / BOARD_H, (g.feet - 4) / BOARD_H)
        foot = g.feet
    else:
        k = min(1.3 * t_ / BOARD_H, (g.feet - 0.3 * t_ - 6) / 268)
        foot = g.feet - 0.3 * t_ + 36 * k
    bx = X(s, 0.4)
    st = Strip(s.h, 0, None, s.look)
    st.line = g
    st.way = s.way
    probe = timetable(st, bx, foot, k, 4, True, False, posts)
    if beat == "tick":
        target = probe["tick"]
        x = reach_x(s, "caterpillar", "present", -w, target, hand_len(s, "caterpillar", (0.0, 11.4)))
        timetable(s, bx, foot, k, 4, True, False, posts)
        who = stand(s, "caterpillar", x, "present", "smile", face=-w, group="timetable")
        hold_reaching(s, who, handheld.pencil, (0.0, 11.4), target)
        place_free(s, "professor", 0.1, "think", "smile", face=w)
        return
    timetable(s, bx, foot, k, 4, True, False, posts)
    edge = (bx + w * 100 * k + w * 4, grip_y(s, "cat"))
    who = hand_on(s, "cat", edge, "present", -w, group="timetable")
    s.hold(who, handheld.sheet)
    place_free(s, "professor", 0.05, "read", "smile", face=w)


def parallel_more(s: Strip, beat: str) -> None:
    """"branch": the lever over, a train runs off the near road through the points onto the branch in its steam
    (in a strip the handcar has taken the branch), the caterpillar watching; "lamp": the agent trims the points'
    lamp on its post by the switch, the professor watching."""
    w = s.way
    g = setting(s, vehicle=0 if low(s) or beat == "lamp" else 2.6, roads=3)
    kt = max(0.6, g.t / 200)
    xs = X(s, 0.62)
    c = Canvas()
    turnout(c, g.rails, xs, kt, w)
    s.put(0.06, c.render(), None)
    p = height(s, "professor")
    if beat == "branch":
        k = rs_k(s)
        tc = Canvas()
        if low(s):
            hk = min(0.95 * p / 110, (g.rails[1] - 6) / 110) * 0.9
            hc = handcar(tc, xs - w * (110 + 60) * kt - w * 70 * hk, g.rails[1], hk, -w)
            beam(tc, hc["pivot"], (hc["pivot"][0] - w * 50 * hk, hc["pivot"][1] - 20 * hk), hk)
            box = hc["box"]
        else:
            tr = train(tc, xs - w * (110 + 60) * kt, g.rails[1], k * 0.8, moving=True, cars=1,
                       steam="low" if s.steam else False, way=-w, tender=False)
            box = (max(0.0, tr["box"][0]), tr["box"][1], min(float(W), tr["box"][2]), g.rails[1])
        s.put(g.rails[1] + 0.5, tc.render(), box, "train", group="lever", backdrop=True)   # the lever before it
        lk = 0.25 * p / 34
        foot, rods, depth = lever_foot(s, g)
        lx = X(s, 0.86) if low(s) else X(s, 0.2)                      # clear of the train on the branch
        pivot = (lx, foot - 34 * lk)
        handle = (pivot[0] + w * 74 * lk * math.cos(math.radians(35)), pivot[1] - 74 * lk * math.sin(math.radians(35)))
        lc = Canvas()
        pl = point_lever(lc, lx, foot, lk, handle, -w, rod=max(46.0, rods * abs(lx - xs) / lk))
        s.put(depth, lc.render(), pl["boxes"][:1], "lever", group="lever")
        place_free(s, "caterpillar", 0.4, "cheer", "smile", face=w)
        place_free(s, "professor", 0.95, "point", "smile", face=-w)
        return
    lamp_top = grip_y(s, "agent") + 10 * (p / 140)
    lc = Canvas()
    lk = p / 90
    foot, _, depth = lever_foot(s, g)                                  # by the track, or on the deep platform
    sl = switch_lamp(lc, xs + w * 30 * lk, foot, lamp_top, lk, sleeper=low(s))
    s.put(depth, lc.render(), sl["box"], "lamp", group="lamp")
    hand_on(s, "agent", (sl["box"][0] - 2 if w > 0 else sl["box"][2] + 2, sl["lamp"][1]), "present", w, group="lamp")
    place_free(s, "professor", 0.95, "think", "smile", face=-w)


def to_pr_more(s: Strip, beat: str) -> None:
    """"listen": the caterpillar bends to the axlebox with her ear to the wheel the cat has just tapped, the
    professor waiting; "buffer": the coupling done up, the professor feels the buffers with his hand, the agent
    beside."""
    if beat == "listen":
        s.swap = {"caterpillar": "professor"}
        to_pr_station(s, "tap")
        cat_ = next(b for b in s.boxes if b.kind == "actor" and b.name == "cat")      # the cat steps aside:
        idx = s.boxes.index(cat_)                                      # the caterpillar is at the wheel instead
        item = s.drawn[id(cat_)][0]
        s.items[item] = (s.items[item][0], s.items[item][1], "")
        del s.boxes[idx]
        stand(s, "caterpillar", (cat_.left + cat_.right) / 2, "think", "surprise", face=1 if not cat_.flip else -1)
        return
    s.swap = {"professor": "cat"}
    to_pr_station(s, "couple")
    ag = next(b for b in s.boxes if b.kind == "actor" and b.name == "agent")    # the agent done, he steps away:
    item = s.drawn[id(ag)][0]                                          # the professor at the buffers instead
    s.items[item] = (s.items[item][0], s.items[item][1], "")
    s.boxes.remove(ag)
    face = -1 if ag.flip else 1
    if low(s):                                                         # in the gap between the buffers
        stand(s, "professor", (ag.left + ag.right) / 2, "present", "smile", face=face, group="stock")
    else:                                                              # on the platform where the agent stood
        f = ((ag.left + ag.right) / 2 - s.lo) / (s.hi - s.lo)
        place_free(s, "professor", f if s.way > 0 else 1 - f, "point", "smile", face=face)


def to_prod_more(s: Strip, beat: str) -> None:
    """"leave": the train has pulled out and steams away along the line, the caterpillar and the professor seeing it
    off (in a strip its steam drifts in over the track from beyond the frame); "lamp": at the buffer stop the cat
    checks its red lamp, the caterpillar beside him."""
    w = s.way
    if beat == "lamp":
        s.swap = {"professor": "caterpillar"}
        to_prod_station(s, "terminus")
        cat_ = next((b for b in s.boxes if b.kind == "actor" and b.name == "cat"), None)
        if cat_ is not None:
            repose(s, cat_, "point")
        return
    g = setting(s, vehicle=0 if low(s) else 2.95)
    k = rs_k(s)
    c = Canvas()
    if low(s):
        edge = W + 10 if w > 0 else -10
        puffs(c, edge, g.rail - 0.2 * g.t, 0.3 * g.t, -w * 0.5 * W, 8, 22, 14, s.index)
        s.put(g.rail + 0.4, c.render(), None)
    else:
        front = X(s, 0.25)
        tr = train(c, front, g.rail, k, moving=True, cars=2, steam="low" if s.steam else False, way=-w)
        box = (max(0.0, tr["box"][0]), tr["box"][1], min(float(W), tr["box"][2]), g.rail)
        on_track(s, c.render(), box, "train")
    place_free(s, "caterpillar", 0.6, "cheer", "smile", face=-w)
    place_free(s, "professor", 0.85, "welcome", "smile", face=-w)


def metrics_more(s: Strip, beat: str) -> None:
    """"wind": the agent winds the station clock on the wall with its key, the professor watching; "notebook": by
    the clock the caterpillar writes the times down, the cat reading the departures board."""
    w = s.way
    g = setting(s)
    t_ = g.t
    c = Canvas()
    if beat == "wind":
        cy = grip_y(s, "agent") - 4
        ck = min(1.25 * t_ / 178, (cy - 8) / 58)
        cx = X(s, 0.5)
        cp = clock_post(c, cx, cy + 178 * ck, ck, w, post=False)
        s.put(g.feet - 1, c.render(), cp["box"], "clock", group="clock")
        who = hand_on(s, "agent", (cp["clock"][0] - w * 30 * ck, cp["clock"][1]), "present", w, group="clock")
        s.hold(who, key_)
        place_free(s, "caterpillar", 0.95, "think", "smile", face=-w)
        return
    bk = min(t_ * 1.0 / 134, (g.feet - 0.4 * t_ - 10) / 80)
    box, _ = wall_board(s, X(s, 0.62) - 67 * bk, 6 + 4 * bk, bk)
    s.put(g.feet - 1, "", box, "board", group="board")
    place_free(s, "cat", 0.7, "read", "smile", face=-w)
    place_free(s, "caterpillar", 0.2, "write", "smile", face=w)


def no_human_more(s: Strip, beat: str) -> None:
    """"wave": the agent waves to the empty cab of the train going by, the professor beside him; "knit": the
    caterpillar knits by the bench while the sparrow on its back watches the driverless train go."""
    if beat == "wave":
        s.swap = {"caterpillar": "professor"}
        no_human_station(s, "gone")
        ag = next((b for b in s.boxes if b.kind == "actor" and b.name == "agent"), None)
        if ag is not None:
            repose(s, ag, "wave")
        return
    s.swap = {"professor": "", "cat": "", "caterpillar": ""}
    no_human_station(s, "past")                                        # the bench empty, the sparrow on its back
    s.swap = {}
    place_free(s, "caterpillar", 0.1, "point", "surprise", face=s.way)  # the cast watch the empty cab go by
    if place_free(s, "professor", 0.05, "think", "smile", face=s.way) is None:
        place_free(s, "agent", 0.05, "point", "smile", face=s.way)


def check_more(s: Strip, beat: str) -> None:
    """"latch": the caterpillar fixes the cover's latch on the stop box, the agent watching; "test": the cover
    open, the professor presses the button to test it, the cat beside him."""
    w = s.way
    g = setting(s)
    foot = g.feet - 2
    gy = grip_y(s, "caterpillar" if beat == "latch" else "professor")
    sk = min((foot - gy) / 126, (g.feet - 8) / 172)
    c = Canvas()
    px = X(s, 0.55)
    sp = stop_post(c, px, foot, sk, w, open_=beat == "test")
    s.put(foot, c.render(), sp["box"], "stop", group="stop")
    if beat == "latch":
        hand_on(s, "caterpillar", (sp["box"][0] - 2 if w > 0 else sp["box"][2] + 2, sp["cover"][1]), "present", w,
                group="stop")
        place_free(s, "agent", 0.95, "think", "smile", face=-w)
    else:
        hand_on(s, "professor", (sp["box"][0] - 2 if w > 0 else sp["box"][2] + 2, sp["button"][1]), "point", w,
                group="stop")
        place_free(s, "cat", 0.95, "think", "worry", face=-w)


MORE = {"roles": roles_more, "plan": plan_more, "parallel": parallel_more, "to-pr": to_pr_more,
        "to-prod": to_prod_more, "metrics": metrics_more, "no-human": no_human_more, "check": check_more}
LATER = {"roles": ("signal", "card"), "plan": ("tick", "notice"), "parallel": ("branch", "lamp"),
         "to-pr": ("listen", "buffer"), "to-prod": ("leave", "lamp"), "metrics": ("wind", "notebook"),
         "no-human": ("wave", "knit"), "check": ("latch", "test")}


def both(key: str, first):
    """A station's draw: its first two moments, then the later ones."""
    def draw(s: Strip, beat: str) -> None:
        (MORE[key] if beat in LATER.get(key, ()) else first)(s, beat)
    return draw


# ============================================================================ the finale
BAYS = ("small", "roles", "plan", "parallel", "to-pr", "to-prod", "metrics", "no-human", "check")


FAR = 0.62                                                             # the far platform's things: that much smaller


def finale(s: Strip) -> None:
    """The whole station at once, the chapter's last panorama, seen from a little above, in two rows: on the near
    platform the caterpillar at her model railway, the professor signing the timetable, the agent throwing the
    points lever in the ballast, the cat's paw on the emergency-stop cover; beyond the tracks, smaller with the
    distance, the handcar on the far road, the coach bogie run out for the wheel tapper, the semaphore with its arm
    dropped, the platform clock, the bench with the sparrow on its back, all against the station's wall. Each name
    on a plaque right over its own thing; the building fills the rest up to its roof."""
    prepare(s, 0)
    if s.h < 300:                                                      # never a panorama: the first station
        _framed(small_station)(s, "telegram")
        return
    s.mirror, s.way = False, 1
    named = True
    feet0 = s.h * 0.87                                                 # the platform raised: little paving below
    s.feet = lambda x, nearer=0, feet=feet0: feet                      # noqa: ARG005
    s._room = None
    plate = 26.0 if named else 4.0
    for _ in range(8):                                                 # the camera: both rows fit, one above other
        s._room = None
        p_, a_ = height(s, "professor"), height(s, "agent")
        t_ = max(height(s, x) for x in ("professor", "agent", "cat", "caterpillar"))
        wd = {x: _box(s, x, 0, feet0)[2] - _box(s, x, 0, feet0)[0] for x in ("professor", "agent", "cat",
                                                                            "caterpillar")}
        row = (268 * 0.42 * p_ / 112 + wd["caterpillar"] + 200 * 1.3 * t_ / BOARD_H + wd["professor"]
               + 100 * 0.25 * p_ / 34 + wd["agent"] + 0.4 * p_ + wd["cat"] + 5 * 18)
        k_ = a_ * 2.5 / ENGINE_H * FAR
        cw = (_box(s, "cat", 0, feet0)[2] - _box(s, "cat", 0, feet0)[0]) * FAR
        frow = (168 * 0.95 * p_ / 110 + 160 * a_ * 2.5 / ENGINE_H + 110 * a_ * 2.5 / ENGINE_H + 112 * 1.25 * t_ / 178
                + 184 * 0.25 * p_ / 46) * FAR + cw + 840 * k_ + 7 * 14
        tall = 1.32 * t_ + plate + 0.3 * t_ + 322 * k_ + plate + 6    # near row, the tracks, the far row
        f = min((s.hi - s.lo) / max(row, frow), (feet0 - 4) / tall)
        if f >= 0.995:
            break
        s.tall *= f * 0.99
        s.unit = s.tall / 137
    s._room = None
    g = Line(s)
    t_ = g.t
    g.wall = g.feet - 1.32 * t_ - plate - 0.3 * t_                     # the far platform's foot, over the near row
    g.cope = g.wall + max(4.0, 0.05 * t_)
    far_rail = g.cope + max(10.0, 0.14 * t_)
    n_ = max(2, int((g.rail - far_rail) / max(14.0, 0.22 * t_)) + 1)
    g.rails = [g.rail + (far_rail - g.rail) * q / (n_ - 1) for q in range(n_)]
    if named:
        s.facade_t = max(t_ * 0.82, (g.wall - 0.06 * s.h) / 3.75)
    s.line = g
    s.steam = False
    backdrop_draw(s, g)
    p = height(s, "professor")
    k = rs_k(s)
    feet = g.feet
    wall = g.wall
    kf = k * FAR
    tops: dict[str, tuple[float, float]] = {}
    # the far row, spread across the frame
    cwf = (_box(s, "cat", 0, feet)[2] - _box(s, "cat", 0, feet)[0]) * FAR
    fw = {"small": 168 * 0.95 * p / 110 * FAR, "to-pr": 160 * kf + cwf, "train": 840 * kf, "to-prod": 110 * kf,
          "metrics": 112 * 1.25 * t_ / 178 * FAR, "no-human": 184 * 0.25 * p / 46 * FAR}
    forder = ("small", "to-pr", "to-prod", "metrics", "train", "no-human")   # the bench by the driverless train
    spare = (s.hi - s.lo - sum(fw.values())) / (len(forder) + 1)
    x = s.lo + spare
    fslot = {}
    for key in forder:
        fslot[key] = (x, x + fw[key])
        x += fw[key] + spare
    a, b = fslot["small"]
    c = Canvas()
    hk = 0.95 * p / 110 * FAR
    hc = handcar(c, a + 93 * hk, far_rail, hk, 1)
    beam(c, hc["pivot"], (hc["pivot"][0] + 50 * hk, hc["pivot"][1] - 20 * hk), hk)
    s.put(far_rail + 0.5, c.render(), hc["box"], "handcar", group="handcar")
    tops["small"] = ((hc["box"][0] + hc["box"][2]) / 2, hc["box"][1])
    a, b = fslot["to-pr"]                                              # the cat tapping the bogie's wheel
    c = Canvas()
    bg = bogie(c, b - 82 * kf, far_rail, kf)
    s.put(far_rail + 0.5, c.render(), bg["box"], "bogie", group="bogie")
    tall_c = tall_of(s, "cat") * FAR
    probe = Stage()
    gx0, gy0, _ = probe.grip(probe.actor("cat", 0.0, wall, "present", "smile", tall=tall_c), "right", "present")
    target = (bg["wheels"][0] - bg["r"] * 0.9, bg["hub"])
    reach = math.hypot(*TAPPER_TIP) * (_box(s, "cat", 0, feet)[3] - _box(s, "cat", 0, feet)[1]) * FAR / 100
    dx = math.sqrt(max(0.0, reach ** 2 - (target[1] - gy0) ** 2))
    tapper_cat = s.actor("cat", target[0] - dx - gx0, wall, "present", "smile", tall=tall_c, group="bogie")
    hold_reaching(s, tapper_cat, tapper, TAPPER_TIP, target)
    tops["to-pr"] = ((a + b) / 2, min(bg["box"][1], tapper_cat.top))
    a, b = fslot["train"]                                              # the train in at the platform
    c = Canvas()
    tr = train(c, b - 26 * kf, far_rail, kf, cars=1, steam=False, tender=False, cab=False)
    s.put(far_rail + 0.5, c.render(), tr["box"], "train", group="train")
    a, b = fslot["to-prod"]
    c = Canvas()
    sm = semaphore(c, a + 24 * kf, wall, kf, True, 1)
    s.put(wall + 0.5, c.render(), sm["box"], "signal", group="signal")
    tops["to-prod"] = (a + 24 * kf, sm["box"][1])
    a, b = fslot["metrics"]
    c = Canvas()
    ckf = 1.25 * t_ / 178 * FAR
    cp = clock_post(c, a + 16 * ckf, wall, ckf, 1)
    s.put(wall + 0.5, c.render(), cp["box"], "clock", group="clock")
    tops["metrics"] = (cp["clock"][0], cp["box"][1])
    a, b = fslot["no-human"]
    c = Canvas()
    bkf = 0.25 * p / 46 * FAR
    bn = bench(c, (a + b) / 2, wall, bkf)
    s.put(wall + 0.4, c.render(), bn["box"], "bench", group="bench")
    tops["no-human"] = ((a + b) / 2, bn["back"])
    # the near row
    mk = 0.42 * p / 112
    bk_ = 1.3 * t_ / BOARD_H
    lk = 0.25 * p / 34
    gyc = grip_at(s, "cat", 0.0, "present", 1)[1]
    sk = min((feet - 2 - gyc) / 126, (feet - 8) / 172) * 1.2
    wd = {x: _box(s, x, 0, feet)[2] - _box(s, x, 0, feet)[0] for x in ("professor", "agent", "cat", "caterpillar")}
    nw = {"roles": 268 * mk + wd["caterpillar"], "plan": 200 * bk_ + wd["professor"],
          "parallel": 100 * lk + wd["agent"], "check": 82 * sk}
    norder = ("roles", "plan", "parallel", "check")
    spare = (s.hi - s.lo - sum(nw.values())) / (len(norder) + 1)
    x = s.lo + spare
    slot = {}
    for key in norder:
        slot[key] = (x, x + nw[key])
        x += nw[key] + spare
    a, b = slot["roles"]
    cc = Canvas()
    ml = model_layout(cc, a + 134 * mk, feet - 2, mk, seed=4, way=1)
    s.put(feet - 2, cc.render(), ml["box"], "model", group="model")
    tops["roles"] = ((ml["box"][0] + ml["box"][2]) / 2, ml["box"][1])
    cat_ = stand(s, "caterpillar", ml["box"][2] + wd["caterpillar"] / 2 + 2, "present", "smile", face=-1,
                 group="model")
    s.hold(cat_, controller)
    pa_, pb_ = in_hand(s, cat_, *CONTROLLER_PORT), in_hand(s, cat_, CONTROLLER_PORT[0], CONTROLLER_PORT[1] + 1)
    pa = port(s, pa_[0], pa_[1], pb_[0] - pa_[0], pb_[1] - pa_[1], "caterpillar")
    pb = port(s, ml["terminal"][0], ml["terminal"][1] + 4 * mk, 0, 1, "model")
    cable(s, pb, pa, max(0.8, 2.2 * mk), feet)
    a, b = slot["plan"]
    bx = a + 100 * bk_
    st = Strip(s.h, 0, None, s.look)
    st.line = g
    probe = timetable(st, bx, feet, bk_, 3, False, False)
    x_ = reach_x(s, "professor", "present", -1, probe["sign"], hand_len(s, "professor", PEN_TIP))
    tt = timetable(s, bx, feet, bk_, 3, True, False)
    who = stand(s, "professor", x_, "present", "smile", face=-1, group="timetable")
    hold_reaching(s, who, pen, PEN_TIP, probe["sign"])
    tops["plan"] = (bx, tt["box"][1])
    a, b = slot["parallel"]
    foot, _, depth = lever_foot(s, g)
    gx0, gy0, _ = grip_at(s, "agent", 0.0, "present", -1)
    lx = a + 30 * lk
    pivot = (lx, foot - 34 * lk)
    tilt = math.asin(max(-0.2, min(0.8, (pivot[1] - gy0) / (74 * lk))))   # leaning along its quadrant
    handle = (pivot[0] + 74 * lk * math.cos(tilt), pivot[1] - 74 * lk * math.sin(tilt))
    who = stand(s, "agent", handle[0] - gx0, "present", "smile", face=-1, group="lever")
    gx, gy, _ = s.grip(who, "right")
    lc = Canvas()
    pl = point_lever(lc, lx, foot, lk, (gx, gy), 1, rod=46)
    s.put(depth, lc.render(), pl["box"], "lever", group="lever")
    tops["parallel"] = (lx, min(pl["box"][1], who.top))
    a, b = slot["check"]
    sc = Canvas()
    sp = stop_post(sc, b - 42 * sk, feet - 2, sk, 1)
    s.put(feet - 2, sc.render(), sp["box"], "stop", group="stop")
    bird_on(s, sp["box"][0] + 41 * sk, sp["box"][1], "stop")            # the sparrow on the box, after the button
    tops["check"] = (sp["box"][0] + 41 * sk, min(b_.top for b_ in s.boxes if b_.group == "stop"))
    if named:
        labels(s, tops)


def labels(s: Strip, tops: dict[str, tuple[float, float]]) -> None:
    """Each station's name on a plaque right over its own thing, a little above it; never on another plaque nor
    on a head - moved up just clear of whatever is under it."""
    size = 11.0
    th = tag_size("Ag", size)[1]
    pen_ = Pen(s, 0, 0, 1)
    placed: list[tuple[float, float, float, float]] = []
    others = [(b.left, b.top, b.right, b.bottom) for b in s.boxes if not b.name.startswith("label")]
    for key in sorted(tops, key=lambda q: -tops[q][1]):
        x0, top = tops[key]
        tw = tag_size(s.word(key), size)[0] + 10
        best = None
        for dx in (0, 12, -12, 24, -24, 36, -36, 50, -50, 66, -66):  # a nudge aside rather than a climb
            x = min(max(x0 + dx, tw / 2 + 4), W - tw / 2 - 4)
            y = top - 8 - th / 2
            moved = True
            while moved:
                moved = False
                box = (x - tw / 2, y - th / 2 - 3, x + tw / 2, y + th / 2 + 3)
                for o in [*placed, *others]:
                    if box[0] < o[2] + 10 and box[2] > o[0] - 10 and box[1] < o[3] + 4 and box[3] > o[1] - 4:
                        y = o[1] - 4 - th / 2 - 3
                        moved = True
            if best is None or y > best[1] + 2:
                best = (x, y)
        x, y = best
        placed.append((x - tw / 2, y - th / 2 - 3, x + tw / 2, y + th / 2 + 3))
        holder = pen_.tag(f"label{key}", x, y, s.word(key), size, mix(RUBY, P.CARD, 0.75), INK)
        s.put(s.h + 2, "", holder.outer, f"label{key}")
    s.put(s.h + 2, pen_.svg(), None)


RAILWAY.backdrop = prepare
RAILWAY.stations.extend([                                              # four moments each: no picture twice
    Station("small", _framed(small_station), ("telegram", "pump", "back", "pump+@caterpillar>professor")),
    Station("roles", _framed(both("roles", roles_station)), ("model", "real", "signal", "card")),
    Station("plan", _framed(both("plan", plan_station)), ("sign", "chalk", "tick", "notice")),
    Station("parallel", _framed(both("parallel", parallel_station)), ("set", "branch", "run", "lamp")),
    Station("to-pr", _framed(both("to-pr", to_pr_station)), ("tap", "couple", "listen", "buffer")),
    Station("to-prod", _framed(both("to-prod", to_prod_station)), ("depart", "board", "leave", "lamp")),
    Station("metrics", _framed(both("metrics", metrics_station)), ("watch", "wind", "check", "notebook")),
    Station("no-human", _framed(both("no-human", no_human_station)), ("past", "wave", "gone", "knit")),
    Station("check", _framed(both("check", check_station)), ("reach", "latch", "stopped", "test")),
])
RAILWAY.finale = finale
RAILWAY.alternate = True


def opener(st, accent: str):
    """The chapter's opener: the story `railway` (stories.py) as it is, handing over its containers and lines for
    the checks the worlds' openers pass."""
    ledger(st)
    drawn = stories.railway(st, accent)
    drawn.holders, drawn.links, drawn.ports = st.holders, st.links, st.ports
    return drawn


stories.OPENERS["railway_station"] = opener

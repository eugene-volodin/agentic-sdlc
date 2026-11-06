"""The space station: the world of chapter 3 (MCP).

One machine runs through the whole station: the *trunk*, a pneumatic tube that enters every module through its left
bulkhead and leaves through its right one, at the same height in every frame, so the pages join up into one line.
Capsules ride in it - the task in orange, the answers in the colour of the service that sent them (`CARGO`) - and
there are more of them the further the chapter goes. Each module is one node of it, one step of the chapter:

1. task      the professor has come in through the airlock with the task and posts it into the line through the
             inlet; at the outlet down the line the agent takes it out - or stands with the open task, puzzled,
             the line dark and empty;
2. tools     the tool rack hanging from the line: read_file, bash, edit - all an agent has without MCP - and spare
             hooks for what is to come;
3. mcp       the box with the MCP socket: the cat carries the connector to it on its cable from the reel - and then
             it is in, and the line comes alive;
4. services  the junction: a branch goes up from the line through the hull to the services in orbit - logs,
             tickets, base, metrics; the agent posts a capsule up it, and the answer comes back as a printout;
5. check     the scanner ring round the line: the caterpillar watches its screen and stops a capsule from the
             tickets with a planted letter in it;
6. panel     the valves on the branches: the agent shuts the ones it does not need, while the sparrow is after
             the big red button under its glass cap (he gets to press it only in the last chapter of the book).

A pulled-back frame shows the module's life outside the hull too, and the round windows in its end walls show the
neighbouring modules down the line.

It draws with the shared kit (`world_kit.py`) and keeps its two rules: containers and ports.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .. import design as P
from ..design import darken, lighten, mix
from . import handheld, props, sets, stories
from .characters import module as char_module
from .footers import Strip
from .ink import INK, Canvas, ellipse_d, lettering, lettering_width, n, rounded_rect_d, uid
from .openers import CLEAR_MM, H, W, Stage
from .scenes import PROFESSOR_HEIGHT
from .world_kit import (FLOPPY_K, GAP_MIN, GLASS, SIZE, Pen, Port, Room, burst, cast, clear_path,
                       connect, floppy_size, frac_of, hide, height_of, ledger, letter, motion, path_points, port, puff,
                       room, route, sound, stash, tag_size, wrap)
from .world_kitchen import _box, _upright, low, who
from .worlds import Station, world

SPACE = world("station", opener="station")

LAMPS = (P.ORANGE, P.YELLOW, P.TEAL, P.BLUE, P.PINK, P.GREEN)   # each module's color, left to right
CARGO = {"task": P.ORANGE, "logs": P.YELLOW, "tickets": P.PINK, "base": P.TEAL, "metrics": P.BLUE}
SERVICES = ("logs", "tickets", "base", "metrics")
SHUT = ("base", "metrics")     # the valves the agent shuts at the panel
BULKHEAD = 24        # a module's end frame at each edge of a frame
HULL_SKIN = 22       # the hull's cut edge over a module in a pulled-back frame
STATE = {"off": P.RED, "idle": P.AMBER, "on": P.GREEN}
GLASS_DEAD = mix(P.METAL_PALE, P.METAL_DARK, 0.35)
_at = props._at


class Hull(Room):
    """A module in a frame: the room, plus the height of the trunk line and the thickness of its tube."""

    def __init__(self, s: Strip) -> None:
        super().__init__(s)
        self.tube = max(10.0, 16 * self.k)
        self.trunk = max(self.top + self.tube * 0.9, self.floor - s.tall * 1.2)


def cabin(s: Strip) -> Hull:
    return room(s, Hull)


# ============================================================================ the camera
LOW_CAST = ("agent", "cat", "caterpillar")      # who stands in a low frame: the professor, the tallest, is left out


def camera(s: Strip) -> None:
    """The station's camera, close (the fair's, `world_fair.zoom`): the cast fills the frame's height under the
    trunk line, which runs over their heads in a tall frame and along the wall behind them in a low one (over their
    heads there, it left them three fifths of a strip), the deck a sixth under their feet; every other page the
    camera stands a step back."""
    from .world_fair import zoom
    zoom(s)
    s.again = (s.seed // 2) % 2 == 1
    feet = s.feet(0)
    names = LOW_CAST if low(s) else ("professor", *LOW_CAST)

    def tallest() -> float:
        return max(_box(s, name, 0, feet)[3] - _box(s, name, 0, feet)[1] for name in names)
    if low(s):
        s.tall *= (feet - 6) / tallest()
    widest = max(_box(s, name, 0, feet)[2] - _box(s, name, 0, feet)[0] for name in names)
    s.tall *= min(1.0, (s.hi - s.lo) * 0.19 / widest)     # two of them take two fifths of the width at most
    for _ in range(6):                                    # the trunk over every head, with air
        s.unit = s.tall / 137
        s._room = None
        r = cabin(s)
        # a close-up: the trunk runs along the wall behind their heads, the cast fills the frame
        clear = r.ceil + max(6.0, 8 * s.unit) if low(s) else r.trunk + r.tube * 0.75 + max(8.0, 10 * s.unit)
        head = feet - tallest()
        if head >= clear - 0.5:
            break
        s.tall *= (feet - clear) / (feet - head)
    if low(s) and s.shot:                                 # the other camera, a step back
        s.tall *= 0.88
    s.unit = s.tall / 137
    s._room = None


def stand(s: Strip, name: str, fracs: tuple[float, ...], pose: str, mood: str = "smile", face: float | None = None,
          mark: str | None = None, hold=None):
    """An onlooker on the deck at the first of `fracs` where it stands whole and clear of everything - failing
    those, at the nearest free spot along the deck - at the frame's one scale, facing the point `face`; None if the
    deck has no room for it."""
    feet = s.feet(0)
    first = [s.x(f) for f in fracs]
    sweep = sorted((s.lo + (s.hi - s.lo) * i / 40 for i in range(41)), key=lambda x: abs(x - first[0]))
    for x in (*first, *sweep):
        box = _box(s, name, x, feet)
        if box[0] >= BULKHEAD + 2 and box[2] <= W - BULKHEAD - 2 and box[1] >= 2 and s.free(box, 4) and \
                not any(box[0] - 2 < px < box[2] + 2 and box[1] - 2 < py < box[3] + 2
                        for link in getattr(s, "links", []) for px, py in link.points):
            target = W / 2 if face is None else face
            actor = s.actor(name, x, feet, pose, mood, flip=target < x, tall=s.tall * SIZE[name], group=name)
            if mark:
                k = min(1.3, max(0.6, s.tall / 160))
                mx, my = x + (actor.right - actor.left) * 0.55 * (1 if target < x else -1), actor.top + 18 * k
                s.put(feet + 1, props.mark(mx, my, mark, k), (mx - 17 * k, my - 17 * k, mx + 17 * k, my + 17 * k),
                      group=actor.group)
            if hold is not None:
                s.hold(actor, hold)
            return actor
    return None


def bird(s: Strip, x: float, top: float, group: str, pose: str = "stand", face: float | None = None):
    """The sparrow standing on a thing of the module (`group`) with its feet on `top` at x, as big as the room over
    it allows - under the trunk, never on anyone; or not at all."""
    r = cabin(s)
    for scale in (0.5, 0.42, 0.34, 0.28):
        box = _box(s, "sparrow", x, top - 3.5, scale)
        if box[1] > r.trunk + r.tube * 0.8 + 2 and all(not b.hits(box, 3) for b in s.boxes if b.group != group):
            target = W / 2 if face is None else face
            return s.actor("sparrow", x, top - 3.5, pose, "smile", flip=target < x,
                           tall=s.tall * SIZE["sparrow"] * scale, group=group)
    return None


# ============================================================================ the room and the trunk
def _space(c: Canvas, top: float, bottom: float, width: float, seed: int) -> None:
    if bottom - top < 8:
        return
    paint = c.gradient([(0, P.SPACE_DEEP), (1, P.SPACE_LOW)], 0, top, 0, bottom)
    c.add(f'<rect x="-4" y="{n(top)}" width="{n(width + 8)}" height="{n(bottom - top)}" fill="{paint}"/>')
    sets.stars(c, (10, top + 6, width - 10, bottom - 6), int(10 + (bottom - top) / 6), seed=seed)


def wall_of(index: int) -> str:
    return mix(P.HULL, LAMPS[index % len(LAMPS)], 0.1)


def backdrop(s: Strip, index: int) -> None:
    """The module's shell: space and the hull above it in a tall frame, the plain wall with its panel seams, the end
    bulkheads, the deck plating underfoot with the cable channel of the line along its back. Nothing on the wall
    but what the station's step needs."""
    ledger(s)
    camera(s)
    c, r = s.back, cabin(s)
    lamp = LAMPS[index % len(LAMPS)]
    wall = wall_of(index)
    if r.ceil > 0:
        _space(c, 0, r.ceil - HULL_SKIN, W, seed=31 + index)
        c.shape(f"M-4,{n(r.ceil - HULL_SKIN)} H{W + 4} V{n(r.ceil)} H-4 Z", P.METAL, sw=2.2, light=(0, -3),
                shade_k=0.85)
        c.add(f'<rect x="-4" y="{n(r.ceil - HULL_SKIN * 0.62)}" width="{W + 8}" height="{n(HULL_SKIN * 0.24)}" '
              f'fill="{lamp}"/>')
        c.line(" ".join(f"M{x},{n(r.ceil)} l8,-6" for x in range(0, W, 14)), 1, INK, 0.35)
    c.add(f'<rect x="0" y="{n(r.ceil)}" width="{W}" height="{n(r.wall)}" fill="{wall}"/>')
    low = r.floor - r.wall * 0.2
    c.add(f'<rect x="0" y="{n(low)}" width="{W}" height="{n(r.floor - low)}" fill="{darken(wall, 0.93)}"/>')
    c.line(f"M0,{n(low)} H{W}", 1.6 * r.u)
    step = 140
    for x in range(int((index * 57) % step), W, step):
        c.line(f"M{x},{n(r.top)} V{n(r.floor)}", 1.2, INK, 0.35)
        for y in (r.top + 8 * r.u, r.floor - 6 * r.u):
            c.dot(x - 6, y, 1.5 * r.u, P.METAL_DARK)
            c.dot(x + 6, y, 1.5 * r.u, P.METAL_DARK)
    c.add(f'<rect x="0" y="{n(r.ceil)}" width="{W}" height="{n(8 * r.u)}" fill="{P.METAL_DARK}"/>')
    c.add(f'<rect x="0" y="{n(r.ceil + 8 * r.u)}" width="{W}" height="{n(4 * r.u)}" fill="{lighten(lamp, 0.35)}"/>')
    for x0 in (0, W - BULKHEAD):
        c.shape(f"M{x0},{n(r.ceil)} H{x0 + BULKHEAD} V{n(r.floor)} H{x0} Z", P.METAL, sw=2, light=(-2, 0),
                shade_k=0.84)
        for y in range(int(r.top + 14), int(r.floor - 6), 26):
            c.dot(x0 + 5, y, 1.4, P.METAL_DARK)
            c.dot(x0 + BULKHEAD - 5, y, 1.4, P.METAL_DARK)
    deck = mix(P.METAL, lamp, 0.06)
    c.add(f'<rect x="-4" y="{n(r.floor)}" width="{W + 8}" height="{n(s.h - r.floor + 4)}" fill="{deck}"/>')
    c.add(f'<rect x="-4" y="{n(r.floor)}" width="{W + 8}" height="{n(4 * r.u)}" fill="{P.METAL_DARK}"/>')
    for x in range(-200, W + 240, 70):
        c.line(f"M{n(W / 2 + (x - W / 2) * 0.5)},{n(r.floor + 4 * r.u)} L{x},{n(s.h + 4)}", 1, INK, 0.28)
    for t in (0.35, 0.72):
        c.line(f"M-4,{n(r.floor + (s.h - r.floor) * t)} H{W + 4}", 1, INK, 0.28)
    # the cable channel along the back of the deck: the line's power and signal run under its slotted cover
    cy, ch = r.floor + 4 * r.u, 6 * r.u
    c.add(f'<rect x="-4" y="{n(cy)}" width="{W + 8}" height="{n(ch)}" fill="{P.METAL_LIGHT}" stroke="{INK}" '
          f'stroke-width="1.2"/>')
    c.line(" ".join(f"M{x},{n(cy + ch * 0.3)} h10 M{x},{n(cy + ch * 0.7)} h10" for x in range(8, W, 22)), 1.1,
           P.METAL_DARK)


def progress(index: int, beat: str) -> int:
    """How many capsules ride the line at this step: more and more as the chapter goes on."""
    return min(5, index + SPACE.stations[index].beats.index(beat))


class Trunk:
    """The trunk line across a module: a glass tube at the fixed height, through a collar in each bulkhead, with
    ring joints and flow chevrons; `taps` are tees where a node hangs from the line, each with a port downward (and
    `up` ones upward) for `connect`. The left bulkhead's gauge and both fittings show the line's state. `riders` are
    capsules placed by the story; `load` more ride where the line is free, in the colours of `cargo`."""

    def __init__(self, s: Strip, state: str, taps: tuple[float, ...] = (), up: tuple[float, ...] = (),
                 riders: tuple[tuple[float, str, int], ...] = (), load: int = 0,
                 cargo: tuple[str, ...] = ("task",), keep: tuple[float, ...] = ()) -> None:
        r = cabin(s)
        self.r, self.state, self.s = r, state, s
        y, t = r.trunk, r.tube
        glass = GLASS if state != "off" else GLASS_DEAD
        c = Canvas()
        c.add(f'<rect x="-8" y="{n(y - t / 2)}" width="{W + 16}" height="{n(t)}" fill="{glass}" stroke="{INK}" '
              f'stroke-width="2"/>')
        c.line(f"M-6,{n(y - t * 0.22)} H{W + 6}", max(1.2, t * 0.14), P.WHITE, 0.7)
        x = 46.0
        while x < W - 20:
            if all(abs(x - tap) > t * 1.6 for tap in (*taps, *up)):
                c.add(f'<rect x="{n(x - 3)}" y="{n(y - t * 0.66)}" width="6" height="{n(t * 1.32)}" rx="1.5" '
                      f'fill="{P.METAL}" stroke="{INK}" stroke-width="1.2"/>')
            if state == "on" and all(abs(x + 30 - tap) > t * 1.6 for tap in (*taps, *up)):
                cx = x + 30
                c.line(f"M{n(cx - 3)},{n(y - t * 0.22)} L{n(cx + 3)},{n(y)} L{n(cx - 3)},{n(y + t * 0.22)}", 1.6,
                       darken(P.TEAL, 0.8), 0.8)
            x += 92
        for tap in (*taps, *up):                              # a tee: a fat collar round the line
            c.add(f'<rect x="{n(tap - t * 0.9)}" y="{n(y - t * 0.75)}" width="{n(t * 1.8)}" height="{n(t * 1.5)}" '
                  f'rx="3" fill="{P.METAL}" stroke="{INK}" stroke-width="1.6"/>')
        for x0 in (0, W - BULKHEAD):                          # the fittings in the bulkheads show the line's state
            c.add(f'<rect x="{x0 - 2}" y="{n(y - t * 0.85)}" width="{BULKHEAD + 4}" height="{n(t * 1.7)}" rx="3" '
                  f'fill="{mix(P.METAL_DARK, STATE[state], 0.55)}" stroke="{INK}" stroke-width="1.6"/>')
        s.put(1.0, c.render(), None)
        self._gauge()
        ride = list(riders)
        if state != "off":
            busy = [*taps, *up, *keep, *(x for x, _, _ in riders)]
            ride += [(x, CARGO[cargo[(i + s.seed) % len(cargo)]], 1 if state == "on" else 0)
                     for i, x in enumerate(self._free_spots(load, busy))]
        self.riders = ride
        s.trunk = self
        for x, color, way in ride:
            s.put(1.2, capsule(x, y, t / 15, color) + (motion(x, y, 30, t / 15, way) if way else ""), None)

    def _free_spots(self, count: int, busy: list[float]) -> list[float]:
        """Up to `count` places along the line for capsules: spread out, a little off even, clear of the tees,
        of the story's own capsules and of each other (a capsule and its speed lines need about four tubes)."""
        t = self.r.tube
        lo, hi = BULKHEAD + 5 * t, W - BULKHEAD - 2 * t
        rnd = random.Random(self.s.seed * 31 + count)
        out: list[float] = []
        slot = (hi - lo) / max(1, count)
        for i in range(count):
            start = lo + slot * (i + 0.5) + rnd.uniform(-0.2, 0.2) * slot
            for shift in (0, 0.25, -0.25, 0.45, -0.45):
                x = start + shift * slot
                if lo <= x <= hi and all(abs(x - b) > 4.4 * t for b in (*busy, *out)):
                    out.append(x)
                    break
        return out

    def _gauge(self) -> None:
        """A flow gauge on the left bulkhead over the line: the needle on red when the line is dead, upright when
        it idles, on green when it runs."""
        r, s = self.r, self.s
        g = min(9.0, BULKHEAD / 2 - 2)
        gx = BULKHEAD / 2
        gy = r.trunk - r.tube * 0.85 - g - 4
        if gy - g < r.ceil + 12 * r.u + 2:
            gy = r.trunk + r.tube * 0.85 + g + 4
        c = Canvas()
        c.add(f'<circle cx="{n(gx)}" cy="{n(gy)}" r="{n(g)}" fill="{P.WHITE}" stroke="{INK}" stroke-width="1.6"/>')
        for a0, a1, color in ((-140, -100, P.RED), (-80, -40, P.GREEN)):
            p0 = (gx + math.cos(math.radians(a0)) * g * 0.7, gy + math.sin(math.radians(a0)) * g * 0.7)
            p1 = (gx + math.cos(math.radians(a1)) * g * 0.7, gy + math.sin(math.radians(a1)) * g * 0.7)
            c.add(f'<path d="M{n(p0[0])},{n(p0[1])} A{n(g * 0.7)},{n(g * 0.7)} 0 0 1 {n(p1[0])},{n(p1[1])}" '
                  f'fill="none" stroke="{color}" stroke-width="2.2"/>')
        a = math.radians({"off": -125, "idle": -90, "on": -55}[self.state])
        c.line(f"M{n(gx)},{n(gy)} L{n(gx + math.cos(a) * g * 0.8)},{n(gy + math.sin(a) * g * 0.8)}", 1.6)
        c.dot(gx, gy, 1.8, INK)
        s.put(1.05, c.render(), (gx - g - 1, gy - g - 1, gx + g + 1, gy + g + 1), "gauge", group="trunk")

    def down(self, x: float) -> Port:
        return port(self.s, x, self.r.trunk + self.r.tube * 0.75, 0, 1, "trunk")

    def upward(self, x: float) -> Port:
        return port(self.s, x, self.r.trunk - self.r.tube * 0.75, 0, -1, "trunk")


def hatch(s: Strip, r: Hull, index: int, side: int) -> None:
    """A round window in the wall by an end bulkhead, between the ceiling and the line: through it, the next module
    down the line that way - its wall, its stretch of the trunk and its node, small with distance; beyond the
    first and the last module, space."""
    band_top, band_bottom = r.ceil + 12 * r.u + 6, r.trunk - r.tube * 0.9 - 6
    rad = min(48.0, (band_bottom - band_top) * 0.42)
    if rad < 20:
        return
    ring = rad * 0.18
    cx = BULKHEAD + 10 + rad + ring if side < 0 else W - BULKHEAD - 10 - rad - ring
    cy = (band_top + band_bottom) / 2
    box = (cx - rad - ring, cy - rad - ring, cx + rad + ring, cy + rad + ring)
    if not s.free(box, 6):
        return
    j = index + side
    c = Canvas()
    clip = uid("hatch")
    c.add(f'<clipPath id="{clip}"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(rad)}"/></clipPath>')
    inside = Canvas()
    if 0 <= j < len(SPACE.stations):
        inside.add(f'<rect x="{n(cx - rad)}" y="{n(cy - rad)}" width="{n(2 * rad)}" height="{n(2 * rad)}" '
                   f'fill="{darken(wall_of(j), 0.96)}"/>')
        fy = cy + rad * 0.55                                  # its deck
        inside.add(f'<rect x="{n(cx - rad)}" y="{n(fy)}" width="{n(2 * rad)}" height="{n(rad)}" '
                   f'fill="{mix(P.METAL, LAMPS[j], 0.06)}" stroke="{INK}" stroke-width="1"/>')
        ty, tt = cy - rad * 0.45, rad * 0.16                  # its stretch of the line, at the same height
        inside.add(f'<rect x="{n(cx - rad - 2)}" y="{n(ty - tt / 2)}" width="{n(2 * rad + 4)}" height="{n(tt)}" '
                   f'fill="{GLASS}" stroke="{INK}" stroke-width="1"/>')
        inside.add(_node_icon(j, cx, ty + tt / 2, fy, rad / 30))
    else:
        inside.add(f'<rect x="{n(cx - rad)}" y="{n(cy - rad)}" width="{n(2 * rad)}" height="{n(2 * rad)}" '
                   f'fill="{P.SPACE_DEEP}"/>')
        sets.stars(inside, (cx - rad, cy - rad, cx + rad, cy + rad), 6, seed=index * 7 + side)
        if j >= len(SPACE.stations):
            inside.add(earth(cx + rad * 0.7, cy + rad * 0.75, rad * 0.7))
    c.add(f'<g clip-path="url(#{clip})">{inside.render()}</g>')
    c.add(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(rad + ring / 2)}" fill="none" stroke="{INK}" '
          f'stroke-width="{n(ring + 3)}"/><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(rad + ring / 2)}" fill="none" '
          f'stroke="{P.METAL}" stroke-width="{n(ring)}"/>')
    for i in range(6):
        a = math.tau * i / 6 + 0.3
        c.dot(cx + math.cos(a) * (rad + ring / 2), cy + math.sin(a) * (rad + ring / 2), 1.5, P.METAL_DARK)
    c.line(f"M{n(cx - rad * 0.6)},{n(cy - rad * 0.35)} A{n(rad * 0.7)},{n(rad * 0.7)} 0 0 1 "
           f"{n(cx - rad * 0.1)},{n(cy - rad * 0.68)}", 2, P.WHITE, 0.7)
    s.put(1.1, c.render(), box, f"hatch{side}", group=f"hatch{side}")


def _node_icon(j: int, x: float, hang: float, floor: float, k: float) -> str:
    """Module `j`'s node as seen far off through a window: hung from its line at `hang` or standing on its deck."""
    c = Canvas()
    if j == 0:                                    # the post boxes
        for dx in (-12, 12):
            c.line(f"M{n(x + dx * k)},{n(hang)} V{n(hang + 6 * k)}", 1.4, P.METAL_DARK)
            c.shape(rounded_rect_d(x + (dx - 6) * k, hang + 6 * k, 12 * k, 14 * k, 2 * k), P.METAL, sw=1, light=None)
            c.add(f'<rect x="{n(x + (dx - 1.5) * k)}" y="{n(hang + 9 * k)}" width="{n(3 * k)}" height="{n(6 * k)}" '
                  f'fill="{P.CHARCOAL}"/>')
    elif j == 1:                                  # the tool rack
        c.line(f"M{n(x - 12 * k)},{n(hang)} V{n(hang + 5 * k)} M{n(x + 12 * k)},{n(hang)} V{n(hang + 5 * k)}", 1.4,
               P.METAL_DARK)
        c.shape(rounded_rect_d(x - 18 * k, hang + 5 * k, 36 * k, 18 * k, 2 * k), P.BEIGE, sw=1, light=None)
        for dx, color in ((-10, P.LENS), (0, P.TERMINAL), (10, P.YELLOW)):
            c.add(f'<rect x="{n(x + (dx - 3) * k)}" y="{n(hang + 9 * k)}" width="{n(6 * k)}" height="{n(8 * k)}" '
                  f'fill="{color}" stroke="{INK}" stroke-width=".6"/>')
    elif j == 2:                                  # the MCP box
        c.line(f"M{n(x)},{n(hang)} V{n(hang + 6 * k)}", 1.4, P.METAL_DARK)
        c.shape(rounded_rect_d(x - 8 * k, hang + 6 * k, 16 * k, 20 * k, 2 * k), P.METAL, sw=1, light=None)
        c.add(f'<rect x="{n(x - 4 * k)}" y="{n(hang + 12 * k)}" width="{n(8 * k)}" height="{n(8 * k)}" '
              f'fill="{P.CHARCOAL}"/>')
    elif j == 3:                                  # the branch up through the roof
        c.add(f'<rect x="{n(x - 3 * k)}" y="{n(hang - 60 * k)}" width="{n(6 * k)}" height="{n(60 * k)}" '
              f'fill="{GLASS}" stroke="{INK}" stroke-width=".8"/>')
    elif j == 4:                                  # the scanner ring round the line
        y = hang - 2.4 * k
        c.add(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(6 * k)}" ry="{n(12 * k)}" fill="none" stroke="{INK}" '
              f'stroke-width="{n(4 * k + 1.6)}"/><ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(6 * k)}" ry="{n(12 * k)}" '
              f'fill="none" stroke="{P.METAL_LIGHT}" stroke-width="{n(4 * k)}"/>')
        c.line(f"M{n(x - 4 * k)},{n(y + 10 * k)} V{n(floor)} M{n(x + 4 * k)},{n(y + 10 * k)} V{n(floor)}", 1.4,
               P.METAL_DARK)
    else:                                         # the valves
        for i, key in enumerate(SERVICES):
            vx = x + (i - 1.5) * 10 * k
            c.line(f"M{n(vx)},{n(hang)} V{n(hang + 10 * k)}", 1.2, P.METAL_DARK)
            c.add(f'<circle cx="{n(vx)}" cy="{n(hang + 13 * k)}" r="{n(3.4 * k)}" fill="none" '
                  f'stroke="{P.RED if key in SHUT else P.GREEN}" stroke-width="{n(1.8 * k)}"/>')
    return c.render()


def finish(s: Strip, index: int, beat: str, at: float) -> None:
    """What every frame ends with: the module's life outside the hull over `at` and the windows to its neighbours
    where the wall is still free. No name plate: every thing in the frame says what it is by itself;
    only the finale names the stations."""
    r = cabin(s)
    outside(s, r, index, beat, at)
    for side in (-1, 1):
        hatch(s, r, index, side)


# ============================================================================ things
def capsule(x: float, y: float, k: float, color: str = P.ORANGE, turn: float = 0, label: str = "",
            cut: float | None = None, glass: str = "") -> str:
    """A pneumatic-post capsule lying along x: a metal tube with colored caps, 34 long and 14 thick at k = 1; a
    `label` is written on its side. `cut` (in its own units, along x) hides what is past that point - the part
    already inside a slot. `glass` makes it transparent, showing what it carries: "letter" (the task) or "planted"
    (an envelope sealed with red wax, a note sticking out of it)."""
    c = Canvas()
    body = P.METAL_LIGHT if not glass else GLASS
    c.shape(rounded_rect_d(-17, -7, 34, 14, 6), body, sw=1.7, light=(-1, -2) if not glass else None, shade_k=0.8,
            highlight="M-12,-3.5 H10")
    if glass == "planted":
        c.shape("M-9,-4.5 H7 V4.5 H-9 Z", P.WHITE, sw=1, light=None)                     # the envelope
        c.line("M-9,-4.5 L-1,1 L7,-4.5", 0.9)
        c.add(f'<circle cx="-1" cy="1.5" r="2.4" fill="{P.RED}" stroke="{INK}" stroke-width=".8"/>')   # its seal
        c.shape("M2,-5 L5,-13 L11,-11 L8,-4 Z", P.PINK_PALE, sw=1, light=None)           # the note poking out
        c.line("M5.5,-10 l3.5,1", 0.8, P.RED)
    elif glass == "letter":
        c.shape("M-9,-4 H7 V4 H-9 Z", P.CARD, sw=1, light=None)
        c.line("M-6,-1.5 H4 M-6,1.5 H2", 0.8, INK, 0.6)
    for cap in (-17, 11):
        c.shape(rounded_rect_d(cap, -7.5, 6, 15, 3), color, sw=1.5, light=None)
    if label:                                   # between the caps, or in what still shows of a capsule half in
        left, right = -11, 11 if cut is None else min(11, cut - 1)
        if lettering_width(label, 7, "plain") * 0.6 <= right - left:
            c.add(lettering((left + right) / 2, 3, label, 7, INK, style="plain", room=right - left))
    body_svg = c.render()
    if cut is not None:
        clip = uid("cut")
        body_svg = (f'<clipPath id="{clip}"><rect x="-30" y="-30" width="{n(cut + 30)}" height="60"/></clipPath>'
                    f'<g clip-path="url(#{clip})">{body_svg}</g>')
    rot = f' transform="rotate({n(turn)})"' if turn else ""
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})"><g{rot}>{body_svg}</g></g>'


# ============================================================================ the nodes
# The post terminal: where a capsule goes into the line, and where answers come out - a pneumatic-post station. A
# glass tube as wide as a capsule comes down from a tee of the trunk, bends and ends at hand height in an open mouth
# with a ring and a hinged hatch lid swung up; the capsule going in is seen through the glass. Under the tube, a
# plate on the wall with an arrow - the way the post goes - and the word.
POST_BEND = 7.5          # the tube's run from its tee down, and along to its mouth, in its widths: room to bend
                         # round wide, as a real glass tube does - three times its width


def post_bore(ck: float) -> float:
    """The tube's width on the page for a capsule drawn at scale `ck`: the capsule slides into it."""
    return 14 * ck + 3


def post_scale(s: Strip, y: float, k: float) -> float:
    """The capsule's scale for a terminal with its mouth at height y: the readable size, or smaller where the
    wall under the trunk is too low for a tube that wide to bend round."""
    r = cabin(s)
    drop = y - (r.trunk + r.tube * 0.75)
    return max(0.1, min(1.15 * k, (drop / POST_BEND - 3) / 14))


def post_center(x: float, ck: float, side: int = -1) -> float:
    """Where the tee of a post terminal goes, its mouth at x facing `side` (-1 left, 1 right)."""
    return x - side * post_bore(ck) * POST_BEND


def post_box(s: Strip, x: float, y: float, k: float, tee: Port, word: str, group: str, lit: bool = True,
             side: int = -1, way: int = 1, ck: float | None = None) -> None:
    """A post terminal, its mouth at (x, y) facing `side` (-1 left, 1 right): the glass tube from `tee` coming
    down and round to the mouth, the hatch lid open over it, the plate under it; `way` 1 - post goes in (the arrow
    points into the tube), -1 - it comes out. `lit`: the line is on."""
    f = -side                                              # the tube runs from the mouth this way to its tee
    bore = post_bore(ck if ck is not None else 1.15 * k)
    mouth = port(s, x, y, f, 0, group)
    connect(s, tee, mouth, "tube", bore, depth=1.6, color=GLASS if lit else GLASS_DEAD,
            lead=(max(4.0, y - tee.y), abs(tee.x - x)))         # one corner, right over the tee
    c = Canvas()                                           # the open end and its hatch lid, hinged at the top
    r = bore / 2 + 2
    c.add(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(r * 0.32)}" ry="{n(r)}" fill="{P.CHARCOAL}" stroke="{INK}" '
          f'stroke-width="1.8"/>')
    hx, hy = x - f * 1.5 * k, y - r                        # the hinge, on top of the mouth's ring
    lid_t = max(3.0, 4.5 * k)                              # the lid seen edge on: a disc as thick as a coin
    c.add(f'<g transform="rotate({n(f * 120)} {n(hx)} {n(hy)})"><rect x="{n(hx - lid_t)}" y="{n(hy)}" '
          f'width="{n(lid_t)}" height="{n(2 * r)}" rx="{n(lid_t / 2)}" fill="{P.METAL}" stroke="{INK}" '
          f'stroke-width="1.5"/><rect x="{n(hx - lid_t - 3 * k)}" y="{n(hy + 2 * r - 6 * k)}" width="{n(3 * k)}" '
          f'height="{n(5 * k)}" rx="1" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1"/></g>')
    c.add(f'<circle cx="{n(hx)}" cy="{n(hy)}" r="{n(2.6 * k)}" fill="{P.METAL_DARK}" stroke="{INK}" '
          f'stroke-width="1"/>')                                                # the hinge
    lid = (x - r * 2.1, y - r * 2.3, x + r * 1.1, y + r) if f > 0 else (x - r * 1.1, y - r * 2.3, x + r * 2.1, y + r)
    s.put(1.75, c.render(), lid, f"hatch_{group}", group=group)
    size = letter(k, 10.0)                                 # the plate under the tube: an arrow and the word
    tag_w, tag_h = tag_size(word, size, k)
    gap = GAP_MIN / k + 3
    arrow = 18.0
    pw, ph = wrap(arrow + gap + tag_w, k), wrap(max(tag_h, 14.0), k)
    px = x + f * (pw / 2 + 6) * k
    pen = Pen(s, px, y + bore / 2 + 8 * k + ph * k / 2, k)
    plate_ = pen.container(f"sign_{group}", -pw / 2, -ph / 2, pw, ph, P.METAL_PALE, radius=4, light=None)
    ax0 = -(arrow + gap + tag_w) / 2
    toward = f if way > 0 else -f                           # the way the post travels
    a0, a1 = (ax0 + arrow, ax0) if toward < 0 else (ax0, ax0 + arrow)
    d = 1 if a1 > a0 else -1
    pen.c.add(f'<path d="M{n(a0)},-2.5 H{n(a1 - d * 7)} V-7 L{n(a1)},0 L{n(a1 - d * 7)},7 V2.5 H{n(a0)} Z" '
              f'fill="{P.GREEN if lit else P.METAL_DARK}" stroke="{INK}" stroke-width="1.3"/>')
    pen.child(plate_, "arrow", ax0, -7, ax0 + arrow, 7)
    pen.tag(f"tag_{group}", ax0 + arrow + gap + tag_w / 2, 0, word, size, inside=plate_)
    s.put(2, pen.svg(), pen.box(-pw / 2, -ph / 2, pw / 2, ph / 2), f"sign_{group}", group=group)


def seen_inside(svg: str, x: float, f: int, y: float, reach: float) -> str:
    """The part of a drawing past x (on the side `f`) as seen through the glass of a tube: faint, clipped."""
    clip = uid("glass")
    left = x if f > 0 else x - reach
    return (f'<clipPath id="{clip}"><rect x="{n(left)}" y="{n(y - reach)}" width="{n(reach)}" '
            f'height="{n(2 * reach)}"/></clipPath><g clip-path="url(#{clip})" opacity=".55">{svg}</g>')


def printer_box(s: Strip, x: float, y: float, k: float, tee: Port, word: str, group: str,
                toward: int = 1) -> Port:
    """The post's printer: a cabinet on the wall, its middle at (x, y), the glass tube from `tee` coming into its
    top, its word on its front, the slit in its side `toward` the reader of the answer. Returns the slit's port."""
    size = letter(k, 10.0)
    tag_w, tag_h = tag_size(word, size, k)
    gap = GAP_MIN / k + 3
    w = wrap(max(tag_w, 44.0), k)
    h = wrap(tag_h + gap + 18, k)
    pen = Pen(s, x, y, k)
    body = pen.container(f"printer_{group}", -w / 2, -h / 2, w, h, P.METAL, radius=6)
    pad = pen.pad(w, h)
    pen.tag(f"tag_{group}", 0, -h / 2 + pad + tag_h / 2, word, size, inside=body)
    ly = h / 2 - pad - 9                                    # a row of vents on its front
    pen.c.line(" ".join(f"M{n(-w / 2 + pad + 4 + i * 6)},{n(ly - 5)} v10" for i in range(int((w - 2 * pad - 8) / 6))),
               1.6, P.METAL_DARK)
    pen.child(body, "vents", -w / 2 + pad + 2, ly - 6, w / 2 - pad - 2, ly + 6)
    sx = toward * w / 2
    pen.c.add(f'<rect x="{n(sx - 2.5)}" y="{n(ly - 8)}" width="5" height="16" rx="1.5" fill="{P.CHARCOAL}" '
              f'stroke="{INK}" stroke-width="1.2"/>')
    s.put(2, pen.svg(), pen.box(-w / 2, -h / 2, w / 2, h / 2), f"printer_{group}", group=group)
    connect(s, tee, pen.port(0, -h / 2, 0, -1, group), "tube", post_bore(1.15 * k), depth=1.6)
    return pen.port(sx + toward * 2, ly, toward, 0, group)


# The airlock: the round door in the wall through which people and post come aboard from the docked shuttle - a
# frame bolted to the wall, a heavy door with a wheel and a small window, its name on a tag over it.
def airlock(s: Strip, x: float, floor: float, k: float) -> None:
    """The airlock, the middle of its foot at (x, floor): a frame bolted to the wall, a door with rounded corners
    in it - a small window high up, the locking wheel below it, air between them and to the door's edge. No name
    tag: the door reads as a door by itself."""
    pen = Pen(s, x, floor, k)
    frame_ = pen.container("airlock_frame", -60, -170, 120, 170, P.METAL, radius=24, shade_k=0.84)
    pad = pen.pad(120, 170)
    dl, dt, dr, db = -60 + pad, -170 + pad, 60 - pad, -pad
    door = pen.container("airlock_door", dl, dt, dr - dl, db - dt, P.METAL_LIGHT, radius=18, light=(-2, -2))
    frame_.children.append(("door", door.outer))
    dpad = pen.pad(dr - dl, db - dt)
    wr = 13.0                                               # the window
    wy = dt + dpad + 3 + wr
    pen.c.add(f'<circle cx="0" cy="{n(wy)}" r="{n(wr)}" fill="{P.SCREEN}" stroke="{INK}" stroke-width="2"/>')
    pen.c.line(f"M-6,{n(wy - 5)} A7,7 0 0 1 2,{n(wy - 9)}", 1.6, P.WHITE, 0.8)
    pen.child(door, "window", -wr - 1, wy - wr - 1, wr + 1, wy + wr + 1)
    hr = 20.0                                               # the wheel, well below the window
    hy = db - dpad - 10 - hr
    pen.c.add(f'<circle cx="0" cy="{n(hy)}" r="{n(hr)}" fill="none" stroke="{INK}" stroke-width="7"/>'
              f'<circle cx="0" cy="{n(hy)}" r="{n(hr)}" fill="none" stroke="{P.RED}" stroke-width="4"/>')
    pen.c.line(f"M{n(-hr)},{n(hy)} H{n(hr)} M0,{n(hy - hr)} V{n(hy + hr)}", 3, INK)
    pen.c.dot(0, hy, 4.5, P.METAL_DARK)
    pen.child(door, "wheel", -hr - 3.5, hy - hr - 3.5, hr + 3.5, hy + hr + 3.5)
    s.put(1.5, pen.svg(), pen.box(-60, -170, 60, 0), "airlock", group="airlock")   # no name tag: it is a door


# The main switch of the line, a real knife switch: a grey steel cabinet screwed to the wall, its door swung open on
# its hinges with a yellow warning plate and a lightning bolt on it; inside, on a ceramic base, two copper blades on
# their hinge clips at the bottom, joined at the top by an insulated crossbar with a big black handle - up in their
# jaws for on, swung out of them for off; small plates for on and off by the jaws and under the hinges; its cable
# goes up out of a gland in the cabinet's top into a tee of the trunk.
COPPER = mix(P.ORANGE, P.WOOD_DARK, 0.35)
CERAMIC = mix(P.CARD, P.WHITE, 0.5)


def switch_size(s: Strip, k: float) -> tuple[float, float, float, float]:
    """The cabinet's width and height in its own units, its lettering size and plate height."""
    size = letter(k, 8.0)
    tw = max(tag_size(s.word(key), size, k, "plain")[0] for key in ("on", "off"))
    th = tag_size("Ag", size, k, "plain")[1]
    gap = GAP_MIN / k + 6
    return wrap(max(tw + 8, 40.0), k), wrap(th * 2 + gap * 2 + 34, k), size, th


def _door(w: float) -> float:
    """How far the open door reaches out to the left of the cabinet."""
    return w * 0.42


def wall_switch(s: Strip, x: float, y: float, k: float, on: bool, tee: Port) -> None:
    """The knife switch, its cabinet's middle at (x, y); `on` - the blades up in their jaws."""
    w, h, size, th = switch_size(s, k)
    pen = Pen(s, x, y, k)
    dw = _door(w)
    pen.c.shape(f"M{n(-w / 2)},{n(-h / 2)} L{n(-w / 2 - dw)},{n(-h / 2 + 8)} V{n(h / 2 - 8)} L{n(-w / 2)},{n(h / 2)} Z",
                darken(P.METAL, 0.9), sw=1.6, light=None)                  # the door, swung open on its hinges
    for hy in (-h / 2 + 10, h / 2 - 10):
        pen.c.add(f'<rect x="{n(-w / 2 - 2)}" y="{n(hy - 4)}" width="4" height="8" rx="1" fill="{P.METAL_DARK}" '
                  f'stroke="{INK}" stroke-width=".8"/>')
    wy = -8.0                                                               # its warning plate, a lightning bolt
    wx = -w / 2 - dw * 0.5
    pen.c.add(f'<path d="M{n(wx)},{n(wy - 9)} L{n(wx + 8)},{n(wy + 6)} H{n(wx - 8)} Z" fill="{P.YELLOW}" '
              f'stroke="{INK}" stroke-width="1.2" stroke-linejoin="round"/><path d="M{n(wx + 1)},{n(wy - 4)} '
              f'L{n(wx - 2)},{n(wy + 1)} H{n(wx + 1)} L{n(wx - 1)},{n(wy + 5)} L{n(wx + 3)},{n(wy - 1)} '
              f'H{n(wx)} Z" fill="{INK}"/>')
    body = pen.container("switch", -w / 2, -h / 2, w, h, P.METAL, radius=4, shade_k=0.84)
    pad = pen.pad(w, h)
    on_y, off_y = -h / 2 + pad + th / 2, h / 2 - pad - th / 2
    for key, ty, lit in (("on", on_y, on), ("off", off_y, not on)):
        pen.tag(f"switch_{key}", 0, ty, s.word(key), size, P.CARD if not lit else (P.GREEN if on else P.RED),
                P.WHITE if lit else INK, style="plain", inside=body)
    air = GAP_MIN / k + 2                                                   # the ceramic base between the plates
    top, foot = on_y + th / 2 + air, off_y - th / 2 - air
    bw = w - 2 * pad - 4
    pen.c.add(f'<rect x="{n(-bw / 2)}" y="{n(top)}" width="{n(bw)}" height="{n(foot - top)}" rx="3" '
              f'fill="{CERAMIC}" stroke="{INK}" stroke-width="1.2"/>')
    pen.child(body, "switch_base", -bw / 2, top, bw / 2, foot)
    hinge, jaw = foot - 7, top + 7
    for bx in (-bw * 0.22, bw * 0.22):                                      # the jaws and the hinge clips
        for cy in (jaw, hinge):
            pen.c.add(f'<rect x="{n(bx - 4)}" y="{n(cy - 4)}" width="8" height="8" rx="1" fill="{COPPER}" '
                      f'stroke="{INK}" stroke-width="1"/><circle cx="{n(bx)}" cy="{n(cy)}" r="1.4" '
                      f'fill="{P.METAL_DARK}"/>')
    blade = hinge - jaw
    turn = 0 if on else -62                                                 # off: swung out of the jaws
    g = Canvas()
    for bx in (-bw * 0.22, bw * 0.22):
        g.add(f'<rect x="{n(bx - 2)}" y="{n(-blade)}" width="4" height="{n(blade)}" fill="{COPPER}" stroke="{INK}" '
              f'stroke-width="1"/>')
    g.add(f'<rect x="{n(-bw * 0.32)}" y="{n(-blade - 3)}" width="{n(bw * 0.64)}" height="6" rx="2" '
          f'fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="1.2"/>'            # the insulated crossbar
          f'<rect x="-4" y="{n(-blade - 16)}" width="8" height="14" rx="3.5" fill="{P.CHARCOAL}" stroke="{INK}" '
          f'stroke-width="1.4"/>')                                               # its handle
    pen.c.add(f'<g transform="translate(0,{n(hinge)}) rotate({turn})">{g.render()}</g>')
    for bx in (-w / 2 + 3.5, w / 2 - 3.5):                # the screws that hold it to the wall
        for by in (-h / 2 + 3.5, h / 2 - 3.5):
            pen.c.add(f'<circle cx="{n(bx)}" cy="{n(by)}" r="1.6" fill="{P.METAL_DARK}" stroke="{INK}" '
                      f'stroke-width=".6"/>')
    gx = -w * 0.2                                         # the cable gland in its top
    pen.c.add(f'<path d="M{n(gx - 6)},{n(-h / 2)} V{n(-h / 2 - 3)} L{n(gx - 4)},{n(-h / 2 - 6)} H{n(gx + 4)} '
              f'L{n(gx + 6)},{n(-h / 2 - 3)} V{n(-h / 2)} Z" fill="{P.METAL_DARK}" stroke="{INK}" '
              f'stroke-width="1"/>')
    box = pen.box(-w / 2 - dw, -h / 2 - 6, w / 2, h / 2)
    s.put(1.5, pen.svg(), box, "switch", group="switch")
    connect(s, tee, pen.port(gx, -h / 2 - 6, 0, -1, "switch"), "cable", max(2.4, 3.5 * k), depth=1.4)


def switch_extent(s: Strip, k: float) -> tuple[float, float, float, float]:
    """How far the switch reaches from its cabinet's middle on the page: left (the open door), up, right, down."""
    w, h, _, _ = switch_size(s, k)
    return (w / 2 + _door(w)) * k, (h / 2 + 6) * k, w / 2 * k, h / 2 * k


def _switch_at(s: Strip, spots: tuple[float, ...], y: float, k: float) -> float | None:
    """The first x of `spots` where the switch fits on the wall with its middle at y, or None."""
    left, up, right, down = switch_extent(s, k)
    r = cabin(s)
    if y - up < r.trunk + r.tube + 6:                      # its gland stays under the trunk it hangs from
        return None
    for x in spots:
        if s.free((x - left - 4, y - up - 4, x + right + 4, y + down + 4), 6):
            return x
    return None


def task(s: Strip, beat: str) -> None:
    r = cabin(s)
    k = s.unit
    ak = min(k, (r.floor - r.trunk - r.tube - 10) / 210)
    ax = s.x(0.0) + 62 * ak
    airlock(s, ax, r.floor, ak)
    lead = who(s, "professor", "cat")
    body = _box(s, lead, 0, r.floor)
    after = ax + 62 * ak + max(s.tall * 0.3, (body[2] - body[0]) / 2 + 4)   # the lead stands clear of the door
    sk = k * 1.1                                            # the switch's scale
    if beat == "work":
        prof = cast(s, lead, max(0.2, frac_of(s, after)), "present", "talk")
        hx, hy = s.hand(prof, "present", False)
        ck = post_scale(s, hy, k)                           # the capsule's scale, the tube's width with it
        cx = hx + 17 * ck                                   # held by its back end, pushed into the mouth
        bx = hx + 26 * ck
        agent = cast(s, "agent", 0.92, "present", "smile", flip=True)
        ax2, ay2 = s.hand(agent, "present", True)
        ok = post_scale(s, ay2, k)
        room_ = (ax2 - hx) - 230 * k                        # the two tubes' bends and the switch between them
        cap = max(0.1, (room_ / (2 * POST_BEND + 4) - 3) / 14)
        if min(ck, ok) > cap:                               # a near camera: thinner tubes, so they never cross
            ck = ok = cap
            cx, bx = hx + 17 * ck, hx + 26 * ck
        ox = ax2 - 26 * ok
        ib = post_center(bx, ck, -1)
        ob = post_center(ox, ok, 1)
        r = cabin(s)
        sx, sy = None, hy                                   # the switch: between the two tubes, or over the inlet's
        for scale in (1.1, 0.9, 0.75, 0.6, 0.5, 0.42):
            sk = k * scale
            left, up, right, down = switch_extent(s, sk)
            mid = (ib + ob) / 2 - (right - left) / 2
            size = letter(k, 10.0)                          # the outlet's plate reaches back under its mouth
            plate = (wrap(18 + GAP_MIN / k + 3 + tag_size(s.word("outlet"), size, k)[0], k) + 6) * k
            if ib + post_bore(ck) / 2 + 8 < mid - left and mid + right < min(ob - post_bore(ok) / 2, ox - plate) - 8:
                sx = _switch_at(s, (mid,), hy, sk)
            if sx is None:                                  # over the inlet's run, under the trunk
                high = hy - post_bore(ck) / 2 - 8 * k - down
                if high - up > r.trunk + r.tube + 6:
                    edge = ib - post_bore(ck) / 2 - 8 - right       # clear of the tube rising to its tee
                    spots = tuple(x for x in (min(edge, bx + (ib - bx) * 0.4), edge) if x - left > bx + post_bore(ck))
                    sx = _switch_at(s, spots, high, sk)
                    sy = high
            if sx is not None:
                break
        sw = switch_size(s, sk)[0] * 0.2 * sk
        trunk = Trunk(s, "on", taps=(ib, ob) + ((sx - sw,) if sx is not None else ()),
                      riders=((s.x(0.55), CARGO["task"], 1),), load=progress(0, beat))
        post_box(s, bx, hy, k, trunk.down(ib), s.word("inlet"), prof.group, side=-1, way=1, ck=ck)
        s.put(prof.bottom + 1, capsule(cx, hy, ck, CARGO["task"], label=s.word("capsule"), cut=(bx - cx) / ck),
              None, group=prof.group)
        s.put(1.7, seen_inside(capsule(cx, hy, ck, CARGO["task"]), bx, 1, hy, 40 * ck), None)
        bore = post_bore(ok)                                # the hiss of the tube bringing the capsule to the outlet
        s.put(3, puff(ox - (ox - ob) * 0.3, ay2 - bore - 10 * k, k), None, group=agent.group)
        post_box(s, ox, ay2, k, trunk.down(ob), s.word("outlet"), agent.group, side=1, way=-1, ck=ok)
        s.put(agent.bottom + 1, capsule(ax2 - 17 * ok, ay2, ok, CARGO["task"], turn=180,
                                        cut=(ax2 - 17 * ok - ox) / ok), None, group=agent.group)
        s.put(1.7, seen_inside(capsule(ax2 - 17 * ok, ay2, ok, CARGO["task"], turn=180), ox, -1, ay2, 40 * ok),
              None)
        if sx is not None:
            wall_switch(s, sx, sy, sk, True, trunk.down(sx - sw))
        size = max(sets.LETTERING_MIN + 6, 24 * k)          # the hiss, last: on the bare wall left of the tube
        sound(s, ob - lettering_width(s.word("pssh"), size) * 0.7, ay2 - bore + 4 * k, s.word("pssh"), size)
    else:
        cast(s, "agent", 0.55, "read", "worry", flip=False, mark="?")
        bx = s.x(0.22)
        foot = s.feet(bx) - height_of("agent", s) * 0.55
        ck = post_scale(s, foot, k)
        ib = post_center(bx, ck, -1)
        sx = None
        for scale in (1.1, 0.8, 0.6, 0.45):               # as big as fits under the trunk
            sk = k * scale
            sx = _switch_at(s, (s.x(0.8), s.x(0.88)), foot, sk)
            if sx is not None:
                break
        sw = switch_size(s, sk)[0] * 0.2 * sk
        trunk = Trunk(s, "off", taps=(ib,) + ((sx - sw,) if sx is not None else ()))
        post_box(s, bx, foot, k, trunk.down(ib), s.word("inlet"), "inlet", lit=False, side=-1, way=1, ck=ck)
        if sx is not None:                                   # the line is off: the blades out of their jaws
            wall_switch(s, sx, foot, sk, False, trunk.down(sx - sw))
        stand(s, "caterpillar", (0.4, 0.68, 0.36, 0.72), "think", "worry", face=s.x(0.55))
    if s.seed % 2 == 0:                                   # the sparrow on the airlock's frame, after the post
        bird(s, ax + 30 * ak, r.floor - 170 * ak, "airlock", face=W)
    finish(s, 0, beat, ax)


# The tool rack: a pegboard hung from two tees of the trunk by rods; the built-in tools on hooks, each with its
# name on a tag under it - what an agent has without MCP - and two spare hooks for the tools still to come.
TOOLS = ("read", "bash", "edit")
SPARE = 34.0          # the width of a spare hook's column


def _tool_icon(c: Canvas, kind: str) -> None:
    if kind == "read":
        c.line("M5,6 L14,17", 4.4, P.WOOD_DARK)
        c.add(f'<circle cx="-2" cy="-2" r="10" fill="{P.LENS}" fill-opacity=".85" stroke="{INK}" '
              f'stroke-width="2.4"/>')
        c.line("M-7,-6 A7,7 0 0 1 -2,-9", 1.6, P.WHITE)
    elif kind == "bash":
        c.shape(rounded_rect_d(-15, -12, 30, 24, 3), P.TERMINAL, sw=1.8, light=None)
        c.line("M-10,-5 L-5,0 L-10,5 M-2,6 H6", 1.8, P.TERMINAL_GREEN)
    else:
        c.shape("M-3,-16 H3 V8 L0,15 L-3,8 Z", P.YELLOW, sw=1.6, light=(-1, 0))
        c.path("M-3,8 L0,15 L3,8 Z", P.WOOD_PALE, 1.2)
        c.path("M-3,-16 H3 V-12 H-3 Z", P.PINK, 1.2)


def rack_size(k: float, labels: tuple[str, ...], egg: bool = False) -> tuple[float, float, list[float], float, float]:
    """The rack's width and height in its own units, the widths of its columns, the label size and tag height; with
    the `egg`, the last spare hook's column is wide enough for the golden floppy hung on it."""
    size = letter(k, 12.0)
    tag_h = tag_size("Ag", size, k, "plain")[1]
    last = max(SPARE, (floppy_size(FLOPPY_K)[0] + 2 * GAP_MIN + 4) / k) if egg else SPARE
    cols = [max(60.0, tag_size(label, size, k, "plain")[0] + 12) for label in labels] + [SPARE, last]
    return wrap(sum(cols), k), wrap(80 + tag_h, k), cols, size, tag_h


def tool_rack(s: Strip, x: float, top: float, k: float, labels: tuple[str, ...], taken: int, trunk: Trunk,
              group: str = "rack") -> None:
    """The rack, its top middle at (x, top), sized from its content: a column per tool, as wide as its tool or its
    label in a tag, then the spare hooks; the labels at a size that reads on the page."""
    w, h, cols, size, tag_h = rack_size(k, labels, bool(getattr(s, "egg", None)))
    pen = Pen(s, x, top, k)
    board = pen.container("rack", -w / 2, 0, w, h, P.BEIGE, radius=6, shade_k=0.88)
    for gx in range(int(-w / 2 + 14), int(w / 2 - 10), 16):
        for gy in range(16, int(h - 8), 16):
            pen.c.dot(gx, gy, 1.3, P.BEIGE_SHADE)
    left = -sum(cols) / 2
    y0 = pen.pad(w, h) + 2
    for i, cw in enumerate(cols):
        cx = left + cw / 2
        left += cw
        pen.c.line(f"M{n(cx - 6)},{n(y0 + 4)} h12 M{n(cx)},{n(y0 + 4)} v10", 2.6, P.METAL_DARK)   # the hook
        if i >= len(labels):                                  # a spare hook, waiting
            if i == len(cols) - 1 and getattr(s, "egg", None):  # the golden floppy hung on it (an easter egg)
                fx, fy = pen.at(cx + 2, y0 + 9 + floppy_size(1.0)[1] * FLOPPY_K / k)
                if stash(s, fx, fy, 3.01, group=group, holder=board):
                    continue
            pen.child(board, f"hook{i}", cx - 7.3, y0 + 2.7, cx + 7.3, y0 + 15.3)
            continue
        if i != taken:
            tool = Canvas()
            _tool_icon(tool, TOOLS[i])
            pen.c.add(f'<g transform="translate({n(cx)},{n(y0 + 42)}) scale(1.3)">{tool.render()}</g>')
            pen.child(board, f"tool{i}", cx - 20, y0 + 20, cx + 20, y0 + 64)
        else:                                                 # the outline where the taken tool hangs
            pen.c.add(f'<path d="M{n(cx - 18)},{n(y0 + 24)} h36 v36 h-36 Z" fill="none" stroke="{INK}" '
                      f'stroke-width="1.2" stroke-dasharray="3 3" opacity=".55"/>')
            pen.child(board, f"tool{i}", cx - 18, y0 + 24, cx + 18, y0 + 60)
        pen.tag(f"label{i}", cx, y0 + 78 + tag_h / 2, labels[i], size, style="plain", ink=P.PEN, inside=board)
    s.put(3, pen.svg(), pen.box(-w / 2, -2, w / 2, h), group, group=group)
    for dx in (-w * 0.36, w * 0.36):
        connect(s, trunk.down(x + dx * k), pen.port(dx, 0, 0, -1, group), "rod", 4, depth=2.9)


def tools(s: Strip, beat: str) -> None:
    r = cabin(s)
    k, t = s.unit, r.tube
    floor = s.feet(s.x(0.4)) - 4
    rk = min(k * 1.3, (floor - (r.trunk + t) - 24 * k) / 170, 1.3)
    for _ in range(6):                                    # the rack leaves the deck room for two onlookers
        rk = min(rk, (s.hi - s.lo) * (0.42 if low(s) else 0.32) / rack_size(rk, ("read_file", "bash", "edit"),
                                                       bool(getattr(s, "egg", None)))[0])
    rx = s.x(0.36)
    labels = ("read_file", "bash", "edit")
    pw = rack_size(rk, labels, bool(getattr(s, "egg", None)))[0] * rk
    trunk = Trunk(s, "idle", taps=(rx - pw * 0.36, rx + pw * 0.36), load=progress(1, beat))
    taken = (1, 0, 2)[s.seed % 3]                  # page after page on this station, the agent takes the next tool
    tool_rack(s, rx, r.trunk + t + 14 * rk, rk, labels, taken, trunk)
    agent = cast(s, "agent", 0.8, "present", "smile", flip=True)
    upright = _upright(s, agent) if TOOLS[taken] == "bash" else 0.0   # the screen held upright
    s.hold(agent, HELD[TOOLS[taken]], turn=upright)       # the tool it took, in its fist by the handle
    stand(s, "caterpillar" if s.again else "cat", (0.64, 0.62, 0.96), "point" if not s.again else "think",
          "talk" if not s.again else "worry", face=rx)
    finish(s, 1, beat, rx)


def held_terminal(x: float, y: float, k: float) -> str:
    """The bash tool held: a small terminal screen gripped by its lower edge, the prompt on it."""
    c = Canvas()
    c.shape(rounded_rect_d(-1.5, -16, 21, 15.5, 1.5), P.TERMINAL, sw=0.9, light=None)
    c.line("M2,-12 L5,-9 L2,-6 M7,-5 H12", 0.9, P.TERMINAL_GREEN)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


HELD = {"read": handheld.magnifier, "bash": held_terminal, "edit": handheld.pencil}   # each tool as held


# The MCP connection box: a box on the wall, fed from the trunk by its pipe; in the middle of its face the socket - a
# bezel with a recessed square mouth and its three pin holes - over it the plate with the protocol's name, under it
# the lamp that lights green once a connector is in.
# The reel: the connector's cable wound on a spool between two flanges, on an axle across its stand; the free end
# leaves the outermost wrap at the bottom of the coil, along the deck.
# The connector: a chunky plug with its pins in front and a carrying handle behind; its cable leaves the back of the
# body downward, so whoever carries it by the handle carries the cable clear of themselves.
# The MCP socket and its plug: a round industrial connector. The socket is a short round collar sticking out of the
# left side of a box on the wall, its flip lid hinged open on top; in its mouth the three holes. The plug is a round
# body on a handle with a coupling ring and a narrower sleeve with three pins - the sleeve just fits the collar, the
# pins the holes. Seated, the sleeve is inside the collar and the collar's rim goes round it.
COLLAR = 22.0            # how far the socket's collar sticks out of its box, in its units
COLLAR_R = 17.0          # its outer radius; the plug's sleeve (12.5) slides into its bore (14)


def socket_size(k: float, word: str) -> tuple[float, float, float, float, float, float]:
    """The socket box's width and height in its own units, its plate's lettering size and tag height, the
    collar's length and the gap under the plate."""
    size = letter(k, 11.0)
    tag_w, tag_h = tag_size(word, size, k)
    gap = GAP_MIN / k + 4
    return wrap(max(tag_w, 40.0), k), max(2 * COLLAR_R + 16, wrap(tag_h + gap + 22, k)), size, tag_h, COLLAR, gap


def socket_center(x: float, k: float, word: str) -> float:
    """Where the middle of the socket's box is, the mouth of its collar at x."""
    return x + (COLLAR + socket_size(k, word)[0] / 2) * k


def socket_box(s: Strip, x: float, y: float, k: float, plugged: bool, trunk: Trunk, word: str,
               group: str = "socket") -> None:
    """The socket, the mouth of its collar at (x, y): the collar out of the box's left side, its lid open, the box
    with its plate, hung from a tee of the trunk by the glass tube."""
    w, h, size, tag_h, collar, gap = socket_size(k, word)
    pen = Pen(s, x, y, k)
    left = collar
    box = pen.container("socket_box", left, -h / 2, w, h, P.METAL, radius=8, shade_k=0.84)
    pad = pen.pad(w, h)
    pen.tag("socket_plate", left + w / 2, -h / 2 + pad + 1 + tag_h / 2, word, size, P.CARD, inside=box)
    for bx in (left + 6, left + w - 6):                   # the bolts that hold it to the wall
        for by in (-h / 2 + 6, h / 2 - 6):
            pen.c.add(f'<circle cx="{n(bx)}" cy="{n(by)}" r="2" fill="{P.METAL_DARK}" stroke="{INK}" '
                      f'stroke-width=".7"/>')
    rr = COLLAR_R                                          # the collar, from the box's side to its mouth
    pen.c.shape(f"M{n(left + 1)},{n(-rr)} H0 V{n(rr)} H{n(left + 1)} Z", P.METAL_LIGHT, sw=2, light=(0, -2),
                shade_k=0.82)
    pen.c.add(f'<rect x="{n(left - 6)}" y="{n(-rr - 2)}" width="6" height="{n(2 * rr + 4)}" rx="2" '
              f'fill="{P.METAL}" stroke="{INK}" stroke-width="1.6"/>')          # its flange on the box
    pen.c.add(f'<ellipse cx="0" cy="0" rx="{n(rr * 0.34)}" ry="{n(rr)}" fill="{P.METAL}" stroke="{INK}" '
              f'stroke-width="2"/>')
    if not plugged:                                        # its mouth: the bore and the three holes
        pen.c.add(f'<ellipse cx="0" cy="0" rx="{n(rr * 0.24)}" ry="14" fill="{P.CHARCOAL}" stroke="{INK}" '
                  f'stroke-width="1.2"/>')
        for dy in (-6, 0, 6):
            pen.c.add(f'<ellipse cx="0" cy="{dy}" rx="1.4" ry="2" fill="{P.METAL_DARK}"/>')
    hx, hy = 4.0, -rr                                      # the flip lid, hinged on top of the mouth, swung open
    pen.c.add(f'<g transform="rotate(-28 {n(hx)} {n(hy)})"><ellipse cx="{n(hx - rr * 0.35)}" cy="{n(hy - rr * 0.95)}" '
              f'rx="{n(rr * 0.5)}" ry="{n(rr * 0.92)}" fill="{LAMPS[2]}" stroke="{INK}" stroke-width="1.8"/>'
              f'<ellipse cx="{n(hx - rr * 0.35)}" cy="{n(hy - rr * 0.95)}" rx="{n(rr * 0.3)}" ry="{n(rr * 0.6)}" '
              f'fill="{lighten(LAMPS[2], 0.3)}" stroke="{INK}" stroke-width="1"/></g>'
              f'<rect x="{n(hx - 4)}" y="{n(hy - 3)}" width="8" height="6" rx="2" fill="{P.METAL_DARK}" '
              f'stroke="{INK}" stroke-width="1.2"/>')                          # the lid and its hinge
    s.put(4, pen.svg(), pen.box(-rr * 0.34 - 1, -h / 2, left + w, h / 2), group, group=group)
    s.put(4, "", pen.box(-rr * 1.4, -rr * 2.9, rr * 0.6, -rr + 1), f"{group}_lid", group=group)   # the open lid
    connect(s, trunk.down(socket_center(x, k, word)), pen.port(left + w / 2, -h / 2, 0, -1, group), "tube",
            trunk.r.tube * 0.7, depth=1.6)


def reel(s: Strip, x: float, floor: float, k: float, group: str = "reel") -> Port:
    """The reel, the middle of its foot at (x, floor), the spool seen from the side; returns the port where the
    cable pays out of the coil - off the bottom of its outermost wrap, tangent to it, hanging straight down between
    the legs of the stand."""
    pen = Pen(s, x, floor, k)
    pen.c.shape("M-34,0 L-26,-46 L-18,0 Z M18,0 L26,-46 L34,0 Z", P.METAL_DARK, sw=1.8, light=None)   # the stand
    pen.c.line("M-30,-46 H30", 3.4, P.METAL)                                                         # the axle
    pen.c.shape(rounded_rect_d(-22, -70, 44, 48, 6), P.CHARCOAL, sw=2, light=(-1, -2), shade_k=0.8)   # the coil
    for i in range(7):                                                                               # its wraps
        wx = -18 + i * 6
        pen.c.line(f"M{wx},-69 Q{wx + 4},-46 {wx},-23", 1.3, P.METAL_DARK)
    for fx in (-26, 26):                                                                             # flanges
        pen.c.add(f'<ellipse cx="{fx}" cy="-46" rx="6" ry="32" fill="{P.ORANGE_DARK}" stroke="{INK}" '
                  f'stroke-width="2"/><circle cx="{fx}" cy="-46" r="3.4" fill="{P.METAL}" stroke="{INK}" '
                  f'stroke-width="1.2"/>')
    s.put(floor - 1, pen.svg(), pen.box(-34, -78, 34, 0), group, group=group)
    return pen.port(0, -22, 0, 1, group)


PLUG_OUT = (-0.45, 0.89)   # the way the cable leaves a seated plug: down and back, onto the deck gently


PLUG_SEAT = 54.0         # seated, the coupling ring's face is at the socket's mouth: the sleeve is inside


def plug(x: float, y: float, k: float, cut: float | None = None) -> str:
    """The connector, its handle's grip at the origin and its nose to the right: the handle, a stem forward to the
    round body (12..50), the coupling ring (50..54), the sleeve that goes into the socket's collar (54..70) and the
    three pins (70..80) that go into its holes. The cable leaves the body's underside at (20, 16) - its port,
    straight down; `connect` draws the boot there. `cut` hides what is past that x - the part inside a socket."""
    c = Canvas()
    c.shape(rounded_rect_d(-10, -5, 22, 10, 4), P.CHARCOAL, sw=1.8, light=None)          # the grip
    c.shape("M8,-3 H14 V3 H8 Z", P.METAL_DARK, sw=1.4, light=None)                      # the stem
    c.shape(rounded_rect_d(12, -16, 40, 32, 8), P.ORANGE, sw=2.2, light=(-2, -2), shade_k=0.8)
    for gx in (20, 26, 32):                                                             # its grip ribs
        c.line(f"M{gx},-13 V13", 1.2, P.ORANGE_DARK, 0.9)
    c.shape(rounded_rect_d(49, -17, 6, 34, 2), P.METAL, sw=1.8, light=None)             # the coupling ring
    c.shape(rounded_rect_d(54, -12.5, 17, 25, 3), P.ORANGE_DARK, sw=2, light=(-1, -1))  # the sleeve
    for dy in (-6, 0, 6):
        c.add(f'<rect x="70" y="{dy - 1.6}" width="10" height="3.2" rx="1" fill="{P.METAL_LIGHT}" stroke="{INK}" '
              f'stroke-width="1"/>')
    body = c.render()
    if cut is not None:
        clip = uid("cut")
        body = (f'<clipPath id="{clip}"><rect x="-20" y="-30" width="{n(cut + 20)}" height="60"/></clipPath>'
                f'<g clip-path="url(#{clip})">{body}</g>')
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{body}</g>'


def cord(s: Strip, rim: Port, end: Port, deck: float, k: float) -> None:
    """The cable from the reel to the plug: paying out of the coil straight down, onto the deck in one wide bend,
    along it, and up into the plug's boot in another - the bends as wide as the room allows; no fitting at the
    coil, a cable just comes off its wrap."""
    drop = max(0.0, deck - rim.y)
    rise = max(0.0, deck - end.y)
    land = end.x + end.dx / end.dy * rise                  # where the plug's line comes down onto the deck
    width = 6 * k if not low(s) else 4.5 * k               # a close-up's cast is bigger: the cable keeps its look
    connect(s, rim, end, "cable", width, via=((rim.x, deck), (land, deck)), depth=s.h,
            lead=(drop * 0.4, rise * 0.4), fits=(False, True))


def mcp(s: Strip, beat: str) -> None:
    plugged = beat == "spark"
    k = s.unit
    word = s.word("mcp")
    cx = s.x(0.86)                                         # the middle of the socket's box
    mx = cx - (COLLAR + socket_size(k, word)[0] / 2) * k  # the mouth of its collar
    r = cabin(s)
    under = r.trunk + r.tube * 0.75 + 10 * k + socket_size(k, word)[1] * k / 2 + COLLAR_R * 2 * k   # clear of it
    sy = max(s.feet(cx) - height_of("cat", s) * 0.55, under)
    trunk = Trunk(s, "on" if plugged else "off", taps=(cx,),
                  riders=((cx + 70 * k, CARGO["task"], 1),) if plugged else (), load=progress(2, beat))
    socket_box(s, mx, sy, k, plugged, trunk, word)
    rx = s.x(0.0) + 36 * k
    rim = reel(s, rx, s.feet(rx) - 2, k)
    deck = s.feet(s.x(0.5)) + 10 * k                       # along the deck, nearer than anyone's feet
    if plugged:
        gx = mx - PLUG_SEAT * k                            # seated: the sleeve and the pins inside the collar
        s.put(s.feet(cx) + 1, plug(gx, sy, k, cut=PLUG_SEAT), None, group="plug")
        s.put(s.feet(cx) + 2, burst(mx + 4 * k, sy - 22 * k, k * 0.8), None, group="plug")
        end = port(s, gx + 20 * k, sy + 16 * k, *PLUG_OUT, "plug")
        cord(s, rim, end, min(max(deck, end.y + 40 * k), s.h - 4 * k), k)   # low enough for a wide bend
        cast(s, "cat", 0.42, "cheer", "smile", flip=True)
        sound(s, mx - 40 * k, sy - 56 * k, s.word("dzyn"), max(sets.LETTERING_MIN + 6, 26 * k), "plug")  # clear of him
    else:
        short = min([mx - COLLAR_R * 0.5 * k - 8] + [b.left - 4 for b in s.boxes if b.group == "socket"])
        for frac in (0.5, 0.45, 0.4, 0.35, 0.3, 0.25):    # carried towards the socket, its pins short of it and its lid
            cat = cast(s, "cat", frac, "present", "talk", flip=False)
            hx, hy = s.hand(cat, "present", False)
            if hx + 80 * k < short or frac == 0.25:
                break
            index, _ = s.drawn.pop(id(cat))               # too close: stand it a step further back
            s.items.pop(index)
            s.boxes.remove(cat)
        s.put(cat.bottom + 1, plug(hx, hy, k), (hx - 10 * k, hy - 17 * k, hx + 80 * k, hy + 17 * k), "plug",
              group=cat.group)
        end = port(s, hx + 20 * k, hy + 16 * k, 0, 1, "plug")      # held: it hangs straight down, clear of the cat
        cord(s, rim, end, min(max(deck, end.y + 56 * k), s.h - 6 * k), k)   # lying low enough for a wide bend
        stand(s, "agent", (0.7, 0.68, 0.3), "think", "smile", face=cx)
    if plugged:
        stand(s, "caterpillar", (0.66, 0.7, 0.22), "cheer", "smile", face=cx)
    if s.seed % 2 == 0:                                   # the sparrow on the reel's flange, watching the cable go
        bird(s, rx + 22 * k, s.feet(rx) - 2 - 78 * k, "reel", face=cx)
    finish(s, 2, beat, cx)


# The junction: a tee on the trunk where a branch goes up through the ceiling to the services in orbit; under it,
# its post box, where a capsule for the services is posted and the answer comes out on paper.
def services(s: Strip, beat: str) -> None:
    r = cabin(s)
    k, t = s.unit, r.tube
    load = progress(3, beat)
    if beat == "send":
        agent = cast(s, "agent", 0.16, "present", "smile", flip=False)
        hx, hy = s.hand(agent, "present", False)
        ck = post_scale(s, hy, k)
        mx = hx + 26 * ck                                    # the mouth meets the capsule held by its back end
        jx = post_center(mx, ck, -1)
        trunk = Trunk(s, "on", taps=(jx,), up=(jx,), load=load, cargo=("task",))
        post_box(s, mx, hy, k, trunk.down(jx), s.word("mail"), agent.group, side=-1, way=1, ck=ck)
        held = capsule(hx + 17 * ck, hy, ck, CARGO["task"], label=s.word("capsule"))
        s.put(agent.bottom + 1, capsule(hx + 17 * ck, hy, ck, CARGO["task"], label=s.word("capsule"),
                                        cut=(mx - hx - 17 * ck) / ck), None, group=agent.group)
        s.put(1.7, seen_inside(held, mx, 1, hy, 40 * ck), None)
        way, going = -1, CARGO["task"]
        stand(s, "cat", (0.44, 0.4, 0.5), "think", "smile", face=hx)
    else:
        jx = s.x(0.28)
        trunk = Trunk(s, "on", taps=(jx,), up=(jx,), load=load, cargo=SERVICES)
        cat = cast(s, "cat", 0.62, "present", "smile", flip=True)
        hx, hy = s.hand(cat, "present", True)
        out = printer_box(s, jx, s.feet(jx) - height_of("agent", s) * 0.55, k, trunk.down(jx), s.word("mail"),
                          "post", toward=1)
        low = max(out.y, hy) + 32 * k                      # the printout sags between the slot and the paw
        connect(s, out, port(s, hx, hy, -1, 0, cat.group), "paper", 12 * k,
                via=(((out.x * 2 + hx) / 3, low), ((out.x + hx * 2) / 3, low)), depth=cat.bottom + 1, lead=12 * k)
        way, going = 1, CARGO["logs"]
        stand(s, "agent", (0.86, 0.9, 0.08), "point", "smile", face=hx)
    connect(s, port(s, jx, r.ceil + 8 * r.u, 0, 1, "hull"), trunk.upward(jx), "tube", t * 0.85, depth=1.1)
    if r.trunk - r.ceil > 70 * k:
        cy = r.ceil + (r.trunk - r.ceil) * 0.45
        s.put(1.15, capsule(jx, cy, t / 15, going, turn=90) + motion(jx, cy, 22, t / 15, way, vertical=True), None)
    pr = max(12.0, min(26.0, r.wall * 0.09))
    if r.ceil < 100:                                       # a tall frame shows the services outside instead
        fracs = (0.5, 0.63, 0.76, 0.89) if beat == "send" else (0.72, 0.8, 0.88, 0.96)
        for f, kind in zip(fracs, SERVICES, strict=True):
            for wy in (r.top + pr * 1.3 + 4, r.trunk + r.tube + pr * 1.3 + 6, r.trunk + r.tube + pr * 2.6 + 10):
                if porthole(s, s.x(f), wy, pr, kind):
                    break
    finish(s, 3, beat, jx)


def porthole(s: Strip, x: float, y: float, r: float, kind: str) -> bool:
    """A small round window with a service in orbit and its name on a tag under it, where the wall is free."""
    size = max(sets.LETTERING_MIN + 1, r * 0.55)
    label = s.word(kind)
    tw, th = tag_size(label, size)
    box = (x - max(r * 1.2, tw / 2), y - r * 1.2, x + max(r * 1.2, tw / 2), y + r * 1.2 + 4 + th)
    rm = cabin(s)
    clear_of_trunk = box[3] < rm.trunk - rm.tube or box[1] > rm.trunk + rm.tube
    if not clear_of_trunk or not s.free(box, 6) or box[3] > s.base - 4:
        return False
    if any(box[0] - 4 < x < box[2] + 4 and box[1] - 4 < y < box[3] + 4 for link in getattr(s, "links", [])
           for x, y in link.points):                      # clear of every tube and cable too
        return False
    pen = Pen(s, 0, 0, 1)
    pen.c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r * 1.2)}" fill="{P.METAL}" stroke="{INK}" stroke-width="2"/>'
              f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{P.SPACE_DEEP}" stroke="{INK}" stroke-width="1.6"/>')
    pen.c.add(satellite(x, y + r * 0.1, r / 38, kind))
    pen.tag(f"win_{kind}", x, y + r * 1.2 + 4 + th / 2, label, size)
    s.put(3, pen.svg(), box, f"win_{kind}")
    return True


# The scanner: an X-ray tunnel the trunk passes through - a boxy housing on two legs from the deck, the line going
# in at its left through a lead curtain and out at its right; the radiation sticker on its face; a window in its
# face onto the tube inside, where the capsule passing through is seen as an X-ray - the letter in it, or the sealed
# envelope with its note. Its console stands by it, joined to it by a cable.
def trefoil(x: float, y: float, rad: float) -> str:
    """The radiation warning sticker: a yellow disc, the black trefoil on it."""
    c = Canvas()
    c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rad)}" fill="{P.YELLOW}" stroke="{INK}" stroke-width="1.4"/>')
    c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rad * 0.16)}" fill="{INK}"/>')
    r0, r1 = rad * 0.26, rad * 0.82
    for i in range(3):
        a0, a1 = math.radians(-90 + i * 120 - 30), math.radians(-90 + i * 120 + 30)
        c.add(f'<path d="M{n(x + math.cos(a0) * r0)},{n(y + math.sin(a0) * r0)} '
              f'L{n(x + math.cos(a0) * r1)},{n(y + math.sin(a0) * r1)} '
              f'A{n(r1)},{n(r1)} 0 0 1 {n(x + math.cos(a1) * r1)},{n(y + math.sin(a1) * r1)} '
              f'L{n(x + math.cos(a1) * r0)},{n(y + math.sin(a1) * r0)} '
              f'A{n(r0)},{n(r0)} 0 0 0 {n(x + math.cos(a0) * r0)},{n(y + math.sin(a0) * r0)} Z" fill="{INK}"/>')
    return c.render()


def scanner(s: Strip, x: float, r: Hull, foot: float, k: float, alarm: bool, color: str = P.ORANGE,
            wide: float = 1.0, drop: float = 0.0) -> Port:
    """The X-ray tunnel round the line at x, showing the capsule of `color` inside; returns the port low on its
    right leg for the console's cable. `drop` lets the housing hang that much lower with the X-ray screen in its
    face, the capsule inside shown big (a close-up)."""
    t = r.tube
    hh = min(t * 1.7 + 12 * k, r.trunk - 3)                 # the housing's half-height round the line
    hw = max(t * 3.4, hh * 1.9) * wide
    pen = Pen(s, x, r.trunk, 1.0)
    for lx in (-hw * 0.62, hw * 0.62):                      # the legs and their feet
        pen.c.shape(f"M{n(lx - 4 * k)},{n(hh + drop)} V{n(foot - r.trunk)} H{n(lx + 4 * k)} V{n(hh + drop)} Z",
                    P.METAL_DARK,
                    sw=1.8, light=None)
        pen.c.shape(rounded_rect_d(lx - 11 * k, foot - r.trunk - 4 * k, 22 * k, 4 * k, 1.5), P.METAL_DARK, sw=1.6,
                    light=None)
    body = pen.container("xray", -hw, -hh, 2 * hw, 2 * hh + drop, P.METAL_PALE, radius=8, shade_k=0.84)
    pad = pen.pad(2 * hw, 2 * hh + drop)
    mouth = t * 0.85                                         # the tunnel's mouths, a little wider than the line
    for side in (-1, 1):
        mx = side * hw
        pen.c.add(f'<rect x="{n(mx - (6 if side > 0 else 0))}" y="{n(-mouth)}" width="6" height="{n(2 * mouth)}" '
                  f'fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="1.4"/>')
    strip = 2 * mouth / 5                                    # the lead curtain over the way in
    for i in range(5):
        pen.c.add(f'<rect x="{n(-hw - 3)}" y="{n(-mouth + i * strip + 0.6)}" width="9" height="{n(strip - 1.2)}" '
                  f'rx="1" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width=".8"/>')
    ww = hw * 0.9                                            # the window onto the tube inside
    wh = min(2 * hh - 2 * pad, t * 2.2)
    pen.c.add(f'<rect x="{n(-ww / 2)}" y="{n(-wh / 2)}" width="{n(ww)}" height="{n(wh)}" rx="5" '
              f'fill="{P.SCREEN_DARK}" stroke="{INK}" stroke-width="2"/>')
    pen.c.add(f'<rect x="{n(-ww / 2)}" y="{n(-t * 0.42)}" width="{n(ww)}" height="{n(t * 0.84)}" '
              f'fill="{P.SCREEN}" fill-opacity=".35"/>')                    # the tube, seen through
    pen.c.add(capsule(0, 0, min(t / 15 * 1.1, wh / 18), color, glass="planted" if alarm else "letter"))
    pen.child(body, "window", -ww / 2, -wh / 2, ww / 2, wh / 2)
    if drop > 20:                                            # the X-ray screen under it, the capsule seen big
        st, sb = wh / 2 + GAP_MIN + 3, hh + drop - pad
        sw_ = min(ww, (sb - st) * 2.4)
        pen.c.add(f'<rect x="{n(-sw_ / 2)}" y="{n(st)}" width="{n(sw_)}" height="{n(sb - st)}" rx="4" '
                  f'fill="{P.SCREEN_DARK}" stroke="{INK}" stroke-width="2"/>')
        ck = min((sw_ - 8) / 36, (sb - st - 6) / 16)
        pen.c.add(capsule(0, (st + sb) / 2, ck, color, glass="planted" if alarm else "letter"))
        pen.child(body, "screen", -sw_ / 2, st, sw_ / 2, sb)
    room = hw - pad - ww / 2 - GAP_MIN - 1                  # the radiation sticker, beside the window
    rad = min(hh - pad, room / 2, 12 * k)
    if rad > 5:
        sx, sy = ww / 2 + GAP_MIN + 1 + rad, -hh + pad + rad
        pen.c.add(trefoil(sx, sy, rad))
        pen.child(body, "trefoil", sx - rad, sy - rad, sx + rad, sy + rad)
    s.put(1.4, pen.svg(), (x - hw - 4, r.trunk - hh, x + hw + 4, foot), "scanner", group="scanner")
    return port(s, x + hw * 0.62 + 4 * k, foot - 18 * k, 1, 0, "scanner")


def monitor(s: Strip, x: float, floor: float, k: float, alarm: bool, word: str, color: str,
            feed: Port | None = None) -> bool:
    """The scanner's console, its foot at (x, floor): a pedestal and on it the screen, sized from its picture and
    its words - the title, the x-ray of the capsule in the ring (its caps in `color`), the letter inside or the
    sealed envelope with its note, and the verdict - with the beacon on the screen's top; the cable from `feed`
    comes into the pedestal's foot. Drawn only where it fits and reads; returns whether it was."""
    size = letter(k, 10.0)
    title = s.word("xray")
    tsize = letter(k, 8.0)
    tag_w, tag_h = tag_size(word, size, k, "plain")
    head_w, head_h = tag_size(title, tsize, k, "plain")
    pic_w, pic_h = 64.0, 28.0
    gap = GAP_MIN / k + 3
    w, h = wrap(max(tag_w, pic_w, head_w), k), wrap(head_h + gap + pic_h + gap + tag_h, k)
    stand, dome = 44.0, 16.0
    box = (x - w / 2 * k, floor - (h + stand + dome) * k, x + w / 2 * k, floor)
    rm = cabin(s)
    wide = (box[0] - (18 * k if alarm else 0), box[1], box[2] + (18 * k if alarm else 0), box[3])
    if box[1] < rm.trunk + rm.tube + 6 or not s.free(wide, 6):
        return False
    pen = Pen(s, x, floor, k)
    pen.c.shape(f"M-16,0 L-11,{-stand} H11 L16,0 Z", P.METAL, sw=1.8, light=(-1, -1))   # the pedestal
    pen.c.line(f"M-9,{-stand * 0.45} H9", 1.4, INK, 0.5)
    top = -h - stand
    screen = pen.container("monitor", -w / 2, top, w, h, P.SCREEN_DARK, radius=6, light=None)
    pad = pen.pad(w, h)
    pen.tag("xray_title", 0, top + pad + head_h / 2, title, tsize, P.SCREEN_DARK, P.SCREEN_LIGHT, style="plain",
            inside=screen)
    py = top + pad + head_h + gap + pic_h / 2
    pen.c.add(capsule(0, py, 1.7, color, glass="planted" if alarm else "letter"))
    pen.child(screen, "x-ray", -30, py - 14, 30, py + 14)
    pen.tag("verdict", 0, -stand - pad - 1 - tag_h / 2, word, size, P.CARD, P.RED if alarm else P.GREEN,
            style="plain", inside=screen)
    light = P.RED if alarm else P.GREEN                    # the beacon, fixed on the screen's top
    by = top
    pen.c.shape(rounded_rect_d(-9, by - 5, 18, 5, 1.5), P.CHARCOAL, sw=1.4, light=None)
    pen.c.shape(f"M-7,{n(by - 5)} Q-7,{n(by - dome)} 0,{n(by - dome)} Q7,{n(by - dome)} 7,{n(by - 5)} Z", light,
                sw=1.6, light=(-1, -1), highlight=f"M-3.5,{n(by - 8)} Q-3.5,{n(by - 12)} 0,{n(by - 13)}")
    if alarm:
        pen.c.line(f"M10,{n(by - 13)} l6,-4 M11,{n(by - 7)} l7,0 M-10,{n(by - 13)} l-6,-4 M-11,{n(by - 7)} l-7,0",
                   2, P.RED)
    s.put(floor, pen.svg(), (box[0] - (18 * k if alarm else 0), box[1], box[2] + (18 * k if alarm else 0), floor),
          "monitor", group="monitor")
    if feed is not None:
        ly = max(-stand + 4, min(-6.0, (feed.y - floor) / k))   # at the feed's height: one straight run
        foot = pen.port(-16 + 5 * (-ly / stand), ly, -1, 0, "monitor")   # into the pedestal's side, its gland
        connect(s, feed, foot, "cable", max(3.0, 5 * k), depth=1.45)
    return True


def check(s: Strip, beat: str) -> None:
    r = cabin(s)
    alarm = beat == "alarm"
    k = s.unit
    close = s.h < 200                          # a strip: the gate in the middle, the two right beside it
    ax = s.x(0.5 if close else 0.36)
    seen = CARGO["tickets"] if alarm else CARGO["logs"]       # the capsule in the ring, and on the screen
    t = r.tube
    gate = max(t * 3.4, min(t * 1.7 + 12 * k, r.trunk - 3) * 1.9) * (1.5 if close else 1.0)
    if alarm:                                  # the line stopped: the capsules stand where they were
        Trunk(s, "off", riders=((ax - gate - 4 * t, CARGO["base"], 0),) if close else ((s.x(0.16), CARGO["base"], 0),))
    elif close:                                # one going in, one coming out, both on the move
        Trunk(s, "on", riders=((ax, seen, 1), (ax - gate - 3 * t, CARGO["tickets"], 1),
                               (ax + gate + 4.5 * t, CARGO["base"], 1)), keep=(ax,))
    else:
        Trunk(s, "on", riders=((ax, seen, 1),), load=progress(4, beat), cargo=SERVICES, keep=(ax,))
    feed = scanner(s, ax, r, s.feet(ax) - 2, k, alarm, seen, wide=1.5 if close else 1.0,
                   drop=(s.feet(ax) - r.trunk) * 0.42 if close else 0.0)
    if close:
        legs = (ax - gate * 0.62 - 12 * k, s.h * 0, ax + gate * 0.62 + 12 * k, s.h)
        right = frac_of(s, legs[2] + 6 + height_of("caterpillar", s) * 0.45)
        left = frac_of(s, legs[0] - 6 - height_of("cat", s) * 0.5)
        stand(s, "caterpillar", (right, right + 0.02, right + 0.05), "wave" if alarm else "write",
              "worry" if alarm else "smile", face=ax, hold=None if alarm else handheld.clipboard)
        stand(s, "cat" if alarm else "agent", (left, left - 0.02, left - 0.05), "point" if alarm else "think",
              "talk" if alarm else "smile", face=ax)
        finish(s, 4, beat, ax)
        return
    if alarm:                                  # stopped in the tunnel and seen through: the planted envelope
        cast(s, "caterpillar", 0.88, "wave", "worry", flip=True)
    else:
        cast(s, "caterpillar", 0.88, "write", "smile", flip=True)
    mx = s.x(0.64)
    for mk in (k, k * 0.85, k * 0.7):                      # the console as big as the wall under the line allows
        if monitor(s, mx, s.feet(mx) - 2, mk, alarm, s.word("suspicious" if alarm else "clean"), seen, feed):
            break
    if alarm:
        stand(s, "cat", (0.08, 0.12, 0.6), "point", "talk", face=ax)
    else:
        stand(s, "agent", (0.08, 0.12, 0.6), "think", "smile", face=ax)
    finish(s, 4, beat, ax)


# The valves: a branch down from a tee of the trunk to each service, a hand wheel on it - green open, red shut -
# and the service's name on a tag with the same color. The red button: on its striped pedestal under a hinged glass
# cap, for the last chapter of the book.
def valve(s: Strip, x: float, y: float, k: float, open_: bool, label: str, trunk: Trunk, group: str) -> None:
    pen = Pen(s, x, y, k)
    pen.c.shape(rounded_rect_d(-9, -12, 18, 24, 3), P.METAL, sw=1.8, light=None)
    pen.c.add(f'<circle cx="0" cy="0" r="16" fill="none" stroke="{INK}" stroke-width="6"/>'
              f'<circle cx="0" cy="0" r="16" fill="none" stroke="{P.GREEN if open_ else P.RED}" stroke-width="3.6"/>')
    turn = 0 if open_ else 45
    pen.c.add(f'<g transform="rotate({turn})"><path d="M-16,0 H16 M0,-16 V16" stroke="{INK}" stroke-width="2.6"/></g>')
    pen.c.dot(0, 0, 4, P.METAL_DARK)
    size = letter(k, 11.0)
    tw, th = tag_size(label, size, k)
    ty = 19 + GAP_MIN / k + th / 2
    pen.tag(f"valve_{label}", 0, ty, label, size, outline=P.GREEN if open_ else P.RED)
    half = max(19.0, tw / 2)
    s.put(2, pen.svg(), pen.box(-half, -19, half, ty + th / 2), f"valve_{label}", group=group)
    connect(s, trunk.down(x), pen.port(0, -12, 0, -1, group), "tube", trunk.r.tube * 0.55, depth=1.6,
            color=None if open_ else GLASS_DEAD)


def button(s: Strip, x: float, floor: float, k: float, word: str) -> tuple[float, float, float, float]:
    """The red button's console, the middle of its foot at (x, floor), sized from its warning plate: a desk-high
    box, the plate striped yellow and black in the middle of its face; on top, the big red mushroom button under a
    clear cover hinged at the back. Returns the cover's box."""
    size = letter(k, 10.0)
    tag_w, tag_h = tag_size(word, size, k, "plain")
    stripe = 5.0
    w = wrap(tag_w + 2 * stripe + 2, k)
    h = max(56.0, wrap(tag_h + 2 * stripe + 2, k))
    pen = Pen(s, x, floor, k)
    body = pen.container("button_console", -w / 2, -h, w, h, P.METAL_DARK, radius=6)
    pw, ph = tag_w + 2 * stripe, tag_h + 2 * stripe
    py = -h / 2
    pen.c.add(f'<rect x="{n(-pw / 2)}" y="{n(py - ph / 2)}" width="{n(pw)}" height="{n(ph)}" rx="3" '
              f'fill="{P.YELLOW}" stroke="{INK}" stroke-width="1.6"/>')
    stripes = " ".join(f"M{n(-pw / 2 + i * 9)},{n(py - ph / 2)} l-6,{n(ph)}" for i in range(1, int(pw / 9) + 1))
    pen.c.add(f'<clipPath id="{(cid := uid("st"))}"><rect x="{n(-pw / 2)}" y="{n(py - ph / 2)}" width="{n(pw)}" '
              f'height="{n(ph)}" rx="3"/></clipPath><path d="{stripes}" stroke="{INK}" stroke-width="3.4" '
              f'clip-path="url(#{cid})"/>')
    pen.tag("button_plate", 0, py, word, size, P.YELLOW_PALE, INK, style="plain")
    pen.child(body, "plate", -pw / 2, py - ph / 2, pw / 2, py + ph / 2)
    top = -h                                                 # the button and its cover on top
    pen.c.shape(rounded_rect_d(-14, top - 8, 28, 8, 2), P.CHARCOAL, sw=1.6, light=None)
    pen.c.shape(f"M-16,{top - 8} Q-16,{top - 30} 0,{top - 30} Q16,{top - 30} 16,{top - 8} Z", P.RED, sw=2.2,
                light=(-2, -2), shade_k=0.78, highlight=f"M-9,{top - 14} Q-8,{top - 24} 0,{top - 26}")
    pen.c.add(f'<path d="M-22,{top} V{top - 34} Q-22,{top - 42} -14,{top - 42} H14 Q22,{top - 42} 22,{top - 34} '
              f'V{top} Z" fill="{P.LENS}" fill-opacity=".3" stroke="{INK}" stroke-width="1.6"/>')
    pen.c.line(f"M-16,{top - 34} Q-10,{top - 39} -2,{top - 39}", 1.6, P.WHITE, 0.85)
    pen.c.add(f'<rect x="18" y="{top - 6}" width="6" height="6" rx="1" fill="{P.METAL}" stroke="{INK}" '
              f'stroke-width="1"/>')
    s.put(floor, pen.svg(), pen.box(-w / 2, top - 42, w / 2, 0), "button", group="button")
    return pen.box(-22, top - 42, 22, top)


def panel(s: Strip, beat: str) -> None:
    r = cabin(s)
    k, t = s.unit, r.tube
    bx = s.x(0.88)
    bk = min(k * 1.1, (s.feet(bx) - r.trunk - t) * 0.62 / 110)
    if beat == "work":
        agent = cast(s, "agent", 0.66, "present", "smile", flip=True)
        hx, hy = s.hand(agent, "present", True)
        size = letter(k, 11.0)                    # the valves far enough apart for their name tags
        step = max(66 * k, max(tag_size(s.word(key), size, k)[0] for key in SERVICES) * k + 10)
        half = tag_size(s.word(SERVICES[-1]), size, k)[0] * k / 2      # its name tag clear of the agent's feet
        last = min(hx - 16 * k, agent.left - half - 6)
        xs = [last - i * step for i in range(4)][::-1]    # the last valve right by the agent's hand
        group = agent.group
    else:
        hy = s.feet(s.x(0.5)) - height_of("agent", s) * 0.5
        xs = [s.x(f) for f in (0.12, 0.23, 0.34, 0.45)]
        group = "valves"
    trunk = Trunk(s, "on", taps=tuple(xs), load=progress(5, beat), cargo=tuple(k_ for k_ in SERVICES
                                                                              if k_ not in SHUT))
    for key, x in zip(SERVICES, xs, strict=True):
        valve(s, x, hy, k, key not in SHUT, s.word(key), trunk, group)
    cover = button(s, bx, s.feet(bx) - 2, bk, s.word("dont_press"))
    if beat == "button":                        # the sparrow comes down on the cover, wings out to lift it
        size_ = min(s.tall * SIZE["sparrow"] * 0.42, (cover[1] - r.trunk - t) * 0.9)
        if size_ > 18:
            s.actor("sparrow", (cover[0] + cover[2]) / 2 - size_ * 0.5, cover[1] + size_ * 0.25, "fly", "smile",
                    flip=False, tall=size_ / 0.42 / 0.95, group="button")
        stand(s, "cat", (0.6, 0.62, 0.56, 0.66), "think", "surprise", face=bx)
    else:
        stand(s, "caterpillar", (0.78, 0.04, 0.06), "write", "smile", face=xs[-1],
              hold=handheld.clipboard)
    finish(s, 5, beat, (xs[0] + xs[-1]) / 2)


# ============================================================================ outside
def earth(x: float, y: float, r: float) -> str:
    c = Canvas()
    clip = c.shape(ellipse_d(0, 0, 20, 20), P.BLUE, sw=1.4, light=(-3, -3), clip=True)
    c.add(f'<g clip-path="url(#{clip})"><path d="M-15,-9 q6,-8 13,-2 q-1,7 -8,6 q-5,5 -7,-1 Z M3,1 q9,-4 13,3 '
          f'q-3,9 -9,9 q-6,-3 -4,-12 Z M-8,10 q4,-2 7,2 q-3,4 -7,-2 Z" fill="{P.GREEN}" stroke="{INK}" '
          f'stroke-width=".6"/><path d="M-18,4 q8,-4 15,0 M2,-14 q6,-2 12,1" stroke="{P.WHITE}" stroke-width="2.2" '
          f'fill="none" stroke-linecap="round" opacity=".85"/></g>')
    return _at(c, x, y, r / 20)


def satellite(x: float, y: float, k: float, kind: str, down: bool = False) -> str:
    """A service in orbit, as satellites are drawn: a box body (its color and sign tell what it keeps), two solar
    panels on booms, a small dish on a mast - on top, or underneath when the station is below (`down`). 104 wide,
    26 tall plus the dish's 21 at k = 1; the dish's feed at (0, -34), or (0, 34) when `down`."""
    c = Canvas()
    c.line("M-14,0 H-20 M14,0 H20", 2, P.METAL_DARK)
    for dx in (-52, 20):
        c.shape(f"M{dx},-9 H{dx + 32} V9 H{dx} Z", P.BLUE, sw=1.4, light=None)
        c.line(f"M{dx + 8},-9 V9 M{dx + 16},-9 V9 M{dx + 24},-9 V9 M{dx},0 H{dx + 32}", 0.8, P.WHITE)
    c.shape(rounded_rect_d(-14, -13, 28, 26, 3), CARGO.get(kind, P.METAL), sw=1.6, light=(-1, -1))
    if kind == "logs":
        c.line("M-8,-6 H8 M-8,-1 H8 M-8,4 H4", 1.4)
    elif kind == "tickets":
        c.path("M-6,-7 H6 V6 L3,3 L0,6 L-3,3 L-6,6 Z", P.WHITE, 1.1)
    elif kind == "base":
        c.path(ellipse_d(0, -4, 6, 2.2), P.WHITE, 1.1)
        c.line("M-6,-4 V5 Q0,8 6,5 V-4", 1.1)
    elif kind == "metrics":
        for bx, bh in ((-7, 6), (-2, 11), (3, 8)):
            c.add(f'<rect x="{bx}" y="{6 - bh}" width="4" height="{bh}" fill="{P.WHITE}" stroke="{INK}" '
                  f'stroke-width=".9"/>')
    way = 1 if down else -1
    c.line(f"M0,{13 * way} V{17 * way}", 2, P.METAL_DARK)
    c.add(f'<path d="M-12,{26 * way} A12,8 0 0 {0 if not down else 1} 12,{26 * way} Z" fill="{P.METAL_PALE}" '
          f'stroke="{INK}" stroke-width="1.6"/><ellipse cx="0" cy="{26 * way}" rx="12" ry="2.6" fill="{P.METAL}" '
          f'stroke="{INK}" stroke-width="1.2"/>')
    c.line(f"M0,{26 * way} V{33 * way}", 1.4)
    c.dot(0, 34 * way, 2, P.RED)
    return _at(c, x, y, k)


def dish(x: float, y: float, k: float, open_: bool) -> str:
    """The station's dish on its mast: folded like a closed umbrella, or open with a beam going out."""
    c = Canvas()
    c.shape("M-3,0 V-26 H3 V0 Z", P.METAL_DARK, sw=1.4, light=None)
    if open_:
        c.shape("M-26,-42 Q0,-16 26,-42 Q0,-31 -26,-42 Z", P.METAL_PALE, sw=1.8, light=(-1, -1))
        c.line("M0,-31 L0,-47", 1.4)
        c.dot(0, -48, 2.4, P.SUN)
        c.line("M-7,-57 Q0,-63 7,-57 M-12,-65 Q0,-74 12,-65", 1.8, P.SUN)
    else:
        bowl = Canvas()                                    # parked: the bowl turned down to the hull, no signal
        bowl.shape("M-26,-42 Q0,-16 26,-42 Q0,-31 -26,-42 Z", P.METAL_PALE, sw=1.8, light=None)
        bowl.line("M0,-31 L0,-47", 1.4)
        c.add(f'<g transform="rotate(150 0 -30)">{bowl.render()}</g>')
    return _at(c, x, y, k)


def shuttle(x: float, y: float, k: float, mirror: bool = False) -> str:
    """A space shuttle seen from the side, nose to the right: a long fuselage with a rounded nose and a row of
    cockpit windows, a payload-bay seam, a delta wing under the body, a tall tail fin, three engine bells at the
    back. The origin is the fuselage's middle; 200 long, 90 tall at k = 1."""
    c = Canvas()
    c.shape("M-60,-6 L-30,-62 H-12 L-8,-6 Z", P.WHITE, sw=2.2, light=(-2, -2), shade_k=0.88)   # the tail fin
    c.add(f'<rect x="-36" y="-50" width="12" height="7" fill="{P.ORANGE}" stroke="{INK}" stroke-width="1"/>')
    c.shape("M-50,8 L20,8 L-16,32 L-56,32 Z", P.METAL_LIGHT, sw=2.2, light=(-2, -2), shade_k=0.86)  # the delta wing
    c.line("M-52,28 L-18,28", 1.4, INK, 0.5)
    for dy in (-10, 0, 10):                                                                   # the engine bells
        c.shape(f"M-74,{dy - 4} L-88,{dy - 8} L-88,{dy + 8} L-74,{dy + 4} Z", P.METAL_DARK, sw=1.6, light=None)
    c.shape("M-74,-18 H50 Q96,-18 100,0 Q96,18 50,18 H-74 Z", P.WHITE, sw=2.4, light=(-2, -3), shade_k=0.86,
            highlight="M-60,-12 H50")                                                        # the fuselage
    c.shape("M70,-16 Q96,-14 100,0 Q96,14 70,16 Q78,0 70,-16 Z", P.CHARCOAL, sw=1.6, light=None)  # the nose cap
    for wx in (46, 56, 66):
        c.shape(f"M{wx - 4},-14 L{wx + 4},-14 L{wx + 5},-7 L{wx - 3},-7 Z", P.SCREEN_LIGHT, sw=1.3, light=None)
    c.line("M-60,-4 H36 M-60,4 H36", 1.2, INK, 0.45)                                         # the bay doors
    c.line("M-74,10 H56", 2.4, P.ORANGE)
    return _at(c, x, y, k, mirror)


def robot_arm(x: float, y: float, k: float, held: str = "", reach: bool = True) -> str:
    """The station's robot arm on the hull: a base, two white booms with orange joints, a claw at (96, -88) in its
    units holding `held`; folded down along the hull when it does not `reach`."""
    c = Canvas()
    c.shape(rounded_rect_d(-14, -10, 28, 10, 3), P.METAL_DARK, sw=1.8, light=None)
    elbow, tip = ((40, -70), (90, -82)) if reach else ((46, -26), (96, -12))
    c.tube(f"M0,-8 L{elbow[0]},{elbow[1]}", P.WHITE, 9, sw=1.6)
    c.tube(f"M{elbow[0]},{elbow[1]} L{tip[0]},{tip[1]}", P.WHITE, 8, sw=1.6)
    for jx, jy in ((0, -8), elbow):
        c.add(f'<circle cx="{jx}" cy="{jy}" r="7" fill="{P.ORANGE}" stroke="{INK}" stroke-width="1.6"/>')
    c.line(f"M{tip[0]},{tip[1]} l10,-8 M{tip[0]},{tip[1]} l10,6", 3, P.METAL_DARK)
    c.add(held)
    return _at(c, x, y, k)


def beacon(x: float, y: float, k: float, on: bool) -> str:
    """A warning beacon on the hull: dark, or lit red and flashing."""
    c = Canvas()
    c.shape(rounded_rect_d(-10, -6, 20, 6, 2), P.METAL_DARK, sw=1.6, light=None)
    c.shape("M-8,-6 Q-8,-22 0,-22 Q8,-22 8,-6 Z", P.RED if on else darken(P.RED, 0.6), sw=1.8, light=(-1, -1))
    if on:
        c.line("M12,-18 l9,-6 M13,-10 l10,0 M-12,-18 l-9,-6 M-13,-10 l-10,0", 2.2, P.RED)
    return _at(c, x, y, k)


def _orbit(s: Strip, hull: float, k: float, src: Port, beams: tuple[str, ...]) -> None:
    """The four services in orbit over the hull, each with its name on a tag over it and its dish turned down to
    the station's antenna at `src`; a beam runs to each service in `beams`. A service whose beam would cross
    another one, or that would sit in another's beam, stays out of the picture."""
    size = max(sets.LETTERING_MIN + 2, 12 * k)
    th = tag_size("Ag", size)[1]
    drawn: list[list[tuple[float, float]]] = []
    sk = min(k * 1.15, 1.1)
    while True:                                               # four abreast, with air between, either side of it
        half = 52 * sk + 3
        xs = _spread_across(half + 6, W - half - 6, src.x, half + 30, len(SERVICES))
        if sk <= 0.6 or all(b - a >= 2 * half + 12 for a, b in zip(xs, xs[1:], strict=False)):
            break
        sk -= 0.05
    sy = max(8 + th + 4 + 13 * sk, min(hull * 0.36, src.y - 70 - 35 * sk))
    for kind, sx in zip(SERVICES, xs, strict=True):
        body = (sx - 52 * sk, sy - 13 * sk, sx + 52 * sk, sy + 35 * sk)
        tw = tag_size(s.word(kind), size)[0]
        top = body[1] - 4 - th
        whole = (min(body[0], sx - tw / 2), top, max(body[2], sx + tw / 2), body[3])
        if top < 4 or body[0] < 4 or body[2] > W - 4 or not s.free(whole, 6):
            continue
        if any(whole[0] < x < whole[2] and whole[1] < y < whole[3] for line in drawn for x, y in path_points(line)):
            continue
        group = f"sat_{kind}"
        end = Port(sx, body[3], 0, 1, group)
        line = route(src, end, 2.2, lead=10)
        if kind in beams and not clear_path(s, line, {src.owner, group}):
            continue
        s.put(0.5, satellite(sx, sy, sk, kind, down=True), body, group, group=group)
        tag = Pen(s, 0, 0, 1)
        tag.tag(f"tag_{kind}", sx, top + th / 2, s.word(kind), size)
        s.put(0.6, tag.svg(), (sx - tw / 2, top, sx + tw / 2, top + th), f"tag_{kind}", group=group)
        if kind in beams:
            connect(s, src, port(s, end.x, end.y, 0, 1, group), "beam", 2.2, depth=0.3, lead=10)
            drawn.append(line)


def _spread_across(lo: float, hi: float, gap_at: float, gap: float, count: int) -> list[float]:
    """`count` places spread evenly over lo..hi, leaving `gap` clear on each side of `gap_at`: as many on each side
    of it as its share of the room."""
    left = max(0.0, gap_at - gap - lo)
    right = max(0.0, hi - gap_at - gap)
    on_left = round(count * left / ((left + right) or 1))
    on_left = min(count, max(0, on_left))
    out = [lo + left * (i + 0.5) / on_left for i in range(on_left)]
    on_right = count - on_left
    return out + [gap_at + gap + right * (i + 0.5) / on_right for i in range(on_right)]


def _antenna(s: Strip, x: float, hull: float, k: float) -> Port:
    """The antenna the branch goes up to, on the hull at x; returns the port its beams leave from."""
    ant = Pen(s, x, hull, k)
    ant.c.shape("M-6,0 V-34 H6 V0 Z", P.METAL, sw=1.8, light=None)
    ant.c.shape("M-22,-50 Q0,-24 22,-50 Q0,-38 -22,-50 Z", P.METAL_PALE, sw=1.8, light=(-1, -1))
    ant.c.line("M0,-38 V-50", 1.4)
    s.put(0.4, ant.svg(), ant.box(-24, -56, 24, 0), "antenna", group="antenna")
    return ant.port(0, -50, 0, -1, "antenna")


def outside(s: Strip, r: Hull, index: int, beat: str, at: float) -> None:
    """Above the module in a pulled-back frame: what belongs to its step outside the hull, over its node at `at`."""
    if r.ceil < 100:
        return
    hull = r.ceil - HULL_SKIN
    k = max(0.7, min(1.4, r.ceil / 240))
    earth_at = None
    if index == 0:                          # the shuttle that brought the task, docked over the airlock
        dock = Pen(s, at, hull, k)
        dock.c.shape(rounded_rect_d(-22, -22, 44, 22, 4), P.METAL, sw=2, light=(-1, -2))
        dock.c.add(f'<rect x="-28" y="-30" width="56" height="8" rx="3" fill="{LAMPS[0]}" stroke="{INK}" '
                   f'stroke-width="1.6"/>')
        sk = k * 0.9                        # nose left; the port meets its belly ahead of the wing
        sx, sy = at + 50 * sk, hull - 30 * k - 18 * sk
        s.put(0.4, dock.svg(), dock.box(-28, -30, 28, 0), "dock", group="dock")
        s.put(0.5, shuttle(sx, sy, sk, mirror=True), (sx - 100 * sk, sy - 62 * sk, sx + 88 * sk, sy + 32 * sk),
              "shuttle", group="dock")
        earth_at = W - 150
    elif index == 1:                        # the arm brings a toolbox down to the rack's module
        box = Canvas()
        box.shape(rounded_rect_d(80, -100, 40, 28, 3), P.RED, sw=1.8, light=(-1, -1))
        box.line("M92,-100 V-106 H108 V-100", 2.2)
        ka = min(k, (hull - 4) / 140)       # the toolbox stays below the top of the frame
        ax = min(at, W - 180 * ka)
        s.put(0.4, robot_arm(ax, hull, ka * 1.3, box.render()), (ax - 20 * ka, hull - 140 * ka, ax + 160 * ka, hull),
              "arm")
    elif index == 2:                        # the dish over the MCP box: folded, or open once the connector is in
        dk = min(k * 1.5, (hull - 4) / 76)  # its rim stays below the top of the frame
        s.put(0.4, dish(at, hull, dk, beat == "spark"), (at - 30 * dk, hull - 76 * dk, at + 30 * dk, hull), "dish")
    elif index == 3:                        # the branch through the hull to an antenna, a beam to each service
        _orbit(s, hull, k, _antenna(s, at, hull, k), SERVICES)
    elif index == 4:                        # the arm stands by; on the alarm the beacon flashes and it reaches over
        alarm = beat == "alarm"
        rise = 150 if alarm else 40
        ka = min(k, hull / rise)            # the raised arm stays below the top of a tall frame's sky
        ax = min(at + 40, W - 180 * ka)
        s.put(0.4, robot_arm(ax, hull, ka * 1.2, reach=alarm), (ax - 20 * ka, hull - rise * ka, ax + 160 * ka, hull),
              "arm")
        s.put(0.45, beacon(at - 40, hull, k * 1.2, alarm), (at - 40 - 30 * k, hull - 30 * k, at - 40 + 30 * k, hull),
              "beacon")
        earth_at = W * 0.12
    else:                                   # only the open valves' services still get a beam
        _orbit(s, hull, k, _antenna(s, at, hull, k), tuple(key for key in SERVICES if key not in SHUT))
    if earth_at is not None:
        rr = min(hull * 0.4, 110)
        box = (earth_at - rr, hull * 0.5 - rr, earth_at + rr, hull * 0.5 + rr)
        if s.free(box, 6):
            s.put(0.2, earth(earth_at, hull * 0.5, rr), box, "earth")


# ============================================================================ the finale
FINALE_CAST = {0: ("professor", "present"), 2: ("cat", "cheer"), 3: ("agent", "cheer"), 4: ("caterpillar", "write"),
               5: ("sparrow", "fly")}     # the tools module shows its rack alone: the agent stands at the services


def finale(s: Strip) -> None:
    """The whole line at once, running: six modules side by side in one cross-section, the trunk running through all
    of them with capsules riding; in each module its one node, hung from the line over the heads, and under it the
    one who works there, everyone at one scale and as big as a module's width lets them be, standing on the deck
    with the floor showing under their feet. A panorama adds the modules' names and, over the hull, the dish turned
    to the services and the Earth; a low strip reads without words."""
    from .world_fair import zoom
    ledger(s)
    zoom(s)
    c = s.back
    left, right = s.lo, s.hi
    shares = (1.0, 0.72, 1.0, 1.0, 1.3, 0.98)          # the rack's module needs little room, the X-ray's more
    edges = [left]
    for share in shares:
        edges.append(edges[-1] + (right - left) * share / sum(shares))
    wide = (right - left) / 6
    feet = s.feet(0)
    bottom = min(s.h - 4, feet + max(8.0, (s.h - feet) * 0.55))     # the deck's front edge, the floor under feet
    named = s.h >= 300
    size = max(sets.LETTERING_MIN + 1, min(16.0, s.h * 0.035))
    th = tag_size("Ag", size)[1]
    s.tall = 137.0
    widest = max((_box(s, name, 0, feet)[2] - _box(s, name, 0, feet)[0]) / 137 for name, _ in FINALE_CAST.values()
                 if name != "sparrow")
    tallest = max((_box(s, name, 0, feet)[3] - _box(s, name, 0, feet)[1]) / 137 for name, _ in FINALE_CAST.values()
                  if name != "sparrow")
    head_room = (th + 14 if named else 0) + (70 if s.h >= 200 else 54)   # the names, the trunk, the nodes
    hull_top = 8.0 if s.h < 300 else max(8.0, s.h * 0.22)
    tall = min(wide * 0.88 / widest, (feet - hull_top - head_room) / tallest, 300.0)
    s.tall, s.unit = tall, tall / 137
    head = feet - tallest * tall                          # the top of the tallest head
    t = max(8.0, min(16.0, tall * 0.08))
    under = hull_top + (th + 10 if named else 4)
    ty = under + t * 2.2 + 2                            # room over it for the X-ray tunnel round it
    room_h = bottom - hull_top
    top = hull_top
    _space(c, 0, s.h, W, seed=40)
    rim = 10
    c.shape(rounded_rect_d(left - rim, top - rim, right - left + 2 * rim, bottom - top + 2 * rim, 14), P.METAL,
            sw=2.4, light=(-3, -3), shade_k=0.82)
    if top > 90:
        dk = max(0.7, min(1.5, top / 160))
        dx = edges[3] + (edges[4] - edges[3]) * 0.22  # right over the junction's branch
        s.put(0.6, dish(dx, top - rim, dk, True), (dx - 30 * dk, top - rim - 76 * dk, dx + 30 * dk, top - rim),
              "dish")
    if top > 150:
        rr = min(top * 0.36, wide * 0.55)
        ex = left + wide * 5.2
        s.put(0.2, earth(ex, top * 0.48, rr), (ex - rr, top * 0.48 - rr, ex + rr, top * 0.48 + rr), "earth")
    deck = bottom - feet + 6
    floor = bottom - deck
    pen = Pen(s, 0, 0, 1)
    for i, station in enumerate(SPACE.stations):
        x0, mw = edges[i], edges[i + 1] - edges[i]
        c.add(f'<rect x="{n(x0 + 3)}" y="{n(top)}" width="{n(mw - 6)}" height="{n(room_h)}" '
              f'fill="{mix(P.HULL, LAMPS[i], 0.16)}" stroke="{INK}" stroke-width="2"/>')
        c.add(f'<rect x="{n(x0 + 3)}" y="{n(floor)}" width="{n(mw - 6)}" height="{n(deck)}" '
              f'fill="{mix(P.METAL, LAMPS[i], 0.08)}" stroke="{INK}" stroke-width="1.2"/>')
        c.line(f"M{n(x0 + 3)},{n(floor + 3)} H{n(x0 + mw - 3)}", 2, P.METAL_DARK)
        if named:
            holder = pen.tag(f"label{i}", x0 + mw / 2, top + 6 + th / 2, s.word(station.key), size,
                             P.CHARCOAL, P.WHITE)
            s.put(2, "", holder.outer, f"label{i}")
    s.put(2, pen.svg(), None)
    line = Canvas()                                   # the trunk, through the hull wall at both ends
    line.add(f'<rect x="{n(left - rim - 6)}" y="{n(ty - t / 2)}" width="{n(right - left + 2 * rim + 12)}" '
             f'height="{n(t)}" fill="{GLASS}" stroke="{INK}" stroke-width="2"/>')
    line.line(f"M{n(left - rim - 4)},{n(ty - t * 0.22)} H{n(right + rim + 4)}", max(1.2, t * 0.14), P.WHITE, 0.7)
    s.put(1, line.render(), None)
    riding = ("task", "task", "logs", "tickets", "base", "logs")      # the task first, then the answers
    for i in range(6):
        x = edges[i] + (edges[i + 1] - edges[i]) * 0.86
        s.put(1.2, capsule(x, ty, t / 15, CARGO[riding[i]]) + motion(x, ty, 16, t / 15, 1), None)
    band = max(20.0, head - 6 - (ty + t / 2))         # the nodes hang in the band over the heads
    k = max(0.3, min(1.25, band / 52))
    at = (0.2, 0.5, 0.62, 0.22, 0.16, 0.5)            # each node's x in its module
    nodes = [_finale_node(s, i, edges[i] + (edges[i + 1] - edges[i]) * at[i], ty, t, floor, k, top - rim)
             for i in range(6)]
    for i, (name, pose) in FINALE_CAST.items():
        x0, x1 = edges[i] + 6, edges[i + 1] - 6
        if name == "sparrow":
            s.actor("sparrow", (x0 + x1) / 2, feet - tall * 0.3, "fly", "smile", flip=True,
                    tall=tall * SIZE["sparrow"] * 0.5)
            continue
        half = (_box(s, name, 0, feet)[2] - _box(s, name, 0, feet)[0]) / 2
        node = nodes[i]
        spots = [(x0 + x1) / 2, x1 - half - 2, node[2] + half + 4]
        for x in spots:
            b = _box(s, name, x, feet)
            if b[0] >= x0 - 2 and b[2] <= x1 + 2 and s.free(b, 3):
                s.actor(name, x, feet, pose, "smile", flip=i >= 3, tall=tall * SIZE[name])
                break
        else:                                         # no room beside the node: as tall as the room beside it
            room_w = x1 - max(node[2] + 4, x0)
            fit = _fit_tall(name, room_w, feet - max(node[3] if node[3] < feet - 10 else ty + t, ty + t) - 4)
            s.actor(name, x1 - room_w / 2, feet, pose, "smile", flip=i >= 3, tall=min(tall * SIZE[name], fit))


def _finale_post(s: Strip, i: int, x: float, ty: float, t: float, k: float, color: str) -> tuple[float, float]:
    """A post terminal in the finale, as in its frames: the glass tube down from the trunk at x, round a wide
    bend to its mouth on the right, the hatch lid open over it and a capsule of `color` half in. Returns the right
    edge of what it draws and the height of its mouth."""
    bore = max(2.6, 5.5 * k)
    run = bore * POST_BEND                                 # room for the glass to bend round wide
    tee = port(s, x, ty + t / 2, 0, 1, f"node{i}")
    my = ty + t / 2 + run
    mx = x + run
    connect(s, tee, port(s, mx, my, -1, 0, f"node{i}"), "tube", bore, depth=1.25, lead=(run, run))
    c = Canvas()
    r = bore / 2 + 1.5
    c.add(f'<ellipse cx="{n(mx)}" cy="{n(my)}" rx="{n(r * 0.32)}" ry="{n(r)}" fill="{P.CHARCOAL}" stroke="{INK}" '
          f'stroke-width="1.4"/>')
    lid_t = max(1.6, 2.6 * k)                              # the lid, hinged on top of the mouth, swung up
    c.add(f'<g transform="rotate(-120 {n(mx)} {n(my - r)})"><rect x="{n(mx - lid_t)}" y="{n(my - r)}" '
          f'width="{n(lid_t)}" height="{n(2 * r)}" rx="{n(lid_t / 2)}" fill="{P.METAL}" stroke="{INK}" '
          f'stroke-width="1.1"/></g>')
    ck = max(0.1, (bore - 1.5) / 14)                       # the capsule, as thick as the bore lets it
    out = 9.0                                              # how much of it is still out of the mouth, own units
    held = capsule(mx + out * ck, my, ck, color, turn=180)
    c.add(seen_inside(held, mx, -1, my, 40 * ck))
    c.add(capsule(mx + out * ck, my, ck, color, turn=180, cut=out))
    right = mx + (out + 17) * ck
    s.put(1.75, c.render(), (mx - r, my - 2.4 * r, right, my + r), f"mouth{i}", group=f"node{i}")
    return right, my


def _finale_node(s: Strip, i: int, x: float, ty: float, t: float, floor: float, k: float,
                 roof: float) -> tuple[float, float, float, float]:
    """Module i's node in the finale, small but the same thing as in its frames, at x on the left of its module,
    scale k: the post tube and the main switch, the rack, the MCP socket with the plug in, the branch to the
    services and the post tube, the X-ray tunnel with its screen, the valves."""
    c = Canvas()
    low = ty + t / 2
    if i == 0:                                        # the post tube, a capsule going in, and the main switch on
        right, my = _finale_post(s, i, x, ty, t, k, CARGO["task"])
        bore = max(2.6, 5.5 * k)
        sw, sh = 11 * k, 15 * k                           # the switch, in the bend's inside corner
        sx, sy = x + bore * 4.2, low + bore * 2.2
        c.shape(rounded_rect_d(sx - sw / 2, sy, sw, sh, 2 * k), P.METAL, sw=1.4, light=None)
        c.add(f'<rect x="{n(sx - sw / 2 + 2 * k)}" y="{n(sy + 2 * k)}" width="{n(sw - 4 * k)}" height="{n(4 * k)}" '
              f'fill="{P.GREEN}" stroke="{INK}" stroke-width=".8"/>')      # its "on" plate, lit
        hub = (sx + sw / 2, sy + sh / 2)
        c.add(f'<g transform="translate({n(hub[0])},{n(hub[1])}) rotate(-50)"><rect x="0" y="{n(-1.3 * k)}" '
              f'width="{n(10 * k)}" height="{n(2.6 * k)}" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width=".9"/>'
              f'<rect x="{n(8 * k)}" y="{n(-2.6 * k)}" width="{n(7 * k)}" height="{n(5.2 * k)}" rx="{n(2.6 * k)}" '
              f'fill="{P.RED}" stroke="{INK}" stroke-width="1"/></g>')
        c.add(f'<circle cx="{n(hub[0])}" cy="{n(hub[1])}" r="{n(2.4 * k)}" fill="{P.METAL_LIGHT}" stroke="{INK}" '
              f'stroke-width=".9"/>')
        connect(s, port(s, sx - sw * 0.2, low, 0, 1, "node0"), port(s, sx - sw * 0.2, sy, 0, -1, "node0"), "cable",
                max(1.6, 2.4 * k), depth=1.25)
        box = (x - bore, low, right, my + bore)
    elif i == 1:                                      # the rack and its three tools
        for dx in (-22, 22):
            c.line(f"M{n(x + dx * k)},{n(low)} V{n(low + 12 * k)}", max(1.6, 3 * k), P.METAL_DARK)
        c.shape(rounded_rect_d(x - 32 * k, low + 12 * k, 64 * k, 40 * k, 4 * k), P.BEIGE, sw=2, light=None)
        for j, kind in enumerate(TOOLS):
            tool = Canvas()
            _tool_icon(tool, kind)
            c.add(f'<g transform="translate({n(x + (j - 1) * 20 * k)},{n(low + 32 * k)}) scale({n(0.62 * k)})">'
                  f'{tool.render()}</g>')
        box = (x - 32 * k, low, x + 32 * k, low + 52 * k)
    elif i == 2:                                      # the socket box, the plug seated in its collar
        bw, bh = 22 * k, 30 * k
        by = low + 12 * k
        c.add(f'<rect x="{n(x + bw / 2 - 3 * k)}" y="{n(low)}" width="{n(6 * k)}" height="{n(12 * k)}" '
              f'fill="{GLASS}" stroke="{INK}" stroke-width="1.4"/>')
        c.shape(rounded_rect_d(x, by, bw, bh, 4 * k), P.METAL, sw=1.8, light=None)
        my = by + bh / 2
        pk = 0.42 * k                                      # the plug, its sleeve as wide as the collar's bore
        rr = COLLAR_R * pk                                 # the collar out of the box's left side
        cl = 10 * k
        c.shape(f"M{n(x + 1)},{n(my - rr)} H{n(x - cl)} V{n(my + rr)} H{n(x + 1)} Z", P.METAL_LIGHT, sw=1.4,
                light=None)
        c.add(plug(x - cl - PLUG_SEAT * pk, my, pk, cut=PLUG_SEAT))
        c.add(f'<ellipse cx="{n(x - cl)}" cy="{n(my)}" rx="{n(rr * 0.34)}" ry="{n(rr)}" fill="none" stroke="{INK}" '
              f'stroke-width="1.4"/>')
        c.add(f'<g transform="rotate(-28 {n(x - cl + 2 * k)} {n(my - rr)})"><ellipse cx="{n(x - cl - rr * 0.3)}" '
              f'cy="{n(my - rr * 1.9)}" rx="{n(rr * 0.45)}" ry="{n(rr * 0.85)}" fill="{LAMPS[2]}" stroke="{INK}" '
              f'stroke-width="1.2"/></g>')                                  # the flip lid, open
        left = x - cl - (PLUG_SEAT + 10) * pk
        box = (left, low, x + bw, by + bh)
    elif i == 3:                                      # the branch up through the roof, a capsule going up it
        c.add(f'<rect x="{n(x - 4 * k)}" y="{n(roof)}" width="{n(8 * k)}" height="{n(ty - t / 2 - roof)}" '
              f'fill="{GLASS}" stroke="{INK}" stroke-width="1.6"/>')
        if ty - t / 2 - roof > 40 * k:
            c.add(capsule(x, (roof + ty) / 2, k * 0.5, CARGO["task"], turn=90))
        right, my = _finale_post(s, i, x, ty, t, k, CARGO["task"])
        bore = max(2.6, 5.5 * k)
        box = (x - bore, low, right, my + bore)
    elif i == 4:                                      # the X-ray tunnel round the line, its screen on its leg
        hw, hh = t * 1.3, t * 1.9
        lx = (x - hw * 0.62, x + hw * 0.62)
        for px in lx:
            c.shape(f"M{n(px - 2.5 * k)},{n(ty + hh)} V{n(floor)} H{n(px + 2.5 * k)} V{n(ty + hh)} Z", P.METAL_DARK,
                    sw=1.4, light=None)
            c.shape(rounded_rect_d(px - 7 * k, floor - 3 * k, 14 * k, 3 * k, 1), P.METAL_DARK, sw=1.2, light=None)
        c.shape(rounded_rect_d(x - hw, ty - hh, 2 * hw, 2 * hh, 5), P.METAL_PALE, sw=2, light=None)
        mouth = t * 0.85
        c.add(f'<rect x="{n(x - hw - 2)}" y="{n(ty - mouth)}" width="{n(5)}" height="{n(2 * mouth)}" '
              f'fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1"/>')  # the lead curtain over the way in
        for j in range(1, 4):
            c.line(f"M{n(x - hw - 2)},{n(ty - mouth + j * mouth / 2)} h5", 0.8, INK)
        c.add(f'<rect x="{n(x + hw - 3)}" y="{n(ty - mouth)}" width="3" height="{n(2 * mouth)}" fill="{P.CHARCOAL}"/>')
        ww, wh = hw * 1.15, t * 1.25                       # the window onto the tube, the capsule's X-ray in it
        c.add(f'<rect x="{n(x - ww / 2)}" y="{n(ty - wh / 2)}" width="{n(ww)}" height="{n(wh)}" rx="3" '
              f'fill="{P.SCREEN_DARK}" stroke="{INK}" stroke-width="1.6"/>')
        c.add(capsule(x, ty, min(ww / 40, wh / 18), CARGO["logs"], glass="letter"))
        rad = (hh - wh / 2) * 0.62                         # the radiation sticker over the window
        if rad > 3:
            c.add(trefoil(x, ty - wh / 2 - (hh - wh / 2) / 2, rad))
        sw_ = min(18 * k, (lx[1] - lx[0]) - 8 * k)         # the screen, on a crossbar between the legs
        sh_ = sw_ * 0.72
        scx, scy = x, ty + hh + (floor - ty - hh) * 0.3 + sh_ / 2
        c.line(f"M{n(lx[0])},{n(scy)} H{n(lx[1])}", max(1.4, 2.2 * k), P.METAL_DARK)
        c.shape(rounded_rect_d(scx - sw_ / 2, scy - sh_ / 2, sw_, sh_, 2 * k), P.SCREEN_DARK, sw=1.4, light=None)
        c.add(capsule(scx, scy - sh_ * 0.1, sw_ / 52, CARGO["logs"], glass="letter"))
        c.add(f'<rect x="{n(scx - sw_ * 0.32)}" y="{n(scy + sh_ * 0.22)}" width="{n(sw_ * 0.64)}" '
              f'height="{n(sh_ * 0.14)}" fill="{P.GREEN}"/>')                # its verdict bar: clean
        bt = scy - sh_ / 2                                 # the beacon on the screen's top, green
        c.shape(f"M{n(scx - 3 * k)},{n(bt)} Q{n(scx - 3 * k)},{n(bt - 6 * k)} {n(scx)},{n(bt - 6 * k)} "
                f"Q{n(scx + 3 * k)},{n(bt - 6 * k)} {n(scx + 3 * k)},{n(bt)} Z", P.GREEN, sw=1.1, light=None)
        box = (x - hw - 2, ty - hh, x + hw, floor)
    else:                                             # the four valves, two open and two shut
        for j, key in enumerate(SERVICES):
            open_ = key not in SHUT
            vx = x + (j - 1.5) * 15 * k
            c.add(f'<rect x="{n(vx - 2 * k)}" y="{n(low)}" width="{n(4 * k)}" height="{n(24 * k)}" '
                  f'fill="{GLASS if open_ else GLASS_DEAD}" stroke="{INK}" stroke-width="1.2"/>')
            c.add(f'<circle cx="{n(vx)}" cy="{n(low + 30 * k)}" r="{n(6 * k)}" fill="none" stroke="{INK}" '
                  f'stroke-width="{n(3.4 * k + 1.6)}"/><circle cx="{n(vx)}" cy="{n(low + 30 * k)}" r="{n(6 * k)}" '
                  f'fill="none" stroke="{P.GREEN if open_ else P.RED}" stroke-width="{n(3.4 * k)}"/>')
        box = (x - 30 * k, low, x + 30 * k, low + 38 * k)
    s.put(1.3, c.render(), box, f"node{i}", group=f"node{i}")
    return box


def _fit_tall(name: str, width: float, height: float) -> float:
    mod = char_module(name)
    per = mod.SCENE_SCALE / PROFESSOR_HEIGHT
    return min(width / (mod.SIZE[0] * 0.8 * per), height / ((mod.FEET_Y - mod.HEAD_TOP) * per))


# ============================================================================ the opener
TILT = 13.0          # degrees: the station drifts across the page, down to the right


def opener(st: Stage, accent: str):
    """The station from outside, the picture of the page, the machine still off: six modules strung along the dark
    trunk, each of its own shape and with the outer part of its job - the shuttle docked at the airlock's port, the
    robot arm with the toolbox, the folded dish over the MCP socket, the round junction with its antenna turned to
    the services, the scanner ring, the cupola - under a truss with solar wings. The services wait in orbit below
    it, their beams dim; the Earth rises behind. On the observation deck, the professor tells the agent and the
    caterpillar what is about to be switched on."""
    ledger(st)
    c = st.back
    paint = c.gradient([(0, P.SPACE_DEEP), (0.72, P.SPACE_LOW), (1, mix(P.SPACE_LOW, accent, 0.3))], 0, 0, 0, 1000)
    c.add(f'<rect x="0" y="0" width="{W}" height="1000" fill="{paint}"/>')
    sets.stars(c, (20, 20, W - 20, 900), 90, seed=17)
    c.add(earth(W + 40, 190, 170))                       # far behind everything, half beyond the page's edge
    deck = 1000
    c.add(f'<rect x="0" y="{deck}" width="{W}" height="{H - deck}" fill="{mix(P.METAL, accent, 0.08)}"/>')
    c.add(f'<rect x="0" y="{deck}" width="{W}" height="9" fill="{P.METAL_DARK}"/>')
    for x in range(-200, W + 240, 90):
        c.line(f"M{n(W / 2 + (x - W / 2) * 0.5)},{deck + 9} L{x},{H}", 1, INK, 0.3)
    rail = deck - 70
    c.add(f'<rect x="0" y="{rail}" width="{W}" height="70" fill="{P.LENS}" fill-opacity=".14"/>')
    st.keep_clear((-6, rail - 6, W + 6, deck))                # the deck's rail and its glass
    c.line(f"M0,{rail} H{W}", 7, P.METAL_DARK)
    c.line(f"M0,{rail} H{W}", 2.6, accent)
    for x in range(30, W, 96):
        c.line(f"M{x},{rail} V{deck}", 4.4, P.METAL_DARK)
    prof = st.actor("professor", 150, 1096, "explain", "talk", tall=330)
    st.speaker(prof, width=92, left=8, air=CLEAR_MM)
    st.actor("agent", 470, 1120, "wave", "smile", tall=330, group="agent")
    st.actor("caterpillar", 690, 1136, "write", "smile", tall=290, group="caterpillar")
    station = _Station()
    place = _fit(st, station)
    st.back.add(f'<g transform="{place.transform}">{station.c.render()}</g>')
    for name, local in station.parts:
        st.put(1, "", place.box(local), name, group="station")
    feed = place.point(*station.feed)
    src = port(st, *feed, *place.turn(0, 1), "station")
    _services_below(st, src)
    drawn = st.render()
    drawn.holders, drawn.links, drawn.ports = st.holders, st.links, st.ports
    return drawn


@dataclass
class _Placed:
    """Where the station went on the page: its local units scaled by `k`, turned by TILT, its centre at (x, y)."""
    k: float
    x: float
    y: float
    cx: float
    cy: float

    def turn(self, x: float, y: float) -> tuple[float, float]:
        a = math.radians(TILT)
        return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)

    def point(self, lx: float, ly: float) -> tuple[float, float]:
        dx, dy = self.turn((lx - self.cx) * self.k, (ly - self.cy) * self.k)
        return self.x + dx, self.y + dy

    def box(self, local: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
        x0, y0, x1, y1 = local
        pts = [self.point(x, y) for x in (x0, x1) for y in (y0, y1)]
        return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))

    @property
    def transform(self) -> str:
        return (f"translate({n(self.x)},{n(self.y)}) rotate({n(TILT)}) scale({n(self.k)}) "
                f"translate({n(-self.cx)},{n(-self.cy)})")


def _fit(st: Stage, station: _Station) -> _Placed:
    """The biggest scale at which the whole station fits on the page between the title, the bubble, the deck and
    the cast - every part's box clear of them - and, at that scale, the middle of the heights where it fits."""
    x0, y0, x1, y1 = station.extent
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for step in range(40):
        k = 1.2 - step * 0.02
        fits = []
        for y in range(240, 760, 6):
            for x in (W / 2, W / 2 + 20, W / 2 - 20):
                place = _Placed(k, x, y, cx, cy)
                boxes = [place.box(local) for _, local in station.parts]
                if all(b[0] >= 2 and b[2] <= W - 2 and b[3] <= 900 and st.free(b, 8) for b in boxes):
                    fits.append(place)
                    break
        if fits:
            return fits[len(fits) // 2]
    raise ValueError("the station does not fit on its opener")


def _services_below(st: Stage, src: Port) -> None:
    """The four services in orbit in a row below the station, as near under the junction's antenna as the page
    allows, each with its name on a tag under it and its dish turned up to the antenna; a dim beam joins each to
    it - the line is not on yet."""
    k, size, step = 0.9, 13.0, 106
    dim = mix(P.SUN, P.SPACE_LOW, 0.55)
    tags = {kind: tag_size(st.word(kind), size) for kind in SERVICES}
    th = max(h for _, h in tags.values())

    def whole(x: float, y: float) -> tuple[float, float, float, float]:
        tw = max(w for w, _ in tags.values())
        return (min(x - 52 * k, x - tw / 2), y - 34 * k, max(x + 52 * k, x + tw / 2), y + 13 * k + 4 + th)

    for y in range(int(src.y) + 70, 880, 8):
        free = [x for x in range(60, W - 50, 4) if st.free(whole(x, y), 10)]
        rows = []
        for first in free:
            row = [first]
            for x in free:
                if x >= row[-1] + step:
                    row.append(x)
                if len(row) == len(SERVICES):
                    break
            if len(row) == len(SERVICES):
                rows.append(row)
        rows.sort(key=lambda row: abs(sum(row) / len(row) - src.x))
        for row in rows:
            ends = [Port(x, y - 34 * k, 0, -1, f"sat_{kind}") for x, kind in zip(row, SERVICES, strict=True)]
            if all(clear_path(st, route(src, end, 2.2, lead=14), {"station", end.owner}) for end in ends):
                for end, kind in zip(ends, SERVICES, strict=True):
                    x, group = end.x, end.owner
                    st.put(1, satellite(x, y, k, kind), (x - 52 * k, y - 34 * k, x + 52 * k, y + 13 * k), group,
                           group=group)
                    tw, _ = tags[kind]
                    tag = (x - tw / 2, y + 13 * k + 4, x + tw / 2, y + 13 * k + 4 + th)
                    pen = Pen(st, 0, 0, 1)
                    pen.tag(f"tag_{kind}", x, (tag[1] + tag[3]) / 2, st.word(kind), size)
                    st.put(1, pen.svg(), tag, f"tag_{kind}", group=group)
                    connect(st, src, port(st, x, end.y, 0, -1, group), "beam", 2.2, depth=0.6, color=dim, lead=14)
                return


class _Station:
    """The station from outside in its own units, the modules' axis on y = 0, left to right: the shuttle docked
    nose-first at the airlock - a fat drum with a big wheeled hatch; the tools module, a squared box with the robot
    arm on its roof holding the toolbox; the MCP module, a long cylinder with the socket plate on its flank and the
    folded dish on its back; the junction, a sphere with its antenna under it, turned to the services; the scanner
    module inside its big ring with the dark beacon; the command module with its cupola. A truss with solar wings
    runs over the middle four; the trunk, dark, runs along all six. `parts` are the boxes the page keeps clear."""

    MODULES = (("drum", 84, 104), ("box", 112, 86), ("long", 140, 74), ("sphere", 124, 124), ("ring", 96, 80),
               ("cupola", 120, 90))
    COLLAR = 18
    TRUNK_Y = 30

    def __init__(self) -> None:
        self.c = Canvas()
        self.parts: list[tuple[str, tuple[float, float, float, float]]] = []
        xs, x = [], 0.0
        for _, w, _ in self.MODULES:
            xs.append(x + w / 2)
            x += w + self.COLLAR
        top = -max(h for _, _, h in self.MODULES) / 2
        self._truss(xs, top)
        ends = [(x - w / 2, x + w / 2) for x, (_, w, _) in zip(xs, self.MODULES, strict=True)]
        for (_, a), (b, _) in zip(ends, ends[1:], strict=False):            # the docking collars between them
            self.c.shape(rounded_rect_d(a - 4, -16, b - a + 8, 32, 5), P.METAL, sw=2, light=(-1, -2))
            self.c.line(f"M{n((a + b) / 2)},-16 V16", 1.2, INK, 0.5)
        for i, ((kind, w, h), x) in enumerate(zip(self.MODULES, xs, strict=True)):
            getattr(self, f"_{kind}")(x, w, h, LAMPS[i])
            self.parts.append((f"module{i}", (x - w / 2, -h / 2, x + w / 2, h / 2)))
        self._trunk(xs)
        self._shuttle(xs[0] - self.MODULES[0][1] / 2)
        boxes = [b for _, b in self.parts]
        self.extent = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes),
                       max(b[3] for b in boxes))

    # ------------------------------------------------------------------ the structure
    def _truss(self, xs: list[float], top: float) -> None:
        """A lattice truss over modules 2 to 5 on struts, a mast at each end carrying two big solar wings."""
        c = self.c
        ty = top - 26
        x0, x1 = xs[1] - 30, xs[4] + 30
        for mx in (x0 + 16, x1 - 16):                          # the wings, behind the truss
            c.shape(f"M{mx - 3},{ty} V{ty - 150} H{mx + 3} V{ty} Z", P.METAL_DARK, sw=1.4, light=None)
            for side in (-1, 1):
                wx = mx + side * 8 if side > 0 else mx - 8 - 44
                c.shape(rounded_rect_d(wx, ty - 146, 44, 120, 2), P.BLUE, sw=2, light=None)
                c.line(f"M{wx},{ty - 116} h44 M{wx},{ty - 86} h44 M{wx},{ty - 56} h44 M{wx + 22},{ty - 146} v120",
                       1, P.WHITE, 0.8)
            self.parts.append(("wings", (mx - 54, ty - 150, mx + 54, ty)))
        c.shape(f"M{x0},{ty - 8} H{x1} V{ty + 8} H{x0} Z", P.METAL, sw=1.8, light=None)
        c.line(" ".join(f"M{x},{ty - 8} L{x + 12},{ty + 8} L{x + 24},{ty - 8}" for x in range(int(x0), int(x1) - 20,
                                                                                         24)), 1.4, P.METAL_DARK)
        for x in xs[1:5]:
            c.line(f"M{x - 18},{ty + 8} L{x - 10},{top + 14} M{x + 18},{ty + 8} L{x + 10},{top + 14}", 3,
                   P.METAL_DARK)
        self.parts.append(("truss", (x0, ty - 8, x1, ty + 8)))

    def _trunk(self, xs: list[float]) -> None:
        """The trunk along the modules' near flank, dark: the line is not on yet."""
        c = self.c
        left = xs[0] - self.MODULES[0][1] / 2 + 10
        right = xs[-1] + self.MODULES[-1][1] / 2 - 10
        y = self.TRUNK_Y
        c.add(f'<rect x="{n(left)}" y="{y - 6}" width="{n(right - left)}" height="12" fill="{GLASS_DEAD}" '
              f'stroke="{INK}" stroke-width="2"/>')
        c.line(f"M{n(left + 2)},{y - 3} H{n(right - 2)}", 1.4, P.WHITE, 0.5)
        for x in xs:
            c.add(f'<rect x="{n(x - 7)}" y="{y - 9}" width="14" height="18" rx="2" fill="{P.METAL}" stroke="{INK}" '
                  f'stroke-width="1.4"/>')

    def _shuttle(self, port_x: float) -> None:
        """The docking adapter on the airlock's outer end, and the shuttle docked to it nose-first."""
        c = self.c
        c.shape(f"M{port_x + 2},-24 L{port_x - 26},-16 V16 L{port_x + 2},24 Z", P.METAL, sw=2, light=(-1, -1))
        c.add(f'<rect x="{n(port_x - 34)}" y="-20" width="10" height="40" rx="3" fill="{LAMPS[0]}" stroke="{INK}" '
              f'stroke-width="1.6"/>')
        k = 0.8
        sx = port_x - 34 - 100 * k
        c.add(shuttle(sx, 0, k))
        self.parts.append(("shuttle", (sx - 88 * k, -62 * k, port_x, 32 * k)))

    def _windows(self, x: float, w: float, y: float) -> None:
        """A row of small square windows along a module, evenly spaced."""
        count = max(3, int((w - 36) / 22))
        for i in range(count):
            wx = x - (count - 1) * 11 + i * 22
            self.c.add(f'<rect x="{n(wx - 5)}" y="{n(y - 5)}" width="10" height="10" rx="2.5" fill="{P.CHARCOAL}" '
                       f'stroke="{INK}" stroke-width="1.3"/>')
            self.c.line(f"M{n(wx - 3)},{n(y - 1)} l3,-3", 1, P.SCREEN_LIGHT, 0.8)

    def _cylinder(self, x: float, w: float, h: float, color: str) -> None:
        """A pressurised cylinder from the side: rounded ends, a light along its top, ribs, its color band."""
        c = self.c
        left, right = x - w / 2, x + w / 2
        c.shape(rounded_rect_d(left, -h / 2, w, h, min(14, h * 0.2)), P.METAL_PALE, sw=2.6, light=(0, -6),
                shade_k=0.82, stipple=(left, h * 0.18, w, h * 0.3, 16, "down"))
        c.line(f"M{left + 10},{-h / 2 + 7} H{right - 10}", 3, P.WHITE, 0.8)
        for rx in (left + w * 0.3, left + w * 0.7):
            c.line(f"M{n(rx)},{-h / 2 + 1} Q{n(rx + 6)},0 {n(rx)},{h / 2 - 1}", 1.4, INK, 0.4)
        c.add(f'<path d="M{left + 12},{-h / 2 + 1} Q{left + 18},0 {left + 12},{h / 2 - 1} L{left + 21},{h / 2 - 1} '
              f'Q{left + 27},0 {left + 21},{-h / 2 + 1} Z" fill="{color}" stroke="{INK}" stroke-width="1.2"/>')

    # ------------------------------------------------------------------ the modules
    def _drum(self, x: float, w: float, h: float, color: str) -> None:
        """The airlock: short and fat, a big round hatch with its locking wheel in the middle of its flank."""
        self._cylinder(x, w, h, color)
        c = self.c
        c.add(f'<circle cx="{n(x + 6)}" cy="-8" r="24" fill="{P.METAL}" stroke="{INK}" stroke-width="2.2"/>'
              f'<circle cx="{n(x + 6)}" cy="-8" r="15" fill="none" stroke="{INK}" stroke-width="5.6"/>'
              f'<circle cx="{n(x + 6)}" cy="-8" r="15" fill="none" stroke="{P.RED}" stroke-width="3.2"/>')
        c.line(f"M{n(x - 9)},-8 H{n(x + 21)} M{n(x + 6)},-23 V7", 2.4)

    def _box(self, x: float, w: float, h: float, color: str) -> None:
        """The tools module: squared, panelled; the robot arm on its roof holds up the toolbox."""
        c = self.c
        left = x - w / 2
        c.shape(rounded_rect_d(left, -h / 2, w, h, 6), P.METAL_PALE, sw=2.6, light=(0, -6), shade_k=0.82)
        c.line(f"M{n(left + w / 3)},{-h / 2} V{h / 2} M{n(left + 2 * w / 3)},{-h / 2} V{h / 2}", 1.4, INK, 0.4)
        c.add(f'<rect x="{left + 8}" y="{-h / 2 + 1}" width="9" height="{h - 2}" fill="{color}" stroke="{INK}" '
              f'stroke-width="1.2"/>')
        self._windows(x + 6, w - 20, -h * 0.2)
        box = Canvas()
        box.shape(rounded_rect_d(80, -100, 40, 28, 3), P.RED, sw=1.8, light=(-1, -1))
        box.line("M92,-100 V-106 H108 V-100", 2.2)
        c.add(robot_arm(x - 36, -h / 2, 0.55, box.render()))
        self.parts.append(("arm", (x - 44, -h / 2 - 62, x - 36 + 66, -h / 2)))

    def _long(self, x: float, w: float, h: float, color: str) -> None:
        """The MCP module: long; the socket plate on its flank, the dish folded on its back."""
        self._cylinder(x, w, h, color)
        c = self.c
        self._windows(x - 22, w - 70, -h * 0.18)
        px = x + w / 2 - 30
        c.shape(rounded_rect_d(px - 13, -20, 26, 30, 4), P.METAL, sw=2, light=(-1, -1))
        c.add(f'<rect x="{n(px - 8)}" y="-14" width="16" height="18" rx="2" fill="{P.CHARCOAL}" stroke="{INK}" '
              f'stroke-width="1.4"/>')
        for dy in (-10, -5, 0):
            c.dot(px, dy, 1.6, P.METAL_DARK)
        c.add(dish(x - 10, -h / 2, 0.9, False))
        self.parts.append(("dish", (x - 18, -h / 2 - 50, x - 2, -h / 2)))

    def _sphere(self, x: float, w: float, h: float, color: str) -> None:
        """The junction: a round node; its antenna hangs under it, turned down to the services."""
        c = self.c
        r = w / 2
        c.shape(ellipse_d(x, 0, r, r), P.METAL_PALE, sw=2.6, light=(-4, -6), shade_k=0.82)
        c.line(f"M{n(x - r)},0 Q{n(x)},{n(r * 0.3)} {n(x + r)},0 M{n(x)},{n(-r)} Q{n(x + r * 0.3)},0 {n(x)},{n(r)}",
               1.4, INK, 0.4)
        band = (f"M{n(x - r * 0.72)},{n(-r * 0.62)} A{n(r)},{n(r)} 0 0 1 {n(x - r * 0.4)},{n(-r * 0.9)} "
                f"L{n(x - r * 0.34)},{n(-r * 0.78)} A{n(r * 0.86)},{n(r * 0.86)} 0 0 0 "
                f"{n(x - r * 0.62)},{n(-r * 0.5)} Z")
        c.add(f'<path d="{band}" fill="{color}" stroke="{INK}" stroke-width="1.2"/>')
        for i in range(6):                                     # windows round its upper latitude
            a = math.radians(200 + i * 24)
            wx, wy = x + math.cos(a) * r * 0.78, -r * 0.18 + math.sin(a) * r * 0.5
            c.add(f'<rect x="{n(wx - 4.5)}" y="{n(wy - 4.5)}" width="9" height="9" rx="2.5" fill="{P.CHARCOAL}" '
                  f'stroke="{INK}" stroke-width="1.2"/>')
        my = r - 4                                             # the antenna: a mast, a dish opening downward
        c.shape(f"M{n(x - 4)},{n(my)} V{n(my + 20)} H{n(x + 4)} V{n(my)} Z", P.METAL_DARK, sw=1.4, light=None)
        c.shape(f"M{n(x - 28)},{n(my + 40)} Q{n(x)},{n(my + 10)} {n(x + 28)},{n(my + 40)} Z", P.METAL_PALE, sw=2,
                light=(-1, -1))
        c.add(f'<ellipse cx="{n(x)}" cy="{n(my + 40)}" rx="28" ry="5" fill="{P.METAL}" stroke="{INK}" '
              f'stroke-width="1.6"/>')
        c.line(f"M{n(x)},{n(my + 40)} V{n(my + 50)}", 1.6)
        c.dot(x, my + 51, 2.4, P.METAL_DARK)
        self.feed = (x, my + 54)
        self.parts.append(("antenna", (x - 30, my, x + 30, my + 54)))

    def _ring(self, x: float, w: float, h: float, color: str) -> None:
        """The scanner module, passing through its big scanner ring: the ring's far half behind the module, its
        near half in front of it, the beacon dark on its top."""
        c = self.c
        ry = h / 2 + 22
        rx = x - 10
        rw = 20.0                                          # the ring seen nearly edge on

        def hoop(d: str) -> str:
            return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="15" stroke-linecap="round"/>'
                    f'<path d="{d}" fill="none" stroke="{P.METAL_LIGHT}" stroke-width="10" stroke-linecap="round"/>')

        c.add(hoop(f"M{n(rx)},{n(-ry)} A{n(rw)},{n(ry)} 0 0 0 {n(rx)},{n(ry)}"))       # the far half, behind
        self._cylinder(x, w, h, color)
        self._windows(x + 26, 40, -h * 0.2)
        c.add(hoop(f"M{n(rx)},{n(-ry)} A{n(rw)},{n(ry)} 0 0 1 {n(rx)},{n(ry)}"))       # the near half, in front
        c.add(beacon(rx, -ry - 6, 0.8, False))
        self.parts.append(("ring", (rx - rw - 8, -ry - 26, rx + rw + 8, ry + 8)))

    def _cupola(self, x: float, w: float, h: float, color: str) -> None:
        """The command module: the cupola of windows on its roof, from where the valves are watched."""
        self._cylinder(x, w, h, color)
        c = self.c
        self._windows(x - 20, w - 60, -h * 0.16)
        cx, base = x + 20, -h / 2
        c.shape(f"M{cx - 34},{base} L{cx - 26},{base - 30} H{cx + 26} L{cx + 34},{base} Z", P.METAL, sw=2.4,
                light=(-2, -3))
        for i in range(4):                                     # its window panes, trapezoids side by side
            a, b = cx - 22 + i * 11, cx - 22 + (i + 1) * 11
            c.add(f'<path d="M{a + 1},{base - 26} H{b - 1} L{b + (i - 1.5) * 1.4},{base - 6} '
                  f'H{a + (i - 1.5) * 1.4} Z" fill="{P.SCREEN}" stroke="{INK}" stroke-width="1.3"/>')
        self.parts.append(("cupola", (cx - 36, base - 32, cx + 36, base)))


SPACE.stations.extend([
    Station("task", task, ("work", "puzzle")),
    Station("tools", tools, ("work",)),
    Station("mcp", mcp, ("work", "spark")),
    Station("services", services, ("send", "return")),
    Station("check", check, ("scan", "alarm")),
    Station("panel", panel, ("work", "button")),
])
SPACE.backdrop = backdrop
SPACE.finale = finale
SPACE.alternate = True                                       # never one moment on two pages in a row
stories.OPENERS["station"] = opener
hide(SPACE, "tools", "work")

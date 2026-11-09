"""The kitchen in the morning: the world of chapter 1 (why an agent writes slop).

The kitchen is the repository and the pie is the agent's work. The counter runs along the back wall at the same
height in every frame, so the pages join up into one kitchen; the pantry over it holds what the agent could cook
with - fresh jars of prompts, skills, hooks, MCP, subagents and checks - and, on the low shelf nearest to hand,
old dusty jars of copy-paste, legacy and crutches. The chapter's idea is the pie's story - an agent that is not
told how this house cooks takes whatever is nearest, and the result is slop; written house rules fix it:

1. recipe   the professor pins the task, a recipe card, on the cork board over the counter - or the agent stands
            reading it, puzzled: nobody told it how this house cooks;
2. pantry   the agent takes what is nearest: a dusty jar of copy-paste off the low shelf, while the fresh jars stand
            labelled above - it imitates the old code nearest to hand;
3. oven     the pie in the oven of the stove, its window glowing; then the timer rings and smoke comes out;
4. slop     out comes a lopsided, burnt pie; the cat holds a magnifier over it next to the recipe card's picture;
5. fridge   the professor writes the house rules on a note - AGENTS.md - and pins it to the fridge with a magnet;
6. good     the agent bakes again with the rules pinned next to the recipe and the fresh jars by the bowl - and
            serves an even pie; the caterpillar checks it off her list, while the sparrow is after the big red
            button of the mixer under its cover (he gets to press it only in the last chapter of the book).

No name boards in the frames: every thing says what it is by itself (an oven needs no label
saying it is an oven); only the finale names its stations. A tall frame shows more of the wall: the window with the
sunrise and the clock at 4:04 (every clock in the book shows it). It draws with the shared kit (`world_kit.py`) and
keeps its two rules: containers and ports.
"""
from __future__ import annotations

import math

from .. import design as P
from ..design import darken, lighten, mix
from . import handheld, props, sets
from .characters import module as char_module
from .footers import Strip
from .ink import INK, Canvas, ellipse_d, lettering, lettering_width, n, rounded_rect_d
from .openers import CLEAR_MM, H, OPENERS, W, Stage
from .scenes import PROFESSOR_HEIGHT
from .world_kit import (GAP_MIN, SIZE, Holder, Pen, Room, cast, clock_hands, hide, ledger, letter, room,
                        stash_along, tag_size, wrap)
from .world_base import Station, world

KITCHEN = world("kitchen", opener="kitchen")

_at = sets._at

LOW_CAST = ("agent", "cat", "caterpillar")      # who stands in a low frame: the professor, the tallest, is left out
UPPER = mix(P.PINK, P.CARD, 0.55)               # the wall cupboards, in the chapter's colour, calmer than the station
UPPER_DARK = mix(P.PINK, P.WOOD_DARK, 0.35)
GLASS_PANE = mix(P.LENS, P.CARD, 0.55)


class Counter(Room):
    """A stretch of the kitchen in a frame: the room, plus the counter's height - the professor's waist, set back at
    the wall behind the cast."""

    def __init__(self, s: Strip) -> None:
        super().__init__(s)
        self.ceil = 0.0                                   # a kitchen has no hull: the wall goes up to the frame's top
        self.wall = self.floor
        self.counter = self.floor - s.tall * 0.5          # the counter's top
        self.surf = self.counter
        self.tile = max(8.0, s.tall * 0.075)              # a splashback tile
        self.splash = self.counter - self.tile * 3        # the splashback's top


def bench(s: Strip) -> Counter:
    return room(s, Counter)


# ============================================================================ the camera
def low(s: Strip) -> bool:
    """A low frame - a strip or a mid strip - is a close-up: the cast nearly fills its height and the professor (the
    tallest) is left out, so the others stand big; a station shows only what stands there at its true size."""
    return s.h < 300


def camera(s: Strip, index: int) -> None:
    """The kitchen's camera, close (the fair's, `world_fair.zoom`): the cast and the counter fill the frame's height,
    the floor a sixth under their feet. In a low frame the tallest of those standing there nearly fills it. Every
    other page the camera steps back and the station swaps sides (`mirror`); a station whose thing is tall - the
    fridge, as tall as the professor - sets the scale so it stands whole."""
    from .world_fair import zoom
    zoom(s)
    s.again = (s.seed // 2) % 2 == 1
    s.mirror = bool(s.shot) != s.again
    feet = s.feet(0)
    names = LOW_CAST if low(s) else ("professor", *LOW_CAST)
    if low(s):
        top = max(_box(s, name, 0, feet)[3] - _box(s, name, 0, feet)[1] for name in names)
        s.tall *= (feet - 6) / top
        if s.shot:                                        # the other camera, a step back
            s.tall *= 0.88
    key = KITCHEN.stations[index].key if 0 <= index < len(KITCHEN.stations) else ""
    share = 0.25 if key == "fridge" else 0.19             # the narrow fridge leaves its cast more room
    widest = max(_box(s, name, 0, feet)[2] - _box(s, name, 0, feet)[0] for name in names)
    s.tall *= min(1.0, (s.hi - s.lo) * share / widest)    # two of them take two fifths of the width at most
    if key == "fridge":
        s.tall = min(s.tall, (s.base - 8) / (0.5 * FRIDGE_TALL))   # the fridge whole under the frame's top
    s.unit = s.tall / 137


def X(s: Strip, frac: float) -> float:
    """A place across the frame, the station's way round: mirrored on a mirrored page."""
    x = s.x(frac)
    return s.lo + s.hi - x if getattr(s, "mirror", False) else x


def _upright(s: Strip, actor) -> float:
    """How far to turn a thing held in the right fist so it stands upright on the page, whatever the forearm's
    slant (a drawn-mirrored hand is mirrored back)."""
    angle = s.grip(actor, "right")[2]
    return -(180 - angle if actor.flip else angle)


def who(s: Strip, name: str, alt: str) -> str:
    """`name`, or `alt` in a low frame when `name` is the professor."""
    return alt if name == "professor" and low(s) else name


# ============================================================================ the room
def backdrop(s: Strip, index: int) -> None:
    """The kitchen behind a station: the warm wall, the tiled splashback over the counter, the floor of square tiles
    in two tones running back to the wall. The counter and its cabinets, the wall cupboards in the chapter's pink,
    the window and the clock go in after the station (`finish`), round what it has put there."""
    ledger(s)
    camera(s, index)
    s.index = index
    _walls(s, index)


def _walls(s: Strip, index: int) -> None:
    """The wall, the splashback and the floor, for the frame's scale as the camera set it."""
    c, r = s.back, bench(s)
    c.add(f'<rect x="-6" y="-6" width="{W + 12}" height="{n(r.floor + 8)}" fill="{P.KITCHEN_WALL}"/>')
    tile, splash = r.tile, r.splash
    c.add(f'<rect x="-6" y="{n(splash)}" width="{W + 12}" height="{n(r.counter - splash)}" fill="{P.KITCHEN_TILE}"/>')
    rows = " ".join(f"M-6,{n(splash + i * tile)} H{W + 6}" for i in range(4))
    cols = " ".join(f"M{n(x)},{n(splash)} V{n(r.counter)}" for x in _range(-((index * 37) % tile), W, tile))
    c.line(f"{rows} {cols}", 1, darken(P.KITCHEN_TILE, 0.82))
    _floor(s, r)
    s.niches = []                                         # where the stove and the fridge stand in the row


def _range(start: float, stop: float, step: float) -> list[float]:
    out, x = [], start
    while x < stop:
        out.append(x)
        x += step
    return out


def _floor(s: Strip, r: Counter) -> None:
    """Square tiles in two tones laid on the floor and seen from a little above: the rows grow towards the front and
    the joints across run to a point far behind the wall, so the floor lies flat; a skirting along the wall."""
    c = s.back
    top, bottom = r.floor, s.h + 4
    c.add(f'<rect x="-6" y="{n(top)}" width="{W + 12}" height="{n(bottom - top)}" fill="{P.KITCHEN_FLOOR}"/>')
    depth = bottom - top
    vy = top - depth * 1.6                                # where the joints across would meet
    mid = W / 2
    near = max(20.0, s.tall * 0.22)                       # a tile at the front
    y, row, cells = top, 0, []

    def scale(yy: float) -> float:
        return (yy - vy) / (bottom - vy)
    while y < bottom:
        h = max(3.0, near * scale(y))
        ya, yb = y, min(bottom, y + h)
        sa, sb = scale(ya), scale(yb)
        u = math.floor((-6 - mid) / sa / near) * near
        col = 0
        while mid + u * sb < W + 6 + near:
            if (row + col + int(u / near)) % 2:
                pts = [(mid + u * sa, ya), (mid + (u + near) * sa, ya), (mid + (u + near) * sb, yb),
                       (mid + u * sb, yb)]
                cells.append(f'<path d="M{" L".join(f"{n(px)},{n(py)}" for px, py in pts)} Z" '
                             f'fill="{P.KITCHEN_FLOOR_DARK}" fill-opacity=".6"/>')
            u += near
            col += 0
        y += h
        row += 1
    c.add("".join(cells))
    joints = []                                           # the joints between the tiles
    yy = top
    while yy < bottom:
        joints.append(f"M-6,{n(yy)} H{W + 6}")
        yy += max(3.0, near * scale(yy))
    for u in _range(-W * 3, W * 3, near):
        x0, x1 = mid + u * scale(top), mid + u * scale(bottom)
        if -40 < x1 < W + 40 or -40 < x0 < W + 40:
            joints.append(f"M{n(x0)},{n(top)} L{n(x1)},{n(bottom)}")
    c.line(" ".join(joints), 0.8, darken(P.KITCHEN_FLOOR_DARK, 0.8), 0.5)
    sk = max(3.0, s.tall * 0.025)                         # the skirting board along the wall
    c.add(f'<rect x="-6" y="{n(top - sk)}" width="{W + 12}" height="{n(sk + 1)}" fill="{P.WOOD}" stroke="{INK}" '
          f'stroke-width="1.2"/>')


def counter_row(c: Canvas, top: float, floor: float, niches: list[tuple[float, float]],
                width: float = W, door: float | None = None) -> None:
    """The counter along the back wall: base cabinets on a dark plinth, a row of drawers under the worktop and the
    doors under them, each with its handle, the worktop over all with its front edge - broken where the stove and
    the fridge stand (`niches`, their left and right): the row ends at each appliance's sides, and each run of
    cabinets between them gets whole doors, as many as fit."""
    cuts = sorted(niches)
    runs, x = [], -4.0
    for left, right in cuts:
        if left > x:
            runs.append((x, left))
        x = max(x, right)
    if x < width + 4:
        runs.append((x, width + 4))
    tall = floor - top
    gap = max(2.0, tall * 0.035)
    plinth = max(3.0, tall * 0.07)
    edge = max(3.0, tall * 0.06)                          # the worktop's front edge
    drawer = (tall - plinth - edge) * 0.24
    door = door or max(46.0, tall * 0.9)
    for x0, x1 in runs:
        if x1 - x0 < 4:
            continue
        c.add(f'<rect x="{n(x0)}" y="{n(top)}" width="{n(x1 - x0)}" height="{n(floor - top)}" '
              f'fill="{P.KITCHEN_CABINET}" stroke="{INK}" stroke-width="2"/>')
        c.add(f'<rect x="{n(x0)}" y="{n(floor - plinth)}" width="{n(x1 - x0)}" height="{n(plinth)}" '
              f'fill="{darken(P.KITCHEN_CABINET, 0.6)}" stroke="{INK}" stroke-width="1.4"/>')   # the plinth
        count = max(1, round((x1 - x0) / door))
        dw = (x1 - x0) / count
        if dw > 4 * gap:
            for i in range(count):
                dx = x0 + i * dw
                face = lighten(P.KITCHEN_CABINET, 0.12)
                dy0, dy1 = top + edge + gap, top + edge + drawer
                c.add(f'<rect x="{n(dx + gap)}" y="{n(dy0)}" width="{n(dw - 2 * gap)}" height="{n(dy1 - dy0)}" '
                      f'rx="{n(gap)}" fill="{face}" stroke="{INK}" stroke-width="1.2"/>')        # the drawer
                hw = min(dw * 0.3, max(8.0, tall * 0.14))
                c.add(f'<rect x="{n(dx + dw / 2 - hw / 2)}" y="{n((dy0 + dy1) / 2 - 1.5)}" width="{n(hw)}" '
                      f'height="3" rx="1.5" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width=".6"/>')
                ty0, ty1 = dy1 + gap, floor - plinth - gap
                c.add(f'<rect x="{n(dx + gap)}" y="{n(ty0)}" width="{n(dw - 2 * gap)}" height="{n(ty1 - ty0)}" '
                      f'rx="{n(gap)}" fill="{face}" stroke="{INK}" stroke-width="1.3"/>')        # the door
                c.add(f'<rect x="{n(dx + gap * 2.5)}" y="{n(ty0 + gap * 1.5)}" width="{n(dw - 5 * gap)}" '
                      f'height="{n(ty1 - ty0 - 3 * gap)}" rx="{n(gap)}" fill="none" '
                      f'stroke="{darken(P.KITCHEN_CABINET, 0.8)}" stroke-width="1"/>')           # its panel
                hx = dx + dw - gap * 3.5 if i % 2 == 0 else dx + gap * 3.5   # the door's handle by its free edge
                hh = min((ty1 - ty0) * 0.3, max(8.0, tall * 0.14))
                c.add(f'<rect x="{n(hx - 1.5)}" y="{n(ty0 + gap * 2.5)}" width="3" height="{n(hh)}" rx="1.5" '
                      f'fill="{P.METAL_DARK}" stroke="{INK}" stroke-width=".6"/>')
        c.add(f'<rect x="{n(x0)}" y="{n(top - 2)}" width="{n(x1 - x0)}" height="{n(edge + 2)}" '
              f'fill="{P.WOOD_LIGHT}" stroke="{INK}" stroke-width="1.6"/>')                    # the worktop
        c.line(f"M{n(x0)},{n(top + edge * 0.4)} H{n(x1)}", 1, P.WOOD, 0.8)


def _counter(s: Strip, r: Counter) -> None:
    """The counter across the frame, around whatever appliances the station has put in it."""
    big = (r.floor - r.counter) * 1.5 if strip(s) else None   # a close-up: fewer, bigger doors
    counter_row(s.back, r.counter, r.floor, getattr(s, "niches", []), door=big)


def _upper_wall(s: Strip, r: Counter, index: int) -> None:
    """The window onto the sunrise and the clock (at 4:04, like every clock in the book), where the wall over the
    splashback is still free."""
    top = r.splash - 6
    room_h = top - 30
    if room_h < 100:
        return
    w = min(s.tall * 0.62, room_h * 0.9)
    h = min(room_h - 24, w * 1.1)
    prefer = (W * 0.72, W * 0.3, W * 0.62, W * 0.26, W * 0.7, W * 0.34)[index % 6]
    spots = sorted(_range(s.lo + w / 2 + 14, s.hi - w / 2 - 14, 20), key=lambda x: abs(x - prefer))
    placed = None
    for scale in (1.0, 0.85, 0.7):
        ww, hh = w * scale, h * scale
        for wx in spots:
            box = (wx - ww / 2 - 12, top - hh - 24, wx + ww / 2 + 12, top - 12)
            if box[1] > 2 and s.free(box, 24):
                s.put(0.3, sets.window_morning(wx, top - hh - 14, ww, hh), box, "window")
                placed = box
                break
        if placed:
            break
    ck = max(1.0, min(2.2, s.tall / 150))
    cy = top - room_h * 0.55
    for cx in (W * 0.5, W * 0.2, W * 0.8, W * 0.35, W * 0.65, W * 0.1, W * 0.9):
        clock = (cx - 26 * ck, cy - 26 * ck, cx + 26 * ck, cy + 26 * ck)
        if clock[1] > 4 and s.free(clock, 10):
            s.put(0.3, wall_clock(cx, cy, ck), clock, "clock")
            break


def wall_clock(x: float, y: float, k: float) -> str:
    """A round kitchen clock showing 4:04, as every clock in the book does (`world_kit.CLOCK_TIME`)."""
    c = Canvas()
    c.shape(ellipse_d(0, 0, 24, 24), P.RED, sw=2.2, light=None)
    c.shape(ellipse_d(0, 0, 19, 19), P.CARD, sw=1.6, light=None)
    for i in range(12):
        a = math.radians(i * 30)
        c.line(f"M{n(math.sin(a) * 15)},{n(-math.cos(a) * 15)} L{n(math.sin(a) * 17)},{n(-math.cos(a) * 17)}", 1.2)
    c.add(clock_hands(0, 0, 9, 14, 1.7))
    c.dot(0, 0, 2)
    return _at(c, x, y, k)


def cupboard(x: float, bottom: float, w: float, h: float, seed: int = 0) -> str:
    """A wall cupboard in the chapter's pink hung over the splashback, its foot's middle at (x, bottom): a cornice
    on top, two doors with glass panes and knobs, plates standing and cups on the shelf seen through the glass."""
    c = Canvas()
    left, top = x - w / 2, bottom - h
    c.shape(rounded_rect_d(left, top, w, h, 3), UPPER, sw=1.8, light=(-1, -1), shade_k=0.9)
    c.add(f'<rect x="{n(left - 3)}" y="{n(top - 4)}" width="{n(w + 6)}" height="5" rx="1.5" fill="{UPPER_DARK}" '
          f'stroke="{INK}" stroke-width="1.3"/>')                                              # the cornice
    pad = max(3.0, w * 0.06)
    dw = (w - 3 * pad) / 2
    for j in range(2):
        dx = left + pad + j * (dw + pad)
        c.add(f'<rect x="{n(dx)}" y="{n(top + pad)}" width="{n(dw)}" height="{n(h - 2 * pad)}" rx="2" '
              f'fill="{lighten(UPPER, 0.15)}" stroke="{INK}" stroke-width="1.2"/>')            # a door
        gx0, gy0, gx1, gy1 = dx + pad * 0.7, top + pad * 1.7, dx + dw - pad * 0.7, bottom - pad * 1.7
        c.add(f'<rect x="{n(gx0)}" y="{n(gy0)}" width="{n(gx1 - gx0)}" height="{n(gy1 - gy0)}" rx="1.5" '
              f'fill="{GLASS_PANE}" stroke="{INK}" stroke-width="1"/>')                       # its glass
        shelf = gy0 + (gy1 - gy0) * 0.52
        c.line(f"M{n(gx0)},{n(shelf)} H{n(gx1)}", 1.2, UPPER_DARK)
        pr = min((gx1 - gx0) * 0.2, (shelf - gy0) * 0.42)                                   # plates on edge
        for i in range(3):
            px = gx0 + (gx1 - gx0) * (0.22 + i * 0.28)
            c.add(f'<ellipse cx="{n(px)}" cy="{n(shelf - pr - 0.5)}" rx="{n(pr * 0.45)}" ry="{n(pr)}" '
                  f'fill="{P.WHITE}" stroke="{INK}" stroke-width=".9"/>')
        cw = min((gx1 - gx0) * 0.26, (gy1 - shelf) * 0.5)                                 # cups below
        for i in range(2):
            ux = gx0 + (gx1 - gx0) * (0.3 + i * 0.4)
            cup = P.RED if (i + j + seed) % 2 else P.KITCHEN_CABINET
            c.add(f'<path d="M{n(ux - cw / 2)},{n(gy1 - cw)} H{n(ux + cw / 2)} L{n(ux + cw * 0.4)},{n(gy1 - 1)} '
                  f'H{n(ux - cw * 0.4)} Z" fill="{cup}" stroke="{INK}" stroke-width=".9"/>')
        kx = dx + dw - pad * 0.9 if j == 0 else dx + pad * 0.9                           # the knobs, by the meeting
        c.add(f'<circle cx="{n(kx)}" cy="{n(top + h / 2)}" r="{n(max(1.6, w * 0.02))}" fill="{P.METAL_DARK}" '
              f'stroke="{INK}" stroke-width=".7"/>')
    return c.render()


def furnish(s: Strip, r: Counter) -> None:
    """The back wall's own row, put in last round what the station has placed: in a tall frame, runs of pink wall
    cupboards with glass doors over the splashback wherever the wall is free, each run as many cupboards side by
    side as fit, so the wall reads as one fitted kitchen. A low frame has no wall to spare: its counter is its row."""
    if s.h < 300:
        return
    bottom = r.splash - max(4.0, r.tile * 0.5)
    h = min(bottom - max(10.0, s.h * 0.05), s.tall * 0.5)
    if h < 40:
        return
    unit = h * 0.85
    band = (bottom - h - 6, bottom)
    step = 4.0
    xs = [x for x in _range(s.lo, s.hi - step, step) if s.free((x, band[0], x + step, band[1]), 10)]
    runs: list[list[float]] = []
    for x in xs:
        if runs and abs(x - runs[-1][1]) < 0.5:
            runs[-1][1] = x + step
        else:
            runs.append([x, x + step])
    for a, b in runs:
        count = int((b - a) / unit)
        if count < 1:
            continue
        width = count * unit
        x0 = a + ((b - a) - width) / 2
        c = "".join(cupboard(x0 + unit * (i + 0.5), bottom, unit, h, seed=i + int(x0)) for i in range(count))
        s.put(0.4, c, (x0 - 3, bottom - h - 5, x0 + width + 3, bottom), "cupboard")


def finish(s: Strip, index: int) -> None:
    """What every frame ends with: the counter around the appliances, then, in a tall frame, the window and the clock
    where the wall is still free, then the wall cupboards - after the station's own things, so they never cover
    them."""
    r = bench(s)
    if strip(s):
        larder(s, r)
    _counter(s, r)
    if s.h >= 300:
        _upper_wall(s, r, index)
    furnish(s, r)


def strip(s: Strip) -> bool:
    """A strip, the lowest frame: a close-up of the station and its cast together in the middle."""
    return s.h < 200


def wall_gap(s: Strip, r: Counter, x0: float, x1: float) -> None:
    """A stretch of bare wall with no counter in front of it - where a board hangs low or shelves stand on the
    floor: the row of cabinets breaks there and the splashback with it."""
    s.niches.append((x0, x1))
    s.back.add(f'<rect x="{n(x0)}" y="{n(r.splash - 1)}" width="{n(x1 - x0)}" height="{n(r.counter - r.splash + 2)}" '
               f'fill="{P.KITCHEN_WALL}"/>')


def larder(s: Strip, r: Counter) -> None:
    """A tall pink larder cupboard standing in the row of a strip, where the floor is free, so the run of counter
    breaks: two tall doors, their knobs, a cornice, the gap of its plinth."""
    h = r.floor - 4
    w = h * 0.46
    for x in sorted((s.lo + w / 2 + 4 + i * 8 for i in range(int((s.hi - s.lo - w) / 8))),
                    key=lambda x_: -abs(x_ - W / 2)):
        box = (x - w / 2, r.floor - h, x + w / 2, r.floor)
        if not s.free(box, 10):
            continue
        c = Canvas()
        c.shape(rounded_rect_d(x - w / 2, r.floor - h, w, h, 3), UPPER, sw=1.8, light=(-1, -1), shade_k=0.9)
        c.add(f'<rect x="{n(x - w / 2 - 2)}" y="{n(r.floor - h)}" width="{n(w + 4)}" height="4" rx="1.5" '
              f'fill="{UPPER_DARK}" stroke="{INK}" stroke-width="1.2"/>')
        pad = max(2.5, w * 0.07)
        dw = (w - 3 * pad) / 2
        for j in range(2):
            dx = x - w / 2 + pad + j * (dw + pad)
            c.add(f'<rect x="{n(dx)}" y="{n(r.floor - h + pad + 3)}" width="{n(dw)}" height="{n(h - 2 * pad - 9)}" '
                  f'rx="2" fill="{lighten(UPPER, 0.15)}" stroke="{INK}" stroke-width="1.2"/>')
            kx = dx + dw - pad * 0.8 if j == 0 else dx + pad * 0.8
            c.add(f'<rect x="{n(kx - 1.2)}" y="{n(r.floor - h * 0.55)}" width="2.4" height="{n(h * 0.1)}" rx="1.2" '
                  f'fill="{P.METAL_DARK}" stroke="{INK}" stroke-width=".6"/>')
        c.add(f'<rect x="{n(x - w / 2 + 2)}" y="{n(r.floor - 5)}" width="{n(w - 4)}" height="5" '
              f'fill="{UPPER_DARK}"/>')
        s.niches.append((box[0] - 1, box[2] + 1))
        s.put(r.floor - 2, c.render(), box, "larder", group="larder")
        return


# ============================================================================ things
def kitchen_table(x: float, y: float, k: float = 1.0, w: float = 110, color: str = P.WOOD_LIGHT,
                  cloth: str | None = P.RED) -> str:
    """A small table 46 high; `cloth` hangs a checked tablecloth over it."""
    c = Canvas()
    hw = w / 2
    c.line(f"M{-hw + 8},0 V-42 M{hw - 8},0 V-42", 4.5, P.WOOD_DARK)
    c.shape(rounded_rect_d(-hw, -48, w, 8, 2), color, sw=2, light=None)
    if cloth:
        clip = c.shape(f"M{-hw - 4},-48 H{hw + 4} V-30 Q{hw},-26 {hw - 8},-30 Q0,-24 {-hw + 8},-30 Q{-hw},-26 "
                       f"{-hw - 4},-30 Z", P.WHITE, sw=1.8, light=None, clip=True)
        checks = "".join(f'<rect x="{-hw - 4 + i * 10}" y="-50" width="5" height="26" fill="{cloth}" opacity=".7"/>'
                         for i in range(int(w / 10) + 2))
        c.add(f'<g clip-path="url(#{clip})">{checks}<rect x="{-hw - 4}" y="-41" width="{w + 8}" height="4" '
              f'fill="{cloth}" opacity=".5"/></g>')
        c.path(f"M{-hw - 4},-48 H{hw + 4} V-30 Q{hw},-26 {hw - 8},-30 Q0,-24 {-hw + 8},-30 Q{-hw},-26 "
               f"{-hw - 4},-30 Z", "none", 1.8)
    return props._at(c, x, y, k)


def pie(x: float, y: float, k: float, kind: str = "good") -> str:
    """A pie in its tin, the middle of the tin's foot at (x, y), 64 wide: "raw" (pale dough, a lattice), "good"
    (golden, even, the lattice browned, a wisp of steam) or "bad" (lopsided, one side slumped, burnt on top, the
    filling run over the tin)."""
    c = Canvas()
    if kind == "bad":
        c.shape("M-30,-10 Q-36,-18 -20,-26 Q-6,-40 8,-24 Q20,-22 31,-10 Z", mix(P.CRUST, P.CRUST_BURNT, 0.45),
                sw=2, light=(-2, -2), shade_k=0.8)
        c.add(f'<path d="M-14,-28 Q-6,-36 4,-27 Q-2,-22 -12,-24 Z" fill="{P.CRUST_BURNT}" stroke="{INK}" '
              f'stroke-width="1.2"/>')                                          # the burnt patch on top
        c.line("M-22,-18 L-14,-22 L-8,-17 M8,-20 L14,-15", 1.4)                 # cracks
        c.shape("M22,-10 Q26,-6 25,-1 Q23,2 21,-1 Q21,-6 18,-10 Z", P.RED, sw=1.2, light=None)   # filling run over
    else:
        crust = P.CRUST if kind == "good" else P.CRUST_RAW
        c.shape("M-30,-10 Q-30,-30 0,-30 Q30,-30 30,-10 Z", crust, sw=2, light=(-2, -2), shade_k=0.85)
        lattice = darken(crust, 0.85)
        c.line("M-22,-12 L-10,-27 M-8,-11 L6,-29 M8,-11 L20,-25 M-24,-20 H24", 1.6, lattice)
        if kind == "good":
            c.line("M-4,-34 q-4,-5 0,-10 q4,-5 0,-10 M6,-34 q4,-5 0,-9", 1.6, P.METAL, 0.8)
    c.shape("M-33,-10 L-29,0 H29 L33,-10 Z", P.METAL_LIGHT, sw=1.8, light=None)    # the tin
    c.line(" ".join(f"M{x0},-10 l2,4" for x0 in range(-28, 29, 7)), 1, INK, 0.5)   # its crimped rim
    return _at(c, x, y, k)


def tin(x: float, y: float, k: float) -> str:
    """An empty pie tin, waiting for the dough."""
    c = Canvas()
    c.shape("M-33,-10 L-29,0 H29 L33,-10 Z", P.METAL_LIGHT, sw=1.8, light=(-1, -1))
    c.line(" ".join(f"M{x0},-10 l2,4" for x0 in range(-28, 29, 7)), 1, INK, 0.5)
    return _at(c, x, y, k)


def recipe(pen: Pen, name: str, left: float, top: float, word: str, k: float, inside: Holder | None = None) -> Holder:
    """The recipe card, its top left at (left, top) in the pen's units: a white card, its title on a tag, the picture
    of the pie as it should be and three lines of method under it."""
    size = letter(k, 11.0)
    tw, th = tag_size(word, size, k)
    pic_w, pic_h = 64.0, 34.0
    gap = GAP_MIN / k + 2
    inner_w = max(tw, pic_w + 4)
    inner_h = th + gap + pic_h + gap + 14
    w, h = wrap(inner_w, k), wrap(inner_h, k)
    card = pen.container(name, left, top, w, h, P.CARD, radius=3, sw=1.8, light=None)
    pad = pen.pad(w, h)
    cx = left + w / 2
    pen.tag(f"{name}_title", cx, top + pad + th / 2, word, size, P.YELLOW_PALE, inside=card)
    py = top + pad + th + gap + pic_h
    pen.c.add(pie(cx, py, 1.0, "good"))
    pen.child(card, f"{name}_picture", cx - 34, py - 34, cx + 34, py)
    ly = py + gap + 3
    pen.c.line(f"M{n(cx - 26)},{n(ly)} H{n(cx + 26)} M{n(cx - 26)},{n(ly + 5)} H{n(cx + 18)} "
               f"M{n(cx - 26)},{n(ly + 10)} H{n(cx + 22)}", 1.4, INK, 0.55)
    pen.child(card, f"{name}_lines", cx - 27, ly - 1, cx + 27, ly + 11)
    if inside is not None:
        inside.children.append((name, card.outer))
    return card


def recipe_size(k: float, word: str) -> tuple[float, float]:
    size = letter(k, 11.0)
    tw, th = tag_size(word, size, k)
    gap = GAP_MIN / k + 2
    return wrap(max(tw, 68.0), k), wrap(th + gap + 34 + gap + 14, k)


def rules(pen: Pen, name: str, left: float, top: float, word: str, k: float) -> Holder:
    """The house rules on a note: a yellow sheet, its title on a tag, four ruled items each with its bullet."""
    size = letter(k, 10.0)
    tw, th = tag_size(word, size, k)
    gap = GAP_MIN / k + 2
    items = 4
    w, h = wrap(max(tw, 72.0), k), wrap(th + gap + items * 9, k)
    note = pen.container(name, left, top, w, h, P.YELLOW_PALE, radius=2, sw=1.8, light=None)
    pad = pen.pad(w, h)
    cx = left + w / 2
    pen.tag(f"{name}_title", cx, top + pad + th / 2, word, size, P.CARD, inside=note)
    y0 = top + pad + th + gap + 4
    lx0, lx1 = left + pad + 2, left + w - pad - 2
    for i in range(items):
        y = y0 + i * 9
        pen.c.add(f'<circle cx="{n(lx0 + 2.5)}" cy="{n(y)}" r="2.2" fill="{INK}"/>')
        pen.c.line(f"M{n(lx0 + 8)},{n(y)} H{n(lx1 - (i % 2) * 10)}", 1.6, INK, 0.6)
    pen.child(note, f"{name}_items", lx0, y0 - 3, lx1, y0 + (items - 1) * 9 + 3)
    return note


def rules_size(k: float, word: str) -> tuple[float, float]:
    size = letter(k, 10.0)
    tw, th = tag_size(word, size, k)
    gap = GAP_MIN / k + 2
    return wrap(max(tw, 72.0), k), wrap(th + gap + 36, k)


CONTENTS = (P.AMBER, P.GREEN, P.PINK)                 # what is seen through a jar's glass, in turn
OLD_KINDS = ("pasta", "dusty", "crate")               # the low shelf: a pack of pasta, a dusty jar, a crate


def kind_of(label: str, old: int | None = None) -> str:
    """How a pantry thing is kept: a short name in a glass jar, a long one in a red tin with white polka dots, the
    way the old kitchen tins were; the old ones each in their own shabby way - copy-paste is
    a pack of pasta, gone dusty."""
    if old is not None:
        return OLD_KINDS[old % len(OLD_KINDS)]
    return "jar" if len(label) <= 5 else "tin"


LABEL_GROW = 1.15      # labels on the goods are set this much above the shelf's lettering size: the hand face is thin


def goods_width(label: str, kind: str, size: float) -> float:
    lw = lettering_width(label, size * LABEL_GROW, "label")
    return {"jar": max(28.0, lw + 20), "tin": max(36.0, lw + 24), "pasta": max(30.0, lw + 20),
            "dusty": max(28.0, lw + 20), "crate": max(36.0, lw + 22)}[kind]   # the label never at the edges


def goods_height(kind: str, size: float) -> float:
    """From the shelf to the top of the lid, the crutches or the bag's fold."""
    return {"jar": max(30.0, size * 2.4) + 7, "tin": max(44.0, size * 3.6) + 9, "pasta": max(40.0, size * 3.4) + 12,
            "dusty": max(30.0, size * 2.4) + 7, "crate": max(26.0, size * 2.2) + 16}[kind]


def _label(c: Canvas, x: float, y: float, label: str, size: float, turn: float = 0, paper: str = P.WHITE) -> tuple:
    size *= LABEL_GROW
    lw = lettering_width(label, size, "label")
    lab_h = size * 1.45
    c.add(f'<g transform="rotate({turn} {n(x)} {n(y)})"><rect x="{n(x - lw / 2 - 3)}" y="{n(y - lab_h / 2)}" '
          f'width="{n(lw + 6)}" height="{n(lab_h)}" rx="{n(lab_h * 0.3)}" fill="{paper}" stroke="{INK}" '
          f'stroke-width="1"/>{lettering(x, y + size * 0.36, label, size, INK, style="label")}</g>')
    return (x - lw / 2 - 4, y - lab_h / 2 - 2, x + lw / 2 + 4, y + lab_h / 2 + 2)


def goods(c: Canvas, x: float, y: float, label: str, kind: str, size: float,
          nth: int = 0) -> tuple[float, float, float, float]:
    """A thing on the pantry shelf standing at (x, y), labelled: "jar" - glass, what is in it seen through, a
    coloured lid; "tin" - a tall red tin in white polka dots, its name on a white plate; "pasta" - an old pack of
    spaghetti with a window, the dry sticks poking out of its top; "dusty" - an old jar gone grey, its label
    crooked and yellowed; "crate" - a wooden crate with crutches sticking out of it. Returns its box."""
    w, h = goods_width(label, kind, size), goods_height(kind, size)
    if kind == "jar":
        body = h - 7
        c.shape(rounded_rect_d(x - w / 2, y - body, w, body, 5), lighten(P.LENS, 0.45), sw=1.8, light=None)
        fill = CONTENTS[nth % len(CONTENTS)]
        c.add(f'<rect x="{n(x - w / 2 + 2.5)}" y="{n(y - body * 0.7)}" width="{n(w - 5)}" '
              f'height="{n(body * 0.7 - 2.5)}" rx="3" fill="{fill}" fill-opacity=".75"/>')
        c.shape(rounded_rect_d(x - w / 2 + 2, y - h, w - 4, 8, 2), (P.RED, P.GREEN, P.BLUE)[nth % 3], sw=1.6,
                light=None)
        c.line(f"M{n(x - w / 2 + 5)},{n(y - body + 6)} v{n(body * 0.35)}", 2, P.WHITE, 0.7)   # the glass shines
        _label(c, x, y - body * 0.45, label, size, paper=lighten(P.YELLOW_PALE, 0.2))
    elif kind == "tin":
        body = h - 9
        c.shape(rounded_rect_d(x - w / 2, y - body, w, body, 4), P.RED, sw=1.8, light=(-2, -2), shade_k=0.88)
        lw, lab_h = lettering_width(label, size, "plain"), size * 1.45
        lab = (x - lw / 2 - 4, y - body * 0.5 - lab_h / 2 - 2, x + lw / 2 + 4, y - body * 0.5 + lab_h / 2 + 2)
        step = max(7.0, size * 0.8)                      # the dots grow with the tin
        dots = []
        for i, dy in enumerate(_range(y - body + 6, y - 3, step)):
            for dx in _range(x - w / 2 + 4 + (step / 2 if i % 2 else 0), x + w / 2 - 3, step):
                if not lab[1] - 3 < dy < lab[3] + 3:          # the label's band stays plain red
                    dots.append(f'<circle cx="{n(dx)}" cy="{n(dy)}" r="{n(step * 0.24)}" fill="{P.WHITE}"/>')
        c.add("".join(dots))
        c.shape(rounded_rect_d(x - w / 2 - 2, y - body - 7, w + 4, 8, 2.5), darken(P.RED, 0.85), sw=1.6, light=None)
        c.shape(rounded_rect_d(x - 5, y - h, 10, 3.5, 1.5), darken(P.RED, 0.75), sw=1.2, light=None)   # the knob
        _label(c, x, y - body * 0.5, label, size)
    elif kind == "pasta":                                 # copy-pasta: an old pack, spaghetti sticking out
        body = h - 12
        strands = " ".join(f"M{n(x - w * 0.32 + i * w * 0.64 / 5)},{n(y - body + 2)} l{n((i % 3 - 1) * 2)},"
                           f"{n(-9 - (i * 5) % 6)}" for i in range(6))
        c.line(strands, 3.4, INK)                         # dry spaghetti, inked like everything else
        c.line(strands, 1.8, lighten(P.CRUST_RAW, 0.1))
        c.shape(rounded_rect_d(x - w / 2, y - body, w, body, 2), mix(P.KITCHEN_KRAFT, P.JAR_DUSTY, 0.35), sw=1.8,
                light=(-1, -1), shade_k=0.85)
        c.add(f'<rect x="{n(x - w / 2 + 4)}" y="{n(y - body + 4)}" width="{n(w - 8)}" height="{n(body * 0.22)}" '
              f'rx="2" fill="{lighten(P.CRUST_RAW, 0.2)}" stroke="{INK}" stroke-width=".9"/>')   # its window
        step = max(4.0, size * 0.45)
        c.line(" ".join(f"M{n(x - w / 2 + 6 + i * step)},{n(y - body + 5)} v{n(body * 0.22 - 2)}"
                        for i in range(int((w - 12) / step))), 0.8, darken(P.CRUST_RAW, 0.75))
        _label(c, x, y - body * 0.42, label, size, turn=-3, paper=mix(P.CARD, P.BEIGE_DARK, 0.4))
    elif kind == "dusty":
        body = h - 7
        c.shape(rounded_rect_d(x - w / 2, y - body, w, body, 5), P.JAR_DUSTY, sw=1.8, light=None)
        c.shape(rounded_rect_d(x - w / 2 + 2, y - h, w - 4, 8, 2), P.METAL_DARK, sw=1.6, light=None)
        _label(c, x, y - body * 0.5, label, size, turn=-6, paper=mix(P.CARD, P.BEIGE_DARK, 0.4))
    else:                                                 # the crate, crutches sticking out of it
        body = h - 16
        for cx, lean in ((x - w * 0.18, -8), (x + w * 0.2, 6)):
            c.add(f'<g transform="rotate({lean} {n(cx)} {n(y - body)})">'
                  f'<rect x="{n(cx - 1.6)}" y="{n(y - body - 14)}" width="3.2" height="16" fill="{P.WOOD_LIGHT}" '
                  f'stroke="{INK}" stroke-width="1"/><rect x="{n(cx - 6)}" y="{n(y - body - 16)}" width="12" '
                  f'height="3.5" rx="1.5" fill="{P.WOOD_DARK}" stroke="{INK}" stroke-width="1"/></g>')
        c.shape(rounded_rect_d(x - w / 2, y - body, w, body, 2), P.WOOD, sw=1.8, light=(-1, -1), shade_k=0.85)
        c.line(f"M{n(x - w / 2)},{n(y - body / 2)} H{n(x + w / 2)}", 1.1, INK, 0.5)
        _label(c, x, y - body * 0.5, label, size, turn=3, paper=mix(P.CARD, P.BEIGE_DARK, 0.4))
    return (x - w / 2 - 2, y - h, x + w / 2 + 2, y)


def _box(s, name: str, x: float, feet: float, scale: float = 1.0) -> tuple[float, float, float, float]:
    """Where a character drawn at its readable size (times `scale`) with its feet at (x, feet) would stand."""
    mod = char_module(name)
    k = s.tall * SIZE[name] * scale / PROFESSOR_HEIGHT * mod.SCENE_SCALE
    half = mod.SIZE[0] * 0.40 * k
    return (x - half, feet - (mod.FEET_Y - mod.HEAD_TOP) * k, x + half, feet)


def extra(s: Strip, name: str, fracs: float | tuple[float, ...], pose: str, mood: str = "smile", flip: bool = True,
          mark: str | None = None):
    """A character on the floor at the first of `fracs` across where it finds room: a frame too low or too full
    leaves it out rather than squeeze it in."""
    for frac in (fracs if isinstance(fracs, tuple) else (fracs,)):
        x = s.x(frac)
        box = _box(s, name, x, s.feet(x))
        if box[1] >= 2 and s.free(box, 3):
            return cast(s, name, frac, pose, mood, flip=flip, mark=mark)
    return None


def perch(s: Strip, name: str, x: float | tuple, top: float, pose: str, mood: str = "smile", flip: bool = False,
          scale: float = 0.8):
    """A character up on something - the counter, the fridge, the board's frame - its feet on `top`, if it fits;
    `x` may be a list of (x, top) spots to try in turn, `top` then ignored."""
    spots = x if isinstance(x, tuple) else ((x, top),)
    for px, ptop in spots:
        ptop -= 3.5                                       # on it, with the air the overlap check wants
        box = _box(s, name, px, ptop, scale)
        above = (box[0], box[1], box[2], ptop - 4)        # what it stands on is not in its way
        if box[1] >= 2 and box[0] >= s.lo and box[2] <= s.hi and s.free(above, 3):
            return s.actor(name, px, ptop, pose, mood, flip=flip, tall=s.tall * SIZE[name] * scale, group=name)
    return None


def flier(s: Strip, x: float | tuple, y: float, mood: str = "smile", flip: bool = False):
    """The sparrow in the air, its feet at (x, y), if the air there is free."""
    return perch(s, "sparrow", x, y, "fly", mood, flip, 0.5)


# ============================================================================ the cork board
def board_size(k: float, cards: tuple[tuple[str, str], ...]) -> tuple[float, float]:
    """The cork board's width and height in its own units for `cards`, each ("recipe" | "rules", its title)."""
    sizes = [recipe_size(k, word) if kind == "recipe" else rules_size(k, word) for kind, word in cards]
    gap = GAP_MIN / k + 8
    inner_w = sum(w for w, _ in sizes) + gap * (len(sizes) - 1) + 8
    inner_h = max(h for _, h in sizes) + 14
    return wrap(inner_w, k), wrap(inner_h, k)


def cork_board(s, left: float, top: float, k: float, cards: tuple[tuple[str, str], ...],
               group: str = "board") -> tuple[float, float, float, float]:
    """A cork board on the wall in a wooden frame, its top left at (left, top) on the page, each card pinned to it by
    a red push pin at its top. An empty `cards` gives a bare board, waiting. Returns its box."""
    w, h = board_size(k, cards) if cards else (wrap(90.0, k), wrap(70.0, k))
    pen = Pen(s, left, top, k)
    board = pen.container(group, 0, 0, w, h, P.KITCHEN_CORK, radius=3, shade_k=0.9)
    pen.c.add(f'<rect x="2.5" y="2.5" width="{n(w - 5)}" height="{n(h - 5)}" rx="2" fill="none" '
              f'stroke="{P.WOOD}" stroke-width="4"/>')                         # the frame
    pad = pen.pad(w, h)
    gap = GAP_MIN / k + 8
    x = pad + 4
    for i, (kind, word) in enumerate(cards):
        cw, ch = recipe_size(k, word) if kind == "recipe" else rules_size(k, word)
        y = pad + 9
        name = f"{group}_card{i}"
        if kind == "recipe":
            recipe(pen, name, x, y, word, k)
        else:
            rules(pen, name, x, y, word, k)
        pen.c.add(f'<circle cx="{n(x + cw / 2)}" cy="{n(y + 1)}" r="4.5" fill="{P.RED}" stroke="{INK}" '
                  f'stroke-width="1.4"/>')                                     # its push pin
        board.children.append((name, pen.box(x, y - 4, x + cw, y + ch)))
        x += cw + gap
    box = pen.box(0, 0, w, h)
    s.put(1.5, pen.svg(), box, group, group=group)
    return box


# ============================================================================ the cast in a frame
FRIDGE_TALL = 2.1          # the fridge's height over the counter's


def stand(s: Strip, name: str, xs: float | tuple[float, ...], pose: str, mood: str = "smile",
          face: float | None = None, mark: str | None = None, hold=None):
    """A character on the floor at the first of `xs` (page x) where it stands whole and free - failing those, at
    the nearest free spot along the floor - at the frame's one scale, facing the point `face` (or the frame's
    middle); `hold` a thing from `handheld` put in its right fist. None if there is no room at all."""
    feet = s.feet(0)
    first = xs if isinstance(xs, tuple) else (xs,)
    sweep = sorted((s.lo + (s.hi - s.lo) * i / 40 for i in range(41)), key=lambda x: abs(x - first[0]))
    writing = name == "caterpillar" and pose == "write"   # she ticks things off on a clipboard held in her fist
    pose = "present" if writing else pose
    for x in (*first, *sweep):
        box = _box(s, name, x, feet)
        if box[0] >= 2 and box[2] <= W - 2 and box[1] >= 2 and s.free(box, 3):
            target = W / 2 if face is None else face
            actor = s.actor(name, x, feet, pose, mood, flip=target < x, tall=s.tall * SIZE[name], group=name)
            if mark:
                k = min(1.3, max(0.6, s.tall / 160))
                mx = x + (actor.right - actor.left) * 0.55 * (1 if target < x else -1)
                my = actor.top + 18 * k
                s.put(feet + 1, props.mark(mx, my, mark, k), (mx - 17 * k, my - 17 * k, mx + 17 * k, my + 17 * k),
                      group=actor.group)
            if writing:
                s.hold(actor, handheld.clipboard)
            elif hold is not None:
                s.hold(actor, hold)
            return actor
    return None


def beside(s: Strip, box: tuple, side: int, name: str, gap: float = 6.0) -> tuple[float, ...]:
    """Page x's where a character stands right beside a thing's `box` on its `side` (-1 left, 1 right, the
    station's way round - mirrored on a mirrored page): close enough to reach it, then a little further out."""
    if getattr(s, "mirror", False):
        side = -side
    probe = _box(s, name, 0, s.feet(0))
    half = (probe[2] - probe[0]) / 2
    x = box[2] + half + gap if side > 0 else box[0] - half - gap
    return (x, x + side * 20, x + side * 44, x + side * 80)


def bird(s: Strip, x: float, top: float, group: str, pose: str = "stand", face: float | None = None):
    """The sparrow standing on a thing (`group`) with its feet on `top` at x, as big as the room over it allows -
    or not at all: never squeezed in, never on a character."""
    for scale in (0.5, 0.42, 0.34, 0.28):
        box = _box(s, "sparrow", x, top - 3.5, scale)
        if box[1] > 2 and box[0] > 2 and box[2] < W - 2 and all(not b.hits(box, 3) for b in s.boxes
                                                                if b.group != group):
            target = W / 2 if face is None else face
            return s.actor("sparrow", x, top - 3.5, pose, "smile", flip=target < x,
                           tall=s.tall * SIZE["sparrow"] * scale, group=group)
    return None


def flying(s: Strip, spots: tuple[tuple[float, float], ...], mood: str = "smile", face: float | None = None):
    """The sparrow in the air at the first of `spots` (x, the height of its feet) where the air is free."""
    for x, y in spots:
        for scale in (0.46, 0.38, 0.3):
            box = _box(s, "sparrow", x, y, scale)
            if box[1] > 2 and box[0] > 2 and box[2] < W - 2 and s.free(box, 4):
                target = W / 2 if face is None else face
                return s.actor("sparrow", x, y, "fly", mood, flip=target < x, tall=s.tall * SIZE["sparrow"] * scale,
                               group="sparrow")
    return None


def mid_of(box: tuple) -> float:
    return (box[0] + box[2]) / 2


# ============================================================================ the stations
def board_on_wall(s: Strip, r: Counter, cx: float, cards: tuple[tuple[str, str], ...], under: float = 0,
                  share: float = 0.34) -> tuple[float, float, float, float]:
    """Pin `cards` on a cork board hung over the counter, its middle at cx, as big as the wall lets it be and no
    wider than `share` of the frame; `under` keeps that much of the wall over the counter free for what stands
    there."""
    k = s.unit * 1.15
    gap = max(4.0, s.tall * 0.05)
    room_h = r.counter - under - gap - 6
    for _ in range(6):                                    # the whole board over the counter
        w, h = board_size(k, cards)
        k = min(k, room_h / h, (s.hi - s.lo) * share / w)
    w, h = board_size(k, cards)
    left = min(max(cx - w * k / 2, s.lo + 2), s.hi - 2 - w * k)
    return cork_board(s, left, r.counter - under - gap - h * k, k, cards)


def board_in_gap(s: Strip, r: Counter, cx: float, cards: tuple[tuple[str, str], ...],
                 share: float = 0.3) -> tuple[float, float, float, float]:
    """In a strip: the cork board hung low on a stretch of bare wall at cx - the counter breaks there - as tall as
    the wall from the frame's top to a hand over the skirting, so its cards read."""
    k = s.unit * 1.6
    room_h = r.floor - 22 - 6
    for _ in range(6):
        w, h = board_size(k, cards)
        k = min(k, room_h / h, (s.hi - s.lo) * share / w)
    w, h = board_size(k, cards)
    left = min(max(cx - w * k / 2, s.lo + 2), s.hi - 2 - w * k)
    wall_gap(s, r, left - 10, left + w * k + 10)
    return cork_board(s, left, 6 + (room_h - h * k) * 0.3, k, cards)


def recipe_station(s: Strip, beat: str) -> None:
    """The task is pinned up. "work": the professor (the cat, in a low frame) pins the recipe card on the cork board
    over the counter, the agent coming in waves, the sparrow on the board's frame. "puzzle": the agent stands
    before it, puzzled - nobody told it how this house cooks - the caterpillar doubting beside it (and the cat, in a
    tall frame, watching)."""
    r = bench(s)
    card = (("recipe", s.word("card")),)
    if strip(s):                                          # a close-up: the board big, the cast round it
        board = board_in_gap(s, r, X(s, 0.46), card)
    else:
        board = board_on_wall(s, r, X(s, 0.3 if beat == "work" else 0.42), card)
    bx = mid_of(board)
    if beat == "work":
        stand(s, who(s, "professor", "cat"), beside(s, board, 1, "professor"), "point", "talk", face=bx)
        stand(s, "agent", beside(s, board, -1, "agent") if strip(s) else (X(s, 0.86), X(s, 0.8)), "wave", "smile",
              face=bx)
        bird(s, board[0] + (board[2] - board[0]) * (0.25 if not s.mirror else 0.75), board[1], "board", face=bx)
    else:
        stand(s, "agent", beside(s, board, 1, "agent"), "think", "worry", face=bx, mark="?")
        stand(s, "caterpillar", beside(s, board, -1, "caterpillar") if strip(s) else (X(s, 0.88), X(s, 0.82)),
              "think", "worry", face=bx)
        if not low(s):
            stand(s, "cat", beside(s, board, -1, "cat"), "think", "smile", face=bx)
    finish(s, 0)


FRESH = (("prompts", "skills", "hooks"), ("mcp", "subagents", "checks"))   # the upper shelves, in the locale
OLD = ("copypaste", "legacy", "crutches")                                    # the low shelf, nearest to hand


def shelves(s, rows: int = 3) -> tuple[tuple[str, ...], ...]:
    """The pantry's rows of jar labels, top to bottom, the old row last; `rows` 2 keeps one fresh shelf, 1 only the
    old one (a low frame has no room for more and still readable)."""
    fresh = FRESH[:rows - 1]
    return (*(tuple(s.word(key) for key in row) for row in fresh), tuple(s.word(key) for key in OLD))


def _kinds(rows: tuple[tuple[str, ...], ...]) -> list[list[str]]:
    last = len(rows) - 1
    skip = len(OLD) - len(rows[-1])                       # the old row without the things taken from its front
    return [[kind_of(label, i + skip if r == last else None) for i, label in enumerate(row)]
            for r, row in enumerate(rows)]


def pantry_size(k: float, rows: tuple[tuple[str, ...], ...]) -> tuple[float, float, float, list[list[float]],
                                                                      list[float]]:
    """The pantry's width and height in its own units, the label size, the things' widths row by row and each
    row's height."""
    size = letter(k, 9.0)
    gap = GAP_MIN / k + 6
    kinds = _kinds(rows)
    widths = [[goods_width(label, kind, size) for label, kind in zip(row, kr, strict=True)]
              for row, kr in zip(rows, kinds, strict=True)]
    heights = [max(goods_height(kind, size) for kind in kr) + 2 for kr in kinds]
    row_w = max(sum(row) + gap * (len(row) + 1) for row in widths)
    between = max(14.0, GAP_MIN / k + 10)                 # a shelf's room over the things under it
    return (wrap(row_w, k), wrap(sum(heights) + between * (len(rows) - 1) + gap, k), size, widths, heights)


def pantry(s, left: float, top: float, k: float, rows: tuple[tuple[str, ...], ...],
           taken: int | None) -> tuple[float, float, float, float]:
    """The pantry shelves on the wall, their top left at (left, top) on the page: fresh jars and polka-dot tins
    standing labelled on the upper shelves; on the lowest one, nearest to hand, the old stuff - `taken` is the one
    the agent has just taken (its outline left in the dust). Returns its box."""
    w, h, size, widths, heights = pantry_size(k, rows)
    kinds = _kinds(rows)
    gap = GAP_MIN / k + 6
    between = max(14.0, GAP_MIN / k + 10)
    pen = Pen(s, left, top, k)
    pad = pen.pad(w, h)
    shelf = Holder("pantry", pen.box(0, 0, w, h), pen.box(pad, pad, w - pad, h - pad))   # open shelves: no back
    ledger(s)[0].append(shelf)
    side = pad - 1.5
    for sx in (0.0, w - side):                            # the two uprights, the wall seen between them
        pen.c.shape(rounded_rect_d(sx, 0, side, h, 1.5), P.WOOD, sw=1.6, light=(-1, -1), shade_k=0.85)
    pen.c.shape(rounded_rect_d(-2, 0, w + 4, side * 0.8, 1.5), P.WOOD_LIGHT, sw=1.6, light=None)   # the top
    for bx in (side + 2, w - side - 2):                   # the brackets that hold it to the wall
        way = 1 if bx < w / 2 else -1
        pen.c.add(f'<path d="M{n(bx)},{n(h)} h{n(way * 10)} L{n(bx)},{n(h + 10)} Z" fill="{P.METAL_DARK}" '
                  f'stroke="{INK}" stroke-width="1.2"/>')
    y, boards = pad, []
    for r, (labels, row_w) in enumerate(zip(rows, widths, strict=True)):
        y += heights[r] + (between if r else 0)
        is_old = r == len(rows) - 1
        boards.append(y)
        x = pad + gap + (w - 2 * pad - sum(row_w) - gap * (len(row_w) + 1)) / 2
        for i, (label, jw) in enumerate(zip(labels, row_w, strict=True)):
            jx = x + jw / 2
            x += jw + gap
            if is_old and i == taken:                     # the outline in the dust where the taken thing stood
                th = goods_height(kinds[r][i], size) - 8
                pen.c.add(f'<path d="M{n(jx - jw / 2)},{n(y)} V{n(y - th)} H{n(jx + jw / 2)} V{n(y)}" '
                          f'fill="none" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3" opacity=".45"/>')
                pen.child(shelf, f"gap{i}", jx - jw / 2 - 2, y - th, jx + jw / 2 + 2, y)
                continue
            pen.child(shelf, f"goods{r}{i}", *goods(pen.c, jx, y, label, kinds[r][i], size, nth=r * 3 + i))
    thick = max(5.0, 2.4 / k)                             # the boards last, over the things' feet: they stand on them
    for by in boards:
        pen.c.add(f'<rect x="{n(side)}" y="{n(by)}" width="{n(w - 2 * side)}" height="{n(thick)}" '
                  f'fill="{P.WOOD}" stroke="{INK}" stroke-width="1.4"/>')
    box = pen.box(-2, 0, w + 2, h + 10)
    s.put(1.5, pen.svg(), box, "pantry", group="pantry")
    return box


def _rest_hand_mirrored() -> bool:
    """Whether the agent's right hand hanging at his side is drawn mirrored: a thing held in it turns its
    lettering back accordingly, or the label reads back to front."""
    return char_module("agent").hands("stand")["right"].mirror


HELD_LETTER = sets.LETTERING_MIN + 0.5   # the label of the jar in the agent's fist, on the page: readable, no bigger


def held_letter(actor, page_size: float) -> float:
    """The lettering size, in a held thing's own units, that comes out `page_size` on the page: a maker's units
    are the holder's height over 100 on the page (its canvas units times the holder's scale), so the label of a
    jar in the fist reads as large as the labels on the shelf."""
    return page_size * 100 / max(actor.bottom - actor.top, 1.0)


def pantry_station(s: Strip, beat: str) -> None:
    """The agent takes the old jar of copy-paste off the low shelf - nearest to hand - while the fresh jars and
    tins stand labelled on the shelves over it; the cat points at them (where they are in the frame), the
    caterpillar frets (in a strip, or on the next visit). A strip has no wall for shelves that still read: there
    the old things stand on the worktop itself, right at hand."""
    r = bench(s)
    gap = max(4.0, s.tall * 0.05)
    room_h = r.counter - gap - 6
    if strip(s):                                          # a close-up: the shelves stand on the floor in a gap
        room_h = r.floor - 16
    fit = None
    for count in ((3, 2, 1) if s.h >= 300 else (2, 1)):
        rows = shelves(s, count)
        if strip(s):       # a close-up: the rack closes up behind the taken jar, no dusty outline of it to puzzle over
            rows = (*rows[:-1], rows[-1][1:])
        k = s.unit * 1.4
        for _ in range(20):                               # the shelves on the wall, with air over the counter
            w, h, size, _, _ = pantry_size(k, rows)
            k = min(k, room_h / (h + 10), (s.hi - s.lo) * (0.42 if strip(s) else 0.38) / w)
        w, h, size, _, _ = pantry_size(k, rows)
        if (h + 10) * k <= room_h + 0.5:
            fit = rows, k, w, h, size
            break
    if fit is not None:
        rows, k, w, h, size = fit
        if strip(s):
            left = min(max(X(s, 0.46) - w * k / 2, s.lo + 2), s.hi - 2 - w * k)
            box = pantry(s, left, r.floor - (h + 10) * k, k, rows, None)   # a low rack before the counter
        else:
            left = min(max(X(s, 0.3) - w * k / 2, s.lo + 2), s.hi - 2 - w * k)
            box = pantry(s, left, r.counter - gap - (h + 10) * k, k, rows, 0)
    else:
        rows = shelves(s, 1)
        box = old_on_worktop(s, r, X(s, 0.3), rows[-1][1:])
        size, k = sets.LETTERING_MIN + 0.5, 1.0
    label = s.word(OLD[0])                               # the copy-paste, taken off the low shelf
    jar_w = lettering_width(label, HELD_LETTER, "label") + 8   # the jar held out towards the shelf: room for it
    agent = stand(s, "agent", beside(s, box, 1, "agent", gap=6 + jar_w * 0.75), "stand", "smile",
                  face=mid_of(box))                   # the jar at his side: held up, a readable label hid his face
    if agent is not None:                                 # the old jar in its fist, its label readable on the page
        upright = _upright(s, agent)         # held upright whatever the forearm's slant
        held_size = held_letter(agent, HELD_LETTER)
        back = agent.flip != _rest_hand_mirrored()   # the lettering turned to read
        s.hold(agent, lambda x, y, kk: handheld.jar(x, y, kk, label, held_size, mirrored=back), turn=upright)
    if len(rows) > 1 and not getattr(s, "again", False):
        stand(s, "cat", beside(s, box, -1, "cat"), "point", "talk", face=mid_of(box))
    else:
        stand(s, "caterpillar", beside(s, box, -1, "caterpillar") + (X(s, 0.9),), "think", "worry",
              face=mid_of(box))
    if s.seed % 2 == 0:
        bird(s, box[0] + (box[2] - box[0]) * 0.8, box[1], "pantry", face=mid_of(box))
    finish(s, 1)


def old_on_worktop(s: Strip, r: Counter, cx: float, labels: tuple[str, ...]) -> tuple[float, float, float, float]:
    """The old things standing on the worktop at cx, as big as the wall over the counter lets them be, their labels
    still readable: the dusty jar of legacy and the crate of crutches. Returns their box."""
    room_h = r.counter - 6
    gk = 1.2
    for _ in range(12):
        size = letter(gk, 9.0)
        kinds = [kind_of(label, i + 1) for i, label in enumerate(labels)]
        tall = max(goods_height(kind, size) for kind in kinds)
        gk = min(gk, room_h / tall)
    size = letter(gk, 9.0)
    c, x = Canvas(), 0.0
    for i, label in enumerate(labels):
        kind = kind_of(label, i + 1)
        gw = goods_width(label, kind, size)
        goods(c, x + gw / 2, 0, label, kind, size, nth=i)
        x += gw + GAP_MIN / gk + 6
    width = (x - GAP_MIN / gk - 6) * gk
    tall = max(goods_height(kind_of(label, i + 1), size) for i, label in enumerate(labels)) * gk
    left = min(max(cx - width / 2, s.lo + 2), s.hi - 2 - width)
    box = (left - 2, r.surf - tall, left + width + 2, r.surf)
    s.put(1.4, f'<g transform="translate({n(left)},{n(r.surf)}) scale({n(gk)})">{c.render()}</g>', box, "pantry",
          group="pantry")
    return box


def stove(s, x: float, counter: float, floor: float, on: bool, inside: str = "raw",
          smoke: bool = False) -> tuple[float, float, float, float]:
    """A kitchen stove standing on the floor in the row of cabinets, its middle at x and its top flush with the
    counter: two burners on its top, the knobs and the timer on the panel under it, the oven door with its handle
    and a big window, the pie on the rack inside - glowing and the element red when it bakes, `smoke` seeping out
    at the door's top when it burns. Returns its box."""
    k = (floor - counter) / 100
    w, h = 96.0, 100.0
    if hasattr(s, "niches"):
        s.niches.append((x - w / 2 * k - 1, x + w / 2 * k + 1))
    pen = Pen(s, x, floor, k)
    for bx in (-24, 24):                                  # the burners' grates, standing on the top
        pen.c.add(f'<rect x="{bx - 15}" y="-105" width="30" height="5" rx="1.5" fill="{P.CHARCOAL}" stroke="{INK}" '
                  f'stroke-width="1.4"/>')
        pen.c.line(f"M{bx - 9},-105 v5 M{bx},-105 v5 M{bx + 9},-105 v5", 1, P.METAL_DARK)
    body = pen.container("stove", -w / 2, -h, w, h, P.KITCHEN_STOVE, radius=4, shade_k=0.88)
    pad = pen.pad(w, h)
    pen.c.add(f'<rect x="{-w / 2}" y="{-h}" width="{w}" height="5" fill="{P.CHARCOAL}" stroke="{INK}" '
              f'stroke-width="1.6"/>')                    # the cooktop's edge
    air = max(4.0, GAP_MIN / k + 1)
    ky = -h + pad + 6                                     # the knobs, the timer between them
    tr = 6.0
    knobs = (-tr - air - 4 - 8 - air, -tr - air - 4, tr + air + 4, tr + air + 4 + 8 + air)
    for i, kx in enumerate(knobs):
        pen.c.add(f'<circle cx="{n(kx)}" cy="{n(ky)}" r="4" fill="{P.METAL_DARK}" stroke="{INK}" '
                  f'stroke-width="1.2"/>')
        turn = math.radians(-50 if on and i == 1 else 0)
        pen.c.line(f"M{n(kx)},{n(ky)} l{n(math.sin(turn) * 3.4)},{n(-math.cos(turn) * 3.4)}", 1.2, P.WHITE)
        pen.child(body, f"knob{i}", kx - 4, ky - 4, kx + 4, ky + 4)
    pen.c.add(f'<circle cx="0" cy="{n(ky)}" r="{tr}" fill="{P.WHITE}" stroke="{INK}" stroke-width="1.6"/>')
    a = math.radians(-60 if on else 0)
    pen.c.line(f"M0,{n(ky)} L{n(math.sin(a) * tr * 0.8)},{n(ky - math.cos(a) * tr * 0.8)}", 1.4, P.RED)
    pen.child(body, "timer", -tr, ky - tr, tr, ky + tr)
    dl, dr, dt, db = -w / 2 + pad, w / 2 - pad, ky + tr + air, -pad   # the oven door
    pen.c.shape(rounded_rect_d(dl, dt, dr - dl, db - dt, 4), lighten(P.KITCHEN_STOVE, 0.4), sw=1.8, light=None)
    pen.c.add(f'<rect x="{n(dl + 8)}" y="{n(dt + 3)}" width="{n(dr - dl - 16)}" height="4" rx="2" '
              f'fill="{P.METAL}" stroke="{INK}" stroke-width="1.2"/>')            # its handle
    wl, wt, wr, wb = dl + 5, dt + 11, dr - 5, db - 5      # its window
    pen.c.shape(rounded_rect_d(wl, wt, wr - wl, wb - wt, 4), P.AMBER if on else P.SCREEN_DARK, sw=1.8, light=None)
    coil = " ".join(f"{'L' if i else 'M'}{n(wl + 5 + i * (wr - wl - 10) / 10)},{n(wt + (4 if i % 2 else 7))}"
                    for i in range(11))
    pen.c.line(coil, 1.4, P.RED if on else P.METAL_DARK)  # the top element
    rack = wb - 5
    pen.c.line(f"M{n(wl + 2)},{n(rack)} H{n(wr - 2)}", 1.2, P.METAL)
    if inside:                                            # the pie fills the window: it is the point of the oven
        pk = min((wr - wl - 10) / 66, (rack - wt - 12) / 32)
        pen.c.add(pie((wl + wr) / 2, rack, pk, inside))
    pen.c.line(f"M{n(wl + 4)},{n(wt + 6)} l8,-3", 1.6, P.WHITE, 0.6)                   # the glass shines
    pen.child(body, "door", dl, dt, dr, db)
    top = -h - 5
    if smoke:                                             # smoke billowing off the top from the oven's vent
        pen.c.add(smoke_cloud(-6, -h - 12, 0.95))
        top = -h - 12 - 112 * 0.95
    box = pen.box(-w / 2, top, w / 2, 0)
    s.put(floor - 1, pen.svg(), box, "stove", group="stove")
    return box


def hood(s, x: float, counter: float, floor: float) -> None:
    """The cooker hood over the stove, where the wall leaves room: a steel canopy, its duct going up out of the
    frame, a lamp glowing under its lip. Put after the cast, so it never covers them."""
    unit = floor - counter
    w, h = unit * 1.0, unit * 0.3
    bottom = counter - unit * 0.8
    if bottom - h < 24:
        return
    duct = w * 0.3
    box = (x - w / 2, 0, x + w / 2, bottom)
    if not s.free(box, 4):
        return
    c = Canvas()
    c.add(f'<rect x="{n(x - duct / 2)}" y="-4" width="{n(duct)}" height="{n(bottom - h + 4)}" '
          f'fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="1.8"/>')
    c.shape(f"M{n(x - duct / 2 - 4)},{n(bottom - h)} H{n(x + duct / 2 + 4)} L{n(x + w / 2)},{n(bottom - 6)} "
            f"V{n(bottom)} H{n(x - w / 2)} V{n(bottom - 6)} Z", P.METAL_LIGHT, sw=2, light=(-1, -1))
    c.line(" ".join(f"M{n(x - w * 0.3 + i * w * 0.12)},{n(bottom - h * 0.55)} h{n(w * 0.07)}" for i in range(6)), 1.4,
           P.METAL_DARK)                                  # its grille
    s.put(1.2, c.render(), box, "hood")


def kitchen_timer(x: float, foot: float, k: float) -> str:
    """A twin-bell wind-up kitchen timer standing at (x, foot), 34 tall at k = 1, ringing: tipped on one foot, its
    red case with a white dial and two hands, the two bells on top and the hammer struck between them."""
    c = Canvas()
    c.add(f'<ellipse cx="0" cy="0" rx="12" ry="1.8" fill="{INK}" fill-opacity=".15"/>')
    g = Canvas()
    g.line("M-6,-2 L-8,2 M6,-2 L8,2", 2.6)                                               # its feet
    for bx in (-7, 7):                                                                   # the bells
        g.shape(f"M{bx - 6},-24 Q{bx - 6},-32 {bx},-32 Q{bx + 6},-32 {bx + 6},-24 Z", P.METAL_LIGHT, sw=1.2,
                light=(-0.6, -0.6))
    g.line("M0,-22 V-31", 1.4)                                                           # the hammer's arm ...
    g.add(f'<circle cx="2.6" cy="-31" r="2.2" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1"/>')
    g.shape("M-11,-12 a11,11 0 1 1 22,0 a11,11 0 1 1 -22,0 Z", P.RED, sw=1.4, light=(-1, -1))    # the case
    g.add(f'<circle cx="0" cy="-12" r="8" fill="{P.CARD}" stroke="{INK}" stroke-width="1"/>')     # the dial
    g.line("M0,-12 L0,-17.5 M0,-12 L4,-10", 1.2)                                         # its hands
    g.add(f'<circle cx="0" cy="-12" r="1" fill="{INK}"/>')
    c.add(f'<g transform="rotate(-12)">{g.render()}</g>')
    return f'<g transform="translate({n(x)},{n(foot)}) scale({n(k)})">{c.render()}</g>'


def oven_station(s: Strip, beat: str) -> None:
    """The pie is in the oven. "bake": the agent shows it baking through the oven's window, the caterpillar asks
    if it will really bake, the sparrow flutters about. "smoke": the timer rings and smoke comes up - the agent
    shrugs, the professor (the cat, in a low frame) hurries in, the sparrow is off."""
    r = bench(s)
    ox = X(s, 0.4)
    box = stove(s, ox, r.counter, r.floor, True, "raw" if beat == "bake" else "bad", smoke=False)
    if beat == "bake":
        stand(s, "agent", beside(s, box, 1, "agent"), "point", "smile", face=ox)
        stand(s, "caterpillar", beside(s, box, -1, "caterpillar"), "think", "worry", face=ox)
        hood(s, ox, r.counter, r.floor)
        flying(s, ((box[0] - 50 * s.unit, r.counter - 16 * s.unit), (box[2] + 50 * s.unit, r.counter - 16 * s.unit),
                   (ox, r.counter - 30 * s.unit)), "smile", face=ox)
        # the golden floppy (an easter egg, `world_kit.hide`): left standing on the worktop, out of everyone's way
        stash_along(s, [X(s, f) for f in (0.92, 0.06, 0.82, 0.16, 0.6, 0.24)], r.counter - 2, r.counter)
    else:
        room_h = r.counter - 4
        sk = min(s.unit * 1.0, room_h / 126)              # the smoke as big as the wall over the stove allows
        if sk > 0.18:
            sx, sy = ox - 6 * sk, r.counter - 8 * sk
            s.put(1.45, smoke_cloud(sx, sy, sk), (sx - 32 * sk, sy - 112 * sk, sx + 36 * sk, r.counter), "smoke",
                  group="stove")
        # the kitchen timer that rang: a twin-bell wind-up timer on the stove's top, rocking on its feet, its
        # hammer between the bells - what made the sound, drawn instead of a sound word
        tk = max(0.5, min(1.2, s.unit * 1.1))
        tx = box[0] + 16 * tk if not getattr(s, "mirror", False) else box[2] - 16 * tk
        s.put(1.5, kitchen_timer(tx, box[1], tk), (tx - 13 * tk, box[1] - 34 * tk, tx + 13 * tk, box[1]), "timer",
              group="stove")
        stand(s, "agent", beside(s, box, 1, "agent"), "shrug", "worry", face=ox)
        stand(s, who(s, "professor", "cat"), beside(s, box, -1, "professor"), "think", "worry", face=ox)
        flying(s, ((X(s, 0.95), r.counter - 40 * s.unit), (X(s, 0.05), r.counter - 40 * s.unit)), "worry",
               face=W - ox)
    finish(s, 2)


def card_stand(s: Strip, x: float, r: Counter, k: float, word: str) -> tuple[float, float, float, float]:
    """The recipe card propped on a little wire stand on the counter, its picture facing us; returns its box."""
    w, h = recipe_size(k, word)
    pen = Pen(s, x - w * k / 2, r.surf - (h + 8) * k, k)
    recipe(pen, "stand_card", 0, 0, word, k)
    pen.c.line(f"M{n(w * 0.2)},{n(h)} L{n(w * 0.1)},{n(h + 8)} M{n(w * 0.8)},{n(h)} L{n(w * 0.9)},{n(h + 8)}", 2,
               P.METAL_DARK)
    box = pen.box(0, 0, w, h + 8)
    s.put(1.6, pen.svg(), box, "stand_card", group="stand_card")
    return box


def board_cut(x: float, y: float, k: float) -> str:
    """A wooden cutting board lying on the counter, its middle at x and its foot at y, its handle with a hole."""
    c = Canvas()
    c.shape("M-40,0 L-36,-7 H30 Q34,-7 36,-4 L46,-4 Q50,-4 50,-1 V0 Z", P.WOOD_LIGHT, sw=1.6, light=None)
    c.add(f'<circle cx="44" cy="-2.2" r="1.3" fill="{P.WOOD_DARK}"/>')
    c.line("M-34,-2.5 H28", 1, P.WOOD, 0.8)
    return _at(c, x, y, k)


def held_pie(x: float, y: float, k: float) -> str:
    """The burnt pie on its cutting board, held out by the board's handle (`handheld` frame): big, for a close-up."""
    f = k * 1.05
    c = Canvas()
    c.add(f'<g transform="translate({n(46 * f)},{n(2 * f)}) scale(-1,1)">{board_cut(0, 0, f)}</g>')   # by its handle
    c.add(pie(46 * f, -4 * f, f, "bad"))                  # the pie out past the fist
    return c.render()


def slop_station(s: Strip, beat: str) -> None:
    """Out comes the burnt pie, on a cutting board. "out": the agent is proud of it - in a strip it holds it out
    by the board's handle, big - the professor (the caterpillar, in a low frame) is not, the sparrow on the worktop
    is after a crumb. "inspect": the cat holds a magnifier over it beside the recipe card - in a strip the card on
    the board on the wall, big enough to compare - and the caterpillar writes down what is wrong."""
    r = bench(s)
    side = -1 if getattr(s, "mirror", False) else 1
    if beat == "out" and strip(s):                        # a close-up: the agent holds the pie out, the cast round it
        agent = stand(s, "agent", (X(s, 0.42), X(s, 0.46), X(s, 0.38)), "present", "smile", face=X(s, 0.7))
        if agent is not None:
            s.hold(agent, held_pie, turn=_upright(s, agent))
            gx, gy, _ = s.grip(agent, "right")            # where the held pie reaches, for the others to keep off
            f = (agent.bottom - agent.top) / 100 * 1.05
            way = -1 if agent.flip else 1
            far = gx + way * 92 * f
            s.put(agent.bottom + 0.5, "", (min(gx, far), gy - 52 * f, max(gx, far), gy + 8 * f), "held_pie",
                  group=agent.group)
            front = far + way * 60 * s.unit
            stand(s, "caterpillar", (front, front + (-20 if agent.flip else 20)), "think", "worry",
                  face=(agent.left + agent.right) / 2)
        finish(s, 3)
        return
    k = min(s.unit * 1.25, (r.counter - 8) / 60)
    px = X(s, 0.4 if not strip(s) else 0.52)
    if beat == "inspect" and strip(s):                    # the recipe card on the wall beside the pie, to compare
        k = min(s.unit * 1.25, (r.counter - 6) / 52)
        card = board_in_gap(s, r, px - side * (51 * k + 60), (("recipe", s.word("card")),), share=0.22)
        px = (card[2] + 51 * k + 12) if side > 0 else (card[0] - 51 * k - 12)
    s.put(1.3, board_cut(px, r.surf, k), (px - 41 * k, r.surf - 8 * k, px + 51 * k, r.surf), "cutting",
          group="slop")
    s.put(1.4, pie(px, r.surf - 6 * k, k, "bad"), (px - 34 * k, r.surf - 48 * k, px + 34 * k, r.surf), "slop",
          group="slop")
    if beat == "out":
        sk = min(k * 0.55, (r.surf - 50 * k - 6) / 112)
        if sk > 0.15:                                     # still smoking a little
            sx, sy = px + 6 * k, r.surf - 40 * k
            s.put(1.45, smoke_cloud(sx, sy, sk, dark=False), (sx - 30 * sk, sy - 112 * sk, sx + 36 * sk, sy),
                  "smoke", group="slop")
        box = (px - 41 * k, r.surf - 48 * k, px + 51 * k, r.surf)
        stand(s, "agent", beside(s, box, 1, "agent"), "cheer", "smile", face=px)
        stand(s, who(s, "professor", "caterpillar"), beside(s, box, -1, "professor"), "think", "worry", face=px)
        for dx in (-64, 74, -90, 100):                    # on the worktop by the pie, after a crumb
            if bird(s, px + side * dx * k, r.surf, "counter", pose="point", face=px):
                break
    elif strip(s):
        box = (px - 41 * k, r.surf - 48 * k, px + 51 * k, r.surf)
        stand(s, "cat", beside(s, box, 1, "cat", gap=2), "present", "worry", face=px, hold=handheld.magnifier)
        stand(s, "caterpillar", beside(s, card, -1, "caterpillar"), "write", "worry", face=px)
    else:
        ck = s.unit * 0.95
        for _ in range(6):                                # the card whole on the counter, under the frame's top
            ck = min(ck, (r.surf - 10) / (recipe_size(ck, s.word("card"))[1] + 8))
        cw = recipe_size(ck, s.word("card"))[0] * ck
        reach = 41 * k if side > 0 else 51 * k            # the cutting board's end on the card's side
        card = card_stand(s, px - side * (reach + cw / 2 + 8), r, ck, s.word("card"))
        box = (min(card[0], px - 41 * k), card[1], max(card[2], px + 51 * k), r.surf)
        stand(s, "cat", beside(s, box, 1, "cat", gap=2), "present", "worry", face=px, hold=handheld.magnifier)
        stand(s, "caterpillar", (X(s, 0.92), X(s, 0.88)), "write", "worry", face=px)
        if not low(s):
            stand(s, "agent", beside(s, box, -1, "agent"), "shrug", "worry", face=px)
    finish(s, 3)


def smoke_cloud(x: float, y: float, k: float, dark: bool = True) -> str:
    """Smoke billowing up from (x, y): puffs that grow as they rise and drift aside, each a cluster of round
    billows drawn as one cloud - the outline round all of them, then the fills over the inner seams - dark at the
    bottom where it comes out and paler higher up, with a light side and a wisp curling off the top; about 70 wide
    and 110 tall at k = 1."""
    c = Canvas()
    puffs = ((0, 0, 9), (5, -20, 12), (-3, -44, 15), (9, -74, 18))
    lobes = ((0, 0, 1.0), (-0.75, 0.25, 0.7), (0.7, 0.3, 0.75), (-0.3, -0.55, 0.72), (0.45, -0.5, 0.65))
    base, top = (P.CHARCOAL, P.METAL_DARK) if dark else (P.METAL_DARK, P.METAL_PALE)
    for i, (px, py, pr) in enumerate(puffs):
        tone = mix(base, top, i / (len(puffs) - 1))
        circles = [(x + (px + dx * pr) * k, y + (py + dy * pr) * k, pr * rr * k) for dx, dy, rr in lobes]
        c.add("".join(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(cr)}" fill="{tone}" stroke="{INK}" '
                      f'stroke-width="{n(max(1.2, 2 * k))}"/>' for cx, cy, cr in circles))
        c.add("".join(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(cr - max(0.6, k))}" fill="{tone}"/>'
                      for cx, cy, cr in circles))
        hx, hy, hr = circles[3]                           # the light side of the billow
        c.add(f'<circle cx="{n(hx - hr * 0.2)}" cy="{n(hy - hr * 0.2)}" r="{n(hr * 0.45)}" '
              f'fill="{lighten(tone, 0.35)}"/>')
    wx, wy = x + 14 * k, y - 96 * k                       # a wisp curling away off the top
    c.line(f"M{n(wx)},{n(wy)} q{n(8 * k)},{n(-6 * k)} {n(4 * k)},{n(-14 * k)} q{n(-4 * k)},{n(-8 * k)} {n(6 * k)},"
           f"{n(-12 * k)}", max(1.4, 2.2 * k), top)
    return c.render()


def fridge(s, x: float, feet: float, tall: float, k: float, note: str | None) -> tuple[float, float, float, float]:
    """The fridge standing on the floor at (x, feet), `tall` high on the page, a fridge's proportions: the freezer
    door over the big door, their long handles, the grille at its foot; `note` - the house rules pinned to the big
    door with a magnet at eye height, as big as the door allows and still readable (else a plain sheet with ruled
    lines), or None. Returns its box."""
    h = tall / k
    w = h * 0.48                                          # a tall fridge: a head taller than the counter and more
    if hasattr(s, "niches"):
        s.niches.append((x - w / 2 * k - 1, x + w / 2 * k + 1))
    pen = Pen(s, x, feet, k)
    body = pen.container("fridge", -w / 2, -h, w, h, P.WHITE, radius=7, shade_k=0.88)
    split = -h * 0.66                                     # the freezer on top, the big door under it
    pen.c.line(f"M{n(-w / 2)},{n(split)} H{n(w / 2)}", 2)
    pad = pen.pad(w, h)
    hx = w / 2 - pad - 8                                  # the freezer's handle, upright on its right
    hy0, hy1 = split - h * 0.14, split - 10
    pen.c.add(f'<rect x="{n(hx)}" y="{n(hy0)}" width="6" height="{n(hy1 - hy0)}" rx="3" '
              f'fill="{P.METAL}" stroke="{INK}" stroke-width="1.4"/>')
    pen.child(body, "freezer_handle", hx - 1, hy0 - 1, hx + 7, hy1 + 1)
    bx0, bx1, by = w / 2 - pad - w * 0.42, w / 2 - pad - 2, split + 8      # the big door's pocket handle, along
    pen.c.add(f'<rect x="{n(bx0)}" y="{n(by)}" width="{n(bx1 - bx0)}" height="6" rx="3" fill="{P.METAL}" '
              f'stroke="{INK}" stroke-width="1.4"/>')                             # the top of the door
    pen.child(body, "door_handle", bx0 - 1, by - 1, bx1 + 1, by + 7)
    gy = -pad - 10                                        # the grille at its foot
    pen.c.add(f'<rect x="{n(-w / 2 + pad + 4)}" y="{n(gy)}" width="{n(w - 2 * pad - 8)}" height="8" rx="2" '
              f'fill="{P.METAL_PALE}" stroke="{INK}" stroke-width="1"/>')
    pen.c.line(" ".join(f"M{n(-w / 2 + pad + 8 + i * 6)},{n(gy + 2)} v4" for i in range(int((w - 2 * pad - 14) / 6))),
               1, P.METAL_DARK)
    pen.child(body, "grille", -w / 2 + pad + 3, gy - 1, w / 2 - pad - 3, gy + 9)
    room_l, room_t = -w / 2 + pad + 1, by + 6 + GAP_MIN / k + 9   # the big door's face under its handle
    room_w, room_h = w - 2 * pad - 2, gy - 6 - room_t
    placed = False
    if note:
        for step in range(12):
            kn = k * (1 - step * 0.05)
            nw, nh = rules_size(kn, note)
            if nw * kn <= room_w * k and nh * kn <= room_h * k:
                nl = room_l + (room_w - nw * kn / k) / 2
                npen = Pen(s, x + nl * k, feet + room_t * k, kn)
                rules(npen, "fridge_note", 0, 0, note, kn)
                npen.c.add(f'<circle cx="{n(nw / 2)}" cy="-1" r="5" fill="{P.RED}" stroke="{INK}" '
                           f'stroke-width="1.4"/>')                     # its magnet
                pen.c.add(f'<g transform="translate({n(nl)},{n(room_t)}) scale({n(kn / k)})">{npen.c.render()}</g>')
                body.children.append(("note", pen.box(nl, room_t - 6, nl + nw * kn / k, room_t + nh * kn / k)))
                placed = True
                break
    if note and not placed:
        sw_, sh = min(room_w, w * 0.5), min(room_h, w * 0.55)
        sl, st_ = room_l + (room_w - sw_) / 2, room_t + 4
        if sh > 12 and sw_ > 10:
            pen.c.shape(rounded_rect_d(sl, st_, sw_, sh, 2), P.YELLOW_PALE, sw=1.6, light=None)
            pen.c.line(" ".join(f"M{n(sl + 4)},{n(st_ + sh * t)} H{n(sl + sw_ - 4)}" for t in (0.3, 0.5, 0.7)), 1.4,
                       INK, 0.6)
            pen.c.add(f'<circle cx="{n(sl + sw_ / 2)}" cy="{n(st_)}" r="4" fill="{P.RED}" stroke="{INK}" '
                      f'stroke-width="1.2"/>')
            pen.child(body, "sheet", sl - 1, st_ - 5, sl + sw_ + 1, st_ + sh + 1)
    box = pen.box(-w / 2, -h, w / 2, 0)
    s.put(feet - 1, pen.svg(), box, "fridge", group="fridge")
    return box


def fridge_station(s: Strip, beat: str) -> None:
    """The house rules. "write": the professor (the cat, in a low frame) writes them in his notebook by the fridge,
    the sparrow watching from its top, the agent waiting. "pin": the note - AGENTS.md - hangs on the fridge's door,
    the agent reads it, the caterpillar is glad (and the professor shows it, in a tall frame)."""
    r = bench(s)
    k = s.unit * 1.1
    fx = X(s, 0.3)
    feet, tall = r.floor, (r.floor - r.counter) * FRIDGE_TALL       # in the row of cabinets
    if beat == "write":
        box = fridge(s, fx, feet, tall, k, None)
        stand(s, who(s, "professor", "cat"), beside(s, box, 1, "professor"), "present", "talk", face=fx,
              hold=handheld.notebook)
        stand(s, "agent", (X(s, 0.86), X(s, 0.9)), "think", "smile", face=fx)
        bird(s, fx, box[1], "fridge", face=W - fx)
    else:
        box = fridge(s, fx, feet, tall, k, s.word("rules"))
        stand(s, "agent", beside(s, box, 1, "agent"), "think", "smile", face=fx)
        stand(s, "caterpillar", (X(s, 0.9), X(s, 0.84)), "cheer", "smile", face=fx)
        if not low(s):
            stand(s, "professor", beside(s, box, -1, "professor"), "point", "talk", face=fx)
    finish(s, 4)


def red_button(s: Strip, x: float, bottom: float, k: float, word: str) -> tuple[float, float, float, float]:
    """The big red button of the book: an emergency stop screwed to the wall - a yellow box, the red mushroom
    button on it under a clear flip-up cover, the warning plate under it. Its middle at x, its plate's foot at
    `bottom`. Returns its box."""
    size = letter(k, 8.0)
    tw, th = tag_size(word, size, k)
    pen = Pen(s, x, bottom, k)
    box_w = max(48.0, 32 + 2 * pen.pad(48.0, 52.0))      # the button keeps clear of the box's edges at any scale
    box_h = max(52.0, 36 + 2 * pen.pad(box_w, 52.0))     # the button keeps clear of the box's edges at any scale
    bt = -th - 6 - box_h                                  # the box's top
    body = pen.container("estop", -box_w / 2, bt, box_w, box_h, P.YELLOW, radius=5, shade_k=0.85)
    for sx, sy in ((-box_w / 2 + 5, bt + 5), (box_w / 2 - 5, bt + 5), (-box_w / 2 + 5, bt + box_h - 5),
                   (box_w / 2 - 5, bt + box_h - 5)):      # its screws
        pen.c.add(f'<circle cx="{n(sx)}" cy="{n(sy)}" r="1.8" fill="{P.METAL_DARK}"/>')
    cy = bt + box_h / 2 - 1
    pen.c.add(f'<circle cx="0" cy="{n(cy + 2)}" r="14" fill="{darken(P.RED, 0.7)}" stroke="{INK}" '
              f'stroke-width="1.8"/>')                     # the mushroom's rim
    pen.c.add(f'<circle cx="0" cy="{n(cy)}" r="12" fill="{P.RED}" stroke="{INK}" stroke-width="1.8"/>')
    pen.c.add(f'<ellipse cx="-4" cy="{n(cy - 4)}" rx="4" ry="2.6" fill="{lighten(P.RED, 0.45)}"/>')
    pen.child(body, "button", -15, cy - 13, 15, cy + 17)
    pen.c.add(f'<path d="M-17,{n(cy + 10)} V{n(cy - 6)} Q-17,{n(cy - 19)} 0,{n(cy - 19)} Q17,{n(cy - 19)} 17,'
              f'{n(cy - 6)} V{n(cy + 10)}" fill="{P.LENS}" fill-opacity=".3" stroke="{INK}" stroke-width="1.4"/>')
    pen.c.add(f'<rect x="-6" y="{n(cy - 22)}" width="12" height="4" rx="1.5" fill="{P.METAL}" stroke="{INK}" '
              f'stroke-width="1"/>')                       # the cover's hinge
    pen.tag("dont", 0, -th / 2 - 1, word, size, P.WHITE, style="plain")
    box = pen.box(-max(box_w / 2, tw / 2), bt, max(box_w / 2, tw / 2), 0)
    s.put(1.5, pen.svg(), box, "estop", group="estop")
    return box


def bowl(x: float, y: float, k: float) -> str:
    """A mixing bowl on the counter with a whisk in it, its foot's middle at (x, y): 56 wide, 30 tall."""
    c = Canvas()
    c.line("M6,-22 L22,-44", 2.6, P.WOOD_DARK)                                      # the whisk's handle
    for dx in (-4, 0, 4):
        c.add(f'<path d="M6,-22 q{dx - 6},10 {dx * 0.6},14 q{-dx * 0.6 + 6},-4 {-dx},-14" fill="none" '
              f'stroke="{P.METAL_DARK}" stroke-width="1.2"/>')
    c.shape("M-28,-22 H28 Q26,-2 10,0 H-10 Q-26,-2 -28,-22 Z", P.KITCHEN_CABINET, sw=2, light=(-1, -1),
            shade_k=0.85)
    c.add(f'<ellipse cx="0" cy="-22" rx="28" ry="4" fill="{P.CREAM}" stroke="{INK}" stroke-width="1.6"/>')   # batter
    c.line("M-20,-12 Q0,-8 20,-12", 1.2, P.WHITE, 0.7)
    return _at(c, x, y, k)


def worktop(s: Strip, r: Counter, x0: float, k: float, side: int) -> tuple[float, float, float, float]:
    """What the agent bakes with this time, on the worktop from x0 along `side` (1 rightwards, -1 leftwards): the
    fresh jars and tins it took, the mixing bowl with its whisk, the new pie in its tin. Returns their box."""
    size = letter(k, 9.0)
    row, x = Canvas(), 0.0
    tallest = 0.0
    for i, key in enumerate(FRESH[0]):
        label = s.word(key)
        kind = kind_of(label)
        jw = goods_width(label, kind, size)
        goods(row, x + jw / 2, 0, label, kind, size, nth=i)
        tallest = max(tallest, goods_height(kind, size))
        x += jw + GAP_MIN / k + 4
    jars_w = (x - GAP_MIN / k - 4) * k
    parts = [("jars", jars_w), ("bowl", 58 * k), ("pie", 66 * k)]
    if side < 0:
        parts.reverse()
    total = sum(w_ for _, w_ in parts) + 2 * 10 * k
    left = x0 if side > 0 else x0 - total
    left = min(max(left, s.lo + 2), s.hi - 2 - total)
    at = left
    for name, w_ in parts:
        mx = at + w_ / 2
        if name == "jars":
            s.put(1.4, f'<g transform="translate({n(at)},{n(r.surf)}) scale({n(k)})">{row.render()}</g>',
                  (at, r.surf - tallest * k, at + w_, r.surf), "goods", group="worktop")
        elif name == "bowl":
            s.put(1.4, bowl(mx, r.surf, k), (mx - 29 * k, r.surf - 44 * k, mx + 29 * k, r.surf), "bowl",
                  group="worktop")
        else:
            s.put(1.4, pie(mx, r.surf, k, "raw"), (mx - 33 * k, r.surf - 31 * k, mx + 33 * k, r.surf), "pie",
                  group="worktop")
        at += w_ + 10 * k
    return (left, r.surf - max(tallest * k, 44 * k), left + total, r.surf)


def worktop_width(s: Strip, k: float) -> float:
    size = letter(k, 9.0)
    jars = sum(goods_width(s.word(key), kind_of(s.word(key)), size) for key in FRESH[0]) + 2 * (GAP_MIN / k + 4)
    return (jars + 58 + 66 + 20) * k


def good_station(s: Strip, beat: str) -> None:
    """The house cooks it right. "bake": the agent bakes again by the rules - the recipe and AGENTS.md pinned on
    the board over the counter, the fresh jars and the mixing bowl by the new pie - the professor's thumb up (the
    cat cheering, in a low frame). "serve": the even golden pie on the table under its checked cloth, the
    caterpillar ticks it off on her list, the agent cheers, and the sparrow is at the big red button on the wall."""
    r = bench(s)
    side = -1 if getattr(s, "mirror", False) else 1
    if beat == "bake":
        cards = (("recipe", s.word("card")), ("rules", s.word("rules")))
        other = "cat" if low(s) else "professor"
        cast_w = sum(_box(s, name, 0, s.feet(0))[2] - _box(s, name, 0, s.feet(0))[0] for name in ("agent", other))
        room_w = s.hi - s.lo - cast_w - 40
        k = min(s.unit * 1.0, (r.counter - 10) * 0.42 / 44)
        under = s.h >= 300                                 # a tall frame: the board over the things on the worktop
        if under:
            k = min(k, k * room_w / worktop_width(s, k))
            things_ = worktop(s, r, X(s, 0.36) - side * worktop_width(s, k) / 2, k, side)
            board = board_on_wall(s, r, mid_of(things_), cards, under=things_[3] - things_[1] + 6, share=0.42)
        else:                                              # a low one: the board beside them, the wall's whole height
            ow = _box(s, other, 0, s.feet(0))[2] - _box(s, other, 0, s.feet(0))[0]
            aw = _box(s, "agent", 0, s.feet(0))[2] - _box(s, "agent", 0, s.feet(0))[0]
            bk = s.unit * 1.15
            for _ in range(6):
                bk = min(bk, (r.counter - max(4.0, s.tall * 0.05) - 6) / board_size(bk, cards)[1],
                         (s.hi - s.lo) * 0.3 / board_size(bk, cards)[0])
            bx_ = s.lo + ow + 16 + board_size(bk, cards)[0] * bk / 2   # room for the one beside it
            board = board_on_wall(s, r, bx_ if side > 0 else s.lo + s.hi - bx_, cards, share=0.3)
            free_w = (s.hi - s.lo) - (board[2] - board[0]) - ow - aw - 60
            k = min(k, k * free_w / worktop_width(s, k))
            edge = board[2] + 12 if side > 0 else board[0] - 12
            things_ = worktop(s, r, edge, k, side)
        work = (min(things_[0], board[0]), board[1], max(things_[2], board[2]), r.surf)
        stand(s, "agent", beside(s, work, 1, "agent"), "present", "smile", face=mid_of(work))
        stand(s, other, beside(s, work, -1, other), "cheer" if low(s) else "thumb", "smile", face=mid_of(work))
    else:
        tx = X(s, 0.36)
        tk = min(s.unit * 1.5, (s.feet(0) - 10) / 100)
        feet = s.feet(0) - 1
        pk = tk * 0.82
        top = feet - 48 * tk
        table = (tx - 47 * tk, top - 44 * pk, tx + 47 * tk, feet)
        s.put(feet, kitchen_table(tx, feet, tk, 90, cloth=P.RED) + pie(tx, top, pk, "good"), table, "table",
              group="table")
        bk = s.unit * 0.95
        for _ in range(6):                                # the button's box and its plate whole on the wall
            bk = min(bk, (r.counter - 12) / (58 + tag_size(s.word("dont"), letter(bk, 8.0), bk)[1] + 8))
        box = red_button(s, X(s, 0.86), r.counter - 8 * bk, bk, s.word("dont"))
        stand(s, "caterpillar", beside(s, table, 1, "caterpillar"), "write", "smile", face=tx)
        stand(s, "agent", beside(s, table, -1, "agent"), "cheer", "smile", face=tx)
        # the sparrow flies at the button, right by its cover: after it all book, never pressing it
        mid = (box[1] + box[3]) / 2 + 10 * bk
        flying(s, ((box[0] - 30 * s.unit, mid), (box[2] + 30 * s.unit, mid), (box[0] - 50 * s.unit, mid)), "smile",
               face=mid_of(box))
        if not low(s):
            stand(s, "cat", (X(s, 0.66), X(s, 0.62)), "cheer", "smile", face=tx)
    finish(s, 5)


# ============================================================================ the finale
def finale(s: Strip) -> None:
    """The whole kitchen at once, left to right in the stations' order, everyone at one scale and as big as the
    width lets them be: the professor with the recipe card under the cork board, the agent with the jar of
    copy-paste under the pantry, the stove baking, the burnt pie on its board and the cat with his magnifier, the
    fridge with the house rules on its door, the golden pie on the table and the caterpillar ticking it off, the
    sparrow over them. A tall frame names each station on a tag just over its things; a low strip reads without
    words and keeps only what stands whole."""
    from .world_fair import zoom
    ledger(s)
    zoom(s)
    s.shot, s.mirror, s.index = 0, False, 0
    feet = s.feet(0)
    named = s.h >= 300
    size = max(sets.LETTERING_MIN + 1, min(15.0, s.h * 0.028))
    words = [s.word(st_.key) for st_ in KITCHEN.stations]
    th = tag_size("Ag", size)[1]
    s.tall = 137.0

    def wof(name: str) -> float:
        b = _box(s, name, 0, feet)
        return (b[2] - b[0]) / 137

    hp = (_box(s, "professor", 0, feet)[3] - _box(s, "professor", 0, feet)[1]) / 137
    cut_w = 92 / 137 * 0.9                                 # the cutting board, per unit of `tall`
    jar = 0.22                                             # the jar of copy-paste in the agent's fist
    need = [max(0.62, wof("professor")), max(0.62, wof("agent")) + jar, 0.5, cut_w, wof("cat"), 0.54,
            0.7, wof("caterpillar")]
    air = 0.05
    top_room = (th + 24) if named else 6.0                 # the names over the tallest things
    tall = min((s.hi - s.lo) / (sum(need) + air * (len(need) + 1)),
               (feet - top_room - 70) / hp if named else (feet - 6) / hp,
               (s.base - top_room) / (0.5 * FRIDGE_TALL),  # the fridge whole under the names
               340.0)
    s.tall, s.unit = tall, tall / 137
    _walls(s, 0)
    r = bench(s)
    spare = (s.hi - s.lo) - tall * (sum(need) + air * (len(need) + 1))
    gap = air * tall + spare / (len(need) + 1)
    x = s.lo + gap
    slots = []
    for w in need:
        slots.append((x, x + w * tall))
        x += w * tall + gap
    k = s.unit
    head = feet - hp * tall                                # the top of the professor's head
    tops: dict[int, float] = {}
    # the things first, then the cast round them
    a0, a1 = slots[0]                                      # 1. the cork board with the recipe over the professor
    b0, b1 = slots[1]
    c0, c1 = slots[2]
    card = (("recipe", s.word("card")),)
    lift = th + 14 if named else 0.0                     # room under the wall things for the names below them
    room_h = min(head - top_room - 10 - lift, tall * 0.85)       # the wall over the heads, never taller than this
    split = (b0 + b1) / 2 - 0.1 * (b1 - b0)               # the board takes the wall up to here, the pantry after
    bk = k * 1.15
    for _ in range(8):
        bw, bh = board_size(bk, card)
        bk = min(bk, room_h / bh, (split - 6 - s.lo) / bw)
    bw, bh = board_size(bk, card)
    board_right = split - 6
    if bh * bk > 40:
        left = max(s.lo + 2, min((a0 + a1) / 2 - bw * bk / 2, split - 6 - bw * bk))
        board_right = left + bw * bk
        tops[0] = cork_board(s, left, head - 8 - lift - bh * bk, bk, card)[1]
    rows = shelves(s, 2)                                   # 2. the pantry over the agent and the stove
    span_ = (board_right + 14, slots[4][1] + gap * 0.4)  # over the agent, the stove, the pie and the cat
    for count in (2, 1):
        rows = shelves(s, count)
        rows = (*rows[:-1], rows[-1][1:])                  # the copy-paste is in the agent's fist
        pk = k * 1.2
        for _ in range(12):
            pw, ph, _, _, _ = pantry_size(pk, rows)
            pk = min(pk, room_h / (ph + 10), (span_[1] - span_[0] - 4) / pw)
        pw, ph, _, _, _ = pantry_size(pk, rows)
        if (ph + 10) * pk <= room_h + 0.5 and ph * pk > 36 and pw * pk <= span_[1] - span_[0] - 3.5:
            left = min(max((b0 + c1) / 2 - pw * pk / 2, span_[0] + 2), span_[1] - 2 - pw * pk)
            tops[1] = pantry(s, left, head - 8 - lift - (ph + 10) * pk, pk, rows, None)[1]
            break
    c0, c1 = slots[2]                                      # 3. the stove, baking
    tops[2] = stove(s, (c0 + c1) / 2, r.counter, r.floor, True, "raw")[1]
    d0, d1 = slots[3]                                      # 4. the burnt pie on its cutting board
    sk = min((d1 - d0) / 92, (r.counter - top_room - 4) / 54)
    px = d0 + 41 * sk
    s.put(1.3, board_cut(px, r.surf, sk), (px - 41 * sk, r.surf - 8 * sk, px + 51 * sk, r.surf), "cutting",
          group="slop")
    s.put(1.4, pie(px, r.surf - 6 * sk, sk, "bad"), (px - 34 * sk, r.surf - 48 * sk, px + 34 * sk, r.surf), "slop",
          group="slop")
    tops[3] = r.surf - 48 * sk
    f0, f1 = slots[5]                                      # 5. the fridge with the house rules on its door
    fbox = fridge(s, (f0 + f1) / 2, r.floor, (r.floor - r.counter) * FRIDGE_TALL, k * 1.1, s.word("rules"))
    tops[4] = fbox[1]
    g0, g1 = slots[6]                                      # 6. the golden pie on the table
    tk = min(k * 1.4, (g1 - g0) / 96)
    tx = (g0 + g1) / 2
    ttop = feet - 1 - 48 * tk
    s.put(feet, kitchen_table(tx, feet - 1, tk, 90, cloth=P.RED) + pie(tx, ttop, tk * 0.82, "good"),
          (tx - 47 * tk, ttop - 44 * tk * 0.82, tx + 47 * tk, feet - 1), "table", group="table")
    tops[5] = ttop - 44 * tk * 0.82
    stand(s, "professor", (a0 + a1) / 2, "present", "smile", face=W, hold=handheld.card)
    agent = stand(s, "agent", (b0 + b1) / 2, "stand", "smile", face=W)
    if agent is not None:
        label = s.word(OLD[0])
        upright = _upright(s, agent)
        size = held_letter(agent, HELD_LETTER)
        back = agent.flip != _rest_hand_mirrored()
        s.hold(agent, lambda xx, yy, kk: handheld.jar(xx, yy, kk, label, size, mirrored=back), turn=upright)
    e0, e1 = slots[4]
    stand(s, "cat", (e0 + e1) / 2, "present", "worry", face=px, hold=handheld.magnifier)
    h0, h1 = slots[7]
    stand(s, "caterpillar", (h0 + h1) / 2, "write", "smile", face=tx)
    if not bird(s, (fbox[0] + fbox[2]) / 2, fbox[1], "fridge", pose="cheer", face=0):
        flying(s, ((tx, tops[5] - 10), (tx + 30 * k, tops[5] - 40 * k)), "smile", face=0)
    _counter(s, r)
    if named:                                             # each name on a tag just over its station's thing
        pen = Pen(s, 0, 0, 1)
        owners = ("board", "pantry", "stove", "slop", "fridge", "table")
        th = tag_size("Ag", size)[1]
        for i, (word, owner) in enumerate(zip(words, owners, strict=True)):
            found = [b for b in s.boxes if b.name == owner]
            if not found:
                continue
            thing = found[0]
            tw = tag_size(word, size)[0]
            cx = min(max((thing.left + thing.right) / 2, s.lo + tw / 2 + 2), s.hi - tw / 2 - 2)
            spot = None
            for dy in range(0, 40, 4):                    # just over it, or a little aside
                for dx in (0.0, -0.6, 0.6, -1.0, 1.0):
                    x_ = min(max(cx + dx * tw, s.lo + tw / 2 + 2), s.hi - tw / 2 - 2)
                    y_ = thing.top - th / 2 - 6 - dy
                    if y_ - th / 2 > 4 and s.free((x_ - tw / 2, y_ - th / 2, x_ + tw / 2, y_ + th / 2), 4):
                        spot = (x_, y_)
                        break
                if spot:
                    break
            if spot is None:
                continue
            cx, y = spot
            holder = pen.tag(f"label{i}", cx, y, word, size, P.CHARCOAL, P.WHITE)
            s.put(2, "", holder.outer, f"label{i}")
        s.put(2, pen.svg(), None)
        if s.h >= 450:                                    # a tall page: the window and the clock over it all
            _upper_wall(s, r, 3)


def _fit_tall(name: str, width: float, height: float) -> float:
    """The professor-height that makes the character fit `width` by `height`, never bigger than in a frame."""
    mod = char_module(name)
    per = mod.SCENE_SCALE / PROFESSOR_HEIGHT
    return min(width / (mod.SIZE[0] * 0.8 * per), height / ((mod.FEET_Y - mod.HEAD_TOP) * per))


# ============================================================================ the opener
def opener(st: Stage, accent: str):
    """The kitchen in the morning, nothing cooking yet: the counter along the back wall, the stove cold in the row of
    its cabinets, an empty tin on the counter; over it the pantry - fresh jars above, old dusty ones nearest to
    hand - the fridge with nothing on its door yet; the sunrise in
    the window, the clock at 4:04. In front, the professor tells the agent and the cat what this kitchen is for."""
    ledger(st)
    c = st.back
    floor, counter = 830.0, 700.0
    c.add(f'<rect x="0" y="0" width="{W}" height="{floor}" fill="{mix(P.KITCHEN_WALL, accent, 0.06)}"/>')
    tile = 26.0
    splash = counter - tile * 3
    tx0 = 468.0                                           # the tiles behind the stove and the fridge only: the
    c.add(f'<rect x="{n(tx0)}" y="{n(splash)}" width="{n(W - tx0)}" height="{n(counter - splash)}" '   # wall under
          f'fill="{P.KITCHEN_TILE}"/>')                                                # the bubble stays plain
    c.line(" ".join(f"M{n(tx0)},{n(splash + i * tile)} H{W}" for i in range(4)) + " " +
           " ".join(f"M{n(x)},{n(splash)} V{n(counter)}" for x in _range(tx0, W, tile)), 1,
           darken(P.KITCHEN_TILE, 0.82))
    # the floor, square tiles receding from the counter to the front of the page
    c.add(f'<rect x="0" y="{n(floor)}" width="{W}" height="{n(H - floor)}" fill="{P.KITCHEN_FLOOR}"/>')
    for i in range(5):
        y0, y1 = floor + (H - floor) * (i / 5) ** 1.3, floor + (H - floor) * ((i + 1) / 5) ** 1.3
        size = 48 + i * 22
        for j, x in enumerate(_range(-size, W + size, size)):
            if (i + j) % 2:
                c.add(f'<rect x="{n(x)}" y="{n(y0)}" width="{n(size)}" height="{n(y1 - y0)}" '
                      f'fill="{P.KITCHEN_FLOOR_DARK}" fill-opacity=".55"/>')
    st.keep_clear((tx0 - 2, splash - 2, W + 6, counter), (-6, counter - 2, W + 6, counter + 14))   # tiles, counter
    st.niches = []
    tall = 300.0                                          # one scale for all, the frames' proportions
    prof = st.actor("professor", 150, 1096, "explain", "talk", tall=tall * SIZE["professor"] * 1.15)   # his bubble
                                                          # over the plain wall, clear of the counter
    st.speaker(prof, width=100, left=8, air=CLEAR_MM)
    st.actor("agent", 450, 1120, "shrug", "worry", tall=tall * SIZE["agent"], group="agent")
    st.actor("cat", 690, 1136, "think", "smile", tall=tall * SIZE["cat"], group="cat")
    # the stove, cold, in the row of cabinets
    sw, placed = (floor - counter) * 0.96, None
    for sx in _range(420, 600, 10):
        if st.free((sx - sw / 2 - 30, counter - 40, sx + sw / 2 + 30, floor), 6):
            stove(st, sx, counter, floor, False, "")
            placed = sx
            break
    # the fridge at the right, in the row too
    ftall = 300.0
    fw = ftall * 0.48                                    # a fridge's width follows from its height
    for fx in (W - 8 - fw / 2, W - 20 - fw / 2):
        if st.free((fx - fw / 2, floor - ftall, fx + fw / 2, floor), 6):
            fridge(st, fx, floor, ftall, 1.2, None)
            break
    # the window onto the sunrise, the clock beside it, high on the wall
    done = False
    for ww, wh in ((170, 160), (150, 140), (140, 128), (120, 110)):     # at the left, over the bubble
        for wy in (262, 270, 290, 300, 312):
            for wx in (150, 170, 190):
                box = (wx - ww / 2 - 12, wy - 10, wx + ww / 2 + 12, wy + wh + 10)
                if box[2] <= W - 4 and box[3] < splash - 10 and st.free(box, 8):
                    st.put(0.3, sets.window_morning(wx, wy, ww, wh), box, "window")
                    done = True
                    break
            if done:
                break
        if done:
            break
    # the pantry over the counter's left end
    rows = shelves(st)
    done = False
    for pk in (1.15, 1.0, 0.9, 0.8, 0.72):
        w, h, *_ = pantry_size(pk, rows)
        for left, top in ((480, 280), (480, 300), (490, 320), (500, 340)):    # over the counter's right end
            box = (left, top, left + w * pk, top + h * pk + 30)          # with its lowest shelf's overhang
            if box[3] < splash - 10 and st.free(box, 8):
                pantry(st, left, top, pk, rows, None)
                done = True
                break
        if done:
            break
    for cx, cy in ((380, 320), (400, 340), (360, 300), (420, 360)):
        clock = (cx - 40, cy - 40, cx + 40, cy + 40)
        if st.free(clock, 10):
            st.put(0.3, wall_clock(cx, cy, 1.6), clock, "clock")
            break
    for tx in (300, 240, 655, 120):                      # the empty tin waiting on the counter
        box = (tx - 34 * 1.2, counter - 12 * 1.2, tx + 34 * 1.2, counter)
        if st.free(box, 6):
            st.put(1.4, tin(tx, counter, 1.2), box, "tin", group="tin")
            break
    if placed is not None:
        hood(st, placed, counter, floor)
    counter_row(c, counter, floor, st.niches)       # the cabinets around the stove and the fridge
    drawn = st.render()
    drawn.holders, drawn.links, drawn.ports = st.holders, st.links, st.ports
    return drawn


KITCHEN.stations.extend([
    Station("recipe", recipe_station, ("work", "puzzle")),
    Station("pantry", pantry_station, ("work",)),
    Station("oven", oven_station, ("bake", "smoke")),
    Station("slop", slop_station, ("out", "inspect")),
    Station("fridge", fridge_station, ("write", "pin")),
    Station("good", good_station, ("bake", "serve")),
])
KITCHEN.backdrop = backdrop
KITCHEN.finale = finale
KITCHEN.alternate = True                                     # never one moment on two pages in a row
OPENERS["kitchen"] = opener
hide(KITCHEN, "oven", "bake")

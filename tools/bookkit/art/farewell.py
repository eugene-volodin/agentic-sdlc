"""The farewell: the last page of the book, the five walking up a bright cobbled road into a computer city at sunset.

On the last page all our heroes go away into a computer city, as in the original book of professor Fortran, a picture
over the whole page: a beautiful sunset, AI agents working tirelessly in the fields in the background, and an even,
super bright cobbled road leading our heroes to the gate of this beautiful city. A homage to the last picture of the
Soviet encyclopedia of professor Fortran, drawn as our own scene in this book's manner, not a copy of the original.

One-point perspective: everything runs to the gate at (VP_X, HORIZON).

- The sky: deep violet-blue at the top through pink and orange to gold at the horizon; the big sun setting behind
  the city, half hidden by the fan-domed hall, its rays fanning out; long clouds lit gold from below.
- The city, backlit, its edges towards the sun rimmed with warm light, its windows lit: server racks with blinking
  units, processor chips on end with their pins, memory sticks in their slots, capacitor towers, the hall under the
  dome of a cooling fan, a cable strung from chip to chip with a cable car on it. In front, the city wall: circuit
  board panels with glowing traces and lights along the top, and in the middle the gate - a connector's metal shell
  with its gold contacts, between two heat-sink pillars, lit from inside.
- The fields on both sides, in rows running to the city: wheat, an orchard, a vineyard, cabbages. Agents work in
  them: picking apples, carrying crates, driving a tractor with a trailer, loading a cart, watering, picking grapes.
- The road (`road.py`; a straight road of slabs would read as a staircase, and the five seen from behind with
  their heads turned back would look twisted): from the gate it comes straight towards the reader through
  the fields, bends near him and runs off across the foot of the page - granite setts in courses that shrink with
  distance, staggered, each with its light edge and its shade, smooth kerbs along both edges, grass verges with
  flowers, street lamps where they stand free. The five walk along the near stretch towards the bend in their
  walking poses, all one way, the agent leading, then the professor, the cat and the caterpillar; the sparrow flies
  on ahead.

Units: the page, 840 x 1188 (4 units to the millimetre), like an opener. No title, no bubble, no words.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten, mix
from .ink import INK, Canvas, ellipse_d, n, rounded_rect_d
from .openers import H, W, Opener, Stage
from .road import Road, birds, body_box, furnish, walk_along
from .world_kit import connect, ledger, port

HORIZON = 560.0              # the vanishing point: the far end of the road, behind the gate
VP_X = 420.0
ROAD_FOOT = (120.0, 720.0)   # the road's edges at the foot of the page
WALL_TOP, WALL_FOOT = 600.0, 664.0      # the city wall
PLAZA = 686.0                # the circuit-board apron in front of the wall ends here; the fields begin
SUN = (420.0, 432.0, 122.0)  # the sun's middle and radius
DUSK = mix(P.SPACE_LOW, P.VIOLET, 0.4)  # the shade the backlit city takes


def edge_x(y: float, foot: float) -> float:
    """The x at height y of a line on the ground that reaches the page's foot at `foot` and runs to the VP."""
    return VP_X + (foot - VP_X) * (y - HORIZON) / (H - HORIZON)


def scale_at(y: float) -> float:
    """How tall the professor would be standing at height y."""
    return 0.5 * (y - HORIZON)


def _rect(x: float, y: float, w: float, h: float) -> str:
    return f"M{n(x)},{n(y)} H{n(x + w)} V{n(y + h)} H{n(x)} Z"


def _poly(points) -> str:
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in points) + " Z"


def _circle(x: float, y: float, r: float) -> str:
    return ellipse_d(x, y, r, r)


def _steps(a: float, b: float, step: float):
    x = a
    while x <= b + 1e-6:
        yield x
        x += step


def _quad(y0: float, y1: float, f0: float, f1: float) -> str:
    """A patch of ground between heights y0, y1 and the converging lines with feet f0, f1."""
    return _poly([(edge_x(y0, f0), y0), (edge_x(y0, f1), y0), (edge_x(y1, f1), y1), (edge_x(y1, f0), y1)])


def _depths(near: float, far: float, step: float) -> list[float]:
    """Heights from `near` up to `far` at even steps of distance (even steps of 1 / depth)."""
    out, inv = [], 1 / (near - HORIZON)
    while True:
        y = HORIZON + 1 / inv
        if y < far:
            break
        out.append(y)
        inv += step
    return out


def backlit(color: str) -> str:
    """A colour as it looks against the setting sun: darker, towards the dusk."""
    return mix(color, DUSK, 0.38)


# ============================================================================ the sky
def _sky(c: Canvas) -> None:
    paint = c.gradient([(0, mix(P.INDIGO, P.SPACE_DEEP, 0.55)), (0.22, mix(P.VIOLET, P.INDIGO, 0.35)),
                        (0.42, mix(P.PLUM, P.PINK, 0.5)), (0.6, mix(P.PINK, P.ORANGE, 0.45)),
                        (0.78, mix(P.ORANGE, P.AMBER, 0.5)), (0.9, P.SUN), (1, mix(P.SUN, P.YELLOW_PALE, 0.6))],
                       0, 0, 0, WALL_FOOT)
    c.add(f'<rect x="-4" y="-4" width="{W + 8}" height="{n(WALL_FOOT + 8)}" fill="{paint}"/>')
    sx, sy, r = SUN
    rays = []
    for i in range(15):                                          # rays fanning out of the sun, every other one lit
        a0, a1 = math.radians(-180 + i * 12 + 2), math.radians(-180 + i * 12 + 8)
        rays.append(_poly([(sx, sy), (sx + 1200 * math.cos(a0), sy + 1200 * math.sin(a0)),
                           (sx + 1200 * math.cos(a1), sy + 1200 * math.sin(a1))]))
    c.add(f'<path d="{" ".join(rays)}" fill="{P.YELLOW_PALE}" fill-opacity=".13"/>')
    for rr, a in ((r + 120, 0.10), (r + 70, 0.14), (r + 32, 0.22)):
        c.add(f'<circle cx="{n(sx)}" cy="{n(sy)}" r="{n(rr)}" fill="{P.YELLOW_PALE}" fill-opacity="{a}"/>')
    c.add(f'<circle cx="{n(sx)}" cy="{n(sy)}" r="{n(r)}" fill="{mix(P.SUN, P.YELLOW_PALE, 0.45)}"/>')
    c.add(f'<circle cx="{n(sx)}" cy="{n(sy)}" r="{n(r * 0.8)}" fill="{mix(P.YELLOW_PALE, P.WHITE, 0.4)}" '
          f'fill-opacity=".55"/>')
    for x, y, k in ((128, 108, 1.15), (690, 76, 0.95), (330, 150, 0.55), (772, 236, 0.5), (548, 156, 0.5)):
        _cloud(c, x, y, k)
    for x, y, k in ((86, 300, 1.0), (122, 286, 0.8), (708, 318, 0.9)):     # birds flying home
        c.line(f"M{n(x - 10 * k)},{n(y)} q{n(5 * k)},{n(-7 * k)} {n(10 * k)},0 q{n(5 * k)},{n(-7 * k)} {n(10 * k)},0",
               2.2, mix(P.INDIGO, INK, 0.5))


def _cloud(c: Canvas, x: float, y: float, k: float) -> None:
    """A long sunset cloud: violet-pink on top, its underside lit gold by the sun below."""
    d = (f"M{n(x - 110 * k)},{n(y)} Q{n(x - 118 * k)},{n(y - 14 * k)} {n(x - 86 * k)},{n(y - 16 * k)} "
         f"Q{n(x - 70 * k)},{n(y - 38 * k)} {n(x - 34 * k)},{n(y - 30 * k)} Q{n(x - 6 * k)},{n(y - 54 * k)} "
         f"{n(x + 28 * k)},{n(y - 32 * k)} Q{n(x + 64 * k)},{n(y - 40 * k)} {n(x + 80 * k)},{n(y - 16 * k)} "
         f"Q{n(x + 118 * k)},{n(y - 16 * k)} {n(x + 112 * k)},{n(y)} Z")
    clip = c.shape(d, mix(P.PINK_PALE, P.VIOLET, 0.35), sw=0, light=None, clip=True)
    c.add(f'<g clip-path="url(#{clip})"><path d="M{n(x - 130 * k)},{n(y - 12 * k)} Q{n(x)},{n(y - 22 * k)} '
          f'{n(x + 130 * k)},{n(y - 12 * k)} V{n(y + 6)} H{n(x - 130 * k)} Z" fill="{mix(P.SUN, P.PINK_PALE, 0.3)}"/>'
          f'<path d="M{n(x - 130 * k)},{n(y - 4 * k)} H{n(x + 130 * k)} V{n(y + 6)} H{n(x - 130 * k)} Z" '
          f'fill="{P.YELLOW_PALE}"/></g>')
    c.path(d, sw=2.0, stroke=mix(P.INDIGO, INK, 0.4))


# ============================================================================ the city
def _rim(c: Canvas, x: float, top: float, bottom: float) -> None:
    """The warm rim of light down a building's edge that faces the sun."""
    c.line(f"M{n(x)},{n(top + 3)} V{n(bottom)}", 3.2, P.SUN, 0.9)


def _lit(c: Canvas, x0: float, x1: float, top: float, bottom: float, cols: int, row: float, seed: int,
         share: float = 0.72) -> None:
    """A grid of windows on a backlit face: most of them lit warm."""
    rnd = random.Random(seed)
    w = (x1 - x0) / cols
    on, off = [], []
    for y in _steps(top, bottom - row * 0.55, row):
        for i in range(cols):
            (on if rnd.random() < share else off).append(_rect(x0 + i * w + w * 0.22, y, w * 0.56, row * 0.55))
    c.add(f'<path d="{"".join(off)}" fill="{backlit(P.SCREEN_DARK)}"/><path d="{"".join(on)}" fill="{P.YELLOW_PALE}"/>')


def server_rack(c: Canvas, x0: float, x1: float, top: float, base: float, seed: int, rim: float) -> tuple:
    """A server rack as a tower: its steel cabinet, servers stacked in it with drive bays and blinking lights."""
    rnd = random.Random(seed)
    c.shape(_rect(x0, top, x1 - x0, base - top), backlit(P.METAL_DARK), sw=2.6, light=None)
    c.shape(_rect(x0 + 6, top + 10, x1 - x0 - 12, base - top - 10), backlit(P.CHARCOAL), sw=1.5, light=None)
    units, bays, leds = [], [], {P.GLOW: [], P.SUN: [], P.TERMINAL_GREEN: []}
    for y in _steps(top + 14, base - 14, 15):
        units.append(_rect(x0 + 9, y, x1 - x0 - 18, 12))
        for k in range(2):
            leds[rnd.choice(list(leds))].append((x0 + 15 + k * 6, y + 6))
        bays.extend(f"M{n(bx)},{n(y + 3)} v6" for bx in _steps(x0 + 30, x1 - 13, 7))
    c.add(f'<path d="{"".join(units)}" fill="{backlit(mix(P.METAL_DARK, P.CHARCOAL, 0.4))}" stroke="{INK}" '
          f'stroke-width="1"/><path d="{" ".join(bays)}" fill="none" stroke="{P.METAL}" stroke-width="1.6" '
          f'stroke-opacity=".6"/>')
    for color, points in leds.items():
        c.add("".join(f'<circle cx="{n(px)}" cy="{n(py)}" r="2.1" fill="{color}"/>' for px, py in points))
    c.shape(_rect(x0 - 3, top - 7, x1 - x0 + 6, 8), backlit(P.METAL), sw=2, light=None)
    _rim(c, rim, top, base)
    return (x0 - 3, top - 7, x1 + 3, base)


def chip_tower(c: Canvas, x0: float, x1: float, top: float, base: float, seed: int, rim: float) -> dict:
    """A processor chip standing on end as a skyscraper: the black package with its notch and pin-one mark, rows of
    silver pins bent down its sides, lit windows. Returns its box and a port high on each side for a cable."""
    pin = 9
    pins = []
    for y in _steps(top + 60, base - 14, 17):
        pins.append(f"M{n(x0)},{n(y)} h{-pin} v11 h4 v-7 h{pin - 4} Z")
        pins.append(f"M{n(x1)},{n(y)} h{pin} v11 h-4 v-7 h{4 - pin} Z")
    c.add(f'<path d="{"".join(pins)}" fill="{backlit(P.METAL_LIGHT)}" stroke="{INK}" stroke-width="1.2" '
          f'stroke-linejoin="round"/>')
    c.shape(rounded_rect_d(x0, top, x1 - x0, base - top, 4), backlit(P.CHARCOAL), sw=2.6, light=None)
    mid = (x0 + x1) / 2
    c.add(f'<path d="M{n(mid - 11)},{n(top)} A11,11 0 0 0 {n(mid + 11)},{n(top)} Z" fill="{P.TERMINAL}" '
          f'stroke="{INK}" stroke-width="1.6"/><circle cx="{n(x0 + 13)}" cy="{n(top + 15)}" r="4.2" '
          f'fill="{backlit(P.METAL)}" stroke="{INK}" stroke-width="1.1"/>')
    _lit(c, x0 + 8, x1 - 8, top + 34, base - 6, 4, 13, seed)
    _rim(c, rim, top + 4, base)
    return {"box": (x0 - pin, top, x1 + pin, base), "left": (x0, top + 34), "right": (x1, top + 34)}


def memory_stick(c: Canvas, x0: float, x1: float, top: float, base: float, rim: float) -> tuple:
    """A memory stick as a tower: the green board standing in its black slot between white latches, its black
    chips one above another lit from inside, the notch in its edge, gold contacts at its foot."""
    slot = base - 16
    c.shape(_rect(x0 - 8, slot, x1 - x0 + 16, 16), backlit(P.CHARCOAL), sw=2.2, light=None)
    for x in (x0 - 14, x1 + 4):                                                         # the latches
        c.shape(rounded_rect_d(x, slot - 34, 10, 50, 3), backlit(P.CARD), sw=1.8, light=None)
    d = (f"M{n(x0)},{n(top)} H{n(x1)} V{n(slot + 4)} H{n(x0)} V{n((top + slot) / 2 + 8)} "
         f"A6,6 0 0 0 {n(x0)},{n((top + slot) / 2 - 4)} Z")                               # with its notch
    c.shape(d, backlit(mix(P.GREEN, P.PINE, 0.5)), sw=2.4, light=None)
    c.add(f'<path d="{"".join(_rect(x0 + 4 + i * 5, slot - 6, 3, 8) for i in range(int((x1 - x0 - 6) // 5)))}" '
          f'fill="{P.GOLD}"/>')
    rnd = random.Random(int(x0))
    for y in _steps(top + 10, slot - 40, 30):
        c.shape(_rect(x0 + 8, y, x1 - x0 - 16, 22), P.TERMINAL, sw=1.4, light=None)
        for j in range(3):
            if rnd.random() < 0.8:
                c.add(f'<path d="{_rect(x0 + 12 + j * (x1 - x0 - 24) / 3, y + 7, (x1 - x0 - 24) / 3 - 4, 8)}" '
                      f'fill="{P.YELLOW_PALE}"/>')
    _rim(c, rim, top, slot)
    return (x0 - 14, top, x1 + 14, base)


def capacitor(c: Canvas, x0: float, x1: float, top: float, base: float, color: str, rim: float) -> tuple:
    """An electrolytic capacitor as a round tower: the sleeve with its light stripe of minus signs, the silver top
    scored with a cross, rings of lit windows."""
    r, cx = (x1 - x0) / 2, (x0 + x1) / 2
    ry = r * 0.28
    body = (f"M{n(x0)},{n(top)} V{n(base)} H{n(x1)} V{n(top)} A{n(r)},{n(ry)} 0 0 0 {n(x0)},{n(top)} Z")
    clip = c.shape(body, backlit(color), sw=2.4, light=None, clip=True)
    side = x0 + r * 0.2 if rim > cx else x1 - r * 0.56
    marks = "".join(f"M{n(side + r * 0.09)},{n(y)} h{n(r * 0.18)}" for y in _steps(top + 16, base - 10, 15))
    c.add(f'<g clip-path="url(#{clip})"><path d="{_rect(side, top - ry, r * 0.36, base - top + ry)}" '
          f'fill="{lighten(backlit(color), 0.45)}"/><path d="{marks}" fill="none" stroke="{darken(color, 0.55)}" '
          f'stroke-width="2.4"/></g>')
    rows = [_rect(cx + t * r - 3, y, 6, 7) for y in _steps(top + 24, base - 14, 18) for t in (-0.3, 0.0, 0.3)
            if not side - 4 < cx + t * r < side + r * 0.36 + 4]
    c.add(f'<path d="{"".join(rows)}" fill="{P.YELLOW_PALE}"/>')
    c.shape(ellipse_d(cx, top, r, ry), backlit(P.METAL_LIGHT), sw=2, light=None)
    c.line(f"M{n(cx - r * 0.5)},{n(top)} H{n(cx + r * 0.5)} M{n(cx)},{n(top - ry * 0.55)} V{n(top + ry * 0.55)}",
           1.4, P.METAL_DARK)
    _rim(c, rim, top + ry, base)
    return (x0, top - ry, x1, base)


def fan_hall(c: Canvas, cx: float, base: float, r: float) -> tuple:
    """The hall under the dome of a cooling fan: the round frame, the curved blades round the hub, the guard's
    wires; the dome's rim lit by the sun behind it; below, the hall's lit front."""
    top = base - 70
    c.shape(_rect(cx - r, top, 2 * r, base - top), backlit(P.METAL_PALE), sw=2.6, light=None)
    _lit(c, cx - r + 10, cx + r - 10, top + 12, base, 12, 16, 9, 0.8)
    dome = f"M{n(cx - r)},{n(top)} A{n(r)},{n(r)} 0 0 1 {n(cx + r)},{n(top)} Z"
    clip = c.shape(dome, backlit(P.CHARCOAL), sw=2.8, light=None, clip=True)
    blades = []
    for i in range(7):                                                   # the blades, swept round the hub
        a = math.radians(-180 + 12 + i * 26)
        b = a + math.radians(18)
        p0 = (cx + 22 * math.cos(a), top + 22 * math.sin(a))
        p1 = (cx + (r - 14) * math.cos(a + 0.18), top + (r - 14) * math.sin(a + 0.18))
        p2 = (cx + (r - 14) * math.cos(b + 0.18), top + (r - 14) * math.sin(b + 0.18))
        p3 = (cx + 22 * math.cos(b), top + 22 * math.sin(b))
        blades.append(f"M{n(p0[0])},{n(p0[1])} Q{n(cx + r * 0.7 * math.cos(a - 0.2))},"
                      f"{n(top + r * 0.7 * math.sin(a - 0.2))} {n(p1[0])},{n(p1[1])} L{n(p2[0])},{n(p2[1])} "
                      f"Q{n(cx + r * 0.6 * math.cos(b))},{n(top + r * 0.6 * math.sin(b))} {n(p3[0])},{n(p3[1])} Z")
    c.add(f'<g clip-path="url(#{clip})"><path d="{" ".join(blades)}" fill="{backlit(P.TEAL)}" stroke="{INK}" '
          f'stroke-width="1.6"/></g>')
    guard = " ".join(f"M{n(cx - rr)},{n(top)} A{n(rr)},{n(rr)} 0 0 1 {n(cx + rr)},{n(top)}"
                     for rr in (r * 0.45, r * 0.72))
    spokes = " ".join(f"M{n(cx)},{n(top)} L{n(cx + (r - 6) * math.cos(math.radians(a)))},"
                      f"{n(top + (r - 6) * math.sin(math.radians(a)))}" for a in range(-165, -10, 30))
    c.line(f"{guard} {spokes}", 1.6, backlit(P.METAL_LIGHT))
    c.shape(f"M{n(cx - 24)},{n(top)} A24,24 0 0 1 {n(cx + 24)},{n(top)} Z", backlit(P.METAL), sw=2, light=None)
    c.add(f'<path d="M{n(cx - r)},{n(top)} A{n(r)},{n(r)} 0 0 1 {n(cx + r)},{n(top)}" fill="none" '
          f'stroke="{backlit(P.METAL)}" stroke-width="9"/>')                      # the frame ring
    c.path(dome, sw=2.8)
    rr = r + 4
    c.add(f'<path d="M{n(cx - rr * 0.8)},{n(top - rr * 0.6)} A{n(rr)},{n(rr)} 0 0 1 {n(cx + rr * 0.8)},'
          f'{n(top - rr * 0.6)}" fill="none" stroke="{P.SUN}" stroke-width="3.4" stroke-linecap="round"/>')  # lit rim
    return (cx - r, top - r, cx + r, base)


def cable_car(x: float, y: float, k: float) -> tuple[str, tuple]:
    """A little cable car on the cable at (x, y): the wheel carriage, the hanger, the cabin with lit windows."""
    c = Canvas()
    c.shape(rounded_rect_d(x - 10 * k, y - 5 * k, 20 * k, 9 * k, 3 * k), backlit(P.METAL_DARK), sw=1.6, light=None)
    for dx in (-5, 5):
        c.shape(_circle(x + dx * k, y - 1 * k, 3.2 * k), P.METAL_LIGHT, sw=1.2, light=None)
    c.line(f"M{n(x)},{n(y + 4 * k)} V{n(y + 14 * k)}", 2.6 * k)
    c.shape(rounded_rect_d(x - 22 * k, y + 14 * k, 44 * k, 30 * k, 6 * k), P.TEAL, sw=2, light=(-3, -3))
    c.add(f'<path d="{"".join(_rect(x + dx * k, y + 19 * k, 9 * k, 10 * k) for dx in (-17, -5, 7))}" '
          f'fill="{P.YELLOW_PALE}" stroke="{INK}" stroke-width="1.1"/>')
    return c.render(), (x - 23 * k, y - 6 * k, x + 23 * k, y + 45 * k)


def _wall(c: Canvas) -> None:
    """The city wall: panels of circuit board with glowing traces, lights along the top, the edge's gold
    contacts at its foot; the apron of board in front with traces running to the gate."""
    pcb = backlit(mix(P.PINE, P.LEAF_DARK, 0.35))
    c.shape(_rect(-6, WALL_TOP, W + 12, WALL_FOOT - WALL_TOP), pcb, sw=2.6, light=None)
    joints = " ".join(f"M{n(x)},{n(WALL_TOP + 8)} V{n(WALL_FOOT - 12)}" for x in range(60, W, 120))
    c.line(joints, 1.4, darken(pcb, 0.7))
    rnd = random.Random(4)
    traces = []
    for x in range(14, W - 20, 40):                                    # traces with their 45-degree jogs
        y0 = WALL_TOP + 16 + rnd.choice((0, 8, 16))
        traces.append(f"M{x},{n(WALL_FOOT - 12)} V{n(y0 + 14)} l12,-12 h{rnd.choice((6, 12))}")
    d = " ".join(traces)
    c.add(f'<path d="{d}" fill="none" stroke="{P.GOLD_LIGHT}" stroke-width="5" stroke-opacity=".35" '
          f'stroke-linecap="round" stroke-linejoin="round"/><path d="{d}" fill="none" stroke="{P.GOLD}" '
          f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
    leds = "".join(rounded_rect_d(x, WALL_TOP - 3, 10, 6, 3) for x in range(6, W, 22))
    c.add(f'<path d="{leds}" fill="{P.GLOW}" stroke="{INK}" stroke-width="1.2"/>')            # the light strip
    fingers = "".join(_rect(x, WALL_FOOT - 9, 6, 7) for x in range(4, W, 11))
    c.add(f'<path d="{fingers}" fill="{P.GOLD}" stroke="{INK}" stroke-width=".8"/>')
    # the apron
    apron = mix(P.PINE, P.LEAF_DARK, 0.25)
    c.add(f'<path d="{_rect(-6, WALL_FOOT, W + 12, PLAZA - WALL_FOOT)}" fill="{apron}"/>')
    streets = " ".join(f"M{n(edge_x(PLAZA, f))},{PLAZA} L{n(edge_x(WALL_FOOT + 2, f))},{n(WALL_FOOT + 2)}"
                       for f in (-2600, -1800, -1100, -500, 1340, 1940, 2640, 3440))
    c.add(f'<path d="{streets} M-6,{n(WALL_FOOT + 11)} H{W + 6}" fill="none" stroke="{P.GOLD_LIGHT}" '
          f'stroke-width="2.4"/>')
    c.line(f"M-6,{PLAZA} H{W + 6}", 2)


def gate(s: Stage) -> tuple:
    """The gate: a connector's metal shell with its gold contacts along the top of the opening and a light trim
    round it, lit warm from inside where the road runs in, between two heat-sink pillars."""
    c = Canvas()
    lo, hi = edge_x(WALL_FOOT, ROAD_FOOT[0]) - 6, edge_x(WALL_FOOT, ROAD_FOOT[1]) + 6
    open_top = WALL_FOOT - 164                     # a tall arch: the city beyond rises in it to its sky
    glow = "".join(f'<ellipse cx="{VP_X}" cy="{n(open_top + 90)}" rx="{n(rx)}" ry="{n(rx * 0.9)}" '
                   f'fill="{P.YELLOW_PALE}" fill-opacity="{a}"/>' for rx, a in ((190, 0.1), (150, 0.12), (115, 0.16)))
    s.put(WALL_FOOT - 0.5, glow)                   # the gate glowing: its light round the shell, over the wall
    shell_l, shell_r, shell_t = lo - 24, hi + 24, open_top - 30
    # the pillars: stacks of fins on a base, a capping block
    for x0 in (shell_l - 62, shell_r + 8):
        c.shape(_rect(x0, shell_t - 26, 54, WALL_FOOT - shell_t + 26), backlit(P.METAL_DARK), sw=2.4, light=None)
        fins = "".join(_rect(x0 - 6, y, 66, 5) for y in _steps(shell_t - 14, WALL_FOOT - 22, 11))
        c.add(f'<path d="{fins}" fill="{backlit(P.METAL_LIGHT)}" stroke="{INK}" stroke-width="1.1"/>')
        c.shape(_rect(x0 - 8, shell_t - 38, 70, 13), backlit(P.METAL), sw=2.2, light=None)
        c.shape(_rect(x0 - 4, WALL_FOOT - 18, 62, 18), backlit(P.METAL), sw=2.2, light=None)
    # the shell, its seams and bolts, the lit edge
    shell = (f"M{n(shell_l)},{n(WALL_FOOT)} V{n(shell_t + 22)} Q{n(shell_l)},{n(shell_t)} {n(shell_l + 22)},"
             f"{n(shell_t)} H{n(shell_r - 22)} Q{n(shell_r)},{n(shell_t)} {n(shell_r)},{n(shell_t + 22)} "
             f"V{n(WALL_FOOT)} Z")
    c.shape(shell, backlit(P.METAL_PALE), sw=2.8, light=None)
    c.line(f"M{n(shell_l + 8)},{n(shell_t + 18)} Q{n(shell_l + 8)},{n(shell_t + 8)} {n(shell_l + 22)},"
           f"{n(shell_t + 8)} H{n(shell_r - 22)}", 2.4, P.SUN, 0.9)
    seams = " ".join(f"M{n(x)},{n(shell_t + 20)} V{n(WALL_FOOT - 2)}" for x in (lo - 12, hi + 12))
    c.line(seams, 1.4, darken(backlit(P.METAL_PALE), 0.75))
    bolts = "".join(_circle(x, y, 1.8) for x in (lo - 18, lo - 6, hi + 6, hi + 18)
                    for y in _steps(shell_t + 30, WALL_FOOT - 8, 14))
    c.add(f'<path d="{bolts}" fill="{backlit(P.METAL)}" stroke="{INK}" stroke-width=".8"/>')
    # the lights along the top of the shell: bulbs in a strip, each with its glow
    bulbs = list(_steps(shell_l + 30, shell_r - 30, 15))
    c.add("".join(f'<circle cx="{n(x)}" cy="{n(shell_t + 13)}" r="6" fill="{P.GLOW}" fill-opacity=".3"/>'
                  for x in bulbs))
    c.add(f'<path d="{"".join(_circle(x, shell_t + 13, 3) for x in bulbs)}" fill="{lighten(P.GLOW, 0.4)}" '
          f'stroke="{INK}" stroke-width="1"/>')
    # the opening, and through it the city's street
    opening = (f"M{n(lo)},{n(WALL_FOOT)} V{n(open_top + 16)} Q{n(lo)},{n(open_top)} {n(lo + 16)},{n(open_top)} "
               f"H{n(hi - 16)} Q{n(hi)},{n(open_top)} {n(hi)},{n(open_top + 16)} V{n(WALL_FOOT)} Z")
    clip = c.shape(opening, P.YELLOW_PALE, sw=0, light=None, clip=True)
    c.add(f'<g clip-path="url(#{clip})">{_street(lo, hi, open_top)}</g>')
    c.path(opening, sw=2.6)
    # the connector's gold pins round the opening: along its top and down both sides
    pins = "".join(_rect(x, open_top - 9, 5, 7) for x in _steps(lo + 14, hi - 18, 9))
    pins += "".join(_rect(x, y, 7, 5) for x in (lo - 9, hi + 2) for y in _steps(open_top + 18, WALL_FOOT - 12, 10))
    c.add(f'<path d="{pins}" fill="{P.GOLD}" stroke="{INK}" stroke-width=".9"/>')
    # the keystone plate over the opening, bolted, with a chip on it
    kx, ky = VP_X, shell_t
    c.shape(f"M{n(kx - 20)},{n(ky - 6)} H{n(kx + 20)} L{n(kx + 14)},{n(ky + 22)} H{n(kx - 14)} Z", P.GOLD, sw=2,
            light=None)
    bolts = "".join(_circle(kx + dx, ky + dy, 1.6) for dx, dy in ((-15, -1), (15, -1), (-11, 17), (11, 17)))
    c.add(f'<path d="{bolts}" fill="{backlit(P.METAL)}" stroke="{INK}" stroke-width=".8"/>')
    chip_pins = " ".join(f"M{n(kx - 7)},{n(y)} h-3 M{n(kx + 7)},{n(y)} h3" for y in (ky + 4, ky + 8, ky + 12))
    c.line(chip_pins, 1.2, INK)
    c.add(f'<path d="{_rect(kx - 7, ky + 1, 14, 14)}" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="1"/>'
          f'<circle cx="{n(kx - 3.5)}" cy="{n(ky + 4.5)}" r="1.2" fill="{P.METAL}"/>')
    s.put(WALL_FOOT, c.render(), [(shell_l - 70, shell_t - 38, shell_r + 70, WALL_FOOT)], "gate", group="city",
          backdrop=True)
    return lo, hi, open_top


def _street(lo: float, hi: float, top: float) -> str:
    """The city seen through the gate, in the same perspective: a street of shops under awnings and balconies, warm
    in the sun on the right and cool in the shade on the left, bunting and a string of lights across it, a monorail
    with its train along it, robots walking on its glowing circuit road; then a square with a fountain, market
    stalls and trees in planters; the blocks round the square with lit windows, signs and roof gardens; and far off
    the city's skyline of chips, a fan dome and server towers under the setting sun. Both leaves of the gate's door
    stand swung open against the sides. Drawn in the plane of the gate and carried back to depth t (1 the gate)."""
    c = Canvas()
    rnd = random.Random(12)

    def at(x: float, y: float, t: float) -> tuple[float, float]:
        return VP_X + (x - VP_X) * t, HORIZON + (y - HORIZON) * t

    def side(x: float, y0: float, y1: float, ta: float, tb: float) -> str:
        """A face along the street: plane x, from height y0 to y1, from depth ta back to tb."""
        return _poly([at(x, y0, ta), at(x, y0, tb), at(x, y1, tb), at(x, y1, ta)])

    def front(x0: float, x1: float, y0: float, y1: float, t: float) -> str:
        """A face across the street at depth t."""
        (a0, b0), (a1, b1) = at(x0, y0, t), at(x1, y1, t)
        return _rect(min(a0, a1), min(b0, b1), abs(a1 - a0), abs(b1 - b0))

    paths: dict[tuple, list[str]] = {}

    def put(d: str, fill: str, stroke: str = INK, width: float = 0.8) -> None:
        paths.setdefault((fill, stroke, round(width, 2)), []).append(d)

    def flush() -> None:
        for (fill, stroke, width), ds in paths.items():
            c.add(f'<path d="{" ".join(ds)}" fill="{fill}" stroke="{stroke}" stroke-width="{n(width)}" '
                  f'stroke-linejoin="round"/>')
        paths.clear()

    # the sky over the far end, and the bottom of the sun behind the far city
    sky = c.gradient([(0, mix(P.ORANGE, P.SUN, 0.5)), (1, mix(P.SUN, P.YELLOW_PALE, 0.7))], 0, top, 0, HORIZON)
    c.add(f'<path d="{_rect(lo - 4, top - 4, hi - lo + 8, HORIZON - top + 8)}" fill="{sky}"/>')
    sx, sy, r = SUN
    c.add(f'<circle cx="{n(sx)}" cy="{n(sy)}" r="{n(r)}" fill="{mix(P.SUN, P.YELLOW_PALE, 0.45)}"/>')
    # the avenue from the square on to the far end, under everything standing on it
    mid = 0.4
    avenue = _poly([at(380, WALL_FOOT, mid), at(460, WALL_FOOT, mid), (VP_X + 2, HORIZON), (VP_X - 2, HORIZON)])
    c.add(f'<path d="{avenue}" fill="{mix(P.CRUST, P.CHARCOAL, 0.3)}"/>')
    # far off: the skyline - chip towers, server towers, a fan dome, bridges between them
    far = 0.12
    skyline = [(150, 300, 520, "chip"), (300, 360, 420, "rack"), (372, 468, 300, "dome"), (480, 540, 460, "rack"),
               (560, 640, 560, "chip"), (650, 720, 380, "rack")]
    for x0, x1, h, kind in skyline:
        tone = backlit(mix(P.INDIGO, P.METAL_DARK, 0.4))
        if kind == "dome":
            (cx, cy), rr = at((x0 + x1) / 2, WALL_FOOT - 80, far), (x1 - x0) / 2 * far
            put(f"M{n(cx - rr)},{n(cy)} A{n(rr)},{n(rr)} 0 0 1 {n(cx + rr)},{n(cy)} Z", tone, INK, 0.7)
            put(front(x0, x1, WALL_FOOT, WALL_FOOT - 80, far), tone, INK, 0.7)
            spokes = (f"M{n(cx)},{n(cy)} l{n(rr * math.cos(math.radians(a)))},{n(rr * math.sin(math.radians(a)))}"
                      for a in range(-160, -10, 30))
            c.line(" ".join(spokes), 0.7, P.TEAL)
            continue
        put(front(x0, x1, WALL_FOOT, WALL_FOOT - h, far), tone, INK, 0.7)
        if kind == "chip":
            for xp in (x0, x1):
                pins = (_rect(at(xp, y, far)[0] - 1, at(xp, y, far)[1], 2, 0.8)
                        for y in _steps(WALL_FOOT - h + 30, WALL_FOOT - 20, 24))
                put(" ".join(pins), P.METAL_LIGHT, P.METAL_LIGHT, 0.2)
        put(" ".join(_rect(*at(x, y, far), 1.4, 1.2) for x in _steps(x0 + 12, x1 - 14, 18)
                     for y in _steps(WALL_FOOT - h + 24, WALL_FOOT - 30, 26) if rnd.random() < 0.7),
            P.YELLOW_PALE, P.YELLOW_PALE, 0.1)
    c.line(" ".join(f"M{n(at(a, WALL_FOOT - 250, far)[0])},{n(at(a, WALL_FOOT - 250, far)[1])} "
                    f"L{n(at(b, WALL_FOOT - 250, far)[0])},{n(at(b, WALL_FOOT - 250, far)[1])}"
                    for a, b in ((300, 150), (720, 640))), 0.9, INK)                 # bridges
    flush()
    # the blocks round the square at depth 0.4, the avenue between them
    blocks = [(120, 250, 210, P.PLUM, -1), (250, 384, 150, P.TEAL, -1), (456, 590, 170, P.ORANGE, 1),
              (590, 720, 230, P.BLUE, 1)]
    for x0, x1, h, color, way in blocks:
        tone = mix(mix(color, P.METAL_PALE, 0.45), P.INDIGO if way < 0 else P.SUN, 0.22)
        put(front(x0, x1, WALL_FOOT, WALL_FOOT - h, mid), tone, INK, 1.0)
        put(front(x0 - 4, x1 + 4, WALL_FOOT - h, WALL_FOOT - h - 8, mid), darken(tone, 0.8), INK, 0.8)   # cornice
        for xg in _steps(x0 + 10, x1 - 22, 22):                              # the roof garden's shrubs
            gx, gy = at(xg + 6, WALL_FOOT - h - 8, mid)
            put(ellipse_d(gx, gy - 1.6, 3, 2.2), P.LEAF, INK, 0.5)
        ax, ay = at(x1 - 16, WALL_FOOT - h - 8, mid)
        c.line(f"M{n(ax)},{n(ay)} v-9 M{n(ax - 2.5)},{n(ay - 7)} h5", 0.9, INK)          # an antenna
        for i, y in enumerate(_steps(WALL_FOOT - h + 16, WALL_FOOT - 40, 24)):
            put(" ".join(front(x, x + 12, y, y + 12, mid) for x in _steps(x0 + 10, x1 - 20, 22)),
                rnd.choice((P.YELLOW_PALE, mix(P.YELLOW_PALE, P.PINK_PALE, 0.6), lighten(P.GLOW, 0.4), P.SUN)),
                INK, 0.4)
            if i % 2:                                                          # balconies
                put(" ".join(front(x - 3, x + 15, y + 12, y + 16, mid) for x in _steps(x0 + 10, x1 - 20, 44)),
                    P.METAL_LIGHT, INK, 0.4)
        put(front(x0, x1, WALL_FOOT - h + 2, WALL_FOOT - h + 6, mid), P.GLOW, P.GLOW, 0.1)   # the light trim
        put(front(x0 + 8, x1 - 8, WALL_FOOT - 30, WALL_FOOT - 4, mid), mix(P.SUN, P.YELLOW_PALE, 0.5), INK, 0.5)
    for x, y, color in ((300, WALL_FOOT - 60, P.PINK), (520, WALL_FOOT - 70, P.GREEN)):   # signs: a heart, a leaf
        cx, cy = at(x, y, mid)
        put(_circle(cx, cy, 5), P.CARD, INK, 0.7)
        put(f"M{n(cx)},{n(cy + 2.6)} l-2.8,-2.8 a1.6,1.6 0 0 1 2.8,-1.6 a1.6,1.6 0 0 1 2.8,1.6 Z"
            if color == P.PINK else ellipse_d(cx, cy, 1.6, 3.2), color, INK, 0.4)
    flush()
    # the square: warm paving in rings, the fountain, market stalls, trees in planters
    sq0, sq1 = 0.62, mid
    square = _poly([at(lo - 80, WALL_FOOT, sq0), at(hi + 80, WALL_FOOT, sq0), at(hi + 300, WALL_FOOT, sq1),
                    at(lo - 300, WALL_FOOT, sq1)])
    c.add(f'<path d="{square}" fill="{mix(P.SAND, P.SUN, 0.35)}"/>')
    fx, fy = at(VP_X, WALL_FOOT, 0.5)
    for rr in (60, 44):
        c.line(ellipse_d(fx, fy, rr * 0.5, rr * 0.5 * 0.16), 0.6, darken(P.SAND, 0.75))
    put(f"M{n(fx - 17)},{n(fy - 3)} V{n(fy)} A17,3 0 0 0 {n(fx + 17)},{n(fy)} V{n(fy - 3)} Z", P.METAL_PALE, INK, 0.8)
    put(ellipse_d(fx, fy - 3, 17, 3), P.WATER, INK, 0.8)
    c.line(" ".join(f"M{n(fx)},{n(fy - 10)} Q{n(fx + d)},{n(fy - 20)} {n(fx + 2.2 * d)},{n(fy - 4)}"
                    for d in (-6, -3, 3, 6)), 1.4, P.WATER_LIGHT)
    put(_rect(fx - 1.4, fy - 11, 2.8, 8), P.METAL, INK, 0.5)
    for x, way in ((392, -1), (448, 1)):                                      # the stalls, striped awnings
        (sx0, sy0), (sx1, sy1) = at(x - 22, WALL_FOOT - 30, 0.56), at(x + 22, WALL_FOOT, 0.56)
        put(_rect(sx0, sy0 + 3, sx1 - sx0, sy1 - sy0 - 3), P.WOOD, INK, 0.6)
        stripes = [_rect(sx0 + i * (sx1 - sx0) / 6, sy0, (sx1 - sx0) / 12, 4) for i in range(6)]
        put(_rect(sx0 - 1, sy0, sx1 - sx0 + 2, 4), P.CARD, INK, 0.6)
        put(" ".join(stripes), P.RED if way < 0 else P.TEAL, P.RED if way < 0 else P.TEAL, 0.1)
        put(" ".join(_circle(sx0 + 3 + i * 3.4, sy0 + 8, 1.3) for i in range(5)),
            P.ORANGE if way < 0 else P.GREEN, INK, 0.3)
    for x, t in ((374, 0.46), (466, 0.46), (404, 0.6), (436, 0.6)):        # trees in planters
        bx, by = at(x, WALL_FOOT, t)
        k = t * 0.9
        put(_rect(bx - 6 * k, by - 7 * k, 12 * k, 7 * k), P.TERRACOTTA, INK, 0.6)
        put(_rect(bx - 0.8 * k, by - 18 * k, 1.6 * k, 11 * k), P.TRUNK, INK, 0.3)
        put(_circle(bx, by - 22 * k, 8 * k), P.LEAF_LIGHT if x > VP_X else P.LEAF, INK, 0.6)
    flush()
    # the street: a warm circuit road with its lit traces and pads, a pavement each side
    s0 = sq0
    road = _poly([at(lo - 4, WALL_FOOT, 1), at(hi + 4, WALL_FOOT, 1), at(hi + 4, WALL_FOOT, s0),
                  at(lo - 4, WALL_FOOT, s0)])
    c.add(f'<path d="{road}" fill="{mix(P.CRUST, P.CHARCOAL, 0.35)}"/>')
    for a, b in ((lo, lo + 16), (hi - 16, hi)):
        put(_poly([at(a, WALL_FOOT, 1), at(b, WALL_FOOT, 1), at(b, WALL_FOOT, s0), at(a, WALL_FOOT, s0)]),
            mix(P.SAND, P.CRUST, 0.3), INK, 0.5)
    traces = " ".join(f"M{n(at(x, WALL_FOOT, 1)[0])},{n(WALL_FOOT)} L{n(at(x, WALL_FOOT, s0)[0])},"
                      f"{n(at(x, WALL_FOOT, s0)[1])}" for x in _steps(lo + 24, hi - 24, (hi - lo - 48) / 5))
    c.add(f'<path d="{traces}" fill="none" stroke="{P.GOLD_LIGHT}" stroke-width="3.4" stroke-opacity=".5"/>'
          f'<path d="{traces}" fill="none" stroke="{P.SUN}" stroke-width="1.3"/>')
    put(" ".join(_rect(at(x, WALL_FOOT, t)[0] - 2.4 * t, at(x, WALL_FOOT, t)[1] - 1.2 * t, 4.8 * t, 2.4 * t)
                 for t in (0.92, 0.78, 0.68) for x in _steps(lo + 24, hi - 24, (hi - lo - 48) / 5)), P.GOLD, INK, 0.4)
    # the street's facades, block by block: cool shade on the left, sunlit on the right; shops under awnings at the
    # foot, windows lit in many colours, balconies, cornices, a light trim along each top
    cuts = (1.0, 0.9, 0.8, 0.71, s0)
    colors = (P.PLUM, P.TEAL, P.ORANGE, P.BLUE, P.PINK, P.GREEN, P.VIOLET, P.YELLOW)
    for way, xf in ((-1, lo + 2), (1, hi - 2)):
        for i, (ta, tb) in enumerate(zip(cuts, cuts[1:], strict=False)):
            color = colors[(i * 2 + (way > 0)) % len(colors)]
            tone = mix(mix(color, P.METAL_PALE, 0.5), P.INDIGO if way < 0 else P.SUN, 0.28)
            height = rnd.choice((150, 175, 200))
            put(side(xf, WALL_FOOT, WALL_FOOT - height, ta, tb), tone, INK, 1.1 * ta)
            put(side(xf, WALL_FOOT - height, WALL_FOOT - height - 6, ta, tb), darken(tone, 0.78), INK, 0.8 * ta)
            put(side(xf, WALL_FOOT - height + 2, WALL_FOOT - height + 5, ta, tb), P.GLOW, P.GLOW, 0.1)
            span = ta - tb
            for y in _steps(WALL_FOOT - height + 14, WALL_FOOT - 56, 22):
                for f in (0.16, 0.56):
                    put(side(xf, y, y + 12, ta - span * f, ta - span * (f + 0.26)),
                        rnd.choice((P.YELLOW_PALE, mix(P.YELLOW_PALE, P.PINK_PALE, 0.6), lighten(P.GLOW, 0.45),
                                    mix(P.SUN, P.YELLOW_PALE, 0.4))), INK, 0.5 * ta)
                put(_poly([at(xf, y + 13, ta - span * 0.1), at(xf, y + 13, ta - span * 0.9),
                           at(xf - way * 6, y + 15, ta - span * 0.9), at(xf - way * 6, y + 15, ta - span * 0.1)]),
                    P.METAL_LIGHT, INK, 0.5 * ta)                                  # a balcony
            put(side(xf, WALL_FOOT - 40, WALL_FOOT - 6, ta - span * 0.12, tb + span * 0.12),
                mix(P.SUN, P.YELLOW_PALE, 0.5), INK, 0.7 * ta)                     # the shop window
            awning = _poly([at(xf, WALL_FOOT - 48, ta - span * 0.06), at(xf, WALL_FOOT - 48, tb + span * 0.06),
                            at(xf - way * 14, WALL_FOOT - 38, tb + span * 0.06),
                            at(xf - way * 14, WALL_FOOT - 38, ta - span * 0.06)])
            put(awning, (P.RED, P.TEAL, P.YELLOW, P.PLUM)[(i + (way > 0)) % 4], INK, 0.8 * ta)
    flush()
    # across the street: bunting and a string of lights; along it the lamps and the monorail with its train
    for t, kind in ((0.86, "flags"), (0.74, "lights")):
        (ax, ay), (bx, by) = at(lo + 2, WALL_FOOT - 120, t), at(hi - 2, WALL_FOOT - 120, t)
        sag = 9 * t
        pts = [(ax + (bx - ax) * u, ay + (by - ay) * u + sag * 4 * u * (1 - u)) for u in (i / 8 for i in range(9))]
        c.line("M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts), 0.8, INK)
        for j, (x, y) in enumerate(pts[1:-1]):
            if kind == "flags":
                put(f"M{n(x - 3 * t)},{n(y)} H{n(x + 3 * t)} L{n(x)},{n(y + 7 * t)} Z",
                    (P.RED, P.SUN, P.TEAL, P.PINK, P.GREEN)[j % 5], INK, 0.5)
            else:
                put(_circle(x, y + 2 * t, 3.4 * t), P.YELLOW_PALE, P.YELLOW_PALE, 0.1)
                put(_circle(x, y + 2 * t, 1.6 * t), P.SUN, INK, 0.4)
    for xp, t in ((lo + 14, 0.7), (hi - 14, 0.7), (lo + 14, 0.85), (hi - 14, 0.85)):     # street lamps
        (bx, by), (tx_, ty) = at(xp, WALL_FOOT, t), at(xp, WALL_FOOT - 80, t)
        c.line(f"M{n(bx)},{n(by)} V{n(ty)}", 1.4 * t, INK)
        put(_circle(tx_, ty, 4.4 * t), P.YELLOW_PALE, P.YELLOW_PALE, 0.1)
        put(_circle(tx_, ty, 2.2 * t), P.SUN, INK, 0.5)
    beam = [at(hi - 22, WALL_FOOT - 140, 1.0), at(hi - 22, WALL_FOOT - 140, mid)]     # the monorail's beam
    c.line(f"M{n(beam[0][0])},{n(beam[0][1])} L{n(beam[1][0])},{n(beam[1][1])}", 4.2, INK)
    c.line(f"M{n(beam[0][0])},{n(beam[0][1])} L{n(beam[1][0])},{n(beam[1][1])}", 2.4, P.METAL_LIGHT)
    for t in (0.8, 0.55):
        (px, py), (qx, qy) = at(hi - 22, WALL_FOOT - 140, t), at(hi - 22, WALL_FOOT - 16, t)
        c.line(f"M{n(px)},{n(py)} L{n(qx)},{n(qy)}", 1.8 * t, P.METAL_DARK)
    train = _poly([at(hi - 22, WALL_FOOT - 168, 0.93), at(hi - 22, WALL_FOOT - 168, 0.76),
                   at(hi - 22, WALL_FOOT - 142, 0.76), at(hi - 22, WALL_FOOT - 142, 0.93)])
    put(train, P.TEAL, INK, 1.0)
    put(" ".join(_poly([at(hi - 22, WALL_FOOT - 162, t0), at(hi - 22, WALL_FOOT - 162, t0 - 0.03),
                        at(hi - 22, WALL_FOOT - 152, t0 - 0.03), at(hi - 22, WALL_FOOT - 152, t0)])
                 for t0 in (0.91, 0.86, 0.81)), P.YELLOW_PALE, INK, 0.5)
    flush()
    # robots walking: in the street and across the square
    for x, t in ((398, 0.82), (446, 0.7), (384, 0.54), (458, 0.5), (414, 0.45)):
        bx, by = at(x, WALL_FOOT, t)
        k = t * 0.55
        put(_rect(bx - 3.5 * k, by - 12 * k, 2.6 * k, 12 * k) + _rect(bx + 0.9 * k, by - 12 * k, 2.6 * k, 12 * k),
            P.METAL, INK, 0.5)                                                    # legs
        put(rounded_rect_d(bx - 8 * k, by - 30 * k, 16 * k, 19 * k, 4 * k), P.ORANGE, INK, 0.7)
        put(rounded_rect_d(bx - 9 * k, by - 46 * k, 18 * k, 15 * k, 3.5 * k), P.ORANGE, INK, 0.7)
        put(rounded_rect_d(bx - 6.5 * k, by - 43.5 * k, 13 * k, 10 * k, 2.5 * k), P.SCREEN, INK, 0.4)
        put(_circle(bx - 2.5 * k, by - 39 * k, 1.2 * k) + _circle(bx + 2.5 * k, by - 39 * k, 1.2 * k), P.GLOW,
            P.GLOW, 0.1)
    flush()
    # the door's two leaves, swung open into the city against the sides: plates, rivets, hinge straps
    for x0 in (lo, hi):
        t_far = 0.9
        near_top, foot = top + 26, WALL_FOOT
        leaf = [(x0, near_top), at(x0, near_top, t_far), at(x0, foot, t_far), (x0, foot)]
        c.add(f'<path d="{_poly(leaf)}" fill="{mix(P.METAL_DARK, P.SUN, 0.18)}" stroke="{INK}" stroke-width="2"/>')
        panels = []
        for f0, f1 in ((0.08, 0.31), (0.36, 0.64), (0.69, 0.92)):
            ya, yb = near_top + (foot - near_top) * f0, near_top + (foot - near_top) * f1
            ta, tb = 1 - (1 - t_far) * 0.2, 1 - (1 - t_far) * 0.8
            panels.append(_poly([at(x0, ya, ta), at(x0, ya, tb), at(x0, yb, tb), at(x0, yb, ta)]))
        c.add(f'<path d="{" ".join(panels)}" fill="{mix(P.METAL, P.SUN, 0.22)}" stroke="{INK}" stroke-width="1.2"/>')
        rivets = "".join(_circle(*at(x0, near_top + (foot - near_top) * f, ta), 1.2)
                         for f in (0.04, 0.335, 0.665, 0.96) for ta in (0.99, 0.95, 0.91))
        c.add(f'<path d="{rivets}" fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width=".6"/>')
        for f in (0.18, 0.82):                                       # the hinge straps
            y = near_top + (foot - near_top) * f
            strap = [(x0, y - 3), at(x0, y - 3, 0.94), at(x0, y + 3, 0.94), (x0, y + 3)]
            c.add(f'<path d="{_poly(strap)}" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width=".8"/>')
    return c.render()


def _city(s: Stage) -> None:
    """The skyline behind the wall, every building on its own spot with air round it, and the cable over it."""
    c = Canvas()
    base = WALL_TOP + 4
    boxes = [server_rack(c, 14, 74, 360, base, 1, 71), memory_stick(c, 196, 240, 292, base, 237),
             server_rack(c, 692, 752, 344, base, 2, 695), memory_stick(c, 780, 822, 300, base, 783)]
    left = chip_tower(c, 102, 170, 190, base, 3, 167)
    right = chip_tower(c, 612, 680, 168, base, 4, 615)
    boxes += [left["box"], right["box"]]
    boxes.append(capacitor(c, 258, 296, 430, base, P.BLUE, 294))
    boxes.append(capacitor(c, 546, 584, 440, base, P.INDIGO, 548))
    boxes.append(fan_hall(c, VP_X, base, 112))
    s.put(base, c.render(), boxes, "city", group="city")
    ledger(s)
    a = port(s, *left["right"], 1, 0, "city")
    b = port(s, *right["left"], -1, 0, "city")
    connect(s, a, b, "cable", 4.2, via=((VP_X, 286),), depth=base + 0.5, lead=40, color=backlit(P.CHARCOAL))
    points = s.links[-1].points
    x = 262
    y = min(points, key=lambda p: abs(p[0] - x))[1]
    car, box = cable_car(x, y, 1.0)
    s.put(base + 0.6, car, box, "cable car", group="city")


# ============================================================================ the road
# The road comes straight from the gate, bends near the reader and runs off across the foot of the page (a straight
# road of slabs would read as a staircase, and the five would walk into it seen from behind). Laid out on the
# ground and projected (`road.py`): f is chosen so that the road is as wide at the gate as the gate's opening, and
# the crosswise stretch fills the band of the page from about 960 down to 1150.
ROAD = Road(vx=VP_X, hz=HORIZON, f=1184.0, half=0.476, gate_z=1184.0 / (WALL_FOOT - HORIZON), near_z=2.63,
            end_x=-0.977, radius=0.977, left_x=-1.5)        # straight at the gate; the bend wholly on the page
CROSS_Y = HORIZON + ROAD.f / ROAD.near_z            # the middle of the crosswise stretch on the page


def _spill(s: Stage) -> None:
    """The warm light from the gate spilling down the far end of the road, fading as it comes."""
    spill = Canvas()
    end = next(i for i, (_, z, _, _) in enumerate(ROAD.line) if HORIZON + ROAD.f / z > 820)
    for u, a in ((ROAD.half, 0.22), (ROAD.half * 0.7, 0.26), (ROAD.half * 0.4, 0.3)):
        spill.add(f'<path d="{ROAD.strip(-u, u, 0, end)}" fill="{mix(P.YELLOW_PALE, P.SUN, 0.3)}" '
                  f'fill-opacity="{a}"/>')
    s.put(WALL_FOOT + 0.3, spill.render())


FLOWERS = (P.PINK, P.YELLOW, P.WHITE, P.VIOLET, P.RED)


def dots(c: Canvas, points: list[tuple[float, float]], d: float, fill: str, rim: float = 1.2) -> None:
    """Round dots of diameter d - flower petals, grapes, hearts - each a stroke with round caps over a slightly
    wider ink one: a circle on the page at a fraction of the weight of a drawn circle in the printed file."""
    if not points:
        return
    path = "".join(f"M{n(x)},{n(y)}h0" for x, y in points)
    c.add(f'<path d="{path}" stroke="{INK}" stroke-width="{n(d + rim)}" stroke-linecap="round" fill="none"/>'
          f'<path d="{path}" stroke="{fill}" stroke-width="{n(d)}" stroke-linecap="round" fill="none"/>')


def _flowers(c: Canvas) -> None:
    """Flowers along both verges, following the road round its bend: two leaves at the foot, five-petalled heads on
    short stems, sized by their distance, the nearest the size of a fist."""
    rnd = random.Random(11)
    leaves: dict[float, list[str]] = {}
    stems: list[str] = []
    heads: dict[tuple[str, float], list[tuple[float, float]]] = {}
    hearts: dict[float, list[tuple[float, float]]] = {}
    out = ROAD.half + ROAD.kerb
    for i in range(0, len(ROAD.line), 11):
        for side in (-1, 1):
            gx, gz = ROAD.at(i, side * (out + ROAD.verge * rnd.uniform(0.3, 0.7)))
            if gz <= 0.4:
                continue
            x, y = ROAD.page(gx, gz)
            if not -10 < x < W + 10 or y > H + 6:
                continue
            k = scale_at(y) / 100
            if k < 0.6:                                  # too far to see as flowers
                continue
            kk = round(k, 1)
            leaves.setdefault(kk, []).append(f"M{n(x - 4 * k)},{n(y - 1 * k)}h{n(2.6 * k)}M{n(x + 1.4 * k)},"
                                             f"{n(y - 1 * k)}h{n(2.6 * k)}")
            for dx, tall in ((-1.8, 6.5), (1.2, 8.5), (3, 5.5))[:rnd.choice((2, 3))]:
                fx, fy = x + dx * k, y - tall * k
                stems.append(f"M{n(x + dx * 0.3 * k)},{n(y - 0.6 * k)} L{n(fx)},{n(fy)}")
                r = 1.35 * k
                heads.setdefault((rnd.choice(FLOWERS), kk), []).extend(
                    (fx + math.cos(a) * r, fy + math.sin(a) * r) for a in (j * 2 * math.pi / 5 - math.pi / 2
                                                                           for j in range(5)))
                hearts.setdefault(kk, []).append((fx, fy))
    for kk, parts in leaves.items():
        c.add(f'<path d="{"".join(parts)}" stroke="{INK}" stroke-width="{n(2.6 * kk + 1.2)}" stroke-linecap="round"/>'
              f'<path d="{"".join(parts)}" stroke="{P.LEAF}" stroke-width="{n(2.6 * kk)}" stroke-linecap="round"/>')
    c.line(" ".join(stems), 1.1, P.LEAF_DARK)
    for (color, kk), pts in heads.items():
        dots(c, pts, 2.2 * kk, color, 1.0)
    for kk, pts in hearts.items():
        dots(c, pts, 1.5 * kk, P.SUN, 0.8)


def lamp(x: float, foot: float, k: float, facing: int) -> tuple[str, tuple]:
    """A street lamp at the kerb: a cast-iron post on its base, the arm over the road, the lantern lit."""
    c = Canvas()
    h = 200 * k
    sw = 1.6 * min(1, k + 0.3)
    c.shape(_rect(x - 2.6 * k, foot - h, 5.2 * k, h - 20 * k), P.CHARCOAL, sw=sw, light=None)
    # the cast-iron base: a square plinth on the kerb, a flared foot, a collar where the post goes in
    c.shape(_rect(x - 8 * k, foot - 4 * k, 16 * k, 4 * k), P.CHARCOAL, sw=sw, light=None)
    c.shape(f"M{n(x - 6.5 * k)},{n(foot - 4 * k)} Q{n(x - 5 * k)},{n(foot - 14 * k)} {n(x - 3.2 * k)},"
            f"{n(foot - 20 * k)} H{n(x + 3.2 * k)} Q{n(x + 5 * k)},{n(foot - 14 * k)} {n(x + 6.5 * k)},"
            f"{n(foot - 4 * k)} Z", P.CHARCOAL, sw=sw, light=None)
    c.shape(_rect(x - 4.2 * k, foot - 23 * k, 8.4 * k, 3 * k), P.CHARCOAL, sw=sw, light=None)
    c.shape(_rect(x - 3.8 * k, foot - h * 0.62, 7.6 * k, 2.6 * k), P.CHARCOAL, sw=sw, light=None)
    c.line(f"M{n(x - 1.2 * k)},{n(foot - 18 * k)} L{n(x - 2.8 * k)},{n(foot - 6 * k)} "
           f"M{n(x - 1)},{n(foot - h + 10 * k)} V{n(foot - 26 * k)}", max(0.6, 1.2 * k), P.METAL_DARK)
    ax = x + facing * 34 * k
    c.line(f"M{n(x)},{n(foot - h + 6 * k)} Q{n(x + facing * 18 * k)},{n(foot - h - 6 * k)} {n(ax)},"
           f"{n(foot - h + 4 * k)}", 3.4 * k, P.CHARCOAL)
    c.add(f'<circle cx="{n(ax)}" cy="{n(foot - h + 20 * k)}" r="{n(22 * k)}" fill="{P.YELLOW_PALE}" '
          f'fill-opacity=".35"/>')
    c.shape(f"M{n(ax - 9 * k)},{n(foot - h + 8 * k)} H{n(ax + 9 * k)} L{n(ax + 6 * k)},{n(foot - h + 26 * k)} "
            f"H{n(ax - 6 * k)} Z", P.YELLOW_PALE, sw=1.6 * min(1, k + 0.3), light=None)
    c.shape(f"M{n(ax - 12 * k)},{n(foot - h + 9 * k)} L{n(ax)},{n(foot - h)} L{n(ax + 12 * k)},"
            f"{n(foot - h + 9 * k)} Z", P.CHARCOAL, sw=1.4 * min(1, k + 0.3), light=None)
    lo, hi = min(x - 9 * k, ax - 23 * k), max(x + 9 * k, ax + 23 * k)
    return c.render(), (lo, foot - h - 4 * k, hi, foot)


def _lamps(s: Stage) -> None:
    """Street lamps along the far kerb of the near stretch and the kerbs of the straight from the gate, at even steps
    of ground, about as tall as the professor; one is left out wherever it would stand against the gate, a tree, the
    cart or one of the five."""
    spots = [i for i, (_, _, tx, tz) in enumerate(ROAD.line) if tz < -0.9][::40]
    spots += [i for i, (_, _, tx, _) in enumerate(ROAD.line) if tx < -0.99][::32]
    for i in spots:
        for side in (-1, 1):
            gx, gz = ROAD.at(i, side * (ROAD.half + ROAD.kerb * 0.5))
            x, y = ROAD.page(gx, gz)
            k = scale_at(y) * 0.95 / 200
            if y - 200 * k - 4 * k < WALL_FOOT + 12 or not -20 < x < W + 20:
                continue
            art, box = lamp(x, y, k, -side if ROAD.line[i][3] < -0.9 else 1)
            if box[0] < 4 or box[2] > W - 4 or not s.free(box, 4):
                continue
            s.put(y, art, box, f"lamp{round(y)}{round(x)}", group="city", backdrop=True)


# ============================================================================ the fields
ORCHARD = 716.0              # wheat from the city's apron to here, then the orchards
TRACK = (744.0, 760.0)       # the farm track across the fields, between the orchards and the vineyards
NEAR = 850.0                 # the vineyards end and the cabbages begin


def _sides(f0: float, f1: float) -> tuple[tuple[float, float], tuple[float, float]]:
    """A stretch of feet on the left of the road and the same stretch mirrored on the right."""
    return (f0, f1), (2 * VP_X - f1, 2 * VP_X - f0)


def _fields(c: Canvas, s: Stage) -> None:
    """The fields on both sides, in rows running to the city: orchards and wheat far off, a farm track, vineyards,
    then cabbages near; a grass verge along each kerb."""
    c.add(f'<path d="{_rect(-6, PLAZA, W + 12, H - PLAZA + 6)}" fill="{P.GRASS}"/>')
    orchard, near_f = (-1800.0, -600.0), -1300.0
    whole = ((-5200.0, 2 * VP_X + 5200),)                        # the road is laid over them afterwards
    for lo, hi in whole:                                         # wheat by the city
        c.add(f'<path d="{_quad(ORCHARD, PLAZA, lo, hi)}" fill="{mix(P.SUN, P.CRUST, 0.45)}"/>')
        c.add(f'<path d="{" ".join(_quad(ORCHARD, PLAZA, f, f + 24) for f in _steps(lo + 30, hi - 40, 60))}" '
              f'fill="{mix(P.SUN, P.YELLOW_PALE, 0.4)}"/>')
        rnd = random.Random(21)
        ears = []
        for y in _depths(ORCHARD - 1, PLAZA + 2, 0.003):              # the ears of wheat, row on row
            k = scale_at(y) / 100
            x = rnd.uniform(0, 6) * k
            while x < W:
                ears.append(f"M{n(x)},{n(y)} l{n(1.2 * k)},{n(-6 * k)}")
                x += rnd.uniform(5, 9) * k
        c.line(" ".join(ears), 0.9, darken(P.SUN, 0.7), 0.8)
    for lo, hi in whole:                                         # the orchards' grass, a meadow beside them
        c.add(f'<path d="{_quad(TRACK[0], ORCHARD, lo, hi)}" fill="{P.GRASS_DARK}"/>')
    c.add(f'<path d="{_rect(-6, TRACK[0], W + 12, TRACK[1] - TRACK[0])}" fill="{mix(P.SAND, P.CRUST, 0.3)}"/>')
    c.line(f"M-6,{TRACK[0]} H{W + 6} M-6,{TRACK[1]} H{W + 6}", 1.4, darken(P.SAND, 0.75))
    for lo, hi in ((near_f, 2 * VP_X - near_f),):                # the vineyards
        c.add(f'<path d="{_quad(NEAR, TRACK[1], lo, hi)}" fill="{mix(P.SAND, P.CRUST, 0.45)}"/>')
        for f in _steps(lo + 40, hi - 20, 64):
            posts = []
            for y in _depths(NEAR - 2, TRACK[1] + 4, 0.0016):
                k = scale_at(y) / 100
                posts.append(f"M{n(edge_x(y, f))},{n(y)} V{n(y - 30 * k)}")
            c.line(" ".join(posts), 2.2, P.WOOD_DARK)
            top = [(edge_x(y, f), y - 30 * scale_at(y) / 100) for y in (NEAR - 2, TRACK[1] + 4)]
            bot = [(edge_x(y, f), y - 12 * scale_at(y) / 100) for y in (TRACK[1] + 4, NEAR - 2)]
            c.add(f'<path d="{_poly(top + bot)}" fill="{P.LEAF}" stroke="{P.LEAF_DARK}" stroke-width="1.4" '
                  f'stroke-linejoin="round"/>')
            bunches: dict[float, list[tuple[float, float]]] = {}
            veins = []
            for y in _depths(NEAR - 8, TRACK[1] + 8, 0.0019):        # bunches of grapes under the leaves
                k = scale_at(y) / 100
                gx, gy = edge_x(y, f) + 5 * k, y - 11 * k
                bunches.setdefault(round(k, 1), []).extend(
                    (gx + dx * k, gy + dy * k) for dx, dy in ((-2, 0), (2, 0), (0, 3.2), (-1, 6), (1.4, 5.6)))
                lx, ly = edge_x(y, f) - 4 * k, y - 24 * k              # a leaf's veins in the green band
                veins.append(f"M{n(lx)},{n(ly)} l{n(3 * k)},{n(4 * k)} l{n(3 * k)},{n(-4 * k)} M{n(lx + 3 * k)},"
                             f"{n(ly + 4 * k)} v{n(4 * k)}")
            c.line(" ".join(veins), 0.8, P.LEAF_DARK, 0.8)
            for kk, pts in bunches.items():
                dots(c, pts, 3.8 * kk, P.PLUM, 0.8)
    for lo, hi in ((near_f, 2 * VP_X - near_f),):                # the cabbages
        c.add(f'<path d="{_quad(H + 6, NEAR, lo, hi)}" fill="{mix(P.CRUST_RAW, P.WOOD_PALE, 0.4)}"/>')
        rows: dict[float, list[tuple[float, float, float]]] = {}
        for f in _steps(lo + 40, hi - 24, 62):
            c.add(f'<path d="{_quad(H + 6, NEAR, f - 7, f + 7)}" fill="{mix(P.CRUST_RAW, P.KITCHEN_KRAFT, 0.5)}"/>')
            for y in _depths(1180, NEAR + 8, 0.0003):
                r = 0.03 * (y - HORIZON)
                rows.setdefault(round(y, 2), []).append((edge_x(y, f), y - r * 0.6, r))
        for y in sorted(rows):                                   # far rows first; each row in four paths
            heads = [h for h in rows[y] if -20 < h[0] < W + 20 and not ROAD.contains(h[0], y, 0.0)]
            if not heads:
                continue
            r = heads[0][2]
            body = "".join(f"M{n(x - rr * 0.45)},{n(yy)}h{n(rr * 0.9)}" for x, yy, rr in heads)
            outer = "".join(f"M{n(x - rr * 1.1)},{n(yy + rr * 0.3)}l{n(rr * 0.5)},{n(-rr * 0.35)}M{n(x + rr * 1.1)},"
                            f"{n(yy + rr * 0.3)}l{n(-rr * 0.5)},{n(-rr * 0.35)}" for x, yy, rr in heads)
            c.add(f'<path d="{outer}" stroke="{INK}" stroke-width="{n(r * 0.75 + 1.2)}" stroke-linecap="round"/>'
                  f'<path d="{outer}" stroke="{P.LEAF_DARK}" stroke-width="{n(r * 0.75)}" stroke-linecap="round"/>')
            lit = "".join(f"M{n(x - rr * 0.45)},{n(yy - rr * 0.25)}h{n(rr * 0.4)}" for x, yy, rr in heads)
            veins = " ".join(f"M{n(x - rr * 0.5)},{n(yy + rr * 0.1)} l{n(rr)},{n(-rr * 0.35)}" for x, yy, rr in heads)
            c.add(f'<path d="{body}" stroke="{INK}" stroke-width="{n(r * 1.56 + max(1.2, r * 0.2))}" '
                  f'stroke-linecap="round"/><path d="{body}" stroke="{P.LEAF}" stroke-width="{n(r * 1.56)}" '
                  f'stroke-linecap="round"/><path d="{lit}" stroke="{P.LEAF_LIGHT}" stroke-width="{n(r * 0.7)}" '
                  f'stroke-linecap="round"/>')
            c.line(veins, max(0.6, r * 0.1), P.LEAF_DARK)
    c.fade(-6, PLAZA, W + 12, 70, [(0, mix(P.PINK_PALE, P.SUN, 0.4), 0.5), (1, mix(P.PINK_PALE, P.SUN, 0.4), 0.0)])
    for lo, hi in _sides(*orchard):                              # the orchards' trees, row by row
        for f in _steps(lo + 50, hi - 30, 110):
            for y in _depths(TRACK[0] - 4, ORCHARD + 2, 0.0045):
                k = scale_at(y) / 100
                x = edge_x(y, f)
                if ROAD.contains(x, y, 0.1):
                    continue
                s.put(y, _tree(x, y, k), (x - 22 * k, y - 62 * k, x + 22 * k, y), f"tree{round(y)}{round(f)}",
                      group="orchard", backdrop=True)


def _tree(x: float, y: float, k: float) -> str:
    """An apple tree of the orchard, `k` its size over 100."""
    c = Canvas()
    sw = max(0.9, 2.0 * k)
    c.shape(_rect(x - 3 * k, y - 22 * k, 6 * k, 22 * k), P.TRUNK, sw=sw, light=None)
    c.shape(f"M{n(x - 20 * k)},{n(y - 30 * k)} Q{n(x - 26 * k)},{n(y - 52 * k)} {n(x - 6 * k)},{n(y - 58 * k)} "
            f"Q{n(x + 10 * k)},{n(y - 66 * k)} {n(x + 20 * k)},{n(y - 48 * k)} Q{n(x + 26 * k)},{n(y - 28 * k)} "
            f"{n(x + 4 * k)},{n(y - 22 * k)} Q{n(x - 16 * k)},{n(y - 18 * k)} {n(x - 20 * k)},{n(y - 30 * k)} Z",
            P.LEAF, sw=sw, light=None)
    apples = "".join(_circle(x + dx * k, y + dy * k, 3 * k) for dx, dy in ((-10, -38), (6, -46), (10, -32), (-2, -28)))
    c.add(f'<path d="{apples}" fill="{P.RED}"/>')
    return c.render()


# ============================================================================ the agents at work
def _crate(x: float, y: float, k: float) -> str:
    """A wooden crate of apples standing at (x, y)."""
    c = Canvas()
    sw = max(0.8, 1.8 * k)
    c.shape(_rect(x - 14 * k, y - 16 * k, 28 * k, 16 * k), P.WOOD, sw=sw, light=None)
    c.line(f"M{n(x - 14 * k)},{n(y - 8 * k)} H{n(x + 14 * k)}", sw * 0.7, P.WOOD_DARK)
    for i, dx in enumerate((-8, 0, 8)):
        c.shape(_circle(x + dx * k, y - 18 * k, 4.6 * k), P.RED if i != 1 else P.GREEN, sw=sw * 0.8, light=None)
    return c.render()


def _tyre(c: Canvas, x: float, y: float, r: float, sw: float) -> None:
    """A tractor tyre: the treads' lugs round it, the rubber, the yellow rim and the hub."""
    lugs = " ".join(f"M{n(x + r * 0.92 * math.cos(a))},{n(y + r * 0.92 * math.sin(a))} "
                    f"L{n(x + r * 1.1 * math.cos(a))},{n(y + r * 1.1 * math.sin(a))}"
                    for a in (i * math.pi / 8 for i in range(16)))
    c.line(lugs, max(1.2, r * 0.22), INK)
    c.shape(_circle(x, y, r), P.CHARCOAL, sw=sw, light=None)
    c.shape(_circle(x, y, r * 0.5), P.SUN, sw=sw * 0.7, light=None)
    c.add(f'<path d="{_circle(x, y, r * 0.18)}" fill="{P.METAL}" stroke="{INK}" stroke-width="{n(sw * 0.5)}"/>')


def tractor(s: Stage, x: float, y: float, k: float) -> None:
    """A little tractor going left with the agent at its wheel: the bonnet with its grille and exhaust pipe in front,
    the small front wheel; behind, the seat over the big treaded rear wheel, the driver on it - his legs out of sight
    behind the mudguard, his hands on the steering wheel. `x` is where the driver sits, `y` the ground."""
    from .characters import module
    from .scenes import PROFESSOR_HEIGHT
    mod = module("agent")
    ka = scale_at(y) / PROFESSOR_HEIGHT * mod.SCENE_SCALE
    guard_top = y - 38 * k
    feet = guard_top + (mod.FEET_Y - 220) * ka          # the mudguard's top under his body, below his hands
    sw = max(0.9, 2.0 * k)
    back = Canvas()
    back.shape(rounded_rect_d(x - 11 * k, feet - 120 * ka, 22 * k, guard_top - feet + 120 * ka + 2, 4 * k),
               P.DARK_BROWN, sw=sw, light=None)                                         # the seat's back
    for dx, dy, r in ((0, 0, 3.4), (5, -6, 4.4), (12, -10, 5.2)):                      # smoke from the pipe
        back.shape(_circle(x - 40 * k + dx * k, y - 64 * k + dy * k, r * k), mix(P.METAL_PALE, P.WHITE, 0.4),
                   sw=sw * 0.6, light=None)
    back.line(f"M{n(x - 40 * k)},{n(y - 36 * k)} V{n(y - 58 * k)}", 3.4 * k, INK)       # the exhaust pipe
    back.line(f"M{n(x - 40 * k)},{n(y - 36 * k)} V{n(y - 58 * k)}", 2 * k, P.METAL_DARK)
    s.put(y - 0.2, back.render(), [(x - 46 * k, y - 76 * k, x - 28 * k, y - 36 * k)], "tractor", group="tractor")
    s.actor("agent", x, feet, "type", "smile", tall=scale_at(y), group="tractor", depth=y - 0.1)
    front = Canvas()
    front.shape(rounded_rect_d(x - 50 * k, y - 22 * k, 62 * k, 9 * k, 2 * k), P.CHARCOAL, sw=sw, light=None)  # chassis
    bonnet = (f"M{n(x - 12 * k)},{n(y - 16 * k)} V{n(y - 36 * k)} H{n(x - 44 * k)} Q{n(x - 52 * k)},{n(y - 36 * k)} "
              f"{n(x - 52 * k)},{n(y - 28 * k)} V{n(y - 16 * k)} Z")
    front.shape(bonnet, P.RED, sw=sw, light=(-1.5 * k, -1.5 * k))
    front.line(" ".join(f"M{n(x - 49 * k + i * 2.4 * k)},{n(y - 31 * k)} V{n(y - 19 * k)}" for i in range(4)),
               1.1 * k, INK)                                                             # the grille
    front.line(f"M{n(x - 36 * k)},{n(y - 30 * k)} H{n(x - 18 * k)}", 1.2 * k, darken(P.RED, 0.6))
    _tyre(front, x - 40 * k, y - 9 * k, 9 * k, sw)                                        # the front wheel
    _tyre(front, x + 4 * k, y - 17 * k, 17 * k, sw)                                       # the rear wheel
    guard = (f"M{n(x - 18 * k)},{n(y - 17 * k)} A{n(22 * k)},{n(21 * k)} 0 0 1 {n(x + 26 * k)},{n(y - 17 * k)} "
             f"L{n(x + 21 * k)},{n(y - 17 * k)} A{n(17 * k)},{n(17 * k)} 0 0 0 {n(x - 13 * k)},{n(y - 17 * k)} Z")
    front.shape(guard, P.RED, sw=sw, light=None)                                          # the mudguard ...
    front.shape(f"M{n(x - 14 * k)},{n(guard_top + 2 * k)} H{n(x + 14 * k)} V{n(y - 24 * k)} H{n(x - 14 * k)} Z",
                P.RED, sw=sw, light=None)                                                 # ... and the seat's box
    hands_y = feet - (mod.FEET_Y - 208) * ka
    front.line(f"M{n(x - 2 * k)},{n(hands_y + 2 * k)} L{n(x - 14 * k)},{n(y - 34 * k)}", 2.6 * k, INK)  # the column
    front.line(f"M{n(x - 2 * k)},{n(hands_y + 2 * k)} L{n(x - 14 * k)},{n(y - 34 * k)}", 1.4 * k, P.METAL_DARK)
    wheel = ellipse_d(x, hands_y, 30 * ka, 7 * ka)                                        # the steering wheel
    front.add(f'<path d="{wheel}" fill="none" stroke="{INK}" stroke-width="{n(6 * ka + 1.6)}"/>'
              f'<path d="{wheel}" fill="none" stroke="{P.METAL_DARK}" stroke-width="{n(6 * ka)}"/>')
    s.put(y, front.render(), [(x - 52 * k, y - 38 * k, x + 28 * k, y)], "tractor body", group="tractor")


def handcart(x: float, y: float, k: float) -> tuple[str, tuple]:
    """A two-wheeled handcart piled with crates of apples, its handles to the left."""
    c = Canvas()
    sw = max(0.9, 2.0 * k)
    c.line(f"M{n(x - 30 * k)},{n(y - 26 * k)} L{n(x - 52 * k)},{n(y - 34 * k)}", 2.6 * k, P.WOOD_DARK)
    c.shape(_rect(x - 32 * k, y - 32 * k, 64 * k, 12 * k), P.WOOD, sw=sw, light=None)
    for dx, dy in ((-18, 0), (0, 0), (18, 0), (-9, -18), (9, -18)):
        c.add(_crate(x + dx * k, y - 32 * k + dy * k, 0.6 * k))
    c.shape(_circle(x, y - 12 * k, 12 * k), P.WOOD_DARK, sw=sw, light=None)
    c.line(" ".join(f"M{n(x)},{n(y - 12 * k)} l{n(10 * k * math.cos(a))},{n(10 * k * math.sin(a))}"
                    for a in (0, 1.05, 2.1, 3.14, 4.19, 5.24)), 1.2 * k, P.WOOD)
    return c.render(), (x - 54 * k, y - 63 * k, x + 33 * k, y)


def watering_can(x: float, y: float, k: float) -> str:
    """A watering can held by its top handle at (x, y), the spout to the right; `k` is the holder's size over 100."""
    c = Canvas()
    c.line(f"M{n(x - 7 * k)},{n(y + 6 * k)} Q{n(x)},{n(y - 7 * k)} {n(x + 7 * k)},{n(y + 6 * k)}", 2.4 * k, P.GREEN)
    c.shape(rounded_rect_d(x - 10 * k, y + 6 * k, 20 * k, 16 * k, 3 * k), P.GREEN, sw=1.6 * k, light=None)
    c.line(f"M{n(x + 9 * k)},{n(y + 18 * k)} L{n(x + 22 * k)},{n(y + 8 * k)}", 2.6 * k, P.GREEN)
    c.add(f'<path d="M{n(x + 22 * k)},{n(y + 8 * k)} l3,6 M{n(x + 24 * k)},{n(y + 7 * k)} l5,5" stroke="{P.WATER}" '
          f'stroke-width="{n(1.4 * k)}" stroke-linecap="round" fill="none"/>')
    return c.render()


def basket(x: float, y: float, k: float) -> tuple[str, tuple]:
    """A wicker basket of apples standing at (x, y)."""
    c = Canvas()
    sw = max(0.8, 1.6 * k)
    c.shape(f"M{n(x - 13 * k)},{n(y - 16 * k)} H{n(x + 13 * k)} L{n(x + 10 * k)},{n(y)} H{n(x - 10 * k)} Z",
            P.KITCHEN_KRAFT, sw=sw, light=None)
    for i, dx in enumerate((-7, 0, 7)):
        c.shape(_circle(x + dx * k, y - 18 * k, 4.4 * k), P.RED if i != 1 else P.GREEN, sw=sw * 0.8, light=None)
    c.line(f"M{n(x - 11 * k)},{n(y - 8 * k)} H{n(x + 11 * k)}", sw * 0.6, P.WOOD_DARK)
    return c.render(), (x - 14 * k, y - 23 * k, x + 14 * k, y)


def _agent_box(x: float, feet: float, tall: float, extra: float = 0.0) -> tuple:
    """Where an agent stood at (x, feet) `tall` would be, as `Stage.actor` boxes it, `extra` of its height wider on
    the right for what it holds out."""
    from .characters import module
    from .scenes import PROFESSOR_HEIGHT
    mod = module("agent")
    k = tall / PROFESSOR_HEIGHT * mod.SCENE_SCALE
    half, height = mod.SIZE[0] * 0.40 * k, (mod.FEET_Y - mod.HEAD_TOP) * k
    return (x - half * 1.05, feet - height, x + half * 1.05 + extra * height, feet)


def _spot(s: Stage, ys: tuple[float, float], feet: tuple[float, float], extra: float = 0.0,
          among: str = "") -> tuple[float, float]:
    """The first place in a field where an agent stands clear of everything placed so far but the group it works
    `among` (a picker stands among the orchard's trees)."""
    rows = int(abs(ys[1] - ys[0]) // 3) + 1
    for y in (ys[0] + (3 if ys[1] >= ys[0] else -3) * j for j in range(rows)):
        way = 1 if feet[1] >= feet[0] else -1
        for i in range(int(abs(feet[1] - feet[0]) // 15) + 1):
            f = feet[0] + way * 15 * i
            box = _agent_box(edge_x(y, f), y, scale_at(y), extra)
            clear = not any(b.group != among and b.hits(box, 5) for b in s.boxes) and not any(
                ROAD.contains(px, box[3], 0.05) for px in (box[0], box[2]))
            if box[0] >= 10 and box[2] <= W - 10 and box[1] >= WALL_FOOT + 6 and clear:
                return edge_x(y, f), y
    raise ValueError(f"no room left in the fields for an agent at {ys}, {feet}; "
                     f"{[(b.name, round(b.left), round(b.top), round(b.right)) for b in s.boxes if b.kind == 'actor']}")


def _workers(s: Stage) -> None:
    """The agents at work in the middle and far fields, each at a task one can read, sized by how far off they
    are: none more than half as tall as our agent on the road; the near fields hold crops only."""
    def agent(x: float, y: float, pose: str, group: str, **options):
        return s.actor("agent", x, y, pose, "smile", tall=scale_at(y), group=group, **options)

    # the tractor along the farm track, the agent at its wheel
    y = TRACK[1] - 2
    k = scale_at(y) / 100
    tractor(s, 226, y, k)
    # the handcart on the track on the right, being loaded
    y = TRACK[1] - 1
    k = scale_at(y) / 100
    art, box = handcart(edge_x(y, 1200), y, k)
    s.put(y, art, box, "cart", group="cart")
    agent(box[0] - 14 * k, y, "carry", "cart", held="crate")
    vines = ((NEAR - 5, NEAR - 64), (-1300.0, -60.0), (2 * VP_X + 1300, 2 * VP_X + 60))
    for name, pose, ys, left, right, extra in (
            ("orchard", "cheer", (TRACK[0] + 6, TRACK[0] + 10), (-560, -1400), (2 * VP_X + 560, 2 * VP_X + 1400), 0.6),
            ("wheat", "carry", (ORCHARD - 2, ORCHARD - 12), (-150, -1800), (2 * VP_X + 150, 2 * VP_X + 1800), 0),
            ("carrier", "carry", (NEAR - 26, NEAR - 64), *vines[1:], 0), ("grapes", "present", *vines, 0.1),
            ("water", "present", *vines, 0.45), ("picker", "present", *vines, 0.1)):
        for side, feet in (("l", left), ("r", right)):
            group = "orchard" if name == "orchard" else f"{name}{side}"     # a picker stands among the trees
            try:
                x, y = _spot(s, ys, feet, extra, among="orchard" if name == "orchard" else "")
            except ValueError:
                continue                                         # the field is full: one worker fewer
            worker = agent(x, y, pose, group, **({"held": "crate"} if pose == "carry" else {}))
            if name == "water":
                s.hold(worker, watering_can)
            elif name == "orchard":                              # apples picked into a basket at the feet
                art, box = basket(worker.right + 6, y, scale_at(y) / 100)
                s.put(y, art, box, "basket", group="orchard")
    # where the road's bend took a field, its worker goes to work further off: ten at work in all
    extra = (("present", (TRACK[0] + 6, TRACK[0] + 10), 0.1), ("carry", (ORCHARD - 2, ORCHARD - 12), 0.0),
             ("cheer", (TRACK[0] + 2, TRACK[0] + 8), 0.6), ("present", (ORCHARD - 6, ORCHARD - 14), 0.1),
             ("carry", (PLAZA + 14, PLAZA + 24), 0.0), ("cheer", (ORCHARD + 4, ORCHARD + 12), 0.6))
    spans = ((2 * VP_X + 300, 2 * VP_X + 1600), (-200, -1600), (2 * VP_X + 900, 2 * VP_X + 2400), (-800, -2400),
             (2 * VP_X + 100, 2 * VP_X + 3400), (300, -3400))
    n_ = 0
    while sum(1 for b in s.boxes if b.kind == "actor" and b.name == "agent") < 11 and n_ < len(extra) * len(spans):
        pose, ys, wide = extra[n_ % len(extra)]
        feet = spans[n_ // len(extra) % len(spans)]
        n_ += 1
        try:
            x, y = _spot(s, ys, feet, wide)
        except ValueError:
            continue
        agent(x, y, pose, f"extra{n_}", **({"held": "crate"} if pose == "carry" else {}))


# ============================================================================ the page
CAST = ("agent", "professor", "cat", "caterpillar")   # walking along the near stretch to the bend, the agent ahead


def _cast(s: Stage) -> None:
    """The five on the road, walking in along it from the left edge and round the bend towards the gate, all one
    way, the agent leading, then the professor, the cat and the caterpillar, spaced like a group walking together;
    the sparrow flies on ahead."""
    bend = [i for i, (_, _, tx, tz) in enumerate(ROAD.line) if -0.99 < tz < -0.35]
    placed = walk_along(s, ROAD, CAST, bend[0], size=1.1, sun=SUN[:2])
    if not placed:
        return
    lead = placed[0]
    tall = (lead.bottom - lead.top) * 1.5
    for dx, lift, k_ in [(dx, lift, k_) for k_ in (0.5, 0.4) for lift in (0.5, 0.7, 0.3) for dx in (40, 80, 120, 0)]:
        bx, by = lead.right + dx, lead.top + (lead.bottom - lead.top) * lift
        probe = body_box("sparrow", bx, by, tall * k_)
        if probe[0] >= 12 and probe[2] <= W - 12 and probe[1] >= 12 and s.free(probe, 4):
            s.actor("sparrow", bx, by, "fly", "smile", tall=tall * k_, depth=lead.bottom)
            return


def city_view() -> str:
    """The walled city alone - its towers, the wall of circuit board with its apron and the glowing gate - as a
    drawing in the page's units, its gate at (VP_X, WALL_FOOT) and the vanishing point at (VP_X, HORIZON): to be set
    small on the horizon of another picture (the conclusion's road leads to it)."""
    s = Stage(seed=31, reserved=[])
    ledger(s)
    _city(s)
    s.put(WALL_FOOT - 1, _wall_art(), [(-6, WALL_TOP - 4, W + 6, WALL_FOOT)], "wall", group="city", backdrop=True)
    gate(s)
    return "".join(f for _, _, f in sorted(s.items, key=lambda item: item[:2]))


def draw() -> Opener:
    """The farewell picture."""
    s = Stage(seed=31, reserved=[])
    ledger(s)
    c = s.back
    _sky(c)
    _city(s)
    s.put(WALL_FOOT - 1, _wall_art(), [(-6, WALL_TOP - 4, W + 6, WALL_FOOT)], "wall", group="city", backdrop=True)
    gate(s)
    _fields(c, s)
    ROAD.draw(c)
    _spill(s)
    _flowers(c)
    _cast(s)
    _workers(s)
    furnish(s, ROAD)
    _lamps(s)
    birds(c, (40, 260, 800, 380), 7, 5)
    drawn = Opener(s.svg("farewell-art"), (0, 0, 0, 0), list(s.boxes), list(s.reserved), (), list(s.edges),
                   s.reach())
    drawn.holders, drawn.links, drawn.ports = s.holders, s.links, s.ports    # for the checks of lines and ports
    return drawn


def _wall_art() -> str:
    c = Canvas()
    _wall(c)
    return c.render()

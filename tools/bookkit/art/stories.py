"""Story openers that stand on their own, one function each, in `STORIES` by the name a chapter without a world
gives as `scene:` in its front matter (`openers.OPENERS` holds them with the worlds' openers). The railway world
draws its opener from the story `railway`.

Each story builds on a `Stage` (see `openers.py`): page units 840 x 1188, the title held at the top left, the
chapter tag at the bottom left, the professor's bubble where `Stage.speaker` puts it. Every object is placed by
hand with its box, so the composition can be checked: nothing overlaps unless it belongs together.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten, mix
from . import handheld, props
from .ink import INK, Canvas, ellipse_d, n, rounded_rect_d

W, H = 840, 1188


# ============================================================================ the railway
def _puff(c: Canvas, x: float, y: float, r: float, fill: str, opacity: float) -> None:
    """One puff of smoke: round lobes as one soft cloud, its outline faint, the whole puff at a flat opacity."""
    c.add(f'<g opacity="{opacity:.2f}">')
    c.path(f"M{x - r},{y + r * 0.35} Q{x - r * 1.15},{y - r * 0.5} {x - r * 0.35},{y - r * 0.55} "
           f"Q{x - r * 0.1},{y - r * 1.15} {x + r * 0.45},{y - r * 0.75} Q{x + r * 1.15},{y - r * 0.45} "
           f"{x + r},{y + r * 0.3} Q{x},{y + r * 0.75} {x - r},{y + r * 0.35} Z", fill, 1.1, mix(INK, fill, 0.78))
    c.add("</g>")


def _wheel(c: Canvas, x: float, r: float, crank: float, centre: str) -> tuple[float, float]:
    """A locomotive wheel standing on the rail (y = 0) at x: the steel tyre, the spokes, the counterweight opposite
    the crank and the crank pin. Returns where the crank pin is."""
    cy = -r
    c.add(f'<circle cx="{n(x)}" cy="{n(cy)}" r="{n(r)}" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="2.4"/>')
    c.add(f'<circle cx="{n(x)}" cy="{n(cy)}" r="{n(r * 0.84)}" fill="{centre}" stroke="{INK}" stroke-width="1.6"/>')
    spokes = 12 if r > 30 else 8
    c.line(" ".join(f"M{n(x + r * 0.2 * math.cos(a))},{n(cy + r * 0.2 * math.sin(a))} "
                    f"L{n(x + r * 0.8 * math.cos(a))},{n(cy + r * 0.8 * math.sin(a))}"
                    for a in (i * 2 * math.pi / spokes for i in range(spokes))),
           max(2.0, r * 0.07), darken(centre, 0.6))
    if r > 30:                                       # the counterweight, a crescent opposite the crank
        a0, a1 = math.radians(crank + 180 - 42), math.radians(crank + 180 + 42)
        rr = r * 0.82
        c.shape(f"M{n(x + rr * math.cos(a0))},{n(cy + rr * math.sin(a0))} A{n(rr)},{n(rr)} 0 0 1 "
                f"{n(x + rr * math.cos(a1))},{n(cy + rr * math.sin(a1))} Z", darken(centre, 0.85), sw=1.4, light=None)
    c.add(f'<circle cx="{n(x)}" cy="{n(cy)}" r="{n(r * 0.2)}" fill="{P.METAL_DARK}" stroke="{INK}" '
          f'stroke-width="1.6"/>')
    pin = (x + r * 0.5 * math.cos(math.radians(crank)), cy + r * 0.5 * math.sin(math.radians(crank)))
    return pin


def _puffs(c: Canvas, x0: float, y0: float, rise: float, drift: float, r0: float, r1: float, count: int,
           seed: int, tint: str, start: float = 0.62) -> None:
    """A plume of smoke or steam: many puffs, small and dense where it leaves the chimney, wider, paler and thinner
    as it rises and drifts back; the far end is drawn first so the dense root lies on top."""
    rnd = random.Random(seed)
    puffs = []
    for i in range(count):
        t = i / (count - 1)
        cx = x0 + drift * t ** 1.25 + 6 * math.sin(t * 8)
        cy = y0 - rise * t
        r = r0 + (r1 - r0) * t ** 1.1
        for _ in range(2 if t < 0.2 else 3):
            puffs.append((cx + rnd.uniform(-0.5, 0.5) * r, cy + rnd.uniform(-0.3, 0.3) * r, r * rnd.uniform(0.75, 1.1),
                          t))
    for px, py, r, t in sorted(puffs, key=lambda p: -p[3]):
        _puff(c, px, py, r, mix(P.WHITE, tint, 0.12 + 0.4 * t), start - (start - 0.1) * t)


def _locomotive(x: float, rail: float, k: float, accent: str, crank: float = 300) -> str:
    """The tank engine, the hero of the railway, facing left as it runs into the station: buffer beam and
    buffers, the smokebox with its chimney and lit headlamp, the boiler with its brass dome and safety valves, the
    side tanks lined in brass over the wheels, the cylinder and the rods to the two big driving wheels, the cab
    with its open side and the coal bunker behind. The origin is the front buffer's face at rail level; 410 long,
    272 tall."""
    c = Canvas()
    body, deep = accent, darken(accent, 0.62)
    # the frame under everything, between the wheels
    c.shape(rounded_rect_d(14, -112, 396, 22, 3), P.CHARCOAL, sw=2, light=None)
    # the wheels: the leading wheel, two big driving wheels, the trailing wheel under the cab
    pins = []
    _wheel(c, 74, 24, crank, deep)
    for wx in (176, 276):
        pins.append(_wheel(c, wx, 48, crank, deep))
    _wheel(c, 366, 26, crank, deep)
    # the cylinder under the smokebox and its guide bars
    c.shape(rounded_rect_d(40, -92, 70, 40, 8), body, sw=2.4, light=(-2, -2))
    c.shape(rounded_rect_d(36, -94, 10, 44, 3), P.GOLD, sw=1.8, light=None)
    c.shape(rounded_rect_d(104, -94, 10, 44, 3), P.GOLD, sw=1.8, light=None)
    c.line("M114,-78 H168 M114,-66 H168", 2.6, P.METAL_DARK)
    # the crosshead slides in the guides, the connecting rod runs from it to the first driving wheel's crank pin
    (p1x, p1y), (p2x, p2y) = pins
    head = 140 + 24 * math.cos(math.radians(crank))
    c.shape(rounded_rect_d(head - 10, -80, 20, 16, 3), P.METAL, sw=1.6, light=None)
    c.line(f"M110,-72 H{n(head)}", 4, P.METAL_LIGHT)                                              # piston rod
    c.tube(f"M{n(head)},-72 L{n(p1x)},{n(p1y)}", P.METAL, 7, sw=1.6)                            # connecting rod
    c.tube(f"M{n(p1x)},{n(p1y)} L{n(p2x)},{n(p2y)}", P.METAL_LIGHT, 7, sw=1.6)                  # coupling rod
    for px, py in pins:
        c.add(f'<circle cx="{n(px)}" cy="{n(py)}" r="5" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1.4"/>')
    # the running board along the engine
    c.shape(rounded_rect_d(10, -118, 402, 10, 2), P.CHARCOAL, sw=2, light=None)
    # the buffer beam and the buffer, the coupling hook under it
    c.shape(rounded_rect_d(0, -132, 18, 44, 3), deep, sw=2.2, light=None)
    c.shape(rounded_rect_d(-16, -116, 18, 12, 2), P.METAL_DARK, sw=1.8, light=None)
    c.shape(rounded_rect_d(-24, -124, 9, 28, 3), P.METAL, sw=1.8, light=None)
    c.line("M0,-96 h-10 q-6,0 -6,6", 3, P.CHARCOAL)
    # the boiler, then the side tank over it, lined in brass
    c.shape(rounded_rect_d(70, -222, 230, 104, 18), body, sw=2.6, light=(-3, -4))
    for bx in (132, 204):
        c.shape(rounded_rect_d(bx, -222, 7, 30, 2), P.GOLD, sw=1.2, light=None)
    c.line("M86,-198 H286", 2, P.GOLD)                                                           # handrail
    for hx in (96, 160, 224, 280):
        c.dot(hx, -198, 2.6, P.METAL_DARK)
    c.shape(rounded_rect_d(118, -192, 172, 76, 6), body, sw=2.6, light=(-3, -3))
    c.path(rounded_rect_d(128, -182, 152, 56, 4), "none", 2.2, P.GOLD)
    # the smokebox, its door seen edge on, the chimney with its copper cap
    c.shape(rounded_rect_d(26, -228, 58, 116, 10), P.CHARCOAL, sw=2.6, light=(-3, -3))
    c.shape("M26,-222 Q12,-170 26,-118 Z", darken(P.CHARCOAL, 0.8), sw=2, light=None)
    c.dot(20, -170, 3, P.METAL)
    c.shape("M40,-226 L44,-262 H70 L74,-226 Z", P.CHARCOAL, sw=2.4, light=(-2, 0))
    c.shape(rounded_rect_d(36, -276, 42, 16, 4), P.GOLD, sw=2.2, light=(-2, -2))
    # the lamp on its bracket at the top of the buffer beam, lit
    for r, a in ((26, 0.16), (16, 0.26)):
        c.add(f'<circle cx="2" cy="-146" r="{r}" fill="{P.SUN}" opacity="{a}"/>')
    c.shape(rounded_rect_d(4, -158, 18, 24, 3), P.CHARCOAL, sw=1.8, light=None)
    c.shape(rounded_rect_d(0, -153, 7, 14, 2), P.YELLOW_PALE, sw=1.4, light=None)
    c.line("M8,-158 Q13,-166 18,-158", 1.8, P.CHARCOAL)
    # the dome, the safety valves and the whistle on top of the boiler
    c.shape("M150,-220 Q150,-252 172,-254 Q194,-252 194,-220 Z", P.GOLD, sw=2.4, light=(-3, -3))
    c.shape(rounded_rect_d(236, -238, 10, 18, 2), P.GOLD, sw=1.6, light=None)
    c.shape(rounded_rect_d(250, -238, 10, 18, 2), P.GOLD, sw=1.6, light=None)
    c.line("M274,-222 V-238", 2.4, P.METAL_DARK)
    c.shape("M268,-238 H280 L278,-252 H270 Z", P.GOLD, sw=1.6, light=None)
    # the cab: the dark inside behind its open side, the roof on its pillars; the coal bunker behind it
    c.shape(rounded_rect_d(296, -268, 80, 150, 4), darken(deep, 0.5), sw=2.4, light=None)
    c.shape(rounded_rect_d(372, -226, 40, 108, 4), body, sw=2.4, light=(-2, -2))
    c.path(rounded_rect_d(378, -218, 28, 92, 3), "none", 2, P.GOLD)
    c.shape("M374,-226 Q378,-246 392,-248 Q406,-246 410,-226 Z", darken(P.CHARCOAL, 0.8), sw=1.8, light=None)
    for cx_, cy_ in ((384, -232), (394, -238), (402, -231), (390, -228)):            # lumps of coal on the heap
        c.shape(ellipse_d(cx_, cy_, 4.5, 3.2), P.CHARCOAL, sw=1, light=None)
    c.shape("M282,-280 Q340,-300 398,-280 V-268 H282 Z", P.CHARCOAL, sw=2.6, light=(0, -2))       # the roof
    return props._at(c, x, rail, k)


def _cab_side(x: float, rail: float, k: float, accent: str) -> str:
    """The cab's near side, drawn over the driver: the front pillar with its round spectacle window, the rear
    pillar with its handrail, and the panel up to the driver's waist, lined in brass."""
    c = Canvas()
    body = accent
    c.shape(rounded_rect_d(286, -270, 14, 154, 3), body, sw=2.4, light=(-2, 0))                   # front pillar
    c.shape(rounded_rect_d(366, -270, 12, 154, 3), body, sw=2.4, light=(-2, 0))                   # rear pillar
    c.line("M384,-250 V-130", 3, P.METAL_LIGHT)                                                  # the handrail
    c.shape(rounded_rect_d(286, -176, 92, 60, 4), body, sw=2.6, light=(-3, -3))                  # waist panel
    c.path(rounded_rect_d(296, -168, 72, 44, 3), "none", 2.2, P.GOLD)
    c.shape(rounded_rect_d(330, -110, 30, 6, 2), P.CHARCOAL, sw=1.6, light=None)                 # the step
    c.line("M336,-116 V-104 M354,-116 V-104", 2, P.CHARCOAL)
    return props._at(c, x, rail, k)


def _coach(x: float, rail: float, k: float, accent: str) -> str:
    """The first coach of the train behind the engine, running off the page: its end with the buffer, the
    body in the chapter's colour with a cream window band and lit windows, the roof, a bogie with two wheels.
    The origin is the coach's front buffer face at rail level."""
    c = Canvas()
    c.shape(rounded_rect_d(-10, -116, 14, 12, 2), P.METAL_DARK, sw=1.6, light=None)
    c.shape(rounded_rect_d(-14, -124, 8, 28, 3), P.METAL, sw=1.6, light=None)
    c.shape(rounded_rect_d(4, -132, 300, 18, 3), P.CHARCOAL, sw=2, light=None)
    for wx in (52, 110):
        _wheel(c, wx, 22, 0, darken(accent, 0.62))
    c.shape(rounded_rect_d(30, -64, 104, 16, 4), P.CHARCOAL, sw=1.8, light=None)                 # bogie frame
    c.shape(rounded_rect_d(4, -270, 300, 140, 8), accent, sw=2.6, light=(-3, -3))
    c.shape(rounded_rect_d(4, -250, 300, 54, 2), P.CREAM, sw=2, light=None)
    for wx in (16, 70, 124, 178):
        c.shape(rounded_rect_d(wx, -244, 42, 42, 6), P.YELLOW_PALE, sw=2, light=None)
        c.line(f"M{wx + 6},{-236} l10,-0 M{wx + 6},-236 v10", 1.6, P.WHITE)
    c.path(rounded_rect_d(4, -186, 300, 40, 2), "none", 1.8, P.GOLD)
    c.shape("M0,-268 Q150,-300 308,-268 V-262 H0 Z", P.METAL_DARK, sw=2.4, light=(0, -2))
    return props._at(c, x, rail, k)


def _track(c: Canvas, top: float, rail: float, bottom: float, accent: str) -> None:
    """The line in front of the platform: a bed of ballast stones packed close, the sleepers across it in
    perspective and the two steel rails on them; the near rail's top is at `rail`."""
    rnd = random.Random(17)
    base = mix(P.STONE, accent, 0.08)
    c.add(f'<rect x="-4" y="{n(top)}" width="{W + 8}" height="{n(bottom - top)}" fill="{darken(base, 0.62)}"/>')
    y = top + 3
    while y < bottom:
        x = -rnd.uniform(0, 10)
        while x < W + 8:
            w = rnd.uniform(8, 13)
            h = w * rnd.uniform(0.55, 0.75)
            tone = rnd.choice((base, lighten(base, 0.25), darken(base, 0.85)))
            c.add(f'<path d="M{n(x)},{n(y + h)} Q{n(x - 1)},{n(y)} {n(x + w * 0.5)},{n(y - 1)} '
                  f'Q{n(x + w + 1)},{n(y + 1)} {n(x + w)},{n(y + h)} Z" fill="{tone}" stroke="{INK}" '
                  f'stroke-width=".6" stroke-opacity=".45"/>')
            x += w + rnd.uniform(0.5, 2)
        y += 6.5
    far = rail - 16
    for sx in range(-20, W + 30, 36):
        c.shape(f"M{sx + 6},{far - 4} H{sx + 26} L{sx + 30},{rail + 12} H{sx + 2} Z", P.WOOD_DARK, sw=1.6, light=None)
    for ry, h in ((far - 3, 5), (rail - 1, 7)):
        c.shape(rounded_rect_d(-6, ry, W + 12, h, 1.5), P.METAL, sw=1.6, light=None)
        c.line(f"M-6,{n(ry + 1.4)} H{W + 6}", 1.2, P.METAL_PALE)


def _platform(c: Canvas, kerb: float, accent: str) -> None:
    """The station platform where everyone stands: the stone kerb along the edge, the yellow line not to be
    crossed and its tactile studs, then rows of paving slabs widening towards the reader."""
    stone = mix(P.BEIGE, accent, 0.1)
    c.add(f'<rect x="-4" y="{n(kerb)}" width="{W + 8}" height="{n(H - kerb + 4)}" fill="{darken(stone, 0.7)}"/>')
    c.shape(rounded_rect_d(-6, kerb, W + 12, 16, 2), P.METAL_PALE, sw=2.2, light=(0, -2))
    c.line(" ".join(f"M{x},{n(kerb + 2)} V{n(kerb + 15)}" for x in range(30, W, 96)), 1.2, INK, 0.4)
    stripe = kerb + 24
    c.shape(rounded_rect_d(-6, stripe, W + 12, 16, 1), P.YELLOW, sw=1.6, light=None)
    for x in range(6, W, 14):
        c.dot(x, stripe + 8, 2.2, darken(P.YELLOW, 0.8))
    y, row = stripe + 22, 0
    rnd = random.Random(23)
    while y < H:
        rh = 22 + row * 7
        x = -rnd.uniform(0, 60) - (row % 2) * 30
        while x < W:
            sw_ = 84 + row * 14
            tone = (stone, lighten(stone, 0.14), darken(stone, 0.95))[rnd.randrange(3)]
            c.add(f'<rect x="{n(x + 2)}" y="{n(y + 2)}" width="{n(sw_ - 4)}" height="{n(rh - 4)}" rx="3" fill="{tone}" '
                  f'stroke="{INK}" stroke-width=".9" stroke-opacity=".35"/>')
            x += sw_
        y += rh
        row += 1


def _bench(x: float, foot: float, k: float, accent: str) -> str:
    """A platform bench: two cast-iron ends in the chapter's colour, each with its arm rest and a curled foot,
    three wooden slats for the seat and two for the back. The origin is the middle of its feet; 140 wide, 84 tall."""
    c = Canvas()
    iron = darken(accent, 0.75)
    for back in (-84, -66):                                                            # the back's slats
        c.shape(rounded_rect_d(-62, back, 124, 9, 2), P.WOOD_LIGHT, sw=1.8, light=None)
    for sx in (-1, 1):
        c.path(f"M{sx * 58},0 Q{sx * 52},-12 {sx * 56},-36 L{sx * 60},-86 M{sx * 56},-36 Q{sx * 64},-44 {sx * 70},-48 "
               f"L{sx * 50},-50", "none", 5.4, INK)
        c.path(f"M{sx * 58},0 Q{sx * 52},-12 {sx * 56},-36 L{sx * 60},-86 M{sx * 56},-36 Q{sx * 64},-44 {sx * 70},-48 "
               f"L{sx * 50},-50", "none", 3, iron)
        c.shape(ellipse_d(sx * 62, -1, 9, 3.4), iron, sw=1.6, light=None)
    for dy in (-40, -34, -28):                                                      # the seat's slats
        c.shape(rounded_rect_d(-66, dy - 3, 132, 6, 2), P.WOOD if dy != -34 else P.WOOD_LIGHT, sw=1.4, light=None)
    return props._at(c, x, foot, k)


def _station_clock(x: float, foot: float, k: float, accent: str) -> str:
    """A station clock on a short post at the platform's end: the post on its base, the round case in the chapter's
    colour, the white face with twelve marks and the hands at four minutes past four. The origin is the foot."""
    c = Canvas()
    c.shape(rounded_rect_d(-14, -8, 28, 9, 2), P.METAL_DARK, sw=1.8, light=None)
    c.shape(rounded_rect_d(-5, -112, 10, 106, 2), darken(accent, 0.7), sw=2, light=(-1, 0))
    c.shape(rounded_rect_d(-10, -118, 20, 10, 2), darken(accent, 0.7), sw=1.8, light=None)
    cy = -146
    c.shape(ellipse_d(0, cy, 30, 30), accent, sw=2.4, light=(-2, -2))
    c.shape(ellipse_d(0, cy, 24, 24), P.WHITE, sw=1.8, light=None)
    c.line(" ".join(f"M{n(20 * math.sin(math.radians(a)))},{n(cy - 20 * math.cos(math.radians(a)))} "
                    f"L{n(23 * math.sin(math.radians(a)))},{n(cy - 23 * math.cos(math.radians(a)))}"
                    for a in range(0, 360, 30)), 1.6)
    hour, minute = math.radians(122), math.radians(24)                             # 4:04, the book's easter egg
    c.line(f"M0,{cy} L{n(12 * math.sin(hour))},{n(cy - 12 * math.cos(hour))}", 3.2)
    c.line(f"M0,{cy} L{n(19 * math.sin(minute))},{n(cy - 19 * math.cos(minute))}", 2)
    c.dot(0, cy, 2.6, P.RED)
    return props._at(c, x, foot, k)


def _emergency_post(x: float, foot: float, k: float, accent: str) -> str:
    """The emergency stop on the platform: a grey post on its base plate, a yellow box with black-and-yellow
    hazard stripes, and on its face the big red mushroom button in its collar. The origin is the foot; 130 tall."""
    c = Canvas()
    c.shape(rounded_rect_d(-16, -6, 32, 8, 2), P.METAL_DARK, sw=1.8, light=None)
    c.shape(rounded_rect_d(-6, -96, 12, 92, 2), P.METAL, sw=2, light=(-1, 0))
    c.shape(rounded_rect_d(-26, -134, 52, 48, 5), P.YELLOW, sw=2.4, light=(-2, -2))
    clip = c.shape(rounded_rect_d(-26, -98, 52, 12, 2), P.CHARCOAL, sw=0, light=None, clip=True)
    c.add(f'<g clip-path="url(#{clip})">')
    for sx in range(-34, 30, 12):
        c.add(f'<path d="M{sx},-86 l6,-12 h6 l-6,12 Z" fill="{P.YELLOW}"/>')
    c.add("</g>")
    c.path(rounded_rect_d(-26, -98, 52, 12, 2), "none", 1.8)
    c.shape(ellipse_d(0, -114, 13, 13), P.CHARCOAL, sw=1.8, light=None)
    c.shape("M-12,-114 Q-12,-128 0,-128 Q12,-128 12,-114 Q0,-108 -12,-114 Z", P.RED, sw=2, light=(-2, -2))
    c.line("M-6,-122 Q-2,-125 3,-124", 1.6, P.WHITE)
    return props._at(c, x, foot, k)


def railway(s, accent: str) -> object:
    """The railway: a request comes in and the agent brings it all the way to the station.

    One hero: a tank engine in the chapter's colour runs into the station pulling its train, the smoke rising from
    its chimney and blown back over the coaches, the rods at work, steam from the cylinder at its feet. The agent
    drives it, waving from the cab's step. By the line the colour-light signal shows green. On the platform in front
    the cat checks the arriving train against his clipboard, the caterpillar doubts, the sparrow sits on the
    emergency-stop post and eyes its big red button, a bench and a station clock at four minutes past four
    stand on the platform, and the professor explains under his bubble.
    """
    c = s.back
    horizon, rail, kerb = 790, 914, 958
    # the sky: deep at the top, warm and light near the hills; calm where the title stands
    paint = c.gradient([(0, darken(accent, 0.7)), (0.45, mix(accent, P.PINK_PALE, 0.35)),
                        (0.8, mix(P.PINK_PALE, P.SUN, 0.25)), (1, mix(P.YELLOW_PALE, P.PINK_PALE, 0.4))],
                       0, 0, 0, horizon)
    c.add(f'<rect x="-4" y="-4" width="{W + 8}" height="{horizon + 12}" fill="{paint}"/>')
    # the hills beyond the line, in the chapter's colour, and the green verge along it
    far, near = mix(accent, P.PINK_PALE, 0.55), mix(accent, P.GRASS_DARK, 0.45)
    c.shape(f"M-10,{horizon} L-10,{horizon - 70} Q140,{horizon - 120} 300,{horizon - 72} Q480,{horizon - 140} 660,"
            f"{horizon - 86} Q760,{horizon - 120} {W + 10},{horizon - 96} V{horizon} Z", far, sw=2, light=None)
    c.shape(f"M-10,{horizon + 20} L-10,{horizon - 30} Q180,{horizon - 64} 380,{horizon - 34} Q600,{horizon - 70} "
            f"{W + 10},{horizon - 40} V{horizon + 20} Z", near, sw=2, light=None)
    c.add(f'<rect x="-4" y="{horizon - 4}" width="{W + 8}" height="{rail - horizon}" '
          f'fill="{mix(P.GRASS_DARK, accent, 0.25)}"/>')
    _track(c, rail - 34, rail, kerb + 4, accent)

    # the low evening sun on the right and a few birds flying home on the left, under the title
    for r, a in ((96, 0.12), (70, 0.18)):
        c.add(f'<circle cx="736" cy="410" r="{r}" fill="{P.SUN}" opacity="{a}"/>')
    c.shape(ellipse_d(736, 410, 48, 48), mix(P.SUN, P.YELLOW_PALE, 0.4), sw=2.2, light=None)
    for bx, by, bk in ((236, 404, 1.0), (270, 388, 0.8), (298, 412, 0.7)):
        c.line(f"M{bx - 12 * bk},{by} q{6 * bk},{-8 * bk} {12 * bk},0 q{6 * bk},{-8 * bk} {12 * bk},0", 2.6)

    # --- the hero: the engine and the first coach, the smoke over them, steam at the cylinder
    lx, k = 316, 1.14
    _puffs(c, lx + 57 * k, rail - 280 * k, 470, 380, 14, 70, 34, 41, accent)
    _puffs(c, lx + 274 * k, rail - 254 * k, 46, 30, 5, 12, 6, 43, accent, start=0.75)      # the whistle blows
    s.put(rail, _coach(lx + 422 * k, rail, k, accent), (lx + 408 * k, rail - 290 * k, W, rail), "coach",
          group="train", backdrop=True)
    s.put(rail + 0.1, _locomotive(lx, rail, k, accent), [(lx - 24 * k, rail - 140 * k, lx + 412 * k, rail),
          (lx + 24 * k, rail - 304 * k, lx + 412 * k, rail - 140 * k)], "engine", group="train", backdrop=True)
    s.put(rail + 0.3, _cab_side(lx, rail, k, accent))
    # the agent, the driver, on the cab's step leaning out and waving to the platform
    s.actor("agent", lx + 346 * k, rail - 108 * k, "wave", "smile", tall=250 * k, group="train", depth=rail + 0.35)
    steam = Canvas()                                 # steam from the cylinder's drain cocks, low along the rails
    for dx, dy, r, a in ((112, -18, 10, 0.75), (92, -12, 13, 0.6), (64, -10, 16, 0.5), (36, -8, 15, 0.4)):
        _puff(steam, lx + dx * k, rail + dy, r, P.WHITE, a)
    s.put(rail + 0.4, steam.render())

    # --- the platform and the cast on it
    _platform(c, kerb, accent)
    s.keep_clear((-6, kerb, W + 6, kerb + 16))
    s.put(1116, _emergency_post(300, 1116, 1.0, accent), (274, 982, 326, 1116), "estop", group="estop")
    s.actor("sparrow", 304, 986, "point", "smile", flip=True, tall=120, group="estop", depth=1117)
    s.actor("caterpillar", 396, 1144, "think", "worry", tall=220, group="caterpillar")
    s.put(1070, _bench(518, 1070, 0.9, accent), (455, 990, 581, 1072), "bench")
    s.put(1086, _station_clock(782, 1086, 1.0, accent), (750, 938, 814, 1086), "clock")
    cat = s.actor("cat", 674, 1142, "point", "smile", flip=True, tall=230, group="cat")
    s.hold(cat, lambda x, y, kk: handheld.clipboard(x, y, kk), "left")

    # --- the professor under his bubble
    prof = s.actor("professor", 142, 1100, "explain", "talk", tall=380)
    s.speaker(prof, width=66, left=8, air=4)
    return s.render()


STORIES = {
    "railway": railway,
}

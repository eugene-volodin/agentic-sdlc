"""The attic workshop: the world of chapter 5 (skills, and the prompts the agent writes them with).

A skill is a card with a short description on its front and, behind it, what the job needs; the agent reaches for
a card by its label alone and does the job as the card says. Under the sloped roof of an attic, a workshop:

1. card       how a skill is made: a recipe card in a clear stand on the bench - its name and steps - and beside
              it the open tray of what it needs, a jig, a template, a small script rolled up;
2. playbooks  the playbooks you already have: old step-by-step sheets pinned to a roof beam, a tick here and there;
3. index      the description decides: a card index with its tabs; the agent picks a card by the tab alone,
              the vague one is passed over;
4. when       when to write a skill: the agent makes the same part by hand for the third time, a little heap of
              them grows, the professor notices;
5. command    commands are skills too: a punch card with "/adr" on it goes into the lathe's card slot, and the
              machine runs that job;
6. where      where skills lie: the personal shelf of card boxes by the window, the project's shelf by the stairs;
7. write      the agent writes the card itself, at the bench, after the job - the card on the top, the pencil on it;
8. check      the machine makes the part from the card, the cat checks it against the drawing, the caterpillar
              compares twice; the sparrow is after the emergency stop;
9. foreign    someone else's skill comes up through the floor hatch in a parcel with an odd tool in it; the
              caterpillar doubts it, the cat reads its shipping label.

The back wall turns from frame to frame: boarded walls, rafters, a dormer window, a tool board with the tools'
outlines, shelves of jars. Words only where they belong to a thing: the cards, the tabs, the punch card, the
parcel's label; the finale names the stations.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten, mix
from . import handheld, sets
from .footers import Strip
from .ink import INK, Canvas, lettering, n, rounded_rect_d
from .openers import CLEAR_MM, H, OPENERS, W, Stage
from .world_fair import held, inside, lane, mid, paving, zoom
from .world_fair import stand as _fair_stand
from .world_kit import (SIZE, Pen, clock_hands, floppy_size, hide, ledger, letter, motion, stash, tag_size, tome,
                        tome_size)
from .world_kitchen import _box, _fit_tall
from .world_library import ph, span, sparrow
from .world_sea import F, M, sx
from .world_base import Station, world

ATTIC = world("attic", opener="workshop")

_at = sets._at

WALL = mix(P.GREEN, P.CARD, 0.72)             # the boarded walls, painted pale green
PANEL = mix(P.GREEN, P.WOOD_DARK, 0.22)       # the green planked wainscot below them
BEAM = darken(P.GREEN, 0.86)                  # the green-painted beams, rafters and cabinets
BOARDS = (mix(P.WOOD_LIGHT, P.WOOD, 0.4), mix(P.WOOD_LIGHT, P.WOOD_PALE, 0.45))
MACHINE = P.GREEN


def calm(color: str) -> str:
    """A colour of the back row, calmer than the station's."""
    return mix(color, WALL, 0.38)


def backdrop(s: Strip, index: int) -> None:
    """The attic behind a station: a wall of upright boards with their grain, green rafters slanting down from the
    top, and along the wall a continuous back row of workshop things - a pegboard with tools hung in their painted
    outlines, shelves of screw jars and labelled boxes, a green chest of small drawers, a dormer window with a plant
    on its sill, a clock - turning from frame to frame, calmer than the station; a
    darker skirting and a planked floor."""
    ledger(s)
    zoom(s)
    c = s.back
    base = s.base
    c.add(f'<rect x="-6" y="-6" width="{W + 12}" height="{n(base + 8)}" fill="{WALL}"/>')
    k = max(0.6, min(1.4, base / 240))
    step = 30 * k
    rnd = random.Random(index * 13 + 1)
    for i in range(int(W / step) + 2):                                      # the boards, their seams and grain
        x = i * step - (index * 9) % step
        tone = darken(WALL, 0.94) if i % 3 == 0 else WALL
        c.add(f'<rect x="{n(x)}" y="-6" width="{n(step)}" height="{n(base + 8)}" fill="{tone}"/>')
        c.line(f"M{n(x)},-6 V{n(base)}", 1.2, darken(WALL, 0.78))
        gy = rnd.uniform(0.2, 0.8) * base
        c.line(f"M{n(x + step * 0.35)},{n(gy)} q{n(step * 0.15)},{n(10 * k)} 0,{n(24 * k)}", 0.9, darken(WALL, 0.84))
    wy = base - min(base * 0.42, 150 * k) if s.h >= 200 else base * 0.55
    c.add(f'<rect x="-6" y="{n(wy)}" width="{W + 12}" height="{n(base - wy + 2)}" fill="{PANEL}"/>')
    for i in range(int(W / (22 * k)) + 2):                                  # the wainscot's planks and its rail
        c.line(f"M{n(i * 22 * k)},{n(wy)} V{n(base)}", 1.1, darken(PANEL, 0.82))
    c.add(f'<rect x="-6" y="{n(wy - 7 * k)}" width="{W + 12}" height="{n(8 * k)}" fill="{BEAM}" '
          f'stroke="{INK}" stroke-width="1.2"/>')
    if s.h >= 200:                                                          # the rafters slanting from the top
        for j in range(-1, 6):
            x = j * W / 4 + (index * 61) % 120
            c.add(f'<path d="M{n(x)},-10 L{n(x + base * 0.5)},{n(base * 0.32)}" stroke="{INK}" '
                  f'stroke-width="{n(18 * k + 2)}"/><path d="M{n(x)},-10 L{n(x + base * 0.5)},{n(base * 0.32)}" '
                  f'stroke="{BEAM}" stroke-width="{n(18 * k)}"/>')
        c.add(f'<rect x="-6" y="{n(base * 0.3)}" width="{W + 12}" height="{n(14 * k)}" fill="{BEAM}" '
              f'stroke="{INK}" stroke-width="1.4"/>')                       # the wall plate they rest on
    top = base * 0.3 + 14 * k if s.h >= 200 else 4.0
    kinds = ("pegboard", "jars", "drawers", "window", "jars", "pegboard", "clock")
    x = -40 * k * ((index * 0.6) % 1)
    i = index * 3
    while x < W:
        kind = kinds[i % len(kinds)]
        w = {"window": 130, "clock": 90}.get(kind, 150) * k
        unit(c, kind, x + 6 * k, x + w - 6 * k, top + 10 * k, base, k, seed=index * 31 + i)
        x += w
        i += 1
    paving(c, -6, W + 6, base, s.h + 4, max(0.8, s.unit), seed=index + 5, tones=BOARDS)
    c.add(f'<rect x="-6" y="{n(base - 6)}" width="{W + 12}" height="10" fill="{darken(P.WOOD_DARK, 0.8)}" '
          f'stroke="{INK}" stroke-width="1.2"/>')                           # the skirting


def unit(c: Canvas, kind: str, x0: float, x1: float, top: float, foot: float, k: float, seed: int = 0) -> None:
    """One thing of the back row between x0 and x1, under `top`, standing on or hung over `foot`."""
    rnd = random.Random(seed)
    w, cx = x1 - x0, (x0 + x1) / 2
    room = foot - top
    lw = 1.3
    if room < 30 * k:
        return
    if kind == "pegboard":                                                  # holes in rows, tools in outlines
        bt, bh = top, min(room * 0.55, 120 * k)
        c.add(f'<rect x="{n(x0)}" y="{n(bt)}" width="{n(w)}" height="{n(bh)}" rx="{n(2 * k)}" '
              f'fill="{calm(P.KITCHEN_KRAFT)}" stroke="{calm(INK)}" stroke-width="{lw}"/>')
        g = 12 * k
        c.add("".join(f'<circle cx="{n(x0 + g * (a + 0.5))}" cy="{n(bt + g * (b + 0.5))}" r="{n(1.1 * k)}" '
                      f'fill="{calm(P.WOOD_DARK)}"/>' for a in range(int(w / g)) for b in range(int(bh / g))))
        tools = [("hammer", 0.2), ("saw", 0.45), ("spanner", 0.68), ("screwdriver", 0.86)]
        for name, f in tools:
            tx, ty = x0 + w * f, bt + bh * 0.18
            th = bh * 0.66
            if name == "hammer":
                c.add(f'<path d="M{n(tx - 1.6 * k)},{n(ty + 8 * k)} v{n(th - 8 * k)} '
                      f'h{n(3.2 * k)} v{n(-th + 8 * k)} Z" '
                      f'fill="{calm(P.WOOD)}" stroke="{calm(INK)}" stroke-width="{lw}"/>'
                      f'<rect x="{n(tx - 9 * k)}" y="{n(ty)}" width="{n(18 * k)}" height="{n(8 * k)}" rx="{n(2 * k)}" '
                      f'fill="{calm(P.METAL)}" stroke="{calm(INK)}" stroke-width="{lw}"/>')
            elif name == "saw":
                c.add(f'<path d="M{n(tx - 8 * k)},{n(ty)} h{n(16 * k)} v{n(th * 0.3)} l{n(-3 * k)},{n(th * 0.7)} '
                      f'h{n(-10 * k)} l{n(-3 * k)},{n(-th * 0.7)} Z" fill="{calm(P.METAL_LIGHT)}" '
                      f'stroke="{calm(INK)}" stroke-width="{lw}"/><rect x="{n(tx - 9 * k)}" y="{n(ty - 2 * k)}" '
                      f'width="{n(18 * k)}" height="{n(th * 0.28)}" rx="{n(3 * k)}" fill="{calm(P.RED)}" '
                      f'stroke="{calm(INK)}" stroke-width="{lw}"/>')
            elif name == "spanner":
                c.add(f'<path d="M{n(tx - 2.5 * k)},{n(ty + 10 * k)} v{n(th - 10 * k)} '
                      f'h{n(5 * k)} v{n(-th + 10 * k)} Z" '
                      f'fill="{calm(P.METAL)}" stroke="{calm(INK)}" stroke-width="{lw}"/>'
                      f'<circle cx="{n(tx)}" cy="{n(ty + 6 * k)}" r="{n(6 * k)}" fill="none" '
                      f'stroke="{calm(P.METAL_DARK)}" '
                      f'stroke-width="{n(3 * k)}"/>')
            else:
                c.add(f'<rect x="{n(tx - 3 * k)}" y="{n(ty)}" width="{n(6 * k)}" height="{n(th * 0.4)}" '
                      f'rx="{n(2 * k)}" '
                      f'fill="{calm(P.YELLOW)}" stroke="{calm(INK)}" stroke-width="{lw}"/>')
                c.line(f"M{n(tx)},{n(ty + th * 0.4)} v{n(th * 0.55)}", 2 * k, calm(P.METAL_DARK))
        return
    if kind == "jars":                                                      # shelves of screw jars and boxes
        rows = max(1, min(3, int(room / (60 * k))))
        for j in range(rows):
            sy = top + 40 * k + j * min(room / rows, 64 * k)
            x = x0 + 4 * k
            while x < x1 - 18 * k:
                if rnd.random() < 0.5:
                    jw, jh = 14 * k, 22 * k
                    c.add(f'<rect x="{n(x)}" y="{n(sy - jh)}" width="{n(jw)}" height="{n(jh)}" rx="{n(3 * k)}" '
                          f'fill="{calm(P.LENS)}" stroke="{calm(INK)}" stroke-width="{lw}"/>'
                          f'<rect x="{n(x)}" y="{n(sy - jh - 4 * k)}" width="{n(jw)}" height="{n(5 * k)}" '
                          f'fill="{calm(P.RED)}" stroke="{calm(INK)}" stroke-width="1"/>')
                    c.add("".join(f'<rect x="{n(x + 3 * k + q * 4 * k)}" y="{n(sy - 8 * k - (q % 2) * 4 * k)}" '
                                  f'width="{n(3 * k)}" height="{n(5 * k)}" fill="{calm(P.METAL_DARK)}"/>'
                                  for q in range(2)))                      # screws inside
                else:
                    jw, jh = 26 * k, 18 * k
                    c.add(f'<rect x="{n(x)}" y="{n(sy - jh)}" width="{n(jw)}" height="{n(jh)}" '
                          f'fill="{calm(P.KITCHEN_KRAFT)}" stroke="{calm(INK)}" stroke-width="{lw}"/>'
                          f'<rect x="{n(x + 6 * k)}" y="{n(sy - jh + 5 * k)}" width="{n(14 * k)}" height="{n(6 * k)}" '
                          f'fill="{calm(P.CARD)}"/>')
                x += jw + 5 * k
            c.add(f'<rect x="{n(x0)}" y="{n(sy)}" width="{n(w)}" height="{n(5 * k)}" fill="{calm(BEAM)}" '
                  f'stroke="{calm(INK)}" stroke-width="{lw}"/>')
        return
    if kind == "drawers":                                                   # a green chest of small drawers
        ch = min(room * 0.75, 150 * k)
        ct = foot - ch
        c.add(f'<rect x="{n(x0 + 6 * k)}" y="{n(ct)}" width="{n(w - 12 * k)}" height="{n(ch)}" rx="{n(3 * k)}" '
              f'fill="{calm(BEAM)}" stroke="{calm(INK)}" '
              f'stroke-width="{lw}"/>')
        cols, rows = 3, max(2, int(ch / (26 * k)))
        dw, dh = (w - 24 * k) / cols, (ch - 12 * k) / rows
        for a in range(cols):
            for b in range(rows):
                dx, dy = x0 + 12 * k + a * dw, ct + 6 * k + b * dh
                c.add(f'<rect x="{n(dx + 2 * k)}" y="{n(dy + 2 * k)}" width="{n(dw - 4 * k)}" height="{n(dh - 4 * k)}" '
                      f'rx="{n(1.5 * k)}" fill="{calm(lighten(BEAM, 0.25))}" stroke="{calm(INK)}" stroke-width="1"/>'
                      f'<rect x="{n(dx + dw / 2 - 6 * k)}" y="{n(dy + dh / 2 - 3 * k)}" width="{n(12 * k)}" '
                      f'height="{n(4 * k)}" fill="{calm(P.CARD)}"/>')
        return
    if kind == "window":                                                    # a dormer window, a plant on its sill
        ww = min(w - 10 * k, room * 0.6)
        wt = top + 8 * k
        wh = ww * 0.9
        c.add(f'<path d="M{n(cx - ww / 2 - 8 * k)},{n(wt + 8 * k)} L{n(cx)},{n(wt - ww * 0.22)} '
              f'L{n(cx + ww / 2 + 8 * k)},{n(wt + 8 * k)} Z" fill="{calm(BEAM)}" stroke="{calm(INK)}" '
              f'stroke-width="{lw}"/>')
        c.add(f'<rect x="{n(cx - ww / 2)}" y="{n(wt + 8 * k)}" width="{n(ww)}" height="{n(wh)}" '
              f'fill="{lighten(P.SKY, 0.2)}" stroke="{calm(BEAM)}" stroke-width="{n(6 * k)}"/>')
        c.line(f"M{n(cx)},{n(wt + 8 * k)} v{n(wh)} M{n(cx - ww / 2)},{n(wt + 8 * k + wh / 2)} h{n(ww)}", 3 * k,
               calm(BEAM))
        sill = wt + 8 * k + wh
        c.add(f'<rect x="{n(cx - ww / 2 - 6 * k)}" y="{n(sill)}" width="{n(ww + 12 * k)}" height="{n(6 * k)}" '
              f'fill="{calm(P.WOOD)}" stroke="{calm(INK)}" stroke-width="{lw}"/>')
        c.add(f'<path d="M{n(cx + ww * 0.2 - 8 * k)},{n(sill)} l{n(2 * k)},{n(-14 * k)} h{n(12 * k)} l{n(2 * k)},'
              f'{n(14 * k)} Z" fill="{calm(P.TERRACOTTA)}" stroke="{calm(INK)}" stroke-width="{lw}"/>')
        for a in (-50, -15, 20, 55):
            r_ = math.radians(a - 90)
            lx_, ly_ = cx + ww * 0.2 + math.cos(r_) * 12 * k, sill - 14 * k + math.sin(r_) * 12 * k
            c.add(f'<ellipse cx="{n(lx_)}" cy="{n(ly_)}" rx="{n(4 * k)}" ry="{n(8 * k)}" '
                  f'transform="rotate({a} {n(lx_)} {n(ly_)})" fill="{calm(P.GREEN)}" stroke="{calm(INK)}" '
                  f'stroke-width="1"/>')
        return
    if kind == "clock":                                                     # a wall clock with numerals
        cr = min(26 * k, room * 0.2)
        cy = top + 20 * k + cr
        c.add(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(cr)}" fill="{calm(P.CARD)}" stroke="{calm(BEAM)}" '
              f'stroke-width="{n(4 * k)}"/>')
        for num, ang in (("12", -90), ("3", 0), ("6", 90), ("9", 180)):
            a = math.radians(ang)
            size = max(5.0, cr * 0.32)
            c.add(lettering(cx + math.cos(a) * cr * 0.72, cy + math.sin(a) * cr * 0.72 + size * 0.36, num, size,
                            calm(INK), style="plain"))
        c.add(clock_hands(cx, cy, cr * 0.45, cr * 0.62, 2 * k, calm(INK)))


def _framed(draw):
    """A station drawn mirrored on every other page, so that no two pages in a row look alike: the station and its
    cast swap sides, the things themselves are never mirrored."""
    def run(s: Strip, beat: str) -> None:
        s.mirror = bool(s.shot)                           # page after page the station swaps sides
        draw(s, beat)
    return run


def stand(s: Strip, name: str, fracs, pose: str, mood: str = "smile", flip: bool = True, mark: str | None = None):
    """A character of the station at the first of `fracs` where it finds room - failing those, at the nearest free
    spot along the floor - whole inside the frame. The caterpillar writing keeps to her own notebook and pencil: no
    checklist is added on top of them here, which would look piled up."""
    first = fracs if isinstance(fracs, tuple) else (fracs,)
    probe = _box(s, name, 0, lane(s).feet)
    half = (probe[2] - probe[0]) / 2
    sweep = sorted((f for f in (i / 40 for i in range(41)) if half + 2 <= s.x(f) <= W - half - 2),
                   key=lambda f: abs(f - first[0]))
    who = _fair_stand(s, name, (*first, *sweep), pose, mood, flip=flip, mark=mark)
    if who is not None or s.h < 200:
        return who
    feet = lane(s).feet
    for scale in (0.88, 0.78):                            # a full frame: a step further back rather than left out
        for f in (*first, *sweep):
            x = s.x(f)
            box = _box(s, name, x, feet, scale)
            if box[1] >= 2 and box[0] >= 2 and box[2] <= W - 2 and s.free(box, 3):
                return s.actor(name, x, feet, pose, mood, flip=flip, tall=s.tall * SIZE[name] * scale, group=name)
    return None


# ============================================================================ things
LATHE_W = (-142.0, 134.0)                                   # its left and right ends, in its own units
LATHE_H = 184.0                                            # from the floor to the lamp's top


def _box_d(x: float, y: float, w: float, h: float, r: float = 2.0) -> str:
    return rounded_rect_d(x, y, w, h, r)


def lathe(c: Canvas, x: float, foot: float, k: float, running: bool = False, slot: bool = False) -> dict:
    """A metal-turning lathe, its foot's middle at (x, foot), 276 wide and 184 tall to its lamp: it stands on a
    cabinet base - two pedestals on levelling feet, drawers in the left one, a door in the right one - with the chip
    tray across them; on the tray the bed with its two ways; at the left the headstock with its gear cover, two speed
    levers with ball knobs, a speed chart and the red emergency stop on a yellow plate, the motor behind it at the
    back under its belt guard; the three-jaw chuck holding the workpiece, turned down to a step; the carriage on the
    ways - its apron with the big handwheel, the cross-slide with its small handwheel, the tool post and its cutting
    bit at the work; at the right the tailstock, its quill and centre in the work, its handwheel; a lamp on a
    gooseneck over the cut. `slot`: a small control box on an arm at the right end, two buttons and a card slot on
    its top. `running`: chips curling off the bit into the tray, a wisp of coolant steam, the chuck spinning, the lamp
    lit. Returns its parts' points on the page."""
    d = Canvas()
    dark, light_ = darken(MACHINE, 0.72), lighten(MACHINE, 0.35)
    # the motor at the back and its belt guard, drawn first: behind everything
    d.shape(_box_d(-140, -74, 30, 26, 4), darken(MACHINE, 0.82), sw=1.6, light=None)
    d.line(" ".join(f"M{-136 + j * 5},-70 V-52" for j in range(5)), 1.0, darken(MACHINE, 0.55))
    d.shape(_box_d(-142, -156, 16, 92, 6), P.YELLOW, sw=1.6, light=(-1, -1))                  # the belt guard
    d.line("M-138,-146 V-74 M-130,-146 V-74", 0.9, darken(P.YELLOW, 0.7), 0.7)
    # the cabinet base
    for px0, px1 in ((-128, -54), (46, 120)):
        for fx in (px0 + 6, px1 - 10):                                                         # levelling feet
            d.shape(_box_d(fx, -5, 4, 5, 1), P.METAL_DARK, sw=1.0, light=None)
            d.shape(_box_d(fx - 3, -2, 10, 2.5, 1), P.CHARCOAL, sw=0.8, light=None)
        d.shape(_box_d(px0, -74, px1 - px0, 69, 3), MACHINE, sw=1.8, light=(-1.5, -1.5), shade_k=0.85)
    for j in range(3):                                                                         # its drawers
        y0 = -68 + j * 21
        d.shape(_box_d(-122, y0, 62, 17, 2), light_, sw=1.2, light=None)
        d.shape(_box_d(-101, y0 + 6, 20, 4, 2), P.METAL, sw=0.9, light=None)
    d.shape(_box_d(52, -68, 62, 57, 2), light_, sw=1.2, light=None)                          # the door
    d.shape(_box_d(104, -46, 4, 14, 2), P.METAL, sw=0.9, light=None)
    d.add(f'<circle cx="58" cy="-62" r="1.2" fill="{INK}"/><circle cx="58" cy="-17" r="1.2" fill="{INK}"/>')
    d.shape("M-132,-84 H124 L120,-72 H-128 Z", P.METAL, sw=1.6, light=None)                 # the chip tray
    d.line("M-126,-78 H118", 1.0, P.METAL_DARK, 0.6)
    # the bed and its ways
    d.shape(_box_d(-112, -100, 214, 16, 2), dark, sw=1.8, light=None)
    d.line("M-110,-97 H100 M-110,-92 H100", 1.4, P.METAL_LIGHT)
    d.line("M-110,-88 H100", 0.8, INK, 0.4)
    # the headstock
    d.shape(_box_d(-126, -156, 66, 56, 5), MACHINE, sw=1.8, light=(-2, -2), shade_k=0.85)
    d.shape(_box_d(-126, -156, 20, 56, 5), darken(MACHINE, 0.86), sw=1.4, light=None)        # its gear cover
    d.add("".join(f'<circle cx="{bx}" cy="{by}" r="1.3" fill="{INK}"/>'
                  for bx, by in ((-121, -151), (-111, -151), (-121, -105), (-111, -105))))
    d.shape(_box_d(-100, -150, 24, 14, 1.5), P.CARD, sw=1.0, light=None)                    # the speed chart
    d.line("M-97,-146 h18 M-97,-142 h14 M-97,-139 h17", 0.7, INK, 0.6)
    for lx_, turn in ((-94, -25), (-80, 20)):                                                  # the speed levers
        d.add(f'<g transform="rotate({turn} {lx_} -122)"><rect x="{lx_ - 1.6}" y="-134" width="3.2" height="12" '
              f'fill="{P.METAL_DARK}" stroke="{INK}" stroke-width=".8"/><circle cx="{lx_}" cy="-136" r="3.6" '
              f'fill="{P.CHARCOAL}" stroke="{INK}" stroke-width=".8"/></g>')
        d.add(f'<circle cx="{lx_}" cy="-122" r="3" fill="{P.METAL}" stroke="{INK}" stroke-width=".9"/>')
    ex, ey = -70, -142                                                                         # the e-stop
    d.shape(_box_d(ex - 8, ey - 8, 16, 16, 2), P.YELLOW, sw=1.0, light=None)
    d.add(f'<circle cx="{ex}" cy="{ey}" r="6" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>'
          f'<ellipse cx="{ex - 2}" cy="{ey - 2}" rx="2" ry="1.2" fill="{lighten(P.RED, 0.5)}"/>')
    # the chuck, its jaws, the workpiece turned down to a step
    cy = -122
    d.shape(_box_d(-60, cy - 16, 14, 32, 3), P.METAL, sw=1.6, light=(-1, -1))
    d.line(f"M-56,{cy - 16} V{cy + 16} M-50,{cy - 16} V{cy + 16}", 0.8, P.METAL_DARK, 0.7)
    for jy in (-13, -2, 9):
        d.shape(_box_d(-46, cy + jy, 6, 5, 1), P.METAL_DARK, sw=0.9, light=None)
    d.shape(_box_d(-42, cy - 7, 36, 14, 1), P.METAL_LIGHT, sw=1.2, light=None)              # uncut
    d.shape(_box_d(-6, cy - 5, 36, 10, 1), lighten(P.METAL_LIGHT, 0.3), sw=1.2, light=None)  # turned
    d.line(" ".join(f"M{wx},{cy - 5} v10" for wx in range(-2, 28, 5)), 0.6, P.METAL, 0.8)
    # the tailstock, its quill and centre, its handwheel
    d.shape("M50,-100 L54,-134 H84 L88,-100 Z", MACHINE, sw=1.8, light=(-1.5, -1.5), shade_k=0.85)
    d.shape(_box_d(36, cy - 4, 16, 8, 1), P.METAL, sw=1.0, light=None)
    d.shape(f"M36,{cy - 3} L30,{cy} L36,{cy + 3} Z", P.METAL_DARK, sw=0.8, light=None)
    d.shape(_box_d(84, cy - 3, 10, 6, 1), P.METAL_DARK, sw=0.8, light=None)
    d.add(f'<circle cx="100" cy="{cy}" r="11" fill="none" stroke="{INK}" stroke-width="4.4"/>'
          f'<circle cx="100" cy="{cy}" r="11" fill="none" stroke="{P.METAL}" stroke-width="2.6"/>'
          f'<path d="M89,{cy} H111 M100,{cy - 11} V{cy + 11}" stroke="{P.METAL_DARK}" stroke-width="1.6"/>'
          f'<circle cx="100" cy="{cy}" r="2.6" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width=".8"/>'
          f'<rect x="108" y="{cy - 9}" width="4" height="9" rx="2" fill="{P.CHARCOAL}" stroke="{INK}" '
          f'stroke-width=".8"/>')
    # the carriage: saddle, apron and its handwheel, cross-slide and its wheel, tool post and bit
    d.shape(_box_d(-16, -106, 52, 8, 1.5), dark, sw=1.4, light=None)                          # the saddle
    d.shape(_box_d(-12, -98, 44, 26, 2), MACHINE, sw=1.6, light=None)                         # the apron
    d.add(f'<circle cx="0" cy="-84" r="9" fill="none" stroke="{INK}" stroke-width="4"/>'
          f'<circle cx="0" cy="-84" r="9" fill="none" stroke="{P.METAL}" stroke-width="2.4"/>'
          f'<path d="M-9,-84 H9 M0,-93 V-75" stroke="{P.METAL_DARK}" stroke-width="1.4"/>'
          f'<rect x="-11" y="-82" width="3.6" height="8" rx="1.8" fill="{P.CHARCOAL}" stroke="{INK}" '
          f'stroke-width=".7"/>')
    d.add(f'<rect x="20" y="-92" width="3" height="12" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width=".7"/>'
          f'<circle cx="21.5" cy="-93" r="3" fill="{P.RED}" stroke="{INK}" stroke-width=".7"/>')
    d.shape(_box_d(-8, -112, 34, 6, 1), P.METAL, sw=1.2, light=None)                         # the cross-slide
    d.add(f'<circle cx="31" cy="-109" r="5" fill="none" stroke="{P.METAL_DARK}" stroke-width="2"/>'
          f'<path d="M26,-109 h10" stroke="{P.METAL_DARK}" stroke-width="1.2"/>')
    d.shape(_box_d(2, -116, 14, 10, 1), P.METAL_DARK, sw=1.2, light=None)                    # the tool post
    d.add(f'<rect x="6" y="-120" width="6" height="4" fill="{P.METAL}" stroke="{INK}" stroke-width=".7"/>')
    d.shape("M3,-114 L-4,-117 L-4,-115 L3,-110 Z", P.METAL_LIGHT, sw=0.8, light=None)       # the bit
    # the lamp on its gooseneck
    d.shape(_box_d(-86, -160, 14, 4, 1), P.CHARCOAL, sw=1.0, light=None)
    d.line("M-79,-160 C-79,-182 -50,-186 -36,-172", 3.2, INK)
    d.line("M-79,-160 C-79,-182 -50,-186 -36,-172", 1.8, P.METAL)
    d.shape("M-42,-176 L-26,-176 L-22,-164 L-46,-164 Z", MACHINE, sw=1.2, light=None)
    if running:
        d.add(f'<path d="M-46,-164 L-60,-128 H-2 L-22,-164 Z" fill="{P.SUN}" fill-opacity=".16"/>')
        d.add(f'<ellipse cx="-34" cy="-163" rx="8" ry="2" fill="{P.YELLOW_PALE}"/>')
        for dx, dy in ((0, 0), (5, 3), (-3, 6)):                                              # chips
            d.add(f'<path d="M{-4 + dx},{-112 + dy} q-6,4 -2,9 q5,4 -1,9 q-5,4 0,9" fill="none" '
                  f'stroke="{darken(P.SUN, 0.85)}" stroke-width="1.6" stroke-linecap="round"/>')
        d.add("".join(f'<path d="M{tx},-83 q2,-4 5,-1 q2,3 5,0" fill="none" stroke="{darken(P.SUN, 0.85)}" '
                      f'stroke-width="1.3"/>' for tx in (-30, -18, 8, 40)))                   # in the tray
        d.add(f'<path d="M-8,-126 q-4,-8 2,-14 q5,-6 0,-14" fill="none" stroke="{P.WHITE}" stroke-width="2" '
              f'stroke-linecap="round" stroke-opacity=".85"/><path d="M-1,-127 q4,-7 -1,-13" fill="none" '
              f'stroke="{P.WHITE}" stroke-width="1.6" stroke-linecap="round" stroke-opacity=".8"/>')   # coolant steam
        d.add(f'<path d="M-62,{cy - 22} A16,22 0 0 1 -46,{cy - 20}" fill="none" stroke="{INK}" stroke-width="1.3" '
              f'stroke-opacity=".6"/><path d="M-62,{cy + 22} A16,22 0 0 0 -46,{cy + 20}" fill="none" '
              f'stroke="{INK}" stroke-width="1.3" stroke-opacity=".6"/>')                         # the chuck spins
    if slot:                                                                                   # the control box
        d.shape("M104,-100 H114 V-132 H110 V-104 H104 Z", P.METAL_DARK, sw=1.0, light=None)
        d.shape(_box_d(104, -160, 30, 30, 3), P.CHARCOAL, sw=1.6, light=None)
        d.shape(_box_d(110, -163, 18, 4, 1), INK, sw=0.8, light=None)                       # the card slot
        d.add(f'<circle cx="112" cy="-146" r="4" fill="{P.GREEN}" stroke="{INK}" stroke-width=".9"/>'
              f'<circle cx="126" cy="-146" r="4" fill="{P.RED}" stroke="{INK}" stroke-width=".9"/>'
              f'<circle cx="119" cy="-136" r="2.4" fill="{P.SUN if running else P.METAL}" stroke="{INK}" '
              f'stroke-width=".7"/>')
    c.add(_at(d, x, foot, k))

    def at(px: float, py: float) -> tuple[float, float]:
        return x + px * k, foot + py * k

    return {"stop": at(ex, ey - 8), "lamp": at(-34, -176), "guard": at(-134, -156), "slot": at(119, -163),
            "top": foot - 160 * k, "tail": at(100, -134),
            "box": (x + LATHE_W[0] * k, foot - LATHE_H * k, x + LATHE_W[1] * k, foot)}


def lathe_box(x: float, foot: float, k: float) -> tuple[float, float, float, float]:
    """Where the lathe stands, lamp included."""
    return (x + LATHE_W[0] * k, foot - LATHE_H * k, x + LATHE_W[1] * k, foot)


def sheets_beam(s, x0: float, x1: float, y: float, k: float, count: int = 3) -> tuple[float, float, float, float]:
    """The playbooks: a green roof beam from x0 to x1 at y, and old step-by-step sheets tacked to it - yellowed,
    numbered steps as lines, a green tick by some, a corner curling. Returns the box of beam and sheets."""
    c = Canvas()
    c.add(f'<rect x="{n(x0)}" y="{n(y - 14 * k)}" width="{n(x1 - x0)}" height="{n(16 * k)}" fill="{BEAM}" '
          f'stroke="{INK}" stroke-width="{n(1.4 * k)}"/>')
    c.line(f"M{n(x0)},{n(y - 9 * k)} H{n(x1)}", k, lighten(BEAM, 0.3))
    sw_, sh = min(70 * k, (x1 - x0) / count - 14 * k), 92 * k
    gap = (x1 - x0 - count * sw_) / (count + 1)
    rnd = random.Random(3)
    for i in range(count):
        sx = x0 + gap + i * (sw_ + gap)
        turn = rnd.uniform(-4, 4)
        g = Canvas()
        g.add(f'<path d="M0,0 H{n(sw_)} V{n(sh - 10 * k)} L{n(sw_ - 10 * k)},{n(sh)} H0 Z" '
              f'fill="{mix(P.CARD, P.YELLOW_PALE, 0.6)}" stroke="{INK}" stroke-width="{n(1.2 * k)}"/>')
        g.add(f'<path d="M{n(sw_)},{n(sh - 10 * k)} L{n(sw_ - 10 * k)},{n(sh - 10 * k)} L{n(sw_ - 10 * k)},{n(sh)} Z" '
              f'fill="{P.WOOD_PALE}" stroke="{INK}" stroke-width="{n(0.8 * k)}"/>')       # the curled corner
        for j in range(5):
            ly = 16 * k + j * 14 * k
            g.add(lettering(8 * k, ly + 3 * k, str(j + 1), max(5.0, 8 * k), INK, anchor="middle", style="plain"))
            g.line(f"M{n(16 * k)},{n(ly)} H{n(sw_ - 14 * k - (j % 2) * 8 * k)}", 1.2 * k, INK, 0.55)
            if (i + j) % 3 == 0:
                g.add(f'<path d="M{n(sw_ - 12 * k)},{n(ly)} l{n(3 * k)},{n(3 * k)} l{n(5 * k)},{n(-6 * k)}" '
                      f'fill="none" stroke="{P.GREEN}" stroke-width="{n(1.8 * k)}"/>')
        g.add(f'<circle cx="{n(sw_ / 2)}" cy="{n(2 * k)}" r="{n(3 * k)}" fill="{P.METAL_DARK}" stroke="{INK}" '
              f'stroke-width="{n(0.8 * k)}"/>')                                            # its tack
        c.add(f'<g transform="translate({n(sx)},{n(y - 6 * k)}) rotate({n(turn)})">{g.render()}</g>')
    box = (x0, y - 14 * k, x1, y + sh)
    s.put(1.4, c.render(), box, "playbooks", group="playbooks")
    return box


def drawing(c: Canvas, x: float, y: float, k: float) -> tuple[float, float, float, float]:
    """The part's drawing pinned to the wall at (x, y), its top left: blue paper, the pin drawn in white with its
    dimension lines. Returns its box."""
    w, h = 70 * k, 50 * k
    c.add(f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="{P.BLUE}" stroke="{INK}" '
          f'stroke-width="{n(1.2 * k)}"/>')
    c.add(f'<path d="M{n(x + 20 * k)},{n(y + 38 * k)} v{n(-8 * k)} h{n(4 * k)} v{n(-16 * k)} h{n(14 * k)} '
          f'v{n(16 * k)} h{n(4 * k)} v{n(8 * k)} Z" fill="none" stroke="{P.WHITE}" stroke-width="{n(1.2 * k)}"/>')
    c.line(f"M{n(x + 20 * k)},{n(y + 44 * k)} h{n(22 * k)} M{n(x + 48 * k)},{n(y + 14 * k)} v{n(24 * k)}",
           0.8 * k, P.WHITE)
    c.add(f'<circle cx="{n(x + w / 2)}" cy="{n(y + 3 * k)}" r="{n(2.6 * k)}" fill="{P.RED}"/>')
    return (x, y - 2, x + w, y + h)


def hatch(c: Canvas, x: float, foot: float, k: float) -> tuple[float, float, float, float]:
    """A floor hatch, open: a framed opening in the floorboards seen a little from above, the top of a ladder
    coming up out of it - its two rails and rungs; the plank lid swung up on two strap hinges and propped
    against a stay. Returns its box."""
    w, depth = 100 * k, 16 * k
    lw = max(1.0, 1.4 * k)
    c.add(f'<path d="M{n(x - w / 2)},{n(foot)} L{n(x - w / 2 + 8 * k)},{n(foot - depth)} H{n(x + w / 2 - 8 * k)} '
          f'L{n(x + w / 2)},{n(foot)} Z" fill="{P.CHARCOAL}" stroke="{P.WOOD_DARK}" stroke-width="{n(3 * k)}"/>')
    for lx in (x - 22 * k, x + 22 * k):                                                       # the ladder's rails
        c.add(f'<rect x="{n(lx - 3 * k)}" y="{n(foot - 34 * k)}" width="{n(6 * k)}" height="{n(30 * k)}" '
              f'rx="{n(2 * k)}" fill="{P.WOOD}" stroke="{INK}" stroke-width="{n(lw)}"/>')
    for ry in (foot - 24 * k, foot - 12 * k):                                                  # its rungs
        c.add(f'<rect x="{n(x - 19 * k)}" y="{n(ry)}" width="{n(38 * k)}" height="{n(4 * k)}" '
              f'fill="{P.WOOD_LIGHT}" stroke="{INK}" stroke-width="{n(k)}"/>')
    hx = x - w / 2 + 8 * k                                                                      # the lid, up
    lid = (f"M{n(hx)},{n(foot - depth)} L{n(hx - 30 * k)},{n(foot - depth - 84 * k)} "
           f"L{n(hx - 6 * k)},{n(foot - depth - 92 * k)} L{n(hx + 24 * k)},{n(foot - depth - 6 * k)} Z")
    c.add(f'<path d="{lid}" fill="{P.WOOD}" stroke="{INK}" stroke-width="{n(lw)}"/>')
    for t in (0.3, 0.65):                                                                      # its planks
        c.line(f"M{n(hx - 30 * k * t + 0)},{n(foot - depth - 84 * k * t)} l{n(24 * k)},{n(-6 * k)}", 0.9 * k,
               P.WOOD_DARK, 0.8)
    for t in (0.12, 0.8):                                                                      # strap hinges
        c.add(f'<path d="M{n(hx - 30 * k * t + 2 * k)},{n(foot - depth - 84 * k * t)} l{n(14 * k)},{n(-3 * k)}" '
              f'stroke="{P.METAL_DARK}" stroke-width="{n(3 * k)}" stroke-linecap="round"/>')
    c.line(f"M{n(hx + 10 * k)},{n(foot - depth)} L{n(hx - 10 * k)},{n(foot - depth - 50 * k)}", 2 * k,
           P.METAL_DARK)                                                                         # its stay
    return (hx - 32 * k, foot - depth - 94 * k, x + w / 2, foot)


def multitool(x: float, y: float, k: float) -> str:
    """Someone else's odd tool sticking up at (x, y): a red handle and, fanned out of it, a fork, a hook, a
    corkscrew and a little saw - nothing quite like ours."""
    c = Canvas()
    for turn, d in ((-28, "M-1,0 V-26 M-4,-26 V-34 M0,-26 V-34 M4,-26 V-34 M-4,-26 H4"),
                    (-6, "M0,0 V-30 q0,-8 6,-8 q5,0 4,5"),
                    (14, "M0,0 V-10 q4,-2 0,-5 q-4,-2 0,-5 q4,-2 0,-5 q-4,-2 0,-5"),
                    (34, "M-2,0 V-28 H3 L5,-24 L3,-20 L5,-16 L3,-12 L5,-8 L3,-4 V0 Z")):
        c.add(f'<g transform="rotate({turn})"><path d="{d}" fill="none" stroke="{INK}" stroke-width="3.2" '
              f'stroke-linecap="round"/><path d="{d}" fill="none" stroke="{P.METAL_LIGHT}" stroke-width="1.6" '
              f'stroke-linecap="round"/></g>')
    c.shape(rounded_rect_d(-6, -2, 12, 26, 4), P.RED, sw=1.4, light=(-1, -1))
    c.add(f'<circle cx="0" cy="3" r="1.6" fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width=".6"/>')
    return _at(c, x, y, k)


def parcel(s, x: float, foot: float, k: float, word: str) -> tuple[float, float, float, float]:
    """Someone else's skill: a cardboard parcel with its flaps open, brown tape across it, a shipping label on its
    front with the word on it, a barcode and address lines; an odd multi-tool sticking up out of it. Returns its
    box."""
    c = Canvas()
    pw, ph_ = 72 * k, 46 * k
    top = foot - ph_
    c.add(multitool(x + 4 * k, top + 8 * k, k * 1.1))
    c.add(f'<path d="M{n(x - pw / 2)},{n(top)} L{n(x - pw / 2 - 12 * k)},{n(top - 16 * k)} '
          f'L{n(x - pw / 2 + 18 * k)},{n(top - 18 * k)} L{n(x - pw / 2 + 24 * k)},{n(top)} Z" '
          f'fill="{darken(P.KITCHEN_KRAFT, 0.9)}" stroke="{INK}" stroke-width="{n(1.2 * k)}"/>')   # the flaps
    c.add(f'<path d="M{n(x + pw / 2)},{n(top)} L{n(x + pw / 2 + 12 * k)},{n(top - 16 * k)} '
          f'L{n(x + pw / 2 - 18 * k)},{n(top - 18 * k)} L{n(x + pw / 2 - 24 * k)},{n(top)} Z" '
          f'fill="{darken(P.KITCHEN_KRAFT, 0.9)}" stroke="{INK}" stroke-width="{n(1.2 * k)}"/>')
    c.add(f'<rect x="{n(x - pw / 2)}" y="{n(top)}" width="{n(pw)}" height="{n(ph_)}" rx="{n(1.5 * k)}" '
          f'fill="{P.KITCHEN_KRAFT}" stroke="{INK}" stroke-width="{n(1.6 * k)}"/>')
    c.add(f'<rect x="{n(x - 5 * k)}" y="{n(top)}" width="{n(10 * k)}" height="{n(ph_)}" '
          f'fill="{darken(P.KITCHEN_KRAFT, 0.8)}" fill-opacity=".8"/>')                          # the tape
    s.put(foot - 1, c.render(), (x - pw / 2 - 14 * k, top - 40 * k, x + pw / 2 + 14 * k, foot), "parcel",
          group="parcel")
    size = letter(k, 8.0)
    tw, th = tag_size(word, size, k)
    lw_ = max(tw + 16, 34.0)
    lh = th + 22
    pen = Pen(s, x + 8 * k, top + 6 * k, k)                                                    # the shipping label
    box = pen.container("parcel_label", 0, 0, lw_, lh, P.WHITE, radius=1, sw=1.0, light=None)
    pad = pen.pad(lw_, lh)
    pen.tag("parcel_word", lw_ / 2, pad + th / 2, word, size, P.CARD, style="plain", inside=box)
    cy = lh - pad - 5
    count = int((lw_ - 2 * pad) / 2.4)
    pen.c.add("".join(f'<rect x="{n(pad + q * 2.4)}" y="{n(cy)}" width="{n(1.2 if q % 3 else 0.7)}" '
                      f'height="4" fill="{INK}"/>' for q in range(count)))                    # its barcode
    pen.child(box, "parcel_code", pad, cy - 0.5, pad + count * 2.4, cy + 4.5)
    s.put(foot - 0.9, pen.svg(), None, group="parcel")
    return (x - pw / 2 - 14 * k, top - 40 * k, x + pw / 2 + 14 * k, foot)


def blank_card(x: float, y: float, k: float) -> str:
    """A new card being written, held at (x, y): its name line done, its description half written."""
    c = Canvas()
    c.shape(rounded_rect_d(-2, -34, 46, 34, 2), P.CARD, sw=1.4, light=None)
    c.shape(rounded_rect_d(4, -30, 24, 8, 2), P.YELLOW_PALE, sw=1, light=None)
    c.line("M4,-16 H38 M4,-10 H22", 1.1, INK, 0.6)
    return _at(c, x, y, k)


def sparrow_on(s: Strip, x: float, top: float, group: str, pose: str = "stand") -> None:
    """The sparrow standing on a thing of the station (`group`), as big as the room over it allows."""
    for scale in (0.45, 0.36, 0.28):
        bird = _box(s, "sparrow", x, top - 3.5, scale)
        if bird[1] > 2 and all(not b.hits(bird, 3) for b in s.boxes if b.group != group):
            s.actor("sparrow", x, top - 3.5, pose, "smile", flip=True, tall=s.tall * SIZE["sparrow"] * scale,
                    group=group)
            return


def fill(s: Strip, frac: float = 0.8) -> float:
    """How tall a station stands: that share of the professor's height, never above the frame's top."""
    return min(ph(s) * frac, lane(s).feet - 8)


def recipe_stand(s, name: str, x: float, y: float, k: float, title: str) -> tuple[float, float, float, float]:
    """The skill's card standing on the bench top at (x, y), its foot's middle there: a recipe card - its name on a
    tag, the steps as lines - leaning in a clear acrylic stand, the stand's foot and back seen through. Returns its
    box."""
    cw, ch = 64.0, 48.0
    c = Canvas()
    c.add(f'<path d="M{n(x - 38 * k)},{n(y)} H{n(x + 38 * k)} L{n(x + 34 * k)},{n(y - 6 * k)} H{n(x - 34 * k)} Z" '
          f'fill="{P.LENS}" fill-opacity=".55" stroke="{INK}" stroke-width="{n(1.1 * k)}"/>')    # the stand's foot
    c.add(f'<path d="M{n(x - 34 * k)},{n(y - 6 * k)} L{n(x - 30 * k)},{n(y - 58 * k)} H{n(x + 30 * k)} '
          f'L{n(x + 34 * k)},{n(y - 6 * k)} Z" fill="{P.LENS}" fill-opacity=".35" stroke="{INK}" '
          f'stroke-width="{n(1.1 * k)}"/>')                                                         # its back
    s.put(y - 1.4, c.render(), None, group=name)
    pen = Pen(s, x - cw / 2 * k, y - 6 * k - ch * k, k)
    box = pen.container(name, 0, 0, cw, ch, P.CARD, radius=2, sw=1.6, light=None)
    size = letter(k, 10.0)
    tw_, th_ = tag_size(title, size, k)
    pen.tag(f"{name}_title", cw / 2, pen.pad(cw, ch) + th_ / 2, title, size, P.YELLOW_PALE, inside=box)
    pad = pen.pad(cw, ch)
    ly = pad + th_ + 7
    steps = max(1, min(3, int((ch - pad - ly - 2) / 7) + 1))                                     # as many as fit
    for j in range(steps):                                                                      # its steps
        pen.c.add(f'<circle cx="{n(pad + 2)}" cy="{n(ly + j * 7)}" r="1.6" fill="{P.GREEN}"/>')
        pen.c.line(f"M{n(pad + 7)},{n(ly + j * 7)} H{n(cw - pad - (j % 2) * 10)}", 1.2, INK, 0.6)
    pen.child(box, f"{name}_lines", pad, ly - 2, cw - pad, ly + (steps - 1) * 7 + 2)
    s.put(y - 1.2, pen.svg(), None, group=name)
    return (x - 38 * k, y - 6 * k - ch * k, x + 38 * k, y)


def tool_tray(x: float, y: float, k: float) -> str:
    """The open tray of what the card needs, standing on the bench top at (x, y), 70 wide: a wooden tray, and in
    it a jig (a wooden block with a slot), a steel template cut to the part's outline, a small rolled script tied
    with string."""
    c = Canvas()
    c.shape("M-35,0 H35 L32,-14 H-32 Z", P.WOOD, sw=1.4, light=None)                         # the tray
    c.shape("M-24,-14 V-30 H-14 V-22 H-4 V-14 Z", P.WOOD_LIGHT, sw=1.2, light=None)          # the jig
    c.line("M-19,-28 V-20", 1.6, P.WOOD_DARK)
    c.shape("M2,-14 V-34 H10 V-28 H16 V-34 H22 V-14 Z", P.METAL_LIGHT, sw=1.2, light=(-1, -1))  # the template
    c.add(f'<circle cx="12" cy="-20" r="2.4" fill="{P.WOOD}" stroke="{INK}" stroke-width=".8"/>')
    c.shape(rounded_rect_d(24, -24, 8, 10, 2), P.CARD, sw=1.0, light=None)                  # the script
    c.add(f'<ellipse cx="28" cy="-24" rx="4" ry="1.6" fill="{P.CARD}" stroke="{INK}" stroke-width=".8"/>'
          f'<path d="M24,-19 h8" stroke="{P.RED}" stroke-width="1"/>')
    return _at(c, x, y, k)


def toolbox(x: float, y: float, k: float) -> str:
    """A red steel toolbox standing at (x, y), 40 wide: its lid, two latches, a carrying handle on top."""
    c = Canvas()
    c.add(f'<path d="M-10,-22 V-28 H10 V-22" fill="none" stroke="{INK}" stroke-width="3.4"/>'
          f'<path d="M-10,-22 V-28 H10 V-22" fill="none" stroke="{P.METAL}" stroke-width="2"/>')   # the handle
    c.shape(rounded_rect_d(-20, -22, 40, 22, 2), P.RED, sw=1.4, light=(-1, -1))
    c.line("M-20,-15 H20", 1.2, darken(P.RED, 0.6))                                            # the lid's edge
    for lx in (-13, 9):                                                                        # its latches
        c.shape(rounded_rect_d(lx, -17, 4, 6, 1), P.METAL_LIGHT, sw=0.8, light=None)
    return _at(c, x, y, k)


def oil_can(x: float, y: float, k: float) -> str:
    """A small oil can standing at (x, y): a round body, its long spout."""
    c = Canvas()
    c.shape("M-7,0 V-10 Q-7,-14 0,-15 Q7,-14 7,-10 V0 Z", P.YELLOW, sw=1.2, light=(-1, -1))
    c.line("M2,-15 L14,-24", 1.8, P.METAL_DARK)
    c.add(f'<path d="M-7,-6 q-5,0 -5,-4 q0,-4 5,-4" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    return _at(c, x, y, k)


def card_on_bench(x: float, y: float, k: float) -> str:
    """A new card lying on the bench top at (x, y), seen a little from above: its name line written, the first step
    half written."""
    c = Canvas()
    c.shape("M-26,0 L-20,-12 H28 L22,0 Z", P.CARD, sw=1.3, light=None)
    c.shape("M-16,-9 L-15,-11 H0 L-1,-9 Z", P.YELLOW_PALE, sw=0.8, light=None)
    c.line("M-20,-4 H6 M-18,-7 H14", 0.9, INK, 0.6)
    return _at(c, x, y, k)


def punch_card(s, x: float, y: float, k: float, word: str, depth: float) -> None:
    """A punch card standing in the machine's card slot at (x, y), its lower part in the slot: a buff card, rows of
    punched holes, its command written on a tag on it."""
    size = letter(k, 9.0)
    tw_, th_ = tag_size(word, size, k)
    w, h = max(44.0, tw_ + 24), th_ + 30                                  # as big as its word needs
    pen = Pen(s, x - w / 2 * k, y - h * k, k)
    box = pen.container("punch", 0, 0, w, h, mix(P.CARD, P.YELLOW_PALE, 0.6), radius=1.5, sw=1.3, light=None)
    pad = pen.pad(w, h)
    pen.tag("punch_word", w / 2, pad + th_ / 2, word, size, P.SUN, style="plain", inside=box)
    hy = h - pad - 8                                                     # its rows of punched holes
    count = int((w - 2 * pad - 2) / 5)
    pen.c.add("".join(f'<rect x="{n(pad + 1 + q * 5)}" y="{n(hy + (q % 3) * 2.6)}" width="2.4" height="2" '
                      f'fill="{INK}"/>' for q in range(count)))
    pen.child(box, "punch_holes", pad, hy - 0.5, pad + 1 + count * 5, hy + 7.7)
    s.put(depth, pen.svg(), None, group="lathe")


def card_cabinet(s, x: float, foot: float, k: float, words: list[str], picked: int = 1) -> tuple:
    """A card index: an oak cabinet of small drawers on short legs, 130 wide and 150 tall; its top drawer pulled
    out on top, cards standing in it behind tab dividers, each tab with its label; the `picked` card lifted above
    the rest. Returns its box and the lifted card's top."""
    c = Canvas()
    size = letter(k, 10.0)
    widest = max(tag_size(word, size, k)[0] for word in words) * k
    nook = floppy_size()[0] + 6 * k if getattr(s, "egg", None) else 0.0   # room at the drawer's end for the egg
    w, h, legs = max(130 * k, 16 * k + len(words) * (widest + 8 * k) / 2) + nook, 92 * k, 24 * k   # tabs clear
    top = foot - legs - h
    for lx in (x - w / 2 + 6 * k, x + w / 2 - 14 * k):
        c.add(f'<rect x="{n(lx)}" y="{n(foot - legs)}" width="{n(8 * k)}" height="{n(legs)}" fill="{P.WOOD_DARK}" '
              f'stroke="{INK}" stroke-width="{n(k)}"/>')
    c.add(f'<rect x="{n(x - w / 2)}" y="{n(top)}" width="{n(w)}" height="{n(h)}" rx="{n(3 * k)}" fill="{P.WOOD}" '
          f'stroke="{INK}" stroke-width="{n(1.8 * k)}"/>')
    for a in range(3):
        for b in range(3):
            dx, dy = x - w / 2 + 6 * k + a * (w - 12 * k) / 3, top + 6 * k + b * (h - 12 * k) / 3
            dw, dh = (w - 12 * k) / 3, (h - 12 * k) / 3
            c.add(f'<rect x="{n(dx + 2 * k)}" y="{n(dy + 2 * k)}" width="{n(dw - 4 * k)}" height="{n(dh - 4 * k)}" '
                  f'rx="{n(1.5 * k)}" fill="{lighten(P.WOOD, 0.14)}" stroke="{darken(P.WOOD, 0.65)}" '
                  f'stroke-width="{n(k)}"/><rect x="{n(dx + dw / 2 - 7 * k)}" y="{n(dy + 6 * k)}" '
                  f'width="{n(14 * k)}" height="{n(5 * k)}" fill="{P.CARD}" stroke="{P.SUN}" '
                  f'stroke-width="{n(k)}"/><circle cx="{n(dx + dw / 2)}" cy="{n(dy + dh - 7 * k)}" '
                  f'r="{n(2.4 * k)}" fill="none" stroke="{P.SUN}" stroke-width="{n(1.2 * k)}"/>')
    dt = top - 18 * k                                                    # the drawer pulled out on top
    c.add(f'<rect x="{n(x - w / 2 + 4 * k)}" y="{n(dt)}" width="{n(w - 8 * k)}" height="{n(20 * k)}" '
          f'rx="{n(2 * k)}" fill="{lighten(P.WOOD, 0.2)}" stroke="{INK}" stroke-width="{n(1.4 * k)}"/>')
    s.put(foot - 1.2, c.render(), None, group="cabinet")
    step = (w - 16 * k - nook) / len(words)
    pen = Pen(s, 0, 0, 1)
    lift = 0.0
    tags = []
    for i, word in enumerate(words):                                     # cards behind their tab dividers
        cx = x - w / 2 + 8 * k + step * (i + 0.5)
        tw, th = tag_size(word, size, k)
        up = 30 * k if i == picked else (th * k + 2 * k) * (i % 2)     # tabs staggered so no two touch
        pen.c.add(f'<rect x="{n(cx - step * 0.42)}" y="{n(dt - 16 * k - up)}" width="{n(step * 0.84)}" '
                  f'height="{n(22 * k + up)}" fill="{P.CARD}" stroke="{INK}" stroke-width="{n(k)}"/>')
        tags.append((i, word, cx, up))
    for i, word, cx, up in tags:          # the tabs over every card: a tab wider than its card is never covered
        tw, th = tag_size(word, size, k)
        tag = Pen(s, 0, 0, k)
        tag.tag(f"tab{i}", cx / k, (dt - 16 * k - up - th * k / 2 - 2 * k) / k, word, size,
                (P.YELLOW, P.GREEN, P.TEAL, P.METAL_LIGHT)[i % 4], style="plain")
        pen.c.add(tag.svg())
        if up:
            lift = dt - 16 * k - up - th * k - 4 * k
    s.put(foot - 1, pen.c.render(), (x - w / 2, min(lift, dt - 40 * k), x + w / 2, foot), "cabinet",
          group="cabinet")
    if nook:                                          # the golden floppy filed behind the last card (an easter egg)
        stash(s, x + w / 2 - 8 * k - nook / 2, dt + 6 * k, foot - 0.9, group="cabinet", turn=3)
    return (x - w / 2, min(lift, dt - 40 * k), x + w / 2, foot)


def shelving(c: Canvas, x0: float, x1: float, top: float, foot: float, k: float, color: str,
             seed: int = 0) -> list[float]:
    """A tall shelving unit of card boxes from x0 to x1, its top at `top`: green uprights, four shelves, on each a
    row of card boxes centred with even gaps, each with a label holder and index cards showing over its rim.
    Returns the shelves' tops."""
    rnd = random.Random(seed)
    side = 8 * k
    c.add(f'<rect x="{n(x0)}" y="{n(top)}" width="{n(x1 - x0)}" height="{n(foot - top)}" '
          f'fill="{darken(P.WOOD, 0.62)}"/>')
    rows = 4
    gap = (foot - top - 14 * k) / rows
    tops = []
    inner = x1 - x0 - 2 * side
    bw, air = 30 * k, 5 * k
    count = max(1, int((inner - air) / (bw + air)))
    space = (inner - count * bw) / (count + 1)                       # even gaps, the row centred on the shelf
    for j in range(rows):
        y = top + 10 * k + gap * (j + 1)
        bh = min(gap - 12 * k, 30 * k)
        for q in range(count):
            x = x0 + side + space + q * (bw + space)
            box_c = mix(color, P.WOOD_LIGHT, rnd.uniform(0, 0.35))
            c.add(f'<rect x="{n(x)}" y="{n(y - bh)}" width="{n(bw)}" height="{n(bh)}" rx="{n(2 * k)}" '
                  f'fill="{box_c}" stroke="{INK}" stroke-width="{n(1.2 * k)}"/>')
            for p_ in range(3):
                c.add(f'<rect x="{n(x + 4 * k + p_ * 8 * k)}" y="{n(y - bh - 6 * k)}" width="{n(6 * k)}" '
                      f'height="{n(8 * k)}" fill="{P.CARD}" stroke="{INK}" stroke-width="{n(0.7 * k)}"/>')
            c.add(f'<rect x="{n(x + bw / 2 - 7 * k)}" y="{n(y - bh + 6 * k)}" width="{n(14 * k)}" '
                  f'height="{n(6 * k)}" fill="{P.CARD}" stroke="{P.SUN}" stroke-width="{n(k)}"/>')
        c.add(f'<rect x="{n(x0)}" y="{n(y)}" width="{n(x1 - x0)}" height="{n(5 * k)}" fill="{BEAM}" '
              f'stroke="{INK}" stroke-width="{n(k)}"/>')
        tops.append(y)
    for sx_ in (x0, x1 - side):
        c.add(f'<rect x="{n(sx_)}" y="{n(top)}" width="{n(side)}" height="{n(foot - top)}" fill="{BEAM}" '
              f'stroke="{INK}" stroke-width="{n(1.4 * k)}"/>')
    c.add(f'<rect x="{n(x0 - 4 * k)}" y="{n(top - 6 * k)}" width="{n(x1 - x0 + 8 * k)}" height="{n(10 * k)}" '
          f'rx="{n(2 * k)}" fill="{BEAM}" stroke="{INK}" stroke-width="{n(1.4 * k)}"/>')
    return tops


def stairs_top(c: Canvas, x: float, foot: float, k: float, right: bool = True) -> tuple[float, float, float, float]:
    """The stairwell: an opening in the floor seen from above, its edge trimmed with a nosing, the top steps going
    down into it - each lower one darker and narrower; along its far side a banister - a handrail on turned
    balusters - ending at the near corner in a square newel post with a round cap. `x` is the newel post; the
    opening runs from it to the right (or the left). Returns its box; the cap's top is the box's top."""
    d = 1 if right else -1
    w = 110 * k
    depth = 12 * k                                                    # how deep the opening looks from here
    far, near = x + d * w, x
    c.add(f'<path d="M{n(near)},{n(foot)} L{n(near + d * 6 * k)},{n(foot - depth)} H{n(far)} V{n(foot)} Z" '
          f'fill="{P.CHARCOAL}"/>')                                                          # the opening
    for q in range(3):                                                                        # the steps down
        sy = foot - depth + 3 * k + q * 3 * k
        inset = (q + 1) * 6 * k
        c.add(f'<rect x="{n(min(near + d * inset, far - d * 4 * k))}" y="{n(sy)}" '
              f'width="{n(w - inset - 4 * k)}" height="{n(2.4 * k)}" fill="{darken(P.WOOD, 0.9 - q * 0.15)}"/>')
    c.add(f'<path d="M{n(near)},{n(foot)} L{n(near + d * 6 * k)},{n(foot - depth)} H{n(far)}" fill="none" '
          f'stroke="{P.WOOD_DARK}" stroke-width="{n(2.4 * k)}"/>')                         # the nosing
    post_h = 92 * k
    rail_y0, rail_y1 = foot - post_h + 14 * k, foot - depth - 46 * k
    for q in range(1, 6):                                                                     # the balusters
        t = q / 6
        bx = near + d * 6 * k + (far - near - d * 6 * k) * t
        by = rail_y0 + (rail_y1 - rail_y0) * t
        c.add(f'<path d="M{n(bx)},{n(by)} V{n(foot - depth)}" stroke="{INK}" stroke-width="{n(4.4 * k)}"/>'
              f'<path d="M{n(bx)},{n(by)} V{n(foot - depth)}" stroke="{BEAM}" stroke-width="{n(2.6 * k)}"/>'
              f'<ellipse cx="{n(bx)}" cy="{n((by + foot - depth) / 2)}" rx="{n(2.6 * k)}" ry="{n(5 * k)}" '
              f'fill="{BEAM}" stroke="{INK}" stroke-width="{n(0.8 * k)}"/>')
    c.add(f'<path d="M{n(x)},{n(rail_y0)} L{n(far)},{n(rail_y1)}" stroke="{INK}" stroke-width="{n(8 * k)}" '
          f'stroke-linecap="round"/><path d="M{n(x)},{n(rail_y0)} L{n(far)},{n(rail_y1)}" stroke="{P.WOOD}" '
          f'stroke-width="{n(5 * k)}" stroke-linecap="round"/>')                            # the handrail
    c.add(f'<rect x="{n(x - 6 * k)}" y="{n(foot - post_h)}" width="{n(12 * k)}" height="{n(post_h)}" '
          f'fill="{BEAM}" stroke="{INK}" stroke-width="{n(1.4 * k)}"/>'
          f'<rect x="{n(x - 8 * k)}" y="{n(foot - post_h - 4 * k)}" width="{n(16 * k)}" height="{n(5 * k)}" '
          f'rx="{n(1 * k)}" fill="{darken(BEAM, 0.8)}" stroke="{INK}" stroke-width="{n(k)}"/>'
          f'<circle cx="{n(x)}" cy="{n(foot - post_h - 10 * k)}" r="{n(7 * k)}" fill="{darken(BEAM, 0.8)}" '
          f'stroke="{INK}" stroke-width="{n(1.4 * k)}"/>')                                  # the newel and its cap
    return (min(x, far) - 10 * k, foot - post_h - 17 * k, max(x, far) + 4 * k, foot)


def bracket(x: float, y: float, k: float) -> str:
    """A small steel angle bracket standing at (x, y), 16 wide: its two flanges, two screw holes."""
    c = Canvas()
    c.shape("M-8,0 V-16 H-3 V-5 H8 V0 Z", P.METAL_LIGHT, sw=1.2, light=(-1, -1))
    c.add(f'<circle cx="-5.5" cy="-11" r="1.3" fill="{P.METAL_DARK}"/><circle cx="3" cy="-2.5" r="1.3" '
          f'fill="{P.METAL_DARK}"/>')
    return _at(c, x, y, k)


def long_bench(c: Canvas, x: float, foot: float, k: float, parts: int = 0, vice: bool = True) -> dict:
    """A long, deep workbench, its foot's middle at (x, foot), 230 wide and 62 tall: a thick top seen a little
    from above, its front apron, four square legs standing on the floor with their feet, a low stretcher shelf, a
    red toolbox on it; a green vice at the right end, an oil can by it; `parts` identical brackets lined up in a
    shallow tray on the top. Returns where things sit."""
    w, h = 230 * k, 62 * k
    top = foot - h
    lw = max(1.0, 1.4 * k)
    for lx in (x - w / 2 + 8 * k, x + w / 2 - 16 * k):                                            # the back legs
        c.add(f'<rect x="{n(lx + 10 * k)}" y="{n(top - 4 * k)}" width="{n(7 * k)}" height="{n(h - 6 * k)}" '
              f'fill="{darken(P.WOOD_DARK, 0.8)}" stroke="{INK}" stroke-width="{n(lw)}"/>')
    c.add(f'<rect x="{n(x - w / 2 + 6 * k)}" y="{n(foot - 18 * k)}" width="{n(w - 12 * k)}" height="{n(6 * k)}" '
          f'fill="{P.WOOD}" stroke="{INK}" stroke-width="{n(lw)}"/>')                       # the stretcher shelf
    c.add(toolbox(x - 30 * k, foot - 18 * k, k * 0.9))
    for lx in (x - w / 2 + 8 * k, x + w / 2 - 16 * k):                                          # the front legs
        c.add(f'<rect x="{n(lx)}" y="{n(top + 10 * k)}" width="{n(8 * k)}" height="{n(h - 12 * k)}" '
              f'fill="{P.WOOD_DARK}" stroke="{INK}" stroke-width="{n(lw)}"/>'
              f'<rect x="{n(lx - 1.5 * k)}" y="{n(foot - 3 * k)}" width="{n(11 * k)}" height="{n(3 * k)}" '
              f'rx="{n(1 * k)}" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="{n(0.8 * k)}"/>')   # its foot
    c.add(f'<path d="M{n(x - w / 2)},{n(top)} L{n(x - w / 2 + 10 * k)},{n(top - 12 * k)} H{n(x + w / 2 + 10 * k)} '
          f'L{n(x + w / 2)},{n(top)} Z" fill="{P.WOOD_LIGHT}" stroke="{INK}" stroke-width="{n(lw)}"/>')   # its top
    c.line(f"M{n(x - w / 2 + 30 * k)},{n(top - 6 * k)} H{n(x + w / 2 - 20 * k)}", 0.8 * k, P.WOOD, 0.8)
    c.add(f'<rect x="{n(x - w / 2)}" y="{n(top)}" width="{n(w)}" height="{n(10 * k)}" fill="{P.WOOD}" '
          f'stroke="{INK}" stroke-width="{n(lw)}"/>')                                        # the apron
    if vice:
        vx = x + w / 2 - 22 * k
        c.add(f'<rect x="{n(vx - 12 * k)}" y="{n(top - 30 * k)}" width="{n(24 * k)}" height="{n(22 * k)}" '
              f'rx="{n(3 * k)}" fill="{MACHINE}" stroke="{INK}" stroke-width="{n(lw)}"/>'
              f'<rect x="{n(vx - 15 * k)}" y="{n(top - 34 * k)}" width="{n(30 * k)}" height="{n(6 * k)}" '
              f'rx="{n(1.5 * k)}" fill="{P.METAL}" stroke="{INK}" stroke-width="{n(k)}"/>')
        c.line(f"M{n(vx + 12 * k)},{n(top - 20 * k)} h{n(16 * k)} M{n(vx + 28 * k)},{n(top - 26 * k)} v{n(12 * k)}",
               2.4 * k, P.METAL_DARK)
        c.add(oil_can(vx - 34 * k, top - 8 * k, k))
    tray = None
    if parts:
        tw_ = min(w * 0.55, (parts * 18 + 14) * k)
        tx0 = x - w / 2 + 24 * k
        c.add(f'<rect x="{n(tx0)}" y="{n(top - 14 * k)}" width="{n(tw_)}" height="{n(8 * k)}" rx="{n(2 * k)}" '
              f'fill="{BEAM}" stroke="{INK}" stroke-width="{n(k)}"/>')                     # the tray
        step = (tw_ - 14 * k) / max(1, parts - 1)
        for i in range(parts):
            c.add(bracket(tx0 + 7 * k + i * step, top - 12 * k, k))
        tray = (tx0, top - 30 * k, tx0 + tw_, top)
    return {"top": top - 6 * k, "box": (x - w / 2, top - 36 * k, x + w / 2 + 34 * k, foot), "tray": tray,
            "vice": (x + w / 2 - 22 * k, top - 34 * k)}


def bench_k(s: Strip) -> float:
    """The long bench's scale: its top at the cast's waist, whole in the frame."""
    r = lane(s)
    return min(ph(s) * 0.48 / 62, (r.feet - 8) / 100, span(s, 0.42 if s.h < 400 else 0.38) / 264)


def when_station(s: Strip, beat: str) -> None:
    """When to write a skill: the long workbench with a tray of identical brackets on it, more of them every page.
    "third": the agent at one end has made yet another one, the cat at the other watches. "notice": the professor
    (the caterpillar in a mid strip) points at the full tray, the agent shrugs; the sparrow on the vice."""
    r = lane(s)
    bk = bench_k(s)
    x = inside(s, sx(s, 0.47 if beat == "third" else 0.42), 116 * bk, 150 * bk)
    c = Canvas()
    b = long_bench(c, x, r.feet, bk, parts=6 if beat == "third" else 9)
    s.put(r.feet - 1, c.render(), b["box"], "bench", group="bench")
    if beat == "third":
        stand(s, "agent", M(s, (0.1, 0.05, 0.14)), "point", "worry", flip=F(s, False))
        stand(s, "cat", M(s, (0.9, 0.95, 0.86)), "think", "smile", flip=F(s, True))
    else:
        stand(s, "caterpillar" if mid(s) else "professor", M(s, (0.06, 0.03, 0.1)), "point", "talk",
              flip=F(s, False))
        stand(s, "agent", M(s, (0.88, 0.92, 0.84)), "shrug", "worry", flip=F(s, True))
        vx, vy = b["vice"]
        sparrow_on(s, vx, vy, "bench")


def write_station(s: Strip, beat: str) -> None:
    """The agent writes the card itself at the long bench after the job: it stands behind the bench, the card lies
    on the top before it and the pencil runs from its hand down to the card's last line. "write": the professor
    (the cat in a mid strip) watching, the sparrow on the vice. "read": the cat and the caterpillar look the card
    over from the bench's two ends."""
    r = lane(s)
    bk = bench_k(s)
    x = inside(s, sx(s, 0.4 if beat == "write" else 0.5), 116 * bk, 150 * bk)
    c = Canvas()
    b = long_bench(c, x, r.feet, bk, parts=2)
    s.put(r.feet - 1, c.render(), b["box"], "bench", group="bench")
    cx = x - 30 * bk
    if beat == "write":                                   # behind the bench, its legs hidden by it, writing
        tall = s.tall * SIZE["agent"] * 0.95
        probe = Stage()
        gx, gy, angle = probe.grip(probe.actor("agent", cx, r.feet, "present", "smile", flip=True, tall=tall),
                                   "right", "present")
        reach = (r.feet - gy) / tall - 0.114              # the fist's height over the feet, less the pencil
        tall = min(tall, (r.feet - 4 - b["top"] - 2 * bk) / reach)     # short enough to reach down to the top
        gx, gy, angle = probe.grip(probe.actor("agent", cx, r.feet, "present", "smile", flip=True, tall=tall),
                                   "right", "present")
        point = 11.4 * tall / 100                         # the pencil's point under the fist, held upright
        lift = gy + point - (b["top"] + 2 * bk)           # stand it so the point touches the card on the top
        who = s.actor("agent", cx + (cx - gx), r.feet - lift, "present", "smile", flip=True, tall=tall,
                      group="bench", depth=r.feet - 2)
        s.hold(who, handheld.pencil, turn=-angle)
        s.put(r.feet - 0.8, card_on_bench(cx, b["top"] + 4 * bk, bk * 1.3), None, group="bench")
        stand(s, "cat" if mid(s) else "professor", M(s, (0.9, 0.94, 0.86)), "think", "smile", flip=F(s, True))
        vx, vy = b["vice"]
        sparrow_on(s, vx, vy, "bench")
    else:
        s.put(r.feet - 0.8, card_on_bench(cx, b["top"] + 4 * bk, bk * 1.3), None, group="bench")
        stand(s, "cat", M(s, (0.9, 0.94, 0.86)), "point", "smile", flip=F(s, True))
        stand(s, "caterpillar", M(s, (0.06, 0.03, 0.1)), "think", "worry", flip=F(s, False))


def lathe_k(s: Strip, share: float) -> float:
    """The lathe's scale: its bed at the cast's waist, the whole machine with its lamp inside the frame."""
    r = lane(s)
    return min(ph(s) * 0.5 / 100, (r.feet - 8) / LATHE_H, span(s, max(share, 0.46)) / 276)


# ============================================================================ the stations
def playbooks_station(s: Strip, beat: str) -> None:
    """The playbooks you already have: big old step-by-step sheets tacked to a green roof beam, their numbered
    lines and ticks. "read": the agent reads one, the caterpillar ticks her checklist, the sparrow on the beam.
    "tick": the professor points at a step, the caterpillar ticks it off, the sparrow at the beam's other end."""
    r = lane(s)
    f = fill(s, 1.0)
    sk = min(f * 0.62 / 92, span(s, 0.46) / 250)
    y = max(16 * sk, r.feet - f)
    width = min(span(s, 0.48), 260 * sk)
    x0 = sx(s, 0.02) if not s.mirror else sx(s, 0.02) - width
    box = sheets_beam(s, x0, x0 + width, y, sk)
    if beat == "read":
        stand(s, "agent", M(s, (0.62, 0.66, 0.58)), "read", "smile", flip=F(s, True))
        held(s, stand(s, "caterpillar", M(s, (0.86, 0.9, 0.82)), "present", "smile", flip=F(s, True)),
             handheld.clipboard)
        sparrow(s, box[0] + 16 * sk if not s.mirror else box[2] - 16 * sk, box[1], "stand")
    else:
        stand(s, "professor", M(s, (0.62, 0.66, 0.58)), "point", "talk", flip=F(s, True))
        held(s, stand(s, "caterpillar", M(s, (0.86, 0.9, 0.82)), "present", "smile", flip=F(s, True)),
             handheld.clipboard)
        sparrow(s, box[2] - 16 * sk if not s.mirror else box[0] + 16 * sk, box[1], "stand")


def card_station(s: Strip, beat: str) -> None:
    """How a skill is made: on the long bench, the recipe card in its clear stand - name, steps - and beside it the
    open tray of what the card needs. "show": the professor (the cat in a mid strip) points at it, the agent reads
    it. "tray": the agent points into the tray, the caterpillar checks it off on her clipboard."""
    r = lane(s)
    bk = bench_k(s)
    x = inside(s, sx(s, 0.45), 116 * bk, 120 * bk)
    c = Canvas()
    b = long_bench(c, x, r.feet, bk, vice=False)
    c.add(tool_tray(x + 50 * bk, b["top"] + 4 * bk, bk * 1.1))
    s.put(r.feet - 1, c.render(), b["box"], "bench", group="skill_card")
    recipe_stand(s, "skill_card", x - 40 * bk, b["top"] + 4 * bk, bk * 1.1, s.word("skill"))
    if beat == "show":
        stand(s, "cat" if mid(s) else "professor", M(s, (0.1, 0.06, 0.14)), "point", "talk", flip=F(s, False))
        stand(s, "agent", M(s, (0.86, 0.9, 0.82)), "think", "smile", flip=F(s, True))
    else:
        stand(s, "agent", M(s, (0.86, 0.9, 0.82)), "point", "smile", flip=F(s, True))
        held(s, stand(s, "caterpillar", M(s, (0.1, 0.06, 0.14)), "present", "worry", flip=F(s, False)),
             handheld.clipboard)


def index_station(s: Strip, beat: str) -> None:
    """The description decides: the card index cabinet, its top drawer out, the cards behind their tabs. "pick":
    the agent lifts one card by its tab alone, the cat explains, the sparrow on the cabinet. "pass": the vague tab
    (anything and everything) is passed over - the caterpillar points at it, doubting."""
    r = lane(s)
    ik = min(fill(s, 0.86) / 150, (r.feet - 8) / 215, span(s, 0.4) / 170)
    foot = r.feet
    x = inside(s, sx(s, 0.42), 70 * ik, 70 * ik)
    words = [s.word(key) for key in ("tab1", "tab2", "tab3", "tab4")]
    box = card_cabinet(s, x, foot, ik, words, picked=1 if beat == "pick" else -1)
    if beat == "pick":
        stand(s, "agent", M(s, (0.12, 0.08, 0.16)), "point", "smile", flip=F(s, False))
        stand(s, "cat", M(s, (0.8, 0.84, 0.76)), "think", "talk", flip=F(s, True))
        sparrow(s, box[2] - 14 * ik, box[1] + 30 * ik, "stand")
    else:
        stand(s, "caterpillar", M(s, (0.8, 0.84, 0.76)), "point", "worry", flip=F(s, True))
        stand(s, "agent", M(s, (0.12, 0.08, 0.16)), "think", "smile", flip=F(s, False))


def command_station(s: Strip, beat: str) -> None:
    """Commands are skills too: the lathe's control box takes a punch card with the command "/adr" on it. "pull":
    the card stands half into the slot, the agent beside the box points at it, the professor (the cat in a mid
    strip) watches from the other end. "run": the card has gone in and the machine runs that job - chips curling,
    the chuck spinning, the lamp lit - the agent cheers, the cat watches, the sparrow on the lamp."""
    r = lane(s)
    lk = lathe_k(s, 0.5 if s.h < 300 else 0.46)
    x = inside(s, sx(s, 0.46), -LATHE_W[0] * lk, LATHE_W[1] * lk)
    c = Canvas()
    parts = lathe(c, x, r.feet, lk, running=beat == "run", slot=True)
    s.put(r.feet - 1, c.render(), lathe_box(x, r.feet, lk), "lathe", group="lathe")
    px, py = parts["slot"]
    punch_card(s, px, py + (14 if beat == "pull" else 26) * lk, lk, s.word("adr"), r.feet - 1.1)
    if beat == "pull":
        stand(s, "agent", M(s, (0.92, 0.95, 0.88)), "point", "smile", flip=F(s, True))
        stand(s, "cat" if mid(s) else "professor", M(s, (0.06, 0.1, 0.03)), "think", "smile", flip=F(s, False))
    else:
        stand(s, "agent", M(s, (0.92, 0.95, 0.88)), "cheer", "smile", flip=F(s, True))
        stand(s, "cat", M(s, (0.06, 0.1, 0.03)), "think", "smile", flip=F(s, False))
        lx, ly = parts["lamp"]
        sparrow_on(s, lx, ly, "lathe")


def where_station(s: Strip, beat: str) -> None:
    """Where skills lie: two tall shelving units of card boxes - the personal one by the dormer window, the
    project's at the top of the stairs, by the stairwell's banister. "shelves": the caterpillar checks the
    personal one, the agent shows the project's, the sparrow on the newel post's cap. "put": the agent points to
    the project's shelf for the new box, the cat agrees, the sparrow on the shelving's top."""
    r, k = lane(s), s.unit
    f = min(fill(s, 1.08), r.feet - 14)
    uw = min(span(s, 0.22 if s.h < 200 else 0.16), 130 * k)
    uk = uw / 130
    c = Canvas()
    lx = s.lo + 6
    shelving(c, lx, lx + uw, r.feet - f, r.feet, uk, P.GREEN, seed=1)                  # the personal one
    ww = uw * 0.7                                                                      # its dormer window beside
    wy = r.feet - f
    c.add(f'<rect x="{n(lx + uw + 14 * k)}" y="{n(wy + 10 * k)}" width="{n(ww)}" height="{n(ww * 0.9)}" '
          f'fill="{lighten(P.SKY, 0.15)}" stroke="{BEAM}" stroke-width="{n(6 * k)}"/>')
    c.line(f"M{n(lx + uw + 14 * k + ww / 2)},{n(wy + 10 * k)} v{n(ww * 0.9)}", 3 * k, BEAM)
    px0 = s.hi - 6 - uw                                                               # the project's one, right
    shelving(c, px0, px0 + uw, r.feet - f, r.feet, uk, P.TEAL, seed=2)
    sk = min(uk * 0.9, (r.feet - 10) / 120)
    stairs = stairs_top(c, px0 - 10 * sk, r.feet, sk, right=False)                     # the stairwell beside it
    s.put(1.4, c.render(), [(lx - 4, r.feet - f - 10, lx + uw + 4, r.feet),
                            (px0 - 4, r.feet - f - 10, px0 + uw + 4, r.feet), stairs], "shelves", group="shelves")
    if beat == "shelves":                                 # the second page: the two trade places
        stand(s, "caterpillar", (0.6, 0.64, 0.56) if s.shot else (0.36, 0.32, 0.4), "think", "worry",
              flip=bool(s.shot))
        stand(s, "agent", (0.38, 0.34, 0.42) if s.shot else (0.56, 0.52, 0.6), "point", "smile", flip=not s.shot)
        sparrow_on(s, px0 - 10 * sk, stairs[1] + 0.5, "shelves")                       # on the newel post's cap
    else:
        stand(s, "agent", (0.62, 0.58, 0.66) if s.shot else (0.5, 0.46, 0.54), "point", "smile", flip=True)
        stand(s, "cat", (0.42, 0.38, 0.46) if s.shot else (0.34, 0.3, 0.38), "think", "smile", flip=False)
        sparrow_on(s, px0 + uw / 2, r.feet - f - 6 * uk, "shelves")
    handbook_shelf(s, r)


def handbook_shelf(s: Strip, r) -> None:
    """The book inside the book: the professor's own handbook lying on a small shelf of its own on the wall, its
    spine to the viewer - put up where the wall is free once the station and its cast stand (none where it is not)."""
    title = s.word("fortran")
    tw, th = tome_size(title)
    sw = tw + 18                                          # the board, a little longer than the book
    for y in (r.feet * f for f in (0.5, 0.56, 0.44, 0.62, 0.38)):
        for x in sorted((s.lo + sw / 2 + q * 8 for q in range(int((s.hi - s.lo - sw) / 8) + 1)),
                        key=lambda v: abs(v - s.x(0.5))):
            box = (x - sw / 2, y - th - 2, x + sw / 2, y + 14)
            if box[1] < 4 or not s.free(box, 6):
                continue
            c = Canvas()
            c.add(tome(x, y, title, P.BLUE))
            c.add(f'<rect x="{n(x - sw / 2)}" y="{n(y)}" width="{n(sw)}" height="5" rx="1.5" fill="{BEAM}" '
                  f'stroke="{INK}" stroke-width="1.2"/>')                                 # the board
            for bx in (x - sw / 2 + 8, x + sw / 2 - 8):                                  # its two brackets
                c.add(f'<path d="M{n(bx - 1.5)},{n(y + 5)} h3 v8 l-3,-3 Z" fill="{P.METAL_DARK}" stroke="{INK}" '
                      f'stroke-width="1"/>')
            s.put(1.3, c.render(), box, "handbook", group="handbook")
            return


def check_station(s: Strip, beat: str) -> None:
    """Does the skill work: the lathe turns the part from the card, its drawing pinned on the wall above. "make":
    the cat checks the part with his caliper against the drawing, the caterpillar compares twice on her clipboard.
    "stop": the sparrow on the headstock reaches for the big red emergency stop, the agent waves him off it, the
    caterpillar worries."""
    r = lane(s)
    lk = lathe_k(s, 0.46)
    x = inside(s, sx(s, 0.48), -LATHE_W[0] * lk, LATHE_W[1] * lk)
    c = Canvas()
    parts = lathe(c, x, r.feet, lk, running=beat == "make")
    boxes = [lathe_box(x, r.feet, lk)]
    dy = parts["box"][1] - 56 * lk
    if dy > 6:                                                        # the drawing, where the wall has room for it
        boxes.append(drawing(c, x + 10 * lk, dy, lk))
    s.put(r.feet - 1, c.render(), boxes, "lathe", group="lathe")
    if beat == "make":
        held(s, stand(s, "cat", M(s, (0.88, 0.92, 0.84)), "present", "smile", flip=F(s, True)), handheld.caliper)
        held(s, stand(s, "caterpillar", M(s, (0.08, 0.04, 0.12)), "present", "worry", flip=F(s, False)),
             handheld.clipboard)
        return
    ex, ey = parts["stop"]
    sparrow_on(s, ex, ey, "lathe", "point")
    stand(s, "agent", M(s, (0.08, 0.04, 0.12)), "wave", "worry", flip=F(s, False))
    stand(s, "caterpillar", M(s, (0.9, 0.94, 0.86)), "think", "worry", flip=F(s, True))


def foreign_station(s: Strip, beat: str) -> None:
    """Someone else's skill comes up through the floor hatch in a parcel with an odd tool in it. "parcel": the
    caterpillar points at it, doubting, the cat holds back. "label": the cat reads its shipping label before it
    goes on any shelf, the caterpillar still doubting."""
    r = lane(s)
    hk = min(fill(s, 0.85) / 110, (r.feet - 8) / 112, span(s, 0.46 if s.h < 200 else 0.34) / 250)
    x = inside(s, sx(s, 0.42), 82 * hk, 196 * hk)
    c = Canvas()
    hb = hatch(c, x, r.feet, hk)
    s.put(1.3, c.render(), hb, "hatch", group="hatch")
    parcel(s, x + 124 * hk, r.feet, hk * 1.3, s.word("label"))
    if beat == "parcel":
        stand(s, "caterpillar", M(s, (0.9, 0.94, 0.86)), "point", "worry", flip=F(s, True))
        stand(s, "cat", M(s, (0.06, 0.03, 0.1)), "think", "smile", flip=F(s, False))
    else:
        stand(s, "cat", M(s, (0.9, 0.94, 0.86)), "think", "smile", flip=F(s, True))
        stand(s, "caterpillar", M(s, (0.06, 0.03, 0.1)), "think", "worry", flip=F(s, False))


# ============================================================================ the finale
BAYS = (("playbooks", "card"), ("index",), ("when", "write"), ("command",), ("where",), ("check", "foreign"))
BAY_WIDTHS = (0.95, 0.9, 1.25, 1.25, 0.8, 0.95)


def finale(s: Strip) -> None:
    """The whole attic at once: rafters and their wall plate across the top, six bays along the wall, each with its
    stations' thing - the playbooks on their beam, the card index cabinet, the long bench with its brackets, the
    lathe with its control box, the shelving of card boxes, the hatch with the parcel - each station's name right
    over its own thing, one or two to a bay; the cast in front on the planks."""
    ledger(s)
    zoom(s)
    backdrop(s, 2)
    r = lane(s)
    left, right = s.lo, s.hi
    share = [w_ / sum(BAY_WIDTHS) * (right - left) for w_ in BAY_WIDTHS]   # the long machines get wider bays
    edges = [left + sum(share[:i]) for i in range(len(BAYS) + 1)]
    wide = min(share)
    plate = s.base * 0.3 + 14 if s.h >= 200 else 4.0
    room = r.feet - plate - 30 - (2 * 26 if s.h >= 300 else 0)          # two names over a bay at most
    k = max(0.35, min(wide / 118, room / 170))
    tops = []
    for i, keys in enumerate(BAYS):
        x, bw = (edges[i] + edges[i + 1]) / 2, share[i]
        main = keys[0]
        if main == "playbooks":
            sk = k * 0.9
            box = sheets_beam(s, x - bw * 0.42, x + bw * 0.42, r.feet - 150 * sk, sk, count=2)
            tops.append(box[1])
        elif main == "index":
            box = card_cabinet(s, x, r.feet, min(k * 0.8, (bw - 16) / 150), [s.word("tab1"), s.word("tab3")], picked=-1)
            tops.append(box[1])
        else:
            c = Canvas()
            if main == "when":
                bk = min(k, (bw - 12) / 264)
                b = long_bench(c, x - 14 * bk, r.feet, bk, parts=4)
                tops.append(b["box"][1])
            elif main == "command":
                lk = min(k * 0.85, (bw - 8) / (LATHE_W[1] - LATHE_W[0]))
                lathe(c, x - (LATHE_W[0] + LATHE_W[1]) / 2 * lk, r.feet, lk, running=True)
                tops.append(r.feet - LATHE_H * lk)
            elif main == "where":
                uw = bw * 0.7
                shelving(c, x - uw / 2, x + uw / 2, r.feet - 170 * k, r.feet, uw / 130, P.TEAL)
                tops.append(r.feet - 176 * k)
            else:
                hk = min(k * 0.6, (bw - 10) / 220)
                hatch(c, x - 20 * hk, r.feet, hk)
                c.add(f'<rect x="{n(x + 40 * hk)}" y="{n(r.feet - 46 * hk)}" width="{n(60 * hk)}" '
                      f'height="{n(46 * hk)}" rx="{n(2 * hk)}" fill="{P.KITCHEN_KRAFT}" stroke="{INK}" '
                      f'stroke-width="{n(1.4 * hk)}"/>')
                tops.append(r.feet - 100 * hk)
            s.put(1.2, c.render(), None)
    cast_ = {0: ("professor", "point"), 1: ("agent", "wave"), 3: ("cat", "think"), 5: ("caterpillar", "think")}
    for i, (name, pose) in cast_.items():
        x = edges[i] + share[i] * 0.72
        over = min(tops[i], tops[min(i + 1, len(tops) - 1)]) + 6         # its head stays under the names
        tall = min(s.tall * SIZE[name] * 1.8, _fit_tall(name, wide * 0.8, r.feet - max(plate + 60, over)))
        group = {0: "playbooks", 1: "cabinet"}.get(i, f"f{i}")   # standing before its bay's thing
        s.actor(name, min(x, s.hi - 40), r.feet, pose, "smile", flip=True, tall=tall, group=group)
    if s.h >= 300:                                                  # each bay's names right over its own thing
        pen = Pen(s, 0, 0, 1)
        size = 12.0
        widest = max(tag_size(s.word(key), size)[0] for keys in BAYS for key in keys)
        if widest > wide - 26:                                      # the tag's own padding comes on top
            size = max(sets.LETTERING_MIN + 1, size * (wide - 26) / widest)
        th = tag_size("Ag", size)[1]
        for i, keys in enumerate(BAYS):
            y = tops[i] - th / 2 - 10
            for key in reversed(keys):
                text = s.word(key)
                tw = tag_size(text, size)[0] + 16
                lx = min(max((edges[i] + edges[i + 1]) / 2, s.lo + tw / 2 + 4), s.hi - tw / 2 - 4)
                while y - th > plate and not s.free((lx - tw / 2, y - th / 2, lx + tw / 2, y + th / 2), 4):
                    y -= 4                                              # a long name next door: a little higher
                holder = pen.tag(f"label{key}", lx, y, text, size, P.CHARCOAL, P.WHITE)
                s.put(2, "", holder.outer, f"label{key}")
                y -= th + 6
        s.put(2, pen.svg(), None)


# ============================================================================ the opener
def opener(st: Stage, accent: str):
    """The attic workshop, one hero: a big green lathe across the middle of the floor, running - chips curling off
    the cut, the chuck spinning, its gooseneck lamp lit; the sloped green ceiling with its rafters
    and a skylight, calm where the title goes; the wall of pale green boards over a green planked wainscot, with
    only a few large things on it - a pegboard of tools, the card index on its shelf, one card
    flying out of it. Before the lathe the cast, big: the professor under his bubble tells them what a skill is,
    the cat points at the cut, the caterpillar watches a careful step back, the agent cheers at the lathe's end;
    the sparrow sits on the lathe's lamp."""
    ledger(st)
    c = st.back
    floor = 1000.0
    c.add(f'<rect x="0" y="0" width="{W}" height="{n(floor)}" fill="{WALL}"/>')
    for i in range(int(W / 34) + 1):
        c.add(f'<rect x="{i * 34}" y="300" width="34" height="{floor - 300}" '
              f'fill="{darken(WALL, 0.96) if i % 3 == 0 else WALL}"/>')
        c.line(f"M{i * 34},300 V{floor}", 1.2, darken(WALL, 0.84))
    wy = 790.0                                                                             # the wainscot
    c.add(f'<rect x="0" y="{wy}" width="{W}" height="{floor - wy}" fill="{PANEL}"/>')
    for i in range(int(W / 36) + 1):
        c.line(f"M{i * 36},{wy} V{floor}", 1.3, darken(PANEL, 0.82))
    c.add(f'<rect x="-6" y="{wy - 12}" width="{W + 12}" height="13" fill="{BEAM}" stroke="{INK}" '
          f'stroke-width="1.6"/>')
    roof = c.gradient([(0, darken(P.GREEN, 0.55)), (1, mix(P.GREEN, P.WOOD_PALE, 0.25))], 0, 0, 0, 320)
    c.add(f'<path d="M0,0 H{W} V250 L{W / 2},320 L0,250 Z" fill="{roof}"/>')          # the sloped ceiling
    for j in range(7):
        x = j * W / 6
        y1 = 250 + 70 * (1 - abs(x - W / 2) / (W / 2))
        c.add(f'<path d="M{n(x)},0 L{n(W / 2 + (x - W / 2) * 1.1)},{n(y1)}" stroke="{INK}" stroke-width="24"/>'
              f'<path d="M{n(x)},0 L{n(W / 2 + (x - W / 2) * 1.1)},{n(y1)}" stroke="{BEAM}" stroke-width="20"/>')
    c.add(f'<path d="M-6,244 L{W / 2},314 L{W + 6},244" fill="none" stroke="{INK}" stroke-width="28"/>'
          f'<path d="M-6,244 L{W / 2},314 L{W + 6},244" fill="none" stroke="{BEAM}" stroke-width="24"/>')
    # the skylight, beside the title whatever its width: a long first line must never cover its frame
    sx = min(max(640.0, st.reserved[0][2] + 16 if st.reserved else 640.0), W - 36 - 130)
    sky = f"M{n(sx)},60 H{n(sx + 130)} V200 H{n(sx)} Z"
    c.add(f'<path d="{sky}" fill="{lighten(P.SKY, 0.15)}" stroke="{BEAM}" stroke-width="12"/>'
          f'<path d="{sky}" fill="none" stroke="{INK}" stroke-width="2"/>')
    c.line(f"M{n(sx + 65)},60 V200 M{n(sx)},130 H{n(sx + 130)}", 5, BEAM)
    unit(c, "pegboard", 360, 500, 380, 1000, 1.7, seed=5)                    # clear of the bubble at the left
    st.keep_clear((-6, 236, W / 2, 330), (W / 2, 236, W + 6, 330), (360, 380, 500, 590), (560, 430, 812, 484),
                  (-6, wy - 12, W + 6, wy + 2))                                   # the ceiling's edge, the wall's
    c.add(f'<rect x="560" y="470" width="250" height="12" fill="{BEAM}" stroke="{INK}" stroke-width="1.6"/>')
    for j in range(6):                                                                     # the card index
        c.add(f'<rect x="{580 + j * 36}" y="{428 - (j == 4) * 22}" width="28" height="40" fill="{P.CARD}" '
              f'stroke="{INK}" stroke-width="1.3"/>')
    c.add(f'<path d="M566,470 L572,436 H798 L804,470 Z" fill="{P.WOOD}" stroke="{INK}" stroke-width="1.6"/>')
    st.put(0.9, f'<g transform="rotate(-14 640 370)">{blank_card(620, 370, 1.7)}</g>' +
           motion(650, 390, 40, 1.3, way=-1), (600, 296, 720, 400), "card")
    parts = lathe(c, 590, floor, 1.75, running=True)                                       # the hero
    paving(c, -6, W + 6, floor, H + 4, 1.8, seed=4, tones=BOARDS)
    c.add(f'<rect x="-6" y="{floor - 6}" width="{W + 12}" height="10" fill="{darken(P.WOOD_DARK, 0.8)}" '
          f'stroke="{INK}" stroke-width="1.4"/>')
    prof = st.actor("professor", 150, 1090, "explain", "talk", tall=360)
    st.speaker(prof, width=74, left=8, air=CLEAR_MM)
    st.actor("caterpillar", 320, 1090, "think", "worry", flip=False, tall=300, group="caterpillar")
    st.actor("cat", 480, 1120, "point", "smile", flip=False, tall=320, group="cat")
    st.actor("agent", 752, 1110, "cheer", "smile", flip=True, tall=340, group="agent")
    lx, ly = parts["lamp"]
    st.actor("sparrow", lx, ly - 2, "stand", "smile", tall=120, group="sparrow")           # on the lathe's lamp
    drawn = st.render()
    drawn.holders, drawn.links, drawn.ports = st.holders, st.links, st.ports
    return drawn


ATTIC.stations.extend([
    Station("playbooks", _framed(playbooks_station), ("read", "tick")),
    Station("card", _framed(card_station), ("show", "tray")),
    Station("when", _framed(when_station), ("third", "notice")),
    Station("index", _framed(index_station), ("pick", "pass")),
    Station("write", _framed(write_station), ("write", "read")),
    Station("command", _framed(command_station), ("pull", "run")),
    Station("where", _framed(where_station), ("shelves", "put")),
    Station("check", _framed(check_station), ("make", "stop")),
    Station("foreign", _framed(foreign_station), ("parcel", "label")),
])
ATTIC.backdrop = backdrop
ATTIC.alternate = True                                     # never one moment on two pages in a row
ATTIC.finale = finale
OPENERS["workshop"] = opener
hide(ATTIC, "index", "pick")

"""The professor's courtyard: the world of the front pages and of the introduction.

One place behind every frame (this is the opening of the book: everything must look superb, so that the reader
reads on without stopping): the professor's cottage on a sunny summer morning. Its street side: the pavement, the
white picket fence with the gate hung on its gatepost, the green rural mailbox on its own post beside it and a
little free library on the other side; behind the fence the front garden, the brick path from the gate to the porch
and the cottage itself - clapboard walls on a stone plinth, a tiled roof with its eaves, gutter, downpipe and brick
chimney, windows with frames, sills, shutters and flower boxes, the door with its canopy, steps and lamp, a climbing
rose. Its yard side: the brick patio, the lawn, the cottage's other wall, the plank shed with its weathervane and
water butt, the apple tree with its swing, the clothesline with real washing on its pegs, the vegetable patch, and
along the back the same picket fence with the neighbours' houses beyond it. One row of the yard (`YARD`) stands behind
every yard frame, the camera moving along it from moment to moment, so the yard is the same place on every page.
Things are drawn in units of the professor's height (100), so everything stands in proportion to the cast.

The front pages are the world `front`; each page picks its moment from its text (`front_place`):

1. gate     the author page (street side): "post" - the professor at his mailbox, its door open and its flag up,
            takes out his letters, the cat brings his morning paper; "read" - the gate open, the professor reads a
            letter on the pavement, the agent holds the rest of the post;
2. print    the fresh version (yard): the printer on the garden workbench under its striped awning, a fresh copy of
            the book sliding out cover up, a stack of fresh copies, a wrapped ream on the shelf below - "print": the
            caterpillar checks the copies against her list, the cat looks one through; "bring": the agent carries an
            armful of copies to the professor, who holds one up;
3. fence    making the book better together (yard, at the back fence): "mend" - a gap in the pickets, the broken one
            on the grass, the agent holds a new picket in place, the caterpillar nails it, the sparrow brings a nail,
            the open toolbox (saw, square, tape, nails) and the paint tin on the paving; "paint" - the new picket in,
            the cat paints it with a brush from the tin;
4. tea      the thanks (yard, by the cottage): a garden table with its cloth, cups on saucers, biscuits, jam -
            "pour":
            the professor pours from the teapot held by its handle, the tea running into a cup, the cat holds out his
            cup; "sip": the professor sits on the bench with his cup, the agent brings the biscuits;
5. hand     the licence (street side): "shelve" - the cat puts a copy into the little free library, its glass door
            open, the caterpillar in the open gate waves the reader in; "give": the agent holds a copy out from it;
6. pack     the contents (yard): "pack" - real rucksacks open on the paving, the agent packs the book, the caterpillar
            ticks her list; "route" - the map spread on the bench, the professor shows the way, the cat holds the
            compass; "ready" - the rucksacks buckled, the mats rolled on top, the professor points the way.

The introduction lives in the same yard as the world `courtyard` (see its own part below). No words in the pictures.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten, mix
from . import characters, handheld, sets
from .footers import Strip, footer_conflicts
from .ink import INK, Canvas, n, rounded_rect_d
from .openers import IN_FRONT, W, Stage
from .world_fair import held, lane, zoom
from .world_camp import mug
from .world_harbour import fx, place
from .world_kit import SIZE, Pen, floppy, ledger
from .world_kitchen import _box
from .world_moon import checklist, height
from .world_sea import beside, sparrow_on
from .worlds import Station, world

FRONT = world("front", opener="")              # the front pages
COURTYARD = world("courtyard", opener="")      # the introduction

_at = sets._at

SUN = P.YELLOW
SKY_TOP = mix(P.CHAPTER_SKY, P.SKY, 0.45)
SKY_LOW = mix(P.SKY_LOW, P.YELLOW_PALE, 0.35)
BRICK = (mix(P.TERRACOTTA, P.WOOD_PALE, 0.25), mix(P.TERRACOTTA, P.ORANGE, 0.2))
LAWN = mix(P.GREEN, P.LEAF_DARK, 0.25)
LAWN_LIGHT = mix(P.GREEN, P.GRASS, 0.45)
PAINT = mix(P.YELLOW, P.WOOD_PALE, 0.35)               # the shed's planks, painted the cover's yellow
PICKET = P.WHITE
BOARD = mix(P.CREAM, P.YELLOW_PALE, 0.45)              # the cottage's clapboard
TRIM = P.WHITE
TILE = mix(P.TERRACOTTA, P.RED, 0.12)                  # roof tiles
TILE_DARK = darken(TILE, 0.7)
SHUTTER = mix(P.CHAPTER_SKY, P.BLUE, 0.55)             # shutters and the front door, the pages' sky blue
STONE_ = mix(P.STONE, P.BEIGE, 0.35)
MAILBOX = mix(P.GREEN, P.PINE, 0.55)
PAPER_RAW = mix(P.WOOD_PALE, P.CARD, 0.35)             # a new, unpainted picket
SLAB = mix(P.STONE, P.PAPER, 0.35)                     # the pavement's slabs


def cover_art(c: Canvas, x: float, y: float, w: float, h: float, sw: float = 0.5) -> None:
    """The handbook's cover, flat, its top left corner at (x, y): the cover's yellow, the pink band at its top, the
    cream plate in the middle with the title as two dark lines - as the reader saw it on page one."""
    c.shape(rounded_rect_d(x, y, w, h, min(w, h) * 0.06), SUN, sw=sw, light=None)
    c.add(f'<rect x="{n(x + sw / 2)}" y="{n(y + sw / 2)}" width="{n(w - sw)}" height="{n(h * 0.17)}" '
          f'fill="{P.PINK}"/>')
    c.add(f'<rect x="{n(x + w * 0.16)}" y="{n(y + h * 0.3)}" width="{n(w * 0.68)}" height="{n(h * 0.3)}" '
          f'rx="{n(w * 0.04)}" fill="{P.PAPER}" stroke="{INK}" stroke-width="{n(sw * 0.7)}"/>')
    c.line(f"M{n(x + w * 0.25)},{n(y + h * 0.4)} h{n(w * 0.5)} M{n(x + w * 0.33)},{n(y + h * 0.5)} h{n(w * 0.34)}",
           max(0.3, h * 0.05), INK)


# ============================================================================ the yard's buildings
def tiles(c: Canvas, outline: str, x0: float, x1: float, top: float, bottom: float, row: float, slope: float = 0.0,
          fill: str = TILE) -> None:
    """A tiled roof face: `outline` filled with the tiles' colour, then course after course of tiles from the eaves
    (`bottom`) up to `top` - each course's lower edge scalloped, its joints staggered - clipped to the outline.
    `slope`: how far each side of the face leans in per unit of height (a hipped face)."""
    clip = c.shape(outline, fill, sw=0, light=None, clip=True)
    edges, joints, shade = [], [], []
    y, q = bottom, 0
    while y > top - row:
        inset = (bottom - y) * slope
        a, b = x0 + inset - row, x1 - inset + row
        w = row * 1.25
        x = a - (q % 2) * w / 2
        d = [f"M{n(x)},{n(y)}"]
        while x < b:
            d.append(f"q{n(w / 2)},{n(row * 0.42)} {n(w)},0")
            joints.append(f"M{n(x + w)},{n(y)} v{n(-row * 0.8)}")
            x += w
        edges.append(" ".join(d))
        shade.append(f"M{n(a)},{n(y - row * 0.18)} H{n(b)}")
        y -= row
        q += 1
    c.add(f'<g clip-path="url(#{clip})">')
    c.line(" ".join(shade), row * 0.32, darken(fill, 0.86))
    c.line(" ".join(joints), max(0.4, row * 0.07), TILE_DARK, 0.75)
    c.line(" ".join(edges), max(0.5, row * 0.09), TILE_DARK)
    c.add("</g>")
    c.path(outline, "none", max(0.8, row * 0.13))


def window(c: Canvas, x: float, sill: float, w: float, h: float, shutters: bool = True, box: bool = True,
           curtain: str = P.PINK) -> None:
    """A cottage window, its sill's middle at (x, sill): the white frame with its glazing bars, the sky in the
    panes, curtains tied back inside, a stone sill, louvred shutters folded back on either side and a flower box
    of geraniums under it."""
    left, top = x - w / 2, sill - h
    if shutters:
        for sx in (left - w * 0.42 - 2, x + w / 2 + 2):
            c.shape(rounded_rect_d(sx, top + 1, w * 0.42, h - 2, 1), SHUTTER, sw=1.1, light=None)
            c.line(" ".join(f"M{n(sx + 2)},{n(top + 5 + i * (h - 10) / 9)} h{n(w * 0.42 - 4)}" for i in range(10)),
                   0.8, darken(SHUTTER, 0.75))
    c.shape(rounded_rect_d(left, top, w, h, 1.5), TRIM, sw=1.4, light=None)                     # the frame
    c.add(f'<rect x="{n(left + 4)}" y="{n(top + 4)}" width="{n(w - 8)}" height="{n(h - 8)}" '
          f'fill="{mix(P.SKY, P.LENS, 0.45)}" stroke="{INK}" stroke-width=".8"/>')               # the glass
    c.add(f'<path d="M{n(left + 4)},{n(top + 4)} Q{n(left + w * 0.3)},{n(top + h * 0.35)} {n(left + 4)},'
          f'{n(sill - 8)} Z M{n(left + w - 4)},{n(top + 4)} Q{n(left + w * 0.7)},{n(top + h * 0.35)} '
          f'{n(left + w - 4)},{n(sill - 8)} Z" fill="{curtain}" stroke="{INK}" stroke-width=".6"/>')   # curtains
    c.add(f'<path d="M{n(left + w * 0.62)},{n(top + 7)} l{n(-w * 0.22)},{n(h * 0.3)} M{n(left + w * 0.78)},'
          f'{n(top + 7)} l{n(-w * 0.22)},{n(h * 0.3)}" stroke="{P.WHITE}" stroke-width="1.6" '
          f'stroke-opacity=".7"/>')                                                               # the gleam
    c.line(f"M{n(x)},{n(top + 4)} V{n(sill - 4)} M{n(left + 4)},{n(top + h * 0.45)} H{n(left + w - 4)}", 2.2,
           TRIM)
    c.line(f"M{n(x)},{n(top + 4)} V{n(sill - 4)} M{n(left + 4)},{n(top + h * 0.45)} H{n(left + w - 4)}", 0.5,
           darken(TRIM, 0.75))
    c.shape(rounded_rect_d(left - 4, sill - 1, w + 8, 4, 1), STONE_, sw=1, light=None)           # the sill
    if box:
        c.shape(rounded_rect_d(left + 2, sill + 3, w - 4, 7, 1), P.TERRACOTTA, sw=1, light=None)  # flower box
        rnd = random.Random(int(x * 7 + sill))
        leaves, blooms = [], []
        for i in range(int(w / 5)):
            fx_ = left + 5 + i * 5 + rnd.uniform(-1, 1)
            leaves.append(f"M{n(fx_ - 3)},{n(sill + 3)} a3,2.4 0 1 1 6,0 Z")
            if i % 2 == 0:
                blooms.append(f"M{n(fx_ + 2.2)},{n(sill - 1)} a2.2,2.2 0 1 1 -4.4,0 a2.2,2.2 0 1 1 4.4,0 Z")
        c.add(f'<path d="{" ".join(leaves)}" fill="{P.LEAF}" stroke="{INK}" stroke-width=".5"/>')
        c.add(f'<path d="{" ".join(blooms)}" fill="{P.RED}" stroke="{INK}" stroke-width=".5"/>')


def door(c: Canvas, x: float, foot: float, w: float = 54, h: float = 128, lamp: int = 1) -> None:
    """The cottage's front door, its foot's middle at (x, foot) on the top step: the white frame, the blue door in
    four panels with its knob, letter plate and fanlight, two stone steps under it, a little gabled canopy on two
    brackets over it and a lantern on the wall at its side (`lamp`: 1 right, -1 left)."""
    left, top = x - w / 2, foot - h
    for i, (sw_, sh_) in enumerate(((w + 26, 6), (w + 14, 6))):                                  # the steps
        c.shape(rounded_rect_d(x - sw_ / 2, foot + 12 - (i + 1) * 6, sw_, sh_, 1), STONE_, sw=1.1, light=None)
    c.shape(rounded_rect_d(left - 5, top - 5, w + 10, h + 5, 1), TRIM, sw=1.4, light=None)      # the frame
    c.shape(rounded_rect_d(left, top + 14, w, h - 14, 1), SHUTTER, sw=1.3, light=(-1, -1))
    c.add(f'<path d="M{n(left)},{n(top + 12)} A{n(w / 2)},{n(w / 3)} 0 0 1 {n(left + w)},{n(top + 12)} Z" '
          f'fill="{mix(P.SKY, P.LENS, 0.4)}" stroke="{INK}" stroke-width="1"/>')                   # the fanlight
    c.line(" ".join(f"M{n(x)},{n(top + 12)} l{n(w / 2 * math.cos(math.radians(a)))},"
                    f"{n(-w / 3 * math.sin(math.radians(a)))}" for a in (30, 90, 150)), 0.8, TRIM)
    for px, py, pw, ph in ((left + 6, top + 20, w / 2 - 9, (h - 30) * 0.45), (x + 3, top + 20, w / 2 - 9,
                                                                               (h - 30) * 0.45),
                           (left + 6, top + 26 + (h - 30) * 0.45, w / 2 - 9, (h - 30) * 0.5),
                           (x + 3, top + 26 + (h - 30) * 0.45, w / 2 - 9, (h - 30) * 0.5)):
        c.add(f'<rect x="{n(px)}" y="{n(py)}" width="{n(pw)}" height="{n(ph)}" rx="1" fill="none" '
              f'stroke="{darken(SHUTTER, 0.7)}" stroke-width="1.2"/>')                           # the panels
    c.add(f'<circle cx="{n(left + w - 8)}" cy="{n(top + h * 0.58)}" r="2.6" fill="{P.GOLD}" stroke="{INK}" '
          f'stroke-width=".7"/>')                                                                 # the knob
    c.shape(rounded_rect_d(x - 7, top + h * 0.5, 14, 4, 1), P.GOLD, sw=0.7, light=None)        # letter plate
    c.shape(f"M{n(left - 14)},{n(top - 6)} L{n(x)},{n(top - 26)} L{n(left + w + 14)},{n(top - 6)} Z", TILE,
            sw=1.3, light=None)                                                                   # the canopy
    c.line(f"M{n(left - 12)},{n(top - 8)} L{n(x)},{n(top - 22)} L{n(left + w + 12)},{n(top - 8)}", 2.2, TRIM)
    for bx, s_ in ((left - 6, -1), (left + w + 6, 1)):                                           # its brackets
        c.line(f"M{n(bx)},{n(top - 6)} v14 M{n(bx)},{n(top + 6)} l{n(s_ * -8)},{n(-12)}", 2, TRIM)
    lx = x + lamp * (w / 2 + 16)                                                                 # the lantern
    c.line(f"M{n(lx - lamp * 6)},{n(top + 34)} h{n(lamp * 6)}", 1.4, INK)
    c.shape(f"M{n(lx - 5)},{n(top + 26)} h10 l-1.5,14 h-7 Z", mix(P.YELLOW_PALE, P.SUN, 0.4), sw=1, light=None)
    c.shape(f"M{n(lx - 7)},{n(top + 26)} L{n(lx)},{n(top + 20)} L{n(lx + 7)},{n(top + 26)} Z", P.CHARCOAL, sw=0.8,
            light=None)
    c.line(f"M{n(lx)},{n(top + 27)} v12", 0.6, P.CHARCOAL)


def rose(c: Canvas, x: float, foot: float, h: float, seed: int) -> None:
    """A climbing rose up a wooden trellis on the wall, its foot at (x, foot), `h` tall: the lattice, the stems
    winding up it, leaves in pairs and red roses open among them."""
    w = 26
    c.line(" ".join([f"M{n(x - w / 2)},{n(foot)} V{n(foot - h)} M{n(x + w / 2)},{n(foot)} V{n(foot - h)}"] +
                    [f"M{n(x - w / 2)},{n(foot - q)} L{n(x + w / 2)},{n(foot - q - w)} M{n(x + w / 2)},{n(foot - q)} "
                     f"L{n(x - w / 2)},{n(foot - q - w)}" for q in range(0, int(h - w) + 1, int(w))]),
           1.2, P.WOOD)
    rnd = random.Random(seed)
    stem, leaves, blooms = [], [], []
    for side in (-1, 1):
        d, y = [f"M{n(x)},{n(foot)}"], foot
        while y > foot - h + 8:
            y2 = y - rnd.uniform(14, 20)
            d.append(f"Q{n(x + side * w * 0.6)},{n((y + y2) / 2)} {n(x + side * rnd.uniform(-4, 4))},{n(y2)}")
            lx = x + side * rnd.uniform(3, 11)
            leaves.append(f"M{n(lx)},{n(y2 + 4)} q4,-5 8,-1 q-4,4 -8,1 Z M{n(lx)},{n(y2 + 4)} q-4,-5 -8,-1 "
                          f"q4,4 8,1 Z")
            if rnd.random() < 0.65:
                bx, by = x + side * rnd.uniform(4, 13), y2 + rnd.uniform(-3, 3)
                blooms.append((bx, by, rnd.uniform(3.2, 4.4)))
            y = y2
        stem.append(" ".join(d))
    c.line(" ".join(stem), 1.4, P.LEAF_DARK)
    c.add(f'<path d="{" ".join(leaves)}" fill="{P.LEAF}" stroke="{INK}" stroke-width=".5"/>')
    for bx, by, r in blooms:
        c.add(f'<circle cx="{n(bx)}" cy="{n(by)}" r="{n(r)}" fill="{P.RED}" stroke="{INK}" stroke-width=".6"/>'
              f'<path d="M{n(bx - r * 0.5)},{n(by)} q{n(r * 0.5)},{n(-r * 0.7)} {n(r)},0 q{n(-r * 0.5)},'
              f'{n(r * 0.5)} {n(-r * 0.3)},{n(r * 0.3)}" fill="none" stroke="{darken(P.RED, 0.7)}" '
              f'stroke-width=".6"/>')


COTTAGE_W = 330          # the cottage, wall to wall
COTTAGE_WALL = 172       # its walls, plinth to eaves
COTTAGE_H = 300          # to the top of its chimney pots


def cottage(c: Canvas, x: float, foot: float, k: float, door_at: float = -86, seed: int = 0,
            garden: bool = True) -> None:
    """The professor's cottage at (x, foot), 330 wide, 172 to the eaves and 300 to the chimney's pots, in units of
    the professor's height (100): a stone plinth; walls of cream clapboard, each board's lap shading the next, white
    corner boards; the hipped roof of terracotta tiles in staggered courses over deep eaves with the half-round
    gutter and its downpipe to a shoe; the brick chimney with its cap and two pots; the front door with its canopy,
    steps and lantern at `door_at`; windows with shutters and flower boxes; a climbing rose on its trellis by the
    door; a soft shadow under the eaves; flowers along its foot (`garden`)."""
    d = Canvas()
    hw, wall = COTTAGE_W / 2, COTTAGE_WALL
    d.add(f'<ellipse cx="0" cy="1" rx="{hw + 10}" ry="4" fill="{INK}" fill-opacity=".12"/>')
    d.shape(rounded_rect_d(-hw, -wall, 2 * hw, wall, 0), BOARD, sw=1.8, light=None)             # the walls
    d.add(f'<path d="{" ".join(f"M{-hw},{n(-wall + 9 + q * 9.4)} H{hw}" for q in range(17))}" fill="none" '
          f'stroke="{darken(BOARD, 0.84)}" stroke-width="2.4"/>')                                 # the laps' shade
    d.add(f'<path d="{" ".join(f"M{-hw},{n(-wall + 7.6 + q * 9.4)} H{hw}" for q in range(17))}" fill="none" '
          f'stroke="{darken(BOARD, 0.68)}" stroke-width=".7"/>')                                  # their edges
    d.add(f'<rect x="{-hw}" y="{-wall}" width="{2 * hw}" height="10" fill="{INK}" fill-opacity=".14"/>')
    for cx in (-hw, hw - 9):                                                                     # corner boards
        d.shape(rounded_rect_d(cx, -wall, 9, wall - 12, 0), TRIM, sw=1.2, light=None)
    d.shape(rounded_rect_d(-hw - 3, -14, 2 * hw + 6, 14, 1), STONE_, sw=1.4, light=None)        # the plinth
    rnd = random.Random(seed + 5)
    d.line(" ".join(f"M{n(-hw + q * 22 + rnd.uniform(-3, 3))},-14 v14" for q in range(1, 15)) +
           " M" + f"{-hw},-7 H{hw}", 0.7, darken(STONE_, 0.7))
    door(d, door_at, -12, lamp=1)
    rose(d, door_at - 48, -14, 120, seed)
    for wx in (door_at + 100, door_at + 196):
        if abs(wx) < hw - 34:
            window(d, wx, -62, 46, 66, curtain=P.PINK if wx < 60 else P.YELLOW_PALE)
    eave = -wall
    d.shape(f"M{-hw - 18},{eave + 2} L{-hw + 40},{eave - 96} H{hw - 40} L{hw + 18},{eave + 2} Z", TILE, sw=0,
            light=None)
    cx_, ctop = 80, eave - 128                                                                   # the chimney
    d.shape(f"M{cx_ - 14},{eave - 60} V{ctop} H{cx_ + 14} V{eave - 82} Z", mix(BRICK[0], P.RUBY, 0.25), sw=1.4,
            light=None)
    d.line(" ".join(f"M{cx_ - 14},{n(ctop + 7 + q * 7)} H{cx_ + 14}" for q in range(6)), 0.6,
           darken(BRICK[0], 0.7))
    tiles(d, f"M{-hw - 18},{eave + 2} L{-hw + 40},{eave - 96} H{hw - 40} L{hw + 18},{eave + 2} Z", -hw - 18,
          hw + 18, eave - 96, eave + 2, 13, slope=58 / 98)
    d.shape(rounded_rect_d(cx_ - 17, ctop - 6, 34, 7, 1), STONE_, sw=1.2, light=None)          # its cap
    for px in (cx_ - 8, cx_ + 8):
        d.shape(f"M{px - 4},{ctop - 6} l1,-11 h6 l1,11 Z", P.TERRACOTTA, sw=1, light=None)     # the pots
    d.line(f"M{-hw + 40},{eave - 96} H{hw - 40}", 3.4, TILE_DARK)                                 # the ridge
    d.shape(rounded_rect_d(-hw - 16, eave - 2, 2 * hw + 32, 6, 3), P.METAL_LIGHT, sw=1.2, light=None)  # gutter
    d.shape(f"M{hw + 4},{eave + 4} V-10 q0,6 7,8 h3 v-5 h-3 q-2,-1 -2,-4 V{eave + 4} Z", P.METAL_LIGHT, sw=1.1,
            light=None)                                                                           # the downpipe
    d.line(" ".join(f"M{hw + 2},{n(-wall + 30 + q * 40)} h10" for q in range(4)), 1.4, P.METAL_DARK)
    if garden:
        flowers(d, -hw + 12, hw - 14, 1, 1, seed + 1, avoid=(door_at - 36, door_at + 36))
    c.add(_at(d, x, foot, k))


def house(c: Canvas, x: float, foot: float, k: float) -> None:
    """A stretch of the professor's house, 180 wide and 140 to the eaves (`roof` puts its roof on): the clapboard
    wall on its plinth, a window with shutters and a flower box, a climbing rose on its trellis."""
    d = Canvas()
    d.shape(rounded_rect_d(-90, -140, 180, 140, 0), BOARD, sw=1.8, light=None)
    d.add(f'<path d="{" ".join(f"M-90,{n(-131 + q * 9.4)} H90" for q in range(14))}" fill="none" '
          f'stroke="{darken(BOARD, 0.84)}" stroke-width="2.4"/>')
    d.shape(rounded_rect_d(-92, -12, 184, 12, 1), STONE_, sw=1.4, light=None)
    window(d, -10, -52, 44, 62)
    rose(d, 58, -12, 116, 3)
    c.add(_at(d, x, foot, k))


def roof(c: Canvas, x: float, foot: float, k: float) -> None:
    """The roof over `house` standing at (x, foot): tiles in staggered courses over the eaves and the gutter, the
    brick chimney with its cap and pots."""
    d = Canvas()
    outline = "M-106,-138 L-74,-190 H74 L106,-138 Z"
    d.shape("M38,-170 V-214 H62 V-180 Z", mix(BRICK[0], P.RUBY, 0.25), sw=1.4, light=None)
    tiles(d, outline, -106, 106, -190, -138, 10, slope=32 / 52)
    d.shape(rounded_rect_d(35, -220, 30, 6, 1), STONE_, sw=1.2, light=None)
    for px in (43, 57):
        d.shape(f"M{px - 3},-220 l1,-9 h4 l1,9 Z", P.TERRACOTTA, sw=0.9, light=None)
    d.shape(rounded_rect_d(-104, -142, 208, 5, 2.5), P.METAL_LIGHT, sw=1.1, light=None)
    c.add(_at(d, x, foot, k))


def shed(c: Canvas, x: float, foot: float, k: float) -> None:
    """The plank shed at (x, foot), 150 wide and 200 to its weathervane: walls of yellow-painted boards and battens,
    a shingled roof with its bargeboard, the ledged door with strap hinges and a latch, a four-pane window with its
    flower box, the weathervane - a cockerel over the four arms - on the ridge, and the water butt on its stand
    under the downpipe."""
    d = Canvas()
    d.add(f'<ellipse cx="0" cy="1" rx="84" ry="3.5" fill="{INK}" fill-opacity=".12"/>')
    d.shape(rounded_rect_d(-62, -116, 124, 116, 0), PAINT, sw=1.8, light=None)
    d.line(" ".join(f"M{q},-116 V0" for q in range(-50, 62, 12)), 2.2, darken(PAINT, 0.82))    # the battens
    rnd = random.Random(int(x))
    d.line(" ".join(f"M{q + rnd.uniform(2, 8)},{n(-rnd.uniform(20, 100))} q2,-6 0,-12" for q in range(-56, 56, 12)),
           0.6, darken(PAINT, 0.7))                                                              # the grain
    tiles(d, "M-76,-112 L-44,-150 H44 L76,-112 Z", -76, 76, -150, -112, 7.5, slope=32 / 38,
          fill=mix(P.WOOD_DARK, P.TERRACOTTA, 0.3))
    d.line("M-44,-150 H44", 2.6, P.WOOD_DARK)
    d.line("M0,-150 V-186 M-10,-170 H10 M0,-180 V-160", 1.6, INK)                                 # the weathervane
    d.shape("M-6,-186 Q-12,-194 -6,-200 Q2,-198 6,-192 L12,-196 L10,-186 Z", INK, sw=0.8, light=None)
    d.shape(rounded_rect_d(4, -92, 40, 92, 1), mix(P.GREEN, P.LEAF_DARK, 0.45), sw=1.4, light=(-1, -1))  # door
    d.line("M8,-86 V-4 M16,-86 V-4 M24,-86 V-4 M32,-86 V-4", 0.7, darken(P.GREEN, 0.6))
    d.line("M6,-80 H42 M6,-14 H42 M6,-16 L42,-78", 3, darken(P.GREEN, 0.75))                     # ledges, brace
    d.line("M4,-78 h18 M4,-16 h18", 2.2, P.CHARCOAL)                                             # strap hinges
    d.shape(rounded_rect_d(36, -50, 6, 4, 1), P.CHARCOAL, sw=0.6, light=None)                   # the latch
    d.shape(rounded_rect_d(-50, -82, 40, 32, 1.5), TRIM, sw=1.3, light=None)                    # the window
    d.add(f'<rect x="-47" y="-79" width="34" height="26" fill="{mix(P.SKY, P.LENS, 0.45)}" stroke="{INK}" '
          f'stroke-width=".7"/>')
    d.line("M-30,-79 V-53 M-47,-66 H-13", 1.8, TRIM)
    d.shape(rounded_rect_d(-52, -50, 44, 6, 1), P.TERRACOTTA, sw=1, light=None)
    for q in range(5):
        d.add(f'<circle cx="{-47 + q * 8.5}" cy="-51" r="3.2" fill="{(P.RED, P.PINK, P.YELLOW, P.RED, P.WHITE)[q]}" '
              f'stroke="{INK}" stroke-width=".6"/>')
    d.shape("M-62,-112 H-70 V-30 h4 v-6 h-4", P.METAL_LIGHT, sw=1, light=None)                  # its downpipe
    d.shape("M-86,0 V-4 H-56 V0 Z", P.WOOD_DARK, sw=1, light=None)                               # the butt's stand
    d.shape("M-84,-4 Q-86,-20 -84,-34 H-58 Q-56,-20 -58,-4 Z", P.WOOD, sw=1.3, light=(-1, -1))  # the water butt
    d.line("M-85,-10 H-57 M-85,-28 H-57", 1.8, P.METAL_DARK)
    d.add(f'<ellipse cx="-71" cy="-34" rx="13" ry="2.4" fill="{P.WATER}" stroke="{INK}" stroke-width=".8"/>')
    c.add(_at(d, x, foot, k))


def small_window(d: Canvas, x: float, sill: float, w: float = 18, h: float = 22, shutters: str | None = None) -> None:
    """A neighbour's window, its sill's middle at (x, sill): the white frame, four panes of sky, a stone sill, and
    (`shutters`) a shutter either side."""
    if shutters:
        for sx in (x - w / 2 - 6, x + w / 2 + 1):
            d.shape(rounded_rect_d(sx, sill - h, 5, h, 0.6), shutters, sw=0.8, light=None)
    d.shape(rounded_rect_d(x - w / 2, sill - h, w, h, 1), TRIM, sw=1, light=None)
    d.add(f'<rect x="{n(x - w / 2 + 2.4)}" y="{n(sill - h + 2.4)}" width="{n(w - 4.8)}" height="{n(h - 4.8)}" '
          f'fill="{mix(P.SKY, P.LENS, 0.4)}" stroke="{INK}" stroke-width=".5"/>')
    d.line(f"M{n(x)},{n(sill - h + 2.4)} V{n(sill - 2.4)} M{n(x - w / 2 + 2.4)},{n(sill - h / 2)} "
           f"H{n(x + w / 2 - 2.4)}", 1.1, TRIM)
    d.shape(rounded_rect_d(x - w / 2 - 2, sill - 0.5, w + 4, 2.6, 0.6), STONE_, sw=0.7, light=None)


def small_door(d: Canvas, x: float, foot: float, colour: str, porch: str) -> None:
    """A neighbour's front door at (x, foot): the door in its white frame with two panels and a knob, a stone step
    under it and a little gabled porch roof over it."""
    d.shape(rounded_rect_d(x - 13, foot - 2, 26, 4, 0.8), STONE_, sw=0.8, light=None)                   # the step
    d.shape(rounded_rect_d(x - 10, foot - 42, 20, 40, 0.8), TRIM, sw=1, light=None)
    d.shape(rounded_rect_d(x - 7.5, foot - 39.5, 15, 37.5, 0.6), colour, sw=0.8, light=None)
    d.add(f'<rect x="{n(x - 5)}" y="{n(foot - 36)}" width="10" height="13" rx=".8" fill="none" '
          f'stroke="{darken(colour, 0.7)}" stroke-width=".8"/><rect x="{n(x - 5)}" y="{n(foot - 20)}" width="10" '
          f'height="14" rx=".8" fill="none" stroke="{darken(colour, 0.7)}" stroke-width=".8"/>'
          f'<circle cx="{n(x + 4.6)}" cy="{n(foot - 20)}" r="1.2" fill="{P.GOLD}"/>')
    d.shape(f"M{n(x - 15)},{n(foot - 43)} L{n(x)},{n(foot - 53)} L{n(x + 15)},{n(foot - 43)} Z", porch, sw=1,
            light=None)
    d.line(f"M{n(x - 12)},{n(foot - 43)} v8 M{n(x + 12)},{n(foot - 43)} v8", 1.2, TRIM)


def far_house(c: Canvas, x: float, foot: float, k: float, kind: int) -> None:
    """A neighbour's house beyond the fence at (x, foot): a gabled cottage 120 wide with its gable to the street
    (`kind` 0-3) or a long house 160 wide under a hipped roof (4-5) - painted walls on a plinth, the roof of tiles or
    slates in courses over deep eaves, a brick chimney, two or three framed windows with sills (shutters on some), the
    front door with its step and little porch, a round window in a gable, a bush at the corner - each house in its
    own colours."""
    walls = (mix(P.PINK_PALE, P.CARD, 0.4), mix(P.SKY, P.CARD, 0.35), mix(P.YELLOW_PALE, P.CARD, 0.3),
             mix(P.GRASS, P.CARD, 0.45), mix(P.WOOD_PALE, P.CARD, 0.5),
             mix(P.CHAPTER_PERIWINKLE, P.CARD, 0.6))[kind % 6]
    roof_ = (TILE, mix(P.METAL_DARK, P.BLUE, 0.25), mix(TILE, P.WOOD_DARK, 0.3), mix(P.TERRACOTTA, P.PINK, 0.3),
             mix(P.METAL_DARK, P.CHARCOAL, 0.3), mix(TILE, P.ORANGE, 0.25))[(kind * 5 + 1) % 6]
    accent = (SHUTTER, mix(P.GREEN, P.PINE, 0.4), P.RED, mix(P.VIOLET, P.BLUE, 0.4), P.TEAL, P.WOOD)[(kind * 3) % 6]
    d = Canvas()
    rnd = random.Random(kind * 31 + int(x))
    d.add(f'<ellipse cx="0" cy="1" rx="{86 if kind % 6 >= 4 else 66}" ry="3" fill="{INK}" fill-opacity=".1"/>')
    if kind % 6 >= 4:                                                # a long house, its hipped roof to the street
        d.shape(rounded_rect_d(-70, -64, 140, 64, 0), walls, sw=1.5, light=None)
        d.shape(rounded_rect_d(-72, -8, 144, 8, 0.6), STONE_, sw=1, light=None)
        d.shape("M30,-86 V-110 H44 V-80 Z", mix(BRICK[0], P.RUBY, 0.25), sw=1.2, light=None)
        d.shape(rounded_rect_d(28, -114, 18, 5, 1), STONE_, sw=0.9, light=None)
        outline = "M-82,-60 L-46,-102 H46 L82,-60 Z"
        d.shape(outline, roof_, sw=1.4, light=None)
        d.line(" ".join(f"M{n(-82 + q * 5.14)},{n(-60 - q * 6)} H{n(82 - q * 5.14)}" for q in range(1, 7)), 0.8,
               darken(roof_, 0.68))                                  # its courses of tiles or slates
        d.line("M-46,-102 H46", 2.4, darken(roof_, 0.65))
        small_door(d, 16, -8, accent, roof_)
        for wx in (-50, -18, 48):
            small_window(d, wx, -26, shutters=accent if kind % 2 else None)
        roof_w = 82
    else:                                                            # a gabled cottage, its gable to the street
        d.shape("M-52,0 V-70 L0,-112 L52,-70 V0 Z", walls, sw=1.5, light=None)
        d.shape(rounded_rect_d(-54, -8, 108, 8, 0.6), STONE_, sw=1, light=None)
        d.shape("M22,-96 V-124 H36 V-84 Z", mix(BRICK[0], P.RUBY, 0.25), sw=1.2, light=None)
        d.shape(rounded_rect_d(20, -128, 18, 5, 1), STONE_, sw=0.9, light=None)
        d.shape("M-64,-63 L0,-120 L64,-63 L55,-56 L0,-104 L-55,-56 Z", roof_, sw=1.4, light=None)  # the eaves
        d.line(" ".join(f"M{n(-4 - q * 6.4)},{n(-114 + q * 5.6)} l{n(-8)},{n(7)} M{n(4 + q * 6.4)},"
                        f"{n(-114 + q * 5.6)} l{n(8)},{n(7)}" for q in range(9)), 0.8, darken(roof_, 0.68))
        d.add(f'<circle cx="0" cy="-82" r="7" fill="{mix(P.SKY, P.LENS, 0.4)}" stroke="{INK}" stroke-width="1.1"/>'
              f'<path d="M-7,-82 H7 M0,-89 V-75" stroke="{TRIM}" stroke-width="1.2"/>')
        small_door(d, -24 if kind % 2 else 24, -8, accent, roof_)
        small_window(d, 24 if kind % 2 else -24, -30, shutters=accent if kind % 3 == 0 else None)
        roof_w = 64
    for bx in (-roof_w + 8, roof_w - 6):                             # a bush at each corner
        if rnd.random() < 0.7:
            d.add(f'<path d="M{bx - 10},0 a10,9 0 0 1 20,0 Z" fill="{mix(P.LEAF, P.LEAF_DARK, 0.3)}" '
                  f'stroke="{INK}" stroke-width="1"/>')
            if rnd.random() < 0.5:
                d.add(f'<circle cx="{bx - 3}" cy="-5" r="1.6" fill="{P.PINK}"/><circle cx="{bx + 4}" cy="-6" '
                      f'r="1.6" fill="{P.PINK}"/>')
    c.add(_at(d, x, foot, k))


def neighbours(c: Canvas, foot: float, k: float, seed: int, view: float = 0.0) -> None:
    """The neighbours' houses beyond the back fence, standing on `foot` at about `k`: each its own size, shape,
    colours and distance, with trees between and behind them - apple trees, birches, pines, round shrubs - some in
    front of a house, partly hiding it. The furthest are drawn first."""
    rnd = random.Random(seed * 13 + 5)
    x = -60 * k - (view % 120) * k
    items = []
    while x < W + 80 * k:
        kind = rnd.randrange(6)
        sc = k * rnd.uniform(0.72, 1.0)
        back = rnd.uniform(0, 16) * k
        w = (180 if kind >= 4 else 150) * sc
        items.append((back, "house", x + w / 2, sc, kind))
        for _ in range(rnd.choice((1, 1, 2, 2))):                    # trees between and behind
            tree = rnd.choice(("apple", "birch", "pine", "shrub", "birch", "pine"))
            items.append((back + rnd.uniform(-10, 22) * k, tree, x + w * rnd.uniform(-0.15, 1.15),
                          sc * rnd.uniform(0.7, 1.0), 0))
        x += max(w + rnd.uniform(10, 40) * k, W / 5.2)            # never a crowd of tiny houses
    for back, what, cx, sc, kind in sorted(items, key=lambda t: -t[0]):
        y = foot - back
        if what == "house":
            far_house(c, cx, y, sc, kind + seed)
        elif what == "apple":
            apple_tree(c, cx, y, sc * 0.85, lite=True)
        elif what == "birch":
            birch(c, cx, y, sc * 0.9, lite=True)
        elif what == "pine":
            pine(c, cx, y, sc * 0.95)
        else:
            shrub(c, cx, y, sc * 1.1, lite=True)


def blob_crown(d: Canvas, cx: float, cy: float, rx: float, ry: float, base: str, rnd: random.Random,
               bumps: int = 14, sw: float = 1.6, lite: bool = False) -> str:
    """A tree's crown as one solid, irregular silhouette: a core ellipse ringed with leafy bumps, outlined once
    round the outside, with the underside in shade and the top lit, and clusters of leaves inside. Returns the id of
    a clip of the crown, for what must stay inside it."""
    parts = [f"M{n(cx - rx * 0.9)},{n(cy)} a{n(rx * 0.9)},{n(ry * 0.9)} 0 1 1 {n(rx * 1.8)},0 "
             f"a{n(rx * 0.9)},{n(ry * 0.9)} 0 1 1 {n(-rx * 1.8)},0 Z"]
    for q in range(bumps):
        a = 2 * math.pi * q / bumps + rnd.uniform(-0.12, 0.12)
        r = min(rx, ry) * rnd.uniform(0.34, 0.46)
        bx, by = cx + (rx - r * 0.7) * math.cos(a), cy + (ry - r * 0.7) * math.sin(a)
        parts.append(f"M{n(bx - r)},{n(by)} a{n(r)},{n(r)} 0 1 1 {n(2 * r)},0 a{n(r)},{n(r)} 0 1 1 {n(-2 * r)},0 Z")
    crown = " ".join(parts)
    d.add(f'<path d="{crown}" fill="{INK}" stroke="{INK}" stroke-width="{n(sw * 2)}" stroke-linejoin="round"/>')
    clip = d.shape(crown, base, sw=0, light=None, clip=True)
    d.add(f'<g clip-path="url(#{clip})">')
    d.add(f'<ellipse cx="{n(cx)}" cy="{n(cy + ry * 0.95)}" rx="{n(rx * 1.2)}" ry="{n(ry * 0.6)}" '
          f'fill="{darken(base, 0.8)}"/>')                                       # the underside in shade
    if lite:                                                    # far off: the shade alone, the leaves not seen
        d.add("</g>")
        return clip
    lit = []
    for _ in range(5):
        a = rnd.uniform(math.pi * 1.1, math.pi * 1.9)
        r = min(rx, ry) * rnd.uniform(0.28, 0.4)
        bx, by = cx + rx * 0.45 * math.cos(a), cy + ry * 0.5 * math.sin(a)
        lit.append(f"M{n(bx - r)},{n(by)} a{n(r)},{n(r)} 0 1 1 {n(2 * r)},0 a{n(r)},{n(r)} 0 1 1 {n(-2 * r)},0 Z")
    d.add(f'<path d="{" ".join(lit)}" fill="{lighten(base, 0.14)}"/>')            # the top in the sun
    leaves = []
    for _ in range(int(rx * ry / 120)):
        lx, ly = cx + rnd.uniform(-0.8, 0.8) * rx, cy + rnd.uniform(-0.75, 0.75) * ry
        leaves.append(f"M{n(lx - 3)},{n(ly)} q3,2.6 6,0")
    d.line(" ".join(leaves), 0.9, darken(base, 0.62), 0.75)
    d.add("</g>")
    return clip


def apple_tree(c: Canvas, x: float, foot: float, k: float, swing: bool = False, lite: bool = False) -> None:
    """An apple tree at (x, foot), 150 tall and about 120 across: a straight, sturdy trunk flaring into its roots,
    its bark, three boughs reaching up into one solid crown - leaf clusters inside, shade underneath, sun on top -
    red apples among the leaves, two hanging from the crown's lower edge on their stalks and one fallen on the grass.
    (`swing` is kept for the callers; the tree carries no swing.)"""
    _ = swing
    d = Canvas()
    rnd = random.Random(int(x * 3 + foot) % 997)
    d.add(f'<ellipse cx="0" cy="0" rx="42" ry="4" fill="{INK}" fill-opacity=".14"/>')
    for bx_, by_ in ((-26, -104), (24, -110), (2, -122)):                       # the boughs, into the crown
        d.tube(f"M0,-78 Q{n(bx_ * 0.4)},{n((by_ - 78) / 2 - 8)} {bx_},{by_}", P.TRUNK, 5, sw=1.2, shaded=False)
    d.shape("M-15,0 Q-8,-3 -7,-16 L-6,-84 H6 L7,-16 Q8,-3 15,0 Z", P.TRUNK, sw=1.6, light=(-1.5, 0))
    d.line("M-2,-10 q2,-14 -1,-30 M3,-34 q-2,-12 1,-26 M-3,-62 q1,-8 -1,-16", 0.9, P.WOOD_DARK, 0.7)
    blob_crown(d, 0, -116, 60, 40, LAWN, rnd, bumps=10 if lite else 14, lite=lite)
    apples = []
    for _ in range(10):
        a, rr = rnd.uniform(0, 2 * math.pi), math.sqrt(rnd.random()) * 0.72
        ax, ay = 54 * rr * math.cos(a), -116 + 34 * rr * math.sin(a)
        apples.append(f"M{n(ax + 3.8)},{n(ay)} a3.8,3.8 0 1 1 -7.6,0 a3.8,3.8 0 1 1 7.6,0 Z")
    hang = [(-30, -84), (22, -82)]
    stalks = " ".join(f"M{hx},{hy - 7} v4" for hx, hy in hang)
    apples += [f"M{hx + 3.8},{hy} a3.8,3.8 0 1 1 -7.6,0 a3.8,3.8 0 1 1 7.6,0 Z" for hx, hy in hang]
    apples.append("M31.8,-3.6 a3.8,3.8 0 1 1 -7.6,0 a3.8,3.8 0 1 1 7.6,0 Z")             # fallen on the grass
    d.line(stalks, 1, P.WOOD_DARK)
    d.add(f'<path d="{" ".join(apples)}" fill="{P.RED}" stroke="{INK}" stroke-width=".8"/>')
    c.add(_at(d, x, foot, k))


def birch(c: Canvas, x: float, foot: float, k: float, lite: bool = False) -> None:
    """A birch at (x, foot), 170 tall: the slender white trunk with its black marks, an oval crown of light green."""
    d = Canvas()
    rnd = random.Random(int(x * 7 + foot) % 991)
    d.add(f'<ellipse cx="0" cy="0" rx="20" ry="3" fill="{INK}" fill-opacity=".12"/>')
    d.tube("M0,-90 Q-6,-112 -12,-126 M0,-100 Q6,-120 10,-134", P.BIRCH, 3, sw=1, shaded=False)
    d.shape("M-6,0 L-4,-128 H4 L6,0 Z", P.BIRCH, sw=1.3, light=None)
    d.line(" ".join(f"M{n(rnd.uniform(-4, 0))},{n(-10 - q * 14 - rnd.uniform(0, 6))} h{n(rnd.uniform(3, 5))}"
                    for q in range(8)), 1.4, P.CHARCOAL)
    blob_crown(d, 0, -128, 30, 44, mix(P.LEAF_LIGHT, P.GRASS, 0.3), rnd, bumps=9 if lite else 12, sw=1.4, lite=lite)
    c.add(_at(d, x, foot, k))


def pine(c: Canvas, x: float, foot: float, k: float) -> None:
    """A pine at (x, foot), 180 tall: the brown trunk, tiers of dark needles narrowing to the top, each tier's
    hem ragged."""
    d = Canvas()
    d.add(f'<ellipse cx="0" cy="0" rx="26" ry="3" fill="{INK}" fill-opacity=".12"/>')
    d.shape("M-5,0 L-4,-40 H4 L5,0 Z", P.WOOD_DARK, sw=1.2, light=None)
    for q, (w, y0, h) in enumerate(((38, -30, 56), (31, -64, 50), (23, -96, 46), (14, -126, 52))):
        hem = " ".join(f"l{n(w / 3)},{n(-4 if i % 2 else 4)}" for i in range(6))
        d.shape(f"M{-w},{y0} {hem} L0,{y0 - h} Z", mix(P.FIR, P.PINE, 0.35 + q * 0.08), sw=1.3, light=(-1.5, 0))
    c.add(_at(d, x, foot, k))


def shrub(c: Canvas, x: float, foot: float, k: float, lite: bool = False) -> None:
    """A round garden shrub at (x, foot), 40 tall: one solid leafy mound."""
    d = Canvas()
    rnd = random.Random(int(x * 5 + foot) % 983)
    d.add(f'<ellipse cx="0" cy="0" rx="26" ry="3" fill="{INK}" fill-opacity=".12"/>')
    blob_crown(d, 0, -18, 24, 17, mix(P.LEAF, P.LEAF_DARK, 0.3), rnd, bumps=8 if lite else 10, sw=1.3, lite=lite)
    c.add(_at(d, x, foot, k))


def clothesline(c: Canvas, x0: float, x1: float, foot: float, k: float) -> None:
    """A clothesline between two T-posts from x0 to x1 at `foot`, 90 tall: the line sagging, and on it, each pinned
    by wooden pegs where it meets the line, a shirt with its collar, sleeves and buttons, a striped towel and a pair
    of socks - hanging in folds."""
    top = foot - 92 * k
    for px in (x0, x1):
        c.line(f"M{n(px)},{n(foot)} V{n(top)} M{n(px - 9 * k)},{n(top)} H{n(px + 9 * k)}", 2.6 * k, P.WOOD_DARK)
    mid = (x0 + x1) / 2
    sag = 12 * k

    def line_y(x: float) -> float:
        t = (x - mid) / ((x1 - x0) / 2)
        return top + 3 * k + sag * (1 - t * t)

    c.line(f"M{n(x0)},{n(top + 3 * k)} Q{n(mid)},{n(top + 3 * k + 2 * sag)} {n(x1)},{n(top + 3 * k)}", 0.9 * k + 0.3,
           INK)
    span = x1 - x0
    pegs = []
    # the shirt: shoulders on the line, sleeves out, a collar, a placket of buttons, hem in a curve
    sx = x0 + span * 0.26
    y = line_y(sx)
    w = 30 * k
    shirt = (f"M{n(sx - w / 2)},{n(y)} L{n(sx - w / 2 - 9 * k)},{n(y + 14 * k)} L{n(sx - w / 2 - 3 * k)},"
             f"{n(y + 17 * k)} L{n(sx - w / 2 + 2 * k)},{n(y + 10 * k)} L{n(sx - w / 2 + 2 * k)},{n(y + 34 * k)} "
             f"Q{n(sx)},{n(y + 38 * k)} {n(sx + w / 2 - 2 * k)},{n(y + 34 * k)} L{n(sx + w / 2 - 2 * k)},"
             f"{n(y + 10 * k)} L{n(sx + w / 2 + 3 * k)},{n(y + 17 * k)} L{n(sx + w / 2 + 9 * k)},{n(y + 14 * k)} "
             f"L{n(sx + w / 2)},{n(y)} Z")
    c.shape(shirt, mix(P.SKY, P.BLUE, 0.35), sw=0.9 * k + 0.2, light=None)
    c.line(f"M{n(sx - 5 * k)},{n(y)} L{n(sx)},{n(y + 6 * k)} L{n(sx + 5 * k)},{n(y)} M{n(sx)},{n(y + 6 * k)} "
           f"V{n(y + 34 * k)} M{n(sx - 8 * k)},{n(y + 14 * k)} q2,8 -1,16 M{n(sx + 9 * k)},{n(y + 12 * k)} q-2,9 1,18",
           0.7 * k + 0.2, darken(P.BLUE, 0.7))
    c.add("".join(f'<circle cx="{n(sx + 1.6 * k)}" cy="{n(y + (11 + q * 7) * k)}" r="{n(0.9 * k + 0.2)}" '
                  f'fill="{P.WHITE}"/>' for q in range(3)))
    pegs += [sx - w / 2 + 2 * k, sx + w / 2 - 2 * k]
    # the towel, folded over the line, its stripes at the ends
    tx = x0 + span * 0.58
    y = line_y(tx)
    c.shape(f"M{n(tx - 13 * k)},{n(y)} H{n(tx + 13 * k)} L{n(tx + 14 * k)},{n(y + 30 * k)} Q{n(tx)},{n(y + 32 * k)} "
            f"{n(tx - 14 * k)},{n(y + 30 * k)} Z", P.WHITE, sw=0.9 * k + 0.2, light=None)
    c.line(f"M{n(tx - 13.6 * k)},{n(y + 23 * k)} Q{n(tx)},{n(y + 25 * k)} {n(tx + 13.6 * k)},{n(y + 23 * k)} "
           f"M{n(tx - 13.8 * k)},{n(y + 26.5 * k)} Q{n(tx)},{n(y + 28.5 * k)} {n(tx + 13.8 * k)},{n(y + 26.5 * k)}",
           1.6 * k, P.PINK)
    c.line(f"M{n(tx - 4 * k)},{n(y + 3 * k)} q-1,10 1,18 M{n(tx + 6 * k)},{n(y + 3 * k)} q1,9 -1,17", 0.6 * k + 0.2,
           P.METAL)
    pegs += [tx - 11 * k, tx + 11 * k]
    # a pair of socks
    for q, ox in enumerate((0.8, 0.88)):
        px = x0 + span * ox
        y = line_y(px)
        c.shape(f"M{n(px - 3 * k)},{n(y)} h{n(6 * k)} v{n(14 * k)} q0,{n(5 * k)} {n(6 * k)},{n(5 * k)} "
                f"v{n(4.5 * k)} q{n(-9 * k)},{n(1 * k)} {n(-12 * k)},{n(-6 * k)} Z", (P.RED, P.RED)[q],
                sw=0.8 * k + 0.2, light=None)
        c.line(f"M{n(px - 3 * k)},{n(y + 3.5 * k)} h{n(6 * k)}", 1.2 * k, P.WHITE)
        pegs.append(px)
    c.add("".join(f'<rect x="{n(px - 1.3 * k)}" y="{n(line_y(px) - 3 * k)}" width="{n(2.6 * k)}" '
                  f'height="{n(7 * k)}" rx="{n(0.8 * k)}" fill="{P.WOOD_PALE}" stroke="{INK}" '
                  f'stroke-width="{n(0.5 * k + 0.15)}"/>' for px in pegs))                       # the pegs


def flowers(c: Canvas, x0: float, x1: float, foot: float, k: float, seed: int,
            avoid: tuple[float, float] | None = None) -> None:
    """A border of flowers along a wall or a fence from x0 to x1 standing on `foot`: clumps of leaves, stems, and
    blooms of four kinds - leaves and blooms as one path a colour."""
    rnd = random.Random(seed)
    leaves, stems = [], []
    blooms: dict[str, list[str]] = {}
    q = x0 + 4 * k
    while q < x1 - 4 * k:
        if avoid and avoid[0] < q < avoid[1]:
            q = avoid[1] + 4 * k
            continue
        h = rnd.uniform(9, 18) * k
        leaves.append(f"M{n(q - 5 * k)},{n(foot)} q{n(5 * k)},{n(-8 * k)} {n(10 * k)},0 Z")
        stems.append(f"M{n(q)},{n(foot - 2 * k)} V{n(foot - h)}")
        col = rnd.choice((P.RED, P.PINK, SUN, P.WHITE, mix(P.VIOLET, P.PINK, 0.3)))
        r = rnd.uniform(2.4, 3.4) * k
        blooms.setdefault(col, []).append(f"M{n(q + r)},{n(foot - h)} a{n(r)},{n(r)} 0 1 1 {n(-2 * r)},0 "
                                          f"a{n(r)},{n(r)} 0 1 1 {n(2 * r)},0 Z")
        q += rnd.uniform(11, 17) * k
    c.line(" ".join(stems), max(0.6, 1.1 * k), P.LEAF_DARK)
    c.add(f'<path d="{" ".join(leaves)}" fill="{P.LEAF}" stroke="{INK}" stroke-width="{n(max(0.4, 0.6 * k))}"/>')
    for col, ds in blooms.items():
        c.add(f'<path d="{" ".join(ds)}" fill="{col}" stroke="{INK}" stroke-width="{n(max(0.4, 0.6 * k))}"/>')


def veg_patch(c: Canvas, x0: float, x1: float, foot: float, k: float) -> None:
    """A vegetable patch in a raised bed of boards: dark earth, cabbages with their outer leaves and carrot tops in
    rows."""
    c.add(f'<rect x="{n(x0)}" y="{n(foot - 10 * k)}" width="{n(x1 - x0)}" height="{n(10 * k)}" '
          f'fill="{P.WOOD}" stroke="{INK}" stroke-width="{n(0.8 * k + 0.2)}"/>')
    c.add(f'<rect x="{n(x0 + 2 * k)}" y="{n(foot - 12 * k)}" width="{n(x1 - x0 - 4 * k)}" height="{n(3 * k)}" '
          f'fill="{darken(P.WOOD, 0.55)}"/>')
    q, i = x0 + 9 * k, 0
    while q < x1 - 9 * k:
        if i % 2:
            c.add(f'<path d="M{n(q - 9 * k)},{n(foot - 11 * k)} q{n(2 * k)},{n(-10 * k)} {n(9 * k)},{n(-9 * k)} '
                  f'q{n(7 * k)},{n(-1 * k)} {n(9 * k)},{n(9 * k)} Z" fill="{P.LEAF}" stroke="{INK}" '
                  f'stroke-width="{n(0.6 * k + 0.2)}"/><circle cx="{n(q)}" cy="{n(foot - 16 * k)}" r="{n(5 * k)}" '
                  f'fill="{lighten(P.LEAF, 0.35)}" stroke="{INK}" stroke-width="{n(0.6 * k + 0.2)}"/>')
        else:
            c.line(f"M{n(q - 3 * k)},{n(foot - 11 * k)} l{n(-2 * k)},{n(-10 * k)} M{n(q)},{n(foot - 11 * k)} "
                   f"v{n(-12 * k)} M{n(q + 3 * k)},{n(foot - 11 * k)} l{n(2 * k)},{n(-10 * k)}", max(1.0, 1.4 * k),
                   P.GREEN)
        q += 16 * k
        i += 1


def pickets(c: Canvas, x0: float, x1: float, foot: float, k: float, gap: tuple[float, float] | None = None) -> None:
    """The white picket fence from x0 to x1 standing at `foot`, 70 tall at k=1: pickets with pointed tops on two
    rails, a stouter post with its cap every ten pickets, the rails' shadow on the pickets, the fence's shadow on
    the ground; an opening between `gap` (for the gate, or the gap being mended)."""
    shadow, pick, posts, xs = [], [], [], []
    q, i = x0, 0
    while q <= x1:
        if not gap or not gap[0] - 6 * k < q < gap[1] + 6 * k:
            if i % 10 == 0:
                posts.append(q)
            else:
                xs.append(q)
                pick.append(f"M{n(q - 4.6 * k)},{n(foot)} V{n(foot - 60 * k)} L{n(q)},{n(foot - 67 * k)} "
                            f"L{n(q + 4.6 * k)},{n(foot - 60 * k)} V{n(foot)} Z")
        q += 13 * k
        i += 1
    segs = [(x0, x1)] if not gap else [(x0, gap[0]), (gap[1], x1)]
    for a, b in segs:
        if b > a:
            shadow.append(f"M{n(a)},{n(foot - 0.5)} H{n(b)} v{n(3 * k)} H{n(a)} Z")
    c.add(f'<path d="{" ".join(shadow)}" fill="{INK}" fill-opacity=".14"/>')
    for a, b in segs:
        for y in (foot - 16 * k, foot - 48 * k):
            if b > a:
                c.shape(rounded_rect_d(a - 5 * k, y - 2.4 * k, b - a + 10 * k, 4.8 * k, 1 * k), darken(PICKET, 0.86),
                        sw=max(0.5, 0.8 * k), light=None)
    c.add(f'<path d="{" ".join(pick)}" fill="{PICKET}" stroke="{INK}" stroke-width="{n(max(0.6, 1.0 * k))}" '
          f'stroke-linejoin="round"/>')
    _ = xs
    for p_ in posts:
        c.shape(rounded_rect_d(p_ - 6 * k, foot - 66 * k, 12 * k, 66 * k, 1 * k), PICKET, sw=max(0.6, 1.1 * k),
                light=None)
        c.shape(f"M{n(p_ - 8 * k)},{n(foot - 66 * k)} h{n(16 * k)} l{n(-3 * k)},{n(-4 * k)} h{n(-10 * k)} Z",
                darken(PICKET, 0.9), sw=max(0.6, 1 * k), light=None)


# ============================================================================ the gate, the mailbox, the library
def gatepost(c: Canvas, x: float, foot: float, k: float) -> None:
    """A square gatepost at (x, foot), 12 wide and 76 tall to the ball on its cap, painted the cover's yellow."""
    c.shape(rounded_rect_d(x - 6 * k, foot - 66 * k, 12 * k, 66 * k, 1 * k), PAINT, sw=max(0.6, 1.3 * k),
            light=(-1 * k, 0))
    c.shape(f"M{n(x - 8 * k)},{n(foot - 66 * k)} h{n(16 * k)} l{n(-3 * k)},{n(-4 * k)} h{n(-10 * k)} Z", PAINT,
            sw=max(0.6, 1.1 * k), light=None)
    c.add(f'<circle cx="{n(x)}" cy="{n(foot - 74 * k)}" r="{n(4.4 * k)}" fill="{PAINT}" stroke="{INK}" '
          f'stroke-width="{n(max(0.6, 1.1 * k))}"/>')


def gate_leaf(c: Canvas, x0: float, x1: float, foot: float, k: float, open_: bool) -> None:
    """The picket gate hung on its hinge post at x0, its latch at the post at x1: shut - six pickets on two rails
    with the diagonal brace rising from the hinge side, black strap hinges, the thumb latch; open - swung into the
    yard on its hinges, seen nearly edge on, its far end higher, further off."""
    w = x1 - x0
    s_ = 1 if w > 0 else -1
    hx = x0 + s_ * 7 * k
    if open_:
        tip = hx + s_ * 16 * k
        c.shape(f"M{n(hx)},{n(foot - 6 * k)} L{n(tip)},{n(foot - 14 * k)} V{n(foot - 66 * k)} L{n(hx)},"
                f"{n(foot - 62 * k)} Z", PICKET, sw=max(0.6, 1.1 * k), light=None)
        c.line(" ".join(f"M{n(hx + s_ * q * 4 * k)},{n(foot - 6 * k - q * 2 * k)} V{n(foot - 62 * k - q * 1 * k)}"
                        for q in range(1, 4)), max(0.5, 0.7 * k), darken(PICKET, 0.75))
        c.line(f"M{n(hx)},{n(foot - 20 * k)} L{n(tip)},{n(foot - 27 * k)} M{n(hx)},{n(foot - 50 * k)} L{n(tip)},"
               f"{n(foot - 55 * k)}", 2.6 * k, darken(PICKET, 0.82))
        c.line(f"M{n(x0)},{n(foot - 20 * k)} h{n(s_ * 9 * k)} M{n(x0)},{n(foot - 50 * k)} h{n(s_ * 9 * k)}", 2.4 * k,
               P.CHARCOAL)
        return
    lx = x1 - s_ * 7 * k
    a, b = min(hx, lx), max(hx, lx)
    c.shape(rounded_rect_d(a, foot - 22 * k, b - a, 5 * k, 1 * k), darken(PICKET, 0.88), sw=max(0.5, 0.9 * k),
            light=None)
    c.shape(rounded_rect_d(a, foot - 52 * k, b - a, 5 * k, 1 * k), darken(PICKET, 0.88), sw=max(0.5, 0.9 * k),
            light=None)
    c.line(f"M{n(hx)},{n(foot - 20 * k)} L{n(lx)},{n(foot - 50 * k)}", 4.6 * k, INK)
    c.line(f"M{n(hx)},{n(foot - 20 * k)} L{n(lx)},{n(foot - 50 * k)}", 3 * k, darken(PICKET, 0.88))  # the brace
    pick = []
    count = 6
    for q in range(count):
        px = a + 5 * k + q * (b - a - 10 * k) / (count - 1)
        top = foot - 58 * k - 4 * k * math.sin(math.pi * q / (count - 1))
        pick.append(f"M{n(px - 4.2 * k)},{n(foot - 8 * k)} V{n(top)} L{n(px)},{n(top - 6 * k)} L{n(px + 4.2 * k)},"
                    f"{n(top)} V{n(foot - 8 * k)} Z")
    c.add(f'<path d="{" ".join(pick)}" fill="{PICKET}" stroke="{INK}" stroke-width="{n(max(0.6, 1 * k))}" '
          f'stroke-linejoin="round"/>')
    c.line(f"M{n(x0)},{n(foot - 19 * k)} h{n(s_ * 16 * k)} M{n(x0)},{n(foot - 49 * k)} h{n(s_ * 16 * k)}", 2.4 * k,
           P.CHARCOAL)                                                                            # strap hinges
    c.shape(rounded_rect_d(min(x1, x1 - s_ * 9 * k), foot - 40 * k, 9 * k, 3 * k, 1 * k), P.CHARCOAL,
            sw=max(0.4, 0.6 * k), light=None)                                                     # the latch


def mailbox(c: Canvas, x: float, foot: float, k: float, open_: bool, flag: bool, way: int = 1) -> None:
    """A rural mailbox on its own wooden post set in the ground at (x, foot), its top at 66 - the professor's chest:
    the post with its arm, the dark-green tunnel box seen from the side, its arched door at the street end (`way`)
    with its pull - hanging open on its bottom hinge with the post inside showing (`open_`) - and the red flag on its
    side, raised (`flag`) when there is mail."""
    d = Canvas()
    d.add(f'<ellipse cx="0" cy="0" rx="9" ry="1.6" fill="{INK}" fill-opacity=".14"/>')
    d.shape("M-3,0 V-50 H3 V0 Z", P.WOOD, sw=1.1, light=(-0.6, 0))                               # the post
    d.line("M-1,-6 q1,-12 0,-24 M1,-30 q-1,-8 0,-14", 0.5, P.WOOD_DARK, 0.7)
    d.shape("M-10,-50 H10 V-46 H-10 Z", P.WOOD_DARK, sw=0.9, light=None)                         # its board
    d.shape("M-15,-51 V-61 Q-15,-66 -9,-66 H13 V-51 Z", MAILBOX, sw=1.2, light=(-0.8, -0.8))     # the box's side
    d.line("M-11,-63 H11", 0.8, lighten(MAILBOX, 0.35))
    d.line("M-14,-55 H12", 0.6, darken(MAILBOX, 0.7))
    if open_:
        d.add(f'<path d="M13,-51 V-62 Q13,-66 16,-66 Q19,-66 19,-62 V-51 Z" fill="{P.CHARCOAL}" stroke="{INK}" '
              f'stroke-width="1"/>')                                                             # the dark mouth
        for q, col in enumerate((P.WHITE, P.CARD)):
            d.shape(rounded_rect_d(12 + q * 1.5, -61 + q * 2, 6, 6, 0.5), col, sw=0.5, light=None)  # letters left
        d.shape("M13,-51 Q19,-49 26,-48 L26,-44 Q19,-45 13,-47 Z", darken(MAILBOX, 0.85), sw=1, light=None)   # the door
        d.line("M24,-48 v4", 1.4, P.METAL_DARK)
    else:
        d.shape("M13,-51 V-62 Q13,-66 16,-66 Q19,-66 19,-62 V-51 Z", darken(MAILBOX, 0.88), sw=1.1, light=None)
        d.line("M20,-58 h2", 1.6, P.METAL_DARK)                                                 # the pull
    if flag:
        d.line("M-8,-57 V-74", 1.6, P.METAL_DARK)
        d.shape("M-8,-74 h8 v6 h-8 Z", P.RED, sw=0.8, light=None)
    else:
        d.line("M-8,-57 H6", 1.6, P.METAL_DARK)
        d.shape("M6,-57 h-6 v-5 h6 Z", P.RED, sw=0.8, light=None)
    d.add(f'<circle cx="-8" cy="-57" r="1.4" fill="{P.CHARCOAL}"/>')
    c.add(_at(d, x, foot, k, mirror=way < 0))


MAILBOX_DOOR = (17.0, -57.0)        # the open mouth of the mailbox, for a hand to reach into


def little_library(s: Strip, x: float, foot: float, k: float, open_: bool) -> tuple:
    """A little free library on its post at (x, foot), never mirrored: a wooden case 40 wide on a post, its gabled
    roof of shingles, the glazed door in its frame - two shelves of books seen through the glass, or the door swung
    open on its hinges to the left and the books bare. The case is a container (`Pen`), its two shelves its parts.
    Returns its box."""
    pen = Pen(s, x, foot, k)
    d = pen.c
    d.add(f'<ellipse cx="0" cy="0" rx="10" ry="1.6" fill="{INK}" fill-opacity=".14"/>')
    d.shape("M-3.4,0 V-46 H3.4 V0 Z", P.WOOD, sw=1.1, light=(-0.6, 0))
    d.shape("M-10,-46 L-3,-40 H3 L10,-46 Z", P.WOOD_DARK, sw=0.9, light=None)                  # its braces
    case = pen.container("library", -20, -86, 40, 40, mix(P.WOOD, P.TERRACOTTA, 0.25), radius=1.5, sw=1.3,
                         light=None)
    pad = pen.pad(40, 40)
    il, it, ir, ib = -20 + pad, -86 + pad, 20 - pad, -46 - pad
    d.add(f'<rect x="{n(il)}" y="{n(it)}" width="{n(ir - il)}" height="{n(ib - it)}" fill="{P.CHARCOAL}" '
          f'fill-opacity=".85"/>')
    rows = 2
    gap = max(2.2, 3.4 / k)                                          # the shelf board between, never too thin
    rh = (ib - it - gap) / rows
    rnd = random.Random(int(x))
    for r_ in range(rows):
        top, bottom = it + r_ * (rh + gap), it + r_ * (rh + gap) + rh
        bx = il + 0.6
        while bx < ir - 3:
            bw = rnd.uniform(2.2, 3.4)
            bh = rh * rnd.uniform(0.62, 0.92)
            col = rnd.choice((P.RED, P.TEAL, SUN, P.BLUE, P.GREEN, P.PINK, P.CARD))
            d.add(f'<rect x="{n(bx)}" y="{n(bottom - bh)}" width="{n(min(bw, ir - 0.6 - bx))}" height="{n(bh)}" '
                  f'fill="{col}" stroke="{INK}" stroke-width=".35"/>')
            bx += bw + 0.25
        pen.child(case, f"shelf{r_}", il, top, ir, bottom)
        if r_ < rows - 1:
            d.add(f'<rect x="{n(il)}" y="{n(bottom)}" width="{n(ir - il)}" height="{n(gap)}" fill="{P.WOOD_PALE}"/>')
    if open_:
        d.shape("M-20,-86 L-31,-82 V-49 L-20,-46 Z", mix(P.WOOD, P.TERRACOTTA, 0.25), sw=1.2, light=None)
        d.add(f'<path d="M-22,-83 L-29,-80 V-51 L-22,-49 Z" fill="{mix(P.SKY, P.LENS, 0.5)}" fill-opacity=".8" '
              f'stroke="{INK}" stroke-width=".5"/>')
    else:
        d.add(f'<rect x="{n(il)}" y="{n(it)}" width="{n(ir - il)}" height="{n(ib - it)}" fill="{P.SKY}" '
              f'fill-opacity=".25"/><path d="M{n(il + 4)},{n(ib - 3)} L{n(il + 14)},{n(it + 3)} M{n(il + 9)},'
              f'{n(ib - 3)} L{n(il + 19)},{n(it + 3)}" stroke="{P.WHITE}" stroke-width="1.2" '
              f'stroke-opacity=".6"/>')
        d.add(f'<circle cx="{n(ir - 1.5)}" cy="{n((it + ib) / 2)}" r="1.1" fill="{P.GOLD}" stroke="{INK}" '
              f'stroke-width=".4"/>')
    d.shape("M-25,-84 L0,-102 L25,-84 L22,-82 L0,-97 L-22,-82 Z", mix(P.TERRACOTTA, P.WOOD_DARK, 0.3), sw=1.2,
            light=None)                                                                          # the roof
    d.add(f'<path d="M-17,-88 L0,-100 L17,-88 Z" fill="{INK}" fill-opacity=".18"/>')
    s.put(foot - 0.5, pen.svg(), None)
    return (x - (31 if open_ else 26) * k, foot - 103 * k, x + 26 * k, foot)


def gate(c: Canvas, x: float, foot: float, k: float, open_: bool) -> dict:
    """The professor's gate at (x, foot), 130 wide and 110 tall (in the units of a 70-tall fence): the two square
    gateposts with their caps and balls, the picket gate hung on the left post - shut, or swung open into the yard -
    and the mailbox on its own post just outside the right gatepost. Returns its box and the mailbox's slot."""
    kk = k * 70 / 66
    gatepost(c, x - 52 * k, foot, kk)
    gatepost(c, x + 52 * k, foot, kk)
    gate_leaf(c, x - 52 * k - 6 * kk, x + 52 * k + 6 * kk, foot, kk, open_)
    mailbox(c, x + 80 * k, foot, kk * 1.25, open_=False, flag=True, way=1)
    return {"box": (x - 60 * k, foot - 110 * k, x + 101 * k, foot), "slot": (x + 80 * k, foot - 86 * k)}


# ============================================================================ the ground
def merged(c: Canvas, shapes: dict[str, list[str]], stroke: str = "") -> None:
    """Many small shapes of one colour as one path each."""
    for fill, ds in shapes.items():
        if ds:
            c.add(f'<path d="{" ".join(ds)}" fill="{fill}"{stroke}/>')


def paving(c: Canvas, y0: float, y1: float, k: float, grow: float = 3.0) -> None:
    """The brick patio: bricks in staggered courses, nearer courses bigger, three reds, mortar between, a soft
    shade along its back edge where the lawn's kerb stands."""
    c.add(f'<rect x="-6" y="{n(y0)}" width="{W + 12}" height="{n(y1 - y0)}" fill="{mix(P.STONE, P.SAND, 0.4)}"/>')
    shades = (BRICK[0], BRICK[1], mix(BRICK[0], P.RUBY, 0.2))
    shapes: dict[str, list[str]] = {col: [] for col in shades}
    y, row = y0 + 6 * k, 0
    rnd = random.Random(9)
    while y < y1:
        rh = (6 + row * grow) * max(0.6, k)
        bw = rh * 2.3
        x = -6 - (row % 2) * bw / 2
        while x < W + 6:
            shapes[shades[rnd.randrange(3)]].append(f"M{n(x + 0.8)},{n(y + 0.8)} h{n(bw - 1.6)} v{n(rh - 1.6)} "
                                                    f"h{n(-bw + 1.6)} Z")
            x += bw
        y += rh
        row += 1
    merged(c, shapes)
    c.add(f'<rect x="-6" y="{n(y0)}" width="{W + 12}" height="{n(6 * k)}" fill="{STONE_}" stroke="{INK}" '
          f'stroke-width="1"/>')                                                                  # the kerb
    c.add(f'<rect x="-6" y="{n(y0 + 6 * k)}" width="{W + 12}" height="{n(3 * k)}" fill="{INK}" fill-opacity=".1"/>')


def pavement(c: Canvas, y0: float, y1: float, k: float) -> None:
    """The street's pavement in front of the fence: square concrete slabs in rows, nearer rows bigger, two greys,
    a crack here and there, a granite edge along the fence's foot."""
    c.add(f'<rect x="-6" y="{n(y0)}" width="{W + 12}" height="{n(y1 - y0)}" fill="{darken(SLAB, 0.8)}"/>')
    shades = (SLAB, darken(SLAB, 0.93))
    shapes: dict[str, list[str]] = {col: [] for col in shades}
    y, row = y0 + 5 * k, 0
    rnd = random.Random(4)
    cracks = []
    while y < y1:
        rh = (16 + row * 10) * max(0.6, k)
        bw = rh * 1.6
        x = -6 - (row % 2) * bw * 0.4
        while x < W + 6:
            shapes[shades[rnd.randrange(2)]].append(f"M{n(x + 1)},{n(y + 1)} h{n(bw - 2)} v{n(rh - 2)} h{n(-bw + 2)} Z")
            if rnd.random() < 0.03:
                cracks.append(f"M{n(x + bw * 0.3)},{n(y + 1)} l{n(bw * 0.1)},{n(rh * 0.4)} l{n(-bw * 0.05)},"
                              f"{n(rh * 0.3)}")
            x += bw
        y += rh
        row += 1
    merged(c, shapes)
    c.line(" ".join(cracks), 0.6, darken(SLAB, 0.6))
    c.add(f'<rect x="-6" y="{n(y0)}" width="{W + 12}" height="{n(5 * k)}" fill="{mix(P.STONE, P.METAL_DARK, 0.3)}" '
          f'stroke="{INK}" stroke-width="1"/>')


def lawn(c: Canvas, y0: float, y1: float, k: float, seed: int) -> None:
    """A strip of lawn: the grass lighter towards the front, tufts here and there."""
    c.add(f'<rect x="-6" y="{n(y0)}" width="{W + 12}" height="{n(y1 - y0)}" fill="{LAWN}"/>'
          f'<rect x="-6" y="{n(y0 + (y1 - y0) * 0.55)}" width="{W + 12}" height="{n((y1 - y0) * 0.45)}" '
          f'fill="{mix(LAWN, LAWN_LIGHT, 0.5)}"/>')
    rnd = random.Random(seed)
    tufts = []
    for _ in range(int(W / 60)):
        tx, ty = rnd.uniform(0, W), rnd.uniform(y0 + (y1 - y0) * 0.3, y1 - 1)
        tufts.append(f"M{n(tx)},{n(ty)} l{n(-1.5 * k)},{n(-4 * k)} M{n(tx + 2 * k)},{n(ty)} l{n(1 * k)},{n(-5 * k)}")
    c.line(" ".join(tufts), max(0.6, 0.9 * k), P.LEAF_DARK, 0.7)


def sky(c: Canvas, bottom: float, seed: int) -> None:
    """The summer sky down to `bottom`, two soft clouds high in it."""
    sets.sky(c, SKY_TOP, SKY_LOW, bottom, W)
    rnd = random.Random(seed * 7 + 3)
    kc = max(0.6, min(1.3, bottom / 200))
    for _ in range(2):
        cx, cy = rnd.uniform(0.1, 0.9) * W, bottom * rnd.uniform(0.18, 0.4)
        c.add(f'<path d="M{n(cx - 40 * kc)},{n(cy)} q{n(10 * kc)},{n(-16 * kc)} {n(26 * kc)},{n(-8 * kc)} '
              f'q{n(14 * kc)},{n(-16 * kc)} {n(30 * kc)},0 q{n(16 * kc)},{n(-4 * kc)} {n(24 * kc)},{n(8 * kc)} Z" '
              f'fill="{P.WHITE}" fill-opacity=".9"/>')


def veil(s: Strip) -> None:
    """The backdrop's top melts into the paper."""
    band = min(s.h * 0.16, 40.0)
    s.back.fade(-10, -10, W + 20, band + 10, [(0, P.PAPER, 1), (0.25, P.PAPER, 0.85), (1, P.PAPER, 0)])


# ============================================================================ the camera
def prepare(s: Strip) -> None:
    """The yard's camera, close: the cast as big as the frame lets it be, the floor showing under their feet."""
    s.decor = False
    s.dress = False
    s.indoor = False
    ledger(s)
    zoom(s)
    feet = lane(s).feet
    names = ("professor", "cat", "agent", "caterpillar")
    if s.h < 300:                                                      # a close-up: the professor nearly fills it
        top = max(_box(s, name, 0, feet)[3] - _box(s, name, 0, feet)[1] for name in names)
        s.tall *= (feet - 6) / top
    else:                                                              # a tall frame: the cast half its height
        top = _box(s, "professor", 0, feet)[3] - _box(s, "professor", 0, feet)[1]
        s.tall *= s.h * 0.52 / top
    widest = max(_box(s, name, 0, feet)[2] - _box(s, name, 0, feet)[0] for name in names)
    s.tall *= min(1.0, (s.hi - s.lo) * (0.19 if s.h < 300 else 0.27) / widest)
    s.tall *= getattr(s, "fit", 1.0)                                   # stepped back until the moment fits
    s.unit = s.tall / 137


def U(s: Strip) -> float:
    """Page units per unit of the professor's height (100 = the professor)."""
    return height(s, "professor") / 100


def low(s: Strip) -> bool:
    """A strip: the camera comes close - the thing drawn big, one or two of the cast beside it."""
    return s.h < 200


# The yard's row, in its own units, left to right: what stands at the back of the lawn, along the back fence.
YARD = (("tree", 120, 1), ("cottage", 420, 0), ("shed", 760, 0), ("line", 930, 0), ("tree", 1140, 0),
        ("veg", 1320, 0), ("tree", 1520, 1), ("line", 1700, 0), ("veg", 1900, 0))
YARD_LEN = 2050
FAR = ((60, 0), (250, 1), (620, 2), (1000, 3), (1180, 1), (1400, 0), (1600, 2), (1800, 3), (1990, 1))


def yard(s: Strip, view: float, seed: int = 0) -> None:
    """The yard side behind a frame, the camera at `view` along its row (`YARD`): the sky, the neighbours' houses
    beyond the back fence, the fence itself, and along it the cottage, the shed, the apple trees, the clothesline,
    the vegetable beds; the lawn, its flowers, and the brick patio the cast stands on."""
    c = s.back
    feet = lane(s).feet
    if low(s):                                                         # a strip: the camera by the back fence
        near_fence(s, seed, view)
        return
    s.yard = s.base - max(12.0, s.base * 0.12)
    sky(c, s.yard, seed)
    kb = min(U(s) * 0.52, (s.yard - 4) / COTTAGE_H)

    def sx(yx: float) -> float:
        return W / 2 + (yx - view) * kb

    kf = kb * 0.62
    far = Canvas()
    neighbours(far, s.yard - 10 * kb, kf, seed, view)
    c.add(f'<g opacity=".9">{far.render()}</g>')
    c.add(f'<rect x="-6" y="{n(s.yard - 12 * kb)}" width="{W + 12}" height="{n(14 * kb)}" '
          f'fill="{mix(LAWN, P.SKY, 0.25)}"/>')
    pickets(c, -6, W + 6, s.yard, kb * 55 / 70)
    near = Canvas()
    for kind, yx, arg in YARD:
        for wrap in (-YARD_LEN, 0, YARD_LEN):
            x = sx(yx + wrap)
            if not -200 * kb < x < W + 200 * kb:
                continue
            if kind == "cottage":
                cottage(near, x, s.yard, kb, seed=seed)
            elif kind == "shed":
                shed(near, x, s.yard, kb)
            elif kind == "tree":
                apple_tree(near, x, s.yard, kb * 1.15, swing=bool(arg))
            elif kind == "line":
                clothesline(near, x - 70 * kb, x + 70 * kb, s.yard, kb)
            elif kind == "veg":
                veg_patch(near, x - 70 * kb, x + 70 * kb, s.yard + 2 * kb, kb)
    flowers(c, -6, W + 6, s.yard + 1, kb, seed + 2)
    c.add(near.render())
    lawn(c, s.yard, s.base + 1, kb, seed)
    paving(c, s.base, s.h + 4, max(0.8, s.unit))
    veil(s)
    _ = feet


def near_fence(s: Strip, seed: int, view: float = 0.0) -> None:
    """A strip's yard: the camera close to the back fence - the neighbours' gabled roofs over it, the pickets big
    behind the cast, flowers at their foot, the patio."""
    c = s.back
    u = U(s)
    fence = lane(s).feet - 18 * u
    s.yard = fence
    sky(c, fence - 20 * u, seed)
    kf = min(u * 0.5, (fence - 20 * u) / 130)
    far = Canvas()
    neighbours(far, fence - 24 * u, kf, seed, view)
    c.add(f'<g opacity=".92">{far.render()}</g>')
    lawn(c, fence - 24 * u, fence + 1, kf, seed)
    pickets(c, -6 - (view % 13), W + 6, fence, u * 55 / 70)
    flowers(c, -6, W + 6, fence + 1, u * 0.7, seed + 4)
    paving(c, fence + 2, s.h + 4, max(0.8, s.unit))
    veil(s)


def street(s: Strip, gx: float, open_: bool, seed: int = 0) -> float:
    """The street side behind a frame, the gate at `gx`: the sky, the cottage's front behind its garden with its door
    on the line of the gate, an apple tree beside it, the brick path from the gate up to the steps between borders of
    flowers, the white fence along the back of the pavement with the gate hung between its posts - shut, or open into
    the yard - and the pavement the cast stands on. Returns the fence's foot."""
    c = s.back
    u = U(s)
    feet = lane(s).feet
    fence = feet - 14 * u
    garden = fence - max(10.0, 58 * u)
    kc = min(u * 0.6, (garden - 4) / COTTAGE_H)
    sky(c, garden, seed)
    far = Canvas()
    for q, kind in enumerate((1, 3, 0, 2)):
        x = gx + (-1) ** q * (230 + 160 * (q // 2)) * kc
        if -80 * kc < x < W + 80 * kc:
            far_house(far, x, garden - 18 * kc, kc * 0.62, kind)
    c.add(f'<g opacity=".9">{far.render()}</g>')
    house_x = gx + 86 * kc                                     # the door (at -86) on the line of the gate
    lawn(c, garden - 14 * kc, fence + 1, kc, seed)
    apple_tree(c, house_x + (215 if gx < W / 2 else -215) * kc, garden - 6 * kc, kc * 1.2, swing=False)
    cottage(c, house_x, garden, kc, seed=seed)
    gw = 52 * u                                                # the gate's opening, post to post
    c.add(f'<path d="M{n(gx - gw / 2)},{n(fence)} L{n(gx - 20 * kc)},{n(garden + 1)} H{n(gx + 20 * kc)} '
          f'L{n(gx + gw / 2)},{n(fence)} Z" fill="{BRICK[0]}" stroke="{INK}" stroke-width="1"/>')  # the path
    rows = []
    for q in range(1, 9):
        t = (q / 9) ** 1.6
        y = garden + (fence - garden) * t
        half = 20 * kc + (gw / 2 - 20 * kc) * t
        rows.append(f"M{n(gx - half)},{n(y)} H{n(gx + half)}")
    c.line(" ".join(rows), 0.8, darken(BRICK[0], 0.75))
    for side in (-1, 1):                                       # borders along the path
        x0 = gx + side * (gw / 2 + 4 * u)
        flowers(c, min(x0, x0 + side * 70 * u), max(x0, x0 + side * 70 * u), fence - 4 * u, u * 0.8, seed + side)
    pk = u * 50 / 70
    pickets(c, -6, W + 6, fence, pk, gap=(gx - gw / 2 - 6 * u, gx + gw / 2 + 6 * u))
    for px in (gx - gw / 2 - 6 * u, gx + gw / 2 + 6 * u):
        gatepost(c, px, fence, u * 0.85)
    gate_leaf(c, gx - gw / 2 - 6 * u, gx + gw / 2 + 6 * u, fence, u * 0.85, open_)
    pavement(c, fence, s.h + 4, max(0.8, s.unit))
    veil(s)
    return fence


# ============================================================================ things held
def upright(s: Strip, who, make, tilt: float = 0.0, side: str = "right") -> None:
    """Put a thing into a hand so that it stands as drawn - +x the way the holder faces, up the page's up - tilted
    `tilt` degrees further (clockwise, as the holder faces right)."""
    if who is None:
        return
    rot = s.grip(who, side)[2]
    if who.flip:
        rot = 180 - rot
    s.hold(who, make, side, turn=-rot + tilt)


def teapot(x: float, y: float, k: float) -> str:
    """The white china teapot with blue bands held by its handle in the fist: the round body before the knuckles,
    its lid with the knob, the spout curving up at the front."""
    c = Canvas()
    c.line("M0,-4 Q-1,2 2,5", 2.2, INK)
    c.line("M0,-4 Q-1,2 2,5", 1.2, P.WHITE)                                                    # the handle
    c.shape("M2,5 Q2,-5 12,-5 Q22,-5 22,5 Q22,13 12,13 Q2,13 2,5 Z", P.WHITE, sw=0.7, light=(-0.6, -0.6))
    c.line("M3,2 H21 M3.4,9 H20.6", 1, P.BLUE)
    c.shape("M7,-5 Q12,-8.5 17,-5 Z", P.WHITE, sw=0.6, light=None)                              # the lid
    c.add(f'<circle cx="12" cy="-8.6" r="1.4" fill="{P.BLUE}" stroke="{INK}" stroke-width=".5"/>')
    c.shape("M21,7 Q26,6 28,-1 L30,-1 Q29,9 22,11 Z", P.WHITE, sw=0.6, light=None)              # the spout
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k * 0.6)})">{c.render()}</g>'


TEAPOT_SPOUT = (17.4, -0.6)


def cup(x: float, y: float, k: float) -> str:
    """A teacup on its saucer held by the saucer's rim, full of tea, a curl of steam over it."""
    c = Canvas()
    c.add(f'<ellipse cx="8" cy="0" rx="8" ry="1.6" fill="{P.WHITE}" stroke="{INK}" stroke-width=".5"/>')
    c.shape("M3.5,-6 H12.5 Q12.5,-1 8,-0.6 Q3.5,-1 3.5,-6 Z", P.WHITE, sw=0.5, light=None)
    c.add(f'<ellipse cx="8" cy="-6" rx="4.5" ry="1" fill="{mix(P.ORANGE, P.WOOD_DARK, 0.5)}" stroke="{INK}" '
          f'stroke-width=".4"/>')
    c.line("M12.4,-5 q2.6,0.4 1.4,3 q-0.8,0.8 -2,0.6", 0.6, INK)
    c.line("M3.6,-4 H12.4", 0.6, P.BLUE)
    c.line("M7,-8.5 q-1,-1.5 0.5,-3 q1,-1.5 0,-3", 0.5, P.METAL, 0.8)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def newspaper(x: float, y: float, k: float) -> str:
    """A folded morning paper held by its lower edge: the front page with its masthead bar, a picture and columns of
    print."""
    c = Canvas()
    c.shape("M-1,2 V-18 H15 V2 Z", P.CARD, sw=0.6, light=None)
    c.add(f'<rect x="1" y="-16.4" width="12" height="2.6" fill="{INK}" fill-opacity=".75"/>')
    c.add(f'<rect x="1" y="-12" width="6" height="5" fill="{P.METAL}" stroke="{INK}" stroke-width=".3"/>')
    c.line("M8,-11.6 H13 M8,-9.6 H13 M8,-7.6 H12 M1,-5 H13 M1,-3 H13 M1,-1 H10", 0.45, INK, 0.55)
    c.line("M15,2 L16.5,1 V-17 L15,-18", 0.5, INK)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def letters(x: float, y: float, k: float) -> str:
    """A bundle of letters held by their corner: envelopes fanned out, each with its flap, one with a stamp."""
    c = Canvas()
    for q, t in enumerate((-14, -2, 10)):
        c.add(f'<g transform="rotate({t})"><rect x="-1" y="-10" width="16" height="10.5" fill="'
              f'{(P.WHITE, P.CARD, mix(P.SKY, P.WHITE, 0.6))[q]}" stroke="{INK}" stroke-width=".5"/><path d="M-1,-10 '
              f'L7,-4.6 L15,-10" fill="none" stroke="{INK}" stroke-width=".4"/></g>')
    c.add(f'<g transform="rotate(10)"><rect x="10.6" y="-9" width="3" height="3.4" fill="{P.RED}"/></g>')
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def letter_open(x: float, y: float, k: float) -> str:
    """An opened letter held up by its lower corner to be read: the sheet, unfolded, its folds and its handwriting."""
    c = Canvas()
    c.shape("M-1,2 V-20 H15 V2 Z", P.WHITE, sw=0.6, light=None)
    c.line("M-1,-13 H15 M-1,-6 H15", 0.4, P.METAL, 0.8)
    c.line(" ".join(f"M2,{n(-17 + q * 2.6)} q3,-1 6,0 t5,0" for q in range(7)), 0.45, P.PEN, 0.8)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def handbook(x: float, y: float, k: float) -> str:
    """A fresh copy of the handbook held up by the lower end of its spine, its cover to the viewer."""
    c = Canvas()
    c.shape("M0,-17.6 H13.4 V-16 H0 Z", P.CARD, sw=0.4, light=None)
    cover_art(c, -1.6, -17, 15.6, 19.4, 0.6)
    c.shape(rounded_rect_d(-1.6, -17, 2.6, 19.4, 0.6), darken(SUN, 0.8), sw=0.45, light=None)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def hammer(x: float, y: float, k: float) -> str:
    """A claw hammer held by its wooden handle, its steel head up over the thumb, the claw behind."""
    c = Canvas()
    c.shape(rounded_rect_d(-1.3, -14, 2.6, 22, 1), P.WOOD, sw=0.5, light=None)
    c.shape("M-1.6,-17.6 H6 Q7,-17.6 7,-16.4 V-13.6 Q7,-12.4 6,-12.4 H-1.6 Z", P.METAL_DARK, sw=0.5, light=None)
    c.shape("M-1.6,-17.6 Q-6,-18 -8,-14 L-6.6,-13.4 Q-5,-15.6 -1.6,-14.6 Z", P.METAL_DARK, sw=0.5, light=None)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def brush(x: float, y: float, k: float) -> str:
    """A flat paint brush held by its handle: the wooden handle, the steel ferrule, the bristles wet with white paint
    pointing ahead of the knuckles."""
    c = Canvas()
    c.shape(rounded_rect_d(-6, -1.4, 9, 2.8, 1.2), P.WOOD, sw=0.45, light=None)
    c.shape(rounded_rect_d(3, -1.8, 4, 3.6, 0.4), P.METAL, sw=0.45, light=None)
    c.shape("M7,-1.8 H11 L12,-1 V1 L11,1.8 H7 Z", P.WHITE, sw=0.45, light=None)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def compass(x: float, y: float, k: float) -> str:
    """A brass pocket compass in the palm, its lid open: the white dial, the red and blue needle, the ring."""
    c = Canvas()
    c.shape("M-1,-1 Q-1,-9 7,-9 Q15,-9 15,-1 Z", mix(P.GOLD, P.AMBER, 0.3), sw=0.5, light=None)
    c.add(f'<circle cx="7" cy="1" r="6" fill="{mix(P.GOLD, P.AMBER, 0.3)}" stroke="{INK}" stroke-width=".6"/>'
          f'<circle cx="7" cy="1" r="4.4" fill="{P.CARD}" stroke="{INK}" stroke-width=".4"/>'
          f'<path d="M7,1 L8,-2.6 L6,-2.6 Z" fill="{P.RED}"/><path d="M7,1 L8,4.6 L6,4.6 Z" fill="{P.BLUE}"/>')
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def biscuits(x: float, y: float, k: float) -> str:
    """A plate of round biscuits held out by its rim."""
    c = Canvas()
    c.add(f'<ellipse cx="10" cy="0" rx="11" ry="2.4" fill="{P.WHITE}" stroke="{INK}" stroke-width=".5"/>')
    for bx, by in ((5, -1.6), (10, -2.4), (15, -1.6), (7.5, -4), (12.5, -4)):
        c.add(f'<circle cx="{bx}" cy="{by}" r="2.6" fill="{P.CRUST}" stroke="{INK}" stroke-width=".4"/>'
              f'<circle cx="{bx - 0.6}" cy="{by - 0.4}" r=".4" fill="{P.WOOD_DARK}"/>')
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def thermos(x: float, y: float, k: float) -> str:
    """A steel thermos flask held round its middle: the cup-lid on top, its shoulder, a band, the gleam."""
    c = Canvas()
    c.shape(rounded_rect_d(-3, -16, 8, 22, 2), P.METAL_LIGHT, sw=0.5, light=(-0.4, 0))
    c.shape(rounded_rect_d(-3.6, -20, 9.2, 5, 1.2), P.RED, sw=0.5, light=None)
    c.line("M-3,-4 H5", 0.8, P.METAL_DARK)
    c.line("M-1,-13 V3", 0.8, P.WHITE, 0.7)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def grip_offset(s: Strip, name: str, pose: str, face: int, tall: float | None = None) -> tuple[float, float]:
    """Where a character's right fist closes relative to its feet, standing in this frame, facing `face`."""
    probe = Stage()
    who = probe.actor(name, 0.0, 0.0, pose, "smile", flip=face < 0, tall=tall or s.tall * SIZE[name])
    gx, gy, _ = probe.grip(who, "right")
    return gx, gy


def stand(s: Strip, name: str, x: float, pose: str, face: int, mood: str = "smile", feet: float | None = None,
          group: str | None = None, depth: float | None = None):
    """A character on the floor at x, facing `face` (1 right, -1 left)."""
    feet = lane(s).feet if feet is None else feet
    pose = pose if pose in characters.module(name).POSES else "present"
    return s.actor(name, x, feet, pose, mood, flip=face < 0, tall=s.tall * SIZE[name], group=group or name,
                   depth=depth)


def fits(s: Strip, name: str, x: float, air: float = 3, ignore: tuple[str, ...] = (),
         solid: tuple[str, ...] = ()) -> bool:
    """A character standing at x is whole in the frame and clear of everything placed so far."""
    b = _box(s, name, x, lane(s).feet)
    if b[0] < s.lo - 4 or b[2] > s.hi + 4 or b[1] < 2:
        return False
    behind = lane(s).feet - IN_FRONT                                   # furniture a step behind: stand in front
    return (not any(o.hits(b, air) for o in s.boxes
                    if o.group not in ignore
                    and not (o.kind == "backdrop" and o.bottom <= behind and o.group not in solid))
            and not any(o for o in s.reserved if b[0] < o[2] and b[2] > o[0] and b[1] < o[3] and b[3] > o[1]))


def lift(s: Strip) -> float:
    """How far behind the cast a moment's furniture stands in a tall frame: a step back, so the cast - big, half the
    frame's height - may stand in front of it, as people stand before a table in a photograph; nothing in a strip."""
    return float(IN_FRONT + 4) if s.h >= 450 else 0.0


def place_(s: Strip, c: Canvas, box: tuple, name: str) -> tuple:
    """`place`, for furniture that may stand a step behind the cast (`lift`): then it is put as furniture the cast
    may stand in front of."""
    if not lift(s):
        return place(s, c, box, name)
    svg = c.render()
    if getattr(s, "mirror", False):
        svg = f'<g transform="translate({n(s.lo + s.hi)},0) scale(-1,1)">{svg}</g>'
        box = (fx(s, box[2]), box[1], fx(s, box[0]), box[3])
    s.put(box[3] - 1, svg, box, name, group=name, backdrop=True)
    return box


def join(s: Strip, name: str, near: float, pose: str, face: int, mood: str = "smile", hold=None, tilt=None,
         solid: tuple[str, ...] = ()):
    """One more of the cast at the free spot nearest to x = `near`; None when there is none. `solid`: furniture
    standing a step behind that the character must still not stand in front of."""
    for dx in sorted(range(-400, 401, 6), key=abs):
        x = near + dx
        if fits(s, name, x, solid=solid):
            who = stand(s, name, x, pose, face, mood)
            if hold is not None:
                if tilt is None:
                    held(s, who, hold)
                else:
                    upright(s, who, hold, tilt)
            return who
    return None


def fx_(s: Strip, f: float) -> float:
    """A place across the frame, read from the side the moment faces: mirrored on a mirrored page."""
    x = s.x(f)
    return fx(s, x)


def way(s: Strip) -> int:
    return -1 if getattr(s, "mirror", False) else 1


# ============================================================================ the things of the moments
def ream(c: Canvas, x: float, y: float, w: float = 26, h: float = 7) -> None:
    """A ream of paper lying at (x, y) (its bottom's middle): the paper wrapper with its coloured band, one end
    torn open on the edges of the white sheets."""
    c.shape(rounded_rect_d(x - w / 2, y - h, w, h, 0.8), mix(P.CARD, P.SKY, 0.3), sw=0.9, light=None)
    c.add(f'<rect x="{n(x - w * 0.1)}" y="{n(y - h + 0.45)}" width="{n(w * 0.2)}" height="{n(h - 0.9)}" '
          f'fill="{P.BLUE}"/>')
    c.shape(f"M{n(x + w / 2 - 7)},{n(y - h)} l2,1.6 l-1.2,1.6 l2,1.4 l-1,1.8 l1.6,{n(h - 6.4)} H{n(x + w / 2)} "
            f"V{n(y - h)} Z", P.WHITE, sw=0.7, light=None)
    c.line(" ".join(f"M{n(x + w / 2 - 4.6)},{n(y - h + 1 + q * 1.1)} H{n(x + w / 2 - 0.6)}"
                    for q in range(int(h - 1.5))), 0.3, P.METAL_DARK)


def lying_copy(c: Canvas, x: float, y: float, w: float = 22, h: float = 3.4) -> None:
    """A copy of the handbook lying flat, its spine to the viewer: the yellow spine, the pink band at its head, a
    cream title label, the page block's edge."""
    c.shape(rounded_rect_d(x - w / 2, y - h, w, h, 0.8), SUN, sw=0.7, light=None)
    c.add(f'<rect x="{n(x - w / 2 + 0.4)}" y="{n(y - h + 0.4)}" width="{n(w * 0.16)}" height="{n(h - 0.8)}" '
          f'fill="{P.PINK}"/><rect x="{n(x - w * 0.12)}" y="{n(y - h * 0.72)}" width="{n(w * 0.38)}" '
          f'height="{n(h * 0.44)}" fill="{P.PAPER}"/>')


def workbench(c: Canvas, x: float, foot: float, k: float, beat: str, awning: bool) -> dict:
    """The garden workbench at (x, foot) in the professor's units, 110 wide, its top at 48 - his hip: a top of two
    thick planks on four square legs with a stretcher and a shelf; on the shelf two wrapped reams of paper; on the
    top the printer - its paper standing in the tray at its back, the control panel with its little screen and
    green light, the output slot - with a fresh copy of the book sliding out cover up onto its tray (`beat`
    "print"), a stack of fresh copies and one copy stood up to show its cover. Over it (`awning`) a striped awning
    on two poles, its scalloped valance. Returns its box and the points the cast reaches for."""
    d = Canvas()
    d.add(f'<ellipse cx="0" cy="0" rx="60" ry="3" fill="{INK}" fill-opacity=".14"/>')
    for lx in (-50, 46):
        d.shape(rounded_rect_d(lx, -45, 4, 45, 0.6), P.WOOD_DARK, sw=1.1, light=None)
    d.shape(rounded_rect_d(-50, -16, 100, 3, 0.6), P.WOOD, sw=1, light=None)                  # the shelf
    for q in range(3):                                                        # more copies on the shelf
        lying_copy(d, -26, -16 - q * 3.6, 24 - (q % 2), 3.4)
        lying_copy(d, 8, -16 - q * 3.6, 23 + (q % 2), 3.4)
    ream(d, 32, -16, 18, 6)
    d.shape(rounded_rect_d(-56, -50, 112, 6, 1.2), P.WOOD, sw=1.3, light=None)                 # the top
    d.line("M-56,-47 H56", 0.6, darken(P.WOOD, 0.7))
    d.line("M-50,-48.6 q8,-1 16,0 t16,0 M10,-46 q8,-1 16,0 t16,0", 0.5, darken(P.WOOD, 0.75), 0.7)
    if awning:
        for px in (-60, 60):
            d.shape(rounded_rect_d(px - 1.6, -116, 3.2, 116, 1), P.WOOD_DARK, sw=1, light=None)    # the poles
        top, edge = -122, -110
        d.shape(f"M-66,{edge} L-62,{top} H62 L66,{edge} Z", P.WHITE, sw=1.2, light=None)
        stripes = " ".join(f"M{n(-66 + q * 13.2)},{edge} L{n(-62 + q * 12.4)},{top} h6.2 "
                           f"L{n(-59.4 + q * 13.2)},{edge} Z"
                           for q in range(10))
        d.add(f'<path d="{stripes}" fill="{SUN}"/>')
        d.path(f"M-66,{edge} L-62,{top} H62 L66,{edge} Z", "none", 1.2)
        val = " ".join(f"M{n(-66 + q * 13.2)},{edge} q3.3,8 6.6,0 Z" for q in range(10))
        val2 = " ".join(f"M{n(-59.4 + q * 13.2)},{edge} q3.3,8 6.6,0 Z" for q in range(10))
        d.add(f'<path d="{val}" fill="{SUN}" stroke="{INK}" stroke-width=".8"/>'
              f'<path d="{val2}" fill="{P.WHITE}" stroke="{INK}" stroke-width=".8"/>')         # the valance
    # the printer
    px, py = -24, -50
    d.shape(f"M{px - 14},{py - 16} L{px - 10},{py - 30} H{px + 8} L{px + 10},{py - 16} Z", P.WHITE, sw=0.8,
            light=None)                                                                          # paper in its tray
    d.line(" ".join(f"M{px - 11 + q * 0.4},{py - 18 - q * 3} H{px + 8.4 - q * 0.2}" for q in range(4)), 0.3,
           P.METAL_DARK)
    d.shape(rounded_rect_d(px - 20, py - 18, 40, 18, 3), mix(P.METAL_PALE, P.WHITE, 0.4), sw=1.2,
            light=(-1, -1))                                                                      # the body
    d.shape(rounded_rect_d(px - 20, py - 18, 40, 5, 2.5), P.METAL_LIGHT, sw=0.9, light=None)  # its lid
    d.shape(rounded_rect_d(px + 6, py - 12, 11, 6, 1), P.CHARCOAL, sw=0.6, light=None)        # the panel
    d.add(f'<rect x="{px + 7.2}" y="{py - 11}" width="5" height="4" rx=".5" fill="{P.SCREEN_LIGHT}"/>'
          f'<circle cx="{px + 14.6}" cy="{py - 9}" r="1.1" fill="{P.GREEN}"/>')
    d.shape(rounded_rect_d(px - 16, py - 6.4, 22, 2.2, 1), P.CHARCOAL, sw=0.5, light=None)    # the slot
    d.shape(f"M{px - 17},{py - 2} H{px + 7} L{px + 10},{py} H{px - 20} Z", P.METAL, sw=0.7, light=None)  # tray
    if beat == "print":                                                       # a copy sliding out, cover up
        d.add(f'<g transform="translate({px - 13},{py - 4.4}) skewX(-28)">')
        cover_art(d, 0, -9, 15, 9, 0.5)
        d.add("</g>")
    for q in range(4):                                                        # the stack of fresh copies
        lying_copy(d, 18, -50 - q * 3.6, 24 - (q % 2), 3.4)
    d.add('<g transform="translate(40,-50) rotate(-8)">')                    # one stood up, its cover out
    d.shape("M0,0 v-21 h2.4 v21 Z", P.CARD, sw=0.4, light=None)
    cover_art(d, 1.6, -21, 14, 21, 0.6)
    d.add("</g>")
    c.add(_at(d, x, foot, k))
    top = 122 if awning else 74
    return {"box": (x - (68 if awning else 57) * k, foot - top * k, x + (68 if awning else 57) * k, foot),
            "printer": (x + (px - 6) * k, foot - 54 * k), "stack": (x + 18 * k, foot - 64 * k)}


def toolbox(c: Canvas, x: float, foot: float, k: float) -> None:
    """A carpenter's open toolbox on the paving at (x, foot), 40 wide: a wooden tray with sloping ends and a dowel
    handle across, and in it a panel saw - its wooden grip and toothed blade - a steel square, a screwdriver and,
    on the rim, a yellow tape measure; beside it a tin of nails."""
    d = Canvas()
    d.add(f'<ellipse cx="0" cy="0" rx="26" ry="2" fill="{INK}" fill-opacity=".14"/>')
    d.shape("M-15,-11 L3,-34 L8,-33 L-9,-10 Z", P.METAL_LIGHT, sw=0.8, light=None)             # the saw's blade
    d.line(" ".join(f"M{n(-14 + q * 1.8)},{n(-12 - q * 2.3)} l1.4,0.9" for q in range(9)), 0.4, INK)
    d.shape("M2,-36 Q8,-42 13,-37 L8,-31 Q6,-35 4,-33 Z", P.WOOD, sw=0.8, light=None)          # its grip
    d.shape("M6,-10 V-26 H8.6 V-12 H16 V-10 Z", P.METAL, sw=0.6, light=None)                  # the square
    d.shape(rounded_rect_d(-4.5, -29, 3, 9, 1.2), P.RED, sw=0.6, light=None)                  # the screwdriver
    d.line("M-3,-20 V-12", 1, P.METAL_DARK)
    d.shape("M-20,0 V-12 L-18,-22 H-15 L-14,-12 H14 L15,-22 H18 L20,-12 V0 Z", P.WOOD, sw=1.1, light=(-0.6, -0.6))
    d.line("M-18,-6 H18", 0.5, darken(P.WOOD, 0.7))
    d.line("M-16.5,-20 H16.5", 2.2, P.WOOD_DARK)                                                  # the handle
    d.add(f'<circle cx="14" cy="-13" r="4" fill="{SUN}" stroke="{INK}" stroke-width=".7"/>'
          f'<circle cx="14" cy="-13" r="1.4" fill="{P.CHARCOAL}"/>')                            # the tape
    d.shape(rounded_rect_d(24, -9, 9, 9, 1), P.METAL_LIGHT, sw=0.7, light=None)               # the tin of nails
    d.line("M26,-9 l-0.6,-3.6 M28.5,-9 l0.4,-4 M31,-9 l1,-3.2", 0.7, P.METAL_DARK)
    c.add(_at(d, x, foot, k))


def paint_tin(c: Canvas, x: float, foot: float, k: float, brush_in: bool) -> None:
    """A tin of white paint on the paving at (x, foot), 11 tall: the tin with its label band and wire handle, its
    lid leaning beside it, a drip down its side, and (`brush_in`) the brush laid across its rim."""
    d = Canvas()
    d.add(f'<ellipse cx="0" cy="0" rx="9" ry="1.4" fill="{INK}" fill-opacity=".14"/>')
    d.shape("M-6,0 V-11 H6 V0 Z", P.METAL_LIGHT, sw=0.8, light=(-0.6, 0))
    d.add(f'<rect x="-6" y="-8" width="12" height="4.4" fill="{P.CHAPTER_SKY}" stroke="{INK}" stroke-width=".4"/>')
    d.add(f'<ellipse cx="0" cy="-11" rx="6" ry="1.4" fill="{P.WHITE}" stroke="{INK}" stroke-width=".6"/>')
    d.line("M3,-11 v4", 1.2, P.WHITE)
    d.line("M-6,-10 Q0,-17 6,-10", 0.5, P.METAL_DARK)
    d.add(f'<ellipse cx="-10" cy="-5" rx="1.6" ry="5.6" fill="{P.METAL}" stroke="{INK}" stroke-width=".6"/>')  # lid
    if brush_in:
        d.add(f'<g transform="rotate(-8)">{brush(-2, -11.6, 1)}</g>')
    c.add(_at(d, x, foot, k))


def broken_picket(c: Canvas, x: float, foot: float, k: float) -> None:
    """The broken picket lying on the paving at (x, foot): snapped in two, the jagged ends, the old white paint
    flaking, a rusty nail sticking out."""
    d = Canvas()
    d.shape("M-30,0 V-4.6 H-6 l2,1.6 l-2,1.4 l2,1.6 Z", P.WHITE, sw=0.8, light=None)
    d.shape("M-3,-1 l2,-1.8 l-1.6,-1.4 l2,-1.4 L24,-8 L30,-6.2 L27,-2.6 Z", P.WHITE, sw=0.8, light=None)
    d.line("M-24,-2.6 h4 M10,-4.6 h5", 0.6, P.STONE)
    d.line("M-18,-4.6 l1,-3", 0.8, P.LEATHER)
    c.add(_at(d, x, foot, k))


def table_tea(c: Canvas, x: float, foot: float, k: float, cups: list[float], full: bool) -> dict:
    """A low garden table at (x, foot), 70 wide and 26 tall, under a checked cloth hanging in folds with a scalloped
    hem: on it cups on their saucers at `cups` (their middles, in its own units), the tea in them (`full`), a plate
    of round biscuits, a jar of jam with a cloth cap tied on, a sugar bowl and a little jug of flowers."""
    d = Canvas()
    d.add(f'<ellipse cx="0" cy="0" rx="40" ry="2.6" fill="{INK}" fill-opacity=".14"/>')
    for lx in (-30, 27):
        d.shape(rounded_rect_d(lx, -18, 3, 18, 0.6), P.WOOD_DARK, sw=0.9, light=None)
    cloth = "M-37,-26 H37 L39,-12 q-4,3 -7.8,0 q-3.9,3 -7.8,0 q-3.9,3 -7.8,0 q-3.9,3 -7.8,0 q-3.9,3 -7.8,0 " \
            "q-3.9,3 -7.8,0 q-3.9,3 -7.8,0 q-3.9,3 -7.8,0 q-3.9,3 -7.8,0 q-3.9,3 -8,0 Z"
    clip = d.shape(cloth, P.WHITE, sw=0, light=None, clip=True)
    checks = " ".join(f"M{n(q)},-27 V-8" for q in range(-36, 40, 5)) + " " + \
             " ".join(f"M-40,{n(y)} H40" for y in (-23.5, -18.5, -13.5))
    d.add(f'<g clip-path="url(#{clip})"><path d="{checks}" stroke="{P.PINK}" stroke-width="2.2" '
          f'stroke-opacity=".55"/></g>')
    d.path(cloth, "none", 1)
    d.line("M-22,-24 q1,6 -1,12 M8,-24 q-1,6 1,12 M28,-24 q2,6 0,11", 0.5, P.METAL, 0.8)        # its folds
    top = -26
    for cx in cups:
        d.add(f'<ellipse cx="{n(cx)}" cy="{top - 0.6}" rx="6" ry="1.3" fill="{P.WHITE}" stroke="{INK}" '
              f'stroke-width=".55"/>')
        d.shape(f"M{n(cx - 3.6)},{top - 6.4} H{n(cx + 3.6)} Q{n(cx + 3.6)},{top - 1.4} {n(cx)},{top - 1} "
                f"Q{n(cx - 3.6)},{top - 1.4} {n(cx - 3.6)},{top - 6.4} Z", P.WHITE, sw=0.55, light=None)
        d.line(f"M{n(cx + 3.4)},{top - 5.4} q2.4,0.4 1.2,2.8 q-0.6,0.6 -1.8,0.4", 0.55, INK)
        d.line(f"M{n(cx - 3.5)},{top - 4.4} H{n(cx + 3.5)}", 0.6, P.BLUE)
        if full:
            d.add(f'<ellipse cx="{n(cx)}" cy="{top - 6.4}" rx="3.6" ry=".8" fill="{mix(P.ORANGE, P.WOOD_DARK, 0.5)}"/>')
    things = [(-18, "biscuits"), (6, "jam"), (22, "jug")]
    for tx, kind in things:
        if any(abs(tx - cx) < 9 for cx in cups):
            continue
        if kind == "biscuits":
            d.add(f'<ellipse cx="{tx}" cy="{top - 0.8}" rx="9" ry="1.8" fill="{P.WHITE}" stroke="{INK}" '
                  f'stroke-width=".5"/>')
            for bx, by in ((-4.5, -2.4), (0, -2.8), (4.5, -2.4), (-2.2, -4.8), (2.2, -4.8)):
                d.add(f'<circle cx="{tx + bx}" cy="{top + by}" r="2.3" fill="{P.CRUST}" stroke="{INK}" '
                      f'stroke-width=".4"/>')
        elif kind == "jam":
            d.shape(f"M{tx - 3.6},{top} V{top - 7} H{tx + 3.6} V{top} Z", P.RED, sw=0.6, light=None)
            d.add(f'<rect x="{tx - 3}" y="{top - 6}" width="1.2" height="5" fill="{P.WHITE}" fill-opacity=".5"/>')
            d.shape(f"M{tx - 4.6},{top - 7} L{tx - 3.4},{top - 9.6} H{tx + 3.4} L{tx + 4.6},{top - 7} Z",
                    P.WHITE, sw=0.5, light=None)
            d.line(f"M{tx - 4},{top - 8} H{tx + 4}", 0.5, P.PINK)
            d.add(f'<rect x="{tx - 2.4}" y="{top - 5}" width="4.8" height="2.6" fill="{P.CARD}" stroke="{INK}" '
                  f'stroke-width=".3"/>')
        else:
            d.shape(f"M{tx - 3},{top} Q{tx - 4.4},{top - 5} {tx - 2},{top - 7} H{tx + 2} Q{tx + 4.4},{top - 5} "
                    f"{tx + 3},{top} Z", mix(P.SKY, P.BLUE, 0.4), sw=0.55, light=None)
            d.line(f"M{tx - 1},{top - 7} l-3,-6 M{tx},{top - 7} v-8 M{tx + 1},{top - 7} l3,-6", 0.6, P.LEAF_DARK)
            for fx0, fy0, col in ((-4, -13, SUN), (0, -15.4, P.WHITE), (4, -13, P.PINK)):
                d.add(f'<circle cx="{tx + fx0}" cy="{top + fy0}" r="1.8" fill="{col}" stroke="{INK}" '
                      f'stroke-width=".4"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 40 * k, foot - 44 * k, x + 40 * k, foot), "top": foot + top * k}


def bench(c: Canvas, x: float, foot: float, k: float, seat: float = 26) -> dict:
    """The garden bench at (x, foot), 84 wide, its seat at `seat` - a seated professor's knee: three yellow slats in
    the back, three in the seat, on cast-iron ends with their scrolls and arms. Returns its box and its seat line."""
    d = Canvas()
    d.add(f'<ellipse cx="0" cy="0" rx="46" ry="2.4" fill="{INK}" fill-opacity=".14"/>')
    for ex in (-38, 38):
        s_ = 1 if ex > 0 else -1
        d.line(f"M{ex - s_ * 4},0 Q{ex},{-seat * 0.5} {ex},{-seat} M{ex + s_ * 4},0 Q{ex},{-seat * 0.5} {ex},{-seat} "
               f"M{ex},{-seat} L{ex - s_ * 2},{-seat - 26}", 2.6, P.CHARCOAL)
        d.line(f"M{ex - s_ * 2},{-seat - 12} q{s_ * 6},-2 {s_ * 8},4", 2.2, P.CHARCOAL)          # the arm
        d.add(f'<circle cx="{ex + s_ * 6}" cy="{-seat - 8}" r="1.6" fill="none" stroke="{P.CHARCOAL}" '
              f'stroke-width="1.4"/>')
    for q in range(3):
        d.shape(rounded_rect_d(-42, -seat - 26 + q * 7, 84, 4.6, 1.4), PAINT, sw=0.9, light=None)  # the back
    for q in range(3):
        d.shape(rounded_rect_d(-42 - q * 0.6, -seat - 1.5 + q * 1.6, 84 + q * 1.2, 2.6, 1), PAINT, sw=0.8,
                light=None)                                                                      # the seat
    c.add(_at(d, x, foot, k))
    return {"box": (x - 47 * k, foot - (seat + 28) * k, x + 47 * k, foot), "seat": foot - seat * k}


def map_sheet(c: Canvas, x: float, y: float, k: float) -> None:
    """The road map spread on the bench's seat at (x, y), its near half hanging over the front edge: the paper with
    its folds, a river, two woods, and a dashed route from a little house to a flag."""
    d = Canvas()
    d.shape("M-30,0 L-27,-4 H27 L30,0 L29,18 Q0,20 -29,18 Z", P.CARD, sw=0.8, light=None)
    d.line("M-10,-4 L-10,18.6 M10,-4 L10,18.6 M-29.6,8 H29.6", 0.4, P.METAL, 0.9)
    d.line("M-28,12 C-16,4 -6,16 6,8 S22,2 28,6", 2, mix(P.SKY, P.BLUE, 0.4))
    for cx, cy in ((-18, 2), (16, 14)):
        for q in range(3):
            d.add(f'<circle cx="{cx + q * 3}" cy="{cy + (q % 2) * 1.6}" r="2" fill="{P.GREEN}" stroke="{INK}" '
                  f'stroke-width=".3"/>')
    d.add(f'<path d="M-24,15 C-14,8 -4,0 4,4 S18,12 24,-1" fill="none" stroke="{P.RED}" stroke-width="1" '
          f'stroke-dasharray="2 1.6"/>')
    d.shape("M-27,16 v-3 l2,-2 l2,2 v3 Z", SUN, sw=0.4, light=None)
    d.line("M24,-1 v-6", 0.6, INK)
    d.shape("M24,-7 l4,1.4 l-4,1.4 Z", P.RED, sw=0.3, light=None)
    c.add(_at(d, x, y, k))


def rucksack(c: Canvas, x: float, foot: float, k: float, color: str, packed: bool, seed: int = 0) -> None:
    """A walking rucksack standing on the paving at (x, foot), 26 wide and 36 tall: the canvas body with its haul
    loop, the shoulder strap curving down its side, the front pocket with its zip, a side pocket with a bottle, and
    the top flap - buckled down with two straps and a rolled mat strapped on top (`packed`), or thrown back behind
    it, its straps hanging loose, the collar pulled up and open, and going in a map tube, a torch or a jumper."""
    d = Canvas()
    dark = darken(color, 0.72)
    d.add(f'<ellipse cx="0" cy="0" rx="15" ry="1.8" fill="{INK}" fill-opacity=".16"/>')
    if not packed:                                                    # the flap thrown back behind it
        d.shape("M-11,-33 Q-13,-44 -4,-47 H6 Q13,-44 11,-33 Z", dark, sw=0.9, light=None)
    d.line("M-10,-31 Q-19,-17 -12,-3", 4.2, INK)
    d.line("M-10,-31 Q-19,-17 -12,-3", 2.8, dark)                                              # the shoulder strap
    d.shape(rounded_rect_d(-17.6, -14, 4, 3, 0.6), P.METAL_DARK, sw=0.4, light=None)          # its buckle
    d.shape("M-12,0 Q-14,-18 -11,-30 Q-9,-36 0,-36 Q9,-36 11,-30 Q14,-18 12,0 Z", color, sw=1.1, light=(-1, -1))
    d.shape("M11,-16 Q16,-16 16,-8 V-1 H10 Z", dark, sw=0.8, light=None)                       # side pocket
    d.shape(rounded_rect_d(11.6, -22, 3.6, 8, 1.2), mix(P.SKY, P.METAL_LIGHT, 0.4), sw=0.6, light=None)
    d.shape("M-8,-1 V-12 Q-8,-15 -5,-15 H5 Q8,-15 8,-12 V-1 Z", dark, sw=0.9, light=None)     # front pocket
    d.line("M-7,-12.6 Q0,-14.6 7,-12.6", 0.6, P.METAL_LIGHT)
    d.add(f'<circle cx="6" cy="-12.8" r=".9" fill="{P.METAL_LIGHT}"/>')
    if packed:
        d.shape(rounded_rect_d(-15, -43, 30, 8, 4), P.TEAL if seed % 2 == 0 else P.ORANGE, sw=0.9, light=None)
        d.line("M-11,-43 v8 M-8,-43 v8 M8,-43 v8 M11,-43 v8", 0.4, INK, 0.5)
        d.shape("M-12,-34 Q0,-40 12,-34 L11,-24 Q0,-27 -11,-24 Z", dark, sw=1, light=None)    # the flap
        for sx in (-5, 5):
            d.line(f"M{sx},-44 V-20", 1.6, P.CHARCOAL)
            d.shape(rounded_rect_d(sx - 1.6, -22, 3.2, 2.6, 0.5), P.METAL_DARK, sw=0.4, light=None)
        d.line("M-6,-44 Q0,-48 6,-44", 1.2, P.CHARCOAL)                                        # the haul loop
    else:                                                             # open: its collar up, things going in
        collar = mix(color, P.WHITE, 0.35)
        d.shape("M-9.5,-34 L-10,-43 Q0,-45.5 10,-43 L9.5,-34 Z", collar, sw=0.9, light=None)
        d.line("M-6,-35 l-0.6,-7 M-2,-35 v-8 M2,-35 v-8 M6,-35 l0.6,-7", 0.5, darken(collar, 0.75))
        d.add(f'<ellipse cx="0" cy="-43.4" rx="9.4" ry="2" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width=".7"/>')
        what = seed % 3                                               # what is going in, sticking out of its mouth
        if what == 0:                                                 # a rolled map in its tube
            d.shape("M-4,-43 L-9,-58 L-5,-59.4 L0,-43.6 Z", P.CARD, sw=0.8, light=None)
            d.shape("M-9.6,-57 L-10.6,-60.6 L-6,-62 L-5,-58.4 Z", P.RED, sw=0.7, light=None)
        elif what == 1:                                               # a torch, its lens up
            d.shape(rounded_rect_d(-3, -55, 6, 12, 1.4), SUN, sw=0.8, light=None)
            d.shape(rounded_rect_d(-4, -58, 8, 4, 1), P.METAL_LIGHT, sw=0.7, light=None)
            d.add(f'<ellipse cx="0" cy="-58" rx="3" ry=".8" fill="{P.YELLOW_PALE}" stroke="{INK}" stroke-width=".4"/>')
        else:                                                         # a folded jumper going in
            d.shape("M-7,-43 Q-8,-50 -2,-51 H5 Q9,-50 7,-43 Z", mix(P.PINK, P.RED, 0.3), sw=0.8, light=None)
            d.line("M-5,-46.6 H5 M-5,-44.6 H5", 0.6, darken(P.PINK, 0.7))
        for sx in (-5, 5):                                            # the flap's straps, loose
            d.line(f"M{sx},-33 V-26", 1.6, P.CHARCOAL)
            d.add(f'<rect x="{sx - 1.6}" y="-26.6" width="3.2" height="2.6" rx=".5" fill="none" '
                  f'stroke="{P.METAL_DARK}" stroke-width=".8"/>')
    c.add(_at(d, x, foot, k))


# ============================================================================ the moments: the street side
def mailbox_moment(s: Strip, beat: str) -> None:
    """The author page, at the gate: "post" - the mailbox's door open and its flag up, the professor takes his
    letters out, the cat brings his morning paper; "read" - the gate open, the flag down, the professor reads a
    letter on the pavement, the agent holds the rest of the post."""
    u = U(s)
    w = way(s)
    feet = lane(s).feet
    mid = (s.lo + s.hi) / 2                                # the gate, the mailbox and the two centred
    gx = fx_(s, 0.3) if low(s) else mid - w * 72 * u
    fence = street(s, gx, open_=beat == "read", seed=s.seed)
    gw = 52 * u
    mx = gx + w * (gw / 2 + 24 * u)
    c = Canvas()
    mailbox(c, mx, feet - 4 * u, u, open_=beat == "post", flag=beat == "post", way=w)
    box = (mx - 20 * u, feet - 78 * u, mx + 20 * u, feet - 2 * u)
    s.put(feet - 4, c.render(), box, "mailbox", group="mailbox")
    sparrow_on(s, gx - w * (gw / 2 + 6 * u), fence - 64 * u, "post")
    if beat == "post":
        dx, _ = grip_offset(s, "professor", "present", -w)
        door_x = mx + w * 21 * u
        who = stand(s, "professor", door_x - dx, "present", -w)
        upright(s, who, letters, tilt=-10)
        if not low(s):
            join(s, "cat", door_x + w * 70 * u, "present", -w, hold=newspaper, tilt=0)
        else:
            join(s, "cat", door_x + w * 60 * u, "present", -w, hold=newspaper, tilt=0)
    else:
        who = join(s, "professor", mx + w * 52 * u, "present", -w)
        upright(s, who, letter_open, tilt=0)
        join(s, "agent", mx + w * 110 * u, "present", -w, hold=letters, tilt=-10)


def library_moment(s: Strip, beat: str) -> None:
    """The licence, the book given away: "shelve" - the little free library's glass door open, the cat puts a copy
    on its shelf, the caterpillar in the open gate waves the reader in; "give" - the agent holds a copy out from the
    library, the cat in the gateway welcomes the reader."""
    u = U(s)
    w = way(s)
    feet = lane(s).feet
    gx = fx_(s, 0.66) if low(s) else (s.lo + s.hi) / 2 + w * 64 * u   # the library, the two and the gate centred
    fence = street(s, gx, open_=True, seed=s.seed + 1)
    gw = 52 * u
    lx = gx - w * (gw / 2 + 40 * u)
    lk = min(u, (feet - 3 * u - 4) / 104)
    up = lift(s)
    box = little_library(s, lx, feet - 3 * u - up, lk, open_=True)
    s.put(feet - 3 - up, "", box, "library", group="library", backdrop=bool(up))
    shelf = lx - w * 30 * u
    if beat == "shelve":
        dx, _ = grip_offset(s, "cat", "present", w)
        who = stand(s, "cat", shelf - dx, "present", w) if fits(s, "cat", shelf - dx) else \
            join(s, "cat", shelf - dx, "present", w)
        upright(s, who, handbook, tilt=0)
        if not low(s):
            s.actor("caterpillar", gx, fence + 3 * u, "wave", "smile", flip=w > 0,
                    tall=s.tall * SIZE["caterpillar"], group="caterpillar", depth=fence + 3 * u)
    else:
        if not low(s):
            s.actor("cat", gx, fence + 3 * u, "welcome", "smile", flip=False,
                    tall=s.tall * SIZE["cat"], group="cat", depth=fence + 3 * u)
        dx, _ = grip_offset(s, "agent", "present", w)
        who = join(s, "agent", lx - w * 30 * u - dx, "present", w)
        upright(s, who, handbook, tilt=0)
        if low(s):
            join(s, "cat", lx - w * 110 * u, "welcome", w)


# ============================================================================ the moments: the yard
def print_moment(s: Strip, beat: str) -> None:
    """The fresh version, at the workbench under its awning: "print" - a fresh copy sliding out of the printer, the
    caterpillar checks the stack against her list, the cat holds a copy up; "bring" - the agent carries an armful of
    copies to the professor, who holds one up to look at it."""
    s.mirror = False                                       # the printer and the covers read one way only
    u = U(s)
    w = way(s)
    feet = lane(s).feet
    up = lift(s)
    c = Canvas()
    k = u * (1.25 if low(s) else 0.92 if up else 1.0)
    awning = feet - up - 124 * k > 2
    shift = 0.08 if s.seed % 2 else 0.0                   # the next page of a beat: the camera a step along
    wb = workbench(c, s.x((0.44 if beat == "print" else 0.3) + shift), feet - 2 * u - up, k, beat,
                   awning and not low(s))
    box = place_(s, c, wb["box"], "bench")
    if beat == "print":
        join(s, "caterpillar", fx(s, wb["box"][2]) + w * 30 * u, "present", -w,
             hold=checklist(4))
        if not low(s):
            join(s, "cat", box[0] - 40 * u if w > 0 else box[2] + 40 * u, "present", w, hold=handbook, tilt=0)
    else:
        right = box[2] if w > 0 else box[0]
        join(s, "agent", right + w * 36 * u, "carry", w, solid=("bench",))
        who = join(s, "professor", right + w * 110 * u, "present", -w, solid=("bench",))
        upright(s, who, handbook, tilt=0)
    _ = box


def fence_moment(s: Strip, beat: str) -> None:
    """Making the book better together, at the back fence: "mend" - a gap in the pickets, the broken one on the
    paving, the agent holds a new picket in its place against the rails, the caterpillar nails it with her hammer,
    the sparrow brings a nail, the open toolbox and the paint tin by them; "paint" - the new picket nailed in,
    still raw wood, the cat paints it white with the brush, the agent looks on with the hammer."""
    u = U(s)
    w = way(s)
    feet = lane(s).feet
    c = s.back
    fence = feet - 18 * u
    s.yard = fence
    sky(c, fence - 30 * u, s.seed)
    kf = max(min(u * 0.42, (fence - 46 * u) / 130), min(u * 0.62, (fence - 46 * u - s.h * 0.2) / 150))
    far = Canvas()
    neighbours(far, fence - 44 * u, kf, s.seed)
    c.add(f'<g opacity=".92">{far.render()}</g>')
    lawn(c, fence - 46 * u, fence + 1, kf, s.seed)
    pk = u * 55 / 70
    step = 13 * pk
    tk = u * 1.25                                                       # the toolbox, big in front
    ax0, _ = grip_offset(s, "agent", "present", -w)
    full = s.h < 560                                                    # the tallest frames: the two and the toolbox
    if beat == "mend":
        reach = abs(ax0) + 2 * u + (92 * u if full else 30 * u)        # the agent's side, to the broken picket
        back_ = step + 62 * u + (94 * tk if full else 58 * tk)         # the hammer's side, to the tin
    else:
        reach = abs(ax0) + 2 * u + 92 * u if full else 90 * u
        back_ = step + 62 * u + 58 * tk if full else step + 80 * u
    mid = (s.lo + s.hi) / 2
    slot = mid + w * (back_ - reach) / 2                                # the whole moment centred in the frame
    x0 = slot - 400 * step
    while x0 < -20:
        x0 += step
    q0 = round((slot - x0) / step)
    x0 = slot - q0 * step                                      # the slot falls on the pickets' rhythm
    left, right = (slot - step * 1.5, slot + step * 0.5) if w > 0 else (slot - step * 0.5, slot + step * 1.5)
    pickets(c, x0 - 10 * step, W + 6, fence, pk, gap=(left + 6 * pk, right - 6 * pk))
    flowers(c, -6, W + 6, fence + 1, u * 0.7, s.seed + 4, avoid=(left - 4 * u, right + 4 * u))
    other = slot - w * step                                    # the second gap, between the picket and the hammer
    if beat == "paint":                                        # both new pickets in, raw wood, nailed on
        for px in (slot, other):
            c.shape(f"M{n(px - 4.6 * pk)},{n(fence)} V{n(fence - 60 * pk)} L{n(px)},{n(fence - 67 * pk)} "
                    f"L{n(px + 4.6 * pk)},{n(fence - 60 * pk)} V{n(fence)} Z", PAPER_RAW if px == slot else P.WHITE,
                    sw=1.0 * pk, light=None)
            c.add("".join(f'<circle cx="{n(px)}" cy="{n(fence - y * pk)}" r="{n(0.9 * pk)}" fill="{INK}"/>'
                          for y in (16, 48)))
    paving(c, fence + 2, s.h + 4, max(0.8, s.unit))
    veil(s)
    things = Canvas()
    cat_x = slot - w * (step + 30 * u)
    tb = cat_x - (32 * u + 36 * tk) if w > 0 else cat_x + 32 * u + 24 * tk
    agent_x = slot - ax0 + w * 2 * u
    if beat == "mend":
        toolbox(things, tb, feet + 2 * u, tk)
        boxes = [(tb - 22 * tk, feet - 34 * tk, tb + 34 * tk, feet + 2 * u)]
        if full:
            bx_ = agent_x + w * 64 * u
            broken_picket(things, bx_, feet + 3 * u, u * 0.9)
            tin = tb - 36 * tk if w > 0 else tb + 46 * tk
            paint_tin(things, tin, feet + 2 * u, tk, brush_in=True)
            boxes += [(bx_ - 28 * u, feet - 6 * u, bx_ + 28 * u, feet + 3 * u),
                      (tin - 11 * tk, feet - 12 * tk, tin + 7 * tk, feet + 2 * u)]
    else:
        paint_tin(things, slot - w * 8 * u, feet + 2 * u, u, brush_in=False)
        boxes = [(slot - w * 8 * u - 11 * u, feet - 12 * u, slot - w * 8 * u + 7 * u, feet + 2 * u)]
        if full:
            toolbox(things, tb, feet + 2 * u, tk)
            boxes.append((tb - 22 * tk, feet - 34 * tk, tb + 34 * tk, feet + 2 * u))
    s.put(feet + 2, things.render(), None)
    for b in boxes:
        s.put(feet + 2, "", sorted_box(b), "tools", group="tools")
    if beat == "mend":
        tall_a = s.tall * SIZE["agent"]
        ax, ay = grip_offset(s, "agent", "present", -w)
        agent = stand(s, "agent", agent_x, "present", -w, group="agent")
        fist_y = feet + ay

        def new_picket(x, y, kk, top=fence - 67 * pk - fist_y, bottom=fence - fist_y, half=4.6 * pk):
            d = Canvas()
            d.shape(f"M{n(-half)},{n(bottom)} V{n(top + 7 * pk)} L0,{n(top)} L{n(half)},{n(top + 7 * pk)} "
                    f"V{n(bottom)} Z", PAPER_RAW, sw=1.0 * pk, light=None)
            d.line(f"M{n(-half * 0.3)},{n(bottom - 4)} q1,{n((top - bottom) * 0.4)} 0,{n((top - bottom) * 0.8)}",
                   0.5 * pk, P.WOOD, 0.8)
            k_ = kk * 100 / (agent.bottom - agent.top)
            return f'<g transform="translate({n(x)},{n(y)}) scale({n(k_)})">{d.render()}</g>'
        upright(s, agent, new_picket, tilt=0)
        _ = tall_a
        cx_, cy_ = grip_offset(s, "caterpillar", "cheer", w)
        if fits(s, "caterpillar", cat_x):
            cater = stand(s, "caterpillar", cat_x, "cheer", w, mood="smile")
            upright(s, cater, hammer, tilt=40 * 1)
        if not low(s):
            sparrow_on(s, tb, feet - 20 * tk, "tools", pose="present")
            bird = next((b for b in s.boxes if b.name == "sparrow"), None)
            if bird is not None:
                mxp, myp = s.mouth(bird)                       # a big nail in its beak, head and point
                bh = bird.bottom - bird.top
                sd = -1 if bird.flip else 1
                ln, th = bh * 0.5, max(1.6, bh * 0.07)
                x0_, x1_ = mxp - sd * ln * 0.25, mxp + sd * ln * 0.75
                s.put(feet + 3, f'<path d="M{n(x0_)},{n(myp - th / 2)} L{n(x1_ - sd * th)},{n(myp - th / 2)} '
                      f'L{n(x1_)},{n(myp)} L{n(x1_ - sd * th)},{n(myp + th / 2)} L{n(x0_)},{n(myp + th / 2)} Z" '
                      f'fill="{P.METAL}" stroke="{INK}" stroke-width="{n(th * 0.3)}"/>'
                      f'<rect x="{n(x0_ - th * 0.6)}" y="{n(myp - th * 1.3)}" width="{n(th * 1.2)}" '
                      f'height="{n(th * 2.6)}" rx="{n(th * 0.3)}" fill="{P.METAL_DARK}" stroke="{INK}" '
                      f'stroke-width="{n(th * 0.3)}"/>', None)
    else:
        cx_, _ = grip_offset(s, "cat", "present", -w)
        cat = stand(s, "cat", slot + w * 10 * u - cx_, "present", -w)
        upright(s, cat, brush, tilt=0)
        if not low(s):
            if full:
                join(s, "agent", slot + w * 140 * u, "present", -w, hold=hammer, tilt=0)
            else:                                              # the tallest: the agent on the other side, close
                join(s, "agent", slot - w * (step + 40 * u), "present", w, hold=hammer, tilt=0)


def sorted_box(b: tuple) -> tuple:
    return (min(b[0], b[2]), min(b[1], b[3]), max(b[0], b[2]), max(b[1], b[3]))


def tea_moment(s: Strip, beat: str) -> None:
    """The thanks, tea by the cottage: "pour" - the professor pours from the teapot held by its handle, the tea
    running from its spout into a cup on the table, the cat holds out his cup, the sparrow on the bench's back;
    "sip" - the professor sits on the bench with his cup on its saucer, the agent brings the biscuits."""
    u = U(s)
    w = way(s)
    feet = lane(s).feet
    c = Canvas()
    if beat == "pour":
        px = fx_(s, 0.3 if not low(s) else 0.26)
        tilt = 38
        prof = stand(s, "professor", px, "present", w)
        gx, gy, _ = s.grip(prof, "right")
        kk = U(s)
        a = math.radians(tilt)
        sx_, sy_ = TEAPOT_SPOUT
        tip = (gx + w * (sx_ * math.cos(a) - sy_ * math.sin(a)) * kk, gy + (sx_ * math.sin(a) + sy_ * math.cos(a)) * kk)
        upright(s, prof, teapot, tilt=tilt)
        tx = tip[0] + w * 30 * u                                   # the table: a cup right under the spout
        cups = [-30 * w + 2 * w, 10 * w]
        up = lift(s)
        tb = table_tea(c, tx, feet - 2 * u - up, u, [-28 if w > 0 else 28, 12 if w > 0 else -12], full=True)
        cup_x = tx + (-28 if w > 0 else 28) * u
        top = tb["top"] - 6.4 * u
        s.put(feet - 2 - up, c.render(), tb["box"], "table", group="table", backdrop=bool(up))
        s.put(feet + 1, f'<path d="M{n(tip[0])},{n(tip[1])} Q{n(tip[0] + w * 1.4 * u)},{n((tip[1] + top) / 2)} '
              f'{n(cup_x)},{n(top)}" fill="none" stroke="{mix(P.ORANGE, P.WOOD_DARK, 0.45)}" '
              f'stroke-width="{n(1.4 * u)}" stroke-linecap="round"/>', None)
        _ = cups
        if not low(s):
            join(s, "cat", tb["box"][2] + 34 * u if w > 0 else tb["box"][0] - 34 * u, "present", -w, hold=cup,
                 tilt=0)
            bc = Canvas()
            bx = px - w * 70 * u
            bn = bench(bc, bx, feet - 4 * u, u)
            if s.free(bn["box"], 3) and bn["box"][0] > s.lo - 10 and bn["box"][2] < s.hi + 10:
                s.put(feet - 4, bc.render(), bn["box"], "bench", group="bench")
                sparrow_on(s, bx, bn["box"][1], "bench")
    else:
        bx = fx_(s, 0.3 if not low(s) else 0.28)
        bn = bench(c, bx, feet - 2 * u, u)
        s.put(feet - 3, c.render(), bn["box"], "bench", group="bench")
        sit = stand(s, "professor", bx - w * 2 * u, "sit", w, group="bench", depth=feet + 1)
        upright(s, sit, cup, tilt=0)
        t = Canvas()
        tx = bx + w * 94 * u
        up = lift(s)
        tb = table_tea(t, tx, feet - 2 * u - up, u, [-16 if w > 0 else 16], full=True)
        s.put(feet - 2 - up, t.render(), tb["box"], "table", group="table", backdrop=bool(up))
        join(s, "agent", tb["box"][2] + 30 * u if w > 0 else tb["box"][0] - 30 * u, "present", -w, hold=biscuits,
             tilt=0)


def pack_moment(s: Strip, beat: str) -> None:
    """The contents, ready for the road: "pack" - the rucksacks open on the paving, the agent puts the book in, the
    caterpillar ticks her list; "route" - the map spread on the bench, the thermos by it, the professor shows the
    way on it, the cat holds the compass; "ready" - the rucksacks buckled, mats rolled on top, the professor points
    the way, the cat waves."""
    u = U(s)
    w = way(s)
    feet = lane(s).feet
    if beat == "route":
        c = Canvas()
        bx = fx_(s, 0.42)
        up = lift(s)
        bn = bench(c, bx, feet - 2 * u - up, u)
        map_sheet(c, bx + 4 * u, bn["seat"] - 1.6 * u, u)
        d = Canvas()
        d.add(thermos(0, 0, 1))
        c.add(_at(d, bx - w * 30 * u, bn["seat"] - 2 * u - 6 * u, u))
        s.put(feet - 2 - up, c.render(), bn["box"], "bench", group="bench", backdrop=bool(up))
        join(s, "professor", (bn["box"][0] - 30 * u) if w > 0 else (bn["box"][2] + 30 * u), "present", w)
        if not low(s):
            join(s, "cat", (bn["box"][2] + 30 * u) if w > 0 else (bn["box"][0] - 30 * u), "present", -w,
                 hold=compass, tilt=0)
        return
    c = Canvas()
    packed = beat == "ready"
    x0 = fx_(s, 0.5 if not low(s) else 0.42)
    cols = (mix(P.GREEN, P.LEAF_DARK, 0.3), P.ORANGE, mix(P.BLUE, P.CHAPTER_SKY, 0.3))
    up = lift(s)
    for q in range(3 if not low(s) else 2):
        rucksack(c, x0 + w * (q - 1) * 36 * u, feet - 2 * u - up, u * 1.05, cols[q], packed, seed=q)
    if not packed:                                                    # waiting to go in: a rolled mat, the flask
        mx_ = x0 - w * 64 * u
        c.add(f'<g transform="translate({n(mx_)},{n(feet - 2 * u - up)}) scale({n(u)})">'
              f'<ellipse cx="0" cy="0" rx="14" ry="1.6" fill="{INK}" fill-opacity=".14"/>'
              f'<rect x="-12" y="-9" width="24" height="9" rx="4.5" fill="{P.TEAL}" stroke="{INK}" '
              f'stroke-width="1"/><path d="M-6,-9 v9 M6,-9 v9" stroke="{P.CHARCOAL}" stroke-width="1.4"/>'
              f'<circle cx="12" cy="-4.5" r="3.6" fill="{lighten(P.TEAL, 0.3)}" stroke="{INK}" stroke-width=".8"/>'
              f'</g>')
        c.add(f'<g transform="translate({n(mx_ - w * 22 * u)},{n(feet - 8 * u - up)}) scale({n(u * 0.9)})">'
              f'{thermos(0, 0, 1)}</g>')
    span = (min(x0 - 54 * u, x0 - w * 64 * u - w * 30 * u), feet - 50 * u - up,
            max(x0 + 54 * u, x0 - w * 64 * u - w * 30 * u), feet - up)
    s.put(feet - 2 - up, c.render(), span, "packs", group="packs", backdrop=bool(up))
    if packed:
        join(s, "professor", span[2] + 30 * u if w > 0 else span[0] - 30 * u, "pointer", w)
        if not low(s):
            join(s, "cat", span[0] - 30 * u if w > 0 else span[2] + 30 * u, "wave", w)
            sparrow_on(s, x0, feet - 50 * u, "packs")
    else:
        who = join(s, "agent", span[2] + 26 * u if w > 0 else span[0] - 26 * u, "present", -w)
        upright(s, who, handbook, tilt=0)
        if not low(s):
            join(s, "caterpillar", span[0] - 30 * u if w > 0 else span[2] + 30 * u, "present", w,
                 hold=checklist(5))


# the yard row's stretch behind each yard moment
VIEW = {"print": 760, "fence": 0, "tea": 480, "pack": 160, "engine": 1150, "editor": 560, "grill": 930}


def clean(s: Strip) -> bool:
    """Everything of a moment lies whole in its frame, clear of each other and of the page-number tag, the floor
    showing under every pair of feet."""
    if footer_conflicts(s):
        return False
    for b in s.boxes:
        if b.kind == "actor" and b.bottom > s.h * 0.88 + 0.5:
            return False
        if b.top < -0.5 or b.bottom > s.h + 0.5 or b.left < -0.5 or b.right > W + 0.5:
            return False
    return True


def _fitted(draw, scene):
    """A moment drawn as it is or mirrored by turns, the camera close - and stepped back, a little at a time, until
    the whole moment fits its frame (the cast is half a tall frame's height, so a wide moment needs room)."""
    def run(s: Strip, beat: str) -> None:
        index = getattr(s, "index_", 0)

        def attempt(fit: float) -> Strip:
            probe = Strip(s.h, s.seed, s.clear, s.look, s.words)
            probe.egg = getattr(s, "egg", None)
            probe.fit = fit
            probe.mirror = bool(s.seed % 2)
            scene(probe, index)
            probe.mirror = bool(s.seed % 2)
            draw(probe, beat)
            return probe

        best, boost = None, 1.0
        for _ in range(2):
            for fit in (1.0, 0.92, 0.85, 0.78, 0.72, 0.66, 0.6, 0.54):
                probe = attempt(fit * boost)
                if not clean(probe):
                    continue
                actors = [x for x in probe.boxes if x.kind == "actor" and x.name != "sparrow"]
                cast_ = len({x.name for x in actors})
                share = max((x.bottom - x.top) for x in actors) / s.h if actors else 1.0
                if best is None or cast_ > best[0] or (cast_ == best[0] and share > best[1]):
                    best = (cast_, share, probe)
                if cast_ >= (2 if s.h >= 200 else 1):              # two of the cast at least, where there is room
                    break
            # a tall frame whose cast came out small (no professor in it): the camera comes closer once
            if best is None or s.h < 300 or best[1] >= 0.42 or boost > 1:
                break
            boost = min(1.6, 0.5 / best[1])
        s.__dict__.update((best[2] if best else probe).__dict__)
    return run


def _remember(s: Strip, index: int) -> None:
    """The world's backdrop hook: only note the station - `_fitted` draws the backdrop with the moment."""
    s.index_ = index


def front_backdrop(s: Strip, index: int) -> None:
    """Behind a front moment: the camera, and for a yard moment its stretch of the yard; the street side and the
    back fence are drawn by their moments, round where they put the gate or the gap."""
    prepare(s)
    key = FRONT.stations[index].key
    if key in ("print", "tea", "pack"):
        yard(s, VIEW[key] + (s.seed % 2) * 60, s.seed)


def _framed(draw):
    """A moment drawn as it is or mirrored by turns."""
    def run(s: Strip, beat: str) -> None:
        s.mirror = bool(s.seed % 2)
        draw(s, beat)
    return run


FRONT.stations.extend([
    Station("gate", _fitted(mailbox_moment, front_backdrop), ("post", "read")),
    Station("print", _fitted(print_moment, front_backdrop), ("print", "bring")),
    Station("fence", _fitted(fence_moment, front_backdrop), ("mend", "paint")),
    Station("tea", _fitted(tea_moment, front_backdrop), ("pour", "sip")),
    Station("hand", _fitted(library_moment, front_backdrop), ("shelve", "give")),
    Station("pack", _fitted(pack_moment, front_backdrop), ("pack", "route", "ready")),
])
FRONT.backdrop = _remember
FRONT.alternate = True


def front_place(request: dict, words: dict, nth: int) -> tuple[int, str]:
    """Which moment a front page's footer shows: its station named in the locale (`worlds: front: pages:`) by a
    heading or the page's title found in its text - the last match wins, so a page whose lower section is about
    mending the book gets the fence - and its beat alternating with the page's place."""
    keys = [st.key for st in FRONT.stations]
    pages = words.get("pages") or {}
    text = f"{request.get('heads', '')} | {request.get('text', '')}".lower()   # headings may be set in capitals
    found, at = None, -1
    for phrase, key in pages.items():
        pos = text.rfind(str(phrase).lower())
        if pos > at and key in keys:
            found, at = key, pos
    index = keys.index(found) if found else keys.index("pack")
    beats = FRONT.stations[index].beats
    if found == "pack" or not found:                     # the contents run over pages: packing, the route, off
        # A longer contents goes round its beats again, so two pages in a row never show one moment.
        return index, beats[int(request.get("nth_in_chapter", nth)) % len(beats)]
    return index, beats[nth % len(beats)]


def cast(s: Strip, box: tuple, who: tuple[tuple, ...]) -> None:
    """The moment's cast beside its thing, each facing it, at one scale, at the first free spot along the path."""
    feet = lane(s).feet
    for name, side, pose, mood, hold in who:
        side = -side if getattr(s, "mirror", False) else side
        pose = pose if pose in characters.module(name).POSES else "present"
        first = beside(s, box, side, name)
        sweep = sorted((i / 40 for i in range(41)), key=lambda f: abs(f - first[0]))
        for f in (*first, *sweep):
            x = s.x(f)
            b = _box(s, name, x, feet)
            if b[0] >= 2 and b[2] <= W - 2 and b[1] >= 2 and fits(s, name, x):
                actor = s.actor(name, x, feet, pose, mood, flip=side > 0, tall=s.tall * SIZE[name], group=name)
                if hold is not None:
                    held(s, actor, hold)
                break


def pk(s: Strip, height_: float, share: float) -> float:
    """A thing `height_` tall standing `share` of the professor's height."""
    return height(s, "professor") * share / height_


# ============================================================================ the introduction's things
STEAM = mix(P.WHITE, P.METAL_PALE, 0.35)
BRASS = mix(P.GOLD, P.AMBER, 0.3)


def shadow(d: Canvas, x: float, y: float, rx: float) -> None:
    """A soft shadow on the ground under a thing standing at (x, y), `rx` wide each way."""
    d.add(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(rx)}" ry="{n(rx * 0.12)}" fill="{INK}" fill-opacity=".14"/>')


def garden_table(d: Canvas, half: float, top: float = 54) -> None:
    """A wooden garden table in local units, its foot's middle at the origin, `half` wide each way and `top` tall:
    a top of three planks with their grain and nail heads, its edge in shade, two crossed trestle legs under it with
    a stretcher between them, its shadow on the ground."""
    shadow(d, 0, 0, half * 0.9)
    for lx in (-half + 16, half - 16):
        d.line(f"M{lx - 10},0 L{lx + 8},{-top + 6} M{lx + 10},0 L{lx - 8},{-top + 6}", 4.4, INK)
        d.line(f"M{lx - 10},0 L{lx + 8},{-top + 6} M{lx + 10},0 L{lx - 8},{-top + 6}", 3, P.WOOD_DARK)
        d.add(f'<circle cx="{lx - 1}" cy="{n(-top * 0.45)}" r="1.4" fill="{P.METAL_DARK}"/>')   # the legs' bolt
    d.line(f"M{-half + 20},{n(-top * 0.42)} H{half - 20}", 3.2, INK)
    d.line(f"M{-half + 20},{n(-top * 0.42)} H{half - 20}", 2, P.WOOD_DARK)                    # the stretcher
    d.shape(rounded_rect_d(-half, -top, 2 * half, 7, 2), P.WOOD, sw=1.4, light=None)
    d.add(f'<rect x="{-half + 1}" y="{-top + 4.6}" width="{2 * half - 2}" height="1.8" fill="{darken(P.WOOD, 0.8)}"/>')
    third = 2 * half / 3
    grain = " ".join(f"M{n(-half + 4 + q * third)},{n(-top + 2.4 + (q % 2) * 1.4)} q{n(third * 0.3)},-1.2 "
                     f"{n(third * 0.6)},0 t{n(third * 0.3)},0" for q in range(3))
    d.line(grain, 0.6, darken(P.WOOD, 0.72), 0.7)                                            # the planks' grain
    d.line(" ".join(f"M{n(-half + q * third)},{-top} v7" for q in (1, 2)), 0.9, darken(P.WOOD, 0.7))
    d.add("".join(f'<circle cx="{n(-half + q * third + 3)}" cy="{-top + 3.5}" r=".7" fill="{INK}"/>'
                  for q in range(3)))


def toy_engine(running: bool) -> Canvas:
    """The toy steam engine, 80 wide and 70 tall to its chimney's top, standing on (0, 0): the base board with its
    screws, the firebox with its door and spirit burner, the brass boiler with its bands and rivets, the sight glass
    and the pressure gauge, the chimney, the whistle, the cylinder on its standard, the red flywheel on its bearing
    and the piston rod to its crank. `running`: the flame lit, the wheel a blur, steam puffing and drifting back."""
    d = Canvas()
    d.shape(rounded_rect_d(-40, -5, 80, 5, 1.5), P.WOOD_DARK, sw=1.2, light=None)              # the base board
    d.line("M-36,-3 q12,-1 24,0 t24,0", 0.5, darken(P.WOOD_DARK, 0.7))
    d.add("".join(f'<circle cx="{q}" cy="-2.5" r=".9" fill="{P.METAL_LIGHT}"/>' for q in (-37, 37)))
    d.shape(rounded_rect_d(-34, -21, 34, 16, 1.5), P.METAL_DARK, sw=1.2, light=None)          # the firebox
    d.line("M-32,-18 h30 M-32,-8 h30", 0.5, darken(P.METAL_DARK, 0.7))
    d.shape(rounded_rect_d(-26, -16, 16, 9, 1), P.CHARCOAL, sw=0.9, light=None)               # its door
    if running:
        d.shape("M-22,-7 q-2,-5 2,-8 q0,4 2,4 q2,-3 1,-6 q4,4 2,10 Z", P.ORANGE, sw=0.6, light=None)
        d.shape("M-19,-7 q-1,-3 1,-5 q1,3 2,5 Z", P.SUN, sw=0, light=None)
    d.shape(rounded_rect_d(-38, -39, 42, 18, 9), BRASS, sw=1.4, light=(-1, -1))              # the boiler
    d.add(f'<path d="M-34,-36 H0" stroke="{lighten(BRASS, 0.45)}" stroke-width="1.6" stroke-linecap="round"/>')
    d.line("M-28,-39 v18 M-6,-39 v18", 1.1, darken(BRASS, 0.7))                                  # its bands
    d.add("".join(f'<circle cx="{bx}" cy="{by}" r=".6" fill="{darken(BRASS, 0.6)}"/>'
                  for bx in (-28, -6) for by in (-36, -30, -24)))                                # rivets
    d.shape(rounded_rect_d(-2, -36, 3, 12, 1), mix(P.LENS, P.WHITE, 0.3), sw=0.7, light=None)  # the sight glass
    d.add(f'<rect x="-1.4" y="-30" width="1.8" height="5" fill="{P.WATER}"/>')
    d.shape(rounded_rect_d(-36, -66, 7, 28, 1), P.CHARCOAL, sw=1.2, light=None)              # the chimney
    d.shape(rounded_rect_d(-38.5, -70, 12, 5, 1.5), P.CHARCOAL, sw=1.2, light=None)
    d.shape(rounded_rect_d(-15, -46, 5, 8, 1), BRASS, sw=0.9, light=None)                     # the whistle
    d.add(f'<circle cx="-12.5" cy="-47" r="2.2" fill="{BRASS}" stroke="{INK}" stroke-width=".8"/>')
    d.add(f'<circle cx="-22" cy="-45" r="4" fill="{P.WHITE}" stroke="{INK}" stroke-width=".9"/>'   # the gauge
          f'<path d="M-22,-45 l2.4,-2" stroke="{P.RED}" stroke-width=".8"/>')
    d.line("M-22,-41 v2", 1, BRASS)
    d.shape(rounded_rect_d(7, -30, 5, 25, 1), P.METAL_DARK, sw=1, light=None)                 # the standard
    d.shape(rounded_rect_d(3, -37, 14, 9, 2.5), BRASS, sw=1.1, light=None)                    # the cylinder
    d.shape(rounded_rect_d(25, -24, 5, 19, 1), P.METAL_DARK, sw=1, light=None)                # the bearing post
    wx, wy, r = 27.5, -26.0, 12.0
    crank = (wx + 6, wy - 3) if running else (wx - 5, wy + 4)
    d.line(f"M17,-32.5 L{crank[0]},{crank[1]}", 1.6, P.METAL_DARK)                              # the piston rod
    spokes = " ".join(f"M{wx},{wy} l{n(r * 0.86 * math.cos(math.radians(a)))},"
                      f"{n(r * 0.86 * math.sin(math.radians(a)))}" for a in range(15, 360, 60))
    d.add(f'<circle cx="{wx}" cy="{wy}" r="{r}" fill="none" stroke="{INK}" stroke-width="5"/>'
          f'<circle cx="{wx}" cy="{wy}" r="{r}" fill="none" stroke="{P.RED}" stroke-width="3"/>')  # the flywheel
    d.line(spokes, 1.4, darken(P.RED, 0.8), 0.45 if running else 1)
    d.add(f'<circle cx="{wx}" cy="{wy}" r="2.4" fill="{P.METAL}" stroke="{INK}" stroke-width=".8"/>'
          f'<circle cx="{crank[0]}" cy="{crank[1]}" r="1.4" fill="{P.METAL_DARK}"/>')
    if running:
        for q in range(2):                                         # the blur of the spinning wheel
            a0 = math.radians(-60 + q * 180)
            a1 = a0 + math.radians(70)
            d.add(f'<path d="M{n(wx + (r + 4) * math.cos(a0))},{n(wy + (r + 4) * math.sin(a0))} '
                  f'A{r + 4},{r + 4} 0 0 1 {n(wx + (r + 4) * math.cos(a1))},{n(wy + (r + 4) * math.sin(a1))}" '
                  f'fill="none" stroke="{INK}" stroke-width="1" stroke-opacity=".55"/>')
        rnd = random.Random(12)
        puffs = []
        for i in range(8):                                         # steam: puffs widening, fading, drifting back
            t = i / 7
            r_ = 3 + 6 * t
            for _ in range(1 if t < 0.2 else 2):
                puffs.append((-32.5 - 24 * t ** 1.3 + rnd.uniform(-0.5, 0.5) * r_,
                              -74 - 26 * t + rnd.uniform(-0.3, 0.3) * r_, r_ * rnd.uniform(0.8, 1.1), t))
        for px, py, r_, t in sorted(puffs, key=lambda p_: -p_[3]):   # the far, thin end first
            d.add(f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(r_)}" fill="{STEAM}" fill-opacity="{n(0.95 - 0.55 * t)}" '
                  f'stroke="{P.METAL}" stroke-width=".6" stroke-opacity="{n(0.9 - 0.6 * t)}"/>')
        d.add(f'<path d="M-10,-50 q-3,-5 1,-9 q-3,-4 0,-8" fill="none" stroke="{P.METAL}" stroke-width="1.6" '
              f'stroke-linecap="round" stroke-opacity=".7"/>')     # a wisp from the whistle
    return d


def steam_engine(c: Canvas, x: float, foot: float, k: float, running: bool, half: float = 60, table: float = 54,
                 toy: float = 1.0) -> dict:
    """The garden table at (x, foot), `half` wide each way and `table` tall, and on it the toy steam engine
    (`toy_engine`) at `toy` times its size. Returns its box."""
    d = Canvas()
    garden_table(d, half, table)
    d.add(f'<g transform="translate(0,{-table}) scale({n(toy)})">{toy_engine(running).render()}</g>')
    c.add(_at(d, x, foot, k))
    left = min((-64 if running else -40) * toy, -half - 1)
    right = max(41 * toy, half + 1)
    up = table + (102 if running else 71) * toy
    return {"box": (x + left * k, foot - up * k, x + right * k, foot)}


def engine_size(running: bool, half: float = 60, table: float = 54, toy: float = 1.0) -> tuple[float, float, float]:
    """The engine on its table in local units: (left, right, height) - for laying it out before drawing it."""
    return (min((-64 if running else -40) * toy, -half - 1), max(41 * toy, half + 1),
            table + (102 if running else 71) * toy)


def screen_face(s: Strip, x: float, oy: float, kk: float, left: float, top: float, w: float, h: float,
                kind: str, rows: int = 5, depth: float | None = None) -> None:
    """A screen drawn on its own, never mirrored (what is on it reads one way): its glass is a container at
    (left, top), in units of `kk`, from the point (x, oy) of a thing drawn the canonical way round - `kind`
    "editor": the old code editor, white, with its tab, line numbers and `rows` highlighted lines; "chat": the
    agent's window - session tabs along the top, the chat's bubbles turn and turn about, the box to type in; "off":
    the glass dark, a gleam across it."""
    gx = fx(s, x + (left + w / 2) * kk) - w / 2 * kk
    pen = Pen(s, gx, oy + top * kk, kk)
    glass = {"editor": P.WHITE, "chat": mix(P.CARD, P.WHITE, 0.5), "off": P.SCREEN_DARK}[kind]
    holder = pen.container(f"screen-{kind}", 0, 0, w, h, glass, radius=1.5, sw=1, light=None)
    pad = pen.pad(w, h)
    il, it, ir, ib = pad, pad, w - pad, h - pad
    iw, ih = ir - il, ib - it
    if kind == "editor":
        pen.c.add(f'<rect x="{n(il)}" y="{n(it)}" width="{n(iw * 0.4)}" height="{n(ih * 0.14)}" '
                  f'fill="{P.METAL_PALE}"/>')                                                  # the file's tab
        pen.c.add(f'<rect x="{n(il)}" y="{n(it + ih * 0.2)}" width="{n(iw * 0.13)}" height="{n(ih * 0.8)}" '
                  f'fill="{P.METAL_PALE}"/>')                                                  # the line numbers
        step = 0.8 / rows
        words = ((0.2, P.SYN_KEYWORD), (0.28, P.SYN_NAME), (0.2, P.SYN_STRING))
        for q in range(rows):
            ly = it + ih * (0.24 + q * step)
            lh = ih * step * 0.55
            pen.c.add(f'<rect x="{n(il + iw * 0.03)}" y="{n(ly)}" width="{n(iw * 0.07)}" height="{n(lh)}" '
                      f'fill="{P.METAL}"/>')                                                   # its number
            indent = (0, 0.1, 0.1, 0.2, 0.1, 0)[q % 6]
            lx = il + iw * (0.17 + indent)
            for j, (share, col) in enumerate(words):
                if (q + j) % 3 == 2 or lx + iw * share > ir:
                    continue
                pen.c.add(f'<rect x="{n(lx)}" y="{n(ly)}" width="{n(iw * share)}" height="{n(lh)}" rx=".4" '
                          f'fill="{col}"/>')
                lx += iw * (share + 0.04)
        pen.child(holder, "editor", il, it, ir, ib)
    elif kind == "chat":
        for q in range(3):                                                                      # session tabs
            pen.c.add(f'<rect x="{n(il + q * iw * 0.27)}" y="{n(it)}" width="{n(iw * 0.24)}" '
                      f'height="{n(ih * 0.14)}" rx=".8" fill="{P.METAL_LIGHT if q else P.TEAL}"/>')
        for q, (side, share) in enumerate(((1, 0.5), (0, 0.66), (1, 0.4))):                     # the chat
            bw = iw * share
            bx = ir - bw if side else il
            by = it + ih * (0.24 + q * 0.19)
            pen.c.add(f'<rect x="{n(bx)}" y="{n(by)}" width="{n(bw)}" height="{n(ih * 0.13)}" rx="1.2" '
                      f'fill="{P.ORANGE if side else P.WHITE}" stroke="{INK}" stroke-width=".4"/>')
            pen.c.add(f'<rect x="{n(bx + bw * 0.12)}" y="{n(by + ih * 0.055)}" width="{n(bw * 0.6)}" '
                      f'height="{n(ih * 0.025)}" fill="{INK}" fill-opacity=".35"/>')           # a line of words
        pen.c.add(f'<rect x="{n(il)}" y="{n(it + ih * 0.84)}" width="{n(iw)}" height="{n(ih * 0.16)}" rx="1" '
                  f'fill="{P.WHITE}" stroke="{INK}" stroke-width=".5"/>')                       # the box to type in
        pen.c.add(f'<rect x="{n(il + iw * 0.04)}" y="{n(it + ih * 0.88)}" width="{n(iw * 0.015 + 0.4)}" '
                  f'height="{n(ih * 0.08)}" fill="{INK}"/>')                                    # its cursor
        pen.child(holder, "chat", il, it, ir, ib)
    else:
        pen.c.add(f'<path d="M{n(w * 0.2)},{n(h * 0.85)} L{n(w * 0.55)},{n(h * 0.15)} H{n(w * 0.68)} '
                  f'L{n(w * 0.33)},{n(h * 0.85)} Z" fill="{P.WHITE}" fill-opacity=".1"/>')   # the gleam
    s.put(lane(s).feet - 0.5 if depth is None else depth, pen.svg(), None)


def devices(now: bool, compact: bool) -> tuple[Canvas, list[tuple]]:
    """What stands on the computer table, on (0, 0) its top: the old beige computer - the case lying flat with its
    floppy drive and power lamp, the fat monitor on it, the keyboard - and, `now`, a grey laptop open beside it, the
    old monitor dark. Returns the drawing and its screens: (left, top, w, h, kind)."""
    d = Canvas()
    mx = (-36 if compact else -48) if now else -10                  # now pushed to the far end
    d.shape(rounded_rect_d(mx - 26, -12, 52, 12, 1.5), P.BEIGE, sw=1.2, light=None)            # the case, flat
    d.shape(rounded_rect_d(mx + 6, -8, 16, 3.2, 0.8), P.BEIGE_DARK, sw=0.6, light=None)        # its floppy drive
    d.line(f"M{mx + 8},-6.4 h12", 0.8, INK)
    d.add(f'<circle cx="{mx - 18}" cy="-6" r="1.4" fill="{P.GREEN if not now else P.BEIGE_DARK}"/>')
    d.line(" ".join(f"M{mx - 12 + q * 3},-10 v6" for q in range(4)), 0.6, P.BEIGE_SHADE)        # its vents
    d.shape(f"M{mx - 14},-14 L{mx - 10},-54 H{mx + 10} L{mx + 14},-14 Z", P.BEIGE_DARK, sw=1.2,
            light=None)                                                                          # the tube's back
    d.shape(rounded_rect_d(mx - 23, -52, 46, 39, 3), P.BEIGE, sw=1.4, light=(-1, -1))          # the bezel
    d.add(f'<circle cx="{mx + 17}" cy="-16.5" r="1.1" fill="{P.GREEN if not now else P.BEIGE_DARK}"/>')
    d.shape(rounded_rect_d(mx - 9, -14, 18, 3, 1), P.BEIGE_DARK, sw=0.8, light=None)           # its foot
    screens = [(mx - 19, -48, 38, 30, "off" if now else "editor")]
    if not now:
        d.shape(f"M{mx + 30},0 L{mx + 34},-5 H{mx + 72} L{mx + 74},0 Z", P.BEIGE, sw=1.1, light=None)  # keyboard
        d.line(" ".join(f"M{mx + 36 + q * 4},-2.5 h2" for q in range(9)), 1.2, P.BEIGE_SHADE)
        d.shape(rounded_rect_d(mx + 78, -4, 7, 4, 2), P.BEIGE, sw=0.8, light=None)             # its mouse
    else:
        lx = 30
        d.shape(f"M{lx - 30},0 L{lx - 26},-3 H{lx + 26} L{lx + 30},0 Z", P.METAL_LIGHT, sw=1.1, light=None)
        d.shape(rounded_rect_d(lx - 26, -39, 52, 36, 2), P.METAL, sw=1.3, light=None)          # the laptop's lid
        d.add(f'<circle cx="{lx}" cy="-37" r=".7" fill="{INK}"/>')                             # its camera
        d.add(f'<path d="M{lx + 34},-1 h6 v-6 h-6 Z" fill="{P.WHITE}" stroke="{INK}" stroke-width=".6"/>'
              f'<path d="M{lx + 40},-6 q3,0 3,2.4 q0,2 -3,2" fill="none" stroke="{INK}" stroke-width=".6"/>')  # mug
        screens.append((lx - 23, -36, 46, 30, "chat"))
    return d, screens


def computer_table(s: Strip, c: Canvas, x: float, foot: float, k: float, now: bool, compact: bool = False,
                   dev: float = 1.0, table: float = 54, depth: float | None = None) -> dict:
    """The computer table at (x, foot), 170 wide (130 `compact`) and `table` tall, and on it `devices` at `dev`
    times their size. The screens are drawn by `screen_face` (never mirrored). Returns its box."""
    d = Canvas()
    half = (64 if compact else 85) * max(1.0, dev * 0.9)
    garden_table(d, half, table)
    things, screens = devices(now, compact)
    d.add(f'<g transform="translate(0,{-table}) scale({n(dev)})">{things.render()}</g>')
    c.add(_at(d, x, foot, k))
    for left, top, w, h, kind in screens:
        screen_face(s, x, foot - table * k, k * dev, left, top, w, h, kind, rows=5 if dev < 1.2 else 4, depth=depth)
    return {"box": (x - (half + 1) * k, foot - (table + 56 * dev) * k, x + (half + 1) * k, foot)}


def grill(c: Canvas, x: float, foot: float, k: float, burnt: bool) -> dict:
    """The round kettle grill at (x, foot), 100 wide and 122 to the top of its smoke: the black enamel bowl with its
    gleam, the vents of its damper and a handle bar at its side, standing in a ring on three straight legs - the two
    front ones on wheels on their axle, the third going back - with the round ash pan slung between them; the lid
    swung open on its hinge at the back, dome up, its handle and vent; on the grate over the glowing coals four
    sausages - charred black under dark smoke (`burnt`), or golden under a light one; a bag of charcoal at its feet.
    Returns its box."""
    d = Canvas()
    shadow(d, 0, 0, 42)
    legs = "M-16,-46 L-28,-4 M16,-46 L28,-4 M0,-46 L1,-10"
    d.line(legs, 5, INK)
    d.line(legs, 3, P.METAL_DARK)                                                               # the three legs
    d.line("M-27,-5 H27", 2.6, INK)
    d.line("M-27,-5 H27", 1.4, P.METAL)                                                         # the axle
    d.add(f'<ellipse cx="0" cy="-24" rx="18" ry="3" fill="{P.METAL_LIGHT}" stroke="{INK}" '
          f'stroke-width="1.1"/>')                                                               # the ash pan
    d.line("M-12,-46 Q-14,-34 -17,-24 M12,-46 Q14,-34 17,-24", 1, P.METAL_DARK)                 # its brackets
    for wx_ in (-28, 28):                                                                        # the wheels
        d.add(f'<circle cx="{wx_}" cy="-5" r="5" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="1.1"/>'
              f'<circle cx="{wx_}" cy="-5" r="1.8" fill="{P.METAL}"/>')
    d.shape("M-18,-50 H18 L15,-44 H-15 Z", P.METAL_DARK, sw=1, light=None)                       # the leg ring
    # the lid, swung up on its hinge at the back left, dome up
    d.add('<g transform="translate(-26,-76) rotate(-112)">')
    d.shape("M0,0 C0,-26 56,-26 56,0 Z", P.CHARCOAL, sw=1.4, light=(0, -1.5))
    d.add(f'<path d="M8,-6 C12,-16 26,-19 36,-17" fill="none" stroke="{P.METAL}" stroke-width="1.4" '
          f'stroke-opacity=".6"/>')
    d.shape(rounded_rect_d(21, -24, 14, 4, 2), P.WOOD, sw=0.8, light=None)                      # its handle
    d.add(f'<circle cx="42" cy="-12" r="2.2" fill="{P.METAL}" stroke="{INK}" stroke-width=".6"/>')   # its vent
    d.add("</g>")
    d.shape(rounded_rect_d(-31, -80, 6, 6, 1), P.METAL, sw=0.8, light=None)                     # the hinge
    d.shape("M-29,-74 C-29,-50 -14,-44 0,-44 C14,-44 29,-50 29,-74 Z", P.CHARCOAL, sw=1.5, light=(-1, -1))  # bowl
    d.add(f'<path d="M-22,-66 C-20,-54 -12,-49 -2,-48" fill="none" stroke="{P.METAL}" stroke-width="1.8" '
          f'stroke-opacity=".5"/>')                                                               # its gleam
    d.add("".join(f'<rect x="{vx - 1.6}" y="-51" width="3.2" height="1.6" rx=".6" fill="{P.METAL}"/>'
                  for vx in (-5, 0, 5)))                                                          # the damper
    d.line("M29,-70 h8 M37,-72 v6", 2.2, P.WOOD)                                                 # the side handle
    d.add(f'<ellipse cx="0" cy="-74" rx="29" ry="5" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="1.3"/>')
    rnd = random.Random(5)
    coals = []
    for _ in range(14):                                                                          # the glowing coals
        cx_, cy_ = rnd.uniform(-22, 22), rnd.uniform(-75.5, -71.8)
        coals.append(f"M{n(cx_ + 2.2)},{n(cy_)} a2.2,1.4 0 1 1 -4.4,0 a2.2,1.4 0 1 1 4.4,0 Z")
    d.add(f'<path d="{" ".join(coals)}" fill="{P.ORANGE if not burnt else mix(P.ORANGE, P.RED, 0.4)}" '
          f'stroke="{P.RED}" stroke-width=".5"/>')
    d.line(" ".join(f"M{q},{n(-74 - 4.6 * math.sqrt(max(0, 1 - (q / 29) ** 2)))} "
                    f"V{n(-74 + 4.6 * math.sqrt(max(0, 1 - (q / 29) ** 2)))}" for q in range(-24, 25, 4)),
           0.8, P.METAL)                                                                         # the grate's bars
    d.add(f'<ellipse cx="0" cy="-74" rx="29" ry="5" fill="none" stroke="{P.METAL}" stroke-width="1.2"/>')
    col = P.CRUST_BURNT if burnt else mix(P.CRUST, P.ORANGE, 0.3)
    for q in range(4):                                                     # the sausages, lying on the grate
        sx = -15 + q * 10
        sy = -74.6 + (q % 2) * 1.2
        d.shape(rounded_rect_d(sx - 5.4, sy - 2.6, 10.8, 3.6, 1.8), col, sw=0.8, light=None)
        d.line(f"M{sx - 2.4},{sy - 2.4} l-1,3.2 M{sx + 1},{sy - 2.4} l-1,3.2 M{sx + 4},{sy - 2.4} l-1,3.2", 0.7,
               P.CHARCOAL if burnt else darken(col, 0.55))                                    # its grill marks
    d.shape("M-50,0 L-48,-15 Q-42,-18 -36,-15 L-34,0 Z", P.KITCHEN_KRAFT, sw=1, light=None)       # charcoal bag
    d.add(f'<rect x="-47" y="-10" width="10" height="5" fill="{P.CHARCOAL}"/>')
    smoke = mix(P.CHARCOAL, P.METAL, 0.3) if burnt else STEAM
    rnd = random.Random(3)
    puffs_ = []
    for i in range(11):                                                # the smoke, widening and fading upwards
        t = i / 10
        for _ in range(1 if t < 0.2 else 2):
            puffs_.append((4 + 18 * t ** 1.4 + rnd.uniform(-3, 3), -82 - 34 * t + rnd.uniform(-2, 2),
                           (3 + 6 * t) * rnd.uniform(0.8, 1.1), t))
    for px, py, r_, t in sorted(puffs_, key=lambda p_: -p_[3]):
        d.add(f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(r_)}" fill="{smoke}" '
              f'fill-opacity="{n((0.92 if burnt else 0.8) - 0.6 * t)}" stroke="{P.METAL_DARK}" '
              f'stroke-width=".5" stroke-opacity="{n(0.6 - 0.5 * t)}"/>')
    c.add(_at(d, x, foot, k))
    return {"box": (x - 59 * k, foot - 124 * k, x + 49 * k, foot)}


def match(x: float, y: float, k: float) -> str:
    """A long match held by its end, its red head lit."""
    c = Canvas()
    c.line("M0,2 L0,-14", 1.1, P.WOOD_PALE)
    c.add(f'<circle cx="0" cy="-14.6" r="1.4" fill="{P.RED}" stroke="{INK}" stroke-width=".4"/>')
    c.shape("M0,-15.6 q-2,-3 0,-6 q2,3 0,6 Z", P.ORANGE, sw=0.3, light=None)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def tongs(x: float, y: float, k: float) -> str:
    """Grill tongs held by their hinge end, the two steel arms opening forward."""
    c = Canvas()
    c.line("M0,0 L18,-4 M0,0 L18,1", 1.1, P.METAL_DARK)
    c.shape(rounded_rect_d(-3, -1.6, 6, 3.2, 1.4), P.WOOD_DARK, sw=0.4, light=None)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def plate(x: float, y: float, k: float) -> str:
    """A plate held out by its rim, two golden sausages on it."""
    c = Canvas()
    c.add(f'<ellipse cx="9" cy="-2" rx="10" ry="2.6" fill="{P.WHITE}" stroke="{INK}" stroke-width=".5"/>')
    for q in range(2):
        c.shape(rounded_rect_d(4 + q * 5, -4.6, 4.4, 2.6, 1.3), mix(P.CRUST, P.ORANGE, 0.3), sw=0.35, light=None)
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


# ============================================================================ the introduction's moments
def close(s: Strip) -> bool:
    """A low strip: the camera comes close - the station's thing drawn big, one character beside it."""
    return s.h < 200


def engine_moment(s: Strip, beat: str) -> None:
    """The steam engine: "fire" - the professor lights the burner with a long match, the caterpillar doubts it will
    work; "steam" - the flywheel spins and the chimney puffs, the cat tells its story from his book, the agent
    cheers, the sparrow on the table's corner. A low strip comes close: the engine big on a low table, one of them
    beside it."""
    r = lane(s)
    running = beat == "steam"
    near = close(s)
    table, toy, half = (30, 2.0, 60) if near else (54, 1.0, 60)
    k = pk(s, engine_size(running, half, table, toy)[2], 0.98 if near else 0.92)
    c = Canvas()
    up = lift(s)
    se = steam_engine(c, s.x(0.42), r.feet - up, k * (0.92 if up else 1), running, half, table, toy)
    box = place_(s, c, se["box"], "engine")
    if running:
        who = (("cat", 1, "present", "smile", lambda x_, y_, kk: handheld.book(x_, y_, kk, P.TEAL)),
               ("agent", -1, "cheer", "smile", None))
        cast(s, box, who)
        if not near:
            sparrow_on(s, fx(s, s.x(0.42) + 50 * k), r.feet - 54 * k, "engine")
    else:
        who = (("professor", 1, "present", "smile", match), ("caterpillar", -1, "think", "worry", None))
        cast(s, box, who)


def editor_moment(s: Strip, beat: str) -> None:
    """From the notepad to the IDE and back: "then" - the old computer, the professor at its keyboard, the cat with
    his mug; "now" - the laptop with the agent's chat, the agent typing, the old monitor dark, the caterpillar
    with her list. A low strip comes close: the computer big, its code lines readable, one of them beside it."""
    r = lane(s)
    near = close(s)
    dev, table = (1.55, 36) if near else (1.0, 54)
    k = pk(s, table + 56 * dev, 0.85 if near else 0.78)
    c = Canvas()
    now = beat == "now"
    up = lift(s)
    ct = computer_table(s, c, s.x(0.45), r.feet - up, k * (0.92 if up else 1), now, compact=near, dev=dev,
                        table=table, depth=r.feet - up - 0.5)
    box = place_(s, c, ct["box"], "computer")
    if now:
        who = (("agent", 1, "type", "smile", None), ("caterpillar", -1, "present", "smile", checklist(3)))
    else:
        who = (("professor", 1, "present", "smile", None), ("cat", -1, "think", "smile", mug))
    cast(s, box, who)


def grill_moment(s: Strip, beat: str) -> None:
    """Why the book - many got burnt: "burnt" - the caterpillar with the tongs over charred sausages and dark smoke,
    the cat raising an eyebrow; "done" - the agent grills them golden, the professor holds out the plate."""
    r = lane(s)
    k = pk(s, 122, 0.8)
    c = Canvas()
    burnt = beat == "burnt"
    up = lift(s)
    gr = grill(c, s.x(0.45), r.feet - up, k * (0.92 if up else 1), burnt)
    box = place_(s, c, gr["box"], "grill")
    if burnt:
        cast(s, box, (("caterpillar", 1, "present", "worry", tongs), ("cat", -1, "think", "smile", mug)))
    else:
        cast(s, box, (("agent", 1, "present", "smile", tongs), ("professor", -1, "present", "smile", plate)))


def intro_backdrop(s: Strip, index: int) -> None:
    """The yard behind the introduction's moments: the same yard as the front pages', the camera at another
    stretch of its row."""
    prepare(s)
    yard(s, VIEW[COURTYARD.stations[index].key] + (s.seed % 2) * 60, s.seed + 7)


def scale_cast(s: Strip) -> None:
    """The yard's camera: the cast as big as the frame lets it be (as `prepare` sets it)."""
    feet = lane(s).feet
    names = ("professor", "cat", "agent", "caterpillar")
    if s.h < 300:
        top = max(_box(s, name, 0, feet)[3] - _box(s, name, 0, feet)[1] for name in names)
        s.tall *= (feet - 6) / top
    widest = max(_box(s, name, 0, feet)[2] - _box(s, name, 0, feet)[0] for name in names)
    s.tall *= min(1.0, (s.hi - s.lo) * 0.19 / widest)
    s.unit = s.tall / 137


def intro_finale(s: Strip) -> None:
    """The heroes of the book: the yard - the cottage, the shed, the apple tree along its back fence - and on the
    patio in front of it the steam engine puffing on its table, the four introducing themselves, each with their
    thing - the professor welcoming, the cat with his book, the caterpillar with her list, the agent waving - and
    the flowerbed where the sparrow digs out a golden floppy. In a tall frame the computer table and the grill stand
    further back, at the patio's back edge. A low strip shows the near row alone. No labels."""
    s.mirror = False
    prepare(s)
    yard(s, 470, 11)
    feet = lane(s).feet
    deep = s.h >= 200
    a0 = height(s, "professor")
    dims = {"engine": (*engine_size(True, 42), 0.92), "dig": (-40, 40, 40, 0.45)}
    who = {"professor": ("welcome", None), "cat": ("present", lambda x_, y_, kk: handheld.book(x_, y_, kk, SUN)),
           "agent": ("wave", None), "caterpillar": ("present", checklist(4))}
    wide = {name: (_box(s, name, 0, feet)[2] - _box(s, name, 0, feet)[0]) / a0 for name in who}
    if s.h >= 450:                                                     # tall: the four in front, the things behind
        finale_deep(s, who, wide, dims, a0, feet)
        return
    items = ["engine", "professor", "cat", "caterpillar", "agent", "dig"]
    widths = [wide[i] if i in wide else (dims[i][1] - dims[i][0]) * dims[i][3] / dims[i][2] for i in items]
    span_ = s.hi - s.lo
    a = min(a0, (span_ - 12 * (len(items) + 1)) / sum(widths))
    spare = (span_ - a * sum(widths)) / (len(items) + 1)
    things = Canvas()
    x = s.lo + spare
    spots = {}
    for item, w in zip(items, widths, strict=True):
        left = x
        x += a * w + spare
        if item in who:
            pose, hold = who[item]
            actor = s.actor(item, left + a * w / 2, feet, pose, "smile", flip=item != "professor",
                            tall=s.tall * SIZE[item] * a / a0, group=f"f{item}")
            if hold is not None:
                s.hold(actor, hold)
            continue
        k = a * dims[item][3] / dims[item][2]
        mx = left - dims[item][0] * k                                   # its own middle, from its left edge
        if item == "engine":
            box = steam_engine(things, mx, feet, k, True, half=42)["box"]
            s.put(feet - 1, "", box, item, group=item)
        else:
            box = dig(s, mx, feet, k, a / a0)
        spots[item] = box
    s.put(feet - 1, things.render(), None)
    _ = deep


def finale_deep(s: Strip, who: dict, wide: dict, dims: dict, a0: float, feet: float) -> None:
    """The tall finale: the four side by side in front, as big as the width allows, and a step behind them the
    steam engine puffing on its table at the left and the flowerbed with the sparrow and the floppy at the right."""
    names = ["professor", "cat", "caterpillar", "agent"]
    span_ = s.hi - s.lo
    total = sum(wide[name] for name in names)
    a = min(a0, (span_ * 0.8 - 14 * 5) / total)
    spare = (span_ * 0.8 - a * total) / 5
    x = s.lo + spare
    for name in names:
        w = wide[name] * a
        pose, hold = who[name]
        actor = s.actor(name, x + w / 2, feet, pose, "smile", flip=name != "professor",
                        tall=s.tall * SIZE[name] * a / a0, group=f"f{name}")
        if hold is not None:
            s.hold(actor, hold)
        x += w + spare
    back = feet - IN_FRONT - 4
    things = Canvas()
    k = a * 0.8 * dims["engine"][3] / dims["engine"][2]
    ex = s.lo - dims["engine"][0] * k + 4
    box = steam_engine(things, ex, back, k, True, half=42)["box"]
    s.put(back - 1, "", box, "engine", group="engine", backdrop=True)
    s.put(back - 1, things.render(), None)
    kd = a * 0.8 * dims["dig"][3] / dims["dig"][2]
    dig(s, s.hi - 48 * kd - 4, back, kd, a / a0 * 0.8, behind=True)


def dig(s: Strip, x: float, feet: float, k: float, size: float = 1.0, behind: bool = False) -> tuple:
    """A raised flowerbed on the patio at (x, feet), 80 wide: a frame of two boards with their grain and corner
    posts, dark earth heaped in it, flowers along its back - and dug up in front of them a mound of fresh earth with
    a golden floppy's top peeking out of it and a trowel stuck in beside it; the sparrow stands on the board's edge,
    digging: the hunt of the book starting (the sparrow says so on this page). Returns its box."""
    d = Canvas()
    d.add(f'<ellipse cx="0" cy="0" rx="44" ry="2.6" fill="{INK}" fill-opacity=".14"/>')
    d.shape("M-38,-13 Q-20,-18 0,-17 Q20,-18 38,-13 V-10 H-38 Z", darken(P.WOOD, 0.5), sw=1, light=None)  # earth
    for q, (fx0, col) in enumerate(((-30, P.PINK), (-20, SUN), (-10, P.RED), (24, P.WHITE), (32, P.PINK))):
        h = 14 + (q % 3) * 4
        d.line(f"M{fx0},-15 V{-15 - h}", 1.2, P.LEAF_DARK)
        d.add(f'<path d="M{fx0 - 4},-15 q4,-6 8,0 Z" fill="{P.LEAF}" stroke="{INK}" stroke-width=".5"/>'
              f'<circle cx="{fx0}" cy="{-15 - h}" r="3.4" fill="{col}" stroke="{INK}" stroke-width=".6"/>'
              f'<circle cx="{fx0}" cy="{-15 - h}" r="1.2" fill="{SUN if col != SUN else P.ORANGE}"/>')
    d.shape(rounded_rect_d(-40, -12, 80, 12, 1), P.WOOD, sw=1.2, light=None)                    # the boards
    d.line("M-40,-6 H40", 0.8, P.WOOD_DARK)
    d.line("M-34,-9 q8,-1 16,0 t16,0 M4,-3 q8,-1 16,0 t14,0", 0.5, darken(P.WOOD, 0.7), 0.7)
    for px in (-40, 36):
        d.shape(rounded_rect_d(px, -14, 4, 14, 0.6), P.WOOD_DARK, sw=0.9, light=None)           # corner posts
    d.shape("M2,-15 Q8,-25 16,-24 Q22,-22 24,-15 Z", darken(P.WOOD, 0.45), sw=0.9, light=None)  # the dug earth
    d.shape("M-2,-16 l7,-14 l2,1 l-6,14 Z", P.METAL_LIGHT, sw=0.6, light=None)                  # the trowel
    d.shape(rounded_rect_d(4, -36, 3, 8, 1.2), P.WOOD, sw=0.6, light=None)
    c = Canvas()
    c.add(_at(d, x, feet, k))
    c.add(floppy(x + 13 * k, feet - 15 * k, 0.75 * k, ""))                                  # half in the earth
    e = Canvas()
    e.add(f'<path d="M{n(x + 3 * k)},{n(feet - 15 * k)} Q{n(x + 6 * k)},{n(feet - 21 * k)} {n(x + 9 * k)},'
          f'{n(feet - 20 * k)} L{n(x + 17 * k)},{n(feet - 20 * k)} Q{n(x + 21 * k)},{n(feet - 21 * k)} '
          f'{n(x + 24 * k)},{n(feet - 15 * k)} Z" fill="{darken(P.WOOD, 0.45)}" stroke="{INK}" '
          f'stroke-width="{n(0.6 * k)}"/>')
    box = (x - 42 * k, feet - 40 * k, x + 42 * k, feet)
    s.put(feet - 1, c.render() + e.render(), box, "flowerbed", group="dig", backdrop=behind)
    s.actor("sparrow", x + (33 if behind else -26) * k, feet - 12 * k, "cheer", "smile", flip=behind,
            tall=s.tall * SIZE["sparrow"] * 0.5 * size, group="dig", depth=feet)
    return box


COURTYARD.stations.extend([
    Station("engine", _fitted(engine_moment, intro_backdrop), ("fire", "steam")),
    Station("editor", _fitted(editor_moment, intro_backdrop), ("then", "now")),
    Station("grill", _fitted(grill_moment, intro_backdrop), ("burnt", "done")),
])
COURTYARD.backdrop = _remember
COURTYARD.finale = intro_finale
COURTYARD.alternate = True

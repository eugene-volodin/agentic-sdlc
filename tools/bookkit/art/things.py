"""Things for the footer episodes: kitchen, shop, museum, village and nursery props.

Like `props` and `sets`: `thing(x, y, k, ...) -> str`, the origin where the thing touches the ground (or, for
things on a wall, as the docstring says), drawn for a 137-unit professor at k = 1.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten
from .ink import INK, Canvas, ellipse_d, n, rounded_rect_d
from .sets import LETTERING_MIN, _at, _label, doodle_at, fit_label, letter_width


# ============================================================================ kitchen
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
    return _at(c, x, y, k)


def potato(x: float, y: float, k: float = 1.0, peeled: bool = False, turn: float = 0) -> str:
    c = Canvas()
    color = P.CREAM if peeled else P.TRUNK
    c.shape("M-9,-1 Q-11,-9 -3,-10 Q6,-12 9,-6 Q11,0 4,1 Q-4,3 -9,-1 Z", color, sw=1.6, light=(-1, -1))
    if not peeled:
        c.dot(-3, -6, 0.9)
        c.dot(3, -4, 0.9)
    return _at(c, x, y, k, turn=turn)


def bucket(x: float, y: float, k: float = 1.0, color: str = P.METAL, fill: str = "potatoes") -> str:
    """A pail; `fill` is potatoes, water or empty."""
    c = Canvas()
    c.line("M-15,-30 Q0,-48 15,-30", 1.8)
    if fill == "potatoes":
        for px, py in ((-8, -30), (4, -32), (10, -29), (-2, -36), (-11, -34)):
            c.add(potato(px, py + 4, 0.9))
    c.shape("M-16,-30 L-12,0 H12 L16,-30 Z", color, sw=2, light=(-2, -1), shade_k=0.85)
    c.shape(ellipse_d(0, -30, 16, 3.5), darken(color, 0.9), sw=1.6, light=None)
    if fill == "water":
        c.add(f'<ellipse cx="0" cy="-30" rx="13" ry="2.4" fill="{P.WATER}"/>')
    c.line("M-14,-20 H14 M-13,-10 H13", 1, opacity=0.5)
    return _at(c, x, y, k)


def pot(x: float, y: float, k: float = 1.0, steam: bool = True, color: str = P.RED) -> str:
    c = Canvas()
    if steam:
        wisps = "M-7,-32 q-4,-5 0,-10 q4,-5 0,-10 M5,-34 q4,-5 0,-10 q-4,-5 0,-11"
        c.line(wisps, 3.6, P.METAL, 0.6)
        c.line(wisps, 2, P.WHITE)
    c.shape("M-20,-26 H20 V-6 Q20,0 14,0 H-14 Q-20,0 -20,-6 Z", color, sw=2, light=(-2, -2),
            highlight="M-15,-21 V-8")
    c.shape(rounded_rect_d(-23, -29, 46, 5, 2), darken(color, 0.85), sw=1.6, light=None)
    c.line("M-24,-20 h-5 M24,-20 h5", 3)
    return _at(c, x, y, k)


def handkerchief(x: float, y: float, k: float = 1.0) -> str:
    """A crumpled polka-dot handkerchief with a potato in it, as if being polished."""
    c = Canvas()
    clip = c.shape("M-14,0 Q-18,-10 -10,-14 Q-2,-20 8,-14 Q16,-12 14,-2 Q4,4 -14,0 Z", P.BLUE, sw=1.6, light=None,
                   clip=True)
    dots = "".join(f'<circle cx="{dx}" cy="{dy}" r="1.8" fill="{P.WHITE}"/>'
                   for dx, dy in ((-8, -8), (0, -12), (6, -6), (-2, -3), (10, -9), (-12, -3)))
    c.add(f'<g clip-path="url(#{clip})">{dots}</g>')
    c.path("M-14,0 Q-18,-10 -10,-14 Q-2,-20 8,-14 Q16,-12 14,-2 Q4,4 -14,0 Z", "none", 1.6)
    c.add(potato(2, -9, 0.8, turn=10))
    c.line("M18,-18 l4,-4 M20,-10 l6,-1 M16,-24 l1,-6", 1.4, P.SUN)   # it shines
    return _at(c, x, y, k)


def wall_shelf(x: float, y: float, k: float = 1.0, w: float = 120, items: tuple = ("jar", "jar", "pot")) -> str:
    """A shelf on brackets with jars on it; the origin is the middle of the board."""
    c = Canvas()
    hw = w / 2
    c.line(f"M{-hw + 12},0 l0,12 l10,-12 M{hw - 12},0 l0,12 l-10,-12", 2, P.WOOD_DARK)
    c.shape(rounded_rect_d(-hw, -2, w, 6, 2), P.WOOD, sw=1.8, light=None)
    step = w / (len(items) + 1)
    for i, item in enumerate(items):
        ix = -hw + step * (i + 1)
        if item == "jar":
            fill = (P.RED, P.GREEN, P.AMBER)[i % 3]
            c.shape(f"M{ix - 9},-2 V-22 H{ix + 9} V-2 Z", lighten(P.WATER_LIGHT, 0.4), sw=1.5, light=None)
            for jx, jy in ((-4, -8), (3, -12), (-2, -16), (4, -6)):
                c.add(f'<circle cx="{n(ix + jx)}" cy="{jy}" r="3.2" fill="{fill}" stroke="{INK}" stroke-width=".8"/>')
            c.shape(f"M{ix - 10},-26 H{ix + 10} V-22 H{ix - 10} Z", P.RED, sw=1.3, light=None)
        else:
            c.add(pot(ix, -2, 0.55, steam=False, color=P.ORANGE))
    return _at(c, x, y, k)


def stool(x: float, y: float, k: float = 1.0, color: str = P.RED) -> str:
    """A round stool, its seat 40 up."""
    c = Canvas()
    for lx, tx in ((-12, -9), (12, 9)):
        c.line(f"M{tx},-38 L{lx},0", 3.4, P.WOOD_DARK)
    c.line("M-9,-16 H9", 2.4, P.WOOD_DARK)
    c.shape(ellipse_d(0, -40, 16, 5), color, sw=1.8, light=(-1, -1))
    return _at(c, x, y, k)


# ============================================================================ winter
def snowman(x: float, y: float, k: float = 1.0, broom: bool = True) -> str:
    c = Canvas()
    if broom:                       # a birch broom held upright in its twig hand, the brush up
        c.line("M22,-22 L34,-90", 2.6, P.WOOD_DARK)
        c.shape("M32,-86 Q26,-100 30,-112 Q36,-104 38,-112 Q42,-100 36,-86 Z", P.AMBER, sw=1.4, light=None)
        c.line("M33,-90 l-1,-14 M35,-90 l2,-13", 0.9, P.WOOD_DARK)
    for cy, r in ((-18, 20), (-50, 15), (-74, 11)):
        c.shape(ellipse_d(0, cy, r, r), P.WHITE, sw=2, light=(-2, -2), shade_k=0.9)
    c.shape("M-10,-84 L-8,-100 H10 L12,-84 Z", P.METAL, sw=1.8, light=None)       # a bucket for a hat
    c.dot(-4, -77, 1.6)
    c.dot(4, -77, 1.6)
    c.shape("M0,-73 L13,-71 L0,-69 Z", P.ORANGE, sw=1.2, light=None)
    for by in (-56, -48, -40):
        c.dot(0, by, 1.8)
    c.line("M-14,-52 L-28,-62 l-5,-1 M-28,-62 l-2,-5 M14,-52 L29,-60 l3,-4 M29,-60 l4,1", 2, P.WOOD_DARK)
    return _at(c, x, y, k)


def smeared_list(x: float, y: float, k: float = 1.0, turn: float = -8) -> str:
    """A wet shopping list lying in the snow, its lines run into blots."""
    c = Canvas()
    c.shape("M-16,0 V-30 H16 V0 Z", P.CARD, sw=1.6, light=None)
    for i, w in enumerate((20, 14, 22, 12)):
        c.line(f"M-11,{-24 + i * 6} h{w}", 1.4, P.PEN, 0.8)
    for bx, by, r in ((-4, -18, 5), (6, -8, 4)):
        c.add(f'<ellipse cx="{bx}" cy="{by}" rx="{r}" ry="{r * 0.7}" fill="{P.PEN}" opacity=".35"/>')
    return _at(c, x, y, k, turn=turn)


def felt_boots(x: float, y: float, k: float = 1.0) -> str:
    """A pair of grey felt boots (valenki) standing side by side: tall soft shafts, rounded toes, a red stitched
    band at the top. 40 wide, 34 tall."""
    c = Canvas()
    felt = P.STONE
    for dx in (8, -8):                                  # the far boot first
        d = (f"M{dx - 7},-34 Q{dx - 8},-20 {dx - 8},-6 Q{dx - 8},0 {dx - 3},0 H{dx + 12} Q{dx + 17},0 {dx + 16},-5 "
             f"Q{dx + 15},-10 {dx + 6},-11 Q{dx + 6},-22 {dx + 7},-34 Q{dx},-36 {dx - 7},-34 Z")
        c.shape(d, felt, sw=1.7, light=(-1.4, -1), shade_k=0.82, stipple=(dx - 8, -34, 24, 34, 14, "right"))
        c.line(f"M{dx - 7},-29 Q{dx},-31 {dx + 7},-29", 2.2, P.RED)
        c.line(f"M{dx - 5},-29.8 l1,1.6 M{dx - 1},-30.4 l1,1.6 M{dx + 3},-30.4 l1,1.6", 0.8, P.WHITE)
        c.line(f"M{dx - 4},-8 Q{dx + 3},-6 {dx + 8},-9", 1, opacity=0.5)
    return _at(c, x, y, k)


def earmuffs(x: float, y: float, k: float = 1.0, span: float = 24, rise: float | None = None) -> str:
    """Fluffy pink earmuffs on a band; the origin is the middle between the muffs, `span` apart; the band arches
    `rise` above them (over the top of a head)."""
    c = Canvas()
    h = span / 2
    top = -(rise if rise is not None else span * 0.6)
    band = f"M{n(-h)},-2 C{n(-h)},{n(top * 1.3)} {n(h)},{n(top * 1.3)} {n(h)},-2"
    c.line(band, 4.2)
    c.line(band, 2.2, P.METAL_DARK)
    for dx in (-h, h):
        c.shape(ellipse_d(dx, 0, span * 0.2, span * 0.27), P.PINK, sw=1.6, light=(-1, -1),
                stipple=(dx - span * 0.2, -span * 0.27, span * 0.4, span * 0.54, 8, "even"))
    return _at(c, x, y, k)


# ============================================================================ museum
def _plaque(label: str, k: float) -> tuple[float, float, float]:
    """(font size, width, height) of a pedestal's plaque: the word with an even margin all round."""
    size = max(8.0, LETTERING_MIN / k * 1.04)
    return size, letter_width(label, size) + size * 1.2, size * 1.6


def pedestal_width(label: str = "", k: float = 1.0) -> float:
    """How wide the pedestal `pedestal` draws is at scale 1 (its cornice), for a plaque with these words."""
    return 2 * _pedestal_half(label, k) + 8


def _pedestal_half(label: str, k: float) -> float:
    return max(18.0, _plaque(label, k)[1] / 2 + 2) if label else 18.0


def pedestal(x: float, y: float, k: float = 1.0, exhibit: str = "abacus", label: str = "") -> str:
    """A museum pedestal with an exhibit on top and a plaque on its front; the pedestal is as wide as its plaque
    needs (see `pedestal_width`)."""
    c = Canvas()
    hw = _pedestal_half(label, k)
    c.shape(f"M{n(-hw)},0 V-40 H{n(hw)} V0 Z", P.CARD, sw=1.8, light=(-2, -1), shade_k=0.9)
    c.shape(rounded_rect_d(-hw - 4, -44, 2 * hw + 8, 6, 2), P.STONE, sw=1.6, light=None)
    c.shape(rounded_rect_d(-hw - 4, -2, 2 * hw + 8, 5, 2), P.STONE, sw=1.6, light=None)
    if exhibit == "abacus":
        c.path("M-16,-46 V-74 H16 V-46 Z", "none", 3, P.WOOD_DARK)
        for row in range(4):
            yy = -68 + row * 6
            c.line(f"M-16,{yy} H16", 0.9)
            for b in range(4):
                c.add(f'<circle cx="{-11 + b * 4 + (row % 2) * 6}" cy="{yy}" r="2" fill="{(P.RED, P.YELLOW)[row % 2]}" '
                      f'stroke="{INK}" stroke-width=".7"/>')
    elif exhibit == "arithmometer":
        c.shape("M-16,-46 V-62 H16 V-46 Z", P.METAL_DARK, sw=1.8, light=(-1, -1))
        c.line("M16,-56 l8,-4 l0,-6", 2)
        c.add(f'<circle cx="24" cy="-68" r="2.4" fill="{P.RED}" stroke="{INK}" stroke-width="1"/>')
        for i in range(5):
            c.dot(-12 + i * 5, -54, 1.2, P.WHITE)
    elif exhibit == "punchcard":
        c.shape("M-15,-46 L-15,-70 L13,-70 L17,-66 V-46 Z", P.YELLOW_PALE, sw=1.5, light=None)
        for i in range(6):
            for j in range(3):
                if (i + j) % 2:
                    c.add(f'<rect x="{-12 + i * 4.6}" y="{-66 + j * 6}" width="2" height="3.4" fill="{INK}"/>')
    else:   # a vacuum tube
        c.shape("M-6,-46 V-58 Q-10,-80 0,-82 Q10,-80 6,-58 V-46 Z", lighten(P.WATER_LIGHT, 0.4), sw=1.6, light=None)
        c.line("M-2,-50 V-72 M2,-50 V-72", 1, P.AMBER)
    if label:   # a plaque on the front, its words never smaller than the page's smallest lettering
        size, w, h = _plaque(label, k)
        top = -34
        c.path(rounded_rect_d(-w / 2, top, w, h, 2.5), P.WHITE, 1.4)
        fit_label(c, 0, top + h / 2 + size * 0.34, label, size, w - size * 0.9)
    return _at(c, x, y, k)


def time_machine(x: float, y: float, k: float = 1.0, lever_down: bool = True) -> str:
    """The Time Machine of a museum of computing: a riveted cabinet on short legs, tape reels behind glass, three
    gauges, signal lamps, punched tape running out of a slot, and a big lever on a pivot at its side. 92 wide
    without the lever and the tape, 113 tall with the beacon; the cabinet's face ends 18 above the floor. Pulled
    down, the lever's knob is at (66, -27): the height of the sparrow's pointing wing."""
    c = Canvas()
    body = P.TEAL
    trim = darken(body, 0.72)
    for lx in (-34, 34):                                              # turned legs on round feet
        c.shape(f"M{lx - 4.5},-17 Q{lx - 3},-9 {lx - 2.2},-3 H{lx + 2.2} Q{lx + 3},-9 {lx + 4.5},-17 Z",
                P.METAL_DARK, sw=1.6, light=(-1, 0))
        c.shape(ellipse_d(lx, -2, 6, 2.2), P.CHARCOAL, sw=1.4, light=None)
    c.shape(rounded_rect_d(-42, -88, 84, 70, 4), body, sw=2.2, light=(-2.5, -2), shade_k=0.84)
    c.shape(rounded_rect_d(-45, -23, 90, 7, 2.5), trim, sw=1.8, light=None)          # the plinth band
    c.shape(rounded_rect_d(-46, -95, 92, 9, 3), trim, sw=1.8, light=None)            # the cornice
    c.shape("M-6,-95 V-100 Q-6,-107 0,-107 Q6,-107 6,-100 V-95 Z", P.RED, sw=1.6, light=(-1, -1),
            highlight="M-3,-101 V-104")                                               # the beacon
    c.line("M-10,-104 l-4,-3 M10,-104 l4,-3 M0,-110 v-3", 1.3, P.RED)
    # upper panel: two tape reels behind glass, three signal lamps beside them
    c.shape(rounded_rect_d(-36, -82, 58, 30, 3), P.METAL_PALE, sw=1.6, light=None)
    for rx, wound in ((-21, 9.4), (7, 4.6)):        # one reel full, one nearly empty: they read as reels
        c.add(f'<circle cx="{rx}" cy="-68" r="{wound}" fill="{P.DARK_BROWN}" stroke="{INK}" stroke-width=".8"/>')
        spokes = [
            f'M{n(rx + 3.2 * math.cos(math.radians(a - 32)))},{n(-68 - 3.2 * math.sin(math.radians(a - 32)))} '
            f'L{n(rx + 9 * math.cos(math.radians(a - 26)))},{n(-68 - 9 * math.sin(math.radians(a - 26)))} '
            f'A9,9 0 0 0 {n(rx + 9 * math.cos(math.radians(a + 26)))},{n(-68 - 9 * math.sin(math.radians(a + 26)))} '
            f'L{n(rx + 3.2 * math.cos(math.radians(a + 32)))},{n(-68 - 3.2 * math.sin(math.radians(a + 32)))} Z'
            for a in (90, 210, 330)]
        holes = "".join(f'<path d="{d}"/>' for d in spokes)
        # the glass with the spokes cut out, one even-odd path: an SVG mask would print as a raster
        glass = f"M{n(rx - 11)},-68 a11,11 0 1 0 22,0 a11,11 0 1 0 -22,0 Z " + " ".join(spokes)
        c.add(f'<path d="{glass}" fill="{P.METAL_LIGHT}" fill-opacity=".9" fill-rule="evenodd"/>')
        c.add(f'<circle cx="{rx}" cy="-68" r="11" fill="none" stroke="{INK}" stroke-width="1.4"/>'
              f'<g fill="none" stroke="{INK}" stroke-width=".9">{holes}</g>')
        c.add(f'<circle cx="{rx}" cy="-68" r="2" fill="{P.METAL}" stroke="{INK}" stroke-width=".9"/>')
    # the tape: off the full reel, round two guide rollers along the bottom, onto the empty one
    c.line("M-30.4,-68 L-30,-56 H16 L11.6,-68", 1.4, P.DARK_BROWN)
    for gx in (-30, 16):
        c.add(f'<circle cx="{gx}" cy="-56" r="1.8" fill="{P.METAL}" stroke="{INK}" stroke-width=".8"/>')
    c.line("M-34,-80 L-26,-74 M18,-80 L10,-74", 1.6, P.WHITE, 0.7)                   # glint on the glass
    for i, color in enumerate((P.RED, P.SUN, P.GREEN)):
        c.add(f'<circle cx="31" cy="{-77 + i * 10}" r="3.3" fill="{color}" stroke="{INK}" stroke-width="1.3"/>')
    # middle panel: three gauges with needles, two push buttons
    c.shape(rounded_rect_d(-36, -49, 72, 20, 3), darken(body, 0.88), sw=1.5, light=None)
    for gx, turn in ((-27, -40), (-12, 10), (3, 55)):
        c.shape(ellipse_d(gx, -39, 6.4, 6.4), P.CARD, sw=1.4, light=None)
        for t in (-60, 0, 60):
            a = math.radians(t - 90)
            c.line(f"M{n(gx + math.cos(a) * 4.4)},{n(-39 + math.sin(a) * 4.4)} "
                   f"L{n(gx + math.cos(a) * 5.6)},{n(-39 + math.sin(a) * 5.6)}", 0.8)
        a = math.radians(turn - 90)
        c.line(f"M{gx},-39 L{n(gx + math.cos(a) * 4.8)},{n(-39 + math.sin(a) * 4.8)}", 1.3, P.RED)
        c.dot(gx, -39, 1)
    for bx, color in ((19, P.RED), (29, P.GREEN)):
        c.shape(ellipse_d(bx, -39, 3.8, 3.8), color, sw=1.3, light=(-0.8, -0.8))
    # the slot with punched tape running out of it, down to the floor
    c.shape(rounded_rect_d(-34, -28, 26, 4, 1.5), P.CHARCOAL, sw=1.2, light=None)
    tape = "M-26,-26 Q-30,-14 -40,-10 Q-52,-6 -50,0 H-70"
    c.line(tape, 6.6)
    c.line(tape, 4.6, P.YELLOW_PALE)
    c.add(f'<path d="{tape}" fill="none" stroke="{INK}" stroke-width="1.6" stroke-dasharray="0.1 3.4" '
          f'stroke-linecap="round" opacity=".7"/>')
    for rx, ry in ((-39, -85), (39, -85), (-39, -26), (39, -26)):                    # rivets
        c.add(f'<circle cx="{rx}" cy="{ry}" r="1.3" fill="{trim}" stroke="{INK}" stroke-width=".6"/>')
    # the lever: a slotted quadrant on the side, the arm on its pivot, a red knob
    c.shape("M42,-70 A16,16 0 0 1 42,-38 Z", P.METAL, sw=1.6, light=None)
    c.line("M44,-66 A12,12 0 0 1 44,-42", 2, P.CHARCOAL)
    end = (66, -27) if lever_down else (56, -86)
    c.line(f"M44,-54 L{end[0]},{end[1]}", 5.8)
    c.line(f"M44,-54 L{end[0]},{end[1]}", 3.2, P.METAL_DARK)
    c.add(f'<circle cx="44" cy="-54" r="3.4" fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="1.4"/>')
    c.shape(ellipse_d(end[0], end[1], 6, 6), P.RED, sw=1.6, light=(-1.2, -1.2),
            highlight=f"M{end[0] - 3},{end[1] - 1} q1,-3 3,-3")
    return _at(c, x, y, k)


def _sign_lines(text: str, size: float, room: float) -> list[str]:
    """The words of a sign on one line, or on two when one would be too wide."""
    words = text.split()
    if letter_width(text, size) <= room or len(words) < 2:
        return [text]
    cut = min(range(1, len(words)), key=lambda i: abs(len(" ".join(words[:i])) - len(text) / 2))
    return [" ".join(words[:cut]), " ".join(words[cut:])]


def _sign_board(c: Canvas, cx: float, top: float, text: str, k: float, room: float = 60,
                color: str = P.RED) -> tuple[float, float]:
    """A white museum sign with a thin frame and red lettering, its top edge at `top`; returns (w, h)."""
    size = max(10.0, LETTERING_MIN / k)
    lines = _sign_lines(text, size, room)
    w = max(letter_width(line, size) for line in lines) + size * 0.9
    h = len(lines) * size * 1.12 + size * 0.55
    c.shape(rounded_rect_d(cx - w / 2, top, w, h, 2.5), P.WHITE, sw=1.6, light=None)
    c.path(rounded_rect_d(cx - w / 2 + 2, top + 2, w - 4, h - 4, 1.5), "none", 0.8, color)
    for i, line in enumerate(lines):
        fit_label(c, cx, top + size * 0.3 + (i + 1) * size * 1.12 - size * 0.2, line, size, w - size * 0.6, color)
    return w, h


def sign_size(text: str, k: float, room: float = 60) -> tuple[float, float]:
    """The (width, height) at scale 1 of the sign `_sign_board` draws for these words at scale k."""
    size = max(10.0, LETTERING_MIN / k)
    lines = _sign_lines(text, size, room)
    return max(letter_width(line, size) for line in lines) + size * 0.9, len(lines) * size * 1.12 + size * 0.55


def sign_stand(x: float, y: float, k: float = 1.0, text: str = "", post: float = 40) -> str:
    """A museum sign on its own stand: a round foot, a brass post `post` high, the sign on top."""
    c = Canvas()
    w, h = sign_size(text, k)
    c.shape(ellipse_d(0, -2, 11, 3.2), P.CHARCOAL, sw=1.6, light=None)
    c.line(f"M0,-3 V{-post}", 5)
    c.line(f"M0,-3 V{-post}", 2.6, P.AMBER)
    c.line(f"M-6,{-post} H6", 3.4)
    _sign_board(c, 0, -post - h, text, k)
    return _at(c, x, y, k)


def stanchion_sign(x: float, y: float, k: float = 1.0, text: str = "", span: float = 30) -> str:
    """A museum rope barrier: two brass posts `span` either side of the middle, a red velvet rope sagging between
    them and, when there are words, a little sign hanging from the rope's middle on two rings."""
    c = Canvas()
    room = max(96.0, 2 * span)              # one line, squeezed if need be, as the rope is low
    sw, sh = sign_size(text, k, room) if text else (0, 0)
    post = max(32.0, sh + 16)
    for dx in (-span, span):
        c.shape(ellipse_d(dx, -2, 8, 2.6), P.CHARCOAL, sw=1.5, light=None)
        c.line(f"M{dx},-3 V{-post}", 4.8)
        c.line(f"M{dx},-3 V{-post}", 2.6, P.SUN)
        c.shape(ellipse_d(dx, -post - 2, 3.6, 3.6), P.SUN, sw=1.3, light=(-0.8, -0.8))
    rope = f"M{-span},{-post + 1} Q0,{-post + 22} {span},{-post + 1}"
    c.line(rope, 5)
    c.line(rope, 3, P.RED)
    if text:
        low = -post + 11.5         # the rope's lowest point
        top = low + 3
        c.line(f"M{n(-sw * 0.3)},{n(top + 1)} L-3,{n(low)} M{n(sw * 0.3)},{n(top + 1)} L3,{n(low)}", 1.1)
        _sign_board(c, 0, top, text, k, room)
    return _at(c, x, y, k)


def burst(x: float, y: float, r: float = 30, text: str = "", color: str = P.SUN) -> str:
    """A comic starburst with a word in it; the word always stays inside the star."""
    c = Canvas()
    points = []
    for i in range(24):
        radius = r if i % 2 == 0 else r * 0.7
        a = math.tau * i / 24 + 0.1
        points.append(f"{n(math.cos(a) * radius)},{n(math.sin(a) * radius * 0.8)}")
    c.shape("M" + " L".join(points) + " Z", color, sw=2, light=None)
    if text:
        size = r * 0.4
        fit_label(c, 0, size * 0.36, text, size, r * 1.2, darken(P.RED, 0.9))
    return _at(c, x, y)


# ============================================================================ village
def fence_with_hole(x: float, y: float, k: float = 1.0, w: float = 120, color: str = P.RED) -> str:
    """A plank fence with one plank missing (the hole the dog goes through)."""
    c = Canvas()
    hw = w / 2
    c.shape(f"M{-hw},-30 H{hw} V-25 H{-hw} Z", darken(color, 0.85), sw=1.6, light=None)
    c.shape(f"M{-hw},-12 H{hw} V-7 H{-hw} Z", darken(color, 0.85), sw=1.6, light=None)
    px, i = -hw + 2, 0
    while px < hw - 8:
        if i != 3:
            c.shape(f"M{n(px)},0 V-38 L{n(px + 4)},-42 L{n(px + 8)},-38 V0 Z", color, sw=1.5, light=(-1, 0))
        px += 11
        i += 1
    return _at(c, x, y, k)


def well(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.shape("M-18,0 V-22 H18 V0 Z", P.STONE, sw=1.8, light=(-1, -1), stipple=(-18, -22, 36, 22, 14, "even"))
    c.line("M-14,-22 V-52 M14,-22 V-52", 2.6, P.WOOD_DARK)
    c.shape("M-20,-50 L0,-62 L20,-50 Z", P.RED, sw=1.6, light=None)
    c.line("M-14,-42 H14", 1.6)
    c.line("M0,-42 V-30", 1)
    c.add(bucket_small(0, -26, 0.5))
    return _at(c, x, y, k)


def bucket_small(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.shape("M-10,-16 L-8,0 H8 L10,-16 Z", P.METAL, sw=1.6, light=None)
    return _at(c, x, y, k)


def _tier(c: Canvas, at, base: float, w: float, apex: float) -> None:
    """One tier of a pine's branches in a frame `at(u, v)`: a triangle `w` either side of the axis at `base`, its
    tip at `apex`, the lower edge drooping in notches."""
    d = (f"M{at(-w, base)} Q{at(-w * 0.75, base - 3)} {at(-w * 0.5, base + 0.5)} "
         f"Q{at(-w * 0.25, base - 3)} {at(0, base + 1)} Q{at(w * 0.25, base - 3)} {at(w * 0.5, base + 0.5)} "
         f"Q{at(w * 0.75, base - 3)} {at(w, base)} Q{at(w * 0.3, (base + apex) / 2 + 2)} {at(0, apex)} "
         f"Q{at(-w * 0.3, (base + apex) / 2 + 2)} {at(-w, base)} Z")
    c.shape(d, P.FIR, sw=1.6, light=(-1.6, -1.4), shade_k=0.76)
    c.line(f"M{at(-w * 0.45, base - 5)} L{at(-w * 0.25, base - 9)} M{at(w * 0.15, base - 6)} "
           f"L{at(w * 0.3, base - 10)}", 1, P.LEAF_DARK)


def _fallen_top(c: Canvas, bx: float, by: float, turn: float) -> None:
    """The top a storm broke off a pine, lying on its side: drawn upright in its own frame (the break at the origin,
    the tip 80 up) and turned by `turn` degrees about the break, which ends at (bx, by)."""
    a = math.radians(turn)

    def at(u: float, v: float) -> str:
        return f"{n(bx + u * math.cos(a) - v * math.sin(a))},{n(by + u * math.sin(a) + v * math.cos(a))}"

    # the bare piece of trunk under the crown, its jagged broken end towards the stump
    c.shape(f"M{at(-5, 1)} L{at(-3.6, -24)} L{at(3.6, -24)} L{at(5, 1)} L{at(2.6, 4)} L{at(0.6, 1)} "
            f"L{at(-1.4, 4.6)} L{at(-3.2, 1.2)} Z", P.TRUNK, sw=1.5, light=(-1, -1), shade_k=0.8)
    c.path(f"M{at(-4.5, 0.6)} L{at(-3.2, 1.2)} L{at(-1.4, 4.6)} L{at(0.6, 1)} L{at(2.6, 4)} L{at(4.5, 0.6)} "
           f"Q{at(0, -1.8)} {at(-4.5, 0.6)} Z", P.WOOD_PALE, 0.9)
    c.line(f"M{at(-1.5, -6)} L{at(-1.2, -14)} M{at(1.5, -12)} L{at(1.3, -20)}", 0.9, opacity=0.55)
    # three tiers of branches, the higher over the lower
    for base, w, apex in ((-18, 20, -46), (-36, 16, -64), (-53, 11, -81)):
        _tier(c, at, base, w, apex)


def broken_pine(x: float, y: float, k: float = 1.0) -> str:
    """A pine snapped by a storm: the tall stump of its trunk, barked, with a jagged splintered break of pale wood
    and a few needled branches low down; the top it lost - a pine crown of three tiers on its piece of trunk -
    lies on the ground to its right, its broken end against the stump. 114 wide (from -22 to 92), 78 tall."""
    c = Canvas()
    _fallen_top(c, 10, -23, 100)

    def up(u: float, v: float) -> str:
        return f"{n(u)},{n(v)}"

    for base, w, apex in ((-27, 23, -50), (-43, 17, -61)):     # the low branches it kept, behind the trunk
        _tier(c, up, base, w, apex)
    # the standing trunk: a flared foot, the bark, and the break: splinters of pale inner wood with a few bark
    # slivers still standing at its rim
    c.shape("M-10,0 Q-6.5,-3 -6.6,-12 L-5.6,-64 L5.6,-64 L6.6,-12 Q6.5,-3 10,0 Z", P.TRUNK, sw=1.8,
            light=(-1.6, 0), shade_k=0.78)
    c.shape("M-5.8,-63.4 L-4.4,-71 L-2.8,-66.6 L-1,-77 L0.8,-67.6 L2.6,-73 L4.2,-66 L5.8,-63.4 Q0,-61.4 "
            "-5.8,-63.4 Z", P.WOOD_PALE, sw=1.3, light=(0.8, 0), shade_k=0.86)
    c.line("M-1,-75 L-0.6,-66.4 M2.6,-71 L2.2,-65.6 M-4.3,-69.5 L-4,-65", 0.7, darken(P.WOOD_PALE, 0.62))
    c.shape("M-5.9,-63.6 L-6.6,-70.4 L-4.2,-64.4 Z", P.TRUNK, sw=1.1, light=None)      # a sliver of bark
    c.shape("M5.6,-63.6 L10.8,-71.6 L8.4,-63.8 Z", P.WOOD_PALE, sw=1.1, light=None)    # a splinter bent out
    c.line("M-3,-6 q-1,-6 0,-13 M2.4,-14 q1,-7 0,-14 M-2.6,-31 q-1,-6 0,-12 M2.6,-44 q1,-6 0,-11 "
           "M-2.2,-55 q-0.8,-4 0,-7", 1, opacity=0.55)
    c.line("M-7,-1 q-3,-1 -5,1 M7,-1 q3,-1 5,1", 1.2, opacity=0.6)                      # roots
    c.tube("M-6,-18 L-11,-22", P.TRUNK, 2, sw=1.1, shaded=False)                      # a dead stub
    return _at(c, x, y, k)


def _route_icon(c: Canvas, kind: str, x: float, y: float, s: float) -> None:
    """A little picture of a stop on the route, standing on (x, y), `s` tall and at most 1.1 s wide: a well, a
    pine snapped in two, a red fence with a plank missing."""
    if kind == "well":
        c.shape(f"M{n(x - s * .4)},{n(y)} V{n(y - s * .38)} H{n(x + s * .4)} V{n(y)} Z", P.STONE, sw=1.1, light=None)
        c.line(f"M{n(x - s * .3)},{n(y - s * .38)} V{n(y - s * .8)} M{n(x + s * .3)},{n(y - s * .38)} V{n(y - s * .8)}",
               1.2, P.WOOD_DARK)
        c.shape(f"M{n(x - s * .48)},{n(y - s * .74)} L{n(x)},{n(y - s)} L{n(x + s * .48)},{n(y - s * .74)} Z", P.RED,
                sw=1.1, light=None)
    elif kind == "pine":
        # the fallen top: a green fir lying on its side, pointing right, on its piece of trunk
        c.line(f"M{n(x - s * .2)},{n(y - s * .2)} L{n(x + s * .04)},{n(y - s * .2)}", 2.2, P.TRUNK)
        c.shape(f"M{n(x)},{n(y)} L{n(x)},{n(y - s * .5)} L{n(x + s * .62)},{n(y - s * .12)} "
                f"Q{n(x + s * .3)},{n(y + s * .02)} {n(x)},{n(y)} Z", P.FIR, sw=1, light=None)
        # the stump with its jagged break of pale wood
        tx = x - s * .3
        c.shape(f"M{n(tx - s * .11)},{n(y)} V{n(y - s * .78)} L{n(tx - s * .05)},{n(y - s * .9)} "
                f"L{n(tx)},{n(y - s * .8)} L{n(tx + s * .05)},{n(y - s)} L{n(tx + s * .11)},{n(y - s * .78)} V{n(y)} Z",
                P.TRUNK, sw=1.1, light=None)
        c.shape(f"M{n(tx - s * .3)},{n(y - s * .28)} L{n(tx)},{n(y - s * .56)} L{n(tx + s * .3)},{n(y - s * .28)} "
                f"Q{n(tx)},{n(y - s * .34)} {n(tx - s * .3)},{n(y - s * .28)} Z", P.FIR, sw=1, light=None)
    else:
        c.line(f"M{n(x - s * .52)},{n(y - s * .32)} H{n(x + s * .52)} M{n(x - s * .52)},{n(y - s * .12)} "
               f"H{n(x + s * .52)}", 1.6, darken(P.RED, 0.8))
        for px in (-0.46, -0.22, 0.26, 0.5):       # the third plank is missing
            px = x + s * px - s * 0.08
            c.shape(f"M{n(px)},{n(y)} V{n(y - s * .58)} L{n(px + s * .08)},{n(y - s * .68)} "
                    f"L{n(px + s * .16)},{n(y - s * .58)} V{n(y)} Z", P.RED, sw=1, light=None)


def _program_layout(title: str, k: float) -> dict:
    """The measures of the program signboard at scale k: lettering, rows, the sheet's even margin, the board."""
    size = max(9.6, LETTERING_MIN / k)               # the numbers
    tsize = size * 1.15                              # the title
    icon = max(21.0, size * 1.5)                     # a stop's picture, this tall
    r = size * 0.66                                  # a number's disc
    rows = [(tsize * 0.98, tsize * 0.38)] if title else []
    rows += [(2 * r, size * 0.45), (icon, 0)]       # (height, gap after it)
    content_h = sum(hh + gap for hh, gap in rows)
    step = max(icon * 1.35, 2 * r + size * 2.2)
    cell = max(2 * r, icon * 1.1)                    # the widest thing in a stop's column
    content_w = max(2 * step + cell, letter_width(title, tsize) if title else 0)
    pad = max(size * 0.6, 0.16 * content_h)          # even on all four sides, over 12 % of the sheet's height
    frame = 4.0
    w = content_w + 2 * pad + 2 * frame
    h = content_h + 2 * pad + 2 * frame
    return {"size": size, "tsize": tsize, "icon": icon, "r": r, "step": step, "pad": pad, "frame": frame,
            "w": w, "h": h, "content_w": content_w, "cell": cell}


def program_card_size(title: str, k: float = 1.0, post: float = 56) -> tuple[float, float]:
    """(width, height) at scale 1 of the signboard `program_card` draws at scale k, its post `post` high."""
    m = _program_layout(title, k)
    return m["w"] + 4, m["h"] + post


def program_card(x: float, y: float, k: float = 1.0, title: str = "", lines: int = 3, post: float = 56) -> str:
    """The program as a signboard on a post: a sheet pinned to a wooden board with the route's numbered stops
    as little pictures - 1 the well, 2 the broken pine, 3 the red fence - arrows between them. `lines` is how many
    stops are shown (1 to 3), `post` how high the board's lower edge is. Everything on the sheet keeps the same
    margin from its edges on all four sides."""
    c = Canvas()
    m = _program_layout(title, k)
    w, h, pad, frame, size, r = m["w"], m["h"], m["pad"], m["frame"], m["size"], m["r"]
    top = -post - h
    c.shape(f"M-3,0 V{n(top + 8)} H3 V0 Z", P.WOOD_DARK, sw=1.6, light=None)            # the post
    c.shape(rounded_rect_d(-w / 2, top, w, h, 2.5), P.WOOD, sw=1.9, light=(-1.5, -1.5), shade_k=0.85)
    c.shape(rounded_rect_d(-w / 2 + frame, top + frame, w - 2 * frame, h - 2 * frame, 1.5), P.CARD, sw=1.3,
            light=None)
    for px in (-w / 2 + frame + pad * 0.45, w / 2 - frame - pad * 0.45):     # pins, in the sheet's corners
        c.add(f'<circle cx="{n(px)}" cy="{n(top + frame + pad * 0.45)}" r="1.6" fill="{P.RED}" stroke="{INK}" '
              f'stroke-width=".7"/>')
    row = top + frame + pad
    if title:
        tsize = m["tsize"]
        fit_label(c, 0, row + tsize * 0.74, title, tsize, m["content_w"])
        row += tsize * (0.98 + 0.38)
    stops = ("well", "pine", "fence")[:max(1, min(3, lines))]
    step = m["step"]
    left = -(step * (len(stops) - 1)) / 2
    for i, kind in enumerate(stops):
        cx = left + step * i
        cy = row + r
        c.add(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{(P.BLUE, P.GREEN, P.RED)[i]}" '
              f'stroke="{INK}" stroke-width="1"/>')
        fit_label(c, cx, cy + size * 0.36, str(i + 1), size, r * 1.6, P.WHITE)
        _route_icon(c, kind, cx, row + 2 * r + size * 0.45 + m["icon"], m["icon"])
        if i < len(stops) - 1:               # an arrow on to the next stop
            x0, x1 = cx + r + size * 0.35, cx + step - r - size * 0.35
            c.line(f"M{n(x0)},{n(cy)} H{n(x1 - 3)}", 1.3)
            c.path(f"M{n(x1 - 4)},{n(cy - 2.6)} L{n(x1)},{n(cy)} L{n(x1 - 4)},{n(cy + 2.6)} Z", INK, 0.8)
    return _at(c, x, y, k)


def envelope(x: float, y: float, k: float = 1.0, turn: float = 0) -> str:
    c = Canvas()
    c.shape("M-12,0 V-16 H12 V0 Z", P.CARD, sw=1.4, light=None)
    c.line("M-12,-16 L0,-7 L12,-16", 1.2)
    c.add(f'<circle cx="0" cy="-7" r="2.6" fill="{P.RED}" stroke="{INK}" stroke-width=".8"/>')
    return _at(c, x, y, k, turn=turn)


# ============================================================================ shop
def checkout(x: float, y: float, k: float = 1.0) -> str:
    """A shop till: a counter with a conveyor and a scanner window shining a red cross. 150 wide, 60 tall."""
    c = Canvas()
    c.shape("M-75,0 V-44 H75 V0 Z", P.METAL_LIGHT, sw=2, light=(-2, -2), shade_k=0.88)
    c.shape(rounded_rect_d(-78, -50, 156, 8, 2), P.CHARCOAL, sw=1.8, light=None)
    for i in range(12):
        c.line(f"M{-72 + i * 12},-49 v6", 0.8, P.METAL)
    c.shape(rounded_rect_d(20, -52, 30, 10, 2), P.CHARCOAL, sw=1.4, light=None)
    c.line("M35,-50 V-60 M25,-55 H45", 1.8, P.RED)
    c.shape(rounded_rect_d(52, -78, 20, 26, 3), P.BEIGE, sw=1.6, light=None)       # the till with its display
    c.shape(rounded_rect_d(55, -75, 14, 8, 1), P.SCREEN_DARK, sw=1, light=None)
    goods = ((-60, P.YELLOW, "box"), (-40, P.RED, "can"), (-20, P.GREEN, "bottle"), (0, P.SUN, "banana"))
    for gx, color, kind in goods:
        if kind == "box":
            c.shape(f"M{gx - 8},-50 V-66 H{gx + 8} V-50 Z", color, sw=1.4, light=None)
            c.line(f"M{gx - 5},-56 h4 M{gx - 1},-56 h1 M{gx + 1},-56 h3", 2)
        elif kind == "can":
            c.shape(f"M{gx - 6},-50 V-64 H{gx + 6} V-50 Z", color, sw=1.4, light=None)
        elif kind == "bottle":
            c.shape(f"M{gx - 5},-50 V-62 L{gx - 2},-68 V-74 H{gx + 2} V-68 L{gx + 5},-62 V-50 Z", color, sw=1.4,
                    light=None)
        else:
            c.shape(f"M{gx - 10},-54 Q{gx},-48 {gx + 10},-58 Q{gx},-52 {gx - 10},-54 Z", color, sw=1.4, light=None)
    return _at(c, x, y, k)


def _curve_points(points: list[tuple[float, float]], step: float = 2.0) -> list[tuple[float, float]]:
    """The smooth line through the midpoints of `points` (as the receipt is drawn), sampled every `step` units."""
    out = [points[0]]
    cur = points[0]
    pieces = []
    for a, b in zip(points[1:], points[2:], strict=False):
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        pieces.append((cur, a, mid))
        cur = mid
    pieces.append((cur, ((cur[0] + points[-1][0]) / 2, (cur[1] + points[-1][1]) / 2), points[-1]))
    for p0, p1, p2 in pieces:
        length = math.dist(p0, p1) + math.dist(p1, p2)
        count = max(2, int(length / step))
        for i in range(1, count + 1):
            t = i / count
            out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                        (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    return out


def receipt_end(width: float, total: str) -> float:
    """How long a straight run the receipt's printed end needs (make the last segment of its path this long)."""
    size = max(LETTERING_MIN + 0.5, width * 0.85)
    return letter_width(total, size) + size * 1.8 if total else 0


def receipt(points: list[tuple[float, float]], width: float = 14, total: str = "") -> str:
    """A long till receipt: a paper strip curling along a path of points, printed lines across it, spreading at the
    end into a flat piece with a torn zigzag edge and the total printed on it in red. The last segment of the path
    should be at least `receipt_end(width, total)` long and fairly straight: the total is printed along it."""
    c = Canvas()
    line = _curve_points(points)
    lengths = [0.0]
    for a, b in zip(line, line[1:], strict=False):
        lengths.append(lengths[-1] + math.dist(a, b))
    full = lengths[-1]
    size = max(LETTERING_MIN + 0.5, width * 0.85)
    end = receipt_end(width, total)
    wide = max(width, size * 2.3) if total else width
    ramp = width * 3.5

    def half(s: float) -> float:
        t = min(1.0, max(0.0, (s - (full - end - ramp)) / ramp)) if total else 0.0
        return (width + (wide - width) * t * t * (3 - 2 * t)) / 2

    lefts, rights, normals = [], [], []
    for i, (x, y) in enumerate(line):
        a, b = line[max(0, i - 1)], line[min(len(line) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        normals.append((nx, ny))
        h = half(lengths[i])
        lefts.append((x + nx * h, y + ny * h))
        rights.append((x - nx * h, y - ny * h))
    # the torn end: a zigzag from the left edge to the right
    ex, ey = line[-1]
    nx, ny = normals[-1]
    tx, ty = ny, -nx                       # along the paper, outwards
    teeth = max(5, int(wide / 4.5)) | 1
    zig = []
    for j in range(1, teeth):
        u = wide / 2 - wide * j / teeth       # from the left edge across to the right
        out = 3.4 if j % 2 else -0.8
        zig.append((ex + nx * u + tx * out, ey + ny * u + ty * out))
    pts = lefts + zig + list(reversed(rights))
    d = "M" + " L".join(f"{n(px)},{n(py)}" for px, py in pts) + " Z"
    c.shape(d, P.CARD, sw=1.7, light=(-0.8, -1.2), shade_k=0.9)
    # printed lines across the narrow strip: item, price, item...
    rnd = random.Random(int(full))
    s, i = 5.0, 0
    stop = full - end - ramp * 0.5 if total else full - 4
    while s < stop:
        while i < len(lengths) - 1 and lengths[i] < s:
            i += 1
        (x, y), (nx, ny) = line[i], normals[i]
        h = half(s) - 2.4
        a, b = rnd.uniform(0.3, 0.62), rnd.uniform(0.72, 0.84)      # an item's name, then its price
        segs = ((0, a), (b, 1)) if rnd.random() < 0.8 else ((0, rnd.uniform(0.5, 1)),)
        for u0, u1 in segs:
            c.line(f"M{n(x + nx * (h - 2 * h * u0))},{n(y + ny * (h - 2 * h * u0))} "
                   f"L{n(x + nx * (h - 2 * h * u1))},{n(y + ny * (h - 2 * h * u1))}", 0.9, P.CHARCOAL, 0.45)
        s += 3.6
    if total:
        # on the flat end: a dashed rule, then the total in red
        angle = math.degrees(math.atan2(ty, tx))
        if abs(angle) > 90:
            angle += 180
        mid = full - end * 0.5
        j = min(range(len(lengths)), key=lambda q: abs(lengths[q] - mid))
        cx, cy = line[j]
        rule = full - end + size * 0.25
        q = min(range(len(lengths)), key=lambda r: abs(lengths[r] - rule))
        (rx, ry), (rnx, rny) = line[q], normals[q]
        hw = wide / 2 - 3
        c.add(f'<path d="M{n(rx + rnx * hw)},{n(ry + rny * hw)} L{n(rx - rnx * hw)},{n(ry - rny * hw)}" '
              f'stroke="{P.CHARCOAL}" stroke-width="1" stroke-dasharray="2 2" stroke-opacity=".6"/>')
        a = math.radians(angle)
        fit_label(c, cx - math.sin(a) * size * 0.36, cy + math.cos(a) * size * 0.36, total, size, end - size,
                  P.RED, turn=angle)
    return c.render()


def shop_shelf(x: float, y: float, k: float = 1.0, seed: int = 0) -> str:
    """A shop's shelving with boxes, jars and bottles; 120 wide, 120 tall."""
    rnd = random.Random(seed)
    c = Canvas()
    c.shape("M-60,0 V-120 H60 V0 Z", P.WOOD_LIGHT, sw=2, light=(-2, -2))
    for row in range(3):
        top = -114 + row * 38
        c.path(f"M-54,{top} H54 V{top + 32} H-54 Z", darken(P.WOOD_LIGHT, 0.85), 1.4)
        gx = -50.0
        while gx < 42:
            w = rnd.choice((8, 10, 12))
            h = rnd.choice((16, 20, 24))
            color = rnd.choice((P.RED, P.YELLOW, P.GREEN, P.BLUE, P.ORANGE, P.PINK))
            c.path(f"M{n(gx)},{top + 32} V{top + 32 - h} H{n(gx + w)} V{top + 32} Z", color, 1.2)
            gx += w + 2
    return _at(c, x, y, k)


def baguette(x: float, y: float, k: float = 1.0, turn: float = -20) -> str:
    c = Canvas()
    c.shape("M-24,0 Q-24,-8 -16,-8 H18 Q26,-8 24,0 Q20,4 -18,4 Q-24,4 -24,0 Z", P.AMBER, sw=1.6, light=(-1, -1))
    c.line("M-12,-6 l4,6 M-2,-6 l4,6 M8,-6 l4,6", 1.2)
    return _at(c, x, y, k, turn=turn)


# ============================================================================ sickroom
def sick_computer(x: float, y: float, k: float = 1.0) -> str:
    """The old computer with a fever: an ice bag on its head, flushed cheeks, a thermometer sticking out of its
    drive slot, and on its screen a spiky germ sweeping the files away with a broom. 90 wide, 96 tall."""
    c = Canvas()
    c.add(doodle_at("monitor", 0, 0, 90))
    for dx in (-30, 30):
        c.add(f'<ellipse cx="{dx}" cy="-44" rx="6" ry="3.6" fill="{P.PINK}" opacity=".8"/>')
    # the germ: a round body with knobbed spikes, cross eyebrows, a broom in its hand
    gx, gy = 9, -58
    for i in range(9):
        a = math.tau * i / 9 + 0.2
        c.line(f"M{n(gx + math.cos(a) * 7)},{n(gy + math.sin(a) * 7)} "
               f"L{n(gx + math.cos(a) * 11)},{n(gy + math.sin(a) * 11)}", 1.4, P.LEAF_DARK)
        c.add(f'<circle cx="{n(gx + math.cos(a) * 11.5)}" cy="{n(gy + math.sin(a) * 11.5)}" r="1.7" '
              f'fill="{P.RED}" stroke="{INK}" stroke-width=".6"/>')
    c.shape(ellipse_d(gx, gy, 8, 8), P.GREEN, sw=1.4, light=(-1, -1))
    c.add(f'<circle cx="{gx - 2.6}" cy="{gy - 1}" r="1.9" fill="{P.WHITE}"/><circle cx="{gx + 2.6}" cy="{gy - 1}" '
          f'r="1.9" fill="{P.WHITE}"/>')
    c.dot(gx - 2.2, gy - 0.8, 0.9)
    c.dot(gx + 2.2, gy - 0.8, 0.9)
    c.line(f"M{gx - 5},{gy - 5} l4,2 M{gx + 5},{gy - 5} l-4,2 M{gx - 2.5},{gy + 3.6} q2.5,-1.6 5,0", 0.9)
    c.line(f"M{gx - 7},{gy + 3} L{gx - 22},{gy + 12}", 1.5, P.WOOD_DARK)           # the broom
    c.shape(f"M{gx - 20},{gy + 10} L{gx - 28},{gy + 13} L{gx - 26},{gy + 18} L{gx - 18},{gy + 14} Z", P.AMBER,
            sw=1, light=None)
    c.line(f"M{gx - 29},{gy + 6} l-3,-1 M{gx - 30},{gy + 10} l-4,0", 0.9, P.SCREEN_TEXT)  # swept bits flying
    # the thermometer in the drive slot, its red column high
    c.add(f'<g transform="translate(15,-29) rotate(-28)"><rect x="0" y="-2.3" width="24" height="4.6" rx="2.3" '
          f'fill="{P.WHITE}" stroke="{INK}" stroke-width="1.1"/><rect x="1" y="-0.9" width="17" height="1.8" '
          f'fill="{P.RED}"/><path d="M6,-2.3 v1.4 M10,-2.3 v1.4 M14,-2.3 v1.4" stroke="{INK}" stroke-width=".6"/></g>')
    # the ice bag on its head
    c.shape("M-24,-80 Q-26,-90 -12,-92 Q2,-96 14,-91 Q24,-88 22,-80 Q0,-76 -24,-80 Z", P.SKY_DEEP, sw=1.6,
            light=(-1, -1.4), stipple=(-24, -94, 46, 16, 10, "bottom"))
    c.shape(rounded_rect_d(18, -93, 8, 6, 1.6), P.RED, sw=1.2, light=None)
    c.line("M-14,-88 q3,-2 6,0 M0,-89 q3,-2 6,0", 1, P.WHITE, 0.8)
    return _at(c, x, y, k)


def medicine(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.shape("M-7,0 V-18 Q-7,-22 -3,-22 V-27 H3 V-22 Q7,-22 7,-18 V0 Z", P.AMBER, sw=1.4, light=(-1, -1))
    c.shape(rounded_rect_d(-4, -31, 8, 5, 1.6), P.WHITE, sw=1.2, light=None)
    c.path("M-5.5,-15.5 H5.5 V-4.5 H-5.5 Z", P.WHITE, 1)          # the label, the red cross well inside it
    c.line("M0,-13.2 V-6.8 M-3.2,-10 H3.2", 1.5, P.RED)
    return _at(c, x, y, k)


def floppy(x: float, y: float, k: float = 1.0, color: str = P.CHARCOAL, turn: float = 0) -> str:
    c = Canvas()
    c.shape("M-12,0 V-24 H10 L12,-22 V0 Z", color, sw=1.5, light=None)
    c.path("M-6,-24 H6 V-16 H-6 Z", P.METAL_LIGHT, 1)
    c.path("M-8,-10 H8 V0 H-8 Z", P.CARD, 1)
    c.line("M-5,-6 h10", 0.8, opacity=0.6)
    return _at(c, x, y, k, turn=turn)


# ============================================================================ nursery: counting letters
def letter_beads(x0: float, y: float, text: str, r: float = 10) -> str:
    """A row of coloured circles, one per letter, a white one for every space: counting symbols."""
    c = Canvas()
    colors = (P.RED, P.YELLOW, P.GREEN, P.BLUE, P.ORANGE, P.PINK, P.TEAL, P.VIOLET)
    for i, ch in enumerate(text):
        cx = x0 + i * r * 2.2
        fill = P.WHITE if ch == " " else colors[i % len(colors)]
        c.shape(ellipse_d(cx, y - r, r, r), fill, sw=1.6, light=None)
        if ch != " ":
            _label(c, cx, y - r * 0.6, ch, r * 1.1, P.WHITE if fill not in (P.YELLOW, P.WHITE) else INK)
    return c.render()


def cube(x: float, y: float, k: float = 1.0, color: str = P.RED, letter: str = "") -> str:
    """A toy block, 30 high."""
    c = Canvas()
    c.shape("M-15,0 V-30 H15 V0 Z", color, sw=1.8, light=(-2, -2))
    c.shape("M-15,-30 L-9,-36 H21 L15,-30 Z", lighten(color, 0.25), sw=1.6, light=None)
    c.shape("M15,0 V-30 L21,-36 V-6 Z", darken(color, 0.8), sw=1.6, light=None)
    if letter:
        _label(c, 0, -9, letter, 18, P.WHITE)
    return _at(c, x, y, k)


def giant_pencil(x: float, y: float, k: float = 1.0, length: float = 80, turn: float = -60,
                 color: str = P.YELLOW) -> str:
    c = Canvas()
    w = 9
    c.shape(f"M0,{-w / 2} H{length - 18} V{w / 2} H0 Z", color, sw=1.6, light=None)
    c.shape(f"M{length - 18},{-w / 2} L{length},0 L{length - 18},{w / 2} Z", P.WOOD_PALE, sw=1.6, light=None)
    c.path(f"M{length - 6},-1.4 L{length},0 L{length - 6},1.4 Z", INK, 1)
    c.shape(f"M-8,{-w / 2} H0 V{w / 2} H-8 Z", P.PINK, sw=1.6, light=None)
    return _at(c, x, y, k, turn=turn)



def wall_clock(x: float, y: float, k: float = 1.0) -> str:
    """A round wall clock; the origin is its centre."""
    c = Canvas()
    c.shape(ellipse_d(0, 0, 24, 24), P.WOOD, sw=2, light=None)
    c.shape(ellipse_d(0, 0, 19, 19), P.CARD, sw=1.6, light=None)
    for i in range(12):
        a = math.radians(i * 30)
        c.line(f"M{n(math.sin(a) * 15)},{n(-math.cos(a) * 15)} L{n(math.sin(a) * 17)},{n(-math.cos(a) * 17)}", 1.2)
    c.line("M0,0 L0,-11 M0,0 L8,4", 2)
    c.dot(0, 0, 2)
    return _at(c, x, y, k)


def cactus(x: float, y: float, k: float = 1.0) -> str:
    """A cactus in a terracotta pot, a pink flower on top. 22 wide, 40 tall."""
    c = Canvas()
    c.shape("M-6,-12 V-30 Q-6,-36 0,-36 Q6,-36 6,-30 V-12 Z", P.LEAF, sw=1.5, light=(-1, -1))
    c.shape("M6,-20 H10 Q12,-20 12,-24 V-28 Q12,-31 9,-31 Q7,-31 7,-28 V-24 H6 Z", P.LEAF, sw=1.3, light=None)
    c.shape("M-6,-17 H-10 Q-12,-17 -12,-21 V-24 Q-12,-27 -9,-27 Q-7,-27 -7,-24 V-21 H-6 Z", P.LEAF, sw=1.3,
            light=None)
    c.line("M-3,-32 l-2,-1 M3,-28 l2,-1 M-2,-22 l-2,-1 M2,-16 l2,-1", 0.9)
    c.shape("M-4,-36 Q0,-42 4,-36 Q0,-34 -4,-36 Z", P.PINK, sw=1, light=None)
    c.shape("M-9,-12 H9 L7,0 H-7 Z", P.TERRACOTTA, sw=1.6, light=(-1, -1))
    return _at(c, x, y, k)


def bee(x: float, y: float, k: float = 1.0) -> str:
    """A bee with a dotted flight path behind it; the origin is the bee."""
    c = Canvas()
    c.add(f'<path d="M-6,0 q-10,-10 -18,-2 q-8,8 -16,0" fill="none" stroke="{INK}" stroke-width="1" '
          'stroke-dasharray="2 3"/>')
    c.add(f'<ellipse cx="-1" cy="-6" rx="4" ry="6" fill="{P.WHITE}" fill-opacity=".8" stroke="{INK}" '
          f'stroke-width="1"/><ellipse cx="4" cy="-6" rx="4" ry="6" fill="{P.WHITE}" fill-opacity=".8" '
          f'stroke="{INK}" stroke-width="1"/>')
    clip = c.shape(ellipse_d(2, 0, 8, 5.4), P.SUN, sw=1.4, light=None, clip=True)
    c.add(f'<g clip-path="url(#{clip})"><path d="M0,-6 v12 M5,-6 v12" stroke="{INK}" stroke-width="2.2"/></g>')
    c.dot(8, -1, 1)
    return _at(c, x, y, k)

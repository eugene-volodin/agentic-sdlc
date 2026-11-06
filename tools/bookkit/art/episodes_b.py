"""Footer episodes, group B: context, memory, documentation and the instruction file.

Each story is retold after a plot of the printed original, with the agent in it: bookmarks for the next session, a
head that read everything in one day, a satchel too heavy to carry, recipes kept in a cupboard until needed, a
notebook that remembers, shelves of every size, a fairy tale read by the fire, a map of the kitchen, a mysterious
tome and the dusty chest in a ship's hold. Props that only these stories need are private functions below, drawn
like `things.py`: `_prop(x, y, k)`, the origin where the thing touches the ground, for a 137-unit professor at
k = 1.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten
from . import props, sets, things
from .footers import Strip, episode, sky_colors
from .characters import module
from .ink import INK, Canvas, ellipse_d, n, rounded_rect_d
from .openers import Box, strip_boxes
from .rig import hand as draw_hand
from .sets import _at, doodle_at

BOOK_COLORS = (P.RED, P.BLUE, P.GREEN, P.YELLOW, P.TEAL, P.VIOLET, P.ORANGE, P.PINK)


# ============================================================================ placing helpers
def _place(s: Strip, make, x: float, y: float, w: float, h: float, name: str, group: str | None = None,
           depth: float | None = None, backdrop: bool = False) -> tuple[float, float, float, float]:
    """Put `make(x, y, k)` standing at an absolute (x, y); `w` and `h` are its size at k = 1."""
    k = s.unit
    box = (x - w * k / 2, y - h * k, x + w * k / 2, y)
    s.put(depth if depth is not None else y - 1, make(x, y, k), box, name, group=group, backdrop=backdrop)
    return box


def _wall(s: Strip, make, spots: list[tuple[float, float]], w: float, h: float, name: str, air: float = 8) -> bool:
    """Hang something on the wall (or in the air) at the first free spot; `make(x, y)` draws it centred at (x, y),
    `w` and `h` being its full size in units. Returns whether it found room."""
    for x, y in spots:
        box = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        if box[1] < 2 or box[0] < 2 or box[2] > 838 or not s.free(box, air):
            continue
        s.put(3, make(x, y), box, name)
        return True
    return False


def _badge(s: Strip, box: Box, kind: str) -> None:
    """A comic badge over a character placed with `s.actor` (as `s.cast` does with `mark=`)."""
    k = min(1.3, max(0.6, s.tall / 160))
    x = (box.left + box.right) / 2
    y = box.top - 18 * k - 2
    if y < 18 * k + 2:
        x, y = box.right + 14 * k, box.top + 18 * k
    s.put(box.bottom + 1, props.mark(x, y, kind, k), (x - 17 * k, y - 17 * k, x + 17 * k, y + 17 * k),
          group=box.group)


def _star_d(cx: float, cy: float, r: float, turn: float = 0) -> str:
    pts = []
    for i in range(10):
        a = math.radians(turn - 90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{n(cx + math.cos(a) * rr)},{n(cy + math.sin(a) * rr)}")
    return "M" + " L".join(pts) + " Z"


def _style(size: float, k: float) -> str:
    """The lettering style for `size` drawn inside a prop scaled by `k`: balloon letters only when they are big
    on the page, flat ones otherwise (the rim would clog small letters)."""
    return "sign" if size * k >= P.SIGN_BALLOON_FROM else "plain"


def _nail(c: Canvas, x: float, y: float, r: float = 2.6) -> None:
    """A nail driven into the wall: a round grey head with a glint; things hang from it."""
    c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{P.METAL}" stroke="{INK}" stroke-width="1.2"/>'
          f'<circle cx="{n(x - r * 0.3)}" cy="{n(y - r * 0.3)}" r="{n(r * 0.3)}" fill="{P.WHITE}"/>')


def _plaque(x: float, y: float, text: str, size: float, room: float = 0, color: str = P.CREAM,
            nails: bool = True) -> tuple[str, tuple[float, float, float, float]]:
    """A board with a word on it, centred at (x, y), in page units (lettering never shrinks with the picture);
    `room` caps its width. Words that would not fit in one line at full size go on two. The lettering keeps an
    even margin from the board's edges; the nails have their own room beside it. Returns the drawing and its
    box."""
    c = Canvas()
    side = size * (2.3 if nails else 1.4)                    # the margins at both sides, with the nails
    lines = [text]
    words = text.split()
    if room and len(words) > 1 and sets.letter_width(text, size) + side > room:
        cut = min(range(1, len(words)), key=lambda i: abs(len(" ".join(words[:i])) - len(text) / 2))
        lines = [" ".join(words[:cut]), " ".join(words[cut:])]
    w = max(sets.letter_width(line, size) for line in lines) + side
    if room:
        w = min(w, room)
    lead = size * 1.2
    h = size * 1.75 + lead * (len(lines) - 1)
    c.shape(rounded_rect_d(x - w / 2, y - h / 2, w, h, min(4.0, size * 0.45)), color, sw=1.6, light=None)
    if nails and w > size * 3:
        for nx in (x - w / 2 + size * 0.42, x + w / 2 - size * 0.42):
            c.dot(nx, y, max(1.0, size * 0.1), P.METAL_DARK)
    for i, line in enumerate(lines):
        ly = y + (i - (len(lines) - 1) / 2) * lead
        sets.fit_label(c, x, ly + size * 0.36, line, size, w - size * (2.1 if nails else 1.2))
    return c.render(), (x - w / 2, y - h / 2, x + w / 2, y + h / 2)


# ============================================================================ books and paper
def _book_pile(x: float, y: float, k: float = 1.0, seed: int = 0, count: int = 4, w: float = 46) -> str:
    """Books lying in a pile, each a little askew; `w` is the widest one, 9 high each."""
    rnd = random.Random(seed)
    c = Canvas()
    top = 0.0
    for i in range(count):
        bw = w - rnd.uniform(0, 14)
        dx = rnd.uniform(-5, 5)
        color = BOOK_COLORS[(seed + i * 3) % len(BOOK_COLORS)]
        c.shape(rounded_rect_d(dx - bw / 2, top - 9, bw, 9, 2), color, sw=1.6, light=(-1, -1))
        c.path(f"M{n(dx + bw / 2 - 5)},{n(top - 7.5)} H{n(dx + bw / 2 - 1)} V{n(top - 1.5)} H{n(dx + bw / 2 - 5)} Z",
               P.CARD, 1)
        c.line(f"M{n(dx - bw / 2 + 5)},{n(top - 4.5)} h{n(bw * 0.4)}", 1, P.WHITE, 0.7)
        top -= 9
    return _at(c, x, y, k)


def _open_book(x: float, y: float, k: float = 1.0, color: str = P.RED, dogears: bool = False) -> str:
    """A book lying open on its back; `dogears` folds the corners of its pages. 52 wide, 14 high."""
    c = Canvas()
    c.shape("M-26,0 Q-13,-3 0,1 Q13,-3 26,0 V-3 Q13,-6 0,-2 Q-13,-6 -26,-3 Z", color, sw=1.6, light=None)
    c.shape("M0,-2 Q-10,-14 -24,-10 L-24,-3 Q-12,-6 0,-2 Z", P.CARD, sw=1.5, light=None)
    c.shape("M0,-2 Q10,-14 24,-10 L24,-3 Q12,-6 0,-2 Z", P.WHITE, sw=1.5, light=None)
    for i in range(3):
        c.line(f"M{-19 + i},{-10 + i * 2.2} q7,-2 14,1", 0.9, opacity=0.5)
        c.line(f"M{5 - i},{-8 + i * 2.2} q7,-3 14,-2", 0.9, opacity=0.5)
    if dogears:
        c.path("M-24,-10 L-18,-11.5 L-23,-5 Z", P.PAPER_FOLD, 1.2)
        c.path("M24,-10 L18,-11.5 L23,-5 Z", P.PAPER_FOLD, 1.2)
    return _at(c, x, y, k)


def _bookmark(c: Canvas, x: float, y: float, h: float, color: str, turn: float = 0, tassel: bool = True) -> None:
    """A paper bookmark with a tassel, its top at (x, y), `h` long."""
    body = (f'<g transform="translate({n(x)},{n(y)}) rotate({n(turn)})">'
            f'<path d="M-4,0 H4 V{n(h)} L0,{n(h - 4)} L-4,{n(h)} Z" fill="{color}" stroke="{INK}" stroke-width="1.2" '
            f'stroke-linejoin="round"/><path d="M-2,4 h4 M-2,8 h4" stroke="{P.WHITE}" stroke-width="1"/>')
    if tassel:
        body += (f'<path d="M0,0 q-2,-5 0,-8" fill="none" stroke="{P.RED}" stroke-width="1.2"/>'
                 f'<circle cx="0" cy="-9" r="1.8" fill="{P.RED}" stroke="{INK}" stroke-width=".8"/>')
    c.add(body + "</g>")


def _bookcase_marked(x: float, y: float, k: float = 1.0, seed: int = 0) -> str:
    """A small bookcase, two shelves, ribbons and paper slips sticking out of the books: notes for next time.
    90 wide, 104 tall."""
    rnd = random.Random(seed)
    c = Canvas()
    c.shape("M-45,0 V-104 H45 V0 Z", P.WOOD, sw=2.3, light=(-3, -3))
    marks = []
    for row in range(2):
        top = -98 + row * 50
        c.path(f"M-39,{top} H39 V{top + 42} H-39 Z", P.WOOD_DARK, 1.8)
        bx = -37.0
        while bx < 30:
            bw = rnd.choice((7, 9, 11))
            bh = rnd.choice((30, 34, 38))
            color = rnd.choice(BOOK_COLORS)
            c.path(f"M{n(bx)},{top + 42} V{top + 42 - bh} H{n(bx + bw)} V{top + 42} Z", color, 1.4)
            c.line(f"M{n(bx + 1.5)},{top + 47 - bh} H{n(bx + bw - 1.5)}", 1, opacity=0.6)
            if rnd.random() < 0.5:
                marks.append((bx + bw / 2, top + 42 - bh, rnd.choice((P.YELLOW, P.WHITE, P.PINK_PALE))))
            bx += bw + 0.6
    for mx, my, color in marks:   # paper slips poking out of the tops
        c.path(f"M{n(mx - 2)},{n(my + 2)} V{n(my - 6)} H{n(mx + 2)} V{n(my + 2)} Z", color, 1)
    c.line("M-30,-56 q2,10 -1,16 M14,-56 q-2,8 1,14 M-8,-6 q2,6 0,10", 1.6, P.RED)   # ribbons over the shelf lip
    return _at(c, x, y, k)


def _bookcase_empty(x: float, y: float, k: float = 1.0) -> str:
    """An emptied bookcase: every book taken out and read, one left lying on its side. 80 wide, 120 tall."""
    c = Canvas()
    c.shape("M-40,0 V-120 H40 V0 Z", P.WOOD, sw=2.3, light=(-3, -3))
    for row in range(3):
        top = -114 + row * 38
        c.path(f"M-34,{top} H34 V{top + 32} H-34 Z", P.WOOD_DARK, 1.8)
    c.shape(rounded_rect_d(-10, -52, 26, 6, 1.5), P.GREEN, sw=1.4, light=None)
    c.dots(None, -32, -84, 64, 3, 20, "even", seed=3, r=0.8, color=P.WHITE, opacity=0.9)
    return _at(c, x, y, k)


def _dogeared_book(x: float, y: float, k: float = 1.0) -> str:
    """A thick book lying open with nearly every page dog-eared: the folded corners stand up all along both
    edges. 60 wide, 22 high."""
    c = Canvas()
    c.shape("M-30,0 Q-15,-4 0,1 Q15,-4 30,0 V-4 Q15,-8 0,-3 Q-15,-8 -30,-4 Z", P.BLUE, sw=1.8, light=None)
    for i in range(3):   # the page block, thick
        c.shape(f"M0,{-3 - i * 2} Q-12,{-16 - i * 2} -28,{-12 - i * 2} L-28,{-5 - i * 2} Q-14,{-8 - i * 2} "
                f"0,{-3 - i * 2} Z", P.CARD if i < 2 else P.WHITE, sw=1.2, light=None)
        c.shape(f"M0,{-3 - i * 2} Q12,{-16 - i * 2} 28,{-12 - i * 2} L28,{-5 - i * 2} Q14,{-8 - i * 2} "
                f"0,{-3 - i * 2} Z", P.CARD if i < 2 else P.WHITE, sw=1.2, light=None)
    for i in range(4):
        c.line(f"M{-24 + i},{-15 + i * 2} q8,-2 16,1", 0.9, opacity=0.5)
        c.line(f"M{6 - i},{-13 + i * 2} q8,-3 16,-2", 0.9, opacity=0.5)
    for side in (-1, 1):   # the dog-ears, sticking up at every corner
        for i, dy in enumerate((-16, -12, -8)):
            cx = 28 * side
            c.path(f"M{cx},{dy} L{cx - 9 * side},{dy - 3 - i} L{cx - 2 * side},{dy + 6} Z", P.PAPER_FOLD, 1.1)
    return _at(c, x, y, k)


def _scissors(x: float, y: float, k: float = 1.0, turn: float = 0) -> str:
    """Open scissors, the origin at the pivot."""
    c = Canvas()
    c.line("M0,0 L14,-4 M0,0 L14,4", 2, P.METAL_DARK)
    c.path(ellipse_d(-6, -4, 4, 3), "none", 2.2, P.RED)
    c.path(ellipse_d(-6, 4, 4, 3), "none", 2.2, P.RED)
    c.dot(0, 0, 1.2)
    return _at(c, x, y, k, turn=turn)


def _glue(x: float, y: float, k: float = 1.0) -> str:
    """A pot of paste with a brush in it."""
    c = Canvas()
    c.line("M2,-12 L8,-26", 2.4, P.WOOD_DARK)
    c.shape("M-7,0 V-12 H7 V0 Z", P.WHITE, sw=1.4, light=(-1, -1))
    c.shape(rounded_rect_d(-8, -14, 16, 3, 1), P.BLUE, sw=1.2, light=None)
    c.line("M-4,-8 h8", 1.2, P.BLUE)
    return _at(c, x, y, k)


def _craft_table(x: float, y: float, k: float = 1.0) -> str:
    """The table spread with newspaper: paste, cut-out bookmarks drying in a fan, scraps. 120 wide, 66 tall."""
    c = Canvas()
    c.add(things.kitchen_table(0, 0, 1.0, 120, P.WOOD_LIGHT, None))
    c.shape("M-56,-48 H54 L58,-28 L46,-30 L50,-38 H-50 L-54,-24 L-60,-26 Z", P.PAPER, sw=1.4, light=None)
    for i in range(5):
        c.line(f"M{-44 + i * 20},-46 v-0 h14", 1, opacity=0.45)
    c.line("M-50,-34 h20 M-26,-34 h24", 1, opacity=0.35)
    c.add(_glue(-40, -48, 0.9))
    for i, color in enumerate((P.RED, P.GREEN, P.YELLOW, P.BLUE)):
        _bookmark(c, 12 + i * 9, -66 + abs(i - 1.5) * 2, 18, color, turn=(i - 1.5) * 12)
    c.path("M36,-50 q4,-3 8,0 q-4,3 -8,0 Z", P.PINK, 1)
    return _at(c, x, y, k)


def _press(x: float, y: float, k: float = 1.0) -> str:
    """Heavy books pressing drying bookmarks, their tassels hanging out, an old flat iron on top. 64 wide, 76 tall."""
    c = Canvas()
    colors = (P.WOOD_DARK, P.RED, P.TEAL, P.VIOLET)
    widths = (62, 56, 60, 52)
    top = 0.0
    for i, (color, w) in enumerate(zip(colors, widths, strict=True)):
        h = 12 if i != 2 else 14
        c.shape(rounded_rect_d(-w / 2 + (i % 2) * 2, top - h, w, h, 2), color, sw=1.8, light=(-1, -1))
        c.path(f"M{n(w / 2 - 6 + (i % 2) * 2)},{n(top - h + 2)} H{n(w / 2 - 1 + (i % 2) * 2)} V{n(top - 2)} "
               f"H{n(w / 2 - 6 + (i % 2) * 2)} Z", P.CARD, 1)
        if i < 3:   # a bookmark squeezed between this book and the next
            c.line(f"M{-14 + i * 10},{n(top - h)} q-3,8 2,14", 2.4, (P.YELLOW, P.PINK, P.GREEN)[i])
            c.add(f'<circle cx="{-12 + i * 10}" cy="{n(top - h + 15)}" r="2" fill="{P.RED}" stroke="{INK}" '
                  f'stroke-width=".8"/>')
        top -= h
    # The iron.
    c.line(f"M-12,{top - 13} Q-12,{top - 26} -2,{top - 26} H6 Q12,{top - 24} 10,{top - 13}", 3.6, P.WOOD_DARK)
    c.shape(f"M-22,{top} V{top - 9} Q-22,{top - 14} -16,{top - 14} H8 Q20,{top - 12} 28,{top} Z", P.CHARCOAL,
            sw=2, light=(-2, -2), highlight=f"M-16,{top - 10} H4")
    c.shape(rounded_rect_d(-24, top - 1, 54, 3, 1), P.METAL, sw=1.2, light=None)
    return _at(c, x, y, k)


def _clothesline(x0: float, x1: float, y: float, k: float, seed: int = 0) -> str:
    """A string across the wall with bookmarks pegged to it, drying."""
    c = Canvas()
    mid = (x0 + x1) / 2
    c.line(f"M{n(x0)},{n(y)} Q{n(mid)},{n(y + 10 * k)} {n(x1)},{n(y)}", 1.2)
    _nail(c, x0, y, 3 * max(0.7, k))
    _nail(c, x1, y, 3 * max(0.7, k))
    count = 5
    for i in range(count):
        t = (i + 0.5) / count
        px = x0 + (x1 - x0) * t
        py = y + 10 * k * 4 * t * (1 - t) * 0.5 + 1
        color = BOOK_COLORS[(i + seed) % len(BOOK_COLORS)]
        c.add(f'<g transform="translate({n(px)},{n(py)}) scale({n(k)})">'
              f'<path d="M-4,2 H4 V28 L0,24 L-4,28 Z" fill="{color}" stroke="{INK}" stroke-width="1.2"/>'
              f'<rect x="-1.6" y="-3" width="3.2" height="8" fill="{P.WOOD_LIGHT}" stroke="{INK}" '
              f'stroke-width=".8"/></g>')
    return c.render()


# ============================================================================ the reading marathon
def _vacuum(x: float, y: float, k: float = 1.0) -> str:
    """A canister vacuum cleaner on its wheels, its wand parked upright beside it with the brush on the floor and
    the hose looping from the canister to the wand's grip; a sticky note on it reads like a prompt. 76 wide,
    80 tall."""
    c = Canvas()
    # The wand, standing on its floor brush, and the grip at its top.
    c.shape(rounded_rect_d(18, -7, 22, 7, 2.5), P.CHARCOAL, sw=1.8, light=None)
    c.shape(rounded_rect_d(26.5, -70, 5, 64, 2.5), P.METAL, sw=1.6, light=(-1, 0))
    c.shape("M26,-70 Q26,-80 34,-80 H38 V-74 H34 Q32,-74 32,-70 Z", P.CHARCOAL, sw=1.5, light=None)
    # The hose: from the canister's nose up and over to the grip.
    hose = "M-4,-30 C-8,-62 18,-84 28,-74"
    c.line(hose, 6.4, INK)
    c.line(hose, 3.6, P.METAL_DARK)
    c.line("M-2,-40 l3,1 M-4,-50 l3,0 M0,-60 l3,-1 M8,-70 l2,-2", 1, P.CHARCOAL, 0.8)
    # The canister.
    c.shape("M-34,-4 Q-38,-34 -6,-36 Q16,-36 18,-14 Q18,-4 12,-4 Z", P.RED, sw=2.2, light=(-2, -2),
            highlight="M-26,-22 Q-22,-30 -12,-30")
    c.shape(ellipse_d(-6, -32, 6, 3), P.CHARCOAL, sw=1.4, light=None)
    for wx in (-24, 6):
        c.shape(ellipse_d(wx, -4, 5.5, 5.5), P.CHARCOAL, sw=1.5, light=None)
        c.dot(wx, -4, 1.5, P.METAL)
    c.add(sets.sticky(-16, -18, P.YELLOW_PALE, 6, 0.6))
    c.line("M-21,-19 l3,2 l-3,2 M-16,-15 h4", 1.1)
    return _at(c, x, y, k)


def _monitor_on_stool(x: float, y: float, k: float = 1.0) -> str:
    """An old monitor on a stool, a little vacuum cleaner drawn on its screen by mistake. 44 wide, 92 tall."""
    c = Canvas()
    c.add(things.stool(0, 0, 1.0, P.BLUE))
    c.add(doodle_at("monitor", 0, -42, 52))
    # Over the screen's lines of code, a little vacuum cleaner glows instead.
    c.path("M-12.6,-85 H12.6 Q14.2,-85 14.2,-83 V-67.5 Q14.2,-65.4 11.6,-65.4 H-11.6 Q-14.2,-65.4 -14.2,-67.5 V-83 "
           "Q-14.2,-85 -12.6,-85 Z", P.SCREEN_DARK, 0)
    c.add(f'<path d="M-10,-69 Q-11,-77 -3,-77.5 Q3,-77.5 3,-71 Q3,-69 1,-69 Z M4,-69 h7 M7.5,-69 V-82 h3 '
          f'M-4,-77 C-5,-84 4,-87 7.5,-82" fill="none" stroke="{P.GLOW}" stroke-width="1.5" stroke-linecap="round" '
          f'stroke-linejoin="round"/>')
    return _at(c, x, y, k)


def _star_ring(x: float, y: float, k: float = 1.0) -> str:
    """Stars circling a dazed head: a dashed orbit with four little stars on it; the origin is the ring's centre."""
    c = Canvas()
    c.add(f'<ellipse cx="0" cy="0" rx="20" ry="6" fill="none" stroke="{INK}" stroke-width="1" '
          f'stroke-dasharray="3 3" stroke-opacity=".6"/>')
    for i, a in enumerate((20, 110, 200, 290)):
        sx, sy = math.cos(math.radians(a)) * 20, math.sin(math.radians(a)) * 6
        c.path(_star_d(sx, sy, 5 if i % 2 else 4, i * 17), (P.SUN, P.YELLOW)[i % 2], 1.2)
    return _at(c, x, y, k)


def _teacup(x: float, y: float, k: float = 1.0, steam: bool = False) -> str:
    c = Canvas()
    if steam:
        c.line("M-2,-14 q-3,-5 0,-9 M3,-14 q3,-5 0,-9", 1.2, P.WHITE)
    c.shape(ellipse_d(0, -1, 11, 2.4), P.WHITE, sw=1.2, light=None)
    c.shape("M-7,-12 H7 Q7,-2 0,-2 Q-7,-2 -7,-12 Z", P.WHITE, sw=1.4, light=(-1, -1))
    c.add(f'<path d="M-6,-11 h12" stroke="{P.RED}" stroke-width="1.6"/>')
    c.line("M7,-10 q5,0 4,4 q-1,3 -5,2", 1.4)
    return _at(c, x, y, k)


# ============================================================================ the satchel walking to school
def _satchel(x: float, y: float, k: float = 1.0) -> str:
    """A huge stuffed school satchel: a ruler, a rolled sheet, a pencil and a book poke out of the flap, a sheet
    flies off behind. The origin is the middle of its bottom; 84 wide, 92 tall."""
    c = Canvas()
    # Things sticking out at the top.
    c.shape("M-24,-74 L-20,-92 L-14,-92 L-18,-74 Z", P.YELLOW, sw=1.4, light=None)          # ruler
    c.line("M-20,-88 h4 M-21,-84 h3 M-21,-80 h4", 1)
    c.shape("M-6,-74 V-88 Q0,-92 6,-88 V-74 Z", P.WHITE, sw=1.4, light=None)                # a rolled sheet
    c.shape(ellipse_d(0, -88, 6, 2), P.CARD, sw=1, light=None)
    c.add(things.giant_pencil(10, -76, 1, 26, -70, P.RED))
    c.shape(rounded_rect_d(16, -86, 14, 14, 2), P.GREEN, sw=1.4, light=None)                # a book
    # The satchel itself.
    c.shape("M-34,-4 Q-36,-68 -26,-74 H26 Q36,-68 34,-4 Q34,0 28,0 H-28 Q-34,0 -34,-4 Z",
            P.LEATHER, sw=2.4, light=(-3, -3), stipple=(18, -72, 16, 70, 20, "right"))
    c.shape("M-30,-72 H30 Q34,-50 28,-38 H-28 Q-34,-50 -30,-72 Z", darken(P.LEATHER, 0.9), sw=2, light=None)
    for bx in (-16, 16):
        c.shape(rounded_rect_d(bx - 4, -46, 8, 18, 2), P.WOOD_DARK, sw=1.4, light=None)
        c.shape(rounded_rect_d(bx - 5, -34, 10, 7, 1.5), P.SUN, sw=1.4, light=None)
    c.shape(rounded_rect_d(-12, -26, 24, 12, 2), P.CARD, sw=1.2, light=None)                 # the name label
    c.line("M-8,-20 h16", 1, opacity=0.5)
    # A sheet that flew out, with the lines of its flight.
    c.add(f'<g transform="translate(-46,-70) rotate(-25)"><path d="M-7,-9 H7 V9 H-7 Z" fill="{P.WHITE}" '
          f'stroke="{INK}" stroke-width="1.2"/><path d="M-4,-4 h8 M-4,0 h8 M-4,4 h5" stroke="{INK}" '
          f'stroke-width=".8" stroke-opacity=".5"/></g>')
    c.line("M-30,-80 q-4,-4 -2,-8 M-36,-76 q-5,-2 -6,-6", 1.2, opacity=0.6)
    return _at(c, x, y, k)


def _apple(x: float, y: float, k: float = 1.0) -> str:
    """A red apple lying in the grass: a dimple at the top, a stem, a leaf and a glint. 16 wide, 16 tall."""
    c = Canvas()
    c.shape("M0,-11 Q-4,-14 -7,-12 Q-11,-9 -9,-4 Q-7,0 -3,0 Q0,-1 0,-1 Q0,-1 3,0 Q7,0 9,-4 Q11,-9 7,-12 "
            "Q4,-14 0,-11 Z", P.RED, sw=1.5, light=(-1.4, -1.2), shade_k=0.8, highlight="M-6,-8 Q-6,-10 -4,-11")
    c.line("M0,-11 Q0,-14 1.6,-16", 1.3, P.WOOD_DARK)
    c.shape("M1.4,-14.4 Q5,-17.6 8,-15 Q5,-12.6 1.4,-14.4 Z", P.LEAF_LIGHT, sw=1, light=None)
    return _at(c, x, y, k)


def _card(x: float, y: float, k: float = 1.0, turn: float = -8) -> str:
    """A small index card with a few lines on it; the origin is its bottom middle."""
    c = Canvas()
    c.shape("M-9,0 V-12 H9 V0 Z", P.CARD, sw=1.3, light=None)
    c.line("M-6,-9 h12 M-6,-6 h9 M-6,-3 h11", 0.9, opacity=0.6)
    c.add(f'<circle cx="-6" cy="-9.5" r="1" fill="{P.RED}"/>')
    return _at(c, x, y, k, turn=turn)


def _school(x: float, y: float, k: float = 1.0) -> str:
    """A school far away: a pediment, rows of windows, a flag and a bell. 140 wide, 112 tall."""
    c = Canvas()
    c.shape("M-70,0 V-60 H70 V0 Z", P.CREAM, sw=2.2, light=(-2, -2))
    c.shape("M-76,-60 L0,-92 L76,-60 Z", P.RED, sw=2.2, light=None)
    c.shape(ellipse_d(0, -72, 7, 7), P.SUN, sw=1.6, light=None)
    c.line("M0,-92 V-112", 1.8)
    c.shape("M0,-112 L16,-107 L0,-102 Z", P.RED, sw=1.2, light=None)
    for row in range(2):
        for i in range(6):
            if row == 1 and i in (2, 3):
                continue
            wx = -58 + i * 21
            c.path(f"M{wx},{-52 + row * 24} h12 v14 h-12 Z", P.SKY, 1.4)
    c.shape("M-12,0 V-24 H12 V0 Z", P.WOOD_DARK, sw=1.6, light=None)
    c.shape("M-18,0 H18 V4 H-18 Z", P.STONE, sw=1.4, light=None)
    return _at(c, x, y, k)


def _ladybug_mushroom(x: float, y: float, k: float = 1.0) -> str:
    """Two mushrooms, a ladybug on the bigger cap. 44 wide, 40 tall."""
    c = Canvas()
    c.add(props.mushroom(-8, 0, 1.0))
    c.add(props.mushroom(14, 0, 0.6, P.AMBER, spots=False))
    c.shape(ellipse_d(-6, -37, 5, 4), P.RED, sw=1.2, light=None)
    c.line("M-6,-41 V-33", 0.8)
    c.dot(-8, -37, 0.9)
    c.dot(-4, -36, 0.9)
    c.shape(ellipse_d(-1, -38, 2, 2), P.INK, sw=0, light=None)
    return _at(c, x, y, k)


# ============================================================================ the kitchen
def _cupboard(x: float, y: float, k: float = 1.0, seed: int = 0) -> str:
    """A tall kitchen cupboard with both doors open: three shelves of recipe notebooks with coloured spines, one
    gap where a notebook has just been taken out. 112 wide with its doors, 132 tall."""
    rnd = random.Random(seed)
    c = Canvas()
    c.shape("M-44,0 V-128 H44 V0 Z", P.WOOD_LIGHT, sw=2.4, light=(-3, -3))
    c.shape(rounded_rect_d(-48, -134, 96, 8, 2), P.WOOD, sw=2, light=None)
    for row in range(3):
        top = -120 + row * 38
        c.path(f"M-38,{top} H38 V{top + 32} H-38 Z", darken(P.WOOD_LIGHT, 0.72), 1.8)
        bx, i = -36.0, 0
        while bx < 30:
            bw = rnd.choice((7, 8, 9))
            if row == 1 and i == 3:     # the gap
                c.path(f"M{n(bx)},{top + 32} V{top + 6} H{n(bx + bw)} V{top + 32} Z", darken(P.WOOD_LIGHT, 0.5), 0)
                bx += bw + 0.6
                i += 1
                continue
            bh = rnd.choice((24, 26, 28))
            color = BOOK_COLORS[(i + row * 3 + seed) % len(BOOK_COLORS)]
            c.path(f"M{n(bx)},{top + 32} V{top + 32 - bh} H{n(bx + bw)} V{top + 32} Z", color, 1.3)
            c.path(f"M{n(bx + 1.5)},{top + 36 - bh} H{n(bx + bw - 1.5)} V{top + 40 - bh} H{n(bx + 1.5)} Z", P.CARD,
                   0.6)
            bx += bw + 0.6
            i += 1
    for side in (-1, 1):   # the open doors
        c.shape(f"M{44 * side},-128 L{56 * side},-122 V-6 L{44 * side},0 Z", P.WOOD, sw=2, light=None)
        c.add(f'<circle cx="{52 * side}" cy="-64" r="2.2" fill="{P.SUN}" stroke="{INK}" stroke-width="1"/>')
    return _at(c, x, y, k)


def _notebook(x: float, y: float, k: float = 1.0, color: str = P.RED, turn: float = 0) -> str:
    """A recipe notebook with a spiral and a label, held up; the origin is its bottom middle."""
    c = Canvas()
    c.shape(rounded_rect_d(-8, -22, 16, 22, 2), color, sw=1.4, light=(-1, -1))
    c.path(rounded_rect_d(-5, -17, 10, 6, 1), P.CARD, 0.8)
    for yy in range(-20, 0, 4):
        c.path(ellipse_d(-8, yy, 2, 1), "none", 0.9)
    return _at(c, x, y, k, turn=turn)


def _door(x: float, y: float, k: float = 1.0) -> str:
    """A front door with a little window where two guests' hats show, the doorknob on its left and a brass ring
    knocker in its middle, just striking its stud: short impact lines flash round the stud. 62 wide, 124 tall;
    the stud is at (0, -50)."""
    c = Canvas()
    c.shape("M-27,0 V-120 H27 V0 Z", P.WOOD_DARK, sw=2.4, light=(-3, -3))
    c.shape("M-31,-124 H31 V-118 H-31 Z", P.WOOD, sw=2, light=None)
    c.path("M-19,-8 V-36 H19 V-8 Z", "none", 1.6)
    c.shape("M-16,-104 H16 V-74 H-16 Z", P.SKY_LOW, sw=2, light=None)
    c.shape("M-12,-82 Q-12,-92 -6,-92 Q0,-92 0,-82 Z", P.CHARCOAL, sw=0, light=None)      # a bowler hat
    c.shape("M-14,-82 H2 V-80 H-14 Z", P.CHARCOAL, sw=0, light=None)
    c.shape("M2,-80 L8,-94 L14,-80 Z", P.RED, sw=0, light=None)                         # a pointed one with a pompom
    c.add(f'<circle cx="8" cy="-95" r="2.2" fill="{P.WHITE}"/>')
    c.line("M0,-104 V-74 M-16,-89 H16", 1.6)
    c.shape(ellipse_d(-20, -52, 3.2, 3.2), P.SUN, sw=1.3, light=(-0.8, -0.8))          # the doorknob
    # The knocker: a brass plate, the ring hanging from it, the stud it strikes.
    c.shape(rounded_rect_d(-4.5, -70, 9, 7, 2.5), P.SUN, sw=1.3, light=None)
    c.add(f'<circle cx="0" cy="-58" r="6.2" fill="none" stroke="{INK}" stroke-width="4.4"/>'
          f'<circle cx="0" cy="-58" r="6.2" fill="none" stroke="{P.SUN}" stroke-width="2.2"/>')
    c.shape(ellipse_d(0, -50, 2.4, 2), P.AMBER, sw=1.1, light=None)
    # The impact: a little flash where the ring strikes the stud and three short strokes fanning out to the right,
    # towards the sound.
    c.shape(_star_d(3, -50, 5.5, 20), lighten(P.SUN, 0.5), sw=1.1, light=None)
    for a in (-38, -4, 30):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        stroke = f"M{n(4 + ca * 6)},{n(-50 + sa * 6)} L{n(4 + ca * 12)},{n(-50 + sa * 12)}"
        c.line(stroke, 3.4)
        c.line(stroke, 1.6, lighten(P.SUN, 0.4))
    return _at(c, x, y, k)


def _knock_burst(cx: float, cy: float, text: str, size: float, to: tuple[float, float]) -> tuple[str, tuple]:
    """A comic sound effect: the word in balloon letters, staggered on two lines, in a smooth starburst whose one
    long spike points at `to` (where the sound comes from). Page units; returns the drawing and its box."""
    head, _, tail = text.partition("-")
    lines = [head + "-", tail] if tail else [text]
    lead = size * 1.02
    w = max(sets.letter_width(line, size) for line in lines) + size * 0.5 * (len(lines) - 1)
    rx, ry = w / 2 + size * 0.55, (lead * len(lines)) / 2 + size * 0.5
    tx, ty = to
    aim = math.atan2(ty - cy, tx - cx)
    spikes = 14
    tip = min(range(spikes), key=lambda i: abs(math.remainder(math.tau * i / spikes + 0.12 - aim, math.tau)))
    c = Canvas()
    pts, vals = [], []
    for i in range(spikes):
        a = math.tau * i / spikes + 0.12
        if i == tip:
            a = aim
            reach = math.hypot(tx - cx, ty - cy)
            pts.append((cx + math.cos(a) * reach, cy + math.sin(a) * reach))
        else:
            pts.append((cx + math.cos(a) * rx * 1.12, cy + math.sin(a) * ry * 1.16))
        b = math.tau * (i + 0.5) / spikes + 0.12
        vals.append((cx + math.cos(b) * rx * 0.78, cy + math.sin(b) * ry * 0.74))
    d = f"M{n(pts[0][0])},{n(pts[0][1])} " + " ".join(
        f"Q{n(vals[i][0])},{n(vals[i][1])} {n(pts[(i + 1) % spikes][0])},{n(pts[(i + 1) % spikes][1])}"
        for i in range(spikes)) + " Z"
    c.shape(d, lighten(P.SUN, 0.35), sw=1.8, light=None)
    top = cy - lead * (len(lines) - 1) / 2
    for i, line in enumerate(lines):
        lx = cx + (i - (len(lines) - 1) / 2) * size * 0.5
        sets.fit_label(c, lx, top + i * lead + size * 0.36, line, size, rx * 1.5, P.RED, turn=-6)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return c.render(), (min(xs) - 1, min(ys) - 1, max(xs) + 1, max(ys) + 1)


def _stove(x: float, y: float, k: float = 1.0) -> str:
    """A kitchen stove, a pie browning behind its oven glass, a kettle steaming on top. 72 wide, 104 tall."""
    c = Canvas()
    c.line("M14,-80 q-4,-6 0,-12 M20,-82 q4,-6 0,-12", 1.6, P.WHITE)
    c.shape("M4,-66 Q4,-80 17,-80 Q30,-80 30,-66 Z", P.BLUE, sw=1.8, light=(-1, -1))
    c.line("M30,-72 l8,-6", 2.4)
    c.line("M9,-80 Q17,-90 25,-80", 1.6)
    c.shape("M-36,0 V-64 H36 V0 Z", P.WHITE, sw=2.4, light=(-3, -3), shade_k=0.88)
    c.shape(rounded_rect_d(-38, -68, 76, 6, 2), P.CHARCOAL, sw=1.8, light=None)
    for i in range(4):
        c.add(f'<circle cx="{-24 + i * 16}" cy="-56" r="3" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="1"/>')
    c.shape(rounded_rect_d(-28, -46, 56, 34, 4), P.CHARCOAL, sw=2, light=None)
    c.add(f'<rect x="-24" y="-42" width="48" height="26" rx="3" fill="{P.ORANGE}" opacity=".55"/>')
    c.shape("M-16,-20 Q-16,-30 0,-30 Q16,-30 16,-20 Z", P.AMBER, sw=1.6, light=None)       # the pie
    c.line("M-8,-26 l3,3 M0,-28 l3,3 M8,-26 l3,3", 1)
    c.line("M-24,-50 H24", 2.4, P.METAL)
    c.line("M40,-30 q4,-6 0,-12 M44,-34 q5,-6 0,-12", 1.2, P.WOOD_DARK, 0.6)     # the smell of it
    return _at(c, x, y, k)


def _basket_apples(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    for ax, ay in ((-8, -14), (2, -16), (10, -13)):
        c.add(f'<circle cx="{ax}" cy="{ay}" r="5" fill="{P.RED}" stroke="{INK}" stroke-width="1.3"/>')
    c.shape("M-16,-12 H16 L12,0 H-12 Z", P.AMBER, sw=1.6, light=(-1, -1))
    c.line("M-14,-8 H14 M-13,-4 H13", 0.9, opacity=0.5)
    c.line("M-14,-12 Q0,-30 14,-12", 1.8, P.WOOD_DARK)
    return _at(c, x, y, k)


def _tea_table(x: float, y: float, k: float = 1.0) -> str:
    """The tea table: checked cloth, a plate of pirozhki, a jar of jam with a spoon, a teapot and cups.
    130 wide, 80 tall."""
    c = Canvas()
    c.add(things.kitchen_table(0, 0, 1.0, 130, P.WOOD_LIGHT, P.RED))
    top = -48
    c.shape(ellipse_d(-34, top - 2, 18, 3.5), P.WHITE, sw=1.4, light=None)            # the plate of pirozhki
    for px, py in ((-44, -3), (-34, -4), (-24, -3), (-39, -9), (-29, -9)):
        c.shape(f"M{px - 6},{top + py} Q{px},{top + py - 9} {px + 6},{top + py} Q{px},{top + py + 2} {px - 6},"
                f"{top + py} Z", P.AMBER, sw=1.3, light=(-1, -1))
    c.shape(f"M-10,{top} V{top - 14} H4 V{top} Z", lighten(P.WATER_LIGHT, 0.4), sw=1.4, light=None)   # jam jar
    c.add(f'<rect x="-9" y="{top - 11}" width="12" height="10" fill="{P.RED}" opacity=".85"/>')
    c.shape(rounded_rect_d(-11, top - 17, 16, 4, 1), P.WHITE, sw=1.2, light=None)
    c.line(f"M0,{top - 12} L8,{top - 22}", 1.6, P.METAL_DARK)
    c.add(_teacup(16, top, 0.9, steam=True))
    c.shape(f"M30,{top} Q24,{top - 20} 38,{top - 22} Q52,{top - 20} 46,{top} Z", P.BLUE, sw=1.6, light=(-1, -1))
    c.line(f"M46,{top - 14} Q56,{top - 18} 56,{top - 26}", 2.2)
    c.line(f"M30,{top - 14} q-6,0 -6,6", 2)
    c.shape(ellipse_d(38, top - 23, 6, 2), P.BLUE, sw=1.2, light=None)
    c.dot(38, top - 26, 1.8, P.WHITE)
    return _at(c, x, y, k)


def _dresser(x: float, y: float, k: float = 1.0) -> str:
    """A low kitchen dresser with two doors; 80 wide, 58 tall: someone can sit on top."""
    c = Canvas()
    c.shape("M-38,0 V-52 H38 V0 Z", P.WOOD, sw=2.3, light=(-3, -3))
    c.shape(rounded_rect_d(-42, -58, 84, 7, 2), P.WOOD_LIGHT, sw=2, light=None)
    for dx in (-19, 19):
        c.path(f"M{dx - 15},-46 H{dx + 15} V-8 H{dx - 15} Z", "none", 1.6)
        c.add(f'<circle cx="{dx - 10 if dx > 0 else dx + 10}" cy="-27" r="2.2" fill="{P.SUN}" stroke="{INK}" '
              f'stroke-width="1"/>')
    c.line("M-34,0 v4 M34,0 v4", 3.6, P.WOOD_DARK)
    return _at(c, x, y, k)


def _arched_window(x: float, y: float, k: float = 1.0, sky: str = P.SKY) -> str:
    """A small arched kitchen window with a sill and a flowering cactus on it; the origin is the middle of the
    sill. 80 wide, 100 tall."""
    c = Canvas()
    c.shape("M-34,-6 V-62 Q-34,-96 0,-96 Q34,-96 34,-62 V-6 Z", P.WHITE, sw=2.2, light=None)
    c.path("M-28,-8 V-60 Q-28,-90 0,-90 Q28,-90 28,-60 V-8 Z", sky, 1.8)
    c.line("M0,-90 V-8 M-28,-50 H28", 2.6, P.WHITE)
    c.line("M0,-90 V-8 M-28,-50 H28", 0.8)
    c.shape(rounded_rect_d(-40, -6, 80, 7, 2), P.WOOD, sw=1.8, light=None)
    c.add(things.cactus(-16, -6, 0.9))
    c.add(_teacup(16, -6, 0.8))
    return _at(c, x, y, k)


def _napkin(x: float, y: float, k: float = 1.0) -> str:
    """A big checked napkin tucked in under a chin; the origin is the knot at the collar."""
    c = Canvas()
    d = "M-13,0 L13,0 L2,28 L-2,28 Z"
    clip = c.shape(d, P.WHITE, sw=1.5, light=None, clip=True)
    checks = "".join(f'<rect x="{-14 + i * 6}" y="0" width="3" height="30" fill="{P.RED}" opacity=".55"/>'
                     for i in range(5))
    checks += "".join(f'<rect x="-14" y="{2 + i * 6}" width="28" height="3" fill="{P.RED}" opacity=".45"/>'
                      for i in range(5))
    c.add(f'<g clip-path="url(#{clip})">{checks}</g>')
    c.path(d, "none", 1.5)
    c.shape("M-6,-3 L0,2 L6,-3 L0,-1 Z", P.WHITE, sw=1.2, light=None)
    return _at(c, x, y, k)


# ============================================================================ the shelves of every size
def _bay(x: float, y: float, k: float, w: float, h: float, fill: int, seed: int = 0) -> str:
    """A shelving bay `w` by `h` (units at k = 1); `fill` says what it holds: 0 a single page, 1 a few books,
    2 crammed full."""
    rnd = random.Random(seed)
    c = Canvas()
    c.shape(f"M{-w / 2},0 V{-h} H{w / 2} V0 Z", P.WOOD, sw=2.2, light=(-3, -3))
    rows = max(1, int(h // 36))
    step = (h - 6) / rows
    for row in range(rows):
        top = -h + 4 + row * step
        inner = step - 6
        c.path(f"M{-w / 2 + 5},{n(top)} H{w / 2 - 5} V{n(top + inner)} H{-w / 2 + 5} Z", P.WOOD_DARK, 1.6)
        floor = top + inner
        if fill == 0:
            if row == rows - 1:
                # The single page, leaning on the back of the shelf: lines of text and a folded corner.
                c.shape(f"M-9,{n(floor)} L-7,{n(floor - 21)} H5 L9,{n(floor - 17)} L7,{n(floor)} Z", P.CARD, sw=1.3,
                        light=None)
                c.path(f"M5,{n(floor - 21)} L5.6,{n(floor - 16.6)} L9,{n(floor - 17)} Z", P.PAPER_FOLD, 1)
                for j in range(4):
                    c.line(f"M{n(-5 + j * 0.15)},{n(floor - 16 + j * 3.6)} h{9 if j % 2 else 11}", 0.9,
                           opacity=0.55)
        else:
            bx = -w / 2 + 7
            limit = (w / 2 - 12) if fill == 2 else (-w / 2 + 7 + (w - 14) * 0.45)
            while bx < limit:
                bw = rnd.choice((5, 6, 7, 8))
                bh = min(inner - 3, rnd.choice((18, 22, 26, 30)))
                color = rnd.choice(BOOK_COLORS)
                c.path(f"M{n(bx)},{n(floor)} V{n(floor - bh)} H{n(bx + bw)} V{n(floor)} Z", color, 1.1)
                bx += bw + 0.4
    return _at(c, x, y, k)


def _book_cart(x: float, y: float, k: float = 1.0) -> str:
    """A library cart on wheels with books leaning on it. 56 wide, 52 tall."""
    c = Canvas()
    c.line("M-26,-48 V-8 M26,-48 V-8", 3, P.METAL_DARK)
    for yy in (-46, -24):
        c.shape(rounded_rect_d(-28, yy, 56, 4, 1.5), P.WOOD_LIGHT, sw=1.4, light=None)
    for row, yy in enumerate((-46, -24)):
        for i in range(5 - row):
            bx = -24 + i * 9
            c.path(f"M{bx},{yy} V{yy - 16 + (i % 2) * 3} H{bx + 7} V{yy} Z", BOOK_COLORS[(i + row * 2) % 8], 1.1)
    for wx in (-20, 20):
        c.shape(ellipse_d(wx, -4, 4, 4), P.CHARCOAL, sw=1.2, light=None)
    return _at(c, x, y, k)


# ============================================================================ by the fire
def _armchair(x: float, y: float, k: float = 1.0) -> str:
    """A wing armchair seen from the front: turned wooden legs, a skirted base, a tall buttoned back with a wing
    at each side, rolled arms with scrolled fronts and a loose seat cushion, gold piping along the edges.
    92 wide, 112 tall."""
    c = Canvas()
    body, side, pipe = P.RED, darken(P.RED, 0.86), lighten(P.SUN, 0.1)
    for lx in (-30, 30):                                                     # turned legs
        c.shape(f"M{lx - 4},-12 Q{lx - 5},-7 {lx - 2.4},-4 L{lx - 1.6},0 H{lx + 1.6} L{lx + 2.4},-4 "
                f"Q{lx + 5},-7 {lx + 4},-12 Z", P.WOOD_DARK, sw=1.6, light=(-1, -1))
    # The back, with its buttons and the soft creases between them.
    c.shape("M-30,-44 V-94 Q-30,-112 0,-112 Q30,-112 30,-94 V-44 Z", body, sw=2.3, light=(-3, -3),
            stipple=(12, -108, 16, 60, 14, "right"))
    for bx, by in ((-14, -96), (0, -100), (14, -96), (-14, -76), (0, -80), (14, -76), (-7, -88), (7, -88),
                   (-7, -68), (7, -68)):
        c.add(f'<circle cx="{bx}" cy="{by}" r="1.7" fill="{darken(P.RED, 0.62)}" stroke="{INK}" '
              f'stroke-width=".8"/>')
    c.line("M-14,-96 L-7,-88 L0,-80 L7,-88 L14,-96 M-14,-76 L-7,-88 M14,-76 L7,-88 M-7,-68 L0,-80 L7,-68 "
           "M0,-100 L-7,-88 M0,-100 L7,-88", 0.8, darken(P.RED, 0.62), opacity=0.7)
    # The wings, curving out from the top of the back down to the arms.
    for sx in (-1, 1):
        c.shape(f"M{30 * sx},-102 Q{48 * sx},-100 {46 * sx},-80 Q{44 * sx},-66 {40 * sx},-58 L{28 * sx},-58 "
                f"L{28 * sx},-98 Z", side, sw=2.2, light=None)
        c.line(f"M{32 * sx},-99 Q{45 * sx},-97 {43 * sx},-80 Q{41 * sx},-68 {38 * sx},-61", 1.2, pipe)
    # The skirted base.
    c.shape(rounded_rect_d(-40, -36, 80, 26, 5), body, sw=2.3, light=(-3, -2))
    c.line("M-38,-14 H38", 1.4, pipe)
    c.line("M-38,-14 H38", 0.6, opacity=0.6)
    # The seat cushion, piped.
    c.shape(rounded_rect_d(-28, -48, 56, 14, 6), lighten(P.RED, 0.12), sw=2.2, light=(-2, -2))
    c.line("M-24,-42 Q0,-45 24,-42", 1.2, pipe)
    # The rolled arms with their scrolled fronts.
    for sx in (-1, 1):
        c.shape(f"M{44 * sx},-14 V-56 Q{44 * sx},-68 {35 * sx},-68 Q{26 * sx},-68 {26 * sx},-56 V-14 Z",
                body, sw=2.3, light=(-2, -2))
        c.shape(ellipse_d(35 * sx, -58, 7, 7), side, sw=1.8, light=None)
        c.line(f"M{35 * sx},-61 a3,3 0 1 {1 if sx > 0 else 0} {3 * sx},3", 1.2, pipe)
    return _at(c, x, y, k)


def _reader_book(c: Canvas) -> None:
    """An open book held up to read, seen from behind - its covers towards us, the page block showing above them,
    a gold castle on the cover; in the professor's canvas, its lower edge resting in his hands in the `read`
    pose."""
    c.shape("M82,218 Q102,206 125,218 Q148,206 168,218 L168,228 L82,228 Z", P.CARD, sw=1.8, light=None)
    c.line("M90,216 Q104,209 123,218 M127,218 Q146,209 160,216", 0.9, opacity=0.4)
    c.shape("M125,222 L80,215 L83,276 L125,283 Z", P.GREEN, sw=2.2, light=(-2, -1))
    c.shape("M125,222 L170,215 L167,276 L125,283 Z", darken(P.GREEN, 0.9), sw=2.2, light=None)
    c.shape(rounded_rect_d(121, 219, 8, 66, 3), darken(P.GREEN, 0.75), sw=1.8, light=None)
    c.path("M138,262 V244 L142,239 L146,244 V249 H151 V242 L155,236 L159,242 V262 Z", P.SUN, 1.1)
    c.line("M88,226 L118,230 M132,230 L162,226", 1.3, P.SUN)


def _palms(name: str, pose: str, width: float, scale: float) -> list[tuple[float, float]]:
    """The middles of a character's two palms (left, right) in its own canvas units, as `rig.arm` draws them."""
    mod = module(name)
    out = []
    for (ex, ey), (wx, wy), _, turn in mod.POSES[pose][-2:]:
        a = math.atan2(wy - ey, wx - ex)
        hx, hy = wx + math.cos(a) * width * 0.42, wy + math.sin(a) * width * 0.42
        b = a + math.radians(turn)
        out.append((hx + math.cos(b) * 10 * scale, hy + math.sin(b) * 10 * scale))
    return out


def _needle(c: Canvas, palm: tuple[float, float], angle: float) -> None:
    """A knitting needle held in the fist at `palm`: its red knob a little behind the fist, its point well out in
    front along `angle` (degrees)."""
    ux, uy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    (px, py) = palm
    c.tube(f"M{n(px - ux * 9)},{n(py - uy * 9)} L{n(px + ux * 46)},{n(py + uy * 46)}", P.METAL, 3.4, shaded=False)
    c.path(f"M{n(px + ux * 46)},{n(py + uy * 46)} l{n(ux * 5 - uy * 1.4)},{n(uy * 5 + ux * 1.4)} "
           f"l{n(-ux * 5 - uy * 1.4)},{n(-uy * 5 + ux * 1.4)} Z", P.METAL_LIGHT, 1.2)   # the point
    c.add(f'<circle cx="{n(px - ux * 10)}" cy="{n(py - uy * 10)}" r="3.4" fill="{P.RED}" stroke="{INK}" '
          f'stroke-width="1.3"/>')


KNIT_ANGLES = (-40, -140)       # the left needle points up and right, the right one up and left: they cross


def _stitches(palm: tuple[float, float]) -> tuple[tuple[float, float], tuple[float, float]]:
    """Where the knitting's first and last stitch sit on the left needle, in the knitter's canvas."""
    ux, uy = math.cos(math.radians(KNIT_ANGLES[0])), math.sin(math.radians(KNIT_ANGLES[0]))
    return (palm[0] + ux * 8, palm[1] + uy * 8), (palm[0] + ux * 34, palm[1] + uy * 34)


def _knit_top() -> tuple[float, float]:
    """Where the knitting's last stitch sits on its needle, in the caterpillar's canvas: the yarn comes here."""
    return _stitches(_palms("caterpillar", "knit", 8, 0.84)[0])[0]


def _knitting_work(c: Canvas) -> None:
    """Knitting in the caterpillar's canvas, in the `knit` pose: a needle in each fist, crossed in an X over her
    chest; the striped piece hangs from the left needle, its stitches strung along it - the side her ball of yarn
    is on."""
    left, right = _palms("caterpillar", "knit", 8, 0.84)
    _needle(c, right, KNIT_ANGLES[1])                         # behind the knitting
    (ax, ay), (bx, by) = _stitches(left)
    drop = 44
    d = (f"M{n(ax)},{n(ay)} L{n(bx)},{n(by)} L{n(bx + 3)},{n(by + drop)} Q{n(bx - 4)},{n(by + drop + 6)} "
         f"{n((ax + bx) / 2)},{n(ay + drop - 4)} Q{n(ax - 2)},{n(ay + drop + 4)} {n(ax - 4)},{n(ay + drop)} Z")
    clip = c.shape(d, P.WHITE, sw=2, light=None, clip=True)
    top = min(ay, by)
    rows = "".join(f'<rect x="{n(ax - 10)}" y="{n(top + i * 8)}" width="{n(bx - ax + 20)}" height="4.4" '
                   f'fill="{(P.RED, P.BLUE)[i % 2]}"/>' for i in range(12))
    c.add(f'<g clip-path="url(#{clip})">{rows}</g>')
    c.path(d, "none", 2)
    _needle(c, left, KNIT_ANGLES[0])                          # the stitches sit on this one
    for i in range(1, 6):                                     # the loops over it
        t = i / 6
        sx, sy = ax + (bx - ax) * t, ay + (by - ay) * t
        c.add(f'<ellipse cx="{n(sx)}" cy="{n(sy + 1)}" rx="2.2" ry="3" fill="none" stroke="{P.RED}" '
              f'stroke-width="1.6"/>')


def _over_body(box, name: str, pose: str, draw, width: float, scale: float) -> str:
    """Draw `draw(c)` in a character's own canvas units over the character placed in `box` (in `pose`), then that
    character's two hands again on top, so that whatever it holds is gripped by them; `width` and `scale` are the
    arm width and hand scale its module draws with."""
    mod = module(name)
    c = Canvas()
    draw(c)
    _hands(c, name, pose, width, scale)
    k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
    cx = (box.left + box.right) / 2
    return (f'<g transform="translate({n(cx)},{n(box.bottom)}) scale({n(-k if box.flip else k)},{n(k)}) '
            f'translate({n(-mod.CENTER_X)},{n(-mod.FEET_Y)})">{c.render()}</g>')


def _hands(c: Canvas, name: str, pose: str, width: float, scale: float) -> None:
    """A character's two hands drawn again exactly as `rig.arm` draws them, in its canvas units."""
    mod = module(name)
    frames = mod.hands(pose)
    for side, (_, _, kind, _) in zip(("left", "right"), mod.POSES[pose][-2:], strict=True):
        f = frames[side]
        draw_hand(c, f.x, f.y, f.rotation, mod.HAND, kind, f.scale, mirror=f.mirror)


def _fireplace(x: float, y: float, k: float = 1.0) -> str:
    """A stone fireplace with logs burning, a candelabra and a little mantel clock on the mantel. 116 wide, 120
    tall."""
    c = Canvas()
    c.shape("M-50,0 V-86 H50 V0 Z", P.STONE, sw=2.4, light=(-3, -3), stipple=(-50, -86, 100, 86, 50, "even"))
    for row in range(5):
        yy = -16 - row * 16
        off = 10 if row % 2 else 0
        c.line(f"M-50,{yy} H50", 1, opacity=0.35)
        for i in range(5):
            c.line(f"M{-40 + i * 22 + off},{yy} v16", 1, opacity=0.3)
    c.shape("M-32,0 V-48 Q-32,-62 0,-62 Q32,-62 32,-48 V0 Z", P.DARK_BROWN, sw=2.2, light=None)
    c.add(f'<ellipse cx="0" cy="-20" rx="30" ry="24" fill="{P.ORANGE}" opacity=".35"/>')
    c.shape("M-16,-10 Q-20,-30 -8,-44 Q-6,-30 0,-28 Q2,-46 12,-50 Q10,-34 18,-24 Q20,-14 14,-10 Z", P.ORANGE,
            sw=1.8, light=None)
    c.shape("M-8,-10 Q-10,-22 -2,-30 Q2,-22 6,-20 Q10,-14 6,-10 Z", P.SUN, sw=1.2, light=None)
    c.shape(rounded_rect_d(-24, -12, 48, 7, 3), P.TRUNK, sw=1.6, light=None)
    c.shape(rounded_rect_d(-18, -7, 38, 7, 3), P.WOOD_DARK, sw=1.6, light=None)
    c.shape(rounded_rect_d(-58, -94, 116, 9, 2), P.WOOD, sw=2.2, light=None)
    # The candelabra.
    c.line("M-28,-94 V-104 M-38,-104 Q-28,-112 -18,-104 M-28,-104 V-110", 2.2, P.SUN)
    for cx in (-38, -28, -18):
        top = -114 if cx == -28 else -108
        c.shape(f"M{cx - 2},{top + 4} V{top - 6} H{cx + 2} V{top + 4} Z", P.WHITE, sw=1, light=None)
        c.shape(f"M{cx},{top - 7} Q{cx - 3},{top - 11} {cx},{top - 15} Q{cx + 3},{top - 11} {cx},{top - 7} Z",
                P.SUN, sw=0.8, light=None)
    # A small mantel clock.
    c.shape("M14,-94 V-106 Q22,-116 30,-106 V-94 Z", P.WOOD_DARK, sw=1.6, light=None)
    c.add(f'<circle cx="22" cy="-104" r="4.5" fill="{P.CARD}" stroke="{INK}" stroke-width="1"/>')
    c.line("M22,-104 v-3 M22,-104 h2.4", 0.9)
    return _at(c, x, y, k)


def _log_basket(x: float, y: float, k: float = 1.0) -> str:
    """A wicker basket of firewood. 48 wide, 32 tall."""
    c = Canvas()
    for lx, ly in ((-12, -26), (0, -29), (12, -26), (-6, -32), (6, -32)):
        c.shape(rounded_rect_d(lx - 5, ly - 4, 10, 8, 3.5), P.TRUNK, sw=1.3, light=None)
        c.add(f'<ellipse cx="{lx + 3}" cy="{ly}" rx="2" ry="3" fill="{P.WOOD_PALE}" stroke="{INK}" '
              f'stroke-width=".8"/>')
    c.shape("M-22,-24 H22 L18,0 H-18 Z", P.AMBER, sw=1.8, light=(-2, -1))
    c.line("M-21,-18 H21 M-20,-12 H20 M-19,-6 H19", 1, P.WOOD_DARK, 0.6)
    return _at(c, x, y, k)


def _floor_cushion(x: float, y: float, w: float) -> str:
    """A big plump floor cushion lying flat, `w` wide (page units), its foot at (x, y): piped round its middle,
    buttoned on top. Its height is a quarter of its width."""
    c = Canvas()
    h = w * 0.26
    d = (f"M{n(x - w / 2)},{n(y - h * 0.2)} Q{n(x - w / 2 - w * 0.03)},{n(y - h * 0.6)} {n(x - w * 0.44)},{n(y - h)} "
         f"Q{n(x)},{n(y - h * 1.18)} {n(x + w * 0.44)},{n(y - h)} Q{n(x + w / 2 + w * 0.03)},{n(y - h * 0.6)} "
         f"{n(x + w / 2)},{n(y - h * 0.2)} Q{n(x)},{n(y + h * 0.16)} {n(x - w / 2)},{n(y - h * 0.2)} Z")
    c.shape(d, P.VIOLET, sw=2, light=(-2, -2))
    c.line(f"M{n(x - w * 0.47)},{n(y - h * 0.45)} Q{n(x)},{n(y - h * 0.62)} {n(x + w * 0.47)},{n(y - h * 0.45)}",
           1.4, lighten(P.VIOLET, 0.4))                                    # the piping
    return c.render()


def _yarn_ball(x: float, y: float, r: float, color: str) -> str:
    """A ball of yarn on the floor: wound strands crossing over it, a loose end lying beside it; page units, its
    foot at (x, y)."""
    c = Canvas()
    cy = y - r
    c.line(f"M{n(x - r * 0.6)},{n(y - 0.5)} q{n(-r * 0.6)},{n(r * 0.1)} {n(-r * 1.3)},{n(-r * 0.15)}", 2.6)
    c.line(f"M{n(x - r * 0.6)},{n(y - 0.5)} q{n(-r * 0.6)},{n(r * 0.1)} {n(-r * 1.3)},{n(-r * 0.15)}", 1.4, color)
    clip = c.shape(ellipse_d(x, cy, r, r), color, sw=1.8, light=(-r * 0.15, -r * 0.15), clip=True)
    dark = darken(color, 0.72)
    strands = "".join(
        f'<path d="M{n(x - r * 1.1)},{n(cy + o * r)} Q{n(x)},{n(cy + o * r - r * 0.55)} {n(x + r * 1.1)},'
        f'{n(cy + o * r + r * 0.15)}" fill="none" stroke="{dark}" stroke-width="{n(max(0.6, r * 0.09))}"/>'
        for o in (-0.6, -0.2, 0.2, 0.6))
    strands += "".join(
        f'<path d="M{n(x + o * r)},{n(cy - r * 1.1)} Q{n(x + o * r + r * 0.5)},{n(cy)} {n(x + o * r - r * 0.1)},'
        f'{n(cy + r * 1.1)}" fill="none" stroke="{lighten(color, 0.3)}" stroke-width="{n(max(0.6, r * 0.09))}"/>'
        for o in (-0.5, 0.0, 0.5))
    c.add(f'<g clip-path="url(#{clip})">{strands}</g>')
    c.path(ellipse_d(x, cy, r, r), "none", 1.8)
    return c.render()


def _plaid(x: float, y: float, w: float, h: float) -> str:
    """A checked blanket over someone's lap, `w` wide and `h` high, its top at y (absolute units): soft, bulging
    over the knees, its hem lying in waves on the seat, two folds."""
    c = Canvas()
    d = (f"M{n(x - w * 0.4)},{n(y + h * 0.04)} Q{n(x)},{n(y - h * 0.1)} {n(x + w * 0.4)},{n(y + h * 0.04)} "
         f"Q{n(x + w * 0.56)},{n(y + h * 0.45)} {n(x + w * 0.5)},{n(y + h)} "
         f"Q{n(x + w * 0.33)},{n(y + h * 1.08)} {n(x + w * 0.17)},{n(y + h * 0.98)} "
         f"Q{n(x)},{n(y + h * 1.1)} {n(x - w * 0.17)},{n(y + h * 0.98)} "
         f"Q{n(x - w * 0.33)},{n(y + h * 1.08)} {n(x - w * 0.5)},{n(y + h)} "
         f"Q{n(x - w * 0.56)},{n(y + h * 0.45)} {n(x - w * 0.4)},{n(y + h * 0.04)} Z")
    clip = c.shape(d, P.TEAL, sw=1.8, light=None, clip=True)
    step = max(4.0, w / 6)
    lines = "".join(f'<path d="M{n(x - w * 0.6 + i * step)},{n(y - 10)} V{n(y + h + 6)}" stroke="{P.YELLOW}" '
                    f'stroke-width="{n(step * 0.28)}" opacity=".7"/>' for i in range(9))
    lines += "".join(f'<path d="M{n(x - w * 0.6)},{n(y + i * step)} H{n(x + w * 0.6)}" stroke="{P.RED}" '
                     f'stroke-width="{n(step * 0.28)}" opacity=".6"/>' for i in range(8))
    c.add(f'<g clip-path="url(#{clip})">{lines}</g>')
    c.path(d, "none", 1.8)
    c.line(f"M{n(x - w * 0.1)},{n(y + h * 0.3)} q{n(-w * 0.03)},{n(h * 0.3)} {n(-w * 0.07)},{n(h * 0.62)} "
           f"M{n(x + w * 0.16)},{n(y + h * 0.36)} q{n(w * 0.02)},{n(h * 0.28)} {n(w * 0.01)},{n(h * 0.56)}",
           1.2, INK, 0.5)                                                     # two soft folds
    return c.render()


# ============================================================================ the kitchen map
def _drawers(x: float, y: float, k: float = 1.0, front: bool = False) -> str:
    """A chest of four drawers, three of them pulled out with spoons, a sock and string spilling over; `front`
    draws only the face of the open top drawer (to be put in front of whoever sits in it). 74 wide, 100 tall."""
    c = Canvas()
    if front:
        c.shape("M-34,-74 H34 V-60 H-34 Z", P.YELLOW, sw=2, light=None)
        c.add(f'<circle cx="0" cy="-67" r="2.6" fill="{P.WOOD_DARK}" stroke="{INK}" stroke-width="1"/>')
        return _at(c, x, y, k)
    c.shape("M-34,0 V-96 H34 V0 Z", P.WOOD, sw=2.4, light=(-3, -3))
    c.shape(rounded_rect_d(-37, -100, 74, 6, 2), P.WOOD_LIGHT, sw=2, light=None)
    for i, yy in enumerate((-92, -70, -48, -26)):
        c.path(f"M-30,{yy} H30 V{yy + 20} H-30 Z", darken(P.WOOD, 0.85), 1.6)
        if i == 0:      # the top drawer is out: its inside shows, its face is drawn separately
            c.shape("M-34,-84 H34 V-74 H-34 Z", P.DARK_BROWN, sw=1.6, light=None)
        elif i == 2:   # pulled out, spoons in it
            c.shape(f"M-34,{yy + 4} H34 V{yy + 10} H-34 Z", P.DARK_BROWN, sw=1.4, light=None)
            c.line(f"M-14,{yy + 6} l-6,-10 M-6,{yy + 6} l2,-12 M6,{yy + 6} l8,-9", 1.8, P.METAL_DARK)
            c.add(f'<ellipse cx="-21" cy="{yy - 5}" rx="3" ry="2" fill="{P.METAL}" stroke="{INK}" '
                  f'stroke-width=".9"/>')
            c.shape(f"M-34,{yy + 10} H34 V{yy + 22} H-34 Z", P.YELLOW, sw=1.8, light=None)
        elif i == 3:   # a sock hanging out
            c.shape(f"M-34,{yy + 6} H34 V{yy + 18} H-34 Z", P.YELLOW, sw=1.8, light=None)
            c.shape(f"M14,{yy + 6} V{yy + 26} Q14,{yy + 30} 20,{yy + 30} H22 Q26,{yy + 30} 26,{yy + 26} V{yy + 6} Z",
                    P.RED, sw=1.3, light=None)
            c.line(f"M14,{yy + 12} h12 M14,{yy + 18} h12", 1.4, P.WHITE)
            c.line(f"M-20,{yy + 6} q-6,8 -2,14 q4,6 -6,10", 1.2, P.WOOD_DARK)
        else:
            c.add(f'<circle cx="0" cy="{yy + 10}" r="2.4" fill="{P.WOOD_DARK}" stroke="{INK}" stroke-width="1"/>')
    return _at(c, x, y, k)


def _counter(x: float, y: float, k: float = 1.0, w: float = 200) -> str:
    """A kitchen counter: cupboard doors below, a pot and a kettle at its right end. `w` wide, 62 tall."""
    c = Canvas()
    hw = w / 2
    c.shape(f"M{-hw},0 V-56 H{hw} V0 Z", P.CREAM, sw=2.4, light=(-3, -3), shade_k=0.9)
    c.shape(rounded_rect_d(-hw - 4, -62, w + 8, 7, 2), P.WOOD, sw=2, light=None)
    doors = int(w // 40)
    for i in range(doors):
        dx = -hw + 4 + i * (w - 8) / doors
        dw = (w - 8) / doors - 4
        c.path(f"M{n(dx)},-50 H{n(dx + dw)} V-6 H{n(dx)} Z", "none", 1.5)
        c.add(f'<circle cx="{n(dx + dw / 2)}" cy="-44" r="2" fill="{P.METAL_DARK}"/>')
    c.add(things.pot(hw - 22, -62, 0.6, steam=True, color=P.TEAL))
    return _at(c, x, y, k)


def _map(x: float, y: float, k: float = 1.0, start: float = 50) -> str:
    """A big colourful map hanging down from a counter's edge: lakes, hills, a forest, a red dotted way to a cross,
    a compass rose; the creases of its folds. The origin is the middle of its top edge; 112 wide, 70 tall."""
    c = Canvas()
    d = "M-56,0 H56 L54,70 L36,66 L18,70 L0,66 L-18,70 L-36,66 L-54,70 Z"
    clip = c.shape(d, P.YELLOW_PALE, sw=2, light=None, clip=True)
    inner = (f'<path d="M-60,30 Q-40,18 -24,28 Q-10,40 -24,56 Q-40,72 -60,60 Z" fill="{P.LEAF_LIGHT}" '
             f'stroke="{INK}" stroke-width="1.2"/>'
             f'<path d="M10,8 Q30,-2 46,10 Q60,22 46,34 Q28,40 18,30 Q4,20 10,8 Z" fill="{P.LEAF_LIGHT}" '
             f'stroke="{INK}" stroke-width="1.2"/>'
             f'<path d="M-30,6 Q-16,0 -8,8 Q-10,18 -26,16 Q-36,12 -30,6 Z" fill="{P.WATER_LIGHT}" stroke="{INK}" '
             f'stroke-width="1.2"/>'
             f'<path d="M14,52 Q30,44 44,54 Q40,64 22,62 Z" fill="{P.WATER_LIGHT}" stroke="{INK}" stroke-width="1.2"/>')
    c.add(f'<g clip-path="url(#{clip})">{inner}</g>')
    for tx, ty in ((-50, 44), (-44, 50), (-38, 44)):
        c.path(f"M{tx},{ty} l4,-8 l4,8 Z", P.FIR, 1)
    for mx in (22, 32):
        c.path(f"M{mx - 6},24 L{mx},12 L{mx + 6},24 Z", P.STONE, 1.1)
        c.path(f"M{mx - 2},16 L{mx},12 L{mx + 2},16 Z", P.WHITE, 0.6)
    c.add(f'<path d="M-52,{n(start)} Q-30,40 -10,46 Q8,52 4,34 Q0,18 30,30 Q40,36 40,44" fill="none" stroke="{P.RED}" '
          f'stroke-width="2.2" stroke-dasharray="3 3" stroke-linecap="round"/>')
    c.line("M37,41 l6,6 M43,41 l-6,6", 2.4, P.RED)
    c.path(_star_d(-44, 12, 7), P.WHITE, 1)
    c.add(f'<path d="M-44,4 L-42,12 L-44,10 Z" fill="{P.RED}"/>')
    c.line("M-18,0 V68 M18,0 V68 M-56,34 H56", 0.9, P.PAPER_FOLD)
    return _at(c, x, y, k)


def _fridge(x: float, y: float, k: float = 1.0) -> str:
    """A rounded old fridge with magnets and a pinned note. 54 wide, 116 tall."""
    c = Canvas()
    c.shape("M-27,0 V-104 Q-27,-116 -15,-116 H15 Q27,-116 27,-104 V0 Z", P.WHITE, sw=2.4, light=(-3, -3),
            shade_k=0.88, highlight="M-20,-104 V-74")
    c.line("M-27,-74 H27", 2)
    c.line("M20,-100 V-84 M20,-64 V-40", 3.2, P.METAL_DARK)
    c.path("M-14,-66 h16 v18 h-16 Z", P.YELLOW_PALE, 1.1)
    c.line("M-11,-61 h10 M-11,-57 h8 M-11,-53 h10", 0.8, opacity=0.6)
    c.add(f'<circle cx="-6" cy="-67" r="2.6" fill="{P.RED}" stroke="{INK}" stroke-width=".9"/>')
    c.path(_star_d(-12, -94, 5), P.SUN, 1)
    c.add(f'<circle cx="4" cy="-96" r="3.4" fill="{P.GREEN}" stroke="{INK}" stroke-width="1"/>')
    c.line("M-22,0 v4 M22,0 v4", 3, P.CHARCOAL)
    return _at(c, x, y, k)


def _compass(x: float, y: float, k: float = 1.0) -> str:
    """A brass pocket compass lying on the floor with its lid thrown open and leaning back on its hinge: a
    cream face with ticks round it, an N at the north and a red-and-white needle. 30 wide, 31 tall."""
    c = Canvas()
    brass, brass_dark = P.SUN, darken(P.SUN, 0.72)
    # The lid, open: its inside faces us, a brass rim round a polished dish with an engraved star.
    c.shape(ellipse_d(0, -21.6, 13.4, 8.8), brass, sw=1.8, light=(-1.4, -1.2), shade_k=0.8)
    c.shape(ellipse_d(0, -21.8, 10, 6.2), lighten(P.SUN, 0.45), sw=1, light=None,
            highlight="M-5,-25 Q-2,-26.6 1,-26.6")
    c.path(_star_d(0, -21.8, 3), "none", 0.8, brass_dark)
    c.shape(rounded_rect_d(-4, -16, 8, 3.6, 1.4), brass_dark, sw=1.1, light=None)         # the hinge
    # The case: its rim seen from a little above, the side below it, the face inside.
    c.shape(ellipse_d(0, -6.4, 15, 7.6), brass_dark, sw=1.8, light=None)
    c.shape(ellipse_d(0, -8.6, 15, 7.6), brass, sw=1.8, light=(-1.2, -1), shade_k=0.82)
    c.shape(ellipse_d(0, -8.6, 11.6, 5.6), P.CARD, sw=1.1, light=None)
    # The rose: ticks at the quarters and between them, an N at the north.
    c.line("M0,-13.4 V-12 M0,-3.8 V-5.2 M-11,-8.6 H-9.2 M11,-8.6 H9.2", 0.9, P.CHARCOAL)
    c.line("M-7.4,-12 l1,0.8 M7.4,-12 l-1,0.8 M-7.4,-5.2 l1,-0.8 M7.4,-5.2 l-1,-0.8", 0.6, P.CHARCOAL)
    c.line("M-1.4,-10.6 V-13.4 L1.4,-10.6 V-13.4", 0.8)
    # The needle: north red, south white, on a brass pin.
    c.path("M8.4,-12.2 L1.4,-7.6 L-1.4,-9.6 Z", P.RED, 0.9)
    c.path("M-8.4,-5 L-1.4,-9.6 L1.4,-7.6 Z", P.WHITE, 0.9)
    c.add(f'<circle cx="0" cy="-8.6" r="1.2" fill="{brass_dark}" stroke="{INK}" stroke-width=".6"/>')
    return _at(c, x, y, k)


def _ladle_rail(x0: float, x1: float, y: float, k: float) -> str:
    """A rail on the wall with a ladle, a whisk and a spatula hanging from it."""
    c = Canvas()
    for bx in (x0 + 3, x1 - 3):      # the brackets that hold it to the wall
        c.shape(rounded_rect_d(bx - 3 * k, y - 6 * k, 6 * k, 12 * k, 1.5 * k), P.METAL, sw=1.2, light=None)
        c.dot(bx, y - 3 * k, 0.9 * k)
    c.add(f'<path d="M{n(x0)},{n(y)} H{n(x1)}" stroke="{INK}" stroke-width="{n(4.6 * max(0.7, k))}" '
          f'stroke-linecap="round"/><path d="M{n(x0)},{n(y)} H{n(x1)}" stroke="{P.METAL_DARK}" '
          f'stroke-width="{n(2.4 * max(0.7, k))}" stroke-linecap="round"/>')
    span = x1 - x0
    for i, kind in enumerate(("ladle", "whisk", "spatula")):
        hx = x0 + span * (i + 1) / 4
        c.add(f'<g transform="translate({n(hx)},{n(y)}) scale({n(k)})">')
        c.line("M0,0 V24", 2, P.WOOD_DARK if kind == "spatula" else P.METAL_DARK)
        if kind == "ladle":
            c.shape("M-6,24 Q-6,32 0,32 Q6,32 6,24 Z", P.METAL, sw=1.3, light=None)
        elif kind == "whisk":
            c.path("M0,20 Q-6,30 0,36 Q6,30 0,20 Z M0,20 Q-2,30 0,36 Q2,30 0,20 Z", "none", 1.1, P.METAL_DARK)
        else:
            c.shape(rounded_rect_d(-4, 22, 8, 12, 2), P.WOOD_LIGHT, sw=1.2, light=None)
        c.add("</g>")
    return c.render()


# ============================================================================ the captain's cabin
def _captain_desk(x: float, y: float, k: float = 1.0) -> str:
    """A captain's writing desk: a candelabra, an inkwell with a quill, stacks of gold coins. 92 wide, 96 tall."""
    c = Canvas()
    c.line("M-38,0 V-42 M38,0 V-42", 5, P.WOOD_DARK)
    c.line("M-38,-14 Q0,-6 38,-14", 2.4, P.WOOD_DARK)
    c.shape(rounded_rect_d(-46, -50, 92, 9, 2), P.WOOD, sw=2.2, light=None)
    c.path("M-36,-41 H36 V-30 H-36 Z", darken(P.WOOD, 0.85), 1.6)
    # Candelabra.
    c.shape("M-34,-50 L-30,-54 H-22 L-18,-50 Z", P.SUN, sw=1.2, light=None)
    c.line("M-26,-54 V-70 M-36,-70 Q-26,-80 -16,-70", 2.2, P.SUN)
    for cx, top in ((-36, -72), (-26, -78), (-16, -72)):
        c.shape(f"M{cx - 2},{top} V{top - 10} H{cx + 2} V{top} Z", P.WHITE, sw=1, light=None)
        c.shape(f"M{cx},{top - 11} Q{cx - 3},{top - 15} {cx},{top - 19} Q{cx + 3},{top - 15} {cx},{top - 11} Z",
                P.SUN, sw=0.8, light=None)
    c.add(f'<circle cx="-26" cy="-80" r="16" fill="{P.SUN}" opacity=".18"/>')
    # Inkwell and quill.
    c.shape("M-6,-50 V-58 Q0,-62 6,-58 V-50 Z", P.CHARCOAL, sw=1.4, light=None)
    c.line("M2,-60 Q8,-80 18,-92", 1.2)
    c.shape("M4,-66 Q8,-90 20,-94 Q16,-80 6,-62 Z", P.WHITE, sw=1.2, light=None)
    # Coins.
    for i, (cx, h) in enumerate(((24, 4), (34, 6), (29, 3))):
        base = -50 if i < 2 else -50 - 4 * 3
        if i == 2:
            continue
        for j in range(h):
            c.shape(ellipse_d(cx, base - j * 3, 5, 1.8), P.SUN, sw=0.9, light=None)
    c.shape(ellipse_d(29, -63, 5, 1.8), P.SUN, sw=0.9, light=None)
    return _at(c, x, y, k)


def _tome(x: float, y: float, k: float = 1.0, title: str = "", size: float = 12) -> str:
    """A huge old book lying shut on the floor, seen a little from above and from the left in an oblique view
    (every receding edge runs the same way, up and to the left): the page block with its leaves faces us between
    the boards, the leather spine with raised bands is the left side, the front cover lies on top with a tooled gold
    border, brass corners at its fore-edge and a brass title plate, and a red ribbon hangs out of the pages down to
    the floor. The origin is the middle of the front foot; 162 wide, 62 tall."""
    c = Canvas()
    hw, th, bd = 75.0, 24.0, 4.2            # half the length, the thickness, a board's thickness
    dx, dy = -11.0, -36.0                    # the receding direction (the cover's depth)
    shear = dx / dy

    def at(u: float, v: float) -> tuple[float, float]:
        """A point on the cover: u from the spine (0) to the fore-edge (1), v from the front (0) to the back."""
        return -hw + 2 * hw * u + dx * v, -th + dy * v

    def poly(*uv: tuple[float, float]) -> str:
        return "M" + " L".join(f"{n(px)},{n(py)}" for px, py in (at(u, v) for u, v in uv)) + " Z"
    c.add(f'<ellipse cx="2" cy="-1" rx="{n(hw + 10)}" ry="4.5" fill="{INK}" opacity=".14"/>')
    # The spine, the left side: leather in shadow, raised bands across it with a gold line beside each.
    lx = -hw
    c.shape(f"M{lx},0 V{-th} L{lx + dx},{-th + dy} V{dy} Z", darken(P.LEATHER, 0.8), sw=2.2, light=None)
    for t in (0.18, 0.42, 0.66, 0.88):
        bx, by = lx + dx * t, dy * t
        c.add(f'<path d="M{n(bx)},{n(by - 1)} V{n(by - th + 1)}" stroke="{INK}" stroke-width="5" '
              f'stroke-linecap="round"/><path d="M{n(bx)},{n(by - 1.6)} V{n(by - th + 1.6)}" '
              f'stroke="{darken(P.LEATHER, 0.95)}" stroke-width="2.6" stroke-linecap="round"/>')
        c.line(f"M{n(bx + dx * 0.07)},{n(by + dy * 0.07 - 3)} V{n(by + dy * 0.07 - th + 3)}", 0.9, P.SUN)
    # The front: the boards' edges, the page block between them, its leaves; the spine's leather rounds it on
    # the left.
    c.shape(f"M{lx},0 H{hw} V{-th} H{lx} Z", P.LEATHER, sw=2.2, light=None)
    c.shape(f"M{lx + 7},{-bd} H{hw - 2} V{-th + bd} H{lx + 7} Z", P.CARD, sw=1.4, light=(0, -1.6), shade_k=0.9)
    for i in range(1, 5):
        yy = -bd - (th - 2 * bd) * i / 5
        c.line(f"M{lx + 10},{n(yy)} H{hw - 5}", 0.8, P.PAPER_FOLD)
    c.add(f'<path d="M{lx + 7},{-bd} Q{lx + 2},{-th / 2} {lx + 7},{-th + bd}" fill="none" stroke="{INK}" '
          f'stroke-width="1.2"/>')
    # The front cover, on top.
    c.shape(poly((0, 0), (1, 0), (1, 1), (0, 1)), P.LEATHER, sw=2.2, light=(2, 2.5), shade_k=0.86)
    c.path(poly((0.08, 0.13), (0.95, 0.13), (0.95, 0.87), (0.08, 0.87)), "none", 1.4, P.SUN)
    c.path(poly((0.11, 0.25), (0.92, 0.25), (0.92, 0.75), (0.11, 0.75)), "none", 0.9, P.SUN)
    # Brass corners at the fore-edge, each with a rivet; the front one folds over the board's edge.
    for v0, dv in ((0.0, 1), (1.0, -1)):
        c.shape(poly((1, v0), (1, v0 + dv * 0.4), (0.9, v0)), P.SUN, sw=1.3, light=(-1, 1), shade_k=0.82)
        px, py = at(0.97, v0 + dv * 0.12)
        c.add(f'<circle cx="{n(px)}" cy="{n(py)}" r="1.3" fill="{darken(P.SUN, 0.7)}"/>')
    c.shape(f"M{hw},{-th} V{-th + bd + 1} H{hw - 9} Z", P.SUN, sw=1.2, light=None)
    # The title plate, brass-framed, lying flat on the cover: its lettering is level and runs with the cover.
    if title:
        cx, cy = at(0.53, 0.5)
        w = min(2 * hw * 0.74, sets.letter_width(title, size) + size * 1.4)
        h = min(size * 1.5, -dy * 0.5)
        c.add(f'<g transform="matrix(1,0,{n(shear)},1,{n(cx)},{n(cy)})">')
        c.shape(rounded_rect_d(-w / 2 - 3, -h / 2 - 3, w + 6, h + 6, 3), P.SUN, sw=1.6, light=(-1, 1),
                shade_k=0.82)
        c.shape(rounded_rect_d(-w / 2, -h / 2, w, h, 2), P.CREAM, sw=1.1, light=None)
        sets.fit_label(c, 0, size * 0.36, title, size, w - size * 1.2, P.INK, style=_style(size, k))
        c.add("</g>")
    # The ribbon: out of the pages, down the front and along the floor, its end cut in a swallowtail.
    sx, sy = hw * 0.42, -th + bd + 1
    rib = f"M{n(sx)},{n(sy)} Q{n(sx - 1)},-8 {n(sx + 3)},-1 Q{n(sx + 6)},3 {n(sx + 16)},3"
    c.add(f'<path d="{rib}" fill="none" stroke="{INK}" stroke-width="6.2" stroke-linejoin="round"/>'
          f'<path d="{rib}" fill="none" stroke="{P.RED}" stroke-width="3.6" stroke-linejoin="round"/>')
    ex = sx + 16
    c.path(f"M{n(ex - 1)},0 L{n(ex + 7)},-0.4 L{n(ex + 4)},3 L{n(ex + 7)},6.4 L{n(ex - 1)},6 Z", P.RED, 1.3)
    return _at(c, x, y, k)


def _coin(x: float, y: float, k: float = 1.0) -> str:
    """A big gold coin standing on its edge, rolling: a rim, a stamped star, the edge showing at the right and two
    lines of its roll behind it. 22 wide, 16 tall."""
    c = Canvas()
    c.shape(ellipse_d(1.4, -7.4, 6.4, 7.4), darken(P.SUN, 0.72), sw=1.4, light=None)
    c.shape(ellipse_d(0, -7.4, 6.4, 7.4), P.SUN, sw=1.4, light=(-1, -1), shade_k=0.84)
    c.add(f'<ellipse cx="0" cy="-7.4" rx="4.4" ry="5.2" fill="none" stroke="{darken(P.SUN, 0.7)}" '
          f'stroke-width=".9"/>')
    c.path(_star_d(0, -7.4, 2.6), darken(P.SUN, 0.88), 0.6)
    c.line("M-9,-10 h-5 M-9,-5 h-7", 1.1, opacity=0.5)
    return _at(c, x, y, k)


def _coin_stack(x: float, y: float, k: float = 1.0) -> str:
    """A little stack of gold coins on the floor and one fallen beside it. 30 wide, 18 tall."""
    c = Canvas()
    c.shape(ellipse_d(9, -2.4, 6, 2.4), darken(P.SUN, 0.75), sw=1.1, light=None)
    c.shape(ellipse_d(9, -3.4, 6, 2.4), P.SUN, sw=1.1, light=None)
    for i in range(4):
        cy = -2.4 - i * 3.2
        c.shape(f"M-10,{n(cy)} V{n(cy - 3.2)} A6,2.4 0 0 0 2,{n(cy - 3.2)} V{n(cy)} A6,2.4 0 0 1 -10,{n(cy)} Z",
                darken(P.SUN, 0.8), sw=1.1, light=None)
    c.shape(ellipse_d(-4, -15.2, 6, 2.4), P.SUN, sw=1.1, light=None)
    c.path(_star_d(-4, -15.2, 1.6), darken(P.SUN, 0.85), 0.5)
    return _at(c, x, y, k)


def _sea_chest(x: float, y: float, k: float = 1.0) -> str:
    """A small sea chest of gold, coins spilling from under its lid. 54 wide, 36 tall."""
    c = Canvas()
    c.shape("M-26,0 V-26 H26 V0 Z", P.WOOD, sw=2, light=(-2, -2))
    c.shape("M-27,-26 Q-27,-38 0,-38 Q27,-38 27,-26 Z", P.WOOD_DARK, sw=2, light=None)
    c.line("M-16,0 V-37 M16,0 V-37", 2.2, P.METAL_DARK)
    c.shape(rounded_rect_d(-5, -30, 10, 10, 2), P.SUN, sw=1.2, light=None)
    for cx in (-20, -10, 4, 14):
        c.shape(ellipse_d(cx, -26, 4, 1.6), P.SUN, sw=0.8, light=None)
    return _at(c, x, y, k)


def _parrot_perch(x: float, y: float, k: float = 1.0) -> str:
    """A green parrot on a T-shaped perch. 40 wide, 100 tall."""
    c = Canvas()
    c.line("M0,0 V-70", 3.4, P.WOOD_DARK)
    c.line("M-12,0 H12", 4, P.WOOD_DARK)
    c.line("M-18,-70 H18", 3.4, P.WOOD_DARK)
    c.shape("M-6,-70 L-14,-48 L-8,-50 L-10,-44 L-2,-56 Z", P.BLUE, sw=1.4, light=None)
    c.shape("M-8,-72 Q-12,-88 -2,-96 Q10,-100 10,-88 Q10,-78 2,-72 Z", P.GREEN, sw=1.8, light=(-1, -1))
    c.shape("M-6,-80 Q-12,-76 -8,-68 Q0,-72 0,-78 Z", lighten(P.GREEN, 0.25), sw=1.2, light=None)
    c.shape("M8,-92 Q16,-90 14,-82 Q12,-84 8,-84 Z", P.SUN, sw=1.3, light=None)
    c.shape(ellipse_d(4, -91, 3, 3), P.WHITE, sw=1, light=None)
    c.dot(4.8, -91, 1.2)
    c.shape("M-2,-96 Q2,-104 6,-98 Q4,-96 -2,-96 Z", P.RED, sw=1, light=None)
    c.line("M-4,-70 l-1,4 M2,-70 l1,4", 1.4, P.ORANGE_DARK)
    return _at(c, x, y, k)


def _ship_wheel(x: float, y: float, r: float) -> str:
    """A ship's wheel on the wall; the origin is its hub."""
    c = Canvas()
    for i in range(8):
        a = math.radians(i * 45)
        c.line(f"M0,0 L{n(math.cos(a) * r * 1.3)},{n(math.sin(a) * r * 1.3)}", r * 0.12, P.WOOD_DARK)
    c.path(ellipse_d(0, 0, r, r), "none", r * 0.2, P.WOOD)
    c.path(ellipse_d(0, 0, r * 1.08, r * 1.08), "none", 1.2)
    c.path(ellipse_d(0, 0, r * 0.9, r * 0.9), "none", 1.2)
    c.shape(ellipse_d(0, 0, r * 0.22, r * 0.22), P.SUN, sw=1.4, light=None)
    return f'<g transform="translate({n(x)},{n(y)})">{c.render()}</g>'


def _hanging_lantern(x: float, y: float, k: float = 1.0) -> str:
    """A ship's lantern hanging from an iron bracket on the wall, glowing; the origin is the bracket's hook."""
    c = Canvas()
    c.add(f'<circle cx="0" cy="26" r="20" fill="{P.SUN}" opacity=".2"/>')
    c.shape(rounded_rect_d(-21, -7, 5, 14, 1.5), P.METAL_DARK, sw=1.2, light=None)
    c.line("M-16,0 H-2 Q2,0 1,3 M-16,4 L-8,0", 2.2, P.METAL_DARK)
    c.line("M0,2 V12", 1.4)
    c.shape("M-6,12 H6 L8,16 H-8 Z", P.METAL_DARK, sw=1.2, light=None)
    c.shape("M-7,16 H7 V34 H-7 Z", P.SUN, sw=1.6, light=None)
    c.line("M-3,16 V34 M3,16 V34", 1.2, P.METAL_DARK)
    c.shape("M-8,34 H8 L6,38 H-6 Z", P.METAL_DARK, sw=1.2, light=None)
    return _at(c, x, y, k)


# ============================================================================ the ship's hold
def _lantern(x: float, y: float, k: float = 1.0) -> str:
    """A hand lantern held by its ring, with a big soft glow; the origin is the ring."""
    c = Canvas()
    c.add(f'<circle cx="0" cy="12" r="44" fill="{P.SUN}" opacity=".16"/>'
          f'<circle cx="0" cy="12" r="24" fill="{P.SUN}" opacity=".22"/>')
    c.path(ellipse_d(0, -1, 4, 3), "none", 1.4)
    c.shape("M-5,2 H5 L7,6 H-7 Z", P.METAL_DARK, sw=1.2, light=None)
    c.shape("M-6,6 H6 V20 H-6 Z", P.SUN, sw=1.5, light=None)
    c.shape("M-1.6,16 Q-2,11 0,9 Q2,11 1.6,16 Z", P.ORANGE, sw=0, light=None)
    c.line("M-6,6 V20 M6,6 V20", 1.6, P.METAL_DARK)
    c.shape("M-7,20 H7 L5,23 H-5 Z", P.METAL_DARK, sw=1.2, light=None)
    return _at(c, x, y, k)


def _slant_ladder(x0: float, y0: float, x1: float, y1: float, w: float) -> str:
    """A ladder leaning from (x0, y0) at the top to (x1, y1) on the floor, `w` wide; absolute units."""
    c = Canvas()
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    nx, ny = -dy / length * w / 2, dx / length * w / 2
    for s in (-1, 1):
        c.line(f"M{n(x0 + nx * s)},{n(y0 + ny * s)} L{n(x1 + nx * s)},{n(y1 + ny * s)}", 5, P.WOOD_DARK)
        c.line(f"M{n(x0 + nx * s)},{n(y0 + ny * s)} L{n(x1 + nx * s)},{n(y1 + ny * s)}", 1.4)
    rungs = max(3, int(length / (w * 0.9)))
    for i in range(1, rungs):
        t = i / rungs
        px, py = x0 + dx * t, y0 + dy * t
        c.line(f"M{n(px - nx)},{n(py - ny)} L{n(px + nx)},{n(py + ny)}", 3.4, P.WOOD)
    return c.render()


def _barrel(x: float, y: float, k: float = 1.0, lying: bool = False) -> str:
    """A barrel, 40 wide and 50 tall standing; lying on its side it is 56 wide and 40 tall."""
    c = Canvas()
    if lying:
        c.shape("M-24,-2 Q-28,-20 -24,-38 H24 Q28,-20 24,-2 Z", P.WOOD, sw=2.2, light=(-2, -2))
        c.line("M-14,-1 Q-17,-20 -14,-39 M14,-1 Q17,-20 14,-39", 2.6, P.METAL_DARK)
        c.shape(ellipse_d(26, -20, 6, 18), P.WOOD_LIGHT, sw=2, light=None)
        c.dot(26, -20, 2)
        return _at(c, x, y, k)
    c.shape("M-18,0 Q-24,-25 -18,-50 H18 Q24,-25 18,0 Z", P.WOOD, sw=2.2, light=(-2, -2),
            stipple=(8, -48, 12, 46, 14, "right"))
    c.line("M-21,-12 H21 M-21,-38 H21", 2.6, P.METAL_DARK)
    c.line("M-8,-1 Q-10,-25 -8,-49 M6,-1 Q8,-25 6,-49", 1, opacity=0.5)
    c.shape(ellipse_d(0, -50, 18, 4), P.WOOD_LIGHT, sw=1.8, light=None)
    return _at(c, x, y, k)


def _dusty_chest(x: float, y: float, k: float = 1.0) -> str:
    """An old iron-bound chest grey with dust (its label is put on by the episode).
    100 wide, 66 tall."""
    c = Canvas()
    c.shape("M-48,0 V-40 H48 V0 Z", P.PEBBLE, sw=2.4, light=(-3, -2), stipple=(-48, -40, 96, 40, 60, "even"))
    c.shape("M-50,-40 Q-50,-66 0,-66 Q50,-66 50,-40 Z", P.STONE, sw=2.4, light=(-3, -3),
            stipple=(-50, -66, 100, 26, 40, "top"))
    c.line("M-32,0 V-63 M32,0 V-63", 3.4, P.METAL_DARK)
    c.line("M-48,-40 H48", 2.6, P.METAL_DARK)
    c.shape(rounded_rect_d(-7, -46, 14, 14, 2), P.METAL_DARK, sw=1.4, light=None)
    c.dot(0, -40, 1.8, P.CHARCOAL)
    c.dots(None, -46, -66, 92, 6, 30, "even", seed=7, r=0.9, color=P.WHITE, opacity=0.8)
    return _at(c, x, y, k)


def _crates(x: float, y: float, k: float = 1.0) -> str:
    """Two plain wooden crates, the smaller on top. 58 wide, 74 tall."""
    c = Canvas()
    for bx, by, w, h in ((-29, 0, 58, 42), (-20, -42, 40, 32)):
        c.shape(f"M{bx},{by} V{by - h} H{bx + w} V{by} Z", P.WOOD_LIGHT, sw=2, light=(-2, -2))
        c.line(f"M{bx},{by - h} L{bx + w},{by} M{bx + 4},{by - h / 2} H{bx + w - 4}", 1.4, P.WOOD_DARK)
    return _at(c, x, y, k)


def _rope_coil(x: float, y: float, k: float = 1.0) -> str:
    """A coil of thick hemp rope lying on the deck: three turns stacked, each twisted, the loose end running off
    along the floor to a whipped tip. 58 wide, 18 tall."""
    c = Canvas()
    hemp, twist = P.AMBER, darken(P.AMBER, 0.7)

    def turn(d: str) -> None:
        c.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="7.4" stroke-linecap="round"/>'
              f'<path d="{d}" fill="none" stroke="{hemp}" stroke-width="4.6" stroke-linecap="round"/>'
              f'<path d="{d}" fill="none" stroke="{twist}" stroke-width="4.6" stroke-dasharray="1.2 3"/>')
    # The loose end, behind the coil, away along the floor.
    turn("M14,-4 Q24,-1 32,-3 Q38,-5 40,-3")
    c.shape(rounded_rect_d(39, -5.6, 5, 5.2, 1.6), lighten(hemp, 0.3), sw=1.1, light=None)
    for i, (rx, ry) in enumerate(((16, 5.4), (12.6, 4.2), (9, 3.2))):
        cy = -5 - i * 4.4
        turn(f"M{-rx},{n(cy)} A{rx},{ry} 0 1 0 {rx},{n(cy)} A{rx},{ry} 0 1 0 {-rx},{n(cy)}")
    c.shape(ellipse_d(0, -13.8, 5, 1.8), darken(P.AMBER, 0.55), sw=1, light=None)      # the hollow in the middle
    return _at(c, x, y, k)


def _fishbone(x: float, y: float, k: float = 1.0) -> str:
    c = Canvas()
    c.line("M-14,-4 H10", 1.6)
    for i in range(4):
        c.line(f"M{-10 + i * 5},-4 l-3,-4 M{-10 + i * 5},-4 l-3,4", 1.2)
    c.path("M10,-4 L18,-9 L18,1 Z", P.WHITE, 1.2)
    c.path("M-14,-4 l-5,-4 v8 Z", P.WHITE, 1.2)
    return _at(c, x, y, k)


# ============================================================================ the episodes
@episode("bookmarks")
def bookmarks(s: Strip) -> None:
    """Bookmarks for next time. The caterpillar cuts paper bookmarks at a table spread with newspaper, paste and
    scissors at hand; the sparrow, meanwhile, has dog-eared every page of his book and proudly shows it, and the
    professor wags a finger at him. Heavy books with a flat iron on top press yesterday's bookmarks; the shelf
    bristles with slips; more bookmarks dry on a string on the wall."""
    s.indoors()
    k = s.unit
    if s.h >= 170:
        y = max(s.h * 0.2 + 4, s.base - s.tall * 1.05)
        x0, x1 = s.x(0.36), s.x(0.6)
        s.put(4, _clothesline(x0, x1, y, k, s.seed), (x0 - 4, y - 4, x1 + 4, y + 34 * k), "line")
    prof = s.cast("professor", 0.05, "point", "talk", flip=False)
    hx, hy = s.hand(prof, "point", False)
    s.put(prof.bottom + 1, f'<path d="M{n(hx + 6 * k)},{n(hy - 14 * k)} q4,4 0,8 M{n(hx - 6 * k)},{n(hy - 14 * k)} '
          f'q-4,4 0,8" fill="none" stroke="{INK}" stroke-width="1.3"/>', None, group=prof.group)
    s.thing(lambda x, y, k: things.stool(x, y, k, P.YELLOW) + _dogeared_book(x, y - 40 * k, k * 1.15),
            0.18, 70, 64, name="book", group="sparrow")
    s.cast("sparrow", 0.29, "present", "smile", flip=True, group="sparrow")
    tx, ty = s.thing(lambda x, y, k: _craft_table(x, y, k), 0.47, 120, 68, name="table", group="table")
    cat = s.cast("caterpillar", 0.63, "point", "smile", flip=True, group="table")
    wx, wy = s.hand(cat, "point", True)
    ck = (cat.bottom - cat.top) / 80
    # She cuts a strip of paper whose other end still lies on the table: it runs from the table's edge to the
    # blades in her hand.
    ex, ey = tx + 50 * k, ty - 48 * k
    bx = wx - 14 * ck
    t = 3.2 * ck
    strip = (f'<path d="M{n(ex)},{n(ey - t)} Q{n((ex + bx) / 2)},{n(max(ey, wy) + 3 * ck)} {n(bx)},{n(wy - t)} '
             f'L{n(bx)},{n(wy + t)} Q{n((ex + bx) / 2)},{n(max(ey, wy) + 3 * ck + 2 * t)} {n(ex)},{n(ey + t * 0.4)} Z" '
             f'fill="{P.YELLOW}" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round"/>')
    s.put(cat.bottom + 1, strip, None, group="table")
    s.put(cat.bottom + 2, _scissors(wx - 2 * ck, wy, ck * 0.9, 180), None, group="table")
    s.thing(lambda x, y, k: _press(x, y, k), 0.75, 66, 78, name="press")
    s.thing(lambda x, y, k: _bookcase_marked(x, y, k, s.seed), 0.91, 92, 106, name="case")

    if s.h >= 300:
        sc = k * 0.45
        _wall(s, lambda x, y: sets.cuckoo_clock(x, y - 83 * sc, sc, (8, 30)),
              [(s.x(f), s.h * 0.2 + 4 + 110 * sc) for f in (0.8, 0.22, 0.7)], 96 * sc, 220 * sc, "cuckoo")


@episode("read_all_day")
def read_all_day(s: Strip) -> None:
    """Read it all in one day. The agent sits dazed on a heap of books with stars circling its head, between an
    old monitor and a vacuum cleaner that it can no longer tell apart: there is a vacuum on the monitor's screen and
    a prompt on a sticky note on the vacuum. The bookcase behind is empty, the sparrow fans the
    agent with a book held in his wing, a snail has found an open one, another lies open on the floor, the tea has
    long gone cold."""
    s.indoors()
    k = s.unit
    s.thing(lambda x, y, k: _bookcase_empty(x, y, k), 0.06, 82, 122, name="case")
    s.thing(lambda x, y, k: _monitor_on_stool(x, y, k), 0.24, 50, 92, name="monitor")
    x, y = s.thing(lambda x, y, k: _book_pile(x - 22 * k, y, k, s.seed, 3, 50) + _book_pile(x + 20 * k, y, k,
                   s.seed + 3, 2, 46) + _book_pile(x, y - 1, k, s.seed + 1, 3, 54), 0.47, 96, 28, name="heap",
                   group="heap")
    agent = s.actor("agent", x, y - 26 * k, "shrug", "surprise", flip=False, tall=s.tall, group="heap")
    s.put(agent.bottom + 2, _star_ring((agent.left + agent.right) / 2, agent.top + 2 * k, k * 0.9),
          (agent.left - 4, agent.top - 6 * k, agent.right + 4, agent.top + 8 * k), "stars", group="heap")
    s.thing(lambda x, y, k: _vacuum(x, y, k), 0.7, 78, 82, name="vacuum")
    s.thing(lambda x, y, k: _book_pile(x, y, k, s.seed + 5, 5, 44) + _teacup(x + 4 * k, y - 45 * k, k * 0.9),
            0.9, 48, 60, name="pile")
    s.thing(lambda x, y, k: _open_book(x + 12 * k, y, k * 0.7, P.ORANGE) + sets.snail(x - 22 * k, y, k * 0.55),
            0.34, 76, 24, nearer=0.95, name="snailbook")
    s.thing(lambda x, y, k: _open_book(x, y, k * 0.75, P.VIOLET), 0.59, 40, 20, nearer=0.95, name="openbook")
    # The sparrow fans the agent with a book held in his wing.
    bird = s.flight("sparrow", 0.6, 0.6, "fly", "worry")
    wx, wy = s.hand(bird, "fly", bird.left > 420, "left")
    bk = (bird.bottom - bird.top) / 100
    # the book goes behind him, its near edge under the finger feathers at his wing's tip, which close over it:
    # it is held by that edge and sticks out beyond the wing; the fanning lines trail from its far end
    out = 1 if wx > (bird.left + bird.right) / 2 else -1
    kk = bk * 1.1
    cx, cy = wx + out * 20 * kk, wy + 4 * bk
    ex = cx + out * 28 * kk
    fan = (f'<path d="M{n(ex)},{n(cy + 2 * bk)} q{n(out * 6 * bk)},{n(5 * bk)} {n(out * 12 * bk)},{n(3 * bk)} '
           f'M{n(ex - out * 2 * bk)},{n(cy + 8 * bk)} q{n(out * 6 * bk)},{n(5 * bk)} {n(out * 11 * bk)},{n(4 * bk)}" '
           f'fill="none" stroke="{INK}" stroke-width="1.2" stroke-linecap="round" stroke-opacity=".6"/>')
    s.put(bird.bottom - 1, _open_book(cx, cy, kk, P.GREEN) + fan, None, group=bird.group)
    if s.h >= 200:
        _wall(s, lambda x, y: _plan_card(x, y, s.word("plan")),
              [(s.x(f), max(s.h * 0.24 + 30, s.base * 0.42)) for f in (0.86, 0.14, 0.36)], 112, 62, "plan")


def _plan_card(x: float, y: float, text: str, size: float = 11) -> str:
    """A sheet pinned to the wall with a red pin, a heading in two lines; centred at (x, y), page units. The box
    the caller reserves is 112 by 62."""
    c = Canvas()
    words = text.split()
    cut = max(1, len(words) // 2) if len(words) > 1 else 1
    lines = [" ".join(words[:cut]), " ".join(words[cut:])] if len(words) > 1 else [text]
    w = min(104, max(sets.letter_width(line, size) for line in lines) + size * 1.6)
    h = 58
    top = y - h / 2 + 4                       # the sheet's top edge; the pin is driven in just under it
    pad = 7.0                                 # the even margin round everything written on the sheet
    c.shape(f"M{n(x - w / 2)},{n(top)} H{n(x + w / 2)} V{n(y + h / 2)} H{n(x - w / 2)} Z", P.WHITE, sw=1.8,
            light=None)
    first = top + 19                           # under the pin, the capitals clear of it
    for i, line in enumerate(lines):
        sets.fit_label(c, x, first + i * size * 1.25, line, size, w - 2 * pad - 2)
    rule = first + (len(lines) - 1) * size * 1.25 + 7
    c.line(f"M{n(x - w / 2 + pad + 2)},{n(rule)} h{n(w - 2 * pad - 8)} M{n(x - w / 2 + pad + 2)},{n(rule + 6)} "
           f"h{n(w - 2 * pad - 20)}", 1.1, opacity=0.5)
    c.add(f'<circle cx="{n(x)}" cy="{n(y - h / 2 + 5)}" r="4.2" fill="{P.RED}" stroke="{INK}" stroke-width="1.4"/>'
          f'<circle cx="{n(x - 1.2)}" cy="{n(y - h / 2 + 3.8)}" r="1.2" fill="{P.WHITE}"/>')
    return f'<g transform="rotate(-3 {n(x)} {n(y)})">{c.render()}</g>'


@episode("briefcase_legs")
def briefcase_legs(s: Strip) -> None:
    """Off to school, lightly. The sparrow trudges down the path under a stuffed satchel bigger than he is - a
    ruler and rolled sheets poke out, a sheet flies off behind, an apple has dropped on the way; the caterpillar
    strolls ahead holding one small card. The school waits far off; butterflies, a ladybug
    on a mushroom, a snail and a signpost line the way."""
    if s.look.season == "winter":
        s.relook(season="autumn")
    s.outdoors()
    k = s.unit
    # The road to school, in perspective: wide in front, under the sparrow's feet, narrowing away to the school.
    # Two quadratic pieces meeting smoothly at the sparrow's feet (their controls lie on one line through there).
    jx, jy = s.x(0.37), s.feet(0)
    pieces = (((s.x(0.26), s.h + 8), (jx - 60 * k, jy + 8 * k), (jx, jy)),
              ((jx, jy), (jx + 120 * k, max(s.base + 1, jy - 16 * k)), (s.x(0.93), s.base)))
    road = [((1 - t) ** 2 * a[0] + 2 * t * (1 - t) * c[0] + t * t * e[0],
             (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * c[1] + t * t * e[1])
            for a, c, e in pieces for t in (i / 8 for i in range(8))] + [pieces[1][2]]
    last = len(road) - 1
    sets.path_band(s.back, road, [s.ground * 1.2 * (1 - i / last) ** 1.6 + 5 * k for i in range(len(road))],
                   seed=s.seed)
    sk = 0.42
    _place(s, lambda x, y, k: _school(x, y, k * sk), s.x(0.95), s.base, 140 * sk, 112 * sk, "school", depth=1)
    word = s.word("school")
    px, py = s.x(0.0) + 6 * k, s.feet(0)
    sk = max(0.56, k * 0.6)          # the lettering on the board never drops below 10 units
    board = (max(66, 12.5 * len(word) + 30) + 18) * sk
    s.put(py - 1, props.signpost(px, py, word, sk), (px - 4 * sk, py - 82 * sk, px + board, py), "sign")
    # The sparrow walks to school bent under a satchel bigger than he is, carried on his back.
    bird = s.actor("sparrow", jx, jy, "walk", "worry", flip=False, tall=s.tall, group="satchel")
    bh = bird.bottom - bird.top
    bx = (bird.left + bird.right) / 2
    sk = bh * 1.2 / 92
    cx, cy = bx - 0.22 * bh, bird.bottom - 0.22 * bh
    s.put(bird.bottom - 0.5, _satchel(cx, cy, sk), (cx - 48 * sk, cy - 92 * sk, cx + 34 * sk, bird.bottom),
          "satchel", group="satchel")
    # Its straps over his shoulders (his own drawing is 200 units square, his body an egg round x = 100).
    u = bh / 190
    straps = "".join(f'<path d="M{n(bx + (sx - 100) * u)},{n(bird.bottom - (190 - 62) * u)} '
                     f'Q{n(bx + (sx * 1.04 - 104) * u)},{n(bird.bottom - (190 - 110) * u)} '
                     f'{n(bx + (sx * 0.96 - 96 + (-6 if sx < 100 else 6)) * u)},{n(bird.bottom - (190 - 150) * u)}" '
                     f'fill="none" stroke="{INK}" stroke-width="{n(max(4.0, 9 * u))}" stroke-linecap="round"/>'
                     f'<path d="M{n(bx + (sx - 100) * u)},{n(bird.bottom - (190 - 62) * u)} '
                     f'Q{n(bx + (sx * 1.04 - 104) * u)},{n(bird.bottom - (190 - 110) * u)} '
                     f'{n(bx + (sx * 0.96 - 96 + (-6 if sx < 100 else 6)) * u)},{n(bird.bottom - (190 - 150) * u)}" '
                     f'fill="none" stroke="{darken(P.LEATHER, 0.85)}" stroke-width="{n(max(2.4, 6 * u))}" '
                     f'stroke-linecap="round"/>' for sx in (66, 134))
    s.put(bird.bottom + 0.5, straps, None, group="satchel")
    dx, dy = bx + 0.26 * bh, bird.top + 0.1 * bh
    s.put(bird.bottom + 1, f'<path d="M{n(dx)},{n(dy)} q{n(-0.03 * bh)},{n(0.05 * bh)} 0,{n(0.07 * bh)} '
          f'q{n(0.03 * bh)},{n(-0.02 * bh)} 0,{n(-0.07 * bh)} Z" fill="{P.WATER_LIGHT}" stroke="{INK}" '
          f'stroke-width="1"/>', None, group="satchel")
    s.thing(lambda x, y, k: _apple(x - 6 * k, y, k) +
            things.giant_pencil(x + 8 * k, y - 2 * k, k * 0.6, 30, 10, P.BLUE),
            0.17, 46, 16, nearer=0.9, name="dropped")
    cat = s.cast("caterpillar", 0.62, "walk", "smile", flip=False)
    hx, hy = s.hand(cat, "walk", False)
    s.put(cat.bottom + 1, _card(hx + 2 * k, hy + 6 * k, k * 1.1, -10), None, group=cat.group)
    s.thing(lambda x, y, k: _ladybug_mushroom(x, y, k), 0.5, 44, 40, nearer=0.85, name="mushrooms")
    s.thing(lambda x, y, k: props.bush(x, y, k * 0.85, berries=True), 0.8, 78, 48, name="bush")
    s.thing(lambda x, y, k: sets.snail(x, y, k * 0.7, mirror=True), 0.74, 40, 26, nearer=0.95, name="snail")
    for frac, color in ((0.52, P.YELLOW), (0.72, P.PINK), (0.24, P.TEAL)):
        bx = s.x(frac)
        _wall(s, lambda x, y, c=color: props.butterfly(x, y, k * 0.8, c),
              [(bx, s.base - s.tall * f) for f in (0.75, 0.55, 0.95, 0.35)], 28 * k, 18 * k, "butterfly", air=4)
    if s.look.season in ("summer", "spring"):
        s.scatter(lambda x, y: props.daisy(x, y, k * 0.5), 4, (s.lo, s.base + 10, s.hi, s.h - 4), (12 * k, 14 * k))


@episode("recipe_cupboard")
def recipe_cupboard(s: Strip) -> None:
    """Recipes kept in the cupboard until they are needed. The caterpillar on a stool puts one more recipe notebook
    on the shelf; guests knock at the door - two hats in its window - and the agent has already pulled out exactly
    the right notebook to meet them. A pie browns in the oven, the kettle steams, and a basket of apples stands on
    the table."""
    s.indoors()
    k = s.unit
    dx, dy = s.thing(lambda x, y, k: _door(x, y, k), 0.05, 70, 124, name="door", group="door")
    agent = s.cast("agent", 0.245, "type", "smile", flip=True, mark="ok", group="agent")
    s.held(agent, "type", True, lambda x, y, k: _notebook(x, y + 4 * k, k * 0.9, P.GREEN))
    # The knock: a sound burst beside the knocker, its long spike reaching to the stud the ring strikes; it may
    # cover the door's right stile, never the knocker.
    size = max(11.0, 10 * k)
    sx_, sy_ = dx + 14 * k, dy - 52 * k                     # just right of the impact lines
    half = (_knock_burst(0, 0, s.word("knock"), size, (0, size * 9))[1][2]) * 0.98      # its right half
    for lift in (60, 72, 48, 86):
        cx, cy = dx + 19 * k + half, dy - lift * k
        art, box = _knock_burst(cx, cy, s.word("knock"), size, (sx_, sy_))
        room = (dx + 19 * k, box[1], box[2], box[3])
        if box[1] > 2 and not any(b.hits(room, 3) for b in s.boxes if b.group != "door"):
            s.put(dy + 2, art, room, "knock", group="door")
            break
    ux, uy = s.thing(lambda x, y, k: _cupboard(x, y, k, s.seed), 0.4, 112, 134, name="cupboard",
                     group="cupboard")
    size = max(10.0, 11 * k)
    plate, box = _plaque(ux, uy - 128 * k, s.word("recipes"), size, 110 * k)    # nailed to the cornice
    s.put(uy - 0.5, plate, box, "plate", group="cupboard")
    sx = ux + 84 * k
    stool_y = s.feet(sx)
    s.put(stool_y - 1, things.stool(sx, stool_y, k, P.RED), (sx - 16 * k, stool_y - 42 * k, sx + 16 * k, stool_y),
          "stool", group="cupboard")
    cat = s.actor("caterpillar", sx, stool_y - 40 * k, "present", "talk", flip=True, tall=s.tall, group="cupboard",
                  depth=uy + 0.5)
    hx, hy = s.hand(cat, "present", True)
    ck = (cat.bottom - cat.top) / 80
    s.put(uy + 1, _notebook(hx, hy + 8 * ck, ck * 0.9, P.ORANGE, -12), None, group="cupboard")
    tx, ty = s.thing(lambda x, y, k: things.kitchen_table(x, y, k, 86, P.WOOD_LIGHT, P.BLUE), 0.71, 90, 50,
                     name="table", group="table")
    s.put(ty + 1, _basket_apples(tx - 10 * k, ty - 48 * k, k * 0.9), None, group="table")
    s.thing(lambda x, y, k: _stove(x, y, k), 0.89, 82, 96, name="stove")
    s.thing(lambda x, y, k: _card(x, y, k * 1.2, 14), 0.28, 22, 14, nearer=0.95, name="card")
    if s.h >= 200:
        y = s.h * 0.2 + 8              # under the strip's melting top
        x0, x1 = s.x(0.66), s.x(0.94)
        box = (x0 - 4, y - 4, x1 + 4, y + 40 * k)
        if s.free(box, 6):
            s.put(4, _ladle_rail(x0, x1, y, k), box, "rail")


@episode("notebook_memory")
def notebook_memory(s: Strip) -> None:
    """Write it down and it is remembered. Over tea with pirozhki and jam, the caterpillar, perched on the dresser,
    writes the recipe into her notebook; the agent copies it onto a card it will keep; the professor, a napkin
    tucked in, nods with his thumb up. A cactus flowers on the windowsill, a bee circles the jam, the kettle
    steams on the stove."""
    s.decor = False    # this room has its own walls and windows
    s.indoors()
    k = s.unit
    prof = s.cast("professor", 0.06, "thumb", "smile", flip=False)
    ph = prof.bottom - prof.top
    s.put(prof.bottom + 2, _napkin((prof.left + prof.right) / 2 + ph * 0.02, prof.top + ph * 0.375, ph / 137 * 0.8),
          None, group=prof.group)
    tx, ty = s.thing(lambda x, y, k: _tea_table(x, y, k), 0.3, 132, 76, name="table")
    _wall(s, lambda x, y: things.bee(x, y, k * 0.8), [(tx - 4 * k, ty - 96 * k), (tx + 10 * k, ty - 90 * k)], 18 * k,
          12 * k, "bee", air=3)
    agent = s.cast("agent", 0.48, "type", "smile", flip=True, group="agent")
    s.held(agent, "type", True, lambda x, y, k: _card(x, y + 2 * k, k * 1.3, 6) +
           things.giant_pencil(x + 6 * k, y - 4 * k, k * 0.22, 60, -120, P.RED))
    dx, dy = s.thing(lambda x, y, k: _dresser(x, y, k), 0.68, 84, 58, name="dresser", group="dresser")
    s.actor("caterpillar", dx - 14 * k, dy - 57 * k, "write", "talk", flip=True, tall=s.tall,
                  group="dresser")
    s.thing(lambda x, y, k: _stove(x, y, k), 0.88, 82, 96, name="stove")
    wk = k * 0.66
    wy = s.h * 0.2 + 50 * wk + 2       # under the strip's melting top
    window = s.h >= 220 and _wall(s, lambda x, y: _arched_window(x, y + 50 * wk, wk, sky_colors(s.look)[1]),
                                  [(s.x(f), wy) for f in (0.66, 0.82, 0.5, 0.4, 0.92, 0.22)],
                                  80 * wk, 100 * wk, "window", air=6)
    if not window:
        s.put(dy - 2, things.cactus(dx + 26 * k, dy - 57 * k, k * 0.9), None, group="dresser")



@episode("gnome_shelves")
def gnome_shelves(s: Strip) -> None:
    """How much fits? Three bays of shelving step up like stairs - one holding a single page, one a few books, one
    crammed full - each with a board saying what it is: page, book, library. The sparrow stands on top of the
    smallest, the caterpillar asks how much will fit, the agent has climbed the ladder by the biggest and points
    at its rows; the cat explains by a cart of books."""
    s.indoors()
    k = s.unit
    feet = s.feet(0)
    top_room = s.h * 0.2 + 6            # the tallest bay stays under the strip's melting top
    tallest = max(60.0, min(170.0, (feet - top_room) / k))
    size = max(10.0, 10.5 * k)
    bays = ((92, 0.4, 0, "page"), (96, 0.68, 1, "book"), (116, 1.0, 2, "library"))
    tops = []
    x = s.x(0.2)
    for i, (w, share, fill, word) in enumerate(bays):
        if i:
            x += (bays[i - 1][0] + w) / 2 * k + 12
        h = tallest * share
        group = f"bay{i}"
        y = s.feet(x)
        s.put(y - 1, _bay(x, y, k, w, h, fill, s.seed + i), (x - w * k / 2, y - h * k, x + w * k / 2, y), group,
              group=group)
        tops.append((x, y - h * k))
        # The board is nailed across the bay's top rail.
        plate, box = _plaque(x, y - h * k + size * 0.7, s.word(word), size, (w + 10) * k)
        s.put(y + 0.5, plate, box, f"plate{i}", group=group)
    # The sparrow stands on top of the smallest bay: a page is about his size.
    px, py = tops[0]
    s.actor("sparrow", px, py, "cheer", "smile", flip=False, tall=s.tall * 0.8, group="bay0")
    # The agent climbs the ladder leaning on the biggest bay, a book under its arm, in front of the ladder.
    lx = tops[2][0] + 58 * k + 12 * k
    ltop = tops[2][1] + 6 * k
    s.put(feet - 1, sets.ladder(lx, ltop, feet, 22 * k), (lx - 13 * k, ltop, lx + 13 * k, feet), "ladder", group="bay2")
    rung = feet - 18                   # the rungs of `sets.ladder`: 18 up from the floor, then every 26
    while rung - 13 > feet - tallest * k * 0.42:
        rung -= 26
    s.actor("agent", lx, rung, "point", "smile", flip=True, tall=s.tall, group="bay2", depth=feet + 1)
    cat = s.cast("caterpillar", 0.06, "point", "worry", flip=False)
    if not s.say(cat, s.word("label"), prefer="right"):
        s.put(cat.bottom + 1, props.mark((cat.left + cat.right) / 2, cat.top - 14, "?", 0.8), None, group=cat.group)
    s.thing(lambda x, y, k: _book_cart(x, y, k), 0.8, 58, 54, name="cart")
    s.cast("cat", 0.93, "present", "talk", flip=True)
    s.thing(lambda x, y, k: _open_book(x, y, k * 0.5, P.TEAL), 0.7, 28, 10, nearer=0.95, name="dropped")


@episode("fireside")
def fireside(s: Strip) -> None:
    """A fairy tale by the fire. The professor stands by his wing armchair reading aloud from a big book; the cat
    listens sitting on a big floor cushion, a checked plaid over his lap; the caterpillar knits a striped
    scarf, the yarn running to her from a ball on the floor. Candles burn on the mantel."""
    s.indoors()
    k = s.unit
    feet = s.feet(0)
    s.put(1, sets.rug_round(s.x(0.48), feet + s.ground * 0.25, 110 * k, 12 * k, P.TEAL), None, "rug")
    ax = s.x(0.05)
    s.put(feet - 2, _armchair(ax, feet, k), (ax - 46 * k, feet - 112 * k, ax + 46 * k, feet), "chair",
          group="prof", backdrop=True)
    prof = s.actor("professor", ax + 62 * k, feet, "read", "talk", flip=False, tall=s.tall, group="prof")
    s.put(prof.bottom + 1, _over_body(prof, "professor", "read", _reader_book, 20, 0.9), None, group="prof")
    px = s.x(0.31)
    probe = Strip(s.h, 0, None, s.look).actor("cat", px, feet, "sit", "smile", tall=s.tall)
    cw = (probe.right - probe.left) * 1.15                              # the cushion: wider than him
    ch_ = cw * 0.26
    s.put(feet - 1, _floor_cushion(px, feet, cw), (px - cw / 2 - 2, feet - ch_ * 1.1, px + cw / 2 + 2, feet),
          "cushion", group="cat")
    cat = s.actor("cat", px, feet - ch_ * 0.7, "sit", "smile", flip=False, tall=s.tall, group="cat")
    ch = cat.bottom - cat.top
    top = cat.top + ch * 0.76                                           # over his lap, his paws free above it
    s.put(cat.bottom + 3, _plaid(px, top, (cat.right - cat.left) * 0.62, feet - ch_ * 0.8 - top), None, group="cat")
    fx, fy = s.thing(lambda x, y, k: _fireplace(x, y, k), 0.5, 116, 120, name="fire", group="fire")
    s.thing(lambda x, y, k: _log_basket(x, y, k), 0.65, 48, 34, name="logs")
    # The caterpillar knits; the yarn runs in one smooth curve from the ball on the floor up to her needles.
    knit = s.cast("caterpillar", 0.79, "knit", "smile", flip=True, group="knit")
    s.put(knit.bottom + 1, _over_body(knit, "caterpillar", "knit", _knitting_work, 8, 0.84), None, group="knit")
    mk = (knit.bottom - knit.top) / (module("caterpillar").FEET_Y - module("caterpillar").HEAD_TOP)
    cxk = (knit.left + knit.right) / 2
    kx, ky = _knit_top()
    tx = cxk - (kx - module("caterpillar").CENTER_X) * mk          # the last stitch on the needle (she faces left)
    ty = knit.bottom - (module("caterpillar").FEET_Y - ky) * mk
    r = 9 * k
    yx, yy = knit.right + 14 * k, feet + s.ground * 0.32          # on the side of the stitches, clear of her tail
    s.put(yy, _yarn_ball(yx, yy, r, P.RED) , (yx - r - 2, yy - 2 * r - 2, yx + r + 2, yy), "yarn", group="knit")
    thread = (f"M{n(yx - r * 0.5)},{n(yy - 2 * r + 1)} C{n(yx - r * 0.8)},{n(yy - 6 * r)} "
              f"{n(tx + 10 * k)},{n(ty + 20 * k)} {n(tx)},{n(ty)}")
    tc = Canvas()
    tc.line(thread, 2.6)
    tc.line(thread, 1.4, P.RED)
    s.put(knit.bottom + 2, tc.render(), None, group="knit")


@episode("map_counter")
def map_counter(s: Strip) -> None:
    """A map of the kitchen. The cat sits up on the counter and unfolds a big colourful map down its front: hills,
    lakes, a forest and a dotted way to a red cross; the agent follows the dotted way with its finger. The sparrow,
    who went looking without a map, is lost in the chest of drawers - every drawer open, spoons and a sock
    spilling out. The compass lies forgotten on the floor."""
    s.indoors()
    k = s.unit
    s.thing(lambda x, y, k: props.plant(x, y, k * 0.9), 0.04, 62, 80, name="plant")
    dx, dy = s.thing(lambda x, y, k: _drawers(x, y, k), 0.19, 76, 100, name="drawers", group="drawers")
    bird = s.actor("sparrow", dx - 2 * k, dy - 68 * k, "shrug", "worry", flip=False, tall=s.tall * 0.85,
                   group="drawers", depth=dy + 0.5)
    s.put(dy + 1, _drawers(dx, dy, k, front=True), None, group="drawers")
    _badge(s, bird, "?")
    cx = s.x(0.58)
    cy = s.feet(cx)
    mx = cx - 44 * k
    probe = Strip(s.h, 0, None, s.look)
    pb = probe.actor("agent", 0, cy, "point", "smile", flip=False, tall=s.tall)
    hx, hy = probe.hand(pb, "point", False)
    s.actor("agent", mx - 47 * k - hx, cy, "point", "smile", flip=False, tall=s.tall, group="counter")
    s.thing(lambda x, y, k: _counter(x, y, k, 210), 0.58, 214, 64, name="counter", group="counter")
    start = max(8.0, min(62.0, (hy - (cy - 58 * k)) / (k * 0.86)))
    s.put(cy + 1, _map(mx, cy - 58 * k, k * 0.86, start), None, group="counter")
    s.actor("cat", cx + 34 * k, cy - 62 * k, "present", "talk", flip=True, tall=s.tall * 0.95,
                  group="counter")
    s.thing(lambda x, y, k: _fridge(x, y, k), 0.9, 56, 118, name="fridge")
    s.thing(lambda x, y, k: _compass(x, y, k * 1.2), 0.81, 36, 38, nearer=1.0, name="compass")
    if s.h >= 200:
        y = s.h * 0.2 + 8              # under the strip's melting top
        for a, b in ((0.66, 0.8), (0.36, 0.5), (0.8, 0.96), (0.2, 0.34)):
            x0, x1 = s.x(a), s.x(b)
            box = (x0 - 4, y - 4, x1 + 4, y + 40 * k)
            if s.free(box, 6):
                s.put(4, _ladle_rail(x0, x1, y, k), box, "rail")
                break


@episode("mystery_book")
def mystery_book(s: Strip) -> None:
    """The mysterious tome in the captain's cabin. By candlelight, among the inkwell, the quill and the coins, lies
    a huge old book, and the agent who found it cheers - its title reads like the file every
    repository should have. The caterpillar gasps «!», the sparrow on the sea chest wonders «?», the
    parrot on its perch has seen it all; a gold coin rolls across the floor."""
    s.decor = False    # this room has its own walls and windows
    s.indoors()
    k = s.unit
    for i in range(int(s.base // (18 * k)) + 1):      # the cabin's planked walls
        yy = s.base - i * 18 * k
        s.back.line(f"M0,{n(yy)} H840", 1, P.WOOD_DARK, 0.25)
    s.thing(lambda x, y, k: _captain_desk(x, y, k), 0.06, 94, 98, name="desk")
    s.cast("caterpillar", 0.215, "cheer", "surprise", flip=False, mark="!")
    # The tome lies shut on the floor; the agent, who found it, cheers beside it.
    # its title plate holds lettering of 12 at most (the cover is that shallow), so on a small strip the tome is
    # drawn bigger, for the title to stay readable on the page
    size = 12.0
    kt = max(k, sets.LETTERING_MIN / size)
    tx, ty = s.thing(lambda x, y, k: _tome(x, y, kt, s.word("title"), size), 0.455, 176 * kt / k, 64 * kt / k,
                     name="tome", group="tome")
    s.actor("agent", tx + 88 * kt + 24 * k, ty, "cheer", "smile", flip=True, tall=s.tall * 0.95, group="tome")
    chx, chy = s.thing(lambda x, y, k: _sea_chest(x, y, k), 0.75, 56, 38, name="chest", group="chest")
    bird = s.actor("sparrow", chx, chy - 36 * k, "shrug", "surprise", flip=True, tall=s.tall, group="chest")
    _badge(s, bird, "?")
    s.thing(lambda x, y, k: _parrot_perch(x, y, k), 0.92, 40, 102, name="parrot")

    s.thing(lambda x, y, k: _coin(x, y, k), 0.27, 22, 16, nearer=0.95, name="coin")
    s.thing(lambda x, y, k: _coin_stack(x, y, k), 0.63, 30, 18, nearer=0.9, name="coins")
    if s.h >= 200:
        wy = max(s.h * 0.2 + 30 * k, s.base * 0.36)
        _wall(s, lambda x, y: sets.round_window(x, y, 18 * k),
              [(s.x(f), wy) for f in (0.3, 0.16, 0.4)], 50 * k, 50 * k, "porthole")
        _wall(s, lambda x, y: _ship_wheel(x, y, 18 * k),
              [(s.x(f), wy) for f in (0.78, 0.66, 0.86)], 52 * k, 52 * k, "wheel")
        _wall(s, lambda x, y: _hanging_lantern(x, y - 20 * k, k),
              [(s.x(f), wy + 4 * k) for f in (0.56, 0.62, 0.5, 0.88)], 46 * k, 44 * k, "lantern")


@episode("ship_hold")
def ship_hold(s: Strip) -> None:
    """Down into the hold of an old ship: a ladder comes down from the hatch, where the daylight falls in; the agent
    is already down and holds up a lantern, the cat follows carefully on the ladder, the sparrow flutters about.
    Among barrels, crates, a coil of rope and a fishbone stands a dusty chest, labelled as the old
    code."""
    s.decor = False    # this room has its own walls and windows
    s.indoors()
    k = s.unit
    feet = s.feet(0)
    for i in range(7):   # the ribs of the hull
        rx = 60 + i * 120
        s.back.add(f'<path d="M{rx},{s.base} Q{rx - 16},{n(s.base * 0.5)} {rx + 4},0" fill="none" '
                   f'stroke="{darken(P.WOOD, 0.6)}" stroke-width="{n(10 * k)}" stroke-opacity=".7"/>')
    # The deck above, cut open for the hatch: a heavy beam the ladder leans on; daylight falls through.
    top = max(s.h * 0.2 + 6, feet - 200 * k)
    deck_x = s.x(0.13)
    s.back.add(f'<path d="M0,0 H{n(deck_x)} L{n(s.x(0.36))},{n(s.base)} H{n(s.x(0.02))} Z" fill="{P.SUN}" '
               f'opacity=".16"/>')
    dc = Canvas()
    dc.shape(f"M-10,{n(top - 9 * k)} H{n(deck_x)} V{n(top + 7 * k)} H-10 Z", P.WOOD_DARK, sw=2.2, light=(0, -2))
    dc.line(f"M-10,{n(top - 1 * k)} H{n(deck_x - 3)}", 1, opacity=0.4)
    s.put(2, dc.render(), (0, top - 9 * k, deck_x, top + 7 * k), "deck", group="ladder")
    x0, y0 = deck_x - 16 * k, top - 9 * k
    x1, y1 = s.x(0.24), feet
    w = 26 * k
    pts = [(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2), (x1, y1)]
    s.put(feet - 2, _slant_ladder(x0, y0, x1, y1, w), strip_boxes(pts, w), "ladder", group="ladder")
    # The cat stands on a rung (the rungs of `_slant_ladder` are at i / rungs of its length).
    rungs = max(3, int(math.hypot(x1 - x0, y1 - y0) / (w * 0.9)))
    cat_h = s.tall * 0.95 * 101 / 132
    best = None
    for i in range(1, rungs):
        t = i / rungs
        if y0 + (y1 - y0) * t - cat_h > s.h * 0.1 and (best is None or abs(t - 0.5) < abs(best - 0.5)):
            best = t
    if best is not None and best < 0.9:
        cx, cy = x0 + (x1 - x0) * best, y0 + (y1 - y0) * best
        s.actor("cat", cx, cy, "stand", "worry", flip=False, tall=s.tall * 0.95, group="ladder", depth=feet - 1)
    # The agent, already down, holds up its lantern towards the chest.
    agent = s.cast("agent", 0.33, "point", "smile", flip=False, group="ladder")
    s.in_hand(agent, "point", False, lambda x, y, k: _lantern(x, y, k / 1.2))
    s.flight("sparrow", 0.44, 0.75, "fly", "smile")
    bx, by = s.thing(lambda x, y, k: _barrel(x - 14 * k, y, k) + _barrel(x + 30 * k, y, k, lying=True), 0.56, 104,
                     52, name="barrels", group="barrels")
    # the chest is big enough for its label to sit on its front with a margin, on two lines when it must
    size = max(10.0, 10 * k)
    ck = max(k * 1.15, (size * 2.95 + 6) / 40)
    grow = ck / k
    chx, chy = s.thing(lambda x, y, k: _dusty_chest(x, y, k * grow), 0.77, 102 * grow, 68 * grow, name="chest",
                       group="chest")
    plate, box = _plaque(chx, chy - 20 * ck, s.word("old"), size, 84 * ck, P.CARD)
    s.put(chy, plate, box, "label", group="chest")
    s.thing(lambda x, y, k: _crates(x, y, k), 0.93, 60, 76, name="crates")
    s.thing(lambda x, y, k: _rope_coil(x, y, k), 0.44, 62, 24, nearer=0.95, name="rope")
    s.thing(lambda x, y, k: _fishbone(x, y, k), 0.68, 40, 12, nearer=0.95, name="fish")

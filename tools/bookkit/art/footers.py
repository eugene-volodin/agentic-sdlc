"""Footer strips: a scene at the foot of every page, and which scene goes on which page.

A chapter lives in a world (`world:` in its front matter, `worlds.py`): its footers are a camera moving along the
world's machine, station by station, and a chapter is planned from its own pages only, so `--only` draws what the full
build draws. A chapter of the main matter not given a world yet lives in the introduction's courtyard; the front pages
and the contents show the professor's courtyard (the world `front`, `world_courtyard.py`), a moment chosen by a
phrase of the page's text.

A footer draws on a `Strip`: the same composition tools as the chapter openers (boxes, groups, the no-overlap check),
at any height from the 34 mm strip to the 190 mm panorama. Units: 840 across, `h` down.
"""
from __future__ import annotations

import math
import zlib
from dataclasses import dataclass, replace

from .. import design as P
from ..design import darken, lighten, mix
from . import props, sets
from .characters import module
from .ink import Canvas
from .openers import W, Box, Stage, conflicts

TAG = 100            # how far in from the edge the page-number tag reaches, in units
TAG_HEIGHT = 80      # and how high up from the bottom
TALL_MAX = 165       # the professor's height in a footer never grows beyond this


# ============================================================================ the look of a chapter
@dataclass(frozen=True)
class Look:
    """Time of day, season and the chapter's color, so the same episode differs from chapter to chapter.

    The chapter's color is in every footer of the chapter (each chapter has its color, and its pages keep to
    it): the sky and the walls are the paper tinted with it, the ground takes a little of it."""
    time: str              # morning | day | evening
    season: str            # summer | autumn | winter | spring
    accent: str = P.YELLOW


LOOKS = (Look("day", "summer"), Look("morning", "spring"), Look("evening", "summer"), Look("day", "autumn"),
         Look("morning", "summer"), Look("day", "winter"), Look("evening", "autumn"), Look("day", "spring"),
         Look("morning", "autumn"), Look("evening", "winter"), Look("morning", "winter"), Look("evening", "spring"))


def look_for(chapter_index: int, accent: str = P.YELLOW) -> Look:
    base = LOOKS[chapter_index % len(LOOKS)]
    return Look(base.time, base.season, accent or P.YELLOW)


def sky_colors(look: Look) -> tuple[str, str]:
    """(top, horizon) of the sky: the top is the paper itself, the horizon the paper tinted with the chapter."""
    horizon = lighten(look.accent, 0.62)       # a tint towards white: towards the cream paper it would turn grey
    if look.time == "morning":
        horizon = mix(horizon, P.YELLOW_PALE, 0.3)
    elif look.time == "evening":
        horizon = mix(lighten(look.accent, 0.5), P.ORANGE, 0.14)
    return P.PAPER, horizon


def wall_color(look: Look) -> str:
    """A room's wall: the paper tinted with the chapter's color."""
    return mix(lighten(look.accent, 0.7), P.PAPER, 0.25)


def ground_colors(look: Look) -> tuple[str, str]:
    """(near, far) ground by the season, with a touch of the chapter's color."""
    near, far = GROUNDS[look.season]
    return mix(near, look.accent, 0.08), mix(far, look.accent, 0.12)


def night_sky(look: Look) -> tuple[str, str]:
    """For a story set in space or at night: a deep sky in the chapter's color, still paper at the very top."""
    return P.PAPER, darken(mix(look.accent, P.PEN, 0.6), 0.6)


GROUNDS = {   # (near, far) grass by season
    "summer": (P.GRASS, P.GRASS_DARK),
    "spring": (lighten(P.GRASS, 0.15), P.GRASS),
    "autumn": (lighten(P.AMBER, 0.35), darken(P.AMBER, 0.85)),
    "winter": (P.WHITE, lighten(P.SKY, 0.35)),
}


# ============================================================================ the strip
def _cloud_segments(x0: float, y0: float, w: float, h: float) -> list[tuple]:
    """The puffy speech cloud filling the box as quadratic segments (start, control, end): round bumps all the way
    round, joined smoothly."""
    cx, cy, rx, ry = x0 + w / 2, y0 + h / 2, w / 2, h / 2
    count = max(8, int((w + h) / 22))
    pts = [(cx + rx * 0.9 * math.cos(math.tau * i / count), cy + ry * 0.86 * math.sin(math.tau * i / count))
           for i in range(count)]
    out = []
    for i in range(count):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % count]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ox, oy = (mx - cx) / rx, (my - cy) / ry                 # push the bump outward
        size = math.hypot(ox, oy) or 1
        out.append(((x1, y1), (mx + ox / size * rx * 0.22, my + oy / size * ry * 0.3), (x2, y2)))
    return out


def _rounded_segments(x: float, y: float, w: float, h: float, r: float) -> list[tuple]:
    """A rounded rectangle as quadratic segments, clockwise from the top edge."""
    def line(a, b):
        return (a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), b)
    return [line((x + r, y), (x + w - r, y)), ((x + w - r, y), (x + w, y), (x + w, y + r)),
            line((x + w, y + r), (x + w, y + h - r)), ((x + w, y + h - r), (x + w, y + h), (x + w - r, y + h)),
            line((x + w - r, y + h), (x + r, y + h)), ((x + r, y + h), (x, y + h), (x, y + h - r)),
            line((x, y + h - r), (x, y + r)), ((x, y + r), (x, y), (x + r, y))]


def _bubble_d(segments: list[tuple], tip: tuple[float, float], spread: float) -> str:
    """A speech bubble and its tail as ONE outline: the body's edge runs on until it turns, tangentially, into the
    tail's side, goes out to the tip and comes back the same way - no notch where the tail joins, at any bump of a
    cloud. `segments` are the body's quadratic pieces (`_cloud_segments`, `_rounded_segments`); the tail leaves
    from the edge where it faces `tip`, `spread` wide on each side."""
    pts = []
    for (x0, y0), (qx, qy), (x2, y2) in segments:                # the edge, sampled about a unit apart
        steps = max(2, int(math.hypot(x2 - x0, y2 - y0) / 1.0))
        for i in range(steps):
            t = i / steps
            pts.append(((1 - t) ** 2 * x0 + 2 * t * (1 - t) * qx + t * t * x2,
                        (1 - t) ** 2 * y0 + 2 * t * (1 - t) * qy + t * t * y2))
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    tx, ty = tip
    aim = math.atan2(ty - cy, tx - cx)                           # the edge point that faces the tip
    mid = min(range(len(pts)), key=lambda i: abs(math.remainder(math.atan2(pts[i][1] - cy, pts[i][0] - cx) - aim,
                                                                math.tau)) + 0.002 * math.hypot(pts[i][0] - tx,
                                                                                                pts[i][1] - ty))
    count = len(pts)

    def walk(start: int, way: int, length: float) -> int:
        i, gone = start, 0.0
        while gone < length:
            j = (i + way) % count
            gone += math.hypot(pts[j][0] - pts[i][0], pts[j][1] - pts[i][1])
            i = j
        return i

    a, e = walk(mid, -1, spread), walk(mid, 1, spread)          # the tail's two roots on the edge

    def tangent(i: int) -> tuple[float, float]:
        (x1, y1), (x2, y2) = pts[(i - 2) % count], pts[(i + 2) % count]
        size = math.hypot(x2 - x1, y2 - y1) or 1
        return (x2 - x1) / size, (y2 - y1) / size

    (ax, ay), (ex, ey) = pts[a], pts[e]
    (tax, tay), (tex, tey) = tangent(a), tangent(e)
    reach = math.hypot(tx - (ax + ex) / 2, ty - (ay + ey) / 2) or 1
    ux, uy = (tx - (ax + ex) / 2) / reach, (ty - (ay + ey) / 2) / reach
    flare = spread * 0.9                                         # how far each root runs on along the edge
    neck = reach * 0.45                                          # where the sides gather toward the tip
    d = f"M{ex:.1f},{ey:.1f}"
    i = e
    while i != a:                                                # the long way round, from one root to the other
        i = (i + 1) % count
        d += f" L{pts[i][0]:.1f},{pts[i][1]:.1f}"
    half = math.hypot(ax - ex, ay - ey) / 2 or 1
    sx, sy = (ax - ex) / 2 / half, (ay - ey) / 2 / half          # across the tail, toward its a side
    nx, ny = tx - ux * neck, ty - uy * neck
    side = spread * 0.3
    d += (f" C{ax + tax * flare:.1f},{ay + tay * flare:.1f} {nx + sx * side:.1f},{ny + sy * side:.1f} "
          f"{tx:.1f},{ty:.1f}")
    d += (f" C{nx - sx * side:.1f},{ny - sy * side:.1f} {ex - tex * flare:.1f},{ey - tey * flare:.1f} "
          f"{ex:.1f},{ey:.1f} Z")
    return d


class Strip(Stage):
    """A footer being composed: `h` units tall, the page-number tag held clear at one corner."""

    def __init__(self, h: float, seed: int, clear: str | None, look: Look, words: dict | None = None) -> None:
        tag = (0, h - TAG_HEIGHT, TAG, h) if clear == "left" else (W - TAG, h - TAG_HEIGHT, W, h)
        super().__init__(seed, words=words, height=h, reserved=[tag] if clear else [])
        self.look = look
        self.clear = clear
        self.seed = seed
        self.indoor = False
        self.decor = True            # an episode with a wall of its own (a ship's cabin) turns the wall decor off
        self.dress = True            # the sun, clouds and birds put into the free sky; off for a sky of its own
        self.ground = max(42, min(h * 0.30, 110))                 # thickness of the ground band
        self.base = h - self.ground                               # the horizon line
        tall = min(h * 0.74, 290) if h < 400 else min(h * 0.62, 340)
        # How tall the professor would be. Episodes are composed across the width in fractions, so the cast keeps
        # the same size from the 55 mm strip up: a panorama gets more sky or wall, filled by `distance`.
        self.tall = min(tall, self.base * 0.86, TALL_MAX)
        self.unit = self.tall / 137                               # scale of props drawn for a 137-unit professor
        self.lo = TAG + 14 if clear == "left" else 30
        self.hi = W - TAG - 14 if clear == "right" else W - 30
        self.big = h >= 300                                       # a panorama: room for a background story

    # ----------------------------------------------------------------- placing
    def x(self, frac: float) -> float:
        """A position across the usable width, 0 at its left end and 1 at its right."""
        return self.lo + (self.hi - self.lo) * frac

    def feet(self, x: float, nearer: float = 0) -> float:
        """Where feet touch the ground at x; `nearer` (0..1) brings them down into the foreground."""
        return self.base + min(16, self.ground * 0.3) + nearer * self.ground * 0.45

    def cast(self, name: str, frac: float, pose: str = "stand", mood: str = "smile", flip: bool | None = None,
             mark: str | None = None, nearer: float = 0, size: float = 1.0, group: str | None = None,
             **options) -> Box:
        """Stand a character at `frac` across; it faces the middle unless told, and may wear a badge."""
        x = self.x(frac)
        feet = self.feet(x, nearer)
        flip = x > W / 2 if flip is None else flip
        box = self.actor(name, x, feet, pose, mood, flip=flip, tall=self.tall * size, group=group, **options)
        if mark:
            k = min(1.3, max(0.6, self.tall / 160))
            above = box.top - 18 * k - 2
            mx = x if above > 18 * k + 2 else x + (box.right - box.left) * 0.62 * (-1 if flip else 1)
            my = above if above > 18 * k + 2 else box.top + 18 * k
            self.put(feet + 1, props.mark(mx, my, mark, k), (mx - 17 * k, my - 17 * k, mx + 17 * k, my + 17 * k),
                     group=box.group)
        return box

    def thing(self, make, frac: float, width: float, height: float, nearer: float = 0, name: str = "",
              group: str | None = None, depth: float | None = None, backdrop: bool = False) -> tuple[float, float]:
        """Put a prop standing on the ground at `frac` across; `make(x, y, k)` draws it at scale k, and
        `width` / `height` are its size at scale 1. Returns where it stands."""
        x = self.x(frac)
        y = self.feet(x, nearer)
        k = self.unit
        self.put(depth if depth is not None else y - 1, make(x, y, k),
                 (x - width * k / 2, y - height * k, x + width * k / 2, y), name or f"thing{len(self.boxes)}",
                 group=group, backdrop=backdrop)
        return x, y

    # ----------------------------------------------------------------- settings
    def outdoors(self, path: bool = False, hills: bool = True) -> None:
        """Sky by the time of day, ground by the season; far hills when there is room."""
        c, h, look = self.back, self.h, self.look
        top, low = sky_colors(look)
        sets.sky(c, top, low, self.base + 10, W)
        rnd = self.rnd
        if hills and h >= 190:
            near, far = ground_colors(look)
            hill = mix(lighten(far, 0.35), low, 0.35) if look.season != "winter" else mix(P.WHITE, low, 0.4)
            sets.hills(c, self.base + 6, W, (hill, lighten(near, 0.2)), seed=rnd.randrange(99))
        near, far = ground_colors(look)
        sets.meadow(c, self.base, h, W, seed=rnd.randrange(99), color=near, near=far)
        if look.season == "winter":
            self._snow()
        else:
            sets.grass_tufts(c, (0, self.base + 6, W, h), int(20 + h / 6), seed=rnd.randrange(99))
        if look.season == "autumn":
            for _ in range(int(8 + h / 30)):   # fallen leaves
                x, y = rnd.uniform(10, W - 10), rnd.uniform(self.base + 8, h - 4)
                color = rnd.choice((P.AMBER, P.ORANGE, P.RED))
                c.add(f'<path d="M{x:.1f},{y:.1f} q5,-7 10,0 q-5,5 -10,0 Z" fill="{color}" stroke="{P.INK}" '
                      f'stroke-width="1" transform="rotate({rnd.randrange(360)} {x:.1f} {y:.1f})"/>')
        if path:
            # a country track winding from the horizon to the front edge, narrow far off and wide near
            g, side = self.ground, rnd.choice((-1, 1))
            mid = self.x(rnd.uniform(0.4, 0.6))
            route = [(mid + side * 70, self.base + 3), (mid + side * 30, self.base + g * 0.18),
                     (mid - side * 20, self.base + g * 0.5), (mid + side * 10, self.base + g * 0.8),
                     (mid - side * 10, h + 12)]
            sets.path_band(c, route, [4, g * 0.22, g * 0.5, g * 0.8, g * 1.1], seed=rnd.randrange(99), soft=True)

    def svg(self, css_class: str, align: str = "xMidYMid", marks: bool = True) -> str:
        """The strip as `<svg>`: the backdrop (sky, wall, whatever an episode painted behind) is veiled so that
        its top melts into the paper - the picture grows out of the page, with no edge."""
        reach = min(self.base * 0.6, 150)
        back = self.back
        self.back = type(back)()
        self.back.add(back.render())
        solid = (10 + reach * 0.25) / (reach + 10)
        self.back.fade(-10, -10, W + 20, reach + 10, [(0, P.PAPER, 1), (solid, P.PAPER, 1), (1, P.PAPER, 0)])
        try:
            return super().svg(css_class, align, marks)
        finally:
            self.back = back

    def _snow(self) -> None:
        c, rnd = self.back, self.rnd
        for _ in range(int(30 + self.h / 4)):
            x, y = rnd.uniform(0, W), rnd.uniform(4, self.h - 4)
            c.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.4, 3):.1f}" fill="{P.WHITE}" '
                  f'stroke="{P.METAL}" stroke-width=".6"/>')

    def indoors(self) -> None:
        """A room: a wall in the chapter's colour and light (never the episode's), floor boards."""
        c, h = self.back, self.h
        self.indoor = True
        sets.wall(c, wall_color(self.look), 0, self.base, W, seed=self.rnd.randrange(99), stripes=h >= 150)
        sets.floor(c, self.base, h, W, vanish=(W / 2, self.base - h * 0.8))

    def in_hand(self, box: Box, pose: str, flip: bool, make, side: str = "right") -> tuple[float, float]:
        """Put something into one hand: `make(x, y, k)` is drawn with its grip at the wrist, `k` being the
        character's height over 100. A thing held is drawn at the hand, never next to it:
        objects meet the characters. It lies over the open hand; for a hand that closes round its handle
        use `hold`."""
        x, y = self.hand(box, pose, flip, side)
        self.put(box.bottom + 0.5, make(x, y, (box.bottom - box.top) / 100), None, group=box.group)
        return x, y

    def mouth(self, box: Box) -> tuple[float, float]:
        """Where a character's mouth is on the page (its module's MOUTH, mirrored with it); for any other
        speaker (a frog, a dog) a point a third of the way down its box."""
        try:
            mod = module(box.name)
        except (KeyError, ValueError, LookupError):
            return (box.left + box.right) / 2, box.top + (box.bottom - box.top) * 0.33
        mx, my = getattr(mod, "MOUTH", (mod.CENTER_X, mod.HEAD_TOP + (mod.FEET_Y - mod.HEAD_TOP) * 0.2))
        k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
        cx = (box.left + box.right) / 2
        dx = (mx - mod.CENTER_X) * k
        return (cx - dx if box.flip else cx + dx), box.bottom - (mod.FEET_Y - my) * k

    def say(self, box: Box, text: str, shout: bool = False, size: float = 13, prefer: str = "") -> bool:
        """A speech bubble for a character, its tail curving down to the mouth; placed beside or above the head
        where nothing else is, inside the strip. A shout is a round puffy cloud. Returns False (and draws
        nothing) when there is no room."""
        words = text.split()
        lines = [text]
        if sets.letter_width(text, size, style="talk") > 210 and len(words) > 1:
            cut = min(range(1, len(words)), key=lambda i: abs(len(" ".join(words[:i])) - len(text) / 2))
            lines = [" ".join(words[:cut]), " ".join(words[cut:])]
        tw = max(sets.letter_width(line, size, style="talk") for line in lines)
        w, h = tw + size * 1.6, len(lines) * size * 1.25 + size * 0.9
        if shout:
            w, h = w + size * 1.2, h + size * 0.8               # the cloud's bumps need room round the words
        hx = (box.left + box.right) / 2
        mx, my = self.mouth(box)
        # spots close to the mouth, so the tail stays short: beside the head first, then above it
        near = 10
        spots = {"side_r": (box.right + near, my - h * 0.85), "side_l": (box.left - near - w, my - h * 0.85),
                 "right": (mx + 6, box.top - h + 6), "left": (mx - 6 - w, box.top - h + 6),
                 "above": (hx - w / 2, box.top - h - 6)}
        if prefer == "right":
            prefer = "side_r"
        elif prefer == "left":
            prefer = "side_l"
        order = ([prefer] if prefer in spots else []) + [k for k in spots if k != prefer]
        for key in order:
            x0, y0 = spots[key]
            rect = (x0, y0, x0 + w, y0 + h)
            if x0 < 6 or x0 + w > W - 6 or y0 < 4 or not self.free(rect, 4):
                continue
            c = Canvas()
            cx, cy = x0 + w / 2, y0 + h / 2
            body = (_cloud_segments(x0, y0, w, h) if shout
                    else _rounded_segments(x0, y0, w, h, min(h / 2, 14)))
            # the tail points from the body's edge toward the mouth and stops short of it
            bx = min(max(mx, x0 + min(18, w * 0.3)), x0 + w - min(18, w * 0.3))
            by = y0 + h - (h * 0.22 if shout else 4)
            if not (y0 + h <= my - 6):                        # beside the head: leave from the near side
                inset = w * 0.2 if shout else 6                  # a cloud's bumps leave its box's corners empty
                bx = x0 + inset if x0 > mx else x0 + w - inset
                by = min(max(my, y0 + h * 0.45), y0 + h - 6)
            dist = math.hypot(mx - bx, my - by) or 1
            reach = max(10.0, dist - 10)                       # stop 10 units short of the mouth
            if y0 + h <= box.top + 4 and my - by > 1:          # from above: stop over the crown, off the face
                reach = min(reach, max(10.0, (box.top - 3 - by) * dist / (my - by)))
            tx, ty = bx + (mx - bx) * reach / dist, by + (my - by) * reach / dist
            spread = min(8.0, w * 0.1, h * 0.28)
            c.path(_bubble_d(body, (tx, ty), spread), P.WHITE, 1.8)    # body and tail: one shape, one outline
            top = cy - (len(lines) - 1) * size * 1.25 / 2 + size * 0.36
            for i, line in enumerate(lines):
                sets.fit_label(c, cx, top + i * size * 1.25, line, size, w - size * (2.2 if shout else 1),
                               style="talk")
            self.put(self.h + 2, c.render(), rect, f"say{len(self.boxes)}", group=box.group)
            return True
        return False

    def relook(self, time: str | None = None, season: str | None = None) -> None:
        """Force the time of day or the season when the story needs it (snow for a snowball fight); the chapter's
        color stays."""
        self.look = replace(self.look, time=time or self.look.time, season=season or self.look.season)

    def hand(self, box: Box, pose: str, flip: bool, side: str = "right") -> tuple[float, float]:
        """Where a character's wrist is on the page (for putting something into its hand).

        A character whose module has `hand_point(pose, side)` says itself where it holds things (the sparrow, at
        a wing's tip); for the others the poses list arms as (elbow, wrist, ...). `side` is the character's own
        right (the near arm) or left."""
        mod = module(box.name)
        if hasattr(mod, "hand_point"):
            wx, wy = mod.hand_point(pose, side)
        else:
            wx, wy = mod.POSES[pose][-1 if side == "right" else -2][1]
        k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
        cx = (box.left + box.right) / 2
        dx = (wx - mod.CENTER_X) * k
        return (cx - dx if flip else cx + dx), box.bottom - (mod.FEET_Y - wy) * k

    def held(self, box: Box, pose: str, flip: bool, make, group: str | None = None) -> tuple[float, float]:
        """Put something into a character's two hands: `make(x, y, k)` is drawn between the wrists, `k` being
        the character's height over 100 (so a thing 20 high at k = 1 is a fifth of the character)."""
        lx, ly = self.hand(box, pose, flip, "left")
        rx, ry = self.hand(box, pose, flip, "right")
        x, y = (lx + rx) / 2, max(ly, ry) + (box.bottom - box.top) * 0.03
        self.put(box.bottom + 0.5, make(x, y, (box.bottom - box.top) / 100), None, group=group or box.group)
        return x, y

    def flight(self, name: str, frac: float, height: float, pose: str = "fly", mood: str = "smile") -> Box:
        """A character in the air (the sparrow flying), `height` above the ground line, as a fraction of the sky."""
        x = self.x(frac)
        feet = self.base - (self.base - self.tall * 0.4) * height
        return self.actor(name, x, feet, pose, mood, flip=x > W / 2, tall=self.tall)


def footer_conflicts(s: Strip) -> list[str]:
    return conflicts(s, air=3)


# ============================================================================ which footer for which page
def _stable(text: str) -> int:
    return zlib.crc32(text.encode("utf-8"))


UNSET = "courtyard"     # the world of a chapter of the main matter that has no `world:` yet: the introduction's


def _chapter_index(chapter: str) -> int:
    """A number for the chapter that does not depend on what else is built (so `--only` matches)."""
    return int(chapter) if str(chapter).isdigit() else _stable(str(chapter)) % 97


def footers(requests: list[dict], vocabulary: dict, trace: list | None = None) -> list[str]:
    """The SVG of every footer, in the order of the requests. A chapter living in a world (`world:`) gets the
    camera along its machine (`worlds.py`), and so does a chapter of the main matter not given a world yet, in the
    introduction's courtyard (`UNSET`); the front pages and the contents get the professor's courtyard (the world
    `front`), each page its own moment (`world_courtyard.front_place`). `trace`, when given, is filled with what each
    footer shows and the strip it was drawn on, in the order of the requests (`worlds.moment`), for `book audit`."""
    from .worlds import WORLDS, frame, moment, world_footers      # first: it loads every world in order
    from .world_courtyard import FRONT, front_place

    moments: list[dict | None] = [None] * len(requests)
    out: list[str | None] = [None] * len(requests)
    in_world: dict[str, list[int]] = {}
    front: list[int] = []                                # the front pages and the contents: the courtyard
    for i, request in enumerate(requests):
        chapter = str(request.get("chapter", ""))
        name = str(request.get("world") or "") or (UNSET if chapter.isdigit() else "")
        if not name:
            front.append(i)
            continue
        if name not in WORLDS:
            raise ValueError(f"no world {name!r}; available: {', '.join(WORLDS)}")
        in_world.setdefault(f"{chapter}\0{name}", []).append(i)
    for key, indexes in in_world.items():
        chapter, name = key.split("\0")
        shown: list[dict] = []
        for i, svg in zip(indexes, world_footers(WORLDS[name], [requests[i] for i in indexes], vocabulary,
                                                 _chapter_index(chapter), shown), strict=True):
            out[i] = svg
        for i, what in zip(indexes, shown, strict=True):
            moments[i] = what
    words = (vocabulary.get("worlds") or {}).get("front") or {}
    seen: dict[str, int] = {}                            # each page's place in its own front chapter
    for nth, i in enumerate(front):
        request = dict(requests[i])
        chapter = str(request.get("chapter", ""))
        request["nth_in_chapter"] = seen.get(chapter, 0)
        seen[chapter] = seen.get(chapter, 0) + 1
        h = round(float(request["mm"]) * P.SCENE_UNITS_PER_PAGE_MM)
        place = front_place(request, words, nth)
        out[i], strip = frame(FRONT, h, place, request.get("clear"), 0, str(request.get("accent") or P.YELLOW),
                              words, seed=nth)
        moments[i] = moment(FRONT, place, strip)
    if trace is not None:
        trace.extend(moments)
    return [svg or "" for svg in out]

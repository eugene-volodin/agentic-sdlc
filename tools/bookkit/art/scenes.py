"""Illustrated scenes: a meadow, a path, a pond, a room and a study with the computer.

One function draws everything from the narrow strip at the foot of a page to
the full illustration of a chapter opener: the height is a parameter, and the
content (plants, furniture, clouds, cast) is chosen from a seed. Every page
therefore gets its own picture while the build stays reproducible.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from . import props
from .characters import MARKS, draw, module, resolve
from .ink import Canvas, n

WIDTH = P.SCENE_WIDTH  # scene width in drawing units
SCENE_KINDS = ("meadow", "path", "pond", "room", "study")
PROFESSOR_HEIGHT = 426  # canvas units from his feet to the top of his head: the yardstick for everyone

GRASS = P.GRASS
GRASS_DARK = P.GRASS_DARK
SAND = P.SAND
WATER = P.WATER
FLOOR = P.FLOOR

# Footer storylines, cycled by page: little episodes of the characters working with the Agent.
# A cast member is (character, pose, mood, mark); a mark is a badge over the head: "?", "!", "ok", "idea".
# `prop` puts a story object between the first two characters: (kind, label).
STORIES = (
    {"kind": "meadow", "prop": ("board", "AGENTS.md"),      # the professor briefs the newcomer
     "cast": (("professor", "read", "talk", None), ("agent", "stand", "smile", "!"))},
    {"kind": "study",                                       # pair programming at the old computer
     "cast": (("professor", "sit", "talk", None), ("agent", "point", "smile", None), ("cat", "sit", "smile", None))},
    {"kind": "path",                                        # the agent carries files, the sparrow scouts ahead
     "cast": (("agent", "carry", "smile", None), ("sparrow", "walk", "smile", None))},
    {"kind": "meadow", "prop": ("crate", "MCP"),            # plugging into an outside tool
     "cast": (("agent", "point", "talk", None), ("caterpillar", "write", "smile", None))},
    {"kind": "meadow",                                      # a vague instruction gets a puzzled robot
     "cast": (("professor", "explain", "talk", "!"), ("agent", "shrug", "worry", "?"))},
    {"kind": "room", "prop": ("crate", "skills"),           # picking a skill off the shelf
     "cast": (("agent", "read", "smile", None), ("cat", "point", "talk", None))},
    {"kind": "path", "prop": ("gate", "hook"),              # a hook stops the agent in its tracks
     "cast": (("agent", "walk", "surprise", "!"), ("sparrow", "point", "talk", None))},
    {"kind": "pond",                                        # thinking it over together
     "cast": (("caterpillar", "think", "talk", "?"), ("agent", "think", "wink", "idea"))},
    {"kind": "study",                                       # the cat dictates, the agent types
     "cast": (("cat", "sit", "talk", None), ("agent", "type", "smile", None))},
    {"kind": "meadow",                                      # tests are green
     "cast": (("professor", "thumb", "wink", None), ("agent", "cheer", "smile", "ok"),
              ("cat", "cheer", "talk", None), ("sparrow", "cheer", "smile", None))},
    {"kind": "path",                                        # off to the next chapter
     "cast": (("cat", "walk", "smile", None), ("agent", "walk", "smile", None), ("sparrow", "fly", "talk", None))},
    {"kind": "room", "prop": ("board", "TODO"),             # the caterpillar reviews the checklist
     "cast": (("caterpillar", "write", "smile", None), ("agent", "present", "talk", "ok"))},
)
STORY_PROPS = {"board": props.board, "crate": props.crate, "gate": props.gate}
STORY_PROP_SPAN = {"board": (-36, 36), "crate": (-34, 34), "gate": (-22, 80)}   # left and right edge, drawing units


def actor(name: str, x: float, feet_y: float, height: float, pose: str | None = None,
          mood: str = "smile", flip: bool = False, shadow: bool = True, **options) -> str:
    """Stand a character with its feet at (x, feet_y).

    `height` is how tall the professor would be in scene units; the other
    characters are scaled in proportion to him.
    """
    name = resolve(name)
    mod = module(name)
    k = height / PROFESSOR_HEIGHT * mod.SCENE_SCALE
    c = Canvas()
    if shadow and pose != "fly":
        c.ground_shadow(x, feet_y + 2 * k, 62 * k, 6 * k, seed=int(x))
    centre = mod.CENTER_X
    sx = -k if flip else k
    tx = x + centre * k if flip else x - centre * k
    lift = 26 * k if pose == "fly" else 0
    c.place(draw(name, pose, mood, **options), f"translate({n(tx)},{n(feet_y - mod.FEET_Y * k - lift)}) "
        f"scale({n(sx)},{n(k)})")
    return c.render()


def parse_cast(cast) -> list[tuple]:
    """Normalize a cast: `"cat:wave:talk:?, sparrow"` or a list of tuples/strings.

    Each member becomes `(character, pose, mood, mark)`.
    """
    if not cast:
        return []
    if isinstance(cast, str):
        cast = [part for part in cast.replace(";", ",").split(",") if part.strip()]
    result = []
    for member in cast:
        if isinstance(member, str):
            bits = [bit.strip() for bit in member.split(":")]
            member = (bits[0], bits[1] if len(bits) > 1 and bits[1] else None,
                      bits[2] if len(bits) > 2 and bits[2] else "smile", bits[3] if len(bits) > 3 else None)
        mark = member[3] if len(member) > 3 else None
        if mark and mark not in MARKS:
            raise ValueError(f"unknown mark {mark!r}; available: {', '.join(MARKS)}")
        result.append((resolve(member[0]), member[1], member[2] or "smile", mark or None))
    return result


class _Scene:
    """Working state while one scene is composed."""

    def __init__(self, h: int, seed: int, kind: str, clear: str | None, sky: bool) -> None:
        self.h, self.kind, self.sky = h, kind, sky
        self.rnd = random.Random(seed * 7919 + h)
        self.seed = seed
        self.ground = max(42, min(h * 0.30, 100))           # thickness of the ground band
        self.base = h - self.ground                          # y of the horizon line
        self.tall = min(h * 0.74, 290) if h < 400 else min(h * 0.62, 340)  # professor's height
        # In a low footer the professor would be taller than the sky above the ground and his head would stick out
        # of the painted part of the picture, up into the text: keep the head well inside.
        self.tall = min(self.tall, self.base * 0.86)
        self.unit = self.tall / 137                          # scale for outdoor props
        self.lo = 150 if clear == "left" else 40             # keep clear of the page number tag
        self.hi = WIDTH - 150 if clear == "right" else WIDTH - 40
        self.indoor = kind in ("room", "study")
        self.phase = self.rnd.random() * math.tau
        self.amp = 0 if self.indoor else min(11, h * 0.05)
        self.back = Canvas()                                 # sky, wall, distant things
        self.items: list[tuple[float, str]] = []             # (depth, svg) sorted before drawing
        self.taken: list[tuple[float, float]] = []           # (x, half-width) of placed actors
        self.desk_right: bool | None = None                  # where the study desk stands, if any
        self.speaker: float | None = None                    # x of whoever speaks from a bubble above the scene
        self.cast_x: list[float] = []                        # where the cast stands

    def ground_y(self, x: float) -> float:
        return self.base + self.amp * math.sin(x / WIDTH * math.pi * 2.2 + self.phase)

    def is_free(self, x: float, radius: float = 30) -> bool:
        return all(abs(x - tx) > radius + half for tx, half in self.taken)

    def nearest_free(self, x: float, half: float, spans: list[tuple[float, float]], lo: float, hi: float,
                     gap: float = 10) -> float | None:
        """The x nearest to `x` where an object `half` wide on each side clears every (left, right) span by `gap`
        and stays within [lo, hi]; None when there is no such place."""
        lo, hi = lo + half, hi - half
        if lo > hi:
            return None
        candidates = [min(max(x, lo), hi)]
        for left, right in spans:
            candidates += [left - gap - half, right + gap + half]
        fits = [c for c in candidates if lo <= c <= hi
                and all(c + half + gap <= left or c - half - gap >= right for left, right in spans)]
        return min(fits, key=lambda c: abs(c - x)) if fits else None

    def put(self, depth: float, fragment: str) -> None:
        self.items.append((depth, fragment))

    def scatter(self, count: int, radius: float, make) -> None:
        """Place up to `count` props at random free spots; `make(x, y)` returns the SVG.

        `radius` is the half-width of the prop: spots are kept that far from both edges, so nothing scattered is ever
        cut off by the frame, and that far from everything already standing, so no two things in a scene overlap.
        """
        lo, hi = max(self.lo, radius + 4), min(self.hi, WIDTH - radius - 4)
        for _ in range(count):
            if lo >= hi:
                return
            x = self.rnd.uniform(lo, hi)
            if self.is_free(x, radius):
                y = self.ground_y(x) + self.rnd.uniform(4, self.ground * 0.28)
                self.put(y, make(x, y))
                self.taken.append((x, radius))   # nothing else lands on it


def _outdoor_backdrop(s: _Scene) -> None:
    c, h, rnd = s.back, s.h, s.rnd
    if s.sky:
        c.fade(0, 0, WIDTH, s.base + 10, [(0, P.SKY, 0), (0.55, P.SKY, 0.55), (1, P.SKY_LOW, 0.95)])
    if h >= 190:
        scale = min(1.35, h / 300)
        # Everything in the sky keeps its full outline inside the picture.
        # Nothing in the sky sits between a speaker and the bubble above them, and no two things overlap there.
        sky: list[tuple[float, float]] = [] if s.speaker is None else [(s.speaker - 110, s.speaker + 110)]
        if s.base - s.tall < h * 0.30 + 60:   # heads (and the badges over them) reach up into the clouds
            sky += [(x - s.tall * 0.22, x + s.tall * 0.22) for x in s.cast_x]
        sun_x = s.nearest_free(rnd.choice((118, WIDTH - 128)), 60 * scale, sky, 0, WIDTH)
        if sun_x is not None:
            c.add(props.sun(sun_x, max(46 * scale, h * 0.17), scale))
            sky.append((sun_x - 60 * scale, sun_x + 60 * scale))
        for _ in range(2 if h < 300 else 3):
            size = rnd.uniform(0.8, 1.3)
            top = 44 * size + 4
            x = s.nearest_free(rnd.uniform(170, WIDTH - 170), 70 * size, sky, 100, WIDTH - 100)
            if x is not None:
                c.add(props.cloud(x, rnd.uniform(top, max(top + 1, h * 0.30)), size))
                sky.append((x - 70 * size, x + 70 * size))
        for _ in range(3):
            x = s.nearest_free(rnd.uniform(120, WIDTH - 120), 12, sky, 100, WIDTH - 100)
            if x is not None:
                c.add(props.bird(x, rnd.uniform(30, h * 0.34), rnd.uniform(0.7, 1.1)))
                sky.append((x - 12, x + 12))
        # Two ranges of distant hills, paler with distance, dotted with tiny firs.
        far = s.base - h * 0.13
        # The hills run past both edges, so neither their outline nor their shaded side shows as a seam.
        c.shape(f"M-14,{n(s.base + 6)} L-14,{n(far + 18)} Q{WIDTH * .2},{n(far - 30)} {WIDTH * .42},{n(far + 6)} "
                f"Q{WIDTH * .7},{n(far - 44)} {WIDTH + 14},{n(far + 2)} L{WIDTH + 14},{n(s.base + 6)} Z",
                P.HILL_FAR, sw=2, light=(-8, -5), shade_k=0.93)
        firs: list[float] = []
        for _ in range(5):
            x = rnd.uniform(40, WIDTH - 40)
            if all(abs(x - other) > 40 for other in firs):   # far-off firs stand apart too
                firs.append(x)
                c.add(props.tree(x, far + 6 + 8 * math.sin(x / 90), s.unit * 0.22, "fir"))
        near = s.base - h * 0.045
        c.shape(f"M-14,{n(s.base + 6)} L-14,{n(near)} Q{WIDTH * .3},{n(near - 26)} {WIDTH * .55},{n(near + 4)} "
                f"Q{WIDTH * .8},{n(near - 18)} {WIDTH + 14},{n(near + 8)} L{WIDTH + 14},{n(s.base + 6)} Z",
                P.HILL_NEAR, sw=2, light=(-8, -5), shade_k=0.93)
    else:
        c.add(props.cloud(rnd.uniform(200, WIDTH - 200), 30, 0.58))
        c.add(props.bird(rnd.uniform(120, WIDTH - 120), 20, 0.7))


def _outdoor_ground(s: _Scene) -> None:
    c, h, rnd, g = s.back, s.h, s.rnd, s.ground
    points = [(x, s.ground_y(x)) for x in range(0, WIDTH + 1, 60)]
    top = " ".join(f"L{x},{n(y)}" for x, y in points[1:])
    paint = c.gradient([(0, GRASS), (1, GRASS_DARK)], 0, s.base - 10, 0, h)
    c.path(f"M0,{h + 4} L0,{n(points[0][1])} {top} L{WIDTH},{h + 4} Z", paint, 2.5)
    c.dots(None, 0, s.base - 6, WIDTH, g * 0.5, int(90 + h / 4), "top", seed=s.seed, opacity=0.4)
    if s.kind in ("path", "pond"):
        t0, t1 = g * 0.36, g * 0.74
        upper = " ".join(f"L{x},{n(y + t0 + 3 * math.sin(x / 70))}" for x, y in points[1:])
        lower = " ".join(f"L{x},{n(y + t1 + 3 * math.cos(x / 90))}" for x, y in reversed(points[:-1]))
        c.path(f"M0,{n(points[0][1] + t0)} {upper} L{WIDTH},{n(points[-1][1] + t1)} {lower} Z", SAND, 2.1)
        c.dots(None, 0, s.base + t0 + 4, WIDTH, t1 - t0 - 4, 170, "even", seed=s.seed + 1, opacity=0.55)
        for _ in range(7):  # pebbles
            x = rnd.uniform(20, WIDTH - 20)
            y = s.ground_y(x) + rnd.uniform(t0 + 5, t1 - 3)
            c.add(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(rnd.uniform(3, 5))}" ry="2.200" fill="{P.PEBBLE}" '
                  f'stroke="{P.INK}" stroke-width="1.200"/>')
    if s.kind == "pond":
        left_room, right_room = (min(t[0] for t in s.taken) - s.lo, s.hi - max(t[0] for t in s.taken)) \
            if s.taken else (s.hi - s.lo, 0)
        x = s.lo + left_room * 0.45 if left_room > right_room else s.hi - right_room * 0.45
        y = s.base + g * 0.2
        rx = min(72 * min(1.7, h / 136), max(left_room, right_room) * 0.36)
        water = c.gradient([(0, P.WATER_LIGHT), (1, WATER)], 0, y - g * 0.17, 0, y + g * 0.17)
        c.path(f"M{n(x - rx)},{n(y)} A{n(rx)},{n(g * 0.17)} 0 1 0 {n(x + rx)},{n(y)} "
               f"A{n(rx)},{n(g * 0.17)} 0 1 0 {n(x - rx)},{n(y)} Z", water, 2.3)
        c.line(f"M{n(x - 34)},{n(y)} q9,-4 18,0 M{n(x + 8)},{n(y + 4)} q9,-4 18,0 M{n(x - 6)},{n(y - 5)} q7,-3 14,0",
               1.4, P.WHITE)
        s.put(y + 2, props.reeds(x - rx * 0.86, y + 3, s.unit * 0.9))
        s.put(y + 2, props.reeds(x + rx * 0.9, y + 1, s.unit * 0.7))
        s.taken.append((x, rx))


def _outdoor_props(s: _Scene) -> None:
    rnd, unit, g = s.rnd, s.unit, s.ground
    k = min(1.5, max(0.8, s.h / 200))
    if s.h >= 190:
        kinds = ["oak", "birch", "fir", "oak"]
        for _ in range(1 if s.h < 300 else 2):
            # Keep the whole crown inside the picture, top and sides.
            size = min(unit * rnd.uniform(0.95, 1.2), (s.base - 8) / 180)
            reach = 84 * size
            if reach + 4 >= WIDTH - reach - 4:
                continue
            x = rnd.uniform(max(s.lo, reach + 4), min(s.hi, WIDTH - reach - 4))
            if s.is_free(x, reach):   # the whole crown clears the cast and the other tree
                s.put(s.ground_y(x) - 2, props.tree(x, s.ground_y(x) + 3, size, rnd.choice(kinds)))
                s.taken.append((x, reach))
    for _ in range(int(18 + s.h / 22)):
        x = rnd.uniform(6, WIDTH - 6)
        y = s.ground_y(x) + rnd.uniform(5, g * 0.92)
        s.put(y - 30, props.tuft(x, y, rnd.uniform(0.7, 1.15) * k))
    palette = (P.WHITE, P.WHITE, P.PINK_PALE, P.YELLOW_PALE)
    s.scatter(rnd.randint(3, 6), 26, lambda x, y: props.daisy(x, y, k * rnd.uniform(0.8, 1.1), rnd.choice(palette)))
    s.scatter(rnd.randint(1, 3), 26, lambda x, y: props.tulip(x, y, k * rnd.uniform(0.8, 1.0),
                                                              rnd.choice((P.RED, P.YELLOW, P.PINK))))
    s.scatter(rnd.randint(1, 3), 34, lambda x, y: props.mushroom(
        x, y, k * rnd.uniform(0.7, 1.0), *rnd.choice(((P.RED, True), (P.TRUNK, False)))))
    for maker in rnd.sample([props.stump, props.stone, props.bush, props.stone, props.fence], 2):
        if maker is props.bush:
            s.scatter(1, 50 * k, lambda x, y: props.bush(x, y, k * rnd.uniform(0.8, 1.0), rnd.random() < 0.5))
        elif maker is props.fence:
            s.scatter(1, 70 * k, lambda x, y: props.fence(x - 40 * k, s.ground_y(x) + 6, k * 0.9, rnd.randint(4, 7)))
        else:
            s.scatter(1, 30 * k, lambda x, y, make=maker: make(x, y, k * rnd.uniform(0.8, 1.0)))
    if rnd.random() < 0.6:
        s.back.add(props.butterfly(rnd.uniform(s.lo, s.hi), s.base - rnd.uniform(18, 40), k * 0.8,
                                   rnd.choice((P.YELLOW, P.PINK, P.WHITE))))
    for _ in range(4):  # leafy clumps at the very front
        x = rnd.uniform(10, WIDTH - 10)
        s.put(s.h + 10, props.grass_clump(x, s.h + 3, k * rnd.uniform(0.9, 1.3)))


def _indoor(s: _Scene, people: list[tuple], xs: list[float] | None = None) -> None:
    """Draw the room and seat whoever asked to sit; they are removed from `people`.

    Nothing in the room overlaps anything else: the desk and the chair (or the plant) take
    their place first, the bookcase stands at the far wall only when it leaves room for whoever stands, and the window
    and the picture hang where the wall is free. Whatever finds no room is left out.
    """
    c, h, rnd, base = s.back, s.h, s.rnd, s.base
    placed = bool(xs)
    furniture = s.tall * 0.0049   # desk top lands just under the seated professor's hands
    if s.sky:
        c.fade(0, 0, WIDTH, base, [(0, P.WALL, 0), (0.5, P.WALL, 0.5), (1, P.WALL, 0.9)])
    # Floor boards receding to the wall, then the skirting board.
    paint = c.gradient([(0, FLOOR), (1, P.FLOOR_DARK)], 0, base, 0, h)
    c.path(f"M-4,{n(base)} H{WIDTH + 4} V{h + 4} H-4 Z", paint, 2.4)
    for i in range(-3, 16):
        x0 = i * 76 + (s.seed * 13) % 60
        c.line(f"M{x0},{n(base)} L{x0 - 58},{h}", 1.1, opacity=0.7)
    c.line(f"M0,{n(base + s.ground * 0.42)} H{WIDTH}", 1.1, opacity=0.7)
    c.dots(None, 0, base, WIDTH, s.ground * 0.4, 80, "top", seed=s.seed, opacity=0.35)
    c.shape(f"M-4,{n(base - 11 * furniture * 1.2)} H{WIDTH + 4} V{n(base)} H-4 Z", P.TERRACOTTA, sw=2.2, light=None)
    floor = base + min(16, s.ground * 0.32)
    desk_right = rnd.random() < 0.5
    covered: list[tuple[float, float]] = []            # spans of the wall hidden by tall things, (left, right)
    if s.speaker is not None:                          # the wall behind a speaker stays plain, so the bubble reads
        covered.append((s.speaker - 90, s.speaker + 90))
    if s.kind == "study":
        s.desk_right = desk_right
        direction = 1 if desk_right else -1
        desk_x = (s.hi - 118 * furniture) if desk_right else (s.lo + 118 * furniture)
        desk_top = floor - 71 * furniture
        chair_x = desk_x - direction * 172 * furniture
        seated = [p for p in people if p[1] == "sit"]
        on_chair = next((p for p in seated if getattr(module(p[0]), "SEAT", "") == "chair"), None)
        on_desk = next((p for p in seated if getattr(module(p[0]), "SEAT", "") == "desk"), None)
        # The chair is drawn only when the cast stands where the scene chose (it keeps clear of the chair) or
        # someone sits on it: with positions given from outside, a standing character could end up in front of
        # an empty chair, which reads as clutter.
        if on_chair or not placed:
            s.put(floor - 4, props.chair(chair_x, floor, s.tall * 0.0033, mirror=not desk_right))
        if on_chair:
            s.put(floor - 3, actor(on_chair[0], chair_x + direction * 4 * furniture, floor, s.tall, "sit",
                                   on_chair[2], flip=not desk_right, shadow=False))
            people.remove(on_chair)
            covered.append((chair_x - s.tall * 0.2, chair_x + s.tall * 0.2))   # nothing hangs behind a head
        s.put(floor - 2, props.desk(desk_x, floor, furniture, width=214, depth=18))
        monitor_x = desk_x - direction * 46 * furniture
        s.put(floor - 1, props.computer(monitor_x, desk_top - 13 * furniture, furniture, lines=3 + s.seed % 2,
                                        keyboard=False)
              + props.keyboard(monitor_x, desk_top - 2 * furniture, furniture))
        covered.append((monitor_x - 50 * furniture, monitor_x + 50 * furniture))
        if on_desk:  # the cat perches on the desk edge beside the monitor, legs dangling
            k = s.tall / PROFESSOR_HEIGHT * module(on_desk[0]).SCENE_SCALE
            cat_x = desk_x + direction * 62 * furniture
            s.put(floor, actor(on_desk[0], cat_x, desk_top - 9 * furniture + 50 * k,
                               s.tall, "sit", on_desk[2], flip=desk_right, shadow=False))
            covered.append((cat_x - 60 * k, cat_x + 60 * k))
            people.remove(on_desk)
        s.taken.append((desk_x - direction * 44 * furniture, 172 * furniture))
    else:
        plant_x = (s.hi - 40 * furniture) if desk_right else (s.lo + 40 * furniture)
        if not placed or all(abs(x - plant_x) >= 52 * furniture + s.tall * 0.16 for x in xs[:len(people)]):
            s.put(floor - 6, props.plant(plant_x, floor - 2, furniture * 1.5))
            s.taken.append((plant_x, 30 * furniture))
            covered.append((plant_x - 52 * furniture, plant_x + 52 * furniture))
        s.put(base + 1, props.rug(WIDTH / 2, floor + s.ground * 0.16, min(1.6, s.tall / 150)))
    # The bookcase goes to the far wall, but only if whoever stands still has room in front of the wall.
    shelf_half = 54 * furniture
    shelf_x = s.lo + shelf_half + 6 if desk_right else s.hi - shelf_half - 6
    standing = len(people)
    person = s.tall * 0.16
    if placed:
        room = all(abs(x - shelf_x) >= shelf_half + person for x in xs[:len(people)])
    else:
        if desk_right:
            edge = min([t[0] - t[1] for t in s.taken] + [s.hi]) - (shelf_x + shelf_half)
        else:
            edge = (shelf_x - shelf_half) - max([t[0] + t[1] for t in s.taken] + [s.lo])
        room = edge >= standing * s.tall * 0.46 + s.tall * (0.30 if standing else 0)
    if room:
        shelves = max(2, min(5, int(((base - 8) / furniture - 8) // 50)))
        c.add(props.bookshelf(shelf_x, base + 2, furniture, s.seed, shelves=shelves))
        s.taken.append((shelf_x, shelf_half + 6))
        covered.append((shelf_x - shelf_half, shelf_x + shelf_half))
    # Wall furniture is sized to fit under the top edge and hung where the wall is free: nothing is ever cut off,
    # nothing hides behind anything else.
    wall = base - 14 * furniture                       # free wall above the skirting board
    window_scale = min(furniture * 1.25, (wall - 10) / 112)
    if window_scale >= furniture * 0.7:
        x = s.nearest_free(WIDTH * (0.40 if desk_right else 0.60), 62 * window_scale, covered, 0, WIDTH, 14)
        if x is not None:
            c.add(props.window(x, 6 + 60 * window_scale, window_scale))
            covered.append((x - 62 * window_scale, x + 62 * window_scale))
    picture_scale = min(furniture * 1.2, (wall - 10) / 66)
    if picture_scale >= furniture * 0.6:
        x = s.nearest_free(WIDTH * (0.62 if desk_right else 0.38), 34 * picture_scale, covered, 0, WIDTH, 14)
        if x is not None:
            c.add(props.picture(x, 6 + 38 * picture_scale + wall * 0.08, picture_scale, s.seed))
    # Anyone still asking to sit has nothing to sit on: let them stand.
    for i, (name, pose, mood, badge) in enumerate(people):
        if pose == "sit":
            people[i] = (name, "stand", mood, badge)


def scene(h: int = 136, seed: int = 0, kind: str | None = None, cast=None, sign: str | None = None,
          clear: str | None = None, xs: list[float] | None = None, sign_x: float | None = None,
          sky: bool = True, prop: tuple[str, str] | None = None, speaker: int | None = None) -> str:
    """Draw a scene 840 units wide and `h` units tall and return it as `<svg>`.

    kind   meadow | path | pond | room | study; when omitted, the story's own setting
    cast   who is in the picture: `"cat:wave:talk, agent:shrug:worry:?"` or a list of tuples;
           `None` plays one of the footer `STORIES` chosen by the seed, an empty cast leaves the scene empty
    prop   a story object placed after the first character: `("board" | "crate" | "gate", label)`;
           ignored when positions are given with `xs`
    sign   text for a wooden signpost (outdoor scenes)
    clear  'left' | 'right': keep that end free for the page number tag
    xs     explicit x positions for the cast, in order
    sky    paint the sky or wall tint; turn off on colored backgrounds
    speaker index in the cast of whoever speaks from a bubble above: the sky over them stays empty

    The picture is composed to fit: the caller must show it in a box of the same proportions
    (840 : h), which the design tokens guarantee for footers, insets, the cover and openers.
    """
    story = STORIES[seed % len(STORIES)] if cast is None else {}
    if cast is None and kind and kind != story["kind"]:   # a forced setting: take the first story that suits it
        story = next((st for st in STORIES if st["kind"] == kind), {**story, "prop": None})
    kind = kind or story.get("kind") or SCENE_KINDS[seed % len(SCENE_KINDS)]
    if kind not in SCENE_KINDS:
        raise ValueError(f"unknown scene kind {kind!r}; available: {', '.join(SCENE_KINDS)}")
    s = _Scene(h, seed, kind, clear, sky)
    people = parse_cast(story["cast"] if cast is None else cast)
    story_prop = story.get("prop") if prop is None else prop
    if story_prop and story_prop[0] not in STORY_PROPS:
        raise ValueError(f"unknown prop {story_prop[0]!r}; available: {', '.join(STORY_PROPS)}")
    if xs and len(xs) < len(people):
        raise ValueError(f"{len(people)} characters need {len(people)} positions, got {len(xs)}")
    if not s.indoor:
        people = [(name, "stand" if pose == "sit" else pose, mood, badge) for name, pose, mood, badge in people]

    if xs and speaker is not None and speaker < len(xs):
        s.speaker = xs[speaker]
    if s.indoor:
        _indoor(s, people, xs)
    # Spread the standing cast across the free width.
    count = len(people)
    slots = count + (1 if story_prop and count else 0)   # the story prop takes a place in the line-up
    feet_offset = min(15, s.ground * 0.3)
    positions: list[float] = []
    prop_x: float | None = None
    if xs:
        positions = list(xs)[:count]
    elif count:
        lo, hi = s.lo, s.hi
        if s.indoor:  # furniture occupies one or both ends of the room
            lo = max([lo] + [t[0] + t[1] for t in s.taken if t[0] < WIDTH / 2])
            hi = min([hi] + [t[0] - t[1] for t in s.taken if t[0] >= WIDTH / 2])
        margin = s.tall * (0.30 if s.indoor else 0.18)
        span = hi - lo - 2 * margin
        gap = max(min(span / max(slots, 1), s.tall * 0.62), s.tall * 0.46)   # room for outstretched arms
        start = lo + margin + s.rnd.uniform(0, max(1.0, span - gap * (slots - 1)))
        if s.desk_right is not None:   # in the study everyone gathers by the computer
            gap = min(gap, s.tall * 0.46)
            aside = s.tall * 0.3   # stand clear of the chair
            start = hi - aside - gap * (slots - 1) if s.desk_right else lo + aside
        positions = [start + i * gap for i in range(slots)]
        if slots > count:
            prop_x = positions.pop(1)
    for x in positions:
        s.taken.append((x, s.tall * 0.16))
    s.cast_x = list(positions)
    if speaker is not None and speaker < len(positions):
        s.speaker = positions[speaker]
    # The story prop and the signpost claim their ground before anything is scattered around them.
    prop_scale = s.tall / 137 * 1.15
    if prop_x is not None:
        left, right = STORY_PROP_SPAN[story_prop[0]]
        s.taken.append((prop_x + (left + right) / 2 * prop_scale, (right - left) / 2 * prop_scale + 6))
    sign_at = None
    if sign and not s.indoor:
        mean = sum(positions) / len(positions) if positions else 0
        sign_at = sign_x if sign_x is not None else (s.hi - 160 if mean < WIDTH / 2 else s.lo + 30)
        sign_scale = min(1.5, max(0.9, h / 190))
        reach = (max(66, 12.5 * len(sign) + 30) + 18) * sign_scale
        s.taken.append((sign_at + reach / 2, reach / 2 + 6))

    if not s.indoor:
        _outdoor_backdrop(s)
        _outdoor_ground(s)
        _outdoor_props(s)
        if sign_at is not None:
            y = s.ground_y(sign_at) + feet_offset
            s.put(y - 1, props.signpost(sign_at, y, sign, sign_scale))

    if prop_x is not None:
        feet = (s.base if s.indoor else s.ground_y(prop_x)) + feet_offset
        make = STORY_PROPS[story_prop[0]]
        extra = {"seed": s.seed} if make is props.crate else {}
        s.put(feet - 2, make(prop_x, feet, story_prop[1], prop_scale, **extra))

    for (name, pose, mood, badge), x in zip(people, positions, strict=True):
        feet = (s.base if s.indoor else s.ground_y(x)) + feet_offset
        flip = x > WIDTH / 2 if s.desk_right is None else not s.desk_right   # face the desk in the study
        s.put(feet, actor(name, x, feet, s.tall, pose, mood, flip=flip))
        mod = module(name)
        k = s.tall / PROFESSOR_HEIGHT * mod.SCENE_SCALE
        crown = feet - (mod.FEET_Y - mod.HEAD_TOP) * k
        if badge:
            # Over the head when there is room, otherwise beside it, so the badge is never cut off.
            size = min(1.5, max(0.7, s.tall / 150))
            radius = 17 * size
            above = crown - radius - 3
            if above >= radius + 2:
                s.put(h + 20, props.mark(x, above, badge, size))
            else:   # beside the head, on the side away from the nearest neighbour
                others = [other for other in positions if other != x]
                nearest = min(others, key=lambda other: abs(other - x)) if others else x + (1 if flip else -1)
                side = -1 if nearest > x else 1
                s.put(h + 20, props.mark(x + side * (70 * k + radius), max(radius + 3, crown + radius), badge, size))
        grips = getattr(mod, "BALLOON_GRIP", {})
        if pose in grips and h >= 130 and not s.indoor:
            side = -1 if flip else 1
            tip_x, tip_y = grips[pose]                 # the string ends exactly in the wing
            hold_x = x + side * (tip_x - mod.CENTER_X) * k
            hold_y = feet - (mod.FEET_Y - tip_y) * k
            length = min(s.tall * 0.36, hold_y - 58)   # keep the whole balloon in the picture
            if length > 14:
                color = s.rnd.choice((P.RED, P.BLUE, P.VIOLET))   # never a color a backdrop can have
                s.put(feet + 1, props.balloon(hold_x, hold_y, length, color))

    body = s.back.render() + "".join(fragment for _, fragment in sorted(s.items, key=lambda item: item[0]))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {h}" class="scene-svg" '
            f'preserveAspectRatio="xMidYMax slice" aria-hidden="true">{body}</svg>')

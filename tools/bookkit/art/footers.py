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

import zlib
from dataclasses import dataclass

from .. import design as P
from ..design import lighten, mix
from . import props
from .characters import module
from .openers import W, Box, Stage, conflicts

TAG = 100            # how far in from the edge the page-number tag reaches, in units
TAG_HEIGHT = 80      # and how high up from the bottom
TALL_MAX = 165       # the professor's height in a footer never grows beyond this


# ============================================================================ the look of a chapter
@dataclass(frozen=True)
class Look:
    """Time of day, season and the chapter's color of a chapter's footers.

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


def wall_color(look: Look) -> str:
    """A room's wall: the paper tinted with the chapter's color."""
    return mix(lighten(look.accent, 0.7), P.PAPER, 0.25)


# ============================================================================ the strip
class Strip(Stage):
    """A footer being composed: `h` units tall, the page-number tag held clear at one corner."""

    def __init__(self, h: float, seed: int, clear: str | None, look: Look, words: dict | None = None) -> None:
        tag = (0, h - TAG_HEIGHT, TAG, h) if clear == "left" else (W - TAG, h - TAG_HEIGHT, W, h)
        super().__init__(seed, words=words, height=h, reserved=[tag] if clear else [])
        self.look = look
        self.clear = clear
        self.seed = seed
        self.ground = max(42, min(h * 0.30, 110))                 # thickness of the ground band
        self.base = h - self.ground                               # the horizon line
        tall = min(h * 0.74, 290) if h < 400 else min(h * 0.62, 340)
        # How tall the professor would be: capped, so the cast keeps the same size from the 55 mm strip up and a
        # panorama gets more of the world above it.
        self.tall = min(tall, self.base * 0.86, TALL_MAX)
        self.unit = self.tall / 137                               # scale of props drawn for a 137-unit professor
        self.lo = TAG + 14 if clear == "left" else 30
        self.hi = W - TAG - 14 if clear == "right" else W - 30

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

    def svg(self, css_class: str, align: str = "xMidYMid", marks: bool = True) -> str:
        """The strip as `<svg>`: the backdrop (sky, wall, whatever the frame painted behind) is veiled so that
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

    def mouth(self, box: Box) -> tuple[float, float]:
        """Where a character's mouth is on the page (its module's MOUTH, mirrored with it); for any other
        speaker (a bird, a robot arm) a point a third of the way down its box."""
        try:
            mod = module(box.name)
        except LookupError:
            return (box.left + box.right) / 2, box.top + (box.bottom - box.top) * 0.33
        mx, my = getattr(mod, "MOUTH", (mod.CENTER_X, mod.HEAD_TOP + (mod.FEET_Y - mod.HEAD_TOP) * 0.2))
        k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
        cx = (box.left + box.right) / 2
        dx = (mx - mod.CENTER_X) * k
        return (cx - dx if box.flip else cx + dx), box.bottom - (mod.FEET_Y - my) * k

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

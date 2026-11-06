"""Chapter openers: one full-page story picture per chapter.

An opener is not a generic scene with the cast lined up: it is a page-sized picture with a story, in the manner
of the printed original's spreads: every chapter picture tells an interesting story, one people would look
at for several minutes. Each story is a function that composes a `Stage`:
a backdrop, then objects and characters placed by hand, each with its box.

The page around the picture is HTML: the title (drawn by `bookkit/title.py`: heavy ink letters on paper plates, line by
line; its real size is reserved) at the
top left, the chapter tag at the bottom left, and the professor's bubble, whose place the story
chooses so that he stands right under its tail. Those areas are reserved: no object may reach into them, and
no two objects overlap unless they belong to one group (a cat sitting on a desk, a book in a shelf).
`tests/test_openers.py` checks both; in the build the boxes go into the SVG as invisible rects, so the
paginator's "nothing runs into a picture" check sees the title and the bubble against the real drawing.

Units: the page is 840 x 1188 (4 units to the millimetre).
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from .. import design as P
from .characters import module, resolve
from .ink import Canvas, n, settle_lettering
from .scenes import PROFESSOR_HEIGHT
from .scenes import actor as _actor

W = 840
H = 1188
MM = W / P.PAGE_WIDTH
# Areas of the page held by HTML, in units: (left, top, right, bottom).
TITLE_AT = 11                         # the title is drawn this many mm from the page's top and left
TITLE_ZONE = (0, 0, 680, 252)        # up to three lines of the title
TAG_ZONE = (0, 1100, 250, 1188)      # the arrow tag with the chapter's number at the bottom left
TAIL_MM = 9                          # how far the opener bubble's tail reaches below the bubble
CLEAR_MM = 4                         # the air round the opener bubble: nothing comes nearer


@dataclass
class Box:
    left: float
    top: float
    right: float
    bottom: float
    name: str
    group: str
    kind: str = "thing"    # "thing", "actor", or "backdrop": big furniture a character may stand in front of
    flip: bool = False     # an actor drawn mirrored (facing left)

    def hits(self, other: Box | tuple, air: float = 0) -> bool:
        o = other if isinstance(other, tuple) else (other.left, other.top, other.right, other.bottom)
        return (self.left < o[2] + air and o[0] < self.right + air and
                self.top < o[3] + air and o[1] < self.bottom + air)


@dataclass
class Opener:
    """A finished opener: the picture and where the professor's bubble goes."""
    svg: str
    bubble: tuple[float, float, float, float]   # left, bottom (the tail's tip), width, tail x - all in mm
    boxes: list[Box] = field(default_factory=list)
    reserved: list[tuple] = field(default_factory=list)
    bubble_box: tuple = ()                      # the bubble on the picture, in page units
    edges: list[tuple] = field(default_factory=list)    # structural edges the bubble keeps clear of
    reach: list[tuple] = field(default_factory=list)    # (name, box) of every character, its hands included


class Stage:
    """A page-sized picture being composed: a backdrop and depth-sorted objects, each with its box."""

    def __init__(self, seed: int = 0, lead_chars: int = 140, words: dict | None = None, height: float = H,
                 reserved: list[tuple] | None = None) -> None:
        self.back = Canvas()
        self.items: list[tuple[float, int, str]] = []
        self.boxes: list[Box] = []
        self.rnd = random.Random(seed)
        self.h = height
        self.reserved: list[tuple] = [TITLE_ZONE, TAG_ZONE] if reserved is None else list(reserved)
        self.bubble: tuple | None = None
        self.lead_chars = lead_chars       # how long the professor's words are: the bubble grows with them
        self.words = words or {}           # the lettering inside the picture, from the locale
        self.drawn: dict[int, tuple[int, dict]] = {}   # id of an actor's box -> its item and how it was drawn
        self.edges: list[tuple] = []       # window frames, posts, rails: what the bubble must not sit on
        self.bubble_box: tuple = ()

    def keep_clear(self, *boxes: tuple) -> None:
        """Declare structural edges drawn in the picture - a window's frame, a post, a railing, a shelf's edge -
        as thin boxes: the professor's bubble keeps clear air from every one of them, so it
        never sticks to a window frame."""
        self.edges.extend(boxes)

    def reach(self) -> list[tuple]:
        """Every character's full extent: its box, and round each hand that has one a fist's room - a waving hand
        reaches past the box."""
        out = []
        for box in self.boxes:
            if box.kind != "actor":
                continue
            l_, t_, r_, b_ = box.left, box.top, box.right, box.bottom
            mod = module(box.name)
            if hasattr(mod, "hands") and id(box) in self.drawn:
                rad = (box.bottom - box.top) * 0.07
                for side in ("left", "right"):
                    try:
                        hx, hy, _ = self.grip(box, side)
                    except (KeyError, IndexError):
                        continue
                    l_, t_, r_, b_ = min(l_, hx - rad), min(t_, hy - rad), max(r_, hx + rad), max(b_, hy + rad)
            out.append((box.name, (l_, t_, r_, b_)))
        return out

    def word(self, key: str) -> str:
        """A label drawn in the picture; the words live in the locale (`openers:`), never in the code."""
        if key not in self.words:
            raise KeyError(f"the locale has no opener word {key!r}; add it under 'openers:' in the locale file")
        return str(self.words[key])

    def put(self, depth: float, fragment: str, box: tuple | list | None = None, name: str = "",
            group: str | None = None, backdrop: bool = False) -> None:
        """Add a drawing at a depth (larger is nearer).

        `box` is (left, top, right, bottom) in page units, or a list of such boxes for a long thin thing (a
        ribbon of paper, a cable). A `backdrop` is big furniture: a character standing clearly in front of it
        may hide part of it, as people do in a room."""
        self.items.append((depth, len(self.items), fragment))
        boxes = box if isinstance(box, list) else [box] if box else []
        label = name or f"item{len(self.items)}"
        for one in boxes:
            self.boxes.append(Box(*one, name=label, group=group or label, kind="backdrop" if backdrop else "thing"))

    def actor(self, name: str, x: float, feet: float, pose: str = "stand", mood: str = "smile",
              flip: bool = False, tall: float = 400, group: str | None = None, depth: float | None = None,
              **options) -> Box:
        """Stand a character with its feet at (x, feet); `tall` is how tall the professor would be here."""
        name = resolve(name)
        mod = module(name)
        k = tall / PROFESSOR_HEIGHT * mod.SCENE_SCALE
        self.put(feet if depth is None else depth, _actor(name, x, feet, tall, pose, mood, flip=flip, **options))
        half = mod.SIZE[0] * 0.40 * k
        top = feet - (mod.FEET_Y - mod.HEAD_TOP) * k
        box = Box(x - half, top, x + half, feet, name, group or name, "actor", flip)
        self.boxes.append(box)
        self.drawn[id(box)] = (len(self.items) - 1, dict(name=name, x=x, feet=feet, tall=tall, pose=pose, mood=mood,
                                                         flip=flip, options=options))
        return box

    def redraw(self, box: Box, **options) -> None:
        """Draw an actor already on the stage again with more `options` (a `hold` is added to the hands it already
        holds with), in its place and at its depth."""
        if id(box) not in self.drawn:
            raise KeyError(f"{box.name} was not stood on this stage with actor()")
        index, how = self.drawn[id(box)]
        merged = dict(how["options"])
        for key, value in options.items():
            merged[key] = {**merged.get(key, {}), **value} if key == "hold" else value
        how = {**how, "options": merged}
        depth, seq, _ = self.items[index]
        self.items[index] = (depth, seq, _actor(how["name"], how["x"], how["feet"], how["tall"], how["pose"],
                                                how["mood"], flip=how["flip"], **merged))
        self.drawn[id(box)] = (index, how)

    def grip(self, box: Box, side: str = "right", pose: str | None = None) -> tuple[float, float, float]:
        """Where a character's fist closes on the page, and the angle (degrees, page space) its forearm points:
        the middle of the grip a held thing passes through (see `rig.HandFrame.grip`). The pose is the one the
        actor was stood in, unless given."""
        mod = module(box.name)
        pose = pose or self.drawn[id(box)][1]["pose"]
        if not hasattr(mod, "hands"):
            raise KeyError(f"{box.name} has no hands to hold things in")
        frame = mod.hands(pose)[side]
        gx, gy = frame.grip
        k = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
        cx = (box.left + box.right) / 2
        dx = (gx - mod.CENTER_X) * k
        page_y = box.bottom - (mod.FEET_Y - gy) * k
        return (cx - dx, page_y, 180 - frame.rotation) if box.flip else (cx + dx, page_y, frame.rotation)

    def hold(self, box: Box, make, side: str = "right", turn: float = 0.0) -> None:
        """Put a thing into a character's hand so the hand closes round it: the character is drawn again with that
        hand made a fist, the thing in it, the fingers over it (`rig.hold`). `make(x, y, k)` draws the thing with
        its grip at (x, y), `k` being the holder's height over 100 - the makers in `handheld.py`, or any that put
        their handle at (x, y). The thing turns with the forearm; `turn` turns it further about the fist."""
        self.redraw(box, hold={side: (make, turn)})

    def speaker(self, box: Box, width: float = 96, left: float | None = None, gap: float = 14,
                head: float | None = None, air: float = 0.0) -> None:
        """The professor speaks: his bubble's tail ends `gap` units over his head, the bubble stands above.

        `left` is the bubble's left edge in mm (centred on him by default); `head` the x of his head if it is
        not over the middle of his box. The bubble's height is estimated from the length of its words (about
        0.4 characters to the millimetre of width, 7 mm a line) with room to spare. `air` (mm): how far every thing
        placed afterwards keeps from the bubble - a world's opener keeps `CLEAR_MM`."""
        cx = head if head is not None else (box.left + box.right) / 2
        tip = box.top - gap
        lft = left if left is not None else max(8.0, min(P.PAGE_WIDTH - 8 - width, cx / MM - width * 0.62))
        tail = cx / MM - lft
        self.bubble = (lft, tip / MM - TAIL_MM, width, tail)
        lines = -(-self.lead_chars // int(width * 0.40))
        height = (lines * 7 + 14) * MM
        self.bubble_box = (lft * MM, tip - TAIL_MM * MM - height - 22, (lft + width) * MM, tip - TAIL_MM * MM)
        clear = air * MM                       # the air every thing keeps from the bubble
        self.reserved.append((lft * MM - clear, tip - TAIL_MM * MM - height - 22 - clear, (lft + width) * MM + clear,
                              tip - TAIL_MM * MM + clear))
        self.reserved.append((lft * MM, tip - TAIL_MM * MM - height - 22, (lft + width) * MM, tip))
        self.reserved.append((cx - 40, tip - 30, cx + 40, box.top - 2))   # the tail and the air over his head

    def free(self, box: tuple, air: float = 6) -> bool:
        """Nothing placed so far and no reserved area is within `air` of this box."""
        return (not any(b.hits(box, air) for b in self.boxes)
                and not any(Box(*zone, "", "").hits(box) for zone in self.reserved))

    def scatter(self, make, count: int, region: tuple, size: tuple[float, float], tries: int = 40) -> None:
        """Up to `count` small things - flowers, stones - at random free spots of `region`.

        `make(x, y)` draws one standing at (x, y); `size` is its (width, height). A spot is free when the thing's
        box clears everything already placed, so nothing scattered ever lands on anything else."""
        left, top, right, bottom = region
        w, h = size
        placed = 0
        for _ in range(tries):
            if placed == count:
                return
            x, y = self.rnd.uniform(left + w / 2, right - w / 2), self.rnd.uniform(top + h, bottom)
            box = (x - w / 2, y - h, x + w / 2, y)
            if self.free(box):
                self.put(y, make(x, y), box, f"small{len(self.boxes)}")
                placed += 1

    def svg(self, css_class: str, align: str = "xMidYMid", marks: bool = True) -> str:
        """The whole picture as `<svg>`; `marks` adds an invisible rect per box for the paginator's checks."""
        body = settle_lettering(self.back.render() + "".join(f for _, _, f in sorted(self.items,
                                                                                    key=lambda item: item[:2])))
        rects = "".join(f'<rect class="art-box" x="{n(b.left)}" y="{n(b.top)}" width="{n(b.right - b.left)}" '
                        f'height="{n(b.bottom - b.top)}" fill="none" stroke="none"/>'
                        for b in self.boxes) if marks else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {n(self.h)}" class="{css_class}" '
                f'preserveAspectRatio="{align} slice" aria-hidden="true">{body}{rects}</svg>')

    def render(self) -> Opener:
        svg = self.svg("opener-art")
        if self.bubble is None:
            raise ValueError("an opener needs a speaker: call Stage.speaker()")
        lft, tip, width, tail = self.bubble
        return Opener(svg, (lft, P.PAGE_HEIGHT - tip, width, tail), list(self.boxes), list(self.reserved),
                      self.bubble_box, list(self.edges), self.reach())


IN_FRONT = 60   # a character whose feet are this much nearer than a backdrop's foot stands in front of it


def _in_front(a: Box, b: Box) -> bool:
    """One of the two is a character standing clearly in front of the other, a big piece of furniture."""
    return any(x.kind == "actor" and y.kind == "backdrop" and x.bottom - y.bottom >= IN_FRONT
               for x, y in ((a, b), (b, a)))


def conflicts(opener: Opener, air: float = 4) -> list[str]:
    """Every pair of boxes from different groups that touch, and every box reaching into a reserved area."""
    found = []
    boxes = opener.boxes
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if a.group != b.group and a.hits(b, air) and not _in_front(a, b):
                found.append(f"{a.name} overlaps {b.name}")
        for zone in opener.reserved:
            if a.hits(zone):
                found.append(f"{a.name} reaches into a reserved area {tuple(round(v) for v in zone)}")
    return found


def opener(name: str, accent: str, seed: int = 0, lead_chars: int = 140, words: dict | None = None,
           title: tuple[float, float] | None = None) -> Opener:
    """Draw the opener `name` in the chapter's accent color.

    `lead_chars` is the length of the bubble's words; `words` the lettering in the picture (`openers:` in the
    locale); `title` the drawn title's width and height in mm, kept clear with some air (the default zone holds
    the square and three lines)."""
    zone = TITLE_ZONE
    if title:
        zone = (0, 0, max(TITLE_ZONE[2], (TITLE_AT + title[0]) * MM + 20), (TITLE_AT + title[1]) * MM + 24)
    return OPENERS[name](Stage(seed, lead_chars, words, reserved=[zone, TAG_ZONE]), accent)


def strip_boxes(points: list[tuple[float, float]], width: float) -> list[tuple]:
    """Boxes along a long thin thing (a ribbon, a cable), one per stretch between two points."""
    half = width / 2
    return [(min(a[0], b[0]) - half, min(a[1], b[1]) - half, max(a[0], b[0]) + half, max(a[1], b[1]) + half)
            for a, b in zip(points, points[1:], strict=False)]


# The stories, registered by the name used as `scene:` in a chapter's front matter.
from . import stories  # noqa: E402  (the stories use Stage, defined above)

OPENERS = stories.OPENERS

"""The flip-book: a tiny sparrow beside the page-number tag at the foot of every page of a chapter, a little further
on in his flight on each page - he stands on the tag, gets ready, takes off, flies a loop and lands again - so that
flicking through the pages animates him (an easter egg). Nothing explains him.

He is drawn into the page's footer scene, in the column over the tag that the scene keeps clear for it; his
sequence restarts with every chapter (so `--only` draws what the full build draws), and a page whose scene leaves
him no room skips its frame - the sequence goes on with the next page; so does a page whose scene has its own
sparrow (two would read as a mistake). A faint paper halo keeps him clear over any backdrop.
"""
from __future__ import annotations

from .. import design as P
from .openers import W, Box
from .scenes import PROFESSOR_HEIGHT, actor
from .sparrow import FEET_Y, SCENE_SCALE

FLIER = "sparrow"            # who flies the flip-book: never drawn where the scene has him already
TALL = 30.0                  # how tall he is on the page, in units (7.5 mm)
HALF = 20.0                  # half his width, wings included
TAG_W, TAG_TOP = 84.0, 68.0  # the page-number tag: 21 mm wide, its top 17 mm over the page's foot (page.css)
STAND = 34.0                 # where he stands on the tag: this far in from the page's edge
AIR = 3.0
ROOM = 64.0                  # how high over the tag his loop goes at most: he keeps by it

# His flight, one frame a page: (how far in from the page's edge, how high his feet are over the tag's top as a
# share of the room there, pose, turn in degrees - his loop - and whether he faces the page's middle).
FRAMES = (
    (STAND, 0.0, "stand", 0, True),
    (STAND, 0.0, "cheer", 0, True),
    (52, 0.25, "fly", -15, True),
    (72, 0.55, "fly", -30, True),
    (84, 0.85, "fly", -100, True),
    (62, 1.0, "fly", -180, True),
    (44, 0.8, "fly", -260, True),
    (56, 0.45, "fly", -340, True),
    (44, 0.18, "fly", 12, False),
    (STAND, 0.0, "wave", 0, True),
)


def tag_box(s) -> tuple[float, float, float, float]:
    """The page-number tag on the footer, in its units."""
    left = 0.0 if s.clear == "left" else W - TAG_W
    return (left, s.h - TAG_TOP, left + TAG_W, s.h - 24)


def frame_box(s, nth: int) -> tuple[tuple[float, float, float, float], float, float, tuple] | None:
    """Where the sparrow of page `nth` of the chapter goes on the footer `s`: his box, his feet, his middle's x,
    and the frame; None when the footer has no tag."""
    if s.clear not in ("left", "right"):
        return None
    d, rise, pose, turn, inward = FRAMES[nth % len(FRAMES)]
    room = max(0.0, min(ROOM, s.h - TAG_TOP - TALL - 4))        # over the tag, under the footer's top
    feet = s.h - TAG_TOP - 1 - rise * room
    x = d if s.clear == "left" else W - d
    if turn:                                                     # turned in his loop: a square round his middle
        half = TALL * 0.62
        feet = max(feet, 3 + half + TALL / 2)                    # kept whole under the footer's top
        mid = feet - TALL / 2
        return (x - half, mid - half, x + half, mid + half), feet, x, (pose, turn, inward)
    return (x - HALF, feet - TALL, x + HALF, feet), feet, x, (pose, turn, inward)


def flipbook(s, nth: int) -> tuple[float, float, float, float] | None:
    """Draw page `nth`'s frame of the flight on the footer `s` if it is free there; returns his box when drawn."""
    found = frame_box(s, nth)
    if found is None:
        return None
    box, feet, x, (pose, turn, inward) = found
    if box[1] < 2 or box[0] < 2 or box[2] > W - 2:
        return None
    if any(b.kind == "actor" and b.name == FLIER for b in s.boxes):   # the scene's own sparrow: never two
        return None
    if any(b.hits(box, AIR) for b in s.boxes):
        return None
    if Box(*tag_box(s), "", "").hits(box):                       # standing on the tag, never over it
        return None
    flip = inward == (s.clear == "right")                        # he is drawn facing right
    k = TALL / FEET_Y
    height = k * PROFESSOR_HEIGHT / SCENE_SCALE
    lift = 26 * k if pose == "fly" else 0.0
    svg = actor(FLIER, x, feet + lift, height, pose, "smile", flip=flip, shadow=False)
    if turn:
        way = -1 if s.clear == "right" else 1                    # the loop turns the same way on both pages
        svg = f'<g transform="rotate({turn * way:.1f} {x:.1f} {feet - TALL / 2:.1f})">{svg}</g>'
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    rx, ry = (box[2] - box[0]) / 2 + 4, (box[3] - box[1]) / 2 + 4
    halo = "".join(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx * f:.1f}" ry="{ry * f:.1f}" fill="{P.PAPER}" '
                   f'fill-opacity="{o}"/>' for f, o in ((1.18, 0.3), (1.0, 0.45), (0.82, 0.6)))
    s.put(s.h + 5, halo + svg, None)                             # a faint paper halo: he reads over any backdrop
    s.flipbook = box
    return box

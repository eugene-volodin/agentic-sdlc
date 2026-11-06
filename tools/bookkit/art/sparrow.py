"""The Sparrow: a brown egg of a bird with a three-hair tuft and permanently worried brows.

Drawn turned slightly to the right on a 200 x 200 canvas, feet on y = 190.
"""
from __future__ import annotations

import math

from .. import design as P
from .ink import Canvas, ellipse_d

SIZE = (200, 200)
VIEW_BOX = "-36 -8 272 216"
FEET_Y = 190
BUST_BOX = "20 -8 160 160"  # square, for round portrait frames

BODY = P.FEATHER
BELLY = P.FEATHER_LIGHT
WING = P.FEATHER_DARK
BEAK = P.AMBER

# pose -> (legs, left wing angle, right wing angle, body tilt); angles in degrees, 0 = straight out
POSES = {
    "stand": ("stand", 62, 62, 0),
    "cheer": ("stand", -52, -52, 0),
    "wave": ("stand", 58, -58, 0),
    "point": ("stand", 58, -8, 0),
    "present": ("stand", 30, 12, 0),
    "walk": ("walk", 36, 20, 4),
    "fly": ("fly", -30, -34, -14),
    "shrug": ("stand", 8, 8, 0),
}
CENTER_X = 100
HEAD_TOP = 0
MOUTH = (107, 99)          # where speech comes from, on the canvas: a bubble's tail points here
PEEK_Y = 92            # an edge the character looks over hides everything below: across the beak line
SCENE_SCALE = 0.95
# Where the tip of the front wing is in each pose that can hold a balloon string: (x, y) on the canvas.
BALLOON_GRIP = {"wave": (174, 59), "walk": (198, 131)}
HAND = WING
TALK_POSE = "wave"
QUOTE_POSES = ("point", "wave", "cheer", "shrug")
RECAP_POSE = "point"


def hand_point(pose: str, side: str = "right") -> tuple[float, float]:
    """Where a wing ends in a pose, on the canvas: he has wings, not wrists, and holds things at their tips."""
    angle = math.radians(POSES[pose][2 if side == "right" else 1])
    if side == "right":
        return 142 + 58 * math.cos(angle), 110 + 58 * math.sin(angle)
    return 60 - 58 * math.cos(angle), 110 + 58 * math.sin(angle)


def _wing(c: Canvas, x: float, y: float, rotation: float, mirror: bool = False) -> None:
    """A wing that doubles as a hand: three finger feathers at the tip."""
    g = Canvas()
    g.shape("M0,-10 C12,-20 30,-22 43,-18 Q55,-19 59,-12 Q53,-9 50,-7 Q61,-5 63,2 Q55,4 50,5 "
            "Q57,10 54,16 C38,20 14,16 0,10 Z", WING, light=(-2, -3))
    g.line("M16,-9 Q28,-13 40,-10 M14,0 Q28,-3 42,-1 M16,8 Q28,7 40,9", 1.5)
    flip = " scale(-1,1)" if mirror else ""
    c.place(g, f"translate({x},{y}){flip} rotate({rotation})")


def _legs(c: Canvas, stance: str) -> None:
    def leg(x0: float, x1: float, y1: float) -> None:
        c.line(f"M{x0},160 L{x1},{y1}", 3)
        c.line(f"M{x1},{y1} l-10,4 M{x1},{y1} l1,7 M{x1},{y1} l11,3", 2.8)

    if stance == "walk":
        leg(90, 76, 184)
        leg(112, 128, 182)
    elif stance == "fly":
        c.line("M92,160 l-8,12 l-7,-2 M84,172 l-2,6 M110,160 l-4,13 l-7,0 M106,173 l0,6", 2.8)
    else:
        leg(90, 88, 184)
        leg(112, 114, 184)


def draw(pose: str = "stand", mood: str = "smile") -> Canvas:
    """Draw the Sparrow. See `POSES` and `MOODS` for the options."""
    stance, left, right, tilt = POSES[pose]
    c = Canvas()
    g = Canvas()
    _legs(g, stance)
    # Tail feathers stick out behind, on the left.
    g.shape("M64,132 L26,150 L36,139 L20,136 L38,128 L26,120 L60,118 Z", WING, light=(-2, -2))
    g.line("M36,139 L52,134 M38,128 L54,127", 1.5)
    _wing(g, 60, 110, left, mirror=True)
    body = g.shape("M100,22 C135,22 150,64 150,104 C150,146 129,168 100,168 C71,168 50,146 50,104 "
                   "C50,64 65,22 100,22 Z", BODY, stipple=(112, 70, 40, 90, 60, "right"),
                   highlight="M72,52 Q62,72 60,94")
    g.add(f'<g clip-path="url(#{body})"><ellipse cx="106" cy="134" rx="30" ry="32" fill="{BELLY}" opacity=".7"/></g>')
    g.dots(body, 60, 140, 80, 28, 26, "bottom", seed=5)
    g.line("M95,23 q-9,-13 -17,-13 M100,22 q0,-15 4,-22 M105,23 q8,-11 17,-11", 2.3)
    g.path("M92,112 L120,112 L106,134 Z", P.DARK_BROWN, 2.2)  # the dark bib
    # Face, shifted right because he is turned that way.
    if mood == "surprise":
        g.line("M86,54 Q93,47 100,53 M110,53 Q117,47 124,54", 2.4)
    else:
        g.line("M85,60 L98,53 M125,60 L112,53", 2.4)
    big = 1.2 if mood == "surprise" else 1
    if mood == "wink":
        g.line("M90,75 Q97,81 104,75", 2.6)
    else:
        g.path(ellipse_d(97, 74, 6.6 * big, 9.4 * big), P.WHITE, 1.9)
        g.dot(99, 76, 3)
    g.path(ellipse_d(112, 74, 6.6 * big, 9.4 * big), P.WHITE, 1.9)
    g.dot(114, 76, 3)
    if mood in ("talk", "surprise"):
        g.shape("M90,93 L106,86 L124,92 L106,98 Z", BEAK, light=(-2, -2))
        g.path("M94,99 L106,98 L119,98 L107,112 Z", BEAK, 2.4)
        g.path("M96,97 L118,96 L107,103 Z", P.MOUTH, 1.4)
    else:
        g.shape("M90,94 L106,86 L124,93 L107,107 Z", BEAK, light=(-2, -2))
        g.line("M90,94 Q107,99 124,93", 2)
    if mood == "worry":
        g.add(f'<path d="M132,58 q5,8 0,12 q-5,-4 0,-12 Z" fill="{P.WATER}" stroke="{P.INK}" stroke-width="1.5"/>')
    _wing(g, 142, 110, right)
    c.place(g, f"rotate({tilt},100,110)")
    return c

"""The Caterpillar: green head, red bow with a yellow tuft, yellow belly, spiked green back.

Drawn upright facing the viewer on a 230 x 270 canvas, feet on y = 258.
The tail trails along the ground to the right. In `stride` she walks to the right: her tail trailing behind her on
the left, her belly ahead, her face turned the way she goes, her little feet stepping.
"""
from __future__ import annotations

from .. import design as P
from .handheld import notebook, pencil
from .ink import Canvas, ellipse_d
from .rig import HandFrame, arm, hand_frame, hold

SIZE = (230, 270)
VIEW_BOX = "-34 0 290 270"
FEET_Y = 258
BUST_BOX = "18 -6 164 164"  # square, for round portrait frames

GREEN = P.CATERPILLAR
GREEN_DARK = P.CATERPILLAR_DARK
YELLOW = P.CATERPILLAR_BELLY
RED = P.RED

SHOULDER_L = (82, 146)
SHOULDER_R = (124, 146)
REST_L = ((58, 166), (58, 192), "relaxed", 0)
REST_R = ((166, 170), (170, 196), "relaxed", 0)
# pose -> (legs, left arm, right arm); an arm is (elbow, wrist, hand kind, hand turn)
POSES = {
    "wave": ("stand", REST_L, ((158, 146), (172, 112), "open", 0)),
    "think": ("stand", REST_L, ((168, 176), (130, 140), "fist", -16)),
    "present": ("stand", REST_L, ((158, 164), (186, 148), "open", -15)),
    "cheer": ("stand", ((48, 146), (34, 112), "open", 0), ((158, 146), (172, 112), "open", 0)),
    "stand": ("stand", REST_L, REST_R),
    "point": ("stand", REST_L, ((156, 158), (186, 152), "point", 0)),
    "walk": ("walk", ((56, 162), (48, 186), "relaxed", 0), ((158, 160), (170, 182), "relaxed", 0)),
    "write": ("stand", ((54, 186), (66, 190), "hold", -18), ((156, 184), (136, 178), "hold", 0)),
    # walking to the right: the far arm swings back behind the body, the near one forward
    "stride": ("stride", ((66, 166), (52, 186), "relaxed", 8), ((146, 162), (164, 182), "relaxed", 0)),
    "knit": ("stand", ((52, 170), (76, 188), "grip", -30), ((158, 168), (136, 186), "grip", 30)),   # needles in
}
CENTER_X = 104
HEAD_TOP = 4
MOUTH = (100, 106)          # where speech comes from, on the canvas: a bubble's tail points here
PEEK_Y = 96            # an edge the character looks over hides everything below: under the nose
SCENE_SCALE = 1.0
HAND = YELLOW
TALK_POSE = "wave"
QUOTE_POSES = ("wave", "present", "write", "cheer")
RECAP_POSE = "write"
NECK = (100, 128)           # the hands turn their thumbs towards it
ARM_WIDTH = 8
HAND_SCALE = 0.84


def _spike(c: Canvas, x: float, y: float, turn: float) -> None:
    g = Canvas()
    g.path("M-5,0 Q0,-12 2,-13 Q5,-6 6,0 Z", GREEN_DARK, 1.9)
    c.place(g, f"translate({x},{y}) rotate({turn})")


TURN = "translate(114,0) scale(.82,1) translate(-100,0)"   # the face turned to the right: features shifted, narrower


def _head(c: Canvas, mood: str, turned: bool = False) -> None:
    c.path("M94,36 Q86,14 102,4 Q99,18 110,34 Z", YELLOW, 2.4)  # tuft, behind the bow
    c.shape(ellipse_d(100, 84, 46, 45), GREEN, stipple=(108, 86, 40, 44, 46, "right"),
            highlight="M72,58 Q64,70 62,84")
    if turned:
        face = Canvas()
        _face(face, mood)
        c.place(face, TURN)
        return
    _face(c, mood)


def _face(c: Canvas, mood: str) -> None:
    """The bow, brows, eyes, nose and mouth."""
    # Bow: two shaded loops and a knot.
    c.shape("M100,42 L66,22 Q58,40 68,58 Z", RED, light=(-3, -3))
    c.shape("M100,42 L134,22 Q142,40 132,58 Z", RED, light=(-3, -3))
    c.line("M78,34 L92,41 M122,34 L108,41 M76,48 L90,44", 1.5)
    c.path(ellipse_d(100, 42, 7, 7.6), RED, 2.4)
    # Eyes with lashes; brows above.
    if mood == "worry":
        c.line("M80,60 L92,55 M116,60 L104,55", 2.2)
    elif mood == "surprise":
        c.line("M81,54 Q87,48 93,53 M103,53 Q109,48 115,54", 2.2)
    else:
        c.line("M81,57 Q87,52 93,57 M103,57 Q109,52 115,57", 2.2)
    big = 1.2 if mood == "surprise" else 1
    if mood == "wink":
        c.line("M84,73 Q90,78 96,73", 2.4)
    else:
        c.path(ellipse_d(90, 72, 6 * big, 8 * big), P.WHITE, 1.9)
        c.dot(91.500, 74, 2.8)
        c.line("M83,66 l-4,-3 M85,64 l-2,-4", 1.4)
    c.path(ellipse_d(106, 72, 6 * big, 8 * big), P.WHITE, 1.9)
    c.dot(107.500, 74, 2.8)
    c.line("M113,66 l4,-3 M111,64 l2,-4", 1.4)
    c.path(ellipse_d(98, 90, 6, 4.6), P.CATERPILLAR_NOSE, 1.9)
    if mood in ("talk", "surprise"):
        c.path(ellipse_d(99, 106, 7.5, 7), P.MOUTH, 2.2)
        c.add(f'<ellipse cx="99" cy="110" rx="4.500" ry="2.800" fill="{P.TONGUE}"/>')
    elif mood == "worry":
        c.line("M86,108 Q99,100 112,108", 2.4)
    else:
        c.path("M76,97 Q100,126 126,95 Q100,106 76,97 Z", P.MOUTH, 2.3)
        c.add(f'<path d="M90,108 Q100,116 112,107 Q100,111 90,108 Z" fill="{P.TONGUE}"/>')
        c.line("M73,93 l5,6 M129,91 l-5,6", 1.8)


def hands(pose: str, grips: tuple[str, ...] = ()) -> dict[str, HandFrame]:
    """Where the hands of a pose are drawn (see `rig.HandFrame`); `grips` names the ones closed round a handle."""
    _, left, right = POSES[pose]
    return {side: hand_frame(limb[0], limb[1], ARM_WIDTH, HAND_SCALE, limb[3],
                             "hold" if side in grips else limb[2], NECK)
            for side, limb in (("left", left), ("right", right))}


def draw(pose: str = "wave", mood: str = "smile", grips: tuple[str, ...] = ()) -> Canvas:
    """Draw the Caterpillar. See `POSES` and `MOODS` for the options; `grips` closes those hands ("left",
    "right") round a handle for `rig.hold` (see `characters.draw(hold=...)`)."""
    stance, left, right = POSES[pose]
    if stance == "stride":
        return _stride(pose, mood, grips, left, right)
    if grips:
        left = (*left[:2], "hold" if "left" in grips else left[2], left[3])
        right = (*right[:2], "hold" if "right" in grips else right[2], right[3])
    c = Canvas()
    # Tail segments on the ground, far to near.
    for cx, cy, rx, ry in ((214, 232, 8, 6), (198, 236, 13, 9), (176, 238, 19, 12), (149, 233, 24, 15)):
        c.shape(ellipse_d(cx, cy, rx, ry), GREEN, light=(-2, -3))
        _spike(c, cx + 1, cy - ry + 1, 8)
    # Little legs and feet.
    feet = ((78, 250, 86, 226), (126, 250, 114, 226))
    if stance == "walk":
        feet = ((66, 250, 86, 226), (140, 246, 114, 226))
    for fx, fy, hx, hy in feet:
        c.tube(f"M{hx},{hy} L{fx + 4},{fy - 4}", YELLOW, 9)
        c.shape(ellipse_d(fx, fy + 1, 14, 7.5), YELLOW, light=(-2, -2))
    glove = dict(sleeve=YELLOW, width=ARM_WIDTH, skin=YELLOW, hand_scale=HAND_SCALE, toward=NECK)

    def reaches_across(limb: tuple) -> bool:
        """An arm whose hand ends over the belly is drawn in front of the body."""
        return 70 < limb[1][0] < 142

    # Arms that hang or wave at the sides come out from behind the body.
    for shoulder, limb in ((SHOULDER_L, left), (SHOULDER_R, right)):
        if not reaches_across(limb):
            arm(c, shoulder, limb[0], limb[1], kind=limb[2], hand_turn=limb[3], **glove)
    # Body, bottom to top: each green back segment peeks out behind its yellow belly segment.
    for cy, rx in ((216, 32), (192, 31), (168, 29), (145, 26)):
        c.shape(ellipse_d(118, cy, rx, 18), GREEN, light=(-2, -3))
        _spike(c, 118 + rx - 3, cy - 6, 62)
        c.shape(ellipse_d(101, cy, rx, 17), YELLOW, light=(-4, -4),
                stipple=(101, cy - 14, rx, 30, 12, "right"))
    if reaches_across(left) or pose == "write":
        arm(c, SHOULDER_L, left[0], left[1], kind=left[2], hand_turn=left[3], **glove)
    if reaches_across(right) and pose != "think":
        arm(c, SHOULDER_R, right[0], right[1], kind=right[2], hand_turn=right[3], **glove)
    if pose == "write":  # a notebook held up in the left hand by its corner, the pencil in the right on its page
        frames = hands(pose, ("left", "right"))
        k = (FEET_Y - HEAD_TOP) / 100
        hold(c, frames["left"], YELLOW, notebook, k, 18)
        hold(c, frames["right"], YELLOW, pencil, k, -30)
    _head(c, mood)
    if pose == "think":  # the finger rests on the cheek, so this arm goes over the head
        arm(c, SHOULDER_R, right[0], right[1], kind=right[2], hand_turn=right[3], **glove)
    return c


def _stride(pose: str, mood: str, grips: tuple[str, ...], left: tuple, right: tuple) -> Canvas:
    """Walking to the right: the tail trailing on the ground behind her (on the left), the far arm behind the body
    swinging forward, the feet stepping, the segments with their green backs behind and the yellow belly ahead, the
    head turned the way she goes, the near arm swinging back."""
    glove = dict(sleeve=YELLOW, width=ARM_WIDTH, skin=YELLOW, hand_scale=HAND_SCALE, toward=NECK)
    kl = "hold" if "left" in grips else left[2]
    kr = "hold" if "right" in grips else right[2]
    c = Canvas()
    for cx, cy, rx, ry in ((-6, 232, 8, 6), (10, 236, 13, 9), (32, 238, 19, 12), (59, 233, 24, 15)):
        c.shape(ellipse_d(cx, cy, rx, ry), GREEN, light=(-2, -3))
        _spike(c, cx - 1, cy - ry + 1, -8)
    arm(c, (128, 146), right[0], right[1], kind=kr, hand_turn=right[3], **glove)   # the far arm, behind, forward
    for fx, fy, hx, hy in ((80, 248, 94, 226), (136, 250, 116, 226)):
        c.tube(f"M{hx},{hy} L{fx - 2},{fy - 4}", YELLOW, 9)
        c.shape(ellipse_d(fx + 4, fy + 1, 14, 7.5), YELLOW, light=(-2, -2))
    for cy, rx in ((216, 32), (192, 31), (168, 29), (145, 26)):
        c.shape(ellipse_d(92, cy, rx, 18), GREEN, light=(-2, -3))
        _spike(c, 92 - rx + 3, cy - 6, -62)
        c.shape(ellipse_d(108, cy, rx, 17), YELLOW, light=(-4, -4), stipple=(108, cy - 14, rx, 30, 12, "right"))
    _head(c, mood, turned=True)
    arm(c, (84, 150), left[0], left[1], kind=kl, hand_turn=left[3], **glove)          # the near arm, swinging back
    return c

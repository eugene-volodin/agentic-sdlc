"""Cat X: a shaggy ginger cat in round glasses, a tiny mortarboard, a bow tie and a denim vest.

Drawn facing the viewer on a 280 x 340 canvas, feet on y = 326. In `stride` he walks to the right, turned side-on:
the body narrower, the face turned the way he goes, both hind paws pointing ahead, the tail up behind him.
"""
from __future__ import annotations

import re

from .. import design as P
from .ink import Canvas, angle_of, ellipse_d, n, polar, uid
from .rig import HandFrame, arm, fingers, hand, pose_hands

SIZE = (280, 340)
VIEW_BOX = "-34 0 348 340"
FEET_Y = 326
BUST_BOX = "22 6 236 236"  # square, for round portrait frames

FUR = P.FUR
FUR_DARK = P.FUR_DARK
VEST = P.BLUE
PINK = P.PINK
WATCH = P.YELLOW

LENS = P.LENS
ARM_WIDTH = 15

# Pear-shaped body: narrow shoulders under the chin, widest at the belly. The arms join it at its sides, at the
# shoulders, coming out of the vest's armholes, so they never look crooked.
BODY = ("M120,170 C106,176 99,190 97,210 C95,230 94,256 100,270 C105,280 112,283 122,283 L158,283 "
        "C168,283 175,280 180,270 C186,256 185,230 183,210 C181,190 174,176 160,170 Z")
SHOULDER_L = (106, 198)
SHOULDER_R = (174, 198)
NECK = (140, 182)           # the hands turn their thumbs towards it
REST_L = ((86, 234), (85, 262), "relaxed", 0)
REST_R = ((194, 234), (195, 262), "relaxed", 0)
# pose -> (legs, left arm, right arm); an arm is (elbow, wrist, hand kind, hand turn)
POSES = {
    "stand": ("stand", REST_L, REST_R),
    "wave": ("stand", REST_L, ((208, 218), (220, 172), "open", 0)),
    "present": ("stand", REST_L, ((202, 236), (234, 216), "open", -20)),
    "point": ("stand", REST_L, ((208, 226), (228, 188), "point", 0)),
    "welcome": ("stand", ((78, 236), (46, 216), "open", 20), ((202, 236), (234, 216), "open", -20)),
    "think": ("stand", REST_L, ((204, 250), (166, 196), "fist", -14)),
    "cheer": ("stand", ((70, 212), (58, 166), "open", 0), ((210, 212), (222, 166), "open", 0)),
    "walk": ("walk", ((84, 232), (100, 258), "relaxed", 0), ((196, 230), (202, 260), "relaxed", 0)),
    # walking to the right in three-quarter view: the near paw (his left) swings back, the far one forward
    "stride": ("stride", ((112, 230), (96, 256), "relaxed", 10), ((196, 226), (214, 248), "relaxed", 0)),
    "sit": ("sit", ((80, 244), (100, 266), "relaxed", 0), ((200, 232), (224, 208), "open", -10)),
    "read": ("stand", ((66, 262), (78, 262), "hold", 0), ((214, 262), (202, 262), "hold", 0)),
}
# Arms that cross in front of the body; the others hang or reach out at its sides and are drawn only outside it.
FRONT = {"think": ("right",), "walk": ("left",), "sit": ("left",), "read": ("left", "right")}
CENTER_X = 140
HEAD_TOP = 16
MOUTH = (140, 148)          # where speech comes from, on the canvas: a bubble's tail points here
PEEK_Y = 135            # an edge the character looks over hides everything below: under the nose
SCENE_SCALE = 1.05
HAND = FUR
TALK_POSE = "present"
QUOTE_POSES = ("present", "wave", "think", "read")
RECAP_POSE = "read"
SEAT = "desk"
PORTRAIT_OPTIONS = {"tail": False}   # a stray tail tip in the corner of a portrait reads as a blemish


def _foot(c: Canvas, x: float, y: float, turn: float = 0.0, mirror: bool = False) -> None:
    """A hind paw with the toes pointing right (or left when mirrored)."""
    g = Canvas()
    g.shape("M-18,0 C-18,-9 -8,-11 2,-10 C14,-9 22,-5 22,2 C22,8 16,10 8,10 L-10,10 C-16,10 -18,6 -18,0 Z",
            FUR, light=(-3, -4))
    g.line("M9,1 q2,4 0,8 M15,2 q2,3 0,6", 1.6)
    flip = " scale(-1,1)" if mirror else ""
    c.place(g, f"translate({x},{y}) rotate({turn}){flip}")


def _legs(c: Canvas, stance: str) -> None:
    if stance == "walk":
        # One paw planted, the other lifted mid-step.
        c.tube("M126,270 L112,304", FUR, 21)
        _foot(c, 106, 314, 0, mirror=True)
        c.tube("M154,270 L170,298", FUR, 21)
        _foot(c, 176, 306, -22)
    elif stance == "stride":
        # Mid-stride to the right: the back paw pushing off on its toes, the front one reaching ahead.
        c.tube("M128,270 L112,302", FUR, 21)
        _foot(c, 112, 312, 14)
        c.tube("M152,270 L170,302", FUR, 21)
        _foot(c, 178, 312, -6)
    elif stance == "sit":
        # Sitting on an edge: the legs hang down and the toes droop.
        c.tube("M126,270 L122,300", FUR, 21)
        _foot(c, 118, 308, -58, mirror=True)
        c.tube("M154,270 L158,300", FUR, 21)
        _foot(c, 162, 308, 58)
    else:
        c.tube("M126,270 L122,306", FUR, 21)
        c.tube("M154,270 L158,306", FUR, 21)
        _foot(c, 116, 315, 0, mirror=True)
        _foot(c, 164, 315)


# Tail shapes: (centre line, where the dark tip sits, stripes). A pose picks one in `TAILS`,
# so the tail never looks stamped on: it curls, hangs, swishes or stands up with the mood of the pose.
TAIL_SHAPES = {
    "curl": ("M176,258 C212,272 240,252 234,222 C231,206 238,196 246,192", "M241,195 L246,192",
             "M229,236 l13,-3 M228,222 l13,1 M231,208 l11,6"),
    "low": ("M176,262 C204,282 232,286 250,270 C258,262 256,252 248,250", "M252,254 L248,250",
            "M204,270 l4,13 M222,276 l1,13 M240,266 l8,10"),
    # stands up out at the side, clear of a raised right arm: drawn up the forearm, it read as a second arm
    "up": ("M176,258 C208,264 238,252 250,226 C257,210 262,198 274,192", "M269,195 L274,192",
           "M229,256 l3,-13 M245,236 l-12,-5 M254,214 l-12,-6"),
    "swish": ("M176,260 C206,262 222,246 236,250 C250,254 256,240 250,226", "M252,231 L250,226",
              "M206,254 l1,-13 M224,242 l5,12 M244,252 l10,-6"),
}
TAILS = {"stand": "curl", "wave": "up", "present": "low", "point": "up", "welcome": "low", "think": "low",
         "cheer": "up", "walk": "swish", "sit": "low", "read": "curl", "stride": "up"}


def _tail(c: Canvas, shape: str) -> None:
    """A thick tail coming out from behind the hip, with a dark rounded tip and a few stripes."""
    line, tip, stripes = TAIL_SHAPES[shape]
    c.tube(line, FUR, 15)
    c.tube(tip, FUR_DARK, 15, shaded=False)
    c.line(stripes, 2, FUR_DARK)


TURN = "translate(160,0) scale(.8,1) translate(-140,0)"   # the face turned to the right: features shifted, narrower


def _head(c: Canvas, mood: str, turned: bool = False) -> None:
    # Ears and a shaggy silhouette: the zigzags along the cheeks are tufts of fur.
    head = c.shape(
        "M96,66 L84,30 Q83,25 88,28 L118,50 Q140,44 162,50 L192,28 Q197,25 196,30 L184,66 "
        "C206,80 218,100 220,120 L208,124 L224,136 L206,140 L218,154 L198,152 L204,166 L184,160 "
        "C170,172 156,176 140,176 C124,176 110,172 96,160 L76,166 L82,152 L62,154 L74,140 "
        "L56,136 L72,124 L60,120 C62,100 74,80 96,66 Z", FUR,
        stipple=(168, 120, 50, 54, 44, "right"), highlight="M92,84 Q80,98 76,114")
    c.dots(head, 70, 140, 140, 36, 34, "bottom", seed=7)
    c.path("M91,40 L107,53 L96,62 Z", P.EAR, 1.8)
    c.path("M189,40 L173,53 L184,62 Z", P.EAR, 1.8)
    if turned:                      # the face drawn on its own, then set turned towards the right
        face = Canvas()
        _face(face, mood)
        c.place(face, TURN)
        return
    _face(c, mood)


def _face(c: Canvas, mood: str) -> None:
    """The forehead fur, cap, glasses, eyes, brows, muzzle and whiskers."""
    c.line("M131,64 l-3,-10 M140,62 l0,-11 M149,64 l3,-10", 1.8)
    # Mortarboard, worn slightly askew, with a tassel.
    c.shape("M127,48 L153,48 L151,33 L129,33 Z", P.METAL_DARK, light=(-2, -2))
    c.shape("M106,29 L140,16 L174,29 L140,42 Z", P.METAL_LIGHT, light=(-2, -3))
    c.dot(140, 29, 2.6)
    c.line("M140,29 Q112,14 96,34", 2)
    c.path("M96,34 l-9,13 l6,-1 l1,6 l5,-5 l4,4 l-1,-13 Z", P.INK, 1.4)
    # Round glasses.
    c.line("M92,100 L72,92 M188,100 L208,92", 3)
    # Opaque lenses keep the eyes readable against the dark fur.
    c.add(f'<circle cx="116" cy="104" r="23" fill="{LENS}" stroke="{P.INK}" stroke-width="3"/>')
    c.add(f'<circle cx="164" cy="104" r="23" fill="{LENS}" stroke="{P.INK}" stroke-width="3"/>')
    c.line("M139,101 Q140,99 141,101", 3)
    # Eyes sit close to the nose.
    if mood == "wink":
        c.line("M112,108 Q120,114 128,108", 2.6)
    else:
        big = 1.2 if mood == "surprise" else 1
        c.path(ellipse_d(122, 106, 5.2 * big, 7.2 * big), P.INK, 0)
        c.dot(123.500, 103.500, 1.8, P.WHITE)
    big = 1.2 if mood == "surprise" else 1
    c.path(ellipse_d(158, 106, 5.2 * big, 7.2 * big), P.INK, 0)
    c.dot(159.500, 103.500, 1.8, P.WHITE)
    if mood == "worry":
        c.line("M106,88 L124,82 M174,88 L156,82", 2.6)
    elif mood == "surprise":
        c.line("M106,80 Q114,74 124,78 M174,80 Q166,74 156,78", 2.6)
    else:
        c.line("M106,84 L124,87 M174,84 L156,87", 2.6)
    # Muzzle: nose, mouth, tooth, whiskers.
    if mood in ("talk", "surprise"):
        c.path("M128,140 Q140,160 152,140 Z", P.MOUTH, 2.2)
        c.path("M136,140 h8 v5.500 h-8 Z", P.WHITE, 1.5)
    elif mood != "worry":
        c.path("M137,137 h6 v5 h-6 Z", P.WHITE, 1.5)
    c.path("M132,121 Q140,118 148,121 L140,131 Z", PINK, 2.2)
    if mood == "worry":
        c.line("M140,131 L140,136 M128,141 Q134,134 140,136 Q146,134 152,141", 2.3)
    else:
        c.line("M140,131 L140,136 M126,136 Q133,146 140,136 Q147,146 154,136", 2.3)
    for dx, dy in ((-18, 0), (-23, 6), (-16, 9)):
        c.dot(140 + dx, 133 + dy, 1.3)
        c.dot(140 - dx, 133 + dy, 1.3)
    c.line("M118,131 Q76,116 32,112 M116,137 Q72,134 26,138 M118,143 Q78,150 34,160", 1.6)
    c.line("M162,131 Q204,116 248,112 M164,137 Q208,134 254,138 M162,143 Q202,150 246,160", 1.6)


PAW = dict(sleeve=FUR, width=ARM_WIDTH, skin=FUR, hand_scale=0.88, toward=NECK)


def hands(pose: str, grips: tuple[str, ...] = ()) -> dict[str, HandFrame]:
    """Where the paws of a pose are drawn (see `rig.HandFrame`); `grips` names the ones closed round a handle."""
    _, left, right = POSES[pose]
    return pose_hands({"left": left, "right": right}, ARM_WIDTH, PAW["hand_scale"], NECK, grips)


def _watch(c: Canvas, elbow: tuple[float, float], wrist: tuple[float, float]) -> None:
    """The yellow wristwatch: a strap round the wrist and a round face on the outside of it."""
    direction = angle_of(*elbow, *wrist)
    cx, cy = polar(*wrist, direction, -4)
    c.add(f'<g transform="translate({n(cx)},{n(cy)}) rotate({n(direction)})">'
          f'<rect x="-3.5" y="{n(-ARM_WIDTH / 2 - 1)}" width="7" height="{n(ARM_WIDTH + 2)}" rx="2.5" '
          f'fill="{WATCH}" stroke="{P.INK}" stroke-width="1.8"/>'
          f'<circle cx="0" cy="0" r="5.6" fill="{P.CARD}" stroke="{P.INK}" stroke-width="1.8"/>'
          f'<path d="M0,0 L0,-3.4 M0,0 L2.4,0.8" fill="none" stroke="{P.INK}" stroke-width="1.1" '
          f'stroke-linecap="round"/></g>')


def _vest(c: Canvas, body: str) -> None:
    """The open denim vest, drawn inside the body's silhouette so the body's outline runs on unbroken round
    it: two panels with an armhole cut at each shoulder, where the arm comes out, and a strip of fur between
    them down the middle, so no bit of the body sticks out at the sides."""
    c.add(f'<g clip-path="url(#{body})">')
    for d, hi in (("M114,170 L128,176 L134,190 L134,266 L104,271 L60,266 L60,170 Z", True),
                  ("M166,170 L152,176 L146,190 L146,266 L176,271 L220,266 L220,170 Z", False)):
        c.shape(d, VEST, light=(-3, -4) if hi else (-2, -3))
    c.add('<path d="M130,190 L130,262 M150,190 L150,262 M96,265 L130,262 M184,265 L150,262 '
          'M102,218 Q105,192 118,178 M178,218 Q175,192 162,178" fill="none" '
          f'stroke="{P.SKY_LOW}" stroke-width="1.7" stroke-dasharray="4.500 4" stroke-linecap="round"/>')
    c.path("M107,236 l14,-2 l1,10 l-14,2 Z", VEST, 1.7)
    c.path("M173,236 l-14,-2 l-1,10 l14,2 Z", VEST, 1.7)
    for y in (214, 240):
        c.add(f'<circle cx="150" cy="{y}" r="3.6" fill="{P.WHITE}" stroke="{P.INK}" stroke-width="1.7"/>')
        c.line(f"M148.500,{y - 1.5} l3,3 M151.500,{y - 1.5} l-3,3", 0.9)
    c.add("</g>")
    c.path(BODY, "none")


def _armhole(c: Canvas, body: str, side: str) -> None:
    """The vest's shoulder over the root of an arm that crosses in front: the arm comes out of the armhole."""
    d = ("M88,166 L118,166 Q116,198 104,220 L86,220 Z" if side == "left" else
         "M192,166 L162,166 Q164,198 176,220 L194,220 Z")
    c.add(f'<g clip-path="url(#{body})">')
    c.shape(d, VEST, light=None)
    c.add('<path d="' + ("M101,214 Q109,196 111,176" if side == "left" else "M179,214 Q171,196 169,176") +
          f'" fill="none" stroke="{P.SKY_LOW}" stroke-width="1.7" stroke-dasharray="4.500 4" '
          'stroke-linecap="round"/></g>')
    c.path(BODY, "none")


def _front_arm(c: Canvas, body: str, side: str, shoulder: tuple, limb: tuple, frame: HandFrame,
               kind: str, watch: bool = True) -> None:
    """An arm crossing in front of the body: the whole arm, the vest's shoulder over its root, then the forearm
    and the paw again over that shoulder, so the arm comes out of the armhole and nothing hides the forearm."""
    arm(c, shoulder, limb[0], limb[1], kind=kind, hand_turn=limb[3], **PAW)
    _armhole(c, body, side)
    (sx, sy), (ex, ey), (wx, wy) = shoulder, limb[0], limb[1]
    mx, my = (sx + 2 * ex + wx) / 4, (sy + 2 * ey + wy) / 4
    c.tube(f"M{n(mx)},{n(my)} Q{n((ex + wx) / 2)},{n((ey + wy) / 2)} {n(wx)},{n(wy)}", FUR, ARM_WIDTH)
    hand(c, frame.x, frame.y, frame.rotation, FUR, kind, frame.scale, mirror=frame.mirror)
    if side == "right" and watch:
        _watch(c, limb[0], limb[1])


def _book(c: Canvas, frames: dict[str, HandFrame]) -> None:
    """An open book held up in both paws by its outer edges; the paws close over the covers."""
    (lx, ly), (rx, ry) = frames["left"].grip, frames["right"].grip
    left, right, mid, y = lx - 5, rx + 5, (lx + rx) / 2, (ly + ry) / 2
    top, bottom = y - 44, y + 40
    c.path(f"M{n(left)},{n(top)} L{n(left)},{n(bottom)} L{n(mid - 2)},{n(bottom + 10)} L{n(mid + 2)},"
           f"{n(bottom + 10)} L{n(right)},{n(bottom)} L{n(right)},{n(top)} L{n(mid)},{n(top + 8)} Z", P.TEAL, 2.2)
    c.shape(f"M{n(left + 4)},{n(top + 3)} L{n(mid)},{n(top + 12)} L{n(mid)},{n(bottom + 5)} L{n(left + 4)},"
            f"{n(bottom - 4)} Z", P.CARD, 2.2, light=None)
    c.shape(f"M{n(right - 4)},{n(top + 3)} L{n(mid)},{n(top + 12)} L{n(mid)},{n(bottom + 5)} L{n(right - 4)},"
            f"{n(bottom - 4)} Z", P.CARD, 2.2, light=None)
    lines = []
    for i in range(5):
        yy = top + 22 + i * 11
        lines.append(f"M{n(left + 14)},{n(yy)} L{n(mid - 8)},{n(yy + 4)}")
        if i < 4:
            lines.append(f"M{n(right - 14)},{n(yy)} L{n(mid + 8)},{n(yy + 4)}")
    c.line(" ".join(lines), 1.3, opacity=0.5)


def draw(pose: str = "stand", mood: str = "smile", tail: bool = True, grips: tuple[str, ...] = (),
         palms: tuple[str, ...] = ()) -> Canvas:
    """Draw Cat X. See `POSES` and `MOODS` for the options; `tail=False` suits tight portraits; `grips` closes
    those paws ("left", "right") round a handle for `rig.hold` (see `characters.draw(hold=...)`); `palms` names the
    paws that cradle a thing in the palm - a stopwatch: that arm goes without the wristwatch, since two watches side
    by side read as a mistake."""
    stance, left, right = POSES[pose]
    if stance == "stride":
        return _stride(pose, mood, tail, grips, palms, left, right)
    front = FRONT.get(pose, ())
    c = Canvas()
    if tail:
        _tail(c, TAILS[pose])
    _legs(c, stance)
    body = c.shape(BODY, FUR, stipple=(134, 200, 12, 72, 16, "even"))
    _vest(c, body)
    _head(c, mood)
    # Bow tie over the chin fur.
    c.shape("M140,188 L116,176 Q112,189 117,202 Z", PINK, light=(-2, -3))
    c.shape("M140,188 L164,176 Q168,189 163,202 Z", PINK, light=(-2, -3))
    c.path(ellipse_d(140, 189, 5.5, 6), PINK, 2.2)
    c.line("M124,186 l8,3 M156,186 l-8,3", 1.4)
    frames = hands(pose, grips)
    for side, shoulder, limb in (("left", SHOULDER_L, left), ("right", SHOULDER_R, right)):
        if side in front:      # out of the armhole and across the body, in front of it
            _front_arm(c, body, side, shoulder, limb, frames[side], "hold" if side in grips else limb[2],
                       side not in palms)
    outside = uid()
    c.add(f'<clipPath id="{outside}"><path clip-rule="evenodd" d="M-400,-400 H700 V800 H-400 Z {BODY}"/>'
          "</clipPath>")
    for side, shoulder, limb in (("left", SHOULDER_L, left), ("right", SHOULDER_R, right)):
        if side in front:
            continue
        kind = "hold" if side in grips else limb[2]
        # a side arm comes out from behind the body at the shoulder: only what is outside it shows, then the paw
        c.add(f'<g clip-path="url(#{outside})">')
        arm(c, shoulder, limb[0], limb[1], kind=kind, hand_turn=limb[3], **PAW)
        c.add("</g>")
        f = frames[side]
        hand(c, f.x, f.y, f.rotation, FUR, kind, f.scale, mirror=f.mirror)
        if side == "right" and side not in palms:
            _watch(c, limb[0], limb[1])
    if pose == "read":  # an open book held up in both paws by its edges
        _book(c, frames)
        for f in frames.values():
            fingers(c, f, FUR)
    return c


# Three-quarter view, turned to the right: the chest's centreline moves right under the turned chin, the near half
# of the body stays nearly as wide and the far half narrows.
CHEST = 154


def _tx(x: float) -> float:
    return CHEST + (x - 140) * (0.9 if x < 140 else 0.6)


def _turn_d(d: str) -> str:
    """A path of absolute commands turned to three-quarter view: every x through `_tx` (relative steps scaled by
    the mean of the two halves)."""
    out, cmd, nums = [], "", []

    def flush() -> None:
        if not cmd:
            return
        vals = [float(v) for v in nums]
        if cmd in "MLCQST":
            vals = [_tx(v) if i % 2 == 0 else v for i, v in enumerate(vals)]
        elif cmd == "H":
            vals = [_tx(v) for v in vals]
        elif cmd in "mlcqst":
            vals = [v * 0.75 if i % 2 == 0 else v for i, v in enumerate(vals)]
        elif cmd == "h":
            vals = [v * 0.75 for v in vals]
        out.append(cmd + " ".join(n(v) for v in vals))

    for tok in re.findall(r"[A-Za-z]|-?\d*\.?\d+", d):
        if tok.isalpha():
            flush()
            cmd, nums = tok, []
        else:
            nums.append(tok)
    flush()
    return " ".join(out)


def _vest_turned(c: Canvas, body: str, turned_body: str) -> None:
    """The open vest in three-quarter view: its two panels and the strip of fur between them symmetric about the
    turned centreline, the near panel wider, the far one narrower."""
    c.add(f'<g clip-path="url(#{body})">')
    for d, hi in (("M114,170 L128,176 L134,190 L134,266 L104,271 L60,266 L60,170 Z", True),
                  ("M166,170 L152,176 L146,190 L146,266 L176,271 L220,266 L220,170 Z", False)):
        c.shape(_turn_d(d), VEST, light=(-3, -4) if hi else (-2, -3))
    seams = _turn_d("M130,190 L130,262 M150,190 L150,262 M96,265 L130,262 M184,265 L150,262 "
                    "M102,218 Q105,192 118,178 M178,218 Q175,192 162,178")
    c.add(f'<path d="{seams}" fill="none" stroke="{P.SKY_LOW}" stroke-width="1.7" stroke-dasharray="4.500 4" '
          'stroke-linecap="round"/>')
    c.path(_turn_d("M107,236 L121,234 L122,244 L108,246 Z"), VEST, 1.7)
    c.path(_turn_d("M173,236 L159,234 L158,244 L172,246 Z"), VEST, 1.7)
    bx = _tx(150)
    for y in (214, 240):
        c.add(f'<circle cx="{n(bx)}" cy="{y}" r="3.2" fill="{P.WHITE}" stroke="{P.INK}" stroke-width="1.7"/>')
    c.add("</g>")
    c.path(turned_body, "none")


def _stride(pose: str, mood: str, tail: bool, grips: tuple[str, ...], palms: tuple[str, ...], left: tuple,
            right: tuple) -> Canvas:
    """Walking to the right in three-quarter view: the far arm (his right) behind the body swinging forward, the
    tail up behind him (on the left), the legs mid-stride, the body and the vest turned about the chest's
    centreline, the bow tie on it under the chin, the face turned the way he goes, the near arm (his left) in
    front swinging back."""
    c = Canvas()
    near = (_tx(SHOULDER_L[0]) + 2, SHOULDER_L[1])
    far = (_tx(SHOULDER_R[0]) - 4, SHOULDER_R[1])
    kl = "hold" if "left" in grips else left[2]
    kr = "hold" if "right" in grips else right[2]
    arm(c, far, right[0], right[1], kind=kr, hand_turn=right[3], **PAW)             # the far arm, behind
    if "right" not in palms:
        _watch(c, right[0], right[1])
    if tail:
        g = Canvas()
        _tail(g, TAILS[pose])
        c.place(g, "translate(280,0) scale(-1,1)")                                    # up behind him
    _legs(c, "stride")
    turned = _turn_d(BODY)
    body = c.shape(turned, FUR, stipple=(134, 200, 12, 72, 16, "even"))
    _vest_turned(c, body, turned)
    _head(c, mood, turned=True)
    bx = _tx(140) + 4                                                                  # under the turned chin
    c.shape(f"M{n(bx)},188 L{n(bx - 22)},176 Q{n(bx - 26)},189 {n(bx - 21)},202 Z", PINK, light=(-2, -3))
    c.shape(f"M{n(bx)},188 L{n(bx + 15)},177 Q{n(bx + 18)},189 {n(bx + 14)},201 Z", PINK, light=(-2, -3))
    c.path(ellipse_d(bx, 189, 5, 6), PINK, 2.2)
    arm(c, near, left[0], left[1], kind=kl, hand_turn=left[3], **PAW)                # the near arm, in front
    return c

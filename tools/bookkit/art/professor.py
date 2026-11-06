"""Professor Fortran: tall bald dome, ginger hair at the back, square glasses, moustache.

The head is always in three-quarter view facing right. The body has two rigs:

* `front` - chest towards the viewer, for standing poses and gestures;
* `side`  - true profile, for walking and sitting, so legs and torso agree.

Canvas 270 x 450, feet on y = 436.
"""
from __future__ import annotations

from .. import design as P
from .ink import Canvas, ellipse_d, n, rounded_rect_d
from .rig import HandFrame, arm, hand_frame

SIZE = (270, 450)
VIEW_BOX = "-30 0 320 450"
FEET_Y = 436
BUST_BOX = "24 0 200 200"  # square, for round portrait frames

SKIN = P.SKIN
HAIR = P.AMBER
MOUSTACHE = P.GINGER
LENS = P.LENS
OUTFITS = {
    # name: (top, rib/lapel, trousers, tie)
    "sweater": (P.SWEATER, P.SWEATER_RIB, P.TROUSERS, P.FIR),
    "suit": (P.SUIT, P.SUIT_DARK, P.SUIT_TROUSERS, P.FIR),
}
ARM_WIDTH = 20

# Front rig: shoulders and resting arms. An arm is (elbow, wrist, hand kind, hand turn).
FRONT_BACK_SHOULDER = (84, 208)
FRONT_NEAR_SHOULDER = (160, 208)
REST_BACK = ((70, 256), (76, 298), "relaxed", 0)
REST_NEAR = ((174, 256), (168, 298), "relaxed", 0)
# Side rig: both shoulders sit on the middle of the torso; the far arm is drawn behind it.
SIDE_FAR_SHOULDER = (130, 208)
SIDE_NEAR_SHOULDER = (120, 210)

# pose -> (rig, stance, back/far arm, near arm)
POSES = {
    "stand": ("front", "stand", REST_BACK, REST_NEAR),
    "point": ("front", "stand", REST_BACK, ((204, 244), (196, 184), "point", 0)),
    "present": ("front", "stand", REST_BACK, ((192, 252), (224, 232), "open", -20)),
    "welcome": ("front", "stand", ((52, 252), (20, 232), "open", 20), ((192, 252), (224, 232), "open", -20)),
    "think": ("front", "stand", REST_BACK, ((198, 260), (180, 206), "fist", -6)),
    "thumb": ("front", "stand", REST_BACK, ((198, 254), (202, 210), "thumb", 90)),
    "pointer": ("front", "stand", REST_BACK, ((198, 254), (228, 230), "fist", 26)),   # a pointer in his fist
    "explain": ("front", "stand", ((52, 254), (28, 240), "open", 10), ((204, 244), (196, 184), "point", 0)),
    "read": ("front", "stand", ((72, 268), (106, 272), "grip", 0), ((172, 268), (140, 274), "grip", 0)),
    "walk": ("side", "walk", ((152, 250), (170, 284), "relaxed", 0), ((104, 254), (94, 292), "relaxed", 0)),
    "sit": ("side", "sit", ((158, 258), (196, 266), "relaxed", 0), ((146, 264), (188, 274), "relaxed", 0)),
}
CENTER_X = 122          # the body axis: where the feet are centred
HEAD_TOP = 10           # y of the crown
MOUTH = (147, 164)          # where speech comes from, on the canvas: a bubble's tail points here
HOLD_Y = 300            # behind a poster he is drawn down to here; the poster covers everything below its top edge
PEEK_Y = 139            # an edge he looks over hides everything below: just under the nose
SCENE_SCALE = 1.0       # size next to the others when standing in a scene
HAND = SKIN             # color of the fingers that grip a poster
TALK_POSE = "point"     # full-figure pose used when speaking
QUOTE_POSES = ("point", "present", "think", "thumb")
RECAP_POSE = "read"      # how the character holds a summary
SEAT = "chair"          # where it sits in the study scene


def _shoe(x: float, y: float, turn: float = 0.0) -> str:
    """A brown shoe pointing right; (x, y) is the ankle."""
    g = Canvas()
    g.tube("M-20,18 L32,18", P.DARK_BROWN, 4.4, shaded=False)
    g.shape("M-22,15 C-24,3 -14,-4 0,-4 L8,-2 C22,2 35,7 35,14 Q35,16.5 30,16.5 L-19,16.5 "
            "Q-22,16.5 -22,15 Z", P.LEATHER, highlight="M17,5 Q26,7 29,11")
    g.line("M3,1 l6,4 M9,1 l-6,4", 1.4)
    return f'<g transform="translate({n(x)},{n(y)}) rotate({n(turn)})">{g.render()}</g>'


def _legs(c: Canvas, stance: str, trousers: str) -> None:
    leg = 34
    if stance == "walk":
        # Far leg trails behind with the heel lifting; near leg steps forward on its heel.
        c.add(_shoe(90, 410, 14))
        c.tube("M122,298 L94,412", trousers, leg, cap="butt")
        c.add(_shoe(160, 412, -10))
        c.tube("M124,298 L156,412", trousers, leg, cap="butt")
        c.line("M130,330 L152,400", 1.4)
    elif stance == "sit":
        # Far leg first, a little higher and further; thighs run forward, shins drop to the floor.
        for dx, dy in ((9, -5), (0, 0)):
            c.add(_shoe(204 + dx, 414 + dy))
            c.tube(f"M{198 + dx},{304 + dy} L{202 + dx},{416 + dy}", trousers, leg - 2, cap="butt")
            c.tube(f"M{116 + dx},{300 + dy} L{196 + dx},{302 + dy}", trousers, leg + 2)
        c.line("M184,290 q10,8 8,24", 1.4)
    else:
        c.add(_shoe(94, 414))
        c.add(_shoe(150, 414))
        c.tube("M104,298 L100,416", trousers, leg, cap="butt")
        c.tube("M140,298 L144,416", trousers, leg, cap="butt")
        c.line("M101,322 L98,410 M145,322 L148,410", 1.4)


def _torso(c: Canvas, rig: str, outfit: str) -> None:
    top, rib, _, tie = OUTFITS[outfit]
    c.path("M108,164 L134,164 L136,194 L106,194 Z", SKIN, 2.4)  # neck
    if rig == "side":
        # Profile: straight back on the left, chest and a slight belly on the right.
        torso = c.shape("M106,188 Q124,183 138,189 C149,195 154,214 154,238 L152,292 Q152,304 141,304 "
                        "L104,304 Q94,304 94,292 L96,214 C96,200 99,191 106,188 Z", top,
                        stipple=(132, 214, 22, 76, 26, "right"))
        c.add(f'<g clip-path="url(#{torso})"><path d="M88,290 H160 V308 H88 Z" fill="{rib}"/></g>')
        c.line("M95,290 H152", 2)
        if outfit == "sweater":
            c.line("M104,293 v9 M116,293 v9 M128,293 v9 M140,293 v9", 1.3)
        # Only the front edge of the collar and a sliver of tie show from the side.
        c.path("M130,186 L143,190 L145,205 L134,197 Z", P.WHITE, 2.2)
        c.path("M143,193 L149,198 L149,224 L144,218 Z", tie, 2)
        c.line("M134,197 Q150,206 152,232", 4.6, rib)
        return
    torso = c.shape("M92,188 Q121,181 150,188 C162,191 168,200 169,212 L172,292 Q172,304 160,304 "
                    "L84,304 Q72,304 72,292 L75,212 C76,200 82,191 92,188 Z", top,
                    stipple=(146, 212, 26, 78, 30, "right"))
    c.add(f'<g clip-path="url(#{torso})"><path d="M66,290 H178 V308 H66 Z" fill="{rib}"/></g>')
    c.line("M73,290 H171", 2)
    if outfit == "sweater":
        c.line("M84,293 v9 M96,293 v9 M108,293 v9 M120,293 v9 M132,293 v9 M144,293 v9 M156,293 v9", 1.3)
    # Shirt, tie and collar; the V sits right of centre because the chest is turned a little.
    c.path("M104,186 L124,230 L144,186 Z", P.WHITE, 2.3)
    c.shape("M119,192 L129,192 L132,216 L124,227 L116,216 Z", tie, light=(-2, -2), sw=2.1)
    c.path("M119,186 L129,186 L130,194 L118,194 Z", tie, 2.1)
    c.path("M104,186 L114,178 L123,192 L111,203 Z", P.WHITE, 2.3)
    c.path("M144,186 L134,178 L125,192 L137,203 Z", P.WHITE, 2.3)
    if outfit == "suit":
        c.path("M104,186 L124,236 L109,262 L91,220 Z", rib, 2.3)
        c.path("M144,186 L124,236 L139,262 L157,220 Z", rib, 2.3)
        c.dot(124, 264, 2.6)
        c.dot(124, 282, 2.6)
        c.path("M146,230 L160,228 L158,236 Z", P.WHITE, 1.8)
    else:
        c.line("M104,186 L124,230 L144,186", 5, rib)
        c.line("M101,188 L124,236 L147,188", 1.9)


def _head(c: Canvas, mood: str) -> None:
    # Skull: tall dome with the back of the head on the left and the face on the right.
    c.shape("M118,10 C86,10 70,52 70,98 C70,134 80,158 98,170 C110,178 134,180 146,173 "
            "C156,167 161,155 161,141 C163,122 164,104 161,88 C157,46 148,10 118,10 Z", SKIN,
            stipple=(122, 152, 36, 26, 18, "bottom"), highlight="M100,28 Q92,44 90,62")
    # Hair: a soft ginger curtain over the back of the head, ending in three locks at the collar.
    c.shape("M84,62 C70,62 60,84 59,112 C58,136 60,158 55,182 Q62,189 68,178 Q73,191 79,180 "
            "Q85,191 91,178 Q96,150 95,122 C95,98 94,72 84,62 Z", HAIR,
            stipple=(56, 120, 12, 56, 14, "left"))
    c.line("M70,96 Q67,136 68,172 M82,88 Q79,134 80,174", 1.4)
    c.line("M112,42 L130,41 M110,49 L131,48 M112,56 L128,55", 1.6)  # forehead wrinkles
    # Eyebrows float above the glasses.
    lift = -5 if mood == "surprise" else 0
    if mood == "worry":
        c.line("M108,84 Q117,78 126,82 M146,81 Q153,78 160,84", 2.3)
    else:
        c.line(f"M110,{83 + lift} Q118,{78 + lift} 126,{83 + lift}", 2.3)
        c.line(f"M147,{83 + lift} Q153,{78 + lift} 159,{83 + lift}", 2.3)
    # Glasses. Lenses are opaque so the outline of the face never shows through them;
    # the far lens is narrower because the head is turned.
    c.line("M101,103 L94,100", 3)
    c.path(rounded_rect_d(100, 92, 34, 28, 8), LENS, 3)
    c.path(rounded_rect_d(141, 92, 24, 28, 7), LENS, 3)
    c.line("M134,103 Q137.5,100 141,103", 3)
    # Eyes look the way he faces.
    big = 1.2 if mood == "surprise" else 1
    if mood == "wink":
        c.line("M111,108 Q118,113 125,108", 2.3)
    else:
        c.path(ellipse_d(119, 107, 4.6 * big, 6 * big), P.WHITE, 1.7)
        c.dot(120.8, 108, 2.6)
    c.path(ellipse_d(152, 107, 4 * big, 6 * big), P.WHITE, 1.7)
    c.dot(153.4, 108, 2.4)
    # Nose in profile: it grows out of the edge of the face, below the glasses.
    c.add(f'<path d="M156,121 C168,119 181,125 181,133 C181,141 170,145 158,142 Z" fill="{SKIN}"/>')
    c.line("M162,121 C172,119 181,125 181,133 C181,141 171,145 161,143", 2.5)
    # Moustache centred under the nose; its far half overhangs the edge of the face.
    c.shape("M151,143 C143,136 128,140 126,152 C135,160 146,157 151,150 C156,157 168,160 177,152 "
            "C175,140 160,136 151,143 Z", MOUSTACHE, light=(-2, -3))
    c.line("M136,150 l5,-4 M166,150 l-4,-4", 1.3)
    # Mouth: just under the middle of the moustache and well inside the chin.
    if mood in ("talk", "surprise"):
        c.path(ellipse_d(147, 164, 5.6, 4.6), P.MOUTH, 2)
    elif mood == "worry":
        c.line("M141,166 Q147,161 153,165", 2.1)
    else:
        c.line("M140,162 Q147,169 154,162", 2.1)


NECK = {"front": (122, 186), "side": (128, 188)}   # the hands turn their thumbs towards it


def hands(pose: str, grips: tuple[str, ...] = ()) -> dict[str, HandFrame]:
    """Where the hands of a pose are drawn (see `rig.HandFrame`): "left" is the back or far arm, "right" the near
    one; `grips` names the ones closed round a handle."""
    rig, _, back, near = POSES[pose]
    return {side: hand_frame(limb[0], limb[1], ARM_WIDTH, 0.9, limb[3], "hold" if side in grips else limb[2],
                             NECK[rig])
            for side, limb in (("left", back), ("right", near))}


def draw(pose: str = "stand", mood: str = "smile", outfit: str = "sweater", grips: tuple[str, ...] = ()) -> Canvas:
    """Draw the professor. See `POSES`, `MOODS` and `OUTFITS` for the options; `grips` closes those hands
    ("left" the back arm, "right" the near one) round a handle for `rig.hold`."""
    rig, stance, back, near = POSES[pose]
    top, rib, trousers, _ = OUTFITS[outfit]
    sleeve = dict(sleeve=top, width=ARM_WIDTH, skin=SKIN, cuff=P.WHITE if outfit == "suit" else rib,
                  hand_scale=0.9, toward=NECK[rig])
    bk = "hold" if "left" in grips else back[2]
    nk = "hold" if "right" in grips else near[2]
    c = Canvas()
    if rig == "side":
        arm(c, SIDE_FAR_SHOULDER, back[0], back[1], kind=bk, hand_turn=back[3], **sleeve)  # behind the body
        _legs(c, stance, trousers)
        _torso(c, rig, outfit)
        _head(c, mood)
        arm(c, SIDE_NEAR_SHOULDER, near[0], near[1], kind=nk, hand_turn=near[3], **sleeve)
        return c
    _legs(c, stance, trousers)
    _torso(c, rig, outfit)
    _head(c, mood)
    arm(c, FRONT_BACK_SHOULDER, back[0], back[1], kind=bk, hand_turn=back[3], **sleeve)
    if pose == "read":  # a sheet of paper held in both hands, under the near hand
        c.shape("M98,238 L152,234 L156,292 L102,296 Z", P.WHITE, 2.2, light=None)
        c.line("M107,249 L145,246 M108,259 L146,256 M109,269 L138,267 M109,279 L144,277", 1.3, opacity=0.55)
    arm(c, FRONT_NEAR_SHOULDER, near[0], near[1], kind=nk, hand_turn=near[3], **sleeve)
    return c

"""The Agent: a small, brand-new orange robot with a screen for a face and a terminal prompt on its chest.

It stands for the AI coding agent the book is about. Drawn facing the viewer
on a 220 x 280 canvas, feet on y = 266. Its mood shows on the screen. In `stride` it walks to the right, turned
side-on: the barrel narrower, its head turned the way it goes - the screen towards the right, the far ear hidden.
"""
from __future__ import annotations

from .. import design as P
from .ink import Canvas, ellipse_d, n, uid
from .rig import HandFrame, arm, fingers, hand, hand_frame

SIZE = (220, 280)
VIEW_BOX = "-40 0 300 280"
FEET_Y = 266
BUST_BOX = "28 -2 164 164"  # square, for round portrait frames

SHELL = P.ORANGE
SHELL_DARK = P.ORANGE_DARK
METAL = P.METAL
GLOVE = P.METAL_PALE
SCREEN = P.SCREEN_DARK
GLOW = P.GLOW

# The arms join the barrel at its sides, each on a ball joint, never out of its front.
BODY = ("M82,133 Q110,126 138,132 Q149,150 146,180 Q147,203 132,208 Q110,213 90,208 "
        "Q73,204 74,178 Q71,150 82,133 Z")
SHOULDER_L = (78, 147)
SHOULDER_R = (143, 147)
NECK = (110, 128)           # the hands turn their thumbs towards it
REST_L = ((60, 176), (62, 204), "relaxed", 0)
REST_R = ((160, 176), (158, 204), "relaxed", 0)
# pose -> (legs, left arm, right arm); an arm is (elbow, wrist, hand kind, hand turn)
POSES = {
    "stand": ("stand", REST_L, REST_R),
    "wave": ("stand", REST_L, ((170, 152), (182, 114), "open", 0)),
    "point": ("stand", REST_L, ((170, 162), (198, 154), "point", 0)),
    "present": ("stand", REST_L, ((168, 170), (196, 152), "open", -15)),
    "think": ("stand", REST_L, ((176, 176), (156, 136), "fist", -10)),
    "cheer": ("stand", ((50, 152), (38, 114), "open", 0), ((170, 152), (182, 114), "open", 0)),
    "shrug": ("stand", ((54, 172), (36, 156), "open", 40), ((166, 172), (184, 156), "open", -40)),
    "walk": ("walk", ((58, 170), (50, 196), "relaxed", 0), ((162, 172), (172, 196), "relaxed", 0)),
    # walking to the right: the far arm swings back behind the barrel, the near one forward
    "stride": ("stride", ((84, 172), (72, 196), "relaxed", 8), ((140, 170), (156, 192), "relaxed", 0)),
    "carry": ("walk", ((54, 194), (66, 194), "hold", 0), ((166, 194), (154, 194), "hold", 0)),
    "read": ("stand", ((56, 188), (68, 188), "hold", 0), ((164, 188), (152, 188), "hold", 0)),
    "type": ("stand", ((62, 186), (84, 208), "relaxed", 0), ((158, 186), (136, 208), "relaxed", 0)),
}
# Arms whose hands work in front of the body; the others hang or reach out at its sides.
FRONT = {"think": ("right",), "type": ("left", "right")}
CENTER_X = 110
HEAD_TOP = 5
MOUTH = (111, 96)          # where speech comes from, on the canvas: a bubble's tail points here
PEEK_Y = 92            # an edge the character looks over hides everything below: across the screen, under the eyes
SCENE_SCALE = 0.92
HAND = GLOVE
TALK_POSE = "present"
QUOTE_POSES = ("present", "wave", "think", "read")
RECAP_POSE = "read"


def _boot(c: Canvas, x: float, y: float, size: float = 1.0) -> None:
    """A lumpy rubber boot; the two are never quite the same size."""
    w, h = 19 * size, 17 * size
    c.shape(f"M{n(x - w)},{n(y + 8)} Q{n(x - w - 2)},{n(y - h * 0.5)} {n(x - 4)},{n(y - h * 0.55)} "
            f"Q{n(x + w + 3)},{n(y - h * 0.5)} {n(x + w)},{n(y + 8)} Q{n(x)},{n(y + 11)} {n(x - w)},{n(y + 8)} Z",
            SHELL_DARK, light=(-3, -3))
    c.line(f"M{n(x - w * 0.5)},{n(y + 3)} q{n(w * 0.5)},3 {n(w)},0", 1.5)


def _legs(c: Canvas, stance: str) -> None:
    if stance == "stride":
        # mid-stride to the right, in three-quarter view: the far leg ahead, planted on its heel; the near leg
        # behind, its knee a little bent, the boot pushing off on its toe
        c.tube("M118,202 Q124,224 132,248", METAL, 11)
        _boot(c, 136, 256, 0.92)
        c.tube("M104,202 Q102,226 94,236 Q88,242 88,248", METAL, 11)
        c.place(_tilted_boot(), "translate(86,256) rotate(18)")
    elif stance == "walk":
        c.tube("M98,202 Q88,224 84,246", METAL, 11)
        _boot(c, 80, 256, 1.05)
        c.tube("M122,202 Q134,220 138,240", METAL, 11)
        _boot(c, 142, 250, 0.92)
    else:
        c.tube("M96,202 Q92,226 95,248", METAL, 11)
        c.tube("M124,202 Q129,226 125,248", METAL, 11)
        _boot(c, 92, 258, 1.05)
        _boot(c, 129, 258, 0.92)


def _tilted_boot() -> Canvas:
    """A boot lifting off on its toe, drawn at the origin, to be turned."""
    g = Canvas()
    _boot(g, 0, 0, 1.0)
    return g


def _face(c: Canvas, mood: str) -> None:
    """Eyes and mouth glow on the dark screen; they are drawn by hand, so nothing is quite even."""
    glow = f'fill="{GLOW}"'
    stroke = f'fill="none" stroke="{GLOW}" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"'
    if mood == "surprise":
        c.add(f'<ellipse cx="92" cy="73" rx="9" ry="10" {glow}/><ellipse cx="129" cy="71" rx="8" ry="9" {glow}/>')
        c.add(f'<ellipse cx="111" cy="96" rx="5" ry="6" {stroke}/>')
    elif mood == "worry":
        c.add(f'<path d="M83,75 Q91,68 100,67 M137,74 Q129,67 121,66" {stroke}/>')
        c.add(f'<path d="M95,99 q6,-8 14,-1 q7,7 15,-1" {stroke}/>')
    else:
        if mood == "wink":
            c.add(f'<path d="M84,75 Q92,65 101,74" {stroke}/>')
        else:
            c.add(f'<path d="M92,63 Q99,62 99,72 Q100,83 92,83 Q85,83 85,72 Q85,63 92,63 Z" {glow}/>')
        c.add(f'<path d="M129,61 Q136,61 136,70 Q136,81 128,81 Q122,80 122,70 Q122,61 129,61 Z" {glow}/>')
        if mood == "talk":
            c.add(f'<path d="M100,92 Q111,89 121,92 Q123,101 111,102 Q99,102 100,92 Z" {glow}/>')
        else:
            c.add(f'<path d="M97,92 Q109,106 124,91" {stroke}/>')


TURN = "translate(124,0) scale(.84,1) translate(-110,0)"   # turned to the right: shifted, narrower


def _head(mood: str, turned: bool = False) -> Canvas:
    """The head on its own canvas, so the whole thing can sit at a slight tilt. `turned`: towards the right - the
    shell, the screen and the face set narrower and further right, the far ear hidden behind the shell."""
    c = Canvas()
    if turned:
        _head_turned(c, mood)
        return c
    _head_parts(c, mood)
    return c


def _head_turned(c: Canvas, mood: str) -> None:
    """The head in three-quarter view, turned to the right: the antenna, the near ear, the shell's near side face
    in shade, its front face, the screen a turned quad - its near edge taller than its far one - and the face on it
    shifted towards the far side, the far eye narrower, the mouth foreshortened."""
    c.line("M114,36 q-7,-9 1,-14 q8,-5 3,-11", 4.6, METAL)
    c.line("M114,36 q-7,-9 1,-14 q8,-5 3,-11", 1.7)
    c.shape("M111,9 Q112,2 119,2 Q126,3 125,10 Q124,16 117,16 Q111,15 111,9 Z", P.YELLOW, light=(-2, -2))
    c.shape("M58,70 Q48,68 47,80 Q46,94 56,96 L61,94 Z", METAL, light=(-2, -2))              # the near ear
    c.line("M50,78 h7 M50,86 h7", 1.4)
    c.shape("M80,38 Q64,42 59,60 Q54,90 61,112 Q66,121 80,124 Q74,88 80,38 Z", SHELL_DARK, light=None)
    c.shape("M80,38 Q112,30 150,36 Q164,48 163,80 Q166,106 152,117 Q120,127 80,124 Q74,88 80,38 Z", SHELL,
            highlight="M86,50 Q82,66 83,84")
    c.line("M136,38 Q148,42 154,54", 2.6, P.WHITE, 0.45)
    c.path("M90,54 Q120,46 148,56 Q155,80 149,102 Q120,112 90,110 Q83,82 90,54 Z", SCREEN, 2.5)   # the screen
    c.line("M95,60 Q92,72 93,84", 2.2, P.WHITE, 0.25)
    glow = f'fill="{GLOW}"'
    stroke = f'fill="none" stroke="{GLOW}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"'
    if mood == "surprise":
        c.add(f'<ellipse cx="111" cy="73" rx="8" ry="10" {glow}/><ellipse cx="136" cy="72" rx="5.5" ry="8.5" {glow}/>')
        c.add(f'<ellipse cx="126" cy="96" rx="3.6" ry="5.4" {stroke}/>')
    elif mood == "worry":
        c.add(f'<path d="M103,75 Q110,68 118,67 M142,74 Q137,68 131,67" {stroke}/>')
        c.add(f'<path d="M112,99 q5,-7 11,-1 q5,6 11,-1" {stroke}/>')
    else:
        if mood == "wink":
            c.add(f'<path d="M103,75 Q110,66 118,74" {stroke}/>')
        else:
            c.add(f'<path d="M110,63 Q117,62 117,72 Q118,83 110,83 Q103,83 103,72 Q103,63 110,63 Z" {glow}/>')
        c.add(f'<path d="M137,62 Q142,62 142,71 Q142,81 137,81 Q132,80 132,71 Q132,62 137,62 Z" {glow}/>')
        if mood == "talk":
            c.add(f'<path d="M115,92 Q125,89 134,92 Q135,100 125,101 Q115,101 115,92 Z" {glow}/>')
        else:
            c.add(f'<path d="M113,92 Q123,104 136,90" {stroke}/>')


def _head_parts(c: Canvas, mood: str, far_ear: bool = True) -> None:
    """The antenna, the ears, the shell, the screen and the face."""
    # A bent antenna with a wobbly lamp.
    c.line("M108,36 q-7,-9 1,-14 q8,-5 3,-11", 4.6, METAL)
    c.line("M108,36 q-7,-9 1,-14 q8,-5 3,-11", 1.7)
    c.shape("M105,9 Q106,2 113,2 Q120,3 119,10 Q118,16 111,16 Q105,15 105,9 Z", P.YELLOW, light=(-2, -2))
    # Ears: two mismatched bolts.
    c.shape("M60,68 Q50,66 49,78 Q48,92 58,94 L63,92 Z", METAL, light=(-2, -2))
    if far_ear:
        c.shape("M160,66 Q171,66 172,76 Q173,89 163,92 L158,90 Z", METAL, light=(-2, -2))
        c.line("M163,74 h6 M163,82 h6", 1.4)
    c.line("M52,76 h7 M52,84 h7", 1.4)
    # The shell: a soft hand-drawn box - no two corners alike, but fresh from the factory.
    c.shape("M66,44 Q84,31 112,34 Q146,31 159,44 Q168,60 165,84 Q167,110 154,118 Q130,126 104,123 "
            "Q72,126 62,112 Q54,92 58,70 Q57,52 66,44 Z", SHELL, highlight="M70,54 Q65,68 65,86")
    c.line("M140,40 Q152,44 157,56", 2.6, P.WHITE, 0.45)     # a second glint: new paint
    # The screen, cut a little crooked.
    c.path("M77,55 Q96,46 124,49 Q146,47 149,60 Q153,84 146,102 Q140,111 112,109 Q84,113 76,102 "
           "Q69,80 77,55 Z", SCREEN, 2.5)
    c.line("M82,60 Q79,72 80,84", 2.2, P.WHITE, 0.25)
    _face(c, mood)


LIMB = dict(sleeve=METAL, width=9, skin=GLOVE, hand_scale=0.82, toward=NECK)


def hands(pose: str, grips: tuple[str, ...] = ()) -> dict[str, HandFrame]:
    """Where the hands of a pose are drawn (see `rig.HandFrame`); `grips` names the ones closed round a handle."""
    _, left, right = POSES[pose]
    return {side: hand_frame(limb[0], limb[1], LIMB["width"], LIMB["hand_scale"], limb[3],
                             "hold" if side in grips else limb[2], NECK)
            for side, limb in (("left", left), ("right", right))}


def _joint(c: Canvas, x: float, y: float) -> None:
    """A ball joint on the side of the barrel, where an arm is plugged in."""
    c.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="7" fill="{METAL}" stroke="{P.INK}" stroke-width="2.2"/>'
          f'<circle cx="{n(x - 1.5)}" cy="{n(y - 1.5)}" r="2" fill="{P.METAL_PALE}"/>')


def _held(c: Canvas, pose: str, held: str, frames: dict[str, HandFrame]) -> None:
    """What the hands hold in `carry` and `read`, between the two grips; the fingers close over its edges."""
    (lx, ly), (rx, ry) = frames["left"].grip, frames["right"].grip
    left, right, y = lx - 4, rx + 4, (ly + ry) / 2
    mid = (left + right) / 2
    if pose == "carry" and held == "crate":  # a wooden crate of apples carried by its ends
        top = y - 30
        c.shape(f"M{n(left)},{n(top)} H{n(right)} V{n(y + 8)} H{n(left)} Z", P.WOOD, sw=2.2, light=(-2, -2))
        c.line(f"M{n(left)},{n(top + 13)} H{n(right)} M{n(left)},{n(top + 26)} H{n(right)}", 1.4, P.WOOD_DARK)
        for i, ax in enumerate(_spread(left + 9, right - 9, 5)):
            c.shape(ellipse_d(ax, top - 3, 7.5, 7), P.RED if i % 3 else P.GREEN, sw=1.8, light=(-1.5, -1.5))
    elif pose == "carry":  # a slipping stack of folders carried by its ends
        for i, (color, tilt) in enumerate(((P.YELLOW, -2), (P.TEAL, 3), (P.PINK, -4))):
            top = y - 4 - i * 13
            c.add(f'<g transform="rotate({tilt} {n(mid)} {n(top)})">')
            c.shape(f"M{n(left)},{n(top)} H{n(left + 14)} L{n(left + 18)},{n(top - 4)} H{n(right)} V{n(top + 11)} "
                    f"H{n(left)} Z", color, sw=2.2, light=(-2, -2))
            c.add("</g>")
    elif held == "old":  # a dusty binder, a puff of dust rising from it
        c.add(f'<g transform="rotate(-3 {n(mid)} {n(y)})">')
        c.shape(f"M{n(left)},{n(y - 34)} H{n(right)} V{n(y + 28)} H{n(left)} Z", P.STONE, 2.2, light=(-2, -2),
                shade_k=0.86, stipple=(left, y - 34, right - left, 62, 70, "even"))
        c.shape(f"M{n(mid - 10)},{n(y - 26)} H{n(mid + 26)} V{n(y - 10)} H{n(mid - 10)} Z", P.CARD, 1.6, light=None)
        c.line(f"M{n(mid - 6)},{n(y - 20)} h26 M{n(mid - 6)},{n(y - 15)} h18", 1.1, opacity=0.5)
        c.line(f"M{n(left)},{n(y - 34)} l18,0 M{n(left)},{n(y - 34)} l0,16 M{n(left)},{n(y - 22)} q8,-2 12,-12",
               0.9, opacity=0.7)
        c.add("</g>")
        for x, yy, r in ((88, 140, 7), (100, 132, 9), (118, 136, 6), (132, 128, 8), (146, 138, 5)):
            c.add(f'<circle cx="{x}" cy="{yy}" r="{r}" fill="{P.STONE}" fill-opacity=".55"/>')
    else:  # a sheet of instructions, held a little askew by its sides
        c.add(f'<g transform="rotate(-3 {n(mid)} {n(y)})">')
        c.shape(f"M{n(left)},{n(y - 30)} H{n(right)} V{n(y + 26)} H{n(left)} Z", P.WHITE, 2.2, light=None)
        c.line(" ".join(f"M{n(left + 10)},{n(y - 18 + i * 10)} H{n(right - 10 - (12 if i == 2 else 0))}"
                        for i in range(4)), 1.4, opacity=0.5)
        c.add("</g>")
    for f in frames.values():
        fingers(c, f, GLOVE)


def _spread(a: float, b: float, count: int) -> list[float]:
    return [a + (b - a) * i / (count - 1) for i in range(count)]


def draw(pose: str = "stand", mood: str = "smile", held: str = "sheet", wear: str = "",
         grips: tuple[str, ...] = ()) -> Canvas:
    """Draw the Agent. See `POSES` and `MOODS` for the options.

    `held` is what it reads in the `read` pose: a clean `sheet`, or an `old` module - a grey binder thick with
    dust, taken off the bottom shelf (the chapter 1 opener); in the `carry` pose a `crate` of apples instead of the
    stack of folders (the farewell's fields). `wear="harness"` puts on braces and a
    tool belt with a wrench: the agent trying on a harness at the fair (the chapter 2 opener). `grips` closes
    those hands ("left", "right") round a handle for `rig.hold` (see `characters.draw(hold=...)`)."""
    stance, left, right = POSES[pose]
    if stance == "stride":
        return _stride(pose, mood, grips, left, right)
    front = FRONT.get(pose, ())
    c = Canvas()
    _legs(c, stance)
    # Body: a soft barrel, wider at the hips, with the terminal prompt on a crooked chest plate.
    c.path("M101,118 Q110,121 121,118 L122,136 L100,136 Z", METAL, 2.2)
    c.shape(BODY, SHELL, highlight="M82,146 Q79,160 80,176")
    c.shape("M89,145 Q110,140 131,142 Q134,158 132,174 Q112,179 91,177 Q87,160 89,145 Z", P.CREAM, sw=2.2,
            light=(-2, -2), shade_k=0.9)
    c.line("M97,152 l9,8 l-10,8 M111,169 h13", 3.2, SCREEN)
    for x, y, color in ((96, 192, P.RED), (110, 194, P.YELLOW), (124, 191, P.GREEN)):
        c.add(f'<circle cx="{x}" cy="{y}" r="3.6" fill="{color}" stroke="{P.INK}" stroke-width="1.5"/>')
    c.place(_head(mood), "rotate(-3 110 84)")
    if wear == "harness":
        for x0, x1 in ((84, 88), (136, 132)):
            c.line(f"M{x0},134 Q{(x0 + x1) / 2 + (2 if x0 < 100 else -2)},170 {x1},198", 7, P.LEATHER)
            c.line(f"M{x0 - 3},134 Q{(x0 + x1) / 2 - 1},170 {x1 - 3},198 M{x0 + 3},134 Q{(x0 + x1) / 2 + 3},170 "
                   f"{x1 + 3},198", 1.1)
        c.shape("M72,194 Q110,202 148,194 L148,206 Q110,214 72,206 Z", P.LEATHER, 2, light=None)
        c.shape("M102,195 H118 V211 H102 Z", P.SUN, 1.8, light=None)
        c.line("M106,203 h8", 1.6)
        c.line("M140,206 L146,232", 4, P.METAL_DARK)
        c.add(f'<circle cx="147" cy="236" r="5" fill="none" stroke="{P.METAL_DARK}" stroke-width="3.4"/>')
    outside = uid()
    c.add(f'<clipPath id="{outside}"><path clip-rule="evenodd" d="M-400,-400 H700 V800 H-400 Z {BODY}"/>'
          "</clipPath>")
    frames = hands(pose, grips)
    for side, shoulder, limb in (("left", SHOULDER_L, left), ("right", SHOULDER_R, right)):
        kind = "hold" if side in grips else limb[2]
        if side in front:
            arm(c, shoulder, limb[0], limb[1], kind=kind, hand_turn=limb[3], **LIMB)
        else:   # an arm at the side: only what is outside the barrel shows, then the hand whole
            c.add(f'<g clip-path="url(#{outside})">')
            arm(c, shoulder, limb[0], limb[1], kind=kind, hand_turn=limb[3], **LIMB)
            c.add("</g>")
            f = frames[side]
            hand(c, f.x, f.y, f.rotation, GLOVE, kind, f.scale, mirror=f.mirror)
        _joint(c, *shoulder)
    if pose in ("carry", "read"):
        _held(c, pose, held, frames)
    return c


SIDE = "translate(114,0) scale(.9,1) translate(-110,0)"       # the barrel turned three-quarter: a little narrower


def _stride(pose: str, mood: str, grips: tuple[str, ...], left: tuple, right: tuple) -> Canvas:
    """Walking to the right in three-quarter view: the far arm (its right) behind the barrel swinging forward, the
    legs one ahead and one behind, the barrel turned with its chest plate towards the right, the head turned the
    way it goes with the shell's near side showing, the near arm (its left) in front swinging back."""
    c = Canvas()
    near = (90, 148)
    far = (136, 146)
    kl = "hold" if "left" in grips else left[2]
    kr = "hold" if "right" in grips else right[2]
    arm(c, far, right[0], right[1], kind=kr, hand_turn=right[3], **LIMB)             # behind the barrel
    _legs(c, "stride")
    c.path("M103,118 Q112,121 123,118 L124,136 L102,136 Z", METAL, 2.2)
    b = Canvas()
    b.shape(BODY, SHELL, highlight="M82,146 Q79,160 80,176")
    c.place(b, SIDE)
    plate = Canvas()
    plate.shape("M89,145 Q110,140 131,142 Q134,158 132,174 Q112,179 91,177 Q87,160 89,145 Z", P.CREAM, sw=2.2,
                light=(-2, -2), shade_k=0.9)
    plate.line("M97,152 l9,8 l-10,8 M111,169 h13", 3.2, SCREEN)
    for x, y, color in ((96, 192, P.RED), (110, 194, P.YELLOW), (124, 191, P.GREEN)):
        plate.add(f'<circle cx="{x}" cy="{y}" r="3.6" fill="{color}" stroke="{P.INK}" stroke-width="1.5"/>')
    c.place(plate, "translate(122,0) scale(.8,1) translate(-110,0)")
    c.place(_head(mood, turned=True), "rotate(2 110 84)")
    arm(c, near, left[0], left[1], kind=kl, hand_turn=left[3], **LIMB)               # in front, swinging back
    _joint(c, *near)
    return c

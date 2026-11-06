"""Body parts shared by the characters: hands, arms, and the grip by which a hand holds a thing.

Holding things: it must be clear how a book lies in a hand or how a tool is held, never crooked. A hand that holds
something closes round it in three layers, back to front: the back of the fist with the thumb
(`hand(..., kind="hold")`), the thing itself, then the curled fingers over it (`fingers`). So the fingers visibly
close over a handle or an edge and the thumb is behind it.

The geometry of a drawn hand is a `HandFrame`: where its wrist is, which way it points, its scale and whether it is
mirrored (a hand always turns its thumb towards the body, see `hand_frame`). In a frame's own units the wrist is at
the origin and the fingers point along +x; the fist closes round `GRIP`.

A thing held is drawn in the *grip frame*: the origin is the middle of the fist, +x runs along the forearm (from
the wrist out through the knuckles), and the handle or edge that is gripped runs along the y axis; -y is the
thumb's side, which a character's hand turns towards its head when the arm is raised or held out, so "up" in a
prop's drawing is up in the picture for the usual poses. The prop therefore turns with the forearm. A prop is any
`make(x, y, k) -> svg` that draws itself with its grip at (x, y), `k` being the holder's height over 100 (the same
makers `Stage.hold` takes); `handheld.py` has ready ones whose handles sit where the fist closes.

    frame = hand_frame(elbow, wrist, width, hand_scale, hand_turn, toward=neck)   # pure geometry
    arm(c, shoulder, elbow, wrist, ..., kind="hold", toward=neck)                  # draws the back of the fist
    hold(c, frame, skin, make, k, turn=0)                                          # the thing, then the fingers

A character module exposes `hands(pose) -> {"left": HandFrame, "right": HandFrame}` and closes the hands named in
`draw(..., grips=(...))`; `characters.draw(name, pose, hold={"right": make})` puts it all together, and
`Stage.hold` (openers and footer strips) puts a thing into the hand of a character already standing.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .. import design as P
from .ink import Canvas, angle_of, ellipse_d, n, polar

GRIP = (13.0, 0.0)          # the middle of the closed fist in a hand's own units: a handle passes here


def pose_hands(limbs: dict[str, tuple], width: float, scale: float, toward: tuple[float, float],
               grips: tuple[str, ...] = ()) -> dict[str, HandFrame]:
    """The hands of a pose, {side: (elbow, wrist, kind, turn)} -> {side: HandFrame}; the hands named in `grips` are
    closed round a handle. Every character's `hands()` is this with its own arm width, hand scale and neck."""
    return {side: hand_frame(limb[0], limb[1], width, scale, limb[3], "hold" if side in grips else limb[2], toward)
            for side, limb in limbs.items()}


@dataclass(frozen=True)
class HandFrame:
    """Where a hand is drawn: wrist at (x, y), pointing along `rotation` degrees, at `scale`, maybe mirrored
    (the thumb then on the +y side of its own units instead of -y)."""
    x: float
    y: float
    rotation: float
    scale: float
    mirror: bool = False

    @property
    def transform(self) -> str:
        flip = " scale(1,-1)" if self.mirror else ""
        return f"translate({n(self.x)},{n(self.y)}) rotate({n(self.rotation)}) scale({n(self.scale)}){flip}"

    def point(self, lx: float, ly: float) -> tuple[float, float]:
        """A point given in the hand's own units, on the canvas the hand is drawn on."""
        ly = -ly if self.mirror else ly
        a = math.radians(self.rotation)
        sx, sy = lx * self.scale, ly * self.scale
        return self.x + sx * math.cos(a) - sy * math.sin(a), self.y + sx * math.sin(a) + sy * math.cos(a)

    @property
    def grip(self) -> tuple[float, float]:
        """The middle of the fist: where a held handle passes."""
        return self.point(*GRIP)

    @property
    def grip_transform(self) -> str:
        """The transform into the grip frame (origin in the fist, +x along the forearm, -y the thumb's side)."""
        gx, gy = self.grip
        flip = " scale(1,-1)" if self.mirror else ""
        return f"translate({n(gx)},{n(gy)}) rotate({n(self.rotation)}){flip}"


def hand(c: Canvas, x: float, y: float, rotation: float, color: str, kind: str = "relaxed",
         scale: float = 1.0, finger: float = 6.6, mirror: bool = False) -> None:
    """Draw a four-fingered cartoon hand of a `kind`: relaxed, open, point, thumb, fist, grip or hold.

    The wrist sits at (x, y) and the hand extends along `rotation` (degrees); `mirror` puts the thumb on the
    other side. Fingers are capsules merged with the palm into one outlined silhouette. `hold` is the back half of
    a fist closed round a handle - the palm and the thumb; `fingers` draws the front half over what it holds.
    """
    g = Canvas()
    palm = ("p", ellipse_d(10, 0, 10.5, 9.6))
    if kind == "open":
        pieces = [("s", "M5,-6 L8,-18", finger), ("s", "M14,-5 L27,-13", finger),
                  ("s", "M17,0 L31,-1", finger), ("s", "M14,6 L26,11", finger), palm]
        g.union(pieces, color, 2.2)
    elif kind == "point":
        pieces = [("s", "M12,-5 L35,-7", finger), ("s", "M4,-5 L4,-15", finger - 0.4), palm]
        g.union(pieces, color, 2.2)
        g.line("M13,0 Q19,0 18,3 M12,5 Q18,5 17,8", 1.6)
    elif kind == "thumb":
        pieces = [("s", "M8,-5 L7,-21", finger + 0.6), palm]
        g.union(pieces, color, 2.2)
        g.line("M12,-3 L19,-3 M12,2 L19,2 M11,6.500 L17,6.500", 1.6)
    elif kind == "grip":
        pieces = [("s", "M5,-6 L12,-13", finger - 0.6), palm]
        g.union(pieces, color, 2.2)
        g.line("M10,-5 Q20,-6 19,-1 M10,0 Q20,-1 19,4 M10,5 Q18,5 17,8", 1.6)
    elif kind == "hold":   # the back of a fist round a handle: palm and the thumb wrapped over the far side
        g.union([("s", "M6,-5 Q12,-12 18,-10", finger - 0.8), palm], color, 2.2)
    elif kind == "fist":
        g.union([palm], color, 2.2)
        g.line("M13,-4 L19,-4 M13,1 L20,1 M12,5.500 L18,5.500", 1.6)
    else:  # relaxed: fingers together, thumb apart
        pieces = [("s", "M6,-6 L14,-12", finger - 0.6), ("s", "M14,-3 L24,-3", finger),
                  ("s", "M14,3 L23,4", finger), palm]
        g.union(pieces, color, 2.2)
        g.line("M15,0 L23,0.500", 1.5)
    c.place(g, HandFrame(x, y, rotation, scale, mirror).transform)


def fingers(c: Canvas, frame: HandFrame, color: str) -> None:
    """The front half of a fist closed round a handle: four curled fingers lying across it, their knuckles
    towards the end of the hand, drawn over whatever the hand holds."""
    g = Canvas()
    pieces = [("s", f"M{x0},{y} L{x1},{y}", w) for x0, x1, y, w in
              ((8, 18.5, -6.2, 5.6), (7.5, 20, -1.6, 5.9), (7.5, 19.5, 3, 5.9), (8.5, 17.5, 7.2, 5.2))]
    g.union(pieces, color, 2)
    g.line("M9,-3.9 L18,-3.9 M8.5,0.7 L19,0.7 M9,5.2 L17.5,5.2", 1.3)
    c.place(g, frame.transform)


def hand_frame(elbow: tuple[float, float], wrist: tuple[float, float], width: float, hand_scale: float = 1.0,
               hand_turn: float = 0.0, kind: str = "relaxed",
               toward: tuple[float, float] | None = None) -> HandFrame:
    """Where `arm` draws the hand of an arm whose forearm runs from `elbow` to `wrist`, `width` thick.

    `toward` is a point of the body (the neck): the hand is mirrored when that turns its thumb towards it - a
    hanging hand's thumb to the thigh, a raised one's to the head - so the two hands of a figure are a left and a
    right, never the same hand twice. A thumbs-up keeps its thumb up."""
    (ex, ey), (wx, wy) = elbow, wrist
    direction = angle_of(ex, ey, wx, wy)
    hx, hy = polar(wx, wy, direction, width * 0.42)
    rotation = direction + hand_turn
    mirror = False
    if toward is not None and kind != "thumb":
        a = math.radians(rotation)
        thumb = (math.sin(a), -math.cos(a))          # the hand's -y, where an unmirrored thumb is
        mirror = thumb[0] * (toward[0] - hx) + thumb[1] * (toward[1] - hy) < 0
    return HandFrame(hx, hy, rotation, hand_scale, mirror)


def arm(c: Canvas, shoulder: tuple[float, float], elbow: tuple[float, float], wrist: tuple[float, float],
        sleeve: str, width: float, skin: str, kind: str = "relaxed", cuff: str | None = None,
        hand_scale: float = 1.0, hand_turn: float = 0.0, toward: tuple[float, float] | None = None) -> HandFrame:
    """Draw an arm from shoulder through elbow to wrist, then the hand; return the hand's frame.

    The elbow is the control point of a quadratic curve, so the limb bends smoothly. `cuff` paints a band of
    that color at the wrist. `toward` turns the thumb to the body (see `hand_frame`).
    """
    (sx, sy), (ex, ey), (wx, wy) = shoulder, elbow, wrist
    c.tube(f"M{n(sx)},{n(sy)} Q{n(ex)},{n(ey)} {n(wx)},{n(wy)}", sleeve, width)
    direction = angle_of(ex, ey, wx, wy)
    if cuff:
        cx, cy = polar(wx, wy, direction, width * 0.22)
        c.add(f'<g transform="translate({n(cx)},{n(cy)}) rotate({n(direction)})">'
              f'<rect x="-4" y="{n(-width / 2 - 1.5)}" width="9" height="{n(width + 3)}" rx="3" '
              f'fill="{cuff}" stroke="{P.INK}" stroke-width="2.2"/></g>')
    frame = hand_frame(elbow, wrist, width, hand_scale, hand_turn, kind, toward)
    hand(c, frame.x, frame.y, frame.rotation, skin, kind, hand_scale, mirror=frame.mirror)
    return frame


def hold(c: Canvas, frame: HandFrame, skin: str, make, k: float, turn: float = 0.0) -> None:
    """Put a thing into a hand already drawn with `kind="hold"`: `make(0, 0, k)` is drawn in the grip frame
    (turned a further `turn` degrees about the fist), then the fingers close over it.

    A maker with `grasp = "palm"` (a stopwatch) is not gripped by a handle but lies in the palm: it is drawn
    upright, its middle over the palm (`make(x, y, k)` then puts its middle at (x, y)), turned by `turn` alone;
    the fingers curl round its rim on the far side and the thumb comes over to press the button at its top.
    Such a maker gives `radius` (of its case) and `top` (how far above its middle the button is), in its units."""
    if getattr(make, "grasp", "fist") == "palm":
        _palm_hold(c, frame, skin, make, k, turn)
        return
    rotate = f" rotate({n(turn)})" if turn else ""
    c.add(f'<g transform="{frame.grip_transform}{rotate}">{make(0, 0, k)}</g>')
    fingers(c, frame, skin)


def _palm_hold(c: Canvas, frame: HandFrame, skin: str, make, k: float, turn: float) -> None:
    """A thing lying in the palm, as a stopwatch is held: upright in the hand, dial to the viewer, the palm behind
    it, the fingertips curled over its rim on the side away from the wrist, the thumb coming up the other side to
    press the button on top. Upright whatever way the forearm points, so the fingers never cover the dial."""
    cx, cy = frame.point(12, 0)
    radius, top = make.radius * k, make.top * k
    rotate = f' transform="rotate({n(turn)} {n(cx)} {n(cy)})"' if turn else ""
    c.add(f"<g{rotate}>{make(cx, cy, k)}</g>")
    s = frame.scale
    away = 1 if cx >= frame.x else -1               # the fingers reach round the side away from the wrist
    tips = []
    for spread in (-16, 8, 32, 56):                 # four fingertips over the rim, from its side down round its foot
        a = math.radians(spread if away > 0 else 180 - spread)
        r0, r1 = radius - 2.4 * s, radius + 3.6 * s
        tips.append(("s", f"M{n(cx + math.cos(a) * r1)},{n(cy + math.sin(a) * r1)} "
                          f"L{n(cx + math.cos(a) * r0)},{n(cy + math.sin(a) * r0)}", 5.4 * s))
    g = Canvas()
    g.union(tips, skin, 2 * s)
    c.add(g.render())
    # the thumb: from the heel of the hand on the wrist's side, up outside the case, its tip on the button
    bx, by = cx - away * radius * 0.8, cy + radius * 0.45
    mx, my = cx - away * (radius + 5 * s), cy - radius * 0.35
    tx, ty = cx - away * 1.2 * s, cy - top + 1.2 * s
    c.union([("s", f"M{n(bx)},{n(by)} Q{n(mx)},{n(my)} {n(tx)},{n(ty)}", 6 * s)], skin, 2 * s)

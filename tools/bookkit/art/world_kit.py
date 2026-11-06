"""The kit every chapter world draws with: containers, ports and lines, lettering in tags, and the checks.

Two rules hold in every world, and `tests/test_world_kit.py` holds every registered world to them - every station at
every beat, height and side, the finale and the opener: content inside a block never sticks to the block, and
every line, rope or cable is attached properly at both ends:

* containers - a board, a plate, a panel, a screen, a tag - are drawn by `Pen.container` from their size, with an
  inner padding of 8 % of the smaller side and never under `PAD_MIN`; whatever goes inside is placed in the inner
  box and recorded (`Pen.child`), and a label is set in a tag of its own (`Pen.tag`); parts side by side inside
  one container keep `GAP_MIN` of air;
* cables, tubes, rods, paper and beams are drawn only by `connect` between two declared `Port`s: the line leaves
  each port along its direction, goes into the object through its `fitting` (a boot, a collar and clamp), bends
  smoothly at every corner (`curves.py`), and passes through nothing but the two things it joins.

`container_faults` and `link_faults` list what breaks them on a drawn stage. Units: 840 across the page.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .. import design as P
from ..design import darken, lighten
from . import props, sets
from .characters import module as char_module
from .curves import eased_d, eased_points
from .ink import INK, Canvas, lettering, lettering_width, n, rounded_rect_d
from .openers import W, Box
from .scenes import PROFESSOR_HEIGHT

if TYPE_CHECKING:
    from .footers import Strip

PAD_SHARE = 0.08     # a container's inner padding: this share of its smaller side ...
PAD_MIN = 3.0        # ... and never less than this, in page units
GAP_MIN = 3.0        # sibling parts inside one object keep at least this much air between them, in page units

GLASS = lighten(P.SKY, 0.45)   # a glass tube's fill
# The characters in a world frame, over the professor's height: big enough to read on the page.
SIZE = {"professor": 1.08, "agent": 1.4, "cat": 1.2, "caterpillar": 1.4, "sparrow": 1.6}   # big enough to read


@dataclass
class Holder:
    """A container as drawn: its outer box, the inner box its content must keep to, and that content's boxes."""
    name: str
    outer: tuple[float, float, float, float]
    inner: tuple[float, float, float, float]
    children: list[tuple[str, tuple[float, float, float, float]]] = field(default_factory=list)


@dataclass(frozen=True)
class Port:
    """A point on an object's outline where a line may be attached, and the way the line must leave it: (dx, dy)
    points out of the object. `owner` is the object's group."""
    x: float
    y: float
    dx: float
    dy: float
    owner: str


@dataclass
class Link:
    """A drawn connection: its two ports and the points along it (for the checks)."""
    a: Port
    b: Port
    kind: str
    points: list[tuple[float, float]]                 # along the drawn curve
    controls: list[tuple[float, float]] = field(default_factory=list)   # the polygon it is drawn from
    width: float = 0.0                                # how thick it is drawn


def ledger(stage) -> tuple[list[Holder], list[Link]]:
    """The containers and connections drawn on a stage so far (a footer strip or an opener)."""
    if not hasattr(stage, "holders"):
        stage.holders, stage.links, stage.ports = [], [], []
    return stage.holders, stage.links


def port(stage, x: float, y: float, dx: float, dy: float, owner: str) -> Port:
    """Declare a port on an object of the stage: the only kind of point a line may start or end at."""
    ledger(stage)
    length = math.hypot(dx, dy) or 1
    made = Port(x, y, dx / length, dy / length, owner)
    stage.ports.append(made)
    return made


def text_box(x: float, y: float, text: str, size: float, style: str = "sign") -> tuple[float, float, float, float]:
    """Where a line of lettering set by `lettering` (centred at x, baseline y) puts its ink, rim included."""
    w = lettering_width(text, size, style) + size * 0.2
    return (x - w / 2, y - size * 0.82, x + w / 2, y + size * 0.26)


def letter(k: float, least: float) -> float:
    """The size of lettering drawn at scale k that still reads on the page: never under `least` in its units."""
    return max(least, (sets.LETTERING_MIN + 0.5) / k)


def _tag_pad(tw: float, th: float, size: float, k: float) -> float:
    return max(PAD_MIN / k, PAD_SHARE * min(tw, th), size * 0.32)


def tag_size(text: str, size: float, k: float = 1.0, style: str = "sign") -> tuple[float, float]:
    """The width and height of a tag holding `text` (as `Pen.tag` draws it), in the units it is drawn in."""
    x0, t, r, b = text_box(0, 0, text, size, style)
    pad = _tag_pad(r - x0, b - t, size, k)
    return r - x0 + 2 * pad, b - t + 2 * pad


def wrap(inner: float, k: float = 1.0) -> float:
    """How big a container must be, along one side, to hold `inner` of content inside its padding."""
    return max((inner + 2) / (1 - 2 * PAD_SHARE), inner + 2 * PAD_MIN / k + 2)


class Pen:
    """Drawing in local units placed at (x, y) on the stage at scale k: the drawing goes into one `<g>`, while
    containers and ports are worked out in page units and recorded in the stage's ledger."""

    def __init__(self, stage, x: float, y: float, k: float) -> None:
        self.stage, self.x, self.y, self.k = stage, x, y, k
        self.c = Canvas()

    def at(self, lx: float, ly: float) -> tuple[float, float]:
        return self.x + lx * self.k, self.y + ly * self.k

    def box(self, left: float, t: float, r: float, b: float) -> tuple[float, float, float, float]:
        (x0, y0), (x1, y1) = self.at(left, t), self.at(r, b)
        return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))

    def port(self, lx: float, ly: float, dx: float, dy: float, owner: str) -> Port:
        x, y = self.at(lx, ly)
        return port(self.stage, x, y, dx, dy, owner)

    def pad(self, w: float, h: float) -> float:
        """A container's inner padding at this scale, in its own units."""
        return max(PAD_MIN / self.k, PAD_SHARE * min(w, h))

    def container(self, name: str, left: float, t: float, w: float, h: float, fill: str, radius: float = 4,
                  sw: float = 2.2, light: tuple | None = (-2, -2), shade_k: float = 0.86) -> Holder:
        """Draw a board, plate or panel and return it with its inner box (in page units) for the content."""
        pad = self.pad(w, h)
        self.c.shape(rounded_rect_d(left, t, w, h, radius), fill, sw=sw, light=light, shade_k=shade_k)
        holder = Holder(name, self.box(left, t, left + w, t + h),
                        self.box(left + pad, t + pad, left + w - pad, t + h - pad))
        ledger(self.stage)[0].append(holder)
        return holder

    def child(self, holder: Holder, name: str, left: float, t: float, r: float, b: float) -> None:
        """Record a part drawn inside a container (in local units), for the checks."""
        holder.children.append((name, self.box(left, t, r, b)))

    def tag(self, name: str, cx: float, cy: float, text: str, size: float, fill: str = P.CARD, ink: str = INK,
            style: str = "sign", inside: Holder | None = None, outline: str = INK) -> Holder:
        """A label in a tag of its own, centred on (cx, cy): the tag is sized from its text plus padding."""
        x0, t, r, b = text_box(0, 0, text, size, style)
        pad = _tag_pad(r - x0, b - t, size, self.k)
        w, h = r - x0 + 2 * pad, b - t + 2 * pad
        left, top = cx - w / 2, cy - h / 2
        self.c.shape(rounded_rect_d(left, top, w, h, min(h * 0.3, 4)), fill, sw=1.5, light=None)
        if outline != INK:
            self.c.add(f'<rect x="{n(left)}" y="{n(top)}" width="{n(w)}" height="{n(h)}" rx="{n(min(h * 0.3, 4))}" '
                       f'fill="none" stroke="{outline}" stroke-width="2.2"/>')
        base = top + pad - t
        self.c.add(lettering(cx, base, text, size, ink, style=style))
        holder = Holder(name, self.box(left, top, left + w, top + h), self.box(left + pad, top + pad, left + w - pad,
                                                                              top + h - pad))
        holder.children.append(("text", self.box(cx + x0, base + t, cx + r, base + b)))
        ledger(self.stage)[0].append(holder)
        if inside is not None:
            inside.children.append((name, holder.outer))
        return holder

    def svg(self) -> str:
        return f'<g transform="translate({n(self.x)},{n(self.y)}) scale({n(self.k)})">{self.c.render()}</g>'


def path_points(points: list[tuple[float, float]], keep_start: float = 0.0,
                keep_end: float = 0.0) -> list[tuple[float, float]]:
    """Points along the line drawn through the polygon `points` (see `curves`), every few units."""
    return eased_points(points, keep_start, keep_end, step=3.0)


def route(a: Port, b: Port, width: float, via: tuple[tuple[float, float], ...] = (),
          lead: float | tuple[float, float] | None = None) -> list[tuple[float, float]]:
    """The polygon `connect` lays a line along: out of each port along its direction for `lead` (one length, or
    one for each end) - long enough by default for the fitting and a wide bend after it - then through `via`."""
    span = math.hypot(b.x - a.x, b.y - a.y)
    if lead is None:
        lead = min(max(width * 8, span * 0.3), max(90.0, width * 8))
    la, lb = lead if isinstance(lead, tuple) else (lead, lead)
    if abs(a.dx * b.dx + a.dy * b.dy + 1) < 1e-6 and not via and abs(a.dx * (b.y - a.y) - a.dy * (b.x - a.x)) < 1e-6:
        return [(a.x, a.y), (b.x, b.y)]                       # facing ports on one line: a straight run
    return [(a.x, a.y), (a.x + a.dx * la, a.y + a.dy * la), *via, (b.x + b.dx * lb, b.y + b.dy * lb), (b.x, b.y)]


def fitting_length(kind: str, width: float) -> float:
    """How far a line's fitting reaches out of its port: the line runs straight that far."""
    return {"cable": width * 2.2, "tube": width * 1.5, "rod": max(3.0, width * 0.45),
            "paper": width * 0.8}.get(kind, 0.0)                    # paper: straight out of its slot


def fitting(c: Canvas, p: Port, kind: str, width: float, color: str | None = None) -> None:
    """Where a line goes into an object, drawn as part of it and coaxial with the line: a cable through a rubber
    strain-relief boot that tapers from the object's face to the cable's own thickness, ribbed; a tube or hose in a
    collar on the face and a clamp round it with its screw; a rod in a plain collar."""
    ang = math.degrees(math.atan2(p.dy, p.dx))
    length = fitting_length(kind, width)
    g = Canvas()
    if kind == "cable":
        base, tip = width * 0.95, width * 0.62           # half-widths at the face and where it meets the cable
        g.shape(f"M0,{n(-base)} C{n(length * 0.45)},{n(-base)} {n(length * 0.55)},{n(-tip)} {n(length)},{n(-tip)} "
                f"V{n(tip)} C{n(length * 0.55)},{n(tip)} {n(length * 0.45)},{n(base)} 0,{n(base)} Z",
                color or P.CHARCOAL, sw=1.3, light=None)
        for f in (0.3, 0.55):                             # its ribs
            half = base + (tip - base) * f
            g.line(f"M{n(length * f)},{n(-half * 0.8)} V{n(half * 0.8)}", 0.9, P.METAL_DARK, 0.9)
    elif kind == "tube":
        g.add(f'<rect x="0" y="{n(-width * 0.82)}" width="{n(width * 0.5)}" height="{n(width * 1.64)}" rx="1.2" '
              f'fill="{P.METAL}" stroke="{INK}" stroke-width="1.2"/>')
        cx = width * 0.85
        g.add(f'<rect x="{n(cx)}" y="{n(-width * 0.66)}" width="{n(width * 0.4)}" height="{n(width * 1.32)}" '
              f'rx="1" fill="{P.METAL_LIGHT}" stroke="{INK}" stroke-width="1.1"/>')
        g.dot(cx + width * 0.2, -width * 0.66, max(0.9, width * 0.12), P.METAL_DARK)   # the clamp's screw
    elif kind == "rod":
        cw = width * 1.5
        g.add(f'<rect x="0" y="{n(-cw / 2)}" width="{n(length)}" height="{n(cw)}" rx="1.2" fill="{P.METAL}" '
              f'stroke="{INK}" stroke-width="1.2"/>')
    c.add(f'<g transform="translate({n(p.x)},{n(p.y)}) rotate({n(ang)})">{g.render()}</g>')


def connect(stage, a: Port, b: Port, kind: str, width: float, via: tuple[tuple[float, float], ...] = (),
            depth: float = 1.5, color: str | None = None, lead: float | tuple[float, float] | None = None,
            fits: tuple[bool, bool] = (True, True)) -> None:
    """Draw a line between two ports - and only so: it leaves each port along its direction (`lead` long), passes
    through the `via` points, bends smoothly at every corner (`curves`) and goes into each object through its
    fitting - unless `fits` says that end has none (a cable paying out of a reel's coil). `kind`: tube (glass),
    cable, rod, paper, beam."""
    keep_a, keep_b = ((fitting_length(kind, width) + width * 0.25) if fit else 0.0 for fit in fits)
    if lead is not None:                                  # a lead always outruns its fitting, so it can bend after it
        la, lb = lead if isinstance(lead, tuple) else (lead, lead)
        lead = (max(la, keep_a + width * 2), max(lb, keep_b + width * 2))
    points = route(a, b, width, via, lead)
    d = eased_d(points, keep_a, keep_b)
    c = Canvas()
    if kind == "beam":
        c.add(f'<path d="{d}" fill="none" stroke="{color or P.SUN}" stroke-width="{n(width)}" '
              f'stroke-dasharray="{n(width * 3)} {n(width * 2)}" stroke-linecap="round"/>')
    else:
        fill = color or {"tube": GLASS, "cable": P.CHARCOAL, "rod": P.METAL_DARK, "paper": P.CARD}[kind]
        c.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{n(width + 3.4)}" stroke-linejoin="round" '
              f'stroke-linecap="butt"/><path d="{d}" fill="none" stroke="{fill}" stroke-width="{n(width)}" '
              f'stroke-linejoin="round" stroke-linecap="butt"/>')
        if kind == "tube":
            c.add(f'<path d="{d}" fill="none" stroke="{P.WHITE}" stroke-width="{n(max(1.0, width * 0.16))}" '
                  f'stroke-opacity=".7" transform="translate({n(-width * 0.18)},{n(-width * 0.18)})"/>')
        if kind == "cable":                               # the sheen along a round cable
            sheen = lighten(fill, 0.45)
            c.add(f'<path d="{d}" fill="none" stroke="{sheen}" stroke-width="{n(max(0.8, width * 0.22))}" '
                  f'stroke-opacity=".55" transform="translate({n(-width * 0.16)},{n(-width * 0.16)})"/>')
        if kind == "paper":
            c.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{n(width * 0.4)}" stroke-opacity=".35" '
                  f'stroke-dasharray="{n(width * 0.15)} {n(width * 0.35)}"/>')
        for p, fit in zip((a, b), fits, strict=True):
            if fit:
                fitting(c, p, kind, width)
    stage.put(depth, c.render(), None)
    ledger(stage)[1].append(Link(a, b, kind, path_points(points, keep_a, keep_b), points, width))


def clear_path(stage, points: list[tuple[float, float]], owners: set[str]) -> bool:
    """Whether a line along `points` would pass through nothing on the stage but its `owners` - nor through an
    area the stage keeps clear (a title, a bubble)."""
    zones = [(b.left, b.top, b.right, b.bottom) for b in stage.boxes if b.group not in owners and b.name not in owners]
    zones += list(stage.reserved)
    for left, top, right, bottom in zones:
        for x, y in path_points(points):
            if left + 1 < x < right - 1 and top + 1 < y < bottom - 1:
                return False
    return True


# ============================================================================ the room and the cast
class Room:
    """The place a frame shows: its ceiling (0 in a low strip, lower in a tall frame, the rest is what is above
    it), its wall and floor, and `u`, the scale of fittings drawn for a 300-unit wall. A world subclasses it to add
    its machine's own heights."""

    def __init__(self, s: Strip) -> None:
        self.floor = s.base
        inner = min(s.base, s.tall * 1.6 + 40)
        self.ceil = max(0.0, s.base - inner)                       # 0 in a strip; lower in a tall frame
        self.wall = self.floor - self.ceil
        self.u = max(0.5, min(1.25, self.wall / 300))
        self.k = s.unit
        self.top = self.ceil + 14 * self.u


def room(s: Strip, kind: type[Room] = Room) -> Room:
    """The frame's room as a world measures it (`kind`), worked out once per frame."""
    made = getattr(s, "_room", None)
    if not isinstance(made, kind):
        made = s._room = kind(s)
    return made


def cast(s: Strip, name: str, frac: float, pose: str, mood: str = "smile", flip: bool = False,
         mark: str | None = None) -> Box:
    """A character at its readable size (`SIZE`), facing the way it is told: toward the action."""
    return s.cast(name, frac, pose, mood, flip=flip, mark=mark, size=SIZE[name])


def frac_of(s: Strip, x: float) -> float:
    """The fraction across the strip's usable width that puts something at x."""
    return (x - s.lo) / (s.hi - s.lo)


def height_of(name: str, s: Strip) -> float:
    mod = char_module(name)
    return (mod.FEET_Y - mod.HEAD_TOP) * s.tall * SIZE[name] / PROFESSOR_HEIGHT * mod.SCENE_SCALE


# ============================================================================ effects
def motion(x: float, y: float, length: float, k: float, way: int = 1, vertical: bool = False) -> str:
    """Speed lines trailing behind something moving (`way` +1 right or down, -1 left or up)."""
    c = Canvas()
    for i, d in enumerate((-5, 0, 5)):
        start = 22 * k + i * 4 * k
        run = length * k * (1 - i * 0.2)
        if vertical:
            c.line(f"M{n(x + d * k)},{n(y - way * start)} v{n(-way * run)}", 1.6, INK, 0.65)
        else:
            c.line(f"M{n(x - way * start)},{n(y + d * k)} h{n(-way * run)}", 1.6, INK, 0.65)
    return c.render()


def puff(x: float, y: float, k: float) -> str:
    c = Canvas()
    for dx, dy, r in ((-8, 2, 6), (0, -4, 7.5), (9, 1, 6), (2, 6, 5)):
        c.add(f'<circle cx="{n(x + dx * k)}" cy="{n(y + dy * k)}" r="{n(r * k)}" fill="{P.WHITE}" stroke="{INK}" '
              f'stroke-width="1.1"/>')
    return c.render()


def burst(x: float, y: float, k: float) -> str:
    """A small burst of sparks."""
    c = Canvas()
    for a in range(0, 360, 45):
        rad = math.radians(a + 10)
        c.line(f"M{n(x + math.cos(rad) * 5 * k)},{n(y + math.sin(rad) * 5 * k)} "
               f"L{n(x + math.cos(rad) * 12 * k)},{n(y + math.sin(rad) * 12 * k)}", max(1.4, 2 * k), P.SUN)
    c.add(f'<path d="{props._burst_d(6, 3, 8)}" transform="translate({n(x)},{n(y)}) scale({n(k)})" '
          f'fill="{P.YELLOW_PALE}" stroke="{INK}" stroke-width="1"/>')
    return c.render()


def sound(s: Strip, x: float, y: float, text: str, size: float, group: str | None = None,
          margin: float = 24) -> None:
    """A sound word in comic lettering, at (x, y) or nearby, where it overlaps nothing but the thing that makes
    the sound (`group`), `margin` clear of the frame's sides."""
    w = lettering_width(text, size)
    for dx, dy in ((0, 0), (0, -size), (-w * 0.6, -size * 0.5), (w * 0.6, -size * 0.5), (0, size)):
        box = (x + dx - w / 2, y + dy - size, x + dx + w / 2, y + dy + size * 0.3)
        if box[1] < 2 or box[0] < margin or box[2] > W - margin:
            continue
        if any(b.group != group and b.hits(box, 3) for b in s.boxes):
            continue
        if any(Box(*zone, "", "").hits(box) for zone in s.reserved):
            continue
        if any(box[0] - 3 < px < box[2] + 3 and box[1] - 3 < py < box[3] + 3      # never over a cable or a tube
               for link in getattr(s, "links", []) for px, py in link.points):
            continue
        s.put(8, lettering(x + dx, y + dy, text, size, P.SUN, turn=-6), box, "sound", group=group)
        return


# ============================================================================ the checks
def container_faults(stage, eps: float = 0.6) -> list[str]:
    """Every container on the stage whose padding is short, whose content leaves its inner box, or whose parts
    side by side come closer than `GAP_MIN`."""
    found = []
    for holder in getattr(stage, "holders", []):
        ol, ot, orr, ob = holder.outer
        il, it, ir, ib = holder.inner
        need = max(PAD_MIN, PAD_SHARE * min(orr - ol, ob - ot)) - eps
        if min(il - ol, it - ot, orr - ir, ob - ib) < need:
            found.append(f"{holder.name}: padding under {need + eps:.1f}")
        for name, child in holder.children:
            if not (child[0] >= il - eps and child[1] >= it - eps and child[2] <= ir + eps and child[3] <= ib + eps):
                found.append(f"{holder.name}: {name} leaves the inner box")
        for i, (name_a, a) in enumerate(holder.children):
            for name_b, b in holder.children[i + 1:]:
                gap = max(b[0] - a[2], a[0] - b[2], b[1] - a[3], a[1] - b[3])
                if gap < GAP_MIN - eps:
                    found.append(f"{holder.name}: {name_a} and {name_b} {gap:.1f} apart")
    return found


def link_faults(stage) -> list[str]:
    """Every line on the stage that does not start and end on a declared port, leaves a port askew, or passes
    through anything but the two things it joins (a character included, unless it holds the line's end)."""
    found = []
    ports = getattr(stage, "ports", [])
    for link in getattr(stage, "links", []):
        for end, point in ((link.a, link.points[0]), (link.b, link.points[-1])):
            if end not in ports:
                found.append(f"{link.kind}: an undeclared port")
            elif math.hypot(point[0] - end.x, point[1] - end.y) > 1e-6:
                found.append(f"{link.kind}: an end off its port")
        for end, nxt in ((link.a, link.controls[1]), (link.b, link.controls[-2])):
            vx, vy = nxt[0] - end.x, nxt[1] - end.y
            length = math.hypot(vx, vy)
            if length > 1e-6 and (vx * end.dx + vy * end.dy) / length <= 0.99:
                found.append(f"{link.kind} from {end.owner}: leaves askew")
        owners = {link.a.owner, link.b.owner}
        for box in stage.boxes:
            if box.group in owners or box.name in owners:
                continue
            if any(box.left + 1 < x < box.right - 1 and box.top + 1 < y < box.bottom - 1 for x, y in link.points):
                found.append(f"{link.kind} {link.a.owner}->{link.b.owner}: passes through {box.name}")
    return found


# ============================================================================ easter eggs
# The hunt (easter eggs for readers to find): every chapter world hides
# one golden 3.5" floppy in one of its frames, each with one letter on its label; read in chapter order the
# letters spell a word. The letters live in the locale (`easter: floppies:`). A world says where its floppy lies
# with `hide(world, station, beat)`, and that station's drawing offers a spot with `stash(...)`: the floppy is
# drawn there only in the one frame the camera schedule picks (`worlds.egg_page`).
FLOPPY_K = 1.3       # a floppy is 20 x 21 units at scale 1: 26 x 27 on the page, about 6.5 mm
CLOCK_TIME = (4, 4)  # every wall clock in the worlds shows 4:04 - never explained (an easter egg too)


def hide(world_, station: str, beat: str) -> None:
    """Declare where a world's golden floppy lies: on the first page showing `station` at `beat` (or, when the
    chapter is too short for that beat, on the station's first page). The station's drawing calls `stash`."""
    keys = [one.key for one in world_.stations]
    if station not in keys or beat not in world_.stations[keys.index(station)].beats:
        raise ValueError(f"world {world_.name!r} has no station {station!r} with a beat {beat!r}")
    world_.floppy = (station, beat)


def floppy_size(k: float = FLOPPY_K) -> tuple[float, float]:
    return 20 * k, 21 * k


def floppy(x: float, y: float, k: float, letter_: str, turn: float = 0.0) -> str:
    """A golden 3.5" floppy standing on its bottom edge, its middle at x and its foot at y: the gold body with one
    corner bevelled, the metal shutter at the top with its slot and the spindle window, the paper label with one big
    letter, the write-protect notch at a lower corner, a soft sparkle on the upper corner. `turn` leans it."""
    c = Canvas()
    gold, edge = P.GOLD, darken(P.GOLD, 0.72)
    c.add(f'<path d="M-10,-21 H8 L10,-19 V-1 Q10,0 9,0 H-9 Q-10,0 -10,-1 Z" fill="{gold}" stroke="{INK}" '
          f'stroke-width="1"/>')                                               # the body, its bevelled corner
    c.add(f'<path d="M-8.6,-1.2 H8.6 V-3" fill="none" stroke="{edge}" stroke-width=".8"/>')   # the shade below
    c.add(f'<rect x="-5" y="-21" width="10.5" height="8" fill="{P.METAL_LIGHT}" stroke="{INK}" '
          f'stroke-width=".8"/>')                                              # the metal shutter
    c.add(f'<rect x="1.4" y="-19.6" width="2.6" height="5.2" rx=".4" fill="{P.CHARCOAL}"/>')   # its slot
    c.add(f'<rect x="-8.3" y="-11.4" width="16.6" height="9.6" rx="1" fill="{P.CARD}" stroke="{INK}" '
          f'stroke-width=".7"/>')                                              # the label
    c.add(f'<rect x="-9.3" y="-4.6" width="1.6" height="1.8" fill="{P.CHARCOAL}"/>')   # the write-protect notch
    if letter_ == ".":                                                    # a full stop: a dot that reads as one
        c.add(f'<circle cx="0" cy="-5" r="1.9" fill="{INK}"/>')
    else:
        c.add(lettering(0, -3.6, letter_, 8.4, INK, style="label"))
    c.add(f'<path d="M-6.5,-20.5 l.9,-2.4 l.9,2.4 l2.4,.9 l-2.4,.9 l-.9,2.4 l-.9,-2.4 l-2.4,-.9 Z" '
          f'fill="{P.GOLD_LIGHT}" stroke="{edge}" stroke-width=".4"/>')        # the sparkle
    c.add(f'<path d="M-9,-19 V-13" stroke="{P.GOLD_LIGHT}" stroke-width="1.1" stroke-linecap="round"/>')   # the shine
    rot = f" rotate({n(turn)})" if turn else ""
    return f'<g transform="translate({n(x)},{n(y)}){rot} scale({n(k)})">{c.render()}</g>'


def floppy_box(x: float, y: float, k: float = FLOPPY_K) -> tuple[float, float, float, float]:
    w, h = floppy_size(k)
    return (x - w / 2 - 1, y - h - 3 * k, x + w / 2 + 1, y)        # the sparkle reaches over the top


def stash(s, x: float, y: float, depth: float, group: str | None = None, holder: Holder | None = None,
          k: float = FLOPPY_K, turn: float = 0.0, air: float = 3.0) -> tuple[float, float, float, float] | None:
    """Offer a spot for the world's golden floppy - its foot's middle at (x, y) on whatever it lies on (`group`,
    which it may touch; `holder`, the container it lies in). Drawn only in the frame that carries the egg
    (`s.egg`, its letter), and only where it is free and whole in the frame; returns its box when drawn."""
    letter_ = getattr(s, "egg", None)
    if not letter_ or getattr(s, "eggs", None):
        return None
    box = floppy_box(x, y, k)
    if box[0] < 2 or box[1] < 2 or box[2] > W - 2 or box[3] > s.h - 2:
        return None
    if any(b.group != group and b.name != group and b.hits(box, air) for b in s.boxes):
        return None
    if any(Box(*zone, "", "").hits(box) for zone in s.reserved):
        return None
    if holder is not None:
        il, it, ir, ib = holder.inner
        if box[0] < il or box[2] > ir or box[1] < it or box[3] > ib + 0.5:
            return None
        if any(max(c_[0] - box[2], box[0] - c_[2], c_[1] - box[3], box[1] - c_[3]) < GAP_MIN
               for _, c_ in holder.children):
            return None
        holder.children.append(("floppy", box))
    s.put(depth, floppy(x, y, k, letter_, turn), box, "floppy", group=group or "floppy")
    s.eggs = [letter_]
    return box


def clock_hands(cx: float, cy: float, hour: float, minute: float, width: float, color: str = INK,
                minute_color: str | None = None, time: tuple[int, int] = CLOCK_TIME) -> str:
    """The two hands of a wall clock at (cx, cy), `hour` and `minute` long, set to `time` (4:04 in every world):
    the hour hand a little past its hour, the minute hand on its minute. Marked with the time it shows, for the
    test that every clock keeps it."""
    h, m = time
    ah = math.radians(((h % 12) + m / 60) * 30 - 90)
    am = math.radians(m * 6 - 90)
    return (f'<g data-clock="{h}:{m:02d}"><path d="M{n(cx)},{n(cy)} L{n(cx + math.cos(ah) * hour)},'
            f'{n(cy + math.sin(ah) * hour)}" stroke="{color}" stroke-width="{n(width * 1.4)}" '
            f'stroke-linecap="round"/><path d="M{n(cx)},{n(cy)} L{n(cx + math.cos(am) * minute)},'
            f'{n(cy + math.sin(am) * minute)}" stroke="{minute_color or color}" stroke-width="{n(width)}" '
            f'stroke-linecap="round"/></g>')


def stash_along(s, xs, y: float, depth: float, group: str | None = None, turn: float = 0.0,
                k: float = FLOPPY_K) -> tuple[float, float, float, float] | None:
    """`stash` on a surface at height y (a worktop, a shelf board, the floor), at the first of `xs` that is free."""
    for x in xs:
        box = stash(s, x, y, depth, group=group, turn=turn, k=k)
        if box:
            return box
    return None


# The book inside the book: the professor's own handbook lying flat on a shelf or a bench, its spine to the
# viewer, the title whole on a label in three lines at the smallest lettering that reads (never squeezed).
TOME_SIZE = sets.LETTERING_MIN       # its lettering, in page units


def tome_size(title: str, size: float = TOME_SIZE) -> tuple[float, float]:
    """The width and height of the lying book's spine (with the top of its board) for `title`, in page units."""
    lines = title.split()
    lw = max(lettering_width(line, size, "label") for line in lines)
    return lw + 30, len(lines) * size * 1.15 + 16


def tome(x: float, foot: float, title: str, color: str, size: float = TOME_SIZE) -> str:
    """A thick book lying flat, its spine to the viewer, its middle at x and its bottom on `foot`: the top of its
    board seen over the spine, the spine with gilt bands at both ends, the title on a cream label, word by word."""
    lines = title.split()
    w, h = tome_size(title, size)
    c = Canvas()
    left, top = x - w / 2, foot - h + 5
    c.add(f'<path d="M{n(left + 1)},{n(top)} L{n(left + 6)},{n(top - 5)} H{n(left + w + 3)} L{n(left + w - 1)},'
          f'{n(top)} Z" fill="{lighten(color, 0.25)}" stroke="{INK}" stroke-width="1.1" stroke-linejoin="round"/>')
    c.shape(rounded_rect_d(left, top, w, h - 5, 3), color, sw=1.4, light=(-1, -1), shade_k=0.85)
    for bx in (left + 5, left + 9, left + w - 9, left + w - 5):                       # the gilt bands
        c.add(f'<rect x="{n(bx - 1)}" y="{n(top + 1.5)}" width="2" height="{n(h - 8)}" fill="{P.GOLD}"/>')
    lw = w - 30
    c.add(f'<rect x="{n(x - lw / 2 - 3)}" y="{n(top + 3)}" width="{n(lw + 6)}" height="{n(h - 11)}" rx="1.5" '
          f'fill="{P.CREAM}" stroke="{INK}" stroke-width=".8"/>')
    for i, line in enumerate(lines):
        c.add(lettering(x, top + 4 + size * 1.15 * (i + 1) - size * 0.22, line, size, INK, style="label"))
    return c.render()

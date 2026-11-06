"""A cobbled country road in one-point perspective that comes towards the viewer from a far gate, bends, and runs
across the foreground - the road the five take to the computer city (the farewell page and the conclusion's finale).

A straight road of flat slabs reads as a staircase, not a road. So the road is laid out on the ground plane and
projected: the camera stands at height 1 over the ground, looking along +Z; a ground point (X, Z) lands on the page
at (vx + X * f / Z, hz + f / Z). The road's middle line runs from the gate (X = 0, far off) straight towards the
viewer, turns on a circular arc and runs off across the page at one depth. Everything on it is laid in ground units
and projected, so it shrinks with distance by itself: setts in courses across the road with their joints staggered,
each stone with its light top edge and its shaded foot; kerbs as long smooth strips along both edges, a gutter of
shade inside them; a soft grass verge outside.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from .. import design as P
from ..design import darken, lighten, mix
from .ink import INK, Canvas, n


def m(value: float) -> str:
    """A coordinate to a tenth of a unit (a fortieth of a millimetre): enough for stones, light for the page."""
    text = f"{value:.1f}".rstrip("0").rstrip(".")
    return text or "0"


STEP = 0.02                    # the middle line is sampled every this much ground


@dataclass
class Road:
    vx: float                  # the vanishing point on the page
    hz: float
    f: float                   # the focal length: page units per ground unit at depth 1
    half: float                # half the road's width, in ground units
    gate_z: float              # where the road begins far off, at X = 0
    near_z: float              # the depth of the crosswise stretch's middle line
    end_x: float               # where the bend ends and the crosswise stretch begins
    radius: float              # the bend's radius at the middle line
    left_x: float              # how far the crosswise stretch runs (to the page's edge and beyond)
    kerb: float = 0.07         # the kerbs' width
    verge: float = 0.16        # the grass verge's width beyond the kerb
    course: float = 0.1        # a course of setts, along the road
    across: int = 8            # setts across the road
    line: list[tuple[float, float, float, float]] = field(default_factory=list)   # (X, Z, tx, tz) along the middle

    def __post_init__(self) -> None:
        self.line = self._middle(STEP)

    # ----------------------------------------------------------------- geometry
    def page(self, x: float, z: float) -> tuple[float, float]:
        return self.vx + x * self.f / z, self.hz + self.f / z

    def _middle(self, step: float = 0.02) -> list[tuple[float, float, float, float]]:
        """The middle line, sampled every `step` of ground: the straight from the gate, the arc, the crosswise run."""
        cx, cz, r = self.end_x, self.near_z + self.radius, self.radius

        def miss(t: float) -> float:                    # the straight from the gate must meet the arc on its tangent
            sx, sz = cx + r * math.cos(t), cz + r * math.sin(t)
            dx, dz = sx, sz - self.gate_z
            return dx * (-math.cos(t)) - dz * math.sin(t)

        lo, hi = 0.0, math.pi / 2 - 1e-6
        for _ in range(60):
            mid = (lo + hi) / 2
            if (miss(lo) > 0) == (miss(mid) > 0):
                lo = mid
            else:
                hi = mid
        t0 = (lo + hi) / 2
        sx, sz = cx + r * math.cos(t0), cz + r * math.sin(t0)
        out = []
        length = math.hypot(sx, sz - self.gate_z)
        tx, tz = sx / length, (sz - self.gate_z) / length
        d = 0.0
        while d < length:                               # far off, coarser: a far stone is a speck anyway
            z = self.gate_z + tz * d
            out.append((tx * d, z, tx, tz))
            d += step * max(1.0, z / 4)
        arc = int(r * (t0 + math.pi / 2) / step) + 1
        for i in range(arc + 1):
            t = t0 - (t0 + math.pi / 2) * i / arc
            out.append((cx + r * math.cos(t), cz + r * math.sin(t), math.sin(t), -math.cos(t)))
        x = self.end_x
        while x > self.left_x:
            x -= step
            out.append((x, self.near_z, -1.0, 0.0))
        return out

    def at(self, i: int, u: float) -> tuple[float, float]:
        """The ground point `u` across from the middle line's i-th sample (u > 0 to the right of the way to the
        viewer, i.e. towards the outside of the bend)."""
        x, z, tx, tz = self.line[i]
        return x - tz * u, z + tx * u

    def strip(self, u0: float, u1: float, i0: int = 0, i1: int | None = None) -> str:
        """A band along the road between offsets u0 and u1, as a page path."""
        i1 = len(self.line) - 1 if i1 is None else i1
        ids = self._ids(i0, i1)
        a = [self.page(*self.at(i, u0)) for i in ids]
        b = [self.page(*self.at(i, u1)) for i in reversed(ids)]
        return "M" + " L".join(f"{m(x)},{m(y)}" for x, y in a + b) + " Z"

    def _ids(self, i0: int, i1: int, every: int = 3) -> list[int]:
        """Every few samples between i0 and i1, both ends kept: smooth enough for a line, light for the page."""
        ids = list(range(i0, i1 + 1, every))
        return ids if ids and ids[-1] == i1 else [*ids, i1]

    def edge(self, u: float) -> str:
        pts = [self.page(*self.at(i, u)) for i in self._ids(0, len(self.line) - 1)]
        return "M" + " L".join(f"{m(x)},{m(y)}" for x, y in pts)

    def contains(self, x: float, y: float, margin: float = 0.0) -> bool:
        """Whether a point of the page lies on the road, its kerbs or verges (`margin` more ground beyond them)."""
        if y <= self.hz + 0.5:
            return False
        z = self.f / (y - self.hz)
        gx = (x - self.vx) * z / self.f
        reach = self.half + self.kerb + self.verge + margin
        return any(math.hypot(mx - gx, mz - z) < reach for mx, mz, _, _ in self.line[::2])

    def index_at(self, x: float, z: float) -> int:
        return min(range(len(self.line)), key=lambda i: (self.line[i][0] - x) ** 2 + (self.line[i][1] - z) ** 2)

    # ----------------------------------------------------------------- drawing
    def draw(self, c: Canvas, seed: int = 7) -> None:
        """The verges, the road bed, the setts course by course, the gutters and the kerbs."""
        h, k, v = self.half, self.kerb, self.verge
        grass = P.GRASS
        c.add(f'<path d="{self.strip(-h - k - v, h + k + v)}" fill="{grass}"/>')
        for u0, u1 in ((-h - k - v, -h - k - v * 0.45), (h + k + v * 0.45, h + k + v)):   # the verge's soft edge
            c.add(f'<path d="{self.strip(u0, u1)}" fill="{lighten(grass, 0.18)}" fill-opacity=".6"/>')
        bed = darken(P.FLOOR, 0.62)
        c.add(f'<path d="{self.strip(-h, h)}" fill="{bed}"/>')
        self._setts(c, seed)
        for u0, u1 in ((-h, -h + 0.05), (h - 0.05, h)):                                  # the gutters' shade
            c.add(f'<path d="{self.strip(u0, u1)}" fill="{INK}" fill-opacity=".12"/>')
        for side in (-1, 1):
            a, b = side * h, side * (h + k)
            u0, u1 = min(a, b), max(a, b)
            c.add(f'<path d="{self.strip(u0, u1)}" fill="{P.CARD}"/>')
            face = (u0, u0 + k * 0.3) if side > 0 else (u1 - k * 0.3, u1)
            c.add(f'<path d="{self.strip(*face)}" fill="{P.STONE}"/>')
            joints = []
            for i in range(0, len(self.line), 9):
                (x0, y0), (x1, y1) = self.page(*self.at(i, u0)), self.page(*self.at(i, u1))
                if abs(y1 - y0) + abs(x1 - x0) > 3:
                    joints.append(f"M{n(x0)},{n(y0)} L{n(x1)},{n(y1)}")
            c.line(" ".join(joints), 0.9, darken(P.STONE, 0.7), 0.8)
            for u in (u0, u1):
                c.add(f'<path d="{self.edge(u)}" fill="none" stroke="{INK}" stroke-width="1.6" '
                      f'stroke-linejoin="round" stroke-linecap="round"/>')

    def _setts(self, c: Canvas, seed: int) -> None:
        """Granite setts in courses across the road, every other course shifted by half a stone; each a rounded
        block a little inset from its neighbours, in five warm tones, its far edge catching the light and its
        near foot in shade. Courses too small to tell apart are left to the road bed's plain surface."""
        rnd = random.Random(seed)
        tones = (P.FLOOR, P.WOOD_PALE, mix(P.FLOOR, P.SAND, 0.5), mix(P.WOOD_PALE, P.YELLOW_PALE, 0.4),
                 mix(P.FLOOR, P.CRUST, 0.35))
        per = max(1, round(self.course / STEP))
        across = self.across
        by_tone: dict[str, list[str]] = {t: [] for t in tones}
        lights, shades = [], []
        width = 2 * self.half / across
        for row, i in enumerate(range(0, len(self.line) - per, per)):
            j = i + per
            shift = 0.5 if row % 2 else 0.0
            for s in range(-1, across + 1):
                u0 = max(-self.half, -self.half + (s + shift) * width)
                u1 = min(self.half, -self.half + (s + 1 + shift) * width)
                if u1 - u0 < width * 0.2:
                    continue
                gap_u, gap_s = width * 0.07, 0.12
                ia, ib = i + per * gap_s, j - per * gap_s
                corners = [self._pt(ia, u0 + gap_u), self._pt(ia, u1 - gap_u), self._pt(ib, u1 - gap_u),
                           self._pt(ib, u0 + gap_u)]
                xs, ys = [p[0] for p in corners], [p[1] for p in corners]
                size = max(max(xs) - min(xs), max(ys) - min(ys))
                if size < 5.0 or max(xs) < -10 or min(xs) > 850 or min(ys) > 1200:
                    continue                                 # a speck, or off the page: the bed shows
                tone = rnd.choice(tones)
                if size < 16:                                # a smaller stone: its corners softened by the stroke
                    by_tone[tone].append("M" + " L".join(f"{m(px)},{m(py)}" for px, py in corners) + "Z")
                    continue
                by_tone[tone].append(_rounded(corners, min(0.28, 2.0 / size)))
                if size > 18:
                    far_i, near_i = (ia, ib) if corners[0][1] < corners[3][1] else (ib, ia)
                    lights.append(_band(self, far_i, near_i, u0 + gap_u * 2, u1 - gap_u * 2, 0.0, 0.22))
                    shades.append(_band(self, far_i, near_i, u0 + gap_u, u1 - gap_u, 0.72, 1.0))
        for tone, parts in by_tone.items():
            if parts:
                c.add(f'<path d="{"".join(parts)}" fill="{tone}" stroke="{darken(P.FLOOR, 0.55)}" '
                      f'stroke-width=".8" stroke-linejoin="round"/>')
        c.add(f'<path d="{"".join(lights)}" fill="{P.WHITE}" fill-opacity=".35"/>'
              f'<path d="{"".join(shades)}" fill="{darken(P.FLOOR, 0.6)}" fill-opacity=".35"/>')

    def _pt(self, i: float, u: float) -> tuple[float, float]:
        """The page point at fractional sample i, offset u."""
        a = int(min(max(i, 0), len(self.line) - 2))
        t = i - a
        (x0, z0), (x1, z1) = self.at(a, u), self.at(a + 1, u)
        return self.page(x0 + (x1 - x0) * t, z0 + (z1 - z0) * t)


def _band(road: Road, far_i: float, near_i: float, u0: float, u1: float, t0: float, t1: float) -> str:
    """A band of a stone between t0 and t1 of the way from its far edge to its near one."""
    a, b = far_i + (near_i - far_i) * t0, far_i + (near_i - far_i) * t1
    pts = [road._pt(a, u0), road._pt(a, u1), road._pt(b, u1), road._pt(b, u0)]
    return "M" + " L".join(f"{m(x)},{m(y)}" for x, y in pts) + " Z"


def _rounded(corners: list[tuple[float, float]], r: float) -> str:
    """A quadrilateral with its corners rounded by `r` of each side."""
    out = []
    count = len(corners)
    for i in range(count):
        p, q, nx = corners[i - 1], corners[i], corners[(i + 1) % count]
        a = (q[0] + (p[0] - q[0]) * r, q[1] + (p[1] - q[1]) * r)
        b = (q[0] + (nx[0] - q[0]) * r, q[1] + (nx[1] - q[1]) * r)
        out.append(f"{'M' if not out else 'L'}{m(a[0])},{m(a[1])} Q{m(q[0])},{m(q[1])} {m(b[0])},{m(b[1])}")
    return " ".join(out) + " Z"


# ============================================================================ the road's company and furniture
def scale(road: Road, y: float) -> float:
    """How tall the professor stands at height y of the page: half the camera's height above the ground."""
    return 0.5 * (y - road.hz)


def body_box(name: str, x: float, feet: float, tall: float) -> tuple[float, float, float, float]:
    """Where a character stood at (x, feet), `tall` being the professor's height there, is boxed on a stage."""
    from .characters import module
    from .scenes import PROFESSOR_HEIGHT
    mod = module(name)
    k = tall / PROFESSOR_HEIGHT * mod.SCENE_SCALE
    half = mod.SIZE[0] * 0.40 * k
    return (x - half, feet - (mod.FEET_Y - mod.HEAD_TOP) * k, x + half, feet)


def walk_along(stage, road: Road, names: tuple[str, ...], lead: int, size: float = 1.0, u: float = 0.12,
               gap: float = 12.0, lo: float = 8.0, hi: float | None = None, bottom: float | None = None,
               dry: bool = False, poses: dict[str, str] | None = None,
               sun: tuple[float, float] | None = None) -> list:
    """The cast walking along the road towards the bend, all one way (to the right on the page), the first of
    `names` at the middle line's sample `lead`, each of the others the next free place back along the road - evenly
    spaced like a group walking together, nobody touching anybody; each with a soft shadow under the feet. A
    character that finds no room on the page is left out. Each walks side-on (`stride`, or its `walk` where it has
    none) unless `poses` says otherwise; with the `sun` given, the low sun rims their edges and throws their long
    shadows towards the reader. Returns their boxes (`dry`: only works them out)."""
    from .characters import module
    from .openers import Box
    hi = 840 - 8.0 if hi is None else hi
    placed = []
    i = lead
    lead_y = road.page(*road.at(lead, u))[1]
    one = scale(road, lead_y) * size                     # one scale for the group, growing gently as they come near
    for name in names:                                  # back along the road: towards the page's edge
        while i < len(road.line) - 1:
            x, y = road.page(*road.at(i, u))
            tall = one * min(1.1, max(1.0, scale(road, y) / max(1e-6, scale(road, lead_y))))  # nearer, a little larger
            box = body_box(name, x, y, tall)
            ok = box[0] >= lo and box[2] <= hi and box[1] >= 6 and (bottom is None or y <= bottom)
            if ok and all(box[0] > b.right + gap or box[2] < b.left - gap or box[3] < b.top - gap
                          or box[1] > b.bottom + gap for b in placed) and _free(stage, box):
                if dry:
                    placed.append(Box(*box, name, name, "actor"))
                    break
                pose = (poses or {}).get(name) or ("stride" if "stride" in module(name).POSES else "walk")
                if sun is not None:
                    long_shadow(stage, box, sun)
                else:
                    stage.back.add(f'<ellipse cx="{n(x)}" cy="{n(y - 1)}" rx="{n((box[2] - box[0]) * 0.42)}" '
                                   f'ry="{n(tall * 0.03)}" fill="{INK}" fill-opacity=".18"/>')
                actor = stage.actor(name, x, y, pose, "smile", tall=tall, group=name)
                if sun is not None:
                    rim(stage, actor, sun)
                placed.append(actor)
                break
            i += 1
    return placed


RIM = P.GOLD_LIGHT        # the low sun's light along a figure's edges


def rim(stage, actor, sun: tuple[float, float], width: float = 2.2) -> None:
    """The setting sun rimming a figure: a flat warm-gold copy of the character just behind it, shifted towards the
    sun, so a thin line of light shows along the edges that face it (vector only: a recoloured copy, no filter)."""
    index = stage.drawn[id(actor)][0]
    depth, _, fragment = stage.items[index]
    cx, cy = (actor.left + actor.right) / 2, (actor.top + actor.bottom) / 2
    dx, dy = sun[0] - cx, sun[1] - cy
    d = math.hypot(dx, dy) or 1
    k = width * max(0.6, (actor.bottom - actor.top) / 160)
    stage.put(depth - 0.001, f'<g class="rim" transform="translate({n(dx / d * k)},{n(dy / d * k)})">'
              f'<style>.rim *{{fill:{RIM} !important;stroke:{RIM} !important}}</style>{fragment}</g>')


def long_shadow(stage, box: tuple, sun: tuple[float, float]) -> None:
    """A long soft shadow on the ground from a figure's feet, thrown away from the low sun towards the reader."""
    x0, x1, y = box[0], box[2], box[3]
    cx = (x0 + x1) / 2
    h = box[3] - box[1]
    dx = (cx - sun[0]) / max(1.0, abs(sun[1] - y)) * h * 0.5
    w = (x1 - x0) * 0.36
    stage.back.add(f'<path d="M{n(cx - w)},{n(y - 1)} Q{n(cx)},{n(y - 4)} {n(cx + w)},{n(y - 1)} '
                   f'L{n(cx + dx + w * 1.4)},{n(y + h * 0.16)} Q{n(cx + dx)},{n(y + h * 0.2)} '
                   f'{n(cx + dx - w * 1.4)},{n(y + h * 0.16)} Z" fill="{INK}" fill-opacity=".14"/>')


def _free(stage, box: tuple) -> bool:
    """Room for a character: nothing within 4 units, but big furniture it clearly stands in front of (as the
    stage's checks allow), and no reserved area."""
    from .openers import IN_FRONT, Box
    if any(Box(*zone, "", "").hits(box) for zone in stage.reserved):
        return False
    return not any(b.hits(box, 4) and not (b.kind == "backdrop" and box[3] - b.bottom >= IN_FRONT)
                   for b in stage.boxes)


def birds(c: Canvas, region: tuple[float, float, float, float], count: int, seed: int, color: str = INK) -> None:
    """Birds flying home across the evening sky: little gull wings, nearer ones bigger."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = region
    for _ in range(count):
        x, y, k = rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(0.5, 1.1)
        c.line(f"M{n(x - 10 * k)},{n(y)} q{n(5 * k)},{n(-7 * k)} {n(10 * k)},0 q{n(5 * k)},{n(-7 * k)} {n(10 * k)},0",
               max(1.2, 2.2 * k), mix(P.INDIGO, INK, 0.5))


def furnish(stage, road: Road, seed: int = 3) -> None:
    """The road's furniture, each on its own verge and only where it stands free: a wooden bench facing the road,
    a hedge of round bushes behind the crosswise stretch and a low rail fence along the straight's far side."""
    rnd = random.Random(seed)
    straight = [i for i, (_, _, tx, tz) in enumerate(road.line) if tz < -0.99]
    if not straight:
        return
    out = road.half + road.kerb + road.verge
    # the rail fence along the straight's inner side, posts at even steps
    posts, rails = [], []
    span = straight[max(0, len(straight) - 1 - int(4.0 / STEP)):]
    for i in span[::12]:
        (x0, y0) = road.page(*road.at(i, -out - 0.05))
        h = scale(road, y0) * 0.45
        if h < 2:
            continue
        posts.append(f"M{n(x0)},{n(y0)} v{n(-h)}")
        rails.append((x0, y0 - h * 0.85, y0 - h * 0.45))
    if posts:
        stage.back.add(f'<path d="{" ".join(posts)}" stroke="{P.WOOD_DARK}" stroke-width="2.2" fill="none"/>')
        for a, b in zip(rails, rails[1:], strict=False):
            stage.back.add(f'<path d="M{n(a[0])},{n(a[1])} L{n(b[0])},{n(b[1])} M{n(a[0])},{n(a[2])} '
                           f'L{n(b[0])},{n(b[2])}" stroke="{P.WOOD}" stroke-width="1.6" fill="none"/>')
    # the hedge behind the crosswise stretch and the bend
    bend = [i for i, (_, _, tx, tz) in enumerate(road.line) if tz >= -0.99]
    bushes = []
    for i in bend[::7]:
        x, y = road.page(*road.at(i, -out - 0.12))
        r = scale(road, y) * 0.07 * rnd.uniform(0.85, 1.15)
        if r > 1.5 and -20 < x < 860:
            bushes.append((y, x, r))
    for y, x, r in sorted(bushes):
        stage.back.add(f'<ellipse cx="{n(x)}" cy="{n(y - r * 0.8)}" rx="{n(r * 1.3)}" ry="{n(r)}" fill="{P.LEAF}" '
                       f'stroke="{INK}" stroke-width="1"/><path d="M{n(x - r * 0.6)},{n(y - r * 1.1)} '
                       f'q{n(r * 0.5)},{n(-r * 0.4)} {n(r)},0" stroke="{P.LEAF_LIGHT}" stroke-width="1.6" '
                       f'fill="none"/>')
    # the bench on the straight's verge
    for kind, at_, side in (("bench", 0.8, -1),):
        i = straight[int(len(straight) * at_)]
        u = side * (road.half + road.kerb + road.verge * 0.55)
        x, y = road.page(*road.at(i, u))
        k = scale(road, y) / 100
        if k < 0.25:
            continue
        art, box = _thing(kind, x, y, k)
        if box[0] > 6 and box[2] < 834 and stage.free(box, 4):
            stage.put(y, art, box, kind, group=kind, backdrop=True)


def _thing(kind: str, x: float, y: float, k: float) -> tuple[str, tuple]:
    """A bench (two cast-iron ends, three slats, a back) standing at (x, y), `k` a hundredth of the professor."""
    c = Canvas()
    sw = max(0.8, 1.6 * k)
    c.add(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(26 * k)}" ry="{n(3 * k)}" fill="{INK}" fill-opacity=".15"/>')
    for ex in (-20, 20):
        c.line(f"M{n(x + ex * k)},{n(y)} V{n(y - 30 * k)}", 2.4 * k, P.CHARCOAL)
    for q in range(3):
        c.shape(f"M{n(x - 24 * k)},{n(y - 16 * k - q * 3 * k)} h{n(48 * k)} v{n(2.4 * k)} h{n(-48 * k)} Z",
                P.WOOD, sw=sw * 0.6, light=None)
    for q in range(2):
        c.shape(f"M{n(x - 24 * k)},{n(y - 30 * k + q * 5 * k)} h{n(48 * k)} v{n(3 * k)} h{n(-48 * k)} Z",
                P.WOOD, sw=sw * 0.6, light=None)
    return c.render(), (x - 25 * k, y - 31 * k, x + 25 * k, y)

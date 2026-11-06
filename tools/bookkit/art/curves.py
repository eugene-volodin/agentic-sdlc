"""How every cable, hose, tube and rope in the book bends: smooth, never kinked.

One algorithm for every hose and wire, so that a cable goes into its plug smoothly. A line is laid along a polygon
(out of a port, through some points, into another port) and each corner of the polygon is replaced by a *bend* the
way a real cable or hose bends: its curvature grows from nothing out of the straight run, peaks in the middle of the
bend and falls back to nothing into the next run (a sine-squared curvature ramp, integrated). So there is no kink
anywhere - not at the corner, not where the bend begins - and for the room it has the bend is wide: its tightest
radius is about half the run it takes, against a quarter for the usual Bezier ease. Each corner takes as much of its
two runs as it may (half a run shared with the next corner, all of a run but its straight `keep` at an end, where the
line goes into a fitting); `turns` measures a drawn line for the tests: the sharpest step and the tightest radius.
"""
from __future__ import annotations

import math
from functools import cache

from .ink import n

Point = tuple[float, float]
STEPS = 48            # points per bend


def _clean(points: list[Point]) -> list[Point]:
    """The polygon without repeated points and without points that lie straight on between their neighbours."""
    out: list[Point] = []
    for p in points:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 0.25:
            out.append(p)
    i = 1
    while i < len(out) - 1:
        (ax, ay), (bx, by), (cx, cy) = out[i - 1], out[i], out[i + 1]
        ux, uy, vx, vy = bx - ax, by - ay, cx - bx, cy - by
        if abs(ux * vy - uy * vx) < 1e-6 * math.hypot(ux, uy) * math.hypot(vx, vy) and ux * vx + uy * vy > 0:
            del out[i]
        else:
            i += 1
    return out


@cache
def _unit_bend(turn: float) -> tuple[tuple[Point, ...], float]:
    """A bend through `turn` radians of arc length 1, starting at the origin heading along +x and turning towards
    +y, its curvature sin^2-shaped: the points along it and how far from its start its two straight runs meet."""
    fine = STEPS * 8
    x = y = 0.0
    pts = [(0.0, 0.0)]
    for i in range(1, fine + 1):
        s = (i - 0.5) / fine
        phi = turn * (s - math.sin(2 * math.pi * s) / (2 * math.pi))
        x += math.cos(phi) / fine
        y += math.sin(phi) / fine
        if i % 8 == 0:
            pts.append((x, y))
    reach = x - y / math.tan(turn)                   # where the end's line crosses the start's (the bend is symmetric)
    return tuple(pts), reach


def _bend(b: Point, uin: Point, uout: Point, t: float) -> list[Point]:
    """The bend at corner b between the runs uin (in) and uout (out), taking `t` of each: its points, start to end."""
    cross = uin[0] * uout[1] - uin[1] * uout[0]
    turn = math.atan2(abs(cross), uin[0] * uout[0] + uin[1] * uout[1])
    pts, reach = _unit_bend(round(turn, 4))
    scale = t / reach
    side = 1 if cross > 0 else -1
    sx, sy = b[0] - uin[0] * t, b[1] - uin[1] * t
    nx, ny = -uin[1] * side, uin[0] * side           # the normal towards the inside of the bend
    return [(sx + (px * uin[0] + py * nx) * scale, sy + (px * uin[1] + py * ny) * scale) for px, py in pts]


def eased_points(points: list[Point], keep_start: float = 0.0, keep_end: float = 0.0,
                 step: float | None = None) -> list[Point]:
    """The eased line through the polygon `points`: straight runs and bends, as a dense list of points (every bend
    in `STEPS` points). The first `keep_start` and the last `keep_end` of it stay straight. `step`, if given, also
    splits the straight runs into points about that far apart (for checks along the line)."""
    pts = _clean(points)
    if len(pts) < 2:
        return list(pts)
    lengths = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:], strict=False)]
    last = len(lengths) - 1

    def room(j: int, corner_at_end: bool) -> float:
        """How much of run j the corner at its end (or at its start) may take."""
        if j == 0 and j == last:
            return 0.0
        if j == 0:
            return max(0.0, lengths[0] - keep_start) if corner_at_end else 0.0
        if j == last:
            return 0.0 if corner_at_end else max(0.0, lengths[j] - keep_end)
        return lengths[j] / 2

    out = [pts[0]]

    def run_to(p: Point) -> None:
        a = out[-1]
        if math.hypot(p[0] - a[0], p[1] - a[1]) < 0.05:     # the bend already ends here
            out[-1] = p
            return
        if step:
            count = max(1, int(math.hypot(p[0] - a[0], p[1] - a[1]) / step))
            out.extend((a[0] + (p[0] - a[0]) * i / count, a[1] + (p[1] - a[1]) * i / count) for i in range(1, count))
        out.append(p)

    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        uin = ((b[0] - a[0]) / lengths[i - 1], (b[1] - a[1]) / lengths[i - 1])
        uout = ((c[0] - b[0]) / lengths[i], (c[1] - b[1]) / lengths[i])
        t = min(room(i - 1, True), room(i, False))
        dot = uin[0] * uout[0] + uin[1] * uout[1]
        slight = round(math.atan2(abs(uin[0] * uout[1] - uin[1] * uout[0]), dot), 4) == 0   # below `_bend`'s table
        if t <= 1e-6 or dot < -0.999 or slight:
            run_to(b)
            continue
        bend = _bend(b, uin, uout, t)
        run_to(bend[0])
        out.extend(bend[1:-1])
        out.append((b[0] + uout[0] * t, b[1] + uout[1] * t))   # exactly on the next run
    run_to(pts[-1])
    return out


def eased_d(points: list[Point], keep_start: float = 0.0, keep_end: float = 0.0) -> str:
    """The SVG path data of the eased line."""
    line = eased_points(points, keep_start, keep_end)
    if not line:
        return ""
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in line)


def turns(samples: list[Point]) -> tuple[float, float]:
    """The sharpest turn between consecutive steps along a sampled line (degrees) and its tightest radius (the
    circle through three consecutive samples)."""
    sharpest, tightest = 0.0, math.inf
    for a, b, c in zip(samples, samples[1:], samples[2:], strict=False):
        ux, uy, vx, vy = b[0] - a[0], b[1] - a[1], c[0] - b[0], c[1] - b[1]
        lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
        if lu < 1e-6 or lv < 1e-6:
            continue
        cross = ux * vy - uy * vx
        sharpest = max(sharpest, math.degrees(math.atan2(abs(cross), ux * vx + uy * vy)))
        chord = math.hypot(c[0] - a[0], c[1] - a[1])
        if abs(cross) > 1e-15:
            tightest = min(tightest, lu * lv * chord / (2 * abs(cross)))
    return sharpest, tightest

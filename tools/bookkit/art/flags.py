"""Small national flags for tables and running text: `:flag-us:` in Markdown.

Drawn in the house style, like the doodles: a cloth waving on a little pole, a wobbly ink outline and cel shading on
the side away from the top-left light, not a flat rectangle. Emoji are not used in the handbook. Colors come from
`bookkit.design`.
"""
from __future__ import annotations

import math

from .. import design as P
from .ink import Canvas, n

# The cloth, in a 100 x 72 box: it hangs from the pole at x=16 and waves to the right.
LEFT, RIGHT, TOP, HEIGHT = 16.0, 94.0, 10.0, 44.0


def _wave(x: float) -> float:
    """How far the cloth dips at `x`: more the further it is from the pole."""
    t = (x - LEFT) / (RIGHT - LEFT)
    return 3.6 * math.sin(t * math.tau * 1.15) * (0.35 + 0.65 * t)


def _band(x0: float, x1: float, v0: float, v1: float, steps: int = 14) -> str:
    """A closed path for the part of the cloth between columns x0..x1 and heights v0..v1 (0 top, 1 bottom)."""
    xs = [x0 + (x1 - x0) * i / steps for i in range(steps + 1)]
    top = [(x, TOP + v0 * HEIGHT + _wave(x)) for x in xs]
    bottom = [(x, TOP + v1 * HEIGHT + _wave(x)) for x in reversed(xs)]
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in top + bottom) + " Z"


def _star(cx: float, cy: float, r: float, color: str) -> str:
    points = []
    for i in range(10):
        radius = r if i % 2 == 0 else r * 0.42
        angle = math.radians(-90 + i * 36)
        points.append(f"{n(cx + radius * math.cos(angle))},{n(cy + radius * math.sin(angle))}")
    return f'<path d="M{" L".join(points)} Z" fill="{color}"/>'


def _us(c: Canvas) -> None:
    for i in range(7):                                   # seven stripes read better than thirteen at this size
        c.path(_band(LEFT, RIGHT, i / 7, (i + 1) / 7), P.RED if i % 2 == 0 else P.WHITE, sw=0)
    c.path(_band(LEFT, LEFT + 34, 0, 4 / 7, steps=6), P.BLUE, sw=0)
    for row in range(3):
        for col in range(4):
            x = LEFT + 5 + col * 8
            c.add(f'<circle cx="{n(x)}" cy="{n(TOP + 5 + row * 7.5 + _wave(x))}" r="1.6" fill="{P.WHITE}"/>')


def _cn(c: Canvas) -> None:
    c.path(_band(LEFT, RIGHT, 0, 1), P.RED, sw=0)
    c.add(_star(LEFT + 14, TOP + 13 + _wave(LEFT + 14), 8, P.YELLOW))
    for dx, dy in ((27, 5), (32, 11), (32, 19), (27, 25)):
        c.add(_star(LEFT + dx, TOP + dy + _wave(LEFT + dx), 2.6, P.YELLOW))


def _fr(c: Canvas) -> None:
    third = (RIGHT - LEFT) / 3
    for i, color in enumerate((P.BLUE, P.WHITE, P.RED)):
        c.path(_band(LEFT + i * third, LEFT + (i + 1) * third, 0, 1, steps=6), color, sw=0)


def _ru(c: Canvas) -> None:
    for i, color in enumerate((P.WHITE, P.BLUE, P.RED)):
        c.path(_band(LEFT, RIGHT, i / 3, (i + 1) / 3, steps=10), color, sw=0)


FLAGS = {"us": _us, "cn": _cn, "fr": _fr, "ru": _ru}


def flag(code: str) -> str:
    """An inline `<svg>` flag on a pole, drawn like the doodles."""
    if code not in FLAGS:
        raise ValueError(f"unknown flag {code!r}; available: {', '.join(FLAGS)}")
    c = Canvas()
    c.line(f"M{n(LEFT - 2)},{n(TOP - 6)} L{n(LEFT - 2)},70", 4.2)                     # the pole
    c.add(f'<circle cx="{n(LEFT - 2)}" cy="{n(TOP - 7)}" r="3.4" fill="{P.YELLOW}" stroke="{P.INK}" stroke-width="2"/>')
    FLAGS[code](c)
    c.path(_band(LEFT, RIGHT, 0.62, 1), P.INK, sw=0, extra='opacity="0.12"')   # shade, away from the light
    c.path(_band(LEFT, RIGHT, 0, 1), "none", sw=3)                                      # the ink outline on top
    for x in (LEFT + 26, LEFT + 52):                                                   # the folds
        c.line(f"M{n(x)},{n(TOP + 2 + _wave(x))} q2,{n(HEIGHT / 2)} 0,{n(HEIGHT - 4)}", 1.3, opacity=0.35)
    return f'<svg class="flag" viewBox="0 0 100 72" aria-hidden="true">{c.render()}</svg>'

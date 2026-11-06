"""Drawing primitives shared by every illustration in the book.

All art is vector SVG assembled from strings. The house style is:

* a dark "ink" outline with round joins,
* flat fills with a second, darker tone on the side away from the light
  (cel shading, built with a clip path so it follows any silhouette),
* dotted stipple texture in the shadows, as in the printed original.

Colors always come from `bookkit.design`; this module never invents one. Shadow tones are
computed from the fill with `design.darken`, so a material needs only its base color.

`Canvas` collects SVG fragments; every helper appends to it and nothing is
rendered until `Canvas.render()` is called.
"""
from __future__ import annotations

import functools
import itertools
import math
import random
import re
from html import escape

from .. import design as P
from ..design import darken

INK = P.INK
SW = 2.6  # default outline width in drawing units
LIGHT = (-4.0, -5.0)  # offset of the lit area: light comes from the top left

_ids = itertools.count(1)
_scope = ""


def id_scope(scope: str) -> None:
    """Start numbering ids afresh under `scope`. A build numbers its pages' drawings from 1 (so the same book always
    gives the same document); the footers, drawn later in another process, take a scope of their own, so their ids
    never meet the page's."""
    global _ids, _scope
    _ids, _scope = itertools.count(1), scope


def uid(prefix: str = "k") -> str:
    """Return a document-unique id for clip paths and gradients."""
    return f"{_scope}{prefix}{next(_ids)}"


def n(value: float) -> str:
    """Format a number compactly for SVG output."""
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text or "0"


def ellipse_d(cx: float, cy: float, rx: float, ry: float) -> str:
    """Path data for an ellipse, so ellipses can be shaded like any other shape."""
    return (f"M{n(cx - rx)},{n(cy)} A{n(rx)},{n(ry)} 0 1 0 {n(cx + rx)},{n(cy)} "
            f"A{n(rx)},{n(ry)} 0 1 0 {n(cx - rx)},{n(cy)} Z")


def circle_d(cx: float, cy: float, r: float) -> str:
    """Path data for a circle."""
    return ellipse_d(cx, cy, r, r)


def rect_d(x: float, y: float, w: float, h: float) -> str:
    """Path data for a plain rectangle."""
    return f"M{n(x)},{n(y)} H{n(x + w)} V{n(y + h)} H{n(x)} Z"


def poly_d(points) -> str:
    """Path data for a closed polygon through `points`."""
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in points) + " Z"


def rounded_rect_d(x: float, y: float, w: float, h: float, r: float) -> str:
    """Path data for a rectangle with rounded corners."""
    return (f"M{n(x + r)},{n(y)} H{n(x + w - r)} Q{n(x + w)},{n(y)} {n(x + w)},{n(y + r)} "
            f"V{n(y + h - r)} Q{n(x + w)},{n(y + h)} {n(x + w - r)},{n(y + h)} "
            f"H{n(x + r)} Q{n(x)},{n(y + h)} {n(x)},{n(y + h - r)} V{n(y + r)} "
            f"Q{n(x)},{n(y)} {n(x + r)},{n(y)} Z")


def angle_of(x1: float, y1: float, x2: float, y2: float) -> float:
    """Direction from point 1 to point 2 in degrees."""
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


def polar(x: float, y: float, angle: float, dist: float) -> tuple[float, float]:
    """Point at `dist` from (x, y) in direction `angle` (degrees)."""
    a = math.radians(angle)
    return x + math.cos(a) * dist, y + math.sin(a) * dist


class Canvas:
    """Accumulates SVG fragments drawn back to front."""

    def __init__(self) -> None:
        self.parts: list[str] = []

    # ------------------------------------------------------------ plumbing
    def add(self, fragment: str) -> Canvas:
        self.parts.append(fragment)
        return self

    def render(self) -> str:
        return "".join(self.parts)

    def place(self, inner: Canvas | str, transform: str) -> Canvas:
        """Insert another drawing under a transform."""
        body = inner.render() if isinstance(inner, Canvas) else inner
        return self.add(f'<g transform="{transform}">{body}</g>')

    def gradient(self, stops: list[tuple[float, str]], x1: float, y1: float, x2: float, y2: float) -> str:
        """Define an opaque linear gradient in drawing units; returns a `url(#id)` paint.

        `stops` is a list of `(offset 0..1, color)`. There is no opacity: Chrome prints a gradient that fades to
        transparent as a 72 dpi raster with a soft mask, which Apple's PDF viewers draw torn - use `fade`.
        """
        gid = uid("g")
        body = "".join(f'<stop offset="{n(o)}" stop-color="{col}"/>' for o, col in stops)
        self.add(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{n(x1)}" y1="{n(y1)}" '
                 f'x2="{n(x2)}" y2="{n(y2)}">{body}</linearGradient>')
        return f"url(#{gid})"

    def fade(self, x: float, y: float, w: float, h: float, stops: list[tuple[float, str, float]],
             steps: int = 48) -> Canvas:
        """A vertical band that fades to or from transparent, as vector shapes with flat opacity.

        `stops` is a list of `(offset 0..1 from the top, color, opacity)`, the opacity rising or falling all the
        way. The band is a stack of rectangles, each running from its step to the band's opaque end, so their
        layered opacity follows the stops and no seam opens between neighbours.
        """
        def at(t: float) -> tuple[str, float]:
            for (o1, c1, a1), (o2, c2, a2) in itertools.pairwise(stops):
                if t <= o2:
                    k = 0.0 if o2 == o1 else max(0.0, (t - o1) / (o2 - o1))
                    return P.mix(c1, c2, k), a1 + (a2 - a1) * k
            return stops[-1][1], stops[-1][2]

        alphas = [a for _, _, a in stops]
        down = alphas[-1] >= alphas[0]          # opaque at the bottom
        if alphas != sorted(alphas, reverse=not down):
            raise ValueError("fade: the opacity must rise or fall all the way")
        step = h / steps
        order = range(steps) if down else range(steps - 1, -1, -1)
        done = 0.0                              # opacity laid down so far
        for i in order:
            color, alpha = at((i + 0.5) / steps)
            if alpha <= done:
                continue
            layer = 1.0 if done >= 1 else 1 - (1 - alpha) / (1 - done)
            top, bottom = (y + i * step, y + h) if down else (y, y + (i + 1) * step)
            self.add(f'<rect x="{n(x)}" y="{n(top)}" width="{n(w)}" height="{n(bottom - top)}" fill="{color}" '
                     f'fill-opacity="{layer:.3f}"/>')
            done = alpha
        return self

    # ------------------------------------------------------------ strokes
    def path(self, d: str, fill: str = "none", sw: float = SW, stroke: str = INK,
             extra: str = "") -> Canvas:
        """A plain filled and/or outlined path."""
        stroke_attrs = (f'stroke="{stroke}" stroke-width="{n(sw)}" stroke-linejoin="round" '
                        f'stroke-linecap="round"') if sw else 'stroke="none"'
        return self.add(f'<path d="{d}" fill="{fill}" {stroke_attrs} {extra}/>')

    def line(self, d: str, sw: float = 1.9, stroke: str = INK, opacity: float = 1.0) -> Canvas:
        """A detail line: folds, hair strands, wrinkles."""
        op = f' stroke-opacity="{opacity}"' if opacity < 1 else ""
        return self.add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{n(sw)}" '
                        f'stroke-linejoin="round" stroke-linecap="round"{op}/>')

    def text(self, x: float, y: float, text: str, size: float, fill: str = INK) -> Canvas:
        """Centred sign lettering (see `lettering`); the text is escaped, so any label is safe."""
        return self.add(lettering(x, y, str(text), size, fill))

    def dot(self, x: float, y: float, r: float = 2.2, fill: str = INK) -> Canvas:
        return self.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{fill}"/>')

    # ------------------------------------------------------------ volumes
    def shape(self, d: str, fill: str, sw: float = SW, light: tuple[float, float] | None = LIGHT,
              shade_k: float = 0.8, stipple: tuple | None = None, highlight: str | None = None,
              clip: bool = False) -> str:
        """A closed silhouette with cel shading.

        The silhouette is filled with the shadow tone, then the lit tone is
        painted through a clip of the same silhouette, shifted towards the
        light. What stays uncovered is a crescent of shadow on the far side.

        `stipple` is `(x, y, w, h, count, falloff)`: a box of dots clipped to
        the silhouette. `highlight` is path data for a white glint.

        Returns the id of a clip path of the silhouette, for callers that clip more detail to
        it. The clip path is only written when something uses it: shading, stipple, a
        highlight, or the caller asking with `clip=True` (then the id is always valid).
        """
        needs_clip = bool(light or stipple or highlight or clip)
        clip_id = uid() if needs_clip else ""
        if needs_clip:
            self.add(f'<clipPath id="{clip_id}"><path d="{d}"/></clipPath>')
        if light:
            self.add(f'<path d="{d}" fill="{darken(fill, shade_k)}"/>')
            self.add(f'<g clip-path="url(#{clip_id})"><path d="{d}" fill="{fill}" '
                     f'transform="translate({n(light[0])},{n(light[1])})"/></g>')
        else:
            self.add(f'<path d="{d}" fill="{fill}"/>')
        if stipple:
            self.dots(clip_id, *stipple)
        if highlight:
            self.add(f'<g clip-path="url(#{clip_id})"><path d="{highlight}" fill="none" stroke="{P.WHITE}" '
                     f'stroke-width="3.2" stroke-linecap="round" stroke-opacity=".55"/></g>')
        if sw:
            self.path(d, "none", sw)
        return clip_id

    def tube(self, d: str, fill: str, w: float, sw: float = SW, cap: str = "round",
             shaded: bool = True) -> Canvas:
        """A limb: a thick stroked centre line with an outline and a lit core."""
        common = f'fill="none" stroke-linejoin="round" stroke-linecap="{cap}"'
        self.add(f'<path d="{d}" {common} stroke="{INK}" stroke-width="{n(w + 2 * sw)}"/>')
        self.add(f'<path d="{d}" {common} stroke="{darken(fill) if shaded else fill}" stroke-width="{n(w)}"/>')
        if shaded:
            # Clip paths ignore strokes, so the lit core is a narrower stroke shifted to the light.
            self.add(f'<path d="{d}" {common} stroke="{fill}" stroke-width="{n(max(1.0, w - 6))}" '
                     f'transform="translate({n(LIGHT[0] * 0.45)},{n(LIGHT[1] * 0.45)})"/>')
        return self

    def union(self, pieces: list[tuple], fill: str, sw: float = SW) -> Canvas:
        """Several overlapping pieces drawn as one outlined silhouette.

        Each piece is `("p", path_data)` for a filled area or `("s", path_data, width)`
        for a capsule. All ink goes down first, then all fills, so outlines
        only survive on the outside of the merged shape.
        """
        for piece in pieces:
            if piece[0] == "p":
                self.add(f'<path d="{piece[1]}" fill="{INK}" stroke="{INK}" stroke-width="{n(2 * sw)}" '
                         f'stroke-linejoin="round"/>')
            else:
                self.add(f'<path d="{piece[1]}" fill="none" stroke="{INK}" stroke-width="{n(piece[2] + 2 * sw)}" '
                         f'stroke-linecap="round" stroke-linejoin="round"/>')
        for piece in pieces:
            if piece[0] == "p":
                self.add(f'<path d="{piece[1]}" fill="{fill}"/>')
            else:
                self.add(f'<path d="{piece[1]}" fill="none" stroke="{fill}" stroke-width="{n(piece[2])}" '
                         f'stroke-linecap="round" stroke-linejoin="round"/>')
        return self

    # ------------------------------------------------------------ texture
    @staticmethod
    def _dot_paths(points: list[tuple[float, float]], r: float, color: str, opacity: float) -> str:
        """Dots as zero-length round-capped strokes: one path per size instead of a circle per dot.

        A stroked point is a single move-and-line in the PDF, while a circle is
        several Bezier curves, so this keeps pages with thousands of dots small.
        """
        out = []
        for scale, group in ((0.85, points[0::2]), (1.2, points[1::2])):
            if group:
                d = "".join(f"M{n(x)},{n(y)}h.01" for x, y in group)
                out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{n(2 * r * scale)}" '
                           f'stroke-linecap="round" stroke-opacity="{opacity}"/>')
        return "".join(out)

    def dots(self, clip: str | None, x: float, y: float, w: float, h: float, count: int = 30,
             falloff: str = "right", seed: int = 1, r: float = 0.85, color: str = INK,
             opacity: float = 0.6) -> Canvas:
        """Stipple: dots in a box, denser towards one edge, optionally clipped."""
        rnd = random.Random(seed * 1009 + int(x * 7 + y * 13))
        points = []
        for _ in range(count):
            t = rnd.random() ** 2.4  # crowd the dots against the dense edge
            u = rnd.random()
            if falloff == "left":
                points.append((x + t * w, y + u * h))
            elif falloff == "right":
                points.append((x + w - t * w, y + u * h))
            elif falloff == "bottom":
                points.append((x + u * w, y + h - t * h))
            elif falloff == "top":
                points.append((x + u * w, y + t * h))
            else:  # even
                points.append((x + rnd.random() * w, y + u * h))
        body = self._dot_paths(points, r, color, opacity)
        return self.add(f'<g clip-path="url(#{clip})">{body}</g>' if clip else body)

    def ground_shadow(self, cx: float, cy: float, rx: float, ry: float, seed: int = 0) -> Canvas:
        """A soft flat shadow under a figure. Not dots: a dotted one reads as dust and litter
        under the characters' feet."""
        return self.add(f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx * 0.8)}" ry="{n(ry * 0.8)}" fill="{INK}" '
                        f'fill-opacity=".13"/>')


def svg(body: str, width: float, height: float, css_class: str = "", view_box: str | None = None,
        flip: bool = False, attrs: str = "") -> str:
    """Wrap drawing content in an <svg> element, optionally mirrored."""
    view_box = view_box or f"0 0 {n(width)} {n(height)}"
    if flip:
        x0, _, vw, _ = (float(v) for v in view_box.split())
        body = f'<g transform="translate({n(2 * x0 + vw)},0) scale(-1,1)">{body}</g>'
    cls = f' class="{css_class}"' if css_class else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}"{cls} aria-hidden="true" '
            f'{attrs}>{body}</svg>')


def lettering(x: float, y: float, text: str, size: float, fill: str = INK, anchor: str = "middle",
              turn: float = 0, room: float | None = None, style: str = "sign") -> str:
    """Lettering in a drawing, escaped. `sign`: balloon letters like the chapter titles - the heavy face in
    `fill` (white where ink is asked for, since the rim is ink already) with an ink rim and a small extrusion.
    `talk`: the comic face of speech bubbles. `plain`: a flat heavy face, for screens and displays. `label`: the sign
    face flat in `fill`, for labels written on things (jars, tins, crates). `room`, when
    given, is the width the line may not exceed: the whole line is set smaller rather than spill over - never
    squeezed narrower, which distorts the letters."""
    rot = f' transform="rotate({n(turn)} {n(x)} {n(y)})"' if turn else ""
    words = escape(text)
    if style == "talk":
        family, weight, spacing = P.ILLUSTRATION_FONT, P.ILLUSTRATION_WEIGHT, ""
    else:
        family, weight = (P.PLAIN_FONT, P.PLAIN_WEIGHT) if style == "plain" else (P.SIGN_FONT, P.SIGN_WEIGHT)
        if style != "plain":            # a glyph the sign face lacks comes from the flat face
            family = f"{family}, {P.PLAIN_FONT}"
        spacing = f' letter-spacing="{n(size * P.SIGN_TRACK)}" word-spacing="{n(size * P.SIGN_WORD)}"'
    if room is not None and lettering_width(text, size, style) > room:
        size *= room / lettering_width(text, size, style)
        if style != "talk":
            spacing = f' letter-spacing="{n(size * P.SIGN_TRACK)}" word-spacing="{n(size * P.SIGN_WORD)}"'
    head = (f'x="{n(x)}" y="{n(y)}" text-anchor="{anchor}" font-family="{family}" font-weight="{weight}" '
            f'font-size="{n(size)}"{spacing}')
    if style != "sign" or size < P.SIGN_BALLOON_FROM:      # small lettering: the heavy face, flat
        return f'<text {head} fill="{fill}"{rot}>{words}</text>'
    rim, deep = max(0.55, size * P.SIGN_RIM), max(0.7, size * P.SIGN_DEEP)
    face = P.WHITE if fill == INK else fill
    shadow = (f'<text {head} fill="{INK}" stroke="{INK}" stroke-width="{n(2 * rim)}" stroke-linejoin="round" '
              f'transform="translate({n(deep)} {n(deep)})">{words}</text>')
    body = (f'<text {head} fill="{face}" stroke="{INK}" stroke-width="{n(2 * rim)}" stroke-linejoin="round" '
            f'paint-order="stroke">{words}</text>')
    # marked, so that `settle_lettering` can flatten it if the drawing is scaled down too far on the page
    return f'<g class="balloon" data-size="{n(size)}" data-fill="{fill}"{rot}>{shadow}{body}</g>'


_TRANSFORM = re.compile(r'transform="([^"]*)"')
_TAG = re.compile(r"<(/?)([a-zA-Z]+)([^>]*?)(/?)>")


def _scale_of(transform: str) -> float:
    """How much a transform attribute enlarges lengths (rotations and moves do not)."""
    k = 1.0
    for kind, args in re.findall(r"(scale|matrix)\(([^)]*)\)", transform):
        v = [float(t) for t in re.split(r"[\s,]+", args.strip()) if t]
        if kind == "scale":
            k *= math.sqrt(abs(v[0] * (v[1] if len(v) > 1 else v[0])))
        elif len(v) == 6:
            k *= math.sqrt(abs(v[0] * v[3] - v[1] * v[2]))
    return k


_BALLOON = re.compile(r'<g class="balloon" data-size="([^"]+)" data-fill="([^"]+)"([^>]*)>'
                      r'<text [^>]*>.*?</text>(<text [^>]*>)(.*?)</text></g>', re.S)


def settle_lettering(svg: str) -> str:
    """Flatten the balloon lettering that the drawing's own scaling made too small on the page: a prop drawn at
    its own size and then shrunk would otherwise carry a rim that clogs its letters. The scale at each lettering
    is the product of its enclosing groups' transforms."""
    scales: dict[int, float] = {}
    stack = [1.0]
    for m in _TAG.finditer(svg):
        closing, attrs, selfclose = m.group(1), m.group(3), m.group(4)
        if closing:
            if len(stack) > 1:
                stack.pop()
            continue
        scale = stack[-1]
        t = _TRANSFORM.search(attrs)
        if t:
            scale *= _scale_of(t.group(1))
        if attrs.startswith(' class="balloon"'):
            scales[m.start()] = scale
        if not selfclose:
            stack.append(scale)

    def flat(m: re.Match) -> str:
        if float(m.group(1)) * scales.get(m.start(), 1.0) >= P.SIGN_BALLOON_FROM:
            return m.group(0)
        head = re.sub(r' (fill|stroke|stroke-width|stroke-linejoin|paint-order)="[^"]*"', "", m.group(4))
        head = head[:-1] + f' fill="{m.group(2)}">'
        return f"<g{m.group(3)}>{head}{m.group(5)}</text></g>"

    return _BALLOON.sub(flat, svg)


def lettering_width(text: str, size: float, style: str = "sign") -> float:
    """How wide a line of lettering is, in units: the real advances of the bundled face that draws it, plus the
    letter and word spacing of signs (kerning aside)."""
    family, weight = ((P.ILLUSTRATION_FONT, P.ILLUSTRATION_WEIGHT) if style == "talk" else
                      (P.PLAIN_FONT, P.PLAIN_WEIGHT) if style == "plain" else (P.SIGN_FONT, P.SIGN_WEIGHT))
    advances, fallback = _advances(family, weight)
    width = sum(advances.get(ord(ch), fallback) for ch in text) * size
    if style == "talk":
        return width
    return width + len(text) * size * P.SIGN_TRACK + text.count(" ") * size * P.SIGN_WORD


@functools.lru_cache(maxsize=8)
def _advances(family: str, weight: int) -> tuple[dict[int, float], float]:
    """Each character's advance in em for the bundled face of `family` at `weight` (a variable face fixed at
    that weight), and the advance to assume for a character the face lacks."""
    from fontTools.ttLib import TTFont

    from ..fonts import FONTS, static_weight

    faces = [(file, spec) for name, file, spec, style in P.FONT_FILES if name == family and style == "normal"]
    if not faces:
        raise ValueError(f"no bundled font for {family!r}")

    def distance(spec: str) -> int:
        low, _, high = spec.partition(" ")
        lo, hi = int(low), int(high or low)
        return 0 if lo <= weight <= hi else min(abs(weight - lo), abs(weight - hi))

    file, spec = min(faces, key=lambda face: distance(face[1]))
    path = FONTS / file
    font = TTFont(path, lazy=True)
    if "fvar" in font:
        low, _, high = spec.partition(" ")
        font = TTFont(static_weight(path, min(max(weight, int(low)), int(high or low))), lazy=True)
    upm = float(font["head"].unitsPerEm)
    metrics = font["hmtx"].metrics
    advances = {code: metrics[name][0] / upm for code, name in font.getBestCmap().items()}
    return advances, advances.get(ord("n"), 0.55)

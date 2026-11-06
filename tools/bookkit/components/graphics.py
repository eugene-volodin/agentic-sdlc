"""Small inline drawings shared by components: tails, ticks, icons, the computer's base."""
from __future__ import annotations

import math

from .. import design as P
from ..art.ink import Canvas, rounded_rect_d, svg
from ..design import darken

_STROKE = f'stroke="{P.INK}" stroke-linejoin="round" stroke-linecap="round"'

# The pointer of a speech bubble. Bubble and tail are outlined as ONE shape, the way the
# characters' merged silhouettes are (`Canvas.union`): all the ink goes down first, then all
# the white, so an outline survives only around the outside of the union and the join is
# exact for any curvature of the bubble.
#
#   ink layers    behind everything: the bubble's own shape grown by the line weight
#                 (`.bubble::before` in CSS) and `tail-line`, the tail path stroked twice the
#                 line weight, of which only the outer half will remain visible;
#   white layers  the bubble's background, then `tail-fill`, the same tail path filled white.
#
# The path is open at x = 44, deep inside the bubble; x = 28 is placed on the bubble's edge.
# CSS sizes, places, mirrors and rotates both tail layers through the shared class `tail`,
# and sets the stroke so that it does not scale with the drawing.
_TAIL_PATH = "M44,0 Q18,11 2,20 Q18,21.5 44,26"
TAIL = (f'<svg class="tail tail-line" viewBox="0 0 44 28" aria-hidden="true"><path d="{_TAIL_PATH}"/></svg>'
        f'<svg class="tail tail-fill" viewBox="0 0 44 28" aria-hidden="true"><path d="{_TAIL_PATH}"/></svg>')
# The curly arrow that leads from a handwritten note to the text.
SQUIGGLE = ('<svg class="squiggle" viewBox="0 0 44 24" aria-hidden="true"><path d="M42,5 Q20,0 6,17 M6,17 l10,-2 '
            f'M6,17 l2,-10" fill="none" stroke="{P.PEN}" stroke-width="2.2" stroke-linecap="round" '
            'stroke-linejoin="round"/></svg>')
# A hand-drawn tick for checklists.
CHECK = (f'<svg viewBox="0 0 30 30" aria-hidden="true"><path d="M5,17 L12,24 L27,4" fill="none" stroke="{P.RED}" '
         'stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
# Small marks drawn, not typed: ✓ ✗ ★ ✦ are missing from the book's fonts, and a glyph the browser has to borrow from
# a system font looks different on every machine (Lucida Grande, for one). Color: currentColor.
_MARK = '<svg class="mark" viewBox="0 0 20 20" aria-hidden="true">{}</svg>'
MARK_TICK = _MARK.format('<path d="M3.5,10.5 L8,15 L16.5,4.5" fill="none" stroke="currentColor" stroke-width="3.2" '
                         'stroke-linecap="round" stroke-linejoin="round"/>')
MARK_CROSS = _MARK.format('<path d="M4.5,4.5 L15.5,15.5 M15.5,4.5 L4.5,15.5" fill="none" stroke="currentColor" '
                          'stroke-width="3.2" stroke-linecap="round"/>')
MARK_STAR = _MARK.format('<path d="M10,1.5 L12.5,7.2 L18.6,7.6 L13.9,11.6 L15.4,17.6 L10,14.3 L4.6,17.6 L6.1,11.6 '
                         'L1.4,7.6 L7.5,7.2 Z" fill="currentColor"/>')
_BURST_MARKS = {"✓": '<path d="M33,52 L45,64 L68,36" fill="none" stroke="{ink}" stroke-width="8.5" '
                     'stroke-linecap="round" stroke-linejoin="round"/>',
                "✦": '<path d="M50,27 Q53,47 73,50 Q53,53 50,73 Q47,53 27,50 Q47,47 50,27 Z" fill="{ink}"/>'}
ICON_FOLDER = (f'<svg class="t-icon" viewBox="0 0 26 20" aria-hidden="true"><path d="M2,4 L10,4 L12,7 L24,7 L24,18 '
               f'L2,18 Z" fill="{P.YELLOW}" {_STROKE} stroke-width="2"/></svg>')
ICON_FILE = (f'<svg class="t-icon" viewBox="0 0 26 20" aria-hidden="true"><path d="M7,1.5 L16,1.5 L20,5.5 L20,18.5 '
             f'L7,18.5 Z" fill="{P.WHITE}" {_STROKE} stroke-width="2"/>'
             f'<path d="M10,9 h7 M10,13 h7" stroke="{P.INK}" stroke-width="1.4"/></svg>')


def grip(css_class: str, color: str) -> str:
    """Fingers curled over the top edge of a poster."""
    c = Canvas()
    c.path("M3,6 Q3,2 8,2 L28,2 Q33,2 33,6 L33,16 Q33,22 29,22 Q25,22 25,18 Q25,22 21.5,22 "
           "Q18,22 18,18 Q18,22 14.5,22 Q11,22 11,18 Q11,22 7,22 Q3,22 3,16 Z", color, 2.4)
    c.line("M11,10 V18 M18,10 V18 M25,10 V18", 1.8)
    return svg(c.render(), 36, 24, css_class=f"grip {css_class}")


def burst(symbol: str) -> str:
    """A jagged starburst with a symbol; its fill is the CSS variable `--c` of the callout."""
    points = []
    for i in range(24):
        radius = 48 if i % 2 == 0 else 35
        a = math.tau * i / 24 - math.pi / 2
        points.append(f"{50 + radius * math.cos(a):.1f},{50 + radius * math.sin(a):.1f}")
    return (f'<svg class="burst" viewBox="0 0 100 100" aria-hidden="true"><polygon points="{" ".join(points)}" '
            f'style="fill:var(--c)" stroke="{P.INK}" stroke-width="4" stroke-linejoin="round"/>'
            + (_BURST_MARKS[symbol].format(ink=P.INK) if symbol in _BURST_MARKS else
               f'<text x="50" y="61" text-anchor="middle" fill="{P.INK}">{symbol}</text>') + '</svg>')


def _computer_base() -> str:
    """System unit and keyboard drawn under the prompt monitor."""
    c = Canvas()
    c.shape("M196,0 L188,12 L252,12 L244,0 Z", darken(P.BEIGE, 0.88), sw=2.3, light=None)
    c.shape(rounded_rect_d(56, 11, 328, 28, 5), P.BEIGE, sw=2.4, light=(-3, -3), shade_k=0.86)
    c.line("M74,19 h64 M74,25 h64 M74,31 h64", 1.5, opacity=0.6)
    c.add(f'<rect x="262" y="21" width="84" height="7" rx="2" fill="{P.DESK}" stroke="{P.INK}" stroke-width="1.6"/>')
    c.add(f'<circle cx="244" cy="24.5" r="3" fill="{P.GREEN}" stroke="{P.INK}" stroke-width="1.2"/>')
    c.shape("M74,50 L366,50 L390,84 L50,84 Z", P.BEIGE_DARK, sw=2.4, light=(-3, -2))
    c.line("M71,58 H369 M65,66 H375 M59,74 H381", 1.4)
    for i in range(1, 15):
        x = 74 + i * 19.5
        c.line(f"M{x:.1f},51 L{x + (x - 220) * 0.07:.1f},74", 1.1)
    c.line("M150,79 H290", 2)
    return svg(c.render(), 440, 88, css_class="crt-base head-only")


COMPUTER_BASE = _computer_base()

# The folded corner of a sheet of paper. The sheet itself is clipped along the diagonal; this
# drawing sits in the cut and supplies the flap and the ink along its edges.
SHEET_FOLD = (f'<svg class="sheet-fold" viewBox="0 0 28 28" aria-hidden="true">'
              f'<path d="M0,0 L28,28 L4,28 Q0,28 0,24 Z" fill="{P.PAPER_FOLD}" stroke="{P.INK}" stroke-width="2.3" '
              f'stroke-linejoin="round"/><path d="M0,0 L28,28" stroke="{P.INK}" stroke-width="4.6"/></svg>')

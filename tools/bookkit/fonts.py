"""The book's fonts as the browser gets them: every weight of a variable font as a static font of its own.

Chrome prints text in a variable font as a Type 3 font - glyphs as drawings, no hinting - which some PDF viewers
render coarsely and slowly, and repeats it for every page. A static font is embedded as an ordinary TrueType
subset. The variable files stay as they are in `theme/fonts`; their weights are cut out once and cached.
"""
from __future__ import annotations

import hashlib
import os
import tempfile
from functools import cache
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

from .design import FONT_FILES

FONTS = Path(__file__).resolve().parent / "theme" / "fonts"
CACHE = Path(tempfile.gettempdir()) / "bookkit" / "fonts"


def _weights(weight: str) -> list[int]:
    low, _, high = weight.partition(" ")
    return list(range(int(low), int(high or low) + 1, 100))


@cache
def _digest(path: Path) -> str:
    """The font file's fingerprint: an edited font is cut anew, not served stale from the cache."""
    return hashlib.sha1(path.read_bytes()).hexdigest()[:10]


def static_weight(path: Path, weight: int) -> Path:
    """The variable font at `path` fixed at one weight, from the cache or made now. Written whole and then moved
    into place, so builds running side by side never read half a file."""
    target = CACHE / f"{path.stem}-{weight}-{_digest(path)}.ttf"
    if not target.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        font = TTFont(path)
        axes = {axis.axisTag: axis.defaultValue for axis in font["fvar"].axes}   # every other axis at its default
        font = instancer.instantiateVariableFont(font, {**axes, "wght": weight})
        names = font["name"]
        family = (names.getDebugName(6) or path.stem).split("-")[0]
        for record in [r for r in names.names if r.nameID == 6]:      # the PostScript name the PDF shows
            names.setName(f"{family}-W{weight}", 6, record.platformID, record.platEncID, record.langID)
        partial = target.with_name(f".{target.name}.{os.getpid()}")
        font.save(partial)
        partial.replace(target)
    return target


def font_faces() -> str:
    """`@font-face` rules for the bundled fonts, one per weight of every variable font."""
    rules = []
    for family, file, weight, style in FONT_FILES:
        path = FONTS / file
        variable = "fvar" in TTFont(path, lazy=True)
        for value in _weights(weight) if variable else [weight]:
            source = static_weight(path, value) if variable else path
            rules.append(f'@font-face{{font-family:"{family}";src:url("{source.as_uri()}");font-weight:{value};'
                         f'font-style:{style};}}')
    return "\n".join(rules)

"""Proof sheets: PNG overviews of what the design system offers.

They exist so that choices are made by looking instead of inventing: every pose and mood of
every character, every color token, every doodle.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

from . import design
from .fonts import font_faces
from .art.characters import MODULES, MOODS, figure
from .art.doodles import DOODLES, doodle
from .config import BookConfig
from .render import screenshot_html

_BASE_STYLE = (f"body{{margin:24px;background:{design.PAPER};font:13px Rubik,sans-serif;color:{design.INK}}}"
               "h2{font:800 22px Rubik;margin:18px 0 6px} code{font:500 13px 'JetBrains Mono';opacity:.6}"
               ".r{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:8px} .c{width:150px;text-align:center}"
               "b{display:block;font-weight:600}")


def _shoot(body: str, style: str, out: Path, width: int) -> Path:
    fonts = font_faces()
    out.parent.mkdir(parents=True, exist_ok=True)
    return screenshot_html(f'<meta charset="utf-8"><style>{fonts}{_BASE_STYLE}{style}</style>{body}', out,
                           width=width, height=900, scale=2)


def character_sheet(config: BookConfig, out: Path) -> Path:
    """Every pose of every character as a full figure, and every mood as a portrait."""
    cells = []
    for name, module in MODULES.items():
        cells.append(f"<h2>{escape(config.character(name)['name'])} <code>{name}</code></h2><div class='r'>")
        cells += [f"<div class='c'>{figure(name, pose, 'smile')}<b>pose={pose}</b></div>" for pose in module.POSES]
        cells.append("</div><div class='r'>")
        cells += [f"<div class='c s'>{figure(name, 'stand', mood, bust=True)}<b>mood={mood}</b></div>"
                  for mood in MOODS]
        cells.append("</div>")
    return _shoot("".join(cells), ".c svg{height:200px;width:150px} .c.s svg{height:120px}", out, 1640)


def doodle_sheet(out: Path) -> Path:
    """Every doodle with its name."""
    cells = "".join(f"<div class='c'>{doodle(name)}<b>{name}</b></div>" for name in DOODLES)
    return _shoot(f"<div class='r'>{cells}</div>", ".c svg{width:150px}", out, 1640)


def palette_sheet(out: Path) -> Path:
    """Every color token as a labelled swatch."""
    cells = "".join(f'<div class="s"><i style="background:{value}"></i><b>{name}</b><code>{value}</code></div>'
                    for name, value in design.palette().items())
    style = (".g{display:grid;grid-template-columns:repeat(6,1fr);gap:14px}"
             f".s i{{display:block;height:56px;border:2px solid {design.INK};border-radius:8px;margin-bottom:4px}}")
    return _shoot(f"<div class='g'>{cells}</div>", style, out, 1300)

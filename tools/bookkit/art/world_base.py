"""The types of a chapter world and the registry every world module adds itself to (`world`).

Kept apart from `worlds.py`, which loads every world: a world module imports only this, so any of them can be
imported first.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .footers import Strip


@dataclass(frozen=True)
class Station:
    """One step of the machine. `draw(s, beat)` draws the station in a frame; `beats` are its moments in order -
    a station shown on several pages shows them in turn."""
    key: str                                   # its label in the locale (`worlds: <world>: <key>`)
    draw: Callable[[Strip, str], None]
    beats: tuple[str, ...] = ("work",)


@dataclass
class World:
    """A chapter's world: its stations left to right, the backdrop of every frame, the finale and the opener."""
    name: str
    stations: list[Station] = field(default_factory=list)
    backdrop: Callable[[Strip, int], None] | None = None     # (strip, station index) -> the place behind it
    finale: Callable[[Strip], None] | None = None             # every station at once, running and labelled
    opener: str = ""                                          # the name of its opener in `OPENERS`
    alternate: bool = False                                   # a station's beats take turns page by page
    floppy: tuple[str, str] | None = None                     # (station, beat) hiding the golden floppy


WORLDS: dict[str, World] = {}


def world(name: str, opener: str) -> World:
    """Register a world; its module then adds stations with `World.stations.append`."""
    if name in WORLDS:
        raise ValueError(f"world {name!r} registered twice")
    WORLDS[name] = World(name, opener=opener)
    return WORLDS[name]

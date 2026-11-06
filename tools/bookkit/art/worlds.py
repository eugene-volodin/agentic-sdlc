"""Chapter worlds: one place per chapter, one machine in it, and a camera that travels along it page by page.

Footers must show at a glance who does what, where and why. So a chapter may live in a *world* (`world:` in its
front matter): one long place - a space station, a kitchen, a beach - with one
machine standing in it from left to right as a row of *stations*, each a step of the chapter's idea.

* The chapter's opener shows the whole world from outside, the machine still off.
* The footers are a camera moving along the machine: page after page it moves on to the next station, and a
  station that gets several pages shows its *beats* in turn - the work, the hitch, the fix. Every frame shows
  one station whole, between its walls, so nothing is ever cut by the frame.
* The last page of the chapter shows the finale: every station at once, the machine running, each one labelled
  - the chapter in one picture.
* The characters keep their roles: the professor sets the task, the agent works, the cat checks and explains,
  the caterpillar doubts and tests, the sparrow gets into everything (and is after the big red button all book).

A world is a module of its own (`world_space.py`, ...) that registers itself in `WORLDS`. It draws the backdrop of
a frame, each station, the finale and the opener; the lettering lives in the locale under `worlds: <name>:`.
Frames draw on a footer `Strip` (`footers.py`): the same boxes, groups and no-overlap check as everything else.
"""
from __future__ import annotations

from . import (  # noqa: F401  (each world registers itself in WORLDS on import)
    world_attic, world_camp, world_city, world_courtyard, world_fair, world_harbour, world_kitchen, world_lab,
    world_library, world_moon, world_railway, world_sea, world_space,
)
from .flipbook import flipbook
from .footers import Strip, look_for
from .world_base import WORLDS, Station, World, world  # noqa: F401  (the registry, re-exported)


def schedule(world_: World, pages: int) -> list[tuple[int, str] | None]:
    """What each of a chapter's `pages` footers shows: (station index, beat), or None for the finale.

    The last footer is always the finale, however tall or short the footers before it. The others go along the
    stations in order, never back. When there are at least as many as stations, every station gets a share in
    proportion to its beats (a station of two moments gets twice the pages of a station of one), and within its
    run its beats come in order, each held for an equal stretch - the hitch is never crowded out by the work; in a
    world that `alternate`s, they take turns instead, so that two pages in a row never show one moment. A
    chapter shorter than its machine visits stations spread evenly from the first to the last, each at its first
    beat; the finale shows them all."""
    if pages <= 0:
        return []
    frames = pages - 1
    beats = [len(station.beats) for station in world_.stations]
    count = len(beats)
    if frames < count:
        picked = [round(i * (count - 1) / max(1, frames - 1)) for i in range(frames)]
        return [*((i, world_.stations[i].beats[0]) for i in picked), None]
    share = [1] * count                                       # every station once, the rest by weight
    for _ in range(frames - count):
        i = min(range(count), key=lambda j: (share[j] / beats[j], -beats[j], j))
        share[i] += 1
    plan: list[tuple[int, str] | None] = []
    for i, run in enumerate(share):
        names = world_.stations[i].beats
        if world_.alternate:
            plan += [(i, names[step % len(names)]) for step in range(run)]
        else:
            plan += [(i, names[min(len(names) - 1, step * len(names) // run)]) for step in range(run)]
    return [*plan, None]


def egg_page(world_: World, places: list[tuple[int, str] | None]) -> int | None:
    """Which of a chapter's footers hides its world's golden floppy (`world_kit.hide`): the first page of the
    declared station at the declared beat, or failing that the station's first page; None when the chapter never
    shows the station (or the world hides none)."""
    if world_.floppy is None:
        return None
    key, beat = world_.floppy
    index = [one.key for one in world_.stations].index(key)
    for wanted in ((index, beat), None):
        for nth, place in enumerate(places):
            if place is not None and (place == wanted or wanted is None and place[0] == index):
                return nth
    return None


def egg_letter(vocabulary: dict, chapter_index: int) -> str | None:
    """The letter on chapter `chapter_index`'s floppy: the locale's `easter: floppies:`, in chapter order."""
    letters = (vocabulary.get("easter") or {}).get("floppies") or []
    return str(letters[chapter_index - 1]) if 1 <= chapter_index <= len(letters) else None


def frame(world_: World, h: float, place: tuple[int, str] | None, clear: str | None, chapter_index: int,
          accent: str, words: dict, seed: int = 0, egg: str | None = None,
          flip: int | None = None) -> tuple[str, Strip]:
    """Draw one footer of a world: a station at a beat, or the finale (`place` is None); `egg` is the letter of
    the golden floppy when this frame hides it, `flip` the page's place in the chapter for the flip-book sparrow."""
    s = Strip(h, seed, clear, look_for(chapter_index, accent), words)
    s.egg = egg
    if place is None:
        if world_.finale:
            world_.finale(s)
    else:
        index, beat = place
        if world_.backdrop:
            world_.backdrop(s, index)
        world_.stations[index].draw(s, beat)
        if egg and not getattr(s, "eggs", None):        # no room at its spot in this frame: dropped on the floor
            from .world_kit import stash_along
            floor = max((b.bottom for b in s.boxes if b.kind == "actor"), default=s.feet(s.x(0.5)))
            stash_along(s, [s.x(i / 20) for i in (2, 18, 6, 14, 10, 4, 16, 8, 12, 1, 19)], floor, floor + 0.5)
    if flip is not None:
        flipbook(s, flip)
    return s.svg("scene-svg", align="xMidYMax"), s


def world_footers(world_: World, requests: list[dict], vocabulary: dict, chapter_index: int,
                  trace: list | None = None) -> list[str]:
    """The footers of one chapter living in `world_`, in the order of its pages. `trace`, when given, receives what
    each frame shows and its drawn strip, for `book audit`."""
    from .. import design as P

    words = (vocabulary.get("worlds") or {}).get(world_.name) or {}
    places = schedule(world_, len(requests))
    hidden, letter = egg_page(world_, places), egg_letter(vocabulary, chapter_index)
    out = []
    for nth, (request, place) in enumerate(zip(requests, places, strict=True)):
        h = round(float(request["mm"]) * P.SCENE_UNITS_PER_PAGE_MM)
        svg, strip = frame(world_, h, place, request.get("clear"), chapter_index,
                           str(request.get("accent") or P.YELLOW), words, seed=nth,
                           egg=letter if nth == hidden else None, flip=nth)
        out.append(svg)
        if trace is not None:
            trace.append(moment(world_, place, strip))
    return out


def moment(world_: World, place: tuple[int, str] | None, strip: Strip) -> dict:
    """What a frame shows, for `book audit`: the world, the station and the beat (None for the finale), and the strip
    it was drawn on."""
    station = world_.stations[place[0]].key if place else None
    return {"kind": "world", "world": world_.name, "station": station, "beat": place[1] if place else None,
            "strip": strip}


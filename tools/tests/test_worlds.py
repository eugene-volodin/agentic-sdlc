"""Chapter worlds: the camera visits every station in order, every frame draws clean, the finale closes the chapter."""
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from bookkit import design
from bookkit.art.footers import footer_conflicts, footers
from bookkit.art.openers import W, conflicts, opener
from bookkit.art.worlds import WORLDS, frame, schedule
from bookkit.config import LOCALES

LOCALE = yaml.safe_load((LOCALES / "ru.yml").read_text(encoding="utf-8"))
HEIGHTS = (136, 220, 320, 560, 760)


@pytest.mark.parametrize("pages", range(1, 41))
def test_the_camera_goes_along_the_machine_and_ends_on_the_finale(pages):
    for world in WORLDS.values():
        plan = schedule(world, pages)
        assert len(plan) == pages and plan[-1] is None and None not in plan[:-1]
        stations = [place[0] for place in plan[:-1]]
        assert stations == sorted(stations)                      # never back along the machine
        if not stations:
            continue
        assert stations[0] == 0
        if len(stations) >= 2:
            assert stations[-1] == len(world.stations) - 1       # the last station is always reached
        if pages - 1 >= len(world.stations):
            assert set(stations) == set(range(len(world.stations)))
        for index, station in enumerate(world.stations):        # each run shows its beats in order - or, in a
            run = [beat for i, beat in plan[:-1] if i == index]  # world that alternates, taking turns
            order = [station.beats.index(beat) for beat in run]
            if world.alternate:
                assert order == [step % len(station.beats) for step in range(len(run))], (pages, index, run)
            else:
                assert order == sorted(order), (pages, index, run)
            if len(run) >= len(station.beats):
                assert set(run) == set(station.beats), (pages, index, run)


@pytest.mark.parametrize("pages", range(8, 41))
def test_a_station_gets_pages_by_its_beats_never_more(pages):
    """A station of two moments gets about twice the pages of a station of one; no station hogs the chapter."""
    for world in WORLDS.values():
        plan = schedule(world, pages)
        runs = [sum(1 for place in plan[:-1] if place[0] == i) for i in range(len(world.stations))]
        weights = [len(station.beats) for station in world.stations]
        per_beat = [run / weight for run, weight in zip(runs, weights, strict=True)]
        assert max(per_beat) - min(per_beat) <= 1, (pages, runs)


def test_a_chapter_alone_draws_the_same_frames_as_in_the_whole_book():
    """`--only` builds one chapter: its world's footers must not depend on what other chapters are built."""
    def request(chapter, mm):
        return {"chapter": chapter, "world": "station", "mm": mm, "clear": "right", "accent": design.ORANGE}

    vocabulary = {"worlds": LOCALE["worlds"]}
    alone = [request("3", mm) for mm in (55, 55, 120, 55)]
    other = [request("7", mm) for mm in (55, 90)]
    same = re.compile(r'(id="|url\(#|href="#)[^")]+')
    together = footers(other + alone, vocabulary)[len(other):]
    assert [same.sub("", svg) for svg in together] == [same.sub("", svg) for svg in footers(alone, vocabulary)]


@pytest.mark.parametrize("name", sorted(WORLDS))
def test_every_station_beat_and_the_finale_draw_clean_at_every_height(name):
    world = WORLDS[name]
    words = LOCALE["worlds"][name]
    places = [(i, beat) for i, station in enumerate(world.stations) for beat in station.beats] + [None]
    for place in places:
        for h in HEIGHTS:
            for clear in ("left", "right"):
                svg, strip = frame(world, h, place, clear, 3, design.ORANGE, words)
                assert svg.startswith("<svg"), (place, h)
                assert footer_conflicts(strip) == [], (place, h, clear)


@pytest.mark.parametrize("name", sorted(name for name, w in WORLDS.items() if w.opener))  # the courtyard's: none
def test_the_worlds_opener_draws_clean(name):
    world = WORLDS[name]
    drawn = opener(world.opener, design.ORANGE, seed=3, words=LOCALE["openers"].get(world.opener) or {})
    assert conflicts(drawn) == []


def test_every_station_has_its_label_in_the_locale():
    for name, world in WORLDS.items():
        assert {station.key for station in world.stations} <= set(LOCALE["worlds"][name])


# Frames that once broke between the sampled heights: a footer grown to fill a page may take any height.
BETWEEN = [("harbour", "entrance", "open", 160), ("harbour", "entrance", "wait", 192),
           ("station", "task", "work", 264), ("station", "tools", "work", 576), ("station", "mcp", "work", 568),
           ("station", "mcp", "work", 208), ("railway", "small", "telegram", 288), ("railway", "no-human", "past", 272),
           ("railway", "no-human", "past", 296), ("railway", None, None, 288)]


@pytest.mark.parametrize("name,key,beat,h", BETWEEN)
def test_frames_between_the_sampled_heights_draw_clean_and_whole(name, key, beat, h):
    world = WORLDS[name]
    keys = [station.key for station in world.stations]
    place = None if key is None else (keys.index(key), beat)
    for clear in ("left", "right"):
        for seed in (0, 1):
            _, strip = frame(world, h, place, clear, 3, design.ORANGE, LOCALE["worlds"][name], seed)
            assert footer_conflicts(strip) == [], (clear, seed)
            assert all(b.top >= -0.5 and b.left >= -0.5 and b.right <= W + 0.5 for b in strip.boxes), (clear, seed)


ART = Path(__file__).resolve().parents[1] / "bookkit" / "art"
FIRST = sorted(p.stem for p in ART.glob("world*.py")) + ["openers", "stories"]


@pytest.mark.parametrize("module", FIRST)
def test_any_world_module_can_be_imported_first(module):
    """No import cycle: each world module, the registry and the openers load on their own in a fresh interpreter."""
    done = subprocess.run([sys.executable, "-c", f"import bookkit.art.{module}"], capture_output=True, text=True,
                          cwd=ART.parents[1])
    assert done.returncode == 0, done.stderr.strip().splitlines()[-1:]

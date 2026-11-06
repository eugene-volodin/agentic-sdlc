"""The easter eggs: a golden floppy hidden in every chapter world, its letters spelling a
word in chapter order; every wall clock at 4:04; the flip-book sparrow by the page-number tag, never on anything."""
import re

import pytest
import yaml

from bookkit import design
from bookkit.art.worlds import WORLDS, egg_letter, egg_page, frame, schedule  # first: it loads the worlds
from bookkit.art.flipbook import FLIER, FRAMES, flipbook, tag_box  # noqa: E402
from bookkit.art.footers import LOOKS, Strip, footer_conflicts  # noqa: E402
from bookkit.art.openers import W, opener  # noqa: E402
from bookkit.art.world_kit import CLOCK_TIME, container_faults, link_faults  # noqa: E402
from bookkit.config import LOCALES

LOCALE = yaml.safe_load((LOCALES / "ru.yml").read_text(encoding="utf-8"))
LETTERS = [str(x) for x in LOCALE["easter"]["floppies"]]
# The worlds of the chapters, in chapter order.
CHAPTERS = ("kitchen", "fair", "station", "library", "attic", "sea", "lab", "harbour", "moon")
HEIGHTS = (136, 220, 320)


def _hidden(name):
    world = WORLDS[name]
    key, beat = world.floppy
    return world, [one.key for one in world.stations].index(key), beat


@pytest.mark.parametrize("name", CHAPTERS)
def test_the_floppy_is_drawn_whole_and_clean_wherever_it_hides(name):
    """The frame that hides the floppy draws exactly one, at every height, side and camera, and it keeps every
    rule of a frame: no overlaps, containers and lines whole, nothing cut by the frame."""
    world, index, beat = _hidden(name)
    words = LOCALE["worlds"][name]
    for h in HEIGHTS:
        for clear in ("left", "right"):
            for seed in (0, 1, 2):
                s = frame(world, h, (index, beat), clear, 3, design.ORANGE, words, seed, egg="A")[1]
                where = (name, h, clear, seed)
                floppies = [b for b in s.boxes if b.name == "floppy"]
                assert len(floppies) == 1, where
                b = floppies[0]
                assert b.left >= 0 and b.top >= 0 and b.right <= W and b.bottom <= s.h, where
                assert footer_conflicts(s) == [], where
                assert container_faults(s) == [] and link_faults(s) == [], where


@pytest.mark.parametrize("pages", range(10, 41))
def test_every_chapter_hides_exactly_one_floppy_and_the_letters_spell_the_word(pages):
    """However long a chapter, its world's floppy lies on exactly one of its pages; read in chapter order, the
    letters are the locale's word."""
    spelled = []
    for number, name in enumerate(CHAPTERS, 1):
        world = WORLDS[name]
        places = schedule(world, pages)
        hidden = egg_page(world, places)
        assert hidden is not None, (name, pages)
        letter = egg_letter({"easter": LOCALE["easter"]}, number)
        drawn = []
        for nth, place in enumerate(places):
            if place is None or place[0] != places[hidden][0]:
                continue                                   # only the floppy's station can draw it
            s = frame(world, 220, place, "right", number, design.ORANGE, LOCALE["worlds"][name], nth,
                      egg=letter if nth == hidden else None)[1]
            drawn += [nth for b in s.boxes if b.name == "floppy"]
        assert drawn == [hidden], (name, pages, drawn)
        spelled.append(letter)
    assert "".join(spelled) == "".join(LETTERS) == "AGENTS.md"


def _all_svg(name):
    world = WORLDS[name]
    words = LOCALE["worlds"][name]
    places = [(i, beat) for i, station in enumerate(world.stations) for beat in station.beats] + [None]
    for place in places:
        for h in (320, 560):
            yield place, frame(world, h, place, "right", 3, design.ORANGE, words)[0]
    if world.opener:                               # the courtyard's worlds have no opener
        yield "opener", opener(world.opener, design.ORANGE, 3, words=LOCALE["openers"].get(world.opener) or {}).svg


def test_every_wall_clock_shows_four_minutes_past_four():
    """Every clock drawn in the worlds keeps the same time, 4:04 - the harbour office's clock alone runs on, by the
    minutes the check takes (its "done" beat and its finale show the check twenty-five minutes on)."""
    told = f"{CLOCK_TIME[0]}:{CLOCK_TIME[1]:02d}"
    seen = {}
    for name in CHAPTERS:
        for place, svg in _all_svg(name):
            for time in re.findall(r'data-clock="([^"]+)"', svg):
                seen.setdefault(name, set()).add(time)
                if name == "harbour" and (place is None or place != "opener" and place[1] == "done"):
                    continue
                assert time == told, (name, place, time)
    assert {"kitchen", "library", "attic", "lab", "harbour"} <= set(seen)


@pytest.mark.parametrize("h", (136, 138, 220, 321, 457))
def test_the_flipbook_sparrow_never_lands_on_anything(h):
    """Over a whole flight, at every height and on both sides, the sparrow stays clear of every thing and
    character of the scene and of the page-number tag, whole inside the footer, and never in a frame where the
    scene has its own sparrow."""
    drawn = 0
    for name, world in sorted(WORLDS.items()):
        words = LOCALE["worlds"][name]
        for nth in range(len(FRAMES)):
            index = nth % len(world.stations)
            beat = world.stations[index].beats[0]
            for clear in ("left", "right"):
                s = frame(world, h, (index, beat), clear, 3, design.ORANGE, words, nth, flip=nth)[1]
                box = getattr(s, "flipbook", None)
                if box is None:
                    continue
                drawn += 1
                assert not any(b.kind == "actor" and b.name == FLIER for b in s.boxes), (name, nth, clear)
                assert box[0] >= 0 and box[1] >= 0 and box[2] <= W and box[3] <= s.h, (name, nth, clear)
                assert not any(b.hits(box, 2) for b in s.boxes), (name, nth, clear)
                tag = tag_box(s)
                assert not (box[0] < tag[2] and tag[0] < box[2] and box[1] < tag[3] and tag[1] < box[3])
    assert drawn > 0


def test_the_flipbook_restarts_with_every_chapter_and_skips_a_full_corner():
    s = Strip(136, 0, "right", LOOKS[0], {})
    s.put(1, "", (W - 120, 0, W, 136), "wall")          # something fills the whole corner
    assert flipbook(s, 0) is None

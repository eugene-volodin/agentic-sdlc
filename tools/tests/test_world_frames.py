"""Nothing in a world's frame is cut by the frame: every character and every station's thing lies whole inside it,
with a band of floor left visible under the feet - at every station, beat, height and side:
nothing is cut at the bottom or at the top of a picture. And two pages in a row never show
one picture: the same station's next page is another beat or another camera.
"""
import re

import pytest
import yaml

from bookkit import design
from bookkit.art.worlds import WORLDS, frame, schedule  # first: it loads the worlds
from bookkit.art.openers import W  # noqa: E402
from bookkit.config import LOCALES

LOCALE = yaml.safe_load((LOCALES / "ru.yml").read_text(encoding="utf-8"))
HEIGHTS = (136, 138, 220, 321, 457, 518, 596, 760)   # 34 mm up to FOOT_MAX: a footer grown to fill a page
# every world, drawn with the close camera
CAMERA = ("kitchen", "fair", "station", "library", "attic", "sea", "lab", "harbour", "moon", "camp",
          "railway", "courtyard", "front", "city")
FLOOR = 0.12                                       # the share of a frame's height kept as floor under the feet


def _frames():
    for name in CAMERA:
        world = WORLDS[name]
        words = LOCALE["worlds"][name]
        places = [(i, beat) for i, station in enumerate(world.stations) for beat in station.beats] + [None]
        for place in places:
            for h in HEIGHTS:
                for clear in ("left", "right"):
                    for seed in (0, 1):
                        yield (name, place, h, clear, seed), frame(world, h, place, clear, 3, design.ORANGE, words,
                                                                   seed)[1]


@pytest.mark.parametrize("where,s", list(_frames()), ids=lambda v: str(v)[:60])
def test_nothing_is_cut_and_the_floor_shows(where, s):
    floor = s.h * (1 - FLOOR)
    faults = []
    for b in s.boxes:
        if b.kind == "actor" and b.bottom > floor + 0.5:
            faults.append(f"{b.name} stands at {b.bottom:.0f}, the floor band starts at {floor:.0f}")
        if b.top < -0.5 or b.bottom > s.h + 0.5 or b.left < -0.5 or b.right > W + 0.5:
            faults.append(f"{b.name} is cut by the frame: {b.left:.0f},{b.top:.0f} - {b.right:.0f},{b.bottom:.0f}")
    assert faults == [], where


NEGATIVE = re.compile(r'\b(width|height|r)="-')


@pytest.mark.parametrize("name", CAMERA)
def test_no_shape_has_a_negative_size_in_a_tall_frame(name):
    """A footer grown to fill a page draws a station far taller than its usual strip: no part of it may come out with
    a negative width, height or radius (the browser rejects it, and the audit reports it)."""
    world = WORLDS[name]
    words = LOCALE["worlds"][name]
    for i, station in enumerate(world.stations):
        for beat in station.beats:
            for h in (420, 596, 760):
                for clear in ("left", "right"):
                    svg = frame(world, h, (i, beat), clear, 3, design.ORANGE, words, 0)[0]
                    assert not NEGATIVE.search(svg), (name, station.key, beat, h, clear)


@pytest.mark.parametrize("name", CAMERA)
def test_two_pages_of_one_beat_differ(name):
    """The pages of one beat, one after another (seed 0 and 1), mirror the station or change the camera."""
    world = WORLDS[name]
    words = LOCALE["worlds"][name]
    for i, station in enumerate(world.stations):
        for beat in station.beats:
            for h in (136, 221, 321):
                a = frame(world, h, (i, beat), "right", 3, design.ORANGE, words, 0)[1]
                b = frame(world, h, (i, beat), "right", 3, design.ORANGE, words, 1)[1]
                where = (name, station.key, beat, h)
                assert _layout(a) != _layout(b), where


def _layout(s) -> list:
    return sorted((x.name, round(x.left), round(x.top)) for x in s.boxes if x.kind in ("actor", "thing"))


@pytest.mark.parametrize("name", CAMERA)
def test_two_pages_in_a_row_show_another_moment(name):
    """Along a chapter of any length, two footers in a row at one station show another beat (where the station has
    more than one) and another cast or another camera distance - a mirror alone is not another picture."""
    world = WORLDS[name]
    words = LOCALE["worlds"][name]
    for pages in range(len(world.stations) + 1, 3 * len(world.stations) + 2):
        plan = schedule(world, pages)
        for nth in range(len(plan) - 2):
            a, b = plan[nth], plan[nth + 1]
            if a is None or b is None or a[0] != b[0]:
                continue
            where = (name, pages, nth, a, b)
            if len(world.stations[a[0]].beats) > 1:
                assert a[1] != b[1], where
            sa = frame(world, 221, a, "right", 3, design.ORANGE, words, nth)[1]
            sb = frame(world, 221, b, "right", 3, design.ORANGE, words, nth + 1)[1]
            cast_a = sorted(x.name for x in sa.boxes if x.kind == "actor")
            cast_b = sorted(x.name for x in sb.boxes if x.kind == "actor")
            assert cast_a != cast_b or abs(sa.tall - sb.tall) > 1, where


def _railway_frames():
    world = WORLDS["railway"]
    words = LOCALE["worlds"]["railway"]
    places = [(i, beat) for i, station in enumerate(world.stations) for beat in station.beats] + [None]
    for place in places:
        for h in HEIGHTS:
            for clear in ("left", "right"):
                for seed in (0, 1, 2, 3):
                    yield (place, h, clear, seed), frame(world, h, place, clear, 3, design.ORANGE, words, seed)[1]


@pytest.mark.parametrize("where,s", list(_railway_frames()), ids=lambda v: str(v)[:60])
def test_railway_cast_keeps_clear_of_the_track_and_the_trains(where, s):
    """On the railway nobody standing on the platform is drawn over a vehicle (an engine, a coach, a wagon, the
    handcar, a bogie, the buffer stop with its engine); only one riding it - standing on its deck - is, and the
    sparrow, who perches. In a frame taller than a strip the near platform is deep enough that the whole cast stands
    below its coping, never over the rails behind."""
    from bookkit.art.world_railway import VEHICLES, low
    vehicles = [b for b in s.boxes if b.name.rstrip("0123456789") in VEHICLES and b.kind != "actor"]
    faults = []
    for a in s.boxes:
        if a.kind != "actor" or a.name == "sparrow":
            continue
        for v in vehicles:
            riding = a.group == v.group and a.bottom < v.bottom - 1
            if not riding and a.hits(v):
                faults.append(f"{a.name} over the {v.name}")
        on_platform = a.bottom > s.line.kerb
        if not low(s) and on_platform and a.top < s.line.kerb - 0.5:
            faults.append(f"{a.name} over the track: top {a.top:.0f}, the coping at {s.line.kerb:.0f}")
    assert faults == [], where

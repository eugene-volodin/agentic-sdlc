"""The space station's own story: what rides the line, what the colours mean, what the tall frames and the opener
show. The kit's two rules are checked for every world in `test_world_kit.py`."""
import yaml

from bookkit import design
from bookkit.art.worlds import WORLDS, frame  # first: it loads the worlds in their order
from bookkit.art import world_space as ws  # noqa: E402
from bookkit.art.openers import opener  # noqa: E402
from bookkit.config import LOCALES

LOCALE = yaml.safe_load((LOCALES / "ru.yml").read_text(encoding="utf-8"))


def test_the_rules_are_in_force():
    """The station does use containers and connections."""
    strip = _station_frame(2, "work")
    assert strip.holders and strip.links and strip.ports
    assert {link.kind for link in strip.links} >= {"cable", "tube"}


def _station_frame(index, beat, h=320, seed=1):
    return frame(WORLDS["station"], h, (index, beat), "right", 3, design.ORANGE, LOCALE["worlds"]["station"], seed)[1]


def test_capsules_ride_the_live_line_and_multiply_as_the_chapter_goes_on():
    world = WORLDS["station"]
    counts = []
    for index, station in enumerate(world.stations):
        for beat in station.beats:
            strip = _station_frame(index, beat)
            if strip.trunk.state == "off":
                assert all(way == 0 for _, _, way in strip.trunk.riders)   # a dead line carries nothing moving
                continue
            assert strip.trunk.riders, (index, beat)
            counts.append(len(strip.trunk.riders))
    assert counts[-1] > counts[0] and max(counts) >= 4


def test_capsule_colours_mean_what_they_carry():
    """The task rides orange; an answer rides in its service's colour - the satellite's body colour too."""
    assert ws.CARGO["task"] == design.ORANGE
    assert set(ws.SERVICES) <= set(ws.CARGO)
    for strip in (_station_frame(0, "work"), _station_frame(1, "work"), _station_frame(2, "spark")):
        assert {color for _, color, _ in strip.trunk.riders} == {ws.CARGO["task"]}


def test_a_tall_frame_shows_the_services_in_orbit_and_only_open_ones_get_a_beam():
    for index, beat, beamed in ((3, "send", set(ws.SERVICES)), (5, "work", set(ws.SERVICES) - set(ws.SHUT))):
        strip = _station_frame(index, beat, h=760)
        names = {box.name for box in strip.boxes}
        assert {f"sat_{kind}" for kind in ws.SERVICES} <= names, (index, names)
        beams = {link.b.owner for link in strip.links if link.kind == "beam"}
        assert beams == {f"sat_{kind}" for kind in beamed}


def test_the_opener_is_the_picture_of_the_page():
    """The station big and central, the shuttle at its airlock, the four services with their beams."""
    stage = opener("station", design.ORANGE, 3, 140, LOCALE["openers"]["station"])
    parts = [box for box in stage.boxes if box.group == "station"]
    left, top = min(b.left for b in parts), min(b.top for b in parts)
    right, bottom = max(b.right for b in parts), max(b.bottom for b in parts)
    assert right - left >= 0.85 * ws.W and bottom - top >= 300
    assert {"shuttle", "module0", "module5", "antenna", "ring", "cupola"} <= {b.name for b in parts}
    beams = [link for link in stage.links if link.kind == "beam"]
    assert {link.b.owner for link in beams} == {f"sat_{kind}" for kind in ws.SERVICES}

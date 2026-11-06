"""The kit's two rules, over every registered world: every station at every beat, height and side, the finale and
the opener - a new world is checked the moment it registers.

* Containers: whatever is inside a board, plate, panel, screen or tag keeps to its inner box, the inner box keeps
  the padding (8 % of the smaller side, never under the minimum), and parts side by side keep their air.
* Connections: every cable, tube, rod, paper ribbon and beam starts and ends on a declared port, leaves each port
  along its direction, and passes through nothing but the two things it joins - no character either, unless that
  character holds the line's end itself.
"""
import pytest
import yaml

from bookkit import design
from bookkit.art.worlds import WORLDS, frame  # first: it loads the worlds
from bookkit.art.openers import opener  # noqa: E402
from bookkit.art.world_kit import container_faults, link_faults  # noqa: E402
from bookkit.config import LOCALES

LOCALE = yaml.safe_load((LOCALES / "ru.yml").read_text(encoding="utf-8"))
HEIGHTS = (136, 220, 320, 560, 760)


def _stages():
    for name, world in sorted(WORLDS.items()):
        words = LOCALE["worlds"][name]
        places = [(i, beat) for i, station in enumerate(world.stations) for beat in station.beats] + [None]
        for place in places:
            for h in HEIGHTS:
                for clear in ("left", "right"):
                    for seed in (0, 1, 2):
                        yield (name, place, h, clear, seed), frame(world, h, place, clear, 3, design.ORANGE, words,
                                                                   seed)[1]
        for lead in (60, 140, 260) if world.opener else ():   # the courtyard's worlds have no opener
            yield (name, "opener", lead), opener(world.opener, design.ORANGE, 3, lead,
                                                 LOCALE["openers"].get(world.opener) or {})


@pytest.mark.parametrize("where,stage", list(_stages()), ids=lambda v: str(v)[:70])
def test_content_keeps_inside_its_container_and_lines_join_only_their_ports(where, stage):
    assert container_faults(stage) == [], where
    assert link_faults(stage) == [], where


@pytest.mark.parametrize("name", sorted(WORLDS))
def test_the_rules_are_in_force(name):
    """Every world does draw containers - in its frames and on its opener - so the test above is not vacuous. Lines
    are checked wherever a world has them; a world may have none (the kitchen, since it lost its belt)."""
    world = WORLDS[name]
    words = LOCALE["worlds"][name]
    strips = [frame(world, 320, (i, beat), "right", 3, design.ORANGE, words)[1]
              for i, station in enumerate(world.stations) for beat in station.beats]
    assert any(getattr(s, "holders", None) for s in strips)
    if world.opener:                               # the courtyard's worlds have no opener
        drawn = opener(world.opener, design.ORANGE, 3, 140, LOCALE["openers"].get(world.opener) or {})
        assert hasattr(drawn, "links"), "the opener must hand over its containers and lines for the checks"

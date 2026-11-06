"""Every cable, hose, tube and rope bends smoothly: no kink at a corner or where a bend begins, never tighter than
three times its own thickness (a paper ribbon: never so tight its inner edge folds over), and it goes into each
object straight along the object's port, never at an angle into a plug."""
import math
import random

import pytest
import yaml

from bookkit import design
from bookkit.art.curves import eased_points, turns
from bookkit.art.worlds import WORLDS, frame  # first: it loads the worlds
from bookkit.art.openers import opener  # noqa: E402
from bookkit.art.world_kit import fitting_length  # noqa: E402
from bookkit.config import LOCALES

LOCALE = yaml.safe_load((LOCALES / "ru.yml").read_text(encoding="utf-8"))
STEP_MAX = 8.0          # degrees between two consecutive steps along a drawn line: a smooth curve, no corner


def test_a_corner_becomes_a_wide_bend_without_a_kink():
    for turn in (20, 45, 90, 135, 160):
        a = math.radians(turn)
        line = eased_points([(-10, 0), (0, 0), (10 * math.cos(a), 10 * math.sin(a))])
        sharpest, tightest = turns(line)
        assert sharpest <= STEP_MAX, turn
        if turn <= 90:
            assert tightest >= 5.0, (turn, tightest)          # half the run it takes, at a right angle


def test_any_polygon_eases_smoothly_and_keeps_its_ends():
    rnd = random.Random(7)
    for _ in range(200):
        pts = [(rnd.uniform(0, 300), rnd.uniform(0, 200)) for _ in range(rnd.randint(2, 6))]
        line = eased_points(pts, 6, 6)
        assert line[0] == pts[0] and line[-1] == pts[-1]
        sharpest, _ = turns(line)
        turns_in = [abs(math.degrees(math.atan2((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]),
                                                (b[0] - a[0]) * (c[0] - b[0]) + (b[1] - a[1]) * (c[1] - b[1]))))
                    for a, b, c in zip(pts, pts[1:], pts[2:], strict=False)]
        if all(t < 175 for t in turns_in):                      # a hairpin in the polygon itself stays one
            assert sharpest <= STEP_MAX, pts


def _links():
    for name, world in sorted(WORLDS.items()):
        words = LOCALE["worlds"][name]
        places = [(i, beat) for i, station in enumerate(world.stations) for beat in station.beats] + [None]
        for place in places:
            for h in (136, 220, 320, 560, 760):
                strip = frame(world, h, place, "right", 3, design.ORANGE, words)[1]
                for link in getattr(strip, "links", []):
                    yield (name, place, h, link.kind, link.a.owner, link.b.owner), link
        if not world.opener:                       # the courtyard's worlds have no opener
            continue
        drawn = opener(world.opener, design.ORANGE, 3, 140, LOCALE["openers"].get(world.opener) or {})
        for link in getattr(drawn, "links", []):
            yield (name, "opener", link.kind, link.a.owner, link.b.owner), link


LINKS = list(_links())


@pytest.mark.parametrize("where,link", LINKS, ids=lambda v: str(v)[:80])
def test_every_line_in_a_world_bends_smoothly_and_goes_in_straight(where, link):
    if link.kind == "beam":
        return
    sharpest, tightest = turns(link.points)
    assert sharpest <= STEP_MAX, (where, sharpest)
    least = link.width * (0.55 if link.kind == "paper" else 3)   # a paper ribbon never folds over its own inner edge
    assert tightest >= least - 1e-6, (where, tightest, link.width)
    for end, inward in ((link.a, link.points), (link.b, link.points[::-1])):
        reach = fitting_length(link.kind, link.width)
        near = [p for p in inward[1:] if math.hypot(p[0] - end.x, p[1] - end.y) <= reach]
        for x, y in near:                                       # the stretch into its fitting runs along the port
            d = math.hypot(x - end.x, y - end.y)
            assert ((x - end.x) * end.dx + (y - end.y) * end.dy) / d >= 0.999, (where, end.owner)


def test_the_worlds_do_draw_lines():
    assert any(link.kind == "cable" for _, link in LINKS) and any(link.kind == "tube" for _, link in LINKS)


def test_a_corner_too_slight_to_bend_runs_straight_through():
    """A corner of a few hundred-thousandths of a radian is a straight run, not a division by zero."""
    line = eased_points([(0, 0), (100, 0), (200, 0.002)])
    assert line[0] == (0, 0) and line[-1] == (200, 0.002) and len(line) == 3

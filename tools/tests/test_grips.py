"""The grip system: hands that close round what they hold, and arms that join the body at its sides."""
import math

import pytest

from bookkit.art import characters, handheld, rig
from bookkit.art.characters import UnknownCharacter
from bookkit.art.footers import Strip, look_for

HOLDERS = [name for name, mod in characters.MODULES.items() if hasattr(mod, "hands")]
PROPS = [handheld.stopwatch, handheld.pencil, handheld.card, handheld.sheet, handheld.book, handheld.clipboard,
         handheld.caliper, handheld.magnifier, handheld.notebook]


def test_every_character_but_the_sparrow_can_hold_things():
    assert set(HOLDERS) == {"professor", "cat", "caterpillar", "agent"}


@pytest.mark.parametrize("name", HOLDERS)
def test_every_pose_holds_a_thing_in_either_hand(name):
    for pose in characters.MODULES[name].POSES:
        for side in ("left", "right"):
            svg = characters.draw(name, pose, hold={side: handheld.stopwatch}).render()
            assert svg.count("<g transform=") > 0


@pytest.mark.parametrize("name", HOLDERS)
def test_the_grip_is_inside_the_fist(name):
    mod = characters.MODULES[name]
    for pose in mod.POSES:
        for side, frame in mod.hands(pose).items():
            (gx, gy), (px, py) = frame.grip, frame.point(10, 0)       # the palm's middle
            assert math.dist((gx, gy), (px, py)) < 4 * frame.scale, (pose, side)


@pytest.mark.parametrize("make", PROPS)
def test_props_draw_round_their_grip(make):
    svg = make(0, 0, 1)
    assert svg.startswith('<g transform="translate(0,0) scale(1)">')


def test_hands_are_a_left_and_a_right():
    """Two hanging hands turn their thumbs towards the body, so one of them is mirrored."""
    for name in HOLDERS:
        frames = characters.MODULES[name].hands("stand")
        assert frames["left"].mirror != frames["right"].mirror, name


def test_mirrored_frame_points():
    frame = rig.HandFrame(10, 20, 90, 2, mirror=True)
    x, y = frame.point(1, 1)
    assert (round(x, 6), round(y, 6)) == (12, 22)


def test_holding_in_a_third_hand_is_an_error():
    with pytest.raises(UnknownCharacter):
        characters.draw("cat", "present", hold={"middle": handheld.card})


def test_the_sparrow_has_no_hands():
    with pytest.raises(UnknownCharacter):
        characters.draw("sparrow", "stand", hold={"right": handheld.card})


def test_a_strip_puts_a_thing_into_a_standing_hand():
    s = Strip(160, 1, None, look_for(0))
    box = s.cast("cat", 0.4, "present")
    before = len(s.items)
    s.hold(box, handheld.stopwatch)
    s.hold(box, handheld.card, side="left")
    assert len(s.items) == before                       # drawn again in its place, not twice
    assert s.drawn[id(box)][1]["options"]["hold"].keys() == {"right", "left"}
    x, y, angle = s.grip(box)
    assert box.left < x < box.right + 60 and box.top < y < box.bottom
    flipped = s.cast("agent", 0.8, "present", flip=True)
    fx, _, fangle = s.grip(flipped)
    assert fx < (flipped.left + flipped.right) / 2      # the near hand reaches left when the actor faces left
    assert -90 < angle < 0 and 180 < fangle < 270


def test_the_cat_takes_off_his_watch_only_for_a_stopwatch():
    """Two watches side by side read as a mistake: the paw cradling a stopwatch goes bare, any other keeps it."""
    def watches(**hold):
        return characters.draw("cat", "present", hold=hold or None).render().count('r="5.6"')
    assert watches() == 1
    assert watches(right=handheld.card) == 1
    assert watches(left=handheld.stopwatch) == 1
    assert watches(right=handheld.stopwatch) == 0

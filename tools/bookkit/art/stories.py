"""The stories told by the chapter openers, one function each, registered in `OPENERS` by the name a chapter
gives as `scene:` in its front matter.

Each story builds on a `Stage` (see `openers.py`): page units 840 x 1188, the title held at the top left, the
chapter tag at the bottom left, the professor's bubble where `Stage.speaker` puts it. Every object is placed by
hand with its box, so the composition can be checked: nothing overlaps unless it belongs together.
"""
from __future__ import annotations

import math
import random

from .. import design as P
from ..design import darken, lighten, mix
from . import handheld, props, sets, things
from .ink import INK, Canvas, ellipse_d, n, rounded_rect_d
from .openers import strip_boxes

W, H = 840, 1188


# ============================================================================ chapter 1: the newcomer's morning
def morning(s, accent: str) -> object:
    """The newcomer who comes in for the first time every morning.

    Nine o'clock: the cuckoo is out, the calendar shows day one again and yesterday's pages lie on the floor.
    The printer runs out a pull request so long it crosses the room, flagged all over with comments; the
    caterpillar sits at its end counting them, the cat with a giant pencil adds the next one, and the
    whiteboard keeps the tally. At the shelf of modules the agent has pulled out the dustiest old one to copy -
    the shiny new binders are on the top shelf, out of its sight - while the sparrow on the monitor has no idea.
    """
    wall_color = mix(lighten(accent, 0.62), P.PAPER, 0.2)
    horizon = 860
    sets.wall(s.back, wall_color, 0, horizon, W, seed=1)
    sets.floor(s.back, horizon, H, W, vanish=(470, 420))
    s.back.add(sets.rug_round(440, 1070, 230, 58, P.TEAL))
    # The morning sun falls through the window onto the floor.
    s.back.add(f'<path d="M462,556 L678,556 L600,1130 L190,1100 Z" fill="{P.SUN}" opacity=".16"/>')
    s.back.add(sets.motes(462, 556, 678, 556, 600, 1130, 190, 1100, 46, seed=2))

    # --- the wall, left to right: calendar, whiteboard with sticky notes, window; the clock in the corner
    s.put(10, sets.tear_calendar(112, 262, 0.84, "1", s.word("month"), s.word("again")), (58, 262, 166, 406),
          "calendar")
    s.put(10, sets.whiteboard(318, 266, 206, 134, s.word("review"), 20), (215, 266, 421, 408), "whiteboard")
    s.put(11, sets.sticky(392, 296, P.PINK_PALE, 8), (376, 280, 408, 312), "whiteboard")
    s.put(11, sets.sticky(396, 340, P.YELLOW_PALE, -6), (380, 324, 412, 356), "whiteboard")
    s.put(10, sets.window_morning(570, 300, 150, 230), (459, 278, 681, 556), "window")
    s.put(10, sets.cuckoo_clock(770, 40, 1.05), (722, 14, 818, 236), "clock")

    # --- the shelf of modules at the right wall: shiny binders on top, dusty boxes below
    s.put(20, sets.legacy_shelf(762, horizon + 6, 0.98, seed=3, gap=1), (688, 466, 836, horizon + 6), "shelf",
          backdrop=True)

    # --- the desk under the window: the old computer and the printer at the back of its top, the keyboard in
    # front, air between them; the sparrow on the monitor
    k = 1.4
    desk_floor = 930
    top = desk_floor - 71 * k                     # the top's front edge
    back = top - 20 * k * 0.7                     # where things stand, towards the back of the top
    ck = 1.2                                      # the computer a little smaller than the desk's scale: room round it
    s.put(30, props.desk(552, desk_floor, k, width=180, depth=20), (426, top - 20 * k, 678, desk_floor), "desk",
          group="desk", backdrop=True)
    s.put(31, props.computer(608, back, ck, lines=3, keyboard=False) + props.keyboard(604, top - 3, ck),
          (548, back - 95 * ck, 668, top + 4), "desk")
    s.put(31, sets.doodle_at("printer", 478, back + 2, 76), (440, back - 74, 516, back + 2), "desk")
    s.actor("sparrow", 608, back - 95 * ck + 2, "shrug", "worry", tall=230, group="desk", depth=32)

    # --- the pull request: fan-fold paper from the printer over the desk's edge and across the floor
    path = [(478, back - 18), (468, top + 30), (456, top + 80), (440, desk_floor + 8), (396, 976), (362, 1030),
            (362, 1084), (390, 1126), (430, 1154), (466, 1172)]
    flags = [(i / 34, (P.RED, P.YELLOW, P.RED, P.BLUE)[i % 4]) for i in range(2, 33)]
    s.put(40, sets.fanfold(path, 60, flags, seed=4), [b for b in strip_boxes(path, 56)], "ribbon", group="desk")
    s.actor("caterpillar", 430, 1140, "write", "worry", tall=300, group="desk")

    # --- the cast
    prof = s.actor("professor", 150, 1092, "explain", "talk", tall=380)
    s.speaker(prof, width=92, left=8)
    s.actor("cat", 600, 1172, "point", "talk", flip=True, tall=340, group="cat")
    s.actor("agent", 762, 1012, "read", "smile", tall=330, group="agent", held="old")

    # --- under the desk a box of old floppies
    s.put(880, sets.box_of_floppies(604, 904, 1.0), (560, 842, 648, 904), "desk")

    # --- small things on the floor
    s.put(1000, sets.loose_page(300, 1030, 0.9, "1", -14), (276, 1006, 324, 1054), "page")
    s.put(1180, sets.yarn(300, 1172, 15, P.BLUE, "M-10,-4 q-20,8 -40,0"), (250, 1140, 316, 1176), "yarn")
    s.put(1150, sets.printout_stack(782, 1160, 1.0, 4, seed=7), (730, 1050, 834, 1160), "stack")
    for x, y in ((268, 960), (300, 1090)):
        s.put(y, sets.paper_ball(x, y - 8, 1.1), (x - 12, y - 20, x + 12, y), f"ball{x}")
    return s.render()


# ============================================================================ chapter 2: the fair
def fair(s, accent: str) -> object:
    """Choosing a tool at the fair.

    Two stalls: the models' stall sells brains in jars, big and small, with price tags,
    and the harnesses' stall hangs out harnesses, tool belts and rucksacks - where the agent tries on braces and a
    tool belt.
    In front, the models have been compared and stand on a winners' podium (a snail has taken third place);
    the cat studies them. The sparrow shoots past on a skateboard - small and fast; the caterpillar wheels home a
    graphics card in a barrow, not at all sure about it. Hot-air balloons drift over the fair.
    """
    horizon = 660
    sets.sky(s.back, lighten(accent, 0.5), lighten(accent, 0.84), horizon, W)
    s.back.add(props.cloud(560, 330, 1.0))
    s.back.add(props.cloud(150, 600, 0.7))
    for x, y, k in ((470, 380, 1.0), (500, 360, 0.8), (640, 300, 0.9)):
        s.back.add(props.bird(x, y, k))
    sets.hills(s.back, horizon, W, (P.HILL_FAR, P.HILL_NEAR), seed=2)
    sets.meadow(s.back, horizon, H, W, seed=3)
    sets.path_band(s.back, [(372, horizon - 4), (384, 760), (372, 860), (340, 960), (306, 1070), (290, H + 10)],
                   [18, 50, 80, 110, 140, 170], seed=4)
    sets.grass_tufts(s.back, (0, horizon + 20, W, H), 160, seed=9)
    s.put(5, sets.hot_air_balloon(765, 262, 0.85), (705, 73, 825, 274), "balloon")
    s.put(4, sets.hot_air_balloon(590, 400, 0.38, (P.BLUE, P.WHITE)), (563, 320, 617, 406), "balloon2")
    s.put(40, sets.high_striker(426, 856, 330, 0.62),
          [(404, 506, 448, 856), (448, 794, 480, 856)], "striker")

    # --- the stalls
    base = 770
    s.put(50, sets.stall(557, base, 190, 290, P.RED, s.word("models")), (452, 438, 652, base), "stallA", backdrop=True)
    top = base - sets.STALL_COUNTER - 10
    for x, k, price in ((492, 1.0, "$$"), (548, 1.35, "$$$"), (603, 0.8, "$")):
        s.put(51, sets.brain_jar(x, top, k, price), (x - 28 * k, top - 62 * k, x + 58 * k, top), "stallA")
    s.put(50, sets.stall(752, base, 160, 290, P.GREEN, s.word("harnesses")), (660, 438, 840, base), "stallB",
          backdrop=True)
    hang = base - 290 + 66
    s.put(51, sets.harness(700, hang, 0.62), (680, hang, 720, hang + 80), "stallB")
    s.put(51, sets.toolbelt(752, hang + 4, 0.8), (722, hang - 10, 782, hang + 50), "stallB")
    s.put(51, sets.backpack(800, hang, 0.8), (778, hang, 822, hang + 62), "stallB")
    s.put(51, sets.hard_hat(712, top, 0.9), (690, top - 24, 734, top), "stallB")
    s.put(51, sets.hard_hat(790, top, 0.8, P.ORANGE), (770, top - 22, 810, top), "stallB")


    # --- the cast
    prof = s.actor("professor", 150, 960, "explain", "talk", tall=380)
    s.put(1080, sets.picnic(130, 1080, 1.0), (30, 1010, 236, 1088), "picnic")
    s.speaker(prof, width=92, left=8)
    s.actor("agent", 760, 920, "present", "smile", tall=300, flip=True, group="agent", wear="harness")
    s.actor("cat", 712, 1180, "think", "smile", flip=True, tall=330)
    s.actor("caterpillar", 309, 982, "walk", "worry", tall=270, flip=True, group="barrow")
    s.put(983, sets.wheelbarrow(456, 984, 1.0), (330, 914, 470, 984), "barrow")
    s.put(984, sets.gpu_box(398, 922, 0.8, "GPU"), (354, 870, 442, 922), "barrow")
    s.put(985, props.mark(309, 790, "?", 1.2), (287, 768, 331, 812), "barrow")

    # --- the podium and the skateboarder
    pk = 1.15
    s.put(1150, sets.podium(510, 1160, pk), (406, 1070, 614, 1160), "podium")
    s.put(1151, sets.brain_jar(510, 1160 - 78 * pk, 1.0), (482, 1160 - 78 * pk - 62, 538, 1160 - 78 * pk), "podium")
    s.put(1151, sets.brain_jar(441, 1160 - 54 * pk, 0.85), (417, 1160 - 54 * pk - 54, 465, 1160 - 54 * pk),
          "podium")
    s.put(1151, sets.snail(580, 1160 - 40 * pk, 0.8), (552, 1160 - 40 * pk - 30, 606, 1160 - 40 * pk), "podium")
    s.actor("sparrow", 346, 1144, "cheer", "smile", tall=230, group="sparrow")
    s.put(1160, sets.skateboard(348, 1150, 0.9), (254, 1120, 390, 1162), "sparrow")

    # --- flowers in the grass where nothing stands
    s.scatter(lambda x, y: props.daisy(x, y, 1.2, P.WHITE), 6, (0, horizon + 40, W, H), (26, 34))
    s.scatter(lambda x, y: props.tulip(x, y, 1.1, P.RED), 3, (0, horizon + 60, W, H), (24, 46))
    s.scatter(lambda x, y: props.mushroom(x, y, 0.9), 2, (0, horizon + 80, W, H), (34, 36))
    return s.render()


# ============================================================================ chapter 3: the valley of services
def valley(s, accent: str) -> object:
    """The agent plugs into the services.

    Sunset over a valley: the services live in their own houses, each with its sign - the logs in a log cabin piled
    with paper rolls, the metrics on a weather mast with a chart, the data in a barn of barrels, the tickets in a little
    post office with tickets pouring out of its window. A cable runs from every house down to the box marked MCP,
    where the agent is plugging in the last one, the sparrow perched on top. At the post office a strange letter
    sticks out of the box, and the caterpillar points at it in alarm; the cat watches over the
    whole thing. A boat rests on the river with its rod out, a frog sits on a lily pad.
    """
    horizon = 470
    sets.sky(s.back, lighten(accent, 0.5), lighten(accent, 0.84), horizon, W)
    sets.sun_low(s.back, 160, horizon - 70, 54)
    s.back.add(props.cloud(730, 300, 0.8))
    s.back.add(props.cloud(470, 330, 0.6))
    for x, y, k in ((560, 280, 0.9), (590, 262, 0.7), (620, 290, 0.6), (300, 300, 0.8)):
        s.back.add(props.bird(x, y, k))
    sets.mountains(s.back, horizon - 30, W, lighten(P.VIOLET, 0.5), seed=4)
    sets.hills(s.back, horizon, W, (lighten(P.VIOLET, 0.65), P.HILL_FAR), seed=5)
    sets.meadow(s.back, horizon, H, W, seed=6, color=P.GRASS)
    sets.grass_tufts(s.back, (0, horizon + 30, W, H), 170, seed=7)
    river = [(612, horizon - 6), (560, 540), (470, 610), (380, 690), (280, 760), (150, 820), (20, 860), (-40, 880)]
    sets.river(s.back, river, [10, 26, 44, 62, 80, 96, 112, 120], seed=8)

    # --- the services, far to near; each claims its own ground
    s.put(500, sets.barn(470, 512, 0.5, s.word("base")), (422, 422, 518, 512), "barn", backdrop=True)
    s.put(490, sets.windmill(590, 492, 0.55, 20), (556, 400, 624, 492), "mill", backdrop=True)
    s.put(520, sets.weather_station(720, 540, 0.62, s.word("metrics")), (686, 379, 790, 540), "metrics", backdrop=True)
    s.put(700, sets.log_cabin(590, 696, 0.82, s.word("logs")), (508, 556, 672, 696), "logs", backdrop=True)
    s.put(900, sets.ticket_booth(748, 910, 0.92, s.word("tickets")), (656, 704, 840, 910), "tickets", backdrop=True)

    # --- the cables, from the houses down to the box; drawn on the ground, under everything standing
    hub_x, hub_y = 450, 1050
    cables = (
        ([(470, 514), (468, 560), (462, 624), (440, 700), (410, 830), (412, 930), (426, 1006)], P.BLUE),
        ([(700, 542), (650, 580), (520, 740), (470, 880), (442, 1006)], P.YELLOW),
        ([(560, 700), (520, 820), (480, 930), (458, 1006)], P.GREEN),
        ([(690, 912), (600, 960), (520, 990), (474, 1006)], P.PINK),
    )
    for points, color in cables:
        s.back.add(sets.cable(points, color, 4.6))
    s.put(700, sets.footbridge(462, 628, 64, 1.0), (428, 580, 496, 636), "bridge")
    s.put(hub_y, sets.hub(hub_x, hub_y, 1.0, "MCP", (P.BLUE, P.YELLOW, P.GREEN)), (384, 948, 516, hub_y), "hub")
    s.actor("sparrow", hub_x + 30, hub_y - 102, "wave", "smile", tall=200, group="hub", depth=hub_y + 1)

    # --- the cast
    prof = s.actor("professor", 150, 1100, "explain", "talk", tall=380)
    s.speaker(prof, width=92, left=8)
    s.actor("agent", 334, 1120, "point", "smile", tall=320, group="hub")
    s.put(1121, sets.cable([(372, 1046), (396, 1020), (482, 1012)], P.PINK, 4.6), None)
    s.actor("caterpillar", 590, 968, "point", "surprise", tall=270, group="post")
    s.put(970, props.mark(590, 788, "!", 1.2), (568, 766, 612, 810), "post")
    s.put(910, sets.mailbox(692, 918, 1.0), (670, 812, 722, 918), "tickets")
    s.put(911, things.envelope(692, 832, 1.0, -8), (678, 814, 706, 834), "tickets")   # the planted letter
    s.actor("cat", 744, 1182, "point", "talk", flip=True, tall=330, group="cat")

    # --- the river: a boat with its rod out, a frog on a lily pad, reeds; a dragonfly over the water
    s.put(780, sets.boat(312, 790, 0.8), (260, 736, 392, 796), "boat")
    s.put(840, props.reeds(436, 800, 1.2), (420, 736, 452, 800), "reeds")
    s.put(9, sets.dragonfly(380, 866, 1.0), (364, 852, 396, 892), "dragonfly")
    # Flowers and stones only on dry land: below the river on the left, beside it on the right.
    for region in ((0, 940, W, H), (480, 720, W, H)):
        s.scatter(lambda x, y: props.daisy(x, y, 1.1, P.WHITE), 4, region, (26, 34))
        s.scatter(lambda x, y: props.mushroom(x, y, 0.9), 2, region, (34, 36))
        s.scatter(lambda x, y: props.stone(x, y, 1.1), 1, region, (40, 22))
    s.scatter(lambda x, y: props.tree(x, y, 0.42, "fir"), 3, (0, horizon + 10, W, horizon + 120), (40, 66))
    return s.render()


# ============================================================================ chapter 4: the house of the repository
def house(s, accent: str) -> object:
    """The repository as a house with its front taken off: every room is a folder.

    The professor has just handed the newcomer its envelope, and the agent reads the one page from it on the
    doorstep, the way a newcomer gets a welcome letter on the first day. Inside, every room has its own sheet
    pinned by the door: the hall (the root, with the commands sheet nearest the door), "src/" with a machine of
    gears and sticky notes on it and a green light for its tests, "tests/" where the caterpillar checks the flasks,
    "docs/" where the cat reads, and up the ladder in the attic the chest of decisions, "adr/", which the sparrow
    has just opened. A red thread runs from the agent's page to the sheet in the hall, on up to the docs and the
    chest: one note pointing to the next.
    """
    ground = 1040
    sets.sky(s.back, lighten(accent, 0.5), lighten(accent, 0.84), ground, W)
    s.back.add(props.sun(780, 90, 1.1))
    s.back.add(props.cloud(300, 300, 0.7))
    for x, y, k in ((240, 270, 0.9), (270, 254, 0.7), (720, 230, 0.8)):
        s.back.add(props.bird(x, y, k))
    sets.hills(s.back, 760, W, (P.HILL_FAR, P.HILL_NEAR), seed=11)
    sets.meadow(s.back, 740, H, W, seed=12)
    sets.grass_tufts(s.back, (0, 760, 420, H), 60, seed=13)
    sets.grass_tufts(s.back, (420, 1060, W, H), 40, seed=14)
    sets.path_band(s.back, [(400, 1046), (360, 1090), (330, 1140), (320, H + 10)], [60, 80, 100, 120], seed=15)

    # --- the house
    left, right, f1, attic = 420, 830, 752, 482
    papers = (lighten(accent, 0.6), P.YELLOW_PALE, P.PINK_PALE, lighten(P.BLUE, 0.62))
    sets.house_shell(s.back, left, right, ground, [f1, attic], 268,
                     [(625, f1 + 12, ground, 150), (625, attic + 12, f1, 140)], list(papers))
    # The walls and slabs are boxes of their own: nothing in a room may reach through them.
    walls = [(left, attic + 8, left + 12, ground - 150), (right - 12, attic + 8, right, ground),
             (left, attic + 8, right, attic + 12), (left, f1 + 8, right, f1 + 12),
             (619, f1 + 16, 631, ground - 150), (619, attic + 16, 631, f1 - 140)]
    s.put(1, "", walls, "house")
    s.put(ground, sets.front_door(426, ground, 150), (360, 894, 432, ground + 16), "agent")

    # The hall: the sheet everyone sees first, a lamp, a coat stand, the ladder up through the hatch.
    s.put(800, sets.pinned_sheet(496, 790, "AGENTS.md", 1.0), (470, 786, 522, 852), "hall")
    s.put(800, sets.pinned_sheet(552, 800, s.word("commands"), 0.8, 4), (530, 796, 574, 852), "hall")
    s.put(ground - 1, sets.coat_rack(462, ground, 0.55), (446, 870, 478, ground), "hall")
    s.put(ground - 2, sets.ladder(596, f1, ground, 30), (579, f1 + 16, 613, ground), "hall")
    s.put(ground, sets.umbrella_closed(530, ground, 0.8, P.RED), (518, 934, 542, ground + 8), "hall")

    # src/: the machine with its comments and its green light.
    s.put(f1 + 20, sets.room_sign(722, f1 + 36, "src/"), (690, f1 + 22, 754, f1 + 48), "src")
    s.put(f1 + 20, sets.pinned_sheet(792, f1 + 30, "AGENTS.md", 0.8, 3), (770, f1 + 26, 814, f1 + 82), "src")
    s.put(ground - 1, sets.workbench(712, ground, 0.92), (636, ground - 142, 788, ground), "src")
    s.put(f1 + 12, sets.wall_lamp(656, f1 + 12, 0.9), (640, f1 + 18, 672, f1 + 46), "src")

    # tests/: the caterpillar checks the flasks.
    s.put(attic + 20, sets.room_sign(486, attic + 36, "tests/"), (446, attic + 22, 526, attic + 48), "tests")
    s.put(attic + 20, sets.pinned_sheet(590, attic + 34, "AGENTS.md", 0.8, -4), (568, attic + 30, 612, attic + 86),
          "tests")
    s.put(f1 - 1, sets.flask_rack(560, f1, 0.62), (512, f1 - 80, 608, f1), "tests")
    s.actor("caterpillar", 492, f1, "write", "worry", tall=250, group="tests")

    # docs/: the shelf of documents, the cat reading, the ladder to the attic.
    s.put(attic + 20, sets.room_sign(760, attic + 36, "docs/"), (726, attic + 22, 794, attic + 48), "docs")
    s.put(f1 - 2, props.bookshelf(712, f1, 0.7, seed=4, shelves=3), (672, f1 - 112, 752, f1), "docs")
    s.actor("cat", 752, f1, "read", "smile", flip=True, tall=220, group="docs")
    s.put(f1 - 3, sets.ladder(650, attic, f1, 28), (636, attic + 16, 664, f1), "ladder")

    # The attic: the chest of decisions, opened by the sparrow; a round window.
    s.put(attic, sets.chest(590, attic, 0.9, "adr/"), (542, attic - 84, 638, attic), "attic")
    s.actor("sparrow", 690, attic, "cheer", "surprise", tall=190, flip=True, group="attic")
    s.put(attic, sets.round_window(625, 356, 16), (603, 334, 647, 378), "window")

    # The red thread: from the page in the agent's hands to the hall's sheet, up to the docs and the chest.
    s.put(1500, sets.red_thread([(368, 968), (496, 792), (596, 700), (650, 560), (590, 424)]), None)

    # --- outside: the professor, the agent on the doorstep with its page
    prof = s.actor("professor", 150, 1096, "explain", "talk", tall=380)
    s.speaker(prof, width=92, left=8)
    s.actor("agent", 340, 1066, "read", "smile", tall=300, group="agent")
    s.put(880, sets.apple_tree(332, 882, 0.86, seed=2), (260, 728, 404, 882), "tree")
    s.put(1100, sets.envelope_open(292, 1132, 1.0), (268, 1088, 316, 1132), "envelope")
    s.put(1150, sets.fence_row(452, 840, 1160), (452, 1113, 840, 1160), "fence")
    s.put(1170, sets.snail(400, 1170, 0.9), (372, 1140, 430, 1170), "snail")
    s.scatter(lambda x, y: props.daisy(x, y, 1.1, P.WHITE), 4, (0, 1110, 450, H), (26, 34))
    s.scatter(lambda x, y: props.tulip(x, y, 1.1, P.RED), 4, (440, 1060, W, 1110), (24, 46))
    return s.render()


# ============================================================================ chapter 5: the library of playbooks
def _card_catalog(x: float, y: float, scale: float, label: str) -> str:
    """A library card catalog on legs: three rows of drawers, one pulled out with its cards; origin at its foot."""
    c = Canvas()
    c.line("M-62,0 V-26 M62,0 V-26", 5, P.WOOD_DARK)
    c.shape("M-70,-26 V-176 H70 V-26 Z", P.WOOD, sw=2.5, light=(-3, -3))
    c.shape(rounded_rect_d(-76, -186, 152, 12, 3), P.WOOD_DARK, sw=2.2, light=None)
    for row in range(3):
        for col in range(3):
            if (row, col) == (1, 2):
                continue
            dx, dy = -62 + col * 42, -140 + row * 36
            c.path(rounded_rect_d(dx, dy, 38, 30, 3), P.WOOD_LIGHT, 1.8)
            c.path(rounded_rect_d(dx + 10, dy + 6, 18, 8, 1.5), P.CREAM, 1.3)
            c.dot(dx + 19, dy + 21, 2.6)
    # The pulled-out drawer: it sticks out towards us, full of cards.
    c.shape("M22,-104 L66,-104 L80,-92 L80,-70 L36,-70 L22,-82 Z", P.WOOD_LIGHT, sw=2, light=None)
    for i in range(5):
        c.path(f"M{30 + i * 8},-104 l2,-16 h8 l-2,16 Z", P.CARD, 1.3)
    c.path(rounded_rect_d(-46, -170, 92, 24, 4), P.CREAM, 1.9)       # the plate on the front, under the top
    c.text(0, -153, label, min(14.0, 120 / max(len(label), 1)))
    return props._at(c, x, y, scale)


def _parcel(x: float, y: float, w: float, h: float, label: str, turn: float = 0) -> str:
    """A cardboard parcel with tape and a label; origin at the middle of its foot."""
    c = Canvas()
    c.shape(f"M{-w / 2},0 V{-h} H{w / 2} V0 Z", P.SAND, sw=2.2, light=(-3, -2))
    c.path(f"M-6,{-h} h12 V0 h-12 Z", lighten(P.WOOD_LIGHT, 0.2), 1.2)
    c.path(rounded_rect_d(-w / 2 + 8, -h + 10, min(56, w - 26), 15, 2), P.CARD, 1.4)
    c.text(-w / 2 + 8 + min(56, w - 26) / 2, -h + 21, label, min(10.0, 60 / max(len(label), 1)))
    return f'<g transform="rotate({turn} {x} {y})">{props._at(c, x, y)}</g>'


def library(s, accent: str) -> object:
    """The library of playbooks: every skill is a book on the shelf, and only its card is in the catalog.

    The agent stands at the card catalog - the descriptions - with one card in its hand, and the cat on top of
    the catalog has found the card it needs; the sparrow flies up to the shelves to fetch the book itself. At the
    door the caterpillar stares at a tower of parcels of other people's skills that keeps growing, a question over
    its head: where is all this to go?
    """
    horizon = 880
    wall_color = mix(lighten(accent, 0.64), P.PAPER, 0.25)
    sets.wall(s.back, wall_color, 0, horizon, W, seed=5)
    sets.floor(s.back, horizon, H, W, vanish=(520, 440))
    s.back.add(sets.rug_round(430, 1096, 230, 52, P.PINK))

    # --- the shelves of playbooks along the right wall, with their plate
    k = 1.45
    for x, seed in ((590, 21), (752, 22)):
        s.put(20, props.bookshelf(x, horizon, k, seed=seed, shelves=4),
              (x - 54 * k, horizon - 208 * k, x + 54 * k, horizon), f"shelf{x}", group="shelves", backdrop=True)
    s.put(19, sets.room_sign(672, horizon - 208 * k - 30, s.word("playbooks")),
          (600, horizon - 208 * k - 46, 744, horizon - 208 * k - 18), "sign", group="shelves")
    s.put(18, sets.wall_lamp(450, 560, 1.0), (432, 566, 468, 596), "lamp")
    s.put(10, props.window(766, 262, 0.85), (713, 208, 819, 312), "window")
    s.put(10, props.picture(520, 372, 1.1, variant=1), (484, 332, 556, 400), "picture")

    # --- the sparrow flies up to the top shelf for the book
    s.actor("sparrow", 690, 520, "fly", "smile", tall=190, group="sparrow", depth=30)
    s.put(31, props.mark(722, 380, "!", 1.0), (702, 360, 742, 400), "sparrow")

    # --- the card catalog with the cat on top, and the agent reading a card beside it
    cx, cfoot = 360, 1064
    s.put(cfoot, _card_catalog(cx, cfoot, 1.0, s.word("catalog")), (cx - 80, cfoot - 186, cx + 80, cfoot), "catalog",
          group="catalog")
    s.actor("cat", cx - 30, cfoot - 186, "read", "smile", tall=200, group="catalog", depth=cfoot + 1)
    s.actor("agent", 506, 1090, "read", "smile", tall=300, group="agent")

    # --- the caterpillar and the tower of other people's skills
    parcels = ((762, 1176, 120, 64, 0), (754, 1112, 104, 56, -3), (766, 1056, 92, 50, 4),
               (754, 1006, 78, 44, -5))
    for x, y, w, h, turn in parcels:
        s.put(1176 - (1176 - y) * 0.01, _parcel(x, y, w, h, s.word("parcel"), turn), (x - w / 2 - 4, y - h - 4,
              x + w / 2 + 4, y), "parcels", group="parcels")
    s.actor("caterpillar", 640, 1164, "think", "worry", tall=260, group="parcels")
    s.put(1161, props.mark(640, 968, "?", 1.1), (618, 946, 662, 990), "parcels")

    # --- the professor under his bubble
    prof = s.actor("professor", 150, 1096, "explain", "talk", tall=380)
    s.speaker(prof, width=92, left=8)

    return s.render()


# ============================================================================ chapter 6: the preview stand
def _monorepo_cabinet(x: float, y: float, scale: float, title: str, labels: tuple[str, ...]) -> str:
    """A tall cabinet of drawers, one per folder of the monorepo, with the cabinet's name on a plate on top; the
    middle drawer is pulled out, its folders taken. The origin is the middle of its foot; 150 wide, 236 tall."""
    c = Canvas()
    c.line("M-66,0 V-14 M66,0 V-14", 5, P.WOOD_DARK)
    c.shape("M-75,-14 V-214 H75 V-14 Z", P.WOOD, sw=2.6, light=(-3, -3), stipple=(40, -210, 30, 190, 22, "right"))
    c.shape(rounded_rect_d(-80, -224, 160, 12, 3), P.WOOD_DARK, sw=2.2, light=None)
    for i, label in enumerate(labels):
        top = -200 + i * 62
        if i == 1:      # pulled out towards us, empty: the agent has the folders
            c.shape(f"M-60,{top} H60 L70,{top + 10} V{top + 54} H-50 L-60,{top + 44} Z", P.WOOD_LIGHT, sw=2,
                    light=None)
            c.path(rounded_rect_d(-34, top + 22, 74, 20, 3), P.CREAM, 1.6)
            c.text(3, top + 37, label, min(13.0, 110 / max(len(label), 1)))
        else:
            c.path(rounded_rect_d(-62, top, 124, 50, 4), P.WOOD_LIGHT, 2)
            c.path(rounded_rect_d(-40, top + 10, 80, 20, 3), P.CREAM, 1.6)
            c.text(0, top + 25, label, min(13.0, 110 / max(len(label), 1)))
            c.dot(0, top + 40, 3)
    c.path(rounded_rect_d(-58, -258, 116, 30, 5), P.CREAM, 2)
    c.text(0, -237, title, min(16.0, 150 / max(len(title), 1)))
    return props._at(c, x, y, scale)


def _preview_screen(x: float, y: float, scale: float, label: str) -> str:
    """A big screen on legs showing the app in a browser window: the address bar says what it is, a green tick
    says the check passed, a red light says it is being recorded. The origin is the middle of its foot; 200 wide,
    190 tall."""
    c = Canvas()
    c.line("M-60,0 L-44,-46 M60,0 L44,-46 M0,0 V-46", 5, P.METAL_DARK)
    c.shape(rounded_rect_d(-100, -190, 200, 146, 8), P.CHARCOAL, sw=2.6, light=(-3, -3))
    c.path(rounded_rect_d(-90, -180, 180, 126, 4), P.CARD, 2)
    c.path("M-90,-162 H90", "none", 1.6)
    for i, color in enumerate((P.RED, P.YELLOW, P.GREEN)):
        c.add(f'<circle cx="{-80 + i * 10}" cy="-171" r="3" fill="{color}" stroke="{P.INK}" stroke-width="1"/>')
    c.path(rounded_rect_d(-42, -177, 112, 12, 3), P.WHITE, 1.3)
    c.text(14, -167.5, label, 9.5)
    c.path(rounded_rect_d(-80, -152, 160, 16, 2), lighten(P.VIOLET, 0.55), 1.4)
    for i in range(3):
        c.path(rounded_rect_d(-80 + i * 56, -128, 48, 34, 3), (P.PINK_PALE, P.YELLOW_PALE, lighten(P.TEAL, 0.6))[i],
               1.4)
    c.path(rounded_rect_d(-30, -86, 60, 16, 6), P.GREEN, 1.6)
    c.add(f'<circle cx="84" cy="-198" r="7" fill="{P.RED}" stroke="{P.INK}" stroke-width="1.8"/>')
    c.add(props.mark(70, -80, "ok", 0.55))
    return props._at(c, x, y, scale)


def _camera(x: float, y: float, scale: float) -> str:
    """A film camera on a tripod, its red light on: it is recording. The origin is the middle of the tripod's
    foot; 90 wide, 150 tall; the lens looks left."""
    c = Canvas()
    c.line("M-30,0 L0,-84 M30,0 L0,-84 M0,0 V-84", 3.4, P.WOOD_DARK)
    c.shape(rounded_rect_d(-24, -124, 58, 40, 6), P.CHARCOAL, sw=2.4, light=(-3, -2))
    c.shape("M-24,-114 L-44,-122 V-86 L-24,-94 Z", P.METAL_DARK, sw=2.2, light=None)
    c.add(f'<circle cx="-46" cy="-104" r="9" fill="{P.SCREEN_LIGHT}" stroke="{P.INK}" stroke-width="2"/>')
    for cx in (-8, 20):
        c.add(f'<circle cx="{cx}" cy="-138" r="14" fill="{P.METAL}" stroke="{P.INK}" stroke-width="2.2"/>'
              f'<circle cx="{cx}" cy="-138" r="4" fill="{P.METAL_DARK}" stroke="{P.INK}" stroke-width="1.2"/>')
    c.add(f'<circle cx="26" cy="-114" r="4" fill="{P.RED}" stroke="{P.INK}" stroke-width="1.2"/>')
    return props._at(c, x, y, scale)


def proving(s, accent: str) -> object:
    """The preview stand: the project is put together and tried out whole before anyone ships it.

    From the cabinet of the monorepo - one drawer per folder, the middle one pulled out and empty - the agent
    carries an armful of folders up to the stand, where the whole app already runs on a big screen with a green
    tick: the branch is deployed. The sparrow perches on the screen; the cat films it all on a camera with its red
    light on, the video that will go into the pull request; the caterpillar checks its list of test cases. The
    clock on the wall says the stand came up in minutes.
    """
    horizon = 870
    wall_color = mix(lighten(accent, 0.62), P.PAPER, 0.3)
    sets.wall(s.back, wall_color, 0, horizon, W, seed=6)
    sets.floor(s.back, horizon, H, W, vanish=(560, 460))

    s.put(10, things.wall_clock(770, 330, 1.2), (738, 298, 802, 362), "clock")
    s.put(10, props.window(560, 420, 0.85), (506, 366, 614, 474), "window")

    # --- the monorepo: a cabinet with a drawer per folder
    labels = (s.word("apps"), s.word("services"), s.word("infra"))
    s.put(20, _monorepo_cabinet(500, horizon, 1.0, s.word("repo"), labels), (420, horizon - 262, 580, horizon),
          "cabinet", backdrop=True)

    # --- the stand: a low stage, the screen with the running app, the sparrow on top
    stage = Canvas()
    stage.shape("M612,980 H840 V1010 H604 Z", P.WOOD_LIGHT, sw=2.4, light=(-3, -2))
    stage.line("M612,992 H840", 1.4, opacity=0.5)
    s.put(979, stage.render(), (604, 976, 840, 1010), "stage", group="stage")
    s.put(980, _preview_screen(730, 980, 1.0, s.word("preview")), (628, 782, 832, 980), "screen", group="stage")
    s.actor("sparrow", 690, 792, "cheer", "smile", tall=170, group="stage", depth=982)

    # --- the agent carries the folders to the stand
    s.actor("agent", 470, 1080, "carry", "smile", tall=300, group="agent")

    # --- the cat films; the caterpillar checks the cases
    s.put(1170, _camera(590, 1170, 1.0), (540, 1020, 640, 1172), "camera", group="filming")
    s.actor("cat", 700, 1180, "stand", "smile", tall=190, group="filming")
    s.actor("caterpillar", 312, 1176, "write", "worry", tall=220, group="caterpillar")

    # --- the professor under his bubble
    prof = s.actor("professor", 150, 1096, "explain", "talk", tall=380)
    s.speaker(prof, width=92, left=8)

    return s.render()


# ============================================================================ chapter 7: the test lab
def lab(s, accent: str) -> object:
    """The test lab: the agent learns about its own mistake in seconds, not from the customers.

    The agent works at the bench on a machine of gears; next to it stands a rack of test tubes, one of them red -
    a test has failed, and the cat points at it. On the wall hangs a whiteboard of tests, tallied by the hundred,
    with the sparrow perched on top. The caterpillar writes the next test on its list before the code exists.
    """
    horizon = 880
    wall_color = mix(lighten(accent, 0.64), P.PAPER, 0.28)
    sets.wall(s.back, wall_color, 0, horizon, W, seed=7)
    sets.floor(s.back, horizon, H, W, vanish=(520, 450))

    # --- the board of tests on the wall, the sparrow on its frame
    s.put(10, sets.whiteboard(640, 380, 300, 200, s.word("tests"), tallies=60), (490, 380, 790, 590), "board",
          group="board")
    s.actor("sparrow", 735, 384, "cheer", "smile", tall=150, group="board", depth=12)

    # --- the bench where the agent builds, the rack of tubes beside it, the cat pointing at the red one
    s.put(1010, sets.workbench(430, 1010, 1.25), (330, 820, 530, 1010), "bench", group="bench", backdrop=True)
    s.actor("agent", 470, 1130, "type", "smile", tall=290, group="bench")
    s.put(1000, sets.flask_rack(660, 1000, 1.3), (562, 840, 758, 1000), "rack", group="rack", backdrop=True)
    s.actor("cat", 590, 1176, "point", "smile", tall=200, group="cat")

    # --- the caterpillar writes the test before the code
    s.actor("caterpillar", 300, 1176, "write", "worry", tall=210, group="caterpillar")

    # --- the professor under his bubble
    prof = s.actor("professor", 140, 1096, "explain", "talk", tall=380)
    s.speaker(prof, width=92, left=8)

    return s.render()


# ============================================================================ chapter 8: the level crossing
def _rails(x0: float, x1: float, y: float) -> str:
    """A straight track from x0 to x1: sleepers under two rails, the near rail at y. 26 tall."""
    c = Canvas()
    for x in range(int(x0) + 8, int(x1) - 4, 26):
        c.shape(rounded_rect_d(x, y - 22, 14, 26, 2), P.WOOD_DARK, sw=1.6, light=None)
    for top in (y - 20, y - 4):
        c.shape(rounded_rect_d(x0, top, x1 - x0, 5, 2), P.METAL, sw=1.6, light=None)
    return c.render()


def _wagon(x: float, y: float, scale: float, label: str, color: str) -> str:
    """A goods wagon on two wheels with its label on the side: one pull request on its way to main. The origin is
    the middle under the wheels; 130 wide, 104 tall."""
    c = Canvas()
    c.shape(rounded_rect_d(-62, -88, 124, 64, 5), color, sw=2.6, light=(-3, -3))
    c.line("M-62,-76 H62", 1.6, opacity=0.5)
    c.shape(rounded_rect_d(-66, -98, 132, 12, 4), P.WOOD_DARK, sw=2.2, light=None)
    c.path(rounded_rect_d(-26, -68, 52, 26, 4), P.CREAM, 1.8)
    c.text(0, -49, label, 15)
    c.line("M-72,-30 H72", 3.2, P.METAL_DARK)                        # the couplers at both ends
    for wx in (-36, 36):
        c.add(f'<circle cx="{wx}" cy="-14" r="14" fill="{P.CHARCOAL}" stroke="{P.INK}" stroke-width="2.4"/>'
              f'<circle cx="{wx}" cy="-14" r="4" fill="{P.METAL}" stroke="{P.INK}" stroke-width="1.4"/>')
    return props._at(c, x, y, scale)


def _barrier(x: float, y: float, scale: float, arm: float) -> str:
    """A level-crossing barrier, closed: a post with a control box and a striped arm reaching left over the
    track. The origin is the foot of the post; the arm is `arm` long, the post 150 tall."""
    c = Canvas()
    c.shape(rounded_rect_d(-26, -10, 52, 10, 3), P.METAL_DARK, sw=2, light=None)
    c.shape(rounded_rect_d(-10, -150, 20, 140, 4), P.METAL, sw=2.4, light=(-2, -2))
    c.shape(rounded_rect_d(-22, -112, 44, 50, 5), P.YELLOW, sw=2.4, light=(-3, -2))  # the box that lifts it
    c.add(f'<circle cx="0" cy="-87" r="9" fill="{P.RED}" stroke="{P.INK}" stroke-width="2"/>')
    c.shape(rounded_rect_d(-arm, -142, arm + 16, 16, 7), P.WHITE, sw=2.4, light=None)
    for i in range(int(arm // 44)):
        left = -arm + 10 + i * 44
        c.shape(f"M{left},-142 h22 v16 h-22 Z", P.RED, sw=0, light=None)
    c.path(rounded_rect_d(-arm, -142, arm + 16, 16, 7), "none", 2.4)
    c.add(f'<circle cx="0" cy="-134" r="6" fill="{P.METAL_DARK}" stroke="{P.INK}" stroke-width="1.8"/>')
    return props._at(c, x, y, scale)


def crossing(s, accent: str) -> object:
    """The level crossing before main: nothing gets onto the line until it has passed.

    A train of pull requests waits at a closed barrier, its wagons coupled up as in a merge queue; beyond the
    barrier stands the station marked main. The cat at the barrier points at the wagons with its list, the sparrow
    sits on the striped arm right by the big red button, the caterpillar checks a wheel with its list in hand, and
    the agent brings up the last wagon.
    """
    horizon = 600
    sets.sky(s.back, lighten(accent, 0.5), lighten(accent, 0.84), horizon, W)
    s.back.add(props.sun(760, 120, 1.0))
    s.back.add(props.cloud(420, 330, 0.7))
    s.back.add(props.cloud(640, 260, 0.55))
    for x, y, k in ((300, 300, 0.8), (330, 284, 0.6)):
        s.back.add(props.bird(x, y, k))
    sets.hills(s.back, horizon, W, (P.HILL_FAR, P.HILL_NEAR), seed=21)
    sets.meadow(s.back, horizon, H, W, seed=22)
    sets.grass_tufts(s.back, (0, horizon + 20, W, H), 120, seed=23)

    # --- the track and the station of main beyond the barrier
    track = 900
    s.back.add(_rails(-10, W + 10, track))     # the track lies on the ground, under everything standing
    s.put(track - 40, sets.ticket_booth(764, track - 40, 0.62, s.word("main")), (706, track - 190, 822,
          track - 40), "station", backdrop=True)

    # --- the barrier, closed, the sparrow on its arm
    s.put(track + 70, _barrier(660, track + 70, 1.0, 130), (530, track - 80, 686, track + 70), "barrier",
          group="barrier")
    s.actor("sparrow", 600, track - 74, "cheer", "smile", tall=140, group="barrier", depth=track + 71)

    # --- the train of pull requests waiting at the barrier
    colors = (lighten(P.BLUE, 0.35), lighten(P.GREEN, 0.3), lighten(P.ORANGE, 0.3))
    for i, x in enumerate((446, 320)):
        s.put(track, _wagon(x, track, 0.85, s.word("pr"), colors[i]), (x - 62, track - 86, x + 62, track),
              f"wagon{i}", group="train")

    # --- the cast: the cat checks at the barrier, the caterpillar a wheel, the agent pushes the last wagon
    s.actor("cat", 700, 1176, "point", "talk", flip=True, tall=230, group="cat")
    s.actor("caterpillar", 470, 1176, "write", "worry", tall=220, group="caterpillar")
    s.actor("agent", 320, 1150, "carry", "smile", tall=280, group="agent")

    # --- the professor under his bubble
    prof = s.actor("professor", 140, 1096, "explain", "talk", tall=380)
    s.speaker(prof, width=92, left=8)

    s.scatter(lambda x, y: props.daisy(x, y, 1.0, P.WHITE), 4, (0, track + 20, W, H), (26, 34))
    return s.render()


# ============================================================================ chapter 9: the review base on the Moon
def _moon_crater(x: float, y: float, k: float = 1.0) -> str:
    """A shallow crater seen from the side, 88 wide: a dark bowl with a lit rim and a few stones on it."""
    c = Canvas()
    c.shape(ellipse_d(0, 0, 40, 9), darken(P.STONE, 0.8), sw=1.8, light=None)
    c.shape("M-44,0 Q-40,-8 -30,-6 L-34,2 Z M44,0 Q40,-8 30,-6 L34,2 Z", P.STONE, sw=1.4, light=None)
    for dx, dy, r in ((-30, -8, 3), (28, -10, 2.4), (36, -4, 2)):
        c.add(f'<circle cx="{dx}" cy="{dy}" r="{r}" fill="{P.STONE}" stroke="{P.INK}" stroke-width=".9"/>')
    return props._at(c, x, y, k)


def _earth(x: float, y: float, r: float) -> str:
    """The Earth in the black sky: a blue disc with green land and a white cloud, lit from the left."""
    c = Canvas()
    c.shape(ellipse_d(0, 0, r, r), P.BLUE, sw=2.4, light=(-4, -3))
    c.shape(f"M{-r * 0.55},{-r * 0.5} q{r * 0.3},{-r * 0.25} {r * 0.55},{-r * 0.05} q{r * 0.1},{r * 0.3} "
            f"{-r * 0.15},{r * 0.5} q{-r * 0.35},{r * 0.05} {-r * 0.4},{-r * 0.45} Z", P.GREEN, sw=1.6, light=None)
    c.shape(f"M{r * 0.1},{r * 0.2} q{r * 0.35},{-r * 0.1} {r * 0.55},{r * 0.15} q{-r * 0.05},{r * 0.35} "
            f"{-r * 0.35},{r * 0.4} q{-r * 0.3},{-r * 0.15} {-r * 0.2},{-r * 0.55} Z", P.GREEN, sw=1.6, light=None)
    c.path(f"M{-r * 0.7},{r * 0.05} q{r * 0.3},{-r * 0.12} {r * 0.6},0", "none", 2.2, P.WHITE)
    return props._at(c, x, y, 1.0)


def _observatory(x: float, y: float, k: float, accent: str) -> str:
    """The review observatory, the hero of the base: a round tower in the chapter's colour under a white dome
    whose slit is open, the telescope reaching out of it to the sky, a door and a round window below. The origin
    is the middle of the tower's foot; 300 wide, about 420 tall with the telescope."""
    c = Canvas()
    c.shape(rounded_rect_d(-130, -210, 260, 210, 10), accent, sw=2.8, light=(-4, -3))
    c.line("M-130,-150 H130 M-130,-80 H130", 1.6, opacity=0.4)
    c.shape(rounded_rect_d(-34, -110, 68, 110, 30), darken(accent, 0.7), sw=2.4, light=None)       # the door
    c.add(f'<circle cx="18" cy="-56" r="4" fill="{P.METAL_LIGHT}" stroke="{P.INK}" stroke-width="1.4"/>')
    c.shape(ellipse_d(-86, -170, 20, 20), P.SCREEN_LIGHT, sw=2.2, light=None)                       # a window
    c.path(ellipse_d(-86, -170, 20, 20), "none", 2.2)
    c.shape(ellipse_d(86, -170, 20, 20), P.SCREEN_LIGHT, sw=2.2, light=None)
    c.path(ellipse_d(86, -170, 20, 20), "none", 2.2)
    # the dome, its slit open towards the upper left, the telescope out of it
    c.shape("M-150,-210 A150,140 0 0 1 150,-210 Z", P.WHITE, sw=2.8, light=(-5, -4))
    c.shape("M-58,-336 L-20,-348 L30,-212 L-20,-212 Z", darken(P.CHARCOAL, 0.9), sw=2.2, light=None)
    c.add('<g transform="translate(0,-240) rotate(-58)">')
    c.shape(rounded_rect_d(0, -26, 230, 52, 10), P.METAL_LIGHT, sw=2.6, light=(-3, -3))
    c.shape(rounded_rect_d(214, -34, 40, 68, 8), P.METAL, sw=2.4, light=None)
    c.shape(ellipse_d(254, 0, 8, 28), P.LENS, sw=2, light=None)
    c.line("M70,-26 V26 M150,-26 V26", 1.6, opacity=0.5)
    c.add("</g>")
    c.add(f'<circle cx="0" cy="-240" r="18" fill="{P.METAL_DARK}" stroke="{P.INK}" stroke-width="2.2"/>')
    c.shape(rounded_rect_d(-150, -216, 300, 14, 6), P.METAL, sw=2.2, light=None)                  # the dome ring
    return props._at(c, x, y, k)


def _rover(x: float, y: float, k: float, mirror: bool = False) -> str:
    """A moon rover, one subagent sent out to look: a box body on six wheels, a mast with a dish and a camera head
    with a big lens. The origin is the middle under the wheels; 150 wide, 150 tall."""
    c = Canvas()
    c.shape(rounded_rect_d(-70, -66, 140, 40, 8), P.METAL_LIGHT, sw=2.4, light=(-3, -3))
    c.shape(rounded_rect_d(-52, -58, 60, 22, 4), P.SCREEN_LIGHT, sw=1.8, light=None)               # solar panel
    c.line("M-32,-58 V-36 M-12,-58 V-36", 1.2, opacity=0.6)
    c.line("M-64,-26 L-58,-16 M64,-26 L58,-16 M0,-26 V-16", 2.2)
    for wx in (-56, 0, 56):
        c.add(f'<circle cx="{wx}" cy="-12" r="12" fill="{P.CHARCOAL}" stroke="{P.INK}" stroke-width="2.2"/>'
              f'<circle cx="{wx}" cy="-12" r="4" fill="{P.METAL}" stroke="{P.INK}" stroke-width="1.2"/>')
    c.line("M40,-66 V-120", 3)                                                                     # the mast
    c.shape(rounded_rect_d(26, -146, 44, 28, 6), P.METAL, sw=2.2, light=None)                      # camera head
    c.shape(ellipse_d(70, -132, 9, 11), P.LENS, sw=2, light=None)
    c.line("M-40,-66 L-56,-110", 2.4)                                                              # the antenna
    c.shape("M-74,-118 Q-56,-96 -38,-118 Z", P.WHITE, sw=2, light=None)
    return props._at(c, x, y, k, mirror)


def _stone(x: float, y: float) -> str:
    """A moon stone lying on the plain, 22 wide."""
    c = Canvas()
    c.shape("M-11,0 Q-12,-8 -4,-11 Q6,-12 11,-4 Q12,0 8,0 Z", P.STONE, sw=1.6, light=(-2, -2))
    return props._at(c, x, y, 1.0)


def _deck(c: Canvas, top: float, width: float, height: float) -> None:
    """The metal deck of the base where everyone stands: rows of riveted plates."""
    c.add(f'<path d="M0,{top} H{width} V{height} H0 Z" fill="{P.METAL}" stroke="{P.INK}" stroke-width="2.4"/>')
    row = 0
    y = top
    while y < height:
        step = 44 + row * 14
        offset = 60 if row % 2 else 0
        x = -offset
        while x < width:
            c.add(f'<path d="{rounded_rect_d(x + 3, y + 3, 114, step - 6, 4)}" fill="{P.METAL_LIGHT}" '
                  f'stroke="{P.INK}" stroke-width="1.2"/>')
            for rx, ry in ((x + 10, y + 10), (x + 110, y + 10)):
                c.add(f'<circle cx="{rx}" cy="{ry}" r="2" fill="{P.METAL_DARK}"/>')
            x += 120
        y += step
        row += 1


def moonbase(s, accent: str) -> object:
    """The review base on the Moon: the agents check, people decide.

    The observatory of review stands on the right under the black sky, its telescope out of the open dome, the
    sparrow perched on the dome's ring. Two rovers - the subagents sent out to look at the code - drive over the
    craters, each leaving its tracks in the dust. On the deck in front the agent waves the near rover on, the cat
    at the observatory points up to where the telescope looks, and the caterpillar checks its list. The professor
    dispatches from the left under his bubble; the Earth hangs low in the corner of the sky.
    """
    horizon = 760
    sets.sky(s.back, darken(mix(accent, P.PEN, 0.5), 0.55), mix(accent, P.CHARCOAL, 0.3), horizon, W)
    sets.stars(s.back, (40, 260, W - 40, horizon - 80), 70, seed=91)
    s.back.add(_earth(730, 360, 52))
    # far mountains in the chapter's colour, then the grey plain with its lit ridges
    ridge = mix(accent, P.STONE, 0.45)
    s.back.add(f'<path d="M0,{horizon - 20} L90,{horizon - 92} L170,{horizon - 40} L260,{horizon - 120} '
               f'L360,{horizon - 50} L430,{horizon - 84} L520,{horizon - 30} L640,{horizon - 104} '
               f'L740,{horizon - 44} L{W},{horizon - 80} V{horizon + 20} H0 Z" fill="{ridge}" stroke="{P.INK}" '
               f'stroke-width="2.4"/>')
    s.back.add(f'<path d="M90,{horizon - 92} L120,{horizon - 60} M260,{horizon - 120} L296,{horizon - 76} '
               f'M640,{horizon - 104} L676,{horizon - 64}" stroke="{lighten(ridge, 0.5)}" stroke-width="3" '
               f'fill="none"/>')
    plain = mix(P.STONE, accent, 0.12)
    s.back.add(f'<path d="M0,{horizon} Q240,{horizon - 24} 480,{horizon - 8} T{W},{horizon - 14} V{H} H0 Z" '
               f'fill="{plain}" stroke="{P.INK}" stroke-width="2.4"/>')
    for y0, k0 in ((horizon + 70, 0.45), (horizon + 150, 0.6), (horizon + 210, 0.75)):
        s.back.add(f'<path d="M0,{y0} Q{W / 3},{y0 - 10 * k0} {W / 2},{y0 + 4} T{W},{y0 - 6}" fill="none" '
                   f'stroke="{darken(plain, 0.88)}" stroke-width="{2 * k0 + 1}"/>')
    deck = 1010
    _deck(s.back, deck, W, H)

    # --- the observatory, the sparrow on its dome ring
    s.put(deck - 4, _observatory(650, deck - 4, 0.78, accent), (533, deck - 336, 767, deck - 4), "observatory",
          group="observatory", backdrop=True)
    s.actor("sparrow", 586, deck - 162, "cheer", "smile", tall=130, group="observatory", depth=deck)

    # --- craters and stones over the plain, the two rovers driving out with their tracks behind them
    for cx, cy, k in ((300, 830, 0.7), (480, 800, 0.55), (300, 920, 0.5)):
        s.put(cy, _moon_crater(cx, cy, k), (cx - 44 * k, cy - 12 * k, cx + 44 * k, cy + 9 * k), f"crater{cx}")
    tracks = Canvas()
    tracks.line("M380,980 Q330,964 280,972 M380,992 Q330,976 280,984", 2, darken(plain, 0.75))
    tracks.line("M350,848 Q320,840 290,846", 1.6, darken(plain, 0.75))
    s.back.add(tracks.render())
    s.put(990, _rover(430, 990, 0.66), (380, 891, 480, 990), "rover_near", group="rover_near")
    s.put(856, _rover(390, 856, 0.42), (358, 793, 422, 856), "rover_far", group="rover_far")
    dust = Canvas()
    for dx, dy, r in ((-58, -10, 9), (-74, -18, 7), (-88, -12, 5)):
        dust.shape(ellipse_d(dx, dy, r, r * 0.8), lighten(plain, 0.4), sw=1.4, light=None)
    s.put(989, props._at(dust, 396, 990, 1.0), (300, 968, 390, 990), "dust", group="rover_near")
    s.scatter(lambda x, y: _stone(x, y), 5, (250, horizon + 30, 530, deck - 10), (22, 12))

    # --- the cast on the deck: the agent sends the rover on, the cat points to the sky, the caterpillar checks
    s.actor("agent", 320, 1160, "wave", "smile", tall=280, group="agent")
    s.actor("cat", 600, 1180, "point", "smile", flip=True, tall=200, group="cat")
    s.actor("caterpillar", 450, 1176, "write", "worry", tall=210, group="caterpillar")

    # --- the professor dispatching under his bubble
    prof = s.actor("professor", 140, 1096, "explain", "talk", tall=380)
    s.speaker(prof, width=92, left=8)
    return s.render()


# ============================================================================ chapter 10: the forest camp
def _pine(c: Canvas, x: float, base: float, h: float, color: str) -> tuple:
    """A pine standing at (x, base), `h` tall: a trunk under five tiers of boughs, each tier lit on its left and
    its lower edge drooping. Returns its box."""
    w = h * 0.26
    c.shape(f"M{x - w * 0.12},{base} L{x - w * 0.08},{base - h * 0.2} H{x + w * 0.08} L{x + w * 0.12},{base} Z",
            P.TRUNK, sw=2.2, light=(-2, 0))
    tiers = 5
    for i in range(tiers):
        t = i / tiers
        bottom = base - h * 0.14 - h * 0.78 * t
        half = w * (1 - t * 0.72)
        top = bottom - h * 0.3
        c.shape(f"M{x},{top} L{x + half},{bottom} Q{x + half * 0.5},{bottom + 7} {x},{bottom + 2} "
                f"Q{x - half * 0.5},{bottom + 7} {x - half},{bottom} Z", color, sw=2.2, light=(-4, -2))
    return (x - w, base - h - 2, x + w, base)


def _tent(c: Canvas, x: float, base: float, w: float, h: float, color: str) -> tuple:
    """A ridge tent seen from its front: the canvas walls, the door flaps tied back on a dark inside, the ridge
    pole's tip, two pegs. Returns its box."""
    c.shape(f"M{x - w / 2},{base} L{x},{base - h} L{x + w / 2},{base} Z", color, sw=2.4, light=(-4, -2))
    c.shape(f"M{x - w * 0.16},{base} L{x},{base - h * 0.62} L{x + w * 0.16},{base} Z", darken(color, 0.45), sw=2,
            light=None)
    c.line(f"M{x},{base - h * 0.62} L{x - w * 0.2},{base} M{x},{base - h * 0.62} L{x + w * 0.2},{base}", 2.2)
    c.line(f"M{x},{base - h} V{base - h - 10}", 3, P.WOOD_DARK)
    c.line(f"M{x - w * 0.34},{base - h * 0.3} L{x - w * 0.26},{base - h * 0.44} M{x + w * 0.34},{base - h * 0.3} "
           f"L{x + w * 0.26},{base - h * 0.44}", 1.4, opacity=0.5)
    return (x - w / 2, base - h - 10, x + w / 2, base)


def _puff(c: Canvas, x: float, y: float, r: float, fill: str, opacity: float) -> None:
    """One puff of smoke: round lobes as one soft cloud, its outline faint, the whole puff at a flat opacity."""
    c.add(f'<g opacity="{opacity:.2f}">')
    c.path(f"M{x - r},{y + r * 0.35} Q{x - r * 1.15},{y - r * 0.5} {x - r * 0.35},{y - r * 0.55} "
           f"Q{x - r * 0.1},{y - r * 1.15} {x + r * 0.45},{y - r * 0.75} Q{x + r * 1.15},{y - r * 0.45} "
           f"{x + r},{y + r * 0.3} Q{x},{y + r * 0.75} {x - r},{y + r * 0.35} Z", fill, 1.1, mix(INK, fill, 0.78))
    c.add("</g>")


def _campfire(c: Canvas, x: float, y: float, k: float) -> None:
    """A campfire on the ground at (x, y): a ring of stones, crossed logs, three tongues of flame and its glow."""
    for r, a in ((60, 0.14), (40, 0.2)):
        c.add(f'<circle cx="{x}" cy="{y - 18 * k}" r="{r * k}" fill="{P.SUN}" opacity="{a}"/>')
    c.shape(rounded_rect_d(x - 30 * k, y - 10 * k, 60 * k, 9 * k, 4 * k), P.WOOD_DARK, sw=1.8, light=None)
    c.add(f'<g transform="rotate(-14 {x} {y - 6 * k})">')
    c.shape(rounded_rect_d(x - 30 * k, y - 10 * k, 60 * k, 8 * k, 4 * k), P.TRUNK, sw=1.8, light=None)
    c.add("</g>")
    c.shape(f"M{x - 18 * k},{y - 10 * k} Q{x - 24 * k},{y - 34 * k} {x - 6 * k},{y - 52 * k} "
            f"Q{x - 4 * k},{y - 34 * k} {x + 4 * k},{y - 30 * k} Q{x + 10 * k},{y - 46 * k} {x + 6 * k},{y - 62 * k} "
            f"Q{x + 28 * k},{y - 38 * k} {x + 18 * k},{y - 10 * k} Z", P.ORANGE, sw=1.8, light=None)
    c.shape(f"M{x - 9 * k},{y - 10 * k} Q{x - 12 * k},{y - 26 * k} {x - 2 * k},{y - 38 * k} "
            f"Q{x + 2 * k},{y - 24 * k} {x + 8 * k},{y - 30 * k} Q{x + 14 * k},{y - 18 * k} {x + 9 * k},{y - 10 * k} Z",
            P.SUN, sw=1.2, light=None)
    for dx in (-34, -22, 22, 34):
        c.shape(ellipse_d(x + dx * k, y - 3 * k, 7 * k, 5 * k), P.STONE, sw=1.4, light=None)


def _palisade(c: Canvas, x0: float, x1: float, ground: float, top: float, gap: tuple, wood: str, seed: int) -> None:
    """A palisade of upright logs from x0 to x1, their tops sharpened to points, bound by a rail on the inside; the
    logs stop at the gateway `gap` (left, right)."""
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        lw = rnd.uniform(20, 25)
        if gap[0] - lw < x < gap[1]:
            x = gap[1]
            continue
        t = top + rnd.uniform(-6, 8)
        c.shape(f"M{x},{ground} V{t} L{x + lw / 2},{t - lw * 0.9} L{x + lw},{t} V{ground} Z",
                wood if rnd.random() < 0.6 else darken(wood, 0.92), sw=2, light=(-3, 0))
        c.line(f"M{x + lw * 0.35},{t + 20} v{rnd.uniform(18, 40)} M{x + lw * 0.65},{t + 70} v{rnd.uniform(14, 30)}",
               1.1, opacity=0.4)
        c.shape(ellipse_d(x + lw / 2, t - lw * 0.32, lw * 0.18, lw * 0.12), lighten(wood, 0.3), sw=0, light=None)
        x += lw


def _log_wall(c: Canvas, left: float, right: float, top: float, bottom: float, wood: str) -> None:
    """A wall of horizontal logs laid one on another, their round sawn ends showing at both corners."""
    y = bottom
    i = 0
    while y > top + 4:
        lh = min(22.0, y - top)
        c.shape(rounded_rect_d(left, y - lh, right - left, lh, lh / 2), wood if i % 2 else darken(wood, 0.93),
                sw=2, light=(0, -2))
        for ex in (left + lh / 2 + 1, right - lh / 2 - 1):
            c.shape(ellipse_d(ex, y - lh / 2, lh / 2 - 2, lh / 2 - 2), P.WOOD_PALE, sw=1.4, light=None)
            c.add(f'<circle cx="{ex}" cy="{y - lh / 2}" r="{lh * 0.14}" fill="none" stroke="{INK}" '
                  f'stroke-width=".9" stroke-opacity=".5"/>')
        y -= lh
        i += 1


def _gate_tower(c: Canvas, x: float, ground: float, accent: str, wood: str, flag_way: int) -> tuple:
    """A gate tower of logs, 80 wide: the log body, a lookout above it of planks with a lit window, a pyramid roof
    of shingles in the chapter's colour and a pennant on its pole. Returns its box."""
    body_top, cab_top, eave = ground - 366, ground - 430, ground - 436
    _log_wall(c, x - 40, x + 40, body_top, ground, wood)
    c.shape(rounded_rect_d(x - 6, ground - 280, 12, 34, 4), darken(P.CHARCOAL, 0.9), sw=1.8, light=None)  # loophole
    c.shape(rounded_rect_d(x - 52, body_top - 8, 104, 12, 3), P.WOOD_DARK, sw=2, light=None)              # floor beam
    for bx in (x - 46, x + 46):
        c.line(f"M{bx},{body_top + 4} L{x + (bx - x) * 0.6},{body_top + 34}", 4, P.WOOD_DARK)               # struts
    c.shape(f"M{x - 50},{body_top - 8} V{cab_top} H{x + 50} V{body_top - 8} Z", P.WOOD_LIGHT, sw=2.2, light=(-3, 0))
    for px in range(int(x - 38), int(x + 50), 16):
        c.line(f"M{px},{cab_top + 2} V{body_top - 10}", 1.2, opacity=0.45)
    c.shape(rounded_rect_d(x - 20, cab_top + 14, 40, 30, 3), P.SUN, sw=2, light=None)                     # lit window
    c.line(f"M{x},{cab_top + 14} V{cab_top + 44} M{x - 20},{cab_top + 29} H{x + 20}", 2, P.WOOD_DARK)
    roof = darken(accent, 0.85)
    c.shape(f"M{x - 64},{eave + 8} L{x},{eave - 84} L{x + 64},{eave + 8} Z", roof, sw=2.6, light=(-5, -2))
    for i in range(1, 5):
        yy = eave + 8 - i * 18
        half = 64 * (1 - i * 18 / 92)
        c.line(f"M{x - half},{yy} H{x + half}", 1.4, opacity=0.45)
    pole_top = eave - 84 - 52
    c.line(f"M{x},{eave - 84} V{pole_top}", 3, P.WOOD_DARK)
    c.shape(f"M{x},{pole_top + 2} Q{x + flag_way * 20},{pole_top + 4} {x + flag_way * 38},{pole_top + 13} "
            f"Q{x + flag_way * 20},{pole_top + 18} {x},{pole_top + 24} Z", lighten(accent, 0.25), sw=2, light=None)
    return (x - 64, pole_top - 2, x + 64, ground)


def _watchtower(c: Canvas, x: float, ground: float, deck: float, wood: str, accent: str) -> tuple:
    """A watchtower on four splayed legs with cross braces and a ladder up to its railed platform under a little
    gable roof. Returns its box."""
    for lx, tx in ((x - 44, x - 30), (x + 44, x + 30)):
        c.shape(f"M{lx - 5},{ground} L{tx - 5},{deck} H{tx + 5} L{lx + 5},{ground} Z", wood, sw=2, light=(-2, 0))
    for y0, y1 in ((ground - 20, deck + 90), (deck + 90, deck + 10)):
        hw0 = 44 - (ground - y0) / (ground - deck) * 14
        hw1 = 44 - (ground - y1) / (ground - deck) * 14
        c.line(f"M{x - hw0},{y0} L{x + hw1},{y1} M{x + hw0},{y0} L{x - hw1},{y1}", 3.4, P.WOOD_DARK)
    for side in (-1, 1):
        c.line(f"M{x + side * 12},{ground} L{x + side * 12},{deck}", 2.4, P.WOOD_DARK)
    for ry in range(int(ground - 16), int(deck), -18):
        c.line(f"M{x - 12},{ry} H{x + 12}", 2.2, P.WOOD_DARK)
    c.shape(rounded_rect_d(x - 44, deck - 6, 88, 12, 3), P.WOOD_DARK, sw=2, light=None)
    c.shape(f"M{x - 40},{deck - 6} V{deck - 40} H{x + 40} V{deck - 6} Z", P.WOOD_LIGHT, sw=2, light=(-2, 0))
    for px in (x - 20, x, x + 20):
        c.line(f"M{px},{deck - 40} V{deck - 6}", 1.4, opacity=0.5)
    for px in (x - 36, x + 36):
        c.line(f"M{px},{deck - 40} V{deck - 84}", 4, P.WOOD_DARK)
    c.shape(f"M{x - 52},{deck - 80} L{x},{deck - 122} L{x + 52},{deck - 80} Z", darken(accent, 0.85), sw=2.4,
            light=(-4, -2))
    return (x - 52, deck - 124, x + 52, ground)


def _lantern(c: Canvas, x: float, y: float, k: float) -> None:
    """A hanging lantern whose ring is at (x, y): a ring, a cap, a glass with the flame lit, a frame of bars and a
    base, and its glow."""
    for r, a in ((46, 0.14), (30, 0.22)):
        c.add(f'<circle cx="{x}" cy="{y + 26 * k}" r="{r * k}" fill="{P.SUN}" opacity="{a}"/>')
    c.add(f'<circle cx="{x}" cy="{y + 2 * k}" r="{3.6 * k}" fill="none" stroke="{INK}" stroke-width="{1.8 * k}"/>')
    c.shape(f"M{x - 12 * k},{y + 14 * k} L{x},{y + 5 * k} L{x + 12 * k},{y + 14 * k} Z", P.CHARCOAL, sw=1.8 * k,
            light=None)
    c.shape(rounded_rect_d(x - 10 * k, y + 14 * k, 20 * k, 26 * k, 3 * k), P.YELLOW_PALE, sw=1.8 * k, light=None)
    c.shape(f"M{x},{y + 20 * k} Q{x + 5 * k},{y + 28 * k} {x},{y + 34 * k} "
            f"Q{x - 5 * k},{y + 28 * k} {x},{y + 20 * k} Z", P.ORANGE, sw=1 * k, light=None)
    c.line(f"M{x - 4 * k},{y + 14 * k} V{y + 40 * k} M{x + 4 * k},{y + 14 * k} V{y + 40 * k}", 1.2 * k,
           P.CHARCOAL)
    c.shape(rounded_rect_d(x - 12 * k, y + 39 * k, 24 * k, 6 * k, 2 * k), P.CHARCOAL, sw=1.6 * k, light=None)


def _gateway(c: Canvas, left: float, right: float, top: float, ground: float, wood: str) -> None:
    """The gateway between the towers: two leaves of planks swung open inwards, each with its iron hinge straps
    and the brackets of the crossbar; the crossbar itself leans by the right leaf; the heavy lintel log above."""
    leaf = (right - left) * 0.22
    for side in (-1, 1):
        hinge = left if side < 0 else right
        free = hinge - side * leaf
        c.shape(f"M{hinge},{ground} V{top + 30} L{free},{top + 48} V{ground - 16} Z", wood, sw=2.2,
                light=(side * 2, 0))
        for f in (0.33, 0.66):
            px = hinge - side * leaf * f
            c.line(f"M{px},{top + 30 + 18 * f} V{ground - 16 * f}", 1.2, opacity=0.5)
        for hy in (top + 70, ground - 60):
            c.line(f"M{hinge},{hy} L{free + side * 4},{hy + 10}", 4.4, P.CHARCOAL)                      # hinge straps
            c.dot(hinge - side * 4, hy + 1, 2.6, P.METAL_DARK)
        c.shape(rounded_rect_d(free + (6 if side < 0 else -18), (top + ground) / 2 + 4, 12, 16, 2), P.CHARCOAL,
                sw=1.4, light=None)                                                                        # bar bracket
    # the crossbar leaning against the right gate post
    c.shape(f"M{right - 30},{ground} L{right - 14},{top + 90} L{right - 4},{top + 92} L{right - 18},{ground} Z",
            P.WOOD_DARK, sw=2, light=None)
    c.shape(rounded_rect_d(left - 18, top - 4, right - left + 36, 30, 15), wood, sw=2.6, light=(0, -3))  # the lintel
    for ex in (left - 3, right + 3):
        c.shape(ellipse_d(ex, top + 11, 11, 11), P.WOOD_PALE, sw=1.6, light=None)


def _dusk_cloud(c: Canvas, x: float, y: float, w: float, accent: str) -> None:
    """A long evening cloud centred at (x, y), `w` wide: dark in the chapter's colour above, its underside lit."""
    h = w * 0.16
    d = (f"M{x - w / 2},{y + h * 0.4} Q{x - w * 0.46},{y - h * 0.5} {x - w * 0.24},{y - h * 0.4} "
         f"Q{x - w * 0.1},{y - h * 1.3} {x + w * 0.1},{y - h * 0.7} Q{x + w * 0.3},{y - h * 1.1} {x + w * 0.38},"
         f"{y - h * 0.2} Q{x + w * 0.52},{y - h * 0.1} {x + w / 2},{y + h * 0.4} Z")
    c.shape(d, mix(accent, P.PEN, 0.3), sw=1.8, light=None)
    c.line(f"M{x - w * 0.44},{y + h * 0.3} Q{x},{y + h * 0.1} {x + w * 0.44},{y + h * 0.3}", 3,
           mix(P.SUN, P.ORANGE, 0.4))


def _check_table(x: float, top: float, k: float, accent: str) -> str:
    """The checkpoint table: a plank top on two trestle legs; on it a tray of envelopes still to look at, a
    lamp lit, and one envelope opened with a folded slip of paper half out of it - the instruction slipped in."""
    c = Canvas()
    for lx in (-50, 50):
        c.line(f"M{lx - 12},70 L{lx},6 L{lx + 12},70", 5, P.WOOD_DARK)
    c.line("M-46,44 H46", 4, P.WOOD_DARK)
    c.shape(rounded_rect_d(-66, 0, 132, 12, 3), P.WOOD_LIGHT, sw=2.2, light=(0, -2))
    # the tray with its stack of envelopes
    c.shape(rounded_rect_d(-60, -14, 46, 14, 2), P.WOOD, sw=1.8, light=None)
    for i, col in enumerate((P.CARD, P.CREAM, P.CARD)):
        c.shape(rounded_rect_d(-56 + i * 2, -22 - i * 5, 38, 14, 1.5), col, sw=1.4, light=None)
        c.line(f"M{-56 + i * 2},{-22 - i * 5} L{-37 + i * 2},{-14 - i * 5} L{-18 + i * 2},{-22 - i * 5}", 1)
    # the lamp
    c.shape(rounded_rect_d(-8, -6, 22, 6, 2), P.CHARCOAL, sw=1.4, light=None)
    for r, a in ((26, 0.16), (16, 0.24)):
        c.add(f'<circle cx="3" cy="-22" r="{r}" fill="{P.SUN}" opacity="{a}"/>')
    c.shape("M-5,-6 Q-10,-22 -3,-34 H9 Q16,-22 11,-6 Z", P.YELLOW_PALE, sw=1.6, light=None)
    c.shape("M3,-14 Q8,-21 3,-28 Q-2,-21 3,-14 Z", P.ORANGE, sw=1, light=None)
    c.shape(rounded_rect_d(-5, -40, 16, 6, 2), P.CHARCOAL, sw=1.4, light=None)
    c.line("M-3,-40 Q3,-50 9,-40", 1.6, P.CHARCOAL)
    # the opened envelope and the slip coming out of it
    c.shape("M24,0 V-16 H58 V0 Z", P.CARD, sw=1.4, light=None)
    c.shape("M24,-16 L41,-28 L58,-16 Z", P.CREAM, sw=1.2, light=None)
    c.shape("M30,-12 L38,-40 L58,-34 L50,-6 Z", P.WHITE, sw=1.4, light=None)
    c.line("M38,-30 L52,-26 M36,-24 L50,-20 M35,-18 L46,-15", 1.1, P.RED)
    c.add(f'<circle cx="41" cy="-7" r="3.4" fill="{P.RED}" stroke="{INK}" stroke-width=".9"/>')
    return props._at(c, x, top, k)


def _stump(x: float, y: float, k: float) -> str:
    """A sawn tree stump on the deck by the checkpoint, its rings showing; 60 wide, 44 tall."""
    c = Canvas()
    c.shape("M-28,0 L-24,-36 H24 L28,0 Q0,6 -28,0 Z", P.TRUNK, sw=2.2, light=(-3, 0))
    c.line("M-14,-30 V-4 M4,-32 V-8 M16,-28 V-6", 1.2, opacity=0.45)
    c.shape(ellipse_d(0, -36, 24, 8), P.WOOD_PALE, sw=2, light=None)
    c.add(f'<ellipse cx="0" cy="-36" rx="14" ry="4.6" fill="none" stroke="{INK}" stroke-width="1" '
          f'stroke-opacity=".5"/><ellipse cx="0" cy="-36" rx="6" ry="2" fill="none" stroke="{INK}" '
          f'stroke-width="1" stroke-opacity=".5"/>')
    return props._at(c, x, y, k)


def _parcel_on_twine(x: float, y: float, k: float) -> str:
    """A parcel carried by the loop of its twine: the loop through the fist at (x, y), the parcel hanging under it
    in brown paper, tied crosswise, a red seal on the knot."""
    c = Canvas()
    c.line("M-3,0 L-7,9 M3,0 L7,9", 1.1, P.WOOD_DARK)
    c.shape(rounded_rect_d(-15, 9, 30, 20, 2), P.KITCHEN_KRAFT, sw=1.3, light=(-1.5, -1))
    c.line("M0,9 V29 M-15,19 H15", 1.1, P.WOOD_DARK)
    c.add(f'<circle cx="0" cy="19" r="2.6" fill="{P.RED}" stroke="{INK}" stroke-width=".7"/>')
    return f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">{c.render()}</g>'


def forestcamp(s, accent: str) -> object:
    """The forest camp at dusk: what comes in is checked at the boundary.

    One hero: the camp's gate in a palisade of sharpened logs, two log towers with lit lookouts and pennants, the
    lintel log with a lantern hanging from it, the leaves swung open on the campfire inside, its smoke rising past
    the lintel into the evening sky. A watchtower stands at the far corner, tents and pines behind the wall, the
    moon and the first stars over the forest. On the plank landing in front of the gate the checkpoint: a table with
    a tray of envelopes and a lamp, where the cat looks through his magnifier at a slip of paper found inside an
    opened envelope - the instruction someone slipped in. The sparrow on a stump eyes the envelopes, the caterpillar
    doubts, the agent brings a parcel to be checked, and the professor explains under his bubble.
    """
    c = s.back
    horizon, ground, deck = 760, 920, 936
    wood = mix(P.WOOD, accent, 0.12)
    paint = c.gradient([(0, darken(mix(accent, P.PEN, 0.2), 0.62)), (0.45, accent),
                        (0.75, lighten(accent, 0.4)), (1, mix(lighten(accent, 0.55), P.SUN, 0.5))], 0, 0, 0, horizon)
    c.add(f'<rect x="-4" y="-4" width="{W + 8}" height="{horizon + 12}" fill="{paint}"/>')
    for cx_, cy_, w_ in ((440, 320, 220), (770, 400, 120)):      # long clouds lit from below
        _dusk_cloud(c, cx_, cy_, w_, accent)
    for bx, by, bk in ((330, 400, 1.0), (362, 384, 0.8), (388, 410, 0.7)):          # birds flying home
        c.line(f"M{bx - 12 * bk},{by} q{6 * bk},{-8 * bk} {12 * bk},0 q{6 * bk},{-8 * bk} {12 * bk},0", 2.6)
    sets.stars(c, (700, 30, W - 30, 250), 14, seed=101)
    sets.stars(c, (400, 270, W - 30, 420), 10, seed=102)
    # the moon, a crescent
    c.add(f'<circle cx="770" cy="130" r="58" fill="{P.YELLOW_PALE}" opacity=".18"/>')
    c.path("M752,92 A42,42 0 1 0 806,152 A34,34 0 1 1 752,92 Z", P.YELLOW_PALE, 2.2)
    # the forest beyond: two ridges in the chapter's colour, far firs on the near one
    far, near = mix(accent, P.PEN, 0.25), darken(accent, 0.72)
    c.shape(f"M-10,{horizon} L-10,{horizon - 66} Q120,{horizon - 110} 260,{horizon - 70} Q420,{horizon - 140} 600,"
            f"{horizon - 96} Q720,{horizon - 140} {W + 10},{horizon - 104} V{horizon} Z", lighten(far, 0.25), sw=2,
            light=None)
    c.shape(f"M-10,{horizon + 10} L-10,{horizon - 34} Q200,{horizon - 70} 420,{horizon - 44} Q640,{horizon - 76} "
            f"{W + 10},{horizon - 52} V{horizon + 10} Z", near, sw=2, light=None)
    for fx in range(18, W, 34):
        fy = horizon - 44 - 12 * math.sin(fx / 90) + 6
        c.add(f'<g transform="translate({fx},{fy}) scale(.42)"><path d="M0,-60 L20,-10 Q0,-4 -20,-10 Z" '
              f'fill="{darken(accent, 0.55)}" stroke="{INK}" stroke-width="2.4"/></g>')
    # the camp's ground behind the wall
    c.add(f'<rect x="-4" y="{horizon - 10}" width="{W + 8}" height="{deck - horizon + 14}" '
          f'fill="{darken(mix(P.GRASS_DARK, accent, 0.5), 0.6)}"/>')
    # tents and pines inside the camp, showing over the wall
    pine = mix(P.FIR, accent, 0.45)
    for box, name in ((_tent(c, 186, ground - 60, 124, 100, lighten(accent, 0.3)), "tent_left"),
                      (_pine(c, 312, ground - 14, 190, darken(pine, 0.9)), "pine_mid")):
        s.put(0.1, "", box, name, backdrop=True)
    tower = _watchtower(c, 784, ground - 10, ground - 336, wood, accent)
    s.put(0.1, "", tower, "watchtower", backdrop=True)
    # through the open gate: the camp's ground lit by the fire, a tent, the fire and its smoke
    gl, gr, lintel = 470, 610, 520
    c.add(f'<rect x="{gl}" y="{lintel}" width="{gr - gl}" height="{ground - lintel}" '
          f'fill="{darken(mix(P.GRASS_DARK, accent, 0.4), 0.7)}"/>')
    _campfire(c, 532, ground - 8, 0.9)
    # the smoke: one plume, behind the lintel and the towers, widening, thinning and bending away with the wind
    rnd = random.Random(31)
    puffs = []
    for i in range(30):
        t = i / 29
        cx = 534 + 160 * t ** 1.9 + 9 * math.sin(t * 9)
        cy = ground - 52 - 600 * t
        r = 8 + 40 * t ** 1.2
        for _ in range(2 if t < 0.25 else 3):
            puffs.append((cx + rnd.uniform(-0.55, 0.55) * r, cy + rnd.uniform(-0.3, 0.3) * r,
                          r * rnd.uniform(0.75, 1.1), t))
    for px, py, r, t in sorted(puffs, key=lambda p: -p[3]):        # the far, thin end first, the dense root on top
        _puff(c, px, py, r, mix(P.WHITE, mix(accent, P.STONE, 0.5), 0.15 + 0.35 * t), 0.62 - 0.54 * t)
    _palisade(c, -6, W + 6, ground, horizon + 50, (gl - 40, gr + 40), wood, seed=7)
    # the gate: the towers, the open leaves, the lintel and its lantern
    _gateway(c, gl, gr, lintel, ground, wood)
    left_tower = _gate_tower(c, gl - 40, ground, accent, wood, 1)
    right_tower = _gate_tower(c, gr + 40, ground, accent, wood, 1)
    c.line(f"M540,{lintel + 26} V{lintel + 40}", 3, P.CHARCOAL)
    _lantern(c, 540, lintel + 40, 1.0)
    s.put(0.2, "", (left_tower[0], left_tower[1], right_tower[2], ground), "gate", backdrop=True)
    # the plank landing in front of the gate, its edge beam along the wall's foot
    c.add(f'<rect x="-4" y="{deck}" width="{W + 8}" height="{H - deck + 4}" fill="{darken(wood, 0.6)}"/>')
    y, row = deck + 6, 0
    rnd = random.Random(5)
    while y < H:
        rh = 12 + row * 5
        x = -rnd.uniform(0, 90)
        while x < W:
            pl = rnd.uniform(110, 180)
            c.add(f'<rect x="{n(x + 1)}" y="{n(y + 1)}" width="{n(pl - 2)}" height="{n(rh - 2)}" rx="2" '
                  f'fill="{wood if (row + int(x / 60)) % 2 else lighten(wood, 0.12)}"/>')
            c.add(f'<circle cx="{n(x + 7)}" cy="{n(y + rh / 2)}" r="{n(rh * 0.07)}" fill="{P.WOOD_DARK}"/>'
                  f'<circle cx="{n(x + pl - 7)}" cy="{n(y + rh / 2)}" r="{n(rh * 0.07)}" fill="{P.WOOD_DARK}"/>')
            x += pl
        y += rh
        row += 1
    c.add(f'<rect x="-4" y="{deck - 4}" width="{W + 8}" height="12" fill="{P.WOOD_DARK}" stroke="{INK}" '
          f'stroke-width="1.6"/>')
    s.keep_clear((-4, deck - 4, W + 4, deck + 8))

    # --- the checkpoint: the table, the stump with the sparrow, the cat with his magnifier over the slip
    tk, tx, ty = 0.96, 622, 1074
    s.put(ty, _check_table(tx, ty, tk, accent), (tx - 70 * tk, ty - 52 * tk, tx + 70 * tk, ty + 70 * tk),
          "table", group="table", backdrop=True)
    s.put(1030, _stump(518, 1030, 0.9), (492, 996, 544, 1030), "stump", group="stump")
    s.actor("sparrow", 518, 998, "point", "smile", flip=False, tall=120, group="stump", depth=1041)
    cat = s.actor("cat", 764, 1176, "point", "smile", flip=True, tall=240, group="cat")
    s.hold(cat, handheld.magnifier, turn=80)

    # --- the caterpillar doubting, the agent bringing a parcel to the gate
    s.actor("caterpillar", 428, 1176, "think", "worry", tall=240, group="caterpillar")   # eyeing the parcel
    agent = s.actor("agent", 312, 1156, "walk", "smile", tall=300, group="agent")
    hang = s.grip(agent, "right")[2] - 180                       # the parcel hangs straight down from the fist
    s.hold(agent, lambda x, y, k: _parcel_on_twine(x, y, k * 0.72), "right", turn=hang)

    # --- the professor under his bubble
    prof = s.actor("professor", 142, 1096, "explain", "talk", tall=380)
    s.speaker(prof, width=74, left=8, air=4)
    return s.render()


# ============================================================================ chapter 11: the railway
def _wheel(c: Canvas, x: float, r: float, crank: float, centre: str) -> tuple[float, float]:
    """A locomotive wheel standing on the rail (y = 0) at x: the steel tyre, the spokes, the counterweight opposite
    the crank and the crank pin. Returns where the crank pin is."""
    cy = -r
    c.add(f'<circle cx="{n(x)}" cy="{n(cy)}" r="{n(r)}" fill="{P.CHARCOAL}" stroke="{INK}" stroke-width="2.4"/>')
    c.add(f'<circle cx="{n(x)}" cy="{n(cy)}" r="{n(r * 0.84)}" fill="{centre}" stroke="{INK}" stroke-width="1.6"/>')
    spokes = 12 if r > 30 else 8
    c.line(" ".join(f"M{n(x + r * 0.2 * math.cos(a))},{n(cy + r * 0.2 * math.sin(a))} "
                    f"L{n(x + r * 0.8 * math.cos(a))},{n(cy + r * 0.8 * math.sin(a))}"
                    for a in (i * 2 * math.pi / spokes for i in range(spokes))),
           max(2.0, r * 0.07), darken(centre, 0.6))
    if r > 30:                                       # the counterweight, a crescent opposite the crank
        a0, a1 = math.radians(crank + 180 - 42), math.radians(crank + 180 + 42)
        rr = r * 0.82
        c.shape(f"M{n(x + rr * math.cos(a0))},{n(cy + rr * math.sin(a0))} A{n(rr)},{n(rr)} 0 0 1 "
                f"{n(x + rr * math.cos(a1))},{n(cy + rr * math.sin(a1))} Z", darken(centre, 0.85), sw=1.4, light=None)
    c.add(f'<circle cx="{n(x)}" cy="{n(cy)}" r="{n(r * 0.2)}" fill="{P.METAL_DARK}" stroke="{INK}" '
          f'stroke-width="1.6"/>')
    pin = (x + r * 0.5 * math.cos(math.radians(crank)), cy + r * 0.5 * math.sin(math.radians(crank)))
    return pin


def _puffs(c: Canvas, x0: float, y0: float, rise: float, drift: float, r0: float, r1: float, count: int,
           seed: int, tint: str, start: float = 0.62) -> None:
    """A plume of smoke or steam: many puffs, small and dense where it leaves the chimney, wider, paler and thinner
    as it rises and drifts back; the far end is drawn first so the dense root lies on top."""
    rnd = random.Random(seed)
    puffs = []
    for i in range(count):
        t = i / (count - 1)
        cx = x0 + drift * t ** 1.25 + 6 * math.sin(t * 8)
        cy = y0 - rise * t
        r = r0 + (r1 - r0) * t ** 1.1
        for _ in range(2 if t < 0.2 else 3):
            puffs.append((cx + rnd.uniform(-0.5, 0.5) * r, cy + rnd.uniform(-0.3, 0.3) * r, r * rnd.uniform(0.75, 1.1),
                          t))
    for px, py, r, t in sorted(puffs, key=lambda p: -p[3]):
        _puff(c, px, py, r, mix(P.WHITE, tint, 0.12 + 0.4 * t), start - (start - 0.1) * t)


def _locomotive(x: float, rail: float, k: float, accent: str, crank: float = 300) -> str:
    """The tank engine, the hero of the railway, facing left as it runs into the station: buffer beam and
    buffers, the smokebox with its chimney and lit headlamp, the boiler with its brass dome and safety valves, the
    side tanks lined in brass over the wheels, the cylinder and the rods to the two big driving wheels, the cab
    with its open side and the coal bunker behind. The origin is the front buffer's face at rail level; 410 long,
    272 tall."""
    c = Canvas()
    body, deep = accent, darken(accent, 0.62)
    # the frame under everything, between the wheels
    c.shape(rounded_rect_d(14, -112, 396, 22, 3), P.CHARCOAL, sw=2, light=None)
    # the wheels: the leading wheel, two big driving wheels, the trailing wheel under the cab
    pins = []
    _wheel(c, 74, 24, crank, deep)
    for wx in (176, 276):
        pins.append(_wheel(c, wx, 48, crank, deep))
    _wheel(c, 366, 26, crank, deep)
    # the cylinder under the smokebox and its guide bars
    c.shape(rounded_rect_d(40, -92, 70, 40, 8), body, sw=2.4, light=(-2, -2))
    c.shape(rounded_rect_d(36, -94, 10, 44, 3), P.GOLD, sw=1.8, light=None)
    c.shape(rounded_rect_d(104, -94, 10, 44, 3), P.GOLD, sw=1.8, light=None)
    c.line("M114,-78 H168 M114,-66 H168", 2.6, P.METAL_DARK)
    # the crosshead slides in the guides, the connecting rod runs from it to the first driving wheel's crank pin
    (p1x, p1y), (p2x, p2y) = pins
    head = 140 + 24 * math.cos(math.radians(crank))
    c.shape(rounded_rect_d(head - 10, -80, 20, 16, 3), P.METAL, sw=1.6, light=None)
    c.line(f"M110,-72 H{n(head)}", 4, P.METAL_LIGHT)                                              # piston rod
    c.tube(f"M{n(head)},-72 L{n(p1x)},{n(p1y)}", P.METAL, 7, sw=1.6)                            # connecting rod
    c.tube(f"M{n(p1x)},{n(p1y)} L{n(p2x)},{n(p2y)}", P.METAL_LIGHT, 7, sw=1.6)                  # coupling rod
    for px, py in pins:
        c.add(f'<circle cx="{n(px)}" cy="{n(py)}" r="5" fill="{P.METAL_DARK}" stroke="{INK}" stroke-width="1.4"/>')
    # the running board along the engine
    c.shape(rounded_rect_d(10, -118, 402, 10, 2), P.CHARCOAL, sw=2, light=None)
    # the buffer beam and the buffer, the coupling hook under it
    c.shape(rounded_rect_d(0, -132, 18, 44, 3), deep, sw=2.2, light=None)
    c.shape(rounded_rect_d(-16, -116, 18, 12, 2), P.METAL_DARK, sw=1.8, light=None)
    c.shape(rounded_rect_d(-24, -124, 9, 28, 3), P.METAL, sw=1.8, light=None)
    c.line("M0,-96 h-10 q-6,0 -6,6", 3, P.CHARCOAL)
    # the boiler, then the side tank over it, lined in brass
    c.shape(rounded_rect_d(70, -222, 230, 104, 18), body, sw=2.6, light=(-3, -4))
    for bx in (132, 204):
        c.shape(rounded_rect_d(bx, -222, 7, 30, 2), P.GOLD, sw=1.2, light=None)
    c.line("M86,-198 H286", 2, P.GOLD)                                                           # handrail
    for hx in (96, 160, 224, 280):
        c.dot(hx, -198, 2.6, P.METAL_DARK)
    c.shape(rounded_rect_d(118, -192, 172, 76, 6), body, sw=2.6, light=(-3, -3))
    c.path(rounded_rect_d(128, -182, 152, 56, 4), "none", 2.2, P.GOLD)
    # the smokebox, its door seen edge on, the chimney with its copper cap
    c.shape(rounded_rect_d(26, -228, 58, 116, 10), P.CHARCOAL, sw=2.6, light=(-3, -3))
    c.shape("M26,-222 Q12,-170 26,-118 Z", darken(P.CHARCOAL, 0.8), sw=2, light=None)
    c.dot(20, -170, 3, P.METAL)
    c.shape("M40,-226 L44,-262 H70 L74,-226 Z", P.CHARCOAL, sw=2.4, light=(-2, 0))
    c.shape(rounded_rect_d(36, -276, 42, 16, 4), P.GOLD, sw=2.2, light=(-2, -2))
    # the lamp on its bracket at the top of the buffer beam, lit
    for r, a in ((26, 0.16), (16, 0.26)):
        c.add(f'<circle cx="2" cy="-146" r="{r}" fill="{P.SUN}" opacity="{a}"/>')
    c.shape(rounded_rect_d(4, -158, 18, 24, 3), P.CHARCOAL, sw=1.8, light=None)
    c.shape(rounded_rect_d(0, -153, 7, 14, 2), P.YELLOW_PALE, sw=1.4, light=None)
    c.line("M8,-158 Q13,-166 18,-158", 1.8, P.CHARCOAL)
    # the dome, the safety valves and the whistle on top of the boiler
    c.shape("M150,-220 Q150,-252 172,-254 Q194,-252 194,-220 Z", P.GOLD, sw=2.4, light=(-3, -3))
    c.shape(rounded_rect_d(236, -238, 10, 18, 2), P.GOLD, sw=1.6, light=None)
    c.shape(rounded_rect_d(250, -238, 10, 18, 2), P.GOLD, sw=1.6, light=None)
    c.line("M274,-222 V-238", 2.4, P.METAL_DARK)
    c.shape("M268,-238 H280 L278,-252 H270 Z", P.GOLD, sw=1.6, light=None)
    # the cab: the dark inside behind its open side, the roof on its pillars; the coal bunker behind it
    c.shape(rounded_rect_d(296, -268, 80, 150, 4), darken(deep, 0.5), sw=2.4, light=None)
    c.shape(rounded_rect_d(372, -226, 40, 108, 4), body, sw=2.4, light=(-2, -2))
    c.path(rounded_rect_d(378, -218, 28, 92, 3), "none", 2, P.GOLD)
    c.shape("M374,-226 Q378,-246 392,-248 Q406,-246 410,-226 Z", darken(P.CHARCOAL, 0.8), sw=1.8, light=None)
    for cx_, cy_ in ((384, -232), (394, -238), (402, -231), (390, -228)):            # lumps of coal on the heap
        c.shape(ellipse_d(cx_, cy_, 4.5, 3.2), P.CHARCOAL, sw=1, light=None)
    c.shape("M282,-280 Q340,-300 398,-280 V-268 H282 Z", P.CHARCOAL, sw=2.6, light=(0, -2))       # the roof
    return props._at(c, x, rail, k)


def _cab_side(x: float, rail: float, k: float, accent: str) -> str:
    """The cab's near side, drawn over the driver: the front pillar with its round spectacle window, the rear
    pillar with its handrail, and the panel up to the driver's waist, lined in brass."""
    c = Canvas()
    body = accent
    c.shape(rounded_rect_d(286, -270, 14, 154, 3), body, sw=2.4, light=(-2, 0))                   # front pillar
    c.shape(rounded_rect_d(366, -270, 12, 154, 3), body, sw=2.4, light=(-2, 0))                   # rear pillar
    c.line("M384,-250 V-130", 3, P.METAL_LIGHT)                                                  # the handrail
    c.shape(rounded_rect_d(286, -176, 92, 60, 4), body, sw=2.6, light=(-3, -3))                  # waist panel
    c.path(rounded_rect_d(296, -168, 72, 44, 3), "none", 2.2, P.GOLD)
    c.shape(rounded_rect_d(330, -110, 30, 6, 2), P.CHARCOAL, sw=1.6, light=None)                 # the step
    c.line("M336,-116 V-104 M354,-116 V-104", 2, P.CHARCOAL)
    return props._at(c, x, rail, k)


def _coach(x: float, rail: float, k: float, accent: str) -> str:
    """The first coach of the train behind the engine, running off the page: its end with the buffer, the
    body in the chapter's colour with a cream window band and lit windows, the roof, a bogie with two wheels.
    The origin is the coach's front buffer face at rail level."""
    c = Canvas()
    c.shape(rounded_rect_d(-10, -116, 14, 12, 2), P.METAL_DARK, sw=1.6, light=None)
    c.shape(rounded_rect_d(-14, -124, 8, 28, 3), P.METAL, sw=1.6, light=None)
    c.shape(rounded_rect_d(4, -132, 300, 18, 3), P.CHARCOAL, sw=2, light=None)
    for wx in (52, 110):
        _wheel(c, wx, 22, 0, darken(accent, 0.62))
    c.shape(rounded_rect_d(30, -64, 104, 16, 4), P.CHARCOAL, sw=1.8, light=None)                 # bogie frame
    c.shape(rounded_rect_d(4, -270, 300, 140, 8), accent, sw=2.6, light=(-3, -3))
    c.shape(rounded_rect_d(4, -250, 300, 54, 2), P.CREAM, sw=2, light=None)
    for wx in (16, 70, 124, 178):
        c.shape(rounded_rect_d(wx, -244, 42, 42, 6), P.YELLOW_PALE, sw=2, light=None)
        c.line(f"M{wx + 6},{-236} l10,-0 M{wx + 6},-236 v10", 1.6, P.WHITE)
    c.path(rounded_rect_d(4, -186, 300, 40, 2), "none", 1.8, P.GOLD)
    c.shape("M0,-268 Q150,-300 308,-268 V-262 H0 Z", P.METAL_DARK, sw=2.4, light=(0, -2))
    return props._at(c, x, rail, k)


def _track(c: Canvas, top: float, rail: float, bottom: float, accent: str) -> None:
    """The line in front of the platform: a bed of ballast stones packed close, the sleepers across it in
    perspective and the two steel rails on them; the near rail's top is at `rail`."""
    rnd = random.Random(17)
    base = mix(P.STONE, accent, 0.08)
    c.add(f'<rect x="-4" y="{n(top)}" width="{W + 8}" height="{n(bottom - top)}" fill="{darken(base, 0.62)}"/>')
    y = top + 3
    while y < bottom:
        x = -rnd.uniform(0, 10)
        while x < W + 8:
            w = rnd.uniform(8, 13)
            h = w * rnd.uniform(0.55, 0.75)
            tone = rnd.choice((base, lighten(base, 0.25), darken(base, 0.85)))
            c.add(f'<path d="M{n(x)},{n(y + h)} Q{n(x - 1)},{n(y)} {n(x + w * 0.5)},{n(y - 1)} '
                  f'Q{n(x + w + 1)},{n(y + 1)} {n(x + w)},{n(y + h)} Z" fill="{tone}" stroke="{INK}" '
                  f'stroke-width=".6" stroke-opacity=".45"/>')
            x += w + rnd.uniform(0.5, 2)
        y += 6.5
    far = rail - 16
    for sx in range(-20, W + 30, 36):
        c.shape(f"M{sx + 6},{far - 4} H{sx + 26} L{sx + 30},{rail + 12} H{sx + 2} Z", P.WOOD_DARK, sw=1.6, light=None)
    for ry, h in ((far - 3, 5), (rail - 1, 7)):
        c.shape(rounded_rect_d(-6, ry, W + 12, h, 1.5), P.METAL, sw=1.6, light=None)
        c.line(f"M-6,{n(ry + 1.4)} H{W + 6}", 1.2, P.METAL_PALE)


def _platform(c: Canvas, kerb: float, accent: str) -> None:
    """The station platform where everyone stands: the stone kerb along the edge, the yellow line not to be
    crossed and its tactile studs, then rows of paving slabs widening towards the reader."""
    stone = mix(P.BEIGE, accent, 0.1)
    c.add(f'<rect x="-4" y="{n(kerb)}" width="{W + 8}" height="{n(H - kerb + 4)}" fill="{darken(stone, 0.7)}"/>')
    c.shape(rounded_rect_d(-6, kerb, W + 12, 16, 2), P.METAL_PALE, sw=2.2, light=(0, -2))
    c.line(" ".join(f"M{x},{n(kerb + 2)} V{n(kerb + 15)}" for x in range(30, W, 96)), 1.2, INK, 0.4)
    stripe = kerb + 24
    c.shape(rounded_rect_d(-6, stripe, W + 12, 16, 1), P.YELLOW, sw=1.6, light=None)
    for x in range(6, W, 14):
        c.dot(x, stripe + 8, 2.2, darken(P.YELLOW, 0.8))
    y, row = stripe + 22, 0
    rnd = random.Random(23)
    while y < H:
        rh = 22 + row * 7
        x = -rnd.uniform(0, 60) - (row % 2) * 30
        while x < W:
            sw_ = 84 + row * 14
            tone = (stone, lighten(stone, 0.14), darken(stone, 0.95))[rnd.randrange(3)]
            c.add(f'<rect x="{n(x + 2)}" y="{n(y + 2)}" width="{n(sw_ - 4)}" height="{n(rh - 4)}" rx="3" fill="{tone}" '
                  f'stroke="{INK}" stroke-width=".9" stroke-opacity=".35"/>')
            x += sw_
        y += rh
        row += 1


def _bench(x: float, foot: float, k: float, accent: str) -> str:
    """A platform bench: two cast-iron ends in the chapter's colour, each with its arm rest and a curled foot,
    three wooden slats for the seat and two for the back. The origin is the middle of its feet; 140 wide, 84 tall."""
    c = Canvas()
    iron = darken(accent, 0.75)
    for back, slat in ((-84, -76), (-66, -58)):                                      # the back's slats
        c.shape(rounded_rect_d(-62, slat - 8 if back == -84 else back, 124, 9, 2), P.WOOD_LIGHT, sw=1.8, light=None)
    for sx in (-1, 1):
        c.path(f"M{sx * 58},0 Q{sx * 52},-12 {sx * 56},-36 L{sx * 60},-86 M{sx * 56},-36 Q{sx * 64},-44 {sx * 70},-48 "
               f"L{sx * 50},-50", "none", 5.4, INK)
        c.path(f"M{sx * 58},0 Q{sx * 52},-12 {sx * 56},-36 L{sx * 60},-86 M{sx * 56},-36 Q{sx * 64},-44 {sx * 70},-48 "
               f"L{sx * 50},-50", "none", 3, iron)
        c.shape(ellipse_d(sx * 62, -1, 9, 3.4), iron, sw=1.6, light=None)
    for dy in (-40, -34, -28):                                                      # the seat's slats
        c.shape(rounded_rect_d(-66, dy - 3, 132, 6, 2), P.WOOD if dy != -34 else P.WOOD_LIGHT, sw=1.4, light=None)
    return props._at(c, x, foot, k)


def _station_clock(x: float, foot: float, k: float, accent: str) -> str:
    """A station clock on a short post at the platform's end: the post on its base, the round case in the chapter's
    colour, the white face with twelve marks and the hands at four minutes past four. The origin is the foot."""
    c = Canvas()
    c.shape(rounded_rect_d(-14, -8, 28, 9, 2), P.METAL_DARK, sw=1.8, light=None)
    c.shape(rounded_rect_d(-5, -112, 10, 106, 2), darken(accent, 0.7), sw=2, light=(-1, 0))
    c.shape(rounded_rect_d(-10, -118, 20, 10, 2), darken(accent, 0.7), sw=1.8, light=None)
    cy = -146
    c.shape(ellipse_d(0, cy, 30, 30), accent, sw=2.4, light=(-2, -2))
    c.shape(ellipse_d(0, cy, 24, 24), P.WHITE, sw=1.8, light=None)
    c.line(" ".join(f"M{n(20 * math.sin(math.radians(a)))},{n(cy - 20 * math.cos(math.radians(a)))} "
                    f"L{n(23 * math.sin(math.radians(a)))},{n(cy - 23 * math.cos(math.radians(a)))}"
                    for a in range(0, 360, 30)), 1.6)
    hour, minute = math.radians(122), math.radians(24)                             # 4:04, the book's easter egg
    c.line(f"M0,{cy} L{n(12 * math.sin(hour))},{n(cy - 12 * math.cos(hour))}", 3.2)
    c.line(f"M0,{cy} L{n(19 * math.sin(minute))},{n(cy - 19 * math.cos(minute))}", 2)
    c.dot(0, cy, 2.6, P.RED)
    return props._at(c, x, foot, k)


def _emergency_post(x: float, foot: float, k: float, accent: str) -> str:
    """The emergency stop on the platform: a grey post on its base plate, a yellow box with black-and-yellow
    hazard stripes, and on its face the big red mushroom button in its collar. The origin is the foot; 130 tall."""
    c = Canvas()
    c.shape(rounded_rect_d(-16, -6, 32, 8, 2), P.METAL_DARK, sw=1.8, light=None)
    c.shape(rounded_rect_d(-6, -96, 12, 92, 2), P.METAL, sw=2, light=(-1, 0))
    c.shape(rounded_rect_d(-26, -134, 52, 48, 5), P.YELLOW, sw=2.4, light=(-2, -2))
    clip = c.shape(rounded_rect_d(-26, -98, 52, 12, 2), P.CHARCOAL, sw=0, light=None, clip=True)
    c.add(f'<g clip-path="url(#{clip})">')
    for sx in range(-34, 30, 12):
        c.add(f'<path d="M{sx},-86 l6,-12 h6 l-6,12 Z" fill="{P.YELLOW}"/>')
    c.add("</g>")
    c.path(rounded_rect_d(-26, -98, 52, 12, 2), "none", 1.8)
    c.shape(ellipse_d(0, -114, 13, 13), P.CHARCOAL, sw=1.8, light=None)
    c.shape("M-12,-114 Q-12,-128 0,-128 Q12,-128 12,-114 Q0,-108 -12,-114 Z", P.RED, sw=2, light=(-2, -2))
    c.line("M-6,-122 Q-2,-125 3,-124", 1.6, P.WHITE)
    return props._at(c, x, foot, k)


def railway(s, accent: str) -> object:
    """The railway: a request comes in and the agent brings it all the way to the station.

    One hero: a tank engine in the chapter's colour runs into the station pulling its train, the smoke rising from
    its chimney and blown back over the coaches, the rods at work, steam from the cylinder at its feet. The agent
    drives it, waving from the cab's step. By the line the colour-light signal shows green. On the platform in front
    the cat checks the arriving train against his clipboard, the caterpillar doubts, the sparrow sits on the
    emergency-stop post and eyes its big red button, a bench and a station clock at four minutes past four
    stand on the platform, and the professor explains under his bubble.
    """
    c = s.back
    horizon, rail, kerb = 790, 914, 958
    # the sky: deep at the top, warm and light near the hills; calm where the title stands
    paint = c.gradient([(0, darken(accent, 0.7)), (0.45, mix(accent, P.PINK_PALE, 0.35)),
                        (0.8, mix(P.PINK_PALE, P.SUN, 0.25)), (1, mix(P.YELLOW_PALE, P.PINK_PALE, 0.4))],
                       0, 0, 0, horizon)
    c.add(f'<rect x="-4" y="-4" width="{W + 8}" height="{horizon + 12}" fill="{paint}"/>')
    # the hills beyond the line, in the chapter's colour, and the green verge along it
    far, near = mix(accent, P.PINK_PALE, 0.55), mix(accent, P.GRASS_DARK, 0.45)
    c.shape(f"M-10,{horizon} L-10,{horizon - 70} Q140,{horizon - 120} 300,{horizon - 72} Q480,{horizon - 140} 660,"
            f"{horizon - 86} Q760,{horizon - 120} {W + 10},{horizon - 96} V{horizon} Z", far, sw=2, light=None)
    c.shape(f"M-10,{horizon + 20} L-10,{horizon - 30} Q180,{horizon - 64} 380,{horizon - 34} Q600,{horizon - 70} "
            f"{W + 10},{horizon - 40} V{horizon + 20} Z", near, sw=2, light=None)
    c.add(f'<rect x="-4" y="{horizon - 4}" width="{W + 8}" height="{rail - horizon}" '
          f'fill="{mix(P.GRASS_DARK, accent, 0.25)}"/>')
    _track(c, rail - 34, rail, kerb + 4, accent)

    # the low evening sun on the right and a few birds flying home on the left, under the title
    for r, a in ((96, 0.12), (70, 0.18)):
        c.add(f'<circle cx="736" cy="410" r="{r}" fill="{P.SUN}" opacity="{a}"/>')
    c.shape(ellipse_d(736, 410, 48, 48), mix(P.SUN, P.YELLOW_PALE, 0.4), sw=2.2, light=None)
    for bx, by, bk in ((236, 404, 1.0), (270, 388, 0.8), (298, 412, 0.7)):
        c.line(f"M{bx - 12 * bk},{by} q{6 * bk},{-8 * bk} {12 * bk},0 q{6 * bk},{-8 * bk} {12 * bk},0", 2.6)

    # --- the hero: the engine and the first coach, the smoke over them, steam at the cylinder
    lx, k = 316, 1.14
    _puffs(c, lx + 57 * k, rail - 280 * k, 470, 380, 14, 70, 34, 41, accent)
    _puffs(c, lx + 274 * k, rail - 254 * k, 46, 30, 5, 12, 6, 43, accent, start=0.75)      # the whistle blows
    s.put(rail, _coach(lx + 422 * k, rail, k, accent), (lx + 408 * k, rail - 290 * k, W, rail), "coach",
          group="train", backdrop=True)
    s.put(rail + 0.1, _locomotive(lx, rail, k, accent), [(lx - 24 * k, rail - 140 * k, lx + 412 * k, rail),
          (lx + 24 * k, rail - 304 * k, lx + 412 * k, rail - 140 * k)], "engine", group="train", backdrop=True)
    s.put(rail + 0.3, _cab_side(lx, rail, k, accent))
    # the agent, the driver, on the cab's step leaning out and waving to the platform
    s.actor("agent", lx + 346 * k, rail - 108 * k, "wave", "smile", tall=250 * k, group="train", depth=rail + 0.35)
    steam = Canvas()                                 # steam from the cylinder's drain cocks, low along the rails
    for dx, dy, r, a in ((112, -18, 10, 0.75), (92, -12, 13, 0.6), (64, -10, 16, 0.5), (36, -8, 15, 0.4)):
        _puff(steam, lx + dx * k, rail + dy, r, P.WHITE, a)
    s.put(rail + 0.4, steam.render())

    # --- the platform and the cast on it
    _platform(c, kerb, accent)
    s.keep_clear((-6, kerb, W + 6, kerb + 16))
    s.put(1116, _emergency_post(300, 1116, 1.0, accent), (274, 982, 326, 1116), "estop", group="estop")
    s.actor("sparrow", 304, 986, "point", "smile", flip=True, tall=120, group="estop", depth=1117)
    s.actor("caterpillar", 396, 1144, "think", "worry", tall=220, group="caterpillar")
    s.put(1070, _bench(518, 1070, 0.9, accent), (455, 990, 581, 1072), "bench")
    s.put(1086, _station_clock(782, 1086, 1.0, accent), (750, 938, 814, 1086), "clock")
    cat = s.actor("cat", 674, 1142, "point", "smile", flip=True, tall=230, group="cat")
    s.hold(cat, lambda x, y, kk: handheld.clipboard(x, y, kk), "left")

    # --- the professor under his bubble
    prof = s.actor("professor", 142, 1100, "explain", "talk", tall=380)
    s.speaker(prof, width=66, left=8, air=4)
    return s.render()


OPENERS = {
    "morning": morning,
    "fair": fair,
    "valley": valley,
    "house": house,
    "library": library,
    "proving": proving,
    "lab": lab,
    "crossing": crossing,
    "moonbase": moonbase,
    "forestcamp": forestcamp,
    "railway": railway,
}

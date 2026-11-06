"""The footer episodes: little stories, most of them after the plots of the printed original, retold with the
agent. Each is registered with `@episode(name)`; its topic words (what the page must talk about for it to be
chosen) and the lettering in its picture are under `footers: name:` in the locale.

An episode draws on a `Strip` (see `footers.py`): `s.outdoors()` / `s.indoors()` for the setting, `s.cast()` for
the characters at a fraction of the width, `s.thing()` for props on the ground, `s.held()` for something in a
character's hands, `s.scatter()` for small things. Everything with a box keeps clear of everything else.
"""
from __future__ import annotations

import math

from .. import design as P
from . import sets, things
from .characters import module
from .footers import Strip, episode
from .openers import strip_boxes
from .scenes import PROFESSOR_HEIGHT


# ============================================================================ prompts: said vaguely, done literally
@episode("potato")
def potato(s: Strip) -> None:
    """"Peel the potatoes!" The cat orders the agent to peel the potatoes; the agent, taking him at his word, polishes
    a potato with the cat's own spotted handkerchief until it shines. The caterpillar notes it all down, worried;
    the potatoes wait in the pail, the pot is on."""
    s.indoors()
    if s.h >= 170:
        y = s.base - s.tall * 0.95
        x = s.x(0.52)
        k = s.unit
        s.put(5, things.wall_shelf(x, y, k, 120), (x - 62 * k, y - 28 * k, x + 62 * k, y + 14 * k), "shelf")
    s.cast("cat", 0.08, "point", "talk", flip=False, mark="!")
    s.thing(lambda x, y, k: things.bucket(x, y, k), 0.28, 34, 48, nearer=0.4, name="pail")
    agent = s.cast("agent", 0.47, "type", "smile", flip=False, mark="ok", group="agent")
    s.held(agent, "type", False, lambda x, y, k: things.handkerchief(x, y + 4 * k, k * 1.35))
    s.thing(lambda x, y, k: things.stool(x, y, k) + things.pot(x, y - 40 * k, k * 0.9), 0.66, 46, 86, name="pot")
    s.cast("caterpillar", 0.88, "write", "worry", flip=True)


@episode("shopping_list")
def shopping_list(s: Strip) -> None:
    """"Buy boots and ears." The shopping list fell in the snow during a snowball fight, and what was left of
    it was bought to the letter: the sparrow shows off a pair of felt boots, the agent wears its new earmuffs, both
    very pleased; the caterpillar reads the smudged list and frowns. A snowman with a bucket for a hat looks on."""
    s.relook(season="winter")
    s.outdoors()
    k = s.unit
    s.thing(lambda x, y, k: things.snowman(x, y, k), 0.1, 76, 116, name="snowman")
    reader = s.cast("caterpillar", 0.32, "present", "worry", flip=False, mark="?", group="list")
    s.in_hand(reader, "present", False, lambda x, y, kk: things.smeared_list(x + 4 * kk, y + 14 * kk, kk * 0.75, 6))
    bird = s.cast("sparrow", 0.55, "present", "smile", flip=False, group="boots")
    hx, _ = s.hand(bird, "present", False)
    by = s.feet(hx, 0.15)
    s.put(by, things.felt_boots(hx + 14 * k, by, k * 0.95), (hx - 6 * k, by - 34 * k, hx + 34 * k, by), "boots")
    agent = s.cast("agent", 0.82, "cheer", "smile", flip=True, mark="ok", group="agent")
    _wear_earmuffs(s, agent, True)


def _wear_earmuffs(s: Strip, box, flip: bool) -> None:
    """Earmuffs on the agent's head: the muffs over its two ear bolts, the band over the top of its head."""
    mod = module("agent")
    kk = (box.bottom - box.top) / (mod.FEET_Y - mod.HEAD_TOP)
    cx = (box.left + box.right) / 2
    ears = [(cx + ((ex - mod.CENTER_X) * kk) * (-1 if flip else 1), box.bottom - (mod.FEET_Y - ey) * kk)
            for ex, ey in ((54, 80), (167, 78))]
    mx, my = (ears[0][0] + ears[1][0]) / 2, (ears[0][1] + ears[1][1]) / 2
    span = abs(ears[1][0] - ears[0][0])
    s.put(box.bottom + 0.5, things.earmuffs(mx, my, 1.0, span, (79 - 30) * kk), None, group=box.group)


# ============================================================================ permissions: "hands off"
@episode("time_machine")
def time_machine(s: Strip) -> None:
    """"Hands off." In the museum of computing the Time Machine stands behind a rope, a sign on its stand beside it;
    the sparrow did not touch it with his hands - he pulled the lever with his wing, and the burst says what came of
    it. The caterpillar is aghast, the agent has seen a rule kept to the letter and broken in spirit."""
    s.indoors()
    k = s.unit
    right = s.lo
    for key, frac, tall, name in (("abacus", 0.025, 82, "p1"), ("arithmometer", 0.145, 74, "p2")):
        label = s.word(key)
        width = things.pedestal_width(label, k) + 2
        px, _ = s.thing(lambda x, y, k, key=key, label=label: things.pedestal(x, y, k, key, label), frac, width, tall,
                        name=name)
        right = px + width * k / 2
    cat = s.cast("caterpillar", max(0.275, (right + s.tall * 0.24 - s.lo) / (s.hi - s.lo)), "cheer", "surprise",
                 flip=False)                                # beside the last pedestal, however wide its label
    text = s.word("no_touch")
    sw, sh = things.sign_size(text, k)
    sign_x = max(s.x(0.4), cat.right + (sw / 2 + 4) * k)
    s.thing(lambda x, y, k: things.sign_stand(x, y, k, text), (sign_x - s.lo) / (s.hi - s.lo), sw + 2, 42 + sh,
            nearer=0.3, name="sign")
    x, y = s.thing(lambda x, y, k: things.time_machine(x, y, k, lever_down=True), 0.59, 140, 113, name="machine")
    # the rope runs in front of the machine's feet, not across its face
    s.thing(lambda x, y, k: things.stanchion_sign(x, y, k, span=50), 0.59, 112, 38, nearer=0.55, group="machine")
    # the sparrow stands where his pointing wing is on the lever's knob
    kx = x + 66 * k
    fx, _ = _reach(s, "sparrow", "point", True, 0.95, kx + 2 * k)
    s.actor("sparrow", fx, y, "point", "worry", flip=True, tall=s.tall * 0.95, group="machine")
    if s.base > 120:
        r = min(34, s.base * 0.22)
        bx = x + 36 * k
        by = max(r + 4, y - 118 * k - r * 0.3)
        s.put(s.h + 5, things.burst(bx, by, r, s.word("bang")), (bx - r, by - r * 0.8, bx + r, by + r * 0.8), "machine")
    s.cast("agent", 0.86, "shrug", "surprise", flip=True)


def _reach(s: Strip, name: str, pose: str, flip: bool, size: float, hand_x: float,
           side: str = "right") -> tuple[float, float]:
    """Where to stand a character (its feet's x) so that its hand in this pose is at `hand_x`; also returns how
    high above the feet that hand is."""
    mod = module(name)
    kk = s.tall * size / PROFESSOR_HEIGHT * mod.SCENE_SCALE
    if hasattr(mod, "hand_point"):
        wx, wy = mod.hand_point(pose, side)
    else:
        wx, wy = mod.POSES[pose][-1 if side == "right" else -2][1]
    dx = (wx - mod.CENTER_X) * kk
    return (hand_x + dx if flip else hand_x - dx), (mod.FEET_Y - wy) * kk


# ============================================================================ a plan, followed step by step
@episode("tyapa")
def tyapa(s: Strip) -> None:
    """Tyapa's errand, after the robot dog the cat programmed: the agent carries a letter along the country path by
    a signboard with the program - 1 the well, 2 the broken pine, 3 the red fence with a plank missing. A snail
    brings up the rear."""
    s.outdoors()
    k, g = s.unit, s.ground
    # the path: from the horizon, winding forward under the agent's feet and out of the picture
    walk = s.x(0.52)
    route = [(s.x(0.68), s.base + 3), (s.x(0.6), s.base + g * 0.13), (walk, s.feet(walk) + g * 0.04),
             (s.x(0.43), s.base + g * 0.62), (s.x(0.47), s.h + 12)]
    sets.path_band(s.back, route, [4, g * 0.2, g * 0.42, g * 0.72, g * 1.15], seed=s.seed, soft=True)
    s.thing(lambda x, y, k: things.well(x, y, k), 0.035, 44, 64, name="well")
    # the snapped pine: its stump and, lying beside it, the top it lost - two boxes, so the sign may stand close
    px = s.x(0.13)
    py = s.feet(px)
    kp = k * 1.2                  # a tree: taller than the agent even with its top gone
    s.put(py - 1, things.broken_pine(px, py, kp), [(px - 24 * kp, py - 78 * kp, px + 24 * kp, py),
                                                   (px + 4 * kp, py - 46 * kp, px + 50 * kp, py),
                                                   (px + 50 * kp, py - 32 * kp, px + 92 * kp, py)], "pine")
    # the program on its signboard: the board up on its post
    title = s.word("program")
    post = 56 if k > 0.8 else 26          # in a low strip the board stands lower, under the sky's top fifth
    cw, ch = things.program_card_size(title, k, post)
    cx = s.x(0.36)
    cy = s.feet(cx)
    s.put(cy - 1, things.program_card(cx, cy, k, title, post=post),
          [(cx - cw * k / 2, cy - ch * k, cx + cw * k / 2, cy - post * k), (cx - 4 * k, cy - post * k, cx + 4 * k, cy)],
          "card")
    agent = s.cast("agent", 0.52, "carry", "smile", flip=False, group="agent")
    s.held(agent, "carry", False, lambda x, y, k: things.envelope(x, y + 6 * k, k * 1.0))
    sx, sy = s.x(0.45), s.base + g * 0.86
    s.put(sy, sets.snail(sx, sy, k * 0.8, mirror=True), (sx - 22 * k, sy - 26 * k, sx + 22 * k, sy), "snail")
    s.thing(lambda x, y, k: things.fence_with_hole(x, y, k, 120), 0.9, 124, 44, name="fence")


# ============================================================================ tokens cost money
@episode("checkout")
def checkout(s: Strip) -> None:
    """"100 purchases a minute." At the shop's till the agent scans everything that crosses the red cross; the
    receipt curls out of the till and runs along the floor right to the caterpillar's feet, the big total printed
    at its end. The sparrow flies off with a baguette."""
    s.indoors()
    if s.h >= 170:
        s.thing(lambda x, y, k: things.shop_shelf(x, y, k, s.seed), 0.08, 120, 120, name="shelf", backdrop=True)
    s.cast("agent", 0.28, "stand", "smile", flip=False, group="till", size=0.95)
    x, y = s.thing(lambda x, y, k: things.checkout(x, y, k), 0.34, 156, 80, nearer=0.5, name="till")
    k = s.unit
    reader = s.cast("caterpillar", 0.9, "present", "surprise", flip=True)
    width = max(10 * k, 7.0)
    floor = y + s.ground * 0.14
    ex = reader.left - 2
    # out of the till, a curl over, down to the floor and straight along it: the straight run carries the total
    points = [(x + 62 * k, y - 62 * k), (x + 80 * k, y - 76 * k), (x + 98 * k, y - 60 * k),
              (x + 102 * k, y - 26 * k), (x + 104 * k, floor - 2), (x + 128 * k, floor), (ex, floor)]
    s.put(floor + 2, things.receipt(points, width, s.word("total")), strip_boxes(points, width * 3), "till")
    bird = s.flight("sparrow", 0.58, 0.85)
    # the baguette carried in his feet, level, as birds carry a twig
    s.put(bird.bottom + 1, things.baguette((bird.left + bird.right) / 2, bird.bottom - 2, k * 0.9, turn=0), None,
          group=bird.group)


# ============================================================================ untrusted input
@episode("virus")
def virus(s: Strip) -> None:
    """The floppy from "somewhere": the sparrow brought a disk of games from somewhere, and the computer has
    caught a fever - an ice bag on its head, flushed cheeks, a thermometer, a spiky germ sweeping its screen. The
    caterpillar nurses it with a bottle of medicine; the professor holds up the culprit disk; the sparrow is very
    sorry."""
    s.indoors()
    s.thing(lambda x, y, k: things.kitchen_table(x, y, k, 100, P.WOOD_LIGHT, None), 0.42, 100, 50, name="desk",
            backdrop=True)
    tx = s.x(0.42)
    ty = s.feet(tx) - 48 * s.unit
    k = s.unit
    s.put(ty, things.sick_computer(tx, ty, k * 0.9), (tx - 44 * k, ty - 92 * k, tx + 44 * k, ty), "desk")
    nurse = s.cast("caterpillar", 0.66, "present", "worry", flip=True)
    s.in_hand(nurse, "present", True, lambda x, y, kk: things.medicine(x, y + 12 * kk, kk * 0.75))
    prof = s.cast("professor", 0.1, "present", "talk", flip=False)
    s.in_hand(prof, "present", False, lambda x, y, kk: things.floppy(x + 2 * kk, y + 6 * kk, kk * 0.55, P.RED, 12))
    s.cast("sparrow", 0.86, "shrug", "worry", flip=True, mark="!")


# ============================================================================ tokens: every symbol counts
@episode("beads")
def beads(s: Strip) -> None:
    """"How many cells?" The sparrow's poem is laid out on the floor letter by letter as coloured beads, a white
    one for every space; the caterpillar counts them with a giant pencil, the agent checks the sum, and the poet
    himself sulks on a toy block: poets need no bytes."""
    s.indoors()
    text = s.word("poem")
    k = s.unit
    r = max(8 * k, 9.0)      # a bead's letter is never smaller than the page's smallest lettering
    x0 = s.x(0.24)
    y = s.feet(x0, 0.75)
    width = len(text) * r * 2.2
    s.put(y, things.letter_beads(x0, y, text, r), (x0 - r, y - 2 * r, x0 + width, y), "beads")
    counter = s.cast("caterpillar", 0.1, "point", "talk", flip=False)
    # the giant pencil in her hand, its point resting on the first bead
    hx, hy = s.hand(counter, "point", False)
    tip = (x0 - r * 0.3, y - r * 2 - 1)
    reach = math.dist((hx, hy), tip)
    turn = math.degrees(math.atan2(tip[1] - hy, tip[0] - hx))
    s.in_hand(counter, "point", False,
              lambda x, y, kk: things.giant_pencil(x, y, kk * 0.9, reach / (kk * 0.9), turn))
    s.thing(lambda x, y, k: things.cube(x, y, k * 1.2, P.BLUE, s.word("block")), 0.76, 48, 50, name="cube")
    cx = s.x(0.76)
    top = s.feet(cx) - 44 * k
    s.actor("sparrow", cx, top, "shrug", "worry", flip=True, tall=s.tall * 0.9, group="cube")
    s.cast("agent", 0.92, "think", "smile", flip=True, mark="idea")

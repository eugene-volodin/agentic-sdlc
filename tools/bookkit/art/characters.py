"""Registry of the characters: the one entry point for every place that draws them.

A character is a module in this package. To add one, write the module and list it in `MODULES`;
nothing else in the code base needs to know its name. The module must define:

    SIZE          (width, height) of its canvas in drawing units
    FEET_Y        y of the ground line on that canvas
    BUST_BOX      square view box cropped to head and shoulders (round portrait frames)
    CENTER_X      x of the body axis, used to stand the figure on a spot
    HEAD_TOP      y of the crown, used to float a badge over the head
    PEEK_Y        y below which the figure is hidden when it looks over an edge
    SCENE_SCALE   canvas scale relative to the professor's so the cast stands in proportion
    HAND          color of the fingers when the character holds up a poster
    TALK_POSE     the full-figure pose used when the character speaks
    QUOTE_POSES   four poses a quote card cycles through
    RECAP_POSE    the pose in which the character presents a summary

Optional:

    VIEW_BOX          a wider view box when gestures reach outside the canvas
    PORTRAIT_OPTIONS  extra `draw` options for cropped views (the cat hides its tail)
    SEAT              "chair" or "desk": where the character sits in the study scene
    BALLOON_GRIP      {pose: (x, y)} where a balloon string ends, for characters that carry one
    POSES         mapping of pose name to whatever the module's rig needs
    draw(pose, mood, **options) -> Canvas
    hands(pose, grips=()) -> {"left": HandFrame, "right": HandFrame}, with `draw(..., grips=(sides))` closing
                  those hands into fists: a character that has them can hold things (`draw(..., hold=...)`)

The localized display name, the role line and extra spellings come from `locale/<lang>.yml`.
"""
from __future__ import annotations

import inspect
from types import ModuleType

from . import agent, cat, caterpillar, professor, sparrow
from .ink import Canvas, svg, uid
from .rig import hold as _hold

MODULES: dict[str, ModuleType] = {
    "professor": professor,
    "cat": cat,
    "caterpillar": caterpillar,
    "sparrow": sparrow,
    "agent": agent,
}
MOODS = ("smile", "talk", "worry", "surprise", "wink")
MARKS = ("?", "!", "ok", "idea")   # badges that can float over a head in a scene

# Extra spellings accepted in content files; filled from the locale at build time.
_aliases: dict[str, str] = {name: name for name in MODULES}


class UnknownCharacter(KeyError):
    """Raised when content refers to a character, pose or mood that does not exist."""

    def __str__(self) -> str:   # KeyError would wrap the message in quotes
        return str(self.args[0]) if self.args else ""


def register_aliases(aliases: dict[str, str]) -> None:
    """Accept additional names (for example localized ones) for the characters."""
    for alias, name in aliases.items():
        if name in MODULES:
            _aliases[alias.lower()] = name


def is_character(name: str) -> bool:
    return name.strip().lower() in _aliases


def resolve(name: str) -> str:
    """Map any accepted spelling to the canonical character key."""
    key = _aliases.get(str(name).strip().lower())
    if not key:
        raise UnknownCharacter(f"unknown character {name!r}; available: {', '.join(MODULES)}")
    return key


def module(name: str) -> ModuleType:
    """The drawing module of a character, by any accepted spelling."""
    return MODULES[resolve(name)]


def check(name: str, pose: str | None = None, mood: str | None = None) -> None:
    """Raise `UnknownCharacter` unless the character has that pose and the mood exists."""
    mod = module(name)
    if pose is not None and pose not in mod.POSES:
        raise UnknownCharacter(f"{resolve(name)} has no pose {pose!r}; available: {', '.join(mod.POSES)}")
    if mood is not None and mood not in MOODS:
        raise UnknownCharacter(f"unknown mood {mood!r}; available: {', '.join(MOODS)}")


def draw(name: str, pose: str | None = None, mood: str = "smile", hold: dict | None = None, **options) -> Canvas:
    """Draw a character on its own canvas (used when composing scenes).

    `hold` puts things into its hands: {"right": make} or {"right": (make, turn)}, "right" being the arm listed
    last in the module's poses. The hand closes into a fist round the thing - its back, the thing, the fingers
    over it - and the thing turns with the forearm (see `rig`); `make(x, y, k)` draws it with its grip at (x, y),
    `k` being the holder's height over 100, as the makers in `handheld.py` do."""
    pose = pose or "stand"
    check(name, pose, mood)
    mod = module(name)
    if not hold:
        return mod.draw(pose=pose, mood=mood, **options)
    if not hasattr(mod, "hands"):
        raise UnknownCharacter(f"{resolve(name)} has no hands to hold things in")
    spec = {side: value if isinstance(value, tuple) else (value, 0.0) for side, value in hold.items()}
    wrong = [side for side in spec if side not in ("left", "right")]
    if wrong:
        raise UnknownCharacter(f"a thing is held in the left or the right hand, not {wrong[0]!r}")
    palms = tuple(side for side, (make, _) in spec.items() if getattr(make, "grasp", "fist") == "palm")
    if palms and "palms" in inspect.signature(mod.draw).parameters:
        options = {**options, "palms": palms}    # hands that cradle a thing (the cat then takes off his watch)
    c = mod.draw(pose=pose, mood=mood, grips=tuple(spec), **options)
    frames = mod.hands(pose, tuple(spec))
    k = (mod.FEET_Y - mod.HEAD_TOP) / 100
    for side, (make, turn) in spec.items():
        _hold(c, frames[side], mod.HAND, make, k, turn)
    return c


def figure(name: str, pose: str | None = None, mood: str = "smile", bust: bool = False,
           flip: bool = False, css_class: str = "", view_box: str | None = None, medal: bool = False,
           **options) -> str:
    """Return a complete `<svg>` of a character.

    `bust` crops to head and shoulders. `flip` mirrors the drawing so the
    character faces left. `view_box` overrides the crop entirely. `medal` lays the round frame's lit backdrop
    inside the drawing: as a CSS background of a rounded box Chrome prints it as a raster, which Apple's PDF
    viewers draw torn.
    """
    name = resolve(name)
    mod = MODULES[name]
    box = view_box or (mod.BUST_BOX if bust else getattr(mod, "VIEW_BOX", None))
    if bust or view_box:
        options = {**getattr(mod, "PORTRAIT_OPTIONS", {}), **options}
    cls = f"char char-{name} {css_class}".strip()
    body = draw(name, pose, mood, **options).render()
    if medal:
        x, y, w, h = (float(v) for v in (box or f"0 0 {mod.SIZE[0]} {mod.SIZE[1]}").split())
        gid = uid("medal")
        body = (f'<radialGradient id="{gid}" cx=".35" cy=".3" r=".96"><stop offset="0" style="stop-color: '
                f'var(--white)"/><stop offset="1" style="stop-color: var(--accent-soft)"/></radialGradient>'
                f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="url(#{gid})"/>{body}')
    return svg(body, *mod.SIZE, css_class=cls, view_box=box, flip=flip)


def peek(name: str, mood: str = "smile", flip: bool = False) -> str:
    """A character looking over an edge: eyes and nose above it, everything below `PEEK_Y` hidden."""
    mod = module(name)
    x, y, w, _ = (float(v) for v in mod.BUST_BOX.split())
    return figure(name, "stand", mood, flip=flip, view_box=f"{x:g} {y:g} {w:g} {mod.PEEK_Y - y:g}")

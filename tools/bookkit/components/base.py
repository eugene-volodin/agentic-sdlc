"""The component library: how blocks are declared, validated and rendered.

A *component* is one visual building block of the book. There are two kinds:

* a **block** is written as `::: name [character] [flags] [key=value] [Title]` ... `:::`
* a **fence** is a code fence whose language selects it: ```` ```prompt title="..." ````

Each component is a plain function registered with `@block(...)` or `@fence(...)`. The decorator
records everything the engine needs to know about it - which character it may take, which
options it understands and of what type, whether it can span the full width - so that

* the author's input is validated in one place, with one style of error message;
* the function receives clean, typed values and only has to build HTML;
* `uv run book components` can print the whole library as a reference.

Adding a component
------------------
1. Write the function in the module of its family (`speech.py`, `callouts.py`, `lists.py`,
   `layout.py`, `people.py`, `code.py`, `chat.py`) and decorate it. Its docstring's first line is its description.
2. Return a `Row` (or a list of rows, or `None`). Put the HTML in `Row.main`; use
   `ctx.blocks(text)` / `ctx.inline(text)` to render the author's Markdown.
3. Style it in the family's sheet in `theme/css/` using design tokens only, and show it in the demo chapter.

The function signature is `render(ctx: Context, call: Call) -> Row | list[Row] | None`.
"""
from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field

from ..art.characters import MODULES, MOODS, UnknownCharacter, check, resolve
from ..markup import BuildError, parse_head


# ============================================================================ output
@dataclass
class Row:
    """One block of the page flow: main-column content plus optional margin content.

    The paginator moves whole rows between pages; a row whose main content contains an
    element with the `data-split` attribute may also be split between that element's children.
    """

    main: str
    side: str = ""
    wide: bool = False      # spans the text column and the margin
    heading: str = ""       # "h1", "h2" or "h3" for heading rows: they stay with what follows
    raw: bool = False       # emit `main` as is (control markers such as page breaks)
    stretch: bool = False   # may be widened by the compiler to vary the rhythm of the page

    @property
    def has_margin(self) -> bool:
        """Whether margin notes can be attached beside this row."""
        return not (self.raw or self.wide or self.heading)

    def html(self) -> str:
        if self.raw:
            return self.main
        classes = ["row"] + (["wide"] if self.wide else []) + (["row-heading", self.heading] if self.heading else [])
        return (f'<div class="{" ".join(classes)}"><div class="main">{self.main}</div>'
                f'<div class="side">{self.side}</div></div>')


# ============================================================================ option types
class Option:
    """Base class of option types. `parse` turns the author's text into a value or raises `ValueError`."""

    describe = "text"

    def parse(self, raw: str) -> object:
        return raw


class Text(Option):
    """Free text, e.g. a title or a label."""


class Flag(Option):
    """A bare word that switches something on: `right`, `numbered`."""

    describe = "flag"


@dataclass(frozen=True)
class Choice(Option):
    """One of a fixed set of words."""

    values: tuple[str, ...]

    @property
    def describe(self) -> str:  # type: ignore[override]
        return " | ".join(self.values)

    def parse(self, raw: str) -> str:
        if raw not in self.values:
            raise ValueError(f"must be one of: {', '.join(self.values)}")
        return raw


@dataclass(frozen=True)
class Number(Option):
    """A number within bounds; `integer=True` rejects fractions."""

    low: float
    high: float
    integer: bool = False

    @property
    def describe(self) -> str:  # type: ignore[override]
        return f"{'integer' if self.integer else 'number'} {self.low:g}..{self.high:g}"

    def parse(self, raw: str) -> float | int:
        try:
            value = int(raw) if self.integer else float(raw)
        except ValueError:
            raise ValueError(f"must be {'a whole number' if self.integer else 'a number'}") from None
        if not self.low <= value <= self.high:
            raise ValueError(f"must be between {self.low:g} and {self.high:g}")
        return value


class Character(Option):
    """The name of a character, in any accepted spelling."""

    describe = " | ".join(MODULES)

    def parse(self, raw: str) -> str:
        return resolve(raw)


# Shared option instances, so every component spells them the same way.
POSE = Text()          # checked against the chosen character when the figure is drawn
MOOD = Choice(MOODS)
FLAG = Flag()
TEXT = Text()

# Values for the `who` parameter of a component.
NO_CHARACTER = None            # the component does not take a character
ANY_CHARACTER = "*"            # a character may be named; there is no default
ROTATE_CHARACTERS = "~"        # when none is named, the cast takes turns


# ============================================================================ input
@dataclass
class Call:
    """One use of a component, after validation."""

    who: str | None                 # canonical character key, or None
    options: dict                   # typed values; flags are True when present
    title: str                      # the free text after the options
    body: str                       # block body or fence content
    language: str = ""              # fences only: the language word

    def flag(self, name: str) -> bool:
        return bool(self.options.get(name))

    def get(self, name: str, default=None):
        return self.options.get(name, default)


@dataclass(frozen=True)
class Spec:
    """Everything the engine knows about a component."""

    name: str
    kind: str                                   # "block" or "fence"
    render: Callable
    who: str | None = NO_CHARACTER
    options: dict[str, Option] = field(default_factory=dict)
    wide: str = "optional"                      # optional | default | always | never
    stretch: bool = False                       # the layout may widen it on its own (see Compiler._emit)
    titled: bool = False                        # takes free text after its options (a title, a term, a name)
    body: str = "required"                      # required | optional | none
    example: str = ""

    @property
    def summary(self) -> str:
        return (self.render.__doc__ or "").strip().split("\n")[0]

    @property
    def flags(self) -> frozenset[str]:
        return frozenset(name for name, option in self.all_options.items() if isinstance(option, Flag))

    @property
    def all_options(self) -> dict[str, Option]:
        """Declared options plus the width switch the `wide` policy implies."""
        extra = {"optional": {"wide": FLAG}, "default": {"narrow": FLAG}}.get(self.wide, {})
        if self.stretch:
            extra = {**extra, "narrow": FLAG}   # lets the author keep a stretchable block in the column
        return {**self.options, **extra}

    def default_who(self, turn: int) -> str | None:
        if self.who == ROTATE_CHARACTERS:
            return list(MODULES)[turn % len(MODULES)]
        return None if self.who in (NO_CHARACTER, ANY_CHARACTER) else self.who


BLOCKS: dict[str, Spec] = {}
FENCES: dict[str, Spec] = {}
DEFAULT_FENCE = "code"   # the fence used for any language without a component of its own


def _register(table: dict[str, Spec], kind: str, names: tuple[str, ...], **settings):
    def decorate(function: Callable) -> Callable:
        if not (function.__doc__ or "").strip():
            raise TypeError(f"component {names[0]!r} needs a docstring: it is its reference entry")
        spec = Spec(name=names[0], kind=kind, render=function, **settings)
        if spec.wide not in ("optional", "default", "always", "never"):
            raise ValueError(f"component {spec.name!r}: unknown wide policy {spec.wide!r}")
        if spec.body not in ("required", "optional", "none"):
            raise ValueError(f"component {spec.name!r}: unknown body policy {spec.body!r}")
        for name in names:
            if name in table:
                raise ValueError(f"{kind} {name!r} is registered twice")
            table[name] = spec
        return function
    return decorate


def block(*names: str, who: str | None = NO_CHARACTER, options: dict[str, Option] | None = None,
          wide: str = "optional", stretch: bool = False, titled: bool = False, body: str = "required",
          example: str = ""):
    """Register a `::: name` block. Extra names are aliases.

    `stretch` marks a boxed block that looks equally good in the column and across the full
    width; the compiler widens some of them so a page is not one unbroken narrow strip.
    """
    return _register(BLOCKS, "block", names, who=who, options=options or {}, wide=wide, stretch=stretch,
                     titled=titled, body=body, example=example)


def fence(*names: str, who: str | None = NO_CHARACTER, options: dict[str, Option] | None = None,
          wide: str = "optional", example: str = ""):
    """Register a code fence selected by its language word. Extra names are aliases."""
    return _register(FENCES, "fence", names, who=who, options=options or {}, wide=wide, example=example)


# ============================================================================ dispatch
def _validate(spec: Spec, text: str, body: str, turn: int, language: str = "") -> Call:
    label = f"'::: {spec.name}'" if spec.kind == "block" else f"'```{language or spec.name}'"
    head = parse_head(text, flags=spec.flags, allow_who=spec.who is not NO_CHARACTER)
    accepted = spec.all_options
    late = [key for key in re.findall(r"(?:^|\s)([a-z_]+)=", head.title) if key in accepted]
    if late:
        raise BuildError(f"{label}: options go before the title, but {', '.join(late)} came after "
                         f"{head.title.split()[0]!r}")
    if head.title and not spec.titled:
        word = head.title.split()[0]
        hint = (f"; {word!r} is not a character: {', '.join(MODULES)}" if spec.who is not NO_CHARACTER
                and re.fullmatch(r"[a-z]+", word) else "")
        raise BuildError(f"{label} takes no title, but got {head.title!r}{hint}")
    unknown = sorted(set(head.options) - set(accepted))
    if unknown:
        raise BuildError(f"{label} does not accept: {', '.join(unknown)}; "
                         f"it accepts: {', '.join(sorted(accepted)) or 'no options'}")
    options = {}
    for name, raw in head.options.items():
        option = accepted[name]
        if isinstance(option, Flag):
            if raw is not True:
                raise BuildError(f"{label}: '{name}' is a flag, write it without a value")
            options[name] = True
            continue
        if raw is True:
            raise BuildError(f"{label}: '{name}' needs a value, e.g. {name}=...")
        try:
            options[name] = option.parse(raw)
        except (ValueError, UnknownCharacter) as error:
            raise BuildError(f"{label}: {name}={raw!r} {error}") from None
    if spec.body == "required" and not body.strip():
        raise BuildError(f"{label} is empty: write its text between the opening and the closing line")
    if spec.body == "none" and body.strip():
        raise BuildError(f"{label} takes no text, but has {body.strip()[:40]!r}")
    who = head.who or spec.default_who(turn)
    if who and "pose" in options:
        check(who, pose=options["pose"])      # fail here, with the block named, not deep in the drawing code
    if "pose" in options and not who:
        raise BuildError(f"{label}: pose={options['pose']!r} needs a character to strike it")
    return Call(who=who, options=options, title=head.title, body=body, language=language)


def _finish(spec: Spec, call: Call, result) -> list[Row]:
    rows = [result] if isinstance(result, Row) else list(result or [])
    wide = (spec.wide == "always" or (spec.wide == "optional" and call.flag("wide"))
            or (spec.wide == "default" and not call.flag("narrow")))
    if wide:
        for row in rows:
            row.wide = True
    elif spec.stretch and not call.flag("narrow"):
        for row in rows:
            row.stretch = True
    return rows


def render_block(ctx, head_text: str, body: str) -> list[Row]:
    """Render one `:::` block from the text after the colons and its body."""
    name, _, rest = head_text.partition(" ")
    spec = BLOCKS.get(name.lower())
    if spec is None:
        raise BuildError(f"unknown block '::: {name}'; available: {', '.join(sorted(BLOCKS))}")
    call = _validate(spec, rest, body, ctx.take_turn(spec.name))
    return _finish(spec, call, spec.render(ctx, call))


def render_fence(ctx, info: str, code: str) -> Row:
    """Render a code fence from its info string and content."""
    language, _, rest = info.strip().partition(" ")
    spec = FENCES.get(language) or FENCES[DEFAULT_FENCE]
    call = _validate(spec, rest, code, ctx.take_turn(spec.name), language=language)
    return _finish(spec, call, spec.render(ctx, call))[0]


def reference() -> str:
    """A plain-text listing of every component, generated from the registry."""
    lines = []
    for title, table in (("BLOCKS   ::: name [character] [options] [Title]", BLOCKS),
                         ("FENCES   ```name [options]", FENCES)):
        lines += [title, "=" * len(title)]
        for name, spec in table.items():
            if name != spec.name:
                continue   # aliases are listed with their component
            aliases = [alias for alias, other in table.items() if other is spec and alias != name]
            lines.append(f"\n{name}" + (f"  (also: {', '.join(aliases)})" if aliases else ""))
            lines.append(f"    {spec.summary}")
            if spec.who == ROTATE_CHARACTERS:
                lines.append("    character: optional; the cast takes turns")
            elif spec.who == ANY_CHARACTER:
                lines.append("    character: optional")
            elif spec.who:
                lines.append(f"    character: optional, default {spec.who}")
            for option, kind in sorted(spec.all_options.items()):
                lines.append(f"    {option:<10} {kind.describe}")
            if spec.example:
                lines += ["    example:"] + [f"        {line}" for line in spec.example.strip("\n").split("\n")]
        lines.append("")
    return "\n".join(lines)

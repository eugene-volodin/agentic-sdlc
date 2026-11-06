"""Components in which the characters talk: speech bubbles, dialogues, quotes, margin notes."""
from __future__ import annotations

import re

from ..art.characters import MOODS, figure, is_character, module, resolve
from ..markup import BuildError
from .base import ANY_CHARACTER, FLAG, MOOD, POSE, ROTATE_CHARACTERS, Call, Row, block
from .context import Context
from .graphics import TAIL

# Where the character of a quote stands when the author does not choose: on the left, then on the right.
QUOTE_SIDES = (False, True)


def speech_row(ctx: Context, who: str, content: str, *, pose: str | None = None, mood: str = "talk",
               right: bool = False, full: bool = False, big: bool = False, cloud: bool = False,
               compact: bool = False) -> Row:
    """A character with a speech bubble.

    Without a pose the character is a head-and-shoulders portrait (a round medallion);
    with one, or with `full`, the whole figure is drawn. On the right the figure is mirrored
    so it always faces its own words.
    """
    full = full or bool(pose)
    pose = pose or (module(who).TALK_POSE if full else "stand")
    portrait = figure(who, pose, mood, bust=not full, flip=right, medal=not full)
    classes = ["say"] + [name for name, on in (("say-right", right), ("big", big), ("compact", compact)) if on]
    return Row(f'<div class="{" ".join(classes)}"><div class="say-who{" full" if full else ""}">{portrait}</div>'
               f'<div class="bubble{" cloud" if cloud else ""}">{content}{TAIL}</div></div>')


@block("say", who="professor",
       options={"pose": POSE, "mood": MOOD, "right": FLAG, "left": FLAG, "full": FLAG, "big": FLAG, "cloud": FLAG},
       example="::: say cat right pose=think mood=worry\nWhat if I do not know which rule to write?\n:::")
def say(ctx: Context, call: Call) -> Row:
    """A character says something in a speech bubble."""
    return speech_row(ctx, call.who, ctx.framed(call.body), pose=call.get("pose"), mood=call.get("mood", "talk"),
                      right=call.flag("right"), full=call.flag("full"), big=call.flag("big"),
                      cloud=call.flag("cloud"))


@block("dialog", wide="never",
       example="::: dialog\nprofessor: Meet the Agent.\nagent (wave): Hello!\ncat (think, worry): Hmm.\n:::")
def dialog(ctx: Context, call: Call) -> list[Row]:
    """A conversation: every line starts with `name:` or `name (pose, mood):`.

    Speakers take sides in order of appearance, so two characters face each other.
    Lines that do not start with a name continue the previous speaker's bubble.
    """
    turns: list[tuple[str, dict, list[str]]] = []
    for line in call.body.strip("\n").split("\n"):
        match = re.match(r"^\s*([\w-]+)\s*(?:\(([^)]*)\))?\s*:\s*(.*)$", line)
        if match and is_character(match.group(1)):
            who, settings = resolve(match.group(1)), {}
            for word in filter(None, (w.strip() for w in (match.group(2) or "").split(","))):
                if word in MOODS:
                    settings["mood"] = word
                elif word in module(who).POSES:
                    settings["pose"] = word
                else:
                    raise BuildError(f"dialog: {who} has no pose or mood {word!r}")
            turns.append((who, settings, [match.group(3)]))
        elif turns:
            turns[-1][2].append(line)
        elif line.strip():
            raise BuildError("dialog lines must start with a character name and a colon, e.g. 'cat: Hello'")
    if not turns:
        raise BuildError("dialog is empty")
    sides: dict[str, bool] = {}
    rows = []
    for who, settings, lines in turns:
        sides.setdefault(who, len(sides) % 2 == 1)
        rows.append(speech_row(ctx, who, ctx.framed("\n".join(lines)), right=sides[who], compact=True, **settings))
    return rows


@block("note", who=ANY_CHARACTER, options={"pose": POSE, "mood": MOOD}, wide="never",
       example="::: note sparrow\nA symlink is a shortcut.\n:::")
def note(ctx: Context, call: Call) -> None:
    """A margin note beside the next block: handwritten, or a small bubble if a character is named."""
    content = ctx.blocks(call.body)
    if call.who:
        ctx.queue_margin(ctx.margin_talk(call.who, content, call.get("pose"), call.get("mood", "talk")))
    else:
        ctx.queue_margin(ctx.margin_note(content))


@block("quote", titled=True, who=ROTATE_CHARACTERS, stretch=True,
       options={"pose": POSE, "mood": MOOD, "right": FLAG, "left": FLAG},
       example="::: quote sparrow left pose=shrug Attribution\nI pick everything up on the fly.\n:::")
def quote(ctx: Context, call: Call) -> Row:
    """A quotation on a card, with a character standing inside it at one end, as tall as the card.

    Without options the character, its side and its pose change from one quote to the next.
    The title is the attribution; it defaults to the character's name.
    """
    turn = ctx.take_turn("quote-layout")
    right = QUOTE_SIDES[turn % len(QUOTE_SIDES)]
    if call.flag("right") or call.flag("left"):
        right = call.flag("right")
    poses = module(call.who).QUOTE_POSES
    portrait = figure(call.who, call.get("pose") or poses[turn % len(poses)], call.get("mood", "talk"), flip=right)
    cite = ctx.inline(call.title) if call.title else ctx.character_name(call.who)
    css = "quote-card" + (" q-right" if right else "")
    return Row(f'<div class="{css}"><div class="q-who">{portrait}</div>'
               f"<blockquote>{ctx.blocks(call.body)}<cite>{cite}</cite></blockquote></div>")

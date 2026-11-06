"""Components that set a piece of text apart: callouts, definitions, summaries, comparisons."""
from __future__ import annotations

import re

from ..art.characters import figure, module
from ..markup import BuildError
from .base import MOOD, Call, Character, Number, Row, block
from .context import Context
from .graphics import MARK_CROSS, MARK_TICK, burst

# kind -> the symbol inside the starburst; the default titles come from the locale (`callouts:`).
CALLOUT_SYMBOLS = {"tip": "✓", "warn": "!", "idea": "✦", "try": "?"}


def _callout(kind: str):
    def render(ctx: Context, call: Call) -> Row:
        title = ctx.inline(call.title) if call.title else ctx.label_callout(kind)
        return Row(f'<div class="callout callout-{kind}">{burst(CALLOUT_SYMBOLS[kind])}'
                   f'<div class="callout-body"><b class="callout-title">{title}</b>{ctx.framed(call.body)}</div></div>')
    return render


for _kind, _text in (("tip", "Advice worth following (green)."), ("warn", "A warning (yellow)."),
                     ("idea", "An idea or a piece of background (teal)."),
                     ("try", "An exercise for the reader (pink).")):
    _render = _callout(_kind)
    _render.__doc__ = f"{_text} The title replaces the default heading."
    block(_kind, stretch=True, titled=True, example=f"::: {_kind}\nThe text of the callout.\n:::")(_render)


@block("define", titled=True, stretch=True, options={"perch": Character(), "peek": Character()},
       example="::: define Skill\na folder with instructions.\n:::")
def define(ctx: Context, call: Call) -> Row:
    """A definition on a scroll; the title is the term being defined."""
    if not call.title:
        raise BuildError("'define' needs the term as its title, e.g. '::: define Skill'")
    percher = figure(call.get("perch", "sparrow"), "cheer", "smile")
    peeker = figure(call.get("peek", "caterpillar"), "think", "smile", bust=True, flip=True)
    return Row(f'<div class="scroll"><div class="scroll-perch">{percher}</div><div class="scroll-sheet">'
               f'<i class="scroll-paper"></i>'
               f'<span class="scroll-text"><b class="scroll-term">{ctx.inline(call.title)}</b> — '
               f'{ctx.framed(call.body)}</span></div><div class="scroll-peek">{peeker}</div></div>')


@block("stat", titled=True, wide="never", example="::: stat 3 files\nare enough to start.\n:::")
def stat(ctx: Context, call: Call) -> None:
    """One big number or word with a line of explanation, in the margin beside the next block.

    A figure is a side remark, not a block of the text: it stands among the margin notes.
    """
    if not call.title:
        raise BuildError("'stat' needs the big text as its title, e.g. '::: stat 3 files'")
    ctx.queue_margin(f'<div class="stat"><div class="stat-big">{ctx.inline(call.title)}</div>'
                     f'<div class="stat-text">{ctx.framed(call.body)}</div></div>')


@block("recap", titled=True, who="caterpillar", options={"mood": MOOD}, stretch=True,
       example="::: recap\n- A hook fires on its own.\n- Project rules live in `AGENTS.md`.\n:::")
def recap(ctx: Context, call: Call) -> Row:
    """A summary on a notebook page, with the character who wrote it down."""
    writer = figure(call.who, module(call.who).RECAP_POSE, call.get("mood", "smile"), flip=True)
    title = ctx.inline(call.title) if call.title else ctx.label("recap")
    return Row(f'<div class="recap"><div class="recap-holes">{"<i></i>" * 7}</div>'
               f'<div class="recap-who">{writer}</div><h4>{title}</h4>'
               f'<div class="recap-body">{ctx.framed(call.body)}</div></div>')


@block("dodont", wide="default", example="::: dodont\n- Make it nice.\n+ Add a test and run `pytest`.\n:::")
def dodont(ctx: Context, call: Call) -> Row:
    """Two columns of examples: lines starting with `-` are bad, lines starting with `+` are good."""
    columns: dict[str, list[str]] = {"-": [], "+": []}
    current = None
    for line in call.body.strip("\n").split("\n"):
        match = re.match(r"^\s*([+-])\s+(.*)$", line)
        if match:
            current = columns[match.group(1)]
            current.append(match.group(2))
        elif current and line.strip():
            current[-1] += " " + line.strip()
    if not columns["-"] or not columns["+"]:
        raise BuildError("'dodont' needs at least one line starting with '-' and one starting with '+'")
    parts = []
    for sign, kind, symbol in (("-", "dont", MARK_CROSS), ("+", "do", MARK_TICK)):
        items = "".join(f"<li>{symbol}{ctx.inline(text)}</li>" for text in columns[sign])
        parts.append(f'<div class="dd dd-{kind}"><h4><i>{symbol}</i>{ctx.label(kind)}</h4><ul>{items}</ul></div>')
    return Row(f'<div class="dodont">{"".join(parts)}</div>')


@block("compare", wide="default", options={"cols": Number(1, 4, integer=True)},
       example="::: compare\n### Hook\nFires on its own.\n### Command\nYou call it.\n:::")
def compare(ctx: Context, call: Call) -> Row:
    """Side-by-side cards; each `### Heading` inside starts a card."""
    parts = re.split(r"^#{2,4}\s+(.+)$", call.body.strip("\n"), flags=re.M)
    cards = [f'<div class="card"><h4>{ctx.inline(parts[i].strip())}</h4>'
             f'<div class="card-body">{ctx.framed(parts[i + 1])}</div></div>' for i in range(1, len(parts), 2)]
    if not cards:
        raise BuildError("'compare' needs at least one '### Heading' to start a card")
    columns = call.get("cols", min(len(cards), 4))
    return Row(f'<div class="cards" style="--n:{columns}">{"".join(cards)}</div>')

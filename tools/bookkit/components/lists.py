"""Components built around lists: checklists, numbered steps, the cast of characters."""
from __future__ import annotations

import re
from html import escape

from ..art.characters import MODULES, figure, module, peek
from ..markup import BuildError
from .base import FLAG, MOOD, Call, Row, block
from .context import Context
from .graphics import CHECK, grip


@block("checklist", titled=True, who="professor", options={"right": FLAG, "numbered": FLAG, "mood": MOOD},
       example="::: checklist cat right Before you start\n- [x] The repository is open\n"
               "- [ ] Tests run with one command\n:::")
def checklist(ctx: Context, call: Call) -> Row:
    """A poster held up by a character who looks over its top edge.

    Items are `- [x] done` / `- [ ] open`; with `numbered` they get numbers instead of boxes.
    """
    items: list[list] = []
    for line in call.body.strip("\n").split("\n"):
        match = re.match(r"^\s*(?:[-*]|\d+[.)])\s+(?:\[( |x|X)\]\s+)?(.*)$", line)
        if match:
            items.append([match.group(1) in ("x", "X"), match.group(2)])
        elif items and line.strip():
            items[-1][1] += " " + line.strip()
    if not items:
        raise BuildError("'checklist' needs list items, e.g. '- [ ] item'")
    entries = []
    for number, (done, text) in enumerate(items, 1):
        mark = (f'<span class="num">{number}</span>' if call.flag("numbered")
                else f'<span class="box">{CHECK if done else ""}</span>')
        entries.append(f"<li>{mark}<div>{ctx.inline(text)}</div></li>")
    right = call.flag("right")
    mod = module(call.who)
    title = f"<h4>{ctx.inline(call.title)}</h4>" if call.title else ""
    hold_y = getattr(mod, "HOLD_Y", None)
    if hold_y:
        # The character stands behind the poster, torso up; only the hands that grip its top edge come out in front.
        x, _, w, _ = (float(v) for v in (getattr(mod, "VIEW_BOX", None) or f"0 0 {mod.SIZE[0]} {mod.SIZE[1]}").split())
        holder = figure(call.who, "stand", call.get("mood", "smile"), flip=right, view_box=f"{x:g} 0 {w:g} {hold_y}")
        side = " board-right" if right else ""
        return Row(f'<div class="board board-hold{side}"><div class="board-peek">{holder}</div>'
                   f'<div class="board-sheet">{grip("grip-left", mod.HAND)}{grip("grip-right", mod.HAND)}{title}'
                   f'<ul class="checks">{"".join(entries)}</ul></div></div>')
    holder = peek(call.who, call.get("mood", "smile"), flip=right)
    hand = mod.HAND
    return Row(f'<div class="board{" board-right" if right else ""}"><div class="board-peek">{holder}</div>'
               f'<div class="board-sheet">{grip("grip-left", hand)}{grip("grip-right", hand)}{title}'
               f'<ul class="checks">{"".join(entries)}</ul></div></div>')


@block("steps", titled=True,
       example="::: steps How a command is made\n1. **Create the file.** Details.\n2. **Call it.**\n:::")
def steps(ctx: Context, call: Call) -> Row:
    """A numbered procedure with large step markers; the body is an ordered list."""
    title = f"<h4>{ctx.inline(call.title)}</h4>" if call.title else ""
    if not re.match(r"\s*\d+[.)]\s", call.body):
        raise BuildError("'steps' needs a numbered list, e.g. '1. **Create the file.** Details.'")
    body = re.sub(r"(?<!\.)\.((?:\s*</(?:p|strong|em|code)>)*\s*)</li>", r"\1</li>", ctx.blocks(call.body))
    body = re.sub(r"<(ol|ul)\b", r"<\1 data-split", body, count=1)   # the steps may break between them (paginate.js)
    return Row(f'{title}<div class="steps">{body}</div>')   # no full stop at the end of a step (text in a block)


@block("cast", body="none", example="::: cast\n:::")
def cast(ctx: Context, call: Call) -> Row:
    """Colored strips introducing every character with a portrait and a line about them."""
    strips = []
    for name in MODULES:
        info = ctx.config.character(name)
        strips.append(f'<div class="cast-row"><div class="medal">{figure(name, "stand", "smile", bust=True)}</div>'
                      f'<div><b>{escape(info["name"])}</b><span>{escape(info.get("role", ""))}</span></div></div>')
    return Row(f'<div class="cast">{"".join(strips)}</div>')

"""Components that shape the page rather than hold text: illustrations, width, page breaks."""
from __future__ import annotations

from .. import design as P
from ..art.scenes import SCENE_KINDS, STORY_PROPS, scene
from .base import TEXT, Call, Choice, Number, Row, block
from .context import Context


@block("scene", wide="always", body="optional",
       options={"kind": Choice(SCENE_KINDS), "h": Number(30, 160), "seed": Number(0, 9999, integer=True),
                "cast": TEXT, "sign": TEXT, "prop": Choice(tuple(STORY_PROPS)), "label": TEXT},
       example='::: scene kind=study h=62 cast="professor:sit:talk, agent:point"\nThe caption.\n:::')
def scene_block(ctx: Context, call: Call) -> Row:
    """A full-width illustration; the body is its caption.

    `cast` lists who appears as `name:pose:mood:mark`; `h` is the height in millimetres;
    `prop` with `label` adds a story object (board, crate, gate); `sign` adds a signpost outdoors.
    """
    story_prop = (call.get("prop"), call.get("label", "")) if call.get("prop") else None
    drawing = scene(h=round(call.get("h", 60) * P.SCENE_UNITS_PER_TEXT_MM), seed=call.get("seed", 3),
                    kind=call.get("kind"), cast=call.get("cast"), sign=call.get("sign"), prop=story_prop)
    caption = f'<div class="caption">{ctx.inline(call.body.strip())}</div>' if call.body.strip() else ""
    return Row(f'<div class="inset">{drawing}</div>{caption}')


@block("wide", wide="always", example="::: wide\nAny blocks inside take the full width.\n:::")
def wide(ctx: Context, call: Call) -> list[Row]:
    """Everything inside spans the full width: text column plus margin."""
    return ctx.compile_body(call.body)


@block("pagebreak", wide="never", body="none", example="::: pagebreak\n:::")
def pagebreak(ctx: Context, call: Call) -> Row:
    """Start a new page here. `<!-- pagebreak -->` does the same."""
    return page_break()


def page_break() -> Row:
    return Row('<div class="pagebreak"></div>', raw=True)


def side_switch(side: str) -> Row:
    """A marker that moves the margin to another side from the next fresh page on."""
    return Row(f'<div class="set-side" data-side="{side}"></div>', raw=True)

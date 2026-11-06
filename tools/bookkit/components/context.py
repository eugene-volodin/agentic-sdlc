"""What a component can ask of the build while it renders."""
from __future__ import annotations

import re

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from html import escape
from typing import TYPE_CHECKING

from ..art.characters import figure
from .base import Row
from .graphics import SQUIGGLE, TAIL

if TYPE_CHECKING:  # imported for annotations only, to keep the import graph one-directional
    from ..config import BookConfig
    from ..markdown import MarkdownRenderer


@dataclass
class Prompt:
    """A prompt collected for export: readers copy these from text files, not from the PDF."""

    chapter: object
    order: int
    title: str
    text: str


# The last full stop of a note, before any closing tags. An ellipsis stays.
_FINAL_PERIOD = re.compile(r"(?<!\.)\.((?:\s*</[a-z]+>)*\s*)$")


def no_final_period(markup: str) -> str:
    """A margin note does not end with a full stop; a question or an ellipsis does."""
    return _FINAL_PERIOD.sub(r"\1", markup)


@dataclass
class Context:
    """Shared state and services for components.

    One context lives for the whole book. The compiler points `chapter` at the chapter being
    compiled and supplies `compile_body` so container components can render nested blocks.
    """

    config: BookConfig
    markdown: MarkdownRenderer
    compile_body: Callable[[str], list[Row]]
    chapter: object = None
    pending_margin: list[str] = field(default_factory=list)   # notes waiting for a row to sit beside
    prompts: list[Prompt] = field(default_factory=list)
    _turns: Counter = field(default_factory=Counter)

    # ------------------------------------------------------------ text
    def blocks(self, text: str) -> str:
        """Render the author's Markdown as block content (paragraphs, lists, nested fences)."""
        return self.markdown.blocks(text)

    def inline(self, text: str) -> str:
        """Render the author's Markdown as inline content (no paragraph wrapper)."""
        return self.markdown.inline(text)

    def label(self, key: str) -> str:
        """A localized UI string, HTML-escaped."""
        return escape(self.config.label(key))

    def label_callout(self, kind: str) -> str:
        """The default heading of a callout, HTML-escaped."""
        return escape(str(self.config.strings.get("callouts", {}).get(kind, kind)))

    def character_name(self, who: str) -> str:
        return escape(self.config.character(who)["name"])

    # ------------------------------------------------------------ state
    def start_chapter(self) -> None:
        """Restart the per-chapter counters."""
        self._turns.clear()

    def take_turn(self, counter: str) -> int:
        """Return how many times `counter` was used before, then count this use.

        Components use it to vary their look from one occurrence to the next.
        """
        turn = self._turns[counter]
        self._turns[counter] += 1
        return turn

    def add_prompt(self, title: str, text: str) -> None:
        order = sum(1 for prompt in self.prompts if prompt.chapter is self.chapter) + 1
        self.prompts.append(Prompt(self.chapter, order, title, text))

    # ------------------------------------------------------------ margin
    def queue_margin(self, markup: str) -> None:
        """Hold margin content until the next row that has a margin."""
        self.pending_margin.append(markup)

    def framed(self, text: str) -> str:
        """Block content for anything in a frame - a bubble, a card, a callout: no full stop at its very end."""
        return no_final_period(self.blocks(text))

    def margin_note(self, content: str) -> str:
        """A handwritten note for the margin."""
        return f'<aside class="note">{SQUIGGLE}{no_final_period(content)}</aside>'

    def margin_talk(self, who: str, content: str, pose: str | None = None, mood: str = "talk") -> str:
        """A small speech bubble with a round portrait, for the margin."""
        portrait = figure(who, pose or "stand", mood, bust=True, medal=True)
        return (f'<div class="margin-talk"><div class="bubble">{no_final_period(content)}{TAIL}</div>'
                f'<div class="who">{portrait}</div></div>')

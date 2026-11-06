"""Chapters to rows: the part of the build that reads the author's files.

Pipeline
--------
    chapter file --split_front_matter--> metadata + body
    body --split_segments--> runs of Markdown and `:::` blocks
    Markdown run --markdown-it--> top-level tokens --> one `Row` per block
    `:::` block  --components.render_block--> rows
    rows of all chapters --pages.document--> one HTML file for the browser to paginate

Every top-level block becomes one grid row: a main column plus a margin column. Margin notes
are queued as they are met and attached to the next row that has a margin. Every problem in
the author's input is reported as a `BuildError` naming the file and the line.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from markdown_it.token import Token

from . import design
from .art.characters import UnknownCharacter, check, resolve
from .art.openers import OPENERS
from .art.scenes import SCENE_KINDS, parse_cast
from .components import Context, Prompt, Row, render_block, render_fence
from .components.layout import page_break, side_switch
from .config import BookConfig, load_config
from .markdown import MarkdownRenderer
from .markup import BuildError, read_source, split_front_matter, split_segments

SIDES = ("outer", "inner", "left", "right", "center", "full")
# Keys a chapter's front matter may contain, with what each one is for.
CHAPTER_KEYS = {
    "title": "chapter title (otherwise the first '# heading')",
    "color": f"accent color: {', '.join(design.ACCENTS)}",
    "number": "false to leave the chapter unnumbered, or its number (a part of the book built on its own)",
    "front": "true for a front page: placed right after the cover, unnumbered, not in the contents",
    "opener": "false to start without the full-page opener",
    "side": f"where the margin is, or a single column (center, full): {', '.join(SIDES)}",
    "who": "the character who speaks on the opener",
    "pose": "that character's pose",
    "lead": "what the character says on the opener",
    "cast": "other characters on the opener, as name:pose:mood",
    "scene": f"opener: a story ({', '.join(OPENERS)}) or a generic setting ({', '.join(SCENE_KINDS)})",
    "sign": "text on the signpost of the opener",
    "world": "the chapter's world: its opener and a camera along its machine in the footers (art/worlds.py)",
    "kicker": "label shown instead of 'Chapter N' on an unnumbered opener; an empty string shows none",
}
OPENER_EXTRAS = 3   # how many characters fit on an opener besides the speaker
_COMMENT = re.compile(r"\s*<!--\s*(pagebreak|side:\s*([\w-]+))\s*-->\s*$")
_AUTHOR_ERRORS = (BuildError, UnknownCharacter, ValueError)
# The opening of a chapter and of each of its sections: the first word is set as a sticker. The word stays whole and in
# place, so the sentence reads normally - unlike a drop cap, which tears the first letter off.
# A word of one or two letters takes the next word along, so the sticker is never a stub.
# Punctuation right after the sticker goes inside it, so a comma never trails after the plate in body type.
_LEAD_IN = re.compile(r"^<p>([^\W\d_][\w-]*)([\s\u00a0]+[\w-]+)?([,.:;!?]?)(?=[\s\u00a0—-]|$)")


def _lead_in(match: re.Match) -> str:
    first, second, mark = match.group(1), match.group(2) or "", match.group(3)
    if len(first) > 2:
        return f'<p><span class="lead-in">{first}{"" if second else mark}</span>{second}{mark if second else ""}'
    return f'<p><span class="lead-in">{first}{second}{mark}</span>'



@dataclass
class Section:
    anchor: str
    title: str


@dataclass
class Chapter:
    path: Path
    meta: dict
    index: int                      # position in the book, 1-based
    number: int | None              # chapter number, None for unnumbered chapters
    color: str
    title: str = ""
    rows: list[Row] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)

    @property
    def anchor(self) -> str:
        return f"chapter-{self.index}"

    @property
    def front(self) -> bool:
        return self.meta.get("front") is True

    @property
    def side(self) -> str:
        return str(self.meta.get("side", "outer"))


@dataclass
class Build:
    """Result of compiling the book: the HTML document plus data for side outputs."""

    html: str
    config: BookConfig
    chapters: list[Chapter]
    prompts: list[Prompt]


def validate_front_matter(meta: dict) -> None:
    """Reject misspelled keys and impossible values before anything is drawn."""
    unknown = sorted(set(meta) - set(CHAPTER_KEYS))
    if unknown:
        raise BuildError(f"front matter: unknown key(s) {', '.join(unknown)}; available: {', '.join(CHAPTER_KEYS)}")
    for key in ("title", "lead", "sign", "kicker", "pose", "who", "color", "scene", "side", "world"):
        if key in meta and (isinstance(meta[key], bool) or not isinstance(meta[key], (str, int, float))):
            raise BuildError(f"front matter: {key} must be text, got {meta[key]!r}")
    if "color" in meta and meta["color"] not in design.ACCENTS:
        raise BuildError(f"front matter: unknown color {meta['color']!r}; available: {', '.join(design.ACCENTS)}")
    if "side" in meta and meta["side"] not in SIDES:
        raise BuildError(f"front matter: side must be one of: {', '.join(SIDES)}")
    if "scene" in meta and meta["scene"] not in SCENE_KINDS and meta["scene"] not in OPENERS:
        raise BuildError(f"front matter: unknown scene {meta['scene']!r}; "
                         f"available: {', '.join([*OPENERS, *SCENE_KINDS])}")
    number = meta.get("number", True)
    if not (number is True or number is False or (isinstance(number, int) and number > 0)):
        raise BuildError(f"front matter: number must be false or a whole number above zero, got {number!r}")
    for key in ("front", "opener"):
        if key in meta and not isinstance(meta[key], bool):
            raise BuildError(f"front matter: {key} must be true or false, got {meta[key]!r}")
    if "world" in meta:
        from .art.worlds import WORLDS
        if meta["world"] not in WORLDS:
            raise BuildError(f"front matter: unknown world {meta['world']!r}; available: {', '.join(WORLDS)}")
        if "scene" in meta:
            raise BuildError("front matter: a chapter with a world takes its opener from it; drop 'scene'")
    if "cast" in meta and not isinstance(meta["cast"], list):
        raise BuildError("front matter: cast must be a list, e.g. [\"cat:wave\", \"sparrow\"]")
    if len(meta.get("cast") or []) > OPENER_EXTRAS:
        raise BuildError(f"front matter: cast can list at most {OPENER_EXTRAS} characters besides the speaker")
    try:
        who = resolve(str(meta.get("who", "professor")))
        check(who, pose=meta.get("pose"))
        for member, pose, mood, _ in parse_cast([str(item) for item in meta.get("cast") or []]):
            check(member, pose=pose, mood=mood)
    except _AUTHOR_ERRORS as error:
        raise BuildError(f"front matter: {error}") from error


class Compiler:
    """Turns chapter files into rows. One instance compiles the whole book."""

    def __init__(self, config: BookConfig) -> None:
        self.config = config
        self.markdown = MarkdownRenderer(config.strings.get("typography", {}))
        self.markdown.root = config.content_dir
        self.context = Context(config=config, markdown=self.markdown, compile_body=self._nested_body)
        self.markdown.fence_handler = lambda info, code: render_fence(self.context, info, code).main
        self.section_count = 0
        self.first_paragraph = True
        self.stretch_turn = 0

    @property
    def chapter(self) -> Chapter | None:
        return self.context.chapter

    # ------------------------------------------------------------ flow
    def _emit(self, rows: list[Row], row: Row) -> None:
        """Append a row, attaching queued margin notes if this row has a margin."""
        pending = self.context.pending_margin
        if pending and row.has_margin:
            row.side = "".join(pending) + row.side
            pending.clear()
        # Dynamic width: a page mixes column-wide and full-width blocks. Every second stretchable
        # block that has nothing in its margin spans the full width - unless its neighbour above
        # already does, so wide blocks stay accents rather than becoming the layout.
        if row.stretch and not row.side:
            self.stretch_turn += 1
            previous = next((r for r in reversed(rows) if not (r.raw or r.heading)), None)
            if self.stretch_turn % 2 == 0 and not (previous and previous.wide):
                row.wide = True
        rows.append(row)

    def _nested_body(self, text: str) -> list[Row]:
        """Compile the body of a container block; line numbers restart inside it."""
        return self.compile_body(text, 1, flush=False)

    def compile_body(self, text: str, first_line: int, flush: bool = True) -> list[Row]:
        """Compile Markdown mixed with `:::` blocks into rows.

        With `flush`, a margin note left over at the end attaches to the last row that can take it.
        """
        rows: list[Row] = []
        for segment in split_segments(text, first_line):
            if segment.kind == "markdown":
                self._markdown_rows(rows, segment.text, segment.line)
                continue
            try:
                for row in render_block(self.context, segment.head, segment.text):
                    self._emit(rows, row)
            except _AUTHOR_ERRORS as error:
                message = str(error)
                raise BuildError(message if message.startswith("line ") else
                                 f"line {segment.line}: {message}") from error
        pending = self.context.pending_margin
        if flush and pending:
            target = next((row for row in reversed(rows) if row.has_margin), None)
            if target is None:
                raise BuildError(f"line {first_line}: a margin note has no block to sit beside")
            target.side += "".join(pending)
            pending.clear()
        return rows

    def _markdown_rows(self, rows: list[Row], text: str, first_line: int) -> None:
        """Render a run of plain Markdown, one row per top-level block."""
        try:
            tokens = self.markdown.parse(text)
        except BuildError as error:
            line, _, message = str(error).partition(": ")
            if not line.startswith("line "):
                raise
            raise BuildError(f"line {first_line + int(line[5:]) - 1}: {message}") from error
        i = 0
        while i < len(tokens):
            token = tokens[i]
            j = i + 1
            if token.nesting == 1:  # find the matching close token
                depth = 1
                while depth:
                    depth += tokens[j].nesting
                    j += 1
            group, i = tokens[i:j], j
            try:
                row = self._markdown_block(group)
            except _AUTHOR_ERRORS as error:
                line = first_line + (token.map[0] if token.map else 0)
                raise BuildError(f"line {line}: {error}") from error
            if row:
                self._emit(rows, row)

    def _markdown_block(self, group: list[Token]) -> Row | None:
        token = group[0]
        if token.type == "heading_open":
            return self._heading(token, group[1])
        if token.type == "fence":
            return render_fence(self.context, token.info, token.content)
        if token.type == "html_block":
            marker = _COMMENT.match(token.content)
            if marker and marker.group(2):
                if marker.group(2) not in SIDES:
                    raise BuildError(f"side must be one of: {', '.join(SIDES)}")
                return side_switch(marker.group(2))
            if marker:
                return page_break()
        if token.type == "paragraph_open":
            figure_row = self._figure(group[1])
            if figure_row:
                return figure_row
            if self.first_paragraph:
                self.first_paragraph = False
                return Row(_LEAD_IN.sub(_lead_in, self.markdown.render(group), count=1))
        if token.type in ("bullet_list_open", "ordered_list_open"):
            token.attrSet("data-split", "")   # long lists may break between items
        if token.type == "table_open":        # a long table breaks between its rows; the header goes along
            for inner in group:
                if inner.type == "tbody_open":
                    inner.attrSet("data-split", "")
        return Row(self.markdown.render(group))

    def _heading(self, token: Token, inline: Token) -> Row | None:
        chapter = self.chapter
        plain = "".join(child.content for child in inline.children or [] if child.type in ("text", "code_inline"))
        inner = self.markdown.render_children(inline)
        if token.tag == "h1":   # the chapter title: shown on the opener, not in the flow
            if chapter and not chapter.title:
                chapter.title = plain
            return None
        if token.tag == "h2":
            self.section_count += 1
            self.first_paragraph = True      # every section opens with a sticker, not only the chapter
            anchor = f"{chapter.anchor}-s{self.section_count}" if chapter else f"s{self.section_count}"
            tag = (f'<span class="h-tag">{chapter.number}.{self.section_count}</span>'
                   if chapter and chapter.number else "")
            if chapter:
                chapter.sections.append(Section(anchor, plain))
            return Row(f'<h2 id="{anchor}">{tag}<span>{inner}</span></h2>', heading="h2")
        tag = "h3" if token.tag == "h3" else "h4"
        return Row(f"<{tag}>{inner}</{tag}>", heading="h3")

    def _figure(self, inline: Token) -> Row | None:
        """A picture alone on its line becomes a figure; its title (or alt text) is the caption."""
        children = [c for c in inline.children or [] if not (c.type == "text" and not c.content.strip())]
        if len(children) != 1 or children[0].type != "image":
            return None
        image = children[0]
        caption = image.attrGet("title") or image.content
        image.attrs.pop("title", None)
        markup = self.markdown.md.renderer.renderInline([image], self.markdown.md.options, {})
        text = f"<figcaption>{self.markdown.inline(str(caption))}</figcaption>" if caption else ""
        return Row(f"<figure>{markup}{text}</figure>")

    # ------------------------------------------------------------ chapters
    def compile_chapter(self, chapter: Chapter, parts: list[tuple[str, str, int]]) -> Chapter:
        """Compile a chapter from its parts: (name for messages, body, first line of the body in its file)."""
        self.context.chapter = chapter
        self.markdown.base_dir = chapter.path if chapter.path.is_dir() else chapter.path.parent
        # Everything that rotates (quote layouts, stretch rhythm) restarts with the chapter, so a
        # chapter built alone with --only looks exactly as it does in the whole book.
        self.section_count, self.first_paragraph, self.stretch_turn = 0, True, 0
        self.context.start_chapter()
        chapter.title = str(chapter.meta.get("title", ""))
        chapter.rows = []
        for name, body, first_line in parts:
            try:
                chapter.rows += self.compile_body(body, first_line)
            except BuildError as error:
                raise BuildError(f"{name}: {error}") from error
        if not chapter.title:
            chapter.title = chapter.path.stem
        return chapter


def compile_book(content_dir: Path, only: str | None = None,
                 world: str | None = None) -> tuple[Compiler, list[Chapter]]:
    """Compile every chapter of the book (or those whose file or folder name contains `only`).

    A chapter is one Markdown file, or a folder: its files are the chapter's parts in alphabetical order, and
    the first of them carries the front matter.

    Chapter numbers are assigned across the whole book even when `only` filters it,
    so a single chapter built on its own looks exactly as it will in the full book.
    """
    config = load_config(content_dir)
    compiler = Compiler(config)
    chapters: list[Chapter] = []
    number = 0
    accents = list(design.ACCENTS)
    scenes: dict[str, str] = {}          # an opener's scene -> the chapter that has it
    for index, source in enumerate(config.chapter_sources(), 1):
        parts: list[tuple[str, str, int]] = []
        meta: dict = {}
        for position, path in enumerate(source.files):
            label = source.label(path)
            try:
                part_meta, body, first_line = split_front_matter(read_source(path))
            except BuildError as error:
                raise BuildError(f"{label}: {str(error).removeprefix(path.name + ': ')}") from error
            if not body.strip():
                raise BuildError(f"{label}: the file has no text" + (" after its front matter" if part_meta else ""))
            if position == 0:
                meta = part_meta
            elif part_meta:
                raise BuildError(f"{label}: only the first file of a chapter folder ({source.files[0].name}) "
                                 f"may have front matter")
            parts.append((label, body, first_line))
        if world and only and only in source.name:      # a preview: the chapter tried in another world
            meta = {key: value for key, value in meta.items() if key != "scene"} | {"world": world}
        # Every chapter has its own, completely unique opener: no two share a scene.
        place = meta.get("scene") or (f"world:{meta['world']}" if meta.get("world") else None)
        if place and meta.get("opener", True) is not False and meta.get("front") is not True:
            kind = str(place)
            if kind in scenes:
                raise BuildError(f"{source.label(source.files[0])}: front matter: the scene {kind!r} is already the "
                                 f"opener of {scenes[kind]}; every chapter needs its own scene")
            scenes[kind] = source.name
        numbered = meta.get("number", True) is not False and meta.get("front") is not True
        explicit = meta.get("number")
        if numbered and isinstance(explicit, int) and not isinstance(explicit, bool):
            number = explicit            # a part built on its own keeps its place in the book; later ones follow on
        else:
            number += 1 if numbered else 0
        if only and only not in source.name:
            continue
        try:
            validate_front_matter(meta)
        except BuildError as error:
            raise BuildError(f"{source.label(source.files[0])}: {error}") from error
        color = str(meta.get("color") or accents[(index - 1) % len(accents)])
        chapter = Chapter(source.path, meta, index, number if numbered else None, color)
        chapters.append(compiler.compile_chapter(chapter, parts))
    if not chapters:
        raise BuildError(f"no chapters found in {content_dir}" + (f" matching {only!r}" if only else ""))
    return compiler, chapters


def build_html(content_dir: Path, only: str | None = None, world: str | None = None) -> Build:
    """Compile the book and assemble the single HTML document the browser paginates.

    With `only`, the cover and the table of contents are left out for a quick layout check. `world` (with `only`)
    previews the chosen chapter in that world without touching its file: the storyboard of a world not yet
    used by any chapter.
    """
    from .art.ink import id_scope
    from .pages import document  # pages draws on the compiler's types

    id_scope("")
    compiler, chapters = compile_book(content_dir, only, world)
    return Build(document(compiler, chapters, front_matter=not only), compiler.config, chapters,
                 compiler.context.prompts)


__all__ = ["Build", "Chapter", "Compiler", "Section", "build_html", "compile_book"]

"""Whole pages and the final document: cover, table of contents, chapter openers.

The document handed to the browser has three parts:

    #source   every page-sized block and every chapter's rows, not yet paginated
    #stock    ornaments the paginator copies onto pages: header perches and accents beside the text
    #book     empty; `theme/paginate.js` fills it with pages
"""
from __future__ import annotations

import json
import re
from html import escape

from . import design, reading
from .art import bookmap, farewell
from .art.characters import figure, module, resolve
from .art.doodles import doodle
from .art.openers import OPENERS, opener
from .art.scenes import parse_cast, scene
from .art.worlds import WORLDS
from .compiler import OPENER_EXTRAS, Chapter, Compiler
from .components import Row
from .components.context import no_final_period
from .components.graphics import MARK_STAR, TAIL
from .config import THEME, BookConfig
from .markup import BuildError
from .fonts import font_faces
from .title import draw as draw_title

# What may stand beside a paragraph to lighten a page of solid text, in the order used:
# (character, pose, mood) or the name of a doodle from `art.doodles`. One or two per page at most.
ACCENTS = (("cat", "read", "smile"), "monitor", ("agent", "wave", "smile"), "floppy", ("caterpillar", "write", "smile"),
           "mug", ("sparrow", "shrug", "worry"), "keyboard", ("professor", "think", "wink"), "cassette",
           ("agent", "carry", "smile"), "duck", ("cat", "think", "smile"), "tower", ("sparrow", "cheer", "talk"),
           "notebook", ("agent", "think", "wink"), "bug", ("caterpillar", "cheer", "smile"), "lamp")
# Style sheets in cascade order: foundations first, then one sheet per component family.
STYLE_SHEETS = ("base.css", "page.css", "typography.css", "speech.css", "callouts.css", "lists.css", "code.css",
                "chat.css", "people.css", "layout.css", "pages.css")
# Who stands on the dashed line of the running header, by page number modulo 4: (who, bust?, drop). The drop, in
# mm, lowers the drawing box so the feet and not the box meet the line; measured on the page PNGs.
PERCHES = {0: ("cat", False, 0.2), 1: ("sparrow", False, -0.3), 2: ("caterpillar", False, -0.2),
           3: ("agent", False, -0.4)}
# Where the opener's cast stands, left to right, in scene units.
OPENER_POSITIONS = (330, 545, 668, 770)
assert len(OPENER_POSITIONS) == OPENER_EXTRAS + 1
COVER_CAST = (("professor", "explain", "talk"), ("agent", "wave", "smile"), ("cat", "think", "smile"),
              ("caterpillar", "cheer", "smile"), ("sparrow", "wave", "talk"))
COVER_POSITIONS = (150, 322, 470, 610, 742)


def cover_page(config: BookConfig) -> str:
    """The cover: topic stickers along the top, the series plate, the name of the book, the whole cast."""
    title = escape(config.title)
    if config.title_highlight and config.title_highlight in config.title:
        title = title.replace(escape(config.title_highlight), f"<em>{escape(config.title_highlight)}</em>")
    drawing = scene(h=round(design.COVER_SCENE_HEIGHT * design.SCENE_UNITS_PER_PAGE_MM), seed=42, kind="path",
                    sky=False, xs=list(COVER_POSITIONS), cast=list(COVER_CAST))
    # The top band carries either the topics as stickers or a plain line of text.
    if config.topics:
        band = "".join(f"<b>{escape(topic)}</b>" for topic in config.topics)
        band = f'<div class="cover-topics">{band}</div>'
    else:
        band = escape(config.kicker)
    headline = ""
    if config.headline:
        text = escape(config.headline)
        mark = escape(config.headline_highlight)
        if mark and mark in text:   # one phrase of the name sits on a colored plate and never breaks
            text = text.replace(mark, f"<mark>{mark}</mark>")
        headline = f'<h1 class="cover-headline">{text}</h1>'
    subtitle = f'<div class="cover-sub">{escape(config.subtitle)}</div>' if config.subtitle else ""
    plate_tag = "div" if config.headline else "h1"   # exactly one <h1> on the page
    version = (f'<span class="cover-version">{escape(config.label("version_short"))} {escape(config.version)}</span>'
               if config.version else "")
    return (f'<section class="fullpage cover"><div class="cover-band cover-top">{band}</div>'
            f'<div class="cover-head"><div class="cover-plate{" small" if config.headline else ""}">'
            f'<{plate_tag} class="cover-title">{title}</{plate_tag}></div>{headline}{subtitle}</div>'
            f'<div class="cover-scene">{drawing}</div><div class="cover-band cover-bottom">'
            f'<span>{escape(config.author)}</span>{version}<span>{escape(config.year)}</span></div></section>')


def opener_page(chapter: Chapter, compiler: Compiler) -> str:
    """The full-page opening of a chapter: a story picture, the title on paper plates, the professor's bubble, a tag.

    A chapter whose `scene:` names a story in `art.stories` gets that picture over the whole page;
    any other setting falls back to the generic scene under a colored page.
    """
    meta, config = chapter.meta, compiler.config
    kind = WORLDS[meta["world"]].opener if meta.get("world") else meta.get("scene", "meadow")
    if kind not in OPENERS:
        return _generic_opener(chapter, compiler)
    plain = re.sub(r"[*_`]", "", str(meta.get("lead", "")))
    title = re.sub(r"[*`]", "", chapter.title).strip()   # drawn letters carry no Markdown emphasis or code
    lettering = draw_title(title)
    art = opener(kind, design.ACCENTS[chapter.color], seed=chapter.index, lead_chars=len(plain),
                 words=config.opener_words(kind), title=(lettering.width, lettering.height))
    lead = ""
    if meta.get("lead"):
        words = no_final_period(compiler.markdown.blocks(str(meta["lead"])))   # framed text: no final full stop
        left, bottom, width, tail = art.bubble
        lead = (f'<div class="opener-lead story" style="left:{left:.1f}mm;bottom:{bottom:.1f}mm;width:{width:.1f}mm;'
                f'--at:{tail:.1f}mm"><div class="bubble">{words}{TAIL}</div></div>')
    label = (f'{escape(config.label("chapter"))} {chapter.number}' if chapter.number
             else escape(str(meta.get("kicker", config.label("intro"))))).upper()
    return (f'<div class="fullpage opener story">'
            f'<div class="opener-art-box">{art.svg}</div>'
            f'<h1 class="opener-title" id="{chapter.anchor}" aria-label="{escape(title)}">{lettering.svg}'
            f'<span class="opener-title-text">{escape(title)}</span></h1>'
            f'{lead}{_tag(label) if label else ""}</div>')


def _tag(label: str) -> str:
    """The arrow tag at the foot of a story opener, like the page-number tags of the original."""
    width = 30 + len(label) * 13.5
    return (f'<svg class="opener-tag" viewBox="0 0 {width + 24:.0f} 46" style="width:{(width + 24) / 4:.1f}mm">'
            f'<path d="M-6,3 H{width:.0f} L{width + 20:.0f},23 L{width:.0f},43 H-6 Z"/>'
            f'<text x="24" y="30.5">{label}</text></svg>')


def _generic_opener(chapter: Chapter, compiler: Compiler) -> str:
    """The colored opening page with a generic scene at its foot: for chapters without a story of their own."""
    meta, config = chapter.meta, compiler.config
    speaker = resolve(str(meta.get("who", "professor")))
    cast = [(speaker, meta.get("pose", module(speaker).TALK_POSE), "talk")]
    cast += [member[:3] for member in parse_cast([str(item) for item in meta.get("cast") or []])]
    drawing = scene(h=round(design.OPENER_SCENE_HEIGHT * design.SCENE_UNITS_PER_PAGE_MM), seed=chapter.index + 11,
                    kind=meta.get("scene", "meadow"), cast=cast, xs=list(OPENER_POSITIONS[:len(cast)]),
                    sign=meta.get("sign"), sign_x=45, sky=False, speaker=0)
    lead = ""
    if meta.get("lead"):
        words = no_final_period(compiler.markdown.blocks(str(meta["lead"])))   # framed text: no final full stop
        lead = (f'<div class="opener-lead"><div class="bubble">{words}'
                f"{TAIL}</div></div>")
    if chapter.number:
        label = (f'<div class="opener-big">{chapter.number}</div>'
                 f'<div class="opener-num">{escape(config.label("chapter"))} {chapter.number}</div>')
    else:
        kicker = str(meta.get("kicker", config.label("intro")))
        label = f'<div class="opener-num">{escape(kicker)}</div>' if kicker else ""     # kicker: "" - no plate
    digits = len(str(chapter.number)) if chapter.number else 0      # the title keeps clear of the big numeral
    return (f'<div class="fullpage opener">{label}<h1 id="{chapter.anchor}" style="--digits: {digits}"><span>'
            f'{compiler.markdown.inline(chapter.title)}</span></h1>{lead}'
            f'<div class="opener-scene">{drawing}</div></div>')


def plain_chapter_title(chapter: Chapter, compiler: Compiler) -> str:
    """The heading of a chapter that has no opener page."""
    return Row(f'<h1 class="chapter-title" id="{chapter.anchor}">{compiler.markdown.inline(chapter.title)}</h1>',
               heading="h1").html()   # in the text column, so it lines up with what follows


# An entry of `plan:` in book.yml: "3. Title" for a numbered chapter, a bare title for the introduction and the like.
_PLANNED = re.compile(r"^(\d+)\.\s+(.+)$")


def contents_section(chapters: list[Chapter], config: BookConfig) -> str:
    """The table of contents as ordinary rows, so it can run over several pages.

    Page numbers are filled in by the paginator once it knows where each heading landed. With `plan:` in
    book.yml the contents show the whole handbook: a written chapter takes its place in the plan (matched by
    number, or by title if it has none), and a chapter not yet written is listed, greyed, as coming soon -
    readers of an early version see where it is going (versions are released as chapters are written).
    """
    def entry(level: int, anchor: str, title: str, badge: str = "", time: str = "") -> str:
        return (f'<a class="toc-{level}" href="#{anchor}">{badge}<span>{escape(title)}</span>{time}'
                f'<span class="dots"></span><span class="pg" data-ref="{anchor}"></span></a>')

    def written(chapter: Chapter) -> str:
        badge = f'<span class="n">{chapter.number or MARK_STAR}</span>'
        time = f'<span class="time">{escape(reading_time(chapter, config))}</span>'   # what lies ahead
        lines = [entry(1, chapter.anchor, chapter.title, badge, time)]
        lines += [entry(2, section.anchor, section.title) for section in chapter.sections]
        return Row(f'<div class="toc-block" data-color="{chapter.color}">{"".join(lines)}</div>').html()

    def planned(number: str, title: str) -> str:
        mark = escape(number) if number else MARK_STAR
        return Row(f'<div class="toc-block planned"><div class="toc-1"><span class="n">{mark}</span>'
                   f'<span>{escape(title)}</span><span class="dots"></span>'
                   f'<span class="soon">{escape(config.label("soon"))}</span></div></div>').html()

    rows = [Row(f'<h2 class="toc-title"><span>{escape(config.label("contents"))}</span></h2>',
                heading="h1").html()]
    for number, title, found in _plan(chapters, config):
        rows.append(written(found) if found else planned(number, title))
    # The map of the book takes the page after the contents: they fill their pages. It
    # draws the plan of the whole handbook, so a book without `plan:` (a part built on its own, the demo) has none.
    if config.plan:
        rows.append(f'<div class="fullpage bookmap">{book_map(chapters, config)}</div>')
    return (f'<section class="chapter contents" data-color="sky" data-num="" '
            f'data-title="{escape(config.label("contents"))}" data-side="right">{"".join(rows)}</section>')


def _plan(chapters: list[Chapter], config: BookConfig) -> list[tuple[str, str, Chapter | None]]:
    """The handbook in plan order: (number, title, the written chapter or None). A written chapter takes its place in
    the plan (matched by number, or by title if it has none); one missing from the plan comes at the end, never lost."""
    out: list[tuple[str, str, Chapter | None]] = []
    left = list(chapters)
    for item in config.plan:
        match = _PLANNED.match(item.strip())
        number, title = (match.group(1), match.group(2)) if match else ("", item.strip())
        found = next((c for c in left if (str(c.number) == number if number else not c.number and c.title == title)),
                     None)
        if found:
            left.remove(found)
        out.append((number, title, found))
    out += [(str(chapter.number or ""), chapter.title, chapter) for chapter in left]
    return out


def reading_time(chapter: Chapter, config: BookConfig) -> str:
    """The reading time in the locale's words, like "≈ 20 min": how long the chapter takes to read (`reading.py`)."""
    return f"≈ {reading.minutes(reading.characters(chapter.path))} {config.label('minutes')}"


def book_map(chapters: list[Chapter], config: BookConfig) -> str:
    """The map of the book: every entry of the plan as a place by the road, with its title and reading time
    (`art/bookmap.py`)."""
    stops, seen_number = [], False
    for number, title, found in _plan(chapters, config):
        seen_number = seen_number or bool(number)
        slot = number or ("end" if seen_number else "intro")
        color = design.ACCENTS.get(found.color, design.TEAL) if found else design.TEAL
        world = (str(found.meta.get("world") or "") or None) if found else None
        if world and world not in bookmap.VIGNETTES and slot != bookmap.RAILWAY:   # the last one is the railway
            raise BuildError(f"{found.path}: the world {world!r} has no place on the map of the book yet; "
                             f"add its vignette to art/bookmap.py")
        stops.append(bookmap.Stop(slot, number, bookmap.plain(found.title if found else title),
                                  reading_time(found, config) if found else "", color, world, found is not None))
    try:
        return bookmap.draw(stops, config.label("soon")).svg
    except bookmap.MapError as error:
        raise BuildError(f"book.yml, plan: {error}") from error


def farewell_page() -> str:
    """The last page of the book: the whole cast walking off into the computer city (`art/farewell.py`).
    A full page of its own after the last chapter, like the map after the contents."""
    return f'<div class="fullpage farewell">{farewell.draw().svg}</div>'


def chapter_section(chapter: Chapter, compiler: Compiler) -> str:
    head = (plain_chapter_title(chapter, compiler) if chapter.meta.get("opener") is False
            else opener_page(chapter, compiler))
    body = "".join(row.html() for row in chapter.rows)
    world = escape(str(chapter.meta.get("world", "")))
    return (f'<section class="chapter" data-color="{chapter.color}" data-num="{chapter.number or ""}" '
            f'data-title="{escape(chapter.title)}" data-side="{chapter.side}" data-world="{world}">{head}{body}'
            f'</section>')


def stock() -> str:
    """Ornaments for the paginator to copy: who perches on the header, what lightens a page of solid text."""
    perches = "".join(f'<div data-perch="{slot}" data-drop="{drop}">{figure(who, "stand", "smile", bust=bust)}</div>'
                      for slot, (who, bust, drop) in PERCHES.items())
    accents = "".join(f'<div data-accent>{doodle(item) if isinstance(item, str) else figure(*item)}</div>'
                      for item in ACCENTS)
    return perches + accents


def stylesheet() -> str:
    """Bundled fonts, design tokens and the style sheets, in the order the cascade needs."""
    fonts = font_faces()
    sheets = "\n".join((THEME / "css" / name).read_text(encoding="utf-8") for name in STYLE_SHEETS)
    return f"{fonts}\n{design.css_variables()}\n{sheets}"


def document(compiler: Compiler, chapters: list[Chapter], front_matter: bool = True) -> str:
    """Assemble the HTML document the browser paginates."""
    config = compiler.config
    # Front pages (author, licence) follow the cover; the contents come after them and list the rest.
    leading = [chapter for chapter in chapters if chapter.front]
    main = [chapter for chapter in chapters if not chapter.front]
    front = ""
    if front_matter:
        front = cover_page(config) if config.cover else ""
    front += "".join(chapter_section(chapter, compiler) for chapter in leading)
    if front_matter and config.toc and main:
        front += contents_section(main, config)
    sections = "".join(chapter_section(chapter, compiler) for chapter in main)
    # The farewell closes the whole handbook, after whatever chapter is last; a book without `plan:` (a part built on
    # its own, the demo) and a build of one chapter have none.
    if front_matter and config.plan and main:
        sections += farewell_page()
    families = sorted({family for family, *_ in design.FONT_FILES})
    # In a <script>: "</" in a title must not close the element.
    settings = json.dumps({"title": config.title, "fonts": families, "continued": config.label("continued"),
                           "continuation": config.label("continuation")},
                          ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="{escape(config.language)}"><head><meta charset="utf-8"><title>{escape(config.title)}</title>
<meta name="author" content="{escape(config.author)}">
<style>{stylesheet()}</style>
</head><body>
<div id="source">{front}{sections}</div>
<div id="stock">{stock()}</div>
<div id="book"></div>
<script>window.__bookConfig = {settings};</script>
<script>{(THEME / "paginate.js").read_text(encoding="utf-8")}</script>
</body></html>"""

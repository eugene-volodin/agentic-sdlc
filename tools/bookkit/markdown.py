"""Markdown rendering with the book's typography.

A thin wrapper around markdown-it that adds what running text in a printed book needs:

* typographic quotes and dashes in the book's language;
* no-break spaces after short words and before dashes, so lines never end on a preposition
  (applied to text only - code is never touched);
* two inline extensions: `[[Key]]` for keyboard keys and `==text==` for a marker highlight;
* images resolved against the chapter file, with a clear error when one is missing;
* code fences inside lists and blocks rendered by the same components as top-level ones.
"""
from __future__ import annotations

import re
from collections.abc import Callable
from html import escape
from pathlib import Path

from markdown_it import MarkdownIt
from markdown_it.token import Token

from .art.flags import flag
from . import design
from .markup import BuildError

# Inline extensions, matched in running text only: [[Key]] and ==marked text==.
# Inline code with spaces up to this length never breaks and is never stretched by justification: `codex mcp add`
# printed with wide gaps reads as a different command.
CODE_WORDS_MAX = 32
_INLINE_EXTRA = re.compile(r"\[\[(?P<key>[^\]\n]{1,24})\]\]|==(?P<mark>\S(?:[^=\n]*\S)?)==|:flag-(?P<flag>[a-z]{2}):")
# A table cell written as "- one<br>- two" is a little list: every line gets a marker (see typography.css).
_CELL_LIST = re.compile(r"<td([^>]*)>(\s*-\s.*?)</td>", re.S)   # a column's alignment adds a style attribute
# A number in groups of three (21 760, 1 234 567): its spaces never break.
_THOUSANDS = re.compile(r"(?<![\d.,])(\d{1,3}(?: \d{3})+)(?!\d)")
# Inline code and a link written as an address break only where a reader expects it: after a slash (after a dot too
# in an address), never inside a name, never before a dot (a line would start with it); `<wbr>` marks each place,
# and the stylesheet keeps the rest whole.
_PATH_BREAK = re.compile(r"(?<=/)(?=[^/.][^/]{3})")      # and never before a piece too short to stand alone
_URL_BREAK = re.compile(r"(?<=[/.])(?=[^/.][^/.]{3})")
_LAST_WORD = re.compile(r" (\S+)\s*$")
_PUNCTUATION = re.compile(r"[,.;:!?)»…]+")
_COMPOUND = re.compile(r"(?<![\w-])[^\W\d_]+-[^\W\d_]{1,2}(?![\w-])")
_ADDRESS = re.compile(r"^(?:[a-z][a-z0-9+.-]*://)?[\w-]+(?:\.[\w-]+)+(?:/\S*)?$", re.I)
_ABSOLUTE = re.compile(r"^([a-z][a-z0-9+.-]*:|/)", re.I)
# The only HTML the author writes by hand: a line break (in a table cell), a tinted result, comments (page breaks,
# layout switches). Anything else - a <script> above all, since readers send pull requests - is an error.
_ALLOWED_HTML = re.compile(r'<!--.*?-->|<br\s*/?>|<span class="score (?:good|weak)">|</span>', re.S)
IMAGE_TYPES = (".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif")


def _cell_list(match: re.Match) -> str:
    items = [re.sub(r"^\s*-\s+", "", piece).strip() for piece in re.split(r"<br\s*/?>", match.group(2))]
    return (f"<td{match.group(1)}>" + "".join(f'<span class="cell-item">{item}</span>' for item in items if item)
            + "</td>")


def _last_word(text: str) -> str:
    """A paragraph never ends with a short word alone on its line: it keeps to the word before it."""
    match = _LAST_WORD.search(text)
    if match and len(re.findall(r"[^\W_]", match.group(1))) < design.AUDIT_SHORT_WORD:
        return text[:match.start()] + "\u00a0" + match.group(1)
    return text


def _glue(children: list[Token]) -> list[Token]:
    """A command kept whole (`code.words`, an inline block) and the punctuation after it never part at a line end;
    nor does a word and a particle of one or two letters after its hyphen: the particle never starts a line alone."""
    out: list[Token] = []
    for child in children:
        if child.type != "text":
            out.append(child)
            continue
        text = child.content
        mark = _PUNCTUATION.match(text)
        if mark and out and out[-1].type == "code_inline" and out[-1].attrGet("class") == "words":
            out[-1:] = [_html('<span class="glue">'), out[-1], Token("text", "", 0, content=mark.group()),
                        _html("</span>")]
            text = text[mark.end():]
        position = 0
        for match in _COMPOUND.finditer(text):
            if match.start() > position:
                out.append(Token("text", "", 0, content=text[position:match.start()]))
            out += [_html('<span class="glue">'), Token("text", "", 0, content=match.group()), _html("</span>")]
            position = match.end()
        if text[position:]:
            out.append(Token("text", "", 0, content=text[position:]))
    return out


def _html(content: str) -> Token:
    return Token("html_inline", "", 0, content=content)


def breakable(text: str, url: bool = False) -> str:
    """`text` escaped for HTML, with a `<wbr>` after each slash (and each dot of an address) followed by more of it,
    not by a dot."""
    pattern = _URL_BREAK if url else _PATH_BREAK
    pieces = pattern.split(text)
    return "<wbr>".join(escape(piece, quote=False) for piece in pieces)


class MarkdownRenderer:
    """Parses and renders Markdown for one book."""

    def __init__(self, typography: dict) -> None:
        md = MarkdownIt("commonmark", {"typographer": True, "html": True,
                                       "quotes": typography.get("quotes", "“”‘’")})
        md.enable(["table", "strikethrough", "replacements", "smartquotes"])
        # Assigned directly: `add_render_rule` would rebind these to the renderer object.
        md.renderer.rules["fence"] = self._fence_rule
        md.renderer.rules["image"] = self._image_rule
        md.renderer.rules["code_inline"] = self._code_rule
        self.md = md
        words = "|".join(re.escape(word) for word in typography.get("short_words", []))
        self._short_words = re.compile(rf"(?<![\w-])({words}) (?=\S)", re.IGNORECASE) if words else None
        self._short_last = re.compile(rf"(?<![\w-])({words}) $", re.IGNORECASE) if words else None
        self.base_dir: Path | None = None                       # folder of the chapter being rendered
        self.root: Path | None = None                           # the book's folder: pictures come from inside it
        self.fence_handler: Callable[[str, str], str] | None = None   # (info, code) -> HTML

    # ------------------------------------------------------------ parsing
    def parse(self, text: str) -> list[Token]:
        """Tokenize block-level Markdown and apply the typography to its text."""
        tokens = self.md.parse(text, {})
        for token in tokens:
            for piece in [token, *(token.children or [])]:
                if piece.type in ("html_block", "html_inline") and not _ALLOWED_HTML.fullmatch(piece.content.strip()):
                    where = f"line {token.map[0] + 1}: " if token.map else ""
                    raise BuildError(f"{where}HTML is not allowed in the text: {piece.content.strip()[:60]!r}; "
                                     f"write Markdown or a '::: block', and put code in `backticks`")
        return self._typography(tokens)

    def _typography(self, tokens: list[Token]) -> list[Token]:
        """Polish the text of inline tokens. Code spans and code blocks are separate tokens and stay untouched."""
        for token in tokens:
            if not token.children:
                continue
            try:
                self._polish(token)
            except ValueError as error:
                raise BuildError(f"line {token.map[0] + 1}: {error}" if token.map else str(error)) from error
        return tokens

    def _polish(self, token: Token) -> None:
        """Typography for the text of one inline token: no-break spaces, keys, markers, flags."""
        children: list[Token] = []
        link = 0
        source = token.children
        for nth, child in enumerate(source):
            link += {"link_open": 1, "link_close": -1}.get(child.type, 0)
            if child.type == "text" and link and _ADDRESS.match(child.content):
                children.append(Token("html_inline", "", 0, content=breakable(child.content, url=True)))
                continue
            if child.type == "code_inline" and " " in child.content and len(child.content) <= CODE_WORDS_MAX:
                child.attrSet("class", "words")   # a short command keeps its spaces as typed (typography.css)
            if child.type != "text":
                children.append(child)
                continue
            following = source[nth + 1] if nth + 1 < len(source) else None
            if self._short_words:
                child.content = self._short_words.sub(lambda m: m.group(1) + "\u00a0", child.content)
                if following is not None:          # a short word before code, a link or a marker keeps to it too
                    child.content = self._short_last.sub(lambda m: m.group(1) + "\u00a0", child.content)
            child.content = child.content.replace(" — ", "\u00a0— ")
            child.content = _THOUSANDS.sub(lambda m: m.group(1).replace(" ", "\u00a0"), child.content)
            if following is None:
                child.content = _last_word(child.content)
            children += self._extras(child)
        token.children = _glue(children)

    @staticmethod
    def _extras(text: Token) -> list[Token]:
        """Split a text token around `[[Key]]` and `==mark==`, turning those into HTML tokens."""
        pieces: list[Token] = []
        position = 0
        for match in _INLINE_EXTRA.finditer(text.content):
            if match.start() > position:
                pieces.append(Token("text", "", 0, content=text.content[position:match.start()]))
            if match.group("flag"):
                pieces.append(Token("html_inline", "", 0, content=flag(match.group("flag"))))
            else:
                tag, inner = ("kbd", match.group("key")) if match.group("key") else ("mark", match.group("mark"))
                pieces.append(Token("html_inline", "", 0, content=f"<{tag}>{escape(inner)}</{tag}>"))
            position = match.end()
        if not pieces:
            return [text]
        if position < len(text.content):
            pieces.append(Token("text", "", 0, content=text.content[position:]))
        return pieces

    # ------------------------------------------------------------ rendering
    def render(self, tokens: list[Token]) -> str:
        return _CELL_LIST.sub(_cell_list, self.md.renderer.render(tokens, self.md.options, {}))

    def render_children(self, inline: Token) -> str:
        """Render the children of an inline token (used for headings)."""
        return self.md.renderer.renderInline(inline.children or [], self.md.options, {})

    def blocks(self, text: str) -> str:
        """Render text as block content: paragraphs, lists, tables, nested fences."""
        return self.render(self.parse(text.strip("\n")))

    def inline(self, text: str) -> str:
        """Render text as inline content, without a paragraph around it."""
        tokens = self.md.parseInline(text.strip(), {})
        for piece in (child for token in tokens for child in token.children or []):
            if piece.type == "html_inline" and not _ALLOWED_HTML.fullmatch(piece.content.strip()):
                raise BuildError(f"HTML is not allowed in the text: {piece.content.strip()[:60]!r}")
        return self.render(self._typography(tokens))

    # ------------------------------------------------------------ rules
    def _fence_rule(self, tokens: list[Token], idx: int, options, env) -> str:
        token = tokens[idx]
        if self.fence_handler is None:
            raise RuntimeError("MarkdownRenderer.fence_handler is not set")
        return self.fence_handler(token.info, token.content)

    @staticmethod
    def _code_rule(tokens: list[Token], idx: int, options, env) -> str:
        token = tokens[idx]
        words = token.attrGet("class") == "words"
        text = escape(token.content, quote=False) if words else breakable(token.content, url="://" in token.content)
        return f'<code class="words">{text}</code>' if words else f"<code>{text}</code>"

    def _image_rule(self, tokens: list[Token], idx: int, options, env) -> str:
        token = tokens[idx]
        token.attrSet("src", self.resolve_image(str(token.attrGet("src") or "")))
        return self.md.renderer.image(tokens, idx, options, env)

    def resolve_image(self, source: str) -> str:
        """Turn an image path relative to the chapter into a URL the browser can load.

        A picture is a file of the book: a link to the web would make the PDF depend on the network at build
        time, and a path out of the book's folder on a file the public repository does not have.
        """
        if _ABSOLUTE.match(source):
            raise BuildError(f"image {source!r}: put the picture next to the chapter and give its file name")
        if not self.base_dir:
            raise BuildError(f"image {source!r}: no chapter folder to look in")
        target = (self.base_dir / source).resolve()
        if self.root and not target.is_relative_to(self.root.resolve()):
            raise BuildError(f"image {source!r} lies outside the book's folder")
        if not target.is_file():
            raise BuildError(f"image not found: {source}")
        if target.suffix.lower() not in IMAGE_TYPES:
            raise BuildError(f"image {source!r}: not a picture; use {', '.join(IMAGE_TYPES)}")
        return target.as_uri()

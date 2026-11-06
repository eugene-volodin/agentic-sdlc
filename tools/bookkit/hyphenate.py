"""Hyphenation at build time: soft hyphens (U+00AD) in the words of running text.

The browser's own hyphenation (`hyphens: auto`) uses the dictionaries of the machine it runs on, so one book laid out
on two systems broke its lines differently and came out with a different page count. Here every word that may break
gets its break points from the pyphen dictionaries that ship with the package, and the style sheets say
`hyphens: manual`: the browser breaks only there, the same on every machine.

Only text inside a paragraph or a list item is touched, and never inside code, keys, links, headings, pictures,
bubbles, margin notes or anything else listed in SKIP_TAGS and SKIP_CLASSES. A word gets break points only when it
stands alone: an address, a path, an identifier, a CamelCase name or an acronym is left whole.
"""
from __future__ import annotations

import re
from functools import lru_cache

import pyphen

from . import design

SHY = "\u00ad"

HOSTS = {"p", "li"}                                          # the blocks whose text is hyphenated
SKIP_TAGS = {"code", "pre", "kbd", "samp", "a", "h1", "h2", "h3", "h4", "h5", "h6", "svg", "math", "script",
             "style", "title", "textarea", "button", "sup", "sub"}
SKIP_CLASSES = {"bubble", "note", "scroll-text", "glue", "screen", "terminal"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
RAW = {"script", "style"}                                    # their content is not markup

_TOKEN = re.compile(r"<!--.*?-->|<!\[CDATA\[.*?\]\]>|<![^>]*>|<\?[^>]*>|</?[A-Za-z][^>]*>|[^<]+|<", re.S)
_TAG = re.compile(r"<(/?)([A-Za-z][\w:-]*)([^>]*?)(/?)>", re.S)
_CLASS = re.compile(r"""\bclass\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", re.I)
_ENTITY = re.compile(r"&(?:#\d+|#x[0-9a-f]+|[a-z][a-z0-9]*);", re.I)
_CHUNK = re.compile(r"\S+")
_WORD = re.compile(r"[^\W\d_]+")
_CYRILLIC = re.compile(r"^[\u0400-\u04ff]+$")
_LATIN = re.compile(r"^[A-Za-z]+$")
# A chunk that is an address, a path, a file name, an identifier or a mention: it is left whole.
_TECHNICAL = re.compile(r"[/\\@_#=<>{}\[\]|~^$%*+]|\w\.\w|\d")


@lru_cache(maxsize=4)
def _dictionary(name: str) -> pyphen.Pyphen:
    return pyphen.Pyphen(lang=name, left=design.HYPHEN_LEFT, right=design.HYPHEN_RIGHT)


@lru_cache(maxsize=65536)
def word(text: str) -> str:
    """One word with its break points: soft hyphens by the dictionary of its script. A word too short, of mixed
    scripts, an acronym or a CamelCase name comes back as it was."""
    if len(text) < design.HYPHEN_MIN_WORD:
        return text
    if _CYRILLIC.match(text):
        script = "cyrillic"
    elif _LATIN.match(text):
        script = "latin"
    else:
        return text
    if any(ch.isupper() for ch in text[1:]):                  # GitHub, AGENTS, CI: names are not broken
        return text
    return _dictionary(design.HYPHEN_DICTIONARIES[script]).inserted(text, hyphen=SHY)


def _chunk(text: str, glued_before: bool, glued_after: bool, last: bool = False) -> str:
    """A run of characters without spaces: each of its words gets break points, unless the run is technical. A word
    that runs on into the text of a neighbouring element (`**auto**mation`) is only part of a word: it is left
    whole. With `last` the run ends its block: its last word is left whole too."""
    if _TECHNICAL.search(text):
        return text
    words = list(_WORD.finditer(text))
    out, at = [], 0
    for n, match in enumerate(words):
        out.append(text[at:match.start()])
        piece = match.group()
        cut_before = n == 0 and match.start() == 0 and glued_before
        cut_after = n == len(words) - 1 and (last or match.end() == len(text) and glued_after)
        out.append(piece if cut_before or cut_after else word(piece))
        at = match.end()
    out.append(text[at:])
    return "".join(out)


def _text(text: str, glued_before: bool, glued_after: bool, last: bool = False) -> str:
    """A text node of running text. Entities (`&amp;`, `&nbsp;`) are kept as they are and end a word. With `last`
    the node ends its block, and its last word is left whole: a paragraph never ends on a piece of a word."""
    out, at = [], 0
    pieces = []
    for match in _ENTITY.finditer(text):
        pieces.append((text[at:match.start()], False))
        pieces.append((match.group(), True))
        at = match.end()
    pieces.append((text[at:], False))
    for k, (piece, entity) in enumerate(pieces):
        if entity or not piece:
            out.append(piece)
            continue
        chunks = list(_CHUNK.finditer(piece))
        final = last and all(not rest or entity for rest, entity in pieces[k + 1:])
        done = 0
        for n, match in enumerate(chunks):
            out.append(piece[done:match.start()])
            before = n == 0 and match.start() == 0 and (glued_before if k == 0 else False)
            after = n == len(chunks) - 1 and match.end() == len(piece) and (glued_after if k == len(pieces) - 1
                                                                           else False)
            out.append(_chunk(match.group(), before, after, last=final and n == len(chunks) - 1))
            done = match.end()
        out.append(piece[done:])
    return "".join(out)


def _classes(attributes: str) -> set[str]:
    match = _CLASS.search(attributes)
    return set((match.group(1) or match.group(2) or match.group(3) or "").split()) if match else set()


def hyphenate(html: str) -> str:
    """The HTML with soft hyphens in the words of its running text (see the module's description)."""
    tokens = [m.group() for m in _TOKEN.finditer(html)]
    # The open elements: (tag, the token that opened the paragraph or list item it is in, or -1; skipped).
    stack: list[tuple[str, int, bool]] = []
    marks: list[tuple[int, int]] = []                        # the text tokens to hyphenate, each with its block
    raw: str | None = None
    for i, token in enumerate(tokens):
        if raw is not None:
            if token.lower().startswith(f"</{raw}"):
                if stack and stack[-1][0] == raw:
                    stack.pop()
                raw = None
            continue
        tag = _TAG.fullmatch(token)
        if tag:
            closing, name, attributes, self_closing = tag.group(1), tag.group(2).lower(), tag.group(3), tag.group(4)
            if closing:
                for depth in range(len(stack) - 1, -1, -1):
                    if stack[depth][0] == name:
                        del stack[depth:]
                        break
                continue
            if name in VOID or self_closing:
                continue
            hosted = i if name in HOSTS else stack[-1][1] if stack else -1
            skipped = (name in SKIP_TAGS or bool(_classes(attributes) & SKIP_CLASSES)
                       or bool(stack and stack[-1][2]))
            stack.append((name, hosted, skipped))
            if name in RAW:
                raw = name
            continue
        if token.startswith("<") and len(token) > 1:          # a comment, a doctype, a declaration
            continue
        if stack and stack[-1][1] >= 0 and not stack[-1][2]:
            marks.append((i, stack[-1][1]))
    if not marks:
        return html
    # The last text of each block that has a word in it: its last word stays whole.
    ends = {block: i for i, block in marks if _WORD.search(tokens[i])}
    out = tokens[:]
    for i, block in marks:
        before = _neighbour(tokens, i, -1)
        after = _neighbour(tokens, i, 1)
        out[i] = _text(tokens[i], before, after, last=ends.get(block) == i)
    return "".join(out)


def _neighbour(tokens: list[str], i: int, step: int) -> bool:
    """Whether the text next to token `i` (across inline tags, up to a block or a space) continues a word."""
    j = i + step
    while 0 <= j < len(tokens):
        token = tokens[j]
        if token.startswith("<") and len(token) > 1:
            tag = _TAG.fullmatch(token)
            if tag and tag.group(2).lower() in {"em", "strong", "b", "i", "span", "mark", "u", "s"}:
                j += step
                continue
            return False
        if not token:
            j += step
            continue
        ch = token[-1] if step < 0 else token[0]
        return ch.isalpha()
    return False


def strip(text: str) -> str:
    """The text without its soft hyphens: for comparing, searching and exporting."""
    return text.replace(SHY, "")

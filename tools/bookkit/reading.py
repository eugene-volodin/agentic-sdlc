"""How long a chapter takes to read: the characters of its running text over a reading rate.

The reader should see what lies ahead - the map and the contents give each chapter's reading
time. Counted is what the reader reads as text: paragraphs, notes, bubbles, lists, tables and the text of prompts.
Not counted: the front matter, HTML comments, Markdown markup, and listings (code, terminals, files, trees), which
one looks over rather than reads. The rate is `design.READ_CPM`; the time is rounded to the nearest five minutes.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import design
from .config import skipped
from .markup import read_source, split_front_matter

_COMMENT = re.compile(r"<!--.*?-->", re.S)
_FENCE = re.compile(r"^(```+|~~~+)\s*([\w-]*)[^\n]*\n(.*?)^\1\s*$", re.S | re.M)
_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_TAG = re.compile(r"<[^>]+>")
_DIRECTIVE = re.compile(r"^\s*:::.*$", re.M)                 # the fences of notes, bubbles, steps
_RULE = re.compile(r"^\s*\|?\s*:?-{3,}.*$", re.M)            # a table's header rule
_MARKS = re.compile(r"^\s{0,3}(#{1,6}|>|[-*+]|\d+[.)])\s+", re.M)
_EMPHASIS = re.compile(r"[*`]|(?<![\w])_|_(?![\w])")    # emphasis marks, not a snake_case underscore
READ_AS_TEXT = {"prompt"}                                     # fences whose words are read like the running text


def running_text(markdown: str) -> str:
    """The words a reader reads in one Markdown file of a chapter, without markup, as plain text."""
    _, body, _ = split_front_matter(markdown)
    body = _COMMENT.sub(" ", body)
    body = _FENCE.sub(lambda m: m.group(3) if m.group(2) in READ_AS_TEXT else " ", body)
    body = _IMAGE.sub(" ", body)
    body = _LINK.sub(r"\1", body)
    body = _TAG.sub(" ", body)
    body = _DIRECTIVE.sub(" ", body)
    body = _RULE.sub(" ", body)
    body = _MARKS.sub("", body)
    body = _EMPHASIS.sub("", body).replace("|", " ")
    return re.sub(r"\s+", " ", body).strip()


def characters(path: Path) -> int:
    """The characters of running text in a chapter: a file, or a folder of files (those the build reads as its parts:
    not a README or a hidden file)."""
    files = sorted(file for file in path.glob("*.md") if not skipped(file)) if path.is_dir() else [path]
    return sum(len(running_text(read_source(file))) for file in files)


def minutes(count: int) -> int:
    """Reading minutes for `count` characters: at `design.READ_CPM`, to the nearest five, at least five."""
    return max(5, 5 * round(count / design.READ_CPM / 5))

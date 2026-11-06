"""Parsing of the book's Markdown extensions.

Two things are added on top of plain Markdown:

    ::: name [character] [flags] [key=value ...] [Title]     a design-system block
    body
    :::

    ```prompt who=cat title="..."                              a smart code fence
    ...
    ```

This module only splits text and parses the option syntax; rendering lives
in `compiler.py`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import yaml

from .art.characters import is_character, resolve

_OPTION = re.compile(r'\s*(?:(?P<key>[a-z_]+)=(?:"(?P<quoted>[^"]*)"|(?P<value>\S+))|(?P<word>\S+))')
_FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})(.*)$")
_OPEN = re.compile(r"^:::\s*(\S.*)$")
_FRONT_MATTER = re.compile(r"\A---[ \t]*\n(?:(.*?)\n)?---[ \t]*(?:\n|\Z)", re.S)


class BuildError(Exception):
    """A problem in the book's source that the author has to fix."""


def yaml_problem(error: Exception, first_line: int = 1) -> str:
    """A YAML error as one line: where and what, without the parser's drawing of the spot."""
    mark = getattr(error, "problem_mark", None)
    where = f"line {first_line + mark.line}: " if mark is not None else ""
    what = getattr(error, "problem", None) or str(error).split("\n")[0]
    context = getattr(error, "context", None)
    return f"{where}not valid YAML: {what}" + (f" ({context})" if context else "")


def read_source(path) -> str:
    """The text of one of the author's files; anything but UTF-8 text is an error naming the file and the line."""
    try:
        data = path.read_bytes()
    except OSError as error:
        raise BuildError(f"{path}: cannot be read: {error.strerror or error}") from error
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        line = data[:error.start].count(b"\n") + 1
        raise BuildError(f"{path.name}: line {line}: not UTF-8 text (byte 0x{data[error.start]:02x}); "
                         f"save the file as UTF-8") from None


@dataclass
class Segment:
    """A run of plain Markdown or one `:::` block."""

    kind: str                 # "markdown" or "directive"
    line: int                 # 1-based line where the segment starts
    text: str                 # Markdown source, or the body of the directive
    head: str = ""            # everything after ":::" on the opening line


@dataclass
class Head:
    """Parsed opening line of a block or info string of a fence."""

    who: str | None = None
    options: dict = field(default_factory=dict)
    title: str = ""


def parse_head(text: str, flags: frozenset[str] | set[str] = frozenset(), allow_who: bool = True) -> Head:
    """Parse `cat right pose=think Title text` into its parts.

    Options are read from the left; the first word that is not a character,
    one of `flags` or `key=value` starts the title, and the title is kept verbatim.
    `flags` are the bare words the component at hand understands, so a title may
    freely begin with a word that is a flag of some other component.
    """
    head = Head()
    position = 0
    while True:
        match = _OPTION.match(text, position)
        if not match:
            break
        if match.group("key"):
            quoted = match.group("quoted")
            head.options[match.group("key")] = quoted if quoted is not None else match.group("value")
        else:
            word = match.group("word")
            if word in flags:
                head.options[word] = True
            elif allow_who and head.who is None and is_character(word):
                head.who = resolve(word)
            else:
                break
        position = match.end()
    head.title = text[position:].strip()
    if "who" in head.options:
        head.who = resolve(head.options.pop("who"))
    return head


class FenceTracker:
    """Tracks whether the scanner is inside a fenced code block."""

    def __init__(self) -> None:
        self.marker: str | None = None
        self.opened = 0              # the 0-based number of the line that opened the fence now open
        self.count = 0               # lines fed so far

    def feed(self, line: str) -> bool:
        """Consume a line; return True if it is part of a fence (delimiter or content)."""
        match = _FENCE.match(line)
        self.count += 1
        if self.marker is None:
            if match:
                self.marker = match.group(1)
                self.opened = self.count - 1
                return True
            return False
        if match and match.group(1)[0] == self.marker[0] and len(match.group(1)) >= len(self.marker) \
                and not match.group(2).strip():
            self.marker = None
        return True


def split_segments(text: str, first_line: int = 1) -> list[Segment]:
    """Split source into Markdown runs and `:::` blocks, ignoring `:::` inside code fences."""
    lines = text.split("\n")
    segments: list[Segment] = []
    buffer: list[str] = []
    buffer_line = first_line
    fence = FenceTracker()
    i = 0
    while i < len(lines):
        line = lines[i]
        opening = None if fence.feed(line) else _OPEN.match(line)
        if not opening and fence.marker is None and line.strip() == ":::":
            raise BuildError(f"line {first_line + i}: ':::' closes no block; remove it or open one with '::: name'")
        if not opening:
            if not buffer:
                buffer_line = first_line + i
            buffer.append(line)
            i += 1
            continue
        if buffer:
            segments.append(Segment("markdown", buffer_line, "\n".join(buffer)))
            buffer = []
        start = i
        body: list[str] = []
        depth = 1
        inner = FenceTracker()
        i += 1
        while i < len(lines):
            current = lines[i]
            if not inner.feed(current):
                if _OPEN.match(current):
                    depth += 1
                elif current.strip() == ":::":
                    depth -= 1
                    if depth == 0:
                        break
            body.append(current)
            i += 1
        else:
            raise BuildError(f"line {first_line + start}: block '::: {opening.group(1)}' is never closed with ':::'")
        segments.append(Segment("directive", first_line + start, "\n".join(body), opening.group(1).strip()))
        i += 1
    if fence.marker is not None:
        raise BuildError(f"line {first_line + fence.opened}: the code block opened with "
                         f"'{lines[fence.opened].strip()}' is never closed with '{fence.marker}'")
    if buffer:
        segments.append(Segment("markdown", buffer_line, "\n".join(buffer)))
    return segments


def split_front_matter(text: str) -> tuple[dict, str, int]:
    """Return `(metadata, body, line number of the first body line)`."""
    text = text.replace("\r\n", "\n").lstrip("\ufeff")
    match = _FRONT_MATTER.match(text)
    if not match:
        if re.match(r"---[ \t]*\n", text):
            raise BuildError("line 1: the front matter is never closed with a line '---'")
        return {}, text, 1
    try:
        meta = yaml.safe_load(match.group(1) or "") or {}
    except yaml.YAMLError as error:
        raise BuildError(f"front matter: {yaml_problem(error, 2)}") from error
    if not isinstance(meta, dict):
        raise BuildError("front matter must be a mapping of keys to values")
    return meta, text[match.end():], text[:match.end()].count("\n") + 1

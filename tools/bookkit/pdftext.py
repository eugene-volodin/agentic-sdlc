"""The PDF's text layer without the soft hyphens of running text.

Chrome prints every soft hyphen (U+00AD, hyphenate.py) that did not break a line as an invisible glyph of zero
advance, marked with `/ActualText <FEFF00AD>`: the copied and searched text then holds a soft hyphen inside every
long word, and a viewer's search for a word misses it. A hyphen that did break a line is printed as a glyph of its own
(`/ActualText <FEFF2010>`) and stays. This pass drops those invisible glyphs - only the glyph and its marked span,
the move to its place stays, so every glyph after it keeps its position - takes U+00AD out of any other replacement
text (a ligature drawn across a soft hyphen), and writes the cross-reference table anew.

It reads the PDF Chrome (Skia) writes: a classic cross-reference table, content streams compressed with Flate and a
direct /Length. Anything else is a BuildError naming what was not found, never a silent skip.
"""
from __future__ import annotations

import re
import zlib

from .markup import BuildError

# A soft hyphen's span: `/Span<</ActualText <FEFF00AD> >> BDC`, an optional move, one glyph shown, `EMC`.
_SPAN = re.compile(rb"/Span\s*<<\s*/ActualText\s*<FEFF00AD>\s*>>\s*BDC\s+(?:([-+\d.]+\s+[-+\d.]+\s+Td)\s+)?"
                   rb"<[0-9A-Fa-f]+>\s*Tj\s+EMC\s+")
# Any other replacement text with a soft hyphen in it: a ligature drawn across one (`f` + U+00AD + `i`).
_ACTUAL = re.compile(rb"/ActualText\s*<FEFF((?:[0-9A-Fa-f]{4})*)>")
_SOFT = re.compile(rb"00[Aa][Dd]")
_STARTXREF = re.compile(rb"startxref\s+(\d+)\s+%%EOF\s*$")
_SUBSECTION = re.compile(rb"(\d+) (\d+)\s*\r?\n")
_ENTRY = re.compile(rb"(\d{10}) (\d{5}) ([nf])")
_HEAD = re.compile(rb"\d+ \d+ obj\s*<<")
_LENGTH = re.compile(rb"/Length (\d+)")


def strip_soft_hyphens(data: bytes, name: str = "the PDF") -> tuple[bytes, int]:
    """The PDF without the invisible glyphs of its soft hyphens, and how many were dropped."""
    tail = _STARTXREF.search(data, max(0, len(data) - 64))
    if not tail:
        raise BuildError(f"{name}: no startxref at the end of the file; cannot take the soft hyphens out of its text")
    xref = int(tail.group(1))
    if not data.startswith(b"xref", xref):
        raise BuildError(f"{name}: no cross-reference table at offset {xref} (a cross-reference stream is not "
                         f"supported); cannot take the soft hyphens out of its text")
    trailer = data.find(b"trailer", xref)
    if trailer < 0:
        raise BuildError(f"{name}: no trailer after the cross-reference table")
    sections = []                               # (first object number, [(offset, generation, kind)])
    at = xref + len(b"xref")
    while True:
        while data[at:at + 1] in (b" ", b"\r", b"\n"):
            at += 1
        if at >= trailer:
            break
        head = _SUBSECTION.match(data, at)
        if not head:
            raise BuildError(f"{name}: a malformed cross-reference table at offset {at}")
        first, count = int(head.group(1)), int(head.group(2))
        at = head.end()
        entries = []
        for _ in range(count):
            entry = _ENTRY.match(data, at)
            if not entry:
                raise BuildError(f"{name}: a malformed cross-reference entry at offset {at}")
            entries.append((int(entry.group(1)), int(entry.group(2)), entry.group(3)))
            at = entry.end()
            while data[at:at + 1] in (b" ", b"\r", b"\n"):
                at += 1
        sections.append((first, entries))

    # The objects in file order; each runs to the next one, the last to the table.
    starts = sorted({offset for _, entries in sections for offset, _, kind in entries if kind == b"n"})
    ends = starts[1:] + [xref]
    out = [data[:starts[0]]] if starts else [data[:xref]]
    moved: dict[int, int] = {}
    position = len(out[0])
    dropped = 0
    for start, end in zip(starts, ends, strict=True):
        body = data[start:end]
        if b"/FlateDecode" in body[:200]:
            body, count = _object(body, name, start)
            dropped += count
        moved[start] = position
        out.append(body)
        position += len(body)
    if not dropped:
        return data, 0
    table = [b"xref\n"]
    for first, entries in sections:
        table.append(b"%d %d\n" % (first, len(entries)))
        for offset, generation, kind in entries:
            offset = moved[offset] if kind == b"n" else offset
            table.append(b"%010d %05d %s \n" % (offset, generation, kind))
    out.append(b"".join(table))
    out.append(data[trailer:tail.start()])
    out.append(b"startxref\n%d\n%%%%EOF\n" % position)
    return b"".join(out), dropped


def _object(body: bytes, name: str, offset: int) -> tuple[bytes, int]:
    """One object: if it is a Flate stream whose content shows soft hyphens, the same object without them."""
    head = _HEAD.match(body)
    marker = body.find(b"stream", head.end()) if head else -1
    if not head or marker < 0:
        return body, 0
    dictionary = body[:marker]
    if b"/FlateDecode" not in dictionary or b"/Subtype" in dictionary or b"/Length1" in dictionary:
        return body, 0                          # an image or a font: no text is shown there
    length = _LENGTH.search(dictionary)
    if not length:
        raise BuildError(f"{name}: a compressed stream without a direct /Length at offset {offset}")
    begin = marker + len(b"stream")
    begin += 2 if body[begin:begin + 2] == b"\r\n" else 1
    size = int(length.group(1))
    try:
        content = zlib.decompress(body[begin:begin + size])
    except zlib.error:
        return body, 0                          # not a content stream this pass understands: a font, an image
    if not _SOFT.search(content):
        return body, 0
    content, count = _SPAN.subn(lambda match: match.group(1) + b"\n" if match.group(1) else b"", content)
    changed = [0]

    def without(match: re.Match) -> bytes:
        quads = [match.group(1)[i:i + 4] for i in range(0, len(match.group(1)), 4)]
        kept = [quad for quad in quads if quad.upper() != b"00AD"]
        changed[0] += len(quads) - len(kept)
        return b"/ActualText <FEFF" + b"".join(kept) + b">"

    content = _ACTUAL.sub(without, content)
    count += changed[0]
    if not count:
        return body, 0
    packed = zlib.compress(content, 9)
    dictionary = dictionary[:length.start(1)] + str(len(packed)).encode() + dictionary[length.end(1):]
    return dictionary + body[marker:begin] + packed + body[begin + size:], count

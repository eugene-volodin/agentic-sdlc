"""Hyphenation at build time (hyphenate.py) and the PDF's text without soft hyphens (pdftext.py): the same break
points on every machine, only in running text, and never in the text a reader copies or searches."""
import zlib
from pathlib import Path

import pytest
import yaml

from bookkit.hyphenate import SHY, hyphenate, strip, word
from bookkit.markup import BuildError
from bookkit.pdftext import strip_soft_hyphens

CASES = yaml.safe_load((Path(__file__).parent / "fixtures" / "hyphenation.yml").read_text(encoding="utf-8"))


def shown(html: str) -> str:
    return html.replace(SHY, "|")


def test_a_word_gets_its_break_points_from_the_dictionary_and_a_short_one_none():
    assert shown(word(CASES["word"])) == CASES["word_hyphenated"]
    assert word(CASES["short"]) == CASES["short"]
    assert shown(word("repository")) == "repos|i|to|ry"


def test_names_acronyms_and_technical_words_stay_whole():
    for whole in ("GitHub", "AGENTS", "OpenAI"):
        assert word(whole) == whole
    html = "<p>see example.com/docs, AGENTS.md, snake_case, v2beta, @someone and GitHub</p>"
    assert hyphenate(html) == html


def test_running_text_is_hyphenated_and_its_last_word_stays_whole():
    assert shown(hyphenate(CASES["paragraph"])) == CASES["paragraph_hyphenated"]
    assert shown(hyphenate("<ul><li>a structured repository</li></ul>")) == "<ul><li>a struc|tured repository</li></ul>"


def test_a_word_split_by_markup_is_left_whole():
    assert shown(hyphenate(CASES["split_word"])) == CASES["split_word_hyphenated"]


@pytest.mark.parametrize("html", [
    "<p><code>configuration</code> x</p>",
    "<p><a href='#x'>documentation</a> x</p>",
    "<p><kbd>Backspace</kbd> x</p>",
    "<h2>documentation documentation</h2>",
    "<div class='bubble'><p>documentation documentation</p></div>",
    "<div class='note'><p>documentation documentation</p></div>",
    "<pre>documentation documentation</pre>",
    "<p><svg><text>documentation</text></svg> x</p>",
    "<div>documentation documentation</div>",
    "<p><!-- documentation documentation --> x</p>",
])
def test_code_links_headings_bubbles_notes_and_pictures_are_never_hyphenated(html):
    assert hyphenate(html) == html


def test_markup_and_entities_pass_through_unchanged():
    html = '<p class="lead" data-x="documentation">one &laquo;documentation&raquo; &amp; <br>more<wbr> text</p>'
    assert strip(hyphenate(html)) == html
    assert "doc" + SHY in hyphenate(html)


def pdf(content: bytes) -> bytes:
    """A minimal PDF in the shape Chrome writes: objects, a classic cross-reference table, a trailer."""
    packed = zlib.compress(content)
    objects = [b"<</Type /Catalog /Pages 2 0 R>>", b"<</Type /Pages /Kids [] /Count 0>>",
               b"<</Filter /FlateDecode\n/Length %d>> stream\n" % len(packed) + packed + b"\nendstream"]
    out, offsets = [b"%PDF-1.4\n"], []
    for number, body in enumerate(objects, 1):
        offsets.append(sum(map(len, out)))
        out.append(b"%d 0 obj\n" % number + body + b"\nendobj\n")
    xref = sum(map(len, out))
    out.append(b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1))
    out += [b"%010d 00000 n \n" % offset for offset in offsets]
    out.append(b"trailer\n<</Size %d /Root 1 0 R>>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref))
    return b"".join(out)


def streams(data: bytes) -> list[bytes]:
    found, at = [], 0
    while (at := data.find(b"stream\n", at)) >= 0:
        end = data.find(b"\nendstream", at)
        found.append(zlib.decompress(data[at + 7:end]))
        at = end + len(b"\nendstream")
    return found


def test_the_pdf_loses_its_invisible_soft_hyphens_and_keeps_every_position():
    content = (b"BT\n<0010> Tj\n/Span<</ActualText <FEFF00AD> >> BDC\n7.5 0 Td <0003> Tj\nEMC\n0 0 Td <0011> Tj\n"
               b"/Span<</ActualText <FEFF006600AD0069> >> BDC\n3 0 Td <02CB> Tj\nEMC\n"
               b"/Span<</ActualText <FEFF2010> >> BDC\n<0012> Tj\nEMC\nET")
    cleaned, dropped = strip_soft_hyphens(pdf(content))
    assert dropped == 2
    text = streams(cleaned)[0]
    assert b"00AD" not in text and b"7.5 0 Td\n0 0 Td <0011> Tj" in text
    assert b"<FEFF00660069>" in text and b"<FEFF2010>" in text            # a breaking hyphen stays
    # The cross-reference table points at every object where it now is.
    table = cleaned[cleaned.index(b"xref\n"):].split(b"\n")[3:6]
    for number, line in enumerate(table, 1):
        assert cleaned[int(line[:10]):].startswith(b"%d 0 obj" % number)
    assert cleaned.endswith(b"startxref\n%d\n%%%%EOF\n" % cleaned.index(b"xref\n"))


def test_a_pdf_without_soft_hyphens_is_left_as_it_is_and_a_broken_one_is_an_error():
    plain = pdf(b"BT\n<0010> Tj\nET")
    assert strip_soft_hyphens(plain) == (plain, 0)
    with pytest.raises(BuildError, match="startxref"):
        strip_soft_hyphens(b"%PDF-1.4\nnothing here")

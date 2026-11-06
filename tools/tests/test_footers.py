"""Which footer goes on which page: a chapter not given a world yet lives in the introduction's courtyard, the front
pages in the professor's yard; clean, never one moment on two pages in a row, and a chapter alone draws what it draws
in the whole book."""
import re

import yaml

from bookkit import design
from bookkit.art.footers import UNSET, footer_conflicts, footers
from bookkit.config import LOCALES

LOCALE = yaml.safe_load((LOCALES / "ru.yml").read_text(encoding="utf-8"))
VOCABULARY = {"worlds": LOCALE["worlds"], "easter": LOCALE["easter"]}
SAME = re.compile(r'(id="|url\(#|href="#)[^")]+')       # ids are numbered per build


def _requests(chapter, sizes, text="ничего особенного"):
    return [{"page": i, "chapter": chapter, "text": text, "heads": "", "mm": mm, "clear": "left" if i % 2 else "right",
             "accent": design.ORANGE} for i, mm in enumerate(sizes)]


def test_a_chapter_without_a_world_is_drawn_in_the_courtyard_clean_and_never_twice_in_a_row():
    trace: list = []
    svgs = footers(_requests("4", (34, 55, 55, 34, 90, 34, 120)), VOCABULARY, trace)
    assert all(svg.startswith("<svg") for svg in svgs)
    assert {moment["world"] for moment in trace} == {UNSET} and trace[-1]["station"] is None   # ends on the finale
    for moment in trace:
        assert footer_conflicts(moment["strip"]) == [], (moment["station"], moment["beat"])
    shown = [(moment["station"], moment["beat"]) for moment in trace]
    assert all(a != b for a, b in zip(shown, shown[1:], strict=False)), shown


def test_a_front_page_shows_the_moment_its_text_names():
    pages = LOCALE["worlds"]["front"]["pages"]
    phrase, station = next(iter(pages.items()))
    trace: list = []
    footers([{"chapter": "Кто автор", "text": f"… {phrase} …", "heads": "", "mm": 55, "clear": "right"}],
             VOCABULARY, trace)
    assert trace[0]["world"] == "front" and trace[0]["station"] == station


def test_a_chapter_without_a_world_alone_draws_what_it_draws_in_the_whole_book():
    """`--only` builds one chapter: its footers must not depend on the pages before it."""
    alone = _requests("5", (55, 34, 120, 55))
    before = _requests("Кто автор", (55,)) + _requests("4", (34, 55))
    together = footers(before + alone, VOCABULARY)[len(before):]
    assert [SAME.sub("", svg) for svg in together] == [SAME.sub("", svg) for svg in footers(alone, VOCABULARY)]


def test_a_page_without_a_world_draws_without_the_locale():
    trace: list = []
    assert footers(_requests("1", (34, 160)), {}, trace)[0].startswith("<svg")
    assert all(footer_conflicts(moment["strip"]) == [] for moment in trace)


def test_lettering_shrunk_on_the_page_is_set_flat():
    from bookkit.art.ink import lettering, settle_lettering
    sign = lettering(0, 0, "Sign", 20, "#ff0000")
    assert settle_lettering(f'<g transform="scale(1)">{sign}</g>').count("<text") == 2     # rim and extrusion
    shrunk = settle_lettering(f'<g transform="translate(5,5) scale(0.5)">{sign}</g>')
    assert shrunk.count("<text") == 1 and "stroke" not in shrunk and 'fill="#ff0000"' in shrunk

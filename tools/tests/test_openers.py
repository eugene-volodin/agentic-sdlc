"""Story openers: every picture draws, nothing in it overlaps, nothing reaches under the title or the bubble."""
from pathlib import Path

import re

import pytest
import yaml

from bookkit import design
from bookkit.art import worlds  # noqa: F401 - registers the worlds' openers
from bookkit.art.openers import OPENERS, TITLE_ZONE, Stage, conflicts
from bookkit.art.openers import opener as draw_opener
from bookkit.compiler import build_html
from bookkit.config import LOCALES

WORDS = yaml.safe_load((LOCALES / "ru.yml").read_text(encoding="utf-8"))["openers"]


def opener(name, accent, **options):
    return draw_opener(name, accent, words=WORDS.get(name), **options)


@pytest.mark.parametrize("name", list(OPENERS))
@pytest.mark.parametrize("lead_chars", [60, 140, 190])
def test_every_opener_is_composed_without_overlaps(name, lead_chars):
    for accent in design.ACCENTS.values():
        result = opener(name, accent, lead_chars=lead_chars)
        assert result.svg.startswith("<svg") and 'viewBox="0 0 840 1188"' in result.svg
        assert conflicts(result) == [], (name, lead_chars)


@pytest.mark.parametrize("name", list(OPENERS))
def test_the_professor_stands_under_his_bubble(name):
    result = opener(name, design.PINK)
    left, bottom, width, tail = result.bubble
    assert 0 < tail < width and left >= 8 and left + width <= design.PAGE_WIDTH - 8
    professor = next(box for box in result.boxes if box.name == "professor")
    head = (professor.left + professor.right) / 2 / (840 / design.PAGE_WIDTH)
    assert abs(left + tail - head) < 1          # the tail points at his head
    assert design.PAGE_HEIGHT - bottom < professor.top / (840 / design.PAGE_WIDTH)   # and the bubble is above it


def test_the_checker_catches_what_it_should():
    s = Stage()
    s.put(1, "", (100, 100, 200, 200), "a")
    s.put(1, "", (150, 150, 250, 250), "b")
    s.put(1, "", (300, 300, 400, 400), "c", group="c")
    s.put(1, "", (320, 320, 380, 380), "d", group="c")        # one group: they belong together
    box = s.actor("professor", 700, 1000)
    s.speaker(box)
    result = s.render()
    found = conflicts(result)
    assert "a overlaps b" in found and not any("c overlaps" in line for line in found)
    assert any(line.startswith("a reaches into a reserved area") for line in found)   # under the title
    assert TITLE_ZONE in result.reserved


def test_a_story_opener_has_a_drawn_title_and_no_numeral(tmp_path: Path):
    (tmp_path / "book.yml").write_text("title: T\n", encoding="utf-8")
    (tmp_path / "01-a.md").write_text("---\ncolor: coral\nscene: morning\nlead: Words `<in>` the bubble\n---\n"
                                      "# Why & `how`\n\ntext\n", encoding="utf-8")
    html = build_html(tmp_path).html
    assert 'class="fullpage opener story"' in html and '<div class="opener-big">' not in html
    assert 'class="opener-lettering"' in html and 'aria-label="Why &amp; how"' in html   # drawn, its text escaped
    assert html.count('class="art-box"') > 10
    assert "&lt;in&gt;" in html and "<in>" not in html


@pytest.mark.parametrize("name", list(OPENERS))
def test_every_word_drawn_comes_from_the_locale(name):
    """An opener that letters anything asks the locale for it; one that letters nothing (the fair) draws no text."""
    try:
        drawn = draw_opener(name, design.PINK, words={})
    except KeyError as error:
        assert "openers:" in str(error)
    else:
        assert "<text" not in drawn.svg, name


def test_an_unknown_scene_lists_the_stories(tmp_path: Path):
    from bookkit.markup import BuildError
    (tmp_path / "book.yml").write_text("title: T\n", encoding="utf-8")
    (tmp_path / "01-a.md").write_text("---\nscene: moon\n---\n# A\n", encoding="utf-8")
    with pytest.raises(BuildError, match="morning"):
        build_html(tmp_path)


def test_the_title_is_ink_on_paper_plates_with_no_letter_set_apart():
    from bookkit import title
    drawn = title.draw("AGENTS.md: что записать для агента и куда")
    plates = re.findall(r'<rect x="0" y="[\d.]+" width="([\d.]+)"', drawn.svg)
    assert plates and all(float(w) <= title.WIDTH for w in plates)
    assert design.WHITE not in drawn.svg and "Gradient" not in drawn.svg


def test_long_titles_are_broken_into_even_lines():
    from bookkit import title
    rows = title.break_lines("one two three four five six seven", 150, 2)
    assert rows and len(rows) == 2 and all(title.advance(r, title.SIZE) <= 150 for r in rows)


WORLD_OPENERS = ("kitchen", "fairground", "station", "reading_room", "workshop", "deepsea", "laboratory", "lighthouse",
                 "lunar_base", "forest_camp", "railway", "city_road")
CLEAR = 4 * 840 / design.PAGE_WIDTH            # 4 mm of air, in picture units


@pytest.mark.parametrize("name", WORLD_OPENERS)
@pytest.mark.parametrize("lead_chars", [60, 140, 190])
def test_the_bubble_keeps_clear_of_every_edge_under_it(name, lead_chars):
    """The professor's bubble never sits on a window frame, a post or a rail: 4 mm of air from every structural
    edge the opener declares and from every thing placed in it."""
    result = opener(name, design.PINK, lead_chars=lead_chars)
    assert result.edges, f"{name} declares no edges to keep clear of"
    l_, t_, r_, b_ = result.bubble_box
    things = [(b.left, b.top, b.right, b.bottom) for b in result.boxes if b.kind != "actor"]
    near = [e for e in result.edges + things if e[0] < r_ + CLEAR and e[2] > l_ - CLEAR and e[1] < b_ + CLEAR
            and e[3] > t_ - CLEAR]
    assert near == [], (name, lead_chars, [tuple(round(v) for v in e) for e in near])


def _in_use() -> list[str]:
    """The openers a chapter of the handbook or of a draft actually shows: its `scene:`, or its world's opener."""
    root = Path(__file__).resolve().parents[2]
    names = set()
    for front in root.glob("book/*/00-chapter.md"):
        meta = yaml.safe_load(front.read_text(encoding="utf-8").split("---")[1])
        if meta.get("world"):
            if worlds.WORLDS[meta["world"]].opener:          # the courtyard keeps the generic opener
                names.add(worlds.WORLDS[meta["world"]].opener)
        elif meta.get("scene") in OPENERS:
            names.add(meta["scene"])
    return sorted(names)


@pytest.mark.parametrize("name", _in_use())
def test_no_character_is_cut_by_the_page(name):
    """Every character whole inside the picture, its hands and feet too: hands are never cut off."""
    result = opener(name, design.PINK)
    margin = 2 * 840 / design.PAGE_WIDTH
    cut = [(who, tuple(round(v) for v in box)) for who, box in result.reach
           if box[0] < margin or box[2] > 840 - margin or box[1] < margin or box[3] > 1188 - margin]
    assert cut == [], name


def test_the_farewell_is_composed_without_overlaps_and_no_one_is_cut():
    """The last page: the five walk off into the computer city - nothing overlaps, every
    character whole on the page, the cable on its ports, no words drawn."""
    from bookkit.art import farewell
    from bookkit.art.world_kit import link_faults
    result = farewell.draw()
    assert result.svg.startswith("<svg") and 'viewBox="0 0 840 1188"' in result.svg and "<text" not in result.svg
    assert conflicts(result) == []
    assert link_faults(result) == [] and result.links
    who = [name for name, _ in result.reach]
    assert {"professor", "cat", "caterpillar", "sparrow"} <= set(who) and who.count("agent") >= 11   # ten at work
    ours = next(b for b in result.boxes if b.kind == "actor" and b.group == "agent")      # our agent, on the road
    workers = [b for b in result.boxes if b.kind == "actor" and b.name == "agent" and b is not ours]
    # none mistaken for ours: smaller than our agent, who walks ahead of the five up the bend, the furthest of them
    assert all(b.bottom - b.top <= (ours.bottom - ours.top) * 0.8 + 0.5 for b in workers)
    gate = next(b for b in result.boxes if b.name == "gate")
    assert all(b.top >= gate.bottom + 8 for b in result.boxes if b.name.startswith("lamp"))   # the gate stands free
    margin = 2 * 840 / design.PAGE_WIDTH
    cut = [(who, tuple(round(v) for v in box)) for who, box in result.reach
           if box[0] < margin or box[2] > 840 - margin or box[1] < margin or box[3] > 1188 - margin]
    assert cut == []


def _book(tmp_path: Path, plan: bool) -> Path:
    (tmp_path / "book.yml").write_text("title: T\ncover: false\ntoc: false\n"
                                       + ("plan:\n  - 1. A\n  - 2. B\n" if plan else ""), encoding="utf-8")
    for number, name, scene in ((1, "A", "morning"), (2, "B", "lab")):
        (tmp_path / f"0{number}-{name.lower()}.md").write_text(
            f"---\ncolor: coral\nscene: {scene}\nnumber: {number}\n---\n# {name}\n\ntext\n", encoding="utf-8")
    return tmp_path


def test_the_farewell_page_comes_after_the_last_chapter(tmp_path: Path):
    html = build_html(_book(tmp_path, plan=True)).html
    assert html.count('class="fullpage farewell"') == 1
    last = html.rindex('<section class="chapter"')
    assert html.index('class="fullpage farewell"') > html.index("</section>", last)   # after it, not inside it
    assert 'class="fullpage farewell"' not in build_html(_book(tmp_path, plan=False)).html   # a draft has none

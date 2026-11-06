"""The map of the book: it draws, every written chapter's world has its place, nothing overlaps or is cut."""
from pathlib import Path

import pytest
import yaml

from bookkit import design
from bookkit.art import bookmap
from bookkit.art.bookmap import RAILWAY, SLOTS, VIGNETTES, MapError, Stop, draw, problems
from bookkit.compiler import build_html
from bookkit.markup import BuildError

BOOK = Path(__file__).resolve().parents[2] / "book"


def _worlds() -> dict[str, tuple[str, str]]:
    """Every chapter of the handbook with a world: its number -> (world, colour)."""
    out = {}
    for path in sorted(BOOK.glob("*/00-chapter.md")):
        meta = yaml.safe_load(path.read_text(encoding="utf-8").split("---")[1]) or {}
        if meta.get("world"):
            number = path.parent.name.split("-")[0].lstrip("0")
            slot = "intro" if not number else "end" if path.parent.name.endswith("-end") else number
            out[slot] = (meta["world"], meta["color"])
    return out


TITLES = {"intro": "Введение", "end": "Заключение: чек-лист и напутствие",
          "11": "Как теперь выглядит разработка: Agentic SDLC", "4": "AGENTS.md: что записать для агента и куда"}


def _stops(written: dict[str, tuple[str, str]]) -> list[Stop]:
    slots = ["intro", *[str(i) for i in range(1, 12)], "end"]
    return [Stop(slot, "" if slot in ("intro", "end") else slot, TITLES.get(slot, "Тесты и линтеры: агент узнаёт"),
                 "≈ 25 мин" if slot in written else "",
                 design.ACCENTS[written[slot][1]] if slot in written else design.TEAL,
                 written[slot][0] if slot in written else None, slot in written) for slot in slots]


def test_every_world_of_the_handbook_has_its_vignette():
    worlds = _worlds()
    assert len(worlds) >= 9
    for number, (world, _) in worlds.items():
        if number == RAILWAY:                   # the last chapter is the railway along the bottom edge, not a stop
            assert world == "railway"
            continue
        assert world in VIGNETTES, world
        assert number in SLOTS, number


def test_the_map_draws_every_written_chapter_in_its_world():
    worlds = _worlds()
    result = draw(_stops(worlds))
    assert result.svg.startswith("<svg") and 'viewBox="0 0 840 1188"' in result.svg
    for number, (world, _) in worlds.items():
        assert result.drawn[number] == world
    assert result.drawn["intro"] == "courtyard" and result.drawn["end"] == "city"
    assert "mask" not in result.svg and "filter" not in result.svg      # the PDF stays vector


@pytest.mark.parametrize("written", [0, 3, 9])
def test_nothing_overlaps_stands_on_the_road_or_is_cut(written):
    worlds = dict(list(_worlds().items())[:written])
    assert problems(draw(_stops(worlds))) == []


def test_every_vignette_fits_its_place_in_every_colour():
    """Any world on any slot of its row would still keep clear of the road and the page's edge."""
    for world in VIGNETTES:
        for color in design.ACCENTS.values():
            stops = [Stop("4", "4", "AGENTS.md: что записать для агента и куда", "≈ 5 мин", color, world, True)]
            assert problems(draw(stops)) == [], world


def test_the_cast_walks_the_road():
    names = {box.name for box in draw(_stops({})).boxes if box.kind == "actor"}
    assert names == {"professor", "cat", "caterpillar", "sparrow", "agent"}


def test_a_chapter_with_no_place_or_an_unknown_world_is_an_error():
    with pytest.raises(MapError, match="no place for chapter 12"):
        draw([Stop("12", "12", "Ещё", "", design.TEAL, None, False)])
    with pytest.raises(MapError, match="cannot draw"):
        draw([Stop("3", "3", "MCP", "≈ 5 мин", design.TEAL, "nowhere", True)])


def test_the_map_follows_the_contents_only_with_a_plan(tmp_path: Path):
    (tmp_path / "book.yml").write_text("title: T\n", encoding="utf-8")
    (tmp_path / "01-a.md").write_text("---\ncolor: coral\n---\n# A\n\ntext\n", encoding="utf-8")
    assert 'class="fullpage bookmap"' not in build_html(tmp_path).html
    (tmp_path / "book.yml").write_text("title: T\nplan:\n  - 1. A\n  - 2. B\n", encoding="utf-8")
    html = build_html(tmp_path).html
    assert html.index('class="fullpage bookmap"') > html.index('class="chapter contents"')


def test_a_world_the_map_cannot_draw_names_the_chapter(tmp_path: Path, monkeypatch):
    (tmp_path / "book.yml").write_text("title: T\nplan:\n  - 1. A\n", encoding="utf-8")
    (tmp_path / "01-a.md").write_text("---\ncolor: coral\nworld: station\n---\n# A\n\ntext\n", encoding="utf-8")
    monkeypatch.delitem(bookmap.VIGNETTES, "station")
    with pytest.raises(BuildError, match="01-a.md"):
        build_html(tmp_path)


def test_every_plaque_carries_its_title_and_a_written_chapter_its_time():
    written = {slot: one for slot, one in _worlds().items() if slot != "end"}   # one stop still to come
    result = draw(_stops(written), soon="скоро")
    assert set(result.plaques) == {"intro", *[str(i) for i in range(1, 12)], "end"}
    assert " ".join(result.plaques["4"]) == "AGENTS.md: что записать для агента и куда"   # every word kept
    assert all(1 <= len(lines) <= 4 for lines in result.plaques.values())
    assert "≈ 25 мин" in result.svg and "СКОРО" in result.svg


def test_a_long_title_is_wrapped_never_squeezed():
    from bookkit.art.ink import lettering_width
    lines, size = bookmap.wrap("Как теперь выглядит разработка: Agentic SDLC", bookmap.PLAQUE_W - 18)
    assert " ".join(lines) == "Как теперь выглядит разработка: Agentic SDLC"
    assert all(lettering_width(line, size, "label") <= bookmap.PLAQUE_W - 18 + 0.01 for line in lines)


def test_the_time_of_a_chapter_is_on_its_plaque_and_in_the_contents(tmp_path: Path):
    (tmp_path / "book.yml").write_text("title: T\nplan:\n  - 1. A\n  - 2. B\n", encoding="utf-8")
    (tmp_path / "01-a.md").write_text("---\ncolor: coral\nworld: kitchen\n---\n# Первая\n\n" + "слово " * 3000,
                                      encoding="utf-8")
    html = build_html(tmp_path).html
    assert html.count("≈ 20 мин") == 2          # 18 000 characters at 900 a minute: in the contents and on the map

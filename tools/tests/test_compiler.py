"""Tests for the compiler: Markdown and blocks to rows, without launching a browser."""
import re
from pathlib import Path

import pytest

from bookkit.art.characters import MODULES, MOODS, figure
from bookkit.art.scenes import SCENE_KINDS, STORIES, scene
from bookkit.cli import parse_pages
from bookkit.compiler import build_html
from bookkit.markup import BuildError


def write_book(tmp_path: Path, chapters: dict[str, str], config: str = "title: Test\n") -> Path:
    (tmp_path / "book.yml").write_text(config, encoding="utf-8")
    for name, text in chapters.items():
        (tmp_path / name).write_text(text, encoding="utf-8")
    return tmp_path


def test_every_pose_and_mood_of_every_character_draws():
    for name, module in MODULES.items():
        for pose in module.POSES:
            for mood in MOODS:
                assert figure(name, pose, mood).startswith("<svg")


def test_every_scene_kind_draws_at_every_footer_height():
    for kind in SCENE_KINDS:
        for height in (136, 220, 320, 440):
            for seed in range(4):
                assert 'viewBox="0 0 840' in scene(height, seed, kind)


def test_scene_is_reproducible_apart_from_ids():
    import re

    def strip(markup: str) -> str:
        return re.sub(r'(id="|url\(#)[a-z]\d+', r"\1", markup)

    assert strip(scene(220, 7)) == strip(scene(220, 7))


def test_chapter_numbers_skip_unnumbered_chapters(tmp_path):
    content = write_book(tmp_path, {
        "00-intro.md": "---\ntitle: Intro\nnumber: false\n---\nHello.\n\n## Part\n",
        "01-first.md": "# First\n\n## One\n\ntext\n\n## Two\n",
    })
    build = build_html(content)
    assert [(c.title, c.number) for c in build.chapters] == [("Intro", None), ("First", 1)]
    assert [s.title for s in build.chapters[1].sections] == ["One", "Two"]
    assert '<span class="h-tag">1.2</span>' in build.html


def test_contents_link_to_headings(tmp_path):
    build = build_html(write_book(tmp_path, {"01-a.md": "# A\n\n## Section\n"}))
    assert 'href="#chapter-1-s1"' in build.html and 'id="chapter-1-s1"' in build.html
    assert 'data-ref="chapter-1"' in build.html and 'id="chapter-1"' in build.html


def test_note_attaches_to_the_next_block_with_a_margin(tmp_path):
    text = "# A\n\n::: note\nmargin text\n:::\n\n## Heading\n\nParagraph.\n"
    build = build_html(write_book(tmp_path, {"01-a.md": text}))
    rows = build.chapters[0].rows
    assert "margin text" not in rows[0].side          # the heading has no margin
    assert "margin text" in rows[1].side


def test_prompts_are_collected_verbatim(tmp_path):
    text = '# A\n\n```prompt title="First skill"\nDo it.\n  - keep indent\n{{stack}}\n```\n'
    build = build_html(write_book(tmp_path, {"01-a.md": text}))
    assert [(p.title, p.text) for p in build.prompts] == [("First skill", "Do it.\n  - keep indent\n{{stack}}\n")]
    assert '<span class="pr-var">{{stack}}</span>' in build.html


def test_a_prompt_can_go_without_a_hint(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    plain = build_html(write_book(tmp_path / "a", {"01-a.md": "# A\n\n```prompt\nDo it.\n```\n"}))
    bare = build_html(write_book(tmp_path / "b", {"01-a.md": '# A\n\n```prompt note="-"\nDo it.\n```\n'}))
    assert bare.html.count('class="prompt"') == 1
    assert len(bare.html) < len(plain.html)
    assert ">-<" not in bare.html


def test_only_uppercase_brackets_are_placeholders(tmp_path):
    text = "# A\n\n```prompt\n[INSERT NAME] and [a link](x)\n```\n"
    build = build_html(write_book(tmp_path, {"01-a.md": text}))
    assert '<span class="pr-var">[INSERT NAME]</span>' in build.html
    assert '<span class="pr-var">[a link]' not in build.html


def test_a_number_in_groups_of_three_never_breaks(tmp_path):
    text = "# A\n\n| Card | Cores |\n|---|---|\n| One | 21 760 |\n\nIn 2026 100 teams, 1 234 567 lines.\n"
    html = build_html(write_book(tmp_path, {"01-a.md": text})).html
    assert "21\u00a0760" in html and "1\u00a0234\u00a0567" in html and "\u00a0100 teams" not in html


def test_short_words_are_glued_but_code_is_untouched(tmp_path):
    config = "title: Test\nstrings:\n  typography:\n    short_words: [a, in, to]\n"
    text = "# A\n\nHe went in a hurry to town and typed `go to town`.\n"
    build = build_html(write_book(tmp_path, {"01-a.md": text}, config))
    assert "in\u00a0a\u00a0hurry to\u00a0town" in build.html
    assert '<code class="words">go to town</code>' in build.html


def test_dialog_alternates_sides_by_speaker(tmp_path):
    text = "# A\n\n::: dialog\ncat: One\nsparrow (worry): Two\ncat: Three\n:::\n"
    rows = build_html(write_book(tmp_path, {"01-a.md": text})).chapters[0].rows
    assert ["say-right" in r.main for r in rows] == [False, True, False]


def test_relative_images_resolve_against_the_chapter(tmp_path):
    (tmp_path / "pic.png").write_bytes(b"\x89PNG\r\n")
    build = build_html(write_book(tmp_path, {"01-a.md": '# A\n\n![Alt](pic.png "Caption")\n'}))
    assert (tmp_path / "pic.png").resolve().as_uri() in build.html
    assert "<figcaption>Caption</figcaption>" in build.html


def test_missing_image_is_reported_with_file_and_line(tmp_path):
    with pytest.raises(BuildError, match=r"01-a.md: line 3: image not found: missing.png"):
        build_html(write_book(tmp_path, {"01-a.md": "# A\n\n![x](missing.png)\n"}))


@pytest.mark.parametrize("front, expected", [
    ("colour: pink", "unknown key(s) colour"),
    ("color: beige", "unknown color"),
    ("side: up", "side must be one of"),
    ("scene: moon", "unknown scene"),
    ("who: dragon", "unknown character"),
    ("who: cat\npose: fly", "cat has no pose 'fly'"),
    ("cast: cat", "cast must be a list"),
    ("cast: [\"cat:fly\"]", "cat has no pose 'fly'"),
    ("cast: [a, b, c, d]", "at most 3"),
])
def test_front_matter_is_validated(tmp_path, front, expected):
    with pytest.raises(BuildError) as error:
        build_html(write_book(tmp_path, {"01-a.md": f"---\n{front}\n---\n# A\n"}))
    assert expected in str(error.value) and str(error.value).startswith("01-a.md: front matter: ")


def test_book_yml_keys_are_validated(tmp_path):
    with pytest.raises(BuildError, match="unknown key"):
        build_html(write_book(tmp_path, {"01-a.md": "# A\n"}, "titel: Oops\n"))


def test_missing_chapters_are_reported(tmp_path):
    with pytest.raises(BuildError, match="no chapters"):
        build_html(write_book(tmp_path, {}))
    with pytest.raises(BuildError, match="do not exist"):
        build_html(write_book(tmp_path, {}, "title: T\nchapters: [nope.md]\n"))


def test_only_filter_keeps_numbering_and_skips_front_pages(tmp_path):
    content = write_book(tmp_path, {"01-a.md": "# A\n", "02-b.md": "# B\n\n## S\n"})
    build = build_html(content, only="02")
    assert [c.number for c in build.chapters] == [2]
    assert 'class="fullpage cover"' not in build.html


def test_parse_pages():
    assert parse_pages("1,3-5") == [1, 3, 4, 5]
    assert parse_pages("all") is None and parse_pages(None) is None
    with pytest.raises(BuildError):
        parse_pages("one")


def test_quote_options_are_not_taken_for_the_title(tmp_path):
    text = "# A\n\n::: quote sparrow left pose=shrug Somebody\nWords.\n:::\n"
    row = build_html(write_book(tmp_path, {"01-a.md": text})).chapters[0].rows[0]
    assert "q-right" not in row.main and "<cite>Somebody</cite>" in row.main


def test_scene_marks_and_story_props(tmp_path):
    for seed in range(len(STORIES)):
        for height in (136, 220, 320, 440):
            assert scene(height, seed).startswith("<svg")
    drawn = scene(220, 0, "meadow", cast="agent:shrug:worry:?", prop=("crate", "MCP"))
    faces = re.findall(r"<text(?![^>]*translate\()[^>]*>MCP</text>", drawn)    # the extrusion is a second layer
    assert len(faces) == 1
    with pytest.raises(ValueError, match="unknown mark"):
        scene(220, 0, "meadow", cast="agent:stand:smile:zzz")


def test_first_word_of_a_chapter_becomes_a_sticker(tmp_path):
    text = "# A\n\nThis guide is free. Really.\n\nNext.\n"
    rows = build_html(write_book(tmp_path, {"01-a.md": text})).chapters[0].rows
    assert rows[0].main.startswith('<p><span class="lead-in">This</span> guide')
    assert "lead-in" not in rows[1].main
    rows = build_html(write_book(tmp_path, {"01-a.md": "# A\n\nI am short, so I take a friend.\n"})).chapters[0].rows
    assert '<span class="lead-in">I am</span>' in rows[0].main
    rows = build_html(write_book(tmp_path, {"01-a.md": "# A\n\n`code` first.\n"})).chapters[0].rows
    assert "lead-in" not in rows[0].main


def test_every_doodle_draws_and_accents_exist():
    from bookkit.art.doodles import DOODLES, doodle
    from bookkit.pages import ACCENTS

    assert len(DOODLES) >= 40
    for name in DOODLES:
        assert doodle(name).startswith("<svg")
    assert all(item in DOODLES for item in ACCENTS if isinstance(item, str))
    with pytest.raises(ValueError, match="unknown doodle"):
        doodle("teapot")


def test_inline_extras_never_touch_code(tmp_path):
    text = ("# A\n\nPress [[Ctrl+C]] and ==mark this==, but `[[x]]` and `a == b and c == d` stay.\n\n"
            "```python\nif a == b and c == d:\n    x = [[1]]\n```\n\n"
            "::: tip\n```python\nok = a == b or c == d\n```\n:::\n")
    html = "".join(row.main for row in build_html(write_book(tmp_path, {"01-a.md": text})).chapters[0].rows)
    assert "<kbd>Ctrl+C</kbd>" in html and "<mark>mark this</mark>" in html
    assert html.count("<mark>") == 1 and html.count("<kbd>") == 1
    assert "<code>[[x]]</code>" in html and '<code class="words">a == b and c == d</code>' in html


def test_rotations_restart_with_each_chapter(tmp_path):
    quotes = "# T\n\n" + "::: quote\nx\n:::\n\n" * 3
    content = write_book(tmp_path, {"01-a.md": quotes, "02-b.md": quotes})
    alone = build_html(content, only="02").chapters[0].rows
    together = build_html(content).chapters[1].rows
    assert [(r.wide, "q-right" in r.main, "char-professor" in r.main) for r in alone] == \
           [(r.wide, "q-right" in r.main, "char-professor" in r.main) for r in together]


def test_prompt_files_are_unique_across_numbered_and_unnumbered_chapters(tmp_path):
    from bookkit.cli import export_prompts

    fence = "\n\n```prompt\nDo it.\n```\n"
    content = write_book(tmp_path, {"01-intro.md": "---\nnumber: false\n---\n# I" + fence,
                                    "02-first.md": "# F" + fence, "03-second.md": "# S" + fence})
    out = tmp_path / "out"
    assert export_prompts(build_html(content), out) == 3
    assert sorted(p.name for p in out.glob("0*.md")) == ["01-01.md", "02-01.md", "03-01.md"]


def test_a_chapter_may_state_its_own_number(tmp_path):
    content = write_book(tmp_path, {"02-b.md": "---\nnumber: 2\n---\n# B\n\nText.\n", "03-c.md": "# C\n\nText.\n"})
    assert [chapter.number for chapter in build_html(content).chapters] == [2, 3]


def test_punctuation_after_the_sticker_goes_inside_it(tmp_path):
    content = write_book(tmp_path, {"01-a.md": "# A\n\nДопустим, у вас есть репозиторий.\n"})
    html = build_html(content).chapters[0].rows[0].main
    assert '<span class="lead-in">Допустим,</span>' in html


def test_every_accent_has_a_rule_in_the_stylesheet():
    from bookkit import design

    css = design.css_variables()
    for name in design.ACCENTS:
        assert f'[data-color="{name}"] {{ --accent: var(--chapter-{name}); }}' in css, name
        assert f"--chapter-{name}: {design.ACCENTS[name]};" in css, name


def test_the_chapter_colours_read_apart_and_carry_ink_text():
    """Thirteen colours, no two alike and ink text readable on each."""
    from bookkit import design

    def lum(hx: str) -> float:
        rgb = [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        r, g, b = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in rgb]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    colours = list(design.ACCENTS.values())
    assert len(colours) == len(set(colours)) >= 13
    for value in colours:
        assert (lum(value) + 0.05) / (lum(design.INK) + 0.05) >= 4.5, value

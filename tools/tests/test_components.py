"""Tests for the component library: the registry, option validation and every component's example."""
from pathlib import Path

import pytest

from bookkit.art.characters import MODULES, MOODS
from bookkit.compiler import build_html
from bookkit.components import BLOCKS, FENCES, reference
from bookkit.components.base import ANY_CHARACTER, Choice, Flag, Number
from bookkit.markup import BuildError

CSS = "".join(path.read_text(encoding="utf-8")
              for path in (Path(__file__).resolve().parent.parent / "bookkit" / "theme" / "css").glob("*.css"))


def compile_chapter(tmp_path: Path, text: str):
    (tmp_path / "book.yml").write_text("title: Test\nrepo: https://github.com/owner/name\nversion: 1.2-10.2026\n",
                                       encoding="utf-8")
    (tmp_path / "01-a.md").write_text("# A\n\n" + text, encoding="utf-8")
    return build_html(tmp_path).chapters[0]


def specs():
    return [spec for table in (BLOCKS, FENCES) for name, spec in table.items() if name == spec.name]


def test_every_component_is_documented():
    for spec in specs():
        assert spec.summary and spec.summary[0].isupper(), f"{spec.name}: docstring must describe the component"
        assert spec.example, f"{spec.name}: needs an example"


@pytest.mark.parametrize("spec", specs(), ids=lambda spec: f"{spec.kind}-{spec.name}")
def test_every_example_compiles(tmp_path, spec):
    chapter = compile_chapter(tmp_path, "Paragraph before.\n\n" + spec.example + "\n\nParagraph after.\n")
    assert len(chapter.rows) >= 2


def test_reference_lists_every_component_and_option():
    text = reference()
    for spec in specs():
        assert f"\n{spec.name}" in text
        for option in spec.all_options:
            assert option in text


def test_option_types():
    assert Choice(("a", "b")).parse("a") == "a"
    with pytest.raises(ValueError):
        Choice(("a", "b")).parse("c")
    assert Number(1, 4, integer=True).parse("3") == 3
    for bad in ("0", "5", "2.5", "x"):
        with pytest.raises(ValueError):
            Number(1, 4, integer=True).parse(bad)
    assert Number(0, 1).parse("0.5") == 0.5
    assert isinstance(BLOCKS["say"].all_options["wide"], Flag)
    assert "narrow" in BLOCKS["compare"].all_options and "wide" not in BLOCKS["compare"].all_options
    assert BLOCKS["note"].who == ANY_CHARACTER and "wide" not in BLOCKS["note"].all_options


@pytest.mark.parametrize("text, expected", [
    ("::: nope\nx\n:::", "unknown block"),
    ("::: tip colour=red\nx\n:::", "does not accept: colour"),
    ("::: say cat pose=fly\nx\n:::", "cat has no pose 'fly'"),
    ("::: say cat mood=angry\nx\n:::", "mood='angry' must be one of"),
    ("::: say cat right=yes\nx\n:::", "'right' is a flag"),
    ("::: compare cols=9\n### A\nx\n:::", "cols='9' must be between 1 and 4"),
    ("::: compare cols=two\n### A\nx\n:::", "must be a whole number"),
    ("::: compare\nno cards\n:::", "needs at least one"),
    ("::: scene kind=moon\n:::", "kind='moon' must be one of"),
    ("::: scene h=tall\n:::", "h='tall' must be a number"),
    ("::: scene cast=\"dragon\"\n:::", "unknown character"),
    ("::: scene cast=\"cat:stand:smile:zzz\"\n:::", "unknown mark"),
    ("::: define perch=dragon Term\nx\n:::", "unknown character"),
    ("::: define\nx\n:::", "needs the term"),
    ("::: stat\nx\n:::", "needs the big text"),
    ("::: dodont\n- only bad\n:::", "at least one line"),
    ("::: checklist\nno items\n:::", "needs list items"),
    ("::: dialog\nnobody: hi\n:::", "must start with a character name"),
    ("::: dialog\ncat (flying): hi\n:::", "no pose or mood 'flying'"),
    ("```prompt colour=red\nx\n```", "does not accept: colour"),
    ("```prompt mood=angry\nx\n```", "must be one of"),
    ("```python titel=x\nx\n```", "does not accept: titel"),
    ("::: tip\nnever closed", "never closed"),
    ("```chat\nOleg: no time\n```", "chat line 1: cannot read"),
    ("```chat\n> Oleg · 10:12: a reply to nothing\n```", "needs a message above it"),
    ("```chat\nOleg · 25:12: late\n```", "is not a time of day"),
    ("```chat\n  [img: a shot]\nOleg · 10:12: hi\n```", "must stand under a message"),
    ("```chat\nOleg · 10:12: hi\n  [img: ]\n```", "needs a caption"),
    ("```chat\nOleg · 10:12: hi\nloose text\n```", "chat line 2: cannot read"),
    ("::: note\nfloating\n:::", "no block to sit beside"),
])
def test_mistakes_are_reported_with_file_and_line(tmp_path, text, expected):
    with pytest.raises(BuildError) as error:
        compile_chapter(tmp_path, "Paragraph.\n\n" + text + "\n" if "floating" not in text else text + "\n")
    message = str(error.value)
    assert expected in message, message
    assert message.startswith("01-a.md: line "), message


def test_title_may_start_with_a_flag_of_another_component(tmp_path):
    row = compile_chapter(tmp_path, "::: tip top secret\nx\n:::\n").rows[0]
    assert "top secret" in row.main


def test_wide_policies(tmp_path):
    rows = compile_chapter(tmp_path, "::: tip\nx\n:::\n\n::: tip wide\nx\n:::\n\n::: compare\n### A\nx\n:::\n\n"
                                     "::: compare narrow\n### A\nx\n:::\n\n::: scene h=40\n:::\n").rows
    assert [row.wide for row in rows] == [False, True, True, False, True]


def test_wide_container_spans_nested_blocks_and_keeps_notes(tmp_path):
    text = "::: wide\nText.\n\n::: tip\nx\n:::\n:::\n\n::: note\nmargin\n:::\n\nAfter.\n"
    rows = compile_chapter(tmp_path, text).rows
    assert [(row.wide) for row in rows] == [True, True, False]
    assert "margin" in rows[2].side


def test_characters_take_turns_in_quotes(tmp_path):
    rows = compile_chapter(tmp_path, "::: quote\nx\n:::\n\n" * (len(MODULES) + 1)).rows
    order = [next(name for name in MODULES if f'char-{name}"' in row.main) for row in rows]
    assert order == [*MODULES, next(iter(MODULES))]


def test_fence_inside_a_list_uses_the_same_component(tmp_path):
    row = compile_chapter(tmp_path, "1. Run:\n\n   ```terminal\n   $ ls\n   ```\n").rows[0]
    assert 'class="terminal"' in row.main and 't-ps' in row.main


def test_labels_in_scenes_are_escaped(tmp_path):
    row = compile_chapter(tmp_path, '::: scene h=40 kind=meadow sign="A<B&C"\n:::\n').rows[0]
    assert "A&lt;B&amp;C" in row.main and "A<B" not in row.main


def test_component_classes_are_styled():
    for css_class in ("say", "bubble", "quote-card", "callout", "scroll", "stat", "recap", "dodont", "cards", "board",
                      "steps", "cast", "inset", "code", "terminal", "tree", "sheet", "prompt", "note", "margin-talk",
                      "accent", "chat", "chat-thread", "chat-mention", "chat-link", "chat-shot"):
        assert f".{css_class}" in CSS, f"no styles for .{css_class}"


def test_moods_are_shared_by_all_characters():
    assert all(not hasattr(module, "MOODS") for module in MODULES.values())
    assert BLOCKS["say"].options["mood"].values == MOODS


def test_front_chapters_come_before_the_contents_and_stay_out_of_them(tmp_path):
    (tmp_path / "book.yml").write_text("title: Test\nrepo: https://github.com/owner/name\nversion: 1.2-10.2026\n",
                                       encoding="utf-8")
    (tmp_path / "01-a.md").write_text("# First\n\ntext\n", encoding="utf-8")
    front = "---\ntitle: About\nfront: true\nopener: false\n---\ntext\n"
    (tmp_path / "zz-about.md").write_text(front, encoding="utf-8")
    build = build_html(tmp_path)
    assert [(c.title, c.number, c.front) for c in build.chapters] == [("First", 1, False), ("About", None, True)]
    html = build.html
    assert html.index('data-title="About"') < html.index('class="chapter contents"') < html.index('data-title="First"')
    assert 'href="#chapter-2"' not in html      # the front page is not listed in the contents


def test_about_photo_must_exist(tmp_path):
    with pytest.raises(BuildError, match="image not found: me.jpg"):
        compile_chapter(tmp_path, "::: about photo=me.jpg Someone\nHello.\n:::\n")
    (tmp_path / "me.jpg").write_bytes(b"x")
    assert "<img" in compile_chapter(tmp_path, "::: about photo=me.jpg Someone\nHello.\n:::\n").rows[0].main


def test_contacts_lines_are_validated(tmp_path):
    with pytest.raises(BuildError, match="kind one of"):
        compile_chapter(tmp_path, "::: contacts\nfax | Label | 123\n:::\n")


def test_stretchable_blocks_alternate_width(tmp_path):
    text = "Text.\n\n" + "::: tip\nx\n:::\n\n" * 4 + "::: note\nn\n:::\n\n::: tip\nx\n:::\n\n::: tip narrow\nx\n:::\n"
    rows = compile_chapter(tmp_path, text).rows[1:]
    assert [row.wide for row in rows] == [False, True, False, True, False, False]
    assert "n" in rows[4].side          # a block with a margin note is never stretched


@pytest.mark.parametrize("markup, expected", [
    ("Агент копирует модуль.", "Агент копирует модуль"),
    ("<p>Одно. Второе.</p>", "<p>Одно. Второе</p>"),
    ("Так и было...", "Так и было..."),
    ("Он точно послушается?", "Он точно послушается?"),
])
def test_a_margin_note_does_not_end_with_a_full_stop(markup, expected):
    from bookkit.components.context import no_final_period
    assert no_final_period(markup) == expected


def test_download_points_at_the_latest_release_and_shows_the_version(tmp_path):
    chapter = compile_chapter(tmp_path, "::: download\nGet it.\n:::\n")
    html = chapter.rows[0].main
    assert "https://github.com/owner/name/releases/latest/download/agentic-sdlc.pdf" in html and "1.2-10.2026" in html


def test_download_without_a_repository_is_an_author_error(tmp_path):
    (tmp_path / "book.yml").write_text("title: Test\n", encoding="utf-8")
    (tmp_path / "01-a.md").write_text("# A\n\n::: download\nGet it.\n:::\n", encoding="utf-8")
    with pytest.raises(BuildError, match="repo"):
        build_html(tmp_path)


@pytest.mark.parametrize("version", ["1.2", "1.2-13.2026", "v1.2-10.2026", "1.2-10.26"])
def test_a_malformed_version_is_an_error(tmp_path, version):
    from bookkit.config import read_version
    with pytest.raises(BuildError, match="MAJOR.MINOR-MM.YYYY"):
        read_version({"version": version}, tmp_path)


def test_a_second_content_folder_can_take_its_version_from_the_book(tmp_path):
    from bookkit.config import load_config
    (tmp_path / "book").mkdir()
    (tmp_path / "book" / "book.yml").write_text("title: T\nversion: 2.5-11.2026\n", encoding="utf-8")
    (tmp_path / "drafts").mkdir()
    (tmp_path / "drafts" / "book.yml").write_text("title: T\nversion_from: ../book/book.yml\n", encoding="utf-8")
    assert load_config(tmp_path / "drafts").version == "2.5-11.2026"


def test_a_folder_of_front_pages_gives_one_page_per_file(tmp_path):
    (tmp_path / "book.yml").write_text("title: Test\n", encoding="utf-8")
    (tmp_path / "00-front").mkdir()
    for name, title in (("1-author.md", "Author"), ("2-thanks.md", "Thanks")):
        (tmp_path / "00-front" / name).write_text(f"---\ntitle: {title}\nfront: true\nopener: false\n---\ntext\n",
                                                   encoding="utf-8")
    (tmp_path / "01-a.md").write_text("# First\n\ntext\n", encoding="utf-8")
    build = build_html(tmp_path)
    assert [(c.title, c.front) for c in build.chapters] == [("Author", True), ("Thanks", True), ("First", False)]


def test_a_file_line_wrapped_in_stars_is_set_bold(tmp_path):
    row = compile_chapter(tmp_path, '```file title="a.md"\n---\n**disable-model-invocation: true**\n---\n```\n').rows[0]
    assert '<strong class="f-mark">disable-model-invocation: true</strong>' in row.main and "**" not in row.main


def test_a_chat_has_messages_a_thread_apps_and_attachments(tmp_path):
    body = ("Oleg Smirnov · 10:12: Can you rename the **button**? Shots attached.\n"
            "  [img: The quiz page]\n"
            "> Tema P · 10:14: @Linear file a ticket for each\n"
            "> Linear [app] · 9:05: Filed ENG-412 and ENG-413\n"
            "> Claude [app] · 10:41: Done: #1287, see <https://example.com/#12>\n")
    row = compile_chapter(tmp_path, '```chat title="# requests"\n' + body + "```\n").rows[0]
    html = row.main
    assert "data-split" not in html                               # a screenshot moves on whole
    assert '<span class="chat-channel"><i>#</i>requests</span>' in html
    assert html.count('class="chat-msg"') == 2 and html.count('class="chat-msg app"') == 2
    assert html.index("chat-thread") < html.index("Tema P")       # the replies sit in the thread
    assert ">OS<" in html and ">TP<" in html and ">L<" in html     # people two initials, apps one
    assert "<strong>button</strong>" in html and "9:05" in html
    assert '<span class="chat-mention">@Linear</span>' in html
    assert '<span class="chat-link">ENG-412</span>' in html and '<span class="chat-link">#1287</span>' in html
    assert 'href="https://example.com/#12"' in html               # an id inside a tag is left alone
    assert html.count('class="chat-shot"') == 1 and "The quiz page" in html
    assert html.count("APP<") == 2


def test_a_name_keeps_its_avatar_color():
    from bookkit.components.chat import APP_COLORS, PEOPLE_COLORS, color
    assert color("Oleg Smirnov", False) == color("Oleg Smirnov", False) in PEOPLE_COLORS
    assert color("Linear", True) in APP_COLORS
    assert len({color(name, False) for name in ("Oleg", "Tema", "Anna", "Ivan", "Maria", "Petr")}) > 1

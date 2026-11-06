"""The builder never fails silently, never shows a traceback for an author's mistake and never hangs.

Every broken input here must stop the build with an error that names the file and the line; the browser tests at the
end build real PDFs and check what the eye cannot: fonts, rasters, ids, a hanging page.
"""
import re
import subprocess
import uuid
from pathlib import Path

import pytest

from bookkit import cli
from bookkit.compiler import build_html
from bookkit.markup import BuildError
from bookkit.render import _font_warnings, render_isolated

FRONT = "---\ntitle: Глава\nscene: railway\n---\n\n# Глава\n\n"
TEXT = "Обычный абзац текста.\n\n"


def book(tmp_path: Path, files: dict[str, str | bytes], config: str | None = "title: Test\n") -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    if config is not None:
        (tmp_path / "book.yml").write_text(config, encoding="utf-8")
    for name, text in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(text, bytes):
            path.write_bytes(text)
        else:
            path.write_text(text, encoding="utf-8")
    return tmp_path


BROKEN = {
    # the book
    "no book.yml": ({"01-a.md": FRONT + TEXT}, None, "no book.yml"),
    "book.yml broken": ({"01-a.md": FRONT + TEXT}, "title: T\ntopics: [a\n", r"book\.yml: line 3: not valid YAML"),
    "front matter broken": ({"01-a.md": "---\ntitle: [x\n---\n# A\n\nx\n"}, "title: T\n",
                            r"01-a\.md: front matter: line 2: not valid YAML"),
    "book.yml toc is text": ({"01-a.md": FRONT + TEXT}, "title: T\ntoc: no thanks\n", "toc must be true or false"),
    "book.yml topics not a list": ({"01-a.md": FRONT + TEXT}, "title: T\ntopics: Skills\n", "topics must be a list"),
    "book.yml repo not github": ({"01-a.md": FRONT + TEXT}, "title: T\nrepo: example.com\n", "repo must be"),
    "book.yml chapters outside": ({"01-a.md": FRONT + TEXT}, "title: T\nchapters: [../x.md]\n",
                                  "chapters outside the book's folder"),
    "book.yml bad language": ({"01-a.md": FRONT + TEXT}, "title: T\nlanguage: ../../x\n", "two-letter code"),
    "color is a list": ({"01-a.md": "---\ncolor: [pink]\n---\n# A\n\nx\n"}, "title: T\n", "color must be text"),
    "world is a list": ({"01-a.md": "---\nworld: [x]\n---\n# A\n\nx\n"}, "title: T\n", "world must be text"),
    # files and front matter
    "not utf-8": ({"01-a.md": FRONT.encode() + b"\xff\xfe"}, "title: T\n", r"01-a\.md: line 8: not UTF-8"),
    "empty file": ({"01-a.md": ""}, "title: T\n", "01-a.md: the file has no text"),
    "front matter only": ({"01-a.md": "---\ntitle: A\n---\n"}, "title: T\n", "no text after its front matter"),
    "front matter unclosed": ({"01-a.md": "---\ntitle: A\n\n# A\n"}, "title: T\n", "never closed with a line '---'"),
    "number is text": ({"01-a.md": "---\nnumber: abc\n---\n# A\n\nx\n"}, "title: T\n", "number must be"),
    "front is text": ({"01-a.md": "---\nfront: yes please\n---\n# A\n\nx\n"}, "title: T\n", "front must be"),
    "one scene twice": ({"01-a.md": FRONT + TEXT, "02-b.md": FRONT + TEXT}, "title: T\n",
                        "the scene 'railway' is already the opener of 01-a.md"),
    # blocks
    "stray closer": ({"01-a.md": FRONT + TEXT + ":::\n"}, "title: T\n", "line 10: ':::' closes no block"),
    "unclosed fence": ({"01-a.md": FRONT + "```prompt\nделай\n"}, "title: T\n", "line 8: the code block opened"),
    "empty prompt": ({"01-a.md": FRONT + '```prompt title="X"\n```\n'}, "title: T\n", "'```prompt' is empty"),
    "empty say": ({"01-a.md": FRONT + "::: say cat\n:::\n"}, "title: T\n", "'::: say' is empty"),
    "say to a stranger": ({"01-a.md": FRONT + "::: say dog\nГав\n:::\n"}, "title: T\n", "'dog' is not a character"),
    "option after title": ({"01-a.md": FRONT + "::: about Имя photo=me.jpg\nТекст\n:::\n"}, "title: T\n",
                           "options go before the title"),
    "steps without a list": ({"01-a.md": FRONT + "::: steps\nтекст\n:::\n"}, "title: T\n", "needs a numbered list"),
    "text in pagebreak": ({"01-a.md": FRONT + TEXT + "::: pagebreak\nтекст\n:::\n"}, "title: T\n", "takes no text"),
    "contact link script": ({"01-a.md": FRONT + "::: contacts\nweb | Сайт | x | javascript:alert(1)\n:::\n"},
                            "title: T\n", "the link must start with"),
    # text
    "script": ({"01-a.md": FRONT + "<script>while(1){}</script>\n"}, "title: T\n", "line 8: HTML is not allowed"),
    "inline html": ({"01-a.md": FRONT + "Текст <b>жирный</b>.\n"}, "title: T\n", "line 8: HTML is not allowed"),
    "unknown flag": ({"01-a.md": FRONT + TEXT + "Флаг :flag-zz:.\n"}, "title: T\n", "line 10: unknown flag 'zz'"),
    # pictures
    "picture from the web": ({"01-a.md": FRONT + "![x](https://example.com/a.png)\n"}, "title: T\n",
                             "put the picture next to the chapter"),
    "picture out of the book": ({"01-a.md": FRONT + "![x](../outside.png)\n"}, "title: T\n", "outside the book"),
    "picture that is not one": ({"01-a.md": FRONT + "![x](notes.txt)\n", "notes.txt": "x"}, "title: T\n",
                                "not a picture"),
}


@pytest.mark.parametrize("case", list(BROKEN))
def test_a_broken_book_stops_with_a_clear_error(tmp_path, case):
    files, config, message = BROKEN[case]
    (tmp_path.parent / "outside.png").write_bytes(b"\x89PNG")
    with pytest.raises(BuildError, match=message):
        build_html(book(tmp_path, files, config))


def test_what_the_book_may_write_by_hand_still_works(tmp_path):
    text = (FRONT + "<!-- pagebreak -->\n\n<!-- side: full -->\n\n| a | b |\n|---|---|\n| 1<br>2 | "
            '<span class="score good">98</span> |\n\n<!-- a comment of the author -->\n\nТекст.\n')
    html = build_html(book(tmp_path, {"01-a.md": text})).html
    assert 'class="score good"' in html and "<br>" in html


def test_the_same_book_gives_the_same_document(tmp_path):
    content = book(tmp_path, {"01-a.md": FRONT + TEXT + "::: say cat\nМяу\n:::\n"})
    assert build_html(content).html == build_html(content).html


def test_a_long_table_may_break_between_its_rows(tmp_path):
    table = "| a | b |\n|---|---|\n" + "| x | y |\n" * 5
    html = build_html(book(tmp_path, {"01-a.md": FRONT + table})).html
    assert "<tbody data-split" in html


def test_a_font_of_the_building_machine_is_reported(tmp_path):
    pdf = tmp_path / "book.pdf"
    pdf.write_bytes(b"%PDF-1.4\n1 0 obj\n<</BaseFont /AAAAAA+Rubik-W800>>\nendobj\n")
    assert _font_warnings(pdf) == []
    pdf.write_bytes(b"%PDF-1.4\n1 0 obj\n<</BaseFont /BAAAAA+LucidaGrande-Bold>>\nendobj\n")
    assert "LucidaGrande-Bold" in _font_warnings(pdf)[0]


# ---------------------------------------------------------------- through the browser
def _browsers(mark: str) -> int:
    return len(subprocess.run(["pgrep", "-f", mark], capture_output=True, text=True).stdout.split())


def test_a_small_book_builds_clean_through_the_browser(tmp_path, capsys):
    content = book(tmp_path / "book", {
        "01-a/00-chapter.md": FRONT + TEXT * 3 + "::: tip\nСовет.\n:::\n\n::: dodont\n- плохо\n+ хорошо\n:::\n\n"
                              "| a | b |\n|---|---|\n" + "| ячейка | ячейка |\n" * 60})
    out = tmp_path / "out" / "book.pdf"
    assert cli.main(["build", "--strict", "--content", str(content), "--out", str(out)]) == 0, capsys.readouterr()
    data = out.read_bytes()
    assert data.startswith(b"%PDF") and not list(out.parent.glob(".*partial"))
    families = {re.sub(rb"^[A-Z]{6}\+", b"", name).split(b"-")[0] for name in re.findall(rb"/BaseFont\s*/(\S+)", data)}
    bundled = {path.stem.split("-")[0].encode() for path in (Path(cli.ROOT) / "bookkit/theme/fonts").glob("*.ttf")}
    assert families <= bundled
    assert b"/SMask" not in data                             # no raster fallbacks


def test_a_hanging_page_is_stopped_and_its_browser_ended(tmp_path):
    page = tmp_path / "hang.html"
    page.write_text("<html><body><script>setTimeout(() => { while (true) {} }, 10)</script></body></html>")
    run = f"test-hang-{uuid.uuid4().hex}"     # unique: test runs side by side must not end each other's browsers
    with pytest.raises(BuildError, match="did not finish"):
        render_isolated(page, tmp_path / "book.pdf", timeout=6, run=run)
    assert not (tmp_path / ".book.pdf.partial").exists() and not (tmp_path / "book.pdf").exists()
    assert _browsers(f"bookkit-run={run}") == 0


def test_a_list_in_an_aligned_table_column_is_still_a_list(tmp_path):
    table = "| a | b |\n|---|--:|\n| x | - one<br>- two |\n"
    html = build_html(book(tmp_path, {"01-a.md": FRONT + table})).html
    assert html.count('class="cell-item"') == 2


def test_a_title_cannot_close_the_script_that_carries_it(tmp_path):
    html = build_html(book(tmp_path, {"01-a.md": FRONT + TEXT}, 'title: "a</script><b>"\n')).html
    assert "a</script><b>" not in html.split("window.__bookConfig")[1].split(";</script>")[0]


"""Tests for the command line: where things go, and what it refuses to delete."""
import tempfile
from pathlib import Path

import pytest

from bookkit import cli
from bookkit.compiler import build_html
from bookkit.markup import BuildError


def test_a_folder_the_tool_did_not_create_is_never_emptied(tmp_path):
    foreign = tmp_path / "pages"
    foreign.mkdir()
    (foreign / "my-notes.txt").write_text("keep me", encoding="utf-8")
    with pytest.raises(BuildError):
        cli.fresh_folder(foreign)
    assert (foreign / "my-notes.txt").exists()


def test_its_own_folder_is_emptied_and_marked(tmp_path):
    own = tmp_path / "pages"
    cli.fresh_folder(own)
    (own / "page-001.png").write_text("old", encoding="utf-8")
    cli.fresh_folder(own)
    assert [path.name for path in own.iterdir()] == [cli.MARKER]


def test_an_empty_foreign_folder_may_be_taken_over(tmp_path):
    (tmp_path / "pages").mkdir()
    cli.fresh_folder(tmp_path / "pages")
    assert (tmp_path / "pages" / cli.MARKER).exists()


def test_the_demo_refuses_an_explicit_content_or_output(capsys):
    assert cli.main(["build", "--demo", "--content", "somewhere"]) == 2
    assert "--demo has its own content and output" in capsys.readouterr().err


def test_dist_holds_only_the_book():
    assert cli.PDF == "agentic-sdlc.pdf" and cli.LOCAL.parent == Path(tempfile.gettempdir())
    assert not cli.LOCAL.is_relative_to(cli.PROJECT)   # nothing built stays in the project


def test_a_bad_page_list_fails_before_anything_is_deleted(tmp_path, capsys):
    pages = tmp_path / "pages"
    cli.fresh_folder(pages)
    (pages / "page-001.png").write_text("proof", encoding="utf-8")
    assert cli.main(["build", "--out", str(tmp_path / "book.pdf"), "--shots", "5-", "--no-pdf"]) == 2
    assert (pages / "page-001.png").exists()


def test_the_default_folders_are_the_book_and_dist_next_to_tools():
    assert cli.BOOK == cli.PROJECT / "book" and cli.DIST == cli.PROJECT / "dist"
    assert Path(cli.__file__).resolve().parent.parent / "demo" == cli.DEMO


def test_the_demo_chapter_compiles():
    result = build_html(cli.DEMO)
    assert result.prompts and "<html" in result.html


@pytest.mark.parametrize("spec", ["5-", "-3", "0", "4-2", "x", "1,,2"])
def test_a_page_list_that_means_nothing_is_refused(spec):
    with pytest.raises(BuildError):
        cli.parse_pages(spec)


def test_a_page_list_reads_ranges_and_single_pages():
    assert cli.parse_pages("1,3-5") == [1, 3, 4, 5] and cli.parse_pages("all") is None


def test_a_storyboard_may_preview_a_chapter_in_another_world_without_touching_it(tmp_path):
    from bookkit.compiler import build_html

    chapter = tmp_path / "01-a.md"
    (tmp_path / "book.yml").write_text("title: T\n", encoding="utf-8")
    chapter.write_text("---\nscene: morning\n---\n# A\n\nText.\n", encoding="utf-8")
    before = chapter.read_text(encoding="utf-8")
    html = build_html(tmp_path, only="01-a", world="station").html
    assert 'data-world="station"' in html and chapter.read_text(encoding="utf-8") == before
    assert 'data-world=""' in build_html(tmp_path, only="01-a").html

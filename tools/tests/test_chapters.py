"""Tests for where chapters come from: single files, folders of parts, and what is left out."""
import pytest

from bookkit.compiler import SIDES, build_html, compile_book
from bookkit.config import load_config
from bookkit.markup import BuildError


def write(folder, files: dict[str, str]):
    files = {"book.yml": "title: Test\n", **files}
    for name, text in files.items():
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return folder


def test_a_folder_is_one_chapter_made_of_its_files_in_order(tmp_path):
    book = write(tmp_path, {
        "01-first/00-chapter.md": "---\ntitle: First\n---\nOpening paragraph.\n",
        "01-first/01-section.md": "## One\n\nBody of one.\n",
        "01-first/02-section.md": "## Two\n\nBody of two.\n",
        "02-second.md": "---\ntitle: Second\n---\nA chapter in a single file.\n",
    })
    _, chapters = compile_book(book)
    assert [chapter.title for chapter in chapters] == ["First", "Second"]
    assert [section.title for section in chapters[0].sections] == ["One", "Two"]
    assert [chapter.number for chapter in chapters] == [1, 2]


def test_files_of_the_book_are_listed_in_reading_order(tmp_path):
    book = write(tmp_path, {"02-b.md": "B", "01-a/02-part.md": "two", "01-a/01-part.md": "one"})
    names = [str(path.relative_to(book)) for path in load_config(book).chapter_files()]
    assert names == ["01-a/01-part.md", "01-a/02-part.md", "02-b.md"]


def test_repository_files_hidden_entries_and_empty_folders_are_not_chapters(tmp_path):
    book = write(tmp_path, {
        "README.md": "about the repository", "LICENSE.md": "licence", "_drafts/idea.md": "not yet",
        ".github/notes.md": "ci", "pictures/photo.txt": "not markdown",
        "01-real/README.md": "about this chapter", "01-real/00-chapter.md": "---\ntitle: Real\n---\nText.\n",
    })
    assert [source.name for source in load_config(book).chapter_sources()] == ["01-real"]
    assert [path.name for path in load_config(book).chapter_files()] == ["00-chapter.md"]


def test_only_the_first_file_of_a_folder_may_have_front_matter(tmp_path):
    book = write(tmp_path, {"01-a/00-chapter.md": "---\ntitle: A\n---\nText.\n",
                            "01-a/01-part.md": "---\ncolor: coral\n---\nMore.\n"})
    with pytest.raises(BuildError, match="01-a/01-part.md: only the first file"):
        compile_book(book)


def test_a_mistake_is_reported_with_the_folder_the_file_and_the_line(tmp_path):
    book = write(tmp_path, {"01-a/00-chapter.md": "---\ntitle: A\n---\nText.\n",
                            "01-a/01-part.md": "Fine.\n\n::: nosuchblock\nbody\n:::\n"})
    with pytest.raises(BuildError, match=r"01-a/01-part\.md: line 3"):
        compile_book(book)


def test_only_matches_the_name_of_the_folder(tmp_path):
    book = write(tmp_path, {"01-alpha/00-chapter.md": "---\ntitle: Alpha\n---\nText.\n",
                            "02-beta/00-chapter.md": "---\ntitle: Beta\n---\nText.\n"})
    _, chapters = compile_book(book, only="beta")
    assert [(chapter.title, chapter.number) for chapter in chapters] == [("Beta", 2)]


def test_a_picture_is_found_next_to_the_files_of_its_chapter(tmp_path):
    book = write(tmp_path, {"01-a/00-chapter.md": "---\ntitle: A\n---\n![alt](pic.png \"Caption\")\n"})
    (book / "01-a" / "pic.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    assert "pic.png" in build_html(book).html


def test_an_explicit_list_in_book_yml_may_name_folders(tmp_path):
    book = write(tmp_path, {"book.yml": "chapters: [b, a.md]\n", "a.md": "---\ntitle: A\n---\nText.\n",
                            "b/00-chapter.md": "---\ntitle: B\n---\nText.\n"})
    _, chapters = compile_book(book)
    assert [chapter.title for chapter in chapters] == ["B", "A"]


def test_a_missing_content_folder_is_a_clean_error(tmp_path):
    with pytest.raises(BuildError, match="no such folder"):
        compile_book(tmp_path / "nowhere")


def test_the_full_layout_is_a_known_side_for_a_chapter_and_for_a_switch(tmp_path):
    assert "full" in SIDES
    book = write(tmp_path, {"01.md": "---\ntitle: T\nside: full\n---\nDense text.\n\n<!-- side: outer -->\n\nBack.\n"})
    html = build_html(book).html
    assert 'data-side="full"' in html or "side-full" in html or '"full"' in html


def test_book_yml_may_list_only_folders_and_markdown_files(tmp_path):
    book = write(tmp_path, {"book.yml": "title: Test\nchapters: [01-a.md, notes.txt]\n", "01-a.md": "Text.\n",
                            "notes.txt": "not a chapter"})
    with pytest.raises(BuildError, match="notes.txt, which is neither a folder nor a Markdown file"):
        load_config(book).chapter_sources()

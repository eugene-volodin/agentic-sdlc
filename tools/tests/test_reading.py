"""Reading time: the running text is counted, listings and markup are not; minutes round to five."""
from pathlib import Path

from bookkit import design, reading


def test_listings_markup_and_comments_are_not_counted_prompts_are():
    text = ("---\ntitle: X\ncolor: coral\n---\n# Заголовок\n\nДва **слова**.\n\n<!-- заметка себе -->\n"
            "```python\nprint('code is looked over, not read')\n```\n\n```terminal\n$ ls\n```\n\n"
            "```prompt who=cat\nНапиши тест\n```\n\n::: note cat\nСм. [доку](https://example.com)\n:::\n\n"
            "| a | b |\n|---|---|\n| да | нет |\n")
    words = reading.running_text(text)
    assert words == "Заголовок Два слова. Напиши тест См. доку a b да нет"
    assert "print" not in words and "ls" not in words and "заметка" not in words and "example" not in words


def test_minutes_round_to_the_nearest_five_and_are_at_least_five():
    cpm = design.READ_CPM
    assert reading.minutes(0) == 5
    assert reading.minutes(cpm * 17) == 15 and reading.minutes(cpm * 18) == 20
    assert reading.minutes(cpm * 33) == 35


def test_a_chapter_folder_is_counted_across_its_files(tmp_path: Path):
    (tmp_path / "00-chapter.md").write_text("---\ntitle: X\n---\nабв\n", encoding="utf-8")
    (tmp_path / "01-more.md").write_text("где\n", encoding="utf-8")
    assert reading.characters(tmp_path) == 6


def test_a_chapter_folder_counts_only_its_parts(tmp_path):
    (tmp_path / "00-chapter.md").write_text("Words.", encoding="utf-8")
    (tmp_path / "README.md").write_text("About the folder, not a part of the chapter.", encoding="utf-8")
    (tmp_path / "_draft.md").write_text("A draft.", encoding="utf-8")
    assert reading.characters(tmp_path) == len("Words.")

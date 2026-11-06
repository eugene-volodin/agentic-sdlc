"""Tests for the parsing layer: block splitting, option syntax, front matter."""
import pytest

from bookkit.markup import BuildError, parse_head, split_front_matter, split_segments


def test_plain_markdown_is_one_segment():
    segments = split_segments("# Title\n\nText")
    assert [s.kind for s in segments] == ["markdown"]


def test_directive_is_extracted_with_line_numbers():
    segments = split_segments("intro\n\n::: tip Title\nbody\n:::\n\noutro", first_line=10)
    assert [(s.kind, s.line) for s in segments] == [("markdown", 10), ("directive", 12), ("markdown", 15)]
    assert segments[1].head == "tip Title"
    assert segments[1].text == "body"


def test_colons_inside_code_fence_are_not_a_directive():
    source = "```text\n::: tip\nnot a block\n:::\n```"
    assert [s.kind for s in split_segments(source)] == ["markdown"]


def test_fence_inside_directive_does_not_close_it():
    source = "::: steps\n1. Run\n\n   ```\n   :::\n   ```\n:::"
    segments = split_segments(source)
    assert len(segments) == 1 and segments[0].kind == "directive"
    assert ":::" in segments[0].text


def test_nested_directives_stay_in_the_outer_body():
    source = "::: wide\n::: tip\ninner\n:::\n:::"
    segments = split_segments(source)
    assert len(segments) == 1
    assert segments[0].text == "::: tip\ninner\n:::"


def test_longer_closing_fence_closes_a_shorter_one():
    source = "```\ncode\n````\n\n::: tip\nbody\n:::"
    assert [s.kind for s in split_segments(source)] == ["markdown", "directive"]


def test_unclosed_directive_is_reported_with_its_line():
    with pytest.raises(BuildError, match="line 3"):
        split_segments("a\n\n::: tip\nnever closed")


def test_head_reads_character_flags_options_and_title():
    head = parse_head('cat right pose=think note="two words" Title: with "quotes"', flags={"right"})
    assert head.who == "cat"
    assert head.options == {"right": True, "pose": "think", "note": "two words"}
    assert head.title == 'Title: with "quotes"'


def test_title_words_are_not_mistaken_for_flags():
    head = parse_head("The right way", flags={"right"})
    assert head.options == {} and head.title == "The right way"


def test_character_is_ignored_when_not_allowed():
    head = parse_head("cat and mouse", allow_who=False)
    assert head.who is None and head.title == "cat and mouse"


def test_who_option_selects_the_character():
    assert parse_head("who=sparrow").who == "sparrow"


def test_front_matter_is_split_and_lines_counted():
    meta, body, line = split_front_matter("---\ntitle: T\ncolor: coral\n---\n# Heading\n")
    assert meta == {"title": "T", "color": "coral"}
    assert body == "# Heading\n" and line == 5


def test_missing_front_matter_is_fine():
    assert split_front_matter("text") == ({}, "text", 1)


def test_windows_line_endings_and_bom_are_tolerated():
    meta, body, _ = split_front_matter("﻿---\r\ntitle: T\r\n---\r\ntext\r\n")
    assert meta == {"title": "T"} and body == "text\n"


def test_invalid_front_matter_raises():
    with pytest.raises(BuildError):
        split_front_matter("---\ntitle: [unclosed\n---\ntext")


def test_only_the_given_flags_are_recognized():
    assert parse_head("top secret").title == "top secret"
    head = parse_head("top secret", flags={"top"})
    assert head.options == {"top": True} and head.title == "secret"


def test_a_flag_is_drawn_inline_and_an_unknown_one_is_an_error():
    from bookkit.art.flags import flag
    from bookkit.markdown import MarkdownRenderer
    html = MarkdownRenderer({}).inline("США :flag-us:")
    assert '<svg class="flag"' in html and ":flag-us:" not in html
    import pytest
    with pytest.raises(ValueError):
        flag("xx")


def test_a_table_cell_written_as_a_list_gets_one_item_per_line():
    from bookkit.markdown import MarkdownRenderer
    html = MarkdownRenderer({}).blocks("| A |\n|---|\n| - one<br>- two |\n| plain |\n")
    assert html.count('class="cell-item"') == 2 and "<td>plain</td>" in html


def test_inline_code_breaks_only_after_a_slash_and_a_link_written_as_an_address_after_a_dot_too():
    from bookkit.markdown import MarkdownRenderer
    html = MarkdownRenderer({}).inline("`.claude/skills/<name>/SKILL.md` `~/.claude/settings.json` `docs/adr/` "
                                       "`claudeMdExcludes` [code.claude.com](https://code.claude.com/docs)")
    assert "<code>.claude/<wbr>skills/<wbr>&lt;name&gt;/<wbr>SKILL.md</code>" in html
    assert "<code>~/.claude/<wbr>settings.json</code>" in html         # never a line starting with a dot
    assert "<code>docs/adr/</code>" in html                             # nor a piece too short to stand alone
    assert "<code>claudeMdExcludes</code>" in html
    assert ">code.<wbr>claude.com</a>" in html


def test_short_words_keep_to_what_follows_and_a_paragraph_never_ends_on_a_short_word_alone():
    from bookkit.markdown import MarkdownRenderer
    md = MarkdownRenderer({"short_words": ["a", "i"]})
    html = md.blocks("read a `file` i see it all.")
    assert "a <code>file</code>" in html and "it all.</p>" in html
    assert "see it" not in html


def test_a_command_kept_whole_and_its_punctuation_and_a_hyphen_before_a_short_particle_never_part():
    from bookkit.markdown import MarkdownRenderer
    html = MarkdownRenderer({}).blocks("run `git commit`, then well-to-do and yes-no.")
    assert '<span class="glue"><code class="words">git commit</code>,</span>' in html
    assert '<span class="glue">yes-no</span>' in html and "well-to-do" in html

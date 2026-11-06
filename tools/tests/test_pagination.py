"""A page is for content and an illustration never takes a half or a third of a page: the
paginator fills the end of a page from the next one - a paragraph splits between its lines, a section starts at the foot
of a page with a few lines of itself - and the footer scene stays small; a large one only before a block that cannot
move up, and the build warns when that is not rare."""
import tempfile
from pathlib import Path

import pytest

from bookkit import design
from bookkit import render as rendering
from bookkit.compiler import build_html
from bookkit.render import footer_warnings

FRONT = "---\ntitle: Test\nscene: fair\n---\n\n# Test\n\n"
SENTENCE = "The agent reads the repository, runs the build and checks its own work before it says that it is done. "
PARAGRAPH = SENTENCE * 7 + "\n\n"                     # about ten lines: whole, it would leave a hole when it moves on
NOTE = "::: note cat\nA remark on the paragraph above, with a source.\n:::\n\n"
QUESTION = "::: note sparrow\nAnd why can it not just do it?\n:::\n\n"


def lay_out(tmp_path: Path, text: str, monkeypatch) -> dict:
    """Lay a one-chapter book out in the browser; the footers are left empty, only their sizes matter here."""
    content = tmp_path / "book"
    (content / "01-a").mkdir(parents=True)
    (content / "book.yml").write_text("title: Test\nlanguage: ru\n", encoding="utf-8")
    (content / "01-a" / "00-chapter.md").write_text(FRONT + text, encoding="utf-8")
    monkeypatch.setattr(rendering, "footers", lambda requests, vocabulary: ["<svg></svg>" for _ in requests])
    result = build_html(content)
    with tempfile.TemporaryDirectory() as work:
        source = Path(work) / "book.html"
        source.write_text(result.html, encoding="utf-8")
        return rendering.render(source)


def test_no_footer_takes_a_third_of_a_page():
    assert set(design.FOOT_HEIGHTS) == {"s", "m", "l"}
    assert design.FOOT_HEIGHTS["m"] <= 0.19 * design.PAGE_HEIGHT
    assert design.FOOT_HEIGHTS["l"] <= 0.30 * design.PAGE_HEIGHT


def test_running_text_fills_the_page_and_the_footer_stays_small(tmp_path, monkeypatch):
    text = "".join(f"## Section {n}\n\n" + PARAGRAPH + (NOTE if n % 2 else QUESTION) + PARAGRAPH * (n % 3 + 1)
                   for n in range(1, 9))
    report = lay_out(tmp_path, text, monkeypatch)
    assert report["warnings"] == []
    inner = [foot for foot in report["feet"] if foot["end"] != "last"]
    assert len(inner) >= 6
    assert all(foot["end"] == "text" for foot in inner)
    assert all(foot["size"] in ("s", "m") for foot in inner), inner
    assert all(foot["free"] < design.FOOT_HEIGHTS["m"] - design.FOOT_HEIGHTS["s"] + design.SECTION_MIN
               for foot in inner), inner


def test_a_large_footer_only_before_a_block_that_cannot_move(tmp_path, monkeypatch):
    listing = "```\n" + "".join(f"line {n} of a listing that fits a page but not the end of one\n"
                                for n in range(40)) + "```\n\n"
    text = "".join("## Section\n\n" + PARAGRAPH * (n % 3 + 1) + listing for n in range(6))
    report = lay_out(tmp_path, text, monkeypatch)
    for foot in report["feet"]:
        if foot["size"] == "l":
            assert foot["end"] == "stuck" and foot["blocker"] == "code", foot
        if foot["size"] == "panorama":
            assert foot["end"] == "last", foot
    large = [foot for foot in report["feet"] if foot["size"] == "l"]
    warned = [warning for warning in report["warnings"] if "large footer" in warning]
    assert bool(warned) == (len(large) > design.FOOT_LARGE_MAX)


@pytest.mark.parametrize(("feet", "expected"), [
    ([], []),
    ([{"page": 5, "chapter": "4", "size": "l", "end": "stuck", "blocker": "table"},
      {"page": 9, "chapter": "5", "size": "l", "end": "stuck", "blocker": "prompt"},
      {"page": 12, "chapter": "5", "size": "panorama", "end": "last"}], []),
    ([{"page": 5, "chapter": "4", "size": "l", "end": "stuck", "blocker": "table"},
      {"page": 7, "chapter": "4", "size": "l", "end": "stuck", "blocker": "prompt"},
      {"page": 9, "chapter": "4", "size": "l", "end": "stuck", "blocker": "say"},
      {"page": 11, "chapter": "4", "size": "l", "end": "stuck", "blocker": "table"}],
     ["chapter 4: 4 pages end with a large footer (l), at most 3 allowed; the next block could not move up on "
      "pages 5 (table), 7 (prompt), 9 (say), 11 (table)"]),
    ([{"page": 3, "chapter": "1", "size": "l", "end": "text"}],
     ["page 3: a footer of size l where the next page's text could have filled the page"]),
    ([{"page": 3, "chapter": "1", "size": "panorama", "end": "stuck"}],
     ["page 3: a footer of size panorama where the next page's text could have filled the page"]),
    ([{"page": 3, "chapter": "1", "size": "l", "end": "break", "blocker": "pagebreak"},
      {"page": 6, "chapter": "1", "size": "l", "end": "stuck", "blocker": "table"}], []),
])
def test_large_footers_are_reported_when_they_are_not_rare(feet, expected):
    assert footer_warnings(feet) == expected


ITEM = "an item of a list that runs over two lines of the column, so that a dozen of them fill most of a page"


@pytest.mark.parametrize("block", [
    "".join(f"- {ITEM};\n" for _ in range(12)),
    "::: steps\n" + "".join(f"{n}. **Step {n}.** {ITEM}\n" for n in range(1, 13)) + ":::\n",
])
def test_a_list_that_fits_a_page_still_breaks_between_its_items_to_fill_one(tmp_path, monkeypatch, block):
    report = lay_out(tmp_path, "## Section\n\n" + PARAGRAPH * 2 + "Here it is:\n\n" + block + "\n" + PARAGRAPH,
                     monkeypatch)
    assert report["warnings"] == []
    inner = [foot for foot in report["feet"] if foot["end"] != "last"]
    assert inner and all(foot["size"] in ("s", "m") and foot["end"] != "stuck" for foot in inner), inner


def test_a_short_list_keeps_two_items_on_each_side_or_moves_on_whole(tmp_path, monkeypatch):
    long = SENTENCE * 3
    report = lay_out(tmp_path, "## Section\n\n" + PARAGRAPH * 3 + "".join(f"- {long}\n" for _ in range(3)),
                     monkeypatch)
    stuck = [foot for foot in report["feet"] if foot["end"] == "stuck"]
    assert all(foot["blocker"] == "ul" for foot in stuck)


def test_a_list_of_two_long_items_breaks_between_them_rather_than_leave_a_hole(tmp_path, monkeypatch):
    """A section, its lead-in and a list of two long items after a listing that cannot move: one item stays on the
    page, the other goes on, instead of all three moving on and leaving the foot of the page empty."""
    listing = "```\n" + "".join(f"line {n}\n" for n in range(14)) + "```\n\n"
    items = "".join(f"- {SENTENCE * 4}\n" for _ in range(2))
    report = lay_out(tmp_path, "## A\n\n" + PARAGRAPH + listing + "## B\n\nRoles:\n\n" + items + "\n" + PARAGRAPH,
                     monkeypatch)
    inner = [foot for foot in report["feet"] if foot["end"] != "last"]
    assert inner and all(foot["size"] == "s" for foot in inner), inner


def test_the_split_threshold_is_a_third_of_the_page():
    assert abs(design.HOLE_MAX - design.PAGE_HEIGHT / 3) < 1


@pytest.mark.parametrize("block", [
    "```\n" + "".join(f"line {n} of a listing that fits a page but not the end of one\n" for n in range(40)) + "```\n",
    "| Column | Another column |\n|---|---|\n" + "".join(f"| row {n} | {SENTENCE} |\n" for n in range(14)),
])
def test_a_block_that_would_leave_a_third_of_the_page_empty_splits(tmp_path, monkeypatch, block):
    report = lay_out(tmp_path, "## Section\n\n" + PARAGRAPH + "Here it is:\n\n" + block + "\n" + PARAGRAPH * 2,
                     monkeypatch)
    assert report["warnings"] == []
    for foot in report["feet"]:
        if foot["end"] == "stuck":
            assert foot["free"] <= design.HOLE_MAX, foot


def test_a_prompt_that_fits_a_page_is_never_cut_in_two(tmp_path, monkeypatch):
    lines = [f"{n}. Step {n}: run the check." for n in range(1, 25)]
    fence = '```prompt title="A long prompt" note="-"\n' + "\n".join(lines) + "\n```\n"
    report = lay_out(tmp_path, "## Section\n\n" + PARAGRAPH * 2 + fence + "\n" + PARAGRAPH, monkeypatch)
    assert report["prompt_parts"] == 0, report
    prompts = build_html(tmp_path / "book").prompts
    assert len(prompts) == 1 and prompts[0].text == "\n".join(lines) + "\n"




def test_a_note_never_stands_between_a_lead_in_and_its_list(tmp_path, monkeypatch):
    """A long remark before a lead-in near the foot of a page: it does not fit beside the one line of the lead-in, so it
    goes across the page - above the lead-in, never between it and its list. The paginator
    reports a note left between them; this layout is one that would put one there."""
    note = "::: note cat\n" + "Everyone names this process differently, and every vendor has a term of its own. " * 4
    items = "".join(f"- item {n} of the list that the lead-in introduces;\n" for n in range(8))
    text = "## Section\n\n" + PARAGRAPH * 3 + note + "\n:::\n\nIn this chapter:\n\n" + items + "\n" + PARAGRAPH
    report = lay_out(tmp_path, text, monkeypatch)
    assert report["warnings"] == []


def test_the_farewell_is_a_full_page_after_the_last_chapter_which_keeps_its_footer(tmp_path, monkeypatch):
    """The book's last page (art/farewell.py) is a full page of its own; the last chapter's own last page before it
    still ends with its footer, as when nothing followed."""
    content = tmp_path / "book"
    (content / "01-a").mkdir(parents=True)
    (content / "book.yml").write_text("title: Test\nlanguage: ru\ncover: false\ntoc: false\nplan:\n  - 1. Test\n",
                                      encoding="utf-8")
    (content / "01-a" / "00-chapter.md").write_text(FRONT.replace("---\n\n", "number: 1\n---\n\n") + PARAGRAPH * 3,
                                                    encoding="utf-8")
    monkeypatch.setattr(rendering, "footers", lambda requests, vocabulary: ["<svg></svg>" for _ in requests])
    with tempfile.TemporaryDirectory() as work:
        source = Path(work) / "book.html"
        source.write_text(build_html(content).html, encoding="utf-8")
        report = rendering.render(source)
    assert report["warnings"] == []
    last = report["feet"][-1]
    assert last["end"] == "last" and last["page"] == report["pages"] - 1   # the farewell is the page after it


PROMPT = ('```prompt title="Long" note="-"\n' + "".join(f"Line {n} of a prompt that has to stay whole on its monitor.\n"
                                                       for n in range(26)) + "```\n\n")
STUCK_PROMPT = "## Section\n\n" + PARAGRAPH * 2 + PROMPT + PARAGRAPH
STUCK_PROMPT_PAGES = 6        # the layout of STUCK_PROMPT before footers could grow to fill: it must not change
# The handbook's page count when footers learned to grow to fill a page (it was the same before). A footer never adds a
# page; raise this only when the text itself grows, never for a change of the footers.
BOOK = Path(__file__).resolve().parents[2] / "book"
BOOK_PAGES = 255


def test_a_prompt_that_moved_on_whole_leaves_a_footer_grown_to_the_last_line(tmp_path, monkeypatch):
    """The text is never trimmed to fit: when a prompt moves on whole, the footer of the page it left grows up to the
    last line (size `fill`) - and that is decided after the page is laid out, so the book keeps its page count."""
    report = lay_out(tmp_path, STUCK_PROMPT, monkeypatch)
    assert report["warnings"] == []
    filled = [foot for foot in report["feet"] if foot["size"] == "fill"]
    assert filled and all(foot["end"] == "stuck" and foot["blocker"] == "prompt" for foot in filled), report["feet"]
    assert all(foot["size"] != "l" for foot in report["feet"] if foot["blocker"] == "prompt")
    assert any(foot["mm"] > design.FOOT_HEIGHTS["l"] for foot in filled)  # the one exception to the size l
    for foot in filled:                                                   # up to the last line, with the usual air
        assert abs(foot["mm"] - min(design.FOOT_MAX, design.FOOT_HEIGHTS["s"] + foot["free"] - 2)) <= 1, foot
    assert report["pages"] == STUCK_PROMPT_PAGES


def test_footers_grown_to_fill_are_not_counted_among_the_large_ones():
    feet = [{"page": n, "chapter": "4", "size": "fill", "end": "stuck", "blocker": "prompt"} for n in range(5)]
    assert footer_warnings(feet) == []
    assert footer_warnings([{"page": 3, "chapter": "4", "size": "fill", "end": "stuck", "blocker": "table"}])


def test_footers_grown_to_fill_never_add_a_page_to_the_handbook(monkeypatch):
    """The whole handbook, laid out with its footers left empty (about ten seconds)."""
    if not (BOOK / "book.yml").is_file():
        pytest.skip("the handbook is not beside the tool")
    monkeypatch.setattr(rendering, "footers", lambda requests, vocabulary: ["<svg></svg>" for _ in requests])
    with tempfile.TemporaryDirectory() as work:
        source = Path(work) / "book.html"
        source.write_text(build_html(BOOK).html, encoding="utf-8")
        report = rendering.render(source)
    assert report["pages"] <= BOOK_PAGES
    assert any(foot["size"] == "fill" for foot in report["feet"])

"""`book audit` finds what it is meant to find, and nothing on a clean book.

Three kinds of test: tiny books built and audited end to end (a hole, a wide-gap line, a broken code chip, markup left
in the text, a table too wide, a clean book that passes); hand-made pages measured by `theme/audit.js` alone, one page
per check, so every browser check is shown to fire; and the checks that need no browser (the footers' moments and
frames, the version, the baseline), on their own.
"""
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from playwright.sync_api import sync_playwright

from bookkit import audit, design
from bookkit.art.worlds import WORLDS, frame, moment  # first: it loads the worlds
from bookkit.art.openers import Box  # noqa: E402
from bookkit.cli import main  # noqa: E402
from bookkit.config import LOCALES  # noqa: E402
from bookkit.markup import BuildError  # noqa: E402
from bookkit.render import _launch, footer_findings  # noqa: E402

CASES = yaml.safe_load((Path(__file__).parent / "fixtures" / "audit_cases.yml").read_text(encoding="utf-8"))
LOCALE = yaml.safe_load((LOCALES / "ru.yml").read_text(encoding="utf-8"))
FRONT = "---\ntitle: Test\nscene: fair\n---\n\n# Test\n\n"
SENTENCE = "The agent reads the repository, runs the build and checks its own work before it says that it is done. "
PARAGRAPH = SENTENCE * 5 + "\n\n"


def book(tmp_path: Path, text: str) -> Path:
    content = tmp_path / "book"
    (content / "01-a").mkdir(parents=True)
    (content / "book.yml").write_text("title: Test\nlanguage: ru\n", encoding="utf-8")
    (content / "01-a" / "00-chapter.md").write_text(FRONT + text, encoding="utf-8")
    return content


def audited(tmp_path: Path, text: str) -> list[dict]:
    return audit.run(book(tmp_path, text))["findings"]


def checks(found: list[dict], severity: str | None = None) -> set[str]:
    return {f["check"] for f in found if severity is None or f["severity"] == severity}


def serious(found: list[dict]) -> list[dict]:
    return [f for f in found if f["severity"] != "info"]


# ============================================================================ whole books
def test_a_clean_book_passes(tmp_path):
    text = "## Section\n\n" + (CASES["clean"] + " ") * 6 + "\n\n" + (CASES["clean"] + " ") * 4 + "\n"
    found = audited(tmp_path, text)
    assert serious(found) == [], serious(found)
    assert not audit.failed(found)
    assert checks(found) == {"last-page"}


def test_a_hole_above_the_footer_is_found_with_its_reason(tmp_path):
    chat = "```chat title=\"# team\"\n" + "".join(f"Anna · 10:{n:02d}: Message {n} of a thread that never splits.\n"
                                                for n in range(30)) + "```\n\n"
    found = audited(tmp_path, "## Section\n\n" + PARAGRAPH * 2 + chat + PARAGRAPH)
    holes = [f for f in found if f["check"] == "hole"]
    assert holes, serious(found)
    assert holes[0]["numbers"]["hole_mm"] > design.AUDIT_HOLE
    assert holes[0]["numbers"]["end"] == "stuck" and holes[0]["numbers"]["blocker"] != "prompt"
    assert "could not move up" in holes[0]["detail"]


def test_a_prompt_that_moved_on_whole_leaves_no_hole_the_footer_fills_it(tmp_path):
    prompt = "```prompt title=\"Long\"\n" + "".join(f"Line {n} of a prompt that has to stay whole on its monitor.\n"
                                          for n in range(26)) + "```\n\n"
    found = audited(tmp_path, "## Section\n\n" + PARAGRAPH * 2 + prompt + PARAGRAPH)
    assert [f for f in found if f["check"] == "hole"] == [], serious(found)
    assert [f for f in found if f["severity"] == "error"] == [], serious(found)


def test_a_line_with_wide_gaps_a_broken_code_chip_and_markup_left_over(tmp_path):
    words = " ".join(letter * 26 for letter in "bcdefgh")
    text = ("## Section\n\n" + PARAGRAPH + f"aaaa {words}.\n\n"
            "It runs `averyveryverylongidentifierwithoutanybreakopportunityatallthatgoesonandonandonforeverandever` "
            "and stops.\n\nSome **bold left open, a ::: fence and a TODO here.\n")
    found = audited(tmp_path, text)
    gaps = [f for f in found if f["check"] == "word-gap"]
    assert gaps and all(f["severity"] == "warning" for f in gaps)
    assert any(f["numbers"]["mean_em"] > design.AUDIT_GAP_MEAN for f in gaps)
    assert "code-break" in checks(found, "error")
    residue = {f["detail"] for f in found if f["check"] == "residue"}
    assert {'markup left in the text: "**"', 'markup left in the text: ":::"',
            'markup left in the text: "TODO"'} <= residue
    assert audit.failed(found)


def test_a_table_wider_than_the_page_is_found_by_the_audit_and_by_the_paginator(tmp_path):
    word = "x" * 140
    found = audited(tmp_path, f"## Section\n\n{PARAGRAPH}| A | B |\n|---|---|\n| {word} | b |\n")
    assert "table" in checks(found, "error")
    assert "off-sheet" in checks(found, "error")          # the paginator's own warning, now a finding


def test_the_command_exits_by_its_findings_and_writes_its_reports(tmp_path):
    clean = book(tmp_path / "clean", "## Section\n\n" + (CASES["clean"] + " ") * 5 + "\n")
    report, data = tmp_path / "report.md", tmp_path / "audit.json"
    assert main(["audit", "--content", str(clean), "--md", str(report), "--json", str(data)]) == 0
    assert report.read_text(encoding="utf-8").startswith("# Book audit")
    assert json.loads(data.read_text(encoding="utf-8"))["pages"] >= 1
    broken = book(tmp_path / "broken", "## Section\n\n" + PARAGRAPH + "A TODO left in the text.\n")
    sheets = tmp_path / "sheets"
    assert main(["audit", "--content", str(broken), "--sheets", str(sheets)]) == 1
    assert sorted(p.name for p in sheets.glob("*.png")) == ["audit-sheet-01.png"]


# ============================================================================ hand-made pages, audit.js alone
STYLE = """<style>body{margin:0;font:16px/1.5 serif}
.page{position:relative;width:210mm;height:297mm;overflow:hidden}
.p-body{position:absolute;top:24mm;left:20mm;width:172mm}
.p-foot{position:absolute;left:0;right:0;bottom:0;height:34mm}
.main > p, .main li{text-align:justify}
.rh-text{display:block;width:20mm;overflow:hidden;white-space:nowrap}</style>"""
FILL = ("<div class='row'><div class='main'><p>" + "Text that fills the page so that it is not blank. " * 40 +
        "</p></div></div>")
LEFT = "<p style='text-align:left;width:"
PAGES = {
    "line-start": LEFT + "60mm'>aaaa " + "b" * 76 + "<span style='display:inline-block'>,tail</span></p>",
    "dash-start": LEFT + "60mm'><span style='display:inline-block;width:58mm'>a</span> — bbb</p>",
    "double-hyphen": LEFT + "40mm'>" + "a" * 12 + "--" + "b" * 28 + "</p>",
    "number-break": LEFT + "30mm;word-break:break-all'>" + "1234567890" * 4 + "</p>",
    "code-break": LEFT + "30mm'><code style='overflow-wrap:anywhere'>"
                  "abcdefghijklmnopqrstuvwxyzabcdefghijkl</code></p>",
    "hanging-word": "<div class='main'><p>" + "Words that run over more than one line of the column. " * 4 +
                    "<br>ab.</p></div>",
    "note-overlap": "<div class='row'><div class='side'><aside style='height:20mm;width:40mm'>One</aside>"
                    "<aside style='height:20mm;width:40mm;margin-top:-10mm'>Two</aside></div></div>",
    "monitor": "<div class='prompt' style='width:60mm'><pre class='screen' style='width:50mm;height:50mm'>x</pre>"
               "</div>",
    "running-head": "<span class='rh-text'>A running head far too long for its place</span>",
    "image": "<img src='data:image/png;base64,AAAA' alt=''>",
    "svg-id": "<svg><defs><clipPath id='twice'></clipPath></defs></svg><svg><defs><clipPath id='twice'></clipPath>"
              "</defs><use href='#nowhere'></use></svg>",
    "heading-at-foot": "<div class='row' style='height:225mm'></div><div class='row row-heading'><h2>Late</h2></div>",
    "off-text-area": LEFT + "200mm'>" + "A line wider than the text block. " * 6 + "</p>",
    "page-weight": "<svg><desc>" + "x" * 700_000 + "</desc></svg>",
    "links": "<a href='ftp://example.com/x'>ftp</a> <a href='#nowhere'>here</a> <a href='https://nodot'>bad</a>"
             "<h2 id='target'>T</h2><span data-ref='target'>9</span>",
    "table": "<table style='width:300mm'><tr><td style='max-width:10mm;overflow:hidden;white-space:nowrap'>"
             "a cell far too long for its column</td></tr></table>",
    "residue": f"<p>{CASES['straight_quote']}</p><p>{CASES['hyphen_dash']}</p>",
    "blank-page": "<p>Short.</p>",
}


RAW = ("note-overlap", "heading-at-foot")          # rows of their own, straight in the text block


def _page(number: int, name: str) -> str:
    rows = PAGES[name]
    body = ("" if name in ("blank-page", "heading-at-foot") else FILL) + \
        (rows if name in RAW else f"<div class='row'><div class='main'>{rows}</div></div>")
    return (f"<div class='page recto' data-page='{number}' data-chapter='1'><div class='p-body'>{body}</div>"
            f"<footer class='p-foot'></footer></div>")


@pytest.fixture(scope="module")
def measured():
    names = list(PAGES)
    html = f"<html><head>{STYLE}</head><body><div id='book'>" + "".join(
        _page(n, name) for n, name in enumerate(names, 1)) \
        + "</div></body></html>"
    with sync_playwright() as playwright:
        browser = _launch(playwright)
        try:
            page = browser.new_page(viewport={"width": 800, "height": 1200})
            page.set_content(html)
            page.wait_for_load_state("load")
            result = page.evaluate((audit.THEME / "audit.js").read_text(encoding="utf-8"), audit.options())
        finally:
            browser.close()
    by_page: dict[str, list[dict]] = {name: [] for name in names}
    for item in result["findings"]:
        if item["page"]:
            by_page[names[item["page"] - 1]].append(item)
    return by_page


@pytest.mark.parametrize(("page", "check", "severity"), [
    ("line-start", "line-start", "error"),
    ("dash-start", "line-start", "warning"),
    ("double-hyphen", "double-hyphen", "error"),
    ("number-break", "number-break", "error"),
    ("code-break", "code-break", "error"),
    ("hanging-word", "hanging-word", "warning"),
    ("note-overlap", "note-overlap", "error"),
    ("monitor", "monitor", "error"),
    ("running-head", "running-head", "error"),
    ("image", "image", "error"),
    ("svg-id", "svg-id", "error"),
    ("heading-at-foot", "heading-at-foot", "error"),
    ("heading-at-foot", "section-start", "error"),
    ("off-text-area", "off-text-area", "error"),
    ("page-weight", "page-weight", "warning"),
    ("links", "links", "error"),
    ("table", "table", "error"),
    ("residue", "residue", "warning"),
    ("blank-page", "blank-page", "warning"),
    ("blank-page", "hole", "warning"),
])
def test_every_browser_check_fires_on_its_page(measured, page, check, severity):
    found = [f for f in measured[page] if f["check"] == check]
    assert found and all(f["severity"] == severity for f in found), measured[page]
    assert all(f["chapter"] == "1" and f["where"] is not None for f in found)


def test_the_hand_made_pages_find_exactly_what_they_hold(measured):
    assert {f["detail"] for f in measured["links"] if f["check"] == "links"} == {
        "a link that is not a well-formed http(s) address: ftp://example.com/x",
        'an internal link to "#nowhere" leads nowhere',
        "a link that is not a well-formed http(s) address: https://nodot",
        "the contents give page 9, the heading is on page 15"}
    residue = {f["detail"] for f in measured["residue"] if f["check"] == "residue"}
    assert residue == {'a straight quote " in Russian text; use «»', 'a hyphen used as a dash: " - "'}
    assert len([f for f in measured["svg-id"] if f["check"] == "svg-id"]) == 2
    assert all(f["rect"] for f in measured["line-start"])            # boxed on the contact sheet


# ============================================================================ without the browser
def _frames(place_a, place_b, seeds=(0, 0)):
    world = WORLDS["fair"]
    words = LOCALE["worlds"]["fair"]
    strips = [frame(world, 220, place, "right", 2, design.BLUE, words, seed)[1]
              for place, seed in zip((place_a, place_b), seeds, strict=True)]
    return [moment(world, place, strip) for place, strip in zip((place_a, place_b), strips, strict=True)]


def test_two_neighbouring_pages_with_one_moment_are_an_error():
    requests = [{"page": 30, "chapter": "2", "mm": 55}, {"page": 31, "chapter": "2", "mm": 55}]
    first = WORLDS["fair"].stations[0]
    found = audit.footer_checks(requests, _frames((0, first.beats[0]), (0, first.beats[0]), (0, 1)))
    assert [f["check"] for f in found] == ["footer-repeat"] and found[0]["severity"] == "error"
    assert found[0]["page"] == 31 and found[0]["rect"]["h"] > 0
    other = WORLDS["fair"].stations[1]
    assert audit.footer_checks(requests, _frames((0, first.beats[0]), (1, other.beats[0]))) == []


def test_the_same_picture_two_pages_apart_is_a_warning():
    requests = [{"page": 30, "chapter": "2", "mm": 55}, {"page": 32, "chapter": "2", "mm": 55}]
    first = WORLDS["fair"].stations[0]
    found = audit.footer_checks(requests, _frames((0, first.beats[0]), (0, first.beats[0])))
    assert [(f["check"], f["severity"]) for f in found] == [("footer-repeat", "warning")]


def test_a_footer_whose_drawing_breaks_its_own_rules_is_an_error():
    strip = SimpleNamespace(h=200, tall=120, reserved=[], boxes=[
        Box(10, 10, 100, 150, "cat", "a", "actor"), Box(50, 20, 160, 190, "crate", "b", "thing")])
    found = audit.footer_checks([{"page": 5, "chapter": "1", "mm": 55}],
                                [{"kind": "episode", "episode": "test", "strip": strip}])
    assert [f["check"] for f in found] == ["footer-frame"] and "cat overlaps crate" in found[0]["detail"]
    world = {"kind": "world", "world": "fair", "station": "x", "beat": "y",
             "strip": SimpleNamespace(h=200, tall=120, reserved=[], boxes=[Box(10, 150, 60, 199, "cat", "a", "actor")])}
    assert any("below the floor band" in fault for fault in audit.frame_faults(world))


def test_footer_sizes_are_reported_as_findings():
    found = footer_findings([{"page": 3, "chapter": "1", "size": "l", "end": "text"}])
    assert found == [{"page": 3, "chapter": "1", "where": "l text",
                      "detail": "page 3: a footer of size l where the next page's text could have filled the page"}]


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True,
                   capture_output=True)


def test_a_change_to_the_book_needs_a_higher_version(tmp_path):
    content = book(tmp_path, "## Section\n\nText.\n")
    (content / "book.yml").write_text("title: Test\nversion: 0.4-10.2026\n", encoding="utf-8")
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-qm", "base")
    assert audit.version_findings(content, "HEAD") == []                       # nothing changed
    (content / "01-a" / "00-chapter.md").write_text(FRONT + "## Section\n\nText, changed.\n", encoding="utf-8")
    stale = audit.version_findings(content, "HEAD")
    assert [f["check"] for f in stale] == ["version"] and "still 0.4-10.2026" in stale[0]["detail"]
    for version, expected in (("0.5-11.2026", None), ("1.0-11.2026", None), ("0.3-11.2026", "must go up"),
                              ("0.5-13.2026", "must look like")):
        (content / "book.yml").write_text(f"title: Test\nversion: {version}\n", encoding="utf-8")
        found = audit.version_findings(content, "HEAD")
        assert (found == []) if expected is None else expected in found[0]["detail"], (version, found)
    assert "no such commit" in audit.version_findings(content, "nowhere/main")[0]["detail"]


def _finding(check="hole", severity="warning", page=12, where="The  end of a PAGE", chapter="4"):
    return audit.finding(check, severity, "detail", page, chapter, where)


def test_the_baseline_matches_by_check_chapter_and_snippet_not_by_page():
    entries = [{"check": "hole", "chapter": "4", "where": "the end of a page", "reason": "the next prompt is long"},
               {"check": "hole", "chapter": "5", "where": "gone", "reason": "fixed since"}]
    found = [_finding(page=14), _finding(page=15), _finding("residue", "error", where="the end of a page")]
    stale = audit.apply_baseline(found, entries)
    assert [f["baselined"] for f in found] == [True, False, False]     # once each; an error never
    assert stale == [entries[1]]
    assert audit.failed(found)
    assert not audit.failed([found[0], _finding("last-page", "info")])


def test_a_baseline_entry_needs_its_reason(tmp_path):
    path = tmp_path / "baseline.json"
    path.write_text(json.dumps({"accepted": [{"check": "hole", "chapter": "4", "where": "x", "reason": ""}]}))
    with pytest.raises(BuildError, match="entry 1 .* has no reason"):
        audit.load_baseline(path)
    assert audit.load_baseline(path, strict=False)[0]["where"] == "x"
    path.write_text("[]")
    with pytest.raises(BuildError, match="list \"accepted\""):
        audit.load_baseline(path)


def test_writing_the_baseline_keeps_the_reasons_given(tmp_path):
    path = tmp_path / "baseline.json"
    old = [{"check": "hole", "chapter": "4", "where": "the end of a page", "reason": "kept"}]
    count = audit.write_baseline(path, [_finding(), _finding("word-gap", where="a b c"),
                                        _finding("code-break", "error")], old)
    written = json.loads(path.read_text(encoding="utf-8"))["accepted"]
    assert count == 2 and [(e["check"], e["reason"]) for e in written] == [("hole", "kept"), ("word-gap", "")]


def test_the_report_groups_by_severity_and_check():
    found = [_finding(), _finding(page=20), _finding("code-break", "error", page=7), _finding("last-page", "info")]
    text = audit.markdown({"pages": 30, "seconds": 3.0, "findings": found, "sheets": [], "stale": []})
    assert text.index("## Errors (1)") < text.index("## Warnings (2)") < text.index("## Notes (1)")
    assert "### hole (2)" in text and "Pages: 12, 20" in text


def test_every_check_is_described():
    sources = (audit.THEME / "audit.js").read_text(encoding="utf-8") + \
        (audit.THEME / "paginate.js").read_text(encoding="utf-8") + Path(audit.__file__).read_text(encoding="utf-8")
    import re
    used = set(re.findall(r"(?<![.\w])(?:add|warn)\(\s*'([a-z-]+)'", sources)) | \
        set(re.findall(r'finding\(\s*"([a-z-]+)"', sources))
    assert used and used <= set(audit.CHECKS), used - set(audit.CHECKS)

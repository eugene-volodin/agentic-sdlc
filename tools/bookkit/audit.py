"""`book audit`: a fast, deterministic check of the whole built handbook, deep enough to catch small layout defects.

One browser run lays the book out and draws its footers exactly as `book build` does, then measures the finished
pages (`theme/audit.js`): holes, wide word gaps, a line starting with a comma, inline code broken inside a token, a
heading at the foot of a page, a hanging short word, tables and monitors that do not fit, notes that touch, broken
pictures and ids, markup left in the text, links. Python adds what needs no browser: the footers' own checks for the
exact frame each page got, two neighbouring pages showing the same moment, the version.

Every finding is `{check, severity, page, chapter, where, detail, numbers, rect}`; `severity` is error, warning or
info. The command fails on any error and on any warning the baseline does not accept. The baseline
(`tools/audit-baseline.json`) lists accepted warnings, each with its reason, matched on (check, chapter, the snippet)
rather than on page numbers, which shift. Only the pages with something new on them get contact sheets: eight pages to
a PNG, each flagged region boxed in red - whoever reviews looks at those and nothing else.
"""
from __future__ import annotations

import base64
import json
import re
import subprocess
import tempfile
import time
import unicodedata
from collections import Counter
from html import escape
from pathlib import Path

import yaml

from . import design
from .markup import BuildError

THEME = Path(__file__).resolve().parent / "theme"
PX_PER_MM = 96 / 25.4
SEVERITIES = ("error", "warning", "info")
HEADINGS = {"error": "Errors", "warning": "Warnings", "info": "Notes"}

# What each check is about, for the report.
CHECKS = {
    "hole": "free space above the footer, on any page but a chapter's last",
    "word-gap": "wide gaps between the words of a justified line",
    "tail-under-note": "a paragraph's last line alone at full width under a note",
    "note-in-lead-in": "a note between a lead-in and the list it introduces",
    "note-below-block": "a note pushed below the block it belongs to",
    "into-picture": "text running into a drawing",
    "off-sheet": "text running off the sheet",
    "off-text-area": "text outside the text block",
    "code-break": "inline code broken across lines inside a token",
    "number-break": "a number broken across lines",
    "double-hyphen": "a doubled hyphen at a line end",
    "line-start": "a line starting with a punctuation mark or a dash",
    "heading-at-foot": "a heading at the foot of the text",
    "section-start": "a section starting at the foot of a page with less than two lines",
    "hanging-word": "a paragraph ending in one short word alone on its line",
    "table": "a table wider than its column or a cell that overflows",
    "monitor": "a prompt's monitor that is not 4:3, too wide, or cuts its text",
    "running-head": "a running head cut with an ellipsis",
    "image": "a picture that did not load",
    "svg-id": "an id used twice or a reference to a missing one",
    "note-overlap": "a note touching another note or a block",
    "footer-size": "a large footer where text could have filled the page, or too many in a chapter",
    "blank-page": "a near-blank page",
    "last-page": "the side the book ends on",
    "footer-repeat": "two neighbouring pages showing the same moment",
    "footer-frame": "a footer's own drawing checks (overlaps, cut characters, cables, containers)",
    "page-weight": "a page's markup heavy enough to run the browser out of memory",
    "residue": "markup or typing left in the text",
    "links": "a malformed link, a link leading nowhere, a wrong page in the contents",
    "version": "book/ changed without a new version",
    "too-tall": "a block taller than a page that cannot be split",
    "font": "a font that did not load",
    "build": "any other warning of the build",
}


def options(baseline: list[dict] | None = None, sheets: Path | None = None) -> dict:
    """The thresholds handed to the browser (all from design.py), and what the browser's side also needs."""
    return {
        "hole": design.AUDIT_HOLE, "gapMean": design.AUDIT_GAP_MEAN, "gapMax": design.AUDIT_GAP_MAX,
        "headingFoot": design.AUDIT_HEADING_FOOT, "sectionLines": design.AUDIT_SECTION_LINES,
        "shortWord": design.AUDIT_SHORT_WORD, "monitorRatio": design.AUDIT_MONITOR_RATIO,
        "noteAir": design.AUDIT_NOTE_AIR, "blank": design.AUDIT_BLANK, "slack": design.AUDIT_SLACK,
        "pageWeight": design.AUDIT_PAGE_WEIGHT, "bodyGap": design.BODY_GAP,
        "baseline": baseline or [], "sheets": str(sheets) if sheets else None,
    }


def finding(check: str, severity: str, detail: str, page: int = 0, chapter: str = "", where: str = "",
            numbers: dict | None = None, rect: dict | None = None) -> dict:
    return {"check": check, "severity": severity, "page": page, "chapter": str(chapter or ""),
            "where": " ".join(str(where or "").split())[:60], "detail": detail, "numbers": numbers or {}, "rect": rect}


# ============================================================================ in the browser's process
def in_browser(page, requests: list[dict], trace: list, report: dict, opts: dict) -> dict:
    """Run in `render.render`'s process once the footers are drawn: the browser's measurements, the paginator's own
    warnings, the footers' checks; then mark what the baseline accepts and draw the contact sheets."""
    from .render import footer_findings

    started = time.time()
    measured = page.evaluate((THEME / "audit.js").read_text(encoding="utf-8"), opts)
    found = [{**item, "numbers": item.get("numbers") or {}} for item in report.get("findings") or []]
    found += measured["findings"]
    timing = {name: round(ms / 1000, 2) for name, ms in measured["timing"].items()}
    found += [finding("footer-size", "error", item["detail"], item["page"], item["chapter"], item["where"],
                      rect=footer_rect(_foot(report, item["page"])))
              for item in footer_findings(report.get("feet") or [])]
    mark = time.time()
    found += footer_checks(requests, trace)
    timing["footers"] = round(time.time() - mark, 2)
    apply_baseline(found, opts.get("baseline") or [])
    sheets = []
    if opts.get("sheets"):
        mark = time.time()
        sheets = contact_sheets(page, found, Path(opts["sheets"]))
        timing["sheets"] = round(time.time() - mark, 2)
    timing["audit"] = round(time.time() - started, 2)
    return {"findings": found, "sheets": sheets, "timing": timing}


def _foot(report: dict, number: int) -> float:
    return next((float(foot["mm"]) for foot in report.get("feet") or [] if foot["page"] == number), 0.0)


def footer_rect(mm: float) -> dict | None:
    """A page's footer, in CSS pixels from the page's top left corner."""
    if not mm:
        return None
    return {"x": 0, "y": (design.PAGE_HEIGHT - mm) * PX_PER_MM, "w": design.PAGE_WIDTH * PX_PER_MM, "h": mm * PX_PER_MM}


def moment_name(moment: dict) -> str:
    station = moment.get("station")
    return f"{moment['world']} / {station} / {moment['beat']}" if station else f"{moment['world']} / finale"


def _key(moment: dict) -> tuple:
    return (moment["world"], moment.get("station"), moment.get("beat"))


def _composition(strip) -> tuple:
    """Who stands where and how big: two frames of one beat that differ here are another camera or cast."""
    return (tuple(sorted(b.name for b in strip.boxes if b.kind == "actor")), round(strip.tall),
            bool(getattr(strip, "mirror", False)))


def footer_checks(requests: list[dict], trace: list) -> list[dict]:
    """Two neighbouring pages never show one moment, and every footer drawn passes its own drawing checks for the
    exact height, side and seed it was drawn at: a text change moves the heights, and a frame never drawn at that
    height by the tests may break."""
    found: list[dict] = []
    drawn = [(request, moment) for request, moment in zip(requests, trace, strict=False) if moment]
    for nth, (request, moment) in enumerate(drawn):
        page, chapter = int(request["page"]), str(request.get("chapter") or "")
        rect = footer_rect(float(request["mm"]))
        for later in drawn[nth + 1:nth + 3]:
            gap = int(later[0]["page"]) - page
            if gap > 2 or _key(later[1]) != _key(moment):
                continue
            same = _composition(later[1]["strip"]) == _composition(moment["strip"])
            if gap == 1:
                found.append(finding("footer-repeat", "error",
                                     f"pages {page} and {page + 1} show the same moment ({moment_name(moment)})"
                                     + ("" if same else ", with another cast or camera"),
                                     page + 1, chapter, moment_name(moment), rect=rect))
            elif same:
                found.append(finding("footer-repeat", "warning", f"pages {page} and {page + 2} show the same picture "
                                     f"({moment_name(moment)})", page + 2, chapter, moment_name(moment), rect=rect))
        for fault in frame_faults(moment):
            found.append(finding("footer-frame", "error", f"{moment_name(moment)}: {fault}", page, chapter,
                                 f"{moment_name(moment)}: {fault}", rect=rect))
    return found


def frame_faults(moment: dict) -> list[str]:
    """The checks the tests run on every frame (tests/test_footers.py, test_worlds.py, test_world_kit.py,
    test_world_frames.py), for this one frame."""
    from .art.footers import footer_conflicts
    from .art.openers import W
    from .art.world_kit import container_faults, link_faults

    strip = moment["strip"]
    faults = list(footer_conflicts(strip))
    if moment.get("kind") == "world":
        faults += container_faults(strip) + link_faults(strip)
        floor = strip.h * (1 - design.AUDIT_FLOOR)
        for b in strip.boxes:
            if b.kind == "actor" and b.bottom > floor + 0.5:
                faults.append(f"{b.name} stands below the floor band ({b.bottom:.0f} > {floor:.0f})")
            if b.top < -0.5 or b.bottom > strip.h + 0.5 or b.left < -0.5 or b.right > W + 0.5:
                faults.append(f"{b.name} is cut by the frame")
    return list(dict.fromkeys(faults))


# ============================================================================ contact sheets
def contact_sheets(page, found: list[dict], folder: Path) -> list[dict]:
    """Small pictures of the pages with something new on them: `AUDIT_SHEET_PAGES` to a PNG at `AUDIT_SHEET_SCALE`,
    each flagged region boxed in red. Only the page being shot is painted (as `render` takes its proofs)."""
    from .render import relieve_memory

    flagged: dict[int, list[dict]] = {}
    for item in found:
        if item["page"] and item["severity"] != "info" and not item.get("baselined"):
            flagged.setdefault(item["page"], []).append(item)
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("audit-sheet-*.png"):
        old.unlink()
    if not flagged:
        return []
    page.add_style_tag(content=".page.unshot { content-visibility: hidden; }"
                               f".audit-box {{ position: absolute; z-index: 999; box-sizing: border-box;"
                               f" border: 1.2mm solid {design.RED}; pointer-events: none; }}")
    page.evaluate("() => document.querySelectorAll('#book > .page').forEach(p => p.classList.add('unshot'))")
    cdp = page.context.new_cdp_session(page)
    shots: list[tuple[int, str, list[dict]]] = []
    for nth, (number, items) in enumerate(sorted(flagged.items()), 1):
        element = page.query_selector(f'#book > .page[data-page="{number}"]')
        if element is None:
            continue
        boxes = [item["rect"] for item in items if item.get("rect")]
        element.evaluate("""(el, boxes) => {
            el.classList.remove('unshot');
            for (const b of boxes) {
              const mark = document.createElement('div');
              mark.className = 'audit-box';
              mark.style.cssText = `left:${b.x - 4}px;top:${b.y - 4}px;width:${b.w + 8}px;height:${b.h + 8}px`;
              el.append(mark);
            }
        }""", boxes)
        png = element.screenshot(type="png")
        element.evaluate("el => { el.querySelectorAll('.audit-box').forEach(m => m.remove()); "
                         "el.classList.add('unshot'); }")
        shots.append((number, base64.b64encode(png).decode("ascii"), items))
        if nth % 20 == 0:
            relieve_memory(cdp)
    cdp.detach()
    page.evaluate("() => document.querySelectorAll('#book > .page').forEach(p => p.classList.remove('unshot'))")
    width = round(design.PAGE_WIDTH * PX_PER_MM * design.AUDIT_SHEET_SCALE)
    per = design.AUDIT_SHEET_PAGES
    columns = (per + 1) // 2
    sheet_page = page.context.browser.new_page(viewport={"width": columns * (width + 12) + 12, "height": 600})
    sheets: list[dict] = []
    try:
        for start in range(0, len(shots), per):
            group = shots[start:start + per]
            cells = "".join(
                f"<figure><img src='data:image/png;base64,{data}'><figcaption><b>{number}</b> "
                f"{escape(', '.join(sorted({item['check'] for item in items})), quote=False)}</figcaption></figure>"
                for number, data, items in group)
            sheet_page.set_content(
                f"<html><body style='margin:0;padding:12px;background:{design.DESK};font:600 12px sans-serif;"
                f"color:{design.WHITE}'><div style='display:grid;grid-template-columns:repeat({columns},{width}px);"
                f"gap:12px'>{cells}</div><style>img{{width:{width}px;display:block}}figure{{margin:0}}"
                f"figcaption{{padding:3px 0;line-height:1.3}}</style></body></html>")
            target = folder / f"audit-sheet-{start // per + 1:02d}.png"
            sheet_page.screenshot(path=str(target), full_page=True)
            sheets.append({"path": str(target), "pages": [number for number, _, _ in group]})
    finally:
        sheet_page.close()
    return sheets


# ============================================================================ checks without the browser
VERSION = re.compile(r"(\d+)\.(\d+)-(0[1-9]|1[0-2])\.(\d{4})")


def version_findings(content: Path, base: str) -> list[dict]:
    """Anything under book/ changed against `base` (a git ref) needs a new `version:` in book.yml - higher than
    the base's, in the form MAJOR.MINOR-MM.YYYY."""
    def git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(content), *args], capture_output=True, text=True, check=False)

    top = git("rev-parse", "--show-toplevel")
    if top.returncode:
        return [finding("version", "error", f"cannot compare with {base}: {content} is not in a git repository")]
    root = Path(top.stdout.strip())
    inside = content.resolve().relative_to(root.resolve()).as_posix()
    if git("rev-parse", "--verify", "--quiet", f"{base}^{{commit}}").returncode:
        return [finding("version", "error", f"cannot compare with {base}: no such commit (fetch it first)")]
    changed = [line for line in git("diff", "--name-only", base, "--", ".").stdout.splitlines() if line.strip()]
    changed += [line for line in git("ls-files", "--others", "--exclude-standard", "--", ".").stdout.splitlines()
                if line.strip()]
    if not changed:
        return []
    new = _version_of((content / "book.yml").read_text(encoding="utf-8"))
    shown = git("show", f"{base}:{inside + '/' if inside != '.' else ''}book.yml")
    old = _version_of(shown.stdout) if not shown.returncode else ""
    where = f"{len(changed)} file(s) changed"
    if not VERSION.fullmatch(new):
        return [finding("version", "error", f"book.yml: the version must look like 1.4-10.2026 (MAJOR.MINOR-MM.YYYY), "
                                            f"got {new!r}", where=where)]
    if old == new:
        return [finding("version", "error", f"book/ changed against {base} ({', '.join(changed[:3])}"
                                            f"{', ...' if len(changed) > 3 else ''}) but its version is still {new}: "
                                            f"raise MINOR and set the month", where=where)]
    if VERSION.fullmatch(old) and _version_order(new) <= _version_order(old):
        return [finding("version", "error", f"the version went from {old} to {new}: it must go up", where=where)]
    return []


def _version_of(text: str) -> str:
    """`version:` of a book.yml's text; "" when it has none or is not a mapping of valid YAML."""
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError:
        return ""
    return str(raw.get("version", "")).strip() if isinstance(raw, dict) else ""


def _version_order(version: str) -> tuple[int, int]:
    major, minor, _, _ = VERSION.fullmatch(version).groups()
    return int(major), int(minor)


# ============================================================================ the baseline
def normalise(text: str) -> str:
    """A snippet as the baseline matches it: the same words, whatever the spaces, the case and the line breaks."""
    text = unicodedata.normalize("NFKC", str(text or "")).replace("\u00ad", "")
    return " ".join(text.lower().split())[:60]


def baseline_key(item: dict) -> tuple[str, str, str]:
    return item["check"], str(item.get("chapter") or ""), normalise(item.get("where", ""))


def load_baseline(path: Path, strict: bool = True) -> list[dict]:
    """The accepted findings, each with its reason. A broken file is an error naming the entry; `strict=False` lets
    an entry without its reason through (to keep the reasons when the baseline is written anew)."""
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BuildError(f"{path}: cannot read the baseline: {error}") from error
    entries = data.get("accepted") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        raise BuildError(f"{path}: the baseline must be an object with a list \"accepted\"")
    for nth, entry in enumerate(entries, 1):
        if not isinstance(entry, dict) or not all(isinstance(entry.get(k), str) for k in ("check", "chapter", "where")):
            raise BuildError(f"{path}: entry {nth} needs the strings check, chapter and where")
        reason = str(entry.get("reason") or "").strip()
        if strict and (not reason or reason.upper().startswith("TODO")):
            raise BuildError(f"{path}: entry {nth} ({entry['check']}, {entry['where']!r}) has no reason; say why it is "
                             f"accepted, or fix it and drop the entry")
    return entries


def apply_baseline(found: list[dict], entries: list[dict]) -> list[dict]:
    """Mark the warnings the baseline accepts (`baselined`); errors are never accepted. Returns the entries that matched
    nothing - stale, to be dropped."""
    left = Counter(baseline_key(entry) for entry in entries)
    for item in found:
        key = baseline_key(item)
        item["baselined"] = item["severity"] == "warning" and left[key] > 0
        if item["baselined"]:
            left[key] -= 1
    stale = []
    for entry in entries:
        key = baseline_key(entry)
        if left[key] > 0:
            stale.append(entry)
            left[key] -= 1
    return stale


def write_baseline(path: Path, found: list[dict], old: list[dict]) -> int:
    """Every warning found, keeping the reasons of entries already accepted; a new one gets an empty reason to fill."""
    reasons: dict[tuple, list[str]] = {}
    for entry in old:
        reasons.setdefault(baseline_key(entry), []).append(entry.get("reason", ""))
    accepted = []
    for item in sorted((f for f in found if f["severity"] == "warning"), key=lambda f: (f["check"], f["page"])):
        known = reasons.get(baseline_key(item)) or []
        accepted.append({"check": item["check"], "chapter": item["chapter"], "where": item["where"],
                         "page": item["page"], "detail": item["detail"], "reason": known.pop(0) if known else ""})
    path.write_text(json.dumps({"accepted": accepted}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(accepted)


# ============================================================================ reports
def markdown(result: dict) -> str:
    """The report: a summary, then the findings grouped by severity and check, with their pages."""
    found = result["findings"]
    new = [f for f in found if not f.get("baselined")]
    counts = Counter(f["severity"] for f in new)
    lines = ["# Book audit", "",
             f"{result['pages']} pages, {result['seconds']:.0f} s. "
             f"**{counts['error']} error(s), {counts['warning']} new warning(s)**, "
             f"{sum(1 for f in found if f.get('baselined'))} accepted by the baseline, {counts['info']} note(s).", ""]
    if result.get("layout"):
        lines += [f"Layout fingerprint `{result['layout']['fingerprint']}`, laid out in {result.get('browser')}: "
                  f"the same text and line breaks give the same fingerprint on every machine.", ""]
    if result.get("sheets"):
        lines += ["Contact sheets of the flagged pages: " +
                  ", ".join(f"`{Path(s['path']).name}` (pages {', '.join(map(str, s['pages']))})"
                            for s in result["sheets"]), ""]
    for severity in SEVERITIES:
        items = [f for f in new if f["severity"] == severity]
        if not items:
            continue
        lines += [f"## {HEADINGS[severity]} ({len(items)})", ""]
        for check in sorted({f["check"] for f in items}, key=lambda c: (-sum(f["check"] == c for f in items), c)):
            group = sorted((f for f in items if f["check"] == check), key=lambda f: f["page"])
            pages = sorted({f["page"] for f in group if f["page"]})
            lines += [f"### {check} ({len(group)}): {CHECKS.get(check, '')}", ""]
            if pages:
                lines += [f"Pages: {', '.join(map(str, pages))}", ""]
            for f in group:
                where = f" «{f['where']}»" if f["where"] and f["where"] not in f["detail"] else ""
                page = f"p. {f['page']}: " if f["page"] else ""
                lines.append(f"- {page}{f['detail']}{where}")
            lines.append("")
    accepted = [f for f in found if f.get("baselined")]
    if accepted:
        lines += [f"## Accepted by the baseline ({len(accepted)})", ""]
        for check, count in sorted(Counter(f["check"] for f in accepted).items()):
            lines.append(f"- {check}: {count}")
        lines.append("")
    if result.get("stale"):
        lines += [f"## Baseline entries no longer found ({len(result['stale'])}): drop them", ""]
        lines += [f"- {e['check']} ({e['chapter'] or 'front'}): «{e['where']}»" for e in result["stale"]]
        lines.append("")
    return "\n".join(lines)


def summary(result: dict) -> str:
    """A few lines for the terminal."""
    found = result["findings"]
    new = [f for f in found if not f.get("baselined")]
    out = []
    for severity in SEVERITIES:
        by_check = Counter(f["check"] for f in new if f["severity"] == severity)
        if by_check:
            listed = ", ".join(f"{check} {count}" for check, count in by_check.most_common())
            out.append(f"  {HEADINGS[severity].lower()}: {listed}")
    accepted = sum(1 for f in found if f.get("baselined"))
    head = (f"audit: {result['pages']} pages in {result['seconds']:.0f} s - "
            f"{sum(f['severity'] == 'error' for f in new)} error(s), {sum(f['severity'] == 'warning' for f in new)} "
            f"new warning(s), {accepted} accepted")
    layout = result.get("layout") or {}
    if layout:
        out.append(f"  layout: {layout['fingerprint']} in {result.get('browser')}")
    return "\n".join([head, *out])


def failed(found: list[dict]) -> bool:
    """Any error, or any warning the baseline does not accept."""
    return any(f["severity"] == "error" or f["severity"] == "warning" and not f.get("baselined") for f in found)


# ============================================================================ the command
def run(content: Path, *, only: str | None = None, baseline: Path | None = None, base: str | None = None,
        sheets: Path | None = None, pdf: Path | None = None) -> dict:
    """Build and audit the book in `content`.

    Returns `{"pages", "seconds", "findings", "sheets", "stale", "timing", "browser", "layout"}`."""
    from .compiler import build_html
    from .render import render_isolated

    started = time.time()
    entries = load_baseline(baseline) if baseline else []
    result = build_html(content, only=only)          # book.yml and the chapters are read and checked first
    found = version_findings(content, base) if base else []
    with tempfile.TemporaryDirectory(prefix="bookkit-audit-") as work:
        source = Path(work) / "book.html"
        source.write_text(result.html, encoding="utf-8")
        if pdf:
            pdf.parent.mkdir(parents=True, exist_ok=True)
        report = render_isolated(source, pdf, None, None, vocabulary=result.config.vocabulary(),
                                 audit=options(entries, sheets))
    audit = report["audit"]
    found += audit["findings"]
    known = {f["detail"] for f in found}
    for warning in report["warnings"]:             # anything the build warned about and no check above reported
        if warning not in known:
            found.append(finding("build", "error", warning, where=warning))
    stale = apply_baseline(found, entries)
    return {"pages": report["pages"], "seconds": round(time.time() - started, 1), "findings": found,
            "sheets": audit["sheets"], "stale": stale, "timing": audit["timing"],
            "browser": report.get("browser", ""), "layout": report.get("layout", {})}

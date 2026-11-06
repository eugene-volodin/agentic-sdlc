"""Rendering through a real browser (Playwright): paginate, illustrate, print to PDF, take PNG proofs."""
from __future__ import annotations

import contextlib
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from . import design
from .art.footers import footers
from .art.ink import id_scope
from .markup import BuildError

CSS_PX_PER_MM = 96 / 25.4
PAGE_VIEWPORT = {"width": round(design.PAGE_WIDTH * CSS_PX_PER_MM),
                 "height": round(design.PAGE_HEIGHT * CSS_PX_PER_MM)}


RUN_SWITCH = "bookkit-run"   # `--bookkit-run=<run>` marks the browsers of one isolated render, so a stopped build
                              # can find and end them


def _launch(playwright):
    """Prefer the installed Chrome; fall back to Playwright's own Chromium."""
    run = os.environ.get("BOOKKIT_RUN")
    args = [f"--{RUN_SWITCH}={run}"] if run else []
    try:
        return playwright.chromium.launch(channel="chrome", args=args)
    except PlaywrightError:
        try:
            return playwright.chromium.launch(args=args)
        except PlaywrightError as error:
            raise BuildError("no browser available: install Google Chrome or run "
                             "'uv run playwright install chromium'") from error


# How long each step may take before the build gives up with an error instead of waiting for ever. The whole
# handbook lays out in about a second and prints in about four; these leave room for a slow or busy machine.
LOAD_TIMEOUT = 60_000        # ms: open the page, load fonts and pictures
LAYOUT_TIMEOUT = 180_000     # ms: paginate
PRINT_TIMEOUT = 300_000      # ms: print the PDF, take the proofs


def _open(playwright, html_path: Path, viewport: dict, scale: float, problems: list[str] | None = None):
    """Open the page. Whatever goes wrong inside it - a script error, a console error, a crash - is collected in
    `problems` (when given) and reported by the build, never just printed and forgotten."""
    browser = _launch(playwright)
    page = browser.new_page(viewport=viewport, device_scale_factor=scale)
    page.set_default_timeout(PRINT_TIMEOUT)
    report = problems.append if problems is not None else (lambda text: print(f"  [browser] {text}"))
    page.on("console", lambda m: report(f"browser: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: report(f"browser: {e}"))
    page.on("crash", lambda _: report("browser: the page crashed"))
    try:
        page.goto(html_path.resolve().as_uri(), timeout=LOAD_TIMEOUT)
    except PlaywrightError as error:
        browser.close()
        raise BuildError(f"the browser could not open the book: {_first_line(error)}") from error
    return browser, page


def _first_line(error: Exception) -> str:
    return str(error).strip().split("\n")[0][:300]


def render(html_path: Path, pdf_path: Path | None = None, shots_dir: Path | None = None,
           pages: list[int] | None = None, scale: float = 1.0, vocabulary: dict | None = None,
           frames_dir: Path | None = None, audit: dict | None = None) -> dict:
    """Lay the book out, draw the footer scenes, then write the PDF and/or page PNGs.

    Returns the paginator's report: `{"pages": N, "warnings": [...], "shots": [...]}`. The PDF appears in one
    piece or not at all: it is printed beside its place and moved there when complete, so a reader or a second
    build never sees half a file. With `audit` (the options of `book audit`, `audit.py`) the finished pages are
    measured as well, and the report gets `"audit": {"findings": [...], "sheets": [...], ...}`.
    """
    problems: list[str] = []
    printed = False
    step = "starting the browser"
    partial = pdf_path.with_name(f".{pdf_path.name}.partial") if pdf_path else None
    try:
        with sync_playwright() as playwright:
            browser, page = _open(playwright, html_path, PAGE_VIEWPORT, scale, problems)
            try:
                step = "laying out the pages"
                page.wait_for_function("window.__bookReady === true", timeout=LAYOUT_TIMEOUT, polling=100)
                error = page.evaluate("window.__bookError || null")
                if error:
                    raise BuildError(f"pagination failed in the browser: {error}")
                # The paginator reports each page's footer height and its text; an episode is drawn for each page
                # (`vocabulary` is the locale's `footers:`, the topic words and lettering of the episodes).
                step = "drawing the footer scenes"
                requests = page.evaluate("window.__bookScenes")
                id_scope("f")                    # the page's own drawings were numbered by the compiler
                trace: list | None = [] if audit is not None else None
                scenes = footers(requests, vocabulary or {}, trace) if audit is not None else \
                    footers(requests, vocabulary or {})
                clash = page.evaluate("list => window.__setScenes(list)", scenes)
                if clash:
                    raise BuildError(f"the drawings could not be given unique ids: {clash}")
                report = page.evaluate("window.__bookReport")
                report["warnings"] += footer_warnings(report.get("feet", []))
                report["shots"] = []
                if audit is not None:
                    from . import audit as auditing
                    step = "auditing the pages"
                    report["audit"] = auditing.in_browser(page, requests, trace or [], report, audit)
                if frames_dir:
                    step = "taking the storyboard frames"
                    frames_dir.mkdir(parents=True, exist_ok=True)
                    report["frames"] = []
                    for nth, element in enumerate(page.query_selector_all(".opener, .p-foot")):
                        target = frames_dir / f"frame-{nth:03d}.png"
                        element.screenshot(path=str(target))
                        number = element.evaluate("el => el.closest('.page').dataset.page")
                        report["frames"].append({"path": str(target), "page": number,
                                                 "opener": element.evaluate("el => el.matches('.opener')")})
                # The proofs are taken before printing: after a print of the whole book the page has no memory
                # left for two hundred screenshots, and the browser crashes.
                if shots_dir:
                    step = "taking the page proofs"
                    shots_dir.mkdir(parents=True, exist_ok=True)
                    # Only the page being shot is painted: the whole book painted at once ran the browser out of
                    # memory once the worlds grew detailed. The layout is untouched, so the PDF below is not.
                    page.add_style_tag(content=".page.unshot { content-visibility: hidden; }")
                    cdp = page.context.new_cdp_session(page)
                    page.evaluate("() => document.querySelectorAll('.page').forEach(p => p.classList.add('unshot'))")
                    for number, element in enumerate(page.query_selector_all(".page"), 1):
                        if pages and number not in pages:
                            continue
                        target = shots_dir / f"page-{number:03d}.png"
                        element.evaluate("el => el.classList.remove('unshot')")
                        element.screenshot(path=str(target))
                        element.evaluate("el => el.classList.add('unshot')")
                        report["shots"].append(str(target))
                        if number % 20 == 0:             # let the browser drop the rasters of the pages shot so far
                            cdp.send("Memory.simulatePressureNotification", {"level": "critical"})
                            cdp.send("HeapProfiler.collectGarbage")
                    page.evaluate("() => document.querySelectorAll('.page').forEach(p => p.classList.remove('unshot'))")
                if pdf_path:
                    step = "printing the PDF"
                    page.pdf(path=str(partial), prefer_css_page_size=True, print_background=True,
                             outline=True, tagged=True)
                    pictures = page.evaluate("new Set([...document.images].map(i => i.currentSrc)).size")
                    report["warnings"] += _raster_warnings(partial, pictures, pdf_path.name)
                    report["warnings"] += _font_warnings(partial, pdf_path.name)
                    printed = True
            finally:
                browser.close()
    except PlaywrightError as error:
        raise BuildError(f"the browser failed while {step}: {_first_line(error)}"
                         + (f" ({problems[-1]})" if problems else "")) from error
    finally:
        if partial and printed:
            partial.replace(pdf_path)
        elif partial:
            partial.unlink(missing_ok=True)
    report["warnings"] += problems
    report["problems"] = problems
    return report


def footer_warnings(feet: list[dict]) -> list[str]:
    """`footer_findings`, as the build prints them."""
    return [finding["detail"] for finding in footer_findings(feet)]


def footer_findings(feet: list[dict]) -> list[dict]:
    """A page is for content: an illustration never takes a half or a third of a page.
    The paginator gives a footer scene of size l only when the next block cannot move up or the chapter breaks the
    page itself, and a panorama only on the last page of a chapter; more than `FOOT_LARGE_MAX` large footers before
    blocks that could not move up in one chapter is a layout to fix, and anything larger than m before running text is
    a paginator error. A footer grown up to the last line (`fill`) is allowed only before a prompt that moved on whole
    and is not counted among the large ones. `feet` is the paginator's report: one entry per footer."""
    problems: list[dict] = []
    large: dict[str, list[dict]] = {}
    for foot in feet:
        size, end = foot.get("size"), foot.get("end")
        if size == "panorama" and end != "last" or size in ("l", "panorama") and end == "text":
            problems.append({"page": foot["page"], "chapter": str(foot.get("chapter") or ""), "where": f"{size} {end}",
                             "detail": f"page {foot['page']}: a footer of size {size} where the next page's text "
                                       f"could have filled the page"})
        elif size == "fill" and not (end == "stuck" and foot.get("blocker") == "prompt"):
            problems.append({"page": foot["page"], "chapter": str(foot.get("chapter") or ""), "where": f"{size} {end}",
                             "detail": f"page {foot['page']}: a footer grown to fill the page where no prompt "
                                       f"moved on whole"})
        elif size == "l" and end == "stuck":
            large.setdefault(str(foot.get("chapter") or ""), []).append(foot)
    for chapter, pages in large.items():
        if len(pages) > design.FOOT_LARGE_MAX:
            listed = ", ".join(f"{foot['page']} ({foot.get('blocker') or 'block'})" for foot in pages)
            detail = (f"chapter {chapter or '(front)'}: {len(pages)} pages end with a large footer (l), at most "
                      f"{design.FOOT_LARGE_MAX} allowed; the next block could not move up on pages {listed}")
            problems.append({"page": pages[-1]["page"], "chapter": chapter, "where": f"{len(pages)} large footers",
                             "detail": detail})
    return problems


OBJECT = re.compile(rb"(\d+) 0 obj\b")
IMAGE = re.compile(rb"/Subtype\s*/Image\b")
SOFT_MASK = re.compile(rb"/SMask\s+(\d+) 0 R")


def _raster_warnings(pdf_path: Path, pictures: int, name: str = "") -> list[str]:
    """Chrome cannot print some things as vectors - an SVG mask or filter, a gradient fading to transparent, a
    gradient background clipped to rounded corners - and puts a low-resolution raster into the PDF instead, which
    Apple's viewers (iOS, Telegram, Preview) draw torn. The book's only rasters are its `<img>` pictures, so every
    other image in the PDF is such a fallback. `pictures` is the number of distinct `<img>` sources."""
    data = pdf_path.read_bytes()
    images: dict[bytes, bytes] = {}
    for found in IMAGE.finditer(data):          # an image's dictionary: from its "N 0 obj" to its "stream"
        head = data.rfind(b" 0 obj", 0, found.start())
        start = data.rfind(b"\n", 0, head) + 1
        number = OBJECT.match(data, start)
        if number:
            images[number.group(1)] = data[start:data.find(b"stream", found.end())]
    masks = {ref for body in images.values() for ref in SOFT_MASK.findall(body)}
    extra = len(set(images) - masks) - pictures
    if extra <= 0:
        return []
    return [f"{name or pdf_path.name}: {extra} drawing(s) printed as a raster (an SVG mask or filter, a gradient "
            f"fading to transparent, or a gradient background with rounded corners); Apple PDF viewers draw them torn"]


BUILD_TIMEOUT = 15 * 60     # seconds: the browser's whole part of a build, the last resort where nothing else reaches


def render_isolated(html_path: Path, pdf_path: Path | None = None, shots_dir: Path | None = None,
                    pages: list[int] | None = None, scale: float = 1.0, vocabulary: dict | None = None,
                    timeout: float = BUILD_TIMEOUT, run: str = "", frames_dir: Path | None = None,
                    audit: dict | None = None) -> dict:
    """`render` in a process of its own, stopped with an error if it outlives `timeout`.

    A page whose script never returns blocks the browser's own timeouts and Python's signals alike; only killing
    the process frees the build. Its browser, started in a process group of its own, is found by the mark
    `RUN_SWITCH` and ended with it.
    """
    with tempfile.TemporaryDirectory(prefix="bookkit-render-") as work:
        job, result = Path(work) / "job.json", Path(work) / "report.json"
        job.write_text(json.dumps({"html": str(html_path), "pdf": str(pdf_path) if pdf_path else None,
                                   "shots": str(shots_dir) if shots_dir else None, "pages": pages, "scale": scale,
                                   "vocabulary": vocabulary or {}, "report": str(result),
                                   "frames": str(frames_dir) if frames_dir else None, "audit": audit}),
                       encoding="utf-8")
        run = run or Path(work).name             # marks this render's browser; a test may name it
        child = subprocess.Popen([sys.executable, "-m", "bookkit.render", str(job)], start_new_session=True,
                                 cwd=Path(__file__).resolve().parent.parent, env={**os.environ, "BOOKKIT_RUN": run})

        def stop() -> None:
            with contextlib.suppress(ProcessLookupError):     # it may have ended on its own meanwhile
                os.killpg(child.pid, signal.SIGKILL)
            child.wait()
            # The browser runs in a process group of its own: end it by the mark it was started with.
            subprocess.run(["pkill", "-KILL", "-f", f"{RUN_SWITCH}={run}"], check=False)
            if pdf_path:
                pdf_path.with_name(f".{pdf_path.name}.partial").unlink(missing_ok=True)

        try:
            code = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            stop()
            raise BuildError(f"the browser did not finish in {timeout:.0f} s and was stopped; something hangs - "
                             f"build one chapter at a time with --only to find which") from None
        except BaseException:          # Ctrl+C: the browser's process is in a session of its own and would live on
            stop()
            raise
        if not result.exists():
            raise BuildError(f"the browser's part of the build failed (exit code {code}); see the messages above")
        outcome = json.loads(result.read_text(encoding="utf-8"))
    if "error" in outcome:
        raise BuildError(outcome["error"])
    return outcome


def _child(job_path: str) -> int:
    """The other end of `render_isolated`: run one render and leave its report (or its error) in a file."""
    job = json.loads(Path(job_path).read_text(encoding="utf-8"))
    try:
        outcome = render(Path(job["html"]), Path(job["pdf"]) if job["pdf"] else None,
                         Path(job["shots"]) if job["shots"] else None, job["pages"], job["scale"], job["vocabulary"],
                         Path(job["frames"]) if job.get("frames") else None, job.get("audit"))
    except BuildError as error:
        outcome = {"error": str(error)}
    except Exception as error:     # a fault of the tool, not of the book: its traceback goes to the console
        traceback.print_exc()
        outcome = {"error": f"the browser's part of the build failed: {type(error).__name__}: {error}"}
    Path(job["report"]).write_text(json.dumps(outcome), encoding="utf-8")
    return 0


FONTS = Path(__file__).resolve().parent / "theme" / "fonts"
BASE_FONT = re.compile(rb"/BaseFont\s*/(?:[A-Z]{6}\+)?([^\s/<>\[\]()]+)")


def _font_warnings(pdf_path: Path, name: str = "") -> list[str]:
    """Every glyph must come from the book's own fonts. One they lack is drawn by the browser from a font of the
    machine that builds - another face on another machine, or a box where nothing is found."""
    families = {font.stem.split("-")[0] for font in FONTS.glob("*.ttf")}
    used = {match.decode("latin-1") for match in BASE_FONT.findall(pdf_path.read_bytes())}
    foreign = sorted(font for font in used if not font.startswith(tuple(families)))
    if not foreign:
        return []
    return [f"{name or pdf_path.name}: text set in a font of this machine, not the book's: {', '.join(foreign)}; "
            f"some character is missing from the book's fonts - draw it or set it in a font that has it"]


def screenshot_html(markup: str, out: Path, width: int = 1200, height: int = 800, scale: float = 1.0) -> Path:
    """Screenshot arbitrary HTML (used for the character sheet)."""
    temp = out.with_suffix(".html")
    temp.write_text(markup, encoding="utf-8")
    try:
        with sync_playwright() as playwright:
            browser, page = _open(playwright, temp, {"width": width, "height": height}, scale)
            try:
                page.wait_for_timeout(300)
                page.screenshot(path=str(out), full_page=True)
            finally:
                browser.close()
    except PlaywrightError as error:
        raise BuildError(f"the browser could not take {out.name}: {_first_line(error)}") from error
    finally:
        temp.unlink(missing_ok=True)
    return out


if __name__ == "__main__":
    sys.exit(_child(sys.argv[1]))

# 0001. The PDF is printed by Chromium

Status: accepted

## Context

The book is an illustrated A4 PDF: running text that wraps around notes in the margin, characters beside paragraphs,
prompts in drawn monitors and a scene at the foot of every page. Pages must be composed row by row, the way a layout
artist would do it, and the source must stay plain Markdown that readers can edit in a pull request.

## Decision

Chapters are compiled to HTML and CSS, and a headless Chromium, driven by Playwright, lays the pages out and prints the
PDF. It is Playwright's own Chromium, the build pinned by the playwright version in `tools/uv.lock`, run in the image of
`tools/Dockerfile` in CI and for the reference build on any machine: the system's Google Chrome and a system's
hyphenation dictionaries laid the same book out on fewer or more pages on another machine. Pagination runs in the browser (`tools/bookkit/theme/paginate.js`), because only the browser knows
how tall every line, note and picture really is.

## Considered

- **LaTeX.** Excellent typography for running text, but floating notes, drawn characters and page-wide scenes would
  need custom packages for every block, and the drawings would leave the Python toolchain.
- **WeasyPrint and other HTML-to-PDF engines.** No JavaScript, so no measured pagination; partial CSS support.
- **A design tool (InDesign, Figma).** Manual layout of about 250 pages on every change; no pull requests from readers.

## Consequences

- The build needs Playwright's Chromium (`uv run playwright install chromium`), or Docker for the reference build.
- Hyphenation is done in Python (`tools/bookkit/hyphenate.py`), not by the browser.
- Layout rules are code and are tested (`tools/tests/test_pagination.py`), and `book audit` measures every built page.
- Chrome prints some effects as rasters; ADR 0002 limits the drawings to what it prints as vectors.

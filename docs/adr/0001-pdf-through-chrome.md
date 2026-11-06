# 0001. The PDF is printed by Google Chrome

Status: accepted

## Context

The book is an illustrated A4 PDF: running text that wraps around notes in the margin, characters beside paragraphs,
prompts in drawn monitors and a scene at the foot of every page. Pages must be composed row by row, the way a layout
artist would do it, and the source must stay plain Markdown that readers can edit in a pull request.

## Decision

Chapters are compiled to HTML and CSS, and a headless Google Chrome (or Playwright's Chromium as a fallback), driven by Playwright, lays the pages out and
prints the PDF. Pagination runs in the browser (`tools/bookkit/theme/paginate.js`), because only the browser knows
how tall every line, note and picture really is.

## Considered

- **LaTeX.** Excellent typography for running text, but floating notes, drawn characters and page-wide scenes would
  need custom packages for every block, and the drawings would leave the Python toolchain.
- **WeasyPrint and other HTML-to-PDF engines.** No JavaScript, so no measured pagination; partial CSS support.
- **A design tool (InDesign, Figma).** Manual layout of about 250 pages on every change; no pull requests from readers.

## Consequences

- The build needs Google Chrome. CI installs it when the runner lacks it.
- Layout rules are code and are tested (`tools/tests/test_pagination.py`), and `book audit` measures every built page.
- Chrome prints some effects as rasters; ADR 0002 limits the drawings to what it prints as vectors.

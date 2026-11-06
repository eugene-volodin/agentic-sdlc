---
name: build-book
description: Build the book into dist/agentic-sdlc.pdf and look at its pages. Use after any change in book/ or tools/, or when asked to build, render or preview the book.
---

# Build the book

1. From `tools/`, run `uv sync` once, then `uv run book build --strict --shots all`.
2. If the build fails, read the `BuildError`: it names the file and the line. Fix the input, don't silence the check.
3. Layout warnings fail `--strict`. Each names the page; open `<temp>/bookkit/book/pages/page-NNN.png` and fix the
   cause (usually the order of blocks in the chapter); never reword the author's text without asking.
4. Open the PNG of every page you changed and check that nothing overlaps, no block is torn across pages, and no
   empty space is left above the picture at the foot of the page.
5. Report the page count and the path of the PDF.

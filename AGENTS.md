# AGENTS.md

A Russian illustrated book built from Markdown into an A4 PDF. The text is in `book/`, the build and check tool in
`tools/`. Read `docs/design-system.md` before changing the layout or the drawings, and `docs/build.md` before
changing the tool.

## Commands

The reference: `tools/container.sh` runs `tools/ci.sh` (tests, linter, `book audit`) in the image of `tools/Dockerfile`,
exactly as CI; the PDF and the report go to `dist/ci/`. Needs Docker. The rest runs natively from `tools/`, needs uv
and Playwright's Chromium, and may break a line differently from the container.

- Install: `uv sync`, then `uv run playwright install chromium`
- Build the book: `uv run book build --strict` → `../dist/agentic-sdlc.pdf`
- Build one chapter with page images: `uv run book build --only <folder> --shots all --no-pdf`
  (PNG files go to `<temp>/bookkit/book/pages/`)
- Check every page, as CI does: `uv run book audit --base origin/main --baseline audit-baseline.json`
- Show every markup block: `uv run book build --demo --shots all`; reference: `uv run book components`
- Tests: `uv run pytest -q`; linter: `uv run ruff check bookkit tests`

## Layout of the repository

- `book/book.yml` — title, version, the plan of chapters; `book/NN-name/` — a chapter: `00-chapter.md` with the front
  matter, then one file per section; pictures sit beside the text
- `tools/bookkit/` — the tool: `compiler.py` (Markdown to rows), `components/` (blocks), `theme/paginate.js` (page
  layout in the browser), `render.py` (PDF and PNG), `audit.py` (page checks), `art/` (every drawing, as code),
  `design.py` (every color, font and size)
- `tools/tests/` — tests; `tools/tests/test_robustness.py` keeps broken books that must fail cleanly
- `docs/` — the design system, the build, the decision records (`docs/adr/README.md` is their index)

## Glossary

- **Opener** — the full-page picture that opens a chapter; **footer** — the scene at the foot of every page
- **World** — the setting of a chapter's footers (a kitchen, a harbour, a railway…), declared by `world:`
- **Note** — a character's remark in the margin (`::: note cat`); the Cat's notes carry the sources
- **Baseline** — `tools/audit-baseline.json`, the audit findings accepted on purpose, each with a reason

## Rules for the text

- The book is in Russian, written in the author's first person, addressing the reader as «ты». No emoji.
- Every fact about a model, tool or price links to the official documentation in a note of the Cat (`::: note cat`).
- A prompt for the reader is a ` ```prompt ` fence; every prompt and command printed in the book has been run.
- Every change to the book raises `version:` in `book/book.yml` (`MAJOR.MINOR-MM.YYYY`: MINOR + 1, current month and
  year). CI fails if it is not raised.

## Rules for the code

- English only in code, comments and docs; Russian lives in `book/`, `tools/bookkit/locale/`, `tools/demo/` and
  `tools/tests/fixtures/`.
- Colors, font stacks and spacing only in `tools/bookkit/design.py`, type sizes in `tools/bookkit/theme/css/`; never
  invent a value elsewhere.
- Every mistake in the input is a `BuildError` naming the file and the line; never a traceback or a silent skip.
- Drawings use only what Chrome prints as vectors and only the bundled fonts (`docs/adr/0002-vectors-only.md`).
- After a change: `uv run pytest -q`, `uvx ruff check bookkit tests`, and look at the PNG of every page you touched.

## Never

- Commit `dist/` or a PDF.
- Weaken a test or add a finding to `audit-baseline.json` to make CI pass, unless the finding is a deliberate
  exception; every entry there needs a reason.
- Change the fonts in `tools/bookkit/theme/fonts/` without their licences.

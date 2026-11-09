# How the book is built

The book is Markdown in `book/`; a Python package, `bookkit` in `tools/`, turns it into an A4 PDF. This document
explains the pipeline, where each part of the code lives, the commands, the audit that checks every page, what makes
the build robust, the tests, CI and releases, and how to extend the tool.

What the pages look like - the grid, the tokens, the blocks, the layout and drawing rules - is in
[design-system.md](design-system.md). The decisions behind the build are recorded in [adr/](adr/README.md).

## Contents

1. [Quick start](#quick-start)
2. [The pipeline](#the-pipeline)
3. [Code map](#code-map)
4. [book.yml](#bookyml)
5. [Commands](#commands)
6. [Outputs](#outputs)
7. [The audit](#the-audit)
8. [A robust build](#a-robust-build)
9. [Tests](#tests)
10. [CI and releases](#ci-and-releases)
11. [Extending](#extending)

---

## Quick start

There are two ways to build, and the first is the reference.

**The reference build, in the container.** Needs Docker. `tools/container.sh` builds the image of `tools/Dockerfile`
(Playwright's image for the playwright version in `uv.lock`: Ubuntu, Python, that version's Chromium; amd64 and arm64)
and runs `tools/ci.sh` inside it with the repository mounted: the tests, the linter and `book audit`, exactly what CI
runs. It writes the PDF, the report, the findings and the contact sheets to `dist/ci/`. The same image and command on
any machine give the same pages: compare the page count and the layout fingerprint the audit prints with those of CI.
The build takes up to about 3 GB of memory inside the container; give Docker at least 4 GB.

```bash
tools/container.sh                                        # what CI runs -> dist/ci/agentic-sdlc.pdf, dist/ci/report.md
BASE=origin/main tools/container.sh                       # the same, with the version check of a pull request
tools/container.sh uv run --frozen book build --strict    # any other command, inside the container, from tools/
```

**The quick native build**, for iteration. Needs [uv](https://docs.astral.sh/uv/) and Playwright's Chromium (once:
`uv run playwright install chromium`). It uses the same browser version, but the system draws the fonts, so a line may
break elsewhere than in the container; the container is the reference. All commands run from `tools/` (from
elsewhere: `uv run --project tools book ...`).

```bash
cd tools
uv sync                                            # once
uv run playwright install chromium                 # once, and after playwright moves in uv.lock
uv run book build --strict                         # ../book -> ../dist/agentic-sdlc.pdf
uv run book build --only why --shots all --no-pdf  # one chapter, a PNG of every page
uv run book audit --baseline audit-baseline.json   # build once and check every page
uv run pytest -q                                   # tests
uv run ruff check bookkit tests                    # linter
```

---

## The pipeline

```
book/*.md + book.yml
   │  config.py      book.yml merged over the locale (locale/ru.yml)
   │  markup.py      front matter, ":::" blocks, fences, options
   ▼
compiler.py          every top-level block -> one grid row (text column 116 mm + margin 48 mm)
   │  components/    each block and fence renders its HTML
   │  markdown.py    Markdown + typography
   ▼
pages.py             cover, contents, map, openers, farewell; one HTML document:
   │                 design tokens as CSS custom properties, then the sheets of theme/css/
   ▼
render.py ── Chromium (Playwright, a child process)
   │  theme/paginate.js   distributes rows over pages, places notes, splits blocks, sizes footers
   │  art/footers.py      Python draws a scene for every footer height the paginator reports
   │  --shots             PNG proofs of pages
   ▼
PDF (printed by Chromium, soft hyphens out of its text, written atomically) + PNG proofs
```

1. **Read.** `config.py` loads `book/book.yml` and merges it over the built-in locale. The chapters are the Markdown
   files and folders of `book/` (see [design-system.md](design-system.md#a-chapter)).
2. **Compile.** `compiler.py` splits a chapter into runs of Markdown and `:::` blocks; every top-level block becomes
   a grid row. Blocks and fences are rendered by the component library (`components/`). Margin notes are queued and
   attached to the next row that has a margin.
3. **Assemble.** `pages.py` builds one HTML document: the tokens of `design.py` become CSS custom properties
   (`css_variables()`), followed by the style sheets of `theme/css/`, the cover, the contents, the map, the chapter
   openers and every row.
4. **Paginate.** `render.py` opens the document in Playwright's Chromium. In the browser `paginate.js`
   distributes the rows over pages, keeps margin notes from colliding, splits paragraphs, lists and long blocks,
   places accents, and reports for each page the height left for its footer, its chapter, its headings and text.
5. **Illustrate.** Python draws a footer scene for each page (`art/footers.py`, `art/worlds.py`) and hands the SVG
   back to the page.
6. **Print.** Chromium prints the PDF; `pdftext.py` takes the soft hyphens out of its text layer, and `render.py`
   scans it for rasters and foreign fonts (see
   [design-system.md](design-system.md#printing-the-same-pdf-in-every-viewer)). With `--shots` it saves PNG proofs.

Why Chrome: [ADR 0001](adr/0001-pdf-through-chrome.md). Why everything must be a vector:
[ADR 0002](adr/0002-vectors-only.md). The browser is always Playwright's own Chromium, the build pinned by the
playwright version in `uv.lock`, never the system's Google Chrome; without it the build stops and names the command
that installs it.

**Hyphenation** is done at build time, not by the browser: `hyphenate.py` puts soft hyphens (U+00AD) into the words of
paragraphs and list items from the pyphen dictionaries (`ru_RU`, `en_US`), and the style sheets say `hyphens: manual`.
A browser's own hyphenation uses the dictionaries of the system, which differ between machines, and so would the
pages. Code, links, headings, bubbles, margin notes and pictures get no soft hyphens, nor do short words (under
`HYPHEN_MIN_WORD` letters), names, acronyms, paths and the last word of a block. A paragraph split between two pages
is cut between words, never inside one: a word that does not fit on the page goes on whole (`splitText` in
`paginate.js`). Whatever is reported, searched or compared (the audit, the paginator's warnings, the text the footers
are picked by) goes without the soft hyphens, and so does the PDF's text layer: copying or searching a word finds it
whole.

---

## Code map

```
book/                   chapters (folders of *.md, or single files) + book.yml; 00-front/ comes before the contents
docs/
  design-system.md      what the pages look like
  build.md              this file
  adr/                  decision records
.github/workflows/      check.yml and release.yml
tools/
  pyproject.toml        package `bookkit`, script `book`
  audit-baseline.json   the audit's accepted warnings, each with its reason
  Dockerfile            the reference environment: Playwright's image, uv, the locked dependencies
  ci.sh                 what CI runs: tests, linter, `book audit` -> ../dist/ci/
  container.sh          runs ci.sh (or any command) inside the image, with the repository mounted
  demo/                 00-vitrina.md: a chapter showing every block, with its own book.yml (never published)
  tests/                pytest; fixtures/ holds the Russian samples
  bookkit/
    design.py           DESIGN TOKENS: palette, fonts, page geometry, paginator and audit thresholds
    config.py           book.yml + locale
    markup.py           syntax: "::: block", options, front matter, fences, BuildError
    markdown.py         Markdown + typography (quotes, no-break spaces, [[keys]], ==marker==, images)
    hyphenate.py        soft hyphens in paragraphs and list items, from the pyphen dictionaries
    compiler.py         chapters -> grid rows; front-matter validation; errors with file and line
    components/         THE COMPONENT LIBRARY
      base.py           registry, @block/@fence, option types, validation, reference (read first)
      context.py        what a component may ask of the build
      graphics.py       small shared drawings: bubble tail, tick, icons, drawn marks, the computer's base
      speech.py         say, dialog, note, quote
      callouts.py       tip, warn, idea, try, define, stat, recap, dodont, compare
      lists.py          checklist, steps, cast
      layout.py         scene, wide, pagebreak
      people.py         about, contacts, download (QR code via segno), github
      code.py           fences: code, terminal, tree, file, prompt
      chat.py           fence: chat, a messenger channel with its thread
    pages.py            cover, contents, openers, the HTML document, the header perches, the accents
    title.py            an opener's title drawn from the real outlines of the heading face
    reading.py          a chapter's reading time
    fonts.py            variable fonts cut into static weights for the browser
    render.py           browser: pagination -> footer scenes -> PDF / PNG; the isolated child process; layout fingerprint
    pdftext.py          the PDF's text layer without soft hyphens
    audit.py            build once and measure every page (`book audit`)
    proofs.py           proof sheets: characters, doodles, palette
    cli.py              build / watch / storyboard / sheet / prompts / components / audit; where book/, demo/,
                        dist/ and <temp>/bookkit/ are
    locale/ru.yml       every Russian string the engine prints, the worlds' and openers' lettering
    theme/css/          style sheets, one per component family - colors and geometry only through var(--token)
    theme/paginate.js   distribution over pages
    theme/audit.js      the audit's measurements in the browser
    theme/fonts/        bundled fonts (OFL), so the build works offline
    art/                every drawing, as code
      ink.py            drawing primitives: outline, cel shading, stipple, gradients, fades, lettering
      rig.py            hands, arms and grips
      characters.py     registry of the characters and the contract of a character module (read before adding one)
      professor.py, cat.py, caterpillar.py, sparrow.py, agent.py
      handheld.py       things a character holds, with their grip
      curves.py         how every cable, hose and tube bends
      props.py, sets.py scenery and props shared by the worlds and the openers
      doodles.py        small standalone objects: accents, icons
      flags.py          the flags of :flag-xx:
      scenes.py         the generic scenes (meadow, path, pond, room, study)
      openers.py        the opener stage (bubble, cast, keep-clear areas) and OPENERS, every opener by name
      stories.py        the story openers a chapter can name as `scene:` (the railway)
      footers.py        footer strips: routing a page to its world, or to the courtyard without one
      world_base.py     World, Station and the WORLDS registry each world module adds itself to
      worlds.py         loads every world; schedule() and frame(): the camera along a world
      world_kit.py      the kit every world draws with, and its checks
      world_*.py        one module per world
      bookmap.py        the map of the book
      farewell.py, road.py   the farewell page and its road
```

---

## book.yml

| Key | What it holds |
|---|---|
| `title`, `title_highlight` | the series plate on the cover and the word set on its plate |
| `headline`, `headline_highlight` | the name of the book and the phrase set on a colored plate |
| `topics` | stickers along the top of the cover |
| `kicker` | a plain line for the top band when there are no topics |
| `subtitle`, `author`, `year` | the cover's handwritten subtitle, author line and year |
| `version` | `MAJOR.MINOR-MM.YYYY`, the month and year of the release; a malformed version is a build error |
| `version_from` | take `version` from another `book.yml` (a path relative to this one) |
| `repo` | the repository's URL: the download link and QR code are `<repo>/releases/latest/download/agentic-sdlc.pdf` |
| `plan` | every chapter of the book in order; unwritten ones show as «скоро»; enables the map and the farewell page |
| `chapters` | an explicit order of chapter files and folders (otherwise alphabetical) |
| `toc`, `cover` | `false` to leave out the contents or the cover |
| `language` | the locale file (`ru` by default) |
| `strings` | overrides merged over the locale |

Unknown keys and wrong types are build errors.

---

## Commands

| Command | What it does |
|---|---|
| `uv run book build` | build the whole book: `../book` -> `../dist/agentic-sdlc.pdf` |
| `uv run book watch` | rebuild whenever the chapters or the theme change; takes the options of `build` |
| `uv run book storyboard <chapter>` | one chapter on one sheet: its opener and every footer in page order |
| `uv run book sheet` | proof sheets: every pose and mood, every doodle, every color |
| `uv run book prompts` | every ` ```prompt ` of the book as its own text file, ready to copy |
| `uv run book components` | the reference of every block and fence, from the registry |
| `uv run book audit` | build once and measure every page; fail on new findings (see [The audit](#the-audit)) |

**`build` / `watch` options**

| Option | |
|---|---|
| `--content DIR` | build any folder with chapters and a `book.yml` (default `../book`) |
| `--out PATH` | where to write the PDF (default `../dist/agentic-sdlc.pdf`) |
| `--only TEXT` | only the chapters whose file or folder name contains this text; a chapter built alone looks exactly as in the whole book, because everything that rotates restarts per chapter |
| `--shots all` / `--shots 1,3-5` | save PNG proofs of those pages |
| `--scale N` | PNG pixel density (2 for sharper proofs) |
| `--no-pdf` | skip writing the PDF |
| `--strict` | fail if the layout has any warning |
| `--demo` | build `tools/demo/` instead of the book; it has its own content and output and refuses `--content` / `--out` |

**`storyboard` options:** `--world NAME` previews the chapter in another world without touching its file; `--scale`,
`--strict`, `--content`.

**`sheet` and `prompts`:** `--out DIR` for the files, `--content`.

---

## Outputs

`uv run book build` writes `dist/agentic-sdlc.pdf` and nothing else. Everything else goes to the system's temporary
folder, `<temp>/bookkit/`:

| What | Where |
|---|---|
| page proofs (`--shots`) | `<temp>/bookkit/book/pages/` |
| the demo | `<temp>/bookkit/demo/` |
| proof sheets | `<temp>/bookkit/sheets/` |
| exported prompts | `<temp>/bookkit/prompts/` |
| storyboards | `<temp>/bookkit/storyboard/` |
| static font cuts | `<temp>/bookkit/fonts/` |

The tool empties only folders it created itself (they hold a `.bookkit` marker); a foreign `pages/` or `prompts/` next
to `--out` is an error, not a deletion.

---

## The audit

`uv run book audit` (`bookkit/audit.py`, `theme/audit.js`) builds the book once, exactly as `book build` does, and
measures the finished pages instead of looking at pictures of them; it writes no PDF unless `--pdf`. Whoever reviews
looks only at the pages it flags.

```bash
uv run book audit --base origin/main --baseline audit-baseline.json \
  --md ../report.md --json ../audit.json --sheets ../sheets --pdf ../dist/agentic-sdlc.pdf
```

| Option | |
|---|---|
| `--content DIR`, `--only TEXT` | as for `build` |
| `--baseline FILE` | the accepted warnings, each with its reason |
| `--write-baseline` | write every current warning into `--baseline`, keeping the reasons already given |
| `--base REF` | the git ref to compare `book/` with: a change needs a higher `version:` |
| `--md FILE` | the report in Markdown |
| `--json FILE` | every finding |
| `--sheets DIR` | contact sheets of the pages with something new: eight pages to a PNG at 40 %, each flagged region boxed in red; only those pages are painted |
| `--pdf FILE` | also print the PDF |

### Checks

The thresholds are the `AUDIT_*` tokens in `design.py`.

| Check | What it finds |
|---|---|
| `hole` | free space above the footer (`AUDIT_HOLE`), on any page but a chapter's last, with the paginator's reason |
| `word-gap` | wide gaps in a justified line: every space measured with a Range; mean over `AUDIT_GAP_MEAN` or one over `AUDIT_GAP_MAX` (em) |
| `tail-under-note` | a paragraph's last line alone at full width under a note |
| `note-in-lead-in` | a note between a lead-in and the list it introduces |
| `note-below-block` | a note pushed below the block it belongs to |
| `into-picture` | text running into a drawing |
| `off-sheet` | text running off the sheet |
| `off-text-area` | text outside the text block (beyond `AUDIT_SLACK`) |
| `code-break` | inline code broken across lines inside a token |
| `number-break` | a number broken across lines |
| `double-hyphen` | a doubled hyphen at a line end |
| `line-start` | a line starting with a comma or a dash |
| `heading-at-foot` | a heading closer than `AUDIT_HEADING_FOOT` to the foot of the text |
| `section-start` | a section starting at the foot of a page with fewer than `AUDIT_SECTION_LINES` lines |
| `hanging-word` | a paragraph ending in one short word (`AUDIT_SHORT_WORD`) alone on its line |
| `table` | a table wider than its column or a cell that overflows |
| `monitor` | a prompt's monitor that is not 4:3 (within `AUDIT_MONITOR_RATIO`), too wide, or cuts its text |
| `running-head` | a running head cut with an ellipsis |
| `image` | a picture that did not load |
| `svg-id` | an id used twice or a reference to a missing one |
| `note-overlap` | a note touching another note or a block (closer than `AUDIT_NOTE_AIR`) |
| `footer-size` | a large footer where text could have filled the page, or too many in a chapter (`render.footer_findings`) |
| `blank-page` | a near-blank page (`AUDIT_BLANK`) |
| `last-page` | the side the book ends on |
| `footer-repeat` | two neighbouring pages showing one moment of a world (an error; two pages apart, a warning) |
| `footer-frame` | every footer drawn rerun through its own checks (overlaps, containers, cables, characters cut or below the floor) at the height, side and seed it was really drawn at (`footers(..., trace)`) |
| `page-weight` | a page's markup over `AUDIT_PAGE_WEIGHT` KB, heavy enough to run the browser out of memory |
| `residue` | markup or typing left in the text |
| `links` | a malformed link, a link leading nowhere, a wrong page number in the contents |
| `version` | with `--base`: `book/` changed without a higher `version:` |
| `too-tall` | a block taller than a page that cannot be split |
| `font` | a font that did not load |
| `build` | any other warning of the build; the paginator's own warnings (`warn` in `paginate.js`) come over as findings too |

The browser-side checks run in `theme/audit.js` after pagination and the footers; the footer, repeat, frame and
version checks run in Python.

### Findings and the baseline

- A finding is `{check, severity, page, chapter, where, detail, numbers, rect}`; `severity` is `error`, `warning` or
  `info`.
- The command fails on any error and on any warning that `--baseline tools/audit-baseline.json` does not accept.
- A baseline entry is matched on its check, chapter and snippet (`where`), never on a page number, which shifts, and
  must say why it is accepted (`reason`). Errors are never baselined. Entries that match nothing are reported as stale.
- Add a warning to the baseline only when it is a deliberate exception, never to make CI pass.

```json
{
  "accepted": [
    {
      "check": "footer-repeat",
      "chapter": "2",
      "where": "fair / engines / look",
      "detail": "pages 30 and 32 show the same picture (fair / engines / look)",
      "reason": "Two pages apart, not neighbouring; the neighbouring pages differ in camera and mirror."
    }
  ]
}
```

---

## A robust build

Every broken input stops the build with an error naming the file and the line - never a traceback, a silent skip or a
hang.

- **`BuildError` for every mistake in the input:** no `book.yml`, wrong keys or types in it, a file not in UTF-8 or empty,
  unclosed front matter or code fence, a stray `:::`, an empty block, text after a block's options or a title on a
  block that takes none, an unknown character, pose or mood, two chapters with one opener scene, a picture that is a URL
  or lies outside the book's folder or is not a picture, HTML beyond `<br>`, the score spans and comments.
  `tests/test_robustness.py` keeps the broken books.
- **An isolated browser.** `render_isolated` runs the browser's part of the build in a child process in a session of
  its own. Each step has its own timeout (`LOAD_TIMEOUT`, `LAYOUT_TIMEOUT`, `PRINT_TIMEOUT`); after `BUILD_TIMEOUT`
  (15 minutes), or on Ctrl+C, the child is killed together with its Chrome, found by the `--bookkit-run=` mark on its
  command line.
- **An atomic PDF.** The PDF is printed beside its place (`.agentic-sdlc.pdf.partial`) and moved in whole: it is
  written whole or not at all.
- **One build per output.** `cli.exclusive` takes a lock per output path, so two builds of one PDF wait for each other
  instead of overwriting the file and emptying each other's proof folders.
- **Unique ids.** After layout every drawing gets unique ids (`uniqueIds` in `paginate.js`), so a reused drawing never
  takes another's clip path.
- **Memory.** Page proofs (`--shots`) are taken before the PDF is printed, one page painted at a time (the others
  `content-visibility: hidden`), and every 20 pages the browser is told to drop its rasters and collect garbage;
  otherwise a book of 250+ pages with detailed worlds runs Chrome out of memory. The PDF is not affected. The audit's
  `page-weight` check keeps any one page from growing too heavy.
- **Printing checks.** The PDF is scanned for rasters and fonts of the building machine
  (`render._raster_warnings`, `render._font_warnings`); `--strict` fails on them.

The whole book (about 250 pages) builds in about a minute and audits in about 20 seconds, with the fonts cached.

---

## Tests

```bash
uv run pytest -q
uvx ruff check bookkit tests
```

| Test | What it guards |
|---|---|
| `test_markup.py` | block splitting, option syntax, front matter |
| `test_compiler.py` | Markdown and blocks to rows without a browser; chapter colors' contrast and uniqueness |
| `test_components.py` | the registry, option validation, every component's example compiles |
| `test_chapters.py` | where chapters come from: single files, folders of parts, what is left out |
| `test_cli.py` | where outputs go and what the tool refuses to delete |
| `test_design.py` | one palette, one set of tokens: no stray colors, no undefined properties, no duplicate or unused color |
| `test_robustness.py` | broken books fail cleanly, never with a traceback or a hang |
| `test_pagination.py` | splitting, footer sizes, `fill` footers, page counts of a fixture book and the whole book |
| `test_print.py` | nothing Chrome cannot print as vectors |
| `test_audit.py` | `book audit` finds what it should and nothing on a clean book (cases in `fixtures/audit_cases.yml`) |
| `test_reading.py` | reading time |
| `test_scenes.py` | nothing in a scene overlaps anything else |
| `test_openers.py` | every opener draws; nothing overlaps or reaches under the title or the bubble; no character cut |
| `test_grips.py` | hands close round what they hold; arms join the body at its sides |
| `test_curves.py` | every line bends smoothly: steps of at most 8 degrees, the radius, coaxial ends |
| `test_footers.py` | a page without a world is drawn in the courtyard, clean, never the same moment twice in a row |
| `test_worlds.py` | the camera visits every station in order; every frame draws clean; the finale closes the chapter; any world module imports first |
| `test_world_frames.py` | nothing in a frame is cut; the floor shows under the feet; neighbouring frames differ |
| `test_world_kit.py`, `test_world_space.py` | containers and ports in every world; the space station's own story |
| `test_bookmap.py` | the map of the book: every written chapter's world has its place |
| `test_easter.py` | the easter eggs stay in place |

Russian test samples live in `tools/tests/fixtures/`; no Cyrillic in `*.py`, `*.js` or `*.css`.

---

## CI and releases

| Workflow | When | What it does |
|---|---|---|
| [`check.yml`](../.github/workflows/check.yml) | every pull request and every push to `main` | builds the image of `tools/Dockerfile` (cached in the GitHub Actions cache) and runs `BASE=origin/main tools/container.sh`: `tools/ci.sh` inside it - `pytest -q`, `ruff check bookkit tests`, then `book audit --base origin/main --baseline audit-baseline.json`. The report goes to the job summary; the report, the findings, the contact sheets of the flagged pages and the PDF are uploaded as the `agentic-sdlc-audit` artifact |
| [`release.yml`](../.github/workflows/release.yml) | every push to `main` that touches `book/` or `tools/` | reads `version:` from `book/book.yml`; unless a release `v<version>` already exists, runs `tools/container.sh` as `check.yml` does and publishes the GitHub release `v<version>` with the `agentic-sdlc.pdf` it built |

**One environment.** CI and an author's machine run the same command (`tools/ci.sh`) in the same image
(`tools/Dockerfile`), so they get the same PDF: the same page count and the same **layout fingerprint**, a hash of
every page's text and the number of lines of each of its blocks, printed by `book build` and `book audit` and written to
the audit's report. When CI and a local container build disagree, the fingerprints differ; when they agree, a build
seen locally is the build CI releases. The page count of the handbook is also guarded by
`test_footers_grown_to_fill_never_add_a_page_to_the_handbook`, measured in the container; its message names the
browser and the number of soft hyphens. When `uv.lock` moves to another playwright, the tag in `tools/Dockerfile`
follows it.

**Versions.** `version:` in `book/book.yml` is `MAJOR.MINOR-MM.YYYY`, the month and year of the release. It is printed
on the cover and on the «Свежая версия» page. Every change under `book/` raises it (MINOR + 1, the current month and
year); `book audit --base` fails on a change with no higher version, so every merged change becomes a release of its
own ([ADR 0004](adr/0004-one-release-per-change.md)). The link `<repo>/releases/latest/download/agentic-sdlc.pdf`
(the QR code and the button on «Свежая версия») always leads to the newest one.

**Licenses** of the text, the examples, the tool and the fonts: [ADR 0003](adr/0003-licenses.md) and `LICENSE`.

---

## Extending

General rules: English only in code, comments and docs; no Cyrillic in `*.py`, `*.js`, `*.css`. Colors, fonts and sizes
come from `design.py`. Every mistake in the input is a `BuildError` naming the file and the line. After a change run the
tests and the linter, and look at the PNG of every page you touched.

### A new block or fence

1. Write a function in the module of its family in `tools/bookkit/components/` and decorate it with `@block(...)` or
   `@fence(...)`. The decorator declares the names, the character it takes (`who=`), typed options (`Flag`, `Choice`,
   `Number`, `Character`, `Text`), the width policy and an example. Validation and error messages are shared; details
   in the header of `components/base.py`.
2. The docstring (its first line is the description) and the example are mandatory: every example is compiled in the
   tests and printed by `book components`.
3. Return a `Row` (or a list of rows, or `None`); render the chapter's Markdown with `ctx.blocks()` / `ctx.inline()`.
4. Style it in the family's sheet in `theme/css/`, with tokens only.
5. Show it in the demo chapter `tools/demo/00-vitrina.md` and add it to
   [design-system.md](design-system.md#blocks-and-fences).

```python
@block("define", titled=True, stretch=True, options={"perch": Character(), "peek": Character()},
       example="::: define Skill\na folder with instructions.\n:::")
def define(ctx: Context, call: Call) -> Row:
    """A definition on a scroll; the title is the term being defined."""
    ...
```

### A UI string

In `tools/bookkit/locale/ru.yml`, never in code.

### A color or size

A constant in `tools/bookkit/design.py`, and only there; only if no existing color is the same material. CSS reads it as
`var(--name)`; `tests/test_design.py` guards the palette.

### A new character

A module in `tools/bookkit/art/` following the contract in `art/characters.py`, one line in `MODULES`, and a name in
`locale/ru.yml`. Nothing outside a character's module tests for its name; what a character can do (poses, `PEEK_Y`,
`HOLD_Y`, mouth) is declared in the module. A **pose** is a line in `POSES` of the character's module: elbow, wrist and
hand kind for each arm.

### A held thing

Drawn through the grip, never put next to a hand: `Stage.hold(box, make, side, turn)` on a page,
`characters.draw(name, pose, hold={"right": make})` alone; ready props with their handle at the fist live in
`art/handheld.py`. See [design-system.md](design-system.md#drawing-rules).

### A new world

1. A module like `art/world_space.py`: `world(name, opener=...)`, its stations (`Station(key, draw, beats)`), the
   `backdrop` of a frame, the `finale`, and an opener registered in `openers.OPENERS`; it imports `world` and
   `Station` from `art/world_base.py`, and `art/worlds.py` imports the module so that it registers.
2. Draw with the kit of `art/world_kit.py`: containers through `Pen.container` / `Pen.tag`, lines through `connect()`
   between declared ports.
3. Its lettering goes under `worlds: <name>:` and `openers: <name>:` in the locale.
4. Give it a vignette on the map of the book (`art/bookmap.py`): a written chapter whose world has none stops the
   build.
5. Set `world: name` in the chapter's front matter, preview it with `uv run book storyboard <chapter>` (or
   `--world <name>` before switching), and run the world tests.

### Scenery, a doodle

- **Scenery:** a function in `art/props.py`.
- **Doodle:** a function with `@doodle_drawing` in `art/doodles.py`.

# Design system

How the book looks and how its pages are composed: the page and its grid, the design tokens, the characters, every
markup block, the layout rules the paginator follows, the chapter openers and worlds, and the rules every drawing and
every printed page obey.

This document describes *what* the book looks like. How the tool turns Markdown into a PDF, the code map, the commands
and how to extend the tool are in [build.md](build.md).

Two sources are always more current than any document:

- `uv run book components` (run in `tools/`) prints every block and fence with its options, straight from the
  component registry;
- `uv run book build --demo --shots all` builds `tools/demo/00-vitrina.md`, a chapter that shows every block live.

## Contents

1. [Foundations](#foundations)
   - [Page and grid](#page-and-grid)
   - [Colors](#colors)
   - [Fonts and type sizes](#fonts-and-type-sizes)
   - [Spacing and geometry tokens](#spacing-and-geometry-tokens)
2. [A chapter](#a-chapter)
3. [Characters](#characters)
4. [Blocks and fences](#blocks-and-fences)
5. [Inline markup and typography](#inline-markup-and-typography)
6. [Layout rules](#layout-rules)
7. [Front pages, cover, contents, map and farewell](#front-pages-cover-contents-map-and-farewell)
8. [Chapter openers](#chapter-openers)
9. [Worlds and footer scenes](#worlds-and-footer-scenes)
10. [Drawing rules](#drawing-rules)
11. [Printing: the same PDF in every viewer](#printing-the-same-pdf-in-every-viewer)
12. [Ideas](#ideas)

---

## Foundations

### Page and grid

| | |
|---|---|
| Format | A4, 210 x 297 mm; inner margin 20 mm (towards the spine), outer 18 mm |
| Grid | text column **116 mm** + margin column **48 mm**, 8 mm apart: 172 mm of text width |
| Single columns | `center`: one 172 mm column, the whole text width; `full`: one 168 mm column for dense pages |
| Page head | an accent band, the chapter number and title at the outer edge, a dashed line. On every page a whole character (Cat, Sparrow, Caterpillar or Agent in turn, a 15 mm box) stands with its feet on the dashed line at the inner edge, away from the title, the top of its head reaching the middle of the colored band. Each character's drop in `PERCHES` (`pages.py`) puts the feet, not the drawing box, on the line. The running head names the chapter only, never the title of the book, and keeps room for the marks over Ё and Й |
| Page foot | a footer scene, different on every page, and the page number on an arrow tag at the outer edge (the tag's corner is kept clear of the scene). Footer sizes: see [Footer sizes](#footer-sizes) |
| Drawing style | ink outline, two-tone shading with light from the top left, stipple in the shadows, gradients on sky, ground and screens |

All page geometry is a token in `tools/bookkit/design.py` (see [Spacing and geometry tokens](#spacing-and-geometry-tokens)).

### Colors

Every color is a constant in `tools/bookkit/design.py`, and only there.

- In drawings: `from .. import design as P`, then `P.WOOD`.
- In CSS: `var(--wood)`. `css_variables()` turns every constant into a custom property (`PAPER_SHADE` becomes
  `--paper-shade`).
- Lighter or darker variants are derived at the point of use with `lighten()`, `darken()` and `mix()`; shading in
  the drawings is computed, so one base color per material is normally enough.
- A new color goes into `design.py` only, only if no existing one is the same material, and under a name that says
  what it *is* (`WOOD`, `SKIN`), not where it is used.
- `uv run book sheet` renders every color to `<temp>/bookkit/sheets/palette.png`.
- `tools/tests/test_design.py` fails if a hex or rgb color appears outside `design.py`, if CSS uses an undefined
  custom property, or if the palette gains a duplicate or an unused color.

**Chapter colors.** Each chapter picks one with `color:` in its front matter; it becomes the chapter's `--accent`.
They are the only saturated UI colors: thirteen `CHAPTER_*` tokens, collected by name in `design.ACCENTS`.

| Name | Token | Used by |
|---|---|---|
| `sky` | `CHAPTER_SKY` | the introduction and the front pages |
| `coral` | `CHAPTER_CORAL` | chapter 1 |
| `blue` | `CHAPTER_BLUE` | chapter 2 |
| `orange` | `CHAPTER_ORANGE` | chapter 3 |
| `teal` | `CHAPTER_TEAL` | chapter 4 |
| `green` | `CHAPTER_GREEN` | chapter 5 |
| `purple` | `CHAPTER_PURPLE` | chapter 6 |
| `yellow` | `CHAPTER_YELLOW` | chapter 7 |
| `orchid` | `CHAPTER_ORCHID` | chapter 8 |
| `periwinkle` | `CHAPTER_PERIWINKLE` | chapter 9 |
| `mint` | `CHAPTER_MINT` | chapter 10 |
| `crimson` | `CHAPTER_CRIMSON` | chapter 11 |
| `lime` | `CHAPTER_LIME` | the conclusion |

The hues sit about 25 degrees apart round the OKLCH wheel; neighbours on the wheel also differ in lightness, and
consecutive chapters sit far apart. Ink text on each keeps a contrast of 4.5:1 or more; `tests/test_compiler.py`
checks that and that no chapter repeats a color. `css_variables()` writes a `[data-color]` rule for every chapter
color, so a new one needs only its token.

**Other color groups** in `design.py`: neutrals (`INK`, `PAPER`, `CARD`, `PEN` for handwriting ...), the saturated
colors of the drawings (`PINK`, `TEAL`, `YELLOW`, `ORANGE`, `GREEN`, `BLUE`, `VIOLET`, `PLUM`, `INDIGO`, `PINE`,
`RUBY`), signals (`RED`, `GOOD`, `BAD`), warm tones, fur and wood, the old computer, metal and glass, plants, sky and
water, the terminal and syntax highlighting (`TERMINAL_*`, `SYN_*`), parchment.

### Fonts and type sizes

All fonts are bundled in `tools/bookkit/theme/fonts/` (SIL Open Font License), all with Cyrillic, so the build works
offline. Their stacks are the `FONTS` token in `design.py` (`--f-head`, `--f-body`, ...).

| Role | Font | CSS |
|---|---|---|
| Headings | **Rubik** 700-900 | `--f-head` |
| Running text | **PT Serif** 11.8 pt, line height 1.66 | `--f-body` |
| Speech bubbles | **Balsamiq Sans**, 11.9 pt | `--f-talk` |
| Handwritten margin notes | **Caveat** | `--f-hand` |
| Code, prompts, terminal | **JetBrains Mono**, 9.2 pt in code blocks | `--f-mono` |
| The cover headline only | **Dela Gothic One** | `--f-display` |
| Signs, labels and sound words in pictures; the «продолжение» mark | **Comfortaa** 700 (`SIGN_FONT`) | `--f-sign` |
| Lettering on screens and displays in pictures | **Rubik** 800 (`PLAIN_FONT`) | |
| Speech inside pictures | **Balsamiq Sans** 700 (`ILLUSTRATION_FONT`) | |

Type is large so it reads freely. Do not shrink type to make things fit: shorten the text or let it run on. Type
sizes are set in the style sheets of `theme/css/`; families, colors and page geometry come from `design.py`.

### Spacing and geometry tokens

All in millimetres unless marked; CSS and `paginate.js` read them as custom properties.

| Token | Value | What it is |
|---|---|---|
| `PAGE_WIDTH`, `PAGE_HEIGHT` | 210, 297 | the sheet |
| `MARGIN_INNER`, `MARGIN_OUTER` | 20, 18 | page margins |
| `COLUMN_MAIN`, `COLUMN_GAP`, `COLUMN_SIDE` | 116, 8, 48 | text column, gap, margin column |
| `COLUMN_CENTER`, `COLUMN_FULL` | 172, 168 | the single columns of `side: center` and `side: full` |
| `BODY_TOP`, `BODY_GAP` | 24, 4 | where the text block starts; air between it and the footer |
| `FOOT_HEIGHTS` | s 34, m 55, l 80 | footer scene sizes |
| `FOOT_LARGE_MAX` | 3 | `l` footers allowed in a chapter |
| `FOOT_PANORAMA`, `FOOT_MAX` | 110, 190 | the panorama on a chapter's last page |
| `HOLE_MAX` | 99 | a third of the page: past this, blocks split instead of moving on whole |
| `AFTER_HEADING` | 5.4 | between a heading and its first block |
| `SECTION_MIN` | 21 | room a section needs under its heading at a page's foot (three lines) |
| `BLOCK_GAP`, `TEXT_GAP` | 4.6, 3.4 | between blocks; between two paragraphs of running text |
| `BLOCK_GAP_TIGHT`, `TEXT_GAP_TIGHT`, `AFTER_HEADING_TIGHT`, `LIST_GAP_TIGHT` | 2.4, 2.2, 4, 0.4 | the closed-up gaps of a page that almost holds its next block (list items are 1.2 mm apart otherwise) |
| `ACCENT_EVERY`, `ACCENT_FROM` | 70, 24 | full-width text before an accent; the smallest paragraph that takes one |
| `ACCENT_WIDTH`, `DOODLE_WIDTH`, `ACCENT_GAP` | 25, 18, 3 | a character accent, an object accent, air round them |
| `PERCH_HEIGHT` | 15 | the character on the running head |
| `QUOTE_FIGURE`, `QUOTE_MIN` | 30, 46 | the character in a quote card; the card's least height |
| `STEP_PAD` | 1.1 | padding of a step's badge |
| `HANG_MAX` | 15 | how far notes may hang below a page's last line |
| `NOTE_GAP` | 6 | between a hanging note and whatever comes under it, another note too |
| `NUMERAL_WIDTH`, `NUMERAL_GAP`, `NUMERAL_CLEAR` | 34, 6, 14 | the big chapter numeral on an opener |
| `MONITOR_MIN`, `MONITOR_NARROW`, `MONITOR_MAX` | 64, 108, 172 | prompt monitor widths |
| `SPREAD_MAX`, `SPREAD_FROM` | 5, 10 | how far blocks may move apart on a page that ends early, and from how much leftover room |
| `EDGE_MIN` | 5 | no text closer than this to the edge of the sheet |
| `TOC_PLANNED_GAP` | 2 | between unwritten chapters in the contents |
| `COVER_SCENE_HEIGHT`, `OPENER_SCENE_HEIGHT` | 130, 135 | the cover's and an opener's picture |
| `WORD_SPACE`, `TRACK_TARGET`, `TRACK_MAX` | -0.04, 0.42, 0.025 em | justified text: word spacing and letter-spacing limits |
| `READ_CPM` | 900 | reading rate, characters per minute |
| `LINE_WEIGHT` | 2.2px | the ink outline round boxes |
| `SCENE_WIDTH` | 840 units | the width of one scene in drawing units |
| `AUDIT_*` | | thresholds of `book audit`, see [build.md](build.md#the-audit) |

---

## A chapter

A chapter is a folder `book/NN-name/` (a single file `book/NN-name.md` also works). The folder's Markdown files are the
chapter's parts, taken in alphabetical order; pictures lie next to them and are referenced by name.

```
book/
  book.yml            the cover's words, the topics, the version, the repository, the plan of the contents
  00-front/           1-author.md, author.jpg, 2-fresh.md, 3-thanks.md, 4-license.md: every page before the
                      chapters, one file each (a folder whose files all say `front: true`)
  01-why-slop/        00-chapter.md      front matter + the opening of the chapter
                      01-agreements.md   one section per file, starting with "## Heading"
                      02-how-it-works.md
                      diagram.png
```

- Only the first file of a folder has front matter; a second one with front matter is an error.
- An error names the folder, the file and the line: `01-why-slop/02-how-it-works.md: line 14: ...`.
- `--only why` builds the chapters whose folder or file name contains `why`.
- Never chapters: `README.md`, `LICENSE.md`, `CONTRIBUTING.md`, anything whose name starts with `.` or `_`, folders
  without Markdown files. So the repository can keep its own readme, and a `_name/` folder holds text that is not
  part of the book.
- The order is alphabetical, or the list `chapters:` in `book.yml` (file and folder names).

The front matter configures the chapter and its opener (the colored opening page). Unknown keys are an error.

```yaml
---
title: ...                        # or the first "# heading" of the text
color: coral                      # a chapter color, see Colors
who: professor                    # who speaks on the opener; he stands right under the bubble's tail
pose: explain                     # that character's pose
cast: ["cat:wave:smile", "agent"] # up to three more, as name:pose:mood
scene: meadow                     # a story opener (see Chapter openers) or a generic setting:
                                  # meadow | path | pond | room | study
world: kitchen                    # instead of scene: the chapter's world - its opener and a camera along
                                  # its machine in the footers (art/worlds.py)
sign: ...                         # text on the opener's signpost (optional)
lead: ...                         # what the speaker says; Markdown allowed
number: false                     # unnumbered; or a whole number to set the chapter's number
kicker: Заключение                # label instead of "Chapter N" on an unnumbered opener; "" shows none
opener: false                     # no opener page, just a heading
front: true                       # a page before the contents, unnumbered, not listed in them
side: outer                       # outer | inner | left | right | center | full
---
```

A chapter with a `world:` takes its opener from the world and must not set `scene:`. No two chapters may share an
opener scene.

`##` is a numbered section (listed in the contents), `###` a subsection. The first word of a chapter and of each `##`
section becomes a sticker on an accent plate (see [Typography](#inline-markup-and-typography)).

---

## Characters

Five characters, drawn from scratch as vectors in `tools/bookkit/art/`. In markup they are named by key; their
localized names from `locale/ru.yml` work too. `uv run book sheet` renders every pose and mood.

| Key | Who | Role in the text | Looks |
|---|---|---|---|
| `professor` | Professor Fortran | explains; sets the task | tall bald dome, ginger lock at the back, square glasses, ginger moustache, blue sweater, green tie; slim |
| `cat` | Cat X | the independent expert: numbers, facts and links to sources | shaggy ginger cat, round glasses, mortarboard with a tassel, pink bow tie, denim vest, yellow watch |
| `caterpillar` | the Caterpillar | a fussy, curious girl who doubts and rechecks everything | green head, red bow with a yellow tuft, yellow belly, spiked green back |
| `sparrow` | the Sparrow | a trusting pupil with naive questions | brown egg with a tuft, close-set eyes, permanently worried brows |
| `agent` | the Agent | the AI agent itself: says it ran the command and it works | small brand-new orange robot: a screen for a face, an antenna, a terminal prompt on the chest |

**Poses** (`pose=`), from each module's `POSES`:

| Character | Poses |
|---|---|
| professor | stand, point, present, welcome, think, thumb, pointer, explain, read, walk, sit |
| cat | stand, wave, present, point, welcome, think, cheer, walk, stride, sit, read |
| caterpillar | wave, think, present, cheer, stand, point, walk, write, stride, knit |
| sparrow | stand, cheer, wave, point, present, walk, fly, shrug |
| agent | stand, wave, point, present, think, cheer, shrug, walk, stride, carry, read, type |

**Moods** (`mood=`): `smile`, `talk`, `worry`, `surprise`, `wink`.

- The professor has two bodies: a front view for standing poses and a true profile for `walk` and `sit`. `sit` works
  in the `study` scene (professor on the chair, cat on the desk); elsewhere the character simply stands. In `pointer`
  he holds a pointer in his fist.
- `stride` is a three-quarter walk, legs forward and back, arms in counter-swing.
- The Agent is brand new: no patches, dents or grime; the hand-drawn feel comes from wobbly lines only.
- The cat's tail differs from pose to pose. Balloons end exactly in the sparrow's wing and are never the color of a
  backdrop.
- The ground shadow under every character is a flat ellipse (`ink.ground_shadow`), never stipple.
- Peeking heads (callouts with `peek`, checklists) are cut at each character's `PEEK_Y` and rest on the edge they look
  over.

---

## Blocks and fences

### Blocks

General form:

```
::: name [character] [flags] [key=value] [Title]
body
:::
```

The flag `wide` spans the text column and the margin; `narrow` keeps a block in the column.

**Dynamic width.** Callouts, `define`, `quote` and `recap` are *stretchable*: every second one that has nothing in
its margin spans the full width automatically, never two wide in a row. `wide` forces it, `narrow` forbids it.

| Block | What it is | Options and notes |
|---|---|---|
| `say` | a character with a speech bubble | no pose: a round portrait; `pose=` or `full`: the whole figure; `left`, `right`, `big`, `cloud`, `mood=`, `wide` |
| `dialog` | a conversation | each line `name:` or `name (pose, mood):`; speakers take opposite sides |
| `note` | a margin note | handwritten, or a small bubble if a character is named; `pose=`, `mood=`. Written **before** the block it belongs to |
| `quote` | a quotation card | a character stands inside the card at one end, feet on its bottom edge, as tall as the card; `left` / `right`, `pose=`, `mood=`; without options side and pose rotate. The title is the attribution |
| `tip` `warn` `idea` `try` | callouts | green / yellow / teal / pink; the title replaces the default heading |
| `define` | a definition on a scroll | the title is the term; `peek=` / `perch=` a character looking over or sitting on the scroll |
| `stat` | one big number or word with a line of explanation | sits **in the margin** beside the next block, like a note; the title is the big part |
| `recap` | a summary on a notebook page | written down by the Caterpillar by default (`recap cat` for another); `mood=` |
| `dodont` | two columns of examples | lines starting with `-` are bad, with `+` good |
| `compare` | side-by-side cards | each `### Heading` starts a card; `cols=1..4` |
| `checklist` | a poster held up by a character | `- [x]` / `- [ ]`; `numbered`, `right`, `mood=`; the professor by default |
| `steps` | a numbered procedure | the body is an ordered list; the title heads it |
| `cast` | strips introducing every character | |
| `about` | a person: photo and a few words in a bubble | the title is the name; `photo=file.jpg` relative to the chapter |
| `download` | where to get the newest version | a QR code and a button for the latest release's `agentic-sdlc.pdf`, and the version of this copy; needs `repo` and `version` in `book.yml`; the body is a line under the button |
| `github` | the repository | its address and a big star; the body is the text beside the star; needs `repo` |
| `contacts` | contact cards | one per line: `kind | label | text | link`; kinds `telegram`, `blog`, `mail`, `web` |
| `scene` | a full-width illustration | `kind=meadow|path|pond|room|study`, `h=` (30-160 mm), `cast="name:pose:mood:mark, ..."`, `sign=`, `prop=board|crate|gate` with `label=`, `seed=`; the body is the caption |
| `wide` | everything inside spans the full width | |
| `pagebreak` | a new page | also `<!-- pagebreak -->` |

### Fences

| Fence | What it is |
|---|---|
| ` ```prompt ` | **the main block**: a prompt for the reader on the screen of the old computer, with a character's hint in the margin. Options: `who=` (the Cat by default), `title=`, `note=` (the hint; `note="-"` for none), `pose=`, `mood=`, `wide`. Headings, list markers and placeholders (`{{name}}`, `<choice>`, `[UPPERCASE]`) are tinted. `uv run book prompts` exports each prompt to its own file |
| ` ```file title="path" ` | the contents of a file on a sheet of paper with a folded corner; a line wrapped in `**` is set bold |
| ` ```terminal ` (alias `console`) | `$ command`, `> /slash-command`, `# comment`. No default caption: the three dots of its title bar say what it is; `title=` is optional |
| ` ```tree title="..." ` (alias `files`) | a directory tree: `name/` is a folder, `# text` a handwritten remark, `a -> b` a symlink; the arrow is set in the mono face |
| ` ```python title="file.py" ` | any other language word: highlighted code; the title is a file name |
| ` ```chat title="# channel" ` | a screenshot of a work-messenger channel (generic, no real product's look). See below |

Every fence also takes `wide`.

**The chat fence.** `Name · 10:12: text` is a message; `> Name · 10:14: text` a reply in its thread (indented behind
a thin rule); `Name [app] · ...` an app (a square avatar and an «APP» tag; people get round avatars with initials and a
stable accent color per name); `  [img: caption]` indented under a message attaches a screenshot (a small drawn browser
page). `@Name` is tinted, `ENG-412` and `#1287` look like links, inline Markdown works. A chat never splits: it moves
on whole. Any other line is a `BuildError` naming its line.

```chat title="# requests"
Oleg Smirnov · 10:12: Can you rename the button on the quiz page?
> Tema P · 10:14: @Linear file a ticket
> Linear [app] · 10:14: Filed ENG-412
```

### Conventions for blocks

- A note is written before the block it comments; the build warns when a note ends up below its block.
- The agent's report on a prompt run is a `::: say agent` placed right after the prompt, so it stands under the
  monitor. An obvious prompt gets no hint: `note="-"`.
- No full stop at the end of framed text (margin notes, bubbles, cards, callouts): the build removes it
  (`Context.framed`). Quotations keep their own punctuation.
- Figures and side remarks (`stat`, notes) go in the margin, never in the middle of the text.

---

## Inline markup and typography

| Markup | Result |
|---|---|
| `==marker==` | a highlighter mark (drawn as an inset shadow) |
| `[[Ctrl+C]]` | a key |
| `` `code` `` | inline code |
| `:flag-us:`, `:flag-cn:`, `:flag-fr:` | a small flag waving on a pole, drawn in the book's style (`art/flags.py`), never an emoji |
| `- one<br>- two` in a table cell | a little list with a marker per line |
| `<span class="score good">98,0</span>`, `score weak` | a tinted result in a table |
| `![alt](pic.png "Caption")` alone on its line | a figure with a caption |
| `<!-- side: center -->` | switch the layout from this point on (a page with content starts anew) |
| `<!-- pagebreak -->` | a new page |

Hand-written HTML is limited to `<br>`, the score spans and comments; anything else is a build error. Pictures are
files inside the book's folder, never URLs.

**Set automatically:** quotes, dashes, no-break spaces after short words, the break points of paths in inline code.

**Stickers.** The first word of a chapter and of each `##` section is a sticker on a colored plate, not a drop cap.
The sticker is raised and its box is no taller than a line, so the gap between the first and second lines equals every
other; it never runs into the line below. A word of one or two letters takes the next word along; punctuation right
after it goes inside it.

**Justified text.** Running text and list items are justified with hyphenation (`hyphens: auto`, Chrome's dictionary
by the page's `lang`; `hyphenate-limit-chars: 5 2 2`). No `text-wrap: pretty`: in justified text it widens the gaps of
the lines it evens. The space between words is `WORD_SPACE` narrower than the font's own; after layout, a line whose
mean gap is still over `TRACK_TARGET` has the letters of its plain words spaced out by at most `TRACK_MAX`
(`paginate.js`, "even word gaps"), and the block is put back if any line would break elsewhere.

**Glue.** `markdown.py` joins with no-break spaces: a number in groups of three (21 760); a short word and what follows
it (code or a link too); the last short word of a paragraph and the word before it; a command kept whole and the
punctuation after it; a word and its particle of one or two letters after a hyphen (`.glue`).

**Inline code** never breaks inside a name: `markdown.py` puts a `<wbr>` after each slash (and after each dot of an
address in a link), never before a dot or a piece shorter than four characters, and the style sheet keeps the rest
whole (`overflow-wrap: break-word`, so a table column widens to its longest piece). A split paragraph is never cut
inside inline code, and a word broken at its own hyphen keeps one hyphen, not two.

**Bubbles**, big and small, stay flush left: justified, their short lines opened wide holes between words.

**Links** in notes show only the site's name and never break (a broken link made PDF viewers underline the text beside
it).

**Tables.** Countries carry a flag; a cell written `- one<br>- two` is a little list; results are a matrix (models
down, ratings across, «—» where absent) with scores tinted green within 5 points of a rating's leader and wine-red
more than 10 behind; the legend is said in the text. A long table breaks between rows with its header repeated.

---

## Layout rules

The paginator (`theme/paginate.js`, see [build.md](build.md#the-pipeline)) composes every page in the browser. These
are the rules it follows; the build reports a broken one as a layout warning, and `--strict` fails on it.

### Rows and widths

- **Dynamic, row by row.** Every top-level block is a row of the grid. A row with nothing beside it spans the full
  172 mm. Whatever a row has for the margin (a 48 mm note, a remark, a figure, an accent) **floats** at one edge and
  the text **wraps round it**: beside the note the text is narrow, below it the paragraph runs on at full width.
- Boxes (code, cards, the monitor) narrow beside a note instead of running under it; a block that must be wide waits
  below.
- A page mixes column-wide rows and full-width blocks; stretchable blocks alternate automatically (see
  [Blocks](#blocks)).
- **`side:`** in the front matter or `<!-- side: ... -->` in the text. `outer` (default), `inner`, `left`, `right`
  only say where the first note of a page goes. `center` is one 172 mm column. `full` is one 168 mm column with no
  margin for dense pages: a `note` becomes one small line under its block (a little head and the words), nothing is
  placed to fill the sides, no block sticks out of the column. A line there holds about 100 characters against 70 in
  the usual column, so keep it for tables, long listings and reference pages, not for running narrative. Switching
  on a page that already has content starts a new page.

### Margin notes

- Notes float beside the text; the text wraps round them and never pushes the column apart; close notes stack.
- Notes on a page alternate between the outer and the inner edge; while one still hangs down, the next takes the same
  edge, so text is never squeezed between two.
- Stacked notes never touch: `NOTE_GAP` (6 mm) between them, the same air as between a note and whatever comes under
  it.
- **No stray lines under a note.** A last line, or two, that would run out alone at full width under a note stays
  beside it: the note column is lengthened (measured from real line boxes, re-measured after narrowing). This holds
  under the paragraph's own note and under one still hanging from the paragraph above. The build checks every
  paragraph line by line.
- **No hole beside hanging notes.** If the notes of a page hang more than `HANG_MAX` (15 mm) below its last line, the
  lowest one leaves the margin and runs across the page under the text: portrait on the left, a wide bubble to the
  right with its tail pointing back; repeated while it helps.
- **Before a heading, a table, steps or any block that is not a plain paragraph**, notes hanging far below the text
  become wide notes across the page, so no hole is left. A block with its own title (steps) starts on a clear line.
- **No empty blocks beside notes:** a note that would leave an empty block beside the next note or paragraph is set
  `wide`, so the following remark and the text start level.
- **A note never stands between a lead-in and its list.** A note that leaves the margin for a row across the page
  (`widenOwnNotes`, `widenHangingNotes`, a split paragraph's questions) never lands between a paragraph ending with a
  colon and the block it introduces: it goes above the lead-in (`aboveOf`); the paginator warns if one still does.
- A character's question that the next paragraph answers stays above that answer: when such a note has to go wide, it
  is placed above its paragraph, not at the foot of the page.

### Lightness: accents

There is no empty margin: rows without notes span the full width. But wall-to-wall text is heavy, so after
`ACCENT_EVERY` (70 mm) of full-width text with nothing beside it, the next tall paragraph (`ACCENT_FROM`, 24 mm or
more) gets an **accent**: a character in a soft circle (25 mm) or an object (18 mm), taken in turn from `ACCENTS` in
`pages.py`, centred against it.

- The text wraps round the accent's box; a character accent has a square box so its soft circle never reaches into
  the text.
- Two accents per page at most, and only if the page still fits.
- Accents keep a paragraph's stray last lines beside them like notes do.
- Nothing is ever put into an empty margin or gap to fill it: no ornaments, no margin fillers.

### Air

| Between | Gap |
|---|---|
| blocks | `BLOCK_GAP` 4.6 mm; boxes with shadows, tilts or tails get extra margin |
| two paragraphs of running text | `TEXT_GAP` 3.4 mm |
| a heading and its first block | `AFTER_HEADING` 5.4 mm |
| a quotation and its attribution | 3.4 mm |
| stacked notes | `NOTE_GAP` 6 mm |

A page whose next block misses it by a little closes its gaps (`*_TIGHT`: blocks 2.4 mm, list items 0.4 mm) rather
than leave a hole. A page that ends early may move its blocks apart by at most `SPREAD_MAX`.

### Headings

- A heading clears every float and stands on its own line.
- **A section never starts at the foot of a page with a line or two of itself:** when a block moves on, a heading
  followed by less than `SECTION_MIN` (21 mm, three lines) moves on with it.

### Filling pages and splitting blocks

A page is for content: an illustration never takes a half or a third of a page. So `paginate.js` fills a page from the
next one:

- **Paragraphs** split between lines: at least 2 lines on each side, the first part's last line justified (`p.cut`).
- **Lists and `steps`** split between items, even when they fit a page: at least 2 items on each side, or 1 when every
  item is three lines or more. The steps title stays with the first part; the numbering runs on.
- A block that fits a page but not the rest of this one **moves on whole** - unless the empty space plus the smallest
  footer would take more than `HOLE_MAX` (99 mm, a third of the page). Then:
  - a sheet (`file`), code block or terminal splits between lines: at least 4 on each side; the first part ends with
    «продолжение →», the second repeats the title bar;
  - a table splits between rows: at least 2; «продолжение →» under it, the header row repeated.
- **A prompt is never cut while it fits a page:** its monitor moves on whole. Only a prompt taller than a page goes on
  to a second monitor («продолжение» in its title line); `book prompts` still exports one file.
- **Speech and callouts never split.** A chat never splits.
- A paragraph of up to three lines that ends with a colon moves on with the list or steps after it (`leadsInto`).
- Only a block taller than a page and unable to split is reported (`too-tall` in the audit).

Tests: `tools/tests/test_pagination.py`.

### Footer sizes

| Size | Height | When |
|---|---|---|
| `s` | 34 mm | the usual footer |
| `m` | 55 mm | the usual footer |
| `l` | 80 mm | only before a block that cannot move up (a prompt, or a short lead-in ending in a colon with its list), at most `FOOT_LARGE_MAX` (3) a chapter; past that the paginator gives `m` and the page keeps a hole, which the audit reports so the text can be moved |
| `fill` | up to `FOOT_MAX` (190 mm) | before a prompt that moved on whole, see below |
| panorama | `FOOT_PANORAMA`..`FOOT_MAX` (110-190 mm) | only on the last page of a chapter, which nothing can fill: one big panoramic scene, a world's finale |

`render.py footer_findings` reports an `l` beyond the limit and any `l` before plain text.

**A prompt that moved on whole leaves no hole.** The text is never trimmed to fit a page. When the page ends because
the next block is a prompt that fits a page but not the rest of this one, its footer grows up to the last line, with
the usual air under it, up to `FOOT_MAX` (size `fill` in `page.foot` and in the report's `feet`). The scene shows more
of its world above the station - more wall, roofs, sky, trees - never a stretched drawing. This is the only exception
to the `l` size and to `FOOT_LARGE_MAX`, and a `fill` footer is not counted among the large ones. It is decided in
`finishPage` alone, after the page's content is final, so no layout choice can aim at it: every preference above
(pulling text up, splitting paragraphs, lists, code and tables, `HOLE_MAX`) comes first, and the book never gains a
page by it. `footer_findings` reports a `fill` footer anywhere else; the audit does not count a hole there. Tests:
`tests/test_pagination.py` (a fixture book and the whole book keep their page counts), `tests/test_audit.py`, and
`tests/test_world_frames.py`, which draws every station up to `FOOT_MAX`.

### The prompt monitor

- The screen is always 4:3 (`aspect-ratio` with `overflow: hidden`); the monitor never stretches lengthwise and is
  never larger than the page within its margins.
- `paginate.js` sizes every monitor before pagination from its text alone: the smallest width from `MONITOR_MIN`
  (64 mm), in 4 mm steps, up to `MONITOR_MAX` (172 mm, the text width), on which the text fits.
- Up to `MONITOR_NARROW` (108 mm) a monitor shares its row with its hint in the margin. Wider, the row goes wide, the
  monitor stands centred and the hint becomes a wide note above it. A hint that had to go above its monitor never stays
  alone at the foot of a page: it moves on with the monitor.
- At the largest width the type steps down to 85 %, then the rest goes on to another monitor of the same size.
- A short prompt does not squash it into a letterbox: the lines sit in its middle, and more text makes it larger.

### Block details

- **Quotes:** every character can stand in a card, in varied poses, inside the card at its full height but smaller,
  not peeking over it; the opening and closing marks are the same size.
- **Steps:** the number badge is centred on its text: on a one-line step, and on the middle line of three.
- **Checklist poster:** a character with `HOLD_Y` in its module (the professor) holds it, standing behind it torso up,
  and only the fists on its top edge are in front; the others peek over its top edge.
- **Speech bubbles:** bubble and tail are outlined as one shape (ink layers, then white layers), so the join is exact;
  the tail never touches the speaker. No name captions under speakers.
- **Terminal:** no caption and no text in its title bar unless `title=` is given; the three dots say what it is.
- **Contents:** the dotted leaders run at mid-height between the title and the page number.

### Nothing runs into anything

After layout the paginator checks every line of text and every box against every drawing on the page (footer scene,
header character, accents, the characters of bubbles and quotes) and reports a hit as a layout warning. After layout
every drawing also gets unique ids (`uniqueIds`), so a reused drawing never takes another's clip path. Text off the
sheet is a warning.

Composing a page is an art: notes, figures and remarks are placed so pages read well, carry about the same amount of
content, and end with content.

---

## Front pages, cover, contents, map and farewell

- **Cover:** the plate «Методичка / профессора / Фортрана» in three stacked lines (`title`, `title_highlight` in
  `book.yml`); below it the name of the book (`headline`) in Dela Gothic One, white with an ink outline, the phrase
  from `headline_highlight` on a pink plate. The highlighted phrase is the largest thing on the cover (1.2x the
  headline) with clear air above and below - the lines round it never touch its plate - and the series plate above
  is deliberately small. The head block is centred between the top band and the illustration. Topic stickers sit on
  the top band (`topics`), a handwritten subtitle below (`subtitle`). The version is printed in the bottom band
  between the author and the year.
- **Front pages** are ordinary chapters with `front: true`, placed after the cover in this order and left out of the
  contents: about the author (`00-front/1-author.md`), «Свежая версия» (`2-fresh.md`: a ticket with a QR code and a
  button for the newest PDF and the version of this copy - `download`; the repository with a big star - `github`),
  thanks (`3-thanks.md`), the licence (`4-license.md`; see [ADR 0003](adr/0003-licenses.md)). A front page that does
  not fit on one page is broken by hand into a two-page spread (`<!-- pagebreak -->`).
- **Contents** («Что внутри») lists the whole book from `plan:` in `book.yml`: written chapters with their sections and
  page numbers; chapters not yet written greyed with «скоро» and drawn closer together (`TOC_PLANNED_GAP`), so the
  plan fits on one page. A written chapter missing from the plan is listed at the end rather than lost. Each written
  chapter shows its reading time (`reading.py`): the running text read - paragraphs, notes, bubbles, lists, tables,
  prompts' text, not code or listings - over `READ_CPM` (900 characters a minute), rounded to 5 minutes.
- **The map of the book** (`art/bookmap.py`): its own page right after the contents, only when `book.yml` has a
  `plan:`. A road from the professor's courtyard (introduction) through every chapter's world to the computer city
  (conclusion, the same city as on the farewell page); a wooden plaque at each stop with the number, the title and the
  reading time; unwritten stops faint with «скоро»; the railway of chapter 11 along the bottom, faint until chapter 11
  is written, then drawn in full with its engine in the chapter's color. A written chapter whose world has no vignette
  on the map stops the build with an error, so a new world needs its vignette there.
- **The farewell page** (`art/farewell.py`): a full page after the last chapter of the plan, only in a full build with
  `plan:`, where all the characters leave for a computer city. A sunset behind a city built of computer parts (chip
  towers, server racks, RAM sticks, capacitors, a cable car) inside a circuit-board wall; a bright cobbled road with
  lamps in one-point perspective to the gate - a connector between heat-sink pylons, its doors open on a living street,
  a square and the far skyline; fields of orchards, vines and crops on either side with small agents at work (at most
  half our agent's height, none in the near fields); the five walking the near bend of the curved road. An homage to
  the original Professor Fortran book; the original's picture is not copied. About 500 KB of SVG.
- **Easter eggs:** the book hides a few easter eggs; `tools/tests/test_easter.py` keeps them in place.

---

## Chapter openers

The opener is a chapter's full-page colored first page: a big picture, the chapter numeral and title, and the speaker
under a bubble with the `lead:`.

- **Every chapter has its own, unique opener:** no two chapters share a `scene:`, and the scene, its props and its cast
  are drawn for that chapter's theme. A chapter with a `world:` takes the world's opener (`World.opener`).
- **Bright, rich and in the chapter's color:** the whole world seen at once, full of objects and life, every part of
  the page used, the chapter's color dominant across it.
- **Rich is not many:** one big hero object, a calm sky, the cast on a deck in front. Life comes from motion and from
  the cast doing something with the hero, not from more props. The weight is spread evenly across the page; every
  object has air; nothing unrelated to the story. The sky where the title goes stays calm.
- **The bubble is the speaker's:** the professor stands right under its tail, and the sky or wall above him stays
  empty, so it is clear who speaks. `Stage.speaker(..., air=...)` keeps what is placed after the bubble off it.
- **The bubble touches nothing:** a world opener declares the edges and things under the bubble (`Stage.keep_clear`:
  window frames, posts, railings, shelf edges), and the bubble keeps `CLEAR_MM` (4 mm) from them.
- **No character is cut by the opener's edge:** `Opener.reach` holds every character's full box, raised hands, tails
  and feet included; `tests/test_openers.py` checks every opener in use.
- **Characters stand on the floor of the scene:** their feet on the paving or floor in front, never on the verge
  behind it.
- **The title** (`title.py`) is drawn from the real outlines of Rubik 900 at 40 pt, ink on a paper plate per line,
  broken into even lines by rule; no white frame and no first letter set apart; its size is reserved in the opener's
  picture.
- **Title and numeral:** the title never runs into the big outlined numeral; a float as wide as the numeral pushes the
  first line aside (`NUMERAL_*` tokens), and the overlap check covers openers.
- **Low scenes:** characters are scaled so the professor's head stays inside the painted sky; a study scene with the
  cast placed from outside has no empty chair behind someone.

**Opener scenes.** `scene:` takes a story opener registered in `stories.OPENERS` (`morning`, `fair`, `valley`,
`house`, `library`, `proving`, `lab`, `crossing`, `moonbase`, `forestcamp`, `railway`, plus the openers the worlds
register) or a generic setting: `meadow`, `path`, `pond`, `room`, `study`.

---

## Worlds and footer scenes

A footer is drawn for each page by Python after layout (`art/footers.py`): the paginator reports each page's height
left for its footer, its chapter, its headings and text, and receives the SVG back ([build.md](build.md#the-pipeline)).

### How a world works

A chapter with `world:` in its front matter gets a **camera along its machine** (`art/worlds.py`):

- The world's opener is the chapter's opener with its machine off.
- `schedule()` lays the chapter's pages along the stations in order, never back: a station gets pages in proportion to
  its beats, its beats shown in turn (`World.alternate`), so two pages in a row never show one moment. A chapter
  shorter than its machine visits stations spread evenly from first to last.
- The last page is the **finale**: every station at once, running and labelled.
- A world is a module that registers its stations, the backdrop of a frame, the finale and the opener; its lettering
  lives under `worlds: <name>:` and `openers: <name>:` in the locale.
- `uv run book storyboard <chapter>` puts the opener and every frame in page order on one sheet in
  `<temp>/bookkit/storyboard/`; `--world <name>` previews a chapter in a world it does not live in yet, without
  touching its file.

A chapter without a world gets **episodes** (`art/episodes*.py`, registered with `@episode`): little stories chosen by
the topic words of each page (`footers: <episode>: topics` in the locale), none twice in a chapter.

### Frames

Enforced by `tests/test_world_frames.py` for every world, station, beat, height, side and seed:

- Nothing in a footer is cropped at a frame's top or bottom; every character and object is whole.
- The floor is always seen under the feet: the camera puts the feet line at least 14 % of the frame above its bottom;
  the test requires at least 12 % (`AUDIT_FLOOR`). A strip shows fewer things whole, never feet below its edge, and
  characters never stand too close to the foot of the page.
- Two neighbouring pages never show the same picture: they differ in beat and in cast or camera distance. Beats
  alternate, and every other page the camera stands a step back (14 % smaller in the shared `world_fair.zoom`). A
  mirror alone is not enough.
- A station fills most of the frame's height, the floor about a sixth; the professor, the tallest, is left out of
  mid-height frames when he limits the scale.
- The back wall is a continuous row of the world's furniture (bookcases, pegboards, shelves), calmer than the station
  and in the chapter's color.
- The backdrop's top melts into the paper under a veil of flat-opacity layers (`Canvas.fade`); the page-number tag's
  corner is kept clear.
- Every frame has a story and its cast: two to four characters wherever there is room, each in their role (the
  professor sets the task, the agent works, the cat checks, the caterpillar doubts, the sparrow gets into everything
  and is after the big red button all book).

### The kit of worlds

`art/world_kit.py`:

| Tool | What it does |
|---|---|
| `Pen.container`, `Pen.tag` | boxes with inner padding: 8 % of the smaller side (`PAD_SHARE`), at least `PAD_MIN` |
| ports and `connect(port_a, port_b)` | a cable, tube, ribbon or beam between two declared ports |
| `fitting()` | a cable boot, a hose collar and clamp, a rod collar at each end of a line |
| `sound()` | a sound word that finds free room |
| `text_box`, `tag_size` | lettering in tags |

Lines bend smoothly through `art/curves.py`, one algorithm for every hose and cable: every corner becomes a bend whose
curvature rises and falls as sine squared, the bend radius at least three times the line's thickness, and a straight
lead runs into each fitting along the port's direction. `tests/test_curves.py` checks steps of at most 8 degrees, the
radius and coaxial ends. Ropes that sag in one curve keep their own drawing.

Enforced by `tests/test_world_space.py` and `tests/test_world_kit.py` for every station, beat, height and side of every
world: containers (boards, plates, panels, screens, tags) only through `Pen.container` / `Pen.tag`, with padding and a
gap between siblings; cables, tubes, ribbons and beams only through `connect()` between declared ports, leaving along
each port's direction, never crossing other objects or characters; no abstract signs; every node commented with what
it is and why it is there.

### The worlds

| World | Module | Chapter | Color | Opener |
|---|---|---|---|---|
| `front` | `world_courtyard.py` | the front pages and the contents | `sky` | none |
| `courtyard` | `world_courtyard.py` | introduction | `sky` | the generic opener |
| `kitchen` | `world_kitchen.py` | 1 | `coral` | `kitchen` |
| `fair` | `world_fair.py` | 2 | `blue` | `fairground` |
| `station` | `world_space.py` | 3 | `orange` | `station` |
| `library` | `world_library.py` | 4 | `teal` | `reading_room` |
| `attic` | `world_attic.py` | 5 | `green` | `workshop` |
| `sea` | `world_sea.py` | 6 | `purple` | `deepsea` |
| `lab` | `world_lab.py` | 7 | `yellow` | `laboratory` |
| `harbour` | `world_harbour.py` | 8 | `orchid` | `lighthouse` |
| `moon` | `world_moon.py` | 9 | `periwinkle` | `lunar_base` |
| `camp` | `world_camp.py` | 10 | `mint` | `forest_camp` |
| `railway` | `world_railway.py` | 11 | `crimson` | `railway_station` |
| `city` | `world_city.py` | conclusion | `lime` | `city_road` |

Station by station:

- **The kitchen** (chapter 1): the kitchen is the repository and the pie is the agent's work. Stations: recipe
  «Задача» → pantry «Кладовка» → oven «Духовка» → slop «Слоп» → fridge «Правила» (the note on it is `AGENTS.md`) →
  «Как надо». The pantry is open wall shelves with jars, red polka-dot tins and, on the low shelf, the old stock
  (копипаста as a spaghetti pack, легаси as a dusty jar, костыли in a crate); the stove and the tall fridge (height
  2.1 × the counter, width 0.48 × its height) stand in the cabinet row (`s.niches`, `counter_row()`), a hood over the
  stove; a cork board with push pins; the red button is a wall e-stop under a flip cover.
- **The fair** (chapter 2) and **the space station** (chapter 3): see their modules.
- **The library** (chapter 4): door with the «AGENTS.md» sheet → reception desk → rolling ladder on a brass rail → an
  aisle's own sheet on a stand → card catalogue with a drawer pulled towards the viewer → the archive of decisions
  (tabs «контекст / решение / отвергли / последствия») → a reading table with a big book on a bookrest and paper
  bookmarks → the sorting trolley → the reference binders → the check (the cat times the agent).
- **The attic workshop** (chapter 5): the old playbooks pinned to a beam → the skill card in a stand with its tool tray
  → the bench where the agent makes the same bracket again → the card index with tabs → the agent writes a card → the
  lathe takes the punch card «/adr» → two shelves, one by the window, one by the stairwell → the check (caliper against
  the drawing) → a parcel up through the floor hatch with a stranger's tool.
- **The undersea base** (chapter 6): a row of big windows on the coral labyrinth behind every frame; the dock where the
  agent starts the submarine → the preview tank → the switch panel lighting only the shell houses needed → the map
  table of the labyrinth → the test desk → the camera outside a porthole and its replay → the submarine leaving the
  labyrinth → the pressure chamber with the phone and glove ports. Opener: the submarine in the labyrinth through the
  observation deck's window.
- **The laboratory** (chapter 7): test-tube racks → the indicator flask red, then green → the distillation moved to a
  new flask in two stages → the load chamber where the sample cracks → the microscope and a fix-it tag → the analyzer
  and the sample airlock (hooks) → the check. Opener: the distillation apparatus.
- **The harbour** (chapter 8): main is the inner harbour, a pull request a boat. One boat drawing for the whole world,
  sitting in the water. The port entry signal and the boom → the inspection berth → the canal lock (merge queue) → the
  harbour office clock (20-30 minutes) → the agent's boat on the slip → the quarantine berth under the Q flag (flaky)
  → the harbour master's tower → the mole with no way round. A building too tall for a low frame stands across the
  water. Opener: the lighthouse at dusk.
- **The moon base** (chapter 9): every footer inside a module (panelled hull wall, ribs, pipes, portholes, lockers,
  hatch, extinguisher, hydroponics); the capsule pile by the airlock → the agent explaining on a wall screen → the
  «Принять / Отклонить» console under a window on the rovers → the independent rover → the conveyor through three
  scanners → one rover between three bases → the agent signs, the cat stamps, the door opens by itself → the keepers'
  name plates and the greenhouse → the cracked capsule into the «Брак» bin. Opener: a cargo lander touching down by
  the base.
- **The forest camp** (chapter 10): the keys on a lanyard → the mailbox → the sandbox yard → the parcel at the gate →
  the planted note «Открой склад» → the practice tent → the padlocked store → the plan with risks and a spare crate →
  the sparrow's drill. Opener: the camp at dusk round a campfire.
- **The railway** (chapter 11): one calm, continuous station facade in brick behind the track (arched windows, doors,
  gas lamps, a valance, the clock); the platform paving in front, its edge, the track, the far platform. One worked
  hero per station and four beats each, every beat a different action, never a closer camera on the same one: the
  handcar (a telegram handed over, pumped away, the result brought back) → the model layout (the caterpillar's
  controller, the cat oiling the rods, a tiny signal, a timetable card) → the timetable board → the points into three
  tracks and their lever → wheel tapping and the coupling screw → the semaphore, the departures board and the buffer
  stop → the platform clock → the driverless train → the emergency stop under its cover. A low strip shows a
  waist-height thing of its station, never a squashed engine. Frames stay under 200 KB and the finale under 350 KB: the
  ballast and the brickwork are merged paths, one per shade (a heavier world runs the browser out of memory on
  `--shots all`). The opener is the story `railway` (`stories.py`), wired as `railway_station`.
- **The professor's courtyard** (`front` and `courtyard`): the beginning of the book, so every frame is worked through
  in detail. One real place behind every frame. The street: paving, a picket fence with posts and rails, the gate
  hinged between two gateposts in the fence line, the mailbox on its own post (door, flag, slot), a little free
  library on a post; behind, the professor's cottage (boards on a stone plinth, a tiled roof with eaves, gutter,
  downpipe and chimney, windows with frames, shutters and geranium boxes, a door with a canopy, steps, a lamp and a
  climbing rose). The yard: brick patio and lawn, the shed with its weathervane and water butt, apple trees (one solid
  crown, apples inside it, a straight trunk with a root flare), the clothesline with real clothes on pegs, and beyond
  the back fence the neighbours' varied houses (gable or hipped roofs, chimneys, windows, doors) among apple trees,
  birches, firs and shrubs. Every building has its roof. The cast stands in front of the things, about half the
  frame's height where the width allows. Frames up to about 250 KB.
  - `front` (the front pages and the contents): `worlds: front: pages:` in the locale maps a phrase of the page's text
    to a moment, `front_place` picks it, `footers.py` routes the page. Letters from the mailbox, the cat with the
    newspaper (about the author); the printer on a workbench under a striped awning printing the book, a stack of
    copies, the agent carrying them to the professor (fresh version); a gap in the fence, the agent holding a new
    picket, the caterpillar nailing it, an open toolbox and a paint tin, then the cat painting it (make it better); a
    tablecloth, cups on saucers, biscuits and jam, the professor pouring from the teapot (thanks); the cat putting the
    book into the little free library, the caterpillar waving from the open gate (licence); real rucksacks being
    packed, the map on the bench (contents). The printer's station is never mirrored.
  - `courtyard` (the introduction, which keeps the generic opener): the toy steam engine on the garden table → the old
    beige computer with its editor, then the laptop with the agent's chat → a kettle grill on its tripod (burnt
    sausages, then golden ones); finale: the four in front, the engine and a raised bed behind where the sparrow digs
    with a trowel, no labels.
- **The road to the city** (`world_city.py`, the conclusion): the farewell page's walled city with its gate, small and
  far (`farewell.city_view()`), a cobbled road through fields of wheat, orchards, vines and cabbages. The apple tree by
  the road → the handcart with its crates; finale: the four walking the near stretch toward the bend. Opener
  `city_road`: the professor at his gate under the bubble, a fingerpost with two arms («В город» toward the city,
  «Домой» back to the gate), the cast on the near bend at one scale with him.
- **The curved road** (`road.py`, the farewell page and the conclusion): laid out on the ground plane and projected, so
  it never reads as a staircase; it comes in from the left edge at full width, bends wholly inside the page with both
  kerbs and verges seen, then runs straight into the gate, its width converging to the gate's opening; setts in
  staggered courses that shrink with distance, each with its light edge and shade; smooth kerbs and gutters; grass
  verges.
- **The walking cast of the closing pages:** no back views, and no heads turned back while walking forward. The
  professor walks in `walk`, the cat, the caterpillar and the agent in `stride`, all toward the bend, one group with a
  gentle depth step; a warm rim on the side facing the sunset and a long soft shadow on the setts.

---

## Drawing rules

Every picture is code (`tools/bookkit/art/`). These rules hold for every opener, footer, accent and doodle.

**Content**

- No mice and no spiders anywhere: no mouse, mouse hole, cheese, spider, thread or cobweb. A computer mouse is hardware
  and may stay.
- No currency symbols: no $, ₽ or other currency; a price is shown by size or by coins.
- Every object explains itself: a reader sees at once what it is and why it is there, at 34 mm and at 190 mm. No
  abstract signs - no bare rings, dots, lamps on posts, «!» or ticks; an indicator is a recognisable object, labelled if
  needed, and only where the story needs it. Whatever cannot answer «what is it, why is it here» is removed.
- A metaphor must explain itself; no symbolic props. A station is a real operation of its world that a reader recognises
  at once (a port entry signal and a boom, a canal lock, a boat on the slip), never a prop standing for an idea (an
  hourglass for time, a bell for flakiness, a lamp for inspection).
- No captions that explain a picture: a frame names nothing; a thing reads by its look. Words stay only where they are
  part of the thing (a jar's label, a switch's ВКЛ/ВЫКЛ, a screen) and on a world's finale, which labels its stations.
- Every number on a sign says what it is compared with: give the unit and what it was.
- A sound word is replaced by what makes the sound.

**Realism and scale**

- Real things, worked through: every object is drawn like the real one with its parts (a lathe with chuck, carriage
  and tailstock; a knife switch in its cabinet; a ladder on its rail and castors), standing on its legs or posts. Smoke
  and dust are many puffs fading back. Rich, but not overloaded.
- Devices are realistic and recognisable: a stove with burners, knobs and a window; a wall switch with a lever; an X-ray
  tunnel with a lead curtain. Household appliances stand built into the counter row, a fridge about twice the
  counter's height; a shelf looks like a shelf and hangs on the wall.
- Objects are in proportion to the characters: a door at least 1.3 times the tallest character; consoles and conveyors
  at waist height; screens at eye level. A tall object that cannot stand at true scale in a low strip is left out of
  that strip, and the characters stay big.
- Things sit in the world at their true scale: a boat sits in the water below its waterline with its reflection; boats
  and other things never overlap; a building is 2.5-4 times a character beside it or stands far away, its size read as
  distance; all characters of a frame have one scale and none stands over an object. A flag is cloth on a staff and
  means something (green passed, red not yet, yellow Q only in quarantine).
- Desks are deep enough for what stands on them: the computer at the back, the keyboard in front of it
  (`props.desk(depth=)`, `props.keyboard()`); a desk a character works at is about waist-high to the professor.
- Characters never climb on tables or counters; only the sparrow perches, and only on something a bird would sit on.

**Composition**

- Nothing in a scene overlaps anything else: trees, flowers, mushrooms, stones, props, the signpost, furniture, the
  window and the picture each take their own place with air round it; a thing that finds no room is left out, never
  squeezed in. `art/scenes.py` places them so; `tests/test_scenes.py` guards it.
- No two objects stick to each other or to a window. Content inside a block keeps off its edges: containers have inner
  padding, siblings inside one object keep a gap, the working part of a device sits centred on its face.
- No large area of one flat color, and no stipple instead: ground is drawn as a real surface - paving, planks, kerb and
  verge.

**Bodies and hands**

- Arms leave the torso at its sides, never its front face; the cat's vest is clipped to the body so no fur shows
  between vest and arm (`tests/test_grips.py`).
- A held thing is drawn through the grip, never put next to a hand: `Stage.hold(box, make, side, turn)` on a page,
  `characters.draw(name, pose, hold={"right": make})` alone. A hand that holds is three layers (the back of the fist
  with the thumb, the prop, the curled fingers; `rig.hold`); hands are a left and a right with the thumb toward the
  neck (`rig.hand_frame`). Ready props with their handle at the fist are in `art/handheld.py` (stopwatch, pencil, card,
  sheet, book, clipboard, caliper, magnifier, notebook, jar). A stopwatch lies in the palm (`rig._palm_hold`): dial to
  the viewer, fingers over the rim, the thumb on the button; the cat takes off his wristwatch on that paw.

**Cables and lines**

- Cables, hoses, tubes and ropes are attached: drawn only between declared ports, leaving and entering along the port's
  direction, with a fitting at each end, never through another object or a character. A reel pays out from its outer
  wrap; a thing held is held by its grip and its cable leaves from its back.
- Every line bends smoothly through `art/curves.py` (see [The kit of worlds](#the-kit-of-worlds)).
- The crate's cable curls from its lid and the plug lies on top, in four curls by seed, so nobody stands on it.

**Lettering**

- Signs, labels and sound words in pictures are set in Comfortaa 700 (`SIGN_FONT`, variable, cut to its weight):
  large lettering white with an ink rim (`SIGN_RIM`) and a small extrusion (`SIGN_DEEP`), set flat below
  `SIGN_BALLOON_FROM`; labels on things flat in ink (`style="label"`, 15 % above the shelf's size, `LABEL_GROW`). A
  glyph it lacks falls back to Rubik. Screens and displays keep Rubik (`PLAIN_FONT`).
- Lettering is never squeezed: a line too wide is set smaller as a whole (`ink.lettering(room=...)`), its width measured
  on the real glyph advances, or its sign is made wider.
- Labels keep off the edges of what they are on.

**Speech in footers:** `footers.py Strip.say` grows the tail out of the bubble in one smooth outline, with no corner
where it joins.

**Doodles** (`art/doodles.py`, 44 functions registered with `@doodle_drawing`) are small standalone objects: the
object accents beside paragraphs, the icons of `contacts`, `download` and `github`, and a proof sheet
(`uv run book sheet`).

---

## Printing: the same PDF in every viewer

Chrome prints some things as a 72 dpi raster with a soft mask, which Apple's viewers (iOS, Telegram, Preview) draw in
torn patches. So the PDF holds only what Chrome prints as vectors (see [ADR 0002](adr/0002-vectors-only.md) and, for
why Chrome prints it, [ADR 0001](adr/0001-pdf-through-chrome.md)):

- No SVG `<mask>` or `<filter>`.
- No gradient with transparent stops: `Canvas.gradient` is opaque only; `Canvas.fade` stacks flat-opacity layers
  instead.
- No gradient background on a box with rounded corners: the gradient goes into a `::before` layer rounded by
  `clip-path: inset(... round ...)`; the box keeps its border and shadow.
- The highlighter marker is an inset shadow; the portrait medallion's backdrop is drawn inside the SVG
  (`figure(medal=True)`).
- Every glyph comes from the bundled fonts: marks the fonts lack (★ ✓ ✗ ✦) are drawn (`graphics.MARK_*`); the tree's
  arrow is set in the mono face.
- Variable fonts are cut into a static font per weight (`fonts.py`, cached in `<temp>/bookkit/fonts/`, every axis
  pinned), so the PDF embeds TrueType, not Type 3. Stroked text stays Type 3: Chrome has no other way.
- The build scans the PDF and warns (`--strict` fails) on any image beyond the book's own `<img>` pictures and on any
  font of the building machine (`render._raster_warnings`, `render._font_warnings`).

---

## Ideas

Profile views for the cat and the caterpillar; comic strips; full-spread illustrations; a back cover; bleed for a print
shop.

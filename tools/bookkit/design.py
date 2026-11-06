"""Design tokens: the single source of truth for color, type and page geometry.

Everything visual in the book reads its values from this module:

* the illustrations (`bookkit.art`) import the color constants directly;
* the style sheets (`theme/css/`) contain no literal colors or page sizes at all -
  `css_variables()` turns every token below into a CSS custom property
  (`PAPER_SHADE` becomes `--paper-shade`, `FOOT_HEIGHTS["m"]` becomes `--foot-m`)
  and the compiler injects that block ahead of the stylesheet;
* the paginator (`theme/paginate.js`) reads the geometry back from those properties.

Rules for evolving the palette
------------------------------
1. Never write a hex color anywhere else. `tests/test_design.py` fails the build if one appears
   in the art, the components or the stylesheet.
2. Before adding a color, look for an existing one of the same material. A lighter or darker
   variant is derived with `lighten()` / `darken()` at the point of use, not declared: shading
   in the drawings is computed, so one base color per material is normally enough.
3. A new constant needs a name that says what it *is* (`WOOD`, `SKIN`), not where it is used.
4. The chapters' colours (`CHAPTER_*`, named in `ACCENTS`) are the only saturated UI colors. A chapter picks one
   as its `--accent`, and no two chapters share one.
"""
from __future__ import annotations

# ============================================================================ color helpers


def _rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    if len(color) == 3:
        color = "".join(ch * 2 for ch in color)
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def darken(color: str, k: float = 0.8) -> str:
    """Multiply a color towards black, shifting slightly to a cooler hue (the shadow tone)."""
    r, g, b = _rgb(color)
    return f"#{int(r * k * 0.97):02x}{int(g * k * 0.98):02x}{min(255, int(b * k * 1.04)):02x}"


def lighten(color: str, k: float = 0.35) -> str:
    """Blend a color towards white by `k` (0 = unchanged, 1 = white)."""
    r, g, b = _rgb(color)
    return f"#{int(r + (255 - r) * k):02x}{int(g + (255 - g) * k):02x}{int(b + (255 - b) * k):02x}"


def mix(a: str, b: str, k: float = 0.5) -> str:
    """Blend color `a` towards color `b` by `k` (0 = a, 1 = b)."""
    (r1, g1, b1), (r2, g2, b2) = _rgb(a), _rgb(b)
    return f"#{int(r1 + (r2 - r1) * k):02x}{int(g1 + (g2 - g1) * k):02x}{int(b1 + (b2 - b1) * k):02x}"


# ============================================================================ palette
# --- neutrals
INK = "#1d1815"            # outlines and text
PAPER = "#fbf4e2"          # the page
PAPER_SHADE = "#f4e9cd"    # inline code background, quiet fills
PAPER_FOLD = "#e6e0d0"     # the underside of a folded corner
WHITE = "#ffffff"
CARD = "#fffdf6"           # cards, sheets, book pages
CREAM = "#fff6e0"          # labels, signboards
CHARCOAL = "#3a3531"       # cables, title bars
DESK = "#6b665d"           # the surface behind the pages on screen; dark slots
PEN = "#25408a"            # handwriting in the margins
GUIDE = "#b3a78d"          # faint guide lines

# --- saturated colours of the drawings
PINK = "#ea5a77"
TEAL = "#2fa7a5"
YELLOW = "#f6c443"
ORANGE = "#ef7d3c"
GREEN = "#57b45a"
BLUE = "#3f7fc4"
VIOLET = "#8a6bbf"
PLUM = "#c0569b"
INDIGO = "#4f55b8"
PINE = "#17664f"
RUBY = "#a8263b"          # chapter 11: deeper and darker than PINK, RED and BAD

# --- the chapters' colours: a palette of colours that read apart and are pleasant to read. Thirteen hues round
# the wheel, about 25 degrees apart in OKLCH; neighbours on the wheel differ in lightness too, so no two read alike;
# every one keeps ink text on it at 4.5:1 or more. Consecutive chapters sit far apart on the wheel. The front pages
# share the introduction's sky.
CHAPTER_SKY = "#76cef4"         # the introduction and the front pages
CHAPTER_CORAL = "#fb8371"       # 1
CHAPTER_BLUE = "#3c8ae7"        # 2
CHAPTER_ORANGE = "#e69300"      # 3
CHAPTER_TEAL = "#07a4a4"        # 4
CHAPTER_GREEN = "#4db956"       # 5
CHAPTER_PURPLE = "#a169da"      # 6
CHAPTER_YELLOW = "#f4cd4b"      # 7
CHAPTER_ORCHID = "#e685c3"      # 8
CHAPTER_PERIWINKLE = "#9aa0ec"  # 9
CHAPTER_MINT = "#6cd5b3"        # 10
CHAPTER_CRIMSON = "#e1505f"     # 11
CHAPTER_LIME = "#99d352"        # the conclusion
ACCENTS = {name.removeprefix("CHAPTER_").lower(): value for name, value in dict(globals()).items()
           if name.startswith("CHAPTER_")}

# --- signals
RED = "#e9483f"            # ticks, alarms, bows, mushrooms
GOOD = "#2f8f3c"           # "do" marks
BAD = "#c8334f"            # "don't" marks

# --- warm tones
AMBER = "#f2a23c"          # hair, beak, curtains, pencil
GINGER = "#e2852f"         # the moustache
ORANGE_DARK = "#c96a24"    # the agent's boots
SUN = "#fbd24a"
GOLD = "#d9a92e"            # the golden floppies hidden in the worlds (easter eggs)
GOLD_LIGHT = "#f4d77a"      # their shine
YELLOW_PALE = "#fff3a8"
PINK_PALE = "#fbd0da"
EAR = "#e9a58f"            # inside of an ear
MOUTH = "#7a2a22"
TONGUE = "#e8736a"
SKIN = "#f7d2ac"

# --- fur, feathers, wood, earth
FUR = "#b96a38"
FUR_DARK = "#8e4d28"
FEATHER = "#8d5a38"
FEATHER_LIGHT = "#a9744a"
FEATHER_DARK = "#6f4329"
DARK_BROWN = "#3a2a1f"     # soles, wheels, the sparrow's bib
LEATHER = "#96623a"
TRUNK = "#b47a4c"
WOOD = "#d9a268"
WOOD_LIGHT = "#e6b77c"
WOOD_PALE = "#edca94"
WOOD_DARK = "#7a4f30"
TERRACOTTA = "#d9744a"
FLOOR = "#f0c08c"
FLOOR_DARK = "#e0a66d"
WALL = "#f3d7a0"
SAND = "#efd9a0"
PEBBLE = "#d8c7a4"
STONE = "#c7c0b3"
BIRCH = "#f4efe2"

# --- the old computer
BEIGE_LIGHT = "#f3e6c0"
BEIGE = "#eedfb4"
BEIGE_DARK = "#dcc993"
BEIGE_SHADE = "#cdb98a"
SCREEN_LIGHT = "#3d8fa6"
SCREEN = "#1b4f67"
SCREEN_DARK = "#163d55"
SCREEN_TEXT = "#e9f8ee"
SCREEN_VAR = "#ffab9a"     # placeholders in a prompt
GLOW = "#9ff0e0"           # the agent's face, list bullets on screen

# --- metal and glass
METAL = "#b9c2c6"
METAL_DARK = "#8d989d"
METAL_LIGHT = "#c5ced2"
METAL_PALE = "#e3e8ea"
SPACE_DEEP = "#1e2848"      # open space behind a station: the deep blue-black
SPACE_LOW = "#34406e"       # ... and lower, towards the planet
HULL = "#dfe5e8"            # the inside wall of a space station module
KITCHEN_WALL = "#f2dcb3"    # the kitchen's walls in the morning light (the world of chapter 1)
KITCHEN_TILE = "#e6eff0"    # the tiled splashback over the counter
KITCHEN_CABINET = "#9cc7b8" # the counter's cabinet doors, a mint green
KITCHEN_FLOOR = "#e7d3b0"   # the floor's light tiles ...
KITCHEN_FLOOR_DARK = "#c4a57c"   # ... and its dark ones
CRUST = "#e3a94e"           # a pie baked right: golden
CRUST_RAW = "#f3dfb2"       # a pie not yet baked: pale dough
CRUST_BURNT = "#6e4a2c"     # a pie gone wrong: burnt brown
JAR_DUSTY = "#b9b49a"       # an old jar's glass under its dust
KITCHEN_CORK = "#c99a62"    # the cork board the recipe is pinned to
KITCHEN_STOVE = "#f4f1ea"   # the stove's enamel
KITCHEN_KRAFT = "#c9a46c"   # a brown paper bag
LENS = "#f6fbfd"

# --- plants
GRASS = "#a9d98d"
GRASS_DARK = "#86c46f"
LEAF = "#64b558"
LEAF_LIGHT = "#7cc46a"
LEAF_DARK = "#3d8a3e"
FIR = "#3f9a5a"
HILL_FAR = "#cfeab9"
HILL_NEAR = "#bfe3a3"
CATERPILLAR = "#4fb866"
CATERPILLAR_DARK = "#379a50"
CATERPILLAR_NOSE = "#2b7040"
CATERPILLAR_BELLY = "#f9d94a"

# --- sky, water, cloth
SKY = "#bfe6f2"
SKY_LOW = "#d9f0ee"
SKY_DEEP = "#9fd3ea"
WATER = "#8fd0e6"
WATER_LIGHT = "#b9e4f1"
SWEATER = "#74a7dc"
SWEATER_RIB = "#4f86c6"
TROUSERS = "#3f5f96"
SUIT = "#66706b"
SUIT_DARK = "#4d5753"
SUIT_TROUSERS = "#5a6460"

# --- terminal and syntax highlighting
TERMINAL = "#26221f"
TERMINAL_TEXT = "#f3ead6"
TERMINAL_DIM = "#9d927e"
TERMINAL_GREEN = "#7fd6a0"
TERMINAL_YELLOW = "#ffd66b"
SYN_KEYWORD = "#b3306b"
SYN_STRING = "#1d7a58"
SYN_COMMENT = "#8a7f6c"
SYN_NAME = "#2456a6"
SYN_NUMBER = "#b45a12"
SYN_BUILTIN = "#7a4fb0"

# --- parchment
SCROLL = "#fff8dc"
SCROLL_SHADE = "#fbf0c4"

# Colors used to dress books on shelves and other multicolored details.
BRIGHTS = (PINK, TEAL, YELLOW, ORANGE, GREEN, BLUE, CREAM, VIOLET)

# ============================================================================ typography
# CSS variable -> font stack. The first family of each stack is bundled in theme/fonts.
FONTS = {
    "f-head": '"Rubik", "Arial Black", sans-serif',            # headings
    "f-body": '"PT Serif", Georgia, serif',                    # running text
    "f-talk": '"Balsamiq Sans", "Comic Sans MS", sans-serif',  # speech bubbles
    "f-hand": '"Caveat", cursive',                             # handwritten margin notes
    "f-mono": '"JetBrains Mono", Menlo, monospace',            # code and prompts
    "f-display": '"Dela Gothic One", "Rubik", sans-serif',     # the name of the book on the cover, nothing else
    "f-sign": '"Comfortaa", sans-serif',                       # small signs on the page: the continued mark
}
# (family, file in theme/fonts, weight or weight range, style)
FONT_FILES = (
    ("Rubik", "Rubik.ttf", "300 900", "normal"),
    ("PT Serif", "PTSerif-Regular.ttf", "400", "normal"),
    ("PT Serif", "PTSerif-Italic.ttf", "400", "italic"),
    ("PT Serif", "PTSerif-Bold.ttf", "700", "normal"),
    ("PT Serif", "PTSerif-BoldItalic.ttf", "700", "italic"),
    ("Balsamiq Sans", "BalsamiqSans-Regular.ttf", "400", "normal"),
    ("Balsamiq Sans", "BalsamiqSans-Bold.ttf", "700", "normal"),
    ("Caveat", "Caveat.ttf", "400 700", "normal"),
    ("JetBrains Mono", "JetBrainsMono.ttf", "100 800", "normal"),
    ("Dela Gothic One", "DelaGothicOne.ttf", "400", "normal"),   # subset: Latin and Cyrillic only
    ("Comfortaa", "Comfortaa.ttf", "700", "normal"),            # signs, labels, sounds; variable, cut to 700
)
# Lettering inside drawings (signs, labels, banners, totals) is set in balloon letters: a cartoon face, a thin ink
# rim and a small dark extrusion: the plain comic face looks primitive on signs. Speech keeps the comic face of
# the book's bubbles; screens and displays keep a flat face (`plain`).
SIGN_FONT = "Comfortaa"     # a round geometric face
SIGN_WEIGHT = 700
PLAIN_FONT = "Rubik"         # flat lettering on screens and displays
PLAIN_WEIGHT = 800
SIGN_RIM = 0.06          # the ink rim, in em of the lettering
SIGN_DEEP = 0.07         # the extrusion's offset, in em
SIGN_TRACK = 0.03        # letter spacing, in em
SIGN_WORD = 0.16         # extra word spacing, in em: the rim must not close the gaps between words
SIGN_BALLOON_FROM = 11   # smaller lettering is set flat: a rim would clog it
ILLUSTRATION_FONT = "Balsamiq Sans"    # speech in pictures, like the book's bubbles
ILLUSTRATION_WEIGHT = 700
# Hyphenation of running text (hyphenate.py): soft hyphens inserted at build time from the pyphen dictionaries, so
# every browser breaks the same words at the same places. No word shorter than HYPHEN_MIN_WORD letters, at least
# HYPHEN_LEFT letters before a break and HYPHEN_RIGHT after it.
HYPHEN_MIN_WORD = 5
HYPHEN_LEFT = 2
HYPHEN_RIGHT = 2
# The dictionary for each script: Cyrillic words by the Russian one, Latin words by the American English one.
HYPHEN_DICTIONARIES = {"cyrillic": "ru_RU", "latin": "en_US"}

# ============================================================================ page geometry (millimetres)
PAGE_WIDTH = 210
PAGE_HEIGHT = 297
MARGIN_INNER = 20            # towards the spine
MARGIN_OUTER = 18
COLUMN_MAIN = 116            # the text column
COLUMN_GAP = 8
COLUMN_SIDE = 48             # the margin column for notes
COLUMN_CENTER = 172          # the single column of the centred layout: the whole text width
COLUMN_FULL = 168            # the single column of the full layout: dense pages without a margin
TEXT_WIDTH = COLUMN_MAIN + COLUMN_GAP + COLUMN_SIDE
BODY_TOP = 24                # where the text block starts
BODY_GAP = 4                 # air between the text block and the footer scene
# Footer scene sizes, smallest first. A page is for content (an illustration never takes a
# half or a third of a page): a footer is s or m; l only when the next block cannot move up (an unsplittable block
# that does not fit), at most `FOOT_LARGE_MAX` times a chapter; the leftover space is filled from the next page.
FOOT_HEIGHTS = {"s": 34, "m": 55, "l": 80}
FOOT_LARGE_MAX = 3           # l footers before a stuck block in a chapter; the paginator gives no more (paginate.js)
# The last page of a chapter, which nothing can fill, is the one exception: when its free space would hold a scene at
# least FOOT_PANORAMA tall, it gets one panoramic scene up to FOOT_MAX (a big panorama
# instead of a big empty space; a world's finale is drawn there).
FOOT_PANORAMA = 110
# A block that fits a page but not the rest of one moves on whole - unless that would leave more than this empty (a
# third of the page): then a sheet, code or terminal splits between its lines, a table between
# its rows (`theme/paginate.js`). Prompts, speech and callouts never split.
HOLE_MAX = 99
FOOT_MAX = 190
AFTER_HEADING = 5.4          # between a heading and its first block
SECTION_MIN = 21             # a section starts at a page's foot only with this much under its heading (3 lines)
BLOCK_GAP = 4.6              # vertical space between blocks: generous, so neighbours never look stuck together
TEXT_GAP = 3.4               # between two paragraphs of running text: closer than blocks
# A page whose next block, which cannot be split, misses it by a little closes up its gaps to keep it, instead of
# leaving a hole and a large footer (a page is for content):
BLOCK_GAP_TIGHT = 2.4
TEXT_GAP_TIGHT = 2.2
AFTER_HEADING_TIGHT = 4
LIST_GAP_TIGHT = 0.4            # between the items of a list on such a page (1.2 mm otherwise)
ACCENT_EVERY = 70            # after this much full-width text with nothing beside it, a paragraph gets a picture
ACCENT_FROM = 24             # a paragraph at least this tall may take one
ACCENT_WIDTH = 25            # a character beside a paragraph; the text wraps round its circle
DOODLE_WIDTH = 18            # an object beside a paragraph
ACCENT_GAP = 3               # air between an accent's outline and the text wrapping round it
PERCH_HEIGHT = 15           # the character on the running head, drawing box included: the top of its head
#                              reaches the middle of the colored band
#         # the character on the running head: feet on the dashed line, head over the band
QUOTE_FIGURE = 30            # the character inside a quote card
QUOTE_MIN = 46               # a quote card is at least this tall, so its character stands at a readable size
STEP_PAD = 1.1               # above and below a step's text: one line of body text plus this is the badge's height
HANG_MAX = 15               # notes may hang this far below the last line of a page; lower, one goes wide
NUMERAL_WIDTH = 34           # one digit of the big outlined chapter number on an opener
NUMERAL_GAP = 6              # air between that numeral and the title
NUMERAL_CLEAR = 14           # how far the numeral reaches below the top of the title
TOC_PLANNED_GAP = 2         # between chapters not yet written in the contents
# Reading time of a chapter (`reading.py`, shown on the map of the book and in the contents). Characters per minute:
# IReST, 17 languages, mean 863 +- 234 cpm read aloud by 18-35-year-olds (Trauzettel-Klosinski & Dietz, IOVS 2012,
# PMID 22661485), rounded up; a technical text with prompts is not read faster.
READ_CPM = 900
MONITOR_MIN = 64             # the prompt monitor's width at least: a short prompt gets a small monitor
MONITOR_NARROW = 108         # up to this wide a monitor shares its row with a note; wider, it stands alone, centred
MONITOR_MAX = 172            # at most the whole text width; its screen is always 4:3
COVER_SCENE_HEIGHT = 130     # the illustration on the cover
OPENER_SCENE_HEIGHT = 135    # the illustration on a chapter opener
# The paginator's manners (read by theme/paginate.js through the custom properties):
NOTE_GAP = 6                 # air kept between a hanging margin note and whatever comes under it, a next note too
SPREAD_MAX = 5               # on a page that ends early, blocks move apart by at most this much each
SPREAD_FROM = 10             # ... and only if at least this much room is left over
EDGE_MIN = 5                 # no text comes closer than this to the edge of the sheet (a long word, a wide table)
# Justified running text (typography.css, theme/paginate.js), in em of the text:
WORD_SPACE = -0.04           # the space between words a little narrower than the font's own, so more words fit a line
TRACK_TARGET = 0.42          # a justified line whose mean word gap is wider than this has its letters spaced out ...
TRACK_MAX = 0.025            # ... by at most this much, too little to see, taking up part of the gaps
# `book audit` (audit.py, theme/audit.js): what it reports on the finished pages.
AUDIT_HOLE = 25              # mm left empty above a footer, on any page but a chapter's last (m takes 21 more than s)
AUDIT_GAP_MEAN = 0.55        # em: the mean gap between the words of a justified line ...
AUDIT_GAP_MAX = 0.9          # ... or its widest gap, above which the line is reported
AUDIT_HEADING_FOOT = 20      # mm: a heading closer than this to the foot of the text
AUDIT_SECTION_LINES = 2      # a section starting at the foot of a page shows at least this many lines of itself
AUDIT_SHORT_WORD = 4         # a paragraph's last line holding one word of fewer letters than this hangs
AUDIT_MONITOR_RATIO = 0.02   # a monitor's screen is 4:3 within this share
AUDIT_NOTE_AIR = 2           # mm at least between two notes stacked in one margin
AUDIT_BLANK = 25             # mm: a page whose content is shorter than this is near-blank
AUDIT_SLACK = 1              # mm text may stand outside the text block (an italic's overhang) before it is reported
AUDIT_PAGE_WEIGHT = 600      # KB of markup on one page; heavier pages ran the browser out of memory
AUDIT_FLOOR = 0.12           # share of a world's frame kept as floor under the feet (audit.frame_faults)
AUDIT_SHEET_SCALE = 0.4      # the contact sheets: pages at this scale,
AUDIT_SHEET_PAGES = 8        # this many to a sheet, each flagged region boxed in RED
LINE_WEIGHT = "2.2px"        # weight of the ink outline around boxes

# Illustrations are drawn in abstract units; one scene spans this many units across.
SCENE_WIDTH = 840
SCENE_UNITS_PER_PAGE_MM = SCENE_WIDTH / PAGE_WIDTH      # full-bleed footer scenes
SCENE_UNITS_PER_TEXT_MM = SCENE_WIDTH / TEXT_WIDTH      # inset scenes inside the text block

assert MARGIN_INNER + TEXT_WIDTH + MARGIN_OUTER == PAGE_WIDTH, "columns and margins must fill the page"


def palette() -> dict[str, str]:
    """Every color constant of this module, by name."""
    return {name: value for name, value in globals().items()
            if name.isupper() and isinstance(value, str) and value.startswith("#")}


def css_name(constant: str) -> str:
    """`PAPER_SHADE` -> `--paper-shade`."""
    return "--" + constant.lower().replace("_", "-")


def css_variables() -> str:
    """The `:root { ... }` block that hands every token to the stylesheet."""
    lines = [f"  {css_name(name)}: {value};" for name, value in palette().items()]
    lines += [f"  --{name}: {stack};" for name, stack in FONTS.items()]
    millimetres = {
        "page-w": PAGE_WIDTH, "page-h": PAGE_HEIGHT, "m-inner": MARGIN_INNER, "m-outer": MARGIN_OUTER,
        "col-main": COLUMN_MAIN, "col-gap": COLUMN_GAP, "col-side": COLUMN_SIDE, "col-center": COLUMN_CENTER,
        "col-full": COLUMN_FULL,
        "body-top": BODY_TOP, "body-gap": BODY_GAP, "gap": BLOCK_GAP, "gap-text": TEXT_GAP,
        "gap-tight": BLOCK_GAP_TIGHT, "gap-text-tight": TEXT_GAP_TIGHT, "after-heading-tight": AFTER_HEADING_TIGHT,
        "list-gap-tight": LIST_GAP_TIGHT,
        "accent-every": ACCENT_EVERY, "accent-from": ACCENT_FROM, "accent-w": ACCENT_WIDTH,
        "doodle-w": DOODLE_WIDTH, "accent-gap": ACCENT_GAP, "perch-h": PERCH_HEIGHT,
        "q-who-w": QUOTE_FIGURE, "q-pad": QUOTE_FIGURE + 8, "q-min": QUOTE_MIN,
        "monitor-max": MONITOR_MAX, "monitor-min": MONITOR_MIN, "monitor-narrow": MONITOR_NARROW,
        "step-pad": STEP_PAD, "toc-planned-gap": TOC_PLANNED_GAP, "after-heading": AFTER_HEADING,
        "section-min": SECTION_MIN, "foot-max": FOOT_MAX, "foot-panorama": FOOT_PANORAMA, "hang-max": HANG_MAX,
        "hole-max": HOLE_MAX,
        "numeral-w": NUMERAL_WIDTH, "numeral-gap": NUMERAL_GAP, "numeral-clear": NUMERAL_CLEAR,
        "cover-scene": COVER_SCENE_HEIGHT, "opener-scene": OPENER_SCENE_HEIGHT,
        "note-gap": NOTE_GAP, "spread-max": SPREAD_MAX, "spread-from": SPREAD_FROM,
        "edge-min": EDGE_MIN,
        **{f"foot-{size}": height for size, height in FOOT_HEIGHTS.items()},
    }
    lines += [f"  --{name}: {value}mm;" for name, value in millimetres.items()]
    lines.append(f"  --line: {LINE_WEIGHT};")
    lines.append(f"  --foot-large-max: {FOOT_LARGE_MAX};")
    lines += [f"  --{name}: {value}em;" for name, value in
              {"word-space": WORD_SPACE, "track-target": TRACK_TARGET, "track-max": TRACK_MAX}.items()]
    # `@page` cannot read custom properties, so the sheet size is written out here as well.
    page = f"@page {{ size: {PAGE_WIDTH}mm {PAGE_HEIGHT}mm; margin: 0; }}\n"
    chapters = "".join(f'[data-color="{name}"] {{ --accent: var({css_name("CHAPTER_" + name.upper())}); }}\n'
                       for name in ACCENTS)
    return ":root {\n" + "\n".join(lines) + "\n}\n" + chapters + page

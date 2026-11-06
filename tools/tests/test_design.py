"""Guards for the design system: one palette, one set of tokens, no strays."""
import re
from pathlib import Path

from bookkit import design
from bookkit.pages import stylesheet

ROOT = Path(__file__).resolve().parent.parent / "bookkit"
HEX = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")
COLOR_FUNCTION = re.compile(r"\brgba?\(|\bhsla?\(")


def sources(*patterns: str) -> list[Path]:
    return [path for pattern in patterns for path in ROOT.rglob(pattern) if path.name != "design.py"]


def test_no_color_literals_outside_the_design_module():
    offenders = []
    for path in sources("*.py", "*.css", "*.js"):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            code = re.sub(r"url\(#[^)]*\)", "", line)   # references to clip paths are not colors
            if HEX.search(code) or COLOR_FUNCTION.search(code):
                offenders.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()[:80]}")
    assert not offenders, "colors must come from bookkit/design.py:\n" + "\n".join(offenders)


def test_stylesheet_has_no_page_or_font_literals():
    css = "".join(path.read_text(encoding="utf-8") for path in (ROOT / "theme" / "css").glob("*.css"))
    assert "@page" not in css and "210mm" not in css and "297mm" not in css
    assert not re.search(r"font(-family)?:[^;]*\"", css), "font families come from the --f-* tokens"


def test_every_custom_property_used_is_defined():
    css = stylesheet()
    defined = set(re.findall(r"(--[\w-]+)\s*:", css))
    used = set(re.findall(r"var\((--[\w-]+)\)", css))   # with a fallback, a property may be set inline
    assert used <= defined, f"undefined custom properties: {sorted(used - defined)}"


def test_palette_is_exported_to_css_under_predictable_names():
    css = design.css_variables()
    assert f"--paper-shade: {design.PAPER_SHADE};" in css
    assert f"--foot-m: {design.FOOT_HEIGHTS['m']}mm;" in css
    assert css.count("@page") == 1
    for name, value in design.ACCENTS.items():
        assert f"--chapter-{name}: {value};" in css


def test_palette_has_no_duplicate_colors_and_valid_values():
    colors = design.palette()
    assert all(re.fullmatch(r"#[0-9a-f]{6}", value) for value in colors.values())
    seen: dict[str, str] = {}
    for name, value in colors.items():
        assert value not in seen, f"{name} repeats {seen[value]}: reuse the existing token"
        seen[value] = name


def test_color_helpers():
    assert design.lighten("#000000", 1) == "#ffffff"
    assert design.lighten("#336699", 0) == "#336699"
    assert design.darken("#ffffff", 0.5) < "#ffffff"
    assert design.css_name("PAPER_SHADE") == "--paper-shade"


def test_geometry_is_consistent():
    assert design.MARGIN_INNER + design.TEXT_WIDTH + design.MARGIN_OUTER == design.PAGE_WIDTH
    heights = list(design.FOOT_HEIGHTS.values())
    assert heights == sorted(heights), "footer sizes must grow from s to l"
    assert design.COLUMN_CENTER <= design.TEXT_WIDTH


def test_every_style_sheet_is_loaded_exactly_once():
    from bookkit.pages import STYLE_SHEETS

    on_disk = sorted(path.name for path in (ROOT / "theme" / "css").glob("*.css"))
    assert sorted(STYLE_SHEETS) == on_disk


def test_every_palette_color_is_used_somewhere():
    """An unused token is dead weight and an invitation to pick a near-duplicate next time."""
    code = "".join(path.read_text(encoding="utf-8") for path in sources("*.py", "*.css", "*.js"))
    chapters = set(design.ACCENTS.values())               # a chapter's colour is used through its `color:` line
    unused = [name for name, value in design.palette().items() if value not in chapters
              and not re.search(rf"\b(?:P|design)\.{name}\b", code) and f"var({design.css_name(name)})" not in code]
    assert not unused, f"unused palette tokens: {unused}"


def test_no_cyrillic_in_code():
    """Code is English only; Russian lives in the locale and in the fixtures."""
    import re
    from pathlib import Path
    package = Path(__file__).resolve().parent.parent / "bookkit"
    offenders = [f"{path.relative_to(package)}:{number}"
                 for path in [*package.rglob("*.py"), *package.rglob("*.js"), *package.rglob("*.css")]
                 for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
                 if re.search("[А-Яа-яЁё]", line)]
    assert not offenders, f"Cyrillic in code: {offenders}"

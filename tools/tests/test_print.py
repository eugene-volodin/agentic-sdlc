"""What Chrome cannot print as vectors stays out of the book: Apple's PDF viewers draw its raster fallbacks torn."""
import re

import pytest

from bookkit.art.ink import Canvas
from bookkit.config import THEME
from bookkit.render import _raster_warnings


def _layers(svg: str) -> list[tuple[float, float, float]]:
    return [(float(y), float(h), float(a)) for y, h, a in
            re.findall(r'y="([-\d.]+)" width="[\d.]+" height="([\d.]+)" fill="#\w+" fill-opacity="([\d.]+)"', svg)]


@pytest.mark.parametrize("stops", [[(0, "#ffffff", 0), (1, "#ffffff", 0.9)], [(0, "#ffffff", 1), (1, "#ffffff", 0)]])
def test_a_fade_stacks_flat_opacity_up_to_the_stops(stops):
    svg = Canvas().fade(0, 0, 100, 100, stops, steps=10).render()
    assert "Gradient" not in svg and "stop-opacity" not in svg
    layers = _layers(svg)
    assert len(layers) >= 9
    for probe in (5, 45, 95):                 # the opacity laid over a point is what the stops ask for there
        clear = 1.0
        for y, h, a in layers:
            if y <= probe <= y + h:
                clear *= 1 - a
        want = stops[0][2] + (stops[1][2] - stops[0][2]) * (int(probe / 10) + 0.5) / 10
        assert abs((1 - clear) - want) < 1e-2, probe


def test_a_fade_must_run_one_way():
    with pytest.raises(ValueError):
        Canvas().fade(0, 0, 10, 10, [(0, "#ffffff", 0), (0.5, "#ffffff", 1), (1, "#ffffff", 0)])


def test_the_theme_has_no_gradient_fading_to_transparent():
    for css in (THEME / "css").glob("*.css"):
        for rule in re.findall(r"[^{}]*\{[^}]*gradient[^}]*\}", css.read_text(encoding="utf-8")):
            assert "transparent" not in rule, (css.name, rule.strip()[:80])


def _pdf(*objects: bytes) -> bytes:
    return b"%PDF-1.4\n" + b"".join(b"%d 0 obj\n<<%s>>\nstream\nxx\nendstream\nendobj\n" % (i + 1, body)
                                    for i, body in enumerate(objects))


def test_a_raster_fallback_in_the_pdf_is_reported(tmp_path):
    pdf = tmp_path / "book.pdf"
    photo = b"/Type /XObject /Subtype /Image /Width 640 /Filter /DCTDecode"
    pdf.write_bytes(_pdf(photo))
    assert _raster_warnings(pdf, pictures=1) == []
    fallback = b"/Type /XObject /Subtype /Image /Width 58 /SMask 3 0 R"
    alpha = b"/Type /XObject /Subtype /Image /Width 58 /ColorSpace /DeviceGray"
    pdf.write_bytes(_pdf(photo, fallback, alpha))
    warnings = _raster_warnings(pdf, pictures=1)
    assert len(warnings) == 1 and "1 drawing(s)" in warnings[0]

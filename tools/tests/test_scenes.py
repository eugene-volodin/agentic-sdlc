"""Scene composition: nothing in a picture overlaps anything else."""
from bookkit.art import scenes
from bookkit.art.scenes import WIDTH, _outdoor_props, _Scene


def spans_overlap(spans):
    ordered = sorted((x - half, x + half) for x, half in spans)
    return any(a[1] > b[0] for a, b in zip(ordered, ordered[1:], strict=False))


def test_scattered_props_never_overlap():
    for seed in range(60):
        for h in (136, 260, 520):
            s = _Scene(h, seed, "meadow", None, True)
            _outdoor_props(s)
            assert not spans_overlap(s.taken), (seed, h)


def test_nearest_free_clears_every_span():
    s = _Scene(200, 0, "room", None, True)
    spans = [(100, 300), (320, 500)]
    x = s.nearest_free(310, 40, spans, 0, WIDTH, 10)
    assert x is not None and all(x + 50 <= left or x - 50 >= right for left, right in spans)
    assert s.nearest_free(400, 500, spans, 0, WIDTH) is None


def test_story_prop_and_cast_do_not_share_ground():
    # The crate claims its place before the flowers and mushrooms are scattered around it.
    captured = {}
    original = scenes._outdoor_props

    def spy(s):
        original(s)
        captured["taken"] = list(s.taken)

    scenes._outdoor_props = spy
    try:
        for seed in range(3, 120, 12):   # the MCP crate story
            scenes.scene(h=180, seed=seed)
            taken = captured["taken"]
            props_only = taken[2:]       # the two cast members stand on their own slots
            assert not spans_overlap(props_only), seed
    finally:
        scenes._outdoor_props = original

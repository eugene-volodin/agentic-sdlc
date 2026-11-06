"""Footer episodes: every one draws without overlaps, has its words, and the choice is fair and reproducible."""
import pytest
import yaml

from bookkit.art.footers import EPISODES, LOOKS, draw_footer, footer_conflicts, plan
from bookkit.config import LOCALES

VOCABULARY = yaml.safe_load((LOCALES / "ru.yml").read_text(encoding="utf-8"))["footers"]


@pytest.mark.parametrize("name", sorted(EPISODES))
def test_every_episode_draws_without_overlaps(name):
    words = (VOCABULARY.get(name) or {}).get("words")
    for i, look in enumerate(LOOKS):
        for h in (136, 220, 320, 560):
            for clear in ("left", "right"):
                svg, strip = draw_footer(name, h, i, clear, look, words)
                assert svg.startswith("<svg") and f'viewBox="0 0 840 {h}"' in svg
                assert footer_conflicts(strip) == [], (name, h, look, clear)
                assert "<mask" not in svg and "stop-opacity" not in svg, name   # they print as rasters


@pytest.mark.parametrize("name", sorted(EPISODES))
def test_every_episode_has_topic_words(name):
    assert len((VOCABULARY.get(name) or {}).get("topics") or []) >= 3, name


def _requests(chapter, pages, text="ничего особенного"):
    return [{"page": i, "chapter": chapter, "text": text, "heads": "", "mm": 34, "clear": "left"} for i in range(pages)]


def test_no_episode_repeats_within_a_chapter():
    chosen = plan(_requests("1", min(30, len(EPISODES))), VOCABULARY)
    names = [name for name, _, _ in chosen]
    assert len(names) == len(set(names))


def test_a_page_gets_the_episode_its_text_is_about():
    name = sorted(EPISODES)[0]
    topic = VOCABULARY[name]["topics"][0]
    chosen = plan([{"chapter": "2", "text": f"здесь про {topic} и снова {topic}", "heads": ""}], VOCABULARY)
    assert chosen[0][0] == name


def test_a_chapter_is_drawn_alike_in_the_full_build_and_alone():
    one = _requests("3", 6, "токен модель тест")
    both = _requests("2", 5) + one
    assert plan(one, VOCABULARY) == plan(both, VOCABULARY)[5:]


def test_lettering_shrunk_on_the_page_is_set_flat():
    from bookkit.art.ink import lettering, settle_lettering
    sign = lettering(0, 0, "Sign", 20, "#ff0000")
    assert settle_lettering(f'<g transform="scale(1)">{sign}</g>').count("<text") == 2     # rim and extrusion
    shrunk = settle_lettering(f'<g transform="translate(5,5) scale(0.5)">{sign}</g>')
    assert shrunk.count("<text") == 1 and "stroke" not in shrunk and 'fill="#ff0000"' in shrunk

"""Components about real people: the author's portrait and ways to reach them."""
from __future__ import annotations

import re
from html import escape

import segno

from .. import design
from ..art import props
from ..art.doodles import doodle
from ..markup import BuildError
from .base import TEXT, Call, Row, block
from .context import Context
from .graphics import TAIL

# kind of contact -> the doodle drawn on its card (see `art.doodles`)
CONTACT_ICONS = {"telegram": "plane", "blog": "megaphone", "mail": "envelope", "web": "globe"}


@block("about", titled=True, wide="default", options={"photo": TEXT},
       example="::: about Ada Lovelace\nI wrote the first program, so I get to write this book.\n:::")
def about(ctx: Context, call: Call) -> Row:
    """A person introduced: a photograph on the left, their name and a few words in a bubble on the right.

    The title is the name. `photo` is an image path relative to the chapter file; until one is
    given, a neutral placeholder is drawn in its place.
    """
    if not call.title:
        raise BuildError("'about' needs the person's name as its title, e.g. '::: about Ada Lovelace'")
    if call.get("photo"):
        source = ctx.markdown.resolve_image(call.get("photo"))
        picture = f'<img src="{escape(source, quote=True)}" alt="{escape(call.title, quote=True)}">'
    else:
        picture = props.portrait_placeholder()
    return Row(f'<div class="about"><div class="about-photo">{picture}</div><div class="about-text">'
               f'<div class="about-name">{ctx.inline(call.title)}</div>'
               f'<div class="bubble">{ctx.framed(call.body)}{TAIL}</div></div></div>')


@block("contacts", wide="default",
       example="::: contacts\ntelegram | My channel | @example | https://t.me/example\n"
               "mail | Write to me | me@example.com | mailto:me@example.com\n:::")
def contacts(ctx: Context, call: Call) -> Row:
    """Cards with ways to reach someone, one per line: `kind | label | text | link`.

    Kinds: telegram, blog, mail, web. The link is optional; with it the whole card is clickable.
    """
    cards = []
    for line in filter(None, (raw.strip() for raw in call.body.split("\n"))):
        parts = [part.strip() for part in line.split("|")]
        if not 3 <= len(parts) <= 4 or parts[0] not in CONTACT_ICONS:
            raise BuildError(f"contacts: each line is 'kind | label | text | link' with kind one of "
                             f"{', '.join(CONTACT_ICONS)}; got {line!r}")
        kind, label, text = parts[:3]
        link = parts[3] if len(parts) > 3 else ""
        if link and not re.match(r"(https?://|mailto:|tg://)\S+$", link):
            raise BuildError(f"contacts: the link must start with https://, mailto: or tg://; got {link!r}")
        inner = (f'{doodle(CONTACT_ICONS[kind])}<b>{ctx.inline(label)}</b>'
                 f'<span>{escape(text)}</span>')
        cards.append(f'<a class="contact" href="{escape(link, quote=True)}">{inner}</a>' if link
                     else f'<div class="contact">{inner}</div>')
    if not cards:
        raise BuildError("'contacts' needs at least one line")
    return Row(f'<div class="contacts" style="--n:{min(len(cards), 3)}">{"".join(cards)}</div>')


def _qr(link: str) -> str:
    """A QR code of the link as inline SVG, ink on transparent, sized by CSS."""
    code = segno.make(link, error="m")
    return code.svg_inline(dark=design.INK, light=None, scale=1, border=0, omitsize=True)


@block("download", wide="default",
       example="::: download\nPoint the camera at the code or tap the button.\n:::")
def download(ctx: Context, call: Call) -> Row:
    """Where to get the newest version: a QR code and a button for the latest release's PDF, and the version
    this copy is. Needs `repo` and `version` in book.yml; the body is a line of text under the button."""
    config = ctx.config
    if not config.repo or not config.version:
        raise BuildError("'download' needs 'repo' and 'version' in book.yml")
    link = escape(config.download, quote=True)
    return Row(f'<div class="download"><a class="download-qr" href="{link}">{_qr(config.download)}</a>'
               f'<div class="download-text"><div class="download-version">{ctx.label("version")} '
               f'<b>{escape(config.version)}</b></div>'
               f'<a class="download-button" href="{link}">{doodle("floppy")}<span>{ctx.label("download")}</span></a>'
               f'<div class="download-note">{ctx.framed(call.body)}</div></div></div>')


@block("github", wide="default",
       example="::: github\nPull requests are welcome.\n:::")
def github(ctx: Context, call: Call) -> Row:
    """The repository of the text: its address, and two things to do there - send a pull request, star it.
    The body is the text beside the star."""
    repo = ctx.config.repo
    if not repo:
        raise BuildError("'github' needs 'repo' in book.yml")
    address = repo.removeprefix("https://")
    return Row(f'<a class="repo-card" href="{escape(repo, quote=True)}"><div class="repo-star">{doodle("star")}</div>'
               f'<div class="repo-text"><span class="repo-address">{escape(address)}</span>'
               f'{ctx.framed(call.body)}</div></a>')

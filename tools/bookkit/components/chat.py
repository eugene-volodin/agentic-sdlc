"""The `chat` fence: a screenshot of a channel in a work messenger - messages, their thread, the apps that answer.

It is a generic messenger, not any real product: a light window with the channel's name in its bar, round avatars with
initials for people, square ones for apps. It never splits between pages (no `data-split`): a screenshot moves on whole.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from html import escape

from ..markup import BuildError
from .base import TEXT, Call, Row, fence
from .context import Context

# `Name · 10:12: text`, `Name [app] · 10:14: text`; a leading `> ` puts the message in the thread of the one above.
_MESSAGE = re.compile(r"^(?P<reply>>\s+)?(?P<name>[^\s·\[\]>][^·\[\]]*?)\s*(?P<app>\[app\])?\s*·\s*"
                      r"(?P<time>\d{1,2}):(?P<minute>\d{2}):\s+(?P<text>\S.*)$")
# `  [img: caption]` indented under a message: a screenshot attached to it.
_ATTACHMENT = re.compile(r"^(?:\s*>)?\s+\[img:\s*(?P<caption>[^\]]*?)\s*\]\s*$")
# What looks live in a message: a mention, a ticket id like ENG-412, a pull request like #1287.
_LIVE = re.compile(r"(<[^>]+>)|(?<![\w@])(@[\w.-]*\w)|(?<![\w-])([A-Z][A-Z0-9]{1,9}-\d+|#\d+)\b")
# Avatar colors: a name always gets the same one (by its letters, not by Python's salted hash).
PEOPLE_COLORS = ("teal", "pink", "blue", "violet", "green", "plum", "orange")
APP_COLORS = ("charcoal", "indigo", "pine", "orange-dark")
APP_TAG = "APP"
SYNTAX = "write a message as 'Name · 10:12: text', a reply in its thread as '> Name · 10:14: text', an app as " \
         "'Name [app] · 10:14: text', a screenshot under a message as '  [img: caption]'"


@dataclass
class Message:
    name: str
    app: bool
    time: str
    text: str
    files: list[str] = field(default_factory=list)
    replies: list[Message] = field(default_factory=list)


def parse(body: str) -> list[Message]:
    """The messages of a chat, each with its thread; a line that is none of the three forms is an author error."""
    messages: list[Message] = []
    last: Message | None = None
    for number, line in enumerate(body.split("\n"), 1):
        if not line.strip():
            continue
        where = f"chat line {number}"
        attachment = _ATTACHMENT.match(line)
        if attachment:
            if last is None:
                raise BuildError(f"{where}: a screenshot must stand under a message: {line.strip()!r}")
            if not attachment["caption"]:
                raise BuildError(f"{where}: the screenshot needs a caption, e.g. '  [img: the quiz page]'")
            last.files.append(attachment["caption"])
            continue
        match = _MESSAGE.match(line)
        if not match:
            raise BuildError(f"{where}: cannot read {line.strip()[:50]!r}; {SYNTAX}")
        hour, minute = int(match["time"]), int(match["minute"])
        if hour > 23 or minute > 59:
            raise BuildError(f"{where}: {match['time']}:{match['minute']} is not a time of day")
        last = Message(match["name"].strip(), bool(match["app"]), f"{hour}:{minute:02d}", match["text"].strip())
        if match["reply"]:
            if not messages:
                raise BuildError(f"{where}: a reply ('> ') needs a message above it to answer")
            messages[-1].replies.append(last)
        else:
            messages.append(last)
    if not messages:
        raise BuildError(f"a chat needs at least one message; {SYNTAX}")
    return messages


def color(name: str, app: bool) -> str:
    """The avatar's color token: stable for a name across chats, chapters and builds."""
    choices = APP_COLORS if app else PEOPLE_COLORS
    return choices[sum(ord(ch) * (i + 1) for i, ch in enumerate(name)) % len(choices)]


def initials(name: str, app: bool) -> str:
    words = [word for word in re.split(r"[\s._-]+", name) if word[:1].isalnum()]
    letters = [word[0] for word in words[: 1 if app else 2]] or [name[0]]
    return "".join(letters).upper()


def _live(markup: str) -> str:
    """Tint mentions and make ids look like links, in rendered markup: tags are left as they are."""
    def mark(match: re.Match) -> str:
        if match[1]:
            return match[1]
        if match[2]:
            return f'<span class="chat-mention">{match[2]}</span>'
        return f'<span class="chat-link">{match[3]}</span>'
    return _LIVE.sub(mark, markup)


def _file(ctx: Context, caption: str) -> str:
    """A screenshot attached to a message: a small browser page with a heading, two cards and a button."""
    page = ('<div class="chat-shot-page"><i class="chat-shot-bar"><b></b><b></b><b></b><s></s></i>'
            '<i class="chat-shot-head"></i><i class="chat-shot-line"></i>'
            '<i class="chat-shot-cards"><b></b><b></b><b></b></i><i class="chat-shot-button"></i></div>')
    return f'<figure class="chat-shot">{page}<figcaption>{ctx.inline(caption)}</figcaption></figure>'


def _message(ctx: Context, message: Message) -> str:
    kind = " app" if message.app else ""
    tag = f'<span class="chat-tag">{APP_TAG}</span>' if message.app else ""
    files = (f'<div class="chat-files">{"".join(_file(ctx, caption) for caption in message.files)}</div>'
             if message.files else "")
    return (f'<div class="chat-msg{kind}" style="--who: var(--{color(message.name, message.app)})">'
            f'<div class="chat-avatar">{escape(initials(message.name, message.app))}</div>'
            f'<div class="chat-body"><div class="chat-head"><b>{escape(message.name)}</b>{tag}'
            f'<time>{message.time}</time></div><div class="chat-text">{_live(ctx.inline(message.text))}</div>'
            f"{files}</div></div>")


@fence("chat", options={"title": TEXT},
       example='```chat title="# requests"\nOleg Smirnov · 10:12: Can you rename the button on the quiz page?\n'
               "> Tema P · 10:14: @Linear file a ticket\n> Linear [app] · 10:14: Filed ENG-412\n```")
def chat(ctx: Context, call: Call) -> Row:
    """A screenshot of a messenger channel: `Name · 10:12: text`, `> ` a reply in its thread, `[app]` an app.

    `@Name` is a mention, `ENG-412` and `#1287` look like links; `  [img: caption]` under a message attaches a
    screenshot. The title is the channel's name. The block never splits between pages.
    """
    feed = []
    for message in parse(call.body):
        feed.append(_message(ctx, message))
        if message.replies:
            feed.append(f'<div class="chat-thread">{"".join(_message(ctx, reply) for reply in message.replies)}</div>')
    title = call.get("title") or call.title
    bar = ""
    if title:
        channel = re.match(r"^\s*([#@])\s*(.*)$", title)
        mark, name = (channel[1], channel[2]) if channel else ("", title)
        bar = (f'<div class="chat-bar"><span class="chat-channel">'
               f'{f"<i>{escape(mark)}</i>" if mark else ""}{escape(name)}</span></div>')
    return Row(f'<div class="chat">{bar}<div class="chat-feed">{"".join(feed)}</div></div>')

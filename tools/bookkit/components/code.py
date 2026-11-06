"""Fences: code, terminal sessions, directory trees, files and - the heart of the book - prompts.

Every fence wraps its lines in `<span class="ln">` inside an element marked `data-split`, which
is what lets the paginator break a long listing between lines.
"""
from __future__ import annotations

import re
from html import escape

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from .base import MOOD, POSE, TEXT, Call, Row, fence
from .context import Context
from .graphics import COMPUTER_BASE, ICON_FILE, ICON_FOLDER, SHEET_FOLD

# Things a reader must replace in a prompt: {{name}}, <choice> and [UPPERCASE WORDS].
_PLACEHOLDER = re.compile(r"\{\{[^}]+\}\}|&lt;[^&\s][^&]*?&gt;|\[[^\]\n]{3,}\]")


def lines(markup_lines: list[str]) -> str:
    """Wrap each line so the paginator can split the listing between lines."""
    return "".join(f'<span class="ln">{line}</span>' for line in markup_lines)


def highlighted(code: str, language: str) -> str:
    """Syntax-highlight code; unknown languages are shown plain."""
    try:
        lexer = get_lexer_by_name(language or "text")
    except ClassNotFound:
        return escape(code)
    return highlight(code, lexer, HtmlFormatter(nowrap=True))


def _title(call: Call) -> str:
    return call.get("title") or call.title


def _mark_placeholder(match: re.Match) -> str:
    text = match.group(0)
    if text.startswith("["):  # only all-caps bracketed text counts, so Markdown links stay plain
        inner = text[1:-1]
        if inner != inner.upper() or not any(ch.isalpha() for ch in inner):
            return text
    return f'<span class="pr-var">{text}</span>'


@fence("code", options={"title": TEXT}, example='```python title="hooks/check.py"\nimport sys\n```')
def code(ctx: Context, call: Call) -> Row:
    """Source code with syntax highlighting; any language word selects it. The title is a file name."""
    title = _title(call)
    bar = (f'<div class="code-title">{escape(title)}<span>{escape(call.language)}</span></div>'
           if title else "")
    body = lines(highlighted(call.body, call.language).rstrip("\n").split("\n"))
    return Row(f'<div class="code">{bar}<pre data-split>{body}</pre></div>')


@fence("terminal", "console", options={"title": TEXT},
       example="```terminal\n$ claude\n# a comment\n> /review the last commit\n```")
def terminal(ctx: Context, call: Call) -> Row:
    """A terminal window: `$ ` starts a shell command, `> ` an agent prompt, `#` a comment."""
    out = []
    for line in call.body.rstrip("\n").split("\n"):
        if line.startswith("$ "):
            out.append(f'<span class="t-ps">$</span> <span class="t-cmd">{escape(line[2:])}</span>')
        elif line.startswith("> "):
            rest = re.sub(r"^(/[\w:-]+)", r'<span class="t-slash">\1</span>', escape(line[2:]))
            out.append(f'<span class="t-ps">&gt;</span> <span class="t-cmd">{rest}</span>')
        elif line.lstrip().startswith("#"):
            out.append(f'<span class="t-rem">{escape(line)}</span>')
        else:
            out.append(escape(line))
    title = escape(_title(call))      # no default caption: the three dots already say "terminal"
    return Row(f'<div class="terminal"><div class="terminal-bar"><i></i><i></i><i></i>{title}</div>'
               f'<pre data-split>{lines(out)}</pre></div>')


@fence("tree", "files", options={"title": TEXT},
       example='```tree title="Project"\nmy-project/\n├── AGENTS.md   # the rules\n└── NEWS.md -> docs/NEWS.md\n```')
def tree(ctx: Context, call: Call) -> Row:
    """A directory tree: `name/` is a folder, `# text` a handwritten remark, `a -> b` a symlink."""
    out = []
    for line in call.body.rstrip("\n").split("\n"):
        guide, rest = re.match(r"^([\s│├└─|`+\-]*)(.*)$", line).groups()
        remark = ""
        comment = re.search(r"\s+(?:#|←|//)\s*(.*)$", rest)
        if comment:
            remark, rest = comment.group(1), rest[:comment.start()]
        if not rest:
            out.append(f'<span class="t-guide">{escape(guide)}</span>')
            continue
        is_folder = rest.endswith("/")
        if re.search(r"\s(->|→)\s", rest):
            link, target = re.split(r"\s+(?:->|→)\s+", rest, maxsplit=1)
            name = f'{escape(link)} <span class="t-guide">→</span> <i>{escape(target)}</i>'
        else:
            name = f'<span class="t-dir">{escape(rest)}</span>' if is_folder else escape(rest)
        arrow = '<span class="t-arrow">←</span>'
        remark_markup = f'<span class="t-note">{arrow} {ctx.inline(remark)}</span>' if remark else ""
        out.append(f'<span class="t-guide">{escape(guide)}</span>{ICON_FOLDER if is_folder else ICON_FILE}'
                   f"{name}{remark_markup}")
    title = _title(call)
    tab = f'<div class="tree-title">{escape(title)}</div>' if title else ""
    return Row(f'<div class="tree{" titled" if title else ""}">{tab}<pre data-split>{lines(out)}</pre></div>')


@fence("file", options={"title": TEXT},
       example='```file title=".claude/skills/review/SKILL.md"\n---\nname: review\n---\n# How to review\n```')
def file(ctx: Context, call: Call) -> Row:
    """The contents of a file shown as a sheet of paper with a folded corner; a line wrapped in `**` is set bold."""
    out = []
    for line in call.body.rstrip("\n").split("\n"):
        markup = escape(line)
        bold = re.fullmatch(r"(\s*)\*\*(.+)\*\*\s*", line)   # a whole line in ** ** is the one to look at
        if bold:
            markup = f'{escape(bold[1])}<strong class="f-mark">{escape(bold[2])}</strong>'
        elif re.match(r"^\s*#{1,4}\s", line):
            markup = f'<span class="f-head">{markup}</span>'
        elif line.strip() == "---" or re.match(r"^[\w-]+:\s", line):
            markup = f'<span class="f-meta">{markup}</span>'
        out.append(markup)
    title = escape(_title(call)) or ctx.label("file")
    return Row(f'<div class="sheet"><div class="sheet-paper"><div class="sheet-name">{ICON_FILE}{title}'
               f'</div><pre data-split>{lines(out)}</pre>{SHEET_FOLD}</div></div>')


@fence("prompt", who="cat", options={"title": TEXT, "note": TEXT, "pose": POSE, "mood": MOOD},
       example='```prompt who=agent title="First skill" note="Fill in your stack!"\nStudy the repository...\n'
               "Stack: {{language}}\n```")
def prompt(ctx: Context, call: Call) -> Row:
    """A prompt for the reader to copy, shown on the screen of the old computer.

    A character in the margin gives a hint (`note`), unless the author already placed a margin
    note before the fence; `note="-"` leaves the prompt without a hint. Headings, list markers and
    placeholders are tinted. The raw text is
    also collected for export (`book prompts`), because copying from a PDF loses indentation.
    """
    out = []
    for line in call.body.rstrip("\n").split("\n"):
        markup = _PLACEHOLDER.sub(_mark_placeholder, escape(line))
        if re.match(r"^\s*#{1,4}\s", line):
            markup = f'<span class="pr-head">{markup}</span>'
        else:
            markup = re.sub(r"^(\s*)(-|\*|\d+[.)])(\s)", r'\1<span class="pr-bullet">\2</span>\3', markup)
        out.append(markup)
    title = _title(call)
    ctx.add_prompt(title, call.body.rstrip("\n") + "\n")
    heading = ctx.inline(title) if title else ""
    label = f'<div class="prompt-label head-only"><b>{ctx.label("prompt")}</b>{heading}</div>'
    main = (f'<div class="prompt">{label}<div class="crt"><pre class="screen">{lines(out)}</pre>'
            f'<div class="crt-chin head-only"><span>{ctx.label("computer_brand")}</span><i class="led"></i><i></i>'
            f"<i></i></div></div>{COMPUTER_BASE}</div>")
    side = ""
    if call.get("note") == "-":  # no hint at all
        return Row(main, side)
    if not ctx.pending_margin:  # a note written by the author replaces the default hint
        hint = ctx.inline(call.get("note")) if call.get("note") else ctx.label("prompt_hint")
        side = ctx.margin_talk(call.who, hint, call.get("pose"), call.get("mood", "talk"))
    return Row(main, side)

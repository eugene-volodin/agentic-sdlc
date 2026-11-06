"""The library of visual components. See `base.py` for how it works and how to extend it.

Importing this package registers every component; the modules group them by family:

    speech     say, dialog, note, quote
    callouts   tip, warn, idea, try, define, stat, recap, dodont, compare
    lists      checklist, steps, cast
    layout     scene, wide, pagebreak
    people     about, contacts, download, github
    code       fences: code, terminal, tree, file, prompt
    chat       fence: a messenger channel with its thread
"""
from . import callouts, chat, code, layout, lists, people, speech  # noqa: F401  (imported to register the components)
from .base import BLOCKS, FENCES, Call, Row, reference, render_block, render_fence
from .context import Context, Prompt

__all__ = ["BLOCKS", "FENCES", "Call", "Context", "Prompt", "Row", "reference", "render_block", "render_fence"]

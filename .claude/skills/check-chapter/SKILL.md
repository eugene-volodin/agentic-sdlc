---
name: check-chapter
description: Check one chapter the way CI checks the whole book - build it, audit every page and review its pictures. Use before opening a pull request that changes a chapter.
---

# Check a chapter

1. From `tools/`, audit the chapter as CI does: `uv run book audit --only <chapter folder> --base origin/main
   --baseline audit-baseline.json --sheets /tmp/bookkit-sheets`. The sheets show only the flagged pages.
2. Take a picture of every page of the chapter: `uv run book build --only <chapter folder> --shots all --no-pdf`
   (PNG files in `<temp>/bookkit/book/pages/`).
3. For every finding, open its contact sheet and the page PNG. Fix layout findings by moving blocks; report findings
   that need a change of wording instead of rewording the author's text yourself.
4. Check the text against `AGENTS.md`: «ты», no emoji, facts with links to official documentation, prompts in
   ` ```prompt ` fences.
5. If `tools/` changed, run `uv run pytest -q` and `uvx ruff check bookkit tests`.
6. Report what the audit found, what you fixed and what needs the maintainer.

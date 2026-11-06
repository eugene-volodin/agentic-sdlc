---
name: release-version
description: Raise the book's version for a change before merging it. Use when a pull request changes book/ or the PDF, or when CI reports that the version was not raised.
---

# Raise the version

1. Read `version:` in `book/book.yml`. It is `MAJOR.MINOR-MM.YYYY`.
2. Raise MINOR by one and set the current month and year, e.g. `0.117-11.2026` → `0.118-11.2026`
   (or `0.118-12.2026` in December). Never change MAJOR
   unless the author asks for it.
3. Make sure no release with that version exists yet: `gh release view v<version>` must fail.
4. Build with `uv run book build --strict` from `tools/`: the version is printed on the cover and on the «Свежая
   версия» page.
5. Commit the version with the change. After the merge, `release.yml` publishes `v<version>` with
   `agentic-sdlc.pdf`; nothing else is needed.

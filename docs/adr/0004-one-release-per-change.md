# 0004. Every change to the book is a release, and one link always gives the newest

Status: accepted

## Context

The book is printed into a PDF that people forward to each other, so old copies keep circulating. The «Свежая
версия» page carries a QR code and a button, and they must always lead to the newest version.

## Decision

- The version lives in `book/book.yml` as `MAJOR.MINOR-MM.YYYY`. Every change to the book raises MINOR and sets the
  current month and year; MAJOR changes only by the author's decision.
- `check.yml` fails a pull request that changes `book/` without raising the version (`book audit --base`), and the
  ruleset of `main` requires a branch to be up to date before merging.
- `release.yml` runs on every push to `main` that touches `book/` or `tools/`: unless that version is already
  released, it builds the book and publishes the GitHub release `v<version>` with `agentic-sdlc.pdf`. The link `…/releases/latest/download/agentic-sdlc.pdf` is printed in the book and always
  resolves to the newest release.

## Consequences

- No PDF is committed to the repository; `dist/` is ignored.
- Two pull requests that raise the version to the same number merge without a conflict. Because a branch must be up
  to date with `main`, the second one re-runs the check, fails it and raises the version again.
- A change only to `tools/` that alters the PDF is released with the next version bump.

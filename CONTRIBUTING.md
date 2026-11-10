# Contributing

Thank you for helping to make the book better!

You only write the text. The pictures, the footers and the layout of the pages are the maintainer's: you never need to
touch `tools/` or the drawings to get a change in.

1. Fork the repository and create a branch.
2. Edit the text in `book/`. Each chapter is a folder and each section is its own `.md` file. The markup blocks
   (the characters' notes, prompts, tables) are described in `docs/design-system.md`; `uv run book components` prints
   their reference.
3. Raise the version in `book/book.yml`: `MAJOR.MINOR-MM.YYYY` with MINOR + 1 and the current month and year.
   The check compares it with `main`: if `main` moved on meanwhile, raise it again above the one there.
4. Optionally, build the book and look at the pages you changed:
   ```bash
   cd tools && uv sync && uv run book build --strict --shots all
   ```
   Your machine may break a few lines differently from CI; `tools/container.sh` (Docker) runs exactly what CI runs.
5. Open a pull request. CI builds the book, checks every page and attaches the PDF, the report and contact sheets of
   the flagged pages. On a pull request from a fork it fails only on errors (the version, broken markup, a broken
   build); layout warnings - a hole above a footer, a gap between words - are listed in the report and fixed by the
   maintainer after the merge.

Please:

- write the way the book is written: in Russian, in the author's first person, addressing the reader as «ты», no emoji;
- back every fact about models and tools with a link to the official documentation;
- run every prompt and command you add to the book before submitting it.

For a large change, open an issue first so we can discuss it.

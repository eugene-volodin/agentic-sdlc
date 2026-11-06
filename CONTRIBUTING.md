# Contributing

Thank you for helping to make the book better!

1. Fork the repository and create a branch.
2. Edit the text in `book/`. Each chapter is a folder and each section is its own `.md` file. The markup blocks
   (the characters' notes, prompts, tables) are described in `docs/design-system.md`; `uv run book components` prints
   their reference.
3. Raise the version in `book/book.yml`: `MAJOR.MINOR-MM.YYYY` with MINOR + 1 and the current month and year.
   The check fails without a new version: every change to the book becomes a release of its own.
4. Build the book and look at the pages you changed:
   ```bash
   cd tools && uv sync && uv run book build --strict --shots all
   ```
5. Open a pull request. CI builds the book, checks every page and attaches the PDF and contact sheets of the flagged
   pages. A pull request can be merged only when the check is green.

Please:

- write the way the book is written: in Russian, in the author's first person, addressing the reader as «ты», no emoji;
- back every fact about models and tools with a link to the official documentation;
- run every prompt and command you add to the book before submitting it.

For a large change, open an issue first so we can discuss it.

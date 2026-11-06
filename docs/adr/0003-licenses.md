# 0003. Different licenses for the text, the examples, the tool and the fonts

Status: accepted

## Context

The book is free to read and share, and the author wants credit for it and no one selling it. At the same time the
book teaches readers to copy its prompts and examples into their own repositories, including at work, and the build
tool may be useful for other non-commercial books.

## Decision

- **Text and pictures:** CC BY-NC 4.0 - share and adapt with credit, no commercial use.
- **Prompts, commands and code examples printed in the book:** CC0 1.0 - no conditions, so using them at work is
  never in question.
- **The build and check tool:** PolyForm Noncommercial 1.0.0 - a software license with the same non-commercial
  spirit as the text; Creative Commons licenses are not meant for code.
- **Fonts:** each keeps its own SIL Open Font License 1.1.

`LICENSE` maps every part of the repository to its license; the full texts are in `licenses/`.

## Consequences

- A paid course or a commercial book built on this material needs the author's permission.
- The tool is source-available rather than open source in the OSI sense.

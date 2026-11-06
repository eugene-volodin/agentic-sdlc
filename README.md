<p align="center">
  <img src="docs/images/cover.png" alt="Cover of the book" width="360">
</p>

<h1 align="center">How to build an Agentic SDLC in your repository</h1>

<p align="center">
  <b>«Методичка профессора Фортрана. Как построить Agentic SDLC в своём репозитории»</b><br>an illustrated book in Russian
  on preparing a repository and a team's process for AI coding agents
</p>

<p align="center">
  <a href="https://github.com/pulyavin/agentic-sdlc/releases/latest/download/agentic-sdlc.pdf"><b>Download the PDF</b></a>
  ·
  <a href="https://github.com/pulyavin/agentic-sdlc/releases">All versions</a>
  ·
  <a href="CONTRIBUTING.md">Contribute</a>
</p>

<p align="center">
  <a href="https://github.com/pulyavin/agentic-sdlc/actions/workflows/check.yml"><img src="https://github.com/pulyavin/agentic-sdlc/actions/workflows/check.yml/badge.svg" alt="check"></a>
  <a href="https://github.com/pulyavin/agentic-sdlc/releases/latest"><img src="https://img.shields.io/github/v/release/pulyavin/agentic-sdlc?label=version" alt="latest version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/text-CC%20BY--NC%204.0-blue" alt="CC BY-NC 4.0"></a>
</p>

---

An agent writes slop in a repository that isn't ready for it: it doesn't know your conventions, can't run your
project and has no way to notice its own mistakes. This book walks through preparing the repository and the process
step by step — from `AGENTS.md` to a pipeline where the agent takes a task from request to production — with a
practical prompt for every step. Professor Fortran, the Cat, the Sparrow, the Caterpillar and the Agent keep you
company along the way.

<p align="center">
  <img src="docs/images/spread.png" alt="A spread from the book" width="720">
</p>

## Contents

| | Chapter |
|---|---|
| | Введение |
| 1 | Почему агент пишет слоп |
| 2 | Выбираем модель и инструмент |
| 3 | MCP: подключаем агента к твоим сервисам |
| 4 | Что агенту нужно знать о проекте |
| 5 | Скиллы — инструкции на каждый день |
| 6 | Агент должен видеть результат своей работы |
| 7 | Агент сам находит свои ошибки |
| 8 | CI — последний рубеж перед main |
| 9 | Код-ревью, когда код пишут агенты |
| 10 | Как не дать агенту всё сломать |
| 11 | Как теперь выглядит разработка |
| | Заключение |

## This repository is an example too

The repository is set up the way the book recommends, so you can see every idea in a working project:

| In the book | Here |
|---|---|
| Instructions for the agent | [`AGENTS.md`](AGENTS.md) |
| Skills for repeated work | [`.claude/skills/`](.claude/skills) — build the book, check a chapter, raise the version |
| Decisions that the code doesn't show | [`docs/adr/`](docs/adr) |
| The agent learns about its mistakes on its own | tests, the linter and `book audit`, which measures every page |
| CI is the gate before `main` | [`check.yml`](.github/workflows/check.yml) on every pull request |
| From merge to production | [`release.yml`](.github/workflows/release.yml) publishes the PDF as a release on every merge that raises the version |

## How the book is built

The chapters are Markdown with a few blocks of their own: the characters' notes, prompts in drawn monitors, tables,
steps. A Python tool compiles them to HTML, Google Chrome lays out every page and prints a vector PDF, and every
drawing — characters, scenes, the worlds of the chapters — is generated as code.

```bash
cd tools
uv sync
uv run book build --strict        # ../book -> ../dist/agentic-sdlc.pdf
uv run book audit --baseline audit-baseline.json   # build once and check every page, as CI does
uv run book build --demo          # a showcase of every block
uv run pytest                     # tests
```

You need [uv](https://docs.astral.sh/uv/) and Google Chrome. Read more in [`docs/build.md`](docs/build.md) and
[`docs/design-system.md`](docs/design-system.md).

## Contributing

Found a typo, an inaccuracy or an outdated fact? Open a pull request or an issue: [CONTRIBUTING.md](CONTRIBUTING.md)
explains how. CI builds the book and checks every page, and every merge that raises the version becomes a new release. A star tells the
author the book is worth developing further.

## Author

Artem Puliavin (Тёма Пулявин), former CTO of the car-sharing service Citydrive —
[blog «Быть Лидом»](https://t.me/tobelead) · [Telegram](https://t.me/puliavin).

The characters are an homage to «Энциклопедия профессора Фортрана» by A. V. Zaretsky, M. O. Zaretskaya,
A. V. Trukhanov and the artist E. L. Desyatnik; the drawings in this repository are original.

## License

- The text and pictures of the book, except the author's photo: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) — share and
  adapt with credit to the author and the book, no commercial use.
- Prompts, commands and code examples in the book: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
- The build tool: [PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0).
- Fonts: SIL Open Font License 1.1.

See [LICENSE](LICENSE) for the details.

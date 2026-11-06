## Один `AGENTS.md` для всех агентов

Поначалу каждая компания решала одну и ту же задачу по-своему, но за последний год всё наконец начало стандартизироваться, а значит, репозиторий, подготовленный по этой книге, поймёт почти любой агент.

::: note cat
goose — открытый ИИ-агент, который работает у тебя на компьютере, а сделала его компания Block, та самая, что стоит за Square и Cash App. Подробности — на сайтах стандартов: [agents.md](https://agents.md), [agentskills.io](https://agentskills.io), а о фонде — на [aaif.io](https://aaif.io)
:::

- **`AGENTS.md`** — файл с инструкциями для агента. Его выпустила OpenAI в августе 2025 года, а в декабре он вместе с MCP от Anthropic и агентом goose от Block вошёл в Agentic AI Foundation — фонд при Linux Foundation, в который входят Anthropic, OpenAI, Google, Microsoft, AWS и другие.
- **Скиллы** — папки с инструкциями, которые агент подгружает, когда они нужны. Их придумала Anthropic в октябре 2025 года, а в декабре выпустила как открытый стандарт Agent Skills, и теперь его поддерживают Claude Code, Codex, Antigravity CLI, Cursor, Copilot и другие.

Раньше был `AGENTS.md`, был `CLAUDE.md`, и каждый инструмент читал своё, а сейчас `AGENTS.md` читают все, и Claude Code тоже — начиная с версии 2.1.277 он читает его сам, если рядом нет `CLAUDE.md`. Так что одного `AGENTS.md` теперь вполне достаточно, а как его завести, разберём в четвёртой главе. А вот с папками для скиллов единства пока нет, и Claude Code, например, читает только свою:

| Инструмент | Файл инструкций | Папка скиллов |
|---|---|---|
| Claude Code | `AGENTS.md`, если нет `CLAUDE.md` | `.claude/skills` |
| Codex | `AGENTS.md` | `.agents/skills` |
| Antigravity CLI | `AGENTS.md` и `GEMINI.md` | `.agents/skills` |
| Cursor | `AGENTS.md` | `.agents/skills`, `.cursor/skills`, `.claude/skills` |
| GitHub Copilot | `AGENTS.md`, `.github/copilot-instructions.md` | `.github/skills`, `.agents/skills`, `.claude/skills` |

::: note agent
Я проверил на себе: скилл из общей папки подхватился по ссылке, и я его вижу
:::

Но на самом деле никто не мешает тебе вести все скиллы в одной папке и сделать на неё символьные ссылки для разных инструментов, и тогда в одной кодовой базе спокойно уживутся разные агенты. Напрямую такого разработчики инструментов не советуют, но работает это вполне, а вот на Windows со ссылками есть свои сложности, о которых поговорим в главе про скиллы.

```terminal
# Скиллы лежат в .agents/skills, а Claude Code видит их по ссылке
$ mkdir -p .claude
$ ln -s ../.agents/skills .claude/skills
```

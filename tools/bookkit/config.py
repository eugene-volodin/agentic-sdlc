"""Book configuration: `book.yml` of the content folder merged over the built-in locale."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .art.characters import register_aliases
from .markup import BuildError, read_source, split_front_matter, yaml_problem

PACKAGE = Path(__file__).resolve().parent
THEME = PACKAGE / "theme"
LOCALES = PACKAGE / "locale"
# Keys `book.yml` may contain.
BOOK_KEYS = ("title", "title_highlight", "headline", "headline_highlight", "topics", "subtitle", "kicker", "author",
             "year", "toc", "cover", "repo", "version", "version_from", "plan",
             "chapters", "language", "strings")
# The handbook's version: MAJOR.MINOR-MM.YYYY, the month and year of the release.
VERSION = re.compile(r"\d+\.\d+-(0[1-9]|1[0-2])\.\d{4}")


def _merge(base: dict, override: dict) -> dict:
    """Recursively overlay `override` on `base` without mutating either."""
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


@dataclass
class BookConfig:
    """Everything the build needs to know about the book as a whole."""

    content_dir: Path
    title: str = "Untitled"
    title_highlight: str = ""
    kicker: str = ""
    headline: str = ""
    headline_highlight: str = ""
    topics: list[str] = field(default_factory=list)
    subtitle: str = ""
    author: str = ""
    year: str = ""
    toc: bool = True
    cover: bool = True
    plan: list[str] = field(default_factory=list)   # every chapter in order, written or not: "3. Title" or "Title"
    repo: str = ""          # the public repository of the text, e.g. https://github.com/owner/name
    version: str = ""       # `version:` in book.yml, or the version of the book.yml that `version_from:` names
    chapters: list[str] = field(default_factory=list)
    strings: dict = field(default_factory=dict)

    @property
    def download(self) -> str:
        """A link that always gives the newest PDF: the asset `agentic-sdlc.pdf` of the repository's latest release."""
        return f"{self.repo.rstrip('/')}/releases/latest/download/agentic-sdlc.pdf" if self.repo else ""

    @property
    def language(self) -> str:
        return self.strings.get("language", "en")

    def label(self, key: str) -> str:
        """A UI string from the locale; a missing one is a build error, not a silent placeholder."""
        labels = self.strings.get("labels", {})
        if key not in labels:
            raise BuildError(f"the locale has no label {key!r}; add it under 'labels:' in the locale file")
        return str(labels[key])

    def opener_words(self, story: str) -> dict:
        """The lettering inside an opener's picture, from `openers:` in the locale."""
        return dict(self.strings.get("openers", {}).get(story) or {})

    def character(self, name: str) -> dict:
        return self.strings.get("characters", {}).get(name, {"name": name, "role": ""})

    def vocabulary(self) -> dict:
        """What the footers need from the locale: `footers:` at the top level, with the lettering of the worlds and of
        the easter eggs beside it."""
        return {**(self.strings.get("footers") or {}), "worlds": self.strings.get("worlds") or {},
                "easter": self.strings.get("easter") or {}}

    def chapter_sources(self) -> list[ChapterSource]:
        """The chapters in order: each is one Markdown file, or a folder whose files are its parts."""
        if not self.content_dir.is_dir():
            raise BuildError(f"no such folder: {self.content_dir}")
        if self.chapters:
            entries = [self.content_dir / str(name) for name in self.chapters]
            outside = [str(name) for name, entry in zip(self.chapters, entries, strict=True)
                       if not entry.resolve().is_relative_to(self.content_dir.resolve())]
            if outside:   # the public repository builds what is in it, nothing from beside it
                raise BuildError(f"book.yml lists chapters outside the book's folder: {', '.join(outside)}")
            missing = [str(entry) for entry in entries if not entry.exists()]
            if missing:
                raise BuildError(f"book.yml lists chapters that do not exist: {', '.join(missing)}")
        else:
            entries = sorted(entry for entry in self.content_dir.iterdir() if not entry.name.startswith((".", "_")))
        sources = []
        for entry in entries:
            if entry.is_dir():
                files = sorted(path for path in entry.glob("*.md") if not skipped(path))
                if files and all(is_front_page(path) for path in files):
                    # A folder of front pages (all pages before the chapters, in one folder):
                    # every file is a page of its own, in the order of its name.
                    sources += [ChapterSource(path, [path], group=entry.name) for path in files]
                elif files:
                    sources.append(ChapterSource(entry, files))
                elif self.chapters:
                    raise BuildError(f"book.yml lists the folder {entry.name}, but it has no Markdown files")
            elif entry.suffix == ".md" and (self.chapters or not skipped(entry)):
                sources.append(ChapterSource(entry, [entry]))
            elif self.chapters:
                raise BuildError(f"book.yml lists {entry.name}, which is neither a folder nor a Markdown file")
        return sources

    def chapter_files(self) -> list[Path]:
        """Every Markdown file of the book, in reading order."""
        return [path for source in self.chapter_sources() for path in source.files]


SKIPPED_NAMES = ("readme.md", "license.md", "contributing.md")   # a repository's own files, never chapters


def is_front_page(path: Path) -> bool:
    """Whether a Markdown file opens with front matter saying `front: true`."""
    try:
        meta = split_front_matter(read_source(path))[0]
    except BuildError:
        return False   # reported with its file and line when the chapter is compiled
    return meta.get("front") is True


def skipped(path: Path) -> bool:
    return path.name.lower() in SKIPPED_NAMES or path.name.startswith((".", "_"))


@dataclass(frozen=True)
class ChapterSource:
    """Where one chapter comes from."""
    path: Path              # the file, or the folder holding the chapter's parts
    files: list[Path]       # its Markdown files in reading order; the first one carries the front matter
    group: str = ""         # the folder a front page shares with the other front pages

    @property
    def name(self) -> str:
        return f"{self.group}/{self.path.name}" if self.group else self.path.name

    def label(self, file: Path) -> str:
        """How a file of this chapter is named in messages."""
        if file == self.path:
            return self.name
        return f"{self.path.name}/{file.name}"


def load_config(content_dir: Path) -> BookConfig:
    """Read `book.yml` (if present) and the locale it selects."""
    path = content_dir / "book.yml"
    if not content_dir.is_dir():
        raise BuildError(f"{content_dir}: no such folder")
    if not path.is_file():
        raise BuildError(f"{content_dir}: no book.yml; a book's folder holds its book.yml and its chapters")
    raw = _yaml(path)
    unknown = sorted(set(raw) - set(BOOK_KEYS))
    if unknown:
        raise BuildError(f"{path.name}: unknown key(s) {', '.join(unknown)}; available: {', '.join(BOOK_KEYS)}")
    _check_types(raw, path.name)
    locale_file = LOCALES / f"{raw.get('language', 'ru')}.yml"
    if not locale_file.exists():
        raise BuildError(f"no locale file for language {raw.get('language')!r} in {LOCALES}")
    strings = _merge(yaml.safe_load(locale_file.read_text(encoding="utf-8")), raw.get("strings") or {})
    aliases = {}
    for name, info in (strings.get("characters") or {}).items():
        if not isinstance(info, dict) or not isinstance(info.get("aliases", []), list):
            raise BuildError(f"{path.name}: strings: characters: {name} must be a mapping with a list of aliases")
        for alias in info.get("aliases", []):
            aliases[str(alias)] = name
    register_aliases(aliases)
    return BookConfig(
        content_dir=content_dir,
        title=str(raw.get("title", "Untitled")),
        title_highlight=str(raw.get("title_highlight", "")),
        kicker=str(raw.get("kicker", "")),
        headline=str(raw.get("headline", "")),
        headline_highlight=str(raw.get("headline_highlight", "")),
        topics=[str(topic) for topic in raw.get("topics") or []],
        subtitle=str(raw.get("subtitle", "")),
        author=str(raw.get("author", "")),
        year=str(raw.get("year", "")),
        toc=bool(raw.get("toc", True)),
        cover=bool(raw.get("cover", True)),
        repo=str(raw.get("repo", "")),
        plan=[str(item) for item in raw.get("plan") or []],
        version=read_version(raw, content_dir),
        chapters=list(raw.get("chapters") or []),
        strings=strings,
    )


def _yaml(path: Path) -> dict:
    """A YAML file of the author's that must hold a mapping; an empty file is an empty mapping."""
    try:
        raw = yaml.safe_load(read_source(path)) or {}
    except yaml.YAMLError as error:
        raise BuildError(f"{path.name}: {yaml_problem(error)}") from error
    if not isinstance(raw, dict):
        raise BuildError(f"{path.name}: must be a mapping of keys to values")
    return raw


# What each key of book.yml must hold, so `toc: no` or `topics: Skills` fail instead of meaning something else.
_TEXT_KEYS = ("title", "title_highlight", "headline", "headline_highlight", "subtitle", "kicker", "author", "year",
              "repo", "version", "version_from", "language")
_LIST_KEYS = ("topics", "plan", "chapters")


def _check_types(raw: dict, name: str) -> None:
    for key in _TEXT_KEYS:
        value = raw.get(key, "")
        if isinstance(value, bool) or not isinstance(value, (str, int)):
            raise BuildError(f"{name}: {key} must be text, got {raw[key]!r}")
    for key in _LIST_KEYS:
        if key in raw and not (isinstance(raw[key], list) and all(isinstance(v, (str, int)) for v in raw[key])):
            raise BuildError(f"{name}: {key} must be a list of text items, e.g. [a, b], got {raw[key]!r}")
    for key in ("toc", "cover"):
        if key in raw and not isinstance(raw[key], bool):
            raise BuildError(f"{name}: {key} must be true or false, got {raw[key]!r}")
    if "language" in raw and not re.fullmatch(r"[a-z]{2}", str(raw["language"])):
        raise BuildError(f"{name}: language must be a two-letter code like ru, got {raw['language']!r}")
    if "strings" in raw and not isinstance(raw["strings"], dict):
        raise BuildError(f"{name}: strings must be a mapping")
    repo = str(raw.get("repo", ""))
    if repo and not re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+/?", repo):
        raise BuildError(f"{name}: repo must be a GitHub address like https://github.com/owner/name, got {repo!r}")


def read_version(raw: dict, content_dir: Path) -> str:
    """`version:` of book.yml, or that of the book.yml `version_from:` points to (a second content folder can share
    the book's version).

    No version means none is printed; a malformed one is an error, not a silent blank.
    """
    source = content_dir / "book.yml"
    if raw.get("version_from"):
        source = content_dir / str(raw["version_from"])
        if not source.is_file():
            raise BuildError(f"book.yml: version_from names {source}, which does not exist")
        raw = _yaml(source)
    version = str(raw.get("version", "")).strip()
    if version and not VERSION.fullmatch(version):
        raise BuildError(f"{source}: the version must look like 1.4-10.2026 (MAJOR.MINOR-MM.YYYY), got {version!r}")
    return version

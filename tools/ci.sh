#!/usr/bin/env bash
# The checks of CI, in the order CI runs them: the tests, the linter, then one build of the book that audits every page
# (`book audit`: every warning of the build is an error there, as with `book build --strict`). It writes the PDF, the
# report and the contact sheets of the flagged pages to ../dist/ci/.
#
# CI runs this inside the image of tools/Dockerfile; tools/container.sh runs it there on any machine. Run from tools/.
# BASE (a git ref, e.g. origin/main) makes the audit check that book/ changed only together with its version.
# ADVISORY=1 (a contributor's pull request from a fork) reports the layout warnings without failing on them: the
# maintainer lays the pages out after the merge, a contributor only writes the text.
set -euo pipefail
cd "$(dirname "$0")"
out=../dist/ci
mkdir -p "$out"
rm -rf "$out/sheets"

uv sync --frozen
# The tests in three runs: the frames of every world are thousands of cases, and one process holding them all with the
# rest outgrows a container's memory on a laptop.
worlds=(tests/test_world_frames.py tests/test_world_kit.py)
uv run --frozen pytest -q -p no:cacheprovider "${worlds[@]/#/--ignore=}"
for file in "${worlds[@]}"; do
  uv run --frozen pytest -q -p no:cacheprovider "$file"
done
uv run --frozen ruff check bookkit tests
uv run --frozen book audit ${BASE:+--base "$BASE"} ${ADVISORY:+--advisory} --baseline audit-baseline.json \
  --md "$out/report.md" --json "$out/audit.json" --sheets "$out/sheets" --pdf "$out/agentic-sdlc.pdf"

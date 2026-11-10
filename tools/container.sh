#!/usr/bin/env bash
# Runs a command inside the build's reference image (tools/Dockerfile), with the repository mounted: the same system,
# browser and fonts as CI, so the same pages. Without arguments it runs ./ci.sh, exactly what CI runs; with arguments
# it runs them instead, from tools/ (e.g. `tools/container.sh uv run book build --strict`). Needs Docker.
set -euo pipefail
tools="$(cd "$(dirname "$0")" && pwd)"
repo="$(dirname "$tools")"
# BOOKKIT_IMAGE names an image built already (CI builds it with its layer cache); otherwise it is built here, from the
# cache of earlier builds when nothing changed.
image="${BOOKKIT_IMAGE:-bookkit-build}"
if [ -z "${BOOKKIT_IMAGE:-}" ]; then
  docker build --quiet --tag "$image" "$tools" >/dev/null
fi
tty=()
[ -t 0 ] && [ -t 1 ] && tty=(--tty --interactive)
exec docker run --rm ${tty[@]+"${tty[@]}"} --init --ipc=host --user "$(id -u):$(id -g)" \
  --env BASE --env ADVISORY --volume "$repo:/repo" --workdir /repo/tools "$image" "${@:-./ci.sh}"

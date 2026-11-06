# The reference environment of the build: the same image runs the checks in CI and on an author's machine
# (tools/container.sh), so both lay the book out in the same browser on the same system and get the same pages.
#
# The base is Playwright's own image for the playwright version pinned in uv.lock: Ubuntu 24.04 with Python and that
# version's Chromium. It is published for amd64 and arm64. When uv.lock moves to another playwright, change the tag.
FROM mcr.microsoft.com/playwright/python:v1.63.0-noble

COPY --from=ghcr.io/astral-sh/uv:0.11.18 /uv /uvx /usr/local/bin/

# git: the audit compares book/ with the main branch. The repository is mounted from the host and owned by another
# user, so git is told to trust it.
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/* \
 && git config --system --add safe.directory '*'

# The dependencies live outside the mounted repository, so a host's own tools/.venv is never touched. Any user may run
# the image (CI runs it as the runner's user): the environment and the caches are writable by all.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_CACHE_DIR=/tmp/uv-cache \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    HOME=/tmp
WORKDIR /opt/bookkit
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project && chmod -R a+rwX /opt/venv /tmp/uv-cache
WORKDIR /repo/tools

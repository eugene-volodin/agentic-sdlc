## What changes

<!-- A sentence or two: what you fixed or added, and why. -->

## Checklist

- [ ] If `book/` changed, the version in `book/book.yml` is raised (`MAJOR.MINOR-MM.YYYY`: MINOR + 1, the current month and year)
- [ ] Facts about models and tools link to official documentation
- [ ] Every prompt or command I added has been run
- [ ] I looked at the changed pages: `cd tools && uv run book build --strict --shots all`
- [ ] The audit passes: `uv run book audit --base origin/main --baseline audit-baseline.json`

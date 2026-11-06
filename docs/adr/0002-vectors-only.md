# 0002. Everything in the PDF is a vector, set in the book's own fonts

Status: accepted

## Context

Readers open the book on phones, in Telegram, in Preview and in browsers. Chrome prints SVG masks, filters and
gradients that fade to transparent as low-resolution rasters with a soft mask, and some viewers draw those in torn
patches. Variable fonts are printed as Type 3 glyph drawings that some viewers render coarsely.

## Decision

- Every drawing is generated as SVG from Python (`tools/bookkit/art/`) using only what Chrome prints as vectors:
  no `<mask>`, no `<filter>`, no gradient with transparent stops (`Canvas.fade` stacks flat layers instead).
- Every glyph comes from the fonts bundled in `tools/bookkit/theme/fonts/`. Variable fonts are cut into one static
  font per weight before printing (`tools/bookkit/fonts.py`), so the PDF embeds TrueType subsets.
- The build scans the finished PDF and fails under `--strict` on any raster other than the book's own pictures and
  on any font taken from the building machine.

## Consequences

- The PDF looks the same in every viewer and stays small.
- Some visual effects (blur, soft shadows, real transparency) are not available; the drawings imitate them with
  flat layers.

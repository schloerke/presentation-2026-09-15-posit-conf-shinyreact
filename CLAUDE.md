# posit::conf(2026) — "Shiny + React"

Talk materials for Barret Schloerke's posit::conf(2026) session. Not a package;
nothing here ships to users. If knowledge is corrected or enhanced, update this 
document to support future sessions.

## Layout

```
outline.md                 the talk's narrative, in speaker-note form
slides.qmd                 the deck (Quarto revealjs) - primary authoring surface
theme/DESIGN.md            the design spec - single source of truth for the look
theme/shinyreact-dark.scss revealjs theme, ported from DESIGN.md
theme/shinyreact-dark.highlight.theme  pandoc code colours (DESIGN.md 4.1)
theme/build_theme.py       generates the Keynote/pptx theme from the same spec
theme/shinyreact-dark.theme  `highlight` colours for Keynote clipboard pastes
theme/preview/*.png        Keynote renders - the reference the SCSS is matched to
apps/                      runnable Shiny apps demoed live in the talk
_extensions/drop/          quarto-drop (webR console in a drawer)
```

**`theme/DESIGN.md` outranks both renderers.** The SCSS and `build_theme.py` are
two ports of it. If a colour, size, or margin needs to change, change DESIGN.md
first, then both ports — otherwise they silently drift.

## Working on the deck

```bash
quarto preview slides.qmd     # live reload while writing
quarto render slides.qmd
```

The canvas is **1920x1080** (set in the qmd), which is why the SCSS uses the
same px values DESIGN.md and `build_theme.py` do. Do not rescale them; reveal
fits the canvas to the viewport.

`theme/fit-width.html` (wired in via `include-after-body`) makes the deck scale
to the window's **width** rather than fitting inside it. Reveal's own scale is
`min(winW/canvasW, winH/canvasH)`, so a window that isn't 16:9 letterboxes and
stops tracking the width; the script pins the canvas at 1920 wide and lets its
height follow the window's aspect ratio, making width the binding constraint.
Canvas height is floored at 1080 so a short, wide window letterboxes instead of
clipping the bottom off every slide. On a 16:9 projector the whole thing is a
no-op. (Same lever as
<https://github.com/orgs/quarto-dev/discussions/11318>, which sets `height:`
statically; this just does it per window.)

Master equivalents, applied as classes on a `##` heading:

| DESIGN.md master | markdown |
|---|---|
| Title | the auto title slide (`title:`/`subtitle:`/`author:` in yaml) |
| Section divider | `## Name {.divider data-number="01"}` |
| Content | `## Name` + a bullet list |
| Code two-up | `## Name {.code-slide}` + `.columns` with two fenced blocks |
| Data | `## Name {.data-slide}` + caption, `.stats`, one chart |

Code fences take `filename="app.R"`, which renders as the uppercase cyan label
from DESIGN.md 6.4.

### Reveal quirks this theme already works around

Do not "clean these up" — each one silently breaks the layout:

- `.reveal .slides section` needs `box-sizing: border-box`. Reveal sets an
  explicit `height: 1080px`, so content-box padding makes slides 1396px tall.
- The same rule needs `top: 0 !important`. Reveal leaves `top: auto` on
  non-centered slides and lets the static position decide, which drops some of
  them a full canvas down.
- Never set `position: relative` on a section. Reveal positions sections
  absolutely; making one relative puts it back in flow and pushes it off-canvas.
  Pseudo-elements can already position against the section as-is.
- Quarto's code filename div is `.code-with-filename-file` (not `-title`), and
  it wraps the name in `<pre><strong>`, so `.reveal pre` re-styles it as a code
  panel unless overridden.
- SVG data-URI motifs (orbit, swoosh) are scaled by `background-size`, so
  strokes need `vector-effect="non-scaling-stroke"` or they thicken with the
  motif.

### Live code and apps

`_extensions/drop` gives a webR console on the backtick key, with state kept
across slides. It is a **console**, not a Shiny runner — it cannot host the
`apps/` demos, which need `shinyreact` and a bundled JS frontend. Run those
locally and embed with `<iframe class="app" src="http://127.0.0.1:8080">`.

## Non-negotiables from DESIGN.md

These were measured, not estimated (DESIGN.md 9). Verify, don't assume:

- Every text pair ≥ 7:1 contrast. Worst in use is the code comment at 7.17:1.
- Body ≥ 36px, code ≥ 32px, nothing below 28px on the 1920x1080 canvas.
- One motif per slide (hexagon / orbit / swoosh). See DESIGN.md 8.
- `#00D8FF` is graphic-only; text cyan is `#6FD4E8` (fringing, not contrast).
- Chart series colours are assigned in fixed order and never cycled.

Check work against `theme/preview/master-N-blank.png`, which is what the Keynote
theme actually produces.

## The Keynote path

Still live, for when Keynote's presenter tooling is wanted. See
`theme/README.md` — in particular that Save Theme captures *master slides*, not
content slides, and must be run from the right window.

## Reference

- Quarto revealjs: <https://quarto.org/docs/presentations/revealjs/>
- Slidecrafting: <https://slidecrafting-book.com/> — good on theming and layout;
  several chapters are still marked WIP, so confirm before relying on one.

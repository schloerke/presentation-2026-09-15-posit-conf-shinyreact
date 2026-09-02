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
_extensions/EmilHvitfeldt/ quarto-revealjs-editable (live slide editing)
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
| (none — deck-local) | `## Name {.demo-slide}` + a `shinylive-r` block |

`.demo-slide` is for live apps: the heading is kept in the source (quarto splits
slides on `##`, and it carries the slide id and speaker notes) but hidden, and
padding, wrapper margin and footer all go to zero so the app fills 1920x1080.
Pair it with `#| viewerHeight: 1080`.

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
- `code-line-numbers="|5|6"` is not a reveal fragment on one block — quarto's
  `quarto-line-highlight` plugin *clones* the `<code>` once per step and stacks
  the clones with `position: absolute; top: 0`. That resolves against `pre`'s
  **padding** box, so every step after the first jumps up by `pre`'s 40px
  padding. The theme fixes it by making such a `pre` a grid and pinning every
  `> code` to cell `1 / 1`; an abspos grid item's containing block is its grid
  area, which sits inside the padding. Don't "fix" it with a hardcoded `top`.
- A trailing `|` in `code-line-numbers` ("|6|7|4,8|") adds a step that clears
  the highlight. Use one before an `auto-animate` pair so the transition only
  has to move the changed lines instead of un-highlighting *and* rewriting.
- To land text on the *same* click as one of those steps, do **not** reach for
  `.fragment fragment-index=N`. Reveal's `sortFragments` puts every
  explicitly-indexed fragment ahead of the unindexed ones, and the
  line-highlight clones are unindexed, so the text jumps to the front of the
  slide. The theme's `.after-code` keys off the last clone instead
  (`section:has(pre > code.fragment:last-of-type.visible)`), which reverses
  correctly too. Quarto's `data-fragment-index` escape hatch in that plugin is
  no help: it reads the attribute off the `<code>`, and a block attribute lands
  on the wrapping `div.sourceCode`.

### Editing slides during the talk (installed, off)

`_extensions/EmilHvitfeldt` (quarto-revealjs-editable) allows dragging,
resizing and retyping content on the rendered slide. It is installed but
**commented out in both yaml lists**, and it needs both to do anything:

```yaml
revealjs-plugins: [drop, editable]
filters: [shinylive, editable]
```

Uncomment only while actually adjusting something, then comment it back out:
it pins a 100px Save/Add/Modify bar to the top of the window and sets
`html.has-editable-toolbar`, which offsets `.reveal` by the same 100px, so
every slide gets a toolbar and loses 100px of height. The plugin has no option
to hide it.

Click **Modify** to edit the current slide; `.editable` on a div or image
pre-marks it. Save Edits writes back absolute geometry
(`{.absolute width=… left=…}`), which is at odds with every master in
DESIGN.md — treat anything it writes into `slides.qmd` as something to fold
back into the theme, not to keep.

### Live code and apps

`_extensions/drop` gives a webR console on the backtick key, with state kept
across slides. It is a **console**, not a Shiny runner.

Plain-Shiny demos run in-browser via `_extensions/quarto-ext/shinylive`
(`filters: [shinylive]`), so no local server is needed:

````
```{shinylive-r}
#| standalone: true
#| components: [viewer]
#| viewerHeight: 660
{{< include apps/00-old-faithful-trim/app.R >}}
```
````

The `{{< include >}}` keeps the slide and `apps/` from drifting — includes
resolve before the shinylive filter runs. webR loads `shiny`/`bslib` from CDN on
first visit (a few seconds); the `preload error:` console lines are just
bslib's masking messages on stderr.

The `shinyreact` demo runs in shinylive too, with its `www/` files passed as
extra `## file:` entries in the same block. There are no iframes in the deck any
more; nothing has to be running for the slides to work.

`shinyreact` is a monorepo, and the R package is **not at the root** — plain
`pak::pak("posit-dev/shinyreact")` fails with "Can't find R package in GitHub
repo". Install the subdirectory:

```r
pak::pak("posit-dev/shinyreact/pkg-r")
```

### Getting `shinyreact` into webR — the fiddly part

Four things had to line up. If any one regresses, the slide goes blank.

1. **`wasm-repo/` at the deck root** holds a webR-format binary of
   `shinyreact`, because it is on neither CRAN nor repo.r-wasm.org. It is a
   pure-R package, so a plain local build is enough — no emscripten toolchain:

   ```bash
   git clone --depth 1 https://github.com/posit-dev/shinyreact /tmp/sr
   R CMD INSTALL --build --library=/tmp/lib /tmp/sr/pkg-r      # -> .tgz
   mkdir -p wasm-repo/bin/emscripten/contrib/4.5
   cp shinyreact_*.tgz wasm-repo/bin/emscripten/contrib/4.5/
   Rscript -e 'tools::write_PACKAGES("wasm-repo/bin/emscripten/contrib/4.5", type = "mac.binary")'
   ```

   `4.5` must match webR's R version, **not** yours: shinylive 0.10.8 runs
   R 4.5.1. Building under a local R 4.5.x is what keeps it loadable — a 4.6
   build would be the wrong series. (Verified by probing shinylive's own
   `webr.mjs`: `R version 4.5.1`, `wasm32-unknown-emscripten`.)

2. **The app installs it at runtime**, from the slide block:

   ```r
   webr::install(
     "shinyreact",
     repos = c("../../../../../../wasm-repo", "https://repo.r-wasm.org")
   )
   ```

   Keep repo.r-wasm.org in that vector. `webr::install()` *replaces* the repo
   list, and dropping it makes the Imports (`brio`, `cli`, `rlang`, …) fail with
   "Requested package brio not found in webR binary repo".

   The relative URL resolves against webR's asset directory
   (`slides_files/libs/quarto-contrib/shinylive-*/shinylive/webr/`), so six
   levels up is always the folder holding `slides.html` — it travels with the
   deck wherever it is served. It does assume that path depth, which is fixed by
   shinylive's layout.

3. **`_quarto.yml` + `_environment`** carry `SHINYLIVE_WASM_PACKAGES=0`. Without
   it the render *fails*: shinylive sees `shinyreact` installed from a GitHub
   remote and calls `get_github_wasm_assets()`, which looks for a GitHub release
   tagged with the install's `RemoteRef` (`HEAD`) carrying `library.data` +
   `library.js.metadata` assets. `posit-dev/shinyreact` has no releases, so
   `gh::gh()` 404s. The env var skips render-time wasm bundling entirely;
   packages are fetched at runtime instead, which this deck already did.
   `_quarto.yml` exists **only** so quarto reads `_environment` — it does that
   for projects, not single-file renders.

4. **The `www/` files ship as `## file:` entries** in the block, because
   `page_react_html()` does `brio::read_file("www/index.html")` inside the webR
   VFS.

**The clean way out of all four:** publish a GitHub release on
`posit-dev/shinyreact` with WebAssembly assets built by
<https://github.com/r-wasm/actions>. Then shinylive resolves the package itself
and steps 1–3 all delete. Adding the package to an r-universe does *not* help —
r-universe wasm builds are currently R 4.6 only (`bin/emscripten/contrib/4.6/`),
and shinylive keys off GitHub releases rather than the r-universe repo.

Expect ~30–45s for the first load of that slide (webR pulls shiny, bslib, brio,
…). The `preload error:` console lines are webR writing to stderr, not failures;
`package 'shinyreact' was built under R version 4.5.2` is a harmless warning
from the local build.

### Running the demos offline

The deck ships **only base R**. The bundled webR VFS image
(`shinylive/webr/library.data.gz`, 1920 files) has no `shiny`, `bslib`,
`htmltools`, … — those come off repo.r-wasm.org at runtime, so the live slides
currently need network.

Bundling them into the deck works, but re-enabling `SHINYLIVE_WASM_PACKAGES` is
**not** sufficient: `shinylive:::download_wasm_packages()` `setdiff`s the Shiny
stack (`shiny`, `bslib`, `renv` *and their recursive deps*) out of the bundle
list, which is why `packages/metadata.rds` renders as an empty 46 bytes. You
also need `SHINYLIVE_DOWNLOAD_WASM_CORE_PACKAGES` naming the **full recursive
set** — measured at 30 packages / 20 MB, after which a served deck makes zero
requests outside its own origin. Regenerate that list with
`tools::package_dependencies(c("shiny","bslib","renv"), recursive = TRUE, which = c("Depends","Imports","LinkingTo"))`.

Blocked for now: bundling resolves from the wasm binary repo, so it can't pick
`shinyreact` out of `wasm-repo/`. Needs posit-dev/shinyreact#268 first. Details
and caveats (version skew, `watcher` has no wasm build) are on
schloerke/presentation-2026-09-15-posit-conf-shinyreact#7.

`apps/01-shinyreact` is upstream's `examples/01-hello` with the bundle renamed
`app.js`/`app.tsx`, so upstream is the reference when something is missing —
`www/app.css` came from its `www/ui.css`. It uses `page_react_html()`, which
needs a `www/index.html` carrying
`<meta name="shiny-dependency-placeholder" content="">`; upstream's
`examples/01-hello` uses `page_react()` instead and has no HTML file at all.
Note the deck writes the bundle as `www/ui.tsx` while the app names it
`app.tsx`.

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

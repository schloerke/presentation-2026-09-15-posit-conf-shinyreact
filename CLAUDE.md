# posit::conf(2026) — "Shiny + React"

Talk materials for Barret Schloerke's posit::conf(2026) session. Not a package;
nothing here ships to users. If knowledge is corrected or enhanced, update this 
document to support future sessions.

## Layout

```
outline.md                 the talk's narrative, in speaker-note form
bundle-wasm.R              post-render: vendors wasm-repo/ into the render
index.qmd                  the deck (Quarto revealjs) - primary authoring surface
theme/DESIGN.md            the design spec - single source of truth for the look
theme/shinyreact-dark.scss revealjs theme, ported from DESIGN.md
theme/shinyreact-dark.highlight.theme  pandoc code colours (DESIGN.md 4.1)
theme/build_theme.py       generates the Keynote/pptx theme from the same spec
theme/fonts.scss           the DESIGN.md faces, inlined as data URIs (generated)
theme/build_fonts.py       regenerates fonts.scss - run it if 5.1 changes
theme/shinyreact-dark.theme  `highlight` colours for Keynote clipboard pastes
theme/preview/*.png        Keynote renders - the reference the SCSS is matched to
apps/                      the apps demoed live in the talk (02 is React-only)
_extensions/drop/          quarto-drop (webR console in a drawer)
_extensions/EmilHvitfeldt/ quarto-revealjs-editable (live slide editing)
```

**`theme/DESIGN.md` outranks both renderers.** The SCSS and `build_theme.py` are
two ports of it. If a colour, size, or margin needs to change, change DESIGN.md
first, then both ports — otherwise they silently drift.

## Working on the deck

```bash
quarto preview index.qmd     # live reload while writing
quarto render                 # whole project -> _site/ (see Publishing)
```

The deck is `index.qmd`, not `slides.qmd`, so the published site's root *is*
the deck. Render output goes to `_site/`, with `apps/` copied in as a project
resource (slide 02 loads it in an iframe by relative path).

### Looking at a slide

Checking a layout or a colour means rendering and *looking*, not reading the
SCSS. Serve the render and drive it with a browser tool; every slide has an id
from its heading, so `index.html#/two-hooks-are-the-whole-api` lands on one
directly. The browser caches `index.html` hard between renders — add a
`?v=N` that changes, or a re-render appears to have done nothing.

**Screenshots go in `.context/`, which is gitignored.** Never leave a debug
image in the repo root; if one is already there, delete it rather than adding
it to a commit or `.gitignore`.

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
| (none — deck-local) | `## Name {.cycle-slide .nostretch}` + a `mermaid` block |

`.demo-slide` is for live apps: the heading is kept in the source (quarto splits
slides on `##`, and it carries the slide id and speaker notes) but hidden, and
padding, wrapper margin and footer all go to zero so the app fills 1920x1080.
Pair it with `#| viewerHeight: 1080`.

Code fences take `filename="app.R"`, which renders as the cyan label from
DESIGN.md 6.4, in whatever casing you wrote — nothing upper-cases it.

A `.code-slide` usually opens with one **lead-in bullet** above the panel, in
`::: {.incremental}` so it lands on its own click, with the block(s) below it
wrapped in `.fragment` so they come after. The bullet is a caption, not a list:
`.code-slide ul` therefore drops the content master's 60px above and runs 32px
below, and the heading's margin shrinks to 16px. That rhythm is what makes a
13-line block fit — the list defaults put it 80px off the bottom of the slide,
which reads on a projector as the code simply ending early. Check the tail of
the longest block after any change here.

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
- Quarto caps highlighted blocks with `.reveal div.sourceCode pre code
  { max-height: 500px }`, which out-specifies `.reveal pre code`. Past ~11 lines
  the block silently becomes a scroll container and loses its tail — on a
  projector that just looks like the code ends mid-line. The theme resets it
  with the same selector.
- `.tsx` is not a skylighting language, so a `{.tsx}` block renders unhighlighted.
  Use `{.javascriptreact}`: it tokenises JSX (DOM tag → keyword, component →
  function, props → `ot`, coloured by the theme). `{.typescript}` highlights the
  type annotations instead but leaves all the markup grey.
- That grammar emits the bracket *and* the name as one token (`<main` is a
  single `span.kw`), so CSS cannot colour them apart.
  `theme/jsx-tokens.html` (a second `include-after-body`) re-splits those spans
  into `.jsx-b` / `.jsx-tag` at parse time — before quarto initialises Reveal,
  so the `code-line-numbers` clones copy the already-split markup. Its second
  pass re-tags what the grammar drops around a type parameter
  (`useShinyInput`, `number`, `HistData` come out as bare text) as `.jsx-id`.
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

### Mermaid (the one diagram, on "The data cycle")

**TODO — Barret does not like this diagram.** It is checked in to unblock the
rest of the deck, not because it is right. The layout went flowchart (two
columns, too wide) → vertical flowchart (needed two `browser` boxes, which ruins
the point) → this sequence diagram, and each step traded away something. If it
gets another pass, the honest options are hand-authored svg/html for this one
slide (full control of a real cycle, at the cost of custom CSS) or `block-beta`
(manual grid placement, still beta). The notes below are what mermaid will and
will not do, so a rewrite does not have to rediscover them.

`mermaid-format: svg` in the yaml is load-bearing: without it quarto leaves the
diagram to client-side mermaid, which measures its labels in a slide reveal has
`display: none`d and renders boxes with no text in them. With it, quarto
pre-renders the svg at build time. Everything else follows from that svg being
sized at build time and re-styled at display time:

- It is a **`sequenceDiagram`**, not a flowchart, and that is the whole reason
  the slide works. A flowchart cannot show the round trip with one browser box
  and one server box: dagre gives a cluster the bounding box of its members, so
  a browser box holding both hooks encloses the server box sitting between them.
  A sequence diagram gets both boxes plus time down the page for free.
- Each side's names sit on its own lifeline as **self-messages** (`B->>B:`,
  `S->>S:`), not as `Note`s. Notes are their own rows *and* render at 14px
  rather than 16px, and they overhang the lifelines, so they cost both of the
  budgets below at once: the note version measured 1200x447 units against this
  one's 810x420.
- The sequence renderer writes its font size **inline** (16px messages, 14px
  notes); the `sequence` config's `actorFontSize`/`messageFontSize` are ignored
  (both numbers and `"32px"` strings were tried). How big the labels read is
  therefore set by how far the whole svg is scaled up — `800px / 420 units` ≈
  x1.9, so 30px. Keep the graph narrow (`actorMargin: 100`) and short (five
  rows) and the text stays large; every extra row or unit of width shrinks it.
  Splitting the server's three steps into three self-messages, for instance,
  takes the graph to 713 units tall and the labels down to 19px.
- `.cycle-slide` pins **both** svg dimensions. Left to itself the svg takes its
  aspect ratio from quarto's 960x480 `width`/`height` attributes rather than
  from the viewBox, and the drawing floats in the middle of an 864px-tall box.
  (`%%| fig-height:` would change those attributes, but only if it comes
  *before* `%%{init}%%` — cell options first, or they are silently dropped.)
- Mermaid does **not** widen the diagram to fit message labels, so a label
  longer than the gap between the lifelines just overhangs them. That is fine
  here — there is empty slide either side — but it is why the two hops are one
  label each rather than a sentence.
- `.cycle-slide` trims the top pad to 76px and drops the swoosh under the
  headline, purely to hand those pixels to the diagram's height.
- The `%%{init}%%` block is JSON: no `//` comments in it, they break the parse.
  Set `fontFamily` at its top level, **not** in `themeVariables`, where it
  silently drops the font-family declarations from the generated css. It must
  also be a font the build host has — Inter is a webfont, so this uses
  Helvetica/Arial.
- The flowchart-specific rules in `.cycle-slide` (`foreignObject` overflow, the
  `font-size: inherit` handback) are still there because a flowchart's labels
  are html in a `foreignObject` sized to the text *as mermaid measured it*, and
  reveal restyles them afterwards. Needed again if this ever goes back to
  `flowchart`; harmless for the sequence renderer, which uses svg `<text>`.

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
DESIGN.md — treat anything it writes into `index.qmd` as something to fold
back into the theme, not to keep.

### Live code and apps

`_extensions/r-wasm/drop` gives a webR console on the backtick key, with state
kept across slides. It is a **console**, not a Shiny runner. It is installed but
**commented out in `index.qmd`** (both the `drop:` config and the
`revealjs-plugins` entry — it needs both), because its webR comes off
`https://webr.r-wasm.org/v0.4.0/` with the base URL hardcoded in the bundle: no
option to point it at local assets, ~30 MB over the venue's wifi, and dead
without wifi. Files are left on disk so it is a two-line re-enable.

`drop-runtime.js` is **patched** (marked `/* patched: … */`) to start its engine
on the first console open instead of at page load — upstream calls
`Rw(el, packages)` straight from `init`, which fired that CDN download on every
page load whether or not you ever pressed backtick. Keep the patch if you
re-enable the plugin; re-applying the extension will wipe it.

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
resolve before the shinylive filter runs. The `preload error:` console lines are
just bslib's masking messages on stderr.

Both apps start **at page load**, not on reveal: shinylive's
`run-python-blocks.js` walks every `.shinylive-r` block when its script runs and
calls `runApp()` there and then. Reveal's `display: none` on far-off slides does
not gate it, and there is no IntersectionObserver anywhere in the bundle. So
there is nothing to "preload" — measured cold on a served render, every asset is
in and both apps are interactive **~4.5s** after load, sitting on the title
slide. If a demo looks like it is loading when you arrive, it is because you got
there inside that window, not because it waited for you.

The `shinyreact` demo runs in shinylive too, with its `www/` files passed as
extra `## file:` entries in the same block.

`apps/02-react-only` ("Old Faithful, React only") is the odd one out: **no
Shiny at all**, so shinylive has nothing to run. It is a static page the slide
loads in an `<iframe>` — the one iframe in the deck. That still keeps the rule
that nothing has to be *running* for the slides to work: the src is a relative
path under `apps/`, served by whatever already serves `index.html`, and React
18's UMD build is vendored into `www/vendor/` so the page makes no off-origin
request. (React 18 because 19 dropped the UMD build, and UMD is what lets the
demo skip a bundler.)

- `www/app.js` is `React.createElement`, not JSX, for the same reason — no
  build step. The slide shows the JSX form of the same component; that is the
  same split `apps/01-shinyreact` already has between `app.js` and `app.tsx`.
- `www/data.js` holds `faithful$waiting` and `bin_data()`, the JS twin of what
  the R server computes in `01-shinyreact`. `node apps/02-react-only/check.mjs`
  asserts its counts match `hist()`'s for several bin counts — run it if you
  touch the binning.
- `www/app.css` is a copy of `01-shinyreact`'s, so the two demos look
  identical. That is the whole point of the pair: the same app, with
  `useState`/`useMemo` swapped for `useShinyInput`/`useShinyOutputValue`.
- Quarto's revealjs theme caps `.reveal iframe` at `max-width/height: 95%`,
  which letterboxes a full-bleed demo. `.demo-slide > iframe` in the SCSS
  undoes it — don't fix that with inline styles on the slide.

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

   `wasm-repo/` also carries **`brio`** — the one `shinyreact` Import that is
   not already in shinylive's library image. It needs no local build; it is the
   prebuilt wasm binary, fetched once:

   ```bash
   curl -O https://repo.r-wasm.org/bin/emscripten/contrib/4.5/brio_1.1.5.tgz
   ```

   (Re-run `write_PACKAGES` after adding anything.)

2. **`bundle-wasm.R` copies both into the render** as a quarto `post-render`
   step, writing the `packages/metadata.rds` that shinylive's runtime
   `.mount_vfs_images()` reads. That runs *before* `.start_app()`'s "install
   anything the app imports" loop, so by the time the loop looks, both packages
   are installed and it asks no repo for anything.

   This replaced a `webr::install("shinyreact", repos = …)` call in the slide
   block. Don't put it back: it ran *after* `.start_app()` had already tried and
   failed to find `shinyreact` on repo.r-wasm.org, i.e. one guaranteed off-origin
   request on the venue's wifi before the local install could rescue it.

3. **`_environment`** carries `SHINYLIVE_WASM_PACKAGES=0`. Without
   it the render *fails*: shinylive sees `shinyreact` installed from a GitHub
   remote and calls `get_github_wasm_assets()`, which looks for a GitHub release
   tagged with the install's `RemoteRef` (`HEAD`) carrying `library.data` +
   `library.js.metadata` assets. `posit-dev/shinyreact` has no releases, so
   `gh::gh()` 404s. The env var skips render-time wasm bundling entirely, and
   `bundle-wasm.R` does the bundling instead. `_quarto.yml` exists so quarto
   reads `_environment` (it does that for projects, not single-file renders) and
   to hold the `post-render` hook.

4. **The `www/` files ship as `## file:` entries** in the block, because
   `page_react_html()` does `brio::read_file("www/index.html")` inside the webR
   VFS.

**The clean way out of all four:** publish a GitHub release on
`posit-dev/shinyreact` with WebAssembly assets built by
<https://github.com/r-wasm/actions>. Then shinylive resolves the package itself
and steps 1–3 all delete. Adding the package to an r-universe does *not* help —
r-universe wasm builds are currently R 4.6 only (`bin/emscripten/contrib/4.6/`),
and shinylive keys off GitHub releases rather than the r-universe repo.

The `preload error:` console lines are webR writing to stderr, not failures;
`package 'shinyreact' was built under R version 4.5.2` is a harmless warning
from the local build.

### Running the demos offline — done, keep it that way

**A served render makes zero requests outside its own origin.** Verified at the
CDP level (which sees webR's worker traffic, unlike `performance.getEntries`):
no `repo.r-wasm.org`, no `webr.r-wasm.org`, no fonts, no CDN. Assume nothing
about venue wifi; if you add anything that reaches off-origin, you have broken
the demo, so re-check with the browser's network panel filtered to
`-localhost`.

The four things that hold it up:

1. **shinylive's own library image already has the Shiny stack.** Contrary to
   what this file used to say, `shinylive/webr/library.data.gz` (0.10.8, 31 MB
   unpacked) ships `shiny`, `bslib`, `htmltools`, `cli`, `jsonlite`, `rlang`,
   `sass`, `renv`, … 35 packages. List them with:

   ```bash
   python3 -c "import json;print(sorted({f['filename'].split('/')[1] for f in json.load(open('_site/index_files/libs/quarto-contrib/shinylive-0.10.8/shinylive/webr/library.js.metadata'))['files']}))"
   ```

   So `SHINYLIVE_DOWNLOAD_WASM_CORE_PACKAGES` and the 30-package / 20 MB
   recursive-dependency bundling described on issue #7 are **not needed** — the
   only gaps were `shinyreact` and `brio`.

2. **`bundle-wasm.R`** puts those two in the render (above).

3. **Fonts are inlined.** `theme/fonts.scss` is generated by
   `theme/build_fonts.py`: the DESIGN.md 5.1 faces as variable-weight woff2
   data URIs (latin + latin-ext, ~250 KB of SCSS), replacing a
   `@import url(fonts.googleapis.com…)`. Data URIs rather than files next to
   the SCSS because the compiled CSS lands under
   `_site/index_files/libs/revealjs/dist/theme/` and no relative path from there
   survives both `quarto preview` and a served render. Without this the deck
   silently falls back to Helvetica offline, which breaks every measured size
   in DESIGN.md.

4. **`html-math-method: plain`** in the qmd. Quarto's revealjs default pulls
   MathJax off jsdelivr; the deck has no math.

`quarto-drop` was the last offline hole and is **commented out** (below).

Still needs a server (`quarto preview`, or `python3 -m http.server` inside
`_site/`) — shinylive uses a service worker, so `file://` will not do.

## Commits and PRs

Commit messages and PR titles use [Conventional Commits](https://www.conventionalcommits.org/):
`type(scope): summary`, imperative mood, no trailing period.

Types in use here: `feat` (new slide, demo, or app), `fix`, `docs` (this file,
`outline.md`, `DESIGN.md` prose), `style` (theme/SCSS/typography), `refactor`,
`chore` (CI, deps, vendored assets), `build`.

Scopes are the repo's own nouns: `deck`, `theme`, `apps`, `wasm`, `ci`, `keynote`.

```
feat(deck): add a React-only Old Faithful demo
fix(theme): stop code-line-numbers clones jumping by pre's padding
chore(wasm): refresh the vendored shinyreact build for R 4.5
```

## Publishing

`.github/workflows/publish.yml` renders on every push to `main` and deploys
`_site/` to GitHub Pages (Settings → Pages → Source: **GitHub Actions**). It
needs the same three things a local render does, which is all the workflow is:

- Quarto, plus `quarto install chromium` — `mermaid-format: svg` pre-renders
  the diagram with headless Chrome.
- R 4.5 with `shinylive` and `shinyreact` installed (the shinylive filter reads
  the app's installed packages).
- `wasm-repo/`, which is checked in, so `bundle-wasm.R` has nothing to fetch.
  Building it in CI with <https://github.com/r-wasm/actions> instead is the
  alternative, and only worth it if the checked-in binary goes stale.

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

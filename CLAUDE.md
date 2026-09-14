# posit::conf(2026) — "Shiny + React"

Talk materials for Barret Schloerke's posit::conf(2026) session. Not a package;
nothing here ships to users. If knowledge is corrected or enhanced, update this 
document to support future sessions.

## Layout

```
outline.md                 the talk's narrative, in speaker-note form
index.qmd                  the deck (Quarto revealjs) - primary authoring surface
theme/DESIGN.md            the design spec - single source of truth for the look
theme/shinyreact-dark.scss revealjs theme, ported from DESIGN.md
theme/shinyreact-dark.highlight.theme  pandoc code colours (DESIGN.md 4.1)
theme/fonts.scss           the DESIGN.md faces, inlined as data URIs (generated)
theme/build_fonts.py       regenerates fonts.scss - run it if 5.1 changes
theme/qr-repo.svg          QR to this repo, bottom-centre of the title/end slides
theme/qr-showcase.svg      QR to the app gallery, on the "Samuel Bharti" slide
theme/fit-width.html       scales the deck to the window's width, not its box
theme/jsx-tokens.html      re-splits the JSX spans the grammar merges
theme/gif-restart.html     replays a slide's GIF from frame 1 on arrival
theme/qr-links.html        lays a clickable anchor over the repo QR
theme/a11y.html            titles the two shinylive iframes (see Accessibility)
record-plotomics-gif.py    drives the live app to record images/plotomics-live.gif
apps/                      the apps demoed live in the talk (02 is React-only)
images/                    slide images (headshot, app screenshots) - 1920x1080
_extensions/drop/          quarto-drop (webR console in a drawer)
_extensions/EmilHvitfeldt/ quarto-revealjs-editable (live slide editing)
```

**`theme/DESIGN.md` outranks the renderer.** The SCSS is a port of it. If a
colour, size, or margin needs to change, change DESIGN.md first, then the port —
otherwise they silently drift.

## Working on the deck

```bash
quarto preview index.qmd     # live reload while writing
quarto render                 # whole project -> _site/ (see Publishing)
```

The deck is `index.qmd`, not `slides.qmd`, so the published site's root *is*
the deck. Render output goes to `_site/`, with `apps/` copied in as a project
resource (slide 02 loads it in an iframe by relative path).

`theme/*.png` and `theme/*.svg` are project resources too. The compiled theme's
`url()`s (the title hex logo, the conf logo) walk out of
`index_files/libs/revealjs/dist/theme/` to `_site/theme/`; without the resource
entries they only resolve under `quarto preview`, which serves the project root
— a served render 404s them, silently, as a missing logo.

### Looking at a slide

Checking a layout or a colour means rendering and *looking*, not reading the
SCSS. Serve the render and drive it with a browser tool; every slide has an id
from its heading, so `index.html#/two-hooks-are-the-whole-api` lands on one
directly. The browser caches `index.html` hard between renders — add a
`?v=N` that changes, or a re-render appears to have done nothing.

**Nothing warns you when a slide runs off the bottom** — reveal clips it in
silence, and `quarto render` is happy. So audit the whole deck rather than the
slide you touched, by walking it in the browser and measuring each present
section's lowest descendant against the canvas:

```js
for (let i = 0; i < Reveal.getTotalSlides(); i++) {
  Reveal.slide(i); await new Promise(r => setTimeout(r, 100));
  const s = document.querySelector('section.present');
  s.querySelectorAll('.fragment').forEach(e => e.classList.add('visible'));
  const top = s.getBoundingClientRect().top, sc = Reveal.getScale();
  let max = 0;
  s.querySelectorAll('*').forEach(e => {           // skip svg: a <g>'s rect lies
    if (e.closest('svg')) return;
    const c = getComputedStyle(e);
    if (c.display === 'none' || c.position === 'fixed' || c.visibility === 'hidden') return;
    max = Math.max(max, e.getBoundingClientRect().bottom);
  });
  console.log(i, s.id, Math.round((max - top) / sc));   // > 1080 = check it
}
```

Show every fragment first or a slide measures short. Three kinds of false
positive come back over 1080 and are fine: the title and `.recap` slides (their
lockup is anchored to the *bottom*, so it sits at canvas height − 30), the
`.demo-slide`s (the app flexes to the canvas), and a block whose last *margin or
padding* crosses the line while its ink does not. Everything else is a real
clip. The deck currently has none: the only slide over 1080 is `#react-code` at
1085, which is `pre`'s own 40px bottom padding plus the line-highlight clones —
its lowest *text* is 1034. When one comes back over, measure the ink before
touching anything: `range.selectNodeContents(code)` and take the lowest rect.

The audit has to be run at **1080**, not at whatever window is open. A window
that is taller than 16:9 gets a canvas *taller* than 1080 from
`theme/fit-width.html` (a 1728x1084 laptop window gives 1204), so a slide that
overflows the design canvas can still look fine there and be clipped on the
projector.

A render can come out **incomplete**: exit 0 and "Output created", but
`_site/index_files/libs/` has no `revealjs/` in it, so the served deck is
unstyled markdown with ~19 console errors. The tell is quarto's own line
`Error adding css vars block SCSSParsingError` plus a
`_quarto_internal_scss_error.scss` dropped in the project root — quarto parses
the theme a second time for that pass, with a stricter parser than sass. The
one trigger found so far is a **missing semicolon after the last declaration in
a block**: `@keyframes x { from { opacity: 0 } to { opacity: 1 } }` kills the
pass, and the same line with both semicolons is fine (bisected by rendering
each). Sass itself accepts either, so nothing else warns you. So:
never commit `_quarto_internal_scss_error.scss`, treat it as "the SCSS you just
wrote broke a build pass", and check `ls _site/index_files/libs` before
concluding anything about a change — otherwise you debug the CSS of a deck that
never loaded the theme.

A **second**, unrelated failure: **hand-deleting `_site/` or `index_files/`**.
Quarto keeps state in `.quarto/` *and* in the project-root `index_files/`, so
removing either behind its back breaks the next render with exit **1** (unlike
the SCSSParsingError case, which exits 0). Two messages seen, same cause:

- `ERROR: NotFound … copy '.quarto/…/sass/<hash>.css' -> 'index_files/libs/
  revealjs/dist/theme/quarto-<hash>.css'` — the sass cache believes the compiled
  theme was already copied. Leaves `revealjs/` holding only `plugin/`, no
  `dist/`. Fix: `rm -rf .quarto`.
- `ERROR: NotFound … stat '…/index_files/figure-revealjs'` — survives
  `rm -rf .quarto`. Fix: just render a second time, which recreates it.

Simplest rule: **never hand-delete those directories.** `quarto render` already
replaces `_site/` on its own, so there is nothing to clean; doing it manually
only buys you one of these.

`quarto render` **deletes and recreates `_site/`**, so a server started *inside*
it keeps serving the old, unlinked directory: every later check silently reads a
stale deck (the tell is reveal bouncing a known slide id back to
`#/title-slide`). Restart the server after each render. Serving the project root
instead is not a fix — the deck's assets resolve from `index.html`'s own
directory, so `/_site/index.html` loads unstyled.

**Screenshots go in `.context/`, which is gitignored.** Never leave a debug
image in the repo root; if one is already there, delete it rather than adding
it to a commit or `.gitignore`.

The canvas is **1920x1080** (set in the qmd), which is why the SCSS uses the
same px values DESIGN.md does. Do not rescale them; reveal
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

The "Samuel Bharti" slide has two deck-local pieces. `[.com]{.dotcom}` in the
heading fades in 2.2s after the slide lands, in `$muted`, so the heading turns
into his address on its own; the animation is keyed off `section.present`, not
a bare `animation-delay`, because reveal keeps the coming slides in the DOM and
a plain delay would have run out before you ever arrived. Section 02's opener
wears the same gag — "React" becomes "React.dev" — but it is **not** on a timer:
it lands on the first bullet's click, so the address finishes as React's own
description arrives. That takes two rules, because the shared one above would
otherwise fire on arrival: `animation: none` for `#what-is-react`, then a
`:has(> ul > li:first-child.fragment.visible)` rule that re-keys it (the
`.logo-strip` trick, which reverses correctly when stepped back). `.qr-inline` is a QR
in a slide's *content* (the gallery's, under its bullet) rather than the
furniture QR the title and recap slides carry as a background layer; it also
zeroes the margin on the `<p>` quarto wraps the image in, which otherwise puts
the code through the bottom of the canvas. 140px on the 1920 canvas decodes
fine — verified by decoding it back out of a screenshot of the rendered slide.

`images/samuel-bharti.png` is Samuel's own studio headshot, resized from
`assets/photos/sb-headshot-1.jpeg` on his resource site (1073px square there;
880px here, 2x the slide's 440). It replaced a 400px avatar that was being
upscaled. The site's "Headshot 2" is a casual shot with sunglasses — not slide
material.

`theme/qr-repo.svg` and `theme/qr-showcase.svg` are generated; regenerate one
if its URL changes:

```bash
uv run --with segno python -c "import segno; segno.make('https://github.com/schloerke/presentation-2026-09-15-posit-conf-shinyreact', error='m').save('theme/qr-repo.svg', scale=10, border=2, dark='#141519', light='#f2f4f8')"
uv run --with segno python -c "import segno; segno.make('https://posit-shiny-showcase-bioinformatics.share.connect.posit.cloud/', error='m').save('theme/qr-showcase.svg', scale=10, border=2, dark='#141519', light='#f2f4f8')"
```

The showcase QR encodes the **deployed gallery**, not the repo the bullet next
to it links to: one bullet, two doors — the text is the source, the code is the
thing. Samuel's own site needs no QR; the heading's `[.com]{.dotcom}` gag spells
his address out, and the five package bullets already link into it.

**Both QRs are links as well as codes**, because the deck is published and a
viewer reading it on a laptop cannot scan their own screen. Both open in a new
tab (`target="_blank" rel="noopener"`) — a click mid-talk must not navigate the
deck away, which would lose the slide you were on and, with it, the reveal state
and the running shinylive apps. The inline one is a markdown link round the
image, carrying those two as link attributes: `[![](…){.qr-inline}](url){target=
"_blank" …}`. The repo one is a `background-image` layer
on three slides, and a background cannot be clicked, so
`theme/qr-links.html` (a fourth `include-after-body`) appends a transparent
`a.qr-link` to each and the scss parks it on the layer — from the same
`$margin + 170px` / 30px / 110px the `background-position` and `-size` use, so
retiring one means retiring both. Injected by script rather than written into
`index.qmd` because one of the three slides is `#title-slide`, which quarto
builds from the yaml and has no authorable body.

Verify a regenerated code by **decoding it back out of a screenshot of the
rendered slide at the full 1920 canvas**, not out of the svg. OpenCV is enough
and needs no system library (`pyzbar` wants a `zbar` that is not installed
here), but `detectAndDecodeMulti` on a whole 1920x1080 frame misses a 110px
code — crop to the code's own rect first, which `getBoundingClientRect()` on
the element gives you:

```bash
uv run --with opencv-python-headless --with numpy python -c "
import cv2; ok, i, *_ = cv2.QRCodeDetector().detectAndDecodeMulti(cv2.imread('.context/crop.png')); print(ok, list(i))"
```

Master equivalents, applied as classes on a `##` heading:

| DESIGN.md master | markdown |
|---|---|
| Title | the auto title slide (`title:`/`subtitle:`/`author:` in yaml) |
| Section divider | `## Name {.divider}` |
| Content | `## Name` + a bullet list |
| Code two-up | `## Name {.code-slide}` + `.columns` with two fenced blocks |
| Data | `## Name {.data-slide}` + caption, `.stats`, one chart |
| (none — deck-local) | `## Name {.demo-slide}` + a `shinylive-r` block |
| (none — deck-local) | `## Name {.app-slide .nostretch}` + bullets and a `.r-stack` of screenshots |
| (none — deck-local) | `## Name {.gif-slide .nostretch}` + a `.gif-caption` span and one `.app-gif` |
| (none — deck-local) | `## Name {.pkg-slide .nostretch}` + bullets and a `.hexpack` of hex logos |
| (none — deck-local) | `## Name {.cycle-slide .nostretch}` + the `.cycle` raw-html block |
| (none — deck-local) | `## Name {.recap}` — content master wearing master 1's furniture |
| (none — deck-local) | `## Name {.logo-slide}` + `.hexlogo` / `.hexreact` divs |
| (none — deck-local) | bullets + an `.r-stack.state-stack` of `.state-viz` rows |
| (none — deck-local) | `.hexreact.corner` — a bare React atom, top right |
| (none — deck-local) | `img.used-by` — a screenshot inline in a bullet |
| (none — deck-local) | `.logo-strip` — a row of linked brand marks under a bullet |
| (none — deck-local) | `.render-out` — a code panel holding rendered UI, not code |
| (none — deck-local) | `.tagline` — a quote bullet as a slide's subtitle |
| (none — deck-local) | `## Wait… what? {.meme background-image=…}` — a full-bleed reaction shot |

**A divider is its section's name, centred on the canvas, and nothing else.**
It carried a `data-number` ghost numeral ("05" behind "Testing") in a
$cyan-.22 240px face down the left; that is gone, along with master 2's 636px
heading baseline — the name now sits `top: 50%` with a `translateY(-50%)`, over
the orbit watermark's own centre, and the swoosh under it takes `margin: … auto`
so it centres with the text. The heading is absolutely positioned rather than
the section being a flex column: reveal's `.reveal .slides > section.present
{ display: block }` out-specifies a `display: flex` written here, so the section
cannot be a flex container (tried; the heading pinned to the top of the slide).
The sections themselves also lost their numbers, so "What's next" no longer
exists as a slide at all — "Future work: incremental adoption" follows "Test
coverage at every hop" directly, and the recap follows it. **"In the wild" then
comes *after* the recap**, so the gallery is what the deck ends on and the
`#recap` slide is a waypoint rather than the last thing on screen. Keep that
in mind when moving anything near the tail.

`.recap` is the slide that stays up through Q&A, so it carries the talk title,
the hex logo, the speaker lockup and the repo QR. The orbit and hex pseudos are
shared with `#title-slide` in one rule — but only the *ring* is: the title
slide holds the mark back (`content: "???"`, white and light-weight, since the
logo is the payoff of section 03) over an `$ink-deep`-filled hex, and `.recap`,
coming after the reveal, re-adds the PNG layer over a hex filled with `$ink`.
Both come from the `hex-ring($fill)` function, so the two stay in register.
**`.recap`'s fill is `$ink` deliberately, and it is not decorative**: `$ink` is
that slide's own background *and* the ground the PNG bakes in, so the fill is
invisible as a patch — its whole job is to stop the orbit watermark, which
reaches that corner, running its ellipses through the 20px of cyan ring the
520x600 PNG does not cover. An atom's orbit crossing the border read as a
smudge on the mark. (The ring was a bare stroke for a long time; the old
comment "a fill behind it would show as a patch" is only true of a fill that is
not `$ink`.)
The lockup is written out as a
`::: {.handle}` div (three lines) because only a real title slide has `author:`
to build one from. Its footer is hidden — the lockup takes that corner — and
`.recap ul` is capped at 1080px so bullets clear the logo's column.
`[text](url){.gh}` prefixes a link with the octocat, as a mask so the mark takes
the link's colour.

`.demo-slide` is for live apps: the heading is kept in the source (quarto splits
slides on `##`, and it carries the slide id and speaker notes) but hidden, and
padding, wrapper margin and footer all go to zero so the app fills 1920x1080.
Pair it with `#| viewerHeight: 1080`.

`.demo-titled` is the variant that keeps the heading, on all three Old Faithful
demos: those apps' pages are white from the first pixel, so full-bleed left the
corner mark floating on nothing. The section becomes a flex column and the app
`flex: 1`, so it takes whatever the heading leaves with no measured height to
keep in sync — and the padding has to be `!important`, because `.demo-slide`'s
own `padding: 0` already is. The shinylive demo is three wrappers deep and
`viewerHeight` lands as an *inline* height on `.shinylive-container`, so that
one is overridden with `!important` too; leave `viewerHeight: 1080` alone, it
is what the block is worth full-bleed and this only shrinks it.

Each carries the mark of what it is running: the plain-Shiny slide a
`.hexlogo.corner` carrying a `.lb-shiny` layer, which is Shiny's own sticker
(and turns the shinyreact ring off for free); the React-only slide a bare
`.hexreact.corner` atom; the `shinyreact` one a `.hexlogo.corner` hex. None
takes a `data-id` — that would enlist it in the logo build's auto-animate
chain. `:has(.hexlogo.corner)` caps the heading at 1380px alongside the body
text, so a longer one wraps instead of running into the hex.

**That mark is why all three demo slides are just headed "Old Faithful".** The
last one read "Live: Old Faithful w/ `shinyreact`", which is the corner hex
said twice; the hex signifies it. Quarto therefore deduplicates the slide ids
(`old-faithful`, `-1`, `-2`, `-3`) — nothing in the theme or the qmd targets
them, but don't write a rule that assumes one.

**All three demo apps hand the deck's keys back to reveal**, and they have to:
each runs in an iframe, so the moment you click a slider the keystrokes go to
the app and reveal never sees them — the deck stops advancing until you click
the slide background. The same seven-line `keydown` listener is in all three
(`apps/0{1,2}-*/www/index.html`, and a `tags$script()` in
`apps/00-old-faithful-trim/app.R`, since that one's page is generated by R);
change one, change all three. It forwards to reveal's own postMessage API
(`{method: "triggerKey", args: [keyCode]}`), so no keymap is duplicated.
PageUp/PageDown — what a presenter remote sends — always go to the deck; the
arrows, space and escape only when focus is *not* in a form control, or
advancing the slide would drag the slider at the same time. Verified by
dispatching keys inside each iframe and watching `Reveal.getIndices()`.

**All three demo apps are sized for a projector, not a laptop**, because they
run at 1:1 with the 1920x1080 canvas. `apps/00-old-faithful-trim` is plain
bslib, so its levers are its own: `bs_theme(font_scale = 1.6)` for the page,
`sidebar(width = 420)` for room, and `res = 130` on `renderPlot()` — base
graphics draw in device pixels, so the chart's text is the one thing
`font_scale` does not reach. Its slider needs a fourth: ionRangeSlider's parts
are fixed px whatever the font size (11px bubble, 10px min/max, 9px grid, a 3px
bar, a 19px handle), so a `tags$style` block resizes each and re-centres its
`top` on the same axis. Scaling the whole widget with a `transform` was tried
first and is worse — it shrinks the track by exactly what it magnifies, so you
get a laptop-sized slider with cartoon bubbles. `.irs-bar` needs `!important`:
bslib's own rule lands after the `tags$style`.

The other two: `.layout` is left-aligned and full-width (a
centred `max-width: 60rem` block parked ~400px of uncollapsible white beside
the sidebar and shrank the chart to nothing), and `html { font-size: 26px }` is
the single lever behind the page's rem sizes. Two things do *not* follow that
lever and are handled on their own:

- **The chart's text is in svg user units** (`fontSize: 17`/`18` on a 620x320
  viewBox), so how big it reads is set by how wide the svg is drawn — ~34px at
  the panel's width here. Widening the chart enlarges its labels; nothing else
  does. `H` is 320 rather than 380 so a full-width chart still clears the
  slide's height, and `.panel svg`'s `max-width` is the backstop for that.
- **A range input's thumb is a fixed ~16px** whatever the font size, so the
  slider is `transform: scale(1.5)` at `width: 66.7%` — the two multiply back
  to the sidebar's full width.

`apps/01-shinyreact/www/{app.css,app.js,app.tsx}` and
`apps/02-react-only/www/{app.css,app.js}` hold the same UI and the same chart
on purpose — the pair's whole point is that only the two hooks differ. Change
all of them together, and `diff` the css afterwards.

`.app-slide` (deck-local, on "Summer Bioinformatics Apps") is bullets
on the left and **one screenshot per bullet** on the right, swapped on the same
click as its bullet. Each bullet is the app's name linked to its Connect Cloud
deployment, over a sub-bullet linked to the source: the deck is published, so
on a projector those read as plain text and afterwards they are how a viewer
reaches the app. `apps.yml` in `posit-dev/shiny-showcase-bioinformatics` is the
source of truth for all three addresses (deployment, source, Zenodo DOI) — the
deployment URL is *derived* there, as
`https://<pcc-account>-<app>.share.connect.posit.cloud/`, so read it from that
file rather than guessing. The README carries the full table.

The gallery is **ten** apps, not nine: six under `samuelbharti/` (with versions
and DOIs) and four inside `posit-dev/shiny-showcase-bioinformatics` itself.
Samuel's own resource site lists all ten with every address, and is easier to
read than `apps.yml`: <https://www.samuelbharti.com/genomes-prompts-shiny/> —
note its tables are empty in the HTML and come from `data/apps.json` and
`data/packages.json`, so fetch those two files, not the page.

**The README's DOIs are the Zenodo *concept* DOIs, deliberately.** Every app
has two: a concept DOI that always resolves to the newest version, and a
version DOI pinned to one release. The README shipped version DOIs at first and
went stale within weeks — its variant-reviewer entry pointed at v2.3.1 after
v2.3.2 was out. Samuel's `apps.json` lists the concept ones, which is what the
README now carries. To tell them apart, ask Zenodo for the version record: its
`conceptrecid` field *is* the concept id (`curl -s
https://zenodo.org/api/records/<id>`). Querying a concept id through that API
404s — it only redirects in a browser — so a 404 there is the confirmation, not
a failure.

**Samuel's "high-res thumbnails" are illustrations, not screenshots.**
`assets/app-thumbnails/*.png` are 4800x3200 marketing cards: cream ground, a
mascot, their own title and caption typography, and — on the Plotomics one — a
hand-drawn field of a few hundred dots under a stylized "1,000,000". Lovely,
and wrong for this deck twice over: they fight the `$ink` ground, and they
replace evidence of the app with a drawing of it. The slide's own claim is that
these are the real apps, so the zoomed crops stay. His `assets/demo/*.mp4` are
likewise out — 12.7 MB for the Plotomics gallery tour against the 4.0 MB Xenium
clip, and a tour rather than the four beats that slide is cut to.

Two lines per app is the ceiling: five apps at two lines each already reach
948px of the 1080 canvas, so a wrapped sub-bullet pushes the fifth caption off
the bottom. Keep them short and re-check the last fragment after any edit. Screenshots rather than iframes: those apps are Connect
Cloud deployments, and a served render makes no off-origin request. Three things
make the swap work, and it breaks if any one goes:

- **Matching `fragment-index` on both halves.** Two fragments only land on one
  click if they carry the same index; the bullet is `{.fragment fragment-index=3}`
  and its image `{.fragment .fade-in-then-out fragment-index=3}`. This is the
  one place explicit indices are right — every fragment on the slide has one, so
  reveal's `sortFragments` has nothing unindexed to hoist (contrast the
  `.after-code` case below).
- **`.nonincremental` on each bullet's div.** `incremental: true` in the yaml
  also fragments the `li` *inside* the div, at an index after all of the
  images — so the div appears on cue and the text stays invisible until the end
  of the slide.
- **`.nostretch` on the heading**, or quarto's auto-stretch lifts each image out
  of its `<p>`, tags it `.r-stretch`, and reveal writes an aspect-preserving
  width/height inline that beats the theme.

The images sit in a reveal `.r-stack` (one grid cell, everything centred in it)
with `.app-stack` for the size. They do not share an aspect ratio, so the rule
is `object-fit: contain` over a panel-coloured backdrop; a shot much wider than
the box shrinks to unreadable, so crop it closer to the box's ratio
(`magick in.png -crop WxH+0+0 +repage -resize 1600x out.png`) rather than
growing the box.

`images/app-plotomics-live.png` is the **last frame of that recording**, cropped
to the same panel, so the still on the app slide and the clip on the next one
are the same picture:

```bash
ffmpeg -sseof -0.1 -i .context/xenium-raw.mov -update 1 \
  -vf "crop=1252:774:238:355" .context/last.png
magick .context/last.png -resize 1100x images/app-plotomics-live.png
```

The five shots are **zoomed crops, not full pages**. A whole 1600px browser
window in a ~930px box renders its 14px UI text at 8px — on a projector that is
a screenshot of nothing. Crop to the one region the bullet is about, sized
~900x630 so it lands at roughly 1:1 in the box, and cut on an element boundary
(a card gap, a panel edge) so nothing is sliced mid-word. Check by looking at
the rendered slide, not at the crop.

### `.pkg-slide` — "Summer Packages", as a honeycomb

"Summer Packages" is the app slide's construction reused: five
one-item `.nonincremental` fragment divs on the left, five hex logos on the
right, each pair sharing a `fragment-index` so they land on one click. Unlike
the app slide the hexes **accumulate** (plain `.fragment`, not
`.fade-in-then-out`), so the honeycomb builds up as the bullets do.

Its one-liners and its ordering (validate → fetch → transport) are Samuel's
own, from
<https://github.com/samuelbharti/bio-packages/blob/main/slides/>; `packages.yml`
in the showcase repo is the source of truth for what each package is and which
languages it ships. `biocohort` and `plotomics` are fourth and fifth and are
not part of that trio — `plotomics` earns its line because it is what Plotomics
Live draws two slides later, and `biocohort` (R only, r-universe rather than
CRAN) because it is the object the study itself lives in. There is no
`slides/biocohort.qmd` upstream, so its line was written from the package's own
DESCRIPTION and README.

**The hex source of truth is each package's `pkg-r/man/figures/logo.svg`.**
Samuel's site lists `biocohort`'s logo as a **png** (240x277, exactly the
slide's own hex size but raster), which is not what to vendor — the repo has
the svg, already drawn on the same 173.2x200 pointy-top viewBox the other
packs use, so it drops straight in.

**Five hexes means three rows, and rows alternate.** `img:nth-child(n + 3)`
pulls every row after the first up by 69.3px and shifts it 120px across;
`img:nth-child(n + 5)` then takes the shift *back* off row 3, which is what
puts the fifth hex over row 1's columns instead of floating half a width out.

The languages are **the R and Python marks in the slide's own hexagon**, not
the text `[r, py]`: `images/lang-r.svg` and `images/lang-py.svg`, each a
`$muted` hex on the same 173.2x200 pointy-top viewBox the package logos use,
with the simple-icons glyph in `$ink` at 132 of those 200 units. Regenerate
them (or add a language) with:

```bash
python3 - <<'PY'
import re, urllib.request
HEX="86.6,0 173.2,50 173.2,150 86.6,200 0,150 0,50"
GREY, INK = "#a3acbb", "#1c1d22"
def path_of(n):
    return re.search(r'<path d="([^"]+)"', urllib.request.urlopen(
        f"https://cdn.jsdelivr.net/npm/simple-icons@13/icons/{n}.svg").read().decode()).group(1)
M = 132.0
S, X, Y = M/24, 86.6-M/2, 100-M/2
for out, icon, label in [("lang-r","r","R"), ("lang-py","python","Python")]:
    open(f"images/{out}.svg","w").write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 173.2 200" '
        f'role="img" aria-label="{label}">\n  <title>{label}</title>\n'
        f'  <polygon points="{HEX}" fill="{GREY}"/>\n'
        f'  <g transform="translate({X:.1f} {Y:.1f}) scale({S:.4f})" fill="{INK}">'
        f'<path d="{path_of(icon)}"/></g>\n</svg>\n')
PY
```

They are 48x56 on the slide. Smaller was tried first (38x44, the glyph at 118
units) and the marks read as smudges — check a zoomed crop of the rendered
slide, not the file, before shrinking them again.

**The languages were checked against the registries, not against prose.**
`biobouncer` and `plotomics` are each on CRAN and PyPI; `biohttp` is CRAN and R
only; `bioclients` and `biocohort` are R only and are on r-universe rather than
CRAN. Both of the
first two are *also* on npm — their repos are monorepos with `pkg-r` /
`pkg-py` / `pkg-js`, and the JS is the TypeScript core the other two are built
out of — but the slide deliberately does not tag that: it is an implementation
detail delivered inside the R and Python packages, not a third thing an R user
would install. Upstream's own `packages.yml` is out of date here (it lists
`biobouncer` as "R · Python" and `plotomics` as "TypeScript · R · Python"), so
re-check the registries rather than copying it.

Each `li` is itself a **three-column grid** — name, language badge, then the
"– description", which grid wraps in an anonymous item for free — so the five
en-dashes line up into a gutter and the block reads as a table. The tracks are
fixed px, not `max-content`: each bullet is its own one-item list (it has to
be, to carry a `fragment-index`) and separate grids cannot share a track size.
Measure the widest name and the widest tag before changing them, and re-check
that no description wraps — the description column is what is left over.
The badge cell is `justify-self: start`, so the R hex lands in the same column
on all five rows and the Python one extends to its right; `end` instead put a
lone R under the *second* badge of the rows above it. The dash is an en dash, not the
em dash the rest of the deck's prose uses: an em dash costs about 15px here,
which was the difference between `biohttp`'s line fitting and wrapping. The
cyan rule is `position: absolute`, so it stays out of the tracks.

The pack is one `<p>` (five images, no blank lines between them, so pandoc
keeps them in one paragraph) with `display: grid` **on the `p`**, which is what
makes the images grid items and lets `nth-child` count them.

- **All five logos are pointy-top hexes on a 173.2x200 viewBox** (ratio 0.866).
  That is what makes the tessellation exact: pointy-top hexes have vertical
  left and right edges, so two in a row touch at exactly one width, and the
  next row interlocks at 0.75 of a height down and half a width across (hence
  `margin-top: -69.3px` — a quarter of the 277.1px height — and
  `translateX(120px)`, half the 240px width). Change the width and all three
  of those numbers change with it.
- **`biobouncer`'s own `logo.svg` is padded** inside a 440x500 box, so
  `images/pkg-biobouncer.svg` is the upstream file with its viewBox cropped to
  the hex itself (`41 32 358 416`). Without that it packs a size small and the
  honeycomb has a hole. `biocohort` comes from its own repo's
  `pkg-r/man/figures/logo.svg`; the other three are copies of the showcase
  repo's `thumbnails/`.
- **Both dimensions are set on the images, with both maxes off.** Quarto caps
  an image at the height of its box; the second row's box is short (negative
  top margin), so `height: auto` let those two shrink and the hexes came
  out at different sizes.

### `.gif-slide` — Plotomics Live, as a recording

**Only one of the five apps uses `shinyreact`.** Verified against each repo's
`renv.lock`, UI sources and code search: `plotomics-live` has
`library(shinyreact)` and `ui <- page_react_html("www/index.html")`; the other
four are `shiny` + `bslib` with the UI written in R. Two of them pull
`reactable`/`reactR`, so React runs in the page, but as an htmlwidget's
internals — not as UI anyone authored in React. Do not describe those four as
`shinyreact` apps; the slide's own claim is that the fifth reached for it
*because the visualization demanded it*, and that only works if the other four
are honestly plain Shiny.

So the app slide is followed by a full slide for that one app: heading, one
`.gif-caption` stat line, and a recording of the deployment filling the rest.
`.corner-hex` parks the `plotomics` hex in the corner the heading leaves free —
this is the app that package draws. It is markup, not a `url()` in the scss,
because quarto does not trace url()s out of an scss file and `images/` is not
a project resource; it is absolutely positioned against the section (reveal
already positions sections absolutely, so nothing needs `position: relative`),
and the `<p>` quarto wraps it in has its margin zeroed or it pushes the caption
and the GIF down by a blank line.
The measured numbers behind the caption (re-measure, do not trust these):
26 visualizations, and 69 `reactive_output()` calls in `app.R` — 22 `*_data`
feeds React reads through `useShinyOutputValue`, 28 `*_png` ggplot2 images, 14
`*_stats`, 5 other (`nd_meta`, `igv_genes`, `igv_config`, `lollipop_genes`,
`chat_response`). `app.R` is 546 lines, 432 of them code — the "476 lines" in
upstream's `apps.yml` no longer matches anything measurable, so the deck says
"one line of UI" instead, which the next slide proves.

A **recording, not an iframe**: it is a Connect Cloud deployment, and a served
render makes no off-origin request. The recording is the **Xenium** page — one
million single-molecule transcripts — in four beats: the points arrive, a hover
names the molecule under the cursor, a zoom, and back out to the whole section.

**It is an `<video>`, not a GIF, and it has to be.** A million-point field is
close to incompressible in GIF: measured on this clip, 11 MB at 48 colours and
6 fps (and visibly posterized), against 4 MB for h264 at full colour and 25
fps. The old Visium GIF got away with 3.2 MB because most of its pixels were a
static H&E photo. The file is local, so the deck is still offline-safe.

Three things the switch needs, and it breaks if any one goes:

- **`images/*.mp4` is a project resource in `_quarto.yml`.** Quarto traces an
  `![](…)` but not a `src=` inside a raw-html block, so without it the slide is
  a black box in a served render (`quarto preview` hides this, as ever).
- **`theme/gif-restart.html` handles `video` as well as `img[src$=".gif"]`** —
  `currentTime = 0` plus `play()`, so you always arrive at the first beat.
- **`autoplay loop muted playsinline`.** `muted` is what makes autoplay legal.

**Do not try to re-record this with playwright.** The WebGL render drops most
of its points under automation — the same failure this file already noted for
the UMAP page, and it is not SwiftShader: Chrome reported ANGLE/Metal on an M2
Pro and 30 s of extra wait changed nothing (4.7% → 5.1% ink coverage). The
decisive test is the app's own **ggplot2 (classic)** toggle, which is a
server-rendered PNG: it showed dense, separated cell-type islands while the
React view of the same data in the same browser was uniform dust. So this clip
was **hand-recorded** in a real Chrome window and cut down:

```bash
# .mov in, 1200x742 mp4 out; the two trims drop the deep-zoom trough in the
# middle of the take, which is pale and near-empty and reads as nothing.
ffmpeg -i screen-recording.mov -filter_complex \
  "[0:v]trim=1.2:6.0,setpts=PTS-STARTPTS[a];\
   [0:v]trim=8.6:12.85,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1,\
   crop=1252:774:238:355,fps=25,scale=1200:-2:flags=lanczos" \
  -an -c:v libx264 -pix_fmt yuv420p -crf 28 -preset slower \
  -movflags +faststart images/plotomics-live.mp4     # ~4.0 MB, 9.0s
```

**Every pixel of the clip's size is bought from its height.** At 1.617:1 it is
height-limited on this canvas, so it cannot use the full 1728px content width
and each pixel reclaimed above it is worth 1.6 across. `.gif-slide` therefore
runs a 60px heading (not the master's 76), a 12px swoosh margin, 44px of top
pad, and zeroed margins on the `<p>` quarto wraps the caption in - that `<p>`
alone was costing 88px, `$presentation-block-margin` above *and* below. The
footer is hidden, as on `.demo-slide`, because the clip now runs past where it
sat. That took the video from 1104x684 to **1324x820** - half again the area.

A *narrower* clip would be worse, not better: it is height-limited, so a lower
aspect ratio just makes it thinner at the same height. The remaining lever is a
**wider** one. Cropping the panel's toolbar and stats strips off, leaving the
plot canvas alone, is about 1252x630 (1.99:1) and would scale the actual point
cloud up by a further ~23% - at the cost of the "Shiny React" pill and the
"React draws 1,000,000 of them on the GPU" line, which are the two bits of
on-screen evidence for the slide's claim. Not done, for that reason.

The crop is the panel alone — toolbar ("WebGL – one million molecules") and
stats footer ("React draws 1,000,000 of them on the GPU") included, browser
chrome excluded; re-measure it for a new take. 1200px wide is the native width,
so `.app-gif`'s 680px height (all the canvas has spare under the heading and
the caption) scales it *down*.

`record-plotomics-gif.py` still drives the **Visium** page headless, which
works because that page is 3,798 spots over a photograph rather than mass
WebGL. It is kept as the reference for that kind of capture; nothing in the
deck uses its output now.

`theme/gif-restart.html` (a third `include-after-body`) blanks and re-sets the
`src` of any `.gif` on `slidechanged`. A GIF starts decoding at page load and
loops forever with no way to seek it, so without this you arrive mid-loop and
the four beats play out of order. Assigning the same URL back is a no-op, hence
the blank-for-a-tick.
### The logo build (`.logo-slide`, three slides)

"Why Shiny + React?" → `.logo-slide` → the `shinyreact` bullets slide are one
auto-animate run that assembles the logo, after slides 30–31 of the
[shinytest2 talk](https://schloerke.com/presentation-2022-07-28-rstudioconf22-shinytest2/#30),
where the Shiny and testthat hexes merge into the shinytest2 hex.

The beats:

1. **"Why Shiny + React?"** carries a small **corner lockup** of the two
   projects *in their own clothes* — Shiny's actual hex sticker, a `+`, and a
   bare React atom. No deck styling on either: this slide is about the two
   projects, not about the combined mark.
2. **`.logo-slide`** auto-animates that lockup to full size at the quarter
   points — still Shiny's blue sticker and a bare atom, unchanged. Everything
   then happens on **one click**: the mark slides to the centre and the sticker
   cross-dissolves into the deck's outlined shinyreact "Shiny" while the atom
   flies its loop round and lands in the tail of the swoosh.
3. **The bullets slide** parks the finished mark in the top-right corner.

**Section 03 has no divider.** The build slide is the divider — the marks
meeting *is* the section opener, and a `## shinyreact {.divider}` in between
would break the auto-animate chain, since reveal only auto-animates between
consecutive slides. If a divider is ever wanted back, it has to go *before* the
"Why" slide, not between it and the build.

There are **two images**, and no more should be needed. `theme/shiny-react.png`
is the finished shinyreact hex; the deck's "Shiny mark" is that same PNG with
`.lb-hole` — the hexagon's own ground colour ($ink; the PNG bakes in `#1C1D22`)
painted over its React atom. `theme/shiny-hex.svg` is Shiny's own sticker
from [rstudio/hex-stickers](https://github.com/rstudio/hex-stickers), drawn on
the **same 2521x2911 viewBox** the PNG uses — so the two are in register and the
cross-dissolve reads as one mark changing rather than two images crossing. It
sits in `.lb-shiny`, a layer over the PNG, hidden except where a slide asks for
it. The flying atom (`.hexreact`) is drawn from the orbit motif's ellipses plus
a nucleus, and is cross-faded out at the exact moment the hole goes, so it never
has to match the logo pixel for pixel. It is **an atom and nothing else** — no
hexagon of its own, on any slide; its box is invisible scaffolding for
auto-animate and `offset-path` to move, with the atom sized off it. Don't cut the wordmark or the atom out
into further files: that is more things to keep in register for no gain.

- **Both images are project resources in `_quarto.yml`.** Quarto does not trace
  `url()`s out of an scss file, so without those entries they are absent from
  `_site/` and the title slide and this build render as empty boxes.
  `quarto preview` serves the project root, so it only breaks once published —
  which is how the missing PNG went unnoticed until this build needed it.
- **The atom is 60% of its box everywhere**, because that is what lands it at
  the logo's own atom size after the flight. So the corner lockup sizes the
  *box* around the atom (250px box for a 150px atom) rather than re-scaling the
  atom inside it. Keeping the ratio fixed is what stops the atom jumping when
  auto-animate carries the pair to full size; the box is invisible there anyway.
- **The sticker converts on the click, not on arrival** — the slide is Shiny's
  logo until React comes for it. So the cross-dissolve is keyed off
  `.hexreact.visible`, the same trigger as the flight.
  `animation-fill-mode: both` plus keyframes that spell out their own `from`
  value is what holds the sticker up (and the ring down) through the animation's
  delay instead of falling back to the base declaration.
- **The dissolve must *end* on the atom's landing, and the flight is sized to
  meet it there — both at 1.8s.** The two marks are *one piece of artwork*:
  measured column by column on the 2521-wide viewBox, Shiny's swoosh and
  shinyreact's are the same silhouette from x=950 rightwards, and shinyreact's
  is Shiny's with the atom knocked out of the swoosh's tail (Shiny's wedge runs
  on to x≈240, the deck's stops at the atom's ring). So the *whole* of what the
  dissolve changes is that socket — and a socket with no atom in it is a
  **partial wedge tip**, which reads as the tail of the `y` cut off in a
  straight line. So the dissolve has to land on the *full* tip: `.8s` after a
  `1s` delay, against a flight of `1.6s` plus a `.2s` hand-over. Four numbers,
  one landing; retime one and retime all of them.
- **Close that gap by shortening the flight, not by sitting on the delay.** The
  flight was 2.2s, which put the atom's landing after the dissolve had already
  finished on an empty socket. Pushing the dissolve out to 1.5s+.9s=2.4s to meet
  it does fix the socket — and was rejected on sight: Shiny's blue mark then
  hangs on half a second past the point where the slide is about anything, while
  you wait for the atom to come round. The loop is the same path, flown faster.
  Mid-dissolve the wedge's extra length (the part beyond the atom) desaturates
  as it fades, but it stays full length — what must never appear is a *short*
  tip.
- **`.lb-hole` is masked to the atom's shape, not a disc**, for the same reason,
  and this is the other half of that bug. A disc large enough to cover the PNG's
  atom also covers the tip of the swoosh — the tail runs into the atom's
  right-hand ring — so through the dissolve the tail of the `y` was being bitten
  off in a circular arc by a layer that is supposed to be invisible. The mask
  comes from `atom-svg()`, the same function the flying atom's background does,
  so the geometry cannot drift; only the weights differ — stroke 17 and nucleus
  24, against the atom's 8.36 and 17.15 — deliberately fat so the mask swallows
  the PNG atom's antialiasing rather than leaving a cyan thread round the edge
  of it. Both numbers are measured: counting leaked cyan pixels in the hole's
  lower-left (where the swoosh never reaches) gives 30 at stroke 12, 17 at 14,
  and a floor of 14 from 17 up — and that floor is the *nucleus* edge, not the
  rings, so 17/24 leaks nothing where 19/17.15 still leaked. Wider than 17 only
  eats more swoosh. The one notch it still leaves in the swoosh is exactly the
  ring that is about to fly in over it.
- **The atom's proportions are React's own, and they are easy to get wrong.**
  react.dev's `logo.svg` is `rx="11" ry="4.2"`, `stroke-width="1"`, nucleus
  `r="2.05"`, so on `atom-svg()`'s rx=92 everything follows from ×8.364: ry 35,
  stroke 8.36, nucleus 17.15. Three sources agree on those ratios —
  react.dev itself (stroke/rx .0909, nucleus/rx .1864), the atom baked into
  `shiny-react.png` (measured off the file: rx 256.5px, 24px stroke, 47.5px
  nucleus → .0936 / .1852) and an independent SVG Repo redraw (.0919 / .1852).
  The deck shipped stroke 14 and nucleus 22 for a while — 1.7× and 1.3× too
  heavy — which reads as a fat cartoon of the atom next to the PNG's own. Only
  the radii were ever right. Re-measure against the rendered slide, not the
  source: at the flight's start the rendered atom should come out ≈.089/.189.
- **Do not "fix" that by editing either image.** Swapping shinyreact's wordmark
  into `shiny-hex.svg` does make the dissolve seamless, and it was tried — but
  it puts a chewed-looking swoosh on Shiny's own sticker, which the corner
  lockup on "Why Shiny + React?" also shows. Shiny's logo keeps Shiny's shape;
  the timing is where this problem gets solved.
- The ring belongs to the *shinyreact* mark, so `:has(.lb-shiny)` turns it off
  wherever Shiny's own sticker is laid over the top. That is the whole of the
  per-slide styling: carrying the `.lb-shiny` div is what makes a slide show
  Shiny's mark, and the corner slide simply has no such div.
- **Both hexagons carry a `$cyan-text` ring** (`::after`, a stroked hex svg).
  The logo bakes in its own `#1C1D22` ground, which *is* `$ink` — the background
  of every master except the divider — so without the ring the hexagons have no
  visible shape at all, most obviously the corner mark on the bullets slide. The
  stroke is `vector-effect="non-scaling-stroke"` because the box runs 150px →
  780px across and a viewBox-relative stroke would go from a hairline to a band.
- **`offset-path: path()` coordinates are relative to the element's own static
  top-left**, not to its containing block, whatever the spec reads like. So the
  path's first point must be the element's own half-size — that is what makes
  `offset-distance: 0%` a no-op — and every later point is an offset from where
  the box already sits. Two consequences that both cost a revision:
  - the declaration is **scoped to `.logo-slide`**, because the same path on the
    150x173 corner lockup would shift it by the difference in half-sizes; and
  - **`offset-anchor` is spelled out as `50% 50%`**. Left at `auto` it follows
    `transform-origin`, and reveal's auto-animate stylesheet sets
    `transform-origin: 0 0` on every `[data-id]` element — so adding a
    `data-id` silently moved the anchor to the box's top-left and parked the
    mark half a box off. Measure the rect before trusting a number here.
- The flight is a **clockwise loop**: down to the bottom right, left along the
  bottom, up the left side, across the top, down to the right by the "y", then
  tracing the swoosh's own tail into the atom's slot. The bottom leg is
  deliberately shy of the canvas edge — the box is still ~450px across there and
  its lower half would run off 1080.
- **Only the containers may be auto-animate-matched.** Reveal animates each
  matched element with its own transform, so a matched child inside a matched
  parent compounds both. `data-id` is on `.hexlogo` / `.hexreact` alone, and the
  slides carry `auto-animate-unmatched="false"` so reveal doesn't cross-fade the
  parts on every transition either.
- `.hexreact` is a **`.fragment.fade-out`**: present on arrival, "shown" on the
  click. Its animation therefore keys off `.visible`, and re-runs cleanly if the
  fragment is stepped back. `opacity`/`visibility` are in its keyframes because
  reveal's own `.fade-out.visible` rule hides the element outright, and a
  running animation outranks a normal declaration.
- The Shiny mark's move to centre is a **keyframe animation** (`:has()` on the
  same fragment state), timed well short of the flight so the atom lands in a
  mark that has stopped moving. That is also what lets the flight path be
  authored against a fixed frame. It was a `transition` and **that cannot
  work**: reveal's auto-animate stylesheet outlives the arrival it was written
  for — the slide keeps `data-auto-animate="running"`, so
  `[data-auto-animate="running"] [data-auto-animate-target="N"]` is still
  matching `.hexlogo` with `transition: transform 1s !important`. The computed
  `transition-property` on the slide is therefore `transform`, and a
  transition on top/left/width/height never fires: the mark snapped to the
  centre. Animations are not filtered by `transition-property`, so the same
  move keyframed runs regardless. Anything else on these slides that has to
  animate a property reveal did not animate needs keyframes for the same
  reason.
- Every `.hexlogo` / `.hexreact` box keeps the hexagon's **0.866 ratio**, and
  the parts inside are sized in `%`, so they ride each move for free. That is
  where the paired numbers in the scss come from: a length that is n% of the
  width is n × 0.866 % of the height.

When checking this by hand: `python3 -m http.server` keeps an open handle on the
directory it was launched in, and `quarto render` **replaces** `_site/` rather
than writing into it — so a server started before a re-render serves the old
inode for ever. Restart it after each render, or you will debug a slide that is
not the one on disk.

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

**A lead-in bullet is all the text a code slide has room for.** "What is
React?" carried two blockquotes *and* the `Stat.jsx` panel and ran 1358px —
278px past the canvas, with the bottom of the code silently gone. It is now two
slides: the quotes keep "What is React?" (a plain content slide, so it takes
the swoosh back), and the panel moved to `## Components` under the one-line
lead-in "A component is a function that returns HTML-like markup." Nothing was
shrunk or cut; both slides carry the corner atom.

When you do that check, **measure the rendered block, and measure the right
`pre`.** A `.code-slide` has two: `div.sourceCode pre` (the code, **34px**) and
`.code-with-filename-file pre` (the cyan filename caption, **36px** — quarto's
own revealjs css beats `.reveal pre` there). A bare `section.querySelector
('pre')` returns the caption, which is 47px tall and will tell you a 13-line
block is fine when it is 66px off the canvas. Measured across all ten code
slides: every one is 34/36. A line costs ~47px at 34px.

**A code block is also clipped sideways, and that fails even more quietly than
the bottom of a slide.** `pre` is `white-space: pre`, so a line wider than the
panel is cut at its right edge with no wrap, no scrollbar and no ellipsis — it
just looks like you wrote shorter code. Two real ones this caught: `#ownership`
rendered `input$bin_count +` with the ` 1` gone, and
`#the-ui-moves-to-typescript` rendered `sliderInput(inputId = "bin_count"`,
losing the elision *and* the closing paren.

The budget at 34px is **20.4px a character**, so a 50% `.columns` column holds
**37** (768px of content inside `pre`'s 40px padding) and a full-width block
holds ~84. Count before writing a long line.

**Do not check this with `scrollWidth`.** `pre.scrollWidth - pre.clientWidth` is
**0** even for a line 150px too wide, so it reports every block as fine. Measure
the ink with a range, having forced `white-space: pre` (the clones the
line-highlight plugin makes can differ), and skip `.notes` — a block in speaker
notes has zero width and reads as infinitely overflowing:

```js
for (let i = 0; i < Reveal.getTotalSlides(); i++) {
  Reveal.slide(i); await new Promise(r => setTimeout(r, 60));
  const s = document.querySelector('section.present');
  s.querySelectorAll('.fragment').forEach(e => e.classList.add('visible'));
  const sc = Reveal.getScale();
  s.querySelectorAll('div.sourceCode pre').forEach((pre, j) => {
    if (pre.closest('.notes') || !pre.getBoundingClientRect().width) return;
    const code = pre.querySelector('code'), cs = getComputedStyle(pre);
    const content = (pre.getBoundingClientRect().width
      - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight)) / sc;
    const prev = code.style.whiteSpace; code.style.whiteSpace = 'pre';
    const r = document.createRange(); r.selectNodeContents(code);
    let w = 0; for (const b of r.getClientRects()) w = Math.max(w, b.width);
    code.style.whiteSpace = prev;
    if (w / sc > content) console.log(s.id, j, Math.round(w / sc - content));
  });
}
```

13 on-slide blocks, and the clean result is no output at all. **Screenshot the
slide anyway** — both clips above were found by looking, after a width check
had already passed.

### "Custom UI… within a string" — the hook into section 02

The slide that turns Old Faithful toward React. It replaced one built on
`renderUI`, which was **the wrong defendant**: dynamic UI is a perfectly good
Shiny tool, so the room did not buy it. What actually hurts is authoring a
*second language inside a quoted string*, where no editor, linter, formatter or
test can reach it — and everyone in that room has done it.

- **The slide makes its own argument, with no annotation.** Skylighting colours
  an R string as a string, so the CSS and JS inside the two `HTML("…")` bodies
  render as one flat green while the R around them is highlighted. That *is*
  what your editor shows you. Verified on the render: 11 `span.st` tokens cover
  all of the foreign code. Don't "fix" that rendering — the flat block is the
  evidence.
- **The question is `.nonincremental`**, so it is up on arrival rather than on a
  click: the show of hands happens while the panel is still blank and the code
  lands as the answer. At 52px it has to stay on **one line** — "How many of you
  have written JavaScript or CSS within a string?" is 1607px, against a
  1728px content width — so there are 121px left, and any longer phrasing wraps
  and costs the panel ~70px it does not have. (It used to end "…within a string
  in R?"; the "in R" went because the escalation is about the *string*, and the
  same objection is a Python user's.) The code's lowest ink measures
  1003 of 1080 with the question on one line (1054 to the bottom of `pre`'s own
  padding).
- **Only the first question is on the slide; the escalation is spoken.** The
  notes carry four more (ten lines → a hundred → without one squiggly underline
  → "thought about just using a real JavaScript framework?"), each thinning the
  hands and the last one turning the room toward section 02. They stay in the
  notes deliberately: the panel has 77px of clearance, so a second on-slide
  bullet would clip it, and a printed escalation lets the audience read ahead
  and kills the beat. Whoever adds a question adds it there.
- **The `.x-mark` covers the CSS and JS lines only** (190/527, 1250x272) — from
  the top of `.stat-card { … }` to the bottom of the JS body's `});`. It must
  not reach the R around them: not `tags$head(tags$style(HTML("`, not the
  closing `")),`, not `uiOutput("cards")`. An X over the R reads as "Shiny is
  wrong", which is the opposite of the talk's claim. Measure those lines
  specifically off the render (each line span's rect against the section's top);
  an earlier cut unioned every `span.st` in the block, which swept in
  `uiOutput("cards")`'s perfectly ordinary R string, and the one after it still
  started on the `tags$head` line and ended on a closing paren.
- `.circle-mark` is the unused partner of that rule; it said "this stays" on the
  `renderUI` version. Kept because the pair is one rule.
- **Five later slides call back to it, in their speaker notes only.** The setup
  is only worth its slide if they are kept; grep the notes for "string" before
  changing any of them:
  - **"Wait… what?"** (the meme, two slides later) — the payoff. *You already
    do.* This is the pair that matters; don't retire either without the other,
    and keep them close — the callback says "a minute ago", which was true when
    the objection moved into section 02 and would not be if it moved back.
  - **"Why Shiny + React?"** — must **not** ask for hands again, though its
    first bullet is about hand-rolled HTML. Asking twice reads as having
    forgotten, and the second ask gets half the hands. Its note refers back
    instead. (Barret's bullet text stays as it is; only the note does this.)
  - **`#shinyreact-ui`** — the visual payoff:
    `Shiny.setInputValue('card_clicked', …)` in flat green against that slide's
    line 2, `useShinyInput<number>("bin_count", 30)` — same job, typed. This
    note used to live on a "Two hooks are the whole API" slide that followed it;
    that slide was **dropped** (it restated the two hooks on their own, one per
    panel, which `#shinyreact-ui`'s four highlight steps already walk) and its
    notes moved onto `#shinyreact-ui` whole.
  - **"The UI moves to TypeScript"** — half of that "cost" is a refund.
  - **"Test coverage at every hop"** and the Q&A **"Is node.js needed?"** — you
    cannot unit-test or lint a string; a build step buys it back. Note the
    second of those is on a `visibility="hidden"` slide, which **quarto drops
    from the render entirely** — grep `_site/index.html` for "node.js needed"
    and you get nothing. All five Q&A slides and "Thanks" are absent from the
    published deck. If they are meant to be reachable during Q&A, the attribute
    wanted is `visibility="uncounted"` (in the deck, not numbered) rather than
    `hidden` (not in the deck at all). Left as-is; flagged, not decided.
- `.code-sm` (a 32px override) was deleted with the old slide — it had exactly
  one user. Shorten the code instead; that is what got this panel from 13 lines
  to 11 and from 1146px to 986px.

`.render-out` is the other half of a `.code-slide`: a panel that holds *rendered
UI* rather than code (used on "What is React?", where the right column shows what
the left column's JSX draws). It is not a screenshot — it is the deck's own
`.stats` markup, carrying the same class names the JSX writes, so the two halves
cannot drift. It joins `pre` in the 6.4 panel selector rather than restating the
panel's six values. Every span in it sits on its own markdown line, so quarto
wraps each in a `<p>`; those block margins are zeroed, and forgetting that is
what pushed the panel 120px off the canvas first time round.

`.tagline` is a slide whose subtitle is a **quote bullet** — `- > text` in a
`::: {.nonincremental}` div, so the bullet's own cyan rule and the blockquote's
border read as the double line React's two quotes carry on "What is React?",
and it costs no click. Only the `shinyreact` slide uses it. Everything else in
the rule is what that quote's box costs the slide, all of it measured on the
render:

- **The quote `p`'s block margins are zeroed.** Quarto puts 54px above *and*
  below it *inside* the quote's own box — 108px of air for two lines of text,
  which is most of what ran the slide 85px off the canvas (1165px) when the
  tagline first became a quote.
- **The second list drops to a 40px top margin**, the tagline keeping the
  master's 60px under the heading — hence `> ul + ul` rather than `> ul`.
- **The `:has(.hexlogo.corner)` 1380px cap is off for the bullets, and that is
  what holds them at the master's 52px.** The cap exists so a bullet does not
  run under the corner mark; the mark ends at y=366 and these bullets start
  below 700, so they can have the full 1728px content width. Nothing else gives
  it back. The three now measure 1449px, 794px and 940px of text — one line
  each, with the widest 279px inside the canvas.
- **That headroom is recent and is the reason to re-measure after any
  rewording.** The third bullet used to read "`shinyreact` is the bridge between
  the two — it ships zero UI components", which was 1731px: three pixels over,
  and hand-broken with a `<br>` so the wrap fell in a chosen place rather than
  between "ships" and "zero". Shrinking the bullets to fit instead was tried and
  reverted — 46px is the largest size that holds a 1731px line, and buying three
  pixels with six points of body text is a bad trade. The bullet is now just
  "`shinyreact` ships zero UI components", so the `<br>` is gone.
- The tagline is **46px**, a subtitle under the 52px bullets.

Two gotchas if this is reused: quarto's
incremental filter **consumes the `.nonincremental` div**, so the list it wraps
carries no class to hook (target the blockquote instead), and the size has to
go on the `p` — quarto sizes the paragraph, so a size on the `blockquote` is
inherited and then overridden.

**"Test coverage at every hop" aligns its four em dashes into a gutter**, so the
bullets read as a table. One rule, on `#test-coverage-at-every-hop`: the
bullet's leading `strong` goes `display: inline-block; min-width: 460px`
("Confirm the client", the widest of the four, measures 455). Not the
`.pkg-slide` grid trick — a grid makes **every** inline child its own item, so
the three `code` spans after the dash each landed in a column of their own and
the line came apart (tried, on the render). `min-width` rather than `width`, so
a longer label pushes its dash out instead of being clipped; re-measure the four
after any rewording, and check the first bullet still fits (it is the longest
line on the slide).

`img.used-by` is a screenshot **inline in a bullet** (GitHub's "Used by 30M"
badge, on "Why React?"). It was shot over an `$ink` ground so it needs no frame
— which means the 2px `$muted` border is the only thing telling the audience it
is a screenshot and not deck typography. Keep it. `theme/`'s numbers assume a
4x raster: 88px of image at 64px tall puts 15px browser UI text at ~44px, over
DESIGN.md's 36px floor. Re-shoot at 4x if the badge is refreshed.

### `.logo-strip` — seven brand marks, on "Why React?"

Under the "component libraries, design systems, charts, tables, maps" bullet:
MUI, shadcn/ui, Ant Design, D3, Plotly, TanStack, Leaflet, in the bullet's own
word order. The bullet is the label, so the strip carries no captions — its job
is recognition, not classification. The bullet's trailing `, ...` was removed
when the strip went in: at 52px those three dots wrapped to a line of their own,
and the strip is the "…".

- **The marks wave in by themselves and cost no click.** The strip is not a
  fragment; each `<a>` runs `logo-wave` (fade + a 14px rise, .4s), the first at
  `.75s` and one every `.12s` after, so the row is settled ~1.6s after the
  bullet lands. Measured on the render: all seven at opacity 0 on the bullet's
  click, two in flight at 900ms, all seven at 1 by 2.2s.
- **The trigger is that bullet's own `visible` class**
  (`section:has(> ul > li:last-child.fragment.visible)`), not a bare
  `animation-delay` — reveal keeps the coming slides in the DOM, so an
  unconditional delay would have run out before you ever arrived (the same trap
  as `.dotcom`). `animation-fill-mode: both`, plus a `from` that restates the
  base `opacity: 0`, is what holds each mark down through its delay; stepping
  the bullet back un-matches the rule and the base declaration takes over, so
  the wave replays on the way forward again (verified by stepping back and
  forward).

- **The marks are in brand colour** — the one place in the deck showing colours
  DESIGN.md does not own — because colour is most of what makes a logo
  recognizable. Two fills are *not* the brand hex, because the brand hex is
  unreadable on `$ink`: shadcn/ui's is `#000000` (1.25:1), so it takes `$text`,
  which is also the mark its own site shows in dark mode; Plotly's glyph hex is
  `#3F4F75` (2.07:1), so it takes Plotly blue `#119DFF` (5.84:1). The other four
  are their own — MUI 4.39:1, Ant Design 3.81:1, D3 8.11:1, Leaflet 4.48:1.
  These are graphics, so DESIGN.md 9's 7:1 floor does not bind, but re-measure
  any mark swapped in.
- **D3 comes before Plotly** so that two blues are not adjacent (MUI, shadcn/ui,
  Ant Design already run blue-white-blue). Both are the "charts" pair, so
  swapping them inside it leaves the category order intact.
- Six marks are simple-icons glyphs with the brand fill **baked onto the file**
  (nothing can inherit `currentColor`, and quarto does not trace a `url()` out
  of the scss). Regenerate them the way `images/lang-*.svg` are generated:

  ```bash
  python3 -c "
  import urllib.request
  for slug, out, fill in [('mui','mui','#007FFF'), ('shadcnui','shadcnui','#F2F4F8'),
                          ('antdesign','antdesign','#0170FE'), ('plotly','plotly','#119DFF'),
                          ('d3dotjs','d3','#F9A03C'), ('leaflet','leaflet','#199900')]:
      s = urllib.request.urlopen(f'https://cdn.jsdelivr.net/npm/simple-icons@13/icons/{slug}.svg').read().decode()
      open(f'images/logo-{out}.svg','w').write(s.replace('<svg ', f'<svg fill=\"{fill}\" ', 1))"
  ```

  The seventh is TanStack's own coloured mark, its sunset-gradient tile taken
  straight from the brand kit (`public/favicon-dark.svg` in
  `TanStack/tanstack.com`). simple-icons has **no** TanStack, AG Grid, Recharts,
  deck.gl or Observable Plot glyph — any of those has to be vendored by hand.
- **The row is a grid of equal-width columns, not a flex row with a gap.** The
  marks are not the same width, so a fixed gap puts their centres at uneven
  intervals; `repeat(7, 190px)` puts them exactly 190px apart (measured).
  TanStack's is the only *filled* mark, so it runs 98px against the others' 110
  — at a shared height a solid tile reads a size larger than a bare glyph. The
  row sits 908→1018 on the canvas, which is all the height there is: the footer
  starts at 1039, so growing the marks again means buying the pixels somewhere.
- **The images are a markdown paragraph, not a raw-html `<img>` row**, because
  quarto traces `![](images/…)` into `_site/` and does not trace a `src=` inside
  a raw block — and `images/` is not a project resource (only `images/*.mp4`
  is). Same trap as the GIF slide.
- **Every mark links to its project, in a new tab** (`target="_blank"
  rel="noopener"`), for the same reason the QRs do: the deck is published, and a
  click mid-talk must not navigate the deck away and lose the reveal state and
  the running shinylive apps. The grid items are therefore the `<a>`s, which
  need `line-height: 0` or the link's own leading pads the cell.
- Plotly, D3 and Leaflet are **not** React libraries — you reach them through
  `react-plotly.js`, visx and `react-leaflet` — and they are on the strip
  precisely because this room knows them from R already. Do not describe them as
  React libraries in the notes.

`.hexreact.corner` is a bare React atom in the top-right corner, on every
section-02 slide. It shares `.hexreact.lockup`'s geometry (one rule, so they
cannot drift), and it must **never** carry a `data-id` — that is what enlists an
element in the logo build's auto-animate chain. The atom's ink starts at x=1674,
so a heading on one of these slides has 1578px; `section:has(.hexreact.corner) >
h2` caps it there so a long one wraps visibly instead of colliding with the mark.
The divider has no atom: its own centred watermark is already the orbit motif.

On the state row ("UI is assembled from data's state"), `.state-stack`'s
**`height` is what sizes the chart** — the svg takes 100% of the row's height and
`preserveAspectRatio` widens it to match. Growing the box to centre the row runs
the bars off the right of the canvas; move the row with `margin-top` and leave
the 190 alone. The `bins` panel also carries `min-width: 26ch` on its `code`,
because `flex: none` sized it to its own string and `[1, 8, 7, 10, …]` is seven
characters shorter than `[13, 19, 31, 20, …]` — so stepping 12 → 30 bins shrank
the panel and slid the arrow and histogram left, which reads as the chart being
redrawn rather than the numbers changing.

**The first row builds in three clicks** — the state, the `bins` it reduces to,
the chart that array *is* — so each hop after the first is a `.state-part` span
wrapping its arrow **and** what the arrow points at, and that span is the
fragment. The wrapper is a flex row of its own carrying the parent's 24px gap,
so grouping two items into one costs the layout nothing; `display: contents`
would have been tidier and cannot work, since opacity needs a box to apply to.
It also needs `align-self: stretch`, or the chart's `height: 100%` resolves
against a wrapper sized to its own content instead of the 190px row.

That build is also why the first row is **not** `.fade-in-then-out`: reveal
hides such a fragment as soon as it stops being the *current* one, and its own
children do exactly that — the row vanished on its second click. The theme
swaps the rows with `:has(> .state-viz:last-child.visible)` instead, which
reverses correctly and rides reveal's own fragment transition. Everything is
laid out from the first click and only fades in, so no panel moves as the row
builds.

### The reaction shot (`.meme`, "Wait… what?")

A full-bleed "Wait… what?" meme, **immediately after the `## React`
divider**. The objection — *you want me to write JavaScript?* — lands the
moment React is proposed, so the beat is taken there and the rest of section 02
is the answer to it. It used to sit twelve slides later, at the end of section
03, as a `.divider` headed "You want me to write JavaScript?!?!" with a walking
pink elephant along the bottom edge; `git log` has both if either is wanted
back. Its four bullets are still the speaker notes, unchanged apart from the
new cue.

- **The picture is the whole slide, so it is a reveal *background***
  (`background-image` + `background-size="contain"` +
  `background-color="#141519"` as attributes on the `##`), not an `img`. Native
  reveal, no layout of the theme's own — the only rule is
  `.reveal section.meme > h2 { display: none }`, hiding the heading quarto needs
  to split the slide and to carry the notes. `.meme` joins `.divider` and
  `#title-slide` in the footer-hiding rule.
- **`#141519` is `$ink-deep`**, so the pillarboxing matches the divider the
  slide follows rather than reading as a second black bar.
- **`images/wait-what.jpg`** is the meme cropped free of the letterbox bars it
  arrived with, and saved as jpg — it is a photograph, and the png was 1.8 MB
  against 225 KB:

  ```bash
  magick in.png -crop 1200x1050+0+75 +repage -quality 84 images/wait-what.jpg
  ```

  1200x1050 `contain`s to 1234x1080 on the canvas, so it is shown at ~1:1.

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
- A master's own rules need an element name to beat quarto's, not just its
  class. `.reveal .app-slide { padding-top }` and `.reveal .app-slide ul
  { margin }` are both *the same specificity* as rules that come later in the
  cascade — `.reveal .slides section` (the master padding) and quarto's
  `.reveal .slide ul { margin-bottom: .5em }` — so they silently lose. The tell
  is a value you can see in the compiled CSS, matching the element, and not in
  `getComputedStyle`. Write `.reveal .slides section.app-slide` instead. (Check
  a spacing change actually moved something before tuning the number again;
  two rounds of "tighten the gap" here did nothing at all.)
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
- **An `auto-animate` code pair needs both blocks laid out identically**, or
  reveal slides the whole panel instead of the lines that changed. Section 04
  has two of these — `#the-server-we-started-with` → the `shinyreact` server,
  and `#react-ui` → `#shinyreact-ui` (the UI half, added later so the `ui.tsx`
  hooks are read against the `useState`/`useMemo` they replace, twelve slides
  after section 02 showed them). Three things that pair needs:
  - **Neither block may be wrapped in a `.fragment`**, and neither slide may
    carry a lead-in bullet the other lacks. An element hidden on arrival has
    nothing to animate *from*, and a bullet above the panel changes the panel's
    own top. Both panels measure top 255 / bottom 947 here; check that before
    trusting a transition.
  - **The "before" block is written to the shape of the "after"** — its
    `useMemo` is on one line rather than the four `apps/02-react-only` spells
    it over — so both are 13 lines and only 1–3 differ. It is a slide, not the
    file; `#react-code` in section 02 still shows the app's own formatting.
  - **Both halves need a `code-line-numbers` attribute**, even one with no
    steps (`="true"`). Dropping it drops the line-number gutter too, and half a
    pair without a gutter slides sideways into the half with one. `#react-ui`
    carries `"|2,3"`: it lands unhighlighted, one click lights the two
    declarations the partner slide rewrites, and the click after that is the
    transition — so the eye is already on those two lines when they change.
- To land text on the *same* click as one of those steps, do **not** reach for
  `.fragment fragment-index=N`. Reveal's `sortFragments` puts every
  explicitly-indexed fragment ahead of the unindexed ones, and the
  line-highlight clones are unindexed, so the text jumps to the front of the
  slide. The theme's `.after-code` keys off the last clone instead
  (`section:has(pre > code.fragment:last-of-type.visible)`), which reverses
  correctly too. Quarto's `data-fragment-index` escape hatch in that plugin is
  no help: it reads the attribute off the `<code>`, and a block attribute lands
  on the wrapping `div.sourceCode`.
- `.chain` is the same trick, one step at a time: the two server slides carry
  `input$bin_count → breaks → …` under the panel, and each link appears with the
  code step that computes it. Since the plugin appends one `code` per step,
  *which clone is `.visible` is the step counter* — `.chain-1` keys off
  `code.fragment:nth-of-type(2)`, `.chain-2` off `(3)`, `.chain-3` off `(4)`.
  Text left *outside* a `.chain-N` span is visible on arrival, which is how the
  second slide keeps the first two links its auto-animate partner ended on.
  Count the steps before writing those numbers: a trailing `|` is a step, so
  `"|5|6|"` is four codes (original + three clones) and `"|6|7|4,8|"` is five.
  **`.after-code` currently has no user in `index.qmd`** — the line it carried
  ("The computation is unchanged — the value sent changed.") was cut from the
  `shinyreact` server slide. The rule is kept because it is the documented way
  to land text on a highlight step; delete it if that stays true.

### The data cycle (`.cycle-slide`) — hand-drawn, not mermaid

Three columns — browser, wires, server — each a flex stack of the same
fixed-height rows, so the hook, the wire's payload and the server's step for
one id share a line with no grid to keep in sync. The two columns are the
`.state-json` panel look; the wires are a cyan rule with a border-triangle
head, flipped on `.cycle-out`. Ids (`"bin_count"`, `"dist_data"`) are the
bold `$cyan-text` on every row, because matching ids *are* the contract.

- **It is a `{=html}` raw block.** Written as loose raw HTML, pandoc parsed the
  `$` in `input$bin_count … output$dist_data` as TeX math and ate the server
  column (a "Could not convert TeX math" warning, exit 0).
- **Every line is cut to 32 characters** of 32px mono — the column is 660px
  with 20px side padding, so 620px inside. `useShinyOutputValue("dist_data",
  null)` is 40, hence the three-line break. The payloads are 19 characters in
  the 360px wire column, 5px over, which the 24px gaps absorb. Widths were
  checked with `scrollWidth > clientWidth` on each `code` — that works here
  because these are plain blocks, not the line-highlight clones the code
  slides warn about.
- **Fragments carry explicit indices, all of them**: the send wire and the
  server column are index 1, the return wire index 2, so arrival shows what the
  React side wrote, click 1 sends it, click 2 answers it. Verified by stepping.
- The whole `.cycle` is `role="img"` with an `aria-label` saying the cycle in a
  sentence; the code inside is not read as a list of tokens.
- Lowest ink is 816 of 1080 with every fragment shown.

It replaced a mermaid `sequenceDiagram` (in `git log`) that went flowchart →
vertical flowchart → sequence, each step losing something: a flowchart cannot
show the round trip with one browser box, and the sequence renderer's inline
16px font left the labels at whatever the svg scaled to. `mermaid-format: svg`
is still in the yaml and now inert; `quarto install chromium` in `publish.yml`
is only needed if a mermaid block comes back.

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
  touch the binning. **That parity is why every R side of this app computes
  `breaks <- seq(min(x), max(x), length.out = n + 1)` rather than the shorter
  `hist(x, breaks = n)`**: given a single number `hist()` treats it as a
  *suggestion* and runs it through `pretty()`, so 30 draws 27 bins and 47 draws
  53. `bin_data()` bins exactly, and matching `pretty()` in JS would cost far
  more than the `seq()` line. The slides carry it too, section 01's
  `#ownership` included — section 04 calls that panel "the server we started
  with", so it has to be the same code.
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
pak::pak("posit-dev/shinyreact/pkg-r@r/v0.1.0")
```

### Getting `shinyreact` into webR — install it from the tagged release

**The tag is the whole mechanism.** `posit-dev/shinyreact`'s `r/v0.1.0` release
carries `library.data.gz` + `library.js.metadata` (built by
<https://github.com/r-wasm/actions>), and that is the one path shinylive has for
a GitHub-installed package: at render time `prepare_wasm_metadata()` sees
`RemoteType: github` in the *locally installed* DESCRIPTION and asks
`/repos/{RemoteUsername}/{RemoteRepo}/releases/tags/{RemoteRef}` for those two
assets. So:

- **Install with the tag, everywhere** — locally and in `publish.yml`. A plain
  `pak::pak("posit-dev/shinyreact/pkg-r")` records `RemoteRef: HEAD`, there is
  no release named `HEAD`, and the render *aborts* ("Can't find GitHub release").
  The slash in the tag is fine; `gh::gh()` does not escape it.
- **Bump both together** when a newer release lands, or the deck ships an older
  wasm binary than the code on the slides.
- `brio` — the one `shinyreact` Import not already in shinylive's library image
  — needs nothing: it is on CRAN, so shinylive pulls its wasm binary from
  repo.r-wasm.org at render time like any other dependency.
- Both land in `_site/…/shinylive-<version>/shinylive/webr/packages/` with a
  `metadata.rds`, which is what the runtime's `.mount_vfs_images()` reads
  *before* `.start_app()`'s "install anything the app imports" loop. So nothing
  is fetched at runtime. Check that directory after a render; it is the tell.

Two things this still needs:

- **The `www/` files ship as `## file:` entries** in the block, because
  `page_react_html()` does `brio::read_file("www/index.html")` inside the webR
  VFS.
- **`_quarto.yml`**, but only for the resources — the `SHINYLIVE_WASM_PACKAGES=0`
  escape hatch (and the `_environment` file that carried it, and the
  `bundle-wasm.R` post-render hook, and the hand-built `wasm-repo/`) are all
  gone. `git log` has them if the release ever disappears.

The `preload error:` console lines are webR writing to stderr, not failures;
`package 'shinyreact' was built under R version 4.6.0` is a harmless warning —
the release's binary is built under 4.6 and the webR you are looking at may run
4.5.1, which a pure-R package survives.

**Which webR you get is set by the shinylive R package, and CI pins it**
(`.github/workflows/publish.yml`). The two are not the same today, which is why
that warning appears locally and not on the published site:

| where | shinylive R pkg | assets | webR's R |
|---|---|---|---|
| CI / published | 0.5.0 (pinned) | 0.10.12 | 4.6.0 |
| a local dev install | 0.4.0.9000 | 0.10.8 | 4.5.1 |

The pin matters because that column *is* the deck's runtime: unpinned, an
upstream release re-cuts it on the next push, which is not a thing to discover
on the morning of the talk. Read both numbers off a render rather than trusting
this table — the assets version is the `shinylive-*/` directory under
`_site/index_files/libs/quarto-contrib/`, and webR's own R version is the one
file inside it that says so in plain text (this is how the 4.6.0 above was
measured, against the published site):

```bash
D=index_files/libs/quarto-contrib/shinylive-0.10.12/shinylive/webr
curl -sL "https://schloerke.com/presentation-2026-09-15-posit-conf-shinyreact/$D/vfs/usr/lib/R/library/translations/DESCRIPTION"
```

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

   So `SHINYLIVE_DOWNLOAD_WASM_CORE_PACKAGES` is **not needed** — shinylive's
   own bundler already skips `shiny`/`bslib`/`renv` and their dependencies, and
   the only gaps were `shinyreact` and `brio`.

2. **shinylive bundles those two at render time** (above), from the tagged
   GitHub release and from repo.r-wasm.org respectively.

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

Scopes are the repo's own nouns: `deck`, `theme`, `apps`, `wasm`, `ci`.

```
feat(deck): add a React-only Old Faithful demo
fix(theme): stop code-line-numbers clones jumping by pre's padding
chore(wasm): refresh the vendored shinyreact build for R 4.5
```

## Publishing

`.github/workflows/publish.yml` renders on every push to `main` and deploys
`_site/` to GitHub Pages (Settings → Pages → Source: **GitHub Actions**). It
needs the same two things a local render does, which is all the workflow is:

- Quarto, plus `quarto install chromium` — only for `mermaid-format: svg`,
  which pre-renders a mermaid block with headless Chrome. The deck has no
  mermaid block since the data cycle was hand-drawn, so it is currently inert.
- R with `shinylive` and `shinyreact` installed (the shinylive filter reads the
  app's installed packages). `shinyreact` must be installed **at its release
  tag**, `posit-dev/shinyreact/pkg-r@r/v0.1.0` — see the webR section above; at
  `HEAD` the render aborts. The render fetches the wasm binaries (the release's
  assets, plus `brio` from repo.r-wasm.org), so CI needs network for that step.

`apps/01-shinyreact` is upstream's `examples/01-hello` with the bundle renamed
`app.js`/`app.tsx`, so upstream is the reference when something is missing —
`www/app.css` came from its `www/ui.css`. It uses `page_react_html()`, which
needs a `www/index.html` carrying
`<meta name="shiny-dependency-placeholder" content="">`; upstream's
`examples/01-hello` uses `page_react()` instead and has no HTML file at all.
Note the deck writes the bundle as `www/ui.tsx` while the app names it
`app.tsx`.

## Accessibility

The deck is published, so it is read as a web page as well as projected. The
palette already carries it (zero contrast failures, DESIGN.md 9); these are the
structural pieces, and they are easy to drop when adding a slide:

- **Every image carries `fig-alt`.** Decorative ones — the package hexes beside
  bullets that already name them, the corner mark — take `fig-alt=""`, which
  quarto emits as `alt=""` and a screen reader then skips. Anything carrying
  information (a screenshot, a language badge, a QR) gets a real description.
  The gallery QR is an *image-only link*, so its alt is the link's only name:
  describe the destination, not the picture.
- **A `.meme`-style slide needs `aria-label` on the `##`.** The picture is a
  reveal background (backgrounds carry no alt) and the heading is
  `display: none`, which hides it from assistive tech too — so the slide is
  otherwise empty. Unknown attributes on a heading land on the `<section>`.
- **`theme/a11y.html`** (a fifth `include-after-body`) names the two shinylive
  iframes from their slide's `h2`. They are generated by shinylive's runtime,
  so there is nowhere in `index.qmd` to write a `title=`; the React-only demo
  is hand-written and carries its own, hence the `:not([title])`.
- **The Plotomics clip has `controls`** (WCAG 2.2.2: 9s of looping motion has
  to be pausable). Chrome fades the bar out while the pointer is elsewhere, so
  it costs the slide nothing — verified on the render — and it hands you a
  pause during Q&A.
- **`prefers-reduced-motion` collapses durations, it does not disable
  animations.** The logo build, the brand-strip wave and the X are all held in
  their end state by `animation-fill-mode`, so `animation: none` would drop
  each element back to its base declaration and leave the logo half-assembled.
  The rule sets `animation-duration: 1ms` instead. Verified with
  `emulateMedia({reducedMotion:'reduce'})`: 150ms after the click the mark
  lands on exactly the geometry the 2.6s build ends on. Playback is not CSS, so
  `theme/gif-restart.html` leaves the video paused on frame 1 under the same
  query.
- **Keyboard: all three demos forward the deck's keys back to reveal** — see
  the demo notes above. PageUp/PageDown always; the arrows and space only when
  focus is not in a form control, or advancing the deck would drag the slider
  at the same time.

## Non-negotiables from DESIGN.md

These were measured, not estimated (DESIGN.md 9). Verify, don't assume:

- Every text pair ≥ 7:1 contrast. Worst in use is the code comment at 7.17:1.
- Body ≥ 36px, code ≥ 32px, nothing below 28px on the 1920x1080 canvas.
- One motif per slide (hexagon / orbit / swoosh). See DESIGN.md 8.
- `#00D8FF` is graphic-only; text cyan is `#6FD4E8` (fringing, not contrast).
- Chart series colours are assigned in fixed order and never cycled.

## Reference

- Quarto revealjs: <https://quarto.org/docs/presentations/revealjs/>
- Slidecrafting: <https://slidecrafting-book.com/> — good on theming and layout;
  several chapters are still marked WIP, so confirm before relying on one.
